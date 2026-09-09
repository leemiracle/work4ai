#!/usr/bin/env python3
"""
tinycache — 参照 Redis 的内存缓存服务器

参照项目：
  Redis   : RESP 协议、事件循环、dict、过期机制
  memcached : slab 分配（简化版）

核心特性（参照 redis-eventloop 精读）：
  P1 ✅ RESP 协议解析（参照 Redis processMultibulkBuffer）
  P2 ✅ 命令分发（参照 Redis processCommand + lookupCommand）
  P3 ✅ dict 哈希表（参照 Redis dict.c）
  P4 ✅ 过期机制（参照 Redis expire 惰性删除 + 定期删除）
  P5 ✅ 兼容 redis-cli

验证：用 redis-cli 连接测试

用法：
  python3 main.py -p 6380
  # 然后用 redis-cli 连接
  redis-cli -p 6380 set hello world
  redis-cli -p 6380 get hello
  redis-cli -p 6380 expire hello 10
"""

import argparse
import asyncio
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinycache")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESP 协议解析（参照 redis-eventloop 精读 §八 RESP）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RESPParser:
    """
    RESP 协议解析器（参照 Redis processMultibulkBuffer）

    RESP 协议格式：
      *N\r\n          → N 个元素的数组
      $N\r\ndata\r\n  → N 字节的批量字符串
      +OK\r\n         → 状态回复
      :123\r\n        → 整数
      -Err msg\r\n    → 错误
      $-1\r\n         → nil

    示例：SET key value
      *3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n
    """

    @staticmethod
    async def read_command(reader: asyncio.StreamReader) -> Optional[list[bytes]]:
        """读取并解析一条 RESP 命令"""
        try:
            first_byte = await reader.read(1)
            if not first_byte:
                return None

            if first_byte == b"*":
                # 多批量回复（标准客户端）
                count = int(await reader.readline())
                args = []
                for _ in range(count):
                    # 每个元素以 $N\r\n 开头
                    prefix = await reader.read(1)  # $
                    if prefix == b"$":
                        length = int(await reader.readline())
                        data = await reader.readexactly(length)
                        await reader.readexactly(2)  # \r\n
                        args.append(data)
                    else:
                        # inline 模式
                        await reader.read(1)
                        return None
                return args
            else:
                # inline 命令（telnet 模式，参照 Redis INLINE 协议）
                rest = await reader.readline()
                line = (first_byte + rest).strip()
                return line.split()
        except (asyncio.IncompleteReadError, ConnectionResetError):
            return None

    @staticmethod
    def encode_bulk(data: Optional[bytes]) -> bytes:
        """编码为 RESP 批量字符串"""
        if data is None:
            return b"$-1\r\n"
        return b"$" + str(len(data)).encode() + b"\r\n" + data + b"\r\n"

    @staticmethod
    def encode_status(msg: str) -> bytes:
        return b"+" + msg.encode() + b"\r\n"

    @staticmethod
    def encode_error(msg: str) -> bytes:
        return b"-" + msg.encode() + b"\r\n"

    @staticmethod
    def encode_integer(n: int) -> bytes:
        return b":" + str(n).encode() + b"\r\n"

    @staticmethod
    def encode_array(items: list[bytes]) -> bytes:
        result = b"*" + str(len(items)).encode() + b"\r\n"
        return result + b"".join(items)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# dict 哈希表（参照 Redis dict.c）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DictEntry:
    __slots__ = ("key", "value", "expire_at", "next")
    def __init__(self, key: bytes, value: bytes, expire_at: float = 0):
        self.key = key
        self.value = value
        self.expire_at = expire_at  # 0 = 永不过期；>0 = Unix 时间戳
        self.next: Optional[DictEntry] = None  # 链表解决冲突（参照 Redis dict 的链地址法）

class CacheDict:
    """
    哈希表（参照 Redis dict.c）

    Redis dict 特性：
    - 链地址法解决冲突
    - 渐进式 rehash（简化版不做）
    - SipHash 防 hash 碰撞攻击（简化版用 Python hash）
    """

    def __init__(self, initial_size: int = 1024):
        self.size = initial_size
        self.used = 0
        self.table: list[Optional[DictEntry]] = [None] * initial_size

    def _hash(self, key: bytes) -> int:
        return hash(key) % self.size

    def _needs_resize(self) -> bool:
        # 参照 Redis dict 的负载因子检查
        return self.used > 0 and self.used > self.size * 5

    def set(self, key: bytes, value: bytes, expire_at: float = 0) -> bool:
        """SET（参照 Redis dictReplace）"""
        idx = self._hash(key)
        entry = self.table[idx]

        # 检查是否已存在（更新）
        while entry:
            if entry.key == key:
                entry.value = value
                entry.expire_at = expire_at
                return False  # 更新，不是新增
            entry = entry.next

        # 新增（头插法，参照 Redis dict 的链表插入）
        new_entry = DictEntry(key, value, expire_at)
        new_entry.next = self.table[idx]
        self.table[idx] = new_entry
        self.used += 1
        return True

    def get(self, key: bytes) -> Optional[bytes]:
        """GET（参照 Redis dictFind）"""
        idx = self._hash(key)
        entry = self.table[idx]
        while entry:
            if entry.key == key:
                # 惰性过期检查（参照 Redis expire 惰性删除）
                if entry.expire_at > 0 and time.time() > entry.expire_at:
                    self._delete_at(idx, key)
                    return None
                return entry.value
            entry = entry.next
        return None

    def delete(self, key: bytes) -> bool:
        """DEL（参照 Redis dictDelete）"""
        idx = self._hash(key)
        return self._delete_at(idx, key)

    def _delete_at(self, idx: int, key: bytes) -> bool:
        entry = self.table[idx]
        prev = None
        while entry:
            if entry.key == key:
                if prev:
                    prev.next = entry.next
                else:
                    self.table[idx] = entry.next
                self.used -= 1
                return True
            prev = entry
            entry = entry.next
        return False

    def active_expire(self, limit: int = 100) -> int:
        """
        定期删除过期 key（参照 Redis activeExpireCycle）

        Redis 策略：每次抽样 20 个 key，删除过期的。如果过期比例 > 25%，再来一轮。
        本实现：遍历最多 limit 个桶。
        """
        deleted = 0
        now = time.time()
        checked = 0
        for idx in range(self.size):
            if checked >= limit:
                break
            entry = self.table[idx]
            prev = None
            while entry:
                checked += 1
                if entry.expire_at > 0 and now > entry.expire_at:
                    # 过期了，删除
                    next_entry = entry.next
                    if prev:
                        prev.next = next_entry
                    else:
                        self.table[idx] = next_entry
                    self.used -= 1
                    deleted += 1
                    entry = next_entry
                else:
                    prev = entry
                    entry = entry.next
        return deleted

    def keys(self, pattern: bytes = b"*") -> list[bytes]:
        """KEYS（参照 Redis keysCommand）"""
        result = []
        now = time.time()
        for entry in self.table:
            while entry:
                if entry.expire_at == 0 or now <= entry.expire_at:
                    if pattern == b"*" or pattern in entry.key:
                        result.append(entry.key)
                entry = entry.next
        return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TinyCache 服务器（参照 Redis aeMain + beforeSleep）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TinyCache:
    """
    缓存服务器（参照 Redis 的整体架构）

    Redis 架构（参照 redis-eventloop 精读）：
      main() → initServer() → aeMain()
        每圈循环：
          ① beforeSleep（刷盘+聚合）
          ② epoll_wait（等客户端）
          ③ readQueryFromClient（读 RESP）
          ④ processCommand（查表+执行）
          ⑤ addReply（回复入 buffer）

    本架构（asyncio 等价）：
      asyncio.start_server
        每个连接：
          ① read_command（RESP 解析）
          ② execute_command（查表+执行）
          ③ write reply
    """

    def __init__(self):
        self.data = CacheDict()
        self.start_time = time.time()
        self.total_commands = 0
        self.connected_clients = 0

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        处理客户端连接（参照 Redis createClient + readQueryFromClient）
        """
        client_addr = writer.get_extra_info("peername")
        self.connected_clients += 1
        log.debug(f"new client: {client_addr} (total: {self.connected_clients})")

        try:
            while True:
                # ① 读取并解析 RESP（参照 Redis processInputBuffer）
                args = await RESPParser.read_command(reader)
                if args is None:
                    break  # 客户端断开

                if not args:
                    continue

                # ② 执行命令（参照 Redis processCommand）
                self.total_commands += 1
                reply = self.execute_command(args)

                # ③ 回复（参照 Redis addReply）
                if reply:
                    writer.write(reply)
                    await writer.drain()

        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            self.connected_clients -= 1
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass
            log.debug(f"client disconnected: {client_addr}")

    def execute_command(self, args: list[bytes]) -> bytes:
        """
        命令分发（参照 Redis processCommand + lookupCommand）

        Redis 维护一个命令表：
          {"get": getCommand, "set": setCommand, ...}

        本实现用 if/elif 链（简化版）。
        """
        cmd = args[0].upper()

        if cmd == b"PING":
            if len(args) > 1:
                return RESPParser.encode_bulk(args[1])
            return RESPParser.encode_status("PONG")

        elif cmd == b"SET":
            if len(args) < 3:
                return RESPParser.encode_error("wrong number of arguments for 'set'")
            key, value = args[1], args[2]
            expire_at = 0
            # 解析 EX 参数（参照 Redis SET ... EX seconds）
            if len(args) >= 5 and args[3].upper() == b"EX":
                expire_at = time.time() + int(args[4])
            self.data.set(key, value, expire_at)
            return RESPParser.encode_status("OK")

        elif cmd == b"GET":
            if len(args) < 2:
                return RESPParser.encode_error("wrong number of arguments for 'get'")
            val = self.data.get(args[1])
            return RESPParser.encode_bulk(val)

        elif cmd == b"DEL":
            if len(args) < 2:
                return RESPParser.encode_error("wrong number of arguments for 'del'")
            deleted = 0
            for key in args[1:]:
                if self.data.delete(key):
                    deleted += 1
            return RESPParser.encode_integer(deleted)

        elif cmd == b"EXPIRE":
            if len(args) < 3:
                return RESPParser.encode_error("wrong number of arguments for 'expire'")
            key = args[1]
            ttl = int(args[2])
            val = self.data.get(key)
            if val is None:
                return RESPParser.encode_integer(0)
            self.data.set(key, val, time.time() + ttl)
            return RESPParser.encode_integer(1)

        elif cmd == b"TTL":
            if len(args) < 2:
                return RESPParser.encode_error("wrong number of arguments for 'ttl'")
            key = args[1]
            idx = self.data._hash(key)
            entry = self.data.table[idx]
            while entry:
                if entry.key == key:
                    if entry.expire_at == 0:
                        return RESPParser.encode_integer(-1)  # 永不过期
                    remaining = int(entry.expire_at - time.time())
                    return RESPParser.encode_integer(max(-2, remaining))
                entry = entry.next
            return RESPParser.encode_integer(-2)  # key 不存在

        elif cmd == b"KEYS":
            pattern = args[1] if len(args) > 1 else b"*"
            keys = self.data.keys(pattern)
            return RESPParser.encode_array([RESPParser.encode_bulk(k) for k in keys])

        elif cmd == b"DBSIZE":
            return RESPParser.encode_integer(self.data.used)

        elif cmd == b"INFO":
            info = self._info()
            return RESPParser.encode_bulk(info.encode())

        elif cmd == b"FLUSHALL":
            self.data = CacheDict()
            return RESPParser.encode_status("OK")

        elif cmd == b"ECHO":
            if len(args) > 1:
                return RESPParser.encode_bulk(args[1])
            return RESPParser.encode_status("")

        elif cmd == b"COMMAND":
            # redis-cli 连接时会发 COMMAND，返回空数组即可
            return RESPParser.encode_array([])

        elif cmd == b"SELECT":
            # redis-cli 默认发 SELECT 0
            return RESPParser.encode_status("OK")

        else:
            return RESPParser.encode_error(f"ERR unknown command '{args[0].decode()}'")

    def _info(self) -> str:
        uptime = int(time.time() - self.start_time)
        return (
            f"# Server\r\n"
            f"redis_version:tinycache-1.0\r\n"
            f"uptime_in_seconds:{uptime}\r\n"
            f"\r\n# Clients\r\n"
            f"connected_clients:{self.connected_clients}\r\n"
            f"\r\n# Keyspace\r\n"
            f"db0:keys={self.data.used},expires=0,avg_ttl=0\r\n"
            f"\r\n# Stats\r\n"
            f"total_commands_processed:{self.total_commands}\r\n"
        )

    async def active_expire_loop(self):
        """
        定期删除过期 key（参照 Redis serverCron 里的 activeExpireCycle）

        Redis 在 serverCron（10Hz）里调用 activeExpireCycle。
        本实现用 asyncio 定时任务，每秒一次。
        """
        while True:
            deleted = self.data.active_expire(limit=100)
            if deleted > 0:
                log.debug(f"expired {deleted} keys")
            await asyncio.sleep(1.0)

    async def start(self, host: str, port: int):
        """启动服务器（参照 Redis aeMain）"""
        server = await asyncio.start_server(
            self.handle_client, host, port, reuse_address=True
        )

        # 启动定期过期任务（参照 Redis serverCron）
        asyncio.create_task(self.active_expire_loop())

        addr = server.sockets[0].getsockname()
        log.info(f"tinycache on {addr[0]}:{addr[1]} ({self.data.size} slots)")
        log.info(f"test: redis-cli -p {port} set hello world")

        async with server:
            await server.serve_forever()


def main():
    p = argparse.ArgumentParser(description="tinycache — 参照 Redis 的内存缓存")
    p.add_argument("-p", "--port", type=int, default=6380, help="端口（默认 6380）")
    p.add_argument("-H", "--host", default="0.0.0.0", help="监听地址")
    p.add_argument("-v", "--verbose", action="store_true", help="debug 日志")
    args = p.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    cache = TinyCache()
    try:
        asyncio.run(cache.start(args.host, args.port))
    except KeyboardInterrupt:
        log.info("tinycache stopped")

if __name__ == "__main__":
    main()
