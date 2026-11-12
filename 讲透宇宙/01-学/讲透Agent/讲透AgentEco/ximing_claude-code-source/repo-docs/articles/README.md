# Claude Code 源码拆解系列

基于本仓库 `src/` 中泄露的 Claude Code TypeScript 源码（约 1884 个文件、51 万行）的 20 篇深度拆解：工作日两天一篇，周末集中更新，覆盖 Agent 工程的完整技术面：主循环、工具系统、提示词装配、上下文压缩、记忆、权限、沙箱、MCP、Skills、多 Agent、Hooks、会话持久化、TUI、任务系统与隐藏面。

所有论断均标注源码文件与行号，代码节选自真实源文件。

| # | 日期 | 文章 |
|---|------|------|
| 01 | 2026-04-02 | [启动链路与整体架构——51 万行源码怎么组织](./01-bootstrap-and-architecture.md) |
| 02 | 2026-04-04 | [Agent 主循环——queryLoop 状态机](./02-agent-loop.md) |
| 03 | 2026-04-04 | [流式协议与 API 客户端——边生成边执行](./03-streaming-and-api-client.md) |
| 04 | 2026-04-04 | [工具系统架构——注册、调度与并发](./04-tool-system.md) |
| 05 | 2026-04-04 | [Bash 工具的三层防线](./05-bash-tool-security.md) |
| 06 | 2026-04-05 | [文件与搜索工具——为什么是 grep 而不是向量索引](./06-file-and-search-tools.md) |
| 07 | 2026-04-05 | [系统提示词装配流水线](./07-system-prompt-assembly.md) |
| 08 | 2026-04-05 | [提示缓存与成本工程](./08-prompt-caching-and-cost.md) |
| 09 | 2026-04-05 | [上下文压缩体系——五层压缩策略](./09-context-compaction.md) |
| 10 | 2026-04-07 | [记忆系统——文件记忆、自动提取与"做梦"整理](./10-memory-system.md) |
| 11 | 2026-04-09 | [权限决策管线](./11-permission-pipeline.md) |
| 12 | 2026-04-11 | [沙箱与容器出口代理](./12-sandbox-and-egress-proxy.md) |
| 13 | 2026-04-11 | [MCP 客户端——连接、OAuth 与工具命名空间](./13-mcp-client.md) |
| 14 | 2026-04-11 | [Skills——渐进式披露的实现](./14-skills-progressive-disclosure.md) |
| 15 | 2026-04-11 | [Subagent 与多 Agent 体系](./15-subagent-and-multi-agent.md) |
| 16 | 2026-04-11 | [Hooks 引擎——5022 行的用户扩展点](./16-hooks-engine.md) |
| 17 | 2026-04-12 | [会话持久化与恢复](./17-session-storage-and-resume.md) |
| 18 | 2026-04-12 | [TUI 渲染与交互层——重度 fork 的 Ink](./18-tui-rendering.md) |
| 19 | 2026-04-12 | [任务系统与自动化](./19-tasks-and-automation.md) |
| 20 | 2026-04-12 | [隐藏面——feature flag、彩蛋与对抗设计](./20-hidden-surface.md) |
