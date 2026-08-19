---
card_id: mcp-ecosystem-03-official-org-sdk
title: 官方仓与 SDK 格局——modelcontextprotocol org 深读（spec 瘦身、Registry 诞生、SDK v2、FastMCP 独立）
universe: 讲透Agent/Agent框架案例/MCP协议生态全景
burke:
  场景: 要选 SDK/找参考 server/发布自己 server 的开发者
  主体: modelcontextprotocol 官方 org（42 公开仓）+ 大厂官方 server（github/microsoft/ChromeDevTools）+ FastMCP 社区分支
  能动: 官方 steering group + 各 SDK 维护团队
  行动: spec 仓只留规范；servers 仓从"生态目录"瘦身为 7 个 reference server；列表职能移交官方 Registry；SDK v2 全面重写对齐 2026-07-28
  目的: 官方只管"协议与样板"，生态目录/分发交给 Registry——治理上的关注点分离
  张力: 中心化治理 vs 6.4 万仓的长尾生态；官方参考实现 vs 社区事实标准（FastMCP）
  弧线: 2024 官方大包大揽（servers 仓=目录）→ 2026 官方退守协议本身，Registry+SDK v2 承接生态
status: 已完成（star 数为 2026-08-19 websearch+官方页快照，动态数字）
refs:
  - https://github.com/modelcontextprotocol（org，42 公开仓）
  - https://github.com/modelcontextprotocol/servers（README 明示职能移交 Registry）
  - https://registry.modelcontextprotocol.io（官方 Registry）
  - https://github.com/PrefectHQ/fastmcp（FastMCP 独立版）
  - https://github.com/github/github-mcp-server（大厂官方 server 样板）
updated: 2026-08-19
---

# 官方仓与 SDK 格局

> 一句话：**官方 org 自己在做减法——servers 仓从"万物目录"瘦身为 7 个 reference server，生态目录职能移交给官方 Registry；SDK 全线 v2 重写对齐 2026-07-28 无状态规范；而 Python 侧的事实标准其实是社区独立版 FastMCP（宣称驱动 70% server）。**

## 1. 官方 org 核心仓（42 公开仓中的六支柱）

| 仓 | star | 语言 | 职能 |
|---|---|---|---|
| `modelcontextprotocol/servers` | ~89.6k | TypeScript | **只剩 7 个 reference server**：Everything（测试）/ Fetch / Filesystem / Git / Memory（知识图谱）/ Sequential Thinking / Time。GitHub/Slack/SQLite 等已 archived 或移交 |
| `modelcontextprotocol/python-sdk` | ~24.0k | Python | v2 = 当前稳定版，**大重构**支持 2026-07-28 spec（及所有旧版）；v1.x 只保 bug/security fix；内置旧版 FastMCP 1.x 兼容层 |
| `modelcontextprotocol/typescript-sdk` | ~13.2k | TypeScript | v2 拆包：`@modelcontextprotocol/server` + `@modelcontextprotocol/client`，外加薄 middleware 包（express/fastify/hono/node）；限制新贡献者 PR 频率 |
| `modelcontextprotocol/inspector` | ~10.4k | TypeScript | 官方可视化调试 UI——发版前必过（手册已收录） |
| `modelcontextprotocol/modelcontextprotocol` | ~9.0k | TypeScript | spec repo：规范 + JSON schema + 官方文档源（Mintlify） |
| `modelcontextprotocol/registry` | ~7.1k | Go | **官方社区 Registry 服务**——servers 仓 README 明示"找 server 请去 Registry" |

其余 ~36 仓为各语言 SDK：**Go / Kotlin / Rust / Swift / Java / C#** 等（servers 仓 README 给出全链接）。org followers ~49k。

## 2. 治理转向：从"大包大揽"到"协议+样板"（直觉层）

2024 年 servers 仓曾同时扮演三个角色：**参考实现 + 生态目录 + 质量背书**。6.4 万仓的生态规模下这三个角色互相拖累（目录维护不过来、背书责任无限）。2026 年的拆分：

```
规范      → modelcontextprotocol（spec repo，SEP 流程）
样板      → servers 仓 7 个 reference server（示范"官方认为该怎么写"）
目录/分发 → Registry（registry.modelcontextprotocol.io + GitHub 内置入口 github.com/mcp）
SDK       → 按语言独立仓，v2 对齐新规范
```

**GitHub 平台级集成**：GitHub 站点导航已把 "MCP Registry — Integrate external tools (github.com/mcp)" 作为一级入口——注册中心长进了代码托管平台本身。

## 3. SDK v2 要点（写 server 前必读）

- **Python SDK v2**：为 2026-07-28 spec 完全重写（修长期架构债），同时兼容所有旧版本规范；官方文档站 py.sdk.modelcontextprotocol.io 提供 migration guide。从 v1 迁移会有 breaking changes
- **TS SDK v2**：包名从 `@modelcontextprotocol/sdk` 拆为 server/client 两包；跑在 Node/Bun/Deno；middleware 包刻意做薄（只做接线，不掺业务逻辑）
- **选型建议**（对齐 [`MCP工程手册`](../../../../工程化手册库/MCP工程手册/README.md) §5 工具栈表）：官方 SDK 适合"贴规范"的实现；要快速开发、客户端、交互 UI，看 FastMCP（下节）

## 4. FastMCP：社区反哺再独立（生态层最有意思的故事）

- **时间线**：FastMCP 1.0（社区作品，装饰器风格）→ 2024 被**并入官方 Python SDK**（`mcp.server.fastmcp`）→ 原作者继续维护独立版 PrefectHQ/fastmcp（现 ~27.2k★，超过官方 python-sdk）→ 宣称日下载百万次、**"某种版本的 FastMCP 驱动跨语言 70% 的 MCP servers"**
- **独立版新增**：Servers（工具/资源/提示词）/ **Apps（工具内交互 UI，渲染进对话流）** / Clients（连任意 server，本地或远程）
- **商业化**：Prefect Horizon = 企业 MCP gateway（SSO、tool 级 RBAC、审计、私有 registry、branch previews）
- **判读**：官方 SDK 是"协议参考"，FastMCP 是"应用框架"——类比 stdlib vs FastAPI 的关系。手册 §7 的 FastMCP 代码在两者间基本通用，但生产选型要明确用哪个

## 5. 大厂官方 server 样板（topics/mcp 顶部的"官方系"）

| 仓 | star | 看点 |
|---|---|---|
| `ChromeDevTools/chrome-devtools-mcp` | ~49.4k | Chrome 官方：DevTools 协议直接喂 agent（性能/网络/DOM 检查） |
| `microsoft/playwright-mcp` | ~36.3k | 微软官方：浏览器自动化的"无障碍树优先"设计（不靠截图，喂结构树省 token） |
| `github/github-mcp-server` | ~32.3k | **toolsets 设计样板**：20+ 工具族（context/actions/issues/pull_requests/code_security...）按需开关，只暴露用得着的；remote hosted 优先，本地 Docker 兜底 |
| `bytedance/UI-TARS-desktop` | ~38.6k | 字节：GUI agent 栈把 MCP 作为工具面 |

**可迁移的设计**：github-mcp-server 的 toolset 开关 = 对"工具面爆炸"（见本案例 [01-生态统计](01-生态统计与赛道地图.md) 赛道六）的正解之一；与本项目 codegraph 案例"默认只暴露 1 个强工具"（[`codegraph代码知识图谱`](../../../Agent上下文案例/codegraph代码知识图谱/README.md)）同一谱系：**工具面越小越准，扩展靠显式开启**。

## 6. 教学映射

- 动手写第一个 server：[`MCP工程手册`](../../../../工程化手册库/MCP工程手册/README.md) §7（FastMCP 代码可直接跑）
- 深入 spec 生命周期与 MRTR：[02-协议演进2026-07-28](02-协议演进2026-07-28.md)
- 生态全量统计与赛道：[01-生态统计与赛道地图](01-生态统计与赛道地图.md)

**✍️ 练习**：用 Registry（registry.modelcontextprotocol.io）搜索 "filesystem"，对比官方 reference server 与社区同名 server 的差异（工具数/鉴权/传输），用手册 §4 的 6 维度给两者打分。

---

*star 数为 2026-08-19 快照（websearch + GitHub 页面），会漂移；引用时注明日期。*
