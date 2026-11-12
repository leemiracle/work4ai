# OnPolicy 与 OffPolicy 双分支 — common/on_policy_algorithm.py + common/off_policy_algorithm.py

## 一、角色定位：把 RL 两大范式铸成两套代码骨架

`BaseAlgorithm` 只钉生命周期协议，但"策略梯度家族"（A2C/PPO）与"replay buffer 家族"（DQN/SAC/TD3）训练节拍根本不同——前者必须用**当前策略新鲜采样的轨迹**算 advantage，数据用完即弃；后者可**反复回放旧数据**，一步交互配多步梯度更新。SB3 将其落成两个中间基类：`OnPolicyAlgorithm`（on_policy_algorithm.py:L21）与 `OffPolicyAlgorithm`（off_policy_algorithm.py:L27），各自实现 `learn/collect_rollouts/_setup_model`，只把 `train()` 留空（on:L270、off:L372）——具体算法（A2C/PPO/SAC/TD3/DQN，各自模块同名文件，如 ppo/ppo.py:L18）只剩"算 loss"。

## 二、内部结构：解剖与对照

### OnPolicyAlgorithm（347 行）

`__init__`（L61-113）收策略梯度六超参，`support_multi_env=True` 硬编码传父类（L95）——天然多 env 并行采样。`_setup_model`（L115-140）：lr schedule + 种子（L116-117）→ 选 buffer 类（L119-123，Dict 观测给 Dict 版）→ 按 `n_steps × n_envs` 定长建 buffer（L125-134）→ 建 ActorCriticPolicy（L135-138）；末尾 `_maybe_recommend_cpu`（L142）警告 MlpPolicy 上 GPU 反而慢。

`collect_rollouts`（L162-268）是心脏：eval 模式（L184）→ gSDE 重采样（L189）→ 循环（L194）内 `th.no_grad()` 前向一次拿 (actions, values, log_probs)（L199-202）→ Box 空间按 squash_output 决定 unscale/clip（L208-216）→ `env.step`（L218）→ callback 中断检查（L224）→ TimeLimit 截断用 V(s_terminal) bootstrap 修正 reward（L236-245）→ `rollout_buffer.add` 存六元组（L247）→ 循环外补最后 obs 的 V 值（L258）并 `compute_returns_and_advantage`（L262，GAE 倒序一次算完）。

`learn`（L300-341）四拍循环（见数据流），`self.train()` **无参**（L337）——数据就在 rollout_buffer 里；存档覆写加 policy.optimizer（L343）。

### OffPolicyAlgorithm（621 行）

`__init__`（L84-151）超参庞大：buffer_size/learning_starts/batch_size/tau/train_freq/gradient_steps/action_noise（L89-96）与 n_steps（L100，>1 启用 n-step return）；L148-149 sde_support 时把 use_sde 塞进 policy_kwargs。`_setup_model`（L177-227）：n_steps>1 且传自定义 buffer 类警告忽略（L181-188）；buffer 三分支（L190-199）——Dict→DictReplayBuffer、n_steps>1→NStepReplayBuffer（L195）、否则 ReplayBuffer；HerReplayBuffer 特判把 `self.env` 塞进 buffer kwargs（L205，HER 采样要用环境重标记）；再建 buffer（L208）、建 policy（L218）、`_convert_train_freq` 归一 TrainFreq（L153）。

`collect_rollouts`（L526-620）循环条件 `should_collect_more_steps(train_freq, ...)`（L571，utils.py:L572——按步数或 episode 数判停；多 env 禁止 episodic L563）。每步 `_sample_action`（L379）：warmup 期（L401）纯随机采样，否则 `predict(deterministic=False)`（L410）；Box 空间 rescale 到 [-1,1] 叠 action_noise 后**存缩放版进 buffer**（L413-422），env 执行 unscale 回原域版本。`_store_transition`（L461，L595 调用）存未归一化 obs/reward（L485-490）并回填 terminal_observation（L496-510）。每步调 `_on_step`（L603；L453 空实现，DQN 覆写做 target 硬更新 dqn.py:L174）。episode 结束才 dump_logs（L616）。返回 `RolloutReturn`（type_aliases.py:L69）。

`learn`（L324-370）collect 一段后调 `train(batch_size, gradient_steps)`（**带参**，L360-366，与 on-policy 无参镜像对立）。buffer 另有独立存档 save_replay_buffer/load_replay_buffer（L229/L239）；`_setup_learn` 覆写（L271）：optimize_memory_usage 截断最后轨迹（L288，issue #46）、多 env 包 VectorizedActionNoise（L309）。

## 三、外部连接

两文件均以 `BaseAlgorithm` 为唯一父类（on L10、off L13）。on-policy 依赖 RolloutBuffer/DictRolloutBuffer（buffers.py:L343/L697）与 ActorCriticPolicy；off-policy 依赖 ReplayBuffer 系（buffers.py:L158/L525/L847）、`should_collect_more_steps`（utils.py:L572），并**跨包引用** her/her_replay_buffer.HerReplayBuffer（L22）——common 反向依赖算法子包。被调用方向：PPO/A2C 的 `train()` 消费 `rollout_buffer.get`（buffers.py:L481，顺序迭代）；SAC/TD3/DQN 消费 `replay_buffer.sample`（buffers.py:L285，随机抽样）。子类名单 grep 实证见角色定位节。

## 四、数据流：PPO 与 SAC 主循环对照

**PPO**：`learn(4096)` → 第一拍 `collect_rollouts`（on L324）：4 个 env 各走 128 步，buffer 追加 512 条六元组；循环末 `predict_values(new_obs)`，`compute_returns_and_advantage`（L262→buffers.py:L403）倒序递推 GAE。第二拍 `PPO.train()`（L337）用 `rollout_buffer.get(64)` 顺序吐 minibatch 算 clipped loss。下一轮 collect 前先 reset（L187）清空重采——**数据生命周期 = 一个 rollout**。

**SAC**：`learn(10000)` → 第一拍 `collect_rollouts`（off L347）：前 100 步随机探索，之后策略采样，每步往 1e6 环形 buffer 写一条。第二拍越过 learning_starts 后 `train(batch_size=256, gradient_steps=1)`（L360、L366）：`replay_buffer.sample(256)` 随机抽样算三路 loss，软更新 target。然后回第一拍再采 1 步——**采样:训练 = 1:1 交替**，PPO 则是 512:1 批次。

## 五、设计决策：批判性权衡

**权衡一：train() 两种签名暴露范式本质。** on-policy `train(self)`（L270）无参——数据就是 buffer 里那一整段；off-policy `train(self, gradient_steps, batch_size)`（L372）带参——"抽多少批、每批多大"须由 learn 循环按 train_freq 节拍动态决定——强求统一签名必有一方受损。

**权衡二：动作缩放策略分道扬镳。** on-policy 存 buffer 与执行同一动作（L208-216）；off-policy 执行原域动作、入库 [-1,1] 缩放动作（L413-422 双轨）——replay buffer 要长期复用、跨环境迁移（HER 重标记），归一化表示更稳。代价是 `_sample_action`/`_store_transition` 双双复杂化，自定义 buffer 时极易搞混两个动作域。

**权衡三：`_on_step` 挂钩 vs train 内更新。** DQN 的 target 硬更新走 `_on_step`（L453，每 env 步查 target_update_interval），SAC/TD3 的软更新在 train() 里（L601 注释点明缘由）。空方法覆写比 if-else 干净，但"在哪更新 target"散落两处。

## 六、新人提示：上手坑与勘误

1. **`log_interval` 单位不同**：on-policy 按 iteration（on L304，默认 1），off-policy 按 episode（off L328 默认 4，判处在 L616），照抄参数日志密度完全不同。
2. **PPO 的 `total_timesteps` 是下界**；off-policy 要 `num_timesteps > learning_starts` 才开始训练（L360），前 100 步只采样无梯度。
3. **buffer 默认不随 `save()` 存档**，off-policy 断点续训必须显式 `save_replay_buffer` + `load_replay_buffer`，否则 SAC/DQN 续训表现跳水。
4. **HER 必须构造时传 `replay_buffer_class=HerReplayBuffer`**（`_setup_model` L205 注入 env，事后手工替换会绕过初始化）；且传自定义 buffer 类后 `n_steps` 被静默忽略（L181-188）。
5. **勘误**：①on-policy 的 `num_timesteps += env.num_envs`（L220）在 `callback.on_step()`（L224）之前，callback locals 里看到的已是含当前步的值；②两个 `dump_logs` 签名不同——前者收 `iteration`（on L277），后者无参（off L429），别统一调用。

---

元数据：不计空格字符数 4781；行号锚 99 处；六节结构完整（角色定位/内部结构/外部连接/数据流/设计决策/新人提示）。
