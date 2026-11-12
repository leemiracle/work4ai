# tool-bash/src/index.ts — 模型手中的 shell：ctx.shell 缝的 Consumer

> 原文件：[`packages/shell/tool-bash/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/shell/tool-bash/src/index.ts)（393 行）

## 角色定位

这是模型看见的那个 bash 工具——`dsh-tool-bash` 插件主体。它注册模型可调用的 `bash` 工具，负责参数校验、沙箱策略解析、升级审批判定、工作目录解析、前台执行与后台作业启动，并把结果规范化为 canonical 输出。

在能力缝（capability seam）的三角色语法里，它是 **shell 能力的模型侧 Consumer**：定义在 `dsh-shell`（Service Definition），实现由沙箱 Provider（如 sandbox-local）提供，本插件站在中间把"模型的工具调用"翻译成"对 ctx.shell 的执行请求"。这个站位意味着它必须懂协议、不必懂沙箱细节——换一个沙箱后端，本文件一行不改。

## 内部结构

**插件形态**：函数插件，`export const name = 'tool-bash'`，`inject = ['tools', 'shell', 'systemPrompt', 'shellEnv']`——声明消费工具注册表、shell 服务、系统提示节与环境面四个注入（函数插件具名导出、无默认导出，是仓库明文的插件出口规则）。

**执行路径**：`apply` 内组装系统提示节（bash 使用说明）、工具 schema 与 execute 路径。execute 时依次：参数校验 → 解析沙箱策略 → 升级判定（见下）→ 解析工作目录 → 前台经 `ctx.shell` 运行，或注册为后台作业。

**升级审批**：`approveEscalation` + `ESCALATION_TARGETS` + `validateEscalationArgs` + `canonicalPath`。命令命中升级目标（需要更多权限的路径/操作）时，先经审批交互获得批准；`canonicalPath` 把目标路径规范化后再比较——防"相对路径/别名/拼接"绕过审批目标匹配。

**后台作业**：后台调用向 `ctx.jobs` 注册，拿到作业 id 后**取消责任移交**——此后取消走 job 通道而非 tool-call 的 signal。生命周期单一拥有者原则的直接体现。

**环境面**：`DSH_ENV_PREFIX` 决定哪些环境变量对模型可见（过滤而非全量透传）。

**结果规范化**：`render.ts` 的 `renderResult`/`renderProcessRead`；`background.ts` 的 `parseExitStatus`/`processOutcome`——退出状态解析与后台进程结局（完成/被杀/失败）映射为 canonical 输出。

**提示节与环境面的组装**：`apply` 里向 `ctx.systemPrompt` 注册 bash 使用说明节——内容只讲任务语义（怎么用命令、后台作业如何查询等待），不出现沙箱实现词汇；`ctx.shellEnv` 注入的是过滤后的环境面。两者共同决定模型对 shell 的认知边界：模型知道自己能跑命令、知道作业语义，但不知道也不需要知道底下是 bwrap 还是 Landlock。

## 外部连接

包内依赖 `background.ts` 与 `render.ts` 两个模块。跨包：`ctx.shell`（Service Definition，本地与 pwsh 等 Provider 实现）；`ctx.tools`（注册进 ToolRuntime，享受分层遮蔽与执行管线）；`ctx.jobs`（后台作业管理）；`ctx.systemPrompt`（提示节注入）；`ctx.shellEnv`（环境面）。上游是 agent-loop 的工具执行编排；审批交互对接 interaction/approval 能力。图谱上本文件无入边（插件由 profile 组合挂载），出边即上述两个本地模块。

插件出口形态本身也是仓库规则的样本：函数插件具名导出 `name`/`inject`/`Config`/`apply`、不得混入默认导出——一旦混用，Loader 会丢弃函数插件的命名空间（仓库有专门的事后剖析记录这个坑）。本文件的四项 inject 正是这个形状的标准示范。

## 数据流

前台路径：模型 tool_call → 参数校验 → 策略解析（该命令在哪个沙箱策略下跑）→ 升级判定：命中 `ESCALATION_TARGETS` 则 `canonicalPath` 规范化 → `approveEscalation` 请求批准（拒绝则工具以拒绝结果收场，不执行）→ `ctx.shell` 前台执行（沙箱内）→ `parseExitStatus` + `renderResult` → canonical 结果 → 工具结果事件落会话日志。后台路径：同前三步 → `ctx.jobs` 注册 → 返回作业 id 给模型（模型可后续查询/等待）→ 作业完成或被取消时 `processOutcome` 结案。环境读取始终经 `DSH_ENV_PREFIX` 过滤面，而非进程全量环境。

## 设计决策

**Consumer 不懂沙箱**：所有平台细节（bwrap/Landlock/Seatbelt/ACL）都在 Provider 那侧。本文件只表达"我要以这个策略跑这条命令"，这让 bash 工具的行为在所有平台一致。

**请求/规范分离**：仓库明文以 `dsh-shell` 为模板——显式的 `resolve(request): Spec` 步骤承担默认值决策，`run()` 里不藏 `?? default`。你在这份代码里看到的策略解析就是那个 resolve 步骤。

**后台所有权移交**：id 返回后取消走 job 而非 tool-call signal——一次异步操作一个生命周期控制者，避免双重取消竞态。

**canonicalPath 先于比较**：审批目标的匹配发生在规范化路径上，把"路径写法绕过审批"这类攻击面压到最小。

**环境前缀过滤**：模型可见的环境是白名单投影，既保护宿主机密，也保证会话重放时环境面确定。

## 新人提示

理解这个文件的最好练习是 trace 一个后台调用的完整生命周期：从 tool_call 进来，到 job 注册、id 返回、模型查询、作业结束、结果落账——走一遍你就同时理解了 tool-bash、jobs 与会话落账三件事。排查"命令没被沙箱包住"先查策略解析给的 spec，再看 Provider 侧（下一篇 sandbox-local）的 runner 选择——问题几乎总在两缝之一。审批不弹出来时，先确认命令目标是否真的命中 `ESCALATION_TARGETS`，以及 `canonicalPath` 之后是否还相等。改工具描述时记住：schema 与说明只写任务相关概念，"沙箱"、"升级"这类实现词汇不该出现在模型面。最后，环境相关的怪问题（模型"看不见"某变量）九成是 `DSH_ENV_PREFIX` 过滤面的预期行为，不是 bug。后台作业还有一条易漏的读取路径：`renderProcessRead` 负责把"读取后台进程输出"这类操作的结果规范化——模型追问作业输出时走的就是它；排查后台相关问题时，把 render 与 processOutcome 两条渲染路径都看一遍。
