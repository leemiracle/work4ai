#!/usr/bin/env python3
"""tinysched — 参照 Linux CFS / Go runtime 的任务调度器
参照：Linux CFS / Go GMP / RTOS 优先级调度
csdiy 对应：os §二(调度/阻塞) + csapp Ch8(异常控制流)
核心：就绪队列 + 调度策略（FCFS/SJF/Round-Robin/优先级）"""
import heapq, time, random
from dataclasses import dataclass, field

@dataclass(order=True)
class Task:
    priority: int
    pid: int = field(compare=False)
    name: str = field(compare=False)
    burst: float = field(compare=False)  # 需要 CPU 时间
    arrival: float = field(compare=False)
    remaining: float = field(default=0, compare=False)
    waiting: float = field(default=0, compare=False)

class Scheduler:
    """CPU 调度器（参照 csapp/os 教材）"""
    def __init__(self, strategy="fcfs"): self.strategy=strategy; self.timeline=[]
    def fcfs(self, tasks):
        """先来先服务（参照 FCFS）"""
        tasks = sorted(tasks, key=lambda t: t.arrival)
        t = 0
        for task in tasks:
            task.waiting = max(0, t - task.arrival)
            self.timeline.append((t, t+task.burst, task.name))
            t += task.burst
        return t
    def sjf(self, tasks):
        """最短作业优先（参照 SJF）"""
        tasks = sorted(tasks, key=lambda t: (t.arrival, t.burst))
        done = []; ready = []; t = 0
        while tasks or ready:
            while tasks and tasks[0].arrival <= t: ready.append(tasks.pop(0))
            if not ready: t = tasks[0].arrival; continue
            ready.sort(key=lambda x: x.burst)
            task = ready.pop(0)
            task.waiting = max(0, t - task.arrival)
            self.timeline.append((t, t+task.burst, task.name))
            t += task.burst
        return t
    def round_robin(self, tasks, quantum=2):
        """轮转调度（参照 Round Robin）"""
        tasks = sorted(tasks, key=lambda t: t.arrival)
        for t in tasks: t.remaining = t.burst
        ready = []; t = 0
        while tasks or ready:
            while tasks and tasks[0].arrival <= t: ready.append(tasks.pop(0))
            if not ready: t = tasks[0].arrival; continue
            task = ready.pop(0)
            run = min(quantum, task.remaining)
            self.timeline.append((t, t+run, task.name))
            task.remaining -= run; t += run
            while tasks and tasks[0].arrival <= t: ready.append(tasks.pop(0))
            if task.remaining > 0: ready.append(task)
        return t
    def stats(self):
        return [{"name":n, "start":s, "end":e, "duration":e-s} for s,e,n in self.timeline]

def main():
    print("tinysched — CPU 调度器（参照 Linux CFS / os 教材）\n")
    tasks = [
        Task(1, 1, "editor", burst=5, arrival=0),
        Task(2, 2, "compiler", burst=10, arrival=1),
        Task(3, 3, "backup", burst=3, arrival=2),
        Task(1, 4, "browser", burst=2, arrival=3),
    ]
    for strategy in ["fcfs", "sjf", "round_robin"]:
        sched = Scheduler(strategy)
        fresh = [Task(t.priority, t.pid, t.name, t.burst, t.arrival) for t in tasks]
        total = getattr(sched, strategy)(fresh)
        print(f"  ── {strategy.upper()} (总时间={total}) ──")
        for s,e,n in sched.timeline:
            bar = "█" * int(e-s)
            print(f"    {n:10s} [{s:4.0f}-{e:4.0f}] {bar}")
        avg_wait = sum(t.waiting for t in fresh) / len(fresh)
        print(f"    平均等待时间: {avg_wait:.1f}\n")

if __name__ == "__main__": main()
