#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冯·杜能竞租模型（bid-rent）最小复现（对应 00 章✨美之时刻 与 04 章代码走廊①）。

模型（1826《孤立国》的现代版）：
  市场位于 x=0；三种土地利用 i，每亩净产出 N_i（扣除非运输成本）、每公里运费 T_i；
  竞租函数 R_i(x) = N_i − T_i·x —— 这块地"愿付的地租"=把货运到市场后剩下的钱；
  均衡 = 竞租曲线族的上包络：每块地归出价最高者，运费越贵的用途越贴近市场。

断言：
  A. 恰好 3 个同心圈层，顺序 = 运费强度降序（蔬菜→谷物→林牧）
  B. 数值边界 x1≈133.3（蔬菜|谷物）、x2=200（谷物|林牧）、外缘=600，误差 < 0.5 km
  C. 上包络（市场地租）在圈层边界连续，且全程单调不升
  D. 反事实"修路"（全部运费减半）：外缘 600→1200，城市影响圈翻倍
"""
import numpy as np

USES = [("蔬菜", 2000.0, 10.0), ("谷物", 1200.0, 4.0), ("林牧", 600.0, 1.0)]

def solve(scale=1.0, x_max=1300.0, step=0.1):
    """竞租上包络与圈层划分。scale：运费系数（1=土路基准，0.5=修路后）。"""
    x = np.arange(0.0, x_max + step, step)
    R = np.vstack([N - T * scale * x for _, N, T in USES])   # 竞租曲线族
    top, who = R.max(axis=0), R.argmax(axis=0)               # 上包络=市场地租
    cuts = np.flatnonzero(np.diff(who)) + 1                  # 用途切换的网格点
    bounds = [x[c] for c in cuts]                            # 圈层边界
    names = [USES[who[i]][0] for i in np.r_[0, cuts]]        # 各圈层用途
    inner = top > 0                                          # 地租为正=有人耕
    edge = x[inner][-1]                                      # 农业外缘
    return x, R, top, bounds, names, edge

# ---- A. 圈层数与顺序 ----
x, R, top, bounds, names, edge = solve()
print(f"[A] 圈层：{' → '.join(names)}（共 {len(names)} 层）")
assert len(names) == 3, "应恰有 3 个圈层"
assert names == ["蔬菜", "谷物", "林牧"], "运费最贵的用途应最靠近市场"

# ---- B. 边界位置（解析解：x1=800/6≈133.3，x2=600/3=200，外缘=600/1）----
x1, x2 = bounds
print(f"[B] 边界：蔬菜|谷物 x1={x1:.1f}（解析 133.3）  谷物|林牧 x2={x2:.1f}（解析 200.0）  "
      f"外缘={edge:.1f}（解析 600.0）")
assert abs(x1 - 800 / 6) < 0.5, "x1 偏离解析边界"
assert abs(x2 - 200.0) < 0.5, "x2 偏离解析边界"
assert abs(edge - 600.0) < 0.5, "农业外缘偏离解析值"

# ---- C. 边界连续 + 全程单调不升 ----
i1 = np.searchsorted(x, x1)
i2 = np.searchsorted(x, x2)
gap1 = abs(R[0, i1] - R[1, i1])
gap2 = abs(R[1, i2] - R[2, i2])
print(f"[C] 边界地租跳变：x1 处 {gap1:.2f} 元、x2 处 {gap2:.2f} 元（连续→≈0）；"
      f"包络最大升幅 {np.diff(top).max():.2e}（≤0 即单调）")
assert gap1 < 1.0 and gap2 < 1.0, "竞租曲线在交点处应相等（地租连续）"
assert np.all(np.diff(top) <= 1e-9), "市场地租应随距离单调不升"

# ---- D. 反事实：修路（运费减半）→ 外缘翻倍 ----
_, _, top2, bounds2, names2, edge2 = solve(scale=0.5)
print(f"[D] 修路（T→T/2）：外缘 {edge:.0f} → {edge2:.0f} km（倍率 {edge2 / edge:.2f}）；"
      f"边界 x1 {x1:.0f}→{bounds2[0]:.0f}、x2 {x2:.0f}→{bounds2[1]:.0f}")
assert names2 == names, "圈层顺序不应改变，只应外推"
assert 1.9 < edge2 / edge < 2.1, "运费减半，外缘应翻倍"

print("\n[ALL ASSERTS PASSED] 圈层不是农业知识，是『运完货剩下的钱付地租』这条公理的必然——")
print("两百年前的庄园账本，至今仍是每个大都市近郊农业带的图纸；修路不改圈层顺序，只把影响圈翻倍。")
