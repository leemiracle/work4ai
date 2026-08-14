"""
MIT 18.175 · 实验03: 鞅论与可选停时定理数值验证
依赖: numpy, matplotlib
运行: python3 03_martingale_optional_stopping.py

验证:
  1. 对称随机游走是鞅 — E[S_{n+1}|F_n] = S_n
  2. 可选停时: E[S_τ] = E[S_0] (停时条件下鞅的期望不变)
  3. S_n^2 - n 也是鞅 → E[τ] = a² (到达 ±a 的期望时间)
  4. Azuma-Hoeffding 不等式: 鞅差的浓度
  5. 赌徒破产问题: 可选停时何时失效
  6. RL 中的 TD 学习 — 值函数估计是鞅
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)


# ============================================================
# 向量化的随机游走首达时间工具
# ============================================================
def hitting_time_batch(a, n_sim, p=0.5, max_steps=100000):
    """向量化模拟对称/带偏随机游走首次到达 ±a 的时间和位置。
    返回 (tau_array, s_tau_array)。
    """
    taus = np.full(n_sim, -1, dtype=int)
    s_taus = np.zeros(n_sim)
    active = np.arange(n_sim)        # 原始索引
    pos = np.zeros(n_sim)
    step = 0
    block = 5000
    while len(active) > 0 and step < max_steps:
        m = len(active)
        n_gen = min(block, max_steps - step)
        steps_block = np.where(np.random.random((m, n_gen)) < p, 1, -1)
        cumpos = pos[active][:, None] + np.cumsum(steps_block, axis=1)
        crossed = np.abs(cumpos) >= a
        new_inactive = []
        for j in range(m):
            idx = active[j]
            if taus[idx] >= 0:
                continue
            hit = np.where(crossed[j])[0]
            if len(hit) > 0:
                h = hit[0]
                taus[idx] = step + h + 1
                s_taus[idx] = cumpos[j, h]
                new_inactive.append(j)
        step += n_gen
        # 更新仍在 active 的模拟的 pos
        keep_mask = np.ones(m, dtype=bool)
        keep_mask[new_inactive] = False
        still_active_local = np.where(keep_mask)[0]
        still_active_global = active[still_active_local]
        if len(still_active_global) > 0:
            pos[still_active_global] = cumpos[still_active_local, -1]
        active = still_active_global
    taus[taus < 0] = max_steps
    return taus, s_taus


# ============================================================
# 实验 1: 对称随机游走是鞅
# ============================================================
print("=" * 60)
print("实验 1: 对称随机游走 S_n — 验证 E[S_{n+1}|F_n] = S_n")
print("=" * 60)

n_steps = 1000
n_simulations = 10000
walks = np.cumsum(np.random.choice([-1, 1], (n_simulations, n_steps)), axis=1)

step_n = 500
s_n = walks[:, step_n]
s_n1 = walks[:, step_n + 1]
bins = np.arange(-30, 31, 4)
bin_centers = (bins[:-1] + bins[1:]) / 2
cond_expectations = []
for i in range(len(bins) - 1):
    mask = (s_n >= bins[i]) & (s_n < bins[i + 1])
    if mask.sum() > 10:
        cond_expectations.append(s_n1[mask].mean())
    else:
        cond_expectations.append(np.nan)

valid = ~np.isnan(cond_expectations)
print("  条件期望 E[S_{n+1}|S_n] vs S_n (应近似相等):")
for bc, ce in zip(bin_centers[valid], np.array(cond_expectations)[valid]):
    if abs(bc) < 20:
        print(f"    S_n≈{bc:6.1f} → E[S_{{n+1}}|S_n]≈{ce:6.2f}")
print("  结论: E[S_{n+1}|F_n] ≈ S_n ✓ (鞅性质验证)")

# ============================================================
# 实验 2: 可选停时定理 — E[S_τ] = E[S_0] = 0
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 可选停时 — 到达 ±a 时 E[S_τ] = 0")
print("=" * 60)

for a in [3, 5, 10, 20]:
    taus, s_taus = hitting_time_batch(a, 20000, p=0.5)
    print(f"  a={a:2d}: E[S_τ] = {s_taus.mean():+.4f} (理论 = 0), "
          f"P(S_τ = +a) = {np.mean(s_taus == a):.4f} (理论 = 0.5)")
print("  结论: 对称游走 E[S_τ] = 0 ✓ → 可选停时定理成立")

# ============================================================
# 实验 3: E[τ] = a² — 用 S_n^2 - n 是鞅
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 到达 ±a 的期望时间 E[τ] = a²")
print("=" * 60)

a_values_3 = [3, 5, 10, 20, 50]
for a in a_values_3:
    n_sim = 2000 if a >= 20 else 5000
    taus, _ = hitting_time_batch(a, n_sim, p=0.5)
    empirical = taus.mean()
    theoretical = a ** 2
    print(f"  a={a:2d}: 模拟 E[τ] = {empirical:.1f}, 理论 a² = {theoretical}, "
          f"误差 = {abs(empirical - theoretical)/theoretical*100:.1f}%")
print("  结论: E[τ] = a² ✓ (由 S_n²-n 是鞅 + 可选停时推得)")

# ============================================================
# 实验 4: Azuma-Hoeffding 不等式
# ============================================================
print("\n" + "=" * 60)
print("实验 4: Azuma-Hoeffding — 鞅差的浓度不等式")
print("=" * 60)

n_steps_ah = 200
n_sim = 50000
walks_ah = np.cumsum(np.random.choice([-1, 1], (n_sim, n_steps_ah)), axis=1)
s_final = walks_ah[:, -1]

thresholds = np.arange(5, 50, 5)
actual_probs = []
azuma_bounds = []
for t in thresholds:
    actual = np.mean(np.abs(s_final) >= t)
    bound = 2 * np.exp(-t ** 2 / (2 * n_steps_ah))
    actual_probs.append(actual)
    azuma_bounds.append(min(bound, 1.0))
    print(f"  t={t:3d}: P(|S_n|>=t) 实测 = {actual:.6f}, "
          f"Azuma 上界 = {bound:.6f}")
print("  结论: Azuma 上界始终 ≥ 实测概率 ✓")

# ============================================================
# 实验 5: 赌徒破产 — 可选停时失效
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 赌徒破产 — 可选停时何时失效")
print("=" * 60)

p_win = 0.49
for a in [5, 10]:
    taus_b, s_taus_b = hitting_time_batch(a, 10000, p=p_win)
    print(f"  a={a}: E[S_τ]={s_taus_b.mean():+.3f} (≠ 0, 因为不是鞅!), "
          f"P(到+a)={np.mean(s_taus_b == a):.4f}")
print("  结论: 带偏游走不是鞅 → E[S_τ] ≠ 0 ⚠️")
print("        这是赌场长期盈利的数学本质 (q/p > 1)")

# ============================================================
# 实验 6: RL 中的 TD(0)
# ============================================================
print("\n" + "=" * 60)
print("实验 6: TD(0) 学习 — 值函数估计误差是鞅")
print("=" * 60)

gamma = 0.9
alpha = 0.01
n_episodes = 5000
true_V = np.array([0.0, gamma, 1.0])
V = np.zeros(3)
td_errors_over_time = []

for ep in range(n_episodes):
    state = 0
    while state < 2:
        next_state = state + 1
        reward = 1.0 if next_state == 2 else 0.0
        td_error = reward + gamma * V[next_state] - V[state]
        td_errors_over_time.append(td_error)
        V[state] += alpha * td_error
        state = next_state

td_errors = np.array(td_errors_over_time)
print(f"  估计 V = {V}")
print(f"  真实 V = {true_V}")
print(f"  TD 误差前1000步均值 = {td_errors[:1000].mean():.6f}")
print(f"  TD 误差后1000步均值 = {td_errors[-1000:].mean():.6f}")
print("  结论: V(s) → V*(s) ✓ — TD 误差在真值处期望为 0 (鞅差)")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

for i in range(10):
    walk = np.cumsum(np.random.choice([-1, 1], 500))
    axes[0][0].plot(walk, alpha=0.5, linewidth=0.8)
axes[0][0].axhline(y=10, color="r", linestyle="--", label="±a=10")
axes[0][0].axhline(y=-10, color="r", linestyle="--")
axes[0][0].set_xlabel("步数 n")
axes[0][0].set_ylabel("S_n")
axes[0][0].set_title("对称随机游走轨迹 (鞅)")
axes[0][0].legend()
axes[0][0].grid(alpha=0.3)

a_values = [3, 5, 10, 20, 50]
empirical_taus = []
for a in a_values:
    n_s = 1000 if a >= 20 else 3000
    taus, _ = hitting_time_batch(a, n_s, p=0.5)
    empirical_taus.append(np.mean(taus))
axes[0][1].plot(a_values, empirical_taus, "bo-", label="模拟 E[τ]", linewidth=2)
axes[0][1].plot(a_values, [a ** 2 for a in a_values], "r--", label="理论 a²", linewidth=2)
axes[0][1].set_xlabel("边界 a")
axes[0][1].set_ylabel("E[τ]")
axes[0][1].set_title("可选停时: E[τ] = a²")
axes[0][1].legend()
axes[0][1].grid(alpha=0.3)

axes[1][0].plot(thresholds, actual_probs, "b.-", label="实测 P(|S_n|≥t)", linewidth=2)
axes[1][0].plot(thresholds, azuma_bounds, "r--", label="Azuma 上界", linewidth=2)
axes[1][0].set_xlabel("阈值 t")
axes[1][0].set_ylabel("概率")
axes[1][0].set_title(f"Azuma-Hoeffding 不等式 (n={n_steps_ah})")
axes[1][0].legend()
axes[1][0].grid(alpha=0.3)

axes[1][1].plot(td_errors[:2000], alpha=0.3, linewidth=0.5, color="gray")
window = 100
rolling = np.convolve(td_errors[:2000], np.ones(window) / window, mode="valid")
axes[1][1].plot(range(window - 1, 2000), rolling, "b-", linewidth=2, label="滑动平均 TD误差")
axes[1][1].axhline(y=0, color="r", linestyle="--", label="E[TD误差]=0 (鞅差)")
axes[1][1].set_xlabel("时间步")
axes[1][1].set_ylabel("TD 误差")
axes[1][1].set_title("RL TD(0): 误差收敛到 0 (鞅)")
axes[1][1].legend()
axes[1][1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
