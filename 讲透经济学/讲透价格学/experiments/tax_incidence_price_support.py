#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税负转嫁与支持价格（对应 00 章✨美之时刻 / 02 章两副面孔 / 03 章转嫁闭式 /
04 章走廊①）。纯 numpy。

市场：Qd = 100 - p；Qs = 0.5 p（供给弹性为需求的一半 -> 供给方更"钝"）。

  A. 从量税 t=10：
     p_d - p_s = t 与 100 - p_d = 0.5 p_s 联立 -> p_s=60, p_d=70
     基期均衡 p*=66.67：买方 +3.33（1/3），卖方 -6.67（2/3）——弹性小者多担
  B. 对买方征税 10（价格楔子同向）：解出的 (p_d, p_s) 与 A 完全相同——记账面纱定理
  C. 支持价格（地板 60 < 均衡 66.67? 否—— 改用对称市场 Qs=p 做地板演示）：
     对称市场 Qd=100-p, Qs=p：均衡 50。地板 p_f=60：
     Qd=40, Qs=60，政府收购过剩 20，成本 1200；
     ΔCS=-450, ΔPS=+550, DWL=1100，恒等式 ΔCS+ΔPS+ΔGov = -DWL 逐项对账
"""
import numpy as np

# ---------- A. 对称市场的税：谁钝谁付 ----------
# 用非对称市场演示弹性归宿
ad, bd = 100.0, 1.0          # Qd = ad - bd*p
as_, ds = 0.0, 0.5           # Qs = as_ + ds*p
t = 10.0
# 基期均衡
p0 = (ad - as_) / (bd + ds)
q0 = ad - bd * p0
ed = bd * p0 / q0            # 需求弹性（绝对值）= 1*66.67/33.33 = 2
es = ds * p0 / q0            # 供给弹性 = 0.5*66.67/33.33 = 1
# 税后：p_d - p_s = t；ad - bd*p_d = as_ + ds*p_s
ps_ = (ad - as_ - bd * t) / (bd + ds)
pd_ = ps_ + t
share_buyers = es / (es + ed)   # 弹性式预测买方份额
d_pd, d_ps = pd_ - p0, p0 - ps_
print(f"[A] 均衡 p*={p0:.4f}, Q*={q0:.4f}; 弹性 ed={ed:.2f}, es={es:.2f}")
print(f"[A] 税 t={t}: p_d={pd_:.4f} (买方 +{d_pd:.4f}), p_s={ps_:.4f} (卖方 -{d_ps:.4f})")
print(f"[A] 弹性式买方份额 = es/(es+ed) = {share_buyers:.4f}; 实际买方份额 = "
      f"{d_pd/t:.4f}")
assert abs(d_pd - t * share_buyers) < 1e-9, "弹性归宿公式不符"
assert d_ps > d_pd, "供给更钝（弹性小）应承担更多"
# DWL 平方律：t 翻倍 DWL 翻四倍（同市场）
def dwl(tax):
    psx = (ad - as_ - bd * tax) / (bd + ds)
    q_new = ad - bd * (psx + tax)
    return 0.5 * tax * (q0 - q_new)
w1, w2 = dwl(t), dwl(2 * t)
print(f"[A] DWL 平方律: t={t:.0f} -> {w1:.4f}; t={2*t:.0f} -> {w2:.4f} "
      f"(比值 {w2/w1:.4f})")
assert abs(w2 / w1 - 4.0) < 1e-9, "DWL 应随 t² 增长（翻倍即四倍）"

# ---------- B. 记账面纱：对买方 vs 对卖方征税等价 ----------
# 对买方：支付价 P（含税），卖方得 P-t：Qd(P)=Qs(P-t) -> 同一方程组
# Qd(P) = ad - bd*P；Qs(P-t) = as_ + ds*(P-t)；相等 -> P = (ad - as_ + ds*t)/(bd+ds)
pd_b = (ad - as_ + ds * t) / (bd + ds)
ps_b = pd_b - t
print(f"\n[B] 对买方征 {t}: 买方支付 p_d={pd_b:.4f}, 卖方到手 p_s={ps_b:.4f}")
print(f"[B] 对卖方征 {t}: 买方支付 p_d={pd_:.4f}, 卖方到手 p_s={ps_:.4f}")
assert abs(pd_b - pd_) < 1e-12 and abs(ps_b - ps_) < 1e-12, \
    "买卖双方征税应完全等价（记账面纱定理）"
print("[B] ✅ 税单写谁的名字不影响谁付钱——楔子只有一个几何位置")

# ---------- C. 支持价格：政府收购与福利对账 ----------
# 换对称市场便于手算：Qd=100-p, Qs=p
Qd = lambda p: 100 - p
Qs = lambda p: p
p_star = 50.0
pf = 60.0                                    # 支持价（地板）
qd_pf, qs_pf = Qd(pf), Qs(pf)
surplus = qs_pf - qd_pf                      # 过剩 20
gov_cost = pf * surplus                      # 收购支出 1200
# 福利分解（供给逆函数 p=q，需求逆函数 p=100-q）
CS0 = 0.5 * (100 - p_star) * Qd(p_star)      # 1250
CS1 = 3200.0 - pf * qd_pf                    # ∫0^40(100-q)dq - 60*40 = 3200-2400
PS0 = p_star * Qs(p_star) - 0.5 * p_star ** 2   # 2500-1250
PS1 = pf * qs_pf - 0.5 * pf ** 2                # 3600-1800
dCS, dPS = CS1 - CS0, PS1 - PS0
DWL = -(dCS + dPS - gov_cost)
print(f"\n[C] 支持价 {pf}（均衡 {p_star}）: 需求量 {qd_pf}, 供给量 {qs_pf}, "
      f"政府收购 {surplus}, 支出 {gov_cost:.0f}")
print(f"[C] ΔCS={dCS:.0f}, ΔPS={dPS:.0f}, ΔGov=-{gov_cost:.0f}, "
      f"合计={dCS+dPS-gov_cost:.0f}, DWL={DWL:.0f}")
assert abs(dCS - (-450.0)) < 1e-9, "消费者剩余变化应为 -450"
assert abs(dPS - 550.0) < 1e-9, "生产者剩余变化应为 +550"
assert abs(gov_cost - 1200.0) < 1e-9, "政府支出应为 1200"
assert abs(DWL - 1100.0) < 1e-9, "DWL 应为 1100（生产 550+消费 550）"
assert abs((dCS + dPS - gov_cost) + DWL) < 1e-9, "福利恒等式不闭合"
# DWL 两瓣对账：生产端浪费 ∫50^60 q dq = 550；消费端损失 ∫40^50 (100-q) dq = 550
waste_prod = 0.5 * (pf ** 2 - p_star ** 2)
loss_cons = (100 * 10 - 0.5 * (50 ** 2 - 40 ** 2))
print(f"[C] DWL 两瓣: 生产端浪费 {waste_prod:.0f} + 消费端损失 {loss_cons:.0f} "
      f"= {waste_prod + loss_cons:.0f}")
assert abs(waste_prod - 550) < 1e-9 and abs(loss_cons - 550) < 1e-9

print("\n[ALL ASSERTS PASSED] 弹性归宿（谁钝谁付）+ 记账面纱（写谁名字无用）+")
print("DWL 平方律（税率翻倍损失四倍）+ 支持价福利对账（补贴的自我复制回路起点）。")
print("价格的几何学从不撒谎——撒谎的从来是弹性估计。")
