#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑斯蒂资源×捕捞的最小生态经济实验。
对应章：00 章 §四/§六（MSY 与核心问题）、03 章构造①②、04 章走廊 A 与 §六美之时刻。

模型：
  生物量动态  dX/dt = r·X·(1 − X/K) − H
  r=0.4、K=10000 → 最大可持续产量 MSY = rK/4 = 1000，出现在 X=K/2=5000
  欧拉积分 dt=0.05；X 到 0 即判灭绝（生态经济学最便宜的"灭绝模型"）

断言：
  A. H=0.8·MSY=800（"保守捕捞"）：X0=9000 收敛到稳定平衡 7236（rX(1−X/K)=800 的大根）；
     但 X0=2500（低于不稳定平衡 2764）照样灭绝——同一政策、两种命运（盆地分离）
  B. H=1.2·MSY=1200 > rK/4：任何初值灭绝——MSY 是硬顶，不是"平均参考值"
  C. 持续产量–捕捞强度扫描：数值峰值 = 1000 ± 5（回到 rK/4）
  D. 开放进入（Gordon 1954 / Schaefer 模型 H=qEX；p=2、q=4e-4、c=3，Ė=ν·π）：
     收敛到生物经济平衡 X∞=c/(pq)=3750，利润≈0（租金耗散），持续产量 937.5 < MSY
     ——经济过度捕捞先于生物过度捕捞发生

真实锚：1992 加拿大北方鳕鱼禁渔（种群在"看起来还很稳"时已越过不稳定平衡，至今未恢复）；
2022 WTO 渔业补贴协定（第一次全球性纠正开放进入的努力）。
"""
import numpy as np

r, K = 0.4, 10_000.0
MSY = r * K / 4.0
dt = 0.05


def simulate_const_H(H: float, X0: float, T: float) -> float:
    """常数捕捞 H 下的欧拉积分；灭绝即返回 0。"""
    X = X0
    for _ in range(int(T / dt)):
        X += (r * X * (1.0 - X / K) - H) * dt
        if X <= 0.0:
            return 0.0
    return X


# ---- A. 同一政策、两种命运：盆地分离 ---------------------------------------
H_A = 0.8 * MSY                                        # 800
disc = np.sqrt(K * K - 4.0 * K * H_A / r)
X_star, X_unst = (K + disc) / 2.0, (K - disc) / 2.0    # 稳定平衡（大根）/不稳定平衡（小根）
X_hi = simulate_const_H(H_A, 9000.0, T=150.0)
X_lo = simulate_const_H(H_A, 2500.0, T=150.0)
print(f"[A] H={H_A:.0f}：稳定平衡 {X_star:.0f} / 不稳定平衡 {X_unst:.0f}")
print(f"    X0=9000 → X(150)={X_hi:.0f}（收敛）；X0=2500 → X(150)={X_lo:.0f}（灭绝）")
assert abs(X_star - 7236) < 1 and abs(X_unst - 2764) < 1, "平衡解析值核对"
assert abs(X_hi - 7236) < 30, "X0=9000 应收敛到 7236"
assert X_lo == 0.0, "X0=2500（低于不稳定平衡）应灭绝"

# ---- B. MSY 是硬顶 ----------------------------------------------------------
X_B = simulate_const_H(1.2 * MSY, 9000.0, T=200.0)
print(f"[B] H={1.2 * MSY:.0f} > rK/4={MSY:.0f}：X(200)={X_B:.1f}（任何初值灭绝）")
assert X_B == 0.0, "超过 MSY 的常数捕捞必然灭绝"

# ---- C. 持续产量–捕捞强度扫描 ----------------------------------------------
Hs = np.arange(600.0, 1225.0, 25.0)
yields = np.array([h if simulate_const_H(h, K, T=400.0) > 100.0 else 0.0 for h in Hs])
h_peak = yields.max()
print(f"[C] 扫描 {Hs[0]:.0f}–{Hs[-1]:.0f}：持续产量峰值 = {h_peak:.0f} @ "
      f"H={Hs[int(yields.argmax())]:.0f}（理论 MSY = rK/4 = {MSY:.0f}）")
assert abs(h_peak - MSY) <= 5.0, "扫描峰值应回到 rK/4"

# ---- D. 开放进入：租金耗散（Gordon 1954）------------------------------------
p, q_, c, nu = 2.0, 4e-4, 3.0, 0.02
X, E = 9000.0, 200.0
for _ in range(int(300.0 / dt)):
    X += (r * X * (1.0 - X / K) - q_ * E * X) * dt
    profit = p * q_ * E * X - c * E                   # 全船队利润
    E = max(E + nu * profit * dt, 0.0)                # 有利润 → 新船进入
    if X <= 0.0:
        X = 0.0
        break
H_D, rev_D = q_ * E * X, p * q_ * E * X
print(f"[D] 开放进入终态：X={X:.0f}（生物经济平衡 c/(pq)={c / (p * q_):.0f}），E={E:.0f}，"
      f"产量={H_D:.1f}（< MSY={MSY:.0f}），利润/收入={profit / rev_D:+.4%}")
assert abs(X - 3750) < 60, "应收敛到生物经济平衡 3750"
assert abs(H_D - 937.5) < 15, "开放进入产量 937.5 < MSY"
assert abs(profit) < 0.01 * rev_D, "租金被竞争耗散（利润≈0）"

print("\n[ALL ASSERTS PASSED] 三行结论：①MSY=rK/4 是硬顶不是参考值；"
      "②同一捕捞政策存在两种命运——越过不稳定平衡即不可逆；"
      "③开放进入下，经济浪费（租金耗散 + 产量<MSY）先于生物崩溃发生。")
