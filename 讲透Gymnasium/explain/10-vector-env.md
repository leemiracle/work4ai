# 10 · vector/vector_env.py + sync_vector_env.py — 向量化环境的契约心脏与串行实现

> 源码：`gymnasium/vector/vector_env.py`（668 行）· `gymnasium/vector/sync_vector_env.py`（422 行）· 兼述 `async_vector_env.py`（977 行）· 图谱定位：vector 子系统根节点，vector_env.py 在图谱中出现 26 处（10 条 file 级 + 16 条符号级引用），是 `gymnasium/vector/` 12 个模块的公共祖先

## 一、角色定位：与 Env 平行的"批量宪法"

上一篇（03-registration）讲了环境怎么被注册与制造；这一篇解决 RL 训练里更根本的吞吐问题——单个 `Env.step()` 一次只走一条轨迹，而采样型算法（PPO、SAC）天然吃批量数据。Gymnasium 的答案是一个**与 `core.Env` 平行、但不继承它**的契约层：`VectorEnv`（vector_env.py:L49）把"运行同一环境的 N 个独立副本"抽象成一个对象，`step` 一次吃一批动作、吐一批 `(observations, rewards, terminations, truncations, infos)`。

"平行而非继承"是本文件的第一个关键认知（01 篇已实证逐属性镜像）：`VectorEnv` 复刻了 `Env` 的整套约定——`render_mode` 类属性（L131）、`_np_random/_np_random_seed` 惰性随机源（L141-142、L249-277）、reset 里同样的 `seeding.np_random(seed)` 两行（L171-172）——但方法签名全部"批量化"了：`reset` 接受 seed 列表、`step` 返回形状 `(num_envs,)` 的奖励与终止布尔、空间属性一分为四（`single_observation_space` 与 `observation_space` 并存，L134-137）。之所以不继承，是因为**批量环境不是一种单环境**：它没有 `render_mode` 语义上的单一渲染、它的 RNG 是 N 个而非 1 个，强行 is-a 关系只会让两边的类型都变脏。

这个文件同时是三层角色的宿主：`VectorEnv` 抽象基类（契约）+ `AutoresetMode` 枚举（vector_env.py:L41-46，回合结束自动复位的语义协议）+ `VectorWrapper` 及三个专用子类（vector_env.py:L361-667，批量版的包装协议，与 `gymnasium.Wrapper` 同构）。`SyncVectorEnv`（sync_vector_env.py:L27）则是最常用的具体实现——用 Python for 循环串行步进 N 个子环境，是理解一切向量化行为的参照系；`AsyncVectorEnv` 换成进程池，行为语义与之逐条对齐。

## 二、内部结构

### 2.1 VectorEnv 基类：文档契约 + 预分配默认值

与 `Env` 一样，`VectorEnv` 不用 ABC，`step` 只 `raise NotImplementedError`（L210），靠 docstring 约束子类。类体先声明六个公共属性（L129-139）：`metadata/spec/render_mode/closed` 走类属性默认，四个空间属性 + `num_envs` 是纯注解，由子类在构造器里填。生命周期方法四件套中，`close`（L222-243）是唯一有实现的：以 `closed` 布尔做幂等守卫（L239），真正的清理委托给 `close_extras` 钩子（L245-247）——基类只管标志位，子类管资源，这让 Sync（关 envs 列表）与 Async（收进程管道）共用同一套关闭协议。

基类里最有分量的是 `_add_info`（L284-345）——infos 聚合算法。v0.25 之前 infos 是 list-of-dict（每个子环境一个 dict），之后改为 **dict-of-array**（每个 key 对应横跨 N 个环境的数组），旧格式由 `DictInfoToList` wrapper 兼容（docstring L72-75 钉版）。算法对单个子环境的 info 逐 key 归并：标量（int/float/bool/np.number）建成 `np.zeros(num_envs, dtype=type(value))`（L317-320）；ndarray 建 `(num_envs, *value.shape)`（L321-325）；未知对象建 object 数组（L327-328）；嵌套 dict 递归（L311-312）。同时为每个 key 生成 `_key` 布尔 mask（L337-344），标记哪些子环境真的携带了这个字段——这是稀疏 info（如只有终止的环境才有 `final_obs`）能无损批量化 的关键。`final_obs` 有特判（L304-309）：存 object 数组而非堆叠，因为终止环境可能只有一两个。

### 2.2 AutoresetMode：三种回合结束语义（L41-46）

`NEXT_STEP`（默认）：某子环境 `terminated or truncated` 后，**下一次** `step` 该槽位自动 reset，且那一步的 reward 记 0、term/trunc 记 False；`SAME_STEP`：终局步**当场** reset，终局观测塞进 `info["final_obs"]`；`DISABLED`：库不做任何自动复位，用户全权负责。模式必须写进 `metadata["autoreset_mode"]`（docstring L68 钉版），Sync 在 L119、Async 在 L224 构造时注入。

### 2.3 VectorWrapper 族：透传-覆盖二态 property

`VectorWrapper`（L361）持有 `env` 并在构造时 `isinstance` 校验（L389-392）。它的设计模式与 `gymnasium.Wrapper` 完全同构但值得单独看：四个空间属性被实现为"本地槽优先、否则透传"的 property——构造器初始化 `_observation_space = None` 等四个槽（L394-397），getter 在槽为 None 时返回 `self.env.observation_space`（L441-446），setter 只写本地槽（L448-451）。这样 wrapper 不改空间时零成本透传，改空间时不污染内层。`num_envs/spec/render_mode/closed` 纯透传（L489-492、L524-540）。三个专用子类各开一个变换钩子：`VectorObservationWrapper.observations()`（L591）、`VectorActionWrapper.actions()`（L625，在动作送进内层**之前**变换）、`VectorRewardWrapper.rewards()`（L658）。注意 `VectorObservationWrapper` 构造时会校验 autoreset_mode（L558-569）：只接受 NEXT_STEP 与 DISABLED，SAME_STEP 直接 ValueError——因为 SAME_STEP 的 `final_obs` 是未经变换的裸观测，观察变换会破坏它的一致性。

### 2.4 SyncVectorEnv：构造四步 + 两个重写

构造器（sync_vector_env.py:L79-181）分四步：**实例化**——`[env_fn() for env_fn in env_fns]`（L112），注意传的是延迟构造的 lambda 列表而非 env 列表（Async 需要每个进程各自构造，API 保持一致）；**属性推导**——`num_envs = len(envs)`（L116）、metadata 做浅拷贝再注入 autoreset_mode（L118-119，`dict(...)` 避免改到子环境类级 metadata）、`single_action_space = envs[0].action_space` 后 `batch_space` 推导批量 action_space（L122-123）；**observation_mode 三态**（L125-147）——`"same"` 要求所有子环境观测空间完全相等、`"different"` 允许同 shape/dtype 不同界（走 `batch_differing_spaces`，L141-143）、二元组直接指定 (batched, single) 两个空间（L132）；**校验 + 预分配**——逐 env 核对空间一致性（L150-167，违反即 RuntimeError 并在报错里直接给出修法建议），然后预分配 `_observations/_rewards/_terminations/_truncations` 四个批量缓冲与 `_autoreset_envs` 布尔数组（L170-181），后续 reset/step 全部 in-place 复用。

它还**重写**了基类两个 property：`np_random/np_random_seed` 变成"逐环境取属性"的元组（L183-191，内部走 `get_attr`）——基类的单 RNG 语义在这里被显式放弃，这是平行契约里少数签名发散点。

此外它提供了穿透批量外壳的三个通道方法：`call(name, *args)`（L361-381）在每个子环境上执行同名方法并打包结果元组，内部经 `get_wrapper_attr` 取属性，callable 才调用、否则直接取值（L374-379）；`get_attr` 就是 `call(name)` 的别名（L383-392）；`set_attr`（L394-416）支持单值广播到全部子环境（L406-407）或按环境列表逐一设置（经 `set_wrapper_attr`，L415-416）。训练代码里"改一下每个环境的重力参数"这类需求全靠这三个口。`render` 则朴素地把各子环境的渲染帧拼成元组（L357-359；Async 侧复用 `call("render")`，async L587-589）。

### 2.5 AsyncVectorEnv 进程池模型（略述）

`AsyncVectorEnv` 每个子环境一个 `multiprocessing.Process` + 一对 `Pipe`（async_vector_env.py:L289-311），命令协议是 `(command, data)` 元组流：`reset/reset-noop/step/close/_call/_setattr/_check_spaces` 七种，由 worker 循环（`_async_worker`，L823-976）分发。主进程侧 `step = step_async + step_wait`（L479-480）两段式，`AsyncState` 枚举（L47-53）防重入（连发两次 `step_async` 抛 `AlreadyPendingCallError`）。观测回传有两条通道：`shared_memory=True`（默认）时 worker 把观测 `write_to_shared_memory` 写进构造期建好的共享缓冲（L910-914）然后 `observation = None`，管道里只回传标量与 info，主进程从共享内存视图直接读——大观测（图像）时省去 pickle 序列化；`shared_memory=False` 时走管道 pickle 回传再 `concatenate`（L557-562）。

## 三、外部连接

**上游**：`gymnasium.core`（ObsType/ActType 等类型与 Env 本体，sync L12-13）、`gymnasium.utils.seeding`（L20）、`gymnasium.spaces.utils.is_space_dtype_shape_equiv`（sync L14，"different" 模式的形状/ dtype 等价判定）、`gymnasium.vector.utils` 五件套（sync L15-21：`batch_space/batch_differing_spaces/concatenate/create_empty_array/iterate`）。Async 额外依赖 `gymnasium.error` 四个专用异常（L23-28）、`CloudpickleWrapper`（L31，让 lambda 形式的 env_fn 能跨进程序列化）与 `clear_mpi_env_vars`（L34，清 MPI 环境变量防 fork 死锁）。

**下游**：`gymnasium.wrappers.vector` 全部包装类（ClipReward/NumpyToTorch/StatefulObservation 等）继承本文的 `VectorObservationWrapper/VectorActionWrapper/VectorRewardWrapper`；`gymnasium.envs.registration.make_vec`（registration.py:L835）是标准入口——`vectorization_mode="sync"/"async"` 分别构造两个实现，`"vector_entry_point"` 模式（registration.py:L246-250 的 VectorizeMode 枚举）走 spec 上注册的 `vector_entry_point` 字段（registration.py:L114）加载环境自带的原生向量化实现（如 Brax、MuJoCo 系的自定义 VectorEnv），且该模式显式禁止再叠 wrappers 参数（registration.py:L942-949）；外部生态（SB3、CleanRL）直接消费 `num_envs/single_*_space` 契约。

## 四、数据流

**reset**（sync L193-273）：seed 两协议展开——`None` 变 `[None]*n`（各自随机），单个 int 展开为 `[seed, seed+1, ..., seed+n-1]`（L213-214，**连续不重复**），显式列表则校验长度等于 num_envs（L215-218）。然后看 `options` 里有没有 `reset_mask`：有则只复位 mask 为 True 的子环境（L220-252），并把它们的 `_terminations/_truncations/_autoreset_envs` 槽位清零（L239-241）——这是部分复位的官方通道；无则全量复位并整体清零三个状态数组（L254-256）。每个子环境的返回经 `_add_info` 聚合，观测经 `concatenate` 写入预分配的 `self._observations`（L267-272），`copy=True` 时 deepcopy 出栈（L273）。

**step**（sync L275-355）：先用 `iterate(action_space, actions)` 把批量动作拆成 N 个单动作（L289，`zip(..., strict=True)` 保证数量对齐，L292），然后逐 env 走三分支：NEXT_STEP 下查 `_autoreset_envs[i]`——为真则该槽 `reset()` 并写 reward=0、term/trunc=False（L294-299），为真为假都汇到 `_add_info`（L338）；DISABLED 下 `assert not self._autoreset_envs[i]`（L310），忘了手动 reset 的用户会在这里直接炸断言而非拿到脏数据；SAME_STEP 下终局时先把 `final_obs/final_info` 写进 infos 再当场 reset（L327-334）。循环结束统一 `concatenate`（L341-346），用 `np.logical_or(terminations, truncations)` 刷新 `_autoreset_envs`（L347），返回时对四个数组逐个 `np.copy`（L349-355）——预分配缓冲是共享可变状态，不拷贝的话调用方下一 step 就会看到手上的数据被改写。Async 的 step 数据流与之逐条镜像，只是循环体搬进了 worker 的 NEXT_STEP 分支（async L867-879，worker 侧用一个本地 `autoreset` 布尔替代 `_autoreset_envs` 数组，L836）。

**异常流**（Async 独有）：子环境抛异常时 worker 捕获，把 `(index, exctype, value, traceback)` 四元组塞进共享 `error_queue` 并向管道发 `(None, False)` 失败标记（async L969-974）；主进程 `_raise_if_errors`（L795-815）发现任一 False 后逐个取队列、关闭出错管道、用 `logger.error` 打印完整 traceback，**最后一个异常以 `raise exctype(value)` 在主进程原样重抛**（L812-815）——用户看到的既是原始异常类型，又能在日志里读到子进程现场。

## 五、设计决策

**batch_space 的类型变换而非维度堆叠**（vector/utils/space_utils.py:L51，singledispatch）：`Box` 批量化只是前缀加 n 维（L78-82），但 `Discrete(n)` 变 `MultiDiscrete([n]*batch)`（L85-92）、`MultiDiscrete/MultiBinary` 直接变 `Box`（L95-115）。观测/动作空间"为神经网络输入输出优化"（docstring L57-58）——网络最后一层输出的本来就是一组 logits，用 Box 承接比维持离散语义更贴近张量流。副作用是**不能从 `action_space` 反推 `single_action_space` 的类型**，两套空间必须分别存（这正是四属性设计的动因）。

**预分配 + in-place 复用**：`create_empty_array(fn=np.zeros)`（sync L171-176）一次建好批量观测缓冲，reset/step 的 `concatenate` 每次写回同一块内存，配合返回时的 `deepcopy/np.copy`（L273、L349-355）在"零分配开销"与"调用方持有安全副本"间取得平衡；追求极致吞吐可以 `copy=False`，代价是必须消费完再调下一步。

**close 的分工与守卫**：基类管 `closed` 标志幂等（vector_env.py:L239-243），子类 `close_extras` 管真实资源；Sync 的 `close_extras` 用 `hasattr(self, "envs")` 守卫（sync L420）——构造器在 L112 之前抛异常时 `__del__` 仍会触发 close，没有守卫就会在半成品对象上二次炸裂。`__repr__` 按有无 spec 给两种打印（vector_env.py:L353-357），wrapper 的尖括号套娃打印（L437-439）与 `gymnasium.Wrapper` 一脉相承。

**Async 的 dummy_env 先行**（async L217-257）：主进程先 `env_fns[0]()` 造一个一次性环境拿 metadata 与空间，随即 close 删掉（L256-257）。源码注释直言不讳：没有这一步，"shared memory and pipes 之间会死锁"（L217）——共享缓冲的形状必须在 spawn 进程前确定，而确定形状需要空间信息。`"different"` 模式更激进，把所有 env 都实例化一遍取空间再销毁（L244-250，注释承认这对有副作用的环境可能出问题）。

**semaphore 的 release-before-send**（async L858-861、L916-919）：`max_concurrency` 用 `BoundedSemaphore` 限制同时执行 reset/step 的进程数（L283-287，物理引擎类环境进程数超核反而变慢）。worker 在 `pipe.send` **之前**释放许可——因为 send 会阻塞直到主进程读管道，先释放才能让别的 worker 顶上；`finally` 块兜底保证异常路径不漏许可（L965-967）。

**worker 签名主进程预检**（async L204-213）：自定义 worker 的签名错误若在子进程才炸，主进程只会看到一个裸 `EOFError`（管道关闭），极难排查；构造期用 `inspect.signature(worker).bind` 先验，把故障面拦在 spawn 之前。

**一处勘误（钉版）**：任务口径中的 "FlatListToDict 协议" 在当前仓**不存在**——全仓 grep 零命中。那是旧版 gym 的设计（Dict 观测先扁平化传输再重组）；Gymnasium 现版由 `read_from_shared_memory` 按 singledispatch 依空间结构直接构造嵌套对象（shared_memory.py:L145-253），Dict 空间的读出就是逐 key 递归（L205-213），`Tuple/Text/OneOf` 各有专用分支（L195/L215/L237）。正确的记忆锚是 **read/write_to_shared_memory 的按空间分发协议**。

## 六、新人提示

1. `num_envs` 是硬契约：所有 wrapper 透传它、所有批量数组第一维等于它、`reset` 的 seed 列表长度对齐它（sync L215-218）。写自定义 VectorEnv 时第一件事就是设置它。
2. **DISABLED 模式不替你收拾**：step 内的 assert（sync L310）意味着"忘了 reset"会以 AssertionError 而非静默脏数据收场；反向说，想做完全手动控制（如按回合边界切数据）就选它。
3. NEXT_STEP 语义下，终局后那一步的 `(obs, 0.0, False, False)` 不是 bug 是协议——训练代码要把这一步的 transition 从梯度里摘出去，或改用 SAME_STEP 靠 `final_obs` 拿终局观测（sync L327-334 写入，`_add_info` 的 object 数组读出，vector_env.py:L304-309）。
4. `reset_mask` 藏在 `options` 里（sync L220），且必须至少一个 True、dtype 必须 np.bool_——想局部复位环境的读者先查这里而不是找新 API。
5. `copy=False` 省一次 deepcopy，但返回的观测与内部缓冲同块内存；任何"存下这批观测稍后用"的代码都会踩到下一 step 的覆写。
6. 自定义观测空间（非 Gym 标准空间）配 Async 必须关 `shared_memory`，否则构造期 `CustomSpaceError` 转 ValueError（async L269-272，报错信息直接给出修法）。
7. 调 Async 崩溃先翻 stderr 里的 `logger.error` 输出——`_raise_if_errors` 会先打印子进程完整 traceback 再重抛（async L804-815），异常类型在主进程、现场在日志里。
8. daemon 进程随主进程退出（async L309），正常路径 `close` 发 `"close"` 命令优雅收尾，`__del__` 兜底 `close(terminate=True)`（L817-820）；但 daemon=True 的子进程不能再 fork 孙进程（docstring L150-152），嵌套并行需求要显式关 daemon。
9. Sync 与 Async 的 `np_random` 是**元组**（sync L183-191），与单 Env 的单 Generator 不同；种子可控性靠 reset 的 seed 展开协议（连续 int），不要指望直接播种批量 RNG。

> 关联篇目：契约源头见 01-core（平行镜像实证）；空间类型见 02-spaces；构造入口见 03-registration（make_vec 三模式）；批量包装器实例见后续 wrappers/vector 篇。
