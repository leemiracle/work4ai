#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hartwick 法则最小模拟（对应 00 章✨美之时刻 与 04 章代码走廊①）。

问题：挖矿卖资源的钱（资源租金）如果全花掉，后代靠什么活？
Hartwick (1977)：沿有效开采路径，把可耗竭资源的租金全部投资人造资本，
消费可以永久不降——弱可持续性（自然资本可被人造资本替代）的可执行规则。

模型（Dasgupta–Heal–Solow 的 Cobb-Douglas，劳动归一）：
  Y_t = K_t^0.3 · R_t^0.2     产出 = 人造资本 × 资源投入
  租金 = ∂Y/∂R · R = 0.2·Y    Cobb-Douglas 的便利：要素收入份额=产出弹性

关键设定——有效开采路径是双曲递减而非指数递减：
  恒定消费路径要求 K(t) = K_0 + β·Y*·t（线性）、R(t) = Y*^(1/β)·K(t)^(-α/β)，
  其中 Y* 由存量约束 ∫R dt = S_0 解出：Y* = [S_0(α-β)·K_0^(1-α/β)]^(β/(1-β))。
  这正是 DHS 最优开采的双曲形态。若换成任意的指数递减路径，租金投资只能
  放缓而无法消除消费下滑——Hartwick 等价定理要求路径本身有效
  （Withagen & Asheim 1998「逆 Hartwick 定理」，脚本尾部有现场演示）。

三情景（同一有效开采路径，只差储蓄行为）：
  H    Hartwick：I=0.2·Y（租金全投）→ C=0.8·Y
  half 半吊子  ：I=0.1·Y（投一半）→ C=0.9·Y
  N    吃老本  ：I=0    （租金全花）→ C=Y，K 恒定

断言：
  A. 情景 H：全程 C_t/C_0 ∈ [0.98, 1.02]——「租金换机器」保住消费
  B. 情景 N：C_T/C_0 = (R_T/R_0)^0.2 ≈ 0.677（K 恒定时 C∝R^β；带 [0.65,0.70]）
  C. 情景 half：末期消费比严格介于 N 与 H 之间
  D. 对照演示：同一租金规则搬到指数递减开采（g=2%/年）上，消费仍下滑 ≥10%
     ——规则失效的原因不是储蓄不够，而是路径无效率
"""
import numpy as np

alpha, beta = 0.3, 0.2           # K 与 R 的产出弹性（=收入份额）
K0, S0 = 10.0, 100.0             # 初始人造资本、资源存量
T, dt = 100.0, 0.05              # 视野 [年]、欧拉子步长
n = int(round(T / dt))

# 恒定消费水平 Y*：由 ∫R dt = S_0 解出（双曲开采的归一化常数）
Ystar = (S0 * (alpha - beta) * K0 ** (1 - alpha / beta)) ** (beta / (1 - beta))
K_of = lambda t: K0 + beta * Ystar * t                    # 恒定消费路径上的 K(t)
R_of = lambda t: Ystar ** (1 / beta) * K_of(t) ** (-alpha / beta)  # 有效开采路径

print(f"参数: α={alpha}, β={beta}, K_0={K0}, S_0={S0}, T={T} 年, dt={dt}")
print(f"恒定消费解: Y*={Ystar:.4f}, C*=0.8Y*={0.8*Ystar:.4f}, "
      f"R_0={R_of(0):.4f}, R_T/R_0={R_of(T)/R_of(0):.4f}")


def simulate(R_path, inv_share):
    """给定开采路径与投资份额（占 Y 比例），跑 100 年返回逐年消费数组。"""
    K = K0
    C = np.empty(n)
    for i in range(n):
        R = R_path(i * dt)
        Y = K ** alpha * R ** beta
        C[i] = Y - inv_share * Y
        K += inv_share * Y * dt
    return C


C_H, C_half, C_N = simulate(R_of, beta), simulate(R_of, beta / 2), simulate(R_of, 0.0)
r_H, r_half, r_N = C_H / C_H[0], C_half / C_half[0], C_N / C_N[0]
used = 1 - (K0 / K_of(T)) ** (1 - alpha / beta)           # 到 T 已开采存量比例（解析）

print(f"\n[A] Hartwick (I=0.2Y): C_0={C_H[0]:.4f}, 全程 C_t/C_0 ∈ [{r_H.min():.4f}, {r_H.max():.4f}]"
      f"（100 年已开采存量 {used:.0%}）")
assert 0.98 <= r_H.min() and r_H.max() <= 1.02, "Hartwick 情景消费越出 ±2% 带——规则或初始化有 bug"

exact_N = (R_of(T) / R_of(0)) ** beta                     # K 恒定时 C ∝ R^β
print(f"[B] 吃老本 (I=0):  C_T/C_0 = {r_N[-1]:.4f}（解析值 (R_T/R_0)^β={exact_N:.4f}）")
assert abs(r_N[-1] - exact_N) < 1e-9, "吃老本情景应与解析值逐位一致"
assert 0.65 <= r_N[-1] <= 0.70, "吃老本情景末期消费比偏离预期带"

print(f"[C] 半吊子 (I=0.1Y): C_T/C_0 = {r_half[-1]:.4f}（应严格介于 N 与 H 之间）")
assert r_N[-1] < r_half[-1] < r_H[-1], "单调性破坏——投资越多末期消费应越高"

print("[D] 三情景全程 min/末期 消费比对比：")
for tag, r in [("Hartwick I=0.2Y", r_H), ("半吊子  I=0.1Y", r_half), ("吃老本  I=0  ", r_N)]:
    print(f"    {tag}: min={r.min():.4f}, 末期={r[-1]:.4f}")
assert r_H.min() > r_half.min() > r_N.min(), "消费路径单调性不符"

# 对照：同样的租金投资规则，搬到无效率的指数递减开采路径上
C_exp = simulate(lambda t: R_of(0) * np.exp(-0.02 * t), beta)
r_exp = C_exp / C_exp[0]
print(f"\n[D+] 对照（指数递减开采 g=2%/年 + 同样租金全投）: "
      f"C_T/C_0 = {r_exp[-1]:.4f}——储蓄规则没变，消费仍下滑 {1 - r_exp[-1]:.0%}")
assert r_exp[-1] < r_exp[0] - 0.10, "对照情景应出现 >10% 的消费下滑（路径无效率的代价）"

print("\n[ALL ASSERTS PASSED] 有效路径上把租金全部换成机器，消费一百年纹丝不动；")
print("全部花掉，末期消费只剩 68%。弱可持续性不是口号，是一条储蓄规则——")
print("但它只救『会安排开采的人』（D），救不了『乱挖的人』（D+），这正是 Hartwick")
print("等价定理的边界：可持续=储蓄规则×开采效率，缺一不可。")
