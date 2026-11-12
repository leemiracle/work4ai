# -*- coding: utf-8 -*-
"""算法招聘的公平陷阱:历史标签筛选器 vs 去代理+阈值校准(检索校准 2026-09-07 方向锚的
教学化仿真;公平概念按学术文献通说:统计均等/校准公平/机会均等,见 Kleinberg et al. 2016、
Chouldechova 2017——基础率不同时诸标准不可兼得)。

00-体系结构.md(反直觉 3)、02-语言特征.md(公平词汇的数学化)、
04-人力资源转代码.md(走廊 1)的配套实验。纯标准库(random/math)。

设定(教学化的最小宇宙):
  两群体 A/B 的**能力 θ 完全同分布** N(0,1)(这是"能力同分布"的断言前提);
  合格定义 qual = θ ≥ z_{0.80} = 0.8416(恰为全体前 20%)。
  可见信号 s = θ + ε,ε~N(0,0.8²);B 组信号有**系统性偏移 −μ**(μ=0.3:
  学历折算/人脉可见度等让 B 的读数整体偏低——信号偏移,不是能力差异)。
  代理变量 p ∈ {0,1}:与组别强相关(A 基率 0.75 / B 基率 0.30)、与能力弱相关
  (π_g(θ)=base_g+0.25θ 截断)——历史偏爱的"人脉背书",有点能力信息,更多组别信息。
  **历史录用规则**(制造历史标签):hire ⟺ s + 1.5·p ≥ τ_H,τ_H 取历史池 80 分位
  (整体录取率=20%)——历史决定因此系统性偏 A。

三种筛选器(同一申请池上评估,阈值都在历史池上校准、不偷看测试池):
  ① 朴素:用历史标签训练的逻辑回归,特征 (s, p)——"用历史标签训练的筛选器";
  ② 去代理+公共阈值:删掉 p,只剩 s,按目标录取率在历史池取**单一**阈值;
  ③ 去代理+组别校准(统计均等式):按组别各取 80 分位阈值,使两组录取率均=20%
     (组别感知的做法,不同法域对其有不同规定,此处仅作教学对比,不构成合规建议)。

核心断言:
  (1) 朴素筛选器产生组间录取率差(偏移被历史标签"合法化"并复制);
  (2) 修正后差异单调收窄(②>③),且整体准确率损失有限(fairness-accuracy 权衡);
  (3) 反直觉对照:公共阈值下 B 组录取者的合格率反而更高(翻越了更高的有效门槛)
      ——"录取率均等"与"录取者合格率图景"不可兼得的现场;
  (4) 教学边界声明:本设定能力同分布、组内信号机制同构,故组别校准近乎"免费";
      文献中的不可兼得定理在**基础率不同**时才咬人(留作练习,见文末注)。

跑法: python -u experiments/hiring_fairness.py
"""

import math
import random

# ---- 世界参数(常量) ----
SEED = 20260907
N_TRAIN = 20_000          # 历史池(校准与训练用)
N_TEST = 40_000           # 新申请池(评估用)
PCT_A = 0.6               # A 组占比
MU = 0.30                 # B 组可见信号的系统性偏移(下移)
SIG_S = 0.8               # 信号噪声标准差
BASE_PA, BASE_PB = 0.75, 0.30   # 代理变量基率(A/B)
DELTA_P = 0.25            # 代理变量对能力的弱载荷
W_PROXY = 1.5             # 历史规则给代理变量的权重
Q_TARGET = 0.20           # 目标整体录取率 = 合格率
Q_CUT = 0.8416212335726736      # Φ^{-1}(0.80):合格线(前 20%)
LR = 2.0                  # 逻辑回归学习率
EPOCHS = 300              # 逻辑回归迭代数(数据线性可分,边界稳定即可)


def gen_pool(rng, n):
    """生成申请池:组别/能力/信号/代理变量/合格真值(两步:先组别再个体)。"""
    rows = []
    for _ in range(n):
        grp = "A" if rng.random() < PCT_A else "B"
        theta = rng.gauss(0.0, 1.0)
        shift = -MU if grp == "B" else 0.0
        s = theta + shift + rng.gauss(0.0, SIG_S)
        base = BASE_PA if grp == "A" else BASE_PB
        pi = min(0.95, max(0.05, base + DELTA_P * theta))
        p = 1 if rng.random() < pi else 0
        rows.append({"grp": grp, "theta": theta, "s": s, "p": p,
                     "qual": theta >= Q_CUT})
    return rows


def sigmoid(z):
    """数值稳定的 sigmoid(截断防溢出)。"""
    z = max(-30.0, min(30.0, z))
    return 1.0 / (1.0 + math.exp(-z))


def fit_logistic(rows, epochs=EPOCHS, lr=LR):
    """在历史标签上训练逻辑回归(特征:截距/s/p)。数据线性可分,
    权重缓慢增长,决策边界收敛到历史规则的阈值结构——这正是要暴露的东西。"""
    w = [0.0, 0.0, 0.0]
    xs = [(1.0, r["s"], float(r["p"])) for r in rows]
    ys = [1.0 if r["hist_hire"] else 0.0 for r in rows]
    n = len(rows)
    for _ in range(epochs):
        g0 = g1 = g2 = 0.0
        for (x0, x1, x2), y in zip(xs, ys):
            d = sigmoid(w[0] * x0 + w[1] * x1 + w[2] * x2) - y
            g0 += d * x0
            g1 += d * x1
            g2 += d * x2
        w[0] -= lr * g0 / n
        w[1] -= lr * g1 / n
        w[2] -= lr * g2 / n
    return w


def quantile(vals, q):
    """经验分位数(最近秩,足够教学精度)。"""
    xs = sorted(vals)
    idx = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[idx]


def calibrate_thresholds(train):
    """阈值校准(全部在历史池上做,不接触测试池):
    公共阈值=全体 s 的 80 分位;组别阈值=各组 s 的 80 分位。"""
    s_all = [r["s"] for r in train]
    s_a = [r["s"] for r in train if r["grp"] == "A"]
    s_b = [r["s"] for r in train if r["grp"] == "B"]
    return {"common": quantile(s_all, 1.0 - Q_TARGET),
            "A": quantile(s_a, 1.0 - Q_TARGET),
            "B": quantile(s_b, 1.0 - Q_TARGET)}


def evaluate(test, decide):
    """评估一个决策函数 decide(row)->bool:录取率(总体/分组)、准确率、
    分组录取者合格率(P(qual|hire,g))、影响比率(B 率/A 率)。"""
    n = len(test)
    hire_a = hire_b = qual_hire_a = qual_hire_b = 0.0
    n_a = n_b = correct = 0.0
    for r in test:
        h = decide(r)
        if r["grp"] == "A":
            n_a += 1
            if h:
                hire_a += 1
                qual_hire_a += 1.0 if r["qual"] else 0.0
        else:
            n_b += 1
            if h:
                hire_b += 1
                qual_hire_b += 1.0 if r["qual"] else 0.0
        if h == r["qual"]:
            correct += 1
    rate_a = hire_a / n_a
    rate_b = hire_b / n_b
    return {"rate": (hire_a + hire_b) / n,
            "rate_a": rate_a, "rate_b": rate_b,
            "gap": abs(rate_a - rate_b),
            "impact": (rate_b / rate_a) if rate_a > 0 else float("inf"),
            "acc": correct / n,
            "qh_a": (qual_hire_a / hire_a) if hire_a else float("nan"),
            "qh_b": (qual_hire_b / hire_b) if hire_b else float("nan")}


def main():
    rng = random.Random(SEED)
    train = gen_pool(rng, N_TRAIN)
    test = gen_pool(rng, N_TEST)

    # ---- 历史标签:偏爱的规则 ----
    hist_scores = [r["s"] + W_PROXY * r["p"] for r in train]
    tau_h = quantile(hist_scores, 1.0 - Q_TARGET)
    for r, sc in zip(train, hist_scores):
        r["hist_hire"] = sc >= tau_h
    hist = evaluate(train, lambda r: r["hist_hire"])

    # ---- 三种筛选器 ----
    w = fit_logistic(train)                      # ① 朴素:历史标签逻辑回归
    th = calibrate_thresholds(train)             # ②/③ 的阈值
    screeners = {
        "① 朴素(历史标签,s+p)": evaluate(
            test, lambda r: sigmoid(w[0] + w[1] * r["s"] + w[2] * r["p"]) >= 0.5),
        "② 去代理+公共阈值": evaluate(
            test, lambda r: r["s"] >= th["common"]),
        "③ 去代理+组别校准(均等式)": evaluate(
            test, lambda r: r["s"] >= th[r["grp"]]),
    }

    # ---- 报告 ----
    print("=" * 88)
    print(f"算法招聘的公平陷阱:能力同分布,信号偏移 μ={MU},代理基率 "
          f"A {BASE_PA:.2f}/B {BASE_PB:.2f},目标录取率 {Q_TARGET:.0%}")
    print(f"历史池 {N_TRAIN},测试池 {N_TEST}(seed={SEED});"
          f"历史规则:s + {W_PROXY}·p ≥ τ_H={tau_h:.3f}")
    print("=" * 88)
    print(f"{'筛选器':<24} {'总率':>6} {'A率':>6} {'B率':>6} {'组间差':>7} "
          f"{'影响比':>6} {'准确率':>7} {'A录取合格':>9} {'B录取合格':>9}")
    print(f"{'(历史标签本身)':<24} {hist['rate']:>6.3f} {hist['rate_a']:>6.3f} "
          f"{hist['rate_b']:>6.3f} {hist['gap']:>7.3f} {hist['impact']:>6.2f} "
          f"{'—':>7} {'—':>9} {'—':>9}")
    for name, m in screeners.items():
        print(f"{name:<24} {m['rate']:>6.3f} {m['rate_a']:>6.3f} {m['rate_b']:>6.3f} "
              f"{m['gap']:>7.3f} {m['impact']:>6.2f} {m['acc']:>7.3f} "
              f"{m['qh_a']:>9.3f} {m['qh_b']:>9.3f}")

    naive, common, parity = (screeners[k] for k in screeners)
    print()
    print("读数:")
    print(f"  · 学到的权重 w_s={w[1]:.2f}, w_p={w[2]:.2f}(比值 {w[2]/w[1]:.2f})——"
          f"逻辑回归把历史对代理变量的偏爱学成了『客观规律』")
    print("  · ①组间录取率差最大:历史标签的系统性偏移被模型复制,还穿上了算法外衣")
    print("  · ②删掉代理变量后差收窄但未消除(信号偏移 μ 仍在);此时 B 组录取者")
    print("    合格率反而更高——他们翻越的有效门槛更高,『率』与『质』的图景相反")
    print("  · ③组别校准把录取率差抹平,准确率几乎不动——本设定里修正近乎免费;")
    print("    文献的不可兼得定理在『基础率不同』时才咬人(见文末练习注)")
    print("  · 公平不是加 buff,是选边:每个筛查器都必须声明自己站哪种标准")

    # ---- 自验证断言 ----
    # A0 能力同分布(前提自检)
    th_a = [r["theta"] for r in test if r["grp"] == "A"]
    th_b = [r["theta"] for r in test if r["grp"] == "B"]
    se = math.sqrt(1.0 / len(th_a) + 1.0 / len(th_b))
    assert abs(sum(th_a) / len(th_a) - sum(th_b) / len(th_b)) < 4 * se, "两组能力均值应无差异"
    for grp in ("A", "B"):
        qr = sum(1 for r in test if r["grp"] == grp and r["qual"]) / \
             sum(1 for r in test if r["grp"] == grp)
        assert abs(qr - Q_TARGET) < 0.01, f"{grp} 组合格率应≈20%"

    # A1 历史标签本身就带偏(伤害在标签里,不在模型里)
    assert hist["gap"] >= 0.10, "历史录用应有系统性组间差"

    # A2 朴素筛选器确实依赖代理变量(权重比>0.5)
    assert w[1] > 0 and w[2] > 0 and w[2] / w[1] > 0.5, "逻辑回归应学到对 p 的依赖"

    # A3 朴素筛选器产生组间录取率差;影响比率低于文献常用的 4/5 对照线
    assert naive["gap"] >= 0.10, "朴素筛选器应产生显著组间录取率差"
    assert naive["impact"] < 0.8, "朴素筛选器影响比率应低于 4/5 对照线(通说经验线)"

    # A4 修正后差异单调收窄:①>②>③
    assert naive["gap"] - common["gap"] >= 0.04, "去代理应显著收窄录取率差"
    assert common["gap"] - parity["gap"] >= 0.03, "组别校准应进一步收窄录取率差"
    assert parity["gap"] <= 0.02, "组别校准后录取率差应≈0"

    # A5 整体准确率损失有限(fairness-accuracy 权衡的教学断言)
    assert abs(common["acc"] - naive["acc"]) <= 0.03, "去代理的准确率损失应有限"
    assert abs(parity["acc"] - naive["acc"]) <= 0.03, "组别校准的准确率损失应有限"

    # A6 反直觉:公共阈值下 B 组录取者合格率更高(有效门槛更高)
    assert common["qh_b"] - common["qh_a"] >= 0.05, \
        "公共阈值下 B 组录取者合格率应显著更高(反直觉对照)"

    # A7 组别校准抹平录取率的同时也抹平了录取者合格率的组间差
    assert abs(parity["qh_b"] - parity["qh_a"]) <= 0.02, \
        "组别校准后录取者合格率组间差应≈0"

    # A8 三种筛查器的整体录取率都贴近目标(可比性前提)
    for name, m in screeners.items():
        assert abs(m["rate"] - Q_TARGET) <= 0.02, f"{name}: 总录取率应≈目标"

    print("\n✓ 自验证通过:历史标签自带偏(差 {:.3f})| 朴素筛选器复制偏移"
          "(组间差 {:.3f},影响比 {:.2f})| 去代理收窄至 {:.3f} | 组别校准至 {:.3f} "
          "| 准确率 {:.3f}→{:.3f}→{:.3f}(损失<3pp) | 公共阈值下 B 录取者合格率"
          "反而更高({:.3f} vs {:.3f})".format(
              hist["gap"], naive["gap"], naive["impact"], common["gap"],
              parity["gap"], naive["acc"], common["acc"], parity["acc"],
              common["qh_b"], common["qh_a"]))
    print("\n练习注:把两组能力分布改成不同(如 B 组 θ~N(0.2,1) 但合格线不变),"
          "重跑后观察③——录取率均等与『录取者合格率均等』开始冲突:"
          "这就是 Kleinberg/Chouldechova 不可兼得定理咬人的地方。")


if __name__ == "__main__":
    main()
