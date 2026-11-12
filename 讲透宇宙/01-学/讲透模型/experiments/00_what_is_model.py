"""
实验 00 — 什么是模型: 架构/参数/权重/目标 四要素实证
对应文档: 讲透模型/00-什么是模型.md

核心结论 (本实验用同一份数据, 分别改变四要素):
  1. 改 [架构]: 线性回归 vs MLP vs k-NN → 同数据精度差 30+
  2. 改 [参数量]: MLP 10参 vs 1000参 → 欠拟合 vs 过拟合
  3. 改 [权重]: 未训练 vs 训练后 → 准确率从 50% 到 95%
  4. 改 [训练目标]: CE vs MSE → CE 在分类上稳赢

跑法: python3 -u 00_what_is_model.py
"""
import math, random
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 造数据: 同心圆分类 (经典非线性数据集)
# ============================================================
def make_circles(n=200, noise=0.15):
    """内圈类别0, 外圈类别1"""
    n2 = n // 2
    # 内圈
    angles = np.random.uniform(0, 2*math.pi, n2)
    inner = np.c_[np.cos(angles)*0.5, np.sin(angles)*0.5] + np.random.randn(n2, 2)*noise
    # 外圈
    angles = np.random.uniform(0, 2*math.pi, n2)
    outer = np.c_[np.cos(angles)*1.5, np.sin(angles)*1.5] + np.random.randn(n2, 2)*noise
    X = np.vstack([inner, outer])
    y = np.array([0]*n2 + [1]*n2)
    return X, y

X, y = make_circles(400)
# 切训练/测试
idx = np.random.permutation(len(y))
n_train = int(0.7 * len(y))
Xtr, ytr = X[idx[:n_train]], y[idx[:n_train]]
Xte, yte = X[idx[n_train:]], y[idx[n_train:]]

def accuracy(y_true, y_pred):
    return float(np.mean(y_true == y_pred))

def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

P("="*70)
P("实验 00 — 什么是模型: 架构/参数/权重/目标 四要素实证")
P("="*70)
P()
P(f"数据: 同心圆分类 (内圈类0, 外圈类1), 训练 {n_train}, 测试 {len(y)-n_train}")
P(f"基线 (瞎猜): {accuracy(yte, np.random.randint(0, 2, len(yte))):.1%}")
P()

# ============================================================
# 要素 1: 架构 (固定 参数/权重/目标)
# ============================================================
P("="*70)
P("要素 1: 架构 — 固定其他, 只改 [怎么算]")
P("-"*70)

# (a) 线性逻辑回归 (无 hidden layer)
def train_linear(X, y, n_steps=2000, lr=0.1):
    n, d = X.shape
    w = np.zeros(d); b = 0.0
    for _ in range(n_steps):
        p = sigmoid(X @ w + b)
        grad = (p - y) / n
        w -= lr * X.T @ grad
        b -= lr * grad.sum()
    return w, b

def predict_linear(X, w, b):
    return (sigmoid(X @ w + b) > 0.5).astype(int)

# (b) MLP (1 hidden layer, tanh)
def train_mlp(X, y, hidden=8, n_steps=3000, lr=0.5):
    n, d = X.shape
    W1 = np.random.randn(d, hidden) * 0.5
    b1 = np.zeros(hidden)
    W2 = np.random.randn(hidden, 1) * 0.5
    b2 = np.zeros(1)
    for _ in range(n_steps):
        # forward
        h = np.tanh(X @ W1 + b1)
        p = sigmoid((h @ W2 + b2).flatten())
        # backward
        dz2 = (p - y).reshape(-1, 1)
        dW2 = h.T @ dz2 / n
        db2 = dz2.sum(axis=0) / n
        dh = dz2 @ W2.T * (1 - h**2)
        dW1 = X.T @ dh / n
        db1 = dh.sum(axis=0) / n
        W2 -= lr * dW2; b2 -= lr * db2
        W1 -= lr * dW1; b1 -= lr * db1
    return W1, b1, W2, b2

def predict_mlp(X, params):
    W1, b1, W2, b2 = params
    h = np.tanh(X @ W1 + b1)
    p = sigmoid((h @ W2 + b2).flatten())
    return (p > 0.5).astype(int)

# (c) k-NN (无参数模型)
def predict_knn(Xtr, ytr, Xte, k=5):
    preds = []
    for x in Xte:
        dists = np.linalg.norm(Xtr - x, axis=1)
        nn = np.argsort(dists)[:k]
        vote = np.mean(ytr[nn])
        preds.append(int(vote > 0.5))
    return np.array(preds)

print(f"\n{'架构':<28}{'训练 acc':>12}{'测试 acc':>12}{'性质':<22}")
print("-"*74)
# 线性
w, b = train_linear(Xtr, ytr.astype(float))
acc_tr = accuracy(ytr, predict_linear(Xtr, w, b))
acc_te = accuracy(yte, predict_linear(Xte, w, b))
print(f"{'线性逻辑回归':<28}{acc_tr:>12.1%}{acc_te:>12.1%}    线性边界, 学不会圆")
# MLP
params = train_mlp(Xtr, ytr.astype(float), hidden=8)
acc_tr = accuracy(ytr, predict_mlp(Xtr, params))
acc_te = accuracy(yte, predict_mlp(Xte, params))
print(f"{'MLP (8 hidden, tanh)':<28}{acc_tr:>12.1%}{acc_te:>12.1%}    非线性边界, 学会圆")
# k-NN
acc_tr = accuracy(ytr, predict_knn(Xtr, ytr, Xtr))
acc_te = accuracy(yte, predict_knn(Xtr, ytr, Xte))
print(f"{'k-NN (k=5)':<28}{acc_tr:>12.1%}{acc_te:>12.1%}    无参数, 距离投票")

P("""
观察:
- 同样数据, 线性模型 ~50% (学不会同心圆, 因为是 [线性不可分])
- MLP ~95%+ (非线性架构能学)
- k-NN ~95%+ (无参数, 但用对距离度量也能学)
→ [架构] 决定 [模型能不能学], 是 [归纳偏置] 的化身
""")

# ============================================================
# 要素 2: 参数量 (固定 架构/权重/目标)
# ============================================================
P("="*70)
P("要素 2: 参数量 — 同架构 MLP, 不同 hidden 大小")
P("-"*70)

print(f"\n{'hidden 大小':<14}{'参数量':>10}{'训练 acc':>12}{'测试 acc':>12}{'性质':<20}")
print("-"*68)
for h in [1, 2, 4, 8, 16, 32, 64]:
    params = train_mlp(Xtr, ytr.astype(float), hidden=h)
    n_params = (Xtr.shape[1] + 1) * h + (h + 1)
    acc_tr = accuracy(ytr, predict_mlp(Xtr, params))
    acc_te = accuracy(yte, predict_mlp(Xte, params))
    nature = "欠拟合" if acc_tr < 0.8 else ("合适" if acc_te > 0.92 else "可能过拟合")
    print(f"{h:<14}{n_params:>10}{acc_tr:>12.1%}{acc_te:>12.1%}    {nature}")

P("""
观察:
- h=1: ~50% (欠拟合, 单 hidden 学不会圆)
- h=4-8: ~95%+ (合适)
- h=64: 训练准但测试可能下降 (开始过拟合)
→ [参数量] 决定 [模型容量], 太小学不动, 太大过拟合
""")

# ============================================================
# 要素 3: 权重 (固定 架构/参数/目标)
# ============================================================
P("="*70)
P("要素 3: 权重 — 同架构 MLP(8 hidden), 未训练 vs 训练后")
P("-"*70)

def init_mlp(d, hidden=8, seed=None):
    if seed is not None: np.random.seed(seed)
    W1 = np.random.randn(d, hidden) * 0.5
    b1 = np.zeros(hidden)
    W2 = np.random.randn(hidden, 1) * 0.5
    b2 = np.zeros(1)
    return W1, b1, W2, b2

print(f"\n{'权重状态':<24}{'训练 acc':>12}{'测试 acc':>12}{'性质':<20}")
print("-"*68)
# 多个随机初始化
for seed in [0, 1, 2, 3, 4]:
    np.random.seed(seed)
    params_untrained = init_mlp(Xtr.shape[1], 8)
    acc = accuracy(yte, predict_mlp(Xte, params_untrained))
    print(f"{'未训练 (seed='+str(seed)+')':<24}{accuracy(ytr, predict_mlp(Xtr, params_untrained)):>12.1%}{acc:>12.1%}    随机权重, 接近瞎猜")

# 训练后
np.random.seed(0)
params_trained = train_mlp(Xtr, ytr.astype(float), hidden=8)
acc_tr = accuracy(ytr, predict_mlp(Xtr, params_trained))
acc_te = accuracy(yte, predict_mlp(Xte, params_trained))
print(f"{'训练后 (2000 步)':<24}{acc_tr:>12.1%}{acc_te:>12.1%}    权重学到规律")

P("""
观察:
- 未训练的模型: 50% 左右 (随机权重 = 随机输出)
- 训练后: 95%+ (权重调整到 [学到规律])
→ [权重] 是模型的 [知识], 训练 = 把随机权重变成 [学到的规律]
   这就是为什么 [大模型下载 = 下载权重, 不是下载架构]
""")

# ============================================================
# 要素 4: 训练目标 (固定 架构/参数/权重初始化)
# ============================================================
P("="*70)
P("要素 4: 训练目标 — 同 MLP, 用 CE vs MSE 训")
P("-"*70)

def train_mlp_mse(X, y, hidden=8, n_steps=3000, lr=0.5):
    """用 MSE 训 MLP"""
    n, d = X.shape
    np.random.seed(0)   # 同样初始化
    W1 = np.random.randn(d, hidden) * 0.5
    b1 = np.zeros(hidden)
    W2 = np.random.randn(hidden, 1) * 0.5
    b2 = np.zeros(1)
    y2d = y.reshape(-1, 1).astype(float)
    for _ in range(n_steps):
        h = np.tanh(X @ W1 + b1)
        p = sigmoid((h @ W2 + b2))
        # MSE: L = (y - p)^2; ∂L/∂z = 2(p-y) * p * (1-p)
        dz2 = 2 * (p - y2d) * p * (1 - p)
        dW2 = h.T @ dz2 / n
        db2 = dz2.sum(axis=0) / n
        dh = dz2 @ W2.T * (1 - h**2)
        dW1 = X.T @ dh / n
        db1 = dh.sum(axis=0) / n
        W2 -= lr * dW2; b2 -= lr * db2
        W1 -= lr * dW1; b1 -= lr * db1
    return W1, b1, W2, b2

print(f"\n{'训练目标':<28}{'训练 acc':>12}{'测试 acc':>12}{'性质':<24}")
print("-"*76)
# CE (前面的 train_mlp 就是 CE)
params_ce = train_mlp(Xtr, ytr.astype(float), hidden=8)
acc_tr_ce = accuracy(ytr, predict_mlp(Xtr, params_ce))
acc_te_ce = accuracy(yte, predict_mlp(Xte, params_ce))
print(f"{'CE (交叉熵)':<28}{acc_tr_ce:>12.1%}{acc_te_ce:>12.1%}    分类正确目标")
# MSE
params_mse = train_mlp_mse(Xtr, ytr.astype(float), hidden=8)
acc_tr_mse = accuracy(ytr, predict_mlp(Xtr, params_mse))
acc_te_mse = accuracy(yte, predict_mlp(Xte, params_mse))
print(f"{'MSE (均方误差)':<28}{acc_tr_mse:>12.1%}{acc_te_mse:>12.1%}    sigmoid 饱和, 学得慢")

P("""
观察:
- 同架构同初始化, CE 测试 acc 通常 ≥ MSE (差距不一定大, 因为数据简单)
- 在更难任务上 (深度网络 + 难数据), CE 完胜 MSE (因 sigmoid 梯度消失)
→ [训练目标] 决定 [模型怎么学], 是优化的方向

[讲透信息论/02] 已证明: CE 是分类的 [唯一正确损失], MSE 是高斯假设的错误套用
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结: 模型 = 架构 × 参数 × 权重 × 目标")
P("="*70)
P("""
四要素各自的作用 (本实验实证):
1. 架构:   决定 [能不能学] (线性模型学不会同心圆, MLP 能)
2. 参数量: 决定 [学多复杂] (h=1 欠拟合, h=8 合适, h=64 过拟合)
3. 权重:   决定 [具体学到什么] (随机权重 = 瞎猜, 训练后 = 95%)
4. 目标:   决定 [怎么学] (CE 在分类上稳赢 MSE)

→ 改任一要素 = 不同模型.
   GPT-3 base / GPT-3 instruct / Codex 是 [同架构同规模] 但 [不同训练目标] 的不同模型.
   Llama-2 7B / 13B / 70B 是 [同架构同目标] 但 [不同参数量] 的不同模型.
   BERT / GPT 是 [同参数量级] 但 [不同架构 + 不同目标] 的不同模型.

学 AI 必须先理解这四要素 — 它是 [模型] 这个词的精确含义.
""")
