# subagent/src/child-agent.ts — 子代理派生：深度与策略传递的唯一入口

> 原文件：[`packages/subagent/subagent/src/child-agent.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/subagent/subagent/src/child-agent.ts)（280 行）

## 角色定位

这个文件回答的问题是："父 agent 派生一个子 agent 时，到底传下去什么、以什么形态传"。它是**子代理派生的组合核心**：从父 Agent 解析子代理选项——委托深度、持久会话元数据、组合应用、委派策略覆盖的捕获与回放——并把父上下文的系统提示节序、工具限制与沙箱策略投影到子会话。图谱与源码一致把它标记为 delegation 深度与策略传递的唯一入口：`SubagentRuntime` 的两条启动路径（一次性的 `start` 与可续接的 `startContinuable`）都汇聚到这里，不存在第三条私自派生通道。

280 行做这么重的事，靠的是"组合而非实现"：它不运行子代理（那是 agent-loop 的事），不管理子代理生命周期（那是 lifecycle/continuation 的事），只负责把"子代理应该长什么样"解析出来。

## 内部结构

**深度预算**：`delegationDepthOf`（来自 `depth.ts`）读取父 agent 的委托深度，子代理以深度 +1 派生。深度预算是硬闸：超过预算的派生直接拒绝，从机制上杜绝"子代理再派子代理"的无穷递归与指数爆炸。

**持久会话元数据**：子代理的会话不是匿名的临时物——派生时写入 durable session metadata（父会话、派生上下文等），使子会话可以像任何普通会话一样被持久化、恢复、分叉。

**解析后的 child AgentOptions**：输出不是"引用父配置"，而是**解析后的值**——系统提示节的顺序、工具限制清单、沙箱策略，都以子代理自己的快照落定。父随后变更不穿透到已派生的子。

**委派 policy seed**：把父侧的委派策略覆盖"捕获/回放"为一颗种子传给子——子在再做委派决策时以这颗种子为基底。策略链因此是显式传递的，而不是读全局。

**scoped setup**：子的注册在 `createScope` 的作用域里进行（对接 dsh-scope 与 ToolRuntime 的分层遮蔽）——子看见的工具集是"全局层 + 委派策略允许的投影"，而不是全量。

**机会式依赖**：`sandboxPolicy`、`approval`、`agentPresets` 都以 **type-only import** 消费——编译期要求形状正确，运行时有则用、无则跳，subagent 包不必硬依赖沙箱与审批实现。

## 外部连接

包内：依赖 `depth.ts`；被 `continuation.ts` 消费（`index.ts` 汇出的 SubagentRuntime 是能力缝的 Service Provider 汇聚点，经 continuation 走到本文件）。跨包：dsh-agent 的 AgentOptions 与注册表、dsh-scope 的作用域、core/tools 的分层注册、agent-loop 的驱动，都是它组装子代理时踩着的地面。图谱确认它的下游只有 continuation 一条正式通道——这正是"唯一入口"的结构证明。

同包的 `projection.ts` 与 `list-children.ts`（经包入口汇出）在派生结果之上提供目录与后代列举：持久会话元数据里的父子关系让"列出某 agent 的全部后代"变成一次日志查询，不需要运行时另行簿记——派生时写下的元数据在事后追溯中持续生息。

## 数据流

派生一次的完整路径：上游请求（一次性 start 或可续接 startContinuable）→ 读父 agent 状态 → `delegationDepthOf` 检查深度预算 → 解析 child AgentOptions（组合应用 + 委派策略种子）→ 写持久会话元数据 → scoped setup（作用域内注册工具投影与系统提示节序）→ 子会话建立、子 agent 交给驱动层运行 → 结果沿各自路径回投（一次性直接返回；可续接的挂进 continuation manager 等待后续投递）。策略面的数据流是单向的：父 → 种子 → 子，子对策略的再覆盖成为下一代的种子。

## 设计决策

**单一组合入口**：一次性与可续接两条路径共享同一个派生核心，避免"两条路径两套语义"漂移。差异被推到最外层（结果如何投递），共性收在最里层（子代理长什么样）——这正是仓库"一个异步操作一个生命周期控制器"规则在派生场景的落地。

**传递解析后的值**：子拿到的是投影快照而非父状态引用。收益是隔离（父后续变化不穿透）与可持久化（快照可以随会话元数据落盘重放）。

**深度预算**：委托递归是 agent 系统特有的失控模式，预算在唯一入口处强制，比在每个 provider 里自查可靠。

**type-only 机会式消费**：subagent 不被沙箱/审批实现绑架，最小部署可以没有它们；类型检查仍然保证"用的时候形状对"。

**策略种子化**：委派策略不读全局配置，而沿派生链显式传递——审计一次派生行为只需要看种子，不需要重放全局状态。

## 新人提示

从 `delegationDepthOf` 的调用处下断点读一遍全文件，是最快的理解路径。对比 `start` 与 `startContinuable` 在本文件之后的分叉点，你会看到"组合 vs 生命周期"的边界画在哪里。排查"子代理看不到某个工具"时，沿着 scoped setup 的投影链查：先查全局有没有注册，再查作用域层遮蔽，最后查委派策略种子的限制——三步定位。要给子代理加新能力时，先问自己它属于 AgentOptions（本文件）、生命周期（lifecycle/continuation）、还是运行时扩展点（插件）——放错层的补丁会被"唯一入口"的结构顶出来。深度预算报错不是 bug，是这一层存在的意义。
