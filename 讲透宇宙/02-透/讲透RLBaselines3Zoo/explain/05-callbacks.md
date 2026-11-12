# 05 · rl_zoo3/callbacks.py——zoo 侧回调装配与并行训练实验

## ① 角色定位

`rl_zoo3/callbacks.py` 是 zoo 在 SB3 回调体系之上补的自定义回调库，237 行、4 个类：**TrialEvalCallback**（callbacks.py:16）把 SB3 `EvalCallback` 接到 optuna 供超参搜索剪枝；**SaveVecNormalizeCallback**（callbacks.py:59）在"新最优模型"诞生同刻保存 `VecNormalize` running average；**ParallelTrainCallback**（callbacks.py:96）是实验性双线程异步训练（一个线程采样、一个做梯度步）；**RawStatisticsCallback**（callbacks.py:206）绕过 logger 滑动平均直写原始 episode 统计。通用的 `CheckpointCallback/EvalCallback/ProgressBarCallback` 不重写，直接 import SB3（exp_manager.py:31）。装配有两条线：常规训练 `create_callbacks()`（exp_manager.py:568）与超参优化 `optimize_agent()`（exp_manager.py:846-856）。

## ② 内部结构

**TrialEvalCallback(EvalCallback)**（callbacks.py:16）：构造函数走 `super().__init__()` 后挂 `self.trial`、`eval_idx`、`is_pruned` 三个状态（callbacks.py:41-43）。覆写的 `_on_step()`（callbacks.py:45-56）每逢 `n_calls % eval_freq == 0` 先调父类评估（callbacks.py:47），再 `trial.report(self.last_mean_reward, self.eval_idx)` 上报**当前**平均回报（callbacks.py:51，注释里还留着作者的犹豫 "report best or report current?"）；若 `trial.should_prune()` 则置 `is_pruned=True` 并 `return False` 中断 `model.learn`（callbacks.py:53-55）。

**SaveVecNormalizeCallback(BaseCallback)**（callbacks.py:59）：`_init_callback()` 建目录（callbacks.py:75-78）；`_on_step()` 在 `n_calls % save_freq == 0` 时落盘——无 prefix 固定写 `vecnormalize.pkl`（callbacks.py:88），实际动作是 `self.model.get_vec_normalize_env().save(path)`（callbacks.py:89-90），即从当前模型反查归一化包装层再序列化。

**ParallelTrainCallback(BaseCallback)**（callbacks.py:96）：文档明说配 off-policy 算法与 `train_freq=(1, "episode")`（callbacks.py:100）。`_init_callback()`（callbacks.py:124-168）做三件非常规事：①主模型 save 到 tempfile 再 load 出影子 `self._model`（callbacks.py:135、144）——序列化克隆而非 deepcopy；②`isinstance` 探测 `model_class`，仅支持 SAC/TQC（callbacks.py:133、138-141）；③两处 monkey-patch——`patch_train` 把主模型 `train` 换成空函数（callbacks.py:158），`patch_save` 把主模型 `save` 转发给影子模型（callbacks.py:168），因为梯度更新后真正持有新参数的是影子侧。`train()` 每次起 daemon `Thread` 跑 `_train_thread`，完成后置 `_model_ready = True`（callbacks.py:170-178）。同步点在 `_on_rollout_end()`（callbacks.py:185-195）：`deepcopy` 回放池喂影子模型、`set_parameters(deepcopy(...))` 写回新策略、手工重接 `model.actor = model.policy.actor`（callbacks.py:190-192），且 `num_timesteps >= learning_starts` 才启动下轮（callbacks.py:193）。`_on_training_end()` 里 `process.join()` 等尾部线程（callbacks.py:198-203）。

**RawStatisticsCallback(BaseCallback)**（callbacks.py:206）：`_init_callback()` 从 `logger.output_formats` 里找 `TensorBoardOutputFormat`，找不到直接 assert（callbacks.py:218-224）——必须开 `--tensorboard-log`。`_on_step()` 扫 `self.locals["infos"]` 的 `episode` 键，把 `raw/rollouts/episodic_return/length` 直写 writer，自带计数器防同 step 重复上报（callbacks.py:226-235）。

## ③ 外部连接

- **imports 进来**：optuna（callbacks.py:8）、sb3_contrib TQC（callbacks.py:9）、SB3 的 SAC/EvalCallback/BaseCallback/TensorBoardOutputFormat（callbacks.py:10-13）。
- **被谁调用**：库内唯一 import 点是 exp_manager.py:52；`hyperparams/sac.yml:24-25` 以注释示范 yml 装配法 `callback: - rl_zoo3.callbacks.ParallelTrainCallback`（即它不在默认装配路径，需手动启用）；tests/test_callbacks.py:17 用 `-params callback:"'rl_zoo3.callbacks.RawStatisticsCallback'"` 验证该通道。
- **装配与出口**：`_preprocess_hyperparams()` 调 `get_callback_list`（exp_manager.py:520，函数在 utils.py:148）把 yml `callback:` 键实例化，原始字符串存 `self.specified_callbacks`（exp_manager.py:521-523）供调参线每 trial 重建（exp_manager.py:846）；`learn()` 时 `kwargs["callback"] = self.callbacks` 传给 `model.learn`（exp_manager.py:262-263），KeyboardInterrupt 的 finally 里 `callbacks[0].on_training_end()` 清理进度条（exp_manager.py:278-279）。

## ④ 数据流

**训练链**：`setup_experiment()` 里 `_preprocess_hyperparams`（exp_manager.py:210）+ `create_callbacks()`（exp_manager.py:222）汇成 `self.callbacks` → `model.learn`（exp_manager.py:272）。`create_callbacks()` 三段式（exp_manager.py:568-603）：①`--progress` 追加 `ProgressBarCallback`（exp_manager.py:569-570）；②`save_freq > 0` 追加 `CheckpointCallback`，`save_freq` 先 `// n_envs` 折算（exp_manager.py:572-582）；③`eval_freq > 0 且非调参模式`时构造 `SaveVecNormalizeCallback(save_freq=1, save_path=self.params_path)` 挂为 `EvalCallback` 的 `callback_on_new_best`（exp_manager.py:585、592-603），`eval_freq` 同样 `// n_envs`（exp_manager.py:586-587）。触发时序：SB3 评估发现新最优 → 存 `best_model.zip` → 触发 `callback_on_new_best` → 存 `vecnormalize.pkl`（save_freq=1 即"被触发即保存"）。

**调参链**：`optimize_agent()` 里 `optuna_eval_freq = int(n_timesteps / n_evaluations)` 再 `// n_envs`（exp_manager.py:839-841），重建 yml 回调 + 追加 `TrialEvalCallback`（exp_manager.py:847-855）后 `model.learn(callback=callbacks)`（exp_manager.py:866）；结束读 `is_pruned / last_mean_reward`（exp_manager.py:881-882），剪枝则 `raise optuna.exceptions.TrialPruned()`（exp_manager.py:888）。

## ⑤ 设计决策

- **stats 与 best model 的原子性**：running average 随训练漂移，checkpoint 与 stats 不同刻保存会让评估时观测归一化错位。挂 `callback_on_new_best` 而非独立周期保存，让 `best_model.zip` 与 `vecnormalize.pkl` 永远同刻成对；训练收尾时 `save_trained_model` 再存最终 stats（exp_manager.py:303-306）。
- **调参线分流**：`create_callbacks` 显式 `not self.optimize_hyperparameters`（exp_manager.py:585）——调参需要 optuna 汇报/剪枝通道而非 best model 管理，且每 trial 必须新回调实例。
- **monkey-patch 而非子类化**：ParallelTrainCallback 面对已构造好的模型对象，patch `train/save` 是最小侵入方案，代价是 `model.actor` 引用要手工重接（callbacks.py:192）。TODO 注释承认 blocking mode 与 force sync 两个正确性缺口（callbacks.py:102-105）——实验性回调，默认不启用。
- **RawStatisticsCallback 绕过 logger**：SB3 logger 对 rollout 统计做 EMA/分桶会失真，直写 writer 保真，代价是强依赖 tensorboard 格式。zoo 整体只写"SB3 没有的语义"，通用能力复用，避免与上游 API 演进打架。

## ⑥ 新人提示

- **读码入口**：从 exp_manager.py:568 `create_callbacks()` 进，先看三条 append 分支再读 callbacks.py 四类；调参线另走 exp_manager.py:846。
- **连锁反应**：动 `eval_freq/save_freq` 的 `// n_envs` 折算（exp_manager.py:574、587）改变所有环境的实际评估/存盘频率；yml 加 `callback:` 键（dict 形式可传 kwargs，utils.py:178-183）会同时进入 `specified_callbacks` 与每个 optuna trial。
- **坑一**：ParallelTrainCallback 的同步点是 `_on_rollout_end`（callbacks.py:185），`train_freq` 配错则参数永不同步；且仅支持 SAC/TQC（callbacks.py:133）。
- **坑二**：RawStatisticsCallback 不开 `--tensorboard-log` 直接 assert 崩（callbacks.py:224）；TrialEvalCallback 上报的 x 轴是 `eval_idx`（第几次评估）而非环境步数（callbacks.py:48、51），画剪枝曲线时别误读。

<!-- chars(no-space): 5518, anchors: 61 -->
