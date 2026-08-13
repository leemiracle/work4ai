# UT Austin M 365C — Real Analysis I

> **学校**：UT Austin | **学期**：Fall/Spring | **学分**：3
> **一手来源**：[catalog.utexas.edu/search/?P=M+365C](https://catalog.utexas.edu/search/?P=M+365C) + [utdirect.utexas.edu/.../10300546](https://utdirect.utexas.edu/apps/student/coursedocs/nlogon/download/10300546/)（一手核实）

## 课程信息
- **编号**：M 365C（与 M 361K 互斥）
- **先修**：M 325K / 328K / 341 中两个 + 证明能力
- **教材**：**Rudin, *Principles of Mathematical Analysis* 3/e** ★
- **特色**：**UT Austin 本科实分析最严格版本**（用 Rudin；M 361K 是较友好的版本用 Bartle）

## 教学大纲（一手核实自 Spring 2020 Lomeli 讲义）
1. Real number system
2. **Metric spaces** ★
3. Sequences, limits
4. Continuity（在 metric spaces 中）
5. **Open, closed, compact sets** ★
6. Differentiation
7. Uniform convergence
8. Riemann integration

**重点**：ε-δ 论证 + 序列方法 + 拓扑概念

## 与 ML 的关联
- 数学成熟度训练
- 紧致性 → 泛函分析预备
- 学完后：能读 ML 理论论文的"证明部分"

## 参考资源
- Rudin, *Principles of Mathematical Analysis* (3rd, McGraw-Hill, 1976) ISBN 978-0070542358
- Lomeli 讲义: [ma.utexas.edu/users/lomeli/m365c](http://www.ma.utexas.edu/users/lomeli/m365c)
- MIT 对照：[MIT 18.100B](../../mit-math-courses/18_100B_real_analysis/)

## 学习建议
- **先修 M 361K**（Bartle & Sherbert）再上 365C（Rudin）——官方推荐
- **节奏**：每周 5-7 小时，14 周

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
M 361K (Bartle)       →   UT Austin M 365C       →   M 381C 研究生
(单变量 ε-δ)               (Rudin 度量空间)            (测度论)
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 基础 | M 361K | Bartle 单变量 |
| **进阶 ★** | **M 365C** | **Rudin 度量空间标准版** |
| 高阶 | M 381C | Lebesgue + 泛函 |

## 🔬 理论联系实际
1. **紧致 + 连续 → 极值定理**: 权重衰减 → loss 最小值存在
2. **ε-δ 连续 → ReLU**: 连续但不可微 → 次梯度
3. **MVT → 优化可达性**: 梯度路径上临界点存在
4. **一致收敛 → 泛化**: $\sup_\theta |\hat{L}_n - L| \to 0$ → ERM 一致
5. **幂级数 → softmax**: $e^x = \sum x^k/k!$ 收敛保证

## 🆕 2024-2026 最新研究
- **泛化理论**: 一致收敛 = 泛化保证的分析基础 ⚠️
- **Double descent**: 紧致性分析的突破 ⚠️
- **自动 ε-δ**: Lean 形式化 ML 分析 ⚠️

---

📌 **下一步**：→ [M 361K Introduction to Real Analysis (Bartle)](../m365c_real_analysis/) 或 [M 381C 研究生 Real Analysis](../m381c_real_analysis_graduate/)
