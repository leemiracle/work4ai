# -*- coding: utf-8 -*-
"""适定性数值实拍：热方程正向（适定）vs 反向（Hadamard 不适定）。

03 章 · 可构造与结构 配套实验。纯标准库。

u_t = α u_xx，初值 = 平滑基线 + 高频小扰动（10⁻⁶ 量级）
放大因子（模式 k，显式格式）：G = 1 − 4r·sin²(kΔx/2)，r = α·dt/dx²
  正向（r>0 且满足稳定性条件）：|G|<1 —— 衰减
  反向（r<0）：G = 1 + |…|>1 —— 指数放大

跑法: python3 -u experiments/03_wellposedness.py
"""
import math

N = 64
ALPHA = 1.0
DX = 1.0 / (N - 1)
BASE_K = 5      # 基线波形模式数（低频）
PERT_K = 31     # 扰动模式数（高频）
PERT_AMP = 1e-6


def init(mode_base, mode_pert):
    return [math.sin(mode_base * math.pi * i * DX)
            + PERT_AMP * math.sin(mode_pert * math.pi * i * DX)
            for i in range(N)]


def step(u, r):
    """显式欧拉一步。r = ALPHA*dt/dx²，反向传 r<0。Dirichlet 边界 u=0。"""
    return [0.0] + [u[i] + r * (u[i + 1] - 2 * u[i] + u[i - 1]) for i in range(1, N - 1)] + [0.0]


def amplification(r, mode):
    """理论放大因子 per step。"""
    return 1 - 4 * r * math.sin(mode * math.pi * DX / 2) ** 2


def track(u0, r, nsteps):
    """走 nsteps 步，返回每步的高频扰动包络（用第 PERT_K 个网格点的 |u| 与最大|u|）。"""
    u = u0
    peak = [max(abs(x) for x in u)]
    for _ in range(nsteps):
        u = step(u, r)
        peak.append(max(abs(x) for x in u))
        if peak[-1] > 1e30:
            break
    return peak


def main():
    # 稳定性条件：r <= 0.5（正向显式格式）
    r_fwd = 0.45
    r_bwd = -0.45          # 反向 = r 取负（相当于 dt<0）
    NSTEPS = 200

    print("=" * 62)
    print("适定性数值实拍：u_t = u_xx，初值 = 基线 sin(5πx) + 10⁻⁶·sin(31πx)")
    print("=" * 62)
    print(f"网格 N={N}，理论放大因子/步（高频模式 {PERT_K}）：")
    gF = amplification(r_fwd, PERT_K)
    gB = amplification(r_bwd, PERT_K)
    print(f"  正向 r=+{r_fwd}: |G| = {abs(gF):.4f}   （衰减）")
    print(f"  反向 r={r_bwd}:   |G| = {abs(gB):.4f}   （每步放大 {abs(gB):.2f} 倍）")
    print(f"  反向 200 步理论放大倍数: {abs(gB)**NSTEPS:.3e}")
    print()

    u0 = init(BASE_K, PERT_K)
    # 方程线性 ⟹ 扰动独立演化：单轨跟踪扰动（不含基线，数字诚实）
    def unit_pert(mode):
        return [math.sin(mode * math.pi * i * DX) for i in range(N)]

    print("正向演化（适定）：高频扰动被磨光")
    pF = track(unit_pert(PERT_K), r_fwd, NSTEPS)
    print(f"  扰动包络: 起始 1.0 → 200 步后 {pF[-1]:.2e}"
          f"（×10⁻⁶ 后 ≈ {PERT_AMP * pF[-1]:.1e}——彻底磨光）")
    print(f"  基线模式 {BASE_K} 同步衰减但慢得多（低频先留）——热方程是磨光机 ✓")
    print()

    print("反向演化（Hadamard 不适定）：10⁻⁶ 的扰动吃掉全场")
    pB = track(unit_pert(PERT_K), r_bwd, NSTEPS)
    blow = next((i for i, v in enumerate(pB) if PERT_AMP * v > 1.0), None)
    for i in (20, 40, 60, 80):
        if i < len(pB):
            print(f"  第 {i:>3} 步: 扰动包络 {pB[i]:.3e}（×10⁻⁶ = {PERT_AMP * pB[i]:.3e}）")
    print(f"  → 10⁻⁶ 扰动在第 {blow} 步放大到 O(1)——数据不连续依赖，第三要件阵亡 ✗")
    print()

    print("频率依赖（病是频率依赖的）：低频扰动反向放大慢得多")
    pL = track(unit_pert(7), r_bwd, NSTEPS)
    gLow = amplification(r_bwd, 7)
    print(f"  低频模式 7 的 |G| = {abs(gLow):.4f}（vs 高频 {abs(gB):.4f}）")
    print(f"  200 步放大倍数: 低频 {abs(gLow)**NSTEPS:.2e} vs 高频 {abs(gB)**NSTEPS:.2e}")
    print(f"  低频扰动 ×10⁻⁶ × 放大 = {PERT_AMP * abs(gLow)**NSTEPS:.1e}（仍小）"
          f"；高频早已 O(1)")
    print("  → 不适定 = 存在放大无界的模式；频率越高病得越重 💡")
    print()
    print("工程结论：不适定问题没有好算法，只有改问题（正则化/先验/平均化）。")
    print("          '难题'与'病题'的分界线，是应用数学最贵的判断之一。")


if __name__ == "__main__":
    main()
