"""推荐系统核心算法最小实现验证（教学用，单文件可跑）。
覆盖：矩阵分解召回 / FM 二阶交叉 / 双塔DSSM / DIN目标注意力 / MMoE多任务 / DPP多样性重排。
所有实现用 PyTorch，数据用随机合成，目标是验证维度/损失/数值合理性。
"""
import torch, torch.nn as nn, torch.nn.functional as F
import numpy as np
torch.manual_seed(0); np.random.seed(0)

# ---------- 1) 矩阵分解召回 (SVD/MF) ----------
class MFRecall(nn.Module):
    """R ≈ U V^T, 用户/物品各一个 embedding，点积预测评分。"""
    def __init__(self, n_user, n_item, k=32):
        super().__init__()
        self.U = nn.Embedding(n_user, k)
        self.V = nn.Embedding(n_item, k)
        nn.init.normal_(self.U.weight, std=0.1); nn.init.normal_(self.V.weight, std=0.1)
    def forward(self, u, i):
        return (self.U(u) * self.V(i)).sum(-1)   # 内积打分

# ---------- 2) FM 二阶交叉 ----------
class FM(nn.Module):
    """FM: y = w0 + <w,x> + sum_{i<j}<v_i,v_j>x_i x_j
    二阶项高效计算: 0.5*[(sum v_i x_i)^2 - sum (v_i x_i)^2]"""
    def __init__(self, n_feat, k=16):
        super().__init__()
        self.w0 = nn.Parameter(torch.zeros(1))
        self.w = nn.Embedding(n_feat, 1)
        self.v = nn.Embedding(n_feat, k)
    def forward(self, x_idx):                 # x_idx: (B, F) 特征 id
        emb = self.v(x_idx)                   # (B, F, k)
        lin = self.w(x_idx).squeeze(-1).sum(-1) + self.w0
        sum_then_sq = emb.sum(1).pow(2).sum(-1)
        sq_then_sum = emb.pow(2).sum(1).sum(-1)
        cross = 0.5 * (sum_then_sq - sq_then_sum)
        return lin + cross

# ---------- 3) 双塔 DSSM (召回) ----------
class TwoTower(nn.Module):
    """user_tower 和 item_tower 各自 MLP，输出做内积/余弦。
    工业要点: 物品塔可离线算好，在线只算用户塔 + ANN 检索。"""
    def __init__(self, u_dim, i_dim, out=64):
        super().__init__()
        self.u_tower = nn.Sequential(nn.Linear(u_dim,128), nn.ReLU(), nn.Linear(128,out))
        self.i_tower = nn.Sequential(nn.Linear(i_dim,128), nn.ReLU(), nn.Linear(128,out))
    def forward(self, u, i):                   # 返回两个向量，训练用 in-batch softmax
        return F.normalize(self.u_tower(u), dim=-1), F.normalize(self.i_tower(i), dim=-1)

def inbatch_softmax_loss(u_vec, i_vec, temp=0.05):
    """召回常用: batch 内其它物品当负样本。logits = u @ i^T / temp"""
    logits = u_vec @ i_vec.t() / temp          # (B, B)
    labels = torch.arange(u_vec.size(0), device=u_vec.device)
    return F.cross_entropy(logits, labels)

# ---------- 4) DIN 目标注意力 (排序, 序列特征) ----------
class TargetAttention(nn.Module):
    """DIN: 候选物品作为 query, 对用户历史序列做 attention pool。
    比直接 mean-pool 更能捕捉'与当前候选相关的兴趣'。"""
    def __init__(self, k=32, hidden=64):
        super().__init__()
        # 注意力网络: 输入 [out_product | difference] -> 标量
        self.attn = nn.Sequential(nn.Linear(2*k, hidden), nn.ReLU(), nn.Linear(hidden,1))
    def forward(self, seq, cand):              # seq:(B,L,k) cand:(B,k)
        cand_e = cand.unsqueeze(1).expand_as(seq)
        inp = torch.cat([seq*cand_e, seq-cand_e], -1)   # (B,L,2k)  外积简化为乘 + 差
        w = self.attn(inp).squeeze(-1)         # (B,L)
        w = F.softmax(w, dim=1).unsqueeze(-1)  # (B,L,1)
        return (w * seq).sum(1)                # (B,k) 加权和

# ---------- 5) MMoE 多任务 (排序) ----------
class MMoE(nn.Module):
    """k 个共享专家 + 每个任务一个 gate(softmax over experts)。
    解决多任务冲突(seesaw), PLE 进一步用任务专属专家。"""
    def __init__(self, in_dim, n_expert=4, tasks=2, expert_h=64):
        super().__init__()
        self.experts = nn.ModuleList(
            [nn.Sequential(nn.Linear(in_dim,expert_h),nn.ReLU(),nn.Linear(expert_h,expert_h)) for _ in range(n_expert)])
        self.gates = nn.ModuleList([nn.Linear(in_dim, n_expert) for _ in range(tasks)])
        self.towers = nn.ModuleList([nn.Linear(expert_h,1) for _ in range(tasks)])
    def forward(self, x):
        e = torch.stack([ex(x) for ex in self.experts], 1)   # (B, n_expert, h)
        outs = []
        for g, t in zip(self.gates, self.towers):
            w = F.softmax(g(x), -1).unsqueeze(-1)            # (B,n_expert,1)
            outs.append(t((w*e).sum(1)))                     # (B,1)
        return outs

# ---------- 6) DPP 多样性重排 ----------
def dpp_greedy(scores, sim, k=5, eps=1e-12):
    """Determinant Point Process 贪心版: 既高相关又互相不相似。
    选 max log det(K_S), K = diag(score) * sim * diag(score)。
    维护已选核矩阵的 Cholesky 分解 L, 每步增量计算 log-det 增益, O(k^2)。"""
    s = np.asarray(scores, float)
    K = (s[:, None] * sim) * s[None, :]              # K[i,j]=s_i*sim_ij*s_j, PSD
    n = len(s)
    selected = [int(np.argmax(np.diag(K)))]          # 第一步: max K_ii = max s_i^2
    L = np.array([[np.sqrt(K[selected[0], selected[0]] + eps)]])
    while len(selected) < k:
        best_gain, best_j, best_u = -np.inf, -1, None
        for j in range(n):
            if j in selected: continue
            u = np.linalg.solve(L, K[j, selected])   # 解下三角 L u = e
            gain = K[j, j] - u @ u                   # log-det 增益 = ||u_new||^2
            if gain > best_gain:
                best_gain, best_j, best_u = gain, j, u
        selected.append(best_j)
        L = np.block([[L, np.zeros((L.shape[0], 1))],
                      [best_u[None, :], np.sqrt(best_gain + eps)]])
    return selected

# ============ 跑通验证 ============
def run():
    print("=== 1) 矩阵分解召回 ===")
    mf = MFRecall(n_user=1000, n_item=5000, k=32)
    u = torch.randint(0,1000,(64,)); i = torch.randint(0,5000,(64,))
    scores = mf(u,i)
    print(f"  MF 打分 shape={tuple(scores.shape)}, 均值={scores.mean().item():.4f}, 标准差={scores.std().item():.4f}")
    # 一轮 SGD
    loss = F.mse_loss(scores, torch.rand(64))   # 用随机目标验证可训练
    loss.backward()
    print(f"  一轮 MSE loss = {loss.item():.4f}, U.grad 非零比例 = {(mf.U.weight.grad!=0).float().mean().item():.2f}")

    print("\n=== 2) FM 二阶交叉 ===")
    fm = FM(n_feat=2000, k=16)
    x = torch.randint(0,2000,(64,10))           # (B=64, F=10个稀疏特征)
    y = fm(x)
    print(f"  FM 打分 shape={tuple(y.shape)}, 均值={y.mean().item():.4f}")
    print(f"  FM 二阶交叉项验证: 若所有x相同, 二阶项=0.5*k*(F^2-F)*v^2")

    print("\n=== 3) 双塔 DSSM (in-batch softmax) ===")
    tt = TwoTower(u_dim=50, i_dim=80, out=64)
    u_in = torch.randn(64,50); i_in = torch.randn(64,80)
    uv, iv = tt(u_in, i_in)
    loss = inbatch_softmax_loss(uv, iv)
    print(f"  双塔向量 shape: u={tuple(uv.shape)} i={tuple(iv.shape)}")
    print(f"  in-batch softmax loss = {loss.item():.4f} (batch=64时随机≈ln(64)={np.log(64):.3f})")

    print("\n=== 4) DIN 目标注意力 ===")
    attn = TargetAttention(k=32, hidden=64)
    seq = torch.randn(64, 50, 32); cand = torch.randn(64,32)   # 50个历史行为
    pool = attn(seq, cand)
    print(f"  DIN 加权池化 shape={tuple(pool.shape)} (用户历史长度被压缩为1向量)")
    # 验证: 改变候选, 池化结果应该改变 (兴趣随候选变化)
    cand2 = cand + torch.randn_like(cand)*0.5
    pool2 = attn(seq, cand2)
    print(f"  换候选后池化向量变化 L2 = {(pool-pool2).norm(dim=-1).mean().item():.4f} (应明显>0)")

    print("\n=== 5) MMoE 多任务 ===")
    mmoe = MMoE(in_dim=40, n_expert=4, tasks=2)
    x_in = torch.randn(64,40)
    ctr, cvr = mmoe(x_in)
    print(f"  任务1(CTR) shape={tuple(ctr.shape)}, 任务2(CVR) shape={tuple(cvr.shape)}")
    print(f"  gate 权重可学, 解决 CTR/CVR 冲突 (典型 seesaw 问题)")

    print("\n=== 6) DPP 多样性重排 ===")
    np.random.seed(1)
    cand_scores = np.random.rand(20)              # 20个候选的相关性
    feat = np.random.randn(20, 16); feat = feat/np.linalg.norm(feat,axis=1,keepdims=True)
    sim = feat @ feat.T                           # 余弦相似度矩阵
    sel = dpp_greedy(cand_scores, sim, k=5)
    greedy = list(np.argsort(-cand_scores)[:5])
    def div(s): 
        return sum(sim[a,b] for ai,a in enumerate(s) for b in s[ai+1:])/(len(s)*(len(s)-1)/2)
    print(f"  纯贪心(只看分数) top5: {greedy}, 平均相似度={div(greedy):.3f}")
    print(f"  DPP top5:               {sel}, 平均相似度={div(sel):.3f}")
    print(f"  DPP 分数和={cand_scores[sel].sum():.3f} vs 贪心={cand_scores[greedy].sum():.3f}")
    print("  注: 随机数据无冗余时 DPP≈贪心(不损失相关性); 冗余场景见 03_dpp_demo.py")

if __name__ == "__main__":
    run()
