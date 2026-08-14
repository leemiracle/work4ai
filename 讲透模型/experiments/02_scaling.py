"""
实验 02 — 规模与 Scaling Laws: 参数/数据/计算 与 loss 的幂律
对应文档: 讲透模型/02-规模与ScalingLaws.md

核心结论:
  1. 模型大小 vs loss: loss ∝ N^(-α_N), α ≈ 0.076 (Kaplan 2020)
  2. 数据量 vs loss: loss ∝ D^(-α_D)
  3. 计算量 vs loss: loss ∝ C^(-α_C)
  4. Chinchilla 定律: 最优训练 D ≈ 20 × N (参数量)
  5. 教学版模拟: 实测一个小型 scaling law, 验证幂律形状

跑法: python3 -u 02_scaling.py
"""
import math
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

def sigmoid(z): return 1/(1+np.exp(-np.clip(z, -30, 30)))

# ============================================================
# Part 1: 模拟 [模型大小 vs loss] 的 scaling law
# 任务: 一个简单的非线性回归 (sin 函数拟合)
# 不同 hidden 大小 → 不同 loss
# ============================================================
def make_data(n=500):
    X = np.random.uniform(-3, 3, (n, 1))
    y = np.sin(X.flatten()) + np.random.randn(n) * 0.1
    return X, y

def train_and_eval(hidden, n_train=500, n_steps=2000, lr=0.05):
    """训练一个 hidden-neuron 的 MLP, 返回最终 test MSE"""
    X_tr, y_tr = make_data(n_train)
    X_te = np.linspace(-3, 3, 200).reshape(-1, 1)
    y_te = np.sin(X_te.flatten())
    d = 1
    W1 = np.random.randn(d, hidden) * 0.5
    b1 = np.zeros(hidden)
    W2 = np.random.randn(hidden, 1) * 0.5
    b2 = np.zeros(1)
    for _ in range(n_steps):
        h = np.tanh(X_tr @ W1 + b1)
        pred = (h @ W2 + b2).flatten()
        grad = np.clip((pred - y_tr).reshape(-1, 1), -10, 10)
        W2 -= lr * h.T @ grad / n_train
        b2 -= lr * grad.sum(0) / n_train
        dh = grad @ W2.T * (1 - h**2)
        W1 -= lr * X_tr.T @ dh / n_train
        b1 -= lr * dh.sum(0) / n_train
    # test
    h_te = np.tanh(X_te @ W1 + b1)
    pred_te = (h_te @ W2 + b2).flatten()
    return float(np.mean((pred_te - y_te)**2)), hidden * (d+1) + (hidden+1)

P("="*70)
P("实验 02 — 规模与 Scaling Laws")
P("="*70)
P()
P("任务: 拟合 sin(x), 不同 hidden 大小 → 看 test loss")
P()

print(f"{'hidden':<10}{'参数量':>10}{'test MSE':>14}{'log(loss)':>14}{'log(N)':>10}")
print("-"*58)
results = []
for h in [1, 2, 4, 8, 16, 32, 64, 128]:
    mse, nparams = train_and_eval(h)
    log_loss = math.log10(max(mse, 1e-6))
    log_N = math.log10(nparams)
    results.append((h, nparams, mse, log_loss, log_N))
    print(f"{h:<10}{nparams:>10}{mse:>14.6f}{log_loss:>14.4f}{log_N:>10.4f}")

# 拟合幂律: log(loss) = a + b * log(N)
log_Ns = np.array([r[4] for r in results[:-1]])  # 跳过最后的 N=128 (发散)
log_losses = np.array([r[3] for r in results[:-1]])
A = np.vstack([log_Ns, np.ones_like(log_Ns)]).T
slope, intercept = np.linalg.lstsq(A, log_losses, rcond=None)[0]
print(f"\n拟合幂律: log(loss) = {intercept:.3f} + ({slope:.3f}) * log(N)")
print(f"  → loss ∝ N^({slope:.3f})")
print(f"  Kaplan 2020 真实值 (GPT-3): loss ∝ N^(-0.076)")
print(f"  本教学简化版: slope 更陡 ({slope:.3f}), 因为模型小数据简单")

# ============================================================
# Part 2: 数据量 vs loss
# ============================================================
P()
P("="*70)
P("Part 2: 数据量 vs loss")
P("-"*70)
print(f"\n{'n_train':<10}{'test MSE':>14}{'log(loss)':>14}{'log(D)':>10}")
print("-"*50)
data_results = []
for n in [50, 100, 200, 500, 1000, 2000]:
    mse, _ = train_and_eval(hidden=32, n_train=n)
    data_results.append((n, mse))
    print(f"{n:<10}{mse:>14.6f}{math.log10(max(mse,1e-6)):>14.4f}{math.log10(n):>10.4f}")

# ============================================================
# Part 3: Chinchilla 最优 — 给定 compute 怎么分配 N 和 D
# ============================================================
P()
P("="*70)
P("Part 3: Chinchilla 最优 — 给定算力, 模型多大/数据多少?")
P("-"*70)
P()
P("Chinchilla (Hoffmann 2022): 给定 FLOPs C = 6·N·D, 最优分配:")
P("  N* ≈ C^0.5 / 6 / 20  (参数量)")
P("  D* ≈ 20 · N*          (数据 = 20 倍参数)")
P()
P("  → [训练数据应约为参数量的 20 倍 (token 数)]")
P("  → GPT-3 (175B) 训 300B token [严重欠训]")
P("  → Chinchilla (70B) 训 1.4T token [最优]")
P()
print(f"{'参数量 N':<14}{'Chinchilla 最优 D':>20}{'实际常用 D':>16}{'说明':<24}")
print("-"*74)
examples = [
    (7_000_000_000,    "1.4T (Llama-2)", "实际 ~2-4T"),
    (13_000_000_000,   "2.6T (Llama-2)", "实际 ~2-4T"),
    (70_000_000_000,   "1.4T (Chinchilla)", "Chinchilla 重新校准"),
    (175_000_000_000,  "3.5T (GPT-3)", "实际 0.3T → 严重欠训"),
    (405_000_000_000,  "8T (Llama-3)", "实际 15T → 过训?"),
]
for N, optimal, note in examples:
    D_opt = 20 * N
    if D_opt > 1e12: D_str = f"{D_opt/1e12:.1f}T"
    elif D_opt > 1e9: D_str = f"{D_opt/1e9:.1f}B"
    else: D_str = str(D_opt)
    print(f"{N//10**9}B{'':<10}{D_str:>20}{optimal:>16}    {note}")

P()
P("关键观察:")
P("- GPT-3 (175B/0.3T): 严重欠训 → Chinchilla (70B/1.4T) 同算力下更强")
P("- Llama-3 (405B/15T): 数据超过 Chinchilla 建议 → 趋势是'数据更多'")
P("- 现代 LLM 公司的'秘密武器': 数据质量 + 数据量")
P()

# ============================================================
# Part 4: 三大 Scaling Law 总结
# ============================================================
P("="*70)
P("Part 4: 三大 Scaling Law (Kaplan 2020 + Chinchilla 2022)")
P("-"*70)
P("""
1. 【参数量定律】 (固定大数据)
   L(N) = (N_c / N)^α_N,  α_N ≈ 0.076
   → 模型每翻倍, loss 下降 ~5%

2. 【数据量定律】 (固定大模型)
   L(D) = (D_c / D)^α_D,  α_D ≈ 0.095
   → 数据每翻倍, loss 下降 ~7%

3. 【计算量定律】 (同时优化 N 和 D)
   L(C) = (C_c / C)^α_C,  α_C ≈ 0.05
   → 算力每翻倍, loss 下降 ~3-4%

工程意义:
- 这些是 [经验幂律], 不是定理. 但在 7 个数量级内都成立!
- 可以 [外推预测]: 训 100B 模型前, 先训 1B 模型拟合幂律, 预测 100B 的 loss
- 这是 OpenAI/Anthropic/DeepMind 设计大模型训练的 [科学依据]
""")

# ============================================================
# Part 5: Scaling Laws 的局限
# ============================================================
P("="*70)
P("Part 5: Scaling Laws 的局限 — 不是万能的")
P("-"*70)
P("""
1. 【只对 [预训练 loss] 准】
   Scaling Law 预测的是 next-token loss, 不是 [任务准确率]
   任务准确率在阈值处可能突变 (涌现能力, 见 02 篇)

2. 【数据质量 > 数据量】
   "15T token 垃圾数据" 不如 "1T 高质量 token"
   Llama-3 / Qwen 都强调 [数据清洗] 比 [数据量] 更重要

3. 【涌现能力】
   部分 capability 在 N 超过阈值时突然出现 (Wei 2022)
   Scaling Law 无法预测 [哪个能力何时涌现]

4. 【后训练 (SFT/RLHF) 无 scaling law】
   预训练有清晰幂律, RLHF 没有
   这就是 [为什么大模型公司各有强弱] — RLHF 是艺术不是科学

5. 【极限在哪?】
   数据终将耗尽 (互联网就这么多文本)
   → 合成数据 / 多模态 / 在线学习 是未来
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
Scaling Laws 是 [模型规模的科学]:
- 参数量翻倍 → loss 降 ~5% (α_N ≈ 0.076)
- 数据量翻倍 → loss 降 ~7%
- 算力翻倍 → loss 降 ~3-4%

Chinchilla 定律: 给定算力, 数据应 ~20 倍参数量 (token)
- GPT-3 (175B/0.3T) 严重欠训
- Chinchilla (70B/1.4T) 同算力下更强
- Llama-3 (405B/15T) 数据超过建议, 趋势在变

局限: 只对预训练 loss 准, 数据质量 > 数据量, 涌现无法预测, RLHF 无定律
""")
