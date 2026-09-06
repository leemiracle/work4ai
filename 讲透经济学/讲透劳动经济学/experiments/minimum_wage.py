#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最低工资：同一政策在两种市场结构下的相反结果（对应 00 章 §3 / 03 章 §2 / 04 章走廊①）。

这是 Card-Krueger 之争（1994-）的极简数学骨架：
  - 竞争市场：最低工资 = 价格下限 → 就业下降、失业出现、无谓损失为正且随工资单调上升；
  - 买方垄断（monopsony）：企业面临向上倾斜的劳动供给，边际用工成本高于工资本身，
    均衡就业本就低于竞争水平 → 适度的最低工资反而把就业往上推，
    恰好等于竞争工资时无谓损失清零。
断言：
  A. 竞争市场：wmin>we 时就业下降、失业>0、DWL>0 且随 wmin 严格递增；
  B. 买方垄断：w_m < w_c（工资被压到竞争水平之下）且 L_m < L_c（就业也低）；
  C. 买方垄断下 wmin ∈ (w_m, w_c] 区间内就业严格高于 L_m，且在 wmin=w_c 时
     恰好补齐全部垄断性无谓损失；
  D. wmin > w_c 后买方垄断市场也开始丢就业——"药效有窗"。
参数：需求 w=25-0.004L（万人，元/时），供给 w=5+0.002L。
"""
import numpy as np

a, b = 25.0, 0.004          # 劳动需求（边际产品价值）截距/斜率
c, d = 5.0, 0.002           # 劳动供给截距/斜率

def demand(w):  return (a - w) / b
def supply(w):  return (w - c) / d

# ---------- 竞争市场 ----------
Lc, wc = (a - c) / (b + d), (a * d + b * c) / (b + d)     # 竞争均衡：精确解
print(f"竞争均衡: L_c = {Lc:.1f} 万人, w_c = {wc:.3f} 元/时")
assert abs(25 - b * Lc - (5 + d * Lc)) < 1e-9

def comp_wmin(wmin):
    Ld = demand(wmin)
    dwl = 0.5 * (wmin - wc) * (Lc - Ld)                   # 三角形无谓损失
    return Ld, supply(wmin) - Ld, dwl                     # 就业、失业、DWL

print("\n== A. 竞争市场：教科书预测 ==")
print("  wmin   就业    失业    DWL")
dwl_prev = 0.0
for wmin in [11.67, 13.0, 15.0, 17.0]:
    Ld, U, DWL = comp_wmin(wmin)
    print(f"  {wmin:5.2f} {Ld:7.1f} {U:7.1f} {DWL:8.1f}")
    if wmin > wc:
        assert Ld < Lc and U > 0 and DWL > 0
        assert DWL > dwl_prev, "竞争下 DWL 随最低工资单调上升"
        dwl_prev = DWL

# ---------- 买方垄断 ----------
Lm = (a - c) / (b + 2 * d)                                 # ME=c+2dL 与需求相交
wm = c + d * Lm
dwl_m = 0.5 * (Lc - Lm) * (wc - wm)
print(f"\n== B. 买方垄断 ==")
print(f"  垄断点: L_m = {Lm:.1f} 万人, w_m = {wm:.3f} 元/时（供给曲线上 L_m 处的工资）")
print(f"  对照:   L_c = {Lc:.1f}, w_c = {wc:.3f} → 垄断买方少雇 {Lc - Lm:.1f} 万人、压价 {wc - wm:.3f} 元")
print(f"  垄断性无谓损失 = {dwl_m:.1f}")
assert wm < wc and Lm < Lc, "买方垄断应同时压低工资与就业"

def monop_wmin(wmin):
    """最低工资下买方垄断者的雇佣量：意愿量与供给量取小（不能强买）。"""
    return min(demand(wmin), supply(wmin))

print("\n== C. 买方垄断：同一政策的相反效果 ==")
print("  wmin   就业    vs L_m")
for wmin in [wm, 10.0, 11.0, wc, 13.0, 15.0]:
    L = monop_wmin(wmin)
    print(f"  {wmin:5.2f} {L:7.1f}   {'↑' if L > Lm + 1e-9 else ('=' if abs(L-Lm)<1e-9 else '↓')}")
    if wm < wmin <= wc:
        assert L > Lm, "wmin∈(w_m, w_c] 应增就业"
assert abs(monop_wmin(wc) - Lc) < 1e-9, "wmin=w_c 时恰好达到竞争就业"
print(f"  wmin = w_c = {wc:.3f} 时就业 {monop_wmin(wc):.1f} = L_c：垄断性 DWL {dwl_m:.1f} 全部清零")

print("\n== D. 药效有窗：wmin 越过 w_c 之后 ==")
assert monop_wmin(13.0) < Lc and monop_wmin(15.0) < monop_wmin(13.0)
print(f"  wmin=13 → {monop_wmin(13.0):.1f}；wmin=15 → {monop_wmin(15.0):.1f}：也开始丢就业")

grid = np.linspace(0, a, 3001)                             # 全谱扫描兜底断言
emp = np.array([monop_wmin(w) for w in grid])
below_wc = emp[grid < wc]
assert below_wc.max() > Lm and abs(emp.max() - Lc) < 1e-9, "就业峰值恰在 w_c、不超过 L_c"
print(f"\n结论：最低工资的就业效应取决于市场结构——竞争市场丢 {Lc - demand(15.0):.0f} 万岗位的同一政策，")
print(f"在买方垄断市场从 {Lm:.0f} 万推到 {Lc:.0f} 万。Card-Krueger 争的不是符号，是哪个模型更像真实劳动市场。")
print("\nALL ASSERTIONS PASSED")
