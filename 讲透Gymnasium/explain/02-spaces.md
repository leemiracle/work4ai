# 02 · Space 抽象基类精讲：spaces/space.py 与 Box/Discrete 双子星

> 源码版本：main @ 8b22ad4（含 2026-10-09 ragged 修复 50ab36f）
> 行号锚格式 `文件:L行号`，全部从当前源码核实。

## 一、角色定位

如果说 `core.py` 的 `Env` 定义了 RL 环境的**行为**契约，那么 `spaces/space.py` 的 `Space` 类（space.py:18）定义的是环境的**类型系统**：每个 Env 必须声明 `action_space` 与 `observation_space`，二者都是 `Space` 实例（spaces/__init__.py:4 的模块 docstring 开宗明义）。官方 docstring 列了三大用途（space.py:24-28）：清晰定义交互格式（动作长什么样、观测长什么样）；把高维结构化数据（如 Dict 空间元素）无痛转成学习代码可用的扁平数组；提供随机采样以支撑 exploration 与调试。

在知识图谱中，`class:Space` 直接 fanIn=13（全部内建空间子类），而它所在的 `spaces/__init__.py` barrel 是全仓最大枢纽之一——图谱实测 fanIn=103、fanOut=12，全库 53 个源文件直接 `from gymnasium.spaces import ...`。换句话说，Gymnasium 的每个环境、每个 wrapper、每条校验链都在消费这个包。`space.py` 本身只有 168 行，却是整个生态的隐式协议源头：下游库（Stable-Baselines3、CleanRL 等）靠"有 `sample`/`contains`/`shape`/`dtype`"这一鸭子类型事实编程，而不是靠显式 ABC 注册。

理解 Space 的正确心智模型是**数学集合 + 采样器**：`Discrete(3)` 就是集合 $\{0,1,2\}$ 附带一个可 seed 的均匀随机源；`Box(low, high)` 就是 n 个闭区间的笛卡尔积附带按区间形态选分布的采样器。它不是张量描述符（不含 device、batch 概念，与 PyTorch/TensorFlow 完全解耦），也不是类型标注（不做任何静态检查）——所有校验都是运行时谓词。这个朴素定位恰恰是它十年不倒的原因：RL 环境需要的就是一个"能采样、能判属、能压平"的集合抽象，多一分都会伤害互操作性。

## 二、内部结构

`Space(Generic[_T_co])` 用协变类型参数刻画"这个空间的元素类型"（如 `Box` 是 `Space[NDArray]`、`Discrete` 是 `Space[np.integer]`），类属性声明只有三个（space.py:44-46）：`dtype`、`_shape`、`_np_random`。构造函数（space.py:48-68）做三件规整事：shape 转 tuple、dtype 转 `np.dtype`（space.py:61-62）、seed 参数兼容 int 与现成 `np.random.Generator` 两种形态（space.py:64-68）。

**四大原语**构成 Space 的核心 API 面：

1. **`sample(mask, probability)`**（space.py:96-110）——随机采样一个元素，mask 与 probability 互斥（space.py:101）。基类只给签名抛 `NotImplementedError`，分布语义完全下放给子类：Box 按区间形态选分布（见第四节），Discrete 有 uniform / mask / probability 三模式，MultiBinary 支持 dtype 校验过的布尔掩码。Box 明确拒绝两种掩码（box.py:424-431 抛 `gym.error.Error`）——"连续空间无合法掩码"被显式写进契约。
2. **`contains(x)`**（space.py:124-126）——判断 x 是否为合法成员，`__contains__`（space.py:128-130）让它支持 `sample in space` 原生语法。基类不提供默认实现，但全族遵循一条隐式不变量（见第五节的 ragged 案例）。
3. **`seed(seed)`**（space.py:112-122）——经 `seeding.np_random`（utils/seeding.py:10）装配 PCG64 Generator 写入 `_np_random`，返回实际使用的 seed（复合空间返回 tuple/dict）。seed 也接受现成 Generator（space.py:65-66），这让 vector 环境能把同一个 RNG 流切分给子空间。
4. **`to_jsonable` / `from_jsonable`**（space.py:160-168）——**批量**样本与 JSON 类型的双向转换，基类默认恒等（假定元素本身 JSONable），由数值型子类覆写。注意参数名 `sample_n` 是复数——这对 API 面向的是"一批样本"，服务 `RecordEpisodeStatistics` 等录制型 wrapper 与 JSON 落盘，而非单元素转换。

除四大原语外还有两个次要接口：`shape` 只读 property（space.py:86-89，内部字段 `_shape` 下划线私有，杜绝外部改形状）；`is_np_flattenable`（space.py:91-94）回答"能否被 `flatten_space` 压成一个 Box"——Box/Discrete/MultiDiscrete/MultiBinary 返回 True，Text/Graph/Sequence 等返回 False，这决定了学习代码能否把它们喂进固定维度输入层。

两个值得咀嚼的细节：其一，`np_random` 是惰性 property（space.py:70-84）——双重兜底逻辑：`_np_random` 为 None 先调 `self.seed()`，若仍为 None（注释明言复合空间不保证设置）则直接 `seeding.np_random()` 随机造一个。这保证"忘记 seed 也能 sample"，代价是静默不可复现。其二，`__setstate__`（space.py:132-158）做旧 pickle 迁移：老版 gym 对象的 `shape`/`np_random` 字段改名为 `_shape`/`_np_random`（space.py:150-155，注释引 openai/gym PR #2397/#1913）。

## 三、外部连接

`spaces/__init__.py:14-25` re-export 全部空间类与工具函数，`__all__`（spaces/__init__.py:27-48）分三层：基类 `Space`；基本空间 `Box/Discrete/Text/MultiDiscrete/MultiBinary`；复合空间 `Graph/Tuple/Sequence/Dict/OneOf`；外加 `flatdim/flatten/unflatten/flatten_space` 四个工具函数（实现在 spaces/utils.py:101/182/356/532）。

上游依赖极薄：`numpy` + `utils/seeding`。下游消费者分五路：**core.py** 的 Env 契约（`action_space`/`observation_space` 是 Env 一等属性，Wrapper 透传并可改写）；**校验链** `utils/env_checker.py` 与 `passive_env_checker.py`（前者侵入式全套检查，后者挂在 `OrderEnforcing`/`PassiveEnvChecker` wrapper 里逐 step 断言，如 passive_env_checker.py:31-36 断言 Box 的 low/high shape 必须等于空间 shape）；**wrappers**（RescaleAction、ClipAction、NormalizedObservation 等直接改写 Box 边界，TransformObservation 用函数+新空间替换声明）；**vector 子包**（下详）；以及**全部 100+ 内建环境**（MuJoCo 系声明 `Box(-inf, inf, ...)` 观测 + `Box` 关节动作，classic control 系用 Discrete 动作 + Box 观测，Atari 系用 MultiBinary/Discrete）。测试基座 `tests/testing_env.py` 的 GenericTestEnv 默认动作空间就是 `Box(0, 1, (1,))`——Box 是整个仓库的"默认空间"。

值得注意的边界：spaces 包**不依赖** core/vector/envs 中任何模块（依赖方向单向向内），这让它可以被独立复用——事实上不少非 RL 项目直接拿 `gym.spaces` 描述张量形状与取值域。`spaces/utils.py:678` 的 `is_space_dtype_shape_equiv` 被 sync_vector_env.py:14 引入，作为 SyncVectorEnv 校验"子环境空间兼容可批"的判据，是 spaces 与 vector 两个子系统的接缝。

## 四、数据流

以一次向量化训练的动作流为例：

1. **seed**：`envs.action_space.seed(123)` → `Space.seed()` → `_np_random` 装配（space.py:121）。
2. **批量空间合成**：`SyncVectorEnv.__init__` 执行 `self.action_space = batch_space(self.single_action_space, self.num_envs)`（sync_vector_env.py:123）。`batch_space`（vector/utils/space_utils.py:51）是 `functools.singledispatch` 分派器，按空间类型做**非对称类型跃迁**：`Box→Box`（shape 前缀 n，tile low/high，space_utils.py:79-84）、`Discrete→MultiDiscrete`（space_utils.py:86-94）、`MultiDiscrete→Box`、`MultiBinary→Box`（space_utils.py:96-117）、`Tuple/Dict` 递归（space_utils.py:120-135）、`Text/Graph/Sequence/OneOf` 及自定义空间兜底为 `Tuple(deepcopy×n)`（space_utils.py:137-142）。注意 `seed=deepcopy(space.np_random)`——批量空间与单空间的采样流互不污染。所谓"batch_dim 前缀"只是 Box/MultiBinary 一支的现象，框架真正的抽象是"批量空间是运行时合成的视图，而非 Space 的某个子类"。
3. **采样**：`actions = envs.action_space.sample()`。以 Box 为例，`Box.sample`（box.py:404-481）按四个布尔掩码把各维度分派到四种分布（box.py:437-457）：双边有界→uniform、仅下界→exponential+low、仅上界→-exponential+high、无界→normal。无界维度用正态、单边用指数是刻意设计：均匀分布无法定义在无穷区间上，而探索恰恰需要能采到任意远处。整数 dtype 有三步特护：上界 +1 再 floor（box.py:433, 459-460，保证 high 可被采到且均匀）；按 dtype 极值 clip（box.py:462-472）；int64 因 float64 精度不够还要留 ±2 margin 并二次 clip（box.py:466-479 的两段注释是教科书级的浮点边界处理）。
4. **校验**：环境内部（及 passive checker）用 `action in action_space` → `contains`。`Box.contains`（box.py:483-497）四连判：`np.can_cast(x.dtype, self.dtype)` + shape 相等 + 逐元素 low/high 比较；输入非 ndarray 时先 `np.asarray` 且转换失败直接返回 False（box.py:485-490）。Discrete 侧的三模式采样同样带武装检查：mask 必须是 int8、shape `(n,)`、值域 0/1（discrete.py:151-164）；**全零 mask 返回 `start` 而非报错**（discrete.py:166-171）——"无合法动作"被定义为返回最小动作，这是给已死局环境留的逃生门，也是新人最意外的语义；probability 则断言和为 1（discrete.py:184-189）。
5. **观测回流**：step 返回的 obs 走对称路径——`env_checker` 断言 `obs in observation_space`，ObservationWrapper 改写观测后同样要过检。观测若是 Dict/Tuple 复合结构，学习代码用 `flatten(space, x)`（spaces/utils.py:182）压平、`unflatten`（spaces/utils.py:356）还原，`flatten_space`（spaces/utils.py:532）把整个空间映射为等价的扁平 Box 声明。
6. **序列化**：录制型 wrapper 用 `to_jsonable` 批量转 JSON——Box 调 `.tolist()`（box.py:499-501），Discrete 转纯 `int`（discrete.py:261-263），`from_jsonable` 逆操作恢复 dtype（discrete.py:265-267）。这一对函数是"numpy 世界"与"JSON 世界"的唯一闸口，自定义空间若元素不可 JSON 序列化必须覆写。

## 五、设计决策

**（1）抽象基类不用 ABCmeta。** sample/contains/is_np_flattenable 都是裸 `raise NotImplementedError`（space.py:96-110, 124-126）而非 `@abstractmethod`——好处是 duck typing 友好、自定义空间可以只实现子集；代价是漏实现推迟到运行时才炸。配套的官方警告（space.py:33-41）直言：参数化采样分布与 vector 批量函数只对内建空间良定义，自定义空间自担风险。

**（2）Box 的 bounded 语义是逐维布尔数组，不是全局标量。** `bounded_below/bounded_above` 在 `_cast_low/_cast_high` 中以 `-np.inf < low` / `high < np.inf` 逐元素计算（box.py:248, 278, 315, 345），这才让混合区间 Box（如 `[-1,1]×[0,∞)`）可表达；`is_bounded(manner)` 提供 below/above/both 三态查询（box.py:379-402）。∞ 不是合法存储值——int dtype 下 ±inf 会被替换为 dtype 极值（box.py:253-258, 283, 319-325，unsigned 直接报错），nan 一律 ValueError（box.py:251, 276）。**dtype 陷阱**：Box 默认 `float32`（box.py:129），若 low/high 传入 float64 数组，精度高于目标 dtype 时仅 `gym.logger.warn` 不 raise（box.py:293-299）——`Box(low=np.array([0.1]), dtype=np.float32)` 的 low 已经不是你写的 0.1。另有一处 docstring 与代码打架：`Box.__eq__` 的 docstring 声称 "Doesn't check dtype equivalence"（box.py:525），但代码明明比较了 `self.dtype == other.dtype`（box.py:529），且边界用 `np.allclose` 容差比较（box.py:530-531）——以代码为准。

**（3）Discrete 的标量哲学与 one-hot 争议。** `Discrete(n, start)` 表示整数集 $\{a, a+1, \dots, a+n-1\}$（discrete.py:30），`sample` 返回**标量** `np.int64` 而非 one-hot 向量（discrete.py:196）。这是立场选择：空间元素 = 数学元素，one-hot 属于"展平"职责——`flatten` 对 Discrete 的实现正是 one-hot（spaces/utils.py:233-236）。争议在于策略网络输出的 logits 形状与空间元素形状天然不匹配，转换负担被推给 flatten/unflatten 与下游库；向量化时 Discrete 变 MultiDiscrete 向量而非 one-hot Box（space_utils.py:86-94），同一动作在不同层有三种形态（标量/one-hot/批量向量），新人最容易在此迷路。`Discrete.contains` 的防御也体现了标量哲学：只接受 int 或 0 维整数 np 标量（discrete.py:209-212），int 输入还要先过 iinfo 值域检查再谈转换（discrete.py:203-207）。

**（4）contains 的 ragged 防御——最新演化的活案例。** 2026-10-09 的 50ab36f（PR #1753，"Return False for ragged MultiBinary and MultiDiscrete inputs"）修复了一个契约违约：`MultiBinary/MultiDiscrete.contains` 对 Sequence 输入裸调 `np.array(x)`，遇到 ragged 输入（如 `[[0], [0, 1]]`）会 raise ValueError 而非返回 False，把"谓词"变成了"炸弹"。修复是 try/except 包裹（multi_binary.py:139-142、multi_discrete.py:252-255）+ 回归测试 `test_contains_ragged_sequence`（tests/spaces/test_space.py）。对照可见防御姿势的代际差：Box 早已这么防（box.py:485-490），Discrete 靠类型白名单从根上免疫，MultiBinary/MultiDiscrete 是最后补齐的一环——"contains 永远返回 bool、永不 raise"现在才成为全族不变量。

**（5）`__setstate__` 三代 pickle 迁移**（space.py:132-158、discrete.py:241-259 补 `start=0`、box.py:534-545 补 `low_repr/high_repr`）：作为老 gym 的继任者，环境 checkpoint 跨版本加载是硬需求，三个数值空间各自背着历史包袱。顺带一提 `Box.__repr__` 的缓存设计（box.py:518-522）：`low_repr/high_repr` 首次渲染后缓存字符串，若 bound 是全同值的数组就只打印标量（`array_short_repr`，box.py:40-54）——repr 是高频调试输出，缓存让 `print(env.action_space)` 不至于每次都序列化整个数组。

**（6）assert 做参数校验的争议**。Discrete 的 mask/probability 检查全部用 `assert`（discrete.py:151-189），而 Box 的边界检查用 `raise ValueError`（box.py:225-228）。`python -O` 会剥掉 assert，届时错误 mask 静默产出非法样本——这在库设计里通常被视为反模式，但 Gymnasium 的立场是采样参数属于"开发者自担"的 fast path，运行时性能优先。写生产级环境时建议学 Box 的防御姿势。

## 六、新人提示

- **`in` 就是 contains**：环境里校验动作写 `assert action in self.action_space` 即可（space.py:128-130）。
- **复现实验必须显式 seed**：`np_random` 惰性兜底意味着不 seed 也能采样，但每次运行不同（space.py:77-82）；复合空间 `seed([s1, s2, ...])` 接受列表，返回实际 seed 集。
- **整数 Box 采样含上界**：uniform 是 `[low, high+1)` 再 floor，high 可被采到（box.py:433）；但构造时 `high` 若超出 dtype 范围会直接 ValueError（box.py:326-329）。
- **要 one-hot 用 flatten**：`flatten(space, space.sample())`（spaces/utils.py:182，Discrete 分支 one-hot 在 233-236），别手搓 `np.eye`——start 非零的 Discrete 手搓必错。
- **dtype 精度静默降级只 warn**（box.py:293-299）：构造 Box 后打一行 `space.low` 验证，别信你传入的数组。
- **自定义空间三思**：vector batching 会走 `Tuple(deepcopy×n)` 兜底（space_utils.py:141-142），性能差且丢失结构；官方 docstring 警告在先（space.py:33-41）。
- **写自定义 contains 记住新不变量**：任何怪输入（ragged、错误类型、溢出）一律返回 False 不 raise——学 box.py:485-490 的姿势，50ab36f 就是前车之鉴。
- **Discrete 全零 mask 返回 start 而非报错**（discrete.py:166-171）：调 sample 前先判断 `np.any(mask)`，否则死局环境会静默拿到最小动作还以为在正常探索。
- **vector 环境的 action_space 形状会变**：`Discrete` 批量化后成 `MultiDiscrete((n,) 个相同 n)`，策略网络输出形状要按 `batch_space` 的结果对齐，别按单空间对齐。
- **Box.__eq__ 是 allclose 语义**（box.py:530-531）：两个"看起来一样"的 Box 相等不代表 low 逐位相同；docstring 关于不查 dtype 的说法已过时（box.py:525 vs 529），读码优先读实现。`Discrete.__eq__` 则要求 n、start、dtype 三者全等（discrete.py:232-239），`Discrete(3)` 与 `Discrete(3, start=0)` 相等但与 `Discrete(3, start=-1)` 不等。
