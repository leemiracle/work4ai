# 07 - 观测变换 wrapper 全解：transform_observation.py 与 stateful_observation.py

> 源码锚点：`gymnasium/wrappers/transform_observation.py`（919 行，10 个类）、`gymnasium/wrappers/stateful_observation.py`（651 行，5 个类），兼及 `transform_action.py` / `transform_reward.py` 的对称结构。行号以当前 main 分支为准。

## 一、角色定位

观测变换 wrapper 是 Gymnasium 里最常被用户触碰的一层：环境产出原始 observation，学习算法想要"另一个样子"的 observation，中间的全部落差都由这一族 wrapper 填平。文件本身是对 `TransformObservation`（`transform_observation.py:L43`）一个基类的九个特化——按老命名习惯叫 "lambda wrapper"：全部变换逻辑被表达成一个函数，构造期与空间推导一起交给父类，运行期只做函数调用。

需要先钉一个类清单勘误：模块 docstring 与常见记忆中的清单并不一致。`transform_observation.py` 实际导出 10 个类（`__all__` 见 `transform_observation.py:L27-38`）：`TransformObservation` / `FilterObservation` / `FlattenObservation` / `GrayscaleObservation` / `ResizeObservation` / `ReshapeObservation` / `RescaleObservation` / `DtypeObservation` / `AddRenderObservation` / `DiscretizeObservation`。而社区常用的 `DelayObservation`、`TimeAwareObservation`、`FrameStackObservation`、`NormalizeObservation`、`MaxAndSkipObservation` 五个**不在本文件**，在 `stateful_observation.py:L35/L106/L305/L465/L565`——因为它们需要跨 step 的内部状态（队列、计数器、统计量），被归入"有状态"文件。此外 docstring（`transform_observation.py:L11`）写的 `RenderObservation` 是笔误，真名是 `AddRenderObservation`。

与它对称的还有两个小文件：`transform_action.py:L25` 的 `TransformAction`（特化为 `ClipAction`、`RescaleAction` 等，变换方向是"用户动作进环境前"）与 `transform_reward.py:L21` 的 `TransformReward`（特化为 `ClipReward`）。三个文件构成 obs/action/reward 三条切面的镜像三兄弟。

## 二、内部结构

### 模板方法骨架：observation() 钩子

一切从 `core.py:L546` 的 `ObservationWrapper` 说起。它继承四参泛型 `Wrapper[WrapperObsType, ActType, ObsType, ActType]`（前两个是 wrapper 自己的 obs/act 类型，后两个是内层 env 的），固定了模板方法：

- `reset()`（`core.py:L564-569`）：先调 `env.reset()`，再对返回的 obs 调 `self.observation(obs)`；
- `step()`（`core.py:L571-576`）：先调 `env.step()`，再对 obs 调 `self.observation(obs)`，reward/terminated/truncated/info 原样透传；
- `observation()`（`core.py:L578-587`）：抽象钩子，默认 `raise NotImplementedError`。

子类只需覆写一个纯函数式的钩子，step/reset 的编排永不用碰——15 个观测变换类里有 12 个走这条路。

`TransformObservation`（`transform_observation.py:L43-97`）把这个钩子做到最简：构造函数收 `func` 与 `observation_space`（v1.0.0 起必填，见 change log L69），钩子体就一行 `return self.func(observation)`（L95-97）。

### 九个特化类的统一套路

`FilterObservation`（L100）是套路范本：构造期 isinstance 分派 `Dict`/`Tuple` 两个分支（L144/L181），逐条校验 `filter_keys` 合法性（字符串键存在性 L150-163、整数索引去重 L186-187），随后用 `spaces.Dict({key: ...})` 机械推导新空间（L165-168），最后把变换逻辑写成闭包委托父类——`func=lambda obs: {key: obs[key] for key in filter_keys}`（L177），Tuple 分支对应 `tuple(obs[key] ...)`（L214）。其余类同构：

| 类 | 行号 | 变换闭包要点 | 空间推导 |
|---|---|---|---|
| FlattenObservation | L225 | `spaces.utils.flatten`（L260） | `flatten_space`（L261） |
| GrayscaleObservation | L265 | BT.709 加权 `0.2125/0.7154/0.0721` 乘加求和（L332-337） | Box(H,W) 或 (H,W,1)（`keep_dim`，L322-343） |
| ResizeObservation | L354 | `cv2.resize(...INTER_AREA).reshape(...)`（L442-444） | `shape + 原shape[2:]`（L430-435） |
| ReshapeObservation | L449 | `np.reshape(obs, shape)`（L512） | low/high 先 ravel 再 reshape（L500-505） |
| RescaleObservation | L517 | `rescale_box` 返回的 `forward` 闭包（L561-567） | 同函数产出的新 Box |
| DtypeObservation | L570 | `new_observation_space.dtype.type(obs)`（L638） | 按 Box/Discrete/MultiDiscrete/MultiBinary 四分支重建（L602-628） |
| AddRenderObservation | L643 | `lambda _: self.render()` 或 Dict 合并（L733/L748/L762） | 像素 Box 探测后拼 Dict（L728-758） |
| DiscretizeObservation | L767 | **不委托父类**，自己覆写 `observation()`（L875-889） | `Discrete(prod(bins))` 或 `MultiDiscrete`（L870-873） |

`DiscretizeObservation` 是唯一例外：它直接 `gym.ObservationWrapper.__init__(self, env)`（L854）并自写钩子。原因有二：钩子需要读 `self.bin_edges`（L865-868 由 `np.linspace` 预生成）做 `np.digitize` 分桶（L882-885），闭包捕获也可但可读性差；二是它还要提供逆变换 `revert_observation()`（L891-905，返回观测所在 bin 的上下边缘），这超出了"一个 lambda"的表达范围。

### 有状态五类：越出钩子的部分

`stateful_observation.py` 的五个类展示了何时必须放弃纯钩子：

- `DelayObservation`（L35）：钩子内维护 `deque` 队列（L96-103），未满 `delay` 长度时返回 `create_zero_array` 零观测（L103）；额外重写 `reset()` 仅为了清空队列（L88-94）。
- `TimeAwareObservation`（L106）：钩子由三个闭包组合——`_time_preprocess_func`（归一化时间 L220-225）、`_append_data_func`（Dict 加键 / Tuple 追加 / 包成 Dict，L229-244 三分支）、`_obs_postprocess_func`（可选 flatten，L247-256）；重写 `step()` 只为 `self.timesteps += 1`（L284），重写 `reset()` 归零（L300）。
- `FrameStackObservation`（L305）与 `MaxAndSkipObservation`（L565）：干脆继承 `gym.Wrapper` 而非 `ObservationWrapper`（L306/L566），完全自管 step/reset——前者的堆叠语义（reset 时整队列填充、step 时滚动追加）和后者的一次动作多次 step（L639-647 循环 + 奖励累加 + 末两帧取 max，L648）都无法塞进"逐观测纯函数"的钩子模型。
- `NormalizeObservation`（L465）：仍是钩子模式，但钩子有副作用——先 `self.obs_rms.update(np.array([observation]))`（L559）再返回标准化值（L560-562）。

## 三、外部连接

**向上：core.py 模板与属性透传。** `Wrapper` 把 `observation_space` 做成 property（`core.py:L497-508`）：子类在 `__init__` 里 `self.observation_space = 新空间` 触发 setter 存入 `_observation_space`，未设置时回退 `env.observation_space`。这是所有变换类"改空间"的唯一正规通道。

**向下：spaces 包的空间代数。** `flatten_space` / `flatten`（`spaces/utils.py`）支撑 Flatten 与 TimeAware；`Box`/`Dict`/`Tuple` 构造器被九个类的空间推导反复调用。

**横向工具：`wrappers/utils.py` 三件套。** `rescale_box`（L160-266）是 RescaleObservation 的数学内核：校验无穷界必须对齐无穷界（L209-216），推导逐元素仿射系数 `gradient = (new_max-new_min)/(high-low)`、`intercept`（L241-251），返回 `(new_box, forward, backward)` 三个产物——backward 逆变换留给需要还原的场景。`RunningMeanStd`（L33-54）是 Normalize 的统计内核，注释直接引用 Wikipedia "Algorithms for calculating variance / Parallel algorithm"（L36），即 Chan 并行方差合并公式，实现于 `update_mean_var_count_from_moments`（L57-71）。`create_zero_array`（L74-157）是 `functools.singledispatch` 分发器：为每种空间注册"最接近零的合法样本"，Box 分支还用两个 `np.where` 修正 low>0 或 high<0 的区间（L100-101）。

**Dict/Tuple 的逐键递归分发。** 真正的泛型分发中枢在 `gymnasium/vector/utils/space_utils.py`：`batch_space`（L51，singledispatch）、`concatenate`（L395）、`iterate`（L306）、`create_empty_array`（L468）四个函数族各自按空间类型注册实现，其中 `_batch_space_dict`（L129）与 `_concatenate_dict`（L450）对每个键**递归调用自身**——这就是"Dict 空间逐键变换"的公共底座。`batch_space(Box, n)` 的语义是 `np.tile` 前插 n 维（L80-84），`concatenate` 对 Box 即 `np.stack(items, axis=0, out=out)`（L426-431）。

**vector 镜像。** `wrappers/vector/vectorize_observation.py` 是 vector 版对应物（v1.x 已从 transform_observation.py 改名）。除 `TransformObservation` 的 vector 版（L20）和九个镜像类（`FilterObservation` L246、`GrayscaleObservation` L314 等），关键新增 `VectorizeTransformObservation`（L104）：它造一个假单代理环境 `_SingleEnv`（L151-156），把**任意单代理变换 wrapper 实例化在假环境上**（L170-172）借其空间推导，再用 `batch_space(single_space, num_envs)` 推批量空间（L173-176）；运行时 `observations()` 用 `iterate` 把批量观测拆成单条、逐条调 `wrapper.func`、再 `concatenate` 拼回（L206-224）——与标量版严格镜像。注意哪些类**没有** vector 版：`DelayObservation`、`TimeAwareObservation`、`FrameStackObservation`、`MaxAndSkipObservation`、`AddRenderObservation` 的 docstring 都明写 "No vector version of the wrapper exists"。

**可选依赖与序列化。** `ResizeObservation` 构造期才 `import cv2`，失败抛 `DependencyNotInstalled`（L419-424）。全部 15 个类混入 `gym.utils.RecordConstructorArgs`（如 L85-87），把构造参数录制下来，供 pickle / `env.copy` / `check_no_unwrapped_access` 等场景重建 wrapper 栈。

## 四、数据流

以一条最常用的图像预处理的完整数据流串起来（外层到内层：`FrameStack(Resize(Grayscale(env)))`）：

1. 用户调 `wrapper.step(action)`，最外层 `FrameStackObservation.step`（`stateful_observation.py:L420-437`）先透传动作给内层。
2. `GrayscaleObservation.observation` 收到 HWC uint8 帧，执行 `np.sum(np.multiply(obs, [0.2125, 0.7154, 0.0721]), axis=-1)`——沿最后一维（通道维）加权求和压成 (H,W)，`keep_dim=True` 时再 `np.expand_dims(axis=-1)` 恢复 (H,W,1)（L329-351）。
3. `ResizeObservation.observation` 调 `cv2.resize(obs, self.cv2_shape, interpolation=cv2.INTER_AREA)` 后 `reshape` 到目标形状（L442-444）。两个防御点：`cv2_shape` 存的是 `(shape[1], shape[0])` 反转对（L427-428，注释自嘲 "for some reason, cv2.resize will return the shape in reverse"）；`reshape` 兜住 OpenCV 对单通道图会悄悄丢掉 channel 维的行为（L441 注释）。
4. 回到 FrameStack：新观测 `obs_queue.append(obs)`（L432），`concatenate(env.observation_space, self.obs_queue, self.stacked_obs)` 把 deque 拼进预分配缓冲（L434-436），最后 **`deepcopy`** 一份返回（L434/L459）——因为 `stacked_obs` 是复用缓冲，不拷贝的话用户持有的引用会在下一步被覆写。
5. 空间侧：`GrayscaleObservation` 构造期三重校验（Box、shape[-1]==3、uint8 且 0-255，L300-318）后建 (H,W,1) Box；`ResizeObservation` 校验 2D/3D、uint8、bounds（L384-400）后建 `shape + env.observation_space.shape[2:]` 的 Box——**只替换 H/W 两维，通道维及其后原样保留**，这是 HWC 约定的直接体现；`FrameStackObservation` 构造期 `batch_space(env.observation_space, n=stack_size)`（L411）——Box 得到 `(4, 96, 96, 3)` 这种前插 stack 维的形状，Dict 则逐键各自前插维（结构不变），Tuple 递归逐槽位 batch。
6. reset 分支（L439-462）：`padding_type="reset"`（默认）时先把 `padding_value` 更新为本次 reset 观测（L453-454），再填满 `stack_size-1` 个 padding + 1 个真观测——所以 reset 返回的是"首帧重复 N 次"；`"zero"` 用 `create_zero_array` 的合法零样本（L397），自定义值须通过 `padding_type in env.observation_space` 包含检查（L398-399）。

`NormalizeObservation` 的数据流是另一型：构造期建 `RunningMeanStd(shape, float32)`（L540-542，初始 mean=0、var=1、count=1e-4），观测空间直接设为 `Box(-inf, inf, float32)`（L533-538）——因为标准化后的值理论上无界。每个观测经过钩子时**先更新统计再标准化**：`(obs - mean) / sqrt(var + epsilon)`（L560-562）。这是纯在线（online）流式统计：Chan 合并公式让 mean/var/count 可以从任意历史时刻无损续算（`update_from_moments` L50-54 也因此公开，供外部批量注入）；没有离线预计算选项，想离线只能自己调 `update_from_moments` 喂大数据集的矩。

`RescaleObservation` 数据流最轻：仿射变换 `gradient * obs + intercept` 逐元素一次乘加（`utils.py:L260-261`），无状态、可逆（`backward` L263-264）。

## 五、设计决策

**1. 钩子优先，越界须有据。** `observation()` 模板方法的收益是 step/reset 编排零重复；12/15 个类守住了这条线。四个越界者各有明确理由：Delay/TimeAware 只需增强 reset（清队列/归零计数）；FrameStack 的 reset 语义（整队列重建 + padding）与 step 语义（滚动追加）根本不同；MaxAndSkip 一次 step 内多次 `env.step`。判断标准清晰：变换是否只依赖"当前这一个观测"。

**2. LazyFrames 之死：正确性换内存。** 任务要点常提"lazy frames"，但 change log 钉死了历史：v1.0.0 "Rename to `FrameStackObservation` and **remove lz4 and `LazyFrame` support** along with adding the `padding_type` parameter"（`stateful_observation.py:L360-363`）。老 Gym 用 LazyFrame 延迟拷贝省 4 倍内存；Gymnasium v1 改为每次 `deepcopy(concatenate(...))` 立即物化——API 更可预测（返回普通 ndarray，无框架兼容问题），代价是每步全量复制。内存敏感场景的官方答案是去 vector 生态或 SB3 的 `VecFrameStack`。

**3. 在线统计的三个防线。** `NormalizeObservation` 的数值健壮性靠：epsilon 参数必须严格正（L520-523，否则超出方差时静默产出 NaN，注释 L517-519 讲明动机）；`RunningMeanStd` 初始 count=1e-4 而非 0（避免除零）；标准化时分母 `sqrt(var + epsilon)` 双保险。`update_running_mean` property（L546-554）支持评估期冻结统计——这是 v1.0.0 专门加的特性。

**4. 空间代数而非手工声明。** 九个类的 `observation_space` 全部由 `flatten_space`/`batch_space`/`rescale_box` 从原空间机械推导，用户无法（也不需要）手写新空间。这保证了空间与变换函数的一致性：`space.contains(func(obs))` 成立是构造期推导的数学必然，不是运行期赌注。`TransformObservation` 的 `observation_space` 必填参数（L76）是唯一逃生口，v1.0.0 才收紧为必填。细节见 `DtypeObservation` 的 L609-615：`Discrete` 空间被映射成 `shape=()` 的标量 `Box`——这是九个特化里唯一连空间**类别**都改掉的变换（其余只改参数），docstring 用 "Note" 明示了四种兼容类型（L576-577）。同样值得留意的是 `FilterObservation` 重建 Dict 时透传了 `sort_keys`（L167），`TimeAwareObservation`（L236）与 `AddRenderObservation`（L743）也如此——键序一致性被当成 Dict 变换的隐性契约。

**5. 命名共识：动词 + Observation，v1.0 去 Wrapper 后缀。** Filter/Flatten/Resize/Reshape/Rescale/Discretize/AddRender 全是动词或动词短语开头；两处历史纠正：`GrayScaleObservation`→`GrayscaleObservation`（L289-290）、`PixelObservationWrapper`→`AddRenderObservation`（L686-687），所有 `*Wrapper` 后缀在 v1.0.0 统一摘除。形容词类（Grayscale/Dtype）是少数例外。

**6. 泛型四参签名。** `Wrapper[WrapperObsType, ActType, ObsType, ActType]` 把"wrapper 看到的类型"与"env 看到的类型"分开编码；`ObservationWrapper` 固定后两个 ActType 相等（动作不改），`TransformObservation[WrapperObsType, ActType, ObsType]`（L44）则允许观测类型漂移——这正是 lambda 变换的本质承诺。

**7. 三兄弟对称。** `transform_action.py` 的 `action()` 钩子（L74-76）在动作**进环境前**反向拦截（`core.py:L625` ActionWrapper 的 step 先变换再下发）；`transform_reward.py` 的 `reward()` 钩子（L58-64）只改 step 返回的标量。三文件结构逐行同构：基类收 func + 空（间）参数、特化类构造期校验 + 委托、`ClipAction`（L79）与 `ClipReward`（L67）互为镜像。

## 六、新人提示

- **构造即有副作用**：`AddRenderObservation.__init__` 会真的调一次 `env.reset()` 和 `env.render()` 来探测像素形状（L722-723）——包 wrapper 本身消耗一次 RNG 种子流，做种子对照实验时别忘了。
- **`FilterObservation` 的 Tuple 分支校验有漏洞**：越界检查写成 `0 < key and key >= len(...)`（L190/L195），`key=0` 和负索引都会绕过检查，传 `filter_keys=[0, 99]` 不会在构造期报错，运行期才炸。Dict 分支无此问题。
- **图像三件套的硬门槛**：`GrayscaleObservation` 与 `ResizeObservation` 都强制 uint8 且 bounds 0-255（L311-318/L392-396）。浮点图像环境得先 `DtypeObservation` 或自定义变换。Gymnasium 图像是 **HWC** 约定，进 PyTorch（CHW）要自己 transpose，这两个 wrapper 不会替你做。
- **Normalize 的冷启动偏差**：初始 var=1、mean=0，前几百步标准化基本是"原样除以 1"，分布远非 N(0,1)；且 docstring 明确警告（L477-479）换了策略后旧统计失效。惯例：随机策略预热数千步再开训；评估前设 `update_running_mean = False`。
- **FrameStack 的性能账**：每步一次 `concatenate` + 一次 `deepcopy`，(4,96,96,3) 的 uint8 无感，(4,480,640,3) 以上就该考虑 vector 版生态或自己写惰性堆叠。
- **`TimeAwareObservation` 的前置条件**：环境必须有 `spec.max_episode_steps` 或栈内存在 `TimeLimit`，否则构造期直接 ValueError（L211-214）——`gym.make` 默认会加 TimeLimit，但裸 `Env` 实例不会。
- **组合顺序即语义**：`FrameStack(Resize(Grayscale(env)))` 与 `Resize(FrameStack(env))` 空间形状都合法但语义完全不同；Normalize 通常放最外层（对最终观测标准化），图像链则内紧外松。wrapper 栈没有全局一致性检查，顺序错了只能靠 `observation_space` 形状自查。
- **读源码学模式**：想写自定义观测预处理，从 `FilterObservation`（L100-222）抄结构——构造期校验、推导空间、闭包委托三段式；需要状态或改 reset/step 行为时，参考 `DelayObservation`（队列）与 `FrameStackObservation`（完全自管）的越界姿势。两类根基（`TransformObservation` 与 `ObservationWrapper`）合计不到百行，却承载了整个生态的预处理习惯——读懂它们，SB3/CleanRL 的 wrapper 栈也就通了。

---

*本篇行号锚均从 main 分支源码逐一核实；`TransformObservation` 家族与 stateful 五类的分野、LazyFrame 移除史、vector 镜像的假环境技巧是本文件群最值得带走的三个知识点。*
