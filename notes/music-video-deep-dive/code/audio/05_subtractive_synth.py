"""
05_subtractive_synth.py
=======================
减法合成（Subtractive Synthesis）= Moog 合成器的工作方式。

思路：用丰富谐波的振荡器（锯齿/方波）→ 用滤波器（低通）削掉高频 → ADSR 包络塑形。
所有 1970s 合成器（Moog, Prophet）的核心。

ADSR = Attack(起音) - Decay(下降) - Sustain(保持) - Release(释放)
"""
import numpy as np
from scipy.io import wavfile
from scipy import signal as sg

SR = 44100


def sawtooth(freq, dur, sr=SR):
    """锯齿波：含所有整数泛音（振幅 1/k 衰减）"""
    t = np.arange(int(dur * sr)) / sr
    return 2 * (t * freq - np.floor(0.5 + t * freq))


def square(freq, dur, sr=SR):
    """方波：只含奇数次泛音"""
    return np.sign(np.sin(2 * np.pi * freq * t := np.arange(int(dur * sr)) / sr))


def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2, sr=SR):
    """ADSR 包络。a/d/r 单位秒，s 是 0-1 的保持电平"""
    n = int(dur * sr)
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    ns = n - na - nd - nr
    if ns < 0: ns = 0
    env = np.concatenate([
        np.linspace(0, 1, na) if na else np.array([]),
        np.linspace(1, s, nd) if nd else np.array([]),
        np.full(ns, s),
        np.linspace(s, 0, nr) if nr else np.array([]),
    ])
    if len(env) < n:
        env = np.concatenate([env, np.zeros(n - len(env))])
    return env[:n]


def lowpass(x, cutoff_hz, sr=SR, order=4):
    """巴特沃斯低通（模拟 Moog 滤波器）"""
    b, a = sg.butter(order, cutoff_hz / (sr / 2), btype='low')
    return sg.lfilter(b, a, x)


def moog_like_bass(freq=55, dur=1.5, cutoff=400):
    """经典 Moog 贝斯：锯齿 → 低通 → ADSR"""
    raw = sawtooth(freq, dur)
    filtered = lowpass(raw, cutoff)
    env = adsr(dur, a=0.005, d=0.15, s=0.6, r=0.3)
    return filtered * env


def filter_sweep_lead(freq=440, dur=2.0):
    """滤波器扫频 lead（cutoff 随时间从低到高）"""
    t = np.arange(int(dur * SR)) / SR
    raw = sawtooth(freq, dur)
    # 时变截止：50Hz → 5000Hz 指数上升
    cutoffs = 50 * (5000 / 50) ** (t / dur)
    # 简化：分段滤波（每 50ms 一段）
    out = np.zeros_like(raw)
    hop = int(0.05 * SR)
    for i in range(0, len(raw), hop):
        c = cutoffs[min(i, len(cutoffs) - 1)]
        seg = raw[i:i + hop]
        out[i:i + hop] = lowpass(seg, c)[:len(seg)]
    env = adsr(dur, a=0.02, d=0.3, s=0.7, r=0.4)
    return out * env


if __name__ == "__main__":
    print("[Subtractive] Moog 风贝斯...")
    bass = moog_like_bass(55, 1.5)
    print("[Subtractive] 滤波器扫频 lead...")
    lead = filter_sweep_lead(440, 2.0)
    print("[Subtractive] 大三和弦 pad...")
    pad = sum(moog_like_bass(f, 2.0, cutoff=1200) for f in [220, 277.18, 329.63]) / 3

    def save(name, x):
        x16 = np.int16(x / np.max(np.abs(x)) * 32767)
        wavfile.write(name, SR, x16)
        print(f"  saved {name}")

    save("sub_bass.wav", bass)
    save("sub_lead.wav", lead)
    save("sub_pad.wav", pad)

    print("\n原理回顾：")
    print("  锯齿波 = 所有整数泛音 (振幅 ∝ 1/k)")
    print("  → 低通滤波器削高频 = '减法'")
    print("  → ADSR 包络塑形时间")
    print("  → 这就是 1970s 模拟合成器（Moog/Prophet）的全部秘密")
