#!/usr/bin/env python3
"""
tinytls — 参照 OpenSSL TLS 1.3 的简化 TLS 实现

参照：OpenSSL / BoringSSL / RFC 8446 (TLS 1.3)
csdiy 对应：network §六(TLS) + tinyencrypt

核心：握手模拟 + 密钥交换概念 + 加密通信
"""
import hashlib, os, struct

class TinyTLS:
    """
    TLS 1.3 握手模拟（教学版，不实现真实加密）

    TLS 1.3 握手（参照 RFC 8446）:
    1. Client → Server: ClientHello（随机数 + 支持的密码套件）
    2. Server → Client: ServerHello + 证书 + Finished
    3. Client → Client: Finished
    总共 1-RTT（TLS 1.2 需 2-RTT）
    """
    def __init__(self):
        self.session_keys = {}
        self.handshake_log = []

    def client_hello(self):
        """模拟 ClientHello（参照 RFC 8446 §4.1.2）"""
        client_random = os.urandom(32)
        cipher_suites = ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"]
        msg = {
            "type": "ClientHello",
            "version": "TLS 1.3",
            "random": client_random.hex(),
            "cipher_suites": cipher_suites,
            "key_share": os.urandom(32).hex(),  # ECDHE 公钥（模拟）
        }
        self.handshake_log.append(f"C→S {msg['type']}: version={msg['version']}, suites={len(cipher_suites)}")
        return msg

    def server_hello(self, client_msg):
        """模拟 ServerHello + 证书"""
        server_random = os.urandom(32)
        shared_secret = hashlib.sha256(
            bytes.fromhex(client_msg["random"]) + server_random +
            bytes.fromhex(client_msg["key_share"])
        ).digest()

        msg = {
            "type": "ServerHello",
            "version": "TLS 1.3",
            "random": server_random.hex(),
            "cipher_suite": client_msg["cipher_suites"][0],
            "certificate": "CN=tiny-server, O=csdiy",
            "key_share": os.urandom(32).hex(),
        }
        self.session_keys["master_secret"] = shared_secret.hex()
        self.handshake_log.append(f"S→C {msg['type']}: suite={msg['cipher_suite']}, cert={msg['certificate']}")
        return msg

    def finished(self, side="client"):
        """Finished 消息（验证握手完整性）"""
        transcript = hashlib.sha256("|".join(self.handshake_log).encode()).hexdigest()
        self.handshake_log.append(f"{'C' if side=='client' else 'S'}→{'S' if side=='client' else 'C'} Finished: transcript={transcript[:16]}...")
        return {"type": "Finished", "verify_data": transcript}

    def handshake(self):
        """完整握手流程"""
        print("tinytls — TLS 1.3 握手模拟\n")
        ch = self.client_hello()
        sh = self.server_hello(ch)
        cf = self.finished("client")
        sf = self.finished("server")

        print("  握手流程:")
        for log in self.handshake_log:
            print(f"  {log}")
        print(f"\n  master_secret: {self.session_keys['master_secret'][:32]}...")
        print(f"  握手消息数: {len(self.handshake_log)}（TLS 1.3 = 1-RTT）")
        print(f"\n  对比 TLS 1.2: 需 2-RTT + RSA（慢）")
        print(f"  TLS 1.3: 1-RTT + ECDHE + 前向安全 ✅")

if __name__ == "__main__":
    tls = TinyTLS()
    tls.handshake()
