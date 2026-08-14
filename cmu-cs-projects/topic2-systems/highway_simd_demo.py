"""
Google Highway SIMD 库 · 7 个可运行思想 demo
============================================
配套文档：../../top-cs-projects/HIGHWAY_SIMD_LIBRARY.md
前置文档：CSAPP_HARDWARE_TRUTHS.md（硬件真相）
姊妹代码：agner_optimization_demo.py / arm_riscv_optimization_demo.py

本文档不是真跑 Highway（那是 C++ 库），而是用 numpy + 纯 Python **模拟 Highway 的
核心抽象与设计思想**——目的是让读者在不装 C++ 编译器的前提下，直观理解：

  §1 demo_lane_concept            —— SIMD lane 概念 + 5 种向量宽度对比（SSE/AVX2/AVX-512/SVE/RVV）
  §2 demo_aos_vs_soa              —— AOS vs SOA 内存布局（Highway 推荐的 SOA 模式）
  §3 demo_strip_mining_strategies —— Highway 4 种 strip-mining 策略模拟（README §5）
  §4 demo_static_vs_dynamic_dispatch —— HWY_STATIC vs HWY_DYNAMIC dispatch 机制
  §5 demo_mask_predication        —— 标量 if vs Highway Mask/IfThenElse 谓词
  §6 demo_highway_api_cheatsheet  —— 用 numpy 模拟 Highway Tag/Vec/Mask 三件套
  §7 demo_saxpy_three_ways        —— SAXPY 真实案例：标量 / Highway 风格 / numpy 三种写法

运行：
    python3 highway_simd_demo.py            # 全部 7 个
    python3 highway_simd_demo.py 2 4 7      # 只跑 §2 §4 §7

注意：纯 Python/numpy 看不到真实 SIMD cycle 加速（CPython 是解释器，numpy 内部有 SIMD 但
对我们不透明）。本文 demo 用「指令计数 + 模拟内存访问」展示 SIMD 编程的思想，要测真实
硬件加速用 Highway C++ + Agner 的 testp / perf。

核心参考：
- Highway README https://github.com/google/highway/blob/master/README.md
- Highway design_philosophy.md / quick_reference.md / faq.md
- 配套文档 HIGHWAY_SIMD_LIBRARY.md 第三旗舰
"""
from __future__ import annotations
import sys
import time
import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

# numpy 仅在 DL/CV 主题可选；Highway 是 SIMD 主题，用 numpy 模拟向量化最直观
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

SEP = "=" * 72
SUBSEP = "-" * 72


# ============================================================================
# Highway 27 target 元数据（来自 README §Current status）
# ============================================================================

@dataclass
class Target:
    name: str            # Highway target 名（如 'AVX2'）
    arch: str            # 架构（'x86' / 'ARM' / 'RISC-V' / ...）
    vlen_bits: int       # 向量位宽（固定宽度架构）；VLA 架构写典型值
    is_vla: bool = False # 是否 Vector Length Agnostic（SVE / RVV）
    notes: str = ""


# 27 个 target（README §Current status 完整对照）
HIGHWAY_TARGETS: List[Target] = [
    # Any（保底）
    Target("SCALAR", "Any", 32, False, "纯标量 fallback，每 cycle 1 元素"),
    Target("EMU128", "Any", 128, False, "128b 软件模拟"),
    # ARM
    Target("NEON_WITHOUT_AES", "ARMv7", 128, False, "无 AES 的早期 NEON"),
    Target("NEON", "ARMv7+", 128, False, "标准 NEON (32×128b)"),
    Target("NEON_BF16", "ARMv8.6+", 128, False, "NEON + BF16"),
    Target("SVE", "ARMv8.6", 128, True, "VLA！寄存器 128-2048b，含谓词"),
    Target("SVE2", "ARMv9", 128, True, "SVE 实用化 + NEON 大部分功能"),
    Target("SVE_256", "ARMv9", 256, True, "假设 VLEN=256（如 A64FX）"),
    Target("SVE2_128", "ARMv9", 128, True, "假设 VLEN=128（如 N1）"),
    # IBM Z
    Target("Z14", "s390x", 128, False, "IBM z14"),
    Target("Z15", "s390x", 128, False, "IBM z15 + vector packed decimal"),
    # LoongArch
    Target("LSX", "LoongArch", 128, False, "龙芯 LSX"),
    Target("LASX", "LoongArch", 256, False, "龙芯 LASX（256b）"),
    # POWER
    Target("PPC8", "POWER", 128, False, "PowerISA v2.07"),
    Target("PPC9", "POWER", 128, False, "PowerISA v3.0"),
    Target("PPC10", "POWER", 128, False, "PowerISA v3.1B（编译器 bug 待修）"),
    # RISC-V
    Target("RVV", "RISC-V", 128, True, "V 扩展 1.0，VLA（VLEN 128-1024+）"),
    # WASM
    Target("WASM", "WASM", 128, False, "固定 128b"),
    Target("WASM_EMU256", "WASM", 256, False, "2× unroll，需 HWY_WANT_WASM2"),
    # x86（按代际）
    Target("SSE2", "x86", 128, False, "~Pentium 4 (2001)"),
    Target("SSSE3", "x86", 128, False, "~Core (2006)"),
    Target("SSE4", "x86", 128, False, "~Nehalem (2008)，含 AES+CLMUL"),
    Target("AVX2", "x86", 256, False, "~Haswell (2013)，含 BMI2+F16+FMA"),
    Target("AVX3", "x86", 512, False, "~Skylake-X (2017)，AVX-512F/BW/CD/DQ/VL"),
    Target("AVX3_DL", "x86", 512, False, "~Icelake (2019)，+VBMI/VBMI2/VNNI/GFNI/VAES"),
    Target("AVX3_ZEN4", "x86", 512, False, "AVX3_DL + BF16，AMD Zen4 优化"),
    Target("AVX3_SPR", "x86", 512, False, "~Sapphire Rapids (2023)，+AVX-512FP16"),
    Target("AVX10_2", "x86", 256, False, "~Diamond Rapids (2024+)"),
]


# ============================================================================
# §1 SIMD lane 概念 + 5 种向量宽度对比
# ============================================================================

def demo_lane_concept():
    print(f"\n{SEP}\n§1 SIMD lane 概念：5 种典型向量宽度对比\n{SEP}")
    print("SIMD = Single Instruction, Multiple Data。一条指令同时对 N 个数据做同样运算。\n")

    # 5 种代表性 target
    reps = [
        ("SSE2", 128, "x86 老兵", 2001),
        ("AVX2", 256, "x86 主流（Haswell+）", 2013),
        ("AVX3", 512, "x86 AVX-512（Skylake-X+）", 2017),
        ("SVE", "VLA(128-2048)", "ARM 可变长", 2016),
        ("RVV", "VLA(128-1024+)", "RISC-V 可变长", 2021),
    ]
    print(f"{'target':<8} {'位宽':<18} {'float32 lane 数':<20} {'背景':<22} {'诞生'}")
    print("-" * 80)
    for name, bits, desc, year in reps:
        if isinstance(bits, int):
            lanes = bits // 32
            lanes_str = f"{lanes} lanes"
        else:
            lanes_str = "随硬件"
        print(f"{name:<8} {str(bits):<18} {lanes_str:<20} {desc:<22} {year}")

    print(f"\n{'▶ 反直觉发现 1':-^72}")
    print("一条 AVX-512 add 指令 = 16 个 float32 同时加。理论吞吐 = 16× 标量。")
    print("但 Agner FAQ Q6.3 实测：AVX-512 在早期 Skylake-X 会降频 3-4%。")
    print("JPEG XL 用 AVX-512 比 AVX2 快 1.4-1.6× —— 降频远小于吞吐提升。\n")

    # 用 numpy 模拟 lane 概念
    if not HAS_NUMPY:
        print("(numpy 未装，跳过 lane 加速模拟)")
        return

    print(f"{'▶ numpy 模拟 lane 加速（数 1M 个 float 的平方和）':-^72}")
    n = 1_000_000
    x = np.random.randn(n).astype(np.float32)

    # 标量
    t0 = time.perf_counter()
    s_scalar = 0.0
    for i in range(n):
        s_scalar += x[i] * x[i]
    t_scalar = time.perf_counter() - t0

    # numpy 向量化（内部用 SIMD，CPython 看不见）
    t0 = time.perf_counter()
    s_vec = float((x * x).sum())
    t_vec = time.perf_counter() - t0

    speedup = t_scalar / t_vec
    print(f"  标量循环  : {t_scalar*1000:8.2f} ms")
    print(f"  numpy 向量: {t_vec*1000:8.2f} ms   (内部用 SIMD，lane 数取决于 CPU)")
    print(f"  加速比    : {speedup:6.1f}×")
    print(f"  结果一致  : {abs(s_scalar - s_vec) < 1e-2 * abs(s_vec)}")
    print()
    print("注：numpy 内部用 LLVM 自动向量化，但行为对 Python 用户不透明。")
    print("    Highway 的卖点：在 C++ 里**显式**控制 lane 操作，跨 7 架构。")


# ============================================================================
# §2 AOS vs SOA 内存布局（Highway 推荐的 SOA 模式）
# ============================================================================

def demo_aos_vs_soa():
    print(f"\n{SEP}\n§2 AOS vs SOA 内存布局：Highway README 推荐的 SOA\n{SEP}")
    print("Highway README: 'the biggest gains are unlocked by designing algorithms")
    print("and data structures for scalable vectors. Helpful techniques include")
    print("batching, **structure-of-array layouts**, and aligned/padded allocations.'\n")

    if not HAS_NUMPY:
        print("(numpy 未装，跳过)")
        return

    # RGB 像素：AOS = [R,G,B, R,G,B, ...]；SOA = [R,R,R,..., G,G,G,..., B,B,B,...]
    n = 100_000  # 像素数

    print(f"场景：{n} 个 RGB 像素，每个 channel ×2.0\n")

    # AOS: shape (n, 3)
    aos = np.random.randint(0, 255, (n, 3)).astype(np.float32)

    # SOA: shape (3, n)
    soa = aos.T.copy()  # (3, n)，确保内存连续

    # AOS 处理：跨 stride 访问，对 SIMD 不友好
    t0 = time.perf_counter()
    aos_out = aos.copy()
    aos_out[:, 0] *= 2.0   # 必须分 3 次（每次跳着读）
    aos_out[:, 1] *= 2.0
    aos_out[:, 2] *= 2.0
    t_aos = time.perf_counter() - t0

    # SOA 处理：连续内存，SIMD lane 直接吃
    t0 = time.perf_counter()
    soa_out = soa.copy()
    soa_out *= 2.0          # 一次连续乘
    t_soa = time.perf_counter() - t0

    print(f"  AOS [(R,G,B), (R,G,B), ...]: {t_aos*1000:7.3f} ms")
    print(f"  SOA [R,R,...; G,G,...; B,B,..]: {t_soa*1000:7.3f} ms")
    print(f"  SOA 加速 : {t_aos/t_soa:.2f}×")
    print(f"  结果一致 : {np.allclose(aos_out, soa_out.T)}")
    print(f"  注：在 numpy 层 SOA 优势很小（甚至持平），因为 numpy 内部已优化")
    print(f"      stride 访问。在 C++ 手写 SIMD（Highway）层面，AOS 必须 gather，")
    print(f"      SOA 才能用普通 Load —— 这时差距可达 5-10×（FAQ Q6.5）。")

    # 内存布局可视化
    print(f"\n{'▶ 内存布局对比（前 3 个像素）':-^72}")
    print("AOS: [R0 G0 B0 R1 G1 B1 R2 G2 B2 ...]")
    print("      ↑ lane 0  ↑ lane 1  ↑ lane 2")
    print("      → AVX2 load 一次拿 8 个 float，但里面是 RGBRGBRGB 混杂")
    print("      → 要乘 R 必须 shuffle 分离 → 慢")
    print()
    print("SOA: [R0 R1 R2 ... Rn | G0 G1 ... Gn | B0 B1 ... Bn]")
    print("     ↑ lane 0..n 连续")
    print("     → AVX2 load 一次拿 8 个 R，直接 Mul(v, Set(d,2))，1 条指令")
    print()
    print("Highway 的 Set(d, k) + Mul 等价 SOA 上的 SIMD 友好代码。")
    print("AOS 上的等价代码需要 Gather/Shuffle，FAQ Q6.5：gather 1 lane/cycle，慢 8×。")


# ============================================================================
# §3 Highway 4 种 strip-mining 策略（README §5）
# ============================================================================

def demo_strip_mining_strategies():
    print(f"\n{SEP}\n§3 Strip-mining 4 种策略（Highway README §5）\n{SEP}")
    print("问题：循环 count=10，Lanes(d)=4，怎么处理尾巴 10 % 4 = 2 个元素？\n")

    count = 10
    N = 4  # 模拟 Lanes(d)
    arr = list(range(count))

    # 策略 1：Padding（输入要保证 pad 到 N 倍数）
    print(f"{'▶ 策略 1：Padding（推荐 ⭐⭐⭐）':-^72}")
    padded = arr + [0] * ((-count) % N)   # pad 到 12
    out1 = []
    for i in range(0, count, N):           # 只处理到 count（不处理 pad 段）
        out1.extend([padded[i + j] * 10 for j in range(N)][:count - i] if i + N > count
                    else [padded[i + j] * 10 for j in range(N)])
    print(f"  pad 到 {len(padded)}，处理前 {count} 个 → {out1}")
    print(f"  限制：写操作时 pad 段会被污染（不能 pad 写）\n")

    # 策略 2：重做最后一段（idempotent 操作）
    print(f"{'▶ 策略 2：重做最后一段（idempotent，如 max/min/xor）':-^72}")
    out2 = [0] * count
    for i in range(0, count, N):
        start = min(i, count - N)        # 最后一段回到 count-N
        for j in range(N):
            if start + j < count:
                out2[start + j] = arr[start + j] * 10
    print(f"  最后一段从 i={count-N} 重做，覆盖之前算的 → {out2}")
    print(f"  限制：必须 idempotent（重做不破坏结果），count >= N\n")

    # 策略 3：Transform 库（最省心）
    print(f"{'▶ 策略 3：Transform1 库（推荐 ⭐⭐⭐，C++14 lambda）':-^72}")
    def transform1(in_arr, op):
        out = []
        for x in in_arr:
            out.append(op(x))             # 库自动分块 + 处理尾巴
        return out
    out3 = transform1(arr, lambda x: x * 10)
    print(f"  Transform1(arr, lambda x: x*10) → {out3}")
    print(f"  优点：用户只写 lambda，库自动 strip-mine（见 hwy/contrib/algo/）\n")

    # 策略 4a：向量 + 标量尾巴
    print(f"{'▶ 策略 4a：向量主循环 + 标量尾巴':-^72}")
    out4a = [0] * count
    i = 0
    while i + N <= count:                  # 向量段
        for j in range(N):
            out4a[i + j] = arr[i + j] * 10
        i += N
    while i < count:                       # 标量尾巴
        out4a[i] = arr[i] * 10
        i += 1
    print(f"  向量段处理 i=0,4,8；标量段处理 i=8,9 → {out4a}\n")

    # 策略 4b：向量 + Mask 尾巴（推荐）
    print(f"{'▶ 策略 4b：向量主循环 + Mask 尾巴（推荐 ⭐⭐）':-^72}")
    out4b = [0] * count
    i = 0
    while i + N <= count:
        for j in range(N):
            out4b[i + j] = arr[i + j] * 10
        i += N
    if i < count:
        remaining = count - i
        mask = [True] * remaining + [False] * (N - remaining)  # FirstN(d, remaining)
        vec = [arr[i + j] if mask[j] else 0 for j in range(N)]
        vec = [v * 10 for v in vec]
        for j in range(N):
            if mask[j]:
                out4b[i + j] = vec[j]     # BlendedStore：只写 mask=true 的 lane
    print(f"  向量段同 4a；最后一段用 Mask=[T,T,F,F]（FirstN(d,2)）→ {out4b}")
    print(f"  限制：FAQ Q2.3，安全时要 #if !HWY_MEM_OPS_MIGHT_FAULT\n")

    # 一致性验证
    expected = [x * 10 for x in arr]
    print(f"{'▶ 一致性':-^72}")
    print(f"  expected       = {expected}")
    print(f"  1 padding      = {out1}  ✓" if out1 == expected else f"  1 padding = {out1}  ✗")
    print(f"  2 redo         = {out2}  ✓" if out2 == expected else f"  2 redo    = {out2}  ✗")
    print(f"  3 transform    = {out3}  ✓" if out3 == expected else f"  3 transf  = {out3}  ✗")
    print(f"  4a vec+scalar  = {out4a}  ✓" if out4a == expected else f"  4a        = {out4a}  ✗")
    print(f"  4b vec+mask    = {out4b}  ✓" if out4b == expected else f"  4b        = {out4b}  ✗")


# ============================================================================
# §4 静态 vs 动态分发（HWY_STATIC_DISPATCH vs HWY_DYNAMIC_DISPATCH）
# ============================================================================

def demo_static_vs_dynamic_dispatch():
    print(f"\n{SEP}\n§4 静态 vs 动态分发（Highway README §Quick Start）\n{SEP}")
    print("问题：同一份源码怎么生成 27 个 ISA 版本？运行时怎么选？\n")

    # 模拟：3 个假 ISA 编译版本
    @dataclass
    class CompiledVariant:
        target: str
        fn: Callable
        cycles_per_elem: float   # 模拟该 ISA 上的 cycle 成本

    # 模拟 SAXPY 在 3 个 ISA 上的"编译版本"
    def saxpy_sse2(k, src, add, dst):
        for i in range(len(src)):
            dst[i] = src[i] * k + add[i]
        return "SSE2 ran"

    def saxpy_avx2(k, src, add, dst):
        for i in range(len(src)):
            dst[i] = src[i] * k + add[i]
        return "AVX2 ran"

    def saxpy_avx3(k, src, add, dst):
        for i in range(len(src)):
            dst[i] = src[i] * k + add[i]
        return "AVX3 ran (AVX-512)"

    variants = {
        "SSE2": CompiledVariant("SSE2", saxpy_sse2, 1.00),
        "AVX2": CompiledVariant("AVX2", saxpy_avx2, 0.50),   # 2× lanes
        "AVX3": CompiledVariant("AVX3", saxpy_avx3, 0.25),   # 4× lanes
    }

    # 静态分发：编译期决定，只链一份
    print(f"{'▶ 静态分发 HWY_STATIC_DISPATCH':-^72}")
    print("编译时只生成 1 份（如 SSE2），开销 0，但只能跑那一种。")
    static_choice = "SSE2"   # 编译期 -msse2
    print(f"  HWY_STATIC_DISPATCH(Saxpy)(...) → 调用 {static_choice}")
    src = [1.0] * 4
    add = [0.5] * 4
    dst = [0.0] * 4
    result = variants[static_choice].fn(2.0, src, add, dst)
    print(f"  result: {result}, dst={dst}\n")

    # 动态分发：运行时 CPUID 检测，首次调用后查表
    print(f"{'▶ 动态分发 HWY_DYNAMIC_DISPATCH':-^72}")
    print("机制（README §Quick Start）：")
    print("  1. foreach_target.h 把 .cc 重复预处理 3 次，每次 namespace 改名")
    print("     （如 N_SSE2::Saxpy / N_AVX2::Saxpy / N_AVX3::Saxpy）")
    print("  2. HWY_EXPORT 生成函数指针表")
    print("  3. HWY_DYNAMIC_DISPATCH 首次调用时 CPUID 检测，之后查表\n")

    # 模拟 CPUID 检测
    @dataclass
    class CPU:
        name: str
        supported: List[str]   # 该 CPU 支持的 target（按优先级）

    cpus = [
        CPU("Pentium 4 (2001)", ["SSE2"]),
        CPU("Haswell (2013)",   ["SSE2", "AVX2"]),
        CPU("Skylake-X (2017)", ["SSE2", "AVX2", "AVX3"]),
    ]

    # 模拟"运行时分发"
    def dynamic_dispatch(cpu: CPU, variants: dict):
        # 模拟 hwy::SupportedTargets() 返回最优
        best = cpu.supported[-1]   # 最末是最优（编译期排序）
        return variants[best]

    print(f"  {'CPU':<22} {'支持的 target':<28} {'运行时选':<10} {'相对 cost'}")
    print("  " + "-" * 70)
    for cpu in cpus:
        chosen = dynamic_dispatch(cpu, variants)
        cost = chosen.cycles_per_elem
        rel = f"{cost:.2f}×"
        print(f"  {cpu.name:<22} {str(cpu.supported):<28} {chosen.target:<10} {rel}")

    print(f"\n{'▶ 反直觉发现 2':-^72}")
    print("同一份 Highway 源码 → 3 个 CPU 自动选不同 ISA → 性能 4× 差距。")
    print("这就是 README 说的 'Applications using Highway can run on heterogeneous")
    print("clouds or client devices, choosing the best available instruction set at runtime'。")
    print()
    print("首次 dispatch 开销：CPUID ~50 ns。之后查表 < 1 ns（Agner FAQ §1 也有同款机制）。")
    print("建议：程序启动时调一次 hwy::GetChosenTarget().Update(hwy::SupportedTargets()) 预热。")


# ============================================================================
# §5 标量 if vs Highway Mask/IfThenElse 谓词
# ============================================================================

def demo_mask_predication():
    print(f"\n{SEP}\n§5 标量 if vs Highway Mask/IfThenElse 谓词\n{SEP}")
    print("场景：if (x[i] > 0) y[i] = sqrt(x[i]); else y[i] = 0;\n")

    # 标量：分支
    print(f"{'▶ 标量版（每元素 if 分支）':-^72}")
    print("""
    for (int i = 0; i < n; ++i) {
        if (x[i] > 0) y[i] = sqrt(x[i]);   // 分支！
        else          y[i] = 0;
    }
    """)
    print("  问题：Agner Vol 1 §1.7 瓶颈 2 —— 分支难预测时，流水线冲刷 15-20 cycle/次。")
    print("  如果 x[i]>0 是 50% 随机，IPC 暴跌。\n")

    # Highway：Mask 谓词，无分支
    print(f"{'▶ Highway 版（无分支，AVX-512 / SVE 用专用 mask 寄存器）':-^72}")
    print("""
    const ScalableTag<float> d;
    const auto zero = Zero(d);
    for (size_t i = 0; i < n; i += Lanes(d)) {
        auto vx = LoadU(d, x + i);
        auto m  = Gt(vx, zero);              // Mask: 每 lane 1 bit
        auto vsqrt = Sqrt(vx);               // 全部 sqrt（被 mask 掉的不影响）
        Store(IfThenElse(m, vsqrt, zero), d, y + i);   // m ? sqrt : 0
    }
    """)
    print("  优势：0 分支，AVX-512 用 __mmask16（专用 mask 寄存器），其他架构零开销模拟。")
    print("  这是 design_philosophy.md §Masks 的核心：用 Mask<D> 抽象抹平 AVX-512 与其他的差异。\n")

    # 模拟两种方式的"分支数"
    if HAS_NUMPY:
        n = 100_000
        np.random.seed(42)
        x = np.random.randn(n).astype(np.float32)  # 50% 负

        # 标量版（Python 模拟）
        y_scalar = np.empty(n, dtype=np.float32)
        t0 = time.perf_counter()
        for i in range(n):
            if x[i] > 0:
                y_scalar[i] = math.sqrt(x[i])
            else:
                y_scalar[i] = 0.0
        t_scalar = time.perf_counter() - t0

        # Highway 风格（numpy 向量化，模拟 IfThenElse）
        t0 = time.perf_counter()
        vsqrt = np.sqrt(np.maximum(x, 0))    # 全 sqrt（mask 掉的不影响结果）
        y_vec = np.where(x > 0, vsqrt, 0).astype(np.float32)  # IfThenElse
        t_vec = time.perf_counter() - t0

        print(f"{'▶ numpy 实测（{n} 元素）':-^72}".format(n=n))
        print(f"  标量循环 (有分支)  : {t_scalar*1000:8.2f} ms")
        print(f"  numpy 向量 (无分支): {t_vec*1000:8.2f} ms   = 模拟 Highway IfThenElse")
        print(f"  加速比             : {t_scalar/t_vec:.1f}×")
        print(f"  结果一致           : {np.allclose(y_scalar, y_vec)}")
    print()
    print("注：CPython 标量循环慢主要因为解释器开销，不是分支预测。")
    print("    但 Highway 的无分支模式在 C++ 里也能赢——尤其分支难预测场景。")


# ============================================================================
# §6 Highway API 速查表（用 numpy 模拟 Tag/Vec/Mask 三件套）
# ============================================================================

def demo_highway_api_cheatsheet():
    print(f"\n{SEP}\n§6 Highway API 速查：用 numpy 模拟 Tag/Vec/Mask 三件套\n{SEP}")
    print("Highway design_philosophy.md：所有 API 围绕 Tag(D) / Vec(V) / Mask(M) 展开。\n")

    if not HAS_NUMPY:
        print("(numpy 未装，跳过)")
        return

    # === Tag（零大小，仅用于重载）===
    print("▶ Tag = 我要什么样的向量".center(72, "-"))
    print("Highway:    ScalableTag<float>()        # 当前 CPU 最宽 float 向量")
    print("            CappedTag<float, 4>()        # 最多 4 lane")
    print("            FixedTag<float, 4>()         # 恰好 4 lane")
    print("numpy 模拟: d = np.float32 + lanes 数\n")

    # === Vec（向量数据）===
    print("▶ Vec = 向量数据（用 numpy 4-lane 模拟）".center(72, "-"))
    LANES = 4   # 模拟 SSE2 / NEON 128b float
    print(f"模拟 Lanes(d) = {LANES}（4-lane float32 = 128-bit，如 SSE2/NEON）\n")

    # Set / Zero / LoadU / Store
    v_k   = np.full(LANES, 3.14, dtype=np.float32)   # Set(d, 3.14)
    v_z   = np.zeros(LANES, dtype=np.float32)         # Zero(d)
    src   = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    v_ld  = src.copy()                                # LoadU(d, src)

    print(f"  Set(d, 3.14)    = {v_k}       ← broadcast")
    print(f"  Zero(d)         = {v_z}       ← 全 0")
    print(f"  src             = {src}")
    print(f"  LoadU(d, src)   = {v_ld}       ← unaligned load\n")

    # Add / Sub / Mul / MulAdd（FMA）
    v_a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    v_b = np.array([10., 20., 30., 40.], dtype=np.float32)
    v_add = v_a + v_b                                  # Add(v_a, v_b)
    v_mul = v_a * v_b                                  # Mul(v_a, v_b)
    v_fma = v_a * v_k + v_b                            # MulAdd(v_a, v_k, v_b) = FMA

    print(f"  v_a = {v_a}")
    print(f"  v_b = {v_b}")
    print(f"  Add(v_a, v_b)      = {v_add}        ← 逐 lane 加")
    print(f"  Mul(v_a, v_b)      = {v_mul}       ← 逐 lane 乘")
    print(f"  MulAdd(v_a, v_k, v_b) = {v_fma}   ← FMA: v_a * v_k + v_b")
    print("    注：MulAdd 在 SSE4/NEON 展开 2 指令；AVX2/AVX-512/SVE 是单 FMA")
    print()

    # === Mask（谓词）===
    print("▶ Mask = 谓词（比较结果，用于 IfThenElse）".center(72, "-"))
    m = v_a > 2.0                                      # Gt(v_a, Set(d,2)) → Mask
    v_then = np.array([100., 200., 300., 400.], dtype=np.float32)
    v_else = np.array([1., 2., 3., 4.], dtype=np.float32)
    v_result = np.where(m, v_then, v_else)             # IfThenElse(m, v_then, v_else)

    print(f"  v_a            = {v_a}")
    print(f"  Gt(v_a, 2.0)→m = {m}        ← 每 lane 1 bit (AVX-512 用 __mmask)")
    print(f"  v_then         = {v_then}")
    print(f"  v_else         = {v_else}")
    print(f"  IfThenElse(m, v_then, v_else) = {v_result}")
    print()

    # Mask 聚合
    print(f"{'▶ Mask 聚合':-^72}")
    cnt_true = int(np.sum(m))                           # CountTrue(d, m)
    all_true = bool(np.all(m))                          # AllTrue(d, m)
    any_true = bool(np.any(m))                          # AnyTrue(d, m)（实际 Highway 1.0+ 有）
    print(f"  CountTrue(d, m) = {cnt_true}")
    print(f"  AllTrue(d, m)   = {all_true}")
    print(f"  AnyTrue(d, m)   = {any_true}")
    print()

    # Reduction
    print(f"{'▶ Reduction（跨 lane 求和/最值）':-^72}")
    s = float(np.sum(v_a))                              # ReduceSum(d, v_a)
    mn = float(np.min(v_a))                             # MinOfLanes(d, v_a)
    mx = float(np.max(v_a))                             # MaxOfLanes(d, v_a)
    print(f"  v_a                 = {v_a}")
    print(f"  ReduceSum(d, v_a)   = {s}")
    print(f"  MinOfLanes(d, v_a)  = {mn}")
    print(f"  MaxOfLanes(d, v_a)  = {mx}")
    print()
    print("注：Highway 用 SumOfLanes 返回**仍是 vector**（所有 lane 都填 reduce 结果），")
    print("    便于继续 SIMD 运算。取标量用 GetLane(v[0])。")


# ============================================================================
# §7 SAXPY 三种写法（标量 / Highway 风格 / numpy）
# ============================================================================

def demo_saxpy_three_ways():
    print(f"\n{SEP}\n§7 SAXPY 三种写法：BLAS 一级基础（README §Quick Start）\n{SEP}")
    print("SAXPY: dst[i] = alpha * src[i] + add[i]，BLAS 一级最常用操作。\n")

    if not HAS_NUMPY:
        print("(numpy 未装，跳过)")
        return

    n = 1_000_000
    alpha = 2.5
    src = np.random.randn(n).astype(np.float32)
    add = np.random.randn(n).astype(np.float32)

    # ① 标量
    print(f"{'▶ ① 标量版（naive for）':-^72}")
    dst_scalar = np.empty(n, dtype=np.float32)
    t0 = time.perf_counter()
    for i in range(n):
        dst_scalar[i] = alpha * src[i] + add[i]
    t_scalar = time.perf_counter() - t0
    print(f"    {t_scalar*1000:8.2f} ms")

    # ② Highway 风格（用 numpy 模拟 Highway 的 SIMD 模式）
    print(f"\n{'▶ ② Highway 风格（SIMD 化，模拟 MulAdd）':-^72}")
    print("""    Highway C++ 源码（README §Quick Start）:
        const ScalableTag<float> d;
        const auto vk = Set(d, alpha);
        for (size_t i = 0; i < n; i += Lanes(d)) {
            Store(MulAdd(LoadU(d, src+i), vk, LoadU(d, add+i)), d, dst+i);
        }
    """)
    dst_hwy = np.empty(n, dtype=np.float32)
    # 模拟"chunk by chunk"的 SIMD 风格（实际 numpy 不会这么写，我们模仿 lane-by-lane）
    # 这里用大 chunk（4096）模拟一次 SIMD 指令处理的"概念 lane 数"
    LANE = 4096
    t0 = time.perf_counter()
    for i in range(0, n, LANE):
        end = min(i + LANE, n)
        v_src = src[i:end]                              # LoadU
        v_add = add[i:end]                              # LoadU
        v_dst = v_src * alpha + v_add                   # MulAdd
        dst_hwy[i:end] = v_dst                          # Store
    t_hwy = time.perf_counter() - t0
    print(f"    {t_hwy*1000:8.2f} ms   (chunk={LANE}，模拟 SIMD lane 处理)")
    print(f"    数值一致: {np.allclose(dst_scalar, dst_hwy, rtol=1e-5)}")

    # ③ numpy 完全向量化（最简写法）
    print(f"\n{'▶ ③ numpy 完全向量化（一行）':-^72}")
    t0 = time.perf_counter()
    dst_np = alpha * src + add
    t_np = time.perf_counter() - t0
    print(f"    {t_np*1000:8.2f} ms   ← alpha * src + add")
    print(f"    数值一致: {np.allclose(dst_scalar, dst_np, rtol=1e-5)}")

    # 总结
    print(f"\n{'▶ 三种方式对比':-^72}")
    print(f"  {'方式':<28} {'耗时(ms)':<12} {'相对'}")
    print(f"  {'-'*50}")
    print(f"  {'① 标量 for':<28} {t_scalar*1000:<12.2f} {'1.0× (baseline)'}")
    print(f"  {'② Highway chunk':<28} {t_hwy*1000:<12.2f} {t_scalar/t_hwy:.1f}× 加速")
    print(f"  {'③ numpy 完全向量':<28} {t_np*1000:<12.2f} {t_scalar/t_np:.1f}× 加速")
    print()
    print(f"{'▶ 反直觉发现 3':-^72}")
    print("在 Python 里 numpy 内部用 SIMD（LLVM 自动向量化 + 手写 kernel），所以 ③ 最快。")
    print("但 numpy 把 SIMD 藏起来——你**看不到** lane 数、不能精确控制 ISA、不能运行时 dispatch。")
    print()
    print("Highway 在 C++ 里的价值：")
    print("  ✓ 同一份源码，AVX2 上 Lanes=8 / AVX-512 上 Lanes=16 / SVE 上 Lanes=VLEN/32")
    print("  ✓ MulAdd 在有 FMA 的 ISA 上是单指令（rounding 一次），无 FMA 的 ISA 自动展开")
    print("  ✓ 运行时自动选最优 ISA（动态分发），同一 binary 跑遍 heterogeneous 云")
    print("  ✓ 27 target 全 CI 测，跨架构行为可预测")
    print()
    print("这就是 README 说的 'Highway makes SIMD/vector programming practical and workable'。")


# ============================================================================
# main
# ============================================================================

DEMOS = {
    1: ("lane 概念 + 5 种向量宽度", demo_lane_concept),
    2: ("AOS vs SOA 内存布局",      demo_aos_vs_soa),
    3: ("Strip-mining 4 种策略",    demo_strip_mining_strategies),
    4: ("静态 vs 动态分发",         demo_static_vs_dynamic_dispatch),
    5: ("Mask 谓词 vs 标量 if",    demo_mask_predication),
    6: ("Highway API 速查",         demo_highway_api_cheatsheet),
    7: ("SAXPY 三种写法",           demo_saxpy_three_ways),
}


def main():
    print("=" * 72)
    print("Google Highway SIMD 库 · 7 个思想 demo".center(72))
    print("配套: top-cs-projects/HIGHWAY_SIMD_LIBRARY.md".center(72))
    print("=" * 72)
    print(f"numpy 可用: {HAS_NUMPY}   (numpy 让 demo 更直观，但非必须)")
    print(f"Highway 全部 target 列表（README §Current status 标题数 27）:")
    arch_count = {}
    for t in HIGHWAY_TARGETS:
        arch_count[t.arch] = arch_count.get(t.arch, 0) + 1
    print(f"  架构数: {len(arch_count)}  ({dict(arch_count)})")
    print(f"  本表展开 {len(HIGHWAY_TARGETS)} 条（README 标题数 27，因 SVE_256/SVE2_128 视为 SVE 变体）")
    print()

    args = sys.argv[1:]
    if args:
        try:
            nums = [int(a) for a in args]
        except ValueError:
            print(f"用法: python3 {sys.argv[0]} [1-7 ...]")
            return
        for n in nums:
            if n in DEMOS:
                DEMOS[n][1]()
            else:
                print(f"⚠️  未知 demo 编号: {n}（有效范围 1-7）")
    else:
        for n, (name, fn) in DEMOS.items():
            fn()

    print(f"\n{'='*72}")
    print("✓ 全部 demo 完成".center(72))
    print("=" * 72)
    print("\n📌 下一步:")
    print("  1. 读 ../../top-cs-projects/HIGHWAY_SIMD_LIBRARY.md 第三旗舰笔记")
    print("  2. 打开 https://gcc.godbolt.org/z/rGnjMevKG 看 Highway 真实汇编")
    print("  3. clone https://github.com/google/highway 跑 hwy/examples/skeleton.cc")
    print("  4. 读 g3doc/quick_reference.md（1 小时过完所有 op）")


if __name__ == "__main__":
    main()
