"""一维热传导 FTCS 显式格式：稳定性宪法 + 收敛阶实测
对应《讲透热学》00 章（输运层）与 04 章（走廊 2）。

对读（同部宪法、两种执法）：
    ../../../讲透数学/讲透分析/讲透偏微分方程/experiments/heat_cfl.py
    —— 那边演示 CFL 分界翻转（r=0.50→0.51 放大因子谱翻转）；
    —— 这边测量误差收敛阶（时间一阶/空间二阶，r 固定时整体二阶）。

量纲纪律（工程代码第一守则）：
    本脚本用无量纲化单位（α=1 m²/s 示意、域 L=1 m、t 以秒计）；
    实际材料只需替换 α：铜 k=400 W/(m·K)、ρ=8960 kg/m³、c=385 J/(kg·K)
    ⟹ α = k/(ρc) ≈ 1.16e-4 m²/s，同一套代码原样适用。

断言（自验证）：
    (a) r=0.4 守宪：稳定，且与解析解 u=sin(πx)·exp(-α π² t) 的 L2 误差 < 5e-3
    (b) r=0.6 违宪：数值爆破解 L∞ 范数 > 初始范数 × 10（格式忠实积分"时间倒流的热方程"）
    (c) 收敛阶：固定 r=0.4，Δx 逐次减半，误差比 ∈ [3, 5]（整体 ~O(h²)）
"""
import numpy as np

def solve_ftcs(N, r, t_end, alpha=1.0, L=1.0):
    """FTCS 求解 u_t = α u_xx，u0=sin(πx)，两端 Dirichlet 0。
    返回最终温度场与网格步长。"""
    dx = L / (N + 1)
    dt = r * dx * dx / alpha                     # 稳定性由 r=αΔt/Δx² 把守
    steps = int(round(t_end / dt))
    x = np.linspace(0, L, N + 2)
    u = np.sin(np.pi * x)
    u[0] = u[-1] = 0.0
    for _ in range(steps):
        u[1:-1] = u[1:-1] + r * (u[2:] - 2 * u[1:-1] + u[:-2])
    return u, x, dx

def l2_err(u, x, t_end, alpha=1.0):
    """与解析解 u=sin(πx)·exp(-α π² t) 的 L2 误差（含边界）。"""
    exact = np.sin(np.pi * x) * np.exp(-alpha * np.pi**2 * t_end)
    return np.sqrt(np.mean((u - exact) ** 2))

def main():
    alpha, L, t_end = 1.0, 1.0, 0.10

    # ── (a) r=0.4 守宪：稳定 + 与解析解对照 ──
    u, x, dx = solve_ftcs(N=99, r=0.4, t_end=t_end, alpha=alpha)
    err = l2_err(u, x, t_end, alpha)
    print(f"(a) r=0.4  N=99   L2误差 = {err:.2e}   (断言 < 5e-3)")
    assert err < 5e-3, "守宪格式应收敛到解析解"

    # ── (b) r=0.6 违宪：爆破解 ──
    u_bad, x_bad, _ = solve_ftcs(N=99, r=0.6, t_end=t_end, alpha=alpha)
    growth = np.max(np.abs(u_bad)) / 1.0         # 初始 max|u|=1
    print(f"(b) r=0.6  N=99   L∞范数增长 = {growth:.2e}×   (断言 > 10×)")
    assert growth > 10.0, "违宪格式必爆（在忠实积分时间倒流的热方程）"

    # ── (c) 收敛阶：Δx 减半，r 固定 ⟹ Δt=rΔx² 同步缩，整体 ~二阶 ──
    errs = []
    for N in (39, 79, 159):
        u, x, _ = solve_ftcs(N=N, r=0.4, t_end=t_end, alpha=alpha)
        errs.append(l2_err(u, x, t_end, alpha))
    ratios = [errs[i] / errs[i + 1] for i in range(len(errs) - 1)]
    print(f"(c) 逐次减半误差比 = {[f'{r_:.2f}' for r_ in ratios]}   (断言各 ∈ [3,5]，~O(h²))")
    assert all(3.0 < r_ < 5.0 for r_ in ratios), "整体收敛阶应约为二"

    print("\n全部断言通过 ✅  FTCS：宪法在 r=1/2，误差阶在 O(h²)。")
    print("带走一句（04 章）：热阻网络管 80/20，FTCS/FVM 管最后两个 9。")

if __name__ == "__main__":
    main()
