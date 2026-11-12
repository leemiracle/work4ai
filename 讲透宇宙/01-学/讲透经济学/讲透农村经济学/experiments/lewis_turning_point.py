#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刘易斯二元经济与拐点：工资何时开始上涨（对应 00 章 §2 / 03 章 §2 / 04 章走廊①）。

刘易斯（Lewis 1954）二元经济：传统农业部门存在剩余劳动，现代工业部门
在制度工资 w̄（生存水平）上获得无限弹性劳动供给；资本利润再投资 →
现代部门扩张吸收劳动，工资纹丝不动；直到剩余劳动吸干（刘易斯拐点），
此后工资随资本积累单调上涨。

模型：现代部门 Y = K^α · L^(1-α)，劳动需求由 MPL = w 决定。
断言：
  A. 拐点前：就业扩张、产出扩张、工资钉死在 w̄（涨资本不涨工资）；
  B. 拐点后：就业钉死在 L_max，工资 = MPL 随 K 严格递增；
  C. 拐点位置有闭式解 K* = (w̄·L_max^α/(1-α))^(1/α)，数值轨迹在该处换挡；
  D. 积累越快（利润再投资率 s 高）越早到达拐点
     （"中国何时跨越刘易斯拐点"之争的参数版）。
参数：α=0.4，w̄=0.5，L_max=100，K0=1，折旧 δ=5%。
"""
import numpy as np

alpha, w_bar, L_max, delta = 0.4, 0.5, 100.0, 0.05

def Y(K, L):  return K ** alpha * L ** (1 - alpha)
def MPL(K, L): return (1 - alpha) * K ** alpha * L ** (-alpha)

def labor_demand(K):
    """制度工资下的意愿雇佣 = min(L*(K), L_max)；L* 为 MPL(K,·)=w̄ 的解。"""
    L_star = ((1 - alpha) * K ** alpha / w_bar) ** (1 / alpha)
    return min(L_star, L_max), L_star

# 闭式拐点：MPL(K*, L_max) = w̄  →  K* = (w̄·L_max^α/(1-α))^(1/α)
K_star = (w_bar * L_max ** alpha / (1 - alpha)) ** (1 / alpha)
assert abs(MPL(K_star, L_max) - w_bar) < 1e-9, "闭式 K* 处 MPL 应恰等于制度工资"
print(f"闭式拐点：K* = (w̄·L_max^α/(1-α))^(1/α) = {K_star:.2f}")
print(f"校验：MPL(K*={K_star:.2f}, L_max) = {MPL(K_star, L_max):.6f} = w̄ ✓")

def simulate(s, T=140):
    K, traj = 1.0, []
    for t in range(T):
        L, _ = labor_demand(K)
        w = max(w_bar, MPL(K, L))          # 劳动无限弹性段 w 钉在 w̄，其后 = MPL
        profit = Y(K, L) - w * L
        traj.append((t, K, L, w, Y(K, L)))
        K = max(K + s * profit - delta * K, 1e-9)
    return traj

def turning_period(traj):
    return next(t for t, K, L, w, y in traj if L >= L_max - 1e-9)

for s in [0.3, 0.8]:
    traj = simulate(s)
    Ks = np.array([r[1] for r in traj]); Ls = np.array([r[2] for r in traj])
    ws = np.array([r[3] for r in traj]); Ys = np.array([r[4] for r in traj])
    t_turn = turning_period(traj)

    assert np.allclose(ws[:t_turn], w_bar, atol=1e-9), "拐点前工资必须钉死在 w̄"
    assert np.all(np.diff(Ls[:t_turn]) > 0) and np.all(np.diff(Ys[:t_turn]) > 0), "拐点前就业与产出同步扩张"
    assert np.allclose(Ls[t_turn:], L_max, atol=1e-9), "拐点后就业钉死在 L_max"
    assert np.all(np.diff(ws[t_turn:]) > 0), "拐点后工资应随资本严格递增"
    assert Ks[t_turn] >= K_star > Ks[t_turn - 1], "换挡应恰在跨过闭式 K* 的那一步"

    print(f"\n[s={s}] 拐点期 t={t_turn}（换挡时 K={Ks[t_turn]:.1f} ≈ K*={K_star:.1f}）")
    print(f"  工资轨迹: 前 {t_turn} 期恒为 {w_bar}（涨资本不涨工资）→ 之后单调涨到 {ws[-1]:.3f}")
    print(f"  就业轨迹: {Ls[0]:.1f} → {L_max:.0f} 钉死；产出 {Ys[0]:.2f} → {Ys[-1]:.2f} 持续增长")

t_fast, t_slow = turning_period(simulate(0.8)), turning_period(simulate(0.3))
print(f"\n[D] 积累速度与拐点时点：s=0.8 于 t={t_fast} 到达，s=0.3 于 t={t_slow}（早 {t_slow - t_fast} 期）")
assert t_fast < t_slow, "高再投资率应更早到达拐点"

print("\n结论：'民工荒=刘易斯拐点'之争，争的不是模型结构，是 L_max 与 K 的现实取值——")
print("同一个模型，参数之争；发展经济学的辩论大多长这样。")
print("\nALL ASSERTIONS PASSED")
