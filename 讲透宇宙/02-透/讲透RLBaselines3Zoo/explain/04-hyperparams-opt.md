# rl_zoo3/hyperparams_opt.py——Optuna 超参自动优化

## ① 角色定位

`hyperparams_opt.py` 是 zoo 调参体系的**自动化层**：静态矩阵 `hyperparams/*.yml` 给人肉 tuned 值，本模块定义"机器怎么搜索参数空间"。两个职责：①每算法一个 `sample_*_params(trial, ...)` 用 Optuna `suggest_*` 声明搜索空间；②`convert_*_params` 把采样空间参数转成 SB3 构造器 kwargs。两套字典 `HYPERPARAMS_SAMPLER`（`rl_zoo3/hyperparams_opt.py:492-504`，11 键）与 `HYPERPARAMS_CONVERTER`（:507-519）登记给 ExperimentManager 分发。优化主循环在 `exp_manager.py` 的 `objective`/`hyperparameters_optimization`，由 `train.py --optimize` 触发（train.py:80）。

## ② 内部结构

**两个转换器**。`convert_onpolicy_params`（:9-52）：`gamma = 1 - one_minus_gamma`（:16-17）、gae_lambda 同式（:19-20）；`batch_size`/`n_steps` 存指数 `_pow`，转换时 `2 ** pow`（:25-28）；net_arch 类别映射双头 dict——tiny/small `[64,64]`/medium `[256,256]`（:30-34）；activation_fn 字符串映射 torch 类（:39-44）；打包成 policy_kwargs 返回（:46-52）。`convert_offpolicy_params`（:55-105）：net_arch 是**共享主干列表** small…verybig（:69-75）；train_freq 直接转写 gradient_steps 实现 1:1 update-to-data 比，有 subsample_steps 时改为 `train_freq // subsample_steps`（≥1，:77-83）；n_quantiles 挪进 policy_kwargs 供 TQC/QRDQN（:101-103）。

**sampler 函数**。旗舰 `sample_ppo_params`（:108-154）：`batch_size_pow = suggest_int(2, 10)`、`n_steps_pow = suggest_int(5, 12)`（:116-118）；`one_minus_gamma = suggest_float(1e-4, 0.03, log=True)`（:119）——对折扣率重参数化，在"接近 1"的区间对数均匀；learning_rate/ent_coef 同为 log 轴（:122-123）；clip_range/n_epochs/net_arch/activation_fn 用 categorical（:124-129）；末尾 `trial.set_user_attr` 写回真实 gamma/n_steps/batch_size（:137-139）——params 存 pow/补数形态，靠 user_attr 才可读。a2c（:222-254）仅 n_steps 改 categorical 列表（:229）；trpo（:178-219）加 n_critic_updates/cg_max_steps/target_kl（:194-197）；sac（:257-302）有 Polyak tau 0.001~0.08 log（:271）、HER 分支（:289-290）与 sample_tqc 标志下的 n_quantiles 5~50（:292-300）；td3（:305-349）独有 noise_type categorical 含 None（:321），按类型现场构造 NormalActionNoise/OrnsteinUhlenbeckActionNoise（:339-344，用 n_actions 定维）；dqn（:352-395）的 `subsample_steps = suggest_int(1, min(train_freq, 8))` 上界依赖已采样的 train_freq（:365），另采 exploration_fraction/final_eps 与 target_update_interval log 1~20000（:367-369）。`sample_her_params`（:398-412）采 n_sampled_goal 1~5 与 goal_selection_strategy 三选一（:407-410），写进 replay_buffer_kwargs（:411）。

**委托复用**：`sample_tqc_params` 置 `additional_args["sample_tqc"]=True` 后调 sac（:415-424）；`sample_qrdqn_params` 同法调 dqn（:427-436）；`sample_ppo_lstm_params` 原样转发 ppo、LSTM 键全注释保留（:157-176）。ARS 独立：`convert_ars_params` 折算 `n_top = int(top_frac_size * n_delta)`（:455-457），`sample_ars_params` 采 n_delta_pow/delta_std/top_frac_size（:470-474）。**crossq 不在两个字典里**——`rl_zoo3/exp_manager.py:814` 的 `HYPERPARAMS_SAMPLER[self.algo]` 直接 KeyError。

**objective（exp_manager.py:803-890）**。`kwargs = self._hyperparams.copy()`（:804，基底是 yml 解析产物）；additional_args 探测 HER（:808-811）；分发采样并 update（:814-815）；`create_envs(no_log=True)`（:817，防多 trial 写爆同一 Monitor 文件）；构造模型 `seed=None, tensorboard_log=None`（:827-835）——不固定种子免得 TPE 被同一随机性骗；评估频率 `optuna_eval_freq = n_timesteps / n_evaluations // n_envs`（:839-841），n_evaluations 由 n_timesteps 推导（每 100k 步一次，:466-467）；挂 TrialEvalCallback（:847-855）；model.learn 包 try，AssertionError/ValueError（典型 NaN）转 `optuna.exceptions.TrialPruned`（:865-874）；finally 关闭 env 防 SubprocVecEnv 管道泄漏（:875-880）；被剪枝再抛 TrialPruned，否则返回 `eval_callback.last_mean_reward`（:887-890）。

**TrialEvalCallback（rl_zoo3/callbacks.py:16-56）**。继承 SB3 EvalCallback，多存 trial 与 eval_idx 计数（:41-42）；`_on_step` 每 eval_freq 步先跑父类评估（:46-48），再 `trial.report(self.last_mean_reward, self.eval_idx)`（:51）——上报**历史最优** mean reward、step 轴是第几次评估而非时间步；`trial.should_prune()` 为真则置 is_pruned 并返回 False 终止训练（:53-55）。

**sampler/pruner 工厂（exp_manager.py:777-801）**。`_create_sampler`：random / tpe（`TPESampler(n_startup_trials, seed, multivariate=True)`，:782）/ auto（optunahub AutoSampler，:784-786）。`_create_pruner`：halving（`SuccessiveHalvingPruner(min_resource=1, reduction_factor=4)`，:793）/ median（`MedianPruner(n_startup_trials, n_warmup_steps=n_evaluations//3)`，:795——前 10 trial 不剪、每 trial 前 1/3 评估不剪）/ none。CLI 默认 `--sampler tpe --pruner median --n-startup-trials 10`（train.py:85-100）。

**hyperparameters_optimization（exp_manager.py:892-1011）**。storage 以 `.log` 结尾转 JournalStorage（:912-917）；`optuna.create_study(..., load_if_exists=True, direction="maximize")`（:922-929，load_if_exists 支持多 worker 续跑同一 study）；study 级 set_user_attr 存 command 与全部基底超参（:931-935）；max_total_trials 路径用 MaxTrialsCallback 且计数状态含 COMPLETE/RUNNING/PRUNED 防多 worker 超发（:941-961）；两路径都开 `gc_after_trial=True`（:960-963，对应 commit 630883a 修 "too many open files"）；收尾 dump trials_dataframe().to_csv + pickle 整个 study（:993-997），画优化历史/参数重要性图（:1004-1009）。

## ③ 外部连接

图谱边实证：`exp_manager.py --imports--> hyperparams_opt.py`（import 行 exp_manager.py:53）、`exp_manager.py --imports--> callbacks.py`（TrialEvalCallback 用在 :847）。**闭环边**：`load_trial`（exp_manager.py:384-398）从 storage 取 best_trial.params 后用 `HYPERPARAMS_CONVERTER[self.algo]`（:397）把 pow/补数形态转回真实值，供 `--study-name + --trial-id` 训练时覆盖 yml（:359-362）——converter 同时服务"进去"（采样后）与"回来"（study 载入）。测试边：`hyperparams_opt.py --tested_by--> tests/test_hyperparams_opt.py`（subprocess 跑 -optimize，2 sampler × 3 pruner × 7 实验含 HER/ppo_lstm）。外部依赖：optuna、torch.nn、`stable_baselines3.common.noise` 两噪声类。

## ④ 数据流

`train --algo ppo --env CartPole-v1 -optimize` → setup_experiment 在 :232-234 分支提前返回（只借道完成 yml 解析与环境探测）→ hyperparameters_optimization → create_study → `study.optimize(self.objective)` 循环：每 trial 采样（one_minus_gamma=0.008 → gamma=0.992、batch_size_pow=8 → 256）→ 建模型 → 边训边按 optuna_eval_freq 评估上报 → MedianPruner 与历史 trial 同评估点中位数比较、差则中途砍掉 → 完整跑完的返回 last_mean_reward → 打印 best trial 的 value/params/user_attrs，落盘 csv+pkl。选定后 `--study-name xxx --trial-id N` 重训，load_trial 把最优参数注回训练管线。

## ⑤ 设计决策

1. **重参数化采样**：one_minus_gamma 与 `_pow` 编码把"人类关心的量纲"（折扣率接近 1、2 的幂 batch）变成对数轴均匀可采的量，TPE 建模效率高；set_user_attr 弥补显示层。
2. **类别菜单而非连续宽度**：net_arch 只给 3~5 档 + converter 映射 torch 对象——Optuna params 需可序列化存库，torch 类进不了 params，转换推迟到最后一刻。
3. **报告最优而非当前值**（callbacks.py:49-50 源码留言 "report best or report current?"）：上报 EvalCallback 的 last_mean_reward，与"取 best model"语义一致，代价是中位数比较略乐观。
4. **NaN 即剪枝**：坏采样当作信息（PRUNED 状态）而非崩溃，study 不被发散配置拖死。
5. **委托而非复制**：tqc→sac、qrdqn→dqn、ddpg→td3（SAMPLER 字典 :495 直接绑 sample_td3_params）用 additional_args 标志扩展，11 个 sampler 零重复。
6. **多 worker 安全**：load_if_exists + MaxTrialsCallback 三态计数 + JournalStorage，一行命令水平扩展。

## ⑥ 新人提示

- **读码入口**：`sample_ppo_params`（hyperparams_opt.py:108）+ `objective`（exp_manager.py:803）+ `TrialEvalCallback._on_step`（callbacks.py:45）三点连起来即全流程。
- **坑 1**：新算法加调参支持必须**同时**登记两个字典，漏 SAMPLER 在 :814 KeyError，漏 CONVERTER 在 load_trial :397 KeyError。
- **坑 2**：`-n-jobs > 1` 或多机并行必须显式 `--storage` + `--study-name`；:896-901 的 warning 提示 storage 无 study_name 时 Optuna 自动起名、续跑会断。
- **坑 3**：调 HER 必须先在 yml 配 `replay_buffer_class: HerReplayBuffer`，探测（:809）以此为据。
- **坑 4**：n_evaluations 自动等于 n_timesteps/1e5——短预算只有 1 次评估，MedianPruner warmup（n_evaluations//3=0）形同虚设，剪枝基本不发生。
- **坑 5**：objective 里 ARS 强制 n_envs=1（:806）再走 AsyncEval，别照抄到别的算法。
- **连锁反应**：改搜索空间要顾及旧 study——params 键集合变化令 TPE 分布失效，惯例换 study_name 重开。

<!-- chars(no-space): 6438, anchors: 90（file:line 14 + 段内 :NNN 引用 76；篇幅超 4800 系任务指定覆盖 objective/callback/pruner/sampler 全链所致） -->
