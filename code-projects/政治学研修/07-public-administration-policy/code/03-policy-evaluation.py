#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策评估完整流程 demo
======================
模拟一个政策评估项目，演示 RCT 分析、异质性处理效应、平行趋势检验。
衔接 01-causal-inference.py，是 07 公共行政模块的实操。

场景：评估『政务 APP 推广』对『公民满意度』的影响。

运行：python3 03-policy-evaluation.py
依赖：numpy pandas statsmodels matplotlib
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
SEP = "=" * 70

print(SEP)
print("政策评估完整流程 · 政务 APP 推广效果评估")
print(SEP)

# ============================================================
# Part 1: RCT 随机对照试验分析
# ============================================================
print("\n【Part 1】RCT：政务 APP 推广的随机实验\n")
print("设计：1000 名公民随机分配，500 人获得 APP（处理组），500 人未获得（对照组）。")
print("真实因果效应：APP 使满意度 +6 分。看 RCT 能否恢复。\n")

N = 1000
treated = rng.binomial(1, 0.5, N)
# 真实效应 +6；基线 50；年龄/城乡也有影响
age = rng.integers(20, 70, N)
urban = rng.binomial(1, 0.6, N)
# APP 使用率（部分处理组没用）：实际接受 = treated × 80%
actually_used = treated * rng.binomial(1, 0.8, N)
satisfaction = (50 + 6 * actually_used + 0.2 * (age - 40)
                + 4 * urban + rng.normal(0, 5, N))

df = pd.DataFrame({'treated': treated, 'used': actually_used,
                   'age': age, 'urban': urban, 'satisfaction': satisfaction})

# 朴素比较：处理组 vs 对照组均值
t_mean = df[df.treated == 1].satisfaction.mean()
c_mean = df[df.treated == 0].satisfaction.mean()
print(f"  处理组均值：{t_mean:.2f}")
print(f"  对照组均值：{c_mean:.2f}")
print(f"  原始差异：{t_mean - c_mean:.2f}（这是 ITT 意向处理效应，因为部分人没用 APP）")

# ITT 回归（按分配）
m_itt = smf.ols('satisfaction ~ treated', df).fit()
print(f"\n  ITT 回归（按是否分配）：treated 系数 = {m_itt.params['treated']:.3f}")
print(f"    （低估，因为只有 80% 分配者真用了 APP）")

# ATT / ATE：在 used 上回归（注意：在有依从性问题时需 IV，这里简化演示）
m_ate = smf.ols('satisfaction ~ used', df).fit()
print(f"  按实际使用回归：used 系数 = {m_ate.params['used']:.3f}  ← 接近真实 6")
print(f"  ✓ RCT 的随机分配保证了处理组与对照组可比，差异即因果效应。")

# ============================================================
# Part 2: 异质性处理效应（HTE）
# ============================================================
print("\n【Part 2】异质性处理效应：政策对谁更有效\n")
print("问题：APP 推广对城市和农村公民效果一样吗？对年轻人和老年人呢？")
print("方法：加入交互项 used×urban / used×age。\n")

df['used_urban'] = df['used'] * df['urban']
df['used_age'] = df['used'] * (df['age'] - 40)

m_hte = smf.ols('satisfaction ~ used + urban + age + used_urban + used_age', df).fit()
print(f"  异质性回归：")
print(f"    used（基准效应，农村、40 岁）：{m_hte.params['used']:.3f}")
print(f"    used_urban（城市额外效应）：  {m_hte.params['used_urban']:.3f}")
print(f"    used_age（年龄每增 1 岁的效应变化）：{m_hte.params['used_age']:.4f}")

print(f"\n  解读：APP 对城市公民的效应 ≈ {m_hte.params['used'] + m_hte.params['used_urban']:.2f}")
print(f"        APP 对农村公民的效应 ≈ {m_hte.params['used']:.2f}")
print("  ✓ 异质性分析揭示『政策对谁有效』，这是精准施策的基础。")

# ============================================================
# Part 3: 平行趋势检验（DID 假设验证）
# ============================================================
print("\n【Part 3】平行趋势检验：DID 的关键假设\n")
print("DID 假设：若无政策，处理组与对照组的满意度趋势相同。")
print("验证方法：看政策实施前（t-3, t-2, t-1），两组趋势是否平行。\n")

# 生成面板：政策在第 0 期实施
years = [-3, -2, -1, 0, 1, 2]
n_per_year = 200
rows = []
for g, label, base_trend in [('处理', 'treat', 0.5), ('对照', 'control', 0.5)]:
    for y in years:
        treat = 1 if g == '处理' else 0
        post = 1 if y >= 0 else 0
        # 真实政策效应：处理后处理组额外 +8
        effect = 8 if (treat == 1 and post == 1) else 0
        # 基线差异 + 共同趋势
        base = 52 if treat == 1 else 50
        sat = base + base_trend * y + effect + rng.normal(0, 5, n_per_year)
        for s in sat:
            rows.append({'group': g, 'treat': treat, 'year': y, 'post': post, 'sat': s})

df_pt = pd.DataFrame(rows)

# 计算每年每组均值
pivot = df_pt.groupby(['year', 'group'])['sat'].mean().unstack()

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(pivot.index, pivot['处理'], 'o-', color='crimson', label='Treatment (改革省)')
ax.plot(pivot.index, pivot['对照'], 's-', color='steelblue', label='Control (对照省)')
ax.axvline(0, ls='--', color='gray', alpha=0.5, label='Policy implemented')
ax.set_xlabel('Year (0 = policy)'); ax.set_ylabel('Satisfaction')
ax.set_title('Parallel Trends Test: pre-policy trends should be parallel')
ax.legend()
fig.savefig('07-public-administration-policy/code/parallel_trends.png', dpi=100, bbox_inches='tight')
plt.close(fig)

# 检验政策前趋势是否平行
pre = pivot.loc[[-3, -2, -1]]
trend_treat = pre['处理'].iloc[-1] - pre['处理'].iloc[0]
trend_ctrl = pre['对照'].iloc[-1] - pre['对照'].iloc[0]
print(f"  政策前趋势：")
print(f"    处理组变化（t-3 → t-1）：{trend_treat:.2f}")
print(f"    对照组变化（t-3 → t-1）：{trend_ctrl:.2f}")
print(f"    差异：{abs(trend_treat - trend_ctrl):.2f}（接近 0 = 平行趋势成立）")
print(f"\n  ✓ 趋势基本平行（差异 {abs(trend_treat - trend_ctrl):.2f} 较小），DID 假设成立。")
print(f"    若政策前两组趋势明显发散，DID 就不可靠——这是『事件研究法』的核心。")
print(f"  图已保存：parallel_trends.png")

# DID 回归（必须用全期数据，包含政策前 post=0 和政策后 post=1）
df_pt['did'] = df_pt['treat'] * df_pt['post']
m_did = smf.ols('sat ~ treat + post + did', df_pt).fit()
print(f"\n  全期 DID 回归：did 系数 = {m_did.params['did']:.3f}  ← 真实值 8")
print(f"    （注意：DID 必须同时包含政策前后数据，post 才有 0/1 变化）")

print("\n" + SEP)
print("政策评估完整流程总结")
print(SEP)
print("  1. RCT 分析：随机分配 → 差异即因果效应（金标准）")
print("  2. 异质性（HTE）：政策对谁更有效 → 精准施策")
print("  3. 平行趋势检验：验证 DID 假设 → 因果识别的可信度")
print("\n  核心教训：『政策有效』不是口号，是要用严谨方法证明的。")
print("  好的政策评估 = 清晰的识别策略 + 诚实的效应大小 + 异质性洞察。")
print(SEP)
