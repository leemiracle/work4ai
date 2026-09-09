#!/usr/bin/env python3
"""
tinyhttpd — 参照 nginx + Go net/http 的迷你 HTTP 服务器

参照：nginx (HTTP解析+路由) + Go net/http (Handler接口)
csdiy 对应：network-程序员视角 + CS144 (HTTP协议)

功能：HTTP/1.1 解析 → 路由 → 静态文件 + JSON API + 反向代理
"""
import asyncio, os, json, time, mimetypes, logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinyhttpd")

class Request:
    """HTTP 请求（参照 nginx ngx_http_request_t）"""
    def __init__(self):
        self.method = ""
        self.path = ""
        self.version = "HTTP/1.1"
        self.headers = {}
        self.body = b""

class Router:
    """路由器（参照 nginx location + Go http.ServeMux）"""
    def __init__(self):
        self.routes = {}  # (method, pattern) → handler

    def add(self, method, pattern, handler):
        self.routes[(method, pattern)] = handler

    def get(self, pattern, handler): self.add("GET", pattern, handler)
    def post(self, pattern, handler): self.add("POST", pattern, handler)

    def match(self, method, path):
        """匹配路由（简化版：精确匹配 + 前缀匹配）"""
        if (method, path) in self.routes:
            return self.routes[(method, path)]
        for (m, pattern), handler in self.routes.items():
            if m == method and path.startswith(pattern.rstrip('/')):
                return handler
        return None

class HTTPServer:
    """HTTP 服务器（参照 nginx worker 进程）"""
    def __init__(self, router: Router, static_dir: str = None):
        self.router = router
        self.static_dir = static_dir
        self.start_time = time.time()
        self.request_count = 0

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理连接（参照 nginx ngx_http_process_request）"""
        client = writer.get_extra_info("peername")
        self.request_count += 1

        try:
            req = await self._parse_request(reader)
            if not req:
                return

            log.debug(f"{client[0]}:{client[1]} → {req.method} {req.path}")

            # 路由匹配
            handler = self.router.match(req.method, req.path)
            if handler:
                status, headers, body = handler(req)
            elif self.static_dir:
                status, headers, body = self._serve_static(req.path)
            else:
                status, headers, body = 404, {}, b"Not Found"

            resp = self._build_response(status, headers, body)
            writer.write(resp)
            await writer.drain()

        except (ConnectionResetError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()
            try: await writer.wait_closed()
            except: pass

    async def _parse_request(self, reader) -> Request:
        """解析 HTTP 请求（参照 nginx HTTP 解析器）"""
        req = Request()
        # 请求行
        line = await reader.readline()
        if not line:
            return None
        parts = line.decode().strip().split()
        if len(parts) < 2:
            return None
        req.method = parts[0]
        req.path = urlparse(parts[1]).path
        if len(parts) > 2:
            req.version = parts[2]

        # 头部
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            try:
                k, v = line.decode().strip().split(":", 1)
                req.headers[k.strip().lower()] = v.strip()
            except ValueError:
                continue

        # Body
        cl = int(req.headers.get("content-length", 0))
        if cl > 0:
            req.body = await reader.readexactly(cl)
        return req

    def _serve_static(self, path):
        """静态文件服务（参照 nginx root + try_files）"""
        if path == "/":
            path = "/index.html"
        filepath = os.path.join(self.static_dir, path.lstrip("/"))

        # 安全检查：防止路径穿越（参照 nginx 的路径安全检查）
        if ".." in path or not os.path.realpath(filepath).startswith(os.path.realpath(self.static_dir)):
            return 403, {}, b"Forbidden"

        if not os.path.isfile(filepath):
            return 404, {}, b"Not Found"

        with open(filepath, "rb") as f:
            data = f.read()
        ctype = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        return 200, {"Content-Type": ctype}, data

    def _build_response(self, status, headers, body):
        """构建 HTTP 响应"""
        reason = {200:"OK", 301:"Moved Permanently", 302:"Found", 400:"Bad Request",
                  403:"Forbidden", 404:"Not Found", 500:"Internal Server Error"}.get(status, "Unknown")
        lines = [f"HTTP/1.1 {status} {reason}"]
        default_headers = {
            "Content-Length": str(len(body)),
            "Connection": "close",
            "Server": "tinyhttpd/1.0",
            "Date": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()),
        }
        default_headers.update(headers)
        for k, v in default_headers.items():
            lines.append(f"{k}: {v}")
        return ("\r\n".join(lines) + "\r\n\r\n").encode() + body

    async def start(self, host="0.0.0.0", port=8000):
        server = await asyncio.start_server(self.handle, host, port, reuse_address=True)
        addr = server.sockets[0].getsockname()
        log.info(f"tinyhttpd on http://{addr[0]}:{addr[1]}")
        if self.static_dir:
            log.info(f"  static dir: {self.static_dir}")
        for (m, p), _ in self.router.routes.items():
            log.info(f"  route: {m} {p}")
        async with server:
            await server.serve_forever()

def json_response(data, status=200):
    """JSON 辅助函数"""
    body = json.dumps(data, ensure_ascii=False).encode()
    return status, {"Content-Type": "application/json"}, body

def html_response(html, status=200):
    return status, {"Content-Type": "text/html; charset=utf-8"}, html.encode() if isinstance(html, str) else html

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinyhttpd — 参照 nginx 的 HTTP 服务器")
    p.add_argument("-p","--port", type=int, default=8000)
    p.add_argument("-d","--dir", default=None, help="静态文件目录")
    p.add_argument("-v","--verbose", action="store_true")
    args = p.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    router = Router()
    # 默认 API 路由
    router.get("/api/time", lambda req: json_response({"time": time.time(), "iso": time.ctime()}))
    router.get("/api/info", lambda req: json_response({
        "server": "tinyhttpd/1.0",
        "endpoints": [f"{m} {p}" for (m,p) in router.routes],
    }))
    router.get("/api/echo", lambda req: json_response({"path": req.path, "headers": req.headers}))

    server = HTTPServer(router, static_dir=args.dir)
    try:
        asyncio.run(server.start(port=args.port))
    except KeyboardInterrupt:
        log.info(f"stopped. served {server.request_count} requests")

if __name__ == "__main__":
    main()
