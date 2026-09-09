"""
01-pareto-distribution.py · 帕累托分布与 80/20 法则
=====================================================
子领域 3 · inequality · 第 1 节

历史 · 直觉 · 数学
-------------------
历史：
    1896 年，意大利经济学家 Vilfredo Pareto 在《Cours d'Économie 
    Politique》中报告了一个惊人发现：
    
    在他能拿到数据的所有国家（英国、意大利、德国），财富分布都
    遵循同一个数学形式：
    
        P(wealth > w) ∝ w^(-α)，α ≈ 1.5
    
    他还观察到：意大利 80% 的土地掌握在 20% 的人口手里——
    "**80/20 法则**"由此诞生。
    
    120 年后，帕累托分布反复出现：
    · 财富分布、收入分布
    · 城市人口分布（Zipf 法则）
    · 公司规模分布
    · 论文引用分布
    · 网页链接分布
    · Twitter 粉丝分布
    · 战争伤亡分布
    · 地震强度分布
    
    → 这不是巧合，是**乘性过程**（multiplicative process）的必然结果。

直觉：
    为什么财富是幂律而不是正态？
    
    正态分布来自**加性过程**：身高 = 基因 + 营养 + ... → 加起来。
    幂律分布来自**乘性过程**：财富 = (1+r1)(1+r2)...(1+rn) → 乘起来。
    
    加性的结果：钟形，极端值极少
    乘性的结果：长尾，极端值很常见
    
    → 财富是乘性的（投资回报率 + 储蓄率 × 时间），所以是幂律。

数学：
    帕累托分布：
        PDF: p(x) = α x_m^α / x^(α+1)，x ≥ x_m
        CCDF: P(X > x) = (x_m / x)^α
    
    关键指标 α：
        α < 1：极度不平等（首尾比 > 1000:1）
        α = 1：80/20 法则
        α = 1.5：典型财富分布
        α = 2：城市规模
        α > 3：接近正态（不那么不平等）
    
    帕累托指数 α 越小，尾部越"肥"，不平等越严重。

替代模型：对数正态分布
    Gibrat 法则（1931）：log(wealth) ~ Normal
    → 也是乘性过程，但每个 (1+r) 都很小，中心极限定理生效
    → 与帕累托在尾部分歧：对数正态的尾更"瘦"
    → 现实数据往往介于两者之间
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
np.random.seed(42)


# ============================================================
# Part 1: 从乘性随机过程涌现帕累托
# ============================================================

print("=" * 70)
print("Part 1: 乘性过程 → 幂律涌现")
print("=" * 70)
print("""
仿真：10000 个 agent，每人初始财富 100。
每回合：wealth *= (1 + r)，r 是随机回报率。
跑 100 回合，看财富分布演化。
""")

N = 10000
T = 100
wealth = np.ones(N) * 100
history = [wealth.copy()]

for t in range(T):
    # 乘性增长：r ~ Normal(0.001, 0.05)
    r = np.random.normal(0.001, 0.05, N)
    wealth = wealth * (1 + r)
    # 防止负值
    wealth = np.maximum(wealth, 1)
    if (t + 1) % 25 == 0:
        history.append(wealth.copy())

print(f"  初始基尼：{(N + 1 - 2 * np.sum(np.cumsum(np.sort(history[0]))) / np.sum(history[0])) / N:.3f}")
for i, w in enumerate(history[1:], 1):
    sorted_w = np.sort(w)
    cum = np.cumsum(sorted_w)
    gini = (N + 1 - 2 * np.sum(cum) / cum[-1]) / N
    top1 = cum[-1] - cum[int(N * 0.99)]
    print(f"  第 {i * 25:3d} 回合：基尼 {gini:.3f}，top 1% 占 {top1/cum[-1]:.1%}")


# ============================================================
# Part 2: 拟合帕累托指数
# ============================================================

print("\n" + "=" * 70)
print("Part 2: 拟合帕累托指数 α")
print("=" * 70)

final = history[-1]
# 用 CCDF 拟合：log P(X > x) = -α log(x) + const
sorted_w = np.sort(final)
ranks = np.arange(1, len(sorted_w) + 1)
ccdf = 1 - ranks / len(sorted_w)

# 只取 top 20% 拟合（帕累托在尾部最好）
mask = sorted_w > np.percentile(final, 80)
log_x = np.log10(sorted_w[mask])
log_ccdf = np.log10(ccdf[mask])
slope, intercept = np.polyfit(log_x, log_ccdf, 1)

print(f"  尾部拟合：P(X > x) ~ x^({slope:.2f})")
print(f"  帕累托指数 α = {-slope:.2f}")
print(f"  典型现实财富分布 α ≈ 1.5-2.5，我们仿真得到 {-slope:.2f}")
print(f"  → 乘性过程 + 足够时间 → 帕累托涌现")


# ============================================================
# Part 3: 三种分布对比
# ============================================================

print("\n" + "=" * 70)
print("Part 3: 正态 vs 对数正态 vs 帕累托")
print("=" * 70)

normal = np.random.normal(100, 30, 10000)
lognormal = np.random.lognormal(4.5, 0.8, 10000)
pareto = (np.random.pareto(1.5, 10000) + 1) * 50

for name, data in [('正态', normal), ('对数正态', lognormal), ('帕累托', pareto)]:
    sorted_d = np.sort(data)
    cum = np.cumsum(sorted_d)
    top20 = (cum[-1] - cum[int(len(data) * 0.8)]) / cum[-1]
    print(f"  {name:8s}：top 20% 占总量的 {top20:.1%}")


# ============================================================
# Part 4: 可视化
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# 4a: 财富分布演化
ax = axes[0, 0]
labels = ['初始', '25', '50', '75', '100']
colors = ['#3498DB', '#27AE60', '#F39C12', '#E74C3C', '#9B59B6']
for i, (w, label, color) in enumerate(zip(history, labels, colors)):
    ax.hist(w, bins=50, alpha=0.5, label=f'回合 {label}', density=True, color=color)
ax.set_xlabel('财富', fontsize=11)
ax.set_ylabel('密度', fontsize=11)
ax.set_title('乘性过程：财富分布演化\n从均匀到幂律', fontsize=12)
ax.set_xscale('log')
ax.legend()
ax.grid(alpha=0.3)

# 4b: log-log CCDF 拟合
ax = axes[0, 1]
ax.loglog(sorted_w[mask], ccdf[mask], 'o', markersize=3, alpha=0.5, color='#27AE60')
fit_x = np.logspace(np.log10(sorted_w[mask].min()), np.log10(sorted_w.max()), 50)
ax.loglog(fit_x, 10 ** intercept * fit_x ** slope, '-', color='red', linewidth=2,
          label=f'拟合: α = {-slope:.2f}')
ax.set_xlabel('财富 w (log)', fontsize=11)
ax.set_ylabel('P(X > w) (log)', fontsize=11)
ax.set_title('帕累托尾部拟合\n（直线 = 幂律）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 4c: 三种分布对比
ax = axes[1, 0]
bins = np.logspace(np.log10(10), np.log10(max(pareto.max(), lognormal.max())), 40)
ax.hist(normal[normal > 0], bins=bins, alpha=0.5, label='正态', density=True, color='#3498DB')
ax.hist(lognormal, bins=bins, alpha=0.5, label='对数正态', density=True, color='#27AE60')
ax.hist(pareto, bins=bins, alpha=0.5, label='帕累托', density=True, color='#E74C3C')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('数值 (log)', fontsize=11)
ax.set_ylabel('密度 (log)', fontsize=11)
ax.set_title('三种分布对比\n正态=钟形，幂律=长尾', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 4d: 洛伦兹曲线
ax = axes[1, 1]
for name, data, color in [('正态', normal, '#3498DB'),
                          ('对数正态', lognormal, '#27AE60'),
                          ('帕累托', pareto, '#E74C3C')]:
    sorted_d = np.sort(data)
    cum = np.cumsum(sorted_d) / sorted_d.sum()
    pop = np.arange(1, len(sorted_d) + 1) / len(sorted_d)
    ax.plot(pop, cum, label=f'{name}', linewidth=2, color=color)
ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='完全平等')
ax.set_xlabel('累计人口比例', fontsize=11)
ax.set_ylabel('累计财富比例', fontsize=11)
ax.set_title('洛伦兹曲线\n（弧度越大=越不平等）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('01-pareto-distribution.png', dpi=100, bbox_inches='tight')
print(f"\n  图已保存：01-pareto-distribution.png")


# ============================================================
# Part 5: 80/20 法则的误用
# ============================================================

print("\n" + "=" * 70)
print("Part 5: 80/20 法则的真相与滥用")
print("=" * 70)
print("""
真相：
  · 帕累托观察的是 α ≈ 1.5 时的近似比例
  · 不同 α 值对应不同比例：
    α = 0.5：top 30% 占 80%
    α = 1.0：top 20% 占 80% ← 经典 80/20
    α = 1.5：top 15% 占 80%
    α = 2.0：top 10% 占 80%
  · 不是普适的"80/20"，而是 α 决定的连续函数

商业滥用：
  · "20% 的客户带来 80% 的收入"——是的，但可能是 5%、30%、10%
  · "20% 的时间做 80% 的事"——这是借口拖延
  · "20% 的 bug 导致 80% 的事故"——这是真理但不是普适

严肃使用：
  · 用帕累托拟合测量 α，**不要假设 80/20**
  · α 越小越不平等，可以作为不平等指标
  · 比较不同国家/时期的 α 值有意义

✍️ 思考题：
1. 你的工作时间分布是帕累托吗？20% 的工作带来 80% 的成果？
2. 全球财富分布的 α 大约是多少？查 Oxfam 报告。
3. 如果一个国家想降低不平等，应该针对 α 的什么因素？
""")

print("=" * 70)
print("✓ 01-pareto-distribution.py 跑通")
print("=" * 70)
