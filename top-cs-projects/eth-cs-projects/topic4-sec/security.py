"""
Information Security — ETH Zürich
================================
覆盖主题：
- 分组密码（mini-Feistel 网络）
- RSA 公钥加密 + 数字签名
- MAC / HMAC
- TLS 握手模拟
- 零知识证明（Schnorr 协议）

核心教材/论文：
- Rivest, Shamir, Adleman "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems" CACM 21(2): 120-126 (1978) — RSA
- Schnorr "Efficient Signature Generation by Smart Cards" J. Cryptology 4(3): 161-174 (1991) — Schnorr
- Bellare, Canetti, Krawczyk "Keying Hash Functions for Message Authentication" CRYPTO 1996 — HMAC
- Dierks & Rescorla "The Transport Layer Security (TLS) Protocol Version 1.2" RFC 5246 (2008)

本文件实现：
1. mini-Feistel 加密（4 轮）
2. RSA 密钥生成 / 加密 / 签名
3. HMAC-SHA256 简化版（用 hashlib）
4. TLS 1.2 握手状态机
5. Schnorr 零知识协议（3 轮交互）

运行：
    python security.py
"""
from __future__ import annotations
import hashlib
import random


# ============ 0. 数论辅助 ============

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if a >= n:
            continue
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


def gen_prime(bits: int = 32) -> int:
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(p):
            return p


def modinv(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("无逆元")
    return x % m


def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


# ============ 1. Mini-Feistel 分组密码 ============

def feistel_f(R: int, key: int) -> int:
    """轮函数 F（简化）"""
    return ((R * key + 0x9E3779B9) ^ (R >> 3)) & 0xFFFFFFFF


def feistel_encrypt(block: tuple[int, int], keys: list[int]) -> tuple[int, int]:
    """Feistel 加密：L0R0 → ... → LnRn"""
    L, R = block
    for k in keys:
        L, R = R, L ^ feistel_f(R, k)
    return L, R


def feistel_decrypt(block: tuple[int, int], keys: list[int]) -> tuple[int, int]:
    L, R = block
    for k in reversed(keys):
        L, R = R ^ feistel_f(L, k), L
    return L, R


# ============ 2. RSA ============

class RSA:
    def __init__(self, bits: int = 32):
        self.p = gen_prime(bits)
        self.q = gen_prime(bits)
        while self.q == self.p:
            self.q = gen_prime(bits)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = 65537
        while extended_gcd(self.e, self.phi)[0] != 1:
            self.e += 2
        self.d = modinv(self.e, self.phi)

    def encrypt(self, m: int) -> int:
        return pow(m, self.e, self.n)

    def decrypt(self, c: int) -> int:
        return pow(c, self.d, self.n)

    def sign(self, m: int) -> int:
        h = int(hashlib.sha256(str(m).encode()).hexdigest(), 16) % self.n
        return pow(h, self.d, self.n)

    def verify(self, m: int, sig: int, pub_n: int, pub_e: int) -> bool:
        h = int(hashlib.sha256(str(m).encode()).hexdigest(), 16) % pub_n
        return pow(sig, pub_e, pub_n) == h


# ============ 3. HMAC ============

def hmac(key: bytes, msg: bytes) -> bytes:
    """HMAC-SHA256 (RFC 2104)"""
    block_size = 64
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    key = key + b'\x00' * (block_size - len(key))
    ipad = bytes(b ^ 0x36 for b in key)
    opad = bytes(b ^ 0x5c for b in key)
    inner = hashlib.sha256(ipad + msg).digest()
    return hashlib.sha256(opad + inner).digest()


# ============ 4. TLS 握手模拟 ============

def tls_handshake_sim():
    """
    TLS 1.2 握手步骤：
    1. ClientHello (随机数, 支持的密码套件)
    2. ServerHello (随机数, 选定套件)
    3. Server 证书 + ServerKeyExchange
    4. ServerHelloDone
    5. ClientKeyExchange (预主密钥加密)
    6. 生成主密钥
    7. Finished (HMAC 校验)
    """
    log = []
    client_random = random.getrandbits(256)
    server_random = random.getrandbits(256)
    log.append(f"1. ClientHello: random=0x{client_random:064x}, suites=[TLS_RSA_AES_256]")

    log.append(f"2. ServerHello: random=0x{server_random:064x}, chosen=TLS_RSA_AES_256")
    log.append("3. Certificate: CN=eth-zurich.ch (RSA-2048)")
    log.append("4. ServerHelloDone")

    pre_master = random.getrandbits(384)
    log.append("5. ClientKeyExchange: pre_master_secret (RSA 加密)")

    master = hashlib.sha256(
        pre_master.to_bytes(48, 'big') +
        b'master secret' +
        client_random.to_bytes(32, 'big') +
        server_random.to_bytes(32, 'big')
    ).digest()
    log.append(f"6. master_secret = PRF(pre_master, 'master secret', rand_c||rand_s)")

    finished_hmac = hmac(master, b"client finished")
    log.append(f"7. Finished: verify_data = HMAC(master, 'client finished')[:8]={finished_hmac[:8].hex()}")
    return log


# ============ 5. Schnorr 零知识协议 ============

class SchnorrProver:
    """
    Schnorr 协议（Σ-protocol）证明知道 x 使得 y = g^x mod p，
    不泄露 x。

    3 轮：
    1. Prover → Verifier: 承诺 t = g^r mod p
    2. Verifier → Prover: 挑战 c (随机)
    3. Prover → Verifier: 响应 s = r + c·x mod q
    验证: g^s = t · y^c mod p
    """

    def __init__(self, p: int, q: int, g: int, x: int):
        self.p, self.q, self.g, self.x = p, q, g, x
        self.y = pow(g, x, p)

    def commit(self) -> int:
        self.r = random.randint(1, self.q - 1)
        self.t = pow(self.g, self.r, self.p)
        return self.t

    def respond(self, c: int) -> int:
        return (self.r + c * self.x) % self.q


def schnorr_verify(p, q, g, y, t, c, s) -> bool:
    """验证 g^s ≡ t · y^c (mod p)"""
    left = pow(g, s, p)
    right = (t * pow(y, c, p)) % p
    return left == right


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Information Security: Feistel + RSA + HMAC + TLS + ZKP")
    print("=" * 60)
    random.seed(42)

    # 1. Feistel
    print("\n📋 1. Mini-Feistel 分组密码 (4 轮)")
    keys = [0xDEADBEEF, 0xCAFEBABE, 0xFEEDFACE, 0x12345678]
    plaintext = (0x0123ABCD, 0x4567EFFF)
    ct = feistel_encrypt(plaintext, keys)
    pt2 = feistel_decrypt(ct, keys)
    print(f"   明文:  (0x{plaintext[0]:08X}, 0x{plaintext[1]:08X})")
    print(f"   密文:  (0x{ct[0]:08X}, 0x{ct[1]:08X})")
    print(f"   解密:  (0x{pt2[0]:08X}, 0x{pt2[1]:08X})  正确: {pt2 == plaintext}")

    # 2. RSA
    print("\n📋 2. RSA 加密 + 签名")
    rsa = RSA(bits=32)
    print(f"   p={rsa.p}, q={rsa.q}, n={rsa.n}")
    msg = 12345
    enc = rsa.encrypt(msg)
    dec = rsa.decrypt(enc)
    print(f"   加密 {msg} → {enc} → 解密 {dec}  正确: {dec == msg}")

    sig = rsa.sign(msg)
    ok = rsa.verify(msg, sig, rsa.n, rsa.e)
    print(f"   签名验证: {'✓' if ok else '✗'}")
    tampered_ok = rsa.verify(msg + 1, sig, rsa.n, rsa.e)
    print(f"   篡改消息后验证: {'✓(错!)' if tampered_ok else '✓ 正确拒绝'}")

    # 3. HMAC
    print("\n📋 3. HMAC-SHA256")
    key = b"secret_key"
    msg = b"Hello ETH Security!"
    tag = hmac(key, msg)
    print(f"   HMAC = {tag.hex()[:32]}...")
    ok1 = hmac(key, msg) == tag
    ok2 = hmac(key, b"tampered") != tag
    print(f"   原始验证: {ok1}, 篡改检测: {ok2}")

    # 4. TLS 握手
    print("\n📋 4. TLS 1.2 握手")
    for line in tls_handshake_sim():
        print(f"   {line}")

    # 5. Schnorr ZKP
    print("\n📋 5. Schnorr 零知识证明")
    q = gen_prime(16)
    # 找一个 p = kq+1 的素数
    k = 2
    while True:
        p = k * q + 1
        if is_prime(p):
            break
        k += 1
    g = 2
    while pow(g, q, p) != 1:
        g += 1
    x = random.randint(1, q - 1)  # 秘密

    prover = SchnorrProver(p, q, g, x)
    t = prover.commit()
    c = random.randint(1, q - 1)  # 挑战
    s = prover.respond(c)
    ok = schnorr_verify(p, q, g, prover.y, t, c, s)
    print(f"   y = g^x mod p (公开), x (秘密) = {x}")
    print(f"   承诺 t=g^r, 挑战 c={c}, 响应 s=r+c·x")
    print(f"   验证 g^s ≡ t·y^c: {'✓ 证明成功(不泄露 x)' if ok else '✗'}")

    # 反直觉
    print("\n💡 反直觉发现：Feistel 网络的解密 = 加密密钥逆序")
    print(f"   加密用 keys[0,1,2,3]，解密用 keys[3,2,1,0]")
    print(f"   → 硬件只需一个电路，正反调用即可加解密（DES/AES 设计精髓）")

    print("\n✅ Information Security 完成！")


if __name__ == "__main__":
    demo()
