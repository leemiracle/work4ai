"""
COS 333 Advanced Programming Techniques（Princeton）
======================================================
覆盖主题：
- mini HTTP server（解析请求 + 生成响应）
- JSON-RPC 协议模拟
- Shell pipeline（pipe & filter 架构）
- C-like 内存安全检查（buffer overflow / use-after-free 检测）

核心参考：
- Fielding et al. 1999 "RFC 2616 HTTP/1.1" (now RFC 9112)
- JSON-RPC 2.0 Specification (2013)
- Kernighan & Pike "The Unix Programming Environment" 1984

本文件实现：
1. HTTP 请求解析器 + 响应生成器
2. JSON-RPC 2.0 请求/响应处理（含 method dispatch）
3. Shell 管道模拟（producer | filter | consumer）
4. C-like 内存安全模拟器（检测 OOB / UAF / double-free）

运行：
    python systems.py
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Optional


# ================================================================
# 1. HTTP Parser
# ================================================================

@dataclass
class HTTPRequest:
    method: str = ""
    path: str = ""
    version: str = "HTTP/1.1"
    headers: dict = field(default_factory=dict)
    body: str = ""


@dataclass
class HTTPResponse:
    status_code: int = 200
    reason: str = "OK"
    headers: dict = field(default_factory=dict)
    body: str = ""


def parse_http_request(raw: str) -> HTTPRequest:
    """Parse raw HTTP request string."""
    req = HTTPRequest()
    # Split header/body
    if "\r\n\r\n" in raw:
        header_part, body = raw.split("\r\n\r\n", 1)
        req.body = body
    else:
        header_part = raw
    lines = header_part.split("\r\n")
    # Request line
    parts = lines[0].split()
    if len(parts) >= 3:
        req.method, req.path, req.version = parts[0], parts[1], parts[2]
    # Headers
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            req.headers[k.lower()] = v
    return req


def build_http_response(resp: HTTPResponse) -> str:
    """Build raw HTTP response string."""
    lines = [f"HTTP/1.1 {resp.status_code} {resp.reason}"]
    resp.headers.setdefault("Content-Type", "text/plain")
    resp.headers["Content-Length"] = str(len(resp.body))
    for k, v in resp.headers.items():
        lines.append(f"{k}: {v}")
    lines.append("")  # blank line
    lines.append(resp.body)
    return "\r\n".join(lines)


def handle_request(req: HTTPRequest) -> HTTPResponse:
    """Simple router."""
    if req.method == "GET" and req.path == "/":
        return HTTPResponse(200, "OK", body="Welcome to COS 333!")
    if req.method == "GET" and req.path == "/api/status":
        body = json.dumps({"status": "ok", "version": "1.0"})
        return HTTPResponse(200, "OK",
                            headers={"Content-Type": "application/json"},
                            body=body)
    if req.method == "POST" and req.path == "/api/data":
        return HTTPResponse(201, "Created", body=f"Created: {req.body[:50]}")
    return HTTPResponse(404, "Not Found", body="404 Not Found")


# ================================================================
# 2. JSON-RPC 2.0
# ================================================================

class JSONRPCServer:
    """JSON-RPC 2.0 server with method dispatch."""

    def __init__(self):
        self.methods = {}
        self.next_id = 0

    def register(self, name: str, func):
        self.methods[name] = func

    def handle(self, request_str: str) -> Optional[str]:
        """Handle a JSON-RPC request string, return response string."""
        req = json.loads(request_str)
        # Validate JSON-RPC 2.0
        if req.get("jsonrpc") != "2.0":
            return self._error(None, -32600, "Invalid Request")
        method = req.get("method")
        params = req.get("params", [])
        req_id = req.get("id")

        if method not in self.methods:
            return self._error(req_id, -32601, f"Method not found: {method}")

        try:
            if isinstance(params, list):
                result = self.methods[method](*params)
            elif isinstance(params, dict):
                result = self.methods[method](**params)
            else:
                result = self.methods[method]()
        except Exception as e:
            return self._error(req_id, -32000, f"Server error: {e}")

        # Notification (no id) → no response
        if req_id is None:
            return None
        return json.dumps({"jsonrpc": "2.0", "result": result, "id": req_id})

    def _error(self, req_id, code, message):
        return json.dumps({"jsonrpc": "2.0",
                           "error": {"code": code, "message": message},
                           "id": req_id})


# ================================================================
# 3. Shell Pipeline (Pipe & Filter)
# ================================================================

class Pipeline:
    """Simulate Unix pipe: producer | filter1 | filter2 | ... | consumer"""

    def __init__(self):
        self.stages = []

    def add_stage(self, name: str, func):
        """func: generator/callable that takes input iterable, yields output."""
        self.stages.append((name, func))
        return self

    def run(self, initial_input):
        """Execute pipeline. Each stage transforms an iterable."""
        data = initial_input
        stage_outputs = {}
        for name, func in self.stages:
            data = func(data)
            stage_outputs[name] = list(data) if hasattr(data, '__iter__') and not isinstance(data, str) else data
        return data, stage_outputs


# ================================================================
# 4. C-like Memory Safety Simulator
# ================================================================

@dataclass
class MemBlock:
    addr: int
    size: int
    data: bytearray
    freed: bool = False


class SafeAllocator:
    """Simulate C malloc/free with safety checks.

    Detects:
    - Buffer overflow (write past allocated size)
    - Use-after-free
    - Double-free
    - Memory leaks
    """

    def __init__(self):
        self.heap: dict[int, MemBlock] = {}
        self.next_addr = 0x1000
        self.errors = []

    def malloc(self, size: int) -> int:
        addr = self.next_addr
        self.next_addr += size + 16  # padding between blocks
        block = MemBlock(addr, size, bytearray(size))
        self.heap[addr] = block
        return addr

    def free(self, addr: int):
        if addr not in self.heap:
            self.errors.append(f"❌ free({hex(addr)}): invalid pointer (never allocated)")
            return
        block = self.heap[addr]
        if block.freed:
            self.errors.append(f"❌ free({hex(addr)}): DOUBLE FREE!")
            return
        block.freed = True

    def write(self, addr: int, offset: int, value: int):
        """Write byte at addr + offset."""
        block = self._find_block(addr)
        if block is None:
            self.errors.append(f"❌ write({hex(addr)}+{offset}): invalid pointer")
            return
        if block.freed:
            self.errors.append(f"❌ write({hex(addr)}+{offset}): USE-AFTER-FREE!")
            return
        actual_offset = offset + (addr - block.addr)
        if actual_offset < 0 or actual_offset >= block.size:
            self.errors.append(
                f"❌ write({hex(addr)}+{offset}): BUFFER OVERFLOW! "
                f"(block size={block.size}, tried offset={actual_offset})")
            return
        block.data[actual_offset] = value & 0xFF

    def read(self, addr: int, offset: int) -> int:
        block = self._find_block(addr)
        if block is None:
            self.errors.append(f"❌ read({hex(addr)}+{offset}): invalid pointer")
            return 0
        if block.freed:
            self.errors.append(f"❌ read({hex(addr)}+{offset}): USE-AFTER-FREE!")
            return 0
        actual_offset = offset + (addr - block.addr)
        if actual_offset < 0 or actual_offset >= block.size:
            self.errors.append(f"❌ read({hex(addr)}+{offset}): OUT-OF-BOUNDS!")
            return 0
        return block.data[actual_offset]

    def _find_block(self, addr: int) -> Optional[MemBlock]:
        for block in self.heap.values():
            if block.addr <= addr < block.addr + block.size:
                return block
        return None

    def check_leaks(self):
        leaked = [a for a, b in self.heap.items() if not b.freed]
        if leaked:
            self.errors.append(f"⚠️  MEMORY LEAK: {len(leaked)} block(s) not freed: {[hex(a) for a in leaked]}")
        else:
            print("   ✅ 所有块已释放，无内存泄漏")


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 333: Advanced Programming Demo")
    print("=" * 60)

    # --- 1. HTTP ---
    print("\n📋 1. HTTP 请求/响应")
    raw_req = (
        "GET /api/status HTTP/1.1\r\n"
        "Host: localhost:8080\r\n"
        "Accept: application/json\r\n"
        "\r\n"
    )
    req = parse_http_request(raw_req)
    print(f"   {req.method} {req.path} {req.version}")
    print(f"   Host: {req.headers.get('host')}")
    resp = handle_request(req)
    raw_resp = build_http_response(resp)
    print(f"   响应:\n{raw_resp}")

    # --- 2. JSON-RPC ---
    print("\n📋 2. JSON-RPC 2.0")
    server = JSONRPCServer()
    server.register("add", lambda a, b: a + b)
    server.register("greet", lambda name: f"Hello, {name}!")
    server.register("factorial", lambda n: 1 if n <= 1 else n * server.methods["factorial"](n - 1))

    rpc_calls = [
        json.dumps({"jsonrpc": "2.0", "method": "add", "params": [3, 4], "id": 1}),
        json.dumps({"jsonrpc": "2.0", "method": "greet", "params": ["Princeton"], "id": 2}),
        json.dumps({"jsonrpc": "2.0", "method": "factorial", "params": [5], "id": 3}),
        json.dumps({"jsonrpc": "2.0", "method": "missing_method", "id": 4}),
    ]
    for call in rpc_calls:
        resp = server.handle(call)
        parsed = json.loads(resp) if resp else None
        if "result" in parsed:
            print(f"   → result: {parsed['result']}")
        elif "error" in parsed:
            print(f"   → error: {parsed['error']['message']}")

    # --- 3. Shell Pipeline ---
    print("\n📋 3. Shell Pipeline")
    # Simulate: echo words | tr A-Z a-z | sort | uniq -c | sort -rn
    words = ["Apple", "banana", "Apple", "cherry", "banana", "Apple", "date"]

    pipe = Pipeline()
    pipe.add_stage("lowercase", lambda data: (w.lower() for w in data))
    pipe.add_stage("sort", lambda data: (w for w in sorted(data)))
    pipe.add_stage("count", lambda data: _count_unique(data))
    pipe.add_stage("sort_by_count", lambda data: sorted(data, key=lambda x: -x[1]))

    result, stage_out = pipe.run(words)
    print(f"   输入: {words}")
    for name, out in stage_out.items():
        print(f"   {name}: {out}")
    print(f"   最终结果 (word: count): {result}")

    # --- 4. Memory Safety ---
    print("\n📋 4. C-like 内存安全模拟")
    alloc = SafeAllocator()
    # Normal usage
    p1 = alloc.malloc(10)
    alloc.write(p1, 0, 65)  # 'A'
    alloc.write(p1, 9, 90)  # 'Z'
    print(f"   正常: malloc(10), write [0]=65, [9]=90, read [0]={alloc.read(p1, 0)}")
    # Buffer overflow
    alloc.write(p1, 10, 99)
    # Free then use-after-free
    alloc.free(p1)
    alloc.read(p1, 0)
    # Double free
    alloc.free(p1)
    # Memory leak (p2 never freed)
    p2 = alloc.malloc(100)
    alloc.write(p2, 0, 1)

    print(f"\n   检测到 {len(alloc.errors)} 个错误:")
    for err in alloc.errors:
        print(f"   {err}")
    print("\n   泄漏检查:")
    alloc.check_leaks()

    # 反直觉发现
    print("\n💡 反直觉发现：")
    print(f"   在纯 Python 中，所有 4 类内存错误（OOB/UAF/double-free/leak）")
    print(f"   都不可能发生——垃圾回收 + 边界检查自动防护。")
    print(f"   但 C/C++ 中这 4 类错误占 CVE 漏洞的 ~70%！")
    print(f"   → Rust 的所有权模型在编译期消除这些，零运行时开销")

    print("\n✅ COS 333 Demo 完成！")


def _count_unique(data):
    """Count unique elements in sorted iterable."""
    counts = {}
    for item in data:
        counts[item] = counts.get(item, 0) + 1
    return counts.items()


if __name__ == "__main__":
    demo()
