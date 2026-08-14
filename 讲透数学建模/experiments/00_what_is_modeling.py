"""
实验 00 — 什么是数学建模: 三大流派对比 (机理/统计/AI)
对应文档: 讲透数学建模/00-什么是数学建模.md

核心结论: 同一个传染病问题, 三种建模方法表现差异巨大
  1. 机理 (SIR 微分方程): 完美预测 (因参数可恢复)
  2. 统计 (多项式): 训练好但外推灾难
  3. AI (MLP): 拟合好但外推差

跑法: python3 -u 00_what_is_modeling.py
"""
import math
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 真实数据生成 (SIR 模型)
# ============================================================
def simulate_sir(N=10000, I0=10, beta=0.35, gamma=0.10, days=120):
    S, I, R = N - I0, I0, 0
    out = [I]
    for _ in range(days):
        new_inf = beta * S * I / N
        new_rec = gamma * I
        S -= new_inf; I += new_inf - new_rec; R += new_rec
        out.append(I)
    return np.array(out[:days])  # 严格 days 个点

I_true = simulate_sir(beta=0.35, gamma=0.10, days=120)
peak_true = int(np.argmax(I_true))
peak_val_true = float(I_true[peak_true])

# 训练数据: 前 60 天
TRAIN_END = 60
train_days = np.arange(TRAIN_END, dtype=float)
train_I = I_true[:TRAIN_END]

P("="*70)
P("实验 00 — 什么是数学建模: 三大流派对比")
P("="*70)
P()
P(f"问题: 预测传染病 120 天传播曲线")
P(f"真实数据 (SIR β=0.35, γ=0.10, R0=3.5): 峰值第 {peak_true} 天, {peak_val_true:.0f} 人")
P(f"训练: 只给前 {TRAIN_END} 天, 预测后 {120-TRAIN_END} 天")
P()

# ============================================================
# 流派 1: 机理建模 (SIR)
# ============================================================
P("="*70)
P("流派 1: 机理建模 (SIR 微分方程)")
P("-"*70)

def fit_sir(train_I, N=10000, I0=10):
    best = (float('inf'), None)
    for beta in np.arange(0.20, 0.50, 0.01):
        for gamma in np.arange(0.05, 0.20, 0.005):
            pred = simulate_sir(N=N, I0=I0, beta=beta, gamma=gamma, days=len(train_I))
            loss = float(np.mean((pred - train_I)**2))
            if loss < best[0]: best = (loss, (beta, gamma))
    return best[1], best[0]

(beta_h, gamma_h), train_loss_mech = fit_sir(train_I)
I_pred_mech = simulate_sir(beta=beta_h, gamma=gamma_h, days=120)
peak_mech = int(np.argmax(I_pred_mech))
pred_loss_mech = float(np.mean((I_pred_mech[TRAIN_END:] - I_true[TRAIN_END:])**2))

print(f"拟合: β={beta_h:.3f} (真 0.350), γ={gamma_h:.3f} (真 0.100), R0={beta_h/gamma_h:.2f}")
print(f"训练 MSE: {train_loss_mech:.2f}")
print(f"预测 MSE: {pred_loss_mech:.2f}")
print(f"预测峰值: 第 {peak_mech} 天 (真 {peak_true}), {I_pred_mech[peak_mech]:.0f} (真 {peak_val_true:.0f})")
print(f"性质: ✅ 白箱可解释 / ✅ 外推强 / ❌ 需机理知识")

# ============================================================
# 流派 2: 统计建模 (多项式)
# ============================================================
P()
P("="*70)
P("流派 2: 统计建模 (6 次多项式拟合)")
P("-"*70)

coeffs = np.polyfit(train_days, train_I, deg=6)
all_days = np.arange(120, dtype=float)
I_pred_poly = np.polyval(coeffs, all_days)
train_loss_poly = float(np.mean((np.polyval(coeffs, train_days) - train_I)**2))
pred_loss_poly = float(np.mean((np.clip(I_pred_poly[TRAIN_END:], 0, None) - I_true[TRAIN_END:])**2))
final_poly = float(I_pred_poly[-1])

print(f"训练 MSE: {train_loss_poly:.2f}")
print(f"预测 MSE: {pred_loss_poly:.2f}")
if final_poly < 0:
    print(f"⚠ 第 120 天预测: {final_poly:.0f} (负数, 物理不可能!)")
elif final_poly > 50000:
    print(f"⚠ 第 120 天预测: {final_poly:.0f} (远超总人口, 完全失控!)")
print(f"性质: △ 简单 / ❌ 外推灾难")

# ============================================================
# 流派 3: AI 建模 (MLP)
# ============================================================
P()
P("="*70)
P("流派 3: AI 建模 (2 层 MLP)")
P("-"*70)

class TinyMLP:
    def __init__(self, h=16):
        self.W1 = np.random.randn(1, h)*0.5; self.b1 = np.zeros(h)
        self.W2 = np.random.randn(h, h)*0.5; self.b2 = np.zeros(h)
        self.W3 = np.random.randn(h, 1)*0.5; self.b3 = np.zeros(1)
    def forward(self, X):
        self.X = (X.reshape(-1, 1)/60.0)
        self.h1 = np.maximum(0, self.X @ self.W1 + self.b1)
        self.h2 = np.maximum(0, self.h1 @ self.W2 + self.b2)
        self.out = (self.h2 @ self.W3 + self.b3).flatten()
        return self.out
    def backward(self, X, y, lr=0.005):
        self.forward(X); n = len(y)
        d = (self.out - y).reshape(-1, 1)/n
        dW3 = self.h2.T @ d; db3 = d.sum(0)
        dh2 = d @ self.W3.T; dh2[self.h2<=0] = 0
        dW2 = self.h1.T @ dh2; db2 = dh2.sum(0)
        dh1 = dh2 @ self.W2.T; dh1[self.h1<=0] = 0
        dW1 = self.X.T @ dh1; db1 = dh1.sum(0)
        self.W3-=lr*dW3; self.b3-=lr*db3; self.W2-=lr*dW2; self.b2-=lr*db2
        self.W1-=lr*dW1; self.b1-=lr*db1

mlp = TinyMLP()
for _ in range(3000): mlp.backward(train_days, train_I)
I_pred_nn = mlp.forward(all_days)
I_pred_nn_clipped = np.maximum(I_pred_nn, 0)
train_loss_nn = float(np.mean((mlp.forward(train_days) - train_I)**2))
pred_loss_nn = float(np.mean((I_pred_nn_clipped[TRAIN_END:] - I_true[TRAIN_END:])**2))

print(f"训练 MSE: {train_loss_nn:.2f}")
print(f"预测 MSE: {pred_loss_nn:.2f}")
print(f"性质: ✅ 强大 / ❌ 黑箱 / ❌ 外推差 / ❌ 数据饥渴")

# ============================================================
# 横评
# ============================================================
P()
P("="*70)
P("横评: 三大流派对比")
P("-"*70)
print(f"\n{'流派':<24}{'训练 MSE':>12}{'预测 MSE':>12}{'性质'}")
print("-"*70)
print(f"{'机理 (SIR 微分方程)':<24}{train_loss_mech:>12.2f}{pred_loss_mech:>12.2f}    ✅ 白箱/外推强")
print(f"{'统计 (6 次多项式)':<24}{train_loss_poly:>12.2f}{pred_loss_poly:>12.2f}    ❌ 外推灾难")
print(f"{'AI (2 层 MLP)':<24}{train_loss_nn:>12.2f}{pred_loss_nn:>12.2f}    ❌ 黑箱")

P("""
关键观察:
- 机理 (SIR): 预测 MSE 最低, 峰值预测准, β/γ 有物理意义 (传染率/康复率)
- 统计 (多项式): 训练拟合好, 但外推灾难 (可能预测负数或远超物理上限)
- AI (MLP): 拟合好, 但外推差 (神经网络在训练域外基本是噪声)

→ AI 不是万能的!
  - 机理已知 → 用机理建模 (SIR/弹簧/电路/Navier-Stokes)
  - 机理未知 → 用 AI (图像/NLP/复杂模式)
  - 部分已知 → 用混合 (PINN, 见 06 篇)
""")

# ============================================================
# Part 2: 三大流派的本质差异
# ============================================================
P("="*70)
P("Part 2: 三大流派的本质差异")
P("-"*70)
P("""
            ┌──────────────────────────────────┐
            │           现实问题                │
            └──────────────┬───────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ 机理建模 │        │ 统计建模 │        │ AI 建模  │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
   用物理定律列方程     从数据拟合关系       神经网络通用逼近
   (SIR/NS)            (回归/ARIMA)        (MLP/Transformer)
        │                  │                  │
   ✅ 白箱可解释        △ 灰箱              ❌ 黑箱
   ✅ 外推强            ❌ 外推差            ❌ 外推差
   ❌ 需要机理知识      ✅ 简单              ✅ 强大
   ❌ 复杂系统难列方程  ❌ 模型形式受限      ❌ 数据饥渴
""")

# ============================================================
# Part 3: 混合建模 (PINN/AI4Science)
# ============================================================
P("="*70)
P("Part 3: 现代趋势 — 混合建模")
P("-"*70)
P("""
2020+ 范式: [机理 + AI] 鱼与熊掌兼得

1. 【PINN (Physics-Informed NN)】
   Loss = 数据拟合 + λ · |物理方程残差|
   例: 流体力学有 Navier-Stokes 方程, NN 拟合速度场,
       loss 加上 NS 残差 → NN 既符合数据又符合物理

2. 【Neural ODE】
   把 [微分方程求解] 变成 [神经网络层]
   dz/dt = f_θ(z, t), 用 NN 参数化 f

3. 【AI4Science】
   AlphaFold (蛋白质): AI 学氨基酸→3D 结构
   DeepMind 聚变: AI 学等离子动力学
   材料/药物: AI 学结构-性质关系

→ 数学建模的 [文艺复兴]: AI 不替代机理, 而是与之融合.
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
数学建模三大流派 (传染病问题实测):
1. 机理 (SIR 微分方程): 白箱, 可解释, 外推强 — 但需要机理知识
2. 统计 (多项式): 简单 — 但外推灾难 (预测负数/超物理上限)
3. AI (MLP): 强大 — 但黑箱, 外推差, 数据饥渴

→ AI 是数学建模的 [一个流派], 不是全部.
   机理已知 → 用机理; 机理未知 → 用 AI; 部分已知 → 用 PINN 混合.
   这就是 AlphaFold/PINN/AI4Science 是 [数学建模的文艺复兴] 的原因.
""")
