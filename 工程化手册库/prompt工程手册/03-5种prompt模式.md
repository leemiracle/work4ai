# 03 · 5 种 prompt 模式：从 Zero-shot 到 Reflexion

> **本文是什么**：5 种主流 prompt 模式的对比、何时用、反模式。
> **目的**：选对模式 = 一半工作。

---

## 🎯 5 种模式速查

| 模式 | 复杂度 | 何时用 | 代表论文 |
|---|---|---|---|
| **Zero-shot** | ⭐ | 简单任务 / 强模型 | GPT-3 2020 |
| **Few-shot** | ⭐⭐ | 需特定格式 / 风格 | GPT-3 2020 |
| **CoT**（Chain of Thought）| ⭐⭐⭐ | 多步推理 / 数学 | Wei 2022 |
| **ReAct**（Reason + Act）| ⭐⭐⭐⭐ | 工具调用 / 检索 | Yao 2022 |
| **Reflexion**（反思）| ⭐⭐⭐⭐⭐ | 长任务 / 可验证 | Shinn 2023 |

加分项：**Self-Consistency**（Wang 2022）—— 跑 N 次取多数。

---

## 1 · Zero-shot

**定义**：不给例子，直接让模型做。

**模板**：
```
You are a [role].
Task: [objective].
Output format: [schema].

Input: {{input}}
Output:
```

**何时用**：
- 简单分类（情感 / 主题）
- 强模型（GPT-5 / Claude Opus 4）
- 通用任务（不需要特定风格）

**反模式**：
- 复杂推理（数学 / 多步）
- 需要特定格式（容易跑偏）
- 弱模型（小模型需要 few-shot）

**例子**：
```
Classify the sentiment of the following review as positive, negative, or neutral.

Review: "{{review}}"
Sentiment:
```

---

## 2 · Few-shot

**定义**：给 N 个 input-output 例子。

**模板**：
```
You are a [role].

Examples:

Input: [example 1 input]
Output: [example 1 output]

Input: [example 2 input]
Output: [example 2 output]

Input: [example 3 input]
Output: [example 3 output]

Now process:
Input: {{real_input}}
Output:
```

**何时用**：
- 需要特定输出格式
- 需要特定写作风格
- 任务有微妙规则（如"忽略 assistant 消息"）

**核心原则**：
- **3-5 个最佳**
- **覆盖边界**（不只"好例"，必须有"空输出"边界）
- **格式严格一致**（所有例子输出 schema 相同）

**反模式**：
- 例子输出格式不一致 → 模型蒙
- 例子都是"成功 case" → 模型不敢返回空（编造）
- 例子太多（>8）→ 过拟合

**例子**（来自 mem0）：
```
Input: Hi.
Output: {"facts": []}

Input: There are branches in trees.
Output: {"facts": []}

Input: Hi, my name is John. I am a software engineer.
Output: {"facts": ["Name is John", "Is a Software engineer"]}
```

注意：前两个是**空边界 case**，第三个是**正常 case**。

---

## 3 · CoT（Chain of Thought）

**定义**：让模型"打草稿"——显式推理再答。

**模板**（手工 CoT）：
```
Let's think step by step.

Question: {{question}}

Reasoning:
1. ...
2. ...
3. ...

Answer:
```

**2024+ 升级版**（推理模型 o1 / R1 / Claude thinking）：
```
Solve this. Output JSON.

Question: {{question}}
```
（模型自己 thinking，不用 prompt 指引）

**何时用**：
- 数学题（GSM8K / MATH）
- 多步推理（逻辑题 / legal case）
- 代码 debug

**反模式**：
- 简单任务（强制 CoT 浪费 token）
- 已经用 o1 / Claude thinking（重复了）

**Self-Consistency 加分**（Wang 2022）：
```
1. 用 CoT 跑 N 次（temperature=0.7）
2. 取 majority vote
```
GSM8K 准确率从 17.7% → 56.9%（GPT-3 时代）。

---

## 4 · ReAct（Reason + Act）

**定义**：Thought → Action → Observation 循环。

**模板**：
```
You have access to these tools:
- search(query): Search the web
- calc(expression): Calculator
- python(code): Run Python

Question: {{question}}

Thought 1: I need to search for X.
Action 1: search("X")
Observation 1: [search result]

Thought 2: Now I need to calculate Y.
Action 2: calc("...")
Observation 2: [result]

Thought 3: I have enough info.
Action 3: Finish("[final answer]")
```

**何时用**：
- 需要工具（搜索 / 计算 / API）
- 多步任务（每个 action 后重新决策）
- 需要可观察的中间步骤

**现代版本**（Function Calling）：
```
# 不再用文本格式，用结构化 tool calling
tools = [
  {"name": "search", "parameters": {...}},
  {"name": "calc", "parameters": {...}}
]
response = model.invoke(messages, tools=tools)
# response.tool_calls = [{"name": "search", "args": {...}}]
```

**反模式**：
- 不提供工具时用 ReAct（模型乱编 Action 结果）
- 任务不需要工具（浪费 step）
- 没设最大 step 数（无限循环）

---

## 5 · Reflexion（反思）

**定义**：失败 → 反思 → 重试。

> **桥**：GEPA 把这个循环自动化到了 prompt 层面——失败（黄金集挂题）→ 反思（reflection LM）→ 重试（重写 prompt）。详见 [`11-自动化优化闭环`](11-自动化优化闭环-六步流水线.md) 的"与 03-Reflexion 的桥"一节。

**模板**：
```
Attempt N:
[trial output]

Evaluation:
[Success: false]
[Failure reason: X is wrong]

Reflection:
The previous attempt failed because X. 
Next time I should Y.

Attempt N+1:
[better output based on reflection]
```

**何时用**：
- 长任务（写代码 / 解数学）
- 可验证（单元测试 / Lean 证明）
- 单次失败成本高

**反模式**：
- 不可验证任务（自欺——模型可能"反思"出错误方向）
- 没设 max iterations（无限反思）
- 反思不基于 ground truth（只是模型自言自语）

---

## 📊 5 模式对比矩阵

| 维度 | Zero-shot | Few-shot | CoT | ReAct | Reflexion |
|---|---|---|---|---|---|
| **复杂度** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **token 消耗** | 低 | 中 | 中 | 高 | 很高 |
| **延迟** | 低 | 低 | 中 | 高 | 很高 |
| **准确性**（简单任务）| 高 | 高 | 中（浪费）| 低（过度工程）| 低 |
| **准确性**（复杂任务）| 低 | 中 | 高 | 高 | 最高 |
| **稳定性** | 中 | 高 | 中 | 中 | 中 |
| **可调试性** | 低 | 中 | 高 | 高 | 最高 |

---

## 🎯 选模式的决策树

```
你的任务是什么？
│
├─ 简单分类 / 通用任务
│  └─→ Zero-shot（先试，不行升级）
│
├─ 需要特定格式 / 风格
│  └─→ Few-shot（3-5 个边界覆盖例子）
│
├─ 多步推理 / 数学
│  ├─ 用 o1 / Claude thinking → 直接 zero-shot（推理模型自带 CoT）
│  └─ 用普通模型 → CoT + Self-Consistency
│
├─ 需要工具（搜索 / 计算 / API）
│  └─→ ReAct / Function Calling
│
└─ 长任务 / 可验证
   └─→ Reflexion
```

---

## 🚀 进阶组合

### CoT + Self-Consistency
```
for i in range(N):
    response = model.invoke(prompt + "Let's think step by step", temperature=0.7)
    answers.append(extract_answer(response))
final = majority_vote(answers)
```

### ReAct + Reflexion
```
for attempt in range(MAX):
    result = react_loop(question)
    if verify(result):
        return result
    reflection = model.invoke(f"Previous: {result}\nFailure: {verify.reason}\nReflect:")
    prompt += reflection  # 反思进 context
```

### Few-shot + CoT
```
Examples:
Input: [Q1]
Thought: [step-by-step reasoning]
Output: [A1]

Input: [Q2]
Thought: [step-by-step reasoning]
Output: [A2]

Now:
Input: {{real_question}}
Thought:
```

---

## 📌 本周必做

1. [ ] 选你最常用的 1 个 prompt，判断它属于哪种模式
2. [ ] 试着换成另一种模式，对比效果（用 Promptfoo 测）
3. [ ] 读 3 篇代表论文（CoT / ReAct / Reflexion）

---

## 📚 推荐论文

- **Wei et al. 2022 "Chain-of-Thought Prompting"**（arXiv 2201.11903）
- **Wang et al. 2022 "Self-Consistency"**（arXiv 2203.11171）
- **Yao et al. 2022 "ReAct"**（arXiv 2210.03629）
- **Yao et al. 2023 "Tree of Thoughts"**（arXiv 2305.10601）
- **Shinn et al. 2023 "Reflexion"**（arXiv 2303.11366）
- **Schick et al. 2023 "Toolformer"**（arXiv 2302.04761）

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**5 模式 = 5 个工具。简单任务用 Zero-shot，复杂任务用 Reflexion。选错模式 = 50% 浪费。**
