# MIT 18.701 · 费曼三层讲透：抽象代数 I（群与环）

> **教材**：Artin, *Algebra* (2nd ed, 2017) ★ — Michael Artin 亲写
> **视频**：[OCW 18.701-702 Artin](https://ocw.mit.edu/courses/18-701-algebra-i-fall-2010/)
> **特色**：MIT 本科纯数学核心——**群 / 环 / 域 / 群作用**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **群（Group）** | **"对称性的语言"**——可逆变换的集合，如旋转、置换 |
| **群作用** | **"群作用于集合 = 对称性操作"**——轨道 = 可到达的点 |
| **子群** | **"群里的家族"**——闭合的子集 |
| **正规子群 / 商群** | **"把群折叠/取模"**——$\mathbb{Z}/n\mathbb{Z}$ = 时钟算术 |
| **同态** | **"保持结构的映射"**——$f(ab) = f(a)f(b)$ |
| **环（Ring）** | **"能加能乘的集合"**——如 $\mathbb{Z}$、多项式、矩阵 |
| **域（Field）** | **"能加能乘能除的集合"**——$\mathbb{R}$、$\mathbb{F}_p$ |
| **群表示** | **"把抽象群变成矩阵"**——$\rho: G \to GL(V)$ |

> **一句话总结**：**群 = 对称性的语言**。等边三角形的对称 = $D_3$（6 阶二面体群）；正方形的对称 = $D_4$；所有 n 阶置换 = $S_n$。**群表示论 = 把对称性变成矩阵**，是等变神经网络的数学根基。

---

## 🧮 数学层

### 1. 群的定义

**群** $(G, \cdot)$：
1. **结合律**：$(ab)c = a(bc)$
2. **单位元**：$\exists e: ae = ea = a$
3. **逆元**：$\forall a, \exists a^{-1}: aa^{-1} = e$

**阿贝尔群**：额外满足 $ab = ba$。

**经典例子**：
| 群 | 元素 | 运算 |
|---|---|---|
| $(\mathbb{Z}, +)$ | 整数 | 加法 |
| $(\mathbb{R}^*, \times)$ | 非零实数 | 乘法 |
| $S_n$ | $\{1,\dots,n\}$ 的置换 | 复合 |
| $GL_n(\mathbb{R})$ | 可逆 $n\times n$ 矩阵 | 矩阵乘 |
| $D_n$ | 正 $n$ 边形对称 | 复合 |

### 2. 子群与陪集

**子群** $H \leq G$：$H$ 在群的运算下是群。

**陪集**：$aH = \{ah : h \in H\}$（左陪集）。

**Lagrange 定理** ★：$|G| = [G:H] \cdot |H|$（群的阶 = 指数 × 子群阶）。
→ **子群的阶整除群的阶**。

### 3. 同态与同构

**同态**：$\varphi: G \to G'$, $\varphi(ab) = \varphi(a)\varphi(b)$。

**核** $\ker\varphi = \{a : \varphi(a) = e\}$ 是正规子群。
**像** $\text{im}\,\varphi$ 是 $G'$ 的子群。

**第一同构定理** ★：
$$G / \ker\varphi \cong \text{im}\,\varphi$$

### 4. 对称群 $S_n$ ★

$S_n$ = $\{1,\dots,n\}$ 的所有置换，$|S_n| = n!$。

**轮换分解**：每个置换可写成不交轮换之积。

**交错群** $A_n$ = 偶置换子群，$|A_n| = n!/2$。

### 5. 群作用 ★★

群 $G$ **作用**于集合 $X$：$G \times X \to X$, $e \cdot x = x$, $(gh)\cdot x = g\cdot(h\cdot x)$。

**轨道**：$\text{Orb}(x) = \{g \cdot x : g \in G\}$。
**稳定子**：$\text{Stab}(x) = \{g : g \cdot x = x\}$。

**轨道-稳定子定理** ★：$|G| = |\text{Orb}(x)| \cdot |\text{Stab}(x)|$。

**Burnside 引理**：轨道数 $= \frac{1}{|G|}\sum_g |\text{Fix}(g)|$。

**Sylow 定理** ★★：
- 若 $p^k | |G|$，则存在 $p^k$ 阶子群（Sylow $p$-子群）
- 所有 Sylow $p$-子群共轭
- Sylow $p$-子群的个数 $n_p \equiv 1 \pmod{p}$ 且 $n_p | m$（$|G| = p^k m$, $\gcd(p,m)=1$）

### 6. 矩阵群

- $GL_n(\mathbb{R})$：一般线性群（可逆矩阵）
- $SL_n$：特殊线性群（$\det = 1$）
- $O_n$：正交群（$A^TA = I$）
- $SO_n$：特殊正交群（旋转）
- $U_n$：酉群（复正交）

> **ML 关联**：**等变神经网络**要求特征对群作用等变。例如 $E(n)$-等变 GNN 对 3D 旋转等变。

### 7. 群表示论入门 ★★

**表示**：同态 $\rho: G \to GL(V)$（把群元变成线性变换）。

**特征标**：$\chi_\rho(g) = \text{tr}(\rho(g))$。

**不可约表示**：没有非平凡不变子空间。

**Maschke 定理**：有限群在 $\text{char}=0$ 域上，所有表示完全可约（直和分解为不可约）。

**特征标正交性** ★：
$$\langle \chi_i, \chi_j \rangle = \frac{1}{|G|}\sum_g \overline{\chi_i(g)}\chi_j(g) = \delta_{ij}$$

> **ML 关联**：
> - **等变神经网络**（Cohen-Welling）：群卷积 = 群表示的张量积
> - **张量分解**：用群表示论分解高阶张量（CP/Tucker 分解的对称性）
> - **深度学习的对称性**：CNN 的平移等变 = $\mathbb{Z}^2$ 群卷积

### 8. 环与域

**环** $(R, +, \cdot)$：加法群 + 乘法半群 + 分配律。

**理想** $I \subseteq R$：加法子群且 $rI \subseteq I$, $Ir \subseteq I$。

**商环** $R/I$：把环"取模"。

**域** = 交换环 + 每个非零元有乘法逆。

**域扩张** $F \subseteq K$：$[K:F]$ = 扩张次数。

**Galois 理论入门**：域扩张的自同构群 ↔ 子域格（Galois 对应）。

---

## 💻 代码层

```python
import numpy as np
from itertools import permutations

# 对称群 S_3 的所有元素 (置换)
S3 = list(permutations(range(3)))
print(f"|S_3| = {len(S3)}")  # 6

def perm_to_matrix(p):
    """置换 → 置换矩阵 (群表示)"""
    n = len(p); M = np.zeros((n, n))
    for i, j in enumerate(p): M[i, j] = 1
    return M

# S_3 的标准表示 (3x3 置换矩阵)
for p in S3:
    print(f"置换 {p} → 矩阵\n{perm_to_matrix(p)}\n")

# 群作用的轨道: 旋转正三角形
def triangle_orbit():
    """D_3 作用在三角形顶点上"""
    D3 = [(r, s) for r in range(3) for s in range(2)]  # (旋转, 翻转)
    print("D_3 的阶:", len(D3))  # 6

# 特征标表 (S_3 的不可约表示)
# 3 个不可约: 平凡(1维), 符号(1维), 标准(2维)
chars = {
    'trivial':  [1, 1, 1],     # 在 (e), (12), (123) 的值
    'sign':      [1, -1, 1],
    'standard':  [2, 0, -1]
}
print("S_3 特征标表:")
for name, ch in chars.items():
    print(f"  {name}: {ch}")

# 验证正交性: <χ_i, χ_j> = δ_ij (用类的大小加权)
class_sizes = [1, 3, 2]  # e, (12)类, (123)类 的元素数
for n1, c1 in chars.items():
    for n2, c2 in chars.items():
        inner = sum(cs * a * b for cs, a, b in zip(class_sizes, c1, c2)) / 6
        print(f"  <{n1},{n2}> = {inner:.1f}")
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **群论高度抽象** | 初学者难建立直觉，需大量例子（对称群、矩阵群）|
| **Galois 理论陡峭** | 需要域论基础，与 ML 直接关联少 |
| **表示论计算量大** | 大群的特征标表手算困难 |
| **无限群理论更深** | Lie 群、拓扑群需额外分析基础 |
| **ML 应用集中在等变网络** | 大部分纯代数（环/域/Galois）与 ML 关联间接 |

---

## 🔬 应用层

1. **群表示论 → 等变神经网络**（Cohen-Welling G-CNN）
2. **CNN 平移等变 = $\mathbb{Z}^d$ 群卷积**
3. **$E(n)$-等变 GNN → 分子结构预测**（AlphaFold 的对称性）
4. **张量分解**：CP/Tucker 分解利用对称性
5. **密码学**：RSA / 椭圆曲线 = 有限域上的群

---

## 🆕 2024-2026 最新研究

- **Equivariant Deep Learning**：Cohen, Welling, Bronstein 等推动的几何深度学习
- **AlphaFold 2/3**：SE(3)-等变网络预测蛋白质/分子结构
- **群等变 Transformer**：用群论设计 attention 的对称性
- **拓扑数据分析**：用群/拓扑分析神经网络损失景观
- **量子计算**：有限群表示论是量子算法的基础

---

## 📚 章节结构对照（Artin）

| 章 | 主题 | 重要性 |
|---|---|---|
| 1-2 | 群定义与例子 | ★★ |
| 3-4 | 子群、同态、商群 | ★★★ |
| 5-6 | **对称群 $S_n$ 与群作用** | ★★★ |
| 7 | Sylow 定理 | ★★ |
| 8-9 | **矩阵群与表示论入门** | ★★★ |
| 10-11 | 环与理想 | ★★ |
| 15-16 | 域与 Galois 入门 | ★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透等变神经网络**：第 8-9 章（群表示论）
- **讲透 CNN 平移等变**：第 5 章（$\mathbb{Z}^d$ 群作用）
- **讲透 AlphaFold 对称性**：第 8 章（SE(3) 群）
