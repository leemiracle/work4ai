"""
算法深挖 1: 报童模型 → 多期扩展 (Multi-Period Newsvendor)
单期: Q* = F^{-1}(cu/(cu+co))
多期新增两个机制:
  (a) 剩余库存跨期结转 (持有成本 h)
  (b) 期末已满足需求的信息更新 -> 若需求可观测, 用本期观测更新下期分布(贝叶斯)
数学: 多期报童 = 库存基址策略 (base-stock policy): 订货至 S*
      S* 满足临界比率分位, 但分布参数随贝叶斯学习演化
仿真: 对比 单期静态 vs 基址策略+贝叶斯学习 的 100 期累计利润
"""
import numpy as np

rng = np.random.default_rng(7)
T = 100                      # 期数
p, c, s, h = 30.0, 18.0, 6.0, 1.0   # 售价/进价/残值(可结转则当作持有)/持有成本
cu, co = p - c, c + h - s    # 多期下过储成本含持有成本

# 需求: 正态但参数未知(真实 mu=100, sigma=20), 管理者先验 mu~N(80, 25^2)
mu_true, sigma = 100.0, 20.0
mu_belief, tau_belief = 80.0, 25.0   # 先验均值与先验"精度"(用方差表达)


def critical_ratio_order(mu, sigma, inv):
    CR = cu / (cu + co)
    from scipy.stats import norm
    S = norm.ppf(CR, loc=mu, scale=sigma)   # 订货至基址
    return max(0.0, S - inv)


def run(learn: bool):
    inv = 0.0
    mu_b, tau2 = mu_belief, tau_belief ** 2
    total = 0.0
    profits = []
    n_obs, sum_obs = 0, 0.0
    for t in range(T):
        d = rng.normal(mu_true, sigma)
        d_obs = max(d, 0.0)
        # 预测分布: 参数不确定 -> sigma_pred^2 = sigma^2 + tau2 (膨胀)
        sigma_pred = np.sqrt(sigma ** 2 + tau2)
        Q = critical_ratio_order(mu_b, sigma_pred, inv)
        inv += Q
        sold = min(inv, d_obs)
        inv -= sold
        short = d_obs - sold
        # 利润: 收入 - 进货 - 持有 (+缺货信誉损失忽略)
        profit = p * sold - c * Q - h * inv
        total += profit
        profits.append(profit)
        if learn:
            # 贝叶斯更新 (正态-正态共轭): 观测需求 d_obs ~ N(mu, sigma^2)
            tau2_new = 1 / (1 / tau2 + 1 / sigma ** 2)
            mu_b = tau2_new * (mu_b / tau2 + d_obs / sigma ** 2)
            tau2 = tau2_new
        else:
            # 不学习: 仅把观测当噪声
            pass
    return total, profits


tot_static, prof_s = run(learn=False)
tot_learn, prof_l = run(learn=True)

# 前10期 vs 后10期平均利润 (学习效应)
print("=" * 66)
print("多期报童: 静态 vs 基址策略+贝叶斯学习  (T=100期)")
print("=" * 66)
print(f"  累计利润  静态: {tot_static:9.1f}   学习: {tot_learn:9.1f}   "
      f"提升 {(tot_learn/tot_static-1)*100:+.1f}%")
print(f"  前10期均值 静态: {np.mean(prof_s[:10]):7.1f}   学习: {np.mean(prof_l[:10]):7.1f}")
print(f"  后10期均值 静态: {np.mean(prof_s[-10:]):7.1f}   学习: {np.mean(prof_l[-10:]):7.1f}")
print("""
  机制解读:
  1) 多期最优策略是'订货至基址 S*' (base-stock), 不是每期独立解
  2) 剩余可结转 -> 过储成本 co 加入持有成本 h; 缺货损失 cu 不变
  3) 参数不确定 -> 预测方差膨胀 (sigma^2 + tau^2), 订更多'信息保守量'
  4) 贝叶斯学习使 tau^2 -> 0, 后期订货量逼近真实最优 -> '学习曲线'利润
  5) 这就是'数据驱动的库存管理'(DDDL)的最简雏形; 现实版 = ML 预测 + 优化
""")
