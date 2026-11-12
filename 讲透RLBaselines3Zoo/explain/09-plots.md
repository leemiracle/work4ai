# 09 · rl_zoo3/plots/——训练曲线可视化子系统

## ① 角色定位

`rl_zoo3/plots/` 是 zoo 的离线可视化子系统：不参与训练，只消费训练链路落盘的两类日志出图——**Monitor.csv**（逐 episode 流水，每完结一局写一行 `r,l,t`）与 **evaluations.npz**（`EvalCallback` 周期评估快照）。四文件分工：`plot_train.py`（95 行）读 Monitor.csv 画单次训练滚动均值曲线；`all_plots.py`（249 行）扫多实验目录的 evaluations.npz 做跨 trial 聚合并 pickle 化；`plot_from_file.py`（428 行）读 pkl 出学习曲线/barplot/boxplot/可选 rliable 图；`score_normalization.py`（113 行）供归一化参考分。三件套均为 CLI 函数，经 `rl_zoo3/plots/__init__.py:1-8` 导出、cli.py:16-18 注册，故 `rl_zoo3 plot_train / all_plots / plot_from_file` 可用（`benchmark` 不在此表，见 10 篇）。依赖走 `pyproject.toml:51` 的 `plots` extra。

## ② 内部结构

**plot_train.py**——最短。`seaborn.set()`（plot_train.py:15）后 `def plot_train()`（plot_train.py:18）。`-a/-e/-f` 三必填（plot_train.py:20-22）；x 轴 `steps/episodes/time` 映射 SB3 常量 `X_TIMESTEPS/X_EPISODES/X_WALLTIME`（plot_train.py:26、36-40）；y 轴 `success/reward/length` 映射 **Monitor.csv 列名** `is_success/r/l`（plot_train.py:47-51）——与监控格式最直接的耦合点。目录发现按 mtime 排序 + env 子串过滤（plot_train.py:62-63）；加载调 SB3 `load_results`，无文件时 `LoadMonitorResultsError` 被 continue 吞掉（plot_train.py:71-73）。`--max-timesteps` 用 `data_frame.l.cumsum()` 过滤（plot_train.py:75），与 ts2xy 横轴算法一致；`window_func(x, y, window, np.mean)` 滚动均值（plot_train.py:86），序列短于窗口不画（plot_train.py:84）。

**all_plots.py**——跨 trial 聚合器（all_plots.py:13）。`-k/--key` 指定取 evaluations.npz 哪个键，默认 `results`（all_plots.py:20-26）；`--max-timesteps` 默认 `int(2e6)` 截断（all_plots.py:27）；`-min` 丢弃短 trial（all_plots.py:28）。循环 env × algo × exp_folder（all_plots.py:52-63），目录约定 `exp_folder/algo.lower()`（all_plots.py:64），trial 子目录靠 env 子串匹配（all_plots.py:74），每个 `np.load(.../evaluations.npz)`（all_plots.py:83）。聚合五步：①按最长 trial 定 `max_len` 并截断（all_plots.py:102-104）；②对 eval 频率不一致的 trial 用 scipy `distance_matrix` 最近邻下采样对齐（all_plots.py:136-137，动机注释见 all_plots.py:111-113）；③剔除不完整 run（all_plots.py:144-150）；④`reshape((n_trials, n_eval, -1))` + `swapaxes` 到 `(n_eval, n_trials, n_eval_episodes)`（all_plots.py:163-165），双轴均值得 `mean_`（all_plots.py:167），trial 间标准差除 `sqrt(n_trials)` 得 standard error（all_plots.py:171-173）；⑤成绩取末次评估 `last_evals`（all_plots.py:176），格式化 `"mean +/- stderr"`（all_plots.py:187，`-median` 则 all_plots.py:183）。后处理字典六键（all_plots.py:194-201），曲线 `plt.plot` + `fill_between` 置信带（all_plots.py:203-204）。表格 `pytablewriter.MarkdownTableWriter`（all_plots.py:209），缺项填 `"0.0 +/- 0.0"`（all_plots.py:232）；表也入 pkl（all_plots.py:237），最终 `pickle.dump` 到 `<output>.pkl`（all_plots.py:239-242）。

**plot_from_file.py**——出图端（plot_from_file.py:40）。rliable **可选**，import 失败置 `rly = None`（plot_from_file.py:12-16）。unpickle（plot_from_file.py:79-80）后先打印内嵌表（plot_from_file.py:83-87）；`--merge` 并入其他 pkl 同 env 新 key（plot_from_file.py:91-99）；skip/keep keys/envs 切片（plot_from_file.py:101-108）。三路出图：每 env 学习曲线（plot_from_file.py:115-144）；`last_evals` 摊平成 pandas 长表（plot_from_file.py:207）供 `seaborn.barplot`（plot_from_file.py:351）；`-b` 箱线图 + `restyle_boxplot` 上色（plot_from_file.py:22-37、414-420）。rliable 线（`-r`）先归一化：硬编码 `env_key_to_env_id` 映射回 env_id（plot_from_file.py:154-161），调 `normalize_score`（plot_from_file.py:190）；四指标 bootstrap 置信区间 `rly.get_interval_estimates`，reps 从 50000 降到 2000（plot_from_file.py:221-235）；`-vs` probability of improvement（`itertools.combinations` 两两，plot_from_file.py:279-283）；`-iqm` 样本效率曲线按 `downsample_factor = 4` 抽稀（plot_from_file.py:306-308）。

**score_normalization.py**——`ReferenceScore` NamedTuple（score_normalization.py:13-16）+ 六环境参考分表（score_normalization.py:19-27），`normalize_score` 线性缩放 `(score-min)/(max-min)`（score_normalization.py:41-52）；min=随机策略、max=可接受性能（score_normalization.py:2-5）。

## ③ 外部连接

- **imports**：SB3 的 `load_results, LoadMonitorResultsError` 与 `X_EPISODES, X_TIMESTEPS, X_WALLTIME, ts2xy, window_func`（plot_train.py:11-12）；scipy `distance_matrix`（all_plots.py:10）；rliable（plot_from_file.py:12-16）；包内 `normalize_score`（plot_from_file.py:18）。
- **被谁调用**：cli.py:3+16-18 注册三子命令；pyproject.toml:90 将 `rl_zoo3.plots` 列为安装包。
- **数据生产者**：训练时 `create_envs` 把 `monitor_dir=self.save_path` 传 `make_vec_env`（exp_manager.py:699-709），eval env 不落盘（exp_manager.py:679）；robotics/parking 注入 `info_keywords=("is_success",)`（exp_manager.py:681-685）。evaluations.npz 由 `EvalCallback(log_path=self.save_path)` 产出（exp_manager.py:593-601），SB3 以 `timesteps/results/ep_lengths[,successes]` 键 `np.savez`——即 `-k` 的键空间。

## ④ 数据流

- **单次训练体检**：`rl_zoo3 plot_train -a ppo -e CartPole-v1 -f logs/ppo/` → mtime 排序找 run 目录（plot_train.py:62-63）→ `load_results` 拼全部 `*monitor.csv` → `ts2xy` 用 `np.cumsum(l)` 造横轴（plot_train.py:81）→ 滚动均值出图。Monitor.csv 物理格式实证于 `logs/benchmark/a2c-Acrobot-v1/0.monitor.csv`：首行 `#{"t_start": ..., "env_id": ...}` JSON header，次行 `r,l,t[,is_success]`。
- **论文级聚合（两级）**：第一级 `rl_zoo3 all_plots -a ppo sac -e HalfCheetah -f logs/ -o hc` 把 N 个 trial 压成 `hc.pkl`（每 env × 每 algo-label 一个六键字典 + results_table）；第二级 `rl_zoo3 plot_from_file -i hc.pkl -b -r --merge other.pkl` 反复切片出图。pkl 是两级唯一接口。

## ⑤ 设计决策

- **两级管线**：聚合（尤其 bootstrap）昂贵，pkl 落盘后可零成本换 keep/skip/merge/标签重画——数据加工与呈现解耦。
- **与 SB3 分工**：不重写 Monitor 解析，复用 `load_results/ts2xy/window_func`，格式契约留在 SB3；zoo 只叠加批量聚合、异频下采样、rliable 统计。
- **最近邻下采样**（all_plots.py:136-137）：不同 run 的 `eval_freq` 不齐，直接 stack 会崩，按 timestep 距离对齐是最小侵入解。
- **rliable 可选**：仅 `-r` 时才 raise ImportError（plot_from_file.py:211-214），不拖累基础安装。
- **参考分硬编码**（score_normalization.py:19-27）：参考分是人工判断；新环境须手工补 `env_key_to_env_id` 与 reference_scores 两处，漏了 warn（plot_from_file.py:193-194）。
- **遗留瑕疵**：`results[env]` 初始化用 `label-algo` key（all_plots.py:69），写表/查询用 `algo-label`（all_plots.py:183/231）——初始化条目是无读者的死数据。

## ⑥ 新人提示

- **读码入口**：plot_train.py 全文建 Monitor.csv 直觉，再啃 all_plots.py:81-150 聚合核心。
- **坑：`-y success` 无数据**。`is_success` 列只有训练时带 `info_keywords` 的环境才有（exp_manager.py:681-685）；普通环境 KeyError 只打印 `No data available`（plot_train.py:76-80）。
- **坑：reshape 假设**"每次评估 episode 数恒定"（all_plots.py:163），不齐 trial 靠截断逻辑清理（all_plots.py:144-150），改这段须维持该不变量。
- **坑：labels 严格配对**，`zip(..., strict=True)` 多一个少一个直接 ValueError（plot_from_file.py:112）。
- **坑：matplotlib 全局状态机**，三文件皆 `seaborn.set()` + `plt.figure()` 脚本风格（plot_train.py:15、all_plots.py:43），同进程重复调用窗口累积。
- **连锁反应**：改 evaluations.npz 键名会静默破坏 `-k` 默认值；改 monitor_kwargs 默认集影响可画 y 轴集合。
- benchmark.md 结果表不是本子系统产物——由 benchmark.py 独立生成（10 篇），两者只共享 Monitor.csv 地基。

<!-- chars(no-space): 5723, anchors: 82 -->
