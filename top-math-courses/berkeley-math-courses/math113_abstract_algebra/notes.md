# UC Berkeley MATH 113 · 抽象代数 精读笔记

> **教材**：Dummit & Foote, *Abstract Algebra* (3rd ed, Wiley) 或 Artin, *Algebra* (2nd ed)
> **参考**：[Berkeley MATH 113](https://math.berkeley.edu/courses) + Dummit-Foote 全书习题

---

## 〇、费曼直觉层：抽象代数到底在研究什么？

### 一句话直觉

> **群 = 对称性的语言。环 = 数系的推广。域 = 可做四则运算的世界。**

抽象代数的本质不是"把简单的东西变难"，而是**发现不同数学对象共享同一套结构**。

**例子**：
- 整数加法群 $\mathbb{Z}$、时钟 $\mathbb{Z}/12\mathbb{Z}$、$n \times n$ 可逆矩阵 $GL_n$、魔方旋转——看起来毫无关系，但它们都是**群**。
- 一旦你证明了"子群阶整除群阶"（Lagrange 定理），这个结论**同时**适用于以上所有对象。

### 三个核心直觉

| 结构 | 直觉 | ML 对应 |
|---|---|---|
| **群** | "可逆变换"的集合 | 等变神经网络（旋转/平移不变性）|
| **群作用** | 群在集合上的对称操作 | 对称增强（data augmentation = 群作用）|
| **环/域** | "可以做四则运算"的集合 | 有限域 → 密码学；多项式环 → 纠错码 |

### 群 = 对称性的语言

考虑一个等边三角形。它的对称群 $D_3$（二面体群）有 6 个元素：
- 旋转 $0°, 120°, 240°$：$e, r, r^2$
- 三个翻转：$s, sr, sr^2$

满足 $r^3 = e$, $s^2 = e$, $sr = r^{-1}s$。

**关键洞察**：一旦你知道了 $D_3$ 的乘法表，你就知道了**所有**具有三角形对称性的对象的行为——不管它是几何三角形、分子、还是神经网络的等变约束。

---

## 一、数学层：核心定义与定理

### 1.1 群的定义与基本性质

**定义（群）**：一个群 $(G, \cdot)$ 是一个集合 $G$ 配合一个二元运算 $\cdot: G \times G \to G$，满足：
1. **结合律**：$(a \cdot b) \cdot c = a \cdot (b \cdot c)$
2. **单位元**：存在 $e \in G$ 使 $e \cdot g = g \cdot e = g$ 对所有 $g$
3. **逆元**：对每个 $g \in G$，存在 $g^{-1}$ 使 $g \cdot g^{-1} = g^{-1} \cdot g = e$

如果还满足**交换律** $a \cdot b = b \cdot a$，则称**阿贝尔群**（Abelian group）。

**基本性质**：
- 单位元唯一：若 $e, e'$ 都是单位元，则 $e = e \cdot e' = e'$
- 逆元唯一：若 $g^{-1}, h$ 都是 $g$ 的逆，则 $h = he = h(gg^{-1}) = (hg)g^{-1} = eg^{-1} = g^{-1}$
- 消去律：$ab = ac \Rightarrow b = c$

### 1.2 子群与陪集

**定义（子群）**：$H \subseteq G$ 是子群，如果 $H$ 在 $G$ 的运算下也构成群。

**陪集**：对 $g \in G$，左陪集 $gH = \{gh : h \in H\}$。

**关键性质**：两个左陪集 $g_1H$ 和 $g_2H$ 要么完全相同，要么不相交。

**定理（Lagrange 定理）** ★：若 $G$ 是有限群，$H \leq G$，则 $|H|$ 整除 $|G|$。

**证明直觉**：$G$ 被划分为若干不相交的陪集，每个陪集大小 = $|H|$。陪集个数 $[G:H] = |G|/|H|$。

**推论**：
- 任何元素的阶（$o(g) = $ 最小的 $n$ 使 $g^n = e$）整除 $|G|$
- **费马小定理**：对素数 $p$，$a^p \equiv a \pmod{p}$（因为 $|(\mathbb{Z}/p\mathbb{Z})^\times| = p-1$）

### 1.3 同态与同构定理

**定义（同态）**：$\varphi: G \to G'$ 是同态，如果 $\varphi(ab) = \varphi(a)\varphi(b)$。

- **核**：$\ker\varphi = \{g \in G : \varphi(g) = e'\}$（$G$ 的正规子群）
- **像**：$\mathrm{im}\,\varphi = \{\varphi(g) : g \in G\}$（$G'$ 的子群）

**第一同构定理** ★：
$$G / \ker\varphi \cong \mathrm{im}\,\varphi$$

**直觉**：同态"坍缩"了核，商群 $G/\ker\varphi$ 就是"压缩后的 $G$"，恰好等于像。

**正规子群**：$N \trianglelefteq G$ 意味着 $gNg^{-1} = N$ 对所有 $g$。只有正规子群才能构造商群 $G/N$。

### 1.4 对称群 $S_n$ 与交错群 $A_n$ ★

**对称群** $S_n$：$\{1, 2, \ldots, n\}$ 的所有排列，$|S_n| = n!$。

- **轮换**：$(1\,2\,3)$ 表示 $1 \to 2 \to 3 \to 1$
- **对换**：$(1\,2)$ 交换两个元素，每个排列 = 对换的乘积
- **奇偶性**：排列 = 偶数个对换的乘积 → 偶排列；否则奇排列

**交错群** $A_n$：$S_n$ 中所有偶排列构成的子群，$|A_n| = n!/2$。

- $A_n$ 是 $S_n$ 的正规子群（指标 2）
- $A_5$（$|A_5| = 60$）是**最小非交换单群** → 五次方程无根式解的根源

### 1.5 群作用 ★（本课核心）

**定义（群作用）**：群 $G$ 作用在集合 $X$ 上，是一个映射 $G \times X \to X$, $(g, x) \mapsto g \cdot x$，满足：
1. $e \cdot x = x$
2. $g \cdot (h \cdot x) = (gh) \cdot x$

等价地，是一个群同态 $G \to \mathrm{Sym}(X)$（$X$ 的排列群）。

**轨道**：$G \cdot x = \{g \cdot x : g \in G\}$（$x$ 在群作用下能到的所有位置）

**稳定子**：$G_x = \{g \in G : g \cdot x = x\}$（固定 $x$ 的群元素）

**轨道-稳定子定理** ★：
$$|G \cdot x| = [G : G_x] = \frac{|G|}{|G_x|}$$

**直觉**：群的"总能量" $|G|$ = 轨道大小 × 稳定子大小。

**Burnside 引理**：$G$ 作用在有限集 $X$ 上，轨道数（本质不同的等价类数）为：
$$\text{轨道数} = \frac{1}{|G|}\sum_{g \in G} |X^g|, \quad X^g = \{x : g \cdot x = x\}$$

### 1.6 Sylow 定理 ★

**定理（Sylow 第一定理）**：若 $|G| = p^a m$（$p$ 为素数，$p \nmid m$），则 $G$ 中存在阶为 $p^a$ 的子群（Sylow $p$-子群）。

**Sylow 第三定理**：Sylow $p$-子群的个数 $n_p$ 满足 $n_p \equiv 1 \pmod{p}$ 且 $n_p \mid m$。

**用途**：判断群是否为单群（没有非平凡正规子群）、群的分类。

### 1.7 环与理想

**定义（环）**：$(R, +, \cdot)$ 有两个运算：
- $(R, +)$ 是阿贝尔群
- $(R, \cdot)$ 满足结合律（有乘法单位元则为"含幺环"）
- 分配律：$a(b+c) = ab + ac$

**理想**：$I \subseteq R$ 满足 $(I, +) \leq (R, +)$ 且 $rI \subseteq I$, $Ir \subseteq I$ 对所有 $r \in R$。

- 理想之于环 = 正规子群之于群（允许构造商环 $R/I$）
- **极大理想**：$R/I$ 是域
- **素理想**：$R/I$ 是整环

**PID（主理想整环）**：$\mathbb{Z}$, $F[x]$（域上的多项式环）——每个理想由一个元素生成。

### 1.8 域扩张与 Galois 理论入门

**域扩张**：$K/F$ 表示 $K$ 是 $F$ 的扩域，$[K:F] = \dim_F K$ 是扩张次数。

**代数 vs 超越**：$\alpha$ 在 $F$ 上代数 = 存在 $f \in F[x]$ 使 $f(\alpha) = 0$。否则超越（如 $\pi$ 在 $\mathbb{Q}$ 上）。

**Galois 群**：$\mathrm{Gal}(K/F) = \{F$-自同构 $K \to K\}$。

**基本定理**：中间域 $F \subseteq L \subseteq K$ ↔ Galois 群的子群 $\mathrm{Gal}(K/L) \leq \mathrm{Gal}(K/F)$。

---

## 二、代码层：群作用的可视化

### 2.1 群乘法表与 Lagrange 定理验证

```python
import numpy as np
from itertools import permutations

# 对称群 S_3 的元素 (作为排列)
S3 = list(permutations(range(3)))
def compose(p, q):
    """排列复合 p∘q (先q后p)"""
    return tuple(p[q[i]] for i in range(len(p)))

def mult_table(S):
    n = len(S)
    T = np.zeros((n, n), dtype=int)
    for i, p in enumerate(S):
        for j, q in enumerate(S):
            r = compose(p, q)
            T[i, j] = S.index(r)
    return T

T = mult_table(S3)
print(f"|S_3| = {len(S3)}")
print("乘法表:"); print(T)

# 验证子群 H = {id, (01)} 的阶整除 |S_3|
H = [(0,1,2), (1,0,2)]  # {id, (01)}
print(f"\n|H| = {len(H)}, |S_3| / |H| = {len(S3) / len(H):.0f} (Lagrange ✓)")
```

### 2.2 轨道-稳定子定理验证

```python
# D_4 (正方形对称群) 作用在顶点 {0,1,2,3} 上
# D_4 = {e, r, r^2, r^3, s, sr, sr^2, sr^3}
def rotate(vertices, k):
    """顺时针旋转 k×90°"""
    n = len(vertices)
    return tuple(vertices[(i - k) % n] for i in range(n))

def reflect(vertices):
    """沿垂直轴翻转"""
    return tuple(vertices[::-1])

# 构建 D_4 的 8 个元素
e = (0, 1, 2, 3)
D4 = [e]
v = e
for k in range(1, 4):
    v = rotate(v, 1)
    D4.append(v)
# 翻转后的元素
for k in range(4):
    D4.append(reflect(rotate(e, k)))

print(f"|D_4| = {len(D4)}")
# 顶点 0 的轨道
orbit_0 = set()
for g in D4:
    orbit_0.add(g[0])  # g 作用后 0 去了哪里
print(f"轨道(顶点0) = {orbit_0}, 大小 = {len(orbit_0)}")
# 稳定子: 固定顶点 0 的群元素
stab_0 = [g for g in D4 if g[0] == 0]
print(f"稳定子(顶点0) 大小 = {len(stab_0)}")
print(f"|D_4| = 轨道×稳定子 = {len(orbit_0)}×{len(stab_0)} = {len(orbit_0)*len(stab_0)} ✓")
```

### 2.3 等变神经网络的群卷积直觉

```python
import numpy as np

# 演示: 平移等变 = Z^n 群卷积
# 标准卷积 f * kernel 是平移等变的: T_g(f * k) = (T_g f) * k
# 其中 T_g 是平移 g 的群作用

signal = np.random.randn(10)  # 1D 信号
kernel = np.array([1, 0, -1], dtype=float)  # 边缘检测核

# 标准卷积 (用 'same' 模式)
conv_original = np.convolve(signal, kernel, mode='same')

# 先平移信号 2 格, 再卷积
shifted_signal = np.roll(signal, 2)
conv_shifted = np.convolve(shifted_signal, kernel, mode='same')

# 平移后的卷积 == 原卷积平移
conv_original_shifted = np.roll(conv_original, 2)
equivariance_error = np.max(np.abs(conv_shifted - conv_original_shifted))
print(f"平移等变性误差 = {equivariance_error:.2e}")
print("(≈0 说明卷积是平移等变的, 这就是 Z 群卷积的本质)")

# G-CNN 推广: 把平移群 Z 替换为任意群 G
# Cohen & Welling (ICML 2016): Group Equivariant Convolutional Networks
```

完整实验代码见 [experiments/group_actions_demo.py](experiments/group_actions_demo.py)。

---

## 三、与 ML 的联系 ★（本课的核心价值）

### 3.1 CNN = $\mathbb{Z}^d$ 群卷积

标准 CNN 的平移等变性：$f * k$ 满足 $T_g(f*k) = (T_g f)*k$，其中 $T_g$ 是平移。

**Cohen-Welling (ICML 2016, [1602.07576](https://arxiv.org/abs/1602.07576) ✅)**：把 $\mathbb{Z}^d$ 替换为任意群 $G$（如 $p4$ = 平移+90°旋转），得到 **G-CNN**——对更大对称群等变。

### 3.2 等变神经网络（Equivariant NN）★

**SE(3)-等变网络**（AlphaFold 2/3 的核心）：

分子结构预测需要：旋转蛋白质后，预测结果也跟着旋转（SE(3) 等变）。用群的**表示论**构造满足等变性的层。

$$f: \mathbb{R}^3 \to \mathbb{R}^3, \quad f(R \cdot x) = R \cdot f(x), \quad R \in SO(3)$$

**SE(3)-Transformer** ([Fuchs et al. 2020, 2006.10503](https://arxiv.org/abs/2006.10503) ✅)：用球谐函数（$SO(3)$ 的不可约表示）构造等变注意力机制。

### 3.3 置换不变/等变（$S_n$ 群）

处理集合数据（点云、集合）时需要 $S_n$ 不变性（输入顺序不影响输出）：

**DeepSets** (Zaheer et al. NeurIPS 2017, [1703.06114](https://arxiv.org/abs/1703.06114) ✅)：
$$f(\{x_1, \ldots, x_n\}) = \rho\!\left(\sum_{i=1}^n \phi(x_i)\right)$$
求和天然满足 $S_n$ 不变性。

**Set Transformer** (Lee et al. ICML 2019)：用注意力机制 + 归纳池化实现 $S_n$ 不变。

### 3.4 群表示论 → 张量分解

- 群 $G$ 的不可约表示（irreps）$\Leftrightarrow$ 张量空间的"基本块"
- **Clebsch-Gordan 分解**：两个 irrep 的张量积 = irrep 的直和
- ML 中：用张量分解（CP/Tucker）压缩神经网络，理论根基来自表示论
- **等变张量网络**：用群表示约束张量结构，减少参数 + 保证对称性

### 3.5 数据增强 = 群作用的近似

对图像做翻转/旋转增强 = 用 $D_4$ 群作用扩充数据。严格等变网络在**每一层**都保持等变，而增强只在输入层施加概率约束。

$$\text{增强（软约束）} \quad \text{vs} \quad \text{等变网络（硬约束/精确）}$$

### 3.6 对称性与泛化

等变网络通过**减少假设空间**（只在对称函数空间中搜索）来提高泛化。这与 RMT 的谱约束（只考虑特定谱结构的权重）异曲同工。

---

## 四、不足层与边界

### 4.1 抽象代数的局限（在 ML 语境下）

1. **连续群比离散群难处理**：CNN（离散群 $\mathbb{Z}^d$）很成功，但 SE(3) 等变网络（连续群）的实现远更复杂（需要球谐、Clebsch-Gordan 系数等）。
2. **对称性假设可能过强**：不是所有数据都有精确对称性。蛋白质有 SE(3) 对称性，但自然图像没有精确旋转对称性。
3. **抽象代数 ≠ 表示论**：本课（Dummit-Foote 体系）偏重纯代数结构（群/环/域），ML 更需要的是**表示论**（群的线性表示），这是另一门课。

### 4.2 从理论到实践的 gap

- Sylow 定理、Galois 理论对 ML 几乎无直接应用
- 真正有用的是**前三章**（群论基础 + 群作用）+ **表示论**（很多学校不开本科表示论课）
- 如果目标是 ML，建议读完群论后直接转表示论（Fulton-Harris 或 Serre）

---

## 五、应用层速查

| 应用 | 代数工具 | 实际效果 |
|---|---|---|
| **CNN 平移等变** | $\mathbb{Z}^d$ 群卷积 | 所有 CV 模型的基础 |
| **AlphaFold** | $SE(3)$ 等变表示 | 分子结构预测突破 |
| **DeepSets / Set Transformer** | $S_n$ 不变性 | 点云、集合数据处理 |
| **数据增强** | 群作用 $G \times X \to X$ | 标准训练技术 |
| **RSA 密码** | $(\mathbb{Z}/n\mathbb{Z})^\times$ 群 | 互联网安全 |
| **椭圆曲线密码** | 有限域上的椭圆曲线群 | Bitcoin/ETH 签名 |
| **纠错码** | 有限域上的多项式环 | 通信/存储 |
| **等变张量压缩** | 群表示 + Clebsch-Gordan | 模型压缩 |

---

## 六、推荐学习路径（ML 方向）

1. **第 1-3 章**（群论基础 + 同态 + 陪集/Lagrange）→ **必读**
2. **第 4-5 章**（群作用 + Sylow）→ **必读**（理解等变网络的前提）
3. **第 7 章**（环论）→ 选读（密码学方向必读）
4. **跳过**：Galois 理论（除非你做代数几何/数论）
5. **转向表示论**：Serre, *Linear Representations of Finite Groups* 或 Fulton-Harris

> ⚠️ Dummit-Foote 全书 900+ 页，不要从头读到尾。ML 方向只需前 6 章 + 后续表示论。

---

## 七、术语对照表

| 英文 | 中文 | 说明 |
|---|---|---|
| Group | 群 | 对称性的代数化 |
| Subgroup | 子群 | 群中的群 |
| Coset | 陪集 | $gH = \{gh : h \in H\}$ |
| Normal subgroup | 正规子群 | $gNg^{-1} = N$，允许构造商群 |
| Quotient group | 商群 | $G/N$，"压缩"后的群 |
| Homomorphism | 同态 | 保运算的映射 |
| Isomorphism | 同构 | 双射同态 |
| Group action | 群作用 | $G$ 在集合上的对称操作 |
| Orbit | 轨道 | 群作用下能到的位置集合 |
| Stabilizer | 稳定子 | 固定某元素的群子集 |
| Representation | 表示 | 群 → 矩阵群的同态 |
| Irreducible representation | 不可约表示 | 不能再分解的表示"基本块" |
| Sylow $p$-subgroup | Sylow $p$-子群 | 阶为 $p^a$ 的极大子群 |
| Ideal | 理想 | 环论版"正规子群" |
| Field extension | 域扩张 | $K \supset F$，更大的域 |
| Galois group | 伽罗瓦群 | 域扩张的自同构群 |
