# -*- coding: utf-8 -*-
"""
测量不确定度传播与量值传递链(教学版)
======================================

家族实验 · 讲透计量学(GB/T 41055)
主题呼应走廊 C1:把「准到多少」与「量值怎么传」各写成一个可计算的模型。

模型:
  [律1] 不确定度合成律(GUM 方和根传播律,不相关输入):
        uc = sqrt(u1^2 + u2^2 + ...)——方差相加,不是不确定度相加。
        主导分量淹没小分量:uc = sqrt(10%^2 + 1%^2) = 10.0499% ≈ 10.05%,
        1% 分量对合成的贡献被 10% 主导分量平方后吞没(方差份额仅 0.99%,
        对 uc 的影响不足 0.5%——「10:1 可忽略」经验规则的来源)。
        退化情形:等权两分量时合成 = 单分量 × sqrt(2)。
  [律2] A 类 sqrt(n) 收敛与小样本 t 因子:
        重复测量均值的标准误 u_mean = s/sqrt(n) 按 1/sqrt(n) 收敛
        (n=4→16 恰好收敛一半);但 95% 包含区间在小样本须乘 t 因子:
        自由度 ν = n−1,n=5 时 t_{0.975}(4) ≈ 2.776(查表值;本脚本用
        ν=4 的闭式 CDF 反解互证),区间比正态假设(1.96)宽
        2.776/1.96 − 1 ≈ 41.6% ≈ 42%;用 1.96 硬套小样本,
        名义 95% 的区间实际覆盖率只有约 87.8%。
  [律3] 量值传递链逐级放大:
        链:国家基准 → 参考标准 → 工作标准 → 现场仪表,
        每级 u_{i+1} = sqrt((r·u_i)^2 + w_{i+1}^2):
        上一级不确定度经传递比 r(>1)放大后,与本级自身分量 w 按方和根合成。
        assert:链每向下一级严格增大(r≥1、w>0 时增量 (r^2−1)u_i^2+w^2>0);
        传递比越大,链末端越快失控(末级/首级之比的几何平均随 r 上升)
        ——「为什么高等级实验室必须少而精」的算术本体:
        链长本身就有代价(即使理想传递 r=1,中间级的自身分量照样进末级方差),
        且末级改善靠打磨本级自身分量,不靠打磨国家基准。

只用标准库 math/random/statistics;固定随机种子,可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random
import statistics


# ----------------------------------------------------------------模型件

def rss(*us):
    """不相关分量的方和根合成(GUM 传播律,相关系数为零):
    uc = sqrt(Σ u_i^2)。方差相加,不是不确定度相加。
    """
    return math.sqrt(sum(u * u for u in us))


def t_cdf_nu4(t):
    """自由度 ν=4 的学生 t 分布 CDF(闭式,t≥0)。

    代换 s = t/sqrt(4+t^2) 后:F(t) = 1/2 + (3/4)s − (1/4)s^3。
    用于互证查表值 t_{0.975}(4) ≈ 2.776(不引入 scipy)。
    """
    s = t / math.sqrt(4.0 + t * t)
    return 0.5 + 0.75 * s - 0.25 * s * s * s


def t_quantile_975_nu4():
    """二分反解 F(t)=0.975,得 ν=4 的 t 分位数。"""
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf_nu4(mid) < 0.975:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def sem(pop_sigma, n):
    """正态总体下,样本均值的标准误 = σ/√n(A 类评定的理论骨架)。"""
    return pop_sigma / math.sqrt(n)


def chain_uncertainties(u0, w_list, r):
    """量值传递链:u_{i+1} = sqrt((r·u_i)^2 + w_{i+1}^2)。

    u0 = 国家基准(首级)不确定度;w_list = 参考标准/工作标准/现场仪表
    各级自身分量;r = 传递比(每传递一级,上一级不确定度被放大的倍数,
    r≥1;理想无损传递 r=1)。返回整条链 [u0, u1, ..., uk]。
    """
    chain = [u0]
    for w in w_list:
        chain.append(math.sqrt((r * chain[-1]) ** 2 + w * w))
    return chain


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """合成律:主导分量淹没小分量;退化情形等权 ×√2。"""
    section("实验 [1] 合成律:uc=sqrt(u1^2+u2^2)——合成不等于相加")

    # (a) 主导分量:10% ⊕ 1%
    u_dom, u_small = 0.10, 0.01
    uc = rss(u_dom, u_small)
    print(f"(a) uc = sqrt(10%² + 1%²) = {uc:.6f} = {uc*100:.4f}% ≈ 10.05%")
    assert abs(uc - 0.1004987562) < 1e-9, \
        "实验[1]:10%⊕1% 应为 √0.0101≈0.100499(10.0499%)"
    assert abs(round(uc * 100, 2) - 10.05) < 1e-12, \
        "实验[1]:四舍五入到两位应为 10.05%"
    var_share = u_small ** 2 / (u_dom ** 2 + u_small ** 2)
    print(f"    1% 分量的方差份额 = 0.0001/0.0101 = {var_share:.4%}"
          f"(贡献被 10% 主导分量平方后吞没)")
    assert var_share < 0.01, "实验[1]:1% 分量方差份额应不足 1%"

    # (b) 「10:1 可忽略」:砍掉小分量,uc 只动 0.5%
    delta = (uc - u_dom) / u_dom
    print(f"(b) 砍掉 1% 分量:uc 从 {uc*100:.4f}% 回到 10%,"
          f"只变化 {delta:.4%}——10:1 分量对合成的影响不足 0.5%")
    assert 0.0049 < delta < 0.0051, "实验[1]:砍掉 1% 分量 uc 变化应约 0.499%"

    # (c) 退化情形:等权两分量,合成 = 单分量 × √2
    u_eq = rss(u_dom, u_dom)
    print(f"(c) 等权两分量:uc = sqrt(2×10%²) = {u_eq*100:.4f}% "
          f"= 10%×√2 = {10*math.sqrt(2):.4f}%")
    assert abs(u_eq - u_dom * math.sqrt(2)) < 1e-15, \
        "实验[1]:等权两分量合成应为单分量×√2"

    # (d) 治理读数:砍主导分量一半 vs 消灭小分量
    u_cut_dom = rss(u_dom / 2, u_small)
    u_kill_small = rss(u_dom, 0.0)
    print(f"(d) 砍主导分量一半:uc={u_cut_dom*100:.4f}%(省 "
          f"{(1-u_cut_dom/uc)*100:.1f}%);消灭 1% 小分量:uc="
          f"{u_kill_small*100:.4f}%(只省 {(1-u_kill_small/uc)*100:.1f}%)"
          "——预算治理先砍最大的那块")
    assert u_dom / 2 < u_cut_dom < 0.06, "实验[1]:砍半主导后 uc 应略高于 5%"
    print("断言通过:①10%⊕1%=10.0499%≈10.05%(小分量被平方吞没) "
          "②等权两分量=单分量×√2 ③10:1 分量对合成影响<0.5%"
          "——「先找主导分量」是不确定度预算的第一问")


# ----------------------------------------------------------------实验 2

def experiment2():
    """A 类 √n 收敛 + 小样本 t 因子:n=4→16 收敛一半;n=5 区间比正态宽 42%。"""
    section("实验 [2] A 类 √n 收敛与小样本 t 因子(n=5 时 2.776 vs 1.96)")

    # (a) 理论:标准误按 1/√n 收敛,n=4→16 恰好减半
    sigma = 1.0
    sem4, sem16 = sem(sigma, 4), sem(sigma, 16)
    print(f"(a) u_mean = σ/√n:n=4 → {sem4:.4f},n=16 → {sem16:.4f},"
          f"比值 {sem4/sem16:.4f}(n 扩大 4 倍,标准误减半)")
    assert sem4 / sem16 == 2.0, "实验[2]:n=4→16 标准误应恰好收敛一半"
    assert sem(sigma, 4) / sem(sigma, 9) == 1.5, "实验[2]:n=4→9 应乘 3/2"

    # (b) 蒙特卡洛互证:试验均值的经验标准差之比 ≈ 2
    trials, mu = 20000, 0.0
    means4 = [statistics.fmean(random.gauss(mu, sigma) for _ in range(4))
              for _ in range(trials)]
    means16 = [statistics.fmean(random.gauss(mu, sigma) for _ in range(16))
               for _ in range(trials)]
    emp4, emp16 = statistics.stdev(means4), statistics.stdev(means16)
    print(f"(b) MC({trials} 次):n=4 均值经验分散 {emp4:.4f},"
          f"n=16 {emp16:.4f},比值 {emp4/emp16:.4f} ≈ 2")
    assert abs(emp4 / emp16 - 2.0) < 0.10, "实验[2]:经验标准误之比应≈2"

    # (c) t 因子:ν=n−1=4,t_{0.975}(4)=2.776(查表),闭式 CDF 互证
    t_tab, t_solve = 2.776, t_quantile_975_nu4()
    print(f"(c) n=5(ν=4):查表 t_0.975(4)={t_tab};闭式 CDF 反解="
          f"{t_solve:.4f};F(2.776)={t_cdf_nu4(2.776):.5f}")
    assert abs(t_solve - 2.776) < 0.001, \
        "实验[2]:ν=4 的 0.975 分位数应≈2.776(查表值)"
    assert abs(t_cdf_nu4(2.776) - 0.975) < 0.0005, \
        "实验[2]:F(2.776) 应≈0.975(闭式互证查表值)"

    # (d) 区间宽度:t 比 1.96 宽 42%
    ratio = t_tab / 1.96
    print(f"(d) 区间宽度比 = 2.776/1.96 = {ratio:.4f}"
          f"→ 比 1.96 正态假设宽 {(ratio-1)*100:.1f}% ≈ 42%")
    assert abs((ratio - 1) - 0.4163) < 0.002, "实验[2]:宽度比应≈41.6%→42%"

    # (e) 覆盖率互证:n=5 用 1.96,名义 95% 实际只有 ~87.8%
    n, k_norm, k_t = 5, 1.96, 2.776
    cover_norm = sum(
        1 for _ in range(20000)
        if abs(statistics.fmean(
            (x := [random.gauss(mu, sigma) for _ in range(n)]))
            - mu) <= k_norm * statistics.stdev(x) / math.sqrt(n))
    cover_t = sum(
        1 for _ in range(20000)
        if abs(statistics.fmean(
            (x := [random.gauss(mu, sigma) for _ in range(n)]))
            - mu) <= k_t * statistics.stdev(x) / math.sqrt(n))
    exact_norm = 2 * t_cdf_nu4(k_norm) - 1
    print(f"(e) n=5 覆盖率:1.96 区间 MC={cover_norm/20000:.4f},"
          f"闭式={exact_norm:.4f};t=2.776 区间 MC={cover_t/20000:.4f}")
    assert abs(cover_norm / 20000 - exact_norm) < 0.01, \
        "实验[2]:1.96 区间覆盖率 MC 应与闭式一致(≈87.8%)"
    assert abs(exact_norm - 0.8784) < 0.002, \
        "实验[2]:n=5 用 1.96 的真实覆盖率应≈87.8%"
    assert abs(cover_t / 20000 - 0.95) < 0.01, \
        "实验[2]:t=2.776 区间覆盖率应≈95%"
    print("断言通过:①均值标准误按 1/√n 收敛(n=4→16 减半,MC 互证) "
          "②n=5 须乘 t(4)=2.776,区间比 1.96 宽 41.6%≈42%,"
          "硬套 1.96 名义 95% 实际 87.8%——「多测几次取平均」的收益"
          "按 √n 递减,小样本的诚实有价")


# ----------------------------------------------------------------实验 3

def experiment3():
    """传递链逐级放大:每级严格增大;传递比越大末端越快失控;链长本身有代价。"""
    section("实验 [3] 传递链:u_{i+1}=sqrt((r·u_i)^2+w^2)——逐级单调放大")

    u0, w_list = 1.0, [2.0, 3.0, 4.0]    # 国家基准 1;参考/工作/现场自身分量
    names = ["国家基准", "参考标准", "工作标准", "现场仪表"]

    # (a) 三条链(r=1/1.2/1.5):逐级严格增大
    chains = {r: chain_uncertainties(u0, w_list, r) for r in (1.0, 1.2, 1.5)}
    for r, ch in chains.items():
        print(f"(a) r={r:.1f}:" + " → ".join(f"{v:.4f}" for v in ch))
        for i in range(len(ch) - 1):
            assert ch[i + 1] > ch[i] + 1e-12, \
                f"实验[3]:r={r} 链在第 {i}→{i+1} 级未严格增大"
        # 增量恒正的解析理由:(r²−1)u_i² + w² > 0
        assert all((r * r - 1) * ch[i] ** 2 + w_list[i] ** 2 > 0
                   for i in range(3)), "实验[3]:逐级增量 (r²−1)u_i²+w² 应恒正"
    print("    三条链全部逐级严格增大(增量 (r²−1)u_i²+w²>0;"
          "r=1 时靠中间级自身分量照样增长)")

    # (b) 传递比越大,链末端越快失控
    ends = {r: ch[-1] for r, ch in chains.items()}
    grow = {r: (ch[-1] / ch[0]) ** (1 / 3) for r, ch in chains.items()}
    print(f"(b) 链末端现场级:r=1.0→{ends[1.0]:.4f},r=1.2→{ends[1.2]:.4f},"
          f"r=1.5→{ends[1.5]:.4f}")
    print(f"    每级几何平均放大率:(u_end/u_0)^(1/3) = "
          f"{grow[1.0]:.4f} → {grow[1.2]:.4f} → {grow[1.5]:.4f}")
    assert ends[1.0] < ends[1.2] < ends[1.5], "实验[3]:末端应随 r 单调放大"
    assert grow[1.0] < grow[1.2] < grow[1.5], \
        "实验[3]:几何平均放大率应随 r 上升(传递比越大末端越快失控)"
    assert abs(ends[1.0] - math.sqrt(30)) < 1e-9, \
        "实验[3]:r=1 时末端=√(1²+2²+3²+4²)=√30≈5.4772"

    # (c) 链长本身有代价:砍掉两级中间标准(r=1),末级 24.7%↓
    direct = rss(u0, w_list[-1])
    print(f"(c) 理想传递 r=1:直连校准(国家→现场)末端=√(1²+4²)="
          f"{direct:.4f},过三级链={ends[1.0]:.4f}"
          f"(链本身多付 {(1-direct/ends[1.0])*100:.1f}%)")
    assert direct < 0.76 * ends[1.0], \
        "实验[3]:砍掉中间两级应省逾 24%——「高等级实验室必须少而精」"

    # (d) 末级治理:打磨现场级自身分量,远胜打磨国家基准
    w2_end = rss(u0, w_list[0], w_list[1], w_list[2] / 2)
    u0_end = rss(u0 / 2, w_list[0], w_list[1], w_list[2])
    print(f"(d) r=1 方差分解:国家基准 {u0**2/30:.1%}、参考 "
          f"{w_list[0]**2/30:.1%}、工作 {w_list[1]**2/30:.1%}、"
          f"现场 {w_list[2]**2/30:.1%};末级自身分量减半→末端 "
          f"{w2_end:.4f}(省 {(1-w2_end/ends[1.0])*100:.1f}%),"
          f"国家基准减半→{u0_end:.4f}(只省 {(1-u0_end/ends[1.0])*100:.1f}%)")
    assert (1 - w2_end / ends[1.0]) > 0.20, \
        "实验[3]:打磨末级自身分量应省逾 20%"
    assert (1 - u0_end / ends[1.0]) < 0.02, \
        "实验[3]:国家基准减半对末端影响应不足 2%"
    print("断言通过:①链每向下一级严格增大(r≥1、w>0)②传递比越大"
          "末端越快失控(几何平均放大率 1.76→1.85→2.02)③链长本身"
          "有代价(r=1 直连省 24.7%)、末级治理先磨自身分量"
          "——传递链是花钱买方便,每级都收税")


# ----------------------------------------------------------------主控

def main():
    print("测量不确定度传播与量值传递链(教学版)——讲透计量学家族实验")
    print("GUM 合成律 + A 类 √n 收敛与小样本 t 因子 + 传递链逐级放大;"
          "纯标准库(math/random/statistics);固定种子,可复现")
    random.seed(20260908)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①合成律主导分量(10%⊕1%=10.0499%≈10.05%,"
          "等权=×√2,小分量平方后被吞没)②A 类 √n 收敛(n=4→16 减半)"
          "+小样本 t 因子(n=5 时 t(4)=2.776 比 1.96 宽 42%)"
          "③传递链逐级单调放大且 r 越大末端越快失控"
          "(u_{i+1}=√((r·u_i)²+w²),链长本身有代价)")
    print("=" * 64)


if __name__ == "__main__":
    main()
