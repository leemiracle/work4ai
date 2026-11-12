# 06 · Weighting 泛型与 `<<` 组合子：`src/torchjd/aggregation/_weighting_bases.py`

## 1. 角色定位

77 行（wc 实测），定义与 `Aggregator` 树（04 篇）对偶的 Weighting 体系：`Weighting(nn.Module, ABC, Generic[_T])` 是"从某种统计量提取 m 维权重向量"的泛型根接口，经 `_T` TypeVar 特化为吃 `Matrix` 的 `_MatrixWeighting`（:60）与吃 `PSDMatrix` 的 `_GramianWeighting`（:70）。本文件还实现了全库最重要的胶水语法：`__lshift__ = _compose`（:42）——`weighting << compute_gramian` 一行完成"先变换再加权"，是三层基类树（`_aggregator_bases.py:87`）与 autogram 引擎（08 篇）共同踩踏的接缝。图谱视角：fan-in 25（24 条 imports 入边，图谱）——比 `_aggregator_bases.py`（22）还多 2，因纯 Weighting 三件（CRMOGM/MoDo/SDMGrad）只进这棵树。

## 2. 内部结构：类/函数地图

imports（:1-9）：`abc`、`Callable`、`Generic/TypeVar`、torch、`from torchjd.linalg import Matrix, PSDMatrix`（:9）。三个 TypeVar（:11-13）：`_T = TypeVar("_T", contravariant=True, bound=Tensor)`（:11，**逆变**——本文件的灵魂修饰词）、`_FnInputT`/`_FnOutputT`（:12-13，服务 `_compose` 的多态签名）。

| 行号 | 定义 | 要点 |
|---|---|---|
| :16 | `class Weighting(nn.Module, ABC, Generic[_T])` | 泛型根；docstring（:17-21）："extracting a vector of weights of dimension m from some statistic ... generally its Gramian" |
| :26-28 | 抽象 `forward(self, stat: _T, /) -> Tensor` | 输入类型由特化决定 |
| :30-37 | `__call__` | 薄壳，直落 `super().__call__`（无校验——与 Aggregator :38 的校验对照） |
| :39-40 | `_compose(self, fn: Callable[[_FnInputT], _T]) -> Weighting[_FnInputT]` | 返回 `_Composition(self, fn)` |
| :42 | `__lshift__ = _compose` | DSL 语法糖：`a << fn` ≡ "fn 先跑，a 后跑" |
| :45-57 | `class _Composition(Weighting[_T])` | 私有组合节点：`__init__(self, weighting, fn)`（:51）存两引用（:53-54），`forward` 就一行 `return self.weighting(self.fn(stat))`（:56-57） |
| :60-67 | `class _MatrixWeighting(Weighting[Matrix])` | 特化：吃任意二维矩阵（Mean/Constant/Random 等） |
| :70-77 | `class _GramianWeighting(Weighting[PSDMatrix])` | 特化：吃半正定 Gramian（UPGrad/MGDA/Krum 等，即 autogram 兼容清单的主体） |

两个子类只覆写 `__call__` 换参数名与 docstring（matrix :61-67 / gramian :71-77），为的是让 Sphinx 文档与 IDE 提示按输入类型区分措辞——类型特化本身由继承 `Weighting[Matrix]`/`Weighting[PSDMatrix]` 完成。

## 3. 外部连接

**24 个 imports 消费者**（图谱）几乎覆盖全部算法模块：`_mean.py:8`（`MeanWeighting(_MatrixWeighting)`）、`_constant.py:9`（`ConstantWeighting` 同档位）、`_upgrad.py:16`（`UPGradWeighting(_GramianWeighting, _NonDifferentiable)`）、`_sdmgrad.py`、`_cr_mogm.py`、`_modo.py`、`_utils/pref_vector.py` 等。上游仅 1 条边——`torchjd/linalg/__init__.py`（:9 的类型 import，图谱）。

**与 04 篇基类树的接驳**：`_aggregator_bases.py:8` `from ._weighting_bases import Weighting` + `:56` `weighting: Weighting[Matrix]` + `:87` `gramian_weighting << compute_gramian`——两棵树靠这三行咬合。**与 autogram 的关系**：`Engine.compute_gramian` 产出 `PSDMatrix`，恰好喂给 `_GramianWeighting`——泛型参数在这里完成"类型即兼容性证明"（08 篇）。**tested_by**（图谱 1 条）与 `tests/unit/aggregation/test_aggregator_bases.py` 族的六性质断言共享（非可微性质 :102 直接测 `_NonDifferentiable` 混入行为，该混入虽在 `_mixins.py` 但语义上属于 Weighting 体系的前置知识）。

## 4. 数据流：`<<` 的两次实弹走读

**实例一（构造期）**：`UPGrad()` → `GramianWeightedAggregator.__init__` 执行 `gramian_weighting << compute_gramian`（`_aggregator_bases.py:87`）。`<<` 触发 `_compose(compute_gramian)`（:39）：`self`=`UPGradWeighting`（即 `_T=PSDMatrix`），`fn`=compute_gramian（`Matrix -> PSDMatrix`，即 `_FnInputT=Matrix`），返回静态类型 `Weighting[Matrix]` 的 `_Composition`（:40 标注）——**逆变 TypeVar 在此显灵**：`_compose` 声明 `fn: Callable[[_FnInputT], _T]`，要求 fn 输出恰是 self 吃的类型、fn 输入成为新 Weighting 的输入，mypy 全自动推出，零 cast。

**实例二（调用期）**：`aggregator(jacobian)` → `WeightedAggregator.forward` 调 `self.weighting(matrix)`（`_aggregator_bases.py:71`）→ `_Composition.forward`（:56）：`compute_gramian(jacobian)` 得 Gramian → 权重器吃入 → 返回权重。全程无分支无拷贝，组合开销只是一次属性跳转。

**方向记忆法**：`a << b` = 数学记号 `(a ∘ b)`，b 在右、先执行——与 shell 管道同向。Transform 域有孪生 `__lshift__`（`autojac/_transform/_base.py:58`），语义一致（10 篇）。

## 5. 设计决策（含批判视角）

- **逆变 TypeVar 而非不变**（:11）：使 `Weighting[PSDMatrix]` 可赋给需要 `Weighting[Matrix]` 的位置吗？不——逆变的方向是反的：`Weighting[Matrix]`（能吃任意矩阵）可以充当 `Weighting[PSDMatrix]`（只要求吃半正定阵），反之不成立。这正确编码了"消费者容忍更宽输入即可替换"的里氏替换直觉。若写成不变（默认），`_aggregator_bases.py:87` 的组合将无法通过类型检查，必须满库 `cast`；
- **`_Composition` 存成员而非继承闭包**（:51-54）：组合节点是一等对象，可 `str()`、可挂 hook、可再组合（`(w << f) << g` 嵌套 `_Composition`）；
- **特化用子类而非直接实例化泛型**（:60/:70）：`MeanWeighting` 继承 `_MatrixWeighting` 而非 `Weighting[Matrix]`，多一层"输入档位"中转站——档位类不承载行为（`__call__` 原样转发 :67/:77），只为文档语义与 isinstance 判定；
- 批判视角一：`Weighting.__call__`（:30-37）不做任何输入校验，与 `Aggregator.__call__` 的 `_check_is_matrix`（04 篇 :38）形成不对称——`MeanWeighting(torch.zeros(3))`（一维输入）会静默产出错误形状的权重或深层报错，错误现场远离病因；库靠"Weighting 只被库内组合消费、输入已在 Aggregator 层校验"的假设兜住，但 autogram 用户直接调 `weighting(gramian)`（08 篇示例 :109）时该假设破防；
- 批判视角二：`_MatrixWeighting`/`_GramianWeighting` 是私有名（下划线），用户想写"接受任意 Matrix 型权重器"的签名只能引用公开的 `Weighting[Matrix]` 泛型应用——档位层对用户不可见，文档站需要额外解释这两层的关系，抽象税偏高；
- 批判视角三：`<<` 操作符无类型上的组合封闭性警告——`matrix_weighting << compute_gramian`（方向反了）会被 mypy 拒绝（fn 输出不匹配），但若 fn 是无标注的第三方函数，错误会延迟到运行时形状不匹配。

## 6. 新人提示

1. 先背 :42 与 `_Composition.forward`（:56-57）两处共 4 行——全库所有 `<<` 的行为都在这 4 行里，别处出现的一律是这两个的调用；
2. 写新 Weighting 时选择档位：只依赖 Gramian（`G=JJ^T` 能算出你要的一切）→ 继承 `_GramianWeighting`（自动进 autogram 兼容候选）；需要 Jacobian 本身（如按行范数）→ `_MatrixWeighting`；拿不准就先写 Gramian 版，autogram 的内存优势值得这个约束；
3. 调试组合链：`print(aggregator.weighting)` 会打出嵌套 Module 树（`_Composition` 的 `fn` 成员也在内），或在 `_Composition` 上挂 hook 截获中间 Gramian；
4. 记住逆变方向的自检题："`MeanWeighting`（Matrix 档）能填 `Weighting[PSDMatrix]` 参数位吗？"——能（吃宽给窄，安全），反之 `UPGradWeighting` 填 `Weighting[Matrix]` 位不能。想通这题，:11 的 `contravariant=True` 就真正落地了。
