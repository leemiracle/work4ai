"""
群论与对称：从晶体到基本粒子
================================
数学概念：群论 / 群作用 / 对称群 / 表示论 / 李群 / 有限群分类
应用领域：密码学 / 粒子物理 / 化学（分子对称）/ 结晶学 / 艺术（装饰图案）
核心思想：群 = 对称性的代数语言。
  群 (G,·)：满足封闭/结合/单位/逆元四条公理的集合+运算
  对称群 S_n：n 个元素的全排列群（|S_n|=n!）
  群作用：G 作用于集合 X → 描述 X 的对称性
  表示论：群元素 → 矩阵（对称性的线性实现）
  李群：连续对称群（如旋转 SO(3)/洛伦兹群）
运行方式：python "22-群论_对称与表示.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import math

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 群论基础 ============

def cayley_table(elements, operation):
    """生成群的 Cayley 表（乘法表）。
    elements: 群元素列表
    operation(a, b): 群运算函数
    """
    n = len(elements)
    table = np.zeros((n, n), dtype=int)
    for i, a in enumerate(elements):
        for j, b in enumerate(elements):
            result = operation(a, b)
            table[i, j] = elements.index(result)
    return table


def multiply_permutations(p, q):
    """排列的复合：先 q 后 p。"""
    return tuple(p[q[i]] for i in range(len(p)))


def perm_inverse(p):
    """排列的逆。"""
    inv = [0] * len(p)
    for i, v in enumerate(p):
        inv[v] = i
    return tuple(inv)


def generate_group(generators, n):
    """从生成元生成群（BFS 搜索）。"""
    identity = tuple(range(n))
    group = {identity}
    queue = list(generators)
    group.update(generators)
    while queue:
        g = queue.pop(0)
        for h in list(group):
            for prod in [multiply_permutations(g, h), multiply_permutations(h, g)]:
                if prod not in group:
                    group.add(prod)
                    queue.append(prod)
    return sorted(group)


# ============ 2. 对称操作 ============

def rotate(points, angle):
    """2D 旋转。"""
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle), np.cos(angle)]])
    return points @ R.T


def reflect(points, axis_angle):
    """2D 反射（关于过原点、角度为 axis_angle 的轴）。"""
    R = np.array([[np.cos(2*axis_angle), np.sin(2*axis_angle)],
                  [np.sin(2*axis_angle), -np.cos(2*axis_angle)]])
    return points @ R.T


# ============ 3. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：对称群 S₃——最小的非阿贝尔群")
    print("=" * 60)

    # S₃ 的 6 个元素
    S3 = [
        (0,1,2),  # e（单位元）
        (1,0,2),  # (12)
        (0,2,1),  # (23)
        (2,1,0),  # (13)
        (1,2,0),  # (123)
        (2,0,1),  # (132)
    ]
    names = ['e', '(12)', '(23)', '(13)', '(123)', '(132)']

    # Cayley 表
    table = cayley_table(S3, multiply_permutations)

    print("S₃ 的 Cayley 表（乘法表）：")
    print("     " + "  ".join(f"{n:>5}" for n in names))
    for i, name in enumerate(names):
        row = "  ".join(f"{names[table[i,j]]:>5}" for j in range(6))
        print(f"{name:>5}  {row}")

    # 验证群公理
    print(f"\n群公理验证：")
    # 单位元
    is_identity = all(multiply_permutations(S3[0], g) == g for g in S3)
    print(f"  单位元 e: {'✓' if is_identity else '✗'}")
    # 逆元
    has_inverse = all(any(multiply_permutations(g, h) == (0,1,2) for h in S3) for g in S3)
    print(f"  逆元存在: {'✓' if has_inverse else '✗'}")
    # 非阿贝尔性
    nonabelian = multiply_permutations(S3[1], S3[4]) != multiply_permutations(S3[4], S3[1])
    print(f"  非交换（非阿贝尔）: {'✓ (12)(123)≠(123)(12)' if nonabelian else '✗'}")
    print(f"  |S₃| = {len(S3)} = 3!")

    print(f"\n[解读] S₃ 是等边三角形的对称群（3 旋转 + 3 反射 = 6 个对称操作）。")
    print(f"       非交换意味着'先转后翻' ≠ '先翻后转'——顺序很重要。")

    print("\n" + "=" * 60)
    print("实验 2：正多边形的对称群（Dₙ 二面体群）")
    print("=" * 60)

    polygons = [(3, '三角形 D₃'), (4, '正方形 D₄'), (5, '五边形 D₅'), (6, '六边形 D₆')]

    print(f"{'图形':<12} {'群阶 |Dₙ|':<12} {'旋转数':<10} {'反射数':<10} {'阿贝尔?'}")
    print("-" * 55)
    for n, name in polygons:
        order = 2 * n
        n_rotations = n
        n_reflections = n
        abelian = n <= 2  # D₁ 和 D₂ 阿贝尔；Dₙ(n≥3) 非阿贝尔
        print(f"{name:<12} {order:<12} {n_rotations:<10} {n_reflections:<10} {'是' if abelian else '否'}")

    print(f"\n[解读] Dₙ = n 个旋转 + n 个反射 = 2n 个元素。")
    print(f"       对称性越多 = 图形越'规则'。圆有无限对称性（O(2) 群）。")

    print("\n" + "=" * 60)
    print("实验 3：群作用——对称性如何作用于图形")
    print("=" * 60)

    # 正六边形的顶点
    angles_hex = np.linspace(0, 2*np.pi, 7)[:-1]
    hex_points = np.column_stack([np.cos(angles_hex), np.sin(angles_hex)])

    print("正六边形在 D₆ 的作用下的变换：")
    # 旋转 60°
    rotated = rotate(hex_points, np.pi / 3)
    print(f"  旋转 60°: 顶点 {0:.1f},{1:.1f} → {rotated[0,0]:.2f},{rotated[0,1]:.2f}")
    # 反射
    reflected = reflect(hex_points, 0)
    print(f"  x 轴反射: 顶点 {0:.1f},{1:.1f} → {reflected[0,0]:.2f},{reflected[0,1]:.2f}")

    print(f"\n[解读] 群作用 = 对称操作如何变换图形。")
    print(f"       不动点 = 保持不变的部分 → 揭示图形结构。")

    print("\n" + "=" * 60)
    print("实验 4：表示论——对称性的矩阵实现")
    print("=" * 60)

    print("SO(2) 旋转群的 2D 表示：")
    print("  R(θ) = [cos θ  -sin θ]")
    print("         [sin θ   cos θ]")

    print("\nSO(3) 旋转群的 3D 表示（欧拉角）：")
    print("  R = Rz(φ) × Ry(θ) × Rz(ψ)")

    # Noether 定理
    print("\n" + "=" * 60)
    print("实验 5：Noether 定理——对称性 = 守恒律")
    print("=" * 60)

    noether = [
        ("时间平移对称", "能量守恒", "物理定律不随时间变"),
        ("空间平移对称", "动量守恒", "物理定律在空间各处相同"),
        ("旋转对称", "角动量守恒", "物理定律与方向无关"),
        ("规范对称 (U(1))", "电荷守恒", "电磁理论的数学结构"),
    ]

    print(f"{'对称性':<20} {'守恒律':<15} {'物理意义'}")
    print("-" * 65)
    for sym, cons, meaning in noether:
        print(f"{sym:<20} {cons:<15} {meaning}")

    print(f"\n[解读] Noether 定理：每一个连续对称性对应一个守恒量。")
    print(f"       这是理论物理最优美的定理之一——连接对称性与物理定律。")
    print(f"       标准模型 = 规范群 SU(3)×SU(2)×U(1) → 3 种基本力的对称性。")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # 图 1：S₃ Cayley 表热力图
    ax = axes[0, 0]
    im = ax.imshow(table, cmap='tab10')
    ax.set_xticks(range(6)); ax.set_xticklabels(names)
    ax.set_yticks(range(6)); ax.set_yticklabels(names)
    ax.set_title('S₃ Cayley 表（对称群乘法表）')
    for i in range(6):
        for j in range(6):
            ax.text(j, i, names[table[i,j]], ha='center', va='center', fontsize=8)

    # 图 2-4：正多边形 + 对称轴
    for idx, (n, name) in enumerate([(3, '三角形'), (4, '正方形'), (6, '六边形')]):
        ax = axes[0 if idx < 2 else 1, idx + 1 if idx < 2 else 0]
        angles_poly = np.linspace(0, 2*np.pi, n+1)
        x_poly = np.cos(angles_poly)
        y_poly = np.sin(angles_poly)
        ax.fill(x_poly, y_poly, alpha=0.2, color='steelblue')
        ax.plot(x_poly, y_poly, 'b-', lw=2)

        # 画对称轴
        for k in range(n):
            angle_axis = k * np.pi / n
            ax.plot([-1.5*np.cos(angle_axis), 1.5*np.cos(angle_axis)],
                    [-1.5*np.sin(angle_axis), 1.5*np.sin(angle_axis)],
                    'r--', alpha=0.3, lw=1)

        # 画旋转后的图形
        rotated_poly = rotate(np.column_stack([x_poly, y_poly]), 2*np.pi/n)
        ax.plot(rotated_poly[:, 0], rotated_poly[:, 1], 'g--', lw=1.5, alpha=0.5)

        ax.set_title(f'{name}（D_{n}, |D_{n}|={2*n}）')
        ax.set_aspect('equal')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.grid(alpha=0.2)

    # 图 5：群阶 vs 图形复杂度
    ax = axes[1, 1]
    ns = range(3, 13)
    orders = [2*n for n in ns]
    ax.bar(ns, orders, color='steelblue', alpha=0.7)
    ax.set_xlabel('正 n 边形')
    ax.set_ylabel('|Dₙ|（群阶）')
    ax.set_title('对称群阶 vs 多边形边数')
    ax.set_xticks(list(ns))
    ax.grid(alpha=0.3, axis='y')

    # 图 6：Noether 定理总结
    ax = axes[1, 2]
    ax.text(0.5, 0.9, 'Noether 定理', ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
    ax.text(0.5, 0.75, '对称性 ⟺ 守恒律', ha='center', fontsize=16, color='red',
            transform=ax.transAxes, fontweight='bold')
    y_pos = 0.6
    for sym, cons, _ in noether:
        ax.text(0.5, y_pos, f'{sym} → {cons}', ha='center', fontsize=10, transform=ax.transAxes)
        y_pos -= 0.13
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("22-群论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 22-群论_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 群 = 对称性的代数（封闭/结合/单位/逆元）")
    print("2. 对称群 S_n：排列群；二面体群 D_n：正多边形对称")
    print("3. 表示论：群元素 → 矩阵（对称性的线性实现）")
    print("4. Noether 定理：连续对称性 ⟺ 守恒律（物理最优美定理）")
    print("5. 应用：密码学/粒子物理/化学/结晶学/艺术")
    print("\n[解读] 群论是'对称性的语言'——")
    print("       从分子的对称性到宇宙的基本力，")
    print("       从密码学到装饰艺术，对称性无处不在。")
    print("       Noether 定理揭示了'对称性=守恒律'——")
    print("       这是人类理解自然的最深刻洞见之一。")


if __name__ == "__main__":
    main()
