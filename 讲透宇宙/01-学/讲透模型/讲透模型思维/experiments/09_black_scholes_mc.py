"""09_black_scholes_mc — 公式对、假设错：BS 闭式 vs 蒙特卡洛，然后换掉高斯假设

问题分两半：
  A. 公式对不对？  GBM 下的欧式 call：Black-Scholes 闭式 vs 蒙特卡洛（10^5 路径）。
                   两者应在蒙特卡洛标准误内一致——公式没问题。
  B. 假设对不对？  同一个框架，把高斯步进换成 Student-t（nu=3，方差归一），
                   各置信级 VaR 两版对比——肥尾下高斯 VaR 低估多少？
                   （nu=3 不是拍脑袋：实证研究常把股票收益的尾指数估在 3 附近，
                    即"逆立方律"，可查 Gopikrishnan et al. 1998 对美股的研究。）
结论：公式（无套利定价）与假设（收益服从高斯）是两件独立的事——
      2008 的模型风险在后者，不在前者。
"""
import math

import numpy as np

rng = np.random.default_rng(42)

# ---- A. Black-Scholes 闭式 vs 蒙特卡洛 ----
S0, K, r, sigma, T = 100.0, 100.0, 0.03, 0.2, 1.0
mu = 0.05  # 真实漂移只影响"真实世界"概率；风险中性定价里进公式的只有 r

def N(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

d1 = (math.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
d2 = d1 - sigma * math.sqrt(T)
bs = S0 * N(d1) - K * math.exp(-r * T) * N(d2)

n_paths = 100_000
Z = rng.standard_normal(n_paths)
ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * Z)
payoff = np.maximum(ST - K, 0.0)
mc = math.exp(-r * T) * payoff.mean()
mc_se = math.exp(-r * T) * payoff.std() / math.sqrt(n_paths)

print("[A] 平价期权 S0=K=100, r=3%, sigma=20%, T=1")
print(f"    Black-Scholes 闭式      = {bs:.4f}")
print(f"    蒙特卡洛 1e5 路径       = {mc:.4f} ± {mc_se:.4f}（1 倍标准误）")
print(f"    误差 {abs(mc - bs):.4f} = {abs(mc - bs) / bs:.2%} —— 与标准误同量级：公式没问题")
print(f"    （mu={mu} 没进任何价格——定价在风险中性测度下做，mu 属于另一个问题）")
print()

# ---- B. 高斯 vs Student-t：同一 sigma，只换尾 ----
h = 1.0 / 252.0                     # 1 个交易日
sig_d = sigma / math.sqrt(252.0)    # 日波动率
drift = (mu - 0.5 * sigma**2) * h   # 日对数收益漂移
nu = 3.0

n = 500_000
ret_g = drift + sig_d * rng.standard_normal(n)                     # 高斯世界
t_unit = rng.standard_t(nu, size=n) * math.sqrt((nu - 2.0) / nu)  # t(3) 归一到单位方差
ret_t = drift + sig_d * t_unit                                     # 同 sigma 同漂移，只有尾不同

print("[B] 同一组合、同一日波动率 sigma_d={:.4%}、同一漂移，只换步进分布：".format(sig_d))
print("    高斯 N(0,1)  vs  Student-t(nu=3, 方差归一)——t 尾按 x^-3（幂律）衰减，高斯按 e^-x^2/2")
print(f"    {'置信级':>7} {'高斯VaR':>9} {'t-VaR':>9} {'t/高斯':>7} {'高斯阈值在t世界的突破率':>14} {'声称':>6}")
for level in (0.95, 0.99, 0.995, 0.999):
    q = 1.0 - level
    var_g = -np.quantile(ret_g, q)
    var_t = -np.quantile(ret_t, q)
    breach = float(np.mean(ret_t < -var_g))
    print(f"    {level:7.1%} {var_g:9.3%} {var_t:9.3%} {var_t / var_g:7.2f} "
          f"{breach:16.3%} {q:6.1%}")

g95, t95 = -np.quantile(ret_g, 0.05), -np.quantile(ret_t, 0.05)
g99, t99 = -np.quantile(ret_g, 0.01), -np.quantile(ret_t, 0.01)
g999, t999 = -np.quantile(ret_g, 0.001), -np.quantile(ret_t, 0.001)
b99 = float(np.mean(ret_t < -g99))
b999 = float(np.mean(ret_t < -g999))
print()
print(f"结论性数字：")
print(f"  99% 档：肥尾真值比高斯报告值高 {t99 / g99 - 1:.0%}，突破频率 {b99:.2%}（声称 1%）")
print(f"          —— 一年 250 个交易日，高斯模型承诺 {250 * 0.01:.1f} 次例外，肥尾世界约 {250 * b99:.0f} 次")
print(f"  99.9% 档：VaR 被低估 {t999 / g999 - 1:.0%}，突破频率放大 {b999 / 0.001:.1f} 倍")
print(f"  95% 档：高斯反而高估 {g95 / t95 - 1:.0%}——t 分布肩膀比高斯薄，同一 sigma 下"
      " 95% 分位反而更小：错的方向随分位水平翻转")
print("  公式没有错，错的是'收益是高斯的'这个假设——这就是 2008 模型风险的缩影。")
