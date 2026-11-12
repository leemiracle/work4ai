"""
讲透复用权重 · 实验 02 —— 自监督预训练 (无标签白嫖特征)
==========================================================
迁移学习假设源任务有标签。但现实中【海量数据往往没标签】(互联网文本/图片).
自监督预训练 (self-supervised) 的天才: 用数据自身构造监督信号, 无需人工标注.

本实验用【去噪自编码器 DAE】演示自监督思想:
  ① 预训练 (无标签!): 给 circles 数据加噪声, 学着恢复原始 —— 代理任务, 标签免费
  ② 线性探测: 冻住 DAE 编码器, 只训线性分类头, 用少量【有标签】数据
  ③ 对比: 随机编码器 vs DAE 编码器, 少样本下的分类效果

预期: DAE 编码器(自监督预训练) 学到了"距原点距离"等结构特征, 对内外圆分类有用
      → 线性探测远好于随机编码器. 这就是 BERT/CLIP 的核心思想 (无标签白嫖).

跑法:  python3 02_pretrain.py     (CPU 约 50 秒)
输出:  selfsupervised.png  (随机 vs DAE 编码器的特征 + 线性分类效果)
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

# 自监督预训练用: 大量无标签数据 (只留X, 丢y)
X_unlab,_ = circles(2000)
# 下游用: 少量有标签数据
Xt_tr,yt_tr = circles(20); Xt_te,yt_te = circles(500)

# ---- 网络: 编码器 (2->64->64) + 解码器 (64->2, 仅预训练用) ----
class DAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU())
        self.dec = nn.Sequential(nn.Linear(64,64),nn.ReLU(),nn.Linear(64,2))
    def forward(self,x): return self.dec(self.enc(x))

# ---- ① 自监督预训练: 加噪声 → 恢复 (MSE, 无标签!) ----
print("① 自监督预训练 (去噪自编码器, 无标签)...", flush=True)
dae=DAE(); opt=torch.optim.Adam(dae.parameters(),1e-3); t=time.time()
for _ in range(1500):
    noise=0.15*torch.randn_like(X_unlab)
    x_noisy=X_unlab+noise                                  # 加噪
    x_recon=dae(x_noisy)                                   # 恢复
    loss=nn.functional.mse_loss(x_recon, X_unlab)          # 目标=原始 (标签免费!)
    opt.zero_grad();loss.backward();opt.step()
print(f"   预训练重构MSE={loss.item():.4f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- ② 线性探测: 冻编码器, 只训线性头 ----
def linear_probe(encoder, steps=300):
    """冻住encoder, 只训一个线性分类头, 用20点有标签数据."""
    for p in encoder.parameters(): p.requires_grad=False
    head=nn.Linear(64,2); opt=torch.optim.Adam(head.parameters(),1e-2); hist=[]
    for _ in range(steps):
        feat=encoder(Xt_tr); loss=nn.functional.cross_entropy(head(feat),yt_tr)
        opt.zero_grad();loss.backward();opt.step()
        with torch.no_grad(): hist.append((head(encoder(Xt_te)).argmax(1)==yt_te).float().mean().item())
    return head,hist

# 随机编码器 (未预训练) vs DAE编码器 (自监督预训练)
print("② 线性探测 (冻编码器, 只训头, 仅20点有标签):\n", flush=True)
torch.manual_seed(1)
rand_enc = nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU())  # 随机权重
h_rand,hist_rand = linear_probe(rand_enc)
h_dae,hist_dae = linear_probe(dae.enc)
print(f"   随机编码器 (未预训练) : 准确率={hist_rand[-1]:.3f}", flush=True)
print(f"   DAE编码器  (自监督)    : 准确率={hist_dae[-1]:.3f}   <- 无标签预训练后特征更好", flush=True)

print(f"\n=== 结论 ===")
print("  自监督预训练只用【无标签】数据(加噪恢复), 却让编码器学到了有用特征.")
print("  少样本(20点)线性探测, DAE >> 随机. 这就是 BERT(MLM)/CLIP(对比) 的核心: 无标签白嫖特征.")

# ---- 画图 ----
fig,axes=plt.subplots(1,3,figsize=(15,5))
axes[0].plot(hist_rand,label=f"随机编码器 ({hist_rand[-1]:.2f})"); axes[0].plot(hist_dae,label=f"DAE自监督 ({hist_dae[-1]:.2f})")
axes[0].set_title("线性探测准确率 (20点有标签)"); axes[0].set_xlabel("步数"); axes[0].set_ylabel("准确率"); axes[0].legend()

# 可视化编码器输出特征 (20点经过编码后的64维, 取前2维PCA近似)
def feats2d(enc,X):
    with torch.no_grad(): f=enc(X).numpy()
    return f[:,0],f[:,1]   # 取前两维示意
for ax,enc,title in [(axes[1],rand_enc,"随机编码器特征\n(线性不可分)"),(axes[2],dae.enc,"DAE自监督特征\n(线性可分)")]:
    fx0,fy0=feats2d(enc,Xt_tr[yt_tr==0]); fx1,fy1=feats2d(enc,Xt_tr[yt_tr==1])
    ax.scatter(fx0,fy0,s=80,c="C0",marker="x"); ax.scatter(fx1,fy1,s=80,c="C3",marker="x")
    ax.set_title(title); ax.set_xlabel("特征维1"); ax.set_ylabel("特征维2")
fig.suptitle("自监督预训练: 无标签数据白嫖特征, 让少样本线性探测远超随机初始化", fontsize=12)
fig.tight_layout(); fig.savefig("selfsupervised.png",dpi=110)
print("\n图已保存: selfsupervised.png")
