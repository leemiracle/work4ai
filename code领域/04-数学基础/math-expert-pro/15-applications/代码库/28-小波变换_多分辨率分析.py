"""小波变换：多分辨率分析与信号处理
================================
数学概念：小波变换 / Haar小波 / 多分辨率分析(MRA) / 离散小波变换(DWT) / 时频分析
应用领域：JPEG2000 / 信号去噪 / 边缘检测 / 地震分析 / 医学影像
核心思想：小波 = 局部化的"波形"，同时提供时间+频率信息。
  Haar小波：最简单的小波，平均值+差值分解
  DWT：金字塔算法，逐级分解为低频(近似)+高频(细节)
  MRA：信号 = 不同尺度的叠加（像缩放地图）
  优势 vs FFT：FFT只有频率信息，小波同时有时间+频率（时频分析）
运行方式：python "28-小波变换_多分辨率分析.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def haar_dwt_1d(signal):
    """一维 Haar 离散小波变换（一级分解）。
    将信号分解为：低频(近似系数) + 高频(细节系数)
    """
    n = len(signal)
    if n % 2 != 0:
        signal = np.append(signal, signal[-1]); n += 1
    # 低频：相邻对的平均值
    approx = (signal[0::2] + signal[1::2]) / np.sqrt(2)
    # 高频：相邻对的差值
    detail = (signal[0::2] - signal[1::2]) / np.sqrt(2)
    return approx, detail

def haar_idwt_1d(approx, detail):
    """一维 Haar 逆变换（重建）。"""
    n = len(approx)
    signal = np.zeros(2 * n)
    signal[0::2] = (approx + detail) / np.sqrt(2)
    signal[1::2] = (approx - detail) / np.sqrt(2)
    return signal

def haar_dwt_multilevel(signal, levels):
    """多级 Haar DWT（金字塔算法）。
    每级对低频部分继续分解。
    """
    coeffs = []
    current = signal.copy()
    for _ in range(levels):
        if len(current) < 2: break
        approx, detail = haar_dwt_1d(current)
        coeffs.append(detail)  # 存高频
        current = approx       # 继续分解低频
    coeffs.append(current)     # 最后的最低频
    coeffs.reverse()           # 从低到高排列
    return coeffs

def haar_reconstruct(coeffs):
    """从多级系数重建信号。"""
    current = coeffs[0]
    for i in range(1, len(coeffs)):
        current = haar_idwt_1d(current, coeffs[i])
    return current

def hard_threshold_denoise(signal, levels, threshold):
    """硬阈值去噪：小波系数小于阈值的置零。"""
    coeffs = haar_dwt_multilevel(signal, levels)
    denoised_coeffs = [coeffs[0]]  # 最低频不动
    for i in range(1, len(coeffs)):
        c = coeffs[i].copy()
        c[np.abs(c) < threshold] = 0  # 硬阈值
        denoised_coeffs.append(c)
    return haar_reconstruct(denoised_coeffs)

def main():
    np.random.seed(42)
    # 构造测试信号（低频正弦 + 高频脉冲 + 噪声）
    N = 256
    t = np.linspace(0, 1, N)
    signal_clean = np.sin(2 * np.pi * 5 * t)  # 5Hz 正弦
    signal_clean[N//3:N//3+10] += 2.0  # 局部脉冲（突变）
    noise = np.random.randn(N) * 0.5
    signal_noisy = signal_clean + noise

    print("="*60); print("实验 1：Haar 小波分解——信号的多分辨率表示"); print("="*60)
    levels = 4
    coeffs = haar_dwt_multilevel(signal_noisy, levels)
    print(f"信号长度: {N}, 分解级数: {levels}")
    print(f"系数结构: {' → '.join(f'c{len(coeffs)-1-i}({len(c)})' for i, c in enumerate(coeffs))}")
    print(f"总系数: {sum(len(c) for c in coeffs)} = {N}（完美重构）")

    # 验证重构
    reconstructed = haar_reconstruct(coeffs)
    recon_error = np.max(np.abs(reconstructed[:N] - signal_noisy))
    print(f"重构误差: {recon_error:.2e} {'✓' if recon_error < 1e-10 else '✗'}")

    print("\n"+"="*60); print("实验 2：时频分析——小波 vs FFT"); print("="*60)
    print("FFT：只有频率信息（不知道脉冲何时发生）")
    print("小波：同时有时间+尺度(频率)信息（能定位脉冲）")
    # FFT 频谱
    fft_spectrum = np.abs(np.fft.fft(signal_clean))[:N//2]
    peak_freq = np.argmax(fft_spectrum) 
    print(f"\nFFT 主峰频率: {peak_freq} Hz（= 信号的真实 5Hz）")
    print(f"FFT 无法定位脉冲的时间位置")
    # 小波在不同尺度上的能量
    print(f"\n小波逐级能量（细节系数）：")
    for i in range(1, len(coeffs)):
        energy = np.sum(coeffs[i]**2)
        max_pos = np.argmax(np.abs(coeffs[i]))
        print(f"  级别{len(coeffs)-1-i}: 能量={energy:.1f}, 峰值位置={max_pos}/{len(coeffs[i])} (N/{2**(len(coeffs)-1-i)}附近)")

    print("\n"+"="*60); print("实验 3：小波去噪——优于传统低通滤波"); print("="*60)
    denoised = hard_threshold_denoise(signal_noisy, levels, threshold=0.8)
    noise_before = np.std(signal_noisy - signal_clean)
    noise_after = np.std(denoised[:N] - signal_clean)
    snr_before = 10 * np.log10(np.var(signal_clean) / np.var(signal_noisy - signal_clean))
    snr_after = 10 * np.log10(np.var(signal_clean) / np.var(denoised[:N] - signal_clean + 1e-20))
    print(f"原始信噪比: {snr_before:.2f} dB")
    print(f"去噪后信噪比: {snr_after:.2f} dB")
    print(f"改善: {snr_after - snr_before:.2f} dB")
    print(f"\n[解读] 小波去噪保留局部脉冲（高频细节），")
    print(f"       而低通滤波会模糊脉冲——小波的时频定位优势。")

    print("\n"+"="*60); print("实验 4：小波应用全景"); print("="*60)
    apps = [("JPEG2000", "小波压缩优于DCT（JPEG）"),
            ("FBI指纹库", "WSQ小波压缩"),
            ("地震分析", "分辨不同深度的反射波"),
            ("医学EEG/ECG", "去除基线漂移+保留诊断信号"),
            ("机器学习", "小波散射网络=不变特征"),
            ("5G信道", "FBMC多载波调制")]
    for app, desc in apps: print(f"  {app:<16} → {desc}")

    # 可视化
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    ax = axes[0,0]; ax.plot(t, signal_clean, 'b-', lw=2); ax.set_title('原始信号（正弦+局部脉冲）'); ax.grid(alpha=0.3)
    ax = axes[0,1]; ax.plot(t, signal_noisy, 'r-', lw=0.5, alpha=0.7); ax.set_title(f'带噪信号（SNR={snr_before:.1f}dB）'); ax.grid(alpha=0.3)
    # 多级分解
    ax = axes[1,0]
    for i, c in enumerate(coeffs):
        offset = -i * 2
        level = len(coeffs) - 1 - i
        label = f'c{level}({"低频" if i==0 else "高频"})'
        ax.plot(np.linspace(0, 1, len(c)), c + offset, lw=1, label=label)
    ax.set_title(f'Haar DWT {levels}级分解（多分辨率）'); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    # 去噪对比
    ax = axes[1,1]; ax.plot(t, signal_clean, 'b-', lw=2, label='原始'); ax.plot(t, denoised[:N], 'g-', lw=1.5, alpha=0.7, label=f'去噪(SNR={snr_after:.1f}dB)'); ax.set_title('小波去噪'); ax.legend(); ax.grid(alpha=0.3)
    # FFT 频谱
    ax = axes[2,0]; freqs = np.fft.fftfreq(N, 1/N)[:N//2]; ax.plot(freqs[:30], fft_spectrum[:30], 'r-', lw=2); ax.set_xlabel('频率 Hz'); ax.set_title('FFT 频谱（只有频率，无时间定位）'); ax.grid(alpha=0.3)
    # 小波系数热力图
    ax = axes[2,1]
    max_len = max(len(c) for c in coeffs[1:])
    heat = np.zeros((len(coeffs)-1, max_len))
    for i in range(1, len(coeffs)):
        heat[i-1, :len(coeffs[i])] = np.abs(coeffs[i])
    ax.imshow(heat, aspect='auto', cmap='hot', interpolation='nearest')
    ax.set_xlabel('位置'); ax.set_ylabel('分解级别')
    ax.set_title('小波系数热力图（时频定位）')
    plt.tight_layout(); plt.savefig("28-小波变换_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 28-小波变换_结果.png")
    print("\n[总结] 1. 小波=时频分析工具(同时有时间+频率信息)")
    print("2. Haar小波: 最简单(平均+差值), 多级分解=金字塔算法")
    print("3. 去噪: 硬阈值保留信号, 去除噪声(SNR改善)")
    print("4. 应用: JPEG2000/FBI指纹/EEG/ML散射网络/5G")

if __name__ == "__main__": main()
