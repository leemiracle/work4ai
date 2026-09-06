# -*- coding: utf-8 -*-
"""两组生存数据模拟 + Kaplan-Meier 乘积极限估计 + logrank 检验。

00 章 §一(KM 一支笔)/§七(早期停止高估疗效)、02 章 §一(删失≠缺失)、
03 章 §一(构造 1/2:风险集代数)、04 章走廊 1 配套实验。纯标准库。

设定: 对照组生存时间 ~ Exp(λ_c),中位 12 月;治疗组 HR=0.6(中位 20 月)。
     每人另有独立删失:失联 ~ Exp(均值 36 月) + 30 月行政删失(试验到期)。
     观测 = (T, δ):T=min(生存, 失联, 30),δ=1 仅当死亡先于一切删失。
对照: 主运行(固定种子) —— KM 中位数(应≈12 vs 20)+ logrank(应检出治疗组优势)
      零假设蒙特卡洛 —— 两组同分布,I 类错误应≈α=.05(p 值在天平上均匀)
      备择蒙特卡洛 —— 同主设置,功效应 >80%(Schoenfeld 公式的实证版)
场景: 删失是语言的语法而非数据的损失——KM 每一步都在消费「至少活到 T」的区间信息。

跑法: python experiments/00_survival_sim.py
"""

import math
import random
from math import erfc, exp, log, sqrt

LN2 = math.log(2.0)
LAM_C = LN2 / 12.0            # 对照风险率:中位 12 月
HR = 0.6                       # 治疗组风险比
LAM_T = HR * LAM_C             # 治疗风险率:中位 12/0.6 = 20 月
DROP = 1.0 / 36.0              # 失联率:均值 36 月
ADMIN = 30.0                   # 行政删失:试验 30 月到期
SEED = 20260907


# ---------- 造数:生存 + 删失 ----------  (03 章风险集语法的原料车间)
def sim_group(rng, n, lam):
    """返回 [(T_i, delta_i), ...]:死亡先于一切删失才算事件。"""
    out = []
    for _ in range(n):
        t_event = rng.expovariate(lam)
        t_drop = rng.expovariate(DROP)
        t_obs = min(t_event, t_drop, ADMIN)
        delta = 1 if t_event <= min(t_drop, ADMIN) + 1e-12 else 0
        out.append((t_obs, delta))
    return out


# ---------- 构造 1:KM 乘积极限 ----------  (03 章:每个事件时刻乘 (1-d/n))
def km_curve(data):
    """data=[(T,delta)];返回阶跃曲线 [(t, S(t)), ...],t=0 处 S=1。"""
    times = [t for t, d in data]
    events = [d for t, d in data]
    event_times = sorted(set(t for t, d in data if d == 1))
    s, curve = 1.0, [(0.0, 1.0)]
    for tt in event_times:
        at_risk = sum(1 for t in times if t >= tt - 1e-12)   # 风险集:还「在场」的人
        d = sum(1 for t, d in zip(times, events) if d == 1 and abs(t - tt) < 1e-12)
        s *= (1.0 - d / at_risk)
        curve.append((tt, s))
    return curve


def km_at(curve, t):
    """S(t):曲线在 t 处的取值。"""
    s = curve[0][1]
    for tt, ss in curve:
        if tt <= t + 1e-12:
            s = ss
        else:
            break
    return s


def km_median(curve):
    """中位生存:Ŝ 首次跌破 0.5 的时刻(跌不破返回 None)。"""
    for tt, ss in curve:
        if ss <= 0.5:
            return tt
    return None


# ---------- 构造 2:logrank ----------  (03 章:每个事件时刻一张 2×2 表)
def logrank(g1, g2):
    """返回 (chi2_1, p)。O-E 对账:假如两组无差,组 1 该死几个?"""
    all_event_times = sorted(set(t for t, d in g1 + g2 if d == 1))
    O1 = E1 = V = 0.0
    for tt in all_event_times:
        n1 = sum(1 for t, _ in g1 if t >= tt - 1e-12)   # 组 1 风险集
        n2 = sum(1 for t, _ in g2 if t >= tt - 1e-12)   # 组 2 风险集
        n = n1 + n2
        d1 = sum(1 for t, d in g1 if d == 1 and abs(t - tt) < 1e-12)
        d2 = sum(1 for t, d in g2 if d == 1 and abs(t - tt) < 1e-12)
        d = d1 + d2
        O1 += d1
        E1 += d * n1 / n
        if n > 1:
            V += n1 * n2 * d * (n - d) / ((n - 1) * n * n)
    if V <= 0:
        return 0.0, 1.0
    chi2 = (O1 - E1) ** 2 / V
    p = erfc(sqrt(chi2 / 2.0))          # χ²(1) 生存函数 = 2(1-Φ(√x)) = erfc(√(x/2))
    return chi2, p


def summarize(data):
    curve = km_curve(data)
    med = km_median(curve)
    cens = sum(1 for _, d in data if d == 0)
    return curve, med, cens


def main():
    print("=" * 66)
    print("生存实验:两组模拟 + KM + logrank(HR=%.1f, 中位 12 vs 20 月,"
          "删失=失联 Exp(36)+30 月行政)" % HR)
    print("=" * 66)

    # ---------- 主运行(固定种子):一次试验的全流程 ----------
    rng = random.Random(SEED)
    n = 150
    control = sim_group(rng, n, LAM_C)
    treat = sim_group(rng, n, LAM_T)

    curve_c, med_c, cens_c = summarize(control)
    curve_t, med_t, cens_t = summarize(treat)
    chi2, p = logrank(treat, control)

    print(f"\n[主运行] 每组 n={n}")
    print(f"  对照组:删失 {cens_c}/{n},KM 中位生存 ≈ {med_c:.1f} 月(理论 12),"
          f"S(12)={km_at(curve_c, 12.0):.3f}(理论 0.5)")
    print(f"  治疗组:删失 {cens_t}/{n},KM 中位生存 ≈ {med_t:.1f} 月(理论 20),"
          f"S(12)={km_at(curve_t, 12.0):.3f}(理论 0.5^(0.6)=0.66)")
    print(f"  logrank:χ²(1)={chi2:.2f},p={p:.2e}"
          f"{'  → 检出治疗组生存优势' if p < 0.05 else '  → 未检出'}")

    # ---------- 零假设蒙特卡洛:I 类错误 ----------
    reps_null, n_null = 400, 60
    rng = random.Random(SEED + 1)
    rej = 0
    for _ in range(reps_null):
        a = sim_group(rng, n_null, LAM_C)
        b = sim_group(rng, n_null, LAM_C)          # 同分布:无效应世界
        if logrank(a, b)[1] < 0.05:
            rej += 1
    type1 = rej / reps_null
    print(f"\n[零假设蒙特卡洛] {reps_null} 次重复(n={n_null}/组,同分布)")
    print(f"  I 类错误率 = {type1:.3f}(应≈0.05;p 值在无效应世界均匀分布)")

    # ---------- 备择蒙特卡洛:功效 ----------
    reps_alt, n_alt = 200, 150
    rng = random.Random(SEED + 2)
    rej = 0
    for _ in range(reps_alt):
        a = sim_group(rng, n_alt, LAM_C)
        b = sim_group(rng, n_alt, LAM_T)
        if logrank(b, a)[1] < 0.05:
            rej += 1
    power = rej / reps_alt
    print(f"\n[备择蒙特卡洛] {reps_alt} 次重复(n={n_alt}/组,HR=0.6)")
    print(f"  功效 = {power:.3f}(应 >0.80;Schoenfeld:~120 事件即 80% 功效)")

    print()
    print("读数:")
    print("  · KM 不假设任何分布,阶梯是数据自己走出来的——而它同时是")
    print("    非参数 MLE:删失者只退出风险集,不贡献概率扣减(00 章美之时刻 1)。")
    print("  · logrank 是『期望死亡 vs 实际死亡』的对账:删失的语法地位(区间信息)")
    print("    决定了它对晚期稀疏信息自动降权——完整案例删除会系统性低估生存(02 章)。")
    print("  · 零假设下 p 值应均匀(≈5% 落在 0.05 以下)——这就是『显著』的原始含义:")
    print("    无效应世界里随机长出来的那 5%。凡偷看数据再挑时点,这个均匀性被破坏,")
    print("    I 类错误膨胀——早期停止高估疗效的机器形态(00 章 §七反直觉 2)。")

    # ---------- 自验证断言 ----------
    assert p < 0.05, "主运行应检出治疗组生存优势(logrank p<0.05)"
    assert med_t > med_c, "治疗组 KM 中位生存应高于对照组"
    assert med_c is not None and abs(med_c - 12.0) < 4.0, "对照 KM 中位应≈理论 12 月"
    assert med_t is not None and abs(med_t - 20.0) < 5.0, "治疗 KM 中位应≈理论 20 月"
    assert 0.02 <= type1 <= 0.10, "零假设下 I 类错误应≈0.05(蒙特卡洛容差)"
    assert power > 0.80, "HR=0.6,n=150/组 时功效应 >80%"
    assert cens_c > 0 and cens_t > 0, "本设置下两组都应有删失(语法实验的前提)"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
