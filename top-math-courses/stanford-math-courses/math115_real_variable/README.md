# Stanford MATH 115 — Functions of a Real Variable

> **学校**：Stanford
> **一手来源**：[mathematics.stanford.edu/academics/math-course-flowchart](https://mathematics.stanford.edu/academics/math-course-flowchart)

## 课程信息
- **编号**：MATH 115（4 units）
- **先修**：MATH 51 或 MATH 56
- **教材**：Ross, *Elementary Analysis*；或 Rudin
- **特色**：本科实分析入门

## 教学大纲
1. Real numbers构造（Dedekind）
2. Sequences & series
3. Continuity, uniform continuity
4. Differentiation
5. Riemann 积分
6. Sequences of functions
7. Metric spaces（如时间允许）

## 与 ML 的关联
- 实分析入门训练
- 与 [Princeton MAT 215](../../princeton-math-courses/mat215_analysis/) 同类

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
MATH 51 微积分        →   Stanford MATH 115      →   MATH 171 分析
(基本证明能力)              (实分析入门)               MATH 113 线代
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 入门 | Berkeley Math 104 | Ross 最友好 |
| **友好 ★** | **Stanford MATH 115** | **Ross/Rudin** |
| 进阶 | Stanford MATH 171 | Rudin 度量空间 |

## 🔬 理论联系实际
1. **Dedekind 切 → 浮点数表示**：实数构造解释了为什么浮点数有精度限制
2. **紧致性 → 极值定理**：loss 最小值存在性
3. **Taylor 定理 → Newton 法**：$\theta_{k+1} = \theta_k - H^{-1}\nabla L$
4. **一致连续 → Lipschitz**：GAN 判别器稳定性
5. **级数收敛 → 激活函数展开**：sigmoid/tanh 的有效线性近似范围

## 🆕 2024-2026 最新研究
- **NTK 一致收敛**用到 MATH 115 的级数收敛判别 ⚠️
- **Diffusion model** 的 Taylor 展开分析推导 Euler-Maruyama 方法 ⚠️

---

📌 **下一步**：→ [MATH 171 Analysis](../math171_analysis_fundamentals/)
