# 前沿与媒体 · 08 - AI Agent 框架与工具调用专题

> 姊妹篇：[`02-后训练`](./02-后训练信息源专题.md)（RL 后端 verl/OpenRLHF）｜[`06-AI 编程工具`](./06-AI编程工具专题.md)（编程 Agent）｜横向打通 [`../横向打通-能力获取决策框架.md`](../横向打通-能力获取决策框架.md)。
>
> Agent 是 2024–2026 LLM 应用的"下一个范式"——从"问一次答一次"到"自主规划 + 工具调用 + 多步执行"。本篇把 Agent **框架 / 协议 / 评测 / 平台**集中。
>
> **核对日期**：2026-08-03（首版；LangChain 实抓确认 Interrupt 2026 大会）
> **图例**：🟢 = 活跃　🟡 = 稳定　🔴 = 停更

---

## 0. 一张图：Agent 生态栈

```
┌──────────────────────────────────────────┐
│  ④ Agent 平台（成品）                       │   ← OpenHands / Devin / AutoGPT / Cursor
└──────────────────────────────────────────┘
                ↑
┌──────────────────────────────────────────┐
│  ③ 框架（构建 Agent）                       │   ← LangGraph / AutoGen / CrewAI / LlamaIndex / Agno
└──────────────────────────────────────────┘
                ↑
┌──────────────────────────────────────────┐
│  ② 协议（工具调用标准化）                    │   ← MCP（Model Context Protocol）/ function calling
└──────────────────────────────────────────┘
                ↑
┌──────────────────────────────────────────┐
│  ① 模型（reasoning + tool use）             │   ← Claude / GPT / Gemini / DeepSeek
└──────────────────────────────────────────┘
```

---

## 一、Agent 框架（构建层）

| # | 框架 | 公司/作者 | 强项 | 状态 |
|---|---|---|---|---|
| A1-1 | **LangChain + LangGraph** [langchain.com](https://www.langchain.com/) | Harrison Chase | ✅ 本轮实抓确认 "Interrupt 2026 大会"（伦敦 + 纽约），LangSmith 是商业化 | 🟢 |
| A1-2 | **AutoGen** | Microsoft | 多 Agent 对话框架 | 🟢 |
| A1-3 | **CrewAI** | João Moura | 角色化多 Agent 协作 | 🟢 |
| A1-4 | **LlamaIndex** | Jerry Liu | RAG 起家，扩到 Agent | 🟢 |
| A1-5 | **Agno**（前 Phidata）| Agno | 简洁、生产友好 | 🟢 |
| A1-6 | **Pydantic AI** | Pydantic 团队 | 强类型 Agent 框架（Pythonista 必看）| 🟢 新 |
| A1-7 | **Smolagents** | HuggingFace | HF 出品"微型" Agent 框架 | 🟢 新 |
| A1-8 | **OpenAI Agents SDK** | OpenAI | OpenAI 官方 | 🟢 新 |
| A1-9 | **Anthropic SDK + Tool Use** | Anthropic | Claude 官方 | 🟢 |

---

## 二、Agent 协议（工具调用标准化）

| # | 协议 / 标准 | 提出者 | 强项 |
|---|---|---|---|
| A2-1 | **MCP（Model Context Protocol）** [modelcontextprotocol.io](https://modelcontextprotocol.io/) | Anthropic 2024-11 | **2025 起 Agent 工具调用事实标准**（被 OpenAI/Google 跟进）|
| A2-2 | **Function Calling** | OpenAI 2023 | 最早工具调用 API，各家 LLM 已通用 |
| A2-3 | **OpenAI Responses API** | OpenAI | 升级版 Function Calling |
| A2-4 | **Computer Use** | Anthropic | Claude 操作电脑（鼠标/键盘/截图）|
| A2-5 | **A2A（Agent-to-Agent）** | Google 2025 | 多 Agent 通信协议 |

---

## 三、Agent 平台（成品 / SaaS）

| # | 平台 | 类型 | 强项 |
|---|---|---|---|
| A3-1 | **Claude Code** | CLI Agent | 已在 [`06 编程清单 P2-1`](./06-AI编程工具专题.md) |
| A3-2 | **OpenHands** | 开源 Agent 平台 | 已在 [`06 编程清单 P2-2`](./06-AI编程工具专题.md) |
| A3-3 | **Devin** | 商业自主 SWE | Cognition |
| A3-4 | **AutoGPT / BabyAGI** | 早期自主 Agent | 2023 现象级，现主要用于教学 |
| A3-5 | **Manus**（蝴蝶效应 / Monica）| 中国通用 Agent | **2025 国产现象级 Agent** |
| A3-6 | **Genspark / You.com / Perplexity Agent** | 搜索 Agent | 商业落地 |
| A3-7 | **Sierra / Decagon / Crescendo** | 客服 Agent | 企业垂直 |

---

## 四、Agent 评测

| # | 评测 | 类型 | 强项 |
|---|---|---|---|
| A4-1 | **SWE-Bench / SWE-Bench Verified** | 真实 GitHub PR | 已在 [`06 编程清单 P4-2`](./06-AI编程工具专题.md) |
| A4-2 | **WebArena / VisualWebArena** | 网页操作 | 浏览器 Agent 评测 |
| A4-3 | **AgentBench** | 多任务 Agent | 8 类任务 |
| A4-4 | **GAIA** | 通用 Agent | DeepMind + Meta + HuggingFace，"现实世界问题" |
| A4-5 | **τ-bench（tau-bench）** | 工具调用多轮 | 多轮工具调用评测 |
| A4-6 | **MLE-Bench** | ML 工程任务 | OpenAI 出品，Agent 跑 Kaggle |

---

## 五、Agent 综述与教程

| # | 源 | 类型 | 强项 |
|---|---|---|---|
| A5-1 | **Lilian Weng "LLM Agents"** | 综述 | 已在 [`01 清单 B2`](./01-AI顶级信息源实时清单.md)，OpenAI 主管级综述 |
| A5-2 | **Anthropic "Building Effective Agents"** | 官方 blog | 2024-12，**最实用的 Agent 设计模式指南** |
| A5-3 | **HuggingFace Agents Course** | 官方课 | HF 出品，免费 |
| A5-4 | **DeepLearning.AI "AI Agents in LangGraph"** | 短课 | Harrison Chase 主讲 |
| A5-5 | **Andrew Ng "Agentic Design Patterns"** | 短文 | 4 大模式：Reflection / Tool Use / Planning / Multi-Agent |

---

## 六、中文 Agent 生态

| # | 项目 | 公司 | 强项 |
|---|---|---|---|
| CN-1 | **Manus** | 蝴蝶效应 | 2025 国产现象级通用 Agent |
| CN-2 | **MetaGPT** | DeepWisdom | 多 Agent 协作（产品经理/架构师/工程师角色）|
| CN-3 | **字节豆包 / Coze** | 字节 | Coze 海外版（扣子）很火 |
| CN-4 | **智谱 GLM Agent / AutoGLM** | 智谱 | 手机操作 Agent |
| CN-5 | **百度文心智能体平台** | 百度 | 低代码 Agent 平台 |
| CN-6 | **阿里通义万相 / 百炼** | 阿里 | Agent 平台 |

---

## 七、维护说明

- **2026-08-03 首版**：✅ LangChain 实抓确认 Interrupt 大会；⚠️ MCP 文档站 onlyMainContent 抓空。
- **下次重核**：每 3 个月（Agent 生态月度级迭代）。
- **重点跟踪**：MCP 生态扩张、SWE-Bench 排行、Manus 类中国 Agent 走向。

📌 **下一步**：想用 LangGraph 跑通第一个 Agent？告诉我任务（写报告 / 调研 / 写代码），我给可运行代码 + 评测。

---

> 🔗 相关：[`../横向打通-能力获取决策框架.md`](../横向打通-能力获取决策框架.md)（什么时候用 Agent vs RAG vs Prompt）｜ [`../讲透Agent/`](../讲透Agent/)（教程）
