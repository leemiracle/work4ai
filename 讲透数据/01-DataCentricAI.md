# 01 — Data-Centric AI：数据质量 > 算法

> 「讲透数据」核心章。00 讲了"数据是 AI 三要素里最被忽视的"。本篇讲 Andrew Ng 提倡的 **Data-Centric AI**——与其调模型，不如改数据。这是 2022 后的范式转变。

---

## 1. 灵魂：固定模型，改数据

$$
\boxed{\text{传统：固定数据，调模型} \quad \to \quad \textbf{Data-Centric：固定模型，改数据}}
$$

吴恩达的洞察：大部分实际项目，**改数据的收益 > 调模型**。

---

## 2. 数据质量的四个维度

| 维度 | 含义 | 怎么改 |
|---|---|---|
| **正确性** | 标签对不对 | 人工复核/置信学习 |
| **覆盖性** | 是否覆盖所有场景 | 找 edge case 补数据 |
| **一致性** | 同类样本标签一致 | 统一标注规范 |
| **及时性** | 是否最新 | 增量更新 |

---

## 3. 数据增强（Data Augmentation）

### 3.1 传统增强

- 图像：翻转/旋转/裁剪/颜色抖动
- 文本：同义词替换/回译

### 3.2 Mixup / CutMix

把两个样本线性混合：

$$
x_{\text{new}} = \lambda x_1 + (1-\lambda) x_2, \quad y_{\text{new}} = \lambda y_1 + (1-\lambda) y_2
$$

**创造新样本**，不只是变换——泛化提升显著。

### 3.3 LLM 生成数据

用 GPT-4 生成训练数据（synthetic data）——Alpaca/self-instruct 的核心。但要注意 **Model Collapse**（03 章）——AI 生成的数据训 AI 会导致退化。

---

## 4. 数据清洗工具

- **Confident Learning**（Cleanlab）：用模型置信度找出可能错标的样本
- **Active Learning**：让模型选"最不确定"的样本让人标注——省标注成本
- **Data Valuation**：给每个样本打分（Shapley 值），找出有害/有价值的样本

---

## 5. Scaling Laws 的数据启示

Chinchilla（DeepMind 2022）：最优训练 = 数据量 × 参数量匹配。

$$
\text{计算最优} : \frac{\text{数据量}}{\text{参数量}} \approx 20 \text{ token/参数}
$$

- GPT-3 (175B) 只训了 0.6× 数据 → 欠拟合（Chinchilla 70B 用同样算力 + 4× 数据，反而更好）
- **启示**：与其堆参数，不如喂够数据

---

## 6. 批判性

- **数据质量难量化**：什么是"好数据"仍靠经验
- **数据隐私/版权**：用网络数据训 LLM 有法律风险（NYT vs OpenAI）
- **合成数据的悖论**：AI 生成数据能扩展规模，但 Model Collapse 警告——小心合成污染

> **诚实结论**：Data-Centric AI 是"工程务实主义"——大部分项目的瓶颈是数据不是模型。理解数据质量/增强/清洗，比追新模型架构更实用。

---

## 📌 下一步

[02-数据增强深挖](02-数据增强.md)（待补）/ [03-Model Collapse](03-ModelCollapse.md)（已有）。

## ✍️ 练习

1. Chinchilla 说 20 token/参数最优。GPT-3 (175B) 训了 300B token（1.7 token/参数）。它"数据不够"吗？（提示：是——所以 Llama 用更多数据。）
2. Mixup 把两类样本混合。这为什么能提升泛化？（提示：创造了类间样本，平滑决策边界。）
3. Cleanlab 找出错标样本。如果模型本身有偏，Cleanlab 会找对吗？（提示：有偏模型的置信度有偏——Cleanlab 不万能。）
