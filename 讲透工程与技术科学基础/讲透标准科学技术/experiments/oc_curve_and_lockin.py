# -*- coding: utf-8 -*-
"""
抽样 OC 曲线与标准锁定动力学(教学版)
======================================

家族实验 · 讲透标准科学技术(GB/T 41050)
主题呼应走廊 C1:把「验收的严格度」与「先发优势」各写成一个可计算的模型。

模型:
  [律1] 计数抽样方案 (n, Ac) 的接受概率(批缺陷率 p)
        P_a(p) = Σ_{k=0}^{Ac} C(n,k)·p^k·(1−p)^(n−k)
        ——精确二项,逐项递推,不用正态近似。
  [律2] 两点定样本量:生产方风险点 (p1=AQL, α) 要求 P_a(p1)≥1−α(给 n 上限),
        使用方风险点 (p2=LTPD, β) 要求 P_a(p2)≤β(给 n 下限)。
        Ac=0 时两式各是 (1−p)^n 的单调式:上限 ln(1−α)/ln(1−p1),
        下限 ln(β)/ln(1−p2)——单自由度钉不住两个风险点;
        LTPD 单点设计 n_min=ln(β)/ln(1−p2):5%→45, 3%→76,
        1%→230(理论值 229.1 取整)。
  [律3] 标准锁定动力学(两不兼容标准,份额 s 与 1−s):
        ds/dt = k·s(1−s)·[a·(s−1/2) + q]
        a=网络效应强度,s−1/2 项=装机量吸引,q=质量差(可负)。
        内点不动点 s* = 1/2 − q/a 即临界份额:
        劣标准(q<0)先发份额超过 s* 仍锁定胜出,低于 s* 被翻盘
        ——QWERTY 叙事的机制化(00 章故事框三;优势幅度争议按文献通说)。

三个实验(全部断言自验证):
  [1] P_a 随 p 单调降;n 增大曲线变陡(最大斜率增大+P_a=50% 点左移);
      附蒙特卡洛互证(模拟抽样批,接受频率≈理论 P_a)。
  [2] Ac=0 的两点冲突(上限 5 < 下限 45,零接受方案钉不住买卖双方风险);
      LTPD=1% 处 n=230(理论 229.1)成立;两点越靠近(5%→3%→2%),
      钉住双方风险的最小方案样本量超比例激增(135→327→…)。
  [3] 劣标准临界锁定:q=−0.1 时 s*=0.6,s0=0.65 锁定、s0=0.55 翻盘;
      数值扫描的临界份额与解析式对表。

只用标准库 math/random(蒙特卡洛部分);固定随机种子,可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random


# ----------------------------------------------------------------模型件

def pa_binom(n, ac, p):
    """计数抽样方案 (n, Ac) 在批缺陷率 p 处的接受概率。

    P_a(p) = Σ_{k=0}^{Ac} C(n,k) p^k (1−p)^(n−k)
    逐项递推:t_0=(1−p)^n,t_{k+1} = t_k·(n−k)/(k+1)·p/(1−p)。
    """
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 1.0 if ac >= n else 0.0
    q = 1.0 - p
    term = q ** n
    total = term
    for k in range(ac):
        term = term * (n - k) / (k + 1) * p / q
        total += term
    return total


def oc_table(n, ac, ps):
    """一行 OC 采样:给定 (n,Ac),返回各 p 处的 P_a。"""
    return [pa_binom(n, ac, p) for p in ps]


def max_slope(n, ac, p_lo=1e-4, p_hi=0.5, m=2000):
    """OC 曲线最大斜率 |dP_a/dp|(数值网格)——判别力的量度。"""
    step = (p_hi - p_lo) / m
    prev = pa_binom(n, ac, p_lo)
    best = 0.0
    for i in range(1, m + 1):
        cur = pa_binom(n, ac, p_lo + i * step)
        best = max(best, abs(cur - prev) / step)
        prev = cur
    return best


def p50_of(n, ac):
    """P_a=50% 对应的缺陷率 p50(二分)。Ac=0 有解析式 1−0.5^(1/n)。"""
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if pa_binom(n, ac, mid) >= 0.5:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def n_min_zero_accept(ltpd, beta):
    """LTPD 单点零接受设计:最小 n 使 (1−ltpd)^n ≤ β。"""
    n = 1
    while (1.0 - ltpd) ** n > beta:
        n += 1
    return n


def two_point_plan(p1, alpha, p2, beta, ac_max=18, n_max=3000):
    """钉住两点风险的最小 (n, Ac) 方案搜索。

    对每个 Ac:使用方约束给 n 下限(越大越易满足),
    生产方约束给 n 上限(越小越易满足);下限≤上限者可行。
    返回 (best_n, best_ac);无解返回 (None, None)。
    """
    assert p1 < p2, "两点方向:AQL 点应在 LTPD 点左侧"
    best = (None, None)
    for ac in range(0, ac_max + 1):
        n_lo, n_hi = None, 0
        for n in range(1, n_max + 1):          # 使用方下限:P_a(p2)≤β
            if pa_binom(n, ac, p2) <= beta:
                n_lo = n
                break
        if n_lo is None:
            continue                            # 该 Ac 连 n_max 都压不住 β,更大的 Ac 更压不住?继续搜
        for n in range(1, n_max + 1):          # 生产方上限:P_a(p1)≥1−α
            if pa_binom(n, ac, p1) < 1.0 - alpha:
                n_hi = n - 1
                break
        else:
            n_hi = n_max
        if n_lo <= n_hi:
            if best[0] is None or n_lo < best[0]:
                best = (n_lo, ac)
    return best


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """OC 曲线:单调降 + n 增大变陡 + 蒙特卡洛互证。"""
    section("实验 [1] OC 曲线:P_a(p) 单调降,n 增大曲线变陡")

    # (a) 单调降:两个代表方案逐点验证
    for n, ac in ((13, 0), (80, 2)):
        ps = [0.005 * (i + 1) for i in range(40)]      # p=0.5%..20%
        pas = oc_table(n, ac, ps)
        mono = all(pas[i] > pas[i + 1] - 1e-12 for i in range(len(ps) - 1))
        assert mono, f"实验[1]:(n={n},Ac={ac}) P_a 不单调降"
        print(f"(a) (n={n}, Ac={ac}):P_a 在 p∈[0.5%,20%] 上严格单调降 ✓")

    # (b) OC 采样表:三个方案并排读
    ps = [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10]
    plans = [(13, 0), (50, 1), (230, 0)]
    print("(b) OC 采样表(接受概率 P_a):")
    head = "   p     " + "".join(f"  n={n},Ac={ac}  " for n, ac in plans)
    print(head)
    for p in ps:
        row = f"  {p*100:4.1f}%  "
        for n, ac in plans:
            row += f"    {pa_binom(n, ac, p):.4f}    "
        print(row)
    # 教学读数:(13,0) 在 p=1% 处接受率仍有 88%(对好批很狠),p=5% 处还有 51%(对坏批太松)
    assert pa_binom(13, 0, 0.01) > 0.85 and 0.4 < pa_binom(13, 0, 0.05) < 0.6, \
        "实验[1]:(13,0) 的『两头不讨好』读数应如教材通说"

    # (c) n 增大→最大斜率增大(判别力升):Ac=0/1/2 三族各自验证
    print("(c) n 增大→OC 最大斜率增大(判别力升):")
    print("   Ac    n=13     n=50     n=200")
    for ac in (0, 1, 2):
        slopes = [max_slope(n, ac) for n in (13, 50, 200)]
        assert slopes[0] < slopes[1] < slopes[2], \
            f"实验[1]:Ac={ac} 最大斜率未随 n 递增"
        print(f"   {ac}   {slopes[0]:7.2f} {slopes[1]:7.2f} {slopes[2]:7.2f}")

    # (d) Ac=0 解析互证:max|dP/dp|=n(p→0);p50=1−0.5^(1/n)
    for n in (13, 50, 200):
        slope0 = n                        # Ac=0 的 dP/dp=−n(1−p)^(n−1),p→0 时最大=n
        p50_exact = 1.0 - 0.5 ** (1.0 / n)
        assert abs(p50_of(n, 0) - p50_exact) < 1e-9, \
            f"实验[1]:n={n} 的 p50 数值与解析式不合"
    p50s = [p50_of(n, 0) for n in (13, 50, 200)]
    assert p50s[0] > p50s[1] > p50s[2], "实验[1]:p50 未随 n 左移"
    print(f"(d) Ac=0:p50(n=13)={p50s[0]:.4f} > p50(50)={p50s[1]:.4f} > "
          f"p50(200)={p50s[2]:.4f}(50% 接受点左移=质量要求收紧)")

    # (e) 蒙特卡洛互证:n=50, Ac=1, p=3%,批接受频率≈理论 P_a
    n, ac, p, batches = 50, 1, 0.03, 30000
    accept = 0
    for _ in range(batches):
        defects = sum(1 for _ in range(n) if random.random() < p)
        if defects <= ac:
            accept += 1
    freq, theo = accept / batches, pa_binom(n, ac, p)
    print(f"(e) MC({batches} 批,n={n},Ac={ac},p={p:g}):"
          f"接受频率 {freq:.4f} ≈ 理论 P_a {theo:.4f}")
    assert abs(freq - theo) < 0.01, "实验[1]:蒙特卡洛接受频率偏离理论值"
    print("断言通过:①P_a 单调降 ②n 增大→最大斜率增大、p50 左移(变陡)"
          "③MC 与精确二项一致——严格度住在曲线形状里,不在单点接受率里")


# ----------------------------------------------------------------实验 2

def experiment2():
    """两点定样本量:Ac=0 两点冲突;LTPD=1% 处 n=230(理论 229.1);两点靠近样本量激增。"""
    section("实验 [2] 两点定样本量:AQL/LTPD 风险点的样本量代价")

    p1, alpha = 0.01, 0.05          # 生产方风险点:AQL=1%,好批误拒≤5%
    p2, beta = 0.05, 0.10           # 使用方风险点:LTPD=5%,坏批溜过≤10%

    # (a) Ac=0 的两限:上限(保生产方)与下限(保使用方)
    n_hi = math.floor(math.log(1 - alpha) / math.log(1 - p1))   # (1−p1)^n≥1−α
    n_lo_exact = math.log(beta) / math.log(1 - p2)              # (1−p2)^n≤β
    n_lo = math.ceil(n_lo_exact)
    print(f"(a) Ac=0 两限:生产方约束 (1−p1)^n≥1−α → n≤{n_hi};"
          f"使用方约束 (1−p2)^n≤β → n≥{n_lo}")
    assert (1 - p1) ** n_hi >= 1 - alpha and (1 - p1) ** (n_hi + 1) < 1 - alpha
    assert (1 - p2) ** n_lo <= beta and (1 - p2) ** (n_lo - 1) > beta
    print(f"    验证:(0.99)^{n_hi}={(1-p1)**n_hi:.4f}≥0.95;"
          f"(0.95)^{n_lo}={(1-p2)**n_lo:.4f}≤0.10")
    assert n_lo > n_hi, "实验[2]:此处应演示两点冲突"
    print(f"    下限 {n_lo} > 上限 {n_hi} ⇒ **零接受方案(Ac=0)钉不住两个风险点**:"
          "单自由度的 OC 曲线不能同时过 (1%,95%) 与 (5%,10%) 两点"
          "——抽样标准族必须给 (n,Ac) 成对档位的数学理由")

    # (b) LTPD 单点零接受设计:n_min=ln β/ln(1−LTPD)
    print("(b) LTPD 单点设计(β=10%):LTPD→最小 n(零接受):")
    print("   LTPD   n_min   核验 (1−p)^n")
    for ltpd in (0.05, 0.03, 0.01):
        n = n_min_zero_accept(ltpd, beta)
        assert (1 - ltpd) ** n <= beta and (1 - ltpd) ** (n - 1) > beta
        print(f"  {ltpd*100:4.0f}%   {n:5d}   {(1-ltpd)**n:.5f}≤0.10 ✓")
    n230 = n_min_zero_accept(0.01, beta)
    assert n230 == 230, \
        "实验[2]:LTPD=1% 的零接受最小样本量应为 230(理论 229.1 取整)"
    n45, n76 = n_min_zero_accept(0.05, beta), n_min_zero_accept(0.03, beta)
    print(f"    断言:LTPD=1% 处 n={n230}(理论 ln0.10/ln0.99="
          f"{math.log(beta)/math.log(0.99):.1f},取整即 230;"
          "(0.99)^229≈0.1001>0.10 不达标);两点从 5% 靠近到 3% 再到 1%,"
          f"n 从 {n45}→{n76}→{n230}(超比例激增,n∝1/p)")
    assert n76 > 1.5 * n45 and n230 > 4 * n45

    # (c) 真钉两点:网格搜 (n,Ac),最小样本方案
    n5, ac5 = two_point_plan(p1, alpha, p2, beta)
    print(f"(c) 钉住两点 (AQL=1%,α=5%)+(LTPD=5%,β=10%) 的最小方案:"
          f"(n={n5}, Ac={ac5})")
    assert n5 is not None and 125 <= n5 <= 145 and ac5 == 3, \
        "实验[2]:(1%,5%) 两点最小方案应在 Ac=3、n≈135 附近(教材量级)"
    assert pa_binom(n5, ac5, p1) >= 1 - alpha and pa_binom(n5, ac5, p2) <= beta
    print(f"    核验:P_a(1%)={pa_binom(n5, ac5, p1):.4f}≥0.95,"
          f"P_a(5%)={pa_binom(n5, ac5, p2):.4f}≤0.10 ✓"
          "——比零接受单点(45 件)多付三倍样本,买到的是『好批不被冤杀』")

    # (d) 两点越靠近,样本量激增(一致性测试的样本量代价)
    n3, _ = two_point_plan(p1, alpha, 0.03, beta)
    n2, _ = two_point_plan(p1, alpha, 0.02, beta)
    print(f"(d) 两点靠近:5%→3% 最小 n={n3};5%→2% 最小 n={n2}")
    assert n3 >= 2 * n5, "实验[2]:两点靠近到 3% 样本量应翻倍以上"
    assert n2 >= 1.6 * n3, "实验[2]:两点靠近到 2% 样本量应继续激增"
    print(f"    {n5}→{n3}→{n2}:判别两类越来越像的批,代价超线性——"
          "**一致性测试的样本量账**:要更细的分辨力,先付更多样本")
    print(f"断言通过:①Ac=0 两点冲突(5<45)②LTPD=1% 处 n=230(理论 229.1)成立 "
          f"③两点 5%→3%→2% 最小样本 {n5}→{n3}→{n2} 超比例激增")


# ----------------------------------------------------------------实验 3

def experiment3():
    """标准锁定动力学:劣标准靠先发份额过临界值锁定胜出。"""
    section("实验 [3] 锁定动力学:劣标准(q<0)的临界份额 s*=1/2−q/a")

    a = 1.0                              # 网络效应强度(速度常数 k 取 1)
    q = -0.1                             # 标准 A 比标准 B 质量劣 0.1
    s_star = 0.5 - q / a                  # 解析临界份额

    def drift(s, a, q):
        return s * (1.0 - s) * (a * (s - 0.5) + q)

    def integrate(s0, a, q, dt=0.005, t_end=300.0):
        """RK4 积分份额轨道;份额天然有界 [0,1],数值上再夹一次。"""
        s, steps = s0, int(t_end / dt)
        for _ in range(steps):
            k1 = drift(s, a, q)
            k2 = drift(max(0.0, min(1.0, s + 0.5 * dt * k1)), a, q)
            k3 = drift(max(0.0, min(1.0, s + 0.5 * dt * k2)), a, q)
            k4 = drift(max(0.0, min(1.0, s + dt * k3)), a, q)
            s = s + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            s = max(0.0, min(1.0, s))
        return s

    # (a) 两条命运线:s0 过临界→锁定;低于→翻盘
    s_hi, s_lo = 0.65, 0.55
    end_hi, end_lo = integrate(s_hi, a, q), integrate(s_lo, a, q)
    print(f"(a) a={a:g}, q={q:g}(A 劣 0.1)⇒ 临界份额 s*={s_star:.2f}")
    print(f"    s0={s_hi:g} → s(∞)={end_hi:.4f}(劣标准 A 锁定胜出)")
    print(f"    s0={s_lo:g} → s(∞)={end_lo:.4f}(被质量好的 B 翻盘)")
    assert end_hi > 0.99, "实验[3]:s0 超临界应锁定"
    assert end_lo < 0.01, "实验[3]:s0 低于临界应被翻盘"

    # (b) 数值扫描临界 vs 解析对表(二分找分水岭)
    lo, hi = 0.51, 0.99
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if integrate(mid, a, q) > 0.5:
            hi = mid
        else:
            lo = mid
    s_crit = 0.5 * (lo + hi)
    print(f"(b) 数值临界份额 s_crit={s_crit:.4f},解析式 1/2−q/a={s_star:.4f}"
          f"(偏差 {abs(s_crit - s_star):.4f})")
    assert abs(s_crit - s_star) < 0.01, "实验[3]:数值临界与解析式不合"

    # (c) 锁定相图:初值扫描
    print("(c) 相图(s0 → 终态;>0.5=劣标准胜):")
    print("   s0      s(∞)")
    for s0 in (0.52, 0.56, 0.58, 0.60, 0.62, 0.65, 0.70, 0.80):
        end = integrate(s0, a, q)
        fate = "A 锁定" if end > 0.5 else "B 胜"
        print(f"  {s0:.2f}   {end:.4f}  {fate}")
        if s0 > s_star + 0.02:
            assert end > 0.99, f"实验[3]:s0={s0} 应锁定"
        if s0 < s_star - 0.02:
            assert end < 0.01, f"实验[3]:s0={s0} 应被翻盘"

    # (d) 对照:质量好的标准(q>0)临界份额左移,先发优势变劣势
    q2 = 0.1
    s_star2 = 0.5 - q2 / a
    assert integrate(0.45, a, q2) > 0.99, "实验[3]:q>0 时 45% 份额应翻盘胜出"
    assert integrate(0.35, a, q2) < 0.01, "实验[3]:q>0 时 35% 份额(低于 s*)应被翻盘"
    print(f"(d) 对照 q=+0.1(A 质量**优**):s*={s_star2:.2f}"
          "——临界左移,质量好者从 45% 份额即可翻盘,"
          "35% 仍被先发者压制;锁定不认好坏,"
          "只认份额与临界值的相对位置")
    print("断言通过:①劣标准 q<0 靠 s0>s* 锁定胜出 ②s0<s* 被翻盘 "
          "③数值临界与解析式 1/2−q/a 一致——"
          "『劣多少能被多少先发救』被写成一行参数(QWERTY 叙事的机制化;"
          "效率劣势幅度之争按文献通说,见 00 章故事框三)")


# ----------------------------------------------------------------主控

def main():
    print("抽样 OC 曲线与标准锁定动力学(教学版)——讲透标准科学技术家族实验")
    print("精确二项 P_a + 两点定样本量 + 锁定动力学;纯标准库"
          "(math/random);固定种子,可复现")
    random.seed(20260908)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①OC 曲线单调整体+变陡(判别力升)"
          "②两点定样本量(Ac=0 冲突/LTPD=1% 处 n=230,理论 229.1/"
          "两点靠近样本量超比例激增)"
          "③劣标准临界锁定(s*=1/2−q/a,过之锁死,低于翻盘)")
    print("=" * 64)


if __name__ == "__main__":
    main()
