# CS329Z: Engineering AI Agents — 课程详细文档

> Stanford University, Autumn 2025-2026
> Instructor: **Diyi Yang** + **John Yang** (SWE-agent 一作)
> 时间: Mon/Wed 1:30-2:50 PM
> 先修: CS224N / CS224U / CS224V / CS336 之一
> 单位: 3-4

---

## 📚 课程定位

**CS329Z 是 Stanford 在 AI Agent 工程化方向的首门完整课程**，与 CS329A（Self-Improving）和 CS329X（Human-Centered）构成"Agent 三剑客"。

核心命题：**从单体 LLM 到 Compound AI Systems** 的工程化转变。学生从零写 RAG/Tool use/Agent loop，再用 DSPy 重写，反思抽象层级。

---

## 🎯 学习目标

完成本课程后，学生应能：

1. **理解** Compound AI Systems 与 monolithic LLM 的本质区别
2. **从零实现** RAG、Tool use、Agent loop（不依赖框架）
3. **使用** DSPy / LangChain / LlamaIndex 等主流框架
4. **设计** 4-tuple 评估方案（CS329Z 的核心方法论）
5. **构建** 一个 portfolio-ready agent 系统（学期项目）
6. **批判** agent 框架的局限（多 agent 失败模式 / LLM judge bias）

---

## 📅 完整模块（11 周 17 讲）

### Week 1: Foundations & Landscape
- **L1 (Mon Sep 23)** — 什么是 Agentic Systems？
  - 从 monolithic model → compound AI systems → agents 的谱系
  - 三大工程挑战：Decomposition / Data / Evaluation
  - 课程介绍 + logistics
- **L2 (Wed Sep 25)** — LLMs for Builders
  - litellm 统一 API
  - Structured output / 约束解码
  - Decoding strategies / test-time compute
  - Context engineering
  - Model selection（成本/延迟权衡）

**核心论文**：
- 🔴 **Zaharia et al. 2024** "The Shift from Models to Compound AI Systems" BAIR Blog — 思想锚点
- 🟡 Anthropic 2024 "Building Effective Agents" — 工程圣经

### Week 2: Building Blocks
- **L3 (Mon Sep 30)** — RAG（检索增强生成）
  - Grounding 与幻觉
  - Embeddings + 向量库
  - Chunking 策略
  - Hybrid search（BM25 + dense）
  - ColBERT (late interaction)
  - **Hands-on**: 从零写 RAG pipeline
- **L4 (Wed Oct 2)** — Tool Use & Function Calling
  - REPL / Function calling API
  - **MCP (Model Context Protocol)** — Anthropic 主导的开放标准
  - 工具设计原则
  - 代码执行沙箱
  - 错误处理 + retries

**核心论文**：
- 🔴 **Lewis et al. 2020** "RAG for Knowledge-Intensive NLP Tasks" NeurIPS
- 🟡 Khattab & Zaharia 2020 "ColBERT" SIGIR
- 🟡 MCP Specification (Linux Foundation 2025)

### Week 3: Frameworks & Patterns
- **L5 (Mon Oct 7)** — Frameworks
  - **DSPy** (signatures / modules / optimizers)
  - LangChain / LangGraph
  - LlamaIndex
  - 抽象层级对比
- **L6 (Wed Oct 9)** — Agent Design Patterns
  - Workflows vs agents taxonomy
  - 5 种 composable workflow patterns
  - ReAct / Plan-and-execute / Reflection
  - Scaffolds as design decisions

**核心论文**：
- 🔴 **Khattab et al. 2024** "DSPy" ICLR
- 🔴 **Yao et al. 2023** "ReAct" ICLR

### Week 4: Memory & Multi-Agent
- **L7 (Mon Oct 14)** — Agent Memory
  - Short vs long-term memory
  - Memory as tool-based actions
  - 文件系统作为外置记忆
  - Cross-agent memory
- **L8 (Wed Oct 16)** — Multi-Agent Systems
  - 单 vs 多 agent 架构
  - Orchestration patterns
  - Handoffs / state transfer
  - 错误传播

**核心论文**：
- 🟡 **MemGPT** (Packer 2023) — LLM as OS
- 🟡 Mem0 (2025) — 生产级长记忆
- 🟡 Park 2023 "Generative Agents" — Stanford 小镇
- 🔴 **AutoGen** (Wu 2024) — Microsoft 多 agent 旗舰
- 🔴 **Cemri et al. 2025** "Why Do Multi-Agent LLM Systems Fail?" — 关键批判

### Week 5: Optimization
- **L9 (Mon Oct 21)** — Optimization 全景
  - 从 prompt 到 fine-tuning 的谱系
  - **Prompt optimization**: GEPA / MIPROv2 / OPRO / TextGrad
  - Test-time compute scaling
  - LoRA / QLoRA
  - Distillation
  - RLHF / DPO（高层）
  - 何时优化 prompt / weights / inference
- **L10 (Wed Oct 23)** — Guest Lecture TBA

**核心论文**：
- 🔴 **Snell et al. 2024** "Scaling LLM Test-Time Compute" ICLR 2025
- 🔴 **GEPA** (Agrawal 2026) — prompt 优化可超 RL
- 🟡 Soylu 2024 "Fine-Tuning + Prompt Optimization Together"
- 🟡 Opsahl-Ong 2024 "MIPROv2"

### Week 6: Data for Agents
- **L11 (Mon Oct 26)** — Data Flywheels
  - Traces / demonstrations / feedback
  - Data for optimization vs evaluation
  - Synthetic data generation
  - Human-agent interaction data
- **L12 (Wed Oct 28)** — Data Selection & Quality
  - 找"最大信息量"数据
  - Filtering / selection strategies
  - Tiny-but-targeted benchmarks
  - 从 agent traces 构建数据集

**核心论文**：
- 🔴 **Shankar 2024** "Data Flywheels for LLM Applications"
- 🟡 Tan 2024 "LLMs for Data Annotation" survey
- 🔴 **Yang 2025** "SWE-smith" — 讲师 John Yang 一作
- 🔴 **Shankar 2024** "Who Validates the Validators?"

### Week 7: Evaluation
- **L13 (Mon Nov 2)** — Evaluation Fundamentals
  - 为什么 evals 难
  - **4-tuple 框架**: (request, environment, stopping criteria, scorer)
  - 好的 benchmark 的性质
  - Realistic scaffolding
- **L14 (Wed Nov 4)** — LLM-as-Judge & Infrastructure
  - 3 种 grader types
  - Judge prompt 设计
  - 已知 biases
  - Pairwise vs pointwise
  - **pass@k vs pass^k**（非确定性指标）
  - Anthropic 8-step roadmap

**核心论文**：
- 🟡 Press 2024 "How to Build Good LM Benchmarks"
- 🟡 tinyBenchmarks (Polo 2024)
- 🔴 **Anthropic 2026** "Demystifying Evals for AI Agents"
- 🔴 **MT-Bench / Chatbot Arena** (Zheng 2023)
- 🔴 **AutoMetrics** (Ryan 2026) — 讲师 Michael Ryan 一作

### Week 8: Safety + Coding Agents
- **L15 (Mon Nov 9)** — Agent Safety & Guardrails
  - 工具访问的隐私风险
  - **Prompt injection**（含 indirect injection）
  - Red-teaming
  - Sandboxing / permission models
  - 输出 guardrails
  - Liability / human-in-the-loop
- **L16 (Wed Nov 11)** — Coding & Software Agents
  - SWE-agent / Claude Code / OpenHands 端到端
  - Scaffolds as design decisions
  - SWE-bench + 4-tuple framework 实践

**核心论文**：
- 🔴 **PrivacyLens** (Shao 2024) — Diyi Yang 组
- 🟡 OpenAI 2025 "Prompt Injections"
- 🔴 **SWE-agent** (Yang 2024) — Agent-Computer Interfaces
- 🔴 **OpenHands** (Wang 2025)
- 🟡 Anthropic 2025 "Claude Code Best Practices"
- 🟡 Young 2025 "Effective Harnesses for Long-Running Agents"
- 🔴 **SWE-bench** (Jimenez 2024)

### Week 9: Frontiers
- **L17 (Mon Nov 16)** — Guest Lecture TBA
- **L18 (Wed Nov 18)** — Proactive Agents
  - Reactive → proactive 转变
  - **General User Models (GUM)**
  - Next Action Prediction
  - 开源 proactive agents
  - Privacy / trust
  - Mixed initiative
- **L19 (Mon Nov 30)** — Frontiers & Open Problems
  - Multimodal agents
  - Web agents / computer use
  - Science agents
  - Long-running architectures
  - Production observability（tracing/monitoring/cost）
- **L20 (Wed Dec 2)** — Final Demos

**核心论文**：
- 🔴 **GUM** (Shaikh 2025) — proactive agent 前沿
- 🟡 Shaikh 2026 "Next Action Predictor"
- 🟡 Xie 2024 "OSWorld" — multimodal agent benchmark
- 🟡 Yao 2022 "WebShop"

---

## 📋 作业（30% 总分，每次 10%）

每次作业后有 **10 分钟 oral exam**（CS329Z 的独特设计）。

### HW1: Build an Agentic System (Weeks 3-5)
- **Part A** (从零写): litellm + RAG + Tool use + Agent loop (ReAct)
- **Part B** (DSPy 重写): 用 DSPy 重构关键组件 + 反思
- **场景**: 给一个论文仓库，做一个 agent 回答科学问题

### HW2: Data for Agents (Weeks 6-8)
- 给定 staff agent
- 学生收集 + curate 数据优化它
- 数据选择 / 质量过滤 / 合成数据
- 构建 SFT 或 preference pairs
- **交付**: curated dataset + data card + 分析

### HW3: Evaluate an Agent (Weeks 7-9)
- 给定预构建 agent
- 设计完整 evaluation suite
- Code-based grader + LLM-as-judge
- 用 4-tuple 框架构建 benchmark
- Error analysis

---

## 🎓 Project (39% 总分)

**主题**: "Making Life at Stanford Better with Agents"

例子:
- 课程大纲 reader（提取 deadline → 加日历）
- 课程排课优化器
- 论文发现 + 摘要 agent
- 校园活动聚合推荐

**里程碑**:
- Week 3: 1-page proposal
- Week 6: Midway report + 工作原型 demo
- Week 10: Final submission + Demo Day

---

## 💻 项目代码（本仓库）

### 📁 主要位置

| 项目 | 路径 | 完成度 |
|------|------|--------|
| HW1 Part A (mini-Agent) | `topic2-agents/cs329z-hw1a/` | ★★★★★ |
| HW1 Part B (DSPy) | `topic2-agent-v2/dspy_framework.py` | ★★★★☆ |
| HW2 (Data Flywheel) | `topic2-agent-v2/hw2_data_flywheel.py` | ★★★★★ |
| HW3 (4-tuple Eval) | `topic2-agent-v2/hw3_self_improve_coding.py` | ★★★★★ |

### 🚀 运行

```bash
# HW1 Part A 完整 demo
cd topic2-agents/cs329z-hw1a
python3 demo.py

# HW1 Part B
cd topic2-agent-v2
python3 dspy_framework.py

# HW2 (Data Flywheel)
python3 hw2_data_flywheel.py

# HW3 (Eval Suite)
python3 hw3_self_improve_coding.py
```

### 🧪 测试

```bash
cd topic2-agents/cs329z-hw1a
python3 -m pytest tests/ -v
```

---

## 🔬 关键实现细节

### mini-Agent v0.1 架构
```
LLMClient (litellm + Mock 兜底)
    ↓
SimpleRAG (chunking + embedding + retrieval)
    ↓
ToolRegistry (calculator + search + read_file)
    ↓
ReActAgent (Thought → Action → Observation loop)
    ↓
AgentTrace (可观测性 + 调试)
```

### 4-tuple Eval 框架
```python
EvalCase(
    request="What is 5+3?",
    environment={"tools": ["calculator"]},
    stopping_criteria=lambda r: True,
    scorer=numeric_scorer(8.0)
)
```

### Data Flywheel
```
agent → traces → 数据选择 → SFT/DPO → 更强 agent → 更好 traces → ...
```

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **AI 工程师** | CS329Z 全套（最高 ROI） |
| **AI 产品经理** | HW1 + W7-W8 (Eval + Safety) |
| **Coding Agent 工程师** | HW1 + W9 SWE-agent + CS329M |
| **想读 PhD** | HW1 + W6 (Data) + W7 (Eval) + 研究 project |

---

## 📊 评分构成

| 部分 | 占比 |
|------|------|
| Project | 39% (proposal 8% + midway 5% + midway demo 5% + final 8% + final demo 15%) |
| Oral check-ins | 20% (2 次 oral exam) |
| Homework | 30% (3 × 10%) |
| Participation | 5% |

---

## 🔗 关键资源

- **课程官网**: https://cs329z.stanford.edu/
- **Anthropic Building Effective Agents**: https://www.anthropic.com/engineering/building-effective-agents
- **DSPy 文档**: https://dspy.ai/
- **MCP 规范**: https://modelcontextprotocol.io/
- **SWE-bench Leaderboard**: https://www.swebench.com/

---

## 💡 反思与批判

### 课程优势
1. **从零写 vs 框架**的双轨设计极其精妙
2. 4-tuple 评估方法论可推广到任何 AI 项目
3. 讲师是 SWE-agent 作者，工业经验丰富

### 潜在局限
1. **过度 Stanford NLP 视角** — DSPy / SWE-agent / OpenHands 都是讲师自家工作
2. **多 agent 章节偏批判** — Neubig "Don't Sleep on Single-agent" 立场明显
3. **缺少 Production / Observability 实战** — W19 只 1 节
4. **Project 主题过于 utility** — 不鼓励有研究深度的工作

---

## 🚀 下一步扩展

完成 CS329Z 后推荐：
1. **CS329A** Self-Improving Agents — 学自我改进（STaR / RL）
2. **CS349E** Efficient ML Infrastructure — 学部署优化
3. **CS329X** Human-Centered LLMs — 学伦理与多元
4. **CS329H** ML from Human Preferences — 学 RLHF 数学
5. 实习/工作：apply 到 OpenHands / Cursor / Replit / Anthropic

---

**最后更新**: 2026-08-11
**文档版本**: v1.0
**对应代码版本**: topic2-agents/cs329z-hw1a (mini-Agent v0.1)
