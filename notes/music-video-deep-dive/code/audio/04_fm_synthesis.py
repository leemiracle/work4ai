"""
04_fm_synthesis.py
==================
FM 合成（Frequency Modulation, John Chowning 1973）。

y(t) = sin(2π * fc * t + I * sin(2π * fm * t))

- fc = 载波频率（决定基础音高）
- fm = 调制器频率
- I  = 调制指数（控制泛音丰富度）
- fm/fc 决定泛音是否整数比（和谐，金属铃声/电钢琴）vs 非整数比（不和谐，钟声）

Yamaha DX7 (1983) 用 FM 统治 80s 流行音乐。

零外部依赖。
"""
import numpy as np
from scipy.io import wavfile

SR = 44100


def fm_synthesis(fc=220, fm_ratio=2.0, I=3.0, dur=2.0, sr=SR):
    """
    fc: 载波频率
    fm_ratio: fm / fc（决定频谱结构）
    I: 调制指数（控制泛音丰富度）
    """
    fm = fc * fm_ratio
    t = np.arange(int(sr * dur)) / sr

    # 让 I 随时间衰减 = 更自然的包络（模拟 DX7 的 operator envelope）
    env = np.exp(-t * 1.5)
    I_t = I * env + 0.5  # 最小保留一点亮度

    y = np.sin(2 * np.pi * fc * t + I_t * np.sin(2 * np.pi * fm * t))
    # 全局 ADSR-like 包络
    attack = int(0.01 * sr); release = int(0.3 * sr)
    amp = np.ones_like(y)
    amp[:attack] = np.linspace(0, 1, attack)
    amp[-release:] = np.linspace(1, 0, release)
    return y * amp


if __name__ == "__main__":
    # 1) 经典电钢琴（fm_ratio=2, 中等 I）
    print("[FM] 电钢琴音色 (fc=220, fm/fc=2, I=3)...")
    ep = fm_synthesis(fc=220, fm_ratio=2.0, I=3.0, dur=2.0)

    # 2) 金属铃声（fm/fc=1.41 非整数比 = 不和谐，铜钟）
    print("[FM] 金属铃声 (fm/fc=√2, I=5)...")
    bell = fm_synthesis(fc=440, fm_ratio=1.414, I=5.0, dur=3.0)

    # 3) 贝斯（低 fc，高 I，fm/fc=1）
    print("[FM] 合成贝斯 (fc=55, fm/fc=1, I=4)...")
    bass = fm_synthesis(fc=55, fm_ratio=1.0, I=4.0, dur=1.5)

    # 4) 简短旋律：C-E-G-C
    print("[FM] 旋律 C4-E4-G4-C5...")
    melody = np.concatenate([
        fm_synthesis(fc=261.63, fm_ratio=2.0, I=2.5, dur=0.4),
        fm_synthesis(fc=329.63, fm_ratio=2.0, I=2.5, dur=0.4),
        fm_synthesis(fc=392.00, fm_ratio=2.0, I=2.5, dur=0.4),
        fm_synthesis(fc=523.25, fm_ratio=2.0, I=2.5, dur=0.8),
    ])

    def save(name, x):
        x16 = np.int16(x / np.max(np.abs(x)) * 32767)
        wavfile.write(name, SR, x16)
        print(f"  saved {name}")

    save("fm_ep.wav", ep)
    save("fm_bell.wav", bell)
    save("fm_bass.wav", bass)
    save("fm_melody.wav", melody)

    print("\n原理回顾：")
    print("  y(t) = sin(2π·fc·t + I·sin(2π·fm·t))")
    print("  展开后泛音出现在 fc ± k·fm（k=0,1,2,...）")
    print("  - fm/fc = 整数比 → 泛音都是 fc 的倍数 → 和谐（电钢琴）")
    print("  - fm/fc = 非整数比 → 泛音非整数倍 → 不和谐（钟声/铜管）")
    print("  - I 大 → 泛音多 → 更明亮/金属")
