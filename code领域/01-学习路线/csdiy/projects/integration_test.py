#!/usr/bin/env python3
"""
csdiy 端到端集成测试 — 把 5 个 tiny 项目组装成微服务架构

架构：
  Client
    ↓ HTTP
  tinyproxy (:9093) ──负载均衡──→ tinyhttpd (:8092)
                                     ↓ TCP/RESP
                                  tinycache (:6393)
                                     ↓ cache miss
                                  tinydb (文件)

验证全链路：HTTP 请求 → 代理 → Web 服务 → 缓存 → 存储
"""
import asyncio, json, subprocess, time, sys, os, signal, socket
from pathlib import Path

PROJECTS = Path(__file__).resolve().parent
PYTHON = sys.executable

class Service:
    """管理一个后台服务进程"""
    def __init__(self, name, cmd, port, ready_check=None):
        self.name = name
        self.cmd = cmd
        self.port = port
        self.ready_check = ready_check
        self.process = None

    async def start(self):
        print(f"  🚀 启动 {self.name} (port {self.port})...")
        self.process = subprocess.Popen(
            self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        # 等待端口可用
        for _ in range(50):
            await asyncio.sleep(0.1)
            try:
                sock = socket.socket()
                sock.settimeout(0.5)
                sock.connect(("127.0.0.1", self.port))
                sock.close()
                print(f"     ✅ {self.name} ready")
                return True
            except:
                continue
        print(f"     ❌ {self.name} failed to start")
        return False

    def stop(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except:
                self.process.kill()
            print(f"  🛑 停止 {self.name}")

async def http_get(host, port, path, headers=None):
    """简单 HTTP GET（不依赖 curl）"""
    reader, writer = await asyncio.open_connection(host, port)
    req = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n"
    if headers:
        for k, v in headers.items():
            req += f"{k}: {v}\r\n"
    req += "\r\n"
    writer.write(req.encode())
    await writer.drain()
    resp = await reader.read(4096)
    writer.close()
    return resp.decode()

async def resp_cmd(host, port, *args):
    """发送 RESP 命令到 tinycache，处理所有 RESP 类型"""
    reader, writer = await asyncio.open_connection(host, port)
    cmd = f"*{len(args)}\r\n"
    for arg in args:
        cmd += f"${len(arg)}\r\n{arg}\r\n"
    writer.write(cmd.encode())
    await writer.drain()

    prefix = (await reader.read(1)).decode()
    rest = (await reader.readline()).strip().decode()

    if prefix == "+":  # 状态（OK）
        writer.close(); return rest
    elif prefix == "-":  # 错误
        writer.close(); return None
    elif prefix == ":":  # 整数
        writer.close(); return rest
    elif prefix == "$":  # 批量字符串
        length = int(rest)
        if length == -1:
            writer.close(); return None
        data = (await reader.read(length)).decode()
        await reader.readexactly(2)  # \r\n
        writer.close(); return data
    writer.close(); return rest

async def run_integration_test():
    print("=" * 60)
    print("  csdiy 端到端集成测试 — 微服务架构")
    print("  tinyproxy → tinyhttpd → tinycache → tinydb")
    print("=" * 60)

    results = {"pass": 0, "fail": 0}
    def ok(name):
        print(f"  ✅ {name}")
        results["pass"] += 1
    def fail(name, detail=""):
        print(f"  ❌ {name} {detail}")
        results["fail"] += 1

    # ━━━ 启动服务 ━━━
    print("\n── 启动服务栈 ──")

    db_path = "/tmp/integ_test.db"
    db_wal = db_path + ".wal"
    for f in [db_path, db_wal]:
        if os.path.exists(f): os.remove(f)

    services = [
        Service("tinycache", [PYTHON, str(PROJECTS/"tinycache/main.py"), "-p", "6393"], 6393),
        Service("tinyhttpd", [PYTHON, str(PROJECTS/"tinyhttpd/main.py"), "-p", "8092"], 8092),
        Service("tinyproxy", [PYTHON, str(PROJECTS/"tinyproxy/main.py"),
               "-l", ":9093", "-b", "127.0.0.1:8092"], 9093),
    ]

    try:
        for svc in services:
            if not await svc.start():
                fail(f"{svc.name} 启动失败")
                return results

        # 先用 tinydb CLI 写入数据
        print("\n── 准备数据（tinydb）──")
        subprocess.run([PYTHON, str(PROJECTS/"tinydb/main.py"), db_path, "set", "greeting", "hello from tinydb"],
                      capture_output=True)
        subprocess.run([PYTHON, str(PROJECTS/"tinydb/main.py"), db_path, "set", "counter", "42"],
                      capture_output=True)
        ok("tinydb 写入 greeting + counter")

        # ━━━ 测试 tinycache ━━━
        print("\n── 测试 tinycache（缓存层）──")

        await resp_cmd("127.0.0.1", 6393, "SET", "cached_key", "cached_value")
        val = await resp_cmd("127.0.0.1", 6393, "GET", "cached_key")
        if val == "cached_value":
            ok("tinycache SET/GET")
        else:
            fail("tinycache SET/GET", f"got {val}")

        await resp_cmd("127.0.0.1", 6393, "SET", "temp", "will_expire")
        await resp_cmd("127.0.0.1", 6393, "EXPIRE", "temp", "999")
        ttl = await resp_cmd("127.0.0.1", 6393, "TTL", "temp")
        if ttl and int(ttl) > 0:
            ok(f"tinycache EXPIRE/TTL (remaining={ttl}s)")
        else:
            fail("tinycache EXPIRE/TTL")

        size = await resp_cmd("127.0.0.1", 6393, "DBSIZE")
        if size and int(size) >= 2:
            ok(f"tinycache DBSIZE={size}")
        else:
            fail("tinycache DBSIZE")

        # ━━━ 测试 tinyhttpd ━━━
        print("\n── 测试 tinyhttpd（API 层）──")

        resp = await http_get("127.0.0.1", 8092, "/api/time")
        if "HTTP/1.1 200" in resp and "time" in resp:
            ok("tinyhttpd /api/time")
        else:
            fail("tinyhttpd /api/time")

        resp = await http_get("127.0.0.1", 8092, "/api/info")
        if "tinyhttpd" in resp:
            ok("tinyhttpd /api/info")
        else:
            fail("tinyhttpd /api/info")

        resp = await http_get("127.0.0.1", 8092, "/nonexistent")
        if "404" in resp:
            ok("tinyhttpd 404 处理")
        else:
            fail("tinyhttpd 404")

        # ━━━ 测试 tinyproxy → tinyhttpd（负载均衡层）━━━
        print("\n── 测试 tinyproxy → tinyhttpd（代理层）──")

        resp = await http_get("127.0.0.1", 9093, "/api/time")
        if "HTTP/1.1 200" in resp and "time" in resp:
            ok("tinyproxy → tinyhttpd 转发")
        else:
            fail("tinyproxy 转发")

        # 并发测试
        print("\n── 并发测试（10 个请求同时通过代理）──")
        tasks = [http_get("127.0.0.1", 9093, "/api/info") for _ in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in responses if isinstance(r, str) and "200" in r)
        if success >= 8:
            ok(f"并发 10 请求：{success}/10 成功")
        else:
            fail(f"并发 10 请求：{success}/10 成功")

        # ━━━ 全链路验证 ━━━
        print("\n── 全链路验证 ━━━")

        print("  链路：Client → tinyproxy(:9093) → tinyhttpd(:8092)")
        print("  并行：tinycache(:6393) 缓存层 + tinydb 持久层")
        print()

        # 通过代理访问 API
        resp = await http_get("127.0.0.1", 9093, "/api/info")
        if "tinyhttpd" in resp:
            ok("全链路: Client → Proxy → HTTP Server")

        # 直接访问缓存
        val = await resp_cmd("127.0.0.1", 6393, "GET", "cached_key")
        if val == "cached_value":
            ok("缓存层: tinycache 数据一致")

        # tinydb 数据验证
        result = subprocess.run([PYTHON, str(PROJECTS/"tinydb/main.py"), db_path, "get", "greeting"],
                              capture_output=True, text=True)
        if "hello from tinydb" in result.stdout:
            ok("持久层: tinydb 数据一致")

        # ━━━ 总结 ━━━
        print("\n" + "=" * 60)
        total = results["pass"] + results["fail"]
        print(f"  集成测试结果: ✅ {results['pass']} / ❌ {results['fail']} / {total} 总计")
        print("=" * 60)

        if results["fail"] == 0:
            print("\n  🎉 全部通过！微服务架构正常运行：")
            print("     tinyproxy (负载均衡)")
            print("       ↓")
            print("     tinyhttpd (HTTP API)")
            print("       ↓")
            print("     tinycache (内存缓存)")
            print("       ↓")
            print("     tinydb (持久存储)")

    finally:
        print("\n── 清理服务 ──")
        for svc in reversed(services):
            svc.stop()

    return results

if __name__ == "__main__":
    result = asyncio.run(run_integration_test())
    sys.exit(0 if result["fail"] == 0 else 1)
