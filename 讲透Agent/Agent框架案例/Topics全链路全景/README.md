# Topics 全链路全景 · 索引

```yaml
card_id: github-topics-fullchain-panorama
title: AI 大模型全链路 GitHub Topics 索引体系（Prompt→Context→MCP/Skills→训练→模型）
universe: Agent框架案例
burke:
  场景: 用户需要从 Prompt 到模型本体的完整技术链路选型与学习地图，GitHub topics 是社区自发标注的生态侧写
  主体: 全链路开发者（应用/框架/算法/推理/模型五类角色）
  能动: 本目录（实测仲裁者）+ 三家素材（Kimi 遍历报告 + 用户两份分层框架）+ GitHub Search API
  行动: 68 个核心 topics 逐个 API 实测 → 三家素材对账仲裁（纠正 fine-tuning 错 67 倍/RAG 漏主 topic 45 倍/MCP 长短名百倍差）→ 十层归组 → 每层写使用背景与代表仓卡 → 5W2H/第一性原理/SWOT/成本阶梯四方法收束
  目的: 把"找参考实现/判断技术成熟度/选赛道"从碰运气变成查表——一张实测校准的 AI 技术栈 GitHub 侧写
  张力: 大 topic 趋势可见但噪声大 vs 小 topic 精准但覆盖窄；概念传播快 vs topic 习惯形成慢（reasoning-model 仅 9 仓）；零训练层大众化 vs 训练层专业化
  弧线: 三家素材结构各异 → 实测统一仲裁 → 十层 MECE 体系成型 → 成为项目内 MCP/Skills 深潜篇的总纲 + 其余八层的检索索引
status: 已完成（快照 2026-08-19）
refs:
  - data/counts-2026-08-19.json（68 topics 实测留档）
  - Kimi《AI 开发全链条 GitHub Topics 完整遍历报告（去重版）》（用户提供 TOS 链接原文）
  - 用户两份分层框架（5 层链路版 / 10 层索引版）
  - 两个深潜篇：../MCP协议生态全景/、../Skills生态全景/（同日快照）
updated: 2026-08-19
```

> 一句话定位：**「Prompt → Context → MCP/Skills → 微调/对齐 → 推理/模型」全链路 GitHub Topics 的实测索引体系**——68 个 topics 逐个 API 实测（2026-08-19）、三家素材对账仲裁、十层归组、每层附使用背景/代表仓/批判视角，5W2H 等四方法收束。**本目录是总纲，L3/L4 两层由姊妹深潜篇承载**（MCP 全景/Skills 全景）。

## 六篇导读

| 篇 | 内容 | 何时查 |
|---|---|---|
| [`notes/01-链路总纲与实测仲裁.md`](notes/01-链路总纲与实测仲裁.md) | 十层链路图；**三家素材对账**（Kimi 报告 fine-tuning 错 67 倍等三处纠正）；68 topics 实测总表；六条结构洞察（规模断层/概念热topic冷/对齐三兄弟/产品名topic化） | 先读这篇——全景与纠错 |
| [`notes/02-交互与知识层Topics.md`](notes/02-交互与知识层Topics.md) | L1 Prompt（prompt-engineering 16k/system-prompts/dspy 范式迁移）+ L2 Context（context-engineering 2.7k/letta）+ L5 RAG（rag 41k 五层标签栈：embeddings→vecdb→rerank→rag→agentic-rag） | 写 prompt/搭 RAG/管上下文 |
| [`notes/03-连接与能力层Topics.md`](notes/03-连接与能力层Topics.md) | L3 MCP 双名现象（mcp 64k vs modelcontextprotocol 663）+ L4 五个 agent 大词分工（ai-agents 74k/agentic-ai/autonomous/llm-agents/multi-agent）+ agent-skills>skills 收敛 | 选工具方案/agent 框架选型 |
| [`notes/04-训练层Topics.md`](notes/04-训练层Topics.md) | L6 微调（lora 5k/peft 1.1k/unsloth 73k★）+ L7 对齐三兄弟（rlhf 778/grpo 522/dpo 441）+ L8 数据评测（synthetic-data 2.4k 最热） | 动微调/对齐/造数据 |
| [`notes/05-模型与推理层Topics.md`](notes/05-模型与推理层Topics.md) | L9 推理三分格局（vllm 89k★/sglang/llama.cpp）+ L10 模型（llm 116k/transformers 单复数语义分野/reasoning-model 9 仓空壳）+ 横切 | 部署推理/选底座 |
| [`notes/06-5W2H方法论详解.md`](notes/06-5W2H方法论详解.md) | 全链路 5W2H 总表 + 十层逐层 5W2H 速查 + 第一性原理（"固定权重如何获得新能力"）+ SWOT + 选型成本阶梯 | 方法论/写报告/做决策 |

## 速查：什么问题查哪里

- **某层该用什么 topic 检索/代表仓是谁** → 对应层篇（02-05）
- **数字可信度/怎么被坑的** → `notes/01` §1 对账表
- **技术选型决策（先 RAG 还是先微调）** → `notes/06` §5 成本阶梯
- **MCP/Skills 深度内容** → 姊妹深潜篇 `../MCP协议生态全景/`、`../Skills生态全景/`
- **季度复测** → 重跑 search API 对比 `data/counts-2026-08-19.json`（盯 agent-skills/agentic-rag/grpo/speculative-decoding 四个增长指标）

## 数据快照

`data/counts-2026-08-19.json`——68 topics 的 total_count 原始留档（GitHub Search API，per_page=1，未认证，当日跑完 68/68）。
