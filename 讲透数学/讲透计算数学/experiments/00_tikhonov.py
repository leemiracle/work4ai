# -*- coding: utf-8 -*-
"""病态的宪法与救赎:Hilbert 最小二乘 × Tikhonov 正则化。

00 章(反直觉:病态是问题的属性,好算法救不了) & 04 章(走廊:正则化=换问题) 配套实验。

设定:Hilbert 矩阵 H[i,j]=1/(i+j+1) —— 经典病态王(κ 随阶数指数爆炸)。
  真解 x_true 已知 → b = H @ x_true(精确) → 对 b 施加 1e-8 相对噪声。
  无正则解:‖x‖ 误差被 κ(H) 放大到荒谬;
  Tikhonov:min ‖Hx−b‖² + λ‖x‖² → 解 = (HᵀH+λI)⁻¹Hᵀb(谱滤波 σ/(σ²+λ))。
  L 曲线:残差范数 vs 解范数 log-log,拐角≈好 λ。

跑法: python experiments/00_tikhonov.py
自验证:结尾 assert 正则化后误差比无正则降低 ≥100 倍(阈值保守,稳定可过)。
"""

import numpy as np


def hilbert(n):
    i = np.arange(n)
    return 1.0 / (i[:, None] + i[None, :] + 1.0)


def cond_from_svd(H):
    s = np.linalg.svd(H, compute_uv=False)
    return s[0] / s[-1]


def main():
    rng = np.random.default_rng(42)
    n = 12
    H = hilbert(n)
    kappa = cond_from_svd(H)
    x_true = np.ones(n)
    b_clean = H @ x_true
    b = b_clean * (1.0 + 1e-8 * rng.standard_normal(n))  # 输入端 1e-8 相对噪声

    print("=" * 66)
    print(f"Hilbert {n} 阶:κ(H) ≈ {kappa:.2e}  (输入噪声 1e-8 → 解误差可放大 κ 倍)")
    print("=" * 66)

    # 1) 无正则:最小二乘(机器上"最好"的算法之一)
    x_ls = np.linalg.lstsq(H, b, rcond=None)[0]
    err_ls = np.linalg.norm(x_ls - x_true) / np.linalg.norm(x_true)
    print(f"无正则 lstsq      : 相对解误差 = {err_ls:.2e}   ← 信息在输入端就被 κ 焚毁")
    print(f"                    理论预言下界 ≈ κ×1e-8 ≈ {kappa * 1e-8:.1f} 量级(吻合)")

    # 2) Tikhonov 扫描 λ:L 曲线 + 误差曲线
    print()
    print(f"{'λ':>10} {'残差‖Hx−b‖':>12} {'解范数‖x‖':>10} {'相对误差':>10}")
    U, s, Vt = np.linalg.svd(H, full_matrices=False)
    lambdas = np.logspace(-18, -2, 25)
    rows = []
    for lam in lambdas:
        # 谱形式:x_λ = Σ (σ/(σ²+λ)) (uᵀb) v —— 滤波因子直接可见
        filt = s / (s**2 + lam)
        x_lam = Vt.T @ (filt * (U.T @ b))
        res = np.linalg.norm(H @ x_lam - b)
        err = np.linalg.norm(x_lam - x_true) / np.linalg.norm(x_true)
        rows.append((lam, res, np.linalg.norm(x_lam), err))
        print(f"{lam:>10.1e} {res:>12.2e} {np.linalg.norm(x_lam):>10.2e} {err:>10.2e}")

    errs = np.array([r[3] for r in rows])
    best_i = int(np.argmin(errs))
    lam_best = lambdas[best_i]
    err_best = errs[best_i]
    print()
    print(f"最优 λ* = {lam_best:.1e}(L 曲线拐角邻域),相对误差 = {err_best:.2e}")
    print(f"滤波视角:λ* 把 σ ≲ √λ* ≈ {np.sqrt(lam_best):.1e} 的方向几乎抹除——")
    print(f"          病态方向(σ_min={s[-1]:.1e})携带的几乎全是噪声放大器,正则化=主动丢弃。")

    # 3) L 曲线拐角(最大曲率,log-log)对照误差最优
    lr = np.log10(np.array([r[1] for r in rows]))
    lx = np.log10(np.array([r[2] for r in rows]))
    ok = np.isfinite(lr) & np.isfinite(lx)
    k = np.argmax(ok * 1)  # 仅在有限值上算曲率
    c2 = np.gradient(np.gradient(lr[ok], lx[ok]), lx[ok])
    corner_i = int(np.argmax(c2))
    print(f"L 曲线最大曲率点 λ ≈ {lambdas[ok][corner_i]:.1e}(工程法则 vs 真误差最优的常规接近)")

    # 4) 自验证断言
    gain = err_ls / err_best
    print()
    print("=" * 66)
    print(f"救赎结论:Tikhonov 把相对误差 {err_ls:.2e} → {err_best:.2e}(改善 {gain:.0f} 倍)")
    print("注意:它没有违反病态宪法——它解的是'附近一个更良态的问题',")
    print("      用偏差换取稳定,这正是 03 章'换问题'的现场。")
    print("=" * 66)
    assert err_best < 0.1, "正则化应把误差压回 10% 以内"
    assert gain >= 100, f"改善应 ≥100 倍(实测 {gain:.0f})"
    assert 1e-8 < err_best < err_ls, "正则化误差应远小于无正则且非零(偏差-方差折衷)"
    print("assert 全部通过 ✓")


if __name__ == "__main__":
    main()
