# -*- coding: utf-8 -*-
"""军事技术扩散模拟:Logistic 采办曲线 × 组织吸收率 × 对手反制窗口
(00/04 章配套实验)。

问题(00 章红线的可算化):同一种新技术(同样的技术潜力 K),
  A. 高吸收组织——训练/条令/编制改造快(战时危机压缩态,r=0.50)
  B. 低吸收组织——制度惯性,试点拖沓(和平态,r=0.12)
谁先形成战斗力?红利窗口有多长?

模型(03 章骨架一/四):
  采办扩散:离散 Logistic,S 曲线 y(t+1)=y+ r·u·y·(1−y/K)
    ——潜力 K 是技术的,斜率 r 是组织的;u~U(0.85,1.15) 为年度
    预算/训练波动;高/低两案配对同噪声(同一预算年景,公平比较)
  对手反制钟:对手在察觉(部署量≥15%)后延迟 D 年启动反制,
    反制成熟度按 logistic 升至 0.85——「使用即正常化」的机制化:
    使用暴露原理,反制随后成熟
  兑现效能:e(t)=y(t)×(1−反制成熟度(t))——效能不是武器的属性,
    是对手反制成熟度的函数(00 章假设三)

五个断言组:
  ① 结构:两案技术潜力/初始采办严格相同,唯一变量=吸收率 r
  ② 形成时间差:低吸收案 T*(90% 潜力时刻)比高吸收案晚 ≥30 年,
     且差值落在 1-107 年的七纪元滞后列包络内——技术必要而
     不充分,组织是充分性的承运人(与军事史家族实测滞后列
     107/17/36/1/7/19 年互证)
  ③ 窗口与峰值:高吸收案的红利窗口(效能≥40% 潜力的年头)与
     峰值效能显著高于低吸收案——慢的组织在反制成熟前兑现
     不了多少潜力
  ④ 窗口可量化:窗口长度随对手响应延迟 D 增大而近似线性延长
     (ΔW≈ΔD)——「使用即正常化」的窗口期=对手响应延迟的函数
  ⑤ 潜力终兑:两案期末部署量都逼近 K——必要条件谁都能满足,
     差别全在时间与窗口(充分性的承运人是组织)

⚠ 学科纪律(02/04 章):K/r/D 均为建制假设的示例值,不是任何
真实军队或项目的数据;推演输出=机器化的反事实,结论的形式
永远是「在 r=X、D=Y 的假设下……」;反制延迟 D 的现实估值来自
情报与建制评估,不来自计算。

跑法: python experiments/adoption_scurve.py
"""

import math
import random

# ── 建制参数(示例值;扫描它们,别信仰它们)───────────────────
K = 100.0                 # 技术潜力上限(两案严格相同——「必要」侧)
Y0 = 0.5                  # 初始采办种子(首批小批量)
R_HIGH = 0.50             # 高组织吸收率(训练/条令/编制改造快)
R_LOW = 0.12              # 低组织吸收率(和平年代制度惯性态)
NOISE = (0.85, 1.15)      # 年度吸收波动(预算/训练年景)
TRIALS = 500
HORIZON = 100             # 推演年数

OBS_THRESHOLD = 15.0      # 对手察觉阈值(规模化使用开始被研究)
FORM_THRESHOLD = 90.0     # 战斗力形成阈值(90% 潜力=规模化部署)
E_FLOOR = 40.0            # 显著效能下限(40% 潜力)

C_MAX, C0 = 0.85, 0.02    # 反制成熟上限/起点
C_GROW = 0.40             # 反制成熟速度
_A = (C_MAX / C0) - 1.0   # logistic 系数,使 c(0)=C0

# 军事史家族七纪元滞后列(实测,互证用参考线;不参与断言)
HIST_LAGS = {"火药": 107, "线列": 17, "堑壕": 36,
             "装甲": 1, "核": 7, "无人": 19}


def adoption_curve(r, trial):
    """一条带年度波动的 Logistic 采办曲线;返回逐年部署量列表。
    配对设计:同一 trial 号两案共用同一噪声序列(同一年景)。"""
    rng = random.Random(83_000 + trial)
    y, series = Y0, [Y0]
    for _ in range(HORIZON):
        u = NOISE[0] + (NOISE[1] - NOISE[0]) * rng.random()
        y += r * u * y * (1.0 - y / K)
        series.append(y)
    return series


def first_index_above(series, level):
    """首个越线年;全程未越线按 HORIZON 截尾计。"""
    for i, v in enumerate(series):
        if v >= level:
            return i
    return HORIZON


def countermeasure(series, delay):
    """反制成熟度序列:察觉年+响应延迟 D 后 logistic 成熟。"""
    t_obs = first_index_above(series, OBS_THRESHOLD)
    t_start = t_obs + delay
    out = []
    for t in range(len(series)):
        if t <= t_start:
            out.append(C0)
        else:
            out.append(C_MAX / (1.0 + _A * math.exp(-C_GROW * (t - t_start))))
    return out


def effective_series(series, delay):
    """兑现效能 e(t)=部署量×(1−反制成熟度)。"""
    cm = countermeasure(series, delay)
    return [y * (1.0 - c) for y, c in zip(series, cm)]


def bonus_window(eff):
    """红利窗口:效能≥E_FLOOR 的年头跨度(首末越线之差)。"""
    above = [i for i, v in enumerate(eff) if v >= E_FLOOR]
    return (above[-1] - above[0]) if above else 0


def evaluate(r, delay):
    """蒙特卡洛:返回(平均形成年, 平均峰值效能, 平均窗口, 期末部署)。"""
    t_form, peak, window, final = [], [], [], []
    for trial in range(TRIALS):
        y = adoption_curve(r, trial)
        eff = effective_series(y, delay)
        t_form.append(first_index_above(y, FORM_THRESHOLD))
        peak.append(max(eff))
        window.append(bonus_window(eff))
        final.append(y[-1])
    n = float(TRIALS)
    return (sum(t_form) / n, sum(peak) / n,
            sum(window) / n, sum(final) / n)


def fmt_row(name, res):
    t_form, peak, window, final = res
    return (f"  {name:<14} 形成年 {t_form:>5.1f}  峰值效能 {peak:>5.1f}"
            f"  红利窗口 {window:>4.1f} 年  期末部署 {final:>5.1f}")


def main():
    print("=" * 76)
    print("军事技术扩散模拟:组织吸收率 × 对手反制窗口(配对同噪声)")
    print("=" * 76)
    print(f"技术潜力 K={K:.0f}(两案相同);吸收率 r: 高 {R_HIGH:.2f} / "
          f"低 {R_LOW:.2f};年度波动 ±15%;试验 {TRIALS} 次/格")
    print(f"反制:察觉线 {OBS_THRESHOLD:.0f} → 延迟 D 年 → logistic "
          f"成熟至 {C_MAX:.2f};显著效能线 {E_FLOOR:.0f}\n")

    scenarios = {
        ("高吸收", R_HIGH, 2): None, ("高吸收", R_HIGH, 10): None,
        ("低吸收", R_LOW, 2): None, ("低吸收", R_LOW, 10): None,
    }
    for key in scenarios:
        name, r, d = key
        res = evaluate(r, d)
        scenarios[key] = res
        print(fmt_row(f"{name}·D={d}", res))

    # ── 断言 1:结构(唯一变量=吸收率)────────────────────────
    assert R_HIGH > R_LOW > 0 and K > 0 and Y0 > 0
    assert all(scenarios[k][3] >= 88 for k in scenarios), \
        "两案期末部署都应逼近 K(潜力终兑:必要条件谁都能满足)"
    print("\n断言 1 通过:两案同潜力/同种子/同噪声,唯一变量=组织吸收率;"
          "\n            期末部署均≥88——必要条件不筛人,充分性才筛 ✓")

    # ── 断言 2:形成时间差(滞后列互证)───────────────────────
    t_hi, t_lo = scenarios[("高吸收", R_HIGH, 10)][0], \
        scenarios[("低吸收", R_LOW, 10)][0]
    gap = t_lo - t_hi
    assert gap >= 30.0, f"形成时间差应≥30 年(实测 {gap:.1f})"
    lag_lo, lag_hi = min(HIST_LAGS.values()), max(HIST_LAGS.values())
    assert lag_lo <= gap <= lag_hi, \
        f"时间差应落在七纪元滞后列包络 [{lag_lo},{lag_hi}] 年内"
    print(f"断言 2 通过:同样技术潜力,战斗力形成差 {gap:.1f} 年——"
          f"落在滞后列包络\n            [{lag_lo},{lag_hi}] 年内"
          f"(军事史实测:{HIST_LAGS}) ✓")
    print("            ——技术必要而不充分,组织是充分性的承运人")

    # ── 断言 3:窗口与峰值的吸收率效应(D=10)──────────────────
    pk_hi = scenarios[("高吸收", R_HIGH, 10)][1]
    pk_lo = scenarios[("低吸收", R_LOW, 10)][1]
    w_hi10 = scenarios[("高吸收", R_HIGH, 10)][2]
    w_lo10 = scenarios[("低吸收", R_LOW, 10)][2]
    assert pk_hi >= pk_lo + 25.0, \
        f"高吸收峰值效能应高出 25+(实测差 {pk_hi - pk_lo:.1f})"
    assert w_hi10 >= 14.0 and w_hi10 >= 2.0 * w_lo10, \
        "高吸收红利窗口应≥14 年且≥低吸收的两倍"
    print(f"断言 3 通过:峰值效能 {pk_hi:.1f} vs {pk_lo:.1f},窗口 "
          f"{w_hi10:.1f} 年 vs {w_lo10:.1f} 年 ✓")
    print("            ——慢的组织:技术到了,组织没到,反制先到,"
          "窗口近乎坍缩")

    # ── 断言 4:窗口可量化(ΔW≈ΔD)──────────────────────────
    w_hi2 = scenarios[("高吸收", R_HIGH, 2)][2]
    dw, dd = w_hi10 - w_hi2, 10 - 2
    assert w_hi10 >= w_hi2 + 5.0, \
        f"响应延迟 +8 年应使窗口至少延长 5 年(实测 ΔW={dw:.1f})"
    assert abs(dw - dd) <= 4.0, \
        f"窗口延长量应近似等于延迟增量(ΔW={dw:.1f} vs ΔD={dd})"
    print(f"断言 4 通过:延迟 D 从 2→10 年,窗口 {w_hi2:.1f}→"
          f"{w_hi10:.1f} 年,ΔW={dw:.1f}≈ΔD={dd} ✓")
    print("            ——「使用即正常化」窗口≈对手响应延迟+反制成熟期:"
          "窗口可量化")

    # ── 结论速查表 ──────────────────────────────────────────
    print("\n" + "=" * 76)
    print("五组断言全部通过 ✓  速查(形成年/峰值效能/红利窗口):")
    print(f"{'场景':<16}{'形成年':>8}{'峰值效能':>10}{'红利窗口(年)':>12}"
          f"{'期末部署':>10}")
    for key in (("高吸收", R_HIGH, 2), ("高吸收", R_HIGH, 10),
                ("低吸收", R_LOW, 2), ("低吸收", R_LOW, 10)):
        name, r, d = key
        t_form, peak, window, final = scenarios[key]
        print(f"{name}·D={d:<4}{t_form:>8.1f}{peak:>10.1f}"
              f"{window:>12.1f}{final:>10.1f}")
    print("\n⚠ 学科纪律:K/r/D=建制假设示例值;结论的正确读法是"
          "\n  「在 r=X、D=Y 的假设下……」。把 K/r/D 当显式变量扫描,"
          "\n  是本模拟区别于新闻推算的第一特征;反制延迟 D 的现实"
          "\n  估值来自情报与建制评估——代码算窗口,不算 D。")


if __name__ == "__main__":
    main()
