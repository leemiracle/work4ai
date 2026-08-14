# CS329Z HW1 Part A - 反思文档

> **CS329Z 的特色**：每次作业后有 10 分钟口试（oral exam），要求学生**反思设计决策**。本文档模拟反思过程。

## 📋 项目目标回顾

构建一个 mini-Agent，能：
1. 通过 RAG 检索知识库回答问题
2. 通过 Tool use 调用计算器 / 搜索
3. 通过 ReAct 循环把"推理"和"行动"交错

## 🎯 设计决策反思

### Q1: 为什么用 litellm 而不是直接用 openai/anthropic SDK？

**决策**：用 `litellm` 作为统一 LLM 接口。

**理由**：
- **统一 API**：一行代码切换 OpenAI/Anthropic/Gemini/DeepSeek/Groq
- **减少 vendor lock-in**：换模型不用改业务代码
- ** fallback 友好**：免费模型（Groq）/付费模型（Claude）切换无成本
- **CS329Z W2 强调**："model selection, cost/latency tradeoffs"——litellm 让 tradeoff 可计算

**代价**：
- 多一层抽象，调试更难（litellm 报错有时不直观）
- 部分高级特性（如 OpenAI 的 structured output）支持滞后

**实际经验**：本项目用 litellm 还提供了 **Mock fallback**——无 API key 时自动回退到 mock，让代码"始终能跑"。这是教学场景的关键设计。

---

### Q2: 为什么 chunking 用固定长度 + overlap，而不是按句子切？

**决策**：用固定 word count（chunk_size=200, overlap=50）。

**理由**：
- **简单**：实现 10 行代码
- **稳定**：不依赖 NLTK / spaCy 分句
- **课程范围**：CS329Z W2 教的就是这个基础方法

**问题**（反思）：
- 固定长度会**切断句子**，破坏语义
- 没有处理 markdown / 代码块 / 表格

**改进方向**（如果有时间）：
1. **Sentence-aware chunking**：用 NLTK 分句后，按句累加直到接近 chunk_size
2. **Recursive chunking**（LangChain 默认）：先按 `\n\n` 切，太大再按 `\n`，再按 `.`，再按 word
3. **Semantic chunking**（2024 新方法）：用 embedding 相似度决定切点

**关键洞察**：CS329Z W2 不会讲高级 chunking，但**真实生产系统 90% 用 recursive chunking**——这是课程和工业界的 gap。

---

### Q3: RAG 检索只用向量相似度够吗？

**决策**：只用 cosine similarity 向量检索。

**问题**（重大）：
- **关键词失效**：搜 "Transformer" 时，如果文档用 "self-attention"，纯向量检索可能错过
- **专有名词**：人名、产品名、代码标识符等很难被 embedding 捕获

**生产系统怎么做**：
- **Hybrid search**：BM25 (关键词) + 向量 (语义)，权重融合
- **Re-ranking**：先用向量召回 top-100，再用 cross-encoder 重排 top-10
- **HyDE**：让 LLM 先生成"假答案"，用假答案做 embedding 检索

**CS329Z 的立场**（讲师 Diyi Yang）：
- W2 教 ColBERT（late interaction）——介于 dense embedding 和 cross-encoder 之间
- 推荐读 ColBERT 论文：https://arxiv.org/abs/2004.12832

**本项目改进计划**：在 Stage 3 添加 BM25 + dense 混合检索。

---

### Q4: ReAct 失败时怎么办？最大步数怎么定？

**决策**：`max_iterations=5`，超过则返回"未得到 final answer"。

**反思**：
- **太大**：成本爆炸（每次迭代都调 LLM）
- **太小**：复杂任务做不完

**经验值**：
- 简单 QA：3 步够
- 多跳推理（multi-hop）：5-8 步
- 复杂 coding task：10-20 步（CS329Z W9 SWE-agent）

**失败模式**（本项目观察）：
1. **LLM 不输出 Final Answer**：陷入无限循环 → 用 max_iterations 兜底
2. **工具调用错误**：返回错误信息，但 LLM 不知道怎么改 → 加 retry 或 fallback
3. **解析失败**：LLM 没遵循 ReAct 格式 → robust parser + retry

**SWE-agent（CS329Z W9）的解法**：
- 设计 **ACI (Agent-Computer Interface)**：让工具的输出格式"诱导"LLM 做正确决策
- 比起 prompt engineering，**interface design** 更稳定

---

### Q5: Mock 模式的局限是什么？

**决策**：无 API key 时用基于规则的 mock 响应。

**优势**：
- 教学场景必备——学生没 key 也能跑通
- 测试基础设施（RAG / Tool / ReAct 主循环）是否正确

**局限**：
- **测不出 prompt 质量好坏**——mock 不知道 LLM 真实响应
- **不能 demo 复杂推理**——mock 规则简单
- **不能验证 ReAct 在失败模式下的鲁棒性**

**真实模式需要的测试**（用户加 API key 后）：
1. 给同样的 query 跑 10 次，看 pass@10
2. 给 adversarial query（错的工具输入）测试恢复
3. 用 LLM-as-judge 评估 final answer 质量

---

### Q6: 这个项目距离 CS329Z A+ 还差什么？

**当前完成度**：~40%

**剩余 60%**：
| 维度 | 当前 | A+ 要求 |
|------|------|---------|
| LLM | mock | 真实 Claude/GPT + 成本统计 |
| RAG | hash embedding | sentence-transformers + hybrid |
| Tools | 3 个简单 | 至少 1 个真实 API（如 Wikipedia API）|
| ReAct | 标准格式 | 至少支持 plan-and-execute 变体 |
| Eval | 无 | 至少 5 个 test cases + 自动评分 |
| 错误处理 | 基础 | retry + fallback + circuit breaker |
| 可观测性 | print | trace JSON + cost tracking |
| 文档 | 此文档 | README + 设计图 + demo video |

---

## 🎯 口试准备（10 分钟 oral exam 模拟）

CS329Z 口试会问的问题（基于课程 W2-W5 内容）：

### 简单题（30 秒答完）
1. **"什么是 Compound AI System？举一个例子。"**
   - 答：多个组件（LLM + retriever + tool）协同的系统。例：我的 mini-Agent = LLM + RAG + Tools + ReAct loop。

2. **"ReAct 的三个核心元素是什么？"**
   - 答：Thought（推理）/ Action（行动）/ Observation（观察）。

3. **"你的 agent 用了哪些工具？为什么选这些？"**
   - 答：calculator（数学必备）/ search（信息检索）/ read_file（本地知识）。

### 中等题（1-2 分钟答完）
4. **"如果你的 agent 在 5 次迭代后还没得到 final answer，你会怎么 debug？"**
   - 答：1) 看 trace 找出在哪一步卡住；2) 检查是否是 LLM 不会用工具（prompt 问题）；3) 检查是否是工具返回错误格式（interface 问题）；4) 增加 max_iterations 或换更强模型。

5. **"你用 hash embedding 而不是 sentence-transformers，会影响什么？"**
   - 答：会严重影响语义检索质量。Hash embedding 只捕获词频，不懂同义词、上下文。比如查 "GPU" 找不到 "graphics card"。**但本项目是教学，重点是流程，不是检索质量**。

6. **"ReAct 和 Chain-of-Thought (CoT) 有什么区别？"**
   - 答：CoT 只在 LLM 脑内推理，不调用外部工具。ReAct 把推理变成行动——可以查资料、算数、调 API。ReAct 更适合需要 ground truth 的任务。

### 难题（3-5 分钟讨论）
7. **"如果让你做 HW1 Part B（DSPy 重写），你觉得 DSPy 会抽象掉什么？什么不会被抽象？"**
   - 答：DSPy 抽象掉的是 prompt 写作——你写 signature，optimizer 自动生成 prompt。**不被抽象的是**：1) 系统结构（什么时候 retrieve / call tool）；2) 工具实现；3) 评估方法。

8. **"Anthropic 的 *Building Effective Agents* 博客说 workflow 和 agent 是不同的。你的 mini-Agent 是 workflow 还是 agent？"**
   - 答：是 agent（按 Anthropic 定义）。Workflow = "LLM + 工具的预定义流程"；Agent = "LLM 自主决定下一步"。我的 ReAct loop 让 LLM 决定何时用工具、何时给 final answer，所以是 agent。

9. **"Cemri 等人 2025 年说多 agent 大多失败。你怎么看？"**
   - 答：我的项目是单 agent。多 agent 失败的常见原因：1) 通信开销 > 单 agent 处理成本；2) 错误传播（一个 agent 错了拖累全局）；3) 评估难。**单 agent + 好工具往往够用**——这是 OpenHands / SWE-agent 的设计哲学。

### 设计题（开放式）
10. **"如果给你一个 Stanford 课程目录的 PDF，让你做一个 agent 回答'哪门课适合我'，你会怎么设计？"**
    - 答：
      1. **预处理**：PDF → text → chunk（recursive）→ embedding → 向量库
      2. **Agent**：ReAct loop + tools = {search_courses, get_prereqs, compare_two}
      3. **个性化**：先问用户兴趣（HCI? ML? 系统?）→ 在 query 里加 personalization context
      4. **Eval**：4-tuple（request / environment / stopping criteria / scorer）
      5. **失败模式**：用户兴趣模糊 / 课程描述太短 / 先修链复杂

---

## 📊 自我评估

| 维度 | 评分（1-5） | 备注 |
|------|------------|------|
| 完成度 | 3 | 基础功能齐全，但缺高级特性 |
| 代码质量 | 4 | 模块化清晰，类型注解完整 |
| 测试覆盖 | 2 | 只有 smoke test，无单元测试 |
| 文档 | 4 | 此反思文档 + 代码内注释 |
| 教学价值 | 5 | 即使没 API key 也能完全跑通 |

**下一步重点**：补 unit test + 加 hybrid search。

---

## 🔗 相关课程材料

- **CS329Z W2**: Building Effective Agents (Anthropic) - https://www.anthropic.com/engineering/building-effective-agents
- **CS329Z W2**: RAG (Lewis 2020) - https://arxiv.org/abs/2005.11401
- **CS329Z W3**: MCP Specification - https://modelcontextprotocol.io/
- **CS329Z W4**: ReAct (Yao 2022) - https://arxiv.org/abs/2210.03629
- **CS329Z W4**: MemGPT - https://arxiv.org/abs/2310.08560
- **CS329Z W9**: SWE-agent - https://arxiv.org/abs/2405.15793
