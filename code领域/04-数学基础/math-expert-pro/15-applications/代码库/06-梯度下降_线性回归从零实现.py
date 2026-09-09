"""
梯度下降与线性回归从零实现
=========================
数学概念：梯度下降 / 最优化 / 学习率调度 / 凸优化
应用领域：机器学习、参数估计、最优化
核心思想：线性回归的损失函数 J(w) = (1/2n)||Xw - y||² 是凸函数,
         其梯度 ∇J = X^T(Xw - y)/n。沿负梯度方向迭代更新 w 即可收敛到全局最优(正规方程解)。
         本例对比批量(BGD)、随机(SGD)、小批量(MBGD)三种变体, 并分析学习率影响。
运行方式：python "06-梯度下降_线性回归从零实现.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 1. 数据生成 ============
np.random.seed(42)
n, d = 200, 2                                # 200 样本, 2 特征
X_true = np.random.uniform(-3, 3, (n, d))
W_true = np.array([3.0, -1.5])               # 真实权重
b_true = 2.0                                 # 真实偏置
y = X_true @ W_true + b_true + 0.8 * np.random.randn(n)  # 加高斯噪声

# 标准化特征 (加速收敛) + 加偏置列
X_mean, X_std = X_true.mean(0), X_true.std(0)
X = (X_true - X_mean) / X_std
X_b = np.c_[np.ones(n), X]                   # (n, 3), 第一列是偏置项
print(f"[数据] {n} 样本, {d} 特征, 真实参数 w={W_true}, b={b_true}")

# 解析解 (正规方程): w* = (X^T X)^{-1} X^T y, 作为对比基准
w_opt = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
loss_opt = 0.5 * np.mean((X_b @ w_opt - y) ** 2)
print(f"[基准] 正规方程解 w*={w_opt.round(3)}, 最优损失={loss_opt:.4f}")

# ============ 2. 数学建模：三种梯度下降变体 ============
def loss_fn(w):
    """均方误差损失 J(w) = (1/2n)||Xw - y||²"""
    return 0.5 * np.mean((X_b @ w - y) ** 2)

def gradient(w, idx=None):
    """计算梯度 ∇J = X^T(Xw - y)/n。idx 指定时只在该子集上计算(用于 SGD/MBGD)。"""
    if idx is None:
        idx = np.arange(n)
    Xi, yi = X_b[idx], y[idx]
    m = len(idx)
    return Xi.T @ (Xi @ w - yi) / m

def batch_gd(lr=0.1, epochs=200):
    """批量梯度下降: 每步用全部数据计算梯度。"""
    w = np.zeros(3)
    hist = [loss_fn(w)]
    for _ in range(epochs):
        w -= lr * gradient(w)
        hist.append(loss_fn(w))
    return w, hist

def stochastic_gd(lr=0.05, epochs=50):
    """随机梯度下降: 每步随机取一个样本计算梯度。"""
    w = np.zeros(3)
    hist = [loss_fn(w)]
    rng = np.random.RandomState(0)
    for _ in range(epochs):
        for _ in range(n):
            i = rng.randint(n)
            w -= lr * gradient(w, idx=[i])
        hist.append(loss_fn(w))
    return w, hist

def minibatch_gd(lr=0.08, epochs=100, bs=32):
    """小批量梯度下降: 每步用一个小批量。"""
    w = np.zeros(3)
    hist = [loss_fn(w)]
    rng = np.random.RandomState(0)
    for _ in range(epochs):
        perm = rng.permutation(n)
        for start in range(0, n, bs):
            idx = perm[start:start + bs]
            w -= lr * gradient(w, idx=idx)
        hist.append(loss_fn(w))
    return w, hist

# ============ 3. 运行与对比 ============
w_bgd, h_bgd = batch_gd()
w_sgd, h_sgd = stochastic_gd()
w_mbgd, h_mbgd = minibatch_gd()

print(f"\n[BGD ] w={w_bgd.round(3)}, 最终损失={h_bgd[-1]:.4f}")
print(f"[SGD ] w={w_sgd.round(3)}, 最终损失={h_sgd[-1]:.4f}")
print(f"[MBGD] w={w_mbgd.round(3)}, 最终损失={h_mbgd[-1]:.4f}")

# 学习率影响分析
print("\n[学习率影响] BGD 在不同学习率下的最终损失:")
for lr in [0.001, 0.01, 0.05, 0.1, 0.3, 0.5]:
    _, h = batch_gd(lr=lr, epochs=100)
    status = "收敛" if h[-1] < 5 else ("发散" if h[-1] > 1e6 else "缓慢")
    print(f"  lr={lr:<6} → 损失={h[-1]:12.4f}  [{status}]")

# ============ 4. 可视化 ============
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
ax.plot(h_bgd, "b-", lw=1.5, label=f"BGD 批量")
ax.plot(range(0, len(h_sgd)), h_sgd, "r-", lw=1, alpha=0.8, label=f"SGD 随机")
ax.plot(range(0, len(h_mbgd)), h_mbgd, "g-", lw=1.2, label=f"MBGD 小批量(bs=32)")
ax.axhline(loss_opt, color="k", ls="--", lw=1, label=f"最优损失={loss_opt:.3f}")
ax.set_xlabel("迭代轮次 (epoch)")
ax.set_ylabel("损失 J(w)")
ax.set_title("三种梯度下降收敛对比")
ax.set_ylim(0, max(20, loss_opt * 4))
ax.legend()
ax.grid(alpha=0.3)

# 学习率影响
ax = axes[1]
for lr in [0.001, 0.01, 0.1, 0.3, 0.5]:
    _, h = batch_gd(lr=lr, epochs=100)
    ax.plot(h, lw=1.3, label=f"lr={lr}")
ax.axhline(loss_opt, color="k", ls="--", lw=1, alpha=0.5)
ax.set_xlabel("迭代轮次")
ax.set_ylabel("损失")
ax.set_title("学习率对收敛的影响")
ax.set_ylim(-0.1, 15)
ax.legend()
ax.grid(alpha=0.3)

# 拟合结果
ax = axes[2]
# 用第一维特征画图 (固定第二维为均值)
mask_x1 = np.abs(X_true[:, 1]) < 0.5
ax.scatter(X_true[mask_x1, 0], y[mask_x1], s=15, alpha=0.5, label="数据点")
xx = np.linspace(-3, 3, 100)
xx_std = (xx - X_mean[0]) / X_std[0]
# 用 BGD 参数 (标准化空间) 还原到原始空间
yy = w_bgd[0] + w_bgd[1] * xx_std + w_bgd[2] * 0   # 第二特征标准化后为 0
ax.plot(xx, yy, "r-", lw=2, label=f"BGD 拟合")
yy_opt = w_opt[0] + w_opt[1] * xx_std
ax.plot(xx, yy_opt, "k--", lw=1.5, alpha=0.7, label="正规方程解")
ax.set_xlabel("特征 x1")
ax.set_ylabel("y")
ax.set_title("线性回归拟合结果")
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("06-梯度下降_结果.png", dpi=120)
print(f"\n[结果] 图像已保存: 06-梯度下降_结果.png")
print("[解读] BGD 平滑收敛但计算量大; SGD 波动大但每步快; MBGD 兼顾两者, 实际最常用。"
          "学习率过小收敛慢, 过大发散, 最佳值需调试。这是理解深度学习优化的基础。")

if __name__ == "__main__":
    pass
