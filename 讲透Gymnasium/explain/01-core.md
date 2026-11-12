# 01 · core.py — Env 与 Wrapper：整个 Gymnasium 的契约心脏

> 源码：`gymnasium/core.py`（662 行）· 图谱定位：16 层第 1 层「核心契约与测试夹具」· 文件级 fanIn=40，符号级入边 134 条

## 一、角色定位：全仓唯一不可替代的契约层

如果只能读 Gymnasium 的一个文件，那就是 core.py。它在 662 行里用六个类规定了整个生态的"宪法"：什么是环境（`Env`）、什么是包装器（`Wrapper`）以及三个专用变体。其余一切——140 余个环境实现、几十个 wrappers、向量化体系——都是这部宪法的"地方法规"。

图谱证据（高扇入）：知识图谱中指向 `file:gymnasium/core.py` 的边共 134 条，来源分布为 `gymnasium/wrappers` 34 条（含 23 个 class 级继承边）、tests 20+ 条、`gymnasium` 包本体 12 条、`wrappers/vector` 9 条、classic_control 5 条、toy_text 4 条、box2d/mujoco/vector 若干。全仓没有任何其他模块接近这个集中度——`spaces/`、`registration` 都消费它而非被它消费。层级上，它在第 1 层只与 error.py（异常信号）、logger.py（告警出口）、tests/testing_env.py（mock 夹具）为伴，其上全部 15 层都要"实现或包装 core.Env"。

一句话定位：**Env 定义协议，Wrapper 定义组合协议的方式**——前者约束"环境长什么样"，后者约束"环境如何被无侵入地改造"。二进制 API 兼容的承诺（Gymnasium v1 的核心卖点）完全由这个文件背书。

## 二、内部结构：一个基类、四个包装器

### 2.1 Env：环境生命周期的最小完整定义（core.py:L28-295）

`class Env(Generic[ObsType, ActType])`（core.py:L28）是泛型基类，两个 TypeVar 都 `default=Any`（core.py:L22-23），允许 `Env[np.ndarray]` 这样的部分下标。它刻意**不用 ABC 抽象方法**，而是"文档契约 + `raise NotImplementedError`"（core.py:L122、L205）——子类忘实现时在调用处才炸，这是为了允许 duck-typing 式的第三方环境接入。

**类属性三分法**（core.py:L64-77）是理解约定的钥匙：

| 分组 | 属性 | 默认值 | 谁来设置 |
|---|---|---|---|
| SOME 子类设置 | `metadata`（L65） | `{"render_modes": []}` | 支持渲染的环境 |
| | `render_mode`（L67） | `None` | 支持渲染的环境 |
| | `spec`（L68） | `None` | `gymnasium.make` 自动填充 |
| ALL 子类必须设置 | `action_space`（L71）/`observation_space`（L72） | 无默认，纯注解 | 每个环境 |
| 框架内部创建 | `_np_random`（L75）/`_np_random_seed`（L77） | `None` | reset 或首次访问 |

**四大生命周期方法**：

- `reset(*, seed=None, options=None) -> (ObsType, dict)`（core.py:L124-129）：keyword-only 签名。基类实现只有两行（core.py:L170-171）——`seed` 非 None 时调 `seeding.np_random(seed)` 重建 PRNG。这就是文档反复强调"自定义环境 reset 第一行必须是 `super().reset(seed=seed)`"（core.py:L139）的全部原因：种子逻辑在基类，不调就断链。
- `step(action) -> (obs, reward, terminated, truncated, info)`（core.py:L79-81）：五元组。文档注明 v0.26 的变更理由——"critical for reinforcement learning bootstrapping"（core.py:L89-91）。
- `render() -> RenderFrame | list[RenderFrame] | None`（core.py:L173）：**无参数**，完全由 `__init__` 时确定的 `render_mode` 驱动（约定见 core.py:L184-195：`None` 不渲染、`"human"` 持续显示且返回 None、`"rgb_array"` 返回 (x,y,3) ndarray、`"ansi"` 返回字符串；`*_list` 变体靠 RenderCollection 包装器实现）。
- `close()`（core.py:L207-213）：幂等清理，`pass` 即默认。

**辅助设施**：`unwrapped` property 剥掉所有包装（core.py:L215-222，Env 自身返回 self）；`np_random`/`np_random_seed` 双惰性 property（core.py:L224-247）；`np_random` setter 把 seed 标记为 -1 表示"不可恢复"（core.py:L249-259，因为无法从 Generator 反推 seed）；`__str__` 优先用 `spec.id` 标识环境（core.py:L261-270）；`__enter__/__exit__` 支持 with 语句自动 close（core.py:L272-280）；`has/get/set_wrapper_attr` 三件套（core.py:L282-295）为包装链提供受控属性通道。渲染返回值由模块级别名 `RenderFrame = str | np.ndarray | tuple[...]` 统一（core.py:L25），是 render 契约的类型化表达。

### 2.2 Wrapper：显式委托的通用包装基类（core.py:L302-543）

```python
class Wrapper(Env[WrapperObsType, WrapperActType],
              Generic[WrapperObsType, WrapperActType, ObsType, ActType]):
```
（core.py:L302-305）——注意这个**四参数泛型**：前两个是"包装器对外呈现"的类型（它自己作为 Env 的面孔），后两个是"内层环境"的类型。类型级就把"变换前/变换后"编码清楚了。

`__init__`（core.py:L322-336）做四件事：存 `self.env`；`isinstance(env, Env)` 校验（core.py:L329-330，包装非 Env 对象立刻 TypeError）；初始化三个"可选覆写槽" `_action_space/_observation_space/_metadata = None`（core.py:L332-334）；`_cached_spec` 缓存（core.py:L336）。

核心机制是**双通道透传**：

1. **方法通道**——`step/reset/render/close` 显式一行委托（core.py:L338-356，如 `return self.env.step(action)`）。
2. **属性通道**——property + 槽位：`action_space` 访问时若 `_action_space is None` 则读 `self.env.action_space`，否则读自己的槽（core.py:L484-491）；setter 只写本地槽（core.py:L493-495）。`metadata` 同构（core.py:L510-519）。而 `render_mode`、`np_random`（含 setter）是无槽纯转发（core.py:L521-533）——这两项语义上必须归内层环境所有。

`unwrapped` 递归下钻（core.py:L363-369），`__str__` 递归拼接整条链——`f"<{type(self).__name__}{self.env}>"`（core.py:L471-473）让嵌套 wrapper 打印成 `TimeLimit<OrderEnforcing<PassiveEnvChecker<CartPole-v1>>>>` 的洋葱形态，一眼可见包装顺序。`spec` 是最精巧的 property（详见第五节）。`has/get/set_wrapper_attr` 的链式版本先查自己再递归 env，找不到时把 AttributeError 重新包装成本层语境抛出（core.py:L427-444）；`set_wrapper_attr` 带 `force` 语义——链上不存在该属性时，`force=True` 才在当前层创建（core.py:L446-469）。

文件末尾的 `_np_random` property（core.py:L535-543）是个"活化石"防御：直接访问 `wrapper._np_random` 会收到明确报错，引导你改用 `.np_random`（转发）或 `.unwrapped._np_random`。其 docstring 提到的 `__getattr__`（core.py:L537）是 Gym 老版本透传方案的遗迹，详见第五节。

### 2.3 三个专用变换包装器（core.py:L546-662）

三者都是"覆写一个入口方法 + 暴露一个抽象变换函数"的模板方法模式（Template Method）：

| 类 | 泛型（L546/L590/L625） | 覆写点 | 抽象函数 |
|---|---|---|---|
| `ObservationWrapper` | `[WrapperObsType, ActType, ObsType, ActType]` | reset（L564-569）与 step（L571-576）出口处对 obs 施加变换 | `observation(obs)`（L578） |
| `RewardWrapper` | `[ObsType, ActType, ObsType, ActType]` | 仅 step 出口对 reward 施加变换（L606-611） | `reward(r)`（L613） |
| `ActionWrapper` | `[ObsType, WrapperActType, ObsType, ActType]` | 仅 step 入口对传入 action 施加变换（L647-651） | `action(a)`（L653） |

泛型参数精确表达了"哪个方向被变换"：ObservationWrapper 只有第一个（外层 obs）与第三个（内层 obs）不同；ActionWrapper 只有第二个与第四个不同；RewardWrapper 四个全同（reward 只是 SupportsFloat 标量，无需参数化）。写自定义变换包装器时继承这三者，只需实现单个纯函数，不必碰五元组拆装。

## 三、外部连接：谁在消费这份契约

**registration/make 的默认包装链**。`gymnasium.make` 从内到外依次套：`PassiveEnvChecker`（最低层，registration.py:L805）→ `OrderEnforcing`（禁止 step-before-reset，registration.py:L809）→ `TimeLimit`（max_episode_steps 触发 truncated，registration.py:L814-817）→ 用户 additional_wrappers → `HumanRendering`/`RenderCollection`（render_mode 变体支持，registration.py:L828-830）。整条链的每一环都是一个 core.py Wrapper 子类实例；make 返回给你的"环境"，实际上永远是这棵包装树的最外层。

**全部环境族直接继承 Env**。图谱中 classic_control（5 条 class 边）、toy_text（4）、box2d（3）、mujoco（1）等环境类的第一行都是 `class XxxEnv(Env)`；`tests/testing_env.py` 的 `GenericTestEnv`（fanIn=45）同样是 Env 子类，被 20+ wrapper 测试文件复用——mock 也必须守法，这是契约层最好的证明。

**vector 体系的平行镜像**。`gymnasium/vector/vector_env.py` 的 `VectorEnv`（vector_env.py:L49）**不继承** Env，而是复制了同一套约定：`render_mode` 类属性（L131）、`_np_random/_np_random_seed`（L141-142）、reset 中同样的 `seeding.np_random(seed)` 两行（L172）、同样的 `np_random` 惰性 property（L250-258）。这是刻意的 API 同构——让用户在单环境与批量环境之间零成本切换，也让 SyncVectorEnv 能把 N 个 Env 装进一个符合 Env 直觉的容器。

**spec 自描述闭环**。`Wrapper.spec` 产出的 `additional_wrappers` 元组被 `registration.py` 的 `make`/`EnvSpec` 重建逻辑消费（registration.py:L779-795 会对比重建出的 spec 与保存的 spec 是否一致）——core.py 与 registration.py 构成"构造↔重建"的双向依赖（后者 import 前者，前者在方法内延迟 import `WrapperSpec`，core.py:L388，避免循环导入）。

## 四、数据流：一次完整回合经过 core.py 的样子

**种子链（惰性初始化）**：`make` 或直接构造时 PRNG 并不存在（`_np_random = None`，core.py:L75）。首次 `env.reset(seed=42)` → 基类 reset 的两行（core.py:L170-171）调 `seeding.np_random(42)` 同时生成 Generator 和 seed 记录。此后 `env.step` 内部用 `self.np_random.uniform(...)` 采样——若从未 reset 过，property 兜底用系统熵源初始化（core.py:L245-247），保证"总能用"但不可复现。`seed=None` 二次 reset **不会**重置已有 PRNG（core.py:L149-152 文档明确），这是"初始化后种一次、永不再种"范式的语义基础。包装链上 `wrapper.np_random` 逐层转发（core.py:L526-529），整条链共享内层那一个随机源——TimeLimit 截断、环境采样不会各自为政。

**回合数据流**：`reset` 返回 `(obs, info)` 二元组（core.py:L129）——v0.25 起强制带 info，旧的 `return_info` 参数被移除。agent 循环 `step(action)`，每步得到五元组 `(obs, reward, terminated, truncated, info)`（core.py:L80-81）。`terminated or truncated` 为真时必须 reset（core.py:L84）。文档要求每步返回**新对象**而非复用 buffer（core.py:L117-120），因为用户通常把数据存进 replay buffer——`gymnasium.utils.env_checker.check_env` 会机械检查这一点。结束时 `close()`（或 with 块退出，core.py:L276-280）幂等清理。

**spec 数据流（反向）**：访问 `wrapper.spec` 时（core.py:L371-407）：先查 `_cached_spec` 缓存（L374-375）→ 取 `self.env.spec`（递归，最终到 make 注入的原始 EnvSpec）→ 若本层继承 `RecordConstructorArgs` 则取 `_saved_kwargs` 并 deepcopy 弹出 `env` 键（L380-385）→ 构造 `WrapperSpec(name, entry_point, kwargs)`（L390-394）→ deepcopy 父 spec 并追加到 `additional_wrappers`（L397-399）→ deepcopy 失败则告警返回 None（L400-404）。于是从最外层读一次 `.spec`，就能拿到能完整重建整棵包装树的配方。

## 五、设计决策：五个值得咀嚼的取舍

**1. 显式委托替代 `__getattr__` 透传——本文件最重要的演进**。Gym 老版本的 Wrapper 用 `def __getattr__(self, name): return getattr(self.env, name)` 一行实现"什么都能透传"。Gymnasium 换成了现在这份"每个方法一行委托 + 每个属性一个 property"的笨办法（core.py:L338-356、L484-533）。代价是基类更长，收益是决定性的：其一，**IDE 补全与 mypy/pyright 可见性**——`__getattr__` 对静态分析完全不可见，显式 property 让 `wrapper.action_space` 有精确类型；其二，**pickle 安全**——unpickle 早期阶段实例 `__dict__` 未填满，`__getattr__` 会拦截 `__setstate__` 等协议属性查找，造成著名的诡异崩溃；其三，**文档与校验点**——每个可透传项在源码里有一行，review 时一目了然。core.py:L536-543 那个"永远不会运行"的 `_np_random` property 就是迁移期的护栏活化石：docstring 里的 `__getattr__` 字样（core.py:L537-539）记录了 @property 定义之后 `__getattr__` 不再被触发的坑，今天它的作用只剩拦截裸访问并给出迁移指引。

**2. 槽位式可选覆写**。Wrapper 不要求子类重写 property，而是给三个 `None` 槽（core.py:L332-334）：None 即透传，赋值即覆写（setter 只写本地，core.py:L493-495）。子类一行 `self.observation_space = new_space` 就完成覆写，比"必须重写 getter"轻得多，且保持了读取路径的统一。

**3. render_mode 声明制**。v0.25 起 render 无参（core.py:L200-203），模式在构造时定死。动机：渲染资源（pygame 窗口、OpenGL 上下文）生命周期随环境而非随调用（core.py:L180-182 明确要求在 `__init__` 初始化）；批量创建上千环境不会意外弹窗；`metadata["render_modes"]`（core.py:L65）作为能力清单让 make 能预先校验并自动附加 RenderCollection/HumanRendering。

**4. 五元组替代 done**。单一 `done` 把 MDP 内在终止与时间截断混在一起，而二者对 TD bootstrap 语义完全不同：terminated 时 bootstrap 目标应为 0，truncated 时应为 V(s')。docstring 原话："critical for reinforcement learning bootstrapping algorithms"（core.py:L89-91）。旧式 `info["TimeLimit.truncated"]` 补丁方案（core.py:L110-111）被正式废弃。

**5. spec 自描述与防御性 deepcopy**。环境"知道自己是怎么被造出来的"使得 vector 化、检查器、保存/加载都能从 `.spec` 重建一切。拼接时 deepcopy 父 spec（core.py:L398）是为了避免多 wrapper 共享同一个 spec 元组的引用污染；失败路径不抛异常而是 logger.warn + 返回 None（core.py:L400-404）——spec 是元信息，不值得让训练因此崩溃。配合 `RecordConstructorArgs`（core.py:L380-385）解决"wrapper 重建时拿不到用户当初的 kwargs"的问题：约定 wrapper 把构造参数存进 `_saved_kwargs`。

## 六、新人提示：六个高频翻车点

1. **忘调 `super().__init__(env)`**。core.py:L317 文档原话 "don't forget to call super().__init__(env)"。漏掉的直接后果是 `self.env` 不存在，任何透传访问触发 `AttributeError`——而且因为 property 都引用 `self.env`，报错栈会指向 core.py 而非你的漏调处，极具迷惑性。
2. **自定义环境 reset 忘调 `super().reset(seed=seed)`**（core.py:L139）。后果：`env.reset(seed=42)` 种子不生效、`np_random` 走熵源兜底、实验不可复现。PassiveEnvChecker 会检查 reset 签名必须含 `seed` 且默认值必须为 `None`（passive_env_checker.py:L255-265）。
3. **render_mode 三联坑**：忘了在子类 `metadata["render_modes"]` 里声明（checker 会告警 "No render modes was declared"，passive_env_checker.py:L407-410）；`__init__` 不接收/不校验 `render_mode` 参数（声明制的另一半义务）；render 返回类型与模式不符（如 rgb_array 模式返回 None，checker 在 passive_env_checker.py:L353-360 逐模式校验）。
4. **在 wrapper 上裸访问 `_np_random`** 会直接 AttributeError（core.py:L541-543）。正确姿势：`.np_random`（property 转发到内层，core.py:L526-529）或 `.unwrapped._np_random`。
5. **ObservationWrapper 改了 obs 忘改 space**：变换后的观测不再落在内层 `observation_space` 里，必须在 `__init__` 里 `self.observation_space = ...`（core.py:L552-553 文档明确），否则 checker 与下游库的空间校验全炸。ActionWrapper 同理（core.py:L630-633）。
6. **返回复用 buffer**：step/reset 返回同一可变对象会让 replay buffer 里的历史数据被后续步骤原地改写（core.py:L117-120）。`check_env` 有专检，别赌运气。

**阅读顺序建议**：先读 Env 的 docstring（core.py:L29-62，本身是一份微型教程）→ 手写一个继承 ObservationWrapper 的灰度变换 wrapper 感受模板方法 → 再回头精读 `Wrapper.spec`（core.py:L371-407）体会自描述设计——这是全文件密度最高的一段。
