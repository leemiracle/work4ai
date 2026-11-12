# hyperparams/*.yml——13 算法调参矩阵体系

## ① 角色定位

`hyperparams/` 是 zoo 的**调参知识库**：13 个 YAML 文件（a2c/ars/crossq/ddpg/dqn/her/ppo/ppo_lstm/qrdqn/sac/td3/tqc/trpo），一算法一文件，文件内按**环境 ID 分段**存 tuned 超参。训练入口不接收超参命令行参数，全部从这份矩阵读取（默认路径拼接在 `rl_zoo3/exp_manager.py:127`：`f"hyperparams/{self.algo}.yml"`）。矩阵规模差异极大：ppo.yml 44 个顶层段、587 行，覆盖面之王；dqn.yml/qrdqn.yml 仅 6 段。除 her.yml 外**12/13 个文件都有 `default` 兜底段**——未调参环境也能用 SB3 默认值跑通。

## ② 内部结构

**三级查找**。消费逻辑在 `ExperimentManager.read_hyperparameters`（`rl_zoo3/exp_manager.py:332-382`）：①精确匹配环境 ID（:349-350）；②Atari 特判取 `atari` 段（:351-352，判定依据是 entry_point 含 "AtariEnv"，:609-611）；③回退 `default` 段（:353-355）；④都没有则 ValueError（:357）。之后两轮覆盖：Optuna study 参数（:359-362）与 CLI 自定义键值（:364-366）。

**default 段**极简（ppo.yml:2-4 与 dqn.yml:2-4 相同）：`n_timesteps: !!float 1e6` + `policy: 'MlpPolicy'`——未调参环境交给 SB3 类默认值。`!!float` 是显式类型标签：不带标签的 `1e6` 会被解析成字符串。

**atari 段**是图像输入配方。dqn.yml:6-23：AtariWrapper + `frame_stack: 4` + CnnPolicy + `buffer_size: 100000` + `learning_starts: 100000`；:21-23 注释标出 `optimize_memory_usage` 与 `handle_timeout_termination` 互斥。ppo.yml:6-19 同结构但换 on-policy 键集。

**键词汇表**。zoo 私有键在 `_preprocess_hyperparams`（`rl_zoo3/exp_manager.py:443-525`）被拦截消费、**从模型构造 dict 删除**：`n_envs`（:446,:497-498）、`n_timesteps`（:458-463,:499）、`frame_stack`（:501-503）、`normalize`（:419-441）、`env_wrapper`/`vec_env_wrapper`（:511-518）、`callback`（:520-523）、`env_kwargs`/`monitor_kwargs`（:483-494）；其余键透传给 `ALGOS[self.algo](...)`（:237）。

四个高语法键：

- **`policy_kwargs`**：YAML 表达不了 Python 对象，写成**字符串**加载时 eval（:478-480，与 `replay_buffer_class`/`replay_buffer_kwargs` 共用循环）。ppo.yml:159-163 多行写法 `dict(..., net_arch=dict(pi=[256,256], vf=[256,256]))` 是 on-policy 分离双头；dqn.yml:39 `dict(net_arch=[256, 256])` 是 off-policy 共享主干列表。
- **`env_wrapper`**：单行类路径（ppo.yml:295 `minigrid.wrappers.FlatObsWrapper`）或带 kwargs 列表（ppo.yml:356-362，CarRacing-v3 叠 FrameSkip/ResizeObservation/GrayscaleObservation）。解析在 `rl_zoo3/utils.py:49-125` `get_wrapper_class`：importlib 动态导入（:104-106）、dict 拆 kwargs（:92-100）、闭包 wrap_env 依序包裹（:118-121）。
- **`normalize`**：`true` 全归一化；字符串形态 `"{'norm_obs': False, 'norm_reward': True}"`（ppo.yml:364）只归一化奖励——eval 后拆 kwargs（:428-430），且算法 gamma 传播进 VecNormalize（:437-438）。
- **调度值 DSL**：`lin_` 前缀（ppo.yml:16 `learning_rate: lin_2.5e-4`）。`_preprocess_schedules`（:401-417）对 `learning_rate/clip_range/clip_range_vf/delta_std` 四键：字符串切分转 `SimpleLinearSchedule`（:406-409，实现即 `progress_remaining * initial_value`，`rl_zoo3/utils.py:308-309`）；数值转 ConstantSchedule，负数跳过表示不调度（:410-414）。

**YAML 锚点复用**：ppo.yml 用 `&pybullet-defaults`（:142）、`&minigrid-defaults`（:294）、`&mujoco-defaults`（:393）三个锚点 + `<<:` 合并键（:167,:310,:410）把家族环境收敛到一处，子段只覆写差异——MiniGrid 12 任务用 14 行锚点定义铺满全家。

**ppo.yml vs dqn.yml 对比**（on-policy vs off-policy 键集活教材）：PPO 段围绕 rollout 组织——`n_steps`/`n_epochs`/`batch_size`/`gae_lambda`/`clip_range`/`vf_coef`，连续控制加 `use_sde`/`sde_sample_freq`（ppo.yml:33-34）；batch_size 必须整除 `n_steps*n_envs`（ppo.yml:300-301 注释，CartPole 段 32×8=256 恰好等于 batch_size）。DQN 段围绕 replay buffer 组织——`buffer_size`/`learning_starts`/`target_update_interval`/`train_freq`/`gradient_steps`/`exploration_fraction`（dqn.yml:26-39），CartPole 段 `train_freq: 256` 配 `gradient_steps: 128` 是"攒一批再狠学"的配比。sac.yml/td3.yml 另有 `noise_type`/`noise_std` 键，在 `_preprocess_action_noise`（:527-563）转 NormalActionNoise/OrnsteinUhlenbeckActionNoise 对象。

**her.yml 钉版：reference-only**。文件头注释（her.yml:1-5）明说"SB3 >= 1.1.0 起 HER 并入 HerReplayBuffer，此文件不再使用，仅作参考"。证据链：①`ALGOS` 字典（`rl_zoo3/utils.py:27-41`）无 her 键，`--algo her` 构造模型时 KeyError；②知识图谱里其余 12 个 yml 均有 `configures → exp_manager.py` 边，唯独 her.yml 没有，只有 `related → tqc.yml/sac.yml` 两条边；③其段内 `model_class: 'tqc'`（her.yml:10）、`n_sampled_goal`、`online_sampling: True`（her.yml:19）全是旧 HER 模型 API。现代等价写法在 tqc.yml:241-252 的 parking-v0：`replay_buffer_class: HerReplayBuffer` + `replay_buffer_kwargs: "dict(goal_selection_strategy='episode', n_sampled_goal=4)"`（sac.yml:232 同款）——HER 从"算法"降格为"replay buffer 插件"。

## ③ 外部连接

图谱实证的边：12 个 `config:hyperparams/<algo>.yml --configures--> file:rl_zoo3/exp_manager.py`（唯一消费者）；`dqn.yml/ppo.yml --configures--> utils.py`（`rl_zoo3/utils.py:289-292` 的 enjoy 路径消费 `frame_stack` 键）；`related` 边三组：dqn↔qrdqn、ppo↔ppo_lstm、her→{tqc,sac}（家族/继任关系）。上游调用者 train.py/enjoy.py/benchmark.py 都 import exp_manager。`env_wrapper` 键把矩阵连向外部世界：`rl_zoo3/wrappers.py`、AtariWrapper、minigrid wrappers、`gymnasium.wrappers.*`——全靠 get_wrapper_class 字符串动态导入。配置格式还支持 Python 文件/pymodule（read_hyperparameters :339-346 分支，样例 `hyperparams/python/ppo_config_example.py`），但矩阵主体仍是 yml。

## ④ 数据流

以 `train --algo ppo --env HalfCheetah-v4` 为例：CLI → `ExperimentManager.__init__` 定位 ppo.yml（:127）→ `setup_experiment`（:209）→ read_hyperparameters：yaml.safe_load（:337-338）→ 三级查找命中段（:349-350）→ `saved_hyperparams` 排序快照（:375-380）→ `_preprocess_hyperparams`：拆 n_envs=1（:446）、学习率 2.0633e-05 包成 ConstantSchedule（:414）、policy_kwargs eval 成真 dict（:480）、删净私有键（:497-503）→ 返回 `(模型kwargs, env_wrapper, callbacks, vec_env_wrapper)` → create_envs 建 VecEnv → `PPO(env=env, **kwargs)`（:237-244）→ `_save_config` dump 超参到日志目录 config.yml（:307-316）保证复现。enjoy.py 靠同一矩阵重建环境侧配置。

## ⑤ 设计决策

1. **YAML 而非 Python 常量**：可读/可 diff/可外部消费，代价是 eval 与字符串类路径两套动态机制——用受控 DSL（`lin_`、`!!float`）换表达力。
2. **三级回退**让矩阵永远可用：tuned > atari > default，新增环境零配置可跑基线。
3. **键删除式预处理**：zoo 键消费完即删（:496 注释），同一 dict 才能安全 `**` 展开——新增键必须同步 `_preprocess_hyperparams`，否则漏进构造器抛 TypeError。
4. **锚点家族化**控制矩阵膨胀（ppo.yml 587 行已近管理极限）。
5. **her.yml 保留不删**：历史 tuned 值的迁移参照（1:1 映射到 replay_buffer_kwargs）。

## ⑥ 新人提示

- **读码入口**：`rl_zoo3/exp_manager.py:332` read_hyperparameters → :443 `_preprocess_hyperparams`，对照 ppo.yml 的 atari/pybullet/minigrid 三锚点段读。
- **坑 1**：`1e7` 忘写 `!!float` → 解析成字符串 → ConstantSchedule 分支抛 ValueError。
- **坑 2**：环境 ID 必须精确匹配（含版本号）；gym 升级改版本号会让段失配静默落到 default。
- **坑 3**：policy_kwargs 里 `nn.ReLU` 能用是因为 eval 命名空间有 torch.nn（`rl_zoo3/utils.py:33`）；自定义激活函数需保证加载环境可见。
- **坑 4**：别往 her.yml 加新环境——死文件；HER 需求走 sac/tqc/ddpg 的 `replay_buffer_class` 键。
- **连锁反应**：改 `normalize`/`gamma` 同时影响训练与评估环境统计；改 `n_envs` 会改 save_freq/eval_freq 实际频率（`create_callbacks` :574/:587 都除以 n_envs）。

<!-- chars(no-space): 5564, anchors: 74（file:line 27 + 段内 :NNN 引用 47） -->
