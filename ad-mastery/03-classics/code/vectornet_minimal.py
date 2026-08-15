"""VectorNet 玩具版: GNN 聚合 agent+地图向量 -> 多模态轨迹预测 (K=3, minADE)
演示: 预测层如何用'向量化输入+图网络'工作, 以及多模态输出+minADE训练
"""
import torch, torch.nn as nn
import torch.nn.functional as F
torch.manual_seed(0)

class VectorNet(nn.Module):
    def __init__(self, in_dim=4, hid=64, K=3, T=4):
        super().__init__()
        self.K, self.T = K, T
        self.mlp = nn.Sequential(nn.Linear(in_dim, hid), nn.ReLU(), nn.Linear(hid, hid))
        self.gnn = nn.Sequential(nn.Linear(hid*2, hid), nn.ReLU(), nn.Linear(hid, hid))  # 消息传递
        self.head = nn.Linear(hid, K*T*2)   # K条轨迹 × T步 × xy
        self.score = nn.Linear(hid, K)      # 每条轨迹的置信度

    def forward(self, agent_hist, map_vec):
        """agent_hist: [B,4] (px,py,vx,vy)  map_vec: [B,M,4] 地图线段向量"""
        a = self.mlp(agent_hist)                                  # [B,hid]
        m = self.mlp(map_vec).mean(1)                             # [B,hid] 地图池化
        h = self.gnn(torch.cat([a, m], -1))                       # agent<->map 交互
        traj = self.head(h).view(-1, self.K, self.T, 2)           # [B,K,T,2]
        score = self.score(h).softmax(-1)                         # [B,K]
        return traj, score

def make_data():
    """合成: 直行/左转/右转三模态, 由地图向量(车道走向)决定概率"""
    B = 32
    hist = torch.rand(B, 4) * 2 - 1                # 归一化历史
    # 三种未来: 直行/左转/右转
    t = torch.arange(1, 5).float()
    straight = torch.stack([torch.zeros(4), t*0.3], -1)
    left     = torch.stack([-t*0.3, t*0.3], -1)
    right    = torch.stack([t*0.3, t*0.3], -1)
    modes = torch.stack([straight, left, right])   # [3,T,2]
    # 地图向量编码"车道走向" -> 决定真实模态
    map_dir = torch.randint(0, 3, (B,))
    maps = torch.zeros(B, 4, 4)
    maps[torch.arange(B), :, :2] = modes[map_dir, -1][:, None, :]  # 地图末段指向模态方向
    gt = modes[map_dir]                             # [B,T,2]
    return hist, maps, gt

m = VectorNet(); opt = torch.optim.Adam(m.parameters(), lr=3e-3)
print("训练 VectorNet (向量化输入 -> K=3 多模态轨迹)...")
for i in range(400):
    hist, maps, gt = make_data()
    traj, score = m(hist, maps)                    # [B,K,T,2]
    # minADE loss: 每样本挑最接近GT的模式(winner-takes-all)
    d = (traj - gt[:, None]).pow(2).sum(-1).mean(-1)   # [B,K]
    l_minade, idx = d.min(-1)
    l_score = F.cross_entropy(score, idx)          # 置信度对齐最优模式
    loss = l_minade.mean() + 0.1*l_score
    opt.zero_grad(); loss.backward(); opt.step()
    if (i+1) % 100 == 0: print(f"  iter{i+1} minADE={l_minade.mean().item():.4f}")

# 评估: 模态识别准确率
hist, maps, gt = make_data()
with torch.no_grad():
    traj, score = m(hist, maps)
    pred_best = score.argmax(-1)
    d = (traj - gt[:, None]).pow(2).sum(-1).mean(-1)
    true_best = d.argmin(-1)
    acc = (pred_best == true_best).float().mean()
    fde = (traj[torch.arange(32), true_best, -1] - gt[:, -1]).norm(dim=-1).mean()
print(f"✅ 模态识别准确率={acc:.2%}, minFDE={fde:.3f}")
print("💡 VectorNet核心: 地图+agent全向量化->GNN聚合; 多模态输出+minADE训练")
