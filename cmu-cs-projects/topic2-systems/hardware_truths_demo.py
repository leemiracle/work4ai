"""
CSAPP 8 个「软件幻觉 vs 硬件真相」可运行对比演示
==================================================
配套文档：../../top-cs-projects/CSAPP_HARDWARE_TRUTHS.md
配套代码：csapp.py（cache 模拟 / malloc / 页表）

本文件演示 8 个 CSAPP 核心真相，每个都用「模拟器 + 真实测量」让你看到反直觉：
  §1 demo_cache_locality       —— Cache Line 与空间局部性（row vs col miss 率）
  §2 demo_tlb_and_pages        —— 虚拟内存 + TLB（4KB page 关键阈值）
  §3 demo_stack_overflow       —— 栈帧布局与 Buffer Overflow
  §4 demo_branch_prediction    —— 流水线 + 分支预测（有序 vs 乱序）
  §5 demo_false_sharing        —— MESI 协议与伪共享
  §6 demo_syscall_cost         —— Ring 0 vs Ring 3 的真实成本（可测）
  §7 demo_memory_reordering    —— Store Buffer 与内存乱序
  §8 demo_float_denormal       —— IEEE 754 与非规格化数（可测）

运行：
    python3 hardware_truths_demo.py            # 跑全部 8 个
    python3 hardware_truths_demo.py 1 4 6      # 只跑 §1 §4 §6

注意：纯 Python（CPython 解释器 + GIL）看不到真正的硬件级效果（如流水线、
伪共享），所以这些 demo 用「硬件行为模拟器」展示原理；而 syscall 成本、
浮点 denormal 减速则可以真实测量。

核心教材：Bryant & O'Hallaron "Computer Systems: A Programmer's Perspective" 3rd ed
"""
from __future__ import annotations
import os
import sys
import time
import struct
import math
from dataclasses import dataclass, field
from typing import List, Tuple

SEP = "=" * 72
SUBSEP = "-" * 72


# ============================================================================
# §1 Cache Line 与空间局部性
# ============================================================================

@dataclass
class _MiniCacheLine:
    valid: bool = False
    tag: int = -1


class MiniCache:
    """极简 direct-mapped cache 模拟器（只为演示空间局部性）。"""

    def __init__(self, num_lines: int, line_size: int):
        self.num_lines = num_lines
        self.line_size = line_size  # bytes per line (e.g. 64)
        self.table: List[_MiniCacheLine] = [_MiniCacheLine() for _ in range(num_lines)]
        self.hits = 0
        self.misses = 0

    def _split(self, addr: int) -> Tuple[int, int]:
        offset_bits = int(math.log2(self.line_size))
        index_bits = int(math.log2(self.num_lines))
        index = (addr >> offset_bits) & (self.num_lines - 1)
        tag = addr >> (offset_bits + index_bits)
        return index, tag

    def access(self, addr: int) -> bool:
        idx, tag = self._split(addr)
        line = self.table[idx]
        if line.valid and line.tag == tag:
            self.hits += 1
            return True
        # miss -> load
        self.misses += 1
        line.valid = True
        line.tag = tag
        return False

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


def demo_cache_locality():
    print(f"\n{SEP}\n§1 Cache Line 与空间局部性 —— 为什么 row-major 快 50×\n{SEP}")
    print("硬件真相：CPU 按 Cache Line（64B）整块读，row-major 命中率碾压 col-major。\n")

    # 模拟一个 256x256 的 int 矩阵（每个 int = 4 bytes）
    # 64B line = 16 ints，所以连续 16 个 int 在同一 cache line
    N = 256
    ELEM_SIZE = 4  # sizeof(int)
    LINE_SIZE = 64
    CACHE_LINES = 64  # 小 cache 容易看出差异

    def simulate(traversal: str) -> Tuple[float, int, int]:
        cache = MiniCache(num_lines=CACHE_LINES, line_size=LINE_SIZE)
        # 矩阵基地址 0，C 是 row-major：a[i][j] 地址 = (i*N + j) * ELEM_SIZE
        if traversal == "row-major":
            order = [(i, j) for i in range(N) for j in range(N)]
        else:  # col-major
            order = [(i, j) for j in range(N) for i in range(N)]
        for (i, j) in order:
            addr = (i * N + j) * ELEM_SIZE
            cache.access(addr)
        return cache.hit_rate, cache.hits, cache.misses

    row_hr, row_h, row_m = simulate("row-major")
    col_hr, col_h, col_m = simulate("col-major")

    print(f"  矩阵: {N}×{N} int = {N*N*ELEM_SIZE//1024} KB，Cache: {CACHE_LINES} lines × {LINE_SIZE}B = {CACHE_LINES*LINE_SIZE//1024} KB")
    print(f"  {'遍历方式':<14} {'命中':>8} {'缺失':>8} {'命中率':>10}")
    print(f"  {SUBSEP}")
    print(f"  {'row-major':<14} {row_h:>8} {row_m:>8} {row_hr*100:>9.2f}%")
    print(f"  {'col-major':<14} {col_h:>8} {col_m:>8} {col_hr*100:>9.2f}%")
    ratio = (col_m / max(row_m, 1))
    print(f"\n  💥 col-major 的 cache miss 是 row-major 的 {ratio:.1f}× —— 这就是 50× 性能差距的根源。")
    print(f"  🛠 工程结论：C/C++ 永远让最右下标 a[i][j] 的 j 在最内层循环。")


# ============================================================================
# §2 虚拟内存与 TLB
# ============================================================================

def demo_tlb_and_pages():
    print(f"\n{SEP}\n§2 虚拟内存与 TLB —— 4KB Page 是关键阈值\n{SEP}")
    print("硬件真相：虚拟地址要翻译成物理地址，TLB 缓存最近用过的页映射。\n")

    PAGE_SIZE = 4096  # 4 KB
    TLB_SIZE = 64     # L1 dTLB 典型大小

    @dataclass
    class TLBEntry:
        vpage: int = -1
        pframe: int = -1

    class TLB:
        def __init__(self, size: int):
            self.size = size
            self.entries: List[TLBEntry] = [TLBEntry() for _ in range(size)]
            self.clock = 0
            self.hits = 0
            self.misses = 0

        def lookup(self, vpage: int) -> bool:
            self.clock += 1
            for e in self.entries:
                if e.vpage == vpage:
                    self.hits += 1
                    return True
            self.misses += 1
            # FIFO 替换
            victim = self.entries[0]
            victim.vpage = vpage
            victim.pframe = vpage  # 简化：物理帧号 = 虚拟页号
            return False

    def simulate_access(stride_bytes: int, num_access: int) -> Tuple[float, int, int]:
        """模拟按 stride 步长访问 num_access 次。"""
        tlb = TLB(TLB_SIZE)
        addr = 0
        for _ in range(num_access):
            vpage = addr // PAGE_SIZE
            tlb.lookup(vpage)
            addr = (addr + stride_bytes) % (1 << 30)  # 限制在 1 GB 内
        total = tlb.hits + tlb.misses
        return (tlb.hits / total if total else 0, tlb.hits, tlb.misses)

    print(f"  Page size = {PAGE_SIZE} B = 4 KB，TLB = {TLB_SIZE} 项（覆盖率 {PAGE_SIZE*TLB_SIZE//1024} KB）")
    print(f"  测试：连续访问 1 MB，对比不同 stride 的 TLB 命中率\n")
    print(f"  {'stride':<14} {'跨页?':<10} {'TLB hit':>8} {'TLB miss':>10} {'命中率':>10}")
    print(f"  {SUBSEP}")
    for stride, label in [(4, "顺序 int"), (64, "cache line"), (256, "小跳"), (4096, "1 page"), (8192, "2 page"), (32768, "8 page")]:
        # 访问 1 MB / stride 次
        num_access = max(1, (1 << 20) // stride)
        hr, h, m = simulate_access(stride, num_access)
        crosses = "否" if stride < PAGE_SIZE else "是"
        print(f"  {stride:>5} B ({label:<8}) {crosses:<10} {h:>8} {m:>10} {hr*100:>9.2f}%")

    print(f"\n  💥 stride ≥ 4 KB（跨页）时 TLB miss 暴涨——这就是为什么大页（HugePages 2MB）能让覆盖率提升 512×。")
    print(f"  🛠 工程结论：MySQL InnoDB 页 = 16 KB（4 个 4KB page），保证节点 TLB 友好。")


# ============================================================================
# §3 Stack Frame 与 Buffer Overflow
# ============================================================================

def demo_stack_overflow():
    print(f"\n{SEP}\n§3 栈帧布局与 Buffer Overflow —— 确定性是原罪\n{SEP}")
    print("硬件真相：栈帧按固定顺序布局，越界写能精准覆盖返回地址。\n")

    # 用 bytearray 模拟一段栈（高地址在下，低地址在上，x86 栈向下生长）
    # 布局：
    #   [返回地址 RET][保存的 RBP][buf[8]]
    # 低地址 ←—————————————————————— 高地址
    STACK_SIZE = 32  # bytes

    def build_stack(buf_init: bytes, ret_addr: bytes) -> bytearray:
        """构造一个简化栈帧：buf(8) + RBP(8) + RET(8)。"""
        stack = bytearray(STACK_SIZE)
        # 低 8 字节 = buf
        stack[0:8] = buf_init.ljust(8, b"\x00")[:8]
        # 中 8 字节 = 保存的 RBP
        stack[8:16] = b"\xAA" * 8
        # 高 8 字节 = 返回地址
        stack[16:24] = ret_addr
        return stack

    def safe_strcpy(stack: bytearray, buf_start: int, payload: bytes):
        """模拟 strcpy（无边界检查）。"""
        for i, b in enumerate(payload):
            stack[buf_start + i] = b  # 越界也照写

    LEGIT_RET = b"\x00\x10\x40\x00\x00\x00\x00\x00"  # 假设合法返回地址 0x401000
    SHELLCODE_ADDR = b"\xEF\xBE\xAD\xDE\x00\x00\x00\x00"  # 攻击者注入的地址 0xDEADBEEF

    # 正常输入
    stack_ok = build_stack(b"HELLO", LEGIT_RET)
    safe_strcpy(stack_ok, 0, b"HELLO\x00")
    ret_after_ok = stack_ok[16:24]

    # 恶意输入：8 字节填满 buf + 8 字节覆盖 RBP + 8 字节覆盖 RET
    payload = b"A" * 8 + b"B" * 8 + SHELLCODE_ADDR
    stack_bad = build_stack(b"\x00" * 8, LEGIT_RET)
    safe_strcpy(stack_bad, 0, payload)
    ret_after_bad = stack_bad[16:24]

    print(f"  栈帧布局（x86-64，栈向下生长）：")
    print(f"    低地址 → [buf(8B)] [saved RBP(8B)] [返回地址 RET(8B)] ← 高地址")
    print(f"  合法返回地址: 0x{int.from_bytes(LEGIT_RET, 'little'):016X}")
    print(f"  攻击目标地址: 0x{int.from_bytes(SHELLCODE_ADDR, 'little'):016X}\n")

    print(f"  输入 1（正常，5 字节 'HELLO'）：")
    print(f"    buf  = {bytes(stack_ok[0:8]).hex()}")
    print(f"    RBP  = {bytes(stack_ok[8:16]).hex()}")
    print(f"    RET  = {bytes(ret_after_ok).hex()}  → 0x{int.from_bytes(ret_after_ok, 'little'):016X} ✅ 未被篡改")

    print(f"\n  输入 2（恶意，{len(payload)} 字节，越界覆盖）：")
    print(f"    payload = buf填充(8B 'A') + RBP覆盖(8B 'B') + RET篡改({SHELLCODE_ADDR.hex()})")
    print(f"    buf  = {bytes(stack_bad[0:8]).hex()}  ← 'AAAAAAAA'")
    print(f"    RBP  = {bytes(stack_bad[8:16]).hex()}  ← 'BBBBBBBB'（被覆盖）")
    print(f"    RET  = {bytes(ret_after_bad).hex()}  → 0x{int.from_bytes(ret_after_bad, 'little'):016X} 💥 被劫持到 Shellcode！")

    print(f"\n  💥 函数 ret 时 CPU 读到被篡改的 RET，跳到攻击者代码——控制权易主。")
    print(f"  🛠 现代缓解：Stack Canary / DEP(NX) / ASLR / PIE / CFI；永远用 strncpy/snprintf。")


# ============================================================================
# §4 流水线与分支预测
# ============================================================================

def demo_branch_prediction():
    print(f"\n{SEP}\n§4 流水线与分支预测 —— 有序数组快 3×\n{SEP}")
    print("硬件真相：CPU 用 2-bit 饱和计数器猜分支，有序数据预测准确率 ≈ 100%。\n")

    class BranchPredictor:
        """2-bit 饱和计数器预测器。
        状态：00 SN(strongly not taken), 01 WN, 10 WT, 11 ST。
        """
        def __init__(self):
            self.state = 0b00  # SN
            self.correct = 0
            self.wrong = 0

        def predict(self) -> bool:
            return self.state >= 0b10  # WT/ST 预测 taken

        def update(self, actual_taken: bool):
            pred = self.predict()
            if pred == actual_taken:
                self.correct += 1
            else:
                self.wrong += 1
            # 状态转移
            if actual_taken:
                self.state = min(self.state + 1, 0b11)
            else:
                self.state = max(self.state - 1, 0b00)

    def simulate(data: List[int], threshold: int = 128) -> Tuple[float, int, int]:
        bp = BranchPredictor()
        for x in data:
            actual = (x < threshold)
            bp.update(actual)
        total = bp.correct + bp.wrong
        return (bp.correct / total if total else 0, bp.correct, bp.wrong)

    N = 10000
    THRESH = N // 2  # 用中位数当阈值：乱序时预测器像抛硬币，有序时几乎 100% 对
    sorted_data = list(range(N))
    random_data = sorted_data[:]
    import random
    random.seed(42)
    random.shuffle(random_data)

    hr_sorted, c_sorted, w_sorted = simulate(sorted_data, THRESH)
    hr_random, c_random, w_random = simulate(random_data, THRESH)

    print(f"  数据规模：{N} 个元素，分支：if (x < {THRESH})（中位数阈值让差异最大化）")
    print(f"  {'数据':<14} {'预测正确':>10} {'预测错误':>10} {'准确率':>10} {'等效流水线 flush'}")
    print(f"  {SUBSEP}")
    print(f"  {'有序数组':<14} {c_sorted:>10} {w_sorted:>10} {hr_sorted*100:>9.2f}% {'~0 次 flush  ✅':>20}")
    print(f"  {'乱序数组':<14} {c_random:>10} {w_random:>10} {hr_random*100:>9.2f}% {f'~{w_random} 次 flush 💥':>20}")
    print(f"\n  💥 每次预测错误 = 15-20 cycle 流水线 flush。{w_random} 次错误 ≈ {w_random*17} cycle 纯浪费。")
    print(f"  🛠 工程结论：热点循环优先处理有序数据；可用位运算 / cmov 消除分支。")


# ============================================================================
# §5 MESI 协议与伪共享
# ============================================================================

def demo_false_sharing():
    print(f"\n{SEP}\n§5 MESI 协议与伪共享 —— 并行为何比串行还慢\n{SEP}")
    print("硬件真相：CPU 不认'变量'只认 Cache Line(64B)，同行的不同变量会乒乓失效。\n")

    LINE_SIZE = 64

    @dataclass
    class CacheLineState:
        """MESI 状态机：M(修改)/E(独占)/S(共享)/I(无效)。"""
        state: str = "I"
        # 记录本行里有哪些变量

    class CoreCache:
        def __init__(self, name: str):
            self.name = name
            self.lines: dict = {}  # line_id -> CacheLineState
            self.invalidations_sent = 0
            self.invalidations_recv = 0

        def write(self, line_id: int, bus: "Bus"):
            """核心写某个 cache line（任何非 M 状态写入都要 RFO + invalidate 其他核心）。"""
            cur = self.lines.get(line_id, CacheLineState("I"))
            if cur.state == "M":
                # 已独占修改，无开销
                return
            # S / E / I -> M：必须 Read-For-Ownership，invalidate 总线上其他持有者
            for other in bus.cores:
                if other is not self and line_id in other.lines and other.lines[line_id].state != "I":
                    other.lines[line_id] = CacheLineState("I")
                    other.invalidations_recv += 1
                    self.invalidations_sent += 1
            self.lines[line_id] = CacheLineState("M")

    class Bus:
        def __init__(self):
            self.cores: List[CoreCache] = []

    def simulate(layout: str, num_writes_per_core: int = 1000) -> Tuple[int, int]:
        """模拟 2 个核心各自反复写一个变量。
        layout='shared': 两变量在同一 cache line -> 伪共享
        layout='padded': 两变量在不同 cache line -> 无伪共享
        """
        bus = Bus()
        c1 = CoreCache("core1")
        c2 = CoreCache("core2")
        bus.cores = [c1, c2]

        if layout == "shared":
            line_x, line_y = 0, 0  # 同一行
        else:
            line_x, line_y = 0, 64  # 不同行

        for _ in range(num_writes_per_core):
            c1.write(line_x, bus)
            c2.write(line_y, bus)

        total_inv = c1.invalidations_sent + c1.invalidations_recv + c2.invalidations_sent + c2.invalidations_recv
        return total_inv, num_writes_per_core * 2

    inv_shared, ops_shared = simulate("shared")
    inv_padded, ops_padded = simulate("padded")

    print(f"  场景：2 核各反复写 1 个变量 × 1000 次，共 {ops_shared} 次写")
    print(f"  {'布局':<28} {'总 invalidate 次数':>22} {'每次写的失效开销':>20}")
    print(f"  {SUBSEP}")
    print(f"  {'同 cache line（伪共享）':<26} {inv_shared:>22} {inv_shared/ops_shared:>17.2f}×")
    print(f"  {'不同 cache line（padding）':<26} {inv_padded:>22} {inv_padded/ops_padded:>17.2f}×")
    print(f"\n  💥 伪共享下每次写都触发跨核 invalidate（~40-100 cycle/次），4 核实测可比单核慢 5-10×。")
    print(f"  🛠 工程结论：用 alignas(64) / @Contended 让热变量独占 cache line；Disruptor 框架的招牌设计。")


# ============================================================================
# §6 系统调用成本（可真实测量）
# ============================================================================

def demo_syscall_cost():
    print(f"\n{SEP}\n§6 系统调用 —— Ring 0 vs Ring 3 的真实成本\n{SEP}")
    print("硬件真相：syscall 要保存现场 + 切内核栈 + 刷 TLB，比纯函数调用慢 100×。\n")

    N = 1_000_000

    # 1. 纯 Python 加法（基线）
    x = 0
    t0 = time.perf_counter_ns()
    for _ in range(N):
        x += 1
    t_add = time.perf_counter_ns() - t0
    ns_per_add = t_add / N

    # 2. os.getpid() syscall
    t0 = time.perf_counter_ns()
    for _ in range(N):
        os.getpid()
    t_syscall = time.perf_counter_ns() - t0
    ns_per_syscall = t_syscall / N

    # 3. 纯函数调用（Python 层，非内建）
    def noop():
        return 0
    t0 = time.perf_counter_ns()
    for _ in range(N):
        noop()
    t_func = time.perf_counter_ns() - t0
    ns_per_func = t_func / N

    print(f"  每次操作耗时（{N:,} 次循环，本机实测）：\n")
    print(f"  {'操作':<28} {'ns/次':>10} {'相对最慢':>12}")
    print(f"  {SUBSEP}")
    print(f"  {'纯加法 x+=1':<28} {ns_per_add:>10.1f} {ns_per_add/ns_per_syscall*100:>10.1f}%")
    print(f"  {'Python 函数调用 noop()':<28} {ns_per_func:>10.1f} {ns_per_func/ns_per_syscall*100:>10.1f}%")
    print(f"  {'os.getpid() syscall':<28} {ns_per_syscall:>10.1f} {'100.0%':>11}")
    print(f"\n  💥 syscall 比纯加法慢 {ns_per_syscall/ns_per_add:.0f}×。如果每次读 1 字节就 syscall，1MB 文件要 ~{ns_per_syscall/1e9*1_048_576:.2f} 秒纯系统调用开销。")
    print(f"  🛠 工程结论：用缓冲 I/O（fread）；sendfile 零拷贝；io_uring 批量化 syscall。")


# ============================================================================
# §7 内存乱序执行（Store Buffer 模拟）
# ============================================================================

def demo_memory_reordering():
    print(f"\n{SEP}\n§7 内存乱序执行 —— 代码并不是从上往下跑\n{SEP}")
    print("硬件真相：CPU 有 Store Buffer，无数据依赖的写可重排，多线程下可见顺序 ≠ 代码顺序。\n")

    # 经典"消息传递"反例：
    #   线程 1:  data = 42; ready = 1;
    #   线程 2:  while (!ready); print(data);
    # 无屏障时，线程 2 可能打印 0！

    @dataclass
    class StoreBuffer:
        """模拟 CPU 核心 的 store buffer（FIFO）。"""
        owner: str
        entries: List[Tuple[str, int]] = field(default_factory=list)  # (var, value)

        def push(self, var: str, value: int):
            self.entries.append((var, value))

        def flush_one(self) -> Tuple[str, int] | None:
            """提交最早的一条到全局内存。"""
            if self.entries:
                return self.entries.pop(0)
            return None

        def flush_all(self, mem: dict):
            while self.entries:
                var, val = self.entries.pop(0)
                mem[var] = val

    class CPU:
        def __init__(self, name: str):
            self.name = name
            self.sb = StoreBuffer(name)

        def store(self, var: str, value: int, mem: dict, reorder: bool = False):
            """模拟 store；reorder=True 时相邻无依赖 store 可交换顺序。"""
            self.sb.push(var, value)
            if reorder and len(self.sb.entries) >= 2:
                # 模拟 store buffer 乱序提交：50% 概率交换最新两条
                import random
                if random.random() < 0.5:
                    self.sb.entries[-1], self.sb.entries[-2] = self.sb.entries[-2], self.sb.entries[-1]

    def simulate(reorder: bool, seed: int) -> int:
        """交错模拟：线程1 的两条 store 进入 buffer，线程2 在它们之间读。
        reorder=True 时 store buffer 可能把 ready 提前提交，线程2 看到 ready=1 但 data 还是 0。
        """
        import random
        random.seed(seed)
        mem = {"data": 0, "ready": 0}
        # 线程1 的代码顺序：data=42; ready=1;
        stores = [("data", 42), ("ready", 1)]
        if reorder and random.random() < 0.5:
            # store buffer 重排提交顺序（弱内存模型的真实行为）
            stores = [stores[1], stores[0]]
        # 模拟"第一条 store 已全局可见，第二条还在 buffer"
        k1, v1 = stores[0]
        mem[k1] = v1
        # 线程2 此刻读（关键窗口：如果 ready 先提交，data 还没提交）
        if mem["ready"] == 1:
            return mem["data"]  # reorder 时可能是 0
        # 第二条 store 提交
        k2, v2 = stores[1]
        mem[k2] = v2
        return mem["data"]

    def simulate_many(reorder: bool, trials: int = 10000) -> int:
        """跑 trials 次，统计线程 2 看到 data=0 的次数。"""
        bug_count = 0
        for s in range(trials):
            result = simulate(reorder, s)
            if result == 0:
                bug_count += 1
        return bug_count

    print(f"  测试场景：线程1 执行 data=42; ready=1;  线程2 等 ready 后读 data\n")
    trials = 10000
    bug_strict = simulate_many(reorder=False, trials=trials)
    bug_reorder = simulate_many(reorder=True, trials=trials)

    print(f"  {'执行模式':<32} {'线程2 看到 data=0 的次数':>26} {'比例':>10}")
    print(f"  {SUBSEP}")
    print(f"  {'严格顺序（TSO / 加 memory barrier）':<30} {bug_strict:>26} {bug_strict/trials*100:>9.2f}%")
    print(f"  {'Store Buffer 乱序（弱内存模型）':<30} {bug_reorder:>26} {bug_reorder/trials*100:>9.2f}%")
    print(f"\n  💥 弱内存模型（ARM/POWER）下，'data=42; ready=1' 可能以 'ready=1; data=42' 顺序对外可见——无锁编程的灾难根源。")
    print(f"  🛠 工程结论：用 std::atomic 的 release/acquire；Java volatile；x86 的 mfence 强制屏障。")


# ============================================================================
# §8 浮点数与非规格化数（可真实测量）
# ============================================================================

def demo_float_denormal():
    print(f"\n{SEP}\n§8 IEEE 754 与非规格化数 —— 0.1+0.2≠0.3 的深渊\n{SEP}")
    print("硬件真相：浮点数位模式不连续，非规格化数让 FPU 退化到微代码（慢 10-100×）。\n")

    # 1. 0.1 + 0.2 ≠ 0.3 的位模式
    print("  ▶ 浮点精度：0.1 + 0.2 ≠ 0.3")
    a, b = 0.1, 0.2
    s = a + b
    target = 0.3
    print(f"    0.1       = {struct.pack('>d', a).hex()}")
    print(f"    0.2       = {struct.pack('>d', b).hex()}")
    print(f"    0.1 + 0.2 = {struct.pack('>d', s).hex()}  = {s!r}")
    print(f"    0.3       = {struct.pack('>d', target).hex()}  = {target!r}")
    print(f"    == 比较：{s == target}  （差 {s - target:.2e}）")
    print(f"    机器 epsilon (double): {np_spacing():.2e}\n")

    # 2. 非规格化数性能（真实可测）
    print("  ▶ 非规格化数（Denormal）性能测试")
    NORM = 1.0
    DENORM = sys.float_info.min * 0.1  # 比 min 还小 -> 非规格化
    print(f"    正常浮点  = {NORM}   (hex {struct.pack('>d', NORM).hex()})")
    print(f"    最小正常  = {sys.float_info.min:.3e}   (hex {struct.pack('>d', sys.float_info.min).hex()})")
    print(f"    非规格化  = {DENORM:.3e}   (hex {struct.pack('>d', DENORM).hex()})")

    N = 2_000_000

    def bench_mul(x: float) -> float:
        arr = [x] * N
        t0 = time.perf_counter_ns()
        acc = 1.0
        for v in arr:
            acc *= v
        return (time.perf_counter_ns() - t0) / N

    ns_norm = bench_mul(NORM)
    ns_denorm = bench_mul(DENORM)
    print(f"\n    {N:,} 次乘法（本机实测）：")
    print(f"    {'操作数':<24} {'ns/次':>10} {'相对':>10}")
    print(f"    {SUBSEP}")
    print(f"    {'正常浮点 1.0':<24} {ns_norm:>10.2f} {'1.0×':>10}")
    print(f"    {'非规格化数':<24} {ns_denorm:>10.2f} {ns_denorm/max(ns_norm, 0.01):>9.1f}×")
    slowdown = ns_denorm / max(ns_norm, 0.01)
    if slowdown >= 5:
        verdict = f"💥 实测减速 {slowdown:.1f}× —— 你的系统 FTZ/DAZ 未开启，FPU 退回微代码处理 denormal。"
    else:
        verdict = f"ℹ️  实测减速仅 {slowdown:.1f}× —— 你的系统/解释器已默认开启 FTZ/DAZ（现代 CPU + Linux 默认行为），denormal 被直接当 0。音频 DSP 工程师遇到的就是关闭 FTZ 时的 10-100× 减速。"
    print(f"\n  {verdict}")
    print(f"  🛠 工程结论：音频/图形/AI 算子显式开启 FTZ+DAZ（MXCSR）；永远不用 == 比较浮点。")


def np_spacing() -> float:
    """模拟 np.spacing(1.0) —— 返回 1.0 旁边的下一个可表示 double。"""
    return sys.float_info.epsilon


# ============================================================================
# 主入口
# ============================================================================

DEMOS = {
    1: ("Cache Line 与空间局部性", demo_cache_locality),
    2: ("虚拟内存与 TLB", demo_tlb_and_pages),
    3: ("栈帧与 Buffer Overflow", demo_stack_overflow),
    4: ("流水线与分支预测", demo_branch_prediction),
    5: ("MESI 协议与伪共享", demo_false_sharing),
    6: ("系统调用成本", demo_syscall_cost),
    7: ("内存乱序执行", demo_memory_reordering),
    8: ("IEEE 754 与非规格化数", demo_float_denormal),
}


def main():
    print("╔" + "═" * 70 + "╗")
    print("║" + " CSAPP 8 个「软件幻觉 vs 硬件真相」可运行对比演示 ".center(70) + "║")
    print("║" + " 配套文档：top-cs-projects/CSAPP_HARDWARE_TRUTHS.md ".center(70) + "║")
    print("╚" + "═" * 70 + "╝")

    args = sys.argv[1:]
    if args:
        try:
            selected = sorted({int(a) for a in args if a.isdigit()})
        except ValueError:
            selected = list(DEMOS.keys())
    else:
        selected = list(DEMOS.keys())

    for n in selected:
        if n in DEMOS:
            name, fn = DEMOS[n]
            print(f"\n\n▶▶▶ 运行 §{n} {name} ▶▶▶")
            try:
                fn()
            except Exception as e:
                print(f"  [!] §{n} 运行出错：{e}")
        else:
            print(f"  [!] 未知 demo 编号：{n}（可选 1-8）")

    print(f"\n{SEP}")
    print("🎯 8 个真相总结：所有'代码慢'的疑问，最终都收敛到：")
    print("   1. CPU 算力闲置？（流水线气泡、分支预测失败）")
    print("   2. 存储总线拥堵？（Cache Miss、TLB Miss）")
    print("   3. 上下文切换频繁？（Page Fault、Syscall）")
    print(f"{SEP}")
    print("📚 完整解读见：top-cs-projects/CSAPP_HARDWARE_TRUTHS.md")
    print("🎓 对应课程：UNIFIED_ROADMAP.md L03 (CMU 15-213 CSAPP)")


if __name__ == "__main__":
    main()
