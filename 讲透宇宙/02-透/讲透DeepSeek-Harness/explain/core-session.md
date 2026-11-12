# session/src/index.ts — dsh-session：事件溯源会话的内核

> 原文件：[`packages/core/session/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/core/session/src/index.ts)（1224 行）

## 角色定位

`dsh-session` 定义了 harness 里"会话"的本来面目：一条 **append-only 的事件日志**，加上两个核心类——`Session`（日志之上的视图与模型可见消息派生器）与 `SessionStore`（创建、恢复、分叉与生命周期管理）。包入口汇出事件信封断言、header 折叠与 surface 折叠等公共 API。

这个文件是仓库级不变式 **"model-visible ⟺ logged"** 的执行现场：任何到达模型请求的输入，都必须能从会话日志重建；反过来，要让模型看见新输入，唯一途径是追加事件。快照测试能"无密钥重放录制会话"（`test:snapshot`），靠的正是这份可重建性。仓库还处于 pre-release 的"地基优先"阶段，`SESSION_FORMAT_VERSION` 刻意停在 `0`，对旧日志格式不做任何兼容承诺——读懂这一点，才能理解为什么这里的格式可以随时改。

## 内部结构

1224 行大致分五块：

**标识与版本**：`SessionId` 等品牌化 id；`SessionSeq`（事件序号）与 `SessionLogOffset`（日志偏移）两个度量；`SESSION_FORMAT_VERSION`。事件类型联合默认"读时必知"——构建期不认识的事件类型会拒绝读日志，除非事件信封带 `ignorable: true`；只有结构性格式变化才 bump 版本号。

**header 折叠**（`request-header.ts` 的 `foldRequestHeader`）：从日志折叠出每个回合的请求头——provider、model、reasoningEffort 等配置事实。`canonicalHeader`/`headerEquals` 供 agent-loop 判断"这回合的请求头是否与上回合一致"。

**surface 折叠**（`surface.ts` 的 `SurfaceManager` 与 `deriveEventMessage`）：把任意事件派生成"模型可见消息"。这是"model-visible ⟺ logged"的具体机制——派生是纯函数式的，日志是唯一输入。

**分叉**：`fork(source, boundary, childSessionId)` 把源会话按**包含式 seq 边界**的前缀复制成新会话。两条校验值得记住：切片不得停在 open turn（未闭合回合）内部——那样的日志无法重放；子会话 meta 记录 `parentSession` 与 `isSeeded`，`inheritedEventCount` 记录继承长度。

**修复与存储编解码**（再导出）：`repair.ts` 提供 `interruptedTurnClosers` 与 `TOOL_NOT_STARTED`/`TOOL_OUTCOME_UNKNOWN` 两个哨兵结果——进程在"模型发了工具调用"与"工具结果落账"之间死掉时，恢复逻辑用它们把断口补成可重放的形态；`chunk-rows.ts` 的 `decodeStorageRecord`/`packChunkRuns` 负责持久化行的分块编解码（大事件拆块存储）。

## 外部连接

包内：`request-header.ts`、`surface.ts`、`types.ts` 是三个直接依赖；`preparation.ts` 消费本入口。包外：**持久化是插件关注点**——`dsh-session-persistence` 订阅 `session/event` 落盘，并在 `session/flush` 时排空；`agent-loop` 每次请求从日志派生上下文（见下一篇）；goal 经 session-projection 机制把状态挂进会话投影；session-controller 的 `inspect`/`page`/`follow` 对日志做冷读与流式跟随；两个 SDK（TypeScript/Python）的输出都从这份事件流投影而来——仓库规则要求改 `SessionEventMap` 时两边 SDK 的期望输出必须同一 PR 更新。

会话生命周期的事件名也在这层定调：`session/created`、`session/disposed`、`session/event`（逐事件流）与 `session/flush`（排空点）。下游的典型读法可以参考 session-controller：冷读路径先查 `ctx.sessions` 有没有活着的实例——有则直接用 `snapshotEvents()` 与 `header` 组装检视结果，没有才走持久层读取；`inheritedEventCount` 则让列表页能把"继承来的前缀"与会话自身新增的部分区分展示。

## 数据流

写入侧：用户消息、工具结果、系统事件以信封形式 append（发布状态只在提交点——先落账再通知）。派生侧：每次模型请求前，从日志折叠 header + surface 消息序列 → 交给上下文组装器。恢复侧：进程重启后由 store 从持久层读回记录 → `decodeStorageRecord` 解块 → repair 闭合中断回合 → 视图重建完成。分叉侧：`fork` 复制前缀 → 子会话以 `isSeeded` 元数据开始自己的追加。`snapshotEvents()` 给外部一个时间点快照，`inheritedEventCount` 让消费方能区分"继承的"与"新写的"。

## 设计决策

**事件溯源而非可变状态**：持久化、重放、分叉、审计、崩溃修复全部变成同一份数据上的不同读者。这是本文件一切复杂度的回报。

**内核不写盘**：Session/SessionStore 只维护内存日志与视图，落盘是订阅 `session/event` 的插件的事。内核因此可以在测试里裸跑，持久层可以独立替换。

**修复是一等导出而非私有补丁**：中断回合的闭合器（`interruptedTurnClosers` + 两个哨兵结果）被测试、迁移工具与恢复路径共用，崩溃语义只有一份定义。

**版本号克制**：未知事件默认拒读（fail-loud）+ `ignorable` 信封豁免 + 只对结构变化 bump——三者合起来既允许前向演化，又不静默吞掉读不懂的日志。

**fork 边界校验**：允许的边界必须是"回合已闭合"的位置，从机制上杜绝产生不可重放日志的切片。

## 新人提示

先读 `types.ts` 里的事件联合再回来读本文件，顺序反了会在各处 fold 里迷路。区分 `SessionSeq` 与 `SessionLogOffset`：前者是逻辑序号（事件个数语义），后者面向存储行——分叉边界与分块存储各用各的。改事件类型时默念三条仓库规则：模型可见的输入必须配事件；两边 SDK 快照同 PR 更新；默认拒读意味着旧构建读不了新日志（pre-release 阶段这是预期行为而非事故）。调试"回合恢复后行为诡异"时，第一步永远是用 repair 的视角检查最后一条事件是不是悬空的工具调用。排查"列表里会话状态不对"时，记得它读的可能是持久层冷数据而非内存视图——attached 与 persisted 两条读取路径的差异，就落在 `ctx.sessions.get` 那一次判空上。还有一条工程约束常被忘记：给事件联合加新类型时默认"读时必知"——旧构建读新日志会拒绝，pre-release 阶段这是预期行为而非事故。
