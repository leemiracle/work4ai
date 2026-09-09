# Prompt Engineering 深度精读：从 Few-shot 到 ReAct

> 参照：Wei 2022 (CoT) / Yao 2023 (ReAct) / OpenAI Cookbook
>
> csdiy 对应：tinyrag + tinyllm + softmax-temperature + AI核心

---

## 一、为什么 Prompt 重要

```
同样的模型（GPT-4），不同的 prompt：

Prompt A: "什么是递归？"
→ 回答: 一段教科书式定义

Prompt B: "用一个小学生能听懂的故事解释递归，然后给一个 Python 例子"
→ 回答: 故事 + 代码 + 类比

→ Prompt 决定了模型输出的质量和格式
```

---

## 二、Prompt 技术演化

```
Zero-shot → Few-shot → Chain-of-Thought → Self-Consistency
→ Tree-of-Thought → ReAct → Plan-and-Solve
```

---

## 三、Zero-shot

```
直接问，不给例子：

"把以下句子翻译成英文：今天天气很好"
→ "The weather is nice today."
```

适合：简单任务（翻译/分类/总结）。

---

## 四、Few-shot

```
给几个例子，让模型学习模式：

"英文到中文翻译：
Good morning → 早上好
Thank you → 谢谢
How are you → 你好吗

翻译以下：
I love you →"
→ "我爱你"
```

### 关键技巧

```
1. 例子要"多样"（覆盖不同模式）
2. 例子顺序影响结果（recency bias）
3. 3-5 个例子通常足够（更多收益递减）
4. 例子要和目标任务格式一致
```

---

## 五、Chain-of-Thought (CoT)

### 核心：让模型"想出来"

```
不用 CoT:
  Q: 一个商店有 23 个苹果，卖了 17 个，又进了 8 个，现在有多少？
  A: 14                    ← 可能直接猜答案，容易错

用 CoT:
  Q: 一个商店有 23 个苹果，卖了 17 个，又进了 8 个，现在有多少？
  A: 让我一步步算。开始有 23 个。卖了 17 个：23-17=6。
     又进了 8 个：6+8=14。答案是 14。   ← 推理过程 → 正确
```

### Zero-shot CoT

```
在 prompt 后加一句话：
"Let's think step by step."

→ 模型自动生成推理链 → 正确率提升 10-20%
```

### 效果

```
数学推理（GSM8K）:
  标准提问: 17% → CoT 提问: 56%（GPT-3）
  标准提问: 56% → CoT 提问: 85%（GPT-4）
```

---

## 六、Self-Consistency

### CoT 的问题

CoT 每次生成的推理链不同 → 有时对有时错。

### 解法：多次采样 + 投票

```
1. 用温度 T=0.7 生成 K 条 CoT 推理链
2. 每条得到一个答案
3. 选最频繁的答案（多数投票）

Q: "数学题..."
→ Chain 1: ...答案是 42
→ Chain 2: ...答案是 42
→ Chain 3: ...答案是 38
→ Chain 4: ...答案是 42
→ Chain 5: ...答案是 42

最终答案: 42（4/5 一致）
```

### 效果

```
GSM8K: CoT 56% → Self-Consistency 74%（+18%）
代价: 生成 K 倍 token → 推理慢 K 倍
```

---

## 七、Tree of Thoughts (ToT)

### 问题：CoT 是线性的（一条路走到底）

ToT = 探索多条推理路径 + 回溯。

```
         开始
        /    \
    策略A    策略B
    /  \      |
  A1   A2    B1 ← 评估: B1 最好
  |         /  \
  ...     B1a  B1b
           |
         答案
```

### 流程

```
1. 生成 K 个候选思路
2. 评估每个思路的前景（用 LLM 打分）
3. 选最优的继续展开（BFS/DFS）
4. 如果走到死路 → 回溯
```

### 适用

复杂推理（24 点游戏/创意写作/填字游戏）。

---

## 八、ReAct（Reasoning + Acting）

### 核心：推理 + 工具调用交替

```
Thought: 我需要查找当前天气
Action: search_weather("北京")
Observation: 北京今天 25°C，晴天
Thought: 25°C 是舒适温度
Action: respond("北京今天 25°C，适合外出")
```

### 架构

```
循环:
  ① Thought（推理）: LLM 思考下一步该做什么
  ② Action（行动）: 调用工具（搜索/计算/API）
  ③ Observation（观察）: 获取工具返回的结果
  → 回到 ①

直到 LLM 认为可以回答
```

### 工具定义

```python
tools = {
    "search": lambda q: web_search(q),
    "calculator": lambda expr: eval(expr),
    "code_interpreter": lambda code: run_python(code),
    "rag": lambda q: rag_pipeline.retrieve(q),
}

prompt = f"""
Use the following tools to answer: {tools}

Question: {user_question}

Thought + Action + Observation loop...
"""
```

---

## 九、各技术对比

| 技术 | 原理 | 加速/减速 | 适用 |
|------|------|---------|------|
| Zero-shot | 直接问 | 1× | 简单任务 |
| Few-shot | 给例子 | 1× | 格式化任务 |
| CoT | 逐步推理 | 3-5× 慢 | 数学/逻辑 |
| Self-Consistency | 多次采样+投票 | 5-10× 慢 | 高精度推理 |
| ToT | 树搜索+回溯 | 10-50× 慢 | 创意/规划 |
| ReAct | 推理+工具 | 取决于工具 | 需要外部信息 |

---

## 十、工程实践

### System Prompt 模板

```
You are a helpful assistant. Follow these rules:
1. Think step by step
2. If you don't know, say "I don't know"
3. Use the provided tools when needed
4. Always cite your sources

Available tools: {tools}

Context from RAG: {retrieved_context}
```

### 温度选择

```
数学/代码: T=0.1（确定）
推理 CoT: T=0.3-0.5（稍微随机，配合 self-consistency）
创意写作: T=0.7-0.9（鼓励多样性）
Self-Consistency: T=0.5-0.7 + K=5-10 次采样
```

---

## 十一、一句话总结

> CoT = "Let's think step by step" → +20% 准确率。
>
> ReAct = Thought + Action + Observation → LLM 智能体的基础。
>
> Self-Consistency = 多次采样 + 投票 → 最简单的高精度技巧。
>
> **Prompt Engineering 是 LLM 时代的"编程语言"——你用自然语言"编程"模型行为。**

---

*配套：[tinyrag/pipeline.py](../projects/tinyrag/pipeline.py) | [tinyllm/infer.py](../projects/tinyllm/infer.py) | [softmax-temperature精读](softmax-temperature-精读.md)*
