# swarmclaw 深读卡 —— 自托管 Agent 编排平台：LangGraph 多 Agent + 心跳自主循环 + SKILL.md 技能生态

> **定位**：swarmclawai 出品的自托管 AI Agent 编排平台——单面板管多 LLM provider、跑自主/半自主 agent、定时调度、桥接外部聊天平台（Discord/Slack/Telegram/WhatsApp）。Node.js + Next.js UI（:3456）+ `swarmclaw` CLI，全状态本地 SQLite（零外部依赖起步）。亮点：**LangGraph 驱动的多 agent 编排器**（子 agent 委派）、**heartbeat 心跳驱动的主 agent 循环**（后台自主）、cron/interval/one-time 调度守护、SKILL.md 技能发现 + MCP 集成、Ollama/OpenClaw 本地推理。
> **本地**：`repos/swarmclaw`（swarmclawai/swarmclaw）｜**深读**：deepwiki 74 子页归档 `deepwiki/swarmclaw/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Web UI | 仪表盘（:3456） | Next.js UI |
| 会话 | 流式聊天 | SSE 流式响应 |
| 自主循环 | 后台 agent | **heartbeat-driven ticks 主循环** |
| 编排 | 多 agent | **LangGraph orchestrator + sub-agent delegation** |
| 调度 | 定时任务 | cron/interval/one-time daemon |
| 渠道 | 聊天平台桥接 | Discord/Slack/Telegram/WhatsApp connectors |
| 推理 | provider | 多 LLM + Ollama/OpenClaw 本地 |
| 工具 | 能力 | shell/browser/sandbox/file per agent |
| 技能 | 技能学习 | **SKILL.md discovery + MCP** |
| 存储 | 状态 | 本地 SQLite（data/） |

## 二、核心机制

1. **心跳自主循环**：主 agent loop 由 heartbeat 定时 tick 驱动——agent 不只是被动应答，可自主巡检（openclaw heartbeat 同思潮的 Node.js 实现）。
2. **LangGraph 编排内嵌**：多 agent 委派直接用 LangGraph 而非自研图引擎——"平台壳×成熟编排核"的务实组合。
3. **SKILL.md 生态**：技能以 SKILL.md 发现与加载（与 openclaw/AWS Agent Skills 同规范）——技能规范 2026 事实标准又添一员。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| heartbeat 自主 | 讲透学习型Agent §主动性 |
| LangGraph 子图委派 | 讲透多Agent协作/03 §图编排 |
| SKILL.md | 讲透Agent/02 §Skills 规范 |

## 四、关键入口

```
（Node.js 应用：web UI+CLI+daemon；详见 wiki Architecture 分层图）
```

## 五、深读子页地图（74 页精选 5）

Overview（用例×特性表）｜Architecture（分层）｜Main Agent Loop/heartbeat｜LangGraph orchestrator｜Scheduling daemon。

## 六、与"我们"的关系（一句话）

openclaw 生态的"平台化亲戚"——同 SKILL.md/heartbeat 基因，但走 LangGraph 编排+Web 面板路线，两仓对照看个人助手→编排平台的分化。

---
生成：2026-08-21 · deepwiki 74 页全归档
