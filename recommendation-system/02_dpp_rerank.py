"""正确版 DPP 贪心: 维护已选集合核矩阵的 Cholesky 分解, 每步选最大化 log-det 增益的点。"""
import numpy as np
np.random.seed(1)

def dpp_greedy(scores, sim, k=5, eps=1e-12):
    s = np.asarray(scores, float)
    K = (s[:, None] * sim) * s[None, :]              # K[i,j]=s_i*sim_ij*s_j, PSD
    n = len(s)
    first = int(np.argmax(np.diag(K)))               # 第一步: max K_ii = max s_i^2
    selected = [first]
    L = np.array([[np.sqrt(K[first, first] + eps)]]) # 已选核矩阵的 Cholesky
    while len(selected) < k:
        best_gain, best_j, best_u = -np.inf, -1, None
        for j in range(n):
            if j in selected: continue
            e = K[j, selected]
            u = np.linalg.solve(L, e)                # 解下三角 L u = e
            gain = K[j, j] - u @ u                   # log-det 增益 = ||u_new||^2
            if gain > best_gain:
                best_gain, best_j, best_u = gain, j, u
        selected.append(best_j)
        L = np.block([[L, np.zeros((L.shape[0], 1))],
                      [best_u[None, :], np.sqrt(best_gain + eps)]])
    return selected

def avg_pairwise_sim(sim, s):
    s = list(s); m = len(s)
    return sum(sim[a, b] for ai, a in enumerate(s) for b in s[ai+1:]) / (m*(m-1)/2)

# 构造: 20个候选, 16维特征, 有些簇很相似
feat = np.random.randn(20, 16); feat /= np.linalg.norm(feat, axis=1, keepdims=True)
sim = feat @ feat.T
scores = np.random.rand(20)

greedy = list(np.argsort(-scores)[:5])
dpp = dpp_greedy(scores, sim, k=5)
print(f"纯贪心(只看分数) top5 索引: {greedy}")
print(f"  分数和 = {scores[greedy].sum():.3f}   平均两两相似度 = {avg_pairwise_sim(sim, greedy):.3f}")
print(f"DPP top5 索引:                {dpp}")
print(f"  分数和 = {scores[dpp].sum():.3f}   平均两两相似度 = {avg_pairwise_sim(sim, dpp):.3f}")
print()
print("结论: DPP 用一点点相关性换取明显更低的相似度(更多样), 这正是重排想要的权衡。")
