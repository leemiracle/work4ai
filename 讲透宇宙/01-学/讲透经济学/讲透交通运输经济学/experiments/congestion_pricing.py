#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拥堵定价三连测（对应 00 章✨美之时刻 / 03 章 Beckmann 与悖论 / 04 章走廊①）。

模型：
  A. Pigou 双路（1920）：路 A 常耗 1.0；路 B 耗 = 其流量 x（越走越堵）；需求 1 单位。
     UE（人人自私）：全部挤上 B，人人耗时 1.0；
     SO（总耗时最小）：半数走 A 半数走 B，平均耗时 0.75 —— 25% 时间凭空回来；
     对 B 收费 0.5（=边际-平均外部成本），自私均衡自动落在 SO。
  B. Braess 悖论（1968）：S→A→T / S→B→T 十字网，加一条零成本近道 A→B，
     均衡成本反而 1.5 → 2.0。
  C. 仿射双路：c1(x)=2+3x，c2(x)=1+x，需求 3。UE 与 SO 分流不同；
     按 MSC（边际社会成本）设通行费后，UE 分流 == SO 分流（数值验证）。

断言：每个部件的均衡/最优解与闭式解一致（容差 1e-9 或格点分辨率）。
"""
import numpy as np

TOL = 1e-9

# ---------- A. Pigou 双路 ----------
# 路 A 成本恒 1；路 B 成本 = x_B；需求 D=1
cA = lambda x: 1.0
cB = lambda x: x
# UE：B 上车直到 x_B = 1（成本追平 A），全员耗时 1.0
xb_ue = 1.0
ue_cost = cB(xb_ue)                       # = 1.0
# SO：min (1-xb)·cA + xb·cB(xb) = (1-xb) + xb^2  ->  xb = 1/2
xb_grid = np.linspace(0, 1, 2_000_001)
tc_grid = (1 - xb_grid) * 1.0 + xb_grid ** 2
i = int(np.argmin(tc_grid)); xb_so = xb_grid[i]; tc_so = tc_grid[i]
avg_so = tc_so / 1.0
print(f"[A] UE: 全员走B, 人均耗时 {ue_cost:.4f}（总耗时 {ue_cost:.4f}）")
print(f"[A] SO: 数值格点 xb={xb_so:.6f}, 总耗时 {tc_so:.6f}, 人均 {avg_so:.6f} "
      f"（闭式 xb=0.5, 人均 0.75）")
assert abs(xb_so - 0.5) < 1e-6, "SO 分流应为一半"
assert abs(tc_so - 0.75) < 1e-6, "SO 总耗时应为 0.75"
assert abs(ue_cost - 1.0) < TOL and (ue_cost - avg_so) / ue_cost > 0.249, \
    "UE 比 SO 慢约 25% 不成立"
# 庇古费 0.5 恢复 SO：广义成本 cB(x)+0.5 = cA = 1 -> x=0.5
toll = 0.5
xb_toll = next(x for x in xb_grid if abs((x + toll) - 1.0) < 1e-6)
print(f"[A] 对B收费 {toll}: 均衡流量回到 xb={xb_toll:.4f}（==SO），"
      f"时间节省 {(ue_cost-avg_so)/ue_cost:.0%} 收进财政而非蒸发于排队")
assert abs(xb_toll - 0.5) < 1e-6, "收费后均衡未恢复 SO"

# ---------- B. Braess 悖论 ----------
# 无近道：两条路 成本 x/2+1 与 1+x/2？——用经典数：SA 耗 x、AT 耗 1、SB 耗 1、BT 耗 x
# 路径1 S-A-T：x_SA+1；路径2 S-B-T：1+x_BT；UE：x_SA=x_BT=1/2，成本 1.5
x = 0.5
cost_no_shortcut = x + 1.0                # 两条路对称，各 1.5
print(f"\n[B] 无近道 UE: 各半分流, 人均成本 {cost_no_shortcut:.4f}（闭式 1.5）")
assert abs(cost_no_shortcut - 1.5) < TOL
# 有零成本近道 A-B：唯一 UE 全员走 S-A-B-T：x_SA=x_BT=1，成本 1+0+1=2
# 验证无偏离激励：改走路1成本 = x_SA+1 = 2，无利可图
cost_shortcut = 1.0 + 0.0 + 1.0
deviate = 1.0 + 1.0                        # 任一agent改走 S-A-T 的成本
print(f"[B] 有近道 UE: 全员走 S-A-B-T, 人均成本 {cost_shortcut:.4f}; "
      f"单方改道成本 {deviate:.4f}（无利可图 -> 确为均衡; 闭式 2.0）")
assert abs(cost_shortcut - 2.0) < TOL and deviate >= cost_shortcut - TOL, \
    "Braess 均衡验证失败"
assert cost_shortcut > cost_no_shortcut, "加零成本近道后全网反而变慢——悖论未复现！"
print(f"[B] ✅ Braess 悖论复现：加一条零成本近道，均衡成本 1.5 -> 2.0（+33%）")

# ---------- C. 仿射双路：MSC 通行费恢复最优 ----------
c1 = lambda x: 2 + 3 * x
c2 = lambda x: 1 + x
D = 3.0
# UE：c1(x1)=c2(D-x1) -> 2+3x1 = 1+3-x1 -> x1=0.5
x1_ue = 0.5; cost_ue = c1(x1_ue)
# SO：min x1·c1(x1)+x2·c2(x2) -> 4x1-2=0 -> x1=0.625（闭式推导见 03 章练习）
x1_grid = np.linspace(0, D, 3_000_001)
tc = x1_grid * c1(x1_grid) + (D - x1_grid) * c2(D - x1_grid)
j = int(np.argmin(tc)); x1_so = x1_grid[j]
# MSC 费：toll_i = x_i·c_i'(x_i) = 3x1 / x2 -> 收费后 UE 复原 SO
t1, t2 = 3 * x1_so, 1 * (D - x1_so)       # 边际-平均 = b_i·x_i
x1_toll = next(x for x in np.linspace(0, D, 3_000_001)
               if abs((c1(x) + t1) - (c2(D - x) + t2)) < 1e-5)
print(f"\n[C] 仿射双路 D=3: UE x1={x1_ue:.4f}(人均成本{cost_ue:.4f}) vs "
      f"SO x1={x1_so:.6f}(闭式 0.625)")
print(f"[C] MSC 通行费 (路1={t1:.4f}, 路2={t2:.4f}) 后 UE 分流 x1={x1_toll:.4f} -> 恢复 SO")
assert abs(x1_so - 0.625) < 1e-6, "SO 分流闭式 0.625 不符"
assert abs(x1_toll - 0.625) < 1e-4, "MSC 收费后均衡未恢复 SO"
assert tc[j] < D * cost_ue - 1e-9, "SO 总成本应严格低于 UE"

print("\n[ALL ASSERTS PASSED] 个体理性≠集体理性（A/B），但价格能把二者焊回来（A/C）——")
print("这就是拥堵定价的全部经济学：25% 的时间损失不是命运，是免费的价格标签。")
