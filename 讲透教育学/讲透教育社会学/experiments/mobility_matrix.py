# -*- coding: utf-8 -*-
"""教育流动表模拟:父代教育 × 子代教育转移矩阵。

00-体系结构.md(反直觉:EMI/科尔曼反转/布东悖论)、03-可构造与结构.md(流动表
schema、相对率不变性、方差分解)与 04-教育社会学转代码.md(走廊 1/2/3)的
配套实验。纯标准库(random/math)。

等级:0=初中及以下(9 年),1=高中(12 年),2=大学及以上(16.5 年)。

三幕:
  幕一 继承模式 vs 机会模式:
      继承矩阵(对角 0.97)→ 转移矩阵对角占优,且代际弹性(子代年限对父代
      年限的 OLS 斜率)→1;机会矩阵(各行相同,与出身无关)→ 弹性≈0。
  幕二 扩张 vs 拉平(EMI 假说的结构表达;序贯 logit,Mare 1980 的最小版):
      子代教育 = 两道关口(超越高中?→ 入大学?),每关通过率
          P(过关|出身 x) = σ(α_t + β·x)
      α = 总量可及性(教育扩张拉它),β = 出身优势(机会拉平动它)。
      数学事实:高出身(x=2)对低出身(x=0)的过关对数几率差 = 2β,与 α 无关。
      断言:扩张(α↑)使边际分布大幅右移,而两关的相对流动率(log OR)不动;
      拉平(β↓)才动 log OR——机会拉平需要转移概率改变,不只是总量扩张。
  幕三 学校效应方差压缩 → 家庭背景占比上升(残余不平等的再集中):
      子代成绩 = 0.6·家庭背景 + 0.8·学校质量 + 个体噪声;
      学校质量均值随出身分隔(0.3·x)再加异质方差 σ_q。
      断言:σ_q 压缩 → 总成绩差异下降,且家庭背景对子代教育等级的解释占比
      (R²)上升——"学校更平等"与"家庭更有解释力"同时成立。

跑法: python3 -u experiments/mobility_matrix.py
"""

import math
import random

LEVELS = ("初中及以下", "高中", "大学及以上")
YEARS = (9.0, 12.0, 16.5)


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def logit(p):
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    return math.log(p / (1.0 - p))


def ols_slope(xs, ys):
    """OLS 斜率 cov(x,y)/var(x)。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    var = sum((x - mx) ** 2 for x in xs) / n
    return cov / var


# ============================ 幕一:继承模式 vs 机会模式 ============================

P_INHERIT = [[0.97, 0.015, 0.015],
             [0.015, 0.97, 0.015],
             [0.015, 0.015, 0.97]]
P_OPEN = [[0.34, 0.33, 0.33]] * 3          # 行相同:子代等级与出身无关


def sample_matrix(P, n, seed):
    """父代均匀取三等级,子代按行转移概率落级;返回样本与经验转移矩阵。"""
    rng = random.Random(seed)
    fathers, children = [], []
    F = [[0] * 3 for _ in range(3)]
    for _ in range(n):
        i = rng.randrange(3)
        r, acc = rng.random(), 0.0
        j = 2
        for k in range(3):
            acc += P[i][k]
            if r < acc:
                j = k
                break
        F[i][j] += 1
        fathers.append(YEARS[i])
        children.append(YEARS[j])
    Fp = [[F[i][j] / sum(F[i]) for j in range(3)] for i in range(3)]
    return fathers, children, Fp


def act1():
    print("=" * 84)
    print("幕一 继承模式 vs 机会模式(转移矩阵的对角占优与代际弹性)")
    print("=" * 84)
    n = 200_000
    results = {}
    for name, P in (("继承", P_INHERIT), ("机会", P_OPEN)):
        fat, chi, Fp = sample_matrix(P, n, seed=20260901 + len(results))
        slope = ols_slope(fat, chi)
        results[name] = (Fp, slope)
        print(f"\n{name}模式(理论矩阵行 = {P[0]}):")
        for i in range(3):
            print(f"  父代[{LEVELS[i]:<5}] → 子代: "
                  + " ".join(f"{Fp[i][j]:.3f}" for j in range(3)))
        print(f"  代际弹性(子代年限~父代年限 的 OLS 斜率) = {slope:.3f}")
    (Finh, slope_inh), (Fopen, slope_open) = results["继承"], results["机会"]
    print("\n读数:")
    print("  · 继承矩阵主对角 ≈0.97:出身几乎决定获得——『社会再生产』的矩阵长相")
    print("  · 机会矩阵三行相同:给定任何出身,子代分布一致——『打破器』满功率")
    print("  · 弹性 0.95 vs 0.00:同一个框架量出复制与开放的两个极端")

    # 断言 1:继承模式对角占优 + 代际弹性→1;机会模式弹性≈0
    for i in range(3):
        for j in range(3):
            if j != i:
                assert Finh[i][i] > Finh[i][j], f"继承模式行 {i} 未对角占优"
    assert slope_inh > 0.9, f"继承模式代际弹性应→1,实测 {slope_inh:.3f}"
    assert abs(slope_open) < 0.05, f"机会模式弹性应≈0,实测 {slope_open:.3f}"
    for i in range(3):                      # 机会模式:三行相同(出身无信息)
        for j in range(3):
            assert abs(Fopen[i][j] - P_OPEN[0][j]) < 0.01, "机会模式行应与出身无关"
    print(f"\n✓ 幕一断言通过:继承模式对角占优且弹性 {slope_inh:.3f}(→1);"
          f"机会模式弹性 {slope_open:+.3f}(≈0)")
    return results


# ==================== 幕二:扩张 vs 拉平(EMI 的结构表达) ====================

def run_cohort(a1, a2, b, n, seed):
    """序贯 logit 队列:两道关口,每关 σ(α_t + β·出身)。
    返回:3×3 流动表计数、各关口的 risk/pass 计数(按出身)。"""
    rng = random.Random(seed)
    counts = [[0] * 3 for _ in range(3)]
    pass1, risk1, pass2, risk2 = [0] * 3, [0] * 3, [0] * 3, [0] * 3
    for _ in range(n):
        x = rng.randrange(3)
        risk1[x] += 1
        if rng.random() < sigmoid(a1 + b * x):
            pass1[x] += 1
            risk2[x] += 1
            if rng.random() < sigmoid(a2 + b * x):
                pass2[x] += 1
                counts[x][2] += 1
            else:
                counts[x][1] += 1
        else:
            counts[x][0] += 1
    return counts, (risk1, pass1, risk2, pass2)


def rel_rates(risk1, pass1, risk2, pass2):
    """相对流动率:两道关口上,高出身(x=2)对低出身(x=0)的经验对数几率差。
    理论值 = 2β,与 α 无关——EMI 假说的代数核心。"""
    lor = []
    for risk, pss in ((risk1, pass1), (risk2, pass2)):
        p_hi = pss[2] / risk[2]
        p_lo = pss[0] / risk[0]
        lor.append(logit(p_hi) - logit(p_lo))
    return lor


def act2():
    print("\n" + "=" * 84)
    print("幕二 扩张 vs 拉平(序贯 logit:α=总量可及性,β=出身优势;EMI 结构表达)")
    print("=" * 84)
    n = 300_000
    BETA = 0.8
    scenarios = {
        "基准":   dict(a1=0.0, a2=-0.5, b=BETA),
        "扩张":   dict(a1=1.2, a2=0.9, b=BETA),      # 只拨 α:总量扩张
        "拉平":   dict(a1=1.2, a2=0.9, b=0.3),       # 拨 β:动转移概率
    }
    out = {}
    print(f"\n出生队列 n={n:,},出身三等级均匀;β(基准)={BETA}")
    print(f"{'情景':<4} {'α₁':>5} {'α₂':>5} {'β':>4} | "
          f"{'大学+占比':>8} | {'关口1 logOR':>10} {'关口2 logOR':>10} (理论 2β)")
    for k, (name, sc) in enumerate(scenarios.items()):
        counts, (risk1, pass1, risk2, pass2) = run_cohort(
            sc["a1"], sc["a2"], sc["b"], n, seed=20260910 + k)
        share2 = sum(counts[i][2] for i in range(3)) / n
        lor = rel_rates(risk1, pass1, risk2, pass2)
        out[name] = dict(sc=sc, share2=share2, lor=lor, counts=counts)
        print(f"{name:<4} {sc['a1']:>5.1f} {sc['a2']:>5.1f} {sc['b']:>4.1f} | "
              f"{share2:>8.3f} | {lor[0]:>10.3f} {lor[1]:>10.3f}   ({2 * sc['b']:.1f})")

    print("\n转移概率矩阵(行=父代出身,列=子代获得;行和=1):")
    for name in ("基准", "扩张", "拉平"):
        print(f"  [{name}]")
        for i in range(3):
            row = out[name]["counts"][i]
            tot = sum(row)
            print(f"    父代[{LEVELS[i]:<5}] → "
                  + " ".join(f"{row[j] / tot:.3f}" for j in range(3)))

    print("\n读数:")
    print("  · 基准→扩张:α 上拨,各出行右移(大学+占比 0.40→0.72),边际大幅右移;")
    print("    但两关 logOR 纹丝不动(≈1.6=2β)——相对流动率是边际重分配的守衡量")
    print("  · 扩张→拉平:α 不动只降 β,logOR 1.6→0.6——相对流动率才会动")
    print("  · EMI 结构表达:『教育增长了』(动 α/边际)≠『教育公平了』(动 β/转移);")
    print("    机会拉平需要转移概率改变,不只是总量扩张")

    # 断言 2:扩张右移边际但不动相对流动率;拉平必须靠 β
    assert out["扩张"]["share2"] - out["基准"]["share2"] > 0.15, \
        "扩张应使边际分布显著右移(大学+占比应大幅上升)"
    for t in (0, 1):
        assert abs(out["基准"]["lor"][t] - 2 * BETA) < 0.08, \
            f"基准关口{t + 1}:logOR 应≈2β={2 * BETA:.1f}"
        assert abs(out["扩张"]["lor"][t] - 2 * BETA) < 0.08, \
            f"扩张关口{t + 1}:扩张不应改变相对流动率(logOR 应仍≈2β)"
        assert out["拉平"]["lor"][t] < out["扩张"]["lor"][t] - 0.7, \
            f"拉平关口{t + 1}:降 β 应显著缩小 logOR"
    assert out["扩张"]["share2"] > 0.65 and out["基准"]["share2"] < 0.5, \
        "边际右移的量级应清晰可读"
    print(f"\n✓ 幕二断言通过:扩张使大学+占比 {out['基准']['share2']:.3f}→"
          f"{out['扩张']['share2']:.3f},而 logOR 基准/扩张均≈{2 * BETA:.1f};"
          f"拉平情景 logOR≈{2 * 0.3:.1f}——边际与转移是两个正交的旋钮")
    return out


# ============= 幕三:学校方差压缩 → 家庭背景占比上升(再集中) =============

def run_schools(sigma_q, n, seed):
    """子代成绩 = 0.6·x + 0.8·q + ε;q = 0.3·x + σ_q·ν(学校均值随出身分隔,
    σ_q 为校际异质方差)。等级 = 成绩按阈值 (-0.8, 0.9) 切三段。
    在线累加统计量,内存 O(1)。"""
    rng = random.Random(seed)
    # 累加器:n, Σx, Σl, Σx², Σl², Σxl, Σscore, Σscore², Σx·score
    s_ = [0.0] * 9
    for _ in range(n):
        x = rng.gauss(0.0, 1.0)                      # 家庭背景(标准化)
        q = 0.3 * x + sigma_q * rng.gauss(0.0, 1.0)  # 学校质量
        score = 0.6 * x + 0.8 * q + rng.gauss(0.0, 1.0)
        lev = 0 if score < -0.8 else (1 if score < 0.9 else 2)
        s_[0] += 1
        s_[1] += x
        s_[2] += lev
        s_[3] += x * x
        s_[4] += lev * lev
        s_[5] += x * lev
        s_[6] += score
        s_[7] += score * score
        s_[8] += x * score
    n_, sx, sl, sx2, sl2, sxl, ss, ss2, sxs = s_
    var_x = sx2 / n_ - (sx / n_) ** 2
    var_l = sl2 / n_ - (sl / n_) ** 2
    cov_xl = sxl / n_ - (sx / n_) * (sl / n_)
    var_s = ss2 / n_ - (ss / n_) ** 2
    cov_xs = sxs / n_ - (sx / n_) * (ss / n_)
    r2_level = (cov_xl ** 2) / (var_x * var_l)
    r2_score = (cov_xs ** 2) / (var_x * var_s)
    return dict(r2_level=r2_level, r2_score=r2_score, var_score=var_s)


def act3():
    print("\n" + "=" * 84)
    print("幕三 学校方差压缩 → 家庭背景占比上升(残余不平等的再集中)")
    print("=" * 84)
    n = 200_000
    print(f"\n成绩 = 0.6·家庭 + 0.8·学校 + ε;学校 = 0.3·家庭 + σ_q·ν;n={n:,}")
    print(f"{'情景':<12} {'σ_q':>5} {'总方差(成绩)':>10} "
          f"{'R²(等级)':>9} {'R²(成绩)':>9}")
    out = {}
    for k, (name, sq) in enumerate((("校际差异大", 1.2), ("校际差异压缩", 0.25))):
        res = run_schools(sq, n, seed=20260920 + k)
        out[name] = res
        print(f"{name:<12} {sq:>5.2f} {res['var_score']:>10.3f} "
              f"{res['r2_level']:>9.3f} {res['r2_score']:>9.3f}")
    A, B = out["校际差异大"], out["校际差异压缩"]
    print("\n读数:")
    print("  · σ_q 从 1.2 压到 0.25:成绩总方差下降(学校这台机器的随机差异被抹平)")
    print("  · 但家庭背景对子代教育等级的解释占比 R² 反而上升——分母变小了:")
    print("    残余的教育差异中,家庭背景的份额被再集中(科尔曼推论:00 章发现 2)")
    print("  · 政策语义:『学校更平等了』与『出身更有解释力了』可以同时成立")

    # 断言 3:压缩学校方差 → 总差异下降 + 家庭占比上升
    assert B["var_score"] < A["var_score"] - 0.2, "压缩 σ_q 应显著降低成绩总方差"
    assert B["r2_level"] > A["r2_level"] + 0.05, \
        f"学校方差压缩后家庭 R²(等级)应上升:{A['r2_level']:.3f} → {B['r2_level']:.3f}"
    assert B["r2_score"] > A["r2_score"] + 0.05, "成绩层面同理"
    print(f"\n✓ 幕三断言通过:总方差 {A['var_score']:.2f}→{B['var_score']:.2f} 下降,"
          f"家庭 R²(等级) {A['r2_level']:.3f}→{B['r2_level']:.3f} 上升"
          "——残余不平等的再集中")
    return out


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 继承模式:转移矩阵对角占优,代际弹性→1(再生产的矩阵长相)")
    print("  ② EMI 结构表达:扩张(α)右移边际但相对流动率(logOR)不变;")
    print("     拉平必须动 β(转移概率)——扩张≠公平")
    print("  ③ 学校方差压缩 → 总差异下降而家庭占比上升(残余不平等再集中)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
