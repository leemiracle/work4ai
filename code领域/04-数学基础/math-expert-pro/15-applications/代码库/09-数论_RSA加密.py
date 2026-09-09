"""
数论与密码学：RSA 加密算法从零实现
==================================
数学概念：素数 / 模运算 / 欧拉定理 / RSA 公钥密码
应用领域：密码学 / 信息安全 / 数字签名 / 区块链
核心思想：RSA 的安全性基于"大整数分解是困难的"。
  密钥生成：选大素数 p,q → n=pq → φ(n)=(p-1)(q-1) → 选 e 与 φ(n) 互素 → d=e⁻¹ mod φ(n)
  公钥：(e, n)  私钥：(d, n)
  加密：c = m^e mod n   解密：m = c^d mod n
  正确性：由欧拉定理 m^(ed) ≡ m (mod n)（当 gcd(m,n)=1）
运行方式：python "09-数论_RSA加密.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import random
import time

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 数论基础 ============

def is_prime(n, k=20):
    """Miller-Rabin 素性测试。
    概率性算法：如果返回 False，n 一定是合数；
    如果返回 True，n 是素数的概率 ≥ 1 - 4^(-k)。
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    # 分解 n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    # k 轮测试
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=16):
    """生成指定位数的随机素数。"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # 确保最高位是1且是奇数
        if is_prime(n):
            return n


def extended_gcd(a, b):
    """扩展欧几里得算法。返回 (gcd, x, y) 使得 ax + by = gcd(a,b)。"""
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def mod_inverse(a, m):
    """求 a 在模 m 下的乘法逆元（用扩展欧几里得）。"""
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} 在模 {m} 下无逆元")
    return x % m


# ============ 2. RSA 算法 ============

def rsa_keygen(bits=16):
    """RSA 密钥生成。
    返回：公钥 (e, n), 私钥 (d, n), 中间参数 (p, q, phi)
    """
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    # 选 e：常用 65537，这里用小的便于演示
    e = 65537
    if e >= phi:
        e = 3
        while extended_gcd(e, phi)[0] != 1:
            e += 2
    d = mod_inverse(e, phi)
    return (e, n), (d, n), (p, q, phi)


def rsa_encrypt(message, public_key):
    """RSA 加密：c = m^e mod n。message 可以是 int 或字符串。"""
    e, n = public_key
    if isinstance(message, str):
        # 每个字符转为数字，逐个加密（教学版，实际 RSA 用分块）
        return [pow(ord(ch), e, n) for ch in message]
    return pow(message, e, n)


def rsa_decrypt(ciphertext, private_key):
    """RSA 解密：m = c^d mod n。"""
    d, n = private_key
    if isinstance(ciphertext, list):
        return ''.join(chr(pow(c, d, n)) for c in ciphertext)
    return pow(ciphertext, d, n)


# ============ 3. 实验与可视化 ============

def main():
    random.seed(42)

    # ---- 实验 1：素数生成与素性测试 ----
    print("=" * 60)
    print("实验 1：Miller-Rabin 素性测试 + 素数生成")
    print("=" * 60)

    test_numbers = [1, 2, 7, 15, 17, 561, 1105, 1729, 7919, 104729]
    # 561=3×11×17 (Carmichael 数，伪素数), 7919=第1000个素数
    print(f"{'数':<10} {'Miller-Rabin':<14} {'是否真素数':<12}")
    print("-" * 40)
    for num in test_numbers:
        mr_result = is_prime(num)
        # 暴力验证（只对小数）
        true_prime = num > 1 and all(num % i != 0 for i in range(2, int(num**0.5) + 1))
        print(f"{num:<10} {'素数' if mr_result else '合数':<14} {'素数' if true_prime else '合数':<12}")

    print("\n[解读] 561 是 Carmichael 数（费马伪素数），但 Miller-Rabin 能正确识别为合数。")

    # ---- 实验 2：RSA 密钥生成 + 加解密 ----
    print("\n" + "=" * 60)
    print("实验 2：RSA 密钥生成与加解密（16 位素数）")
    print("=" * 60)

    public_key, private_key, (p, q, phi) = rsa_keygen(bits=16)
    e, n = public_key
    d, _ = private_key

    print(f"素数 p = {p}")
    print(f"素数 q = {q}")
    print(f"模数 n = p×q = {n}")
    print(f"欧拉函数 φ(n) = (p-1)(q-1) = {phi}")
    print(f"公钥指数 e = {e}")
    print(f"私钥指数 d = e⁻¹ mod φ(n) = {d}")
    print(f"\n公钥 (e, n) = ({e}, {n})  ← 公开发布")
    print(f"私钥 (d, n) = ({d}, {n})  ← 严格保密")

    # 验证 ed ≡ 1 (mod φ(n))
    print(f"\n验证：e×d mod φ(n) = {(e * d) % phi}（应为 1）✓" if (e * d) % phi == 1 else " ✗")

    # 加密一条消息
    message = "MATH"
    print(f"\n明文: '{message}'")
    print("逐字符加密（ASCII → 密文）：")
    encrypted = rsa_encrypt(message, public_key)
    for ch, c in zip(message, encrypted):
        print(f"  '{ch}' (ASCII={ord(ch)}) → c = {ord(ch)}^{e} mod {n} = {c}")

    decrypted = rsa_decrypt(encrypted, private_key)
    print(f"\n解密: {encrypted}")
    print(f"     → '{decrypted}'")
    print(f"原文 == 解密: {'✓ 正确' if message == decrypted else '✗ 错误'}")

    # ---- 实验 3：RSA 安全性——密钥长度 vs 分解时间 ----
    print("\n" + "=" * 60)
    print("实验 3：大整数分解的困难性（RSA 安全根基）")
    print("=" * 60)

    bit_sizes = [8, 10, 12, 14, 16, 18, 20]
    factor_times = []
    for bits in bit_sizes:
        pub, priv, (p, q, _) = rsa_keygen(bits=bits)
        n = pub[1]
        start = time.time()
        # 试除法分解（最朴素的攻击）
        found = None
        for i in range(2, int(np.sqrt(n)) + 1):
            if n % i == 0:
                found = i
                break
        elapsed = time.time() - start
        factor_times.append(elapsed)
        status = f"p={found}, q={n//found}" if found else "未找到"
        print(f"  {bits:2d}位素数 → n={n:<12} 分解耗时={elapsed:.4f}s  ({status})")

    print(f"\n[解读] 密钥每增加 2 位，分解时间约翻倍（试除法 O(√n)）。")
    print(f"       现代 RSA 用 2048 位（~617 位十进制），分解需 ~10¹⁵ 年。")
    print(f"       这就是 RSA 的安全根基：'乘法容易，分解难'（单向函数）。")

    # ---- 实验 4：数字签名验证 ----
    print("\n" + "=" * 60)
    print("实验 4：RSA 数字签名（用私钥签名，公钥验证）")
    print("=" * 60)

    # 签名 = 用私钥加密
    e, n = public_key  # 恢复实验2的密钥（实验3的循环可能覆盖了n）
    d, _ = private_key
    doc = 12345
    signature = pow(doc, d, n)
    print(f"文件哈希值: {doc}")
    print(f"签名: s = {doc}^{d} mod {n} = {signature}")
    # 验证 = 用公钥解密
    verified = pow(signature, e, n)
    print(f"验证: s^{e} mod {n} = {verified}")
    print(f"签名有效: {'✓' if verified == doc else '✗'}")
    print("\n[解读] 加密用公钥，签名用私钥——方向相反但数学相同。")
    print("       签名证明'只有持私钥的人才能生成它'（不可否认性）。")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：素数分布（前 1000 个素数的间距）
    ax = axes[0, 0]
    primes = [i for i in range(2, 8000) if is_prime(i)]
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    ax.hist(gaps, bins=range(1, max(gaps) + 2), color='steelblue', alpha=0.7, edgecolor='black')
    ax.set_xlabel('相邻素数间距')
    ax.set_ylabel('出现次数')
    ax.set_title(f'素数间距分布（前 {len(primes)} 个素数）')
    ax.axvline(np.mean(gaps), color='red', ls='--', label=f'平均间距={np.mean(gaps):.1f}')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')

    # 图 2：RSA 加解密流程
    ax = axes[0, 1]
    flow_steps = ['明文\nMATH', '公钥加密\nm^e mod n', '密文\n[数字]', '私钥解密\nc^d mod n', '明文\nMATH']
    flow_colors = ['lightgreen', 'lightyellow', 'lightcoral', 'lightyellow', 'lightgreen']
    for i, (step, color) in enumerate(zip(flow_steps, flow_colors)):
        ax.add_patch(plt.Rectangle((i * 2, 0.3), 1.5, 0.6, facecolor=color, edgecolor='black', lw=1.5))
        ax.text(i * 2 + 0.75, 0.6, step, ha='center', va='center', fontsize=9, fontweight='bold')
        if i < len(flow_steps) - 1:
            ax.annotate('', xy=(i * 2 + 2, 0.6), xytext=(i * 2 + 1.5, 0.6),
                        arrowprops=dict(arrowstyle='->', lw=2))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(0, 1.2)
    ax.set_title('RSA 加解密流程')
    ax.axis('off')

    # 图 3：密钥长度 vs 分解时间（对数尺度）
    ax = axes[1, 0]
    ax.semilogy(bit_sizes, factor_times, 'ro-', lw=2, markersize=8)
    ax.set_xlabel('素数位数')
    ax.set_ylabel('分解时间（秒，对数）')
    ax.set_title('RSA 安全性：密钥长度 vs 分解时间')
    ax.grid(alpha=0.3)
    # 标注外推
    ax.annotate('2048位 RSA\n≈ 10¹⁵ 年（外推）', xy=(20, factor_times[-1]),
                xytext=(12, factor_times[-1] * 100),
                fontsize=10, color='red',
                arrowprops=dict(arrowstyle='->', color='red'))

    # 图 4：模运算的周期性（欧拉定理可视化）
    ax = axes[1, 1]
    base = 3
    mod = 7
    powers = [pow(base, k, mod) for k in range(15)]
    ax.plot(range(15), powers, 'bs-', lw=2, markersize=8)
    ax.axhline(1, color='red', ls='--', alpha=0.5, label='返回 1（欧拉定理）')
    period = powers.index(1, 1) if 1 in powers[1:] else len(powers)
    ax.axvline(period, color='green', ls=':', alpha=0.7, label=f'周期 = {period} (=φ({mod})={mod-1})')
    ax.set_xlabel('指数 k')
    ax.set_ylabel(f'{base}^k mod {mod}')
    ax.set_title(f'模运算周期性：{base}^k mod {mod}')
    ax.set_xticks(range(15))
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("09-数论RSA_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 09-数论RSA_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 素数是数论的原子——RSA 用大素数的'难分解性'做安全根基")
    print("2. 欧拉定理 m^φ(n) ≡ 1 (mod n) 是 RSA 正确性的数学保证")
    print("3. 公钥加密/私钥解密 ↔ 私钥签名/公钥验证（同一数学，方向相反）")
    print("4. 密钥每加 2 位，分解难度翻倍——2048 位 = 当今安全标准")
    print("\n[解读] RSA 是'数学直接换安全'的典范——")
    print("       数论（素数/模运算/欧拉定理）→ 密码学 → HTTPS/加密货币/数字签名。")


if __name__ == "__main__":
    main()
