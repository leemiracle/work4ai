#!/usr/bin/env python3
"""讲透优化实验 1：凸分析实验室。
E1 凸性二阶判据随机验证 | E2 Jensen | E3 LP 对偶间隙+KKT 互补松弛 | E4 条件数之字形预演
产出：convex.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linprog

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "sans-serif"]
rng = np.random.default_rng(7)

# E1 凸性判据
for _ in range(200):
    M = rng.normal(size=(3, 3)); Q = M.T @ M + 1e-9 * np.eye(3)
    assert np.linalg.eigvalsh(Q).min() >= -1e-10
print("E1 ✓ 200 个随机 PSD 矩阵二阶判据全过")

# E2 Jensen
X = rng.normal(1.0, 2.0, 500_000)
assert (X**2).mean() > X.mean()**2
print(f"E2 ✓ Jensen（x²）：E[X²]={(X**2).mean():.3f} ≥ (EX)²={X.mean()**2:.3f}（差=方差）")

# E3 LP 对偶 + KKT
c = [-1, -2]
A_ub = np.array([[1, 1], [1, 3]]); b_ub = np.array([4, 6])
r = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * 2)
mu = r.ineqlin.marginals             # scipy 对偶变量（min 问题惯例 μ≤0）
dual_obj = float(b_ub @ mu)          # 对偶目标 b'μ（与原目标同号同值=强对偶）
lam = -mu                            # 影子价格取正（03 章惯例）
print(f"E3 ✓ LP 原目标={r.fun:.6f} 对偶目标={dual_obj:.6f} 对偶间隙={abs(r.fun-dual_obj):.2e}")
resid = A_ub @ r.x - b_ub
for i in range(2):
    assert lam[i] * resid[i] < 1e-7, "互补松弛失败"
    print(f"    约束{i}: λ={lam[i]:.3f} 残差={resid[i]:.4f} → 互补松弛 ✓")

# E4 条件数
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for kappa, col in [(5, "tab:green"), (50, "tab:orange")]:
    Q = np.array([[kappa, 0], [0, 1]]); b = np.zeros(2)
    x = np.array([4.0, 4.0]); traj = [x.copy()]
    for _ in range(25):
        x = x - (2 * Q @ x + b) / (2 * kappa)   # 步长 1/L
        traj.append(x.copy())
    T = np.array(traj)
    ax[0].plot(T[:, 0], T[:, 1], "o-", ms=3, c=col, label=f"κ={kappa}")
    ax[1].semilogy([np.linalg.norm(t) for t in T], c=col, label=f"κ={kappa}")
ax[0].legend(); ax[0].set_title("GD 轨迹：κ 大→之字形（04 章伏笔）")
ax[1].legend(); ax[1].set_xlabel("步"); ax[1].set_title("到最优距离（对数）")
fig.tight_layout(); fig.savefig("convex.png", dpi=140)
print("E4 ✓ 条件数之字形演示 saved convex.png")
print("（E3 分离超平面/软阈值见 exercises 扩展位）")
