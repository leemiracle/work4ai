#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
庇古税 × 科斯谈判 × 数量帽：三种环境政策工具的数值等价与失效边界
（对应 00 章✨美之时刻、02 章走廊①、04 章三件套）。

模型（教科书式外部性，全部量纲抽象）：
  - 排放收益 B(e) = 120e − e²   （企业的减排成本即 B 的放弃，边际收益 MB = 120 − 2e）
  - 外部损害 D(e) = 4e²         （边际损害 MD = 8e）
  - 社会福利 W(e) = B(e) − D(e) → 解析最优 e* = 12，W* = 720
  全部用网格搜索求数值解（模拟"实验"而非代数）。

断言：
  A. 庇古税 t* = MD(e*) = 96：企业税后择优 e = 12（|Δ|<0.1），福利恢复到 W*
  B. 科斯零交易成本：无论初始排污权给受害者（基线 e=0）还是给企业（基线 e=60），
     合作谈判（联合剩余最大化）都收敛到 e* = 12——初始分配不影响效率（科斯定理）
  C. 交易成本楔子 k=800 > 最大合作剩余 720：受害者持权 → 谈判破裂、e 停在 0、
     福利损失 720 > 700；企业持权 → 合作剩余 11520 仍成交到 e*=12。
     交易成本 > 0 时初始分配开始重要（科斯定理的边界）
  D. 数量帽 = e* 下许可出清价 = 96（|Δ|<0.1）——价格工具与数量工具数值握手
     （Weitzman 1974：斜率对称时税与帽等价）
"""
import numpy as np

# ---------- 公共网格与函数 ----------
E = np.linspace(0.0, 60.0, 60001)          # 网格步长 0.001
B = 120 * E - E ** 2
D = 4 * E ** 2
W = B - D

i_opt = int(np.argmax(W))
e_star, W_star = E[i_opt], W[i_opt]
print(f"[0] 网格搜索社会最优: e* = {e_star:.3f}, W* = {W_star:.2f}（解析: e*=12, W*=720）")
assert abs(e_star - 12) < 0.1 and abs(W_star - 720) < 1.0

MB_opt = 120 - 2 * e_star                   # 最优处边际收益
MD_opt = 8 * e_star                         # 最优处边际损害
print(f"[0] 最优处 MB = {MB_opt:.2f}, MD = {MD_opt:.2f}（应相等=庇古税）")
assert abs(MB_opt - MD_opt) < 0.5

# ---------- A. 庇古税 ----------
t = MD_opt                                  # 税 = 最优处边际损害 ≈ 96
profit = B - t * E
e_firm = E[int(np.argmax(profit))]
W_tax = B[int(np.argmax(profit))] - D[int(np.argmax(profit))]
print(f"[A] 庇古税 t = {t:.2f}：企业择优 e = {e_firm:.3f}，福利 = {W_tax:.2f}")
assert abs(e_firm - 12) < 0.1, "税后排放未回到最优"
assert abs(W_tax - W_star) < 1.0, "庇古税未恢复最优福利"

# ---------- B. 科斯定理：零交易成本，初始分配无关 ----------
# 受害者持权（基线 e=0）：联合剩余 = B(e)−B(0)−D(e)
S_victim = B - D                            # B(0)=D(0)=0
# 企业持权（基线 e=60）：联合剩余 = [D(60)−D(e)] − [B(60)−B(e)]（受害者买减排）
S_firm = (D[-1] - D) - (B[-1] - B)
e_coase_v = E[int(np.argmax(S_victim))]
e_coase_f = E[int(np.argmax(S_firm))]
print(f"[B] 零交易成本科斯谈判：受害者持权 → e = {e_coase_v:.3f}；"
      f"企业持权 → e = {e_coase_f:.3f}（均应 = e* = 12）")
assert abs(e_coase_v - 12) < 0.1, "受害者持权谈判未达最优"
assert abs(e_coase_f - 12) < 0.1, "企业持权谈判未达最优"

# ---------- C. 交易成本楔子：科斯定理的边界 ----------
k = 800.0                                   # 固定谈判成本
gain_v = float(np.max(S_victim))            # 受害者持权最大合作剩余 ≈ 720
gain_f = float(np.max(S_firm))              # 企业持权最大合作剩余（D(60)−D(12)−[B(60)−B(12)]）
print(f"[C] 谈判成本 k = 800：受害者持权最大合作剩余 = {gain_v:.1f}；"
      f"企业持权 = {gain_f:.1f}")
assert 700 < gain_v < 740, "受害者持权剩余应约 720"
assert gain_v < k < gain_f, "k 应落在两个剩余之间（楔子恰好选择性杀伤）"
# 受害者持权 + k=800 → 破裂：排放停在 0，福利 0，损失 = W* − 0 = 720
W_collapse = 0.0
loss = W_star - W_collapse
print(f"[C] 受害者持权谈判破裂：e 停在 0，福利损失 = {loss:.1f}（>700）")
assert loss > 700, "谈判破裂的福利损失应 > 700"
# 企业持权 + k=800 → 仍成交到 e*（剩余 11520 >> 800）
e_c_f = E[int(np.argmax(S_firm))]           # 成交（剩余远超 k）
print(f"[C] 企业持权：剩余 {gain_f:.0f} >> k → 仍成交到 e = {e_c_f:.3f}；"
      f"但破裂时福利损失将达 {W_star - (B[-1]-D[-1]):.0f}")
assert abs(e_c_f - 12) < 0.1, "企业持权应仍谈判到最优"

# ---------- D. 数量帽：许可出清价 = 庇古税 ----------
cap = e_star                                # 帽 = 12
# 反应函数：价 p 下企业无约束需求 e(p) = argmax(B − p·e)（内点 = (120−p)/2）
prices = np.linspace(0.0, 120.0, 12001)
demand = np.array([E[int(np.argmax(B - p * E))] for p in np.linspace(0, 120, 121)])
# 出清价：需求被帽约束 binding（e(p) ≥ cap 且 cap>0）的最大 p，即 e(p)=cap 处
i_clear = int(np.argmin(np.abs(demand - cap)))
p_clear = np.linspace(0, 120, 121)[i_clear]
print(f"[D] 总量帽 {cap:.2f} 下许可出清价 = {p_clear:.2f}（应 = 庇古税 {t:.2f}）")
assert abs(p_clear - t) < 0.1, "出清价未与庇古税重合"

print("\n[ALL ASSERTS PASSED] 价格=数量在确定性世界数值握手；"
      "科斯定理在交易成本处失效——三条线围出环境政策工具箱的全部设计空间："
      "税价、帽量、产权+谈判，各有其失效边界。")
