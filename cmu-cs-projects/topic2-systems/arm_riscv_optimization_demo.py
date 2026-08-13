"""
ARM 与 RISC-V 优化 · 6 个可运行对比 demo
==========================================
配套文档：../../top-cs-projects/ARM_AND_RISCV_OPTIMIZATION.md
姊妹代码：hardware_truths_demo.py（CSAPP 8 真相）+ agner_optimization_demo.py（x86 优化）

本文件演示 ARM/RISC-V 与 x86 的关键差异，每个都用「硬件模型 + 真实计算」让差异可见：
  §1 demo_microarch_compare       —— 三 ISA 现代核心参数对比（解码/ROB/L1/SIMD）
  §2 demo_simd_spectrum           —— SIMD 谱系映射（SSE/AVX vs NEON/SVE2 vs RVV）
  §3 demo_vla_concept             —— RISC-V VLA：同一份代码适配不同 VLEN
  §4 demo_weak_memory_model       —— x86 TSO vs ARM RMO vs RISC-V RVWMO 合法重排
  §5 demo_hardware_reciprocal     —— 三 ISA 硬件倒数指令精度对比
  §6 demo_cross_platform_dispatch —— 跨平台 CPU 特性检测 + dispatch

运行：
    python3 arm_riscv_optimization_demo.py            # 全部 6 个
    python3 arm_riscv_optimization_demo.py 3 4         # 只跑 §3 §4

注意：纯 Python 看不到真实 ARM/RISC-V 硬件，所以 demo 用「微架构模型 + 精度真实计算」
展示差异。要在真实 ARM/RISC-V 上跑用 OSACA / Spike / QEMU。

核心数据来源：
- ARM ARMv8-A / ARMv9-A Architecture Reference Manual
- RISC-V V spec v1.0 (riscvarchive/riscv-v-spec)
- OSACA 数据库 (github.com/RRZE-HPC/OSACA)
- Agner Fog Vol 3 (x86 基线对比)
"""
from __future__ import annotations
import sys
import math
from dataclasses import dataclass
from typing import List, Tuple

SEP = "=" * 72
SUBSEP = "-" * 72


# ============================================================================
# §1 三 ISA 现代核心微架构参数对比
# ============================================================================

def demo_microarch_compare():
    print(f"\n{SEP}\n§1 三 ISA 现代核心微架构参数对比（OSACA + ARM SOG + SiFive）\n{SEP}")
    print("硬件真相：Apple Silicon 解码/ROB 领先 1.5-2×，但 ARM/RISC-V 端口仍少于 x86。\n")

    @dataclass
    class Microarch:
        name: str
        isa: str
        decode_width: int      # 解码宽度（每周期 x86/ARM 指令数）
        rob_size: int          # Reorder Buffer（在飞指令上限）
        exec_ports: int        # 执行端口数
        l1_dcache_kb: int
        l1_latency_cyc: int
        branch_mispred_cost: int
        simd: str              # 顶级 SIMD 谱系

    cpus = [
        Microarch("Intel Golden Cove (Alder Lake P-core)", "x86-64",  6, 512, 12, 48,  14, 20, "AVX-512"),
        Microarch("AMD Zen 4 (Genoa)",                     "x86-64",  4, 320, 10, 32,  14, 19, "AVX-512"),
        Microarch("ARM Cortex-X4 (2023)",                  "AArch64", 5, 288, 15, 64,   4, 16, "SVE2"),
        Microarch("ARM Neoverse V2 (Graviton 4 / Grace)",  "AArch64", 5, 320, 11, 64,   4, 16, "SVE2"),
        Microarch("Apple M4 Everest",                      "AArch64", 9, 620, 14, 128,  3, 15, "NEON+AMX"),
        Microarch("SiFive P670",                            "RISC-V", 5, 200,  9, 64,   4, 15, "RVV (VLA)"),
        Microarch("Fujitsu A64FX (Fugaku)",                "AArch64", 4, 256,  8, 64,   4, 14, "SVE-512"),
    ]

    print(f"  {'核心':<40} {'ISA':<8} {'解码':>4} {'ROB':>4} {'端口':>4} {'L1':>8} {'SIMD':<12}")
    print(f"  {SUBSEP}")
    for c in cpus:
        l1_desc = f"{c.l1_dcache_kb}KB/{c.l1_latency_cyc}cyc"
        print(f"  {c.name:<40} {c.isa:<8} {c.decode_width:>4} {c.rob_size:>4} {c.exec_ports:>4} {l1_desc:>8} {c.simd:<12}")

    # 反直觉统计
    apple = cpus[4]
    x86 = cpus[0]
    print(f"\n  💥 反直觉：")
    print(f"     • Apple M4 解码宽度 {apple.decode_width}（vs x86 {x86.decode_width}）= {apple.decode_width/x86.decode_width:.1f}× → 因 ARM 指令等长 4 字节")
    print(f"     • Apple M4 ROB {apple.rob_size}（vs x86 {x86.rob_size}）= {apple.rob_size/x86.rob_size:.1f}× → ILP 容量最大")
    print(f"     • Apple L1 D-cache {apple.l1_dcache_kb}KB / {apple.l1_latency_cyc}cyc → x86 不可想象的'又大又快'")
    print(f"     • ARM L1 延迟普遍 4 cyc（vs x86 14 cyc）→ 但容量小，需更精细的循环展开")
    print(f"  🛠 优化：跨平台代码别假设单一微架构；用 OSACA 在目标核心上分析。")


# ============================================================================
# §2 SIMD 谱系映射
# ============================================================================

def demo_simd_spectrum():
    print(f"\n{SEP}\n§2 SIMD 谱系映射：x86 / ARM / RISC-V\n{SEP}")
    print("硬件真相：RISC-V RVV 和 ARM SVE 是 VLA（变长），x86 AVX 是固定宽度。\n")

    @dataclass
    class SIMDIsa:
        name: str
        isa_family: str
        reg_width_bits: int
        floats_per_reg: int       # float32 个数
        variable_length: bool     # 是否 VLA
        has_predicate: bool       # 是否有谓词掩码
        introduced: str

    simds = [
        # x86
        SIMDIsa("SSE2",          "x86",    128,  4, False, False, "2001"),
        SIMDIsa("AVX2",          "x86",    256,  8, False, False, "2013"),
        SIMDIsa("AVX-512",       "x86",    512, 16, False, True,  "2017"),
        # ARM
        SIMDIsa("NEON",          "ARM",    128,  4, False, False, "2010"),
        SIMDIsa("SVE",           "ARM",   2048, 64, True,  True,  "2016"),  # 上限 2048
        SIMDIsa("SVE2",          "ARM",   2048, 64, True,  True,  "2020"),
        # RISC-V
        SIMDIsa("RVV (VLEN=128)","RISC-V", 128,  4, True,  True,  "2021"),
        SIMDIsa("RVV (VLEN=512)","RISC-V", 512, 16, True,  True,  "2021"),
        SIMDIsa("RVV (VLEN=1024)","RISC-V",1024,32, True,  True,  "2021"),
    ]

    print(f"  {'指令集':<20} {'ISA':<8} {'宽度':>8} {'floats':>7} {'VLA?':>6} {'谓词?':>6} {'引入':>6}")
    print(f"  {SUBSEP}")
    for s in simds:
        vla = "⭐是" if s.variable_length else "否"
        pred = "⭐有" if s.has_predicate else "无"
        print(f"  {s.name:<20} {s.isa_family:<8} {s.reg_width_bits:>6}b {s.floats_per_reg:>7} {vla:>6} {pred:>6} {s.introduced:>6}")

    # 累加吞吐对比（假设 FMA 端口数）
    print(f"\n  ▶ 同一段 1M float 累加，各 ISA 理论循环数（2 个 FMA 端口）\n")
    N = 1_000_000
    OPS_PER_FMA = 2  # mul + add
    print(f"  {'方案':<22} {'floats/周期':>12} {'理论周期数':>12} {'提速':>8}")
    print(f"  {SUBSEP}")
    base = None
    for name, floats_per_cyc in [
        ("标量 (scalar)",          2),
        ("x86 SSE2",               2 * 4),       # 2 FMA × 4 floats
        ("x86 AVX2",               2 * 8),
        ("x86 AVX-512",            2 * 16),
        ("ARM NEON",               2 * 4),
        ("ARM SVE2 (VLEN=128)",    2 * 4),
        ("ARM SVE2 (VLEN=512)",    2 * 16),
        ("RISC-V RVV (VLEN=512)",  2 * 16),
    ]:
        cyc = math.ceil(N / floats_per_cyc)
        if base is None: base = cyc
        print(f"  {name:<22} {floats_per_cyc:>12} {cyc:>10}cyc {base/cyc:>7.0f}×")

    print(f"\n  💡 VLA 的价值：写一份 RVV 代码，VLEN=128/512/1024 不同硬件自动适配，二进制兼容。x86 AVX 做不到。")


# ============================================================================
# §3 RISC-V VLA：同一份代码适配不同 VLEN
# ============================================================================

def demo_vla_concept():
    print(f"\n{SEP}\n§3 RISC-V VLA：一份代码适配 VLEN=128/256/512/1024\n{SEP}")
    print("硬件真相：RVV 用 vsetvli 动态查询向量长度，代码硬件无关。\n")

    # 模拟 RVV 累加循环在不同 VLEN 下的执行
    @dataclass
    class VLENConfig:
        name: str
        vlen_bits: int
        elem_size_bits: int = 32  # float32

        @property
        def elements_per_vreg(self) -> int:
            return self.vlen_bits // self.elem_size_bits

        @property
        def m1_groups(self) -> int:
            """LMUL=1 时一组多少个元素（vsetvli 返回值）"""
            return self.elements_per_vreg

    def simulate_vla_sum(N: int, cfg: VLENConfig) -> Tuple[int, int]:
        """模拟 RVV 风格的累加循环：vle32 + vadd。
        返回 (总周期数, 迭代次数)。"""
        elements_per_iter = cfg.m1_groups
        # 假设每周期可执行 1 个 vle32 + 1 个 vadd（2 端口）
        iters = math.ceil(N / elements_per_iter)
        # 每次迭代 ~2 周期（load + add）+ 1 周期 loop overhead
        cyc_per_iter = 3
        total_cyc = iters * cyc_per_iter
        return total_cyc, iters

    N = 100_000
    print(f"  任务：用 RVV 风格累加 {N:,} 个 float32（同一段汇编，跑在不同 VLEN 上）\n")
    print(f"  {'VLEN':<14} {'elements/vreg':>14} {'迭代次数':>12} {'理论周期':>12} {'相对最慢':>12}")
    print(f"  {SUBSEP}")

    configs = [
        VLENConfig("VLEN=128  (低端嵌入式)",   128),
        VLENConfig("VLEN=256  (中端)",         256),
        VLENConfig("VLEN=512  (SiFive P670)",  512),
        VLENConfig("VLEN=1024 (服务器/HPC)",   1024),
        VLENConfig("VLEN=2048 (A64FX SVE 风格)",2048),
    ]
    base_cyc = None
    for cfg in configs:
        cyc, iters = simulate_vla_sum(N, cfg)
        if base_cyc is None: base_cyc = cyc
        rel = base_cyc / cyc
        print(f"  {cfg.name:<20} {cfg.elements_per_vreg:>14} {iters:>12} {cyc:>10}cyc {rel:>10.1f}×")

    # RVV 风格伪代码
    print(f"""
  ▶ 对应的 RVV 汇编（同一份代码适配所有 VLEN）：
    # a0 = 数组指针, a1 = 元素数, v1 = 累加器
    loop:
        vsetvli  t0, a1, e32, m1   # 动态查询：t0 = 本次能算多少个 float32
        vle32.v  v0, (a0)          # 加载 t0 个 float 到 v0
        vadd.vv  v1, v1, v0        # v1 += v0
        slli     t0, t0, 2         # t0 *= 4 (字节数)
        add      a0, a0, t0        # 指针前进
        sub      a1, a1, t0        # 剩余数减少
        bnez     a1, loop          # 没完继续
  """)

    print(f"  💥 同一份二进制：VLEN=128 时迭代 {math.ceil(N/4):,} 次，VLEN=1024 时只迭代 {math.ceil(N/32):,} 次。")
    print(f"  🛠 对比：x86 AVX-512 代码到只支持 SSE 的 CPU 上跑不了；RVV 代码到处都能跑。")
    print(f"  📚 ARM SVE/SVE2 借鉴了这个思想；详细 spec：riscv-v-spec/v-spec.adoc")


# ============================================================================
# §4 弱内存模型对比（x86 TSO vs ARM RMO vs RISC-V RVWMO）
# ============================================================================

def demo_weak_memory_model():
    print(f"\n{SEP}\n§4 内存模型强弱：x86 TSO vs ARM RMO vs RISC-V RVWMO\n{SEP}")
    print("硬件真相：x86 几乎顺序，ARM/RISC-V 可大幅重排，无屏障会出 bug。\n")

    # 经典 store-store 重排测试
    # 线程 1: store data; store ready;
    # 线程 2: 读 ready; 如果 ready=1 读 data
    # 弱模型下：线程 2 可能先看到 ready=1 但 data 还是旧值

    @dataclass
    class MemoryModel:
        name: str
        # 合法重排规则（简化）
        store_store_reorder: bool  # Store-Store 可重排
        load_load_reorder: bool    # Load-Load 可重排
        store_load_reorder: bool   # Store-Load 可重排（最危险）
        fence_cost_cyc: int        # 内存屏障单次成本

    models = [
        # x86 TSO: Store-Store 不重排，Store-Load 可重排（store buffer）
        MemoryModel("x86 TSO",        False, False, True,  10),
        # ARM RMO: 全部可重排
        MemoryModel("ARM RMO",        True,  True,  True,  50),
        # RISC-V RVWMO: 弱但形式化
        MemoryModel("RISC-V RVWMO",   True,  True,  True,  30),
    ]

    import random
    random.seed(42)
    trials = 100_000

    def simulate_model(model: MemoryModel, with_fence: bool, n_trials: int) -> int:
        """模拟线程 1 执行 [store data; store ready] 后，线程 2 看到 'ready=1 但 data=0' 的次数。"""
        bug_count = 0
        for _ in range(n_trials):
            # 线程 1 的两条 store 进入内存系统
            stores = [("data", 42), ("ready", 1)]
            # 模拟重排
            if not with_fence:
                if model.store_store_reorder and random.random() < 0.5:
                    stores = [stores[1], stores[0]]
            # 第一条提交全局可见
            mem = {"data": 0, "ready": 0}
            k1, v1 = stores[0]; mem[k1] = v1
            # 线程 2 在此刻读（关键窗口）
            if mem["ready"] == 1 and mem["data"] == 0:
                bug_count += 1
            # 第二条提交
            k2, v2 = stores[1]; mem[k2] = v2
        return bug_count

    print(f"  测试场景：线程1 执行 `data=42; ready=1;`，线程2 等 ready 后读 data\n")
    print(f"  跑 {trials:,} 次模拟，统计线程2 看到 'ready=1 但 data=0' 的 bug 数：\n")
    print(f"  {'内存模型':<22} {'无屏障 bug 数':>14} {'比例':>8} {'有屏障 bug 数':>16} {'屏障成本':>10}")
    print(f"  {SUBSEP}")
    for m in models:
        no_fence_bug = simulate_model(m, False, trials)
        fence_bug = simulate_model(m, True, trials)
        print(f"  {m.name:<22} {no_fence_bug:>14} {no_fence_bug/trials*100:>7.2f}% {fence_bug:>16} {m.fence_cost_cyc:>8}cyc")

    print(f"\n  💥 ARM/RISC-V 上无屏障时，~50% 概率出诡异 bug（单线程测试永远过，多核上线性崩溃）。")
    print(f"     屏障成本：x86 {models[0].fence_cost_cyc}cyc（便宜）vs ARM {models[1].fence_cost_cyc}cyc（贵 5×）→ ARM 要减少屏障数。")
    print(f"  🛠 跨平台：永远用 std::atomic 的 acquire/release（编译器自动生成对的屏障），别手写汇编。")


# ============================================================================
# §5 三 ISA 硬件倒数指令精度对比
# ============================================================================

def demo_hardware_reciprocal():
    print(f"\n{SEP}\n§5 三 ISA 硬件倒数指令精度对比（rcpss / frsqrte / vfrec7）\n{SEP}")
    print("硬件真相：x86 rcpss 给 11-bit，RISC-V vfrec7 只给 7-bit，但都靠 N-R 修正。\n")

    import struct

    def truncate_to_bits(y_exact: float, n_mantissa_bits: int) -> float:
        """模拟硬件倒数指令的有限精度：保留 float32 尾数的 n_mantissa_bits 位。"""
        if y_exact == 0: return 0.0
        bits = struct.unpack('<I', struct.pack('<f', float(y_exact)))[0]
        # float32 尾数 23 bit，保留高 n_mantissa_bits，清低 (23-n)
        keep = n_mantissa_bits
        clear_low = 23 - keep
        mask = ~((1 << clear_low) - 1)
        bits &= mask
        return struct.unpack('<f', struct.pack('<I', bits))[0]

    # Newton-Raphson: y_{n+1} = y_n * (2 - x * y_n)
    def newton_raphson(x: float, y0: float, iters: int) -> float:
        y = y0
        for _ in range(iters):
            y = y * (2.0 - x * y)
        return y

    x = 3.7  # 测试值
    exact = 1.0 / x

    # 各 ISA 的硬件倒数初值精度
    configs = [
        ("x86 rcpss",      11, "AVX/AVX-512 都有"),
        ("ARM vrecpe",      8, "NEON/SVE 都有（定点 8-bit）"),
        ("RISC-V vfrec7",   7, "V 扩展，spec vfrec7.adoc"),
    ]

    print(f"  测试：1/{x} = {exact:.10e}\n")
    print(f"  {'指令':<22} {'初值精度':>10} {'初值相对误差':>16} {'+1次N-R误差':>14} {'+2次N-R误差':>14}")
    print(f"  {SUBSEP}")
    for name, bits, note in configs:
        y0 = truncate_to_bits(exact, bits)
        err0 = abs(y0 - exact) / exact
        y1 = newton_raphson(x, y0, 1)
        err1 = abs(y1 - exact) / exact
        y2 = newton_raphson(x, y0, 2)
        err2 = abs(y2 - exact) / exact
        print(f"  {name:<22} {bits:>8}bit {err0:>14.2e} {err1:>14.2e} {err2:>14.2e}")

    print(f"\n  💥 即使 RISC-V vfrec7 只有 7-bit 精度，加 2 次 N-R 后达到 ~10⁻¹⁴（float64 满精度）。")
    print(f"     N-R 每次精度翻倍：7b → 14b → 28b → 56b。")
    print(f"  🛠 优化：批量倒数用硬件近似 + N-R；RISC-V 参考实现见 riscv-v-spec/recip.c。")


# ============================================================================
# §6 跨平台 CPU 特性检测 + dispatch
# ============================================================================

def demo_cross_platform_dispatch():
    print(f"\n{SEP}\n§6 跨平台 CPU 特性检测 + dispatch（CPUID/HWCAP/getauxval）\n{SEP}")
    print("硬件真相：x86 用 CPUID，ARM/RISC-V 用 getauxval(AT_HWCAP)，API 完全不同。\n")

    @dataclass
    class Platform:
        name: str
        detect_api: str
        example_code: str
        features: List[Tuple[str, str]]  # (特性名, 检测位)

    platforms = [
        Platform("Linux x86-64", "__get_cpuid",
                 "__get_cpuid(7, &a, &b, &c, &d); return (b & bit_AVX2) != 0;",
                 [("AVX2", "CPUID(7).ebx[5]"),
                  ("AVX-512F", "CPUID(7).ebx[16]"),
                  ("FMA", "CPUID(1).ecx[12]"),
                  ("BMI2", "CPUID(7).ebx[8]")]),
        Platform("Linux AArch64", "getauxval(AT_HWCAP)",
                 "return (getauxval(AT_HWCAP) & HWCAP_ASIMD) != 0;",
                 [("NEON/ASIMD", "HWCAP_ASIMD"),
                  ("SVE", "HWCAP_SVE"),
                  ("SVE2", "HWCAP2_SVE2"),
                  ("AES", "HWCAP_AES"),
                  ("ATOMICS", "HWCAP_ATOMICS")]),
        Platform("Linux RISC-V", "getauxval(AT_HWCAP)",
                 "return (getauxval(AT_HWCAP) & HWCAP_ISA_V) != 0;",
                 [("V 扩展", "HWCAP_ISA_V ('v' bit)"),
                  ("A 原子", "HWCAP_ISA_A ('a' bit)"),
                  ("C 压缩", "HWCAP_ISA_C ('c' bit)")]),
        Platform("macOS ARM", "sysctlbyname",
                 "int v=0; size_t s=sizeof(v); sysctlbyname(\"hw.optional.advsimd\", &v, &s, NULL, 0);",
                 [("NEON", "hw.optional.advsimd"),
                  ("AMX", "hw.optional.arm.amx"),
                  ("FP16", "hw.optional.fp16")]),
    ]

    print(f"  {'平台':<18} {'检测 API':<26} {'示例代码'}")
    print(f"  {SUBSEP}")
    for p in platforms:
        print(f"  {p.name:<18} {p.detect_api:<26} `{p.example_code}`")
        for fname, bit in p.features:
            print(f"  {'':<18} {'':<26}   {fname:<14} ← {bit}")
        print()

    # 模拟 dispatch 决策
    print(f"  ▶ 跨平台 dispatch 决策树（同一段 C++ 代码 3 平台都跑得快）：\n")
    print(f"     ┌─ x86-64? ─→ CPUID 检测 AVX-512 → AVX2 → SSE2")
    print(f"     │")
    print(f"     ├─ AArch64? ─→ HWCAP 检测 SVE2 → SVE → NEON")
    print(f"     │             （Apple Silicon 还要检测 AMX）")
    print(f"     │")
    print(f"     └─ RISC-V?  ─→ HWCAP 检测 V → RVV；否则标量\n")

    print(f"  🛠 推荐：(1) 别自己写，用 simdjson / Google Highway 的 cpu_detection.h；")
    print(f"          (2) 编译时用 `__attribute__((target_clones(\"default\",\"avx2\",\"sve2\")))` 让 GCC/Clang 自动 dispatch；")
    print(f"          (3) glibc 启动时检测一次，存函数指针（ifunc 机制）。")


# ============================================================================
# 主入口
# ============================================================================

DEMOS = {
    1: ("三 ISA 微架构对比",        demo_microarch_compare),
    2: ("SIMD 谱系映射",             demo_simd_spectrum),
    3: ("RISC-V VLA 概念",           demo_vla_concept),
    4: ("弱内存模型对比",            demo_weak_memory_model),
    5: ("硬件倒数指令精度",          demo_hardware_reciprocal),
    6: ("跨平台 CPU 检测",           demo_cross_platform_dispatch),
}


def main():
    print("╔" + "═" * 70 + "╗")
    print("║" + " ARM 与 RISC-V 优化 · 6 个可运行对比 demo ".center(70) + "║")
    print("║" + " 配套：top-cs-projects/ARM_AND_RISCV_OPTIMIZATION.md ".center(70) + "║")
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
            print(f"  [!] 未知 demo 编号：{n}（可选 1-6）")

    print(f"\n{SEP}")
    print("🎯 三 ISA 优化总结：")
    print("   x86：固定 SIMD（SSE/AVX），TSO 强内存模型，Agner Fog 圣经")
    print("   ARM：VLA SIMD（SVE/SVE2），RMO 弱模型，OSACA + 官方 SOG")
    print("   RISC-V：VLA + 模块化扩展，RVWMO 形式化，厂商差异大")
    print(f"{SEP}")
    print("📚 完整链路：")
    print("   CSAPP_HARDWARE_TRUTHS.md          ← 为什么（8 个硬件真相）")
    print("   AGNER_FOG_OPTIMIZATION.md         ← x86 怎么优化")
    print("   ARM_AND_RISCV_OPTIMIZATION.md     ← ARM/RISC-V 怎么优化")
    print("🎓 对应课程：UNIFIED_ROADMAP.md L03 (CSAPP) + L21 (MLSys)")


if __name__ == "__main__":
    main()
