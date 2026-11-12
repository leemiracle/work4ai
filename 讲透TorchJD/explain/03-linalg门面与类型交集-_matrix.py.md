# 03 · linalg 双层门面与类型交集：`linalg/__init__.py` + `_linalg/_matrix.py`

## 1. 角色定位

本篇覆盖一对互为表里的文件：公共门面 `src/torchjd/linalg/__init__.py`（18 行）与私有类型系统 `src/torchjd/_linalg/_matrix.py`（57 行）。前者是用户唯一被允许 import 的线性代数入口——只露 4 个符号；后者回答一个类型工程难题：**Python 类型系统没有交集类型（intersection type）时，如何表达"既是 Matrix 又是 PSDTensor"**。答案是用类继承伪造：`PSDMatrix(PSDTensor, Matrix)`。这套类型是全库数值代码的"语法"——`Aggregator.forward(matrix: Matrix)`、`Weighting[PSDMatrix]` 等签名都建立在其上。图谱视角：`linalg/__init__.py` 是全库 fan-in 之冠——29 条 imports 入边（图谱，另有 1 条 documents），几乎每个聚合器文件都从它取 `Matrix`/`PSDMatrix`；`_matrix.py` 自身 fan-in 4（`_linalg/__init__.py`、`_dual_cone.py`、`_generalized_gramian.py`、`_gramian.py`，图谱）。

## 2. 内部结构

**公共门面 `linalg/__init__.py`**：模块 docstring 定调"utility linear algebra methods as well as types to represent specific structural properties"（:1-4）；`from torchjd._linalg import (...)` 拉 4 符号（:6-11：`DualConeProjector`、`Matrix`、`PSDMatrix`、`QuadprogProjector`）；`__all__` 同 4 项（:13-18）。刻意**不含**任何函数（`compute_gramian` 等留在私有包）——门面只放"类型 + 投影器"这种用户需要做类型标注/注入的构件。

**私有 barrel `_linalg/__init__.py`**：15 项 `__all__`（实测计数）——数值三件套 `compute_gramian`/`normalize`/`regularize`、类型 6 项（`Matrix`/`PSDMatrix`/`PSDTensor`/三个谓词）、高维形状三件套 `flatten`/`reshape`/`movedim`、投影三件套 `DualConeProjector`/`QuadprogProjector`/`projector_or_default`。

**`_matrix.py` 类型层次**：
- `:5-7` 设计宣言注释："we're using classes and inheritance instead of NewType because it's possible to have multiple inheritance but there is no type intersection. However, these classes should never be instantiated"——一句话把方案与禁区说尽。
- `Matrix(Tensor)`（:10）：二维张量。docstring 给出两个标准实例——Jacobian `J` 形状 `[m, n]`、Gramian `G=JJ^T` 形状 `[m, m]`（:14-16）；`:19` note 重申"永不实例化，仅静态检查"。
- `PSDTensor(Tensor)`（:23）：二次型张量——前半维度与反转的后半维度一致（如 `[4,3,3,4]`，:25-27）。
- `PSDMatrix(PSDTensor, Matrix)`（:31）：交集伪造的核心——同时"是"两者（:35-37 再次以 Gramian 为例）。
- 三个 TypeGuard 谓词：`is_matrix`（:43，仅查 `ndim == 2` :44）、`is_psd_tensor`（:47-49，`half_dim = t.ndim // 2` 后用负步长切片 `t.shape[: half_dim - 1 : -1]` 比对对称性）、`is_psd_matrix`（:54，方阵检查 :55）。:50-51 与 :56-57 两处注释明言**不真正检查半正定性**（太贵），责任转嫁给"每个使用该 TypeGuard 的函数的测试"，配套断言函数 `assert_is_psd_tensor`/`assert_is_psd_matrix` 在测试侧。

## 3. 外部连接

**门面的 29 个消费者**（图谱 imports 入边）横跨三族：aggregation 侧 `_sdmgrad.py`、`_upgrad.py`、`_weighting_bases.py`、`_utils/pref_vector.py` 等几乎所有算法模块（取 `Matrix`/`PSDMatrix` 做签名）；`_dual_cone.py` 等私有内核；以及测试组。门面自身出边仅 1 条——`imports -> _linalg/__init__.py`（图谱），双层桶结构一望即知。

**`_matrix.py` 的 4 个消费者**（图谱）全部在 `_linalg` 包内，其中最重要的是 `_gramian.py`：`compute_gramian` 带 4 个 `@overload` 签名（`_gramian.py:9`、:14、:19、:24，实现 :29）——返回类型在 `contracted_dims=-1` 时精确到 `PSDMatrix`（:15）、`1` 时（输入为 `Matrix`）同为 `PSDMatrix`（:20）、一般 int 时宽化为 `PSDTensor`（:25）。这条 overload 链正是类型层次的第一个真实消费者：快速路径 `matrix @ matrix.T`（:43）的返回值因此天然获得 `PSDMatrix` 标注，无需 cast。

文档侧 `docs/source/docs/linalg/index.rst`（图谱 documents 边）以 autodoc 呈现这 4 个公共符号。

## 4. 数据流：一次签名级类型流转

以 UPGrad 主链走读（结合 04/06 篇）：

1. `autojac.jac_to_grad` 把各参数的 `.jac` 摊平拼接成组合 Jacobian——运行时就是普通 `Tensor`，但按约定它**应当**满足 `is_matrix`；
2. 传入 `GramianWeightedAggregator.forward(matrix: Matrix)`（`_aggregator_bases.py:70`）——静态检查器此刻要求实参可静态证明为二维；
3. 基类构造时已组装 `gramian_weighting << compute_gramian`（`_aggregator_bases.py:87`）：`compute_gramian: Matrix -> PSDMatrix`（`_gramian.py:15` 的 overload 分支）与 `Weighting[PSDMatrix]` 经 `_compose` 接驳——**类型系统在此自动验证"Gramian 型权重器只会吃到半正定方阵"**，这是裸 Tensor + 注释方案做不到的；
4. 运行时防线：`Aggregator._check_is_matrix`（`_aggregator_bases.py:21`）在 `__call__` 里真正调 `is_matrix`（:22），维度不符抛 `ValueError`（:23-26）。半正定性则没有运行时检查——`normalize`/`regularize`（`_gramian.py:55`、:72）在数值路径上兜底（对角加 ε 保正定），测试侧 `assert_is_psd_matrix` 负责对拍。

一句话总结这条流：**静态层靠"伪造的交集类型"证明结构、运行时只查最便宜的维度、昂贵的半正定性交给测试**——三层各司其职。

## 5. 设计决策（含批判视角）

- **为何不用 NewType**：`NewType` 每次只能包一层，两个 NewType 无法叠加（`PSDMatrix = NewType(NewType(Tensor), ...)` 不合法），:5-7 的注释直说了这个动机。继承方案让 mypy 把 `PSDMatrix` 同时当作 `Matrix` 与 `PSDTensor` 的子类型，泛型 `Weighting[_T]` 的协变/逆变传播（06 篇）才有地基。
- **公共/私有双包**：`linalg`（4 符号）与 `_linalg`（15 符号）分立，用户面窄、内全面宽。`compute_gramian` 不进公共门面是有意为之——它是库内数值原语，用户算 Gramian 该走 `autogram` 引擎（08 篇）而非自己拼。
- **TypeGuard 只做廉价检查**：`is_psd_tensor` 的对称性检查（:48-49）本身就是 O(1) 的形状元组比较；真正特征值分解被注释（:50-51）显式拒绝。这个"性能借口"把正确性责任推向测试——是一个诚实的权衡，但也意味着**误标类型的 bug 在生产环境不可见**。
- 批判视角一：`Matrix(Tensor)` 在运行时确实存在（可被 `isinstance` 命中且等价于 `isinstance(x, Tensor)`），文档靠"never instantiated"（:19）约束，但没有任何机制阻止用户 `Matrix([[1,2]])` 真的实例化它——继承方案天然带着这个后门，NewType 反而没有（NewType 只在类型层存在）。注释承认了风险，靠约定封印；
- 批判视角二：4 个 overload（`_gramian.py:9-25`）中 `Literal[-1]` 与 `Literal[1]` 分支返回更窄类型，但 `contracted_dims` 的"负数表示保留前缀维度"约定（docstring :33-35）与 numpy 负索引心智模型相近却有微妙差异（-1 不是"最后一维"而是"收缩全部尾维"），新人易踩。

## 6. 新人提示

1. import 纪律：用户代码 `from torchjd.linalg import Matrix, PSDMatrix`；库内代码可 `from torchjd._linalg import compute_gramian`。若发现自己在库外 import `_linalg`，几乎一定是走错了门。
2. 写新聚合器时：签名统一 `forward(self, matrix: Matrix, /)`（Matrix 型）或 `forward(self, gramian: PSDMatrix, /)`（Gramian 型），`/` 位置限定符是全库惯例（强制位置传参，防关键字名漂移）。
3. `is_psd_tensor` 的负步长切片 `t.shape[: half_dim - 1 : -1]`（:49）是"反转维度序"的惯用写法，读不懂时手动展开 `[4,3,3,4]`：`half_dim=2`，`shape[:1:-1]` = `(4,)`，`shape[:2]` = `(4,3)`……比对前后半互为反序。这是本文件唯一需要动笔演算的行。
4. 修改 `_matrix.py` 影响半径极大（门面 29 fan-in 图谱 + 语义变化波及全部聚合器签名），动手前先跑 `uv run ty check`（CI 的 code-quality job 用同一工具）看全库类型回归。
