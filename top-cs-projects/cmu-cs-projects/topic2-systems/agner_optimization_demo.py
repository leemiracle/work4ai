"""
Agner Fog 优化手册 · 7 个可运行优化模式 demo
=============================================
配套文档：../../top-cs-projects/AGNER_FOG_OPTIMIZATION.md
前置文档：CSAPP_HARDWARE_TRUTHS.md（8 个硬件真相）
姊妹代码：hardware_truths_demo.py

本文件用「微架构模拟器 + 微基准实测」演示 Agner Fog 优化手册的核心手法：
  §1 diagnose_bottleneck          —— 4 类瓶颈自动诊断（profile 后判定）
  §2 demo_uop_scheduling          —— Skylake 8 端口调度模拟（μop 吞吐瓶颈）
  §3 demo_ilp_accumulator         —— 单 vs 多 accumulator（打破依赖链）
  §4 demo_simd_throughput         —— SSE/AVX/AVX-512 吞吐 + AVX-512 降频陷阱
  §5 demo_instruction_substitution —— div/mul/branch/cmov 的 cycle 替换收益
  §6 demo_cpu_dispatch            —— CPUID 检测 + 运行时分发决策
  §7 demo_float_reciprocal        —— Newton-Raphson 浮点倒数近似（精度 vs 速度）

运行：
    python3 agner_optimization_demo.py            # 全部 7 个
    python3 agner_optimization_demo.py 2 4 7      # 只跑 §2 §4 §7

注意：纯 Python 看不到真实硬件 cycle（CPython 是解释器），所以 §2-§5 用
「微架构模拟器」按 Agner Vol 4 的 latency/throughput 数据计算理论 cycle；
§7 是真实可测的浮点近似。要测真实硬件 cycle 用 Agner 的 testp / perf。

核心教材：Agner Fog "Optimization manuals" Vol 1-5
        https://www.agner.org/optimize/（2025-2026 最新版）
"""
from __future__ import annotations
import sys
import time
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

SEP = "=" * 72
SUBSEP = "-" * 72


# ============================================================================
# Skylake 指令延迟数据（摘自 Agner Vol 4 + uops.info）
# ============================================================================

# (latency, throughput, uops, port)
# throughput = 该指令连续执行时平均占用端口的 cycle 数（越小越快）
SKYLAKE_INSTR = {
    # 整数 ALU
    "add":  (1, 0.25, 1, "0156"),    # 4 个 ALU 端口都能跑
    "sub":  (1, 0.25, 1, "0156"),
    "imul": (3, 1.00, 1, "1"),       # 只 port 1
    "idiv": (24, 24.0, 10, "0+1"),   # 极慢！占用 port 0+1 24 cycle
    "and":  (1, 0.25, 1, "0156"),
    "xor":  (1, 0.25, 1, "0156"),
    "shr":  (1, 0.50, 1, "06"),      # shift 在 0 或 6
    # 分支
    "jcc":  (0, 0.50, 1, "6"),       # branch port 6；预测对 0 cycle
    "cmov": (2, 1.00, 2, "0156"),
    # 内存
    "load": (4, 0.50, 1, "23"),      # L1 hit：4 cycle 延迟，2 个端口
    "store":(0, 1.00, 2, "4+7"),
    # 浮点
    "addss":  (4, 0.50, 1, "01"),
    "mulss":  (4, 0.50, 1, "01"),
    "divss":  (12, 6.0, 3, "0"),     # 浮点除法慢
    "vfmadd": (4, 0.50, 1, "01"),    # FMA
    # SIMD（向量）
    "addps_xmm":   (4, 0.50, 1, "01"),    # SSE: 4 floats
    "addps_ymm":   (4, 0.50, 1, "01"),    # AVX2: 8 floats
    "addps_zmm":   (4, 0.50, 1, "01"),    # AVX-512: 16 floats
}


# ============================================================================
# §1 4 类瓶颈自动诊断（Agner Vol 1 §1.7）
# ============================================================================

def diagnose_bottleneck():
    print(f"\n{SEP}\n§1 4 类性能瓶颈自动诊断（Agner Vol 1 §1.7）\n{SEP}")
    print("输入 perf stat 的关键计数器，自动判定瓶颈类型。\n")

    @dataclass
    class Profile:
        name: str
        ipc: float                  # IPC（每周期指令数）
        cache_miss_rate: float      # L1+L2 cache miss 占比（0-1）
        llc_miss_rate: float        # LLC miss 占比（0-1）
        branch_mispred_rate: float  # 分支误预测率（0-1）
        uops_port_saturation: float # 某个执行端口利用率（0-1）

    profiles = [
        Profile("热点 A（内存密集）", 0.4, 0.32, 0.15, 0.03, 0.5),
        Profile("热点 B（分支密集）", 1.1, 0.05, 0.01, 0.18, 0.4),
        Profile("热点 C（ILP 受限）", 0.7, 0.02, 0.005, 0.01, 0.5),
        Profile("热点 D（端口瓶颈）", 2.8, 0.03, 0.005, 0.01, 0.97),
        Profile("热点 E（CPU 不忙）", 3.5, 0.05, 0.01, 0.02, 0.6),
    ]

    def diagnose(p: Profile) -> str:
        # Agner 的 4 类判定规则（按优先级）
        if p.cache_miss_rate > 0.10 or p.llc_miss_rate > 0.05:
            return "1️⃣ 内存访问瓶颈  → 改数据布局（AoS→SoA）、对齐、预取"
        if p.branch_mispred_rate > 0.05:
            return "2️⃣ 分支预测瓶颈  → 位运算 / cmov 消除分支"
        if p.ipc < 1.0 and p.branch_mispred_rate < 0.05:
            return "3️⃣ ILP 受限      → 多 accumulator 打破依赖链"
        if p.uops_port_saturation > 0.90:
            return "4️⃣ μop 端口瓶颈  → 查 Vol 4 找替代指令（如 div→imul）"
        if p.ipc > 3.0:
            return "✅ 不是 CPU 瓶颈  → 看 IO/syscall/锁（参 CSAPP 真相 6）"
        return "❓ 混合瓶颈，需细化分析（用 testp 测指令级）"

    print(f"  {'热点':<22} {'IPC':>6} {'cache miss':>11} {'br mispred':>11} {'port sat':>9}  →  诊断")
    print(f"  {SUBSEP}")
    for p in profiles:
        print(f"  {p.name:<22} {p.ipc:>6.1f} {p.cache_miss_rate*100:>9.1f}% {p.branch_mispred_rate*100:>9.1f}% {p.uops_port_saturation*100:>8.0f}%  →  {diagnose(p)}")

    print(f"\n  💡 Agner 的方法论：先 profile（找 20% 热点）→ 再 classify（4 类瓶颈）→ 最后 optimize（对症下药）。")
    print(f"     90% 的'优化'失败，是因为开发者跳过了 profile，直接凭感觉优化。")


# ============================================================================
# §2 Skylake 8 端口 μop 调度模拟
# ============================================================================

def demo_uop_scheduling():
    print(f"\n{SEP}\n§2 Skylake 8 端口 μop 调度模拟（Agner Vol 3 §Skylake）\n{SEP}")
    print("硬件真相：Skylake 有 8 个执行端口，μop 吞吐受端口分布限制。\n")

    PORTS = ["0", "1", "2", "3", "4", "5", "6", "7"]

    @dataclass
    class Port:
        name: str
        busy_until: int = 0   # 该端口何时空闲
        executed: int = 0

    class Scheduler:
        """简化 μop 调度器：每个 μop 送到能跑它的端口，模拟 cycle 推进。"""
        def __init__(self):
            self.ports = {p: Port(p) for p in PORTS}
            self.clock = 0

        def issue(self, instr_ports: str, latency: int) -> int:
            """把一条 μop 送到最早空闲的兼容端口。返回完成 cycle。"""
            candidates = [self.ports[p] for p in instr_ports if p in self.ports]
            if not candidates:
                return self.clock
            # 选最早空闲的兼容端口
            best = min(candidates, key=lambda p: p.busy_until)
            start = max(self.clock, best.busy_until)
            finish = start + latency
            best.busy_until = finish
            best.executed += 1
            self.clock = max(self.clock, start)
            return finish

        def tick(self):
            self.clock += 1

    def simulate_sequence(seq: List[Tuple[str, str, int]]) -> Tuple[int, int]:
        """seq: [(instr_name, port_str, latency), ...] 假设无数据依赖。"""
        sch = Scheduler()
        last_finish = 0
        for name, ports, lat in seq:
            last_finish = max(last_finish, sch.issue(ports, lat))
        # 总 cycle = 最后一条完成
        return last_finish + 1, len(seq)

    # 场景 1：4 条独立 add（4 个 ALU 端口，1 cycle 内全部完成）
    seq_add = [("add", "0156", 1)] * 4
    cycles_add, n_add = simulate_sequence(seq_add)

    # 场景 2：4 条独立 imul（只 port 1，串行 4 cycle × 3 = 12 cycle）
    seq_imul = [("imul", "1", 3)] * 4
    cycles_imul, n_imul = simulate_sequence(seq_imul)

    # 场景 3：4 条独立 idiv（占用 port 0+1 各 24 cycle）
    seq_idiv = [("idiv", "0+1", 24)] * 4
    cycles_idiv, n_idiv = simulate_sequence(seq_idiv)

    # 场景 4：4 条独立 load（2 个 load 端口，4 cycle 延迟）
    seq_load = [("load", "23", 4)] * 4
    cycles_load, n_load = simulate_sequence(seq_load)

    print(f"  Skylake 端口分布：")
    print(f"    port 0/1: ALU+SIMD+FMA+mul   port 2/3: Load   port 4: Store 数据")
    print(f"    port 5: ALU+SIMD             port 6: ALU+branch  port 7: Store 地址\n")
    print(f"  {'指令序列':<22} {'可用端口':>10} {'延迟':>6} {'实测 cycle（4 条独立）':>24}")
    print(f"  {SUBSEP}")
    print(f"  {'add × 4':<22} {'0156':>10} {1:>5}cyc {cycles_add:>20}cyc  ✅ 4 端口并行")
    print(f"  {'imul × 4':<22} {'1':>10} {3:>5}cyc {cycles_imul:>20}cyc  ⚠️  单端口串行")
    print(f"  {'idiv × 4':<22} {'0+1':>10} {24:>5}cyc {cycles_idiv:>20}cyc  💥 除法极慢")
    print(f"  {'load × 4':<22} {'23':>10} {4:>5}cyc {cycles_load:>20}cyc  ✅ 2 端口并行")

    print(f"\n  💥 教训：同样的'4 条指令'，add 只要 {cycles_add} cycle，idiv 要 {cycles_idiv} cycle——差 {cycles_idiv/cycles_add:.0f}×。")
    print(f"  🛠 优化：把 idiv 换成 imul 倒数（编译器对常量除法自动做）；多用 add 而非 mul；preload 数据让 load 端口饱和。")


# ============================================================================
# §3 ILP：单 accumulator vs 多 accumulator（Agner Vol 1 §9.6）
# ============================================================================

def demo_ilp_accumulator():
    print(f"\n{SEP}\n§3 ILP 打破依赖链：单 vs 多 accumulator（Agner Vol 1 §9.6）\n{SEP}")
    print("硬件真相：浮点 add latency=4，单 accumulator 每条必须等前一条→IPC<1。\n")

    # 模拟 cycle-by-cycle 调度
    # 单 accumulator: 每条 add 依赖前一条，cycle 间隔 = latency
    # 多 accumulator: 4 条并行（每条用独立寄存器），cycle 间隔 = latency / 4（理论）

    LAT_ADD = 4   # float add 延迟
    PORTS_FADD = 2  # 2 个浮点 add 端口（port 0/1）

    def simulate(n: int, n_acc: int) -> int:
        """n 个加法，n_acc 个 accumulator 并行。返回总 cycle。"""
        # 每个 accumulator 是独立的依赖链，长度 = n/n_acc
        per_chain = math.ceil(n / n_acc)
        # 每条链 cycle = per_chain * LAT_ADD
        # 但多条链可并行（受 PORTS_FADD 限制）
        # 总 cycle = max(per_chain * LAT_ADD, n / PORTS_FADD)
        chain_latency = per_chain * LAT_ADD
        throughput_bound = math.ceil(n / PORTS_FADD)
        return max(chain_latency, throughput_bound)

    N = 1000
    print(f"  任务：{N} 个 float 累加，Skylake add latency={LAT_ADD}cyc，浮点端口={PORTS_FADD}个\n")
    print(f"  {'方案':<24} {'依赖链长度':>12} {'延迟 bound':>12} {'吞吐 bound':>12} {'实测 cycle':>12} {'IPC':>7}")
    print(f"  {SUBSEP}")
    for n_acc, label in [(1, "单 accumulator"), (2, "2-way"), (4, "4-way"), (8, "8-way"), (16, "16-way")]:
        per_chain = math.ceil(N / n_acc)
        chain_lat = per_chain * LAT_ADD
        thr_bound = math.ceil(N / PORTS_FADD)
        total = simulate(N, n_acc)
        ipc = N / total
        print(f"  {label:<24} {per_chain:>12} {chain_lat:>11}cyc {thr_bound:>11}cyc {total:>11}cyc {ipc:>6.2f}")

    single = simulate(N, 1)
    quad = simulate(N, 4)
    print(f"\n  💥 单→4-way 加速比：{single}/{quad} = {single/quad:.1f}×。")
    print(f"  💡 关键：编译器通常不会自动多 accumulator（浮点结合律不可假定），需要手写 + `-ffast-math`。")
    print(f"  🛠 优化：热点求和/点积/矩阵乘 都用多 accumulator；AVX-512 时 accumulator 数 = 寄存器数 / 2。")


# ============================================================================
# §4 SIMD 吞吐：SSE / AVX / AVX-512（+ 降频陷阱）
# ============================================================================

def demo_simd_throughput():
    print(f"\n{SEP}\n§4 SIMD 吞吐对比 + AVX-512 降频陷阱（Agner Vol 3 §Skylake-X）\n{SEP}")
    print("硬件真相：寄存器越宽，每周期算的 float 越多；但 AVX-512 触发降频。\n")

    # 理论峰值：FLOP/cycle = vector_width/32 × 2 FMA 端口 × 2(mul+add in FMA)
    configs = [
        ("标量 (scalar)",      1,  3.0, 0),   # 主频假设 3 GHz，无降频
        ("SSE2 (128-bit)",     4,  3.0, 0),
        ("AVX2 (256-bit)",     8,  3.0, 0),
        ("AVX-512 重 (512-bit)", 16, 2.4, 300),  # 降频 300 MHz
        ("AVX-512 轻 (256-in-zmm)", 8, 2.7, 100),  # 轻度降频
    ]

    FMA_PORTS = 2  # 2 个 FMA 端口
    OPS_PER_FMA = 2  # mul+add 算 2 flop

    print(f"  假设：CPU 标称 3.0 GHz，2 个 FMA 端口，每个 FMA 算 mul+add = 2 flop\n")
    print(f"  {'方案':<28} {'宽度':>6} {'主频':>8} {'FLOP/cyc':>10} {'GFLOP/s':>10} {'提速':>8}")
    print(f"  {SUBSEP}")
    base_gflops = None
    for name, width, freq_ghz, _ in configs:
        flop_per_cyc = width * FMA_PORTS * OPS_PER_FMA / (width if width > 1 else 1)  # 标量是 1×2×1=2
        # 修正：标量只有 1 个标量 FMA 端口对，向量化后才有 2 个
        if width == 1:
            flop_per_cyc = 2  # 1 mul + 1 add
        else:
            flop_per_cyc = width * 2  # 2 FMA 端口 × width × (mul+add in FMA)
        gflops = flop_per_cyc * freq_ghz
        if base_gflops is None:
            base_gflops = gflops
        ratio = gflops / base_gflops
        flag = ""
        if "重" in name:
            flag = " ⚠️降频"
        elif "轻" in name:
            flag = " ⚠️微降频"
        print(f"  {name:<28} {width*32:>5}b {freq_ghz:>6.1f}GHz {flop_per_cyc:>9}  {gflops:>8.0f}  {ratio:>6.1f}×{flag}")

    print(f"\n  💥 反直觉：AVX-512 重指令虽然每周期算 16 个 float，但降频 20% 后，")
    print(f"     短循环可能比 AVX2 还慢！这是 Intel Skylake-X / Ice Lake 的'AVX-512 transition penalty'。")
    print(f"  🛠 优化：(1) 用 'AVX-512 light'（128/256 指令但 zmm 寄存器）；")
    print(f"          (2) 循环足够长，让降频摊薄；(3) 测真实加速，别假设 16×。")


# ============================================================================
# §5 关键指令替换收益表（Agner Vol 4 数据）
# ============================================================================

def demo_instruction_substitution():
    print(f"\n{SEP}\n§5 关键指令替换收益（Agner Vol 4 latency/throughput 数据）\n{SEP}")
    print("硬件真相：div 比 mul 慢 5-10×，难预测 if 比 cmov 慢 8×。\n")

    # 用 SKYLAKE_INSTR 数据对比
    cases = [
        ("整数除以常量",   "idiv",  "imul(magic)", "idiv", "imul"),
        ("模 2 的幂",      "idiv",  "and",         "idiv", "and"),
        ("除 2 的幂",      "idiv",  "shr",         "idiv", "shr"),
        ("double 除法",    "divss", "mulss(N-R)",  "divss", "mulss"),
        ("难预测 if 赋值", "jcc",   "cmov",        "jcc",  "cmov"),
        ("分支求 max",     "jcc",   "cmov",        "jcc",  "cmov"),
    ]

    print(f"  {'场景':<18} {'慢指令':>10} {'快替代':>14} {'慢 latency':>12} {'快 latency':>12} {'提速':>8}")
    print(f"  {SUBSEP}")
    for scene, slow_name, fast_name, _, _ in cases:
        # jcc 的有效延迟取决于预测：误预测 ~18 cyc，预测对 0.5 cyc。这里取误预测代价。
        if slow_name == "jcc":
            slow_lat = 18  # 误预测代价（Agner Vol 3）
            fast_lat = SKYLAKE_INSTR["cmov"][0]
        elif slow_name == "divss":
            slow_lat = SKYLAKE_INSTR["divss"][0]
            fast_lat = SKYLAKE_INSTR["mulss"][0] * 2  # Newton-Raphson 2 次乘
        else:
            slow_lat = SKYLAKE_INSTR[slow_name][0]
            # 提取核心指令名（去掉括号后缀，如 "imul(magic)" -> "imul"）
            core = fast_name.split("(")[0].strip()
            fast_lat = SKYLAKE_INSTR.get(core, (0, 0, 0, ""))[0] or 1
        speedup = slow_lat / max(fast_lat, 1)
        print(f"  {scene:<18} {slow_name:>10} {fast_name:>14} {slow_lat:>10}cyc {fast_lat:>10}cyc {speedup:>6.1f}×")

    print(f"\n  💥 idiv → imul 提速 {SKYLAKE_INSTR['idiv'][0]/SKYLAKE_INSTR['imul'][0]:.0f}×（{SKYLAKE_INSTR['idiv'][0]}cyc → {SKYLAKE_INSTR['imul'][0]}cyc）；难预测 jcc → cmov 提速 {18/SKYLAKE_INSTR['cmov'][0]:.0f}×（18cyc → {SKYLAKE_INSTR['cmov'][0]}cyc）。")
    print(f"  🛠 优化：(1) 编译器对'常量除法'自动转 imul（看汇编验证）；(2) 手写位运算替代可预测的分支；")
    print(f"          (3) 浮点除法密集处用 rcpss + Newton-Raphson；（4) 永远用 -O3 + 看 Godbolt。")


# ============================================================================
# §6 CPU dispatch（运行时检测 + 分发决策）
# ============================================================================

def demo_cpu_dispatch():
    print(f"\n{SEP}\n§6 CPU Dispatch：运行时检测 + 分发（Agner Vol 1 §12）\n{SEP}")
    print("硬件真相：-march=native 只优化本机；分发到客户的二进制必须运行时检测。\n")

    # 模拟 CPUID 检测结果（真实场景用 __get_cpuid / cpuid 指令）
    @dataclass
    class CPUInfo:
        name: str
        # 特性位
        sse2: bool = False
        sse4_2: bool = False
        avx: bool = False
        avx2: bool = False
        avx512f: bool = False
        fma: bool = False
        # 微架构特征
        avx512_heavy: bool = False  # 触发重降频的 AVX-512

    test_cpus = [
        CPUInfo("Intel Core 2 (2007)",     sse2=True, sse4_2=False),
        CPUInfo("Intel Sandy Bridge (2011)", sse2=True, sse4_2=True, avx=True),
        CPUInfo("Intel Haswell (2013)",    sse2=True, sse4_2=True, avx=True, avx2=True, fma=True),
        CPUInfo("Intel Skylake-X (2017)",  sse2=True, sse4_2=True, avx=True, avx2=True, avx512f=True, fma=True, avx512_heavy=True),
        CPUInfo("AMD Zen 2 (2019)",        sse2=True, sse4_2=True, avx=True, avx2=True, fma=True),
        CPUInfo("Intel Alder Lake P-core", sse2=True, sse4_2=True, avx=True, avx2=True, fma=True),
    ]

    def pick_kernel(cpu: CPUInfo) -> str:
        """模拟 glibc / BLAS 的 dispatch 决策。"""
        if cpu.avx512f and not cpu.avx512_heavy:
            return "kernel_avx512（16-wide）"
        elif cpu.avx512f and cpu.avx512_heavy:
            # 关键判断：重 AVX-512 是否值得？看任务规模
            return "kernel_avx512_light 或 kernel_avx2（避免降频）"
        elif cpu.avx2 and cpu.fma:
            return "kernel_avx2_fma（8-wide）"
        elif cpu.avx:
            return "kernel_avx（4-wide）"
        elif cpu.sse4_2:
            return "kernel_sse42（4-wide）"
        elif cpu.sse2:
            return "kernel_sse2（2-wide）"
        return "kernel_scalar（兜底）"

    print(f"  {'CPU':<32} {'最高 SIMD':>14} {'Dispatch 决策':<48}")
    print(f"  {SUBSEP}")
    for cpu in test_cpus:
        if cpu.avx512f: top_simd = "AVX-512"
        elif cpu.avx2: top_simd = "AVX2"
        elif cpu.avx:  top_simd = "AVX"
        elif cpu.sse4_2: top_simd = "SSE4.2"
        else: top_simd = "SSE2"
        kernel = pick_kernel(cpu)
        print(f"  {cpu.name:<32} {top_simd:>14} {kernel}")

    print(f"\n  💡 真实案例：glibc 的 memcpy/strlen 就是这么做的——启动时检测一次，后续调用走函数指针。")
    print(f"  🛠 工具：(1) GCC `__attribute__((target_clones(\"avx2\",\"sse4.2\",\"default\")))` 自动 dispatch；")
    print(f"          (2) glibc `ifunc` 机制；(3) 手写 `__get_cpuid` + 函数指针表。")


# ============================================================================
# §7 Newton-Raphson 浮点倒数近似（真实可测）
# ============================================================================

def demo_float_reciprocal():
    print(f"\n{SEP}\n§7 Newton-Raphson 浮点倒数近似（精度 vs 速度）\n{SEP}")
    print("硬件真相：divss 延迟 12cyc，mulss 4cyc；用 rcpss + N-R 可近似倒数，提速 2×。\n")

    N = 2_000_000
    # 一组正数，要算 1/x
    import random
    random.seed(42)
    xs = [random.uniform(0.1, 100.0) for _ in range(N)]

    # 方法 1：硬件除法（基线）
    t0 = time.perf_counter_ns()
    div_result = [1.0 / x for x in xs]
    t_div = time.perf_counter_ns() - t0

    # 方法 2：Newton-Raphson 倒数（模拟硬件 rcpss 的 11-bit 低精度初值）
    # N-R 公式：y_{n+1} = y_n * (2 - x * y_n)
    # 硬件 rcpss 给 11 bit 相对精度；N-R 每次迭代精度翻倍：11→22→44 bit
    import struct

    def rcpss_approx(x: float) -> float:
        """模拟硬件 rcpss：返回 1/x 的 ~11 bit 相对精度近似。
        真实 rcpss 用 ROM 查表 + 线性插值；这里用清尾数低位来模拟精度损失。"""
        if x == 0:
            return 0.0
        y_exact = 1.0 / x
        # 转 float32（23 bit 尾数），清低 12 bit，模拟 11 bit 精度
        bits = struct.unpack('<I', struct.pack('<f', float(y_exact)))[0]
        bits &= ~0xFFF
        return struct.unpack('<f', struct.pack('<I', bits))[0]

    def newton_raphson_reciprocal(x: float, iters: int = 2) -> float:
        y = rcpss_approx(x)  # 模拟 rcpss 初值
        for _ in range(iters):
            y = y * (2.0 - x * y)  # N-R 迭代
        return y

    # 先展示 rcpss 初值的精度（无迭代）
    rcpss_err = max(abs(1.0/x - rcpss_approx(x)) for x in xs)

    # 用 1 次迭代（精度 ~22 bit，接近 IEEE 单精度极限）
    t0 = time.perf_counter_ns()
    nr1_result = [newton_raphson_reciprocal(x, 1) for x in xs]
    t_nr1 = time.perf_counter_ns() - t0

    # 用 2 次迭代（精度 ~44 bit，超过 IEEE 单精度）
    t0 = time.perf_counter_ns()
    nr2_result = [newton_raphson_reciprocal(x, 2) for x in xs]
    t_nr2 = time.perf_counter_ns() - t0

    # 误差分析（相对硬件精确除法）
    err_rcpss = rcpss_err
    err1 = max(abs(a - b)/a for a, b in zip(div_result, nr1_result))
    err2 = max(abs(a - b)/a for a, b in zip(div_result, nr2_result))

    print(f"  任务：对 {N:,} 个随机浮点数计算 1/x\n")
    print(f"  N-R 收敛性（rcpss 初值精度低，N-R 迭代精度翻倍）：\n")
    print(f"  {'方法':<32} {'相对误差':>14}  精度等级")
    print(f"  {SUBSEP}")
    print(f"  {'rcpss 初值（11 bit）':<32} {err_rcpss:>14.2e}  ~11 bit（硬件 rcpss）")
    print(f"  {'rcpss + N-R 1 次迭代':<32} {err1:>14.2e}  ~22 bit（IEEE float32 满精度）")
    print(f"  {'rcpss + N-R 2 次迭代':<32} {err2:>14.2e}  ~44 bit（超过 float32）")

    print(f"\n  耗时（本机 Python 实测，仅作对比；真实收益在 C/SIMD 层）：")
    print(f"  {'方法':<32} {'耗时':>10} {'相对':>8}")
    print(f"  {SUBSEP}")
    print(f"  {'硬件除法 1/x':<32} {t_div/1e6:>7.0f} ms {'1.0×':>8}")
    print(f"  {'rcpss + N-R 1 次（2 mul）':<32} {t_nr1/1e6:>7.0f} ms {t_div/t_nr1:>7.2f}×")
    print(f"  {'rcpss + N-R 2 次（4 mul）':<32} {t_nr2/1e6:>7.0f} ms {t_div/t_nr2:>7.2f}×")

    # 注意：Python 层 N-R 反而慢（因为多用了乘法，且 Python 除法不慢）
    # 真实收益在 C/汇编层：用 rcpss 替代除法 + N-R 修正，divss 12cyc → rcpss(4) + 2*mulss(8) = 12cyc
    # 真正加速来自：(1) 并行多个倒数（FMA 吞吐高）；(2) 避免长依赖链

    print(f"\n  ⚠️  注意：本机实测 N-R 可能不比硬件除法快（Python 层看不出，硬件 divsd 也才 13cyc）。")
    print(f"     真实收益在 SIMD 批量场景：8 个并行倒数（AVX2），8×divss=96cyc vs 8×(rcpss+2mulss)=48cyc，**2× 加速**。")
    print(f"  🛠 工程结论：(1) 单个倒数用硬件 div；(2) 批量倒数用 rcpss + N-R + SIMD；")
    print(f"              (3) 量化交易/3D 渲染里常用；（4) rcpss(11bit) + 1 次 N-R ≈ 10⁻⁷（float32 满）；+ 2 次 ≈ 10⁻¹⁴（float64 满）。")


# ============================================================================
# 主入口
# ============================================================================

DEMOS = {
    1: ("4 类瓶颈自动诊断",        diagnose_bottleneck),
    2: ("Skylake 8 端口 μop 调度",  demo_uop_scheduling),
    3: ("ILP 打破依赖链",           demo_ilp_accumulator),
    4: ("SIMD 吞吐 + AVX-512 降频", demo_simd_throughput),
    5: ("关键指令替换收益",         demo_instruction_substitution),
    6: ("CPU Dispatch 决策",        demo_cpu_dispatch),
    7: ("Newton-Raphson 倒数近似",  demo_float_reciprocal),
}


def main():
    print("╔" + "═" * 70 + "╗")
    print("║" + " Agner Fog 优化手册 · 7 个可运行优化模式 demo ".center(70) + "║")
    print("║" + " 配套：top-cs-projects/AGNER_FOG_OPTIMIZATION.md ".center(70) + "║")
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
                import traceback
                print(f"  [!] §{n} 运行出错：{e}")
                traceback.print_exc()
        else:
            print(f"  [!] 未知 demo 编号：{n}（可选 1-7）")

    print(f"\n{SEP}")
    print("🎯 Agner 优化总纲：Profile → Classify 4 类瓶颈 → 对症下药 → 测验证。")
    print("   1. 内存瓶颈  → AoS→SoA、对齐、预取（参 CSAPP 真相 1）")
    print("   2. 分支瓶颈  → 位运算 / cmov / 数据有序化（参 CSAPP 真相 4）")
    print("   3. ILP 瓶颈  → 多 accumulator、独立指针（参 CSAPP 真相 7）")
    print("   4. 端口瓶颈  → 查 Vol 4 找替代指令（div→mul、branch→cmov）")
    print(f"{SEP}")
    print("📚 完整解读：top-cs-projects/AGNER_FOG_OPTIMIZATION.md")
    print("🔬 前置原理：top-cs-projects/CSAPP_HARDWARE_TRUTHS.md（8 个硬件真相）")
    print("🎓 对应课程：UNIFIED_ROADMAP.md L03 (CMU 15-213) + L21 (CMU 10-414 MLSys)")


if __name__ == "__main__":
    main()
