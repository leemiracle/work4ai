"""
讲透生成模型 · 实验 06 —— 统一视角: Score (分数) 与朗之万采样 ★
================================================================
本实验用【解析】方式 (无需训练) 展示『分数类』的核心直觉:
  分数 s(x) = ∇_x log p(x)  = 分布在每个点的『斜率』, 指向更高密度方向
  朗之万采样: 从随机点出发, 顺着分数走, 就能收敛到数据模态 —— 这就是生成!

第5章的『预测噪声 ε_θ』数学上正比于『负分数』, 所以 DDPM ≡ 分数匹配.
本实验把这个等价关系用一张『分数箭头场 + 朗之万轨迹』图直观化.

跑法:  python3 06_score.py     (CPU 约 5 秒, 纯解析无训练)
输出:  score_field.png  (分数场 + 朗之万采样轨迹 + 最终样本)
"""
import math
import numpy as np
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

np.random.seed(0)

# ------------------------------------------------------------------
# 1. 定义一个已知分布: 两个高斯团的混合 (这样分数能解析算)
#    p(x) = 0.5 N(μ1, σ²I) + 0.5 N(μ2, σ²I)
# ------------------------------------------------------------------
MU = np.array([[-1.6, 0.0], [1.6, 0.0]])     # 两个模态中心
SD = 0.35                                     # 每团标准差

def gauss_pdf(x, mu, s):
    d = x - mu
    return np.exp(-(d**2).sum(1)/(2*s**2)) / (2*np.pi*s**2)

def p_mix(x):                                 # 混合密度
    return 0.5*gauss_pdf(x, MU[0], SD) + 0.5*gauss_pdf(x, MU[1], SD)

def score(x):                                 # ★ 分数 ∇log p(x), 解析
    p0 = gauss_pdf(x, MU[0], SD); p1 = gauss_pdf(x, MU[1], SD)
    r0 = 0.5*p0/(0.5*p0+0.5*p1 + 1e-12)       # 责任度 r_k
    r1 = 0.5*p1/(0.5*p0+0.5*p1 + 1e-12)
    s0 = -(x - MU[0])/(SD**2)                 # 每团的分数 = -(x-μ)/σ²
    s1 = -(x - MU[1])/(SD**2)
    return r0[:,None]*s0 + r1[:,None]*s1      # 混合分数 = 责任度加权

# ------------------------------------------------------------------
# 2. 朗之万动力学采样 (Langevin dynamics) —— 顺着分数走回模态
#    x_{k+1} = x_k + (η/2)·∇log p(x_k) + √η · ε
#    第一项: 顺分数爬向高密度; 第二项: 随机扰动 (防止卡死)
# ------------------------------------------------------------------
def langevin(n=1500, steps=200, eta=0.15):
    x = np.random.uniform(-3, 3, (n, 2))      # 从均匀分布(≈噪声)出发
    traj = [x.copy()]
    for _ in range(steps):
        x = x + (eta/2)*score(x) + np.sqrt(eta)*np.random.randn(n,2)
        if _ % 40 == 0: traj.append(x.copy())
    traj.append(x.copy())
    return x, traj

final, traj = langevin()

# 真实样本 (从分布直接采, 作参照)
def true_sample(n=1500):
    k = np.random.randint(0,2,n)
    return MU[k] + SD*np.random.randn(n,2)
true = true_sample()

# ------------------------------------------------------------------
# 3. 画图: 左=分数箭头场; 中=朗之万轨迹(几步快照); 右=最终样本 vs 真实
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15,5))
g = np.linspace(-3.2, 3.2, 17)
XX, YY = np.meshgrid(g, g)
grid = np.c_[XX.ravel(), YY.ravel()]
sv = score(grid).reshape(XX.shape[0], XX.shape[1], 2)

# 左: 分数场
ax = axes[0]
ax.quiver(XX, YY, sv[:,:,0], sv[:,:,1], color="C0", scale=80)
ax.scatter(true[:,0], true[:,1], s=4, c="k", alpha=0.2)
ax.set_title("分数场 ∇log p(x)\n箭头指向高密度(模态)\n黑点=真实数据"); ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect("equal")

# 中: 朗之万轨迹 (起点均匀 → 收敛到两团)
ax = axes[1]
colors = plt.cm.viridis(np.linspace(0,1,len(traj)))
for i,t in enumerate(traj):
    ax.scatter(t[:,0], t[:,1], s=3, c=[colors[i]], alpha=0.5)
ax.set_title(f"朗之万采样轨迹\n(均匀起点 → 顺分数走 → 收敛到模态)\n{len(traj)} 个快照"); ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect("equal")

# 右: 最终样本 vs 真实
ax = axes[2]
ax.scatter(true[:,0], true[:,1], s=8, c="k", alpha=0.3, label="真实")
ax.scatter(final[:,0], final[:,1], s=8, c="C3", alpha=0.5, label="朗之万生成")
ax.set_title("朗之万生成 vs 真实\n(只靠分数就收敛到正确分布)"); ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect("equal"); ax.legend()

fig.suptitle("分数类的灵魂: 学会∇log p(x), 顺着它走, 就能从噪声生成数据 (DDPM≡此理)", fontsize=12)
fig.tight_layout(); fig.savefig("score_field.png", dpi=110)
print("图已保存: score_field.png")
print("\n要点:")
print("  1. 分数 ∇log p(x) 指向高密度区 —— 它是『往哪走能到数据』的路标.")
print("  2. 朗之万采样: 顺分数走 + 随机扰动 → 收敛到真实分布.  这就是『生成』.")
print("  3. DDPM 的『预测噪声 ε_θ』正比于『-分数』, 所以扩散 ≡ 分数匹配 ≡ 朗之万采样.")
print("  4. 这套统一视角 (Song Yang, 2021) 把 DDPM/分数匹配/SDE 串成一件事.")
