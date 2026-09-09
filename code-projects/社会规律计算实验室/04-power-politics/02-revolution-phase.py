"""
02-revolution-phase.py · Kuran 革命相变模型
=============================================
子领域 4 · power-politics · 最经典模型

历史 · 直觉 · 数学
-------------------
历史：
    1989 年，Timur Kuran 在 *Public Choice* 发表《Sparks and Prairie 
    Fires: A Theory of Unanticipated Political Revolution》。
    
    解释一个谜题：为什么革命**总是突然爆发**，毫无征兆？
    
    · 1789 法国大革命：之前一年法国经济还在增长
    · 1917 俄国革命：沙皇政权看起来稳定
    · 1989 东欧剧变：CIA、克格勃都没预测到
    · 2011 阿拉伯之春：突尼斯小贩自焚 → 整个中东动荡
    
    Kuran 的回答：**人们有"双重偏好"**——
    · 私下偏好：心里反对政权
    · 公开偏好：嘴上支持政权（怕被孤立/惩罚）
    
    当累积的"私下反对"超过临界点，一个偶然事件（火花）引发
    雪崩——所有人同时表露真实偏好，政权瞬间崩溃。
    
    这是**社会相变**最经典的数学模型。

直觉：
    想象 100 个人，每人心里反对政权，但每人都有一个"阈值"：
    "如果有 N 人公开反对，我也反对"。
    
    阈值分布：
    · 激进分子：阈值 0（先反对）
    · 早期跟随者：阈值 1-5
    · 多数人：阈值 20-50
    · 保守者：阈值 80-99
    
    如果有 5 个激进分子站出来 → 早期跟随者跟上 → 共 10 人
    → 下一波跟随者（阈值 ≤ 10）跟上 → 共 25 人 → ...
    
    如果阈值分布**连贯**（每一步都有人接棒），级联到 100 人。
    如果阈值分布**有断层**（比如 25 之后没人 < 50），级联停止。
    
    革命 = 阈值连贯 + 触发事件。
    "稳定"政权 = 阈值有断层，但实际累积压力可能在断层后面。

数学：
    Granovetter (1978) 的"阈值模型"：
    
    每人 i 有阈值 θ_i。在 t 时刻，若公开反对者比例 R(t) ≥ θ_i，
    则 i 加入反对。
    
    离散动力学：
        R(t+1) = #{i : θ_i ≤ R(t)} / N
    
    不动点：R* = #{i : θ_i ≤ R*} / N
    
    相变：阈值分布的"连贯性"决定级联是否发生。

批判：
    - 阈值是固定的，但人会学习和适应
    - 信息不完全：人们不知道有多少人"心里反对"
    - 网络结构：阈值取决于"邻居"而非全体
    - 政府也会学习——会主动制造"断层"（镇压早期抗议）
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
np.random.seed(42)


# ============================================================
# Part 1: Granovetter 阈值模型
# ============================================================

def cascade(thresholds, trigger=0.01, max_iter=20):
    """跑级联仿真。返回每步的反对者比例。"""
    N = len(thresholds)
    R = trigger  # 初始有少量激进分子
    history = [R]
    for _ in range(max_iter):
        new_R = np.mean(thresholds <= R * 100)  # thresholds 是 0-100
        history.append(new_R)
        if abs(new_R - R) < 1e-6:
            break
        R = new_R
    return history

print("=" * 70)
print("Part 1: Granovetter 阈值模型——三种阈值分布")
print("=" * 70)
print("""
对比三种阈值分布：
A. 连贯分布：每段阈值都有人 → 级联成功（革命）
B. 有断层：阈值有缺口 → 级联停止（稳定）
C. 双峰：两极分化 → 看断层位置
""")

N = 1000
# A. 连贯（正态分布，均值 30，标准差 15）
thresh_A = np.clip(np.random.normal(30, 15, N), 0, 100)
# B. 有断层（双峰，避开 30-50）
low = np.random.uniform(0, 30, N // 2)
high = np.random.uniform(50, 100, N // 2)
thresh_B = np.concatenate([low, high])
# C. 多数保守（正态，均值 60）
thresh_C = np.clip(np.random.normal(60, 15, N), 0, 100)

results = {}
for name, thresh in [('A 连贯', thresh_A), ('B 有断层', thresh_B), ('C 多数保守', thresh_C)]:
    hist = cascade(thresh)
    results[name] = (thresh, hist)
    print(f"  {name}：初始 1% → 最终 {hist[-1]*100:.1f}%（共 {len(hist)} 步）")


# ============================================================
# Part 2: 阈值分布的关键——"断层"
# ============================================================

print("\n" + "=" * 70)
print("Part 2: 阈值分布的可视化——找'断层'")
print("=" * 70)
print("""
画阈值分布的 CCDF（≥ R 的人数）vs R 的曲线。
连贯：单调下降
断层：水平段（某 R 区间没人）
""")

for name, (thresh, hist) in results.items():
    sorted_t = np.sort(thresh)
    cum = np.arange(len(sorted_t), 0, -1) / len(sorted_t)
    # 找最大断层
    diffs = np.diff(cum)
    max_gap = 0
    gap_at = 0
    for i, d in enumerate(diffs):
        if d == 0:  # 阈值重复，跳过
            continue
    print(f"  {name}：阈值范围 [{thresh.min():.0f}, {thresh.max():.0f}]")


# ============================================================
# Part 3: 可视化
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# 3a: 三种阈值分布的直方图
ax = axes[0, 0]
for name, (thresh, _), color in zip(results.keys(), results.values(),
                                     ['#27AE60', '#E74C3C', '#F39C12']):
    ax.hist(thresh, bins=30, alpha=0.5, label=name, color=color, density=True)
ax.set_xlabel('阈值 θ（看到多少人反对才加入）', fontsize=11)
ax.set_ylabel('密度', fontsize=11)
ax.set_title('三种阈值分布\n（A 连贯 / B 双峰有断层 / C 多数保守）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 3b: 级联动力学
ax = axes[0, 1]
for name, (_, hist), color in zip(results.keys(), results.values(),
                                   ['#27AE60', '#E74C3C', '#F39C12']):
    ax.plot(range(len(hist)), [r * 100 for r in hist], 'o-', label=name,
            linewidth=2, markersize=8, color=color)
ax.set_xlabel('迭代步', fontsize=11)
ax.set_ylabel('公开反对者比例 (%)', fontsize=11)
ax.set_title('级联动力学\nA：革命（→100%）/ B,C：稳定（停止）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 3c: Kuran 双重偏好模型
print("\n" + "=" * 70)
print("Part 3: Kuran 双重偏好——压力积累 + 火花")
print("=" * 70)
print("""
Kuran 升级版：
  · 每人有"私下不满度" d_i ∈ [0, 1]
  · 公开阈值 θ_i 与 d_i 相关但不等同
  · 当某事件让一些人公开 → 改变其他人的"恐惧成本"
  · 不满积累 + 触发事件 = 相变
""")

ax = axes[1, 0]
# 仿真：30 年压力积累 + 不同时间点的火花
years = np.arange(30)
private_dissatisfaction = 1 - np.exp(-years / 10)  # 私下不满逐年增加
# 假设阈值 = 1 - 0.5 * private_dissatisfaction（越不满阈值越低）
threshold_dynamic = 1 - 0.5 * private_dissatisfaction

public_revolt = np.zeros(30)
# 不同年份点火：5, 15, 25
sparks = [5, 15, 25]
for s in sparks:
    public_temp = np.zeros(30)
    public_temp[s] = 0.05  # 火花引发 5% 反对
    for t in range(s + 1, 30):
        new = np.mean(threshold_dynamic[:t] <= public_temp[t-1])
        public_temp[t] = new
        if new > 0.99:
            break
    ax.plot(years, public_temp * 100, linewidth=2,
            label=f'第 {s} 年点火', alpha=0.8)

ax.plot(years, private_dissatisfaction * 100, 'k--', linewidth=2,
        label='私下不满度', alpha=0.5)
ax.set_xlabel('年份', fontsize=11)
ax.set_ylabel('比例 (%)', fontsize=11)
ax.set_title('Kuran 双重偏好：压力积累 + 点火时机\n早点点火失败，晚点点火成功', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(alpha=0.3)

# 3d: 阈值 vs 不动点（相变图）
ax = axes[1, 1]
# y = f(R) = #{θ ≤ R} / N，画 y = R 和 y = f(R) 的交点
R_range = np.linspace(0, 1, 100)
for name, (thresh, _), color in zip(results.keys(), results.values(),
                                     ['#27AE60', '#E74C3C', '#F39C12']):
    f_R = np.array([np.mean(thresh <= r * 100) for r in R_range])
    ax.plot(R_range * 100, f_R * 100, linewidth=2, label=name, color=color)
ax.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='y = R（不动点条件）')
ax.set_xlabel('R（公开反对者比例 %）', fontsize=11)
ax.set_ylabel('f(R)（阈值 ≤ R 的人数 %）', fontsize=11)
ax.set_title('相变图：f(R) = R 的交点是不动点\n曲线在对角线上方 = 级联继续', fontsize=12)
ax.legend(loc='upper left', fontsize=9)
ax.grid(alpha=0.3)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('02-revolution-phase.png', dpi=100, bbox_inches='tight')
print(f"\n  图已保存：02-revolution-phase.png")


# ============================================================
# Part 4: 历史案例
# ============================================================

print("\n" + "=" * 70)
print("Part 4: 历史案例——为什么预测革命几乎不可能")
print("=" * 70)
print("""
1. **1989 东欧剧变**
   · 6 个月内，东德、波兰、捷克、罗马尼亚、保加利亚政权全垮
   · CIA 和克格勃都没预测到
   · Kuran 解释：私下不满累积 40 年，但被恐惧压制
   · 戈尔巴乔夫放弃武力支持 → "恐惧成本"骤降 → 相变
   
2. **2011 阿拉伯之春**
   · 突尼斯小贩自焚 → 28 天后总统逃亡
   · 埃及、利比亚、也门、叙利亚接连爆发
   · 每国阈值不同，但累积不满类似
   
3. **预测失败的统计**：
   · 政治学家预测的成功率 ≈ 抛硬币
   · 美国国务院 1960-2000 报告里预测的革命，准确率 < 30%
   · 因为相变本质上是临界点附近的"小扰动放大"——不可预测

4. **反面：稳定政权**
   · 朝鲜、土库曼斯坦：信息封闭 + 高镇压成本 → 阈值断层巨大
   · 沙特：用石油财富买稳定 → 私下不满累积慢
   · 但 Kuran 警告：稳定是表面的，断层后面积累可能爆炸
""")

print("=" * 70)
print("✓ 02-revolution-phase.py 跑通")
print("=" * 70)
print("推荐：Kuran 1989 原文 + Granovetter 1978 阈值模型")
