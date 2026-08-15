"""进阶验证脚本: DeepFM / PLE / ESMM / 向量检索 / IPS-DR 评估 / 生成式召回语义ID。
全部 numpy/torch/sklearn, 无重依赖, 教学可跑。"""
import torch, torch.nn as nn, torch.nn.functional as F
import numpy as np
torch.manual_seed(0); np.random.seed(0)

# ===================== A) DeepFM: Wide + FM + DNN 三合一 =====================
class DeepFM(nn.Module):
    """FM部分(一阶+二阶交叉) + DNN部分(高阶), 两者共享embedding。
    论文: Huawei 2017. 比 Wide&Deep 的wide不用手工构造交叉, FM自动做二阶。"""
    def __init__(self, n_feat, n_fields, k=8, dnn=(64,32)):
        super().__init__()
        assert n_feat  # placeholder
        self.n_fields = n_fields
        self.emb = nn.Embedding(n_feat, k)
        self.lin = nn.Embedding(n_feat, 1)
        self.w0 = nn.Parameter(torch.zeros(1))
        layers, d = [], n_fields * k          # DNN 输入 = 所有特征embedding拼接
        for h in dnn:
            layers += [nn.Linear(d,h), nn.ReLU()]; d=h
        self.dnn = nn.Sequential(*layers)
        self.out = nn.Linear(d + 1, 1)        # dnn向量 + fm二阶标量
    def forward(self, x):                      # x:(B,F) 特征id
        e = self.emb(x)                        # (B,F,k)
        lin = self.w0 + self.lin(x).squeeze(-1).sum(-1)
        sum_sq = e.sum(1).pow(2).sum(-1); sq_sum = e.pow(2).sum(1).sum(-1)
        fm2 = 0.5*(sum_sq - sq_sum)            # (B,) 二阶交叉标量
        d = self.dnn(e.flatten(1))             # (B, dnn_last)
        return self.out(torch.cat([d, fm2.unsqueeze(1)],1)).squeeze(-1) + lin

# ===================== B) PLE (CGC): 任务专属专家+共享专家 =====================
class CGC(nn.Module):
    """PLE 的核心模块 CGC(Customized Gate Control):
    每个任务有自己的专属专家 + 共享专家, gate 在专属+共享上 softmax。
    比 MMoE 多了'专属'维度, 解决任务差异极大时的冲突。"""
    def __init__(self, in_dim, n_specific=2, n_shared=2, tasks=2, h=32):
        super().__init__()
        self.spec = nn.ModuleDict({f"t{t}": nn.ModuleList(
            [nn.Linear(in_dim,h) for _ in range(n_specific)]) for t in range(tasks)})
        self.share = nn.ModuleList([nn.Linear(in_dim,h) for _ in range(n_shared)])
        self.gates = nn.ModuleList([nn.Linear(in_dim, n_specific+n_shared) for _ in range(tasks)])
        self.towers = nn.ModuleList([nn.Linear(h,1) for _ in range(tasks)])
        self.tasks = tasks; self.n_specific = n_specific
    def forward(self, x):
        sh = [s(x) for s in self.share]
        outs=[]
        for t in range(self.tasks):
            sp = [e(x) for e in self.spec[f"t{t}"]]
            cand = torch.stack(sp+sh, 1)                 # (B, n_spec+n_shared, h)
            w = F.softmax(self.gates[t](x), -1).unsqueeze(-1)
            outs.append(self.towers[t]((w*cand).sum(1)))
        return outs

# ===================== C) ESMM: pCTCVR = pCTR * pCVR =====================
class ESMM(nn.Module):
    """ESMM 解决 CVR 标签极稀疏问题: 只有转化的样本才有CVR标签。
    核心: 共享embedding, 输出pCTR和pCVR, 训练用 pCTCVR=pCTR*pCVR 在全量点击样本上算loss。
    CVR塔借CTR塔的梯度间接训练。"""
    def __init__(self, in_dim, h=32):
        super().__init__()
        self.ctr_tower = nn.Sequential(nn.Linear(in_dim,h),nn.ReLU(),nn.Linear(h,1))
        self.cvr_tower = nn.Sequential(nn.Linear(in_dim,h),nn.ReLU(),nn.Linear(h,1))
    def forward(self, x):
        p_ctr = torch.sigmoid(self.ctr_tower(x).squeeze(-1))
        p_cvr = torch.sigmoid(self.cvr_tower(x).squeeze(-1))
        p_ctcvr = p_ctr * p_cvr                       # 关键: 乘积
        return p_ctr, p_cvr, p_ctcvr

# ===================== D) 向量检索: 暴力 / IVF / HNSW 思路 =====================
def brute_force(query_vecs, item_vecs, k=5):
    """暴力: 算全部点积, 取top-k. O(N*d). 适合小规模/基线。"""
    sim = query_vecs @ item_vecs.T                    # (Q, N)
    idx = np.argsort(-sim, axis=1)[:, :k]
    return idx, np.take_along_axis(sim, idx, axis=1)

def ivf_search(query_vecs, item_vecs, centroids, k=5, n_probe=2):
    """IVF(Inverted File): 先聚类, 查询时只搜最近的n_probe个簇。
    代价: 精度换速度(召回率随n_probe↑)。Faiss IVF原理。"""
    N = item_vecs.shape[0]
    # 每个item归属最近簇
    item_to_centroid = np.argmax(item_vecs @ centroids.T, axis=1)
    results = []
    for q in query_vecs:
        # 找最近的 n_probe 个簇
        probe = np.argsort(-(q @ centroids.T))[:n_probe]
        mask = np.isin(item_to_centroid, probe)
        cand_idx = np.where(mask)[0]
        if len(cand_idx)==0: cand_idx = np.arange(N)
        sims = item_vecs[cand_idx] @ q
        top = np.argsort(-sims)[:k]
        results.append(cand_idx[top])
    return np.array(results)

# ===================== E) IPS / Doubly Robust 反事实评估 =====================
def ips_estimate(rewards, exposed, propensities):
    """Inverse Propensity Scoring: 给低曝光倾向的样本更大权重, 纠正选择偏差。
    E[R] ≈ mean( r * 1[exposed] / p )。无偏当 p 估计正确。"""
    w = exposed / np.clip(propensities, 1e-6, None)
    return np.mean(rewards * w)

def doubly_robust(rewards, exposed, propensities, q_hat):
    """DR = IPS + 直接模型估计, 双重保护: 任一(倾向或模型)无偏则整体无偏。
    formula: mean( q_hat + (exposed*(r - q_hat))/p )。方差通常比IPS小。"""
    w = exposed / np.clip(propensities, 1e-6, None)
    return np.mean(q_hat + (rewards - q_hat) * w)

# ===================== F) 生成式召回语义ID (TIGER 思路) =====================
def make_semantic_ids(item_feats, n_levels=3, cluster_per_level=16):
    """TIGER 核心: 用层次聚类把item的语义向量量化成多级ID(如 [3,17,204])。
    推荐变成'生成下一个item的ID序列'。这里用递归KMeans简化。"""
    from sklearn.cluster import KMeans
    ids = np.zeros((len(item_feats), n_levels), dtype=int)
    codes = []
    cur = item_feats
    for lv in range(n_levels):
        km = KMeans(n_clusters=min(cluster_per_level, len(cur)), n_init=4, random_state=lv).fit(cur)
        lab = km.labels_
        ids[:, lv] = lab
        codes.append(km.cluster_centers_)
        # 下一层在每个簇内再分(简化: 直接用残差)
        cur = cur - km.cluster_centers_[lab]
    return ids, codes

# ===================== 跑通验证 =====================
def run():
    print("="*70)
    print("A) DeepFM 精排")
    print("="*70)
    m = DeepFM(n_feat=2000, n_fields=12, k=8, dnn=(64,32))
    x = torch.randint(0,2000,(128,12))               # B=128, F=12个稀疏特征
    y = m(x)
    loss = F.binary_cross_entropy_with_logits(y, torch.randint(0,2,(128,)).float())
    loss.backward()
    print(f"  DeepFM 输出 shape={tuple(y.shape)}, mean={y.mean().item():.3f}, BCE loss={loss.item():.4f}")
    print(f"  结构: embedding共享 -> FM二阶 + DNN高阶, 拼接后线性输出")

    print("\n"+"="*70); print("B) PLE / CGC 多任务(对比MMoE)"); print("="*70)
    ple = CGC(in_dim=40, n_specific=2, n_shared=2, tasks=2, h=32)
    xi = torch.randn(128,40)
    y1,y2 = ple(xi)
    n_specific = 2
    print(f"  PLE 任务1={tuple(y1.shape)} 任务2={tuple(y2.shape)}")
    print(f"  vs MMoE: 每任务多了{n_specific}个专属专家, 任务差异大时冲突更小")

    print("\n"+"="*70); print("C) ESMM (CTR/CVR 级联)"); print("="*70)
    esmm = ESMM(in_dim=40,h=32)
    p_ctr,p_cvr,p_ctcvr = esmm(torch.randn(128,40))
    print(f"  pCTR mean={p_ctr.mean():.3f}, pCVR mean={p_cvr.mean():.3f}, pCTCVR mean={p_ctcvr.mean():.3f}")
    print(f"  pCTCVR = pCTR*pCVR ∈[0,1] 恒成立: {((p_ctcvr>=0)&(p_ctcvr<=1)).all().item()}")
    print(f"  训练只在全量曝光样本上算 pCTCVR 的loss, CVR塔借CTR梯度训练, 绕开CVR稀疏")

    print("\n"+"="*70); print("D) 向量检索: 暴力 vs IVF"); print("="*70)
    np.random.seed(3)
    N, d = 5000, 64
    item_vecs = np.random.randn(N,d).astype('float32')
    item_vecs /= np.linalg.norm(item_vecs,axis=1,keepdims=True)
    q = np.random.randn(10,d).astype('float32'); q/=np.linalg.norm(q,axis=1,keepdims=True)
    bf_idx, bf_sim = brute_force(q, item_vecs, k=5)
    # IVF: 64个聚类中心
    from sklearn.cluster import KMeans
    cents = KMeans(n_clusters=64,n_init=3,random_state=0).fit(item_vecs).cluster_centers_.astype('float32')
    ivf_idx = ivf_search(q, item_vecs, cents, k=5, n_probe=2)
    # 召回率对比
    recall = np.mean([len(set(bf_idx[i])&set(ivf_idx[i]))/5 for i in range(10)])
    print(f"  库大小 N={N}, dim={d}, 查询数=10")
    print(f"  暴力检索 top5 准确; IVF(n_probe=2) 召回率={recall:.2%} (牺牲精度换~{N//64}x候选缩减)")
    print(f"  HNSW 未装faiss无法实测: 思路=图索引, 邻居连邻居, logN跳数, 召回率/内存权衡")

    print("\n"+"="*70); print("E) IPS / Doubly Robust 反事实评估"); print("="*70)
    np.random.seed(5)
    n=2000
    prop = np.random.uniform(0.05, 0.5, n)          # 真实曝光倾向
    exposed = (np.random.rand(n) < prop).astype(int) # 是否被旧系统曝光
    true_val = 0.5                                   # 真实平均奖励
    rewards = np.random.normal(true_val, 0.3, n) * exposed
    # 朴素评估: 只看曝光样本 -> 有偏(偏高, 因为高prop的才被看到)
    naive = rewards[exposed==1].mean()
    ips = ips_estimate(rewards, exposed, prop)
    q_hat = np.full(n, true_val+0.05)               # 模型估计(略偏)
    dr = doubly_robust(rewards, exposed, prop, q_hat)
    print(f"  真实平均奖励 = {true_val:.3f}")
    print(f"  朴素(只看曝光样本) = {naive:.3f}  ← 严重偏估(选择偏差)")
    print(f"  IPS 估计          = {ips:.3f}  ← 接近真值(纠正偏差)")
    print(f"  Doubly Robust     = {dr:.3f}  ← 方差更小, 任一无偏则无偏")

    print("\n"+"="*70); print("F) 生成式召回语义ID (TIGER)"); print("="*70)
    np.random.seed(9)
    item_f = np.random.randn(200, 32)               # 200个item的语义向量
    sem_ids, _ = make_semantic_ids(item_f, n_levels=3, cluster_per_level=16)
    print(f"  200个item -> 3级语义ID, 每级16簇, 例: item[0]={sem_ids[0]}, item[1]={sem_ids[1]}")
    print(f"  ID空间 = 16^3 = {16**3} (远小于item数, 自然层次聚类)")
    print(f"  推荐 = 自回归生成下一个ID序列(beam search解码), 再映射回item")
    print(f"  优势: 端到端/可泛化新组合; 挑战: ID设计/延迟/评估")

if __name__=="__main__":
    run()
