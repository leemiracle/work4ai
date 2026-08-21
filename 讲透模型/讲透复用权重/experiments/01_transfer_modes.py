"""
讲透复用权重 · 实验 01 —— 迁移学习全景: 特征提取 vs 微调 vs 从零
================================================================
源任务大数据预训练 → 目标任务少样本, 对比三种"复用方式":
  ① 从零训练 (scratch)        对照组, 不复用
  ② 特征提取 (feature extract) 冻骨干, 只训分类头 —— 最省, 但骨干不能改
  ③ 微调     (fine-tune)       复用骨干权重 + 解冻全训 —— 最灵活, 效果通常最好

跑法:  python3 01_transfer_modes.py     (CPU 约 60 秒)
输出:  transfer_modes.png  (三模式准确率曲线 + 决策边界)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- circles 数据 (同实验00) ----
def circles(n, noise=0.06):
    inner = n//2
    ri = np.sqrt(np.random.rand(inner))*0.5; ro = 0.8+np.sqrt(np.random.rand(n-inner))*0.4
    thi = np.random.rand(inner)*2*math.pi; tho = np.random.rand(n-inner)*2*math.pi
    Xi = np.c_[ri*np.cos(thi), ri*np.sin(thi)]+noise*np.random.randn(inner,2)
    Xo = np.c_[ro*np.cos(tho), ro*np.sin(tho)]+noise*np.random.randn(n-inner,2)
    X = np.r_[Xi,Xo]; y = np.r_[np.zeros(inner),np.ones(n-inner)]; idx=np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32), torch.tensor(y[idx],dtype=torch.long)

Xs,ys = circles(2000); Xt_tr,yt_tr = circles(20); Xt_te,yt_te = circles(500)   # 目标20点

# ---- 网络 ----
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU())
        self.head = nn.Linear(64,2)
    def forward(self,x): return self.head(self.backbone(x))
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

# ---- 源预训练 ----
print("① 源任务预训练 (circles 2000)...", flush=True)
src=MLP(); opt=torch.optim.Adam(src.parameters(),1e-3); t=time.time()
for _ in range(2000):
    loss=nn.functional.cross_entropy(src(Xs),ys); opt.zero_grad();loss.backward();opt.step()
print(f"   源准确率={acc(src,Xs,ys):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- 三种迁移模式 ----
def run(mode, steps=250):
    m=MLP()
    if mode in ('feature_extract','fine_tune'):
        m.backbone.load_state_dict(src.backbone.state_dict())
    if mode=='feature_extract':
        for p in m.backbone.parameters(): p.requires_grad=False   # ★ 冻骨干
    params = [p for p in m.parameters() if p.requires_grad]
    n_train = sum(p.numel() for p in params)
    opt=torch.optim.Adam(params,1e-3); hist=[]
    for _ in range(steps):
        loss=nn.functional.cross_entropy(m(Xt_tr),yt_tr); opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(m,Xt_te,yt_te))
    return m,hist,n_train

print("② 目标任务 (circles, 仅20点) 三模式对比:\n", flush=True)
results={}
for mode,tag in [('scratch','从零训练'),('feature_extract','特征提取(冻骨干)'),('fine_tune','微调(解冻)')]:
    t=time.time(); m,h,nt=run(mode); results[mode]=(m,h,nt)
    print(f"   {tag:18s}: 准确率={h[-1]:.3f}  可训参数={nt}  ({time.time()-t:.0f}s)", flush=True)

print(f"\n=== 解读 ===")
print("  从零训练 : 不复用, 少样本学非线性边界难")
print("  特征提取 : 冻骨干只训头, 最省(只训~130参数), 源特征够好时效果就够好")
print("  微调     : 解冻全训, 最灵活, 少样本下通常最好 (但要防过拟合)")

# ---- 画图 ----
fig,axes=plt.subplots(2,4,figsize=(18,9))
for mode,tag,c in [('scratch','从零','C3'),('feature_extract','特征提取(冻骨干)','C1'),('fine_tune','微调','C2')]:
    m,h,nt=results[mode]
    axes[0,0].plot(h,label=f"{tag} ({h[-1]:.2f}, {nt}参)",lw=2,color=c)
axes[0,0].set_title("目标任务(20点)准确率 vs 步数"); axes[0,0].set_xlabel("步数"); axes[0,0].set_ylabel("准确率"); axes[0,0].legend(fontsize=9)

def pb(ax,m,X,y,title,c0="C0",c1="C3"):
    ax.scatter(X[y==0,0],X[y==0,1],s=8,c=c0); ax.scatter(X[y==1,0],X[y==1,1],s=8,c=c1)
    gx,gy=np.meshgrid(np.linspace(-1.5,1.5,100),np.linspace(-1.5,1.5,100))
    with torch.no_grad(): Z=m(torch.tensor(np.c_[gx.ravel(),gy.ravel()],dtype=torch.float32)).argmax(1).numpy().reshape(gx.shape)
    ax.contourf(gx,gy,Z,alpha=0.15,levels=[-0.5,0.5,1.5],colors=[c0,c1]); ax.set_title(title); ax.set_aspect("equal"); ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5)
pb(axes[1,0],src,Xs,ys,f"源预训练\n(大数据, {acc(src,Xs,ys):.2f})")
for j,(mode,tag) in enumerate([('scratch','从零训练'),('feature_extract','特征提取(冻骨干)'),('fine_tune','微调')],1):
    m,h,nt=results[mode]; pb(axes[1,j],m,Xt_te,yt_te,f"{tag}\n{h[-1]:.2f}, {nt}参")
axes[0,1].scatter(Xt_tr[yt_tr==0,0],Xt_tr[yt_tr==0,1],s=80,c="C0",marker="x"); axes[0,1].scatter(Xt_tr[yt_tr==1,0],Xt_tr[yt_tr==1,1],s=80,c="C3",marker="x")
axes[0,1].set_title("目标训练集 (仅20点!)"); axes[0,1].set_aspect("equal"); axes[0,1].set_xlim(-1.5,1.5); axes[0,1].set_ylim(-1.5,1.5)
axes[0,2].axis('off'); axes[0,3].axis('off')
fig.suptitle("迁移学习三模式: 从零 / 特征提取(冻骨干) / 微调 —— 复用程度 vs 灵活度的权衡", fontsize=13)
fig.tight_layout(); fig.savefig("transfer_modes.png",dpi=110)
print("\n图已保存: transfer_modes.png")
