# AgentGym-RL 核心文件深解（CORE-FILES-EXPLAIN）

> 对 ONBOARDING.md 提到的每个代码文件做逐文件深解：职责 / 输入输出 / 关键函数（签名+行为）/ 上下游依赖 / 值得学的工程手法。证据一律 `文件:行号`。仓库根：`~/ai/AgentGym-RL`。

## 1. controller/types.py —— 协议词汇表

- **路径**：`AgentGym/agentenv/agentenv/controller/types.py` ｜ **82 行** ｜ 纯类型定义，零逻辑
- **职责**：定义全系统交换的数据结构。所有模块（env/agent/task/envs）都 import 它。
- **输入输出**：无运行时输入输出；被上游 import。
- **关键定义逐个**：
  - `ConversationMessage = TypedDict("ConversationMessage", {"from": str, "loss": Optional[bool], "value": str})`（types.py:5-7）——vicuna 风格消息。**`loss` 三态是全系统最精妙的设计**：`None`=环境/提示（不训）、`True`=模型生成（训）、`False`=预设助手句"OK."（不训）。它最终决定 `action_mask`。
  - `APIConversationMessage {role, content, reasoning_content}`（types.py:9-11）——API 版消息，`reasoning_content` 字段为推理模型（如 GLM/o1 风格）的思维链留位。
  - `TokenizedConversationOutput {text, input_ids, action_mask}`（types.py:13-20）——模板 tokenize 的输出三元组。
  - `ActionFormat(Enum)`: `react / function_calling / code_as_action`（types.py:23-26）——三种动作协议枚举。**注意**：定义了但三个代表性客户端都没用（见 ONBOARDING 附§6）。
  - `InferenceEngine(Enum)`: `default / vllm`（types.py:29-31）。
  - `@dataclass StepOutput {state, reward, done}`（types.py:34-38）——`client.step()` 的返回，单轮交互原子。
  - `@dataclass ExperienceOutput {conversation, reward, text, seq_ids, attention_mask, action_mask}`（types.py:41-48）——一条完整轨迹，字段即 RL 训练张量。
  - `APIExperienceOutput {conversation, reward}`（types.py:51-54）。
  - `@dataclass ActionWithTought {thought, action}`（types.py:57-60）——拼写错误：Tought 应为 Thought。
  - `EvaluationOutput`（types.py:63-67）、`Function`/`ChatCompletionMessageToolCall`（types.py:70-82）——function calling 支撑。
- **上下游**：被 env.py:3、agent.py:14、task.py:6、全部 envs/*.py import。
- **值得学**：用 TypedDict 而非 dataclass 定义消息（保持 dict 兼容、可整体 `**` 展开构造）；loss 语义内嵌消息体，让模板层无状态地产生训练掩码。

## 2. controller/env.py —— 最小环境契约

- **路径**：`AgentGym/agentenv/agentenv/controller/env.py` ｜ **34 行**
- **职责**：定义环境客户端抽象基类 `BaseEnvClient`。整个"接入一个新环境"的契约只有 4 个方法。
- **输入输出**：抽象层；子类收 HTTP 响应、产出 `str`/`StepOutput`。
- **关键定义逐个**：
  - 类注解 `_conversation_start: dict[ActionFormat, tuple[ConversationMessage]]`（env.py:7）——**注解说是 dict，但子类（babyai.py:10）直接以 tuple 覆盖**，注解与实现脱节，阅读时以子类为准。
  - `def __init__(self, action_format: ActionFormat = "react")`（env.py:9-10）——保存动作格式；三个代表性客户端均未消费此参数（协议预留）。
  - `@abstractmethod __len__(self) -> int`（env.py:12-16）——环境数据集大小（任务条数）。
  - `@abstractmethod observe(self) -> str`（env.py:18-22）——把环境服务器响应解析成喂给 LLM 的文本。
  - `@abstractmethod step(self, action) -> StepOutput`（env.py:24-28）——从模型输出解析动作并调用服务器。
  - `@abstractmethod reset(self, idx: int) -> None`（env.py:30-33）——重置到第 idx 个任务。
- **上下游**：被 task.py:5（经 controller `__init__`）使用；envs/*.py 继承。
- **值得学**：**34 行定义一个生态的接入协议**。环境实现在远端进程，客户端只做"HTTP 包装 + 输出解析"，所以 ABC 才能这么小；对比 Gym API（reset/step/observe/render...），这里砍掉一切非必需。

## 3. controller/agent.py —— 推理引擎与聊天模板（400 行）

- **路径**：`AgentGym/agentenv/agentenv/controller/agent.py` ｜ **400 行**
- **职责**：① `Agent`（本地 HF/vLLM 推理）② `APIAgent`（OpenAI 兼容 API）③ 4 种 ChatTemplate（token 级拼接 + action_mask）。
- **输入输出**：吃 token id / conversation，吐 generated_tokens（token id 列表）或文本。
- **关键函数逐个**：
  - `BaseChatTemplate.tokenize_conversation_one(message, tokenizer, idx, add_generation_prompt=False) -> TokenizedConversationOutput`（agent.py:27-35，抽象）；`tokenize_conversation(conversation, tokenizer, add_generation_prompt) -> TokenizedConversationOutput`（agent.py:37-59）——逐条调 `_one` 并累积 text/input_ids/action_mask；`add_generation_prompt` 只作用于**最后一条**消息（agent.py:48 的 `and idx == len(conversation)-1`）。
  - `Agent.__init__(model, tokenizer, chat_template=None, inference_engine="default")`（agent.py:63-74）——默认 `Llama2Template`，懒初始化 `self._vllm=None`。
  - `Agent.generate(input_ids, generation_config, refresh_engine=False) -> torch.Tensor`（agent.py:76-193，@torch.no_grad）——核心推理入口，两分支：
    - **vLLM 分支**（agent.py:87-181）：置 `VLLM_WORKER_MULTIPROC_METHOD=spawn`（L88）；首次/refresh 时把训练态权重 `save_pretrained` 到 `/dev/shm/agentgym/inference_model_cache/<随机>` 共享内存（L100-106）再喂给 vLLM，随后 `shutil.rmtree`（L142）——**训练权重→推理引擎的免序列化握手**；用 `gcd(num_attention_heads, vocab_size)` 从设备数向下搜最大的合法 `tensor_parallel_size`（L116-126）；`enable_prefix_caching` 对 NPU 关闭（L131）；生成参数白名单式映射到 `SamplingParams`（L154-166），`detokenize=False` 直接回 token_ids（L167-175）。
    - **HF 分支**（agent.py:183-191）：直接 `model.generate`，切片去掉 prompt 部分。
  - `APIAgent.__init__(api_key, base_url, model, max_tokens=4096, temperature=1, top_p=1)`（agent.py:197-211）；`APIAgent.generate(conversation) -> Tuple[str, str|None]`（agent.py:213-231）——`while True` 包裹 API 调用，任何异常打印后 `sleep(1)` 无限重试（L217-231）；返回 `(content, reasoning_content)`，用 `hasattr` 探测推理模型思维链（L228）。
  - `Llama2Template.tokenize_conversation_one`（agent.py:234-264）——human 拼成 `<s>[INST] {v} [/INST]`，gpt 拼成 `{v}</s>`；**`loss` 直接展开成 0/1 action_mask**（L253-256）。
  - `ChatMLTemplate`（agent.py:267-311）——`<|im_start|>` 体系；首条若无 system 自动补默认 system（L279-281）。
  - `Llama3Template`（agent.py:314-357）——`<|begin_of_text|>/<|start_header_id|>` 体系；先 strip 尾部空白（L323-324）。
  - `ChatGLM4Template`（agent.py:360-400）——`[gMASK]<sop><|user|>` 体系。
- **上下游**：被 task.py:5 使用；types.py 提供类型；NPU 兼容探测 `torch_npu`（agent.py:20-23）。
- **值得学**：①不依赖 tokenizer.apply_chat_template 而手写四种模板——因为**必须逐 token 控制 action_mask 边界**，通用模板 API 做不到；②vLLM 权重经 /dev/shm 交接，规避 deepspeed/FSDP 状态字典到 vLLM 的转换链；③APIAgent 的 hasattr 探测 reasoning_content 是对接国产推理模型的实用兼容层。

## 4. controller/task.py —— rollout 主循环（185 行）

- **路径**：`AgentGym/agentenv/agentenv/controller/task.py` ｜ **185 行**
- **职责**：`BaseTask` 把 Agent 与 EnvClient 缝合成多轮交互循环，产出可训练的 `ExperienceOutput`。SFT 数据采集/评估走这条路径（RL 训练侧另有 vllm_rollout 平行实现）。
- **输入输出**：输入 `(agent, idxs, generation_config, max_rounds)`；输出轨迹列表。
- **关键函数逐个**：
  - 类属性 `env_client_cls: Callable` / `env_name: str`（task.py:10-11）——子类只需填这两个（babyai.py:105-106）。
  - `__init__(client_args, n_clients=1)`（task.py:13-28）——创建 n 个客户端；`self.len = len(self.clients[0])`（L28）。docstring 自曝"批量生成未实现"（L23）。
  - `_generate_experience_one(agent, client, idx, generation_config, max_rounds) -> ExperienceOutput`（task.py:30-148）——**全文件心脏**，逐段：
    1. `client.reset(idx)` + `state = client.observe()`（L38-41）；
    2. 组装开场：`conversation = list(client.conversation_start)` + 追加首个 human 状态（L44-47）；API 路线把 conversation_start 两句 + state 摊平成三条 role 消息（L52-54）；
    3. tokenize 一次（L48-50）；
    4. 主循环 `while not done`（L59-131）：
       - **长度熔断**：`input_length >= (generation_config.max_length or 4096)` 则 break（L61-64）——默认 4096 硬编码在表达式里；
       - 生成；**异常即 break**（L65-71，broad-except 注释化豁免 pylint）；
       - **eos 补齐**：若末 token 非 eos 则手动补（L73-74），保证后续拼接格式闭合；
       - 拼回 tokenized：text/input_ids 追加，`action_mask += [1]*len`（L77-79）——**模型生成段全 1**；
       - `client.step(generated_text)` → `(state, reward, done)`（L99-104）；
       - 环境回话 token 化追加，`action_mask` 由 loss=None 展开为全 0（L106-119）；
       - `rounds += 1`；`max_rounds` 到顶 break（L129-131）。
    5. 返回 `ExperienceOutput`（L133-141）：`attention_mask` 是全 1 直拼（L139）。
  - `_generate_experience_batch(agent, idxs, ...)`（task.py:150-168）——**串行 for 循环**逐 idx 调 `_one`，名叫 batch 实为顺序执行。
  - `generate_experience(agent, idxs, ...)`（task.py:170-185）——统一入口，int 自动包 list。
- **上下游**：依赖 controller 的 Agent/APIAgent/BaseEnvClient（task.py:5）与 types（L6）；utils.py 的 Evaluator 反过来用它。
- **值得学**：**增量 tokenization**——只 tokenize 新增消息而非每轮重 tokenize 整段对话，把多轮交互的 tokenization 成本从 O(rounds²) 降到 O(rounds)；代价是模板必须保证"逐条拼接==整段拼接"，这正是四种模板手写的原因。

## 5. controller/utils.py —— 动作格式与评估（286 行）

- **路径**：`AgentGym/agentenv/agentenv/controller/utils.py` ｜ **286 行**（深读前 90 行 + `__init__.py:13-20` 导出清单）
- **职责**：三种动作协议的提示词构造 + 代码块解析 + Evaluator 评估 + BaseAdapter 轨迹转换。
- **关键函数逐个**（前 90 行实证）：
  - 常量 `INVOKING_FUNCTION_PROMPT`（utils.py:18-29）——要求模型以 ```json {"thought":..., "function_name":..., "arguments":...}``` 回复。
  - 常量 `WRITE_CODE_PROMPT`（utils.py:31-39）——要求以 ```python 代码块回复，thought 写进注释。
  - `format_function_call_prompt(function_description) -> str`（utils.py:41-50）——工具 JSON schema 列表 + INVOKING_FUNCTION_PROMPT。
  - `generate_function_signatures(function_descriptions)`（utils.py:53-81）——把 OpenAI 风格 schema 逆写成 `def name(param):"""docstring"""` 签名文本。
  - `format_code_as_action_prompt(function_description) -> str`（utils.py:84-90）——签名 + WRITE_CODE_PROMPT。
  - 其后（L91-286）为 `extract_python_code_blocks`/`parse_python_code_comments`/`BaseAdapter`/`Evaluator`（依据：`controller/__init__.py:13-20` 的导出与 utils.py:8-16 的 import）。
- **值得学**：`generate_function_signatures` 实现"schema→可读签名"的降维——把结构化工具描述翻译成 LLM 最熟的 python 文本，是 code-as-action 范式的提示工程基石。

## 6. envs/babyai.py —— BabyAI 客户端样板（111 行）

- **路径**：`AgentGym/agentenv/agentenv/envs/babyai.py` ｜ **111 行**
- **职责**：具身网格世界（上游 mila-iqia/babyai）的 HTTP 客户端 + ReAct 动作解析。**写自定义环境的最佳抄写样板**。
- **输入输出**：HTTP；`step(str)->StepOutput`。
- **关键函数逐个**：
  - 类属性 `conversation_start`（babyai.py:10-25）——指令 system prompt（动作清单 + "Thought:/Action:" 格式约定，L15）+ 助手确认句 `"OK. I'll follow..."`（L18-24，loss=False）。
  - `__init__(env_server_base, data_len, *, timeout=300)`（babyai.py:27-40）——构造即 `POST /create`（L35），失败抛 `RequestException`（L36-37），存 `self.env_id = ok["id"]`（L40）。**注意**：连接失败在对象构造期暴露，fail-fast。
  - `__len__`（L42-43）——返回外部传入的 `data_len`（客户端不向服务器要规模）。
  - `_post(path, data)`（L45-53）/`_get(path)`（L55-61）——统一注入 `id` 键 + assert 200。
  - `observe(self) -> str`（L63-64）——**读 `self.info["observation"]` 本地缓存**（由 step/reset 时刷新），不再发请求。
  - `step(self, action) -> StepOutput`（L66-88）——动作解析流水线：
    1. `re.findall(r"Action:\s*(.*?)(?=\n|$)", action, re.DOTALL)`（L67）；
    2. `len>1` → 返回错误状态消息（reward=0, done=False，L68-73）——**用环境反馈惩罚格式错误，而非抛异常**；
    3. 取最后一个匹配（L74）；
    4. `re.sub(r"[^A-Za-z0-9, ]+", "", action)` 清洗非法字符（L75）+ 空白归一（L76）；
    5. `POST /step`，`reward=response["score"]`、`done=response["done"]`（L77-88）。
  - `reset(data_idx=0)`（L90-98）——`POST /reset {"data_idx": ...}`，刷新 `self.info` 四元组。
  - `close()`（L100-102）。
  - `BabyAITask(BaseTask)`（L104-111）——只挂 `env_client_cls=BabyAIEnvClient` / `env_name="BabyAI"`。
- **上下游**：import `agentenv.controller`（L5）与 types（L6）；被 envs/__init__.py:3 注册。
- **值得学**：动作解析的"宽容+纠错"分层：多个 Action→环境内错误消息（模型下轮可自纠）；无匹配→空字符串照发（服务器端兜底）；非法字符→静默清洗。错误是训练信号的一部分，不是异常。

## 7. envs/webarena.py —— WebArena 客户端与协议漂移（111 行）

- **路径**：`AgentGym/agentenv/agentenv/envs/webarena.py` ｜ **111 行**
- **职责**：真实网页环境（上游 web-arena-x/webarena）客户端。与 babyai 同为 111 行，处处对照出**同一 ABC 下的协议漂移**。
- **关键差异逐条（行号证据）**：
  1. **ID 键名**：`env_idx`（webarena.py:37,43,54）vs babyai 的 `id`（babyai.py:40,46）——同一框架两套 HTTP 方言。
  2. **动作解析**：`re.findall(r"```(.*?)```", action, re.DOTALL)` 三反引号块（L66）vs babyai 的 `Action:` 行（L67）；**多动作检查整段被注释掉**（L67-73），只保留 0 动作报错（L74-80）——放宽约束的演进痕迹。
  3. **奖励语义**：`reward = response["reward"] if response["terminated"] else 0`（L82）——**只在终止时发奖励**（稀疏奖励由客户端而非服务器强制）；babyai 每步都回 `score`（babyai.py:86）。
  4. **observe 实现**：走 `GET /observation`（L60-62）返回 dict（与基类 `-> str` 签名不符）；babyai 读本地缓存不发请求（babyai.py:63-64）。
  5. **reset 韧性**：响应为字符串 `"TimeoutError"` 时抛出带建议（重启 web server）的异常（L90-94）；且 `seed: 0` 硬编码（L91）。
  6. `conversation_start`：巨型浏览器操作手册 system prompt（L11-16，含 click/type/scroll/stop 等全集）。
- **值得学**：客户端层允许"方言"存在——ABC 只锁 4 个方法签名，解析策略/奖励语义/键名全部留给子类；代价是跨环境代码不能想当然复用，写通用工具必须同时兼容 `id` 与 `env_idx`。

## 8. verl/agent_trainer/config/ppo_trainer.yaml —— 训练默认配置（198 行）

- **路径**：`AgentGym-RL/verl/agent_trainer/config/ppo_trainer.yaml`
- **职责**：hydra 默认配置，CLI `key=value` 即覆写（train.sh 的机制）。
- **关键段**：
  - `algorithm.rounds_ctrl`（ppo_trainer.yaml:171-174）：`type: fixed`（默认）/ `rounds: 15` / `steps_scaling_inter: 100`——**ScalingInter 的全部三旋钮**。README.md:179-183 的参数文档与此一一对应。
  - `actor_rollout_ref.agentgym`（L63-68）：`task_name: textcraft`（默认环境）、`env_addr: 'http://localhost:5000'`、`max_retries: 10`、`max_rounds: 10`（main_generation.py:107 消费）、`timeout: 300`。**L67 注释误贴**："Maximum token length of a single response per turn"是 max_tokens 的文案。
  - `trainer`（L179-189）：`total_epochs: 30`、`n_gpus_per_node: 8`、`save_freq: -1`。
- **值得学**：单一 yaml 同时服务 hydra CLI 覆写与文档；参数间用 OmegaConf 插值（如 `prompt_length: ${data.max_prompt_length}`，L74）避免重复维护。

## 9. verl/agent_trainer/ppo/ray_trainer.py —— RoundScheduler 与训练主循环（884 行，聚焦增量）

- **路径**：`AgentGym-RL/verl/agent_trainer/ppo/ray_trainer.py` ｜ 884 行（verl 原版改造 + 本项目核心增量）
- **职责**：RayPPOTrainer 全流程；本文只解 **RoundsScheduler 家族**（ScalingInter-RL 本体）与三个调用点。
- **关键类逐个**：
  - `RoundsScheduler`（抽象，ray_trainer.py:198-205 附近）：`step()` / `set_global_steps(int)` / `get_rounds()` 三方法。
  - `FixedRoundsScheduler(rounds)`（L208-219）：`max_rounds` 恒定；`step`/`set_global_steps` 均为 `pass`——**空实现也是契约**（保持调用方统一）。
  - `StepRoundsScheduler(steps_scaling_inter, rounds_ls)`（L222-245）——**渐进轮数调度器**：
    - 构造：`max_rounds = rounds_ls[0]`、`current_stage = 0`、`global_steps = 1`（L226-228，注释 start from 1）；
    - `set_global_steps(g)`（L230-236）：`stage = g // steps_scaling_inter`，**越界封顶 `len(rounds_ls)-1`**（L234-235），`max_rounds = rounds_ls[stage]`（L236）；
    - `step()`（L238-242）：`current_stage+1 < len` 且 `global_steps % steps_scaling_inter == 0` 时升档（L239-241），随后 `global_steps += 1`；
    - 语义：**训练步数每满 100 步换下一档地平线，6→13→20 后永远停在 20**。
  - 工厂（L543-549）：按 `config.algorithm.rounds_ctrl.type` 分支实例化，其余类型 `NotImplementedError`。
- **三个调用点**（数据流闭环）：
  1. `self.rounds_scheduler.set_global_steps(self.global_steps)`（L696）——epoch 对齐；
  2. `gen_batch.meta_info['max_rounds'] = self.rounds_scheduler.get_rounds()`（L770）+ 写入 metrics（L772）——**轮数注入 rollout 批**；
  3. `self.rounds_scheduler.step()`（L876）——每个训练 step 末推进。
- **值得学**：调度器从训练器中被抽成 3 方法小对象，`Fixed` 与 `Stepwise` 同接口可换——**算法创新的正确工程形态：新方法=一个新类+一行工厂分支+零散弹式修改**。

## 10. verl/workers/rollout/agent_vllm_rollout/vllm_rollout.py —— max_rounds 消费端（节选）

- **路径**：`AgentGym-RL/verl/workers/rollout/agent_vllm_rollout/vllm_rollout.py`（多轮 rollout worker）
- **关键行**：
  - `max_rounds = prompts.meta_info.get('max_rounds', 10)`（vllm_rollout.py:195）——接收训练器注入，缺省 10；
  - `rollout_bar = tqdm(total=max_rounds, ...)`（L228）；
  - `while rounds < max_rounds and not all_done_flag:`（L247）——**ScalingInter 的轮数在这里物理生效**；
  - `rollout_bar.set_description(f"Rounds {rounds+1}/{max_rounds} | Active agents per gpu: {len(not_done_idxs)}")`（L256）——活跃 agent 掩码随任务完成收缩，已 done 的不再占生成算力。
- **与协议层的关系**：**不 import agentenv**（`grep import agentenv AgentGym-RL/verl/agent_trainer/` 零命中）；它自带同协议的 HTTP 环境调用，与 `envs/*.py` 是同一服务端契约的两个平行客户端实现——协议解耦的实证。

## 11. examples/train/AgentGym-RL/babyai_train.sh（71 行，基线）

- **路径**：`examples/train/AgentGym-RL/babyai_train.sh` ｜ 71 行
- **职责**：BabyAI 固定 20 轮 GRPO 训练的全启动脚本。结构四段：
  1. **环境变量**（L1-4）：`VLLM_WORKER_MULTIPROC_METHOD=spawn`、`VLLM_ATTENTION_BACKEND=XFORMERS`（多卡 vLLM 必需）；
  2. **变量区**（L19-35）：`Qwen2.5-7B-Instruct`、`kl_coef=0.001`、`lr=1e-6`、`rollout_sample_num=8`、`train_batch_size=16`、`ppo_inner_epochs=1`、`total_epoches=10`；
  3. **启动命令**（L39-69）：`python3 -m verl.agent_trainer.main_ppo` + 30 个 hydra 覆写参数。关键：`algorithm.rounds_ctrl.type=fixed`、`rounds=20`（L41-42）、`adv_estimator=grpo`（L40）、`rollout.n=8`（L55）、`max_tokens=200`（L57）、`env_addr=http://127.0.0.1:36005`（L48）；
  4. **退出码透传**（L70-71）。
- **值得学**：变量区与 hydra 覆写分离——改实验只动前 30 行变量，不动 30 行参数清单；`HYDRA_FULL_ERROR=1` 保证配置错误时打全栈。

## 12. examples/train/ScalingInter-RL/babyai_train.sh（72 行，渐进轮数）

- **路径**：`examples/train/ScalingInter-RL/babyai_train.sh` ｜ 72 行
- **职责**：同任务同模型同 RL 算法，仅换轮数调度与配套容量参数。**与基线逐行 diff 共 11 处**（详见 ONBOARDING.md §⑤ 表格），其中 4 处直接构成 ScalingInter 开关：
  - L41 `type=scaling_inter_stepwise`（vs `fixed`）
  - L42 `steps_scaling_inter=100`（基线无此行）
  - L43 `rounds=[6,13,20]`（vs `rounds=20`）——注意 hydra 传列表语法 `[6,13,20]`
  - 三档语义联动 ray_trainer.py:230-242：step 1-100 用 6 轮、101-200 用 13 轮、201+ 恒 20 轮
- **配套容量 7 处**（设计动机）：`rollout.n` 8→4（短地平线不需大组）、batch 16→32、inner_epochs 1→2、epochs 10→20（总步数翻倍才能走完三档）、`max_prompt_length` 1024→512（BabyAI 指令短）、`max_response_length` 4096→8192（长地平线轨迹总长翻倍）、`max_tokens` 200→512（单轮 thought+action 更长）。
- **值得学**：**方法对比实验的脚本纪律**——除方法开关与必要容量配套外一切不变；两文件 99% 相同本身就是可复现性的证明。

## 13. verl/agent_trainer/main_ppo.py —— 训练入口（96 行）

- **路径**：`AgentGym-RL/verl/agent_trainer/main_ppo.py` ｜ 96 行
- **职责**：hydra 入口 → Ray 集群 → 组装 trainer。
- **关键函数**：
  - `@hydra.main(config_path='config', config_name='ppo_trainer')` `main(config)`（main_ppo.py:23-25）。
  - `run_ppo(config)`（L28-33）：`ray.init(runtime_env={'env_vars': {'TOKENIZERS_PARALLELISM': 'true', 'NCCL_DEBUG': 'WARN'}})`（L31）——用 ray runtime_env 注入 worker 环境变量，而非 shell export。
  - `@ray.remote(num_cpus=1) main_task(config)`（L36-88）：注释"make sure main_task is not scheduled on head"（L36）；FSDP worker 选路（L53-60，仅 fsdp 分支）；`RayPPOTrainer(...)` + `init_workers()` + `fit()`（L82-88）。
- **值得学**：入口极薄（96 行），把"解析配置/起集群/选 worker/跑训练"四件事各交专职组件；`ray.remote(num_cpus=1)` 防止调度器把主任务放上 head 节点抢资源的注释级经验。

## 14. envs/__init__.py 与注册表（14 行）

- **路径**：`AgentGym/agentenv/agentenv/envs/__init__.py` ｜ 14 行
- **职责**：一环境一行的注册表：`from .babyai import BabyAIEnvClient, BabyAITask`（L3）式×14 文件 16 对（lmrlgym.py 导出 Maze+Wordle 两对，L4；searchqa 是 AgentGym-RL 新增，L14）。
- **值得学**：注册表模式使"加环境=加文件+加一行"；上游 AgentGym README.md:30-45 的 14 环境表与它一一对应（searchqa 除外）。

## 15. main_generation.py —— 评估/生成入口（节选）

- **路径**：`AgentGym-RL/verl/agent_trainer/main_generation.py`
- **关键行**：`data.meta_info['max_rounds'] = config.agentgym.max_rounds`（main_generation.py:107）——评估侧用 yaml 的 `agentgym.max_rounds`（默认 10）而非调度器，保证评估条件恒定。README.md:230 指向的 `generation.yaml` 是它的姊妹配置。

---
**总结**：协议层（types/env/task）用 300 行定义了"多轮 Agent RL 的最小完备契约"；ScalingInter-RL 的全部增量 = `StepRoundsScheduler` 24 行 + 配置三旋钮 + 两个脚本 11 行 diff——**论文级方法落成代码时的"少即是多"范本**。
