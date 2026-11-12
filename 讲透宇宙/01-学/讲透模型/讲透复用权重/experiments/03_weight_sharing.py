"""
讲透复用权重 · 实验 03 —— 权重共享 (同组权重多处复用)
=====================================================
权重共享 (weight sharing) = 同一组参数在网络多处被复用, 从而【用更少参数做更深网络】.
经典案例: CNN (卷积核在整图滑动复用)、ALBERT (Transformer层共享)、Universal Transformer.

本实验对比:
  A 独立 MLP: 6 层, 每层独立权重 → 参数多 (~25K)
  B 共享 MLP: 1 层权重复用 6 次  → 参数少 (~4K, 约 1/6)
  在同一任务上, 展示【共享版用 1/6 参数达到相近效果】.

跑法:  python3 03_weight_sharing.py     (CPU 约 30 秒)
输出:  weight_sharing.png  (两网络的准确率曲线 + 参数量对比)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- circles 数据 ----
def circles(n, noise=0.06):
    inner=n//2
    ri=np.sqrt(np.random.rand(inner))*0.5; ro=0.8+np.sqrt(np.random.rand(n-inner))*0.4
    thi=np.random.rand(inner)*2*math.pi; tho=np.random.rand(n-inner)*2*math.pi
    Xi=np.c_[ri*np.cos(thi),ri*np.sin(thi)]+noise*np.random.randn(inner,2)
    Xo=np.c_[ro*np.cos(tho),ro*np.sin(tho)]+noise*np.random.randn(n-inner,2)
    X=np.r_[Xi,Xo]; y=np.r_[np.zeros(inner),np.ones(n-inner)]; idx=np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32), torch.tensor(y[idx],dtype=torch.long)

Xtr,ytr = circles(400); Xte,yte = circles(400)
HID=64; DEPTH=6

# ---- A 独立 MLP: DEPTH 层, 每层独立权重 ----
class IndepMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.inp=nn.Linear(2,HID)
        self.layers=nn.ModuleList([nn.Sequential(nn.Linear(HID,HID),nn.ReLU()) for _ in range(DEPTH)])
        self.out=nn.Linear(HID,2)
    def forward(self,x):
        x=self.inp(x)
        for l in self.layers: x=l(x)
        return self.out(x)

# ---- B 共享 MLP: 1 层权重复用 DEPTH 次 (Universal Transformer 风格) ----
class SharedMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.inp=nn.Linear(2,HID)
        self.layer=nn.Sequential(nn.Linear(HID,HID),nn.ReLU())   # ★ 只有一层!
        self.out=nn.Linear(HID,2)
    def forward(self,x):
        x=self.inp(x)
        for _ in range(DEPTH): x=self.layer(x)                    # ★ 同一组权重用 6 次
        return self.out(x)

def nparam(m): return sum(p.numel() for p in m.parameters() if p.requires_grad)
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

def train(Model):
    torch.manual_seed(0); m=Model(); opt=torch.optim.Adam(m.parameters(),1e-3); hist=[]
    for _ in range(800):
        loss=nn.functional.cross_entropy(m(Xtr),ytr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m,Xte,yte))
    return m,hist

print("权重共享 vs 独立权重 (同深度6层, 同任务):\n", flush=True)
mA,hA=train(IndepMLP); nA=nparam(mA)
mB,hB=train(SharedMLP); nB=nparam(mB)
print(f"  独立MLP : 参数={nA:>5d}  准确率={hA[-1]:.3f}", flush=True)
print(f"  共享MLP : 参数={nB:>5d}  准确率={hB[-1]:.3f}   <- 用 {nB/nA:.0%} 的参数达到相近效果", flush=True)
print(f"\n  参数节省: {nA} → {nB} ({(1-nB/nA):.0%} 更少)")

# ---- 画图 ----
fig,axes=plt.subplots(1,2,figsize=(12,5))
axes[0].plot(hA,label=f"独立MLP ({nA}参, {hA[-1]:.2f})"); axes[0].plot(hB,label=f"共享MLP ({nB}参, {hB[-1]:.2f})")
axes[0].set_title("准确率 vs 训练步数"); axes[0].set_xlabel("步数"); axes[0].set_ylabel("准确率"); axes[0].legend()
axes[1].bar(["独立MLP","共享MLP"],[nA,nB],color=["C0","C2"])
axes[1].set_title(f"参数量对比 (共享节省 {(1-nB/nA):.0%})"); axes[1].set_ylabel("可训练参数数")
for i,n in enumerate([nA,nB]): axes[1].text(i,n,f"{n}",ha="center",va="bottom")
fig.suptitle("权重共享: 同一组权重复用多次, 用 ~1/6 参数达到相近深度与效果", fontsize=12)
fig.tight_layout(); fig.savefig("weight_sharing.png",dpi=110)
print("\n图已保存: weight_sharing.png")
print("\n要点: CNN(卷积核滑动)/ALBERT(层共享)/Siamese(双子网络同权重) 都是此思想.")
