# 07 · 工具枢纽：rl_zoo3/utils.py——wrapper 装配、模型定位与 YAML 字面量解析

## ① 角色定位

`rl_zoo3/utils.py`（520 行）是 zoo 的共享工具箱 + 全局算法注册表，被四个 CLI（enjoy / record_video / push_to_hub / benchmark）和 `ExperimentManager` 共同依赖，填补 SB3 本体不管的三块空白：

1. **YAML 字面量 → Python 对象的马歇林**：hyperparams 里一切非平凡值（wrapper 类、callback、policy_kwargs、normalize 配置）以字符串/嵌套 dict 存在，utils 负责变成可调用对象；
2. **训练产物路径解析**：`logs/<algo>/<env>_<id>/` 目录约定下，best_model / checkpoint / final model 的定位与 run id 递增；
3. **评估期环境重建**：`create_test_env` 把训练时 YAML 声明的 wrapper 链、VecNormalize 统计、frame stacking 按同样顺序复刻——「训练-评估一致性」的基石。

文件头部的 `ALGOS` 字典（`rl_zoo3/utils.py:27-41`）兼任算法命名空间：6 个 SB3 核心算法（`rl_zoo3/utils.py:28-33`）+ 6 个 sb3_contrib 算法（`rl_zoo3/utils.py:35-40`），`"ppo_lstm"` 是 `RecurrentPPO` 的 zoo 专属别名键（`rl_zoo3/utils.py:40`）；`rl_zoo3/train.py:23` 的 `--algo` choices 直接取 `ALGOS.keys()`。

## ② 内部结构

按职能分五组：

**A. 算法表**：`ALGOS`（`rl_zoo3/utils.py:27-41`），值是 `BaseAlgorithm` 子类。

**B. YAML 字面量解析器三件套**：

- `get_wrapper_class(hyperparams, key="env_wrapper")`（`rl_zoo3/utils.py:49-125`）：把 `env_wrapper` / `vec_env_wrapper` 键解析成组合闭包。每个条目三种形态——纯字符串点分路径（`importlib.import_module` + `getattr`，`rl_zoo3/utils.py:104-106`）、直接传类对象（`rl_zoo3/utils.py:107-109`）、单键 dict 携带 kwargs（`rl_zoo3/utils.py:92-102`，assert len==1 防 YAML 缩进错，`rl_zoo3/utils.py:93-97`）；列表即多 wrapper（`rl_zoo3/utils.py:82-90`）。返回闭包 `wrap_env` 按 YAML 声明序逐层包裹（`rl_zoo3/utils.py:118-123`，`zip(..., strict=True)` 保证类与 kwargs 等长）。
- `get_class_by_name`（`rl_zoo3/utils.py:128-145`）：通用「全名字符串→类」工具，get_callback_list 与自定义 policy 导入（`rl_zoo3/exp_manager.py:507`）都走它。
- `get_callback_list`（`rl_zoo3/utils.py:148-200`）：同一套形态处理（str/列表/单键 dict kwargs，`rl_zoo3/utils.py:181-191`），区别是直接 `callback_class(**kwargs)` 实例化（`rl_zoo3/utils.py:197-198`），且接受现成 `BaseCallback` 实例直通（`rl_zoo3/utils.py:193-195`）。
- `StoreDict`（`rl_zoo3/utils.py:449-468`）：argparse 自定义 Action，把 `--env-kwargs key:value` 切分（`rl_zoo3/utils.py:464-465`）后 eval 成 Python 值（`rl_zoo3/utils.py:467`），CLI 侧的字面量解析器。

**C. `create_test_env`**（`rl_zoo3/utils.py:203-293`）：评估环境装配链，详见④。

**D. 学习率 schedule**：`SimpleLinearSchedule`（`rl_zoo3/utils.py:296-312`）——`__call__(progress_remaining)` 返回 `progress_remaining * initial_value`（`rl_zoo3/utils.py:308-309`）线性归零；工厂 `linear_schedule`（`rl_zoo3/utils.py:315-322`）。`_preprocess_schedules` 把 YAML 里的 `"linear_0.001"` 切成它（`rl_zoo3/exp_manager.py:414-416`）。

**E. 训练产物定位四件套**：

- `get_trained_models`（`rl_zoo3/utils.py:325-343`）：扫 `logs/<algo>/<model_folder>/*/args.yml`（恰好一份，`rl_zoo3/utils.py:335-337`），UnsafeLoader 读出 env id（`rl_zoo3/utils.py:339`），组装 `ModelName`（`rl_zoo3/utils.py:341`）。
- `get_hf_trained_models`（`rl_zoo3/utils.py:346-386`）：`HfApi().list_models(cardData=True)`（`rl_zoo3/utils.py:358-359`），从 model card 的 `model-index` 抠 env id 与算法名（`rl_zoo3/utils.py:366-367`），hub 的 `recurrentppo` 归一化回 `ppo_lstm`（`rl_zoo3/utils.py:369-370`）；`check_filename` 时逐模型核对文件名约定（`rl_zoo3/utils.py:379-382`）。
- `get_latest_run_id`（`rl_zoo3/utils.py:389-404`）：glob `<env>_[0-9]*` 目录（`rl_zoo3/utils.py:399`），剥尾段数字取最大（`rl_zoo3/utils.py:400-403`）。
- `get_model_path`（`rl_zoo3/utils.py:471-520`）：`exp_id=0` 取最新 run（`rl_zoo3/utils.py:480-482`），`exp_id=-1` 表示无实验子目录、直接用 `folder/algo`（`rl_zoo3/utils.py:484-487`）；四种加载模式互斥——`load_best` → `best_model.zip`（`rl_zoo3/utils.py:493-495`）、`load_checkpoint=<n>` → `rl_model_<n>_steps.zip`（`rl_zoo3/utils.py:496-498`）、`load_last_checkpoint` → glob 后按步数排序取最大（`step_count` 从路径尾段倒数取数字以避开其他下划线，`rl_zoo3/utils.py:504-510`）、默认 final `<env>.zip`（`rl_zoo3/utils.py:511-514`）；不存在抛 `ValueError`（`rl_zoo3/utils.py:516-518`）；返回 `(name_prefix, model_path, log_path)`（`rl_zoo3/utils.py:520`）。
- `get_saved_hyperparams`（`rl_zoo3/utils.py:407-446`）：优先读 `<stats_path>/config.yml`（UnsafeLoader，`rl_zoo3/utils.py:425-429`），`normalize` 缺省 False（`rl_zoo3/utils.py:430`）；无 config.yml 时退回探测旧版 `obs_rms.pkl`（`rl_zoo3/utils.py:432-433`）；再把 `normalize` 统一成 `normalize_kwargs`——字符串形态 `eval`（`rl_zoo3/utils.py:437-438`）、dict 直用（`rl_zoo3/utils.py:441-442`）、布尔拼 `{"norm_obs": ..., "norm_reward": norm_reward}`（`rl_zoo3/utils.py:443-444`）；`test_mode=True` 允许覆盖 `norm_reward`（`rl_zoo3/utils.py:439-440`）。

## ③ 外部连接

**imports 出去**：gymnasium（`rl_zoo3/utils.py:9`）、sb3_contrib 六算法（`rl_zoo3/utils.py:16`）、SB3 的 `make_vec_env` 与五个 vec_env 类（`rl_zoo3/utils.py:20-22`）、`HfApi` + `huggingface_sb3` 的 `EnvironmentName/ModelName`（`rl_zoo3/utils.py:14-15`）、`torch.nn`（`rl_zoo3/utils.py:25`，注释明示为 eval 字面量里的激活函数名服务）、yaml（`rl_zoo3/utils.py:12`）。`RMSpropTFLike`（`rl_zoo3/utils.py:21`）是 `# noqa: F401`——专供 YAML 里 `dict(optimizer_class=RMSpropTFLike, ...)` 字面量在 eval 时解析到名字（`hyperparams/a2c.yml:19`）。

**被谁调用**（grep 实证）：`rl_zoo3/__init__.py:7-15` 导出 7 个公共符号；`enjoy.py:87,114,140,164`；`record_video.py:60,79,96`；`push_to_hub.py:324,353,373`；`benchmark.py:29,32,112,129`；`rl_zoo3/train.py:18`（只要 ALGOS + StoreDict）；`exp_manager.py:507,511,516,520,846`。测试侧 `tests/test_wrappers.py:12,37,56,63` 与 `tests/test_callbacks.py:7,37` 锁行为。

**跨文件到 SB3 本体**：`create_test_env` 的核心装配委托 SB3 `make_vec_env`——配套仓 `/usr-data/data1/workspace/rl/stable-baselines3`（2.9.2a0）的 `stable_baselines3/common/env_util.py:113` 先包 `Monitor`、`stable_baselines3/common/env_util.py:116` 后包 `wrapper_class`，**Monitor 在最内层**，`env_wrapper` 列表包在 Monitor 外面。

## ④ 数据流

**典型链 A：enjoy 的评估环境装配**（`enjoy.py:87→140→164→204`：get_model_path → get_saved_hyperparams → create_test_env → `ALGOS[algo].load`），`create_test_env` 九步：

1. `get_wrapper_class(hyperparams)` 解析 `env_wrapper`（`rl_zoo3/utils.py:232`），随即 del 该键（`rl_zoo3/utils.py:236-237`）——消费掉的键必须删；
2. `vec_env_cls` 缺省：`n_envs > 1` 用 `SubprocVecEnv`，否则 `DummyVecEnv`（`rl_zoo3/utils.py:240-241`）；
3. `deepcopy(env_kwargs)` 防共享引用，未指定 `render_mode` 且要渲染时注入 `render_mode="human"`（gym 0.26 兼容，`rl_zoo3/utils.py:243-247`）；
4. `gym.spec(env_id)` 在**父进程**查注册表拿 spec（`rl_zoo3/utils.py:249`）；
5. `make_env(**kwargs)` 闭包调 `spec.make`（`rl_zoo3/utils.py:254-255`，注释引 imitation#160：spec 落定后子进程不再依赖 registry 状态，`--gym-packages` 运行时改过 registry 也不怕）；
6. `make_vec_env`（`rl_zoo3/utils.py:257-266`）：每个子环境按「裸 env → `Monitor`（SB3 env_util.py:113）→ `wrapper_class` 逐层（env_util.py:116）」装配；YAML 列表顺序 = 由内向外；
7. 若有 `vec_env_wrapper` 键，取组合闭包包住整个 VecEnv（`rl_zoo3/utils.py:268-272`）；
8. `stats_path` 存在且 `normalize=True` 时 `VecNormalize.load(vecnormalize.pkl, env)` 并**冻结**：`training=False`、`norm_reward=False`（`rl_zoo3/utils.py:276-287`）——评估期不更新 running mean，reward 归一化默认关（`--norm-reward` 经 `rl_zoo3/utils.py:439-440` 穿透打开）；
9. `frame_stack` 键 >0 时再包 `VecFrameStack`（`rl_zoo3/utils.py:289-292`）。

**典型链 B：policy_kwargs 的字面量之旅**：YAML 里写成带引号字符串 `policy_kwargs: "dict(net_arch=[256, 256])"`（`hyperparams/dqn.yml:39`）；`read_hyperparameters` 用 `yaml.safe_load`（`rl_zoo3/exp_manager.py:338`）刻意保持字符串；`_preprocess_hyperparams` 才对 `policy_kwargs/replay_buffer_class/replay_buffer_kwargs` 三键统一 eval 成真对象（`rl_zoo3/exp_manager.py:477-479`），随后随 `**hyperparams` 进模型构造器。CLI 侧 `-params learning_rate:0.01` 走 `StoreDict` 同样 eval（`rl_zoo3/utils.py:467`）。

**典型链 C：`get_model_path` 消费者**：`rl_zoo3/enjoy.py:87`、`rl_zoo3/record_video.py:60`、`rl_zoo3/push_to_hub.py:324`，均解构三元组；`log_path` 随后喂给 `get_saved_hyperparams` 找同目录 `config.yml`。

## ⑤ 设计决策

1. **「YAML 保持纯数据 + 集中后置 eval」**：不用 `!!python/name:` tag，`safe_load` 就够（`rl_zoo3/exp_manager.py:338`）；Python 字面量集中在三处 eval（`rl_zoo3/exp_manager.py:477-479`、`rl_zoo3/utils.py:438`、`rl_zoo3/utils.py:467`）。收益是配置文件对非 Python 工具友好；代价是这三处是代码执行点——只应喂受信任的配置。
2. **`get_wrapper_class` 返回单一组合闭包而非类列表**：`make_vec_env` 只收一个 `wrapper_class` 参数，闭包（`rl_zoo3/utils.py:118-123`）把多 wrapper + kwargs 压平成统一接口，训练链（`rl_zoo3/exp_manager.py:511`）与评估链（`rl_zoo3/utils.py:232`）零差别复用。
3. **Monitor 最内层**（SB3 env_util.py:113 在 :116 之前）：AtariWrapper 等业务 wrapper 包在 Monitor 外，奖励日志不受 wrapper 改写影响。
4. **评估链不做 VecTransposeImage**：训练链 `rl_zoo3/exp_manager.py:723-746` 对 channel-last 图像兜底转置；`create_test_env` 不做——AtariWrapper 已产出 channel-first LazyFrames（`hyperparams/dqn.yml:7-8`），评估链刻意更瘦。
5. **`SimpleLinearSchedule` 不复用 SB3 LinearSchedule**：docstring 自述「simpler」（`rl_zoo3/utils.py:298-299`）——zoo 只需 `progress_remaining → 线性归零` 的裸 callable（`rl_zoo3/utils.py:308-309`）。
6. **「消费即删除」纪律**：`env_wrapper`/`vec_env_wrapper`（`rl_zoo3/utils.py:236-237,272`）、`normalize`/`frame_stack` 等 zoo 专属键（`rl_zoo3/exp_manager.py:509-512`）用完就 del，否则残留键随 `**hyperparams` 直捅模型构造器报 TypeError。
7. **hub 侧名称归一化**：`recurrentppo → ppo_lstm`（`rl_zoo3/utils.py:369-370`）与 ALGOS 别名键（`rl_zoo3/utils.py:40`）呼应——hub 与 zoo 两套命名规范的翻译放在工具层。

## ⑥ 新人提示

- **读码入口**：`ALGOS`（`rl_zoo3/utils.py:27`）→ `get_wrapper_class`（`rl_zoo3/utils.py:49`）→ `create_test_env`（`rl_zoo3/utils.py:203`）→ `get_model_path`（`rl_zoo3/utils.py:471`）。
- **env_wrapper 三种写法**实测参考：纯字符串（`hyperparams/dqn.yml:7-8` 的 `AtariWrapper`）、带 kwargs 的单键 dict（`hyperparams/tqc.yml:258-260` 的 `FrameSkip: skip: 2`）、`vec_env_wrapper` 等价形式（`hyperparams/a2c.yml:9-12` 注释）。
- **改动连锁**：给 YAML 加新键必须想清「谁消费、谁 del」；漏 del 会在模型构造器处炸 TypeError，报错位置离 YAML 很远。
- **安全红线**：enjoy 别人的模型 = 执行别人的配置——UnsafeLoader（`rl_zoo3/utils.py:429`）与 eval（`rl_zoo3/utils.py:438`）都是代码执行面，只跑可信来源的 zip。
- **坑**：`VecNormalize.load` 找不到 `vecnormalize.pkl` 直接 ValueError（`rl_zoo3/utils.py:287`）；frame stacking 读的键名是 `frame_stack` 不是 `n_stack`（`rl_zoo3/utils.py:289`）。
- **版本漂移敏感**：config.yml 里存着训练时的 env id；上游环境升版（如 LunarLander v2→v3）后旧 config 指向不存在的 id，需配合 08 篇的注册机制排查。

<!-- chars(no-space): 8611, anchors: 123 -->
