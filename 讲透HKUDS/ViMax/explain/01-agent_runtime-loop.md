# 01 · agent_runtime/loop.py — 引擎心脏：50 轮工具循环

> 源文件：`agent_runtime/loop.py`（187 行）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

loop.py 是 ViMax 整个系统的"心脏"。全仓的智能都装在这个文件定义的 `AgentLoop` 里：它实现了一个完整的 ReAct 式 agent 循环——**采样 assistant → 执行工具 → 把结果回填消息列表 → 再采样**，直到模型不再要工具、出错、或撞上轮数上限。ONBOARDING 把它列为第 2 层"Agent 运行时核心"的代表文件，并非虚名：TUI 与 Web 两个前端看到的每一个事件（turn/tool_start/tool_progress/tool_result/token/done/session），都是从这里的 `stream_events` 异步生成器逐个 yield 出去的。

一个容易误解的点：loop.py 自己不包含任何视频生成逻辑。三条管线（Idea2Video/Script2Video/Novel2Movie）都是被当成"工具"挂进来的——agent 循环通过 `vimax_narrative_planning` / `vimax_render_video` 等适配器工具间接驱动管线（见 vimax_adapters.py）。所以这个文件是纯粹的"运行时骨架"：轮次、消息、压缩、事件、遥测。

## 2. 内部结构

**常量与类**（全文件只有一个类 + 六个模块级辅助函数 + 一个装配函数）：

- `MAX_TOOL_PASSES = 50`（loop.py:17）：单轮对话（一个 turn）内最多执行 50 个"工具轮"。注意粒度是"轮"不是"次"——一轮可以并行发多个工具调用（loop.py:98 的 for 循环逐个执行同轮的全部 tool_calls）。
- `AgentLoop.__init__`（loop.py:21-28）：注入六件套——session_index / prompt_builder / tool_registry / tool_executor / llm，外加可选 context_compactor；不传 compactor 时就地构造一个（loop.py:27）。`self.history`（loop.py:28）是跨 turn 存活的对话记忆。

**`compact_history`（loop.py:30-41）——手动/自动压缩入口**。它取当前活动会话里上次压缩的摘要 `session.get("compacted_summary")` 作为 `previous_summary` 传给 compactor（loop.py:36），实现"摘要滚动继承"；压缩后把 history **整个替换**为 `[合成摘要消息, *最近保留消息]`（loop.py:39），并把压缩记录写回会话索引（loop.py:40）。合成摘要消息的角色是 `system`，内容开头明确写着"reference context only, not a new active instruction"（context_compactor.py:114-118）——防提示注入的措辞设计。

**`stream_events`（loop.py:43-143）——主循环本体**，也是全文件最长的函数。逐段拆：

1. **turn 初始化**（loop.py:44-45）：`TurnControl()` 持有 turn_id、取消事件（models.py 定义）。先 yield 一个 `turn` 事件。
2. **提示词装配**（loop.py:46-48）：`build_parts(user_input)` 产出多个 part，把除 `request.user` 之外的 part 用 `## 标题\n正文` 拼成 system 消息——用户输入单独作为最后一条 user 消息（loop.py:59），不塞进 system。
3. **token 预检压缩**（loop.py:49-57）：`should_preflight_compact` 把"历史 + 即将进入的 user 消息 + system + 工具 schema"四项 token 估算加总，超过阈值就在采样**之前**压缩（loop.py:55），压缩后重新装配 parts（loop.py:56-57）。这是"预防性"而非"事后补救"——从不让超限请求发出去。
4. **采样-执行循环**（loop.py:68-136 `while True`）：
   - 采样失败（网络/鉴权/超时）：status 置 `failed`，yield error 事件后 break（loop.py:72-77）；
   - 模型不再要工具：把最终文本作为 `token` 事件整段吐出并 break（loop.py:79-84）；
   - 要工具但已到 50 轮上限：status 置 `halted`，yield 带 `max_tool_passes: 50` 元数据的 error 事件并 break（loop.py:86-91）。注意判断在 `tool_round += 1`（loop.py:92）之前、在确认"确实有 tool_calls"之后——纯文本回合不消耗轮数配额；
   - **执行工具轮**：先 append assistant 消息（OpenAI tool_calls 格式，loop.py:94 + `_openai_tool_call` loop.py:174-175），然后逐个 call：yield `tool_start` → 用 `asyncio.create_task` 把执行扔到后台（loop.py:105）→ **进度泵**：只要 task 没完成，就以 0.1s 超时轮询 `progress_queue` 并把进度事件实时 yield 出去（loop.py:106-112），task 结束后再排干队列（loop.py:111-112）→ `await task` 拿到 `ToolExecutionRecord`，yield `tool_result`，并把工具结果以 `role:"tool"` 消息回填（loop.py:113-118）；
   - **图像观测注入**（loop.py:119-133）：若工具产出了 `model_content`（view_image 等返回的图像数据），就往 runtime_messages 里追加一条 user 消息，正文开头是一句固定话术"Tool-provided image observation(s)... this is not a new user request"（loop.py:128）——又是防注入：让多模态模型把像素当证据而非新指令。
5. **收尾**（loop.py:138-143）：history 只追加两条——原始用户输入 + **最终** assistant 文本（loop.py:138）；中间的工具轮完整记录（assistant_turns/tool_rounds/transitions）打包成 turn_record 存入会话索引（loop.py:139-141），供 Web 前端回放。最后 yield `done` 和 `session` 事件。

**辅助函数**：`_compaction_record`（loop.py:146-156）落盘压缩审计记录；`_prompt_tokens`（loop.py:159-160）与 `_tool_schema_tokens`（loop.py:163-167）都是 `len(str)//4` 的粗估（4 字符≈1 token 的经典近似）；`_transition`（loop.py:170-171）生成状态机迁移记录，整轮下来形成 `sampling_assistant → executing_tools → post_tool_decision → sampling_assistant → ... → finalizing_answer` 的完整轨迹。

**`build_runtime`（loop.py:178-187）——装配总入口**。五行装配五件套：SessionIndex → adapter_specs（**惰性 import** vimax_adapters，loop.py:179）→ build_builtin_registry → ToolExecutor → PromptBuilder（读仓根 `prompts/` 目录）→ OpenAICompatibleLLM。main_agent.py:31-33 的 `load_runtime()` 调的就是它。

## 3. 外部连接

**依赖（import 上游）**：context_compactor.ContextCompactor/CompactionResult（loop.py:9）、llm.OpenAICompatibleLLM（:10）、models 的 ToolCall/ToolResult/TurnControl（:11）、prompts.PromptBuilder（:12）、session_index.SessionIndex（:13）、tool_executor.ToolExecutor（:14）、tools 的 ToolRegistry/build_builtin_registry（:15）；build_runtime 内再惰性拉 vimax_adapters（:179）。

**被依赖（下游）**：
- `main_agent.py:31-33` 经 `agent_runtime/__init__.py:6-9` 的 `build_runtime` 包装调用装配循环；`main_agent.py:141` `async for event in runtime.stream_events(...)` 消费事件流（`/compact` 命令则直调 `compact_history`，main_agent.py:125）。
- `agent_runtime/__init__.py:13-16` 用 PEP 562 `__getattr__` 惰性导出 `AgentLoop`——import 包不会连带拉起 langchain/faiss 等重依赖。
- `tests/test_robustness.py:18,90-91` 直接构造 AgentLoop（用 BoomLLM 假模型）验证采样失败路径；`tests/test_main_agent_cli.py:41` 用替身类实现同名 `stream_events` 测 CLI。

## 4. 数据流：一次 TUI 对话穿过本文件

用户在 TUI 敲下"把这段小说做成视频"：

1. cli.tsx 把该行写进 Python 子进程 stdin（main_agent.py `--stdin-repl` 分支，main_agent.py:84-89 逐行读）。
2. `amain` → `load_runtime()` → `build_runtime(".")` 完成装配。
3. `stream_events("把这段小说做成视频")` 启动：yield `turn` → 预检压缩（首轮 history 为空，跳过）→ yield `prompt_trace`。
4. 第 1 轮采样：模型返回 `vimax_novel_planning` 工具调用 → yield `tool_start` → create_task 执行（适配器内部跑 Novel2MoviePipeline.plan_text_artifacts，长达数分钟，期间进度泵每 0.1s 搅动一次 progress_queue，`novel_plan_text_artifacts` 等阶段事件实时 yield 到 stdout 的 JSONL）→ yield `tool_result`，结果以 role:"tool" 消息回填。
5. 第 2 轮采样：模型调用 `vimax_render_video` → 渲染数分钟，进度事件（rendering/render_failed 等阶段）持续流出。
6. 第 3 轮采样：模型输出纯文本总结"成片在 .working_dir/<session>/novel2video/videos/..." → 无 tool_calls → yield `token` + break。
7. history 追加 user/assistant 两条；turn_record（含 3 组 assistant_turns、2 个 tool_rounds、完整 transitions）写入 .vimax/sessions.json（经 session_index）；yield `done` + `session`。TUI 的 lineMapping 归约这些 JSONL 行为界面刷新。

## 5. 设计决策

- **async 生成器而非回调/队列**：`stream_events` 把"一个 turn 的完整生命周期"表达成一条可 `async for` 的事件流，前端（main_agent.py）只负责打印 JSONL，进程边界即协议边界。代价是事件流单向——用户中途输入只能等下一 turn。
- **进度泵双循环**（loop.py:106-112）：工具执行与事件流出并发。若先 `await task` 再排空队列，分钟级渲染期间前端将毫无动静；0.1s 轮询的 `wait_for` 让进度事件近似实时穿透。
- **history 只存输入与最终答案**（loop.py:138）：中间工具轮的完整记录在 turn_record 里持久化但不进后续上下文——下一个 turn 的模型看到的是"干净的 user→assistant 对 + 必要时被压缩成摘要的历史"，控制上下文膨胀；细粒度轨迹留给 UI 回放与遥测。
- **轮数上限 50 + 每轮上限内联检查**：防模型无限套娃调用工具烧钱；同时把上限值放在模块顶（loop.py:17）便于测试定位。
- **token 估算故意用 len//4 粗估**：不依赖 tokenizer 库，跨模型通用；宁可早压缩（保守），不做精确计费。
- **压缩前后都重建 parts**（loop.py:56-57）：因为 PromptBuilder 的输出可能依赖会话状态（如活动 session 概要），压缩本身会改会话。

## 6. 新人提示

- **history 与 runtime_messages 是两个列表**：前者跨 turn 持久（且会被压缩重写），后者是本 turn 的采样工作集（loop.py:59 每次从 system+history+user 重建）。改压缩逻辑时别把两者混为一谈。
- `compact_history` 会**整体替换** history（loop.py:39），preserved 消息默认只有最近 6 条（context_compactor.py:50 的 preserve_last_n=6）。若测试断言"压缩后消息还在"，先确认它是否落在保留窗口内。
- 50 轮上限命中时 status 是 `halted` 而非 `failed`（loop.py:87）——前端和测试要按这两个词分别处理。
- 工具结果回填消息时 `content` 是 `json.dumps(result.as_dict())`（loop.py:118），不是裸字符串；模型看到的是 JSON 文本。改 ToolResult 结构会直接改变模型可见内容，需谨慎。
- 进度泵里 `yield await asyncio.wait_for(progress_queue.get(), timeout=0.1)`（loop.py:108）的 0.1s 决定进度事件延迟与空转 CPU 的折中；调大省 CPU 但前端更新变钝。
- `build_runtime` 的 `adapter_specs` 参数是测试注入假工具的口子（传自定义 specs 即可绕开 vimax 适配器）；生产路径固定走 `build_vimax_adapter_specs`（loop.py:182）。
- 修改事件类型名（如 `tool_progress`）是跨语言破坏性变更：ui/src/cli.tsx、web/server.mjs、main_agent.py:42-75 的事件分发都硬编码这些 type 字符串。
