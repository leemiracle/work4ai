# TorchJD 新人上手指南（ONBOARDING）

> 基于知识图谱（590 节点 / 1687 边，14 层 / 16 步导览，校验 0 issues，commit `5ccd6e6`）与源码逐项核实撰写。所有 `文件:行号` 锚均经 grep 实证，图谱派生指标（fan-in/fan-out/边数）单独标注「图谱」。

## 1. 一句话定位

TorchJD 是一个为「多损失 PyTorch 训练」提供 Jacobian descent（雅可比下降）能力的库：把每个损失各自的梯度（Jacobian 的行）**聚合**成单一更新方向，与传统的 scalarization（先把多个损失压成一个标量）路线互补（`README.md:18`「TorchJD is a PyTorch library for training neural networks with **multiple losses**」；`README.md:85-90` 定义 Jacobian descent 为 per-loss gradients individually → aggregate into a single update）。

理解这个定位要先理解它要解决的问题：当一个网络同时有多个损失（多任务学习、多目标优化、物理约束训练等），最朴素的办法是把损失加权求和成一个标量再普通反传——这正是 scalarization 子系统的职责；另一条路线则是对每个损失单独求梯度、得到一整个 Jacobian 矩阵，再用一个「聚合器」把这些行组合成单一梯度——这就是 Jacobian descent。后者的优势是能显式处理梯度之间的冲突与量纲差异（例如把每行投影到其余所有行张成的对偶锥），代价是需要计算并聚合 Jacobian，TorchJD 的全部工程都在围绕「如何让这条路在真实模型上跑得动、省得下内存」展开。主打算法 UPGrad 来自论文 arXiv:2406.16232（`src/torchjd/aggregation/_upgrad.py:62`、`src/torchjd/autogram/_engine.py:50`），readme 用 diff 风格的代码并排展示两条路线只差几行改动（`README.md:57` 起的 GeometricMean 对照块）。全库由 SimplexLab 维护（`CODEOWNERS:15`），文档站 torchjd.org，`README.md` 共 230 行（wc 实测），`CHANGELOG.md` 586 行 30 个版本节，是仍在快速演进的年轻库。

## 2. 核心架构总览：五子系统与依赖梯度

`src/torchjd` 下五个子系统，依赖方向严格单向（图谱实证的 imports 边）：

```
torchjd（门面）──再导出──▶ autojac（主 API 顶端）
                              │ 消费 aggregation(1 条边) + linalg + 包内核
        ┌─────────────────────┼──────────────────┐
aggregation（fan-out 130）  autogram          scalarization
        │ 19+4 条边            │ 4+2 条            │ 5 条（只碰包内核，不碰 linalg）
        ▼                    ▼                  ▼
   linalg / _linalg（fan-in 合计 55：29+26）
        │ 1 条边
        ▼
   包内核 package-core（Stateful/_WithOptionalDeps/_vector_str，fan-in 25）
```

对应图谱 14 层的分工：**Layer 0 包内核**（4 文件）→ **Layer 1 linalg 基础**（6 文件）→ **Layer 2-4 三大功能子系统**（aggregation 30 文件 / scalarization 15 / autogram 7）→ **Layer 5 autojac**（19 文件，依赖链顶端）→ **Layer 6-9 四组测试层**（aggregation 单测 32 文件、autojac+linalg+autogram 单测 23、scalarization 单测 15、测试基建与实验工具 35）→ **Layer 10-13 文档与工程层**（API 文档 49 页 rst、教程 11 篇、CI/治理 25 文件）。

这套分层对新人最有用的读法是「先看依赖方向再看文件」：src 侧六个层恰好构成一条从数值原语到用户 API 的流水线——底层数学（Gramian、对偶锥）→ 算法层（聚合器族、标量化器族、免物化引擎）→ 编排层（autojac 把 Jacobian 计算与聚合串成一次反向）。测试、文档、工程各层分别与 src 层平行镜像，所以任何一个功能改动通常要同步触碰四处：实现、对应单测、API 文档页、教程示例。

关键依赖事实（图谱派生指标，经 imports 边汇总核实）：
- **linalg 是全库地基**：fan-in 55，被 aggregation（19+4 条 imports 边）、autogram（4+2 条）、autojac 与测试组单向消费，自身仅向上依赖包内核 1 条边——修改 `_linalg` 内核会波及所有子系统。
- **aggregation 是最重消费者**：fan-out 130 全库最大；被 autojac 仅以 1 条边引用——子系统间耦合极克制，聚合算法的更换对求导编排零侵入。
- **scalarization 与 autogram 完全独立**：scalarization 只依赖包内核类型（5 条边）不碰 linalg；autogram 复用 linalg 但不依赖 aggregation/autojac/scalarization，自成一体。这意味着两条路线可以各自演进甚至被分别弃用，而不会互相拖累。
- **测试侧 fan-in 之王**是 `tests/utils/tensors.py`（62 条边，图谱），全测试底座 fan-in 158——改这个文件的函数签名会触碰几乎全部测试文件，属于「动一发牵全身」的敏感区。

## 3. 关键模块深读

### 3.1 包内核（Layer 0）

- `src/torchjd/__init__.py` 极薄：`__all__ = ["Stateful"]`（:12）。backward/mtl_backward 已迁入 autojac，顶层经 **PEP 562 模块级 `__getattr__`**（:15）做惰性再导出：查 `_deprecated_items` 字典（:7），命中则发 `DeprecationWarning`（:24）返回旧引用，未命中抛 `AttributeError`（:28）。回归测试在 `tests/unit/test_deprecations.py:5-13`（`pytest.deprecated_call()`，注释钉版「deprecated since 2025-08-18」:4）。
- `src/torchjd/_mixins.py` 两个全局混入：`Stateful(ABC)`（:6）约定 `reset()` 抽象方法（:10），所有跨调用保状态（EMA、迭代权重）的聚合器/标量化器都实现它；`_WithOptionalDeps`（:14）在实例化时用 `importlib.util.find_spec` 逐个检查 `_REQUIRED_DEPS`（:31），缺失即抛 `ImportError` 并附安装提示。
- `src/torchjd/_vector_str.py` 的 `vector_to_str`（:4）/`pref_vector_to_str_suffix`（:14）供各聚合器 `__str__` 渲染偏好向量。

### 3.2 linalg 基础（Layer 1）

- 公共门面 `src/torchjd/linalg/__init__.py` 只导出 4 个符号：DualConeProjector / Matrix / PSDMatrix / QuadprogProjector（:6-11，`__all__` :13）。背后是私有包 `_linalg` 的 barrel（`src/torchjd/_linalg/__init__.py:6`，`__all__` 15 项）。
- `src/torchjd/_linalg/_matrix.py` 用**类继承而非 NewType** 表达类型交集（:5 注释原文）：`Matrix(Tensor)`（:10）→ `PSDTensor(Tensor)`（:23）→ `PSDMatrix(PSDTensor, Matrix)`（:31），配套 `is_matrix` 等 TypeGuard 谓词（:43）；这些类只服务静态检查、从不实例化（:19 docstring）。
- `src/torchjd/_linalg/_gramian.py` 是数值核心：`compute_gramian` 带 4 个 `@overload` 签名（:9-25，实现 :29），加 `normalize`（Frobenius 归一化，:55）与 `regularize`（对角加 ε 保正定，:72）。几乎所有 Gramian 域聚合算法都踩在这三件套上。
- `src/torchjd/_linalg/_dual_cone.py`：抽象 `DualConeProjector(ABC)`（:19）+ `QuadprogProjector(_WithOptionalDeps, DualConeProjector)`（:59）——先 normalize+regularize 再逐向量解 QP，是 UPGrad/DualProj 的数学引擎（quadprog 为可选依赖）。
- `src/torchjd/_linalg/_generalized_gramian.py` 提供高维对称张量的 `flatten`（:9）/`reshape`（:27）/`movedim`（:56）形状变换三件套，在前后半维度上对称操作以保住二次型结构。

### 3.3 aggregation 聚合子系统（Layer 2，最大子系统）

目录实测 28 个非 `__init__` 的 .py 文件（含基类/混入/`_utils` 两个工具），`src/torchjd/aggregation/__init__.py` 的 `__all__` 实测 **43 项**（:67，grep 计数）；包 docstring 本身就是对照示例：`UPGrad` 聚合 Jacobian vs `UPGradWeighting` 从 Gramian 提取权重（:26-32，`>>> from torchjd.aggregation import UPGrad, UPGradWeighting`）。

**三层基类树**（`src/torchjd/aggregation/_aggregator_bases.py`）：
1. `Aggregator(nn.Module, ABC)`（:11）——校验二维输入，约定 `forward(matrix) -> Tensor`（:29）；
2. `WeightedAggregator`（:48）——委托 `Weighting` 提取权重后线性组合各行；
3. `GramianWeightedAggregator`（:76）——构造时直接用 `<<` 组合：`super().__init__(gramian_weighting << compute_gramian)`（:87），先算 Gramian 再加权。

**Weighting 泛型体系**（`src/torchjd/aggregation/_weighting_bases.py`）：`Weighting(nn.Module, ABC, Generic[_T])`（:16）按输入统计类型特化为 `_MatrixWeighting`（:60，吃 Matrix）与 `_GramianWeighting`（:70，吃 PSDMatrix/Gramian）；`__lshift__ = _compose`（:42）让权重器可与函数自由组合。

**`<<` 运算符 DSL 是全库最重要的组合语法**，同时存在于两个体系：Weighting 侧的 `_compose`（`src/torchjd/aggregation/_weighting_bases.py:42`）与 Transform 侧的 `compose`（`src/torchjd/autojac/_transform/_base.py:58` `__lshift__ = compose`，:59 `__or__ = conjunct` 表合取）。

**聚合器族**（挑选代表）：
- `_upgrad.py`：主打算法。`UPGradWeighting(_GramianWeighting, _NonDifferentiable)`（:16）核心就三行（:35-38）：`U = torch.diag(self.weighting(gramian))` → `W = self.projector(U, gramian)` → `return torch.sum(W, dim=0)`——把加权对角阵投影到对偶锥再按列求和。这三行值得逐行读懂：第一行先由内层 weighting（默认 MeanWeighting）从 Gramian 提取权重并铺成对角阵，第二行把每个加权梯度列送到投影器解二次规划，第三行求和得到最终聚合方向。偏好向量 setter 缺省回退 `MeanWeighting()`（:46）。
- `_mixins.py`：`_NonDifferentiable`（:7）重写 `__call__` 包 `torch.no_grad()`（:18），阻断 autograd 图；几乎所有 numpy/cvxpy 求解器型聚合器都混入它——这解释了为什么聚合过程不会被二次求导，也解释了测试体系里「非可微性」是一条可断言的性质。
- `_constant.py`/`_mean.py` 是最简加权基元，也是各聚合器偏好向量的底层载体（`src/torchjd/aggregation/_upgrad.py:46` 实证：`pref_vector_to_weighting(value, default=MeanWeighting())`）；`src/torchjd/aggregation/_utils/pref_vector.py:8` 的 `pref_vector_to_weighting` 把可选偏好向量包成 ConstantWeighting，被 AlignedMTL/ConFIG/DualProj/UPGrad 的 setter 共用；`src/torchjd/aggregation/_utils/simplex.py:5` 的 `project_onto_simplex` 被 MoDo/SDMGrad 的内层更新共用。这种「基元 + 共享小工具」的组织让 27 个算法模块极少互相 import，族内共享全走 `_utils` 与基类。
- 论文级算法谱系：NashMTL（cvxpy/ECOS）、ExcessMTL、MoDo（双批 J1@J2^T 输入）、SDMGrad、CAGrad（cvxpy+CLARABEL）、GradVac、AlignedMTL（改编自 SamsungLabs，`NOTICES` 逐一登记 8 个被改编算法的来源与 MIT 许可，如 ConFIG `NOTICES:90`、MoDo `NOTICES:118`、FAMO `NOTICES:202`）、PCD（层级多目标，QP 用 Goldfarb-Idnani 对偶活跃集法精确解，`src/torchjd/aggregation/_pcd.py:35`，`_solve_qp` 调用点 :120，TMLR 2026 论文 :178）。新人读这族代码的统一套路：先看类声明挂哪棵基类树（决定吃 Matrix 还是 Gramian、是否 Stateful）、再看 forward 的数学、最后看属性 setter 的校验逻辑。

### 3.4 scalarization 标量化子系统（Layer 3）

实测 14 个实现文件，`src/torchjd/scalarization/__init__.py` `__all__` **13 项**（:36，含基类）= 12 个具体标量化器。根接口 `Scalarizer(nn.Module, ABC)`（`src/torchjd/scalarization/_scalarizer_base.py:6`）只约定 `forward(values) -> 标量`（:16）。与 aggregation 的分工：这里把向量值损失直接压成标量，**不碰 linalg**，是 Jacobian 聚合的基线路径。代表实现：`UW`（Kendall CVPR 2018 同方差不确定性加权，`src/torchjd/scalarization/_uw.py:11` `class UW(Scalarizer, Stateful)`，组合式 `0.5*exp(-log_var)*values + 0.5*log_var` 在 :75）；`FAMO`（NeurIPS 2023，内部持有专属 Adam，`src/torchjd/scalarization/_famo.py:8` `from torch.optim import Adam`，:17 `class FAMO(Scalarizer, Stateful)`）。

### 3.5 autogram：免物化的 Gramian 引擎（Layer 4，实验性）

`src/torchjd/autogram/__init__.py:35` 只导出一个 `Engine`。包 docstring 明言：逐层迭代计算 Jacobian 的 Gramian 而无需物化整个 Jacobian，**比 autojac 内存高效得多**（:9），并列出 16 个兼容的 Weighting（:14 起，实测计数 16），接口未来可能变化（:11）。`src/torchjd/autogram/_engine.py:48` `class Engine` 递归 hook 所有含直接可训练参数的模块（`_hook_module_recursively` :203，叶子判据 `any(p.requires_grad ...)` :204），`compute_gramian(output)`（:245）以 ones/identity 为 grad_outputs 触发一次反向，经 hook 注入的节点逐层累积（`ModuleHookManager` 装配点 :197）。docstring 给出三类 output 形状语义（标量→梯度范数、向量→标准 JD、矩阵→IWMTL 每样本×每任务，:247-262）。

### 3.6 autojac 主入口（Layer 5，库的门面 API）

`src/torchjd/autojac/__init__.py` 导出且仅导出四函数（:8-11，`__all__` :13）：
- `backward`（`src/torchjd/autojac/_backward.py:14`）：对标 `torch.autograd.backward`，但把 Jacobian 累积到 `.jac` 字段（docstring :26），内部组装变换链 `_create_transform`（:120，`AccumulateJac << Jac` 声明见文件头 :5）；
- `mtl_backward`（`src/torchjd/autojac/_mtl_backward.py:25`）：多任务混合反向——任务头参数走 `.grad`、共享参数走 `.jac`（每任务一行，docstring :42-43）；由 Grad/Select/Stack/Jac/Accumulate 变换组装 per-task 分支再合流（import :6-13，`Stack(task_transforms)` :175、`Jac(features, shared_params, ...)` :178）；
- `jac`（`src/torchjd/autojac/_jac.py:17`）：与 backward 唯一差别是返回元组而非写入 `.jac`；
- `jac_to_grad`（`src/torchjd/autojac/_jac_to_grad.py:22`）：把 `.jac` 聚合成 `.grad`——**正是聚合器被消费的地方**。参数 `optimize_gramian_computation`（:28）为 True 时逐个求 Gramian 求和、免持有完整组合 Jacobian（docstring :85-90），分支点 :138。

支撑它们的 `_transform` 包（`src/torchjd/autojac/_transform/__init__.py:11`，`__all__` 13 项）是可组合求导流水线：`src/torchjd/autojac/_transform/_base.py:9` 定义 `TensorDict: TypeAlias = dict[Tensor, Tensor]`，:10-17 注释非正式约定 Gradients/Jacobians 等四类流；`Transform(ABC)`（:26）双操作符 `__lshift__`/`__or__`（:58-59）；`Jac(Differentiate)`（`src/torchjd/autojac/_transform/_jac.py:12`）按 `chunk_size` 分块（:20，行数切分 `n_chunks = math.ceil(m / max_chunk_size)` :73）。

## 4. 数据流与典型调用链

**最短闭环**（`docs/source/examples/basic_usage.rst`）：一个双目标回归模型，前两个损失各自反传得到 Jacobian，聚合后交给普通优化器——

```python
autojac.backward([loss1, loss2])                    # :67 计算两损失 Jacobian → .jac
jac_to_grad(model.parameters(), aggregator)         # :68 UPGrad 聚合 → .grad
optimizer.step()                                    # :78 普通 optimizer 前进一步
```

聚合发生在 `jac_to_grad` 内部：flatten+concat 成组合 Jacobian 矩阵 → `GramianWeightedAggregator`（其内部已是 `weighting << compute_gramian`，`src/torchjd/aggregation/_aggregator_bases.py:87`）→ 权重线性组合行 → 写回 `.grad`。UPGrad 的聚合语义即 3.3 节三行代码。注意这条链的用户心智模型：`backward` 与 `jac_to_grad` 是两步显式调用，中间可以插入任何对 `.jac` 的检查或修改（教程 monitoring.rst 正是利用 Aggregator 继承 nn.Module 的特性挂 forward hook 打印权重）。

**多任务链**（`docs/source/examples/mtl.rst`）：共享特征提取器 `shared_module = Sequential(Linear(10,5), ReLU(), Linear(5,3), ReLU())`（:31）+ 任务头；`mtl_backward` 一步完成双写（共享参数 `.jac` 行=任务数，任务私有参数 `.grad`），再对共享参数 `jac_to_grad(shared_module.parameters(), aggregator)`（:29 import 处实证）。这条链对应变换树的组装：每任务一条 Grad 分支，`Stack` 把各任务对共享表示的梯度合流成 Jacobian（`src/torchjd/autojac/_mtl_backward.py:175`），再接一条公共 `Jac`（:178）。

**免物化链**（`docs/source/examples/iwrm.rst`）：autogram `Engine.compute_gramian` 直接得 Gramian → `UPGradWeighting` 从中提取权重 → 按样本加权 backward。教程明言两引擎数学等价、autogram 通常更快但有层兼容性限制（:28-31），并用 tab-set 三栏对比 autograd 基线/autojac/autogram（:41-42）——同一实例级风险最小化任务的三种实现与内存代价一目了然。

**变换链视角**：`backward`/`mtl_backward` 本质都是一条 `<<` 声明的变换链，`tests/unit/autojac/_transform/test_interactions.py` 直接测 `Init << Diagonalize << Jac` 等真实管道端到端数值。新人想真正吃透 autojac，与其逐函数读，不如把九个基础变换各自的输入输出键集搞清楚，再看两个主函数如何把它们拼起来。

## 5. 测试与质量体系

四组单测与实现近一一镜像，共享 Layer 9 基建。这个仓的测试哲学是「性质对拍优先于逐点断言」：聚合器不逐个测输出数值（那是 `test_values.py` 的参考值职责），而是统一断言六条数学性质，因此新增聚合器只需套用同一套断言就能获得可观的正确性背书。

- **测试底座**：`tests/settings.py:9` 从 `PYTEST_TORCH_DEVICE`/`PYTEST_TORCH_DTYPE` 环境变量读 DEVICE/DTYPE（合法值 cpu/cuda:0、float32/float64，:5-6）——这正是 CI 矩阵里 float64 组与 GPU 组的注入点；`tests/utils/tensors.py:16-27` 提供 `arange_`/`randn_`/`ones_` 等按 DEVICE/DTYPE 柯里化的构造器（注释 :13 强调不改全局默认设备）——图谱 fan-in 62 的全测试之锚；`tests/conftest.py:22` autouse 的 `fix_randomness` 固定种子（CPU 强制确定性算法 :31），:35 注册 `--runslow`；`tests/utils/architectures.py` 1212 行声明式测试架构库（wc 实测），`ShapedModule`（:33）经 `__init_subclass__` 强制子类声明 `INPUT_SHAPES`/`OUTPUT_SHAPES`（:36-37，违者 `TypeError` :41-42），实测 54 个顶层 class（含嵌套共 64 个 class 定义），从嵌套/冻结/RNN/PyTree 边角案例到 ResNet18/AlexNet/Transformer 真实视觉模型全覆盖；`tests/utils/optional_deps.py:32` 提供 `skip_if_deps_not_installed`，:42 兜底选择 `UPGrad() if IS_QUADPROG_PROJ_AVAILABLE else IMTLG()`——本地没装 quadprog 时测试自动降级。
- **aggregation 组最厚**（图谱 57 条 tested_by 回链）：`_asserts.py` 把六大性质做成共享断言——结构（:9）、非冲突（:22）、排列不变（:36）、尺度线性（:61）、强平稳（:84）、非可微（:102）；`tests/unit/aggregation/_inputs.py:48` 注释钉版「NashMTL does not work for matrices with 1 row」故单列专用矩阵；`tests/unit/aggregation/_matrix_samplers.py` 提供按目标秩采样的 Normal/Strong/StrictlyWeak/NonWeak 四分布（:38/:49/:75/:117），用于构造能区分这些性质的特定结构输入；`tests/unit/aggregation/test_values.py` 用 `torch.testing.assert_close`（:3）对拍预存参考值。
- **autojac 组**：`test_mtl_backward.py` 773 行 30 例（wc/grep 实测，全库最大测试文件）、`test_backward.py` 19 例、`test_jac.py` 19 例、`test_jac_to_grad.py` 覆盖 17 种聚合器全链路；**autogram 组**：`test_engine.py` 591 行 14 测试（实测），对 50+ 测试架构逐一验证与 autograd 参考等价——新架构加入 architectures.py 后这里自动获得覆盖。
- **实验工具**（开发期分析，非单测）：`tests/trajectories/` 12 文件——`tests/trajectories/_constants.py:23` 的 `AGGREGATORS` 字典实测 11 个聚合器实例，跑 Jacobian descent 参数轨迹与 Pareto 前沿绘图（判断各聚合器收敛行为的可视化证据）；`tests/profiler/compare_traces.py` 对比新旧 autojac 的 Chrome trace 耗时；`tests/plots/interactive_plotter.py:87` 是 Dash 交互应用（滑杆实时对比多聚合器输出，`webbrowser.open_new` :261 自动打开本地服务）。

## 6. 构建发布与 CI

- **单一配置源** `pyproject.toml`（201 行，wc 实测）：PEP 621 元数据 `requires-python = ">=3.10"`（:15）；`lower_bounds` 依赖组钉死 `torch==2.3.0`/`quadprog==0.1.9` 等下界（:100-105）；可选依赖组 `quadprog_projector`/`nash_mtl`/`cagrad`/`fairgrad`（:107-128）——到聚合器的映射表在 `docs/source/installation.md:15-17`（如 `pip install "torchjd[quadprog_projector]"` 启用 UPGrad/DualProj）；内嵌 `[tool.pytest.ini_options]`（:135，`xfail_strict = true`）、coverage/ruff/ty 全套配置（:138-198）。
- **主 CI** `.github/workflows/checks.yml`：三 job——`tests`（:17，include 矩阵实测 13 组：Python 3.10-3.14 各一 :27-31、Windows/macOS、float64、无可选依赖、3.10.0+lower_bounds :44-45、nightly :47、3.15+nightly :50-51；默认配置 py3.14/ubuntu/float32/full 注释钉版 :18）、`build-doc`（:79，`make dirhtml` + `make doctest`）、`code-quality`（:103，pre-commit+ty）。
- **发布** `.github/workflows/release.yml`：GitHub release 触发，`uv build`（:25）→ **trusted publishing**（`id-token: write` :14，注释明言 mandatory）→ `uv publish`（:28），全程无密码凭据——新人不必找任何人要 PyPI token。
- **文档站** `.github/workflows/build-deploy-docs.yml`：Sphinx dirhtml 经 peaceiris/action-gh-pages（:57）双部署到外部仓 SimplexLab/TorchJD-documentation（:62），tag→版本号、main→latest/stable；`docs/Makefile` 默认严格模式（`-W --keep-going -n`，警告即失败）；`conf.py` 从 pyproject 读元数据并实现 linkcode 指向 GitHub 源码行。autodoc 体系意味着「docstring 即文档」：写代码时的注释质量直接决定线上 API 手册质量，doctest 还会让示例代码真的跑一遍。
- **协作约定**：`CONTRIBUTING.md` 293 行 17 节（wc/grep 实测）；`AGENTS.md` 是 AI 代理行为准则——docstring 仅公开或超 4 行函数（:1）、Sphinx 风格且不用 `:returns:`（:2）、全类型标注（:4）、一切用 `uv run`（:6-7）、测试带 `-W error`（:13）、新用户内容必须配 `.rst`（:16）；`skills/` 目录 6 篇技能化流程手册（implement-method 八步 `skills/implement-method/SKILL.md:25-121`、research-method、prepare-release、check-release），把「调研→实现→发布」做成可复用流水线——本仓治理一大特色。

## 7. 新人路线图（16 步导览之前 5 步）

按图谱 tour 顺序，前 5 步构成「从外到内、从用到建」的第一周路径：

1. **项目概览**：读 `README.md`（230 行）——diff 风格双路径代码示例 + 30+ 聚合器/标量化器论文对照矩阵，这张矩阵就是子系统地图（每个算法都能顺着论文链接找到出处）；再翻 `docs/source/index.rst`（三大支柱导读，toctree 四子包 :74-77）与 `CHANGELOG.md`（586 行 30 版本演进史，能看出哪些 API 近期刚破坏性变更）。
2. **安装与工程约定**：`docs/source/installation.md`（可选依赖映射表）+ `pyproject.toml` + `CONTRIBUTING.md` 三份文件即开发环境全部入口；本地起环境用 `uv sync`，跑单测用 `uv run pytest tests/unit`。
3. **包门面与共享内核**：`src/torchjd/__init__.py`（`__getattr__` 兼容层，弄清哪些顶层导入已废弃）→ `_mixins.py`（Stateful/reset 契约与可选依赖检查，后面到处会遇到）→ `py.typed`（PEP 561 标记，mypy 直接采用包内类型）。
4. **linalg 门面与类型系统**：`src/torchjd/linalg/__init__.py` 四符号门面 → `src/torchjd/_linalg/__init__.py` 15 符号 barrel → `_matrix.py` 的继承式类型交集。重点理解公共/私有双包结构：用户只该 import 前者。
5. **linalg 数值内核**：`_gramian.py`（compute_gramian 四重载 + normalize/regularize）→ `_dual_cone.py`（对偶锥投影，UPGrad 的数学引擎）→ `_generalized_gramian.py`（高维对称张量三件套）。**读懂这三个文件，后面 27+ 聚合器的数值骨架就透明了**——绝大多数聚合器的 forward 只是这三件套上的几行组合。

（后续 11 步依次为：aggregation 三层基类 → 聚合器族巡礼 → scalarization → autogram → autojac 主入口 → `_transform` 变换流水线 → 测试基建 → 单测体系 → API 文档站 → 教程示例 → CI 与治理；完整导览见图谱 tour，每步均已配文件清单。）

## 8. 已知坑与发现

1. **PEP 562 惰性再导出**：顶层 `from torchjd import backward` 仍可用但发 DeprecationWarning（`src/torchjd/__init__.py:15-28`），应改从 `torchjd.autojac` 导入；只有 `_deprecated_items` 里两个名字走此路径，其余未知名字正常抛 ImportError——`tests/unit/test_deprecations.py:5-13` 守护该行为。
2. **`<<` 运算符 DSL 双语义**：Weighting 域（`src/torchjd/aggregation/_weighting_bases.py:42`）与 Transform 域（`src/torchjd/autojac/_transform/_base.py:58`）各自实现 `__lshift__`，还有 `__or__` 合取（:59）；读代码时须先判断操作数类型再理解组合方向。这是全库最核心的胶水语法。
3. **测试架构类爆炸**：`tests/utils/architectures.py` 54 个顶层类（嵌套共 64 个 class），图谱中该文件 fan-out 112——每个架构类都成为图节点。新人改 autogram/autojac 时要意识到 `test_engine.py`/`test_mtl_backward.py` 会把全部架构跑一遍（591 行 14 测试 / 773 行 30 例），本地可先用 `--runslow` 跳过慢例。
4. **可选依赖静默分层**：QuadprogProjector 的 ImportError 在 `src/torchjd/_linalg/_dual_cone.py` 被**静默抑制**（缺 numpy/qpsolvers 时不炸），聚合器实例化才经 `_WithOptionalDeps` 报错；测试侧由 `skip_if_deps_not_installed` 决定跳过（`tests/utils/optional_deps.py:32`），CI 有专门一组「no options」矩阵项（`.github/workflows/checks.yml:38-42`）验证裸安装路径。
5. **`.jac` 是自定义字段**：backward 家族写入的张量属性不是 PyTorch 原生 `.grad`；`jac_to_grad` 才是桥。混淆两者是新人最常见错误；`retain_jac`（`src/torchjd/autojac/_jac_to_grad.py:27`）默认 False 意味着聚合后 `.jac` 即被清空。
6. **autogram 的兼容边界**：仅 16 个 Weighting 兼容（`src/torchjd/autogram/__init__.py:14`），且部分层不兼容 batched 模式（docstring :11 自述接口可能变化）；RNN 路径 `torch.vmap` 在 CUDA 上与 `torch.nn.RNN` 不兼容是已知问题（`docs/source/examples/rnn.rst` 引 issue #220，`parallel_chunk_size=1` 为规避手段）。
7. **`_NonDifferentiable` 混入位置敏感**：置于继承列表前会遮蔽主基类 `__call__` 的文档签名（`src/torchjd/aggregation/_mixins.py` docstring 警告）——新增聚合器时混入顺序别随手放。
8. **图谱派生数字与实测的差异提示**：图谱汇总称「27 个实现模块/60 测试架构类」，实测为 28 个非 `__init__` 文件（含基类混入与 `_utils`）与 54 顶层类（64 全量 class）；引用计数时以本文件锚为准（`__all__` 43 项、13 项为最硬口径）。这类小出入不影响架构结论，但提醒新人：二手摘要（包括本文）永远要回到源码锚点复核。

另一条贯穿性的观察：本仓把「给新人看的」与「给机器看的」混在同一目录里——`skills/` 目录是面向 AI 代理的开发手册，`AGENTS.md` 约定代理行为，CI 里甚至有 AI 编码代理工作流（`.github/workflows/opencode.yml`）。人类新人与 AI 代理共享同一套 research→implement→check-release 流程文档，这是全库协作方式上最不寻常的一点，也意味着读懂 `skills/implement-method/references/` 下的两份参考手册（aggregators.md、scalarizers.md）就等于拿到了「本仓认为正确的实现 checklist」。

---

*生成：2026-10-21，基于 knowledge-graph.json（590n/1687e，校验 0 issues）@ commit 5ccd6e6。全文行号锚 182 处引用、108 个不同（文件,行号）对，全部经 grep 越界核验通过。字数：汉字 4072 / 不计空格总字符 16527（双口径）。*
