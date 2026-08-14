# 语言学 · LLM 句法 circuit 探测

> **博士级**：怎么用 mechanistic interpretability 找 LLM 的语法结构。

## 一、问题

LLM 学到真句法吗？还是只是统计模式？

**两种立场**：
- **Hinton / Manning**：LLM 内部有真句法结构
- **Chomsky**：LLM 只是模式匹配，没有真语法

## 二、方法：结构探针（Structural Probe）

### 2.1 Hewitt & Manning 2019

**核心**：BERT 的中间层表示**编码句法树**。

### 2.2 数学

给定 BERT 嵌入 $h_i$，定义距离：

$$d_\theta(h_i, h_j) = (h_i - h_j)^T M_\theta (h_i - h_j)$$

如果 $d_\theta$ 与真实句法树距离相关，则 BERT 学到了句法。

**结果**：BERT 中间层的 $d_\theta$ 与 Penn Treebank 句法树**高度相关**。

## 三、Anthropic 的 Circuit 工作（2023-2024）

### 3.1 找 induction heads

**Anthropic circuits thread**：找到 LLM 的"功能回路"。

**induction heads**（2022）：
- 负责 **in-context learning**
- 两层 attention 协作
- 复制 → 匹配 → 续写

### 3.2 句法 circuit

- 哪些 head 处理主谓一致？
- 哪些处理依附？
- **Sparse Autoencoder**（SAE）找特征

详见 [`讲透可解释性`](../../../讲透可解释性/)。

## 四、关键证据

### 4.1 BERT 的层次句法

- **底层**：词性 / 词法
- **中层**：短语 / 句法
- **顶层**：语义 / 任务

### 4.2 跨语言共性

- 多语言 BERT 内部有**普遍句法表示**
- 支持**普遍语法**（Chomsky 概念）

### 4.3 副作用：LLM 的句法"幻觉"

- LLM 有时违反自己学到的句法
- **circuit 失效**案例

## 五、Chomsky vs Hinton

### 5.1 Chomsky 2023 NYT

- LLM 不"理解"语言
- 没有普遍语法（UG）
- 只是统计

### 5.2 Piantadosi 2023 反驳

- LLM 的成功**反驳** Chomsky
- 普遍语法不必要——大数据 + 统计够
- 行为 = 理解

### 5.3 当前的"混合"结论

- LLM 部分学到句法结构
- 但**不完全**（边界 case 失败）
- **Chomsky vs Hinton**：部分都对

## 六、博士级练习

1. 实现结构探针（PyTorch + BERT）
2. 用 SAE 找句法特征
3. 测试 LLM 在**长距离依赖**的表现

## 关键引用

- Hewitt & Manning 2019 *ACL*
- Manning 2020 *PNAS*
- Olsson 2022 induction heads（Anthropic）
- Piantadosi 2023
