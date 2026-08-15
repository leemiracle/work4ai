"""
01_fourier_stft_mdct.py
=======================
音频三大变换：FFT / STFT / MDCT 的最小实现与可视化。

为什么这三个：
- FFT: 任何信号的频域等价
- STFT: 时变信号（音乐/语音）必备——滑窗 FFT
- MDCT: MP3/AAC/Opus 的核心变换（有时域混叠对消 TDAC）

零外部依赖（除可选 matplotlib）。
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

SR = 16000  # 采样率

# ============ 1. 合成一个真实音色（带泛音的小提琴近似）============
def violin_like(freq=440, dur=1.0, harmonics=None):
    """基频 + 多个泛音叠加 = 音色"""
    if harmonics is None:
        # (振幅, 倍频数)
        harmonics = [(1, 1), (0.7, 2), (0.5, 3), (0.3, 4), (0.2, 5), (0.1, 6)]
    t = np.arange(int(SR * dur)) / SR
    x = sum(a * np.sin(2 * np.pi * freq * k * t) for a, k in harmonics)
    return t, x / np.max(np.abs(x))  # 归一化


# ============ 2. FFT ============
def fft_demo(x):
    """单段 FFT：把整段信号分解到频域"""
    N = len(x)
    X = rfft(x * np.hanning(N))  # 加窗减少频谱泄漏
    freqs = rfftfreq(N, 1 / SR)
    return freqs, np.abs(X)


# ============ 3. STFT（短时傅里叶）============
def stft(x, win=1024, hop=256):
    """滑窗 FFT -> 时频谱谱图"""
    n_frames = 1 + (len(x) - win) // hop
    out = np.zeros((win // 2 + 1, n_frames))
    for i in range(n_frames):
        seg = x[i * hop:i * hop + win] * np.hanning(win)
        out[:, i] = np.abs(rfft(seg))
    return out


# ============ 4. MDCT（Modified Discrete Cosine Transform）============
def mdct(x, N=512):
    """
    MDCT: Princen-Bradley 1987。
    输入长度 2N（50% 重叠窗口），输出长度 N。
    关键性质：相邻块的时域混叠对消（TDAC）。

    X[k] = sum_{n=0}^{2N-1} x[n] * cos(pi/N * (n + 1/2 + N/2) * (2k+1))
    """
    n = np.arange(2 * N)
    k = np.arange(N)
    mat = np.cos(np.pi / N * (n[None, :] + 0.5 + N / 2) * (2 * k[:, None] + 1))
    return mat @ x


def window_mdct(N=512):
    """正弦窗，满足 Princen-Bradley 完美重建条件 w[n]^2 + w[n+N]^2 = 1"""
    return np.sin(np.pi / (2 * N) * (np.arange(2 * N) + 0.5))


def mdct_forward_signal(x, N=512):
    """对整段信号做分块 MDCT，返回 [n_blocks, N]"""
    w = window_mdct(N)
    n_blocks = len(x) // N - 1
    blocks = []
    for i in range(n_blocks):
        seg = x[i * N:(i + 2) * N] * w  # 2N 长度，50% 重叠
        blocks.append(mdct(seg, N))
    return np.array(blocks)


if __name__ == "__main__":
    t, x = violin_like(440, 1.0)

    # FFT demo
    freqs, mag = fft_demo(x[:8192])
    top_idx = np.argsort(mag)[::-1][:5]
    print("[FFT] 能量最大的 5 个频率:")
    for i in top_idx:
        print(f"  {freqs[i]:7.1f} Hz   幅度={mag[i]:.2f}")
    # 应该看到 440, 880, 1320, 1760, 2200 — 泛音列

    # STFT
    S = stft(x, win=1024, hop=256)
    print(f"\n[STFT] 谱图形状 {S.shape}, 总能量 {np.linalg.norm(S):.1f}")

    # MDCT
    blocks = mdct_forward_signal(x, N=512)
    # 能量集中性：每个 block 只需保留少数系数即可近似重建
    energy = (blocks ** 2).sum(axis=0)
    cum = np.cumsum(energy) / energy.sum()
    k_90 = np.searchsorted(cum, 0.9)  # 保留多少系数能涵盖 90% 能量
    print(f"\n[MDCT] 每块 512 个系数，保留前 {k_90} 个即可覆盖 90% 能量")
    print("       → 这就是 MP3 能扔掉大量系数的物理原因")

    # 可视化（matplotlib 缺失则跳过）
    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(3, 1, figsize=(10, 8))
        axes[0].plot(t[:2000], x[:2000]); axes[0].set_title("Waveform (440 Hz + harmonics)")
        axes[0].set_xlabel("time (s)")
        axes[1].plot(freqs[:2000], mag[:2000]); axes[1].set_title("FFT spectrum")
        axes[1].set_xlabel("Hz"); axes[1].set_xlim(0, 4000)
        axes[2].imshow(20 * np.log10(S + 1e-6), aspect='auto', origin='lower',
                       extent=[0, len(x) / SR, 0, SR / 2])
        axes[2].set_title("STFT spectrogram"); axes[2].set_xlabel("time (s)"); axes[2].set_ylabel("Hz")
        plt.tight_layout(); plt.savefig("fourier_demo.png", dpi=80); print("\n[saved] fourier_demo.png")
    except ImportError:
        print("\n(matplotlib 未安装，跳过画图)")
