"""
Part II Information Theory & Coding (Cambridge CST)
====================================================
覆盖主题：
- 熵 H(X) / 联合熵 / 条件熵 / 互信息
- Kraft 不等式 & 前缀码
- Huffman 编码
- Lempel-Ziv 77 (LZ77)
- 信道容量（BSC / BEC）
- 汉明码（纠错编码）

核心教材：
- MacKay 2003 "Information Theory, Inference, and Learning Algorithms" Cambridge University Press
- Cover & Thomas 2006 "Elements of Information Theory" 2nd ed, Wiley

核心参考：
- Shannon 1948 "A Mathematical Theory of Communication" Bell System Technical Journal
- Huffman 1952 "A Method for the Construction of Minimum-Redundancy Codes" Proc IRE
- Ziv & Lempel 1977 "A Universal Algorithm for Sequential Data Compression" IEEE Trans IT
- Hamming 1950 "Error Detecting and Correcting Codes" Bell System Technical Journal

本文件实现：
- 熵计算 + 信源编码定理验证
- Huffman 编码（最优前缀码）
- LZ77 压缩
- 二进制对称信道容量
- (7,4) 汉明码编解码 + 纠错

运行：
    python info_theory.py
"""
from __future__ import annotations
import math
import heapq
from collections import Counter


# ================================================================
# 1. 熵与信息量
# ================================================================

def entropy(probs):
    """
    Shannon 熵: H(X) = -Σ p(x) log₂ p(x)
    """
    return -sum(p * math.log2(p) for p in probs if p > 0)


def joint_entropy(joint_probs):
    """联合熵 H(X,Y) = -ΣΣ p(x,y) log₂ p(x,y)"""
    return -sum(p * math.log2(p) for p in joint_probs if p > 0)


def mutual_information(px, py, pxy):
    """
    I(X;Y) = H(X) + H(Y) - H(X,Y)
           = ΣΣ p(x,y) log₂ [p(x,y) / (p(x)p(y))]
    """
    mi = 0.0
    for i in range(len(px)):
        for j in range(len(py)):
            if pxy[i][j] > 0:
                mi += pxy[i][j] * math.log2(pxy[i][j] / (px[i] * py[j]))
    return mi


def kl_divergence(p, q):
    """KL(p||q) = Σ p(x) log₂ [p(x)/q(x)]"""
    return sum(pi * math.log2(pi / qi) for pi, qi in zip(p, q) if pi > 0 and qi > 0)


# ================================================================
# 2. Kraft 不等式 & 前缀码验证
# ================================================================

def kraft_inequality(code_lengths):
    """
    前缀码存在 ⟺ Σ 2^{-l_i} ≤ 1
    """
    return sum(2**(-l) for l in code_lengths) <= 1.0 + 1e-9


def is_prefix_code(codes):
    """检查是否无歧义前缀码"""
    sorted_codes = sorted(codes, key=len)
    for i, c1 in enumerate(sorted_codes):
        for c2 in sorted_codes[i+1:]:
            if c2.startswith(c1):
                return False
    return True


# ================================================================
# 3. Huffman 编码
# ================================================================

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq


def huffman_encode(freq_map):
    """
    Huffman 1952: 构建最优前缀码。
    返回 {char: code_string}
    """
    if len(freq_map) == 0:
        return {}
    if len(freq_map) == 1:
        char = list(freq_map)[0]
        return {char: "0"}

    heap = [HuffmanNode(char=c, freq=f) for c, f in freq_map.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = HuffmanNode(freq=n1.freq + n2.freq, left=n1, right=n2)
        heapq.heappush(heap, merged)

    root = heap[0]
    codes = {}

    def traverse(node, code=""):
        if node.char is not None:
            codes[node.char] = code if code else "0"
            return
        if node.left:
            traverse(node.left, code + "0")
        if node.right:
            traverse(node.right, code + "1")

    traverse(root)
    return codes


def avg_code_length(freq_map, codes):
    """平均码长 L = Σ p(x) · l(x)"""
    total = sum(freq_map.values())
    return sum(freq_map[c] * len(codes[c]) for c in freq_map) / total


# ================================================================
# 4. Lempel-Ziv 77 (LZ77) 压缩
# ================================================================

def lz77_compress(text, window_size=16):
    """
    LZ77: 输出 (offset, length, next_char) 三元组。
    Ziv & Lempel 1977.

    注意: 本实现限制 match length ≤ offset（不允许 overlap 匹配）。
    标准 LZ77 允许 overlap（如 "aaaa" 可用 (1,3,'') 编码），
    此简化版在高度重复数据上压缩率略低。
    """
    result = []
    pos = 0
    while pos < len(text):
        best_offset = 0
        best_length = 0
        # 搜索窗口
        search_start = max(0, pos - window_size)
        for offset in range(1, pos - search_start + 1):
            length = 0
            while (pos + length < len(text) and
                   text[pos - offset + length] == text[pos + length]):
                length += 1
                if pos - offset + length >= pos:
                    break
            if length > best_length:
                best_length = length
                best_offset = offset
        next_char = text[pos + best_length] if pos + best_length < len(text) else ""
        result.append((best_offset, best_length, next_char))
        pos += best_length + 1
    return result


def lz77_decompress(compressed):
    """解压 LZ77"""
    result = []
    for offset, length, char in compressed:
        start = len(result) - offset
        for i in range(length):
            result.append(result[start + i])
        if char:
            result.append(char)
    return "".join(result)


# ================================================================
# 5. 信道容量（二进制对称信道 BSC）
# ================================================================

def bsc_capacity(error_prob):
    """
    二进制对称信道容量:
    C = 1 - H(p)  where H(p) = -p log₂ p - (1-p) log₂(1-p)
    """
    if error_prob == 0 or error_prob == 1:
        return 1.0
    h = entropy([error_prob, 1 - error_prob])
    return 1.0 - h


def shannon_limit(code_rate, channel_capacity):
    """Shannon 编码定理: 可靠传输 ⟺ R < C"""
    return code_rate < channel_capacity


# ================================================================
# 6. 汉明码 (7,4)
# ================================================================

# (7,4) Hamming: 4 数据位 + 3 校验位
# 系统码：数据位在位置 0-3（单位矩阵），校验位在位置 4-6
# H 矩阵的列 j 的值 = j+1 的二进制表示，使 syndrome 直接给出错误位置
#   列值: [1,2,3,4,5,6,7]  ← 标准序
# 生成矩阵 G (4×7) — 系统码形式 [I₄ | P]
# P 由 H·G^T = 0 (mod 2) 解出
HAMMING_G = [
    [1,0,0,0,0,1,1],
    [0,1,0,0,1,0,1],
    [0,0,1,0,1,1,0],
    [0,0,0,1,1,1,1],
]
# 校验矩阵 H (3×7) — 列值为标准序 [1,2,3,4,5,6,7]
# syndrome = H · received, syndrome 值 = 出错位（1-indexed）
HAMMING_H = [
    [1,0,1,0,1,0,1],  # 位 0 (权 1): 覆盖位置 1,3,5,7
    [0,1,1,0,0,1,1],  # 位 1 (权 2): 覆盖位置 2,3,6,7
    [0,0,0,1,1,1,1],  # 位 2 (权 4): 覆盖位置 4,5,6,7
]


def hamming_encode(data_bits):
    """编码 4 位 → 7 位"""
    assert len(data_bits) == 4
    codeword = [0] * 7
    for j in range(7):
        for i in range(4):
            codeword[j] += data_bits[i] * HAMMING_G[i][j]
    return [b % 2 for b in codeword]


def hamming_syndrome(received):
    """计算校验子 syndrome = H · received"""
    syndrome = [0, 0, 0]
    for i in range(3):
        for j in range(7):
            syndrome[i] += HAMMING_H[i][j] * received[j]
    return [s % 2 for s in syndrome]


def hamming_decode(received):
    """解码 + 单比特纠错"""
    syndrome = hamming_syndrome(received)
    # syndrome 值直接给出出错位置（1-indexed），因为 H 列为标准序 [1..7]
    error_pos = syndrome[0]*1 + syndrome[1]*2 + syndrome[2]*4
    if error_pos > 0:
        corrected = list(received)
        corrected[error_pos - 1] ^= 1
        return corrected[:4], error_pos - 1
    return received[:4], -1


def hamming_min_distance():
    """遍历全部 2⁴=16 个码字，计算最小 Hamming 距离 d_min。
    Hamming(7,4) 的 d_min = 3，故可纠正 ⌊(3-1)/2⌋ = 1 个错误。"""
    codewords = [hamming_encode([(i >> b) & 1 for b in range(4)])
                 for i in range(16)]
    min_dist = 7
    for i in range(len(codewords)):
        for j in range(i + 1, len(codewords)):
            d = sum(a != b for a, b in zip(codewords[i], codewords[j]))
            min_dist = min(min_dist, d)
    return min_dist


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part II Information Theory & Coding — Demo")
    print("=" * 64)

    # 1. 熵
    print("\n📋 1. Shannon 熵 H(X)")
    distributions = {
        "均匀(2)": [0.5, 0.5],
        "偏斜(0.9/0.1)": [0.9, 0.1],
        "确定(1.0/0.0)": [1.0, 0.0],
        "4路均匀": [0.25]*4,
    }
    for name, probs in distributions.items():
        h = entropy(probs)
        print(f"   {name:20s}: H = {h:.3f} bits (理论最大 log₂{len(probs)} = {math.log2(len(probs)):.1f})")
    print(f"   ⚠️ 均匀分布熵最大！确定的分布熵=0")

    # 2. Kraft 不等式
    print("\n📋 2. Kraft 不等式 Σ 2^(-l_i) ≤ 1")
    code_lens = [1, 2, 3, 3]  # 经典: {0, 10, 110, 111}
    kraft_sum = sum(2**(-l) for l in code_lens)
    print(f"   码长 {code_lens}: Σ 2^(-l) = {kraft_sum:.3f} ≤ 1? {kraft_sum <= 1.0 + 1e-9}")
    codes = {"a": "0", "b": "10", "c": "110", "d": "111"}
    print(f"   前缀码 {codes}: 无歧义? {is_prefix_code(list(codes.values()))}")

    # 3. Huffman
    print("\n📋 3. Huffman 编码（最优前缀码）")
    freq = {"A": 50, "B": 25, "C": 15, "D": 10}
    huff = huffman_encode(freq)
    total = sum(freq.values())
    probs = [f / total for f in freq.values()]
    H = entropy(probs)
    L_avg = avg_code_length(freq, huff)
    print(f"   频率: {freq}")
    print(f"   编码: {huff}")
    print(f"   熵 H(X) = {H:.3f} bits")
    print(f"   Huffman 平均码长 = {L_avg:.3f} bits")
    print(f"   效率 = H/L = {H/L_avg:.1%}  (Huffman ≤ 熵 + 1 bit)")

    # 4. LZ77
    print("\n📋 4. LZ77 压缩")
    text = "abracadabraabracadabra"
    compressed = lz77_compress(text, window_size=12)
    decompressed = lz77_decompress(compressed)
    orig_bits = len(text) * 8
    comp_bits = len(compressed) * 12  # 每三元组 ≈ 12 bits (简化)
    print(f"   原文: '{text}' ({len(text)} 字符, {orig_bits} bits)")
    print(f"   压缩: {len(compressed)} 三元组")
    for t in compressed[:5]:
        print(f"     offset={t[0]}, len={t[1]}, next='{t[2]}'")
    if len(compressed) > 5:
        print(f"     ... ({len(compressed)-5} more)")
    print(f"   解压: '{decompressed}'")
    print(f"   正确? {decompressed == text}")
    print(f"   压缩比: {orig_bits/comp_bits:.2f}x")

    # 5. 信道容量
    print("\n📋 5. 二进制对称信道（BSC）容量")
    for p in [0.0, 0.01, 0.1, 0.5, 0.9]:
        cap = bsc_capacity(p)
        print(f"   错误率 p={p:.2f}: C = 1 - H(p) = {cap:.3f} bits/信道使用")

    # 6. 汉明码
    print("\n📋 6. (7,4) 汉明码（单比特纠错）")
    data = [1, 0, 1, 1]
    encoded = hamming_encode(data)
    print(f"   数据: {data} → 编码: {encoded}")
    # 遍历全部 7 个位置，逐个翻转验证纠错
    correct_count = 0
    for pos in range(7):
        corrupted = list(encoded)
        corrupted[pos] ^= 1
        decoded, error_pos = hamming_decode(corrupted)
        ok = (decoded == data and error_pos == pos)
        if ok:
            correct_count += 1
    print(f"   7 个位置单比特翻转纠错: {correct_count}/7 正确")
    # 展示一个具体例子
    corrupted = list(encoded)
    corrupted[3] ^= 1
    print(f"   传输错误(第4位翻转): {corrupted}")
    decoded, error_pos = hamming_decode(corrupted)
    print(f"   解码: {decoded}, 纠错位置: {error_pos}")
    print(f"   纠错正确? {decoded == data}")

    # 最小 Hamming 距离
    d_min = hamming_min_distance()
    t_corr = (d_min - 1) // 2
    t_det = d_min - 1
    print(f"   遍历全部 2⁴=16 码字: d_min = {d_min}")
    print(f"   → 可纠 {t_corr} 个错误, 可检 {t_det} 个错误")

    print("\n✅ Information Theory & Coding 完成！")
    print("\n💡 反直觉发现：")
    print(f"   - Hamming(7,4) 遍历 16 码字: d_min={d_min}, "
          f"即 3 个冗余位换来纠正 1 个错误（R=4/7≈57%）")
    print(f"   - Huffman 效率 = H/L = {H/L_avg:.1%}（4 符号已逼近 100%；"
          f"符号越多效率越高，因 H↑时 +1 bit 碎片占比↓）")
    print(f"   - BSC p=0.5 时容量=0（完全噪声无法传输信息）")
    print(f"   - Shannon 极限: Hamming(7,4) R={4/7:.3f}, "
          f"C(p=0.01)={bsc_capacity(0.01):.3f} > R 可靠, "
          f"C(p=0.1)={bsc_capacity(0.1):.3f} < R 不可靠")


if __name__ == "__main__":
    demo()
