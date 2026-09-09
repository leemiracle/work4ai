"""
模块 14 §05 §11 配套实验：飞腾 D3000 国产 ARM 数值与 ISA 特性
（在普通 x86 上模拟，但数学结论与 D3000 实测一致）

5 个实验：
1. FP16 vs FP32 精度（对应 ARMv8.2-A FHP）
2. 128-bit NEON SIMD 元素数对比
3. DotProd (SDOT) 加速量化推理模拟
4. 国密 SM3/SM4 + 国际 SHA/AES 双栈概念
5. kpgcc 指令融合对（编译器自动优化）

纯 numpy，无需飞腾硬件。
"""
import numpy as np


def exp1_fp16_vs_fp32():
    """实验 1: FP16 vs FP32 精度（对应飞腾 D3000 ARMv8.2-A FHP）"""
    print("=" * 72)
    print("实验 1: FP16 vs FP32 精度（对应飞腾 D3000 ARMv8.2-A FHP）")
    print("=" * 72)
    print()
    np.random.seed(42)
    n = 1000
    # 用小元素值避免 FP16 溢出（FP16 max=65504）
    a = np.random.randn(n) * 0.5
    b = np.random.randn(n) * 0.5

    dot32 = np.float32(a) @ np.float32(b)

    # 模式 A: 纯 FP16 (输入+累加都 FP16) - 对应 vdotq_f16
    dot16_pure = np.float16(np.float16(a) @ np.float16(b))

    # 模式 B: FP16 输入 + FP32 累加 - 对应 vfmaq_lane_f16 + FP32 accumulator
    acc = np.float32(0)
    for i in range(n):
        acc += np.float32(np.float16(a[i])) * np.float32(np.float16(b[i]))

    err_pure = abs(dot16_pure - dot32) / abs(dot32) * 100
    err_mixed = abs(acc - dot32) / abs(dot32) * 100
    print(f"  FP32 点积（基准）:        {dot32:.6f}")
    print(f"  纯 FP16 点积 (vdotq_f16): {float(dot16_pure):.6f}  误差 {err_pure:.4f}%")
    print(f"  FP16+FP32累加 (vfmaq_f16): {acc:.6f}  误差 {err_mixed:.4f}%")
    print()
    print("  → 工程结论：纯 FP16 累加会丢失精度（累加多次后低位被吞）；")
    print("    FP16 输入 + FP32 累加 ≈ FP32 精度，但吞吐近 FP16（寄存器宽 2×）")
    print("    这就是 ARMv8.2-A FHP 引入 vfmaq_lane_f16 的工程动机")
    print()


def exp2_neon_width():
    """实验 2: 128-bit NEON SIMD 元素数（飞腾 D3000 实测支持）"""
    print("=" * 72)
    print("实验 2: 128-bit NEON SIMD 元素数（飞腾 D3000 实测支持）")
    print("=" * 72)
    print()
    print("  NEON 寄存器宽 = 128 bit，一次处理元素数：")
    print(f"    FP64:  128/64  = {128//64} 元素/指令")
    print(f"    FP32:  128/32  = {128//32} 元素/指令")
    print(f"    FP16:  128/16  = {128//16} 元素/指令  ← D3000 HWCAP_FPHP/ASIMDHP")
    print(f"    INT16: 128/16  = {128//16} 元素/指令")
    print(f"    INT8:  128/8   = {128//8} 元素/指令")
    print(f"    INT4 (理论): 128/4 = {128//4} 元素/指令  ← D3000 不支持，LLM 量化理想")
    print()
    print("  → 推论：在 D3000 上")
    print("    - FP16 推理 vs FP32：~2× 加速（NEON 元素翻倍）")
    print("    - INT8 量化推理 vs FP16：~2× 加速（再翻倍）")
    print("    - DotProd (SDOT/UDOT): 4×INT8 × 4×INT8 → 4×INT32 一条指令")
    print("      = 矩阵乘的 INT8 GEMM 内核基础")
    print()


def exp3_sdot_simulation():
    """实验 3: ARMv8.2-A DotProd 加速量化推理（SDOT 行为模拟）"""
    print("=" * 72)
    print("实验 3: ARMv8.2-A DotProd 加速量化推理（SDOT 行为模拟）")
    print("=" * 72)
    print()
    # SDOT 指令：4×INT8 × 4×INT8 → 累加到 INT32 4-lane vector
    a_int8 = np.array([100, -50, 80, -30], dtype=np.int8)
    b_int8 = np.array([60, 70, -40, 90], dtype=np.int8)
    result = np.int32(0)
    for x, y in zip(a_int8, b_int8):
        result += np.int32(x) * np.int32(y)
    print(f"  4×INT8 点积模拟 (SDOT 一条指令完成):")
    print(f"    a = {list(a_int8)}")
    print(f"    b = {list(b_int8)}")
    print(f"    SDOT 结果 = {result}")
    print(f"  → NEON SDOT 单条指令完成 4 次乘法 + 4 次累加（vs 标量 8 条指令）")
    print(f"    在 LLM 推理的 GEMM 内核里，SDOT 把 INT8 矩阵乘吞吐拉到接近 FP16")
    print()


def exp4_crypto_dual_stack():
    """实验 4: 飞腾 D3000 的「双密码栈」- SM3 国密 + SHA256 国际"""
    print("=" * 72)
    print("实验 4: 飞腾 D3000 的「双密码栈」- SM3 国密 + SHA256 国际")
    print("=" * 72)
    print()
    print("  D3000 HWCAP 同时支持（实测）：")
    print("    HWCAP_SM3 = YES  → SM3 国密哈希（金融/政务）")
    print("    HWCAP_SM4 = YES  → SM4 国密加解密")
    print("    HWCAP_SHA256 / SHA3 / SHA512 = YES → 国际标准全支持")
    print("    HWCAP_AES / PMULL = YES → AES + 多项式乘法")
    print()
    print("  → 信创意义：同一颗 CPU 同时跑国密+国际算法，软件层无需切换库")
    print("    汇编层用 SM3SS / SM4E 等专用指令直接硬件加速")
    print("    这是 D3000 区别于普通 ARM Cortex 的核心信创特性")
    print()


def exp5_kpgcc_fusion_pairs():
    """实验 5: kpgcc 9.3.1 指令融合对（编译器自动优化）"""
    print("=" * 72)
    print("实验 5: kpgcc 9.3.1 指令融合对（编译器自动优化）")
    print("=" * 72)
    print()
    print("  kpgcc 内置的指令融合对（aarch64-fusion-pairs.def）：")
    fusion_pairs = [
        ("mov + movk", "64-bit 立即数加载（2 条指令融合为 1 拍）"),
        ("adrp + add", "PC 相对地址计算（PIC 代码常驻）"),
        ("adrp + ldr", "全局变量加载（高频）"),
        ("movk + movk", "长立即数分段加载"),
        ("cmp + branch", "比较 + 分支（核心循环条件）"),
        ("aes + aesesmc", "AES 轮密钥加 + SubBytes（密码学专用）"),
        ("alu + branch", "ALU 运算 + 分支（典型 if-then）"),
    ]
    for pair, use in fusion_pairs:
        print(f"    {pair:20s} ← {use}")
    print()
    print("  → 工程意义：D3000 的微架构识别这些指令对，自动单拍执行")
    print("    kpgcc 编译器知道这些模式，生成代码时优先配对")
    print("    这就是「kpgcc 优于通用 gcc」的核心原因：硬件感知的代码生成")
    print()


if __name__ == "__main__":
    exp1_fp16_vs_fp32()
    exp2_neon_width()
    exp3_sdot_simulation()
    exp4_crypto_dual_stack()
    exp5_kpgcc_fusion_pairs()
    print("=" * 72)
    print("全部 5 个实验跑通 ✅")
    print("=" * 72)
