#!/usr/bin/env python3
"""tinystream — 参照 Flink/Spark Streaming 的流处理引擎
参照：Apache Flink / Spark Streaming / Kafka Streams
csdiy 对应：tinykafka + tinymapreduce + tinysearch
核心：窗口 + 算子链（map/filter/reduce）+ watermark"""
import time
from collections import deque, defaultdict
from dataclasses import dataclass

@dataclass
class Event:
    key: str; value: float; timestamp: float = 0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()

class StreamOperator:
    """流算子基类（参照 Flink StreamOperator）"""
    def process(self, event): pass

class MapOperator(StreamOperator):
    def __init__(self, fn): self.fn = fn
    def process(self, e): r = self.fn(e); return r if r else []

class FilterOperator(StreamOperator):
    def __init__(self, pred): self.pred = pred
    def process(self, e): return [e] if self.pred(e) else []

class WindowOperator(StreamOperator):
    """滑动窗口（参照 Flink SlidingWindow）
    每 slide 秒输出过去 window 秒的聚合"""
    def __init__(self, window_size, slide, agg_fn):
        self.window_size=window_size; self.slide=slide; self.agg_fn=agg_fn
        self.buffer = defaultdict(list)
    def process(self, e):
        self.buffer[e.key].append(e)
        now = time.time()
        window = [ev for ev in self.buffer[e.key] if now - ev.timestamp <= self.window_size]
        self.buffer[e.key] = window  # 清理过期
        return [Event(e.key, self.agg_fn([ev.value for ev in window]))]

class TinyStream:
    """流处理引擎（参照 Flink DataStream API）"""
    def __init__(self): self.operators = []; self.output = []
    def map(self, fn): self.operators.append(MapOperator(fn)); return self
    def filter(self, pred): self.operators.append(FilterOperator(pred)); return self
    def window(self, size, slide, agg): self.operators.append(WindowOperator(size,slide,agg)); return self
    def process(self, events):
        for event in events:
            current = [event]
            for op in self.operators:
                current = [r for e in current for r in op.process(e)]
            self.output.extend(current)
        return self.output

def main():
    print("tinystream — 流处理引擎（参照 Flink）\n")
    # 模拟实时事件流
    events = [
        Event("cpu", 45.0), Event("mem", 60.0), Event("cpu", 55.0),
        Event("disk", 80.0), Event("cpu", 65.0), Event("mem", 70.0),
        Event("net", 30.0), Event("cpu", 75.0), Event("disk", 90.0),
    ]
    # 过滤 + 窗口聚合
    stream = TinyStream()
    stream.filter(lambda e: e.value > 50) \
          .window(10, 5, lambda vals: sum(vals)/len(vals) if vals else 0)
    results = stream.process(events)
    print("  输入事件:")
    for e in events: print(f"    {e.key:6s} = {e.value}")
    print(f"\n  过滤 > 50 + 窗口平均值:")
    for r in results: print(f"    {r.key:6s} avg = {r.value:.1f}")

if __name__ == "__main__": main()
