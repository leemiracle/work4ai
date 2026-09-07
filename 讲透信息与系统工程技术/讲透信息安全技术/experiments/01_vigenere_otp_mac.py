# -*- coding: utf-8 -*-
"""
01_vigenere_otp_mac.py — 维吉尼亚自动破译 + 一次性密码板重用灾难 + HMAC 截断伪造概率

对应章:04-信息安全技术转代码(走廊① 经典密码分析"算得准"/§三 可机械化边界/§五 裂缝1)
      00-体系结构(§六 反直觉① 一次一密密钥不短于明文、② 加密≠认证家族背景)
      02-语言特征(§一 安全游戏:破译优势/伪造优势都是概率语句)
GB/T 41320 信息安全技术 · 家族层实验(纯标准库,assert 自验证,exit 0)

三部分:
  [1] 频率分析自动破译维吉尼亚密码(重合指数定钥长 + 卡方定移位)——assert 恢复密钥与明文
  [2] 一次性密码板(OTP)的信息论视角——穷举验证完美保密、Shannon 界违反演示、
      两次使用(重用)泄漏明文异或 + crib-drag 部分恢复明文
  [3] HMAC 截断标签的随机伪造概率——解析解 2^-t vs 蒙特卡洛实测(二项置信带)

运行:python 01_vigenere_otp_mac.py
"""

import hmac
import hashlib
import random
import string
import sys

if hasattr(sys.stdout, "reconfigure"):          # Windows 控制台兼容
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

A = string.ascii_lowercase                      # 'abcdefghijklmnopqrstuvwxyz'

# 英文字母频率(%),Katz & Lindell 附录/Brown 语料通行值
ENG_FREQ = {
    'a': 8.167, 'b': 1.492, 'c': 2.782, 'd': 4.253, 'e': 12.702, 'f': 2.228,
    'g': 2.015, 'h': 6.094, 'i': 6.966, 'j': 0.153, 'k': 0.772, 'l': 4.025,
    'm': 2.406, 'n': 6.749, 'o': 7.507, 'p': 1.929, 'q': 0.095, 'r': 5.987,
    's': 6.327, 't': 9.056, 'u': 2.758, 'v': 0.978, 'w': 2.360, 'x': 0.150,
    'y': 1.974, 'z': 0.074,
}

# 自然英文明文(约 690 字母,讲述本家族自己的历史)——频率分析需要真实语言分布
BASE_PLAIN = (
    "cryptology is the mathematics of security it studies the design of "
    "ciphers and codes and the art of breaking them a cipher protects a "
    "message by mixing it with a key so that an eavesdropper who sees only "
    "the ciphertext learns nothing about the original text for thousands of "
    "years ciphers were symmetric the same key that encrypted a message also "
    "decrypted it then in nineteen seventy six diffie and hellman showed that "
    "two strangers could agree on a shared secret over a public channel and "
    "modern cryptography was born today encryption protects bank transfers "
    "private messages and medical records yet the rule behind it is simple "
    "enough to state keep the method public and keep only the key secret"
)


# ─────────────────────────────────────────────────────────────────────
# 第 1 部分:维吉尼亚密码频率分析自动破译
# ─────────────────────────────────────────────────────────────────────

def vigenere_encrypt(plain: str, key: str) -> str:
    """加密:ci = (mi + ki) mod 26(密钥循环使用)。"""
    out = []
    for i, ch in enumerate(plain):
        k = A.index(key[i % len(key)])
        out.append(A[(A.index(ch) + k) % 26])
    return "".join(out)


def vigenere_decrypt(cipher: str, key: str) -> str:
    out = []
    for i, ch in enumerate(cipher):
        k = A.index(key[i % len(key)])
        out.append(A[(A.index(ch) - k) % 26])
    return "".join(out)


def index_of_coincidence(seq: str) -> float:
    """重合指数 IC = Σ f_i(f_i-1) / (n(n-1)):随机文本≈0.038,单表替换英文≈0.066。
    (Friedman 1920s 为破多表密码发明——统计侧信道的祖师爷)"""
    n = len(seq)
    if n < 2:
        return 0.0
    freq = {c: seq.count(c) for c in A}
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))


def chi2_english(seq: str, shift: int) -> float:
    """该列以 shift 为钥字解密后与英文分布的卡方距离(越小越像英文)。
    解密:明文字母 e 对应的密文字母是 A[(idx(e)+shift)%26] —— 方向别搞反。"""
    n = len(seq)
    chi2 = 0.0
    for c in A:
        observed = seq.count(A[(A.index(c) + shift) % 26])
        expected = n * ENG_FREQ[c] / 100.0
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return chi2


def break_vigenere(cipher: str, max_keylen: int = 12) -> str:
    """全自动破译:①重合指数定钥长(取平均 IC 达标的最小长度——避开真长的倍数);
    ②逐列卡方对齐英文频率定移位。"""
    # ① 钥长检测:真钥长 L 的每一列都是单表替换 → 平均 IC≈0.066;
    #    错误钥长的列混入多表 → IC 塌向 0.038。L 的倍数同样高分,故取最小达标者。
    best_len = None
    for L in range(1, max_keylen + 1):
        cols = [cipher[i::L] for i in range(L)]
        avg_ic = sum(index_of_coincidence(col) for col in cols) / L
        if avg_ic >= 0.058:                       # 达标阈值:单表英文水平
            best_len = L
            break
    if best_len is None:                          # 兜底:取平均 IC 最大者
        ic_by_len = {}
        for L in range(1, max_keylen + 1):
            cols = [cipher[i::L] for i in range(L)]
            ic_by_len[L] = sum(index_of_coincidence(col) for col in cols) / L
        best_len = max(ic_by_len, key=ic_by_len.get)
    # ② 逐列卡方:找让列"最像英文"的移位
    key = ""
    for i in range(best_len):
        col = cipher[i::best_len]
        best_shift = min(range(26), key=lambda s: chi2_english(col, s))
        key += A[best_shift]
    return key


def part1_vigenere():
    print("=" * 64)
    print("[1] 维吉尼亚密码 · 频率分析自动破译(重合指数定钥长 + 卡方定移位)")
    print("=" * 64)
    plain = (BASE_PLAIN.replace(" ", "")) * 2     # ~1380 字母,给卡方足够样本

    # 测试 A:经典钥 LEMON(钥长 5)
    key_a = "lemon"
    cipher_a = vigenere_encrypt(plain, key_a)
    rec_key = break_vigenere(cipher_a)
    rec_plain = vigenere_decrypt(cipher_a, rec_key)
    ic_rand = index_of_coincidence("".join(random.Random(1).choices(A, k=2000)))
    print(f"  随机文本 IC ≈ {ic_rand:.3f}(理论 0.038)| 单表英文 IC ≈ 0.066")
    print(f"  密钥 lemon(5 字母): 破译钥 = {rec_key}  "
          f"[{'OK' if rec_key == key_a else 'FAIL'}]")
    assert rec_key == key_a, f"破译钥 {rec_key} != {key_a}"
    assert rec_plain == plain, "明文未恢复"
    print(f"  明文完整恢复: assert 通过(前 40 字母: {rec_plain[:40]}...)")

    # 测试 B:确定性随机钥(7 字母)——方法不能只认识演示钥
    rng = random.Random(20260907)
    key_b = "".join(rng.choice(A) for _ in range(7))
    cipher_b = vigenere_encrypt(plain, key_b)
    rec_key_b = break_vigenere(cipher_b)
    print(f"  随机钥 {key_b}(7 字母): 破译钥 = {rec_key_b}  "
          f"[{'OK' if rec_key_b == key_b else 'FAIL'}]")
    assert rec_key_b == key_b, f"破译钥 {rec_key_b} != {key_b}"
    assert vigenere_decrypt(cipher_b, rec_key_b) == plain
    print("  → 结论:多表密码的泄漏是统计性的——字母分布=明文的指纹,")
    print("    优势≈1,安全游戏毫无悬念(02 章:频率分析就是一个多项式时间策略)")


# ─────────────────────────────────────────────────────────────────────
# 第 2 部分:一次性密码板(OTP)——信息论视角
# ─────────────────────────────────────────────────────────────────────

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def part2_otp():
    print()
    print("=" * 64)
    print("[2] 一次性密码板 · 完美保密 / Shannon 界 / 重用灾难")
    print("=" * 64)

    # ① 完美保密穷举验证(Z3:模 3 加法一次一密)
    #    P(C=c | M=m) 对一切 m 相同 ⟺ 密文不含明文信息(Shannon 1949 的定义)
    for modulus in (3, 5):
        max_dev = 0.0
        for c in range(modulus):
            probs = []
            for m in range(modulus):
                hits = sum(1 for k in range(modulus) if (m + k) % modulus == c)
                probs.append(hits / modulus)      # 密钥均匀
            max_dev = max(max_dev, max(probs) - min(probs))
        assert max_dev < 1e-12, "完美保密失效"
        print(f"  ① |K|=|M|={modulus} 的 OTP: P(C=c|M=m) 处处相等"
              f"(最大偏差 {max_dev:.1e}) → 完美保密 [OK]")

    # ② Shannon 界违反演示:|K| < |M| 时不可能完美保密
    #    模 3 明文,密钥只有 {0,1} 两把 → 密文立刻泄漏
    leaks = {}
    for c in range(3):
        probs = []
        for m in range(3):
            hits = sum(1 for k in (0, 1) if (m + k) % 3 == c)
            probs.append(hits / 2)
        leaks[c] = (min(probs), max(probs))
    worst = max(leaks.values(), key=lambda t: t[1] - t[0])
    print(f"  ② |K|=2 < |M|=3:观察到 C=2 时 P(M) 随 m 在 "
          f"{leaks[2][0]:.2f}~{leaks[2][1]:.2f} 摆动 → 密文泄漏明文")
    assert worst[1] - worst[0] > 0.4, "Shannon 界违反未演示出来"
    print("     → Shannon 界:完美保密必须 |K|>=|M|(00 章反直觉①)")

    # ③ 两次使用(重用):c1^c2 = m1^m2,密钥彻底消失
    m1 = (b"meeting at the watchtower at dawn bring our encoded roster "
          b"and burn after reading")
    m2 = (b"the supply convoy will pass the northern bridge before "
          b"moonrise wait for the signal")
    rng = random.Random(42)
    key = bytes(rng.randrange(256) for _ in range(len(m1)))   # "一次性"密码板
    c1, c2 = xor_bytes(m1, key), xor_bytes(m2, key)           # 用了两次!
    assert xor_bytes(c1, c2) == xor_bytes(m1, m2), "两次使用泄漏恒等式失败"
    print("  ③ 重用一次:c1^c2 == m1^m2(密钥从等式中消失)[OK]")
    print("     知道 m1 任意片段即可剥出 m2 对应片段——crib-drag:")

    crib = b"watchtower"                              # m1 中唯一的实物名词
    probe = xor_bytes(c1, c2)
    scores = []
    for off in range(0, len(probe) - len(crib) + 1):
        frag = xor_bytes(probe[off:off + len(crib)], crib)
        score = sum(1 for b in frag if b in b"abcdefghijklmnopqrstuvwxyz ")
        scores.append((score, off))
    top_score, top_off = max(scores)
    true_off = m1.index(crib)
    top_frag = xor_bytes(probe[top_off:top_off + len(crib)], crib)
    print(f"     crib='watchtower' → 最佳窗口偏移 {top_off}(真实偏移 {true_off})")
    print(f"     剥出 m2 对应片段: {top_frag!r}  得分 {top_score}/{len(crib)}")
    assert (top_score, top_off) == (len(crib), true_off), "crib-drag 未命中"
    assert xor_bytes(probe[true_off:true_off + len(crib)], crib) == \
        m2[true_off:true_off + len(crib)]
    print("     → 一次一密只用一次才完美;用两次,连密钥都不用找——")
    print("       00 章 Kerckhoffs 假设的反面教材:秘密的重用=结构的泄漏")


# ─────────────────────────────────────────────────────────────────────
# 第 3 部分:HMAC 截断标签的随机伪造概率
# ─────────────────────────────────────────────────────────────────────

def part3_hmac():
    print()
    print("=" * 64)
    print("[3] HMAC 截断标签 · 随机伪造概率(解析 2^-t vs 蒙特卡洛)")
    print("=" * 64)
    key = bytes(random.Random(7).randrange(256) for _ in range(32))
    msg = b"transfer 1000 yuan to account 8899"
    t_bits = 8                                     # 截断到 1 字节
    n_trials = 25600
    tag = hmac.new(key, msg, hashlib.sha256).digest()[:t_bits // 8]

    rng = random.Random(2026)
    hits = 0
    for _ in range(n_trials):                      # 不持密钥的随机伪造者
        guess = bytes(rng.randrange(256) for _ in range(t_bits // 8))
        if hmac.compare_digest(guess, tag):        # 恒定时间比较(04 章走廊②纪律)
            hits += 1
    p_exact = 2 ** -t_bits
    expected = n_trials * p_exact
    lo, hi = expected * 0.55, expected * 1.45      # ~5σ 置信带(二项 σ≈10)
    print(f"  截断 {t_bits} 比特(1 字节), 伪造 {n_trials} 次:")
    print(f"  解析成功率 2^-{t_bits} = {p_exact:.6f} → 期望命中 {expected:.0f}")
    print(f"  实测命中 {hits} 次, 置信带 [{lo:.0f}, {hi:.0f}] "
          f"[{'OK' if lo <= hits <= hi else 'FAIL'}]")
    assert lo <= hits <= hi, f"实测 {hits} 偏离二项期望 {expected:.0f}"
    print("  → 工程直觉:每砍 1 比特标签,伪造成本减半——「指数墙是可以被")
    print("    工程师亲手拆掉的」(03 章练习 2 的现场)。全 32 字节标签时,")
    print("    随机伪造要 ~2^255 次才期望命中一次:归约把不对称买成了顺差")


def main():
    print("GB/T 41320 讲透信息安全技术 · 家族实验")
    print("维吉尼亚破译 / 一次性密码板 / HMAC 截断伪造\n")
    part1_vigenere()
    part2_otp()
    part3_hmac()
    print()
    print("=" * 64)
    print("[ALL ASSERTS PASSED] 三部分全部通过(exit 0)")
    print("带走一句(04 章):安全等级的断层=构造力的断层——")
    print("维吉尼亚全自动破开,OTP(单用)信息论封死,截断 MAC 的墙由你保留的比特数决定。")
    print("=" * 64)


if __name__ == "__main__":
    main()
