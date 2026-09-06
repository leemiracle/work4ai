# -*- coding: utf-8 -*-
"""
OLS 小样本回归与标准误断言（走廊1：估计量动物园 + 走廊2：蒙特卡洛）
对应章：讲载数量经济学/04-数量经济学转代码.md

设计：DGP 已知（y = 1 + 0.5x + ε, ε~N(0,2²), x~U(2,10), n=24, 固定种子），
双实现（正规方程 vs lstsq）+ 经典/HC1 稳健标准误 + 小型蒙特卡洛，
全部断言脚本自验。数值：numpy 即可，无外部数据。
"""
import numpy as np

rng = np.random.default_rng(42)
N, K = 24, 2          # n=24 小样本，k=2（截距+斜率）
BETA_TRUE = np.array([1.0, 0.5])
SIGMA = 2.0

def make_data(n, rng):
    x = 2.0 + 8.0 * rng.random(n)            # x ~ U(2, 10)
    eps = SIGMA * rng.standard_normal(n)     # ε ~ N(0, 2²)
    y = BETA_TRUE[0] + BETA_TRUE[1] * x + eps
    X = np.column_stack([np.ones(n), x])
    return X, y, eps

def ols_full(X, y):
    """OLS 全套：系数、残差、经典 SE、HC1 稳健 SE、t、R²（手写实现）。"""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    rss = e @ e
    sigma2 = rss / (n - k)                   # 自由度价格：n-k
    se_classic = np.sqrt(sigma2 * np.diag(XtX_inv))
    meat = (X * (e ** 2)[:, None]).T @ X     # Σ e_i² x_i x_i'
    V_hc1 = XtX_inv @ meat @ XtX_inv * n / (n - k)
    se_robust = np.sqrt(np.diag(V_hc1))
    tss = ((y - y.mean()) ** 2).sum()
    return beta, e, se_classic, se_robust, rss / tss, tss

def main():
    X, y, eps = make_data(N, rng)

    # 断言1：双实现一致——正规方程 vs lstsq，两条独立路径同达
    beta_ne = np.linalg.solve(X.T @ X, X.T @ y)
    beta_ls, *_ = np.linalg.lstsq(X, y, rcond=None)
    assert np.allclose(beta_ne, beta_ls, atol=1e-10)
    assert np.allclose(beta_ne, ols_full(X, y)[0], atol=1e-10)
    print(f"[1] 双实现一致：正规方程 = lstsq = 手写 OLS = "
          f"({beta_ne[0]:.4f}, {beta_ne[1]:.4f})")

    # 断言2：小样本系数落在真值邻域（n=24 的抽样误差内）
    beta_hat, e, se_c, se_r, r2, _ = ols_full(X, y)
    assert abs(beta_hat[0] - BETA_TRUE[0]) < 0.9
    assert abs(beta_hat[1] - BETA_TRUE[1]) < 0.20
    print(f"[2] β̂ = ({beta_hat[0]:.3f}, {beta_hat[1]:.3f})，"
          f"真值 = ({BETA_TRUE[0]:.1f}, {BETA_TRUE[1]:.1f})（小样本邻域内）")

    # 断言3：R² 落在合理区间（信噪比中等：σ=2、x 跨度 8）
    assert 0.3 < r2 < 0.95, r2
    print(f"[3] R² = {r2:.3f}")

    # 断言4：斜率 t 统计量显著；自由度价格——分母 n vs n-k 的 SE 差
    t_stat = beta_hat[1] / se_c[1]
    assert t_stat > 2.0, t_stat
    se_naive = np.sqrt((e @ e) / N * np.linalg.inv(X.T @ X)[1, 1])
    print(f"[4] t = {t_stat:.2f}（>2 显著）；SE(斜率)：n-k 除法 {se_c[1]:.4f} "
          f"vs n 除法 {se_naive:.4f}（自由度价格 "
          f"{(se_naive/se_c[1]-1)*-100:.1f}% 的低估）")

    # 断言5：蒙特卡洛最小版——均值收束到真值；正态误差样本偏度≈0
    mc = []
    for _ in range(2000):
        Xm, ym, _ = make_data(N, np.random.default_rng())
        mc.append(np.linalg.lstsq(Xm, ym, rcond=None)[0][1])
    mc = np.array(mc)
    assert abs(mc.mean() - BETA_TRUE[1]) < 0.05, mc.mean()
    skew = ((eps - eps.mean()) ** 3).mean() / eps.std() ** 3
    # n=24 时偏度估计量标准误 ≈ sqrt(6/n) ≈ 0.5，区间放宽到 2 倍标准误
    assert abs(skew) < 1.0, skew
    print(f"[5] 蒙特卡洛 2000 次：均值 {mc.mean():.4f}（真值 0.5，无偏）；"
          f"正态样本偏度 {skew:+.2f}（n=24 偏度标准误≈0.5，容许带宽 1.0）"
          f"——'定义即程序'")

    # 断言6：HC1 稳健 SE 与经典 SE 同为正且数值不等——假设不同区间不同
    assert np.all(se_r > 0) and np.all(se_c > 0)
    ratio = se_r[1] / se_c[1]
    assert not np.isclose(ratio, 1.0, atol=1e-3) and 0.5 < ratio < 2.0
    print(f"[6] 斜率 SE：经典 {se_c[1]:.4f} vs HC1 稳健 {se_r[1]:.4f} "
          f"（比值 {ratio:.2f}）——同一样本，两套假设")

    print("\n全部断言通过 ✓ （双实现对账=数值代码的自验金标准）")

if __name__ == "__main__":
    main()
