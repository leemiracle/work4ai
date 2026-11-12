# -*- coding: utf-8 -*-
"""信任、辟谣与议程:公共关系学实验三律。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(三具结构引擎的严格
可构造性)、04-公共关系学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖。

三律:
  律一 信任账户的不对称恢复(信任=贴现的履约积分和):
      每期正常履约记 +a,历史按贴现率 δ 折算(信任=组织-公众关系的第一
      指标,Hon-Grunig 五维之首);一次危机期记 −C。恢复判据:回到危机前
      水平一个履约分(ε=a)以内。
      断言:危机一瞬抹掉 a+C 个信任单位(=C/a+1 期的进账),恢复所需
      无事故期数 ≈ ln(1+C/a)/ln(1/δ) ≫ 1(C/a 的量级);且 δ 越大
      (记忆越长)恢复越慢——信任烧起来一秒钟,攒回来要年头。
  律二 辟谣时间窗(谣言 SI × 延迟竞争):
      谣言按 SI 动力学传播,接触率 β(t)=β0·e^{−λt} 随议题注意衰减
      (Downs 式注意周期,通说);辟谣在延迟 d 后以相同动力学进入竞争,
      信谣者接触辟谣转为"纠正态"(吸收)。
      断言:最终"信谣未纠正"份额随 d 单调上升;d 落在谣言增速峰值 t*
      之后,纠正份额骤降——辟谣要在波峰之前,落在峰后是给历史做注脚。
  律三 议程设置的时间签名(媒体议程→公众议程的领先-滞后结构):
      媒体议程由外生事件流驱动(一阶 AR);公众议程对媒体议程带 1 期
      延迟响应+自身惯性。
      断言:互相关在 lag=1 最大——corr(m_{t−1}, p_t) > corr(m_t, p_t)
      且 > corr(m_{t+1}, p_t)——媒体先动,公众跟进一期。

跑法: python -u experiments/trust_and_agenda.py
"""

import math
import random

# ==================== 律一:信任账户的不对称恢复 ====================

A_CREDIT = 1.0      # 每期正常履约的信任进账
C_CRISIS = 8.0      # 一次危机的信任扣减(C/a = 8:危机烧掉八个履约期的进账)
PRE_PERIODS = 1200  # 危机前正常履约期数(充分逼近稳态,δ^1200 已可忽略)
DELTAS = (0.90, 0.95, 0.98)   # 贴现率:公众记忆长度的三个档位


def trust_account(delta, a=A_CREDIT, c=C_CRISIS):
    """信任账户:T ← δT + x(x 正常期=+a,危机期=−C)。

    返回 (危机前水平 T_pre, 危机后水平 T_hit, 瞬时跌幅, 恢复期数 k)。
    恢复判据:回到危机前一个履约分(ε=a)以内。
    解析:T_pre ≈ a/(1−δ)(稳态);危机后缺口 = (a+c)·δ^k,
    故 k ≈ ln(1+C/a)/ln(1/δ)。
    """
    T = 0.0
    for _ in range(PRE_PERIODS):
        T = delta * T + a
    T_pre = T
    T = delta * T - c          # 危机期:这一期不但没挣到 +a,还记了 −C
    T_hit = T
    k = 0
    while T < T_pre - a:
        T = delta * T + a
        k += 1
        assert k < 10 ** 7, "恢复期数失控(参数或判据写错)"
    return T_pre, T_hit, T_pre - T_hit, k


def act1():
    print("=" * 84)
    print("律一 信任账户的不对称恢复(每期履约 +a=%g,危机记 −C=%g,贴现率 δ)"
          % (A_CREDIT, C_CRISIS))
    print("=" * 84)
    print("\n信任 = 贴现的履约积分和:T ← δT + x;稳态容量 a/(1−δ)——")
    print("记忆越长(δ 越大),账户容量越大,同一笔伤疤也保存得越久\n")
    print(f"{'δ':>5} {'稳态T=a/(1−δ)':>13} {'危机后T':>9} {'瞬时跌幅':>9}"
          f" {'恢复期数k':>9} {'解析预测':>9}")
    results = {}
    for delta in DELTAS:
        T_pre, T_hit, drop, k = trust_account(delta)
        k_pred = math.ceil(math.log(1 + C_CRISIS / A_CREDIT)
                           / math.log(1.0 / delta))
        results[delta] = (T_pre, T_hit, drop, k, k_pred)
        print(f"{delta:>5.2f} {A_CREDIT / (1 - delta):>13.1f} {T_hit:>9.2f}"
              f" {drop:>9.2f} {k:>9d} {k_pred:>9d}")
    print("\n读数:")
    print("  · 一次危机(1 期)瞬时抹掉的信任 = a + C = %g 个单位——"
          % (A_CREDIT + C_CRISIS))
    print("    相当于 C/a = %g 个履约期的进账一次性烧掉;" % (C_CRISIS / A_CREDIT))
    print("  · 每期正常履约只挣 +a=%g:恢复不是把烧掉的一次性存回来,"
          "而是靠" % A_CREDIT)
    print("    无事故期一点点攒——缺口以 δ^k 几何收窄,k ≈ ln(1+C/a)/ln(1/δ);")
    print("  · δ 0.90→0.98(记忆变长),恢复期数 21→109:"
          "记忆越长,伤疤消得越慢;")
    print("  · 信任烧起来一秒钟,攒回来要年头(声誉的时间不对称)")

    # 断言 1:瞬时跌幅=a+C;恢复期数与解析解一致;随 δ 单调变慢;≫ 1 且 C/a 量级
    for delta in DELTAS:
        T_pre, T_hit, drop, k, k_pred = results[delta]
        assert abs(drop - (A_CREDIT + C_CRISIS)) < 1e-6, \
            f"瞬时跌幅应=a+C,实测 {drop:.6f}"
        assert k == k_pred, f"δ={delta}:恢复期数应贴解析解 {k_pred},实测 {k}"
    ks = [results[d][3] for d in DELTAS]
    assert all(x < y for x, y in zip(ks, ks[1:])), \
        f"δ 越大恢复应越慢,实测 {ks}"
    assert ks[0] >= C_CRISIS / A_CREDIT, \
        f"恢复期数应是 C/a 的量级(≥{C_CRISIS / A_CREDIT:.0f}),实测 {ks[0]}"
    asym = ks[0]
    print(f"\n✓ 律一断言通过:跌幅恒为 a+C={A_CREDIT + C_CRISIS:.0f};恢复期数"
          f" {ks[0]}/{ks[1]}/{ks[2]}(δ=0.90/0.95/0.98)与解析解逐一相等;"
          f"不对称比 {asym}:1——1 期的危机,{asym} 期的偿还")


# ==================== 律二:辟谣时间窗 ====================

BETA0 = 0.6    # 初始接触率(谣言与辟谣共用——相同动力学)
LAMBDA = 0.08  # 议题注意衰减率(Downs 式注意周期:公共注意力会移开)
SEED = 0.01    # 谣言种子份额(辟谣以同额种子进场,公平竞争)
DT = 0.02
T_END = 80.0
DELAYS = (0.0, 4.0, 8.0, 12.0, 16.0, 20.0)


def rumor_peak_time():
    """无辟谣对照:谣言增速峰值时刻(闭式解的数值定位 vs 模拟)。

    闭式解:logit(I) = logit(s0) + (β0/λ)(1−u),u = e^{−λt};
    dI/dt = β·I(1−I) 的峰值条件 β'·I(1−I) + β²·I(1−I)(1−2I) = 0 给出
    I* = 1/2 − λ/(2β)——注意衰减把峰值压到 I≈0.36(渗透半程之前);
    代回闭式解得根方程 logit(s0) + (β0/λ)(1−u) = ln((β0u−λ)/(β0u+λ)),
    在 u ∈ (λ/β0, 1] 上二分求根(f(lo)→+∞,f(hi)<0)。
    """
    logit0 = math.log(SEED / (1 - SEED))

    def f(u):
        return logit0 + (BETA0 / LAMBDA) * (1 - u) \
            - math.log((BETA0 * u - LAMBDA) / (BETA0 * u + LAMBDA))

    lo, hi = LAMBDA / BETA0 + 1e-9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    tstar = -math.log((lo + hi) / 2) / LAMBDA
    Ir, S = SEED, 1.0 - SEED
    t, best_t, best_rate = 0.0, 0.0, -1.0
    for _ in range(int(T_END / DT)):
        rate = BETA0 * math.exp(-LAMBDA * t) * Ir * S
        if rate > best_rate:
            best_rate, best_t = rate, t
        dI = DT * rate
        Ir += dI
        S -= dI
        t += DT
    return tstar, best_t


def debunk_run(d):
    """谣言 SI × 延迟 d 的辟谣竞争。

    分室:S(未知)→I_r(信谣);S→I_d(辟谣持有,自 t=d 起,同种子同动力学);
    I_r→C(纠正态,吸收):信谣者接触辟谣持有者即被纠正。
    返回 (信谣未纠正 I_r, 辟谣持有 I_d, 纠正 C)。
    """
    Ir, Id, C = SEED, 0.0, 0.0
    S = 1.0 - SEED
    t = 0.0
    seeded = (d <= 0.0)
    if seeded:
        S -= SEED
        Id = SEED
    for _ in range(int(T_END / DT)):
        beta = BETA0 * math.exp(-LAMBDA * t)
        if not seeded and t >= d:
            S -= SEED
            Id = SEED
            seeded = True
        grow_r = beta * Ir * S      # 谣言从未知池招募
        grow_d = beta * Id * S      # 辟谣从未知池招募(相同动力学)
        corr = beta * Ir * Id       # 信谣者×辟谣持有者接触→纠正
        Ir += DT * (grow_r - corr)
        Id += DT * grow_d
        C += DT * corr
        S -= DT * (grow_r + grow_d)
        t += DT
    assert S > -1e-6, f"数值失稳:S={S}"
    return Ir, Id, C


def act2():
    print("\n" + "=" * 84)
    print(f"律二 辟谣时间窗(谣言 SI;β(t)=β0·e^(−λt)={BETA0}·e^(−{LAMBDA}t) "
          "注意衰减;辟谣延迟 d 后同动力学进场)")
    print("=" * 84)
    tstar, best_t = rumor_peak_time()
    print(f"\n谣言增速峰值:解析 t* = {tstar:.2f},无辟谣对照模拟峰值"
          f" t = {best_t:.2f}(对表一致)")
    print(f"\n{'辟谣延迟d':>8} {'信谣未纠正':>10} {'纠正态':>8} {'辟谣持有':>8}"
          f"  位置")
    results = {}
    for d in DELAYS:
        Ir, Id, C = debunk_run(d)
        results[d] = (Ir, Id, C)
        pos = "峰前" if d < tstar else "峰后"
        print(f"{d:>8.1f} {Ir:>10.3f} {C:>8.3f} {Id:>8.3f}  {pos}")
    print("\n读数:")
    print("  · 信谣未纠正份额随辟谣延迟 d 单调上升——每晚一步,谣言多占一步;")
    print("  · 公共注意力按 e^{−λt} 移开(Downs 式注意周期):辟谣进场越晚,")
    print("    剩下的注意力能量(e^{−λd})越少,既传不开也纠不动;")
    print("  · d 落在谣言增速峰值 t*≈{:.1f} 之前,纠正态还成气候;落在峰后,"
          .format(tstar))
    print("    纠正份额骤降——辟谣要在波峰之前,落在峰后是给历史做注脚")

    # 断言 2:单调上升;峰后骤降;峰值解析对表
    uncorr = [results[d][0] for d in DELAYS]
    corr = [results[d][2] for d in DELAYS]
    assert abs(best_t - tstar) <= 0.5, \
        f"模拟峰值应贴解析解,实测 {best_t:.2f} vs {tstar:.2f}"
    assert all(x < y for x, y in zip(uncorr, uncorr[1:])), \
        f"信谣未纠正应随 d 单调上升,实测 {['%.3f' % v for v in uncorr]}"
    assert uncorr[-1] >= 4 * uncorr[0], \
        "最晚辟谣的信谣未纠正应≥最早情形的 4 倍"
    before = [results[d][2] for d in DELAYS if d < tstar]
    after = [results[d][2] for d in DELAYS if d > tstar]
    mean_before = sum(before) / len(before)
    mean_after = sum(after) / len(after)
    assert mean_before >= 3.0 * mean_after, \
        f"峰前辟谣的平均纠正份额应≥峰后 3 倍,实测 {mean_before:.3f} vs {mean_after:.3f}"
    assert corr[0] >= 2.5 * corr[-1], "立即辟谣的纠正份额应≥最晚的 2.5 倍"
    print(f"\n✓ 律二断言通过:信谣未纠正 {uncorr[0]:.2f}→{uncorr[-1]:.2f}"
          f" 随 d 单调上升({uncorr[-1] / uncorr[0]:.1f} 倍);纠正份额峰前平均"
          f"{mean_before:.2f} vs 峰后平均{mean_after:.2f}(骤降"
          f"{mean_before / mean_after:.1f} 倍);t*={tstar:.2f} 解析与模拟对表")


# ==================== 律三:议程设置的时间签名 ====================

PHI_M, PHI_P, ALPHA = 0.6, 0.5, 0.5   # 媒体惯性 / 公众惯性 / 公众对媒体(滞后1期)的响应
SIG_E, SIG_N = 1.0, 0.35              # 事件流强度 / 公众噪声
T_OBS, BURN = 4000, 200               # 观测期数 / 预热期(丢弃)
LAGS = tuple(range(-3, 4))


def pearson(xs, ys):
    """皮尔逊相关(手写,免依赖)。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy)


def agenda_run():
    """媒体议程 m(一阶 AR×外生事件流)与公众议程 p(惯性+滞后 1 期响应)。"""
    rng = random.Random(840543)
    m, p = 0.0, 0.0
    ms, ps = [], []
    for t in range(BURN + T_OBS):
        e = SIG_E * rng.gauss(0.0, 1.0)     # 常规事件流
        if rng.random() < 0.05:
            e *= 2.5                          # 偶发大事件(冲击×2.5)
        m_next = PHI_M * m + e                # 媒体议程:事件流驱动+自身惯性
        p_next = (PHI_P * p + ALPHA * m       # 公众议程:对 m 滞后 1 期响应
                  + SIG_N * rng.gauss(0.0, 1.0))
        if t >= BURN:
            ms.append(m_next)
            ps.append(p_next)
        m, p = m_next, p_next
    return ms, ps


def act3():
    print("\n" + "=" * 84)
    print("律三 议程设置的时间签名(媒体议程一阶 AR;公众议程=惯性+滞后 1 期响应)")
    print("=" * 84)
    ms, ps = agenda_run()
    n = len(ms)
    print(f"\n观测 {n} 期(预热 {BURN} 期已丢弃);r[k] = corr(m_(t−k), p_t):"
          " k>0 媒体领先,k<0 媒体落后\n")
    print(f"{'lag k':>6} {'互相关r':>8}  读数")
    r = {}
    for k in LAGS:
        pairs_m = ms[max(0, -k):n - max(0, k)]
        pairs_p = ps[max(0, k):n - max(0, -k)]
        r[k] = pearson(pairs_m, pairs_p)
        if k == 1:
            note = "◀ 时间签名:媒体先动,公众跟进一期"
        elif k == 0:
            note = "同期相关(零阶错觉:看起来像'同步')"
        elif k == -1:
            note = "媒体落后 1 期(公众先于媒体?不成立)"
        else:
            note = ""
        print(f"{k:>6d} {r[k]:>8.3f}  {note}")
    print("\n读数:")
    print("  · 互相关峰值在 lag=+1:corr(m_(t−1), p_t) 同时高于同期相关")
    print("    与反向滞后——领先-滞后结构是方向论证的必要线索(不是充分证明);")
    print("  · 同期相关也不低(媒体议程自身有惯性,m_t 携带 m_(t−1) 的记忆),")
    print("    只看零阶相关会误读成'媒体与公众同步起舞';")
    print("  · 经典议程设置研究的滞后量级为数周到数月(通说);本实验的")
    print("    '期'是抽象时间单位,签名(峰值在领先 1 期处)才是可迁移的结论")

    # 断言 3:lag=1 处最大,且高于同期与反向滞后
    best = max(LAGS, key=lambda k: r[k])
    assert best == 1, f"互相关峰值应在 lag=+1,实测 lag={best}"
    assert r[1] > r[0] + 0.05, \
        f"corr(m_(t−1),p_t) 应明显高于同期,实测 {r[1]:.3f} vs {r[0]:.3f}"
    assert r[1] > r[2], f"lag=1 应高于 lag=2(媒体自相关的肩膀),实测反超"
    assert r[1] > r[-1] + 0.2, \
        f"应明显高于反向滞后,实测 {r[1]:.3f} vs {r[-1]:.3f}"
    print(f"\n✓ 律三断言通过:r[+1]={r[1]:.3f} 为全表最大(>同期 {r[0]:.3f},"
          f">lag2 {r[2]:.3f},>反向 {r[-1]:.3f})——媒体先动,公众跟进一期")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 信任=贴现的履约积分和:1 期危机烧掉 a+C=9 个单位,恢复需"
          " 21/43/109 期")
    print("     (δ=0.90/0.95/0.98,贴解析解;记忆越长恢复越慢):"
          "信任烧起来一秒钟,攒回来要年头")
    print("  ② 辟谣时间窗:信谣未纠正随延迟 d 单调上升(0.08→0.92,11 倍);"
          "d 越过谣言")
    print("     增速峰值 t*≈9.6 后纠正份额骤降(峰前均值 0.18 vs 峰后 0.02):"
          "辟谣要在波峰")
    print("     之前,落在峰后是给历史做注脚")
    print("  ③ 议程设置的时间签名:互相关峰值在 lag=+1(媒体领先 1 期,"
          "高于同期/肩膀/反向):")
    print("     媒体先动,公众跟进一期")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
