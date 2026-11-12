# 08 · common.py：默认包装链五件套与动作粘滞

## 一、角色定位

`gymnasium/wrappers/common.py` 是用户最先撞见的 wrapper 文件——不是因为大家爱读它，而是因为 `gym.make()` 出厂的每个标量环境都自动穿着它的三件套。模块 docstring（common.py:L1-8）与 `__all__`（common.py:L34-40）列出五个类：`TimeLimit`（步数上限截断）、`Autoreset`（终止自动重置）、`PassiveEnvChecker`（被动 API 校验）、`OrderEnforcing`（调用顺序强制）、`RecordEpisodeStatistics`（回合统计）。前三个由 `make` 默认挂载（Autoreset 除外，需手动），后两个一个保调试体验、一个保训练遥测。

它回答的核心问题是：**哪些职责不属于环境本身，而属于"环境的外壳"**。04 篇已实证这个边界——CartPoleEnv 的 `step` 返回 `truncated` 恒为 False（cartpole.py:L226-227），因为时间预算是外管职责，由 `TimeLimit` 接手；而 vector 版 CartPoleVectorEnv 绕过 make 包装链，必须自管 truncated（cartpole.py:L474-476）。本篇把这条边界翻到 wrapper 侧看：`TimeLimit` 如何计数、`OrderEnforcing` 如何拦截、`PassiveEnvChecker` 如何只看不改。兼及 stateful_action.py 的 `StickyAction`/`RepeatAction` 两个动作侧近亲，stateful_observation.py 已由 07 篇详解，本篇只交代其与本文件的耦合点。

## 二、内部结构

**TimeLimit**（common.py:L43-171）。状态极简：`_max_episode_steps` 与 `_elapsed_steps`（构造时置 None，common.py:L114-115）。构造器做双重校验——非 int 抛 TypeError、非正数抛 ValueError（common.py:L101-108）。核心逻辑在 `step`（common.py:L117-136）：先透传底层五元组，`_elapsed_steps += 1`，再判 `>= _max_episode_steps` 就把 truncated 置 True（common.py:L131-134）。`reset` 只做一件事：步数归零（common.py:L150）。`spec` property（common.py:L153-171）是隐藏的复杂点——deepcopy 底层 spec 后改写 `max_episode_steps`，让 `env.spec` 与实际行为一致（`gym.make("CartPole-v1", max_episode_steps=3)` 后 `spec.max_episode_steps==3`，见 doctest common.py:L64-66），并缓存到 `_cached_spec`（基类机制，core.py:L336/L374-406）。

**Autoreset**（common.py:L174-222）。单布尔状态 `self.autoreset`（common.py:L195），构成一个两态状态机。`step`（common.py:L204-222）分两路：若上一步已终止/截断（autoreset=True），本步的 action 被丢弃，直接 `env.reset()` 并返回 `(obs, 0.0, False, False, info)`（common.py:L215-217）——注意此分支不透传 action，agent 这一帧的决策被无声吞掉；否则正常 step。每次结束时用 `terminated or truncated` 回写标志（common.py:L221）。`reset` 显式清标志（common.py:L201），保证用户主动重置后状态机回到干净起点。

**PassiveEnvChecker**（common.py:L225-368）。构造期做两类检查：gym/gymnasium 血统甄别（老 gym 环境类会得到带迁移文档链接的 TypeError，common.py:L253-263）与 action/observation space 的存在性及合法性（common.py:L265-275）。运行期是"一次性体检"模式：四个布尔 `checked_reset/checked_step/checked_render/close_called`（common.py:L277-280）保证每类调用只在**首次**走全量校验函数（来自 utils/passive_env_checker.py 的 `env_reset_passive_checker` L250 / `env_step_passive_checker` L293 / `env_render_passive_checker` L405），之后直通底层。额外的 `checked_data_reuse` 与 `_previous_data`（common.py:L282-285）串起三次采样点：首次 reset 的 (obs, info) ↔ 首次 step ↔ 第二次 step，两两做对象共享比较（common.py:L296-311）。

**OrderEnforcing**（common.py:L371-465）。状态只有 `_has_reset` 布尔（common.py:L417）。`step` 在标志为 False 时抛 `ResetNeeded`（common.py:L422-423），`reset` 置 True（common.py:L430）。`render` 单独有 `disable_render_order_enforcing` 开关（common.py:L404/L435）——默认也要求先 reset，报错文案直接教学解法（common.py:L436-439）。`has_reset` 只读 property（common.py:L442-445）供外部探询。

**RecordEpisodeStatistics**（common.py:L468-583）。两套状态：标量累计器 `episode_returns/episode_lengths/episode_start_time/episode_count`（common.py:L533-536）与三个 `deque(maxlen=buffer_length)` 滚动窗口 `return_queue/length_queue/time_queue`（默认 100，common.py:L538-540）。`step`（common.py:L542-570）累加 reward、步数加一；一旦 terminated 或 truncated，先 `assert self._stats_key not in info` 防键冲突（common.py:L552），再把 `{"r": 累计回报, "l": 回合长度, "t": 耗时}` 写进 `info[stats_key]`（common.py:L557-561，耗时用 `time.perf_counter()` 差值 round 到 6 位），三队各 append 一项后重新起表（common.py:L563-568）。`stats_key` 可自定义（common.py:L517）。

**动作侧近亲**（stateful_action.py）。`StickyAction`（L16-142）是 ActionWrapper，重写 `action()`（L118-142）而非 `step`：以概率 `repeat_action_probability`（校验区间 [0,1) 左闭右开，L62-65）丢弃 agent 本步动作、沿用 `last_action`；v1.1.0 新增 `repeat_action_duration` 支持 int 或 (min,max) tuple（归一化存 `repeat_action_duration_range`，L70-90），一旦"粘住"会连续执行随机采样时长的旧动作，直到 `repeats_taken == num_repeats` 解粘（L126-139）。`RepeatAction`（L145-220）是普通 Wrapper，`step` 里 for 循环把同一动作执行 `num_repeats` 次、reward 求和、遇 terminated/truncated 提前 break（L215-220）。

## 三、外部连接

**与 registration.py 的挂载契约**：`make` 在实例化裸环境后按固定顺序包装——先 `PassiveEnvChecker`（registration.py:L805，最内层，除非 `disable_env_checker`），再 `OrderEnforcing`（L809，若 spec.order_enforce），最后 `TimeLimit`（L814/L816，若 max_episode_steps 非空，make 参数可覆盖 spec 值）。docstring 里的栈打印 `<TimeLimit<OrderEnforcing<PassiveEnvChecker<CartPoleEnv>>>>>`（common.py:L60-61）正是这一顺序的快照；03 篇从注册侧讲过 spec 的三个开关字段（registration.py:L587-590），本篇是其执行侧。

**与 vector 体系的语义对齐**：scalar `Autoreset` 的 docstring 明言"follows the vector autoreset api"（common.py:L179）。三态枚举 `AutoresetMode` 定义在 vector_env.py:L41-46：`NEXT_STEP`（终止后的下一步做 reset，scalar Autoreset 与 SyncVectorEnv 默认实现的就是它）、`SAME_STEP`（终止当步就地重置，v0.x 老语义）、`DISABLED`（传统手动 reset）。v1.0.0 的 breaking change（common.py:L183）正是把 Autoreset 从 SameStep 改为 NextStep 并删掉 `final_observation`/`final_info`——终止步的最终观测现在直接返回给用户，下一步才重置。

**与检查器工具层的分工**：PassiveEnvChecker 只是把 utils/passive_env_checker.py 的四个纯函数包成 wrapper；对照的主动版是 utils/env_checker.py 的 `check_env`（L406），它会跑完整回合做 seed 决定性检查（`check_reset_seed_determinism` L79、`check_step_determinism` L204）——有副作用、耗时，只能离线手动跑；被动版只搭便车查首步返回值。`TimeAwareObservation` 反向依赖本文件：构造时若 spec 无 `max_episode_steps`，会沿包装栈下钻找 `TimeLimit._max_episode_steps`，找不到就抛 ValueError（stateful_observation.py:L200-214）——这是 TimeLimit 深入别处实现细节的罕见正例。07 篇的 transform/stateful observation 系列与本篇共用 RecordConstructorArgs 混入（保证 wrapper 可从 spec 重建）。

## 四、数据流

以 `gym.make("CartPole-v1")` 后的一次 step 为例，调用**自外向内**穿透、返回值**自内向外改写**：

1. 用户调 `env.step(action)`，最外层 TimeLimit.step 先 `self.env.step(action)`（common.py:L130）——注意 TimeLimit 自己不拦动作，纯透传。
2. OrderEnforcing.step 检查 `_has_reset`（common.py:L422），通过则 `super().step()` 继续下钻。
3. PassiveEnvChecker.step：首步走 `env_step_passive_checker(self.env, action)`（common.py:L293），它内部调真实 `env.step` 并就地校验五元组结构、reward 可转 float、terminated/truncated 是 bool、obs 在 space 内，**原样返回数据**（passive_env_checker.py:L293-299 连 action 都刻意不查——注释说明部分环境允许越界动作）；第二步起仅剩 data-reuse 比对，第三步起零开销直通。
4. 裸环境返回 `(obs, 1.0, False, False, info)`——CartPole 的 truncated 恒 False。
5. 回程逐层加工：PassiveEnvChecker 原样上交 → OrderEnforcing 原样上交 → TimeLimit 计数加一，第 500 步时把 truncated 改写为 True（common.py:L131-134）。用户拿到的 `(obs, r, False, True, info)` 里截断信号完全诞生于 wrapper 层。

若链上有 `RecordEpisodeStatistics`（用户手动外挂），它在自己的层累加 reward 并在 done 时注入 `info["episode"]`。把它放在 Autoreset **内层**（先包）时，done 那步照常穿过统计层完成记录，随后 Autoreset 折叠出的 reset 步只触发统计层 `reset()` 的清零（common.py:L216 调的是整条内链的 reset），统计完整性不受影响；这也是官方推荐的叠放次序。时间线上，同一回合内两个"终点信号"可能同时到达：第 500 步环境恰好倒下时，terminated（来自裸环境）与 truncated（TimeLimit 改写，common.py:L133-134）同帧为 True，RecordEpisodeStatistics 对二者取或（common.py:L551）只记一次。

StickyAction 则在数据流更早的岔口工作：它实现 `action()` 钩子，ActionWrapper 基类自动在 `step` 前调用它改写动作——agent 的决策在到达裸环境前就可能被替换为上一步的动作。RepeatAction 连五元组形状都改变：一次用户 step 对应底层 `num_repeats` 次 step，reward 是多次之和（stateful_action.py:L212-217），对上层算法而言"一步"的时间尺度被拉长。

## 五、设计决策

**（1）terminated/truncated 的职责二分**。TimeLimit docstring 写得直白：环境内部若不定义截断，这里就是截断信号的唯一发出点，且它与 MDP 内生的 terminated 是两回事（common.py:L48-49）。落地为改写式实现 `truncated = True`（common.py:L134）：环境自己提前截断（如 vector CartPole）时该赋值幂等无害；学习算法据此区分"真吸收态不 bootstrap"与"截断态仍应估计后继价值"。同环境配不同上限复用成 v0/v1 两个 spec（200/500），是这套外包的直接红利；环境作者因此只需专心写对物理与终止条件，时间预算问题留给外壳统一处置。

**（2）挂载顺序为何是 checker 最内、enforcer 居中、limit 最外**。PassiveEnvChecker 最内（registration.py:L805）是因为它要体检的是**裸环境**的 API——套在别层之外查的就是包装后行为了。OrderEnforcing 在 checker 外面（L809）：用户忘 reset 就 step 时，ResetNeeded 在到达 checker 之前拦截，避免"非法调用污染首步体检样本"。TimeLimit 最外（L814）保证用户看到的步数语义即最终语义，spec 覆盖值也落在最外层。三个类各自的 `spec` property 分别回写 `disable_env_checker=False`（common.py:L346）、`order_enforce=True`（common.py:L457）、`max_episode_steps`（common.py:L163），且都 deepcopy 而非原地改——注册表里的 spec 是全局共享对象，原地改会污染后续所有 make。

**（3）检查的成本分层**。OrderEnforcing 的运行时开销是一个布尔判断（纳秒级），换来的是把"忘 reset"这类高频 bug 从"静默错误数据"变成"带教学文案的异常"（common.py:L436-439）。PassiveEnvChecker 用一次性标志把全量校验摊销到首步，稳态零成本；data-reuse 检查的存在理由在被动检查器的 docstring 里（passive_env_checker.py:L226-230）：用户会把每步数据存进 replay buffer，环境若复用内部缓冲，改一处毁全部历史。render 的顺序强制单独给开关，是因为"先看一眼画面再 reset"是合法需求（预览画面不该被迫先走一次 reset 逻辑）。`close_called` 标志（common.py:L280）把 close 也纳入体检：重复 close 本应幂等，若二次 close 底层抛异常，wrapper 先告警再原样上抛（common.py:L356-368）——错在环境，但教学信息由 wrapper 补齐。

**（4）统计的长度语义：定长滚动而非无界追加**。`episode_returns` 名字是复数、实为标量 float（common.py:L535），每步累加（L548）、done 时一次性入队；三个 `deque(maxlen=100)` 是**定长覆盖**语义——第 101 回合 append 时最旧值自动挤出，内存有界，天然适合"最近 N 个回合均值"的训练曲线。若用普通 list append 则需自管截断。`assert` 键冲突检查（L552）与可自定义 `stats_key`（L531）共同防御嵌套统计互踩。

**（5）StickyAction 与 RepeatAction 的动机分野**。StickyAction 源自 Machado et al., 2018 §5.2（stateful_action.py:L21）的 Atari sticky actions：以概率 p 重复**上一步**动作，把确定性游戏变成真 MDP，抑制策略对确定性转移的过拟合——步数不减少，只注入转移噪声。RepeatAction 则**确定性地**重复**当前**动作 n 次并求和奖励（docstring 对比 stateful_action.py:L155-159）：降低决策频率、放大单步语义，遇终止提前止损。一个是"环境噪声化"，一个是"动作时间尺度粗粒化"，名字相近而目标相反。

## 六、新人提示

- 手动包装时**顺序即语义**：`TimeLimit(Autoreset(env))` 与 `Autoreset(TimeLimit(env))` 行为不同——autoreset 折叠掉的那步 reset 若发生在 TimeLimit 计数层之外，`_elapsed_steps` 的归零路径也随之不同。默认心智模型：越"业务"的 wrapper（统计、autoreset）越靠外，越"协议"的（checker、enforcer、limit）越靠内。
- `env.spec.max_episode_steps` 是被 TimeLimit property 改写过的副本，别拿它反推注册表原始值；要原始值用 `gym.spec("CartPole-v1")` 查 registry。
- PassiveEnvChecker 的警告只在**首次**调用时发：如果首步日志丢了告警，别以为环境后来才坏——是检查器只看了一眼。做 CI 用主动版 `check_env`（utils/env_checker.py:L406），做日常训练留着被动版即可。
- `info["episode"]` 只在 done 那步出现，训练循环要在每步 step 后检查该键而非假定常驻；且键名可能被 `stats_key` 参数改掉。
- Autoreset 语义是 NextStep：done 步的最终观测**当步返回、只有一次**，下一步 action 被丢弃。需要保存最终观测的算法要在收到 done 的那一步立即处理，v0.x 的 `final_observation` 缓冲已不存在（common.py:L183）。
- `disable_env_checker=True` 传给 make 只是不挂 checker，不影响 OrderEnforcing/TimeLimit；三者开关彼此独立（registration.py:L801-816）。同理 `max_episode_steps=-1` 传给 make 可显式摘掉 TimeLimit（registration.py:L813），拿到无步数上限的裸环境栈。
- StickyAction 的概率区间是 [0,1)（p=1 被拒，stateful_action.py:L62-65）——永远粘住等于策略失效，校验替你挡了；`repeat_action_duration` 是 v1.1.0 参数，老代码迁移时注意默认 1 退化为经典单步粘滞。
- `has_reset` 只读 property（common.py:L442-445）是探询包装链状态的正规入口，别去摸 `_has_reset` 私有变量；同理三个统计队列用 `env.return_queue` 之类直接读，deque 支持 len、索引与迭代，无需转 list。
- 阅读 07 篇可补全观测侧图景；`TimeAwareObservation` 对 TimeLimit 的存在性硬依赖（stateful_observation.py:L200-214）意味着"裸环境 + TimeAwareObservation"会直接抛 ValueError，先套 TimeLimit 再说。
