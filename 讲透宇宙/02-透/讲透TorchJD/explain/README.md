# TorchJD 精讲系列（explain，12 篇）

> 基于 TorchJD 仓（`/usr-data/data2/repos/pytorch-landscape/repos/TorchJD`，commit `5ccd6e6`）源码与知识图谱（`.understand-anything/knowledge-graph.json`，590 节点/1687 边/14 层/16 步 tour，校验 0 issues）撰写。12 篇覆盖图谱 tour 第 3-12、14-15 步的核心文件：从包门面到聚合器族、从求导流水线到测试底座与文档站。

## 篇目索引

| # | 文件 | 主角 | 一句话 |
|---|---|---|---|
| 01 | [包门面与 PEP 562 兼容层](01-包门面与PEP562兼容层-__init__.py.md) | `src/torchjd/__init__.py` | 28 行门面：`__getattr__` 弃用哨卡 + `__all__` 收缩到 1 项 |
| 02 | [全局混入双件套](02-全局混入双件套-_mixins.py.md) | `src/torchjd/_mixins.py` | `Stateful`（reset 契约）与 `_WithOptionalDeps`（实例化期依赖门卫） |
| 03 | [linalg 门面与类型交集](03-linalg门面与类型交集-_matrix.py.md) | `linalg/__init__.py` + `_linalg/_matrix.py` | 用类继承伪造交集类型（`PSDMatrix(PSDTensor, Matrix)`），全库 fan-in 之冠（29，图谱） |
| 04 | [聚合三层基类](04-聚合三层基类-_aggregator_bases.py.md) | `aggregation/_aggregator_bases.py` | `Aggregator→WeightedAggregator→GramianWeightedAggregator` 树与 :87 的 `<<` 组合 |
| 05 | [43 项聚合器族总装](05-43项聚合器族总装-aggregation-__init__.py.md) | `aggregation/__init__.py` | 16 对孪生 + 4 纯 Aggregator + 3 纯 Weighting 的族谱；doctest 即规格 |
| 06 | [Weighting 泛型与组合子](06-Weighting泛型与组合子-_weighting_bases.py.md) | `aggregation/_weighting_bases.py` | 逆变 TypeVar + `__lshift__ = _compose`，全库最重要胶水语法 |
| 07 | [标量化根接口](07-标量化根接口-_scalarizer_base.py.md) | `scalarization/_scalarizer_base.py` | 31 行对照组基线：values→scalar，不碰 linalg 的独立路线 |
| 08 | [免物化 Gramian 引擎](08-免物化Gramian引擎-autogram-_engine.py.md) | `autogram/_engine.py` | 340 行上帝类：递归 hook + vmap 批处理，逐层累积 Gramian 不物化 Jacobian |
| 09 | [autojac 主入口](09-autojac主入口-backward.py.md) | `autojac/_backward.py` | `backward` 写 `.jac`；全部工作委托 `AccumulateJac << Jac` 变换链 |
| 10 | [可组合求导流水线](10-可组合求导流水线-_transform-_base.py.md) | `autojac/_transform/_base.py` | `TensorDict` 微内核：`<<` 串接、`\|` 合取、`check_keys` 静态推演 |
| 11 | [测试张量工厂](11-测试张量工厂-tests-utils-tensors.py.md) | `tests/utils/tensors.py` | partial 柯里化 DEVICE/DTYPE，fan-in 62（图谱）的全测试之锚 |
| 12 | [文档站构建中枢](12-文档站构建-docs-conf.py.md) | `docs/source/conf.py` | pyproject 单一配置源 + linkcode 行号锚 + 自定义 doctest 指令 |

## 字数与锚点口径（钉版）

- **字数口径**：单篇「不计空格总字符」2500-4800（含代码/表格/路径锚字符；汉字单字计 1）。12 篇实测 3459-4796，合计 54721。
- **锚点口径**：全口径锚（`路径:行号` 反引号式 + 裸 `:行号` 上下文式）共 **636 个**，其中带文件路径的完整锚 127 个。所有行号经脚本对源码逐条核验（越界即 FAIL）；带文件路径的锚另经 grep 内容抽查确认行号处确为所述内容。
- **数字来源双标注**：fan-in/fan-out/边数等图谱派生指标一律标注「图谱」；`__all__` 计数、文件行数、类/函数行号、grep 计数一律为「实测」。两套数字并存时以实测为准。

## 与 ONBOARDING 的勘误差异（本系列新发现）

1. **autogram 兼容 Weighting 数量**：ONBOARDING 记 16，实测 `autogram/__init__.py` bullet 清单为 **15 项**（:16-30，grep 计数）。08/05 篇按 15 表述。
2. ONBOARDING 已钉的「实现模块 28 非 27、顶层 class 54 非 60」在 05/11 篇沿用（实测口径）。
3. 聚合器族分解细化：43 项 = 16 对孪生（32）+ 4 纯 Aggregator（ConFIG/GradDrop/NashMTL/TrimmedMean）+ 3 纯 Weighting（CRMOGM/MoDo/SDMGrad）+ 4 基类/接口（05 篇，`__all__` 实测推导）。

## 阅读路线建议

- **算法线**：04 → 06 → 05（基类树→权重器→族谱），配合 `_upgrad.py` 对照读；
- **引擎线**：09 → 10 → 08（backward→变换流水线→免物化引擎），理解 `.jac` 的生产与两种消费路径；
- **工程线**：01/02/03 → 11 → 12（包内核→测试底座→文档站），适合准备提 PR 的贡献者。
