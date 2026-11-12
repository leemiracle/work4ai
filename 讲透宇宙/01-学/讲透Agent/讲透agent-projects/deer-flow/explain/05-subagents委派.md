# 05 · subagents 委派：registry、双线程池执行器与 task 工具

## 角色定位

`deerflow/subagents/` 实现"委派"能力：lead agent 通过 `task` 工具把子任务交给独立上下文的子 agent 跑，保护主对话上下文不被冗长探索污染。与多智能体编排不同，这里是**单层委派**——子 agent 拿到的工具集被显式切断 task 工具（防递归嵌套），架构上是 Claude Code 式的 lead/subagent 二级结构。四个组件：SubagentConfig（配置载体）、builtins（两个模块级常量工厂）、registry（查询面）、SubagentExecutor（执行引擎），外加 tools/builtins/task_tool.py 的入口工具。

## 内部结构

**SubagentConfig**（config.py:6）：dataclass 八字段——name/description/system_prompt 三文案，`tools` 白名单（None=继承全部），`disallowed_tools` 默认 `["task"]`（:25，防嵌套是默认姿态），`model="inherit"` 继承父模型（:26），`max_turns=50`（:27），`timeout_seconds=900` 即 15 分钟（:28）。

**内置双子代理是模块级常量**，不是类也不是注册调用：`bash_agent.py:5` 的 `BASH_AGENT_CONFIG`——描述"命令执行专家"、system_prompt 内嵌 guidelines/output_format/working_directory 三段，工具白名单锁死五个沙箱工具（bash_agent.py:42），disallowed 再加 ask_clarification/present_files（:43，子代理不许向用户提问/展示文件），max_turns=30（:45）。`general_purpose.py:5` 的 `GENERAL_PURPOSE_CONFIG`——tools=None 继承全部（:43）、max_turns=50（:46），prompt 明示"DO NOT ask for clarification"（general_purpose.py:24）。两者都靠 dataclasses 的不可变常量性质在 import 期即定型；`builtins/__init__.py:12` 的 `BUILTIN_SUBAGENTS` dict 是唯一注册表。

**registry**（registry.py:12）：`get_subagent_config` 先查内置 dict（:21），再延迟 import `deerflow.config.subagents_config`（:26，注释明示避循环）应用 config.yaml 的 timeout 覆盖，经 `dataclasses.replace` 生成生效副本（:32）——内置常量本体永不被改写。`list_subagents`/`get_subagent_names` 只是浅包装（:37-52）。

**SubagentExecutor**（executor.py:123，约 300 行的核心类）：构造期完成工具过滤——`_filter_tools`（:78）先白名单后黑名单两道（:96-103），模型经 `_get_model_name` 解析 "inherit"（:108-120）。`_create_agent`（:164）每次执行新建 agent：`create_chat_model(thinking_enabled=False)`（:167，子代理关思考省钱），函数体内延迟 import `build_subagent_runtime_middlewares`（:169，避循环）复用主 agent 的共享基座（ThreadData+Sandbox+ToolError 三环，:172），`create_agent(..., state_schema=ThreadState)`（:174-180）——子 agent 与主 agent 共享同一状态 schema。`_build_initial_state`（:182）把父 agent 的 `sandbox`/`thread_data` 原样透传（:195-199）：**子代理与父代理共用同一个沙箱与同一线程目录**，委派的是上下文不是执行环境。执行核心 `_aexecute`（:203）：`recursion_limit=max_turns` 控制轮数（:232），用 `astream(stream_mode="values")` 而非 invoke（:244）——每个值快照检查最后一条 AIMessage，按 id 去重后 `model_dump` 收进 `result.ai_messages`（:254-266），实现运行中实时可见；终态从消息表倒序找最后一条 AIMessage 提取文本（:279-300），兼容 str/list 双 content 形态（:288-298）。

**双线程池**（executor.py:71-75）：`_scheduler_pool`（3 workers，编排）与 `_execution_pool`（3 workers，实际执行）分离；`execute`（:321）在池线程里 `asyncio.run` 自建事件循环跑 `_aexecute`（:344）——注释钉版三理由：MCP 等异步工具需要事件循环、ThreadPoolExecutor 线程没有现成 loop、外层 try 只兜 asyncio.run 自身失败（:334-342）。`execute_async`（:361）是后台入口：预建 PENDING 结果注册进全局 `_background_tasks` dict（:384-385，`_background_tasks_lock` 保护 :67-68），闭包 `run_task` 提交调度池（:422）：置 RUNNING → 真执行提交执行池并 `future.result(timeout=timeout_seconds)`（:397-400）→ FuturesTimeoutError 时标 TIMED_OUT 并 best-effort cancel（:407-414）。`MAX_CONCURRENT_SUBAGENTS = 3` 定义在本文件（:426），被 SubagentLimitMiddleware 反向 import（subagent_limit_middleware.py:10）。`cleanup_background_task`（:452）只删终态任务防与执行器竞态（:473-486）。

## 外部连接

**task_tool**（task_tool.py:21）是唯一入口：`subagent_type` 用 Literal 锁死两型（:26）；查 config 后拼接 skills 提示段（:68-70）与 max_turns 覆盖（:72-76）；从 runtime 提取父上下文（sandbox/thread_data/thread_id :85-88）与 metadata 里的 model_name/trace_id（:91-95）；**延迟 import `get_available_tools` 并传 `subagent_enabled=False`**（task_tool.py:99-102，注释明示经 barrel 穿透避免循环依赖 + 切断递归嵌套）；`execute_async` 直接以 tool_call_id 作 task_id 便于追踪（:117）。之后是**后端代轮询**模式：`get_stream_writer` 发 SSE 事件 task_started（:130），while True 每 5s 查结果（:132、:182），新 AI 消息逐条发 task_running（:148-162），终态发 task_completed/task_failed/task_timed_out（:165-179）并清理；轮询上限 = timeout+60s 缓冲（:124、:191-195），兜底线程池超时失灵的边缘情况。上游闸门：SubagentLimitMiddleware 在 after_model 截断超额并行 task 调用（agent.py:244-247 条件装配）；conftest.py 对 executor 有 sys.modules mock 先例（CLAUDE.md 语境）。

## 数据流

一次委派的完整链路：模型产出 task 工具调用 → （Limit 中间件先截断超额）→ task_tool 提取父上下文 → registry 取 config（含 yaml timeout 覆盖）→ 组子代理工具集（去 task）→ SubagentExecutor 构造（过滤工具）→ execute_async 注册 PENDING → 调度池闭包置 RUNNING → 执行池新事件循环 astream 逐步产出 → result_holder 实时累积 ai_messages → task_tool 5s 轮询发现新消息即发 task_running SSE → 终态写入 → task_tool 发终态事件、cleanup、返回 "Task Succeeded. Result: ..." 给模型。父 agent 的工具调用全程阻塞在轮询里，但子代理消息经 stream writer 已实时推给前端。

## 设计决策

1. **配置即常量工厂**：内置子代理用模块级 SubagentConfig 赋值而非类继承——tree-sitter/静态分析提取为 0 函数 0 类属预期，运行期零构造开销，override 走 dataclasses.replace 生成副本保常量纯净。
2. **双池分离 + 后端轮询**：LLM 不需要自己轮询（task_tool.py:119 注释"removes need for LLM to poll"），轮询发生在工具内部，SSE 事件同时喂前端进度——一个设计同时解决模型 token 浪费与用户可观测性。
3. **递归防护在两处**：disallowed_tools 默认含 "task"（config 级）+ get_available_tools(subagent_enabled=False)（装配级），双保险。
4. **共享沙箱、隔离上下文**：子代理继承父的 sandbox/thread_data（executor.py:195-199），文件产出直达同一线程目录，但消息表完全独立——委派的收益（上下文隔离）与代价（无父子通信通道，只有初始 prompt 和最终结果）都源于此。
5. **每次执行重建 agent/模型**（executor.py:164-180）：无缓存，子代理生命周期短，缓存复杂度不值。

## 新人提示

- 子代理数量三个上限分布在三处：executor.py:426 常量、中间件 [2,4] 硬钳（subagent_limit_middleware.py:15-21）、config configurable 可调——改并发先看钳制区间。
- `_background_tasks` 是进程内 dict，LangGraph Server 重启即丢，task_tool 对 "Task disappeared" 有显式处理（task_tool.py:135-139）。
- 子代理 max_turns 经 recursion_limit 实现（executor.py:232），语义是图步数而非 LLM 调用数，粗估时记得乘 2。
- 新增内置子代理三步：builtins 下建常量文件、进 BUILTIN_SUBAGENTS dict、task_tool 的 Literal 与工具描述同步——漏 Literal 会直接 Unknown subagent type（task_tool.py:63）。
