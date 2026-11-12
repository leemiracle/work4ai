"""
讲透代数拓扑 00 章实验：拓扑等价 + 洞 + Euler 示性数。
跑法：python3 -u experiments/00_topology.py
"""
import numpy as np


def part1_genus_and_chi():
    print("=" * 65)
    print("[1] 曲面亏格 g 与 Euler 示性数 χ = 2 - 2g")
    print("=" * 65)
    print(f"  {'g':<4} {'曲面':<14} {'χ'}")
    for g in [0, 1, 2, 3]:
        chi = 2 - 2*g
        name = {0: "球面 S²", 1: "甜甜圈 T²", 2: "双甜甜圈", 3: "三甜甜圈"}[g]
        print(f"  {g:<4} {name:<14} {chi}")


def part2_homology():
    print()
    print("=" * 65)
    print("[2] 同调群 H_n（'洞'的代数）")
    print("=" * 65)
    print(f"  {'空间':<14} {'H_0':<6} {'H_1':<14} {'H_2':<6}")
    spaces = [
        ("点",        "Z",   "0",     "0"),
        ("圆 S¹",     "Z",   "Z",     "0"),
        ("球面 S²",   "Z",   "0",     "Z"),
        ("球面 S³",   "Z",   "0",     "0"),
        ("甜甜圈 T²", "Z",   "Z⊕Z",   "Z"),
        ("Klein 瓶",  "Z",   "Z⊕Z/2", "0"),
        ("RP²",       "Z",   "Z/2",   "0"),
    ]
    for name, h0, h1, h2 in spaces:
        print(f"  {name:<14} {h0:<6} {h1:<14} {h2:<6}")
    print("  → H_0 = 连通分量数（Z = 1 个）")
    print("  → H_1 = 1 维洞（环路数）")
    print("  → H_2 = 2 维洞（空腔数）")


def part3_euler_characteristic_polyhedra():
    """凸多面体 V-E+F = 2（Euler 定理）"""
    print()
    print("=" * 65)
    print("[3] Euler 示性数：凸多面体 V - E + F = 2")
    print("=" * 65)
    print(f"  {'多面体':<10} {'V':<4} {'E':<4} {'F':<4} {'χ=V-E+F'}")
    polyhedra = [
        ("四面体", 4, 6, 4),
        ("立方体", 8, 12, 6),
        ("八面体", 6, 12, 8),
        ("十二面体", 20, 30, 12),
        ("二十面体", 12, 30, 20),
    ]
    for name, v, e, f in polyhedra:
        chi = v - e + f
        print(f"  {name:<10} {v:<4} {e:<4} {f:<4} {chi:<4} {'= 球面 χ ✓' if chi == 2 else ''}")
    print("  → 所有凸多面体 χ = 2（都同伦等价于 S²）")


def part4_topology_in_ml():
    """TDA 与拓扑数据分析"""
    print()
    print("=" * 65)
    print("[4] 应用：拓扑数据分析（TDA）")
    print("=" * 65)
    np.random.seed(42)
    # 在圆上采样 + 加噪声
    n = 100
    theta = np.random.uniform(0, 2*np.pi, n)
    X_circle = np.column_stack([np.cos(theta), np.sin(theta)]) + 0.1 * np.random.randn(n, 2)
    # 在球面（无洞）采样
    X_ball = np.random.randn(n, 2)
    X_ball /= np.linalg.norm(X_ball, axis=1, keepdims=True)
    X_ball *= np.random.uniform(0, 1, n)[:, None]  # 填充圆盘
    # 简单"洞检测"：内部点的密度
    print("  圆采样：外部环带密度 vs 内部密度")
    r_circle = np.linalg.norm(X_circle, axis=1)
    inner_circle = np.mean(r_circle < 0.5)
    print(f"    圆环数据：r<0.5 的比例 = {inner_circle:.3f}（应低 → 有洞）")
    r_ball = np.linalg.norm(X_ball, axis=1)
    inner_ball = np.mean(r_ball < 0.5)
    print(f"    圆盘数据：r<0.5 的比例 = {inner_ball:.3f}（应高 → 无洞）")
    print("  → TDA 用持续同调检测这种'洞'，用于数据形状分析")


def main():
    print("讲透代数拓扑 00 章实验：拓扑等价 + 洞 + Euler + TDA")
    part1_genus_and_chi()
    part2_homology()
    part3_euler_characteristic_polyhedra()
    part4_topology_in_ml()
    print()
    print("=" * 65)
    print("✓ 代数拓扑入门完成。")
    print("  → 拓扑 = 橡皮膜几何")
    print("  → 同调群把'洞'变成代数")
    print("  → χ = V-E+F 是拓扑不变量")
    print("  → TDA 用于 ML 数据形状分析")
    print("=" * 65)


if __name__ == "__main__":
    main()
