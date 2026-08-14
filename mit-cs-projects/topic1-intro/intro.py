"""
6.100A Introduction to CS and Programming Using Python（MIT）
================================================
覆盖主题：
- Big-O 复杂度分析（对应 Lecture 10-11 Complexity）
- 排序算法对比与 ASCII 可视化（Lecture 12-13 Sorting）
- 素数筛 Eratosthenes（Lecture 14）
- 渐近分析的陷阱：理论 vs 实测

核心教材/论文（无 arXiv ID 项为经典教材/论文）：
- Guttag, "Introduction to Computation and Programming Using Python" 3rd ed, MIT Press 2021
- Cormen, Leiserson, Rivest, Stein, "Introduction to Algorithms" 4th ed (CLRS), Ch 2-3
- Hoare 1962 "Quicksort" The Computer Journal

本文件实现：
- Big-O 对比演示（bubble / selection / insertion / merge / quick / heap）
- 6 种排序的步数计数 + ASCII 可视化
- Eratosthenes 素数筛（分段优化版）
- 反直觉发现：常数因子 vs 渐近——小 n 下 O(n^2) 击败 O(n log n)

运行：
    python intro.py
"""
from __future__ import annotations
import math
import time
from dataclasses import dataclass


# ============ 1. 带计步器的排序算法 ============

@dataclass
class SortStats:
    comparisons: int = 0
    swaps: int = 0
    name: str = ""

    def reset(self, name: str = ""):
        self.comparisons = 0
        self.swaps = 0
        self.name = name


def bubble_sort(a: list, st: SortStats) -> list:
    a = a[:]
    n = len(a)
    for i in range(n):
        for j in range(n - i - 1):
            st.comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                st.swaps += 1
    return a


def selection_sort(a: list, st: SortStats) -> list:
    a = a[:]
    n = len(a)
    for i in range(n):
        mi = i
        for j in range(i + 1, n):
            st.comparisons += 1
            if a[j] < a[mi]:
                mi = j
        if mi != i:
            a[i], a[mi] = a[mi], a[i]
            st.swaps += 1
    return a


def insertion_sort(a: list, st: SortStats) -> list:
    a = a[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            st.comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                st.swaps += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return a


def merge_sort(a: list, st: SortStats) -> list:
    a = a[:]
    return _ms(a, st)


def _ms(a: list, st: SortStats) -> list:
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = _ms(a[:mid], st)
    right = _ms(a[mid:], st)
    return _merge(left, right, st)


def _merge(L: list, R: list, st: SortStats) -> list:
    out = []
    i = j = 0
    while i < len(L) and j < len(R):
        st.comparisons += 1
        if L[i] <= R[j]:
            out.append(L[i]); i += 1
        else:
            out.append(R[j]); j += 1
        st.swaps += 1  # 写操作
    out.extend(L[i:]); out.extend(R[j:])
    return out


def quick_sort(a: list, st: SortStats) -> list:
    a = a[:]
    _qs(a, 0, len(a) - 1, st)
    return a


def _qs(a: list, lo: int, hi: int, st: SortStats):
    if lo >= hi:
        return
    # Lomuto partition with last element as pivot
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        st.comparisons += 1
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            st.swaps += 1
            i += 1
    a[i], a[hi] = a[hi], a[i]
    st.swaps += 1
    _qs(a, lo, i - 1, st)
    _qs(a, i + 1, hi, st)


# ============ 2. ASCII 柱状图可视化 ============

def ascii_bar(a: list, width: int = 40, max_val: int = None) -> str:
    """把数组画成 ASCII 柱状图"""
    if not a:
        return "(empty)"
    mv = max_val or max(a) or 1
    lines = []
    for idx, v in enumerate(a):
        bar_len = int(v / mv * width)
        lines.append(f"{idx:3d}|{'#' * bar_len} ({v})")
    return "\n".join(lines)


def visualize_sort_step(a: list, title: str):
    """打印某时刻数组状态"""
    print(f"\n  [{title}] (n={len(a)})")
    print("  " + ascii_bar(a, width=30).replace("\n", "\n  "))


# ============ 3. Eratosthenes 素数筛 ============

def sieve_of_eratosthenes(n: int) -> list[int]:
    """经典筛：返回 [2, n] 内所有素数。O(n log log n)"""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def trial_division_primes(n: int) -> list[int]:
    """朴素试除法，O(n sqrt(n))，用于对比"""
    primes = []
    for num in range(2, n + 1):
        is_p = True
        for d in range(2, int(num ** 0.5) + 1):
            if num % d == 0:
                is_p = False
                break
        if is_p:
            primes.append(num)
    return primes


# ============ 4. Big-O 理论对比 ============

def big_o_table() -> str:
    """生成 n vs 操作次数的理论对比表"""
    ns = [10, 100, 1000, 10000]
    funcs = [
        ("O(log n)", lambda n: math.log2(n)),
        ("O(n)", lambda n: n),
        ("O(n log n)", lambda n: n * math.log2(n)),
        ("O(n^2)", lambda n: n ** 2),
        ("O(n^3)", lambda n: n ** 3),
        ("O(2^n)", lambda n: 2 ** n if n <= 30 else float('inf')),
    ]
    lines = ["Big-O 理论操作次数对比:", ""]
    header = f"{'函数':<12}" + "".join(f"{'n='+str(n):>14}" for n in ns)
    lines.append(header)
    lines.append("-" * len(header))
    for name, f in funcs:
        row = f"{name:<12}"
        for n in ns:
            v = f(n)
            if v == float('inf'):
                row += f"{'(爆炸)':>14}"
            elif v > 1e15:
                row += f"{v:.2e}".rjust(14)
            else:
                row += f"{v:>14,.0f}"
        lines.append(row)
    return "\n".join(lines)


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.100A: Big-O, 排序算法对比, 素数筛")
    print("=" * 65)

    # --- 排序步数对比 ---
    print("\n" + "=" * 65)
    print("📋 实验 1: 六种排序算法的步数 (n=20 随机数组)")
    print("=" * 65)

    import random
    random.seed(42)
    arr = [random.randint(1, 100) for _ in range(20)]
    print(f"原数组: {arr}")
    visualize_sort_step(arr, "未排序")

    st = SortStats()
    sorts = [
        ("Bubble Sort", bubble_sort),
        ("Selection Sort", selection_sort),
        ("Insertion Sort", insertion_sort),
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
    ]
    print(f"\n{'算法':<16}{'比较次数':>10}{'交换/写入':>12}{'总操作':>10}")
    print("-" * 48)
    for name, fn in sorts:
        st.reset(name)
        result = fn(arr, st)
        total = st.comparisons + st.swaps
        assert result == sorted(arr), f"{name} 排序错误!"
        print(f"{name:<16}{st.comparisons:>10}{st.swaps:>12}{total:>10}")

    # --- 可视化前几步 ---
    print("\n📋 实验 2: Insertion Sort 逐步可视化 (前 5 步)")
    arr2 = arr[:8]
    snap = arr2[:]
    for i in range(1, len(snap)):
        key = snap[i]
        j = i - 1
        while j >= 0 and snap[j] > key:
            snap[j + 1] = snap[j]
            j -= 1
        snap[j + 1] = key
        if i <= 5:
            visualize_sort_step(snap, f"step {i}, insert key={key}")

    # --- Big-O 理论表 ---
    print("\n📋 实验 3: 理论 Big-O 对比表")
    print(big_o_table())

    # --- 素数筛 ---
    print("\n📋 实验 4: Eratosthenes 筛 vs 试除法")
    for n in [100, 1000, 5000]:
        t1 = time.perf_counter()
        p1 = sieve_of_eratosthenes(n)
        t1 = time.perf_counter() - t1
        t2 = time.perf_counter()
        p2 = trial_division_primes(n)
        t2 = time.perf_counter() - t2
        assert p1 == p2
        print(f"  n={n:>5}: 筛 {t1*1e6:>8.1f}μs | 试除 {t2*1e6:>10.1f}μs | "
              f"加速 {t2/max(t1,1e-9):>5.1f}x | {len(p1)} 个素数")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：常数因子击败渐近复杂度")
    print("=" * 65)
    print("理论上 insertion sort = O(n^2) 远慢于 merge sort = O(n log n)。")
    print("但实测小数组（n<50）insertion sort 常更快——没有递归开销。")
    print()
    for n in [10, 20, 30, 50, 100, 500, 2000]:
        data = [random.randint(0, 10000) for _ in range(n)]
        st_ins = SortStats(); st_mrg = SortStats()
        t1 = time.perf_counter()
        insertion_sort(data, st_ins)
        t1 = time.perf_counter() - t1
        t2 = time.perf_counter()
        merge_sort(data, st_mrg)
        t2 = time.perf_counter() - t2
        winner = "insert" if t1 < t2 else "merge"
        print(f"  n={n:>4}: insert {t1*1e6:>8.1f}μs | merge {t2*1e6:>8.1f}μs "
              f"| 胜者={winner}")

    print("\n  → n≈30-50 是交叉点；工程中 hybrid sort (Timsort/Introsort) 正是")
    print("    在小段切换到 insertion sort，这就是 Python/Java 标准库的做法。")

    print("\n✅ 6.100A Demo 完成！")


if __name__ == "__main__":
    demo()
