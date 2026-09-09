# LLM 评估精读：从 Perplexity 到 Arena

> 参照：HELM / OpenAI evals / LMSYS Arena / MMLU
>
> csdiy 对应：nanoGPT精读(train.py) + tinyllm + softmax-temperature

---

## 一、为什么评估 LLM 很难

```
传统 ML: accuracy / F1 / MSE → 明确的数值指标
LLM: 生成文本 → "好" 是主观的 → 没有唯一正确答案

挑战：
  1. 开放式生成没有标准答案
  2. 人类偏好因人而异
  3. 模型可能"看起来对"但实际错了（幻觉）
  4. 基准测试可以被"刷榜"（数据泄露）
```

---

## 二、内部指标（训练时用）

### Perplexity（困惑度）

```
PPL = exp(-1/N × Σ log P(token_i | context))

直觉：模型对测试文本"有多惊讶"
  PPL=1: 完美预测（每个 token 概率=1）
  PPL=∞: 完全随机
  GPT-4 在英文: ~3-5
  LLaMA-7B 在英文: ~5-10
```

**用途**：比较模型在相同数据上的语言建模能力。

**局限**：PPL 低 ≠ 回答问题好（只是"更像人话"）。

### Loss Curve

```
训练 loss 持续下降 → 模型在学习
验证 loss 上升 → 过拟合
→ 和 PPL 直接相关（PPL = exp(loss)）
```

---

## 三、知识/推理基准

### MMLU（Massive Multitask Language Understanding）

```
57 个学科 × ~14K 多选题
  数学/历史/法律/医学/编程/...

格式：单选题（A/B/C/D）
评分：accuracy（0-100%）

结果（2024）：
  GPT-4:          86%
  Claude-3 Opus:  87%
  LLaMA-3 70B:    82%
  LLaMA-3 8B:     66%
```

### GSM8K（小学数学）

```
8,500 道小学数学应用题
  "Janet 的鸭子每天下 16 个蛋..."

评分：accuracy
CoT（思维链）prompting 在这里效果显著

结果：
  GPT-4:     92%
  LLaMA-3 70B: 85%
```

### HumanEval（代码生成）

```
164 道 Python 编程题
  给函数签名 + docstring → 生成代码

评分：pass@k（生成的 k 个方案中至少 1 个通过测试）

结果：
  GPT-4:        pass@1 = 85%
  Claude-3.5:   pass@1 = 92%
  LLaMA-3 70B:  pass@1 = 70%
```

### 其他重要基准

| 基准 | 类型 | 题量 | 代表 |
|------|------|------|------|
| MMLU | 知识 | 14K | 综合 |
| GSM8K | 数学推理 | 8.5K | 数学 |
| HumanEval | 代码 | 164 | 编程 |
| BBH | 推理 | 6.5K | Big-Bench Hard |
| TruthfulQA | 幻觉 | 817 | 真实性 |
| MT-Bench | 多轮对话 | 80 | 对话质量 |
| AlpacaEval | 指令遵循 | 805 | 与 GPT-4 对比 |
| AGIEval | 标准化考试 | | SAT/GRE/高考 |

---

## 四、人类偏好评估

### Elo Rating（LMSYS Chatbot Arena）

```
用户同时问两个匿名模型同一个问题
→ 选择更好的回答（或平局）
→ 用 Elo Rating 计算排名

模型      Elo    胜率
GPT-4o    1287   75%
Claude-3.5 1278  73%
Gemini-1.5 1261  68%
LLaMA-3-70B 1208  55%

→ 最接近真实用户体验的评估方式
```

### MT-Bench（多轮对话）

```
80 道多轮对话题 → GPT-4 当裁判打分（1-10）

Round 1: "解释量子纠缠"
Round 2: "给我一个生活中的类比"

GPT-4 裁判评分:
  模型A回答: 8/10
  模型B回答: 6/10
```

---

## 五、LLM-as-a-Judge（LLM 当裁判）

### 原理

用 GPT-4 或 Claude 当裁判，评估其他模型的输出。

```python
judge_prompt = f"""
Rate the following response on a scale of 1-10.

Question: {question}
Response: {response}

Criteria: helpfulness, accuracy, clarity, completeness

Output: {{"score": 8, "reasoning": "..."}}
"""
```

### 问题

```
1. 位置偏好: LLM 裁判偏好第一个/最后一个回答
2. 长度偏好: LLM 裁判偏好更长的回答
3. 自我偏好: GPT-4 当裁判时偏好 GPT 的回答
4. 能力上限: 裁判模型不如被评模型时 → 评不准
```

### Pairwise Comparison（成对比较）

```
不用绝对分数，而是 A vs B 哪个更好：

A better: 60%
B better: 25%
Tie:      15%

→ Bradley-Terry 模型转换为 Elo Rating
```

---

## 六、RAG 评估

### RAGAS（RAG Assessment）

```
3 个维度：
  ① Faithfulness（忠实度）: 回答是否基于检索的文档（无幻觉）
  ② Answer Relevancy（答案相关性）: 回答是否切题
  ③ Context Precision（检索精度）: 检索的文档是否相关
  ④ Context Recall（检索召回）: 是否检索到了所有相关文档
```

### 你的 tinyrag 的评估

```python
# pipeline.py 的 evaluate_retrieval
def evaluate_retrieval(self, queries_with_expected, top_k=5):
    """Recall@K: 正确文档是否出现在 top-K 检索结果中"""
    hits = 0
    for query, expected_doc_id in queries_with_expected:
        results = self.retrieve(query, top_k=top_k)
        doc_ids = {r["metadata"]["doc_id"] for r in results}
        if expected_doc_id in doc_ids: hits += 1
    return {"recall@k": hits / total}
```

---

## 七、评估的陷阱

### 数据泄露

```
模型在训练时见过 MMLU 的题目 → 分数虚高
→ 解法：用未公开的新题 / 动态生成题目

GPT-4 的 MMLU=86% 可能有 5-10% 的数据泄露效应
```

### Goodhart's Law

```
"当指标变成目标时，它就不再是好指标"

→ 模型优化 MMLU 分数 → 实际能力可能没提升
→ 解法：用多个维度 + 人类评估
```

### 快速过时

```
2023: MMLU 领先 = 好
2024: LLaMA-3 在 MMLU 上接近 GPT-4 → MMLU 不再区分性
→ 需要更难的基准（GPQA / ARC-AGI）
```

---

## 八、完整评估框架

```
生产级 LLM 评估应该包含：

① 基础能力: MMLU + GSM8K + HumanEval
② 对话质量: MT-Bench + AlpacaEval
③ 人类偏好: Chatbot Arena Elo
④ 安全性: TruthfulQA + ToxiGen
⑤ 特定任务: 自定义评估集（如你的业务场景）
⑥ RAG 评估: RAGAS（如果用 RAG）
```

---

## 九、一句话总结

> 评估 LLM = 内部指标（PPL）+ 知识基准（MMLU）+ 人类偏好（Arena Elo）+ 任务特定。
>
> Arena Elo 是最接近真实体验的指标。LLM-as-Judge 是最实用的自动评估。
>
> **没有"最好的"指标 → 多维度组合 + 定期更新基准才是正确做法。**

---

*配套：[nanoGPT精读](nanoGPT-读懂最小GPT.md) | [tinyllm/infer.py](../projects/tinyllm/infer.py) | [tinyrag/pipeline.py](../projects/tinyrag/pipeline.py)*
