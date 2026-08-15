"""
07_euclidean_rhythm.py
======================
节奏的数学：Euclidean rhythms（Godfried Toussaint, 2005）。

惊人的发现：世界各地的"均匀分散节奏"（巴西 samba、古巴 bell pattern、
印度 tala、马其顿 7/8）全部是欧几里得算法（gcd 那个）的副产品。

把 k 个 onset 尽可能均匀放进 n 个时间槽 = E(k, n)。
Bjorklund 算法（最初用于原子加速器定时）高效实现。
"""
import numpy as np


def bjorklund(k, n):
    """
    Bjorklund 算法：把 k 个 1 均匀放进 n 个位置（k ≤ n）。
    返回长度 n 的 0/1 数组。
    """
    if k == 0: return [0] * n
    if k > n: k = k % n
    # 初始：k 个 [1] 和 (n-k) 个 [0]
    ones = [[1] for _ in range(k)]
    zeros = [[0] for _ in range(n - k)]
    while len(zeros) > 1 and len(ones) > 1:
        m = min(len(ones), len(zeros))
        # 把 zeros 的前 m 个并入 ones
        merged = [a + b for a, b in zip(ones[:m], zeros[:m])]
        remaining_ones = ones[m:]
        remaining_zeros = zeros[m:]
        ones = remaining_ones + merged
        zeros = remaining_zeros
        if len(ones) == 0:
            ones = merged; zeros = []
    result = []
    for seq in ones + zeros:
        result.extend(seq)
    return result[:n]


def rotate(seq, k):
    """循环移位（让第一个 onset 在拍点 0）"""
    n = len(seq)
    idx = seq.index(1) if 1 in seq else 0
    return seq[-idx:] + seq[:-idx]


def pattern_to_grid(pattern, label=""):
    """可视化：x = onset, . = 空"""
    grid = " ".join("x" if p else "." for p in pattern)
    return f"[{grid}]  {label}"


def inter_onset_intervals(pattern):
    """计算 onset 之间的间隔序列（识别节奏指纹）"""
    idxs = [i for i, p in enumerate(pattern) if p]
    if len(idxs) < 2: return []
    diffs = np.diff(idxs).tolist()
    diffs.append(len(pattern) - idxs[-1] + idxs[0])  # 循环
    return diffs


if __name__ == "__main__":
    print("=" * 70)
    print("Euclidean Rhythms：世界节奏的数学指纹")
    print("=" * 70)

    cases = [
        (3, 8,   "古巴 tresillo / 巴西 samba 基础"),
        (3, 7,   "Ruchenitza（马其顿/巴尔干 7/8）"),
        (2, 5,   "古巴 Cinquillo Cubano 变体"),
        (2, 3,   "基本三对二"),
        (4, 7,   "Yoruba bell pattern 变体"),
        (5, 8,   "古巴 Cinquillo"),
        (5, 12,  "南非/西非 Venda bell pattern"),
        (7, 12,  "西非/古鲁巴 bell pattern（最经典）"),
        (7, 16,  "现代 16 步电子常用"),
        (9, 16,  "复杂 syncopated 节奏"),
        (11, 24, "印度 tala 变体"),
    ]
    for k, n, label in cases:
        p = bjorklund(k, n)
        p = rotate(p, 0)
        iv = inter_onset_intervals(p)
        print(f"\nE({k},{n})  {label}")
        print(f"  {pattern_to_grid(p)}")
        print(f"  间隔: {iv}")

    print("\n" + "=" * 70)
    print("核心洞察：")
    print("  - 人类对'好节奏'的直觉 = 数学上'最大分散'")
    print("  - 简单整数比不仅是和声（毕达哥拉斯），也是节奏（Toussaint）")
    print("  - E(3,8) 在古巴西非巴西；E(7,12) 横跨非洲；不是文化传递，是数学必然")
    print("=" * 70)
