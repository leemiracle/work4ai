"""
讲透复用权重 · 实验 00 —— 从零训练 vs 复用预训练权重
=====================================================
核心问题: 在【少量目标数据】下, 同一个目标任务:
  ① 从零训练 (随机初始化)  ② 复用源任务预训练权重再微调
谁更好? 用 make_circles (同心圆, 需非线性边界) 直观展示复用权重的价值.

设计:
  源任务: circles 大数据 (2000) → 训一个 MLP 特征提取器
  目标任务: 同分布 circles, 仅 12 点 (少样本痛点) → 从零 vs 复用
  关键: circles 需要学到"环形"非线性边界, 12 点从零很难学好;
        复用源权重 (已学好环形特征) 则轻松适配 —— 这就是预训练范式 (ImageNet/BERT/GPT) 的立身之本.

跑法:  python3 00_reusing_vs_scratch.py     (CPU 约 25 秒)
输出:  reusing_vs_scratch.png  (准确率曲线 + 决策边界)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ------------------------------------------------------------------
# 1. 数据: 同心圆 (需要非线性环形边界, 比 moons 更难, 少样本下从零更吃亏)
# ------------------------------------------------------------------
def circles(n, noise=0.06):
    inner = n//2
    ri = np.sqrt(np.random.rand(inner))*0.5            # 内圆 r∈[0,0.5]
    ro = 0.8 + np.sqrt(np.random.rand(n-inner))*0.4    # 外圆 r∈[0.8,1.2]
    thi = np.random.rand(inner)*2*math.pi
    tho = np.random.rand(n-inner)*2*math.pi
    Xi = np.c_[ri*np.cos(thi), ri*np.sin(thi)] + noise*np.random.randn(inner,2)
    Xo = np.c_[ro*np.cos(tho), ro*np.sin(tho)] + noise*np.random.randn(n-inner,2)
    X = np.r_[Xi, Xo]; y = np.r_[np.zeros(inner), np.ones(n-inner)]
    idx = np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32), torch.tensor(y[idx],dtype=torch.long)

Xs, ys = circles(2000)              # 源: 大数据
Xt_tr, yt_tr = circles(12)          # 目标: 仅 12 点 (少样本!)
Xt_te, yt_te = circles(500)         # 目标测试集

# ------------------------------------------------------------------
# 2. 网络: 2->64->64->64 (骨干) -> 2 (头)
# ------------------------------------------------------------------
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU())
        self.head = nn.Linear(64,2)
    def forward(self,x): return self.head(self.backbone(x))
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

# ------------------------------------------------------------------
# 3. 源任务预训练 (大数据) —— 学好"环形"特征
# ------------------------------------------------------------------
print("① 源任务预训练 (circles 大数据 2000)...", flush=True)
src = MLP(); opt=torch.optim.Adam(src.parameters(),1e-3); t=time.time()
for it in range(2000):
    loss = nn.functional.cross_entropy(src(Xs), ys); opt.zero_grad();loss.backward();opt.step()
print(f"   源任务准确率 = {acc(src,Xs,ys):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ------------------------------------------------------------------
# 4. 目标任务对比 (同分布 12 点): 从零 vs 复用
# ------------------------------------------------------------------
def train_target(init_from=None, steps=300):
    m = MLP()
    if init_from is not None:
        m.backbone.load_state_dict(init_from.backbone.state_dict())  # ★ 复用骨干
        m.head.load_state_dict(init_from.head.state_dict())
    opt=torch.optim.Adam(m.parameters(),1e-3); hist=[]
    for it in range(steps):
        loss = nn.functional.cross_entropy(m(Xt_tr), yt_tr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m, Xt_te, yt_te))
    return m, hist

print("② 目标任务 (同分布 circles, 仅12点训练):\n", flush=True)
print("   A 从零训练 ...", flush=True); t=time.time(); mA,hA=train_target(None);    print(f"     最终测试准确率 = {acc(mA,Xt_te,yt_te):.3f}  ({time.time()-t:.0f}s)", flush=True)
print("   B 复用源权重+微调 ...", flush=True); t=time.time(); mB,hB=train_target(src); print(f"     最终测试准确率 = {acc(mB,Xt_te,yt_te):.3f}  ({time.time()-t:.0f}s)", flush=True)

s80_A = next((i for i,a in enumerate(hA) if a>0.85), len(hA))
s80_B = next((i for i,a in enumerate(hB) if a>0.85), len(hB))
print(f"\n=== 结论 ===")
print(f"  从零训练准确率 : {hA[-1]:.3f}   (12点学环形边界, 难, 易欠拟合/过拟合)")
print(f"  复用权重准确率 : {hB[-1]:.3f}   <- 复用预训练特征, 少样本下显著更好")
print(f"  达到85%准确率: 从零需 {s80_A} 步, 复用需 {s80_B} 步")

# ------------------------------------------------------------------
# 5. 画图
# ------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
axes[0,0].plot(hA, label=f"从零 (最终{hA[-1]:.2f})", lw=2)
axes[0,0].plot(hB, label=f"复用 (最终{hB[-1]:.2f})", lw=2)
axes[0,0].axhline(0.85, color='gray', ls='--', alpha=0.5); axes[0,0].set_title("目标任务(12点)测试准确率 vs 训练步数")
axes[0,0].set_xlabel("步数"); axes[0,0].set_ylabel("准确率"); axes[0,0].legend()

def plot_b(ax, m, X, y, title):
    ax.scatter(X[y==0,0], X[y==0,1], s=8, c="C0"); ax.scatter(X[y==1,0], X[y==1,1], s=8, c="C3")
    gx, gy = np.meshgrid(np.linspace(-1.5,1.5,100), np.linspace(-1.5,1.5,100))
    with torch.no_grad(): Z=m(torch.tensor(np.c_[gx.ravel(),gy.ravel()],dtype=torch.float32)).argmax(1).numpy().reshape(gx.shape)
    ax.contourf(gx,gy,Z,alpha=0.15,levels=[-0.5,0.5,1.5],colors=["C0","C3"]); ax.set_title(title); ax.set_aspect("equal"); ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5)

plot_b(axes[1,0], src, Xs, ys, f"源预训练模型 (大数据)\n准确率{acc(src,Xs,ys):.2f}")
plot_b(axes[1,1], mA, Xt_te, yt_te, f"从零 (仅12点)\n准确率{acc(mA,Xt_te,yt_te):.2f}")
plot_b(axes[1,2], mB, Xt_te, yt_te, f"复用权重+微调 (仅12点)\n准确率{acc(mB,Xt_te,yt_te):.2f}")
axes[0,1].scatter(Xt_tr[yt_tr==0,0], Xt_tr[yt_tr==0,1], s=60, c="C0", marker="x"); axes[0,1].scatter(Xt_tr[yt_tr==1,0], Xt_tr[yt_tr==1,1], s=60, c="C3", marker="x")
axes[0,1].set_title("目标训练集 (仅12点!)"); axes[0,1].set_aspect("equal"); axes[0,1].set_xlim(-1.5,1.5); axes[0,1].set_ylim(-1.5,1.5)
axes[0,2].axis('off')
fig.suptitle("复用权重的价值: 12点少样本下, 预训练特征让模型远胜从零训练 (现代ML基石)", fontsize=13)
fig.tight_layout(); fig.savefig("reusing_vs_scratch.png", dpi=110)
print("\n图已保存: reusing_vs_scratch.png")
