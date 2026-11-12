"""
讲透复用权重 · 实验 05 —— 知识蒸馏 (大模型 → 小模型)
====================================================
知识蒸馏 (Knowledge Distillation): 用一个【大教师】模型的输出(soft labels)
指导【小学生】模型训练, 把大模型的知识压进小模型权重.
  - soft label 比硬标签信息更丰富 ("这个数字80%是5, 但也有点像3")  ← dark knowledge
  - 蒸馏损失 = α·CE(硬标签) + (1-α)·KL(教师soft概率, 学生soft概率)

本实验对比:
  ① 直接训练小模型   (只用硬标签)
  ② 蒸馏训练小模型   (硬标签 + 大教师 soft 标签)
在少样本下, 展示蒸馏让小模型更强.

跑法:  python3 05_distillation.py     (CPU 约 50 秒)
输出:  distillation.png  (直接 vs 蒸馏小模型的准确率)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- 三分类数据 (3个高斯团, 蒸馏的 soft label 更有意义: 模糊样本的类间相似度) ----
def three_blobs(n=300):
    centers = np.array([[0,0],[2.5,0],[1.25,2.2]])
    X=[]; y=[]
    for c in range(3):
        X.append(centers[c] + 0.4*np.random.randn(n,2)); y.append(np.full(n,c))
    X=np.concatenate(X); y=np.concatenate(y); idx=np.random.permutation(len(X))
    return torch.tensor(X[idx],dtype=torch.float32), torch.tensor(y[idx],dtype=torch.long)

Xall,yall = three_blobs(400)
Xtr,ytr = Xall[:300],yall[:300]        # 少样本训练 (每类100)
Xte,yte = Xall[300:],yall[300:]
def acc(m,X,y):
    with torch.no_grad(): return (m(X).argmax(1)==y).float().mean().item()

# ---- 教师: 大模型 (128宽, 深) ; 学生: 小模型 (16宽, 浅) ----
def make_teacher(): return nn.Sequential(nn.Linear(2,128),nn.ReLU(),nn.Linear(128,128),nn.ReLU(),nn.Linear(128,3))
def make_student(): return nn.Sequential(nn.Linear(2,16),nn.ReLU(),nn.Linear(16,16),nn.ReLU(),nn.Linear(16,3))

# ---- ① 训练教师 (大数据/充分训练) ----
print("① 训练大教师模型...", flush=True)
teacher=make_teacher(); opt=torch.optim.Adam(teacher.parameters(),1e-3); t=time.time()
for _ in range(1500):
    loss=nn.functional.cross_entropy(teacher(Xtr),ytr); opt.zero_grad();loss.backward();opt.step()
print(f"   教师准确率={acc(teacher,Xte,yte):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- ② 直接训练小学生 vs 蒸馏小学生 ----
T=4.0   # 蒸馏温度 (软化概率, 暴露类间关系)
def train_student(distill=False, alpha=0.5, steps=600):
    torch.manual_seed(0)
    s=make_student(); opt=torch.optim.Adam(s.parameters(),1e-2); hist=[]
    teacher.eval()
    for _ in range(steps):
        logits=s(Xtr)
        loss_hard = nn.functional.cross_entropy(logits, ytr)
        if distill:
            with torch.no_grad():
                t_soft = nn.functional.softmax(teacher(Xtr)/T, dim=1)
            s_soft = nn.functional.log_softmax(logits/T, dim=1)
            loss_soft = nn.functional.kl_div(s_soft, t_soft, reduction='batchmean') * (T*T)
            loss = alpha*loss_hard + (1-alpha)*loss_soft
        else:
            loss = loss_hard
        opt.zero_grad();loss.backward();opt.step()
        hist.append(acc(s,Xte,yte))
    return s,hist

print("② 小学生模型 (16宽): 直接训练 vs 蒸馏:\n", flush=True)
sD,hD=train_student(distill=False)
sK,hK=train_student(distill=True)
print(f"  直接训练 : 准确率={hD[-1]:.3f}", flush=True)
print(f"  蒸馏训练 : 准确率={hK[-1]:.3f}   <- 教师的soft label提供了额外信息", flush=True)

# ---- 画图 ----
fig,axes=plt.subplots(1,2,figsize=(12,5))
axes[0].plot(hD,label=f"直接训练 ({hD[-1]:.2f})"); axes[0].plot(hK,label=f"蒸馏训练 ({hK[-1]:.2f})")
axes[0].set_title("小学生准确率 vs 步数"); axes[0].set_xlabel("步数"); axes[0].set_ylabel("准确率"); axes[0].legend()

# 看一个样本的 soft label (展示 dark knowledge)
with torch.no_grad():
    sample = Xte[0:1]
    print(f"\n样本 soft label 对比 (真实类={yte[0].item()}):")
    print(f"  硬标签       : {[1.0 if i==yte[0] else 0.0 for i in range(3)]}")
    print(f"  教师soft(T=4): {nn.functional.softmax(teacher(sample)/T,dim=1)[0].numpy().round(3)}")
    print(f"  学生soft蒸馏 : {nn.functional.softmax(sK(sample)/T,dim=1)[0].numpy().round(3)}")
    print(f"  学生soft直接 : {nn.functional.softmax(sD(sample)/T,dim=1)[0].numpy().round(3)}")

def pb(ax,m,X,y,title):
    for c in range(3):
        ax.scatter(X[y==c,0],X[y==c,1],s=8,c=f"C{c}")
    gx,gy=np.meshgrid(np.linspace(-1.5,4,100),np.linspace(-1.5,3.5,100))
    with torch.no_grad(): Z=m(torch.tensor(np.c_[gx.ravel(),gy.ravel()],dtype=torch.float32)).argmax(1).numpy().reshape(gx.shape)
    ax.contourf(gx,gy,Z,alpha=0.1,levels=[-0.5,0.5,1.5,2.5],colors=["C0","C1","C2"]); ax.set_title(title); ax.set_aspect("equal")
pb(axes[1],sD,Xte,yte,f"直接训练学生\n{acc(sD,Xte,yte):.2f}")
fig.suptitle("知识蒸馏: 大教师的soft label 比硬标签信息更丰富, 让小学生更强", fontsize=12)
fig.tight_layout(); fig.savefig("distillation.png",dpi=110)
print("\n图已保存: distillation.png")
