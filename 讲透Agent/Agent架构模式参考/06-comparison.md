# 06 · 横向对比矩阵

> 五形态架构维度 × 场景维度全景对比。所有列按形态代号，不含可识别产品细节。

---

## 一、架构维度对比

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|:---:|:---:|:---:|:---:|:---:|
| **形态** | IDE | 桌面 Agent | IDE | CLI/TUI/SDK | 网关 + 多端 |
| **基础** | VS Code Fork | Electron App | VS Code Fork | Native binary + Ink TUI | Node + 多端 native |
| **包结构** | VS Code + 单一 extension | Electron app | VS Code + 多独立 extension | 多 package monorepo | 多 package + 大量扩展 |
| **语言栈** | TypeScript (webpack) | TypeScript | TypeScript | TypeScript + 函数式（Effect 风格）| TypeScript |
| **运行时** | Node.js (Electron) | Node.js (Electron) | Node.js (Electron) | Bun | Node.js |
| **状态管理** | 平台自带 state | 自研 | **Protobuf schema** | 函数式 Service 组合 | EventStream + AsyncLocalStorage |
| **持久化** | 平台 workspace state | SQLite + 对象存储 | SQLite | SQLite（函数式 ORM）| SQLite + 向量库 |
| **CLI** | ✗ | ✗ | ✗ | Native binary | Node.js CLI |
| **TUI** | ✗ | ✗ | ✗ | Ink + TSX | ✗ |
| **Desktop** | ✅ Electron | ✅ Electron | ✅ Electron | ✅ Electron | ✅ 多平台 native |
| **Web UI** | ✗ | ✗ | ✗ | ✅ | ✅ Control UI |
| **多渠道** | ✗ | 少量 IM | ✗ | 仅 Slack | ✅ 多渠道（数十）|
| **协议层** | 平台 RPC | ACP (JSON ndjson) | Protobuf agent schema | 内嵌函数式 | Gateway Protocol + ACP |
| **进程模型** | 单进程 | daemon + main | **3+1 进程** | 单进程 | 单进程 |
| **AI 模块化粒度** | 单一大型 bundle | 多个 main bundles | **多独立 extension** | 多 packages | 多 package + 大量扩展 |

---

## 二、场景维度对比

| 场景 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|:---:|:---:|:---:|:---:|:---:|
| **IDE 内编码** | ★★★★★ | ★★ | ★★★★★ | ★★★ | ★ |
| **CLI 终端编码** | ✗ | ★★ | ✗ | ★★★★★ | ★★ |
| **个人桌面办公** | ★★ | ★★★★★ | ★★ | ★★ | ★★★ |
| **IM Bot 接入** | ✗ | ★★★ | ✗ | ★ | ★★★★★ |
| **企业内部部署** | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★ |
| **多用户协作** | ★★ | ★★★ | ★★ | ★★ | ★★★★★ |
| **定时/自动化** | ✗ | ★★★★★ | ✗ | ★★ | ★★★★ |
| **多 Agent 协作** | ★★ | ★★★★ | ★★★★ | ★★★ | ★★★★ |
| **可扩展生态** | ★★★ | ★★★★ | ★（封闭）| ★★★★ | ★★★★★ |
| **多模型支持** | ★★★★ | ★★★★ | ★★★★ | ★★★★★ | ★★★★★ |
| **专业开发者** | ★★★★ | ★★ | ★★★★★ | ★★★★★ | ★★ |
| **代码补全/NES** | ★★★★ | ★★ | ★★★★★ | ✗ | ✗ |
| **大型 codebase RAG** | ★★★ | ★★ | ★★★★★ | ★★★ | ✗ |
| **隐私本地推理** | ✗ | ✗ | ★★★★ | ✗ | ✗ |

---

## 三、技术栈对比

| 层 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|---|---|---|---|---|
| **主语言** | TypeScript (webpack) | TypeScript | TypeScript | TypeScript + 函数式 | TypeScript |
| **运行时** | Node.js (Electron) | Node.js (Electron) | Node.js (Electron) | Bun | Node.js |
| **包管理** | npm + 平台工具链 | npm | npm | bun + turbo | pnpm workspace |
| **构建** | webpack + gulp | webpack | webpack | 脚本化构建 | 现代工具链（tsgo/oxfmt/oxlint）|
| **UI 渲染** | Electron + Chromium | Electron + Chromium | Electron + Chromium | Ink (TUI) + web/desktop | Node CLI + native apps + Web UI |
| **状态管理** | 自研（多 Service/Manager）| 自研 | **Protobuf agent schema** | **函数式（Effect 风格）** | EventStream + AsyncLocalStorage |
| **代码理解** | tree-sitter（多语言）| tree-sitter | tree-sitter + 多增强 | LSP + grep/glob | tree-sitter |
| **多 LLM 抽象** | 单一后端 + MCP | 多模型支持 | 多 provider | 多 provider 包 | 多 provider 扩展 |
| **HTTP/RPC** | 平台 RPC | ACP | Protobuf + ndjson | server (Hono) + 函数式 | Gateway protocol + ACP |
| **远程开发** | 有 | ✗ | 有 | ✗ | ✗ |

---

## 四、Agent Loop 对比

| 机制 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|:---:|:---:|:---:|:---:|:---:|
| **双层循环（outer follow-up + inner tool）** | ✗ | ✗ | ✗ | ✗ | ✅ |
| **Tool Loop 死循环检测/恢复** | 不明 | 不明 | 不明 | 单独 max-steps 模块 | ✅ |
| **Turn 标记（tainted/interrupted）** | 不明 | 不明 | 不明 | 单独 context-epoch | ✅ |
| **Steering messages（运行时插入）** | 不明 | 不明 | 不明 | ✗ | ✅ |
| **模型动态切换（next turn）** | ✅ | ✗（多模型可选）| ✗（config-time）| ✅ prepareNextTurn | ✗ |
| **AbortSignal 持久化** | ✗ | ✗ | ✗ | ✗ | ✅ reason 持久化 |
| **AsyncLocalStorage 注入 tool context** | 不明 | 不明 | 不明 | ✗ | ✅ |
| **EventStream（first-class）** | ✗ | ✗ | ✗ | 函数式流 | ✅ |
| **Durable session（resume）** | 部分 | ✗（云端 7×24）| ✗ | ✗ | ✗ |
| **Crash-safe tool settlement** | 部分（Message Queue Recovery）| ✗ | ✗ | ✅ | ✗ |
| **User Declined ≠ Tool Output** | 不明 | 不明 | 不明 | ✅ | ✗ |
| **Turn Transition 类型化** | 不明 | 不明 | 不明 | ✅ | ✗ |
| **AgentStore CRDT（多 agent 同步）** | ✗ | ✗ | ✅ | ✗ | ✗ |
| **Skill 自动闭环** | ✗ | ✅ | ✗ | ✗ | ✗ |
| **present_files 强制交付** | ✗ | ✅ | ✗ | ✗ | ✗ |

> ✅ 在"独有创新"列 = 该形态有此机制；✗ = 没有；不明 = 闭源部分无法确认。

---

## 五、工具协议对比（MCP / Skills / Plugins）

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|---|---|---|---|---|
| **MCP 支持** | ✅ connector + market | ✅ mcp-app-preload | ✅ MCP 模块（+ fork patch）| ✅ 完整 lifecycle/oauth/session-recovery | ✅ Gateway 协议层 |
| **MCP 双向** | ✅ sampling | ✅ | ✗ | ✗ | ✗ |
| **Skills** | rules 管理 | 大量预置专家 + Skills | AgentSkill schema | ✅ skill 包 | ✅ active-memory 扩展 |
| **Skill 体系** | 多 Rule 管理器 | 三级渐进披露 + 自动闭环 | AgentSkillMetadata | 用户级 + 项目级 | memory-core |
| **Plugin 机制** | 平台 extension 标准 | Plugin 三件套 | 多独立 extension + patches | plugin 包 | 大量 extensions + plugin-package-contract |
| **Sub-agent / 委派** | agentProcessPool | ✅（多 Agent 并行）| AgentHostSubagentStarted | ✅ subagent-permissions + task tool | ✅ ACP + acpx |
| **工具白名单/权限** | 平台权限 | 本地文件授权边界 | AgentStore Claim | permission 包 | gateway-protocol approvals |

---

## 六、上下文 / 记忆 / 持久化

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|---|---|---|---|---|
| **上下文压缩** | PlanService（推断）| microcompact | retrieval 模块 | session/compaction + context-epoch | tool-call-repair |
| **记忆系统** | chatHistory | chatHistory | AiAttribution | 本地 memory 目录 | 多 memory engine |
| **记忆层数** | working_memory | 多段（多 Memory + Working + User）| 单段 + attribution | 多层（global + project）| 多 engine（embeddings/baseline/qmd/storage）|
| **会话存储** | 平台 workspace state | 推断 + 云端 | SQLite | 函数式 ORM sqlite | session-url-contract + workboard-contract |
| **可分享** | ✗ | ✅（项目空间沉淀）| ✗ | share 包 | session-url-contract（URL 分享会话）|
| **快照/回滚** | checkpointService | ✗ | ✗ | snapshot + revert | session-lineage-meta（血统追踪）|
| **代码归因** | ✗ | ✗ | **AiAttribution** | ✗ | ✗ |
| **Shadow Workspace** | ✗ | ✗ | ✅ | ✗ | ✗ |

---

## 七、可扩展性 / 部署

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|---|---|---|---|---|
| **桌面客户端** | Linux/Mac/Windows | macOS arm64 | Linux/Mac/Windows | desktop 包 | 多平台（含移动）|
| **CLI** | ✗ | ✗ | ✗ | ✅（主入口）| ✅（主入口）|
| **TUI** | ✗ | ✗ | ✗ | ✅ Ink/TSX | ✗ |
| **Web UI** | ✗ | ✗ | ✗ | web + session-ui 包 | Control UI（web）|
| **Server/daemon** | ✗ | ✅（云端 7×24）| ✗ | server 包（Hono）| ✅ Gateway daemon |
| **SDK** | ✗ | ✗ | ✗ | sdk + sdk-next 包 | sdk 包 |
| **企业版** | ✗ | ✅ Enterprise（私有化）| ✗ | enterprise + identity + control-plane | 自托管即可 |
| **IM 集成** | ✗ | ✅（多 IM 平台）| ✗ | ✅ Slack 包 | ✅ extension |
| **HTTP API codegen** | ✗ | ✗ | ✗ | ✅ httpapi-codegen + http-recorder（**独有**）| ✗ |
| **本地推理** | ✗ | ✗ | ✅ 本地 agent runtime | ✗ | ✗ |
| **远程开发** | 有 | ✗ | 有 | ✗ | ✗ |
| **BugBot** | ✗ | ✗ | ✅（schema 有 bugbot_response）| ✗ | ✗ |
| **Computer Use** | browserCdpClient | ✗ | ✅ computer_call | ✗ | ✅ cua-computer |

---

## 八、定位与生态策略（不含商业敏感信息）

| 维度 | IDE-A | 桌面 Agent | IDE-B | CLI/TUI 框架 | 多渠道网关 |
|---|---|---|---|---|---|
| **闭源/开源** | 闭源 | 闭源 | 闭源 | 开源 | 开源 |
| **底座模型** | 自有 + 多模型 | 多模型支持 | 自有 + 主流大模型 | 任意（多 provider）| 任意（多 provider 扩展）|
| **生态策略** | 半开放（MCP market）| SkillHub + 专家 + 企业沉淀 | 封闭 walled garden | skills + plugins + MCP + SDK | extensions + channels + companion apps |
| **目标用户** | 企业/区域开发者 | 非技术职场人 | 全球专业开发者 | 极客开发者 | 任意个人 |

> 商业模式具体定价、厂商归属、同源/对标关系等商业敏感信息已脱敏。

---

## 九、关键洞察

### 1. 这五类根本不是一个赛道
- IDE-A / IDE-B = **VS Code Fork AI IDE**（编码助手）
- 桌面 Agent = **桌面办公 Agent**（对标通用办公 Agent 范式）
- CLI/TUI 框架 = **开发者 CLI/TUI 框架**
- 多渠道网关 = **个人 AI 助手 + 多渠道网关**

### 2. 闭源商业 vs 开源基础设施
- 闭源商业（IDE-A/桌面 Agent/IDE-B）：**场景驱动**，重视用户体验和合规
- 开源基础设施（CLI/TUI 框架/多渠道网关）：**架构驱动**，重视工程严谨性和可扩展性

### 3. 工程深度排序
1. **IDE-B**（3 进程分离 + Protobuf + CRDT + 自研 LSP）—— 工程最深
2. **多渠道网关**（双层循环 + Tool Loop Recovery + 多渠道抽象）—— 工程最严谨
3. **CLI/TUI 框架**（函数式多 Service 组合）—— 函数式最纯粹
4. **桌面 Agent**（三模式 + Skill 闭环 + 守护进程）—— 产品最完整
5. **IDE-A**（大量 feature 开关 + Variables + Multi-Agent 路由）—— 企业/区域市场最适配

---

## 下一步
- 看独有创新对决矩阵 → [`07-innovations.md`](./07-innovations.md)
- 看架构选型决策 → [`08-blueprint.md`](./08-blueprint.md)
