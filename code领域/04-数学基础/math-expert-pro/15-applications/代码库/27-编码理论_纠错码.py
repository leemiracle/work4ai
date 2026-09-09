"""编码理论：纠错码与可靠通信
================================
数学概念：编码理论 / 汉明距离 / 线性码 / 汉明码 / Reed-Solomon / Shannon 定理
应用领域：二维码 / CD/DVD / 卫星通信 / 5G / 深空探测 / QR码 / 数据存储
核心思想：在信息中加入冗余，使接收端能检测并纠正传输错误。
  汉明距离 d(x,y)：两个码字不同的位数
  码的最小距离 d_min：纠 t 位错需要 d_min ≥ 2t+1
  线性码 [n,k,d]：k 位信息 → n 位码字，最小距离 d
  汉明码 [7,4,3]：4 位信息 + 3 位校验 = 7 位码字，纠 1 位错
  Reed-Solomon：多项式运算的纠错码，CD/QR/卫星的标准
  Shannon 定理：信道容量 C = 1-H(p)（二进制对称信道）
运行方式：python "27-编码理论_纠错码.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def hamming_distance(a, b):
    """汉明距离：两个二进制向量不同的位数。"""
    return np.sum(np.array(a) != np.array(b))

def hamming_encode(msg):
    """汉明(7,4)编码。4位信息→7位码字。
    生成矩阵 G = [I₄ | P]，P 是校验部分。"""
    G = np.array([[1,0,0,0,1,1,0],
                   [0,1,0,0,1,0,1],
                   [0,0,1,0,0,1,1],
                   [0,0,0,1,1,1,1]], dtype=int)
    return np.dot(msg, G) % 2

def hamming_decode(codeword):
    """汉明(7,4)译码（纠1位错）。
    校验矩阵 H，伴随式 s = H·r^T 指出错误位置。"""
    H = np.array([[1,1,0,1,1,0,0],
                   [1,0,1,1,0,1,0],
                   [0,1,1,1,0,0,1]], dtype=int)
    s = np.dot(H, codeword) % 2  # 伴随式
    syndrome_val = s[0]*4 + s[1]*2 + s[2]  # 二进制→十进制（错误位置）
    if syndrome_val > 0:
        codeword = codeword.copy()
        codeword[syndrome_val - 1] ^= 1  # 翻转错误位
    return codeword[:4]  # 返回信息位

def main():
    np.random.seed(42)
    print("="*60); print("实验 1：汉明距离与检错能力"); print("="*60)
    print(f"{'码字对':<20} {'汉明距离':<10} {'可检测':<10} {'可纠正'}")
    pairs = [(np.array([0,0,0,0]), np.array([0,0,0,0])),
             (np.array([0,0,0,0]), np.array([1,0,0,0])),
             (np.array([0,0,0,0]), np.array([1,1,0,0])),
             (np.array([0,0,0,0]), np.array([1,1,1,0])),
             (np.array([0,0,0,0]), np.array([1,1,1,1]))]
    for a, b in pairs:
        d = hamming_distance(a, b)
        print(f"  {a} vs {b}  d={d:<5} {d}位{'':>4} ⌊(d-1)/2⌋={max(0,(d-1)//2)}位")

    print("\n"+"="*60); print("实验 2：汉明(7,4)码——编码与纠错"); print("="*60)
    msg = np.array([1, 0, 1, 1])
    encoded = hamming_encode(msg)
    print(f"原始信息: {msg}")
    print(f"编码后: {encoded} (4位信息+3位校验)")
    # 注入1位错误
    error_pos = 3
    corrupted = encoded.copy(); corrupted[error_pos] ^= 1
    print(f"注入错误(位置{error_pos}): {corrupted}")
    decoded = hamming_decode(corrupted)
    print(f"纠错后信息: {decoded} {'✓ 正确' if np.array_equal(decoded, msg) else '✗ 错误'}")
    # 测试所有单比特错误
    print(f"\n测试所有7个位置的单比特错误：")
    success = 0
    for pos in range(7):
        c = encoded.copy(); c[pos] ^= 1
        d = hamming_decode(c)
        ok = np.array_equal(d, msg)
        success += ok
        print(f"  错误位置{pos}: 纠正 {'✓' if ok else '✗'}")
    print(f"成功率: {success}/7 = {success/7:.0%}")

    print("\n"+"="*60); print("实验 3：Shannon 编码定理——理论极限"); print("="*60)
    p_error = np.linspace(0.001, 0.999, 100)
    # 二进制对称信道容量 C = 1 - H(p)
    H_p = -p_error * np.log2(p_error) - (1-p_error) * np.log2(1-p_error)
    capacity = 1 - H_p
    print("Shannon 定理：C = 1 - H(p)")
    print(f"  p=0.0: C=1.0（无噪声，完美传输）")
    print(f"  p=0.1: C={1-(-0.1*np.log2(0.1)-0.9*np.log2(0.9)):.3f}")
    print(f"  p=0.5: C=0.0（完全噪声，不可通信）")
    print(f"\n[解读] C>0 时理论上可以实现任意可靠的通信。")
    print(f"       这就是 Shannon（1948）的革命性洞见——噪声不限制可靠性！")

    print("\n"+"="*60); print("实验 4：编码理论的应用全景"); print("="*60)
    apps = [("汉明码", "内存ECC/通信校验", "1位"),
            ("Reed-Solomon", "CD/DVD/QR码/卫星", "多位(多项式)"),
            ("BCH码", "SSD存储/二维码", "多位"),
            ("LDPC码", "5G/Wi-Fi 6/DVB-S2", "接近Shannon极限"),
            ("Turbo码", "3G/4G/深空探测", "接近Shannon极限"),
            ("Polar码", "5G控制信道", "理论可达Shannon极限")]
    for code, app, capability in apps:
        print(f"  {code:<18} → {app:<22} 纠错: {capability}")

    # 可视化
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    ax = axes[0]
    ax.plot(p_error[:50]*2, capacity[:50]*2 if hasattr(capacity,'__len__') else capacity, 'b-', lw=2)
    ax2 = ax.twinx()
    ax2.plot(p_error, H_p, 'r--', lw=2, label='H(p) 熵')
    ax.plot(p_error, capacity, 'b-', lw=2, label='C=1-H(p) 容量')
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0.5, color='orange', ls=':', alpha=0.5)
    ax.set_xlabel('错误概率 p'); ax.set_ylabel('信道容量 C', color='blue')
    ax2.set_ylabel('熵 H(p)', color='red')
    ax.set_title('Shannon 信道容量 vs 噪声'); ax.legend(loc='upper right')
    # 汉明码编码过程
    ax = axes[1]
    all_msgs = [list(map(int, format(i, '04b'))) for i in range(16)]
    all_codes = [hamming_encode(np.array(m)) for m in all_msgs]
    codeword_ints = [sum(b << (6-i) for i, b in enumerate(c)) for c in all_codes]
    ax.scatter(range(128), [1 if i in codeword_ints else 0 for i in range(128)], s=3, c=['red' if i in codeword_ints else 'lightgray' for i in range(128)])
    ax.set_xlabel('7位码字（十进制）'); ax.set_ylabel('是/否')
    ax.set_title('汉明(7,4)码：128个可能中只用16个码字')
    ax.set_xlim(-1, 128)
    # 纠错能力
    ax = axes[2]
    d_mins = [1, 3, 5, 7, 9]
    detect = [d-1 for d in d_mins]
    correct = [(d-1)//2 for d in d_mins]
    x = np.arange(len(d_mins)); w = 0.35
    ax.bar(x - w/2, detect, w, label='可检测位数', color='steelblue')
    ax.bar(x + w/2, correct, w, label='可纠正位数', color='coral')
    ax.set_xticks(x); ax.set_xticklabels([f'd={d}' for d in d_mins])
    ax.set_xlabel('最小距离 d_min'); ax.set_ylabel('位数')
    ax.set_title('最小距离 vs 检错/纠错能力')
    ax.legend(); ax.grid(alpha=0.3, axis='y')
    plt.tight_layout(); plt.savefig("27-编码理论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 27-编码理论_结果.png")
    print("\n[总结] 1. 编码理论=用数学实现可靠通信")
    print("2. 汉明码[7,4,3]: 4信息+3校验, 纠1位错")
    print("3. Shannon定理: C>0时理论可靠, 噪声不限制可靠性")
    print("4. LDPC/Polar码接近Shannon极限→5G/深空通信")

if __name__ == "__main__": main()
