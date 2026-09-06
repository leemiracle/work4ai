# Stanford MATH 171 — Fundamental Concepts of Analysis

> **学校**：Stanford
> **一手来源**：[mathematics.stanford.edu/academics/math-course-flowchart](https://mathematics.stanford.edu/academics/math-course-flowchart)

## 课程信息
- **编号**：MATH 171
- **先修**：MATH 115 + MATH 61CM/DM 或 MATH 51 + 113
- **教材**：Rudin *Principles*；或 Pugh
- **特色**：**数学专业核心实分析**（115 的进阶版）

## 教学大纲
1. Metric spaces ★
2. Uniform convergence
3. Stone-Weierstrass
4. Arzela-Ascoli
5. Inverse / Implicit function theorem
6. Lebesgue 积分入门（如时间允许）

## 与 ML 的关联
- 数学成熟度训练
- 学完后：能读 ML 理论论文证明

## 参考资源
- Rudin, *Principles of Mathematical Analysis*
- Pugh, *Real Mathematical Analysis*（更直观）
- MIT 对照：[18.100B](../../mit-math-courses/18_100B_real_analysis/)

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
MATH 115 实分析        →   Stanford MATH 171      →   MATH 230A 概率
(Ross/Rudin 单变量)         (Rudin 度量空间)            泛函分析
```

| 阶梯 | 课程 | 核心内容 |
|---|---|---|
| 入门 | MATH 115 | 单变量 ε-δ |
| **进阶 ★** | **MATH 171** | **度量空间 + Stone-Weierstrass + Arzelà-Ascoli** |
| 高阶 | Harvard Math 114 | 测度论 + 泛函 |

## 🔬 理论联系实际
1. **Stone-Weierstrass → UAT**：多项式稠密 → 神经网络万能逼近
2. **Arzelà-Ascoli → 泛化界**：等度连续+有界 → 覆盖数有限 → Rademacher 复杂度
3. **压缩映射 → SGD 收敛**：$T(\theta) = \theta - \eta \nabla L$, $|1-\eta L_{lip}| < 1$
4. **反函数定理 → Normalizing Flows**：$p_Y(y) = p_X(f^{-1}(y)) |\det J_{f^{-1}}|$
5. **隐函数定理 → 隐式表示**：约束 $F(x,y) = 0$ 局部定义 $y = g(x)$

## 🆕 2024-2026 最新研究
- **NTK 收敛性证明**直接用 Arzelà-Ascoli（等度连续+有界 → 一致收敛子序列）⚠️
- **Normalizing Flows** 的可逆性依赖反函数定理 + Jacobian 行列式 ⚠️
- **Implicit Neural Representations**（SIREN, NeRF）用隐函数定理 ⚠️

---

📌 **下一步**：→ [MATH 230A Probability Theory](../math230A_probability_theory/)
