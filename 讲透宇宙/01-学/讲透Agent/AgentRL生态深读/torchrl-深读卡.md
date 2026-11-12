# torchrl 深读卡 —— PyTorch 官方通用 RL 组件库（一切皆 TensorDict 的可组合全栈）

> **定位**：Meta/PyTorch 出品的通用 RL 组件库。与 verl（只做 LLM 训练层）互补：torchrl 提供 RL 全栈一等公民组件——环境→采集→回放→模型→损失→训练器，每层可独立组合替换；近年加出 LLM 后训练（GRPO/SFT/vLLM/SGLang）与多智能体专线。
> **本地**：`~/ai/torchrl`（46M 全仓含 .git 12M，434 核心 .py 实测）@3b6b5b9 ｜**深读**：deepwiki 40 子页（2025-12-14 索引）+ 本地 grep 全锚点重核（多处漂移，见 §四注）

## 一、组件栈分层（全本地实测）

| 层 | 职责 | 关键实体（本地锚点）|
|---|---|---|
| 数据地基* | 统一载体+类型系统 | TensorDict/TensorSpec（外部 tensordict 库，pyproject.toml:47 锁 `>=0.14,<0.15`）；`TensorSpec`（data/tensor_specs.py:607）/`Composite`（:5042）——验证/采样/编码三合一 |
| 环境 | 世界模拟 | `EnvBase`（envs/common.py:404，元类 _EnvPostInit:306；rollout:3449；_step/_reset/_set_seed 契约 :3097/:3104/:3345）；`TransformedEnv`+`Transform`（transforms/_base.py:944/:178，已拆 28 文件）；`SerialEnv`/`ParallelEnv`（batched_envs.py:1546/:1918）；**22 个后端**（envs/libs/ 实测：gym/dm_control/brax/jumanji/isaacgym/isaac_lab/vmas/pettingzoo/meltingpot/openspiel/smacv2/habitat/robohive/libero/genesis/mjlab/mujoco_playground/procgen/envpool/safety_gymnasium/unity_mlagents/openml）|
| 采集 | 数据生产 | `BaseCollector`（collectors/_base.py:220）→`Collector`（_single.py:297）/`AsyncCollector`（:18）→`MultiSync/MultiAsyncCollector`（:27/:25）；LLM 专线 collectors/llm/ray_collector.py |
| 回放 | 经验存储 | `ReplayBuffer`（replay_buffers.py:181）= **Storage×Sampler×Writer 组合式**：Storage（storages.py:172 家族，LazyMemmapStorage:1769/CompressedListStorage:2136）×Sampler（samplers.py:106，PrioritizedSampler:942/SliceSampler:1696）×Writer（writers.py:58，RoundRobinWriter:197）|
| 模型 | nn 与 TD 桥接 | `SafeModule`（tensordict_module/common.py:97）/`SafeProbabilisticModule`（probabilistic.py:36）；`ProbabilisticActor`（actors.py:146）/`QValueModule`（:500）；探索 EGreedyModule:38/OU:428（exploration.py）；`MLP`（models/models.py:29）；MARL `MultiAgentMLP`（models/multiagent.py:348）+VDN/QMixer（:935/:1008）|
| 算法 | 损失函数族 | `LossModule`（objectives/common.py:87，set_keys:379）——**36 个子类实测**：PPO 三兄弟（ppo.py:109/1082/1458）、SAC:59/DiscreteSAC:979、DQN:34/分布态 DQN:389、DDPG:27/TD3:27/TQC:20、CQL/IQL/REDQ/CrossQ、Dreamer×3/V3×3、DT×2、BC/GAIL/RND/ACT…；价值估计五件套 advantages.py：TD0:962/TD1:1245/TDλ:1541/GAE:1871/VTrace:2484（ValueEstimators 枚举 utils.py:48）|
| 训练编排 | 循环+hook | `Trainer`（trainers/trainers.py:320，register_op:1058，TrainerHookBase:173）+ helpers（trainers/helpers/envs.py:47 LIBS 字典）|
| LLM 后训练 | RLHF/RLVR | `GRPOLoss`（objectives/llm/grpo.py:355）/CISPO:1004/DAPO 不对称 clip（:1010 `clip(w,[1-eps_low,1+eps_high])`）；SFTLoss（sft.py:104）；推理后端 `TransformersWrapper`（policies/transformers_wrapper.py:40）/`vLLMWrapper`（vllm_wrapper.py:88）+backends/{sglang,vllm}；Agent 循环 `ChatEnv`（envs/llm/chat.py:60）/GSM8KEnv（datasets/gsm8k.py:143）+transforms：KLComputation:1369/RetrieveLogProb:561（kl.py）、PythonInterpreter:1051/`MCPToolTransform`:1521（tools.py）；数据结构 History TensorClass（data/llm/history.py:465）|

*tensordict 是独立 pytorch 官方库，torchrl 建在其上——这是与 verl（自研 DataProto）的根本架构差异。

## 二、核心架构：TensorDict 单一数据流

- **一切组件读/写 TensorDict**：环境 rollout 产出 TD → Collector 打批 → ReplayBuffer 存取 TD → TensorDictModule 前向读 TD 写 TD → LossModule 吃 TD 吐 `loss_*` 键 → Trainer 汇总（trainers.py:2037 `sum(loss_components)`）。键名即接口，`step_mdp`（envs/utils.py:327）做 done 截断换位。
- **LossModule 双绝**：①`_AcceptedKeys`+`set_keys()`（common.py:157/379）声明并允许重命名输入输出键；②`convert_to_functional`（common.py:426）把 nn.Module 参数变函数式——target 网络与分布式靠它零拷贝切换。
- **组合式回放**是全库设计哲学的最佳标本：PER=PrioritizedSampler 换进任意 Storage，memmap 大缓冲=LazyMemmapStorage 换进任意 Sampler，互不感知。

## 三、与本项目知识的对位

| torchrl 实体 | 讲透系列 | verl / 生态 |
|---|---|---|
| EnvBase._step/_reset + TensorSpec | 讲透RL/00 MDP 地基 | verl 无环境层（rollout 内置）|
| PPOLoss/ClipPPOLoss（ppo.py:109/1082）| 讲透RL/02 策略梯度 | verl core_algos.py:70-110 同构 |
| GAE/VTrace（advantages.py:1871/2484）| 讲透RL/02 §优势估计 | verl advantage 函数族 |
| GRPOLoss（llm/grpo.py:355）| 讲透RL/03 RLHF·GRPO | verl 同名；RAE v5 exp3 真链路对照源码 |
| DQNLoss+EGreedy+LazyMemmap | 讲透RL/01 Q-Learning·DQN | cleanrl 单文件教学版对照 |
| ReplayBuffer 组合式 | 讲透RL/07 全景地图 | verl 无通用 RB（DataProto 流式）|
| MCPToolTransform（tools.py:1521）| 讲透RL/06 RL+系统软件 | 直通 Agent框架案例/MCP 三件卡 |

## 四、关键入口（本地验证）

```
torchrl/envs/common.py:404              # EnvBase（rollout:3449）
torchrl/envs/transforms/_base.py:944    # TransformedEnv/Transform:178
torchrl/collectors/_single.py:297       # Collector（旧名 SyncDataCollector 已删）
torchrl/data/replay_buffers/replay_buffers.py:181  # ReplayBuffer
torchrl/modules/tensordict_module/actors.py:146    # ProbabilisticActor
torchrl/objectives/common.py:87         # LossModule（set_keys:379）
torchrl/objectives/ppo.py:109           # PPOLoss｜llm/grpo.py:355 GRPOLoss
torchrl/trainers/trainers.py:320        # Trainer
```

**注**：deepwiki 索引（2025-12-14）→本地 3b6b5b9 多处漂移：EnvBase 314→404；transforms.py→拆成 _base.py 等 28 文件（Transform 189→178）；Collector 家族从 collectors.py:8-61 拆成 _single/_multi_* 独立文件且 SyncDataCollector 改名 Collector；QValueModule 468→500；Trainer 106→320。本卡一律以本地 grep 为准。

## 五、40 页深读子页地图（12 组）

总览：1｜数据：2/2.1 TensorDict/2.2 TensorSpec｜环境：3/3.1 EnvBase/3.2 transforms/3.3 后端/3.4 并行｜采集：4/4.1/4.2｜回放：5/5.1/5.2｜模型：6/6.1 TDM/6.2 actors/6.3 分布/6.4 网络/6.5 探索｜算法：7/7.1 LossModule/7.2 on-policy/7.3 off-policy/7.4 value-based/7.5 价值估计｜训练：8/8.1 Trainer/8.2 helpers｜LLM：9/9.1 wrapper/9.2 数据结构/9.3 目标/9.4 环境工具｜MARL：10｜教程：11｜工程：12/12.1/12.2

**精选 10**：2.1（TensorDict=全库中心抽象）、3.1（_step/_reset 契约+specs）、5.1（组合式 RB 哲学）、7.1（_AcceptedKeys/set_keys/functional 化——最值得偷的 API 设计）、7.5（五种优势估计器统一接口）、8.1（Trainer hook 生命周期）、9.3（GRPO/DAPO/CISPO：verl 之外的另一实现）、9.4（ChatEnv+MCPToolTransform+PythonInterpreter：Agent RL 关键页）、10（agent 分组/参数共享/MAPPO vs IPPO）、11（coding_ppo/dqn/ddpg 从零教程）。

## 六、与"我们"的关系（一句话）

torchrl=组件工业级、cleanrl=单文件教学级、verl=LLM 训练专精，三者构成学 RL 的完整三角——讲透RL/00-03 的每个算法在 torchrl 里就是一个 LossModule 子类（36 个实测），rl_agent 的 loss 隔离在 `convert_to_functional` 里见到工业版；而 `MCPToolTransform`（tools.py:1521）已把 MCP 工具协议接进 RL 环境循环，是 Agent框架案例 MCP 三件卡与 Agent RL 生态的交叉点。

---
生成：2026-08-20 · deepwiki 索引 2025-12-14（eaaa11c）+ 本地 @3b6b5b9 全锚点 grep 重核（434 py/46M/22 后端/36 LossModule 全实测）
