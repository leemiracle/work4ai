# -*- coding: utf-8 -*-
"""experiments/00_falsification.py — 迪昂-蒯因不可证伪性的极简贝叶斯模拟
======================================================================

讲透自然辩证法 · 家族层实验(纯标准库,assert 自验证,exit 0 = 全部通过)

哲学背景
--------
迪昂(1906)与蒯因(1951)的整体论:判决实验打击的从来不是单个理论,
而是「主理论 ∧ 仪器理论 ∧ 辅助假设群」的**合取**。观察到反例时,
否决的只是整个合取——责备落在谁头上,贝叶斯更新有唯一答案,而这个答案
随辅助假设网络的结构系统性变化。

模型(闭合预言的最小贝叶斯化)
--------------------------------
- 成员:主理论 H(先验 h)与 m 条辅助假设 A1..Am(先验 a_i)
- 闭合约定:预言 O 成立 ⟺ 全体成员为真(判决实验的理想化)
- 反例到来(观察到 ¬O):至少一个成员为假
- 责备公式(贝叶斯更新在合取结构上的直接结果):

      P(成员 i 为假 | ¬O) = (1 - p_i) / (1 - ∏ p_j)

三条断言(对应家族 00 章 §七发现 1、03 章 §二)
--------------------------------------------
A1 朴素证伪主义 = m=0 的特例:责备 100% 落主理论
A2 责备随辅助假设条数 m 单调严格下降 —— 理论免疫是算术必然
A3 替罪羊选择是理性的:最不可信的成员自动领受最大责备
   (附带:各成员责备之和 ≥ 1,因为「真凶」不互斥——可能同时坏几个)
A4 事后追加辅助假设可救主理论(蒯因:任何理论都能免于被证伪)
A5 免疫有价格:救一次,合取先验下降,下一次预言的成功概率同步下跌
   ——拉卡托斯「退化的纲领」的贝叶斯版本

运行:python experiments/00_falsification.py
"""

from math import prod


# ---------------------------------------------------------------- 模型核心
def blame_distribution(priors):
    """给定成员先验列表 [p_H, p_A1, ..., p_Am],返回反例后的责备分布。

    闭合约定:O ⟺ 全体为真;观察 ¬O ⟹ ¬(合取)。
    P(i 为假 | ¬O) = (1 - p_i) / (1 - ∏ p_j)
    """
    joint = prod(priors)                 # 合取先验 = 预言成功的事前概率
    anomaly_mass = 1.0 - joint           # P(¬O):至少一个成员为假的总质量
    return [(1.0 - p) / anomaly_mass for p in priors], joint


def show(title, priors, names):
    blames, joint = blame_distribution(priors)
    print(f"\n== {title} ==")
    print(f"   合取先验 ∏p = {joint:.4f}   (预言成功的事前概率)")
    for name, p, b in zip(names, priors, blames):
        bar = "#" * int(round(b * 40))
        print(f"   P({name:<6} 为假|¬O) = {b:6.4f} {bar}")
    return blames, joint


# ================================================================ 段 1
# 责备如何随辅助假设条数单调稀释(A1 + A2)
def segment_auxiliary_count():
    print("\n" + "=" * 62)
    print("段 1:辅助假设网络稀释证伪责备(A1 朴素证伪 = m=0 特例;A2 单调)")
    print("=" * 62)

    h, a = 0.9, 0.9                     # 成熟理论 + 同等可信的辅助假设
    blames_by_m = []
    print(f"\n   {'m(辅助数)':<10}{'P(H假|¬O)':<14}{'P(¬O)':<12}")
    for m in range(10):
        blames, joint = blame_distribution([h] + [a] * m)
        blames_by_m.append(blames[0])
        print(f"   {m:<12}{blames[0]:<14.4f}{1 - joint:<12.4f}")

    assert abs(blames_by_m[0] - 1.0) < 1e-12, "A1 失败:m=0 时责备应为 100%"
    assert all(x > y for x, y in zip(blames_by_m, blames_by_m[1:])), \
        "A2 失败:责备应随 m 单调严格下降"
    print(f"\n   [A1 通过] m=0:责备 = {blames_by_m[0]:.1%}"
          " —— 朴素证伪主义只是没有辅助假设的特例")
    print(f"   [A2 通过] m=0→9:主理论责备 {blames_by_m[0]:.0%} → "
          f"{blames_by_m[-1]:.1%} —— 免疫是算术必然,不是诡辩")


# ================================================================ 段 2
# 异质先验:替罪羊选择在贝叶斯意义下是理性的(A3)
def segment_heterogeneous():
    print("\n" + "=" * 62)
    print("段 2:替罪羊的理性选择(A3 最不可信者领受最大责备)")
    print("=" * 62)

    priors = [0.9, 0.99, 0.9, 0.5]      # H, A1(高精度仪器), A2, A3(新辅助)
    names = ["H", "A1", "A2", "A3"]
    blames, joint = show("异质网络:H=0.9, A=[0.99, 0.9, 0.5]",
                         priors, names)

    weakest = blames.index(max(blames))
    assert weakest == priors.index(min(priors)), \
        "A3 失败:最大责备应落在最小先验的成员上"
    total = sum(blames)
    assert total >= 1.0 - 1e-9, "A3 失败:真凶不互斥,责备之和应 ≥ 1"
    print(f"   [A3 通过] 最大责备落在 {names[weakest]}"
          f"({max(blames):.1%})——替罪羊=先验缺口最大者,选择是理性的")
    print(f"   [A3 附注] 责备之和 = {total:.2f} > 1:'真凶'不互斥,"
          "可能同时坏好几个——责备分配不是分蛋糕")


# ================================================================ 段 4-5
# 事后免疫与它的价格(A4 + A5:蒯因论纲 vs 拉卡托斯账单)
def segment_immunization_price():
    print("\n" + "=" * 62)
    print("段 4/5:任何理论都能免于被证伪——但每次免疫都付价格(A4+A5)")
    print("=" * 62)

    h, a1, a2 = 0.9, 0.9, 0.9
    b0, joint0 = blame_distribution([h, a1, a2])
    scapegoat = 0.5                     # 事后追加的「补丁」辅助假设
    b1, joint1 = blame_distribution([h, a1, a2, scapegoat])

    assert b1[0] < b0[0], "A4 失败:追加辅助应降低主理论责备"
    assert joint1 < joint0, "A5 失败:免疫的代价是合取先验下降"
    print(f"\n   反例后不认账:追加一条先验 {scapegoat} 的辅助假设")
    print(f"   主理论责备:{b0[0]:.2%} → {b1[0]:.2%}   (免罪成功)")
    print(f"   合取先验  :{joint0:.2%} → {joint1:.2%}   (下一次预言成功"
          f"率跌 {1 - joint1 / joint0:.0%})")
    print("   [A4 通过] 蒯因论纲量化版:责备可以被合法导走")
    print("   [A5 通过] 拉卡托斯账单:免疫不是免费的——每次导走责备,"
          "整个纲领的可信预测力都在贬值")

    # 替罪羊先验扫描:免罪难度与价格的同步双曲线
    print("\n   替罪羊先验扫描(越敢甩锅 → 免罪越易 → 合取越不值钱):")
    print(f"   {'替罪羊先验':<12}{'P(H假|¬O)':<14}{'合取先验':<12}")
    scan = []
    for s in (0.9, 0.7, 0.5, 0.3, 0.1):
        b, j = blame_distribution([h, a1, a2, s])
        scan.append((b[0], j))
        print(f"   {s:<14}{b[0]:<14.4f}{j:<12.4f}")
    assert scan[0][0] > scan[-1][0], "扫描失败:低先验替罪羊应更低责备"
    assert scan[0][1] > scan[-1][1], "扫描失败:低先验替罪羊应更低合取先验"
    print("\n   双下降曲线:免罪越容易的纲领,预测力贬值越狠——"
          "波普尔与库恩各执一词的战场,在两条曲线上一览无余")


# ================================================================ 主流程
def main():
    print("迪昂-蒯因不可证伪性 · 极简贝叶斯模拟(讲透自然辩证法家族实验)")
    print("模型:P(成员i为假|¬O) = (1-p_i) / (1-∏p_j);成员=主理论+辅助假设群")
    segment_auxiliary_count()
    segment_heterogeneous()
    segment_immunization_price()
    print("\n" + "=" * 62)
    print("全部断言通过(exit 0)。读法总结:")
    print("  理论免疫不是逻辑漏洞,是合取结构的算术;")
    print("  真正的哲学问题是『哪一次免疫值得付那个价格』——那是价值裁决,")
    print("  代码算得出价格,替不了裁决(家族 03 章 §四的三保留地)。")
    print("=" * 62)


if __name__ == "__main__":
    main()
