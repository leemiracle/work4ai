#!/usr/bin/env python3
"""tinymetrics — 参照 prometheus_client 的 metrics 收集
参照：Prometheus client / Micrometer / StatsD
csdiy 对应：tinyproxy(metrics) + perf
核心：Counter / Gauge / Histogram + /metrics 端点"""
import time, asyncio, math
from dataclasses import dataclass, field
from collections import defaultdict

class Counter:
    """只增不减的计数器（参照 prometheus Counter）"""
    def __init__(self, name, help=""): self.name=name; self.help=help; self.value=0; self.labels={}
    def inc(self, n=1): self.value += n
    def get(self): return self.value

class Gauge:
    """可增可减的仪表（参照 prometheus Gauge）"""
    def __init__(self, name, help=""): self.name=name; self.help=help; self.value=0
    def set(self, v): self.value=v
    def inc(self, n=1): self.value+=n
    def dec(self, n=1): self.value-=n
    def get(self): return self.value

class Histogram:
    """直方图（参照 prometheus Histogram）"""
    def __init__(self, name, buckets=None, help=""):
        self.name=name; self.help=help
        self.buckets = buckets or [0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10]
        self.counts = [0]*(len(self.buckets)+1)  # +1 for +Inf
        self.sum = 0.0; self.count = 0
    def observe(self, v):
        self.sum += v; self.count += 1
        for i, b in enumerate(self.buckets):
            if v <= b: self.counts[i]+=1; return
        self.counts[-1]+=1
    def percentile(self, p):
        if self.count==0: return 0
        target = self.count * p / 100
        cum = 0
        for i, c in enumerate(self.counts):
            cum += c
            if cum >= target:
                return self.buckets[min(i, len(self.buckets)-1)]
        return float('inf')

class MetricsRegistry:
    """指标注册中心（参照 prometheus Registry）"""
    def __init__(self): self.metrics = {}
    def counter(self, name, help=""):
        if name not in self.metrics: self.metrics[name] = Counter(name, help)
        return self.metrics[name]
    def gauge(self, name, help=""):
        if name not in self.metrics: self.metrics[name] = Gauge(name, help)
        return self.metrics[name]
    def histogram(self, name, **kw):
        if name not in self.metrics: self.metrics[name] = Histogram(name, **kw)
        return self.metrics[name]
    def expose(self):
        """输出 Prometheus 格式（参照 /metrics 端点）"""
        lines = []
        for name, m in self.metrics.items():
            if isinstance(m, Counter):
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {m.get()}")
            elif isinstance(m, Gauge):
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {m.get()}")
            elif isinstance(m, Histogram):
                lines.append(f"# TYPE {name} histogram")
                for i, b in enumerate(m.buckets):
                    lines.append(f'{name}_bucket{{le="{b}"}} {m.counts[i]}')
                lines.append(f'{name}_bucket{{le="+Inf"}} {m.count}')
                lines.append(f"{name}_sum {m.sum}")
                lines.append(f"{name}_count {m.count}")
        return "\n".join(lines)

def main():
    print("tinymetrics — Prometheus 兼容 metrics（参照 prometheus_client）\n")
    reg = MetricsRegistry()
    requests = reg.counter("http_requests_total", "Total HTTP requests")
    active = reg.gauge("active_connections", "Current connections")
    latency = reg.histogram("request_duration_seconds", buckets=[0.01,0.05,0.1,0.5,1,5])

    # 模拟请求
    import random
    for _ in range(1000):
        requests.inc()
        active.set(random.randint(1, 50))
        latency.observe(random.expovariate(5))  # 平均 200ms

    active.set(10)
    print(reg.expose())
    print(f"\n  p50 latency: {latency.percentile(50)*1000:.1f}ms")
    print(f"  p99 latency: {latency.percentile(99)*1000:.1f}ms")
    print(f"  total requests: {requests.get()}")

if __name__ == "__main__": main()
