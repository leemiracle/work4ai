# -*- coding: utf-8 -*-
"""委托代理仿真:隐藏行动的道德风险(hidden-action moral hazard)。

00-体系结构.md(美之时刻 3:双 agent 对称美)、03-可构造与结构.md(结构引擎 1:
激励相容)与 04-管理理论转代码.md(走廊 1)的配套实验。纯标准库。

模型(Holmström 1979 的两态最小版):
  代理人努力 e ∈ {L, H},成本 c(H)=c, c(L)=0;
  产出:成功 π=R 概率 p_H(高努力)/ p_L(低努力),失败 π=0;Δp = p_H − p_L > 0;
  委托人风险中性,代理人 CRRA 风险厌恶(γ 网格),效用
      u(w) = ((W0+w)^(1−γ) − W0^(1−γ)) / (1−γ)     (u(0)=0;γ→0 退化为线性)
  合同 w=(w_S, w_F),有限责任 LL:0 ≤ w_F ≤ w_S。

一阶最优 FB(努力可观测):完全保险 w_FB = u⁻¹(Ū + c)(确定性死工资);
  代理人租金 = 0(EU 恰等于保留效用);委托人利润 Π_FB = p_H·R − w_FB。

二阶最优 SB(努力不可观测):极小化期望工资 p_H·w_S + (1−p_H)·w_F,约束
  IC: Δp·(u(w_S) − u(w_F)) ≥ c        —— 效用空间拉开差距才肯努力
  IR: p_H·u(w_S) + (1−p_H)·u(w_F) − c ≥ Ū
  LL: w_F ≥ 0
  在效用空间解:u⁻¹ 凸增 ⟹ 把 v_F=u(w_F) 压到下限 0(LL 绑定),v_S = c/Δp。
  此时 IR 松弛量 = **信息租金** rent = p_H·c/Δp − c − Ū > 0;
  委托人亦可退守"只买低努力"(平工资 u⁻¹(Ū),利润 p_L·R − u⁻¹(Ū)),
  SB = max(高努力合同利润, 低努力合同利润)。

敏感性(核心断言):γ↑ ⟹ 同一效用差距 c/Δp 对应的财富差距(激励强度)
膨胀——激励变贵;高努力利润单调下降;γ 过临界点 ⟹ 委托人放弃激励退守低努力。

跑法: python3 -u experiments/00_principal_agent.py
"""

import random


# ---- 参数(全局常量) ----
R = 100.0     # 成功产出
P_H = 0.8     # 高努力成功概率
P_L = 0.4     # 低努力成功概率
DP = P_H - P_L
C = 2.0       # 高努力成本(效用单位)
U_BAR = 1.0   # 代理人保留效用(效用单位)
W0 = 10.0     # CRRA 基础财富
GAMMAS = (0.0, 0.2, 0.4, 0.6, 0.8)


def u(w, gamma):
    """CRRA 效用(规范化 u(0)=0);γ=0 为风险中性。"""
    if abs(gamma) < 1e-12:
        return w
    return ((W0 + w) ** (1.0 - gamma) - W0 ** (1.0 - gamma)) / (1.0 - gamma)


def u_inv(v, gamma):
    """u 的反函数(效用→财富)。v ≥ 0 时有定义。"""
    if abs(gamma) < 1e-12:
        return v
    return (W0 ** (1.0 - gamma) + (1.0 - gamma) * v) ** (1.0 / (1.0 - gamma)) - W0


def first_best(gamma):
    """努力可观测:完全保险,IR 绑定,租金=0。"""
    w_fb = u_inv(U_BAR + C, gamma)
    profit = P_H * R - w_fb
    eu = u(w_fb, gamma) - C          # = Ū(由构造)
    return {"w": w_fb, "profit": profit, "eu": eu, "rent": eu - U_BAR}


def second_best_high(gamma):
    """努力不可观测,买高努力:LL 绑定(w_F=0)+ IC 绑定(v_S=c/Δp)。"""
    v_s = C / DP
    w_f, w_s = 0.0, u_inv(v_s, gamma)
    eu = P_H * v_s - C               # IR 松弛 ⟹ 租金
    rent = eu - U_BAR
    profit = P_H * (R - w_s) + (1.0 - P_H) * (0.0 - w_f)
    return {"w_s": w_s, "w_f": w_f, "spread": w_s - w_f,
            "eu": eu, "rent": rent, "profit": profit}


def second_best_low(gamma):
    """努力不可观测,退守低努力:平工资完全保险,无激励需求。"""
    w = u_inv(U_BAR, gamma)
    profit = P_L * R - w             # 两种状态下都付 w
    return {"w": w, "profit": profit, "eu": U_BAR, "rent": 0.0}


def agent_best_response(w_s, w_f, gamma):
    """代理人最优反应:比较两努力水平的期望效用(隐藏行动的『不可观测』在此)。
    平局偏袒委托人(高努力)——与解析解的弱 IC 处理一致。"""
    eu_h = P_H * u(w_s, gamma) + (1.0 - P_H) * u(w_f, gamma) - C
    eu_l = P_L * u(w_s, gamma) + (1.0 - P_L) * u(w_f, gamma)
    return ("H" if eu_h >= eu_l else "L"), eu_h, eu_l


def monte_carlo_profit(w_s, w_f, gamma, n, seed=20260907):
    """蒙特卡洛:代理人按最优反应选努力,产出按该努力的成功概率抽样。"""
    rng = random.Random(seed)
    effort, _, _ = agent_best_response(w_s, w_f, gamma)
    p = P_H if effort == "H" else P_L
    total = 0.0
    for _ in range(n):
        if rng.random() < p:                       # 成功
            total += R - w_s
        else:                                      # 失败(产出 0)
            total += 0.0 - w_f
    mean = total / n
    # 单次抽值的方差(两点分布):v1=R−w_s(概率 p),v2=−w_f(概率 1−p)
    v1, v2 = R - w_s, -w_f
    var = p * v1 * v1 + (1.0 - p) * v2 * v2 - mean * mean
    se = (var / n) ** 0.5
    return effort, mean, se


def main():
    print("=" * 84)
    print("委托代理:隐藏行动的道德风险 —— 最优合同 vs 风险厌恶 γ(解析+蒙特卡洛)")
    print(f"参数:R={R:.0f}, p_H={P_H}, p_L={P_L}, c={C}, Ū={U_BAR}, W0={W0}")
    print("=" * 84)
    print(f"{'γ':>5} {'w_FB':>7} {'Π_FB':>7} | {'w_S':>7} {'w_F':>5} {'w_S−w_F':>8} "
          f"{'E[w]':>7} {'Π_高':>7} {'Π_低':>7} {'SB':>4} {'租金':>5}")
    rows = []
    for g in GAMMAS:
        fb = first_best(g)
        hi = second_best_high(g)
        lo = second_best_low(g)
        regime = "高" if hi["profit"] >= lo["profit"] else "低"
        e_wage = P_H * hi["w_s"] + (1.0 - P_H) * hi["w_f"]
        print(f"{g:>5.1f} {fb['w']:>7.2f} {fb['profit']:>7.2f} | "
              f"{hi['w_s']:>7.2f} {hi['w_f']:>5.2f} {hi['spread']:>8.2f} "
              f"{e_wage:>7.2f} {hi['profit']:>7.2f} {lo['profit']:>7.2f} "
              f"{regime:>4} {hi['rent']:>5.2f}")
        rows.append((g, fb, hi, lo, regime))

    print()
    print("读数:")
    print("  · 租金列恒为正:LL(w_F≥0)+不可观测努力 ⟹ 代理人拿信息租金(效用空间 p_H·c/Δp−c−Ū)")
    print("    —— FB 行的租金恰为 0:租金是『看不见努力』的价格,不是市场行情")
    print("  · γ: 0.0→0.8,激励强度 w_S−w_F 从 5 膨胀到 100+:CRRA 弯曲使同一效用差距")
    print("    的财富代价膨胀——激励(拉开差距)与保险(抹平差距)的冲突随风险厌恶加剧")
    print("  · γ 过临界点后 Π_高 < Π_低:委托人放弃激励,退守『平工资买低努力』")
    print("    ——『过度风险厌恶杀死强激励』的数值实拍(04 章落点 1 的机制)")

    # ---- γ 临界点:高努力利润 = 低努力利润 ----
    lo_g, hi_g = 0.6, 0.8
    for _ in range(60):
        mid = (lo_g + hi_g) / 2.0
        if second_best_high(mid)["profit"] >= second_best_low(mid)["profit"]:
            lo_g = mid
        else:
            hi_g = mid
    gamma_star = (lo_g + hi_g) / 2.0
    print(f"\nγ 临界点(二分):γ* ≈ {gamma_star:.3f} —— γ>{gamma_star:.2f} 时最优合同是"
          f"『放弃激励』")

    # ---- 蒙特卡洛行为验证(γ=0.2) ----
    g_mc = 0.2
    hi = second_best_high(g_mc)
    eps = 1e-3                                    # IC 严格化:现实合同总留一点余量
    w_s_strict = hi["w_s"] + eps
    print("\n蒙特卡洛验证(γ=0.2,T=200_000):")
    for label, (ws, wf) in {
        "SB 合同+ε(IC 严格)": (w_s_strict, hi["w_f"]),
        "平工资(完全保险)": (first_best(g_mc)["w"], first_best(g_mc)["w"]),
    }.items():
        effort, mean, se = monte_carlo_profit(ws, wf, g_mc, 200_000)
        p = P_H if effort == "H" else P_L
        pred = p * (R - ws) + (1.0 - p) * (0.0 - wf)
        _, eu_h, eu_l = agent_best_response(ws, wf, g_mc)
        print(f"  {label:<22} 代理人选 {effort}  模拟利润 {mean:>7.2f} "
              f"vs 解析 {pred:>7.2f}(±4se≈{4*se:.2f})  EU_H−EU_L={eu_h-eu_l:+.3f}")
        assert abs(mean - pred) < 4 * se + 1e-9, f"{label}: MC {mean:.3f} vs {pred:.3f}"

    # ---- 自验证断言 ----
    rent_theory = P_H * C / DP - C - U_BAR
    assert rent_theory > 0, "LL+隐藏行动应产生正信息租金"
    for g, fb, hi, lo, regime in rows:
        # 断言 1:信息租金存在(SB 高努力合同,效用空间解析值;FB 租金=0 作对照)
        assert abs(hi["rent"] - rent_theory) < 1e-9, f"γ={g}: 租金应为 p_H·c/Δp−c−Ū"
        assert abs(fb["rent"]) < 1e-9, f"γ={g}: FB 完全保险下 IR 绑定,租金应为 0"
        # 断言 2:代理成本存在(Π_FB > Π_SB;风险中性时=纯租金,风险厌恶时=租金+保险费)
        sb_profit = max(hi["profit"], lo["profit"])
        assert fb["profit"] > sb_profit, f"γ={g}: 隐藏行动的代理成本应 > 0"
        # IC/IR/LL 可行性
        assert hi["w_f"] >= 0.0 and hi["w_s"] >= hi["w_f"], f"γ={g}: LL 违反"
        assert DP * (u(hi["w_s"], g) - u(hi["w_f"], g)) >= C - 1e-9, f"γ={g}: IC 违反"
        assert hi["eu"] >= U_BAR - 1e-9, f"γ={g}: IR 违反"
    # 断言 3:最优合同对风险厌恶的敏感性
    spreads = [hi["spread"] for _, _, hi, _, _ in rows]
    profits_h = [hi["profit"] for _, _, hi, _, _ in rows]
    bills = [P_H * hi["w_s"] + (1 - P_H) * hi["w_f"] for _, _, hi, _, _ in rows]
    for i in range(len(rows) - 1):
        assert spreads[i + 1] > spreads[i], "激励强度应随 γ 严格膨胀"
        assert profits_h[i + 1] < profits_h[i], "高努力利润应随 γ 严格下降"
        assert bills[i + 1] > bills[i], "期望工资账单应随 γ 严格上升"
    # 断言 4:γ 足够高时委托人放弃激励(体制切换发生在网格内)
    assert rows[-1][4] == "低", "网格末端(γ=0.8)应切换到低努力合同"
    assert rows[0][4] == "高", "网格起点(γ=0)应保留高努力合同"
    # 断言 5:平工资在隐藏行动下劣于 SB(完全保险杀死激励)
    flat = first_best(0.2)
    flat_profit = P_L * R - flat["w"]
    assert flat_profit < second_best_high(0.2)["profit"], \
        "平工资(买不到高努力)应劣于 SB 激励合同"
    print("\n✓ 自验证通过:信息租金存在(FB=0 vs SB>0)| 代理成本>0 | "
          "激励强度/工资账单随 γ 严格膨胀、利润严格下降 | γ*≈%.3f 处体制切换 "
          "| 蒙特卡洛与解析一致 | 平工资杀死激励" % gamma_star)


if __name__ == "__main__":
    main()
