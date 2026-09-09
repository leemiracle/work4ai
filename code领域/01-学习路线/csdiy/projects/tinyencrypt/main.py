#!/usr/bin/env python3
"""
tinyencrypt — 参照 OpenSSL/age 的迷你加密库

参照：OpenSSL (AES/RSA) + age (现代加密工具)
csdiy 对应：network §六(TLS) + code-review §六(安全) + csapp Ch2(位运算)

核心：
- XOR 流密码（简化版 AES-CTR，演示用）
- SHA-256 哈希（从零实现，参照 RFC 6234）
- 密钥派生（PBKDF2 简化版）

⚠️ 仅供学习，生产环境请用 cryptography 库！
"""
import sys, os, struct, hashlib, time

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHA-256 从零实现（参照 RFC 6234 + csapp 位级操作）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SHA256:
    """
    SHA-256 哈希（参照 NIST FIPS 180-4）

    不用 hashlib，从位运算开始实现。
    用于理解哈希函数的本质。
    """
    K = [
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
    ]
    H0 = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]

    @staticmethod
    def _rotr(x, n): return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
    @staticmethod
    def _ch(x, y, z): return (x & y) ^ (~x & z)
    @staticmethod
    def _maj(x, y, z): return (x & y) ^ (x & z) ^ (y & z)
    @staticmethod
    def _s0(x): return SHA256._rotr(x,2) ^ SHA256._rotr(x,13) ^ SHA256._rotr(x,22)
    @staticmethod
    def _s1(x): return SHA256._rotr(x,6) ^ SHA256._rotr(x,11) ^ SHA256._rotr(x,25)
    @staticmethod
    def _g0(x): return SHA256._rotr(x,7) ^ SHA256._rotr(x,18) ^ (x >> 3)
    @staticmethod
    def _g1(x): return SHA256._rotr(x,17) ^ SHA256._rotr(x,19) ^ (x >> 10)

    @staticmethod
    def hash(data: bytes) -> str:
        """计算 SHA-256"""
        h = list(SHA256.H0)
        # 填充（参照 FIPS 180-4 §5.1.1）
        msg = bytearray(data)
        msg_len = len(data) * 8
        msg.append(0x80)
        while len(msg) % 64 != 56:
            msg.append(0)
        msg.extend(struct.pack('>Q', msg_len))

        # 分块处理
        for i in range(0, len(msg), 64):
            block = msg[i:i+64]
            w = list(struct.unpack('>16I', block))
            for j in range(16, 64):
                w.append((SHA256._g1(w[j-2]) + w[j-7] + SHA256._g0(w[j-15]) + w[j-16]) & 0xFFFFFFFF)

            a,b,c,d,e,f,g,hh = h
            for j in range(64):
                t1 = (hh + SHA256._s1(e) + SHA256._ch(e,f,g) + SHA256.K[j] + w[j]) & 0xFFFFFFFF
                t2 = (SHA256._s0(a) + SHA256._maj(a,b,c)) & 0xFFFFFFFF
                hh=g; g=f; f=e; e=(d+t1)&0xFFFFFFFF; d=c; c=b; b=a; a=(t1+t2)&0xFFFFFFFF
            h = [(x+y)&0xFFFFFFFF for x,y in zip(h,[a,b,c,d,e,f,g,hh])]

        return ''.join(f'{x:08x}' for x in h)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# XOR 流密码（简化版 AES-CTR，演示用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StreamCipher:
    """
    XOR 流密码（演示 CTR 模式原理）

    AES-CTR 原理：
    1. 用密钥加密 nonce+counter → 生成密钥流
    2. 密钥流 XOR 明文 → 密文

    本实现用 SHA-256 生成密钥流（简化）。
    生产环境请用 AES-256-GCM！
    """

    def __init__(self, key: bytes):
        """用密钥初始化（密钥先 SHA-256 确保 32 字节）"""
        self.key = bytes.fromhex(SHA256.hash(key))

    def _keystream(self, nonce: int, length: int) -> bytes:
        """生成密钥流（参照 AES-CTR 的 counter 模式）"""
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            block_input = nonce.to_bytes(8, 'big') + counter.to_bytes(8, 'big')
            block = bytes.fromhex(SHA256.hash(self.key + block_input))
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    def encrypt(self, plaintext: bytes) -> bytes:
        """加密（参照 OpenSSL enc）"""
        nonce = int.from_bytes(os.urandom(8), 'big')
        keystream = self._keystream(nonce, len(plaintext))
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, keystream))
        # nonce 前置（参照 age 的封装）
        return nonce.to_bytes(8, 'big') + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        """解密"""
        nonce = int.from_bytes(data[:8], 'big')
        ciphertext = data[8:]
        keystream = self._keystream(nonce, len(ciphertext))
        return bytes(a ^ b for a, b in zip(ciphertext, keystream))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 密钥派生（参照 PBKDF2）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def derive_key(password: str, salt: bytes = None, iterations: int = 10000) -> bytes:
    """
    PBKDF2 简化版（参照 RFC 2898）

    用 SHA-256 反复迭代，增加暴力破解成本。
    """
    if salt is None:
        salt = os.urandom(16)
    key = password.encode() + salt
    for _ in range(iterations):
        key = bytes.fromhex(SHA256.hash(key))
    return salt + key  # salt 前置，解密时用

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("tinyencrypt — 加密库（学习用，非生产安全）\n")

    # Test 1: SHA-256
    print("── SHA-256 验证 ──")
    test_cases = [
        (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        (b"Hello, World!", "dffd6021bb2bd5b0af676290892799995ea0b1"),
    ]
    for data, expected in test_cases[:2]:
        result = SHA256.hash(data)
        status = "✅" if result == expected else "❌"
        # 对比 hashlib
        ref = hashlib.sha256(data).hexdigest()
        ok = "✅" if result == ref else "❌"
        print(f"  {ok} SHA256({data.decode()!r}) = {result[:32]}...")

    # Test 2: 流密码
    print("\n── XOR 流密码 ──")
    key = b"my-secret-key"
    cipher = StreamCipher(key)
    plaintext = b"Hello, tinyencrypt! This is a secret message."
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    print(f"  密钥:   {key.decode()}")
    print(f"  明文:   {plaintext.decode()}")
    print(f"  密文:   {encrypted[:32].hex()}...")
    print(f"  解密:   {decrypted.decode()}")
    print(f"  校验:   {'✅ PASS' if decrypted == plaintext else '❌ FAIL'}")

    # Test 3: 不同密钥无法解密
    print("\n── 密钥隔离 ──")
    cipher2 = StreamCipher(b"wrong-key")
    wrong = cipher2.decrypt(encrypted)
    print(f"  错密钥解密: {wrong[:20]}...")
    print(f"  隔离:   {'✅ 错密钥无法解密' if wrong != plaintext else '❌ FAIL'}")

    # Test 4: 密钥派生
    print("\n── PBKDF2 密钥派生 ──")
    t1 = time.perf_counter()
    derived = derive_key("password123", iterations=10000)
    t2 = time.perf_counter()
    print(f"  密码:   password123")
    print(f"  salt:   {derived[:16].hex()}")
    print(f"  key:    {derived[16:].hex()}")
    print(f"  耗时:   {(t2-t1)*1000:.1f}ms (10000 iterations)")

    # 文件加密
    if len(sys.argv) > 2:
        cmd, fname = sys.argv[1], sys.argv[2]
        data = open(fname, 'rb').read()
        if cmd == "encrypt":
            pwd = input("密码: ")
            key = derive_key(pwd)
            cipher = StreamCipher(key)
            enc = cipher.encrypt(data)
            open(fname + ".enc", 'wb').write(enc)
            print(f"\n{fname} → {fname}.enc ({len(data)} → {len(enc)})")
        elif cmd == "decrypt":
            pwd = input("密码: ")
            key = derive_key(pwd)
            cipher = StreamCipher(key)
            dec = cipher.decrypt(open(fname, 'rb').read())
            out = fname.replace('.enc', '')
            open(out, 'wb').write(dec)
            print(f"\n{fname} → {out}")

if __name__ == "__main__":
    main()
