# 01 - Sylow 定理：有限群的"骨架"

> Sylow 三大定理是**有限群论最深刻的结果之一**。它们告诉你：有限群内部必然存在某些特定阶的子群。

---

## 一、直觉

### 1.1 Lagrange 的"逆问题"

Lagrange 定理：子群阶整除群阶。但反过来吗？对 $|G|$ 的每个因子 $d$，$G$ 都有 $d$ 阶子群吗？

**反直觉**：不一定！$A_4$（12 阶交错群）没有 6 阶子群——虽然 6 整除 12。

### 1.2 Sylow 的回答（1872）

Sylow 说：**对于素数幂阶**，子群必然存在。

设 $|G| = p^k \cdot m$，其中 $p$ 是素数，$\gcd(p, m) = 0$（即 $p^k$ 是 $p$ 在 $|G|$ 里的最高次幂）。

→ $G$ 必有 $p^k$ 阶子群（**Sylow $p$-子群**）。

---

## 二、Sylow 三大定理

### 2.1 第一定理（存在性）

$|G| = p^k m$, $\gcd(p,m)=1$ ⟹ $G$ 存在 $p^k$ 阶子群 $P$（称 Sylow $p$-子群）。

**例**：$|S_5| = 120 = 2^3 \cdot 3 \cdot 5$。
- Sylow 2-子群：8 阶
- Sylow 3-子群：3 阶
- Sylow 5-子群：5 阶

### 2.2 第二定理（共轭性）

所有 Sylow $p$-子群互相共轭。即任两个 Sylow $p$-子群 $P, P'$，存在 $g \in G$ 使 $P' = gPg^{-1}$。

→ Sylow $p$-子群"长得都一样"（同构）。

### 2.3 第三定理（计数）

Sylow $p$-子群的个数 $n_p$ 满足：
- $n_p \equiv 1 \pmod{p}$
- $n_p \mid m$（即 $n_p$ 整除 $|G|/p^k$）

**例**：$|G| = 30 = 2 \cdot 3 \cdot 5$。
- $n_5 \in \{1, 6\}$（$n_5 \mid 6$ 且 $n_5 \equiv 1 \pmod 5$）
- $n_3 \in \{1, 10\}$

### 2.4 应用：群的"分解"

Sylow 定理让你**把大群分解成素数幂阶的小块**。这是分类有限群的基础。

---

## 三、应用

### 3.1 证明群不是单群

**单群**：没有非平凡正规子群。Sylow 定理帮你证明某些群不是单的。

**例**：$|G| = 30$。$n_5 \in \{1, 6\}$，$n_3 \in \{1, 10\}$。如果 $n_5 = 1$ 或 $n_3 = 1$，则 Sylow 子群是正规的 → $G$ 不单。

### 3.2 Galois 理论的工具

Galois 用"可解群"概念判断方程是否可解。可解性用到 Sylow 子群的链。

### 3.3 Burnside 定理（$p^a q^b$ 定理）

$|G| = p^a q^b$（只有两个素因子）⟹ $G$ 可解。证明用 Sylow。

---

## 四、实验

### `experiments/01_sylow.py`

```python
"""
讲透群论 01 章实验：Sylow 定理验证。
"""
from sympy import factorint, divisors

def sylow_subgroup_count(n, p):
    """对 |G|=n，计算 Sylow p-子群的个数可能值"""
    factors = factorint(n)
    if p not in factors:
        return None, 0
    k = factors[p]
    pk = p ** k
    m = n // pk
    # n_p | m 且 n_p ≡ 1 mod p
    possible = [d for d in divisors(m) if d % p == 1]
    return pk, possible

print("Sylow 定理验证：")
print(f"{'|G|':<8} {'p':<4} {'Sylow p-子群阶':<18} {'n_p 可能值'}")
for n in [6, 12, 24, 30, 60, 120, 360]:
    factors = factorint(n)
    for p in factors:
        pk, possible = sylow_subgroup_count(n, p)
        print(f"{n:<8} {p:<4} {pk:<18} {possible}")
    print()
```

预期输出（部分）：
```
60       2   4                 [1, 3, 5, 15]
60       3   3                 [1, 4, 10]
60       5   5                 [1, 6]
```

---

## 五、反直觉发现

**Sylow 子群不唯一**。$|S_5| = 120$，Sylow 2-子群有 $n_2 \in \{1, 3, 5, 15\}$ 个。实际是 15 个。

→ "群的结构"比"群的阶"复杂得多。两个同阶群可能完全不同构。

---

📌 **下一步**：读 [`02-群作用与轨道.md`](02-群作用.md)（待写）。跑 `experiments/01_sylow.py`。

## ✍️ 练习

1. **基础**：陈述 Sylow 三大定理。
2. **计算**：$|G| = 30$，求 $n_2, n_3, n_5$ 的所有可能值。
3. **思考**：为什么 Sylow 定理只对**素数幂**阶保证子群存在？（提示：素数幂群有中心，可归纳）
4. **🐍 Python**：在 `01_sylow.py` 加验证 $|A_4|=12$ 没有 6 阶子群（Lagrange 逆问题反例）。
5. **应用**：解释 Sylow 怎么用来证明 $|G|=15$ 的群必循环。
