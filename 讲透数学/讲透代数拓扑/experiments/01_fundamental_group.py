"""
讲透代数拓扑 01 章实验：基本群 + 绕数。
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def winding_number(path, center):
    """计算环路绕 center 的绕数（数值版）"""
    cx, cy = center
    angles = np.arctan2(path[:, 1] - cy, path[:, 0] - cx)
    # 解卷绕（unwrap）+ 总变化 / 2π
    unwrapped = np.unwrap(angles)
    return (unwrapped[-1] - unwrapped[0]) / (2 * np.pi)


def part1_winding_number():
    print("=" * 65)
    print("[1] 绕数（winding number）= π₁(S¹) 的元素")
    print("=" * 65)
    t = np.linspace(0, 1, 1000)
    # 绕原点 n 圈的环路
    for n in [-2, -1, 0, 1, 2, 3]:
        theta = 2 * np.pi * n * t
        path = np.column_stack([np.cos(theta), np.sin(theta)])
        w = winding_number(path, (0, 0))
        print(f"  设计绕 {n} 圈：实测绕数 = {w:.4f}")


def part2_loop_can_contract():
    print()
    print("=" * 65)
    print("[2] 环路能否缩点：R² vs R²\\{0}")
    print("=" * 65)
    t = np.linspace(0, 1, 1000)
    theta = 2 * np.pi * t
    circle = np.column_stack([np.cos(theta), np.sin(theta)])
    # 在 R² 上：可以线性缩到原点
    print("  R² 上的环路（线性缩点）：")
    for alpha in [1.0, 0.5, 0.0]:
        contracted = alpha * circle
        max_r = np.max(np.linalg.norm(contracted, axis=1))
        print(f"    α={alpha:.1f}: 最大半径 = {max_r:.4f}")
    print("  → α=0 时缩成原点 ✓")

    # 在 R²\\{0}：绕一圈缩不掉
    print()
    print("  R²\\{0} 上绕一圈的环路：无法缩点")
    print("  任何连续缩放必须保持绕数 = 1")
    print("  → 必须穿过原点（被禁止）→ 缩不掉 ✗")


def part3_visualize():
    """可视化环路 + 缩点"""
    print()
    print("=" * 65)
    print("[3] 可视化：环路 + 缩点（保存 PNG）")
    print("=" * 65)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    t = np.linspace(0, 1, 1000)
    theta = 2 * np.pi * t
    circle = np.column_stack([np.cos(theta), np.sin(theta)])

    # 左图：R² 上缩点
    ax = axes[0]
    ax.plot(circle[:, 0], circle[:, 1], 'b-', lw=2, label='original')
    for alpha in [0.75, 0.5, 0.25]:
        c = alpha * circle
        ax.plot(c[:, 0], c[:, 1], '--', alpha=0.5, label=f'α={alpha}')
    ax.plot(0, 0, 'ko', markersize=8)
    ax.set_title("R²: loop can contract to point")
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 右图：R²\\{0} 不能缩
    ax = axes[1]
    ax.plot(circle[:, 0], circle[:, 1], 'r-', lw=2, label='winding=1')
    # 尝试缩（但必须绕过原点）
    for r in [0.75, 0.5]:
        c = r * circle
        ax.plot(c[:, 0], c[:, 1], '--', alpha=0.5)
    ax.plot(0, 0, 'kx', markersize=15, markeredgewidth=3, label='hole (excluded)')
    ax.set_title("R²\\{0}: loop CANNOT contract")
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fundamental_group.png")
    plt.savefig(out, dpi=80)
    print(f"  图像保存：{out}")


def main():
    np.random.seed(0)
    print("讲透代数拓扑 01 章实验：基本群 + 绕数")
    part1_winding_number()
    part2_loop_can_contract()
    part3_visualize()
    print()
    print("=" * 65)
    print("✓ 基本群核心验证。")
    print("  → 绕数 = π₁(S¹) 的元素（整数）")
    print("  → R² 上环路可缩；R²\\{0} 不行")
    print("=" * 65)


if __name__ == "__main__":
    main()
