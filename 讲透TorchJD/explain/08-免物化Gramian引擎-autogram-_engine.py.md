# 08 · 免物化 Gramian 引擎：`src/torchjd/autogram/_engine.py`

## 1. 角色定位

340 行（wc 实测），autogram 子系统唯一公共类 `Engine` 的家——论文 arXiv:2406.16232 Algorithm 3 的工程超集。它解决的问题是：标准 autojac 路线（09 篇）必须把整个 Jacobian `[m, n]`（n=参数量，轻易上百万）物化进内存才能聚合；而大多数聚合器其实只消费 `G=JJ^T`（`[m, m]`，m=损失数）。autogram 递归 hook 模型各层，**逐层累积 Gramian，全程不持有完整 Jacobian**——docstring 明言"often much more memory-efficient, and thus typically faster"（`_engine.py:114-117`）。它是全库工程难度最高的单文件：递归 hook、vmap 批处理、autograd 图边注册、四类状态复位，全挤在一个类里。包门面 `autogram/__init__.py:35` 只导出 `Engine`，docstring（:9-11）标注实验性："its interface may change in future releases"。图谱视角：fan-out 9（7 条 imports），fan-in 6（2 条 imports 入边：`autogram/__init__.py` 与 `tests/unit/autogram/test_engine.py`，图谱）。

## 2. 内部结构：类/函数地图

模块级两张黑名单：`_MODULES_INCOMPATIBLE_WITH_BATCHED`（:20-29，8 种：BatchNorm1d/2d/3d、LazyBatchNorm 三兄弟、SyncBatchNorm、`nn.RNNBase`）、`_TRACK_RUNNING_STATS_MODULE_TYPES`（:31-45，14 种，再含 InstanceNorm 六种）——batched 模式的兼容边界直接编码为类型元组。

**`class Engine:`**（:48）成员地图：

| 行号 | 成员 | 职责 |
|---|---|---|
| :189-201 | `__init__(*modules, batch_dim)` | 装配五大组件并递归挂钩；:194 accumulator（`_gramian_accumulator.py:4`）、:195 `EdgeRegistry`（`_edge_registry.py:6`）、:197 `ModuleHookManager`（`_module_hook_manager.py:24`）、:198 模块→computer 映射、:200-201 入口循环 |
| :203-211 | `_hook_module_recursively` | 判据 `any(p.requires_grad for p in module.parameters(recurse=False))`（:204，**只看直接参数**）；有参挂钩、无参深入子模块 |
| :213-221 | `_make_gramian_computer` | `batch_dim` 非 None → `FunctionalJacobianComputer`（:216，vmap 函数式）；None → `AutogradJacobianComputer`（:218）；统一包进 `JacobianBasedGramianComputerWithCrossTerms`（:219，`_gramian_computer.py:43`） |
| :223-242 | `_check_module_is_compatible` | 两道 ValueError 防线：黑名单类型（:225-233）、`track_running_stats=True`（:234-242），消息都附替代方案 |
| :245-305 | `compute_gramian(output)` | 公共主入口（见 §4） |
| :307-340 | `_compute_square_gramian` | 核心反向（见 §4） |

构造器 docstring（:48-187）长达 140 行，是全库最详尽的"兼容性合同"：batched 五条件（:119-160，含 batch_first、无原地操作、无副作用、随机模块不得有直接参数）、父子调用约定（:162-180 反例）、"直接参数包进子模块"的性能建议（:182-186）。

## 3. 外部连接

**7 条 imports 出边**（图谱）：私有数值 `flatten/movedim/reshape`（:7，高维对称张量形状还原）与 `PSDMatrix`（:8）；子系统内四件——`EdgeRegistry`、`GramianAccumulator`、`GramianComputer`/`JacobianBasedGramianComputerWithCrossTerms`（:12）、`JacobianComputer` 三态（:13-17：抽象 + Functional/Autograd）、`ModuleHookManager`（:18）。**外部消费**：仅 `autogram/__init__.py`（barrel）与 `tests/unit/autogram/test_engine.py`（591 行 14 测试，实测——对 `tests/utils/architectures.py` 的 50+ 架构逐一验证与 autograd 参考等价）。**跨子系统耦合为零**：不 import aggregation/autojac/scalarization（图谱实证）——输出 `PSDMatrix`，由用户接上 15 项兼容 Weighting（`autogram/__init__.py:16-30` 实测计数），权重回灌 `losses.backward(weights)`。

## 4. 数据流：`compute_gramian` 全链走读

以 docstring 示例（:84-112，`batch_dim=0` 的 16 样本损失向量）：

1. **形状归一**（:264-280）：`movedim(batch_dim, -1)`（:266）批维挪尾；非批维摊平为 `[dim, batch_size]`（:277-280）——注释 :281-285 列全四种形状情形；
2. **开启累积相**（:287）：`gramian_accumulation_phase.value = True`——共享 `BoolRef`（`_module_hook_manager.py:80`）告诉所有 hook"这次 forward+backward 为 Gramian 服务"；
3. **触发反向**（:307-340）：`get_leaf_edges({get_gradient_edge(output)})`（:308）从 output 图边做可达性分析，筛出真正需求导的 hook 节点；有非批维时（:318-325）`einsum("ij, ... -> ij...", identity, ones)`（:323）造 vmap 种子并 `vmap(differentiation)`（:325）批量反传，否则 `torch.ones_like(output)` 一次反传（:327-328）；闭包（:310-316）调 `torch.autograd.grad(..., retain_graph=True)`；
4. **hook 逐层截获**：反向流经被挂钩模块时，`Hook.__call__`（`_module_hook_manager.py:103`）经 `AutogramNode`（:150，自定义 `torch.autograd.Function`）把该层局部 Jacobian 的 Gramian 累加进 accumulator——**Jacobian 从未整块存在**，每层算完即弃；
5. **状态硬复位**（:291-297）：`try/finally` 无论成败清全部状态；:330-334 还有"有 forward 无 backward"（如输出被 detach）的显式 ValueError；
6. **形状还原**（:299-303）：批模式下块状 Gramian 经 `reshape`（:300）+`movedim`（:301）还原到用户视角；
7. 用户 `weights = weighting(gramian)`（06 篇）→ `losses.backward(weights)`（:110）落 `.grad`。

## 5. 设计决策（含批判视角）

- **"直接参数"为挂钩粒度**（:204）：hook 只挂在"有直接可训练参数"的模块上（recurse=False），纯容器模块（如 Sequential）被穿透——粒度与计算图的自然分层对齐，而不是与用户的模块组织对齐；
- **batch_dim 双实现**（:215-218）：Functional 路线（`torch.func` 函数式变换 + vmap）吃块对角稀疏性省内存，Autograd 路线是兼容兜底但"not recommended"（:159-160 明言内存暴涨）——把最常见情形（批式训练）做成快路径的取舍非常果断；
- **错误消息即迁移指南**（:226-242）：两条 ValueError 都内嵌修复建议（换 norm 层/关 track_running_stats/降级 batch_dim=None），黑名单元组直接打印进消息——诊断信息自包含；
- 批判视角一：**340 行单类是全库最大的"上帝类"**——五组件协作、双路线分派、形状工程、错误防线全在 Engine，测试只能整体进行（`test_engine.py` 591 行正是代价）；`AutogramNode` 与 Engine 的耦合靠共享 `BoolRef` 翻转，跨文件隐式通信；
- 批判视角二：兼容约束靠**文档+运行时黑名单**双保险，但黑名单只能枚举已知类型（:20-45 共 22 种），自定义层违反"批独立/无副作用"不会被拦——错误以数值错乱（而非异常）静默出现，是最难排查的故障模式；
- 批判视角三：forward 会被跑两遍（:137）——带随机性的层（Dropout 除外）结果不可复现，虽有 :138-149 专门警告与 `dropout=0.0` 处方，约束无法机器强制。

## 6. 新人提示

1. 第一次跑 `Engine` 前对齐三个心智：一次构造多次使用（docstring :101 "Create the engine before the backward pass, and only once"）；`compute_gramian` 后必须自己接 `Weighting` 与 `losses.backward(weights)`（引擎不管最后一步）；输出形状语义看 :254-262（标量→梯度范数平方、向量→标准 JD、矩阵→IWMTL 每样本×每任务）；
2. 遇到报错先查 `:20-45` 两张黑名单再查自定义层；"数值不对但不报错"优先怀疑副作用/原地操作/批不独立（:120-137）；
3. 与 autojac 的等价性验证参考 `tests/unit/autogram/test_engine.py`（对拍 autograd 参考值）与教程 `docs/source/examples/iwrm.rst` 的三栏对比——两引擎数学等价、autogram 更省内存但有层兼容边界；
4. RNN 用户注意：`nn.RNNBase` 在黑名单（:28），CUDA 上 vmap×RNN 已知不兼容（issue #220），`parallel_chunk_size=1` 是 autojac 侧规避（`_backward.py:98-105`），autogram 侧只能改架构。
