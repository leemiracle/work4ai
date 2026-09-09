#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政治学因果推断入门 demo
========================
用模拟数据演示四种核心因果推断方法：OLS / DID / RDD / IV。

核心思想：相关 ≠ 因果。因果推断的全部技术，都是在"构造可信的反事实"。
本脚本设定"真实因果效应"，看各方法能否恢复。

运行：python3 01-causal-inference.py
依赖：numpy pandas statsmodels matplotlib（环境已确认齐全）
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')  # 无头环境
import matplotlib.pyplot as plt
from statsmodels.regression.linear_model import OLS

rng = np.random.default_rng(42)
N = 4000
SEP = "=" * 70

print(SEP)
print("政治学因果推断入门 · 模拟演示")
print("核心问题：我们想知道『政策 A 是否真的导致了结果 B』")
print("难点：我们永远观察不到同一个人『既接受又没接受处理』的两种状态")
print(SEP)

# ============================================================
# Part 0: 为什么相关 ≠ 因果（混淆偏误）
# ============================================================
print("\n【Part 0】为什么相关 ≠ 因果：混淆偏误\n")
print("场景：观察『教育年限』与『政治信任』的关系。")
print("如果直接回归，可能得到正向相关——但这是因果吗？")
print("可能『家庭背景』同时影响教育年限和政治信任（混淆变量）。\n")

# 生成数据：家庭背景 → 教育 + 政治信任（混淆）
family = rng.normal(0, 1, N)                # 家庭背景（未观察）
education = 8 + 2 * family + rng.normal(0, 2, N)  # 教育年限受家庭影响
# 真实因果效应：教育对政治信任的直接影响 = 0.3
trust = 50 + 0.3 * (education - 8) + 1.5 * family + rng.normal(0, 3, N)

df0 = pd.DataFrame({'education': education, 'trust': trust, 'family': family})

# 朴素 OLS（不控制 family）
m_naive = smf.ols('trust ~ education', df0).fit()
print(f"  朴素 OLS（不控制混淆变量）：education 系数 = {m_naive.params['education']:.3f}")
print(f"    → 严重高估！（因为家庭背景同时推高教育和信任）")

# 控制 family 后
m_ctrl = smf.ols('trust ~ education + family', df0).fit()
print(f"  控制 family 后 OLS：education 系数 = {m_ctrl.params['education']:.3f}")
print(f"    → 接近真实值 0.3 ✓")
print(f"  教训：如果遗漏了混淆变量，相关就严重偏离因果。")

# ============================================================
# Part 1: DID（双重差分）—— 政策评估利器
# ============================================================
print("\n【Part 1】DID 双重差分：政策评估\n")
print("场景：某省 2018 年实施『政务公开』改革，测量公民满意度。")
print("问题：满意度上升了，是政策导致的，还是全国性趋势？")
print("DID 思路：用未改革省作对照组，比较『前后变化之差』。\n")

# 生成面板数据：2 省 × 2 期
n_per = 1000
periods = ['2017', '2021']
provinces = ['改革省', '对照省']

rows = []
# 改革省：2017 基线 60，2021 因政策 +8（真实效应）
for p in ['改革省']:
    for t in periods:
        treat = 1
        post = 1 if t == '2021' else 0
        effect = 8 if post == 1 else 0  # 真实政策效应
        sat = 60 + 3 * post + effect + rng.normal(0, 5, n_per)  # +3 全国趋势
        for s in sat:
            rows.append({'province': p, 'year': t, 'treat': treat, 'post': post, 'satisfaction': s})
# 对照省：2017 基线 58，2021 仅 +3 全国趋势
for p in ['对照省']:
    for t in periods:
        treat = 0
        post = 1 if t == '2021' else 0
        sat = 58 + 3 * post + rng.normal(0, 5, n_per)
        for s in sat:
            rows.append({'province': p, 'year': t, 'treat': treat, 'post': post, 'satisfaction': s})

df_did = pd.DataFrame(rows)
df_did['did'] = df_did['treat'] * df_did['post']

# 简单比较组均值
print("  描述性统计：")
tab = df_did.groupby(['province', 'year'])['satisfaction'].mean().unstack()
print(tab.round(2).to_string())
print(f"\n  改革省变化：{tab.loc['改革省','2021']-tab.loc['改革省','2017']:.2f}")
print(f"  对照省变化：{tab.loc['对照省','2021']-tab.loc['对照省','2017']:.2f}")
print(f"  直观 DID（差中之差）：{(tab.loc['改革省','2021']-tab.loc['改革省','2017'])-(tab.loc['对照省','2021']-tab.loc['对照省','2017']):.2f}")

# 回归 DID
m_did = smf.ols('satisfaction ~ treat + post + did', df_did).fit()
print(f"\n  DID 回归系数：")
print(f"    treat（改革省本身差异）：{m_did.params['treat']:.3f}")
print(f"    post（全国趋势）：       {m_did.params['post']:.3f}")
print(f"    did（政策效应，关键！）： {m_did.params['did']:.3f}  ← 真实值 8")
print(f"  ✓ DID 成功识别了政策因果效应，剔除了全国趋势。")

# ============================================================
# Part 2: RDD（断点回归）—— 阈值政策
# ============================================================
print("\n【Part 2】RDD 断点回归：阈值政策\n")
print("场景：某国『选举得票率 50%』决定议员是否当选。")
print("问题：当选是否改变了议员所在选区的『联邦拨款』？")
print("RDD 思路：阈值上下（49.9% vs 50.1%）的选区几乎可比（仿佛随机），")
print("         断点处的『跳跃』就是因果效应。\n")

# 生成 RDD 数据
vote = rng.uniform(40, 60, N)               # 得票率
won = (vote >= 50).astype(int)              # 是否当选（阈值 50）
# 真实因果效应：当选使拨款 +100 万
funding = 200 + 3 * (vote - 50) + 100 * won + rng.normal(0, 30, N)

df_rdd = pd.DataFrame({'vote': vote, 'won': won, 'funding': funding})

# 可视化
fig, ax = plt.subplots(figsize=(8, 5))
for w, label, color in [(0, '未当选', 'gray'), (1, '当选', 'crimson')]:
    sub = df_rdd[df_rdd.won == w]
    ax.scatter(sub.vote, sub.funding, alpha=0.1, s=10, color=color, label=label)
ax.axvline(50, ls='--', color='black', alpha=0.5)
ax.set_xlabel('得票率 (%)'); ax.set_ylabel('联邦拨款（万元）')
ax.set_title('RDD 示例：断点处的跳跃 = 当选的因果效应')
ax.legend()
fig.savefig('06-methodology/code/rdd_demo.png', dpi=100, bbox_inches='tight')
plt.close(fig)
print("  图已保存：rdd_demo.png")

# 线性 RDD（断点两侧分别拟合）
df_rdd['vote_c'] = df_rdd['vote'] - 50  # 中心化
m_rdd = smf.ols('funding ~ won + vote_c + won:vote_c', df_rdd).fit()
print(f"\n  RDD 回归：")
print(f"    won（断点跳跃 = 因果效应）：{m_rdd.params['won']:.3f}  ← 真实值 100")
print(f"  ✓ RDD 识别出当选使拨款增加约 {m_rdd.params['won']:.0f} 万。")

# ============================================================
# Part 3: IV（工具变量）
# ============================================================
print("\n【Part 3】IV 工具变量：当存在不可观察的混淆\n")
print("场景：研究『上大学』对『收入』的因果效应。")
print("问题：能力同时影响上大学和收入（混淆，不可观察）。")
print("IV 思路：找一个只影响『是否上大学』但不直接影响收入的工具。")
print("经典：距离大学远近（Angrist & Krueger 1991 用出生季度）。\n")

# 生成数据
ability = rng.normal(0, 1, N)               # 能力（不可观察，混淆）
# 工具：家到大学的距离（near=1 近，影响上大学但不直接影响收入）
near = rng.binomial(1, 0.5, N)
# 上大学：受距离（+）和能力（+）影响
college = (0.4 * near + 0.5 * ability + rng.normal(0, 1, N) > 0.5).astype(int)
# 收入：真实因果效应 = 上大学 +8000；能力也直接 +5000
income = 30000 + 8000 * college + 5000 * ability + rng.normal(0, 4000, N)

df_iv = pd.DataFrame({'near': near, 'college': college, 'income': income, 'ability': ability})

# 朴素 OLS（有混淆偏误）
m_ols = smf.ols('income ~ college', df_iv).fit()
print(f"  朴素 OLS（混淆能力）：college 系数 = {m_ols.params['college']:.0f}  ← 高估（真实 8000）")

# 2SLS（两阶段最小二乘）
# 用 statsmodels 手动 2SLS（不依赖 linearmodels）
# 第一阶段：college ~ near
stage1 = smf.ols('college ~ near', df_iv).fit()
df_iv['college_hat'] = stage1.fittedvalues
# 第二阶段：income ~ college_hat
stage2 = smf.ols('income ~ college_hat', df_iv).fit()
print(f"  IV（2SLS）：college 系数 = {stage2.params['college_hat']:.0f}  ← 接近真实 8000 ✓")
print(f"  ✓ 工具变量成功剔除了能力的混淆，恢复真实因果效应。")
print(f"  关键假设：距离只通过上大学影响收入（排除性约束），且距离确实影响上大学（相关性）。")

print("\n" + SEP)
print("总结：四种方法的『反事实构造』逻辑")
print(SEP)
print("  OLS   ：控制可观察的混淆变量")
print("  DID   ：用对照组的前后变化，推断处理组『若无处理』")
print("  RDD   ：阈值上下几乎随机，断点跳跃 = 因果效应")
print("  IV    ：用外生工具隔离因果通道")
print("\n  核心教训：没有完美方法，只有『更可信的识别策略』。")
print("  政治学好的实证研究，永远是『问题驱动 + 方法匹配』。")
print(SEP)
