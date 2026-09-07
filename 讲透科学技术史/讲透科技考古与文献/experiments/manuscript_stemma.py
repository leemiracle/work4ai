# -*- coding: utf-8 -*-
"""手稿谱系(stemma)重建:模拟抄写传播,用"共享罕见错误"聚类出抄本家谱。

00 章手稿谱系骨架 + 04 章 C2(谱系走廊)的成品。文本谱系学百年方法的
教学化(拉赫曼-毛斯传统,02 章 T3 降档的定量面):
  祖本(archetype)O 经抄写产生抄本树:O→X/Y(中间支本,各自隔着
  一代佚名抄工)→X1,X2,Y1,Y2(存世证人)。每个抄写事件逐位点
  (locus,一个可变异的词位)以 p 概率出错:以 q 概率犯"形近通行讹"
  (所有抄工在同一位点倾向犯同一个错——己/已/巳式趋同),否则犯
  独有错;出错即改写该位点(晚近抄工的新错覆盖祖传读法)。
  谱系学家的程序(不偷看真相):
    ① 四本多数票出临时定本 ② 两证人同偏离定本、读法相同且全库
       恰 2 例 = 共享罕见错误(谱系信号) ③ 各证人与信号最强者互配。

三组结构化断言:
  ① 谱系信号成立:低错误率下,子树内(X1-X2,Y1-Y2)共享罕见错误
     严格多于子树间(显著分离),互配恢复真实谱系;多数票近似
     复原祖本——共同错误即共同祖先,一个好错胜过十处相同的正确
  ② 方法边界:抄写错误率推向极端时信号淹没——祖传共享错误被
     后代新错覆盖(存活率随错误率下跌),巧合趋同讹增长;
     分离率与配对率崩塌。错误率过低也不行(太干净的传统无错误
     可共享)——方法只活在中间区间
  ③ HTR 稳健性与质量门槛:数字化层(随机误读+书写体系统性误读,
     各证人私有)叠加后,罕见错误聚合仍稳健——识别噪声多为单证
     人私有变体,被"全库恰 2 例"的稀有性筛自动剔除;但转录质量
     恶化到门槛之下,谱系重建随之崩塌——数字化管线的质量纪律
     (皇家历史学会"The Trouble with Text Mining"的定量小品)。

⚠ 史学纪律(02/04 章):本脚本是零模型(机器化 T6)——真实校勘
  面临污染(混合抄本)、趋同仿古、转录粒度之争等本模型未含的
  困难;输出是方法机理演示,不构成对任何真实手稿传统的谱系结论。

跑法: python experiments/manuscript_stemma.py
"""
import random

# ── 教学参数(真实研究须以 03 章 schema 换实证参数)──────────────────
N_LOCI = 250          # 变体位点数(一部小作品的"词位"规模)
CHAIN = 2             # 每条树边隔几代抄工(中间支本也是抄本链的终点)
Q_COMMON = 0.75       # 出错时取"形近通行讹"(可趋同)的概率
P_LOW, P_MID, P_HIGH = 0.10, 0.20, 0.55   # 每抄写事件每位点出错率
P_HTR, P_HAND = 0.08, 0.06   # 数字化层:随机误读率/书写体系统性误读率
P_HTR_BAD, P_HAND_BAD = 0.15, 0.10        # 劣质转录门槛
TRIALS = 240          # 断言②③的重复试验次数

WITNESSES = ("X1", "X2", "Y1", "Y2")          # 存世证人(抄本)
TREE = {"X": "O", "Y": "O", "X1": "X", "X2": "X",
        "Y1": "Y", "Y2": "Y"}                  # 子→父;O=祖本
EDGES = (("O", "X"), ("O", "Y"), ("X", "X1"),
         ("X", "X2"), ("Y", "Y1"), ("Y", "Y2"))
WITHIN = (("X1", "X2"), ("Y1", "Y2"))          # 真实谱系:子树内对
ACROSS = (("X1", "Y1"), ("X1", "Y2"), ("X2", "Y1"), ("X2", "Y2"))
PAIRS = WITHIN + ACROSS


def transcribe(text, p_err, rng, uid):
    """一次抄写:逐位点以 p_err 出错并改写该位点。

    读法编码:0=祖本读法;"s{位点}"=形近通行讹(全抄工趋同);
    "u{序号}"=独有错(绝不趋同)。出错即改写——晚近抄工的新错
    覆盖祖传读法,这是高错误率下祖传共享错误被侵蚀的机制(断言②)。
    """
    out = []
    for locus, reading in enumerate(text):
        if rng.random() < p_err:
            if rng.random() < Q_COMMON:
                out.append("s%d" % locus)
            else:
                uid[0] += 1
                out.append("u%d" % uid[0])
        else:
            out.append(reading)
    return out


def make_tradition(p_err, rng):
    """从祖本 O 按拓扑序抄写全树;每条边隔 CHAIN 代抄工。"""
    uid = [0]
    texts = {"O": [0] * N_LOCI}
    for parent, child in EDGES:
        text = texts[parent]
        for _ in range(CHAIN):
            text = transcribe(text, p_err, rng, uid)
        texts[child] = text
    return texts


def majority_text(texts):
    """谱系学家第一步:存世证人多数票临时定本(平票取祖本读法,
    再平取字典序小者——确定性,不偷看真相)。"""
    prov = []
    for locus in range(N_LOCI):
        counts = {}
        for w in WITNESSES:
            r = texts[w][locus]
            counts[r] = counts.get(r, 0) + 1
        prov.append(max(counts, key=lambda r: (counts[r], str(r) == "0", str(r))))
    return prov


def shared_rare_errors(texts, prov):
    """第二步:两证人共享的罕见错误——同偏离定本、读法相同,
    且该读法全库恰 2 例(稀有性筛:自动剔除单证人私有噪声)。"""
    freq = {}
    for w in WITNESSES:
        for locus, r in enumerate(texts[w]):
            freq[(locus, r)] = freq.get((locus, r), 0) + 1
    shared = {}
    for a, b in PAIRS:
        n = 0
        for locus in range(N_LOCI):
            base = prov[locus]
            ra, rb = texts[a][locus], texts[b][locus]
            if ra == rb != base and freq[(locus, ra)] == 2:
                n += 1
        shared[(a, b)] = n
    return shared


def pair_up(scores, best=True):
    """第三步:各证人与得分最优者互配;成功=两对互指还原真实谱系。"""
    partner = {}
    for w in WITNESSES:
        others = [o for o in WITNESSES if o != w]
        if best:      # 共享错误最多者=同支本兄弟
            partner[w] = max(others, key=lambda o: (
                scores.get((w, o), scores.get((o, w), 0)), o))
        else:         # 全谱距离最近者(对照法:吸收一切噪声)
            partner[w] = min(others, key=lambda o: (
                scores.get((w, o), scores.get((o, w), 0)), o))
    return all(partner[a] == b and partner[b] == a for a, b in WITHIN)


def separation(texts, prov):
    """经典判据:子树内共享错误的最小值 > 子树间的最大值(显著分离)。"""
    shared = shared_rare_errors(texts, prov)
    return (min(shared[p] for p in WITHIN)
            > max(shared[p] for p in ACROSS), shared)


def group_by_shared(texts):
    """谱系学程序:多数票→罕见共享→互配。返回是否恢复真实谱系。"""
    return pair_up(shared_rare_errors(texts, majority_text(texts)), best=True)


def distance_matrix(texts):
    """对照法:全谱逐位点距离,不做稀有性过滤(以全权重吸收噪声)。"""
    return {(a, b): sum(1 for locus in range(N_LOCI)
                        if texts[a][locus] != texts[b][locus])
            for a, b in PAIRS}


def group_by_distance(texts):
    return pair_up(distance_matrix(texts), best=False)


def digitize(texts, p_htr, p_hand, rng):
    """数字化层:每本独立过 HTR,每位点两种误读(先判系统性再判随机):
      书写体系统性误读(率 p_hand):同一引擎对同一写手反复认错——
        输出读法带证人标记,永不与他人相同(各证人私有);
      随机误读(率 p_htr):误读为该位点读法池(祖本读法+全库已见
        读法)中的另一读法——独立噪声。
    机器抄写员与抄工同构:私有错为主,恰好是稀有性筛的过滤对象。"""
    out = {}
    for w in WITNESSES:
        new = list(texts[w])
        for locus in range(N_LOCI):
            dice = rng.random()
            if dice < p_hand:
                new[locus] = "h%s_%d" % (w, locus)
            elif dice < p_hand + p_htr:
                pool = ({0} | {texts[v][locus] for v in WITNESSES}) - {new[locus]}
                if pool:
                    new[locus] = rng.choice(sorted(pool, key=str))
        out[w] = new
    return out


def survival_rate(texts):
    """真谱系诊断:中间支本(X/Y)的祖传错误原样存活到两片叶子的比例。"""
    hit = miss = 0
    for node in ("X", "Y"):
        kids = [k for k in TREE if TREE[k] == node]
        for locus in range(N_LOCI):
            if texts[node][locus] != 0:
                if all(texts[k][locus] == texts[node][locus] for k in kids):
                    hit += 1
                else:
                    miss += 1
    return hit / (hit + miss) if hit + miss else 1.0


def rate(p_err, p_htr, p_hand, method, seed):
    """TRIALS 次独立传统的成功率;另计经典分离判据的达标率。"""
    rng = random.Random(seed)
    ok = sep = 0
    for _ in range(TRIALS):
        texts = make_tradition(p_err, rng)
        if p_htr or p_hand:
            texts = digitize(texts, p_htr, p_hand, rng)
        if method(texts):
            ok += 1
        if separation(texts, majority_text(texts))[0]:
            sep += 1
    return ok / TRIALS, sep / TRIALS


def witness_profile(texts, w, prov):
    """单本错误构成:与临时定本不同处=讹;其中全库恰 2 例≈承自支本。"""
    err = sum(1 for locus in range(N_LOCI) if texts[w][locus] != prov[locus])
    return err


def main():
    print("=" * 76)
    print("手稿谱系重建:O→X/Y(各隔 %d 代抄工)→X1,X2,Y1,Y2;"
          "共享罕见错误聚类(L=%d 位点)" % (CHAIN, N_LOCI))
    print("=" * 76)

    # ── 主表:低错误率单次运行,展示信号结构 ──────────────────────
    rng = random.Random(20260907)
    texts = make_tradition(P_LOW, rng)
    prov = majority_text(texts)
    shared = shared_rare_errors(texts, prov)
    recon_err = sum(1 for locus in range(N_LOCI) if prov[locus] != 0)
    print("\n[演示传统] 抄写错误率 p=%.2f(每次抄写约 %.0f 处新错)"
          % (P_LOW, P_LOW * N_LOCI))
    print("  存世证人各自偏离临时定本处数:",
          " ".join("%s=%d" % (w, witness_profile(texts, w, prov))
                   for w in WITNESSES))
    print("  罕见共享错误矩阵(同偏离定本+读法相同+全库恰2例):")
    for a, b in PAIRS:
        tag = "子树内" if (a, b) in WITHIN else "子树间"
        print("    %s-%s: %2d  (%s)" % (a, b, shared[(a, b)], tag))
    within_min = min(shared[p] for p in WITHIN)
    across_max = max(shared[p] for p in ACROSS)
    surv = survival_rate(texts)

    # ── 断言 1:谱系信号成立(显著分离+互配复原+祖本近似重建)────────
    assert within_min > across_max + 1, \
        "子树内共享应显著多于子树间(留间隔)"
    assert group_by_shared(texts), "互配法应恢复真实谱系 {X1,X2},{Y1,Y2}"
    assert recon_err < 0.24 * N_LOCI, \
        "多数票定本应与祖本大体一致(≥3/4 位点,足以支撑偏离统计)"
    assert surv >= 0.5, "低错误率下祖传错误应多数存活到两叶"
    print("\n" + "=" * 76)
    print("断言 1 通过:子树内共享 ≥ %d ≫ 子树间 ≤ %d;互配恢复真实谱系;"
          "支本错误存活率 %.2f ✓" % (within_min, across_max, surv))
    print("            ——多数票临时定本 %d/%d 位点(%.0f%%)与祖本一致:"
          "作偏离统计的底座够用,作校勘定本不够——'临时'二字的含义"
          % (N_LOCI - recon_err, N_LOCI, 100.0 * (N_LOCI - recon_err) / N_LOCI))
    print("            ——共同错误即共同祖先:一个好错胜过十处相同的"
          "正确(谱系学百年通则,00 章反直觉之二)")

    # ── 断言 2:方法边界——错误率推向极端时信号淹没 ───────────────────
    stats = {}
    for tag, p in (("过低", 0.01), ("低", P_LOW), ("中", P_MID), ("高", P_HIGH)):
        stats[tag] = rate(p, 0.0, 0.0, group_by_shared,
                          seed=1000 + int(p * 1000))
    rng2 = random.Random(7)
    surv_hi = sum(survival_rate(make_tradition(P_HIGH, rng2))
                  for _ in range(30)) / 30
    assert stats["低"][1] >= 0.99 and stats["低"][0] >= 0.99, \
        "低错误率应几乎总是显著分离且配对成功"
    assert stats["高"][1] <= 0.75, "极端错误率应频繁失去显著分离(信号淹没)"
    assert stats["高"][1] < stats["低"][1] - 0.2, "分离率应有大幅落差"
    assert stats["过低"][1] < 0.99, "错误过少也不行:太干净的传统无信号"
    print("断言 2 通过:错误率 0.01/低/中/高 → 配对成功率 "
          "%.2f/%.2f/%.2f/%.2f,分离率 %.2f/%.2f/%.2f/%.2f;"
          "高错误率下支本错误存活率仅 %.2f ✓"
          % (stats["过低"][0], stats["低"][0], stats["中"][0], stats["高"][0],
             stats["过低"][1], stats["低"][1], stats["中"][1], stats["高"][1],
             surv_hi))
    print("            ——两路夹击:祖传共享错误被后代新错覆盖(存活率 "
          "%.2f),巧合趋同讹随错误率增长;而错误过少时无错可共享——"
          "方法只活在中间区间(断言②=方法边界)" % surv_hi)

    # ── 断言 3:HTR 叠加的稳健性与质量门槛 ──────────────────────────
    clean = rate(P_LOW, 0.0, 0.0, group_by_shared, seed=2001)
    real = rate(P_LOW, P_HTR, P_HAND, group_by_shared, seed=2002)
    bad = rate(P_LOW, P_HTR_BAD, P_HAND_BAD, group_by_shared, seed=2003)
    dist_real = rate(P_LOW, P_HTR, P_HAND, group_by_distance, seed=2004)
    dist_bad = rate(P_LOW, P_HTR_BAD, P_HAND_BAD, group_by_distance, seed=2005)
    assert real[0] >= 0.95, "现实级 HTR 噪声下罕见错误聚合应稳健(≥0.95)"
    assert bad[0] <= 0.90, "劣质转录应显著破坏谱系重建(质量门槛)"
    assert real[0] - bad[0] >= 0.10, "稳健与崩塌之间应有显著落差"
    print("断言 3 通过:HTR(误读 %.0f%%+写手噪声 %.0f%%)叠加后配对成功率 "
          "%.3f(无数字化层 %.3f);转录劣化到 %.0f%%/%.0f%% 后跌至 %.3f ✓"
          % (P_HTR * 100, P_HAND * 100, real[0], clean[0],
             P_HTR_BAD * 100, P_HAND_BAD * 100, bad[0]))
    print("            ——识别噪声多为单证人私有变体,被'全库恰 2 例'"
          "筛自动剔除(对照的全距离法:稳健 %.3f/劣化 %.3f);但私有噪声"
          "也在侵蚀真信号,转录质量跌过门槛,重建照样崩——数字化不是"
          "护身符,是管线纪律" % (dist_real[0], dist_bad[0]))

    print("\n" + "=" * 76)
    print("三组断言全部通过:谱系信号成立 / 极端错误率信号淹没+过净无"
          "信号(双边界)/ HTR 噪声下聚合稳健但转录质量设门槛 ✓")
    print("\n⚠ 史学纪律提醒:真实手稿传统有污染(混合抄本)、趋同仿古、"
          "转录粒度之争——本模型未含;谱系结论须经 03 章构造合法性"
          "三问(provenance 分离/转录声明/幸存声明)方可入库。")


if __name__ == "__main__":
    main()
