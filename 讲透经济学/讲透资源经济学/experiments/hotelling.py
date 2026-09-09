#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotelling 法则最小模拟（对应 00 章✨美之时刻、03 章§二结构定理、04 章走廊①）。

设定：线性需求 q = 100 − p，初始存量 S = 600，利率 r = 5%，后备技术价 p_b = 50。
闭式（实数 T 延拓）：T(p0) = ln(p_b/p0)/ln(1+r)，累计开采
  C(p0) = 100·T − (p_b − p0)/r        [几何级数用 (1+r)^T = p_b/p0 整体坍缩]
C(p0) 单调递减，二分法解 C(p0) = 600 唯一钉死 p0。

断言：
  A. 价格路径逐期恰以 r 复利（p_{t+1}/p_t = 1.05，单调无跳跃）——离散模拟自检
  B. 切换点 p_T = p_b（容差 1e-6）且闭式累计−存量残差 < 1e-6（存量恰耗尽）
  C. 比较静态 r=10%：p0 更低、T 更短、前半窗口开采占比更高（开采前载）
  D. 绿色悖论：p_b 50→40 → 切换提前（T 更短）、固定前 4 期窗口累计开采更高
     （存量持有者抢在更低的价格天花板压顶前放量——Sinn 2008 的数值现场）
"""
import numpy as np

A_DEM, S0, R0, PB = 100.0, 600.0, 0.05, 50.0

def path_closed(p0, r, pb, a=A_DEM):
    """闭式：切换期 T（实数）与累计开采 C(p0)。"""
    T = np.log(pb / p0) / np.log(1.0 + r)
    C = a * T - (pb - p0) / r
    return T, C

def solve_p0(r, pb, S=S0, a=A_DEM):
    """二分法解 C(p0) = S。C 单调递减：p0→0 给 C→∞，p0→p_b 给 C→0。"""
    lo, hi = 1e-9, pb * (1.0 - 1e-12)
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if path_closed(mid, r, pb, a)[1] > S:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

def simulate(p0, r, pb, a=A_DEM):
    """离散逐期模拟：p_t = p0(1+r)^t，开采到 p_t >= p_b（该期切换后备）。"""
    p, t = [], 0
    while p0 * (1.0 + r) ** t < pb:
        p.append(p0 * (1.0 + r) ** t)
        t += 1
    p = np.array(p)
    return p, a - p

# ---------- 基准解 ----------
p0 = solve_p0(R0, PB)
T, C = path_closed(p0, R0, PB)
p_sim, q_sim = simulate(p0, R0, PB)
print(f"[基准] p0 = {p0:.4f}，闭式 T = {T:.4f} 期，累计开采 C = {C:.6f}（存量 {S0:.0f}）")
print(f"[基准] 离散模拟 {len(p_sim)} 期开采，累计 {q_sim.sum():.2f}；切换期价格 p_T = {p0*1.05**T:.6f}（后备价 {PB}）")

# A. 价格逐期恰以 r 复利，单调无跳
ratios = p_sim[1:] / p_sim[:-1]
print(f"[A] 逐期价格比 min={ratios.min():.12f} max={ratios.max():.12f}（应为 1.05）")
assert np.allclose(ratios, 1.0 + R0, atol=1e-12), "价格比值偏离 1+r——路径构造有 bug"
assert np.all(np.diff(p_sim) > 0), "价格非单调——路径有 bug"

# B. 切换点价格=后备价，存量恰耗尽（闭式账）
assert abs(p0 * (1.0 + R0) ** T - PB) < 1e-6, "切换点价格偏离后备价"
assert abs(C - S0) < 1e-6, "闭式累计开采残差超标——二分未收敛"
print(f"[B] p_T − p_b = {p0*1.05**T - PB:+.2e}，|C − S| = {abs(C - S0):.2e}（均 < 1e-6）✓")

# C. r = 10%：p0 更低、T 更短、前半窗口开采占比更高
def front_share(r, pb, S=S0, a=A_DEM):
    """闭式前半窗口（T/2）累计开采占总量比例 = 开采前载度。"""
    p0_ = solve_p0(r, pb, S, a)
    T_ = path_closed(p0_, r, pb, a)[0]
    front = a * (T_ / 2) - p0_ * ((1.0 + r) ** (T_ / 2) - 1.0) / r
    return p0_, T_, front / S

p0_c, T_c, share_c = front_share(0.10, PB)
share_0 = front_share(R0, PB)[2]
print(f"[C] r=10%: p0={p0_c:.4f} < {p0:.4f}，T={T_c:.4f} < {T:.4f}，前半占比 {share_c:.1%} > 基准 {share_0:.1%}")
assert p0_c < p0 and T_c < T, "利率升高的比较静态方向反了"
assert share_c > share_0, "前半窗口占比未上升——前载结论失败"

# D. 绿色悖论：p_b 50→40 → 切换提前 + 固定前 4 期窗口累计开采更高
def window_cum(r, pb, W, S=S0, a=A_DEM):
    """闭式前 W 期（固定窗口）累计开采。"""
    p0_ = solve_p0(r, pb, S, a)
    return a * W - p0_ * ((1.0 + r) ** W - 1.0) / r

W = 4
p0_d, T_d = solve_p0(R0, 40.0), path_closed(solve_p0(R0, 40.0), R0, 40.0)[0]
cum_base, cum_green = window_cum(R0, PB, W), window_cum(R0, 40.0, W)
print(f"[D] p_b=40: p0={p0_d:.4f}，T={T_d:.4f} < 基准 {T:.4f}；前 {W} 期累计 {cum_green:.1f} > 基准 {cum_base:.1f}")
assert T_d < T, "后备价下降未使切换提前"
assert cum_green > cum_base, "固定窗口早期开采未加速——绿色悖论机制失败"

print("\n[ALL ASSERTS PASSED] Hotelling：利率是资源价格的发动机，后备价是天花板；")
print("清洁替代的'好消息'压低未来租→存量持有者今天放量——绿色悖论不是悖论，是无套利的算术。")
