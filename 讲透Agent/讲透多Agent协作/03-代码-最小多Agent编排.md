---
card_id: COL-03
title: "第 3 幕 · 代码：最小 orchestrator-worker 多 Agent 编排"
universe: 讲透多Agent协作
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: COL-04
---

# 💻 第 3 幕 · 代码：最小 orchestrator-worker 编排

200 行实现「一个 lead 派多个 worker 并行干活，汇总结果」。

```python
import concurrent.futures
import time
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Task:
    id: str
    desc: str
    fn: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)

@dataclass
class Result:
    task_id: str
    ok: bool
    value: object = None
    error: str = ""

class MessageBus:
    """简单的 message bus: pub/sub."""
    def __init__(self):
        self._subs = {}
    def subscribe(self, topic, fn):
        self._subs.setdefault(topic, []).append(fn)
    def publish(self, topic, msg):
        for fn in self._subs.get(topic, []):
            fn(msg)

class Worker:
    """执行单个 task."""
    def __init__(self, wid):
        self.wid = wid
    def run(self, task: Task) -> Result:
        try:
            val = task.fn(*task.args, **task.kwargs)
            return Result(task.id, True, value=val)
        except Exception as e:
            return Result(task.id, False, error=str(e))

class Orchestrator:
    """lead: 拆任务→派 worker→汇总."""
    def __init__(self, n_workers=4):
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=n_workers)
        self.workers = [Worker(f"w{i}") for i in range(n_workers)]
        self.bus = MessageBus()
        self.log = []
        self.bus.subscribe("log", lambda m: self.log.append(m))

    def dispatch(self, tasks: list[Task]) -> list[Result]:
        self.bus.publish("log", f"orchestrator: 派发 {len(tasks)} 个任务")
        futures = {}
        for i, t in enumerate(tasks):
            w = self.workers[i % len(self.workers)]
            fut = self.pool.submit(w.run, t)
            futures[fut] = t.id
        results = []
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            self.bus.publish("log", f"  worker 完成 {r.task_id}: ok={r.ok}")
            results.append(r)
        return results

    def synthesize(self, results: list[Result]) -> str:
        """汇总(简化: 拼接所有成功的 value)."""
        parts = [r.value for r in results if r.ok]
        self.bus.publish("log", f"orchestrator: 汇总 {len(parts)}/{len(results)} 个成功结果")
        return "\n".join(str(p) for p in parts)

# ===== Demo: 两个 worker 协作写 README =====
def research_topic(topic):
    time.sleep(0.3)  # 模拟 LLM 调用
    return f"## {topic}\n核心要点: 这是关于 {topic} 的研究摘要."

def write_intro(ctx):
    time.sleep(0.2)
    return f"# 项目 README\n\n{ctx}\n\n## 介绍\n本项目..."

if __name__ == "__main__":
    orch = Orchestrator(n_workers=3)
    # 任务: 并行研究 3 个主题
    tasks = [
        Task("t1", "研究 RAG", research_topic, args=("RAG",)),
        Task("t2", "研究 Agent", research_topic, args=("Agent",)),
        Task("t3", "研究 世界模型", research_topic, args=("世界模型",)),
    ]
    t0 = time.time()
    results = orch.dispatch(tasks)
    print(f"\n⏱ 并行耗时: {time.time()-t0:.2f}s (3 任务 × 0.3s 串行应 0.9s)")
    print("\n=== 汇总 ===")
    print(orch.synthesize(results))
    print("\n=== 编排日志 ===")
    for line in orch.log: print(line)
```

## 运行

```bash
python3 讲透多Agent协作/03-代码-最小多Agent编排.py
```

## 这段代码教什么

1. **Orchestrator-Worker 模式**：lead 拆任务，worker 并行执行
2. **MessageBus**：解耦的通信（worker 不直接互调，通过 bus）
3. **容错**：单个 task 失败不拖垮全局（Result.ok 标记）
4. **并行加速**：3 个 0.3s 任务并行 ≈ 0.3s vs 串行 0.9s

**生产化**：用真 LLM 当 worker、加 retry/timeout、用 LangGraph 的状态图替代朴素 ThreadPool、加人审断点。

📌 **下一张卡** → `04-不足-协作失败模式.md`
