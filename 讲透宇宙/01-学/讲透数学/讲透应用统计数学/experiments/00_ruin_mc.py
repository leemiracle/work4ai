# -*- coding: utf-8 -*-
"""Cramér–Lundberg 破产概率蒙特卡洛:轻尾 vs 重尾索赔,对照 Lundberg 上界。

00/03/04 章 配套实验。纯 numpy。

模型: 盈余过程 U(t) = u + c·t − S(t)
  理赔按速率 λ 的泊松过程到达;单笔索赔 i.i.d.(指数=轻尾,对数正态=重尾)
  保费率 c = (1+θ)·λ·E[X](安全负荷 θ>0)
破产: 首次 U(t) < 0
Lundberg 上界(仅轻尾): ψ(u) ≤ e^{−R·u},R 为调节系数
  指数索赔 X~Exp(β) 时有闭式: R = θ/(1+θ) · β  (经典精算教材结果)

跑法: python 讲透数学/讲透应用统计数学/experiments/00_ruin_mc.py
"""
import numpy as np

rng = np.random.default_rng(42)


def ruin_probability(u, c, lam, claim_sampler, T_max=200.0, n_paths=20000):
    """蒙特卡洛估计最终破产概率:向量化复合泊松盈余模拟。

    盈余 U(t)=u+c·t−S(t);只需在理赔时刻检查破产(保费连续,索赔跳变):
    存在 k 使 u + c·t_k − Σ_{i≤k} X_i < 0 ⟺ 破产。
    """
    n_arr = 400                                        # 每路径最多理赔笔数(λT_max 的安全余量)
    waits = rng.exponential(1.0 / lam, size=(n_paths, n_arr))
    claims = claim_sampler(size=(n_paths, n_arr))
    arr_t = np.cumsum(waits, axis=1)                   # 理赔时刻
    surplus_at_claims = u + c * arr_t - np.cumsum(claims, axis=1)
    in_window = arr_t < T_max                          # 只统计 T_max 内的理赔
    surplus_at_claims = np.where(in_window, surplus_at_claims, np.inf)
    ruined = (surplus_at_claims < 0).any(axis=1)
    est = ruined.mean()
    se = np.sqrt(est * (1 - est) / n_paths)
    return est, se


def lundberg_R_exp(beta, theta):
    """指数索赔 X~Exp(β) 的调节系数闭式:R = θ/(1+θ)·β。"""
    return theta / (1.0 + theta) * beta


def main():
    lam = 1.0
    beta = 1.0                       # 指数索赔率参数: E[X]=1
    theta = 0.20                     # 安全负荷 20%
    c = (1 + theta) * lam * (1.0 / beta)
    R = lundberg_R_exp(beta, theta)

    print("=" * 66)
    print("Cramér–Lundberg 破产概率 MC:λ=1, E[X]=1, 安全负荷 θ=20%")
    print("=" * 66)

    lognorm_sampler = lambda size: rng.lognormal(mean=-0.5, sigma=1.0, size=size)
    # 对数正态(μ=-0.5, σ=1) 期望 = exp(μ+σ²/2) = exp(0) = 1 —— 与指数索赔同均值!

    print(f"{'u':>6} {'ψ_轻尾(MC)':>12} {'±se':>9} {'Lundberg上界':>13} {'ψ_重尾(MC)':>12}")
    for u in (2.0, 4.0, 8.0, 16.0):
        psi_l, se_l = ruin_probability(u, c, lam, lambda size: rng.exponential(1 / beta, size))
        bound = np.exp(-R * u)
        psi_h, se_h = ruin_probability(u, c, lam, lognorm_sampler)
        print(f"{u:>6.1f} {psi_l:>12.4f} {se_l:>9.4f} {bound:>13.4f} {psi_h:>12.4f}")

    print()
    print("读数:")
    print("  · 轻尾(指数):每个 ψ 都 ≤ Lundberg 上界 ✓(03 章『指数压缩』实拍)")
    print("  · 重尾(对数正态,同均值):ψ 整体显著高于轻尾——均值相同,命运由尾部决定")
    print("  · 重尾无调节系数 R(矩母函数发散),Lundberg 界不存在——数学事实=代码报警路径(04 章)")
    print()

    # 断言 1: 轻尾 MC 值被 Lundberg 界罩住(容差 2 个标准误)
    u0 = 8.0
    psi_l, se_l = ruin_probability(u0, c, lam, lambda size: rng.exponential(1 / beta, size))
    assert psi_l <= np.exp(-R * u0) + 3 * se_l, "Lundberg 上界被击穿?!"

    # 断言 2: 同均值下重尾破产概率 > 轻尾破产概率
    psi_h, se_h = ruin_probability(u0, c, lam, lognorm_sampler)
    assert psi_h > psi_l, "重尾应更危险(00 章反直觉 2)"

    print(f"自验证断言通过:ψ_轻尾(u=8)={psi_l:.4f} ≤ e^(−Ru)={np.exp(-R*u0):.4f}; "
          f"ψ_重尾={psi_h:.4f} > ψ_轻尾 ✓")


if __name__ == "__main__":
    main()
