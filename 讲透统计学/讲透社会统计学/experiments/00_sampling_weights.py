# -*- coding: utf-8 -*-
"""SRS vs 分层抽样的方差对比 + 事后加权对无应答偏差的校正模拟。

00 章 §六(反直觉:低应答率≠偏差)与 02 章 §一(代表性语法)、04 章走廊 2 配套实验。纯标准库。

设定: 总体=家庭年收入 y(万元),两层:城市(W=0.40, μ=8.0, σ=3.0)/乡村(W=0.60, μ=4.0, σ=1.5)。
     总体均值 μ=5.6。无限总体模型(不做有限总体校正),下列公式精确成立:
       Var(ȳ_SRS)  = S²/n,  S² = Σ_h W_h·(σ_h² + (μ_h−μ)²)   ——含层间方差
       Var(ȳ_分层) = Σ_h W_h·σ_h²/n(比例分配)               ——层间方差被除掉
       分层增益 = Σ_h W_h·(μ_h−μ)²/n =「白拿的精度」
对照: Part1  SRS vs 分层(同样本量 n=200)——抽样设计如何白送方差
      Part2  无应答三场景(同样低应答率量级,三种命运):
       A 应答率 54% 与一切无关(MCAR)      → 低应答率,偏差≈0(应答率高低≠偏差大小)
       B 应答率与层相关(城 30%/乡 70%)    → 未加权均值偏低;按 W_h 事后加权可校正
       C 应答率与收入直接相关(MNAR,富人不答)→ 事后加权只救回一半——加权的语法边界

跑法: python experiments/00_sampling_weights.py
"""

import random

W1, MU1, SD1 = 0.40, 8.0, 3.0      # 城市层
W2, MU2, SD2 = 0.60, 4.0, 1.5      # 乡村层
MU = W1 * MU1 + W2 * MU2           # 总体均值 = 5.6
S2 = W1 * (SD1 ** 2 + (MU1 - MU) ** 2) + W2 * (SD2 ** 2 + (MU2 - MU) ** 2)  # 总体方差
WITHIN = W1 * SD1 ** 2 + W2 * SD2 ** 2                                        # 层内加权方差
BETWEEN = S2 - WITHIN                                # 层间方差 = 分层能除掉的部分


def draw(rng, h):
    """从第 h 层抽一个收入。h=0 城市,h=1 乡村。"""
    return rng.gauss(MU1, SD1) if h == 0 else rng.gauss(MU2, SD2)


# ---------- Part 1:SRS vs 分层抽样(比例分配,同样本量) ----------
def variance_faceoff(n=200, reps=1500, seed=20260907):
    rng = random.Random(seed)
    n1, n2 = round(n * W1), round(n * W2)
    srs, strat = [], []
    for _ in range(reps):
        # SRS:全池随机抽——每个入样者先掷层籍再掷收入(收入混合分布)
        srs.append(sum(draw(rng, 0 if rng.random() < W1 else 1) for _ in range(n)) / n)
        # 分层:城 n1 乡 n2 层内独立抽,层均值按已知 W_h 加权合成
        m1 = sum(draw(rng, 0) for _ in range(n1)) / n1
        m2 = sum(draw(rng, 1) for _ in range(n2)) / n2
        strat.append(W1 * m1 + W2 * m2)

    def var(xs):
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs) / len(xs)

    return var(srs), var(strat)


# ---------- Part 2:无应答三场景(调查模拟) ----------
def survey_once(rng, n0, resp):
    """邀请 n0 人(城市 round(W1·n0),其余乡村);y 应答与否由规则 resp(h,y) 决定。
    返回 (未加权均值, 事后分层加权均值, 应答率)。事后加权=按真 W_h 重新配权(人口结构已知)。"""
    n1 = round(n0 * W1)
    sum_all, cnt_all = 0.0, 0
    sums, cnts = [0.0, 0.0], [0, 0]
    for h, nh in ((0, n1), (1, n0 - n1)):
        for _ in range(nh):
            y = draw(rng, h)
            if rng.random() < resp(h, y):
                sum_all += y
                cnt_all += 1
                sums[h] += y
                cnts[h] += 1
    unw = sum_all / cnt_all
    pos = W1 * (sums[0] / cnts[0]) + W2 * (sums[1] / cnts[1])
    return unw, pos, cnt_all / n0


def run_scenarios(n0=3000, reps=250, seed=20260907):
    rng = random.Random(seed)
    rules = {
        "A 均匀54% ": lambda h, y: 0.54,                       # MCAR:应答与一切无关
        "B 城乡差异": lambda h, y: 0.30 if h == 0 else 0.70,   # 与层相关:加权可校正
        "C 富人不答": lambda h, y: max(0.05, 0.80 - 0.04 * y),  # 与收入直接相关:MNAR
    }
    out = {}
    for label, rule in rules.items():
        us, ps, rs = [], [], []
        for _ in range(reps):
            u, p, r = survey_once(rng, n0, rule)
            us.append(u)
            ps.append(p)
            rs.append(r)
        mean = lambda xs: sum(xs) / len(xs)
        out[label.strip()] = (mean(us) - MU, mean(ps) - MU, mean(rs))
    return out


def main():
    print("=" * 68)
    print(f"社会统计实验:抽样设计 × 无应答 × 加权  (总体 μ={MU}, S²={S2:.2f})")
    print("=" * 68)

    # ---------- Part 1 ----------
    n = 200
    v_srs, v_str = variance_faceoff(n=n)
    t_srs, t_str = S2 / n, WITHIN / n
    print(f"[Part1] SRS vs 分层(n={n}, 1500 次重复的均值方差)")
    print(f"    SRS   实测 {v_srs:.4f}  vs 理论 {t_srs:.4f}")
    print(f"    分层  实测 {v_str:.4f}  vs 理论 {t_str:.4f}")
    print(f"    设计效应 deff = {v_srs / v_str:.2f}(理论 {t_srs / t_str:.2f});"
          f"分层白拿的精度 = 层间方差/n = {BETWEEN / n:.4f}")
    print()

    # ---------- Part 2 ----------
    print("[Part2] 无应答三场景(每场 3000 人 × 250 次重复,报告对 μ 的偏差)")
    res = run_scenarios()
    for label, (bu, bw, r) in res.items():
        print(f"    {label}  应答率≈{r:.2f}  未加权偏差 {bu:+.3f}   事后加权偏差 {bw:+.3f}")

    print()
    print("读数:")
    print("  · 分层把层间方差整块除掉——同样的 n,方差打了对折以上:抽样设计先于样本量。")
    print("  · A 场景:应答率只有 54%,但应答机制与收入无关(MCAR),样本仍是总体的随机切片,")
    print("    偏差≈0——「低应答率」本身不是偏差的预测器(00 章 §六反直觉的实测版)。")
    print("  · B 场景:城市(富人层)少答→未加权均值被拉低 0.7 万元;人口结构已知时,")
    print("    事后分层加权几乎完全校正——权数是拿已知换未知。")
    print("  · C 场景:应答直接依赖收入本身(MNAR),同层的富人不答——分层权数只救回一半,")
    print("    剩下的偏差不可观测也不可加权修复:加权的语法边界(需敏感性分析/工具变量)。")

    # ---------- 自验证断言 ----------
    assert v_str < v_srs, "分层(比例分配)方差必须小于 SRS(本总体层均值差异大)"
    assert abs(v_srs - t_srs) < t_srs * 0.15, "SRS 实测方差应贴理论值 S²/n"
    assert abs(v_srs / v_str - t_srs / t_str) < 0.35, "实测设计效应应贴理论 deff"
    a_u, a_w, _ = res["A 均匀54%"]
    b_u, b_w, _ = res["B 城乡差异"]
    c_u, c_w, _ = res["C 富人不答"]
    assert abs(a_u) < 0.06 and abs(a_w) < 0.06, "MCAR 无应答:低应答率≠偏差"
    assert b_u < -0.45, "城乡差异应答:未加权均值应显著偏低(城市富、应答少)"
    assert abs(b_w) < 0.08, "事后分层加权应基本校正 MAR 偏差"
    assert c_u < -0.40, "MNAR:未加权应显著偏低"
    assert c_w < -0.20, "MNAR:事后加权救不干净——残余偏差是加权方法的边界"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
