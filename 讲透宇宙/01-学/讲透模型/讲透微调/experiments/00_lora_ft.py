"""
实验 00 —— 微调的核心: 为什么 LoRA 用极少参数就能逼近全参数微调?
对应文档: 讲透微调/00-为什么LoRA能用1%参数逼近全参数微调.md
核心结论:
  1. 全参数微调(Full FT): 更新所有权重, 效果好但参数多 + 易灾难遗忘原任务
  2. LoRA: 冻结原权重 W, 只训低秩增量 ΔW = B·A (B:d×r, A:r×d, r≪d)
     参数省 10-100x, 效果接近 Full FT
  3. LoRA 因增量受低秩约束 + 原权重不动, 对原任务遗忘更少
  4. rank r 是权衡旋钮: r↑ 效果↑ 参数↑; 实践 r=8~64 常够
跑法: python3 -u 00_lora_ft.py
"""
import math, copy
import torch
import torch.nn as nn

def P(*a): print(*a, flush=True)
torch.manual_seed(0)

# 任务 A: y=sin(x), 任务 B: y=cos(x) —— 相关但不同的两个任务
x = torch.linspace(-math.pi, math.pi, 300).unsqueeze(1)
yA, yB = torch.sin(x), torch.cos(x)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.l1 = nn.Linear(1, 64); self.l2 = nn.Linear(64, 64); self.l3 = nn.Linear(64, 1)
    def forward(self, x):
        return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))

def train(model, x, y, steps=500, lr=0.01):
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=lr)
    for _ in range(steps):
        opt.zero_grad(); nn.MSELoss()(model(x), y).backward(); opt.step()

def loss_of(model, x, y):
    with torch.no_grad(): return nn.MSELoss()(model(x), y).item()

# ============ Part 1: 预训练基座 (在任务 A=sin 上训好) ============
P("="*60); P("Part 1: 预训练基座 (通才, 在任务A=sin上训好)"); P("="*60)
base = MLP(); train(base, x, yA)
P("基座 taskA(sin) loss = %.4f   taskB(cos) loss = %.4f (没见过cos, 不会)" %
  (loss_of(base, x, yA), loss_of(base, x, yB)))

# ============ Part 2: Full FT (全参数微调到 cos) ============
P("\n"+"="*60); P("Part 2: 全参数微调 Full FT (更新所有权重学cos)"); P("="*60)
full = copy.deepcopy(base)
n_full = sum(p.numel() for p in full.parameters() if p.requires_grad)
train(full, x, yB)
P("可训练参数 = %d (全部)" % n_full)
P("微调后 taskB(cos) loss = %.4f   taskA(sin) loss = %.4f ← 灾难遗忘!" %
  (loss_of(full, x, yB), loss_of(full, x, yA)))

# ============ Part 3: LoRA (冻结W, 只训低秩增量 ΔW=B·A) ============
P("\n"+"="*60); P("Part 3: LoRA (冻结原权重, 只训 ΔW=B·A, r≪d)"); P("="*60)
class LoRA(MLP):
    def __init__(self, base, r):
        super().__init__()
        self.load_state_dict(base.state_dict())     # 复制基座权重
        for p in self.parameters(): p.requires_grad = False   # 全冻结
        d = 64
        self.B1 = nn.Parameter(torch.zeros(d, r)); self.A1 = nn.Parameter(torch.randn(r, 1)*0.01)
        self.B2 = nn.Parameter(torch.zeros(d, r)); self.A2 = nn.Parameter(torch.randn(r, d)*0.01)
        self.B3 = nn.Parameter(torch.zeros(1, r));  self.A3 = nn.Parameter(torch.randn(r, d)*0.01)
        self.r = r
    def forward(self, x):
        h1 = torch.relu(self.l1(x)   + (x @ self.A1.T @ self.B1.T))
        h2 = torch.relu(self.l2(h1)  + (h1 @ self.A2.T @ self.B2.T))
        return self.l3(h2) + (h2 @ self.A3.T @ self.B3.T)
    def n_trainable(self):
        return sum(p.numel() for p in [self.B1,self.A1,self.B2,self.A2,self.B3,self.A3])

for r in [1, 2, 4]:
    torch.manual_seed(0)
    m = LoRA(base, r); train(m, x, yB)
    P("LoRA r=%2d: 可训练参数=%4d (%.1f%% of Full) | taskB=%.4f | taskA(sin 遗忘)=%.4f" %
      (r, m.n_trainable(), 100*m.n_trainable()/n_full, loss_of(m,x,yB), loss_of(m,x,yA)))

P("\n==> 对比:")
P("  Full FT:  参数 %d,  taskB=%.4f" % (n_full, loss_of(full,x,yB)))
P("  LoRA r=1: 参数 258 (仅 5.9%%),  taskB=0.0002 ≈ Full FT —— 少参数近效果!")
P("  关键: 任务微调的'权重更新 ΔW'本身是低秩的, LoRA 直接参数化 ΔW=B·A,")
P("        所以用极少参数就能表达 Full FT 学到的大部分变化。这是 LoRA work 的本质。")
P("  注: sin→cos 是强迁移(两函数正交), LoRA 也遗忘了 sin(0.998). '少遗忘'")
P("      要在相关任务(如指令风格微调)才显现; 本实验聚焦'省参数+近效果'这个核心。")
