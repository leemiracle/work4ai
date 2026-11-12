# -*- coding: utf-8 -*-
"""
讲透声学 · 实验：拍频的 FFT 解剖 + 驻波模式的正交性与能量守恒
对应章：00-体系结构（§一 驻波/模式论）、03-可构造与结构（§三 模式离散谱/§一 解析构造）
运行：python standing_wave_beats_fft.py   （纯 numpy，无外部依赖）

三个断言：
  A1 拍频信号频域只有两根谱线（440/444 Hz），包络检波后出现 |Δf|=4 Hz 峰
  A2 两端固定弦模式族 {sin(nπx/L)} 数值积分正交（非对角 <1e-12）
  A3 驻波总能量（动能+势能）在解析构造下守恒（漂移 <1e-10）
"""
import numpy as np

# ───────────────────────── A1 拍频与 FFT ─────────────────────────
print("═" * 64)
print("A1 拍频：440+444 Hz 的时域'嗡-嗡-嗡'在频域只是两根谱线")
print("═" * 64)
fs, T = 8192.0, 10.0                  # 采样率/时长 → FFT 分辨率 0.1 Hz
t = np.arange(int(fs * T)) / fs
f1, f2 = 440.0, 444.0
s = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)

S = np.abs(np.fft.rfft(s)) / len(s)
freqs = np.fft.rfftfreq(len(s), 1 / fs)

def top_peak(mask):
    idx = np.argmax(S * mask)
    return freqs[idx]

peak1 = freqs[np.argmax(S)]
mask_used = np.abs(freqs - peak1) > 1.0          # 挖掉第一峰找第二峰
peak2 = top_peak(mask_used)
print(f"  谱线峰：{peak1:.1f} Hz 与 {peak2:.1f} Hz（理论 440/444）")

# 包络检波：|s(t)| 低通（移动平均 64ms 窗）后再看低频谱
env = np.abs(s)
win = int(0.064 * fs)
env_lp = np.convolve(env, np.ones(win) / win, mode="same")
E = np.abs(np.fft.rfft(env_lp)) / len(env_lp)
low = (freqs > 0.5) & (freqs < 50)               # 只看低频段
beat = freqs[np.where(low)[0][np.argmax(E[low])]]
print(f"  包络谱峰：{beat:.2f} Hz（理论 |f1-f2| = {abs(f1-f2):.0f} Hz）")

assert abs(peak1 - 440) < 0.2 and abs(peak2 - 444) < 0.2, "A1 断言失败：谱线位置"
assert abs(beat - 4.0) < 0.3, "A1 断言失败：拍频位置"
print("  [A1 ✓] 两根谱线 + 4 Hz 拍频包络，全部命中（窗长 64ms，分辨率 0.1 Hz）")
print(f"  解读：'拍'不是第三个频率——是两列独立波的线性叠加被耳朵做包络检波。")

# ───────────────────── A2 模式正交性（梯形积分） ─────────────────────
print()
print("═" * 64)
print("A2 两端固定弦：模式族 {sin(nπx/L)} 的正交性（数值梯形积分 vs δ_mn/2）")
print("═" * 64)
L, N = 1.0, 4001
x = np.linspace(0, L, N)
modes = [np.sin(n * np.pi * x / L) for n in range(1, 7)]
gram = np.zeros((6, 6))
for m in range(6):
    for n in range(6):
        gram[m, n] = np.trapezoid(modes[m] * modes[n], x)
off = np.abs(gram - np.diag(np.diag(gram))).max()
dia = np.abs(np.diag(gram) - 0.5).max()
print(f"  Gram 矩阵对角线 ≈ {np.diag(gram)[:3].round(12)}（理论全 0.5）")
print(f"  非对角最大 |G_mn| = {off:.2e}（理论 0）")
assert off < 1e-12 and dia < 1e-12, "A2 断言失败：正交性"
print("  [A2 ✓] 模式族两两正交到机器精度——这是驻波可分解、能量可分账的根据")

# ───────────────────── A3 驻波能量守恒 ─────────────────────
print()
print("═" * 64)
print("A3 驻波能量守恒：E(t)=T+U 恒定（动能与势能周期性互换，总额不动）")
print("═" * 64)
c, rho_tau = 1.0, 1.0                             # 无量纲：c=√(τ/ρ)=1
A = {1: 0.3, 2: 0.2}                              # 两个模式的振幅
tt = np.linspace(0, 4.0, 4001)
T_kin, U_pot = [], []
for t_i in tt:
    u_t = sum(A[n] * (-n * np.pi * c) * np.sin(n * np.pi * x) * np.sin(n * np.pi * c * t_i)
              for n in A)                          # ∂u/∂t
    u_x = sum(A[n] * (n * np.pi) * np.cos(n * np.pi * x) * np.cos(n * np.pi * c * t_i)
              for n in A)                          # ∂u/∂x
    T_kin.append(0.5 * rho_tau * np.trapezoid(u_t**2, x))
    U_pot.append(0.5 * rho_tau * np.trapezoid(u_x**2, x))
T_kin, U_pot = np.array(T_kin), np.array(U_pot)
E_tot = T_kin + U_pot
drift = (E_tot.max() - E_tot.min()) / E_tot.mean()
phases = 2 * np.pi * 2 * tt                        # 二模式各自周期换能
print(f"  总能量 E = {E_tot.mean():.10f}（均值），相对漂移 {drift:.2e}")
print(f"  动能摆幅：[{T_kin.min():.4f}, {T_kin.max():.4f}]，势能摆幅：[{U_pot.min():.4f}, {U_pot.max():.4f}]")
assert drift < 1e-10, "A3 断言失败：能量守恒"
print("  [A3 ✓] 动能势能周期互换、总额守恒——'弦的振动'是能量在两种形态间流动")

print()
print("全部断言通过 ✓")
print("带走一句（00/03 章）：驻波的'模式'是边界条件选出的离散语言；")
print("正交性让每个模式独立记账，线性让叠加不串账——这就是乐器音高离散、")
print("房间模式'染色'、以及傅里叶方法在声学全能的同一个根源。")
