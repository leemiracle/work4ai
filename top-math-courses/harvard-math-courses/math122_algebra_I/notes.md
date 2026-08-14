# Harvard Math 122 · 抽象代数 I 精读笔记

> **教材**：Dummit & Foote, *Abstract Algebra* (3rd ed) — Harvard 标准教材
> **参考**：[Harvard Math 122](https://www.math.harvard.edu/)；Artin *Algebra* 对照
> **特色**：Dummit-Foote 体系比 Artin 更全面，习题丰富，适合系统性学习

---

## 〇、费曼直觉层

> **代数的本质 = 发现不同数学对象共享的结构。** 群 = 对称性的语言。

Harvard 122 与 [MIT 18.701](../../mit-math-courses/18_701_algebra_I/)（Artin）和 [Berkeley 113](../../berkeley-math-courses/math113_abstract_algebra/) 内容高度重叠。核心差异：**Dummit-Foote 更系统全面**（900+ 页，涵盖群/环/域/模/Galois），Artin 更几何直觉（矩阵群视角）。

本笔记聚焦 Dummit-Foote 的**独特重点**，公共内容参见 Berkeley 113 notes.md。

---

## 一、Dummit-Foote 的独特组织

### 1.1 群论（DF Part I）

比 Artin 更详尽的覆盖：
- **群作用** + **Burnside 引理** → 等价类计数（详细组合技巧）
- **合成列**与 **Jordan-Hölder 定理** ★：群可分解为单群的"积"，顺序不影响因子
- **可解群** ★：导列 $G \trianglerighteq G' \trianglerighteq G'' \trianglerighteq \cdots$ 终止于 $\{e\}$
  - $G$ 可解 ↔ 存在合成列，因子都是阿贝尔群
  - Galois 理论中：多项式 $f$ 根式可解 ↔ $\mathrm{Gal}(f)$ 可解

### 1.2 环论（DF Part II）★（Dummit-Foote 强项）

Dummit-Foote 的环论比 Artin 更深入：
- **理想运算**：和、交、积，理想的商
- **PID vs UFD vs Euclidean 域** 的层次关系：
  $$\text{Euclidean} \subsetneq \text{PID} \subsetneq \text{UFD} \subsetneq \text{整环}$$
- **多项式环 $F[x]$**：唯一分解 → 因式分解算法
- **Noether 环** ★：理想升链条件（ACC）→ Hilbert 基定理

### 1.3 模论（DF Part III）

Dummit-Foote 独有的详细模论（很多本科课跳过）：
- **模** = 环上的"向量空间"
- **自由模**：有基的模 ≈ $R^n$
- **结构定理**（PID 上的有限生成模）：
  $$M \cong R^r \oplus R/(a_1) \oplus \cdots \oplus R/(a_m)$$
  这是**有理标准形**和**Jordan 标准形**的代数基础

### 1.4 域论与 Galois 理论（DF Part IV）

- **分裂域**：多项式 $f$ 在 $F$ 上的最小扩域，$f$ 在其中完全分裂
- **可分扩张** vs **不可分扩张**（特征 $p$ 问题）
- **Galois 对应** ★：中间域 ↔ 子群

---

## 二、与 ML 的联系

参见 [Berkeley 113 notes.md](../../berkeley-math-courses/math113_abstract_algebra/notes.md) §3（群等变神经网络、DeepSets、AlphaFold）。Dummit-Foote 的独特贡献：
- **模论 → 张量分解**：神经网络的张量压缩理论基础
- **Noether 环 → 代数几何**：多项式约束的优化问题

---

## 三、推荐路径

1. **DF Part I**（群论 1-6 章）→ 参考 Berkeley 113 notes
2. **DF Part II**（环论 7-9 章）→ **Dummit-Foote 强项，必读**
3. **DF Part III**（模论 10-12 章）→ 选读（Jordan 标准形理论）
4. **DF Part IV**（Galois 13-14 章）→ 跳过（除非做数论/代数几何）

> **关键建议**：不要从头读 900 页。读群论后直接转 [Berkeley 113](../../berkeley-math-courses/math113_abstract_algebra/) 的 ML 应用视角 + 表示论。
