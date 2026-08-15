# 07 · 创新对决矩阵

> 五形态独有创新点完整对照（其他四类没有的）。本表只列**公开的工程概念**，所有"出处"按形态归类。

---

## 一、独有创新数排行

| 形态 | 独有创新数 | 最有价值的三项 |
|---|:---:|---|
| **IDE-B** | **13 个** | 3 进程分离 / Protobuf agent schema / AgentStore CRDT |
| **多渠道网关** | **8 个** | 多渠道统一抽象 / Agent Loop 双层循环 / Tool Loop Recovery |
| **IDE-A** | **8 个** | Multi-Agent × Multi-Model 路由 / Variables @ 触发 / 大量 feature 开关 |
| **桌面 Agent** | **6 个** | 三模式 Craft/Plan/Ask / Skill 自动闭环 / present_files 强制交付 |
| **CLI/TUI 框架** | **5 个** | 函数式 Service 组合 / Crash-safe tool settlement / Native binary CLI |

---

## 二、完整创新对决矩阵

| 创新点 | IDE-A | IDE-B | CLI/TUI 框架 | 多渠道网关 | 桌面 Agent |
|---|:---:|:---:|:---:|:---:|:---:|
| **3+1 进程 Agent 分离**（host/exec/worker/runtime）| — | ✅ | — | — | — |
| **Protobuf agent schema**（binary 强类型协议）| — | ✅ | — | — | — |
| **AgentStore CRDT 冲突解决** | — | ✅ | — | — | — |
| **AI Attribution**（代码归因标记）| — | ✅ | — | — | — |
| **Shadow Workspace**（虚拟工作区副本）| — | ✅ | — | — | — |
| **BugBot 独立 agent** | — | ✅ | — | — | — |
| **Computer Call**（OS 级 Computer Use）| — | ✅ | — | — | — |
| **本地 agent runtime**（独立推理进程）| — | ✅ | — | — | — |
| **MCP SDK fork + OAuth 增强** | — | ✅ | — | — | — |
| **强制替换默认 LSP**（自研语言服务）| — | ✅ | — | — | — |
| **登录态增强 RAG** | — | ✅ | — | — | — |
| **独立索引忽略文件** | — | ✅ | — | — | — |
| **私有平台 API 扩展** | 部分 | ✅ | — | — | — |
| **多渠道统一抽象**（IM 统一接口）| — | — | — | ✅ | — |
| **Agent Loop 双层循环** | — | — | — | ✅ | — |
| **Tool Loop Recovery**（死循环检测终止）| — | — | — | ✅ | — |
| **Turn Tainting** | — | — | — | ✅ | — |
| **AsyncLocalStorage 工具上下文** | — | — | — | ✅ | — |
| **多 memory engine 分离** | — | — | — | ✅ | — |
| **Frame Guards + Secret Ref** | — | — | — | ✅ | — |
| **Thread Ownership + Policy** | — | — | — | ✅ | — |
| **Idle reaper + eviction**（长跑防泄漏）| — | — | — | ✅ | — |
| **函数式 Service 组合**（依赖注入）| — | — | ✅ | — | — |
| **Crash-safe tool settlement** | — | — | ✅ | — | — |
| **Turn Transition 类型化** | — | — | ✅ | — | — |
| **User Declined ≠ Tool Output** | — | — | ✅ | — | — |
| **MAX_STEPS 硬约束** | — | — | ✅ | — | — |
| **Native binary CLI** | — | — | ✅ | — | — |
| **HTTP API Codegen + Recorder** | — | — | ✅ | — | — |
| **Multi-Agent × Multi-Model 路由** | ✅ | — | — | — | 部分 |
| **自有协议层**（多内部服务）| ✅ | — | — | — | — |
| **Variables @ 触发系统** | ✅ | — | — | — | — |
| **大量 feature 开关**（同代码多形态）| ✅ | 部分 | — | — | 部分 |
| **Slash Command 系统** | ✅ | ✅ | — | — | — |
| **光标位置预取**（零延迟预测）| ✅ | ✅ | — | — | — |
| **fileDiffHistory + checkpoint** | ✅ | — | — | — | — |
| **Message Queue Recovery** | ✅ | — | ✅ | — | — |
| **agentProcessPool 多进程** | ✅ | ✅ | — | — | — |
| **Rule 系统**（多管理器）| ✅ | — | — | — | — |
| **ACP 双向 RPC**（agent-UI 解耦）| — | — | — | ✅ | ✅ |
| **三模式 Craft/Plan/Ask** | 部分 | — | — | — | ✅ |
| **Skill 自动闭环** | — | — | — | — | ✅ |
| **Plugin 三件套统一格式** | — | — | — | — | ✅ |
| **三层 Memory 注入** | — | — | — | — | ✅ |
| **Automations SQLite 多表** | — | — | — | — | ✅ |
| **present_files 强制交付** | — | — | — | — | ✅ |

---

## 三、按"借鉴价值"分类

### 🥇 核心架构级（影响整体设计）

| 创新 | 出处形态 | 借鉴价值 |
|---|---|---|
| **3+1 进程 Agent 分离** | IDE-B | 主编辑器不被 AI 影响，每进程独立崩溃恢复 |
| **Protobuf agent schema** | IDE-B | binary 高效 + 强类型 + 跨语言 |
| **AgentStore CRDT** | IDE-B | 多 agent 真并行的根基 |
| **函数式 Service 组合** | CLI/TUI 框架 | 依赖注入，任何 Service 可替换 |
| **Agent Loop 双层循环** | 多渠道网关 | 处理"用户边说边改" |
| **ACP 双向 RPC** | 多渠道网关/桌面 Agent | agent 与 UI 进程解耦 |

### 🥈 机制设计级（影响具体模块）

| 创新 | 出处形态 | 借鉴价值 |
|---|---|---|
| **Crash-safe tool settlement** | CLI/TUI 框架 | 先持久化再执行，crash 可恢复 |
| **Tool Loop Recovery** | 多渠道网关 | 检测死循环并终止 |
| **AI Attribution** | IDE-B | 行业首创，合规关键 |
| **Shadow Workspace** | IDE-B | 用户审查前不污染主文件 |
| **AsyncLocalStorage 工具上下文** | 多渠道网关 | 工具内反向追溯调用者 |
| **Turn Transition 类型化** | CLI/TUI 框架 | 调试和审计 |
| **User Declined ≠ Tool Output** | CLI/TUI 框架 | 防 LLM 绕过权限 |
| **MAX_STEPS 硬约束** | CLI/TUI 框架 | 简单防死循环 |
| **Idle reaper + eviction** | 多渠道网关 | 长跑服务防泄漏 |

### 🥉 场景适配级（影响用户体验）

| 创新 | 出处形态 | 借鉴价值 |
|---|---|---|
| **三模式 Craft/Plan/Ask** | 桌面 Agent | 用户可控 agent 自主度 |
| **Skill 自动闭环** | 桌面 Agent | skill 自进化，不延迟到下次 |
| **present_files 强制交付** | 桌面 Agent | 完成任务必交付物 |
| **Variables @ 触发系统** | IDE-A | UI 级 context 注入 |
| **Multi-Agent × Multi-Model 路由** | IDE-A | 不同任务用不同模型 |
| **大量 feature 开关** | IDE-A | 同代码多形态（SaaS/企业/私有化）|
| **光标位置预取** | IDE-A/IDE-B | 零延迟预测 |
| **fileDiffHistory + checkpoint** | IDE-A | Agent 自有版本（不依赖 git）|
| **多渠道统一抽象** | 多渠道网关 | 异构 IM 统一接口 |

---

## 四、按"实现难度"分类

### 极难复刻（需要 fork 平台）
- **私有平台 API 扩展**（IDE-B）—— 必须 fork 底层平台加自家 API
- **强制替换默认 LSP**（IDE-B）—— 必须自研各语言 LSP
- **3+1 进程 Agent 分离**（IDE-B）—— 需要多 extension host 支持

### 中等难度（需要大量工程）
- **AgentStore CRDT**（IDE-B）—— 需要分布式算法
- **多渠道统一抽象**（多渠道网关）—— 每渠道都要适配
- **函数式 Service 组合**（CLI/TUI 框架）—— 团队需要熟练函数式编程
- **Protobuf agent schema**（IDE-B）—— 需要完整 schema 设计

### 容易复刻（一两天可实现）
- **三模式 Craft/Plan/Ask**（桌面 Agent）—— reminder + prompt 模板
- **Skill 自动闭环**（桌面 Agent）—— prompt 段 + skill 管理工具
- **MAX_STEPS 硬约束**（CLI/TUI 框架）—— 十几行 prompt 注入
- **present_files 强制交付**（桌面 Agent）—— prompt 段 + 一个工具
- **User Declined ≠ Tool Output**（CLI/TUI 框架）—— 错误类型判断
- **Turn Transition 类型化**（CLI/TUI 框架）—— union type 定义
- **Idle reaper + eviction**（多渠道网关）—— 简单 LRU + TTL
- **Variables @ 触发系统**（IDE-A）—— UI parser + resolver
- **独立索引忽略文件**（IDE-B）—— 多一种 ignore 文件

---

## 五、按"独占性"分类（只有一类形态有）

### 仅 IDE-B 有（13 个）
3+1 进程分离 / Protobuf schema / AgentStore CRDT / AI Attribution / Shadow Workspace / BugBot / Computer Call / 本地 agent runtime / MCP SDK fork / 强制替换 LSP / 登录增强 RAG / 独立索引忽略文件 / 私有平台 API 扩展

### 仅 多渠道网关 有（8 个）
多渠道统一抽象 / Agent Loop 双层循环 / Tool Loop Recovery / Turn Tainting / AsyncLocalStorage 工具上下文 / 多 memory engine / Frame Guards + Secret Ref / Thread Ownership + Policy

### 仅 IDE-A 有（独占 + 共享）
Multi-Agent × Multi-Model 路由 / 自有协议层 / Variables @ 触发 / 大量 feature 开关 / Rule 系统 + fileDiffHistory（独占）+ 光标位置预取（与 IDE-B 共享）+ agentProcessPool（与 IDE-B 共享）

### 仅 桌面 Agent 有（6 个）
三模式 Craft/Plan/Ask（部分 IDE-A 有）/ Skill 自动闭环 / Plugin 三件套 / 三层 Memory 注入 / Automations SQLite 多表 / present_files 强制交付

### 仅 CLI/TUI 框架 有（5 个）
函数式 Service 组合 / Crash-safe tool settlement / Turn Transition 类型化 / User Declined ≠ Tool Output / HTTP API Codegen

---

## 六、最值得"组合借鉴"的创新套餐

### 套餐 A：严肃商业编码 Agent（出海）
**以 IDE-B 为骨架 + IDE-A 周边 + 多渠道网关防御**
- 核心：3 进程分离（IDE-B）+ Protobuf schema（IDE-B）+ Shadow Workspace（IDE-B）
- 协作：AgentStore CRDT（IDE-B）+ Multi-Agent × Multi-Model（IDE-A）
- 安全：AI Attribution（IDE-B）+ Frame Guards（多渠道网关）
- 防御：Tool Loop Recovery（多渠道网关）+ User Declined ≠ Tool Output（CLI/TUI 框架）

### 套餐 B：企业市场办公 Agent
**以 桌面 Agent 为骨架 + IDE-A 周边 + IDE-B 安全**
- 核心：三模式（桌面 Agent）+ Plugin 三件套（桌面 Agent）
- 闭环：Skill 自动闭环（桌面 Agent）+ present_files 强制交付（桌面 Agent）
- 用户：Variables @（IDE-A）+ Multi-Model 路由（IDE-A）
- 安全：AI Attribution（IDE-B）+ Shadow Workspace（IDE-B）
- 企业：大量 feature 开关（IDE-A）

### 套餐 C：开发者 CLI/TUI 工具
**以 CLI/TUI 框架 为骨架 + 多渠道网关防御**
- 核心：函数式 Service 组合 + Native binary CLI
- 稳健：Crash-safe tool settlement + MAX_STEPS
- 防御：Tool Loop Recovery + Turn Tainting

### 套餐 D：多渠道 IM Bot
**直接借鉴 多渠道网关**
- 核心：多渠道抽象 + Gateway Protocol + Frame Guards
- agent：Agent Loop 双层循环 + AsyncLocalStorage 工具上下文
- 治理：Thread Ownership + Policy
- 记忆：多 memory engine 分离

---

## 下一步
- 看具体借鉴清单和决策树 → [`08-blueprint.md`](./08-blueprint.md)
- 看具体形态细节 → [`01-05`](./)
