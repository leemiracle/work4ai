"""
CS251 + CS258 - Cryptocurrencies + Quantum Cryptography
覆盖课程模块：CS251 RSA / 哈希 / 数字签名 + CS258 量子基础

实现内容：
1. RSA 从零实现（用小素数，教学）
2. SHA-256 简化版
3. 数字签名
4. 区块链（简化比特币）
5. Diffie-Hellman 密钥交换

参考：Boneh CS251 / Zhandry CS258
"""
from __future__ import annotations
import math
import hashlib
import random
from dataclasses import dataclass


# ============ 1. RSA ============

def is_prime(n: int, k: int = 5) -> bool:
    """Miller-Rabin 素数测试"""
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randint(2, n - 2)
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


def gen_prime(bits: int = 8) -> int:
    """生成素数（教学用小素数）"""
    while True:
        n = random.randint(2**(bits-1), 2**bits - 1)
        if n % 2 == 1 and is_prime(n):
            return n


def modinv(a: int, m: int) -> int:
    """扩展欧几里得求模逆"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("无模逆")
    return x % m


def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


@dataclass
class RSAKey:
    n: int
    e: int  # 公钥指数
    d: int = 0  # 私钥（0 if public only)
    p: int = 0
    q: int = 0


def rsa_keygen(bits: int = 8) -> tuple[RSAKey, RSAKey]:
    """生成 RSA 公钥/私钥对"""
    p, q = gen_prime(bits), gen_prime(bits)
    while p == q:
        q = gen_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while math.gcd(e, phi) != 1:
        e += 2
    d = modinv(e, phi)
    return RSAKey(n, e, 0, p, q), RSAKey(n, e, d, p, q)  # public, private


def rsa_encrypt(m: int, pub: RSAKey) -> int:
    """m^e mod n"""
    return pow(m, pub.e, pub.n)


def rsa_decrypt(c: int, priv: RSAKey) -> int:
    """c^d mod n"""
    return pow(c, priv.d, priv.n)


def rsa_sign(m: int, priv: RSAKey) -> int:
    """数字签名 = 用私钥加密哈希"""
    h = simple_hash(str(m)) % priv.n
    return pow(h, priv.d, priv.n)


def rsa_verify(m: int, sig: int, pub: RSAKey) -> bool:
    """验证签名"""
    h_expected = simple_hash(str(m)) % pub.n
    h_got = pow(sig, pub.e, pub.n)
    return h_expected == h_got


# ============ 2. SHA-256 简化（用 stdlib）============

def simple_hash(data: str) -> int:
    """简化的 SHA-256 → 整数"""
    h = hashlib.sha256(data.encode()).hexdigest()
    return int(h, 16)


# ============ 3. 区块链 ============

@dataclass
class Block:
    index: int
    data: str
    prev_hash: str
    nonce: int = 0

    def compute_hash(self) -> str:
        return hashlib.sha256(
            f"{self.index}{self.data}{self.prev_hash}{self.nonce}".encode()
        ).hexdigest()


class Blockchain:
    """简化比特币"""

    def __init__(self, difficulty: int = 2):
        self.chain: list[Block] = []
        self.difficulty = difficulty
        # 创世块
        genesis = Block(0, "Genesis", "0")
        genesis.nonce = self.mine(genesis)
        self.chain.append(genesis)

    def mine(self, block: Block) -> int:
        """PoW: 找 nonce 使 hash 前 difficulty 位为 0"""
        prefix = "0" * self.difficulty
        nonce = 0
        while True:
            block.nonce = nonce
            h = block.compute_hash()
            if h.startswith(prefix):
                return nonce
            nonce += 1

    def add_block(self, data: str) -> Block:
        prev = self.chain[-1]
        block = Block(len(self.chain), data, prev.compute_hash())
        block.nonce = self.mine(block)
        self.chain.append(block)
        return block

    def verify(self) -> bool:
        """验证整条链"""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.prev_hash != prev.compute_hash():
                return False
            if not curr.compute_hash().startswith("0" * self.difficulty):
                return False
        return True


# ============ 4. Diffie-Hellman ============

def dh_demo():
    """Diffie-Hellman 密钥交换"""
    # 公开参数（小数字教学）
    p = 23  # 素数
    g = 5   # 生成元
    # Alice 私钥
    a = random.randint(1, p-1)
    A = pow(g, a, p)
    # Bob 私钥
    b = random.randint(1, p-1)
    B = pow(g, b, p)
    # 共享密钥
    s_alice = pow(B, a, p)
    s_bob = pow(A, b, p)
    return {"alice_pub": A, "bob_pub": B,
            "alice_secret": a, "bob_secret": b,
            "shared_alice": s_alice, "shared_bob": s_bob,
            "match": s_alice == s_bob}


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS251 + CS258: Crypto & Blockchain")
    print("=" * 60)

    # 1. RSA
    print("\n📋 1. RSA 从零实现")
    pub, priv = rsa_keygen(bits=10)
    print(f"   p={priv.p}, q={priv.q}, n={priv.n}, e={pub.e}, d={priv.d}")
    m = 42
    c = rsa_encrypt(m, pub)
    decrypted = rsa_decrypt(c, priv)
    print(f"   原文 m = {m}")
    print(f"   密文 c = {c}")
    print(f"   解密  = {decrypted} {'✓' if decrypted == m else '✗'}")

    # 2. 数字签名
    print("\n📋 2. RSA 数字签名")
    sig = rsa_sign(m, priv)
    valid = rsa_verify(m, sig, pub)
    print(f"   消息 m={m}")
    print(f"   签名 sig={sig}")
    print(f"   验证: {valid}")
    print(f"   篡改消息后验证: {rsa_verify(43, sig, pub)}")

    # 3. 区块链
    print("\n📋 3. 简化区块链（PoW）")
    bc = Blockchain(difficulty=2)
    for tx in ["Alice→Bob 5 BTC", "Bob→Carol 2 BTC", "Carol→Dave 1 BTC"]:
        block = bc.add_block(tx)
        print(f"   Block #{block.index}: {tx}, nonce={block.nonce}, hash={block.compute_hash()[:16]}...")
    print(f"   链有效: {bc.verify()}")

    # 篡改测试
    print("\n   篡改测试:")
    bc.chain[1].data = "Alice→Eve 999 BTC"
    print(f"   篡改后链有效: {bc.verify()}")

    # 4. Diffie-Hellman
    print("\n📋 4. Diffie-Hellman 密钥交换")
    result = dh_demo()
    print(f"   公开: p=23, g=5")
    print(f"   Alice: 私钥 {result['alice_secret']}, 公钥 {result['alice_pub']}")
    print(f"   Bob:   私钥 {result['bob_secret']}, 公钥 {result['bob_pub']}")
    print(f"   共享密钥: Alice 算出 {result['shared_alice']}, Bob 算出 {result['shared_bob']}")
    print(f"   密钥匹配: {result['match']}")

    print("\n✅ CS251 + CS258 完成！")


if __name__ == "__main__":
    demo()
