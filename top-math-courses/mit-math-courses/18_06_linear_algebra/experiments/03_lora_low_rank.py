"""
MIT 18.06 · 实验03: LoRA 低秩更新的线性代数
依赖: numpy, matplotlib
运行: python3 03_lora_low_rank.py

验证 LoRA 的核心数学:
  1. 低秩参数化 W₀ + BA 能逼近任意秩-r 增量 (Eckart-Young)
  2. 参数压缩比 vs 近似误差的权衡 (秩-误差曲线)
  3. 奇异值谱"骤降"解释了为何小秩 r 就够用
  4. B=0 初始化保证训练起点 ΔW=0
  5. 随机矩阵的 Marchenko-Pastur 边界: 区分信号 vs 噪声奇异值
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(2024)

# ============================================================
# 实验 1: LoRA 低秩参数化 vs 全量参数
# ============================================================
print("=" * 60)
print("实验 1: LoRA 参数压缩比")
print("=" * 60)

d, k = 4096, 4096  # 模拟一个 Transformer 权重层
for r in [4, 8, 16, 64]:
    full = d * k
    lora = r * (d + k)
    ratio = full / lora
    print(f"  rank r={r:3d}: 全量={full:,}  LoRA={lora:,}  压缩={ratio:.0f}x  "
          f"(LoRA 参数占比={lora/full:.2%})")

# ============================================================
# 实验 2: 低秩近似精度 —— Eckart-Young 定理验证
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 低秩近似误差 = Eckart-Young 下界 (σ_{k+1})")
print("=" * 60)

# 构造一个"真增量" ΔW: 低秩信号 + 噪声
m, n_dim = 100, 80
true_rank = 5
B_true = np.random.randn(m, true_rank)
A_true = np.random.randn(true_rank, n_dim)
signal = B_true @ A_true           # 秩-5 信号 (模拟真实的任务适配增量)
noise = 0.05 * np.random.randn(m, n_dim)
delta_W = signal + noise           # 观测到的增量

U, S, Vt = np.linalg.svd(delta_W, full_matrices=False)

print(f"ΔW 的奇异值 (前 10): {np.round(S[:10], 2)}")
print(f"注意前 {true_rank} 个奇异值远大于后续 (噪声)")
print("\nEckart-Young 验证: 对每个秩 k, 误差 ‖ΔW - ΔW_k‖_F 应 = √(Σ σ²_{i>k})")
for r in [1, 2, 3, 5, 8, 10, 20]:
    approx = U[:, :r] @ np.diag(S[:r]) @ Vt[:r, :]
    err = np.linalg.norm(delta_W - approx, "fro")
    ey_bound = np.sqrt(np.sum(S[r:] ** 2))
    print(f"  rank k={r:2d}: 实际误差={err:.4f}  Eckart-Young 下界={ey_bound:.4f}  "
          f"匹配={np.isclose(err, ey_bound)}")

# ============================================================
# 实验 3: 秩 vs 近似质量曲线 (LoRA 选秩的依据)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 秩-误差曲线 —— LoRA 该选多大的 r?")
print("=" * 60)

ranks = np.arange(0, 30)
relative_err = []
for r in ranks:
    if r == 0:
        err = np.linalg.norm(delta_W, "fro") / np.linalg.norm(delta_W, "fro")
    else:
        approx = U[:, :r] @ np.diag(S[:r]) @ Vt[:r, :]
        err = np.linalg.norm(delta_W - approx, "fro") / np.linalg.norm(delta_W, "fro")
    relative_err.append(err)

# 找"拐点"(elbow): 误差下降明显变缓的秩
relative_err = np.array(relative_err)
print(f"  真实信号秩 = {true_rank}")
print(f"  r=5 时相对误差 = {relative_err[5]:.2%}  (已捕获大部分信号)")
print(f"  r=10 时相对误差 = {relative_err[10]:.2%}")

# ============================================================
# 实验 4: Marchenko-Pastur 边界 —— 区分信号 vs 噪声奇异值
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 随机矩阵理论 —— 信号 vs 噪声奇异值的分界")
print("=" * 60)

# 纯噪声矩阵 (随机): 奇异值应落在 MP 律的 [σ-, σ+] 内
ratio = m / n_dim  # 形状比 c = m/n
sigma_plus = 1 + np.sqrt(ratio)   # MP 上边缘 (单位方差噪声)
sigma_minus = max(0, 1 - np.sqrt(ratio))

pure_noise = 0.05 * np.random.randn(m, n_dim)
_, S_noise, _ = np.linalg.svd(pure_noise, full_matrices=False)
# 归一化噪声奇异值 (除以噪声标准差 × √n)
S_noise_norm = S_noise / (0.05 * np.sqrt(n_dim))

print(f"  矩阵形状 m×n = {m}×{n_dim},  形状比 c = {ratio:.2f}")
print(f"  Marchenko-Pastur 边界: σ- = {sigma_minus:.3f},  σ+ = {sigma_plus:.3f}")
print(f"  纯噪声奇异值范围: [{S_noise_norm.min():.3f}, {S_noise_norm.max():.3f}]")
print(f"  噪声奇异值是否都在 MP 区间内: {S_noise_norm.max() <= sigma_plus + 0.2}")

# 信号矩阵: 前 true_rank 个奇异值应明显突破 σ+
S_signal_norm = S / (0.05 * np.sqrt(n_dim))  # 用噪声尺度归一化 (简化对比)
above_mp = np.sum(S_signal_norm[:true_rank] > sigma_plus)
print(f"  含信号矩阵: 前 {true_rank} 个奇异值中 {above_mp} 个突破 MP 上边缘 σ+={sigma_plus:.2f}")
print("  => 这些突破的奇异值就是'信号', 可用 LoRA 的秩 r 捕获; 其余是'噪声'")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 图1: 奇异值谱 (信号骤降)
ax = axes[0]
ax.semilogy(range(1, len(S) + 1), S, "o-", color="crimson", markersize=4, label="ΔW 奇异值")
ax.axvline(true_rank, color="gray", ls="--", label=f"真实信号秩 = {true_rank}")
ax.set_xlabel("奇异值序号 i"); ax.set_ylabel("σᵢ (对数)")
ax.set_title("奇异值谱: σ₅ 后骤降 → LoRA 用小秩 r 即可")
ax.legend(); ax.grid(True, alpha=0.3)

# 图2: 秩-误差曲线
ax = axes[1]
ax.plot(ranks, relative_err * 100, "s-", color="steelblue", markersize=4)
ax.axvline(true_rank, color="gray", ls="--", label=f"真实秩 = {true_rank}")
ax.axhline(relative_err[true_rank] * 100, color="crimson", ls=":", alpha=0.5)
ax.set_xlabel("LoRA 秩 r"); ax.set_ylabel("相对误差 (%)")
ax.set_title("Eckart-Young: 秩 ↑ → 误差 ↓ (拐点 ≈ 真实秩)")
ax.legend(); ax.grid(True, alpha=0.3)

# 图3: 噪声 vs 信号的奇异值分布 (MP 律)
ax = axes[2]
ax.hist(S_noise_norm, bins=20, alpha=0.6, color="gray", label="纯噪声奇异值")
ax.axvline(sigma_minus, color="green", ls="--", lw=2, label=f"MP 下沿 σ-={sigma_minus:.2f}")
ax.axvline(sigma_plus, color="green", ls="--", lw=2, label=f"MP 上沿 σ+={sigma_plus:.2f}")
# 信号奇异值
for i in range(true_rank):
    ax.axvline(S_signal_norm[i], color="crimson", lw=2, alpha=0.7)
ax.set_xlabel("归一化奇异值"); ax.set_ylabel("频数")
ax.set_title("随机矩阵理论: 信号奇异值突破 MP 上沿")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.suptitle("LoRA = SVD 低秩近似: 线性代数视角", fontsize=14)
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")

# ============================================================
# 实验 5: B=0 初始化验证
# ============================================================
print("=" * 60)
print("实验 5: LoRA 初始化 B=0 保证起点 ΔW=0")
print("=" * 60)

W0 = np.random.randn(d, k) * 0.02  # 预训练权重 (冻结)
r_init = 8
# LoRA 初始化: A 高斯随机, B = 0
A_init = np.random.randn(r_init, k) * 0.01
B_init = np.zeros((d, r_init))
delta_W_start = B_init @ A_init
print(f"  训练起点 BA 的范数: {np.linalg.norm(delta_W_start):.2e} (B=0 → ΔW=0 ✓)")
print(f"  即: 模型行为 = 原始预训练 W₀ (不破坏预训练知识)")

print("\n核心结论:")
print("  LoRA 的全部数学根基 = SVD + Eckart-Young 低秩近似定理.")
print("  语言模型的任务适配增量本征维度低 → 小秩 r 即可无损.")
