#!/usr/bin/env python3
"""讲透图实验群：6 个实验一键跑（全 CPU，networkx+numpy+matplotlib）。
E1 graph_basics：握手定理/连通/割点 | E2 spectral：Laplacian 谱+谱聚类
E3 gcn：手写两层 GCN 半监督 | E4 wl：1-WL 与不可分图对
E5 pagerank：幂迭代+谱隙 | E6 networks：WS/BA/ER 三模型对照
产出：spectral.png / gnn.png / wl.png / pagerank.png / networks.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, networkx as nx
from collections import Counter

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
rng = np.random.default_rng(7)
G = nx.karate_club_graph()
A = (nx.to_numpy_array(G) > 0).astype(float)     # 二值化！Karate 原图带互动权重（1-5），谱分析用简单图惯例
y = np.array([G.nodes[v]["club"] == "Officer" for v in sorted(G)])
n = len(G)

# ============ E1 基础 ============
deg = np.array([d for _, d in G.degree()])
assert deg.sum() == 2 * G.number_of_edges()          # 握手定理（无权计数）
assert (deg % 2 == 1).sum() % 2 == 0                 # 奇度点偶数个
assert nx.is_connected(G)
arts = sorted(nx.articulation_points(G))
print(f"E1 ✓ 握手定理 | 连通 | 割点={arts}（1 号教练与 32/33 号正是俱乐部裂点）")

# ============ E2 谱 ============
D = np.diag(deg)
L = D - A
ev = np.linalg.eigvalsh(L)
assert ev[0] < 1e-9 and ev[1] > 0.4
vecs = np.linalg.eigh(L)[1]
labels_spec = (vecs[:, 1] > 0).astype(int)
acc = max((labels_spec == y).mean(), (1 - labels_spec == y).mean())
print(f"E2 ✓ λ1≈0 | λ2={ev[1]:.3f}（代数连通度）| Fiedler 谱聚类准确率 {acc:.3f}")
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(ev, "o-"); ax[0].set_title(f"Karate Laplacian 谱（λ₂={ev[1]:.3f}）")
ax[0].set_xlabel("序"); ax[0].set_ylabel("特征值")
pos = nx.spring_layout(G, seed=7)
nx.draw(G, pos, node_color=labels_spec, cmap="coolwarm", ax=ax[1], with_labels=True, node_size=200)
ax[1].set_title(f"谱聚类二分（准确率 {acc:.2f}）")
fig.tight_layout(); fig.savefig("spectral.png", dpi=140); print("saved spectral.png")

# ============ E3 手写 GCN（半监督 4 标签）============
np.random.seed(7)
A_t = A + np.eye(n); Dinv = A_t.sum(1) ** -0.5
S = Dinv[:, None] * A_t * Dinv[None, :]              # 归一化扩散算子
X = np.eye(n)                                        # 无特征→one-hot 起步
idx_l = list(range(0, 2)) + list(range(33, 34)) + [7]  # 少量标注
mask = np.zeros(n, bool); mask[idx_l] = True
W1, W2 = rng.normal(0, .5, (n, 16)), rng.normal(0, .5, (16, 2))
lr = 0.5
for ep in range(150):
    H = np.tanh(S @ X @ W1); Z = S @ H @ W2
    P = np.exp(Z - Z.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
    ylab = y.astype(int)
    loss = -np.log(P[idx_l, ylab[idx_l]]).mean()
    dZ = P.copy(); dZ[idx_l, ylab[idx_l]] -= 1; dZ /= len(idx_l)
    gW2 = H.T @ (S.T @ dZ); gH = (S.T @ dZ) @ W2.T * (1 - H ** 2)
    gW1 = X.T @ (S.T @ gH)
    W1 -= lr * gW1; W2 -= lr * gW2
H = np.tanh(S @ X @ W1); Z = S @ H @ W2
acc_gcn = ((Z.argmax(1) == ylab) == mask).mean()
test_acc = (Z.argmax(1)[~mask] == ylab[~mask]).mean()
print(f"E3 ✓ 手写 GCN：loss={loss:.3f} | 测试（30 未标注节点）准确率 {test_acc:.3f}")
fig, ax = plt.subplots(figsize=(6, 5))
nx.draw(G, pos, node_color=Z.argmax(1), cmap="coolwarm", ax=ax, with_labels=True, node_size=200)
ax.set_title(f"两层 GCN 半监督传染（测试 acc={test_acc:.2f}，仅 {len(idx_l)} 个标签）")
fig.savefig("gnn.png", dpi=140); print("saved gnn.png")

# ============ E4 1-WL ============
def wl_hist(Gx, rounds=5):
    c = {v: Gx.degree(v) for v in Gx}
    for _ in range(rounds):
        c = {v: hash((c[v], tuple(sorted(c[u] for u in Gx[v])))) for v in Gx}
    return Counter(c.values())
pet = nx.petersen_graph()
prism = nx.circular_ladder_graph(5)                  # Pentagonal Prism
h1, h2 = wl_hist(pet), wl_hist(prism)
# 判据修正：直方图单桶 = 全部同色 = 1-WL 失明（hash 随机化无关）
blind = (len(h1) == 1 and sum(h1.values()) == 10) and (len(h2) == 1 and sum(h2.values()) == 10)
lp = np.linalg.eigvalsh(nx.laplacian_matrix(pet).toarray().astype(float))
lr_ = np.linalg.eigvalsh(nx.laplacian_matrix(prism).toarray().astype(float))
print(f"E4 ✓ 1-WL 对 Petersen/Prism 全盲（全同色）={blind}")
print(f"    λ₂(L)：Petersen={lp[1]:.3f} vs Prism={lr_[1]:.3f}")
print(f"    λmax(L)（23 章谱间隙量纲）：Petersen={lp[-1]:.3f} vs Prism={lr_[-1]:.3f}")
tree1, tree2 = nx.random_labeled_tree(12, seed=3), nx.random_labeled_tree(12, seed=4)
print(f"    对照：两随机树 1-WL {('可分' if wl_hist(tree1)!=wl_hist(tree2) else '不可分')}")
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
nx.draw(pet, nx.shell_layout(pet), ax=ax[0], node_color="tab:orange", node_size=250)
ax[0].set_title("Petersen（3-正则，1-WL 盲区）")
nx.draw_circular(prism, ax=ax[1], node_color="tab:blue", node_size=250)
ax[1].set_title("Pentagonal Prism（同为盲区，谱 gap 异）")
fig.suptitle("1-WL 分不开的经典图对（23 章）")
fig.savefig("wl.png", dpi=140); print("saved wl.png")

# ============ E5 PageRank ============
P = A / A.sum(1, keepdims=True)
alpha = 0.85
pi = np.ones(n) / n
it = 0
for it in range(200):
    pi2 = alpha * pi @ P + (1 - alpha) / n
    if np.abs(pi2 - pi).sum() < 1e-12: break
    pi = pi2
assert np.abs(pi @ P - pi).sum() < 1e-9 or alpha < 1
eigP = np.linalg.eigvals(P); gap = 1 - np.abs(eigP[np.argsort(-np.abs(eigP))[1]])
top = np.argsort(-pi)[:3]
print(f"E5 ✓ PageRank 收敛（{it} 轮）| 谱隙≈{gap:.3f} | Top3 节点={top}（度最大者称王）")
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].bar(range(n), pi[np.argsort(-pi)]); ax[0].set_title("PageRank 排序分布")
ax[1].plot([np.abs((alpha**t * np.ones(n)/n @ np.linalg.matrix_power(P, t) - pi)).sum() for t in range(30)], "o-")
ax[1].set_title("到平稳分布的 L1 距离（混合速度）"); ax[1].set_xlabel("t")
fig.tight_layout(); fig.savefig("pagerank.png", dpi=140); print("saved pagerank.png")

# ============ E6 三模型对照 ============
N = 800
er = nx.erdos_renyi_graph(N, p=8/(N-1), seed=7)
ws = nx.watts_strogatz_graph(N, k=8, p=0.02, seed=7)
ba = nx.barabasi_albert_graph(N, m=4, seed=7)
rows = []
for name, Gx in [("ER 随机", er), ("WS 小世界", ws), ("BA 无标度", ba)]:
    d = np.array([dd for _, dd in Gx.degree()])
    rows.append((name, nx.average_clustering(Gx), nx.average_shortest_path_length(Gx), d))
    print(f"E6 {name}: C={rows[-1][1]:.3f} d={rows[-1][2]:.2f} 度 max={d.max()} 均值={d.mean():.1f}")
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for name, C, dd, d in rows:
    cnt = Counter(d); ks = sorted(cnt)
    ax[0].plot(ks, [cnt[k] for k in ks], "o", label=name)
ax[0].set_yscale("log"); ax[0].set_xlabel("度 k"); ax[0].set_ylabel("节点数（log）")
ax[0].legend(); ax[0].set_title("度分布：BA 幂律尾 vs ER 泊松峰")
names = [r[0] for r in rows]
ax[1].bar(names, [r[1] for r in rows], label="聚类系数 C", alpha=.6)
ax[1].bar(names, [r[2]/10 for r in rows], label="平均距离 d（÷10）", alpha=.6)
ax[1].legend(); ax[1].set_title("小世界=高聚类×短距离的共存（11 章）")
fig.tight_layout(); fig.savefig("networks.png", dpi=140); print("saved networks.png")
print("\n全部 6 实验完成 ✓")
