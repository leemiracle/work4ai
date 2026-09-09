# -*- coding: utf-8 -*-
"""布卢姆「两西格玛问题」教学版:传统课堂 / 一对一辅导 / 掌握学习 三组仿真。

00-体系结构.md(反直觉 3、美之时刻引)、03-可构造与结构.md(结构引擎 2:
标准参照)与 04-教育学原理转代码.md(走廊 1/2)的配套实验。纯标准库(random+math)。

布卢姆 1984《两西格玛问题》(The 2 Sigma Problem, Educational Researcher)
的通说数字(文献通说陈述):
  · 一对一辅导组均值比传统课堂组高约 2 个标准差(平均被辅导学生位于
    课堂组的第 98 百分位);
  · 掌握学习(形成性测验+矫正循环)约收回差距的一半(1σ,第 84 百分位);
  · 布卢姆把「找到与一对一辅导同样有效的大班组教学法」命名为两西格玛问题。

模型(成绩以课堂组标准差为单位;z 分数制):
  初始差异 pre ~ N(0,1);组内成绩 post = λ_g·pre + Δ_g + ε,ε ~ N(0, s_g²)。
  每组的两个教学法参数:
    Δ_g  均值移位(教学法效应——把学生带多远)
    λ_g  初始差异的传导系数(个体化程度——拉平还是放大起点差异;λ 越小方差越收敛)
  辅导与课堂的结构差异不来自知识量,来自反馈结构(即时诊断/即时矫正/自定进度),
  参数化如下:

  ① 师生比 r 的注意力稀释(走廊 1 的规模化曲线):
       a(r) = r_half / (r_half + r − 1)        a(1)=1, r→∞ 时 a→0(r_half=4)
       Δ(r) = Δ_max · a(r)                     均值效应随稀释双曲衰减
       λ(r) = 0.70 − 0.35·a(r);s(r)=sqrt(Var(r)−λ(r)²),
       Var(r) = 1 − (1−V_min)·a(r)             方差同步收敛(V_min=0.425)
     读数:a(5)=0.5 → 1:5 小组 ≈ +1.0σ、sd≈0.84——恰是掌握学习组的落点:
     掌握学习 ≈「用矫正材料把一个教师放大成 1:5 反馈结构」的结构解读。

  ② 掌握学习的循环动力学(走廊 2 的收敛速度):
       单元循环 k 次,均值增益 Δ_m(k) = Δ_∞·(1−e^(−β_m k))   (β_m=0.75, Δ_∞=1.06)
       方差收敛 Var_m(k) 沿更慢速率 β_v=0.5/0.4 的指数逼近
     读数:均值收敛快于方差收敛(f_mean(k) > f_var(k))——
     「补差比提优贵」的最小机制版;k=4 时 Δ_m≈1.01σ, sd≈0.85。

断言(自验):
  1) 辅导组均值高出传统组约 2σ(d ∈ [1.85, 2.15];理论百分位 Φ(2.0)≈97.7%≈98th);
  2) 掌握学习收回差距一半左右(d_m/d_t ∈ [0.42, 0.58],d_m≈1σ→Φ(1.0)≈84th),
     且方差收敛更慢(sd_tut < sd_mast < sd_trad;f_var(k) < f_mean(k) 对 k=1..6);
  3) 效应对师生比敏感:效应随 r 单调下降,1:5 约折半,1:30 趋近课堂水平
     ——两西格玛难以规模化的结构成因:守住 +2σ 需要把教师容量放大 30 倍。

跑法: python3 -u experiments/bloom_two_sigma.py
"""

import math
import random

N_GROUP = 4000          # 每组样本量
N_RATIO = 2000          # 师生比扫描每组样本量
SEED = 20260907

# ---- 课堂基线组(对照):Δ=0, sd=1(单位定义) ----
LAM_TRAD, S_TRAD = 0.70, 0.714          # Var = 0.49+0.51 ≈ 1.00

# ---- 辅导/师生比参数 ----
R_HALF = 4.0            # 注意力半饱和:稀释速度的结构参数
DELTA_MAX = 2.0         # 1:1 饱和效应(布卢姆通说 +2σ)
V_MIN = 0.425           # 1:1 的成绩方差(sd≈0.652)

# ---- 掌握学习循环参数 ----
BETA_MEAN, DELTA_INF = 0.75, 1.06       # 均值增益渐近线(→≈1σ 略高)
K_MAIN = 4              # 主对照取 k=4 个单元循环


def phi(z):
    """标准正态分布函数(math.erf 实现)。"""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def attention(r):
    """师生比 r 的注意力份额 a(r):每个学生分得的反馈容量(1:1 饱和)。"""
    return R_HALF / (R_HALF + r - 1.0)


def effect(r):
    """均值效应 Δ(r):教学法效应随师生比的双曲稀释。"""
    return DELTA_MAX * attention(r)


def group_params(r):
    """师生比 r 的 (λ, Δ, s):均值移位+初始差异传导+残差。"""
    a = attention(r)
    var = 1.0 - (1.0 - V_MIN) * a
    lam = 0.70 - 0.35 * a
    return lam, effect(r), math.sqrt(max(var - lam * lam, 0.0))


def mastery_params(k):
    """掌握学习 k 次反馈-矫正循环的 (λ, Δ, s):均值收敛快(β=0.75),
    方差收敛慢(λ 的衰减 β=0.5、残差的衰减 β=0.4)——双速度是断言 2 的机制。"""
    delta = DELTA_INF * (1.0 - math.exp(-BETA_MEAN * k))
    lam = 0.50 + 0.20 * math.exp(-0.50 * k)      # 0.70 → 0.50,慢
    s = 0.65 + 0.064 * math.exp(-0.40 * k)       # 0.714 → 0.65,更慢
    return lam, delta, s


def simulate(lam, delta, s, n, seed):
    """生成一组成绩:post = λ·pre + Δ + ε(独立 RNG,按组分流 seed 可复现)。"""
    rng = random.Random(seed)
    return [lam * rng.gauss(0.0, 1.0) + delta + rng.gauss(0.0, s)
            for _ in range(n)]


def mean_std(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var)


def main():
    print("=" * 84)
    print("布卢姆两西格玛问题:传统课堂 vs 一对一辅导 vs 掌握学习(单位=课堂组 sd)")
    print(f"参数:n={N_GROUP}/组,r_half={R_HALF},Δ_max={DELTA_MAX},"
          f"掌握学习 k={K_MAIN}")
    print("=" * 84)

    # ---- 三组主对照 ----
    trad = simulate(LAM_TRAD, 0.0, S_TRAD, N_GROUP, SEED)
    lam_t, d_t, s_t = group_params(1)
    tut = simulate(lam_t, d_t, s_t, N_GROUP, SEED + 1)
    lam_m, d_m, s_m = mastery_params(K_MAIN)
    mast = simulate(lam_m, d_m, s_m, N_GROUP, SEED + 2)

    m_tr, sd_tr = mean_std(trad)
    m_tu, sd_tu = mean_std(tut)
    m_ma, sd_ma = mean_std(mast)
    dd_t = (m_tu - m_tr) / sd_tr                      # 效应量 d(课堂 sd 为单位)
    dd_m = (m_ma - m_tr) / sd_tr

    print(f"{'组':<6} {'均值':>7} {'sd':>6} {'效应d':>7} {'均值在课堂组的百分位':>10}")
    print(f"{'传统课堂':<6} {m_tr:>7.3f} {sd_tr:>6.3f} {'—':>7} {'—':>10}")
    print(f"{'一对一辅导':<5} {m_tu:>7.3f} {sd_tu:>6.3f} {dd_t:>7.3f} {phi(dd_t):>10.4f}")
    print(f"{'掌握学习':<6} {m_ma:>7.3f} {sd_ma:>6.3f} {dd_m:>7.3f} {phi(dd_m):>10.4f}")
    print()
    print("读数:")
    print("  · 辅导组效应 d≈2:平均被辅导学生位于课堂组第 98 百分位(布卢姆 1984 通说)")
    print("  · 掌握学习 d≈1:收回两西格玛差距的一半(通说 84th 百分位)")
    print("    ——靠的不是教师更多,而是测验→诊断→矫正→复测的循环(走廊 2)")
    print("  · sd:辅导 0.65 < 掌握 0.85 < 课堂 1.00:个体化程度=方差压缩程度")

    # ---- 掌握学习的收敛双速度(断言 2 后半) ----
    print(f"\n掌握学习循环扫描:k=1..6(Δ_∞={DELTA_INF},β_mean={BETA_MEAN})"
          f"  [f=已实现的渐近收敛比例]")
    print(f"{'k':>2} {'Δ_m(k)':>7} {'f_mean':>8} {'Var_m(k)':>9} {'f_var':>8}")
    conv = []
    var_inf = 0.50 ** 2 + 0.65 ** 2                   # 渐近方差(≈0.6725)
    for k in range(1, 7):
        lam, delta, s = mastery_params(k)
        var = lam * lam + s * s
        f_mean = delta / DELTA_INF
        f_var = (1.0 - var) / (1.0 - var_inf)         # 方差压缩的实现比例
        conv.append((k, f_mean, f_var))
        print(f"{k:>2} {delta:>7.3f} {f_mean:>8.3f} {var:>9.3f} {f_var:>8.3f}")
    print("  读数:每一行 f_mean > f_var——均值先到,方差后到:")
    print("        全员「平均达标」快,全员「一起达标」慢(补差比提优贵)。")

    # ---- 师生比扫描(断言 3) ----
    print("\n师生比扫描:效应 Δ(r)=Δ_max·a(r) 与经验仿真对照"
          f"(n={N_RATIO}/组)")
    print(f"{'师生比':>6} {'a(r)':>6} {'理论Δ':>7} {'仿真Δ':>7} {'sd':>6}")
    rows = []
    for r in (1, 2, 5, 10, 30):
        lam, delta, s = group_params(r)
        scores = simulate(lam, delta, s, N_RATIO, SEED + 100 + r)
        m_r, sd_r = mean_std(scores)
        emp = (m_r - m_tr) / sd_tr
        rows.append((r, attention(r), delta, emp, sd_r))
        print(f"{'1:%d' % r:>6} {attention(r):>6.3f} {delta:>7.3f} "
              f"{emp:>7.3f} {sd_r:>6.3f}")
    print("  读数:1:5 效应折半(≈掌握学习),1:30 只剩 +0.24σ——")
    print("        反馈结构决定效应上限:守住 +2σ 需把教师容量放大 30 倍,")
    print("        这就是两西格玛「难以规模化」的成本结构(04 章落点 2 的审计点)。")

    # ================= 断言(自验)=================
    # 断言 1:辅导组均值高出传统组约 2σ;理论百分位 ≈ 98th(布卢姆通说)
    assert 1.85 <= dd_t <= 2.15, f"辅导效应 d={dd_t:.3f} 应≈2σ"
    assert abs(phi(2.0) - 0.977) < 0.005, "Φ(2.0) 应≈97.7%(第 98 百分位)"
    assert abs(phi(dd_t) - 0.977) < 0.02, "经验效应换算百分位应≈98th"

    # 断言 2:掌握学习收回差距一半左右;方差收敛更慢(组间+组内双证据)
    assert 0.8 <= dd_m <= 1.2, f"掌握学习效应 d={dd_m:.3f} 应≈1σ"
    assert 0.42 <= dd_m / dd_t <= 0.58, \
        f"收回比例 d_m/d_t={dd_m/dd_t:.3f} 应≈一半"
    assert abs(phi(1.0) - 0.841) < 0.005, "Φ(1.0) 应≈84.1%(第 84 百分位)"
    assert sd_tu < sd_ma - 0.10 < sd_tr, \
        "方差收敛更慢:sd(辅导) < sd(掌握) < sd(课堂),且差距明显"
    for k, f_mean, f_var in conv:
        assert f_var < f_mean, f"k={k}: 方差收敛比例({f_var:.3f})应慢于均值({f_mean:.3f})"

    # 断言 3:效应大小对师生比敏感(单调下降;1:5 折半;大班趋近课堂)
    for i in range(len(rows) - 1):
        assert rows[i + 1][2] < rows[i][2], "效应应随师生比单调下降"
        assert rows[i + 1][3] < rows[i][3], "仿真效应应随师生比单调下降"
    assert abs(rows[0][2] - 2.0) < 1e-9, "1:1 应为饱和效应 +2σ"
    assert abs(rows[2][2] - 1.0) < 0.05, "1:5 效应应≈+1σ(≈掌握学习落点)"
    assert rows[-1][2] < 0.30, "1:30 效应应衰减到课堂水平附近(<0.3σ)"
    # 结构回声:掌握学习(k=4)≈ 1:5 小组曲线的经验落点(参数化的设计意图)
    lam_m5 = group_params(5)
    assert abs(mastery_params(K_MAIN)[1] - lam_m5[1]) < 0.1, \
        "掌握学习(k=4)应落在 1:5 曲线附近(结构解读:矫正材料≈放大教师到 1:5)"

    # 成本结构:守住 +2σ 的教师容量
    class_size = 30
    tutors_needed = class_size * 1                     # 1:1 需 30 位辅导者
    print(f"\n规模化成本:一个 {class_size} 人班级全部 1:1 辅导,需约 "
          f"{tutors_needed} 位辅导者(教师容量 ×{tutors_needed})——"
          f"而 1:30 恰是课堂本身。")

    print("\n✓ 自验证通过:辅导≈+2σ(98th)| 掌握学习≈+1σ 且收回差距一半、"
          "方差收敛慢于均值(sd:0.65<0.85<1.00;f_var<f_mean 对 k=1..6)| "
          "效应随师生比单调衰减(1:5 折半、1:30<0.3σ)| 规模化成本=×30 教师容量")


if __name__ == "__main__":
    main()
