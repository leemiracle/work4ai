# 04 · 聚合三层基类：`src/torchjd/aggregation/_aggregator_bases.py`

## 1. 角色定位

88 行（wc 实测），定义 aggregation 子系统的三层基类树——`Aggregator` → `WeightedAggregator` → `GramianWeightedAggregator`。全库 16 对"聚合器 + 权重器"孪生结构（`__all__` 43 项中 32 项成对，实测统计）都挂在这棵树上：顶层约定"输入二维矩阵、输出行向量"的契约与校验；中层引入 `Weighting` 委托并定义"权重线性组合行"的通用算法；底层用一行 `<<` 组合把 Gramian 计算内联进权重提取。读懂这 88 行，任何聚合器文件都只剩"数学部分"是新的。图谱视角：fan-in 25（22 条 imports 入边 + 3 条 documents，图谱）——被 `_upgrad.py`、`_mean.py`、`_nash_mtl.py`、`_pcd.py` 等 22 个实现文件集体引用，是 aggregation 子系统事实上的"宪法"。

## 2. 内部结构：类/函数地图

imports 三条（:1-8）：`abc`、`torch`、私有数值 `from torchjd._linalg import compute_gramian, is_matrix`（:5，注意走私有桶拿函数）、公共类型 `from torchjd.linalg import Matrix, PSDMatrix`（:6）、`from ._weighting_bases import Weighting`（:8，唯一下游依赖）。

**第一层 `Aggregator(nn.Module, ABC)`**（:11-45）
- 类 docstring（:12-15）用 LaTeX 写明契约：把 `m×n` 矩阵聚合成 `n` 维行向量；
- `_check_is_matrix` 静态方法（:20-26）：`is_matrix` 不过则抛 `ValueError`，消息内嵌实际 shape（:24-25）；
- 抽象 `forward(self, matrix: Matrix, ) -> Tensor`（:28-30）；
- `__call__` 覆写（:32-39）：先 `Aggregator._check_is_matrix(matrix)`（:38）再 `super().__call__(matrix)`（:39）——把校验钉进调用链，子类无法绕过（也意味着 forward 本体无需重复校验）；
- `__repr__`/`__str__`（:41-45）：默认输出裸类名，供 pytest 参数化 id 与 monitoring 教程展示。

**第二层 `WeightedAggregator(Aggregator)`**（:48-73）
- 构造（:56-58）：持有 `self.weighting: Weighting[Matrix]`；
- `_combine` 静态方法（:60-68）：核心就一行 `vector = weights @ matrix`（:67）——权重行向量左乘矩阵 = 行的线性组合；
- `forward`（:70-73）：`weights = self.weighting(matrix)`（:71）→ `_combine`（:72）——"权重提取"与"组合"两步彻底解耦。

**第三层 `GramianWeightedAggregator(WeightedAggregator)`**（:76-88）
- 构造（:86-88）全文最关键的两行：`super().__init__(gramian_weighting << compute_gramian)`（:87）与 `self.gramian_weighting = gramian_weighting`（:88）。前者把"Gramian 型权重器"经 `<<`（06 篇的 `_compose`）提升为"Matrix 型权重器"，后者保留原引用供属性 setter 透传（如 `UPGrad.pref_vector` 直通 `gramian_weighting.pref_vector`，setter 三行在 `_upgrad.py:85-87`）。

## 3. 外部连接

**22 个 imports 消费者**（图谱）分三类：`WeightedAggregator` 直接子类（`_mean.py`、`_sum.py`、`_constant.py` 等简单加权族）、`GramianWeightedAggregator` 子类（`_upgrad.py`、`_dualproj.py`、`_imtl_g.py`、`_krum.py`、`_mgda.py`、`_pcgrad.py` 等 Gramian 族）、以及 `Aggregator` 直系（`_trimmed_mean.py`、`_graddrop.py`——不走权重范式的特例）。`_config.py`（ConFIG）与 `_nash_mtl.py` 也间接经基类拿类型。

**tested_by**（图谱 4 条）：`tests/unit/aggregation/test_aggregator_bases.py` 等——`_asserts.py` 六大性质断言（结构/非冲突/排列不变/尺度线性/强平稳/非可微，`tests/unit/aggregation/_asserts.py:9`/:22/:36/:61/:84/:102）全部以 `Aggregator` 为参数类型，给整棵树定义了统一的正确性验收标准。**上游**：`from ._weighting_bases import Weighting`（:8）是唯一子包内依赖——基类树与权重器树（06 篇）靠 :87 接驳。**下游消费**：`autojac/_jac_to_grad.py` 的 `_can_skip_jacobian_combination` 用 `isinstance(aggregator, GramianWeightedAggregator)` 做 TypeGuard，决定能否走"免组合 Jacobian"优化路径（09 篇）——基类身份直接变成运行时优化开关。

## 4. 数据流：UPGrad 一行的展开

以 `UPGrad()` 聚合一个 2×3 Jacobian `J`（`tests` 与 docstring 通用例）走读全树：

1. `UPGrad(J)` → `Aggregator.__call__`（:32）→ `:38` 维度校验通过 → `nn.Module.__call__` 触发 hooks → `forward`；
2. MRO 落到 `GramianWeightedAggregator` 继承来的 `WeightedAggregator.forward`（:70）：`self.weighting` 是 :87 组装出的 `_Composition`——其 `fn` 是 `compute_gramian`、其 `weighting` 是 `UPGradWeighting`；
3. `:71` 调 `self.weighting(J)`：`_Composition.forward`（`_weighting_bases.py:56-57`）先 `compute_gramian(J)` 得 `G = JJ^T`（2×2 半正定阵，快速路径 `matrix @ matrix.T`，`_gramian.py:43`），再 `UPGradWeighting.forward(G)`（`_upgrad.py:35-38`）：内层 `MeanWeighting` 提取 `[0.5, 0.5]` 权重铺对角阵 `U`（:36），`QuadprogProjector` 把加权列投影到对偶锥（:37），按列求和（:38）；
4. 回到 `:72` `_combine(J, weights)`：`weights @ J`（:67）——**注意此处乘的是原始 `matrix` 而非 Gramian**，权重来自 Gramian、组合作用于 Jacobian，这正是"Gramian 只是充分统计量"论文论断（arXiv:2406.16232 §6）的代码化身；
5. 返回 3 维行向量，写入下游 `.grad`（09 篇）。

## 5. 设计决策（含批判视角）

- **校验放 `__call__` 而非 `forward`**（:38）：绕过 `__call__` 直接调 `forward` 的库内代码不付校验开销，而用户路径必有校验——同一契约双层强度，聪明但隐晦；
- **继承 `nn.Module`**（:11）而非纯 ABC：换来 forward hook（monitoring.rst 教程实时打印权重）、`.to(device)`、生态互操作三件免费资产；代价是每个聚合器背着 Module 状态机，对纯函数式算法是冗余；
- **`<<` 组合发生在构造期**（:87）而非调用期：组合结构固化在对象图里，调用路径零分支；同时 `:88` 保留 `gramian_weighting` 原引用，让 UPGrad 的属性 setter 能穿透两层到达权重器内部（`_upgrad.py:87` 直接赋 `self.gramian_weighting.pref_vector = value`）——组合性与可配置性兼得；
- 批判视角一：`WeightedAggregator._combine`（:60-68）作为 staticmethod 但从未被子类覆写——16 个加权族聚合器全部共享 `weights @ matrix` 这一行，若某算法需要非线性组合（如 NashMTL 的乘性耦合）只能绕开整棵树自己实现 `Aggregator`——树的"中层"其实只服务线性族，命名却暗示普适；
- 批判视角二：三层树的第三层（:76-88）仅 13 行，却承载了全库最重要的类型区分（Gramian 族 vs Matrix 族），`jac_to_grad` 的优化判定（09 篇）依赖 `isinstance` 挂在这层——基类层级与运行时性能耦合，未来若加"四层"（如块对偶锥）需重估该判定的语义。
- 批判视角三：`__repr__`（:41-42）丢弃了 `weighting` 信息，`UPGrad` 等子类被迫自行覆写 `__repr__`/`__str__`（`_upgrad.py:97`/:103）——基类提供的默认值实际是个"必须覆写"的占位。

## 6. 新人提示

1. 读任何聚合器文件的第一件事：看类声明挂第几层——`WeightedAggregator` 直挂 = 吃 Matrix 的简单加权；`GramianWeightedAggregator` = 数学建立在 Gramian 上（可被 autogram 加速）；`Aggregator` 直挂 = 特例范式。这一眼决定你接下来该看 `forward(matrix)` 还是 `forward(gramian)`。
2. 新增 Gramian 族聚合器的最小路径：写 `XWeighting(_GramianWeighting)`（数学在此）+ `X(GramianWeightedAggregator)`（构造时传入前者），照抄 `_upgrad.py` 的文件结构；`tests/unit/aggregation/_asserts.py` 的六性质断言套上即可获得基础正确性背书。
3. 调试时想看中间权重：给聚合器挂 forward hook（`aggregator.weighting.register_forward_hook(...)`，monitoring.rst 有完整例），因为组合是 nn.Module 嵌套（:87），内层 weighting 的 hook 也能收到 Gramian 输入。
4. 记住 :87 的方向：`<<` 是"右操作数先跑"（06 篇详述），读反了整棵树的数学就全拧了。
