#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双重加价与两部制费（对应 00 章✨美之时刻 / 03 章结构一 / 04 章走廊①）。

模型：线性需求 P = 100 - Q，上游制造商边际成本 c = 20。
  ① 一体化（或两部制费）：零售价 60、销量 40、总利润 1600、CS 800、W 2400
  ② 双重加价（上下游均垄断、线性批发价）：w=60 → 零售价 80、销量 20、
     利润 800+400=1200、CS 200、W 1400 —— 价更高、利更薄、两家更穷
  ③ 两部制费（w=20 + 固定费 1600）：恢复一体化每一个数字

断言：三组闭式全部数值验证（格点搜索独立复核垄断解）。
"""
import numpy as np

a, c = 100.0, 20.0          # 需求截距 / 上游边际成本
Q = lambda p: a - p          # 需求
pi = lambda p, cost: (p - cost) * Q(p)   # 售价 p、边际成本 cost 的利润

# ---------- ① 一体化 ----------
p_int = (a + c) / 2                       # 60
Q_int, pi_int = Q(p_int), pi(p_int, c)
CS_int = 0.5 * (a - p_int) * Q_int        # 消费者剩余（三角）
print(f"[1] 一体化: p={p_int:.0f}, Q={Q_int:.0f}, Pi={pi_int:.0f}, "
      f"CS={CS_int:.0f}, W={pi_int+CS_int:.0f}")
# 数值复核：格点搜利润峰
pg = np.linspace(c, a, 800_001)
p_num = pg[int(np.argmax(pi(pg, c)))]
assert abs(p_num - p_int) < 1e-4, "一体化垄断价格格点复核失败"
assert abs(pi_int - 1600.0) < 1e-9

# ---------- ② 双重加价 ----------
# 下游面对边际成本 w：p_d(w) = (a+w)/2, Q_d(w) = (a-w)/2
p_dm = lambda w: (a + w) / 2
# 上游预见下游反应，max (w - c) * Q_d(w) -> w* = (a+c)/2 = 60
w_star = (a + c) / 2
p_star = p_dm(w_star); Q_dm = Q(p_star)
pi_up = (w_star - c) * Q_dm               # 40 * 20 = 800
pi_dn = (p_star - w_star) * Q_dm          # 20 * 20 = 400
CS_dm = 0.5 * (a - p_star) * Q_dm         # 200
print(f"[2] 双重加价: w={w_star:.0f} -> p={p_star:.0f}, Q={Q_dm:.0f}, "
      f"上游利润={pi_up:.0f}, 下游利润={pi_dn:.0f}, 合计={pi_up+pi_dn:.0f}, "
      f"CS={CS_dm:.0f}, W={pi_up+pi_dn+CS_dm:.0f}")
# 上游最优 w 的数值复核（Stackelberg 格点）
wg = np.linspace(c, a - 1, 800_001)
w_num = wg[int(np.argmax((wg - c) * (a - p_dm(wg))))]
assert abs(w_num - w_star) < 1e-4, "Stackelberg 批发价格点复核失败"
assert p_star > p_int, "双重加价零售价应更高"
assert pi_up + pi_dn < pi_int - 1e-9, "两垄断合计利润应低于一体化"
assert CS_dm < CS_int, "双重加价消费者更惨"
assert pi_up + pi_dn + CS_dm < pi_int + CS_int - 1e-9, "总福利应下降（双重死重损失）"

# ---------- ③ 两部制费：w=c + 固定费 ----------
w_2p = c                                  # 20
F = pi_int                                # 固定费=一体化利润 1600
p_2p = p_dm(w_2p); Q_2p = Q(p_2p)         # 下游零售价 60、量 40
pi_dn_2p = (p_2p - w_2p) * Q_2p - F       # 1600 - 1600 = 0（上游抽走全部）
print(f"[3] 两部制费: w={w_2p:.0f}+F={F:.0f} -> p={p_2p:.0f}, Q={Q_2p:.0f}, "
      f"上游利润={F:.0f}, 下游利润={pi_dn_2p:.0f}, CS={0.5*(a-p_2p)*Q_2p:.0f}, "
      f"W={F+pi_dn_2p+0.5*(a-p_2p)*Q_2p:.0f}")
assert abs(p_2p - p_int) < 1e-9 and abs(Q_2p - Q_int) < 1e-9, \
    "两部制费应恢复一体化价格与销量"
assert abs(F + pi_dn_2p - pi_int) < 1e-9, "利润总量应恢复 1600"
assert abs(0.5 * (a - p_2p) * Q_2p - CS_int) < 1e-9, "消费者剩余应恢复"

print("\n[ALL ASSERTS PASSED] 垄断+垄断 = 价更高(80>60)、利更薄(1200<1600)、"
      "全社会更穷(W 2400->1400)。")
print("一张发票治好：批发价=成本+固定费，扭曲消失（第[3]组）。")
print("这就是纵向约束/RPM 效率辩护与『免费』式定价结构的共同源头。")
