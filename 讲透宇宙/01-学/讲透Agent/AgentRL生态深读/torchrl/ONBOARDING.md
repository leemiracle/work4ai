# TorchRL 新人上手指南

> 基于 `~/ai/torchrl` 的 knowledge-graph 深度分析（understand-anything 管线，2026-08-20，commit `3b6b5b9c`）。全图 2267 节点 / 5854 边 / 10 架构层 / 13 步引导路线；文件级节点 474 个（torchrl/ 核心 434 个 py + 根配置与文档）。所有 fan-in 数字为图谱实测。

## ① 项目概览

| 项 | 内容 |
|---|---|
| 名称 | torchrl（PyTorch 官方 RL 库） |
| 语言 | Python（核心），C++/CUDA（`csrc/` 线段树内核与 pybind11 绑定） |
| 框架 | PyTorch（+ tensordict 为数据底座）、pytest、GitHub Actions、Sphinx |
| 定位 | 模块化强化学习库：不是单一算法实现，而是可自由组装的 RL 系统零件箱 |

**一句话**：以 TensorDict 为通用数据容器，串联环境接入（EnvBase/TransformedEnv）→ 数据采集（Collector）→ 回放缓冲（ReplayBuffer）→ 策略模块（TensorDictModule）→ 损失算法（PPO/SAC/DQN 等十余种）全链路，支持多进程/分布式训练、40+ 环境后端，并提供 LLM 后训练（RLHF/GRPO）与多智能体扩展。

三大设计理念（README 开篇，理解全库的钥匙）：
1. **数据全链路带名字/结构/设备**——TensorDict + TensorSpec 是所有组件的通用语；
2. **各组件可独立替换**——回放缓冲、采集器、损失全是组合件而非黑盒；
3. **从本地原型到分布式无需改数据模型**——同一套 TensorDict 语言平滑扩展。

## ② 架构分层（10 层）

数据自底向上流动：核心基础 → 数据 → 环境 → 模块 → 采集 → 损失 → 训练；分布式/渲染记录/测试为横切支撑。

| # | 层 | 职责 | 关键文件（一句话） |
|---|---|---|---|
| 1 | 核心基础层 | 包根入口、全库共享工具、C++/CUDA 线段树内核 | `torchrl/__init__.py`（版本初始化 + monkey-patch torch 分布逆变换缓存）；`torchrl/_utils.py`（多进程/RNG/设备工具，**fan-in 125 全库最高**）；`torchrl/csrc/segment_tree.h`（CPU 线段树模板，优先采样的内核）；`torchrl/csrc/pybind.cpp`（`_torchrl` 原生扩展入口） |
| 2 | 数据层 | TensorSpec 规格、回放缓冲、离线数据集、LLM 数据 | `torchrl/data/tensor_specs.py`（spec 体系中枢，fan-in 95）；`torchrl/data/replay_buffers/replay_buffers.py`（回放缓冲核心）；`torchrl/data/replay_buffers/storages.py`（内存/memmap 存储后端）；`torchrl/data/replay_buffers/samplers.py`（随机/优先级采样器）；`torchrl/data/llm/prompt.py`（SFT 提示张量结构） |
| 3 | 环境层 | EnvBase 契约、20+ 第三方环境适配、Transforms、LLM/世界模型环境（128 文件，最大层） | `torchrl/envs/common.py`（EnvBase 根类，fan-in 62）；`torchrl/envs/utils.py`（step_mdp/check_env_specs，fan-in 65）；`torchrl/envs/libs/gym.py`（Gymnasium 适配样板）；`torchrl/envs/transforms/_base.py`（Transform/TransformedEnv 核心）；`torchrl/envs/llm/chat.py`（ChatEnv 对话环境） |
| 4 | 模块层 | TensorDict 化网络模块、策略头、分布、探索、规划器、推理服务 | `torchrl/modules/tensordict_module/common.py`（SafeModule 基类）；`.../actors.py`（18 种策略头）；`.../probabilistic.py`（概率采样层）；`torchrl/modules/models/models.py`（MLP/ConvNet/Dueling 骨干）；`torchrl/modules/distributions/continuous.py`（TanhNormal 等 RL 专用分布） |
| 5 | 采集层 | 驱动"策略读环境"的 rollout 发动机，单进程→多进程→Ray 分布式 | `torchrl/collectors/_base.py`（采集器抽象基类 + 权重同步生命周期）；`torchrl/collectors/_single.py`（单进程 rollout 最小完整实现）；`torchrl/collectors/_multi_base.py`（多进程编排）；`torchrl/collectors/llm/base.py`（LLM rollout 采集器） |
| 6 | 损失函数层 | 十余种 RL 算法的数学核心 | `torchrl/objectives/common.py`（LossModule 骨架，fan-in 42）；`torchrl/objectives/ppo.py`（ClipPPOLoss/KL 变体）；`torchrl/objectives/sac.py`（最大熵 + 双 Q + 自适应温度）；`torchrl/objectives/llm/grpo.py`（GRPO/DAPO，LLM 后训练）；`torchrl/objectives/value/advantages.py`（GAE 等 6 种价值估计器） |
| 7 | 训练层 | Trainer 钩子编排、算法配置工厂、检查点 | `torchrl/trainers/trainers.py`（训练中枢 + 19 个钩子）；`torchrl/trainers/algorithms/configs/__init__.py`（Hydra 配置注册表总入口）；`torchrl/checkpoint/_checkpoint.py`（组件化检查点） |
| 8 | 分布式与权重同步层 | WeightSyncScheme 框架、_comm 通信原语、vLLM/SGLang NCCL 同步 | `torchrl/weight_update/weight_sync_schemes.py`（权重同步抽象框架）；`torchrl/_comm/mailbox.py`（生产者-消费者邮箱原语）；`torchrl/weight_update/llm/vllm_nccl.py`（vLLM NCCL 热加载） |
| 9 | 渲染与记录层 | 环境渲染器（rlrender）、多后端日志与录像 | `torchrl/record/loggers/common.py`（Logger 基类，自动服务化）；`torchrl/record/recorder.py`（VideoRecorder/TensorDictRecorder）；`torchrl/render/config.py`（rlrender CLI 配置） |
| 10 | 测试与工程支撑层 | mock 环境家族、分布式测试助手、构建与 CI 配置 | `torchrl/testing/mocking_classes.py`（47 个 mock 环境覆盖 EnvBase 语义各切面）；`pyproject.toml`（PEP 621 + 20+ extras）；`Makefile`/`pytest.ini`（CI 工程链） |

## ③ 核心概念

读懂这 12 个概念，就读懂了 torchrl 的设计语言：

1. **TensorDict 中心架构**：一切数据（观测/动作/奖励/done）都是带名字的张量字典，环境、采集器、网络、损失全部说这门语言——这是"换组件不换代码"的根本机制。
2. **TensorSpec 规格系统**（`tensor_specs.py`）：描述每条数据的形状/dtype/取值域（OneHot/Bounded/Composite…），是组件间的"数据语法"；`Composite` 把观测-动作-奖励组装成规格树；`encode/project/rand` 负责编码与投影。
3. **EnvBase 契约**（`envs/common.py`）：所有环境的抽象根类——`_reset`/`_step`/`_step_and_maybe_reset` 统一接口，输入输出皆 TensorDict，batch 维度即并行环境数；done 语义（terminated/truncated）在此严格定义。
4. **step_mdp 与 next_\* 键约定**（`envs/utils.py`）：`next_observation` 提升为 `observation` 的时间步切换是全库数据处理的心跳；`check_env_specs` 用随机 rollout 对账 spec 与真实数据。
5. **TransformedEnv 可组合变换**（`transforms/_base.py`）：归一化/裁剪/dtype/奖励缩放全部做成可组合 Transform 套在任意 EnvBase 外——"装饰而非侵入"哲学的最佳体现（变换体系被 86 处依赖）。
6. **Collector 采集器**：数据生产循环的发动机，输出批量 rollout TensorDict；从 `Collector`（单进程）到 `MultiSyncDataCollector`（多进程）到 Ray 分布式，接口不变。
7. **ReplayBuffer 三件套 + Transform**：`storage`（存哪里：内存/memmap/栈）× `sampler`（怎么采：随机/优先级线段树/轨迹切片）× `writer`（怎么写：RoundRobin 游标）三轴正交、独立可换；优先级采样的性能内核在 `csrc/` 的 C++/CUDA 线段树。
8. **TensorDictModule / SafeModule**（`tensordict_module/common.py`）：声明 `in_keys`/`out_keys` 的 nn.Module，从 TensorDict 读输入、写输出——策略由此成为可交给采集器、也可单独调用的普通模块。
9. **ProbabilisticActor 与概率头**（`probabilistic.py` + `distributions/continuous.py`）：网络输出分布参数（如 TanhNormal），TensorSpec 约束采样域；探索（EGreedy/OU 过程）以模块形式包裹确定性策略并可退火。
10. **LossModule 函数式骨架**（`objectives/common.py`）：损失内部持有策略/价值网络，接收 TensorDict 批次输出损失字典；自动管理 `loss_mask`（padding/越界 bootstrap 掩码）、目标网络注册与软/硬更新（`objectives/utils.py`）。
11. **Trainer 钩子系统**（`trainers/trainers.py`）：采集 → 回放 → 损失 → 优化器 → 日志/评估/检查点 的每一步都是可插拔 `TrainerHookBase`，把前述所有零件装配成端到端训练。
12. **权重同步与 LLM 后训练**：`WeightSyncScheme`（指令-ACK 协议 + 多种传输后端）让 learner 与采集进程解耦；ChatEnv（对话即环境）+ GRPOLoss + vLLM/SGLang NCCL 热加载，把同一套 RL 数据流用于大模型微调。

## ④ 引导式学习路线（tour 13 步）

| 步 | 主题 | 说明 | 涉及文件 |
|---|---|---|---|
| 1 | 项目概览：TorchRL 是什么 | 从 README 开始：零件箱定位 + 三大设计理念，是理解后续每一步的钥匙 | `README.md` |
| 2 | 库根入口与全局工具 | 包根初始化版本并加载 C++ 扩展；`_utils.py` fan-in 125，先扫一眼避免后面反复查定义 | `torchrl/__init__.py`、`torchrl/_utils.py` |
| 3 | 数据底座：TensorSpec 规格系统 | "数据全程有名字/结构/批维度/设备"契约的落实处；Composite 组装规格树，是组件间的数据语法 | `torchrl/data/tensor_specs.py`、`torchrl/data/utils.py` |
| 4 | 环境系统：EnvBase 契约 | 统一 `_reset`/`_step`/`_step_and_maybe_reset`，TensorDict 进出、batch 维即并行数——异构环境拉到同一数据模型 | `torchrl/envs/common.py`、`torchrl/envs/utils.py` |
| 5 | 第三方环境适配层 | Gymnasium/Brax/DMControl/MJX 包装成 EnvBase；GymWrapper 处理像素/状态双模式与批维度推断，看懂一个适配器=看懂全部 | `torchrl/envs/libs/__init__.py`、`torchrl/envs/libs/gym.py` |
| 6 | TransformedEnv 可组合变换 | 观测/动作/奖励预处理全部可组合（fan-in 86）；与第 3 步规格系统配合无缝——"装饰而非侵入" | `torchrl/envs/transforms/_base.py`、`torchrl/envs/transforms/transforms.py` |
| 7 | 采集器：rollout 的发动机 | 单进程 Collector 是数据流最小完整示例；MultiSync 等多环境并行模式接口一致 | `torchrl/collectors/__init__.py`、`torchrl/collectors/_single.py`、`torchrl/collectors/_multi_base.py` |
| 8 | 回放缓冲：仓储与调度 | 三正交维度组合：storages（存哪里）× samplers（怎么采）× writers（怎么写），独立可换 | `torchrl/data/replay_buffers/{replay_buffers,storages,samplers,writers}.py` |
| 9 | 策略模块：TensorDict 化的 nn.Module | SafeModule 声明 in/out_keys 从 TensorDict 读写；actors.py 组合出 Actor/ProbabilisticActor/QValueActor 等现成策略头 | `torchrl/modules/tensordict_module/{common,actors}.py` |
| 10 | 网络骨干、探索与概率头 | models.py 骨干 + exploration.py 模块式探索（带退火）+ probabilistic.py 采样分布，三层叠加成完整可训练策略 | `torchrl/modules/models/models.py`、`.../tensordict_module/{exploration,probabilistic}.py` |
| 11 | 损失算法：RL 数学核心 | LossModule 内持网络、收 TensorDict 批、出损失字典；PPO 与 SAC 对比阅读看清 on/off-policy 数据流真实差异 | `torchrl/objectives/{common,ppo,sac}.py` |
| 12 | Trainer：训练循环的指挥家 | 钩子系统编排采集→回放→损失→优化→日志/检查点；make_trainer 展示配置驱动的全栈组装 | `torchrl/trainers/trainers.py`、`torchrl/trainers/helpers/trainers.py` |
| 13 | 进阶应用：世界模型与 LLM 环境 | DreamerEnv 在 latent 空间"想象"轨迹（WorldModel 本身也是 EnvBase！）；envs/llm 把 RL 数据流用到 LLM 训练——同一套语言从玩具控制读到前沿研究 | `torchrl/envs/model_based/{dreamer,imagined}.py`、`torchrl/envs/llm/__init__.py` |

## ⑤ 文件地图（40 个最值得深讲的文件，按层组织）

> 全图 474 个文件级节点中精选 40 个（按"被依赖程度 × 概念权重"挑选），供 understand-explain 逐个深讲。

**核心基础层（2）**

| 文件 | 职责 |
|---|---|
| `torchrl/_utils.py` | 全库 fan-in 最高（125）的底层工具：多进程 start method、种子派生、RNG 保护、设备探测、Ray remote 元类 |
| `torchrl/csrc/segment_tree.h` | CPU 非递归线段树模板：O(logN) 单点更新/区间归约 + 前缀和下界 ScanLowerBound（优先级采样内核） |

**数据层（6）**

| 文件 | 职责 |
|---|---|
| `torchrl/data/tensor_specs.py` | TensorSpec 体系中枢（fan-in 95）：全部 spec 类型 + Box 值域 + encode/project/rand 编码投影 |
| `torchrl/data/replay_buffers/replay_buffers.py` | ReplayBuffer 基类：组合 storage/writer/sampler/transform 四组件，派生 Prioritized/TensorDict/Remote 等变体 |
| `torchrl/data/replay_buffers/storages.py` | 存储后端全家桶：List/Tensor/LazyMemmap/LazyStack/Ensemble，含 memmap 全局清理 |
| `torchrl/data/replay_buffers/samplers.py` | 采样器全家桶：Random/Prioritized（线段树加权）/Slice（轨迹边界）/PromptGroup（LLM 分组） |
| `torchrl/data/replay_buffers/writers.py` | 写入器全家桶：RoundRobin 等写入策略、游标与世代（generation）追踪 |
| `torchrl/data/llm/prompt.py` | SFT 提示数据：PromptData tensorclass（input_ids/attention_mask/prompt_rindex）+ 标签掩码 |

**环境层（7）**

| 文件 | 职责 |
|---|---|
| `torchrl/envs/common.py` | 环境体系中枢：EnvBase 根类（step/reset/rollout、spec 管理、done 语义、seed/设备/编译支持） |
| `torchrl/envs/utils.py` | envs 核心工具（fan-in 65）：step_mdp 时间步切换、check_env_specs 对账、MARL 分组校验 |
| `torchrl/envs/libs/gym.py` | Gym/Gymnasium 全功能适配：像素/状态双模式、spec 双向转换注册表、后端切换上下文 |
| `torchrl/envs/transforms/_base.py` | Transform 基类（正/逆变换链 + transform_*_spec 钩子）与 TransformedEnv 容器 |
| `torchrl/envs/transforms/vecnorm.py` | VecNormV2：并行环境间聚合运行统计的观测/奖励归一化，torch.compile 兼容 |
| `torchrl/envs/batched_envs.py` | 向量化环境：SerialEnv/ParallelEnv 执行器、进程 worker 主循环、共享内存通信 |
| `torchrl/envs/llm/chat.py` | ChatEnv：以聊天 History 为中心的 LLM 环境，tokens/text/history 三模式自动生成 spec |

**模块层（5）**

| 文件 | 职责 |
|---|---|
| `torchrl/modules/tensordict_module/common.py` | SafeModule（TensorDict 读写基类）、VmapModule 与兼容性检查工具 |
| `torchrl/modules/tensordict_module/actors.py` | 18 个策略头：Actor/ProbabilisticActor/QValueActor/ActorCriticOperator/扩散策略/VLA 多步动作 |
| `torchrl/modules/tensordict_module/probabilistic.py` | SafeProbabilisticModule：在分布之上接受 TensorSpec 约束采样域，概率策略的采样层基类 |
| `torchrl/modules/models/models.py` | 网络骨干库：MLP/ConvNet/Dueling DQN/DDPG 全家族/Decision Transformer actor |
| `torchrl/modules/distributions/continuous.py` | RL 专用连续分布：TanhNormal/TanhDelta/TruncatedNormal/Delta，适配 TorchScript 与 compile |

**采集层（4）**

| 文件 | 职责 |
|---|---|
| `torchrl/collectors/_base.py` | BaseCollector：权重同步 scheme 生命周期、轨迹迭代协议、profiling 钩子 |
| `torchrl/collectors/_single.py` | 单进程 Collector：进程内驱动 env.step 与策略前向——TensorDict 中心数据流的最小完整示例 |
| `torchrl/collectors/_multi_base.py` | 多进程采集基类：worker 启动、队列/管道通信、多回放缓冲装配、权重同步分发 |
| `torchrl/collectors/llm/base.py` | LLMCollector：单进程驱动语言模型策略与 ChatEnv，管理策略版本与 vLLM 权重更新 |

**损失函数层（7）**

| 文件 | 职责 |
|---|---|
| `torchrl/objectives/common.py` | LossModule 骨架（fan-in 42）：in/out 键管理、loss_mask 自动掩码、目标网络注册、函数式训练接口 |
| `torchrl/objectives/utils.py` | 公共工具箱（fan-in 37）：价值估计器注册分发、软/硬目标网络更新器、next_state_value |
| `torchrl/objectives/ppo.py` | PPOLoss 基类 + ClipPPOLoss（比率裁剪）+ KLPENPPOLoss（自适应 KL 惩罚） |
| `torchrl/objectives/sac.py` | SACLoss：最大熵 + TanhNormal 策略 + 双 Q 取小 + 温度 α 自适应；离散版 DiscreteSACLoss |
| `torchrl/objectives/dreamer_v3.py` | DreamerV3 三件套：世界模型损失（symlog/two-hot + balanced KL）+ actor + value |
| `torchrl/objectives/llm/grpo.py` | GRPOLoss 及 DAPO/CISPO 变体 + MCAdvantage（Ray 分布式蒙特卡洛优势），大模型 RL 微调核心 |
| `torchrl/objectives/value/advantages.py` | 6 种价值估计器模块：TD0/TD1/TDλ/GAE/MultiAgentGAE/VTrace |

**训练层（3）**

| 文件 | 职责 |
|---|---|
| `torchrl/trainers/trainers.py` | Trainer 主类（56 方法，主循环 + checkpoint + 远程权重发布）+ 19 个 TrainerHookBase 钩子 |
| `torchrl/trainers/algorithms/configs/__init__.py` | 配置系统总入口：按 env/network/collector/hook 等分组惰性注册到 Hydra ConfigStore 的可组合配置注册表 |
| `torchrl/checkpoint/_checkpoint.py` | 组件化检查点：注册/manifest/版本迁移、多格式适配器、RNG 状态捕获、latest/best 轮转保留 |

**分布式与权重同步层（3）**

| 文件 | 职责 |
|---|---|
| `torchrl/weight_update/weight_sync_schemes.py` | 权重同步框架：指令-ACK 协议、后台接收线程、full/dtensor/LoRA 权重策略、后端注册表 |
| `torchrl/_comm/mailbox.py` | 基于 multiprocessing.connection 的生产者-消费者邮箱：submit/wait_for_work/drain 语义 + 对端存活检测 |
| `torchrl/weight_update/llm/vllm_nccl.py` | vLLM NCCL 同步：自定义通信组广播权重并触发热加载（训练器 ↔ vLLM worker） |

**渲染与记录层（1）**

| 文件 | 职责 |
|---|---|
| `torchrl/record/loggers/common.py` | Logger 基类：`__init_subclass__` 自动把子类包装为 process/ray 服务后端，含视频编码与指标安全化 |

**测试与工程支撑层（2）**

| 文件 | 职责 |
|---|---|
| `torchrl/testing/mocking_classes.py` | 47 个 mock 环境（嵌套 key/多智能体/动态 spec/故障注入…），EnvBase 语义的全切面测试网 |
| `pyproject.toml` | 构建与依赖中枢：setuptools_scm + 20+ extras（llm/grpo/marl/brax…）+ rlrender CLI 与 vLLM 插件入口 |

## ⑥ 复杂度热点（complex 级 × fan-in Top 10）

> 全图 474 个文件节点中 244 个标为 complex；下表按"复杂度 × 被依赖数"取前十，新人请按"接近方式"由浅入深。

| # | 文件 | fan-in | 为什么难 | 新人如何接近 |
|---|---|---|---|---|
| 1 | `torchrl/_utils.py` | 125 | 聚合了多进程、RNG 状态、CUDA、Ray 元类等互不相干却全库依赖的工具，横切所有子系统 | 不通读；当字典查——遇到 `_set_seed`/`start_processes`/device 解析再回来看 |
| 2 | `torchrl/data/tensor_specs.py` | 95 | spec 类型多、形状推导与 encode/project 语义微妙，是所有组件的隐式契约 | 先只用 `Composite`+`Bounded` 跑通，再读 `encode`/`to`/`index` 的形状规则 |
| 3 | `torchrl/envs/utils.py` | 65 | `step_mdp` 的 next_\* 提升规则与 `check_env_specs` 的对账逻辑，牵一发动全身 | 用 `check_env_specs(env)` 跑一次报错信息来学：错误消息本身就是教程 |
| 4 | `torchrl/envs/common.py` | 62 | EnvBase 承载 step/reset/rollout、done 双语义（terminated/truncated）、spec 锁定、编译支持 | 从 `rollout()` 的调用链自顶向下读，先忽略 `_EnvWrapper` 与属性缓存 |
| 5 | `torchrl/objectives/common.py` | 42 | LossModule 的函数式 API + 目标网络注册 + loss_mask 掩码三个机制交织 | 先读 `forward` 返回的损失字典结构，再对照 PPO 的 `distance_loss` 用法 |
| 6 | `torchrl/objectives/utils.py` | 37 | 价值估计器注册分发 + SoftUpdate 硬更新 + vmap 伪映射，元编程密度高 | 只抓两件事：`next_state_value` 怎么算、`SoftUpdate` 怎么挂 |
| 7 | `torchrl/data/replay_buffers/storages.py` | 18 | LazyMemmapStorage 的 mmap 生命周期与信号处理、多种存储的 collate 差异 | 从 `ListStorage`→`TensorStorage`→`LazyMemmapStorage` 递进读，最后看清理信号 |
| 8 | `torchrl/data/replay_buffers/replay_buffers.py` | 17 | 四组件组合 + 预取队列 + 分布式服务化，状态同步路径多 | 先 `ReplayBuffer(storage=..., sampler=...)` 手工组装一次，再读 Prioritized 变体 |
| 9 | `torchrl/envs/transforms/_base.py` | 17 | 正/逆变换链与十余个 `transform_*_spec` 钩子的调用时机 | 从 `TransformedEnv(env, Compose([t1, t2]))` 的执行顺序逆推 `_call` 与 spec 钩子 |
| 10 | `torchrl/weight_update/weight_sync_schemes.py` | 17 | 指令-ACK 协议 + 后台接收线程 + 多传输后端，并发与分布式语义叠加 | 本地单机先跳过；到多进程训练再看 sender/receiver 生命周期的时序图 |

## ⑦ 分析范围说明

本图谱通过 `.understand-anything/.understandignore` 限定深读范围：**核心包 `torchrl/`（434 个 py）+ 仓库根配置与文档**；排除 `docs/`、`examples/`、`test/`、`tutorials/`、`gallery/`、`benchmarks/`、`sota-check/`、`sota-implementations/`、`knowledge_base/`、`packaging/`、`scripts/`、`.github/` 等目录（其内容叙事由 deepwiki 渠道覆盖）。文件级节点共 474 个 = torchrl/ 下 434 个 py + 21 个非 py 资产（`csrc/` C++/CUDA、MuJoCo XML、数据集 JSON 等）+ 19 个根级配置/文档（`pyproject.toml`、`README.md`、CI 配置等）。
