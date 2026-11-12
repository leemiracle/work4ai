# -*- coding: utf-8 -*-
"""大众化与分层:特罗阶段论的模拟(00/04 章配套实验)。

主题呼应 04 章走廊 1-3:一个虚构高教系统的 60 年扩张——
  GER(t):毛入学率,logistic 连续曲线(约 6.5%→82%),15%/50% 为特罗阈值;
  分层:三层系统(研究型层 R/普通本科层 M/职业与社区层 V),容量按
        C_i(t)=a_i·N(t)^{e_i} 次线性增长(e_R<e_M:高声望层扩得慢),
        职业与社区层吸收残差(系统总能装下全部需求——"开放入学"由底层兜底);
  师资:F(t)=F_0·(N(t)/N_0)^{e_f},e_f<1(学术职位增长滞后于学生扩张);
        分层师资弹性 e_fR≈0.95(研究型受保护)vs e_fV≈0.65(大众层先透支)。

断言三律(高等教育学通说的结构化):
  A. 阶段转换是连续函数的阈值标记而非断崖(阈值=叙事构造):
     GER 单调、每阈值恰穿一次;阶段标签在穿越年阶跃,而系统的一切连续
     状态量(GER/各层份额/在校生)在穿越年的变化不超过该序列自身最大
     变化的 1.15 倍——断崖在标签里,不在系统里(与比较教育学家族
     pisa_decomposition.py 的"阈值-叙事"方法论互为呼应);
  B. 扩张伴随分层(分层虹吸):研究型层份额随扩张单调下降;扩张增量
     主要被低声望层吸收——全期增量中低层占比 > 其期初存量份额 + 8pp,
     增量中研究型占比 < 其期初存量份额 - 5pp
     (MMI/EMI 通说的结构化:扩张不消灭分层,分层吸收扩张);
  C. 学术职位增长滞后于学生扩张(学术职业的结构性压力):
     师生比末/初 ≥1.25×;学生增长倍数 > 教师增长倍数 ×1.35;
     且大众层师生比恶化幅度 > 研究型层 ×1.8(双重劳动力市场:
     内圈受保护,外围先透支)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值,不拟合任何真实高教系统;系统为虚构;
  2. 模拟证明「次线性容量增长 + 残差吸收 + 职位弹性<1 的简单机制
     足以生成三律」(机制充分性),不是任何真实系统的数量断言;
  3. 通说依据:特罗阶段论的启发式本义(特罗自己声明阈值非断裂)、
     教育扩张中的不平等存续(MMI/EMI)、学术劳动力市场的双重化
     与博士就业压力——均为综述级通说,未逐条核数;
  4. 敏感性分析:文末 Monte Carlo(80 次参数抖动)报告三律通过率
     ——换参数重跑=检验结论的结构刚性(04 章的正确用法)。

跑法: python experiments/massification_tier.py
"""

import math
import random
import sys

# ----------------------------- 世界参数(基准情形,虚构系统) -----------------------------
T = 60                      # 年数 t=0..59(约两代人的扩张史)
K_G, L_G, T0 = 0.10, 0.85, 25.0   # logistic:速率/上限/拐点年
POP = 1_000_000             # 适龄人口(恒定;人口波动另算,见文末纪律)
THR_ELITE, THR_UNIV = 0.15, 0.50  # 特罗阈值:精英/大众、大众/普及
SHARE_R0, SHARE_M0 = 0.20, 0.50   # 期初三层份额(研究型/普通本科;余为职业与社区层)
E_R, E_M = 0.55, 0.85       # 容量弹性:研究型扩得慢,普通本科次之
RATIO0 = 14.0               # 期初整体师生比 1:14(风格化)
E_F = 0.72                  # 整体师资弹性(<1:职位增长滞后)
E_FR, E_FV = 0.95, 0.65     # 分层师资弹性:研究型受保护/大众层先透支

STAGES = ["精英", "大众", "普及"]


# ----------------------------- 基础件:曲线、分层、师资 -----------------------------
def ger_curve(k=K_G, lim=L_G, t0=T0):
    """毛入学率 logistic 曲线(连续、单调、单拐)。"""
    return [lim / (1.0 + math.exp(-k * (t - t0))) for t in range(T)]


def stage_labels(ger):
    """特罗阶段标签:对连续曲线做阈值切分(唯一的离散化步骤)。"""
    out = []
    for g in ger:
        out.append(STAGES[0] if g < THR_ELITE else
                   (STAGES[1] if g < THR_UNIV else STAGES[2]))
    return out


def tier_capacities(N, n0, share_r0=SHARE_R0, share_m0=SHARE_M0,
                    e_r=E_R, e_m=E_M):
    """三层容量:C_i = share_i0·n0^{1-e_i}·N^{e_i}(过 (n0, share_i0·n0) 校准);
    职业与社区层 = 残差(扩张的兜底层)。"""
    aR = share_r0 * (n0 ** (1.0 - e_r))
    aM = share_m0 * (n0 ** (1.0 - e_m))
    cR = aR * (N ** e_r)
    cM = aM * (N ** e_m)
    return cR, cM, N - cR - cM


def crossing_year(ger, thr):
    """首次穿越阈值的年份(ger 单调 ⇒ 恰穿一次)。"""
    for t, g in enumerate(ger):
        if g >= thr:
            return t
    return None


def diffs(xs):
    return [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]


# ----------------------------- 断言 A:阈值是标记不是断崖 -----------------------------
def law_a(ger, series, labels):
    """series: dict 名→序列(GER 及各状态量)。返回读数并断言。"""
    t15, t50 = crossing_year(ger, THR_ELITE), crossing_year(ger, THR_UNIV)
    assert t15 is not None and t50 is not None and t15 < t50
    # A1 单调 + 恰穿一次
    assert all(d > 0.0 for d in diffs(ger)), "A1失败:GER 非单调"
    for thr, tc in ((THR_ELITE, t15), (THR_UNIV, t50)):
        n_cross = sum(1 for i in range(T - 1) if ger[i] < thr <= ger[i + 1])
        assert n_cross == 1, f"A1失败:阈值 {thr:.0%} 穿越 {n_cross} 次"
    # A2 断崖在标签里:标签阶跃,状态量不阶跃(≤自身其余年份最大变化的 1.15 倍)
    for tc in (t15, t50):
        assert labels[tc] != labels[tc - 1], "A2失败:标签未阶跃"
        for name, xs in series.items():
            d = diffs(xs)
            jump = abs(d[tc - 1])
            others = max(abs(v) for i, v in enumerate(d) if i != tc - 1)
            assert jump <= 1.15 * others, \
                f"A2失败:{name} 在穿越年 t={tc} 出现超常态跳变({jump:.4f})"
    # A3 转换是过程:阈值 ±3pp 带内停留年数;±3 年窗变化远小于全期变化
    band15 = sum(1 for g in ger if abs(g - THR_ELITE) <= 0.03)
    band50 = sum(1 for g in ger if abs(g - THR_UNIV) <= 0.03)
    rng = ger[-1] - ger[0]
    win15 = abs(ger[min(t15 + 3, T - 1)] - ger[max(t15 - 3, 0)])
    win50 = abs(ger[min(t50 + 3, T - 1)] - ger[max(t50 - 3, 0)])
    assert band15 >= 4, f"A3失败:15% 带内仅 {band15} 年"
    assert band50 >= 2, f"A3失败:50% 带内仅 {band50} 年"
    assert win15 < 0.25 * rng and win50 < 0.25 * rng, "A3失败:转换窗变化过大"
    return {"t15": t15, "t50": t50, "band15": band15, "band50": band50,
            "win15": win15, "win50": win50, "range": rng}


# ----------------------------- 断言 B:分层虹吸 -----------------------------
def law_b(shares_r, shares_v, caps, n0, n1):
    """份额序列 + 首末容量 → 虹吸断言。"""
    assert all(d < 1e-12 for d in diffs(shares_r)), "B失败:研究型份额非单调下降"
    decline = shares_r[0] - shares_r[-1]
    assert decline >= 0.04, f"B失败:研究型份额仅降 {decline:.1%}"
    assert shares_v[-1] - shares_v[0] >= 0.05, "B失败:低层份额升幅<5pp"
    dN = n1 - n0
    inc_v = (caps["V"][-1] - caps["V"][0]) / dN
    inc_r = (caps["R"][-1] - caps["R"][0]) / dN
    assert inc_v > shares_v[0] + 0.08, \
        f"B失败:低层增量占比 {inc_v:.1%} 未显著超存量 {shares_v[0]:.1%}"
    assert inc_r < shares_r[0] - 0.05, \
        f"B失败:研究型增量占比 {inc_r:.1%} 未显著低于存量 {shares_r[0]:.1%}"
    return {"decline": decline, "inc_v": inc_v, "inc_r": inc_r}


# ----------------------------- 断言 C:职位滞后与双重市场 -----------------------------
def law_c(n0, n1, gr, gv, e_f=E_F, e_fr=E_FR, e_fv=E_FV):
    """学生增长倍数 vs 师资增长倍数;分层师生比恶化对比。"""
    g_students = n1 / n0
    g_faculty = g_students ** e_f
    ratio_mult = g_students ** (1.0 - e_f)
    assert ratio_mult >= 1.25, f"C失败:师生比仅恶化 ×{ratio_mult:.2f}"
    assert g_students > 1.35 * g_faculty, "C失败:学生/教师倍数差距不足 1.35×"
    growth_r = gr ** (1.0 - e_fr)   # 研究型层师生比恶化倍数
    growth_v = gv ** (1.0 - e_fv)   # 大众层师生比恶化倍数
    assert growth_v > 1.8 * growth_r, \
        f"C失败:双重市场对比不足({growth_v:.2f} vs {growth_r:.2f})"
    return {"g_students": g_students, "g_faculty": g_faculty,
            "ratio_mult": ratio_mult, "growth_r": growth_r, "growth_v": growth_v}


# ----------------------------- 基准情形:建世界并出报告 -----------------------------
def run_world(params):
    """从参数跑一个虚构系统:返回 GER/标签/份额/容量序列。"""
    ger = ger_curve(params["k"], params["lim"], params["t0"])
    labels = stage_labels(ger)
    n0 = ger[0] * POP
    caps = {"R": [], "M": [], "V": []}
    for g in ger:
        cR, cM, cV = tier_capacities(g * POP, n0, params["share_r0"],
                                     params["share_m0"], params["e_r"],
                                     params["e_m"])
        caps["R"].append(cR); caps["M"].append(cM); caps["V"].append(cV)
    shares_r = [c / (g * POP) for c, g in zip(caps["R"], ger)]
    shares_m = [c / (g * POP) for c, g in zip(caps["M"], ger)]
    shares_v = [c / (g * POP) for c, g in zip(caps["V"], ger)]
    return {"ger": ger, "labels": labels, "caps": caps,
            "shares": {"R": shares_r, "M": shares_m, "V": shares_v},
            "n0": n0, "n1": ger[-1] * POP}


def base_params():
    return {"k": K_G, "lim": L_G, "t0": T0, "share_r0": SHARE_R0,
            "share_m0": SHARE_M0, "e_r": E_R, "e_m": E_M,
            "e_f": E_F, "e_fr": E_FR, "e_fv": E_FV}


def main():
    if hasattr(sys.stdout, "reconfigure"):           # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(20260907)
    P = base_params()
    w = run_world(P)
    ger, labels = w["ger"], w["labels"]

    print("=" * 72)
    print("大众化与分层:特罗阶段论的模拟(虚构系统,60 年)")
    print("=" * 72)
    print(f"模型:GER(t)={P['lim']:.2f}/(1+exp(-{P['k']:.2f}(t-{P['t0']:.0f})))"
          "  三层容量 N^{e}:R e=0.55 / M e=0.85 / V 残差吸收")
    print(f"GER:{ger[0]:.1%} → {ger[-1]:.1%};在校生 ×{w['n1']/w['n0']:.1f};"
          f"期初份额 R/M/V = {SHARE_R0:.0%}/{SHARE_M0:.0%}/"
          f"{1-SHARE_R0-SHARE_M0:.0%}(全部风格化虚构参数)")

    # ---- 断言 A ----
    series = {"GER": ger, "研究型份额": w["shares"]["R"],
              "普通本科份额": w["shares"]["M"], "职业与社区份额": w["shares"]["V"],
              "在校生": [g * POP for g in ger]}
    ra = law_a(ger, series, labels)
    print(f"\n[断言A 阈值=标记] 15% 穿越于 t={ra['t15']},50% 穿越于 t={ra['t50']}:")
    print(f"  阶段标签序列:{''.join(labels[:1])}…{labels[ra['t15']-1]}|"
          f"{labels[ra['t15']]}…{labels[ra['t50']-1]}|{labels[ra['t50']]}…"
          f"{labels[-1]}(两处阶跃)")
    print(f"  穿越年 GER 单年变化 {abs(ger[ra['t15']]-ger[ra['t15']-1]):.1%} / "
          f"{abs(ger[ra['t50']]-ger[ra['t50']-1]):.1%},"
          f"均 ≤ 序列自身最大变化的 1.15 倍")
    print(f"  阈值 ±3pp 带内停留:{ra['band15']} 年(15%)与 {ra['band50']} 年(50%);"
          f"穿越 ±3 年窗 GER 变化 {ra['win15']:.1%}/{ra['win50']:.1%},"
          f"均 < 全期变幅({ra['range']:.1%})的 1/4")
    print("  ✓ 断崖在标签里,不在系统里:唯一阶跃的对象是『阶段』这个词;"
          "转换是以年计的过程,不是事件")

    # ---- 断言 B ----
    rb = law_b(w["shares"]["R"], w["shares"]["V"], w["caps"], w["n0"], w["n1"])
    print(f"\n[断言B 分层虹吸] 60 年间三层份额(R/M/V):")
    print(f"  研究型 {w['shares']['R'][0]:.0%} → {w['shares']['R'][-1]:.0%}"
          f"(降 {rb['decline']:.1%},单调);"
          f"普通本科 {w['shares']['M'][0]:.0%} → {w['shares']['M'][-1]:.0%};"
          f"职业与社区 {w['shares']['V'][0]:.0%} → {w['shares']['V'][-1]:.0%}")
    print(f"  全期增量分配:低层吃下 {rb['inc_v']:.0%}(存量仅 "
          f"{w['shares']['V'][0]:.0%});研究型仅 {rb['inc_r']:.0%}"
          f"(存量 {w['shares']['R'][0]:.0%})")
    print("  ✓ 扩张的增量主要进入低声望层:『更多人上大学』与"
          "『更多人上好大学』是两件事——分层吸收扩张(MMI 的机制版)")

    # ---- 断言 C ----
    gr = w["caps"]["R"][-1] / w["caps"]["R"][0]
    gv = w["caps"]["V"][-1] / w["caps"]["V"][0]
    rc = law_c(w["n0"], w["n1"], gr, gv)
    print(f"\n[断言C 职位滞后] 学生 ×{rc['g_students']:.1f} vs "
          f"教师 ×{rc['g_faculty']:.1f}(弹性 {E_F}):")
    print(f"  整体师生比 1:{RATIO0:.0f} → 1:{RATIO0*rc['ratio_mult']:.0f}"
          f"(恶化 ×{rc['ratio_mult']:.2f})")
    print(f"  分层对比:研究型层容量 ×{gr:.1f}/师资弹性 {E_FR} → 师生比恶化"
          f" ×{rc['growth_r']:.2f};大众层容量 ×{gv:.1f}/师资弹性 {E_FV} →"
          f" 恶化 ×{rc['growth_v']:.2f}")
    print("  ✓ 学术职位增长系统性滞后于学生扩张;滞后的账单主要由外围层"
          "(大众层)支付——洪堡式『教学科研统一』的岗位越来越贵,"
          "扩张的系统把统一做成了内圈的稀缺品")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:80 次参数抖动(k/L/t0/期初份额/五弹性)")
    n_draws, need = 80, 0.85
    passes = {"A 阈值=标记": 0, "B 分层虹吸": 0, "C 职位滞后": 0}
    for _ in range(n_draws):
        pj = {"k": rng.uniform(0.08, 0.13), "lim": rng.uniform(0.78, 0.88),
              "t0": rng.uniform(23.0, 27.0),
              "share_r0": rng.uniform(0.16, 0.24),
              "share_m0": rng.uniform(0.44, 0.55),
              "e_r": rng.uniform(0.45, 0.65), "e_m": rng.uniform(0.75, 0.92),
              "e_f": rng.uniform(0.58, 0.80), "e_fr": rng.uniform(0.88, 0.98),
              "e_fv": rng.uniform(0.52, 0.72)}
        wj = run_world(pj)
        ger_j = wj["ger"]
        # A(稳健子集:单调+恰穿一次+无超常态跳变+转换窗<30% 变幅)
        try:
            assert all(d > 0.0 for d in diffs(ger_j))
            t15 = crossing_year(ger_j, THR_ELITE)
            t50 = crossing_year(ger_j, THR_UNIV)
            assert t15 is not None and t50 is not None and 3 <= t15 < t50 <= T - 4
            ser_j = {"ger": ger_j, "r": wj["shares"]["R"], "v": wj["shares"]["V"]}
            ok_a = True
            for tc in (t15, t50):
                for xs in ser_j.values():
                    d = diffs(xs)
                    if abs(d[tc - 1]) > 1.15 * max(
                            abs(v) for i, v in enumerate(d) if i != tc - 1):
                        ok_a = False
            rng_j = ger_j[-1] - ger_j[0]
            if (abs(ger_j[t50 + 3] - ger_j[t50 - 3]) >= 0.30 * rng_j
                    or abs(ger_j[t15 + 3] - ger_j[t15 - 3]) >= 0.30 * rng_j):
                ok_a = False
            assert ok_a
            law_b(wj["shares"]["R"], wj["shares"]["V"], wj["caps"],
                  wj["n0"], wj["n1"])
            gr_j = wj["caps"]["R"][-1] / wj["caps"]["R"][0]
            gv_j = wj["caps"]["V"][-1] / wj["caps"]["V"][0]
            g_s = wj["n1"] / wj["n0"]
            assert g_s ** (1.0 - pj["e_f"]) >= 1.25
            assert g_s > 1.30 * g_s ** pj["e_f"]
            assert gv_j ** (1.0 - pj["e_fv"]) > 1.5 * gr_j ** (1.0 - pj["e_fr"])
            passes["A 阈值=标记"] += 1
            passes["B 分层虹吸"] += 1
            passes["C 职位滞后"] += 1
        except AssertionError:
            continue
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『次线性容量增长+残差吸收+职位弹性<1")
    print("  的简单机制足以生成三律』,不是任何真实高教系统的数量断言。")
    print("  真实读数还需:GER 分母口径(适龄人口怎么定义/留学生怎么算)、")
    print("  分层的制度变体(分层是设计还是自发)、人口波动与经济周期、")
    print("  师资的质的构成(兼职/非升即走/博士后化)——把容量弹性改成")
    print("  政策变量、把人口改成外生冲击,是使用本脚本的正确姿势(04 章 §三)。")


if __name__ == "__main__":
    main()
