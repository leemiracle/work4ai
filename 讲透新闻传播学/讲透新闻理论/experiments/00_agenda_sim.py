# -*- coding: utf-8 -*-
"""议程设置极简模拟:两议题有限注意力竞争的传播模型。

00 章 §七/03 章层 1/04 章走廊 3 配套实验。纯标准库。

模型(新闻理论 → 传播动力学的最小翻译):
  - N 个个体,每人一份注意力 a ∈ [0,1](对议题 A 的显著度;对议题 B 为 1−a
    ——有限注意力,此消彼长,归一写在结构里)
  - 每一 tick,每个个体:
      * 以 p_media 收到一条媒体报道:话题以 M_A 的概率是 A(媒体议程 = M_A)
      * 以 p_talk 与随机同伴交谈:话题概率由双方**合计显著性**的凸放大决定
        ——u=(a_i+a_j)/2,谈 A 的概率 = u^γ/(u^γ+(1−u)^γ),γ=1.2
        (乐队花车/共鸣的最小实现:多数话题更谈得起来,少数话题更难出口;
        与沉默的螺旋的"准统计感官"同构)
      * 发生事件者按 a ← (1−α)a + α·1[话题=A] 更新
  - 公众议程 P_A = mean(a)

断言(exit 0 即通过):
  A1 语法:所有注意力 a ∈ [0,1]——有限注意力的结构体现(归一)
  A2 议程设置:网格 M_A ∈ {0.05..0.95} 上,corr(媒体议程, 公众议程) ≥ 0.95
     ——「媒体告诉人们想什么事」在零智力模型里自发涌现
     (McCombs & Shaw 1972 教堂山研究:媒体议程与公众议程相关约 0.97 的极简回声)
  A3 共鸣放大:P(0.75) > 0.80 且 P(0.25) < 0.20
     ——人际谈论放大媒体议程的偏离:公众比媒体更极端
     (0.25 的媒体偏离被放大成 >0.55 的公众偏离——"带节奏"易过头的结构原因)
  A4 赢者通吃(中间最陡):P(0.60) − P(0.40) > 0.30
     ——媒体议程 0.2 的差距,在公众议程上放大成 >0.3:中间区域的共识最不稳,
     微小的显著性优势被注意力竞争滚成一边倒

另附观察(不设断言):议程惯性——M_A 中途 0.7 → 0.3,公众议程掉头需要多少 tick
  (解释"改议程比带议程难":既有公众议程是模型的吸引子,不是白板)。

跑法: python experiments/00_agenda_sim.py
"""

import random
import statistics

N = 400          # 个体数
T = 2500         # tick 数
ALPHA = 0.10     # 单次事件对注意力的更新强度
P_MEDIA = 0.25   # 每 tick 收到媒体报道的概率
P_TALK = 0.50    # 每 tick 与人交谈的概率
GAMMA = 1.2      # 共鸣凸性:交谈概率对合计显著性的放大指数(>1 即多数放大)
SEED = 20260907


def run(m_a, seed=SEED, n=N, t=T, alpha=ALPHA, p_media=P_MEDIA, p_talk=P_TALK,
        gamma=GAMMA, flip_at=None, flip_to=None):
    """跑一次模拟。返回 (公众议程轨迹, 终态公众议程)。"""
    rng = random.Random(seed)
    att = [0.5 + rng.uniform(-0.02, 0.02) for _ in range(n)]  # 对称附近出发
    m = m_a
    traj = []
    for tick in range(t):
        if flip_at is not None and tick == flip_at:
            m = flip_to
        for i in rng.sample(range(n), n):
            r = rng.random()
            if r < p_media:                      # 媒体事件:议程 M 决定话题分布
                topic_a = rng.random() < m
                att[i] = (1 - alpha) * att[i] + alpha * (1.0 if topic_a else 0.0)
            elif r < p_media + p_talk:           # 人际交谈:合计显著性的凸放大裁决话题
                j = rng.randrange(n)
                if j == i:
                    continue
                u = (att[i] + att[j]) / 2
                pa = (u ** gamma) / (u ** gamma + (1 - u) ** gamma)
                topic_a = rng.random() < pa
                for k in (i, j):
                    att[k] = (1 - alpha) * att[k] + alpha * (1.0 if topic_a else 0.0)
        traj.append(sum(att) / n)
    return traj, traj[-1]


def pearson(xs, ys):
    """皮尔逊相关(纯标准库手写)。"""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs)
           * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den


def main():
    # ---------- A1 语法:有限注意力(归一)----------
    traj, p_end = run(0.75)
    assert 0.0 <= p_end <= 1.0
    assert 0.0 <= min(traj) and max(traj) <= 1.0
    print("[A1] 注意力归一(有限注意力):P_A=%.3f 始终在 [0,1] —— 结构保证,非检查出来" % p_end)

    # ---------- A2 议程设置:媒体显著性 → 公众议程 相关性 ----------
    grid = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    seeds = [SEED, SEED + 1]
    ms, ps = [], []
    for m in grid:
        for s in seeds:
            _, p = run(m, seed=s)
            ms.append(m)
            ps.append(p)
    r = pearson(ms, ps)
    print("[A2] 议程设置:corr(媒体议程, 公众议程) = %.4f (教堂山研究 ≈ 0.97 的极简回声)"
          % r)
    assert r >= 0.95

    p_hi = statistics.mean([run(0.75, seed=s)[1] for s in seeds])
    p_lo = statistics.mean([run(0.25, seed=s)[1] for s in seeds])
    print("      M_A=0.75 → P_A=%.3f;M_A=0.25 → P_A=%.3f(两端分别贴向 0 与 1)" % (p_hi, p_lo))

    # ---------- A3 共鸣放大:公众比媒体更极端 ----------
    print("[A3] 共鸣放大:P(0.75)=%.3f > 0.80 且 P(0.25)=%.3f < 0.20" % (p_hi, p_lo))
    assert p_hi > 0.80
    assert p_lo < 0.20
    dev_media, dev_public = 0.25, (p_hi - p_lo) / 2
    print("      媒体偏离中点 0.25 → 公众偏离中点 %.3f(放大约 %.1f 倍)"
          % (dev_public, dev_public / dev_media))

    # ---------- A4 赢者通吃:中间区域最陡 ----------
    p_60 = statistics.mean([run(0.60, seed=s)[1] for s in seeds])
    p_40 = statistics.mean([run(0.40, seed=s)[1] for s in seeds])
    print("[A4] 赢者通吃:P(0.60)−P(0.40) = %.3f > 0.30(媒体 0.2 差距 → 公众 >0.3 差距)"
          % (p_60 - p_40))
    assert (p_60 - p_40) > 0.30

    # ---------- 观察:议程惯性(不设断言)----------
    traj, _ = run(0.70, flip_at=T // 2, flip_to=0.30)
    turn = next((t for t in range(T // 2, T) if traj[t] < 0.5), None)
    if turn is not None:
        print("[观察] 议程惯性:M_A 中途 0.70→0.30,公众议程经 %d tick 才掉头"
              "(既有议程是吸引子,不是白板——改议程比带议程难)" % (turn - T // 2))
    else:
        print("[观察] 议程惯性:M_A 中途反转后公众议程 %d tick 内未掉头(粘性极强)" % (T - T // 2))

    print("\n全部断言通过:媒体显著性→公众议程的相关性、共鸣放大、中间赢者通吃,均成立。")


if __name__ == "__main__":
    main()
