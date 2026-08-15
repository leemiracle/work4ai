"""
COS 126 General Computer Science（Princeton）
================================================
覆盖主题（Sedgewick & Wayne, Computer Science: An Interdisciplinary Approach）：
- TOY machine（teach-yourself machine）：16-bit 教学计算机，模拟冯诺依曼架构
- 基本排序可视化（insertion / selection / bubble 的比较/交换计数）
- Monte Carlo π：随机采样估算圆周率
- 立方根（Newton's method）、二分查找
- 布尔逻辑 + 二进制运算

核心教材：
- Sedgewick & Wayne "Computer Science: An Interdisciplinary Approach" Ch 1-3
- Sedgewick, Sedgewick, Dondero "Introduction to Programming in Python" Ch 1-3

本文件实现：
1. TOY 模拟器（16-bit, 32 寄存器, 256 内存, 真实执行机器码）
2. 三种排序算法的比较/交换步数对比（揭示 quadratic vs n log n 反直觉）
3. Monte Carlo π + Buffon 投针实验

运行：
    python intro.py
"""
from __future__ import annotations
import random
import math


# ================================================================
# 1. TOY Machine 模拟器（16-bit 教学计算机）
# ================================================================
# TOY: Princeton 经典教学机器
#   - 16 个寄存器（R[0]..R[15]），R[0] 恒为 0
#   - 256 字内存（M[0]..M[FF]）
#   - 每条指令 16-bit: opcode(4) | addr-or-immediate(12)
#   - 指令集：1=load, 2=add, 3=sub, 4=and, 5=xor, 6=shift-left,
#             7=shift-right, 8=store, A=load-addr, B=jump-if-zero,
#             C=jump-and-link, E=halt, F=system-out

class TOYMachine:
    """Princeton TOY 模拟器（基于 Sedgewick 教材）"""

    OPCODES = {
        0x1: "LOAD",   0x2: "ADD",   0x3: "SUB",   0x4: "AND",
        0x5: "XOR",    0x6: "SHL",   0x7: "SHR",   0x8: "STORE",
        0xA: "LOADA",  0xB: "JZ",    0xC: "JAL",   0xE: "HALT",
        0xF: "OUT",
    }

    def __init__(self):
        self.R = [0] * 16         # 16 registers (R[0] always 0)
        self.M = [0] * 256        # 256 words of memory
        self.pc = 0x10            # program counter starts at 0x10
        self.halted = False
        self.output = []
        self.trace = []

    def load_program(self, program: list[int], start: int = 0x10):
        """加载机器码到内存"""
        for i, word in enumerate(program):
            self.M[start + i] = word & 0xFFFF

    def fetch_decode_execute(self) -> bool:
        """取指—译码—执行一个周期。返回是否继续。"""
        if self.halted:
            return False
        ir = self.M[self.pc]          # fetch
        opcode = (ir >> 12) & 0xF     # top 4 bits
        d = (ir >> 8) & 0xF           # register dest (4 bits)
        s = (ir >> 4) & 0xF           # sometimes register source
        addr = ir & 0xFF              # 8-bit address
        imm = ir & 0xFF               # 8-bit immediate (for load)

        old_pc = self.pc
        self.pc = (self.pc + 1) & 0xFF
        op_name = self.OPCODES.get(opcode, f"?{opcode:X}")

        if opcode == 0xE:  # HALT
            self.halted = True
        elif opcode == 0x1:  # LOAD: R[d] = M[addr]
            self.R[d] = self.M[addr]
        elif opcode == 0x2:  # ADD: R[d] = R[d] + M[addr]
            self.R[d] = (self.R[d] + self.M[addr]) & 0xFFFF
        elif opcode == 0x3:  # SUB: R[d] = R[d] - M[addr]
            self.R[d] = (self.R[d] - self.M[addr]) & 0xFFFF
        elif opcode == 0x4:  # AND
            self.R[d] = self.R[d] & self.M[addr]
        elif opcode == 0x5:  # XOR
            self.R[d] = self.R[d] ^ self.M[addr]
        elif opcode == 0x8:  # STORE: M[addr] = R[d]
            self.M[addr] = self.R[d]
        elif opcode == 0xA:  # LOADA: R[d] = addr (load address literal)
            self.R[d] = addr
        elif opcode == 0xB:  # JZ: if R[d]==0, jump to addr
            if self.R[d] == 0:
                self.pc = addr
        elif opcode == 0xC:  # JAL: R[15]=return addr, jump to addr
            self.R[15] = self.pc
            self.pc = addr
        elif opcode == 0xF:  # OUT: print R[d]
            self.output.append(self.R[d])
        else:
            pass  # unimplemented opcode, skip

        self.R[0] = 0  # R[0] always 0
        self.trace.append((old_pc, op_name, d, addr, list(self.R[:8])))
        return not self.halted

    def run(self, max_steps: int = 1000) -> list[int]:
        """运行直到 halt 或达到最大步数"""
        for _ in range(max_steps):
            if not self.fetch_decode_execute():
                break
        return self.output


# ================================================================
# 2. 排序算法步数对比
# ================================================================

class SortProfiler:
    """统计比较和交换次数的排序分析器"""

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    def reset(self):
        self.comparisons = 0
        self.swaps = 0

    def insertion_sort(self, arr: list) -> list:
        a = list(arr)
        for i in range(1, len(a)):
            j = i
            while j > 0:
                self.comparisons += 1
                if a[j - 1] > a[j]:
                    a[j], a[j - 1] = a[j - 1], a[j]
                    self.swaps += 1
                    j -= 1
                else:
                    break
        return a

    def selection_sort(self, arr: list) -> list:
        a = list(arr)
        n = len(a)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self.comparisons += 1
                if a[j] < a[min_idx]:
                    min_idx = j
            if min_idx != i:
                a[i], a[min_idx] = a[min_idx], a[i]
                self.swaps += 1
        return a

    def merge_sort(self, arr: list) -> list:
        a = list(arr)
        return self._merge_sort(a)

    def _merge_sort(self, a: list) -> list:
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = self._merge_sort(a[:mid])
        right = self._merge_sort(a[mid:])
        return self._merge(left, right)

    def _merge(self, left: list, right: list) -> list:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            self.comparisons += 1
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
                self.swaps += 1  # count inversions
        result.extend(left[i:])
        result.extend(right[j:])
        return result


# ================================================================
# 3. Monte Carlo π + Buffon 投针
# ================================================================

def monte_carlo_pi(n: int) -> float:
    """蒙特卡洛 π：在单位正方形内随机投点，落入 1/4 圆的比例 × 4 ≈ π"""
    inside = 0
    for _ in range(n):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return 4.0 * inside / n


def buffon_needle(n: int, needle_len: float = 1.0, gap: float = 2.0) -> float:
    """Buffon 投针实验：π ≈ 2 * needle_len * n / (gap * crosses)"""
    crosses = 0
    for _ in range(n):
        # 针中心到最近线的距离
        y = random.uniform(0, gap / 2)
        # 针与平行线的夹角
        theta = random.uniform(0, math.pi / 2)
        if y <= (needle_len / 2) * math.sin(theta):
            crosses += 1
    if crosses == 0:
        return float('inf')
    return 2.0 * needle_len * n / (gap * crosses)


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 126: General CS Demo (TOY + Sort + Monte Carlo)")
    print("=" * 60)
    random.seed(42)

    # --- 1. TOY Machine: 计算 5 + 3 = 8 ---
    print("\n📋 1. TOY Machine 模拟器")
    print("   程序：计算 5 + 3，输出结果")
    # Machine code:
    #   10: 1A01  R[A] = M[01]  (load 5)
    #   11: 1B02  R[B] = M[02]  (load 3)
    #   12: 2A02  R[A] = R[A] + M[02]  (add)
    #   13: FA00  OUT R[A]
    #   14: E000  HALT
    #   01: 0005  (data: 5)
    #   02: 0003  (data: 3)
    program = [0x1A01, 0x1B02, 0x2A02, 0xFA00, 0xE000]
    toy = TOYMachine()
    toy.load_program(program, start=0x10)
    toy.M[0x01] = 0x0005  # data
    toy.M[0x02] = 0x0003  # data
    output = toy.run()
    print(f"   M[01]=5, M[02]=3")
    print(f"   执行 {len(toy.trace)} 步后输出: {output}")
    print(f"   验证: 5 + 3 = {output[0]}")
    print(f"   最后 3 条 trace:")
    for pc, op, d, addr, regs in toy.trace[-3:]:
        print(f"     PC={pc:02X} {op:6s} d=R{d:X} addr={addr:02X}  R[0:8]={[hex(r) for r in regs]}")

    # --- 2. 排序步数对比 ---
    print("\n📋 2. 排序算法比较/交换步数对比")
    profiler = SortProfiler()
    sizes = [16, 32, 64, 128, 256]
    print(f"   {'n':>5} {'algo':>12} {'comparisons':>13} {'swaps':>10} {'cmp/n²':>8}")
    print(f"   {'-'*55}")
    for n in sizes:
        arr = [random.randint(0, 1000) for _ in range(n)]
        for algo_name, sort_fn in [("insertion", profiler.insertion_sort),
                                     ("selection", profiler.selection_sort),
                                     ("merge", profiler.merge_sort)]:
            profiler.reset()
            sort_fn(arr)
            ratio = profiler.comparisons / (n * n) if n > 0 else 0
            print(f"   {n:>5} {algo_name:>12} {profiler.comparisons:>13} {profiler.swaps:>10} {ratio:>8.4f}")

    # --- 3. Monte Carlo π ---
    print("\n📋 3. Monte Carlo π")
    print(f"   {'samples':>10} {'MC π':>10} {'error':>10} {'Buffon π':>10}")
    for n in [100, 1000, 10000, 100000]:
        pi_mc = monte_carlo_pi(n)
        pi_buf = buffon_needle(n)
        print(f"   {n:>10} {pi_mc:>10.5f} {abs(pi_mc - math.pi):>10.5f} {pi_buf:>10.5f}")
    print(f"   {'true':>10} {math.pi:>10.5f}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    # Insertion sort on nearly-sorted data
    profiler.reset()
    sorted_arr = list(range(100))
    profiler.insertion_sort(sorted_arr)
    ins_sorted_cmp = profiler.comparisons
    profiler.reset()
    profiler.insertion_sort([random.randint(0, 100) for _ in range(100)])
    ins_random_cmp = profiler.comparisons
    print(f"   Insertion sort 对已排序数组(100): {ins_sorted_cmp} 次比较")
    print(f"   Insertion sort 对随机数组(100):   {ins_random_cmp} 次比较")
    print(f"   → 已排序数据下 insertion sort 是 O(n)，比 merge sort 更快！")
    print(f"   → 这就是 Python Timsort 用 insertion sort 处理小段的原因。")

    print("\n✅ COS 126 Demo 完成！")


if __name__ == "__main__":
    demo()
