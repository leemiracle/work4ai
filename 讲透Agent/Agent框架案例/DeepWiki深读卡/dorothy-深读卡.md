# dorothy 深读卡 —— Electron 桌面并行编码 Agent 编排器：PTY 隔离 10+ Agent 同跑 + 五 MCP 服务器

> **定位**：Charlie85270 出品的 Electron 桌面应用——编排多个 AI 编码 Agent（**Claude Code/Codex/Gemini/本地模型**）并行执行：突破 CLI 单 agent 限制，10+ agent 跨项目同时跑，配自动化/远程控制/任务管理/持久知识库。Agent=Claude CLI 进程跑在隔离 PTY，五状态机（idle→running→completed/error/waiting）；**Super Agent** 可访问全部 MCP orchestrator 工具充当总指挥。
> **本地**：`repos/dorothy`（Charlie85270/Dorothy）｜**深读**：deepwiki 61 子页归档 `deepwiki/dorothy/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 桌面壳 | Electron 应用 | electron/core/agent-manager.ts（agents Map） |
| Agent 运行时 | PTY 隔离进程 | `AgentStatus`（五状态）、每 agent 独立 project path/skills/config |
| MCP 生态 | 五服务器 40+ 工具 | `mcp-orchestrator`(26 工具：管理/消息/调度/自动化)、`mcp-vault`(10：文档+全文搜索)、`mcp-kanban`(8)、`mcp-telegram`(4)、`mcp-socialdata`(5) |
| Super Agent | 总指挥 | isSuperAgent()=访问全部 orchestrator 工具 |
| UI | 多 agent 视图 | User Interface 子系统 |

## 二、核心机制

1. **Agent=PTY 进程**：每个编码 Agent 是独立伪终端会话的 CLI 进程——隔离+真实终端行为，桌面层只做编排不做执行（与 bernstein 的 40+ adapter 思路对照：Dorothy 深度绑定 Claude 生态但编排粒度到 PTY）。
2. **五 MCP 分域服务器**：编排/知识库/看板/消息/社交数据各一服务器，每服务器独立 Node 进程 stdio 通信——按域拆分 MCP 的工程范本（对照 dust 的 60+ 工具单仓库路线）。
3. **Super Agent 元编排**：一个特殊 agent 持全部管理工具——"管理 agent 的 agent"最直接实现。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| PTY 隔离多 agent | 讲透多Agent协作/01 §进程级隔离编排 |
| MCP 分域服务器 | 讲透Agent/02 §MCP（域拆分设计） |
| Super Agent | 讲透多Agent协作/01 §层级编排 |

## 四、关键入口

```
electron/core/agent-manager.ts    # agent 生命周期（L34 agents Map）
mcp-*/                            # 五个 MCP 服务器
```

## 五、深读子页地图（61 页精选 5）

Overview｜Agents（PTY 生命周期）｜MCP Ecosystem（五服务器详解）｜User Interface｜Build and Release。

## 六、与"我们"的关系（一句话）

"桌面版多编码 Agent 指挥台"样本——与 bernstein（服务端编排）/claw-code（Lane 事件流）对照讲"多 CLI agent 编排的 N 种宿主形态"。

---
生成：2026-08-21 · deepwiki 61 页全归档
