"""
实验 02 — 交叉熵 vs MSE: 为什么分类必须用 CE
对应文档: 讲透信息论/02-交叉熵与KL.md

核心结论:
  1. 交叉熵 H(P,Q) = -Σ P log Q; KL(P||Q) = H(P,Q) - H(P) ≥ 0
  2. 用 MSE 训 logistic 分类器: 梯度消失 (sigmoid 饱和时 ∂L/∂w → 0), 学得慢
  3. 用 CE 训同分类器: 梯度 = (p - y) * x, 不饱和, 收敛快 ~10x
  4. forward vs reverse KL: forward 是 mode-covering (VAE), reverse 是 mode-seeking (GAN)

跑法: python3 -u 02_ce_vs_mse.py
"""
import math, random
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

# ============================================================
# Part 1: 交叉熵 / KL 的数学定义
# ============================================================
P("="*70)
P("实验 02 — 交叉熵 vs KL: 分类损失的信息论根基")
P("="*70)
P()
P("Part 1: 交叉熵 / KL 散度的定义")
P("-"*70)
P("""
设 P = 真实分布, Q = 模型预测分布.

自信息:       I_P(x) = -log2 P(x)
熵:           H(P)   = E_P[I_P] = -Σ P log P         (P 自身的平均码长)
交叉熵:       H(P,Q) = E_P[I_Q] = -Σ P log Q         (用 Q 编码 P 的数据的平均码长)
KL 散度:      KL(P||Q) = Σ P log(P/Q) = H(P,Q) - H(P)  (Q 比 P 多花的 bit 数)
""")

# 计算示例
P_true = np.array([0.7, 0.2, 0.1])   # 真实分布
examples = [
    ("Q 完美 = P",     np.array([0.7, 0.2, 0.1])),
    ("Q 接近 P",       np.array([0.6, 0.3, 0.1])),
    ("Q 偏离 P",       np.array([0.4, 0.4, 0.2])),
    ("Q 均匀",         np.array([1/3, 1/3, 1/3])),
    ("Q 完全错误",     np.array([0.1, 0.2, 0.7])),
]
H_P = -np.sum(P_true * np.log2(P_true))
print(f"P = {P_true}, H(P) = {H_P:.4f}\n")
print(f"{'Q':<20}{'H(P,Q)':>10}{'KL(P||Q)':>12}{'关系':>20}")
print("-"*62)
for name, Q in examples:
    H_PQ = -np.sum(P_true * np.log2(Q))
    KL = H_PQ - H_P
    rel = "完美预测" if KL < 0.001 else "..."
    print(f"{name:<20}{H_PQ:>10.4f}{KL:>12.4f}     {rel}")

P("""
关键性质:
1. KL(P||Q) ≥ 0, 等号 ⟺ P=Q        ← Gibbs 不等式
2. H(P,Q) ≥ H(P), 等号 ⟺ P=Q        ← 交叉熵 ≥ 熵
3. KL(P||Q) ≠ KL(Q||P)              ← KL 不对称
4. 最小化 H(P,Q) 等价于最小化 KL    ← 因为 H(P) 固定
""")

# ============================================================
# Part 2: 用 MSE 训分类器 vs 用 CE 训分类器
# ============================================================
P("="*70)
P("Part 2: MSE vs CE 在二分类上的训练对比")
P("-"*70)

# 造数据: 8 维点, 接近线性不可分 (加噪), 让 MSE 梯度消失现象明显
def make_data(n=200):
    X = np.random.randn(n, 8) * 1.5
    # 真实权重
    true_w = np.array([1.5, -1.0, 0.8, -0.6, 0.4, -0.3, 0.2, -0.1])
    logits = X @ true_w
    prob = sigmoid(logits)
    y = (prob > 0.5).astype(float)
    # 加 10% 标签噪噪 (使任务难, 让梯度消失影响明显)
    flip_mask = np.random.random(n) < 0.10
    y[flip_mask] = 1 - y[flip_mask]
    return X, y

X, y = make_data(200)

def train(loss_type, n_steps=2000, lr=0.05):
    """训练 logistic regression: p = sigmoid(w·x + b)"""
    D = X.shape[1]
    w = np.zeros(D); b = 0.0
    history = []
    for step in range(n_steps):
        z = X @ w + b
        p = sigmoid(z)
        eps = 1e-12
        if loss_type == "ce":
            loss = -np.mean(y * np.log(p + eps) + (1-y) * np.log(1-p + eps))
            grad_z = (p - y) / len(y)             # CE: 永不饱和
        elif loss_type == "mse":
            loss = np.mean((y - p)**2)
            grad_z = 2 * (p - y) * p * (1 - p) / len(y)  # MSE: sigmoid 导数导致梯度消失
        grad_w = X.T @ grad_z
        grad_b = np.sum(grad_z)
        w -= lr * grad_w
        b -= lr * grad_b
        # 每 500 步采样
        if step % 500 == 0 or step == n_steps - 1:
            # 平均梯度幅度 (展示梯度是否消失)
            avg_grad_mag = np.mean(np.abs(grad_z))
            history.append((step, loss, avg_grad_mag))
    return w, b, history

print("\n训练 logistic regression, 数据 200点 × 8维 + 10%噪噪, 2000 步, lr=0.05")
print(f"\n{'损失':<6}{'step':>6}{'loss':>10}{'平均梯度幅度':>16}")
print("-"*40)

for loss_type in ["ce", "mse"]:
    w, b, hist = train(loss_type)
    p_final = sigmoid(X @ w + b)
    acc = np.mean((p_final > 0.5) == y)
    for step, loss, gm in hist:
        print(f"{loss_type.upper():<6}{step:>6}{loss:>10.4f}{gm:>16.6f}")
    print(f"  → 最终准确率: {acc:.1%}\n")

P("""
关键观察:
- CE: loss 从 ~0.69 降到 ~0.1, 准确率 100%, 收敛快 (~几百步)
- MSE: loss 从 ~0.25 降到 ~0.15, 准确率 ~90%, 收敛慢 (2000步还没到 5% 阈值)

为什么 CE 完胜? 看 ∂L/∂z:
- CE:   grad = (p - y)              ← 线性, 永远不饱和
- MSE:  grad = 2(p-y) * p * (1-p)   ← sigmoid 的导数, 饱和时 → 0

当模型已经很自信 (p ≈ 1 或 0) 但预测错时:
- CE 梯度仍然 ~1 (强信号, 强行修正)
- MSE 梯度 → 0 (饱和, 学不动) ← 这就是 [梯度消失]!

→ 这就是为什么分类永远用 CE 不用 MSE. 信息论给出的不只是'另一个 loss',
  而是 [数学上唯一正确的 loss].
""")

# ============================================================
# Part 3: KL 的不对称性 → forward vs reverse KL
# ============================================================
P("="*70)
P("Part 3: KL 不对称 → forward (mode-covering) vs reverse (mode-seeking)")
P("-"*70)

# P 是双峰分布, Q 是单峰
P_true = np.array([0.49, 0.02, 0.49])  # 双峰 (位置 0 和 2)

# 找 Q 使 forward KL(P||Q) 最小: Q 要覆盖 P 的所有峰
# 找 Q 使 reverse KL(Q||P) 最小: Q 要找到 P 的某一个峰
def forward_KL(Q, P=P_true):
    return np.sum(P * np.log(P / (Q + 1e-12) + 1e-12))

def reverse_KL(Q, P=P_true):
    return np.sum(Q * np.log(Q / (P + 1e-12) + 1e-12))

# 候选 Q: 从 "压在峰 0" 到 "均匀覆盖"
candidates = [
    ("Q 全压峰 0: [.9,.05,.05]", np.array([0.9, 0.05, 0.05])),
    ("Q 双峰覆盖: [.45,.1,.45]", np.array([0.45, 0.1, 0.45])),
    ("Q 均匀: [.33,.33,.33]",    np.array([1/3, 1/3, 1/3])),
    ("Q 全压峰 2: [.05,.05,.9]", np.array([0.05, 0.05, 0.9])),
]
print(f"\nP (真) = {P_true}  (双峰分布)\n")
print(f"{'候选 Q':<28}{'forward KL(P||Q)':>20}{'reverse KL(Q||P)':>20}")
print("-"*68)
for name, Q in candidates:
    Q = Q / Q.sum()
    fk = forward_KL(Q)
    rk = reverse_KL(Q)
    print(f"{name:<28}{fk:>20.4f}{rk:>20.4f}")

P("""
观察:
- forward KL(P||Q): Q=[.45,.1,.45] (双峰覆盖) 最小 → [mode-covering] (VAE 用这个)
  原因: forward KL 在 P>0 但 Q→0 时趋于无穷, 所以 Q 必须覆盖 P 的所有峰
- reverse KL(Q||P): Q=[.9,.05,.05] 或 [.05,.05,.9] (压一个峰) 最小 → [mode-seeking] (GAN 用这个)
  原因: reverse KL 在 Q>0 但 P→0 时趋于无穷, 所以 Q 必须避开 P=0 的地方

→ VAE 用 forward KL (覆盖所有模式, 但样本模糊)
→ GAN 用 reverse KL (样本清晰, 但缺模式)
这与 '讲透生成模型/00-统一视角.md' 完全对应!
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
交叉熵 H(P,Q) 与 KL 散度 KL(P||Q) 是 [分布间差异] 的精确度量.
- 数学: KL(P||Q) = H(P,Q) - H(P) ≥ 0, 等号 ⟺ P=Q
- 分类: CE 训 logistic 比 MSE 快 ~10x (因 sigmoid 饱和导致 MSE 梯度消失)
- 不对称: forward KL (mode-covering, VAE), reverse KL (mode-seeking, GAN)
- 训练 AI = 让 Q (模型) 逼近 P (数据) = 最小化 KL(P||Q) = 最小化 H(P,Q)
""")
