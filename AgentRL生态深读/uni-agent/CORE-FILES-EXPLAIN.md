# uni-agent 核心文件深解（CORE-FILES-EXPLAIN）

> 与 `ONBOARDING.md` 配套：对其提到的每个代码文件做深解。引用格式 `文件:行号`，行号以本深读快照（2026-08-17）为准。

---

## 一、Gateway 接入层（灵魂）

### 1. uni_agent/gateway/gateway.py（286 行）

**职责**：Thin FastAPI/Ray actor 层——路由、能力门、会话所有权。文档首行即声明分工："actor 拥有路由/能力门/每会话 GatewaySession；provider adapter 拥有 wire↔内部翻译与响应封套"（gateway.py:1-6）。

**关键类与函数**：

- `_GatewayActor.__init__(config: GatewayActorConfig, backend)` (:63-88)：取 Ray 节点 IP、持 backend（LLM 客户端）、构造共享 `MessageCodec`、解析采样参数白名单（默认 `{temperature, top_p, top_k, max_tokens, stop}`，:41）、建 `self._sessions: dict[str, GatewaySession]` 与 FastAPI app。
- `_register_routes()` (:90-147)：注册三个模型面端点——`POST /sessions/{session_id}/v1/chat/completions`(:123)、`POST /sessions/{session_id}/v1/messages`(:131)、`POST /sessions/{session_id}/reward_info`(:139)；两个异常处理器把错误体按路径尾巴塑形成 OpenAI 或 Anthropic 形状（:93-121），未捕获异常也返回 provider 可解析的错误体（保 SDK 兼容）。
- `_handle_openai_chat_completions(session_id, payload)` (:161-185)：404 未知会话 → `openai_to_internal` 降维（合并会话级信任采样默认 + 白名单键）→ `_validate_sampling_params`（max_tokens 必须正整数，:46-51）→ `session.run_generation(internal, self._backend)` → 按 `payload["stream"]` 选 `openai_stream_response`（伪 SSE）或 `openai_build_response`（JSON）。Anthropic 版对称（:187-211）。
- `create_session(session_id, metadata, sampling_params) -> SessionHandle` (:234-258)：要求已 start、拒绝重复 id；handle 的 base_url 即 `{server}/sessions/{id}/v1`、reward_info_url 为兄弟端点；GatewaySession 以 handle+codec+长度预算构造。
- `start()/shutdown()` (:213-232)：用 verl 的 `run_uvicorn` 起服务，IPv6 感知的 base_url 拼接。
- 生命周期转发：`finalize_session`(:265) 取轨迹并删会话、`abort_session`(:272) 幂等、`get_session_state`(:280) 暴露 snapshot。
- 模块底：`GatewayActor = ray.remote(_GatewayActor)`(:286)——类即 actor 句柄。

**上下游**：上承 `GatewayManager`（manager.py:46-55 remote 实例化）与 `debug_launcher.py`（examples/gateway/debug_launcher.py:21 直接用 `_GatewayActor`）；下接 adapters 与 GatewaySession；backend 由外部注入（不在 config.py，见 config.py:4-6 注释——codec/session 边界看不到 LLM 客户端生命周期）。

**工程手法**：①"薄 actor + 厚 session"——所有业务状态与轨迹逻辑下沉 GatewaySession，actor 只做协议路由，可测性高（tests/uni_agent/gateway/test_gateway_actor_on_cpu.py）；②错误体按 provider 塑形，黑盒 SDK 永远可解析。

### 2. uni_agent/gateway/manager.py（116 行）

**职责**：驱动侧管理器——拥有 gateway actor 池并把会话路由到正确 actor（manager.py:1-6）。

**关键类**：

- `GatewayManager.__init__(llm_client, gateway_count, gateway_actor_config)` (:25-58)：`gateway_count>0` 校验；取存活且有 CPU 的 Ray 节点，用 `NodeAffinitySchedulingStrategy(soft=True)` 轮询（`i % len(node_ids)`）放置 actor，注释明说防 Ray 默认 PACK 全挤驱动节点、镜像 verl AgentLoopWorker 的放置策略(:39-44)；`ray.get([...start.remote()])` 同步起服。
- `_select_gateway_index()` (:60-63)：`min(active_sessions_per_gateway)` 最小负载。
- `create_session` (:75-92)：**先同步占位计数再 await**——注释解释：同一事件循环上并发创建若 await 后再计数，全部协程读到相同旧值，min 会把整批灌进最低下标 actor；失败则回滚计数。这是异步代码里典型的"check-then-act 竞态"防御。
- `finalize_session/abort_session` (:94-107)：remote 调用后清路由与计数；`shutdown` 并发 gather。

**上下游**：被 `framework/entry.py:51-55`（build_gateway_manager）与 `framework/framework.py`（generate_sequences 里 create/finalize/abort）调用。

### 3. uni_agent/gateway/config.py（56 行）

**职责**：`GatewayActorConfig` 冻结 dataclass——tokenizer / processor / tool_parser_name / apply_chat_template_kwargs / 采样白名单 / vision 提取器 / prompt_length+response_length（两者都设时其和为轨迹总容量）/ enable_last_assistant_rollback（默认 True）。`__post_init__` 校验类型与正性（:47-56）。**后端刻意不进配置**：由 GatewayManager 单独注入（config.py:3-6）。

### 4. uni_agent/gateway/session/session.py（829 行，全库最厚）

**职责**：每会话状态、生成封套与生命周期（session.py:1）。

**关键数据结构**：

- `SessionPhase`(:21-33)：ACTIVE/FINALIZED/ABORTED 三态。
- `TrajectoryBuffer`(:35-62)：prompt_ids + response_ids/response_mask/response_logprobs（1=模型输出，0=续写上下文）+ routed_experts（MoE 路由，后端每轮全量重 prefill 故整体替换而非累积，:45-49 注释）+ generation_versions（每次生成记 `(min,max)_global_steps` 版本标；回滚连带删除最后一标）。
- `ChainState`/`MaterializedChain`/`LastAssistantStart`(:65-97)：并发请求在一个会话里分叉出多条线性链；LastAssistantStart 快照链在"最新 assistant 之前"的各长度。
- `EncodedData`(:99-142)：prepare 与 commit 之间的会话私有交接物（buffer/context_ids/采样参数/多模态/容量耗尽标志/链选择与回滚计数）。
- `GenerationOutcome`(:145-163)：业务结果（assistant_msg/finish_reason/prompt_tokens/completion_tokens）——session 吐业务对象而非 HTTP dict，序列化留给 actor+adapter。

**关键函数**：

- `run_generation(request, backend)` (:218-326)：核心两段锁协议——①锁内 prepare（可触碰 codec/多模态状态）；容量耗尽则提前返回空 assistant + finish_reason="length"；预留 chain_id 防并发写；②**锁外** `backend.generate(request_id, prompt_ids, sampling_params, image/video)` 拿 token_ids；把 response_ids/mask=1/logprobs 追加进 buffer（logprobs 长度强校验，:280-288）；③重新拿锁 decode（tool-call 解析须与会话其他操作串行）+ `_commit_generation_to_chain`；finally 里 `asyncio.shield` 释放链预留。同会话并发请求按后端完成序提交，框架对 `session_trajectories[-1]` 打分广播——并发兄弟共享一个奖励目标（:228-231 注释）。
- `_prepare_generation_inputs` (:384-530)：①对来消息链算 SHA256 前缀哈希序列；②`_select_chain` 找可复用链（工具 schema 相同 + 前缀哈希匹配）；③选中则增量编码：`encode_incremental(增量消息)` 追加为 mask=0 token；④**last-assistant 回滚**（:416-447）：请求改写了链上最新 assistant 时，从 `last_assistant_start` 切回——删 response 尾巴/对应版本标/多模态尾部，校验存储轨迹确实以 assistant 前缀（turn_separator+generation_prompt）结尾再削掉前缀重编码（:436-441），并统计丢弃的可训练 token 数；⑤容量钳制：`max_tokens = min(请求值, 剩余容量)`（:501-508）。
- `_select_chain` (:532-584)：候选 = 未被预留 + 工具 schema 相同 + assistant 起点小于来消息长度 + tip 哈希对上；精确前缀匹配优先，否则最深回滚候选唯一时选回滚；平局按 (历史长度, 精确匹配, updated_seq, chain_id) 排序。
- 前缀哈希 (:599-623)：`sha256("uni-agent-prefix-v1\0" + 前哈希 + 消息哈希)` 的链式哈希——O(1) 比较任意前缀等价性，是"增量复用/回滚/分链"正确性的地基。
- `finalize` (:337-353)：物化所有活跃链、按 order_seq 排序、广播 `reward_info` 到每条轨迹。
- `_build_materialized_trajectory` (:778-811)：折叠版本标为轨迹级 `min/max_global_steps`（trainer 的 staleness 指标；无版本则省键回退）。

**上下游**：上承 gateway.py 两 handler；codec 做全部编码；产物 Trajectory 被 framework.py 消费。测试 test_session_multiple_chains_on_cpu.py / test_message_codec_*.py 覆盖链与编解码。

**工程手法**：①两段锁（prepare/commit 锁内、重生成锁外）保并发不牺牲吞吐；②不可变替换式更新 ChainState（`replace()`）避免共享可变状态；③链式哈希做前缀等价判断。

### 5. uni_agent/gateway/session/codec.py（387 行）

**职责**：模型边界编解码——chat template、多模态 processor、tool-call 解析、输出解码（codec.py:1-5）。

**关键函数**：

- `initialize_generation_prompt(processing_class, **kwargs)` (:45-65)：用一条空 user 消息分别以 add_generation_prompt=False/True 渲染再求差，**动态测定** generation prompt token 后缀；若差不是稳定后缀则 raise——把"模板假设"变成启动期断言。
- `MessageCodec.__init__` (:158-182)：持 tokenizer/processor/vision 提取器/tool_parser_name；预计算 generation_prompt 与 turn_separator（verl 的 initialize_turn_separator）。
- `encode_full(messages, tools, ...)` (:267-284)：全量渲染 chat template（add_generation_prompt=True, tokenize=False）再编码。
- `encode_incremental(messages, ...)` (:286-331)：**dummy-user 锚点差分法**——渲染 `锚点+增量` 的完整 prompt 与单独锚点的 prompt，剥掉 turn_separator 后要求前者是后者的前缀（"prefix-stable" 断言），对差量编码。增量中只允许第一条是 assistant（:300-301）。TODO 注释坦承待替换为 continuous-token merging（:303）。
- `decode_response(response_ids, tools, stop_reason)` (:333-366)：有 tool_parser 且带 tools 时，先解码全文→`_extract_tool_calls_with_sglang_or_vllm`（:124-146：SGLang FunctionCallParser 优先，ModuleNotFoundError/异常再落 vLLM ToolParserManager，再失败返回原文；别名表 :34-42 把 qwen3_xml↔qwen3_coder 等对齐）→ 组装 `tool_calls` 消息 + finish_reason="tool_calls"；否则纯文本解码 + `_FINISH_REASON_MAP` 归一（:23-32：eos/matched_stop→stop，length/max_tokens→length）。
- `canonicalize_message_for_prefix_comparison` (:368-387)：剥 tool_call_id/id、把 JSON 字符串参数与 dict 参数归一成同一形状——**让语义相同的不同 wire 写法命中同一条链**。

**上下游**：被 session.py 的 prepare/commit 调用；依赖 verl.utils.tokenizer.chat_template。

### 6. uni_agent/gateway/session/types.py（76 行）

三个契约类型：`InternalGenerationRequest`（TypedDict：messages/tools/sampling_params；注释强调"不是 provider 中立的 block model"，:13-19）；`SessionHandle`（session_id + base_url + reward_info_url，:26-41）；`Trajectory`（:44-76，十个字段：prompt_ids/response_ids/response_mask/response_logprobs/reward_info/reward_score/num_turns/routed_experts/multi_modal_data/extra_fields）——**RL 训练的原子数据单位**，debug_launcher 的 trajectories.jsonl 与 framework 的 TQ 字段都由它展开。

### 7. uni_agent/gateway/adapters/openai.py（220 行）

**职责**：OpenAI Chat Completions wire ↔ InternalGenerationRequest（openai.py:1-4）。

- `openai_to_internal(payload, base_sampling_params, allowed_sampling_keys)` (:169-220)：能力门——`n!=1` 拒、`response_format` 拒、`tool_choice` 仅 auto/none（指定函数拒）；messages 必须非空；`tool_choice="none"` 时丢 tools；采样参数=会话信任默认 ∪ 白名单键覆盖（**合并而非规范化**，:210-214）。
- `_normalize_message/_normalize_tool_calls` (:105-166)：content None→""；tool_calls 的 JSON 字符串参数尽力 parse 成 dict；只保留已知字段（role/content/name/tool_calls/tool_call_id/reasoning_content）。
- `openai_build_response` (:52-64) 与 `openai_stream_response` (:67-102)：**伪流式**——整个 outcome 已完成后，把 reasoning_content/content/tool_calls 拆成 chat.completion.chunk SSE 序列再 `[DONE]`。黑盒 harness 要 stream=true 也兼容。
- `openai_error_body` (:37-49)：状态码→error.type 映射，只列 gateway 实际会发的码（400/409），注释明说没有 auth/限流路径就不假装有。

### 8. uni_agent/gateway/adapters/anthropic.py（552 行）

对称的 Anthropic Messages 适配：`anthropic_to_internal` 降维；`_outcome_to_blocks`(:81-112) 把内部 assistant 组装成 text/tool_use content blocks（tool_use id 缺省 `toolu_` + 随机 hex）；`_STOP_REASON_MAP`(:23-29) stop→end_turn、tool_calls→tool_use；错误体 Anthropic 形状（:47-51 同样只映射实发状态码）。:83-88 注释解释为何不合成 thinking 块——信任边界不做防御性代码，等 decode 产出 reasoning_content 再加。**这是 Claude Code 黑盒接入的协议支点**（Claude Code 只说 Anthropic 协议）。

## 二、Agent 抽象层

### 9. uni_agent/agents/base.py（118 行，四抽象之一）

- `ModelConfig`(:15-59)：OpenAI 兼容端点三件套（base_url 由 runner 在 RL 时填成当前策略服务器、api_key 默认 "EMPTY"——gateway 接受任意非空、model_name）+ 采样三旋钮 + **双层生成预算**：max_total_tokens（整集生成预算=各轮 completion 之和）vs max_tokens_per_turn（每轮 max_tokens）。
- `AgentConfig`(:62-70)：name（注册键）+ model。
- `AgentResult`(:73-86)：output/transcript/info + **finished 三态**——None=不追踪；注释点明"opting out 永不静默把回合标成不可训练"。
- `Agent` ABC(:89-117)：`name`/`config_model` ClassVar、`from_config` 钩子、唯一抽象 `run(*, sandbox, messages) -> AgentResult`——docstring 规定 sandbox 已启动、messages 是 OpenAI chat 形态、agent 自行连 config.model。

### 10. uni_agent/agents/registry.py（67 行）

`AGENT_REGISTRY` + `AGENT_MODULES`（name→module 懒加载表 :21-26：react/claude_code/mini_swe_agent/mem_agent）。`get_agent_cls` 首次使用才 import（:42-52），可选依赖缺失只影响被选中的 agent。`build_agent(config)` = `get_agent_cls(config.name).from_config(config)`(:65-67)。四个注册表（agent/task/tool/sandbox）同构——**命名即组装**是全库一致的扩展语法。

### 11. uni_agent/agents/react/agent.py（205 行，白标杆）

- `ReActConfig`(:25-47)：tools 列表（默认 str_replace_editor + stateful_shell(command_timeout=120) + submit）、max_steps=50、action_timeout、timeout_budget=3（容忍的每集超时次数）。
- `run()`(:56-109)：`Toolbox.from_specs` → `OpenAICompatibleChatModel`（带工具 schema）→ `async with toolbox.entered(retry=3, timeout=60)` 内逐步循环；异常也保留部分 transcript，交给任务层分桶。
- `step()`(:111-205)：一次"问询→分发"回合。终止语义四分类：`finished`（纯文本回复或调用 submit/finish 成功，_FINISH_TOOLS :22）/`token_limit`（总预算耗尽或单轮被截断）/`timeout_limit`（超预算后跳过本轮剩余调用并补 "Skipped" tool 消息保 transcript 完整，:189-200）/`max_steps`。每步详细日志（THOUGHT/ACTION/OBSERVATION）。

**手法**：终止原因而非布尔成功——任务层能区分"没做完"与"做错了"；超时预算让交互式命令的偶发超时不毁整个 episode。

### 12. uni_agent/agents/react/model.py（180 行）

`OpenAICompatibleChatModel`：裸 aiohttp（不用 OpenAI SDK）直打 `{base_url}/chat/completions`；懒建复用 ClientSession（force_close 连接器）；429/5xx 走 `_TransientHTTPError` 重试；`_normalize_messages_for_api` 剥本地簿记字段只留 API 接受的四类字段（:75-80）。轻、零依赖、可长持有——为千并发会话省去 SDK 开销。

### 13. uni_agent/agents/claude_code/agent.py（224 行，黑标杆）

- 模块 docstring(:1-9) 一句讲透架构：Claude Code 说 Anthropic Messages 协议，vLLM 原生或 Gateway 会话都能伺服；**无代理进程**——把 `ANTHROPIC_BASE_URL` 指过去即可，工具调用由服务端解析。
- `_strip_v1`(:59-70)：OpenAI 风格 base 剥尾 `/v1` 得 Anthropic 根（claude 自己拼 `/v1/messages`）；两种传输都覆盖：`http://h:8000/v1→http://h:8000`、`.../sessions/<id>/v1→.../sessions/<id>`。
- `ClaudeCodeConfig`(:73-92)：max_turns=80、disallowed_tools 默认关 Agent/Task/WebFetch/WebSearch/AskUserQuestion（保 rollout 自包含确定）、permission_mode=bypassPermissions、run_timeout=1800。
- `run()`(:101-134)：拆 system/problem（至多两条消息）→ `_ensure_claude`（沙箱内 npm 或 native installer 装 CLI，:137-152）→ `git config --system safe.directory '*'` → `sandbox.exec(argv, env, timeout)` → AgentResult(finished=exit_code==0)。
- `_claude_env`(:188-224)：**模型槽位全 pin**（ANTHROPIC_MODEL/OPUS/SONNET/HAIKU/SUBAGENT 全设同一 served model——否则后台摘要/子代理调用在直连 vLLM 时 404，:205-213 注释）；`IS_SANDBOX=1`（root 下无值守放行）；`NO_PROXY=*`+清空代理；`_CC_QUIET_ENV`(:27-35) 静默化非必要流量。

## 三、Tools 工具层

### 14. uni_agent/tools/base.py（449 行，四抽象之二）

- `ToolResult`(:33-58)：text+status(ok/format_error/error/timeout)；`to_observation(max_length=100_000)` 超长裁剪并注入"请改用 head/tail/grep、不要交互式分页"的引导——**观察即训练信号**。
- 两类异常(:61-75)：`ToolError`=运行期失败→"Error: ..." 观察；`ToolCallFormatError`=调用格式错（未知函数/参数非 JSON 对象）→以 "Invalid action: ..." 措辞回给策略自纠错（措辞与策略训练分布一致，:73-75）。
- `_normalize_json_schema`(:78-118) + `build_function_schema`(:121-130)：Pydantic schema→OpenAI function 参数 schema（去 title、Optional anyOf 折叠、稳定键序）。
- `Tool` ABC(:133-195)：name/description/args_model/config_model（构造 kwargs 的 Pydantic 模型，自动解析进 self.config，:150-160）；`schema()` 默认由 args_model 生成；`start/close` 可选生命周期（懒开通道/close 释放）。
- `register_tool`(:201-219)：注册键与模型面 name 解耦——`stateful_shell` 注册、模型看到 `shell`。
- `Toolbox`(:233-449)：`from_specs`（`[{name, ...kwargs}]` 配置→实例）；`__aenter__(retry=3, timeout=60)` 带指数退避启动、失败回滚已启动工具（:281-297；`entered()` 提供可传参版本 :303-316）；`call(name, args, timeout)`(:348-369) 单一分发口：未知函数/坏参数→format_error 观察、ToolError→error 观察、真 bug 继续抛；`_validate_arguments`(:401-441) **双重校验**：先 pydantic model_validate 再用发布给模型的同一 schema 跑 jsonschema iter_errors——保证"模型看见的约束=强制执行的约束"。

### 15. uni_agent/tools/shell.py（469 行）

- `Shell` Protocol(:50-58) + 双实现：`SandboxShell`(:61-104) 包沙箱原生 `open_shell`；`TmuxShell`(:160-349) **tmux over one-shot exec 兜底**。
- TmuxShell 手法：私有 socket `-S`；命令写文件再 `eval "$(cat ...)"` 注入（绕过 send-keys 参数超长限制，:246-261）；文件捕获协议 `_capture_wrapper`(:128-138) 把 stdout/stderr/rc 落盘、`mv .part` 原子化；`tmux wait -S` 通道信号 + 轮询侧 `timeout N tmux wait` **事件驱动唤醒**（丢失信号最多损失一个有界时间片而非挂死，:279-295）；超时中断三段式 Ctrl-C→Ctrl-Z→`kill -KILL %+`(:317-332)；镜像缺 tmux 自动跨五家包管理器安装（:144-157）。
- `ShellTool`(:418-469)：config=ShellToolConfig（env_vars/command_timeout=180/终端宽高）；`run` 输出 `[exit code]/[stdout]/[stderr]` 格式，超时给"交互式命令永不完成"的引导文案（:375-394）；ANSI 转义与 \r 清洗（:358-362）。

## 四、Task 与 Sandbox 执行层

### 16. uni_agent/tasks/base.py（112 行，四抽象之三）

- `TaskConfig`(:29-65)：sandbox(SandboxConfig) + agent(**多态字段**：`SerializeAsAny[AgentConfig]`，`_resolve_agent` validator 把 `{"name",...}` mapping 经注册表解析成具体子类、保子类字段往返无损，:50-65) + prompt + metadata（**数据集样本就骑在这里**）。
- `TaskResult`(:68-75)：reward（Any，任务自定义）/accuracy/finished/extra_info。
- `Task` ABC(:78-112)：`run()` 无参——样本在 config.metadata、端点在 config.agent.model；base 提供 `build_sandbox/build_agent` 让 runner 保持通用。

### 17. uni_agent/tasks/registry.py（70 行）与 tasks/config.py（79 行）

registry：`TASK_MODULES` 五族懒加载(:22-28)；`get_task` 兼容 config 实例与**扁平 mapping**（训练侧 `extra_info.tools_kwargs.task` 的序列化形态，:54-70)。
config：`TaskConfigResolver`——YAML 文件默认（lru_cache 索引，重名/缺 name 即报错）←样本配置←运行时模型端点，`_deep_merge` 递归合并（:12-25, 57-79）。**同一合成规则服务独立评估与 RL 训练**，这是"推理即训练"在配置侧的落点。

### 18. uni_agent/tasks/swe_bench/task.py（62 行，任务范本）

`SWEBenchTask.run()`(:29-62)：`async with self.build_sandbox() as sandbox:` 内——oracle 模式直接 `git apply` 金补丁(:40-44)；正常模式 `build_agent().run(sandbox, messages)`；随后 `compute_reward(sample, sandbox)`（reward.py 用 swebench harness 在**同一沙箱**跑 FAIL_TO_PASS/PASS_TO_PASS 判 resolved）→ `TaskResult(reward=resolved, accuracy=resolved, finished, extra_info)`。62 行写完一个任务族，展示 Task 层的克制：编排+打分，别的都在抽象里。

### 19. uni_agent/sandbox/base.py（408 行，四抽象之四）

- `SandboxBackend` Protocol(:70-105)：**窄数据面**——exec/exec_shell/read_file/write_file/upload/download/expose_port，刻意排除生命周期；任何结构性满足该协议的对象都能当工具的后端（工具与 provider 解耦的支点）。
- `Sandbox` ABC(:149-408)：控制面 start/stop（abstract）+ 数据面 `_exec` 原语（abstract）——公共 `exec` 包装统一错误策略：超时→`ExecResult(exit_code=-1, "exec timed out...")`；非超时异常探测 `is_alive()`，死沙箱重抛、活沙箱降级 exit_code=127(:262-297)。文件传输 **floor-and-override**：base64-over-exec 打底（read/write :318-334，base64 保二进制完整性）；目录走单 tar 归档过单文件通道（:376-408）；provider 有原生通道就覆盖 upload_file/download_file 这道缝(:360-373)。
- 启动治理：`SANDBOX_STARTUP_TIMEOUT`（默认 600s）+ 每事件循环共享的 `SANDBOX_STARTUP_CONCURRENCY` 信号量（weakref 绑 loop，:127-146，注释解释"每调用新建信号量永远立即获取、限不住任何东西"）；`__aenter__(retry=3)` 退避重试且失败清理(:211-236)。

## 五、训练集成层

### 20. uni_agent/framework/base.py（23 行）

`AgentFramework` ABC：`from_config(*, config, **kwargs)` + `generate_sequences(prompts: TensorDict) -> None`（docstring：跑 agent 会话并把轨迹写 TransferQueue）。23 行定义训练器眼中的整个 agent 框架——verl 与 uni-agent 的全部接缝就这两个方法。

### 21. uni_agent/framework/framework.py（1001 行，训练发动机）

- `_RunnerConfig`(:50-94)：runner_fqn/kwargs/dispatch_mode(inline_async|ray_task)/max_concurrent_sessions/trajectory_selection(all|longest)。
- `OpenAICompatibleAgentFramework.generate_sequences`(:384-428)：校验 uid/global_steps（训练必需）→ `_run_batch_to_tq` → 汇总日志；**全批失败才 raise**(:423-427)。
- 三层并发(:430-574)：batch→每 prompt 一个 task（一个 prompt 失败不拖全批）；prompt→rollout.n 个会话 task（失败只计该 uid 统计）；成功会话写 TQ 后 `tq.async_kv_put(uid, status=finished|failure)`——BaseException 里的控制流异常（CancelledError 等）继续上抛，只有普通 Exception 算隔离失败(:474-482)。
- `_run_session`(:635-736)：会话 id=`session-sample-{i}-rollout-{j}-{uuid}`；日志目录 `step_{global_steps}/{session_id}/`（framework.log/task.log）；ray_task 模式只把 runner 放 Ray 远端，"token 真相、finalize、打分、TQ 写入留在父进程"(:676-688 注释)；异常→abort_session；成功→`_select_session_trajectories`（longest 按 mask=1 数/长度/轮数取最大，:143-170）→打分→落盘 trajectory.json+npz（:757-809，元数据 JSON+token 数组压缩 npz 分离，"在网络盘上这比旧缩进 JSON 小得多快得多"）。
- 奖励双源(:711-731, 811-864)：优先 `_score_from_reward_info`——runner POST 的 reward_info 里 pop 出 reward 作 score、finished 被框架直接消费不算奖励指标；无则 `RewardLoopWorker.compute_score`（随机选 handle，把**最后一条轨迹**包成单样本 DataProto 打分再广播全会话——镜像 verl AgentLoopWorkerTQ 语义，:829-864）；都没有则 rm_scores=0 + 警告。
- `_trajectory_to_tq_field_and_tag`(:910-1001)：组装训练记录——prompts/responses/input_ids/attention/position（无 processor 用 mask 推；有则 processor 感知，:937-945）；`mask_unfinished_episode` 时未完成回合 response_mask/loss_mask 全 0（奖励保留，:925-929）；`rm_scores` 稀疏打在最后一个 response token(:961-963)；`min/max_global_steps` 版本跨度标签供 trainer staleness 度量，缺省回退 dataloader 步（:984-991）。

### 22. uni_agent/framework/entry.py（159 行）

- `build_gateway_manager`(:31-55)：从 verl config 抽 tokenizer/processor/tool_parser（rollout.multi_turn.format）/prompt_length+response_length/rollback 开关 → GatewayManager。
- `build_agent_framework`(:58-75)：`framework_class_fqn` 可换框架实现（默认 OpenAICompatibleAgentFramework）。
- `AgentFrameworkWorker`(Ray actor, :78-95)：构造即 `tq.init()` + 持一个 framework；manager 由驱动侧创建注入（actor 不拥有 gateway actor）。
- `AgentFrameworkRolloutAdapter`(:98-159)：`create()` 工厂（teacher_client 明确不支持即报错）；`generate_sequences` fire-and-forget（trainer 经 ReplayBuffer 异步消费 TQ）；`generate_sequences_and_wait` 阻塞版给独立运行。**零配方胶水**：所有配方 YAML 都写同一个类名（:7-13 docstring 给出一行接入示例）。

### 23. uni_agent/framework/task_runner.py（99 行）

`run_task(*, session, tools_kwargs, ...)`(:17-72)：要求 `tools_kwargs["task"]`（序列化 Task Config）→ `TaskConfigResolver.from_file(task_config_path)` → `resolver.resolve(sample_config, runtime_model={base_url: session.base_url, api_key, model_name})`——**会话端点在这里注入任务**；`get_task(task).run()`；`report_reward=True` 时 `_post_reward_info` best-effort POST `{reward, acc?, finished?}` 到 reward_info_url（失败仅警告，:75-88）。raw_prompt 只为协议对齐被接受但不用（任务自带 prompt，:31-33）。

## 六、Examples

### 24. examples/gateway/debug_launcher.py（707 行）

独立 Gateway 调试器：不训练起 `_GatewayActor`（:21）+ 单外部会话，打印两套连接 URL（Claude Code 用不带 /v1 的根、OpenAI 用带 /v1 的），finalize 后写 trajectories.jsonl / session_metadata.json / debug_snapshot.json（finalize 前的规范化消息史+会话状态快照，用来反解 token 轨迹）。内置 `DebugFakeTokenizer`(:30-59, ord/chr 双射) 与 fake backend（永远返回 "OK" 的 token）——**零 GPU 冒烟**。配套 examples/gateway/README.md 详列 Claude Code 连接的四个坑（/v1、代理、NO_PROXY、max_tokens 钳制）。

### 25. examples/blackbox_recipes/claude_code/claude_code_runner.py（317 行）

自建 runner 范本（harness 无法改环境变量/沙箱网络受限时）：`claude_code_runner`(:230-317) 流程=①`_create_claude_sandbox`（sidecar 工具镜像挂 /opt/claude-code + upstream/proxy_port 隧道 kwargs，:208-227）→②`rewrite_gateway_url` 把会话 URL 改写为沙箱内 `127.0.0.1:<proxy_port>`（:41-50）→③`build_claude_command` 生成一条 shell 命令（环境变量前缀 + conda env + claude argv，:149-205）→④同沙箱 `evaluate_in_env` 评奖→⑤POST reward_info。展示 AgentRunner 契约（framework.py:37-47）的完整自定义实现。

### 26. examples/quickstart/inference/task_config_claude_code.yaml（13 行）

Task Config 最小样例：`swe_bench` + sandbox(provider=modal, runtime_timeout=7200) + agent(name=claude_code, max_turns=200, run_timeout=4800, model: temperature=1.0/top_p=0.95/max_total_tokens=131072)。训练版（examples/quickstart/training/task_config_claude_code.yaml）结构相同——**换 provider/换 agent 就是改几行 YAML**，这是四抽象+注册表设计给出的最终用户体验。

---

## 附：文件行数速查（本快照实测）

| 文件 | 行数 | | 文件 | 行数 |
|---|---|---|---|---|
| gateway/gateway.py | 286 | | tools/base.py | 449 |
| gateway/manager.py | 116 | | tools/shell.py | 469 |
| gateway/config.py | 56 | | tasks/base.py | 112 |
| gateway/session/session.py | 829 | | tasks/registry.py | 70 |
| gateway/session/codec.py | 387 | | tasks/config.py | 79 |
| gateway/session/types.py | 76 | | tasks/swe_bench/task.py | 62 |
| gateway/adapters/openai.py | 220 | | sandbox/base.py | 408 |
| gateway/adapters/anthropic.py | 552 | | framework/base.py | 23 |
| agents/base.py | 118 | | framework/framework.py | 1001 |
| agents/registry.py | 67 | | framework/entry.py | 159 |
| agents/react/agent.py | 205 | | framework/task_runner.py | 99 |
| agents/react/model.py | 180 | | examples/gateway/debug_launcher.py | 707 |
| agents/claude_code/agent.py | 224 | | examples/blackbox_recipes/claude_code/claude_code_runner.py | 317 |
