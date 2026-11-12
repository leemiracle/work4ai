#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
09_scaling_collapse.py — 模拟 supercollapse: 不同大小模型的loss曲线归一化后坍缩
讲透模型宇宙 / Ch09 实验
纯标准库, 几秒跑完。
复现 Qiu et al. 2025 (ICML, Scaling Collapse) 的核心定性现象。
"""
import math

def loss_curve(N_params, n_points=20):
    """模拟一个参数量=N 的模型的 loss 曲线 (power law + 末段衰减)
    返回 (相对compute序列, loss序列)"""
    alpha = 0.07 + 0.01 * (N_params % 3)   # 不同模型略不同的指数
    A = 2.5 + 0.3 * (N_params % 5)
    L_inf = 1.8
    total_C = 10.0 * (N_params / 1.0)       # 总算力 (归一化前)
    losses = []
    comps = []
    for i in range(1, n_points + 1):
        c = total_C * (i / n_points)        # 当前 compute
        L = A * (c ** (-alpha)) + L_inf
        losses.append(L)
        comps.append(c)
    return comps, losses

def normalize(comps, losses):
    """归一化: compute 除以总 compute, loss 除以最终 loss (supercollapse)"""
    C_total = comps[-1]
    L_final = losses[-1]
    return [c / C_total for c in comps], [L / L_final for L in losses]

def variance_at(losses_list, frac, n_points=20):
    """在 frac 处, 各 loss 序列的方差"""
    idx = int(frac * (n_points - 1))
    vals = [L[idx] for L in losses_list]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return mean, var

def main():
    print("=" * 68)
    print("Supercollapse: 不同大小模型 loss 曲线归一化后坍缩成一条")
    print("=" * 68)

    model_sizes = [1, 7, 13, 70, 175]   # 模拟 1B~175B
    n_points = 20
    raw_curves = []
    norm_curves = []
    print(f"\n模拟 {len(model_sizes)} 个模型 (1B~175B), 各训练 {n_points} 个checkpoint:")
    for N in model_sizes:
        c, l = loss_curve(N, n_points)
        raw_curves.append((N, c, l))
        cn, ln = normalize(c, l)
        norm_curves.append((N, cn, ln))

    # 原始曲线: 在 50% compute 处各模型的 loss
    print(f"\n【原始 loss】(在各自 50% compute 处):")
    for N, c, l in raw_curves:
        print(f"  {N:>3}B 模型: loss = {l[n_points//2]:.3f}  (最终 {l[-1]:.3f})")
    mid_raw_mean, mid_raw_var = variance_at([l for _,_,l in raw_curves], 0.5)
    print(f"  -> 各模型原始 loss 差异大 (方差 {mid_raw_var:.4f})")

    # 归一化曲线
    print(f"\n【归一化 loss】(除以各自最终loss, compute除以总算力):")
    print(f"  {'模型':>6} | " + " ".join(f"{i/n_points*100:>5.0f}%" for i in range(2, n_points, 3)))
    for N, cn, ln in norm_curves:
        row = " ".join(f"{ln[i]:>5.2f}" for i in range(2, n_points, 3))
        print(f"  {N:>4}B | {row}")
    mid_norm_mean, mid_norm_var = variance_at([ln for _,_,ln in norm_curves], 0.5)

    print("\n" + "=" * 68)
    print(">>> 反直觉发现: Supercollapse <<<")
    print(f"  归一化前: 各模型在 50% compute 处 loss 方差 = {mid_raw_var:.4f} (分散)")
    print(f"  归一化后: 各模型在 50% compute 处 loss 方差 = {mid_norm_var:.4f} (坍缩)")
    ratio = mid_raw_var / (mid_norm_var + 1e-9)
    print(f"  方差缩小约 {ratio:.0f} 倍")
    print(f"  => 完全不同大小的模型, 归一化后训练动力学形状几乎一致。")
    print(f"  => 规模只是'幅度', '形状'是普适的 (Qiu et al. 2025 ICML)。")
    print(f"  这是深度学习罕见的'普适律', 类比物理学不同物质的相变标度函数。")
    print("=" * 68)

if __name__ == "__main__":
    main()
