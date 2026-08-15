"""
COS 463 / COS 432 Networks and Security（Princeton）
=======================================================
覆盖主题：
- TCP 状态机（三次握手 + 四次挥手 + TIME_WAIT）
- TLS 1.3 握手（简化版 1-RTT）
- RSA + Diffie-Hellman 密钥交换
- ARP 欺骗原理（中间人攻击演示）

核心论文/教材：
- Postel 1981 "RFC 793: Transmission Control Protocol"
- Rescorla 2018 "RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3"
- Rivest, Shamir, Adleman 1978 "A Method for Obtaining Digital Signatures" CACM (RSA)
- Diffie & Hellman 1976 "New Directions in Cryptography" IEEE Trans IT (DH)

本文件实现：
1. TCP 状态机模拟器（连接建立/关闭）
2. TLS 1.3 握手流程演示
3. RSA 加密/解密 + 数字签名
4. Diffie-Hellman 密钥交换
5. ARP 欺骗攻击模拟

运行：
    python net_sec.py
"""
from __future__ import annotations
import random
import math
from dataclasses import dataclass


# ================================================================
# 1. TCP State Machine
# ================================================================

class TCPStateMachine:
    """TCP finite state machine (RFC 793).

    States: CLOSED, LISTEN, SYN_SENT, SYN_RCVD, ESTABLISHED,
            FIN_WAIT_1, FIN_WAIT_2, CLOSING, TIME_WAIT,
            CLOSE_WAIT, LAST_ACK
    """

    STATES = [
        "CLOSED", "LISTEN", "SYN_SENT", "SYN_RCVD", "ESTABLISHED",
        "FIN_WAIT_1", "FIN_WAIT_2", "CLOSING", "TIME_WAIT",
        "CLOSE_WAIT", "LAST_ACK"
    ]

    def __init__(self, role: str = "server"):
        self.state = "CLOSED"
        self.role = role
        self.transitions = []
        self.time_wait_counter = 0

    def event(self, evt: str) -> str:
        """Process TCP event, return new state."""
        old = self.state
        # Server-side transitions
        if self.state == "CLOSED" and evt == "PASSIVE_OPEN":
            self.state = "LISTEN"
        elif self.state == "LISTEN" and evt == "RCV_SYN":
            self.state = "SYN_RCVD"
        elif self.state == "SYN_RCVD" and evt == "RCV_ACK":
            self.state = "ESTABLISHED"
        # Client-side transitions
        elif self.state == "CLOSED" and evt == "ACTIVE_OPEN":
            self.state = "SYN_SENT"
        elif self.state == "SYN_SENT" and evt == "RCV_SYN_ACK":
            self.state = "ESTABLISHED"
        # Close transitions
        elif self.state == "ESTABLISHED" and evt == "CLOSE":
            self.state = "FIN_WAIT_1"
        elif self.state == "FIN_WAIT_1" and evt == "RCV_ACK":
            self.state = "FIN_WAIT_2"
        elif self.state == "FIN_WAIT_2" and evt == "RCV_FIN":
            self.state = "TIME_WAIT"
        elif self.state == "TIME_WAIT" and evt == "TIMEOUT":
            self.state = "CLOSED"
        elif self.state == "ESTABLISHED" and evt == "RCV_FIN":
            self.state = "CLOSE_WAIT"
        elif self.state == "CLOSE_WAIT" and evt == "CLOSE":
            self.state = "LAST_ACK"
        elif self.state == "LAST_ACK" and evt == "RCV_ACK":
            self.state = "CLOSED"

        self.transitions.append((old, evt, self.state))
        return self.state


def simulate_tcp_handshake():
    """Simulate 3-way handshake + 4-way close."""
    client = TCPStateMachine("client")
    server = TCPStateMachine("server")

    # 3-way handshake
    print("   --- 三次握手 ---")
    events = [
        (client, "ACTIVE_OPEN", "Client → SYN → Server"),
        (server, "RCV_SYN", "Server 收到 SYN → SYN+ACK"),
        (client, "RCV_SYN_ACK", "Client 收到 SYN+ACK → ACK"),
        (server, "RCV_ACK", "Server 收到 ACK"),
    ]
    for sm, evt, desc in events:
        old = sm.state
        sm.event(evt)
        print(f"   {desc}: {old} → {sm.state}")

    print(f"   Client state: {client.state}, Server state: {server.state}")
    print(f"   连接建立: {client.state == 'ESTABLISHED' and server.state == 'ESTABLISHED'}")

    # 4-way close
    print("   --- 四次挥手 ---")
    events = [
        (client, "CLOSE", "Client → FIN"),
        (server, "RCV_FIN", "Server 收到 FIN → ACK"),
        (server, "CLOSE", "Server → FIN"),
        (client, "RCV_FIN", "Client 收到 FIN → ACK"),
        (client, "TIMEOUT", "Client TIME_WAIT → 2*MSL timeout"),
    ]
    for sm, evt, desc in events:
        old = sm.state
        sm.event(evt)
        print(f"   {desc}: {old} → {sm.state}")


# ================================================================
# 2. TLS 1.3 Handshake (simplified)
# ================================================================

def simulate_tls13_handshake():
    """Simulate TLS 1.3 1-RTT handshake (conceptual)."""
    steps = [
        ("ClientHello",
         "Client → Server: supported_versions, cipher_suites, key_share(X25519), client_random"),
        ("ServerHello",
         "Server → Client: selected_cipher, key_share(X25519), server_random"),
        ("EncryptedExtensions",
         "Server → Client: (encrypted) ALPN, SNI confirmation"),
        ("Certificate",
         "Server → Client: (encrypted) X.509 certificate chain"),
        ("CertificateVerify",
         "Server → Client: (encrypted) signature over handshake transcript"),
        ("Finished",
         "Server → Client: (encrypted) HMAC of transcript"),
        ("Finished",
         "Client → Server: (encrypted) HMAC of transcript"),
        ("ApplicationData",
         "Bidirectional encrypted data (1-RTT complete)"),
    ]
    print("   TLS 1.3 握手流程 (1-RTT):")
    for i, (name, desc) in enumerate(steps):
        arrow = "→" if "Client" in desc.split(":")[0] else "←"
        print(f"   [{i+1}] {name} {arrow} {desc}")


# ================================================================
# 3. RSA Encryption
# ================================================================

def is_prime(n: int, k: int = 20) -> bool:
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
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


def gen_prime(bits: int = 16) -> int:
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(p):
            return p


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def mod_inverse(e, phi):
    g, x, _ = extended_gcd(e % phi, phi)
    if g != 1:
        raise ValueError("no inverse")
    return x % phi


class RSA:
    """RSA cryptosystem (small keys for demo)."""

    @staticmethod
    def keygen(bits: int = 16) -> dict:
        p, q = gen_prime(bits), gen_prime(bits)
        while p == q:
            q = gen_prime(bits)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        if math.gcd(e, phi) != 1:
            e = 3
        d = mod_inverse(e, phi)
        return {"public": (e, n), "private": (d, n), "p": p, "q": q}

    @staticmethod
    def encrypt(m: int, pub: tuple) -> int:
        e, n = pub
        return pow(m, e, n)

    @staticmethod
    def decrypt(c: int, priv: tuple) -> int:
        d, n = priv
        return pow(c, d, n)

    @staticmethod
    def sign(m: int, priv: tuple) -> int:
        d, n = priv
        return pow(m, d, n)

    @staticmethod
    def verify(m: int, sig: int, pub: tuple) -> bool:
        e, n = pub
        return pow(sig, e, n) == m


# ================================================================
# 4. Diffie-Hellman Key Exchange
# ================================================================

def diffie_hellman(p: int, g: int) -> tuple[int, int, int]:
    """DH key exchange. Returns (Alice_shared, Bob_shared, match)."""
    a = random.randint(2, p - 2)  # Alice's private key
    b = random.randint(2, p - 2)  # Bob's private key
    A = pow(g, a, p)  # Alice's public key
    B = pow(g, b, p)  # Bob's public key
    alice_shared = pow(B, a, p)
    bob_shared = pow(A, b, p)
    return alice_shared, bob_shared, alice_shared == bob_shared


# ================================================================
# 5. ARP Spoofing Simulation
# ================================================================

@dataclass
class Host:
    name: str
    ip: str
    mac: str


class ARPTableSimulator:
    """Simulate ARP table and ARP spoofing attack."""

    def __init__(self):
        self.arp_table: dict[str, str] = {}  # IP → MAC
        self.attacker_log = []

    def learn(self, ip: str, mac: str):
        """Host sends ARP reply, all hosts update their table."""
        self.arp_table[ip] = mac

    def spoof(self, victim_ip: str, gateway_ip: str, attacker_mac: str):
        """Attacker sends forged ARP reply to victim:
        'I am the gateway!' (gateway_ip → attacker_mac)
        """
        self.arp_table[gateway_ip] = attacker_mac
        self.attacker_log.append(
            f"攻击者({attacker_mac}) 告诉 {victim_ip}: 我是网关 {gateway_ip}")


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 463/432: Networks & Security Demo")
    print("=" * 60)
    random.seed(42)

    # --- 1. TCP State Machine ---
    print("\n📋 1. TCP 状态机")
    simulate_tcp_handshake()

    # --- 2. TLS 1.3 ---
    print("\n📋 2. TLS 1.3 握手")
    simulate_tls13_handshake()

    # --- 3. RSA ---
    print("\n📋 3. RSA 加密/签名")
    keys = RSA.keygen(bits=32)
    pub, priv = keys["public"], keys["private"]
    print(f"   p={keys['p']}, q={keys['q']}")
    print(f"   n={pub[1]}, e={pub[0]}, d=***")

    plaintext = 123456
    ciphertext = RSA.encrypt(plaintext, pub)
    decrypted = RSA.decrypt(ciphertext, priv)
    print(f"   明文: {plaintext}")
    print(f"   加密: {ciphertext}")
    print(f"   解密: {decrypted} ✓" if decrypted == plaintext else f"   解密失败 ✗")

    # Digital signature
    sig = RSA.sign(plaintext, priv)
    valid = RSA.verify(plaintext, sig, pub)
    print(f"   签名验证: {'✓' if valid else '✗'}")

    # --- 4. Diffie-Hellman ---
    print("\n📋 4. Diffie-Hellman 密钥交换")
    # Use known prime (small for demo)
    p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1  # truncated small prime
    p = 8191  # use Mersenne prime for demo
    g = 5
    alice_key, bob_key, match = diffie_hellman(p, g)
    print(f"   公开参数: p={p}, g={g}")
    print(f"   Alice 计算的共享密钥: {alice_key}")
    print(f"   Bob   计算的共享密钥: {bob_key}")
    print(f"   密钥一致: {'✓' if match else '✗'}")
    print(f"   → 窃听者只知道 p, g, A, B，无法算出共享密钥（离散对数难题）")

    # --- 5. ARP Spoofing ---
    print("\n📋 5. ARP 欺骗模拟")
    victim = Host("Victim", "192.168.1.10", "AA:BB:CC:00:00:10")
    gateway = Host("Gateway", "192.168.1.1", "AA:BB:CC:00:00:01")
    attacker = Host("Attacker", "192.168.1.99", "AA:BB:CC:00:00:99")

    arp = ARPTableSimulator()
    # Normal learning
    arp.learn(gateway.ip, gateway.mac)
    print(f"   正常 ARP 表: {victim.ip} → 网关 {arp.arp_table[gateway.ip]}")

    # Attack
    arp.spoof(victim.ip, gateway.ip, attacker.mac)
    print(f"   攻击后 ARP 表: 网关 {gateway.ip} → {arp.arp_table[gateway.ip]}")
    print(f"   → Victim 现在把所有发往网关的流量发给攻击者！")
    print(f"   防御: 静态 ARP 绑定 / DAI (Dynamic ARP Inspection)")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    print(f"   RSA 用小素数(32-bit)即可被破解——但真实 RSA 用 2048+ bit")
    print(f"   2048-bit RSA 的 n 有 ~617 位十进制数字")
    print(f"   → 分解这么大的数，即使全球算力也要数十亿年")
    print(f"   DH 的安全性也基于离散对数：已知 g^x mod p 求 x 是 NP-hard")
    print(f"   TLS 1.3 把握手从 TLS 1.2 的 2-RTT 减到 1-RTT，")
    print(f"   还支持 0-RTT 恢复（但有重放攻击风险）")

    print("\n✅ COS 463/432 Demo 完成！")


if __name__ == "__main__":
    demo()
