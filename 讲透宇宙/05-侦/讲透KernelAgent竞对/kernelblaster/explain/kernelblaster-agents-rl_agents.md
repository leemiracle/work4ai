# 深解 rl_agents.py × opt_ncu_minimal.py：RL 组件层与最小对照基线

> 图谱定位：两者同属 `layer:agent-core`（Agent 核心层），对应 tour 第 8/10 站。邻接：`opt_ncu_rl.py`（RL 主循环）、`feedback.py`（迭代基座）、`database.py`（知识库）。

## ① 角色定位：策略层 vs 循环层 vs 对照基线

三个文件是一条流水线的三种角色，不要混着读：

- **`opt_ncu_rl.py` = 循环层（rollout 引擎）**：`RLNCUAgent` 跑并发探索——每步由知识库分析状态、生成排序优化计划、按 relevance 加权随机选技术、LLM 生成代码并 NCU 剖析、算 reward，把整条轨迹喂进 ReplayBuffer。
- **`rl_agents.py` = 策略层（学习组件库）**：它自己**不跑任何循环**，提供四类零件——`TrajectoryStep`/`Trajectory` 数据模型、定长 `ReplayBuffer`（含统计）、三个 LLM 反思 agent（策略评估→差距归因→参数更新），以及 `_apply_database_updates` 这个全仓唯一的写库执行器。opt_ncu_rl 在 `__init__` 里实例化全部零件，每条 rollout 结束后 `add_trajectory` 入 buffer。
- **`opt_ncu_minimal.py` = 对照基线（ablation 臂）**：`MinimalOptimizationAgent` 继承同一个 `FeedbackAgent`，import opt_ncu_rl 的 `parse_ncu_metrics`/`generate_strategy_guided_prompt`（提示词共享），然后**砍掉整个决策与学习回路**：无状态匹配、无策略选择采样、无 reward、无 Trajectory/ReplayBuffer、无反思链。它保留 FeedbackAgent 的外层迭代/回滚与修复预算（`MAX_FIX_RETRIES/BUDGET/PER_ITERATION = 4/4/4`，trajectory 级共享预算+每迭代上限），直接"代码+profile+知识库前 6000 字→LLM→剖析→下一轮"。产物命名刻意对齐 RL 版（`trajectory_N_uid/`、`rl_iter_X_best.cu`、`success_rl_optimization.cu`），下游评测脚本可无感知替换——这是为了干净地隔离"RL 决策回路到底贡献多少增益"。全仓无其他调用点，是独立实验入口。

## ② 内部结构

**rl_agents.py（498 行）**：
- 数据模型：`TrajectoryStep`（state/action/code/cycles/predicted/actual/reward 七元组）、`Trajectory`（累加 total_reward、记录首末 cycles）。
- `ReplayBuffer`：max 1000 的 FIFO，`get_recent_trajectories(n)` 取窗口，`get_statistics()` 出 avg/std/max/min reward、平均改进百分比、success_rate。
- 三个反思 agent（各只暴露一个 async 方法，全部走 `generate_code_retry`）：
  1. `PolicyEvaluationAgent.evaluate_policy(buffer, db)`：最近 10 条轨迹逐步数据+buffer 统计+库统计→文本分析（预测准确度趋势、技术 over/under-perform）。
  2. `PerfGapAnalysisAgent.analyze_performance_gaps(评估文本, 失败steps)`：gap=predicted−actual，输出根因/系统性偏差/修正建议。
  3. `ParameterUpdateAgent.update_parameters(归因文本, db)`：另扫一遍库里 `actual < 0.5×predicted` 的劣者，要求 LLM 输出六类结构化 JSON：复合优化/单技术调预测值、置信度更新、新策略、参数微调变体、**发现新状态**、淘汰劣者；`_apply_database_updates` 落地（deprecated=置信度压到 0.1 的软淘汰，不删条目）。

**opt_ncu_minimal.py（1166 行）**：`ProfilingData`（可外接 reprofile 结果）、`SYSTEM_PROMPT`、三个 MAX_FIX 常量、`MinimalOptimizationAgent`（initialize 打包首 prompt → run() 并发 `run_single_trajectory`×num_pgen → `__run` 落盘 prompt/调 LLM → `get_feedback` 编译运行+fix 循环+剖析 → 成功判定=best_cycles<initial_cycles）。`gather_perf_metrics` 一次剖析全部 kernel、`_extract_speed_of_light_section` 只留 SOL 表控制上下文长度。

## ③ 外部连接

- rl_agents ← imports：`database.py`（OptimizationEntry/CompositeOptimization）、`utils`（generate_code_retry）、`config`。被 `opt_ncu_rl.py` 与 `agents/__init__.py` 导入。
- minimal ← imports：`feedback.py`、`database.py`（含 LLMInterface）、`opt_ncu_rl.py`（两函数）、utils 全家桶（编译运行/NCU 解析）。被 `graph/nodes/optimization_rl_ncu.py` 引用的是 RL 版，minimal 无图节点消费。

## ④ 数据流：真 RL 还是 in-context 学习？

**都不是，准确说是"以数据库为策略参数表的 LLM 文本化策略迭代"**：

- 单步决策：状态→库检索→LLM 排序 plan→`relevance_score³` 加权随机采样（≈Boltzmann 式探索；`KERNELAGENT_DB_FALLBACK_TOP1=1` 切确定性 top-1）→代码→实测 cycles→`reward = actual_improvement/100 + accuracy_bonus(预测准 ±0.2/偏差 −0.1|acc−1|) − 0.5 变慢惩罚`。
- 学习回路：**replay buffer 里的成功/失败轨迹不进决策 prompt**（所以不是 in-context 学习），而是走三级反思：评估→归因→JSON 更新**写回数据库字段**（predicted_improvement/confidence/新策略/新状态）——"参数更新"=改表，下一轮决策自然变好。这更像 bandit 价值表更新 + LLM 当优化器的混合，无梯度。
- **关键发现（读码钉死）**：`policy_update_cycle`（opt_ncu_rl.py:1458）在**全仓无任何调用点**——三级反思链当前是休眠/未接线能力，默认跑批时学习不发生，跨任务记忆只剩 database.md 静态内容。要做"学习"实验需自己调度它。
- 反观 minimal：学习只发生在单条 trajectory 内——失败/不提速的 profile 连同代码打进下一轮 user prompt，是纯 in-context 迭代；知识注入是静态 6000 字截断，永不写回。

## ⑤ 设计决策

1. **对照实验公平性优先**：minimal 与 RL 共享 harness、修复预算、产物契约，差异只剩"决策+学习"一个变量——典型的 ablation 设计。
2. **软淘汰而非删除**：deprecated 压 confidence 到 0.1，保留审计轨迹。
3. **修复预算三常量分层**（重试/总预算/每迭代上限）防止 fix 循环吞掉整个 trajectory 资源。
4. **窗口化反思**（10 条轨迹/5 条失败）控制 LLM 上下文成本；SOL 表裁剪同理。
5. 瑕疵：三个反思 agent 的 `system_prompt` 定义了却从未注入 messages（调用只发 user 角色）；minimal 的 cycles 用"全 kernel 求和"，与 RL 版口径需对齐再比较。

## ⑥ 新人提示

读码顺序：`feedback.py` → `opt_ncu_rl.py` → `rl_agents.py` → `opt_ncu_minimal.py`。记住三句话：**循环在 rl，策略零件在 rl_agents，minimal 是删掉决策的照妖镜**；reward 是启发式分数不是环境真值；想观察"学习"必须手动触发休眠的 `policy_update_cycle`。并发轨迹计数有 `asyncio.Lock`，改 rollout 逻辑时别破坏。
