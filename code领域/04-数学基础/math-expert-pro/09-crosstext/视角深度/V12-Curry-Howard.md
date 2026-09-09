# V12 · Curry-Howard 翻译视角 · "命题=类型，证明=程序"

> 28 视角深度 · 第 12 份 · C 族跨学科翻译

---

## 🌌 哲学根基
**20 世纪最深洞察之一**：数学证明与计算机程序是同一事物的两面。Curry 1934 + Howard 1969 的对应：每个命题 = 一个类型；每个证明 = 该类型的项（程序）。

## 📜 发展史
- **1934 Haskell Curry**：命题 ↔ 类型观察
- **1969 William Howard**：形式化对应
- **1972 Per Martin-Löf**：直觉类型论
- **1985 Coquand-Huet**：Calculus of Constructions（Coq 基础）
- **2013 Lean / 2016 Lean 4**：现代形式化工具

## 🎓 大师方法
- **Per Martin-Löf**：依赖类型论
- **Thierry Coquand**：构造演算
- **Philip Wadler**《Theorems for Free》
- **Sterling Harper**：定理证明器设计
- **Carlo Angiuli**：Cartesian Cubical Type Theory

## 📚 475 本应用

| 数学 | 程序 | 书 |
|------|-----|----|
| 命题 $A$ | 类型 $A$ | 数理逻辑 |
| $A \to B$ | 函数类型 | 全部 |
| $A \land B$ | 积类型 $A \times B$ | 同调 |
| $A \lor B$ | 和类型 $A + B$ | 离散 |
| $\exists x. P(x)$ | Σ 类型 | HoTT |
| $\forall x. P(x)$ | Π 类型 | 类型论 |
| $\neg A$ | $A \to \bot$ | 直觉主义 |
| 数学归纳法 | 结构递归 | Lean |

## 🔧 完整方法论（10 步）
1. 命题类型化 2. 假设变元 3. 模式匹配 4. 递归 5. extract 程序 6. 反向（程序→证明）7. 依赖类型 8. 同伦类型论 9. 立方类型论 10. 形式化

## ⚠️ 失败边界
- ❌ 经典数学（排中律）不直接对应
- ⚠️ 翻译可能失真

## 🤝 协同：V12 + V13（Lean 实操）/ V08（范畴语义）

## 💻 实战
```lean
theorem modus_ponens (A B : Prop) (h1 : A → B) (h2 : A) : B := h1 h2
```

## 🎯 独家切面：**证明的"计算内容"**——纯数学隐藏的可执行部分。

---

> 📖 配套：[V08 范畴](V08-范畴俯瞰.md) · [V13 Lean](V13-Lean形式化.md) · [C 族深度](C族跨学科翻译-深度.md)
