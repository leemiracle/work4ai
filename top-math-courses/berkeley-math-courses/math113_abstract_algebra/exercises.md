# UC Berkeley MATH 113 · 抽象代数 · 习题

> **教材**：Dummit & Foote, *Abstract Algebra* (3rd ed)
> **难度**：⭐ 基础 → ⭐⭐⭐⭐ 挑战

---

## 一、群论基础

### 题 1（⭐）群的基本性质

(a) 证明群中消去律成立：$ab = ac \Rightarrow b = c$。

(b) 证明：若 $g^2 = e$ 对所有 $g \in G$ 成立，则 $G$ 是阿贝尔群。

(c) 在 $S_3$ 中，验证 $(12)(13) \neq (13)(12)$（$S_3$ 不是阿贝尔群的最小例子）。

---

### 题 2（⭐⭐）Lagrange 定理的应用

(a) 证明费马小定理：对素数 $p$ 和任意整数 $a$ 不被 $p$ 整除，$a^{p-1} \equiv 1 \pmod{p}$。

(b) $|G| = 15$ 的群一定是循环群吗？（提示：用 Sylow 定理）

(c) 证明阶为 $p^2$（$p$ 为素数）的群是阿贝尔群。

---

## 二、群作用与轨道

### 题 3（⭐⭐）轨道-稳定子定理

$D_4$（正方形对称群，$|D_4| = 8$）作用在正方形的 4 条边上。

(a) 一条边的轨道有多大？稳定子有多大？验证轨道-稳定子定理。

(b) $D_4$ 作用在正方形的 2 条对角线上。轨道和稳定子分别是多少？

(c) $D_4$ 作用在所有有序顶点对 $(i, j)$（$i \neq j$，共 $4 \times 3 = 12$ 个）上。有多少个轨道？

---

### 题 4（⭐⭐⭐）Burnside 引理 — 项链染色

用 $k$ 种颜色给 $n$ 颗珠子的圆形项链染色，在旋转对称下本质不同的染色数？

(a) 用 Burnside 引理证明：答案为 $\frac{1}{n}\sum_{d|n} \varphi(d)\, k^{n/d}$，其中 $\varphi$ 是欧拉函数。

(b) 对 $n = 6$, $k = 3$，计算具体答案。

(c) 用代码（见 [experiments/group_actions_demo.py](experiments/group_actions_demo.py)）验证你的答案。

---

## 三、对称群与正规子群

### 题 5（⭐⭐⭐）$A_n$ 的性质

(a) 证明 $A_n$ 是 $S_n$ 的正规子群（指标 2）。

(b) 证明 $A_n$ 由所有 3-轮换 $(i\,j\,k)$ 生成。

(c) 证明 $A_4$ 不是单群（提示：找到 Klein 四元群 $V_4 \trianglelefteq A_4$）。

(d) ⭐⭐⭐⭐ 证明 $A_5$ 是单群（这是五次方程无根式解的关键）。只需给出证明思路。

---

## 四、环与理想

### 题 6（⭐⭐）环的基本性质

(a) 证明 $\mathbb{Z}/n\mathbb{Z}$ 是域当且仅当 $n$ 是素数。

(b) 在 $\mathbb{Z}[i]$（高斯整数环）中，$1 + i$ 是素元吗？$3$ 呢？

(c) 证明 $\mathbb{Z}[\sqrt{-5}]$ 不是 PID（提示：考虑理想 $(6) = (2, 1+\sqrt{-5})(3, 1-\sqrt{-5})$ 的非唯一分解）。

---

## 五、ML 应用

### 题 7（⭐⭐⭐）等变性与不变性的区别

设 $f: \mathbb{R}^n \to \mathbb{R}^n$，群 $G$ 作用在 $\mathbb{R}^n$ 上。

(a) 写出 **$G$-等变** 和 **$G$-不变** 的精确定义。

(b) 标准 CNN 卷积层 $f(x) = x * w$ 是 $\mathbb{Z}^d$-等变还是 $\mathbb{Z}^d$-不变？全局平均池化呢？

(c) 对 DeepSets $f(X) = \rho\big(\sum_i \phi(x_i)\big)$：是 $S_n$-等变还是 $S_n$-不变？

(d) 用代码验证你对 (b)(c) 的回答（修改 [experiments/group_actions_demo.py](experiments/group_actions_demo.py)）。

---

### 题 8（⭐⭐⭐⭐）等变网络的参数节省（开放题）

假设你要设计一个 $SO(3)$-等变的 3D 点云分类网络。

(a) 一个普通的 MLP 层 $\mathbb{R}^{3N} \to \mathbb{R}^{3N}$ 有多少参数？

(b) 如果强制 $SO(3)$-等变，有效参数空间缩小了多少？（提示：考虑不可约表示的维度）

(c) 等变约束如何帮助泛化？从假设空间大小的角度论证。

(d) ⚠️ 等变约束可能的副作用是什么？什么情况下等变性假设反而有害？

---

## 参考答案要点

<details>
<summary>题 2(b) 参考答案</summary>

$|G| = 15 = 3 \times 5$。Sylow 定理：$n_5 | 3$ 且 $n_5 \equiv 1 \pmod 5$ → $n_5 = 1$。$n_3 | 5$ 且 $n_3 \equiv 1 \pmod 3$ → $n_3 = 1$。所以 Sylow 5-子群和 Sylow 3-子群都是唯一的（从而是正规的）。设它们为 $P_5 \cong \mathbb{Z}_5$, $P_3 \cong \mathbb{Z}_3$。则 $G \cong P_5 \times P_3 \cong \mathbb{Z}_{15}$（循环群）。**是的，阶 15 的群一定循环。**
</details>

<details>
<summary>题 4(b) 参考答案</summary>

$n=6$, $k=3$：$\frac{1}{6}[\varphi(1)\cdot 3^6 + \varphi(2)\cdot 3^3 + \varphi(3)\cdot 3^2 + \varphi(6)\cdot 3^1]$
$= \frac{1}{6}[1 \cdot 729 + 1 \cdot 27 + 2 \cdot 9 + 2 \cdot 3]$
$= \frac{1}{6}[729 + 27 + 18 + 6] = \frac{780}{6} = 130$。
</details>
