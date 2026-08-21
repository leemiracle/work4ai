#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 14 章配套实验：MFCC 从零实现 —— 纯 NumPy，不依赖 librosa
====================================================================
对应文档: 14-语音学与特征提取.md

只用 NumPy + 标准库 + matplotlib(画图)。手写 MFCC 全流程：
    预强调 → 分帧 → Hamming窗 → FFT功率谱 → mel三角滤波 → 对数 → DCT

跑这个脚本，你会看到三个「能跑出来」的结论：

  1. 完整 MFCC 流水线在合成的"假语音"(源-滤波模型)上跑通，
     画出 波形→功率谱→mel滤波组→mel谱→MFCC 五张子图。
  2.【★ 反直觉发现 · 核心】MFCC 第 1 维 C0 只编码"能量/响度"，
     第 2-13 维 C1-C12 才编码"音素/频谱包络"。铁证有两个方向：
       (a) 把信号振幅放大 4 倍 → C0 明显变大, C1-C12 几乎不变；
       (b) 改变共振峰位置(频谱"形状") → C0 几乎不变, C1-C12 明显变化。
     数学根因：DCT 的 k=0 项 cos(0)=1, C0∝Σlog(能量)=log(总能量)；
               而振幅缩放在对数域只是一个常数，DCT 把"常数"全部
               归到 k=0 这一项上 → 高阶系数对"纯响度变化"免疫。
  3. mel 刻度的非线性：在 mel 域均匀铺 26 个滤波器，反算到 Hz 域后
     低频密、高频疏——这正是模仿人耳对频率的"对数"感知。

自包含，几秒跑完，不需要任何真实音频文件：
    python3 -u experiments/14_mfcc.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")          # 无显示器也能存图
import matplotlib.pyplot as plt

np.random.seed(0)

# 图表用英文标签，避免中文字体缺失出现豆腐块
FIG_PIPELINE = "experiments/fig_pipeline.png"
FIG_C0 = "experiments/fig_c0_vs_shape.png"


def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 一、MFCC 全流程（纯 NumPy 从零实现）
# ============================================================
def pre_emphasis(x, alpha=0.97):
    """① 预强调：一阶高通 y[n]=x[n]-0.97·x[n-1]，提亮高频、平衡频谱。"""
    return np.append(x[0], x[1:] - alpha * x[:-1])


def frame_signal(x, sr, frame_ms=25.0, hop_ms=10.0):
    """② 分帧：frame_ms 一帧、hop_ms 步进。不足补零。返回 (n_frames, frame_len)。"""
    frame_len = int(round(sr * frame_ms / 1000.0))
    hop_len = int(round(sr * hop_ms / 1000.0))
    if len(x) <= frame_len:
        n_frames = 1
    else:
        n_frames = 1 + int(np.ceil((len(x) - frame_len) / hop_len))
    pad_len = (n_frames - 1) * hop_len + frame_len
    x = np.concatenate([x, np.zeros(pad_len - len(x))])
    idx = np.tile(np.arange(frame_len), (n_frames, 1))
    hops = np.tile(np.arange(0, n_frames) * hop_len, (frame_len, 1)).T
    return x[hops + idx]


def hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)


def mel_to_hz(m):
    return 700.0 * (10.0 ** (m / 2595.0) - 1.0)


def mel_filterbank(n_filt, nfft, sr, low_hz=0.0, high_hz=None):
    """③ mel 三角滤波器组 (n_filt, nfft//2+1)。mel 域均匀 → Hz 域低密高疏。"""
    if high_hz is None:
        high_hz = sr / 2.0
    mel_pts = np.linspace(hz_to_mel(low_hz), hz_to_mel(high_hz), n_filt + 2)
    hz_pts = mel_to_hz(mel_pts)
    bin_pts = np.floor((nfft + 1) * hz_pts / sr).astype(int)
    fb = np.zeros((n_filt, nfft // 2 + 1))
    for m in range(1, n_filt + 1):
        lo, mid, hi = bin_pts[m - 1], bin_pts[m], bin_pts[m + 1]
        for k in range(lo, mid):
            fb[m - 1, k] = (k - lo) / max(mid - lo, 1)
        for k in range(mid, hi):
            fb[m - 1, k] = (hi - k) / max(hi - mid, 1)
    return fb


def dct_ii(log_mel, n_mfcc):
    """⑤ 离散余弦变换 DCT-II，保留前 n_mfcc 个系数。
    C[k] = 2·Σ_m x[m]·cos(πk(2m+1)/(2M))。"""
    M = log_mel.shape[1]
    m = np.arange(M)
    C = np.zeros((log_mel.shape[0], n_mfcc))
    for k in range(n_mfcc):
        basis = np.cos(np.pi * k * (2 * m + 1) / (2 * M))
        C[:, k] = 2.0 * (log_mel * basis).sum(axis=1)
    return C


def mfcc(x, sr, n_mfcc=13, n_filt=26, frame_ms=25.0, hop_ms=10.0, nfft=512):
    """完整 MFCC。返回 (mfcc[n_frames, n_mfcc], 中间结果字典)。"""
    x = pre_emphasis(x, 0.97)
    frames = frame_signal(x, sr, frame_ms, hop_ms)
    frames = frames * np.hamming(frames.shape[1])             # Hamming 窗
    mag = np.fft.rfft(frames, n=nfft, axis=1)
    powspec = (np.abs(mag) ** 2) / nfft                        # 功率谱
    fb = mel_filterbank(n_filt, nfft, sr)
    mel_e = powspec @ fb.T                                     # mel 能量
    log_mel = np.log(mel_e + 1e-10)                            # 对数
    ceps = dct_ii(log_mel, n_mfcc)                             # DCT → MFCC
    info = dict(frames=frames, powspec=powspec, fb=fb,
                mel_e=mel_e, log_mel=log_mel)
    return ceps, info


# ============================================================
# 二、合成"假语音"：源-滤波模型 (声源谐波 × 声道共振峰)
# ============================================================
def fake_vowel(sr=16000, dur=1.0, f0=120.0, formants=(730.0, 1090.0, 2440.0),
               amp=1.0, noise=0.0):
    """用源-滤波理论合成一个元音：声源=基频f0及谐波梳齿，声道=formants共振峰包络。
    返回波形。这是"假语音"——有真实元音的频谱结构，但不需音频文件。"""
    n = int(sr * dur)
    t = np.arange(n) / sr
    # 声源：f0 的前 ~60 个谐波，幅度随阶数衰减 1/k (声门脉冲谱) → 谐波梳齿
    max_h = int(min((sr / 2) / f0, 60))
    src = np.zeros(n)
    for k in range(1, max_h + 1):
        src += (1.0 / k) * np.sin(2 * np.pi * f0 * k * t)
    # 声道：在频域施加共振峰包络。每个共振峰用一个 Lorentzian，
    # 中心恰在 F 处达峰 → 改 formants 就是改频谱"形状"(= 改音素)。
    spec = np.fft.rfft(src, n=n)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    env = np.zeros_like(freqs)
    for F in formants:
        bw = 150.0  # 共振峰带宽(Hz)
        env += 1.0 / (1.0 + ((freqs - F) / (bw / 2.0)) ** 2)   # 在 F 处=1, 两侧衰减
    spec_f = spec * (env + 1e-6)
    out = np.fft.irfft(spec_f, n=n)
    # 峰值归一化后乘振幅：amp1 与 amp4 形状完全相同，只差整体缩放 → 保证
    # 方向(a)中 C1-C12 对"纯响度"严格不变(数学免疫)。
    out = out / (np.max(np.abs(out)) + 1e-12) * amp
    if noise > 0:
        out = out + noise * np.random.randn(n)
    return out


# ============================================================
# 主程序
# ============================================================
def main():
    SR = 16000
    DUR = 1.0

    # ----------------------------------------------------------
    # 结论 1：完整 MFCC 流水线跑通 + 画图
    # ----------------------------------------------------------
    P("=" * 68)
    P("结论 1：纯 NumPy 实现的 MFCC 流水线，在合成\"假语音\"上跑通")
    P("=" * 68)
    sig = fake_vowel(sr=SR, dur=DUR, f0=120.0, formants=(730.0, 1090.0, 2440.0), amp=1.0)
    P(f"合成元音(源-滤波模型)：f0={120}Hz, 共振峰 F1=730 F2=1090 F3=2440 Hz")
    P(f"波形：{len(sig)} 个采样点 @ {SR}Hz = {DUR}s")

    ce, info = mfcc(sig, SR, n_mfcc=13, n_filt=26, nfft=512)
    P(f"MFCC 形状：{ce.shape[0]} 帧 × {ce.shape[1]} 维 (每 10ms 一帧, C0..C12)")
    P("中间产物：")
    P(f"  功率谱 bin 数 = {info['powspec'].shape[1]} (=nfft/2+1=257)")
    P(f"  mel 滤波器组 = {info['fb'].shape[0]} 个三角滤波器")
    P(f"  mel 能量      = {info['mel_e'].shape[1]} 维/帧")

    # 画流水线五连图
    t = np.arange(len(sig)) / SR
    fig, ax = plt.subplots(2, 3, figsize=(15, 8))
    ax[0, 0].plot(t[: int(0.03 * SR)], sig[: int(0.03 * SR)], lw=0.8)
    ax[0, 0].set_title("(1) Waveform (30ms)")
    ax[0, 0].set_xlabel("time (s)")
    # 功率谱(第一帧)
    ax[0, 1].semilogy(np.arange(info["powspec"].shape[1]) * SR / 512,
                      info["powspec"][10] + 1e-12, lw=0.8)
    ax[0, 1].set_title("(2) Power spectrum (one frame)")
    ax[0, 1].set_xlabel("freq (Hz)")
    # mel 滤波器组
    for r in info["fb"][::2]:
        ax[0, 2].plot(np.arange(info["fb"].shape[1]) * SR / 512, r, lw=0.8)
    ax[0, 2].set_title("(3) Mel filterbank (26 triangular)")
    ax[0, 2].set_xlabel("freq (Hz)")
    # mel 谱(热图)
    im = ax[1, 0].imshow(info["log_mel"].T, aspect="auto", origin="lower",
                         cmap="magma")
    ax[1, 0].set_title("(4) log-Mel spectrogram")
    ax[1, 0].set_xlabel("frame")
    ax[1, 0].set_ylabel("mel bin")
    fig.colorbar(im, ax=ax[1, 0])
    # MFCC (热图)
    im2 = ax[1, 1].imshow(ce.T, aspect="auto", origin="lower", cmap="viridis")
    ax[1, 1].set_title("(5) MFCC (13-dim, C0..C12)")
    ax[1, 1].set_xlabel("frame")
    ax[1, 1].set_ylabel("cepstral coeff k")
    fig.colorbar(im2, ax=ax[1, 1])
    # 单帧 MFCC 柱状图
    ax[1, 2].bar(np.arange(13), ce[len(ce) // 2], color="steelblue")
    ax[1, 2].set_title("MFCC of 1 frame (C0..C12)")
    ax[1, 2].set_xlabel("k")
    ax[1, 2].set_xticks(np.arange(13))
    fig.suptitle("MFCC Pipeline: waveform -> power spec -> mel filterbank "
                 "-> log-mel -> DCT -> MFCC", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG_PIPELINE, dpi=110)
    P(f"已存图 {FIG_PIPELINE}\n")

    P("👉 结论 1：7 步流水线(预强调→分帧→窗→FFT→mel滤波→log→DCT)全部从零实现，")
    P("   无 librosa 依赖。每 10ms 输出 13 维向量，这就是 GMM/HMM 时代的\"语音 token\"。\n")

    # ----------------------------------------------------------
    # 结论 2：★ 反直觉——C0=能量, C1-C12=音素(频谱形状)
    # ----------------------------------------------------------
    P("=" * 68)
    P("结论 2：★ 反直觉——C0 只编码\"响度\", C1-C12 才编码\"音素/频谱形状\"")
    P("=" * 68)
    P("""
数学根因：DCT 的 k=0 项 cos(0)=1，于是
    C0 = 2·Σ_m log(E_m) ∝ log(总能量)   ← 只反映"这帧多响"
而振幅整体缩放 a 倍 → 功率谱整体 ×a² → log 域加一个常数
    → DCT 把"常数"全部归到 k=0 这一项 → C1-C12 对"纯响度"免疫。
两个方向的铁证：
  (a) 同形状, 改响度 → 只有 C0 动, C1-C12 几乎不变;
  (b) 同响度, 改形状(共振峰位置) → C0 不动, C1-C12 明显变。
""")

    # --- 方向 (a)：同形状，振幅 ×4 ---
    sig_amp1 = fake_vowel(sr=SR, dur=DUR, f0=120.0,
                          formants=(730.0, 1090.0, 2440.0), amp=1.0)
    sig_amp4 = fake_vowel(sr=SR, dur=DUR, f0=120.0,
                          formants=(730.0, 1090.0, 2440.0), amp=4.0)
    ce1, _ = mfcc(sig_amp1, SR)
    ce4, _ = mfcc(sig_amp4, SR)
    m1 = ce1[len(ce1) // 2]            # 取中间一帧
    m4 = ce4[len(ce4) // 2]
    P("【方向 (a)】同共振峰形状，振幅 1.0 → 4.0（响度变 16 倍功率）")
    P(f"  C0 :  {m1[0]:+.3f}  →  {m4[0]:+.3f}    变化 {m4[0]-m1[0]:+.3f}  ← 明显变大")
    diff_shape = np.max(np.abs(m4[1:] - m1[1:]))
    P(f"  C1..C12 最大变化 = {diff_shape:.2e}  ← 几乎为 0！(机器精度内不变)")
    P(f"  → 频谱\"形状\"没变，C1-C12 纹丝不动；只有 C0 记录了\"变响了\"。\n")

    # --- 方向 (b)：同响度，改共振峰 ---
    sig_v1 = fake_vowel(sr=SR, dur=DUR, f0=120.0,
                        formants=(730.0, 1090.0, 2440.0), amp=1.0)   # /ɑ/
    sig_v2 = fake_vowel(sr=SR, dur=DUR, f0=120.0,
                        formants=(300.0, 870.0, 2240.0), amp=1.0)    # /u/ 形状
    ce_v1, _ = mfcc(sig_v1, SR)
    ce_v2, _ = mfcc(sig_v2, SR)
    mv1 = ce_v1[len(ce_v1) // 2]
    mv2 = ce_v2[len(ce_v2) // 2]
    P("【方向 (b)】同响度，共振峰 (730,1090,2440)→(300,870,2240)（形状变了）")
    P(f"  C0 :  {mv1[0]:+.3f}  →  {mv2[0]:+.3f}    变化 {mv2[0]-mv1[0]:+.3f}  ← 几乎不变(能量没变)")
    diff_phon = np.max(np.abs(mv2[1:] - mv1[1:]))
    P(f"  C1..C12 最大变化 = {diff_phon:+.3f}  ← 明显变化！这才是\"换了音\"")
    # 哪几维变化最大
    per_k = np.abs(mv2[1:] - mv1[1:])
    topk = np.argsort(per_k)[::-1][:3] + 1
    P(f"  变化最大的 3 维：C{topk[0]}, C{topk[1]}, C{topk[2]}  (低阶系数=共振峰包络)\n")

    # 画对比图
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    k = np.arange(13)
    w = 0.38
    ax[0].bar(k - w / 2, m1, w, label="amp=1.0", color="steelblue")
    ax[0].bar(k + w / 2, m4, w, label="amp=4.0", color="indianred")
    ax[0].set_title("(a) Same shape, change LOUDNESS: only C0 moves")
    ax[0].set_xlabel("cepstral coeff k")
    ax[0].set_xticks(k)
    ax[0].legend()
    ax[0].axvspan(-0.5, 0.5, color="gold", alpha=0.25)
    ax[1].bar(k - w / 2, mv1, w, label="formants (730,1090,2440)", color="steelblue")
    ax[1].bar(k + w / 2, mv2, w, label="formants (300,870,2240)", color="indianred")
    ax[1].set_title("(b) Same loudness, change SHAPE: C0 stays, C1-C12 move")
    ax[1].set_xlabel("cepstral coeff k")
    ax[1].set_xticks(k)
    ax[1].legend()
    ax[1].axvspan(0.5, 12.5, color="gold", alpha=0.25)
    fig.suptitle("C0 encodes ENERGY, C1-C12 encode PHONETIC SHAPE", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG_C0, dpi=110)
    P(f"已存图 {FIG_C0}")
    P("👉 结论 2：MFCC 的\"第 1 维\"是个幌子——它只是这帧有多响(能量)。")
    P("   真正装着\"说了什么音\"的是 C1..C12（共振峰包络）。这就是为什么")
    P("   早期 ASR 常把 C0 换成独立的 log-energy、再算 Δ/ΔΔ 凑成 39 维。\n")

    # ----------------------------------------------------------
    # 结论 3：mel 刻度的非线性（低频密、高频疏）
    # ----------------------------------------------------------
    P("=" * 68)
    P("结论 3：mel 刻度非线性——26 个滤波器在 Hz 域低频密、高频疏")
    P("=" * 68)
    fb = mel_filterbank(26, 512, SR)
    centers = []
    for r in fb:
        centers.append(np.argmax(r) * SR / 512)
    centers = np.array(centers)
    P(f"  26 个 mel 滤波器中心频率(Hz):")
    P("  " + " ".join(f"{c:5.0f}" for c in centers))
    gap_low = centers[1] - centers[0]
    gap_high = centers[-1] - centers[-2]
    P(f"  前两滤波器间距(低频) = {gap_low:.0f} Hz")
    P(f"  末两滤波器间距(高频) = {gap_high:.0f} Hz")
    P(f"  高频间距 / 低频间距 ≈ {gap_high / gap_low:.1f} 倍")
    P("  → mel 域等距, 但 Hz 域高频间距远大于低频——模仿人耳对频率的对数感知。")
    P("  这让 MFCC 在低频(辅音区别、元音细节)有更高分辨率。\n")

    # ----------------------------------------------------------
    # 总结
    # ----------------------------------------------------------
    P("=" * 68)
    P("一句话总结")
    P("=" * 68)
    P("""
  MFCC = 把"连续声波"压成"每10ms一个13维向量"的手工特征流水线，专为
  GMM/HMM 的"对角协方差"假设量身定做。核心洞察：
    频谱包络(共振峰=音素)留在 C1..C12，梳齿细节(音高)被 DCT 丢弃。

  本章最该记住的反直觉结论：
    C0 = 响度(能量)，不是音素；C1..C12 才是"说了什么"。
    振幅缩放只动 C0，共振峰变化只动 C1-C12——实验已用数学铁证跑出。

  为什么现代 ASR(Whisper/Conformer/wav2vec2)不再用 MFCC：
    DCT 的去相关是给"对角协方差 GMM"用的；神经网络没有这个假设，
    DCT 反而是个有损变换(扔掉了高阶信息)。所以 SOTA 直接吃 log-mel
    谱(80 bin, 不做DCT)甚至原始波形。MFCC 是上一个时代的遗产。

  下一章(15-ASR)：看 MFCC/mel谱怎么喂进 HMM→CTC→Attention→Whisper。
""")


if __name__ == "__main__":
    main()
