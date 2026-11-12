# -*- coding: utf-8 -*-
"""比较研究三陷阱的最小实验:辛普森翻转 / 测量不等价的假差异 / QCA 真值表。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(三张结构卡的可构造端)、
04-比较社会学转代码.md(三条走廊)的配套实验。纯标准库(random/statistics/math),
无第三方依赖。

三幕:
  幕一 辛普森悖论(跨社会比较不分层=拿幻觉当发现):
      晋升数据,两国各两部门——A 国:部门1 通过 80/90(88.9%)、部门2 通过
      2/10(20%),聚合 82/100=82%;B 国:部门1 通过 9/10(90%)、部门2 通过
      30/90(33.3%),聚合 39/100=39%。断言:部门内 A 两部门通过率均低于 B
      (88.9%<90%、20%<33.3%)而聚合 A(82%)>B(39%)结论翻转——部门结构分布
      (A 国 90% 的人在高通过部门,B 国 90% 的人在低通过部门)吃掉真实差距;
      直接标准化(50/50 共同权重)后结论翻回 B>A。
  幕二 测量等价性(DIF 简化版,解析+MC 双证):
      两群体潜特质同分布 N(0,1),5 题量表,4 题无 DIF(载荷 0.8、噪声 0.6),
      第 5 题对群体二带 +0.3 偏移。断言:原始总分的群体差≈+0.3(解析值恰为
      δ:前 4 题期望差全为 0,第 5 题期望差 δ;MC 固定种子复现)——量表
      不等价时「跨国均值差」里混着题目的方言;按群体校准该项偏移(用第 5 题
      的群体均值差估计并扣除)后,差异回到≈0。
  幕三 QCA 真值表(集合论,不是概率论):
      3 条件 A/B/C,真值 Y = A·B + C,8 组态 90 例:AB 通路覆盖 30 例
      (组态 ABc 25 例 + ABC 重叠 5 例)、C 通路覆盖 25 例(组态 abC 20 例 +
      ABC 重叠 5 例),其余三个组态 Y=0 共 40 例,两个组态未观察到=逻辑余项。
      断言:解组态一致性=1.0;原始覆盖度之和(30+25=55)>解覆盖度(50,
      重叠 5 例扣减);必要性检验:A 单独非必要(C 通路存在 A=0 的 Y=1 案例)。

跑法: python3 -u experiments/comparison_pitfalls.py
"""

import math
import random
import statistics

# ==================== 幕一:辛普森悖论 ====================


def act1():
    print("=" * 84)
    print("幕一 辛普森悖论:不分层的跨国比较会翻案(晋升数据)")
    print("=" * 84)
    country_a = {"部门1": (80, 90), "部门2": (2, 10)}   # (通过, 申请)
    country_b = {"部门1": (9, 10), "部门2": (30, 90)}
    for name, data in (("A 国", country_a), ("B 国", country_b)):
        print(f"\n{name}:")
        for dept, (passed, applied) in data.items():
            print(f"  {dept}:通过 {passed:>3}/{applied:<3} = {passed / applied:.1%}")
        p = sum(v[0] for v in data.values())
        a = sum(v[1] for v in data.values())
        print(f"  聚合:通过 {p}/{a} = {p / a:.0%}")

    a1 = 80 / 90   # A 国部门1 通过率
    a2 = 2 / 10    # A 国部门2 通过率
    b1 = 9 / 10    # B 国部门1 通过率
    b2 = 30 / 90   # B 国部门2 通过率
    agg_a = (80 + 2) / 100
    agg_b = (9 + 30) / 100

    # 断言 1:部门内 A 两部门通过率均低于 B,聚合却 A>B——结论翻转
    assert a1 < b1, f"A 国部门1 通过率应低于 B 国部门1({a1:.4f} < {b1:.4f})"
    assert a2 < b2, f"A 国部门2 通过率应低于 B 国部门2({a2:.4f} < {b2:.4f})"
    assert agg_a > agg_b, f"聚合应翻转:A 国 {agg_a:.0%} > B 国 {agg_b:.0%}"

    # 直接标准化:给两国套同一部门权重(50/50),消除结构分布差
    std_a = (a1 + a2) / 2
    std_b = (b1 + b2) / 2
    assert std_b > std_a, "标准化后 B 国平均通过率应反超 A 国"

    print("\n读数:")
    print("  · 分层看:B 国每个部门内部的通过率都更高(90%>88.9%、33.3%>20%)")
    print("    ——若真要评「哪国晋升环境好」,证据其实偏向 B")
    print("  · 聚合看:A 国 82% vs B 国 39%,差 43 个百分点——方向完全翻转")
    print("  · 翻转的机关在结构分布:A 国 90% 的申请者挤在高通过的部门1,")
    print("    B 国 90% 的申请者挤在低通过的部门2——部门结构吃掉了部门内差距")
    print(f"  · 直接标准化(50/50 共同权重):A 国 {std_a:.1%} vs B 国 {std_b:.1%},")
    print("    结论翻回「B 更高」——控制了结构分布,幻觉消失")
    print("  · 跨社会比较不分层=拿幻觉当发现:每个国家一行聚合数据的报表,")
    print("    第一眼就该问「这行数字是哪些部门/人群加出来的」")
    print(f"\n✓ 幕一断言通过:部门内 {a1:.1%}<{b1:.0%}、{a2:.0%}<{b2:.1%},"
          f"聚合 {agg_a:.0%}>{agg_b:.0%}——分层方向与聚合方向相反")
    return agg_a, agg_b, std_a, std_b


# ==================== 幕二:测量等价性(DIF 简化版) ====================


def act2():
    print("\n" + "=" * 84)
    print("幕二 测量等价性:量表不等价时,均值差里混着题目的方言(DIF 简化版)")
    print("=" * 84)
    rng = random.Random(20260931)
    n = 50000          # 每群体样本量(固定种子可复现)
    delta = 0.3        # 第 5 题对群体二的偏移(DIF)
    load = 0.8         # 共同载荷(4 题无 DIF)
    noise = 0.6        # 题目噪声标准差(题方差=0.64+0.36=1.0)
    items = 5

    def sample_group(offset):
        """一群潜特质 ~N(0,1) 的被访者:5 题量表,第 5 题带群体偏移。"""
        totals, firsts, fifths = [], [], []
        for _ in range(n):
            theta = rng.gauss(0.0, 1.0)
            scores = [load * theta + rng.gauss(0.0, noise) for _ in range(items)]
            scores[4] += offset
            totals.append(sum(scores))
            firsts.append(scores[0])
            fifths.append(scores[4])
        return totals, firsts, fifths

    t1, i1_1, i5_1 = sample_group(0.0)        # 群体一:全部题目无偏移
    t2, i1_2, i5_2 = sample_group(delta)       # 群体二:第 5 题 +0.3

    mean = statistics.mean
    diff = mean(t2) - mean(t1)                 # 原始总分的群体差
    item1_diff = mean(i1_2) - mean(i1_1)       # 无 DIF 题的群体差
    item5_diff = mean(i5_2) - mean(i5_1)       # 带 DIF 题的群体差

    # 解析:两群体潜特质同分布 → 前 4 题期望差全为 0,第 5 题期望差 δ
    analytic = delta
    assert abs(analytic - 0.3) < 1e-12, "解析假差异应恰为 δ=0.3"

    # MC 互证(固定种子可复现)
    se_total = math.sqrt(2 * items / n)        # 总分差的标准误(总分方差=5)
    se_item = math.sqrt(2 * 1.0 / n)           # 单题差的标准误(题方差=1)
    assert abs(diff - analytic) < 0.05, f"MC 总分差应≈0.3,实测 {diff:.4f}"
    assert abs(item1_diff) < 0.05, f"无 DIF 题差应≈0,实测 {item1_diff:.4f}"
    assert abs(item5_diff - delta) < 0.05, f"第 5 题差应≈0.3,实测 {item5_diff:.4f}"

    # 按群体校准:用第 5 题的群体均值差估计偏移并扣除(实践中 DIF 分析即此逻辑)
    calibrated = diff - item5_diff
    assert abs(calibrated) < 0.05, f"校准后差异应≈0,实测 {calibrated:.4f}"

    print(f"\n两群体潜特质同分布 N(0,1);5 题量表,载荷 {load},前 4 题无 DIF,")
    print(f"第 5 题对群体二偏移 +{delta};每群体 n={n}(固定种子)")
    print(f"\n  原始总分群体差(群体二−群体一):{diff:+.4f}(解析值 {analytic:+.1f},"
          f"MC 标准误≈{se_total:.4f})")
    print(f"  第 1 题(无 DIF)群体差:{item1_diff:+.4f}(≈0)")
    print(f"  第 5 题(带 DIF)群体差:{item5_diff:+.4f}(≈+{delta})")
    print(f"  校准后总分差(扣除第 5 题偏移):{calibrated:+.4f}(≈0)")
    print("\n读数:")
    print("  · 两群体「真实」的潜特质分布一模一样——社会学意义上没有群体差异")
    print("  · 可原始量表硬是「测出」了 0.3 的均值差:全部由第 5 题贡献——")
    print("    题目在那边「变难/变易」了 0.3,不是那边的人变了")
    print("  · DIF(differential item functioning,题目功能差异)的机制:量表")
    print("    在不同情境里不是同一把尺——某题沾了当地文化的方言,")
    print("    「跨国均值差」里就混进了方言差")
    print("  · 校准(按群体估计并扣除该项偏移)后差异归零:假差异可被等价性")
    print("    工程识别并矫正——前提是你先检验等价性,而不是直接比均值")
    print(f"\n✓ 幕二断言通过:解析+MC 双证假差异≈{delta}(实测 {diff:+.4f}),"
          f"校准后归零(实测 {calibrated:+.4f})")
    return diff, item5_diff, calibrated


# ==================== 幕三:QCA 真值表 ====================


def act3():
    print("\n" + "=" * 84)
    print("幕三 QCA 真值表:组态逻辑是集合论,不是概率论(Y = A·B + C)")
    print("=" * 84)
    # 组态 → (案例数, 结局 Y);真值即按 Y = A·B + C 构造
    config_data = {
        (1, 1, 0): (25, 1),   # AB 通路独有
        (1, 1, 1): (5, 1),    # 两通路重叠(ABC)
        (0, 0, 1): (20, 1),   # C 通路独有
        (0, 0, 0): (18, 0),   # 以下三组态 Y=0
        (1, 0, 0): (12, 0),
        (0, 1, 0): (10, 0),
        (1, 0, 1): (0, None),   # 未观察到 → 逻辑余项
        (0, 1, 1): (0, None),
    }
    cases = []
    for (a, b, c), (m, y) in config_data.items():
        cases.extend([(a, b, c, y)] * m)
    total = len(cases)
    outcome = [cs for cs in cases if cs[3] == 1]

    # 从案例清单构建真值表:8 组态逐行统计案例数与一致性
    truth_table = {}
    for row in range(8):
        abc = ((row >> 2) & 1, (row >> 1) & 1, row & 1)
        ys = [cs[3] for cs in cases if cs[:3] == abc]
        n_row = len(ys)
        cons = (sum(ys) / n_row) if n_row else None   # None=逻辑余项
        truth_table[abc] = (n_row, cons)

    print(f"\n真值表(3 条件 → 2³=8 组态,共 {total} 例,Y=1 共 {len(outcome)} 例):")
    print(f"  {'A B C':>7} {'案例数':>4}  一致性")
    for abc in sorted(truth_table, reverse=True):
        n_row, cons = truth_table[abc]
        tag = " ".join(str(v) for v in abc)
        cons_str = "  余项" if cons is None else f"{cons:.1f}"
        print(f"  {tag:>7} {n_row:>4}  {cons_str}")

    # 解:Y = A·B + C(对观察到的组态已是最小表达式)
    in_ab = lambda cs: cs[0] == 1 and cs[1] == 1
    in_c = lambda cs: cs[2] == 1
    in_sol = lambda cs: in_ab(cs) or in_c(cs)

    matched = [cs for cs in cases if in_sol(cs)]
    sol_consistency = sum(cs[3] for cs in matched) / len(matched)

    cov_ab = [cs for cs in outcome if in_ab(cs)]        # AB 通路的原始覆盖
    cov_c = [cs for cs in outcome if in_c(cs)]          # C 通路的原始覆盖
    cov_sol = [cs for cs in outcome if in_sol(cs)]      # 解覆盖(并集,重叠只数一次)
    raw_sum = len(cov_ab) + len(cov_c)
    overlap = raw_sum - len(cov_sol)

    # 断言 3a:解组态一致性 = 1.0(解覆盖的案例全部 Y=1,真值表无矛盾行)
    assert sol_consistency == 1.0, f"解一致性应为 1.0,实测 {sol_consistency}"
    observed_cons = [c for (_, c) in truth_table.values() if c is not None]
    assert all(c in (0.0, 1.0) for c in observed_cons), "真值表不应有矛盾行"
    # 断言 3b:原始覆盖度之和(55)> 解覆盖度(50)——重叠扣减
    assert len(cov_ab) == 30 and len(cov_c) == 25
    assert raw_sum == 55 and len(cov_sol) == 50
    assert raw_sum > len(cov_sol) and overlap == 5, "重叠 5 例应被扣减"
    assert len(cov_sol) == len(outcome) == 50, "解应覆盖全部 Y=1 案例"

    # 断言 3c:必要性检验——A 单独非必要(C 通路存在 A=0 的 Y=1 案例)
    nec_a = sum(1 for cs in outcome if cs[0] == 1) / len(outcome)
    nec_b = sum(1 for cs in outcome if cs[1] == 1) / len(outcome)
    nec_c = sum(1 for cs in outcome if cs[2] == 1) / len(outcome)
    has_y1_without_a = any(cs[0] == 0 and cs[3] == 1 for cs in cases)
    has_y1_without_c = any(cs[2] == 0 and cs[3] == 1 for cs in cases)
    has_y0_with_a = any(cs[0] == 1 and cs[3] == 0 for cs in cases)
    assert nec_a == 0.6 and nec_a < 1.0, "A 的必要性一致性应为 0.6(<1,非必要)"
    assert has_y1_without_a, "应存在 A=0 而 Y=1 的案例(C 单独通路)"
    assert has_y1_without_c, "应存在 C=0 而 Y=1 的案例(AB 单独通路)"
    assert has_y0_with_a, "应存在 A=1 而 Y=0 的案例(A 单独非充分)"

    # 最小性检查:两项都不可去,AB 的字面量也不可再省
    assert any(cs[:3] == (1, 1, 0) and cs[3] == 1 for cs in cases), "去掉 AB 通路将漏覆盖 25 例"
    assert any(cs[:3] == (0, 0, 1) and cs[3] == 1 for cs in cases), "去掉 C 通路将漏覆盖 20 例"
    assert any(cs[:3] == (0, 1, 0) and cs[3] == 0 for cs in cases), "AB 若删去 A 字面量(B 单独)将错盖 10 例 Y=0"

    print(f"\n解:Y = A·B + C")
    print(f"  解组态一致性:{sol_consistency:.1f}(解覆盖的每个案例都是 Y=1)")
    print(f"  AB 通路原始覆盖:{len(cov_ab)} 例(组态 ABc 25 + ABC 重叠 5)")
    print(f"  C  通路原始覆盖:{len(cov_c)} 例(组态 abC 20 + ABC 重叠 5)")
    print(f"  原始覆盖之和:{len(cov_ab)}+{len(cov_c)}={raw_sum}  >  解覆盖:{len(cov_sol)}"
          f"(重叠 {overlap} 例被扣减)")
    print(f"  必要性一致性:A={nec_a:.1f}  B={nec_b:.1f}  C={nec_c:.1f}(均 <1,皆非必要)")
    print("\n读数:")
    print("  · 一致性=1.0 是集合包含:解组态是 Y=1 案例的子集描述,不是")
    print("    「平均而言更可能」——案例要么在组态里,要么不在")
    print(f"  · 两条通路各自报告覆盖 {len(cov_ab)} 与 {len(cov_c)} 例,加起来 {raw_sum} 例,")
    print(f"    比 Y=1 案例总数({len(outcome)})还多 {overlap} 例——ABC 那 5 例被两条")
    print("    通路各数了一次。集合论里覆盖度按并集算,重叠必须扣减:")
    print("    把各通路覆盖度当「方差份额」加总,是读 QCA 表的第一大坑")
    print("  · A 的必要性一致性只有 0.6:20 例 Y=1 的案例根本没有 A——")
    print("    「A 很重要」不等于「非 A 不可」;必要/充分是子集关系,")
    print("    与回归系数的大小无关")
    print("  · 组态逻辑是集合论不是概率论:没有期望值,没有净效应,")
    print("    只有隶属与包含")
    print(f"\n✓ 幕三断言通过:一致性 {sol_consistency:.1f};原始覆盖之和 {raw_sum}>"
          f"解覆盖 {len(cov_sol)}(重叠扣减 {overlap});A 非必要(必要性一致性 {nec_a:.1f})")
    return sol_consistency, raw_sum, len(cov_sol), nec_a


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 辛普森翻转:部门内 A 全面低于 B(88.9%<90%、20%<33.3%),聚合却")
    print("     82%>39%——部门结构分布吃掉真实差距;跨社会比较不分层=拿幻觉当发现")
    print("  ② 量表方言:潜特质同分布的两群体,仅 1 题带 +0.3 偏移,原始总分就")
    print("     「测出」0.3 的系统差(解析+MC 双证);按群体校准该题后差异归零——")
    print("     量表不等价时,跨国均值差里混着题目的方言")
    print("  ③ QCA 真值表:解 Y=A·B+C 一致性=1.0;原始覆盖之和 55>解覆盖 50")
    print("     (重叠 5 例扣减);A 单独非必要(存在 A=0 而 Y=1 的案例)——")
    print("     组态逻辑是集合论,不是概率论")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
