"""
讲透复用权重 · 实验 04 —— 参数高效微调 PEFT / LoRA ★当代最火
================================================================
LoRA (Low-Rank Adaptation): 冻住整个预训练大模型, 只在每个线性层旁插入
一个【低秩】更新 ΔW = B·A (A∈r×d, B∈d×r, r<<d), 只训 A,B.
  - 可训参数量 ≈ 2rd (远小于 d²)
  - 效果接近全量微调, 但【只训 ~1% 参数】

本实验对比:
  ① 全量微调 (fine-tune)   : 解冻所有, 训 100% 参数
  ② LoRA 微调 (r=2)        : 冻所有, 插低秩, 训 ~6% 参数
在少样本目标任务上, 展示 LoRA 用极少参数接近全量微调.

跑法:  python3 04_lora.py     (CPU 约 60 秒)
输出:  lora_vs_full.png  (全量 vs LoRA 的准确率 + 可训参数对比)
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

Xs,ys = circles(2000); Xt_tr,yt_tr=circles(30); Xt_te,yt_te=circles(500)
HID=64

# ---- 基础 MLP ----
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone=nn.Sequential(nn.Linear(2,HID),nn.ReLU(),nn.Linear(HID,HID),nn.ReLU())
        self.head=nn.Linear(HID,2)
    def forward(self,x): return self.head(self.backbone(x))
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

# ---- 源预训练 ----
print("① 源任务预训练...", flush=True)
src=MLP(); opt=torch.optim.Adam(src.parameters(),1e-3); t=time.time()
for _ in range(2000):
    loss=nn.functional.cross_entropy(src(Xs),ys); opt.zero_grad();loss.backward();opt.step()
print(f"   源准确率={acc(src,Xs,ys):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- LoRA 封装: 给线性层加低秩旁路 ΔW=BA ----
class LoRALinear(nn.Module):
    def __init__(self, orig, r=2):
        super().__init__()
        self.orig=orig
        for p in self.orig.parameters(): p.requires_grad=False          # ★ 冻原权重
        d_in=orig.in_features; d_out=orig.out_features
        self.A=nn.Parameter(torch.randn(r,d_in)*0.01)                   # A 小随机
        self.B=nn.Parameter(torch.zeros(d_out,r))                       # B 零 → 初始 ΔW=0
    def forward(self,x):
        return self.orig(x) + (x @ self.A.t() @ self.B.t())             # Wx + xAᵀBᵀ = (W+BA)x

def make_lora_mlp(r=2):
    m=MLP()
    m.backbone[0]=LoRALinear(m.backbone[0],r)                            # 给每个 Linear 插 LoRA
    m.backbone[2]=LoRALinear(m.backbone[2],r)
    m.head=LoRALinear(m.head,r)
    # 载入源权重到 orig
    m.backbone[0].orig.load_state_dict(src.backbone[0].state_dict())
    m.backbone[2].orig.load_state_dict(src.backbone[2].state_dict())
    m.head.orig.load_state_dict(src.head.state_dict())
    return m

def ntrain(m): return sum(p.numel() for p in m.parameters() if p.requires_grad)

# ---- ② 全量微调 vs LoRA ----
def finetune_full():
    m=MLP(); m.load_state_dict(src.state_dict())                         # 复用源权重
    opt=torch.optim.Adam(m.parameters(),1e-3); hist=[]
    for _ in range(300):
        loss=nn.functional.cross_entropy(m(Xt_tr),yt_tr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m,Xt_te,yt_te))
    return m,hist

def finetune_lora(r=2):
    m=make_lora_mlp(r)
    params=[p for p in m.parameters() if p.requires_grad]                # 只有 LoRA 参数
    opt=torch.optim.Adam(params,1e-2); hist=[]
    for _ in range(300):
        loss=nn.functional.cross_entropy(m(Xt_tr),yt_tr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m,Xt_te,yt_te))
    return m,hist

print("② 目标任务 (circles, 30点): 全量微调 vs LoRA:\n", flush=True)
mF,hF=finetune_full(); nF=ntrain(mF)
mL,hL=finetune_lora(r=2); nL=ntrain(mL)
print(f"  全量微调 : 可训参数={nF:>5d} (100%)   准确率={hF[-1]:.3f}", flush=True)
print(f"  LoRA r=2 : 可训参数={nL:>5d} ({nL/nF:.1%}) 准确率={hL[-1]:.3f}   <- 极少参数, 接近全量", flush=True)

# ---- 画图 ----
fig,axes=plt.subplots(1,2,figsize=(12,5))
axes[0].plot(hF,label=f"全量微调 ({nF}参, {hF[-1]:.2f})"); axes[0].plot(hL,label=f"LoRA r=2 ({nL}参, {hL[-1]:.2f})")
axes[0].set_title("目标任务准确率 vs 步数"); axes[0].set_xlabel("步数"); axes[0].set_ylabel("准确率"); axes[0].legend()
axes[1].bar(["全量微调","LoRA"],[nF,nL],color=["C0","C2"])
axes[1].set_title(f"可训练参数对比 (LoRA 仅 {nL/nF:.1%})"); axes[1].set_ylabel("可训练参数数")
for i,n in enumerate([nF,nL]): axes[1].text(i,n,f"{n}",ha="center",va="bottom")
fig.suptitle("LoRA: 冻大模型, 插低秩旁路, 用 ~6% 参数接近全量微调 (2023最火微调法)", fontsize=12)
fig.tight_layout(); fig.savefig("lora_vs_full.png",dpi=110)
print("\n图已保存: lora_vs_full.png")
print("\n要点: LoRA 让普通人也能微调大模型 (省显存/省算力), 是开源社区微调 LLaMA 等的事实标准.")
