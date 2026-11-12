# -*- coding: utf-8 -*-
"""关系结构的全流程数值实拍:传递闭包 → Hasse 图提取 → 拓扑排序。

00-体系结构/03-可构造与结构/04-转代码 三章配套实验。纯标准库。

数学事实链:
  1. Warshall: 传递闭包 R⁺ = ⋃ₖ≥1 Rᵏ,三重循环 O(n³)
     —— 03 章的最小不动点视角: R ⊆ R² ⊆ ... 的极限
  2. Hasse 图: 偏序的全部信息压缩进"覆盖关系"(去掉自反与传递冗余)
  3. 拓扑排序: 偏序的线性扩展(Kahn 算法,每次取入度 0 的极小元)
     —— 反直觉点: 找 1 个线性扩展 O(V+E),数全部线性扩展是 #P 完全

手算例(5 元偏序,取自 00 章"构建依赖"意象):
  1<2, 1<3, 2<4, 3<4, 4<5   (DAG: 1→2→4→5, 1→3→4)
  传递闭包应含: 1→2,1→3,1→4,1→5,2→4,2→5,3→4,3→5,4→5 (共 9 对)
  Hasse 覆盖边: 恰好那 5 条给定的边(无冗余)
  线性扩展计数: 2 (1,[2,3]两种中间顺序,4,5)

跑法: python3 -u experiments/00_relation_closure.py
"""

from itertools import permutations


def warshall(matrix):
    """传递闭包:原地 Warshall。matrix[i][j]=1 ⟺ iRj。

    允许中途点 k 参与: R[i,j] |= R[i,k] & R[k,j],按 k 扫一遍即得闭包。
    —— 动态规划的第一次显灵(00 章美之时刻 2)。
    """
    n = len(matrix)
    reach = [row[:] for row in matrix]          # 不改输入
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                row_i, row_k = reach[i], reach[k]
                for j in range(n):
                    if row_k[j] and not row_i[j]:
                        row_i[j] = 1
    return reach


def pairs(matrix):
    """把矩阵读成有序对集合(可读输出用)。"""
    return {(i, j) for i, row in enumerate(matrix) for j, v in enumerate(row) if v}


def hasse_edges(less_matrix):
    """覆盖关系: i≺j 且不存在 k 使 i<k<j。

    Hasse 图=偏序的无损压缩: 去掉自反边与可传递推出的边。
    """
    n = len(less_matrix)
    covers = []
    for i in range(n):
        for j in range(n):
            if less_matrix[i][j] and not any(
                less_matrix[i][k] and less_matrix[k][j]
                for k in range(n) if k not in (i, j)
            ):
                covers.append((i, j))
    return covers


def toposort(less_matrix):
    """Kahn 拓扑排序: 反复取入度为 0 的极小元(字典序最小,保证确定性)。"""
    n = len(less_matrix)
    indeg = [sum(less_matrix[i][j] for i in range(n)) for j in range(n)]
    order, avail = [], sorted(j for j in range(n) if indeg[j] == 0)
    while avail:
        j = avail.pop(0)
        order.append(j)
        for k in range(n):
            if less_matrix[j][k]:
                indeg[k] -= 1
                if indeg[k] == 0:
                    avail.append(k)
        avail.sort()
    assert len(order) == n, "存在环:偏序被违反(Kahn 的免费环检测)"
    return order


def is_linear_extension(order, less_matrix):
    """验证 order 是线性扩展: 所有 i<j 的偏序关系都被尊重。"""
    pos = {v: i for i, v in enumerate(order)}
    return all(
        pos[i] < pos[j]
        for i, row in enumerate(less_matrix) for j, v in enumerate(row) if v
    )


def count_linear_extensions(n, less_matrix):
    """数全部线性扩展(brute force,只作小规模演示)。

    构造易(O(V+E)) vs 计数难(#P 完全)——03 章反直觉发现的现场。
    """
    return sum(
        1 for perm in permutations(range(n)) if is_linear_extension(perm, less_matrix)
    )


def main():
    # ---- 手算例:1<2,1<3,2<4,3<4,4<5 (顶点 0..4) ----
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    n = 5
    R = [[0] * n for _ in range(n)]
    for i, j in edges:
        R[i][j] = 1

    closure = warshall(R)
    got = sorted(pairs(closure))
    expected = sorted({
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 3), (1, 4),
        (2, 3), (2, 4),
        (3, 4),
    })
    assert got == expected, f"闭包与手算不符: {got}"

    covers = hasse_edges(closure)
    assert sorted(covers) == sorted(edges), f"Hasse 覆盖边应恰为原边: {covers}"

    order = toposort(closure)
    assert is_linear_extension(order, closure)
    assert order == [0, 1, 2, 3, 4], f"字典序 Kahn 应得确定序: {order}"

    cnt = count_linear_extensions(n, closure)
    assert cnt == 2, f"线性扩展应恰 2 个(2/3 可交换): {cnt}"

    print("=" * 62)
    print("关系结构全流程:闭包 → Hasse → 拓扑排序(5 元手算例全过)")
    print("=" * 62)
    print(f"输入边        : {edges}")
    print(f"传递闭包      : {len(got)} 对 —— {got}")
    print(f"Hasse 覆盖边  : {covers}  (无损压缩:9 对 → 5 边)")
    print(f"Kahn 拓扑序   : {order}")
    print(f"线性扩展总数  : {cnt}  (找 1 个 O(V+E);数全部 #P 完全)")
    print()

    # ---- 对照组:加一条边 2<3,偏序收紧,线性扩展坍缩为 1 ----
    R2 = [row[:] for row in R]
    R2[1][2] = 1                                    # 2<3:链 1<2<3<4<5
    closure2 = warshall(R2)
    cnt2 = count_linear_extensions(n, closure2)
    assert cnt2 == 1, f"全链偏序的线性扩展应唯一: {cnt2}"
    print("对照组(加边 2<3 → 全链):")
    print(f"  闭包对数     : {len(pairs(closure2))} (C(5,2)=10,链的闭包=全部有序对)")
    print(f"  线性扩展总数 : {cnt2}  —— 偏序越紧,自由度越小,排序唯一化")
    print()

    # ---- Warshall 的位并行彩蛋:同一算法,布尔行=整数位串 ----
    def warshall_bits(rows):
        """每行压成一个整数(位并行 Warshall):64 个顶点内,内层循环进位运算。"""
        m = rows[:]
        for k in range(len(m)):
            for i in range(len(m)):
                if (m[i] >> k) & 1:
                    m[i] |= m[k]
        return m

    rows = [sum(1 << j for j, v in enumerate(row) if v) for row in R]
    bits = warshall_bits(rows)
    got_bits = {(i, j) for i, r in enumerate(bits) for j in range(n) if (r >> j) & 1}
    assert got_bits == set(got), "位并行 Warshall 与朴素版必须一致"
    print("位并行 Warshall:同一数学,每条内循环做 64 个赋值——")
    print("  04 章 Boole 走廊的免费午餐(x&(x-1) 家族)在算法层的应用")

    print()
    print("读数:")
    print("  · 闭包=最小不动点(R⊆R²⊆… 的极限,Knaster–Tarski 的有限现场)")
    print("  · Hasse 图把 9 对关系压回 5 条边——偏序信息的无损压缩")
    print("  · 构造 1 个线性扩展线性时间;数全部 = #P 完全——隔着整个动物园")
    print("  · 位并行:数学恒等式直接换算力(64×),性能工程的离散观")


if __name__ == "__main__":
    main()
