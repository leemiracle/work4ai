"""
讲透复用权重 · 实验 06 —— 持续学习与灾难性遗忘
================================================
持续学习 (Continual Learning): 模型顺序学多个任务, 复用旧知识又不忘记.
核心痛点: 【灾难性遗忘】—— 学新任务后, 旧任务能力崩溃.

本实验:
  任务A: circles 分类 (内/外圆)
  任务B: moons 分类 (月牙)
  顺序训练 A → B, 观察遗忘; 再用【经验回放 rehearsal】缓解.

  ① 纯顺序训练 (A→B)      : 学 B 后 A 性能崩溃 (遗忘)
  ② 回放训练 (B 时混入A样本): A 性能保持 (缓解)

跑法:  python3 06_continual.py     (CPU 约 40 秒)
输出:  continual.png  (训练B过程中 A/B 准确率的变化曲线)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- 任务A: circles ----
def circles(n, noise=0.06):
    inner=n//2; ri=np.sqrt(np.random.rand(inner))*0.5; ro=0.8+np.sqrt(np.random.rand(n-inner))*0.4
    thi=np.random.rand(inner)*2*math.pi; tho=np.random.rand(n-inner)*2*math.pi
    Xi=np.c_[ri*np.cos(thi),ri*np.sin(thi)]+noise*np.random.randn(inner,2)
    Xo=np.c_[ro*np.cos(tho),ro*np.sin(tho)]+noise*np.random.randn(n-inner,2)
    X=np.r_[Xi,Xo]; y=np.r_[np.zeros(inner),np.ones(n-inner)]; idx=np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32),torch.tensor(y[idx],dtype=torch.long)
# ---- 任务B: moons ----
def moons(n, noise=0.10):
    t=np.linspace(0,math.pi,n//2)
    up=np.c_[np.cos(t),np.sin(t)]+noise*np.random.randn(n//2,2)
    dn=np.c_[1-np.cos(t),-np.sin(t)-0.5]+noise*np.random.randn(n//2,2)
    X=np.r_[up,dn]; y=np.r_[np.zeros(n//2),np.ones(n//2)]; idx=np.random.permutation(n)
    return torch.tensor(X[idx],dtype=torch.float32),torch.tensor(y[idx],dtype=torch.long)

Xa_tr,ya_tr=circles(400); Xa_te,ya_te=circles(400)
Xb_tr,yb_tr=moons(400);   Xb_te,yb_te=moons(400)

net=nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,2))
def acc(X,y):
    with torch.no_grad(): return (net(X).argmax(1)==y).float().mean().item()

# ---- 阶段1: 学任务A ----
print("阶段1: 学任务A (circles)...", flush=True)
opt=torch.optim.Adam(net.parameters(),1e-3); t=time.time()
for _ in range(400):
    loss=nn.functional.cross_entropy(net(Xa_tr),ya_tr); opt.zero_grad();loss.backward();opt.step()
print(f"  A准确率={acc(Xa_te,ya_te):.3f}  B准确率={acc(Xb_te,yb_te):.3f}  ({time.time()-t:.0f}s)\n", flush=True)

# ---- 阶段2: 学任务B, 两种策略对比 ----
def stageB(rehearse, steps=400):
    """rehearse=True: 训练B时每步混入少量A样本 (经验回放)."""
    hist_A=[]; hist_B=[]
    for _ in range(steps):
        loss=nn.functional.cross_entropy(net(Xb_tr),yb_tr)
        if rehearse:
            # 混入32个A样本 (经验回放)
            idx=torch.randint(0,len(Xa_tr),(32,)); loss=loss+nn.functional.cross_entropy(net(Xa_tr[idx]),ya_tr[idx])
        opt.zero_grad();loss.backward();opt.step()
        hist_A.append(acc(Xa_te,ya_te)); hist_B.append(acc(Xb_te,yb_te))
    return hist_A,hist_B

print("阶段2a: 纯顺序训练 B (不回放) → 预期 A 遗忘:", flush=True)
net.load_state_dict(net.state_dict())  # 保留阶段1权重
hA_forget,hB_forget = stageB(rehearse=False)
print(f"  训练B后: A准确率={hA_forget[-1]:.3f} (遗忘!)  B准确率={hB_forget[-1]:.3f}\n", flush=True)

# 重置回阶段1结束的权重 (重新训阶段1, 因为上一步把权重改了)
print("阶段2b: 重新学A, 然后带【经验回放】学B → 预期 A 保持:", flush=True)
torch.manual_seed(0)
net2=nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,2))
opt2=torch.optim.Adam(net2.parameters(),1e-3)
for _ in range(400):
    loss=nn.functional.cross_entropy(net2(Xa_tr),ya_tr); opt2.zero_grad();loss.backward();opt2.step()
# 临时把net换成net2做回放训练
net=net2; opt=opt2
def acc2(X,y):
    with torch.no_grad(): return (net(X).argmax(1)==y).float().mean().item()
hA_replay,hB_replay = stageB(rehearse=True)
print(f"  训练B后: A准确率={hA_replay[-1]:.3f} (保持!)  B准确率={hB_replay[-1]:.3f}", flush=True)

print(f"\n=== 结论 ===")
print(f"  纯顺序 : 学B后 A 从 ~1.0 崩到 {hA_forget[-1]:.3f}  ← 灾难性遗忘!")
print(f"  回放   : 学B后 A 保持 {hA_replay[-1]:.3f}         ← 经验回放缓解")

# ---- 画图 ----
fig,ax=plt.subplots(1,1,figsize=(10,5))
ax.plot(hA_forget,'r-',label='任务A 准确率 (纯顺序, 遗忘)',lw=2)
ax.plot(hB_forget,'b-',label='任务B 准确率 (纯顺序)',lw=2)
ax.plot(hA_replay,'r--',label='任务A 准确率 (经验回放, 保持)',lw=2)
ax.plot(hB_replay,'b--',label='任务B 准确率 (经验回放)',lw=2)
ax.axvline(0,color='gray',ls=':'); ax.set_xlabel("训练任务B的步数"); ax.set_ylabel("准确率")
ax.set_title("灾难性遗忘 vs 经验回放: 学新任务时, 旧任务能力怎么办?")
ax.legend(loc='center right'); ax.set_ylim(0,1.05)
fig.tight_layout(); fig.savefig("continual.png",dpi=110)
print("\n图已保存: continual.png")
