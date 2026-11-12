# 12 · 录像与训练记录：record_video.py 的 VecVideoRecorder 装配 + record_training.py 的定时快照 subprocess 链

## ① 角色定位

RL 实验的可视化出口。`rl_zoo3/record_video.py` 负责给**单个**已保存模型（final/best/指定 checkpoint）录一段 mp4；`rl_zoo3/record_training.py` 负责把**一次训练的全过程**讲成一个故事——对每个定时 checkpoint、final model、best model 各录一段短视频，ffmpeg 叠上进度字幕再拼接成 `training.mp4`（可选 `training.gif`），一眼看到策略从随机到收敛的演化。前者是可独立复用的原子能力，后者是编排器：自己不碰任何模型，纯粹用 `subprocess` 反复调用前者。两脚本都不在 `rl_zoo3/cli.py` 的分发表里，只能 `python -m rl_zoo3.record_video / record_training` 直跑（`docs/guide/enjoy.md:58/83`）。

## ② 内部结构

**record_video.py（167 行）**，纯 `__main__` 脚本，六段：

- **argparse**（`rl_zoo3/record_video.py:15-50`）：`--env` 默认 CartPole-v1、`-f` 默认 rl-trained-agents、`--algo` 默认 ppo（`:16-19`）；`-n` 默认 1000 步（`:20`）；`--load-best/--load-checkpoint/--load-last-checkpoint` 三种模型定位（`:29-42`）；`--env-kwargs` 用 `StoreDict` 收 dict（`:43-45`）。
- **模型定位**：`get_model_path()`（`rl_zoo3/record_video.py:60-68`）返回三元组，其中 `name_prefix` 决定视频文件名——best 是 `best-model-{algo}-{env}`（`rl_zoo3/utils.py:495`）、显式 checkpoint 是 `checkpoint-{N}-{algo}-{env}`（`rl_zoo3/utils.py:498`）、默认 final 是 `final-model-{algo}-{env}`（`rl_zoo3/utils.py:514`）。
- **环境装配**：`get_saved_hyperparams` 读回超参与 stats 路径（`rl_zoo3/record_video.py:78-79`）；从 `args.yml` 用 `yaml.UnsafeLoader` 读回 env_kwargs（`rl_zoo3/record_video.py:82-88`）；**强制 `render_mode="rgb_array"`**（`rl_zoo3/record_video.py:94`，注释 "gym 0.26+"）——VecVideoRecorder 从 rgb 帧缓存截帧，human 模式截不到；`create_test_env()`（`rl_zoo3/record_video.py:96-105`）产出带 Monitor/VecNormalize 等包装的 VecEnv。
- **模型加载**：off-policy 算法 `buffer_size=1` 假 buffer（`rl_zoo3/record_video.py:108-115`，附 v1.6 `optimize_memory_usage` 兼容 hack）；Python≥3.8 时注入 `custom_objects` 把 `learning_rate/lr_schedule/clip_range` 替换成常数 0.0/lambda（`rl_zoo3/record_video.py:119-127`），专治旧 Python 存档的 schedule pickle 失配。
- **录像装配**（核心五连）：`VecVideoRecorder(env, video_folder, record_video_trigger=lambda x: x == 0, video_length=video_length, name_prefix=name_prefix)`（`rl_zoo3/record_video.py:141-147`）。trigger 收到的是累计步数，`x == 0` 即 reset 后第一步就开录；录满 `video_length` 步自动停。输出文件名 = `{name_prefix}-step-0-to-step-{N}.mp4`——`tests/test_enjoy.py:107` 断言的 `final-model-sac-Pendulum-v1-step-0-to-step-100.mp4` 即此格式。
- **rollout 循环**：`env.reset()`（`rl_zoo3/record_video.py:149`）→ 循环 `video_length` 次 `model.predict(obs, state=lstm_states, episode_start=episode_starts, deterministic=...)`（`rl_zoo3/record_video.py:153-159`，lstm_states/episode_starts 双状态传递支持 RecurrentPPO）→ 未 `--no-render` 时每步 `env.render()`（`rl_zoo3/record_video.py:160-161`）→ `env.step(action)`、`episode_starts = dones`（`rl_zoo3/record_video.py:162-163`）；`KeyboardInterrupt` 被吞掉保已录内容（`rl_zoo3/record_video.py:164-165`）；`env.close()`（`rl_zoo3/record_video.py:167`）触发 ffmpeg 落盘——**不 close 视频是坏的**。

**record_training.py（161 行）**，编排器五段：

- **参数与定位**：argparse（`rl_zoo3/record_training.py:13-24`）比 record_video 精简（无 env-kwargs/custom-objects，多 `-g/--gif`）；`--exp-id 0` 时 `get_latest_run_id` 取最新实验（`rl_zoo3/record_training.py:36-38`）；拼出 `log_path = {folder}/{algo}/{env}_{exp_id}`（`rl_zoo3/record_training.py:40-43`）并 assert 存在（`:45`）。
- **快照发现**：`video_folder` 默认 `{log_path}/videos` 绝对路径（`rl_zoo3/record_training.py:47-48`），**先 `shutil.rmtree(ignore_errors=True)` 清场再重建**（`rl_zoo3/record_training.py:49-50`）——每次全量重录，不与旧视频混放；`os.scandir` 列 log_path 下文件（`:53`）、`filter` 出 `rl_model_` 前缀（`:54`）、`re.findall(r"\d+", x)[0]` 抠出步数（`:55`）、sort（`:56`）得到按时间升序的 checkpoint 步数表。
- **subprocess 链构造**：基础参数表 `args_final_model`（`rl_zoo3/record_training.py:58-77`）含 `--env/--algo/--exp-id/-f/-o/--n-timesteps/--n-envs/--seed`，并**硬编码 `--no-render`**（`:75-76`，注释 "Disable rendering to generate videos faster"——批量录制只靠 rgb_array 截帧，渲染纯属开销）；`if deterministic is not None: args_final_model.append("--deterministic")`（`rl_zoo3/record_training.py:78-79`）——见⑥的坑。三波录制：final model（zip 存在时，`rl_zoo3/record_training.py:81-83`）、best model（追加 `--load-best`，`:85-88`）、每个 checkpoint（复用参数表、只改末位 `--load-checkpoint {steps}`，`:90-95`），全部 `subprocess.call(["python", "-m", "rl_zoo3.record_video", ...])` 且 assert return_code==0（`:83/88/95`）。
- **排序与字幕**：扫回 video_folder 全部 mp4（`rl_zoo3/record_training.py:98`）；checkpoint 视频用 `get_number_from_checkpoint_filename`（正则 `checkpoint-(.*?)-`，`:103-109`）按步数排序（`:112`）；拼接顺序 = checkpoints（时间序）+ final + best（`:114-116`）——「演化过程 → 最终成果 → 最佳成果」的叙事线。字幕文本取文件名前两个词（`^(\w+)-(\w+)`，如 `checkpoint 10000`、`final model`，`:120-128`）。
- **ffmpeg 后处理**：逐视频生成 `*_with_text.mp4` 临时副本，`drawtext` 白字黑底半透明框居中在 y=12（`rl_zoo3/record_training.py:132-141`，`-y -hide_banner -loglevel error`）；写 `tmp.txt` concat 清单（`:144-147`，注意 open 模式是 `"a"`）后 `ffmpeg -f concat -safe 0 -c copy` 拼成 `training.mp4`（`:149-151`）；`--gif` 时再 `ffmpeg -vf fps=10` 转 `training.gif`（`:154-157`）；最后删掉全部临时字幕视频（`:159-161`）。

## ③ 外部连接

- **依赖 SB3**：`VecVideoRecorder`/`set_random_seed`（`rl_zoo3/record_video.py:8-9`）——recorder 是 VecEnv wrapper，包装 `create_test_env` 产出的整个 wrapper 栈（Monitor 在内也不干扰：录像读的是 render 帧，不是 Monitor 日志）。
- **依赖 zoo 内部**：`ExperimentManager.is_atari/is_minigrid` 判定随机策略默认值（`rl_zoo3/record_video.py:75-76`，atari/minigrid 默认 stochastic，`:134-135`）；`utils.py` 的 `ALGOS/create_test_env/get_model_path/get_saved_hyperparams`（`rl_zoo3/record_video.py:12`）；`get_latest_run_id`（`rl_zoo3/record_training.py:10`）。
- **被测试覆盖**：`tests/test_enjoy.py:96-108` `test_record_video` 录 100 步断言 mp4 非空；`:110-131` `test_record_training` 先 `train.py -n 10000 --save-freq 4000` 制造两个 checkpoint 再录制，断言 `training.mp4` 与 gif 存在——两测试无 DISPLAY 即 skip（`:98-99/116-117`）。
- **被文档消费**：`docs/guide/enjoy.md:55-76` 三个 record_video 示例（final/best/checkpoint 10000）、`:78-92` record_training 示例（含 `--gif` 变体）。
- **系统依赖 ffmpeg**：`env.close()` 内部编码与 record_training 的 drawtext/concat/gif 四类调用全部依赖 PATH 里的 ffmpeg，缺失时报错分散在上游。
- **上游呼应**：huggingface_sb3 的 `_generate_replay`（push_to_hub.py Step 4 借用）内部也是同样的 VecVideoRecorder+predict 循环——zoo 版是它的原型。

## ④ 数据流

单模型链：CLI 参数 → `get_model_path` 出 (name_prefix, model_path, log_path) → `create_test_env` 出 VecEnv → `ALGOS[algo].load` 出 model → VecVideoRecorder 包装 → N 步 predict/step 循环（帧被 recorder 每步缓存）→ `close()` 时 ffmpeg 编码 `{name_prefix}-step-0-to-step-{N}.mp4` 落入 video_folder。训练记录链：log_path 目录清单（rl_model_*_steps.zip 序列 + {env}.zip + best_model.zip）→ 步数表 → 每项一次 `python -m rl_zoo3.record_video` 子进程（各自独立加载环境与模型）→ video_folder 收集 N 个 mp4 → 排序 → drawtext 字幕 → concat → training.mp4（→ gif）→ 清理。典型命令：`python -m rl_zoo3.record_training --algo ppo --env CartPole-v1 -n 1000 -f logs --deterministic --gif`（`docs/guide/enjoy.md:90`），前提是训练时 `--save-freq` 留下过 checkpoint（`tests/test_enjoy.py:117` 的 `--save-freq 4000` 即为此铺垫）。

## ⑤ 设计决策

- **subprocess 而非进程内循环**：每段视频需要全新的 env 栈与模型加载，子进程天然隔离 VecNormalize 统计、随机态与 GPU 上下文，一次崩溃只 assert 一处；与 `scripts/migrate_to_hub.py:19` 的批量上传同一编排风格。代价是每个 checkpoint 都要冷启动一次（模型+环境加载），checkpoint 多时总时长线性膨胀——这正是 `--no-render` 硬编码（`rl_zoo3/record_training.py:76`）的动机。
- **name_prefix 即协议**：视频名由 `get_model_path` 的分支决定（`utils.py:495/498/514`），record_training 全靠文件名前缀反向分类（`:100/114/115`）与抠步数（`:104`）——两个脚本间的契约是「命名」而非任何元数据文件。
- **trigger 设计**：`lambda x: x == 0` 让录制窗口严格等于前 `video_length` 步；想录训练中段就得改 trigger 语义，zoo 选择不暴露这个自由度，保持「每段视频从头 reset」的可比性。
- **rmtree 清场**（`rl_zoo3/record_training.py:49`）：视频目录是派生品，宁可全删重录也不做增量——避免旧 run 的 mp4 混进本次 concat 清单。
- **与 push_to_hub 分工**：replay.mp4（上传用）走 huggingface_sb3 临时目录方案，zoo 本地录像走持久 videos/ 目录；两条路共用 SB3 的 VecVideoRecorder，但产物归宿不同，故不合并。

## ⑥ 新人提示

- **读码入口**：record_video 从 `rl_zoo3/record_video.py:141` 的 VecVideoRecorder 装配往上读；record_training 从 `rl_zoo3/record_training.py:58` 的参数表往下读，其余全是 ffmpeg 后处理。
- **已知怪味 `rl_zoo3/record_training.py:78-79`**：`if deterministic is not None:` 对 bool 恒真，`--deterministic` 实际总是被追加——想改行为先改这行（应是 `if deterministic:`），并注意会改变所有既有 training.mp4 的策略采样。
- **不 close 无视频**：`rl_zoo3/record_video.py:167` 的 `env.close()` 是落盘触发点；自定义循环时提前 return 会拿到空/坏 mp4（test 里专门断言文件非空，`tests/test_enjoy.py:108`）。
- **rgb_array 是硬前提**：`rl_zoo3/record_video.py:94` 强制覆写 render_mode；若某自定义 env 不支持 rgb_array，录像层拿不到帧，表现为 mp4 零字节。
- **ffmpeg 命令是 os.system 拼串**（`record_training.py:136-141/150/156`）：路径含空格/引号即碎；tmp.txt 用追加模式 `"a"`（`:145`），目录没清干净时旧清单会污染 concat。
- **改动连锁**：动 `utils.py::get_model_path` 的 name_prefix 命名会同时打断 record_training 的前缀过滤/排序/字幕提取三处正则（`record_training.py:100/104/121`）与 test 的文件名断言（`tests/test_enjoy.py:107`）；动 checkpoint 保存命名（`rl_model_*_steps.zip`）同理——`rl_zoo3/record_training.py:54-55` 的 filter+findall 是唯一发现机制。
- **无头环境**：两个 test 都在无 DISPLAY 时 skip（`tests/test_enjoy.py:98-99`），CI 里录像覆盖默认不跑；docker 内使用需 xvfb 或确认 env 纯 rgb_array。

<!-- chars(no-space): 7496, anchors: 51 -->
