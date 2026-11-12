# 06 · rl_zoo3/enjoy.py——评估与模型加载主流程

## ① 角色定位

`rl_zoo3/enjoy.py` 是 zoo 的推理/评估入口：给定 `--algo` 与 `--env`，把训练产物三件套（`<env>.zip` 模型、`vecnormalize.pkl` 归一化 stats、`config.yml`/`args.yml` 超参快照）还原成可交互的评估环境，跑 N 步并汇报平均回报。它与训练侧评估（`EvalCallback`，见 05 篇）是两条独立链路——enjoy 是纯离线的事后评估/演示工具。整个文件就是一个 277 行的 `def enjoy() -> None:  # noqa: C901` 大函数（enjoy.py:20）。它有三个宿主：根目录壳 `rl_zoo3/enjoy.py:1` 的 `from rl_zoo3.enjoy import enjoy`、CLI 分发器 cli.py:3+15 的 `"enjoy": enjoy` 注册表、pyproject.toml:86-87 的 console_scripts（故 `rl_zoo3 enjoy ...` 与 `python enjoy.py ...` 等价）。姊妹实现 `rl_zoo3/record_video.py:10-11` 复用同一套 `create_test_env/get_model_path/get_saved_hyperparams`，只把渲染换成 `VecVideoRecorder`。

## ② 内部结构

**1) argparse 参数面（enjoy.py:21-76）**：`--env` 用 huggingface_sb3 的 `EnvironmentName` 类型，`-f` 默认 `rl-trained-agents`，`--exp-id` 默认 0 表示取最新实验号；三种加载变体 `--load-best`/`--load-checkpoint <steps>`/`--load-last-checkpoint`（enjoy.py:35-49）；`--stochastic` 与 `--norm-reward` 两个语义开关（enjoy.py:50-53）；`--env-kwargs` 借 `StoreDict` action 把 `key:value` 对解析成 dict（enjoy.py:63-65，实现在 utils.py:449）。

**2) 环境注册与模型定位（enjoy.py:79-124）**：先 `importlib.import_module` 用户 `--gym-packages` 让自定义环境注册进全局 registry（enjoy.py:79-80）。`get_model_path(...)`（enjoy.py:87-95，实现在 utils.py:471-520）解析出 `(name_prefix, model_path, log_path)`：`exp_id=0` 查最新实验号、`-1` 不带实验子目录，文件名四分支 best_model.zip / `rl_model_<steps>_steps.zip` / 最大步数 checkpoint / 默认 `<env>.zip`（utils.py:493-514），找不到 raise ValueError。enjoy 捕获后特判：folder 含 `rl-trained-agents` 就 `download_from_hub(organization="sb3", ...)` 自动从 HuggingFace 下载再重试（enjoy.py:99-122），否则 re-raise。

**3) 离线准备（enjoy.py:127-160）**：`set_random_seed(args.seed)`（enjoy.py:129，默认 0）与 `th.set_num_threads`（enjoy.py:131-134）；`ExperimentManager.is_atari/is_minigrid` 静态判定（enjoy.py:136-137，实现在 exp_manager.py:610-615）——只借静态分类工具，不构造 ExperimentManager。`get_saved_hyperparams(..., test_mode=True)`（enjoy.py:139-140，实现在 utils.py:407）读 `config.yml` 还原 `normalize` 与 `normalize_kwargs`（utils.py:425-445，test_mode 下 `norm_reward` 换成 CLI 值）。env_kwargs 三级合并：config.yml（enjoy.py:146-148）→ 存档 args.yml（enjoy.py:151-156）→ 命令行（enjoy.py:159-160），后者优先级最高。

**4) 重建环境（enjoy.py:164-174）**：调 `create_test_env(env_name.gym_id, n_envs, stats_path=maybe_stats_path, seed, log_dir, should_render, hyperparams, env_kwargs, ...)`。该函数（utils.py:203-293）做四件事：`n_envs>1` 选 `SubprocVecEnv`（utils.py:241）；要渲染且未指定则注入 `render_mode="human"`（utils.py:246-247）；用 `spec.make` 闭包过 `make_vec_env`（utils.py:254-266）再套 yml 声明的 `vec_env_wrapper`（utils.py:268-272）；最后 `VecNormalize.load(path_, env)` 加载 stats 并**冻结**——`env.training = False`（停更 running average）、`env.norm_reward = False`（汇报原始尺度回报）（utils.py:282-285），stats 缺失直接 ValueError（utils.py:287）；`frame_stack` 存在则补 `VecFrameStack`（utils.py:289-292）。

**5) 模型加载（enjoy.py:176-211）**：命中 off-policy 名单（enjoy.py:127）时 `kwargs.update(dict(buffer_size=1))`（enjoy.py:177-179）——评估不需要回放池，占位 1 条省内存；另有 `optimize_memory_usage` 与 SB3 v1.6 后 `handle_timeout_termination` 互斥的 hack（enjoy.py:180-184）。Python 3.8+ 加载旧模型时构造 `custom_objects`，把 `learning_rate/lr_schedule/clip_range` patch 成常数 0.0（enjoy.py:188-199）——推理用不到 schedule，也绕开旧 pickle 里 lambda 反序列化失败。HER 配置时把 env 塞回 kwargs（enjoy.py:201-202）。最终 `ALGOS[algo].load(model_path, custom_objects=..., device=args.device, **kwargs)`（enjoy.py:204；`ALGOS` 是 utils.py:27 的算法名→类映射）。

**6) episode 循环与汇总（enjoy.py:213-292）**：`obs = env.reset()`（enjoy.py:213）；确定性规则——默认 deterministic，仅当 `--stochastic` 或（atari/minigrid 且未显式 `--deterministic`）时转 stochastic（enjoy.py:216-217）。循环状态含 `lstm_states`、`episode_start = np.ones(...)` 与 HER 用的 `successes`（enjoy.py:219-225）；`-P` 时套 tqdm（enjoy.py:227-231）。每步 `model.predict(obs, state=lstm_states, episode_start=episode_start, deterministic=deterministic)` → `env.step(action)` → `episode_start = done`（enjoy.py:234-243）→ `env.render("human")`（enjoy.py:245-246）。统计口径：atari 分数从 `infos[0]["episode"]` 取（step reward 是裁剪值，enjoy.py:252-258）；普通环境 done 时打印并收集 Episode Reward/Length（enjoy.py:260-268）；HER 收集 `is_success` 并重置计数（enjoy.py:271-277）。`KeyboardInterrupt` 被静默吞掉（enjoy.py:279-280）——Ctrl+C 是合法退出，仍走汇总（success rate / mean reward ± std / mean length，enjoy.py:282-290），最后 `env.close()`（enjoy.py:292）。

## ③ 外部连接

- **imports 进来**（enjoy.py:9-17）：`huggingface_sb3.EnvironmentName`、SB3 的 `set_random_seed`/`tqdm`、`rl_zoo3.import_envs`（enjoy.py:13，副作用 import——注册 atari/minigrid 等 zoo 自定义环境）、`from rl_zoo3 import ALGOS, create_test_env, get_saved_hyperparams`（enjoy.py:14）、`ExperimentManager`/`download_from_hub`/`StoreDict, get_model_path`（enjoy.py:15-17）。
- **被谁调用**：根壳 enjoy.py:1-4、cli.py:3+15（`rl_zoo3 enjoy` 子命令）、tests/test_enjoy.py 回归。
- **calls 出去**：utils.py 的 `get_model_path/create_test_env/get_saved_hyperparams/StoreDict`、load_from_hub 的 `download_from_hub`、exp_manager 的 is_atari/is_minigrid。注意 enjoy **不调** `setup_experiment`——评估路径刻意绕开训练装配，只共享静态分类函数。

## ④ 数据流

完整调用链（`python enjoy.py --algo ppo --env CartPole-v1 -n 5000`）：

```
args → get_model_path → rl-trained-agents/ppo/CartPole-v1_1/CartPole-v1.zip
     → get_saved_hyperparams → {normalize: ...} + maybe_stats_path
     → env_kwargs 三级合并（config.yml → args.yml → CLI）
     → create_test_env → [VecNormalize(冻结) →] Monitor → DummyVecEnv → CartPole
     → PPO.load(model_path, custom_objects=..., seed=0)
     loop: predict(deterministic) → step → render → 收集 episode_reward/length
     → "N Episodes / Mean reward: μ ± σ" → env.close()
```

输入是磁盘训练产物目录，输出是终端统计 + 渲染画面 + 可选 `--reward-log` Monitor CSV（enjoy.py:162、169）。

## ⑤ 设计决策

- **stats 冻结而非沿用训练态**（utils.py:284-285）：`training=False` 防评估轨迹污染 running average；`norm_reward=False` 保证汇报值与原生环境同尺度——`--norm-reward` 只在想看训练目标值时手动打开（enjoy.py:261-263 注释）。
- **确定性默认、atari/minigrid 例外**（enjoy.py:216-217）：评估惯例 deterministic argmax，但像素环境策略在确定性模式下易陷入重复动作死循环，故反转默认值，`--deterministic` 仍可强制覆盖——三层优先级（显式 stochastic > 环境类别默认 > deterministic）。
- **两个加载 hack 都是"评估最小化"取向**：`buffer_size=1` 不分配回放池（enjoy.py:177-179）；`custom_objects` 不恢复 schedule 函数，同时是跨 Python 版本兼容垫片（enjoy.py:186-188 注释）。
- **自动 HF 下载只认 rl-trained-agents**（enjoy.py:99）：zoo 官方 pretrained agents 目录约定；用户自训目录报错应直给，不去 hub 猜。
- **atari 分数取 infos 而非 step reward**（enjoy.py:252-258）：atari reward 经裁剪/缩放不是真实分数，Monitor 的 `episode` info 才是原生计分。同理 `reward[0]` 只统计第一个子环境（enjoy.py:248）——`--n-envs > 1` 时统计仅对 env 0 有效。
- **KeyboardInterrupt 语义化**（enjoy.py:279-280）：与训练侧 `learn()` 吞 Ctrl+C 保 checkpoint（exp_manager.py:271-275）同一哲学——中断后仍输出已积累统计。

## ⑥ 新人提示

- **读码入口**：enjoy.py:20 单函数顺序读；先 87-124（定位）再 164-204（重建+加载），这两段是与 utils.py 的接缝；循环体 234-277 独立成块。
- **连锁反应**：动 `create_test_env`（utils.py:203）同时影响 enjoy、record_video.py 与 exp_manager 的 eval env 三处调用方；动加载 kwargs 分支（enjoy.py:176-202）要跑 tests/test_enjoy.py——它覆盖 best/checkpoint/HER 等加载变体。
- **坑一**：开了 normalize 的模型，`vecnormalize.pkl` 丢了评估直接 ValueError（utils.py:287）——三件套必须成套搬运；`--load-checkpoint` 传的是**步数**不是序号（enjoy.py:39-43），要与 `rl_model_<steps>_steps.zip` 文件名对上。
- **坑二**：atari/minigrid 上"没给 --stochastic 却是随机策略"不是 bug（enjoy.py:216），排障先看这条默认值反转；`episode_start = done`（enjoy.py:243）是 LSTM 策略的状态复位信号，重构循环时丢了会导致 RNN 策略跨 episode 状态泄漏、指标 silently 变差。

<!-- chars(no-space): 6460, anchors: 74 -->
