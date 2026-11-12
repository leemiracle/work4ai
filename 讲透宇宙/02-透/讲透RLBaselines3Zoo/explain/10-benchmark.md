# 10 · rl_zoo3/benchmark.py——基准复现体系

## ① 角色定位

`rl_zoo3/benchmark.py`（206 行）是 zoo 的"训练后成绩单"生成器：枚举**所有**可用已训练 agent，逐个用子进程跑 `enjoy`（默认 15 万步），从落盘的 Monitor.csv 算平均 episode reward，把七列结果表写进 `logs/benchmark/benchmark.md` 并同步仓根 `benchmark.md`（README 首屏链接的大表，当前 221 行、199 数据行）。它串起三件事：**模型清单**（本地 `rl-trained-agents/` git 子模块 + HuggingFace `sb3` org 全量）、**评估执行器**（顺序 subprocess 调 `enjoy.py`）、**结果表口径**（单 run、确定性策略、自我声明的"非定量 benchmark"）。结构上是纯模块级脚本：argparse 与主循环都在 import 时执行、无函数包裹（benchmark.py:16 起），入口 `python -m rl_zoo3.benchmark`（表头自述 benchmark.py:173）；它**不在** cli.py:11-19 的 `known_scripts` 里，与 plots 三件套的接入方式形成对照。

## ② 内部结构

**1) 参数面（benchmark.py:16-27)**：`--log-dir` 默认 `rl-trained-agents/`（benchmark.py:17，.gitmodules 声明的子模块）；`--benchmark-dir` 默认 `logs/benchmark/`（benchmark.py:18）；`-n` 默认 150000（benchmark.py:19）；`--seed` 默认 0（benchmark.py:22）；`--test-mode` 只做第一个实验（benchmark.py:23）；`--with-mujoco` 连 Fetch 一起跑（benchmark.py:24）；`--no-hub` 不拉 HF 清单（benchmark.py:25）；`--num-threads` 默认 2（benchmark.py:26）。

**2) 模型清单（benchmark.py:29-32)**：`get_trained_models(log_dir)`（utils.py:325-343）扫 `<algo>/<model_folder>/*/args.yml`，glob 须恰好一个（utils.py:335-337），读回 `env` 字段；`get_hf_trained_models()`（utils.py:346-386）用 `HfApi().list_models(author="sb3", cardData=True)`（utils.py:358-359）解析 model card 的 `model-index` 拿 env_id 与算法名（utils.py:366-370）。两者 update 合并。

**3) results 收集器（benchmark.py:35-43)**：七列 dict——`algo/env_id/mean_reward/std_reward/n_timesteps/eval_timesteps/eval_episodes`。

**4) 主循环（benchmark.py:45-155)**：解包 `algo, env_id`（benchmark.py:46）；`her` 跳过（benchmark.py:51-52，HER 已降级为 replay buffer class）；off-policy 名单 `dqn/qrdqn/ddpg/sac/td3/tqc` 强制 `n_envs = 1` 并 `n_timesteps *= args.n_envs` 补偿（benchmark.py:54-56）——on-policy 可并行采样、off-policy 只支持单 env，步数预算拉平；`reward_log = benchmark_dir/<model_name>`（benchmark.py:58）；组装 16 项命令行参数（benchmark.py:59-79），关键是 `--reward-log` 与 `--no-render/--seed/--verbose 0`。

**5) 断点续跑判定（benchmark.py:84-97)**：`reward_log` 目录已有非空 Monitor.csv（`ts2xy(load_results(reward_log), "timesteps")` 非空）则 `skip_eval = True`（benchmark.py:85-90）；Fetch/mujoco 无 `--with-mujoco` 跳过（benchmark.py:94-97）。

**6) 子进程评估（benchmark.py:99-106)**：`subprocess.call(["python", "enjoy.py", *arguments])`（benchmark.py:102），返回码非零只跳过不中断（benchmark.py:103-105）；随后 `x, y = ts2xy(load_results(reward_log), "timesteps")`（benchmark.py:106）——x 是 `np.cumsum(l)` 累计步数、y 是逐 episode 回报。

**7) 训练步数列（benchmark.py:110-135)**：`get_latest_run_id`（utils.py:389-404）定位实验目录，`get_saved_hyperparams`（utils.py:407-446）读 `config.yml`（utils.py:425-429）；模型不在本地时空 `hyperparams` 触发 `download_from_hub(organization="sb3", ...)` 自动下载后重读（benchmark.py:113-129）；训练步数格式化 `k/M` 后缀（benchmark.py:131-135）。

**8) 统计（benchmark.py:137-155)**：`mean_reward = np.mean(y)`、`std_reward = np.std(y)`（benchmark.py:137-138）——是**全体评估 episode 的均值**而非末段；`eval_timesteps` 取 `x[-1]`、`eval_episodes` 取 `len(y)`（benchmark.py:144-145）。

**9) 出表（benchmark.py:157-205)**：`pd.DataFrame` → `sort_values(by=["algo", "env_id"])`（benchmark.py:160）→ `MarkdownTableWriter(max_precision=3).from_dataframe`（benchmark.py:166-167）；表头文案硬编码（benchmark.py:169-189）先写 `benchmark-dir/benchmark.md`（benchmark.py:192-197），非 test-mode 再 `shutil.copy` 覆盖仓根（benchmark.py:200-201）。

## ③ 外部连接

- **imports**（benchmark.py:7-14）：pandas/pytablewriter、`huggingface_sb3.EnvironmentName`、SB3 的 `load_results, ts2xy`、包内 `download_from_hub` 与 utils 四函数。
- **calls 出去**：子进程 `enjoy.py`（实现见 06 篇）。`--reward-log`（enjoy.py:55）被转成 `log_dir`（enjoy.py:162）传 `create_test_env`（enjoy.py:164-174），经 `make_vec_env(monitor_dir=log_dir)`（utils.py:257-266）给每个 env 套 SB3 `Monitor`，落盘 `<reward_log>/0.monitor.csv`——实证 `logs/benchmark/a2c-Acrobot-v1/0.monitor.csv`（首行 `#{"t_start": ..., "env_id": "Acrobot-v1"}`，次行 `r,l,t`）。
- **CI 工作流联动（.github/workflows/trained_agents.yml）**：workflow 名 `Check-Trained-Agents`（trained_agents.yml:4），push/PR master 触发（trained_agents.yml:6-10），checkout `submodules: true` 拉权重仓（trained_agents.yml:33），核心步骤 `make check-trained-agents`（trained_agents.yml:61-63）→ Makefile:8-9 即 `pytest -k trained_agent` → 命中 `test_trained_agents`（tests/test_enjoy.py:26-28），parametrize 列表同为"本地 + HF"两源（tests/test_enjoy.py:21-23），每 agent 起子进程 `python enjoy.py ... -n 100` 断言返回码 0（tests/test_enjoy.py:58-59）。它带 `@pytest.mark.slow`（tests/test_enjoy.py:27），被常规 CI 的 `-m "not slow"`（scripts/run_tests.sh）排除——常规 CI 只跑 `test_benchmark`（tests/test_enjoy.py:63-65，`--test-mode --no-hub` 验证脚本不炸）。

## ④ 数据流

以 `a2c / Acrobot-v1` 一行为例：`get_trained_models` 从 args.yml 还原 `(a2c, Acrobot-v1)`（utils.py:335-342）→ `subprocess.call(["python", "enjoy.py", "-n", "150000", ..., "--reward-log", "logs/benchmark/a2c-Acrobot-v1"])`（benchmark.py:102）→ enjoy 重建环境（VecNormalize 冻结，utils.py:282-285）逐 episode 推理 → `Monitor` 每完结一局向 csv 追加一行 → 主进程 `load_results` + `ts2xy`（benchmark.py:106）→ 均值/标准差/末步数/episode 数（benchmark.py:137-145）→ 收满排序出表。该行实况：`a2c | Acrobot-v1 | -83.353 | 17.213 | 500k | 149979 | 1778`（benchmark.md）——500k 来自 config.yml 格式化，149979/1778 说明 15 万步跑了 1778 局。

## ⑤ 设计决策

- **subprocess 隔离而非进程内调 enjoy()**：约 200 个模型连续评估，进程内反复 `model.load` 会累积内存与句柄；子进程崩了只 `continue`（benchmark.py:103-105），且与 CI test_trained_agents 同构，评估行为两边一致。
- **口径诚实声明**：表头明言"not a quantitative benchmark ... only one run (cf issue #38)"、定位是"查算法最大性能、找 bug、提供预训练 agent"（benchmark.py:182-185）——故只有 mean±std 无显著性检验；`eval_episodes` 列让读者自判样本量。除 Atari 外确定性策略（benchmark.py:177）。
- **skip_eval 幂等续跑**（benchmark.py:84-90）：全量以天计，有旧 csv 就跳过——代价是改了 enjoy 想重评须手删目录。
- **HF 兜底下载**（benchmark.py:113-129）：清单含 HF 全量而本地子模块可能没拉全，缺谁下载谁。
- **off-policy 名单两处维护**：benchmark.py:54 与 enjoy.py:127 各一份，增删算法要同步。
- **顺序执行零并行**：串行换脚本极简与单机可控；要并行就多进程分片（reward_log 按 model_name 分目录，配合 skip_eval 不冲突）。

## ⑥ 新人提示

- **读码入口**：线性脚本从 benchmark.py:29 顺读；配套 utils.py:325-404 三个清单/定位函数。
- **`--n-envs` 语义陷阱**：off-policy 下实际跑 `-n × --n-envs` 步（benchmark.py:56）且被强制单 env——加速只有分片。
- **benchmark.md 是生成物**：手改必被覆盖（benchmark.py:200-201）；改表头要改 benchmark.py:169-189 而非 md。
- **旧 env id 漂移**：表里 `LunarLander-v2`/`-v3` 系列是历史训练产物与当前 gymnasium v3 命名并存；CI 对 Lander、`-v3`、Panda、MiniGrid 有 skip 分支（tests/test_enjoy.py:41-55）。
- **复现单行数字**：`--seed 0` + 确定性策略下 enjoy 单 run 可复现，但跨机器 float 差异仍可能让末位抖动——表口径本来就是"指示性"的。
- **与 plots 的关系**：复用 `load_results/ts2xy/pytablewriter` 同一地基，但自成一路直出 markdown 表（无 pkl 中间层）；plots 管线消费训练期日志，不消费 benchmark 输出。

<!-- chars(no-space): 5794, anchors: 79 -->
