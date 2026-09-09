#!/usr/bin/env python3
"""tinytrace — 参照 Jaeger/Zipkin 的分布式追踪
参照：Jaeger / Zipkin / OpenTelemetry
csdiy 对应：tinyrpc + tinylog + 分布式
核心：trace_id + span_id + 父子关系 → 可视化调用链"""
import time, uuid, json
from dataclasses import dataclass, field

@dataclass
class Span:
    """一个操作单元（参照 OpenTelemetry Span）"""
    trace_id: str; span_id: str; parent_id: str
    name: str; service: str
    start_time: float; end_time: float = 0
    tags: dict = field(default_factory=dict)
    logs: list = field(default_factory=list)
    def duration_ms(self): return (self.end_time-self.start_time)*1000

class Tracer:
    """追踪器（参照 Jaeger tracer）"""
    def __init__(self, service):
        self.service = service; self.spans = []
    def start_span(self, name, trace_id=None, parent_id=None):
        trace_id = trace_id or uuid.uuid4().hex[:16]
        span_id = uuid.uuid4().hex[:16]
        span = Span(trace_id=trace_id, span_id=span_id, parent_id=parent_id or "",
                    name=name, service=self.service, start_time=time.time())
        return span
    def finish(self, span, **tags):
        span.end_time = time.time(); span.tags.update(tags)
        self.spans.append(span)
    def trace_tree(self, trace_id=None):
        """打印调用链（参照 Jaeger UI 的 trace view）"""
        spans = [s for s in self.spans if not trace_id or s.trace_id==trace_id]
        by_parent = {}
        for s in spans: by_parent.setdefault(s.parent_id, []).append(s)
        def render(parent_id, depth):
            for s in by_parent.get(parent_id, []):
                indent = "  "*depth
                dur = s.duration_ms()
                print(f"  {indent}├─ {s.service}.{s.name} ({dur:.1f}ms) {s.tags}")
                render(s.span_id, depth+1)
        print("  Trace 调用链:")
        render("", 0)

def main():
    print("tinytrace — 分布式追踪（参照 Jaeger/Zipkin）\n")
    # 模拟微服务调用链
    api_tracer = Tracer("api-gateway")
    db_tracer = Tracer("database")
    cache_tracer = Tracer("cache")

    # 主调用
    root = api_tracer.start_span("GET /api/users")
    time.sleep(0.02)

    # 子调用：查缓存
    cache_span = cache_tracer.start_span("GET user:42", trace_id=root.trace_id, parent_id=root.span_id)
    time.sleep(0.005)
    cache_tracer.finish(cache_span, hit=False)

    # 缓存 miss → 查数据库
    db_span = db_tracer.start_span("SELECT * FROM users WHERE id=42",
                                   trace_id=root.trace_id, parent_id=root.span_id)
    time.sleep(0.03)
    db_tracer.finish(db_span, rows=1)

    # 回填缓存
    cache_span2 = cache_tracer.start_span("SET user:42", trace_id=root.trace_id, parent_id=root.span_id)
    time.sleep(0.003)
    cache_tracer.finish(cache_span2, ttl=3600)

    api_tracer.finish(root, status=200)

    # 合并所有 tracer 的 spans
    all_tracer = Tracer("merged")
    all_tracer.spans = api_tracer.spans + cache_tracer.spans + db_tracer.spans
    all_tracer.trace_tree()

    total = sum(s.duration_ms() for s in all_tracer.spans)
    print(f"\n  总耗时: {total:.1f}ms (3 个 span)")
    print(f"  Trace ID: {root.trace_id}")

if __name__ == "__main__": main()
