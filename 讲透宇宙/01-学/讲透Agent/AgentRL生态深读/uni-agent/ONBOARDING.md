# uni-agent 新人指南（ONBOARDING）

> 深读对象：`~/ai/uni-agent`（github.com/verl-project/uni-agent，约 148 文件，Apache-2.0，2026 年项目）
> 深读日期：2026-08-17 ｜ 管线：work4ai AgentRL 生态深读（/understand --language zh 等效执行）
> 姊妹文件：`CORE-FILES-EXPLAIN.md`（逐文件深解）、`knowledge-graph.json`（结构化图谱）

---

## 1. 一句话定位

**uni-agent = 把任意 agent harness 变成 RL 环境的统一框架。**

只要一个 harness（Claude Code、Mini-SWE-Agent、或你自己写的循环）能把它的模型端点指向 uni-agent Gateway 暴露的 OpenAI/Anthropic 兼容 URL，Gateway 就在"假扮模型服务器"的同时，把每一轮对话沉淀为 **token 级训练轨迹**（prompt_ids / response_ids / response_mask / logprobs / reward），经 TransferQueue 喂给 verl 的 GRPO/GSPO 训练器。官方口号：**request string in, training tokens out**（README.md:23）。

三行展开：

- **黑盒路径**：harness 原封不动跑在沙箱里，只把 `ANTHROPIC_BASE_URL`/OpenAI base_url 换成 Gateway 会话 URL，即可收集轨迹并训练（`uni_agent/agents/claude_code/agent.py:59-70`）
- **白盒路径**：用 `Agent / Tool / Task / Sandbox` 四抽象自己写 agent 与工具，复用同一套评估/训练运行时（`uni_agent/agents/react/agent.py`）
- **规模化**：GatewayManager actor 池 + 1000+ 并发有状态会话 + 异步 rollout + partial rollout（README.md:29-31, 69）

## 2. 架构总览

### 2.1 训练数据流（灵魂图）

```text
verl Trainer (Megatron/FSDP, GRPO/GSPO/...)
   │  prompts(TensorDict: uid / raw_prompt / tools_kwargs / global_steps)
   ▼
AgentFrameworkRolloutAdapter            ← verl 的 agent_loop_manager_class 扩展点
   │  (uni_agent/framework/entry.py:98) 建 GatewayManager + AgentFrameworkWorker
   ▼
OpenAICompatibleAgentFramework.generate_sequences   (framework/framework.py:384)
   │  每个 sample × rollout.n 个并发会话（三层并发隔离失败）
   ▼
GatewayManager.create_session ──► GatewayActor(Ray actor + FastAPI)
   │  (gateway/gateway.py:123-147 三路由)  返回 SessionHandle:
   │    base_url      = http://host:port/sessions/{id}/v1
   │    reward_info_url = http://host:port/sessions/{id}/reward_info
   ▼
Runner（默认 run_task, framework/task_runner.py:17）
   │  TaskConfigResolver: YAML默认 ← 样本配置 ← 会话端点 三层深合并
   │  把 session.base_url 注入 agent.model.base_url（RL 时=当前策略服务器）
   ▼
Task.run()  (tasks/swe_bench/task.py:29)
   ├─ build_sandbox()  ──► Sandbox(local/docker/vefaas/modal/...)
   └─ build_agent()    ──► Agent.run(sandbox, messages)
        ├─ 白盒 ReAct：Toolbox.call() 驱动工具 → 自己 POST /v1/chat/completions
        └─ 黑盒 Claude Code：沙箱内 claude CLI → ANTHROPIC_BASE_URL=会话URL
   ▼
Agent 的每一次模型调用（OpenAI 或 Anthropic 协议）都打到会话 URL
   ▼
GatewayActor 路由 → adapter 降维成 InternalGenerationRequest
   → GatewaySession.run_generation (session/session.py:218)
       锁内 prepare：链匹配(SHA256前缀哈希)/增量编码/容量钳制max_tokens
       锁外 backend.generate（vLLM/SGLang，返回 token_ids+logprobs）
       锁内 decode（tool-call 解析）+ commit（response_mask: 模型=1/续写=0）
   ▼
任务完成 → POST /reward_info {reward, acc, finished}   (task_runner.py:75-88)
   ▼
finalize_session() → Trajectory[]（多链物化 + logprobs + 版本跨度）
   (session/session.py:337-353)
   ▼
framework 打分：runner 回传的 reward_info 优先，否则 RewardLoopWorker 兜底
   → 写 TransferQueue: key = {uid}_{session_index}_{traj_index}
   (framework.py:811-827, 878-908)
   ▼
Trainer ReplayBuffer 异步消费 → 策略更新 → 新权重 → 下一批 rollout（闭环）
```

两条路径的关键区别（docs/source/concepts/gateway-and-trajectories.md:7-28）：
- **外部 API 推理**（Task→Agent→外部模型 API）绕过 Gateway：可用于评估，但拿不到训练轨迹
- **verl 托管推理/训练**走完整链路：推理即训练，同一交互栈
- **Gateway 不是推理引擎**：vLLM/SGLang 产 token；Gateway 只管会话路由、协议转换、轨迹物化

### 2.2 分层与目录表

| 层 | 目录 | 一句话职责 |
|---|---|---|
| Gateway 接入层 | `uni_agent/gateway/` | 灵魂：Ray actor + FastAPI 会话端点、协议适配、链式会话状态机、轨迹物化 |
| Agent 抽象层 | `uni_agent/agents/` | 谁解题怎么启动：base 契约 + react(白盒)/claude_code/mini_swe_agent/mem_agent(黑盒) + registry |
| Task 执行层 | `uni_agent/tasks/` | 一个任务族 = sandbox + agent + 奖励；5 族：swe_bench / swe_rebench / swe_bench_multilingual / terminal_bench / hotpotqa（各有 task.py + reward.py + preprocess.py） |
| Sandbox 层 | `uni_agent/sandbox/` | 隔离执行环境：base 契约 + local / docker / vefaas / modal / openyuanrong providers + registry |
| Tools 工具层 | `uni_agent/tools/` | host 侧工具：base(Tool/Toolbox) + stateful_shell + str_replace_editor + submit + finish |
| 训练集成层 | `uni_agent/framework/` | 与 verl 的接缝：AgentFramework 并发编排 + TQ 写入 + entry 适配器 + run_task 桥 |
| 支撑 | `uni_agent/logging/` `uni_agent/utils.py` | 会话级日志、脱敏 |
| 示例 | `examples/` | gateway 调试器 / quickstart(训练+推理+sandbox) / blackbox_recipes(claude_code) / mem_agent |
| 文档 | `docs/source/` | concepts(概念真经) / quickstart / benchmark |
| 其他 | `verl/`(git submodule，PYTHONPATH=verl) `tests/` `app/`(lark_chat 周边) | 捆绑 verl 源码、单测、小应用 |

## 3. 核心模块清单

### 3.1 Gateway 接入层（gateway/，灵魂）

| 模块 | 职责 | 关键类/函数 | 扩展点 |
|---|---|---|---|
| `gateway.py` (286行) | Ray actor + FastAPI 路由与会话所有权 | `_GatewayActor`：`create_session`(:234)、`_handle_openai_chat_completions`(:161)、`_handle_anthropic_messages`(:187)、`finalize/abort_session`；模块级 `GatewayActor = ray.remote(_GatewayActor)`(:286) | 加新 provider 协议=加一条路由+一个 adapter |
| `manager.py` (116行) | 驱动侧 actor 池与路由 | `GatewayManager`：NodeAffinity 轮询放置(:42-55)、最小负载选 actor(:60-63)、先占位再 await 的 create_session(:75-92) | `gateway_count` 配置池大小 |
| `session/session.py` (829行) | 会话状态机与轨迹物化 | `GatewaySession.run_generation`(:218)、`_prepare_generation_inputs`(:384)、`_select_chain`(:532)、`_extend_message_prefix_hashes`(:599)、finalize(:337) | `enable_last_assistant_rollback` 开关 |
| `session/codec.py` (387行) | 模型边界编解码 | `MessageCodec.encode_full/encode_incremental/decode_response`(:267/:286/:333)、`_extract_tool_calls_with_sglang_or_vllm`(:124) | 换模型=换 tokenizer/processor/tool_parser_name |
| `session/types.py` (76行) | 数据契约 | `InternalGenerationRequest`、`SessionHandle`、`Trajectory` | Trajectory.extra_fields 自带扩展位 |
| `adapters/openai.py` (220行) | OpenAI wire↔internal | `openai_to_internal`(:169) 能力门+采样白名单；`openai_stream_response`(:67) 伪 SSE | 新采样参数加入白名单 |
| `adapters/anthropic.py` (552行) | Anthropic wire↔internal | `anthropic_to_internal`、`_outcome_to_blocks`(:81) tool_use 组装 | Claude Code 协议跟进在此改 |

### 3.2 Agent 抽象层（agents/）

- `base.py`：`ModelConfig`（base_url/api_key/model_name/采样/双预算 max_total_tokens vs max_tokens_per_turn）、`AgentResult.finished` 三态（True/False/None=不追踪，永不误伤可训练性）、`Agent.run(sandbox, messages)` 唯一抽象方法
- `registry.py`：`@register_agent` + `AGENT_MODULES` 懒加载——按需 import，未装可选依赖不炸包
- `react/agent.py`（白标杆）：终止原因四分类 finished/token_limit/timeout_limit/max_steps + timeout_budget 容忍预算
- `claude_code/agent.py`（黑标杆）：`_strip_v1` 端点改写 + 全模型槽位 pin + 静默化环境变量组（`_CC_QUIET_ENV`）
- 另有 `mini_swe_agent/`、`mem_agent/`

### 3.3 Task 执行层（tasks/）

- `base.py`：`TaskConfig`（agent 字段多态解析：`{"name",...}` mapping → 具体 AgentConfig 子类）+ `Task.run()` 负责编排与打分；base 提供 `build_sandbox()/build_agent()` 胶水
- `registry.py`：`get_task()` 兼容 config 实例与扁平 mapping（训练侧 `extra_info.tools_kwargs.task` 的形态）
- `config.py`：`TaskConfigResolver` 三层深合并——**Task Config YAML ← 样本配置 ← 运行时模型端点**（训练与独立评估共用）
- 5 个任务族各三件套 `task.py/reward.py/preprocess.py`；`swe_bench/task.py:39-54` 是标准范本：sandbox 上下文管理器内跑 agent（或 oracle 金补丁），同沙箱 swebench harness 判 resolved

### 3.4 Sandbox 层（sandbox/）

- `base.py`：`SandboxBackend` 窄协议（工具只依赖数据面 exec/文件/端口，不见生命周期）；`Sandbox` ABC = 控制面 `start/stop` + `_exec` 原语；**floor-and-override 工程模式**——base64-over-exec 文件传输打底层，provider 有原生通道就覆盖；启动并发信号量（SANDBOX_STARTUP_CONCURRENCY）+ 超时 + 重试
- providers：`local` / `docker` / `vefaas`（火山引擎 Serverless）/ `modal` / `openyuanrong`，`registry.py` 按名构建

### 3.5 Tools 工具层（tools/）

- `base.py`：`Tool` = schema（Pydantic→OpenAI function schema 归一化）+ `async run()`；`ToolResult(text, status)`；**格式错误转为观察让策略自纠错**（"Invalid action: ..." 措辞与训练分布一致）；`Toolbox.call` 统一分发 + pydantic/jsonschema 双重校验；`async with toolbox.entered(retry, timeout)` 带重试启动
- `shell.py`：`stateful_shell`（模型看到的名字是 `shell`）——优先沙箱原生 `open_shell`，否则 `TmuxShell` 兜底：命令经文件捕获协议注入、`tmux wait` 通道事件唤醒轮询、超时三段中断（Ctrl-C→Ctrl-Z→kill）、镜像缺 tmux 自动装
- 另有 `edit_file.py`(str_replace_editor)、`submit.py`、`finish.py`

### 3.6 训练集成层（framework/）

- `base.py`：`AgentFramework` ABC —— `from_config` + `generate_sequences(prompts) → 写 TransferQueue`
- `framework.py`（1001 行，训练发动机）：批次→prompt→session 三层并发（失败逐层隔离，仅全批失败才 raise）；runner 分发 `inline_async`/`ray_task` + 每 runner 并发信号量；奖励双源（session reward_info 优先 → RewardLoopWorker 兜底 → 全无则 rm_scores=0 警告）；`trajectory_selection: all|longest`；TQ 字段组装（input_ids/attention/position/loss_mask/稀疏 rm_scores 打在最后一个 token/min-max_global_steps 权重版本跨度标签）；`mask_unfinished_episode` 把未完成回合的 loss_mask 全置 0（奖励保留进组基线）
- `entry.py`：`AgentFrameworkRolloutAdapter` 实现 verl `agent_loop_manager_class` 契约——配方 YAML 一行 `uni_agent.framework.entry.AgentFrameworkRolloutAdapter` 接入，零胶水
- `task_runner.py`：`run_task` 标准 runner——解析样本配置、注入会话端点、跑 Task、best-effort POST reward_info

### 3.7 ★ 如何把一个现有 harness 接进来（步骤化）

**A. 黑盒接入（harness 能配 base_url —— 最常见，参照 claude_code）**

1. **写配置与类**：在 `uni_agent/agents/<your_harness>/agent.py` 定义 `XxxConfig(AgentConfig)` + `@register_agent("xxx") class XxxAgent(Agent)`，实现 `run(sandbox, messages)`（参照 `agents/claude_code/agent.py:73-134`）
2. **端点改写**：把 `config.model.base_url` 交给 harness 的环境变量。Anthropic 系注意剥 `/v1`（claude 自己会拼 `/v1/messages`）：`_strip_v1()`（agent.py:59-70）；OpenAI 系直接用 `base_url`（已带 `/sessions/{id}/v1`）
3. **环境变量防坑**（agent.py:188-224 现成清单）：`NO_PROXY=*` + 清空 http(s)_proxy；把 harness 的**全部模型槽位**（opus/sonnet/haiku/subagent 等）pin 到同一个 served model；`IS_SANDBOX=1`；api_key 给非空占位
4. **安装与启动**：沙箱内检测/安装 harness CLI（npm 或 native installer，agent.py:137-152），`git config --system safe.directory '*'`，然后 `sandbox.exec(argv, env=..., timeout=run_timeout)`
5. **注册**：把 `"xxx": "uni_agent.agents.xxx.agent"` 加进 `agents/registry.py:21-26` 的 `AGENT_MODULES`
6. **Task Config**：yaml 里 `agent: {name: xxx, ... kwargs}`；预处理脚本把每条数据打成含此配置的 parquet 行
7. **训练接线**：默认 runner `run_task` 自动生效；harness 需要特殊编排（如 sidecar 镜像、隧道）就自写 AgentRunner（契约见 framework.py:37-47：`__call__(session, raw_prompt, sample_index, **kwargs)`），在 `agent_runners.<name>.runner_fqn` 指向它——参照 `examples/blackbox_recipes/claude_code/claude_code_runner.py`

**B. 沙箱网络不通 Gateway 时**：参照 blackbox 配方——沙箱 kwargs 里配 upstream+proxy_port 做隧道，把 Gateway URL 重写为沙箱内 `127.0.0.1:<proxy_port>`（claude_code_runner.py:41-50, 281）

**C. 白盒接入（自己写循环）**：写 `Agent` 子类持有 `Toolbox` + `OpenAICompatibleChatModel`（可直接复用 `react/model.py`），按 `react/agent.py` 的循环骨架实现终止语义即可

## 4. 推荐学习路径

| 顺序 | 读什么 | 目标 | 用时 |
|---|---|---|---|
| 1 | README + docs/concepts/gateway-and-trajectories.md | 建立心智模型：Gateway 是假扮模型服务器的轨迹收集器 | 30min |
| 2 | 四个 base.py（agents/tools/tasks/sandbox） | 记住四个唯一动作：Agent.run / Tool.run / Task.run / Sandbox._exec | 40min |
| 3 | gateway.py → adapters → session.py → codec.py | 沿一次模型调用走通数据流 | 90min |
| 4 | session.py 精读（链/回滚/mask）+ types.py | 吃透 RL 数据正确性：response_mask 0/1 从哪来 | 60min |
| 5 | react/agent.py + shell.py + claude_code/agent.py | 白盒循环设计与黑盒端点改写两大范本 | 60min |
| 6 | framework/{entry,framework,task_runner}.py | 训练闭环：并发、双源奖励、TQ | 90min |
| 7 | 跑 examples/gateway/debug_launcher.py（fake 后端即可） | 手感：亲眼看 trajectories.jsonl 落盘 | 30min |
| 8 | docs/quickstart/rl-training.md + examples/quickstart/training/ | 复现第一个训练配方 | 按机器 |

## 5. RL 训练入口与已验证配方

### 5.1 入口链

`bash examples/quickstart/training/train_qwen3_moe.sh` → verl 主训练器 → YAML `agent_loop_manager_class: uni_agent.framework.entry.AgentFrameworkRolloutAdapter`（entry.py:7-13）→ Gateway 池 + AgentFrameworkWorker → run_task → 会话轨迹 → TransferQueue → 策略更新。

### 5.2 已验证结果（README.md:73-78 与 docs/source/benchmark/rl-training.md:9-11）

| 模型 | 数据集 | 算法 | 设定 | Base | RL | Δ |
|---|---|---|---|---:|---:|---:|
| Qwen3-30B-A3B-Instruct | R2E-Gym | GSPO | Fully Async, 100 turns, 128K | 22.2 | **36.8** | +14.6 |
| Qwen3-Coder-30B-A3B-Instruct | R2E-Gym | GSPO | Fully Async, 100 turns, 128K | 46.2 | **52.0** | +5.8 |
| Qwen3.5-9B | SWE-reBench | GRPO | Fully Async, 100 turns, 128K | 53.8 | **59.2** | +5.4 |
| Qwen3-Coder-30B-A3B-Instruct | SWE-reBench | — | Colocate Async, 200 turns, 128K | 47.4 | **54.2** | +6.8 |

配套数字：partial rollout 把 200 步训练从 95.6h 压到 45.8h（**2.1×**，8×A100，Pass@1 基本持平）；并行推理榜：Qwen3-Coder-480B SWE-Bench Verified **64.2**（Avg@4, 500 turns, 256K）、Qwen3.5-35B-A3B **68.4**、Qwen3.6-35B-A3B Terminal-Bench v2 **42.5**（README.md:55-63）。

### 5.3 训练配方骨架（quickstart/rl-training.md:189-217）

- 数据：`python3 -m uni_agent.tasks.swe_rebench.preprocess`（或直接用 HF `syyyyyyyyy/swe-rebench-filtered-1150` 的 1150 样本版）+ swe_bench 验证集 parquet
- 启动：`DATA_DIR=... NNODES=8 CONCURRENCY=1024 GEN_TP=4 TP=1 PP=2 CP=4 EP=8 TRAIN_PROMPT_BSZ=64 N_RESP_PER_PROMPT=8 LOSS_MODE=gspo ROUTER_REPLAY_MODE=R3 TASK_CONFIG=.../task_config_react.yaml bash examples/quickstart/training/train_qwen3_moe.sh`
- Claude Code 黑盒训练：`train_qwen3p5_dense.sh` + `task_config_claude_code.yaml`（ADV_ESTIMATOR=rloo, LOSS_MODE=dppo_tv；runner 设 `trajectory_selection=longest` 只训模型 token 最多的链）

### 5.4 已知坑（ newcommer 必看）

1. `ANTHROPIC_BASE_URL` **不能带 `/v1`**（claude 自己拼 `/v1/messages`）；OpenAI 端点则必须带 `/v1`（examples/gateway/README.md:142-152）
2. Claude Code 会请求大 `max_tokens`（如 32000）——本地小后端必须配 `prompt_length+response_length` 容量让 Gateway 钳制（session.py:501-508；debug_launcher 的 `--response-length`）
3. `mask_unfinished_episode=True` 时未完成回合 loss_mask 全 0 但奖励仍进 GRPO 组基线——不是样本删除（concepts/gateway-and-trajectories.md:104-106）
4. Claude Code 沙箱必须能网络可达 GPU 机上的会话端点；不行就走 blackbox 隧道方案
5. 工具解析器必须匹配模型的 chat template：`rollout.multi_turn.format`（如 qwen3_coder/qwen3_xml）（codec.py:34-42 别名表）
6. 一个会话可物化多条轨迹（并发请求分链）；训练默认取全部或 `longest`——奖励在会话级广播
