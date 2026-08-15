import numpy as np
np.random.seed(7)

def dpp_greedy(scores, sim, k=4, eps=1e-12):
    s = np.asarray(scores, float)
    K = (s[:, None] * sim) * s[None, :]
    n = len(s)
    selected = [int(np.argmax(np.diag(K)))]
    L = np.array([[np.sqrt(K[selected[0], selected[0]] + eps)]])
    while len(selected) < k:
        best_gain, best_j, best_u = -np.inf, -1, None
        for j in range(n):
            if j in selected: continue
            u = np.linalg.solve(L, K[j, selected]); gain = K[j, j] - u @ u
            if gain > best_gain: best_gain, best_j, best_u = gain, j, u
        selected.append(best_j)
        L = np.block([[L, np.zeros((L.shape[0],1))],[best_u[None,:], np.sqrt(best_gain+eps)]])
    return selected

# 场景: 候选0,1,2 是"同一爆款视频的3个相似副本", 分数都很高且互相相似度0.9
# 候选3,4,5,6 是分数稍低但彼此不同(相似度~0)的内容
feat = np.eye(7, 6)                      # 7个候选, 6维
feat[0] = feat[1] = feat[2] = np.array([1,0,0,0,0,0])   # 前3个副本高度相似
feat[3] = np.array([0,1,0,0,0,0])
feat[4] = np.array([0,0,1,0,0,0])
feat[5] = np.array([0,0,0,1,0,0])
feat[6] = np.array([0,0,0,0,1,0])
sim = feat @ feat.T
scores = np.array([0.9, 0.9, 0.88, 0.7, 0.7, 0.7, 0.7])  # 副本分数高

def aps(sim,s):
    s=list(s); m=len(s); return sum(sim[a,b] for ai,a in enumerate(s) for b in s[ai+1:])/(m*(m-1)/2)

greedy = list(np.argsort(-scores)[:4])
dpp = dpp_greedy(scores, sim, k=4)
print("场景: 候选0/1/2是同一爆款的3个高分相似副本(相似度0.9), 3-6是分数略低但互不相似的内容")
print(f"  纯贪心 top4 = {greedy}  分数和={scores[greedy].sum():.2f} 平均相似度={aps(sim,greedy):.2f}  ← 3个冗余副本挤掉了多样性")
print(f"  DPP    top4 = {dpp}  分数和={scores[dpp].sum():.2f} 平均相似度={aps(sim,dpp):.2f}   ← 只保留1个副本, 腾出位置给多样内容")
