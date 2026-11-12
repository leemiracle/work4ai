#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cournot 竞争、HHI 与合并模拟：反垄断执法的计算内核（对应 00 章 §3 / 03 章 §2 / 04 章走廊①）。

线性需求 P = 100 - Q，边际成本 MC = 20，N 家对称 Cournot 章争者：
  均衡 P = (a + N·c)/(N+1)，每家 q = (a-c)/(b(N+1))。
断言：
  A. 模拟价格与古诺闭式解完全一致；
  B. Cowling-Waterson 恒等式：市场勒纳指数 L = (P-c)/P = HHI/ε
     （HHI 取 0-10000 点值、ε 为市场弹性绝对值）——集中度与加价之间不是
     经验相关，是 Cournot 结构下的恒等式；
  C. 无协同合并模拟：5 家 → 4 家（零协同效应）价格上涨、HHI 上升，
     与 2023 美国合并指南的"结构推定"（ΔHHI>100 且合并后 HHI>1800）对照；
  D. 效率抗辩的门槛：合并要抵消涨价，边际成本须下降多少——
     5→4 需 -66.7%，2→1（双寡头合垄断）无解（需要负边际成本）。
"""
import numpy as np

a, b, c = 100.0, 1.0, 20.0

def cournot(N):
    q = (a - c) / (b * (N + 1))          # 每家产量
    Q, P = N * q, (a + N * c) / (N + 1)  # 总量与价格（闭式解）
    return Q, P, q

print("== A. Cournot 均衡：N 家对称厂商 ==")
print("  N     P      Q      每家q    Lerner   HHI")
for N in [1, 2, 3, 4, 5, 10]:
    Q, P, q = cournot(N)
    L = (P - c) / P
    HHI = 10000 / N                       # 对称厂商
    print(f"  {N:2d} {P:6.2f} {Q:6.2f} {q:7.2f}   {L:.3f}   {HHI:6.0f}")
    # 数值校验：N 个一阶条件联立的解（梯度残差）
    Qv = np.full(N, q)
    foc = a - b * Qv.sum() - b * Qv - c   # 每家的 ∂π/∂q 应为 0
    assert np.abs(foc).max() < 1e-9, "Cournot 一阶条件残差应为零"

print("\n== B. Cowling-Waterson 恒等式：L = HHI/ε ==")
for N in [2, 3, 5, 10]:
    Q, P, q = cournot(N)
    L = (P - c) / P
    eps = P / (b * Q)                     # 市场弹性 |ε| = P/(b·Q)
    HHI = 10000 / N
    assert abs(L - (HHI / 10000) / eps) < 1e-12, "恒等式应精确成立"
    print(f"  N={N:2d}: L={L:.4f}  HHI/ε = ({HHI:.0f}/10000)/{eps:.3f} = {(HHI/10000)/eps:.4f}")
print("  → 集中度（HHI）与加价（Lerner）在 Cournot 世界里是同一枚硬币的两面")

print("\n== C. 无协同合并模拟（零协同效应）==")
Q5, P5, _ = cournot(5)
Q4, P4, _ = cournot(4)
dHHI = 10000 / 4 - 10000 / 5
print(f"  5家: P={P5:.2f}, HHI={10000/5:.0f}")
print(f"  4家: P={P4:.2f}, HHI={10000/4:.0f}")
print(f"  涨价 {P4 - P5:+.2f}（{ (P4/P5-1)*100:.1f}%），ΔHHI={dHHI:.0f}")
assert P4 > P5 and dHHI > 100 and 10000 / 4 > 1800
print(f"  → 触发 2023 美国合并指南结构推定（ΔHHI>100 且合并后 HHI>1800），")
print(f"    且涨价幅度可直接算出——合并审查从'结构性猜测'走向'可计算预测'")

print("\n== D. 效率抗辩的算术门槛 ==")
c_merge = 5 * P5 - a - 3 * c              # 合并后 4 家中 1 家成本 c' 使价格回到 P5
print(f"  5→4 合并：要把价格压回 {P5:.2f}，合并厂商边际成本须从 {c:.0f} 降到 {c_merge:.2f}")
assert abs((a + 3 * c + c_merge) / 5 - P5) < 1e-9 and c_merge < c
print(f"  → 须降 {abs(c_merge - c) / c * 100:.0f}%：'合并产生协同'是一句需要 2/3 成本削减才能兑现的辩词")
c_mono = 2 * cournot(2)[1] - a            # 2→1 合并：垄断者成本 c' 使 P 回到双头价
print(f"  2→1 合并：双头价 {cournot(2)[1]:.2f} 要求垄断成本 c'={c_mono:.2f} < 0 —— 无解")
assert c_mono < 0
print("  → 双寡头合并成垄断，不存在任何正的成本削减能抵消涨价（效率抗辩在此数学上破产）")

print("\nALL ASSERTIONS PASSED")
