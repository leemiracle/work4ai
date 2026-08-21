# CleanRL 新人上手指南

> 基于对 `~/ai/cleanrl` 的知识图谱分析（`.understand-anything/knowledge-graph.json`，2026-08-20 生成，commit `fe8d8a0`，487 节点 / 1052 边 / 7 层 / 11 步导览）。文中文件路径相对仓库根目录；算法脚本实际位于 `cleanrl/cleanrl/` 包目录下。本指南的文件地图将作为后续 understand-explain 逐文件深讲的清单。

## ① 项目概览

| 项 | 内容 |
|---|---|
| 名称 | CleanRL（cleanrl 2.0.0b1） |
| 描述 | 提供高质量**单文件实现**的深度强化学习算法库 |
| 语言 | Python 为主（另有 Dockerfile / Terraform / Shell / SLURM 模板 / MkDocs 文档） |
| 框架 | PyTorch + Gymnasium；JAX/Flax/Optax 第二技术栈；tyro（CLI）、TensorBoard、Weights & Biases（实验追踪）、Optuna（调参）、EnvPool（向量化环境）、Docker、Terraform（AWS 云端）、MkDocs、pytest、GitHub Actions |

**单文件哲学**是理解本项目的钥匙：每个算法变体（ppo / dqn / sac / td3 / c51 等，含 PyTorch 与 JAX 双栈）是一个**独立可执行脚本**——数据收集、网络定义、训练循环、日志追踪全部在一个 `.py` 文件里，没有类层次抽象、没有共享的算法基类。官方明确用"可复现的代码重复"（reproducible code duplication）换取**可读性**：你可以打开任何一个文件、从头读到尾，就看到该算法的全部真相。代价是同一段逻辑在几十个文件里各自演化，因此配套了严格的 CI 冒烟测试矩阵（7 个并行 job × Python 3.8–3.10）防止重复代码引入回归。

除算法本身外，仓库还内置：seeding / TensorBoard / W&B 实验 tracking、benchmark 基准复现（7+ 算法 × 34+ 游戏）、HuggingFace 模型发布、以及 AWS Batch + Docker + Terraform 云端实验基建——形成"读懂一个文件 → 复现一篇论文 → 跑一批实验 → 发布一个模型"的完整研究工作流。

## ② 架构分层

知识图谱将仓库分为 7 层。依赖方向自下而上：算法脚本调用共享工具库；benchmark 脚本编排算法脚本；云端基建把整套东西打包上云。

| 层 | 职责 | 关键文件 |
|---|---|---|
| **核心算法脚本层** | 单文件自包含的深度 RL 实现：PPO/DQN/SAC/TD3/C51/DDPG/Rainbow/PQN/QDagger/RPO/PPG 等，覆盖 Atari、MuJoCo、Procgen、Pettingzoo 多智能体、IsaacGym、Transformer-XL 等环境变体 | `cleanrl/ppo.py`、`cleanrl/dqn_atari.py`、`cleanrl/sac_continuous_action.py`、`cleanrl/c51.py`、`cleanrl/rainbow_atari.py`、`cleanrl/ppo_atari_envpool_xla_jax_scan.py` |
| **共享工具库层** | 唯一允许跨脚本复用的组件：replay/rollout buffer、Atari 预处理 wrapper、评估回调、Optuna 调参、benchmark 启动器、断点恢复、HF 上传、回放演示 | `cleanrl_utils/buffers.py`、`cleanrl_utils/atari_wrappers.py`、`cleanrl_utils/tuner.py`、`cleanrl_utils/benchmark.py`、`cleanrl_utils/huggingface.py`、`cleanrl_utils/evals/ppo_eval.py` |
| **基准评测层** | 复现基准实验的 shell 脚本（每算法一个），多 SEED 重跑 + `*_plot.sh` 用 rliable 统计聚合出图；含 SLURM 集群单 GPU 作业模板 | `benchmark/ppo.sh`、`benchmark/ppo_plot.sh`、`benchmark/cleanrl_1gpu.slurm_template` |
| **云端与容器基础设施层** | Terraform 定义的 AWS Batch 基建（启动模板、队列、计算环境、实验提交/终止）；Docker 镜像与 entrypoint（Xvfb 后台渲染 Atari 录像） | `cloud/main.tf`、`cloud/modules/cleanrl/setups.tf`、`cloud/examples/submit_exp.sh`、`Dockerfile`、`entrypoint.sh` |
| **测试层** | pytest 冒烟测试：按环境族（classic-control/Atari/MuJoCo/Procgen/EnvPool/Pettingzoo/multigpu）对每个算法做短程训练验证；JAX GAE 数值正确性、工具函数与 enjoy 回放单测 | `tests/test_classic_control.py`、`tests/test_atari.py`、`tests/test_mujoco.py`、`tests/test_jax_compute_gae.py`、`tests/test_tuner.py` |
| **文档层** | MkDocs 文档站：各算法实现讲解（含公式推导与超参表）、基准结果页、上手指南、云端教程、博客 | `docs/rl-algorithms/overview.md`、`docs/rl-algorithms/ppo.md`、`README.md`、`CONTRIBUTING.md` |
| **项目配置与 CI 层** | GitHub Actions 工作流、按环境拆分的 12 份 requirements、`pyproject.toml`（uv 锁定）、pre-commit、mkdocs.yml | `pyproject.toml`、`.github/workflows/tests.yaml`、`requirements/requirements.txt` |

## ③ 核心概念

读懂任何一份算法脚本前，先掌握这套在所有文件中重复出现的"词汇表"：

1. **单文件实现（single-file implementation）**：一个算法变体 = 一个入口脚本。算法骨架（网络/损失/循环）永远留在单文件内不抽取；只有"与算法无关的基础设施"（buffer、预处理、调参、上传）才进 `cleanrl_utils/`。理解这条边界，就理解了整个仓库的组织逻辑。
2. **Args dataclass + tyro CLI**：每个脚本开头用 `@dataclass` 定义 `Args` 类，集中列出全部超参（学习率、buffer 大小、target 网络同步频率、探索退火区间、wandb/HF 追踪开关等，如 `dqn_atari.py` 的 22 个参数），命令行接口由 `tyro.cli(Args)` 自动生成——带帮助文档、类型检查，且超参数可被 tuner/benchmark 流水线程序化注入。
3. **make_env 环境包装**：脚本内定义 `make_env(env_id, seed, idx, capture_video)` 闭包，统一完成 `gym.make` → 设置 seed → 挂 `RecordEpisodeStatistics`（必要时 `RecordVideo`）→ Atari 场景再套 `AtariWrapper` 预处理栈。这是所有环境差异被"压平"为一行包装链的地方——算法骨架对环境无感知。
4. **Agent 网络定义**：每个脚本内联定义自己的网络（MLP / Nature CNN / ImpalaCNN / LSTM），无共享模型库。典型如 PPO 的 actor-critic 共享主干 + 正交初始化，DQN 的 `QNetwork` 输出逐动作 Q 值。on-policy 算法网络内含 `get_action_and_value` 方法直接服务采样与训练。
5. **训练循环范式**：所有脚本都是"rollout → update"两段式循环 + `track.writer`（TensorBoard/W&B 双写）记录 `charts/episodic_return` 等指标。on-policy 是"采集一批、学几轮、丢掉"；off-policy 是"每步采一点、从 replay buffer 均匀采样一小批、立刻更新"。
6. **on-policy vs off-policy**：全库最大的分野。PPO/PPG/PQN 用 `RolloutBuffer` + GAE 优势估计；DQN/C51/Rainbow/TD3/SAC/DDPG 用 `ReplayBuffer` + 目标网络（硬更新 vs 软更新 τ）+ ε-greedy/高斯噪声/温度熵探索。对照 `ppo.py` 与 `dqn.py` 即可看清两条范式的最小骨架。
7. **JAX 双栈**：同一算法有 PyTorch 与 JAX/Flax 两版（`*_jax.py`）。JAX 版的核心差异：损失经 `jax.value_and_grad` 求梯度、目标网络参数存进扩展的 `TrainState`（如 `dqn_jax.py`）、更新用 `optax.incremental_update` 软同步（如 `td3_continuous_action_jax.py` 的三目标网络）；巅峰形态是用 `jax.lax.scan` 把 rollout+GAE+更新整个编译进 XLA，消除 Python 调度开销。
8. **benchmark 复现链路**：`benchmark.py` 把实验命令模板在 env×seed 网格展开（本地 subprocess 并行或填充 SLURM 模板）；`benchmark/*.sh` 是各算法的总编排脚本；`*_plot.sh` 用 rliable（IQM、performance profile、bootstrap 置信区间）从 W&B 拉曲线出图。每个 benchmark 数字都可由 `reproduce.py` + `enjoy.py`（从 HF Hub 下载检查点复验）独立复核——这是"单文件可扩展到上千实验"承诺的工程兑现。

## ④ 引导式学习路线（11 步，来自知识图谱 tour）

| 步 | 主题 | 说明与涉及文件 |
|---|---|---|
| 1 | 项目概览与单文件哲学 | 从 `README.md` 理解定位：单文件 + 可复现代码重复换可读性；浏览 `docs/rl-algorithms/overview.md` 算法总表——全部变体及对应脚本的地图 |
| 2 | 最简 PPO 精读 | **全库第一精读文件** `cleanrl/ppo.py`（被引用最多）：约三百行呈现 on-policy 闭环——SyncVectorEnv 向量化采样、GAE、minibatch 裁剪更新、正交初始化；对照 `docs/rl-algorithms/ppo.md` 的推导与超参细节 |
| 3 | DQN 对照：off-policy 三要素 | `cleanrl/dqn.py` 对比出三大件：replay buffer、目标网络硬更新、ε-greedy 线性衰减；`cleanrl/dqn_atari.py` 展示换环境后的两处改造——Nature CNN + DeepMind 预处理 wrapper 栈，体会"骨架不变、环境适配分层" |
| 4 | 连续控制三部曲 DDPG→TD3→SAC | `cleanrl/ddpg_continuous_action.py`（tanh Actor + 单 Q 软更新 + 高斯噪声）→ `cleanrl/td3_continuous_action.py`（双 Q 取 min、目标裁剪噪声、延迟更新三刀）→ `cleanrl/sac_continuous_action.py`（tanh 高斯随机策略 + α 自动调节）。三文件几乎同构，逐行 diff 看清进化脉络 |
| 5 | 高级变体四重奏 | `cleanrl/ppo_atari_lstm.py`（部分可观测：隐藏态在 done 置零、按时间步重排序列）；`cleanrl/ppo_rnd_envpool.py`（RND 内在奖励解决稀疏探索，Montezuma 复仇）；`cleanrl/pqn.py`（DQN 改造成 PPO 式多 epoch minibatch 更新，新一代分布式 Q 学习）；`cleanrl/ppo_atari_multigpu.py`（torchrun + DDP 单文件分布式） |
| 6 | cleanrl_utils 共享工具层 | `cleanrl_utils/buffers.py`（SB3 风格双 buffer，被全部 DQN 系与连续控制复用，fan-in 最高）；`cleanrl_utils/atari_wrappers.py`（NoopReset/MaxAndSkip/EpisodicLife 等经典组件）；`cleanrl_utils/tuner.py`（Optuna 搜索：runpy 动态执行算法脚本、从 TensorBoard 日志提取回报打分）。看懂这层 = 理解"哪些允许共享、哪些必须留在单文件"的权衡边界 |
| 7 | 研究友好生态：评估与发布 | `cleanrl_utils/evals/ppo_eval.py`（检查点评估标准写法：重建 Agent、加载权重、统计回报）；`cleanrl_utils/huggingface.py`（push_to_hub 自动生成含指标与超参的 model card 批量上传）；`cleanrl_utils/enjoy.py`（按实验名取 (Model, make_env, evaluate) 三元组，从 HF Hub 下载检查点跑演示）。这条链路解释 benchmark 页每个数字如何被独立复验 |
| 8 | JAX 栈对照实现 | `cleanrl/dqn_jax.py`（最直观入门：value_and_grad + TrainState 扩展）；`cleanrl/td3_continuous_action_jax.py`（三个目标网络的纯函数式同步）；`cleanrl/ppo_atari_envpool_xla_jax.py` 与 `cleanrl/ppo_atari_envpool_xla_jax_scan.py`（性能巅峰：lax.scan 把 rollout、GAE 反传与更新全编译进 XLA，全库吞吐最高的实现之一） |
| 9 | benchmark 基准评测流水线 | `cleanrl_utils/benchmark.py`（fan-in 第二高，被 17 个文件引用）；`benchmark/ppo.sh`（PPO 全变体总编排：50 任务、57 Atari、procgen、多智能体等 13 段）；`benchmark/cleanrl_1gpu.slurm_template`（SLURM 集群模板）；`benchmark/ppo_plot.sh`（rliable 统计出图） |
| 10 | 云端与容器基建 | `cloud/main.tf`（Terraform 入口：50% spot 比例实例化 cleanrl 模块）；`cloud/modules/cleanrl/setups.tf`（VPC/IAM/Batch 计算环境与队列）；`cloud/examples/submit_exp.sh`（向 AWS Batch 提交实验）；`Dockerfile`（CUDA 运行时 + uv 锁定安装）；`entrypoint.sh`（后台 Xvfb 供 Atari 渲染录像） |
| 11 | CI 测试矩阵与贡献流程 | `.github/workflows/tests.yaml`（pull_request 触发 7 个并行 job，Python 3.8–3.10 矩阵冒烟测试——单文件哲学的质量保障）；`CONTRIBUTING.md`（贡献流程指向官方文档站）。至此完成"读懂一份 ppo.py → 能提交一个新变体"的闭环 |

## ⑤ 文件地图（28 个最关键文件，按层组织）

### 核心算法脚本层 · on-policy 族（PPO 系 + PPG）

| 文件 | 一句话说明 |
|---|---|
| `cleanrl/ppo.py` | **全库参考模板**：CartPole 上的基准 PPO（SyncVectorEnv + GAE + minibatch 裁剪更新），约三百行读懂 on-policy 全闭环 |
| `cleanrl/ppo_atari.py` | PPO 的 Atari 参考版：共享 CNN 主干 actor-critic，入门 Atari 实现的第一站 |
| `cleanrl/ppo_continuous_action.py` | MuJoCo 连续动作 PPO：Normal 策略（可学习 logstd）+ 观测/奖励归一化包装链 |
| `cleanrl/ppo_atari_lstm.py` | LSTM 记忆变体：CNN 后接 LSTM，get_states 按时间步重排序列并在 done 处置零隐藏态 |
| `cleanrl/ppo_rnd_envpool.py` | RND 探索变体：预测器/目标双网络生成内在奖励，RewardForwardFilter 折扣滤波，内外双价值头 |
| `cleanrl/ppo_atari_multigpu.py` | 多 GPU 分布式：torchrun + DDP，各 rank 独立环境子集、梯度同步等效大 batch |
| `cleanrl/ppg_procgen.py` | Phasic Policy Gradient：Impala 残差骨干 + 三头网络 + 策略/辅助阶段交替的双相训练 |

### 核心算法脚本层 · off-policy 族（DQN 系）

| 文件 | 一句话说明 |
|---|---|
| `cleanrl/dqn.py` | off-policy 最小骨架：MLP Q 网络 + 目标网络硬更新 + ε-greedy 线性衰减 |
| `cleanrl/dqn_atari.py` | DQN×Atari：Nature 风格 CNN + 经典预处理 wrapper 栈；其 QNetwork 被 qdagger 教师蒸馏复用 |
| `cleanrl/c51.py` | 分布式 RL 入门：Q 网络输出 n_atoms 支持点上的分布，目标分布投影 + 交叉熵损失 |
| `cleanrl/rainbow_atari.py` | 组件集成之王：NoisyNet + Dueling 分布式网络 + n-step 回报 + 线段树优先经验回放（PER） |
| `cleanrl/pqn.py` | Phasic Q-Network：DQN 改造成 PPO 式 minibatch 多 epoch 更新，Q(λ) 目标 + LayerNorm MLP |
| `cleanrl/qdagger_dqn_atari_impalacnn.py` | 教师蒸馏（DQfD 式）：从 HF 下载 DQN 教师在线收集转换，学生 ImpalaCNN 以 KL 蒸馏 + TD 损失联合训练 |

### 核心算法脚本层 · 连续控制族

| 文件 | 一句话说明 |
|---|---|
| `cleanrl/ddpg_continuous_action.py` | 最朴素的确定性策略梯度：tanh Actor 缩放动作区间、单 Q 软更新、高斯噪声探索 |
| `cleanrl/td3_continuous_action.py` | DDPG 修三刀：双 Q 取 min 抑制过估计、目标动作裁剪噪声（目标策略平滑）、策略延迟更新 |
| `cleanrl/sac_continuous_action.py` | 最大熵 RL：双 Q 取 min、tanh 高斯随机策略带 log-prob 修正、温度系数 α 自动调节 |
| `cleanrl/rpo_continuous_action.py` | Robust PO（AAAI 2023）：Normal 均值上叠加 ±rpo_alpha 均匀扰动再重采样，得鲁棒策略梯度 |

### 核心算法脚本层 · JAX 双栈

| 文件 | 一句话说明 |
|---|---|
| `cleanrl/dqn_jax.py` | JAX 入门对照：MSE TD 损失经 jax.value_and_grad，目标网络参数存进扩展 TrainState |
| `cleanrl/td3_continuous_action_jax.py` | 函数式 TD3：目标动作裁剪噪声 + 双 Q 取 min + optax.incremental_update 同步三目标网络 |
| `cleanrl/ppo_atari_envpool_xla_jax_scan.py` | 全库性能巅峰：lax.scan 把 rollout、GAE 反传、epoch/minibatch 更新全部编译进 XLA |

### 共享工具库层

| 文件 | 一句话说明 |
|---|---|
| `cleanrl_utils/buffers.py` | fan-in 最高的共享模块：SB3 风格 ReplayBuffer（多环境 + timeout 截断区分）与 RolloutBuffer（含 GAE） |
| `cleanrl_utils/atari_wrappers.py` | DeepMind 预处理组件库：NoopReset/MaxAndSkip/EpisodicLife/FireReset/ClipReward/WarpFrame + 一键 AtariWrapper |
| `cleanrl_utils/tuner.py` | Optuna 超参搜索：runpy 动态执行算法脚本、从 TensorBoard 提取 episodic return 打分、支持剪枝与 W&B |
| `cleanrl_utils/benchmark.py` | 基准启动器：实验命令模板在 env×seed 网格展开，本地 subprocess 并行或填充 SLURM 模板批量提交 |
| `cleanrl_utils/evals/ppo_eval.py` | 检查点评估标准写法：重建 Agent → 加载权重 → 采样统计评估回合回报 |
| `cleanrl_utils/huggingface.py` | HF Hub 发布：push_to_hub 生成含指标与完整超参的 model card，批量 CommitOperation 上传 |
| `cleanrl_utils/enjoy.py` | 模型演示入口：按实验名从注册表取 (Model, make_env, evaluate) 三元组，从 HF Hub 下载检查点跑评估 |

### 云端与容器基础设施层

| 文件 | 一句话说明 |
|---|---|
| `cloud/main.tf` | Terraform 入口：声明 AWS provider，以 50% spot 比例实例化 cleanrl 模块（GPU/CPU/ARM 多机型池） |

## ⑥ 复杂度热点（top 8：为什么难、如何接近）

> 说明：图谱的 complexity 为三档（simple/moderate/complex），41 个算法/工具文件被评为 complex。以下 8 个是其中**集成广度与范式跨度最大**者，按"难度来源"分组排列。

| # | 文件 | 为什么难 | 如何接近 |
|---|---|---|---|
| 1 | `cleanrl/ppo_atari_envpool_xla_jax_scan.py` | 范式跨度最大：rollout、GAE 反传、epoch/minibatch 更新全部塞进 `jax.lax.scan`，Python 循环消失、形状推理与 jit 心智模型完全不同于 PyTorch | 先读 `cleanrl/ppo_atari_envpool.py`（envpool 版）→ `cleanrl/ppo_atari_envpool_xla_jax.py`（非 scan 版）→ 最后 diff 出 scan 化改动 |
| 2 | `cleanrl/rainbow_atari.py` | 组件集成之王：NoisyNet 探索 + Dueling 分布式网络 + n-step 回报 + Sum/Min 线段树 PER，任一组件理解不透都会卡在损失计算 | 拆解法：先 `c51.py`（分布式投影）→ `dqn_atari.py`（Atari 骨架）→ 最后只关注 Rainbow 的增量（线段树采样权重与 NoisyNet 前向） |
| 3 | `cleanrl/qdagger_dqn_atari_impalacnn.py` | 双损失（offline KL 蒸馏 + online TD）交织、教师在线收集与学生训练共用循环、教师/学生两套 buffer 与网络 | 先理解 `dqn_atari.py`（其 QNetwork 即教师模型），把文件切成"教师收集"与"学生更新"两段分别读 |
| 4 | `cleanrl/ppo_atari_lstm.py` | 部分可观测的序列处理：done 处隐藏态置零、按时间步重排（reshape）序列以适配 LSTM 输入，张量形状极易绕晕 | 手算一遍 `(n_steps, n_envs)` ↔ `(n_envs, n_steps)` 的重排，对照 `ppo_atari.py` 看新增的 get_states 逻辑 |
| 5 | `cleanrl/ppo_rnd_envpool.py` | 内外双价值头分别拟合外部/内部回报、RewardForwardFilter 折扣滤波、RND 预测器/目标双网络，且价值头**不能**用正交初始化（官方实现细节） | 以 `ppo_atari_envpool.py` 为底座，只追"内在奖励如何产生、如何进 GAE、如何进价值头"一条数据流 |
| 6 | `cleanrl/ppo_atari_multigpu.py` | 分布式心智模型：torchrun 启动、DDP 梯度同步、各 rank 持有独立环境子集、日志与指标只由 rank 0 记录 | 先跑通单 GPU `ppo_atari.py`，再对照本文件看 device 与 process group 相关的增量行 |
| 7 | `cleanrl/c51.py` | 分布投影是不可导操作：目标分布投影到固定原子集需相邻原子线性插值（依赖 `(δ < 0) * (δ²)` 这类技巧分配权重），与普通 MSE 回归思路完全不同 | 手推一遍 2 原子示例的投影权重分配，再读代码里的向量化实现；这是读懂 Rainbow 的前置 |
| 8 | `cleanrl/ppg_procgen.py` | 双相训练循环：策略阶段与辅助阶段交替，策略/价值/辅助价值三头网络，辅助阶段的 KL 锁定项容易与 PPO 主损失混淆 | 先熟悉 `ppo_procgen.py`（若跳过可直接对照 `ppo_atari.py`），把文件按"两个 phase"物理切块阅读 |

**新人建议**：无论从哪个热点入手，路线永远是——先读对应的 `ppo.py`/`dqn.py`/`dqn_atari.py` 最小骨架，再 diff 出变体的增量。这正是单文件哲学赠予读者的礼物：任何复杂度都被隔离在一个文件内，读懂一个文件就真正读懂一个算法。
