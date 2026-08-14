"""
讲透群论 02 章实验：群作用 + 轨道-稳定化子 + Burnside。
"""
from itertools import permutations, product


def dihedral_action_on_vertices():
    """D3 作用在三角形 3 顶点上"""
    print("=" * 65)
    print("[1] D3 作用在 3 个顶点上：轨道-稳定化子")
    print("=" * 65)
    # D3 ≅ S3：6 个排列
    elems = list(permutations(range(3)))
    # 顶点 0 的轨道
    orbit_0 = set()
    for g in elems:
        orbit_0.add(g[0])
    print(f"  顶点 0 的轨道 = {orbit_0}, 大小 = {len(orbit_0)}")
    # 顶点 0 的稳定化子
    stab_0 = [g for g in elems if g[0] == 0]
    print(f"  顶点 0 的稳定化子 = {stab_0}, 大小 = {len(stab_0)}")
    print(f"  |G|=6, 轨道 × 稳定化子 = {len(orbit_0)} × {len(stab_0)} = {len(orbit_0)*len(stab_0)} ✓")


def burnside_necklace():
    """Burnside：n 颗珠子 k 种颜色的项链数（可旋转）"""
    print()
    print("=" * 65)
    print("[2] Burnside 引理：项链计数")
    print("=" * 65)
    for n, k in [(6, 3), (4, 2), (8, 3)]:
        # 旋转群 Z/nZ 作用
        # 每个 g（旋转 r）固定的染色数 = k^(gcd(n,r))
        fixed_sum = sum(k ** gcd(n, r) for r in range(n))
        orbits = fixed_sum // n
        print(f"  n={n} 颗珠子, k={k} 色: 本质不同项链 = {orbits}")


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def conjugation_action():
    """共轭作用：S3 的共轭类"""
    print()
    print("=" * 65)
    print("[3] 共轭作用：S3 的共轭类")
    print("=" * 65)
    elems = list(permutations(range(3)))
    classes = {}
    for g in elems:
        # 找共轭类
        key = tuple(sorted(g))  # 简化：用 cycle type
        # 实际应该用 cycle structure
        cycle_type = sorted([len(c) for c in cycles(g)], reverse=True)
        key = tuple(cycle_type)
        classes.setdefault(key, []).append(g)
    print(f"  S3 的共轭类（按 cycle type）：")
    for ct, members in classes.items():
        print(f"    cycle type {ct}: {len(members)} 个元素")
    print(f"  → 共轭类数 = {len(classes)}（S3 有 3 个共轭类）")


def cycles(p):
    """排列的 cycle 分解"""
    visited = set()
    result = []
    for i in range(len(p)):
        if i not in visited:
            c = []
            j = i
            while j not in visited:
                visited.add(j)
                c.append(j)
                j = p[j]
            if len(c) > 1:
                result.append(c)
    return result


def main():
    print("讲透群论 02 章实验：群作用 + Burnside")
    dihedral_action_on_vertices()
    burnside_necklace()
    conjugation_action()
    print()
    print("=" * 65)
    print("✓ 群作用核心验证。")
    print("  → 轨道-稳定化子：|G·x| × |G_x| = |G|")
    print("  → Burnside 数本质不同的配置")
    print("=" * 65)


if __name__ == "__main__":
    main()
