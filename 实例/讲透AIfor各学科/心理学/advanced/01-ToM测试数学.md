# 心理学 · ToM（心智理论）测试数学

> **博士级**：心智理论的计算模型 + 怎么测 LLM。

## 一、什么是 ToM

**心智理论**（Theory of Mind）：理解他人有不同信念 / 意图 / 知识。

### 1.1 经典测试：False Belief Task

**Sally-Anne 测试**：
1. Sally 放球在篮子 A
2. Sally 离开
3. Anne 把球移到篮子 B
4. Sally 回来——她会去哪找？

**正确答案**：篮子 A（Sally 的**假信念**）。

**儿童**：4 岁前答错（B），4 岁后答对（A）。

**自闭症**：ToM 受损。

## 二、ToM 的计算模型

### 2.1 Bayesian ToM（Baker 等）

**目标**：推断他人意图 / 信念。

$$P(\text{goal} | \text{action}) \propto P(\text{action} | \text{goal}) P(\text{goal})$$

**递归**：我认为你认为他认为...

### 2.2 计划模型

agent 行为 = 计划 + 执行：

$$a_t = \pi^*(s_t, b_t)$$

其中 $b_t$ 是 agent 的信念状态（可能错误）。

## 三、LLM 的 ToM 测试

### 3.1 ToM Benchmark

**Strachan 2024**（*Nature Hum Behav*）：
- 多种 ToM 任务
- GPT-4 ~ 接近人类
- Llama 3 等：略低

### 3.2 False Belief 测试

LLM 在经典 Sally-Anne 上几乎全对——**真的理解还是模式匹配**？

### 3.3 进阶测试

- **二次序 ToM**（"他认为她认为"）
- **情绪推理**
- **意图理解**

## 四、关键争议

### 4.1 真理解 vs 模式匹配

**Ullman 2023**：LLM 在简单变化后失败——只是模式匹配。

**Strachan 2024**：在更难 ToM 任务上接近人类。

**结论**：部分真，部分假。

### 4.2 涌现 vs 训练

**Kosinski 2023**：ToM 在 GPT-3.5 涌现。
**后续**：可能训练数据包含类似题。

## 五、ToM 的认知建模

### 5.1 用 LLM 作为人类 ToM 模型

- 比较 LLM 内部 vs 人脑 fMRI
- 找"心理 circuit"（[`讲透可解释性`](../../../讲透可解释性/)）

### 5.2 自闭症研究

- LLM 在 ToM 任务失败 = 类似自闭症？
- **诊断 / 治疗** 启发

## 六、应用

### 6.1 AI 助手

- 理解用户意图
- 推测情绪
- **Claude / GPT** 部分实现

### 6.2 谈判 + 博弈

- 推测对手
- AI 在扑克 / 外交上（Meta CICERO）

### 6.3 教育

- 自适应：学生知道什么？
- **诊断误解**

## 七、博士级练习

1. 实现 Bayesian ToM（Pyro / PyMC）
2. 在 ToMi benchmark 测 GPT-4
3. 设计新 ToM 测试（避免训练污染）

## 关键引用

- Premack & Woodruff 1978（ToM 概念）
- Baker 2009 *Cognition*（Bayesian ToM）
- Strachan 2024 *Nature Hum Behav*
- Ullman 2023
