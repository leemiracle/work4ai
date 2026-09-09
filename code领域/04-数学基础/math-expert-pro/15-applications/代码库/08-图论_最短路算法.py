"""
图论：最短路算法与网络分析
==========================
数学概念：图论 / 最短路 / Dijkstra 算法 / Floyd-Warshall 算法 / 邻接矩阵
应用领域：网络路由 / GPS 导航 / 社交网络 / 物流调度
核心思想：图 G=(V,E) 用邻接矩阵 A 表示，A[i][j]=权重（距离）。
         Dijkstra 算法用贪心策略从源点逐步扩展最短路径树（要求非负权）。
         Floyd-Warshall 用动态规划求所有点对最短路（可处理负权但非负环）：
           dist[k][i][j] = min(dist[k-1][i][j], dist[k-1][i][k] + dist[k-1][k][j])
         最短路 = 图上两点间的"测地线"，连接图的谱性质与网络流。
运行方式：python "08-图论_最短路算法.py"
依赖：numpy, matplotlib, networkx
"""

import numpy as np
import matplotlib.pyplot as plt
import heapq

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 图数据结构 ============

def random_graph(n=10, density=0.4, max_weight=20, seed=42):
    """生成随机带权无向图。返回邻接矩阵（无穷大表示无边）。"""
    rng = np.random.RandomState(seed)
    A = np.full((n, n), np.inf)
    np.fill_diagonal(A, 0)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.rand() < density:
                w = rng.randint(1, max_weight + 1)
                A[i][j] = A[j][i] = w
    return A


# ============ 2. Dijkstra 算法（单源最短路，贪心）============

def dijkstra(A, source):
    """Dijkstra 单源最短路算法。
    核心：用最小堆维护待扩展节点，每次取距离最小的扩展。
    要求：所有边权非负。
    复杂度：O((V+E) log V) with heap
    返回：dist[] 最短距离, prev[] 前驱节点（用于重建路径）
    """
    n = len(A)
    dist = [float('inf')] * n
    prev = [None] * n
    dist[source] = 0
    visited = [False] * n
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        for v in range(n):
            if A[u][v] < np.inf and not visited[v]:
                new_dist = d + A[u][v]
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(heap, (new_dist, v))
    return dist, prev


def reconstruct_path(prev, source, target):
    """从前驱数组重建最短路径。"""
    path = []
    node = target
    while node is not None:
        path.append(node)
        if node == source:
            break
        node = prev[node]
    return path[::-1] if path[0] == source else []


# ============ 3. Floyd-Warshall 算法（全源最短路，动态规划）============

def floyd_warshall(A):
    """Floyd-Warshall 全源最短路算法。
    核心 DP: dist[k][i][j] = min(dist[k-1][i][j], dist[k-1][i][k] + dist[k-1][k][j])
    含义：前 k 个节点做中转时，i 到 j 的最短路。
    复杂度：O(V³)
    """
    n = len(A)
    dist = A.copy().astype(float)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


# ============ 4. 可视化与实验 ============

def main():
    # ---- 生成随机图 ----
    n = 10
    A = random_graph(n=n, density=0.5, max_weight=20, seed=42)
    print(f"[数据] 生成 {n} 节点随机图，{np.sum(A < np.inf) - n} 条边")

    # ---- Dijkstra: 从节点 0 出发 ----
    print("\n" + "=" * 60)
    print("实验 1：Dijkstra 单源最短路（源点 = 节点 0）")
    print("=" * 60)
    source = 0
    dist_from_0, prev = dijkstra(A, source)

    print(f"从节点 {source} 到各节点的最短距离：")
    for i in range(n):
        path = reconstruct_path(prev, source, i)
        path_str = " → ".join(map(str, path)) if path else "不可达"
        print(f"  到节点 {i}: 距离={dist_from_0[i]:.0f}  路径=[{path_str}]")

    # ---- Floyd-Warshall: 全源最短路 ----
    print("\n" + "=" * 60)
    print("实验 2：Floyd-Warshall 全源最短路矩阵")
    print("=" * 60)
    all_dist = floyd_warshall(A)

    # 图的直径 = 最长最短路
    finite_dists = all_dist[all_dist < np.inf]
    diameter = finite_dists.max()
    avg_dist = finite_dists.mean()
    print(f"图直径（最长最短路）: {diameter:.0f}")
    print(f"平均最短路距离: {avg_dist:.1f}")
    print(f"图的半径（从节点0出发的最远距离）: {max(d for d in dist_from_0 if d < np.inf):.0f}")

    # ---- 中心性分析 ----
    print("\n" + "=" * 60)
    print("实验 3：节点中心性分析（谁是最「中心」的节点？）")
    print("=" * 60)

    # 接近中心性：到所有其他节点距离之和的倒数
    closeness = []
    for i in range(n):
        d_i = all_dist[i]
        total = np.sum(d_i[d_i < np.inf])
        closeness.append(1.0 / total if total > 0 else 0)

    # 介数中心性：多少条最短路经过该节点（简化版）
    betweenness = np.zeros(n)
    for s in range(n):
        for t in range(s + 1, n):
            path = reconstruct_path(
                (lambda src: dijkstra(A, src)[1])(s), s, t)
            for node in path[1:-1]:  # 排除起点终点
                betweenness[node] += 1

    print(f"{'节点':<6} {'接近中心性':<14} {'介数中心性':<14} {'角色'}")
    print("-" * 50)
    for i in range(n):
        role = "★枢纽" if betweenness[i] > np.median(betweenness) else "边缘"
        print(f"{i:<6} {closeness[i]:<14.6f} {betweenness[i]:<14.0f} {role}")

    best_hub = np.argmax(betweenness)
    print(f"\n[解读] 节点 {best_hub} 介数中心性最高 = 网络的关键枢纽。")
    print(f"       若移除该节点，最多最短路会中断（网络脆弱性分析的基础）。")

    # ============ 5. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 用 spring layout 固定节点位置
    rng = np.random.RandomState(7)
    pos = rng.rand(n, 2)

    # 图 1：图结构 + 从节点 0 的最短路树
    ax = axes[0, 0]
    # 画所有边
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j] < np.inf:
                ax.plot([pos[i, 0], pos[j, 0]], [pos[i, 1], pos[j, 1]],
                        'gray', alpha=0.3, lw=1)
                mx, my = (pos[i, 0] + pos[j, 0]) / 2, (pos[i, 1] + pos[j, 1]) / 2
                ax.text(mx, my, f"{int(A[i][j])}", fontsize=7, color='gray')
    # 画最短路树边
    for i in range(n):
        if prev[i] is not None and i != source:
            j = prev[i]
            ax.plot([pos[i, 0], pos[j, 0]], [pos[i, 1], pos[j, 1]],
                    'r-', lw=2.5, alpha=0.8)
    # 画节点
    colors = ['red' if i == source else 'steelblue' for i in range(n)]
    ax.scatter(pos[:, 0], pos[:, 1], c=colors, s=300, zorder=5, edgecolors='black')
    for i in range(n):
        ax.annotate(str(i), pos[i], fontsize=10, ha='center', va='center',
                    color='white', fontweight='bold')
    ax.set_title(f'Dijkstra 最短路树（红色，源点={source}）')
    ax.set_aspect('equal')

    # 图 2：距离矩阵热力图
    ax = axes[0, 1]
    dist_display = all_dist.copy()
    dist_display[dist_display == np.inf] = -1
    im = ax.imshow(dist_display, cmap='YlOrRd')
    ax.set_xlabel('目标节点')
    ax.set_ylabel('源节点')
    ax.set_title('Floyd-Warshall 全源最短路矩阵')
    plt.colorbar(im, ax=ax, label='最短距离')
    for i in range(n):
        for j in range(n):
            val = all_dist[i][j]
            txt = f"{int(val)}" if val < np.inf else "∞"
            ax.text(j, i, txt, ha='center', va='center', fontsize=7)

    # 图 3：中心性对比
    ax = axes[1, 0]
    x = np.arange(n)
    ax.bar(x - 0.2, closeness / max(closeness), 0.4, label='接近中心性(归一化)', color='steelblue')
    ax.bar(x + 0.2, betweenness / max(betweenness) if max(betweenness) > 0 else betweenness,
           0.4, label='介数中心性(归一化)', color='coral')
    ax.set_xlabel('节点')
    ax.set_ylabel('中心性（归一化）')
    ax.set_title('节点中心性对比')
    ax.legend()
    ax.set_xticks(x)
    ax.grid(alpha=0.3, axis='y')

    # 图 4：最短路径长度分布
    ax = axes[1, 1]
    all_shortest = finite_dists[finite_dists > 0]
    ax.hist(all_shortest, bins=range(0, int(diameter) + 2), color='green', alpha=0.7, edgecolor='black')
    ax.axvline(avg_dist, color='red', ls='--', lw=2, label=f'平均={avg_dist:.1f}')
    ax.axvline(diameter, color='orange', ls='--', lw=2, label=f'直径={diameter:.0f}')
    ax.set_xlabel('最短路径长度')
    ax.set_ylabel('节点对数量')
    ax.set_title('最短路径长度分布')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig("08-图论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 08-图论_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. Dijkstra：贪心策略，O((V+E)logV)，适合单源非负权")
    print("2. Floyd-Warshall：动态规划，O(V³)，适合全源/负权")
    print("3. 介数中心性：识别网络枢纽（移除它破坏最多最短路）")
    print('4. 图直径=最长最短路，平均距离=网络「紧密度」')
    print('\n[解读] 最短路是图论的「测地线」——GPS导航、网络路由、社交网络')
    print("       都在找它。介数中心性高的节点=网络脆弱点，是网络分析的核心指标。")


if __name__ == "__main__":
    main()
