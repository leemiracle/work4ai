"""
06_pitch_consonance.py
======================
音乐的数学：协和 = Plomp-Levelt 粗糙度曲线。

为什么纯五度 3/2 比三全音 45/32 好听？
- Helmholtz: 两音频率差 < 临界带宽 → 基底膜激活区干涉 → 拍 → "粗糙"
- Plomp & Levelt (1965): 量化粗糙度曲线
- 倒过来 = 协和度曲线，峰值与简单整数比高度吻合

同时演示：12 平均律 vs 纯律 vs 毕达哥拉斯调律的音分差异。
"""
import numpy as np


def roughness_plomp_levelt(freq_diff_hz, b=15.0):
    """
    简化的 Plomp-Levelt 粗糙度（临界带宽 ~ 临界频率差约 15 Hz 的低频）。
    实际公式对每个频率不同，这里用简化版做演示。
    """
    return freq_diff_hz * np.exp(-freq_diff_hz / b) / b


def consonance_curve(base=440, max_ratio=2.0, n_points=2000):
    """
    扫描 [base, base*max_ratio]，计算每个频率相对 base 的"粗糙度"。
    低粗糙度 = 协和。
    """
    ratios = np.linspace(1.0, max_ratio, n_points)
    # 简化：把"频率差"映射到 bark 域，越接近越粗糙
    # 真实 PL 公式更复杂；这里用 Δf / 临界带宽 近似
    df = (ratios - 1) * base  # Hz 差
    bark_bandwidth = 24.7 * (4.37e-3 * base + 1)  # 临界带宽（Moore formula 简化）
    rough = np.array([roughness_plomp_levelt(d, bark_bandwidth / 4) for d in df])
    consonance = 1.0 - rough / rough.max()
    return ratios, consonance


def find_simple_ratios():
    """列出简单整数比及其音分值（相对于 1）"""
    print("\n简单整数比（协和度候选）:")
    print(f"{'ratio':>8} {'freq_ratio':>12} {'cents':>8}  interval")
    candidates = [
        (1, 1, "同度 unison"),
        (2, 1, "八度 octave"),
        (3, 2, "纯五度 perfect fifth"),
        (4, 3, "纯四度 perfect fourth"),
        (5, 4, "大三度 major third"),
        (6, 5, "小三度 minor third"),
        (5, 3, "大六度 major sixth"),
        (8, 5, "小六度 minor sixth"),
        (9, 8, "大全音 major second"),
        (16, 15, "小二度 minor second"),
        (45, 32, "三全音 tritone (不协和)"),
    ]
    for p, q, name in candidates:
        cents = 1200 * np.log2(p / q)
        print(f"  {p}/{q:<5d} {p/q:>10.4f}  {cents:>7.1f}   {name}")


def compare_tunings():
    """对比 12-TET / 纯律 / 毕达哥拉斯的音分"""
    # C 大调音阶：C D E F G A B C
    # 12-TET 半音 = 100 cents
    tet = [0, 200, 400, 500, 700, 900, 1100, 1200]
    # 纯律（C 大调）
    just = [0, 200, 386, 498, 702, 884, 1088, 1200]  # 9/8, 5/4, 4/3, 3/2, 5/3, 15/8
    # 毕达哥拉斯（五度相生）
    pyth = [0, 204, 408, 498, 702, 906, 1110, 1200]

    names = ["C", "D", "E", "F", "G", "A", "B", "C"]
    print("\n三种调律对比（cents，C 大调）：")
    print(f"{'note':>5} {'12-TET':>8} {'Just':>8} {'Pyth.':>8}  Just-TET  Pyth.-TET")
    for i, name in enumerate(names):
        print(f"  {name:>3} {tet[i]:>7} {just[i]:>7} {pyth[i]:>7}   {just[i]-tet[i]:>+5.0f}     {pyth[i]-tet[i]:>+5.0f}")


if __name__ == "__main__":
    ratios, cons = consonance_curve(440)
    # 找协和峰
    peaks = []
    for i in range(2, len(cons) - 2):
        if cons[i] > cons[i - 1] and cons[i] > cons[i + 1] and cons[i] > 0.5:
            peaks.append((ratios[i], cons[i]))
    print("[Plomp-Levelt] 440Hz 之上的协和峰（频率比）:")
    for r, c in peaks[:8]:
        print(f"  ratio={r:.4f}  consonance={c:.3f}")
    print("  （应该接近 2/1, 3/2, 4/3, 5/4 等简单整数比）")

    find_simple_ratios()
    compare_tunings()

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(ratios, cons, label='consonance curve (1 - roughness)')
        # 标出简单整数比位置
        for p, q in [(2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (5, 3), (9, 8)]:
            r = p / q
            if 1 <= r <= 2:
                plt.axvline(r, color='r', alpha=0.3)
                plt.text(r, 1.02, f"{p}/{q}", ha='center', fontsize=8)
        plt.xlabel("frequency ratio"); plt.ylabel("consonance")
        plt.title("Plomp-Levelt: 协和峰 ≈ 简单整数比"); plt.legend()
        plt.savefig("consonance.png", dpi=80); print("\n[saved] consonance.png")
    except ImportError:
        pass
