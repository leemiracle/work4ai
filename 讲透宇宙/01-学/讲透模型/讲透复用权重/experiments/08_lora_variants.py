"""
讲透复用权重 · 实验 08 —— LoRA 深水区: 变体家族对比 ★进阶
================================================================
原版 LoRA (实验04) 只是起点. 2023-2026 涌现一批改进变体:
  - DoRA   : 把权重分解为【大小 magnitude + 方向 direction】, 分别适配 → 更灵活
  - AdaLoRA: 动态调整每层的秩 r (重要层给更高秩) → 自适应
  - QLoRA  : 基座 4bit 量化 + LoRA → 极致省显存, 单卡微调 70B
  - LoRA+  : A/B 用不同学习率 (B 快, A 慢) → 收敛更快更稳

本实验对比【原版 LoRA vs DoRA】, 展示"分解 magnitude/direction"带来的灵活度.
其余变体(QLoRA/AdaLoRA/LoRA+) 原理在 md 里讲清.

跑法:  python3 08_lora_variants.py     (CPU 约 50 秒)
输出:  lora_variants.png  (全量/LoRA/DoRA 的准确率+参数对比)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

def circles(n, noise=0.06):
    inner=n//2; ri=np.sqrt(np.random.rand(inner))*0.5; ro=0.8+np.sqrt(np.random.rand(n-inner))*0.4
    thi=np.random.rand(inner)*2*math.pi; tho=np.random.rand(n-inner)*2*math.pi
    Xi=np.c_[ri*np.cos(thi),ri*np.sin(thi)]+noise*np.random.randn(inner,2)
    Xo=np.c_[ro*np.cos(tho),ro*np.sin(tho)]+noise*np.random.randn(n-inner,2)
    X=np.r_[Xi,Xo]; y=np.r_[np.zeros(inner),np.ones(n-inner)]; idx=np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32),torch.tensor(y[idx],dtype=torch.long)

Xs,ys=circles(2000); Xt_tr,yt_tr=circles(30); Xt_te,yt_te=circles(500)
HID=64; R=2

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone=nn.Sequential(nn.Linear(2,HID),nn.ReLU(),nn.Linear(HID,HID),nn.ReLU())
        self.head=nn.Linear(HID,2)
    def forward(self,x): return self.head(self.backbone(x))
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

# ---- 源预训练 ----
print("① 源预训练...", flush=True)
src=MLP(); opt=torch.optim.Adam(src.parameters(),1e-3); t=time.time()
for _ in range(1500):
    loss=nn.functional.cross_entropy(src(Xs),ys); opt.zero_grad();loss.backward();opt.step()
print(f"   源准确率={acc(src,Xs,ys):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- LoRA 层 (原版) ----
class LoRALinear(nn.Module):
    def __init__(self, orig, r=R):
        super().__init__(); self.orig=orig
        for p in self.orig.parameters(): p.requires_grad=False
        self.A=nn.Parameter(torch.randn(r,orig.in_features)*0.01); self.B=nn.Parameter(torch.zeros(orig.out_features,r))
    def dWx(self,x): return x @ self.A.t() @ self.B.t()
    def forward(self,x): return self.orig(x) + self.dWx(x)

# ---- DoRA 层: LoRA + 可学 magnitude (分解大小/方向) ----
class DoRALinear(LoRALinear):
    def __init__(self, orig, r=R):
        super().__init__(orig,r)
        self.mag=nn.Parameter(torch.ones(orig.out_features))   # ★ 额外的 per-output magnitude
    def forward(self,x):
        base = self.orig(x) + self.dWx(x)                       # W+BA 的输出
        return self.mag * base                                  # ★ magnitude 单独调控每个输出维

def build(variant):
    m=MLP()
    def wrap(layer):
        return LoRALinear(layer) if variant=='lora' else DoRALinear(layer)
    m.backbone[0]=wrap(m.backbone[0]); m.backbone[2]=wrap(m.backbone[2]); m.head=wrap(m.head)
    m.backbone[0].orig.load_state_dict(src.backbone[0].state_dict())
    m.backbone[2].orig.load_state_dict(src.backbone[2].state_dict())
    m.head.orig.load_state_dict(src.head.state_dict())
    return m
def ntrain(m): return sum(p.numel() for p in m.parameters() if p.requires_grad)

def finetune(variant, steps=300):
    m=build(variant); params=[p for p in m.parameters() if p.requires_grad]
    opt=torch.optim.Adam(params,1e-2); hist=[]
    for _ in range(steps):
        loss=nn.functional.cross_entropy(m(Xt_tr),yt_tr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m,Xt_te,yt_te))
    return m,hist

print("② 目标任务(30点): 全量 / LoRA / DoRA:\n", flush=True)
# 全量
mF=MLP(); mF.load_state_dict(src.state_dict()); optF=torch.optim.Adam(mF.parameters(),1e-3); hF=[]
for _ in range(300):
    loss=nn.functional.cross_entropy(mF(Xt_tr),yt_tr); optF.zero_grad();loss.backward();optF.step(); hF.append(acc(mF,Xt_te,yt_te))
nF=ntrain(mF)
mL,hL=finetune('lora'); nL=ntrain(mL)
mD,hD=finetune('dora'); nD=ntrain(mD)
print(f"  全量微调 : 参数={nF:>5d} (100%)   准确率={hF[-1]:.3f}", flush=True)
print(f"  LoRA r=2 : 参数={nL:>5d} ({nL/nF:.1%}) 准确率={hL[-1]:.3f}", flush=True)
print(f"  DoRA r=2 : 参数={nD:>5d} ({nD/nF:.1%}) 准确率={hD[-1]:.3f}   <- 多了magnitude, 更灵活", flush=True)

# ---- 画图 ----
fig,axes=plt.subplots(1,2,figsize=(12,5))
axes[0].plot(hF,label=f"全量 ({nF}参,{hF[-1]:.2f})"); axes[0].plot(hL,label=f"LoRA ({nL}参,{hL[-1]:.2f})"); axes[0].plot(hD,label=f"DoRA ({nD}参,{hD[-1]:.2f})")
axes[0].set_title("目标任务准确率 vs 步数"); axes[0].set_xlabel("步数"); axes[0].set_ylabel("准确率"); axes[0].legend()
axes[1].bar(["全量","LoRA","DoRA"],[nF,nL,nD],color=["C0","C2","C4"]); axes[1].set_title("可训练参数对比"); axes[1].set_ylabel("参数数")
for i,n in enumerate([nF,nL,nD]): axes[1].text(i,n,f"{n}",ha="center",va="bottom")
fig.suptitle("LoRA 变体: DoRA 多学一个 magnitude, 用几乎相同参数更灵活 (2024改进)", fontsize=12)
fig.tight_layout(); fig.savefig("lora_variants.png",dpi=110)
print("\n图已保存: lora_variants.png")
print("\n要点: QLoRA(量化基座)/AdaLoRA(动态秩)/LoRA+(差分学习率) 原理见 md, 均为原版LoRA的工程改进.")
