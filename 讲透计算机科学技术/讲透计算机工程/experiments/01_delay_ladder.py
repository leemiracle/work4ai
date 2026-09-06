"""01_delay_ladder.py — 存储层级延迟阶梯实测（对应 00/04 章）

指针追逐（pointer chasing）是测内存延迟的经典方法：把数组串成一条
随机置换的链，然后顺着链走——每一步都必须等上一次访存结果才能算出
下一步地址，访存延迟无法被预取或乱序掩盖。

诚实的测量地板：CPython 解释器每步自身开销 ~30-60ns，所以 L1/L2 级
（~1-4ns）的延迟会被地板淹没——这本身就是教学点（观察者效应）。
本实验实测可分辨的是「仍在缓存里 vs 已出缓存进 DRAM」的跳变。

运行：python 01_delay_ladder.py
"""
import time
import random


def make_chain(n: int) -> list[int]:
    """构造随机置换链：next[i] 指向下一个要访问的下标。"""
    perm = list(range(n))
    random.seed(42)
    random.shuffle(perm)
    return perm


def chase(chain: list[int], steps: int) -> float:
    """顺着链走 steps 步，返回平均每步延迟（纳秒）。"""
    idx = 0
    t0 = time.perf_counter_ns()
    for _ in range(steps):
        idx = chain[idx]
    t1 = time.perf_counter_ns()
    # 防止循环被优化掉：消费 idx
    if idx == -1:
        print("unreachable")
    return (t1 - t0) / steps


def main() -> None:
    sizes = [
        ("8KB  (~L1)", 8 * 1024 // 8),
        ("256KB (~L2)", 256 * 1024 // 8),
        ("4MB   (~L3)", 4 * 1024 * 1024 // 8),
        ("256MB (DRAM)", 256 * 1024 * 1024 // 8),
    ]
    steps = 3_000_000
    print(f"{'工作集':<14}{'每步延迟':>12}   （含 Python 解释器开销地板）")
    latencies = {}
    for name, n in sizes:
        chain = make_chain(n)
        chase(chain, 50_000)          # 预热：把链页调入缓存/页表
        ns = chase(chain, steps)
        latencies[name] = ns
        print(f"{name:<14}{ns:>10.1f} ns")

    # 断言 1：DRAM 工作集延迟明显高于最小工作集（跨过缓存边界跳变）
    small = latencies["8KB  (~L1)"]
    big = latencies["256MB (DRAM)"]
    assert big > small * 1.15, f"DRAM 应明显慢于缓存内: {big:.1f} vs {small:.1f} ns"

    # 断言 2：物理量级合理性——每步延迟应在 10ns~2000ns 之间
    # （Python 开销地板 ~30-60ns + DRAM ~100ns 量级；异常小说明测量被优化）
    for name, ns in latencies.items():
        assert 5.0 < ns < 2000.0, f"{name} 延迟异常: {ns:.1f} ns"

    print("\n[ALL ASSERTS PASSED] 跳变可见：数据跨出缓存进入 DRAM 时延迟显著上升。")
    print("带走一句（00 章）：寄存器到网络差 6 个数量级=眨眼 vs 一昼夜；")
    print("本脚本只量出其中 1-2 级——剩下 4 级要用 C/rigorous 工具（如 Intel MLC）。")


if __name__ == "__main__":
    main()
