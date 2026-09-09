"""
马尔可夫链与 Google PageRank
============================
数学概念：马尔可夫链 / 平稳分布 / 主特征向量 / 幂迭代法
应用领域：网页排名、社交网络分析、节点重要性评估
核心思想：网页间的超链接构成一个随机游走马尔可夫链，PageRank 即该链的平稳分布向量 π，
         满足 π = π P (P 为转移矩阵)。用幂迭代法反复乘以转移矩阵即可收敛到主特征向量。
         加入"阻尼因子" d=0.85 模拟用户随机跳转, 保证链的遍历性与收敛性。
运行方式：python "02-马尔可夫链_PageRank.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 1. 构造网页链接图 (12 个网页) ============
# adj[i][j] = 1 表示页面 i 有链接指向页面 j
N = 12
PAGES = [f"P{i}" for i in range(N)]
# 人工设计的链接结构 (含环路与汇聚点, 模拟真实网络)
EDGES = {
    0: [1, 2],   1: [2, 3],   2: [0, 3, 4],
    3: [5],      4: [2, 5, 6], 5: [6, 7],
    6: [5, 8],   7: [8, 9],   8: [6, 9, 10],
    9: [10, 11], 10: [11],    11: [0],
}
adj = np.zeros((N, N))
for i, outs in EDGES.items():
    for j in outs:
        adj[i, j] = 1.0
print(f"[网络] {N} 个网页, {int(adj.sum())} 条链接")

# ============ 2. 数学建模：构造转移矩阵 + 幂迭代 ============
def build_transition(adj, d=0.85):
    """
    构造 PageRank 转移矩阵 P (Google 矩阵):
        P = d * M + (1-d)/N * J
    其中 M 为行归一化链接矩阵(处理悬挂节点),
    d 为阻尼因子, J 为全 1 矩阵(模拟随机跳转)。
    """
    M = adj.copy()
    # 处理悬挂节点(无出链的页面): 均匀跳转到所有页面
    for i in range(N):
        if M[i].sum() == 0:
            M[i] = np.ones(N) / N
        else:
            M[i] /= M[i].sum()
    P = d * M + (1 - d) / N * np.ones((N, N))
    return P

def power_iteration(P, n_iter=100, tol=1e-10):
    """幂迭代法求 PageRank: π_{t+1} = π_t P, 迭代至收敛。"""
    pi = np.ones(N) / N              # 初始均匀分布
    history = [pi.copy()]
    for t in range(n_iter):
        pi_new = pi @ P              # 右乘转移矩阵
        history.append(pi_new.copy())
        if np.linalg.norm(pi_new - pi, 1) < tol:
            print(f"[收敛] 第 {t+1} 步达到容差")
            break
        pi = pi_new
    return pi / pi.sum(), np.array(history)

# ============ 3. 计算与可视化 ============
P = build_transition(adj, d=0.85)
pagerank, hist = power_iteration(P, n_iter=200)

# 验证: π 是否为 P 的左特征向量 (特征值=1)
check = pagerank @ P
print(f"[验证] ||πP - π||_1 = {np.linalg.norm(check - pagerank, 1):.2e} (应≈0)")

# 排名
rank = np.argsort(-pagerank)
print("\nPageRank 排名:")
for r, idx in enumerate(rank, 1):
    print(f"  #{r:2d}  {PAGES[idx]:4s}  PR={pagerank[idx]:.4f}")

# ---- 绘图 ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
for i in range(N):
    ax.plot(hist[:, i], label=PAGES[i], alpha=0.8)
ax.set_xlabel("迭代步数")
ax.set_ylabel("PageRank 值")
ax.set_title("幂迭代收敛过程 (各页面 PR 值随迭代变化)")
ax.legend(ncol=4, fontsize=7)
ax.grid(alpha=0.3)

ax = axes[1]
colors = plt.cm.viridis(pagerank / pagerank.max())
bars = ax.bar(range(N), pagerank[rank], color=colors)
ax.set_xticks(range(N))
ax.set_xticklabels([PAGES[i] for i in rank], rotation=45)
ax.set_ylabel("PageRank 值")
ax.set_title("最终 PageRank 排名 (降序)")
ax.grid(alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("02-PageRank_结果.png", dpi=120)
print("\n[结果] 图像已保存: 02-PageRank_结果.png")
print("[解读] 入链越多、且来自高 PR 页面的节点排名越高。P5/P6 入链密集且互相引用, "
      "形成'权威节点'。幂迭代约 20-30 步即收敛, 体现了马尔可夫链平稳分布的快速可达性。")

if __name__ == "__main__":
    pass  # 脚本级代码已执行
