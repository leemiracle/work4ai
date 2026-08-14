#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
finance_demos.py — 经济金融费曼式可跑 demo（纯标准库，python3 直接跑）
================================================================================
对应 top-economics-finance-courses 八大主题的精华演示。

设计原则（与 work4ai 铁律一致）：
  - 纯标准库（math/random/statistics），无需 pip install，python3 直接跑
  - 每个 demo = 费曼一句话直觉 + 数学公式 + 可跑验证 + 模型风险提醒
  - 覆盖主题③计量④资产定价⑤衍生品⑧风险管理（其余主题 demo 阶段 3 补）

用法:
    python3 finance_demos.py

依赖: Python 3.6+ 标准库（无 numpy/scipy/pandas，仿 physics_demos.py 风格）
================================================================================
"""

import math
import random
import statistics

# ============================================================================
# 标准正态分布工具（用 erf 近似 CDF，不依赖 scipy）
# ============================================================================
SQRT_2PI = math.sqrt(2.0 * math.pi)


def norm_cdf(x):
    """标准正态累积分布函数 Φ(x)，用 math.erf 精确实现。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x):
    """标准正态密度 φ(x)。"""
    return math.exp(-0.5 * x * x) / SQRT_2PI


def box_muller_normal():
    """Box-Muller 法生成标准正态样本（纯标准库）。"""
    u1, u2 = random.random(), random.random()
    while u1 == 0.0:  # 防 log(0)
        u1 = random.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


# ============================================================================
# Demo 1 & 2 —— 主题⑤：衍生品与随机微积分
# Black-Scholes 解析解 vs Monte Carlo 模拟
# ============================================================================
def black_scholes_call(S, K, T, r, sigma):
    """
    Black-Scholes-Merton 欧式看涨期权解析解。

        C = S · N(d1) − K · e^{−rT} · N(d2)
        d1 = [ ln(S/K) + (r + σ²/2)·T ] / (σ√T)
        d2 = d1 − σ√T

    参数:
        S     标的现价
        K     行权价
        T     到期时间（年）
        r     无风险利率（连续复利）
        sigma 标的波动率（年化）
    返回:
        看涨期权价格 C
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


def monte_carlo_call(S, K, T, r, sigma, n=100_000):
    """
    Monte Carlo 验证 BS：在风险中性测度下模拟几何布朗运动 (GBM) 终值。

        S_T = S · exp( (r − σ²/2)·T + σ√T · Z ),   Z ~ N(0,1)
        C ≈ e^{−rT} · E[ max(S_T − K, 0) ]

    n 个样本取平均即得期权价格的蒙特卡洛估计。
    """
    total = 0.0
    drift = (r - 0.5 * sigma ** 2) * T
    vol = sigma * math.sqrt(T)
    for _ in range(n):
        z = box_muller_normal()
        s_t = S * math.exp(drift + vol * z)
        total += max(s_t - K, 0.0)
    return math.exp(-r * T) * (total / n)


# ============================================================================
# Demo 3 —— 主题④：资产定价
# CAPM 资本资产定价模型
# ============================================================================
def capm_expected_return(rf, beta, market_premium):
    """
    Capital Asset Pricing Model:

        E(R_i) = R_f + β_i · ( E(R_m) − R_f )

    β_i 衡量个股相对市场的系统性风险；市场只补偿系统性风险（非系统性风险可分散）。
    """
    return rf + beta * market_premium


# ============================================================================
# Demo 4 —— 主题⑧：风险管理与量化交易
# VaR / CVaR / Sharpe / Sortino / MaxDrawdown
# ============================================================================
def value_at_risk(returns, alpha=0.05):
    """
    经验 VaR（Value at Risk）：收益分布的 alpha 分位点。
    返回负值代表亏损。VaR(95%) = -2% 表示「95% 的日子亏损不超过 2%」。
    """
    s = sorted(returns)
    idx = max(0, int(alpha * len(s)))
    return s[idx]


def conditional_var(returns, alpha=0.05):
    """
    CVaR / Expected Shortfall：最坏 alpha 比例样本的平均损失。
    比 VaR 更保守（看「门后」），2008 后 Basel 主推指标。
    """
    s = sorted(returns)
    idx = max(0, int(alpha * len(s)))
    return statistics.mean(s[: idx + 1])


def sharpe_ratio(returns, rf=0.0, periods=252):
    """年化夏普比率 = (均值/标准差) · √periods。衡量每单位总波动的超额收益。"""
    excess = [r - rf for r in returns]
    sd = statistics.pstdev(excess)
    if sd == 0:
        return 0.0
    return (statistics.mean(excess) / sd) * math.sqrt(periods)


def sortino_ratio(returns, rf=0.0, periods=252):
    """年化 Sortino：分母只用下行偏差（只惩罚不利波动）。"""
    excess = [r - rf for r in returns]
    downside = [min(e, 0.0) for e in excess]
    dd = math.sqrt(statistics.mean([d * d for d in downside])) if downside else 0.0
    if dd == 0:
        return 0.0
    return (statistics.mean(excess) / dd) * math.sqrt(periods)


def max_drawdown(equity_curve):
    """
    最大回撤：从历史最高点到后续最低点的最大跌幅。
    「活着比赚钱重要」——MDD 决定能不能熬过最坏时刻。
    """
    peak = equity_curve[0]
    mdd = 0.0
    for v in equity_curve:
        if v > peak:
            peak = v
        dd = (v - peak) / peak
        if dd < mdd:
            mdd = dd
    return mdd


# ============================================================================
# Demo 5 —— 主题④+⑧：因子模拟（Fama-French 风格多因子）
# ============================================================================
def simulate_factor_returns(n_days=252, seed=42):
    """
    模拟带「市场因子 + 价值因子 (HML)」的日收益序列（Fama-French 风格）。
        r_t = β_m · MKT_t + β_v · HML_t + ε_t
    展示因子暴露如何驱动收益（对应因子投资工业化）。
    """
    random.seed(seed)
    returns = []
    for _ in range(n_days):
        mkt = random.gauss(0.0004, 0.010)   # 市场因子（日）
        hml = random.gauss(0.0002, 0.008)   # 价值因子 High-Minus-Low
        beta_m, beta_v = 1.1, 0.3
        eps = random.gauss(0.0, 0.005)       # 特质噪声
        returns.append(beta_m * mkt + beta_v * hml + eps)
    return returns


def equity_from_returns(returns, start=1.0):
    """把日收益序列转为净值曲线。"""
    eq = [start]
    for r in returns:
        eq.append(eq[-1] * (1.0 + r))
    return eq


# ============================================================================
# Demo 6 —— 主题③：计量经济学 / 因果推断
# 「相关不是因果」—— 混淆偏差演示
# ============================================================================
def ols_slope(x, y):
    """简单 OLS 回归斜率（二元情况）。"""
    n = len(x)
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    return num / den if den else 0.0


def simulate_confounding(seed=7):
    """
    混淆偏差演示：冰淇淋销量 X 与溺水数 D 都受气温 T 驱动。
    naive 回归会伪报 X→D 的「显著」因果，控制 T 后效应 → 0。
    这就是计量经济学识别 (identification) 的灵魂。
    """
    random.seed(seed)
    T = [random.gauss(25.0, 5.0) for _ in range(500)]
    X = [0.5 * t + random.gauss(0, 2) for t in T]   # 冰淇淋销量
    D = [0.3 * t + random.gauss(0, 2) for t in T]   # 溺水数
    return X, D, T


# ============================================================================
# 主程序：跑全部 demo
# ============================================================================
def main():
    print("=" * 74)
    print(" top-economics-finance-courses · finance_demos.py".center(74))
    print(" 八大主题费曼式可跑 demo（纯标准库，python3 直接跑）".center(74))
    print("=" * 74)

    # ---- Demo 1 & 2: Black-Scholes vs Monte Carlo ---------------------------
    print("\n── Demo 1&2 · 主题⑤ 衍生品：Black-Scholes 解析解 vs Monte Carlo ──")
    S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
    bs = black_scholes_call(S, K, T, r, sigma)
    mc = monte_carlo_call(S, K, T, r, sigma, n=100_000)
    print(f"  参数: S={S}  K={K}  T={T}年  r={r}  σ={sigma}")
    print(f"  Black-Scholes 解析解 : C = {bs:.4f}")
    print(f"  Monte Carlo (1e5样本): C = {mc:.4f}")
    print(f"  相对误差: {abs(bs - mc) / bs * 100:.2f}%  ← MC 收敛到 BS，验证无套利定价")
    print("  💡 费曼: BS 假设对数正态 + 连续对冲; 1987/2008/LTCM 证明肥尾下它会杀人")
    print("          —— 这就是 §1 张力③「模型 vs 市场」的全部血泪。")

    # ---- Demo 3: CAPM -------------------------------------------------------
    print("\n── Demo 3 · 主题④ 资产定价：CAPM 资本资产定价 ──")
    rf, beta, mkt_prem = 0.03, 1.2, 0.06
    exp_ret = capm_expected_return(rf, beta, mkt_prem)
    print(f"  rf={rf}  β={beta}  市场溢价={mkt_prem}")
    print(f"  E(R_i) = {rf} + {beta}×{mkt_prem} = {exp_ret:.2%}")
    print("  💡 费曼: β=「跟着大盘跳舞的程度」; β>1 放大市场, β<1 缓冲")
    print("          CAPM 是 EMH 的数学骨架, 也是 §1 张力②「有效 vs 异象」的战场。")

    # ---- Demo 4 & 5: 风险指标 on 因子模拟收益 -------------------------------
    print("\n── Demo 4&5 · 主题⑧ 风险管理：风险指标 on 模拟因子收益 ──")
    rets = simulate_factor_returns()
    eq = equity_from_returns(rets)
    ann_ret = statistics.mean(rets) * 252
    print(f"  252 日模拟: 年化收益 = {ann_ret:.2%}")
    print(f"  VaR(95%)      = {value_at_risk(rets, 0.05):.2%}   ← 5% 最坏日子的下界")
    print(f"  CVaR(95%)     = {conditional_var(rets, 0.05):.2%}   ← 最坏 5% 的平均（更保守, Basel 主推）")
    print(f"  Sharpe (年化) = {sharpe_ratio(rets):.3f}   ← 风险调整收益")
    print(f"  Sortino(年化) = {sortino_ratio(rets):.3f}   ← 只惩罚下行波动")
    print(f"  MaxDrawdown   = {max_drawdown(eq):.2%}   ← 活着比赚钱重要")
    print("  💡 费曼: VaR 看门, CVaR 看门后, Sharpe 看性价比, MDD 看能不能熬过。")

    # ---- Demo 6: 因果识别 ---------------------------------------------------
    print("\n── Demo 6 · 主题③ 计量经济学：相关不是因果 ──")
    X, D, T = simulate_confounding()
    naive = ols_slope(X, D)
    print(f"  场景: 冰淇淋销量 X vs 溺水数 D，两者真实因果都被气温 T 驱动")
    print(f"  naive 回归斜率 (X→D)   = {naive:.3f}   ← 看起来 X「显著导致」D!")
    # 控制气温 T（FWL 定理：残差回归）
    bx_t = ols_slope(T, X)
    bd_t = ols_slope(T, D)
    X_res = [x - bx_t * t for x, t in zip(X, T)]
    D_res = [d - bd_t * t for d, t in zip(D, T)]
    controlled = ols_slope(X_res, D_res)
    print(f"  控制 T 后(残差回归)斜率 = {controlled:.3f}   ← 趋近 0, 揭露伪相关")
    print("  💡 费曼: 这是计量经济学的灵魂 —— 识别 (identification) > 估计 (estimation)")
    print("          IV/DiD/RDD/RCT 都是为了剔除混淆, 锁定真因果。")

    print("\n" + "=" * 74)
    print(" 全部 demo 完成。覆盖主题: ③计量 ④资产定价 ⑤衍生品 ⑧风控".center(74))
    print(" 其余主题(微观/宏观/公司金融/市场微观结构) demo 见阶段 3".center(74))
    print("=" * 74)


if __name__ == "__main__":
    main()
