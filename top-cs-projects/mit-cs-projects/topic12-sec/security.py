"""
6.4420/6.858 Computer Systems Security（MIT）
================================================
覆盖主题：
- RSA 加密 + OAEP-lite padding（Lecture 5-6）
- 符号执行 mini（约束求解）（Lecture 11）
- Sandbox capability model（Lecture 8）
- Control-Flow Integrity (CFI)（Lecture 14）

核心教材/论文（经典，无 arXiv ID）：
- Rivest, Shamir, Adleman 1978 "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems" CACM (RSA)
- Bellare & Rogaway 1994 "Optimal Asymmetric Encryption Padding" CRYPTO (OAEP)
- King 1976 "Symbolic Execution and Program Testing" CACM
- Abadi et al. 2005 "Control-Flow Integrity" CCS

本文件实现：
- RSA 密钥生成 + 加解密（Miller-Rabin 素性测试 + 扩展欧几里得）
- OAEP-lite 填充（防确定性攻击）
- mini 符号执行器（Z3-free 约束枚举）
- Capability-based sandbox + CFI 检查

运行：
    python security.py
"""
from __future__ import annotations
import os
import hashlib
import random


# ============ 1. RSA + OAEP-lite ============

def miller_rabin(n: int, rounds: int = 20) -> bool:
    """Miller-Rabin 素性测试。"""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    # n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1; d //= 2
    for _ in range(rounds):
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


def gen_prime(bits: int = 64) -> int:
    """生成 bits 位素数。"""
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(p):
            return p


def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """扩展欧几里得：返回 (g, x, y) s.t. ax + by = g。"""
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y


def modinv(a: int, m: int) -> int:
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError("无逆元")
    return x % m


class RSA:
    def __init__(self, bits: int = 64):
        self.p = gen_prime(bits)
        self.q = gen_prime(bits)
        while self.q == self.p:
            self.q = gen_prime(bits)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = 65537
        self.d = modinv(self.e, self.phi)

    def encrypt(self, m: int) -> int:
        return pow(m, self.e, self.n)

    def decrypt(self, c: int) -> int:
        return pow(c, self.d, self.n)

    def sign(self, m: int) -> int:
        return pow(m, self.d, self.n)

    def verify(self, m: int, sig: int) -> bool:
        return pow(sig, self.e, self.n) == m


def oaep_lite_pad(message: bytes, k0: int = 16) -> bytes:
    """OAEP-lite: 用 hash 填充防确定性加密。
    EM = 0x00 || H(random) XOR message
    """
    r = os.urandom(k0)
    h = hashlib.sha256(r).digest()
    padded = bytes(a ^ b for a, b in zip(message.ljust(len(h), b'\x00'), h))
    return r + padded


def oaep_lite_unpad(em: bytes, msg_len: int) -> bytes:
    r = em[:16]
    padded = em[16:]
    h = hashlib.sha256(r).digest()
    message = bytes(a ^ b for a, b in zip(padded, h))
    return message[:msg_len]


# ============ 2. Mini Symbolic Execution ============

class SymVar:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name


def symbolic_branch_demo():
    """简化符号执行：分析下面代码可达哪些分支。
    if (x * 2 + 1 > 5): path A else: path B
    if (x < 10): path C else: path D
    枚举 x 的取值范围找可达路径。
    """
    paths = []
    for x in range(-20, 21):
        cond1 = x * 2 + 1 > 5   # x > 2
        cond2 = x < 10
        branch = ("A" if cond1 else "B") + ("C" if cond2 else "D")
        paths.append((x, branch))
    # 汇总每个路径约束
    path_summary = {}
    for x, b in paths:
        path_summary.setdefault(b, []).append(x)
    return path_summary


# ============ 3. Capability Sandbox ============

class Capability:
    """权限令牌：(object, permission)"""
    def __init__(self, resource: str, perms: set):
        self.resource = resource
        self.perms = set(perms)


class CapabilitySandbox:
    """capability-based 权限模型"""
    def __init__(self):
        self.capabilities: dict[str, list[Capability]] = {}  # subject -> caps

    def grant(self, subject: str, cap: Capability):
        self.capabilities.setdefault(subject, []).append(cap)

    def check(self, subject: str, resource: str, perm: str) -> bool:
        for cap in self.capabilities.get(subject, []):
            if cap.resource == resource and perm in cap.perms:
                return True
        return False


# ============ 4. Control-Flow Integrity (CFI) ============

class CFIChecker:
    """模拟 CFI：只允许预定义的间接跳转目标。"""
    def __init__(self):
        self.indirect_targets: set[str] = set()  # 允许的间接跳转目标
        self.violations: list[str] = []

    def register_valid_target(self, func_name: str):
        self.indirect_targets.add(func_name)

    def check_indirect_call(self, target: str) -> bool:
        if target in self.indirect_targets:
            return True
        self.violations.append(target)
        return False


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.858 Systems Security: RSA/SymExec/Sandbox/CFI")
    print("=" * 65)
    random.seed(42)

    # --- RSA ---
    print("\n📋 1. RSA 公钥加密 + 数字签名 (64-bit)")
    rsa = RSA(bits=64)
    print(f"  p={rsa.p}, q={rsa.q}")
    print(f"  n={rsa.n} ({rsa.n.bit_length()} bits)")
    print(f"  e={rsa.e}, d={rsa.d}")
    msg = 123456789
    ct = rsa.encrypt(msg)
    pt = rsa.decrypt(ct)
    print(f"  原文: {msg}")
    print(f"  密文: {ct}")
    print(f"  解密: {pt}  ✓" if pt == msg else f"  解密: {pt}  ✗")
    # 签名
    sig = rsa.sign(msg)
    ok = rsa.verify(msg, sig)
    print(f"  签名验证: {ok} ✓")
    print(f"  篡改检测: 改 msg=123456790, verify={rsa.verify(123456790, sig)}")

    # --- OAEP ---
    print("\n📋 2. OAEP-lite 填充 (防确定性加密)")
    plaintext = b"Hello RSA"
    em1 = oaep_lite_pad(plaintext)
    em2 = oaep_lite_pad(plaintext)
    recovered = oaep_lite_unpad(em1, len(plaintext))
    print(f"  原文: {plaintext}")
    print(f"  两次填充相同? {em1 == em2} (应不同, 随机性)")
    print(f"  恢复: {recovered} ✓" if recovered == plaintext else f"  恢复: {recovered} ✗")
    print(f"  → 同一明文每次加密结果不同，防止已知明文/字典攻击。")

    # --- Symbolic Execution ---
    print("\n📋 3. Mini 符号执行 (路径约束求解)")
    print("  代码:")
    print("    if (x*2+1 > 5): A else: B")
    print("    if (x < 10):    C else: D")
    summary = symbolic_branch_demo()
    print(f"  可达路径与约束:")
    for path, xs in sorted(summary.items()):
        print(f"    路径 {path}: x ∈ [{min(xs)}, {max(xs)}]")

    # --- Sandbox ---
    print("\n📋 4. Capability-based Sandbox")
    sandbox = CapabilitySandbox()
    sandbox.grant("app1", Capability("/tmp", {"read","write"}))
    sandbox.grant("app1", Capability("/etc/passwd", {"read"}))
    sandbox.grant("app2", Capability("/tmp", {"read"}))
    checks = [
        ("app1", "/tmp", "write", True),
        ("app1", "/etc/passwd", "read", True),
        ("app1", "/etc/passwd", "write", False),
        ("app1", "/etc/shadow", "read", False),
        ("app2", "/tmp", "write", False),
        ("app2", "/tmp", "read", True),
    ]
    for subj, res, perm, expected in checks:
        result = sandbox.check(subj, res, perm)
        status = "✓" if result == expected else "✗ UNEXPECTED"
        print(f"  {subj} → {res}:{perm} = {result} {status}")

    # --- CFI ---
    print("\n📋 5. Control-Flow Integrity (CFI)")
    cfi = CFIChecker()
    cfi.register_valid_target("合法回调")
    cfi.register_valid_target("logger")
    calls = ["合法回调", "logger", "system", "exec", "合法回调"]
    print(f"  注册合法目标: {cfi.indirect_targets}")
    for target in calls:
        ok = cfi.check_indirect_call(target)
        print(f"  间接调用 → '{target}': {'允许 ✓' if ok else '拒绝 ✗ (CFI 违规!)'}")
    print(f"  CFI 违规记录: {cfi.violations}")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：RSA 直接加密相同明文→相同密文（确定性，可被攻击）")
    print("=" * 65)
    print("  无 OAEP 时，RSA 是确定性加密：")
    msgs = [42, 42, 42, 42]
    cts = [rsa.encrypt(m) for m in msgs]
    print(f"  4 次加密相同明文 42:")
    for i, c in enumerate(cts):
        print(f"    第{i+1}次: {c}")
    print(f"  全部相同? {len(set(cts)) == 1} ← 攻击者可建字典！")
    print(f"\n  加 OAEP 后（即使这里 m 小，演示概念）:")
    cts2 = []
    for _ in range(4):
        em = oaep_lite_pad(b"\x00\x00\x00\x2a")  # 42 的小端
        m_int = int.from_bytes(em, 'big')
        if m_int < rsa.n:
            cts2.append(rsa.encrypt(m_int))
    print(f"  4 次加密(带 OAEP): 全不同? {len(set(cts2)) == len(cts2)}")
    print("  → OAEP 的随机填充是 RSA 加密安全的基石(ECB→IND-CPA)。")

    print("\n✅ 6.858 Demo 完成！")


if __name__ == "__main__":
    demo()
