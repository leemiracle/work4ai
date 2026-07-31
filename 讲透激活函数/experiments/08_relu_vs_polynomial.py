"""
实验 08 —— ReLU 两层网络能拟合 sin,理论支持是什么? 等价于几次多项式?

核心问题(用户提问):
  Q1: 带 ReLU 的两层 MLP 能拟合 sin(x),数学理论支持是什么?
  Q2: 它相当于多少次的多项式?

核心发现(剧透):
  - 理论支持 = 万能逼近定理 (Universal Approximation Theorem, Cybenko 1989 / Leshno 1993)
  - 但 ReLU 网络的输出是【分段线性函数】(piecewise-linear),不是多项式!
    两者是【完全不同的函数空间】,不存在"等价于 n 次多项式"的简单换算。
  - 公平对比维度是【参数数量】或【逼近误差】,本实验给出数值对照表。

跑法: python3 08_relu_vs_polynomial.py
"""
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(0)
np.random.seed(0)

# ============================================================
# 目标函数: y = sin(x), x in [-pi, pi]
# ============================================================
N_PTS = 400
x_np = np.linspace(-np.pi, np.pi, N_PTS)
y_np = np.sin(x_np)
x_t = torch.tensor(x_np, dtype=torch.float32).unsqueeze(1)
y_t = torch.tensor(y_np, dtype=torch.float32).unsqueeze(1)


def count_params(width):
    """两层 MLP: Linear(1,w) + ReLU + Linear(w,1) 的参数数"""
    return (1 * width + width) + (width * 1 + 1)  # = 3w + 1


def train_relu(width, steps=4000, lr=0.01):
    model = nn.Sequential(nn.Linear(1, width), nn.ReLU(), nn.Linear(width, 1))
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    for _ in range(steps):
        opt.zero_grad()
        loss = loss_fn(model(x_t), y_t)
        loss.backward()
        opt.step()
    with torch.no_grad():
        pred = model(x_t).numpy().flatten()
    mse = float(np.mean((pred - y_np) ** 2))
    return model, pred, mse


def count_relu_knots(model, x_grid):
    """数 ReLU 网络在 x_grid 上的【折点】数量(一阶导变号的点)"""
    with torch.no_grad():
        y = model(x_grid).numpy().flatten()
    dy = np.diff(y)
    # 一阶导符号变化的位置 ≈ 折点(ReLU 的拐弯处)
    sign_changes = np.where(np.diff(np.sign(dy)) != 0)[0]
    return len(sign_changes)


# ============================================================
# A. 多项式拟合: degree = 1..15
# ============================================================
print("=" * 72)
print("A. 多项式拟合 sin(x)  (numpy.polyfit, 最小二乘)")
print("=" * 72)
print(f"{'次数n':>6} | {'参数数':>6} | {'MSE':>14} | {'最大误差':>12}")
print("-" * 50)
poly_results = {}
for deg in range(1, 16):
    coeffs = np.polyfit(x_np, y_np, deg)
    pred = np.polyval(coeffs, x_np)
    mse = float(np.mean((pred - y_np) ** 2))
    maxerr = float(np.max(np.abs(pred - y_np)))
    poly_results[deg] = (mse, pred)
    print(f"{deg:>6} | {deg+1:>6} | {mse:>14.3e} | {maxerr:>12.3e}")

# ============================================================
# B. ReLU 两层网络: width = 2,4,8,16,32,64,128
# ============================================================
print("\n" + "=" * 72)
print("B. ReLU 两层 MLP 拟合 sin(x)")
print("=" * 72)
print(f"{'宽度N':>6} | {'参数数':>6} | {'折点数':>6} | {'MSE':>14} | {'最大误差':>12}")
print("-" * 60)
relu_results = {}
widths = [2, 4, 8, 16, 32, 64, 128]
x_fine = torch.linspace(-np.pi, np.pi, 2000).unsqueeze(1)
for w in widths:
    model, pred, mse = train_relu(w)
    knots = count_relu_knots(model, x_fine)
    maxerr = float(np.max(np.abs(pred - y_np)))
    relu_results[w] = (mse, pred, knots, model)
    print(f"{w:>6} | {count_params(w):>6} | {knots:>6} | {mse:>14.3e} | {maxerr:>12.3e}")

# ============================================================
# C. 关键对照: 同样参数量下,谁更强?
# ============================================================
print("\n" + "=" * 72)
print("C. 公平对照:【参数数量】相近时,多项式 vs ReLU 网络")
print("=" * 72)
print("ReLU 两层网络参数数 = 3N+1 (Linear(1,N):2N 个 + Linear(N,1):N+1 个)")
print()
print(f"{'ReLU宽N':>8} | {'ReLU参数':>8} | {'对应多项式n':>12} | {'ReLU_MSE':>12} | {'Poly_MSE':>12} | {'胜者':>6}")
print("-" * 70)
for w in widths:
    relu_mse = relu_results[w][0]
    target_params = count_params(w)
    # 找参数数最接近的多项式次数(多项式 n 次有 n+1 个参数)
    best_deg = max(1, target_params - 1)
    best_deg = min(best_deg, 15)
    poly_mse = poly_results[best_deg][0]
    winner = "ReLU" if relu_mse < poly_mse else "多项式"
    print(f"{w:>8} | {target_params:>8} | {best_deg:>12} | {relu_mse:>12.3e} | {poly_mse:>12.3e} | {winner:>6}")

# ============================================================
# D. 可视化: ReLU 输出是【折线】,多项式是【光滑曲线】
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 图1: ReLU 宽度递增的拟合曲线(看出"折线"本质)
ax = axes[0]
ax.plot(x_np, y_np, "k-", linewidth=2, label="sin(x) target", alpha=0.5)
for w in [4, 8, 16, 64]:
    pred = relu_results[w][1]
    ax.plot(x_np, pred, linewidth=1.2, label=f"ReLU N={w} ({relu_results[w][2]} knots)")
ax.set_title("ReLU net = Piecewise-Linear (knots)\nmore knots -> better fit to sin")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_xlim(-np.pi, np.pi)

# 图2: 多项式次数递增的拟合曲线(光滑但端点振荡,即 Runge 现象)
ax = axes[1]
ax.plot(x_np, y_np, "k-", linewidth=2, label="sin(x) target", alpha=0.5)
for deg in [3, 5, 9, 15]:
    pred = poly_results[deg][1]
    ax.plot(x_np, pred, linewidth=1.2, label=f"poly n={deg}")
ax.set_title("Polynomial = smooth curve\nhigh degree oscillates at ends (Runge)")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_xlim(-np.pi, np.pi)

# 图3: 参数量 vs MSE 的"学习曲线"对比
ax = axes[2]
# 多项式: 参数 = deg+1
poly_params = [d + 1 for d in poly_results]
poly_mses = [poly_results[d][0] for d in poly_results]
ax.semilogy(poly_params, poly_mses, "ro-", label="poly (params=n+1)", linewidth=2)
# ReLU: 参数 = 3w+1
relu_params = [count_params(w) for w in widths]
relu_mses = [relu_results[w][0] for w in widths]
ax.semilogy(relu_params, relu_mses, "bs-", label="ReLU net (params=3N+1)", linewidth=2)
ax.set_xlabel("#parameters"); ax.set_ylabel("MSE (log)")
ax.set_title("params vs accuracy\npoly beats ReLU on SMOOTH 1D functions")
ax.legend(fontsize=9); ax.grid(alpha=0.3, which="both")

plt.tight_layout()
out = "relu_vs_polynomial.png"
plt.savefig(out, dpi=110)
print(f"\n==> 图已保存: experiments/{out}")

# ============================================================
# E. 理论误差阶对比 (解析公式, 不依赖训练)
# ============================================================
print("\n" + "=" * 72)
print("D. 理论误差阶: 用 N 段折线 / n 次多项式 逼近 sin(x) on [-pi,pi]")
print("=" * 72)
print("""
【ReLU 网络 = N 段折线】(单输入, 宽度 N → 最多 N+1 段)
  线性插值误差理论界:  max|sin - 折线| ≤ (h²/8) · max|sin''|
                       其中 h = 区间长度/(段数) = 2π/(N+1)
  → 误差 = O(1/N²)  (二阶收敛, 因为折线只用到一阶信息)

【多项式 n 次】(切比雪夫最佳逼近, 比 Taylor 强很多)
  最佳 n 次多项式逼近 sin on [-π,π] 的误差 ≈ (π/4)^(n+1)/(2n+1)!!
  → 误差 = O((1/π)^n)  (指数收敛 / 谱精度, 远快于任何多项式阶)

【关键洞察】
  - 多项式对【光滑函数】收敛速度远快于 ReLU 折线 (谱精度 vs 2 阶)
  - 但多项式在【非光滑/高维】函数上会崩 (Runge 振荡 / 维数灾难)
  - ReLU 网络的优势在【高维】【局部特征】(图像/语音), 不在【1D光滑】
""")

# 数值验证理论阶
print("数值验证 (ReLU 折线误差随 N 的衰减率, 应接近 -2.0):")
prev = None
for w in widths:
    mse = relu_results[w][0]
    if prev is not None and mse > 0 and prev > 0:
        rate = -np.log(mse / prev) / np.log(2)  # 宽度翻倍的收敛率
        print(f"  N={w:>3}: MSE={mse:.2e}  (翻倍收敛率 ≈ {rate:.2f})")
    else:
        print(f"  N={w:>3}: MSE={mse:.2e}")
    prev = mse
print("(理论预测: 宽度翻倍 → 误差降为 1/4, 即收敛率 ≈ 2.0)")
