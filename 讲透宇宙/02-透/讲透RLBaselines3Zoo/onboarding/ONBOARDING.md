# RL Baselines3 Zoo（rl-baselines3-zoo）ONBOARDING

> 图谱 201 节点/389 边/15 层/16 步 tour；commit `3ef9b46`，版本 2.9.2a2（`rl_zoo3/version.txt:1`）；`file:line` 锚均实读自源码。

## 1. 项目是什么：SB3 生态里的"训练基建"层

RL Baselines3 Zoo（DLR-RM 出品）是围绕 Stable-Baselines3 的**训练基建仓**，生态位三分：**SB3（算法层）**提供 DQN/PPO/SAC 实现与 VecEnv/callback 组件；**Gymnasium（环境层）**提供 Env API 与 registry；**zoo（本仓，基建层）不实现任何算法**——`rl_zoo3/utils.py:27` 的 `ALGOS` 表只是把 11 个算法名映射到实现类（前 6 个来自 SB3，其余来自 sb3-contrib）。

zoo 填"算法库之上、具体实验之下"的空档：**超参哪里找、一条命令怎么训练/评估/录像/上传、超参怎么搜、200+ 预训练智能体怎么复现**。核心资产是 13 份超参 YAML 矩阵与 Hub 预训练模型库（submodule，`.gitmodules:3`；benchmark.md 由 `rl_zoo3/benchmark.py:102` 生成）。四条主线：**训练→评估→调参→发布**。

## 2. 一分钟跑起来

```bash
git clone --recursive https://github.com/DLR-RM/rl-baselines3-zoo  # 拉预训练 submodule
cd rl-baselines3-zoo && pip install -e .
python train.py --algo ppo --env CartPole-v1 -n 5000   # 训练
python enjoy.py --algo ppo --env CartPole-v1 -n 5000   # 评估
```

三个入口：根目录 `train.py`/`enjoy.py` 是 4 行壳，转发包内同名模块（`rl_zoo3/train.py:21`，约 40 个参数）；pip 装后有 `rl-zoo3` 命令（`pyproject.toml:87`），`rl_zoo3/cli.py:18` 向 train/enjoy/plot_* 等五个子命令分发；env id 打错时 `rl_zoo3/train.py:180` 会 difflib 提示最近匹配；评估输出 `Mean reward: ...`（`rl_zoo3/enjoy.py:287`）。

## 3. 架构总览：15 层从门面到 CI

沿 tour 路线把 15 层压成六段：**门面**（README/benchmark.md/CHANGELOG）→**入口**（根壳 + cli.py；`rl_zoo3/__init__.py:3` 在包导入时副作用加载 gym_patches，补丁全局生效——排查行为差异先想到这里）→**命令层**（train/enjoy/record/push，"解析参数→委托 ExperimentManager"的薄层）→**中枢**（`rl_zoo3/exp_manager.py:64` 的 `ExperimentManager`，27 方法，见 §4）→**组件与基座**（callbacks/hyperparams_opt、`rl_zoo3/import_envs.py:10` try/except 导入 8 个可选环境包、`rl_zoo3/load_from_hub.py:13` 拉模型、utils/wrappers 基座）→**支撑层**（plots/Docker/CI 等）。

**主数据流**：CLI args → `rl_zoo3/train.py:233` 构造 ExperimentManager → `setup_experiment()`（`rl_zoo3/train.py:274`）读 YAML（如 `hyperparams/ppo.yml:37` 的 CartPole-v1 段）→ 预处理超参 → `create_envs`（默认 DummyVecEnv，`rl_zoo3/exp_manager.py:697` 有注释）→ `ALGOS[algo](env=..., **hyperparams)`（`rl_zoo3/exp_manager.py:237`）→ `model.learn()` → `save_trained_model`（`:287`，normalize 另存 vecnormalize.pkl）。产物落 `logs/<algo>/<env>_<N>/`，由 enjoy 反向消费：`get_model_path`（`rl_zoo3/enjoy.py:87`）→ 恢复超参 → `create_test_env`（`:164`）→ `ALGOS[algo].load`（`:204`）；反馈线是 plot_train（快查 monitor.csv）与 plot_from_file（rliable 报告）。

## 4. 核心子系统深潜

### 4.1 ExperimentManager：唯一编排中枢

`setup_experiment()`（`rl_zoo3/exp_manager.py:202`）：读超参 → `_preprocess_hyperparams`（schedule/normalize/noise/callbacks 在此物化）→ 建日志与回调 → `create_envs` → 建模。建模三分支（`:230-244`）：`-i` 续训、`--optimize` 时 `return None`（`:232-234`）、否则从头建；`setup_experiment()` 返回 None 即转 Optuna 分支（`rl_zoo3/train.py:288`）。

`read_hyperparameters`（`rl_zoo3/exp_manager.py:332`）是 YAML 消费口，四级段匹配：精确 env_id 段（`:349`）→ `atari` 段（`:351`）→ `default` 段（`:354`，静默打印提示）→ 报错。支持 `.yml`/`.py`（exec，`:339-343`）两种配置源，可叠加 Optuna trial 回填与 `-params` 覆写（`:364-366`，`rl_zoo3/utils.py:449` 的 `StoreDict` 把 `key:value` eval 成 dict）。

### 4.2 hyperparams YAML：仓库真正的核心资产

以 `hyperparams/ppo.yml`（587 行 44 段）为例：`default:`（`hyperparams/ppo.yml:2`）兜底 1e6 步 + MlpPolicy；`atari:`（`hyperparams/ppo.yml:6`）声明 AtariWrapper、frame_stack 4、CnnPolicy、`lin_2.5e-4` 学习率；具体环境段如 `CartPole-v1:`（`hyperparams/ppo.yml:37`）逐键覆盖，共享配置用 YAML 锚点 `:142`。`lin_` 前缀是魔法：`_preprocess_schedules`（`rl_zoo3/exp_manager.py:401`）把字符串拆成 `SimpleLinearSchedule`（`rl_zoo3/utils.py:296`），纯数字则包成常数——写成数字就没有线性衰减。

### 4.3 Optuna 超参搜索

`hyperparameters_optimization`（`rl_zoo3/exp_manager.py:892`）创建 study（JournalFileBackend 支持分布式续跑）；objective（`:803`）每 trial 调 `HYPERPARAMS_SAMPLER[algo]`（注册表 `rl_zoo3/hyperparams_opt.py:492`，11 算法）采样，经 `HYPERPARAMS_CONVERTER`（`:507`）转成 learn kwargs。巧思：`sample_ppo_params`（`rl_zoo3/hyperparams_opt.py:108`）用 `batch_size_pow` 在 2 的幂指数空间采样、`one_minus_gamma`（`:117`）对数空间采 `1-γ` 再换回（`rl_zoo3/hyperparams_opt.py:16`）。剪枝靠 `TrialEvalCallback` 报告中间评估值。

### 4.4 callbacks 四件套

`TrialEvalCallback`（`rl_zoo3/callbacks.py:16`，评估+剪枝）、`SaveVecNormalizeCallback`（`:59`，同步保存 VecNormalize 统计）、`ParallelTrainCallback`（`:96`，采样/训练双线程）、`RawStatisticsCallback`（`:206`，episode 数据直写 TensorBoard）。注入方式是 YAML `callback:` 键，由 `get_callback_list`（`rl_zoo3/utils.py:148`）解析成实例列表。

## 5. 代码地图

| 路径 | 导读 |
|---|---|
| `rl_zoo3/` | 包主体：exp_manager 中枢 + 四命令模块 + 基座 + plots 子包 |
| `hyperparams/` | 13 份算法超参 YAML 矩阵 + python 配置示例 |
| `scripts/` | SLURM 消融/批量投递/docker 构建 |
| `tests/` | 5 个集成测试 + dummy_env/ 测试环境包 |
| `logs/` | 训练输出 |
| `rl-trained-agents/` | 预训练智能体 submodule |
| `docker/` `.github/` `docs/` | 镜像；模板+三工作流；Sphinx 源 |

## 6. 测试与质量线

测试哲学是**subprocess 端到端真跑 CLI**（`tests/test_train.py:35` 即 `subprocess.call(shlex.split(cmd))`），不 mock。`test_train.py` 9 用例覆盖冒烟/续训/`-conf`/default 兜底/自定义环境；`test_hyperparams_opt.py` 锁 2 sampler × 3 pruner × 7 实验矩阵；`test_wrappers.py` 用 `check_env`（`tests/test_wrappers.py:22`）校验 wrapper 链；`test_enjoy.py` 枚举全部预训练 agent 冒烟；dummy_env 装上即注册 `TestEnv-v0`（`tests/dummy_env/test_env/__init__.py:3`）。

CI 三闸：Python 3.10-3.13（`.github/workflows/ci.yml:23`）× Gymnasium 双版本；trained_agents.yml 从 Hub 回归全部模型；pypi-publish 走 OIDC。本地 `make commit-checks`（`Makefile:35`）。

## 7. 如何上手改代码

**加新环境**：① 已注册环境只需在 `hyperparams/<algo>.yml` 加一段（不加则 default 兜底）；② 第三方包在 `rl_zoo3/import_envs.py:10` 仿加 try/except import，或运行时 `--gym-packages your.env.module` 免改代码；③ 需预处理则写 wrapper（如 `HistoryWrapper`，`rl_zoo3/wrappers.py:136`），YAML 用全限定名挂进 `env_wrapper` 键，`get_wrapper_class`（`rl_zoo3/utils.py:49`）动态 import。

**加新算法**：`rl_zoo3/utils.py:27` ALGOS 加一行 → 新建 `hyperparams/<algo>.yml`（default 段即可）→ 要调参则在 hyperparams_opt.py 写 `sample_*`/`convert_*` 注册进 `:492`/`:507` 两表。

**加新超参**：YAML 段加 key 即可——未消费的键透传 `ALGOS[algo](**hyperparams)`（`rl_zoo3/exp_manager.py:237`）；只有需物化成对象（schedule/noise/wrapper）才动 `_preprocess_*`。

## 8. 常见坑与 FAQ

- **clone 忘 `--recursive`**：`rl-trained-agents/` 为空，enjoy 报错（README:90）。
- **以为专调参数，其实跑了 default**：段匹配失败是静默 fallback（`rl_zoo3/exp_manager.py:354` 只 print 一行），长任务前查日志。
- **学习率衰减没生效**：`learning_rate: 2.5e-4` 是常数；线性衰减必须写字符串 `lin_2.5e-4`（`rl_zoo3/exp_manager.py:401` 类型分派）。
- **评估奖励差一个量级**：normalize 模型评估须加载训练时的 VecNormalize 统计（保存于 `rl_zoo3/exp_manager.py:301`）。
- **gym 0.26+ 行为突变**：`rl_zoo3/gym_patches.py:15` 的 PatchedTimeLimit 改写 truncated 语义，`:9` 另有 `np.bool8` 补丁，由 `rl_zoo3/__init__.py:3` 全局生效。
- **n_envs 被强制 1**：ars 与 `--optimize` 模式下是硬编码特例（`rl_zoo3/exp_manager.py:225`），不是 bug。
- **SubprocVecEnv 没更快**：默认 DummyVecEnv（`rl_zoo3/exp_manager.py:697` 注释），需 `--vec-env subproc`。
- **FAQ**：模型在哪？`logs/<algo>/<env>_<N>/`，`-id 0` 取最新（`rl_zoo3/utils.py:471`）。从 Hub 拉？`enjoy.py -orga sb3`（`rl_zoo3/load_from_hub.py:13`）。批量消融？仿 `scripts/create_cluster_jobs.py:41`。
