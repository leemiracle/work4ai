# 01 · pina/__init__.py —— 37 行的门面：PINA 公共 API 契约本身

## 1. 角色定位

`pina/__init__.py` 是整个库的根 barrel（门面）：全文件仅 37 行，不做任何计算，只做两件事——把五个核心符号 `LabelTensor / Trainer / Condition / DataModule / Graph` 聚合导出（pina/__init__.py:7-13），以及为 v0.2 旧名 `PinaDataModule` 提供弃用警告映射（pina/__init__.py:24）。知识图谱统计它的 imports 入边达 98 条——即全仓 126 个测试文件与 24 个 tutorial 几乎全部经 `import pina` 进入库；若计入 contains/tested_by 等全部边类型，fan-in 611 为全仓最高（ONBOARDING 速查口径）。这组数字说明：**门面就是公共 API 契约本身**——它导出什么，用户的 `from pina import X` 就能用什么；它不导出的，就得走子桶路径。理解 PINA 的第一把钥匙是"门面只转发、不做实现"：在 `pina/` 顶层看到的任何类，真正代码都在 `pina/_src/` 里。

## 2. 内部结构

文件结构三段式，无类、无逻辑分支（除 `__getattr__`）：

| 行号 | 成员 | 说明 |
|---|---|---|
| pina/__init__.py:7-13 | `__all__` | 五符号白名单：`LabelTensor`、`Trainer`、`Condition`、`DataModule`、`Graph` |
| pina/__init__.py:15-19 | 五行 `from pina._src...import` | 分别来自 core 三件（label_tensor/graph/trainer）+ condition + data 子系统 |
| pina/__init__.py:24 | `_DEPRECATED_IMPORTS` | 单条映射 `{"PinaDataModule": "DataModule"}` |
| pina/__init__.py:27-37 | `__getattr__` | PEP 562 模块级钩子：命中弃用表则发 `DeprecationWarning`（pina/__init__.py:30-35）并返回 `globals()` 里的新符号（pina/__init__.py:37） |

配套的三个子桶文件共同构成"桶层"：`pina/solver/__init__.py` 导出 16 个求解器类（pina/solver/__init__.py:3-20）；`pina/model/__init__.py` 导出 18 个模型符号（pina/model/__init__.py:3-22），其中 `DeepONet, MIONet` 一行双导出（pina/model/__init__.py:26）；`pina/condition/__init__.py` 导出 9 个条件符号（pina/condition/__init__.py:9-19）。根桶与子桶是"精选 vs 全集"关系：`Condition` 在根桶可用，`DomainEquationCondition` 则要走 `pina.condition`。

## 3. 外部连接

图谱里本文件 imports 出边 5 条，全部指向 `_src` 实现文件：condition.py、graph.py、label_tensor.py、trainer.py、data_module.py——恰好覆盖 core/condition/data 三个子系统。tested_by 出边 1 条指向 `tests/test_package.py`，后者整个文件只有两行：`def test_import():` 加 `import pina`（tests/test_package.py:1-2），验证发行版"可装可导"这个最低契约。另有 depends_on 入边来自 `code_formatter.sh`（CI 格式化范围）。弃用机制上最重的邻居是 `pina/solver/__init__.py`：它的 `_DEPRECATED_IMPORTS` 表 12 条（pina/solver/__init__.py:63-76），最著名的一条是 `"PINN": "PhysicsInformedSingleModelSolver"`（pina/solver/__init__.py:69）——旧教程里满天飞的 `PINN` 类名如今只是一个警告转发。

## 4. 数据流

走读两条真实链路。**新名链**：`from pina import Trainer` → 解释器执行 pina/__init__.py:17 `from pina._src.core.trainer import Trainer` → 触发 `pina._src.core` 包初始化 → 最终落到 `_src/core/trainer.py` 的类定义。**旧名链**：用户脚本写 `pina.solver.PINN(problem, model)` → 属性查找在 solver 桶的 `__all__` 与模块字典落空 → 进入 `__getattr__`（pina/solver/__init__.py:94）→ 命中 `_DEPRECATED_IMPORTS`（pina/solver/__init__.py:69）→ 打印弃用警告并 `return globals()["PhysicsInformedSingleModelSolver"]`（pina/solver/__init__.py:104）→ 训练照常进行。若访问的是已删除名（如 `GAROM`，pina/solver/__init__.py:90），则走 `_REMOVED_IMPORTS` 分支直接 `raise ImportError`（pina/solver/__init__.py:107）——弃用与移除是两张表、两种结局。根桶的 `PinaDataModule` 同理：`__getattr__`（pina/__init__.py:27）发警告后返回 `DataModule`（pina/__init__.py:37）。

## 5. 设计决策

三个决策值得细看。**其一，极简根桶**：只放 5 个符号而非全量 re-export，代价是 `FeedForward`、`PINN` 等高频类必须写 `from pina.model import ...`；收益是 `import pina` 极轻、命名空间干净，且五符号恰好是"数据载体（LabelTensor/Graph）+ 契约（Condition）+ 数据管理（DataModule）+ 训练（Trainer）"的最小概念集——读 `__all__` 就能猜出库的形状。**其二，PEP 562 惰性弃用**：旧名不占模块字典、只在被访问时报警，既不拖慢 import 也保持兼容。**其三，deprecated/removed 双表分层迁移**（pina/solver/__init__.py:63 与 78）：可自动迁移的旧名进弃用表，语义已无处安放的（`PINNInterface` 的逻辑已由 mixin 承接，见其移除说明 pina/solver/__init__.py:83-86）进移除表——这是 API 演进的诚实姿态。批判视角：注释写 "to be removed soon"（pina/__init__.py:21）却无任何版本时间表，弃用名会长期游荡；更实际的坑是**仓内 CLAUDE.md 的示例仍在用 `PINN` 旧名**，新用户照抄会先吃一个 DeprecationWarning——以桶文件 `__all__` 为准才是权威。

## 6. 新人提示

装包名是 `pip install pina-mathlab` 而非 `pina`，别在 PyPI 上找错。看到任何 `pina.X` 的类，第一步 `grep -r "class X" pina/_src/` 下探实现，顶层永远是转发。写新代码一律用新名（`PhysicsInformedSingleModelSolver` 而非 `PINN`），见到 DeprecationWarning 不要屏蔽——它就是你手里教程版本的年代检测器。想知道完整公共面，直接读各子桶 `__all__`（model 18 / solver 16 / condition 9），比读文档快且永不漂移。

*不计空格字符数：3,425；行号锚引用：26 处（全部经 sed/grep 逐条核实）*
