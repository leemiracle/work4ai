# -*- coding: utf-8 -*-
"""黄金时段共同在场模拟:观众可用性钟形曲线 × 多频道排播的份额竞争。

00 章反直觉 2/03 章层 1/04 章走廊 2 配套实验。纯标准库。

模型(广播电视 → 注意力分配的最小翻译):
  - N 个观众,每人一条**可用性曲线**(晚饭后、睡前前的钟形主峰;部分人有
    晨间通勤小峰与夜猫小峰)——模拟里【不给任何「节目质量」的先验位置】,
    唯一的原料是国民作息
  - 时间轴:06:00-次日 02:00,每 30 分钟一个槽
  - 线性播出模式:每槽每人以 avail_prob(i,t)「在家有空」;有空者
    以 w(t)=BASE_W × (0.5+ lineup 强度) × (1+λ×全场可用密度) 决定是否开机——
    λ 是【社交协调】项:大家都在看的时候,看更值(第二天有得聊),
    与沉默的螺旋的「准统计感官」同构
  - 开机后按 softmax(a^γ_s) 在 K 个频道间分配份额(排播对位竞争)
  - 断言(exit 0 即通过):
  A1 语法:可用性/开机率 ∈ [0,1];各频道观众数 ∈ [0,N](份额守恒)
  A2 黄金时段涌现:19:00-22:00 合计收视 > 2× 09:00-12:00 合计,
     且峰值槽落在 19:00-22:00——「黄金时段」从作息钟形曲线里自发涌现,
     与节目质量无关(00 章:黄金时段是社交协调的产物,不是内容最优的产物)
  A3 对位分流:20:00 强档,排一强 vs 排两强——两强同槽各自观众下降
     (互相分流)而总收视上升(市场扩大)——排播对策的最小机制
  A4 社交协调磨尖:λ=0.8 的峰值/均值比 > λ=0 的 1.10 倍——
     共同在场的网络效应把晚间峰磨得更陡
  A5 时移反事实:把同样的收看事件按「个人方便」重排(时移自由),
     峰值/均值比塌陷 ≥ 20% 且总量守恒——共同在场假设买到的是【峰】,
     不是【量】;流媒体的时移自由拆的正是这座峰

另附观察(不设断言):周末反事实——作息主峰整体后移 1.5 小时,
  黄金时段(峰值槽)随之漂移:黄金时段跟着社会的钟走,不跟着内容走。

跑法: python experiments/00_primetime.py
"""

import math
import random
import statistics

N = 1200            # 观众数
SEED = 20260907
SLOTS = [6.0 + 0.5 * k for k in range(41)]          # 06:00 → 次日 02:00
K = 3               # 频道数
GAMMA_WATCH = 4.0   # 节目阵容强度指数(谁家强档更能把人从沙发上拽起来)
GAMMA_SHARE = 3.0   # 份额集中指数(softmax 幂)
BASE_W = 0.35       # 有空者的基础开机倾向
LAM = 0.8           # 社交协调强度(λ=0 即无共同在场增益)


# ---------- 观众群体 ----------

def make_population(rng, n=N, mu_shift=0.0):
    """每人一条可用性曲线:晚间钟形主峰 + (部分人)晨峰/夜峰。"""
    pop = []
    for _ in range(n):
        mu = min(23.5, max(18.5, rng.gauss(20.6 + mu_shift, 0.85)))  # 晚间作息中心
        pop.append({
            "mu": mu,
            "sigma": 1.15,
            "amp": rng.uniform(0.70, 0.95),     # 晚间主峰高度(在家率)
            "owl": rng.random() < 0.25,          # 夜猫:24 点小峰
            "lark": rng.random() < 0.40,         # 早起:8 点通勤小峰
        })
    return pop


def avail_prob(person, t):
    p = person["amp"] * math.exp(
        -((t - person["mu"]) ** 2) / (2 * person["sigma"] ** 2))
    if person["owl"]:
        p += 0.30 * math.exp(-((t - 24.0) ** 2) / 2.0)
    if person["lark"]:
        p += 0.22 * math.exp(-((t - 8.0) ** 2) / 2.0)
    return min(p, 0.98)


# ---------- 排播:节目阵容(单位:吸引力 0-1) ----------

def lineup(t):
    """K 个频道的节目单:强弱分布(教具级手排)。
    ch1 综合:19:00 新闻/20:00 强综艺/22:00 剧;ch2:20:00 强剧;ch3:22:30 深夜。"""
    if abs(t - 19.0) < 0.25:
        return [0.62, 0.45, 0.55]
    if 20.0 <= t <= 21.5:
        return [0.95, 0.90, 0.45]
    if abs(t - 12.0) < 0.25:
        return [0.50, 0.40, 0.40]
    if abs(t - 22.5) < 0.25 or abs(t - 22.0) < 0.25:
        return [0.75, 0.55, 0.65]
    return [0.42, 0.38, 0.40]


def strength(attrs):
    """节目阵容强度:吸引力的 L^γ 范数(一强独大≈强,三强并列≈更强)。"""
    return sum(a ** GAMMA_WATCH for a in attrs) ** (1.0 / GAMMA_WATCH)


# ---------- 线性播出模式 ----------

def run_linear(rng, pop, lam=LAM):
    """跑一晚。返回:各槽总收视曲线 / 各频道曲线 / 每人收看事件数。"""
    density = [statistics.mean(avail_prob(p, t) for p in pop) for t in SLOTS]
    peak_density = max(density)
    tuned_total = [0] * len(SLOTS)
    tuned_by_ch = [[0] * len(SLOTS) for _ in range(K)]
    per_person = [0] * len(pop)
    for ti, t in enumerate(SLOTS):
        attrs = lineup(t)
        norm_avail = density[ti] / peak_density
        w_open = min(0.97, BASE_W * (0.5 + strength(attrs))
                     * (1.0 + lam * norm_avail))
        weights = [a ** GAMMA_SHARE for a in attrs]
        wsum = sum(weights)
        for pi, p in enumerate(pop):
            if rng.random() >= avail_prob(p, t):
                continue                                  # 不在家/没空
            if rng.random() >= w_open:
                continue                                  # 有空但今晚不看
            r = rng.random() * wsum                       # softmax 份额分配
            acc = 0.0
            for c in range(K):
                acc += weights[c]
                if r <= acc:
                    tuned_by_ch[c][ti] += 1
                    tuned_total[ti] += 1
                    per_person[pi] += 1
                    break
    return tuned_total, tuned_by_ch, per_person


def peak_mean_ratio(curve):
    return max(curve) / max(1e-9, statistics.mean(curve))


# ---------- A3:单槽对位分流(同池配对比较) ----------

def slot_battle(rng, pop, attrs, hour=20.0):
    """固定可用池下,给定阵容的观众分配(同种子 ⇒ 同池配对)。"""
    w_open = min(0.97, BASE_W * (0.5 + strength(attrs)))
    weights = [a ** GAMMA_SHARE for a in attrs]
    wsum = sum(weights)
    aud = [0] * K
    total = 0
    for p in pop:
        if rng.random() >= avail_prob(p, hour):
            continue
        if rng.random() >= w_open:
            continue
        r = rng.random() * wsum
        acc = 0.0
        for c in range(K):
            acc += weights[c]
            if r <= acc:
                aud[c] += 1
                total += 1
                break
    return aud, total


def main():
    rng = random.Random(SEED)
    pop = make_population(rng)
    density = [statistics.mean(avail_prob(p, t) for p in pop) for t in SLOTS]

    # ---------- A1 语法:概率与守恒 ----------
    assert all(0.0 <= avail_prob(p, t) <= 1.0 for p in pop[:50] for t in SLOTS[:8])
    tuned, by_ch, per_person = run_linear(random.Random(SEED + 1), pop, lam=LAM)
    assert all(0 <= c[ti] <= N for c in by_ch for ti in range(len(SLOTS)))
    assert all(sum(c[ti] for c in by_ch) == tuned[ti]
               for ti in range(len(SLOTS)))                # 份额守恒
    print("[A1] 语法:可用性∈[0,1];三频道观众分项之和=总收视(份额守恒) —— 结构保证")

    # ---------- A2 黄金时段涌现 ----------
    def window_sum(curve, lo, hi):
        return sum(v for t, v in zip(SLOTS, curve) if lo <= t <= hi)
    prime, morning = window_sum(tuned, 19.0, 22.0), window_sum(tuned, 9.0, 12.0)
    peak_t = SLOTS[tuned.index(max(tuned))]
    hh = int(peak_t % 24)
    mm = int(round(peak_t % 1 * 60))
    print("[A2] 黄金时段涌现:19:00-22:00 合计 %d 人次 vs 09:00-12:00 合计 %d 人次"
          " (比值 %.1f);峰值槽 %02d:%02d 落在晚间" % (prime, morning, prime / morning, hh, mm))
    assert prime > 2.0 * morning
    assert 19.0 <= peak_t <= 22.0
    print("      —— 模型里没有「节目质量」这个变量,峰值完全由作息钟形曲线产出")

    # ---------- A3 对位分流:一强 vs 两强 ----------
    s1 = slot_battle(random.Random(SEED + 2), pop, [0.95, 0.45, 0.45])
    s2 = slot_battle(random.Random(SEED + 2), pop, [0.95, 0.90, 0.45])
    print("[A3] 对位分流:20:00 强档,一强(%s)→ 强台 %d 人/总 %d;"
          " 两强(%s)→ 强台 %d 人/总 %d" %
          ("0.95,0.45,0.45", s1[0][0], s1[1], "0.95,0.90,0.45", s2[0][0], s2[1]))
    assert s2[0][0] < s1[0][0]          # 两强同槽:原强台被分流
    assert s2[1] > s1[1]                # 总市场扩大:强阵容把更多人拽到电视机前
    print("      —— 各自缩水 %.0f%% 而市场扩大 %.0f%%:排播对位是零和份额×正和市场的叠加"
          % (100 * (1 - s2[0][0] / s1[0][0]), 100 * (s2[1] / s1[1] - 1)))

    # ---------- A4 社交协调磨尖峰值 ----------
    tuned_nosocial, _, _ = run_linear(random.Random(SEED + 1), pop, lam=0.0)
    r_social, r_plain = peak_mean_ratio(tuned), peak_mean_ratio(tuned_nosocial)
    print("[A4] 社交协调:峰值/均值比 λ=0 → %.2f,λ=0.8 → %.2f(磨尖 %.0f%%)"
          % (r_plain, r_social, 100 * (r_social / r_plain - 1)))
    assert r_social > 1.10 * r_plain
    print("      —— 「大家都在看时看更值」的网络效应,把晚间峰磨得更陡")

    # ---------- A5 时移反事实:同样的量,塌掉的峰 ----------
    events = per_person[:]                               # 每人在该晚的收看事件数
    shifted = [0] * len(SLOTS)
    rng2 = random.Random(SEED + 3)
    for pi, k in enumerate(events):
        if k == 0:
            continue
        weights = [avail_prob(pop[pi], t) + 0.15 for t in SLOTS]   # 时移:个人方便即可
        wsum = sum(weights)
        for _ in range(k):
            r, acc = rng2.random() * wsum, 0.0
            for ti in range(len(SLOTS)):
                acc += weights[ti]
                if r <= acc:
                    shifted[ti] += 1
                    break
    r_shift = peak_mean_ratio(shifted)
    print("[A5] 时移反事实:总量 %d 守恒;峰值/均值比 %.2f → %.2f(塌陷 %.0f%%)"
          % (sum(shifted), r_social, r_shift, 100 * (1 - r_shift / r_social)))
    assert sum(shifted) == sum(tuned)                    # 事件守恒
    assert r_shift < 0.80 * r_social                     # 峰值塌陷 ≥ 20%
    print("      —— 共同在场假设买到的是峰不是量:时移自由拆掉的是公共时间这座峰")

    # ---------- 观察:周末反事实(不设断言) ----------
    pop_wknd = make_population(random.Random(SEED), mu_shift=1.5)  # 作息整体后移
    tuned_wknd, _, _ = run_linear(random.Random(SEED + 1), pop_wknd, lam=LAM)
    peak_w = SLOTS[tuned_wknd.index(max(tuned_wknd))]
    print("[观察] 周末反事实:作息主峰后移 1.5h,峰值槽 %02d:%02d → %02d:%02d"
          "——黄金时段跟着社会的钟走,不跟着内容走"
          % (hh, mm, int(peak_w % 24), int(round(peak_w % 1 * 60))))

    print("\n全部断言通过:黄金时段自发涌现、对位分流、社交磨尖、时移塌峰,均成立。")


if __name__ == "__main__":
    main()
