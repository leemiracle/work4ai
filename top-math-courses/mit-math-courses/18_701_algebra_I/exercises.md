# MIT 18.701 · 习题集

---

### Q1.1（基础）
证明 $S_3$（3 阶对称群）同构于 $D_3$（正三角形二面体群）。

<details><summary>解</summary>

$S_3$ 有 6 个元素：$e, (12), (13), (23), (123), (132)$。
$D_3$ 有 6 个元素：$e, r, r^2, s, rs, r^2s$（$r$ = 120° 旋转，$s$ = 翻转）。

对应：$(123) \leftrightarrow r$（3-轮换 = 旋转），$(12) \leftrightarrow s$（对换 = 翻转）。

验证关系：$r^3 = e$, $s^2 = e$, $srs = r^{-1}$ 在两边都成立。✓

> $S_n \cong D_n$ **只对 $n=3$ 成立**。$D_n$ 的阶是 $2n$，$S_n$ 的阶是 $n!$，只有 $n=3$ 时相等。
</details>

### Q1.2（中等）
用 Lagrange 定理证明：阶为 $p$（素数）的群同构于 $\mathbb{Z}/p\mathbb{Z}$。

<details><summary>解</summary>

设 $|G| = p$。取 $a \neq e \in G$，由 Lagrange，$|\langle a \rangle|$（$a$ 生成的子群阶）整除 $p$。因 $a \neq e$，$|\langle a \rangle| > 1$，所以 $|\langle a \rangle| = p$。故 $\langle a \rangle = G$，$G$ 是循环群。

阶 $p$ 的循环群唯一（同构意义下）$\Rightarrow G \cong \mathbb{Z}/p\mathbb{Z}$。
</details>

### Q1.3（中等）
$S_4$ 中 $(1234)$ 的共轭类有哪些元素？共轭类的大小？

<details><summary>解</summary>

共轭元素有相同的轮换类型。$(1234)$ 是 4-轮换，共轭类 = 所有 4-轮换。

4-轮换个数：$\frac{4!}{4} = 6$（每个 4-轮换有 4 种写法，$4!/4 = 6$）。

中心化子大小：$|C_G((1234))| = 24/6 = 4$，即 $\langle (1234) \rangle$。

**ML 关联**：置换等变网络需理解置换的共轭类（相同 cycle type 的置换"等价"）。
</details>

### Q1.4（中等 — 表示论）
验证 $S_3$ 的特征标正交性。$S_3$ 有 3 个不可约表示（平凡、符号、标准），验证 $\langle \chi_i, \chi_j \rangle = \delta_{ij}$。

<details><summary>解</summary>

共轭类：$C_1 = \{e\}$, $C_2 = \{(12),(13),(23)\}$, $C_3 = \{(123),(132)\}$，大小 $1, 3, 2$。

| | $e$ (size 1) | $(12)$ (size 3) | $(123)$ (size 2) |
|---|---|---|---|
| 平凡 $\chi_1$ | 1 | 1 | 1 |
| 符号 $\chi_2$ | 1 | -1 | 1 |
| 标准 $\chi_3$ | 2 | 0 | -1 |

$\langle \chi_1, \chi_1 \rangle = (1\cdot1 + 3\cdot1 + 2\cdot1)/6 = 1$ ✓
$\langle \chi_1, \chi_2 \rangle = (1 + 3(-1) + 2)/6 = 0$ ✓
$\langle \chi_3, \chi_3 \rangle = (4 + 0 + 2)/6 = 1$ ✓
$\langle \chi_1, \chi_3 \rangle = (2 + 0 - 2)/6 = 0$ ✓

**ML 关联**：等变神经网络中，特征标的正交性保证不同对称模式的解耦。
</details>

### Q1.5（开放 — Sylow）
阶为 15 的群一定是循环群吗？

<details><summary>提示</summary>

$15 = 3 \times 5$。Sylow 定理：$n_5 | 3$ 且 $n_5 \equiv 1 \pmod{5}$ → $n_5 = 1$。$n_3 | 5$ 且 $n_3 \equiv 1 \pmod{3}$ → $n_3 = 1$。

唯一的 Sylow 3-子群和 Sylow 5-子群都是正规的。$G \cong \mathbb{Z}/3 \times \mathbb{Z}/5 \cong \mathbb{Z}/15$（因 $\gcd(3,5)=1$）。**是循环群**。
</details>

### Q1.6（开放 — ML & 群表示）
等变神经网络为什么需要群表示论？CNN 的平移等变如何用群论描述？

<details><summary>提示</summary>

CNN 的卷积 $f * g$ 满足 $T_a(f*g) = T_a f * g$（平移算子 $T_a$ 与卷积可交换）。这正是 **$\mathbb{Z}^d$ 群作用的等变性**。

推广到其他群（旋转群 $SO(3)$、置换群 $S_n$）需要群卷积：$(f *_G g)(x) = \sum_{g \in G} f(g^{-1}x)g$。

群表示论告诉我们如何分解特征空间为不可约表示的直和（类比 FFT 把信号分解为频率分量）。Cohen-Welling 2016 的 G-CNN 是理论基础。
</details>
