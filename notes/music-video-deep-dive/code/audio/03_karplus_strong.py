"""
03_karplus_strong.py
====================
物理建模合成的经典：Karplus-Strong 拨弦算法（1983）。

算法极简但效果惊人——一个延迟线 + 一个低通反馈 = 逼真的拨弦衰减。
这是 Stanford CCRMA 数字波导（Digital Waveguide）理论的鼻祖。

原理：
    buffer[n] = 0.5 * (buffer[n] + buffer[n+1])
即每个样本 = 当前和下一个的平均 → 等效低通滤波 → 高频先衰减 → 拨弦自然音色

零外部依赖（除可选 matplotlib）。输出 wav 用 scipy.io.wavfile。
"""
import numpy as np
from scipy.io import wavfile


def karplus_strong(freq=220, dur=2.0, decay=0.99, sr=44100, strike=None):
    """
    Karplus-Strong 拨弦合成。
    :param freq: 期望音高频率
    :param dur: 输出时长（秒）
    :param decay: 整体衰减系数（每周期）
    :param strike: 初始扰动（默认 = 白噪声 = 拨弦）
    """
    N = max(int(sr / freq), 2)  # 延迟线长度 = 一个周期
    if strike is None:
        buf = np.random.uniform(-1, 1, N).astype(np.float32)  # 噪声 = 拨弦
    else:
        buf = strike.astype(np.float32).copy()

    out_len = int(dur * sr)
    out = np.zeros(out_len, dtype=np.float32)
    idx = 0
    for i in range(out_len):
        # 平均当前和下一个 → 低通；乘 decay → 整体衰减
        next_val = buf[(idx + 1) % N]
        new = decay * 0.5 * (buf[idx] + next_val)
        out[i] = buf[idx]
        buf[idx] = new
        idx = (idx + 1) % N
    return out


def chord(freqs, dur=2.5):
    """多个 Karplus-Strong 叠加 = 和弦"""
    waves = [karplus_strong(f, dur) for f in freqs]
    m = min(len(w) for w in waves)
    mix = sum(w[:m] for w in waves) / len(waves)
    return mix


if __name__ == "__main__":
    # 单音 A3 = 220 Hz
    print("[Karplus-Strong] 合成 A3 (220 Hz)...")
    a3 = karplus_strong(220, dur=2.5, decay=0.995)

    # C 大三和弦：C4-E4-G4 = 261.63-329.63-392.00
    print("[Karplus-Strong] 合成 C 大三和弦...")
    cmajor = chord([261.63, 329.63, 392.00], dur=3.0)

    # 一个简单的"琶音"
    print("[Karplus-Strong] 合成琶音...")
    arp_freqs = [261.63, 329.63, 392.00, 523.25]  # C-E-G-C
    arp = np.concatenate([karplus_strong(f, dur=0.6, decay=0.99) for f in arp_freqs])

    # 写 wav（16-bit PCM）
    def save(name, x):
        x16 = np.int16(x / np.max(np.abs(x)) * 32767)
        wavfile.write(name, 44100, x16)
        print(f"  saved {name}")

    save("karplus_a3.wav", a3)
    save("karplus_cmajor.wav", cmajor)
    save("karplus_arpeggio.wav", arp)

    print("\n原理回顾：")
    print("  buffer[n] ← 0.99 * 0.5 * (buffer[n] + buffer[n+1])")
    print("  ↑ 平均 = 低通滤波 → 高频先衰减 → 自然拨弦音色")
    print("  ↑ 延迟线长度 = 一个周期 → 决定音高")
    print("  ↑ 初始噪声 = 拨弦的'激发'（也可换成滤波后的脉冲 = 弓拉弦）")
