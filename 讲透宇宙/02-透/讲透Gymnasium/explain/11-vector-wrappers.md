# 11 · wrappers/vector/ —— 作用于 VectorEnv 的包装器镜像层

> 源码：`gymnasium/wrappers/vector/`（12 个文件 2582 行：`__init__.py` 115 · `array_conversion.py` 136 · `common.py` 238 · `dict_info_to_list.py` 158 · `jax_to_numpy.py` 39 · `jax_to_torch.py` 35 · `numpy_to_torch.py` 49 · `rendering.py` 553 · `stateful_observation.py` 167 · `stateful_reward.py` 185 · `vectorize_action.py` 290 · `vectorize_observation.py` 475）· 图谱定位：vector 子系统的 wrapper 集群，图谱摘语钉版为"作用于 VectorEnv 的 wrappers 镜像集：vectorize_observation/action/reward 把单环境 transform 变换升维到批量轴；array_conversion/jax_to_numpy/jax_to_torch/numpy_to_torch 做批量转换"

## 一、角色定位：三层镜像，一个懒加载网关

上一篇（10）讲了 `VectorEnv` 引擎本身——契约、Sync/Async 实现、autoreset 三态。但训练代码真正打交道的很少是裸 `SyncVectorEnv`：采样循环要归一化观测、裁剪动作、统计回合回报，GPU 训练还要在 numpy 与 torch/jax 之间搬运数组。`wrappers/vector/` 就是把这些横切需求从引擎里剥出来、按 `gymnasium.Wrapper` 的组合模式（07 篇讲过标量版）整体镜像到批量世界的一层。它不实现任何环境动力学，只做三件事：

其一，**变换镜像**。`vectorize_observation.py` / `vectorize_action.py` / `vectorize_reward.py` 三个文件复刻了标量层 transform 家族的全部成员（`FilterObservation`、`ResizeObservation`、`ClipAction`、`RescaleAction`、`ClipReward` 等 10 个薄壳类），核心机制是把"只认识单条数据的标量变换函数"逐条套到批量数组的每个槽位上再拼回来。其二，**状态化统计**。`stateful_observation.py` 的 `NormalizeObservation`、`stateful_reward.py` 的 `NormalizeReward`、`common.py` 的 `RecordEpisodeStatistics` 维护跨 step 的运行统计，是 09 篇标量版的批量对应物。其三，**数组框架转换**。`array_conversion.py` 加三个单行子类（`jax_to_numpy.py` / `jax_to_torch.py` / `numpy_to_torch.py`）让 jax 引擎（如 `FunctionalJaxVectorEnv`）和 torch 训练循环无缝对接。`rendering.py`（`HumanRendering` + `RecordVideo`）与 `dict_info_to_list.py` 补齐可视化与 info 格式需求。

入口 `__init__.py` 是一个精心设计的 barrel：`__all__` 列出 26 个类名（`__init__.py:L34-73`），其中 22 个在模块顶层直接导入（L6-32），唯独 4 个数组转换类（`ArrayConversion`/`JaxToNumpy`/`JaxToTorch`/`NumpyToTorch`）走 **PEP 562 模块级 `__getattr__` 懒加载**（`__init__.py:L93-115`）——理由写在 L83-84 的注释里：这些类源文件顶部有 `import jax` / `import torch`，而这两个包导入动辄数秒，绝不能在 `import gymnasium` 时被连带触发。`_wrapper_to_class` 映射表（L85-91）把类名映射到模块名字符串，访问时才 `importlib.import_module`（L110-113）。对静态类型检查器则用 `TYPE_CHECKING` 分支（L75-79）直接 import，保证 IDE 补全与类型推导不受懒加载影响——运行时零成本、静态期全可见，两头占全。

## 二、内部结构

### 2.1 基类塔：来自 vector_env.py 的四个钩子

本目录所有类的父辈不在目录内，而在 `gymnasium/vector/vector_env.py`：`VectorWrapper`（L361）是批量版 `Wrapper`——持有 `env` 并做 `isinstance` 校验（L389-392），四个空间属性实现为"本地槽优先、None 则透传"的 property（L394-397 初始化槽，L441-451 读写）。三个特化子类各开一个变换钩子：`VectorObservationWrapper.observations()`（L591，reset 与 step 的输出都过它，L571-589）、`VectorActionWrapper.actions()`（L625，动作进内层**之前**变换，L619-623）、`VectorRewardWrapper.rewards()`（L658，L651-656）。这套钩子协议决定了本目录每个类的实现形态：覆写一个函数，而不是拦截整个 step。

### 2.2 vectorize 三兄弟：假环境驱动的"标量 wrapper 复用机"

每族分三层。第一层 `TransformObservation`/`TransformAction`/`TransformReward`（`vectorize_observation.py:L20`、`vectorize_action.py:L20`、`vectorize_reward.py:L21`）接受**用户手写的批量函数**直接套在整批数据上——适合能用 NumPy 广播或 jax vmap 一次算完整批的场景；构造器里的空间推断逻辑（如 `vectorize_action.py:L83-95`）在 `action_space` 与 `batch_space(single_action_space, num_envs)` 不一致时发警告。

第二层是本目录最机巧的设计：`VectorizeTransformObservation` / `VectorizeTransformAction`（`vectorize_observation.py:L104`、`vectorize_action.py:L104`）内部造一个**假单环境** `_SingleEnv`——一个只有 `observation_space`（或 `action_space`）属性的空壳 `Env`（`vectorize_observation.py:L147-154`）——然后把**标量层的 wrapper 类**实例化在这个假环境上（L190-192）。标量 wrapper 在构造时对空间做的一切推导（Resize 改 shape、Dtype 改 dtype、Rescale 换上下界）全部白拿，向量层只需 `batch_space` 一次（L194-196）就得到正确的批量空间，两套实现永不漂移。真正干活的是 `observations()`/`actions()` 钩子：`iterate(space, batch)` 把批量数据按单环境切片，逐片喂给标量 wrapper 的 `func`，再 `concatenate` 拼回批量（`vectorize_action.py:L185-192`）。`same_out` 标志（L171）记录输出空间是否与内层一致：一致时 `concatenate` 直接以输入数组为缓冲就地写回（零分配），不一致时写入预分配的 `self.out`（`create_empty_array`，L173）再 `deepcopy` 交出（L193-203）——预分配数组内含垃圾值，Dict/Tuple 空间下不能直接外露。`VectorizeTransformReward` 更极端：连假环境都不需要，直接 `wrapper(Env(), **kwargs)`（`vectorize_reward.py:L97`），因为标量 `TransformReward` 构造时不碰空间；其 `rewards()` 是朴素的原地 for 循环逐元素覆写（L99-103）。第三层是 10 个一行委托的薄壳：`ClipAction`（`vectorize_action.py:L208`）、`RescaleAction`（L235）、`FilterObservation`（`vectorize_observation.py:L246`）、`FlattenObservation`（L287）、`GrayscaleObservation`（L314）、`ResizeObservation`（L346）、`ReshapeObservation`（L376）、`RescaleObservation`（L406）、`DtypeObservation`（L449）、`ClipReward`（`vectorize_reward.py:L106`）等，构造器一行 `super().__init__(env, transform_x.X)` 把标量类传给复用机。

### 2.3 array_conversion：singledispatch 树遍历 + 单行子类

`ArrayConversion`（`array_conversion.py:L20-24`，继承 `VectorWrapper` + `RecordConstructorArgs`）持四个参数：环境所在框架 `env_xp`、目标框架 `target_xp` 及两个 device（L40-47）。`step` 是全双工的：动作先从外部框架转回环境框架（L75-77），内层 step 后五个返回值（obs/reward/terminated/truncated/info）逐个转到目标框架（L80-88）；`reset` 连 `options` 也转（L105-108）。真正的转换函数 `array_conversion` 不在本目录——它躺在标量层 `gymnasium/wrappers/array_conversion.py:L72`，是一个 `functools.singledispatch` 函数，按值类型分派成**递归树遍历**：`numbers.Number` 走 `xp.asarray`（L80-85）；`abc.Mapping` 重建同类型 dict 并对每个 value 递归（L88-93）；`abc.Iterable` 先用 `is_array_api_obj` 拦截真正的数组（L105-106，Array API 对象没有独立类型标记，只能落在 Iterable 分支里再甄别），namedtuple 用 `_make` 保类型（L107-110），普通可迭代重建容器递归（L111）；`None` 直通（L148-153）；全部不中则抛异常（L75-77）——所以 dict 套 tuple 套 ndarray 的复杂 obs 会被自动整树转换。叶子转换 `_array_api_array_conversion`（L114-145）主路径是 `xp.from_dlpack(value, device=device)`——**DLPack 零拷贝**，目标数组与源共享底层内存而非复制；后面挂三条异常降级链：torch 尚不支持 dlpack 的 device 参数（TypeError→裸 from_dlpack 再 `to_device`，L122-125）、源缓冲只读（BufferError→先显式 copy 成可写再转，L126-132 与 L139-145 两处，jax 不支持 `copy=True` 所以分两路）、torch 张量与目标设备不兼容（RuntimeError→先搬 CPU 再转，L133-138）。NumPy 没有设备概念，目标为 numpy 时强制 `device="cpu"`（L118）。三个子类都是单行委托：`JaxToNumpy`（`jax_to_numpy.py:L39`）、`JaxToTorch`（`jax_to_torch.py:L33`）、`NumpyToTorch`（`numpy_to_torch.py:L47`）只是把 `(env_xp, target_xp)` 固定成 `(jnp, np)`/`(jnp, torch)`/`(np, torch)`。

### 2.4 状态化三件套与渲染双子

`NormalizeObservation`（`stateful_observation.py:L29`）用 `RunningMeanStd` 维护观测均值方差（L120-123），`observations()` 每步先用整批 obs 更新统计再除以标准差（L162-167）；构造时把观测空间重建为无界 float32（L110-118），且**硬性只支持 `AutoresetMode.NEXT_STEP`**（L105-108，SAME_STEP 直接 ValueError），`reset` 拒绝部分重置的 `reset_mask`（L144-148）。`NormalizeReward`（`stateful_reward.py:L21`）不继承 `VectorRewardWrapper` 而直继承 `VectorWrapper`——它的语义是"先累积折扣回报再归一"，单纯 rewards 钩子表达不了；它维护标量 `return_rms = RunningMeanStd(shape=())` 与逐 env 的 `accumulated_reward`（L113-114），step 里用 `active` 掩码区分两种 autoreset（L158-168）：NEXT_STEP 跳过终止后那一步的 autoreset，SAME_STEP 每步都算且终局后立即清零。`RecordEpisodeStatistics`（`common.py:L23`）持四个 `(num_envs,)` 状态数组与三个 deque（L111-118），对 NEXT_STEP/SAME_STEP 分别记账（L181-199），任一子环境 done 时把 `{"r","l","t"}` 写进 `info["episode"]`、布尔掩码写进 `info["_episode"]`（L212-217）。`RecordVideo`（`rendering.py:L215`）每步从 `env.render()` 拿 `num_envs` 帧序列（L414-416），`_get_concat_frame_shape`（L378-396）枚举 1 到 √n 的因子分解找最接近目标宽高比的网格布局，`_concat_frames`（L398-409）拼成一张大帧，`stop_recording` 用 moviepy `ImageSequenceClip` 写 mp4（L532-535）；`HumanRendering`（L25）走 pygame 窗口，网格行列由宽高比贪心算法决定（L137-147）、cv2 逐帧缩放拼贴（L182-190）。`DictInfoToList`（`dict_info_to_list.py:L15`）把 dict-of-array 的批量 info 逆转换回 list-of-dict，靠 `_key` 布尔掩码恢复稀疏字段（L146-156），跳过下划线前缀键（L117-118）。

## 三、外部连接

**上游**是 `gymnasium/vector/` 引擎层：本目录大量消费 `vector.utils` 的四个空间工具——`batch_space`（单空间→批量空间）、`iterate`（批量→逐 env 切片）、`concatenate`（逐 env →批量拼装）、`create_empty_array`（预分配）——它们是 singledispatch 按 Space 类型实现的，撑起 2.2 节整条流水线。**横向**是标量 wrappers 层的双向依赖：方向一，`vectorize_*` 通过 `_SingleEnv` 复用机调用 `gymnasium.wrappers.transform_observation/action/reward` 里的 10 个标量类（`vectorize_action.py:L17`）；方向二，`ArrayConversion` 直接 import 标量层 `wrappers/array_conversion.py` 的转换函数与 `module_name_to_namespace`（`array_conversion.py:L11-15`）——批量与标量共享同一套 singledispatch 树遍历，这是刻意的一处实现两用。`RunningMeanStd` 同样来自共享的 `wrappers/utils.py:L33`（其 `update` 用 `np.mean(x, axis=0)` 沿批量维聚合，L43-48，Chan 并行合并算法见 L57-71）。**下游**是 jax 生态：`FunctionalJaxVectorEnv`（`envs/functional_jax_env.py:L103`）用 `jax.vmap` 把 FuncEnv 批量化（L153），产出 jax 数组，用户套 `JaxToNumpy`/`JaxToTorch` 转回主流框架；标量版 `FunctionalJaxEnv` 在 metadata 打 `"jax": True` 标记（L36-37），当前全仓唯一消费者是 `utils/env_checker.py:L449`（跳过 numpy 特有的检查）。注意一个常见误解：注册体系不会自动套 vector wrapper——`envs/registration.py` 中无任何对 `wrappers.vector` 的引用，所有包装都是用户显式叠加。测试锚点在 `tests/wrappers/vector/test_vector_wrappers.py` 与 `test_array_conversion.py`（图谱实证）。

## 四、数据流

**转换链**（jax 引擎 + torch 训练的典型管线）：`FunctionalJaxVectorEnv.step` 经 vmap 产出 `(num_envs, ...)` 的 jnp 数组 → `JaxToTorch.step` 把 torch 动作经 `from_dlpack` 转成 jax 数组（通常零拷贝）喂给内层 → 内层返回后五个输出逐个 `from_dlpack` 成 torch 张量并落到 `target_device`（GPU 训练时动作下发与观测上载各一次搬运，dict/tuple 嵌套结构由树遍历自动展开）→ 训练循环拿到的全是 torch 张量，反向传播梯度不穿过环境。

**变换链**（以 `ResizeObservation(envs, (28,28))` 为例）：构造期，假环境携带 `(96,96,3)` 的 single 空间喂给标量 `ResizeObservation`，后者算出新空间 `(28,28,3)`，`batch_space` 升维成 `(3,28,28,3)`，`same_out=False` 触发 `create_empty_array` 预分配。运行期每个 step：`(3,96,96,3)` 批量 obs → `iterate` 切成 3 张 `(96,96,3)` → 各自过 cv2 resize 成 `(28,28,3)` → `concatenate` 写进预分配缓冲 → deepcopy 交出。相同形状时（如 `DtypeObservation`）走就地路径，零分配。

**统计链**：`NormalizeObservation` 收到 `(num_envs, obs_dim)` 批量后**整批喂给** `obs_rms.update`——`np.mean(x, axis=0)` 沿第 0 维聚合，所以统计量形状是**单环境 obs 形状**（`stateful_observation.py:L120-123`），全部子环境**共享同一套均值方差**（这里纠正一个流传的误解：源码里没有 `(num_envs, ...)` 形状的逐 env 独立统计——共享设计让统计以 num_envs 倍速收敛，且各子环境本是同一环境的副本、分布一致，独立统计反而浪费样本）。`NormalizeReward` 则相反：折扣回报必须逐 env 独立累积（`(num_envs,)` 数组，`stateful_reward.py:L162-165`），统计量却是全局标量 `shape=()`（L113）——归一化分母对所有 env 统一。

**录像链**：`RecordVideo.step` 先推进 episode_id（NEXT_STEP 模式由 `has_autoreset = terminations[0] or truncations[0]` 驱动，`rendering.py:L470`——episode 边界只看第一个子环境）→ `episode_trigger` 判定是否开录 → `_capture_frame` 取 `num_envs` 帧（`record_first_only=True` 时只留第 0 帧，L418-419）→ 首帧时计算网格布局 → 拼大帧入 `recorded_frames` → 终局时 `ImageSequenceClip` 以 `render_fps` 写盘。

## 五、设计决策

**懒加载 vs 顶层导入**：`__init__.py` 把 26 个类劈成两半，唯一的判据是"源文件是否 import 重型框架"。PEP 562 `__getattr__` 的成本是每次属性访问多一次字典查找，换来 `import gymnasium` 的秒级提速；`TYPE_CHECKING` 分支保证 mypy/pyright 全程可见（顶部 `pyright: reportUnsupportedDunderAll=false` 注释即为此）。

**singledispatch vs isinstance 链**：转换函数面对的 obs 结构是开放集合（任意嵌套的 dict/tuple/namedtuple/标量/None），singledispatch 按 ABC 分派天然可扩展（第三方可为自定义容器注册新分支），递归结构让"容器的容器"免费获得支持；代价是 Array API 数组对象没有类型标记，只能挤进 Iterable 分支再用 `is_array_api_obj` 二次甄别（共享文件 L101-106 的注释坦言这是权宜）。

**DLPack 零拷贝与三层降级**：选 `from_dlpack` 而非 `np.asarray`/`torch.tensor` 是性能决策——跨框架搬运在批量 RL 里每步都发生，复制语义会把 num_envs×obs_dim 的数据量翻倍。但 DLPack 协议实现参差（torch 不支持 device 参数、jax 不支持 copy、只读缓冲崩溃），于是有了 TypeError/BufferError/RuntimeError 的瀑布降级（L120-145），每条注释都指向具体上游 issue——这是"标准先进、实现滞后"生态里写兼容层的标准姿势。

**假环境复用 vs 双份实现**：`_SingleEnv` 只带空间属性，因为标量 transform wrapper 的构造器**只**消费空间。这个约束是刻意维护的：一旦某个标量 wrapper 在构造期访问 `env.reset()` 之类，复用机立即失效。收益是 10 个向量薄壳总共只有几百行，且语义与标量版严格同步。

**autoreset_mode 协议的三档态度**：同一个协议，不同 wrapper 态度迥异——`VectorizeTransformObservation` 接受全部模式但为 SAME_STEP 专门处理 `final_obs` 逐 env 补变换（`vectorize_observation.py:L209-217`）；`NormalizeObservation` 只收 NEXT_STEP（统计连续性容不得终局步当场 reset 的歧义）；`RecordVideo` 收 SAME_STEP 但警告丢最后一帧（`rendering.py:L334-337`）。共同点是全部从 `metadata["autoreset_mode"]` 读模式、缺失即警告并假设 NEXT_STEP——v1.x 把 autoreset 从隐式行为提升为显式契约的缩影。

**就地写回 vs deepcopy**：`same_out` 双路径是热路径微优化——变换不改形状时以输入数组为拼接缓冲，省掉每步一次批量分配；`concatenate` 本身是空间感知的（Dict 空间按 key 写子数组），所以就地路径对嵌套结构同样成立。

**pickle 的模块字符串化**：`ArrayConversion.__getstate__`（`array_conversion.py:L116-128`）把 xp 模块降级为 `__name__` 字符串，`__setstate__` 用 `module_name_to_namespace` 反解——模块对象不可 pickle，这条协议让包装后的环境能进 `AsyncVectorEnv` 的进程管道（子进程 pickling 是刚需）。

## 六、新人提示

**包装顺序有铁律**：`DictInfoToList` 必须是最外层（`dict_info_to_list.py:L25` 钉版 `DictInfoToList(RecordEpisodeStatistics(envs))`），因为它把 dict-of-array 拆成 list-of-dict 后，任何期望向量 info 格式的内层 wrapper 都会 assert 失败（`common.py:L177-179` 的 isinstance 断言就是防线）。同理，`RecordEpisodeStatistics` 要求内层 info 是 dict，套反了直接崩。

**autoreset 适配先查表**：动手前确认你的 VectorEnv 的 `metadata["autoreset_mode"]`。用 `NormalizeObservation` 前若环境是 SAME_STEP 会直接 ValueError；想要归一化观测又想要 SAME_STEP，只能换实现。`RecordVideo` 在 NEXT_STEP 下 episode 边界由第一个子环境的 done 决定（`rendering.py:L470`）——子环境步调差异大时录制区间可能不精确，这是已知取舍。

**懒加载的 AttributeError 陷阱**：`from gymnasium.wrappers.vector import ArrayConversion` 走的是 `__getattr__`，此时才真正 `import jax`——如果用户环境没装 jax，报错的不是 import 语句而是**首次访问时**的 `ModuleNotFoundError`（`JaxToNumpy` 里 `jnp is None` 的 `DependencyNotInstalled` 检查，`jax_to_numpy.py:L35-38`，是第二道防线）。调试"明明 import 成功却用不了"时先想到这层。

**统计语义两个反直觉**：一，`NormalizeObservation` 的统计是跨 env 共享的（四节已纠偏），评估时记得 `update_running_mean = False` 冻结（`stateful_observation.py:L127-135`），否则评估数据污染训练统计；二，`NormalizeReward` 归一化的是**折扣回报方差**而非单步 reward（`stateful_reward.py:L173-175` 的分母是 `return_rms.var`），gamma 设错方向统计会漂。

**性能心智模型**：vectorize_* 的逐 env Python 循环在 num_envs 大时是瓶颈——能写出广播/vmap 版批量函数就用第一层 `TransformObservation` 直传，薄壳类只是便捷层。数组转换优先走 DLPack 零拷贝路径，但注意 torch 对只读缓冲会静默退化为先复制（五节降级链），从 jax jit 输出转 torch 时这个复制躲不掉。

**上手路径**：读码顺序建议 `__init__.py` → `vectorize_reward.py`（142 行最小完整样本）→ `vectorize_action.py` → `array_conversion.py` + 共享的 `wrappers/array_conversion.py` → `stateful_*` → `rendering.py`；跑通 `tests/wrappers/vector/test_vector_wrappers.py` 里的 doctest（`gym.make_vec("CartPole-v1", num_envs=3)` 五行内可复现）比读文档快。
