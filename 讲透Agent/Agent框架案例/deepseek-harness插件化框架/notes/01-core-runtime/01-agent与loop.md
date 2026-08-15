# 01 · Agent 与 Loop：turn/step 状态机

> 对应 `packages/core/agent/`、`packages/core/agent-loop/`、`packages/core/scope/`
> 所有行号钉版 `47f943859b`

## 1. Agent 是什么

`Agent` 接口（`packages/core/agent/src/runtime-types.ts:64`）：

- `id: SessionId`——agent 与会话**同 id**（注册表强制 `agent.id === agent.session.id`）。
- `inbox: Inbox`——唯一输入通道；`status: 'idle' | 'running'`。
- `ctx: Context`——agent 作用域注册边界（scope 机制见 §5）。
- `send(message, target, wakeup)`——统一路由原语；三个预设（`agent-loop/src/agent.ts:122-132`）：
  - `followup` → `next-turn` 队列，唤醒
  - `steer` → `next-step` 队列，唤醒
  - `inject` → `next-step` 队列，**不唤醒**（注入上下文等下一条消息来了一起被消费）
- `cancel(cause, {keepInbox})`——中止当前轮；默认清空 inbox 全部待办。
- `AgentCancelCause = user | parent | hook | disposed`（`session/src/types.ts:143-147`）。

## 2. Inbox：一次性的投影

`packages/core/agent/src/inbox.ts:25`。核心设计：Inbox 不是独立存储，而是**对 durable `agent/inbox/spliced` 会话事件的 replay-once 投影**——两条 FIFO（`next-turn` / `next-step`），每次变更先追加 splice 事件再改内存投影（事件先于状态 = 崩溃可恢复）。`claim(target, turn)`（`inbox.ts:71`）一次取走整个 `next-step` 批次 + 一条 `next-turn`。

## 3. turn/step 状态机

`packages/core/agent-loop/src/agent.ts`（驱动类）：

```text
turn/start（durable）
  每步:
    preStep (:225)  = inbox.claim → systemPrompt.assemble → agent/pre-step 瀑布
                      ↓ 返回 reject → 本轮零 step 关闭（turn/end: blocked）——但日志记录了尝试
    step/start → 消息以 user/message(surfaceOp:'append') 落日志
    step (:332)     = agent/request 瀑布（冻结 LlmCallConfig）
                      → llm/stream → assistant/chunk* 流式落日志 → assistant/message 锚点
                      → 工具调用 → executeToolCalls
    step/end
  agent/turn-stopping（串行，监听器可 agent.steer 留住本轮）
turn/end（durable，理由: completed|aborted|blocked|error|max-tokens|interrupted）
```

关键细节：

- **零 step 的 turn 也是合法 turn**：`agent/pre-step` 拒绝或首 claim 为空 → 关闭一个"花了 0 个 step 的 durable turn"（`agent.ts:267-277`）。为什么？**日志必须记录"有人试图说话但被拒"**——否则审计断链。
- **请求冻结**：`agent/request` 瀑布后 `markAgentLoopRequest` 冻结请求（`agent.ts:486`）；`request/header`（initial/resume/change）+ `request/context` 均落日志。
- **流错误恢复**：流式失败进 `agent/request-error` 瀑布，监听器返回 `{kind:'retry'}` 且不调 `next()` 即自己持有恢复；默认终局。`dsh-llm-retry` 就挂在这个扩展点。
- **turn 循环**：`turn()`（`:246`）在还有待办时继续开新 turn；`max-tokens` 结束是粘性的（`:290`）。

## 4. 工具调用调度

`packages/core/agent-loop/src/tool-calls.ts:59`：独占调用形成屏障，连续可并行调用进有界滚动池（`maxParallelToolCalls` 默认 10）。设计要点：**策略与结果保持模型顺序，仅派发重叠**——通过注册表的分阶段调度器（`prepare/dispatch/finalize`）实现。中止时未派发的调用得到合成 `ABORTED_BEFORE_DISPATCH` 结果——不留悬空。

## 5. 注册表与作用域

- `AgentRegistry`（`packages/core/agent/src/index.ts:256`）：`enter`（幂等插入+id 冲突检查）→ `announce`（发 `agent/created`，**同步监听器抛错可否决发布并回滚**）→ 按序拆除。`dispose()` 是**消费者能力**：只有句柄持有者能拆 agent。
- **Initiator 作用域**：两个 `AsyncLocalStorage`（`index.ts:259-260`）做进程内因果归责——loop 在 `withInitiator` 里跑，工具执行时 `requireInitiator()` 找回"这是哪个 agent 的调用"。
- **scope 原语**（`packages/core/scope/src/index.ts:137`）：`createScope` 铸出带不透明 `ScopeKey` 的子 fiber context；未打标的监听器全局收，打标的按 key 或祖先链匹配——事件沿链上流、注册沿链下继承。这是所有 agent 级事件过滤的底座。

## 6. 验证命令

```bash
$ rg -n "export interface Agent " packages/core/agent/src/runtime-types.ts
64:export interface Agent {
$ rg -n "private async turn\(|private async preStep\(|async step\(" packages/core/agent-loop/src/agent.ts
225:  private async preStep(...
246:  private async turn(): Promise<boolean> {
332:  async step(...
$ rg -n "export class Inbox|claim\(" packages/core/agent/src/inbox.ts
25:export class Inbox {
71:  claim(target: InboxTarget, turn: number): UserMessage[] {
```

## 7. 设计要点提炼

1. **inbox 不是队列是日志投影**——崩溃恢复、重放、审计三合一。
2. **拒绝也要留痕**——零 step turn 的存在让"被拒的输入"可审计。
3. **取消语义分级**（followup/steer/inject + keepInbox）——把"用户插话"建模为一等公民。
4. **注册即 effect**——`agent/created` 被监听器否决即回滚，发布是事务。

→ 下一篇：[02-session事件日志](02-session事件日志.md)——这一切 durable 事件存在哪、怎么投影回模型输入。
