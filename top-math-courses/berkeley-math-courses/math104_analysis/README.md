# UC Berkeley MATH 104 — Introduction to Analysis

> **学校**：Berkeley
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses) + Major Map

## 课程信息
- **编号**：MATH 104 / 105（honors）
- **先修**：MATH 53 + 54 + **证明能力**（**官方推荐先上 110 再上 104**）
- **教材**：**Ross, *Elementary Analysis: The Theory of Calculus*** ★
- **特色**：**本科实分析入门**——比 Rudin 友好

## 教学大纲
1. Real numbers & supremum
2. Sequences & limits
3. Series
4. Continuity
5. Differentiation
6. Integration
7. Sequences of functions
8. Taylor series

## 与 ML 的关联
- 实分析入门的**最佳起点**（比 Rudin 友好）
- 学完后：能 ε-δ 证明，准备读 Rudin

## 参考资源
- Ross, *Elementary Analysis* (2nd ed, Springer) ISBN 978-1461462705
- 替代：Pugh, *Real Mathematical Analysis*
- MIT 对照：[18.100A](../../mit-math-courses/18_100B_real_analysis/)

## 学习建议
- **强烈推荐先于 110 学**：但 Berkeley 建议先 110（因为 110 是更友好的 proof 入门）
- **节奏**：每周 5-6 小时，12-14 周

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
微积分 + 证明入门     →   Berkeley Math 104      →   Math 110 线代
(Ross 友好入门)              (ε-δ + 序列)                MIT 18.100B (Rudin)
                                                         Math 105 honors
```

| 阶梯 | 课程 | 教材 | 角色 |
|---|---|---|---|
| **最友好 ★** | **Berkeley Math 104** | **Ross** | **零基础实分析入门** |
| 标准 | MIT 18.100B | Rudin | 度量空间严格 |
| 严格 | Princeton MAT 215 | Rudin/Tao | 证明密集 |

> Ross 教材以**循序渐进**著称——比 Rudin 友好得多。适合第一次接触 ε-δ 的人。

## 🔬 理论联系实际

### 应用 1：单调收敛定理 → loss 单调下降
SGD 在凸函数上 loss 单调递减有下界 → 由单调收敛定理收敛。

### 应用 2：Taylor 定理 → 梯度下降分析
$L(\theta_{k+1}) \approx L(\theta_k) + \nabla L^T (-\eta \nabla L) + \frac{\eta^2 L}{2}\|\nabla L\|^2$（Lipschitz 梯度条件下）。

### 应用 3：一致连续 → Lipschitz 条件 → GAN 稳定性
判别器要求 Lipschitz 连续 = 一致连续的特例。

## 🆕 2024-2026 最新研究
- **NTK 理论**（2018 起）的一致收敛证明用到 Ross Ch 16-17 的工具
- **知识蒸馏**中温度参数的极限行为 = Ross 习题 $\sigma(nx)$ 的逐点收敛 ⚠️

---

📌 **下一步**：→ [MATH 110 Linear Algebra](../math110_linear_algebra/)
