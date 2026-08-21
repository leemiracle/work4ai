#!/usr/bin/env python3
"""
讲透NLP · Ch16 语音合成 TTS — 配套实验: 共振峰(formant)合成器
对应文档: 16-语音合成-TTS.md

★ 反直觉发现: 只需要 3 个共振峰频率 + 1 个声源(脉冲串),
  就能合成出可辨别的元音——这就是语音产生的 source-filter 模型的铁证。

四个部分:
  Part 1: 声源 — 声门脉冲串 (f0 = 120 Hz)
  Part 2: 滤波器 — 2-pole 共振峰滤波器 (Klatt 形式)
  Part 3: ★ 合成三个元音 /a/ /i/ /u/, 频谱可视化, 存 wav
  Part 4: ★ 反直觉发现 — 从 1961 到 2026, 本质不变

纯 NumPy + stdlib wave, 无外部依赖, 几秒内跑完.
跑法: python3 -u experiments/16_formant_tts.py
"""

import numpy as np
import wave
import os

# ============================================================
#  全局参数
# ============================================================

SR = 16000          # 采样率 16 kHz
DURATION = 0.3      # 每个元音 0.3 秒 = 4800 samples
F0 = 120            # 基频 120 Hz (男性音高)

# 元音的共振峰参数 (频率Hz, 带宽Hz)
# 数据来源: Klatt (1980) "Software for a cascade/parallel formant synthesizer"
# 及 Fant (1973) 经典测量值
VOWELS = {
    '/a/': {
        'name':    'ah  (如英语 "father", 汉语 "啊")',
        'formants': [(730, 60), (1090, 100), (2440, 150)],
    },
    '/i/': {
        'name':    'ee  (如英语 "heed",   汉语 "衣")',
        'formants': [(270, 50), (2290, 120), (3010, 200)],
    },
    '/u/': {
        'name':    'oo  (如英语 "who",    汉语 "乌")',
        'formants': [(300, 60), (870, 100), (2240, 150)],
    },
}


def P(*a, **kw):
    """强制 flush 的 print, 防止输出缓冲。"""
    print(*a, **kw, flush=True)


# ============================================================
#  Part 1: 声源 — 声门脉冲串 (glottal pulse train)
# ============================================================

def impulse_train(f0, duration, sr):
    """
    生成频率 f0 的脉冲串 — 模拟声带周期性振动。

    浊音(voiced sound)的声源就是声带的周期性开合:
      每 1/f0 秒声带打开一次 → 一个脉冲 → 脉冲串
    f0 = 120 Hz → 每 8.3ms 一个脉冲
    """
    n = int(duration * sr)
    period = max(1, int(round(sr / f0)))
    src = np.zeros(n, dtype=np.float64)
    src[::period] = 1.0
    return src


# ============================================================
#  Part 2: 滤波器 — 2-pole 共振峰谐振器 (Klatt formant filter)
# ============================================================

def formant_filter(x, freq, bw, sr):
    """
    2-pole IIR 谐振器 — 模拟声道在 freq 处的共振。

    这是 Klatt (1980) formant 合成器的核心构件。
    声道被建模为一个级联的 2-pole 谐振器系统。

    传递函数:
      H(z) = A / (1 - B·z⁻¹ - C·z⁻²)

    极点在 z 平面的单位圆内 (R = e^{-π·bw/sr}):
      z = R · e^{±j·2π·freq/sr}

    系数:
      R = exp(-π · bw / sr)          极点半径 (带宽 bw 越大, 衰减越快)
      θ = 2π · freq / sr             极点角度 (freq 决定谐振频率)
      B = 2 · R · cos(θ)
      C = -R²
      A = 1 - B - C                  DC 归一化 (直流增益=1)
    """
    R = np.exp(-np.pi * bw / sr)
    theta = 2 * np.pi * freq / sr
    Bc = 2.0 * R * np.cos(theta)     # 分母 z⁻¹ 系数
    Cc = -(R * R)                    # 分母 z⁻² 系数
    A = 1.0 - Bc - Cc                # 分子 (DC 归一化)

    n = len(x)
    y = np.zeros(n, dtype=np.float64)
    # 递归 IIR: y[n] = A·x[n] + Bc·y[n-1] + Cc·y[n-2]
    y[0] = A * x[0]
    if n > 1:
        y[1] = A * x[1] + Bc * y[0]
    for i in range(2, n):
        y[i] = A * x[i] + Bc * y[i - 1] + Cc * y[i - 2]
    return y


def synthesize_vowel(formants, f0, duration, sr):
    """
    级联(cascade)共振峰合成:
      脉冲源 → F1 谐振器 → F2 谐振器 → F3 谐振器 → 输出

    级联的含义: 前一个滤波器的输出是后一个的输入,
    总传递函数 = H_F1(z) × H_F2(z) × H_F3(z)
    """
    sig = impulse_train(f0, duration, sr)
    for freq, bw in formants:
        sig = formant_filter(sig, freq, bw, sr)
    # 归一化到 [-0.8, 0.8] (留余量防 clipping)
    peak = np.max(np.abs(sig))
    if peak > 1e-12:
        sig = sig / peak * 0.8
    return sig


# ============================================================
#  频谱可视化 (ASCII 频谱包络)
# ============================================================

def show_spectrum(signal, sr, formant_freqs, title, n_bands=28, f_max=4000):
    """
    计算幅度谱, 聚合成 n_bands 个频带, 用 ASCII 柱状图显示。
    在共振峰频率附近标注 F1/F2/F3。
    """
    spectrum = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(len(signal), 1 / sr)

    # 聚合到频带 (取每带最大值 → 看到包络而非谐波细节)
    band_edges = np.linspace(0, f_max, n_bands + 1)
    band_width = band_edges[1] - band_edges[0]
    band_amps = []
    band_centers = []
    for i in range(n_bands):
        lo, hi = band_edges[i], band_edges[i + 1]
        mask = (freqs >= lo) & (freqs < hi)
        amp = np.max(spectrum[mask]) if np.any(mask) else 0.0
        band_amps.append(amp)
        band_centers.append((lo + hi) / 2)

    max_amp = max(band_amps) + 1e-12

    P(f"\n  ┌── 频谱包络 (0–{f_max} Hz) ── {title}")
    P("  │   (柱高 = 能量, █ 越多 = 越强)")
    P("  │")
    for i in range(n_bands):
        center = band_centers[i]
        bar_len = int(band_amps[i] / max_amp * 32)
        bar = "█" * bar_len + "░" * (32 - bar_len)
        # 标注共振峰
        marker = ""
        for j, ff in enumerate(formant_freqs):
            if abs(center - ff) < band_width * 0.7:
                marker = f"  ← F{j+1}={ff}Hz"
        P(f"  │ {center:5.0f} │{bar}│{marker}")
    P("  └──")


# ============================================================
#  WAV 保存 (stdlib wave, 16-bit PCM)
# ============================================================

def save_wav(filepath, signal, sr):
    """把 float64 数组保存为 16-bit PCM WAV (单声道)。"""
    signal_int16 = (signal * 32767).astype('<i2')
    with wave.open(filepath, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)           # 16-bit = 2 bytes
        w.setframerate(sr)
        w.writeframes(signal_int16.tobytes())
    return os.path.getsize(filepath)


# ============================================================
#  主程序
# ============================================================

P("=" * 72)
P("讲透NLP · Ch16 TTS — 共振峰(formant)合成器")
P("=" * 72)

P(f"""
  语音产生的 source-filter 模型 (Fant, 1960):

    声音 = 声源(声带振动) × 声道(共振)

    声源 = 脉冲串, 频率 = f0 (基频) → 决定音高
    声道 = 共振峰滤波器 F1, F2, F3 → 决定元音音色

  ★ 反直觉: 你以为要精确模拟整个声道才能合成语音?
            事实: 只需 3 个共振峰 + 1 个脉冲源 = 可辨别的元音!

  参数:
    采样率 = {SR} Hz
    基频 f0 = {F0} Hz (男性音高)
    时长   = {DURATION}s ({int(DURATION * SR)} samples/元音)
""")

# ────────────────────────────────────────────────────────────
#  Part 1: 声源
# ────────────────────────────────────────────────────────────
P("─" * 72)
P("Part 1: 声源 — 声门脉冲串")
P("─" * 72)

src = impulse_train(F0, DURATION, SR)
period = int(round(SR / F0))
n_pulses = int(DURATION * F0)

P(f"""
  声带每 1/f0 = {1/F0*1000:.1f}ms 振动一次 → 每 {period} 个采样一个脉冲
  共 {n_pulses} 个脉冲

  这个脉冲串听起来是"嗡嗡"的蜂鸣声 — 不像任何元音!
  因为它没有经过声道滤波。

  想象: 你只振动声带但完全不张嘴 — 就是这个声音。
""")

# 看看脉冲串的频谱: 应该是在 f0 整数倍处的等高谐波
show_spectrum(src, SR, [], "脉冲源 (未滤波)")

P("""
  ↑ 注意: 谐波在 120, 240, 360, ... Hz 处, 几乎等高。
    声道的任务就是把这些谐波"塑形"成不同元音。
""")

# ────────────────────────────────────────────────────────────
#  Part 2: 滤波器
# ────────────────────────────────────────────────────────────
P("\n" + "─" * 72)
P("Part 2: 滤波器 — 2-pole 共振峰谐振器 (Klatt formant filter)")
P("─" * 72)

P("""
  每个共振峰 = 一个 2-pole IIR 谐振器:

     H(z) = A / (1 - B·z⁻¹ - C·z⁻²)

  极点位置 (z平面):
     z = R · e^{±jθ}
     R = exp(-π·bw/sr)    ← 半径, bw 越大越靠圆心(共振越宽)
     θ = 2π·freq/sr       ← 角度, freq 决定谐振频率

  级联 3 个 → 声道传递函数:
     V(z) = H_F1(z) · H_F2(z) · H_F3(z)

  这就是 source-filter 模型的"filter"部分。
""")

# ────────────────────────────────────────────────────────────
#  Part 3: ★ 合成三个元音
# ────────────────────────────────────────────────────────────
P("─" * 72)
P("Part 3: ★ 合成三个元音 — 3 共振峰 + 1 声源")
P("─" * 72)

output_dir = os.path.dirname(os.path.abspath(__file__))
vowel_signals = []

for symbol, info in VOWELS.items():
    formants = info['formants']
    P(f"\n{'─'*40}")
    P(f"  {symbol}  {info['name']}")
    P(f"{'─'*40}")
    for j, (freq, bw) in enumerate(formants):
        P(f"    F{j+1} = {freq:>5} Hz  (带宽 {bw} Hz)")

    sig = synthesize_vowel(formants, F0, DURATION, SR)
    vowel_signals.append(sig)

    # 频谱可视化
    f_list = [f[0] for f in formants]
    show_spectrum(sig, SR, f_list, symbol)

    # 保存
    fname = os.path.join(output_dir, f"vowel_{symbol.strip('/')}.wav")
    fsize = save_wav(fname, sig, SR)
    P(f"\n    ✅ 已保存: {os.path.basename(fname)} ({fsize/1024:.1f} KB)")

# 三个元音拼接 (中间加静音)
P(f"\n{'─'*40}")
P("  拼接三个元音 → vowels_all.wav")
P(f"{'─'*40}")
silence = np.zeros(int(SR * 0.1))
full_audio = np.concatenate([
    vowel_signals[0], silence,
    vowel_signals[1], silence,
    vowel_signals[2],
])
fname_all = os.path.join(output_dir, "vowels_all.wav")
fsize = save_wav(fname_all, full_audio, SR)
P(f"  ✅ 已保存: vowels_all.wav ({fsize/1024:.1f} KB)")
P(f"     (顺序: /a/ → /i/ → /u/, 各 {DURATION}s + 0.1s 静音)")

# ────────────────────────────────────────────────────────────
#  Part 4: ★ 反直觉发现
# ────────────────────────────────────────────────────────────
P("\n" + "─" * 72)
P("Part 4: ★ 反直觉发现 — 3 个数字 = 3 种元音")
P("─" * 72)

P("""
  传统直觉:
    "计算机要像人一样说话, 需要精确模拟整个声道——
     舌头位置、嘴唇圆展、鼻腔耦合、声带质量……太多了!"

  实际真相 (source-filter 理论, Fant 1960):
    语音 = 激励(声源) × 传递函数(声道)

    → 声道传递函数可以用少数 2-pole 谐振器近似
    → 每个谐振器只需 2 个参数 (频率 + 带宽)
    → 3 个共振峰 = 6 个数字 = 足以区分所有元音!

  本实验的铁证:
""")

P(f"    {'元音':<6} {'F1':>6} {'F2':>6} {'F3':>6}   {'声源':>6}   {'滤波器':>8}   {'结果':>20}")
P("    " + "─" * 64)
for symbol, info in VOWELS.items():
    f1, f2, f3 = [f[0] for f in info['formants']]
    P(f"    {symbol:<6} {f1:>5}Hz {f2:>5}Hz {f3:>5}Hz   {F0}Hz脉冲   3×谐振器   → 可辨别的{info['name'][:2]}声")

P("""
  总计生成元音所需的信息:
    声源:   1 个数字 (f0 = 基频)
    滤波器: 6 个数字 (3×(频率, 带宽))
    合计:   7 个数字 → 一个可辨别的元音!

  这就是为什么:
    ① 1961 年 Bell Labs 用模拟电路就做出了 formant 合成器
    ② Klatt (1980) 的数字 formant 合成器统治 TTS 二十年
    ③ 现代 ASR 的 MFCC 特征 = 只保留频谱包络 (= 共振峰信息)
    ④ 现代 TTS 的 mel-spectrogram = 同样只保留包络
    ⑤ VITS 的 variational latent z = 显式建模 source-filter 分离

  从 1961 到 2026, 六十年 TTS 技术演化:
""")

P("""    1961  Formant 合成器     手动调 3 共振峰     质量差但揭示模型
    1980s Diphone 拼接      录真人音素拼接       自然但机械
    2000s HMM 参数合成       统计学谱参数         灵活但闷
    2016  WaveNet           神经波形生成         ★质量飞跃
    2017  Tacotron 2        端到端声学模型       ★接近真人
    2019  FastSpeech 2      非自回归+可控        ★快 270×
    2020  HiFi-GAN          GAN 声码器           ★实时高质量
    2021  VITS              端到端单模型         ★无误差累积
    2023  VALL-E            TTS=条件语言建模     ★3秒克隆人声

    本质未变: 都在做 "文本 → 声学特征(≈共振峰) → 波形"
              只是从 "手动调参" 变成 "端到端学习"
""")

# ────────────────────────────────────────────────────────────
#  总结
# ────────────────────────────────────────────────────────────
P("=" * 72)
P("一句话总结")
P("=" * 72)
P("""
  source-filter 模型: s(t) = e(t) * v(t)
    e(t) = 声源(脉冲串)   → 决定音高 (f0)
    v(t) = 声道(共振峰)   → 决定元音 (F1, F2, F3)

  ★ 反直觉: 3 个共振峰 + 1 个脉冲 = 可辨别的元音
    → TTS 六十年技术演化的本质都是在学这个分解
    → 从手动调参(1961) 到 端到端学习(2021) 到 语言建模(2023)

  📂 生成的音频文件 (用播放器打开验证):
     vowel_a.wav  — 低沉开阔的 "啊"
     vowel_i.wav  — 尖锐明亮的 "衣"
     vowel_u.wav  — 圆润低沉的 "呜"
     vowels_all.wav — 三个元音连放

  🔬 延伸练习 (见 16-语音合成-TTS.md 练习 16.2):
     把 F0 从 120 改成 220 → 听到音高变高, 但元音不变
     → 铁证: f0 和 formants 是独立的
""")
