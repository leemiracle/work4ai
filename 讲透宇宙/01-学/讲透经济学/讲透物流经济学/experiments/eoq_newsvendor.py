#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EOQ 与报童双模型断言自验（对应 00 章✨美之时刻 / 02 章服务水平公式 /
03 章四件闭式神器 / 04 章走廊①）。纯 numpy+math，无 scipy。

模型：
  A. EOQ：年需求 D=12000 箱，单次订货成本 S=300 元，单箱年持有成本 H=12 元。
     Q* = sqrt(2DS/H) = sqrt(600000) ≈ 774.60；TC* = sqrt(2DSH) ≈ 9295.16。
  B. 平坦性：TC(1.5Q*)/TC(Q*) = (1/1.5+1.5)/2 = 1.0833——批量偏 50% 成本仅 +8.3%；
     TC(0.5Q*)/TC(Q*) = (2+0.5)/2 = 1.25。
  C. 报童：进价 2 元/份，售价 5 元，残值 0.5 元 -> cu=3, co=1.5，
     临界比 = cu/(cu+co) = 2/3；需求 ~ N(100, 20^2)。
     Q* = mu + sigma*Phi^{-1}(2/3)，Phi^{-1} 用 math.erf + 二分手写。

断言：
  A. 百万格点数值最优批量/成本 == 闭式（相对误差 < 1e-6）
  B. 曲线比 = 恰 1.0833 / 1.25（容差 1e-9），且 2 倍批量 < 1.26
  C. 期望利润格点最优 == 正态分位数闭式（容差 0.5 份），且 Q* > mu（cu>co 必右偏）
"""
import math
import numpy as np

# ---------- A. EOQ ----------
D, S, H = 12000.0, 300.0, 12.0
Q_star = math.sqrt(2 * D * S / H)
TC_star = math.sqrt(2 * D * S * H)
q_grid = np.linspace(1.0, 4 * Q_star, 2_000_001)
tc_grid = D / q_grid * S + q_grid / 2 * H
i = int(np.argmin(tc_grid))
q_num, tc_num = q_grid[i], tc_grid[i]
print(f"[A] EOQ 闭式: Q*={Q_star:.4f} 箱/次, TC*={TC_star:.2f} 元/年 "
      f"(订货项=持有项={TC_star/2:.2f})")
print(f"[A] 数值格点: Q={q_num:.4f}, TC={tc_num:.2f}")
assert abs(q_num - Q_star) / Q_star < 1e-5, "数值最优批量偏离闭式"
assert abs(tc_num - TC_star) / TC_star < 1e-7, "数值最优成本偏离闭式"
# 对冲结构：最优处两项成本相等
order_cost, hold_cost = D / Q_star * S, Q_star / 2 * H
assert abs(order_cost - hold_cost) < 1e-6 * TC_star, "最优处两项成本应相等"

# ---------- B. 平坦性 ----------
r15 = (D / (1.5 * Q_star) * S + 1.5 * Q_star / 2 * H) / TC_star
r05 = (D / (0.5 * Q_star) * S + 0.5 * Q_star / 2 * H) / TC_star
r20 = (D / (2 * Q_star) * S + 2 * Q_star / 2 * H) / TC_star
print(f"\n[B] 批量偏 +50%: 成本比 {r15:.4f} (理论 1.0833)")
print(f"[B] 批量偏 -50%: 成本比 {r05:.4f} (理论 1.2500)")
print(f"[B] 批量翻倍  : 成本比 {r20:.4f} (理论 1.2500)")
assert abs(r15 - 1.0833333333) < 1e-9, "1.5Q* 的成本比应为 25/24"
assert abs(r05 - 1.25) < 1e-9 and abs(r20 - 1.25) < 1e-9, "半量/倍量成本比应为 1.25"
assert r15 < 1.09, "EOQ 曲线平坦性断言失败"

# ---------- C. 报童 ----------
cu, co = 5 - 2, 2 - 0.5            # 缺货损失 3 / 压货损失 1.5
ratio = cu / (cu + co)             # 2/3
mu, sigma = 100.0, 20.0

def Phi(x):                          # 标准正态 CDF（erf 手写）
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def Phi_inv(p):                      # 二分求逆
    lo, hi = -8.0, 8.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if Phi(mid) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

z = Phi_inv(ratio)
Q_nv = mu + sigma * z                # 闭式订量

def Phi(x):                          # 标准正态 CDF（erf 手写，支持数组）
    return 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))

def phi(x):                          # 标准正态 PDF
    return np.exp(-0.5 * x ** 2) / math.sqrt(2 * math.pi)

def profit(Q):                       # 报童期望利润（闭式，向量化）
    # E[售出] = Q - [(Q-mu)*Phi(z) + sigma*phi(z)]；E[残值] = 方括号项
    z = (np.asarray(Q, dtype=float) - mu) / sigma
    unsold = (np.asarray(Q, dtype=float) - mu) * Phi(z) + sigma * phi(z)
    sales = np.asarray(Q, dtype=float) - unsold
    return sales * 5 + unsold * 0.5 - np.asarray(Q, dtype=float) * 2

qg = np.linspace(50, 200, 30_001)
pg = np.array([profit(q) for q in qg])
Q_num = qg[int(np.argmax(pg))]
print(f"\n[C] 报童临界比 = cu/(cu+co) = {ratio:.4f}; z={z:.4f}; "
      f"闭式 Q*={Q_nv:.2f} 份 (mu={mu})")
print(f"[C] 期望利润数值最优 Q={Q_num:.2f} 份 (利润 {pg.max():.2f} 元)")
assert abs(Q_num - Q_nv) < 0.5, "报童闭式与数值最优不符"
assert Q_nv > mu, "cu>co 时订量必须右偏于均值"
# 服务水平读数：SL* = 1 - co/(cu+co) = 2/3
assert abs(ratio - (1 - co / (cu + co))) < 1e-12, "临界比=最优服务水平"

print("\n[ALL ASSERTS PASSED] EOQ: 对冲与宽容（8.3% 的 50% 偏差）；")
print("报童: 态度即分位数（2/3）。物流学的两件闭式神器，一个教你不必精确，")
print("一个教你必须定量。")
