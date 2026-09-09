#!/usr/bin/env python3
"""
tinyprof — 参照 perf/py-spy 的采样式性能分析器

参照：perf (Linux) + py-spy (Python sampling profiler)
csdiy 对应：notes/perf-程序员视角.md + cheatsheets/profiling-场景速查.md

核心：signal handler 定时采样调用栈 → 统计函数频率 → 输出火焰图数据
"""
import signal, sys, time, threading, collections, os, json
from typing import Optional

class Profiler:
    """
    采样式 Profiler（参照 py-spy）

    原理（参照 perf 精读）：
    1. 设置 SIGPROF 信号定时器（setitimer）
    2. 信号触发时记录当前线程的调用栈
    3. 统计每个函数出现在栈顶的次数
    4. 输出火焰图数据（folded stack format）
    """
    def __init__(self, interval: float = 0.01):
        self.interval = interval  # 采样间隔（秒）
        self.samples = []         # 所有采样
        self.stack_counts = collections.Counter()  # 调用栈频率
        self.is_running = False
        self.start_time = 0
        self._old_timer = None

    def _sample(self, signum, frame):
        """信号处理函数：记录当前调用栈（参照 perf record）"""
        if not self.is_running:
            return
        stack = []
        f = frame
        while f is not None:
            func_name = f.f_code.co_name
            filename = os.path.basename(f.f_code.co_filename)
            lineno = f.f_lineno
            stack.append(f"{func_name} ({filename}:{lineno})")
            f = f.f_back
        stack.reverse()
        stack_key = ";".join(stack)
        self.stack_counts[stack_key] += 1
        self.samples.append(stack)

    def start(self):
        """启动采样（参照 perf record 开始）"""
        self.is_running = True
        self.start_time = time.time()
        self._old_handler = signal.signal(signal.SIGPROF, self._sample)
        # setitimer 设置重复定时器（参照 perf -F 99）
        signal.setitimer(signal.ITIMER_PROF, self.interval, self.interval)

    def stop(self):
        """停止采样（参照 perf record 结束）"""
        self.is_running = False
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, self._old_handler)

    def stats(self):
        """输出统计（参照 perf report）"""
        elapsed = time.time() - self.start_time
        total_samples = sum(self.stack_counts.values())
        top_funcs = collections.Counter()

        for stack_str, count in self.stack_counts.items():
            funcs = stack_str.split(";")
            if funcs:
                top_funcs[funcs[-1]] += count  # 栈顶函数

        return {
            "elapsed_seconds": round(elapsed, 3),
            "total_samples": total_samples,
            "sample_rate": round(total_samples / elapsed, 1) if elapsed > 0 else 0,
            "unique_stacks": len(self.stack_counts),
            "top_functions": top_funcs.most_common(10),
        }

    def flamegraph_data(self) -> str:
        """
        输出 folded stack 格式（参照 FlameGraph 工具的输入格式）

        格式：stack;frame;frame count
        可直接喂给 flamegraph.pl 生成火焰图。
        """
        lines = []
        for stack, count in sorted(self.stack_counts.items(), key=lambda x: -x[1]):
            lines.append(f"{stack} {count}")
        return "\n".join(lines)

    def print_report(self):
        """打印报告（参照 perf report 的交互式输出）"""
        s = self.stats()
        print(f"\n{'━' * 60}")
        print(f"tinyprof report ({s['elapsed_seconds']}s, {s['total_samples']} samples @ {s['sample_rate']} Hz)")
        print(f"{'━' * 60}")
        print(f"\n  Top functions (self time):")
        print(f"  {'function':<45} {'samples':>8} {'pct':>6}")
        print(f"  {'─'*45} {'─'*8} {'─'*6}")
        for func, count in s["top_functions"]:
            pct = count / s["total_samples"] * 100 if s["total_samples"] else 0
            print(f"  {func:<45} {count:>8} {pct:>5.1f}%")
        print(f"\n  Unique call stacks: {s['unique_stacks']}")
        print(f"  FlameGraph: python3 main.py --flame | flamegraph.pl > prof.svg")

# ─── 被测函数示例（CPU 密集型任务）───

def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def matrix_multiply(a, b):
    n = len(a)
    result = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += a[i][k] * b[k][j]
    return result

def demo():
    """运行 CPU 密集型任务，同时采样"""
    print("tinyprof — 采样式性能分析器\n")
    print("Running CPU-intensive tasks...\n")

    prof = Profiler(interval=0.005)  # 200 Hz
    prof.start()

    # 模拟混合负载
    import random
    random.seed(42)

    # Task 1: fibonacci（递归，CPU 密集）
    fib_result = fibonacci(28)
    print(f"  fibonacci(28) = {fib_result}")

    # Task 2: 冒泡排序
    arr = [random.randint(0, 1000) for _ in range(5000)]
    bubble_sort(arr[:])
    print(f"  bubble_sort(5000) done")

    # Task 3: 矩阵乘法
    n = 80
    mat_a = [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]
    mat_b = [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]
    matrix_multiply(mat_a, mat_b)
    print(f"  matrix_multiply({n}x{n}) done")

    prof.stop()
    prof.print_report()

    # 输出火焰图数据
    print("\n  FlameGraph folded data (first 10 lines):")
    for line in prof.flamegraph_data().split("\n")[:10]:
        print(f"    {line}")

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinyprof — 采样式性能分析器")
    p.add_argument("--flame", action="store_true", help="输出 FlameGraph folded 格式")
    p.add_argument("--interval", type=float, default=0.01, help="采样间隔（秒）")
    p.add_argument("--script", help="运行指定 Python 脚本并 profile")
    args = p.parse_args()

    if args.script:
        prof = Profiler(interval=args.interval)
        prof.start()
        exec(open(args.script).read())
        prof.stop()
        if args.flame:
            print(prof.flamegraph_data())
        else:
            prof.print_report()
    else:
        demo()

if __name__ == "__main__":
    main()
