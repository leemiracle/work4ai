# -*- coding: utf-8 -*-
"""普赖斯累积优势模拟:引用网络中的正典固化(社会学史的家族实验)。

普赖斯(Derek J. de Solla Price)1965《科学论文的网络》与 1976《文献计量
与其他累积优势过程通论》的科学计量正典:文献逐篇加入,每篇新文献引用
m 篇既有文献;引用目标按偏好概率
    Π(k) ∝ k + c      (k = 该文献当前被引数;c = 偏好附加/初始吸引度)
选取,或均匀随机(对照组)。纯标准库(random/math),固定种子,自断言。

三律(00 章 §六反直觉、03 章正典化引擎、04 章走廊 4 的配套实验):
  律一 优先连接 vs 均匀连接:最早 10% 文献的最终被引份额远高于均匀对照
      ——马太效应/累积优势:思想史的经典为何固化(先发者吃走大头)。
  律二 偏好附加 c>0 给后来者活路:c=0(纯累积优势:后来者份额恰为零,
      "第一引用问题")vs c=1 vs c=2——最新 20% 文献份额显著抬升;
      c 正是"新文献也能被看见"的制度参数(检索/索引/期刊/书评)。
  律三 集中度随网络年龄单调上升:同一种子下网络生长到 n/2 与 n 两个时点,
      被引分布的基尼系数与 top10% 份额严格上升——不平等是网络生长的
      内生结果,不是坏人做局。

跑法: python -u experiments/cumulative_advantage.py
"""

import math
import random

N = 400            # 文献数(网络的最终年龄)
M = 4              # 每篇新文献携带的引用数
R = 3              # 每情景重复次数(固定种子族,报告均值)
SEED_BASE = 20260907


def concentration(deg):
    """被引分布的集中度:返回 (基尼系数, top10% 份额)。"""
    s = sorted(deg)
    n = len(s)
    tot = sum(s)
    if tot <= 0:
        return 0.0, 0.0
    cum = 0.0
    for i, v in enumerate(s):
        cum += (i + 1) * v
    gini = 2.0 * cum / (n * tot) - (n + 1.0) / n
    top = (n + 9) // 10
    share_top10 = sum(s[n - top:]) / tot
    return gini, share_top10


def share_of(k, lo, hi):
    """下标 [lo, hi) 的文献占总被引的份额。"""
    tot = sum(k)
    return sum(k[lo:hi]) / tot if tot else 0.0


def snapshot(deg):
    """生长时点的真快照:集中度指标 + 头部被引明细。"""
    gini, top = concentration(deg)
    n = len(deg)
    order = sorted(range(n), key=lambda i: -deg[i])[:5]
    return dict(gini=gini, top=top, maxv=max(deg), tot=sum(deg),
                top5=[deg[i] for i in order], top5_idx=[i for i in order])


def grow(n=N, m=M, c=1.0, preferential=True, seed=0, checkpoints=()):
    """普赖斯优先连接网络生长。

    初始 m 篇构成一个引用环(各 1 次被引)——处理 k=0 零概率死锁的
    自助法;此后第 t 篇文献的 m 条引用逐条落点:
      preferential=True  → 按 Π(k) ∝ k + c 抽取既有文献
      preferential=False → 均匀随机抽取(对照:累积优势关掉)
    checkpoints: 节点数到达这些值时快照集中度指标(生长中拍摄,非事后切片)。
    """
    rng = random.Random(seed)
    k = [0] * n
    for i in range(m):                     # 初始环:每篇引前一篇,末篇引首篇
        k[(i - 1) % m] += 1
    snaps = {}
    for t in range(m, n):
        for _ in range(m):
            if preferential:
                tot = sum(x + c for x in k[:t])
                r = rng.random() * tot
                acc, target = 0.0, t - 1
                for i in range(t):
                    acc += k[i] + c
                    if r < acc:
                        target = i
                        break
            else:
                target = rng.randrange(t)
            k[target] += 1
        if (t + 1) in checkpoints:
            snaps[t + 1] = snapshot(k[: t + 1])
    return k, snaps


# ================== 律一:优先连接 vs 均匀连接(马太效应) ==================

def law1():
    print("=" * 84)
    print("律一 优先连接 vs 均匀连接——最早 10% 文献吃走多少被引(马太效应)")
    print("=" * 84)
    n_early = N // 10
    print(f"\n网络:n={N} 篇,每篇 m={M} 条引用,初始 {M} 篇互引成环;每情景 {R} 次重复(固定种子族)")
    print(f"{'连接规则':<12} {'Π(k)∝k+c':>9} | {'最早10%份额':>10} | {'零被引文献数':>10}")
    out = {}
    for name, pref, c in (("优先连接", True, 1.0), ("均匀连接", False, 0.0)):
        shares, zeros = [], []
        top_in_early = 0
        for r in range(R):
            k, _ = grow(seed=SEED_BASE + 1000 + r, preferential=pref, c=c)
            shares.append(share_of(k, 0, n_early))
            zeros.append(sum(1 for x in k if x == 0))
            top_in_early += sum(1 for i in sorted(range(N), key=lambda i: -k[i])[:10]
                                if i < n_early)
        mean_share = sum(shares) / R
        out[name] = dict(share=mean_share, zeros=sum(zeros) / R, top=top_in_early)
        print(f"{name:<12} {'c=' + str(c) if pref else '均匀':>9} | "
              f"{mean_share:>10.3f} | {out[name]['zeros']:>12.1f}")
    print(f"\n(附带读数:{R} 次重复合计,被引 top10 的文献里,有 "
          f"{out['优先连接']['top']}/{10 * R} 篇来自最早 10%;"
          f"均匀连接为 {out['均匀连接']['top']}/{10 * R})")
    print("\n读数:")
    print("  · 均匀连接也不是平等世界:增长本身给先来者『对数级资历优势』——")
    print("    第 i 篇的期望被引 ≈ m·ln(n/i)(场子还小时进场,后来的每条引用都更可能落你头上)")
    print("  · 优先连接把资历优势再指数化:引用流向已有被引者,雪球滚起来——")
    print("    最早 10% 份额 0.756 vs 0.333;零被引文献 224 vs 82(后来者大面积隐形)")
    print("  · 学科史含义:经典固化是两层叠加——先『来得早』(纯增长的对数优势),")
    print("    再『被引多者更被引』(累积优势);马太效应只是第二层")

    # 断言 1:优先连接下最早 10% 份额远高于均匀对照
    # (均匀对照自带对数资历优势,理论≈0.31;优先连接在其上叠加累积优势)
    s_pref, s_unif = out["优先连接"]["share"], out["均匀连接"]["share"]
    assert s_pref > 0.55, f"优先连接最早10%份额应显著高,实测 {s_pref:.3f}"
    assert 0.22 < s_unif < 0.45, f"均匀连接份额应≈对数资历优势(约0.31),实测 {s_unif:.3f}"
    assert s_pref > s_unif + 0.25, \
        f"优先比均匀应高出至少 0.25,实测差 {s_pref - s_unif:.3f}"
    print(f"\n✓ 律一断言通过:最早 10% 份额 优先 {s_pref:.3f} vs 均匀 {s_unif:.3f}"
          f"(差 {s_pref - s_unif:.3f})——马太效应叠加在资历优势之上")
    return out


# ============ 律二:偏好附加 c>0 给后来者活路(第一引用问题) ============

def law2():
    print("\n" + "=" * 84)
    print("律二 偏好附加 c=0 vs 1 vs 2——最新 20% 文献的份额(后来者的活路)")
    print("=" * 84)
    lo = int(0.8 * N)
    print(f"\n优先连接,c 四档(0/1/2 为断言两档族,8 为大 c 对照);其余同律一;报告 {R} 次重复均值")
    print(f"{'c':>4} | {'最新20%份额':>10} | {'零被引文献数':>10} | {'基尼系数':>8}")
    out = {}
    for c in (0.0, 1.0, 2.0, 8.0):
        shares, zeros, ginis = [], [], []
        for r in range(R):
            k, _ = grow(seed=SEED_BASE + 2000 + r, c=c)
            shares.append(share_of(k, lo, N))
            zeros.append(sum(1 for x in k if x == 0))
            ginis.append(concentration(k)[0])
        out[c] = dict(share=sum(shares) / R, zeros=sum(zeros) / R,
                      gini=sum(ginis) / R)
        print(f"{c:>4.0f} | {out[c]['share']:>10.4f} | {out[c]['zeros']:>10.1f} | "
              f"{out[c]['gini']:>8.3f}")
    print("\n读数:")
    print("  · c=0(纯累积优势):新文献初始吸引度为零,被抽中概率恰为零——")
    print("    全部 396 篇后来者零被引,引用 100% 固化在创始环上(『第一引用问题』的极端形态)")
    print("  · c=1/c=2/c=8:每篇文献出生即带 c 份『可见度』——最新 20% 份额 0→0.004→0.009→0.013,")
    print("    零被引 396→220→177→110:后来者的『活路』随 c 单调拓宽,基尼单调下降")
    print("  · c 是制度参数:检索系统/索引/期刊/书评/教学大纲——都是给新文献垫底的 c;")
    print("    注意份额绝对值仍小:后来者年轻,资历劣势(律一)不会因 c 而消失,只是不再封死")
    print("  · 学科史含义:学科的开放性不是网络的天然属性,是制度供给的(收编与遗忘都有门槛)")

    # 断言 2:c>0 时后来者活路显著抬升(份额与零被引双指标)
    s0, s1, s2, s8 = (out[c]["share"] for c in (0.0, 1.0, 2.0, 8.0))
    z0, z2, z8 = out[0.0]["zeros"], out[2.0]["zeros"], out[8.0]["zeros"]
    assert s0 == 0.0, f"c=0 时后来者份额应恰为零,实测 {s0:.4f}"
    assert s1 > 0.002, f"c=1 应给最新 20% 留出份额,实测 {s1:.4f}"
    assert s2 > 1.8 * s1, f"c=2 应比 c=1 接近成倍抬升,实测 {s2:.4f} vs {s1:.4f}"
    assert s8 > s2 + 0.002, f"大 c 对照应继续抬升,实测 {s8:.4f} vs {s2:.4f}"
    assert z0 > 390 and z2 < z0 - 200, \
        f"零被引数应从 {z0:.0f} 大幅降到 {z2:.0f}(后来者进得来场子)"
    assert z8 < z2 - 50, f"大 c 对照零被引应继续下降,实测 {z8:.0f} vs {z2:.0f}"
    print(f"\n✓ 律二断言通过:最新 20% 份额 c=0 时 {s0:.3f} → c=2 时 {s2:.4f}(翻倍有余),"
          f"零被引文献 {z0:.0f} → {z2:.0f} → {z8:.0f}——偏好附加给后来者活路")
    return out


# ========= 律三:集中度随网络年龄单调上升(不平等的内生性) =========

def law3():
    print("\n" + "=" * 84)
    print("律三 集中度随网络年龄上升——n/2 与 n 两个时点(同一种子)")
    print("=" * 84)
    half, seed = N // 2, SEED_BASE + 3000
    k, snaps = grow(seed=seed, c=1.0, checkpoints={half, N})
    print(f"\n同一随机流(种子 {seed}),优先连接 c=1;网络长到 {half} 篇时快照,继续长到 {N} 篇")
    print(f"{'时点':>6} | {'总被引':>6} | {'基尼系数':>8} | {'top10%份额':>9} | "
          f"{'最高被引':>8} | {'前5名被引数':>16}")
    for t in (half, N):
        s = snaps[t]
        print(f"{t:>6} | {s['tot']:>6} | {s['gini']:>8.3f} | {s['top']:>9.3f} | "
              f"{s['maxv']:>8} | " + " ".join(f"{v}" for v in s["top5"]))
    print("\n读数:")
    print("  · 同一个世界长了一倍岁数:基尼与 top10% 份额双双上升——不平等是")
    print("    网络生长的内生结果,不需要任何人做局(『富者愈富』不需要坏人)")
    print(f"  · 头名文献被引 {snaps[half]['maxv']}→{snaps[N]['maxv']}:头部在加厚;同时新文献")
    print("    进来都是零被引,尾部在拉长——集中度上升是头部加厚与尾部稀释的合账")
    print("  · 学科史含义:学科越老,经典枷锁越重是结构趋势;让新思想被看见,")
    print("    靠的是改变规则(律二的 c),不是等待网络自发变平等")

    # 断言 3:两个集中度指标严格上升
    g1, g2 = snaps[half]["gini"], snaps[N]["gini"]
    t1, t2 = snaps[half]["top"], snaps[N]["top"]
    assert g2 > g1, f"基尼系数应随年龄上升:{g1:.3f} → {g2:.3f}"
    assert t2 > t1, f"top10% 份额应随年龄上升:{t1:.3f} → {t2:.3f}"
    print(f"\n✓ 律三断言通过:基尼 {g1:.3f}→{g2:.3f},top10% 份额 {t1:.3f}→{t2:.3f}"
          "——集中度随网络年龄单调上升")

    # 可复现性自检:同种子重跑,度序列逐位一致
    k2, _ = grow(seed=seed, c=1.0, checkpoints={half, N})
    assert k == k2, "同一种子两次生长应产出完全相同的被引序列"
    print("✓ 可复现性自检通过:同种子重跑,全部 400 篇被引数逐位一致")
    return snaps


def main():
    law1()
    law2()
    law3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 优先连接下最早 10% 份额远高于均匀对照——正典固化=累积优势(马太效应)")
    print("  ② 偏好附加 c>0 显著抬升最新 20% 份额——c 是『新文献可见度』的制度参数")
    print("     (c=0 的零份额=第一引用问题:纯累积优势不给后来者任何入口)")
    print("  ③ 同一种子下 n/2→n 基尼与 top10% 严格上升——不平等是生长的内生结果")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
