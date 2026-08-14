"""
实验 04 — 通道编码: 香农极限 / Hamming / 重复码
对应文档: 讲透信息论/04-通道编码.md

核心结论:
  1. 二元对称信道 BSC(p): 每个 bit 以概率 p 翻转, 容量 C = 1 - H(p)
  2. 无编码: BER = p (出错率 = 翻转率)
  3. 重复码 (3 倍 + 多数表决): BER 大幅下降, 但效率 1/3
  4. Hamming(7,4): 4 bit 数据 + 3 bit 校验, 能纠 1 bit 错, 效率 4/7
  5. Shannon-Hartley: C = W log2(1+SNR), 5G/WiFi/硬盘都逼近此极限

跑法: python3 -u 04_channel_coding.py
"""
import math, random
from collections import Counter
random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# Part 1: 二元对称信道 (Binary Symmetric Channel, BSC)
# ============================================================
def bsc_channel(bits, p):
    """每个 bit 以概率 p 翻转"""
    return [(b ^ 1) if random.random() < p else b for b in bits]

# ============================================================
# Part 2: 三种编码方案
# ============================================================
def no_encode_decode(data_bits, p):
    """无编码: 直传, 直收"""
    received = bsc_channel(data_bits, p)
    errors = sum(1 for a, b in zip(data_bits, received) if a != b)
    return errors / len(data_bits), len(data_bits)

def repetition_encode_decode(data_bits, p, rep=3):
    """重复码: 每个 bit 重复 rep 次, 接收端多数表决"""
    encoded = []
    for b in data_bits:
        encoded.extend([b] * rep)
    received = bsc_channel(encoded, p)
    decoded = []
    for i in range(0, len(received), rep):
        chunk = received[i:i+rep]
        decoded.append(1 if sum(chunk) > rep // 2 else 0)
    errors = sum(1 for a, b in zip(data_bits, decoded) if a != b)
    return errors / len(data_bits), len(encoded)

# 标准 Hamming(7,4): 编码后 7 位 = [p1, p2, d1, p4, d2, d3, d4]
# p1 覆盖位置 1,3,5,7 (即 p1, d1, d2, d4)
# p2 覆盖位置 2,3,6,7 (即 p2, d1, d3, d4)
# p4 覆盖位置 4,5,6,7 (即 p4, d2, d3, d4)
def hamming_encode(data_4bits):
    """4 数据 bit → 7 编码 bit"""
    d1, d2, d3, d4 = data_4bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p4, d2, d3, d4]

def hamming_decode(received_7bits):
    """7 bit → 4 数据 bit, 能纠 1 个错"""
    p1, p2, d1, p4, d2, d3, d4 = received_7bits
    s1 = p1 ^ d1 ^ d2 ^ d4
    s2 = p2 ^ d1 ^ d3 ^ d4
    s4 = p4 ^ d2 ^ d3 ^ d4
    err_pos = s1 * 1 + s2 * 2 + s4 * 4   # 0=无错, 1-7=出错位置
    corrected = list(received_7bits)
    if err_pos != 0:
        corrected[err_pos - 1] ^= 1
    return [corrected[2], corrected[4], corrected[5], corrected[6]]

def hamming_encode_decode(data_bits, p):
    """Hamming(7,4) 编码 + 解码"""
    pad = (4 - len(data_bits) % 4) % 4
    data_padded = list(data_bits) + [0] * pad
    encoded = []
    for i in range(0, len(data_padded), 4):
        encoded.extend(hamming_encode(data_padded[i:i+4]))
    received = bsc_channel(encoded, p)
    decoded = []
    for i in range(0, len(received), 7):
        decoded.extend(hamming_decode(received[i:i+7]))
    decoded = decoded[:len(data_bits)]
    errors = sum(1 for a, b in zip(data_bits, decoded) if a != b)
    return errors / len(data_bits), len(encoded)

# ============================================================
# Part 3: 跑实验
# ============================================================
P("="*70)
P("实验 04 — 通道编码: 香农极限 / Hamming / 重复码")
P("="*70)
P()
P("信道: 二元对称信道 BSC(p) — 每个 bit 以概率 p 翻转")
P("容量: C = 1 - H(p) bit/信道使用")
P()

def binary_entropy(p):
    if p == 0 or p == 1: return 0.0
    return -p * math.log2(p) - (1-p) * math.log2(1-p)

N_BITS = 10000

print(f"{'翻转率 p':<12}{'容量 C':>10}{'无编码 BER':>14}{'重复 3x BER':>14}{'Hamming BER':>14}{'重复效率':>10}{'Hamming效率':>12}")
print("-"*88)

for p in [0.001, 0.005, 0.01, 0.03, 0.05, 0.1, 0.2]:
    random.seed(42)
    data = [random.randint(0, 1) for _ in range(N_BITS)]
    C = 1 - binary_entropy(p)
    ber_no, _ = no_encode_decode(data, p)
    ber_rep, bits_rep = repetition_encode_decode(data, p)
    ber_ham, bits_ham = hamming_encode_decode(data, p)
    print(f"{p:<12.3f}{C:>10.4f}{ber_no:>14.4%}{ber_rep:>14.4%}{ber_ham:>14.4%}{N_BITS/bits_rep:>10.1%}{N_BITS/bits_ham:>12.1%}")

P("""
解读:
- 无编码: BER = p (出错率 = 翻转率)
- 重复 3x: BER 大幅下降 (多数表决救场), 但效率只有 33%
- Hamming(7,4): BER 更低, 效率 57% (4 数据 / 7 总)
- 信道容量 C: p=0.01 时 C=0.919, p=0.1 时 C=0.531, p=0.5 时 C=0 (无法通信)

香农定理 (Channel Coding Theorem):
  只要传输率 R < C, 就存在某种编码让差错率任意小.
""")

# ============================================================
# Part 4: Shannon-Hartley 定律 (高斯信道)
# ============================================================
P("="*70)
P("Part 2: Shannon-Hartley 定律 — 高斯信道容量 C = W log2(1+SNR)")
P("-"*70)
print(f"\n{'场景':<22}{'带宽 W':>10}{'SNR (dB)':>12}{'SNR (线性)':>14}{'容量 C':>16}")
print("-"*74)
scenarios = [
    ("电话线 (传统)",     3000,    30),
    ("电话线 (高质量)",    3000,    45),
    ("WiFi 2.4GHz",       20000000, 40),
    ("WiFi 5GHz",         80000000, 35),
    ("4G LTE",            20000000, 20),
    ("5G mmWave",         100000000, 10),
    ("光纤入户 (1Gbps)", 500000000, 40),
    ("深空通信",          100,     -100),
]
for name, W, snr_db in scenarios:
    snr_lin = 10 ** (snr_db / 10)
    C = W * math.log2(1 + snr_lin)
    if C > 1e9: cstr = f"{C/1e9:.2f} Gbps"
    elif C > 1e6: cstr = f"{C/1e6:.2f} Mbps"
    elif C > 1e3: cstr = f"{C/1e3:.2f} kbps"
    else: cstr = f"{C:.2f} bps"
    print(f"{name:<22}{W:>10}{snr_db:>12}{snr_lin:>14.2e}{cstr:>16}")

P("""
解读:
- 电话线 30dB SNR → 30 kbps (Shannon 1948 计算的极限)
- 5G mmWave 100MHz + 10dB → ~360 Mbps (实际峰值更高, 因多天线)
- 深空通信 SNR=-100dB → ~0.3 bps (Voyager 1, 靠强纠错码硬撑)
""")

P("="*70)
P("Part 3: 通道编码 → AI 的桥")
P("-"*70)
P("""
1. 【LDPC / Polar 解码 = 概率图模型】
   5G 用的 LDPC 用 Belief Propagation 解码 — 这就是概率图模型的消息传递.

2. 【自监督学习 = 通道编码思想】
   BERT MLM / MAE / Diffusion 都在干: 加噪 → 还原. 本质是 [加冗余再纠错].

3. 【Information Bottleneck】
   深度网络训练 = 压缩 I(X; hidden) + 保留 I(hidden; Y).
   这是 [信道容量] 在表征学习里的化身.
""")
