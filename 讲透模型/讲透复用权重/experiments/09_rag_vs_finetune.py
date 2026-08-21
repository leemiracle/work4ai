"""
讲透复用权重 · 实验 09 —— RAG vs 微调: 知识更新抉择 ★进阶
================================================================
当代 LLM 应用的第一抉择: 给模型补【新知识】, 该
  ① 微调 (finetune): 把知识烧进权重 (内化)
  ② RAG (检索增强):  知识外挂数据库, 推理时查表 (外挂)

核心对比:
  - 微调: 知识在权重里, 推理快, 但【新增知识要重训】(僵化)
  - RAG:  知识在数据库, 【新增知识零成本】, 但推理要检索 (略慢)
  - 准确性: RAG 对见过的知识【精确查表】; 微调靠泛化可能记不准

本实验用一个 key→value 知识库对比两者:
  - 微调: MLP 拟合 (key,value) 对
  - RAG:   最近邻查表
  - 测试: 训练集(见过) + 新增知识(训练后加的) 的准确性

跑法:  python3 09_rag_vs_finetune.py     (CPU 约 30 秒)
输出:  rag_vs_finetune.png
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ---- 知识库: 一组 (key 1维, value 1维) 对 (模拟"事实/规则") ----
# 初始知识库 (训练用)
N_INIT = 60
keys_init = np.sort(np.random.uniform(-3, 3, N_INIT))
# value 是一个复杂分段函数 (模拟"不规则的知识")
vals_init = np.sin(keys_init*2) + 0.5*np.sign(keys_init) + 0.1*np.random.randn(N_INIT)
# 训练后【新增】的知识 (RAG 能直接用, 微调要重训)
keys_new = np.array([-2.7, 2.9])
vals_new = np.array([2.0, -2.0])

# 测试集
keys_te = np.linspace(-3.2, 3.2, 200)
vals_te_true = np.sin(keys_te*2) + 0.5*np.sign(keys_te)   # 无噪声真值

K_init = torch.tensor(keys_init[:,None],dtype=torch.float32)
V_init = torch.tensor(vals_init[:,None],dtype=torch.float32)

# ---- ① 微调方案: MLP 拟合知识库 (烧进权重) ----
print("① 微调方案: MLP 学习知识库...", flush=True)
net=nn.Sequential(nn.Linear(1,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,1))
opt=torch.optim.Adam(net.parameters(),1e-3)
for _ in range(2000):
    pred=net(K_init); loss=nn.functional.mse_loss(pred,V_init); opt.zero_grad();loss.backward();opt.step()
with torch.no_grad(): ft_init=((net(K_init)-V_init)**2).mean().item()  # 见过知识的MSE
print(f"   微调在【见过知识】上 MSE={ft_init:.4f}", flush=True)

# 微调对【新增知识】的表现 (它没见过, 只能泛化/瞎猜)
K_new=torch.tensor(keys_new[:,None],dtype=torch.float32); V_new=torch.tensor(vals_new[:,None],dtype=torch.float32)
with torch.no_grad(): ft_new=((net(K_new)-V_new)**2).mean().item()
print(f"   微调在【新增知识】上 MSE={ft_new:.4f}  (没见过, 只能泛化, 记不准!)", flush=True)

# ---- ② RAG 方案: 最近邻查表 ----
print("\n② RAG 方案: 最近邻查表...", flush=True)
def rag_predict(query_keys, db_keys, db_vals):
    """对每个query, 找db里最近的key, 返回其value."""
    q = query_keys[:,None]; d = db_keys[None,:]
    dist = np.abs(q - d); nn_idx = dist.argmin(1)
    return db_vals[nn_idx]

# RAG 对见过知识 (用init库查init)
rag_init = rag_predict(keys_init, keys_init, vals_init)
rag_init_mse = ((rag_init - vals_init)**2).mean()
# RAG 对新增知识: 用 init 库查 → 没有新增点, 靠最近邻近似 (不准)
rag_new_oldlib = rag_predict(keys_new, keys_init, vals_init)
rag_new_oldlib_mse = ((rag_new_oldlib - vals_new)**2).mean()
print(f"   RAG(init库) 在【见过知识】上 MSE={rag_init_mse:.4f}  (精确查表!)", flush=True)
print(f"   RAG(init库) 在【新增知识】上 MSE={rag_new_oldlib_mse:.4f}  (库没有, 靠最近邻近似)", flush=True)

# ★ RAG 的杀手锏: 把新增知识加入库, 立即精确!
db_keys = np.concatenate([keys_init, keys_new]); db_vals = np.concatenate([vals_init, vals_new])
rag_new_newlib = rag_predict(keys_new, db_keys, db_vals)
rag_new_newlib_mse = ((rag_new_newlib - vals_new)**2).mean()
print(f"   RAG(+新增库) 在【新增知识】上 MSE={rag_new_newlib_mse:.4f}  ← 零成本重训, 立即精确!", flush=True)

print(f"\n=== 核心对比 ===")
print(f"  对【新增知识】:")
print(f"    微调        : MSE={ft_new:.3f}  (必须重训才能学会)")
print(f"    RAG(+新库)  : MSE={rag_new_newlib_mse:.3f}  (加条记录立即生效, 零训练成本)")

# ---- 画图 ----
fig,axes=plt.subplots(1,2,figsize=(13,5))
with torch.no_grad(): ft_curve=net(torch.tensor(keys_te[:,None],dtype=torch.float32)).numpy()
rag_curve = rag_predict(keys_te, db_keys, db_vals)
axes[0].plot(keys_te, vals_te_true, 'k-', label='真值', alpha=0.5)
axes[0].plot(keys_te, ft_curve, 'C0-', label='微调(烧进权重)', lw=2)
axes[0].scatter(keys_init, vals_init, s=20, c='gray', label='训练知识', zorder=3)
axes[0].scatter(keys_new, vals_new, s=120, c='red', marker='*', label='★新增知识', zorder=4)
axes[0].set_title("微调: 新增知识(红星)没见过 → 泛化/记不准"); axes[0].legend(fontsize=9); axes[0].set_ylim(-3,3)
axes[1].plot(keys_te, vals_te_true, 'k-', label='真值', alpha=0.5)
axes[1].plot(keys_te, rag_curve, 'C2-', label='RAG(查表)', lw=2)
axes[1].scatter(keys_init, vals_init, s=20, c='gray', label='库中知识', zorder=3)
axes[1].scatter(keys_new, vals_new, s=120, c='red', marker='*', label='★新增(已加入库)', zorder=4)
axes[1].set_title("RAG: 新增知识加入库 → 立即精确返回"); axes[1].legend(fontsize=9); axes[1].set_ylim(-3,3)
fig.suptitle("RAG vs 微调: 微调内化知识(僵化), RAG外挂知识(灵活, 新增零成本)", fontsize=12)
fig.tight_layout(); fig.savefig("rag_vs_finetune.png",dpi=110)
print("\n图已保存: rag_vs_finetune.png")
