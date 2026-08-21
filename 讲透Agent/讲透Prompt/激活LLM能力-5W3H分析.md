# 激活大语言模型能力的所有手段 · 5W3H 分析

> **问题**：同一个 LLM，为什么有时候答得好、有时候答得烂？答案在于**激活手段**——LLM 的能力是**潜在的**，需要正确的 prompt/decoding/外部刺激才能"激活"出来。
>
> 本文档用 **5W3H 框架** 系统梳理**所有已知激活手段**，告诉你每个手段 What / Why / Where / When / Who / How / How much / How many。

---

## 一、5W3H 框架

> 外部对照：本总纲 22 手段可与 The Prompt Report（arXiv:2406.06608）的 58 技术六族分类互查（22↔58 映射表见 [`Prompt综述精华-四篇地图.md`](Prompt综述精华-四篇地图.md) §四）——本总纲按**激活力度**排序（工程视角），Report 按**本体论**分类（学术视角）。

| 维度 | 问什么 | 在本文的对应 |
|---|---|---|
| **What** | 是什么 | 一句话定义 |
| **Why** | 为什么有效 | 原理（机制/论文证据）|
| **Where** | 在哪用 | 适用场景 |
| **When** | 何时用 | 时机/前置条件 |
| **Who** | 谁提出/谁该用 | 提出者 + 目标用户 |
| **How** | 怎么用 | 具体 prompt 模板 |
| **How much** | 效果多大 | 实证增益（论文数据）|
| **How many** | 成本多少 | token / 调用次数 / 延迟 |

---

## 二、22 个核心激活手段（按激活力度排序）

### 🧠 A. 思维链家族（最强激活，必学）

#### 1. Zero-shot CoT

| 维度 | 内容 |
|---|---|
| **What** | 在 prompt 末尾加一句"Let's think step by step" |
| **Why** | LLM 单步直出答案 = 跳过中间推理；显式要求分步 = 强制展开计算图。**机制**：自回归生成时，中间 token 成为后续推理的上下文 |
| **Where** | 数学题、逻辑题、多步推理、任何"答案依赖中间步骤"的任务 |
| **When** | 模型规模够大（>10B，涌现点之后）；小模型不奏效 |
| **Who** | Kojima et al. 2022（NeurIPS）|
| **How** | `prompt = "问题\n\nLet's think step by step."` |
| **How much** | GSM8K：18% → 57%（GPT-3）；MultiArith：18% → 81% |
| **How many** | +几十 token；延迟 ~2-3x |

#### 2. Few-shot CoT

| 维度 | 内容 |
|---|---|
| **What** | 给 2-8 个**带推理过程**的示例（不只是答案）|
| **Why** | 示例教会模型"怎么推理"，不只是"答什么"。比 zero-shot CoT 更稳 |
| **Where** | 任务格式固定、能找到示例的场景 |
| **When** | zero-shot CoT 不稳定时；任务需要特定推理范式 |
| **Who** | Wei et al. 2022（NeurIPS，Google）|
| **How** | `示例1: 问题... 推理... 答案: X\n示例2: ...\n实际问题: ... 推理: ... 答案:` |
| **How much** | GSM8K：57% → 74%（GPT-3）；超过 zero-shot CoT 约 17pp |
| **How many** | +数百 token（每个示例 ~100 token）|

#### 3. Self-Consistency

| 维度 | 内容 |
|---|---|
| **What** | 同一 CoT prompt 采样 N 次（temperature>0），取**多数票答案** |
| **Why** | 单次推理有随机性错误；多条推理路径趋同 = 高置信。**机制**：用多样性对冲单点错误 |
| **Where** | 答案可枚举（数学/分类/选择）；不适用开放式生成 |
| **When** | CoT 已用，想再压错误率 |
| **Who** | Wang et al. 2022（ICLR）|
| **How** | `for i in range(N): answer_i = LLM(prompt, temp=0.7); final = mode(answers)` |
| **How much** | GSM8K：74% → 88%（GPT-3，N=40）；GSM8K：17% → 56%（PaLM-8B）|
| **How many** | N 次调用（典型 N=10-40）；成本 N×；延迟 N×（可并行降到 1×）|

#### 4. Universal Self-Consistency

| 维度 | 内容 |
|---|---|
| **What** | Self-consistency 的扩展：用 LLM 自己**判断**哪个答案最对（不只多数票）|
| **Why** | 开放式生成无标准答案可比，多数票失效；用 LLM 评估 LLM 答案 |
| **Where** | 开放式生成（写作/摘要/代码）|
| **When** | 答案不可枚举 |
| **Who** | Chen et al. 2023 |
| **How** | 采样 N 个回答 → 让 LLM 评分选最佳 |
| **How much** | 开放任务 +5-15% |
| **How many** | N× 生成 + 1× 评估 |

---

### 🌳 B. 思维结构（处理复杂搜索空间）

#### 5. Tree-of-Thoughts (ToT)

| 维度 | 内容 |
|---|---|
| **What** | 把推理建成**树**：每步生成 K 个候选 → 评估剪枝 → BFS/DFS 搜索 |
| **Why** | CoT 是单线；ToT 允许回溯、比较、剪枝。**机制**：显式搜索 + LLM 当评估器 |
| **Where** | 需要试错的复杂任务（24点游戏、创意写作、Crossword）|
| **When** | 单线 CoT 失败；问题有明确评估函数 |
| **Who** | Yao et al. 2023（NeurIPS）|
| **How** | `定义 thought 生成器 + state 评估器 + 搜索算法（BFS/DFS）` |
| **How much** | 24 点游戏：4%（CoT）→ 74%（ToT）；Creative Writing： coh.-7.56 → 7.56 |
| **How many** | 每节点 K× 调用，深度 D → K^D 次；成本高（10-100×）|

#### 6. Graph-of-Thoughts (GoT)

| 维度 | 内容 |
|---|---|
| **What** | ToT 的泛化：思维是**图**（可合并、可分支、可循环）|
| **Why** | 有些推理需要**合并**多个分支（如多视角综合）|
| **Where** | 需要聚合多视角/多路径的任务 |
| **When** | ToT 的树结构不够 |
| **Who** | Besta et al. 2023 |
| **How** | 定义图操作：聚合/分支/回溯/循环 |
| **How much** | 比 ToT 在排序/合并任务上再 +5-10% |
| **How many** | 比 ToT 更多调用 |

#### 7. Least-to-Most Decomposition

| 维度 | 内容 |
|---|---|
| **What** | 把复杂问题**分解为子问题**：从最简单的开始，逐步用前面的答案 |
| **Why** | LLM 单步推理能力有限；分解后每步变简单 |
| **Where** | 多步数学题、组合泛化任务 |
| **When** | 问题明显可分解 |
| **Who** | Zhou et al. 2022（Google）|
| **How** | `1. 让 LLM 把问题分解为子问题\n2. 依次解每个子问题，前面答案传入后面` |
| **How much** | SCAN 数据集：16% → 76%（GPT-3）|
| **How many** | 子问题数次调用 |

#### 8. Plan-and-Solve

| 维度 | 内容 |
|---|---|
| **What** | "先制定计划，再执行计划"——zero-shot CoT 的增强版 |
| **Why** | 单纯"step by step"可能乱；显式计划让推理有序 |
| **Where** | 多步任务（zero-shot CoT 失效时）|
| **When** | 推理步骤之间有依赖 |
| **Who** | Wang et al. 2023 |
| **How** | `prompt = "先制定计划再解。Let's first understand the problem, devise a plan, then carry out the plan."` |
| **How much** | GSM8K：57%（CoT）→ 78%（Plan-Solve）|
| **How many** | +几十 token；延迟 ~1.5× |

---

### 🪞 C. 反思与自改

#### 9. Reflexion

| 维度 | 内容 |
|---|---|
| **What** | 答完一题后让 LLM **反思**自己的错误，下次用反思改进 |
| **Why** | LLM 能识别自己的错误（即便初次犯错）；反思文本作为 memory |
| **Where** | 编程（HumanEval）、决策（HotpotQA）、推理 |
| **When** | 有反馈信号（编译器/答案核对/环境）|
| **Who** | Shinn et al. 2023（NeurIPS）|
| **How** | `1. 答\n2. 反馈（编译/对照）\n3. 让 LLM 反思"为什么错"\n4. 重答，带反思 memory` |
| **How much** | HumanEval：80% → 91%；HotpotQA：协作多 30pp |
| **How many** | 迭代 2-4 次；成本 2-4× |

#### 10. Self-Refine

| 维度 | 内容 |
|---|---|
| **What** | LLM 自己**生成反馈** + 自己改进（不需要外部信号）|
| **Why** | Reflexion 需要外部反馈；Self-Refine 内循环 |
| **Where** | 写作、代码、对话生成 |
| **When** | 无外部反馈源 |
| **Who** | Madaan et al. 2023（NeurIPS）|
| **How** | `1. 答\n2. 让 LLM 评自己答案（找问题）\n3. 让 LLM 改进\n重复 2-3` |
| **How much** | 任务平均 +20%（对话/代码）|
| **How many** | 2-3 次迭代 |

#### 11. Self-Critique（自我反驳）

| 维度 | 内容 |
|---|---|
| **What** | "先答，然后扮演批评者攻击自己答案" |
| **Why** | 强制考虑反方；避开单边论证 |
| **Where** | 论证、分析、决策 |
| **When** | 任何有立场的回答 |
| **Who** | 多篇工作 |
| **How** | `prompt = "答完后，扮演 devil's advocate，给出 3 个最强反驳，然后修正答案"` |
| **How much** | 主观题 +10-15% |
| **How many** | 1 次调用（多角色 prompt）|

---

### ⚡ D. 推理 + 行动

#### 12. ReAct

| 维度 | 内容 |
|---|---|
| **What** | **Re**ason + **Act** 交替：推理一步 → 调工具 → 看结果 → 再推理 |
| **Why** | 纯推理会幻觉；调工具（搜索/计算器）补外部事实 |
| **Where** | 需要外部信息/计算的任务 |
| **When** | LLM 有工具访问权 |
| **Who** | Yao et al. 2022（ICLR）|
| **How** | `Thought: ...\nAction: search("...")\nObservation: ...\nThought: ...\nFinal Answer: ...` |
| **How much** | HotpotQA：28%（CoT）→ 34%（ReAct）；Fever：58% → 64% |
| **How many** | 每个工具调用一次 LLM；总调用 = 思考步数 |

#### 13. Tool Use / Function Calling

| 维度 | 内容 |
|---|---|
| **What** | LLM 显式调用外部函数（计算器、搜索、API）|
| **Why** | LLM 算术/实时信息弱；外包给专用工具 |
| **Where** | 数学、实时信息、代码执行 |
| **When** | 任务有明确工具 |
| **Who** | Toolformer（Schick 2023）；OpenAI Function Calling |
| **How** | `tools = [...]; LLM 自动生成 tool_call；执行；结果返回 LLM` |
| **How much** | 数学题 +30-50%（用计算器）；实时信息无限提升 |
| **How many** | 1-3 次工具调用 |

---

### 🎭 E. Persona / 角色

#### 14. Expert Persona

| 维度 | 内容 |
|---|---|
| **What** | "You are an expert in X" 框定身份 |
| **Why** | 调整输出分布到"专家"区域；触发领域知识 |
| **Where** | 任何专业领域任务 |
| **When** | 想要专业语气/深度 |
| **Who** | 通用实践 |
| **How** | `system = "You are a senior ML researcher with 20 years experience..."` |
| **How much** | 主观 +5-10%；客观题效果不显著 |
| **How many** | +几十 token |

#### 15. Multi-Agent Debate

| 维度 | 内容 |
|---|---|
| **What** | 多个 LLM 实例扮演不同角色**辩论**，最后综合 |
| **Why** | 多视角 > 单视角；辩论暴露盲区 |
| **Where** | 复杂推理、政策分析、代码审查 |
| **When** | 单 LLM 答案不确定 |
| **Who** | Du et al. 2023；Chan et al. 2023 |
| **How** | `Agent A 提案 → Agent B 反驳 → Agent A 改进 → ... → 综合` |
| **How much** | GSM8K：+5-10%；辩论 3-5 轮饱和 |
| **How many** | N agents × R rounds = N×R 调用 |

---

### 💖 F. 情绪 / 心理触发（争议但有效）

#### 16. Emotional Prompting

| 维度 | 内容 |
|---|---|
| **What** | "This is very important to my career" / "I'll tip you $200" |
| **Why** | **机制不明**——可能触发 LLM 训练数据里"重要任务"的高质量回答模式 |
| **Where** | 通用任务 |
| **When** | 想榨取最后 1-2% |
| **Who** | Google 2023 论文（"Large Language Models Understand and Can Be Enhanced by Emotional Stimuli"）|
| **How** | `prompt += "This is very important to my career."` |
| **How much** | +0-10%（不稳定，依赖任务/模型）|
| **How many** | +10 token；零额外调用 |

#### 17. "Take a Deep Breath"

| 维度 | 内容 |
|---|---|
| **What** | "Take a deep breath and work through this step by step" |
| **Why** | 类似 CoT 但更"安抚"，可能降低焦虑相关错误模式 |
| **Where** | 数学题 |
| **When** | CoT 已用 |
| **Who** | Google 2023 |
| **How** | `prompt = "Take a deep breath and work through this step by step.\n\n" + 问题` |
| **How much** | GSM8K：+8%（PaLM 2）|
| **How many** | +10 token |

---

### 📋 G. 格式 / 约束

#### 18. Verify-then-Answer

| 维度 | 内容 |
|---|---|
| **What** | "先验证你的答案，再给最终答案" |
| **Why** | LLM 能识别自己的简单错误；显式验证触发检查 |
| **Where** | 数学、事实问答 |
| **When** | 单次答错率高 |
| **Who** | 通用实践 |
| **How** | `prompt = "答完后用 unit test 验证，最后给 final answer"` |
| **How much** | +5-15%（数学）|
| **How many** | +1 次验证步骤 |

#### 19. Constrained Decoding

| 维度 | 内容 |
|---|---|
| **What** | 在 decoding 层面约束输出（grammar/JSON schema/正则）|
| **Why** | 保证输出格式合法；不浪费 token 在无效生成 |
| **Where** | 结构化输出（JSON/SQL/代码）|
| **When** | 需要 100% 格式保证 |
| **Who** | Guidance / Outlines / JSON mode |
| **How** | `grammar = ...; generator(prompt, grammar=grammar)` |
| **How much** | 格式正确率 50% → 100%；内容质量持平 |
| **How many** | 0 额外调用（decoding 时拦截）|

---

### 🔍 H. 外部增强

#### 20. RAG (Retrieval-Augmented Generation)

| 维度 | 内容 |
|---|---|
| **What** | 检索相关文档 → 塞进 prompt → LLM 据此答 |
| **Why** | 补长尾知识；避免幻觉；无需微调 |
| **Where** | 知识密集任务（QA、文档总结）|
| **When** | 任务需要外部/最新知识 |
| **Who** | Lewis et al. 2020（NeurIPS）|
| **How** | `1. 问题 → embedding → 检索 top-k 文档\n2. prompt = "context: {docs}\nquestion: {q}"` |
| **How much** | QA：+20-40%（取决于检索质量）|
| **How many** | +检索调用（向量库）|

#### 21. Constitutional AI / Self-Critique Loop

| 维度 | 内容 |
|---|---|
| **What** | 让 LLM 用一组**原则**自我约束（安全/有用/诚实）|
| **Why** | 减少有害输出；对齐价值观 |
| **Where** | 对话系统、安全场景 |
| **When** | 需要 RLHF 替代 |
| **Who** | Anthropic 2022 |
| **How** | `principles = [...]; LLM 答完后用 principles 自评自改` |
| **How much** | 有害输出 -50% |
| **How many** | +1 次评估/改写 |

#### 22. DSPy / 自动 Prompt 优化

| 维度 | 内容 |
|---|---|
| **What** | 不手写 prompt，用**优化器**（MIPRO/GEPA）自动找最佳 prompt + few-shot |
| **Why** | 手工 prompt 工程难复现、难优化；自动搜索能找到人想不到的组合 |
| **Where** | 有评估指标的任务（且能跑大量样本）|
| **When** | 任务量大、追求极致 |
| **Who** | Khattab et al. 2023（Stanford）|
| **How** | `import dspy; train, eval; teleprompter = dspy.MIPROv2; compiled = teleprompter.compile(program, train, eval)` |
| **How much** | 比手工 prompt +10-30% |
| **How many** | 优化阶段：100-1000 次 LLM 调用；推理：和手工相同 |

---

## 三、决策树：怎么选手段

```
任务来了
│
├─ 是数学/逻辑多步推理？
│   ├─ 简单：→ Zero-shot CoT（手段 1）
│   ├─ 中等：→ Few-shot CoT（手段 2）+ Self-Consistency（手段 3）
│   └─ 复杂（需试错）：→ ToT（手段 5）或 Plan-and-Solve（手段 8）
│
├─ 是开放式生成（写作/代码）？
│   ├─ → Self-Refine（手段 10）+ Self-Critique（手段 11）
│   └─ 想压极限：→ Universal Self-Consistency（手段 4）
│
├─ 需要外部信息/计算？
│   ├─ → RAG（手段 20）+ Tool Use（手段 13）
│   └─ 复杂代理：→ ReAct（手段 12）
│
├─ 答错后能反馈？
│   └─ → Reflexion（手段 9）迭代
│
├─ 多视角问题？
│   └─ → Multi-Agent Debate（手段 15）
│
├─ 追求格式 100% 合规？
│   └─ → Constrained Decoding（手段 19）
│
└─ 大规模生产、追求极致？
    └─ → DSPy 自动优化（手段 22）
```

---

## 四、组合策略（实战推荐）

### 黄金组合 1：通用推理任务
```
Few-shot CoT + Self-Consistency (N=5-10)
```
**理由**：CoT 展开推理，self-consistency 对冲随机性。覆盖 80% 推理任务。

### 黄金组合 2：代码生成
```
Expert Persona + ReAct（调代码解释器）+ Reflexion（用编译错误反馈）
```
**理由**：persona 框专业，ReAct 让 LLM 真跑代码，Reflexion 用错误迭代。

### 黄金组合 3：知识问答
```
RAG + Verify-then-Answer
```
**理由**：RAG 补事实，Verify 让 LLM 自检引用。

### 黄金组合 4：复杂决策
```
Multi-Agent Debate（3-5 agents，2-3 轮）+ Self-Critique
```
**理由**：多视角 + 自我反驳 = 减少单边论证。

### 黄金组合 5：批量生产
```
DSPy 自动优化（找最佳 prompt + few-shot）
```
**理由**：手工调 prompt 在大规模生产不可持续；自动化 + 可复现。

---

## 五、已知陷阱

| 陷阱 | 说明 | 规避 |
|---|---|---|
| **CoT 在小模型无效** | <10B 模型 CoT 反而降分（涌现点前）| 用 ≥10B 模型 |
| **Self-Consistency 只适合可枚举答案** | 开放式生成没法多数票 | 用 Universal Self-Consistency |
| **ToT 成本爆炸** | K^D 调用 | 限制深度 D=2-3，剪枝激进 |
| **Reflexion 缺反馈就退化为 Self-Refine** | 没有编译器/答案对照，反思可能空转 | 必须接外部反馈 |
| **Emotional Prompting 不稳定** | 不同模型效果差异大，可能无效 | 当 bonus，不当主力 |
| **RAG 检索差 = 全盘差** | 检索不到正确文档，LLM 答错 | 先优化检索（embedding/rerank）|
| **DSPy 优化过拟合** | 在训练集上过拟合 | 留独立测试集 |
| **Multi-Agent Debate 3 轮饱和** | 多于 5 轮边际收益递减 | 限 2-3 轮 |
| **Persona 不是万能** | 客观题效果小；过度 persona 显得做作 | 主观题用，客观题跳过 |

---

## 六、效果排序（综合论文数据，参考性）

| 排名 | 手段 | 典型增益 | 成本 |
|---|---|---|---|
| 1 | Few-shot CoT | +20-40pp | 中 |
| 2 | Self-Consistency | +5-15pp（在 CoT 基础上）| N× |
| 3 | ReAct + Tool Use | +30-50%（外部信息任务）| 中 |
| 4 | RAG | +20-40pp（知识任务）| 中 |
| 5 | Reflexion | +10-15pp（迭代）| 2-4× |
| 6 | ToT | +50pp（特定任务如 24 点）| 高 |
| 7 | DSPy 优化 | +10-30% | 优化高/推理低 |
| 8 | Multi-Agent Debate | +5-10pp | N×R |
| 9 | Plan-and-Solve | +5-20pp | 低 |
| 10 | Self-Refine | +10-20%（开放式）| 2-3× |
| 11 | Zero-shot CoT | +10-40pp | 极低 |
| 12 | Emotional Prompting | +0-10% | 极低 |
| 13 | Expert Persona | +5-10%（主观）| 极低 |

---

## 七、关键文献

1. Wei et al. 2022. *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS.
2. Kojima et al. 2022. *Large Language Models are Zero-Shot Reasoners*. NeurIPS.
3. Wang et al. 2022. *Self-Consistency Improves Chain of Thought Reasoning*. ICLR.
4. Yao et al. 2023. *Tree of Thoughts*. NeurIPS.
5. Shinn et al. 2023. *Reflexion*. NeurIPS.
6. Madaan et al. 2023. *Self-Refine*. NeurIPS.
7. Yao et al. 2022. *ReAct*. ICLR.
8. Lewis et al. 2020. *Retrieval-Augmented Generation*. NeurIPS.
9. Khattab et al. 2023. *DSPy*. arXiv.
10. Du et al. 2023. *Improving Factuality and Reasoning via Multi-Agent Debate*.

---

## 八、一句话总结

> **LLM 能力是潜在的，激活手段决定它能发挥多少**。最低成本最高收益：**CoT + Self-Consistency**（通用推理）；**RAG + Tool Use**（外部信息）；**Reflexion**（可迭代任务）；**DSPy**（大规模生产）。**情绪 prompt 是 bonus 不是主力**。

---

📌 **下一步**

- 想实操：复制"黄金组合 X"的模板到你任务上试
- 想深挖：看参考文献原文（最值得读的是 CoT、Self-Consistency、ReAct）
- 想自动化：上 DSPy，让它自动找最佳 prompt
