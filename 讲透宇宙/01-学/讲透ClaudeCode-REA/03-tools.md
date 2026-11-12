# 03 · 工具系统：80 个工具、执行管线与并发调度

> 证据：全 chunk `Tt({...})` 工具字面量扫描（80 个工具对象全量提取）+ 执行器
> `T6o`（26.7KB）逐段还原 [S]。深报告（工具清单全表+Edit errorCode 全谱+常量速查）：
> `rea-claude/reports/03-tools.md`。

## 1. 工具接口 buildTool [S]

`Tt`（chunk-00cp8q44）构建工具对象。**默认值全部保守**：isConcurrencySafe=false、
isReadOnly=false、checkPermissions→allow（权限靠规则层）。字段六类：
标识（name/aliases/searchHint）/schema（Zod inputSchema+coerceInput+strict）/
校验权限（validateInput/checkPermissions/preparePermissionMatcher）/行为
（call 或 create 工厂）/属性（isReadOnly/isConcurrencySafe/isDestructive）/
渲染与存储（mapToolResult/stripForStorage/maxResultSizeChars/remoteExecution）。

**schema 技术栈确证为 Zod**（safeParse/superRefine/omit/extend 全套）。

## 2. 注册表：核心 8 件套 + 懒加载 + 门控 [S]

- 核心 8 件套恒在：Read/Write/Edit/Glob/Grep/Bash(+PowerShell)/NotebookEdit；
- **80 个工具对象**经 `import.meta.require` 懒加载 + feature gate 装配；
- 有趣的门控：**TodoWrite 与 Task* 家族互斥**；**KillShell/BashOutput 已降级为
  TaskStop/TaskOutput 的 aliases**；ToolSearch 只在 deferred 工具集启用时出现；
  `CLAUDE_CODE_SIMPLE` 模式裁到 [Read,Edit,Write]（repl 版换 REPL）。

## 3. 执行管线（10 步）[S]

```
1 工具解析（查不到→立即合成 <tool_use_error> tool_result，不中断循环）
2 Zod 解析（coerceInput→safeParse）
3 MCP 必填检查（isMcp 时比对 JSON Schema）
4 validateInput（自定义前置校验，false→errorCode）
5 PreToolUse hooks（updatedInput/defer/stop 分支）
6 权限决策 FPe（hook deny > deny/ask 规则 > checkPermissions+canUseTool+classifier）
7 call(input, ctx, assistantMessage, requestId, onProgress)
8 mapToolResultToToolResultBlockParam
9 PostToolUse hooks（updatedToolOutput 须再过 outputSchema.safeParse；
  hooks 改了文件→补 stale 提示）
10 持久化（stripForStorage 决定 transcript 存量）
```

权限 decision 协议：`{behavior: allow|ask|deny|passthrough, updatedInput,
decisionReason:{type:hook|sandboxOverride|...}}`。

## 4. Bash 细节（工业级）[S]

| 机制 | 实证 |
|---|---|
| 超时 | 默认 120s/上限 600s（env 可覆盖，超上限钳制+timeout_clamped note） |
| 输出 | 30K 字符默认（硬顶 150K）；溢写文件 + `[Truncated. Full output: <path>]` |
| auto-background | 前台 2s 未完成→arm 后台槽；超时自动转后台；turn-abort 时可后台命令转后台 |
| **sleep 拦截** | `sleep ≥25s` 直接 block（errorCode 10）："use Monitor/run_in_background"，**"Do not chain shorter sleeps to work around this block"** |
| **sed 拦截** | sed 编辑被识别→按 Edit 权限通道走（防绕过文件写守卫） |
| sandbox 覆盖 | dangerouslyDisableSandbox→ask（decisionReason=sandboxOverride） |
| 命令分类 | find/grep 族=搜索；cat 族=读；mv/cp/rm 族=写——供 isReadOnly/遥测 |

后台任务输出：轮询 1s、4096B 块、内存缓冲 8MB 后转文件。

## 5. Read/Edit/Write（上下文经济学的核心）[S]

- **"2000 行默认"只是 prompt 话术**：运行时真实约束 = 256KB / 25K token，
  超限自动按行二分分页并提示 `Read with offset=N+1`；
- **file-state 跟踪**：每次成功 Read 记录 `{content, mtimeMs, offset, limit,
  isPartialView}`；Edit/Write 前置校验"读过且未变更"——
  **Edit errorCode 6**（not read）/ **7**（stale，"modified since read"）/
  **9**（多匹配须 replace_all）——这三条就是"读后免重读"机制的全部门面；
- 同 offset/limit 且 mtime 未变 → `file_unchanged` 直接复用（去重）；
- **Write 拦截子代理写 REPORT*.md**（ec=5 "return findings as text, not write
  report files"）——防子代理把结论藏进文件而非回传。

## 6. 并发调度 [S]

- **ToolQueue**：安全工具全并行；**首个不安全工具形成双重屏障**（启动屏障+结果
  按序回流屏障）——串行工具不阻塞 UI 但阻塞后续不安全工具；
- 并发上限 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`（默认 10）；
- 子代理并发槽默认 20。

## 7. 与公开文档对照的差异（勘误）[S]

1. "2000 行 Read 上限"实为 prompt 层描述，运行时是字节/token 双约束+自动分页；
2. KillShell/BashOutput 是 aliases 不是独立工具；
3. TodoWrite 在 Task* 家族启用时被隐藏（两套任务系统互斥）；
4. chunk-6c9tf546 实为 workflow-plan 提示词 chunk（非工具内核）——任务书预设误导，
   Bash 执行内核 `cts` 在主 bundle。

## 8. 手搓启示（→ rl-and-agents/）

1. **默认保守**：新工具默认不可并发、不只读——安全是 opt-in 的；
2. file-state（content+mtime 快照）四两拨千斤：免重读+stale 检测+去重三个功能
   一个机制——mini 版 30 行可复刻；
3. 命令分类器（搜索/读/写/黑名单）让 Bash 的权限粒度接近专用工具；
4. "工具错误→tool_result 而非异常"贯穿始终：循环永不被工具失败打断；
5. sleep 拦截+sed 拦截说明：**防的不是命令，是模型绕过专用工具的捷径**。
