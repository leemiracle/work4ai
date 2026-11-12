# agent-loop/src/agent.ts — ReactLoopAgent：ReAct 回合引擎

> 原文件：[`packages/core/agent-loop/src/agent.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/core/agent-loop/src/agent.ts)（545 行）

## 角色定位

`ReactLoopAgent` 是 harness 的心脏起搏器：它把"组装上下文 → 调模型 → 执行工具调用 → 结果落账 → 再调模型"的 ReAct 循环一轮轮驱动下去，直到某个回合模型不再发起工具调用，回合（turn）自然闭合。它是 `dsh-agent-loop` 包的实现核心（包入口 `index.ts` 定义的 AgentLoop 插件负责按配置身份恢复或创建 agent，然后把实际驱动交给这里）。

这个文件的特殊地位由一条仓库制度标记出来：**"Plugins, not loop changes"**——新行为必须落在文档化的扩展点上，修改 `agent-loop` 本身要求同步更新 `docs/architecture.md`。换句话说，全仓库的扩展性设计，很大一部分是为了让这个文件可以保持稳定。

## 内部结构

**Phase 状态机**：`idle` / `maintenance` / `running` 三态。running 期间持有 `AbortController`，取消（cancel）经 `abort` 一路贯穿到工具执行与模型流；`wakeRequested` 标记"排空过程中又来了新输入"，让循环在安全点重新唤醒而不是丢消息。

**inbox 待定消息并入**：回合进行中到达的用户输入不排队丢弃，而是进入 inbox，由并入策略决定语义——是并入当前回合（steer）、留作下一回合（followup）、注入中间内容（inject），还是触发取消（cancel）。phase 的动词集合 `send/followup/steer/inject/cancel` 就是对这些语义的显式建模。

**推进结构**：`preStep` / `turn` / `step` 三层。turn 管一个完整回合的生命周期（含 header 决策——本回合用哪个 provider/model/reasoningEffort），step 管一次"模型请求 + 工具调用波"的迭代，preStep 是每次步进前的准备钩子。

**上下文投影**：`runtime-context.ts` 的 `RuntimeContextProjection` 把"当前请求需要什么上下文"表达成可投影的数据——运行时事实（当前工作目录、环境面等）与系统提示节的组装都经它进入请求。

**工具执行**：`tool-calls.ts` 的 `executeToolCalls` 按并发模式把本步的工具调用分组调度，组内并行/串行与取消信号由 `runGroup` 处理；`appendToolResult`/`appendSkippedToolCall` 把结果与跳过事件写回会话日志——落账永远走 session，引擎自己不留小账本。

## 外部连接

源码与图谱共同确认的依赖面：包内 `runtime-context.ts`、`tool-calls.ts`，被包入口 `index.ts` 引用。跨包：`dsh-agent`（`Inbox`、`agentEvents`、`assembleContextFor`——AgentRegistry 提供 initiator 作用域的 agent 生命周期）；`dsh-llm`（`BlockAssembler`、`createAssistantMessage`、`markAgentLoopRequest`）；`dsh-scope` 的 `createScope`（回合内的作用域化注册）；`dsh-session` 的 `canonicalHeader`/`headerEquals`（回合间请求头比较）；`dsh-system-prompt` 的 `joinContextSections`/`renderPrompt`（系统提示节拼接与渲染）。上游消费者是 AgentLoop 插件与 session-controller 的 promotions（后台激活）。

状态的外化也发生在这条边界上：引擎发出的 `agent/status`（是否 running）与 `agent/error`（错误链）事件，被 session-controller 转换成 `api-session/status`、`api-session/error` 推给客户端；回合请求头里的 provider/model/reasoningEffort 落成 `request/header` 事件后，模型选择投影随即消费——引擎只管产出事实，投影与远程面各自订阅。包入口的 `index.ts` 还定义了 `FactoryOwnership`（工厂所有权与排空等待），"按配置身份恢复或创建 agent"的编排与启动失败上报归它管。

## 数据流

单回合主线：触发（用户消息事件到达）→ maintenance 检查（维护窗口内的整理动作）→ 进入 running → **从 session log 派生**本回合上下文（surface 消息序列 + header 折叠结果 + 系统提示节）→ `assembleContextFor` 组装 → LLM 流式调用 → `BlockAssembler` 把流式 chunk 组装成冻结的 assistant 消息 → 若含工具调用：`executeToolCalls` 分组执行，结果事件 append 回日志 → 回到组装，进入下一步；若无工具调用：回合闭合，回 idle。期间任何时刻 inbox 到新消息，按其语义改变后续走向；abort 触发时各层在最近的安全点停止并如实记录中断事件。

注意"派生"二字：引擎**每次请求都从日志重建上下文**，自己不维护一份可变对话历史。这份纪律是"model-visible ⟺ logged"不变式在引擎侧的镜像。

## 设计决策

**每请求重派生**：内存里的对话状态与会话日志可能漂移是一切诡异 bug 的温床。把派生做成每请求的纯函数调用，代价是重复折叠，换来的是"日志即真相"的强保证——快照重放、分叉、崩溃恢复全部免费受益。

**inbox 语义显式化**：回合中用户输入的四种去路（steer/followup/inject/cancel）不是隐式行为而是命名的 phase 动词，测试与文档都能引用它们。

**取消的单一通道**：AbortController 从 phase 一路贯穿到工具组与模型流，避免"半取消"状态。

**循环封闭性**：引擎只认 session（读写）、llm（调用）、tools（执行）三个接口，扩展点全部外移——这正是"Plugins, not loop changes"能成立的结构性前提。

## 新人提示

最好的入门路径是挑一个 `test:snapshot` 的录制会话，按"事件流顺序"单回合 trace 一遍：先看 phase 迁移，再看消息组装，最后看工具分组。理解 steer 与 followup 的区别是掌握 inbox 的钥匙：前者改变当前回合的走向，后者只预约下一回合。排查"模型行为不受新插件影响"时，先确认插件挂的是文档化扩展点（系统提示节、上下文投影、工具管线），而不是试图改本文件——后者是被制度性劝阻的路径。调试取消问题时，从 AbortController 的 owner 关系入手，比逐层加日志快得多。看懂 turn 与 step 的层级后，再去找 `agent/status` 事件的发射点读一遍——你会看到 UI 上"运行中"指示灯的完整旅程：引擎置位、事件冒泡、控制器转译、远程推送，四步全是声明式的订阅关系。另外记住维护规则：本文件的任何行为改动都要同步更新 docs/architecture.md——这不是流程负担，而是把"循环语义变更"强制变成一次显式评审。
