# -*- coding: utf-8 -*-
"""
设计洪水三律(教学版)
=====================

家族实验 · 讲透工程水文学(GB/T 41035)
主题呼应走廊 C1:Gumbel 设计值的教学版——重现期语言怎么读、
短样本怎么把设计值估歪、稳态假设怎么被非平稳气候击穿。

Gumbel 分布(极值 I 型):
    F(x) = exp(−exp(−(x−μ)/σ))
    P(X > x_T) = 1/T  ⇔  x_T = μ + y_T·σ,y_T = −ln(−ln(1−1/T))
    母体:均值 = μ + γσ(γ≈0.5772 欧拉常数),标准差 = πσ/√6
    矩法(MOM):σ̂ = s·√6/π,μ̂ = x̄ − 0.5772·σ̂

三个实验(三律):
  [1] 重现期语言:T 年一遇 = 年超标概率 1/T,不是「T 年才来一次」。
      寿命 L 年内至少遭遇一次的概率 P = 1−(1−1/T)^L;
      T=100、L=50 ⇒ ≈39.5%(与蒙特卡洛互证)。
      「百年一遇」是频率刻度,不是大自然的日程表。
  [2] 短样本陷阱:同一真值总体(μ0=1000,σ0=400)反复抽样,
      矩法估 x₁₀₀(n=15 vs n=60):小样本组估计的离散度(标准差)
      显著更大(理论比≈√(60/15)=2),且两组都系统性低估
      (矩法 σ̂ 向下有偏,而 x₁₀₀ 住在均值上方 4.6σ 处——
      σ 低估一分,设计值低估 4.6 分)。「资料比公式更要紧」
      的定量版:尾巴不在样本里,估计就会系统性乐观。
  [3] 非平稳失效:年最大序列带线性趋势项(气候非平稳),
      用前半段稳态拟合出的 x₁₀₀,在序列末端年份的真实年
      超标概率比名义 1% 大一倍以上——稳态假设失效
      (呼应 01 章方向锚:非平稳气候下稳态假设失效×AI)。

物理约定:洪峰流量量级 m³/s;趋势斜率取教学值(仅演示
「趋势让稳态设计值失效」的机制,不代表任何现实流域)。
只用标准库 math/statistics/random;固定随机种子,结果可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random
import statistics

EULER_GAMMA = 0.5772156649015329      # 欧拉常数 γ
SQRT6_OVER_PI = math.sqrt(6.0) / math.pi   # σ̂ = s·√6/π ≈ 0.7797s

MU0 = 1000.0     # 真值总体:位置参数(教学值,m³/s 量级)
SIGMA0 = 400.0   # 真值总体:尺度参数


# ----------------------------------------------------------------模型件

def y_t(T):
    """Gumbel 简化变量 y_T = −ln(−ln(1−1/T)):x_T = μ + y_T·σ。"""
    return -math.log(-math.log(1.0 - 1.0 / T))


def gumbel_cdf(x, mu, sigma):
    """Gumbel 分布函数 F(x)=exp(−exp(−(x−μ)/σ))。"""
    return math.exp(-math.exp(-(x - mu) / sigma))


def gumbel_exceed_prob(x, mu, sigma):
    """真值年超标概率 P(X>x)=1−F(x)(律3 的核心量)。"""
    return 1.0 - gumbel_cdf(x, mu, sigma)


def sample_gumbel(mu, sigma):
    """Gumbel 抽样:U~U(0,1) ⇒ X = μ − σ·ln(−ln U)。"""
    return mu - sigma * math.log(-math.log(random.random()))


def mom_fit(sample):
    """矩法参数估计:σ̂ = s·√6/π,μ̂ = x̄ − 0.5772·σ̂。"""
    xbar = statistics.fmean(sample)
    s = statistics.stdev(sample)                # n−1 分母
    sigma_hat = s * SQRT6_OVER_PI
    mu_hat = xbar - EULER_GAMMA * sigma_hat
    return mu_hat, sigma_hat


def design_value(mu, sigma, T):
    """T 年一遇设计值 x_T = μ + y_T·σ。"""
    return mu + y_t(T) * sigma


def encounter_prob(T, L):
    """律1:T 年一遇洪水在 L 年寿命内至少遭遇一次的概率。"""
    return 1.0 - (1.0 - 1.0 / T) ** L


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """重现期语言:遭遇概率 1−(1−1/T)^L;T=100,L=50 ≈ 39.5%。"""
    section("实验 [1] 重现期语言:「百年一遇」≠「百年才等一次」")
    T, L = 100, 50
    p = encounter_prob(T, L)
    print(f"(a) 公式:P = 1−(1−1/T)^L = 1−0.99^{L} = {p:.4f}"
          f"(≈{p * 100:.1f}%)")
    assert abs(p - 0.395) < 0.001, \
        "实验[1]:T=100,L=50 的遭遇概率应≈39.5%"

    # (b) 寿命扫描:遭遇概率随寿命爬升
    print("(b) T=100,扫描设计寿命 L:")
    print("    L(年)   遭遇概率")
    for life in (10, 20, 30, 50, 70, 100, 200):
        print(f"   {life:4d}    {encounter_prob(T, life) * 100:6.2f}%")
    assert encounter_prob(T, 100) > 0.63, (
        "实验[1]:L=T 时遭遇概率应≈63.4%——「按百年一遇设计、"
        "运行一百年」近三分之二机会见到它")

    # (c) 蒙特卡洛互证:每年独立以 1% 超标,50 年寿命至少一次的频率
    shots = 200000
    hit = 0
    for _ in range(shots):
        seen = False
        for _year in range(L):
            if random.random() < 1.0 / T:
                seen = True
                break
        if seen:
            hit += 1
    mc = hit / shots
    print(f"(c) 蒙特卡洛({shots} 次寿命,每年独立 1% 超标):"
          f"至少遭遇一次的频率 = {mc:.4f}(公式 {p:.4f})")
    assert abs(mc - p) < 0.005, "实验[1]:MC 与公式遭遇概率不合"

    # (d) 「连着来」不违反概率:两次超标是独立事件
    p_two = (1.0 / T) ** 2
    print(f"(d) 连续两年各来一次「百年一遇」的年对概率 = {p_two:.6f}"
          f"(独立事件,合法且不罕见于长序列)")
    print("断言通过:①T=100,L=50 遭遇概率≈39.5% ②L=T 时≈63.4% "
          "③MC 与公式一致——重现期是频率刻度,不是日程表")


# ----------------------------------------------------------------实验 2

def experiment2(reps=3000):
    """短样本陷阱:n=15 vs n=60 的 x₁₀₀ 估计——离散度与低估。"""
    section("实验 [2] 短样本陷阱:矩法 x₁₀₀ 的抽样分布(n=15 vs n=60)")
    true_x100 = design_value(MU0, SIGMA0, 100)
    y100 = y_t(100)
    print(f"真值总体:μ0={MU0:g},σ0={SIGMA0:g}"
          f"(均值={MU0 + EULER_GAMMA * SIGMA0:.0f})")
    print(f"真值 x₁₀₀ = μ0 + {y100:.4f}·σ0 = {true_x100:.1f}\n")

    res = {}
    for n in (15, 60):
        est = []
        for _ in range(reps):
            sample = [sample_gumbel(MU0, SIGMA0) for _ in range(n)]
            mu_h, sig_h = mom_fit(sample)
            est.append(design_value(mu_h, sig_h, 100))
        est.sort()
        res[n] = dict(
            mean=statistics.fmean(est),
            std=statistics.stdev(est),
            q05=est[int(0.05 * reps)],
            q95=est[int(0.95 * reps)],
        )

    print(f"蒙特卡洛 {reps} 组样本,每组矩法估 x₁₀₀:")
    print("    n    均值    标准差    5%分位   95%分位   均值偏差")
    for n, r in res.items():
        bias = r["mean"] - true_x100
        print(f"  {n:3d}  {r['mean']:7.1f}  {r['std']:7.1f}  "
              f"{r['q05']:7.1f}  {r['q95']:7.1f}   {bias:+7.1f}")

    # 断言①:小样本离散度显著更大(理论比≈√(60/15)=2)
    ratio = res[15]["std"] / res[60]["std"]
    print(f"\n  · 离散度比 std(n=15)/std(n=60) = {ratio:.2f}"
          f"(理论≈√(60/15)=2.00)")
    assert ratio > 1.7, "实验[2]:小样本估计的离散度应显著更大"

    # 断言②:两组都系统性低估(矩法 σ̂ 向下有偏,x₁₀₀ 在 4.6σ 处)
    assert res[15]["mean"] < true_x100 and res[60]["mean"] < true_x100, \
        "实验[2]:矩法 x₁₀₀ 应存在系统性低估"
    b15 = true_x100 - res[15]["mean"]
    b60 = true_x100 - res[60]["mean"]
    print(f"  · 系统性低估:n=15 偏低 {b15:.1f}({b15 / true_x100 * 100:.1f}%),"
          f"n=60 偏低 {b60:.1f}({b60 / true_x100 * 100:.1f}%)——"
          "σ̂ 低估一分,设计值低估 4.6 分")

    # 断言③:小样本的低估更深(偏差随 n 收敛)
    assert res[15]["mean"] < res[60]["mean"], \
        "实验[2]:n=15 的低估应比 n=60 更深"

    # (d) 区间对照:设计值必须带区间交付(03 章 schema 的 ci 字段)
    w15 = res[15]["q95"] - res[15]["q05"]
    w60 = res[60]["q95"] - res[60]["q05"]
    print(f"  · 90% 抽样区间宽:n=15 为 {w15:.0f},n=60 为 {w60:.0f}"
          f"(比 {w15 / w60:.1f} 倍)——naked 设计值把这么宽的"
          "抽样误差冒充成安全余量")
    print("断言通过:①离散度比>1.7(理论 2)②矩法系统性低估 "
          "③n=15 低估更深——资料年限买的是方向,不只是精度")


# ----------------------------------------------------------------实验 3

def experiment3(reps=2000, n_years=60, slope=15.0):
    """非平稳失效:前半段稳态拟合的 x₁₀₀,在末端年份真实超标概率翻倍以上。"""
    section("实验 [3] 非平稳失效:稳态设计值的「保质期」")
    y100 = y_t(100)
    print(f"设定:{n_years} 年年最大序列,位置参数线性抬升 "
          f" slope={slope:g}/年(趋势项,气候非平稳),σ0={SIGMA0:g} 不变")
    print(f"末端位置 μ_end = μ0 + {n_years - 1}·{slope:g} = "
          f"{MU0 + (n_years - 1) * slope:g}\n")

    def mu_at(t):
        """第 t 年(1 起)的真实位置参数。"""
        return MU0 + slope * (t - 1)

    # (a) 单次实现:前半段稳态拟合 → 固定设计值
    series = [sample_gumbel(mu_at(t), SIGMA0) for t in range(1, n_years + 1)]
    mu_h, sig_h = mom_fit(series[:n_years // 2])
    x100_st = design_value(mu_h, sig_h, 100)
    print(f"(a) 一次实现:前 30 年矩法拟合 μ̂={mu_h:.0f},σ̂={sig_h:.0f}")
    print(f"    稳态设计值 x₁₀₀^(st) = {x100_st:.1f}(名义年超标概率 1%)\n")

    # (b) 保质期表:该固定设计值逐年代的真实超标概率
    print("(b) 同一条频率曲线的「保质期」——真实年超标概率逐年抬升:")
    print("    年份 t    μ(t)    P(X_t > x₁₀₀^(st))")
    p_end_list = []
    for t in (1, 10, 20, 30, 40, 50, 60):
        p_t = gumbel_exceed_prob(x100_st, mu_at(t), SIGMA0)
        flag = "  ←名义" if t == 30 else ("  ←末端" if t == 60 else "")
        print(f"   {t:5d}   {mu_at(t):6.0f}      {p_t * 100:6.2f}%{flag}")
    p_end_single = gumbel_exceed_prob(x100_st, mu_at(n_years), SIGMA0)
    assert p_end_single > 0.02, \
        "实验[3]:末端年份真实超标概率应>2%(名义的两倍)"

    # (c) 蒙特卡洛平均:2000 次实现,末端真实超标概率的期望
    for _ in range(reps):
        s = [sample_gumbel(mu_at(t), SIGMA0)
             for t in range(1, n_years // 2 + 1)]
        m_h, sg_h = mom_fit(s)
        x100_hat = design_value(m_h, sg_h, 100)
        p_end_list.append(
            gumbel_exceed_prob(x100_hat, mu_at(n_years), SIGMA0))
    p_end_mean = statistics.fmean(p_end_list)
    ratio_end = p_end_mean / 0.01
    print(f"\n(c) 蒙特卡洛 {reps} 次实现(每次前 30 年拟合→末端评估):")
    print(f"    末端年份真实年超标概率均值 = {p_end_mean * 100:.2f}%"
          f"(名义 1%)——为名义值的 {ratio_end:.1f} 倍")
    assert p_end_mean > 0.02, \
        "实验[3]:平均末端超标概率应大于名义值两倍以上"

    # (d) 对照组:无趋势稳态序列,同流程末端超标概率≈1%(方法自检)
    ctrl = []
    for _ in range(reps):
        s = [sample_gumbel(MU0, SIGMA0)
             for _ in range(n_years // 2)]
        m_h, sg_h = mom_fit(s)
        ctrl.append(gumbel_exceed_prob(design_value(m_h, sg_h, 100),
                                       MU0, SIGMA0))
    ctrl_mean = statistics.fmean(ctrl)
    print(f"(d) 对照组(无趋势,slope=0):同流程末端超标概率均值 = "
          f"{ctrl_mean * 100:.2f}% ≈ 名义 1%(略高出的零点几个百分点"
          "正是律②矩法低估的投影)")
    assert 0.008 < ctrl_mean < 0.02, \
        "实验[3]:无趋势对照应在名义 1% 附近(方法自检)"
    assert p_end_mean > 3.0 * ctrl_mean, \
        "实验[3]:趋势组失效应显著盖过估计偏差(3 倍以上)"
    print(f"    趋势组 {p_end_mean * 100:.2f}% / 对照组 "
          f"{ctrl_mean * 100:.2f}% = {p_end_mean / ctrl_mean:.1f} 倍——"
          "失效的大头是稳态假设本身,不是估计方法")
    print("断言通过:①单次实现末端超标概率>2% ②MC 平均超标概率"
          "大于名义两倍以上 ③无趋势对照≈1% 附近且趋势组为其 3 倍"
          "以上——失效不是方法的错,是「过去代表未来」这条稳态"
          "假设的错(01 章方向锚)")


# ----------------------------------------------------------------主控

def main():
    print("设计洪水三律(教学版)——讲透工程水文学家族实验")
    print("Gumbel 极值 I 型+矩法;纯标准库(math/statistics/random);"
          "固定种子,可复现")
    random.seed(20260908)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①重现期遭遇概率(T=100,L=50≈39.5%,"
          "「百年一遇≠百年才等一次」)②短样本陷阱(n=15 离散度"
          "显著更大+矩法系统性低估)③非平稳失效(稳态 x₁₀₀ 末端"
          "真实超标概率>名义两倍)——稳态假设失效")
    print("=" * 64)


if __name__ == "__main__":
    main()
