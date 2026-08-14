"""
实验 03 — QLoRA: 4bit 量化基座 + LoRA (显存革命)
对应文档: 讲透微调/03-QLoRA.md
核心结论:
  1. 把基座权重量化到 4bit(NF4), 存储省 8x (FP32→INT4), 显存大幅下降
  2. 量化基座有精度损失, 但前向时反量化成 FP 计算 + LoRA 的 FP 增量能补偿
  3. QLoRA = 量化冻结基座(省显存) + LoRA(训 FP 增量), 让 70B 单卡可训
跑法: python3 -u 03_qlora.py
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
def train(m,x,y,steps=500,lr=0.01):
    ps=[p for p in m.parameters() if p.requires_grad]
    opt=torch.optim.Adam(ps,lr=lr)
    for _ in range(steps):
        opt.zero_grad(); nn.MSELoss()(m(x),y).backward(); opt.step()
def loss_of(m,x,y):
    with torch.no_grad(): return nn.MSELoss()(m(x),y).item()

base=MLP(); train(base,x,yA)
P("基座 taskA=%.4f taskB=%.4f"%(loss_of(base,x,yA),loss_of(base,x,yB)))

def quantize(w, bits):  # 对称量化, 返回 (量化值, scale)
    levels=2**(bits-1)-1; scale=w.abs().max()/levels
    return torch.round(w/scale).clamp(-levels,levels), scale

# ---- QLoRA: 基座量化到 4bit(冻结), 加 LoRA(FP, 可训) ----
class QLoRA(nn.Module):
    def __init__(self, base, r=4, bits=4):
        super().__init__()
        # 量化基座权重(存 int + scale, 反量化时用)
        self.q1,self.s1=quantize(base.l1.weight.data.clone(),bits); self.b1=base.l1.bias.data.clone()
        self.q2,self.s2=quantize(base.l2.weight.data.clone(),bits); self.b2=base.l2.bias.data.clone()
        self.q3,self.s3=quantize(base.l3.weight.data.clone(),bits); self.b3=base.l3.bias.data.clone()
        self.bits=bits
        # LoRA 增量(FP32, 可训练)
        d=64
        self.A1=nn.Parameter(torch.randn(r,1)*0.01); self.B1=nn.Parameter(torch.zeros(d,r))
        self.A2=nn.Parameter(torch.randn(r,d)*0.01); self.B2=nn.Parameter(torch.zeros(d,r))
        self.A3=nn.Parameter(torch.randn(r,d)*0.01); self.B3=nn.Parameter(torch.zeros(1,r))
    def fwd_l1(self,x): return torch.nn.functional.linear(x, self.q1*self.s1, self.b1)
    def fwd_l2(self,x): return torch.nn.functional.linear(x, self.q2*self.s2, self.b2)
    def fwd_l3(self,x): return torch.nn.functional.linear(x, self.q3*self.s3, self.b3)
    def forward(self,x):
        h1=torch.relu(self.fwd_l1(x)+(x@self.A1.T@self.B1.T))
        h2=torch.relu(self.fwd_l2(h1)+(h1@self.A2.T@self.B2.T))
        return self.fwd_l3(h2)+(h2@self.A3.T@self.B3.T)
    def base_bytes(self):  # 基座存储: 量化值占 bits/8 字节
        n=sum(q.numel() for q in [self.q1,self.q2,self.q3])
        return n*self.bits/8

# ---- 对比: FP32基座+LoRA  vs  INT4基座+LoRA(QLoRA) ----
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

P("\n"+"="*60); P("对比: LoRA(FP32基座) vs QLoRA(INT4基座)"); P("="*60)
torch.manual_seed(0); lora=LoRA(base,4); train(lora,x,yB)
torch.manual_seed(0); qlora=QLoRA(base,4,bits=4); train(qlora,x,yB)

# 基座参数量
n_base=sum(p.numel() for p in base.parameters())
P("基座参数 %d 个:" % n_base)
P("  LoRA  (FP32基座): 基座存储 %d 字节" % (n_base*4))
P("  QLoRA (INT4基座): 基座存储 %d 字节 (省 %.0fx)" % (qlora.base_bytes(), n_base*4/qlora.base_bytes()))
P("\n微调后 taskB(cos) loss:")
P("  LoRA  (FP32基座): %.4f" % loss_of(lora,x,yB))
P("  QLoRA (INT4基座): %.4f  (量化损失被 LoRA 的 FP 增量补偿)" % loss_of(qlora,x,yB))
P("\n==> QLoRA 基座存储省 8x, 效果仍接近 LoRA. ")
P("    真实规模: 70B 模型 FP32 需 280GB, QLoRA(INT4) 仅需 ~35GB → 单张 A100/H100 可训!")
P("    这就是 QLoRA(Dettmers 2023) 的革命意义: 让开源社区能在消费级硬件微调百亿模型.")
