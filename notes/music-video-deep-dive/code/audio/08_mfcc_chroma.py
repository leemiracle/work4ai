"""
08_mfcc_chroma.py
=================
音乐信息检索（MIR）两大特征：MFCC + Chroma。

MFCC (Mel-Frequency Cepstral Coefficients):
  语音/音乐识别通用特征。
  FFT → Mel 滤波器组（对数频率）→ log → DCT
  前 13 维通常已足够。

Chroma:
  12 维向量，每个 bin = 一个半音的能量。
  用于和弦识别、cover 检测、key 估计。
  基于 Constant-Q Transform（对数频率分辨率）。

零外部依赖。
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

SR = 16000


def hz_to_mel(f): return 2595 * np.log10(1 + f / 700)
def mel_to_hz(m): return 700 * (10 ** (m / 2595) - 1)


def mel_filterbank(n_filters=26, n_fft=512, sr=SR, fmin=0, fmax=None):
    """构造 Mel 滤波器组 [n_filters, n_fft//2+1]"""
    if fmax is None: fmax = sr / 2
    mel_min, mel_max = hz_to_mel(fmin), hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_filters + 2)
    hz_points = mel_to_hz(mel_points)
    freqs = rfftfreq(n_fft, 1 / sr)
    fb = np.zeros((n_filters, len(freqs)))
    for i in range(n_filters):
        left, center, right = hz_points[i:i + 3]
        for j, f in enumerate(freqs):
            if left <= f <= center:
                fb[i, j] = (f - left) / (center - left + 1e-10)
            elif center < f <= right:
                fb[i, j] = (right - f) / (right - center + 1e-10)
    return fb


def mfcc(x, n_fft=512, hop=256, n_mfcc=13, sr=SR):
    """提取 MFCC（一个帧序列）"""
    n_frames = 1 + (len(x) - n_fft) // hop
    fb = mel_filterbank(n_filters=26, n_fft=n_fft, sr=sr)
    mfcc_frames = []
    for i in range(n_frames):
        seg = x[i * hop:i * hop + n_fft] * np.hanning(n_fft)
        spec = np.abs(rfft(seg)) ** 2
        mel_energy = fb @ spec  # [n_filters]
        mel_energy = np.log(mel_energy + 1e-10)
        # DCT-II
        from scipy.fft import dct
        c = dct(mel_energy, type=2, norm='ortho')[:n_mfcc]
        mfcc_frames.append(c)
    return np.array(mfcc_frames)  # [n_frames, n_mfcc]


def cqt_power(x, n_bins=12 * 4, f0=130.81, sr=SR, bins_per_octave=12):
    """
    简化版 Constant-Q Transform。
    每八度固定 bins 数，频率对数等分。
    """
    bins = []
    for k in range(n_bins):
        f = f0 * 2 ** (k / bins_per_octave)
        if f >= sr / 2: break
        # 一个匹配该频率的窗（高斯，长度 ∝ 1/f）
        Q = 24
        N = max(int(Q * sr / f), 16)
        t = np.arange(N) / sr
        # 复数正弦 × 窗
        kernel = np.exp(-2j * np.pi * f * t) * np.hanning(N)
        bins.append(np.abs(np.dot(x[:N] if len(x) >= N else np.pad(x, (0, N - len(x))), kernel)))
    return np.array(bins)


def chroma(x, n_octaves=4, f0=130.81, sr=SR):
    """12 维 chroma：把 CQT 能量按 octave 折回 12 个半音"""
    cqt = cqt_power(x, n_bins=12 * n_octaves, f0=f0, sr=sr)
    chrom = np.zeros(12)
    for i, e in enumerate(cqt):
        chrom[i % 12] += e
    return chrom / (chrom.max() + 1e-10)


if __name__ == "__main__":
    # 合成一段音乐：C 大三和弦 (C4-E4-G4 = 261.63-329.63-392)
    t = np.arange(SR * 2) / SR
    x = (0.4 * np.sin(2 * np.pi * 261.63 * t)
         + 0.4 * np.sin(2 * np.pi * 329.63 * t)
         + 0.4 * np.sin(2 * np.pi * 392.00 * t))

    print("[MFCC] 提取中...")
    m = mfcc(x)
    print(f"  MFCC shape: {m.shape}")
    print(f"  前 5 帧前 5 系数：")
    print("    " + "\n    ".join(" ".join(f"{v:+6.2f}" for v in m[i, :5]) for i in range(5)))

    print("\n[Chroma] 提取...")
    c = chroma(x)
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    print("  Chroma vector:")
    for i, v in enumerate(c):
        bar = "█" * int(v * 30)
        print(f"    {note_names[i]:>2}: {v:.3f}  {bar}")

    print("\n  → C/E/G 应该最高（输入是 C 大三和弦）")

    print("\n[Spotify 推荐] 这些特征就是 Echo Nest 推荐算法的基础")
    print("              Spotify 用它们估计 Valence/Arousal → 个性化推荐")
