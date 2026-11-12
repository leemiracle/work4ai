# Claude Code 源码与拆解

本仓库包含两部分内容：

- `src/`：Claude Code 泄露的 TypeScript 源码（约 1884 个文件、51 万行），来自 2026 年 3 月 npm 包中未删除的 source map
- `articles/`：基于这份源码的 20 篇深度拆解，覆盖一个生产级 Agent 的完整实现面

## 源码拆解系列

所有论断均标注源码文件与行号，代码节选自真实源文件。完整索引见 [articles/README.md](./articles/README.md)。

**核心循环与工具**

| # | 日期 | 文章 |
|---|------|------|
| 01 | 2026-04-02 | [启动链路与整体架构](./articles/01-bootstrap-and-architecture.md) |
| 02 | 2026-04-04 | [Agent 主循环：queryLoop 状态机](./articles/02-agent-loop.md) |
| 03 | 2026-04-04 | [流式协议与 API 客户端](./articles/03-streaming-and-api-client.md) |
| 04 | 2026-04-04 | [工具系统架构：注册、调度与并发](./articles/04-tool-system.md) |
| 05 | 2026-04-04 | [Bash 工具的三层防线](./articles/05-bash-tool-security.md) |
| 06 | 2026-04-05 | [文件与搜索工具](./articles/06-file-and-search-tools.md) |

**上下文与记忆**

| # | 日期 | 文章 |
|---|------|------|
| 07 | 2026-04-05 | [系统提示词装配流水线](./articles/07-system-prompt-assembly.md) |
| 08 | 2026-04-05 | [提示缓存与成本工程](./articles/08-prompt-caching-and-cost.md) |
| 09 | 2026-04-05 | [上下文压缩体系](./articles/09-context-compaction.md) |
| 10 | 2026-04-07 | [记忆系统](./articles/10-memory-system.md) |

**安全与扩展**

| # | 日期 | 文章 |
|---|------|------|
| 11 | 2026-04-09 | [权限决策管线](./articles/11-permission-pipeline.md) |
| 12 | 2026-04-11 | [沙箱与容器出口代理](./articles/12-sandbox-and-egress-proxy.md) |
| 13 | 2026-04-11 | [MCP 客户端](./articles/13-mcp-client.md) |
| 14 | 2026-04-11 | [Skills：渐进式披露的实现](./articles/14-skills-progressive-disclosure.md) |
| 15 | 2026-04-11 | [Subagent 与多 Agent 体系](./articles/15-subagent-and-multi-agent.md) |
| 16 | 2026-04-11 | [Hooks 引擎](./articles/16-hooks-engine.md) |

**持久化、交互与收官**

| # | 日期 | 文章 |
|---|------|------|
| 17 | 2026-04-12 | [会话持久化与恢复](./articles/17-session-storage-and-resume.md) |
| 18 | 2026-04-12 | [TUI 渲染与交互层](./articles/18-tui-rendering.md) |
| 19 | 2026-04-12 | [任务系统与自动化](./articles/19-tasks-and-automation.md) |
| 20 | 2026-04-12 | [隐藏面：feature flag、彩蛋与对抗设计](./articles/20-hidden-surface.md) |

## 阅读路径

只想快速了解实现要点：02（主循环）→ 04（工具系统）→ 09（上下文压缩）→ 11（权限）。关心安全：05 → 11 → 12。关心 Agent 设计取舍：06 → 14 → 15 → 20。
