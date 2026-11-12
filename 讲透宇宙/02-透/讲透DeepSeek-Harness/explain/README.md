# 讲透DeepSeek-Harness · 源码精讲索引（explain/）

本目录收录 deepseek-harness 仓库 14 个最重要源码文件的中文精讲，每篇 1500+ 字（纯中文字符计）、固定六节结构：**角色定位 / 内部结构 / 外部连接 / 数据流 / 设计决策 / 新人提示**。全部内容基于真实源码阅读（commit `76fda72`，版本 0.1.2-rc.1）与 `.understand-anything/knowledge-graph.json`（3368 节点 / 5160 边）的依赖关系核实，每篇开头附原文件相对路径链接。

仓库根：`~/ai/explore/deepseek-ai/deepseek-harness`

## 推荐阅读路径

**主干五篇**（入口 → 原语 → 会话 → 引擎 → 工具）：1 → 2 → 3 → 4 → 5，读完即掌握"一次 tool_call 的完整生命线"。之后按兴趣选读：模型链（8 → 9）、执行安全链（10 → 12 → 13，bash 工具 → 本地沙箱 → Landlock 原生层）、扩展与外部（6 → 7 → 11）、Python 侧（14）。

## 篇目总表

| # | 精讲 | 原文件 | 层 | 一句话 | 字数 |
|---|------|--------|-----|--------|------|
| 1 | [bin.md](bin.md) | `apps/cli/src/bin.ts` | CLI 入口 | dsh 命令行入口：50 行分发壳，三种模式全动态 import，`satisfies never` 穷尽性护栏 | 1532 |
| 2 | [core-scope.md](core-scope.md) | `packages/core/scope/src/index.ts` | core 基础原语 | 作用域原语：不透明 ScopeKey + 一张父链表驱动"注册向下、事件向上"双向语义 | 1507 |
| 3 | [core-session.md](core-session.md) | `packages/core/session/src/index.ts` | core 会话内核 | 事件溯源会话：append-only 日志、header/surface 折叠、fork 边界校验、中断回合修复 | 1549 |
| 4 | [agent-loop-agent.md](agent-loop-agent.md) | `packages/core/agent-loop/src/agent.ts` | core 回合引擎 | ReactLoopAgent：ReAct 循环心脏，inbox 并入（steer/followup/inject/cancel）+ phase 状态机 + 每请求重派生 | 1550 |
| 5 | [tools-runtime.md](tools-runtime.md) | `packages/core/tools/src/index.ts` | core 工具运行时 | ToolRuntime：分层遮蔽注册、pre/guard/around/post/result 管线、并行子调用调度、TS/Py SDK 渲染 | 1527 |
| 6 | [goal.md](goal.md) | `packages/goal/goal/src/index.ts` | 会话域服务 | GoalService：七个 CAS 变更动词的目标状态机 + fold 与服务分离 + continuation 进程内激活 | 1505 |
| 7 | [child-agent.md](child-agent.md) | `packages/subagent/subagent/src/child-agent.ts` | subagent 组合 | 子代理派生唯一入口：委托深度预算、策略种子传递、scoped 组装、type-only 机会式依赖 | 1502 |
| 8 | [llm-runtime.md](llm-runtime.md) | `packages/llm/llm/src/index.ts` | LLM 服务 | LlmRuntime：适配器注册表 + 路由冻结 + waterfall 可拦截流式调用 + BlockAssembler 组装 | 1533 |
| 9 | [deepseek-adapter.md](deepseek-adapter.md) | `packages/llm/llm-deepseek/src/adapter.ts` | LLM Provider | DeepSeekAdapter：transport-only 的 fetch+SSE 运输层，thunk 连接事实、逐请求 token、图像卸载、错误码公民 | 1521 |
| 10 | [tool-bash.md](tool-bash.md) | `packages/shell/tool-bash/src/index.ts` | shell Consumer | 模型手中的 bash 工具：升级审批（canonicalPath）、后台作业所有权移交、DSH_ENV_PREFIX 环境面 | 1534 |
| 11 | [mcp-tools.md](mcp-tools.md) | `packages/mcp/mcp-client/src/tools.ts` | MCP 桥 | MCP 工具桥：确定性公共名（raw 只上线、永不反解析）、re-sync、图像双重准入 | 1523 |
| 12 | [sandbox-local.md](sandbox-local.md) | `packages/sandbox/sandbox-local/src/index.ts` | 沙箱 Provider | 本地沙箱：bwrap→Landlock / Seatbelt / ACL runner 链，探测一次缓存，fail-closed 不裸跑 | 1526 |
| 13 | [landlock-main.md](landlock-main.md) | `native/landlock-run/packages/entry/src/main.c` | native 执行层 | 自限制后 exec 的 Landlock 启动器：纯 C11 + musl 静态，allow-list 默认拒绝，失败退出码 125 | 1549 |
| 14 | [python-client.md](python-client.md) | `python/sdk/src/deepseek_harness/client.py` | Python SDK | HarnessClient：stdio 换行分隔 JSON-RPC 的同步传输核心，双守护线程、按 id 路由、三段超时 | 1547 |

**合计：14 篇 / 21405 字**（East Asian 宽字符计数，不含 ASCII 标识符与标点）。

## 阅读公约

- 每篇开头的"原文件"链接指向仓库真实路径，可对照源码读；
- "外部连接"节的依赖关系来自 knowledge-graph 的 imports 边与源码 import 语句双重核实；
- 文中函数/类/常量名均出自源码原文，未做臆造；仓库存量行为与作者推断以"值得/建议/应当"等措辞区分。
