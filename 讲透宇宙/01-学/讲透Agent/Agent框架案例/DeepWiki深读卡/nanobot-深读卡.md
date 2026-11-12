# nanobot 深读卡 —— HKUDS 超轻量个人 AI 助理运行时：可读性优先的"真拥有"极简内核

> **定位**：HKUDS（港大数据智能实验室）出品的超轻量自托管个人 AI 助理框架——刻意保持 agent 核心**小而可读**（"minimalist agent runtime, true ownership"），同时配齐长跑实用件：25+ 消息渠道（Telegram/飞书/Matrix/Discord/Slack）、React WebUI、工具/记忆/MCP/模型路由/自动化/部署。`Nanobot` facade SDK 可嵌入 Python 应用（`RunResult`/`StreamEvent` 类型化）。
> **本地**：`repos/nanobot`（HKUDS/nanobot）｜**深读**：deepwiki 49 子页归档 `deepwiki/nanobot/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 渠道层 | 25+ 消息平台 + WebUI | Telegram/Feishu/Matrix/Discord/Slack、React WebUI |
| SDK | 嵌入式调用 | `Nanobot` facade、`RunResult`/`StreamEvent` |
| Agent 引擎 | 执行循环 | `AgentLoop`（LLM 查询×工具调用，`max_tool_iterations=200`） |
| LLM 层 | 多 provider | 统一接口+集中路由（config/schema.py） |
| 工具/记忆/MCP | 能力与上下文 | tools、memory、MCP |
| 自动化 | 后台任务 | autonomous background tasks |

## 二、核心机制

1. **极简内核+实用外围**：核心循环（AgentLoop）一个类说清，外围（渠道/记忆/自动化）全是可选拼装——与 openclaw 的"五大件全家桶"对照，这是"能少则少"路线。
2. **200 次工具迭代上限**：单轮最多 200 次工具调用的显式配置——长任务自主性与安全阈值的默认权衡。
3. **25+ 渠道矩阵**：消息渠道覆盖面为同类最广（含飞书/Matrix 等中文/极客生态）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| AgentLoop 极简循环 | llm_agents 同主题（教学级清晰度） |
| 渠道矩阵 | openclaw 渠道插件对照 |
| max_tool_iterations | 循环终止工程 |

## 四、关键入口

```
nanobot/__init__.py     # Nanobot facade（L31-83）
nanobot/config/schema.py # 全配置（渠道/引擎/迭代上限）
docs/webui.md           # WebUI
```

## 五、深读子页地图（49 页精选 5）

Overview｜Agent Engine（AgentLoop）｜Channels（25+ 渠道）｜Memory/Tools｜Automation。

## 六、与"我们"的关系（一句话）

"个人助理 Agent"谱系里"极简东方派"标本——与 openclaw（重装备）/aeon（GitHub Actions 运行时）三对照讲"自托管助理的 N 种体格"。

---
生成：2026-08-21 · deepwiki 49 页全归档
