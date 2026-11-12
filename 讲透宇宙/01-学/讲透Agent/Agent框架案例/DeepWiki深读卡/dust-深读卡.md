# dust 深读卡 —— 法国企业 AI 助手平台：Temporal 持久化 Agent 执行 + MCP 工具 + 技能系统

> **定位**：dust-tt（法国巴黎，Y Combinator 系）的企业 AI 助手平台——对话式 Agent + 工具执行（60+ 内置 MCP 工具）+ workspace 知识集成 + **Temporal durable 执行**（重试策略/流式更新）+ 技能系统（instructions+tools+knowledge 打包）+ 定时/webhook 触发器。七层架构的企业级 SaaS 开源样本。
> **本地**：`repos/dust`（dust-tt/dust）｜**深读**：deepwiki 26 子页归档 `deepwiki/dust/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端 | 对话 UI | front/（Next.js） |
| Agent 系统 | 多步 agent 工作流 | Agent System（多 provider LLM） |
| 工具系统 | MCP 扩展 | 60+ 内置工具 + 远程 MCP server |
| 知识集成 | workspace 数据源/文档/结构化数据 | data sources |
| 持久化执行 | durable agent 运行 | **Temporal**（retry 策略+streaming） |
| 技能系统 | 可复用能力包 | Skills（instructions+tools+knowledge） |
| 触发器 | 自动化调用 | Scheduled + Webhook |
| 类型/SDK | 契约 | sdks/js types |

## 二、核心机制

1. **Temporal durable 执行**：agent 多步工作流跑在 Temporal 上——重试策略/心跳/流式进度全部企业级（对照 mastra 的 Inngest 引擎：同为"工作流持久化换可靠性"路线，Dust 更早更彻底）。
2. **技能=三合一能力包**：instructions（怎么做）+tools（用什么）+knowledge（知道什么）打包成可分享单元——企业内 Agent 知识沉淀的单位设计。
3. **MCP 深度集成**：60+ 内置工具全 MCP 化 + 远程 MCP server 接入——平台即 MCP 生态公民。
4. **触发器系统**：定时/网络钩子自动唤起 agent——从"被动问答"到"主动企业流程参与者"。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| Temporal durable 执行 | 讲透Agent/00 §可靠性（对照 mastra 三引擎） |
| 技能三合一包 | 讲透Agent/02 §Skills（openclaw 同规范） |
| MCP 60+ 工具 | 讲透Agent/02 §MCP 生态 |
| 触发器自动化 | cline Cron/openclaw heartbeat 同思潮 |

## 四、关键入口

```
front/                    # Next.js 应用（含 /api agent 路由）
sdks/js/src/types.ts      # 类型契约源头
front/lib/actions/mcp_internal_actions/  # MCP 内置工具
```

## 五、深读子页地图（26 页精选 5）

Overview（七层架构）｜Agent System｜MCP Tool System｜Conversation System｜Type System and SDK。

## 六、与"我们"的关系（一句话）

企业 Agent 平台的"欧洲样本"——与 superagi（2023 平台化石）对照可看出 Agent 平台从"工具市场"到"durable 执行+技能+MCP"的两年进化全谱。

---
生成：2026-08-21 · deepwiki 26 页全归档
