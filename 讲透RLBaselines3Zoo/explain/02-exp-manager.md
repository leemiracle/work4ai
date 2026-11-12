# 02 · ExperimentManager：训练编排核心（rl_zoo3/exp_manager.py）

## ① 角色定位

`rl_zoo3/train.py::train()` 只负责收 CLI 参数；从「一份 yaml + 一个 Namespace」到「环境、模型、回调、训练循环、可复现落盘」的全部编排，都在 `ExperimentManager` 一个类里（`rl_zoo3/exp_manager.py:64`）。它是 zoo 的灵魂：1011 行文件里类占 948 行，SB3 本体（算法）与 zoo（调参基建）的边界就在这里——**zoo 不改算法，只做配置→对象→循环→落盘的翻译**。它同时兼任 Optuna 超参搜索的 orchestrator，一套类服务普通训练与 `-optimize` 两条路径。

## ② 内部结构

**`__init__`（75-200 行）纯赋值无副作用**：`rl_zoo3/exp_manager.py:117` 包 `EnvironmentName`；`rl_zoo3/exp_manager.py:120-127` 定位超参文件（pip 安装取包内 `hyperparams/`，源码取仓根，`-conf` 覆盖）；`rl_zoo3/exp_manager.py:137` 映射 `vec_env_class`（dummy/subproc），`rl_zoo3/exp_manager.py:73` 类属性 `default_vec_env_cls` 是 Brax/IsaacLab 等 VecEnv 的覆写钩子；`rl_zoo3/exp_manager.py:164` 一个表达式定续训模式（zip 存在即 continue_training）；`rl_zoo3/exp_manager.py:184` `deterministic_eval` 对 Atari/Minigrid 例外。**落盘布局在此定型**：`rl_zoo3/exp_manager.py:196-199` `save_path=logs/{algo}/{env}_{latest_run_id+1}{uuid}`，`rl_zoo3/exp_manager.py:200` `params_path=save_path/{env}` 子目录。

**`setup_experiment()`（202-247 行）唯一总入口**，六步：`read_hyperparameters`（209）→ `_preprocess_hyperparams`（210）→ `create_log_folder`+`create_callbacks`（221-222）→ `create_envs`（226；ARS 与优化模式强制 n_envs=1，225）→ `_preprocess_action_noise`（228，需真实 action_space）→ 三分支：续训走 `_load_pretrained_agent`（230-231）、优化模式关 env 返回 None（232-234）、否则 `ALGOS[self.algo](env=..., **self._hyperparams)` 从零建模型（237-244）；收尾 `_save_config`（246）。

**预处理群（332-563 行）——字符串翻译成对象**：`read_hyperparameters`（332-382）支持 yaml / python exec / 包 import 三源（335-346），选节优先级 env 精确 > atari > default > 报错（349-357，对应 `hyperparams/ppo.yml:2` 的 `default:` 与 `hyperparams/ppo.yml:6` 的 `atari:`），可选从 Optuna 回灌 trial（359-362），CLI `-params`/`--env-kwargs` 最后覆盖（364-373）。`_preprocess_hyperparams`（443-525）是大杂烩：`-n` 覆盖 n_timesteps（459-463）、优化模式推导 n_evaluations=n_timesteps//1e5（466-471）、`policy_kwargs` 等字符串键直接 `eval`（478-480）、`frame_stack` 摘出存实例（501-503）、`policy` 带点号则动态 import（506-507）、wrapper/callback 键转对象并删除（511-523）——**删完剩下的键才允许进模型构造器**。三个小方法同一哲学：`_preprocess_schedules`（400-417）把 `lin_2.5e-4` 拆成 `SimpleLinearSchedule`（407-409）、数值包 `ConstantSchedule`（414）；`_preprocess_normalization`（419-441）解析 normalize 三形态、gamma 透传给 VecNormalize（437-438）；`_preprocess_action_noise`（527-563）先取 n_actions（531-532），把 `noise_type`+`noise_std` 合成噪声对象（546-554）。

**环境与回调装配**：`create_callbacks`（568-603）——可选进度条（569-570）；`save_freq>0` 挂 `CheckpointCallback` 前缀 `rl_model`（572-582）；`eval_freq>0` 且非优化模式挂 `EvalCallback`，`rl_zoo3/exp_manager.py:592` 的 `SaveVecNormalizeCallback` 挂在 `callback_on_new_best`，产出 `best_model.zip`+`evaluations.npz`（593-601）；两个频率都先除以 n_envs（574、587）。环境探测五件套（605-629）全靠 registry entry_point 字符串 sniff（605-611）。`create_envs`（668-745）——eval 模式不写 monitor（679），`make_env` 闭包捕获 spec 保证子进程可用（687-693），装配序 `make_vec_env`→vec_env_wrapper→`_maybe_normalize`→`VecFrameStack`→自动 `VecTransposeImage`（699-743）。`_maybe_normalize`（631-666）续训时 load 旧 `vecnormalize.pkl`（644-650），eval env 强制 `norm_reward=False/training=False`（648-658）。

**训练与落盘**：`learn`（249-285）把 log_interval 三态翻译（-1 默认/<-1 关自动日志，254-260），ARS 多环境搭 `AsyncEval`（266-269），`model.learn` 包在 `except KeyboardInterrupt` 里——Ctrl-C 也保存（271-275）。`save_trained_model`（287-305）存 `{env}.zip`、可选 replay buffer（297-299）、`vecnormalize.pkl`（301-305，**评测侧没它分数就废**）。`_save_config`（307-328）写三件套：`config.yml` 未处理超参（315）、`args.yml` 排序后命令行参数（319-321）、`command.txt` 原始命令（324-328）——可复现性全部依据。

**续训**：`_load_pretrained_agent`（747-775）删 `policy`/`policy_kwargs`（751-754，策略结构不许换）→ `ALGOS[algo].load`（756-764）→ 旁有 `replay_buffer.pkl` 则连缓冲恢复（766-774）。

**Optuna 三方法**：`_create_sampler`/`_create_pruner`（777-801，tpe 多变量、median warmup=n_evaluations//3）；`objective`（803-890）每 trial 采样超参（814 `HYPERPARAMS_SAMPLER`）、建模型 **seed=None**（827-835）、挂 `TrialEvalCallback`（847-855；类在 `rl_zoo3/callbacks.py:16`，周期 `trial.report`+`should_prune`）、NaN/断言错误转 `TrialPruned`（867-874）、finally 关 env 防泄漏（875-880）；`hyperparameters_optimization`（892-1011）关 tensorboard（903-905）、`.log` 转 `JournalStorage` 支持分布式（912-917）、`create_study(load_if_exists=True)`（922-929）、`MaxTrialsCallback` 计数含 RUNNING（938-961）、`gc_after_trial=True` 修 fd 泄漏（960）、收尾出 csv+pkl 报告（993-997）。

## ③ 外部连接

**imports 进来**：SB3 侧 `make_vec_env` 与 `VecNormalize`/`VecFrameStack`/`VecTransposeImage` 等（`rl_zoo3/exp_manager.py:32-45`）、`EvalCallback`/`CheckpointCallback`（31 行）、`sb3_contrib.AsyncEval`（26 行）；zoo 侧 `import_envs`（51 行）、两个自定义 callback（52 行）、`HYPERPARAMS_SAMPLER`（53 行）、utils 五件（54-61 行，`get_latest_run_id` 在 `rl_zoo3/utils.py:389-404`）。

**被谁调用**：`rl_zoo3/train.py:233` 构造，`rl_zoo3/train.py:274-288` 依次调 `setup_experiment`/`learn`/`save_trained_model`/`hyperparameters_optimization`；`rl_zoo3/enjoy.py:136-137` 复用静态方法 `is_atari`/`is_minigrid`。

**calls 出去**：`ALGOS[self.algo](...)` 构造与 `.load(...)`（237、756 行）；`optuna.create_study/study.optimize`（922、948 行）；文件名契约来自 huggingface_sb3 的 `EnvironmentName`/`ModelName`。

## ④ 数据流

**训练主链**（`python train.py --algo ppo --env CartPole-v1`）：`hyperparams/ppo.yml:37` 的 `CartPole-v1:` 节（n_envs:8、learning_rate:lin_0.001）→ schedule 实例化、摘除 n_envs/n_timesteps → `create_envs(8)` → `PPO(env=..., **hyperparams)` → `learn(1e5)` → 保存。产物：`logs/ppo/CartPole-v1_1/CartPole-v1.zip`（最终模型）+ 子目录 `CartPole-v1/`（config/args/command/vecnormalize）+ `best_model.zip`/`evaluations.npz` + `rl_model_*_steps.zip`。run 号自增：下次 `get_latest_run_id+1` 得 `CartPole-v1_2`（`rl_zoo3/exp_manager.py:197-199`）。

**续训链**（`-i .../CartPole-v1.zip`）：同一 setup 流程，230-231 行转 `_load_pretrained_agent`——load 权重+可选回放缓冲，`_maybe_normalize` 读旧统计继续更新。

**优化链**（`-optimize`）：`setup_experiment` 在 232-234 行返回 None → `rl_zoo3/train.py:288` 转 `hyperparameters_optimization` → 每 trial 进 `objective`：采样超参覆盖基线 → 短训练 → 周期 report → median pruner 中途砍 → 幸存 trial 的 mean reward 即目标值 → 报告落 `logs/{algo}/`。

## ⑤ 设计决策

- **与 SB3 本体分工**：SB3 给算法与通用组件，zoo 给 tuned 配置+编排；本文件全是字符串→对象翻译，没有一行梯度代码。schedule 用 zoo 自己的 `SimpleLinearSchedule`（`rl_zoo3/utils.py:296-312`）而非 SB3 闭包，为了能被 yaml 表达、被存档。
- **配置是数据、eval 是胶水**：`lin_0.001`、`"dict(net_arch=[400,300])"`、normalize 字符串全靠 `eval` 翻译（407-409、478-480、429 行）——换来 yaml 单一事实源，代价是零静态检查+任意代码执行面。
- **双目录落盘约定**：save_path 与 params_path 分离，`enjoy` 侧 `rl_zoo3/utils.py:407-446` 严格对称读取——改一边必须改两边。
- **频率除以 n_envs**（574、587 行）：CLI 语义是总步数，SB3 callback 按「每 env 步」计数，翻译在此完成。
- **优化模式信号设计**：不用额外 flag，让 `setup_experiment` 返回 None 表达「去跑优化」（232-234 行）；代价是返回类型 `tuple | None`。
- **分布式友好**：JournalStorage+`load_if_exists`+`MaxTrialsCallback` 计 RUNNING（912-917、938-961 行）让多 worker 安全共跑一个 study；`gc_after_trial=True`（960 行）是修 "too many open files" 的近期修复（commit 630883a）。

## ⑥ 新人提示

- **读码入口**：沿 `setup_experiment`（202 行）一条竖线读完全类；Optuna 三方法最后看。
- **加一个 yaml 超参键的连锁反应**：新键若不被 `_preprocess_hyperparams`（443-525 行）翻译或删除，会原样进 `ALGOS[algo](**hyperparams)` 报 TypeError。
- **改落盘命名的连锁反应**：save_path/params_path 格式（196-200 行）被 `rl_zoo3/utils.py:471-520` 的 `get_model_path`、benchmark、push_to_hub、plots 硬约定，动它等于动全仓。
- **坑一**：`eval_freq`/`save_freq` 输入是总步数、生效是每 env 步数（574、587 行），n_envs=8 时实际触发频率 ×8。
- **坑二**：优化模式 seed 故意 None（830 行），复现靠 `--trial-id` 回灌（359-362 行）。
- **坑三**：两个「最优」语义不同——`best_model.zip` 是 EvalCallback 历史最优（593-601 行），`CartPole-v1.zip` 是最终模型（295 行）；enjoy 默认载后者。
- **坑四**：`deterministic_eval`（184 行）对 Atari/Minigrid 自动关确定性，对比分数时别忽略。

<!-- chars(no-space): 6578, anchors: 86 (24 处 file:line + 62 处 exp_manager.py 上下文行锚) -->
