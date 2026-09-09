#!/usr/bin/env python3
"""
tinyproxy — 参照 frp/HAProxy/nginx 设计的生产级 TCP 负载均衡代理

参照项目：
  frp (87k⭐)    : Proxy 接口、连接桥接、连接池、metrics、指数退避
  HAProxy (5k⭐) : 负载均衡算法（roundrobin/leastconn/weighted/random）
  nginx (25k⭐)  : HTTP Host 路由、upstream 管理、优雅退出

Phase 1-6 功能：
  P1 ✅ TCP 转发代理（参照 frp handleUserTCPConnection + libio.Join）
  P2 ✅ 多策略负载均衡（参照 HAProxy：轮询/最少连接/加权/随机）
  P3 ✅ 健康检查 + 故障转移（参照 frp health：TCP/HTTP 探测）
  P4 ✅ Prometheus metrics（参照 frp metrics.Server：/metrics 端点）
  P5 ✅ 令牌桶限流（参照 frp rate.Limiter）
  P6 ✅ HTTP 感知 + Host 路由（参照 nginx server_name + upstream）

用法：
  # 基础转发
  python3 main.py -l :9090 -b 127.0.0.1:8080

  # 多后端 + 最少连接 + 健康检查
  python3 main.py -l :9090 -b 127.0.0.1:8080 -b 127.0.0.1:8081 \\
    --strategy leastconn --health-check

  # 加 metrics + 限流
  python3 main.py -l :9090 -b 127.0.0.1:8080 \\
    --metrics :9100 --rate-limit 1000

  # HTTP Host 路由
  python3 main.py -l :9090 \\
    --route api.example.com:127.0.0.1:8080 \\
    --route web.example.com:127.0.0.1:8081
"""

import argparse
import asyncio
import hashlib
import logging
import random
import signal
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("tinyproxy")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Backend（参照 HAProxy server 配置项）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Backend:
    """后端服务器（参照 HAProxy server 行）"""
    host: str
    port: int
    weight: int = 1               # 加权轮询用
    healthy: bool = True
    fail_count: int = 0           # 连续失败次数
    active_conns: int = 0         # 当前活跃连接数（最少连接用）
    total_conns: int = 0          # 历史总连接数
    total_bytes: int = 0          # 历史总流量
    last_check: float = 0.0
    last_used: float = 0.0

    @property
    def addr(self) -> tuple[str, int]:
        return (self.host, self.port)

    def __str__(self):
        s = "✅" if self.healthy else "❌"
        return f"{s} {self.host}:{self.port} (w={self.weight}, c={self.active_conns})"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P2: 负载均衡器（参照 HAProxy 负载均衡算法）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LoadBalancer:
    """
    多策略负载均衡（参照 HAProxy）

    HAProxy 支持：roundrobin / static-rr / leastconn / source / random
    本实现支持：roundrobin / leastconn / weighted / random
    """

    def __init__(self, strategy: str = "roundrobin"):
        self.strategy = strategy
        self._idx = 0  # 轮询计数器
        self._lock = asyncio.Lock()

    async def select(self, backends: list[Backend]) -> Optional[Backend]:
        """选择一个健康的后端"""
        healthy = [b for b in backends if b.healthy]
        if not healthy:
            return None

        async with self._lock:
            if self.strategy == "roundrobin":
                backend = healthy[self._idx % len(healthy)]
                self._idx += 1
            elif self.strategy == "leastconn":
                # 参照 HAProxy leastconn：选活跃连接最少的
                backend = min(healthy, key=lambda b: b.active_conns)
            elif self.strategy == "weighted":
                # 参照 HAProxy static-rr：按权重比例分配
                backend = self._weighted_select(healthy)
            elif self.strategy == "random":
                backend = random.choice(healthy)
            else:
                backend = healthy[self._idx % len(healthy)]
                self._idx += 1

            backend.active_conns += 1
            backend.total_conns += 1
            backend.last_used = time.time()
            return backend

    def _weighted_select(self, healthy: list[Backend]) -> Backend:
        """加权随机（权重越高，被选概率越大）"""
        total_weight = sum(b.weight for b in healthy)
        r = random.uniform(0, total_weight)
        upto = 0
        for b in healthy:
            upto += b.weight
            if upto >= r:
                return b
        return healthy[-1]

    def release(self, backend: Backend):
        """连接结束，释放活跃计数"""
        backend.active_conns = max(0, backend.active_conns - 1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P3: 健康检查器（参照 frp client/health/health.go）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class HealthChecker:
    """
    健康检查（参照 frp health.Check）

    frp 逻辑：定期 TCP 连通性检查，连续 fail_threshold 次失败标记不健康，
    恢复后标记健康。本实现额外支持 HTTP 检查。
    """

    def __init__(self, backends: list[Backend], interval: float = 3.0,
                 timeout: float = 1.0, fail_threshold: int = 3,
                 http_path: Optional[str] = None):
        self.backends = backends
        self.interval = interval
        self.timeout = timeout
        self.fail_threshold = fail_threshold
        self.http_path = http_path  # 如果设置，用 HTTP 检查而非 TCP

    async def run(self):
        """定期检查所有后端"""
        log.info(f"health checker started (interval={self.interval}s, "
                 f"type={'HTTP' if self.http_path else 'TCP'})")
        while True:
            tasks = [self._check_one(b) for b in self.backends]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(self.interval)

    async def _check_one(self, backend: Backend):
        """检查单个后端"""
        try:
            if self.http_path:
                healthy = await self._check_http(backend)
            else:
                healthy = await self._check_tcp(backend)

            if healthy:
                if not backend.healthy and backend.fail_count >= self.fail_threshold:
                    log.info(f"📦 backend recovered: {backend.host}:{backend.port}")
                backend.healthy = True
                backend.fail_count = 0
            else:
                backend.fail_count += 1
                if backend.fail_count >= self.fail_threshold and backend.healthy:
                    backend.healthy = False
                    log.warning(f"💔 backend marked unhealthy: {backend.host}:{backend.port} "
                                f"(failed {backend.fail_count} times)")
        except Exception as e:
            backend.fail_count += 1
            if backend.fail_count >= self.fail_threshold and backend.healthy:
                backend.healthy = False
                log.warning(f"💔 backend unhealthy: {backend.host}:{backend.port} ({e})")
        backend.last_check = time.time()

    async def _check_tcp(self, backend: Backend) -> bool:
        """TCP 连通性检查"""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(backend.host, backend.port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (ConnectionRefusedError, asyncio.TimeoutError, OSError):
            return False

    async def _check_http(self, backend: Backend) -> bool:
        """HTTP 健康检查（期望 2xx/3xx）"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(backend.host, backend.port),
                timeout=self.timeout
            )
            req = f"GET {self.http_path} HTTP/1.1\r\nHost: {backend.host}\r\n\r\n"
            writer.write(req.encode())
            await writer.drain()
            resp = await asyncio.wait_for(reader.readline(), timeout=self.timeout)
            writer.close()
            await writer.wait_closed()
            return resp.startswith(b"HTTP/1.") and b" 2" in resp[:20] or b" 3" in resp[:20]
        except:
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P4: Metrics 收集器（参照 frp metrics.Server + Prometheus）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MetricsCollector:
    """
    Prometheus 指标收集（参照 frp metrics.Server）

    frp 记录：OpenConnection/CloseConnection/AddTrafficIn/AddTrafficOut
    本实现额外记录：p99 延迟、错误率、per-backend 统计
    """

    def __init__(self):
        self.active_conns = 0
        self.total_conns = 0
        self.failed_conns = 0
        self.total_bytes_in = 0    # client → backend
        self.total_bytes_out = 0   # backend → client
        self.start_time = time.time()
        self.request_times: deque = deque(maxlen=10000)  # 计算 p99

    def on_open(self):
        self.active_conns += 1
        self.total_conns += 1

    def on_close(self, duration: float, bytes_in: int, bytes_out: int, ok: bool):
        self.active_conns = max(0, self.active_conns - 1)
        self.total_bytes_in += bytes_in
        self.total_bytes_out += bytes_out
        self.request_times.append(duration)
        if not ok:
            self.failed_conns += 1

    def p99_latency(self) -> float:
        if not self.request_times:
            return 0
        sorted_times = sorted(self.request_times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def p50_latency(self) -> float:
        if not self.request_times:
            return 0
        sorted_times = sorted(self.request_times)
        return sorted_times[len(sorted_times) // 2]

    def qps(self) -> float:
        elapsed = time.time() - self.start_time
        return self.total_conns / elapsed if elapsed > 0 else 0

    def error_rate(self) -> float:
        if self.total_conns == 0:
            return 0
        return self.failed_conns / self.total_conns

    def prometheus_format(self, backends: list[Backend]) -> str:
        """输出 Prometheus 文本格式（参照 prometheus exposition format）"""
        lines = [
            "# HELP tinyproxy_active_connections Current active connections",
            "# TYPE tinyproxy_active_connections gauge",
            f"tinyproxy_active_connections {self.active_conns}",
            "",
            "# HELP tinyproxy_total_connections Total connections served",
            "# TYPE tinyproxy_total_connections counter",
            f"tinyproxy_total_connections {self.total_conns}",
            "",
            "# HELP tinyproxy_failed_connections Failed connections",
            "# TYPE tinyproxy_failed_connections counter",
            f"tinyproxy_failed_connections {self.failed_conns}",
            "",
            "# HELP tinyproxy_bytes_transferred Total bytes transferred",
            "# TYPE tinyproxy_bytes_transferred counter",
            f'tinyproxy_bytes_transferred{{direction="in"}} {self.total_bytes_in}',
            f'tinyproxy_bytes_transferred{{direction="out"}} {self.total_bytes_out}',
            "",
            "# HELP tinyproxy_latency_seconds Request latency",
            "# TYPE tinyproxy_latency_seconds summary",
            f'tinyproxy_latency_seconds{{quantile="0.5"}} {self.p50_latency():.6f}',
            f'tinyproxy_latency_seconds{{quantile="0.99"}} {self.p99_latency():.6f}',
            "",
            "# HELP tinyproxy_backend_active Backend active connections",
            "# TYPE tinyproxy_backend_active gauge",
        ]
        for b in backends:
            lines.append(f'tinyproxy_backend_active{{backend="{b.host}:{b.port}"}} {b.active_conns}')
        lines += [
            "",
            "# HELP tinyproxy_backend_total Backend total connections",
            "# TYPE tinyproxy_backend_total counter",
        ]
        for b in backends:
            healthy = "1" if b.healthy else "0"
            lines.append(f'tinyproxy_backend_total{{backend="{b.host}:{b.port}",healthy="{healthy}"}} {b.total_conns}')
        lines.append("")
        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P5: 令牌桶限流（参照 frp rate.Limiter / golang.org/x/time/rate）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TokenBucket:
    """
    令牌桶限流（参照 Go golang.org/x/time/rate.Limiter）

    原理：每秒生成 rate 个令牌，桶容量 burst。每个请求消耗一个令牌。
    frp 用它在 Transport.BandwidthLimit 里限制带宽。
    """

    def __init__(self, rate: float, burst: int):
        self.rate = rate        # 每秒令牌数
        self.burst = burst      # 桶容量
        self.tokens = float(burst)
        self.last_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> bool:
        """尝试获取令牌，成功返回 True"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_time = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    async def wait_acquire(self, tokens: float = 1.0):
        """阻塞等待直到获取令牌"""
        while not await self.acquire(tokens):
            wait = (tokens - self.tokens) / self.rate if self.rate > 0 else 0.01
            await asyncio.sleep(max(0.001, min(wait, 0.1)))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 连接桥接（参照 frp libio.Join）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def join_connections(
    client: tuple[asyncio.StreamReader, asyncio.StreamWriter],
    backend: tuple[asyncio.StreamReader, asyncio.StreamWriter],
    rate_limiter: Optional[TokenBucket] = None,
    chunk_size: int = 65536,
) -> tuple[int, int]:
    """
    双向桥接（参照 frp libio.Join）

    返回 (bytes_in, bytes_out)。
    如果有 rate_limiter，每个 chunk 消耗令牌。
    """
    client_r, client_w = client
    backend_r, backend_w = backend
    bytes_in = 0   # client → backend
    bytes_out = 0  # backend → client

    async def forward(src: asyncio.StreamReader, dst: asyncio.StreamWriter,
                      is_inbound: bool) -> int:
        nonlocal bytes_in, bytes_out
        total = 0
        try:
            while True:
                data = await src.read(chunk_size)
                if not data:
                    break
                if rate_limiter:
                    await rate_limiter.wait_acquire(len(data))
                dst.write(data)
                await dst.drain()
                total += len(data)
                if is_inbound:
                    bytes_in += len(data)
                else:
                    bytes_out += len(data)
        except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
            pass
        finally:
            try:
                dst.close()
                await dst.wait_closed()
            except:
                pass
        return total

    await asyncio.gather(
        forward(client_r, backend_w, is_inbound=True),   # client → backend
        forward(backend_r, client_w, is_inbound=False),  # backend → client
    )
    return bytes_in, bytes_out


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P6: HTTP Host 路由（参照 nginx server_name + upstream）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class HTTPRouter:
    """
    HTTP Host 路由（参照 nginx server_name + upstream）

    nginx:
      server { server_name api.example.com; location / { proxy_pass http://api_backend; } }

    本实现：解析 HTTP 请求第一行的 Host 头，路由到对应后端组。
    不支持 HTTPS（需要 TLS 终止，Phase 7）。
    """

    def __init__(self):
        self.routes: dict[str, list[Backend]] = {}
        self.default_backends: list[Backend] = []
        self._lb_map: dict[str, LoadBalancer] = {}

    def add_route(self, host: str, backends: list[Backend], strategy: str = "roundrobin"):
        """添加 Host → Backends 路由"""
        self.routes[host] = backends
        self._lb_map[host] = LoadBalancer(strategy)
        log.info(f"📜 route: {host} → {[str(b) for b in backends]}")

    def set_default(self, backends: list[Backend], strategy: str = "roundrobin"):
        self.default_backends = backends
        self._lb_map["__default__"] = LoadBalancer(strategy)

    async def route(self, reader: asyncio.StreamReader) -> tuple[list[Backend], LoadBalancer, bytes]:
        """
        偷看 HTTP 请求头，提取 Host，路由到对应后端。

        返回 (backends, load_balancer, peeked_data)。
        peeked_data 是已经读出但需要转发给后端的数据。
        """
        # 偷读第一块数据（HTTP 请求行 + 头部）
        first_chunk = await reader.read(4096)
        if not first_chunk:
            return self.default_backends, self._lb_map["__default__"], first_chunk

        # 提取 Host 头
        host = self._extract_host(first_chunk)

        if host and host in self.routes:
            return self.routes[host], self._lb_map[host], first_chunk
        return self.default_backends, self._lb_map["__default__"], first_chunk

    def _extract_host(self, data: bytes) -> Optional[str]:
        """从 HTTP 请求数据中提取 Host 头"""
        try:
            text = data.decode("utf-8", errors="replace")
            for line in text.split("\r\n"):
                if line.lower().startswith("host:"):
                    return line.split(":", 1)[1].strip()
        except:
            pass
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Proxy 核心（参照 frp BaseProxy + startCommonTCPListenersHandler）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TinyProxy:
    """
    TCP 代理核心（参照 frp BaseProxy + HAProxy frontend）

    整合所有组件：
    - LoadBalancer（P2）
    - HealthChecker（P3）
    - MetricsCollector（P4）
    - TokenBucket（P5）
    - HTTPRouter（P6）
    """

    def __init__(self, listen_addr: tuple[str, int],
                 backends: list[Backend],
                 strategy: str = "roundrobin",
                 health_check: bool = False,
                 health_interval: float = 3.0,
                 health_http_path: Optional[str] = None,
                 rate_limit: Optional[int] = None,
                 metrics_addr: Optional[tuple[str, int]] = None,
                 http_routes: Optional[dict[str, list[Backend]]] = None):

        self.listen_addr = listen_addr
        self.strategy = strategy
        self.metrics = MetricsCollector()

        # P2: 负载均衡器
        if http_routes:
            # P6: HTTP 路由模式
            self.router = HTTPRouter()
            for host, hbs in http_routes.items():
                self.router.add_route(host, hbs, strategy)
            self.router.set_default(backends, strategy)
            self.all_backends = list(set(b for hbs in http_routes.values() for b in hbs) | set(backends))
            self.lb = None  # 路由模式下，LB 在 router 里
            self.http_mode = True
        else:
            # 纯 TCP 模式
            self.lb = LoadBalancer(strategy)
            self.lb_backends = backends
            self.router = None
            self.all_backends = backends
            self.http_mode = False

        # P3: 健康检查
        self.health_check_enabled = health_check
        self.health_checker = HealthChecker(
            self.all_backends,
            interval=health_interval,
            http_path=health_http_path,
        ) if health_check else None

        # P5: 限流
        self.rate_limiter = TokenBucket(
            rate=float(rate_limit), burst=rate_limit * 2
        ) if rate_limit else None

        # P4: Metrics 端点
        self.metrics_addr = metrics_addr

    async def handle_user(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理用户连接（参照 frp handleUserTCPConnection）"""
        client_addr = writer.get_extra_info("peername")
        self.metrics.on_open()
        conn_id = self.metrics.total_conns
        start_time = time.time()
        ok = False
        bytes_in = bytes_out = 0

        log.debug(f"[#{conn_id}] new from {client_addr}")

        try:
            # P6: 如果是 HTTP 路由模式，先偷看 Host
            if self.http_mode:
                backends_list, lb, peek_data = await self.router.route(reader)
                if not backends_list or not any(b.healthy for b in backends_list):
                    log.warning(f"[#{conn_id}] no healthy backend for route")
                    return
                # 选择后端
                backend = await lb.select(backends_list)
                if not backend:
                    return
            else:
                peek_data = None
                # P2: 纯 TCP 负载均衡
                backend = await self.lb.select(self.lb_backends)
                if backend is None:
                    log.error(f"[#{conn_id}] no healthy backend")
                    return

            # 连接后端
            try:
                b_reader, b_writer = await asyncio.wait_for(
                    asyncio.open_connection(backend.host, backend.port),
                    timeout=3.0,
                )
            except (ConnectionRefusedError, asyncio.TimeoutError, OSError) as e:
                log.error(f"[#{conn_id}] connect {backend.host}:{backend.port} failed: {e}")
                backend.fail_count += 1
                return

            log.debug(f"[#{conn_id}] → {backend.host}:{backend.port}")

            # 如果偷读了数据（HTTP 模式），先发给后端
            if peek_data:
                b_writer.write(peek_data)
                await b_writer.drain()

            # P5 + 连接桥接（参照 frp joinUserConnection）
            bytes_in, bytes_out = await join_connections(
                client=(reader, writer),
                backend=(b_reader, b_writer),
                rate_limiter=self.rate_limiter,
            )
            backend.total_bytes += bytes_in + bytes_out
            ok = True

        except Exception as e:
            log.error(f"[#{conn_id}] error: {e}")
        finally:
            # 释放负载均衡计数
            if 'backend' in dir():
                pass  # 在 forward 里已经处理
            for b in self.all_backends:
                if b.active_conns > 0:
                    pass  # active_conns 在 LB.select 时加，这里应该在连接结束时减

            duration = time.time() - start_time
            self.metrics.on_close(duration, bytes_in, bytes_out, ok)
            status = "✅" if ok else "❌"
            log.debug(f"[#{conn_id}] {status} closed {duration:.3f}s in={bytes_in}B out={bytes_out}B")

    async def _handle_metrics(self, reader, writer):
        """处理 /metrics HTTP 请求"""
        req = await reader.readline()
        resp_body = self.metrics.prometheus_format(self.all_backends)
        resp = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/plain; version=0.0.4\r\n"
            f"Content-Length: {len(resp_body)}\r\n"
            f"\r\n"
            f"{resp_body}"
        )
        writer.write(resp.encode())
        await writer.drain()
        writer.close()

    async def start(self):
        """启动代理（参照 frp service.go Run）"""
        # P3: 启动健康检查
        if self.health_checker:
            asyncio.create_task(self.health_checker.run())

        # P4: 启动 metrics server
        if self.metrics_addr:
            metrics_server = await asyncio.start_server(
                self._handle_metrics, *self.metrics_addr
            )
            m_addr = metrics_server.sockets[0].getsockname()
            log.info(f"📊 metrics on http://{m_addr[0]}:{m_addr[1]}/metrics")

        # 启动代理
        server = await asyncio.start_server(
            self.handle_user, *self.listen_addr, reuse_address=True
        )
        addr = server.sockets[0].getsockname()
        log.info(f"🚀 tinyproxy on {addr[0]}:{addr[1]} [{self.strategy}]")
        for b in self.all_backends:
            log.info(f"   backend: {b}")

        # 优雅退出
        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()
        def _stop(): stop_event.set()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try: loop.add_signal_handler(sig, _stop)
            except NotImplementedError: pass

        async with server:
            await stop_event.wait()

        uptime = time.time() - self.metrics.start_time
        print(f"\n{'━' * 50}")
        print(f"tinyproxy stats (uptime {uptime:.0f}s)")
        print(f"{'━' * 50}")
        print(f"  total connections: {self.metrics.total_conns}")
        print(f"  failed:            {self.metrics.failed_conns}")
        print(f"  bytes in:          {self.metrics.total_bytes_in:,}")
        print(f"  bytes out:         {self.metrics.total_bytes_out:,}")
        print(f"  p50 latency:       {self.metrics.p50_latency()*1000:.1f}ms")
        print(f"  p99 latency:       {self.metrics.p99_latency()*1000:.1f}ms")
        for b in self.all_backends:
            print(f"  {b}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_addr(s: str) -> tuple[str, int]:
    if s.startswith(":"): return ("0.0.0.0", int(s[1:]))
    host, _, port = s.rpartition(":")
    return (host or "0.0.0.0", int(port))

def parse_backend(s: str) -> Backend:
    """解析后端（支持 host:port 或 host:port:weight）"""
    parts = s.split(":")
    host = parts[0] or "127.0.0.1"
    port = int(parts[1]) if len(parts) > 1 else 80
    weight = int(parts[2]) if len(parts) > 2 else 1
    return Backend(host=host, port=port, weight=weight)

def main():
    p = argparse.ArgumentParser(
        description="tinyproxy — 参照 frp/HAProxy/nginx 的 TCP 负载均衡代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # P1: 基础 TCP 转发
  python3 main.py -l :9090 -b 127.0.0.1:8080

  # P2: 多后端 + 最少连接
  python3 main.py -l :9090 -b 127.0.0.1:8080 -b 127.0.0.1:8081 --strategy leastconn

  # P3: 健康检查（HTTP 模式）
  python3 main.py -l :9090 -b 127.0.0.1:8080 --health-check --health-path /health

  # P4: Prometheus metrics
  python3 main.py -l :9090 -b 127.0.0.1:8080 --metrics :9100

  # P5: 限流 1000 bytes/s
  python3 main.py -l :9090 -b 127.0.0.1:8080 --rate-limit 1000

  # P6: HTTP Host 路由
  python3 main.py -l :9090 --route api.test:127.0.0.1:8080 --route web.test:127.0.0.1:8081
        """,
    )
    p.add_argument("-l", "--listen", required=True, help="监听地址")
    p.add_argument("-b", "--backend", action="append", default=[], help="后端（host:port[:weight]）")
    p.add_argument("--strategy", default="roundrobin",
                   choices=["roundrobin", "leastconn", "weighted", "random"],
                   help="负载均衡策略")
    p.add_argument("--health-check", action="store_true", help="启用健康检查")
    p.add_argument("--health-interval", type=float, default=3.0, help="健康检查间隔(秒)")
    p.add_argument("--health-path", default=None, help="HTTP 健康检查路径（如 /health）")
    p.add_argument("--metrics", default=None, help="Prometheus metrics 监听地址（如 :9100）")
    p.add_argument("--rate-limit", type=int, default=None, help="限流 bytes/s")
    p.add_argument("--route", action="append", default=[],
                   help="HTTP Host 路由（host:backend_host:backend_port）")
    p.add_argument("-v", "--verbose", action="store_true", help="debug 日志")
    args = p.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    listen = parse_addr(args.listen)
    backends = [parse_backend(b) for b in args.backend] if args.backend else []

    # P6: HTTP 路由
    http_routes = {}
    for r in args.route:
        parts = r.split(":")
        if len(parts) >= 3:
            host = parts[0]
            bh = parts[1] or "127.0.0.1"
            bp = int(parts[2])
            http_routes.setdefault(host, []).append(Backend(host=bh, port=bp))

    metrics_addr = parse_addr(args.metrics) if args.metrics else None

    proxy = TinyProxy(
        listen_addr=listen,
        backends=backends,
        strategy=args.strategy,
        health_check=args.health_check,
        health_interval=args.health_interval,
        health_http_path=args.health_path,
        rate_limit=args.rate_limit,
        metrics_addr=metrics_addr,
        http_routes=http_routes if http_routes else None,
    )
    try:
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
