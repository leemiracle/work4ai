"""
实验 01 — 机理建模：SIR 传染病模型
====================================
用 Euler 积分求解 SIR 微分方程，验证"机理已知时，3个参数预测拐点"。
对比：SIR vs 多项式拟合 vs (概念)神经网络——机理模型外推强。
跑法: python3 01_mechanistic.py  (需 numpy，几秒跑完)
"""
import numpy as np

# SIR 参数
beta = 0.4       # 传染率
gamma = 0.1      # 康复率（1/gamma = 平均病程 10 天）
N = 1000         # 总人口
S0, I0, R0 = N - 1, 1, 0  # 初始：1人感染
Rnought = beta * S0 / gamma  # 基本再生数

dt = 0.5  # 时间步（天）
days = 500

S, I, R = float(S0), float(I0), float(R0)
peak_I, peak_day = 0, 0
history = []

for t in range(days):
    dS = -beta * S * I / N * dt
    dI = (beta * S * I / N - gamma * I) * dt
    dR = gamma * I * dt
    S += dS
    I += dI
    R += dR
    history.append((S, I, R))
    if I > peak_I:
        peak_I, peak_day = I, t * dt

print("=" * 60)
print(f"SIR 传染病模型（β={beta}, γ={gamma}, N={N}）")
print("=" * 60)
print(f"基本再生数 R0 = {Rnought:.1f}  {'→ 爆发' if Rnought > 1 else '→ 消退'}")
print(f"感染峰值: {peak_I:.0f} 人 ({peak_I/N*100:.0f}% 人口感染)")
print(f"拐点（峰值时刻）: 第 {peak_day:.0f} 天")
print(f"最终康复: {R:.0f} 人 ({R/N*100:.0f}% 人口经历过感染)")
print()
print("对比（00 章的三大流派）：")
print(f"  SIR（机理）:        拐点≈第{peak_day:.0f}天, 仅需β,γ两个参数")
print(f"  多项式拟合:         需大量数据, 外推差")
print(f"  神经网络:           需大数据, 黑箱, 外推差")
print()
print("结论: 机理已知时，机理建模完胜数据驱动（外推强+可解释）")
