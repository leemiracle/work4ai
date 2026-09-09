# ch01 练习题：自然数

> 阶段 1 / 模块 01 / 第 1 章
> 完成标准：3 题跑通 + 能讲清证明
> **铁律**：先自己写，跑不通再看答案。数学题"看答案 ≠ 会"。

---

## 📝 题 1：归纳法手证 + 程序验证（基础，20 分钟）

### 题目

用数学归纳法证明：

$$1^2 + 2^2 + \cdots + n^2 = \frac{n(n+1)(2n+1)}{6}$$

**你的任务**：
1. **手写证明**（纸笔，三段式：基础、归纳、结论）。
   - 提示：归纳步要证 $\sum_{k=1}^{n+1} k^2 = \frac{(n+1)(n+2)(2n+3)}{6}$
   - 用归纳假设 $\sum_{k=1}^{n} k^2 = \frac{n(n+1)(2n+1)}{6}$，两边加 $(n+1)^2$，因式分解
2. **程序验证**：写代码算 $\sum_{k=1}^{n} k^2$ 和 $\frac{n(n+1)(2n+1)}{6}$，对 n=1..100 验证恒等。
3. **思考题**：$1^3+2^3+\cdots+n^3 = ?$（猜测公式，用归纳法证明）。

### 期望输出

```
n=1:  1 = 1×2×3/6 = 1 ✓
n=10: 385 = 10×11×21/6 = 385 ✓
n=100: 338350 = 100×101×201/6 = 338350 ✓
归纳法手证: ... (写在纸上)
1³+...+n³ = (n(n+1)/2)²  ← 立方和 = 平方和的平方!
```

---

## 📝 题 2：哥德巴赫猜想验证（程序 + 可视化，25 分钟）

### 题目

哥德巴赫猜想（1742，至今未证）：**每个 >2 的偶数 = 两素数之和**。

**你的任务**：
1. 写函数 `goldbach(n)`：返回偶数 n 的一组素数分解对 `(p, q)`（n=p+q）。
2. 验证 4 到 1000 的**所有偶数**都能分解（如果有一个不能，你就推翻了 280 年的猜想！）。
3. 统计每个偶数的**分解方式数** g(n)，画 g(n) 图（"哥德巴赫彗星"）。
4. **思考题**：g(n) 总体趋势是上升还是下降？这暗示了什么？

### 提示

```python
def goldbach(n, primes_set):
    for p in primes_set:
        if p > n // 2: break
        if (n - p) in primes_set:
            return (p, n - p)
    return None   # 如果返回 None, 你就名垂青史了 (推翻猜想)

def goldbach_count(n, primes_set):
    return sum(1 for p in primes_set if p <= n//2 and (n-p) in primes_set)
```

### 期望观察

```
4 = 2+2,  10 = 3+7,  100 = 3+97
4..1000 所有偶数都能分解 ✓ (猜想在此范围内成立)
g(n) 总体上升 (偶数越大, 分解方式越多 → 暗示猜想"应该"成立)
但「验证」≠「证明」, 哪怕验证到 10^18 也不算证
```

---

## 📝 题 3：迷你 RSA 加密演示（工程锚点，25 分钟）

### 题目

用 §3 的费马小定理实现一个**玩具 RSA**，理解 HTTPS 的数学根基。

**RSA 流程**：
1. 选两个小素数 $p, q$（如 $p=11, q=17$），算 $n=pq=187$
2. 欧拉函数 $\phi(n) = (p-1)(q-1) = 160$
3. 选公钥 $e$（与 $\phi(n)$ 互素，如 $e=7$）
4. 算私钥 $d$：$ed \equiv 1 \pmod{\phi(n)}$（即 $d = e^{-1} \bmod \phi$）
5. **加密**：$c = m^e \bmod n$
6. **解密**：$m = c^d \bmod n$（用费马-欧拉定理保证还原）

**你的任务**：
1. 实现 `modinv(e, phi)`（扩展欧几里得算法求模逆元）。
2. 实现完整 RSA：生成密钥、加密消息 $m=42$、解密验证还原。
3. 把 "MATH" 用 ASCII 编码逐字符加密解密。
4. **思考题**：为什么 n 必须难分解？如果有人分解了 $n=pq$，会发生什么？

### 提示

```python
def modinv(a, m):
    """扩展欧几里得求 a^-1 mod m"""
    def egcd(a, b):
        if b == 0: return (a, 1, 0)
        g, x, y = egcd(b, a % b)
        return (g, y, x - (a // b) * y)
    g, x, _ = egcd(a, m)
    return x % m if g == 1 else None

p, q = 11, 17
n = p * q
phi = (p-1) * (q-1)
e = 7
d = modinv(e, phi)   # 私钥
# 加密 m
m = 42
c = pow(m, e, n)
# 解密
m2 = pow(c, d, n)
print(m, '->加密->', c, '->解密->', m2)  # 应得 42
```

### 期望输出

```
p=11, q=17, n=187, phi=160
公钥 (e=7, n=187), 私钥 (d=23, n=187)
加密 m=42: c = 42^7 mod 187 = ?
解密 c:    m = c^23 mod 187 = 42 ✓ 还原
"MATH" 加密: [c_M, c_A, c_T, c_H], 解密还原 "MATH" ✓
```

**思考题答案**：分解 $n=pq$ → 算出 $\phi=(p-1)(q-1)$ → 算出私钥 $d=e^{-1}\bmod\phi$ → 完全破解。
所以 RSA 安全 = **大整数分解困难**。2048 位 n 用最快计算机要分解几亿年。这就是你网银安全的根基——建立在这章的费马小定理上。

---

## 🔑 参考答案（做完再看！）

<details>
<summary>👉 点击展开题 1 答案</summary>

**手证归纳**：
- 基础 n=1：$1^2 = 1 = \frac{1\cdot2\cdot3}{6}$ ✓
- 归纳：假设 $\sum_{k=1}^n k^2 = \frac{n(n+1)(2n+1)}{6}$。则
  $$\sum_{k=1}^{n+1} k^2 = \frac{n(n+1)(2n+1)}{6} + (n+1)^2 = (n+1)\left[\frac{n(2n+1)}{6} + (n+1)\right]$$
  $$= (n+1)\cdot\frac{2n^2+n+6n+6}{6} = (n+1)\cdot\frac{(n+2)(2n+3)}{6} = \frac{(n+1)(n+2)(2n+3)}{6} \checkmark$$
- 结论：$\forall n$ 成立。$\blacksquare$

```python
def sq_sum(n): return sum(k**2 for k in range(1, n+1))
def formula(n): return n*(n+1)*(2*n+1)//6
all(sq_sum(n) == formula(n) for n in range(1, 101))   # True
# 立方和
def cb_sum(n): return sum(k**3 for k in range(1, n+1))
all(cb_sum(n) == (n*(n+1)//2)**2 for n in range(1, 101))  # True
```

</details>

<details>
<summary>👉 点击展开题 2 答案</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
def sieve_set(N):
    is_p = np.ones(N+1, bool); is_p[:2]=False
    for i in range(2, int(N**0.5)+1):
        if is_p[i]: is_p[i*i::i]=False
    return set(np.where(is_p)[0])
P = sieve_set(1000)
def goldbach(n):
    for p in sorted(P):
        if p > n//2: return None
        if n-p in P: return (p, n-p)
def gcount(n):
    return sum(1 for p in P if p <= n//2 and n-p in P)
# 验证 4..1000
evens = list(range(4, 1001, 2))
broken = [n for n in evens if goldbach(n) is None]
print(f"4..1000 不能分解的偶数: {broken} (应为空)")
print("100 =", goldbach(100))
# 哥德巴赫彗星
gs = [gcount(n) for n in evens]
plt.figure(figsize=(10,4))
plt.scatter(evens, gs, s=4, alpha=0.5)
plt.xlabel('偶数 n'); plt.ylabel('分解方式数 g(n)')
plt.title('哥德巴赫彗星: g(n) 总体上升 (偶数越大分解方式越多)')
plt.grid(True, ls=':', alpha=0.3); plt.savefig('goldbach_comet.png', dpi=100)
```

</details>

<details>
<summary>👉 点击展开题 3 答案</summary>

```python
def modinv(a, m):
    def egcd(a, b):
        if b == 0: return (a, 1, 0)
        g, x, y = egcd(b, a % b)
        return (g, y, x - (a // b) * y)
    g, x, _ = egcd(a, m)
    return x % m if g == 1 else None

p, q = 11, 17
n = p * q          # 187
phi = (p-1)*(q-1)  # 160
e = 7
d = modinv(e, phi)
print(f"公钥 (e={e}, n={n}), 私钥 (d={d}, n={n})")
assert (e*d) % phi == 1

m = 42
c = pow(m, e, n)
m2 = pow(c, d, n)
print(f"加密: {m} -> {c}, 解密: {c} -> {m2}, 还原? {m == m2}")

# 加密字符串
msg = "MATH"
enc = [pow(ord(ch), e, n) for ch in msg]
dec = ''.join(chr(pow(c, d, n)) for c in enc)
print(f"'{msg}' -> 加密 {enc} -> 解密 '{dec}'")
```

</details>

---

## ✅ 完成检查表

- [ ] 题 1 手写归纳证明（基础+归纳+结论完整）
- [ ] 题 2 验证 4..1000 哥德巴赫成立，画出彗星
- [ ] 题 3 RSA 加解密成功还原明文
- [ ] 能讲清"为什么分解 n 就能破解 RSA"

**全部 ✓ = 第 1 章真正过关**。进入《什么是数学》第 2 章（数系）。

---

## 📌 完成后

回到 `ch01-自然数.md` §8 自测，用嘴巴回答 7 个问题。
**能流利回答 5 个以上 = 第 1 章掌握**，建 `ch02-数系.md` + `what_is_math_ch2.py` 进入下一章。
