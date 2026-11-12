# 05 · 43 项聚合器族总装：`src/torchjd/aggregation/__init__.py`

## 1. 角色定位

111 行（wc 实测），aggregation 子系统的 barrel 文件——把 25 个实现模块（imports 出边 25 条，图谱）汇成 `__all__` 43 项（实测计数）的公共清单。它是"论文到代码"的对照总表：43 个导出符号背后是 16 对 Aggregator/Weighting 孪生 + 4 个纯 Aggregator + 3 个纯 Weighting + 4 个基类/接口（实测分解：`__all__` 中 20 项以 Weighting 结尾，23 项非 Weighting 含 3 个基类与 `Weighting` 本身）。更重要的是文件头 :1-39 的包 docstring：它本身是一个**可执行的 doctest**，在同一组数字上同时演示 `UPGrad`（吃 Jacobian）与 `UPGradWeighting`（吃 Gramian）两条路线——这正是全库"autojac 用前者、autogram 用后者"双引擎设计的微缩胶片。图谱视角：fan-out 25 / fan-in 39（36 条 imports 入边，图谱），是测试侧被引用最广的库内入口。

## 2. 内部结构：25 行 import 的族谱

文件三段式：

**doctest 文档**（:1-39）：`:2-4` 定义职责（聚合 Jacobian 进 `.grad`）；`:6-8` 引出 Weighting 的用途（autogram 引擎只需从 Gramian 提权重）；`:10-18` note 说明"大多数聚合器双接口供给、少数只有 Aggregator 接口"；`:26-38` 可运行示例——`jacobian = tensor([[-4.0, 1.0, 1.0], [6.0, 1.0, 1.0]])`（:30），`aggregation = aggregator(jacobian)` 得 `tensor([0.2929, 1.9004, 1.9004])`（:31-33），`weights = weighting(gramian)` 得 `tensor([1.1109, 0.7894])`（:36-38）。CI 的 `make doctest`（`checks.yml:101`）会真跑这段。

**import 块**（:41-65）：25 行按字母序。每行一个模块，孪生的一行取双符号（如 `from ._upgrad import UPGrad, UPGradWeighting` :64）。

**`__all__`**（:67-111）：43 项字典序。

从 import 行可直接读出族谱（本文件行号实证）：
- **孪生 16 对**：`_aligned_mtl`（:42）、`_cagrad`（:43）、`_constant`（:45）、`_dualproj`（:47）、`_excess_mtl`（:48）、`_fairgrad`（:49）、`_gradvac`（:51）、`_imtl_g`（:52）、`_krum`（:53）、`_mean`（:54）、`_mgda`（:55）、`_pcd`（:58）、`_pcgrad`（:59）、`_random`（:60）、`_sum`（:62）、`_upgrad`（:64）；
- **纯 Aggregator（4）**：`ConFIG`（:44）、`GradDrop`（:50）、`NashMTL`（:57）、`TrimmedMean`（:63）——算法本质不吃 Gramian（NashMTL 是乘性博弈、GradDrop 是随机掩码、TrimmedMean 是逐列排序）；
- **纯 Weighting（3）**：`CRMOGMWeighting`（:46）、`MoDoWeighting`（:56）、`SDMGradWeighting`（:61）——依赖双批输入或内层迭代态，无法包装成无状态 Aggregator；
- **基类 4**：`Aggregator`/`GramianWeightedAggregator`/`WeightedAggregator`（:41）与 `Weighting`（:65）。

目录侧配套：28 个非 `__init__` 的 .py 文件（实测，含 `_mixins.py` 与 `_utils/` 两文件），`_utils/` 下 `pref_vector.py:8`（`pref_vector_to_weighting`，偏好向量→ConstantWeighting 的公共工厂）与 `simplex.py:5`（`project_onto_simplex`）承担族内共享。

## 3. 外部连接

**36 个 imports 消费者**（图谱）几乎全是测试：`tests/unit/aggregation/` 全family（`test_aggregator_bases.py`、`test_gradvac.py`、`test_imtl_g.py`、`test_krum.py`、`test_mean.py`、`test_mgda.py`、`test_nash_mtl.py`、`test_pcd.py`、`test_pcgrad.py`、`test_random.py`...）、`tests/utils/forward_backwards.py`、`tests/conftest.py`（pytest_make_parametrize_id 需要 `Aggregator`/`Weighting` 的 str 表示，`tests/conftest.py:72`）、`tests/profiler/` 两个性能脚本与 `tests/trajectories/`。生产侧唯一入口是 `autojac/_jac_to_grad.py` 的类型标注（`Aggregator` 参数）与文档站 `docs/source/docs/aggregation/index.rst`（图谱 documents 边 2 条）。

**tested_by 面**（图谱）：aggregation 子系统共 59 条 tested_by 回链（图谱统计，全库 141 条）——`_asserts.py` 六性质（结构 :9、非冲突 :22、排列不变 :36、尺度线性 :61、强平稳 :84、非可微 :102）+ `test_values.py` 预存参考值对拍 + 各算法专属测试，构成本仓最厚的测试毯。

## 4. 数据流：43 项清单如何被两台引擎消费

**autojac 路线**（吃 Aggregator）：`backward(losses)` 算出 `.jac` → `jac_to_grad(params, UPGrad())`——`jac_to_grad` 的 `aggregator` 参数类型即本包导出的 `Aggregator`，43 项中"Aggregator 形态"的 20 个（16 孪生 + 4 纯）都合法。其中 Gramian 族还会触发 `optimize_gramian_computation=True` 的免组合优化（09 篇）。

**autogram 路线**（吃 Weighting）：`Engine.compute_gramian(losses)` 直接得 Gramian → `weights = weighting(gramian)` → `losses.backward(weights)`（`autogram/_engine.py` docstring 示例 :108-110）。合法参数是"Gramian 型 Weighting"——`src/torchjd/autogram/__init__.py:16` 起的清单实测 15 项（ONBOARDING 记 16，实测差 1；以本数为准），全部来自本包 `__all__` 的 Weighting 侧。

两条路线在 doctest（:26-38）里同屏对拍：同一 `jacobian`，`aggregator(jacobian)` 直接出聚合向量（autojac 语义）；`weighting(jacobian @ jacobian.T)` 出权重向量（autogram 语义）——两者数学等价（`_aggregator_bases.py:87` 的组合链保证），用户按内存/速度需求选边。

## 5. 设计决策（含批判视角）

- **barrel 全量再导出而非按需**：43 项一次到位，`from torchjd.aggregation import *` 即得全家桶。对"算法对照库"这是对的——用户的工作流是"换聚合器跑实验"，全量暴露降低摩擦；代价是 `import torchjd` 链路变重（25 个模块及其 numpy/cvxpy 依赖都会被 import），但可选重依赖（cvxpy 等）在各模块内 try-import 静默降级（02 篇），import 不会炸；
- **孪生命名约定 `X`/`XWeighting`**：机械化可预测，`__all__` 可按后缀过滤；autogram 的兼容清单因此可以自动推导。这是全库最成功的一条命名规范；
- **doctest 即规格**（:26-38）：示例数字精确到小数四位（:33、:38），任何聚合数值实现的回归都会被 `make doctest` 抓住——文档与测试共享同一份真值；
- 批判视角一：43 项清单对新人有压迫感，且无分组——基类（4 项）与具体算法混排，`dir()` 里无法一眼区分"我该实例化的"与"我该继承的"。对比 scikit-learn 的分层包，这里选择了平面，理由是算法间确无天然分组（都吃同一 Matrix），但学习曲线因此全押在文档站；
- 批判视角二：纯 Weighting 三件（:46/:56/:61）不可用于 autojac，但 barrel 并未在类型或命名上警示——用户把 `MoDoWeighting` 传给 `jac_to_grad` 要到运行时类型检查才报错；如果命名是 `MoDo`（无 Aggregator 形态）会更诚实，历史原因是它们未来可能补出 Aggregator 形态；
- 批判视角三：import 行的字母序（:41-65）与族谱无关（孪生/纯种混排），想按"是否 Gramian 族"浏览必须逐个打开文件看基类——本篇第 2 节的族谱表就是为此补的地图。

## 6. 新人提示

1. 把 :26-38 的 doctest 敲进 REPL 跑一遍（两行 `tensor` 定义 + 各三行调用），10 分钟建立"聚合 vs 加权"的肌肉记忆——这是全库最重要的一个区分；
2. 选型起步顺序建议：`Mean`（:91，最简）→ `Sum`（:104）→ `UPGrad`（:107，主打）→ 论文驱动再扩展。README 的算法矩阵给每个名字配了论文链接；
3. 加新聚合器的收尾清单：实现文件 → 此处加 import 行与 `__all__` 两项（若做孪生）→ `docs/source/docs/aggregation/` 加 rst 页（AGENTS.md:16 要求用户可见内容配 rst）→ `NOTICES` 登记来源（若改编第三方，仓内已有 8 个先例）→ 套 `_asserts.py` 六性质 + `test_values.py` 参考值；
4. 判断"这个聚合器能不能配 autogram"：看 `autogram/__init__.py:14` 起的 15 项清单，而不是猜——`GradVacWeighting` 在列但 `NashMTL` 不在，与算法名气无关，只与"是否只依赖 Gramian"有关。
