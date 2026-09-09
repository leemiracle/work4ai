# -*- coding: utf-8 -*-
"""
fields_and_rc.py —— 讲透电磁学家族实验（九要件·Python 层）

对应章：
  00/03 章 走廊A：电偶极子场 —— 叠加原理的可执行版
      两个点电荷的场数组相加（数值） vs 解析式 |E_轴| = 2kp/r^3、|E_中垂| = kp/r^3
  04 章   走廊B：RC 充电 —— 集总抽象的最简时域步进
      dQ/dt = (V - Q/C)/R 欧拉前向 vs 解析 Q(t) = C·V·(1 - e^{-t/τ}), τ = RC

运行：python fields_and_rc.py   （纯 numpy，无外部依赖）
"""
import numpy as np

# ════════════════ 走廊A：电偶极子场 ════════════════
# 单位制：国际单位制；ε₀ 取精确值，q=1nC，d=1cm，观测距离 r 远大于 d
EPS0 = 8.8541878128e-12
k_e = 1.0 / (4.0 * np.pi * EPS0)
q = 1e-9          # 电荷 ±1 nC
d = 1e-2          # 偶极间距 1 cm
p = q * d         # 偶极矩

def point_charge_field(qi, ri, obs):
    """点电荷 qi 在 obs 处（obs 为 Nx3 数组）的场：叠加原理的原生口音（NumPy 广播）"""
    r_vec = obs - ri
    r = np.linalg.norm(r_vec, axis=-1, keepdims=True)
    return k_e * qi * r_vec / r**3

# 观测点：沿轴（z 轴）与中垂面（x 轴），r 取远大于 d 的距离
r_ax = np.linspace(0.1, 1.0, 10)   # 米
ax_pts = np.stack([np.zeros_like(r_ax), np.zeros_like(r_ax), r_ax], axis=1)
mid_pts = np.stack([r_ax, np.zeros_like(r_ax), np.zeros_like(r_ax)], axis=1)

# 数值：两个点电荷叠加（+q 在 z=+d/2，−q 在 z=−d/2）
E_ax_num = point_charge_field(+q, np.array([0, 0, +d/2]), ax_pts) + \
           point_charge_field(-q, np.array([0, 0, -d/2]), ax_pts)
E_mid_num = point_charge_field(+q, np.array([0, 0, +d/2]), mid_pts) + \
            point_charge_field(-q, np.array([0, 0, -d/2]), mid_pts)
ax_num, mid_num = np.linalg.norm(E_ax_num, axis=-1), np.linalg.norm(E_mid_num, axis=-1)

# 解析：|E_轴| = 2kp/r^3，|E_中垂| = kp/r^3（r ≫ d 极限）
ax_ana = 2 * k_e * p / r_ax**3
mid_ana = k_e * p / r_ax**3

# 物理注记：数值=两点电荷的精确叠加；解析式 2kp/r³、kp/r³ 是 r≫d 的**偶极近似**。
# 二者之差 = 被丢掉的四极矩修正 O((d/r)²) —— 断言就验证这个收敛阶（这本身就是教学点）。
rel_err_ax = np.abs(ax_num - ax_ana) / ax_ana
err_ax = np.max(rel_err_ax)
err_mid = np.max(np.abs(mid_num - mid_ana) / mid_ana)
quad_scale = (d / r_ax)**2                       # 四极收敛阶的理论尺子
print(f"[走廊A 偶极子场] 轴向最大相对误差   = {err_ax:.3e}（≈ 四极修正 O((d/r)²)）")
print(f"[走廊A 偶极子场] 中垂线最大相对误差 = {err_mid:.3e}")
print(f"  偶极近似残差/理论尺子 (d/r)² 逐点比 = "
      f"{np.allclose(rel_err_ax / quad_scale, rel_err_ax[0]/quad_scale[0], rtol=0.02)}")
print(f"  （轴向:中垂 = 2:1 —— 偶极子场的指纹；数值确认 = "
      f"{ax_num[-1]/mid_num[-1]:.3f}）")
assert err_ax < 1.2e-2, "四极修正超出 O((d/r)²) 量级"
assert err_mid < 1.2e-2, "中垂线四极修正超量级"
r_ratio = r_ax[-1] / r_ax[0]                     # 观测距离放大 10 倍
assert rel_err_ax[-1] < rel_err_ax[0] / r_ratio**2 * 1.5, \
    "残差未按 (d/r)² 收敛——偶极展开阶数错误"
assert 1.95 < ax_num[-1] / mid_num[-1] < 2.05, "2:1 偶极指纹破坏"

# ════════════════ 走廊B：RC 充电 ════════════════
# dQ/dt = (V - Q/C)/R,  Q(0)=0  →  Q(t) = C·V·(1 - e^{-t/τ}), τ = RC
V, R, C = 5.0, 1e3, 100e-6        # 5V, 1kΩ, 100µF → τ = 0.1 s
tau = R * C
dt, T = 1e-4, 0.5                 # 步长远小于 τ
n = int(T / dt)
Q = np.zeros(n)
for i in range(1, n):             # 显式欧拉：一阶时域步进（FDTD 的集总表亲）
    Q[i] = Q[i-1] + dt * (V - Q[i-1]/C) / R
t = np.arange(n) * dt
Q_ana = C * V * (1 - np.exp(-t/tau))

# 断言1：t = τ 时充电到 63.2%（一阶系统的时间常数指纹）
Q_at_tau = Q[int(round(tau/dt))]
frac = Q_at_tau / (C*V)
print(f"\n[走廊B RC 充电] t=τ 时 Q/CV = {frac:.4f}（理论 0.6321）")
assert 0.630 < frac < 0.635, "时间常数 63.2% 指纹失败"

# 断言2：欧拉全局误差 = O(dt)（终值相对偏差 < 1%）
err_rc = abs(Q[-1] - Q_ana[-1]) / Q_ana[-1]
print(f"[走廊B RC 充电] t=0.5s (=5τ) 终值相对误差 = {err_rc:.3e}（欧拉 O(dt)）")
assert err_rc < 1e-2, "欧拉一阶精度失败"

# 断言3：5τ 后基本充满（工程判据 99.3%）
assert Q[-1] / (C*V) > 0.993, "5τ ≈ 99.3% 判据失败"
print(f"[走廊B RC 充电] t=5τ 时已充至 {Q[-1]/(C*V)*100:.2f}% —— '5τ 即充满'工程口诀验证")

print("\n全部断言通过 ✅  （叠加走廊 ↔ 解析走廊 互相交叉验证=免费单元测试）")
