# 08 · 架构选型 + 借鉴清单 + 决策树

> 综合五形态，给出做 Agent 时的实战指南。所有"出处"按形态归类，不指向具体产品。

---

## 一、架构选型决策树

```
你要做什么？
│
├─ 1. AI 编码 IDE（VS Code Fork 路线）
│   │
│   ├─ 企业 / 区域市场 / 合规优先？
│   │   └─ 以 IDE-A 为骨架（Multi-Agent × Multi-Model + Variables @ + 大量 feature 开关）
│   │       + 借鉴 IDE-B（AI Attribution + Shadow Workspace）
│   │       + 借鉴 多渠道网关（Tool Loop Recovery）
│   │
│   ├─ 全球专业开发者 / 工程极致？
│   │   └─ 以 IDE-B 为骨架（3 进程分离 + Protobuf + AgentStore CRDT +
│   │       Shadow Workspace + AI Attribution + 自研 LSP）
│   │       + 借鉴 IDE-A（Variables @ + 大量 feature 开关）
│   │       + 借鉴 多渠道网关（Tool Loop Recovery）
│   │
│   └─ 想要简单？
│       └─ 用轻量编辑器扩展模式（不在本分析，更轻量）
│
├─ 2. 个人 / 团队桌面办公 Agent（桌面 Agent 路线）
│   └─ 以 桌面 Agent 为骨架（三模式 + Plugin 三件套 + Skill 闭环 + Automations）
│       + 借鉴 IDE-B（AI Attribution + Shadow Workspace）
│       + 借鉴 IDE-A（Variables @ + 大量 feature 开关）
│
├─ 3. 开发者 CLI/TUI/SDK 工具
│   └─ 以 CLI/TUI 框架 为骨架（函数式 Service + Native binary CLI）
│       + 借鉴 多渠道网关（Tool Loop Recovery + Turn Tainting）
│
└─ 4. 多渠道 IM Bot / 个人 AI 网关
    └─ 以 多渠道网关 为骨架（多渠道抽象 + Gateway Protocol）
        + 借鉴 桌面 Agent（Automations SQLite 多表）
```

---

## 二、做 Agent 时核心架构 Checklist

按"必做 / 按需 / 选做"分类。

### 核心架构（**必做**）

- [ ] **分层**：明确分 7-9 层（入口 / 协调 / 运行时 / 模板 / 扩展 / 工具 / 持久化）
- [ ] **协议边界**：定义 agent 与 UI 的 RPC 方法表（参考 ACP 双向 RPC 或 Protobuf agent schema）
- [ ] **Agent Loop**：7 步循环（分析 → 思考 → 选工具 → 执行 → 观察 → 迭代 → 交付）
- [ ] **强制交付**：每个任务必须有显式收尾（present_files 风格）
- [ ] **进程边界**：agent 进程与 UI 解耦（IDE-B 的 3 进程分离是最佳实践）

### 场景适配（**按需**）

- [ ] **三模式**（Craft/Plan/Ask）：如果用户群分新手/进阶，做模式切换（桌面 Agent）
- [ ] **Plugin 三件套**：如果要生态，统一 Expert/Skill/Connector 格式（桌面 Agent）
- [ ] **Skill 闭环**：如果要自进化，加 Accumulation/Reflection/Correction（桌面 Agent）
- [ ] **Automations**：如果要做工作流，用 SQLite 多表 + rrule + daemon（桌面 Agent）
- [ ] **多渠道接入**：如果要做 IM bot，参考多渠道网关的 channel bridges
- [ ] **多 Agent 协作**：如果做 Team 型，必须有 SOP 编排而非自由 delegation（桌面 Agent/IDE-A）
- [ ] **Multi-Agent × Multi-Model 路由**：补全用小模型，主推理用大模型（IDE-A）

### 安全与稳健（**必做**）

- [ ] **文件安全**：明确 personal_files 的安全规则（桌面 Agent 的多规则是范本）
- [ ] **命令安全**：危险命令拦截规则
- [ ] **Skill 安装审计**：security-check 分级（P0/P1/P2）
- [ ] **沙箱执行**：本地沙箱 + 云端沙箱双层
- [ ] **Hook 系统**：UserPromptSubmit / PreToolUse / PostToolUse 拦截点
- [ ] **AI Attribution**：所有 file edit 打 attribution 标（IDE-B）
- [ ] **Shadow Workspace**：agent 改动先进副本（IDE-B）
- [ ] **Frame Guards**：协议层防注入 / 防越权（多渠道网关）
- [ ] **Secret Ref**：secret 用 ref 引用不直接传（多渠道网关）

### Agent Loop 工程（**强烈推荐**）

- [ ] **双层循环**：outer 处理 follow-up，inner 处理 tool/steering（多渠道网关）
- [ ] **Tool Loop Recovery**：检测死循环并终止（多渠道网关）
- [ ] **Turn Tainting**：被中断的 turn 标记，防 LLM 误用（多渠道网关）
- [ ] **AsyncLocalStorage 工具上下文**：工具内反向追溯调用者（多渠道网关）
- [ ] **Crash-safe tool settlement**：先持久化再执行（CLI/TUI 框架）
- [ ] **MAX_STEPS 硬约束**：十几行简单防死循环（CLI/TUI 框架）
- [ ] **User Declined ≠ Tool Output**：用户拒绝直接 halt（CLI/TUI 框架）
- [ ] **Turn Transition 类型化**：把 turn 转换做成 union type（CLI/TUI 框架）
- [ ] **Idle reaper + eviction**：长跑服务防泄漏（多渠道网关）

### 工程化（**必做**）

- [ ] **模板引擎 prompt**：不要硬编码 prompt，用 Nunjucks 等模板（桌面 Agent）
- [ ] **多层记忆**：至少分全局/项目/任务三层（桌面 Agent 多段注入）
- [ ] **OpenTelemetry**：从 day 1 就接入追踪（桌面 Agent）
- [ ] **错误类型联合**：参考 CLI/TUI 框架的 RunError 联合类型
- [ ] **Native binary CLI**：CLI 工具用 native 分发（CLI/TUI 框架）
- [ ] **HTTP API Codegen**：如果做 API 集成（CLI/TUI 框架）

### 可选高级（**选做**）

- [ ] **Protobuf 通信**：替代 JSON，binary 高效（IDE-B）
- [ ] **AgentStore CRDT**：多 agent 真并行（IDE-B）
- [ ] **BugBot 独立 agent**：多 agent 专业分工（IDE-B）
- [ ] **Computer Call**：集成 OS 级 Computer Use（IDE-B）
- [ ] **本地推理独立 extension**：Privacy Mode（IDE-B）
- [ ] **登录态增强 RAG**：公开代码补强（IDE-B）
- [ ] **多 memory engine**：按职责分离（多渠道网关）
- [ ] **多渠道统一抽象**：异构 IM 接入（多渠道网关）

---

## 三、按场景的借鉴组合

### 场景 A：严肃商业编码 Agent（出海）

**必做（核心架构）**——以 IDE-B 为骨架：
1. 3+1 进程 Agent 分离（主编辑器不被 AI 影响）
2. Protobuf agent schema（binary 高效通信）
3. Shadow Workspace（agent 改动先进副本）
4. AI Attribution（代码归因，合规关键）
5. AgentStore CRDT（多 agent 并行同步）

**强烈推荐（用户/产品）**——借鉴 IDE-A：
6. Variables @ 触发系统（UI 级 context 注入）
7. Multi-Agent × Multi-Model 路由（不同任务用不同模型）
8. 大量 productFeatures 开关（一份代码多形态）
9. 光标位置预取（零延迟预测）
10. fileDiffHistory + checkpoint（Agent 自有版本）

**防御（安全）**——借鉴多渠道网关 + CLI/TUI 框架：
11. Tool Loop Recovery（防死循环）
12. User Declined ≠ Tool Output（防 LLM 绕过）
13. Crash-safe tool settlement（crash 可恢复）

**工程化**：
14. MCP SDK fork + patch（不要直接用 vanilla SDK）
15. Native binary CLI（启动快）

### 场景 B：企业 / 区域市场的 Agent

**必做（核心架构）**——以 桌面 Agent 为骨架：
1. 三模式 Craft/Plan/Ask（用户可控自主度）
2. Plugin 三件套统一格式（Expert/Skill/Connector 同构）
3. Skill 自动闭环（Accumulation/Reflection/Correction）
4. present_files 强制交付（完成任务必交付物）
5. ACP 双向 RPC（agent 与 UI 解耦）

**强烈推荐**——借鉴 IDE-A + 桌面 Agent：
6. Variables @ 触发系统（多种 context 用 @ 触发）
7. 大量 feature 开关（产品分化）
8. Multi-Agent × Multi-Model 路由
9. 多层 Memory 注入（防 lost-in-the-middle）

**工作流**：
10. Automations SQLite 多表（定时任务）
11. Daemon 持久化（云端 7×24 任务托管）
12. MCP Tasks 流式 API（长任务）

**安全**——借鉴 IDE-B + 桌面 Agent：
13. AI Attribution（代码归因）
14. Shadow Workspace（审查前不污染）
15. 文件安全多规则（文件安全硬约束）

### 场景 C：开发者 CLI/TUI 工具

**必做**——以 CLI/TUI 框架 为骨架：
1. 函数式 Service 组合（多 Service 依赖注入）
2. Native binary CLI（编译分发）
3. Crash-safe tool settlement（先持久化再执行）
4. MAX_STEPS 硬约束（简单防死循环）
5. 完整 MCP 支持（lifecycle/oauth/session-recovery）

**推荐**——借鉴多渠道网关 + CLI/TUI 框架：
6. Tool Loop Recovery（检测死循环）
7. Turn Tainting（中断 turn 标记）
8. AsyncLocalStorage 工具上下文（反向追溯）
9. User Declined ≠ Tool Output（权限处理）
10. HTTP API Codegen + Recorder（独门绝活）

### 场景 D：多渠道 IM Bot

**直接借鉴 多渠道网关**：
1. 多渠道统一抽象（异构 IM 统一接口）
2. Gateway Protocol（完整协议规范）
3. Agent Loop 双层循环（处理"用户边说边改"）
4. AsyncLocalStorage 工具上下文
5. 多 memory engine（记忆按职责分离）
6. Frame Guards + Secret Ref（协议层安全）
7. Thread Ownership + Policy（多用户/多渠道治理）
8. Idle reaper + eviction（长跑多 session）

### 场景 E：桌面办公 Agent

**必做**——以 桌面 Agent 为骨架：
1. 三模式 Craft/Plan/Ask
2. Plugin 三件套（配置 + MCP + hooks）
3. Skill 三级渐进披露（metadata / SKILL / resources）
4. Skill 自动闭环（Accumulation / Reflection / Correction）
5. present_files 强制交付
6. 多层记忆注入（多段 Memory + Working + User）
7. 模板引擎 prompt
8. Automations SQLite 多表
9. Daemon 持久化
10. MCP Tasks 流式 API

**加 IDE-B 安全**：
11. AI Attribution
12. Shadow Workspace

---

## 四、做 Agent 时**不能犯的错**（反模式合集）

### 架构反模式
1. ❌ **单文件巨型 bundle**——保持模块小
2. ❌ **过度抽象**（数千个 service）——能函数化就函数化
3. ❌ **过度拆分**（过多 packages）——历史包袱重
4. ❌ **依赖闭源 SDK 做核心**——核心用开源，闭源只做集成

### 协议反模式
5. ❌ **JSON 跨进程通信**——Protobuf 更高效（IDE-B 的实践）
6. ❌ **重新发明协议**（自有数十服务）——用行业标准 + 薄扩展

### Prompt 反模式
7. ❌ **合规策略硬写在 prompt**——放在 L1 拦截层
8. ❌ **内部代号暴露**——内部代号和外部 API 名分离
9. ❌ **硬编码 prompt**——用模板引擎

### 产品反模式
10. ❌ **商业策略绑架产品**——通过插件机制
11. ❌ **强制替换用户选择**——给用户选择权
12. ❌ **闭源 walled garden**（大量私有 API）——第三方无法扩展

### 命名反模式
13. ❌ **产品绑定的目录名**——用产品无关命名
14. ❌ **保留字命名**（agent/chat 等通用词）——避让
15. ❌ **大小写不统一**——统一 kebab-case

### 功能开关反模式
16. ❌ **大量扁平开关**（数十个）——按功能域分组嵌套
17. ❌ **V2 共存**——替换不要共存

### Agent 反模式
18. ❌ **大量"假 agent"**（多名但工具集相同）——真 agent 要有不同工具集
19. ❌ **schema 超前于产品**（schema 有但 UI 不开放）——schema 跟产品同步

---

## 五、按形态的参考实现方向

做 agent 时按需求找对应形态的实现方向（不指向具体文件）：

| 需求 | 参考形态 | 实现方向 |
|---|---|---|
| 双向 RPC 协议方法表 | 桌面 Agent | ACP 风格的 agent-UI 解耦 |
| Protobuf agent schema | IDE-B | binary 强类型 schema 设计 |
| Agent Loop 双层循环 | 多渠道网关 | outer follow-up + inner tool |
| 函数式 Session Runner | CLI/TUI 框架 | Service 组合 + Effect 风格 |
| 完整 prompt 模板系统 | 桌面 Agent | Nunjucks + 多模板 |
| Skill 三级渐进披露 | 桌面 Agent | metadata / SKILL / resources |
| Plugin 三件套格式 | 桌面 Agent | 配置 + MCP + hooks 统一 |
| 大量 feature 开关 | IDE-A | product.json 风格分组 |
| Multi-Agent × Multi-Model | IDE-A | 配置驱动路由 |
| Variables @ 触发 | IDE-A | UI parser + resolver |
| 多渠道 channel 抽象 | 多渠道网关 | schema 驱动统一接口 |
| 多 memory engine | 多渠道网关 | 按职责分离（embeddings/baseline/qmd/storage）|
| MCP SDK patch | IDE-B | OAuth 重试等增强 |
| AI Attribution | IDE-B | 行级归因标记 |
| Shadow Workspace | IDE-B | 虚拟工作区副本 |
| Automations SQLite | 桌面 Agent | 多表 + rrule + daemon |

---

## 下一步
- 选定路线 → 起项目骨架（参考各章节借鉴清单）
- 想看通用结构分析方法 → [`09-reversing-toolchain.md`](./09-reversing-toolchain.md)
