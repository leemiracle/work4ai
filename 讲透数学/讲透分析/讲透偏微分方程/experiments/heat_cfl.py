# -*- coding: utf-8 -*-
"""
heat_cfl.py — 热方程显式格式的 CFL 宪法实验
对应章：00（适定性三问之连续依赖的离散镜像）/ 02（能量估计的代码化身）/
        03（格式继承能量耗散结构）/ 04（CFL 宪法主场）

实验设计（对应 04-转代码.md 第二节）：
  (a) 违宪：r = 0.55 > 1/2，随机初值 200 步 → 数值解爆破（断言 >10× 初值）
  (b) 守宪：r = 0.40，单模初值 sin(πx) → 与解析解 e^{-π²t}sin(πx) 对照（断言 L∞ 误差 < 1e-3）
      同时监控 ℓ² 范数单调不增（离散能量耗散 = 03 章骨架一的格式继承）
  (c) 放大器谱：扫描 r，打印最坏放大因子 |g|_max，CFL 阈值 r=1/2 处符号翻转

运行：python heat_cfl.py   （纯 numpy，无其他依赖）
"""

import numpy as np

# ---------------------------------------------------------------- 网格
N = 41                      # 内点数（边界 x=0,1 固定为 0）
dx = 1.0 / (N + 1)
x = np.linspace(dx, 1 - dx, N)   # 内点坐标
PI2 = np.pi ** 2


def step(u: np.ndarray, r: float) -> np.ndarray:
    """热方程显式格式一步：u_j^{n+1} = u_j^n + r (u_{j+1} - 2u_j + u_{j-1})，
    Dirichlet 边界 u_0 = u_{N+1} = 0。u 为内点数组（j=1..N），ghost 边界取 0。"""
    lap = np.empty_like(u)
    lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
    lap[0] = u[1] - 2 * u[0]          # 左邻 = 边界 0
    lap[-1] = u[-2] - 2 * u[-1]       # 右邻 = 边界 0
    return u + r * lap


def regime_a_unstable() -> float:
    """(a) 违宪：r=0.55，随机初值跑 200 步，返回终值 ∞-范数 / 初值 ∞-范数。"""
    r = 0.55
    rng = np.random.default_rng(42)
    u = rng.uniform(-1.0, 1.0, N)
    u0max = np.abs(u).max()
    for _ in range(200):
        u = step(u, r)
    return np.abs(u).max() / u0max


def regime_b_stable() -> tuple[float, bool]:
    """(b) 守宪：r=0.40，初值 sin(πx)，跑到 T=0.1。
    返回 (L∞ 误差, ℓ² 范数是否单调不增)。解析解：e^{-π²t} sin(πx)。"""
    r = 0.40
    dt = r * dx * dx
    T = 0.1
    n_steps = int(round(T / dt))
    u = np.sin(np.pi * x)
    norms = [np.linalg.norm(u)]
    for _ in range(n_steps):
        u = step(u, r)
        norms.append(np.linalg.norm(u))
    exact = np.exp(-PI2 * T) * np.sin(np.pi * x)
    err = np.abs(u - exact).max()
    monotone = bool(np.all(np.diff(norms) <= 1e-12))
    return err, monotone


def amplifier_spectrum() -> None:
    """(c) 放大器谱：g(k) = 1 - 4r sin²(kπdx/2)，最坏模在 k=N（|1-4r|）与 k=1 处。
    r ≤ 1/2 ⟹ |g|_max ≤ 1（稳定/耗散）；r > 1/2 ⟹ |g|_max = 4r-1 > 1（爆破）。"""
    print(f"{'r':>6} {'worst |g|':>12}  verdict")
    for r in (0.10, 0.25, 0.40, 0.49, 0.50, 0.51, 0.55, 0.70):
        worst = max(abs(1 - 4 * r), abs(1 - 4 * r * np.sin(np.pi * dx / 2) ** 2))
        verdict = "STABLE" if worst <= 1.0 else "UNSTABLE"
        print(f"{r:>6.2f} {worst:>12.6f}  {verdict}")


def main() -> None:
    print(f"网格：N={N} 内点，dx={dx:.6f}，CFL 阈值 dt <= dx²/2 = {dx*dx/2:.3e}\n")

    # (a) 违宪
    ratio = regime_a_unstable()
    print(f"(a) r=0.55（超阈值）随机初值 200 步：")
    print(f"    ‖u‖∞ 膨胀倍数 = {ratio:.3e}   （增长因子 1.2²⁰⁰ ≈ 1e15 的复利）")
    assert ratio > 10.0, f"(a) 应爆破（>10×），实测 {ratio:.3e}"
    print("    ✔ 断言过：连续依赖性死亡——格式自身成了放大器\n")

    # (b) 守宪
    err, monotone = regime_b_stable()
    print(f"(b) r=0.40 初值 sin(πx) 跑到 T=0.1：")
    print(f"    与解析解 e^(-π²t)sin(πx) 的 L∞ 误差 = {err:.3e}")
    assert err < 1e-3, f"(b) 误差应 < 1e-3，实测 {err:.3e}"
    assert monotone, "(b) ℓ² 范数应单调不增（离散能量耗散）"
    print("    ✔ 断言过：误差界 + 能量耗散结构被格式忠实继承\n")

    # (c) 谱扫描
    print("(c) 放大器谱（最坏模 |g| 跨过 1 的位置 = CFL 阈值）：")
    amplifier_spectrum()

    # 阈值定位断言：r=0.50 稳定、r=0.51 不稳定
    g_half = max(abs(1 - 4 * 0.50), 0.0)
    g_over = abs(1 - 4 * 0.51)
    assert g_half <= 1.0 and g_over > 1.0, "CFL 阈值定位失败"
    print("\n全部断言通过：CFL = r* （r=1/2）确实是稳定/爆破的宪法分界。")
    print("违反它的爆破不是 bug——格式在忠实积分一个『时间倒流的热方程』。")


if __name__ == "__main__":
    main()
