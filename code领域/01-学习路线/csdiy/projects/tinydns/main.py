#!/usr/bin/env python3
"""
tinydns — 参照 CoreDNS/Bind 的迷你 DNS 服务器

参照：CoreDNS (Go) + BIND + dnsmasq
csdiy 对应：network-程序员视角(DNS/UDP协议) + db(缓存)

核心：
- DNS 协议解析（UDP，RFC 1035）
- 记录存储（A/AAAA/CNAME/MX/TXT）
- 查询转发（参照 CoreDNS 的 forward 插件）
- DNS 缓存（参照 dnsmasq）

协议格式（RFC 1035）：
  Header: ID(2) + Flags(2) + QDcount(2) + ANcount(2) + NScount(2) + ARcount(2)
  Question: QNAME(labels) + QTYPE(2) + QCLASS(2)
  Answer: NAME + TYPE + CLASS + TTL(4) + RDLENGTH(2) + RDATA
"""
import asyncio, struct, socket, time, logging, sys
from dataclasses import dataclass
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinydns")

# DNS 记录类型（参照 RFC 1035 §3.2.2）
TYPE_A = 1        # IPv4 地址
TYPE_CNAME = 5    # 别名
TYPE_MX = 15      # 邮件交换
TYPE_AAAA = 28    # IPv6 地址
TYPE_TXT = 16     # 文本记录
TYPE_NS = 2       # 名称服务器

TYPE_NAMES = {1:"A", 5:"CNAME", 15:"MX", 28:"AAAA", 16:"TXT", 2:"NS"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DNS 协议编解码（参照 RFC 1035 §4.1）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encode_name(name: str) -> bytes:
    """
    编码域名（参照 RFC 1035 §4.1.2）

    "example.com" → \x07example\x03com\x00
    每个 label 前面是长度字节
    """
    result = b""
    for label in name.rstrip(".").split("."):
        result += bytes([len(label)]) + label.encode()
    return result + b"\x00"

def decode_name(data: bytes, offset: int) -> tuple[str, int]:
    """
    解码域名（含指针压缩，参照 RFC 1035 §4.1.4）

    指针压缩：前两位为 11 时，剩余 14 位是指向另一个位置的指针。
    """
    labels = []
    pos = offset
    jumped = False
    original_pos = offset

    while True:
        length = data[pos]
        if length == 0:
            pos += 1
            break
        if (length & 0xC0) == 0xC0:
            # 指针压缩
            if not jumped:
                original_pos = pos + 2
            pointer = ((length & 0x3F) << 8) | data[pos + 1]
            pos = pointer
            jumped = True
        else:
            labels.append(data[pos+1:pos+1+length].decode())
            pos += 1 + length

    name = ".".join(labels) if labels else "."
    return name, (original_pos if jumped else pos)

def parse_query(data: bytes) -> Optional[dict]:
    """解析 DNS 查询"""
    if len(data) < 12:
        return None

    # Header（12 字节，参照 RFC 1035 §4.1.1）
    tx_id, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", data[:12])
    qr = (flags >> 15) & 1       # 0=查询, 1=响应
    opcode = (flags >> 11) & 0xF  # 0=标准查询
    rd = (flags >> 8) & 1        # 期望递归

    if qdcount == 0:
        return None

    # 解析 Question（第一个）
    qname, offset = decode_name(data, 12)
    qtype, qclass = struct.unpack(">HH", data[offset:offset+4])
    offset += 4

    return {
        "tx_id": tx_id,
        "flags": flags,
        "rd": rd,
        "qname": qname,
        "qtype": qtype,
        "qclass": qclass,
        "raw": data,
    }

def build_response(query: dict, answers: list[tuple]) -> bytes:
    """
    构建 DNS 响应（参照 RFC 1035 §4.1）

    answers: [(type, ttl, rdata_bytes), ...]
    """
    tx_id = query["tx_id"]
    # 响应 flags: QR=1, OPCODE=0, AA=1, TC=0, RD=copy, RA=1, RCODE=0
    flags = 0x8180  # 1000 0001 1000 0000
    qdcount = 1
    ancount = len(answers)

    header = struct.pack(">HHHHHH", tx_id, flags, qdcount, ancount, 0, 0)

    # Question section（原样返回）
    qname_bytes = encode_name(query["qname"])
    question = qname_bytes + struct.pack(">HH", query["qtype"], query["qclass"])

    # Answer section
    answer_section = b""
    for rtype, ttl, rdata in answers:
        answer = qname_bytes  # NAME（简化：用指针指向 Question）
        answer = b"\xc0\x0c"  # 指针压缩，指向偏移 12（Question 的 name）
        answer += struct.pack(">HHIH", rtype, 1, ttl, len(rdata))
        answer += rdata
        answer_section += answer

    return header + question + answer_section

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DNS 记录存储 + 缓存
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DNSStore:
    """
    DNS 记录存储（参照 CoreDNS 的 file 插件 + hosts 插件）

    两种来源：
    1. 静态配置（参照 /etc/hosts 或 zone file）
    2. 上游 DNS 缓存（参照 dnsmasq 的 cache）
    """
    def __init__(self):
        self.records: dict[str, dict[int, list]] = {}  # name → {type → [records]}
        self.cache: dict[str, tuple[float, list]] = {}  # name+type → (expire_time, answers)
        self.cache_ttl = 300  # 缓存 TTL（5 分钟）

    def add_record(self, name: str, rtype: int, rdata: str, ttl: int = 3600):
        """添加记录（参照 zone file 格式）"""
        if name not in self.records:
            self.records[name] = {}
        self.records[name].setdefault(rtype, []).append((ttl, rdata))

    def lookup(self, name: str, qtype: int) -> list[tuple[int, str]]:
        """查找记录"""
        # 先查缓存
        cache_key = f"{name}:{qtype}"
        if cache_key in self.cache:
            expire, answers = self.cache[cache_key]
            if time.time() < expire:
                return answers
            else:
                del self.cache[cache_key]

        # 查静态记录
        if name in self.records and qtype in self.records[name]:
            return self.records[name][qtype]
        return []

    def cache_result(self, name: str, qtype: int, answers: list, ttl: int = 300):
        """缓存上游 DNS 结果（参照 dnsmasq cache）"""
        self.cache[f"{name}:{qtype}"] = (time.time() + ttl, answers)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DNS 服务器（参照 CoreDNS）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TinyDNS:
    """
    DNS 服务器（参照 CoreDNS）

    流程（参照 network-程序员视角 的 DNS 排查）：
    1. 收到 UDP 查询
    2. 查本地记录（zone file）
    3. 如果没有 → 转发到上游（forward 插件）
    4. 缓存结果
    5. 返回响应
    """
    def __init__(self, upstream: str = "8.8.8.8:53"):
        self.store = DNSStore()
        self.upstream = upstream
        self.query_count = 0
        self.cache_hits = 0

    def add_record(self, name: str, rtype_str: str, rdata: str, ttl: int = 3600):
        """添加记录（支持字符串类型名）"""
        rtype_map = {"A": TYPE_A, "AAAA": TYPE_AAAA, "CNAME": TYPE_CNAME, "MX": TYPE_MX, "TXT": TYPE_TXT}
        rtype = rtype_map.get(rtype_str.upper(), TYPE_A)
        self.store.add_record(name, rtype, rdata, ttl)
        log.info(f"  {name} {ttl} IN {rtype_str} {rdata}")

    async def handle_query(self, data: bytes, addr) -> Optional[bytes]:
        """处理 DNS 查询（参照 CoreDNS 的 ServeDNS）"""
        query = parse_query(data)
        if not query:
            return None

        self.query_count += 1
        qname = query["qname"]
        qtype = query["qtype"]
        type_name = TYPE_NAMES.get(qtype, f"TYPE{qtype}")

        log.debug(f"  query from {addr}: {qname} {type_name}")

        # 查本地记录
        records = self.store.lookup(qname, qtype)

        if records:
            # 本地命中
            answers = []
            for ttl, rdata in records:
                rdata_bytes = self._encode_rdata(qtype, rdata)
                answers.append((qtype, ttl, rdata_bytes))
            log.info(f"  local: {qname} {type_name} → {len(answers)} answers")
            return build_response(query, answers)

        # 转发到上游（参照 CoreDNS forward 插件）
        if query["rd"]:
            upstream_resp = await self._forward(data)
            if upstream_resp:
                log.info(f"  forward: {qname} {type_name} → upstream")
                return upstream_resp

        # NXDOMAIN（域名不存在）
        return build_response(query, [])

    def _encode_rdata(self, qtype: int, rdata: str) -> bytes:
        """编码 RDATA"""
        if qtype == TYPE_A:
            return socket.inet_aton(rdata)
        elif qtype == TYPE_AAAA:
            return socket.inet_pton(socket.AF_INET6, rdata)
        elif qtype in (TYPE_CNAME, TYPE_NS):
            return encode_name(rdata)
        elif qtype == TYPE_TXT:
            encoded = rdata.encode()
            return bytes([len(encoded)]) + encoded
        elif qtype == TYPE_MX:
            parts = rdata.split(" ", 1)
            preference = int(parts[0]) if len(parts) > 1 else 10
            exchange = parts[-1]
            return struct.pack(">H", preference) + encode_name(exchange)
        return rdata.encode()

    async def _forward(self, query_data: bytes) -> Optional[bytes]:
        """转发查询到上游 DNS（参照 CoreDNS forward）"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2.0)
            sock.sendto(query_data, tuple(self.upstream.split(":")))
            data, _ = sock.recvfrom(4096)
            sock.close()
            return data
        except (socket.timeout, OSError):
            return None

    async def start(self, host="0.0.0.0", port=53):
        """启动 DNS 服务器（UDP，参照 CoreDNS）"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.setblocking(False)

        log.info(f"tinydns on {host}:{port} (UDP)")
        log.info(f"upstream: {self.upstream}")

        loop = asyncio.get_event_loop()
        log.info("waiting for queries... (Ctrl+C to stop)")

        while True:
            try:
                data, addr = await loop.sock_recvfrom(sock, 4096)
                response = await self.handle_query(data, addr)
                if response:
                    await loop.sock_sendto(sock, response, addr)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"error: {e}")

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinydns — 参照 CoreDNS 的 DNS 服务器")
    p.add_argument("-p","--port", type=int, default=8053, help="端口（默认 8053，53 需要 root）")
    p.add_argument("--upstream", default="8.8.8.8:53", help="上游 DNS")
    p.add_argument("--add", nargs=3, action="append", default=[],
                   metavar=("NAME", "TYPE", "VALUE"), help="添加记录")
    p.add_argument("-v","--verbose", action="store_true")
    args = p.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    dns = TinyDNS(upstream=args.upstream)

    # 添加内置记录（演示用）
    dns.add_record("hello.local", "A", "127.0.0.1")
    dns.add_record("tinydns.local", "A", "127.0.0.1")
    dns.add_record("api.local", "A", "10.0.0.1")
    dns.add_record("alias.local", "CNAME", "api.local")
    dns.add_record("test.local", "TXT", "this is a test record")

    # 用户自定义记录
    for name, rtype, value in args.add:
        dns.add_record(name, rtype, value)

    print(f"\ntinydns — DNS 服务器（参照 CoreDNS）")
    print(f"测试:")
    print(f"  dig @127.0.0.1 -p {args.port} hello.local")
    print(f"  dig @127.0.0.1 -p {args.port} api.local A")
    print(f"  dig @127.0.0.1 -p {args.port} alias.local CNAME")
    print(f"  dig @127.0.0.1 -p {args.port} google.com  # 转发到上游\n")

    try:
        asyncio.run(dns.start(port=args.port))
    except KeyboardInterrupt:
        log.info(f"stopped. served {dns.query_count} queries ({dns.cache_hits} cache hits)")

if __name__ == "__main__":
    main()
