#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柠檬市场三幕剧：逆向选择如何杀死一个市场，机制设计如何救活它
（对应 00 章✨美之时刻 与 04 章代码走廊①）。

模型（Akerlof 1970 的最小数值版）：
  - 卖方知道自家商品质量 q（私有信息），买方只见价格、按在场平均质量出价；
  - 买方支付意愿 = a·q（a=1.3：买方估值系统性高于卖方 30%，若无信息问题全市场都能成交）；
  - 试探价格动态：价格 p 下出场的是 q ≤ p/a 的卖方，买方按平均质量修正出价 p' = a·E[q|q≤p/a]。

三幕：
  A 幕 均匀质量（q~U[0,1]）：出价几何坍塌（p'=p/2），20 轮内跌破初始价 1%，市场解体；
     对照全信息基准：每单位都成交，福利 = (a-1)·E[q] = 0.15。
  B 幕 两类型（50% 柠檬 q=0.4，50% 好车 q=0.9）：吸引好车的池化价须 ≥0.9，
     但买方至多付 a·E[q]=1.3×0.65=0.845 < 0.9 → 好车绝迹，均衡=柠檬专场 p≈0.52。
  C 幕 池化价+平衡交叉补贴重建（ACA 三件套的微缩版，对应 Einav-Finkelstein 风险调剂）：
     池化价 p=0.845 + 柠檬单位缴/好车单位补的平衡转移，两类卖方都自愿参与，
     福利从 0.06（仅柠檬）升至 0.195（全信息水平）。

断言：
  A. 20 轮内 p < 1%·p0 且在场份额 < 1%；不对称信息福利 < 1e-3；全信息基准 = 0.15。
  B. 均衡搜索：成交中好车份额 = 0，成交份额 = 50%，福利 = 0.06。
  C. 交叉补贴预算恰好平衡；两类都参与；成交份额 = 100%；福利 = 0.195（> 3×B 幕）。
"""
import numpy as np

a = 1.3  # 买方质量溢价比（WTP = a·q）

# ───────────────────── 幕 A：均匀质量市场的几何坍塌 ─────────────────────
def cond_mean(t, n=200_001):
    """E[q | q ≤ t]，q~U[0,1]，网格数值积分（不硬编码解析式 t/2）。"""
    if t <= 0.0:
        return 0.0
    qs = np.linspace(0.0, t, n)
    return np.trapezoid(qs, qs) / t          # ∫q dq / P(q≤t)

p0 = 0.8
p_hist, vol_hist = [p0], [min(p0 / a, 1.0)]
for _ in range(20):
    p = p_hist[-1]
    p_hist.append(a * cond_mean(p / a))          # 买方按平均质量修正出价
    vol_hist.append(min(p_hist[-1] / a, 1.0))    # 本轮出场份额 P(q ≤ p/a)

w_asym = vol_hist[-1] * (a - 1) * cond_mean(p_hist[-1] / a)  # 末轮实现的交易增益
w_full = (a - 1) * 0.5                                        # 全信息：(a-1)·E[q]

print(f"[A] 价格: {p0:.3f} → {p_hist[-1]:.2e}（{len(p_hist)-1} 轮，每轮约减半）；"
      f"在场份额 {vol_hist[0]:.2f} → {vol_hist[-1]:.2e}")
print(f"[A] 福利：不对称信息 ≈ {w_asym:.2e} vs 全信息基准 {w_full:.4f}")
assert p_hist[-1] < 0.01 * p0, "价格未在 20 轮内坍塌到初始价 1%"
assert vol_hist[-1] < 0.01, "在场份额未趋零——市场解体不彻底"
assert w_asym < 1e-3, "不对称信息下仍有可观交易"
assert abs(w_full - 0.15) < 1e-12, "全信息基准应为 0.15"

# ───────────────────── 幕 B：两类型市场，好车绝迹 ─────────────────────
q_types = np.array([0.4, 0.9])            # 柠檬 / 好车（卖方保留价 = q）
shares = np.array([0.5, 0.5])

def buyer_wtp(p):
    """价格 p 下在场卖方的平均质量 → 买方最高出价；无人在场返回 0。"""
    mask = q_types <= p
    if not mask.any():
        return 0.0, mask
    return a * np.average(q_types, weights=shares * mask), mask

grid = np.linspace(0.01, 1.2, 2000)
feasible = []
for p in grid:
    w, m = buyer_wtp(p)
    if m.any() and w >= p - 1e-9:
        feasible.append((p, m))
p_eq, mask_eq = max(feasible, key=lambda t: t[0])
share_traded = shares[mask_eq].sum()
good_share = (shares[1] / share_traded) if mask_eq[1] else 0.0
w_b = sum(sh * (a * q - q) for sh, q, m in zip(shares, q_types, mask_eq) if m)

print(f"[B] 均衡价格 ≈ {p_eq:.3f}（柠檬专场）；成交份额 {share_traded:.0%}；"
      f"成交中好车份额 {good_share:.0%}；福利 {w_b:.4f}")
assert not mask_eq[1], "好车竟然出场——池化逻辑有 bug"
assert abs(share_traded - 0.5) < 1e-9, "成交份额应恰为柠檬占比 50%"
assert abs(w_b - 0.06) < 1e-9, "B 幕福利应为 0.06"
assert 0.4 <= p_eq <= 0.52 + 1e-9, "柠檬专场价格应落在 [0.4, 0.52]"

# ───────────── 幕 C：池化价 + 预算平衡的交叉补贴（风险调剂微缩版） ─────────────
p_pool = a * np.average(q_types, weights=shares)   # 0.845：两类全在场的池化价（买方顶格出价）
s_good = q_types[1] - p_pool                       # 好车单位补贴：补足其保留价
levy_lemon = s_good * shares[1] / shares[0]        # 柠檬单位征费：使预算恰好平衡
revenue = levy_lemon * shares[0]
cost = s_good * shares[1]
net_lemon, net_good = p_pool - levy_lemon, p_pool + s_good
w_c = sum(sh * (a * q - q) for sh, q in zip(shares, q_types))   # 转移在福利中抵消

print(f"[C] 池化价 {p_pool:.3f}；交叉补贴：柠檬单位缴 {levy_lemon:.3f}、"
      f"好车单位补 {s_good:.3f}（预算 {revenue:.4f} = {cost:.4f}）")
print(f"[C] 卖方净得：柠檬 {net_lemon:.3f}（≥保留 {q_types[0]}）、"
      f"好车 {net_good:.3f}（=保留 {q_types[1]}）；成交份额 100%；福利 {w_c:.4f}")
assert abs(revenue - cost) < 1e-12, "交叉补贴预算不平衡"
assert net_lemon >= q_types[0] - 1e-12 and net_good >= q_types[1] - 1e-12, "有类型不愿参与"
assert abs(w_c - 0.195) < 1e-9, "C 幕福利应为 0.195（全信息水平）"
assert w_c > 3 * w_b, "重建后福利应超过仅柠檬市场的三倍"

print("\n[ALL ASSERTS PASSED] 价格本身改变商品质量构成：信息不对称摧毁的不只是几笔交易，"
      "而是市场本身（A→B）；把『了解类型』换成一个预算平衡的转移机制，市场完整重建（C）"
      "——这正是 00 章『价格改变质量』与 04 章『机制即代码』的实测现场。")
