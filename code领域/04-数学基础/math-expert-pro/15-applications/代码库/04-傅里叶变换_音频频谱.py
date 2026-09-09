"""
傅里叶变换与音频频谱分析
=======================
数学概念：傅里叶变换 (FFT) / 频谱分析 / 数字滤波
应用领域：音频处理、信号处理、通信、语音识别
核心思想：任意信号可分解为不同频率正弦波的叠加。FFT 将信号从时域变换到频域,
         揭示其频率成分。在频域滤除不需要的频率后, 用逆 FFT (IFFT) 重建滤波后的时域信号。
运行方式：python "04-傅里叶变换_音频频谱.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============ 1. 数据生成：合成音频信号 ============
FS = 2000                      # 采样率 (Hz)
T = 1.0                        # 信号时长 (秒)
t = np.linspace(0, T, int(FS * T), endpoint=False)

# 三个频率成分 + 噪声 (模拟含基频/谐波/高频干扰的音频)
f1, f2, f3 = 50, 120, 500      # 50Hz 基音, 120Hz 谐波, 500Hz 高频干扰
signal_clean = (1.0 * np.sin(2 * np.pi * f1 * t)
                + 0.5 * np.sin(2 * np.pi * f2 * t)
                + 0.8 * np.sin(2 * np.pi * f3 * t))
noise = 0.3 * np.random.randn(len(t))
signal = signal_clean + noise
print(f"[信号] 采样率={FS}Hz, 时长={T}s, 采样点={len(t)}")
print(f"[成分] 基频={f1}Hz, 谐波={f2}Hz, 高频干扰={f3}Hz")

# ============ 2. 数学建模：FFT 频谱分析 ============
def compute_fft(sig, fs):
    """计算单边幅度谱。返回频率轴和对应幅值。"""
    N = len(sig)
    fft_vals = np.fft.fft(sig)                    # 离散傅里叶变换
    freqs = np.fft.fftfreq(N, 1 / fs)             # 频率轴
    # 取正频率部分
    pos = freqs >= 0
    freqs_pos = freqs[pos]
    magnitude = 2.0 / N * np.abs(fft_vals[pos])   # 归一化幅值 (单边谱)
    return freqs_pos, magnitude

freqs, mag = compute_fft(signal, FS)

# 识别主要频率成分
peak_idx = np.argsort(mag)[-3:][::-1]
print("[频谱] 检测到的前 3 个峰值频率:")
for i in peak_idx:
    print(f"  {freqs[i]:6.1f} Hz  幅值={mag[i]:.3f}")

# ============ 3. 低通滤波：频域处理 ============
def lowpass_filter(sig, fs, cutoff):
    """理想低通滤波器: FFT → 频域截断 → IFFT。"""
    N = len(sig)
    fft_vals = np.fft.fft(sig)
    freqs = np.fft.fftfreq(N, 1 / fs)
    # 构造低通掩码: |f| < cutoff 的频率保留
    mask = np.abs(freqs) < cutoff
    fft_filtered = fft_vals * mask
    return np.fft.ifft(fft_filtered).real

CUTOFF = 200  # 截止频率: 滤除 500Hz 干扰, 保留 50/120Hz
filtered = lowpass_filter(signal, FS, CUTOFF)
freqs_f, mag_f = compute_fft(filtered, FS)

# ============ 4. 可视化 ============
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

ax = axes[0, 0]
ax.plot(t[:300], signal[:300], "b-", lw=0.8)
ax.set_xlabel("时间 (s)")
ax.set_ylabel("幅值")
ax.set_title("原始信号 (时域) — 含噪声与高频干扰")
ax.grid(alpha=0.3)

ax = axes[0, 1]
ax.plot(freqs, mag, "r-", lw=0.8)
for f in [f1, f2, f3]:
    ax.axvline(f, color="gray", ls=":", alpha=0.7)
ax.set_xlabel("频率 (Hz)")
ax.set_ylabel("幅值")
ax.set_title("原始信号频谱 (频域) — FFT")
ax.set_xlim(0, 700)
ax.grid(alpha=0.3)

ax = axes[1, 0]
ax.plot(t[:300], filtered[:300], "g-", lw=0.8)
ax.plot(t[:300], signal_clean[:300], "k--", lw=0.5, alpha=0.6, label="真实纯净信号")
ax.set_xlabel("时间 (s)")
ax.set_ylabel("幅值")
ax.set_title(f"低通滤波后 (截止 {CUTOFF}Hz)")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1, 1]
ax.plot(freqs, mag, "r-", lw=0.6, alpha=0.4, label="滤波前")
ax.plot(freqs_f, mag_f, "b-", lw=1.2, label="滤波后")
ax.axvline(CUTOFF, color="green", ls="--", label=f"截止 {CUTOFF}Hz")
ax.set_xlabel("频率 (Hz)")
ax.set_ylabel("幅值")
ax.set_title("滤波前后频谱对比")
ax.set_xlim(0, 700)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("04-FFT频谱_结果.png", dpi=120)

# 量化滤波效果
noise_before = np.std(signal - signal_clean)
noise_after = np.std(filtered - (1.0*np.sin(2*np.pi*f1*t) + 0.5*np.sin(2*np.pi*f2*t)))
print(f"\n[结果] 图像已保存: 04-FFT频谱_结果.png")
print(f"[解读] 滤波前噪声标准差={noise_before:.3f}, 滤波后={noise_after:.3f}。"
      f"低通滤波有效去除了 {f3}Hz 高频干扰, 同时保留了 {f1}/{f2}Hz 有效成分。"
      f"FFT 是连接时域与频域的核心桥梁。")

if __name__ == "__main__":
    pass
