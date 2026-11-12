# -*- coding: utf-8 -*-
"""Lotka 逆幂律与 Price 指数增长的合成实拍。

00/03/04 章配套实验。纯标准库(random/math)。

Part 1  Price 增长:世界论文年产出的指数拟合(1950-2025 合成面板)
  · 分段增速生成:1950-1990 双倍期 15 年(普赖斯经典)→ 1990-2010 18 年 → 2010-2025 显著减速
  · 对数线性最小二乘:经典段 |T2-15|<0.6,全窗 15-18 年(普赖斯窗口),R²>0.99
  · 年代增速切片:增速从 ~4.9%/年 滑向 ~2.1%/年——指数增长自带"到期日"
Part 2  Lotka 逆幂律:累积优势 urn(Simon 1955 / Price 1976 的可执行化身)
  · 新论文 q=0.4 概率开新作者,否则按已有产量比例优选依附(纯累积优势)
  · 作者产量分布的对数-对数回归:斜率 ≈ -2(Lotka 1926 的 1/n²)
  · 一篇作者占比 ≈ 60%(Lotka 化学文摘实测口径)+ 普赖斯平方根定律方向检验

跑法: python experiments/00_lotka_price.py
"""

import math
import random
from collections import Counter


def linreg(xs, ys):
    """一元线性最小二乘(手写,无依赖):返回 slope, intercept, r2。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    intercept = my - slope * mx
    r2 = (sxy * sxy) / (sxx * syy)
    return slope, intercept, r2


# ---------------------------------------------------------------- Part 1

def synthetic_world_output():
    """1950-2025 世界论文年产出(单位:千篇,合成量级锚:1950≈10 万篇)。

    增速设计(连续复利,双倍期 T2 = ln2/r):
      1950-1990  T2=15 年  —— Price《Little Science, Big Science》经典段
      1990-2010  T2=18 年  —— 增速放缓
      2010-2025  T2=28 年  —— 显著减速(普赖斯定律的"自杀条款"显形)
    叠加 1.5% 乘性噪声。
    """
    rng = random.Random(1963)  # 纪念 Frascati 会议与《Little Science, Big Science》同年

    def rate(year):
        if year <= 1990:
            return math.log(2) / 15.0
        if year <= 2010:
            return math.log(2) / 18.0
        return math.log(2) / 28.0

    n = 100.0
    years, out = [], []
    for y in range(1950, 2026):
        years.append(y)
        out.append(n)
        n *= math.exp(rate(y) + rng.gauss(0.0, 0.015))
    return years, out


def part1_price_growth():
    bar = "=" * 64
    print(bar)
    print("Part 1 · Price 指数增长:1950-2025 合成面板的对数线性拟合")
    print(bar)

    years, out = synthetic_world_output()
    logs = [math.log(v) for v in out]

    # 经典段 1950-1990:普赖斯窗口 |T2 - 15| < 0.6
    sl, ic, r2 = linreg(years[:41], logs[:41])
    t2_classic = math.log(2) / sl
    print(f"经典段 1950-1990 拟合: r = {sl:.4%}/年  T2 = {t2_classic:.2f} 年  R² = {r2:.4f}")
    assert abs(t2_classic - 15.0) < 0.6, "经典段翻倍期必须落在普赖斯 15 年窗口"
    assert r2 > 0.99, "指数增长的对数线性拟合应近乎完美"

    # 全窗 1950-2025:减速把双倍期拖到 15-18 年
    slf, icf, r2f = linreg(years, logs)
    t2_full = math.log(2) / slf
    print(f"全窗   1950-2025 拟合: r = {slf:.4%}/年  T2 = {t2_full:.2f} 年  R² = {r2f:.4f}")
    print(f"(2025 年产出约 {out[-1] / 1000:.1f} 百万篇/年,量级锚:现实世界约 2-3 百万)")
    assert 15.0 <= t2_full <= 18.0, "减速后全窗双倍期应仍在普赖斯窗口内偏慢一侧"
    assert r2f > 0.99

    # 年代增速切片:指数增长的"到期日"可直接读出
    def cagr(y0, y1):
        return (out[y1 - 1950] / out[y0 - 1950]) ** (1.0 / (y1 - y0)) - 1.0

    print()
    print("年代增速切片(CAGR):")
    for y0 in range(1950, 2011, 10):  # 整十年切片,最后一段 2010-2020
        print(f"  {y0}-{y0 + 10}: {cagr(y0, y0 + 10):.2%}/年")
    print(f"  2015-2025: {cagr(2015, 2025):.2%}/年(近十年,含减速末段)")
    first, last = cagr(1950, 1960), cagr(2015, 2025)
    assert first - last >= 0.02, "增速应显著下滑——15 年翻倍在有限地球上必然到期"
    print(f"→ 增速从 {first:.1%} 滑到 {last:.1%}:普赖斯定律的正确读法不是")
    print("  \"永远翻倍\",而是\"翻倍正在减速\"。(03 章:规律自带衰减,衰减可测。)\n")


# ---------------------------------------------------------------- Part 2

def cumulative_advantage_urn(papers, q, seed):
    """Simon-Price 累积优势 urn(纯比例依附,无初始加成)。

    初始一位作者一篇论文;此后每篇新论文:
      · 以概率 q 由"新作者"写出(科学界扩容);
      · 否则按各作者已有产量 k 成比例挑选老作者(名声复利:k 越大越容易再写)。
    返回各作者的产量列表。"""
    rng = random.Random(seed)
    counts = [1]
    total = 1  # sum(counts),纯比例依附的分母
    for _ in range(papers - 1):
        if rng.random() < q:
            counts.append(1)
            total += 1
        else:
            x = rng.random() * total
            acc = 0.0
            for i, c in enumerate(counts):
                acc += c
                if acc >= x:
                    counts[i] += 1
                    total += 1
                    break
    return counts


def part2_lotka_powerlaw():
    bar = "=" * 64
    print(bar)
    print("Part 2 · Lotka 逆幂律:累积优势 urn 长出 1/n²")
    print(bar)

    counts = cumulative_advantage_urn(papers=6000, q=0.4, seed=7)
    hist = Counter(counts)
    authors = len(counts)
    print(f"合成社群:{authors} 位作者,共 {sum(counts)} 篇论文"
          f"(新作者率 q=0.4,纯比例依附)")

    # 对数-对数回归:产量分布直方图的斜率(Lotka 1926: -2)
    xs, ys = [], []
    for k in range(1, 26):
        if hist.get(k, 0) >= 3:  # 尾部稀疏箱噪声大,只拟合充足箱
            xs.append(math.log10(k))
            ys.append(math.log10(hist[k]))
    sl, ic, r2 = linreg(xs, ys)
    print(f"\n产量分布 log-log 拟合(k=1..25 充足箱):斜率 = {sl:.3f}"
          f"(Lotka 1926: -2)  R² = {r2:.4f}")
    assert -2.5 <= sl <= -1.7, "斜率应落在 Lotka 逆幂律 -2 的邻域"
    assert r2 > 0.95, "幂律在对数-对数纸上应近乎一条直线"

    # 一篇作者占比:Lotka 化学文摘实测约六成
    one_share = hist.get(1, 0) / authors
    print(f"\n一篇作者占比:{one_share:.1%}(Lotka 化学文摘 A-B 姓氏实测 ≈ 60%)")
    assert 0.50 <= one_share <= 0.70, "一篇作者应约六成——'多产者恒少'"

    # 普赖斯平方根定律方向检验:头部 √N 作者的产量份额
    srt = sorted(counts, reverse=True)
    top = int(math.sqrt(authors))
    share = sum(srt[:top]) / sum(srt)
    people = top / authors
    print(f"\n普赖斯平方根定律:头部 {top} 位作者(人数占比 {people:.1%})"
          f"产出份额 {share:.1%}(理论极限说法:半数)")
    print(f"→ 富集倍数 {share / people:.0f} 倍:马太效应实拍;"
          f"不足半数=有限样本+斜率略陡,方向命中、量级打折")
    assert share >= 5 * people, "√N 头部的份额应远超其人数占比(马太效应)"

    print("\n→ 三行规则(新作者+比例依附)生成一条百年经验律——"
          "结构引擎'累积优势'的全部(03 章)。")


if __name__ == "__main__":
    part1_price_growth()
    part2_lotka_powerlaw()
    print()
    print("[ALL ASSERTS PASSED] Price 指数增长(15 年翻倍窗口+减速)+ "
          "Lotka 逆幂律(斜率≈-2+六成一篇作者)全部命中。")
