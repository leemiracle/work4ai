# AgentGym-RL 新人上手指南

> 基于对 `~/ai/AgentGym-RL` 的源码深读（2026-08-17），所有结论附 `文件:行号` 证据。vendored verl fork 仅读其新增的 `agent_trainer` 与 rollout 相关增量。

## ① 这个项目是什么

**一句话**：把 LLM Agent 的"多轮环境交互"变成可强化学习的目标——用 HTTP 服务端-客户端解耦环境生态，用 verl 扩展做 GRPO/PPO 训练，用 ScalingInter-RL（渐进拉长交互轮数）解决多轮 RL 的探索-利用失衡（README.md:25-29）。

**定位**：ICLR 2026 Oral（arXiv:2509.08755），7B 开源模型在 27 个任务上比肩/超越商业模型（README.md:6,11）。它是两个体系的合体：
- **AgentGym**（环境生态，`AgentGym/`）：14 环境的服务器-客户端协议 + 轨迹集 + AgentEval（AgentGym/README.md:28-45）
- **AgentGym-RL**（训练，`AgentGym-RL/`）：vendored verl fork + 自研 `agent_trainer` 模块

## ② 架构总览：三模块解耦怎么落地

```
┌────────────────────────────────────────────────────────────┐
│ 训练模块 (AgentGym-RL/verl fork)                            │
│  main_ppo.py ──hydra──> ppo_trainer.yaml                   │
│    └> RayPPOTrainer (ray_trainer.py)                       │
│         ├─ RoundScheduler ← rounds_ctrl (固定/渐进轮数)      │
│         └─ actor_rollout_wg.generate_sequences()           │
│              └─ vllm_rollout.py: while rounds < max_rounds │
│                   │ HTTP (env_addr, 如 :36005)             │
┌───────────────┼────────────────────────────────────────────┐
│ 环境服务器（独立进程/机器，各环境独立仓库 agentenv-*）        │
│   POST /create /step /reset /close (+GET /observation)     │
┌───────────────┼────────────────────────────────────────────┐
│ AgentGym/agentenv 协议包（SFT/评估侧的客户端）               │
│   controller: types(类型) env(ABC) agent(推理) task(循环)   │
│   envs: 14+1 环境客户端，每环境 = EnvClient + Task 对       │
└────────────────────────────────────────────────────────────┘
```

**关键事实**：训练侧（verl fork）**不 import** agentenv 包（`grep "import agentenv" AgentGym-RL/verl/agent_trainer/` 零命中），两边是**同一 HTTP 协议的两个平行实现**——协议即契约，这是三模块真正解耦的机制。

### 目录表

| 路径 | 是什么 |
|---|---|
| `README.md` | 总文档：架构、ScalingInter-RL、参数表、教程 |
| `AgentGym/` | 环境生态（上游 AgentGym 仓库） |
| `AgentGym/agentenv/agentenv/controller/` | 协议核心：types/env/agent/task/utils |
| `AgentGym/agentenv/agentenv/envs/` | 16 个环境客户端（15 文件，lmrlgym 含 Maze+Wordle） |
| `AgentGym-RL/` | RL 训练（vendored verl fork） |
| `AgentGym-RL/verl/agent_trainer/` | **自研增量**：main_ppo.py + config/ + ppo/ray_trainer.py |
| `AgentGym-RL/verl/workers/rollout/agent_vllm_rollout/` | 多轮 rollout worker（max_rounds 消费端） |
| `examples/train/{AgentGym-RL,ScalingInter-RL}/` | 对照训练脚本（每任务一份） |
| `examples/eval/` | 评估脚本 |

## ③ 核心模块清单

### M1 环境协议层 `AgentGym/agentenv/agentenv/controller/`

- **职责**：定义"与环境服务器对话"的全部词汇与流程。
- **关键类**：
  - `BaseEnvClient`（env.py:6-32）：4 抽象方法 `__len__`/`observe`/`step`/`reset`，子类挂 `conversation_start` 类属性即成环境。
  - `BaseTask`（task.py:9-185）：`_generate_experience_one`（task.py:30-148）= 多轮 rollout 主循环（Agent/环境交替，产出带 `action_mask` 的 `ExperienceOutput`）。
  - `Agent`（agent.py:62-193）：HF/vLLM 双引擎；`APIAgent`（agent.py:196-231）：OpenAI 兼容 API + `reasoning_content` 捕获。
  - 4 种 ChatTemplate（agent.py:234-400）：手工拼 token 以精确控制 `action_mask`（loss 范围）。
- **怎么扩展**：见下"如何加自定义环境"。

### M2 环境客户端层 `AgentGym/agentenv/agentenv/envs/`

- **职责**：每环境一对 `XxxEnvClient + XxxTask`，做 HTTP 包装 + LLM 输出解析。
- **注册表**：`envs/__init__.py:1-14` 导出 16 对；`searchqa` 是 AgentGym-RL 新增（第 14 行，上游 README 14 环境表中无）。
- **解析风格三例**（同一 ABC 下的"方言"）：
  - babyai：`Action:` 行正则，>1 个报错，取最后一个，清洗非法字符（babyai.py:67-76）
  - webarena：三反引号块正则，0 个报错，多动作检查被注释（webarena.py:66-80）
  - searchqa：`<think>/<search>/<information>` 标签协议（searchqa.py:14）

### M3 训练引擎层 `AgentGym-RL/verl/agent_trainer/`（+ rollout worker）

- **职责**：GRPO/PPO/RLOO/REINFORCE++ 多轮 RL（README.md:78）。
- **关键类**（ray_trainer.py, 884 行）：
  - `FixedRoundsScheduler`（L208-219）：恒定 max_rounds。
  - `StepRoundsScheduler`（L222-245）：`current_stage = global_steps // steps_scaling_inter`（封顶最后档），ScalingInter-RL 本体。
  - 工厂分支 L543-549；fit 循环 L770 把 `get_rounds()` 注入 `gen_batch.meta_info['max_rounds']`。
- **消费端**：vllm_rollout.py L195 读 `max_rounds`（默认 10）、L247 `while rounds < max_rounds and not all_done_flag` 逐轮生成，活跃 agent 掩码收缩（L256）。

### 如何加自定义环境（三步 + 官方教程）

1. **起环境服务器**（任意语言/机器），实现 4 个 HTTP 端点（以 babyai.py 为证据样板）：
   - `POST /create` → 返回 `{"id": <env_id>}`（babyai.py:35-40；webarena 用 `env_idx` 键，webarena.py:37）
   - `POST /step` `{id, action}` → `{observation, reward, score, done}`（babyai.py:77-83）
   - `POST /reset` `{id, data_idx}` → 同构响应（babyai.py:90-98）
   - `POST /close`（babyai.py:100-102）；可选 `GET /observation?id=`（webarena.py:52-58）
2. **写客户端**：新建 `envs/myenv.py`，继承 `BaseEnvClient` 实现 4 方法 + `conversation_start` 类属性（指令 prompt + 助手确认句，babyai.py:10-25）；`step()` 里用正则从 LLM 原始输出解析动作并调用 HTTP。再建 `MyEnvTask(BaseTask)` 挂 `env_client_cls`/`env_name`（babyai.py:104-111）。
3. **注册 + 数据**：在 `envs/__init__.py` 加一行导入；RL 训练需 `AgentItemId/{task}_train.json`（train.sh:43）+ `actor_rollout_ref.agentgym.task_name/env_addr`（train.sh:47-48）。
官方二开教程：`docs/tutorials/en/05-2nd-Development.md`（README.md:12 链接）。

## ④ 推荐学习路径（8 步，对应 knowledge-graph.json 的 tour）

| 步 | 读什么 | 看什么要点 |
|---|---|---|
| 1 | `README.md` | 三模块图、ScalingInter 动机（L82-88）、rounds_ctrl 参数表（L179-183） |
| 2 | `AgentGym/README.md` | 14 环境表、HTTP API 约定（L51，注意 `/createEnv` 与代码 `/create` 不符） |
| 3 | `controller/types.py` | `loss` 三态→`action_mask`；`ExperienceOutput` 字段即 RL 训练张量 |
| 4 | `controller/env.py` | 34 行 ABC：最小契约设计 |
| 5 | `controller/task.py` | `_generate_experience_one` 逐行：截断/熔断/action_mask 维护 |
| 6 | `controller/agent.py` | vLLM `/dev/shm` 暂存（L100-106）、gcd 求 tp（L116-126）、APIAgent 重试（L217-231） |
| 7 | `envs/babyai.py` vs `envs/webarena.py` | 逐行对照解析风格与协议键名差异 |
| 8 | `ppo_trainer.yaml` → `ray_trainer.py` → `vllm_rollout.py` → 两份 `babyai_train.sh` | rounds_ctrl 从配置到 while 循环的完整数据流；最后逐行 diff 脚本 |

## ⑤ ScalingInter-RL vs AgentGym-RL 配置差异表（BabyAI 对照，逐行 diff）

两脚本 71/72 行，仅 11 处不同（行号分别为 `examples/train/AgentGym-RL/babyai_train.sh` 与 `examples/train/ScalingInter-RL/babyai_train.sh`）：

| 参数 | AgentGym-RL（基线） | ScalingInter-RL | 含义与设计动机 |
|---|---|---|---|
| `algorithm.rounds_ctrl.type` | `fixed`（L41） | `scaling_inter_stepwise`（L41） | 轮数调度策略：固定 vs 阶梯渐进 |
| `algorithm.rounds_ctrl.rounds` | `20`（L42） | `[6,13,20]`（L43） | 固定 20 轮 vs 6→13→20 三档地平线 |
| `algorithm.rounds_ctrl.steps_scaling_inter` | 未设置（yaml 默认 100） | `100`（L42） | 每 100 个训练 step 升一档（ray_trainer.py:232-236 的整除索引） |
| `rollout_sample_num`（→`rollout.n`） | `8`（L24,55） | `4`（L24,56） | GRPO 组内采样数减半：短地平线阶段方差小，省算力 |
| `train_batch_size` | `16`（L25） | `32`（L25） | 批量翻倍补样本数下降 |
| `ppo_inner_epochs` | `1`（L28,59） | `2`（L28,60） | 每批多一轮策略更新 |
| `total_epoches` | `10`（L30） | `20`（L30） | 总 epoch 翻倍（配合渐进档位需要更长训练） |
| `data.max_prompt_length` | `1024`（L45） | `512`（L46） | BabyAI 指令短，压缩首轮 prompt |
| `data.max_response_length` | `4096`（L46） | `8192`（L47） | 多轮轨迹总 token 上限翻倍（长地平线需要） |
| `rollout.max_tokens` | `200`（L57） | `512`（L58） | 单轮生成上限放大 2.56×（每轮 thought+action 更长） |
| 脚本行数 | 71 | 72 | ScalingInter 多 1 行（rounds 列表单独一行） |

**其余全部相同**：`kl_coef=0.001`、`lr=1e-6`、`adv_estimator=grpo`、`Qwen2.5-7B-Instruct`、`env_addr=:36005`、`timeout=600`、`gpu_memory_utilization=0.7`、`max_model_len=32768`、`tensor_model_parallel_size=1`、`kl_loss_type=low_var_kl`、`save_freq=25`。

**轮数阶梯的实际执行**：`StepRoundsScheduler`（ray_trainer.py:230-242）以 `global_steps//100` 取 `rounds_ls` 下标（越界封顶最后档），fit 循环每个训练 step 把 `max_rounds` 写入 rollout 批的 `meta_info`（L770），worker 侧 `while rounds < max_rounds` 消费（vllm_rollout.py:247）。

## 附：README 与代码不符处（深读实测）

1. AgentGym/README.md:51 称 API 为 `/createEnv`；客户端实际 `POST /create`（babyai.py:35、webarena.py:30、searchqa.py:30）。
2. 顶层 README.md:98 称 EnvClient 有 `available_actions()`；`BaseEnvClient` 仅 4 方法（env.py:12-32），babyai/webarena/searchqa 均未实现。
3. ppo_trainer.yaml:67 注释误贴："max_rounds: 10 # Maximum token length of a single response per turn."（是 max_tokens 的注释文案）。
4. 上游 AgentGym README 的 14 环境表不含 searchqa；它是 AgentGym-RL 为深度搜索场景新增（envs/__init__.py:14）。
5. task.py:23 自述 batch generation 未实现——`_generate_experience_batch` 实为串行 for（task.py:158-167）。
6. `ActionFormat` 枚举（types.py:23-26）与 `BaseEnvClient(action_format=...)`（env.py:9-10）存在但三个代表性客户端均未使用——协议预留未接线。
7. `ActionWithTought` 拼写错误（types.py:58，应为 Thought）。
