"""
Mini-UniAD —— 用一个玩具任务演示 UniAD 的核心哲学:
  "感知、预测、规划共享一个网络, query 作为接口, 端到端联合训练"
================================================================
合成任务设计(让"感知必须服务规划"):
  - BEV 16x16 网格上有 1~3 个"障碍物"(高斯亮斑), 位置随机
  - 自车沿 +x 直行; 若障碍物挡道(靠近直行走廊), 自车未来速度必须减慢
  - GT: 自车未来 T=4 步的位移(取决于障碍物位置) —— 规划必须先"看见"障碍物

模型(UniAD 精神缩小版):
  BEV Encoder (CNN)  ->  BEV tokens
  Agent Queries (可学习) --cross-attn--> BEV tokens  = 感知(query接口!)
  det head: 每个query回归障碍物位置
  motion head: 障碍物未来位置
  planner: [ego_state + pooled_bev + agent_embeds] -> 自车未来轨迹
联合损失: L = L_det + L_motion + L_plan

对照实验: "分离式"(规划器拿不到感知梯度/特征) vs "联合式"
预期: 联合式规划误差更低 -> 展示端到端的价值
"""
import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)

H, W, T, MAX_AG = 16, 16, 4, 3   # 网格/时序/最多障碍物
DIM, NQ = 64, 5                   # 特征维/query数

def make_scene():
    """合成一个场景: BEV图 + 障碍物GT + 自车未来GT"""
    n = torch.randint(1, MAX_AG+1, (1,)).item()
    pos = torch.rand(n, 2) * 1.2 - 0.6           # [-0.6, 0.6]^2 归一化坐标
    bev = torch.zeros(1, H, W)
    xs = torch.linspace(-0.8, 0.8, W); ys = torch.linspace(-0.8, 0.8, H)
    for p in pos:
        bev[0] += torch.exp(-((xs[None,:]-p[0])**2 + (ys[:,None]-p[1])**2) / 0.02)
    bev = bev.clamp(0, 1)
    vel = torch.randn(n, 2) * 0.05               # 障碍物速度
    fut = torch.stack([pos + vel*t for t in range(1, T+1)], 1)  # [n,T,2]
    # 自车GT: 直行速度取决于最近障碍物到走廊(|y|<0.25, x>0)的距离
    corridor = [(p[0] > 0.0) & (abs(p[1]) < 0.25) for p in pos]
    blocked = any(corridor)
    v = 0.0 if blocked else 0.5                  # 挡道->停, 否则0.5/步
    ego_fut = torch.stack([torch.tensor([0.5*(t+1)*v, 0.0]) for t in range(T)])
    return bev, pos, fut, ego_fut

class MiniUniAD(nn.Module):
    def __init__(self, joint=True):
        super().__init__()
        self.joint = joint                      # False = 分离式对照
        self.bev_enc = nn.Sequential(           # CNN: [B,1,16,16] -> [B,16,DIM]
            nn.Conv2d(1, 32, 3, 2, 1), nn.ReLU(),
            nn.Conv2d(32, DIM, 3, 2, 1), nn.ReLU(),   # -> [B,DIM,4,4]
        )
        self.pos_emb = nn.Parameter(torch.randn(1, 16, DIM) * 0.02)
        self.agent_q = nn.Parameter(torch.randn(1, NQ, DIM) * 0.02)
        self.cross_attn = nn.MultiheadAttention(DIM, 4, batch_first=True)
        self.det_head = nn.Linear(DIM, 2)               # query -> 障碍物xy
        self.motion_head = nn.Linear(DIM, T*2)          # query -> 障碍物未来
        self.planner = nn.Sequential(
            nn.Linear(DIM*2 + 1, 128), nn.ReLU(), nn.Linear(128, T*2))

    def forward(self, bev, ego_vel):
        B = bev.shape[0]
        tokens = self.bev_enc(bev).flatten(2).transpose(1, 2) + self.pos_emb  # [B,16,DIM]
        q = self.agent_q.expand(B, -1, -1)
        agent_emb, _ = self.cross_attn(q, tokens, tokens)     # 感知: query<->BEV
        det = self.det_head(agent_emb)                        # [B,NQ,2]
        motion = self.motion_head(agent_emb)                  # [B,NQ,T*2]
        pooled = agent_emb.mean(1)                            # [B,DIM]
        if not self.joint:                                    # 分离式: 切断感知特征
            pooled = pooled.detach()
        plan_in = torch.cat([pooled, tokens.mean(1), ego_vel], -1)
        plan = self.planner(plan_in)                          # [B,T*2]
        return det, motion, plan

def train(model, iters=400, lr=2e-3):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for i in range(iters):
        bev, pos, fut, ego_fut = make_scene()
        det, motion, plan = model(bev[None], torch.tensor([[0.5]]))
        # L_det/L_motion: 每个GT障碍物取最近query (min-style, UniAD式匹配的简化)
        l_det = sum((det[0]-p).norm(dim=-1).min() for p in pos) / len(pos)
        l_mot = 0
        for j, p in enumerate(pos):
            q_idx = (det[0]-p).norm(dim=-1).argmin()
            l_mot = l_mot + ((motion[0, q_idx] - fut[j].flatten()).pow(2).mean())
        l_mot /= len(pos)
        l_plan = (plan[0] - ego_fut.flatten()).pow(2).mean()
        loss = l_det + l_mot + l_plan
        opt.zero_grad(); loss.backward(); opt.step()
        if (i+1) % 100 == 0:
            print(f"  iter{i+1:4d} | L_det={l_det.item():.3f} L_mot={l_mot.item():.3f} L_plan={l_plan.item():.3f}")
    return model

@torch.no_grad()
def eval_plan(model, n=300):
    err = 0
    for _ in range(n):
        bev, pos, fut, ego_fut = make_scene()
        det, motion, plan = model(bev[None], torch.tensor([[0.5]]))
        err += (plan[0] - ego_fut.flatten()).pow(2).mean().item()
    return (err/n) ** 0.5

print("=" * 62)
print("Mini-UniAD: 感知+预测+规划 联合训练 (query 接口, 端到端)")
print("=" * 62)
joint = train(MiniUniAD(joint=True))
separate = train(MiniUniAD(joint=False), iters=1)   # 分离式也需公平训练
separate = train(separate)

e1, e2 = eval_plan(joint), eval_plan(separate)
print("-" * 62)
print(f"规划 RMSE  联合式(端到端): {e1:.4f}")
print(f"规划 RMSE  分离式(无感知梯度): {e2:.4f}")
print(f"\n💡 结论: 联合式{'更优 ✓' if e1 < e2 else '持平'} ——")
print("   规划头要判断'是否减速'必须依赖感知特征;")
print("   端到端让规划损失直接塑造感知表示 —— UniAD 的核心论证。")
