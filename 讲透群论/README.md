# 讲透群论 · 对称性的代数（基于 Milne Group Theory）

> 用「直觉 → 数学 → Python 实验 → Lean 形式化 → 应用」的方式，把 J.S. Milne《Group Theory》（免费 PDF，https://www.jmilne.org/math/CourseNotes/GT.pdf）讲透。
>
> Milne 是纯代数方向的"David Tong"——免费、权威、覆盖全。

---

## 〇、为什么群论

### 0.1 群 = 对称性

群论的本质是**对称性**。一个集合的所有"对称变换"（保持结构的双射）构成一个群。

- 三角形的对称 = $D_3$（二面体群）
- 立方体的对称 = $S_4$
- 数域的自同构 = Galois 群
- 物理定律的对称 = 规范群（粒子物理标准模型）

### 0.2 Galois 的革命

故事见 [`../top-math-courses/MATH_STORIES.md`](../top-math-courses/MATH_STORIES.md) 故事 8。Galois 用群论证明 **5 次方程没有求根公式**——把"解方程"变成"研究对称"。

### 0.3 你的应用

- **ML**：等变神经网络（equivariant NN）= 用群作用保持对称
- **物理**：粒子物理的标准模型用 Lie 群
- **密码学**：椭圆曲线群
- **形式化**：Mathlib 的 `Algebra.GroupTheory.*` 极成熟

---

## 一、章节（基于 Milne）

| # | 文件 | 主题 | Milne 章 | 状态 |
|---|------|------|---------|------|
| 00 | [`00-群论是什么.md`](00-群论是什么.md) | 对称性 + 历史 + 直觉 | Ch 1 | ✅ |
| 01 | [`01-Sylow定理.md`](01-Sylow定理.md) | Sylow 三大定理（群论最深刻定理之一）| Ch 5 | ✅ |
| 02 | `02-群作用与轨道.md` | 群作用 / 轨道-稳定化子 | Ch 4-5 | 📝 |
| 03 | `03-对称群与交错群.md` | $S_n$, $A_n$，单性 | Ch 4 | 📝 |
| 04 | `04-正规子群与商.md` | 商群 / 同构定理 | Ch 2-3 | 📝 |
| 05 | `05-直积与半直积.md` | 分类有限群的基础 | Ch 6-7 | 📝 |
| 06 | `06-可解群与幂零群.md` | Galois 理论的工具 | Ch 6 | 📝 |
| 07 | `07-自由群与展示.md` | 计算群论 | Ch 9 | 📝 |

---

## 二、前置

- 高中数学 + 集合概念
- Python（实验用）
- Lean 4（形式化用，可选）

---

## 三、与 work4ai 联动

- [`../top-math-courses/MATH_STORIES.md`](../top-math-courses/MATH_STORIES.md) 故事 8 Galois
- [`../top-math-courses/TEXTBOOK_LIBRARY.md`](../top-math-courses/TEXTBOOK_LIBRARY.md) §二代数方向
- [`../讲透Lean4数学/`](../讲透Lean4数学/) 形式化群

---

📌 **下一步**：读 [`00-群论是什么.md`](00-群论是什么.md)。
