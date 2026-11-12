"""
实验 02 — PEFT 全家桶: LoRA vs Adapter (参数/效果/推理延迟 三维对比)
对应文档: 讲透微调/02-PEFT全家桶.md
核心结论:
  1. LoRA 和 Adapter 参数量相近(都 ~2dr), 效果相近
  2. 关键区别在【推理】: LoRA 的 ΔW=BA 可合并进 W₀, 推理=base 无额外延迟
     Adapter 是额外插入的层, 推理永久多一次 forward, 无法合并
  3. Prefix/Prompt Tuning 改输入不改权重, 参数更少但只适合大模型
跑法: python3 -u 02_peft.py
"""
import math, torch, torch.nn as nn

def P(*a): print(*a, flush=True)
torch.manual_seed(0)
x = torch.linspace(-math.pi, math.pi, 300).unsqueeze(1)
yA, yB = torch.sin(x), torch.cos(x)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.l1=nn.Linear(1,64); self.l2=nn.Linear(64,64); self.l3=nn.Linear(64,1)
    def forward(self,x): return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
    def flops(self):  # 单次前向 FLOPs(近似)
        return (1*64+64*64+64*1) + (64+64+1)  # 三个 Linear 的乘加 + bias
def train(m,x,y,steps=500,lr=0.01):
    opt=torch.optim.Adam([p for p in m.parameters() if p.requires_grad],lr=lr)
    for _ in range(steps):
        opt.zero_grad(); nn.MSELoss()(m(x),y).backward(); opt.step()
def loss_of(m,x,y):
    with torch.no_grad(): return nn.MSELoss()(m(x),y).item()

base=MLP(); train(base,x,yA)
P("基座 taskA=%.4f taskB=%.4f"%(loss_of(base,x,yA),loss_of(base,x,yB)))

# ---- LoRA (可合并, 推理无延迟) ----
class LoRA(MLP):
    def __init__(self,base,r=4):
        super().__init__(); self.load_state_dict(base.state_dict())
        for p in self.parameters(): p.requires_grad=False
        d=64
        self.A1=nn.Parameter(torch.randn(r,1)*0.01); self.B1=nn.Parameter(torch.zeros(d,r))
        self.A2=nn.Parameter(torch.randn(r,d)*0.01); self.B2=nn.Parameter(torch.zeros(d,r))
        self.A3=nn.Parameter(torch.randn(r,d)*0.01); self.B3=nn.Parameter(torch.zeros(1,r))
    def forward(self,x):
        h1=torch.relu(self.l1(x)+(x@self.A1.T@self.B1.T))
        h2=torch.relu(self.l2(h1)+(h1@self.A2.T@self.B2.T))
        return self.l3(h2)+(h2@self.A3.T@self.B3.T)
    def n_tr(self): return sum(p.numel() for p in [self.A1,self.B1,self.A2,self.B2,self.A3,self.B3])

# ---- Adapter (额外层, 推理永久多计算) ----
class AdapterMLP(MLP):
    def __init__(self,base,r=4):
        super().__init__(); self.load_state_dict(base.state_dict())
        for p in self.parameters(): p.requires_grad=False
        d=64
        self.ad1=nn.Sequential(nn.Linear(d,r),nn.ReLU(),nn.Linear(r,d))
        self.ad2=nn.Sequential(nn.Linear(d,r),nn.ReLU(),nn.Linear(r,d))
    def forward(self,x):
        h1=torch.relu(self.l1(x)); h1=h1+self.ad1(h1)   # 残差 adapter, 不可合并
        h2=torch.relu(self.l2(h1)); h2=h2+self.ad2(h2)
        return self.l3(h2)
    def n_tr(self): return sum(p.numel() for p in self.ad1.parameters())+sum(p.numel() for p in self.ad2.parameters())
    def extra_flops(self):  # adapter 额外推理 FLOPs(每次前向, 永久)
        return 2*(64*4+4*64)  # 两个 adapter: d·r + r·d

P("\n"+"="*60); P("对比: Full FT / LoRA / Adapter (r=4)"); P("="*60)
P("%-12s%12s%12s%16s"%("方法","可训练参数","taskB loss","推理额外开销"))

# Full FT
full=MLP(); full.load_state_dict(base.state_dict()); train(full,x,yB)
P("%-12s%12d%12.4f%16s"%("Full FT", sum(p.numel() for p in full.parameters()), loss_of(full,x,yB), "0 (但存全模型)"))

# LoRA
torch.manual_seed(0); lora=LoRA(base,4); train(lora,x,yB)
P("%-12s%12d%12.4f%16s"%("LoRA", lora.n_tr(), loss_of(lora,x,yB), "0 (ΔW可合并)"))

# Adapter
torch.manual_seed(0); adp=AdapterMLP(base,4); train(adp,x,yB)
P("%-12s%12d%12.4f%16d FLOPs"%("Adapter", adp.n_tr(), loss_of(adp,x,yB), adp.extra_flops()))

P("\n==> LoRA 与 Adapter 参数/效果相近, 但 LoRA 推理可合并(无延迟),")
P("    Adapter 推理永久多 %d FLOPs/层 —— 这就是 LoRA 淘汰 Adapter 的关键." % adp.extra_flops())
P("\nPrefix/Prompt Tuning: 改输入(加可学习token), 参数更少(~0.1%%),")
P("  但只在大模型(>10B)才有效, 小模型上不如 LoRA. 适合'多个任务热切换'.")
