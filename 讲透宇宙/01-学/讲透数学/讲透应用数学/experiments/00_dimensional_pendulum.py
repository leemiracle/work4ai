# -*- coding: utf-8 -*-
"""Buckingham π 定理现场：从单位推摆周期，再数值验证。

00 章 · 体系结构 配套实验。纯标准库。

第一部分（纸笔推理的机器重演）：摆周期 T 依赖 L, m, g, θ₀。
量纲表：[T]=t, [L]=l, [m]=M, [g]=l/t²。
设 T = L^a m^b g^c · Φ(θ₀)，解量纲方程 t = l^{a+c} M^b t^{-2c}：
  b=0（质量不进门！）、a+c=0、-2c=1 ⟹ c=-1/2, a=+1/2
  ⟹ T = √(L/g) · Φ(θ₀) ——不解任何 ODE 拿到的骨架。

第二部分（数值验证）：RK4 积分单摆，log-log 拟合 T vs L 的斜率 ≈ 0.5。

跑法: python3 -u experiments/00_dimensional_pendulum.py
"""
import math

G = 9.81


def period_by_rk4(L, theta0=0.2, dt=1e-4, tmax=30.0):
    """RK4 积分 θ'' = -(g/L)·sin θ，测第一个完整周期（两次同向过零）。"""
    def deriv(s):
        th, om = s
        return (om, -(G / L) * math.sin(th))

    s = (theta0, 0.0)
    t, crossings = 0.0, []
    prev = s[0]
    while t < tmax:
        k1 = deriv(s)
        k2 = deriv((s[0] + dt / 2 * k1[0], s[1] + dt / 2 * k1[1]))
        k3 = deriv((s[0] + dt / 2 * k2[0], s[1] + dt / 2 * k2[1]))
        k4 = deriv((s[0] + dt * k3[0], s[1] + dt * k3[1]))
        s = (s[0] + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
             s[1] + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]))
        t += dt
        if prev < 0 <= s[0] and crossings:
            pass
        if prev * s[0] < 0 or (prev == 0 and s[0] != 0):
            crossings.append(t)
            if len(crossings) >= 3:
                return crossings[2] - crossings[0]   # 同向相邻过零 = 整周期
        prev = s[0]
    raise RuntimeError("没测到周期")


def main():
    print("=" * 62)
    print("① Buckingham π：单位推理（机器重演纸笔）")
    print("=" * 62)
    print("设 T = L^a·m^b·g^c·Φ(θ₀)，量纲方程 t = l^{a+c}·M^b·t^{-2c}：")
    print("  M:  b = 0        ← 质量被单位开除（伽利略比萨斜塔的量纲版）")
    print("  l:  a + c = 0")
    print("  t:  -2c = 1  ⟹  c = -1/2, a = +1/2")
    print("  ⟹  T = √(L/g)·Φ(θ₀)   ——零 ODE，零求解，纯单位")
    print()

    print("=" * 62)
    print("② RK4 数值验证：log T–log L 斜率应为 0.5")
    print("=" * 62)
    Ls = [0.25, 0.5, 1.0, 2.0, 4.0]
    rows = []
    for L in Ls:
        T_sim = period_by_rk4(L)
        T_dim = 2 * math.pi * math.sqrt(L / G)     # 小角公式（Φ(0)→2π 由分析补）
        rows.append((math.log(L), math.log(T_sim)))
        print(f"  L={L:>4}: 模拟周期 {T_sim:.5f}s | 2π√(L/g) {T_dim:.5f}s "
              f"| 偏差 {100*(T_sim/T_dim-1):+.2f}%")
    # 最小二乘斜率
    n = len(rows)
    sx = sum(x for x, _ in rows)
    sy = sum(y for _, y in rows)
    sxx = sum(x * x for x, _ in rows)
    sxy = sum(x * y for x, y in rows)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    print(f"\n  log-log 拟合斜率 = {slope:.4f}   （π 定理预言 0.5000）")
    print(f"  偏差来源：θ₀=0.2 的非线性修正 Φ(θ₀)>2π（量纲给的骨架不含常数——Buckingham 的边界）")
    print()
    print("收束：量纲分析给出形态 T∝L^{1/2}，数值验证形态；")
    print("      常数 2π 与 Φ(θ₀) 是分析/计算环的活——三环分工的微缩标本 💡")


if __name__ == "__main__":
    main()
