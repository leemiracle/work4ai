# 01 · 桌面办公 Agent 架构模式

> 桌面办公自动化 Agent 形态的架构分析。本文档已脱敏，不指向任何具体产品。

---

## 一、形态定位

- **形态**：Electron 桌面应用 + 云端守护进程
- **用户**：非技术职场人（vs IDE 的开发者）
- **目标**：办公自动化（文档/表格/邮件/IM/定时任务）
- **对标范式**：通用桌面办公 Agent（业内多款产品采用此路线）

---

## 二、架构分层（七层模型）

```
L7 多端入口
   Electron Desktop │ Daemon (云端 7×24) │ Mini Program │ IM Connectors
                          ↓ ACP Protocol（双向 RPC，ndjson）
L6 应用协调层
   认证/产品协调 + 应用服务器 + 桌面监控服务
   ↓
L5 Agent 运行时（基于 OpenAI Agents SDK 风格）
   • 7 步 Agent Loop（分析→思考→选工具→执行→观察→迭代→交付）
   • TaskCreate/Get/Update/List 任务管理
   • Three Modes: Craft / Plan / Ask
   • SubAgent delegation
   ↓
L4 Prompt 模板引擎（Nunjucks / Jinja2 风格）
   多模板 + 多风格 + 条件渲染
   多段记忆注入（早期/工具相关/总结性 + Working + User）
   ↓
L3 能力扩展层（Plugin = 三件套统一格式）
   插件配置 + MCP 声明 + hooks 声明
   • Skill：SKILL.md + scripts/ + references/ + assets/
   • Expert：角色 prompt + 头像 + 展示字段
   • Connector：MCP Server（含实验性 tasks 流式 API）
   ↓
L2 工具与协议
   内置：Bash/Read/Write/Edit/Glob/Grep/Task/WebFetch/ImageGen/VideoGen/
        present_files/TaskCreate/automation_update/terminal_*
   外挂：MCP（experimental.tasks 流式）
   ACP 反向调用：elicitation_create/complete, request_permission
   ↓
L1 持久化与基础设施
   SQLite - automations 多表 + sessions
   对象存储 - 云端文件
   E2B Cloud Sandbox - 云端隔离执行
   本地沙箱 - 命令隔离
   OpenTelemetry - 全链路追踪
   安全审计
```

---

## 三、独有设计（该形态的创新）

### ★★★★★ 三模式架构（Craft / Plan / Ask）

三种用户可控的自主度档位，用 reminder XML 切换：

```xml
<!-- Ask 模式硬约束 reminder（只读，不改任何东西）-->
<ask_mode>
Ask mode is active. You MUST NOT make any edits, run any non-readonly tools,
or otherwise make any changes to the system. This supersedes any other instructions.
</ask_mode>
```

**借鉴价值**：定义明确的自主度档位，硬约束优先级写在 reminder 里，覆盖其他指令。

### ★★★★★ Skill 自动闭环（Accumulation / Reflection / Correction）

```
完成任务（多次 tool calls） → 强制 Accumulation（写新 skill）
用过 skill                 → 强制 Reflection（评估是否更新）
发现 skill 有问题           → 强制 Correction（立即修复，不问用户）
```

**借鉴价值**：把 skill 维护作为 agent loop 的一部分，**不延迟到下次**——这是"自进化 agent"的关键。

### ★★★★★ Plugin 三件套统一格式（Expert / Skill / Connector 同构）

任何扩展 = 插件配置 + 内容文件，内容文件按形态不同：
- **Skill**：SKILL.md + scripts/ + references/ + assets/
- **Expert**：agents/*.md + 头像（+ 可选 scripts/refs）
- **Connector**：MCP 声明 + hooks 声明 + dist/

**借鉴价值**：统一扩展格式降低生态碎片化。

### ★★★★ 多层 Memory 注入（分段防 lost-in-the-middle）

```
prompt 头部:   早期重要记忆
prompt 中段:   工具相关记忆
prompt 尾部:   总结性记忆
```

**借鉴价值**：长 prompt 的关键信息分头/中/尾三段注入，避免中间位置被 LLM 忽略（lost-in-the-middle 现象）。

### ★★★★ ACP 协议作为标准 RPC 边界

双向 RPC（agent 暴露给 UI 的方法 + UI 暴露给 agent 的反向调用）：

```
AGENT→UI 方向（agent 暴露）:
  session_{new/load/list/close/...}  document_did_{open/change/...}
  nes_{start/suggest/accept/...}     providers_{list/set/...}

UI→AGENT 方向（反向调用）:
  fs_{read/write}_text_file          mcp_{connect/disconnect/message}
  terminal_{create/kill/...}         elicitation_{create/complete}
  session_request_permission         session_update
```

**借鉴价值**：定义清晰的进程边界，**agent 不知 UI 存在**——agent 可被任意 UI（桌面/web/IM）复用。

### ★★★★ Automations SQLite 多表

```sql
automations              -- 定义（name/prompt/schedule/rrule/status/...）
automation_runtime_state -- 运行时状态（last_run/next_run）
automation_runs          -- 执行历史
```

两种调度：recurring（rrule RFC 5545）/ once（ISO 8601）。Daemon 进程即使关闭客户端也持续运行。

### ★★★★ present_files 强制交付

prompt 段强制每个完成任务必须调用 `present_files`——确保 agent 总是显式交付结果。

### ★★★ MCP 实验性 Tasks 流式 API

```javascript
server.experimental.tasks.requestStream(request, resultSchema, options)
// 事件：'taskCreated' → 'taskStatus' → 'result' | 'error'
```

长任务用流式事件，而非一次性返回。

---

## 四、典型工作流：用户提问 → Agent 执行 → 交付（Craft 模式）

```
1. Prompt 渲染（模板引擎）
   主模板 + 多段记忆 + 当前 workspace + 当前模式

2. Agent Loop（7 步循环）
   Analyze → Think（写计划）→ Select tool（含 Skill 触发判断）
   → Execute → Observe → Iterate → Present outcome（present_files）

3. Skill 自动维护闭环（同一回合内）
   Accumulation（多次调用后保存）→ Reflection（用过 skill 后反思）→ Correction（发现问题立即修）

4. 结果交付
   present_files：HTML live preview / 图像/PPT/视频 artifact 卡片 / URL 内置浏览器
```

---

## 五、反模式（做 agent 时要避免）

1. ❌ **合规策略硬写在 prompt 里**——prompt 注入可绕过；应放在 L1 拦截层
2. ❌ **内部代号暴露设计灵感**——内部代号和外部 API 名应分离
3. ❌ **插件目录名硬编码产品名**——用产品无关命名
4. ❌ **依赖闭源 SDK 做核心**——核心 agent loop 用开源，闭源只做集成层
5. ❌ **单文件 minified 巨型 bundle**——保持模块小（<500KB/文件）

---

## 六、借鉴价值总结

做**桌面办公 Agent**时，借鉴此形态的：
- **三模式 Craft/Plan/Ask**（用户可控自主度）
- **Plugin 三件套**（统一扩展格式）
- **Skill 自动闭环**（agent 自进化）
- **present_files 强制交付**（确保交付）
- **Automations + Daemon**（定时任务 + 云端 7×24）
- **ACP 双向 RPC**（进程解耦）
- **多层 Memory 注入**（防 lost-in-the-middle）

---

## 下一步
- 看 IDE-B 怎么用进程分离解决同样的问题 → [`03-IDE-B.md`](./03-IDE-B.md)
- 看横向对比 → [`06-comparison.md`](./06-comparison.md)
