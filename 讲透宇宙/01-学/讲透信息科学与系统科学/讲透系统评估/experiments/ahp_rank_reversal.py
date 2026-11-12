# -*- coding: utf-8 -*-
"""
AHP 特征向量机 + rank reversal 数值显形(对应 00/02/03/04 章)
============================================================
复现 Belton–Gear (1983) 的排序反转:在**完全一致**的两两比较下,
加入一个不触碰 B 利益的新方案 D,竟能把 B 抬到第一——
证明 rank reversal 不是"专家不一致"的锅,是 distributive 归一化的结构性效应。

跑法:python experiments/ahp_rank_reversal.py
"""
import numpy as np

def pairwise(v):
    """由真实重要性 v 构造完全一致的两两比较矩阵 a_ij = v_i / v_j。"""
    v = np.asarray(v, float)
    return np.outer(v, 1.0 / v)

def ahp_weights(A, iters=200):
    """幂法提主特征向量(AHP 权重),并返回主特征值(一致性检验用)。"""
    v = np.ones(A.shape[0])
    for _ in range(iters):
        v = A @ v
        v = v / v.sum()
    lam = ((A @ v) / v).mean()          # 主特征值
    return v, lam

def consistency_ratio(A, lam):
    n = A.shape[0]
    RI = {1: 0, 2: 0, 3: .58, 4: .90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}  # 1-9 标度随机指标
    CI = (lam - n) / (n - 1) if n > 1 else 0.0
    if n <= 2:              # n≤2 的两两比较恒一致(AHP 惯例 CR≡0)
        return 0.0, 0.0
    return CI / RI[n], CI

def aggregate(vectors, weights):
    """distributive AHP:各准则下局部优先度(已归一)按准则权重加权合成总排序。"""
    return sum(w * np.asarray(v) / np.asarray(v).sum() for v, w in zip(vectors, weights))

def report(tag, names, scores, extra=""):
    order = np.argsort(-scores)
    print(f"[{tag}] " + " > ".join(f"{names[i]}({scores[i]:.4f})" for i in order) + extra)

# ── 场景:选址评估。准则1=交通(等权)、准则2=成本;真实重要性 v ──
w = (0.5, 0.5)                                   # 两准则等权
c1_AB, c2_AB = (1.0, 0.45), (0.5, 1.0)           # A 交通强、B 成本强
names3 = ["A(郊区)", "B(市区)"]

# 完全一致的两两比较矩阵 → 幂法权重 → 一致性
for tag, v_true in [("准则1", c1_AB), ("准则2", c2_AB)]:
    A = pairwise(v_true)
    wv, lam = ahp_weights(A)
    CR, CI = consistency_ratio(A, lam)
    print(f"[{tag}] 幂法权重={np.round(wv,6)} 解析={np.round(np.asarray(v_true)/sum(v_true),6)} | λmax={lam:.12f} CR={CR:.2e}")
    assert CR < 1e-9, "完全一致矩阵应 CR≈0"
    assert np.allclose(wv, np.asarray(v_true) / sum(v_true), atol=1e-10), "幂法=解析归一"

s_AB = aggregate([c1_AB, c2_AB], w)
report("三方案→两方案", names3, s_AB)
assert s_AB[0] > s_AB[1], "原始: A > B(交通优势胜出)"

# ── 加入激进方案 D:交通极强(1.4)、成本极弱(0.1)——完全不碰 B 的成本优势 ──
c1_ABD, c2_ABD = (1.0, 0.45, 1.4), (0.5, 1.0, 0.1)
names4 = names3 + ["D(新港区)"]
for tag, v_true in [("准则1'", c1_ABD), ("准则2'", c2_ABD)]:
    A = pairwise(v_true); _, lam = ahp_weights(A)
    CR, _ = consistency_ratio(A, lam)
    assert CR < 1e-9

s_ABD = aggregate([c1_ABD, c2_ABD], w)
report("加入 D 后", names4, s_ABD, extra="  ← rank reversal!")
assert s_ABD[1] > s_ABD[0], "反转: B > A(D 只稀释 A 的交通份额,B 躺赢)"

print()
print("结论:两轮比较矩阵全部完全一致(CR≈0),排序仍翻转——")
print("  rank reversal 是 distributive 归一化的结构性质,不是判断不一致的产物。")
print("  机制:D 在 A 的主场强、B 的主场弱;归一化把 A 的优势稀释得更多,B 被动登顶。")
print("[ALL ASSERTS PASSED] AHP 特征向量机正确;CR≈0;两场景排序断言通过。")
