# -*- coding: utf-8 -*-
"""出-回旅行-断层记忆-成长弧三律模拟:德国文学家族实验(GB/T 75064)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-德国文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。
涉纳粹时期文学与战后处理一律通说学术口径,本实验只做代际动力学的
风格化模型,不做史学判决。

三幕:
  幕一 世界文学概念的双向旅行(Weltliteratur 的出-回):
      概念=6 维单位语义向量,从魏玛 1827 出发(歌德铸造:民族文学互照的
      对话设想),经伦敦 1848(政治经济学回炉)、美国学院(学科化回炉)
      出走,再回流德语学界(方法论回炉)。每程 v←normalize(v+0.55·语境
      引力+0.10·噪声),漂移=1−cos(v0,v)。
      断言:①出-回累积漂移 > 单程漂移 2 倍,且末程漂移>0.30——回到德语
            时已非出发时的词(出口的词回不了家)
            ②回流版在德语学界的采纳竞争中胜出(声望瓮:英美中转声望
            加权,富者愈富);公平声望对照下两版对半——胜出靠中转声望
            不是瓮本身(学术话语的英美中转效应,回来的词自带签证)。
      分工声明:比较文学家族实验管"观念多站一般漂移",本幕管"单个概念
      的双向旅行个案"(出-回+回流竞争),两题不同。
  幕二 战后文学的断层记忆(1945 零点之争的代际动力学):
      四代作家各 260 部作品:是否触及 1933-45 主题按该代密度做伯努利,
      触及者再按该代母题分布抽母题。密度参数按通说叙事校形(风格化):
      流亡归来一代(亲历·幸存者叙事窄频)0.44;废墟文学一代(少年亲历·
      沉默的五十年代)0.14;68 一代(子代·审判父辈)0.32;两德统一/孙代
      (家族秘密延迟解码)0.40。
      断言:①直接经历代密度最高但母题频段最窄(有效种数最少)——幸存者
            叙事是高密度窄频段
            ②孙代反弹:密度高于 68 代与废墟代,并达到亲历代 0.8 倍以上;
            用 G1/G3 拟合的纯衰减模型预测废墟代远高于实测——记忆不是随
            时间衰减,是隔代回声(集体记忆的"孙子效应":家族秘密要到
            孙代才解码)。
  幕三 教育小说的路径规范(Bildungsroman 的标准弧与反噬):
      作品层:成长弧符合度 c(出走-迷误-和解三段)与正典化概率耦合,
      p=0.08+0.45·c·(0.30+0.70·规范强度(t));规范强度按通说校形
      (古典-浪漫期成形登顶,此后缓慢弱化)。
      时代层:反成长小说(成长失败型)份额=0.05+0.62·规范强度(t−L),
      L=60(作家写他们成长期经历过的最强规范)。
      断言:①符合标准弧的作品正典率 > 残弧作品 1.6 倍(范型与经典化耦合)
            ②反弧滞后:互相关搜索的最佳滞后在 40-80 年内,反弧峰值年晚于
            规范峰值年 40 年以上,1945 后反弧均值 > 1850 前 3 倍——反成长
            小说集中在传统规范最强的时期之后(规范的辩证反噬:没有比
            成长失败更德国的成长)。

跑法: python -u experiments/themes_collapse_memory.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现


# ==================== 幕一:世界文学概念的双向旅行 ====================

DIM = 6
GRAV_OUT = [
    ("伦敦 1848(政治经济学回炉)", (0.00, 0.90, 0.60, 0.00, 0.00, 0.00)),
    ("美国学院(学科化回炉)",     (0.20, 0.30, 0.20, 0.90, 0.70, 0.00)),
]
GRAV_BACK = [
    ("德语学界回流(方法论回炉)", (0.30, 0.10, 0.10, 0.40, 0.60, 0.80)),
]
V0 = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # 魏玛 1827 出发义:民族文学互照的对话
N_REP = 4000
N_SCHOLARS = 4000
URN_BASE = 600        # 声望瓮底数(两版各按声望×底数起票)
TRANSIT_P = 1.00      # 回流版的英美中转声望
DOMESTIC_P = 0.45     # 本土版(歌德原义)的本土声望


def travel(legs, rng):
    """概念旅行:逐程加语境引力与噪声后归一(拆包重铸)。"""
    v = list(V0)
    for _, g in legs:
        v = [v[i] + 0.55 * g[i] + 0.10 * rng.gauss(0, 1) for i in range(DIM)]
        n = math.sqrt(sum(x * x for x in v))
        v = [x / n for x in v]
    return v


def drift(v):
    """漂移 = 1 − cos(v0, v):语义改铸的幅度。"""
    return 1.0 - sum(a * b for a, b in zip(V0, v))


def adoption(transit, domestic, rng):
    """声望瓮:N 位学者在回流版/本土版间采纳,采纳即加票(富者愈富)。"""
    w_re, w_do = transit * URN_BASE, domestic * URN_BASE
    n_re = 0
    for _ in range(N_SCHOLARS):
        if rng.random() * (w_re + w_do) < w_re:
            n_re += 1
            w_re += 1
        else:
            w_do += 1
    return n_re / N_SCHOLARS


def act1():
    print("=" * 84)
    print("幕一 Weltliteratur 的出-回旅行: 语境引力改铸语义向量(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED)

    rt = [drift(travel(GRAV_OUT + GRAV_BACK, rng)) for _ in range(N_REP)]
    sg = [drift(travel(GRAV_OUT[:1], rng)) for _ in range(N_REP)]
    rt_m, sg_m = statistics.mean(rt), statistics.mean(sg)
    frac_changed = sum(1 for d in rt if d > 0.25) / len(rt)

    print("\n旅行路线: 魏玛1827 →(出)伦敦1848 → 美国学院 →(回)德语学界")
    print(f"  每程 v←normalize(v+0.55·引力+0.10·噪声); 蒙特卡洛 {N_REP} 次")
    print(f"{'旅程':<24} {'平均漂移':>8} {'漂移>0.25 占比':>14}")
    print(f"{'单程(仅伦敦一程)':<24} {sg_m:>8.3f} {'—':>14}")
    print(f"{'出-回全旅程(三程)':<24} {rt_m:>8.3f} {frac_changed:>13.1%}")
    print("读数:")
    print(f"  · 出-回累积漂移 {rt_m:.3f} = 单程 {sg_m:.3f} 的 {rt_m / sg_m:.1f} 倍——")
    print("    每一中转学科都是一次回炉, 回到德语时已非出发时的词")
    print(f"  · {frac_changed:.1%} 的旅程末程漂移>0.25: '改姓'不是小概率, 是结构性")

    assert rt_m > 2.0 * sg_m, "出-回累积漂移应>单程 2 倍"
    assert rt_m > 0.30, "末程漂移应>0.30(回国已改姓)"
    assert sg_m < 0.25, "单程对照应显著小于全旅程"
    assert frac_changed > 0.95, "绝大多数旅程末程漂移应过 0.25"

    share_re = adoption(TRANSIT_P, DOMESTIC_P, rng)
    share_ct = adoption(0.70, 0.70, rng)
    print(f"\n回流采纳竞争(声望瓮, {N_SCHOLARS} 位德语学界学者):")
    print(f"  英美中转声望 {TRANSIT_P:.2f} vs 本土声望 {DOMESTIC_P:.2f}: "
          f"回流版胜率 {share_re:.2f} —— 回流版胜出")
    print(f"  公平对照(两版声望同 0.70): 胜率 {share_ct:.2f} —— 对半")
    print("读数: 回流版自带签证: 声望差被瓮放大锁定, 而非瓮本身偏心")

    assert share_re > 0.55, "回流版应在德语学界胜出(>0.55)"
    assert 0.60 < share_re < 0.80, "回流版胜率应在 0.6-0.8(结构放大, 非碾压)"
    assert 0.44 < share_ct < 0.56, "公平对照应对半(机制检查: 靠声望不靠瓮)"
    assert share_re - share_ct > 0.10, "声望差应造成显著胜率差"
    print(f"\n✓ 幕一断言通过: 出-回漂移 {rt_m:.3f}>{sg_m:.3f}(×{rt_m / sg_m:.1f}); "
          f"回流版胜率 {share_re:.2f}(公平对照 {share_ct:.2f})"
          "——出口的词回不了家, 回来的词自带签证")


# ==================== 幕二:战后文学的断层记忆(孙子效应) ====================

N_WORKS_G = 260
GENS = [
    ("G1 流亡归来一代(亲历)", 0.44,
     [("流亡与归来", 0.42), ("集中营与迫害", 0.32), ("战争亲历", 0.18), ("抵抗", 0.08)]),
    ("G2 废墟文学一代(少年亲历)", 0.14,
     [("家中沉默的加害者", 0.40), ("少年兵的最后岁月", 0.40), ("空掉的犹太邻居住房", 0.20)]),
    ("G3 68 一代(子代)", 0.32,
     [("审判与文件", 0.28), ("父辈之罪", 0.28), ("法西斯的社会根源", 0.24), ("抵抗传统的重述", 0.20)]),
    ("G4 两德统一/孙代", 0.40,
     [("家族档案", 0.24), ("加害者后代", 0.22), ("普通人的共谋", 0.20), ("跨代沉默", 0.18), ("掠夺与归还", 0.16)]),
]


def effective_species(counts):
    """母题分布的有效种数 exp(H): 频带宽度的度量。"""
    n = sum(counts.values())
    h = -sum(c / n * math.log(c / n) for c in counts.values() if c > 0)
    return math.exp(h)


def act2():
    print("\n" + "=" * 84)
    print("幕二 断层记忆的代际动力学: 1933-45 主题书写密度×频段(四代各 260 部)")
    print("=" * 84)
    rng = random.Random(SEED)
    print("\n密度参数按通说叙事校形(风格化): 亲历 0.44/沉默 0.14/子代 0.32/孙代 0.40\n")

    dens, effs, tops = {}, {}, {}
    print(f"{'代际':<26} {'密度(实测)':>8} {'有效种数':>8}  首要母题")
    for name, p, themes in GENS:
        counts = dict.fromkeys([t for t, _ in themes], 0)
        themed = 0
        for _ in range(N_WORKS_G):
            if rng.random() < p:
                themed += 1
                r, acc, pick = rng.random(), 0.0, themes[-1][0]
                for tname, w in themes:
                    acc += w
                    if r <= acc:
                        pick = tname
                        break
                counts[pick] += 1
        dens[name] = themed / N_WORKS_G
        effs[name] = effective_species(counts)
        tops[name] = max(counts, key=counts.get)
        print(f"{name:<26} {dens[name]:>8.3f} {effs[name]:>8.2f}  {tops[name]}")

    d1 = dens[GENS[0][0]]
    d2 = dens[GENS[1][0]]
    d3 = dens[GENS[2][0]]
    d4 = dens[GENS[3][0]]
    e1, e3, e4 = effs[GENS[0][0]], effs[GENS[2][0]], effs[GENS[3][0]]
    # 纯衰减对照: 用 G1(代距0)与 G3(代距2)拟合密度=A·exp(-k·g), 预测 G2(代距1)
    k = -math.log(d3 / d1) / 2.0
    pred2 = d1 * math.exp(-k)

    print("\n读数:")
    print(f"  · 亲历代密度 {d1:.2f} 最高, 但有效种数 {e1:.2f} 最少——幸存者叙事:")
    print("    高密度窄频段(只写亲历过的: 流亡/迫害/战争/抵抗)")
    print(f"  · 废墟一代 {d2:.2f} 塌到谷底(沉默的五十年代); 68 一代 {d3:.2f} 回升,")
    print(f"    孙代 {d4:.2f} 继续爬——隔代回声, 不是衰减")
    print(f"  · 纯衰减模型(用 G1/G3 拟合)预测废墟代 {pred2:.2f} = 实测 {d2:.2f} 的 "
          f"{pred2 / d2:.1f} 倍——塌陷是记忆动力学的额外结构")
    print(f"  · 孙代频段 {e4:.2f} vs 亲历 {e1:.2f}: 从窄频到宽频(档案/后代/共谋/归还)")

    assert d1 > d3 and d1 > d4, "直接经历代密度应最高"
    assert e1 < e3 and e1 < e4, "直接经历代频段应最窄(幸存者叙事)"
    assert d3 > d2 and d4 > d2, "子代与孙代密度应反弹过废墟代"
    assert d4 > d3, "孙代密度应继续爬升(回声仍在增强)"
    assert d4 > 0.8 * d1, "孙代密度应达到亲历代 0.8 倍(隔代回声接近亲历水平)"
    assert pred2 > 1.8 * d2, "纯衰减模型应显著高估沉默代(记忆不是衰减)"
    print(f"\n✓ 幕二断言通过: 密度 {d1:.2f}/{d2:.2f}/{d3:.2f}/{d4:.2f}(高-塌-弹); "
          f"孙代达亲历代 {d4 / d1:.0%}——记忆不是随时间衰减, 是隔代回声")


# ==================== 幕三:教育小说的路径规范与反噬 ====================

N_WORKS_A = 240
YEARS = list(range(1780, 2021, 5))
LAG_TRUE = 60   # 反弧滞后: 作家写他们成长期经历过的最强规范


def norm_strength(t):
    """规范强度(通说校形): 古典-浪漫期(约 1800-1830)成形登顶, 此后缓慢弱化。"""
    up = 1.0 / (1.0 + math.exp(-(t - 1800.0) / 12.0))
    if t <= 1815:
        return up
    return up * (0.35 + 0.65 * math.exp(-(t - 1815.0) / 90.0))


def anti_share(t):
    """反成长小说(成长失败型)份额 = 规范强度延迟 LAG_TRUE 年的函数。"""
    return 0.05 + 0.62 * norm_strength(t - LAG_TRUE)


def pearson(xs, ys):
    """皮尔逊相关(手写, 兼容旧版 Python)。"""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else 0.0


def act3():
    print("\n" + "=" * 84)
    print("幕三 成长弧的规范与反噬: 弧符合度×正典化耦合 + 反弧滞后搜索")
    print("=" * 84)
    rng = random.Random(SEED)

    # 3a 作品层: 符合标准弧(出走-迷误-和解)的作品正典率高
    canon_hi = canon_lo = n_hi = n_lo = 0
    for _ in range(N_WORKS_A):
        year = rng.randint(1790, 2015)
        c = rng.random()
        p = 0.08 + 0.45 * c * (0.30 + 0.70 * norm_strength(year))
        canon = rng.random() < p
        if c >= 0.70:
            n_hi += 1
            canon_hi += canon
        elif c <= 0.30:
            n_lo += 1
            canon_lo += canon
    r_hi, r_lo = canon_hi / n_hi, canon_lo / n_lo

    print(f"\n[3a] 作品层({N_WORKS_A} 部, 年份 1790-2015 随机):")
    print(f"  标准弧作品(c≥0.70, n={n_hi}): 正典率 {r_hi:.3f}")
    print(f"  残弧作品  (c≤0.30, n={n_lo}): 正典率 {r_lo:.3f}")
    print(f"  耦合正差: 标准弧 ≈ 残弧的 {r_hi / r_lo:.1f} 倍——范型与经典化耦合")
    assert r_hi > 1.6 * r_lo, "标准弧作品正典率应>残弧 1.6 倍"
    assert r_hi > 0.25 and r_lo < 0.20, "两组正典率应落在合理带"

    # 3b 时代层: 反成长小说份额滞后规范强度
    anti = {t: anti_share(t) + rng.uniform(-0.008, 0.008) for t in YEARS}
    lags = list(range(0, 95, 5))
    corrs = {}
    for L in lags:
        ts = [t for t in YEARS if t - L >= 1780]
        corrs[L] = pearson([anti[t] for t in ts], [norm_strength(t - L) for t in ts])
    l_star = max(lags, key=lambda L: corrs[L])
    t_norm_peak = max(YEARS, key=norm_strength)
    t_anti_peak = max(YEARS, key=lambda t: anti[t])
    pre1850 = statistics.mean(anti[t] for t in YEARS if t < 1850)
    post1945 = statistics.mean(anti[t] for t in YEARS if t >= 1945)

    print(f"\n[3b] 时代层(1780-2020, 步长 5): 反弧份额=0.05+0.62·规范强度(t−L)+噪声")
    print(f"  互相关搜索: 最佳滞后 L*={l_star} 年(r={corrs[l_star]:.3f}; "
          f"L=0 时 r={corrs[0]:.3f})")
    print(f"  规范强度峰值 {t_norm_peak} 年(古典-浪漫期), 反弧份额峰值 {t_anti_peak} 年"
          f"(滞后 {t_anti_peak - t_norm_peak} 年)")
    print(f"  反弧份额均值: 1850 前 {pre1850:.3f} → 1945 后 {post1945:.3f}"
          f"(×{post1945 / pre1850:.1f})")
    print("读数: 反成长小说不是范型衰弱后的空位填补, 是规范最强时期的延迟回声")
    print("      ——作家写他们成长期经历过的最强规范, 用它的彻底反面为它注释")

    assert 40 <= l_star <= 80, "最佳滞后应在 40-80 年(检测到滞后而非同步)"
    assert corrs[l_star] > corrs[0] + 0.15, "滞后版相关应显著压过同步版"
    assert t_anti_peak - t_norm_peak >= 40, "反弧峰值应晚于规范峰值 40 年以上"
    assert post1945 > 3.0 * pre1850, "1945 后反弧均值应>1850 前 3 倍(反噬集中在后期)"
    print(f"\n✓ 幕三断言通过: 正典率 {r_hi:.2f} vs {r_lo:.2f}(×{r_hi / r_lo:.1f}); "
          f"滞后 L*={l_star} 年, 反弧峰 {t_anti_peak} 晚规范峰 {t_norm_peak} "
          f"{t_anti_peak - t_norm_peak} 年——没有比成长失败更德国的成长")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① Weltliteratur 出-回旅行: 累积漂移>单程 2 倍且末程改姓; 回流版靠英美")
    print("     中转声望在德语学界胜出(公平对照对半)——出口的词回不了家, 回来的词")
    print("     自带签证")
    print("  ② 断层记忆的孙子效应: 亲历代高密度窄频; 废墟代塌陷; 孙代反弹至亲历代")
    print("     0.8 倍以上且频段变宽; 纯衰减模型解释不了塌陷——记忆不是随时间衰减,")
    print("     是隔代回声(家族秘密要到孙代才解码)")
    print("  ③ 成长弧的规范反噬: 标准弧作品正典率≈残弧 2-3 倍; 反成长小说份额滞后")
    print("     规范强度约两代(40-80 年), 峰值晚于规范峰 40 年以上, 集中在 1945 后")
    print("     ——没有比成长失败更德国的成长")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
