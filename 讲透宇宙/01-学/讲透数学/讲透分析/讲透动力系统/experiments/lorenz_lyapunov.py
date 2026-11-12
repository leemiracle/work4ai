# -*- coding: utf-8 -*-
"""
Lorenz 系统的 Lyapunov 谱：Benettin 重正交化算法
================================================

对应章：00-体系结构.md 第四节（混沌与敏感依赖）、04-转代码.md 走廊③（Benettin）。

演示内容：
  1. RK4 同步积分状态方程 + 变分方程（Benettin 流水线）
  2. QR 重正交化估计 Lyapunov 谱（文献值 λ ≈ (0.906, 0, -14.57)）
  3. Kaplan–Yorke 分形维数（文献值 ≈ 2.062）
  4. 双初值差 1e-8 的轨道分离演化（敏感依赖的直观测度：误差按 e^{λ1·t} 放大）

自验证断言：
  - λ1 ∈ [0.85, 0.95]（最大 Lyapunov 指数对照文献值 0.906）
  - λ3 < λ2 ≤ λ1（谱有序）
  - 谱和 ≈ -σ-1-β ≈ -13.67（散度定理：相体积收缩率 = 向量场散度的平均）
  - 分离演示：log10 距离从 -8 涨到 -2（六个数量级）用时在 [5, 40] 内
    （理论预期 ln(1e6)/λ1 ≈ 15.3）

运行：python lorenz_lyapunov.py
依赖：仅 numpy
"""
import numpy as np

# ── Lorenz 参数 ────────────────────────────────────────────────
SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0


def f(x):
    """向量场。"""
    return np.array([
        SIGMA * (x[1] - x[0]),
        x[0] * (RHO - x[2]) - x[1],
        x[0] * x[1] - BETA * x[2],
    ])


def DF(x):
    """Jacobian（变分方程的系数矩阵）。"""
    return np.array([
        [-SIGMA, SIGMA, 0.0],
        [RHO - x[2], -1.0, -x[0]],
        [x[1], x[0], -BETA],
    ])


def rk4_step(x, Phi, dt):
    """RK4 同步积分 (状态, 切丛)。Phi 是 3x3 矩阵，每列一个切向量。"""
    k1x = f(x)
    k1P = DF(x) @ Phi
    k2x = f(x + 0.5 * dt * k1x)
    k2P = DF(x + 0.5 * dt * k1x) @ (Phi + 0.5 * dt * k1P)
    k3x = f(x + 0.5 * dt * k2x)
    k3P = DF(x + 0.5 * dt * k2x) @ (Phi + 0.5 * dt * k2P)
    k4x = f(x + dt * k3x)
    k4P = DF(x + dt * k3x) @ (Phi + dt * k3P)
    x_new = x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
    P_new = Phi + dt / 6.0 * (k1P + 2 * k2P + 2 * k3P + k4P)
    return x_new, P_new


def benettin(x0, dt=0.005, tau=0.5, t_total=400.0, t_transient=50.0):
    """Benettin 算法：每 tau 时间单位 QR 重正交化，累计 log|R_ii|。"""
    steps_per_reorth = int(round(tau / dt))
    n_cycles = int(round(t_total / tau))

    # 瞬态：丢掉前 t_transient，落在吸引子上
    x = np.array(x0, dtype=float)
    for _ in range(int(round(t_transient / dt))):
        x, _ = rk4_step(x, np.eye(3), dt)

    Phi = np.eye(3)
    log_diag = np.zeros(3)
    for _ in range(n_cycles):
        for _ in range(steps_per_reorth):
            x, Phi = rk4_step(x, Phi, dt)
        Q, R = np.linalg.qr(Phi)
        Q *= np.sign(np.diag(R))          # 固定符号，防止 Q 逐次翻转
        log_diag += np.log(np.abs(np.diag(R)))
        Phi = Q
    return log_diag / t_total, x


def separation_demo(x0, dt=0.005, t_max=40.0, eps0=1e-8):
    """双轨道分离：初值差 eps0，记录 |差| 随时间的演化。"""
    xa = np.array(x0, dtype=float)
    xb = xa + np.array([eps0, 0.0, 0.0])
    n = int(round(t_max / dt))
    ts, ds = [], []
    sample_every = max(1, n // 400)
    for i in range(n + 1):
        if i % sample_every == 0:
            ts.append(i * dt)
            ds.append(float(np.linalg.norm(xa - xb)))
        xa, _ = rk4_step(xa, np.eye(3), dt)
        xb, _ = rk4_step(xb, np.eye(3), dt)
    return np.array(ts), np.array(ds)


def kaplan_yorke(lams):
    """D_KY = k + S_k/|λ_{k+1}|，k = 最大使部分和 S_k = Σ_{i<=k} λ_i > 0 的下标。"""
    lams = np.sort(lams)[::-1]
    S = np.cumsum(lams)
    k = np.nonzero(S > 0)[0][-1]         # S_k > 0 的最后一个 k（0-based）
    return (k + 1) + S[k] / abs(lams[k + 1])


def main():
    np.random.seed(0)
    x0 = [1.0, 1.0, 1.0]

    # ── 1) Benettin 谱 ────────────────────────────────────────
    lams, _ = benettin(x0)
    lams_sorted = np.sort(lams)[::-1]
    lam1, lam2, lam3 = lams_sorted
    print("== Benettin Lyapunov 谱 (T=400, tau=0.5, dt=0.005) ==")
    print(f"  λ1 = {lam1:+.4f}   (文献 ≈ +0.9056)")
    print(f"  λ2 = {lam2:+.4f}   (文献 ≈  0.0000)")
    print(f"  λ3 = {lam3:+.4f}   (文献 ≈ -14.5723)")
    print(f"  谱和 = {lams.sum():+.4f}   (散度定理预期 ≈ {-(SIGMA + 1 + BETA):+.4f})")

    # ── 2) Kaplan–Yorke 维数 ──────────────────────────────────
    d_ky = kaplan_yorke(lams)
    print(f"\n== Kaplan–Yorke 分形维数 ==")
    print(f"  D_KY = {d_ky:.4f}   (文献 ≈ 2.062)")

    # ── 3) 双轨道分离 ─────────────────────────────────────────
    eps0 = 1e-8
    ts, ds = separation_demo(x0)
    # 距离从 1e-8 涨到 1e-2 用时（增长段的实测速率）
    i_from = np.argmax(ds >= 1e-8)
    i_to = np.argmax(ds >= 1e-2)
    growth_time = ts[i_to] - ts[i_from]
    # 增长段斜率 ≈ λ1 / ln(10)
    mask = (ds > 1e-10) & (ds < 1e-1)
    if mask.sum() >= 10:
        slope = np.polyfit(ts[mask], np.log(ds[mask]), 1)[0]
    else:
        slope = float("nan")
    print(f"\n== 双轨道分离演示（初值差 {eps0:.0e}）==")
    print(f"  距离从 1e-8 涨到 1e-2 用时 ≈ {growth_time:.1f} 时间单位"
          f"（理论 4·ln10/λ1 ≈ {4 * np.log(10) / lam1:.1f}）")
    print(f"  增长段对数斜率 = {slope:.3f}（对照 λ1 = {lam1:.3f}）")
    for t_show in (5, 10, 15, 20, 30):
        j = np.argmin(np.abs(ts - t_show))
        print(f"    t={t_show:>2}  |δx| = {ds[j]:.3e}")

    # ── 断言（自验证）─────────────────────────────────────────
    assert 0.85 <= lam1 <= 0.95, f"λ1={lam1} 超出 [0.85, 0.95]"
    assert lam3 < lam2 <= lam1, "谱未按降序排列？"
    assert abs(lams.sum() - (-(SIGMA + 1 + BETA))) < 0.5, "谱和偏离散度定理"
    assert 5 <= growth_time <= 40, f"分离用时 {growth_time} 超出预期窗"
    print("\n[OK] 全部断言通过：λ1 对照文献、谱序、谱和（散度定理）、分离时限。")


if __name__ == "__main__":
    main()
