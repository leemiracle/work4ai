#!/usr/bin/env python3
"""
tinyrpc — 参照 gRPC/Thrift 的 RPC 框架

参照：gRPC (Google) + Apache Thrift
csdiy 对应：network(TCP) + distributed(序列化) + patterns(代理模式)

核心：
- 服务定义（参照 Protobuf IDL）
- JSON 序列化（简化版，真实用 Protobuf/Thrift）
- 服务端注册 + 客户端代理（Stub）
- 异步 TCP 传输

模式：客户端 → Stub(序列化) → TCP → Server(分发) → Handler → 返回
"""
import asyncio, json, time, logging, sys, inspect
from dataclasses import dataclass
from typing import Any, Optional, Callable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinyrpc")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPC 消息格式（参照 gRPC 的 Wire Format，简化版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class RPCRequest:
    """RPC 请求（参照 gRPC HTTP/2 frame，简化为 JSON over TCP）"""
    id: int               # 请求 ID（用于匹配响应）
    service: str           # 服务名
    method: str            # 方法名
    args: dict            # 参数（参照 Protobuf message）

@dataclass
class RPCResponse:
    """RPC 响应"""
    id: int               # 对应请求 ID
    result: Any = None     # 返回值
    error: str = None      # 错误信息

def encode(msg) -> bytes:
    """编码消息（参照 gRPC 的序列化，简化为 JSON + 长度前缀）"""
    data = json.dumps(msg.__dict__ if hasattr(msg,'__dict__') else msg,
                      default=str, ensure_ascii=False).encode()
    # 4 字节长度前缀 + JSON（参照 gRPC 的 Length-Prefixed Message）
    length = len(data).to_bytes(4, 'big')
    return length + data

def decode(data: bytes):
    """解码消息"""
    length = int.from_bytes(data[:4], 'big')
    msg_data = data[4:4+length]
    return json.loads(msg_data)

async def read_msg(reader: asyncio.StreamReader):
    """读取一条消息（参照 gRPC 的帧读取）"""
    header = await reader.readexactly(4)
    length = int.from_bytes(header, 'big')
    data = await reader.readexactly(length)
    return json.loads(data)

async def write_msg(writer: asyncio.StreamWriter, msg: dict):
    """写入一条消息"""
    writer.write(encode_obj(msg))
    await writer.drain()

def encode_obj(msg):
    """编码 dict → bytes"""
    data = json.dumps(msg, default=str, ensure_ascii=False).encode()
    return len(data).to_bytes(4, 'big') + data

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPC 服务端（参照 gRPC server）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RPCServer:
    """
    RPC 服务端（参照 gRPC Server）

    注册服务 → 监听 TCP → 接收请求 → 分发到 handler → 返回响应
    """
    def __init__(self):
        self.services: dict[str, dict[str, Callable]] = {}  # service → {method → handler}
        self.request_count = 0
        self.start_time = time.time()

    def register(self, service_name: str):
        """装饰器：注册服务（参照 gRPC add_XXXServicer_to_server）"""
        def decorator(cls):
            service_methods = {}
            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    service_methods[name] = method
            self.services[service_name] = service_methods
            log.info(f"registered service '{service_name}' with methods: {list(service_methods.keys())}")
            return cls
        return decorator

    def add_service(self, service_name: str, methods: dict[str, Callable]):
        """直接注册服务（非装饰器方式）"""
        self.services[service_name] = methods
        log.info(f"registered service '{service_name}': {list(methods)}")

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接（参照 gRPC HTTP/2 stream handling）"""
        client = writer.get_extra_info("peername")
        try:
            while True:
                req = await read_msg(reader)
                if not req:
                    break

                self.request_count += 1
                t1 = time.perf_counter()

                # 分发到 handler
                service = self.services.get(req["service"])
                if not service:
                    resp = {"id": req["id"], "error": f"Unknown service: {req['service']}"}
                else:
                    handler = service.get(req["method"])
                    if not handler:
                        resp = {"id": req["id"], "error": f"Unknown method: {req['method']}"}
                    else:
                        try:
                            result = handler(**req.get("args", {}))
                            resp = {"id": req["id"], "result": result}
                        except Exception as e:
                            resp = {"id": req["id"], "error": str(e)}

                t2 = time.perf_counter()
                log.debug(f"  {req['service']}.{req['method']} → {(t2-t1)*1000:.1f}ms")

                await write_msg(writer, resp)

        except (asyncio.IncompleteReadError, ConnectionResetError):
            pass
        finally:
            writer.close()

    async def start(self, host="0.0.0.0", port=50051):
        """启动服务（参照 gRPC server.add_insecure_port + serve）"""
        server = await asyncio.start_server(self.handle_client, host, port)
        addr = server.sockets[0].getsockname()
        log.info(f"tinyrpc server on {addr[0]}:{addr[1]}")
        log.info(f"  services: {list(self.services.keys())}")
        async with server:
            await server.serve_forever()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPC 客户端（参照 gRPC Stub）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RPCClient:
    """
    RPC 客户端（参照 gRPC Stub）

    call(service.method(args)) → 序列化 → TCP → 等响应 → 反序列化
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self._next_id = 0

    async def connect(self):
        """连接服务端"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        log.info(f"connected to {self.host}:{self.port}")

    async def call(self, service: str, method: str, **args) -> Any:
        """
        远程调用（参照 gRPC client.method(args)）

        1. 构建请求（序列化）
        2. 发送（TCP）
        3. 等响应（匹配 id）
        4. 返回结果
        """
        self._next_id += 1
        req = {"id": self._next_id, "service": service, "method": method, "args": args}
        await write_msg(self.writer, req)

        # 等待响应
        resp = await read_msg(self.reader)
        if resp.get("error"):
            raise RPCError(resp["error"])
        return resp.get("result")

    def stub(self, service: str) -> "RPCStub":
        """创建服务 Stub（参照 gRPC 的 generated client）"""
        return RPCStub(self, service)

    async def close(self):
        if self.writer:
            self.writer.close()

class RPCStub:
    """
    服务 Stub（参照 gRPC 生成的 xxxStub）

    stub = client.stub("Calculator")
    result = await stub.add(a=1, b=2)
    """
    def __init__(self, client: RPCClient, service: str):
        self._client = client
        self._service = service

    def __getattr__(self, method: str):
        """动态生成方法（参照 gRPC stub 的动态分发）"""
        async def remote_call(**args):
            return await self._client.call(self._service, method, **args)
        return remote_call

class RPCError(Exception):
    pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 示例服务
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculator_add(a: float, b: float) -> float:
    return a + b

def calculator_multiply(a: float, b: float) -> float:
    return a * b

def greeter_say_hello(name: str) -> str:
    return f"Hello, {name}!"

def greeter_say_goodbye(name: str) -> str:
    return f"Goodbye, {name}!"

async def run_server(port=50051):
    """启动服务端"""
    server = RPCServer()
    server.add_service("Calculator", {"add": calculator_add, "multiply": calculator_multiply})
    server.add_service("Greeter", {"say_hello": greeter_say_hello, "say_goodbye": greeter_say_goodbye})
    await server.start(port=port)

async def run_client(host="127.0.0.1", port=50051):
    """客户端测试"""
    await asyncio.sleep(0.5)  # 等服务端起来
    client = RPCClient(host, port)
    await client.connect()

    # 直接调用
    print("\n── 直接调用 ──")
    result = await client.call("Calculator", "add", a=10, b=20)
    print(f"  Calculator.add(10, 20) = {result}")

    result = await client.call("Calculator", "multiply", a=7, b=8)
    print(f"  Calculator.multiply(7, 8) = {result}")

    # Stub 调用（参照 gRPC 生成的 stub）
    print("\n── Stub 调用（像本地函数一样）──")
    calc = client.stub("Calculator")
    result = await calc.add(a=100, b=200)
    print(f"  calc.add(a=100, b=200) = {result}")

    greeter = client.stub("Greeter")
    result = await greeter.say_hello(name="tinyrpc")
    print(f"  greeter.say_hello(name='tinyrpc') = '{result}'")

    # 错误处理
    print("\n── 错误处理 ──")
    try:
        await client.call("Calculator", "divide", a=1, b=0)
    except RPCError as e:
        print(f"  divide(1, 0) → RPCError: {e}")

    try:
        await client.call("Unknown", "method")
    except RPCError as e:
        print(f"  Unknown.method → RPCError: {e}")

    await client.close()

async def main():
    print("tinyrpc — RPC 框架（参照 gRPC/Thrift）\n")

    # 同时启动服务端和客户端
    await asyncio.gather(
        run_server(),
        run_client(),
    )

if __name__ == "__main__":
    asyncio.run(main())
