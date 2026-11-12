#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级价格歧视的数值实验（对应 00 章✨美之时刻、03 章定价阶梯、04 章走廊①）。

设定：同一产品、边际成本 MC=10，两个细分市场
    A 商务客：q_A = 50 - p    （低弹性：提价只掉少量客）
    B 休闲客：q_B = 90 - 3p   （高弹性：价格敏感，p=30 处停止购买）
统一定价与三级歧视定价全部由「嵌套网格 + 逐层缩放」数值求解（不抄解析解）。

断言：
  A. 歧视利润 700 > 统一 625（+12%）：p_A=30(q=20)、p_B=20(q=30) vs 统一 p=22.5(Q=50)
  B. 勒纳条件逐市场成立：(p-MC)/p = 1/|ε|（容差 1e-3），且弹性低的市场定高价
  C. 总产量不变：|Q_PD - Q_统一| < 1e-6（线性需求 + 共同 MC 的经典结果：
     三级歧视只是把既有产量重新分配，不改变总量）
  D. 总剩余下降：W_PD=1050 < W_统一=1087.5 —— 产量相同、配置错位
     （7.5 个单位从边际价值 22.5-30 的 A 市场挪到边际价值 20-22.5 的 B 市场，
     平均每单位损失 5，共 37.5）——「对企业好 ≠ 对社会好」。
"""
import numpy as np

MC = 10.0

def qA(p):
    return np.maximum(0.0, 50.0 - p)

def qB(p):
    return np.maximum(0.0, 90.0 - 3.0 * p)

def zoom_max(f, lo, hi, n=4001, rounds=12):
    """嵌套网格+逐层缩放的无梯度极大化：把 argmax 逼近到机器精度。"""
    for _ in range(rounds):
        xs = np.linspace(lo, hi, n)
        i = int(np.argmax(f(xs)))
        lo, hi = xs[max(0, i - 2)], xs[min(n - 1, i + 2)]
    xs = np.linspace(lo, hi, n)
    return float(xs[np.argmax(f(xs))])

# --- 统一定价（两个市场同一张价格标签） ---
pi_uni = lambda p: (p - MC) * (qA(p) + qB(p))
p_u = zoom_max(pi_uni, MC + 1e-6, 50.0 - 1e-6)
Q_u, profit_u = qA(p_u) + qB(p_u), pi_uni(p_u)

# --- 三级价格歧视（看得见身份，分别贴价） ---
pi_A = lambda p: (p - MC) * qA(p)
pi_B = lambda p: (p - MC) * qB(p)
p_A = zoom_max(pi_A, MC + 1e-6, 50.0 - 1e-6)
p_B = zoom_max(pi_B, MC + 1e-6, 30.0 - 1e-6)   # B 市场需求在 p=30 处掐断
Q_pd = qA(p_A) + qB(p_B)
profit_pd = pi_A(p_A) + pi_B(p_B)

print(f"[A] 统一: p*={p_u:.4f}, Q={Q_u:.2f}, π={profit_u:.2f}")
print(f"    歧视: p_A={p_A:.4f}(q_A={qA(p_A):.2f}), p_B={p_B:.4f}(q_B={qB(p_B):.2f}), π={profit_pd:.2f}")
assert profit_pd > profit_u, "歧视居然不赚钱——需求或优化器有 bug"
assert abs(profit_pd - 700.0) < 1e-3 and abs(profit_u - 625.0) < 1e-3, "利润偏离解析基准"
assert abs(profit_pd / profit_u - 1.12) < 0.005, "利润增幅应约 +12%"

# --- 勒纳条件：加成只由弹性决定 ---
eps_A = 1.0 * p_A / qA(p_A)    # |ε| = |dq/dp| * p/q
eps_B = 3.0 * p_B / qB(p_B)
for tag, p, eps in [("A", p_A, eps_A), ("B", p_B, eps_B)]:
    lerner = (p - MC) / p
    print(f"[B] 市场{tag}: p={p:.2f}, |ε|={eps:.4f}, Lerner={lerner:.4f}, 1/|ε|={1/eps:.4f}")
    assert abs(lerner - 1.0 / eps) < 1e-3, f"市场{tag}勒纳条件不成立"
assert eps_A < eps_B and p_A > p_B, "弹性低的市场应定高价——否则方向反了"

# --- 总产量不变（线性需求 + 共同 MC 的经典定理） ---
print(f"[C] Q_统一={Q_u:.6f}, Q_歧视={Q_pd:.6f}, |ΔQ|={abs(Q_pd - Q_u):.2e}")
assert abs(Q_pd - Q_u) < 1e-6, "三级歧视不应改变总产量（线性需求经典结果）"

# --- 总剩余：CS 数值积分（梯形法对线性需求精确），PS=(p-MC)q ---
def CS(qfun, p, choke, n=200001):
    pp = np.linspace(p, choke, n)
    return float(np.trapezoid(qfun(pp), pp))

CS_u = CS(qA, p_u, 50.0) + CS(qB, p_u, 30.0)
W_u = CS_u + profit_u
CS_pd = CS(qA, p_A, 50.0) + CS(qB, p_B, 30.0)
W_pd = CS_pd + profit_pd
print(f"[D] 统一: CS={CS_u:.2f}, W={W_u:.2f} | 歧视: CS={CS_pd:.2f}, W={W_pd:.2f} | ΔW={W_pd - W_u:.2f}")
assert W_pd < W_u - 1.0, "同产量错配置，总剩余应下降"
assert abs(W_u - 1087.5) < 0.1 and abs(W_pd - 1050.0) < 0.1, "总剩余偏离解析基准"
print(f"    错配置解剖：A 少卖 {27.5 - qA(p_A):.1f} 单位（每单位值 22.5-30），"
      f"B 多卖 {qB(p_B) - 22.5:.1f} 单位（每单位值 20-22.5）→ 每单位平均损失 5")

print("\n[ALL ASSERTS PASSED] 歧视利润 +12%、总产量不变、总剩余 -37.5——")
print("三个数字合起来就是管理经济学 03 章的定价阶梯：歧视把企业剩余做大、把社会剩余做小，")
print("「对企业好 ≠ 对社会好」，这正是大数据杀熟立法（个保法第24条）的经济学坐标。")
