# -*- coding: utf-8 -*-
"""
treaty_reservation_game.py — 条约保留博弈：VCLT 三重门 + 互惠遵守的重复博弈

对应章：00-体系结构（反直觉⑴：软执行却大多被遵守）/ 02-语言特征（§二 同意推理）/
       03-可构造与结构（§一 L1-L2 条约工程）/ 04-国际法学转代码（走廊②③）
GB/T 82040 国际法学 · 家族层实验

演示内容：
  Part A  条约保留状态机（《维也纳条约法公约》VCLT 第 19-21 条简化直译）
          - 第 19 条三重门：条约禁止？保留清单穷尽？与目的和宗旨相容？
          - 第 20(4)(c)/21(1) 条效果矩阵：接受 / 反对 / 反对且阻止生效三态
  Part B  互惠遵守的重复博弈（Henkin 现象的机制版）
          - grim trigger（你违约我永远报复）支撑合作的贴现因子阈值
            δ* = (T-R)/(T-P)：没有警察，但有无穷个明天
          - 民间定理（folk theorem）的两人特例

模型边界（必读）：
  - Part A 的"与目的和宗旨相容"（VCLT 19(c)）是规范性判断：
    代码不计算它，只消费"裁判输入"的布尔值——这正是 04 章
    可机械化边界表里'目的性检验=半自动'的现场演示
  - Part B 是机制解释模型，不是行为预测模型：真实国家还受声誉、
    国内政治、议题联动影响；支付矩阵是教学设定
  - 效果矩阵取最简化读法；VCLT 第 20(4)(a)(b)(5)、第 20(5) 十二个月
    默认接受等细则未建模（注释标出）

运行：python treaty_reservation_game.py   （纯标准库，assert 自验证，exit 0）
"""

from itertools import product

# ================================================================ Part A
# VCLT 第 19-21 条：保留的可许性与效果（简化状态机）

def reservation_admissible(treaty, reservation):
    """VCLT 第 19 条三重门。返回 (是否可许, 理由)。

    treaty: dict(name, articles, reservations_prohibited, permitted_list)
    reservation: dict(state, article, text, compatible_object_purpose)
      -- compatible_object_purpose 是"裁判输入"：目的与宗旨检验
         是法学论证，不是查表（见模型边界）
    """
    if treaty["reservations_prohibited"]:                      # 门 1
        return False, "VCLT 19(a): treaty prohibits reservations"
    plist = treaty["permitted_list"]
    if plist is not None and reservation["article"] not in plist:   # 门 2
        return False, "VCLT 19(b): outside the permitted list"
    if not reservation["compatible_object_purpose"]:           # 门 3
        return False, "VCLT 19(c): incompatible with object and purpose"
    return True, "admissible"


def reservation_effect_matrix(treaty, reservation, reactions):
    """VCLT 第 20-21 条效果矩阵（最简化读法）。

    reactions: {state: "accept" | "object" | "object_and_oppose"}
    返回 {对方国: {文章: 效果}} 与总体缔约状态。
      accept            → 保留条款"在保留范围内修改后"适用于两国间（21(1)(a)）
      object            → 条约仍生效，但被保留条款"在该范围内不适用"于
                          两国间（21(1)(b)）
      object_and_oppose → 反对且阻止条约在两国间生效（20(4)(c)），
                         全部条款均不适用（本演示从简，不建"条约其余
                          部分可分离适用"之分支）
    """
    art, res_state = reservation["article"], reservation["state"]
    matrix = {}
    for other, react in reactions.items():
        if react == "accept":
            row = {a: ("as_modified_by_reservation" if a == art else "applies")
                   for a in treaty["articles"]}
        elif react == "object":
            row = {a: ("does_not_apply_between_them" if a == art else "applies")
                   for a in treaty["articles"]}
        else:  # object_and_oppose
            row = {a: "treaty_not_in_force_between_them"
                   for a in treaty["articles"]}
        matrix[other] = row
    # 简化：保留可许 + 至少一国接受（或未全体反对且阻止）→ 保留国成缔约国
    # （VCLT 20(4)(a) 的接受要求与 20(5) 十二个月默认接受规则未建模）
    is_party = any(r == "accept" for r in reactions.values())
    return {"reserving_state": res_state, "is_party": is_party,
            "matrix": matrix}


def part_a_reservation_machine():
    print("Part A: VCLT 19-21 reservation state machine (toy treaty)")
    # 玩具条约：跨境电子证据调取合作公约（虚构，仅演示机制）
    treaty = {
        "name": "Toy Convention on Cross-Border Evidence Cooperation",
        "articles": ["A1_mutual_assistance", "A2_data_protection_floor",
                     "A3_dispute_settlement"],
        "reservations_prohibited": False,      # UNCLOS 式"单一公约"才整体禁保
        "permitted_list": None,               # None = 无保留清单限制
    }
    reservation = {
        "state": "R",
        "article": "A2_data_protection_floor",
        "text": "R may substitute its domestic localization regime",
        "compatible_object_purpose": True,     # 裁判输入：本保留与目的相容
    }
    reactions = {"S1": "accept", "S2": "object", "S3": "object_and_oppose"}

    ok, why = reservation_admissible(treaty, reservation)
    assert ok and why == "admissible"
    result = reservation_effect_matrix(treaty, reservation, reactions)
    assert result["is_party"] is True
    m = result["matrix"]
    # S1 接受 → A2 在保留范围内修改后适用
    assert m["S1"]["A2_data_protection_floor"] == "as_modified_by_reservation"
    assert m["S1"]["A1_mutual_assistance"] == "applies"
    # S2 反对但未阻止生效 → A2 在保留范围内于两国间不适用
    assert m["S2"]["A2_data_protection_floor"] == "does_not_apply_between_them"
    assert m["S2"]["A3_dispute_settlement"] == "applies"
    # S3 反对且阻止生效 → 两国间条约不生效
    assert m["S3"]["A1_mutual_assistance"] == "treaty_not_in_force_between_them"

    # 门 1 反例：条约明文禁止保留（一揽子"单一公约"的常见工艺）
    ban_treaty = dict(treaty, reservations_prohibited=True)
    ok1, why1 = reservation_admissible(ban_treaty, reservation)
    assert not ok1 and "prohibits" in why1
    # 门 2 反例：保留清单穷尽
    list_treaty = dict(treaty,
                       permitted_list=["A3_dispute_settlement"])
    ok2, why2 = reservation_admissible(list_treaty, reservation)
    assert not ok2 and "permitted list" in why2
    # 门 3 反例：与目的和宗旨不相容（裁判改判输入 → 结论翻转）
    bad_res = dict(reservation, compatible_object_purpose=False)
    ok3, why3 = reservation_admissible(treaty, bad_res)
    assert not ok3 and "object and purpose" in why3

    for other, row in m.items():
        eff = row["A2_data_protection_floor"]
        print(f"  R vs {other} ({reactions[other]:<17}): A2 -> {eff}")
    print("  gates: prohibited->rejected; off-list->rejected; "
          "object-purpose->rejected (adjudicator input flips verdict)")
    print("  Part A: ALL ASSERTIONS PASSED\n")


# ================================================================ Part B
# 互惠遵守的重复博弈：Henkin 现象的机制版

# 囚徒困境支付（教学设定）：R=互守约3  T=背叛诱惑5  P=互违约1  S=被违约0
PAYOFF = {("C", "C"): (3.0, 3.0), ("C", "D"): (0.0, 5.0),
          ("D", "C"): (5.0, 0.0), ("D", "D"): (1.0, 1.0)}
R_, T_, P_, S_ = 3.0, 5.0, 1.0, 0.0


def delta_star(T=T_, R=R_, P=P_):
    """grim trigger 支撑合作的最小贴现因子：δ*=(T-R)/(T-P)。

    直觉：背叛当期多赚 (T-R)，代价是未来每期只剩 P 而非 R；
    贴现和的比较给出阈值。δ≥δ* 时"你违约我永远报复"的威胁
    足以让守约成为最优——没有警察，但有无穷个明天。
    """
    return (T - R) / (T - P)


def grim_trigger(my_hist, other_hist):
    """先合作；对方一旦违约，永远报复（民间定理的最简策略）。"""
    return "D" if "D" in other_hist else "C"


def tit_for_tat(my_hist, other_hist):
    """先合作；此后镜像对方上一轮。"""
    return other_hist[-1] if other_hist else "C"


def always_defect(my_hist, other_hist):
    return "D"


def always_cooperate(my_hist, other_hist):
    return "C"


def play(s1, s2, rounds):
    """跑一场重复博弈，返回 (双方各轮动作, 双方总支付)。"""
    h1, h2 = [], []
    total = [0.0, 0.0]
    for _ in range(rounds):
        m1 = s1(h1, h2)
        m2 = s2(h2, h1)
        p1, p2 = PAYOFF[(m1, m2)]
        h1.append(m1)
        h2.append(m2)
        total[0] += p1
        total[1] += p2
    return h1, h2, total


def cooperation_rate(hist):
    return hist.count("C") / len(hist)


def part_b_compliance_game():
    print("Part B: reciprocity without a police (repeated PD, 60 rounds)")
    n = 60

    # 1. 互惠均衡：grim vs grim → 全程守约（Henkin 现象的机制内核）
    h1, h2, tot = play(grim_trigger, grim_trigger, n)
    assert cooperation_rate(h1) == 1.0 and cooperation_rate(h2) == 1.0
    assert tot == [R_ * n, R_ * n]
    henkin_index = sum(1 for a, b in zip(h1, h2) if a == b == "C") / n
    assert henkin_index >= 0.95

    # 2. 背叛的诱惑被明天吃掉：对 grim 对手，
    #    全程守约 3n vs 首轮背叛后互罚 T+P(n-1)——守约胜出（n>2 即可）
    g1, d2, tot_gd = play(grim_trigger, always_defect, n)
    assert g1[0] == "C" and "C" not in g1[1:]      # 报复从第 2 轮起永远持续
    assert cooperation_rate(g1) == 1.0 / n
    value_coop, value_defect_vs_grim = R_ * n, T_ + P_ * (n - 1)
    assert value_coop > value_defect_vs_grim
    assert tot_gd == [S_ + P_ * (n - 1), T_ + P_ * (n - 1)]

    # 3. 阈值公式：δ* = (T-R)/(T-P) = 2/4 = 0.5（解析）
    ds = delta_star()
    assert abs(ds - 0.5) < 1e-12
    # 贴现值验证：合作价值 R/(1-δ) vs 背叛价值 T+δP/(1-δ)
    for delta, coop_is_best in ((0.6, True), (0.4, False)):
        v_coop = R_ / (1.0 - delta)
        v_defect = T_ + delta * P_ / (1.0 - delta)
        assert (v_coop > v_defect) == coop_is_best
        assert (delta >= ds) == coop_is_best     # 与阈值公式一致
    # 高诱惑议题（T=7）：阈值升到 0.667 → 合作更难维持
    assert abs(delta_star(T=7.0) - 4.0 / 6.0) < 1e-12

    # 4. TFT 同样能守约，但对噪音更脆（一次性背叛引发报复循环）
    t1, t2, tot_tt = play(tit_for_tat, tit_for_tat, n)
    assert cooperation_rate(t1) == 1.0 and tot_tt == [R_ * n, R_ * n]

    # 5. 单轮逻辑（无明天）中背叛占优——对照出"重复"才是守法之源
    p_c, p_d = PAYOFF[("C", "D")], PAYOFF[("D", "C")]
    assert p_d[0] > PAYOFF[("C", "C")][0]         # 单轮：背叛是占优策略

    print(f"  grim vs grim          : compliance {cooperation_rate(h1):.0%}, "
          f"payoff {tot[0]:.0f} each (Henkin index {henkin_index:.0%})")
    print(f"  grim vs always-defect : defector total {tot_gd[1]:.0f} < "
          f"mutual-coop total {R_ * n:.0f} -> patience beats temptation")
    print(f"  delta* = (T-R)/(T-P) = {ds}  "
          f"(delta>=0.5 sustains, delta<0.5 collapses; T=7 -> {delta_star(T=7.0):.3f})")
    print("  one-shot PD: defection dominates -> repetition is the enforcer")
    print("  Part B: ALL ASSERTIONS PASSED\n")


# ================================================================ 主程序

def main():
    part_a_reservation_machine()
    part_b_compliance_game()
    print("ALL ASSERTIONS PASSED (Part A + Part B)")


if __name__ == "__main__":
    main()
