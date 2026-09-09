"""
SVD 与协同过滤推荐系统
=====================
数学概念：奇异值分解 (SVD) / 低秩近似 / 矩阵补全
应用领域：推荐系统、协同过滤、Netflix Prize 类问题
核心思想：用户-物品评分矩阵 R 是低秩的(用户偏好可由少数隐因子解释)。
         对 R 做 SVD: R = U Σ V^T, 截断到前 k 个奇异值得低秩近似 R_k,
         即可预测缺失评分。Eckart-Young 定理保证截断 SVD 是最优低秩近似(Frobenius 范数下)。
运行方式：python "03-SVD_推荐系统.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 1. 数据生成：构造低秩评分矩阵并人为制造缺失 ============
np.random.seed(42)
N_USERS, N_ITEMS, K_TRUE = 50, 40, 3     # 50 用户, 40 物品, 真实隐因子数=3

# 生成真实低秩矩阵: R = U @ V (隐因子模型)
U_true = np.random.randn(N_USERS, K_TRUE) * 2
V_true = np.random.randn(K_TRUE, N_ITEMS) * 2
R_true = U_true @ V_true                 # 真实完整评分矩阵 (低秩=3)

# 映射到 1-5 分并加少量噪声
R_obs = np.clip(np.round(R_true + np.random.randn(*R_true.shape) * 0.5), 1, 5).astype(float)

# 随机掩盖 30% 作为测试集 (模拟用户未评分的物品)
MASK = np.random.rand(N_USERS, N_ITEMS) > 0.30   # True=观测, False=缺失
R_masked = R_obs.copy()
R_masked[~MASK] = 0                          # 缺失处置 0
print(f"[数据] {N_USERS} 用户 x {N_ITEMS} 物品, 观测率 {MASK.mean()*100:.1f}%")

# ============ 2. 数学建模：截断 SVD 低秩近似 ============
def svd_predict(R, k, n_iter=20):
    """
    对含缺失的评分矩阵做 SVD 补全 (交替最小二乘的简化版 + 截断 SVD):
    1. 缺失值先用均值填充
    2. 做截断 SVD 得低秩近似
    3. 保留观测值, 用近似值更新缺失值, 迭代收敛
    """
    Rf = R.copy().astype(float)
    # 初始填充: 列均值(每个物品的平均分)
    col_mean = np.array([Rf[Rf[:, j] > 0, j].mean() if (Rf[:, j] > 0).any() else 3.0
                         for j in range(Rf.shape[1])])
    for j in range(Rf.shape[1]):
        Rf[Rf[:, j] == 0, j] = col_mean[j]

    observed = R > 0
    for _ in range(n_iter):
        # 截断 SVD: 只保留前 k 个奇异值
        U, s, Vt = np.linalg.svd(Rf, full_matrices=False)
        Sk = np.diag(s[:k])
        Rk = U[:, :k] @ Sk @ Vt[:k, :]
        # 用低秩近似值更新缺失位置, 观测值保持不变
        Rf = np.where(observed, R, Rk)
    return Rk

# ============ 3. 评估与可视化 ============
# 不同 k 值的测试集 RMSE
Ks = [1, 2, 3, 5, 8, 12, 20]
rmses = []
for k in Ks:
    R_pred = svd_predict(R_masked, k)
    # 只计算测试集(缺失位置)的 RMSE
    test_mask = ~MASK
    rmse = np.sqrt(((R_pred[test_mask] - R_obs[test_mask]) ** 2).mean())
    rmses.append(rmse)
    print(f"k={k:2d} | 测试集 RMSE = {rmse:.4f}")

# 最优 k
best_k = Ks[np.argmin(rmses)]
print(f"\n[最优] k={best_k}, RMSE={min(rmses):.4f} (真实秩={K_TRUE})")

# 用最优 k 做最终预测
R_final = svd_predict(R_masked, best_k)

# 为每个用户推荐 Top-3 未观测物品
print("\n[推荐示例] 前 5 位用户的 Top-3 推荐物品:")
for u in range(5):
    scores = R_final[u].copy()
    scores[MASK[u]] = -1            # 排除已评分物品
    top3 = np.argsort(-scores)[:3]
    items = ", ".join(f"物品{i}(预测{R_final[u, i]:.1f}分)" for i in top3)
    print(f"  用户{u:2d}: {items}")

# ---- 绘图 ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
ax.plot(Ks, rmses, "rs-", lw=1.5)
ax.axvline(best_k, color="g", ls="--", label=f"最优 k={best_k}")
ax.set_xlabel("隐因子数 k (截断秩)")
ax.set_ylabel("测试集 RMSE")
ax.set_title("SVD 推荐系统: k 值选择")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
im = ax.imshow(R_masked, aspect="auto", cmap="YlOrRd")
ax.set_xlabel("物品")
ax.set_ylabel("用户")
ax.set_title("观测评分矩阵 (含缺失=深色底)")
plt.colorbar(im, ax=ax, fraction=0.046)

ax = axes[2]
im = ax.imshow(R_final, aspect="auto", cmap="YlOrRd")
ax.set_xlabel("物品")
ax.set_ylabel("用户")
ax.set_title(f"SVD 补全后完整矩阵 (k={best_k})")
plt.colorbar(im, ax=ax, fraction=0.046)

plt.tight_layout()
plt.savefig("03-SVD推荐_结果.png", dpi=120)
print("\n[结果] 图像已保存: 03-SVD推荐_结果.png")
print("[解读] k=真实秩(3)附近 RMSE 最低, k 过大时引入噪声导致过拟合。"
          "SVD 揭示了'用户偏好好可由少数隐因子解释'这一核心洞察, 是现代推荐系统的基础。")

if __name__ == "__main__":
    pass
