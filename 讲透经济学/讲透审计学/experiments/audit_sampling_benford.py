#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计的两件统计武器：属性抽样上界与本福特定律筛查（对应 00 章 §3 / 03 章 §2 / 04 章走廊①②）。

Part A：属性抽样（attributes sampling）的泊松上界。
  审计从来不做"全查"，而是抽 n 笔查偏差。零偏差 ≠ 零风险：
  95% 置信的上偏差率上界 = λ_0.95 / n，其中 λ 满足 P(X≤k | λ)=0.05（泊松）。
  断言：零偏差时上界 ≈ 3.0/n（"查了 60 笔没毛病"只保证偏差率 < 5%）；
        出现 1 笔偏差上界跳升；要减半上界样本量须约翻两番（平方根律）。

Part B：本福特定律（Benford's law）首 digit 筛查。
  自然发生的金额（跨数量级）首位数字 d 出现概率 = log10(1+1/d)——1 远多于 9。
  造假者惯写"中间值"金额（如 3000-8000），首位分布被压平，离 Benford 谱即远。
  检验：卡方统计量 + Nigrini 平均绝对偏差（MAD）分区：
  <0.006 密合 / 0.006-0.012 可接受 / 0.012-0.015 边缘 / >0.015 不密合。
"""
import math
import numpy as np

rng = np.random.default_rng(42)

# ---------- Part A：泊松上界与平方根律 ----------
def poisson_upper(k, conf=0.95, lo=0.0, hi=200.0):
    """求 λ 使 P(X≤k)=1-conf（单侧 95% 上界），二分法。"""
    target = 1 - conf
    for _ in range(200):
        mid = (lo + hi) / 2
        p = sum(math.exp(-mid) * mid ** i / math.factorial(i) for i in range(k + 1))
        if p > target: lo = mid
        else: hi = mid
    return (lo + hi) / 2

n0, tolerable = 60, 0.07          # 样本 60 笔，可容忍偏差率 7%
lam0, lam1 = poisson_upper(0), poisson_upper(1)
ub0, ub1 = lam0 / n0, lam1 / n0
print("== Part A：属性抽样（n=60，可容忍偏差率 7%）==")
print(f"  零偏差: λ={lam0:.3f} → 95% 上偏差率上界 = {ub0:.2%}  （'3.0/n' 律：{3.0/n0:.2%}）")
print(f"  一偏差: λ={lam1:.3f} → 上界跳到 {ub1:.2%}")
assert abs(lam0 - math.log(20)) < 1e-6, "零偏差时 λ 应恰为 -ln(0.05)"
assert ub0 < tolerable < ub1, "零偏差可接受、一偏差即拒绝/扩样——统计抽样的悬崖"
print(f"  判定: 零偏差 {ub0:.2%} < 7% 接受；一偏差 {ub1:.2%} > 7% 拒绝（结论整个翻转于一笔）")

ub_big = poisson_upper(0) / (n0 * 4)
print(f"  平方根律: 样本 60→240，零偏差上界 {ub0:.2%}→{ub_big:.2%}（减半靠翻两番）")
assert abs(ub_big / ub0 - 0.25) < 1e-9

# ---------- Part B：本福特定律筛查 ----------
N = 20_000
benford = np.array([math.log10(1 + 1 / d) for d in range(1, 10)])
natural = 10 ** rng.uniform(0, 6, N)                     # 对数均匀=天然跨数量级金额
gamed = rng.uniform(1500.0, 9500.0, N // 4)             # 造假者的"中间值"四位数

def first_digits(x):
    return np.array([int(str(f"{v:.10e}")[0]) for v in x[:4000]])

def screen(x, tag):
    d = first_digits(x)
    obs = np.array([(d == k).mean() for k in range(1, 10)])
    chi2 = N / 4000 * ((obs - benford) ** 2 / benford).sum() * 1.0
    chi2 = 4000 * ((obs - benford) ** 2 / benford).sum()
    mad = np.abs(obs - benford).mean()
    verdict = "密合" if mad < 0.006 else "可接受" if mad < 0.012 else "边缘" if mad < 0.015 else "不密合→标记详查"
    print(f"  [{tag}] 卡方={chi2:7.1f}（df=8, 5%临界 15.51） MAD={mad:.4f} → {verdict}")
    print(f"    首位=1 占比 {obs[0]:.3f}（Benford 期望 {benford[0]:.3f}）  首位=9 占比 {obs[8]:.3f}（期望 {benford[8]:.3f}）")
    return chi2, mad

print("\n== Part B：本福特定律首 digit 筛查（各 4000 笔）==")
chi_nat, mad_nat = screen(natural, "自然金额")
chi_gam, mad_gam = screen(gamed, "人为中间值金额")

assert chi_nat < 15.51 and mad_nat < 0.006, "自然金额应通过卡方与 MAD 双检"
assert chi_gam > 15.51 and mad_gam > 0.015, "造假金额应双双越界"
print("  Benford 筛查不是证明舞弊，是给 2 万笔交易排序——审计资源永远稀缺，先查最不对劲的 40 笔")

print("\nALL ASSERTIONS PASSED")
