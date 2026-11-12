# 09 - 有状态 wrapper 全解：stateful_observation.py 与 stateful_action.py

> 源码锚点：`gymnasium/wrappers/stateful_observation.py`（651 行，5 个类）、`gymnasium/wrappers/stateful_action.py`（221 行，2 个类），兼及 `gymnasium/utils/record_constructor.py`（35 行）。行号以 main 分支 v1.4.0 为准。与 07 篇的分工：07 讲透了逐观测纯函数的 transform 家族与 FrameStack 空间推导、RunningMeanStd 在线算法、LazyFrames 移除史，本篇不重复，专攻"有状态"这条主轴本身。

## 一、角色定位

这一族 wrapper 回答的问题是：当"当前这一个观测/这一个动作"不足以决定输出时，wrapper 需要记忆。`stateful_observation.py` 的 `__all__`（L26-32）钉死清单为五类：`DelayObservation`（L35）、`TimeAwareObservation`（L106）、`FrameStackObservation`（L305）、`NormalizeObservation`（L465）、`MaxAndSkipObservation`（L565）。`stateful_action.py` 导出 `StickyAction`（L16）与 `RepeatAction`（L145）。

先钉一个类清单勘误：社区资料常列出的 `AddObservationNoise` 及其 `sen` 参数**在 Gymnasium 全仓不存在**（`grep -rn "AddObservationNoise" gymnasium/` 零命中），疑为与 PettingZoo/自定义 wrapper 集的记忆混淆。想加观测噪声，官方路径是 07 篇讲过的 `TransformObservation(env, func, space)` 一行闭包，不进本文件。

这七个类的共同身份是"越出 `ObservationWrapper.observation()` 逐观测纯函数钩子的能力"：或维护队列（Delay/FrameStack）、或持计数器（TimeAware/Sticky）、或累积统计量（Normalize）、或在一次外层 step 里多次驱动内层 env（MaxAndSkip/RepeatAction）。它们把 RL 理论里的部分可观测、延迟观测、控制噪声（执行丢失）、决策频率解耦这些"MDP 标准假设之外"的现实因素，以可栈式组合的方式注入环境。

## 二、内部结构

### 有状态光谱：reset 时清理什么

"有状态"不是二值属性，七个类在光谱上分三档，判据是 **reset() 覆写里动了哪些状态**：

| 档位 | 类 | reset 行为 | 状态生命期 |
|---|---|---|---|
| 伪有状态（无跨步状态） | MaxAndSkip、RepeatAction | 不覆写 reset | 无 |
| episode 内状态 | Delay、TimeAware、Sticky | 清空/归零 | 单 episode |
| 跨 episode 状态 | Normalize、FrameStack | 不清统计/重建队列但残留 padding | wrapper 整个生命期 |

具体看：`DelayObservation.reset` 只做 `self.observation_queue.clear()`（L92）；`TimeAwareObservation.reset` 只做 `self.timesteps = 0`（L300）；`StickyAction.reset` 清四件套 `last_action/is_sticky_actions/num_repeats/repeats_taken`（L111-114）。而 `NormalizeObservation` **根本不覆写 reset**——`obs_rms` 的 mean/var/count 跨 episode 永续积累，它的"状态"是训练期全局统计而非回合内记忆。`FrameStackObservation.reset`（L439-462）则介于两者：`obs_queue` 整体重建（L455-457 填 `stack_size-1` 个 padding + 1 个真观测），但自定义 padding_value 会残留到下次 reset。由此得出一个批判性结论：**文件归类"stateful"的真实标准不是有无状态，而是"能否塞进逐观测纯函数钩子"**——MaxAndSkip 与 RepeatAction 严格说无跨步状态，只因改写了 step 的编排频率（一次外层 step 驱动多次内层 step）才归入此文件。

### 各类骨架

**DelayObservation**（L35-103）：最薄的实现。`deque()` 无 maxlen（L86），钩子内 `append` 当前观测（L98），队列长度超过 `delay` 才 `popleft` 吐出头部，否则返回 `create_zero_array(self.observation_space)` 的合法零观测（L100-103）。`delay=0` 合法（L77-80 校验 `0 <= delay`），退化为恒等直通。注意 L46 的 Note 明言不支持随机延迟。

**TimeAwareObservation**（L106-302）：构造期搭一条三闭包管线——`_time_preprocess_func`（L219-226：归一化时 `lambda t: np.array([t / max_timesteps], float32)`，否则 `int32`）、`_append_data_func`（L229-244 按 Dict 加键/Tuple 追尾/其他包成 `{"obs":..., "time":...}` 三分派）、`_obs_postprocess_func`（L247-256 可选 flatten）。运行期钩子只是三者串联（L267-271）。`step` 覆写只有一句 `self.timesteps += 1` 再透传（L284-286）。`max_timesteps` 的探测链最讲究（L200-214）：先查 `env.spec.max_episode_steps`，失败则沿 wrapper 栈逐层下钻找 `TimeLimit`（L204-209，读其私有 `_max_episode_steps`），仍无则构造期 `ValueError`——因为归一化除数与时间空间上界 `Box(0, max_timesteps)`（L226）都依赖它。

**FrameStackObservation**（L305-462）：构造期 padding 三分支（L394-409）——`"reset"`/`"zero"` 共用 `create_zero_array` 占位（L397，reset 时前者会被真观测覆盖，L453-454），自定义值必须通过 `padding_type in env.observation_space` 包含检查（L398-399），随后 `padding_type` 字符串被改写为 `"_custom"`（L400）。空间用 `batch_space` 前插堆叠维（L411），`stacked_obs` 预分配输出缓冲（L418），step/reset 都走 `deepcopy(concatenate(...))` 物化返回（L434-436/L459-461）——deepcopy 防的是用户持有的引用被下一步覆写。

**NormalizeObservation**（L465-562）：构造期三道校验——`epsilon <= 0` 抛 `InvalidBound`（L520-523，注释 L517-519 讲明动机：epsilon 进平方根防除零，一旦超过方差会静默产出 NaN）；观测空间必须有 shape（L528-531，Dict/Tuple 被拒）；随后空间直接重置为 `Box(-inf, inf, shape, float32)`（L533-538）——归一化值理论上无界。核心是 property 对 `update_running_mean`（L546-554）冻结统计开关；钩子（L556-562）**先**喂统计**再**归一化：`if self._update_running_mean: self.obs_rms.update(np.array([observation]))`，然后 `(obs - mean) / sqrt(var + epsilon)` 转 float32。逐条流式，batch 维恒为 1。

**MaxAndSkipObservation**（L565-650）：docstring 注明移植自 stable-baselines3 的 `MaxAndSkipEnv`（L574）。`skip` 默认 4 且强制 `>= 2`（L598/L612-615）——末两帧取 max 至少需要两帧。`_obs_buffer` 预分配 `(2, *shape)`（L620-622）；step 循环内用 `i == skip-2` / `i == skip-1` 两个条件把倒数第二、第一帧分别写入两槽（L639-644），reward 累加（L645），`terminated or truncated` 提前 break（L646-647），最后 `np.max(buffer, axis=0)`（L648）。

**StickyAction**（L16-142）：以概率 p 丢弃 agent 本步动作、改执行上一步动作——"执行丢失"（execution slip）的建模。docstring 明确引用 Machado et al., 2018（arXiv:1709.06009）§5.2 第 12 页（L21-22）。p 校验为左闭右开 `[0,1)`（L62-65，`InvalidProbability`）——p=1 会让动作永久冻结。v1.1.0 新增 `repeat_action_duration: int | tuple[int, int]`（L44/L51）：int 归一化为 `(n, n)` 确定性重复（L70-73），tuple 给出随机重复长度区间，校验链在 L75-90（类型/长度/上下界/≥1）。运行期是一个四变量状态机（L102-105）：已在粘滞序列中、或抽样 `self.np_random.uniform() < p`（L121-124）则触发；新序列开始时从区间采样长度 `np_random.integers(lo, hi+1)`（L126-130）；动作替换为 `last_action`（L131）；计数到位后清零状态（L136-139）；**本步实际执行的动作回写 `last_action`**（L141）——粘滞动作本身成为新的锚点，连续触发可级联。

**RepeatAction**（L145-220）：确定性重复当前动作 `num_repeats` 次（默认无、强制 ≥1，L187-190），reward 求和，terminated/truncated 提前 break（L215-219）。docstring L155-159 精确点出与 StickyAction 的差异：后者**随机**用**前一**动作替换，前者**确定**地多次执行**当前**动作。

## 三、外部连接

**向上：core.py 的两个模板与 RNG 转发。** `ObservationWrapper` 固定 `Wrapper[WrapperObsType, ActType, ObsType, ActType]`，reset/step 编排后调 `observation()` 钩子；`ActionWrapper` 在 step **下发前**反向拦截调 `action()` 钩子——StickyAction 的替换因此对 env 完全透明。最容易被忽视的连接是 RNG：`Wrapper` 把 `np_random` 覆写成直转 property，getter/setter 都是 `self.env.np_random`（`core.py:L527-534`；`np_random_seed` 同样转发，L359-361；连 `_np_random` 私有槽都被 property 堵死并抛错，L536-541）。所以 StickyAction 钩子里的 `self.np_random`（L123/L127）**用的是内层 env 的 Generator**——粘滞抽样与环境自身随机性共流，`reset(seed=)` 播种 env 时抽样序列随之确定，实验可复现；代价是任何一方的随机消费都会移动另一方的流。

**向下：spaces 与 vector 工具。** FrameStack 依赖 `gymnasium/vector/utils` 的 `batch_space`/`concatenate`/`create_empty_array`（L23 导入、L411/L418/L435 使用）；TimeAware 依赖 `spaces.flatten_space`/`spaces.flatten`（L248/L251）；Normalize 的统计内核 `RunningMeanStd` 与 Delay/FrameStack 的 `create_zero_array` 都来自 `wrappers/utils.py`（07 篇已详）。

**构造参数记录系：RecordConstructorArgs。** 混入体全文仅 35 行（`utils/record_constructor.py`）：`__init__` 把 kwargs deepcopy 后存进 `_saved_kwargs`（L32-34）；关键设计是 first-wins——`if not hasattr(self, "_saved_kwargs")`（L31）保证只有第一次调用生效，docstring（L15-18）因此**强制要求在父类 `__init__` 之前先调它**（七个类全部遵守，如 L82-83、L92-97）。消费端在 `Wrapper.spec`（`core.py:L372-409`）：检测到混入后取出 `_saved_kwargs`、剥掉 `"env"` 键（L382-384），装成 `WrapperSpec`（L390-395）追加到 `env_spec.additional_wrappers`（L399）——整条 wrapper 栈因此可由 spec 完整重建（`env.copy()`、pickle、`make(**kwargs)` 复原）。一个精妙的配套设计是**记录语义与运行语义分离**：StickyAction 的注释（L67-69）明说 `repeat_action_duration` 保留调用者原值供 spec 存档、内部另用归一化的 `duration_range`；FrameStack 把 `padding_type` 改写成 `"_custom"`（L400）但 L381-383 入档的是原值——重建时原值能重新通过包含检查，两侧自洽。

**vector 镜像与弃用别名。** 五个观测类中**唯一**有 vector 版的是 NormalizeObservation（`wrappers/vector/stateful_observation.py:L29`）；其余四类 docstring 均明写 "No vector version of the wrapper exists"。模块级还有 v1.0.0 改名残留：`_renamed_wrapper = {"FrameStack": "FrameStackObservation", ...}`（`wrappers/__init__.py:L157-161`）经模块 `__getattr__` 发弃用警告。另外 Atari 场景的 `AtariPreprocessing`（`atari_preprocessing.py:L16`）**自己实现了 `frame_skip=4`**（L55-56）而非复用 MaxAndSkipObservation——领域专用管线与通用类有意分离。

## 四、数据流

**StickyAction 一次 step（duration 区间版）**：agent 调 `wrapper.step(a)` → `ActionWrapper.step` 先调 `action(a)`（core.py 模板）→ 钩子判定：若 `is_sticky_actions=True`（序列未完）或 `uniform() < p` 命中（L121-124），且 `num_repeats == 0` 则先采样本序列长度（L126-130），执行动作替换为 `last_action`（L131），`repeats_taken += 1`（L133）；随后若序列数耗尽（`num_repeats == repeats_taken`）清三计数（L136-139）；最后 `last_action = 实际执行值` 并返回（L141-142）→ env 收到的是替换后的动作，reward/obs 原样上浮。`duration=1`（默认）时长度采样恒为 1，每步独立判定，退化回经典 sticky；tuple 版则把独立伯努利升级为"一次抽中、连粘 k 步"的突发式丢失。由于 RNG 与 env 共流，同 seed 下 CartPole 的 doctest（L30-40，p=0.9）输出完全确定。

**MaxAndSkip 一次 step**：外层一次 `step(action)` 展开为内层 4 次同动作 step——决策频率降为物理频率的 1/4，reward 是 4 帧之和，观测是末两帧逐像素 max。doctest（L576-592）钉证：wrapped 第一步观测等于裸环境第 3、4 步观测的 `np.max(np.stack(...))`。

**Delay 的时序**：reset 清队列后，前 `delay` 个 step 全部返回零观测（L100-103），第 `delay+1` 步才吐出 episode 第 1 个真观测——doctest（L54-60）里 delay=2 时前两步全零、第三步返回 reset 时刻的观测。观测流水线整体右移，信息不丢只迟。

**TimeAware 的注入**：reset 返回的 obs 携带 t=0，首个 step **先** `timesteps += 1` 再透传（L284-286），故首步返回 t=1（doctest L135/L138 钉证）；`normalize_time=True` 时第 t 步注入 `t / max_timesteps ∈ [0,1]`（float32，L220-222），t=1 恰对应 TimeLimit 置 `truncated=True` 的时刻——agent 由此获得"距离截断还剩多少"的显式信念。

**Normalize 的流式归一**：每条观测以 batch 维 1 喂 `obs_rms.update`（L559），随即用更新后的统计归一化——Welford 式"先吸收再归一"，冷启动阶段近似原样除以 1。

## 五、设计决策

**1. reset 契约是有状态 wrapper 的第一文档。** 判断一个 wrapper 的状态语义，看 reset 覆写比看类名更可靠：清队列/归零计数的是 episode 内记忆；不覆写 reset 的 Normalize 意味着统计跨回合共享——这正是它"评估前必须冻结"的根源。这条隐式契约没有任何基类强制，全靠各覆写自觉维护 super().reset() 透传链。

**2. MaxAndSkip 的三合一与 flicker max 的 Atari 传统。** 动作重复（降决策频率）、reward 求和（保持回报尺度）、末两帧 max（消除 Atari 偶/奇帧 sprite 闪烁——部分物体只在半数帧渲染，单帧会随机丢物体，DQN Nature 2015 预处理的传统）打包在一个 wrapper 里，因为三者在 frameskip 语境下不可分割：跳帧必须补偿闪烁，而回报尺度必须随物理步数同步缩放。与 RepeatAction 的分立则体现语义边界：RepeatAction 是通用的"降频"工具（无 max、默认无、≥1 即可），MaxAndSkip 是像素观测专用（强制 ≥2 保两帧 max，docstring 直接挂 SB3 出处）。Atari 官方管线里两者都退场，由 AtariPreprocessing 一体化实现。

**3. StickyAction：从独立伯努利到粘滞序列。** Machado et al. 2018 推荐的 ALE 评估"难模式"用 p=0.25 的 sticky action 模拟人类输入抖动，Gymnasium 把 p 作为必填参数强制用户显式选择；v1.1.0 的 `repeat_action_duration` 再把"每步独立以 p 丢一拍"升级为"以 p 触发、连丢 k 拍（k 可采样）"——后者更贴近真实输入设备的卡顿突发性。四变量状态机（L102-105）以最小成本同时支持两种模式，默认 duration=1 保持向后兼容。

**4. update_running_mean 冻结语义。** 训练期 True（默认）流式更新；评估期设 False 后统计只读——否则评估轨迹会持续污染统计（自馈偏差），且不同 checkpoint 的评估结果不可比。实现上用 property 对而非公开属性（L546-554），为文档与未来校验留口。这是 v1.0.0 专门补的特性（L503），与"空间重置为 ±inf + 强制 float32"同期落地——三者共同构成"归一化观测无界"的完整承诺。

**5. RNG 共流：可复现性与交织风险同源。** wrapper 不自建 Generator 而转发 env（`core.py:L527-534`），好处是 `reset(seed=)` 一个种子同时确定环境动态与 wrapper 随机性；坏处是栈内多个随机消费者（StickyAction + 随机 reset 环境）的抽样顺序耦合，增删任何一层 wrapper 都会改变双方的流。做严格对照实验时这是必须意识到的坑。

**6. 四参泛型在状态改写下的型变。** 七个类的泛型签名精确编码了"谁被改写"：`DelayObservation` 是 `ObservationWrapper[ObsType, ActType, ObsType]`（L36）——观测类型恒等（只延迟不改形）；`TimeAwareObservation`/`NormalizeObservation` 是 `[WrapperObsType, ActType, ObsType]`（L107/L466）——观测类型漂移（增维/换 dtype）；`FrameStackObservation`/`MaxAndSkipObservation` 干脆继承 `gym.Wrapper[WrapperObsType, ActType, ObsType, ActType]`（L306/L566）完全自管 step；动作侧 `StickyAction` 是 `ActionWrapper[ObsType, ActType, ActType]`（L17）动作类型恒等（只换值不换型），`RepeatAction`（L146）四参全恒等。类型签名本身就是 wrapper 能力的声明书。

## 六、新人提示

- **MaxAndSkip 的 early-break 边缘瑕疵**：`_obs_buffer` 只在构造期分配零（L620-622），reset 不清空。若 skip 循环第一步就 terminated，`buffer[0]` 仍是**上一次外层 step** 的倒数第二帧（首回合则是全零），max 会混入陈旧像素。影响轻微但做像素级回归测试时会咬人。
- **Normalize 两个坑**：冷启动阶段（mean=0,var=1）输出远非 N(0,1)，惯例随机策略预热数千步；docstring L477-479 明确警告换策略后旧统计失效。评估前务必 `update_running_mean = False`，且冻结前确认统计已积累足够。
- **TimeAware 的构造前置条件**：`spec.max_episode_steps` 或栈内 TimeLimit 必居其一，否则构造即 ValueError（L211-214）。`gym.make` 默认套 TimeLimit，裸 `Env()` 实例不套——自己 new 的环境记得先包。
- **StickyAction 与 RNG 共流**：同 seed 可复现是福利；但栈序变化会改变抽样流。另注意 p=1 被设计性拒绝（L62-65）。
- **组合顺序即语义**：Atari 惯例 `FrameStack(Normalize? No—)` 应为内层像素预处理（Grayscale/Resize）→ MaxAndSkip（内，物理降频）→ FrameStack（中，堆叠历史）→ Normalize（最外，对最终观测归一）。wrapper 栈无全局一致性检查，用 `observation_space` 形状自查。
- **Delay 不支持随机延迟**（L46 Note），需要随机延迟得自己写 deque 变体；`delay=0` 是合法的恒等直通。
- **写自定义 wrapper 的判断口诀**：变换只依赖当前观测 → 覆写 `observation()` 钩子；只需增强 reset（清状态）→ 覆写 reset 记得调 super；要多次驱动内层 step（降频/聚合）→ 直接继承 `gym.Wrapper` 自管 step/reset；要拦截动作 → `ActionWrapper` 的 `action()` 钩子；消费随机数 → 记住 `self.np_random` 是 env 的流，先 `RecordConstructorArgs.__init__` 再调父类构造（first-wins 语义，`record_constructor.py:L31`）。

---

*本篇行号锚均从 v1.4.0 main 分支源码逐一核实；"reset 契约三分档"、StickyAction 状态机与 RNG 共流、RecordConstructorArgs 的记录/运行语义分离是本文件群最值得带走的三个知识点。*
