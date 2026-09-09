"""
蒙特卡洛模拟与欧式期权定价
=========================
数学概念：蒙特卡洛方法 / 随机过程 / 几何布朗运动 (GBM) / 风险中性定价
应用领域：金融工程、衍生品定价、风险管理
核心思想：在风险中性测度下, 标的资产价格服从几何布朗运动 dS = rS dt + σS dW。
         通过大量模拟价格路径, 取到期日期权收益的期望, 再按无风险利率贴现, 即得期权价格。
         大数定律保证: 模拟次数 N → ∞ 时, MC 估计收敛到真实价格。
         与 Black-Scholes 解析公式对比可验证正确性。
运行方式：python "05-蒙特卡洛_期权定价.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 1. 参数设置 (欧式看涨期权) ============
S0 = 100.0       # 标的资产当前价格
K = 105.0        # 行权价
T = 1.0          # 到期时间 (年)
r = 0.05         # 无风险利率
sigma = 0.20     # 波动率
N_PATHS = 50000  # 蒙特卡洛模拟路径数
N_STEPS = 252    # 时间离散步数 (约一年的交易日)
np.random.seed(42)
print(f"[参数] S0={S0}, K={K}, T={T}年, r={r}, σ={sigma}")
print(f"[模拟] {N_PATHS} 条路径, {N_STEPS} 步/路径")

# ============ 2. 数学建模：几何布朗运动模拟 ============
def simulate_gbm_paths(S0, r, sigma, T, n_paths, n_steps):
    """
    用 Euler-Maruyama 离散化模拟几何布朗运动路径:
        S_{t+dt} = S_t * exp((r - σ²/2)dt + σ√dt * Z),  Z~N(0,1)
    返回路径矩阵 (n_paths, n_steps+1)。
    使用指数形式保证价格为正, 且与 GBM 解析解一致。
    """
    dt = T / n_steps
    # 生成标准正态随机数
    Z = np.random.standard_normal((n_paths, n_steps))
    # 漂移项与扩散项
    drift = (r - 0.5 * sigma ** 2) * dt
    diffusion = sigma * np.sqrt(dt) * Z
    # 累积收益并还原价格路径
    log_returns = np.cumsum(drift + diffusion, axis=1)
    paths = S0 * np.exp(log_returns)
    paths = np.column_stack([np.full(n_paths, S0), paths])  # 加入初始价格
    return paths

# ============ 3. 蒙特卡洛期权定价 ============
def mc_call_price(paths, K, r, T):
    """欧式看涨期权: payoff = max(S_T - K, 0), 折现求期望。"""
    ST = paths[:, -1]                               # 到期日价格
    payoff = np.maximum(ST - K, 0)                  # 期权收益
    price = np.exp(-r * T) * payoff.mean()          # 折现期望
    std_err = np.exp(-r * T) * payoff.std() / np.sqrt(len(payoff))
    return price, std_err

# 模拟路径
paths = simulate_gbm_paths(S0, r, sigma, T, N_PATHS, N_STEPS)
mc_price, se = mc_call_price(paths, K, r, T)

# ============ 4. Black-Scholes 解析解 (对比基准) ============
def black_scholes_call(S0, K, T, r, sigma):
    """Black-Scholes 欧式看涨期权定价公式。"""
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    price = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return price

bs_price = black_scholes_call(S0, K, T, r, sigma)
error = abs(mc_price - bs_price)
print(f"\n{'='*50}")
print(f"  Black-Scholes 解析价格 : {bs_price:.4f}")
print(f"  蒙特卡洛模拟价格       : {mc_price:.4f} ± {1.96*se:.4f} (95%CI)")
print(f"  绝对误差               : {error:.4f}")
print(f"  相对误差               : {error/bs_price*100:.2f}%")
print(f"{'='*50}")

# ============ 5. 可视化 ============
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
for i in range(min(100, N_PATHS)):           # 只画前 100 条避免过密
    ax.plot(np.linspace(0, T, N_STEPS + 1), paths[i], lw=0.5, alpha=0.3)
ax.axhline(K, color="r", ls="--", lw=1.2, label=f"行权价 K={K}")
ax.set_xlabel("时间 (年)")
ax.set_ylabel("资产价格")
ax.set_title(f"GBM 价格路径模拟 (展示 100/{N_PATHS} 条)")
ax.legend()

ax = axes[1]
ST = paths[:, -1]
ax.hist(ST, bins=100, density=True, alpha=0.7, color="steelblue", edgecolor="none")
ax.axvline(K, color="r", ls="--", lw=1.2, label=f"K={K}")
ax.axvline(ST.mean(), color="orange", ls="-", lw=1.2, label=f"均值={ST.mean():.1f}")
ax.set_xlabel("到期日价格 S_T")
ax.set_ylabel("概率密度")
ax.set_title("到期日价格分布")
ax.legend()

# 收敛曲线: 不同 N 对应的 MC 估计
ax = axes[2]
Ns = np.logspace(2, np.log10(N_PATHS), 30).astype(int)
prices = []
for n in Ns:
    p, _ = mc_call_price(paths[:n], K, r, T)
    prices.append(p)
ax.semilogx(Ns, prices, "b.-", lw=1)
ax.axhline(bs_price, color="r", ls="--", lw=1.5, label=f"BS={bs_price:.4f}")
ax.axhline(mc_price, color="g", ls=":", lw=1.5, label=f"MC={mc_price:.4f}")
ax.set_xlabel("模拟路径数 N")
ax.set_ylabel("期权价格")
ax.set_title("蒙特卡洛收敛过程 (大数定律)")
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("05-蒙特卡洛期权_结果.png", dpi=120)
print(f"\n[结果] 图像已保存: 05-蒙特卡洛期权_结果.png")
print("[解读] MC 估计随路径数增加收敛到 BS 解析解(相对误差 <1%), "
          "验证了风险中性定价与大数定律。MC 方法虽不如解析公式精确, "
          "但可轻松扩展到路径依赖期权(亚式/障碍), 是金融工程的核心数值方法。")

if __name__ == "__main__":
    pass
