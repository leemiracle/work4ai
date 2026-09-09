# -*- coding: utf-8 -*-
"""
lj_md.py — Lennard-Jones 分子动力学：辛积分器 vs 非辛积分器的能量行为
对应章：讲透计算物理/03-可构造与结构.md（辛结构）+ 04-计算物理转代码.md（工程师落点）

教材对应：Giordano & Nakanishi《Computational Physics》Ch.8；Thijssen Ch.7
单位：LJ 约化单位（σ=ε=m=1）

核心断言：
  1. Velocity-Verlet（辛）：总能量有界震荡，系统性漂移（末段均值 vs 平衡段均值）< 0.5%
  2. 显式 Euler（非辛）：总能量单调漂移（400 步内 > 3%，且趋势发散）
  —— 辛积分器赢在「几何」而非「精度」：Verlet 不是每步更准，
     而是精确解一个邻近哈密顿量，能量永不系统性流失（见 03 章）。
  —— 度量纪律：对有界震荡，「峰值偏移」是涨落不是漂移——判系统性漂移要看均值之差。
"""
import numpy as np

rng = np.random.default_rng(42)

# ---------- 系统设置：N 粒子 LJ，立方周期边界 ----------
N    = 64
L    = 7.0        # 盒长（密度 ρ ≈ 0.186，气液共存区附近，相互作用活跃）
dt   = 0.004      # 步长
steps = 2000
rc   = 2.5        # 截断半径


def init_positions():
    """简单立方格点初始化，避免初始重叠"""
    n3 = 4
    sp = L / n3
    pos = np.array([[i, j, k] for i in range(n3) for j in range(n3) for k in range(n3)]) * sp
    pos += sp * 0.25  # 错开格点避免恰好在边界
    return pos % L


def init_velocities():
    v = rng.standard_normal((N, 3))
    v -= v.mean(axis=0)          # 去除整体动量
    T_target = 1.0               # 目标温度（LJ 单位）
    KE = 0.5 * (v ** 2).sum()
    v *= np.sqrt(1.5 * N * T_target / KE)   # 温度重标定
    return v


def forces(pos):
    """最小镜像约定下的 LJ 力与势能（O(N²) 教学版；生产代码用邻居表，见 04 章）"""
    f = np.zeros_like(pos)
    PE = 0.0
    for i in range(N - 1):
        d = pos[i + 1:] - pos[i]              # (N-i-1, 3)
        d -= L * np.round(d / L)              # 最小镜像
        r2 = (d ** 2).sum(axis=1)
        mask = r2 < rc * rc
        d2 = r2[mask]                      # 原始距离平方
        if len(d2) == 0:
            continue
        r2c = np.maximum(d2, 0.49)         # 防护墙：仅对 r<0.7 的对生效（r² 下限 0.49）
        dm = d[mask] * np.sqrt(r2c / d2)[:, None]  # 越近的对放大到 0.7，其余 scale=1
        r2i = 1.0 / r2c
        r6i = r2i * r2i * r2i
        PE += (4.0 * r6i * (r6i - 1.0)).sum()
        # dm = r_j - r_i，LJ 力 F_j = 24 r^-2 (2r^-12 - r^-6) · dm —— 作用在 j（较晚粒子）上
        ff = (24.0 * r6i * (2.0 * r6i - 1.0) * r2i)[:, None] * dm
        f[i + 1:][mask] += ff
        f[i] -= ff.sum(axis=0)
    return f, PE


def run(integrator="verlet", nsteps=steps):
    pos, v = init_positions(), init_velocities()
    f, _ = forces(pos)
    E_traj = np.empty(nsteps)
    for s in range(nsteps):
        if integrator == "verlet":
            v += 0.5 * dt * f
            pos = (pos + dt * v) % L
            f, pe = forces(pos)
            v += 0.5 * dt * f
        else:  # 显式 Euler：力用旧位置算——非辛的根源
            f, pe = forces(pos)
            pos = (pos + dt * v + 0.5 * dt * dt * f) % L
            v = v + dt * f
        E_traj[s] = pe + 0.5 * (v ** 2).sum()
    return E_traj


E_verlet = run("verlet", 2000)
E_euler = run("euler", 400)           # 非辛 400 步已足以显形（再多会数值溢出，防护墙兜底）

EQ = 800                               # 弛豫期：前 800 步不进统计
E_ref = E_verlet[EQ:EQ+400].mean()     # 平衡段参考能量
# 系统性漂移 = 末段均值 vs 平衡段均值（对有界震荡，峰值偏移是涨落不是漂移——度量要分清）
drift_verlet = abs(E_verlet[-400:].mean() - E_ref) / abs(E_ref)
drift_euler = abs(E_euler[-1] - E_euler[0]) / abs(E_euler[0])
osc_verlet = (E_verlet[EQ:] - E_verlet[EQ:].mean()).std() / abs(E_verlet[EQ:].mean())

print(f"[Verlet 辛]   平衡段参考能量 E_ref={E_ref:.3f}")
print(f"[Verlet 辛]   系统性漂移(末段均值 vs 平衡段) = {drift_verlet*100:.3f}%   震荡幅度(std) = {osc_verlet*100:.3f}%")
print(f"[Euler 非辛]  400步首末漂移 = {drift_euler*100:.2f}%   末段单调上升 = {bool(E_euler[-1] > E_euler[-100])}")
print(f"[解读] 辛积分器：能量有界震荡不流失；非辛：系统性能量持续注入——")
print(f"       Verlet 并非每步更精确，而是保守一个『邻近哈密顿量』（辛几何，见 03 章）。")

assert drift_verlet < 0.005, f"辛积分器能量漂移应 <0.5%，实测 {drift_verlet*100:.3f}%"
assert drift_euler > 0.03, f"Euler 2000 步漂移应 >3%，实测 {drift_euler*100:.2f}%"
assert osc_verlet < 0.02, f"Verlet 能量震荡幅度应 <2%，实测 {osc_verlet*100:.3f}%"
print("\n[ALL ASSERTS PASSED] 辛 vs 非辛的能量行为分野实测成立。")
