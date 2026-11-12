# tools/src/index.ts — ToolRuntime：工具能力的运行时核心

> 原文件：[`packages/core/tools/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/core/tools/src/index.ts)（1937 行）

## 角色定位

`ToolRuntime`（包的默认导出服务类）是工具能力的**服务端枢纽**：工具注册表、分层限制与守卫、native 与 PTC 双模式分派、并行子调用调度、取消信号融合、结果呈现与物化，全在这一个类里。包入口同时汇出 `defineTool`、JSON Schema 校验、TS/Python SDK 类型渲染等公共 API——后者意味着"工具的模型面描述"与"工具的宿主面类型"由同一处源头生成。

全仓库所有模型可调用的能力都要在这里注册：bash 工具（tool-bash）、MCP 桥接来的外部工具、子代理工具投影、内置的 `run_code`。可以说这是 agent "手"的关节——模型发出 tool_call 之后的世界，从这 1937 行开始。

## 内部结构

**注册**：`register(definition)` 支持全局注册与 scope 注册两条路。scoped 注册进入作用域层（对接 `dsh-scope` 的 `ScopedLayers`），**子层遮蔽父层与全局**——子代理可以拥有自己的工具集而不动全局；同层之内重名注册报错，保留名 `run_code` 一律拒绝（内置 PTC 工具的专属命名空间）。注册是 effect：registry 的 `register()` 返回 disposer，随作用域拆卸自动移除（HMR 安全由测试强制）。

**呈现**（`presentation.ts`）：面向模型的 schema 呈现模式——同一个工具在不同呈现面（宿主 UI、Web 卡片、模型请求）投影出不同的描述形态。

**执行管线**：一次 tool_call 依次经过 pre → guard → around → post → result 各阶段。guard 是审批 seam（升级批准在这里拦），pre/post/around 是观察与包装点。仓库规则"决策在执行它的操作里做"在这里落地：schema 缺省、提示词过滤、外观包装都不算 enforcement，真正的拒绝发生在执行器内。

**输入校验**（`json-schema.ts`）：`assertSupportedJsonSchema` 在注册时把关 schema 子集（模型面只暴露可表达的 JSON Schema），`validateJsonSchemaValue` 在执行前校验参数值。

**代码运行时**：`requireCodeRuntime` 按工具的 `codeRuntime.language` 查 `SDK_RENDERERS`——`ts-types.ts`/`py-types.ts` 两个渲染器把工具定义投影成 TypeScript 与 Python 的调用面，双 SDK 的类型因此与工具 schema 永远同步。`ptc.ts` 提供内置 `run_code` 工具（PTC 模式的代码执行桥）。

**审批可选**：审批能力经 **type-only import** 注入——编译期类型耦合、运行时缺位也不崩。

**调度与取消**：并行子调用按工具声明的并发模式分组——同组并行、组间按依赖串行；来自回合的取消信号与工具自身的取消语义在执行器处融合为一条 `AbortSignal`，半途取消的调用以"被跳过"事件落账而不是无声消失。包内的 `testing.ts`/`invariant.ts`/`schema.ts` 分别提供测试基建、不变量检查与 schema 公共面，是这 1937 行的配套骨架。

## 外部连接

包内直接依赖：`json-schema.ts`、`presentation.ts`、`ptc.ts`、`py-types.ts`、`ts-types.ts`；`invariant.ts`、`ptc.ts`、`schema.ts`、`testing.ts` 反向引用本入口。包外消费者按能力缝三角色（Service Definition / Provider / Consumer）组织：本包是工具缝的服务端，`tool-bash` 是 shell 缝的 Consumer 但在这里注册工具，`mcp-client/tools.ts` 的桥把外部工具注册进来，subagent 把父工具集投影给子会话。agent-loop 的 `executeToolCalls` 是调用侧入口。

## 数据流

注册期：`defineTool` 造定义 → `register` 进全局层或作用域层 → schema 白名单校验通过后面向模型可见。调用期：模型 tool_call → 按当前作用域解析工具（遮蔽优先）→ 参数 JSON Schema 校验 → pre（观察）→ guard（审批/升级判定）→ around（包装执行）→ 执行体运行（并行子调用经调度器分组，取消信号融合进执行）→ post（结果观察）→ result 规范化 → 工具结果事件 append 进会话日志（由 tool-calls 侧落账）。渲染期：SDK 渲染器把注册表投影成 TS/Python 类型面。

## 设计决策

**分层遮蔽而非白名单复制**：子作用域不是"复制一份工具清单再增删"，而是压一层上去——祖先层的注册自然可见，同名被近层遮蔽。这让子代理、会话局部工具的策略表达变成 O(1) 的层压叠，也和 dsh-scope"注册向下"共用同一套数据结构。

**保留名 `run_code`**：内置代码执行与用户工具的命名空间从机制上隔离，避免"注册了个同名工具顶掉了 run_code"这类静默劫持。

**管线分段**：观察（pre/post/around）、授权（guard）、执行三者分离，任何一层可以独立测试与替换；审批用 type-only import 保持可选，测试与最小部署不必拉进整套交互能力。

**schema 校验双点**：注册时验证"可表达性"（模型面约束），执行前验证"值合法性"——前者保护协议，后者保护执行体。

**SDK 渲染器内嵌**：两个 SDK 的工具类型从工具注册表直接生成，杜绝"SDK 类型落后于 schema"的漂移。

## 新人提示

入门练习：用 `defineTool` 写一个玩具工具，分别在全局与 scope 注册，观察遮蔽效果——这一步做完，"工具没生效"类问题的排查直觉就有了（第一反应查作用域层，第二反应查保留名与 schema 校验）。读源码建议顺序：注册与解析 → 执行管线 → 调度与取消；呈现模式放最后，它不影响行为只影响展示。给工具加"模型面文档"时记住仓库规则：schema 与描述只含任务相关概念，不出现 UI、传输或实现词汇——模型读的不是给程序员看的 README。改执行语义时，把拒绝路径的测试一并补上，"执行器处拒绝"是被明文要求的 enforcement 位置。最后一个定位技巧：HMR 卸载后工具仍在，多半是 disposer 没随作用域排空——"注册是 effect"这条规则配上专门的 HMR 安全测试，就是防这件事的。
