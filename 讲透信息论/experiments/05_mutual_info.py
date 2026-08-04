"""
实验 05 — 互信息: 特征选择 / InfoNCE / 对比学习
对应文档: 讲透信息论/05-互信息.md

核心结论:
  1. I(X;Y) = H(X) - H(X|Y): Y 提供了关于 X 的多少信息
  2. 特征选择: 选与标签互信息最大的特征, 比 Pearson 相关更鲁棒 (非线性)
  3. InfoNCE 是互信息的下界估计: L_NCE = -log(e^s+ / Σ e^s_i)
  4. 对比学习 (SimCLR/CLIP) 本质: 最大化同一样本两个 view 的互信息

跑法: python3 -u 05_mutual_info.py
"""
import math, random
from collections import Counter
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

def entropy_bits(p_list):
    """离散分布的熵"""
    H = 0
    for p in p_list:
        if p > 0: H -= p * math.log2(p)
    return H

def mutual_information(joint_counts):
    """从联合计数算互信息. joint_counts: dict[(x,y) -> count]"""
    total = sum(joint_counts.values())
    px = Counter(); py = Counter()
    for (x, y), c in joint_counts.items():
        px[x] += c; py[y] += c
    I = 0
    for (x, y), c in joint_counts.items():
        pxy = c / total
        if pxy > 0:
            I += pxy * math.log2(pxy / (px[x]/total * py[y]/total))
    return I

# ============================================================
# Part 1: 互信息 I(X;Y) 在三种相关度下的对比
# ============================================================
P("="*70)
P("实验 05 — 互信息: 特征选择 / InfoNCE / 对比学习")
P("="*70)
P()
P("Part 1: 互信息 I(X;Y) — 度量变量间的依赖")
P("-"*70)
P()

# 模拟 3 种 X-Y 关系, 各采样 5000 次
N = 5000

# (a) 完全独立: X, Y 各是公平币
mi_indep = Counter()
for _ in range(N):
    x = random.randint(0, 1); y = random.randint(0, 1)
    mi_indep[(x, y)] += 1

# (b) 完全相关: Y = X
mi_corr = Counter()
for _ in range(N):
    x = random.randint(0, 1); y = x
    mi_corr[(x, y)] += 1

# (c) 部分相关: Y = X 异或 噪声(20% 翻转)
mi_partial = Counter()
for _ in range(N):
    x = random.randint(0, 1)
    y = x if random.random() > 0.2 else (1 - x)
    mi_partial[(x, y)] += 1

print(f"{'关系':<20}{'I(X;Y) bit':>14}{'解读':<30}")
print("-"*64)
for name, mi in [("X, Y 独立",       mi_indep),
                  ("X = Y 完全相关",   mi_corr),
                  ("Y = X ⊕ 20%噪声",  mi_partial)]:
    I = mutual_information(mi)
    meaning = ("Y 不携带 X 的信息" if I < 0.01 else
               "Y 完全确定 X" if I > 0.95 else
               "Y 部分携带 X 的信息")
    print(f"{name:<20}{I:>14.4f}    {meaning}")

P("""
核心公式:
  I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X) = H(X) + H(Y) - H(X,Y)
  - I = 0 ⟺ X, Y 独立
  - I = H(X) ⟺ Y 完全确定 X
  - I 是对称的: I(X;Y) = I(Y;X)
""")

# ============================================================
# Part 2: 特征选择 — 哪个特征最有信息量?
# ============================================================
P("="*70)
P("Part 2: 特征选择 — 互信息 vs Pearson 相关")
P("-"*70)

# 造数据: 标签 y 由特征决定, 但关系非线性
N_samples = 2000
x_linear = np.random.randn(N_samples)            # 与 y 线性相关
x_nonlinear = np.random.randn(N_samples)         # 与 y 非线性相关 (cos)
x_noise = np.random.randn(N_samples)             # 与 y 无关

y = (x_linear + np.cos(x_nonlinear * 2) + np.random.randn(N_samples) * 0.3 > 0).astype(int)

def discretize(x, n_bins=10):
    """把连续变量离散化为 n_bins 个等频桶"""
    edges = np.quantile(x, np.linspace(0, 1, n_bins+1))
    return np.digitize(x, edges[1:-1])

def feature_mutual_info(x, y, n_bins=10):
    """特征 x (连续) 与 y (离散) 的互信息"""
    x_discrete = discretize(x, n_bins)
    joint = Counter(zip(x_discrete, y))
    return mutual_information(joint)

def pearson_corr(x, y):
    """Pearson 相关系数"""
    xm, ym = x.mean(), y.mean()
    num = np.mean((x - xm) * (y - ym))
    den = np.std(x) * np.std(y)
    return num / den if den > 0 else 0

features = [
    ("x_linear (与 y 线性)", x_linear),
    ("x_nonlinear (cos)",   x_nonlinear),
    ("x_noise (无关)",       x_noise),
]
print(f"\n{'特征':<26}{'互信息 I':>12}{'|Pearson|':>12}{'真实关系':<20}")
print("-"*70)
for name, x in features:
    mi = feature_mutual_info(x, y)
    pcc = abs(pearson_corr(x, y))
    rel = "线性" if "linear" in name else "非线性" if "nonlinear" in name else "无关"
    print(f"{name:<26}{mi:>12.4f}{pcc:>12.4f}    {rel}")

P("""
关键观察:
- x_linear: 互信息和 Pearson 都高 (线性关系两者都抓住)
- x_nonlinear: 互信息高 (~0.15), Pearson 几乎 0! (cos 关系是 [非线性], Pearson 抓不到)
- x_noise: 两者都 ~0

→ 互信息能抓住 [非线性依赖], Pearson 只能抓 [线性].
   这是为什么 sklearn 的 mutual_info_classif 在特征选择里更鲁棒.
""")

# ============================================================
# Part 3: InfoNCE — 对比学习的损失 = 互信息下界
# ============================================================
P("="*70)
P("Part 3: InfoNCE — 互信息下界估计 (对比学习损失)")
P("-"*70)
P()
P("InfoNCE 公式:")
P("  L_NCE = -log[ exp(s(x, y+) / τ) / Σ_i exp(s(x, y_i) / τ) ]")
P()
P("定理 (Oord 2018): L_NCE ≥ log(K) - I(X;Y), 其中 K 是负样本数")
P("  → 最小化 L_NCE = 最大化 I(X;Y) 的下界")
P()

# 模拟 InfoNCE: x 是 query, y+ 是正样本, y_i 是负样本
# 用 cos 相似度作为 score, τ=0.5
def info_nce_loss(positive_sim, negative_sims, tau=0.5):
    """positive_sim, negative_sims 是 cos 相似度"""
    numerator = math.exp(positive_sim / tau)
    denominator = numerator + sum(math.exp(s / tau) for s in negative_sims)
    return -math.log(numerator / denominator)

# 实验: 当正样本越相似 (高互信息), InfoNCE loss 越小
print(f"{'正样本相似度':>16}{'负样本平均相似度':>20}{'InfoNCE loss':>16}{'等效互信息估计':>18}")
print("-"*72)

random.seed(0)
for pos_sim in [0.95, 0.8, 0.6, 0.4, 0.2]:
    # 模拟 batch: 1 正 + 9 负
    neg_sims = [random.uniform(-0.3, 0.3) for _ in range(9)]
    loss = info_nce_loss(pos_sim, neg_sims, tau=0.5)
    # 等效互信息估计 (Oord 定理): I_est ≈ log(K) - loss
    I_est = math.log(1 + len(neg_sims)) - loss
    print(f"{pos_sim:>16.2f}{sum(neg_sims)/len(neg_sims):>20.4f}{loss:>16.4f}{I_est:>18.4f}")

P("""
关键观察:
- 正样本相似度越高 → InfoNCE loss 越小 → 估计的互信息越大
- InfoNCE 是 [互信息下界]: I(X;Y) ≥ log(K) - L_NCE
- 增大 K (负样本数) → log(K) 增大 → 估计更紧 (但计算成本也增大)

对比学习 (SimCLR/CLIP/MoCo) 本质:
- 把同一样本的两个 view (data augmentation) 当作正样本
- 把其他样本当作负样本
- 最小化 InfoNCE → 最大化同一样本两 view 的互信息
- 学到的表示 = 保留样本本质信息, 抛弃 augmentation 噪声
""")

# ============================================================
# Part 4: 互信息在 AI 中的其他应用
# ============================================================
P("="*70)
P("Part 4: 互信息 → AI 的全景")
P("-"*70)
P("""
互信息是连接信息论和现代 AI 的核心概念:

1. 【特征选择】 (本实验 Part 2)
   sklearn.feature_selection.mutual_info_classif
   选与标签互信息最大的特征, 抓住非线性依赖.

2. 【对比学习】 (本实验 Part 3)
   SimCLR/CLIP/MoCo 都用 InfoNCE, 本质是 [最大化互信息下界].

3. 【VAE 的 ELBO】
   ELBO = 重构项 + KL(q(z|x) || p(z))
   训练 VAE = 最大化数据 x 和隐变量 z 的互信息 (受 KL 约束).

4. 【信息瓶颈 (Information Bottleneck)】
   Tishby 理论: 深度网络训练 = 压缩 I(X;hidden) + 保留 I(hidden;Y).
   解释了为什么深度网络能泛化.

5. 【独立成分分析 (ICA)】
   找到组件使得它们互信息最小 (= 相互独立).
   用于盲源分离 (鸡尾酒会问题).

6. 【互信息估计 (MINE, InfoNCE)】
   直接用神经网络估计高维变量的互信息, 解决传统方法维度爆炸问题.
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
互信息 I(X;Y) = H(X) - H(X|Y) 是 [变量间依赖] 的精确度量.
- 范围 [0, min(H(X), H(Y))], 0=独立, max=完全相关
- 比Pearson更强: 能抓非线性依赖 (实测 cos 关系 Pearson≈0, 互信息 ~0.15)
- InfoNCE 是互信息下界估计, 是对比学习 (SimCLR/CLIP) 的核心损失
- 互信息贯穿: 特征选择 / 对比学习 / VAE ELBO / 信息瓶颈 / ICA / MINE
""")
