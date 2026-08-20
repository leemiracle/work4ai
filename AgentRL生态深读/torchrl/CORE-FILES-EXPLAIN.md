# torchrl 核心文件精讲（1/3）：数据底座与环境系统

> 分片范围：数据底座（tensor_specs / data.utils / replay buffers 四件套）+ 环境系统（common / utils / batched_envs / libs/gym / transforms 双文件），共 16 个文件。
> 方法：知识图谱节点（`.understand-anything/knowledge-graph.json`，summary/tags/complexity/出入边）+ 实源码精读，行号锚点全部来自真实读取。
> 版本锚点：torchrl v0.14.0（version.txt），HEAD `3b6b5b9` "[Performance] Lock TransformedEnv specs by default (#4121)"。
> 图谱十层坐标：本分片覆盖 **核心基础层**（`__init__.py`/`_utils.py`）、**数据层**（specs/RB，52 节点）、**环境层**（128 节点）三层。

---

## README.md + pyproject.toml（合并简讲：项目叙事与依赖版图）

### 架构角色
README 是整个仓库的"宪法序言"（图谱记为 `document:README.md`，582 行 29 节，complexity=complex，`documents -> file:torchrl/__init__.py`）；pyproject.toml 是构建与依赖中枢（`config:pyproject.toml`，`configures -> file:torchrl/__init__.py`）。两者合起来回答"torchrl 是什么、靠什么活"。

### 项目叙事（README.md）
三大设计理念（README.md:31-40）：
1. **数据全程带名字/结构/批维度/设备**——由 TensorDict 落实（README.md:42-44）；
2. **环境/策略/回放缓冲/目标函数/采集器皆可独立替换**；
3. **从本地原型到分布式/编译/多智能体不改数据模型**。

心智模型（README.md:74-82）是一条 TensorDict 流水线：policy 写 action → env 写 next/reward/done → collector 批量化 → replay buffer 存采变换 → loss 读命名键 → 普通 PyTorch optimizer 更新。Quick demo（README.md:94-118）三行核心：`TransformedEnv(PendulumEnv(), StepCounter(...))` + `TensorDictModule(..., in_keys=["observation"], out_keys=["action"])` + `env.rollout(max_steps=32, policy=policy)`——这就是全库的 API 风格缩影。0.13 起的亮点（README.md:53-67）：循环 RL（scan/Triton GRU reset）、MuJoCo 定制环境、MAPPO/IPPO、异步优先级写、LLM 工作流。

### 依赖版图（pyproject.toml）
- **运行时依赖仅 7 项**（pyproject.toml:40-48）：`torch>=2.1.0`、`tensordict>=0.14.0,<0.15.0`（硬锁同版本线——TensorDict 是数据模型的孪生库）、`pyvers`/`hoptorch`（版本分发/优化器工具）、numpy、packaging、cloudpickle。可选依赖 20+ 组（pyproject.toml:91-196）：环境类（atari/dm_control/brax/mjlab/genesis/procgen…）、数据类（offline-data/checkpointing）、`llm`/`llm-vllm`/`llm-sglang`/`grpo`（LLM 后训练栈）、`marl`。
- 构建后端 setuptools+setuptools_scm（pyproject.toml:1-12, 216-222，fallback_version=0.14.0），带 csrc C++/CUDA 源码包（package-data 引 `csrc/*.h/*.cu`，pyproject.toml:236-241）。
- 两个入口点：`rlrender` CLI（pyproject.toml:202-204）与 **vLLM 通用插件** `torchrl_fp32_overrides`（pyproject.toml:256-263）——vLLM 每个进程自动加载、默认 NO-OP，只有设了 `TORCHRL_VLLM_FP32_OVERRIDES` 才生效，是 LLM 训推一体部署的钩子。
- uv 工程化：nightly PyTorch 源、tensordict git 源、extras 冲突声明（mjlab vs genesis，pyproject.toml:67-84）。

### 模式与坑
- 读 README 的正确姿势：先看 74-82 行心智模型图，再看 125-355 行"What TorchRL is today"按子系统展开；357-399 行是 0.13 changelog。
- 坑：`vla`/`brax`/`llm-vllm` 等 extras 都有 python_version/platform 条件标记，跨平台安装行为不一致是预期内的。

---

## torchrl/__init__.py

### 架构角色
核心基础层的包根入口（图谱：tags=`entry-point/package-root/monkey-patch`，complexity=simple）。它不做业务，只做四件事：**定版本、加载 C++ 扩展、定多进程基调、打两个 monkey-patch**。

### 内部结构（全 158 行，已通读）
| 行号 | 内容 |
|---|---|
| 13-17 | 过滤 tensordict 注册 pytree 的弃用警告 |
| 29 | `set_lazy_legacy(False).set()`——关闭 TensorDict 懒执行遗留模式 |
| 33-52 | 三级降级版本探测：importlib.metadata("torchrl") → nightly → `_version.py` |
| 59 | `_init_extension()`：探测并加载 C++ segment-tree 内核（来自 `torchrl/_extension.py`） |
| 61-79 | 从 `_comm.backends` 取 service/transport 后端、从 `_utils` 再导出 timeit/logger 等 13 个符号 |
| 81-93 | **默认 spawn**：`_get_default_mp_start_method()`，若全局已被设成非 spawn 只警告不覆盖 |
| 102-141 | monkey-patch `torch.distributions.transforms.Transform.inv` 与 `ComposeTransform.inv` |

### 外部连接（图谱边）
- OUT `imports`：`torchrl/_extension.py`（C++ 扩展延迟初始化）、`torchrl/_utils.py`、`torchrl/_comm/backends.py`。
- IN `imports`（13 个）：collectors 三件套（`_single.py`/`_multi_base.py`/`_runner.py`）、`checkpoint/_checkpoint.py`、`modules/llm/policies/transformers_wrapper.py`、`render/artifacts.py` 等——都是"要用 timeit/logger/版本号就 import 包根"。
- 被 `config:pyproject.toml`、`mypy.ini`、`setup.cfg`、`document:README.md`、`AGENTS.md` configures/documents。

### 数据流
import torchrl 的瞬间：警告过滤 → tensordict 模式设定 → C++ 扩展加载（无 CUDA 也能跑，内核退回 Python）→ spawn 设定 → `Transform.inv` 补丁生效。此后全库任何 `dist.inv` 访问都走补丁。

### 模式与坑
- **monkey-patch 的动机是性能**：原版 `Transform.inv` 每次访问都新建 `_InverseTransform`；补丁用 `weakref` 缓存并保证 `t.inv.inv is t`（103-118 行），rollout 中反复取逆变换（如 TanhNormal 采样）不再重复建对象。
- 116/131 行的 `is_dynamo_compiling()` 分支：torch.compile 图捕获期间 weakref 会造成 graph break，改用闭包 `lambda out=self: out`——**在编译语境下弱引用是地雷**，这是全库反复出现的主题。
- spawn 默认意味着 ParallelEnv 的每个 worker 都是全新解释器：模块级全局态（如 VecNorm 统计）必须显式走共享内存。

---

## torchrl/_utils.py

### 架构角色
全库 fan-in 最高的工具集（图谱 IN edges **125 个**，被 collectors/envs/data/objectives/trainers 全线依赖；tags=`utility/multiprocessing/profiling/ray/cuda`，complexity=complex）。图谱 tour 第 2 站原话："几乎所有子系统都复用它的张量与设备工具"。

### 内部结构（1838 行，关键类+行号）
| 行号 | 符号 | 职责 |
|---|---|---|
| 48-123 | `_get_default_mp_start_method` 等 3 函数 | 多进程 start method 三件套（用户已设则尊重，否则 spawn） |
| 113-123 | `_mp_sharing_strategy_for_spawn` | 用 `implement_for` 按 torch 版本二选一（<2.8 用 file_system 减少 FD 传递） |
| 221-433 | `timeit` | 装饰器+上下文管理器双模式计时器，类级 `_REG` 全局累积 |
| 543-560 | `seed_generator` | 种子链：`np.random.default_rng(seed)` 取 8 字节映射到 [0, 2³²) |
| 563-579 | `KeyDependentDefaultDict` | default 工厂能拿到缺失 key 本身 |
| 742 | `context_decorator` | 把上下文管理器适配成装饰器（标准库 contextmanager 的轻量替代） |
| 1046 | `_rng_decorator` | 进出保存/恢复全局 RNG 状态（可复现实验） |
| 1102 | `get_available_device` | CUDA→MPS→CPU 探测 |
| 1158-1219 | `_standardize` | 按均值/方差标准化，支持 `exclude_dims`（多智能体按 agent 维独立统计）——ObservationNorm 的数学内核之一 |
| 1223 | `compile_with_warmup` | torch.compile 包装 + 预热前向，规避 CUDA graph 首次开销 |
| 1462 | `cuda_memory_profile` | CUDA 内存快照上下文 |
| 1546-1725 | `_RayServiceMetaClass` | 把普通类透明转成 Ray remote actor 的元类 |
| 1689-1786 | `as_remote` / `get_ray_default_runtime_env` / `merge_ray_runtime_env` | Ray 服务包装三件套 |

### 精读三例
1. **`timeit`（221-320）**：`_REG` 是类级字典，`_record`（307-315）做增量均值——`val[0] = val[0]*(count/N) + elapsed/N`，注册表永不清理，长训练里只增不减；`timeit.print()` 全局打印。它是 collector/worker 里所有 `batched_env_worker/{pid}/lifetime` 计时标签的来源。
2. **`seed_generator`（543-560）**：为什么绕道 numpy？注释直引 PyTorch 论坛——torch 的 max seed 是 2³²-1，直接 `hash()` 可能越界。ParallelEnv 给每个 worker 派生独立种子就是链式调用它。
3. **`_RayServiceMetaClass`（1546-1620）**：`__call__` 拦截构造——`use_ray_service=True` 时返回 `_RayServiceClass` 的 actor handle 而不是本地实例；`__instancecheck__`（1571-1582）让 `isinstance(actor_handle, MyClass)` 依然为 True。1606-1614 行处理了嵌套构造的坑：service 工厂内部再构造同元类对象时用 `_SERVICE_BACKEND_DISPATCHING`（contextvars）防止二次分发。ReplayBuffer/Logger 都挂这个元类，所以同一构造函数能一键"本地版/Ray 版"。

### 外部连接
- OUT：仅 `_comm/backends.py`（服务后端解析）+ 巨量 `contains`/`exports`（60 条出边主要是成员导出）。
- IN：125 个文件（envs 全家族、collectors、objectives、data、trainers……），图谱 IN 摘要里 `gym_like.py`、`tensor_specs.py`、`batched_envs.py`、`common.py` 等本分片主角全部在列。

### 数据流与坑
- `_get_mp_ctx`（65-78）刻意**不依赖全局 set_start_method**，按上下文取 ctx——Queue/Pipe/Lock 与 Process 必须同 ctx 创建，混用是死锁经典来源（AGENTS.md 也专门强调）。
- 坑：`_standardize` 的 `exclude_dims` 全部维度都被排除时只 warning 并原样返回（1208-1212），不会报错——静默通过要小心。
- 坑：`timeit._REG` 无限增长且跨进程不合并，多 worker 场景各自记账，主进程聚合需自己做。

---

## torchrl/data/tensor_specs.py

### 架构角色
**数据层的类型系统**。图谱 IN edges **95 个**（envs 全部 40+ 包装器、modules、objectives 十余种损失、record、testing……），是名副其实的契约中枢：观测/动作/奖励空间的 shape+dtype+值域+设备描述，加 encode/project/rand/is_in 四大操作。tags=`tensor-spec/data-model/core/validation/encoding`。

### 内部结构（7265 行，全类行号表）
| 行号 | 类 | 一句话 |
|---|---|---|
| 346 | `invertible_dict` | 值→键反查字典（编码映射逆向） |
| 380-606 | `Box` 族 | `ContinuousBox`（low/high 张量）/`CategoricalBox`/`DiscreteBox`/`BoxList`/`BinaryBox`——值域容器 |
| 607 | `TensorSpec` | 抽象基类：shape/space/dtype/device 四字段 |
| 1261/1496 | `_LazyStackedMixin`/`Stacked` | 惰性堆叠：不物理拼接，索引/克隆委托成员 |
| 1695 | `OneHot` | 离散动作 one-hot 编码 |
| 2259 | `Bounded`（`_BoundedMeta` 2248） | 有界连续，encode 即裁剪投影 |
| 2683/2701 | `BoundedContinuous`/`BoundedDiscrete` | Bounded 的连续/离散特化 |
| 2738 | `NonTensor` | 字符串等非张量观测（LLM prompt 走这） |
| 3053 | `Unbounded` | 无界（reward/done 常用） |
| 3298 | `MultiOneHot` | 多段 one-hot 拼接 |
| 3808 | `Categorical` | 类别索引编码（支持 `set_provisional_n` 未定类别数） |
| 4243/4398/4600 | `Choice`/`Binary`/`MultiCategorical` | 离散取值集/二值/多维类别 |
| **5042** | **`Composite`** | **嵌套 spec 树——obs/action/reward 的标准载体** |
| 6463 | `StackedComposite` | Composite 的懒堆叠版 |
| 6819-7076 | `_stack_specs`/`_index_select_spec`/`_stack_composite_specs` 等 | 堆叠/索引/形状推导自由函数 |

### 精读
**TensorSpec 基类（607-1260）**：类文档（608-633）开宗明义——spec 的首要用途是"不启动环境就能描述输入输出结构"，还能用来预分配跨进程共享缓冲。核心方法族：`encode`（719，占位抽象）→ `_encode_eager`（747-786）：list[np] → `torch.as_tensor(device, dtype)` → reshape 到 self.shape，末尾若 `_CHECK_SPEC_ENCODE`（环境变量，文件头 66 行）则 `assert_is_in` 校验；`memoize_encode`（646）把 encode 编译成 callable 链缓存（`_encode_memo_dict`），官方自标 experimental；`cardinality` 抽象（709）；`SPEC_HANDLED_FUNCTIONS` + `implements_for_spec`（679-688）是 torch_function 协议——让 `torch.stack(specs)` 这类操作可被 spec 覆写。

**OneHot._encode_eager（2010-2035）**：离散动作编码的教科书路径——`as_tensor` → （可选 register 查表）→ 越界断言 → `F.one_hot(val.long(), n).to(dtype)`。memo 版（2037-2084）把同样步骤编译成 `functools.reduce` 的函数链缓存。

**Composite（5042-6462）**：方法是"映射到每个叶子"——`_project`（5240 附近）递归 `from_dict({k: item._project(val[k])})`；`shape` setter（5225 起）在 `locked` 时直接 `RuntimeError("Cannot modify shape of locked composite spec.")`，未锁时逐键检查叶子前缀形状一致。这套 locked 机制与 HEAD commit `3b6b5b9`（TransformedEnv 默认锁 spec）呼应：**spec 锁 = 性能优化 + 防误改**。

### 外部连接
- OUT `imports`：仅 `torchrl/_utils.py`（`_make_ordinal_device`/`get_binary_env_var`/`implement_for`）。
- IN 95 个：本分片的 `data/utils.py`、`envs/common.py`、`envs/batched_envs.py`、`envs/libs/gym.py`、`transforms/_base.py`、RB `replay_buffers.py` 全部导入它；上层还有全部 objectives 损失（ppo/sac/td3/dqn/iql/cql...）、record、trainers helpers。

### 数据流（TensorDict 键如何流转）
spec 是**键的元数据侧**：环境 reset/step 产出 numpy（gym 系）→ `obs_spec.encode(np)` 变成 shape/dtype/device 全对齐的 tensor → 写进 TensorDict 对应键。策略侧反向：网络裸输出（可能越界）→ `action_spec.project(tensor)` 拉回值域才交给 env。`rand()` 则按 spec 造随机数据（check_env_specs 与 fake_tensordict 的基础）。

### 模式与坑
- **-1 形状 = 动态维度**（类文档 623-624），配合 `Stacked` 懒堆叠支撑变长 batch（LLM 序列、异构多智能体）。
- `Composite` 的 device 可为 None，叶子必须非 None（690-696 property docstring）——序列化跨设备时的 `_bounds_cache` 会被剔除（`__getstate__` 672-677）避免 CUDA 张量进 pickle。
- 坑：`CHECK_SPEC_ENCODE` 默认关（性能），encode 越界不报错静默通过；调试环境时务必打开。
- 坑：`memoize_encode` 缓存按 `(input_type 一致性)` 生效，输入类型一变就错——所以官方警告"experimental, use at your own risks"。

---

## torchrl/data/utils.py

### 架构角色
数据层小工具箱（334 行，complexity=moderate，fan-in **45**）：dtype 映射表 + Composite 独占键治理 + cloudpickle 序列化包装 + 动作空间字符串互转。是 tensor_specs 与上层（modules/models、objectives、trainers helpers）之间的胶水。

### 内部结构（全 334 行，已通读）
| 行号 | 符号 | 职责 |
|---|---|---|
| 28-43 | `numpy_to_torch_dtype_dict` / `torch_to_numpy_dtype_dict` | np.dtype↔torch.dtype 双向表（gym 适配的基石） |
| 44-50 | `DEVICE_TYPING`/`INDEX_TYPING` | 类型别名 |
| 53-71 | `ACTION_SPACE_MAP` | spec 类 ↔ 字符串（"one_hot"/"mult_one_hot"/"binary"/"categorical"/"multi_categorical"），还接受多种连字符拼写宽容归一 |
| 74-139 | `consolidate_spec` | 消除 Composite 独占键：给缺键的子 spec 补 0 形状占位（递归 entries + lazy stack 两层） |
| 142-185 | `_empty_like_spec` | 生成同构空 spec；异构维度置 0 |
| 188-208 | `check_no_exclusive_keys` | 检查堆叠/合并前是否还有独占键 |
| 211-224 | `contains_lazy_spec` | spec 树里有无 Stacked/StackedComposite |
| 227-258 | `CloudpickleWrapper` | cloudpickle 序列化任意 callable（lambda/闭包跨进程）；元类保证重复包装幂等（229-232）；**239-243 显式拒绝包装 EnvCreator**（会破坏共享张量指针传递） |
| 261-311 | `_process_action_space_spec` | 把 `action_space`（字符串或 spec）与 spec 参数归一成一致对；Composite 里找 `action` 键（嵌套时找首个以 action 结尾的键，271-275） |
| 314-334 | `_find_action_space` | spec → 字符串方向查表 |

### 外部连接
- OUT：`tensor_specs.py`（唯一 import）。
- IN 45 个：collectors 全家族（含 distributed 三件套）、RB `replay_buffers.py`、envs 全家族（common/batched_envs/gym/dm_control/...）、modules（models/actors/exploration/multiagent）、objectives（dqn/sac/iql/cql/qmixer）、trainers。

### 数据流
两个方向：**环境侧** numpy array 经 28 行表转 torch tensor；**模型侧** 用户传 `action_space="one_hot"` 或 OneHot spec 进 `make_dqn_actor` 等工厂 → `_process_action_space_spec` 统一成 (字符串, spec) 二元组，决定 QValueActor 输出离散化的方式。

### 模式与坑
- 独占键（exclusive keys）是多智能体/异构 batch 的顽疾：不同子环境的 Composite 键集不同，直接 `torch.stack` 会炸——`consolidate_spec` 用 0 形状占位符抹平，代价是该键在部分环境里是空数据。
- 坑：`CloudpickleWrapper` + `EnvCreator` 组合被硬性禁止（240-243 RuntimeError）——VecNorm 跨进程共享统计依赖 EnvCreator 携带共享张量指针，cloudpickle 会把指针序列化成普通副本。

---

## torchrl/data/replay_buffers/replay_buffers.py

### 架构角色
回放缓冲的**编排层**（4012 行，tags=`replay-buffer/core/data-model/distributed`）：ReplayBuffer 把 Storage/Writer/Sampler/Transform 四个正交组件装配成一台数据机器，再派生 Prioritized/TensorDict/Remote/Ensemble 变体。上游消费者是 trainers 全部 algorithm 装配器（ddpg/dqn/iql/sac/td3/cql/on_policy）。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| 108 | `_storage_index` | RB 层索引 → 存储层索引（环形回绕换算） |
| 134 | `ConditionalUpdateResult` | 条件更新三计数（updated/version_rejected/stale）——陈旧数据诊断 |
| **181** | **`ReplayBuffer`**（挂 `_RayServiceMetaClass` 元类） | 基类：四组件生命周期 + add/extend/sample/prefetch/优先级/检查点/分布式服务化 |
| 2421 | `PrioritizedReplayBuffer` | 包装 PrioritizedSampler，暴露 alpha/beta 与 update_priority |
| **2712** | **`TensorDictReplayBuffer`** | TensorDict 特化：extend 时可从数据里读 priority 键批量更新优先级 |
| 3171 | `TensorDictPrioritizedReplayBuffer` | TensorDict 接口 × 优先级语义 |
| 3596 | `RemoteTensorDictReplayBuffer` | 瘦客户端：sample/add/extend 转发远端服务 |
| 3629 | `InPlaceSampler` | 零拷贝采样（只读数据集） |
| 3668 | `ReplayBufferEnsemble` | 按概率 p 从多个子缓冲加权采样合并 |

### 精读 ReplayBuffer（181-2420）
构造文档（186-296）极其详尽：storage/sampler/writer/transform 都可传**实例或工厂 callable**（pickle 友好）；`batch_size` 构造期 vs 采样期二选一（prefetch 必须预知）；`dim_extend` 支持多维存储但明确警告 `trajs_per_batch` 采集器写的是变长 1-D 扁平序列、必须保持 ndim=1（245-248）；`delayed_init`（280-285）默认在传 `transform_factory` 时开启——带梯度模块的 transform 要延迟到远端 worker 才实例化。

**写入路径** `extend`（1966-2004）→ `_extend`（1938-1963）：先 `transform.inv(data)`（1999-2001，逆变换发生在**写入前**——存的是环境原始域数据），再加双锁（`_replay_lock`+`_write_lock`，torch.compile 下让位 nullcontext，1941），consumo 型采样器先回收已消费槽位（1944-1960），最后 `writer.extend(data)` 拿到索引 → `sampler.extend(index)`。

**采样路径** `sample`（2056-2097+）→ `_sample`（2022-2042）：`sampler.sample(storage, batch_size)` 得索引 → 可选 `sample_unit.expand`（轨迹单元展开）→ `info["index"]` 记录 → `storage.get(_storage_index(index, storage))` 取数 → collate 成批 → `transform(data)`（**正向变换在采样后**，2035-2040，且要先 `data.unlock_()`）。prefetch 分支（2093-2097+）用 futures 队列多线程预取。

### 外部连接
- OUT `imports`：`samplers.py`/`storages.py`/`writers.py`/`replay_buffers/utils.py`/`checkpointers 缺`（实为 `query.py`/`sample_units.py`/`_comm/replay_service.py`/`transforms/transforms.py`/`_utils.py`/`data/utils.py`）——四件套 + 分布式服务 + 变换。
- IN 17 个：`her.py`/`offline_to_online.py`/`ray_buffer.py`/`scheduler.py`、datasets（openx）、collectors/llm 两个、trainers 六个 algorithm 装配器 + helpers。

### 数据流（TensorDict 键流转）
collector 的 rollout（含 observation/action/reward/done/next…）→ `rb.extend(td)`：transform.inv 归一化还原 → writer 算环形索引写入 storage → sampler 登记索引。训练侧 `rb.sample(batch)`：sampler 出索引（普通/Prioritized 带 priority_weight info）→ storage.get → collate → transform 正向（如 ObservationNorm 重新归一化）→ loss module 按键消费。`TensorDictReplayBuffer.extend` 还会顺手把数据里的 `priority` 键（构造参数 `priority_key`）写进优先级树——TD 与 RB 的键级联动。

### 模式与坑
- **策略模式 + 组合根**：四组件接口在各自基类（Sampler/Storage/Writer），ReplayBuffer 只是编排；换采样策略零成本。
- 坑：tuple 当 PyTree、list 当"逐条添加"的约定（extend 文档 1984-1992）——`list` of TensorDict 与单个 batched TensorDict 语义不同。
- 坑：`_RayServiceMetaClass` 意味着 `ReplayBuffer(service_backend="ray", ...)` 返回的是 actor handle 而非本地对象；`isinstance` 仍 True（元类 `__instancecheck__` 兜底）。
- 坑：sample 的 info 字典里 `index` 是 RB 层索引，直接拿去 `storage.get` 要先过 `_storage_index` 回绕换算。

---

## torchrl/data/replay_buffers/samplers.py

### 架构角色
采样策略全家桶（4207 行，tags=`replay-buffer/sampling/prioritized/core`）：**决定"抽哪些索引"**——与怎么存（storages）、写到哪（writers）完全正交。

### 内部结构
| 行号 | 类 | 职责 |
|---|---|---|
| 72 | `_SamplerMeta` | 构造拦截元类（公共参数规范化） |
| 106 | `Sampler`(ABC) | 契约：sample/add/extend/update_priority/mark_update/state_dict |
| 181 | `RandomSampler` | 均匀随机（默认） |
| 228 | `ConsumingSampler` | 只采未消费的，采完 `ran_out`（单遍数据集） |
| 580 | `SamplerWithoutReplacement` | epoch 内不重复 |
| 735 | `StalenessAwareSampler` | 按消费者/写入者版本差加权偏向新数据（异步训练防陈旧） |
| **942** | **`PrioritizedSampler`** | PER：segment tree 比例优先级 + IS 权重校正 |
| **1696** | **`SliceSampler`** | 沿轨迹边界切 episode/片段 |
| 2800 | `SliceSamplerWithoutReplacement` | 以轨迹为单位无放回 |
| 3102 | `PrioritizedSliceSampler` | 多继承 Slice × Prioritized |
| 3572 | `PromptGroupSampler` | **LLM RL（GRPO）**：按 prompt 分组采 completion，组内选择/方差优先/近因缓存 |
| 3988 | `SamplerEnsemble` | 多采样器加权抽取 |

### 精读 PrioritizedSampler（942-1695）
docstring（944-1048）自带完整数学：优先级 `p_i=|δ_i|+ε`，采样概率 `P(i)=p_i^α/Σp_j^α`，IS 权重 `w_i=(N·P(i))^{-β}`；参数指南给出典型值（α 0.4-0.7、β 从 0.4-0.6 退火到 1.0）。
**实现（sample，1356-1420）**：优先级树有 C++/CPU 与 CUDA 两套（imports 37-54 行按扩展可用性切换 Sum/MinSegmentTreeFp32/64）；流程 = `_sum_tree.query(0, len)` 取 p_sum/p_min → 采 `mass ~ U(0, p_sum)` → `_sum_tree.scan_lower_bound(mass)` 线段树下钻定位 → CPU 路径还要处理零权重槽位（1389-1395 的 while 回退）→ IS 权重化简为 `(p_i/p_min)^{-β}`（1404-1413 的注释给出完整推导）→ ndim>1 时 `unravel_index` 展平索引。CUDA 路径全程 device 张量（1362-1371），配合 pyproject 的 CUDA wheel extras（README 提到的 CUDA prioritized kernels）。
docstring 1029-1047 还演示了与 `TensorDictReplayBuffer(priority_key=...)` 的键联动：`rb.update_priority(data)` 直接读数据键。

### 精读 SliceSampler（1696-2800）头
关键参数（1718-1780）：`end_key` 默认 `("next","done")`；`end_keys` 支持多键 OR（处理只有 truncated 没 done 的数据集——单键会静默把两轨迹并成一条，1735-1740 的 note 是实打实的坑）；`traj_key="episode"`；`cache_values` 静态数据集缓存边界（storage revision 变更即失效）；`strict_length=False` 允许短轨迹但实际 batch 可能不足额；`pad_output` 用复制末步补齐并写 `("collector","mask")`。

### 外部连接
- OUT：`_extension.py`（CUDA segment tree）、`_utils.py`、`storages.py`（类型引用）、`replay_buffers/utils.py`（轨迹边界检索）。
- IN 14 个：RB 核心、her、scheduler、7 个 datasets 加载器、openml 环境、trainers helpers、on_policy。

### 数据流与坑
- Sampler 只见索引不见数据：`sample(storage, batch_size) -> (index, info)`，取数在 ReplayBuffer._sample 完成——info 里的 `priority_weight` 会被 loss（如 DQN）用来加权 TD 误差。
- 坑：SliceSampler 检索轨迹边界慢，官方建议优先 `end_key` 而非 `traj_key`，并开 `compile/cache_values/use_gpu`（1696 docstring note）。
- 坑：PER 的 α=0 退化为均匀但仍有 IS 权重开销；β 退火要外部用 scheduler.py 的 ParameterScheduler 驱动。

---

## torchrl/data/replay_buffers/storages.py

### 架构角色
存储后端全家桶（2962 行，tags=`replay-buffer/storage/memmap/core`）：**决定"数据物理上放哪"**——内存 list、连续张量、磁盘 memmap、压缩列表、多路集成。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| 87-164 | `_cleanup_all_memmap_storages` / `_signal_cleanup_handler` / `_register_cleanup_handlers` | memmap 全局清理：atexit + SIGTERM/SIGINT 双保险，防脏文件 |
| 172 | `Storage`(ABC) | 契约：set/get/attach/state_dict/checkpointer；管理 mutation revision |
| 482 | `ListStorage` | Python list 容器，任意对象按索引读写 |
| 687 | `LazyStackStorage` | ListStorage 变体，读取时懒堆叠 |
| 760 | `TensorStorage` | TensorDict/pytree 树形容器，支持条件补丁/扁平化/memmap 读 |
| **1517** | **`LazyTensorStorage`** | **首条数据到达才按 schema 分配张量空间** |
| **1769** | **`LazyMemmapStorage`** | 惰性 memmap：超内存大数据集零拷贝共享 |
| 2136 | `CompressedListStorage` | 逐条压缩/解压 + 专属 Checkpointer |
| 2451 | `StorageEnsemble` | 按概率路由多子存储 |
| 2603 | `StoreStorage` | 整体存取（TCPStore 分布式共享） |
| 2894-2960 | `_stack_anything` / `_get_default_collate` / `_make_memmap` | collate 工具族 |

### 精读 LazyTensorStorage（1517-1768）
docstring（1518-1600）三要点：`device="auto"` 从首批数据推断（默认 cpu 防 GPU 误放 OOM）；`ndim>1` 时容量按多维计（如 [3,4] 形状 ndim=2 容量 12）但 `trajs_per_batch` 采集必须 ndim=1（1535-1539 重要警告）；`shared_init=True` 开多进程协调初始化——**首进程 memmap 初始化，其余进程等待后加载共享**（1545-1547），`cleanup_memmap=True` 初始化完删临时文件回 RAM。
构造（1604-1631）后 storage=None，直到第一条数据 `set()` 触发按其结构分配——这就是"Lazy"的全部含义：用户无需预先声明 schema，TensorDict 的键结构即 schema。

### 外部连接
- OUT：`_utils.py`、`checkpointers.py`（各存储专属检查点器）、`replay_buffers/utils.py`。
- IN 18 个：RB 核心、samplers、writers、her、offline_to_online、sample_units、8 个 datasets、map/tree（MCTS）、trainers helpers。

### 数据流
`writer.extend(data)` → `storage.set(index, data)`：Tensor 型直接把 data 写进预分配张量的对应行（torch 索引赋值，支持共享内存/memmap 跨进程可见）；`sample` → `storage.get(index)` 返回该行视图（LazyMemmap 下是磁盘映射视图，零拷贝读）。

### 模式与坑
- **模板方法 + 策略**：TensorStorage 定骨架，LazyTensor/LazyMemmap 只改"何时/在哪分配"。
- 坑：memmap 存储的清理依赖信号处理器注册（133-164）——异常 kill -9 仍会留脏文件，路径在 tmp，重跑占盘。
- 坑：LazyMemmapStorage 写入时有磁盘 I/O 尖峰，capacity 一次性映射满文件（sparse 文件），df 看到的占用与实际写入量可能不一致。

---

## torchrl/data/replay_buffers/writers.py

### 架构角色
写入策略全家桶（1114 行，tags=`replay-buffer/writer/cursor-management`）：**决定"新数据写到哪个槽位"**——环形覆写、不可变、Top-N 保留、多路路由。

### 内部结构
| 行号 | 类 | 职责 |
|---|---|---|
| 58 | `Writer`(ABC) | 契约：register_storage/add/extend + 写入索引计算 |
| 170 | `ImmutableDatasetWriter` | 拒绝一切写（只读离线数据集） |
| **197** | **`RoundRobinWriter`** | 环形游标顺序覆写（默认） |
| 614 | `TensorDictRoundRobinWriter` | 按 TensorDict 内容算写入索引 |
| 692 | `TensorDictMaxValueWriter` | 按标量键（reward/q_value）只保留 Top-N |
| 1012 | `WriterEnsemble` | 按权重路由多子写入器 |

### 精读 RoundRobinWriter（197-613）
`add`（421-435）：**先推进游标再写数据**（424-425 注释："update the cursor first to avoid race conditions between workers"——多进程共享 buffer 时两个 worker 不会拿到同一槽）→ `storage.set(_cursor, data)` → `_bump_generation`（世代计数 +1）→ `_replicate_index`（把扁平索引展开成 storage 形状）→ `_mark_update_entities`。
`extend`（437-464）：batch_size 判定三分支（TensorDict/Tensor 走 len，list 走 len，其他 pytree 取首个叶子长度）→ `torch.arange(cur, cur+n) % max_size` 一次性算环形索引 → 同样先移游标后写。
`write_at`（466-485）：定点写不动游标，**每写必 bump generation**——"handles previously handed out for those slots are stale"（469-470），这是 StalenessAwareSampler/条件更新的版本基础。`_update_storage_len_for_write_at`（487-499）保证 write_at 越界时抬高 storage._len。
世代追踪：`state_dict`（501-505）带 `_generation` 张量，跨设备世代张量对齐在 load 时处理。

### 外部连接
- OUT：`_utils.py`、`storages.py`、`replay_buffers/utils.py`。
- IN 9 个：RB 核心、7 个 datasets 加载器（它们用 ImmutableDatasetWriter 或 RoundRobin 预填充）。

### 数据流与坑
- Writer 是 RB 与 Storage 之间唯一的写入口：index 由 writer 计算、返回给 RB 再转给 sampler 登记——**索引的单一事实来源是 writer**。
- 坑：`TensorDictMaxValueWriter` 需要数据里的标量键，且初始填满阶段行为与 RoundRobin 相同（前 max_size 条照单全收），之后才开始淘汰。
- 坑：环形覆写后旧索引仍可被采样（sampler 只看 `len(storage)`），不存在"写入即失效"——要用世代/条件更新机制显式管理陈旧性。

---

## torchrl/envs/common.py

### 架构角色
**环境体系中枢**（4658 行最大单文件之一，IN edges **62 个**）：定义一切环境的根类 `EnvBase`。图谱 tour 第 4 站："统一 _reset/_step/_step_and_maybe_reset 接口，输入输出都是 TensorDict，batch 维度即并行环境数"。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| 71/90/107 | `_maybe_unlock`/`_cache_value`/`_clear_cache_when_set` | spec 解锁与属性缓存装饰器三件套 |
| **124** | **`EnvMetaData`** | 批大小+全套 spec 的可序列化快照（tensordict/specs 强制存 CPU，161-172 设备注释解释了为何避免触碰 CUDA stream） |
| 306 | `_EnvPostInit`(ABCMeta) | 环境元类：实例化后自动 batch_size 锁定、spec 校验、元数据注册；还承接 `policy=`/`spec_locked`/`auto_reset`/`compile=` 这些"不在 `__init__` 签名里"的 kwargs（EnvBase 文档 423-470 明说） |
| **404** | **`EnvBase`(nn.Module)** | 一切环境的根类 |
| 4463 | `_EnvWrapper` | 包装类环境基类：属性代理到 `self._env`，GymLikeEnv 的父类 |
| 4596 | `make_tensordict` | 用环境+策略 spec 构造初始 reset TensorDict 的工厂 |
| 4617 | `_get_sync_func` | 策略/环境设备异同 → 设备同步函数或 no-op |

### 精读 EnvBase
**step（2340-2421）**：公共流程 = 形状断言 → 弹出 `_step` 部分步进掩码（2360-2381：batch_locked 与否两条路——部分 step 让批量环境里只有部分子环境真正前进）→ `next_preset = tensordict.get("next")`（2383：**输入里预置的 next 键会覆盖环境计算结果**，2388-2394，这是调试/强迫注入的机关）→ `self._step(tensordict)`（子类实现的抽象方法，3097 声明）→ `_step_proc_data` 对齐批维度 → `tensordict.set("next", next_tensordict)`（2395）。
**done 语义 `_complete_done`（2423-2483）**：done/terminated/truncated 三键的补全规则——缺省补 False，但两条特例：有 done 无 terminated 时 done 值拷给 terminated（2457-2467）；有 terminated 无 done 时 done = terminated | truncated（2468-2477）；只有 done+truncated 却缺 terminated 直接报错（2462-2465，无法推断）。**这三键语义是全库 rollout/价值估计的基石**。
**rollout（3449-3868）**：签名即 API 哲学——`policy` 可为任意 callable（3842 起 `_make_compatible_policy` 自动包装）；`actions` 可迭代对象直接开环回放（3750-3767：包成"从迭代器取动作"的 policy，sized 时 max_steps 被 len 截断）；`break_when_any_done` 默认 True、`break_when_all_done` 默认 False 且互斥（3724-3732）；`auto_reset=False` 必须传 tensordict 且会 `maybe_reset`（3778-3781）；docstring 3719-3726 给出"rollout 循环 + step_mdp 接力"的标准采集范式。
**step_mdp 方法版（3869）**：把 envs/utils.step_mdp 缓存键值后复用（3943 `_step_mdp` 生成缓存版 callable）。

### 外部连接
- OUT：`_utils.py`、`tensor_specs.py`、`data/utils.py`、`envs/utils.py`。
- IN 62 个：collectors 五件套、envs 全家族（custom 五环境 + libs 二十余包装器 + llm + model_based + transforms）、trainers 全家族、testing。

### 数据流
`td = env.reset()`（3108：可选 tensordict 传入部分 reset 掩码）→ policy(td) 写 action → `env.step(td)`：td 原地更新，新增 `"next"` 子 TensorDict（observation/reward/done/...）→ `step_mdp(td)` 把 next 提升为根 → 循环。rollout 把每步结果沿时间维 stack 成 `[T, B, ...]`。

### 模式与坑
- **模板方法**：step/reset/rollout 是公共骨架，子类只写 `_step`/`_reset`——公共层统一处理形状、done 补全、部分步进、设备。
- **元类注入 kwargs**（`policy=`/`compile=`/`spec_locked=`）不在任何子类 `__init__` 签名里，但处处可用——读子类源码找不到这些参数是正常的。
- 坑：`spec_locked=True` 默认开启后，运行时改 spec 必须 `set_spec_lock_()` 解锁（`_maybe_unlock` 装饰器内部自动处理）。
- 坑：EnvBase 继承 nn.Module——环境参数会进 `state_dict()`，也被 to()/compile() 管；自定义环境忘记调 super().__init__() 会出现各种灵异。

---

## torchrl/envs/utils.py

### 架构角色
envs 包核心工具集（1740 行，IN edges **65 个**——连 objectives 全家族都在用，tags=`utility/environment/spec-validation/marl/core`）。四根支柱：`step_mdp`（MDP 时间步切换）、`check_env_specs`（spec 对账）、`make_composite_from_td`（数据反推 spec）、MARL 分组。

### 内部结构
| 行号 | 符号 | 职责 |
|---|---|---|
| 79 | `_StepMDP` | step_mdp 的类封装（嵌套键排除树打印/keep_other/exclude 语义） |
| **327** | **`step_mdp`** | 核心时间步切换：next_* 提升为当前键 |
| 502/543 | `_set_single_key`/`_set` | 搬运辅助（嵌套展开） |
| 653 | `_per_level_env_check` | 逐层比较两份 TensorDict 的 key/shape/dtype |
| **686** | **`check_env_specs`** | 随机 rollout 对账 spec |
| 928 | `make_composite_from_td` | 数据 → Unbounded Composite |
| 1001 | `clear_mpi_env_vars` | 防 MPI 误连集群 |
| 1026/1101 | `MarlGroupMapType`/`check_marl_grouping` | MARL 分组（everyone/independents/global-state…） |
| 1142/1269 | `_terminated_or_truncated`/`terminated_or_truncated` | 轨迹终止判定 |
| 1446 | `_update_during_reset` | 部分重置时合并掩码保留旧值 |
| 1517/1655 | `_make_compatible_policy`/`_policy_is_tensordict_compatible` | 任意 callable 策略包装 |
| 1709 | `_NonParametricPolicyWrapper` | 无参数策略包成 nn.Module |

### 精读
**step_mdp（327-501）**：默认 `exclude_reward=True, exclude_done=False, exclude_action=True`（343-346）——语义注释在 docstring：观测/奖励/done 从 next 拷到根，**当前 action 被丢弃**（新时刻要新动作），done 却保留（rollout 循环要靠它判断）。docstring 380-401 的三个 print 示例把 exclude 开关的行为演示得明明白白。
**check_env_specs（686-765+）**：`fake_tensordict = env.fake_tensordict()`（754，按 spec 造的"应该长这样"）vs `real_tensordict = env.rollout(3, ...)`（759-765，真实跑 3 步）→ 逐键 `_per_level_env_check`。`break_when_any_done="both"` 两种都测（727-743）；seed 传入时用 `_rng_decorator` 保护全局 RNG（744-752）。docstring 720-722 警告：**这函数会动 env 的 seed，训练脚本里别调用，离线检查用**。
**make_composite_from_td（928-997）**：递归把 TensorDict 映成全 Unbounded 的 Composite（963-996 的字典推导三分支：嵌套集合→递归 / non_tensor→NonTensor spec（以 `view(-1)[0].data` 为模板）/ 其他→Unbounded）；`dynamic_shape=True` 时末维置 -1（变长序列）。

### 外部连接
- OUT：`_utils.py`、`tensor_specs.py`、`data/utils.py`、`modules/tensordict_module/exploration.py`（MarlGroupMapType 相关）。
- IN 65 个：collectors 全家族、envs 全家族、objectives 十余损失（advantages/value 估计要用 terminated_or_truncated）、record/render、testing、trainers。

### 数据流与坑
- step_mdp 是采集循环的"节拍器"：`env.rollout(...)` 内部末步、collector 每步、Trainer 的 on-policy 批处理都调它；`EnvBase.step_mdp`（common.py:3869）是其缓存版。
- 坑：`check_env_specs` 只查 shape/dtype/device，不查值域（除非配 `_CHECK_SPEC_ENCODE`）——spec 值域写错它不报。
- 坑：`make_composite_from_td` 产出全是 Unbounded——适合做占位/对账，不能当动作空间用（project 会失效）。

---

## torchrl/envs/batched_envs.py

### 架构角色
批量（向量化）环境引擎（3966 行，tags=`vec-env/parallel/multiprocessing/core`）：`BatchedEnvBase` 抽象 + `SerialEnv`/`ParallelEnv` 双执行器。上游只有 7 个直接 import（envs/__init__、brax/libero/mujoco_playground 三个包装、vec_envs 兼容 shim、testing、trainers helpers），但 **ParallelEnv 是 collector 高吞吐的物理基础**。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| 115 | `_check_start` | 未 start 就 step/reset 的明确报错 |
| 141 | `_normalize_batched_env_index` | 各种索引形态 → (worker_idx, env_idx) |
| **175/214** | **`_dispatch_caller_parallel`/`_dispatch_caller_serial`** | 调用分派代理：`env.some_attr` 广播到所有子环境收集结果列表 |
| 227 | `lazy` | 惰性求值装饰器 |
| 251 | `_PEnvMeta` | ParallelEnv 元类（post-init + 元数据展开） |
| **322** | **`BatchedEnvBase`** | 子环境集合生命周期（start/shutdown）、批量 spec 聚合、select_and_clone、聚合 state_dict |
| 1546 | `SerialEnv` | 同进程顺序 step/reset |
| **1918** | **`ParallelEnv`** | 每子环境一进程：管道+共享内存通信、worker 故障清理、种子/权重分发 |
| 3309 | `_recursively_strip_locks_from_state_dict` | 剔除锁对象使可序列化 |
| **3322** | **`_run_worker_pipe_shared_mem`** | worker 主循环（共享内存模式） |
| 3655 | `_run_worker_pipe_direct` | worker 主循环（直接管道模式） |

### 精读 _run_worker_pipe_shared_mem（3322-3654）
入口先过滤警告、按需 `torch.set_num_threads`（3340-3341，fork 模式防线程爆炸）、探测 CUDA 张量决定用 `torch.cuda.Event` 还是同步信号（3343-3357）、构造或接收环境后 **`env.set_spec_lock_()`**（3370，worker 侧锁 spec）。
主循环（3400-3416）：`child_pipe.poll(_timeout)` 等命令，超时抛 `TimeoutError`（可用环境变量 `BATCHED_PIPE_TIMEOUT` 调），EOF 视为父进程死亡；每 1000 条命令 debug 日志一条（3406-3411）。命令协议：`"init"`（3437-3453：拆 `shared_tensordict` 成 root/next 两视图并 unlock）→ `"reset"`（3455-3470：只 select 必要键传给子环境，**避免整个缓冲区回传的副作用**）→ `"step"` → `"seed"` → …。**零拷贝通信**：worker 直接在共享 TensorDict 缓冲区上 `update_` 写数据（3468-3470），管道只传命令不传张量。

### 外部连接
- OUT：`_utils.py`、`tensor_specs.py`、`data/utils.py`、`envs/common.py`（继承 EnvBase）、`env_creator.py`（EnvCreator 跨进程构造）、`libs/envpool.py`、`envs/utils.py`。
- IN 7 个（见上）。

### 数据流
ParallelEnv._step（2789）：把输入 TensorDict 的 action 切片写进各 worker 的共享缓冲 → 管道广播 `"step"` → 各 worker 调子环境 `_step` 并把 next 写回共享缓冲 → 主进程聚合。reset 走 `_reset`（3006）+ 部分重置掩码（`_reset` 键）。SerialEnv._step（1735）则纯顺序 for 循环。

### 模式与坑
- **代理模式**（`_dispatch_caller_parallel`）：`env.env_method(...)` / 属性访问被透明广播——ParallelEnv 用起来像单环境。
- 坑：worker lambda 不可 pickle 会被 `_is_unpicklable_lambda`（239）拦下提示用 EnvCreator；环境构造函数传 lambda 给 ParallelEnv 是新手第一大坑。
- 坑：`mp_event.set()` 通知就绪，但共享内存模式下主进程读数据前要确保 event/同步原语配对——直接读未就绪缓冲会拿到脏数据。
- 坑：SerialEnv 与 ParallelEnv 的 spec 必须同构（BatchedEnvBase 聚合校验），异构环境要用 Stacked spec（-1 维）。

---

## torchrl/envs/libs/gym.py

### 架构角色
OpenAI Gym/Gymnasium 适配核心（2333 行，tags=`gym/gymnasium/wrapper/spec-conversion/core`）：**40+ 环境后端里最典型的适配样例**——gym 的 `(obs, reward, done, info)` 协议 → torchrl 的 TensorDict 协议。图谱里 habitat/isaac/pettingzoo/procgen/robohive/safety_gymnasium/vmas 等包装器都反过来 import 它（借 GymEnv 基类）。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| 79-94 | `_patch_legacy_ale_py_gym_env` ×4 | `implement_for` 按版本四份实现的 ale-py 兼容补丁 |
| **138** | **`set_gym_backend`** | gym↔gymnasium 全局后端切换上下文管理器/装饰器 |
| 268 | `gym_backend` | 查询/设置全局后端（支持子模块访问） |
| **310/343** | **`_ConversionRegistry`/`register_gym_spec_conversion`** | spec 转换器注册表（UserDict 按类型路由） |
| **383** | **`_gym_to_torchrl_spec_transform`** | gym space → TensorSpec 主入口：查注册表分发，batch_size 非空先递归再 expand |
| 431-712 | `convert_*` 家族 | Tuple→Composite、Discrete→OneHot/Categorical、MultiBinary→Binary、MultiDiscrete→MultiOneHot/MultiCategorical、Box→Bounded、Sequence、Dict→Composite 递归、Text→NonTensor |
| 871 | `_GymAsyncMeta` | Gym 系元类：异步/向量化环境 post-init 特化 |
| **972** | **`GymWrapper`**（GymLikeEnv + `_GymAsyncMeta`） | 全功能包装器：像素/状态双模式、info 读取器、向量化批大小推断、新旧 render API 兼容 |
| 1288 | `read_action` | one-hot/类别 spec 且单元素非批环境时降级成 `int(action)`（某些 env 只吃整数索引） |
| 1300-1330 | `_build_gym_env` ×3 | `implement_for` 按 gym 版本选 PixelObservationWrapper 的三种构造法 |
| 1775 | `_reset` | 批量（向量化）gym 环境的 reset 特化：有 `_reset` 掩码且非全 True 时直接跳过（gym 向量化环境 step 内自动 reset） |
| **1805** | **`GymEnv`** | 用户入口：环境名+kwargs 构造；`num_envs`→gym 向量化、`num_workers`→ParallelEnv（元类处理，1821-1828） |
| 2104/2146 | `MOGymWrapper`/`MOGymEnv` | 多目标 gym（奖励为向量） |
| 2177 | `terminal_obs_reader` | 读 info 里的 `terminal_observation`（向量化环境截断时的最终观测）——default_info_dict_reader 子类 |

### 精读
**spec 双向转换**：`_gym_to_torchrl_spec_transform`（383-430）是纯注册表分发——`conversion_func = _conversion_registry[type(spec)]`（411）——开闭原则的教科书：新 gym space 类型只需 `register_gym_spec_conversion` 注册，不改主函数。`convert_box_spec`（526）处理上下界与 dtype（inf 边界退化 Unbounded）；`convert_discrete_spec`（456）按 `categorical_action_encoding` 决定 OneHot（默认）还是 Categorical。
**版本地狱的治理**：`implement_for` 装饰器让同一函数名有 3-4 份按 gym/gymnasium 版本选择的实现（79-94、1300-1330、653-712 的 `_box_convert` 五连）——这是 gym 生态碎片化（0.19/0.26 断层、gymnasium 分叉）的直接代价，也是 torchrl 能"同时支持两后端"的核心手段。`set_gym_backend`（138-267）+ `gym_backend()`（268-309）用全局状态+上下文管理器让同一份代码跑在两个生态上。

### 外部连接
- OUT：`_utils.py`、`tensor_specs.py`、`data/utils.py`、`envs/common.py`、`envs/gym_like.py`（继承其 obs/reward/action 解析骨架）、`envs/utils.py`。
- IN 14 个：`libs/__init__`、`_gym_utils`、habitat、isaac_lab、isaacgym、pettingzoo、procgen、robohive、safety_gymnasium、vmas、testing 两件、trainers 两个 config/helpers。

### 数据流
`GymEnv("CartPole-v1")`：gym.make → 包装（像素模式下按版本套 PixelObservationWrapper）→ `_build_specs` 用转换注册表把 observation_space/action_space 映成 Composite 树。step：TensorDict 的 action 键 → `read_action`（1288：one-hot 张量可能要降 int）→ 底层 `env.step` → obs/reward/done 经 spec.encode 进 `"next"` 子 TensorDict，info 字典由 info_reader（如 terminal_obs_reader）解析成附加键。

### 模式与坑
- **适配器 + 注册表 + 版本分发**三件套是所有 libs/*.py 的模板（dm_control/brax/jumanji 同构）。
- 坑：`from_pixels=True` 时旧版 gym 需要 `gym.make(..., render_mode="rgb_array")`，否则走 EnvCompatibility 兼容层并警告（1317-1330）。
- 坑：向量化 gym 环境（num_envs>1）自带 auto-reset，`_reset`（1775-1796）对部分 reset 掩码的处理是"非全 True 就跳过"——与 torchrl 原生 ParallelEnv 的语义差异要靠 `terminal_obs_reader` 补最终观测。
- 坑：默认 one-hot 离散动作；要类别索引必须 `categorical_action_encoding=True`（GymEnv 文档 1812-1815）。

---

## torchrl/envs/transforms/_base.py

### 架构角色
**变换体系核心**（2118 行，tags=`core/transform/base-class/container`）：`Transform` 基类（nn.Module）+ `TransformedEnv` 容器 + `Compose` 组合器。图谱 tour 第 6 站称 Transform fan-in 86——是"环境之上可组合预处理"的全部基础。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| **104/123** | **`_apply_to_composite`/`_apply_to_composite_inv`** | 装饰器：把单 spec 函数自动映射到 Composite 每个叶子（inv 版交换 in/out 键） |
| **178** | **`Transform`(nn.Module)** | 一切变换的基类 |
| 350-428 | `Transform._reset`/`_step` | 默认直通实现（子类按需覆写） |
| 715-792 | `transform_observation_spec` 等 6 钩子 | 默认恒等返回，子类按需覆写 |
| 931 | `_TEnvPostInit` | TransformedEnv 元类钩子（run_type_checks 等） |
| **944** | **`TransformedEnv`**(EnvBase) | 用变换序列包装 EnvBase 的容器环境 |
| 1321 | `TransformedEnv._step` | 核心：逆变换 → 基环境 → 正变换 |
| **1627** | `ObservationTransform` | 观测类标记基类（in_keys 默认指向 observation） |
| **1650** | **`Compose`** | 组合容器：调用/spec 变换/reset/clone 依次分派 |
| 2073 | `_CallableTransform` | 任意 callable → Transform 适配器 |
| 2094 | `AutoResetEnv` | 原生 auto-reset 环境的 TransformedEnv 特化 |

### 精读
**Transform 子类化指南**（docstring 196-218）本身就是 API 设计：数据无差别 → 覆写 `_apply_transform`/`_inv_apply_transform`；要看 step 的输入+输出 → 覆写 `_step`；只动数据流 → `_call`/`_inv_call`；要进回放缓冲用 → `forward`/`inv`；**改了数据必须改 spec**——顶层 `transform_output_spec`/`transform_input_spec`，叶子级 `transform_observation_spec` 等 6 个钩子（715-792 默认全恒等）。`_apply_to_composite`（104-122）让叶子钩子写一遍就能作用于整棵 Composite——全部 `_observation.py`/`_normalization.py` 里的变换都靠它省掉遍历样板。
**TransformedEnv._step（1321-1390）**：三段式——`tensordict_in = self.transform.inv(tensordict)`（1325，**动作逆变换在进环境前**：如 ActionScaling 把策略输出还原到原始域）→ `next_tensordict = self.base_env._step(tensordict_in)` + `_complete_done` 补 done（1357-1365）→ `next_tensordict = self.transform._step(tensordict_in, next_tensordict)`（1367，**观测正变换在出环境后**：归一化/裁剪/帧堆叠）。部分步进（1328-1354）与 EnvBase.step 同一套 `_step` 掩码逻辑。
**Compose._step（1777-1782）**：朴素 for 循环 `for t in self.transforms: next = t._step(td_in, next)`——顺序即语义。
**TransformedEnv 构造（944-1014）**：`cache_specs=True` 默认——spec 只变换一次缓存（967-970 警告：训练中变换对象会变就设 False）；`auto_unwrap`（973-975）：包已变换环境会自动摊平内层变换（986-988 示例），该行为将在 v0.9 翻转。HEAD commit 3b6b5b9 又把 spec 锁定设为默认——性能三连：cache + lock + 恒等钩子直通。

### 外部连接
- OUT：`_utils.py`、`tensor_specs.py`、`envs/common.py`（继承 EnvBase）、`transforms/utils.py`、`envs/utils.py`。
- IN 17 个：`transforms/transforms.py`（barrel）+ 14 个实现模块（_action/_clip/_device/_env/_keys/_misc/_normalization/_observation/_primitive/_reward/_tensor/_timer/_video）+ 3 个 MuJoCo custom 环境 + gym_transforms。

### 数据流
`TransformedEnv(GymEnv(...), Compose(ToTensorImage(), ObservationNorm(...)))`：policy 输出 action → `transform.inv`（若 ObservationNorm 有逆、ActionScaling 有逆则作用于对应键）→ `base_env._step` → `transform._step` 逐个改写 next 里的 observation（归一化统计在 transform 自身的 buffer 里）→ rollout 侧 `transform_observation_spec` 同步把 spec 的 shape/dtype/值域改掉——**数据与 spec 永远同步变换**，这是 torchrl 区别于裸 gym wrapper 的根本。

### 模式与坑
- **装饰器/责任链 + 组合**：Transform 是 nn.Module（参数可训练可持久化，ObservationNorm 的统计就是 buffer）；TransformedEnv 是 EnvBase（可再包一层）。
- 坑：`cache_specs=True` 时运行中改 transform（如手动调 ObservationNorm 统计没问题，但换 out_keys）不会反映到 spec。
- 坑：变换顺序=书写顺序，`inv` 逆序执行——`Compose(A, B).inv == B.inv ∘ A.inv`；观测归一化放错 action 变换前后语义完全不同。
- 坑：`Transform.parent` 是"基环境+此前所有变换"、`container` 是宿主（docstring 208-210）——变换内访问环境的正道，别直接抓全局。

---

## torchrl/envs/transforms/transforms.py

### 架构角色
**纯 barrel（桶文件）**（188 行，complexity=simple，CONTAINS=0）：本版本已把昔日 7000+ 行的 transforms 单体拆成 14 个按类别命名的私有模块（`_base`/`_action`/`_observation`/`_normalization`/...），此文件只做聚合再导出。模块 docstring（5-11 行）自述："Backward-compatible re-export hub... Importing from `torchrl.envs.transforms` (the public API) or from this module (legacy path) both continue to work unchanged."

### 内部结构
| 行号 | 来源模块 | 导出代表 |
|---|---|---|
| 25-37 | `_base` | `Transform`/`TransformedEnv`/`Compose`/`ObservationTransform`/`AutoResetEnv` |
| 14-23 | `_action` | `ActionScaling`/`ActionMask`/`DiscreteActionProjection`/`ActionChunkTransform`/`MultiAction` |
| 38-43 | `_clip`/`_device` | `ClipTransform`/`ExpandAs`；`DoubleToFloat`/`DTypeCastTransform`/`DeviceCastTransform` |
| 44-57 | `_env` | `StepCounter`/`TerminateTransform`/`TensorDictPrimer`/`FrameSkipTransform`/`InitTracker`/`NoopResetEnv`/`AutoResetTransform`/`RandomTruncationTransform`/`TrajCounter`/`BurnInTransform`/`gSDENoise`/`BatchSizeTransform` |
| 58-64 | `_keys` | `SelectTransform`/`ExcludeTransform`/`RenameTransform`/`FlattenTensorDict`/`RemoveEmptySpecs` |
| 65-74 | `_misc` | `FiniteTensorDictCheck`/`PinMemoryTransform`/`RandomCropTensorDict`/`TimeMaxPool`/`VecGymEnvTransform`/`ConditionalSkip` |
| 75-79 | `_normalization` | `ObservationNorm`/`RewardScaling`/`VecNorm` |
| 80-92 | `_observation` | `Resize`/`CenterCrop`/`GrayScale`/`CatFrames`/`ToTensorImage`/`Crop`/`PermuteTransform`/`Squeeze`/`Unsqueeze`/`FlattenObservation`/`NextObservationDelta` |
| 93 | `_primitive` | `MacroPrimitive`/`MacroPrimitiveTransform`（宏动作原语） |
| 94-103 | `_reward` | `RewardClipping`/`Reward2GoTransform`/`RewardSum`/`TargetReturn`/`BinarizeReward`/`SignTransform`/`SuccessReward` |
| 104-110 | `_tensor` | `CatTensors`/`UnaryTransform`/`Stack`/`Hash`/`Tokenizer` |
| 111-112 | `_timer`/`_video` | `Timer`（FPS 剖析）；`DecodeVideoTransform` |
| 114-188 | `__all__` | 共 74 个公共符号 |

### 外部连接（图谱边）
- OUT `imports` 14 条：全部指向 `_*.py` 实现模块（上文 KG 摘要即来自这些边）。
- IN 20 个：包括 `data/replay_buffers/replay_buffers.py`（RB 的 transform 参数默认从这取 Compose）、`data/replay_buffers/ray_buffer.py`、`objectives/llm/grpo.py`、`envs/llm/transforms/*`、`envs/model_based/dreamer.py`、trainers helpers——**barrel 是全库引用 transforms 的稳定门面**。

### 数据流与模式
无运行时数据流——import 期聚合。注意拆分后的依赖方向：14 个实现模块 import `_base`（1 条共享边），barrel 再聚合它们；外部只碰 barrel 或 `transforms/__init__`（后者另有 `__getattr__` 延迟导出）。

### 模式与坑
- **单体→类别拆分的教科书**：旧代码 `from torchrl.envs.transforms.transforms import X` 不破（本文件），新代码走 `torchrl.envs.transforms`（包 `__init__`）——双层兼容。
- 坑：往本文件加实现是错误方向——新变换应进对应类别模块再在 barrel 补 import + `__all__`；两个 `Tokenizer`（此处 `_tensor.Tokenizer` 与 `envs/llm/transforms/tokenizer.py` 的 LLM 分词器）同名不同物，看 import 来源辨别。

---

## 分片小结：三层的咬合方式

数据底座与环境系统的接缝就是 **spec**：`tensor_specs.py` 定义契约（Composite 树）→ `envs/common.py` 的 EnvBase 用 `observation_spec/action_spec/reward_spec/done_spec` 四棵树自我描述 → `check_env_specs`（envs/utils）用 fake vs real 对账 → gym.py 的注册表把外部空间译成 spec → `transforms/_base` 保证数据变 spec 同变 → rollout 产出的 TensorDict 流进 replay buffers（storages 按结构存、writers 定槽位、samplers 定策略）。向上（modules/objectives/collectors，见分片 2/3）传递的只有两样东西：**带键的 TensorDict 数据**与**描述这些键的 Composite spec**——这就是 README 三理念中"数据全程带名字/结构/设备"的全部工程含义。


---

# torchrl 核心文件精讲（2/3）：策略模块、分布与采集器

> 数据锚点：commit `3b6b5b9`（"[Performance] Lock TransformedEnv specs by default (#4121)"），知识图谱 analyzedAt 2026-08-20T06:24:51（gitCommitHash `3b6b5b9c1b326fb76eaba93d2ea3ebaba7c76644`）。
> 方法：图谱节点（summary/tags/complexity + contains + 出入边）× 源码精读（小文件全读、大文件类表 + 代表类精读）。所有行号均实测。
> 本篇覆盖 15 个文件（约 20,129 行），按依赖顺序分四组：**模块层 6**（models/common/probabilistic/actors/continuous/vecnorm）、**LLM 数据与环境 2**（prompt/chat）、**采集层 4**（_base/_single/_multi_base/llm-base）、**基础设施与测试 3**（mailbox/_checkpoint/mocking_classes）。

---

## torchrl/modules/models/models.py

### 架构角色
模块层的**网络骨干库**——TorchRL 里一切"带参数的计算"几乎都从这里的类开始搭。它不读 TensorDict（那是 tensordict_module 的职责），只提供纯 `nn.Module`：`MLP`/`ConvNet` 是通用底座，DDPG 全家族与 Dueling DQN 是算法专用网络，DT/OnlineDT 是序列决策（Decision Transformer）骨干。图谱定位：模块层，complexity=complex；被 `trainers/helpers/models.py`（make_dqn_actor/make_dreamer 工厂）与 `vla/models.py`（TinyVLA）直接消费——即"教程级 API → 骨干网络"的汇点。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| L29 | `MLP(nn.Sequential)` | 高度可配置感知机：深度/宽度/激活/归一化/lazy 全可配；**多输入沿最后维拼接**（obs + action 拼接进 critic 的标准做法） |
| L305 | `ConvNet(nn.Sequential)` | 2D 卷积网络，层堆叠完全可配置，内置 `default_atari_dqn` Atari 默认配置 |
| L572 | `Conv3dNet(nn.Sequential)` | 3D 卷积：视频/堆叠帧等时空输入 |
| L819 | `DuelingMlpDQNet(nn.Module)` | Dueling DQN MLP 版：价值流与优势流分离输出（`Q = V + A - mean(A)`） |
| L936 | `DuelingCnnDQNet(nn.Module)` | Dueling 的 CNN 版 |
| L1042 | `ddpg_init_last_layer()` | DDPG 最后一层均匀初始化，**scale=6e-4**（控制初始动作幅度，Lillicrap 原论文超参的工程延续） |
| L1081/L1207 | `DdpgCnnActor` / `DdpgMlpActor` | DDPG actor：卷积/MLP 主干 + tanh 输出有界连续动作 |
| L1278/L1401 | `DdpgCnnQNet` / `DdpgMlpQNet` | DDPG critic：评估 (状态, 动作) 价值 |
| L1507 | `OnlineDTActor(nn.Module)` | Online Decision Transformer（arXiv:2202.05607）的动作头 |
| L1609 | `DTActor(nn.Module)` | Decision Transformer actor（GPT2 骨干序列决策） |
| L1692/L1701 | `_iter_maybe_over_single` / `_ExecutableLayer` | 内部工具：单条目按次数重复；把任意 callable 包装成 nn.Module 层（让 lambda 也能进 Sequential） |

### 外部连接
- **出边（imports）5 条**：`_utils.py`（底层工具）、`data/utils.py`（dtype 映射等）、`models/decision_transformer.py`（OnlineDTActor 依赖的 GPT2 骨干）、`models/utils.py`（SqueezeLayer 等形状层）、`tensordict_module/common.py`（DistributionalDQNnet 等头模块）。
- **入边（被依赖）5 条**：`models/__init__.py`（barrel 再导出）、`models/cross_group_critic.py`（跨组 MARL critic 用 MLP）、`models/model_based.py`（Dreamer RSSM 组件）、`vla/models.py`（TinyVLA 用 ConvNet+MLP 编码器）、`trainers/helpers/models.py`（make_dqn_actor 一键构建）。
- 模式：**骨干只依赖更底层，头模块反向依赖骨干**——models.py 不 import 任何 tensordict_module，方向始终向下。

### 数据流
纯张量进出（无 TensorDict 语义）。典型链路：`MLP(obs_dim + action_dim → hidden → 1)` 作为 QValueActor 的 module，输入是沿最后维 concat 的 `[obs, action]`，输出标量 Q；`MLP(obs_dim → hidden → 2*action_dim)` 作为 ProbabilisticActor 的 module，输出被 `NormalParamWrapper` 拆成 loc/scale。多输入拼接发生在 MLP.forward：对 `in_keys` 对应的多个张量 `torch.cat([...], dim=-1)`。

### 模式与坑
- **坑 1：MLP 多输入靠"最后维拼接"**——若各输入形状不匹配（如 obs 是 `[B, T, D]` 而 action 是 `[B, D]`），不会报友好错误，会在 cat 时炸或静默广播错。用 RNN 时序数据接 MLP 要先确认时间维一致。
- **坑 2：DDPG 家族自带 tanh 出口与 6e-4 初始化**——如果你再套一层 TanhModule 或在 ProbabilisticActor 里配 TanhNormal，等于双重压缩，动作分布会异常集中在 0 附近。
- **模式：lazy 支持**——MLP 可用 `lazy_nodes=True` 延迟推断输入维度，配合 EnvBase spec 自动定型，是"spec 驱动建网"的关键一环。
- **模式：`_ExecutableLayer` 把 callable 变层**——所以 MLP 可以直接吃函数式变换（如 reshape lambda），不必为小操作写 Module 类。

---

## torchrl/modules/tensordict_module/common.py

### 架构角色
模块层的**枢纽基座**：`SafeModule` 是"nn.Module + TensorDict 读写协议 + TensorSpec 约束"三者合一的基类，几乎所有 torchrl 模块（actors/exploration/probabilistic/sequence）都是它的直接或间接子类。图谱入边高达 **11 条**（全库模块层最多），包括损失层（cql/dqn/qmixer）反向依赖它做类型检查——它是"什么算一个 torchrl 模块"的定义者。complexity=complex。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| L41 | `_check_all_str()` | 校验 in_keys/out_keys 全为字符串（容错嵌套 key） |
| L55 | `_forward_hook_safe_action()` | SafeModule 的 forward hook：把网络原始输出**投影到 action_spec 声明的键与域**，保证动作永远满足环境规范（越界自动裁剪/编码） |
| L97 | `SafeModule(TensorDictModule)` | 核心基类：in_keys/out_keys 约束 + spec 注册，forward 自动校验与投影 |
| L295 | `is_tensordict_compatible()` | 探测 nn.Module 是否 TensorDict 兼容（是 TensorDictModuleBase 实例，或带 in_keys/out_keys） |
| L361 | `ensure_tensordict_compatible()` | 不兼容则按 module_key 包一层 SafeModule（采集器收编外部 policy 的入口） |
| L415 | `VmapModule(TensorDictModuleBase)` | 用 `torch.vmap` 包装 forward，服务 ensemble/向量化策略 |
| L478 | `DistributionalDQNnet(TensorDictModuleBase)` | 分布化 DQN 网络：主干 + support 数量输出头，配合 DistributionalQValueModule |

文件头部还有 functorch 的容错导入（旧版 torch 无 functorch 时不炸），体现对老版本兼容的防御式写法。

### 外部连接
- **出边 2 条**：`data/tensor_specs.py`（spec 体系）、`data/utils.py`。
- **入边 11 条**：`modules/__init__`、`models/__init__`、`models/models.py`、`tensordict_module/__init__`、`tensordict_module/actors.py`、`tensordict_module/exploration.py`、`tensordict_module/probabilistic.py`、`tensordict_module/sequence.py`、`objectives/cql.py`、`objectives/dqn.py`、`objectives/multiagent/qmixer.py`。
- 解读：**模块层的中介中心**。损失层只 import 它而不 import actors——损失代码通过 `is_tensordict_compatible`/`ensure_tensordict_compatible` 与任意策略解耦。

### 数据流
`SafeModule.forward(td) -> td`：从 `td` 按 `in_keys` 取张量列表 → 调内层 module → 把输出张量按 `out_keys` 写回同一 td。注册了 spec 时（如 `action_spec`），`_forward_hook_safe_action` 在写回前做域投影（Bounded → clip，OneHot → argmax/softmax 编码）。ensure 路径：外部普通 `nn.Module` 进来 → 包成 `SafeModule(module, in_keys=[module_key], out_keys=[module_key])` → 从此按 TensorDict 协议工作。

### 模式与坑
- **坑 1：spec 投影是隐式的**——给了 action_spec，hook 会静默修正越界动作。调试"为什么我的动作总是不对"时要意识到可能是 hook 在裁剪，而不是策略真的输出了那个值。
- **坑 2：`is_tensordict_compatible` 只查结构不查语义**——带 in_keys/out_keys 属性就算兼容，键名与环境对不对它不管。键名错配要到 rollout 时才炸。
- **模式：VmapModule 是 ensemble 的正解**——想跑 N 个参数不同的同构策略，不要 for 循环，直接 vmap 包装。
- **模式：这是收编第三方模型的适配器层**——HuggingFace 模型、自定义网络进 torchrl 生态的第一站就是 ensure_tensordict_compatible。

---

## torchrl/modules/tensordict_module/probabilistic.py

### 架构角色
**采样层基类**：把 tensordict.nn 的概率模块"安全化"——核心增量是接受 `TensorSpec` 约束采样域。`ProbabilisticActor`（actors.py）的采样能力全部由这里的两个类提供。图谱入边仅 2 条（`__init__` barrel 和 actors.py），出边 5 条——典型的**窄腰层**：上游接口窄，下游（分布族、采样工具）依赖深。

### 内部结构
| 行号 | 类 | 职责 |
|---|---|---|
| L36 | `SafeProbabilisticModule(ProbabilisticTensorDictModule)` | tensordict.nn ProbabilisticModule 的安全扩展：接受 TensorSpec 控制采样域，提供 sample/log_prob/entropy 及随机初始化 |
| L393 | `SafeProbabilisticTensorDictSequential(ProbabilisticTensorDictSequential, SafeSequential)` | 双继承：先按序执行确定模块（网络算参数）再采样（spec 约束输出） |

### 外部连接
- **出边 5 条**：`data/tensor_specs.py`、`modules/distributions/__init__.py`（分布族入口）、`modules/distributions/utils.py`（sample_and_log_prob/rsample_and_log_prob 原子化采样打分、FasterTransformedDistribution）、`tensordict_module/common.py`、`tensordict_module/sequence.py`（SafeSequential）。
- **入边 2 条**：`tensordict_module/__init__.py`、`tensordict_module/actors.py`。
- 解读：它是 actors ↔ distributions 之间的**契约层**——actors 决定"用什么分布、in_keys 是什么"，本文件决定"分布参数如何从 td 读出、采样如何受 spec 约束"。

### 数据流
`SafeProbabilisticTensorDictSequential.forward(td)`：先跑网络段（SafeSequential 语义，如 `MLP → "loc","scale"` 写入 td）→ 构造分布（`dist_class(**{k: td[k] for k in dist_kwargs_keys})`）→ 按 exploration_type 调 `sample`/`mode`/`mean`/确定性 → 写 `out_keys`（默认 `action`、`log_prob` 等，由 default_interaction_mode 与 kwargs 决定）。spec 在手时采样后投影回合法域。

### 模式与坑
- **坑 1：采样模式由全局 `exploration_type` 上下文控制**（`set_exploration_type`），不是构造参数。训练用 Random、评估用 Deterministic 的切换发生在采集器（`_single.py` rollout L2058 的 `with set_exploration_type(...)`）。忘记切换是"评估结果异常好/差"的经典原因。
- **坑 2：`default_interaction_mode` 的语义**——`"mode"`/`"mean"`/`"median"`/`"random"` 决定 Deterministic 类型下取什么，分布族不同默认不同（如 IndependentNormal 的 mode ≠ mean）。
- **模式：Safe 后缀的统一含义**——本库中 Safe* = tensordict.nn 原类 + TensorSpec 接受能力。actors.py 的所有复合类都遵循此命名约定。

---

## torchrl/modules/tensordict_module/actors.py

### 架构角色
**策略头大全——torchrl 模块层的 API 门面**：18 个类覆盖确定性策略、概率策略、Q 值策略、分布化 Q、Actor-Critic 复合、Decision Transformer、扩散策略与 VLA 多步动作。所有 losses（ddpg/dqn/sac/cql/qmixer）import 的 policy 类型都定义于此。complexity=complex，2981 行是模块层最大文件。**读懂本文件 = 读懂 torchrl 的策略 API 设计语言**。

### 内部结构（按行号）
| 行号 | 类 | 职责 |
|---|---|---|
| L36 | `Actor(SafeModule)` | 确定性策略头：任意网络 → SafeModule，in_keys 读观测写 `action`，可选 spec 约束 |
| L146 | `ProbabilisticActor(SafeProbabilisticTensorDictSequential)` | 概率策略头：网络出分布参数 → 采样 action+log_prob；支持 in_keys/分布族/温度/偏置等丰富配置，**torchrl 概率策略的标准入口** |
| L427 | `ValueOperator` | 价值网络头：TensorDictModule 包装，读观测写 `value` |
| L500 | `QValueModule` | Q 值头：按 action_space（one-hot/mult-one-hot/binary/categorical）把网络 logits 映射为 `action_value`/`action`，含 argmax 采样；默认键 `action`/`action_value`/`chosen_action_value` |
| L750 | `DistributionalQValueModule` | 分布化 Q 值头：support 上出 logits → softmax → 按期望聚合 |
| L938 | `QValueHook` | forward hook：网络输出 → 按动作空间变换写回（供 QValueActor 复用） |
| L1108 | `QValueActor` | 特征网络 + QValueHook 组合的 SafeSequential：一步完成 Q 计算与贪心动作选择 |
| L1415 | `ActorValueOperator` | **共享骨干 Actor-Critic**：common 编码网络 → policy 头 + value 头三段；`get_policy_operator()`/`get_value_operator()` 分别取出两个视图 |
| L1564 | `ActorCriticOperator` | 逆序版（先价值再加策略头），兼容旧 API |
| L2066 | `TanhModule` | 网络输出经 tanh 压缩到 spec [low,high] 且**可逆还原**（log_prob 校正交给上游分布）；无 spec 时自动推导 |
| L2280 | `MultiStepActorWrapper` | **VLA 动作 chunk 包装**：把演员的动作 chunk 按步切分写回、缓存剩余步，配合 `("collector","is_init")` 等键对齐步边界 |
| L2705 | `_DDPMModule` | DDPM 去噪内核：线性 beta 扩散调度对动作加噪/去噪，管理 timestep dtype，是 DiffusionActor 的内核 |

另有 `ActorCriticWrapper`（独立 actor+value 拼 SafeSequential）、`DistributionalQValueActor`/`DistributionalQValueHook`、`DecisionTransformerInferenceWrapper`（return-to-go 上下文 + 未来信息 mask）、`LMHeadActorValueOperator`（LLM RL：token 特征共享骨干双头）、`DiffusionActor`（SafeModule 包装 _DDPMModule）。

### 外部连接
- **出边 6 条**：`_utils.py`、`data/tensor_specs.py`、`data/utils.py`、`tensordict_module/common.py`（SafeModule 基类）、`tensordict_module/probabilistic.py`（采样层）、`tensordict_module/sequence.py`（SafeSequential）。
- **入边 6 条**：`tensordict_module/__init__.py` + 五个损失：`objectives/cql.py`、`ddpg.py`、`dqn.py`、`multiagent/qmixer.py`、`sac.py`。
- 解读：**策略头与损失是"接口级耦合"**——损失只认这里的类暴露的键（action_value/chosen_action_value 等），键约定即协议。

### 数据流
三条典型链路（键流转）：
1. **QValueActor**：`observation` → 特征网络 → 原始 logits → QValueHook 按 action_space 变换 → 写 `action_value`（全部 Q）+ `action`（argmax/one-hot）+ `chosen_action_value`（被选 Q 标量）。损失读 `action_value` 与 `("next","action_value")`。
2. **ProbabilisticActor**：`observation` → MLP → `loc`,`scale` → SafeProbabilistic 层采样 → `action`,`log_prob`（+ 可选 `distribution` 键留熵计算）。
3. **ActorValueOperator**：`observation` → common →（policy 头写 action）+（value 头写 value）一次性双写；训练时用 `get_value_operator()` 只跑 value 段，采集时用 `get_policy_operator()` 只跑 policy 段——**同一份参数、两个视图**，避免参数复制不同步。

### 模式与坑
- **坑 1：QValueModule 的键随 action_space 变**——categorical 空间的 action 是 int 索引，one-hot 是浮点向量，mult-one-hot 是拼接向量。损失模块对键形状有假设（DQNLoss 期望 `action_value` 形状 `[B, n]`），空间类型传错会在损失里炸而不是这里。
- **坑 2：ActorValueOperator 的双视图共享参数**——`get_policy_operator()` 取出的模块没有 value 头参数，state_dict 保存/加载时要用整体的，不能用子视图的，否则丢参数。
- **坑 3：TanhModule 与 TanhNormal 别叠用**——TanhModule 是给"确定性网络输出无界"场景的边界压缩；策略已经用 TanhNormal 采样时再加 TanhModule 会双重 tanh 且 log_prob 失真。
- **坑 4：MultiStepActorWrapper 改变了 rollout 的步语义**——环境每步消耗 chunk 中一个动作，剩余动作缓存在 wrapper 状态里；`is_init` 键标记轨迹开头时才重新生成 chunk。采集器测试若不带 is_init 键，行为会静默退化。
- **模式：Hook 拆分**——QValueActor = 网络 + Hook 的组合（而非子类），使同一 Hook 能被不同网络复用（Distributional 版只需换 Hook）。这是本文件 18 个类不膨胀的关键设计。

---

## torchrl/modules/distributions/continuous.py

### 架构角色
**RL 专用连续分布库**：标准 torch.distributions 缺的三样东西在这里补齐——(1) 对 TensorDict/compile 友好，(2) TanhNormal 的数值安全实现（SAC 的标准选择），(3) Delta/TanhDelta 确定性分布（DDPG 类策略做 log_prob 的载体）。图谱 tags 直指要害：`tanh-squash`、`numerical-stability`。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| L47 | `IndependentNormal(D.Independent)` | 对 loc 施加 **tanh 定位缩放**（`loc = tanh(loc/upscale)*upscale`，upscale 默认 1）防定位参数离 0 过远导致采样不稳与梯度爆炸；提供 update/mode/deterministic_sample |
| L138 | `SafeTanhTransform(D.TanhTransform)` | 数值安全 tanh：正逆变换均规避上溢/下溢，是 TanhNormal/TanhDelta 核心组件 |
| L159 | `NormalParamWrapper(nn.Module)` | 网络的均值/尺度输出包装成单个 params 张量（`[loc, scale]` 沿 -1 拼），对接概率 actor |
| L171 | `TruncatedNormal(D.Independent)` | TorchDict 友好截断正态：**委托 truncated_normal.py 的解析闭式实现**（移植自 toshas/torch_truncnorm） |
| L310/L324 | `_PatchedComposeTransform` / `_PatchedAffineTransform` | 对旧版 torch 逆变换行为的兼容补丁 |
| L337 | `TanhNormal(FasterTransformedDistribution)` | tanh 压缩正态（**SAC 标准选择**）：基于 FasterTransformedDistribution，`rsample_and_log_prob`、support 边界、safe log_prob；**scale 支持 callable**（compile 友好，避免捕获常量张量） |
| L651 | `uniform_sample_tanhnormal()` | ExplorationType.UNIFORM 模式的均匀随机采样 |
| L667 | `Delta(D.Distribution)` | Dirac delta：仅确定性采样与 log_prob（**log_prob 返回 ±inf/0**——at 时 0，否则 -inf），DDPG 类确定性策略用 |
| L755 | `TanhDelta(FasterTransformedDistribution)` | tanh 压缩 Delta：有界动作空间的确定性策略 |
| L881/L890 | `_uniform_sample_delta` / `_err_compile_safetanh` | UNIFORM 回退采样；compile 路径命中不兼容 safe-tanh 实现时抛友好错误 |

### 外部连接
- **出边 3 条**（很克制）：`_utils.py`、`distributions/truncated_normal.py`（解析闭式 cdf/icdf/entropy/log_prob/rsample）、`distributions/utils.py`（FasterTransformedDistribution 与原子采样打分）。
- **入边 1 条**：`distributions/__init__.py`（与 discrete 族一起统一导出）。
- 注意：probabilistic.py 通过 `distributions/__init__.py` 间接消费这里的全部类——**actors 的 dist_class 参数字符串（"TanhNormal" 等）最终解析到本文件**。

### 数据流
分布对象由 SafeProbabilisticModule 构造：td 中的 `loc`/`scale`（或 NormalParamWrapper 的单 params 再拆）→ `TanhNormal(loc, scale, upscale, low, high)` → `rsample_and_log_prob()` 一次产出 `action`（tanh 域内）+ `log_prob`（含 tanh 的 log-det-Jacobian 校正，safe 实现规避 ±inf）。UNIFORM 探索模式走 `uniform_sample_tanhnormal` 直接在 [low,high] 均匀采。Delta 路径：`Delta.at(sample)` 下 log_prob=0，采到别的样本 → -inf，DDPG 的"伪 log_prob"就靠这个语义。

### 模式与坑
- **坑 1：Delta.log_prob 的 ±inf 语义**——REINFORCE 式损失对 -inf 求梯度会得 NaN。DDPG/TD3 用确定性策略梯度绕开 log_prob，别把 Delta 喂给需要 log_prob 的损失（PPO 等）。
- **坑 2：IndependentNormal 的 tanh(loc) 定位缩放不是 TanhNormal**——前者只是参数重整化（分布仍是 Normal），后者才改变支撑集。名字相近语义完全不同。
- **坑 3：TruncatedNormal 是解析实现不是 reject sampling**——icdf 用闭式逼近，极深截断处精度有限；若发现边界概率异常优先查 upscale/low/high 配置。
- **模式：FasterTransformedDistribution 是性能层**——把 torch 的 TransformedDistribution 重写成免于反复 build 的形态，`rsample_and_log_prob` 合并计算是采集吞吐的关键路径。

---

## torchrl/envs/transforms/vecnorm.py

### 架构角色
**运行时归一化的新一代实现**（注意在 envs/transforms 而非 modules——它是 Transform，挂在 TransformedEnv 上）：在线 running mean/std 归一化观测与奖励，在并行环境间聚合统计、支持远程更新（mp/UUID 标识）与 torch.compile 兼容，服务大规模 PPO/A2C。图谱 tags：运行统计/并行环境。V1（VecNorm）已被 V2 取代。

### 内部结构
| 行号 | 成员 | 职责 |
|---|---|---|
| L34 | `VecNormV2(Transform)` | 主类：stateful/stateless 双模式 |
| L417 | `_step` | 归一化前的统计更新入口；处理 lock（并行写保护）与 `is_compiling`（compile 下统计更新路径切换） |
| L614 | `_stateful_update` | 有状态模式：本地 buffer 累积统计，_call 时用当前统计归一化 |
| L690 | `_stateless_update` | 无状态模式：统计由外部聚合后下发（多进程场景主进程统一算） |
| L711 | `transform_output_spec` | 改写输出 spec：把被归一化键的域改成归一化后的范围 |
| L927/L936 | `loc` / `scale` 属性 | 暴露当前统计量（还原/调试/远程同步用） |

### 外部连接
- **出边 4 条**：`data/tensor_specs.py`（改 spec）、`envs/common.py`（EnvBase）、`envs/transforms/transforms.py`（Transform 基类经 barrel）、`envs/transforms/utils.py`（数值校验/容错上下文）。
- **入边 1 条**：`transforms/__init__.py`。
- 跨层引用：`testing/mocking_classes.py` 有专门的 `CountingVecNormV2`（L1104）内嵌它测试交互——**归一化模块有专属测试替身**，说明其状态语义复杂度被官方认可。

### 数据流
观测进 `_call`：`(obs - loc) / max(scale, eps)` 写回原键；`("next","reward")` 同理（可选 return 归一化）。stateful 模式：每步 `_step` 先累积 batch 统计（Welford 式），lock 保证多 env 写安全。stateless/远程模式：各 worker 本地累积 → 主进程按 UUID 聚合 → 下发统一 loc/scale，各 env 用下发值归一化（collectors 的多进程架构里由 worker 侧 Transform 群协同）。动作反归一化可选：策略在归一化空间训练，输出前乘 scale 加 loc 还原到真实域。

### 模式与坑
- **坑 1：统计漂移改变观测语义**——训练中期 loc/scale 变了，同一观测的归一化值也变。on-policy 算法（PPO）要求同批数据用一致统计，旧数据重放时会轻微不一致（这正是 V2 锁定/聚合机制要缓解的）。
- **坑 2：奖励归一化会改变回报尺度**——配了 reward 归一化后，奖励超参（如 PPO 的 vf_coef 语义）等效变化；对比实验必须保持归一化配置一致。
- **坑 3：compile 兼容需要 stateless 路径**——`is_compiling` 分支说明 stateful 的 in-place 统计更新会破坏图；用 torch.compile 时走 stateless。
- **模式：Transform 挂在环境侧而非模块侧**——归一化属于"环境接口的一部分"（观测本来就是非平稳的），放 Transform 使策略模块保持无状态、可被多环境共享。

---

## torchrl/data/llm/prompt.py

### 架构角色
**SFT 提示数据的最小数据模型**：数据层、moderate 体量（198 行）。`PromptData` tensorclass 定义 RLHF/SFT 数据在 TensorDict 世界里的标准形状，`PromptTensorDictTokenizer` 负责把文本 prompt 编码成这个形状。它是 torchrl LLM 数据管线的**第一环**——datasets 语料（dataset.py）→ 本文件（prompt 编码）→ utils.py 的 RolloutFromModel（生成 rollout）。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L12 | `DEFAULT_DATASET` | 默认数据集 `"CarperAI/openai_summarize_tldr"`（RLHF 经典 TL;DR 语料） |
| L16 | `PromptData` | tensorclass：字段 `input_ids`/`attention_mask`/`prompt_rindex`（prompt 长度标记）/`labels`/`logits`/`loss` |
| L26 | `mask_label()` | 按 prompt 长度生成 **-100 掩码标签**——prompt 部分 label=-100（CrossEntropy 忽略），只对 completion 部分算损失 |
| L42 | `from_dataset()` | 从 HF datasets 直接构造 |
| L102 | `PromptTensorDictTokenizer(TensorDictTokenizer)` | prompt 专用 tokenizer 封装：逐样本自适应编码（不等长 batch 不炸），输出含 prompt_rindex 的 PromptData 兼容键 |
| L153/L171 | `__init__` / `__call__` | tokenizer 注入；sample（dict）→ 编码键值 |

### 外部连接
- **出边 1 条**：`data/llm/dataset.py`（TokenizedDatasetLoader：HF datasets → memmap TensorDict 分词缓存）。
- **入边 2 条**：`data/llm/__init__.py`（barrel）、`data/llm/utils.py`（RolloutFromModel：策略+奖励+参考模型从 PromptData 生成完整 rollout——**RLHF 数据管线下一棒**）。

### 数据流
文本样本（`{"prompt": "..."}`）→ PromptTensorDictTokenizer.__call__ → `input_ids [L]`、`attention_mask [L]`、`prompt_rindex`（标量，prompt token 数）。进策略后补 `labels`（mask_label 生成：前 rindex 个位置 -100）→ 训练时 CrossEntropy 只在 completion 段反传。`logits`/`loss` 字段在 rollout 阶段由模型写入（vLLM/本地推理结果落同一 tensorclass）。

### 模式与坑
- **坑 1：-100 是硬约定**——mask_label 的 -100 与 torch CrossEntropyLoss 的 ignore_index 对齐；自定义损失若忘了这约定会把 prompt 段算进损失（SFT 变 LM 训练）。
- **坑 2：`prompt_rindex` 而非 `prompt_mask`**——存标量索引省内存，但消费方要自己做 `arange < rindex` 才能得到 mask；直接拿去当 mask 用是类型错。
- **模式：tensorclass = 带 spec 的 dataclass**——PromptData 既是数据容器又是 spec 声明（形状/dtype 检查），这是 torchrl 数据层的统一风格：**数据模型前置、管线按 spec 对齐**。
- **模式：逐样本自适应编码**——tokenizer 对 batch 内不等长样本逐条处理再组织，避免 HF tokenizer 的 padding 假设与 TensorDict 的等批形约束打架。

---

## torchrl/envs/llm/chat.py

### 架构角色
**以 History 为中心的 LLM 环境基类**：环境层、complex。把"对话"建模为 EnvBase——policy 生成 response 是 action，环境返回更新后的 History 与终止信号。`ChatEnv` 支持 tokens/text/history 三种输入模式并自动生成对应 spec；`DatasetChatEnv` 把 dataloader 包装成可 endless 采样、支持分组 repeats 的对话环境。它是 GSM8K/MATH/IFEval/Countdown 四个数据集环境的**公共底座**。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L29 | `_ChatEnvMeta(_EnvPostInit)` | 元类：实例化参数含 tokenizer 时延迟注入 `with_tokenizer` 构造逻辑 |
| L48 | `_default_collate_fn` | 默认 collate：tensordict 的 default_collate_fn_torch 对 prompt batch 堆叠（**text→query 键改名**发生在这里） |
| L60 | `ChatEnv(EnvBase, metaclass=_ChatEnvMeta)` | 主类：三模式输入，自动生成 spec，实现 _step/_reset；`from_dataloader` 直接从数据集构造 |
| L182 | `with_tokenizer()` | 延迟注入 tokenizer 的构造路径 |
| L251-L343 | `_make_specs` × 4 | 按 history/text/tokens 模式生成对应的输入/输出 Composite spec |
| L410/420/433/443 | `_step` / `_step_history` / `_step_text` / `_step_tokens` | step 的三模式分发实现 |
| L453/505/513/523 | `_reset` / `_reset_history` / `_reset_text` / `_reset_tokens` | reset 的三模式分发实现 |
| L542 | `DatasetChatEnv(TransformedEnv)` | **注意：继承 TransformedEnv 不是 EnvBase**——把 dataloader 包装为环境，管理 endless 迭代器、分组 repeats 与 `reset_dataloader`（L782） |

### 外部连接
- **出边 5 条**：`data/__init__.py`、`data/llm/history.py`（History TensorClass：chat template 正向渲染与 chatml/qwen/direct 格式）、`envs/__init__.py`、`envs/common.py`（EnvBase）、`envs/llm/transforms/dataloading.py`（as_nested_tensor/as_padded_tensor 变长 batch 压缩、DataLoadingPrimer）、`modules/llm/policies/common.py`（Tokens/Masks/ChatHistory/LogProbs/Text 五个 TensorClass 与 LogProbValueWrapper——**LLM 策略侧的数据类型**）。
- **入边 5 条**：`envs/llm/__init__.py` + 四个数据集环境：`datasets/countdown.py`、`gsm8k.py`、`ifeval.py`、`math.py`。

### 数据流
reset：dataloader 取一条样本 → 按 data_key（默认 `"query"`）作为初始 prompt → History 初始化 → 写入观测键。step：td 中的 response 键（text 模式）或 token 键（tokens 模式）作为 action → 拼进 History → 产出 `("next", data_key)`（新 History/文本）与 done（对话终止判定，如 max rounds 或解析出终答）。text 模式下 `_default_collate_fn` 把 batch 的 prompt collate 时改名为 query——**环境侧键名与数据集列名的适配点**。

### 模式与坑
- **坑 1：三种模式的 spec 不同，tokenizer 注入是分水岭**——text 模式观测是字符串（NonTensor spec），tokens 模式是 int 张量。带 tokenizer 构造（元类注入）会切换 spec 形态；中途换模式要在构造时决定，不能运行时改。
- **坑 2：data_key 默认 "query"**——GSM8K 等子环境改写了 observation spec，键名与默认不同时容易拿 None。消费 prompt 用 `env.observation_spec` 查实际键。
- **坑 3：DatasetChatEnv 是 TransformedEnv**——它的 state_dict/序列化走 TransformedEnv 路径；dataloader 迭代器状态默认不进 checkpoint（endless 迭代器靠 reset_dataloader 重建）。
- **模式：环境三段式分发**（_step/_reset 各三个模式方法）是**策略模式在 EnvBase 约束下的落地**——EnvBase 接口固定（_step/_reset 抽象），变化点用内部分发吸收，子环境（GSM8K 等）只需组合不需继承 ChatEnv。

---

## torchrl/collectors/_base.py

### 架构角色
**采集器体系的抽象基类**：`BaseCollector`（IterableDataset）定义所有 Collector 的公共契约——权重同步编排（**WeightUpdater 旧通道 + WeightSyncScheme 新通道双轨**）、按批/按轨迹迭代、随机帧注入、profiling 钩子与生命周期管理。图谱入边 **10 条**：单进程、多进程、分布式（generic/ray/rpc/sync）、async-batched、LLM 全部采集器都继承它。complexity=complex。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L33 | `ProfileConfig` | worker 侧 torch.profiler 配置 dataclass（活动集/日程/输出路径/C++ profiler 选项映射） |
| L144 | `_ProfilerHook` | worker 进程内安装/停止 torch profiler 的钩子对象 |
| L220 | `BaseCollector(IterableDataset)` | 基类本体 |
| L924-L973 | `update_policy_weights_` × 6 个 @overload | **5 组重载签名**：按 WeightUpdater/WeightSyncScheme/列表/无更新等组合分发——类型上吸收新旧两代权重同步 API |
| L1414 | `__iter__` | 迭代入口：按 trajs_per_batch 分流 |
| L1426 | `_iter_by_trajectories` | 按轨迹迭代：用 `("collector","mask")` 标记轨迹有效帧（**trajs_per_batch 模式的核心机制**） |
| L1544/L1553 | `shutdown` / `iterator` | 生命周期终止；迭代器属性 |

类级约定：**回放缓冲写入用平坦 1-D**——当 collector 直连 RB 时，逐帧 add（`replay_buffer.add(td)`），而非按轨迹结构写入；轨迹信息由 `("collector","traj_ids")` 承载。

### 外部连接
- **出边 4 条**：`collectors/utils.py`（split_trajectories 轨迹切分、meta policy 构造、权重 CPU 映射）、`collectors/weight_update.py`（旧 WeightUpdaterBase，已弃用建议迁移）、`weight_update/utils.py`（权重键排序/签名/_resolve_attr 点路径解析）、`weight_update/weight_sync_schemes.py`（**WeightSyncScheme 框架核心**：sender/receiver 生命周期、指令-ACK 协议、后台接收线程）。
- **入边 10 条**：`collectors/__init__.py`、`_async_batched.py`、`_multi_base.py`、`_runner.py`（worker 入口 import 基类构造子采集器）、`_single.py`、`collectors.py`（向后兼容 barrel）、`distributed/generic.py`（SLURM/submitit）、`distributed/ray.py`、`distributed/rpc.py`、`distributed/sync.py`。

### 数据流
本文件是**协议层**，数据流以键约定形式存在：每个 rollout 步产出 carrier td，含环境键 + `("collector","traj_ids")`（轨迹归属）+ 可选 `("collector","mask")`（按轨迹迭代时有效帧标记）+ `("collector","step_count")`。权重流：训练进程 `TensorDict.from_module(policy)` 抽参 → WeightSyncScheme sender 发送（共享内存/NCCL/Ray 按后端）→ worker 侧 receiver 后台线程收到 → 应用到本地策略副本。trajs_per_batch 模式：收集到超额帧后按 traj_ids 切分、mask 掉跨界帧。

### 模式与坑
- **坑 1：traj_ids = -1 表示无效帧**——preemptive_threshold 抢占或 trajs_per_batch 截断时，被丢弃帧的 traj_ids 置 -1；下游训练不滤掉它们会把脏数据算进损失。
- **坑 2：双轨权重同步并存**——WeightUpdater 是 legacy，WeightSyncScheme 是新框架。混用时 `update_policy_weights_` 的 6 个 overload 决定路由；传参组合不在 overload 表内会得到难懂的 TypeError。新代码一律用 scheme。
- **坑 3：IterableDataset 身份**——BaseCollector 继承 torch 的 IterableDataset，可直接接 DataLoader（num_workers>0 时会整体 pickle 到 worker，CUDA 张量会炸）；通常直接迭代而非包 DataLoader。
- **模式：协议先行**——本文件 1601 行里几乎没有 rollout 循环本体，全是契约（键约定/迭代协议/生命周期钩子）。**torchrl 把"采集"拆成协议（_base）+ 单进程实现（_single）+ 编排（_multi_base）+ worker 程序（_runner）**，四件套各司其职。

---

## torchrl/collectors/_single.py

### 架构角色
**单进程采集器——rollout 核心的最小完整实现**：`Collector` 在进程内直接驱动 env.step 与策略前向，管理三设备布局（policy/env/storing）、回放缓冲写入、轨迹截断与 postproc。图谱 summary 点名它是"TensorDict 中心数据流的最小完整示例"——**读懂 rollout() 就读懂 torchrl 全部采集器的语义**。同时它还是构造分发入口：`Collector(...)` 按参数直接构造本地采集，或分发到进程/Ray/RPC/分布式版本。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L78 | `_CollectorMeta(abc.ABCMeta)` | 元类：规范化 create_env_fn/policy 参数形态、剔除不适用的默认参数、动态生成 `__signature__`（构造分发 direct/process/Ray/RPC/distributed 的入口逻辑挂在这里） |
| L297 | `Collector(BaseCollector)` | 单进程采集器本体 |
| L677 | `__init__` | env/policy 初始化、设备与权重同步设置 |
| L1761 | `iterator` | 迭代入口（含 CUDA stream/event 同步管理） |
| L2014 | `rollout()` | **主循环**（详见数据流） |
| L2255 | `_maybe_set_truncated` | 批尾把被截断轨迹的 `("next","truncated")` 置 True（跨批轨迹的正确性保障） |

文件级函数 `_cuda_sync_if_initialized`：CUDA 已初始化才做流同步，规避多进程 CUDA 上下文问题。

### 外部连接
- **出边 19 条**（采集层最多）：`torchrl/__init__`、`_comm/backends.py`（服务/传输后端解析）、`_utils.py`、`collectors/_base.py`、`_constants.py`（超时/探索默认/平台标志 + _Interruptor）、`collectors/utils.py`、`weight_update.py`、`data/__init__.py`、`data/utils.py`、`envs/__init__.py`、`envs/common.py`、`envs/llm/transforms/__init__.py`（Tokenizer/IncrementalTokenizer/KLReward 等）、`envs/utils.py`（step_mdp）、`modules/__init__.py`、`modules/inference_server/_config.py`（**推理服务配置——策略可卸载到 InferenceServer**）、`modules/utils/utils.py`（TensorDictPrimer 自动补齐）、`weight_update/utils.py`、`weight_update/weight_sync_schemes.py`。
- **入边 9 条**：`collectors/__init__.py`、`_multi_base.py`（多进程版把 Collector 类发给 worker 实例化）、`_runner.py`、`collectors.py`、distributed 四件套（generic/ray/rpc/sync）、`collectors/llm/base.py`（LLMCollector 继承它）。

### 数据流（rollout L2014-2253，五阶段）
docstring 官方五步（L2020-2037）+ 实现细节：
1. **Carrier 准备**：读 `self._carrier`（跨时间步存活的持久 tensordict，`_make_carrier` 一次性分配）；`reset_at_each_iter=True` 时先 `env.reset()`。
2. **策略步**：`_should_use_random_frames()`（init_random_frames 阶段）→ `env.rand_action`；否则 carrier cast 到 policy_device（`non_blocking` 视 `no_cuda_sync` 与设备类型定，L2078-2091）→ `cudagraph_mark_step_begin()`（compiled_policy 时）→ `_wrapped_policy(policy_input)` → 输出 merge 回 carrier（`keys_to_update=_policy_output_keys`）。compiled 策略输出要 `select(...).clone()`（L2104-2107）。
3. **环境步**：carrier cast 到 env_device → `env.step_and_maybe_reset(env_input)` 返回 `(env_output, env_next_output)`，把 `env_output["next"]` 写回 carrier。
4. **持久化**：三岔路——(a) 直连 RB 且非 extend：`replay_buffer.add(carrier)` 逐帧写（平坦 1-D 约定），`_increment_frames` 达量即 return；(b) storing_device 异设备：append cast 后的快照 + `_sync_storage()`；(c) 同设备直接 append。`compact_obs` 开启时排除 `("next",...)` 里的观测键再存（下一帧根键可恢复，L2141-2147）。
5. **推进**：carrier 换成 reset 后的 `env_next_output`，回灌 `collector` 数据，`_update_traj_ids` 给 done 的 env 发新 traj_id。
批尾组装：`_use_buffers` 时 `torch.stack(tensordicts, out=self._final_rollout)`（预分配缓冲，RuntimeError 时 `unlock_` 重试——锁定的张量遇上需要写的场景）；extend_buffer 时 LazyStackedTensorDict.lazy_stack（免中间拷贝）；否则 `maybe_dense_stack` + `refine_names(..., "time")`。`interruptor.collection_stopped()` 中断路径同构但只 stack 到 t+1。

### 模式与坑
- **坑 1：三设备布局是性能调优主旋钮**——policy_device（GPU 推理）/env_device（CPU env）/storing_device（大内存机）可全不同，每步两次 cast。`no_cuda_sync=True` 省同步点但依赖 non_blocking 语义，出错时数据可能是旧的——先排障时关掉它。
- **坑 2：carrier 是持久对象**——跨步复用同一 TensorDict。自定义 transform 若在 carrier 上留了脏键，会在后续步静默传播。`reset_at_each_iter=True` 只 reset 环境不清理额外键。
- **坑 3：compiled_policy 的输出被 select+clone**——torch.compile 的图返回可能引用内部缓冲，不 clone 会被下步覆盖。自己包 compiled 模块时要保留这个防御。
- **坑 4：`_maybe_set_truncated` 的必要性**——轨迹跨批时，批内最后一步不是真终止；不补 truncated 标记，GAE/算回报会把跨界当 done 截断。**任何自写采集循环都容易漏这一步**。
- **模式：构造分发**——`Collector` 的元类动态改签名，使同一个类名能当 factory 用（num_collectors/Ray 后端等参数改变构造目标）。这是 torchrl API 表面简单、背后可扩展的惯用法。

---

## torchrl/collectors/_multi_base.py

### 架构角色
**多进程采集编排器**：`MultiCollector` 以子进程方式启动 worker（target 是 `_runner.py` 的 `_main_async_collector`）、管理队列（数据）与管道（控制）通信、装配多回放缓冲与多策略工厂、分发权重同步 scheme，并提供远程属性访问与统计聚合。`MultiSyncCollector`/`MultiAsyncCollector`（在 _multi_sync.py/_multi_async.py）是它的两个薄子类。tags：multiprocessing/orchestration。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L55 | `_MultiCollectorMeta(abc.ABCMeta)` | 多采集器元类：实例化时规范化多 policy/多 env 构造参数 |
| L64 | `__call__`（元类内） | `sync=True` → MultiSyncCollector，`False` → MultiAsyncCollector（**同步/异步在元类层分流**） |
| L79 | `MultiCollector(BaseCollector)` | 基类本体：docstring 明示新代码用 `Collector(num_collectors=..., sync=...)` 构造 |
| L625-L927 | `_setup_*` 家族 × 15 | worker/env 配对、env kwargs、多 RB、policy 工厂、多策略权重（新旧两代）、版本跟踪、fallback 策略、total_frames、split_trajs、preemptive 阈值——**构造期的一切装配** |
| L1181-L1185 | `frames_per_batch_worker` / `_queue_len` | 各 worker 配额计算；队列长度 |
| L1188 | `_recv_and_check` | 收队列消息并校验（错误传播） |
| L1247 | `_run_processes()` | **进程启动总装**（见下） |
| L1569 | `start()` | 异步自由采集：向所有 pipe 发 `run_free`，数据进 RB，训练侧轮询 `rb.write_count`（docstring 有完整 Pong 例子） |
| L1648 | `pause()` | 上下文管理器：发 pause 并等全部 worker 确认（带 30s 超时健康检查） |
| L1735-L1835 | `_set_worker_attr` / `map_fn` / `get_distant_attr` / `stats` | 远程属性操作与统计聚合 |
| L1882-L1963 | `__del__` / `shutdown` / `_shutdown_main` / `async_shutdown` | 四种关闭路径（析构/同步/主进程/异步） |
| L1966-L2075 | `set_seed` / `reset` / `state_dict` / `load_state_dict` / `increment_version` / `policy_version` | 跨进程的种子/状态/版本管理 |

`_run_processes` 细节（L1247-1566）：num_threads 默认 = 全局线程数 - 总 worker 数；`ctx.Queue` 出数据 + 预建 `ctx.Pipe` 对（每 worker 一对，父端留作控制/轮询）+ `_TrajectoryPool(lock=True)` 跨进程轨迹 ID 池；weight_sync_schemes 先于 worker 启动初始化（sender 侧）；policy 难序列化时用 `policy_factory`（CloudpickleWrapper 包装）——**带 scheme 时 policy 只用于主进程抽权重、不发给 worker**；legacy 通道则 `_policy_weights_dict` 按 device 共享权重就地注入。worker 启动后、等 "instantiated" 前，先连 policy scheme 再连其余 scheme（防死锁注释：worker init 期间会阻塞等数据）。**错误分类学**（L1414-1496）：TypeError "cannot pickle"→不可序列化对象；RuntimeError "Cowardly refusing to serialize non-leaf tensor"→策略/RB/env 工厂带梯度张量（建议 transform_factory+delayed_init、detach）；"_share_fd_ only available on CPU"→spawn+CUDA 张量（给 fork/升版建议+上游 issue 链接）；ValueError "fds_to_keep"→老 Python+老 torch 的 spawn 兼容问题；PicklingError "<lambda>"→ParallelEnv 的 lambda 须 EnvCreator 包装。

### 外部连接
- **出边 15 条**：_base/_constants/_runner/_single/utils/weight_update（采集层内部）、`torchrl/__init__`、`_utils.py`、`data/__init__`、`data/utils`、`envs/__init__`、`envs/llm/transforms/__init__`（PolicyVersion 从这里引入做版本跟踪）、`weight_update/__init__`（六种后端方案）、`weight_update/utils`。
- **入边 5 条**：`collectors/__init__.py`、`_multi_async.py`、`_multi_sync.py`、`collectors.py`、`distributed/generic.py`。

### 数据流
控制面（pipe）：主进程 → worker 发指令（run_free/pause/set_attr/…）；worker → 主进程回状态（"instantiated"、错误 dict 含 exception_type/msg/traceback——主进程**按模块名动态 import 还原异常类型再 raise**，L1538-1560）。数据面（queue）：worker rollout 满配额 → 轨迹 TensorDict 进 ctx.Queue → 主进程 `_recv_and_check` 校验 → 按 cat_results 策略（"stack"/-1/其它）合并各 worker 批。权重面（scheme）：见 _base.py 条目；特别地 worker_idx 参与 queue 式权重分发。轨迹 ID：`_TrajectoryPool` 共享对象保证跨 worker 的 traj_id 全局唯一。

### 模式与坑
- **坑 1：spawn 下的 CUDA 张量是头号事故源**——三处针对性报错信息都在 _run_processes。规矩：**能 fork 就 fork（Unix），必须 spawn 时一切张量留 CPU**。
- **坑 2：同步 vs 异步的选择**——MultiSync 每 worker 固定配额、阻塞齐批（批形状稳定，适合 on-policy 精确控制）；MultiAsync 各 worker 自由生产（吞吐优先，批形状可能不齐）。元类 `sync` 参数决定，选错对 PPO 这类要求固定 frames_per_batch 的算法是灾难。
- **坑 3：policy vs policy_factory 的微妙分工**——用 scheme 时两者可同时给：policy 只用于主进程抽权重、factory 在 worker 建策略。只给 policy 且难序列化 → 启动报 pickle 错；只给 factory 且要权重同步 → 无从抽参。
- **坑 4：worker 崩溃的静默性**——worker 死后 pipe EOF，`_recv_and_check`/poll(timeout) 会转为 RuntimeError；但运行中崩溃可能表现为队列无产出。`watch_process_liveness` 式哨兵思想（见 mailbox 条目）与 pause() 的健康检查是官方给的两种缓解。
- **模式：编排与执行分离**——_multi_base 只做编排，rollout 循环本体在 _runner.py 的 `_main_async_collector`（worker 进程内 import _single.Collector 完成实际采集）。**这种分离使分布式（generic/ray/rpc）能复用同一 worker 程序**，只换传输层。

---

## torchrl/collectors/llm/base.py

### 架构角色
**LLM 专用采集器**：`LLMCollector` 继承单进程 `Collector`，针对对话式 rollout 重写迭代协议——按**对话轮次/轨迹**而非固定帧数产出批次，并管理策略版本与 vLLM 权重更新器对接。RLHF 训练环（LLM 策略 × ChatEnv 数据环境 × vLLM 推理）的采集侧粘合剂。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L26 | `LLMCollector(Collector)` | 主类：全量/按轨迹/异步三种产出模式 |
| L146 | `__init__` | 构造：对话轮次配额、PolicyVersion 跟踪、weight updater 接线 |
| L254 | `set_postproc` | rollout 后处理注入（如奖励解析/格式校验） |
| L259/L269/L275 | `increment_version` / `policy_version` / `get_policy_version` | **策略版本三件套**：权重每次更新版本+1，rollout 数据带版本戳——off-policy 程度可观测 |
| L287/L291 | `total_dialog_turns` / `dialog_turns_per_batch` | "帧数"在 LLM 场景重新定义为**对话轮次** |
| L296 | `rollout()` | 分发到三个私有实现 |
| L305 | `_rollout_all` | 全量模式：攒满整批一次返回（简化版 rollout） |
| L335 | `_rollout_yield_trajs` | 按轨迹产出：完整轨迹逐条 yield |
| L397 | `_rollout_yield_trajs_async` | 异步轨迹产出 |
| L472/L483/L492 | `get_policy_model` / `is_initialized` / `set_weight_updater` | 取策略模型（vLLM 同步用）；初始化状态；**权重更新器注入**（WeightUpdaterBase 接口，vLLM 实现在 llm 子包） |

### 外部连接
- **出边 8 条**：`_utils.py`、`collectors/_single.py`（父类）、`collectors/llm/utils.py`（**_QueueAsRB：把队列包装成回放缓冲接口**，逐条入队、满则丢最旧——LLM rollout 不落盘的轻量通道）、`collectors/weight_update.py`、`data/replay_buffers/replay_buffers.py`（真 RB 路径）、`envs/__init__.py`、`envs/common.py`、`envs/llm/transforms/policy_version.py`（**PolicyVersion Transform：UUID/整数版本维护，配合权重更新自动递增**）。
- **入边 1 条**：`collectors/llm/__init__.py`（与 RayLLMCollector、vLLM 权重更新器一起导出）。

### 数据流
一条对话 = 一条轨迹：ChatEnv.reset 下发 prompt → LLM 策略生成 response（action 键）→ env.step 拼进 History → 直到 done（终答/轮次上限）。rollout 产出 td 带全套 token/掩码/log_prob 键（LLM 策略模块写入）+ `("collector","policy_version")` 戳。权重更新流：训练侧更新策略 → `set_weight_updater` 注入的更新器把新权重推给 vLLM 推理引擎 → PolicyVersion Transform 自动递增版本 → 下一轮 rollout 带新版本戳。产出通道二选一：_QueueAsRB（训练进程消费队列）或真 ReplayBuffer（跨进程共享）。

### 模式与坑
- **坑 1：frames 语义换成 dialog turns**——frames_per_batch 在这里按对话轮计。从通用 RL 迁移配置时按 token 预算/轮次重算，直接抄数字会爆内存（一条轨迹的 token 量远大于一帧）。
- **坑 2：版本戳是 off-policy 诊断的关键**——rollout 数据的 policy_version 与当前版本差值过大 → 数据过时（KL 漂移）。LLM RLHF 的经典失败（数据太旧导致策略坍缩）靠这个键早发现。
- **坑 3：_QueueAsRB 会丢旧数据**——队列满丢最旧是刻意设计（在线消费），误当持久 RB 用会静默丢轨迹。
- **模式：继承而非组合**——LLMCollector 直接继承 Collector 而非包一层，因为要重写 rollout 协议本身（轮次边界 ≠ 帧边界）；但复用了父类全部设备/权重/中断机制——**协议差异集中在三个 _rollout_* 方法**，是"继承点选在最小差异面"的示范。

---

## torchrl/_comm/mailbox.py

### 架构角色
**进程间通信的邮箱原语**（分布式与权重同步层）：基于 `multiprocessing.connection` 的生产者-消费者模式——`Mailbox`（服务端）多路复用轮询所有客户端连接取请求，`MailboxClient`（客户端）提交载荷、按 req_id 取回结果。它是 `_comm` 栈的传输地基：`command.py`（命令通道）与 `distributed.py`（torch.distributed 传输）都建在其上。284 行小而精。

### 内部结构
| 行号 | 类/方法 | 职责 |
|---|---|---|
| L18 | `MailboxTransportError(RuntimeError)` | 传输层基异常：整个 _comm 栈统一的传输错误信号 |
| L22 | `MailboxPeerClosedError(MailboxTransportError)` | 对端已关闭专用异常：区分"对端退出"与一般故障，触发优雅停机 |
| L26 | `watch_process_liveness()` | 后台看护循环：监视目标进程哨兵，进程一退出立即清 alive_event——**让通信双方尽快感知对端死亡而非永远阻塞** |
| L43 | `MailboxFuture` | Future 句柄：done/result 委托 client._get_result，非阻塞/阻塞两式取结果或异常 |
| L70 | `MailboxClient` | submit 写连接发载荷并登记回调表；`_get_result(req_id)` 按 ID 轮询/阻塞取回；实现 `__getstate__/__setstate__`（连接对象不可 pickle，自管重连语义） |
| L106 | `submit()` | 提交载荷 → 返回 MailboxFuture |
| L185 | `Mailbox` | 服务端：`client()`（L217）接受连接；`wait_for_work(timeout)`（L231）用 `multiprocessing.connection.wait` **多路复用**轮询所有连接取请求；`drain`（L242）排空；`resolve`/`reject`（L273/L282）回写结果或异常 |

### 外部连接
- **出边 0 条（不 import 任何 torchrl 模块）**——纯标准库 + multiprocessing，**零内部依赖**是它作为最底层原语的资格证明。
- **入边 3 条**：`_comm/__init__.py`（barrel）、`_comm/command.py`（CommandRequest/CommandClient/CommandChannel：动词+载荷的命令语义建立在 mailbox 之上）、`_comm/distributed.py`（跨进程 TensorDict 请求-应答：TorchDistributedTransport）。

### 数据流
请求向：client.submit(payload) → 写入 mp.Connection → server.wait_for_work 用 `connection.wait([所有连接])` 就绪即收 → 服务端处理得到 callback 句柄 `(client_id, req_id)`。应答向：server.resolve(callback, result)（或 reject 传异常）→ 写回对应连接 → client._get_result 按 req_id 从回调表匹配 → Future.result() 交付。异常以值的形式跨进程传递（reject 的 BaseException 会被序列化传回、在 client 侧重抛）。看护向：watch_process_liveness 独立线程轮询进程哨兵 → 死亡 → alive_event.clear() → 通信 API 检查 event 后快速抛 MailboxPeerClosedError。

### 模式与坑
- **坑 1：对端死亡的经典挂死**——没有 liveness 看护时，server 阻塞在 wait、client 阻塞在 result，互相等。本文件的答案是哨兵线程 + PeerClosed 异常分层。**自写多进程代码必抄这个模式**。
- **坑 2：连接不可 pickle**——MailboxClient/Mailbox 的 `__getstate__/__setstate__` 自定义是因为 mp.Connection 不能随对象序列化传输；把这些对象当参数传给子进程（而非在子进程内创建）会炸。
- **坑 3：Future 的 result 阻塞式默认**——`__call__`（L116）是 submit+阻塞等待的糖；高吞吐场景应 submit 后攒一批 Future 再统一收割。
- **模式：req_id 回调表 = 轻量 actor 邮箱**——这套 submit/future/resolve 语义就是 Erlang 风格邮箱在 Python mp 上的最小复刻；torchrl 的推理服务（InferenceServer）与权重同步指令-ACK 协议都直接复用。

---

## torchrl/checkpoint/_checkpoint.py

### 架构角色
**检查点系统核心**（训练层）：组件化 `Checkpoint` 容器（注册/manifest/版本迁移）+ 多格式 `CheckpointAdapter` 抽象（pickle 整存 / state_dict 张量分离 / 纯 JSON）+ 全局 RNG 状态捕获 + 按策略轮转保留的 `CheckpointRotation`。设计关键词是**组件化**——policy/optimizer/RB/env/optimizer scheduler 各为一个命名组件，独立选择保存或恢复。

### 内部结构
| 行号 | 类/函数 | 职责 |
|---|---|---|
| L46 | `_to_json_value()` | 路径/张量等对象 → JSON 兼容原生值 |
| L65 | `CheckpointError(RuntimeError)` | 子系统专属异常，带上下文 |
| L87 | `CheckpointOptions` | 保存/加载选项 dataclass（压缩/格式/map_location），支持与默认值合并 |
| L135 | `CheckpointLoadResult` | 加载结果容器：各组件加载出的对象 + 警告信息 |
| L166 | `CheckpointAdapter(abc.ABC)` | 适配器抽象基类：save/load 统一接口与**加载路径分离协议** |
| L211 | `DumpLoadCheckpointAdapter` | 最简适配器：torch.save/torch.load 整对象 dump |
| L253/L369 | `_encode_state_dict_value` / `_decode_state_dict_value` | **递归编解码 state_dict**：张量抽到张量表（TensorDict 承载）落盘、其余结构转 JSON；解码时按 map_location 重组 |
| L353 | `_mapped_device()` | 按 map_location 规则解析保存设备→目标设备 |
| L432 | `StateDictCheckpointAdapter` | **王牌适配器**：payload_format 四选一（directory/archive/consolidated/torch）；张量抽离成 TensorDict 存、schema 存 `state.json`；load **自动探测四种格式**；torch 格式默认 `weights_only=True`（反 pickle 漏洞） |
| L550 | `JSONCheckpointAdapter` | 纯 JSON：仅可 JSON 化标量/配置，用于元信息 |
| L605 | `GlobalRNGState` | 捕获/恢复 Python random + numpy + torch CPU + **各 CUDA 设备**的全局随机状态 |
| L695 | `_Component` | 内部组件记录（值/适配器/选项） |
| L701 | `Checkpoint` | 容器本体：register/register_adapter/save/load；**原子写**——stage 目录（`.name.stage-{uuid}`）写全 → publish（rename）到目标；directory/archive(zip) 双格式；`_format_migrations` 类字典挂版本迁移函数；`_compare_versions`（L904）比对 torchrl/tensordict/torch 三方版本并标注 matches |
| L1341/L1348 | `_RotatedCheckpoint` / `CheckpointRotation` | 轮转管理：按 keep 数 prune、按 latest/best 指标选取并加载 |

save 主流程（L809-902）：选组件（sorted 稳定序）→ 每组件解析适配器 → 写 stage 子目录 → 登记组件记录（adapter_id/版本/相对路径/**文件清单**）→ manifest JSON → directory 则 rename 发布 / archive 则打 zip（stored/deflate 压缩）再发布 → finally 清理残留 stage。

### 外部连接
- **出边 2 条**：`torchrl/__init__.py`（取版本号做 manifest 比对）、`_utils.py`。
- **入边 1 条**：`checkpoint/__init__.py`（重导出 Checkpoint 及适配器体系）。
- 解读：**入边极窄 = 通用工具**——它不依赖任何 RL 概念（env/policy 一概不知），任何"多组件有状态对象"都能用；Trainer 只是它的最大用户。

### 数据流
保存：`Checkpoint(policy=model, optimizer=opt).save(path)` → 各组件经适配器序列化到 `components/<idx>-<name>/` → manifest.json（组件清单+文件列表+版本+metadata）落盘。恢复：`Checkpoint(policy=model2, optimizer=opt2).load(path)` → 读 manifest → 版本比对（不匹配给警告/按迁移函数升级）→ 按记录逐组件适配器 load → state_dict 注入活对象 → 返回 CheckpointLoadResult（loaded 集合 + 警告）。StateDict 路径的张量分离：`_encode_state_dict_value` 递归遍历，tensor 进 `TensorDict(tensors)`（tensordict.save 落盘，mmap 可读），结构骨架进 JSON schema；load 时反向重组，map_location 逐张量迁移设备。

### 模式与坑
- **坑 1：strict 默认 "error"**——请求加载的组件在 checkpoint 里缺失/不兼容直接抛错。部分恢复（只要 policy 不要 optimizer）要么显式传 components，要么 strict="warn"。
- **坑 2：torch 格式才吃 tensor_load_kwargs**——mmap/weights_only 只有 state.pt 路径支持；directory/archive 载荷传了会 TypeError（L522-529 显式校验）。
- **坑 3：weights_only=True 是默认但非绝对安全**——torch.load 的 weights_only 仍允许部分算子；不可信 checkpoint 依旧要沙箱里开。
- **坑 4：GlobalRNGState 要覆盖在用的一切随机源**——自定义 env 内持有私有 RNG（如 numpy Generator 实例属性）不在捕获范围，恢复后 env 内随机流与训练前不同步（复现实验差一票的元凶）。
- **模式：stage-then-publish 原子写**——任何崩溃最多残留 stage 目录（finally 清理），目标路径永远只有完整 checkpoint。**自写训练循环保存逻辑应照抄此模式**，"写到一半崩了把好 checkpoint 覆盖了"是真实事故。
- **模式：manifest 记文件清单**——files 列表使损坏检测（少文件）与增量迁移（只动某组件）成为可能。

---

## torchrl/testing/mocking_classes.py

### 架构角色
**测试基础设施核心**：47 个 mock 环境与配套策略/变换，系统性覆盖 EnvBase 语义的每个测试切面——计数环境家族（嵌套 key/多智能体/异构/自动 reset/动态 spec/字符串观测/故障注入…）。它不只是测试文件：**它是 EnvBase 契约的可执行规格书**——图谱把它放在"测试与工程支撑层"，但被 `_single.py` 之外的几乎每个采集/损失测试引用。理解这 47 个类的分类学 = 理解 torchrl 认为环境语义有哪些正交维度。

### 内部结构（家族分类学）
| 家族 | 行号 | 代表 | 测试切面 |
|---|---|---|---|
| 工厂设施 | L39/L49/L64 | `spec_dict` / `default_spec_kwargs` / `make_spec()` | spec 字符串（bounded/one_hot/categorical/…）→ spec 实例 |
| 基类 | L70 | `_MockEnv(EnvBase)` | **`__new__` 中按 spec 统一构造观测/动作/奖励 Composite spec 并统一 dtype/device**（含 reward/done 自动包 Composite、terminated/truncated 双键） |
| 串行/批 | L154/L266/L417 | `MockSerialEnv` / `MockBatchedLockedEnv` / `MockBatchedUnLockedEnv` | 串行 vs batch-locked（固定 batch_size）vs 非 locked；done/terminated/truncated 语义区分 |
| 无状态 | L432 | `StateLessCountingEnv` | 观测恒 1、reward 记步数——值函数/损失测试（无环境噪声） |
| Vec/Conv 族 | L517-L995 | `DiscreteActionVecMockEnv` / `ContinuousActionVecMockEnv` / `*ConvMockEnv` / `*Numpy` 版 / 配套 Policy | 离散/连续 × 向量/图像 × torch/numpy 观测的组合矩阵 |
| Model-based | L997 | `DummyModelBasedEnvBase` | ModelBasedEnvBase 世界模型替身 |
| 变换交互 | L1063/L1104 | `AddPixelsTransform` / `CountingVecNormV2` | Transform 改写 spec（加像素通道）；与 VecNormV2 的状态交互 |
| 计数核心族 | L1168-L1299 | `CountingEnv`（**观测递增计数、动作 +1、reward 联动——rollout 一致性测试的基础环境**）/ `CountingEnvWithString` | 非张量（字符串）观测在采集/回放中的传递 |
| MARL | L1299/L1787 | `MultiAgentCountingEnv`（分组 group map）/ `HeterogeneousCountingEnv`（**智能体规格互异**） | 分组与异构 spec |
| 嵌套/多键 | L1492/L1992 | `NestedCountingEnv` / `MultiKeyCountingEnv`（多 done/obs 键 + nested_1/nested_2） | 嵌套 TensorDict 的 rollout/存储 |
| 批环境 | L1674 | `CountingBatchedEnv` | 自带 batch 维（非 batch-locked）语义 |
| 边界语义 | L2191/L2230/L2246 | `EnvWithMetadata` / `AutoResettingCountingEnv` / `AutoResetHeteroCountingEnv` | EnvMetaData；到限自动 reset |
| 异形 spec | L2307/L2362 | `EnvWithDynamicSpec`（**reset 时改 spec**）/ `EnvWithScalarAction` | 动态/lazy spec；标量动作 |
| 故障注入 | L2486/L2742 | `EnvThatErrorsAfter10Iters` / `EnvThatErrorsBecauseOfStack` | 迭代 10 次后抛错（容错测试）；stack 维度不一致异常路径 |
| LLM 族 | L2558-L2649 | `History`（role/content）/ `HistoryTransform` / `DummyStrDataLoader` / `DummyTensorDataLoader` | 对话历史数据类；历史写入 td；假数据加载器（padding/stack 逻辑） |
| 杂项 | L2433/L2449/L2515/L2522/L2687/L2810 | `EnvThatDoesNothing` / `Str2StrEnv` / `TC`（tensorclass）/ `EnvWithTensorClass` / `MockNestedResetEnv` / `FastImageEnv` | 空操作；纯字符串通路；tensorclass 载体/观测；嵌套 reset；随机图像性能测试 |

### 外部连接
- **出边 7 条**：`_utils.py`、`data/__init__.py`、`data/utils.py`、`envs/__init__.py`、`envs/common.py`、`envs/model_based/common.py`（ModelBasedEnvBase）、`envs/utils.py`（step_mdp/check_env_specs）。
- **入边 1 条**：`testing/__init__.py`（与断言工具、gym 兼容常量、Ray 测试 worker 一起导出）。
- 解读：**出边全是 envs/data 的公共 API**——mock 环境只用公开接口建环境，这本身就是 EnvBase 抽象完备性的持续验证。

### 数据流
以 CountingEnv 为例：观测键 = 计数器张量，`_step` 执行 `obs += action`（动作约定 +1），reward 与计数联动，到 max_steps 置 done。策略侧配套 `CountingEnvCountPolicy`：读观测输出使计数 +1 的动作——**env 与 policy 是配对设计的**，rollout 结果可精确断言（第 N 步观测必为 N）。_MockEnv 基类的 `__new__` 数据流值得注意：spec 修整发生在**实例化之前**（类级 _output_spec/_input_spec 就地改写），保证任何子类拿到手的 spec 都已 Composite 化/dtype 统一。

### 模式与坑
- **坑 1：`_MockEnv.__new__` 改的是类级 spec**——子类继承时类属性被就地修改，同一解释器里反复构造同族环境看到的是已修整的 spec（幂等但值得知道）。
- **坑 2：mock 环境的键名是测试契约**——CountingEnv 族用固定观测键；换键名的环境（如 MultiKey）是为专门测试，别在通用测试里误用。
- **模式：正交维度矩阵设计**——离散×连续 × vec×conv × torch×numpy × serial×batched×locked × 嵌套×多键×异构……47 个类不是堆出来的，是维度笛卡尔积上有意义的采样。**为库写测试替身时先列语义维度表，再按格点造类**，本文件是最好的范本。
- **模式：配对策略**——几乎每个环境族都有同名 Policy（DiscreteActionVecPolicy L749、HeterogeneousCountingEnvPolicy L1772、MultiKeyCountingEnvPolicy L1956…），使端到端 rollout 可无网络权重运行且结果确定。
- **模式：故障注入环境的存在**说明 torchrl 把"采集器在 env 崩溃时的行为"当作一等测试对象——多进程采集器的错误传播链（见 _multi_base）正是靠 EnvThatErrorsAfter10Iters 验证的。

---

## 尾注：15 文件的分层坐标（图谱视角）

```
模块层  models.py ──► common.py(SafeModule) ──► probabilistic.py ──► actors.py
                    continuous.py(分布族)▲                        │
                                                              被 5 个 losses 消费
环境层  vecnorm.py(Transform)        chat.py(ChatEnv) ◄── 4 个 LLM 数据集环境
数据层  prompt.py(PromptData) ──► llm/utils.RolloutFromModel
采集层  _base.py(协议) ──► _single.py(rollout 本体) ──► _multi_base.py(编排) ──► _runner.py(worker)
                            ▲ llm/base.py(LLMCollector)
分布式  mailbox.py(零依赖 IPC 原语) ◄── command.py/distributed.py ◄── weight_update/*
训练层  _checkpoint.py(组件化检查点，入边仅 1)
测试层  mocking_classes.py(47 mock = EnvBase 可执行规格书)
```

三条贯穿性设计律：
1. **Safe\* = tensordict.nn 原类 + TensorSpec 接受能力**；模块层的所有"安全"都指 spec 约束。
2. **键约定即协议**：action/action_value/chosen_action_value/log_prob/("collector",traj_ids|mask|policy_version)——损失、采集器、回放缓冲之间没有接口类型检查，全靠这些键名对齐。
3. **协议/实现/编排分离**：_base(协议) × _single(实现) × _multi_base(编排) × _runner(worker 程序) 的四件套，加上分布式层只换传输（generic/ray/rpc），是 torchrl 采集体系可扩展性的全部秘密。


---

# torchrl 核心文件精讲（3/3）：损失算法、训练器与周边系统

> 本篇是 torchrl 核心文件精讲三部曲的收官篇：**objectives/（损失算法层）+ trainers/（训练编排层）+ record/render/weight_update/envs 周边系统**，共 17 个文件。行号锚点基于当前工作区源码实测；图谱信息来自 `.understand-anything/knowledge-graph.json`。
>
> 三部曲全景：①数据基座（TensorDict/采集器/回放缓冲）→ ②模块与分布（modules）→ **③损失+训练+周边（本篇）**。一句话架构：`collector 采数据 → replay buffer 存取 → LossModule(loss) 算梯度 → Trainer 编排 → weight_update 同步权重回 collector，record/render 全程观测`。

## 目录

1. [torchrl/objectives/common.py](#torchrlobjectivescommonpy) — LossModule 基类
2. [torchrl/objectives/utils.py](#torchrlobjectivesutilspy) — objectives 工具箱
3. [torchrl/objectives/ppo.py](#torchrlobjectivesppopy) — PPO 损失家族
4. [torchrl/objectives/sac.py](#torchrlobjectivessacpy) — SAC 连续/离散
5. [torchrl/objectives/dreamer_v3.py](#torchrlobjectivesdreamer_v3py) — DreamerV3 三件套
6. [torchrl/objectives/value/advantages.py](#torchrlobjectivesvalueadvantagespy) — 价值估计器族
7. [torchrl/objectives/llm/grpo.py](#torchrlobjectivesllmgrpopy) — GRPO/DAPO + MCAdvantage
8. [torchrl/trainers/trainers.py](#torchrltrainerstrainerspy) — Trainer 主类 + 19 hooks
9. [torchrl/trainers/helpers/trainers.py](#torchrltrainershelperstrainerspy) — make_trainer 工厂
10. [torchrl/trainers/algorithms/configs/__init__.py](#torchrltrainersalgorithmsconfigs__init__py) — Hydra 配置注册表
11. [torchrl/record/loggers/common.py](#torchrlrecordloggerscommonpy) — Logger 基类
12. [torchrl/record/recorder.py](#torchrlrecordrecorderpy) — 视频/TensorDict 记录器
13. [torchrl/render/config.py](#torchrlrenderconfigpy) — 渲染配置
14. [torchrl/weight_update/weight_sync_schemes.py](#torchrlweight_updateweight_sync_schemespy) — 权重同步框架
15. [torchrl/weight_update/llm/vllm_nccl.py](#torchrlweight_updatellmvllm_ncclpy) — vLLM NCCL 同步
16. [torchrl/envs/libs/__init__.py](#torchrlenvslibs__init__py) — 20+ 环境库入口（简讲）
17. [torchrl/envs/llm/__init__.py](#torchrlenvsllm__init__py) — LLM 环境入口（简讲）

---

## torchrl/objectives/common.py

**1018 行 | 复杂度 complex | 图谱角色：损失函数层的地基**。图谱摘要：LossModule 基类——所有 torchrl 损失的骨架，实现 TensorDict 驱动的 in/out 键管理、损失掩码、目标网络参数注册与 functional 化训练接口。

### 架构角色

torchrl 里每一个损失（PPO/SAC/DQN/GRPO/Dreamer…共 30+ 个）都继承 `LossModule`。它不定义任何具体算法，只解决三件事：

1. **键约定**：损失读什么键（`in_keys`）、写什么键（`out_keys`），用 `_AcceptedKeys` dataclass + `set_keys()` 统一配置（L379）；
2. **functional 化**：把用户传入的有状态网络拆成"无状态模块 + `TensorDictParams` 参数容器"，这是 meta-RL、vmap 批处理、目标网络的生命线（L426 `convert_to_functional`）；
3. **损失归约协议**：所有 `loss_*` 键经过 `_reduce_loss`（L340），自动叠加 padding 掩码与优先级权重。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_updater_check_forward_prehook` | L44 | target 参数前置检查钩子 |
| `_LossMeta` 元类 | L72 | 在类创建时校验子类结构 |
| `LossModule` | L87 | 基类主体（docstring 内含 loss_mask 三态说明 L120-129） |
| `tensor_keys` property | L181 | 暴露 `_AcceptedKeys` 实例 |
| `__setattr__` | L188 | 对 `_schedulable_buffers` 内的 buffer 做**就地标量赋值**（`loss.entropy_coeff = 0.003` 不换 device/dtype） |
| `get_stateful_net` / `from_stateful_net` | L227 / L254 | functional ↔ stateful 网络互转 |
| `loss_mask_key` | L288 | 掩码三态：`"auto"`（自动发现 torchrl 自写的 `("collector","mask")` 和 `"shifted_valid"`）/ 显式 NestedKey / `None` |
| `_reduce_loss` | L340 | 归约核心：**用 `torch.where` 选择而非乘 0**（注释 L364-367：nan×0=nan，前向反向都污染） |
| `set_keys` | L379 | 运行时改键名 |
| `convert_to_functional` | L426 | **最重要的方法**（见下） |
| `register_coeff_buffer` | L764 | 注册可调度系数 buffer（clip_epsilon/entropy_coeff 等） |
| `make_value_estimator` | L840 | 构造默认价值估计器 |
| `add_random_module` | L1012 | 便捷工厂：附加随机动作模块 |

### 外部连接（图谱边）

- **出边（imports）**：`torchrl/_utils.py`、`torchrl/envs/utils.py`、`modules/tensordict_module/rnn.py`、`objectives/utils.py`、`objectives/value/__init__.py`。
- **入边（被 import）**：图谱显示 **41 个文件 import 它**——objectives 下全部损失（ppo/sac/dqn/ddpg/td3/iql/cql/dreamer/redq/gail/diffusion_bc/llm/grpo/llm/sft/llm/distillation…）、multiagent/qmixer、trainers 全部算法装配文件（helpers/trainers.py、algorithms/{sac,dqn,ddpg,td3,cql,iql,on_policy,offline_to_online}.py）、`trainers/_execution.py`、`_ray_execution.py`。**它是图谱中入度最高的节点之一，堪称损失层的"万有引力中心"**。
- 所属层：`layer:objectives`（损失函数层，向上被 Trainer 消费）。

### 数据流

`convert_to_functional(module, "actor_network", expand_dim=N, create_target_params=True)` 执行后，损失对象上出现三个属性：

- `self.actor_network`：无状态版模块（forward 需要外部喂参数）
- `self.actor_network_params`：`TensorDictParams`（可训练，optimizer 直接吃它）
- `self.target_actor_network_params`：detach 副本（`create_target_params=True` 时）或 detach 视图（默认 False，改源即改目标——SAC 里利用这一点做"无目标"模式）

`expand_dim` 分支（L520-549）：SAC 的双 Q 集成用 `expand_dim=num_qvalue_nets`。**坑**：不在 `compare_against` 里的参数会被**重新均匀采样**（`p_out.uniform_(min, max)`，L543-548）——这是为 ensemble 多样性故意设计的，但共享 backbone 时必须传 `compare_against=policy_params`（PPO 的 `separate_losses` 分支 L527-536 正是为此），否则会把共享参数炸成随机数。

forward 协议（L409）：输入一个 rollout batch 的 TensorDict，输出 `TensorDict({"loss_objective": ..., "loss_critic": ..., ...})`——所有 `loss_` 前缀键参与求和反传，其余键（entropy、ESS、clip_fraction…）只做日志。

### 模式与坑

1. **掩码语义二分**（L351-354 注释）：调用方显式传 `mask=` → 掩码位置被**压缩丢掉**（legacy reduction="none" 契约）；从输入 tensordict 里发现的掩码 → **保持 loss 形状**，仅置零，保证 per-position 输出与输入 batch 对齐。
2. **`_clear_weakrefs`**：functional 参数容器在 forward 结束后清理 weakref，防止内存泄漏——每个损失 forward 尾部都有一串这个调用（PPO L998-1005 可见）。
3. **vmap 兼容**：`_make_vmap`（L994）+ `vmap_randomness`（L939）让 SAC 这类需要"一个 batch 过 N 个 Q 网络"的损失可以真 vmap 或退化为 for 循环（`deactivate_vmap`）。
4. **TARGET_NET_WARNING**（L172-178）：发现 target 参数却没注册 updater 时只警告不报错（可用 `RL_WARNINGS=0` 关闭）——因为有的算法故意手动更新目标网络。
5. 类注解检查（L474-488）：`convert_to_functional` 会走 MRO 收集父类注解，子类忘写 `actor_network: TensorDictModule` 注解只警告不崩溃，但 state_dict 序列化会漏。

---

## torchrl/objectives/utils.py

**1054 行 | 复杂度 complex | 图谱角色：objectives 包的公共工具箱**。图谱摘要：价值估计器注册/分发机制、目标网络更新器（软/硬）、距离损失、next_state_value、vmap 伪映射与裁剪辅助，被所有损失模块共享。

### 架构角色

如果说 `common.py` 是损失的"骨架"，`utils.py` 就是"关节"：损失用什么价值估计器（GAE 还是 TD0）、目标网络怎么更新（软还是硬）、critic 回归用什么距离——全部从这里分发。它实现了 torchrl 独特的**价值估计器注册表机制**：第三方可以 `register_value_estimator` 注册自定义估计器，所有 30+ 个损失立刻可用。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `ValueEstimators` 枚举 | L48 | TD0/TD1/TDLambda/GAE/MultiAgentGAE/VTrace 的调度键 |
| `_ValueEstimatorRegistryEntry` | L106 | 注册表条目（类 + 默认 kwargs） |
| `register_value_estimator` | L119 | **扩展入口**：装饰器把估计器类挂进全局注册表（可按别名） |
| `dispatch_value_estimator` | L227 | 统一分发入口：按 value_type 构造估计器并挂到损失上 |
| `default_value_kwargs` | L283 | 各内置估计器的默认超参（GAE 默认 gamma/lmbda…） |
| `distance_loss` | L330 | 通用距离损失：l1/l2/smooth_l1 |
| `TargetNetUpdater` | L367 | 目标网络更新器基类（生命周期见下） |
| `SoftUpdate` | L532 | Polyak 软更新：`p_target.lerp_(p_source, 1-eps)`（L585-588） |
| `HardUpdate` | L591 | 硬更新：计数器到 interval 直接 copy（L615-624） |
| `hold_out_net` / `hold_out_params` | L627 / L654 | 上下文管理器：临时 eval+no_grad / 冻结参数 |
| `next_state_value` | L671 | 用目标网络算下一状态价值并处理 done/terminated 掩码 |
| `_pseudo_vmap` | L786/839 | 没有 vmap 时的 for 循环降级 |
| `_clip_value_loss` | L933 | PPO value clipping 辅助 |
| `group_optimizers` | L997 | 多优化器合并成单优化器（多损失联合训练） |

### 外部连接

- **入边 38 条**：所有 objectives 损失、advantages.py、`trainers/_execution.py`、`_ray_execution.py`、trainers 装配层全部 import。与 common.py 并列为 objectives 层双核。
- 出边只有 `torchrl/_utils.py` 和 `torchrl/envs/utils.py`——工具箱自身几乎零内部依赖，这是它能被各方安全 import 的原因。

### 数据流

**TargetNetUpdater 生命周期**（L367-529）值得精读，这是理解 torchrl 目标网络的钥匙：

1. **构造**（L375-417）：扫描损失模块的所有 `named_children()`，找 `target_*_params` 命名的子模块，自动配对 `target_xxx_params ↔ xxx_params`；
2. **init_()**（L447-494）：逐参数检查 `data_ptr()` 是否与源相同——**若所有目标参数都与源共享内存则直接 RuntimeError**（L467-474，提示"delay_value 设 True 了吗？"）。这是新手最常踩的坑的自动检测器：SAC/TD3 若忘了 `delay_qvalue=True`，目标网络根本不是独立副本，bootstrapping 目标会跟着训练漂移；
3. **step()**（L496-506）：每次优化步后调用，SoftUpdate 每步 lerp，HardUpdate 按 counter 到点整段复制；
4. **state_dict**（L511-522）：只存 `initialized` 和 `counter`——参数本体在损失模块的 state_dict 里，这里只存"进度"。

### 模式与坑

1. **注册表懒初始化**（L162 `_ensure_builtin_value_estimators_registered`）：内置估计器也是走同一注册表，`for_loss` 钩子（advantages.py L140）让"损失怎么接估计器"的接线知识只写一次。
2. **`hold_out_net`** 进入时保存 training 状态和参数 requires_grad，退出恢复——Dreamer 损失里大量使用（想象力 rollout 时冻结世界模型）。
3. `SoftUpdate` 的 tau/eps 二选一校验（L575-581）：eps 必须在 (0,1)，传错立即报错而非静默 NaN。
4. `distance_loss` 的 reduction 默认 "mean"，但 PPO 里调用时传的是 `loss_critic_type` 字符串——两套 reduction 语义（损失内元素距离 vs batch 归约）不要混淆。

---

## torchrl/objectives/ppo.py

**1819 行 | 复杂度 complex | 图谱角色：on-policy 策略梯度的旗舰实现**。图谱摘要：PPOLoss 基类（log-ratio 策略目标、critic 回归、熵正则）+ ClipPPOLoss（比率裁剪）+ KLPENPPOLoss（自适应 KL 惩罚）。

### 架构角色

PPO 是 torchrl 中被引用最多的 on-policy 损失（multiagent/mappo.py 继承它，LLM 的 GRPO 大量复刻其代码结构——对比 grpo.py 的 `_log_weight`/`forward` 可见明显同构）。它展示了一个标准 LossModule 的完整形态：`__init__` 里 convert_to_functional 两个网络 → forward 里"优势 → 比率 → 目标 → critic → 熵"五步流水。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_check_advantage_broadcast` | L48 | **防御性检查**：[B] 优势 × [B,1] log-weight 会静默广播成 [B,B] 外积，直接 ValueError（L64-72） |
| `_broadcast_advantage_to_log_weight` | L75 | 反向辅助：per-token 目标（DAPO/VLA 场景）把决策级优势广播到 token 维 |
| `PPOLoss` | L109 | 基类（无正则的 log-ratio 目标） |
| — `__init__` | L463 | 参数装配；entropy_coeff 支持**标量或 per-head Mapping**（L566-575） |
| — `_get_cur_log_prob` | L704 | 用当前参数重算 log-prob；**要求 action 不带梯度**（L732-735 报错） |
| — `_log_weight` | L753 | 核心：`log_weight = (log_prob - prev_log_prob).unsqueeze(-1)`（L788），同时产出 kl_approx 日志键 |
| — `_critic_loss_inputs` | L799 | 子类钩子（MAPPOLoss 注入 ValueNorm 归一化） |
| — `loss_critic` | L816 | critic 回归 + 可选 value clip + explained_variance 日志（L888-896） |
| — `_standardize_advantage` | L916 | 掩码感知的优势标准化（支持 shifted_valid 与 exclude_dims） |
| — `forward` | L943 | 基类前向（无 clip 版目标 L970） |
| — `SUPPORTED_VALUE_ESTIMATORS` | L1008 | TD0/TD1/TDLambda/GAE/MAGAE/VTrace 六种 |
| `ClipPPOLoss` | L1082 | 最常用变体；`_schedulable_buffers = {clip_epsilon, ...}`（L1219） |
| — `__init__` / `_clip_bounds` | L1230 / L1332 | 非对称 clip 用 `log1p` 空间：`(−eps_low).log1p(), eps_high.log1p()` |
| — `forward` | L1362 | clip 版目标 + ESS/clip_fraction/max_ratio/mean_ratio 日志 |
| `KLPENPPOLoss` | L1458 | KL 惩罚变体 |
| — `forward` | L1700 | 解析 KL（无公式时 MC 估计 L1747-1768）+ beta 自适应（L1771-1774） |
| — `reset` | L1818 | 恢复 beta 初值 |

### 外部连接

- 出边：`objectives/common.py`、`objectives/utils.py`、`modules/distributions/utils.py`、`_utils.py`。
- 入边：`objectives/__init__.py`（导出）、`multiagent/mappo.py`（继承 PPOLoss 实现 MAPPO）。
- 消费上游：`GAE`（advantages.py）写入的 `advantage`/`value_target` 键；输出被 `trainers.LogScalar` hook 抽取打日志。

### 数据流

**读**（in_keys，L605-617 自动收集）：actor/critic 的 in_keys ∪ `action` ∪ `sample_log_prob` ∪ `("next", reward/done/terminated)`。
**写**（out_keys，L629-640）：`loss_objective`、`loss_entropy`、`loss_critic`、`entropy`、`value_clip_fraction`、`explained_variance`，Clip 版追加 `clip_fraction/ESS/kl_approx/max_ratio/mean_ratio`（L1346-1354）。

前向五步（ClipPPOLoss.forward L1362-1455）：

```
1. advantage 缺失 → 内嵌 value_estimator（GAE）现算（L1367-1377，传 detached critic params + target params）
2. 可选标准化（L1378-1388）
3. _log_weight：exp(log_prob_cur − log_prob_old)（L1390-1392）
4. 目标：gain = min(gain1, clip(gain1))（L1404-1411），ESS 用 no_grad 算（L1396-1402）
5. loss_critic（L1427-1435）→ 所有 loss_ 键过 _reduce_loss（L1442-1446）
```

### 模式与坑

1. **log 空间 clip**（L1332-1341）：非对称 DAPO 式 clip 在 log1p 域做，`clip_value=True` 与非对称 tuple 不兼容（docstring L1113-1117 有说明）。
2. **train/eval 模式陷阱**（docstring L1092-1096）：模型若在 eval 采集、train 训练（Dropout/BN 不一致），ESS 会剧烈漂移——官方把"ESS 异常 → 先查模式"写进了 docstring。
3. **advantage 维度陷阱**：L48-106 两个辅助函数专门对付"缺尾维 1"这一类静默广播 bug，报错信息给出 `unsqueeze(-1)` 修法。
4. **composite 分布**（多头动作）：L772-787 处理 `CompositeDistribution`，log-prob 是 TensorCollection 时用 `_sum_td_features` 求和，且要求用户脚本开头 `set_composite_lp_aggregate(False)`（L776-781 警告）。
5. KLPEN 的 beta 更新规则（L1771-1774）：KL > 1.5×dtarg 时 ×increment（默认 2），KL < dtarg/1.5 时 ×decrement（默认 0.5）——乘法调节使 beta 指数级追踪目标 KL。
6. **action 带梯度 = 报错**（L732-735、L765-768）：PPO 的 ratio 是显式重要性权重，action/log_prob_old 若可微说明数据流接错了。

---

## torchrl/objectives/sac.py

**1616 行 | 复杂度 complex | 图谱角色：最大熵 off-policy 连续控制旗舰**。图谱摘要：SACLoss（TanhNormal 策略 + 双 Q 取小 + 温度 α 自适应）与 DiscreteSACLoss（离散动作版）。

### 架构角色

SAC 展示 LossModule 三个高级特性的极限用法：**expand_dim 参数集成**（双 Q 变 N Q）、**vmap 批前向**（一个 batch 同时过 N 个 Q 网络）、**buffer 化系数**（log_alpha/target_entropy 都是 buffer，可调度可 checkpoint）。REDQ/TQC/CrossQ 等变体直接继承或复刻它。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_delezify` | L42 | 装饰器：state_dict/load 时剥离 TensorDict 包装 |
| `compute_rsample_log_prob` | L51 | 对 TanhDelta 等分布 rsample 并返回 (action, log_prob) |
| `SACLoss` | L59 | 主类（支持 v1/v2 两个 SAC 版本，`_version` 属性切换） |
| — `__init__` | L321 | actor + num_qvalue_nets 个 Q（expand_dim）+ 可选 value 网（v1） |
| — `_make_vmap` | L473 | vmap 或伪 vmap（`deactivate_vmap=True` 退化 for 循环） |
| — `target_entropy` property | L491 | **"auto" 惰性解析**：从 action_spec 推 −numel，首次访问后固化为 buffer `_target_entropy` |
| — `forward` | L655 | 调度 v1/v2 的 qvalue/value loss + actor + alpha |
| — `actor_loss` | L717 | `loss = α·logπ − min_i Q_i(s, ã)`（L743），ã 为重参数化采样 |
| — `_alpha` property | L764 | 读取时先 clamp log_alpha 到 [min,max]（L766）再 exp |
| — `qvalue_v1_loss` | L784 | v1：**batch 切成 N 份，每个 Q 只训自己那份**（L796-807） |
| — `_compute_target_v2` | L825 | v2 核心：`V_next = min_i Q_i(s',a') − α·logπ(a')`，写进 `("next", state_value)` 后交给 value_estimator 完成 TD 展开 |
| — `qvalue_v2_loss` | L903 | v2：全部 Q 对同一目标回归，td_error 取 max |
| — `value_loss` | L927 | v1 专用 value 网回归 |
| — `_alpha_loss` | L969 | `−log_alpha·(logπ + target_entropy)`（L972） |
| `DiscreteSACLoss` | L979 | 离散版：Q 输出全动作值，**期望可精确计算** |
| — `_compute_target` | L1402 | `V = Σ_a π(a)·[min_i Q_i(a) − α·logπ(a)]`（L1447/L1474）——连续 SAC 只能采样，离散可以枚举 |
| — `qvalue_loss` / `actor_loss` | L1482 / L1522 | 离散对应物 |
| — `_alpha_loss` / `alpha_loss` | L1554 / L1563 | α 温度损失 |

### 外部连接

- 出边 7 条：`data/tensor_specs.py`（action_spec 解析）、`data/utils.py`、`envs/utils.py`（ExplorationType）、`modules/distributions/utils.py`、`modules/tensordict_module/actors.py`、`objectives/common.py`、`objectives/utils.py`。
- 入边：`objectives/__init__.py`、`tqc.py`（TQC 继承 SACLoss 思路）、`trainers/algorithms/configs/objectives.py`（SACLossConfig）。
- 与 TargetNetUpdater 的配合：`SoftUpdate(loss_module)` 扫描 `target_qvalue_network_params` 等属性自动配对（utils.py L388-396 的 `target_` 前缀匹配正是为 SAC 设计）。

### 数据流

**读**：`("next", reward/done/terminated)`、obs 键、action 键（Q 训练时）、`td_error`→priority 权重。
**写**：`loss_actor`、`loss_qvalue`、`loss_alpha`（v1 加 `loss_value`）、`alpha`、`entropy`，以及**优先级键 `td_error`**（forward L668 直接 `tensordict.set(priority_key, ...)`，供 PrioritizedReplayBuffer 更新优先级）。

v2 目标链（最常考的一条数据流）：

```
_compute_target_v2 (L825):
  next_obs --(actor, RANDOM 模式)--> a', logπ'
  (s',a') --(vmap × N target Q)--> min_i Q^tar_i
  V_next = min Q − α·logπ'                        # L895
  TD: y = r + γ·(1-terminated)·V_next              # value_estimator.value_estimate (L900)
qvalue_v2_loss (L903): 每个 Q_i(s,a) 对 y 回归，取 td_error = |Q_i − y| 的 max (L917,924)
```

actor_loss 的 vmap（L729-737）：`td_q` 经 `_vmap_qnetworkN0` 前开后第 0 维是 Q 集成维，`min(0)` 取最悲观值。

### 模式与坑

1. **skip_done_states**（L846-875）：done 的 next 状态不喂 actor（避免对终止状态采样无意义动作），再用 masked_scatter 补零回原形状——MARL/RNN 场景不成立（docstring 明示默认 False）。
2. **target_entropy="auto"** 的解析时机是惰性的（L491-548）：composite action spec 需要显式传 `target_entropy` 或保证 actor 带 spec；解析结果注册成 buffer，所以 checkpoint 完整。
3. **log_alpha 的 clamp 在读取路径上**（L764-766）：任何用 α 的地方都会先 clamp——不会漏。
4. **v1 vs v2**：v1 的 Q 各自训半批数据（独立性更强），v2 全 Q 共享目标。`loss_function` 默认 smooth_l1。
5. **离散版 log(0) 防护**（L1460）：`torch.where(prob==0, 1e-8, prob)` 再 log。
6. `_cached_target_params_actor_value`（L773-782）：用 `TensorDict._new_unsafe` 把 actor+value 目标参数拼成一个嵌套容器，`@_cache_values` 保证同一数据流内只构建一次——functional 参数容器复用的典型优化。

---

## torchrl/objectives/dreamer_v3.py

**1138 行 | 复杂度 complex | 图谱角色：model-based RL 的损失标杆**。图谱摘要：模型损失（symlog/two-hot + balanced KL）、actor 损失（scaled return 的 reinforce）、value 损失三件套 + categorical KL 工具。

### 架构角色

DreamerV3 与其他损失有本质区别：**它训练的不是"环境数据上的策略梯度"，而是"想象轨迹上的策略梯度"**——actor/value 损失的输入是 world model 生成的 fake_data。三个损失各自独立 LossModule，由用户分别接 optimizer（对应论文的三个 actor-critic/world-model 优化器），文件导出的 `categorical_kl_terms/categorical_kl_balanced`（L61/L109）是 KL 平衡的参考实现。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `categorical_kl_terms` | L61 | 分离式 KL：dyn 项停 posterior 梯度、rep 项停 prior 梯度（L101-102），unimix 防确定性坍缩 |
| `categorical_kl_balanced` | L109 | 平衡式：`α·KL(sg(post)‖prior) + (1−α)·KL(post‖sg(prior))`（L118-119），free_bits **逐 categorical** clamp（L158-160，对齐 Hafner 2023 eq.5） |
| `_match_trailing_dim` | L165 | 广播辅助 |
| `DreamerV3ModelLoss` | L190 | 世界模型损失 |
| — `forward` | L386 | 见数据流 |
| `DreamerV3ActorLoss` | L498 | actor 损失 |
| — `forward` | L718 | 想象 rollout → λ-target → reinforce/reparam 二选一 |
| — `_return_scale` | L825 | **分位数归一**：return_low/high 两个 buffer 按 `return_normalization_rate` lerp 追踪分位边界（L828-839） |
| — `lambda_target` | L844 | λ-returns 递归（含 continuation 折扣） |
| `DreamerV3ValueLoss` | L913 | value 损失 |
| — `_resolved_gamma` | L1034 | gamma 从 actor_loss 的 estimator 读取（保证两边一致） |
| — `sync_gamma_with_actor_loss` | L1043 | 旧式两步构造的同步方法 |
| — `forward` | L1055 | two-hot 交叉熵或 symlog MSE + 可选 slow-critic 正则 |

### 外部连接

- 出边 10 条，最特别的是 `envs/model_based/dreamer.py`（DreamerEnv——actor 损失内部要造一个 model_based_env 来想象）和 `modules/models/model_based_v3.py`（ gracious heads：two-hot/symlog 编解码器）、`modules/functional.py`。
- 入边：`objectives/__init__.py`（它是 torchrl 少数"模型基"损失，被单独导出）。

### 数据流

**ModelLoss.forward**（L386-490）：输入真实环境 batch →

```
world_model(td) → prior_logits/posterior_logits        # RSSM 前后验
KL: balanced 或 separate 二选一（kl_mode）             # L398-413
重构: (symlog(pixels) − symlog(reco))² 逐元素           # L421-427
奖励: two_hot_cross_entropy(pred_logits, r, bins)      # L450-452
（旧版 symlog MSE 兼容路径 L453-455）
continue: BCE with logits（可选）                       # L475-487
出键: loss_model_reco / loss_model_reward / loss_model_kl（或 dynamic+representation 两键）/ loss_model_continue
返回 (td_out, tensordict.data)——第二个是给 actor/value 用的中间态
```

注意 L388-391 的键重命名：`("next", reward)` → `("next", true_reward)`，因为 world model 会**自己写一个预测 reward 键**，真值必须先改名避免冲突。

**ActorLoss.forward**（L718-823）：

```
选 state/belief → model_based_env.reset → rollout(imagination_horizon, policy=actor_model)  # L723-732
value_model 评 next value（hold_out_net 冻结）          # L734-735
lambda_target = λ-returns(reward, V, continuation)      # L749
discount = γ·continuation 的累积积（可选）              # L752-767
use_reinforce=True: advantage = (λt − baseline)/return_scale，loss = −(discount·logπ·adv)   # L776-790
  （注释 L777-779 点破：rollout 的 action 是重参数化采的，缓存 log-prob 带路径梯度，
    不是 score-function 估计，必须重算 log_prob）
否则: loss = −(discount·λt) 直接反传                    # L791-796
熵正则 ≤ 值损失熵 ×1e-4（dynamic entropy scaling 思想）
```

**ValueLoss.forward**（L1055-1138）：读 actor 写入的 `lambda_target` 与 `discount`（fake_data 上），two-hot 交叉熵或 symlog MSE；`slow_critic_regularization` 时额外向 target value 网回归（L1102-1125）。

### 模式与坑

1. **三损失 gamma 一致性**：value 的 gamma 从 actor 的 estimator 读取（`_resolved_gamma` L1034-1041），推荐构造时直接传 `actor_loss=` 实例。
2. **return 归一化只在 training 模式更新边界**（L828），eval 时 scale 冻结——评估不该改运行统计。
3. **two-hot logits 键正在迁移**：L433-443 与 L1079-1089 都有 deprecation warning——logits 要写到 `reward_logits/value_logits` 键而非解码后的值键（v0.16 移除）。
4. `categorical_kl_balanced` 的 free_bits 语义（per-categorical clamp）与 `categorical_kl_terms`（聚合后 clamp L103-105）**不一样**，别混用；前者对齐论文 eq.5。
5. REINFORCE 分支的 baseline 用的是**当前 value_model 在 fake_data 上的输出**（L783-787），且整个分支里 λt/baseline 都 detach，梯度只走 log_prob。

---

## torchrl/objectives/value/advantages.py

**2891 行（本篇最长）| 复杂度 complex | 图谱角色：GAE 等价值估计器的模块化封装层**。图谱摘要：ValueEstimatorBase 基类 + TD0/TD1/TDλ/GAE/MultiAgentGAE/VTrace 六估计器，封装键约定、梯度控制与向量化路径。

### 架构角色

pure 函数版估计器在 `value/functional.py`（`generalized_advantage_estimate` 等），本文件把它们包装成 **TensorDictModule**：自动调价值网络、处理 shifted 值调用、掩码 NaN、支持序列数据。损失的 `make_value_estimator` 最终落到这里（经 utils.py 的注册表 dispatch）。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_call_actor_net` | L89 | VTrace 用：调 actor 网算重要性比 |
| `ValueEstimatorBase` | L110 | 基类 |
| — `for_loss` | L140 | 类方法：从损失模块自动捡 critic/value 网络 |
| — `_AcceptedKeys` | L164 | advantage/value_target/value/reward/done/terminated/steps_to_next_obs/sample_log_prob 八键 |
| — `forward`（抽象） | L248 | 模板 |
| — `_call_value_net_shifted` | L648 | **shifted 技巧**：单次前向同时算 V(s) 与 V(s')（拼接送入再拆），大 batch 省一半调用 |
| — `_call_value_nets` | L785 | 两次调用版 + 分块（value_chunk_size/num_chunks） |
| — `_sanitize_next_nan` | L562 | done 但 next_obs 是 NaN 的场景清洗 |
| `TD0Estimator` | L962 | 单步 bootstrap → `td0_return_estimate` |
| `TD1Estimator` | L1245 | 蒙特卡洛回报 → `vec_td1_return_estimate` |
| `TDLambdaEstimator` | L1541 | λ 回报（标量/向量化双路径，`vectorized` 开关 L1682） |
| `GAE` | L1871 | **最常用**；forward L2070 |
| — `_prepare_signals` / `_normalize_advantage` | L2254 / L2277 | 子类扩展钩子（MultiAgentGAE 覆写） |
| `MultiAgentGAE` | L2378 | 广播到 agent 维（agent_dim=-2），团队共享信号广播 + agent 独立归一化 |
| `VTrace` | L2484 | IMPALA 截断重要性权重 |
| — `forward` | L2683 | 需要额外 actor 网络算 ρ（截断在 functional.py 完成） |
| `_deprecate_class` | L2875 | 旧类名（TDEstimate 等）的弃用包装 |

### 外部连接（图谱出边，全部是 calls）

- `TD0Estimator → functional.td0_return_estimate`、`TD1Estimator → vec_td1_return_estimate`、`TDLambdaEstimator → (vec_)td_lambda_return_estimate`、`GAE → (vec_)generalized_advantage_estimate`、`VTrace → vtrace_advantage_estimate`——**模块层只做接线，数学全在 functional.py**。
- 入边：`objectives/value/__init__.py`、`testing/modules.py`（测试工具造估计器）、trainers 装配层。
- GAE 与 PPO 的运行时连接：`PPOLoss.forward` L1367-1377 发现缺 advantage 时现场调用 `self.value_estimator(td, params=detached_critic, target_params=...)`。

### 数据流

GAE.forward（L2070-2250）标准流：

```
读 ("next", reward)（L2151）→ gamma/lmbda 搬到同 device
steps_to_next_obs 存在时 gamma 逐步指数化（L2159-2161，frame-skip 场景）
value_network 存在:
  params detach；target_params 缺省 clone 自 params（L2164-2167）
  _call_value_nets（shifted=True 走单次调用路径，产出 shifted_valid 掩码 L2183-2184）
  否则直接读 value / ("next", value) 两键（L2186-2196）
auto_reset_env: truncated 处理 reward += γ·V·truncated（L2214-2218）
vectorized=True: vec_generalized_advantage_estimate(...)（L2220-2230）
average_gae=True: 掩码感知归一化（L2243-2244 → _normalize_advantage L2277-2294）
写 advantage / value_target 两键（L2246-2247）
```

### 模式与坑

1. **shifted 与 T+1 预算**：`shifted_budget`（docstring L132-135）控制多出的时间槽位数——序列数据带内部 reset 时 2 才不丢样本。`shifted_valid` 掩码会被 GAE 写回 tensordict，PPO 的 `_standardize_advantage`（ppo.py L919）和 LossModule 的 auto loss_mask 都会捡它。
2. **梯度语义**：params 传入时 detach（L2164-2165），但**价值输出本身可能仍带对输入的梯度**（注释 L2171-2173："we may still need to pass gradient"）——GAE 估计优势时通常不该训 critic，故 PPO 传 `params=self._cached_critic_network_params_detached`。
3. **time_dim 解析顺序**（L2098-2101 docstring）：显式参数 > 维度名 "time" > 最后一维。多智能体 [B, T, A] 数据必须显式传或命名时间维。
4. **MultiAgentGAE 的两处覆写**：`_prepare_signals` 把团队级 done 广播到 agent 维、`_normalize_advantage` 排除 agent 维各自归一——继承一个钩子就能改语义，这是基类设计的教科书示范。
5. VTrace 的 `for_loss`（L2591）覆写：额外从损失模块抓 actor 网络（重要性比必需）。

---

## torchrl/objectives/llm/grpo.py

**1922 行 | 复杂度 complex | 图谱角色：LLM 后训练（RLHF/GRPO）的损失与环境侧基础设施**。图谱摘要：GRPOLoss 及变体 DAPO/CISPO，配合 MCAdvantage（共享队列 + Ray 分布式）支持大模型 RL 微调。

### 架构角色

这个文件是 torchrl 从"传统 RL 库"跨入"LLM 后训练框架"的枢纽，包含两类组件：

1. **GRPOLoss 家族**（LossModule）：token 级 PPO-clip 目标 + 组相对优势；
2. **MCAdvantage**（`Transform`，挂在 replay buffer 上）：**组内归一化的蒙特卡洛优势**——GRPO 的灵魂在损失侧只是"读 advantage"，真正组内标准化发生在这条回放侧 transform 里。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `LLMLossOutput` | L48 | TensorClass 输出容器（nocast） |
| `_MCAdvantageSharedQueues` | L99 | 跨进程共享队列（multiprocessing manager 代理） |
| `MCAdvantageSelector` | L154 | 候选组选择器：uniform / length-balanced |
| `GRPOLoss` | L355 | 主损失 |
| — `__init__` | L483 | masking_strategy（rlhf/sft/generic）、aggregation、kl 系数等 |
| — `forward` | L649 | 见数据流 |
| — `_compute_policy_objective` | L761 | 默认 PPO 式 min(gain1, clipped gain) |
| — `_aggregate_loss_value` | L776 | **token_mean / prompt_mean / none** 三种聚合（L784-808） |
| — `_kl_to_ref` | L849 | k3 估计器：`(exp(diff)−1−diff).mean()`（L886-887），diff = logπ_ref − logπ_cur |
| — `_log_weight` | L890 | 与 PPO 同构 + attention mask 对齐 + masking_strategy 报错提示（L913-927） |
| `DAPO` | L953 | 校验非对称 clip（推荐 (0.20, 0.28)） |
| `CISPOLoss` | L1004 | 覆写 `_compute_policy_objective` 实现裁剪式 IS 目标 |
| `MCAdvantage` | L1028 | **组相对优势 Transform**（docstring 含完整 doctest L1116-1147） |
| — `requires_shared_write_state` | L1151 | 声明需要共享写状态 |
| — `share_memory_` | L1256 | 队列/计数器搬到 mp manager（`TORCHRL_MC_ADVANTAGE_LOCAL_QUEUES=1` 可关，L1072-1082） |
| — `_inv_call_single` | L1442 | **单轨迹处理核心**（在 `_state_lock` 下执行） |
| — `_trajectory_advantage` | L1534 | 轨迹级优势 + 动态采样过滤 |
| `_MCAdvantageRayActor` | L1600 | Ray actor 版队列宿主 |
| `RayMCAdvantage` | L1664 | 队列/统计集中到 Ray actor 的 Transform 变体 |

### 外部连接

- 出边：`objectives/common.py`、`objectives/utils.py`、`envs/transforms/transforms.py`（Transform 基类）、`envs/transforms/ray_service.py`、`modules/llm/__init__.py`、`modules/distributions/utils.py`。
- 入边：`objectives/llm/__init__.py`。它与 `envs/llm/`（本篇第 17 节）构成 LLM 训练闭环：ChatEnv 采集 → MCAdvantage 组队 → GRPOLoss 训练 → vllm_nccl 同步权重。

### 数据流

**GRPOLoss.forward**（L649-759）：

```
读 action 键（必须存在 L653-654）+ advantage（必须存在 L657-663）
_log_weight (L890): cur_log_prob 由 actor 现算（left-padding 对齐 L896-901），
  attention_mask 屏蔽 padding 位（L929-935），log_weight 逐 token
可选 kl_mask_threshold：逐 token KL 近似 0.5·(logπ_cur−logπ_inf)² 超阈值 → 屏蔽（L670-693）
_compute_policy_objective (L761): min(ratio·A, clip(ratio)·A) 逐 token
_aggregate_loss_value: token_mean（默认，全局 token 均值）/ prompt_mean（先样本内均值再批均值）/ none
可选 loss_kl_to_ref: k3 无偏 KL 对 ref_log_probs（L849-888）
可选 loss_kl_to_inference: 同式对推理引擎 log-prob（保持训练/推理引擎一致）
输出 LLMLossOutput（loss_objective / clip_fraction / ESS / entropy / kl_* ...）
```

**MCAdvantage 的组内归一化流程**（这是任务点名的重点）：

```
replay buffer 写入路径（inv 方向）触发 _inv_call_single (L1442):
1. 校验：单条 1 维轨迹、末步 done（L1449-1454）
2. group = tensordict[0][prompt_key]（字符串或张量 id，张量按值分组 L1456-1464）
3. 轨迹入组队列 self.queues[group]（L1481）
4a. trajectory_return=None（原始 LLM GRPO 语义）：
    队列满 grpo_size → 拼批，逐 step 奖励全体做 (r − mean)/std（L1516-1523），
    advantage 写进每条轨迹每个 step —— 稀疏奖励下同组 step 的 advantage 相同
4b. trajectory_return="sum"/"max"/"mean"（SimpleVLA-RL 语义，稀疏轨迹级奖励）：
    每条轨迹先归约成标量 return（L1527-1532）
    候选满 candidate_selection_min_size → _trajectory_advantage (L1534)：
      MCAdvantageSelector 选 grpo_size 条（uniform 或 length-balanced）
      keep_return_bounds=(low,high)：组均值 return 出界 → 整组丢弃（DAPO 动态采样，
        "全对/全错组无学习信号"L1581-1591）
      A_i = (R_i − mean(R))/std(R)，广播到该轨迹全部 step（L1592-1596）
    选不出有用子集且队列到 candidate_group_size → 整组丢弃（L1501-1504）
5. 完成组以拼接 TensorDict 返回（写进真正的 storage）
```

统计计数器（completed_trajectories/written_groups/dropped_groups/rescued_groups…）通过 `_get_stat/_set_stat`（L1283-1289）与 `@property` 暴露，Ray 版远程转发。

### 模式与坑

1. **优势计算必须在回放侧**：组需要"同一 prompt 的 G 条完整轨迹"才齐，任意 worker 单独看都不完整——所以 MCAdvantage 挂在**共享 replay buffer** 上而非损失里；多 writer 时 `share_memory_` 把队列集中（L1064-1070 docstring）。
2. **std 防零**：`.clamp_min(1e-6)`（L1520、L1592）——全对/全错组 std=0 会除零，虽有动态采样兜底仍要防。
3. **left padding 约定**：`sample_log_prob`/`ref_log_probs` 一律 `padding_side="left"`（L674-677、L864-867）读取，与 vLLM 生成侧对齐，否则 log_weight 逐 token 错位。
4. **三种 masking_strategy**（sft/rlhf/generic）决定哪些 token 计损失；shape 不匹配的报错信息（L913-927）直接给出排查顺序——这是社区最高频 issue。
5. `_cur_log_prob` 是 `_log_weight` 塞进 tensordict 的临时键，forward 结尾 `del`（L758）避免泄漏进 storage。
6. RayMCAdvantage 的 `forward` 是直通（L1879），只有 inv（写缓冲）路径走 actor——读路径零开销。

---

## torchrl/trainers/trainers.py

**3229 行（本篇次长）| 复杂度 complex | 图谱角色：训练层的中枢**。图谱摘要：Trainer 主类（56 方法）+ 19 个 TrainerHookBase 训练钩子（优化、日志、回放、权重同步、早停、LR 调度）。

### 架构角色

Trainer 是 torchrl 最顶层的编排器，设计哲学是**"空壳主循环 + 全 hook 化"**（docstring L324-326："Trainer does not construct any of its specific operations: they all must be hooked"）。它自己只懂：迭代 collector → 数帧 → 触发优化子循环 → 存档；其余一切（回放采样、目标网更新、权重同步、日志、早停）都是注册进来的 hook。新版还支持 `learner_backend="ray"` 把优化循环整体搬到远端（`_train_with_execution_backend` L1464）。

### 内部结构

**A. 基础设施（L92-318）**

| 成员 | 行号 | 职责 |
|---|---|---|
| `_torch_load_defaults` | L92/97 | torch 版本兼容的 load 默认参 |
| `_TrainerCheckpointState` / `_ExecutionCheckpointState` | L104 / L120 | checkpoint 状态适配器 |
| `_state_dict_to_td` / `_td_to_state_dict` | L148 / L164 | state_dict ↔ TensorDict |
| `TrainerHookBase` | L173 | hook 抽象基类：`__call__/state_dict/load_state_dict/register` 四件套 |
| `OptimizationStepper` | L200 | **新优化协议**：封装 backward/step 与梯度状态 |
| `DefaultOptimizationStepper` | L249 | 默认实现：可选梯度裁剪 + step（L288-318） |

**B. Trainer 主类（L320-1787，核心方法）**

| 方法 | 行号 | 职责 |
|---|---|---|
| `__init__` | L413 | 装配 collector/loss/optimizer/stepper/checkpoint；ray 后端时构造 `_execution_backend` |
| `_sync_checkpoint_components` | L675 | 把 collector/rb/loss/logger/hook 纳入统一 checkpoint 名册 |
| `state_dict` / `load_state_dict` | L806 / L816 | 聚合 app_state |
| `_save_trainer` / `save_trainer` | L835 / L919 | 定期/强制存档（manifest 元数据 L906） |
| `load_from_file` | L928 | 从 checkpoint 复活 Trainer |
| `register_op`（=register_hook 别名 L1230） | L1058 | **18 个挂点**的分发中枢（见下） |
| `train` | L1400 | 主循环（本地后端） |
| `_train_with_execution_backend` | L1464 | ray 后端主循环：replay 写够 → backend.step(N) → 收 metrics → 发布权重 |
| `optim_steps` | L1653 | 优化子循环（epoch × steps_per_batch） |
| `_log` | L1713 | logger + 进度条双写 |

**C. 19 个 Hook（L1807-3226）**：`SelectKeys`(L1807)、`ReplayBufferTrainer`(L1852)、`OptimizerHook`(L1969)、`ClearCudaCache`(L2059)、`LogTiming`(L2088)、`LogScalar`(L2165)、`RewardNormalizer`(L2271)、`BatchSubSampler`(L2400)、`LogValidationReward`(L2530)、`UpdateWeights`(L2690)、`CountFramesLog`(L2812)、`TargetNetUpdaterHook`(L2882)、`ValueEstimatorHook`(L2911)、`LRSchedulerHook`(L2961)、`UTDRHook`(L3024)、`EarlyStopping`(L3092)，辅助函数 `mask_batch`(L1790 附近)/`flatten_dict`(L2869)。

### 外部连接

- 出边 11 条：`checkpoint/`、`collectors/`、`data/replay_buffers/`、`envs/common.py`、`objectives/{common,utils}.py`、`record/loggers/`——**它是唯一下游，objectives 层的最终消费者**。
- 入边 12 条：`trainers/__init__.py`、helpers/trainers.py、algorithms/ 下 8 个装配脚本、`_execution.py`、`_ray_execution.py`。
- 所属层：`layer:trainers`（最顶层使用者 API）。

### 数据流

**register_op 的 18 个挂点**（L1060-1079 字面量）按时序排列：

```
setup
→ [每个 collector batch] batch_process（SelectKeys→cpu→RewardNormalizer.stats→RBTrainer.extend）
→ pre_steps_log（LogScalar/CountFramesLog）
→ [若 frames ≥ init_random_frames] optim_steps 子循环：
    pre_optim_steps（ClearCudaCache/reset_noise）
    pre_epoch → pre_epoch_log
      process_optim_batch（RBTrainer.sample 或 BatchSubSampler→to(device)）
      → loss_module(sub_batch) → post_loss（RB.update_priority，弃用中）
      → process_loss（弃用中）→ optimizer（backward+step，弃用中）
      或 optimization_stepper.step(trainer, sub_batch)（新路径）
      → post_optim（target_net_updater.step / lr_scheduler.step）
      → post_optim_log
    post_epoch_log → post_epoch
→ post_steps（UpdateWeights / policy_exploration.step）
→ post_steps_log（LogValidationReward ×2）
→ pre_epoch/post_epoch 兜底 → shutdown
```

**train() 主循环**（L1400-1462）：同步模式逐 batch 走上述流程，帧数用 `("collector","mask")` 求和×frame_skip（L1422-1427，pad 数据不计帧）；`_stop_training` 或达 total_frames 时 `save_trainer(force_save=True)` 后 break。异步模式（L1407-1413）由 collector 后台写 rb、主循环轮询 write_count。

**optim_steps()**（L1653-1711）：嵌套 for（epochs × steps_per_batch），`_process_optim_batch_hook` 抛 `StopIteration`/返回 None 即提前结束（BatchSubSampler 切完子批的信号）；增量平均 losses（L1696-1701）避免内存爆；结束后 `_post_optim_complete_log_hook` 一次性写平均损失。

### 模式与坑

1. **ray 后端的挂点封锁**（L1083-1095）：`learner_backend="ray"` 时只有 6 个本地挂点可用，其余报错——因为优化循环在远端 actor 里，本地 hook 够不着。错误信息会引导改用 OptimizationStepper。
2. **三段弃用迁移**：`post_loss/process_loss/optimizer` 三个挂点正被 `OptimizationStepper` 取代（L1122-1159 三处 FutureWarning），新代码用 `optimization_stepper=DefaultOptimizationStepper(...)` 传给构造器。
3. **帧数计数双轨**：`collected_frames`（当前）与 `_collected_frames`（弃用）并存（L401-409）；pad batch 必须靠 collector mask 扣除 padding 帧。
4. **`UpdateWeights` hook**（L2690-2809）：新版 `weight_update_map={"policy": "loss_module.actor_network", ...}` 用 `_resolve_module`(L2667) 按点分路径在 trainer 上解析源/目标——比旧 `policy_weights_getter` 声明式且可同步多个模型（如 replay buffer 上的 transform）。
5. **EarlyStopping**（L3092-3226）支持 `patience/min_delta/mode`，通过 `trainer.request_stop(reason)`（L830）温和停机而非硬抛。
6. 每个 hook 注册时自动被 `_wrap_hook_with_timing`（L751）包一层可选计时（`log_timings=True` 时输出 `time/hook/<Name>` 指标）。

---

## torchrl/trainers/helpers/trainers.py

**301 行 | 复杂度 complex | 图谱角色：旧版一键组装入口**。图谱摘要：make_trainer 一站式工厂（collector/env/replay/loss/logger/hooks 全装配）+ TrainerConfig dataclass。

### 架构角色

新代码应使用 `trainers/algorithms/`（Hydra 配置驱动），但这个文件是**理解"一个完整 Trainer 需要哪些零件"的最短教材**——222 行装配链把 trainers.py 的挂点全部用一遍。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `OPTIMIZERS` | L37 | adam/sgd/adamax 映射 |
| `TrainerConfig` | L44 | 14 字段 dataclass（optim_steps_per_batch=500、lr=3e-4、clip_norm=1000…） |
| `make_trainer` | L80 | 工厂主函数 |

### 外部连接

- 出边 10 条：collectors、replay_buffers、envs/common、modules（reset_noise）、objectives/{common,utils}、record/loggers、trainers/trainers.py——横跨全库。
- 入边：`trainers/helpers/__init__.py`。

### 数据流（make_trainer 装配链，L142-301）

```
optimizer: adam 默认 betas=(0.0, 0.9)（L153，DDPG 系约定俗成）+ 可选 Cosine LR
Trainer(collector=..., loss_module=..., optimizer=...)
CUDA 存在 → pre_optim_steps 挂 ClearCudaCache
noisy 网 → pre_optim_steps 挂 reset_noise
selected_keys → batch_process 挂 SelectKeys；无论如何 batch → cpu
有 replay_buffer：batch_process.extend / process_optim_batch.sample / post_loss.update_priority
无 rb（纯 on-policy）：process_optim_batch 挂 BatchSubSampler + to(device)
post_optim ← lr_scheduler.step + target_net_updater.step
normalize_rewards_online → batch_process 更新统计 + process_optim_batch 归一
policy_exploration.step → post_steps
lr 标量 → post_steps_log
recorder：两个 LogValidationReward（确定性 + 探索模式，L258-292）
post_steps ← UpdateWeights(collector, interval=1)
pre_steps_log ← LogScalar + CountFramesLog
```

### 模式与坑

1. cfg=None 时打警告并造默认配置（L142-151）——仅调试用。
2. 双验证记录器的差异在 `exploration_type=ExplorationType.RANDOM` 与 `out_keys` 重命名（L276-285），reward 曲线与 reward_exploration 曲线对照是判断"探索退火是否过头"的常用手段。
3. 这个文件属于 legacy API：与 `trainers/algorithms/configs/` 的新配置系统平行存在，图谱 tags 直接标了 `legacy-api`。

---

## torchrl/trainers/algorithms/configs/__init__.py

**819 行 | 复杂度 complex | 图谱角色：Hydra 配置系统总入口**。图谱摘要：汇总导入全部配置类并 `__all__` 导出，`_register_configs` 按分组惰性注册到 Hydra ConfigStore，构成可组合的 RL 训练配置注册表。

### 架构角色

把 torchrl 全部可配组件（环境/网络/损失/回放/采集/hook/日志/权重同步）变成 Hydra 可组合配置组——这是 `torchrl/trainers/algorithms/` 里 `sac.py`、`dqn.py` 等脚本能用一行 `@hydra.main(config_path="../configs", config_name="sac_config")` 跑起来的基础。

### 内部结构

| 段落 | 行号 | 内容 |
|---|---|---|
| hydra 可用性检查 | L10-21 | 缺 hydra-core/omegaconf 直接 ImportError（提示 `pip install 'torchrl[utils]'`） |
| 批量 import | L23-140+ | collectors/common/data/envs/envs_libs/hooks/logging/modules/objectives/trainers/transforms/utils/weight_* 共 14 个子模块的配置类 |
| `__all__` | ~L145-466 | 100+ 配置类名（含 8 个 WeightUpdaterConfig、9 个 WeightSyncSchemeConfig） |
| `_register_configs` | L468 | 注册函数（~350 行 cs.store 调用） |

### 外部连接（图谱出边 15 条）

导入 `configs/` 下全部子模块：collectors/common/data/envs/envs_libs/envs/hooks/logging/modules/objectives/trainers/transforms/utils/weight_sync_schemes/weight_update。无入边（终端消费者是 hydra CLI）。

### 数据流（_register_configs 的分组注册）

```
group="env"：gym/batched_env/transformed_env + 15 个库专属（brax/dm_control/habitat/
  isaac_gym/jumanji/meltingpot/mo_gym/mjlab/multi_threaded/openml/openspiel/
  pettingzoo/robohive/smacv2/unity_mlagents/vmas）      # L485-505
group="network"：mlp/convnet/qmixer/vdn_mixer/tensordict_module/tensordict_sequential
group="model"：tanh_module/tanh_normal/value/qvalue
group="transform"：50+ 个（observation_norm/reward_clipping/vec_norm/…）# L539-591
group="loss"：ppo/a2c/ddpg/dqn/sac/td3/iql/cql/tqc/…    # L640 附近
group="value"：gae
group="target_net_updater"：soft/hard
group="replay_buffer"/"sampler"/"storage"：tensordict/random/prioritized/slice/lazy_stack/list…
group="collector"/"hook"/"logger"/"trainer"/"weight_update"/"weight_sync_scheme"
```

用户在 YAML 里 `env: gym` + `loss: ppo` + `value: gae` 即完成算法组装——**配置组名与 torchrl 概念一一对应**。

### 模式与坑

1. **import 即校验**：文件顶部 import 失败会炸掉整个包——所以 hydra 是 `[utils]` extra 而非核心依赖，纯库用户不受影响。
2. 注册是**函数体惰性执行**（`_register_configs` 在被调用时才 store），避免 import 副作用。
3. weight_update/weight_sync_scheme 两组（L455-465 附近的 `__all__`）映射到本篇第 14/15 节的类——配置系统与分布式层同步演化（vLLMUpdaterConfig/VLLMWeightSyncSchemeConfig 已入册）。

---

## torchrl/record/loggers/common.py

**391 行 | 复杂度 complex | 图谱角色：日志子系统的协议核心**。图谱摘要：Logger 抽象基类（`__init_subclass__` 自动包装 process/ray 服务后端）+ `_write_video` + `_make_metrics_safe`（CUDA 事件同步的跨进程安全化）。

### 架构角色

定义"什么是一个日志器"：四个抽象方法（`log_scalar/log_video/log_hparams/log_histogram`）+ 生命周期（`start/flush/shutdown/close`）+ 可序列化（`state_dict/load_state_dict`）。所有具体后端（csv/tensorboard/wandb/mlflow/trackio/monitoring）继承它。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_write_video` | L29 | (T,H,W,C)→(T,C,H,W) 转 torchcodec VideoEncoder 写 mp4；**torchcodec 缺失直接报错**（不再回退 torchvision，L30-38 的错误信息教你怎么装） |
| `_make_metrics_safe` | L74 | 两遍法：先所有 CUDA 张量 `to("cpu", non_blocking=True)`，**一个 CUDA Event 同步**（L127-130），再逐个 item/tolist |
| `_make_metrics_safe_tensordict` | L142 | TensorDict 版：批量 `.to("cpu")` + flatten_keys |
| `Logger` | L186 | 基类（metaclass=`_RayServiceMetaClass`） |
| — `__init_subclass__` | L205 | **服务化魔法**：给每个子类挂 `_RayServiceClass`/`_ServiceClass` 工厂 |
| — 生命周期 | L264-308 | start/is_alive/client/flush/shutdown/close |
| — state_dict | L310-332 | 只存 exp_name/log_dir + 子类 local 计数 |
| — 4 个抽象方法 | L334-358 | 子类契约 |
| — `log_metrics` | L360 | 批量入口：先 `_make_metrics_safe` 再逐项 log_scalar |

### 外部连接

- 入边 **12 条**：`loggers/__init__.py`、`_service.py`、csv/mlflow/trackio/wandb/monitoring/process/ray/tensorboard 六后端、`loggers/utils.py`、`render/video.py`。
- 上游消费者：trainers.py 的 `_log`、LogScalar/LogTiming 等 hook。

### 数据流

`log_metrics({"loss": cuda_tensor, ...}, step)` →

```
_make_metrics_safe: dict 遍历 → CUDA 张量 non_blocking 拷贝 → Event.record()+synchronize()
→ numel==1 ? .item() : .tolist() → 纯 Python dict
逐项 log_scalar → （可能跨进程的）具体后端
```

`__init_subclass__` 的服务化（L205-256）：定义 `class WandbLogger(Logger)` 后，调用 `WandbLogger(service_backend="process", *args)` 实际返回 `ProcessLogger(WandbLogger, *args)`——**子类永远不用自己处理进程/Ray 化**，这是模板方法+元编程的组合拳。

### 模式与坑

1. **Event 同步而非 `torch.cuda.synchronize()`**（注释 L124-126）：Event 只等它 record 之前入队的拷贝，不阻塞整卡——训练主循环里频繁打日志时的关键优化。
2. TensorDict 版在 `torch.cuda.is_initialized()` 时才做 Event 同步（L163-166）——纯 CPU 训练零开销。
3. `shutdown` 后再 `start` 会 RuntimeError（L266-267）——服务日志器不可重启，需新建。
4. 视频方向坑：docstring L56 明示调用方传 (T,H,W,C)，函数内 permute 成编码器要的 (N,C,H,W)。

---

## torchrl/record/recorder.py

**711 行 | 复杂度 complex | 图谱角色：训练过程可视化三件套**。图谱摘要：VideoRecorder（定期渲染滚动视频）、TensorDictRecorder（转储 TensorDict）、PixelRenderTransform（把 env.render 像素写进 next 观测）。

### 架构角色

三个类都是 **Transform**（挂在 TransformedEnv 上随环境步进而观察数据），把"训练中发生了什么"变成 mp4/gif/npz 工件。与 loggers/common.py 的 Logger 协作：VideoRecorder.dump 最终调用 `logger.log_video`。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `_make_video_grid` | L29 | 无 torchvision 依赖的 [N,C,H,W] 方阵拼图 |
| `VideoRecorder` | L43 | ObservationTransform 子类 |
| — `__init__` | L142 | logger/tag/in_keys/skip/center_crop/make_grid/max_frames |
| — `_apply_transform` | L221 | **逐帧采集**：count%skip 采样 → 通道对齐（[...,C,H,W]→[...,H,W,C]，L231-236）→ 灰度扩 3 通道（L238-241）→ uint8 存 self.obs |
| — `_step` | L292 | `dump_on_done` 时轨迹结束自动 dump（L292-299） |
| — `to_animation` | L325 | matplotlib 可用时转 gif |
| — `dump` | L395 | obs 列表 → (T,H,W,C) → logger.log_video / mp4 |
| `TensorDictRecorder` | L433 | `_call` 缓存 next_tensordict，dump 序列化落盘 |
| `PixelRenderTransform` | L501 | 调父环境 render，像素写进 next 观测键 |
| — `transform_observation_spec` | L661 | 相应改 spec |
| — `switch` / `enabled` | L680 / L698 | 运行时开关（省渲染开销） |

### 外部连接

- 出边：`data/tensor_specs.py`、`envs/__init__.py`、`envs/transforms/__init__.py`、`record/loggers/__init__.py`、`services/base.py`（Service 基类——logger 可以是服务）。
- 入边：`record/__init__.py`、`trainers/helpers/envs.py`（make_rgb_env 之类装配时插入）。

### 数据流

```
env.step → _apply_transform(observation)（环境变换链的一环）
  → 每 skip 帧转 uint8 append 到 self.obs（CPU）
dump(suffix, step):
  stack → (T,H,W,C) → Logger.log_video（进而 _write_video 编码 mp4）
  或 to_animation 出 gif
```

### 模式与坑

1. **skip 默认值的差异**（docstring L59-61）：向量化环境/独立用 1，单个父环境 2——渲染器会把 batch 维也画进同一帧（make_grid），帧率视觉上翻倍所以 skip=2。
2. `_apply_transform` 是**透传变换**：返回原 observation（L289 附近 return observation），只偷看不改数据——渲染零副作用。
3. 形状启发式（L231-243）用 "末三维中第一维 ∈{1,3} 且后两维>3" 判通道位——极端小图（≤3 像素）会误判。
4. `dump_on_done` 依赖 `_all_done`（L300）检查整批 done；向量化环境部分 done 时等全员结束才 dump。

---

## torchrl/render/config.py

**416 行 | 复杂度 complex | 图谱角色：渲染子系统的数据模型核心**。图谱摘要：RenderConfig 主 dataclass + RenderEnvSpec/RenderPolicySpec/FrameBundle/RenderResult + Literal 类型别名；**零内部依赖**。

### 架构角色

torchrl 新渲染栈（`render/` 包：cli.py/rollout.py/policy.py/env.py/backends/…）的"宪法"：一切渲染入口（CLI/notebook/API）都从 RenderConfig 出发。图谱显示它被 render/ 下 **12 个文件 import** 且自身无出边——纯数据层。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| 8 个 Literal 别名 | L18-25 | RenderFormat（ipynb/mp4/gif/frames/npz/jsonl）、CameraLayout、RenderBackendName、NotebookRenderBackendName、NotebookRolloutMode、EnvBackendName、ExplorationMode |
| `RenderConfig` | L46 | 主配置（45+ 字段） |
| — 字段区 | L72-115 | ckpt/policy/env 三必需 + num_trajs/format/fps/camera/camera_layout/deterministic/seed/device/policy_device/env_device/render_backend/…checkpoint_key/strict_load/auto_load_policy/obs_key/action_key/from_pixels/save_*/mujoco_*/notebook_viewer_port/dry_run/validate_only |
| — `__post_init__` | L121 | Path 化 + `_validate_choice` 枚举校验 |
| — `to_dict` / `to_json` | L202 / L229 | 序列化（设备/可调用对象安全化） |
| `RenderEnvSpec` | L235 | 环境工厂规格：import spec（"module:obj" 字符串）+ backend + kwargs；`from_config` L272 |
| `RenderPolicySpec` | L291 | 策略工厂规格 + 权重加载选项 |
| `FrameBundle` | L322 | 单帧元数据（步索引/轨迹索引/来源键） |
| `RenderResult` | L348 | 渲染产物容器：paths/trajs/frames/metadata/warnings |
| `parse_nested_key` 等 4 个工具 | L374-414 | 键解析/CSV 拆分/可调用命名/枚举校验 |

### 外部连接

入边 12 条全在 render/ 包内（__init__/artifacts/backends×4/cli/env/mujoco_wasm/notebook/policy/rollout）；无出边。

### 数据流

```
RenderConfig(policy="project.policy:make_policy", env="...", ckpt="policy.pt")
  → RenderPolicySpec.from_config：延迟 import 工厂，load checkpoint
  → RenderEnvSpec.from_config：按 env_backend 选 torchrl/gym/mujoco/… 构造
  → rollout.py 跑 num_trajs 条轨迹 → backends/{pixels,env,null} 渲染
  → RenderResult（mp4/gif/frames/npz/jsonl/ipynb 之一或多）
```

### 模式与坑

1. **工厂即字符串**：`"module:object"` import spec 让配置可 JSON 序列化、可跨进程传递——与 configs/__init__.py 的 Hydra 思路一致但更轻。
2. `validate_only=True`/`dry_run=True` 支持只校验不渲染（CI 友好）。
3. `device/policy_device/env_device` 三分：渲染常用 cpu 策略 + gpu 环境（或反之）。
4. `_validate_choice`（L414）在 `__post_init__` 里逐枚举字段校验，错误在构造期而非渲染中途爆炸。

---

## torchrl/weight_update/weight_sync_schemes.py

**1360 行 | 复杂度 complex | 图谱角色：权重同步框架的抽象核心**。图谱摘要：WeightSyncScheme 抽象基类（sender/receiver 生命周期、指令-ACK 协议、后台接收线程）、WeightStrategy（full/dtensor/LoRA）、TransportBackend/InitialSyncTransport Protocol 与后端注册表。

### 架构角色

torchrl v2 分布式权重同步的**模板方法框架**：定义"学习者怎么把最新策略权重推给采集 worker"。所有具体后端——`_mp.py`（多进程）、`_shared.py`（共享内存）、`_ray.py`、`_rpc.py`、`_distributed.py`（DDP）、`_noupdate.py`、`llm/vllm_nccl.py`、`llm/sglang_nccl.py`、`llm/vllm_double_buffer.py`——共 9 个实现继承这里的 `WeightSyncScheme`。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `TransportBackend` | L39 | **Protocol**：`send_weights/receive_weights` 数据面接口 |
| `InitialSyncTransport` | L70 | **Protocol**：初始建连 + 交换初始权重 |
| `register_weight_sync_backend` | L114 | 字符串别名 → 类的全局注册表 |
| `WeightStrategy` | L145 | 权重提取/应用策略 |
| — `extract_weights` | L172 | tensordict / state_dict 两种形态，支持 dtensor 与 **LoRA-only** |
| — `apply_weights` | L228 | 接收侧应用（含 LoRA 合并） |
| `_merged_lora_state_dict` | L332 | LoRA 权重合并进基座 |
| `WeightSyncScheme` | L346 | **抽象基类主体** |
| — `from_backend` | L397 | 按注册名构造 |
| — `init_on_sender` ×10 重载 | L435-523 | **多重载分发**：支持 collector/model/engine 等不同签名，统一落到 `_init_on_sender_impl`(L541) |
| — `init_on_receiver` | L553 | 接收侧初始化（`_init_on_receiver_impl` L603） |
| — context/model_id/worker_idx/model/weights 属性 | L616-723 | 注册的采集器、模型 id、权重缓冲 |
| — `_register_worker_sender` / `_register_transport_receiver` | L740 / L768 | worker ↔ transport 配对记账 |
| — `create_transport` | L806 | 工厂方法（子类覆写返回具体 Transport） |
| — `send` | L872 | **同步发送协议**：prepare → 逐 transport 发送（有 async 就 async）→ 逐个 wait_ack |
| — `prepare_weights` | L932 | 权重解析：None→从 context 模型提取；nn.Module→strategy.extract；str→按名解析 |
| — `receive` | L985 | 接收侧非阻塞轮询（后台线程常调） |

### 外部连接

- 入边 **17 条**（本组最多）：collectors 侧 `_base.py`、`_single.py`、distributed/{generic,rpc,ray,_ray_eval_runtime}.py；trainers 侧 `_execution.py`；weight_update 下全部 9 个后端文件 + `__init__.py`。
- 出边仅 2 条（`_utils.py`、`weight_update/utils.py` 的 `_resolve_model`）——**依赖倒置的样板：抽象核心几乎不依赖任何人，所有人依赖它**。

### 数据流（send 全流程，L872-930）

```
sender.send(weights=None):
  校验 initialized_on_sender + synchronized_on_sender
  prepare_weights: context 里按 model_id 解析模型（找不到回落 collector._fallback_policy L944-948）
    → strategy.extract_weights(model)（tensordict 或 LoRA-only）
  for transport in _iterate_transports(worker_ids):
    transport.send_weights_async(prepared)  # 无 async 方法则退化同步 send
  for transport: transport.wait_ack()       # 指令-ACK：确认 worker 已应用
receiver 侧: 后台线程轮询 receive(timeout) → apply_weights 到注册的模型 → ACK
```

### 模式与坑

1. **Protocol 而非 ABC**：TransportBackend/InitialSyncTransport 是 `typing.Protocol`——鸭子类型，第三方传输层无需继承（静态检查仍受益）。
2. **init_on_sender 的 10 连重载**（L435-523）是 API 演化的化石层：不同版本 caller 传 collector/model/engine 组合都能接，最终归一到 impl——读代码时直接跳 impl。
3. **LoRA 同步**：`extract_as="state_dict"` + LoRA 策略只传适配器权重（网络流量骤减），接收侧 `_merged_lora_state_dict` 合并——LLM 微调场景的关键路径。
4. **ACK 语义**：send 返回即"worker 已应用"，不是"已发送"——省心的强一致，但慢网络下会阻塞学习循环（可看 vllm_double_buffer 的双缓冲优化）。
5. worker_ids 精确投递：None=全体，int/list=指定 worker——多模型多 worker 拓扑下避免广播浪费。

---

## torchrl/weight_update/llm/vllm_nccl.py

**804 行 | 复杂度 complex | 图谱角色：vLLM 推理引擎的 NCCL 权重热同步**。图谱摘要：VLLMCollectiveTransport 初始化 NCCLWeightTransferEngine 自定义通信组，VLLMWeightSender/Receiver 在训练器与 vLLM worker 间广播权重并触发热加载。

### 架构角色

GRPO 训练闭环的"最后一公里"：策略梯度更新后的 LoRA/全量权重需要推给 vLLM 推理引擎（rollout 引擎），且不能重启引擎。文件头 docstring（L9-58）给出了清晰的**两层架构**说明：

1. **RPC 层（协调）**：Ray remote 调用告诉 vLLM worker"准备收权重"；
2. **Collective 层（数据）**：NCCL broadcast 高带宽 GPU-GPU 传输。

分离的理由（L33-38）：RPC 后端可换（Ray/gRPC/torch.distributed.rpc），collective 层后端无关；各用最优传输。

### 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| （模块 docstring：架构图+流程图） | L9-58 | Trainer rank0 ↔ vLLM workers 的三步协议示意 |
| `VLLMCollectiveTransport` | L121 | vLLM 侧传输实现 |
| — `init_all_workers_group` | L164 | 后台线程初始化自定义 NCCL 组（rank0=trainer，其余=vLLM worker） |
| — `send_weights` | L275 | **核心**：见数据流 |
| — `receive_weights` | L375 | 返回 None——vLLM 原生 API 内部应用 |
| `VLLMWeightSyncScheme` | L405 | WeightSyncScheme 子类：transport/sender/receiver 三工厂（L507/531/535） |
| `VLLMWeightSender` | L544 | 训练侧：register_collector/register_model + 版本号管理 |
| — `update_weights` | L641 | 对接 collector 的权重更新回调 |
| `VLLMWeightReceiver` | L682 | vLLM 侧：init_all_workers_group / apply_weights / poll_and_apply（L765） |
| `get_model_metadata` | L781 | 提取（含 LoRA 合并后）state_dict 的 name/dtype/shape 元数据 |

### 外部连接

- 出边 2 条：`weight_update/weight_sync_schemes.py`（继承）+ `_utils.py`。**完全寄生在 v2 框架上，自身只实现 vLLM 特有的传输**。
- 入边：`weight_update/llm/__init__.py`。运行时依赖 `vllm.distributed.weight_transfer.*`（延迟 import，L286-291）与 `ray`。
- 所属层：`layer:distributed`（分布式与权重同步层）。

### 数据流（send_weights，L275-373）

```
前置校验：rank==0 / NCCL 组已建 / 元数据已设 / vllm_engine 已给（L293-307）
1. 构造 NCCLWeightTransferUpdateInfo（names/dtypes/shapes/packed=True）（L322-334）
2. 让 vLLM 全体 actor sleep(level=0)（释放推理显存，L337-340）
3. Ray RPC: actor.update_weights_native(update_request)——worker 进入接收态（L343-345）
4. NCCLWeightTransferEngine.trainer_send_weights(iterator=(name→cuda tensor)...)（L348-358）
   ——逐张量 broadcast，packed 打包传输
5. ray.get(refs) + torch.cuda.synchronize()（L360-361）
6. **reset_prefix_cache()**（L363-365）：权重变了，前缀缓存全失效——不重置会用旧权重续写！
7. wake_up(tags=["scheduling"]) 恢复调度（L367-371）
```

### 模式与坑

1. **prefix cache 失效**是正确性问题而非优化（注释 L363-365 明示"cached prefixes are stale now"）——自研同步方案最容易漏这一步。
2. **sleep/wake 配对**：sleep level=0 只释放 KV cache 级显存；唤醒只带 scheduling 标签，避免把不必要的状态拉起来。
3. **receive_weights 返回 None**：与基类"receive 返回 TensorDict"协议不同——因为 vLLM 在 collective 内部就完成了参数写入，torchrl 侧无需再 apply。
4. `torch.cuda.set_device(self.device)`（L309）：NCCL 对当前设备敏感，忘了设会在多卡训练器上选错 NIC/组。
5. 版本号机制（`_increment_all_collector_versions` L595）：collector 侧记录权重代数，评测时可确认"这条轨迹用的是第几版策略"。

---

## torchrl/envs/libs/__init__.py

**90 行 | 复杂度 simple | 图谱角色：20+ 第三方环境库包装器的 barrel 入口**。

简讲：该文件是纯聚合导出层——从 22 个子模块（brax/dm_control/envpool/genesis/gym/habitat/isaac_lab/isaacgym/jumanji/libero/meltingpot/mjlab/mujoco_playground/openml/openspiel/pettingzoo/procgen/robohive/safety_gymnasium/smacv2/unity_mlagents/vmas）import `XxxEnv` + `XxxWrapper` 对（L6-40），`__all__` 列 49 个名字（L42-90）。

三个设计要点：

1. **Env/Wrapper 成对导出**：`GymEnv`（直接建）与 `GymWrapper`（包已有 gym env）双入口，批量向量化环境（MultiThreadedEnv=envpool、VmasEnv）与多智能体（PettingZoo/SMACv2/OpenSpiel/Meltingpot）都在同一平面。
2. **import 即失败语义**：这里是无条件 import——装了 torchrl 但没装 brax 就不能 `from torchrl.envs.libs import brax`…实际上该入口 import 需要各库在位；深度防御在各子模块内部（惰性 import 第三方库）。
3. gym 的额外导出（L10-18）：`gym_backend/set_gym_backend`（gym vs gymnasium 切换）、`register_gym_spec_conversion`——gym 生态分裂的官方兼容层。
4. 图谱上出边 22 条（每库一个）、入边 1 条（`envs/__init__.py`），complexity=simple——是典型的稳定门面（facade）。

---

## torchrl/envs/llm/__init__.py

**75 行 | 复杂度 simple | 图谱角色：LLM 环境子包 barrel 入口**。

简讲：聚合导出 LLM 后训练的全部环境侧组件，四组来源（L6-40）：

1. **环境**：`chat.py` 的 `ChatEnv/DatasetChatEnv`（对话环境主类）、`envs.py` 的 `LLMEnv/LLMHashingEnv`（底层引擎抽象）、datasets 的 `GSM8KEnv/MATHEnv/IFEvalEnv/CountdownEnv`（四大基准即环境）；
2. **奖励**：`reward/` 的 `GSM8KRewardParser/MATHRewardParser/CountdownRewardParser/IfEvalScorer`——答案解析打分器；
3. **transforms**（15 个）：`Tokenizer`、`KLComputation/KLRewardTransform/RetrieveKL/RetrieveLogProb`（KL 与 log-prob 注入，对接 GRPOLoss 的 ref_log_probs 键）、`TemplateTransform/AddThinkingPrompt`（提示模板）、`PythonInterpreter/MCPToolTransform/BrowserTransform`（工具调用执行环境）、`DataLoadingPrimer/RayDataLoadingPrimer`（数据集注入）；
4. **libs**：`make_mlgym/MLGymWrapper`（ml-gym 桥接）。

与 grpo.py（第 7 节）的闭环关系：`ChatEnv` 产出 query → vLLM 生成 action → RewardParser 打分写 `("next", reward)` → `MCAdvantage` 组内归一化写 advantage → `GRPOLoss` 训练 → `VLLMWeightSyncScheme` 推权重回 vLLM。`as_nested_tensor/as_padded_tensor` 两个工具函数也在此导出——变长序列的两种张量表示，是整条链路的血液类型。

---

## 收束：三篇纵览下的 torchrl 架构定律

1. **LossModule 协议是最大公约数**：从 DQN 到 GRPO 到 DreamerV3，全部服从"TensorDict 进、loss_* 键出"——Trainer 因此可以对任何算法一视同仁地做 backward/日志/checkpoint。
2. **functional 化贯穿始终**：参数即 TensorDict（可 detach/clone/expand/vmap），目标网络、ensemble、meta-RL 全是它的衍生玩法。
3. **掩码是一等公民**：`("collector","mask")`、`shifted_valid`、attention mask、loss_mask_key auto 发现——从采集 padding 到 LLM token 级屏蔽，同一套 `torch.where` 选择语义。
4. **hook 化编排 + 注册表配置 + Protocol 传输**：Trainer 的 18 挂点、configs 的 Hydra 分组、weight_update 的 Protocol 后端——三种解耦机制同构地出现，是大型 RL 框架应对"算法×部署拓扑"组合爆炸的通用解。

---

## torchrl/collectors/__init__.py（补遗：采集器子包的 API 之门）

**架构角色**：`document/` 层之外的"门面"节点——47 行纯导出文件，是 `from torchrl.collectors import Collector, MultiSyncCollector` 等一切用法的入口，图谱中它 `imports` 全部具体采集器实现模块并被上层用户代码反向依赖。

**导出面（torchrl/collectors/__init__.py:7-47，本地实测）**：

| 类别 | 导出 | 来源模块 |
|---|---|---|
| 基类 | `BaseCollector`, `ProfileConfig` | `_base.py` |
| 主构造 API | `Collector` | `_single.py` |
| 同步并行 | `MultiCollector`, `MultiSyncCollector` | `_multi_base.py` / `_multi_sync.py` |
| 异步系 | `AsyncCollector`, `MultiAsyncCollector`, `AsyncBatchedCollector` | `_single_async.py` / `_multi_async.py` / `_async_batched.py` |
| 评估 | `Evaluator` | `_evaluator.py` |
| 权重同步 | `WeightUpdaterBase` + `Vanilla`/`Ray`/`RemoteModule`/`MultiProcessed` 四实现 | `weight_update.py` |
| 探索 | `RandomPolicy` | 反向借自 `modules/tensordict_module/exploration.py` |

**两个值得注意的信号**（较 deepwiki 2025-12 索引更新的本地演进）：
1. `AsyncBatchedCollector` 与 `Evaluator` 是 `__all__` 中的新面孔——采集器家族仍在横向扩张（异步批量采集、独立评估通道）。
2. 权重更新器（5 个）从采集器包导出而非独立顶层包——**权重同步被定位为"采集的伴生问题"**：多进程 worker 拿到新权重才能继续 on-policy 采集，这与 verl 的 3D-HybridEngine 训推切换是同一问题的两种工业解。
