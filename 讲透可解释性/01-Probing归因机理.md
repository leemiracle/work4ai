# 01 — Probing、归因与机理可解释性：打开黑箱的三把钥匙

> 「讲透可解释性」核心章。00 讲了"为什么模型是黑箱"。本篇讲三种主流方法——**probing**（探测）、**attribution**（归因）、**mechanistic**（机理）——从外部观察到内部解剖，层层深入。

---

## 1. 灵魂：可解释性的三个层次

$$
\boxed{\underbrace{\text{Probing}}_{\text{模型学到了什么}} < \underbrace{\text{Attribution}}_{\text{这个预测因为什么}} < \underbrace{\text{Mechanistic}}_{\text{模型内部怎么算}}}
$$

---

## 2. Probing（探测）：表征里有什么

### 2.1 思路

训一个**简单分类器**（线性 probe）读模型的中间层表征，预测某个属性（词性/情感/语法）。

- probe 准确率高 → 表征里**编码了**这个属性
- probe 准确率低 → 没编码（或编码方式非线性）

### 2.2 控制实验

probe 太强会"自己学"，不是"读表征"。用**控制任务**（Hewitt & Liang 2019）：随机标签的 probe 准确率应该低——确认 probe 在读而非学。

### 2.3 发现

BERT 的中层编码了语法（主谓宾），高层编码了语义。GPT 的中间层有"induction head"（in-context learning 的神经基础）。

---

## 3. Attribution（归因）：这个预测归功于哪个输入

### 3.1 梯度归因

输入的梯度 $\partial y / \partial x_i$ 大 → 该输入特征重要。代表：**Integrated Gradients**（沿路径积分梯度，消除噪声）。

### 3.2 注意力作为归因？

"attention 权重高 = 模型看了那里"——**这个直觉部分错**。attention 不一定是归因（权重可分散/不可加和）。更可靠的是**attention rollout**（跨层累积）或**attention flow**。

### 3.3 LIME / SHAP

局部扰动输入，看预测怎么变——**模型无关**的归因。SHAP 有博弈论保证（Shapley 值）。

---

## 4. Mechanistic Interpretability（机理）：逆向工程模型内部

### 4.1 思路

不只看"表征有什么"，而是**找出模型内部执行的具体算法**。像逆向工程一个程序——找出"这个电路实现了什么功能"。

### 4.2 Circuit 分析

Anthropic 的研究方法：在小型 transformer 里找**电路**（neuron 的组合），如：
- **Induction head**（Olsson 2022）：复制前文模式的电路，ICL 的基础
- **名字完成电路**：补全人名的特定 neuron 组合

### 4.3 Sparse Autoencoder（SAE）

2024 突破：用 SAE 把 neuron 激活分解成**可解释特征**——发现单个 neuron 其实是多个特征的叠加（superposition）。

---

## 5. 可解释性的价值

| 场景 | 用哪种 |
|---|---|
| **调试模型**（为什么错）| Attribution |
| **科学理解**（LLM 怎么工作）| Mechanistic |
| **合规/审计**（有没有偏见）| Probing + Attribution |
| **安全**（对齐/欺骗检测）| Mechanistic + SAE |

---

## 6. 批判性

- **Probing 是"关联"不是"因果"**：表征里有语法 ≠ 模型用语法推理
- **Attribution 不唯一**：不同方法（梯度/LIME/SHAP）给不同归因，没有"正确"答案
- **Mechanistic 太贵**：只能在小模型上做，LLM 规模的逆向工程极难
- **可解释性 ≠ 可靠性**：理解了模型不一定让它更安全（可能发现它在欺骗）

> **诚实结论**：可解释性是 AI 安全的"必经之路"。SAE/circuit 分析是 2024-2025 的突破，但规模化的 LLM 可解释性仍开放。理解模型 = 控制 模型的前提。

---

## 📌 下一步

02-SAE与Superposition（待写/未落盘）（待补）——2024 突破：解开 neuron 的特征叠加。

## ✍️ 练习

1. Probing 发现 BERT 中层有语法。这能证明"BERT 用语法推理"吗？（提示：不能——有关联不代表有因果。）
2. Attention 权重不是可靠的归因。为什么？（提示：attention 可分散/多头/跨层混合。）
3. SAE 发现单个 neuron 是多特征叠加。这对"一个 neuron 一个概念"的假设意味着什么？（提示：假设错——特征被压进 neuron。）
