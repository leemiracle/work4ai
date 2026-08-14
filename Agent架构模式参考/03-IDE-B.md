# 03 · IDE-B 架构模式（VS Code Fork，全球专业开发者路线）

> 全球专业开发者的 AI 编码 IDE 形态——**工程深度最高**，独有创新最多。本文档已脱敏。

---

## 一、形态定位

- **形态**：VS Code Fork AI IDE（**高度模块化**——多独立 extension）
- **用户**：全球专业开发者
- **特点**：工程极致（进程分离 / Protobuf / CRDT / 自研 LSP）
- **架构取向**：架构驱动，重工程严谨性和性能

---

## 二、架构特点

- **基础**：VS Code Fork（Electron）
- **AI 集成方式**：**高度模块化**——多个独立 extension 各司其职（agent-exec / local-agent-runtime / retrieval / agent-host / mcp 等），不混在单一 bundle
- **协议层**：**Protobuf agent schema**（区别于全行业的 JSON）
- **进程模型**：**3+1 进程分离**（host / exec / worker / runtime）
- **状态管理**：Protobuf schema + AgentStore CRDT
- **代码理解**：tree-sitter + 多增强 + 自研 LSP（强制替换默认 LSP）
- **AI 模块化粒度**：多独立 extension（最大单模块是 agent-exec）

---

## 三、独有设计（该形态的 13 个创新，工程最深）

### ★★★★★ 3+1 进程 Agent 分离（host / exec / worker / runtime）

主编辑器进程不被 AI 影响——每个进程独立崩溃恢复。这是该形态最核心的架构创新。

**借鉴价值**：**主编辑器稳定性是 AI IDE 的命门**。AI crash 不应影响用户编辑。多进程分离是最佳实践。

### ★★★★★ Protobuf agent schema（vs 全行业 JSON）

binary 高效 + 强类型 + 跨语言。用 Protobuf 定义 agent 的所有通信（vs 其他产品用 JSON）。

**借鉴价值**：性能敏感的 agent 通信用 Protobuf 比 JSON 高效（序列化快/体积小/类型安全）。

### ★★★★★ AgentStore CRDT（多 agent 真并行同步）

多 agent 并行修改时的冲突解决——用 CRDT（无冲突复制数据类型）保证一致性。

**借鉴价值**：多 agent 真并行（不是串行 delegation）需要 CRDT 同步。

### ★★★★★ AI Attribution（代码归因）

所有 file edit 打 attribution 标——标记哪些代码是 AI 生成的。

**借鉴价值**：**合规关键**。企业部署必须能追溯代码来源（人写 vs AI 写）。

### ★★★★★ Shadow Workspace（虚拟工作区副本）

agent 改动先进副本（Shadow Workspace），用户审查后才合并到主文件。

**借鉴价值**：**用户审查前不污染主文件**。AI 改动可控可回滚。

### ★★★★ BugBot 独立 agent

专门找 bug 的独立 agent（schema 有 bugbot_response）——多 agent 专业分工。

### ★★★★ Computer Call（OS 级 Computer Use）

集成 OS 级 Computer Use（操控整个桌面，不只编辑器）。

### ★★★★ 本地 agent runtime（Privacy Mode）

独立进程做本地推理——数据不出本机（隐私模式）。

**借鉴价值**：隐私敏感场景（金融/医疗）必须支持本地推理。

### ★★★★ MCP SDK fork + patch（OAuth 重试增强）

不直接用 vanilla MCP SDK，fork 后加 OAuth 重试等增强。

**借鉴价值**：核心依赖的 SDK 不要直接用 vanilla——fork + patch 满足生产需求。

### ★★★★ 强制替换默认 LSP（自研语言服务）

强制替换微软默认 LSP（extensionReplacementMap）——自研 Python/C++/C# LSP 以深度集成 AI。

### ★★★ 登录态增强 RAG

用登录态（如 GitHub login）增强 RAG——检索用户私有/组织代码。

### ★★★ 独立索引忽略文件

独立的索引忽略文件（类似 .gitignore 但针对 AI 索引）。

### ★★★ 私有平台 API 扩展

fork VS Code 加自家 API proposal——需要修改底层平台。

---

## 四、反模式（该形态的教训）

- ❌ **闭源 walled garden**（大量私有 API）—— 第三方无法扩展
- ❌ **强制替换用户选择**（extensionReplacementMap 强制替换）—— 应给用户选择权
- ❌ **schema 超前于产品**（BugBot/Computer Call 在 schema 但 UI 不开放）—— schema 应跟产品同步

---

## 五、借鉴价值

做**严肃商业编码 Agent（出海/专业）**时，借鉴此形态的：
- **3+1 进程分离**（主编辑器稳定）
- **Protobuf agent schema**（高效通信）
- **AgentStore CRDT**（多 agent 并行）
- **AI Attribution**（合规归因）
- **Shadow Workspace**（改动可控）
- **本地 runtime**（隐私模式）
- **MCP SDK fork + patch**（生产级 SDK）

> 该形态是"工程极致"的典范——13 个独有创新里有多个需要大量工程（CRDT/自研 LSP/进程分离），但其架构模式（尤其进程分离 + Shadow Workspace + AI Attribution）值得所有编码 Agent 借鉴。

---

## 下一步
- 看 CLI/TUI 框架的函数式架构 → [`04-CLI-TUI框架.md`](./04-CLI-TUI框架.md)
- 看横向对比 → [`06-comparison.md`](./06-comparison.md)
