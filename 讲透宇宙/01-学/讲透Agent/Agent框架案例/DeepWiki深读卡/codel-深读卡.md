# codel 深读卡 —— Go 单体后端驱动的自托管 Docker 沙盒编码 Agent：LLM 每步只决定"下一个任务"，循环直到 done

> **定位**：codel 是一个 self-hosted 的全自主 AI 软件工程师：用户给出目标后，LLM 在沙盒 Docker 容器里循环使用 terminal、headless browser（Puppeteer）、code editor 三类工具逐步执行，直到标记 done。Go 后端（GraphQL + SQLite）+ React 前端（实时订阅 + 内嵌 Terminal）单容器部署，挂载宿主机 docker.sock 来动态创建执行容器。
> **本地**：`repos/codel`（semanser/codel）｜**深读**：deepwiki 17 子页归档 `deepwiki/codel/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Frontend（React/Vite） | Chat 界面、动态 Tab、xterm 终端回放、浏览器截图预览 | `ChatPage.tsx`、`Terminal.tsx`、`Messages.tsx` |
| API 层 | 单一 GraphQL 入口：queries/mutations/**subscriptions**（实时推送） | `graph/schema.graphqls`、`schema.resolvers.go` |
| Task Processing | 每 Flow 一条 Go channel 队列，顺序消费任务 | `executor/queue.go`（`AddQueue/ProcessQueue`）、`processor.go` |
| LLM Integration | `Provider` 接口抽象 OpenAI/Ollama，产出"下一个任务" | `providers.go`（`NextTask/DockerImageName/Summary`）、`agent.tmpl` |
| Container Execution | Docker 容器全生命周期 + 三类执行器 | `executor/container.go`、`terminal.go`、`browser.go` |
| Data | SQLite + sqlc 生成 ORM，四张核心表 | `Flow`、`Task`、`Container`、`Log` |
| Infra | Docker Engine（经 docker.sock）、Puppeteer | 单容器部署 `ghcr.io/semanser/codel:latest` |

## 二、核心机制

1. **"下一个任务"单步循环（而非一次性 plan）**：LLM 不生成完整计划，而是 `NextTask(history) → 执行 → 结果回填 DB → 再问 LLM`，直到 LLM 主动调 `done` 工具。每步即一个 `Task`（`input/terminal/browser/code/ask/done` 六型），失败/超长/解析错误统统**降级为 ask 任务问用户**，Agent 永不崩（来源：Core Systems、Language Model Integration）。
2. **队列 = `map[int64]chan database.Task`**：每个 Flow 独立 channel，天然实现多会话并发、单会话内严格串行；`stopChannels` 支持中止，Flow 结束 `CleanQueue`（来源：Core Systems L704-747）。
3. **LLM 选 Docker 镜像**：Flow 首个 input 任务处理时，`DockerImageName(task)` 让 LLM 按任务需求挑选运行环境，再 spawn 专属容器；`Summary()` 同步为 Flow 起名——LLM 既当大脑也当运维（来源：Language Model Integration L1714-1733）。
4. **上下文 = 任务史重放**：`tasksToMessages()` 把 DB 里的历史 Task 转成 user/assistant/tool 消息序列重新喂给 LLM，对话状态完全持久化在 SQLite，重启可续（来源：Language Model Integration L1590-1617）。

## 三、与讲透系列的对位

| codel 机制 | 讲透系列对位 | 互补点 |
|---|---|---|
| NextTask 单步循环 | Agent Loop / ReAct 模式 | codel 是"无显式 Thought、纯 tool call"的极简 ReAct 落地 |
| `Provider` 接口 + Factory | 模型层抽象 / Function Calling | 5 个工具的 schema 定义是 tool calling 最小完整样例 |
| `tasksToMessages` 任务史重放 | 记忆机制 / 上下文管理 | DB 即记忆，无向量检索——短程 Agent 的反例对照 |
| Docker 沙盒 + docker.sock | 工具调用之沙盒执行环境 | "Agent 动态建容器"的工程实现范本 |
| GraphQL subscriptions 实时推送 | 多模态 Agent UI / Human-in-the-loop | `ask` 工具把"问用户"做成一等公民 |

## 四、关键入口

```bash
# 部署：单容器 + 宿主 docker.sock
docker run -e OPEN_AI_KEY=... -p 3000:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/semanser/codel:latest

# 源码主线（按执行顺序）
backend/main.go                      # 启动：DB 迁移→Docker→Browser→GraphQL
backend/executor/queue.go            # ProcessQueue：每 Flow 一 channel 的消费循环
backend/providers/providers.go       # Provider 接口 + ProviderFactory + toolToTask
backend/providers/openai.go          # NextTask：历史→消息→tool call→database.Task
backend/executor/processor.go        # processInputTask / processTerminalTask / ...
backend/templates/prompts/agent.tmpl # Agent 系统提示词（"give the next best step"）
```

## 五、深读子页地图（17 页精选 5）

| 页 | full.md 行 | 价值 |
|---|---|---|
| Overview | L6 | 全局架构图 + 数据模型 + 端到端时序，5 分钟入门 |
| Core Systems | L628 | 三大核心系统串联，全库最大页（18KB） |
| Language Model Integration | L1396 | Provider/工具定义/任务生成/错误兜底，mermaid 最多（9 图） |
| Container Execution System | L1791 | 容器生命周期 + terminal/browser 执行细节 |
| Real-time Communication | L3316 | GraphQL subscriptions 双端实现，UI 如何"直播"Agent 操作 |

（备选：Database Schema L2598 看 sqlc 四表；Application Bootstrapping L5647 看启动序列）

## 六、与"我们"的关系（一句话）

codel 是"讲透 Agent Loop + 工具调用"最干净的 Go 参照实现——用 ~3 个文件就把 ReAct 循环、tool calling、沙盒执行、human-in-the-loop 全部走通，适合当零基础教程的"先看真家伙再拆原理"案例。

---
生成：2026-08-21 · deepwiki 17 页全归档
