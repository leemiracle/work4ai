# Harvard Math 154 · 数论 精读笔记

> **教材**：Niven-Zuckerman-Montgomery, *An Introduction to the Theory of Numbers*；或 Hardy-Wright
> **参考**：[Harvard Math 154](https://www.math.harvard.edu/)

---

## 〇、费曼直觉层：数论到底在研究什么？

### 一句话直觉

> **数论 = 研究整数的深层结构——"最纯的数学"的代名词。**

整数的加法、乘法、整除性，看似简单到幼稚——但藏在这些基本运算背后的是惊人的深度和复杂性。

### 与 ML/工程的联系（不像其他课那么直接，但存在）

| 概念 | ML/工程对应 |
|---|---|
| **模运算** | 哈希函数、伪随机数生成器 |
| **素数 + RSA** | 公钥密码（互联网安全）|
| **椭圆曲线** | Bitcoin/Ethereum 签名 |
| **中国剩余定理** | 分布式计算、联邦学习 |
| **离散对数** | Diffie-Hellman 密钥交换 |

---

## 一、数学层：核心定理

### 1.1 整除与素数

**算术基本定理** ★：每个正整数 $n > 1$ 唯一分解为素数乘积：
$$n = p_1^{a_1} p_2^{a_2} \cdots p_k^{a_k}$$

**素数无穷（Euclid 证明）**：假设素数有限 $\{p_1, \ldots, p_k\}$，则 $N = p_1 p_2 \cdots p_k + 1$ 要么是素数，要么有不在列表中的素因子。矛盾。

### 1.2 同余与模运算

**Fermat 小定理** ★：对素数 $p$，$a^{p-1} \equiv 1 \pmod{p}$（$p \nmid a$）。

**Euler 定理**：$a^{\varphi(n)} \equiv 1 \pmod{n}$（$\gcd(a,n)=1$），$\varphi$ = Euler 函数。

**中国剩余定理（CRT）** ★：若 $\gcd(m_i, m_j) = 1$，则
$$x \equiv a_i \pmod{m_i} \quad (i = 1, \ldots, k)$$
在 $\bmod\, M = m_1 \cdots m_k$ 下有唯一解。

### 1.3 RSA 密码 ★

**密钥生成**：
1. 选两个大素数 $p, q$，$n = pq$
2. 计算 $\varphi(n) = (p-1)(q-1)$
3. 选 $e$ 使 $\gcd(e, \varphi(n)) = 1$
4. 计算 $d = e^{-1} \bmod \varphi(n)$

**加密/解密**：$c = m^e \bmod n$；$m = c^d \bmod n$。

**正确性**：$(m^e)^d = m^{ed} = m^{1 + k\varphi(n)} \equiv m \pmod{n}$（Euler 定理）。

**安全性**：分解 $n = pq$ 很难（没有已知多项式算法）。

### 1.4 二次剩余与 Legendre 符号

**定义**：$a$ 是模 $p$ 的二次剩余，如果 $x^2 \equiv a \pmod{p}$ 有解。

**Legendre 符号**：$\left(\frac{a}{p}\right) = \begin{cases} 1 & \text{剩余} \\ -1 & \text{非剩余} \\ 0 & p | a\end{cases}$

**二次互反律** ★（Gauss 的"黄金定理"）：
$$\left(\frac{p}{q}\right)\left(\frac{q}{p}\right) = (-1)^{\frac{p-1}{2}\frac{q-1}{2}}$$

### 1.5 椭圆曲线 ★

**Weierstrass 方程**：$y^2 = x^3 + ax + b$

**群运算**：椭圆曲线上的点 + "无穷远点 $O$" 构成一个阿贝尔群。三点共线 → 和为零。

$$P + Q + R = O \iff P, Q, R \text{ 共线}$$

**ECC（椭圆曲线密码）**：基于椭圆曲线离散对数问题（ECDLP）的困难性。256-bit ECC ≈ 3072-bit RSA 的安全级别。

### 1.6 连分数与 Pell 方程

**连分数**：$\sqrt{2} = [1; \overline{2}] = 1 + \frac{1}{2 + \frac{1}{2 + \cdots}}$

**Pell 方程** $x^2 - Dy^2 = 1$：解由 $\sqrt{D}$ 的连分数给出。

### 1.7 解析数论入门

**Riemann Zeta 函数**：$\zeta(s) = \sum_{n=1}^\infty n^{-s}$

**素数定理** ★：$\pi(x) \sim x/\ln x$（$\pi(x)$ = 不超过 $x$ 的素数个数）

**Riemann 假设**（千禧年问题）：$\zeta(s)$ 的所有非平凡零点在 $\mathrm{Re}(s) = 1/2$ 上。

---

## 二、代码层

### 2.1 RSA 加密演示

```python
from sympy import randprime, mod_inverse

p, q = randprime(10**50, 10**51), randprime(10**50, 10**51)
n = p * q
phi = (p - 1) * (q - 1)
e = 65537  # 标准 RSA 公钥指数
d = mod_inverse(e, phi)

message = 12345678901234567890
ciphertext = pow(message, e, n)
decrypted = pow(ciphertext, d, n)
print(f"原文: {message}")
print(f"密文: {ciphertext}")
print(f"解密: {decrypted} ✓" if decrypted == message else "解密失败!")
```

### 2.2 素数计数函数验证

```python
import numpy as np

def prime_count(x):
    """π(x): 不超过 x 的素数个数"""
    sieve = np.ones(int(x) + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(np.sqrt(x)) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    return sieve.sum()

for x in [100, 1000, 10000, 100000]:
    pi_x = prime_count(x)
    approximation = x / np.log(x)
    print(f"π({x}) = {pi_x}, x/ln(x) = {approximation:.1f}, 比值 = {pi_x/approxination:.4f}")
```

---

## 三、与 ML/工程的联系

### 3.1 密码学（最直接的工程应用）
- RSA、ECC、Diffie-Hellman → 互联网安全基础设施
- 全同态加密（FHE）→ 隐私保护的 ML（联邦学习）

### 3.2 伪随机数生成
- 线性同余生成器（LCG）：$x_{n+1} = (ax_n + c) \bmod m$
- 基于 CRT 的并行随机数生成

### 3.3 纠错码
- Reed-Solomon 码（基于有限域上的多项式）→ CD/DVD/QR 码

### 3.4 中国剩余定理 → 联邦学习
CRT 允许把大模数运算拆成小模数并行运算 → 分布式密码学计算

---

## 四、不足层

1. **数论与 ML 的联系是间接的**：主要通过密码学（安全/隐私）而非模型设计
2. **解析数论需要大量复分析准备**：素数定理的证明需要 $\zeta(s)$ 的解析延拓
3. **计算数论**（算法层面）比理论数论对 ML 更实用——本课偏理论

---

## 五、推荐路径

1. **Niven-Zuckerman-Montgomery** 第 1-3 章：整除 → 同余 → CRT → **核心**
2. **第 4-5 章**：二次剩余 + 连分数 → 选读
3. **密码学方向**：RSA + 椭圆曲线 → **工程必读**
4. **跳过**：解析数论（除非对 Riemann 假设有兴趣）

---

## 术语对照

| 英文 | 中文 |
|---|---|
| Prime number | 素数 |
| Congruence | 同余 |
| Euler's totient function | Euler 函数 $\varphi(n)$ |
| Chinese Remainder Theorem | 中国剩余定理 |
| Quadratic residue | 二次剩余 |
| Legendre symbol | Legendre 符号 |
| Quadratic reciprocity | 二次互反律 |
| Elliptic curve | 椭圆曲线 |
| Discrete logarithm | 离散对数 |
| Riemann zeta function | Riemann zeta 函数 |
| Prime number theorem | 素数定理 |
| Continued fraction | 连分数 |
