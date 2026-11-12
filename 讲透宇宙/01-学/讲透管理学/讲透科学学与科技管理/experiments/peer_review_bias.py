# -*- coding: utf-8 -*-
"""同行评议偏差的蒙特卡洛解剖:噪声、利益冲突与录用率制度。

00 章 §七(反直觉②:拒稿≠质量差)、02 章 §二(指标代理效度)与 04 章走廊 3(评议沙盘)配套实验。纯标准库。

设定: 一批投稿,每篇有真实质量 q ~ N(0,1);每篇由 R 位审稿人评分后取均分,
     按录用率 α 截取前 k% 录用(录用率 = 期刊制度参数,非质量参数)。
     审稿分 = q + 噪声 ε + 利益冲突偏置 b·[审稿人与作者同阵营]。
         噪声 ε ~ N(0, σ²),σ=2.0 参数化(审稿分歧大于质量分歧——评议研究的通说校准);
         偏置:审稿人池 70% 属主导阵营 A(主导学派垄断评议),投稿两阵营各半;
         同阵营审稿人给投稿加 b(圈子内互相抬轿)。
对照: Part 1 噪声层:R 从 1 扫到 8——录用决定与真实质量的相关性应随 R 上升
         (多审稿人取均,噪声方差 σ²/R 收缩,信号占比上升);
     Part 2 偏置层:同一对"孪生稿"(同质量、异阵营)被独立 panels 反复评议——
         噪声成分的 SD 按 ~σ/√R 收缩,阵营均分差(偏置漂移)不随 R 缩小
         (系统性偏差不因平均而消失,信噪比反而上升);
         全池版:阵营间录用率差不随 R 收敛,而 bias=0 的对照组差 ≈ 0;
     Part 3 制度层:录用率从 8%(顶刊制)扫到 50%——低录用率下噪声主导录用:
         两个独立编辑部对同一批投稿的录用重合度崩塌、真质量前 10% 的稿子被拒是
         大概率事件——「拒稿≠质量差」的统计结构(结论属制度层,不可用于个体申诉)。
跑法: python experiments/peer_review_bias.py
"""

import math
import random


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (vx * vy)


def review_mean(rng, q, sigma, n_rev, paper_camp=None, p_camp_a=0.7, bias=0.0):
    """一篇投稿的 n_rev 人评议:返回均分。
    审稿人阵营:A(主导)概率 p_camp_a;与投稿同阵营时加 bias,否则 0。
    paper_camp=None 或 bias=0 时为纯噪声评议。"""
    total = 0.0
    for _ in range(n_rev):
        s = q + rng.gauss(0.0, sigma)
        if paper_camp is not None and bias > 0.0:
            camp_a = 1 if rng.random() < p_camp_a else 0
            if camp_a == paper_camp:
                s += bias
        total += s
    return total / n_rev


def decide(scores, rate):
    """按均分取前 rate 比例录用:返回录用指示列表。"""
    n = len(scores)
    k = max(1, int(round(n * rate)))
    order = sorted(range(n), key=lambda i: scores[i], reverse=True)
    acc = [0.0] * n
    for i in order[:k]:
        acc[i] = 1.0
    return acc


# ---------- Part 1: 噪声层——多审稿人平均,录用-质量相关性随 R 上升 ----------
def noise_sweep(seed=20260907):
    print("=" * 66)
    print("Part 1 噪声层:纯噪声评议(bias=0),录用率 20%,σ=2.0")
    print("=" * 66)
    n_papers, sigma, rate = 9000, 2.0, 0.20
    rows = []
    print(f"{'R(审稿人数)':>10} | {'录用-质量相关 r':>14} | {'真前20%被录率':>12}")
    for R in (1, 2, 4, 8):
        rng = random.Random(seed + 13 * R)
        qs, ss = [], []
        for _ in range(n_papers):
            q = rng.gauss(0.0, 1.0)
            qs.append(q)
            ss.append(review_mean(rng, q, sigma, R))
        acc = decide(ss, rate)
        r = pearson(acc, qs)
        top_q = set(sorted(range(n_papers), key=lambda i: qs[i], reverse=True)[:int(n_papers * rate)])
        recall = sum(acc[i] for i in top_q) / len(top_q)
        rows.append({"R": R, "r": r, "recall": recall})
        print(f"{R:10d} | {r:14.3f} | {recall:12.3f}")
    return rows


# ---------- Part 2: 偏置层——系统性偏差不因平均而消失 ----------
def bias_twins(seed=20260908):
    print()
    print("=" * 66)
    print("Part 2a 孪生稿层:q=0.6 的两篇同质稿(A 阵营 vs B 阵营),")
    print("       各被 4000 个独立 panel 评议——看均分分布怎么随 R 变")
    print("=" * 66)
    q0, sigma, b, panels = 0.6, 2.0, 0.8, 4000
    rows = []
    print(f"{'R':>4} | {'A 阵营均分':>10} | {'B 阵营均分':>10} | {'阵营差(漂移)':>12} | {'SD(噪声)':>9}")
    for R in (1, 4, 16):
        rng = random.Random(seed + 7 * R)
        sa = [review_mean(rng, q0, sigma, R, paper_camp=1, bias=b) for _ in range(panels)]
        sb = [review_mean(rng, q0, sigma, R, paper_camp=0, bias=b) for _ in range(panels)]
        drift = mean(sa) - mean(sb)
        sd = 0.5 * (math.sqrt(sum((x - mean(sa)) ** 2 for x in sa) / (panels - 1))
                    + math.sqrt(sum((x - mean(sb)) ** 2 for x in sb) / (panels - 1)))
        rows.append({"R": R, "drift": drift, "sd": sd})
        print(f"{R:4d} | {mean(sa):10.3f} | {mean(sb):10.3f} | {drift:12.3f} | {sd:9.3f}")
    print(f"理论漂移 = b·(2·p_A−1) = {b * (2 * 0.7 - 1):.2f}(与 R 无关);理论 SD ~ σ/√R")
    return rows


def bias_pool(seed=20260909):
    print()
    print("=" * 66)
    print("Part 2b 全池层:9000 篇投稿(两阵营各半、同质量分布),")
    print("       录用率 20%——阵营录用率差 vs R(附 bias=0 对照组)")
    print("=" * 66)
    n_papers, sigma, b, rate = 9000, 2.0, 0.8, 0.20
    rows = []
    print(f"{'R':>4} | {'偏置版 A−B 差':>13} | {'对照组 A−B 差':>13}")
    for R in (1, 4, 8):
        out = []
        for use_bias in (True, False):
            rng = random.Random(seed + 31 * R + (5 if use_bias else 0))
            qs, ss, camps = [], [], []
            for _ in range(n_papers):
                q = rng.gauss(0.0, 1.0)
                c = 1 if rng.random() < 0.5 else 0
                qs.append(q)
                camps.append(c)
                ss.append(review_mean(rng, q, sigma, R, paper_camp=c,
                                      bias=b if use_bias else 0.0))
            acc = decide(ss, rate)
            na = [i for i in range(n_papers) if camps[i] == 1]
            nb = [i for i in range(n_papers) if camps[i] == 0]
            ra = sum(acc[i] for i in na) / len(na)
            rb = sum(acc[i] for i in nb) / len(nb)
            out.append(ra - rb)
        rows.append({"R": R, "gap": out[0], "gap0": out[1]})
        print(f"{R:4d} | {out[0]:13.4f} | {out[1]:13.4f}")
    return rows


# ---------- Part 3: 制度层——低录用率下,噪声主导录用决定 ----------
def rate_regime(seed=20260910):
    print()
    print("=" * 66)
    print("Part 3 制度层:同一批 15000 篇投稿交两个独立编辑部(R=3,σ=2,纯噪声),")
    print("       录用率 8%(顶刊制)→25%→50%")
    print("=" * 66)
    n_papers, sigma, R = 15000, 2.0, 3
    rng0 = random.Random(seed)
    qs = [rng0.gauss(0.0, 1.0) for _ in range(n_papers)]
    rows = []
    print(f"{'录用率':>6} | {'换个部还能中':>12} | {'真前10%被拒':>12} | {'录用非前10%占比':>15}")
    for rate in (0.08, 0.25, 0.50):
        rng1 = random.Random(seed + 101 + int(rate * 1000))
        rng2 = random.Random(seed + 202 + int(rate * 1000))
        s1 = [review_mean(rng1, q, sigma, R) for q in qs]
        s2 = [review_mean(rng2, q, sigma, R) for q in qs]
        a1 = decide(s1, rate)
        a2 = decide(s2, rate)
        n1 = sum(a1)
        both = sum(x * y for x, y in zip(a1, a2))
        rep = both / n1                                  # P(录用2 | 录用1)
        top_q = set(sorted(range(n_papers), key=lambda i: qs[i], reverse=True)
                    [:int(n_papers * 0.10)])
        rej_top = 1.0 - sum(a1[i] for i in top_q) / len(top_q)   # P(拒 | 真前10%)
        non_top_share = (n1 - sum(a1[i] for i in top_q)) / n1    # 录用中非前10%占比
        rows.append({"rate": rate, "rep": rep, "rej_top": rej_top,
                     "non_top": non_top_share})
        print(f"{rate*100:5.0f}% | {rep:12.3f} | {rej_top:12.3f} | {non_top_share:15.3f}")
    return rows


# ---------- 主流程 ----------
def main():
    p1 = noise_sweep()
    p2a = bias_twins()
    p2b = bias_pool()
    p3 = rate_regime()

    print()
    print("读数:")
    print("  · Part 1:审稿人从 1 加到 8,录用-质量相关从 "
          f"{p1[0]['r']:.2f} 升到 {p1[-1]['r']:.2f}——多审稿人取均把噪声方差压成 1/R,")
    print("    决策里的质量信号占比上升。但相关封顶在 0.7 一带(20% 录用率的理论上限),")
    print("    再加人也买不回被噪声吞掉的区分度。")
    print(f"  · Part 2a:孪生稿的阵营差稳定在 {0.8 * (2 * 0.7 - 1):.2f} 上下,不随 R 缩小;")
    print("    而噪声 SD 从 ~2.0 塌到 ~0.5——平均把噪声除掉了,把偏置完整保留,")
    print("    偏置的信噪比反而随 R 上升。")
    print("  · Part 2b:偏置版阵营录用率差随 R 不收敛(噪声越小,同一漂移撬动越大),")
    print("    对照组(bias=0)差在 0 附近——平均对噪声有效,对系统性偏置无效:")
    print("    制度对策只能是利益冲突披露/回避,不是'多请几位'。")
    print("  · Part 3:录用率 8% 时,同一批稿换个独立编辑部只有约四分之一还能中,")
    print("    真质量前 10% 的稿子被拒是大概率事件,录用名单里一半以上不在真前 10%——")
    print("    低基率×高噪声的制度里,录用决定的大部分方差是噪声。")
    print("    拒稿≠质量差;录用也≠盖棺的优秀。这是制度层的统计性质,不是个人判决。")

    # ---------- 自验证断言 ----------
    # Part 1: 相关性随审稿人数严格上升(平均降噪)
    for a, b in zip(p1, p1[1:]):
        assert b["r"] > a["r"], "录用-质量相关性应随审稿人数上升(平均降噪)"
    assert p1[-1]["r"] - p1[0]["r"] > 0.12, "加审稿人应显著提升决策效度"
    assert all(r["r"] < 0.71 for r in p1), "20% 录用率下相关性有理论上限(~0.70)"

    # Part 2a: 漂移不随 R 缩小;噪声 SD 按 1/√R 塌缩
    theo = 0.8 * (2 * 0.7 - 1)                      # 理论漂移 0.32
    assert all(abs(r["drift"] - theo) < 0.06 for r in p2a), \
        "阵营漂移应稳定在理论值 b·(2p_A−1),不随 R 收缩"
    assert p2a[-1]["drift"] >= p2a[0]["drift"] - 0.02, "漂移不因平均而衰减"
    assert p2a[-1]["sd"] < p2a[0]["sd"] / 3.0, "噪声 SD 应按 ~σ/√R 塌缩(R=16 vs 1 应缩 4 倍)"
    assert p2a[0]["sd"] > theo * 3, "R=1 时噪声应淹没偏置(为什么它平时看不出来)"

    # Part 2b: 偏置版阵营差不收敛;对照组 ≈ 0
    assert all(r["gap"] > 0.018 for r in p2b), "偏置版阵营录用率差在所有 R 下应显著"
    assert p2b[-1]["gap"] >= p2b[0]["gap"] * 0.8, \
        "阵营差不随 R 收敛(噪声越小,同一漂移撬动的录用差越大)"
    assert all(abs(r["gap0"]) < 0.03 for r in p2b), "对照组(bias=0)阵营差应在 0 附近"

    # Part 3: 低录用率 → 噪声主导
    for a, b in zip(p3, p3[1:]):
        assert b["rep"] > a["rep"], "录用重合度应随录用率上升(基率升高,噪声占比下降)"
        assert b["rej_top"] < a["rej_top"], "真前 10% 被拒率应随录用率下降"
    assert p3[0]["rep"] < 0.50, "顶刊制(8%)下,换独立编辑部还能中的概率应低于一半"
    assert p3[-1]["rep"] - p3[0]["rep"] > 0.15, "录用率从 8% 到 50%,重合度应大幅上升"
    assert p3[0]["rej_top"] > 0.35, "顶刊制下真前 10% 的稿被拒应超过三分之一"
    assert p3[0]["non_top"] > 0.30, "顶刊制录用名单中,不在真前 10% 的应占三成以上"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
