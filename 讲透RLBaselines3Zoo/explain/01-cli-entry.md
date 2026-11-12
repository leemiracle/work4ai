# 01 · CLI 总入口与命令分发：train.py / enjoy.py → rl_zoo3.cli → rl_zoo3/train.py

## ① 角色定位

rl-baselines3-zoo 的用户界面几乎全是命令行：训练、回放 pretrained agent、画曲线、跑 benchmark，四件事四个 CLI。这一层回答的问题是——用户敲下的一行命令如何变成一次 SB3 训练/推理。三层结构：

1. **仓根壳脚本**：`train.py` / `enjoy.py` 各 4 行（`rl_zoo3/train.py:1-4`），import 后在 `__main__` 守卫里调用——git clone 后不 pip install 也能直接跑。
2. **pip console script 分发器**：`rl_zoo3/cli.py` 的 `main()`。`pyproject.toml:86-87` 注册 `rl_zoo3 = "rl_zoo3.cli:main"`，安装后即有 `rl_zoo3 train / enjoy / plot_train / plot_from_file / all_plots` 子命令；`README.md:48` 明说 `rl_zoo3 train` 等价 `python train.py`。
3. **实现函数本体**：`rl_zoo3/train.py::train()`、`rl_zoo3/enjoy.py::enjoy()`、`rl_zoo3/plots/` 三函数，同时可被壳 import、被 cli 分发、`python -m rl_zoo3.train` 直跑（`rl_zoo3/train.py:291-292` 自带 `__main__`）——一份代码三种入口。

注意 `benchmark` 不在 cli.py 分发表里，它是 `python -m rl_zoo3.benchmark` 的模块级脚本（见⑤）。

## ② 内部结构

**根壳**：`rl_zoo3/train.py:1` import、`rl_zoo3/train.py:4` 调用；`rl_zoo3/enjoy.py:1` / `rl_zoo3/enjoy.py:4` 同构。无参数处理。

**cli.py::main()**：`rl_zoo3/cli.py:8` 定义；`rl_zoo3/cli.py:9` 取 `sys.argv[1]` 当子命令名，`rl_zoo3/cli.py:11` `del sys.argv[1]` 原地删除；`rl_zoo3/cli.py:13-19` 的 `known_scripts` 字典映射五个名字到函数；`rl_zoo3/cli.py:20-22` 未知名字抛 `ValueError`，否则裸调。全文 27 行，无 argparse。

**rl_zoo3/train.py::train()**（292 行，CLI 层最重），七段：

- **argparse**（`rl_zoo3/train.py:22-167`，约 45 个参数）：`--algo` choices 来自 `ALGOS.keys()`（`rl_zoo3/train.py:23`）、`-n` 默认 -1 沿用 yaml 值（`rl_zoo3/train.py:34`）、`-f` 默认 logs（`rl_zoo3/train.py:61`）、`-i` 断续训练（`rl_zoo3/train.py:26`）、`-optimize` 超参搜索（`rl_zoo3/train.py:79-81`）、`-params` 用 `StoreDict` 收 dict（`rl_zoo3/train.py:131-138`）；`rl_zoo3/train.py:168` 才 `parse_args()`。
- **环境注册与纠错**：`rl_zoo3/train.py:171-172` 把 `--gym-packages` 逐个 import（触发注册副作用）；`rl_zoo3/train.py:174-183` 查 registry，未命中用 `difflib.get_close_matches` 报「你是不是想打 XXX」（`rl_zoo3/train.py:180`）。
- **种子/线程/校验**：`rl_zoo3/train.py:187-191` 当 `--seed<0` 随机采种并 `set_random_seed`；`rl_zoo3/train.py:194-197` 设 `th.set_num_threads`；`rl_zoo3/train.py:199-202` 断言 `-i` 是存在的 `.zip`。
- **wandb**（`rl_zoo3/train.py:207-231`）：`--track` 时完整命令存 `args.command`（`rl_zoo3/train.py:216`，`sys.orig_argv`），`sync_tensorboard=True` 复用 SB3 日志（`rl_zoo3/train.py:227`）。
- **构造 ExperimentManager**（`rl_zoo3/train.py:233-271`）后**三分支收尾**（`rl_zoo3/train.py:274-288`）：`setup_experiment()` 非 None → `learn()`+`save_trained_model()`；None（优化模式）→ `hyperparameters_optimization()`。

**rl_zoo3/enjoy.py::enjoy()**（296 行）：参数段 `rl_zoo3/enjoy.py:22-76`（`--folder` 默认 `rl-trained-agents` 而非 logs，`rl_zoo3/enjoy.py:23`；`--exp-id` 0=最新/-1=无实验目录，`rl_zoo3/enjoy.py:28`）。`rl_zoo3/enjoy.py:87-95` 调 `get_model_path` 定位模型，失败且 folder 含 `rl-trained-agents` 则自动从 HF hub 下载重试（`rl_zoo3/enjoy.py:99-122`）。`rl_zoo3/enjoy.py:127` 硬编码 off-policy 名单，用于 hack `buffer_size=1`（`rl_zoo3/enjoy.py:177-184`）。`rl_zoo3/enjoy.py:139-160` 读回 `config.yml`+`args.yml` 重建 env_kwargs；`rl_zoo3/enjoy.py:164-174` `create_test_env`；`rl_zoo3/enjoy.py:176-204` 组 `custom_objects`（schedule 压 0）后 `ALGOS[algo].load`；`rl_zoo3/enjoy.py:213-241` 推理循环 predict/step/render（Atari/Minigrid 默认随机策略，`rl_zoo3/enjoy.py:216`）；`rl_zoo3/enjoy.py:282-292` 汇总输出并 close。

**rl_zoo3/benchmark.py**（206 行模块级脚本）：`rl_zoo3/benchmark.py:16-27` 在模块顶层建 parser 并 parse——import 即执行，无 main()；`rl_zoo3/benchmark.py:29-32` 合并本地与 hub 的模型清单。

**plots 三件套**：`rl_zoo3/plots/plot_train.py:18` 读 Monitor csv 画训练曲线；`rl_zoo3/plots/all_plots.py:13` 聚合多算法 `evaluations.npz`；`rl_zoo3/plots/plot_from_file.py:40` 读 all_plots 的 pickle 再加工。

## ③ 外部连接

**imports 进来**：`rl_zoo3/train.py:16` `import rl_zoo3.import_envs`（注册自定义环境）；`rl_zoo3/train.py:17-18` 引 `ExperimentManager`、`ALGOS`/`StoreDict`；`rl_zoo3/train.py:13` 用 SB3 `set_random_seed`。`rl_zoo3/cli.py:3-5` import 五个入口函数。`rl_zoo3/enjoy.py:13-17` 引包级导出（`rl_zoo3/__init__.py:8-16`）、`ExperimentManager`（只用静态方法 `is_atari`，`rl_zoo3/enjoy.py:136-137`）、`download_from_hub`。

**被谁调用**：① pip console script（`pyproject.toml:86-87`）；② 仓根壳；③ 测试——`tests/test_train.py:31` 用 `subprocess.call("python train.py ...")` 黑盒整进程跑；④ benchmark 是 enjoy 的旁路调用者：`rl_zoo3/benchmark.py:102` `subprocess.call(["python","enjoy.py",...])`，靠 `--reward-log` 让 enjoy 落 Monitor 日志再读回。

**calls 出去**：train() → `ExperimentManager`（02 篇）、`wandb.init`；enjoy() → `get_model_path`/`create_test_env`/`get_saved_hyperparams`（`rl_zoo3/utils.py`）、`ALGOS[algo].load`；两者都消费 `ALGOS` 字典（`rl_zoo3/utils.py:27-41`，SB3 六算法+sb3-contrib 五算法）。

## ④ 数据流

**训练链**：`python train.py --algo ppo --env CartPole-v1 -n 200` → `train()` → args → 校验 env 注册 → 定种子 →（可选 wandb）→ 构造 `ExperimentManager`（尚未碰 yaml）→ `setup_experiment()` 读 `hyperparams/ppo.yml` 的 `CartPole-v1:` 节（`hyperparams/ppo.yml:37`）→ `learn(200)` → `save_trained_model()`。等价形态：`rl_zoo3 train ...` 或 `python -m rl_zoo3.train ...`。

**推理链**：`python enjoy.py --algo ppo --env CartPole-v1` → `get_model_path(0,...)` 解析 `rl-trained-agents/ppo/CartPole-v1_1/CartPole-v1.zip`（缺则 hub 下载）→ 读 `config.yml`+`args.yml` 复原 normalize/wrapper → `create_test_env` → `PPO.load` → 1000 步 predict/step → 打印 mean reward。

**benchmark 链**：`python -m rl_zoo3.benchmark` → 枚举全部模型 → 逐个 subprocess 调 `enjoy.py --reward-log ...` → `ts2xy(load_results(...))` 聚合（`rl_zoo3/benchmark.py:106`）→ pytablewriter 出 Markdown 表 → `rl_zoo3/benchmark.py:200-201` 拷回仓根 `benchmark.md`。

## ⑤ 设计决策

- **保留 4 行根壳**：CI、tests（`tests/test_train.py:31`）、benchmark 子进程（`rl_zoo3/benchmark.py:102`）都以 `python train.py/enjoy.py` 为契约路径，删壳连断三处；同时是零安装入口。
- **cli.py 手写分发而不用 argparse subparsers**：五子命令参数集差异极大（train 约 45 个 vs plot_train 10 个），且历史各自独立。`del sys.argv[1]`（`rl_zoo3/cli.py:11`）后各函数自建 parser，保持「函数即脚本」，三种入口复用同一函数。代价是 `rl_zoo3` 总入口没有统一 `--help`。
- **benchmark 不进 known_scripts**：它是编排器而非原子命令——自己拼参数再子进程调 enjoy.py，且 `rl_zoo3/benchmark.py:16-27` parser 写在模块顶层（import 即执行），与「函数内建 parser」的约定不兼容，故文档固定 `python -m rl_zoo3.benchmark`（`README.md:114`）。
- **StoreDict（`rl_zoo3/utils.py:449-468`）**：自定义 argparse Action，把 `-params learning_rate:0.01` 解析成 dict，值直接 `eval`——省事但有安全代价（见⑥）。
- **train 与 enjoy 的 `-f` 语义故意不同**：前者「写哪」（logs），后者「读哪」（rl-trained-agents），对应产出物与资产库两个方向。

## ⑥ 新人提示

- **读码顺序**：根壳 → `rl_zoo3/train.py::train()` 只看 274-288 行主干 → 跳 `rl_zoo3/exp_manager.py`（02 篇）。enjoy 推理循环在 `rl_zoo3/enjoy.py:234-277`，Atari 分支多，第一遍可跳。
- **加一个 CLI 参数的连锁反应**：`rl_zoo3/train.py:22-167` 加定义 → `rl_zoo3/train.py:233-271` 手工透传 → `rl_zoo3/exp_manager.py:75-114` 构造器加形参 → `_save_config` 自动记进 args.yml（`rl_zoo3/exp_manager.py:319-321`）。漏中段即静默失效。
- **坑一**：`rl_zoo3/cli.py:11` 的 `del sys.argv[1]` 原地改全局 argv，分发前缓存 argv 的代码会拿错参数。
- **坑二**：`-params`/`--env-kwargs` 的值会被 `eval`（`rl_zoo3/utils.py:467`），别接不可信输入。
- **坑三**：`--seed` 默认 -1=每次随机（`rl_zoo3/train.py:187-189`），复现必须显式传；enjoy 默认 deterministic，但 Atari/Minigrid 反转（`rl_zoo3/enjoy.py:216`）。
- **坑四**：off-policy 在 enjoy 被强塞 `buffer_size=1`（`rl_zoo3/enjoy.py:177-184`），别拿 enjoy 做需要回放缓冲的实验。

<!-- chars(no-space): 5657, anchors: 68 -->
