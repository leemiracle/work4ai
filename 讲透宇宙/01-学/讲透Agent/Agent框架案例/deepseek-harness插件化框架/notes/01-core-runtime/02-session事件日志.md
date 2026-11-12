# 02 · Session 事件日志：唯一事实源

> 对应 `packages/core/session/`（`src/index.ts` / `src/types.ts` / `src/surface.ts` / `src/repair.ts`）
> 行号钉版 `47f943859b`

## 1. 铁律：Model-visible ⟺ logged

`docs/architecture.md:96` / `AGENTS.md:107`：**凡是到达模型请求的内容，必须能从会话日志重建**，且有运行时断言强制。推论：新增一种模型可见输入 = 必须新增一个会话事件（扩展 `SessionEventMap`）。

这条不变量消灭了一整类欺骗：agent 无法"对模型说一套、对日志说一套"——UI、fork、resume、transcript、telemetry 全部从同一事件流派生。

## 2. 结构

- `SessionEvent`：按 `type` 区分的联合 + `{seq, time, data}` 信封（`src/types.ts:404`）。
- `SessionEventMap`（`types.ts:236`）核心事件：`turn/start|end`、`step/start|end`、`user/message`、`assistant/chunk`（原始流块）、`assistant/message`（锚点，带 usage）、`tool/call`（**原始未解析的 arguments 字符串**）、`tool/result`、`request/header`、`request/context`、`session/end-seed`。
- **声明合并可扩展**：插件 merge-extend 这个 map（如 `agent/inbox/spliced` 由 agent 包补充）。未知事件类型若不带 `ignorable: true`，**加载时直接拒绝**（`types.ts:413-422`）——向前兼容靠 ignorable 标志，而非版本号膨胀。
- `SESSION_FORMAT_VERSION = 0`（`types.ts:56`）钉进每个 `SessionHeader`，加载不匹配即 throw（`index.ts:101-102`）。只有**结构性**格式变化才 bump。

## 3. `Session` 类

`packages/core/session/src/index.ts:425`：

- 只追加；`seq = log.length` 连续性契约（`:565`）。
- `append()`（`:604`）：一遍无损 JSON 快照 → surface 校验 → 重入保护 → 提交后广播 `session/event`（监听器失败被包含、不影响已提交事实，`:637-654`）。**提交后监听器无法回滚**——"日志即已发生"。
- Surface 事件必须带 `SurfaceIntent {surfaceOp, sourceEventSeqs}`（编译期强制，`types.ts:607`）。

## 4. 投影：`deriveMessages()`

`index.ts:726`。只走**有序 surface**（带 `surfaceOp` 的 `user/message`/`assistant/message`/`tool/result`），增量缓存 O(新增节点)。核心技巧：`surfaceOp: 'replace'` bump `replaceGeneration` 触发重建——**compaction 删除被遮蔽的消息而不动原始日志**。原始 `assistant/chunk` 永远保留（重放与 UI 保真）。

一句话：**日志是事实，模型历史是视图**。改视图（compaction/pruner）永远不丢事实。

## 5. fork / resume / 崩溃修复

- `fork(source, boundary?, childId?)`（`index.ts:1081`）：取到一个**完整 turn 边界**的连续前缀做子会话种子，带 `parentSession`/`seedLength` 血统。subagent `fork-in-process` provider 就用它把父会话的已完成 turns 作为子 agent 的出身。
- resume：`Session.fromRestore`（`:495`）+ 持久化种子 + `agent-loop.resume()` 发布 `agent/session-start {source: 'resume'}`。
- 崩溃修复（`src/repair.ts`）：合成 `interrupted` turn 结尾 + `TOOL_NOT_STARTED`/`TOOL_OUTCOME_UNKNOWN` 工具结果——**崩溃不留悬空状态，修复本身也是日志事实**。

## 6. 持久化

`packages/session/` 组：persistence 接缝 + JSONL / SQLite 两个后端；SQLite 用单调 `SCHEMA_VERSION`；JSONL 在 Windows 用 `MoveFileExW` write-through 发布（`pnpm-workspace.yaml:52` 注释）。另有 projection 缓存、标题生成（LLM）、遥测（含 OTel 导出）、checkpoint 策略、`session-query` 组（SQLite 全文检索 + `session_search` 等模型工具）。

## 7. 验证命令

```bash
$ rg -n "export const SESSION_FORMAT_VERSION" packages/core/session/src/types.ts
56:export const SESSION_FORMAT_VERSION = 0
$ rg -n "session header version must be" packages/core/session/src/index.ts
102:    throw new Error(`session header version must be ${SESSION_FORMAT_VERSION}, got ${String(record.version)}`)
$ rg -n "export class Session |deriveMessages\(\)" packages/core/session/src/index.ts
425:export class Session {
726:  deriveMessages(): Message[] {
```

## 8. 设计要点提炼

1. **event sourcing for agents**：不是"对话历史存 DB"，而是"领域事件流 + 派生视图"——compaction/fork/重放/审计全部免费。
2. **未知事件默认拒绝**（`ignorable` 是显式豁免）——旧版本读到新数据 fail-loud 而非静默丢弃。
3. **修复即事件**——崩溃恢复写成日志，而非日志外的 side channel。
4. **原始与投影分层**——chunk 保真、message 锚定、surface 投影，三层各司其职。

→ 下一篇：[03-tools管线与系统提示](03-tools管线与系统提示.md)
