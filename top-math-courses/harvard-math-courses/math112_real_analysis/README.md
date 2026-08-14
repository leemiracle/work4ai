# Harvard Math 112 — Introductory Real Analysis

> **学校**：Harvard | **学期**：Spring
> **一手来源**：[math.harvard.edu/course/mathematics-112-spring](https://www.math.harvard.edu/course/mathematics-112-spring/)

## 课程信息
- **编号**：Math 112
- **先修**：Math 21a/b 或 Math 22a/b 或 Math 23a/b + proof 能力
- **教材**：Rudin, *Principles of Mathematical Analysis*；替代 Pugh
- **特色**：**Harvard 标准实分析**（不像 Math 55 那么极端）

## 教学大纲
1. Metric spaces（度量空间）
2. Convergence of sequences & series
3. Continuity, uniform convergence
4. Spaces of functions
5. Riemann 积分

## 与 ML 的关联
- 实分析标准训练
- 学完后：能读 ML 理论论文的"证明部分"

## 参考资源
- Rudin, *Principles of Mathematical Analysis*
- Pugh, *Real Mathematical Analysis*（更友好）
- MIT 对照：[MIT 18.100B](../../mit-math-courses/18_100B_real_analysis/)

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
Math 21a/b 微积分     →   Harvard Math 112        →   Math 114 测度论
Math 23a/b 证明       →   (Rudin/Pugh 度量空间)         Math 131 拓扑
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 极端 | Harvard Math 55 | 一年讲完本科+研究生 |
| **标准 ★** | **Harvard Math 112** | **Rudin 度量空间标准版** |
| 进阶 | Harvard Math 114 | 测度论 + 泛函 |

## 🔬 理论联系实际
1. **ε-δ 连续 → ReLU**: 连续但不可微 → PyTorch 使用次梯度
2. **紧致+连续 → 极值定理**: 权重衰减 → loss 最小值存在
3. **一致收敛 → 泛化**: 逐点收敛 ≠ 泛化好
4. **Stone-Weierstrass → UAT**: 多项式稠密 → 神经网络万能逼近
5. **Arzelà-Ascoli → 覆盖数**: 泛化界 $O(\sqrt{d/n})$ 的推导基础

## 🆕 2024-2026 最新研究
- **NTK** 的 Arzelà-Ascoli 应用 ⚠️
- **Double descent** 的紧致性分析 ⚠️

---

📌 **下一步**：→ [Harvard Math 114 Measure](../math114_measure_integration/)
