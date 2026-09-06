# Princeton MAT 345 · 代数 I 精读笔记

> **教材**：Artin, *Algebra* (2nd ed) — Princeton 使用 Artin 体系
> **参考**：[math.princeton.edu](https://www.math.princeton.edu/)；Dummit-Foote 对照
> **定位**：与 [MIT 18.701](../../mit-math-courses/18_701_algebra_I/)（同为 Artin 体系）和 [Harvard 122](../../harvard-math-courses/math122_algebra_I/)（DF 体系）高度重叠

---

## 〇、核心定位

Princeton MAT 345 使用 Artin 教材，与 MIT 18.701 完全同源。Artin 的独特视角：**从矩阵群出发**（$GL_n$, $O_n$, $SL_n$），而非从抽象公理出发。

详细笔记参见 [MIT 18.701 notes.md](../../mit-math-courses/18_701_algebra_I/notes.md) 和 [Berkeley 113 notes.md](../../berkeley-math-courses/math113_abstract_algebra/notes.md)。本笔记聚焦 Princeton 的教学特色。

---

## 一、Artin 体系的独特之处

### 1.1 几何直觉优先 ★

Artin 从**具体矩阵群**出发：
- $GL_n(\mathbb{R})$：一般线性群（可逆矩阵）
- $O_n$：正交群（保长度）
- $SL_n$：特殊线性群（行列式 = 1）
- 用这些具体例子建立对"群 = 对称"的直觉

**与 Dummit-Foote 的区别**：DF 从抽象群公理开始（更系统但更枯燥），Artin 从几何对称开始（更直觉但不够系统）。

### 1.2 核心主题

1. **矩阵群**：$GL_n$ 的子群结构
2. **群作用**：$G$ 在集合上的对称操作 → 轨道/稳定子
3. **表示论入门**：群的线性表示 → 不可约表示
4. **对称群 $S_n$**：排列的代数结构
5. **环/域**：多项式环 → 域扩张

### 1.3 Princeton 数论传统

Princeton 数论极强（Andrew Wiles 证明 Fermat 大定理的工作就在 Princeton）。MAT 345 的代数课会有更强的数论倾向：
- 有限域 $\mathbb{F}_p$ 的结构
- 多项式在有限域上的因式分解
- 椭圆曲线的群结构

---

## 二、与 ML 的联系

参见 [Berkeley 113 notes.md §3](../../berkeley-math-courses/math113_abstract_algebra/notes.md)。核心要点：
- 群作用 → 等变神经网络（G-CNN, SE(3)-Transformer, AlphaFold）
- 矩阵群 → 线性表示论（张量分解、网络压缩）
- 对称群 → 置换不变性（DeepSets）

---

## 三、推荐路径

1. **Artin 第 1-7 章**：矩阵群 + 群论基础 + 群作用 → **核心**
2. **Artin 第 8-9 章**：线性群 + 群表示 → **ML 方向重点**
3. **跳过**：第 15-16 章 Galois 理论（除非做数论）
4. **交叉**：[MIT 18.701](../../mit-math-courses/18_701_algebra_I/)（Artin 原版视频课）
