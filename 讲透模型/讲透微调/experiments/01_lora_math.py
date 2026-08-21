"""
实验 01 — LoRA 的两个关键数学细节: B=0 初始化 + α 缩放
对应文档: 讲透微调/01-LoRA数学深挖.md
核心结论:
  1. B=0 初始化(配合 A 高斯): 训练开始 ΔW=B·A=0, 模型严格等于基座, loss 平稳起步
     若 B 随机初始化: ΔW≠0, 模型偏离基座, 初始 loss 跳变, 训练不稳
  2. α 缩放: 实际 LoRA 输出 = W₀x + (α/r)·BAx. α/r 是 ΔW 强度旋钮(等效学习率)
     α 大=激进调整, α 小=温和; 实践常 α=16, r=8 → scale=2
跑法: python3 -u 01_lora_math.py
"""
import math
import torch, torch.nn as nn

def P(*a): print(*a, flush=True)
torch.manual_seed(0)
x = torch.linspace(-math.pi, math.pi, 300).unsqueeze(1)
yA, yB = torch.sin(x), torch.cos(x)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.l1=nn.Linear(1,64); self.l2=nn.Linear(64,64); self.l3=nn.Linear(64,1)
    def forward(self,x): return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
def train(m,x,y,steps=500,lr=0.01):
    opt=torch.optim.Adam([p for p in m.parameters() if p.requires_grad],lr=lr)
    for _ in range(steps):
        opt.zero_grad(); nn.MSELoss()(m(x),y).backward(); opt.step()
def loss_of(m,x,y):
    with torch.no_grad(): return nn.MSELoss()(m(x),y).item()

base=MLP(); train(base,x,yA)
P("基座: taskA(sin)=%.4f  taskB(cos)=%.4f (没见过cos)"%(loss_of(base,x,yA),loss_of(base,x,yB)))

class LoRA(MLP):
    def __init__(self, base, r, init_B_zero=True, alpha=8):
        super().__init__(); self.load_state_dict(base.state_dict())
        for p in self.parameters(): p.requires_grad=False
        d=64; self.r=r; self.scale=alpha/r
        z = lambda: torch.zeros(d,r) if init_B_zero else torch.randn(d,r)*0.01
        self.A1=nn.Parameter(torch.randn(r,1)*0.01); self.B1=nn.Parameter(z())
        self.A2=nn.Parameter(torch.randn(r,d)*0.01); self.B2=nn.Parameter(z() if d==64 else None)
        self.B2=nn.Parameter(torch.zeros(d,r) if init_B_zero else torch.randn(d,r)*0.01)
        self.A3=nn.Parameter(torch.randn(r,d)*0.01); self.B3=nn.Parameter(torch.zeros(1,r) if init_B_zero else torch.randn(1,r)*0.01)
    def forward(self,x):
        s=self.scale
        h1=torch.relu(self.l1(x)+s*(x@self.A1.T@self.B1.T))
        h2=torch.relu(self.l2(h1)+s*(h1@self.A2.T@self.B2.T))
        return self.l3(h2)+s*(h2@self.A3.T@self.B3.T)

# ============ Part 1: B 初始化的妙处 ============
P("\n"+"="*60); P("Part 1: B=0 vs B=rand 初始化"); P("="*60)
m0=LoRA(base,r=4,init_B_zero=True)
mr=LoRA(base,r=4,init_B_zero=False)
P("B=0   初始 taskB loss=%.4f  (ΔW=0·A=0, 模型严格=基座, 平稳起步)"%loss_of(m0,x,yB))
P("B=rand 初始 taskB loss=%.4f  (ΔW≠0, 模型偏离基座, 初始就跳变!)"%loss_of(mr,x,yB))
train(m0,x,yB); train(mr,x,yB)
P("训练500步后: B=0 → %.4f,  B=rand → %.4f"%(loss_of(m0,x,yB),loss_of(mr,x,yB)))
P("==> B=0 保证训练起点=基座(无破坏), A 高斯打破对称. 这是 LoRA 稳定的关键 trick.\n")

# ============ Part 2: α 缩放 ============
P("="*60); P("Part 2: α 缩放 (α/r 控制 ΔW 强度, 等效学习率)"); P("="*60)
for alpha in [1,4,8,16,32]:
    torch.manual_seed(0)
    m=LoRA(base,r=4,alpha=alpha); train(m,x,yB)
    P("α=%2d (scale α/r=%.2f): taskB=%.4f"%(alpha, alpha/4, loss_of(m,x,yB)))
P("==> α 大=ΔW 调整激进(等效高学习率, 快但可能不稳), α 小=温和.")
P("    实践常用 α=16, r=8 → scale=2; 换 r 时调 α 保持 scale 不变, 复用超参.")
