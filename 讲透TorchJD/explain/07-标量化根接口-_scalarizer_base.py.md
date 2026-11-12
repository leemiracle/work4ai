# 07 · 标量化根接口：`src/torchjd/scalarization/_scalarizer_base.py`

## 1. 角色定位

31 行（wc 实测），全库最小的子系统根：`Scalarizer(nn.Module, ABC)` 只约定一件事——`forward(values) -> 标量`。它是 Jacobian descent 路线的**对照组基线**：aggregation 先分头求梯度再聚合（`Aggregator.forward(matrix)`），scalarization 先把损失向量压成一个标量再普通 `backward`——包 docstring 明言这是"simple baseline against which Aggregators are compared"（`scalarization/__init__.py:2-5`）。理解本文件的关键不在代码量（三分钟读完），而在它划出的**架构红线**：scalarization 子系统被刻意设计为不依赖 linalg、不依赖 aggregation——图谱实测其全部实现文件的 imports 只指向包内核（`_mixins.py`）与本文件，5 条边（图谱），是五大子系统中依赖最少、最可整体弃用的一个。

## 2. 内部结构：类/函数地图

全文一个类：

| 行号 | 成分 | 内容 |
|---|---|---|
| :1-3 | imports | `abc`、`torch`（`Tensor, nn`）——注意**无任何 torchjd 内部依赖** |
| :6 | `class Scalarizer(nn.Module, ABC):` | 根接口 |
| :12-13 | `__init__` | 仅 `super().__init__()`（形式上存在，为子类多继承 MRO 服务） |
| :15-17 | 抽象 `forward(self, values: Tensor, /) -> Tensor` | docstring："Computes the scalarization from input tensor." |
| :19-25 | `__call__` | 薄壳直落 `super().__call__`；docstring（:23）强调 "May be of any shape"——与 Aggregator 的二维硬约束（`_aggregator_bases.py:22`）刻意相反 |
| :27-31 | `__repr__`/`__str__` | 裸类名，与 `Aggregator` 同款（`_aggregator_bases.py:41-45`），供 pytest 参数化 id |

子系统的公共清单：`scalarization/__init__.py` 的 `__all__` 13 项（:36 起，实测计数）= 基类 `Scalarizer` + 12 个具体标量化器（`Constant`/`COSMOS`/`DWA`/`FAMO`/`GeometricMean`/`IMTLL`/`Mean`/`PBI`/`Random`/`STCH`/`Sum`/`UW`，import 块 :22-34）。目录 14 个非 `__init__` 实现 .py 文件（实测，含 `_utils.py`）。注意与 aggregation 的镜像差异：**没有 "XWeighting" 孪生**——标量化输出标量天然可微，没有"从 Gramian 提权重"的需求面，autogram 引擎与它无关。

## 3. 外部连接

图谱 fan-in 15：13 条 imports 入边 = barrel（:14）+ 全部 12 个实现文件（`_constant.py`、`_cosmos.py`、`_dwa.py`、`_famo.py`、`_geometric_mean.py`、`_imtl_l.py`、`_mean.py`、`_pbi.py`、`_random.py`、`_stch.py`、`_sum.py`、`_uw.py`），另有 2 条 documents 边（API 文档站 `docs/source/docs/scalarization/index.rst`）。**没有 tested_by 直连**（图谱）——测试经由 barrel 或直接 import 实现类（`tests/unit/scalarization/` 下 `_asserts.py`、`test_values.py`、`_inputs.py` 与 12 个 `test_*.py`，从 `tests/utils/tensors.py` 拿张量构造器，11 篇）。

**继承侧的两种挂法**（实现族的两个范式）：
- 无状态：`class Mean(Scalarizer)`（`scalarization/_mean.py:6`）——纯函数式；
- 有状态：`class UW(Scalarizer, Stateful)`（`_uw.py:11`）、`class FAMO(Scalarizer, Stateful)`（`_famo.py:17`）——带可学习参数或内部优化器，必须混入 02 篇的 `Stateful` 并实现 `reset()`。`UW.reset` 把 `log_var` 清零（`_uw.py:77-78`），`FAMO` 内部还持有专属 Adam（`_famo.py:8` `from torch.optim import Adam`）——"Scalarizer 本身是个小模型"是这条支线的常态。

## 4. 数据流：与 aggregation 路线的分岔走读

同一个双任务训练循环，两条路线的对照（basic_usage.rst 的镜像）：

**scalarization 路线**：
1. 前向得损失向量 `losses`（形状 `[m]`）；
2. `loss = scalarizer(losses)`——`Scalarizer.__call__`（:19）触发 forward。以 `UW` 为例：`(0.5 * torch.exp(-self.log_var) * values + 0.5 * self.log_var).sum()`（`_uw.py:75`），可学习的 `log_var = nn.Parameter(torch.zeros(shape))`（:67）随训练下降不确定性大的任务的权重；
3. `loss.backward()`——**一次标准反传**，autograd 顺着标量化操作的图回传，`.grad` 直接就位；
4. `optimizer.step()`（优化器参数表需含 `scalarizer.parameters()`，`_uw.py` docstring 示例 :49 明示）。

**aggregation 路线**（对照）：`autojac.backward(losses)` 先把 `losses` 的 Jacobian 算进 `.jac`（每损失一行，09 篇），再 `jac_to_grad(params, aggregator)` 聚合——多花一次全图求导，换取"聚合器看得见整幅梯度几何"（冲突、夹角、量纲）。

分岔点正是本文件的 `forward` 签名：输入是**损失值**（values，:23 任意形状）而非梯度矩阵（matrix，二维硬约束）——两个根接口用输入类型把两条哲学焊死在类型层。

## 5. 设计决策（含批判视角）

- **31 行的克制**：不加校验、不加组合子、不建两层树——与 `_aggregator_bases.py`（88 行三层）形成鲜明对比。原因：标量化是"压扁"操作，组合空间小（没有"加权器 × 统计量"的二维矩阵可枚举），泛型与 DSL 都无从谈起。**接口面积与组合空间成正比**，这是本文件给库设计者的最佳一课；
- **"any shape" 的宽松契约**（:23）：`Mean` 可吃 `[m]` 也可吃 `[batch, m]`（按需 mean），`UW` 则在 forward 里自查形状（`_uw.py:70-74` 抛 ValueError）——校验责任下放给需要它的实现，根接口不预设；
- **继承 nn.Module 的深层理由**：`UW`/`FAMO` 的可学习参数（`log_var` 等）必须能 `.to(device)`、被 optimizer 接管、随 checkpoint 保存——这三件都白拿自 Module。标量化器=微型模型，是这个子系统与 aggregation 最大的气质差异；
- 批判视角一：`forward` 返回类型标注为 `Tensor`（:16-17）而非更窄的"标量 Tensor"，docstring 口头承诺（:7-8 "single scalar value"）没有类型背书——实现若返回向量，mypy 不报、运行时可能悄悄广播，契约靠测试（`tests/unit/scalarization/_asserts.py:8-11` 的 `assert_returns_scalar` 断言 `out.dim() == 0`）兜底；
- 批判视角二：`Scalarizer` 与 `Aggregator` 的对称性是文档性的而非类型性的——两者没有共同祖先（都直接继承 `nn.Module, ABC`），想写"接受聚合器或标量化器"的通用训练循环只能 Union 类型或鸭子类型；库的立场是"这是两条独立路线"，拒绝过早统一，诚实的代价是用户侧胶水代码；
- 批判视角三：`__call__` 覆写（:19-25）与 04 篇 `Aggregator.__call__` 的校验壳形成风格漂移——三个根接口（Aggregator 校验 / Weighting 不校验 / Scalarizer 不校验）三种处理，新人难以归纳"本库的 `__call__` 惯例是什么"。

## 6. 新人提示

1. 先跑通 docstring 里的 `Mean` 三行例（`scalarization/__init__.py:12-19`：`scalarizer(losses)` 得 `tensor(2.)`），再读 `UW`（Kendall CVPR 2018）——前者 10 行代码，后者是"标量化器即模型"的完整样本；
2. 有状态的标量化器（Stateful 混入）三个坑：参数要手动加进 optimizer（`_uw.py` docstring :51）；跨实验要 `reset()`；保存 checkpoint 别漏了它的参数——库不会替你做任何一件；
3. 论文对照阅读顺序建议 `Sum` → `Mean`（加权基线）→ `UW`（学习权重）→ `DWA`/`FAMO`（动态权重）→ `PBI`/`STCH`/`COSMOS`（偏好向量系）——正好是 `__all__` 13 项从简到繁的自然序；
4. 想对比两条路线的实际效果：`tests/trajectories/optimize.py` 与 Pareto 前沿绘图（`plot_distance_to_pf.py`）同时收录聚合器与标量化器，跑出的轨迹图是"scalarization 基线 vs Jacobian descent"最直观的差异证据。
