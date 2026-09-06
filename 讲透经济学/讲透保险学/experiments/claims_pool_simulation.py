"""复合泊松风险池：大数定律、附加费率与破产概率（断言自验）
对应《讲透保险学》00 章（风险池三层结构）、03 章（Cramér-Lundberg 集体风险
模型与 Lundberg 直觉）、04 章（走廊 1：赔付模拟走廊）。

模型（集体风险模型，离散按年）：
    年理赔次数 N ~ Poisson(λ)，单次理赔额 X ~ LogNormal(μ, σ_L)
    年总赔付 S = Σᵢ Xᵢ；资本过程  U_t = u₀ + (1+θ)·λ·E[X]·t − Σ S
    （θ=附加费率，u₀=初始资本=0.5×年期望赔付）

断言（自验证）：
    (a) 大数定律：5000 个模拟年的平均赔付率与解析值 λ·E[X] 相对误差 < 2%；
        且 10 年滚动平均的波动 < 单年波动的 0.6 倍（池化 1/√T 效应，理论 0.32）
    (b) 有附加费率（θ=10%）：50 年生存概率 > 0.85（正漂移=安全垫）
    (c) 零附加费率（θ=0，纯保费定价）：同样 50 年破产概率远高于 (b)
        且 > 0.5 —— 零漂移随机游走的常返性：长期破产概率趋于 1
"""
import math
import numpy as np

LAM, MU, SIG_L = 100.0, 9.0, 0.8          # 泊松强度 / 对数正态参数
THETA, U0_FRAC = 0.10, 0.5                # 附加费率 / 初始资本占年期望赔付比例
N_YEARS, N_PATHS, T = 5000, 2000, 50
EX = math.exp(MU + SIG_L ** 2 / 2.0)      # 单次理赔期望 E[X]
MEAN_S = LAM * EX                         # 年期望赔付（纯保费）
rng = np.random.default_rng(42)


def compound_poisson(shape):
    """按 shape 抽复合泊松赔付（每单元=一个"年"的赔付总额 S）。"""
    n = rng.poisson(LAM, size=shape)
    x = rng.lognormal(MU, SIG_L, size=int(n.sum()))
    year_idx = np.repeat(np.arange(n.size), n)
    return np.bincount(year_idx, weights=x, minlength=n.size)


def ruin_prob(theta, n_paths=N_PATHS, years=T, seed=7):
    """模拟 n_paths 条资本路径，返回 years 年内破产（U<0）的频率。"""
    r = np.random.default_rng(seed)
    n = r.poisson(LAM, size=(n_paths, years))
    x = r.lognormal(MU, SIG_L, size=int(n.sum()))
    cell = np.repeat(np.arange(n.size), n.ravel())
    s = np.bincount(cell, weights=x, minlength=n.size).reshape(n.shape)
    u = U0_FRAC * MEAN_S + (1 + theta) * MEAN_S * np.arange(1, years + 1) - np.cumsum(s, axis=1)
    return float((u.min(axis=1) < 0).mean())


def main():
    # ── (a) 大数定律：年赔付率收敛 + 池化效应 ──
    s = compound_poisson(N_YEARS)
    rel = abs(s.mean() / MEAN_S - 1.0)
    blocks = s[: (N_YEARS // 10) * 10].reshape(-1, 10).mean(axis=1)   # 10 年滚动平均
    pool_eff = blocks.std() / s.std()
    print(f"(a) 大数定律：{N_YEARS} 年平均赔付={s.mean():,.0f}  解析={MEAN_S:,.0f}  "
          f"相对误差={rel*100:.2f}%   (断言 < 2%)")
    print(f"    池化效应：10 年均值波动/单年波动={pool_eff:.2f}  "
          f"(理论 1/√10≈0.32，断言 < 0.6)")
    assert rel < 0.02 and pool_eff < 0.6, "大数定律与 1/√T 池化应成立"

    # ── (b) 有附加费率：正漂移压住波动 ──
    ruin_b = ruin_prob(THETA)
    print(f"(b) θ=10%：{T} 年破产频率={ruin_b:.3f}  生存概率={1-ruin_b:.3f}  "
          f"(断言生存 > 0.85)")
    assert 1 - ruin_b > 0.85, "正漂移下生存概率应高"

    # ── (c) 纯保费（θ=0）：没有安全垫，长期破产趋于必然 ──
    ruin_c = ruin_prob(0.0)
    print(f"(c) θ=0 ：{T} 年破产频率={ruin_c:.3f}  与 (b) 之差={ruin_c-ruin_b:.3f}  "
          f"(断言 > 0.5 且差 > 0.2)")
    assert ruin_c > 0.5 and ruin_c - ruin_b > 0.2, "零附加费率下破产概率应显著更高"

    print("\n全部断言通过 ✅  附加费率 θ 的存在性一行代码讲完：")
    print("纯保费只保期望（长期必撞随机下行），安全附加买的是 Lundberg 的")
    print("指数安全垫——保费原理族的全部分歧就在'垫多厚'（03 章）。")

if __name__ == "__main__":
    main()
