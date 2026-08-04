# 数学 · Neurosymbolic 理论

> **博士级**：神经 + 符号融合的数学基础。

## 一、为什么需要 Neurosymbolic

| 神经 | 符号 |
|---|---|
| 感知强 | 推理强 |
| 学习强 | 学习弱 |
| 黑箱 | 可解释 |

**互补性** → 融合是 AI 下一范式候选。

## 二、融合的几种数学形式

### 2.1 嵌入式（embedding）

符号 → 神经表示（Word2Vec / Knowledge Graph Embeddings）

**形式**：实体 $e \in \mathcal{E}$ → 向量 $\mathbf{v}_e \in \mathbb{R}^d$

**TransE**：$\mathbf{v}_{head} + \mathbf{v}_{relation} \approx \mathbf{v}_{tail}$

### 2.2 可微逻辑（Differentiable Logic）

经典一阶逻辑不可微。改造：

**模糊逻辑**：$\neg x = 1 - x$, $x \land y = \min(x, y)$
**乘积 t-norm**：$x \land y = xy$

→ 可用 SGD 优化。

### 2.3 Probabilistic Logic Programming

**ProbLog / DeepProbLog**：
- 符号事实有概率
- 神经网络产生概率

形式：
$$P(\text{conclusion}) = \sum_{\text{proofs}} P(\text{proof})$$

### 2.4 LLM + Tool Use

LLM 生成函数调用 → 符号工具（Lean / 求解器）执行。

**数学**：
- LLM: $P(\text{action} | \text{state})$
- 符号: $\text{action}(x) \to y$
- 循环

## 三、AlphaProof 的架构（2024）

```
自然语言题
   ↓ Gemini（LLM 翻译）
Lean 形式化
   ↓ AlphaZero 风格 MCTS + RL
证明搜索
   ↓ Lean 验证
通过 = True proof
```

**核心**：神经给"直觉"，Lean 给"验证"。

## 四、理论问题

### 4.1 可表达性 vs 可学习性 trade-off

神经：任意函数逼近，但需数据
符号：精炼，但需手工编码

### 4.2 不可通约性

Neurosymbolic 是**新范式**还是**旧 trick**？（[`讲透AI历史/advanced/01`](../../讲透AI历史/advanced/01-范式转移的库恩分析.md)）

### 4.3 评估难题

Neurosymbolic 系统**怎么 benchmark**？

## 五、当前前沿

- **DeepProbLog**（Manhaeve 2018）
- **Logic Tensor Networks**（Serafini）
- **SATNet**（Wang 2019）
- **AlphaProof / AlphaGeometry**（DeepMind 2024）
- **LLM + Lean**（LeanDojo, Lean Copilot）

## 六、博士级练习

1. 用 ProbLog 实现简单知识库
2. 实现可微 And/Or
3. 设计 Neurosymbolic benchmark

## 关键引用

- Garcez 2015 *Neural-Symbolic Learning and Reasoning*
- Manhaeve 2018 DeepProbLog
- Yang 2023 *Neurosymbolic AI 综述*
