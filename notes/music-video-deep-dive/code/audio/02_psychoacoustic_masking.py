"""
02_psychoacoustic_masking.py
============================
MP3 的真正魔法：心理声学掩蔽模型。

核心：
- 同时掩蔽（simultaneous masking）：强音会盖住邻近频率的弱音
- 前向/后向掩蔽：强音前后短时间内的弱音听不见
- 由掩蔽阈值决定每个子带能丢多少比特

本文件实现一个简化版的频域掩蔽阈值估计。
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

SR = 16000
N = 1024


def freq_to_bark(f):
    """Hz → Bark（临界频带）scale。Zwicker & Terhardt 1980."""
    return 13.0 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f / 7500.0) ** 2)


def bark_to_freq(b):
    """近似反函数（数值）"""
    from scipy.optimize import brentq
    return brentq(lambda f: freq_to_bark(f) - b, 1, SR / 2)


def spreading_function(bark_diff):
    """
    掩蔽扩散函数（simplified Terhardt）：
    强音对邻近 Bark 的掩蔽效应。
    bark_diff = bark_pineer - bark_target
    """
    return 15.81 + 7.5 * (bark_diff + 0.474) - 17.5 * np.sqrt(1 + (bark_diff + 0.474) ** 2)


def compute_masking_threshold(x):
    """
    输入信号 x（长度 N），返回每个频率 bin 的掩蔽阈值（dB SPL）。
    简化模型：取功率谱，每个峰值向邻近扩散掩蔽。
    """
    X = np.abs(rfft(x * np.hanning(N)))
    power = X ** 2
    freqs = rfftfreq(N, 1 / SR)
    bark = freq_to_bark(freqs)

    # 找峰值（掩蔽源）
    peaks = []
    for i in range(2, len(X) - 2):
        if X[i] > X[i - 1] and X[i] > X[i + 1] and X[i] > np.max(X) * 0.05:
            peaks.append((i, 10 * np.log10(power[i] + 1e-10)))

    # 每个频率 bin 的阈值 = 所有峰对该 bin 的掩蔽扩散叠加（power sum 近似）
    threshold_dB = np.full(len(X), -100.0)  # 默认安静阈值很低
    # 安静阈值（Terhardt）：低于这个听不见
    quiet = 3.64 * (freqs / 1000) ** -0.8 - 6.5 * np.exp(-0.6 * (freqs / 1000 - 3.3) ** 2) + 1e-3 * (freqs / 1000) ** 4
    threshold_dB = np.maximum(threshold_dB, quiet - 20)

    for idx, peak_dB in peaks:
        bark_diff = bark - bark[idx]
        mask = peak_dB + spreading_function(bark_diff) - 10  # 偏置
        threshold_dB = np.maximum(threshold_dB, mask)

    return freqs, X, threshold_dB


def simulate_mp3_like_quantization(x, threshold_dB):
    """
    模拟 MP3：根据掩蔽阈值决定每个 bin 保留多少精度。
    听不见的（X_dB < threshold）= 直接置零。
    """
    X = rfft(x * np.hanning(N))
    X_dB = 20 * np.log10(np.abs(X) + 1e-10)
    # 低于阈值的系数 = 扔掉（量化到 0）
    mask_keep = X_dB > threshold_dB
    X_quant = X * mask_keep
    return X_quant, mask_keep.sum(), len(X)


if __name__ == "__main__":
    # 合成：440Hz 强 + 500Hz 弱（500Hz 会被 440Hz 同时掩蔽）
    t = np.arange(N) / SR
    x = (0.8 * np.sin(2 * np.pi * 440 * t)
         + 0.05 * np.sin(2 * np.pi * 500 * t)
         + 0.05 * np.sin(2 * np.pi * 2000 * t))

    freqs, X, thr = compute_masking_threshold(x)
    Xq, n_keep, n_total = simulate_mp3_like_quantization(x, thr)

    print(f"[心理声学掩蔽] 总系数 {n_total}, 保留 {n_keep}, 扔掉 {n_total - n_keep}")
    print(f"              扔掉比例 {(n_total - n_keep) / n_total * 100:.0f}%")
    print("              → 这就是 MP3 在 128kbps 听起来还行的原因")
    print("              → 500 Hz 那条弱音很可能被 440 Hz 强音掩蔽而丢掉")

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.semilogx(freqs[1:], 20 * np.log10(X[1:] + 1e-10), label='signal spectrum')
        plt.semilogx(freqs[1:], thr[1:], 'r--', label='masking threshold (听不见区)')
        plt.fill_between(freqs[1:], -120, thr[1:], alpha=0.1, color='red', label='masked (扔掉)')
        plt.xlabel("Hz"); plt.ylabel("dB"); plt.ylim(-100, 60); plt.legend()
        plt.title("Psychoacoustic Masking (MP3 core idea)")
        plt.savefig("masking_demo.png", dpi=80); print("[saved] masking_demo.png")
    except ImportError:
        pass
