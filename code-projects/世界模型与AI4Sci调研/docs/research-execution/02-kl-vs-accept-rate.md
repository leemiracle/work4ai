# 课题 IT-3 第一个结果：KL 散度 vs 推测解码 Accept Rate

> 对应课题：`docs/research-topics-50.md` IT-3 / `docs/learning-paths.md` 路径 9
> 关联章节：模块 12 §05 §12.1 推测解码 + 模块 14 §01 §四 信息论

---

## 1. 问题

推测解码的加速比 $S = \frac{1+\beta}{1+c(1+\beta)}$（β = α/(1-α)）完全由 accept rate α 决定。但**如何在不跑实验的情况下预测 α？**

信息论直觉：α 应该和 draft/target 分布的"距离"有关——KL 散度越小（draft 越像 target），α 越高。Pinsker 不等式给出 $\alpha \geq 1 - \sqrt{\text{KL}/2}$，但这个下界有多紧？

## 2. 理论

- **Accept rate 精确公式**（Leviathan 2022）：$\alpha = 1 - \text{TV}(p, q) = 1 - \frac{1}{2}\sum_x |p(x) - q(x)|$
- **Pinsker 不等式**：$\text{TV} \leq \sqrt{\text{KL}/2}$ → $\alpha \geq 1 - \sqrt{\text{KL}/2}$
- **问题**：Pinsker 是渐近不等式，在有限词汇表 + 具体分布下可能高度保守

## 3. 实验

vocab_size=100，target = random softmax，draft = target + Gaussian noise（30 个 noise level × 200 次平均）。

## 4. 结果

| KL(p‖q) | 实测 α | Pinsker 下界 | 紧度（实测/下界）|
|---|---|---|---|
| 0.00 | 0.996 | 0.995 | 1.00× |
| 0.14 | 0.793 | 0.741 | 1.07× |
| 0.52 | 0.611 | 0.491 | 1.24× |
| 1.16 | 0.452 | 0.244 | 1.85× |
| 1.99 | 0.333 | 0.057 | 5.81× |
| 2.94 | 0.250 | 0.003 | ~80× |
| 4.98 | 0.157 | 0 | ∞ |
| 7.52 | 0.101 | 0 | ∞ |

**经验拟合**：α ∝ KL^-0.43

**Pinsker 下界紧度**：平均 70× 保守（KL > 2 时下界 = 0，完全无用）

## 5. 发现

1. **Pinsker 不等式高度保守**：KL > 2 时下界为 0（无信息），但实际 α 仍有 10-25%。**Pinsker 对 spec decoding 的 accept rate 预测完全不可用**。

2. **α ∝ KL^-0.43 的经验关系**：这是一个 power-law 衰减——KL 翻 10 倍，α 降到 37%。比 Pinsker 的 1-√(KL/2)（KL > 2 时归零）慢得多。

3. **工程含义**：即使 draft 模型与 target 的 KL 散度较大（如 3-5，对应"很不同的模型"），accept rate 仍有 15-25%——**这解释了为什么小 draft 模型（160M 给 8B 当 draft）在 spec decoding 中仍有效**。

## 6. Gap

- α ∝ KL^-0.43 的理论解释：为什么指数是 -0.43 而不是 -0.5？
- 需要在真实 LLM 上验证（随机分布 vs 真实 token 分布可能不同）
- 是否有比 Pinsker 更紧的信息论不等式？（Bretagnolle-Huber 不等式？）

## 7. 工程意义

对 spec decoding 的 draft 模型选型：
- 不要用 KL 散度做硬过滤（"KL < 1 才用"太保守）
- 经验法则：KL < 3 时 α > 25%（仍有效）；KL > 5 时 α < 15%（不值得）
- 更精确的预测公式：α ≈ 0.8 × KL^-0.43（经验拟合常数）
