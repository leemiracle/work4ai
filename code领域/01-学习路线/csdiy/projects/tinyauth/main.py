#!/usr/bin/env python3
"""tinyauth — 参照 JWT/OAuth2 的认证授权
参照：JWT (RFC 7519) / OAuth2 / Auth0
csdiy 对应：tinyencrypt + tinyhttpd + 安全
核心：JWT 签发+验证 + RBAC 权限"""
import hashlib, hmac, json, base64, time

class TinyJWT:
    """JWT 实现（参照 RFC 7519）
    Header.Payload.Signature（base64url 编码）"""
    def __init__(self, secret): self.secret = secret.encode()
    def encode(self, payload, exp=3600):
        payload["exp"] = int(time.time()) + exp
        header = {"alg":"HS256","typ":"JWT"}
        h = self._b64(json.dumps(header).encode())
        p = self._b64(json.dumps(payload).encode())
        sig = hmac.new(self.secret, f"{h}.{p}".encode(), hashlib.sha256).hexdigest()
        return f"{h}.{p}.{sig}"
    def decode(self, token):
        try:
            h, p, sig = token.split(".")
            expected = hmac.new(self.secret, f"{h}.{p}".encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                raise ValueError("Invalid signature")
            payload = json.loads(self._unb64(p))
            if payload.get("exp",0) < time.time():
                raise ValueError("Token expired")
            return payload
        except Exception as e: raise ValueError(f"JWT error: {e}")
    def _b64(self, data): return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
    def _unb64(self, s): return base64.urlsafe_b64decode(s + "==")

class TinyAuth:
    """认证授权系统"""
    def __init__(self, secret):
        self.jwt = TinyJWT(secret); self.users = {}; self.roles = {}
    def register(self, username, password, roles=[]):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = {"hash": pw_hash, "roles": roles}
    def login(self, username, password):
        user = self.users.get(username)
        if not user: return None
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if pw_hash != user["hash"]: return None
        return self.jwt.encode({"sub": username, "roles": user["roles"]})
    def authorize(self, token, required_role):
        payload = self.jwt.decode(token)
        return required_role in payload.get("roles", [])

def main():
    print("tinyauth — JWT 认证授权（参照 Auth0）\n")
    auth = TinyAuth("super-secret-key")
    auth.register("admin", "pass123", roles=["admin","user"])
    auth.register("alice", "pwd456", roles=["user"])

    token = auth.login("admin", "pass123")
    print(f"  admin login → JWT: {token[:40]}...")
    decoded = auth.jwt.decode(token)
    print(f"  decoded: {decoded}")

    print(f"  authorize('admin'): {auth.authorize(token, 'admin')} ✅")
    print(f"  authorize('superadmin'): {auth.authorize(token, 'superadmin')} ❌")

    token2 = auth.login("alice", "pwd456")
    print(f"\n  alice login → authorize('admin'): {auth.authorize(token2, 'admin')} ❌")

    bad = auth.login("alice", "wrong")
    print(f"  wrong password → {bad}")

    print(f"\n  JWT 三段: header.payload.signature")
    print(f"  无状态验证（不需要查 DB）→ 水平扩展友好")

if __name__ == "__main__": main()
