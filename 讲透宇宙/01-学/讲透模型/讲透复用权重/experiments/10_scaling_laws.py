"""
讲透复用权重 · 实验 10 —— 预训练 Scaling Laws: Chinchilla 定律 ★进阶
===================================================================
神经缩放定律 (Neural Scaling Laws): 模型 loss 随【参数量 N】【数据量 D】【算力 C】
幂律下降:  L(N,D) ≈ A/N^α + B/D^β + L∞

关键洞察 (Chinchilla, DeepMind 2022):
  - 给定算力 C, 存在【最优的 N 和 D 配比】——不是模型越大越好
  - Chinchilla 定律: 最优 D/N ≈ 20 (每参数配 ~20 个token)
  - 这纠正了 GPT-3 时代"只堆参数、数据不够"的误区

本实验在玩具回归任务上拟合缩放定律:
  ① 扫参数量 (隐藏宽度): loss 随参数幂律下降
  ② 扫数据量: loss 随数据幂律下降
  ③ 演示"小模型+多数据" 可媲美 "大模型+少数据" (Chinchilla 精神)

跑法:  python3 10_scaling_laws.py     (CPU 约 70 秒)
输出:  scaling_laws.png  (log-log 幂律图)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- 任务: y = sin(2x) + 0.5x, 回归 ----
def make_data(n, noise=0.1):
    x = np.random.uniform(-3, 3, n)
    y = np.sin(2*x) + 0.5*x + noise*np.random.randn(n)
    return torch.tensor(x[:,None],dtype=torch.float32), torch.tensor(y[:,None],dtype=torch.float32)
Xte,Yte = make_data(2000, noise=0)   # 无噪声测试集 (测真实逼近能力)

def make_net(width):
    return nn.Sequential(nn.Linear(1,width),nn.ReLU(),nn.Linear(width,width),nn.ReLU(),nn.Linear(width,1))
def nparam(m): return sum(p.numel() for p in m.parameters())

def train_eval(width, n_data, steps=500):
    torch.manual_seed(0)
    Xtr,Ytr = make_data(n_data)
    net=make_net(width); opt=torch.optim.Adam(net.parameters(),1e-3)
    for _ in range(steps):
        loss=nn.functional.mse_loss(net(Xtr),Ytr); opt.zero_grad();loss.backward();opt.step()
    with torch.no_grad(): test_mse=nn.functional.mse_loss(net(Xte),Yte).item()
    return test_mse, nparam(net)

print("① 扫参数量 (隐藏宽度), 固定大数据 2000:\n", flush=True)
widths=[8,16,32,64,128,256]; res_N=[]
for w in widths:
    mse,npar=train_eval(w, 2000); res_N.append((npar,mse))
    print(f"   宽度={w:>3d} 参数={npar:>6d}  test MSE={mse:.4f}", flush=True)

print("\n② 扫数据量, 固定大模型 (宽度128):\n", flush=True)
datas=[25,50,100,300,1000,3000]; res_D=[]
for d in datas:
    mse,npar=train_eval(128, d); res_D.append((d,mse))
    print(f"   数据={d:>4d}  参数={npar}  test MSE={mse:.4f}", flush=True)

# ---- 拟合幂律 log(L) = -α log(N) + c ----
def fit_power(x, y):
    lx,ly=np.log(x),np.log(y); A=np.vstack([lx,np.ones_like(lx)]).T
    alpha, c = np.linalg.lstsq(A,ly,rcond=None)[0]
    return alpha, np.exp(c)
alphaN, cN = fit_power([r[0] for r in res_N],[r[1] for r in res_N])
alphaD, cD = fit_power([r[0] for r in res_D],[r[1] for r in res_D])
print(f"\n拟合幂律: loss ~ N^(-{alphaN:.2f})  (参数量);  loss ~ D^(-{alphaD:.2f}) (数据量)", flush=True)
print(f"(真实大模型 α≈0.05~0.10; 玩具任务 α 偏大, 但幂律形状成立)")

# ---- Chinchilla 精神演示: 小模型+多数据 vs 大模型+少数据, 同算力 ----
print("\n③ Chinchilla 精神: 固定算力(~等参数×数据), 哪种配比赢?", flush=True)
# 大模型少数据 vs 小模型多数据 (近似等算力: 参数×数据 接近)
cfgs = [("大模型少数据", 256, 100), ("平衡", 64, 800), ("小模型多数据", 16, 3000)]
for tag,w,d in cfgs:
    mse,npar=train_eval(w,d,steps=400)
    print(f"   {tag}: 宽度{w:>3d}({npar}参) + 数据{d:>4d}  → 算力~{npar*d//1000}K  MSE={mse:.4f}", flush=True)

# ---- 画图 (log-log) ----
fig,axes=plt.subplots(1,2,figsize=(13,5))
N_arr=np.array([r[0] for r in res_N]); L_arr=np.array([r[1] for r in res_N])
axes[0].loglog(N_arr,L_arr,'bo-',label='实测'); axes[0].loglog(N_arr,cN*N_arr**(-alphaN),'b--',label=f'拟合 N^(-{alphaN:.2f})')
axes[0].set_title("Loss vs 参数量 N (幂律下降)"); axes[0].set_xlabel("参数量 N"); axes[0].set_ylabel("test MSE"); axes[0].legend(); axes[0].grid(True,which='both',alpha=0.3)
D_arr=np.array([r[0] for r in res_D]); Ld_arr=np.array([r[1] for r in res_D])
axes[1].loglog(D_arr,Ld_arr,'rs-',label='实测'); axes[1].loglog(D_arr,cD*D_arr**(-alphaD),'r--',label=f'拟合 D^(-{alphaD:.2f})')
axes[1].set_title("Loss vs 数据量 D (幂律下降)"); axes[1].set_xlabel("数据量 D"); axes[1].set_ylabel("test MSE"); axes[1].legend(); axes[1].grid(True,which='both',alpha=0.3)
fig.suptitle("神经缩放定律: loss 随参数/数据幂律下降 → Chinchilla: 最优 D/N≈20", fontsize=12)
fig.tight_layout(); fig.savefig("scaling_laws.png",dpi=110)
print("\n图已保存: scaling_laws.png")
