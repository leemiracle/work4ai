#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wright 学习曲线（干中学）的拟合、判别与外推（对应 00 章✨美之时刻 与 04 章代码走廊①）。

模型：
  - Wright 律（1936，飞机机身工时）：单位成本 C = a·Q^(-b)，Q=累计产量；
  - 学习率 LR = 1 - 2^(-b)：累计产量每翻倍，成本下降的比例；
  - Moore 律（对照）：C = a·e^(-g·t)，对时间指数下降——产量加速期会系统性跑偏。

断言：
  A. 合成数据（b=−log2(0.8)≈0.3219 即 LR=20%，σ=0.03 对数正态噪声，seed=42）
     OLS 恢复：|b̂−b|<0.03，|LR̂−20%|<2pp
  B. 模型判别：产量增速 20%/年→45%/年 分段加速时，Wright（对累计产量）R² > Moore（对时间）R²
     ——累计产量才是成本下降的因果变量，时间只是它的代理
  C. 十年十倍的算术：LR=20% 下累计产量 ×1024（2^10）→ 成本降 1−0.8^10≈89.3%
     （OWID「光伏十年降约 90%」的常识锚）
  D. 外推预测：用 A 的拟合预测 Q=2^20 处成本，误差 <15%
"""
import numpy as np

rng = np.random.default_rng(42)
b_true = -np.log2(0.8)          # ≈ 0.32193
LR_true = 1 - 2 ** (-b_true)    # = 0.20

# ---- A. 合成 Wright 数据 + OLS 恢复 ----
d = np.arange(16)
Q1 = 2.0 ** d                                   # 累计产量：1,2,4,...,32768（15 次翻倍）
C1 = 1.0 * Q1 ** (-b_true) * np.exp(rng.normal(0, 0.03, Q1.size))
X1 = np.column_stack([np.ones_like(Q1), np.log(Q1)])
coef, *_ = np.linalg.lstsq(X1, np.log(C1), rcond=None)
a_hat, b_hat = np.exp(coef[0]), -coef[1]
LR_hat = 1 - 2 ** (-b_hat)
print(f"[A] OLS 恢复: b̂={b_hat:.4f}（真值 {b_true:.4f}），学习率 LR̂={LR_hat*100:.2f}%（真值 20%）")
assert abs(b_hat - b_true) < 0.03, "b̂ 偏离真值"
assert abs(LR_hat - 0.20) < 0.02, "学习率偏离 20%"

# ---- B. Wright vs Moore 判别：产量分段加速 ----
t = np.arange(60, dtype=float)
lam = np.where(t < 20, 0.20, 0.45)              # 年产量增速：前 20 年 20%/年，之后 45%/年
q = 1.0 * np.exp(np.cumsum(lam))                # 年产量
Q2 = np.cumsum(q) + 1.0                         # 累计产量
C2 = 1.0 * Q2 ** (-b_true) * np.exp(rng.normal(0, 0.03, t.size))

def r2(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    ss_res = np.sum((y - X @ beta) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot

logC2 = np.log(C2)
R2_wright = r2(logC2, np.column_stack([np.ones_like(t), np.log(Q2)]))
R2_moore = r2(logC2, np.column_stack([np.ones_like(t), t]))
print(f"[B] 产量分段加速（20%→45%/年）: R²(Wright)={R2_wright:.4f} > R²(Moore)={R2_moore:.4f}")
assert R2_wright > R2_moore + 0.01, "Wright 未显著胜出——累计产量才应是因果变量"

# ---- C. 十年十倍的算术 ----
drop = 1 - 0.8 ** 10                            # 累计产量 ×2^10=1024
print(f"[C] LR=20% 下累计产量×1024 → 成本下降 {drop*100:.1f}%（OWID 光伏十年降 ~90% 的常识锚）")
assert 0.85 < drop < 0.92

# ---- D. 外推预测 ----
Q_new = 2.0 ** 20
C_true = 1.0 * Q_new ** (-b_true)
C_pred = a_hat * Q_new ** (-b_hat)
err = abs(C_pred - C_true) / C_true
print(f"[D] 预测 Q=2^20: 预测 {C_pred:.3e} vs 真值 {C_true:.3e}，误差 {err*100:.2f}%")
assert err < 0.15

print("\n[ALL ASSERTS PASSED] 成本下降的因果变量是累计产量而非时间：")
print("价格会周期性背叛学习曲线（2023-24 组件崩价 60-70%、2025 政策反内卷反弹 30-45%），")
print("但曲线本身长期不爽约——这正是技术经济学 01 章『成本与价格的分离』的实测现场。")
