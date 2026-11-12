# 01 · 包门面与 PEP 562 兼容层：`src/torchjd/__init__.py`

## 1. 角色定位

这是整个 TorchJD 包的门面文件——但它是全库最"反门面"的门面：仅 28 行（wc 实测），`__all__` 只有一个名字 `"Stateful"`（`src/torchjd/__init__.py:12`）。真正的用户 API（`backward`/`mtl_backward`/`jac`/`jac_to_grad`）已全部迁入 `torchjd.autojac` 子包；本文件的核心职责只剩一件：用 **PEP 562 模块级 `__getattr__`** 实现一个"带弃用警告的惰性再导出层"，让老代码 `from torchjd import backward` 依然能跑，同时收到明确的 `DeprecationWarning`。它同时是理解本仓 API 演进史的入口——一次从"扁平 API"到"子包 API"的重构在这里留下了全部痕迹。图谱（knowledge-graph.json）将其归入 Layer「包门面与共享内核」，fan-out 7 / fan-in 7（图谱）。

## 2. 内部结构：逐行地图

全文 28 行，无类定义，只有模块级对象与一个函数：

| 行号 | 成员 | 职责 |
|---|---|---|
| :1-2 | `from collections.abc import Callable` / `from warnings import warn as _warn` | 类型标注与警告（下划线别名防泄漏到 `from torchjd import *`） |
| :4 | `from ._mixins import Stateful` | 唯一被"正牌"导出的符号 |
| :5 | `from .autojac import backward as _backward, mtl_backward as _mtl_backward` | **预取**两个已迁移函数，供弃用路径返回 |
| :7-10 | `_deprecated_items: dict[str, tuple[str, Callable]]` | 弃用登记表：名字 → (新家模块名, 函数对象)。目前两项 `backward`(:8)、`mtl_backward`(:9) |
| :12 | `__all__ = ["Stateful"]` | 门面契约：`import *` 只给 Stateful |
| :15-28 | `__getattr__(name)` | PEP 562 钩子（见下） |

`__getattr__` 的三分支：命中 `_deprecated_items`（:20）→ `_warn(..., DeprecationWarning, stacklevel=2)`（:21-26，:25 的 `stacklevel=2` 让警告指向调用方那一行而非本文件）→ 返回旧引用（:27）；未命中 → 抛 `AttributeError(f"module {__name__} has no attribute {name}")`（:28）。注意 docstring（:16-19）把语义写得很清楚："If an attribute is not found in the module's dictionary"——`__getattr__` 只在常规查找失败后才被调用，所以 `Stateful` 等正常属性零开销。

## 3. 外部连接

图谱视角：imports 出边 4 条——`_mixins.py`、`autojac/__init__.py`、`autojac/_backward.py`、`autojac/_mtl_backward.py`（后两条是 :5 显式点到具体文件的深 import，绕过了 barrel）；入边仅 1 条 imports，来自 `tests/unit/test_deprecations.py`（图谱）。这条测试是本文件的唯一守护者：`test_deprecate_imports_from_torchjd`（`tests/unit/test_deprecations.py:5`）用两个 `pytest.deprecated_call()` 上下文（:6、:9）分别验证两个旧名字仍可取到且必发警告，文件头注释钉版弃用起始日「deprecated since 2025-08-18」（:4）。同目录的 `py.typed`（PEP 561 标记文件）与本文件同属 Layer 0 包内核，让 mypy 直接采用包内类型标注。同层的 `_vector_str.py`（`vector_to_str` :4、`pref_vector_to_str_suffix` :14）则不再经门面导出，仅供聚合器渲染字符串。

## 4. 数据流：一次弃用导入的完整走读

老用户代码 `from torchjd import backward`：

1. Python 先查 `torchjd` 模块字典——没有 `backward`（:12 的 `__all__` 已确认）；
2. 触发 PEP 562：解释器调用本模块 `__getattr__("backward")`（:15）；
3. `:20` 命中登记表；`:21-26` 发出 `DeprecationWarning`，消息体直接从登记表取新家名 `` `autojac` ``（:22-23 拼串）；
4. `:27` 返回 :5 预取的 `_backward` 函数对象——**不发生任何延迟 import**，因为 :5 在模块初始化时就已把函数装进字典；
5. 用户拿到与 `torchjd.autojac.backward` 完全同一的函数对象（可用 `is` 判等），警告由 pytest 的 `-W error` 配置（`pyproject.toml` 内嵌 pytest 段）在 CI 里升级为错误，倒逼迁移。

这条流程的关键设计点：弃用项在模块加载时即已 import（:5），`__getattr__` 里没有任何 `import` 语句——惰性的是"查找"而非"加载"，换来警告路径的零异常风险。

## 5. 设计决策（含批判视角）

- **为什么用 PEP 562 而不是直接再导出？** 直接 `from .autojac import backward` 会让老导入静默通过，弃用永不被发现；而模块级 `__getattr__` 是 Python 官方为"动态/条件导出"设计的钩子（需 Python 3.7+，本仓 `requires-python = ">=3.10"` 无压力），在这里被挪用为"弃用哨卡"——教科书级用法。
- **登记表驱动**（:7-10）：新增弃用项只需加一行字典条目，`__getattr__` 逻辑不动。警告消息的新家模块名存在表里而非硬编码在 warn 调用中（:22-23 从 `_deprecated_items[name][0]` 取），单一事实源。
- **`__all__` 收缩到 1 项**：这是激进但干净的选择——IDE 自动补全从源头杜绝新用户走旧路。代价是 `import *` 行为与多数科学计算库（倾向平铺再导出）相反，初见会困惑。
- 批判视角一：`:5` 的深 import（直指 `_backward.py`/`_mtl_backward.py` 而非 `from .autojac import ...` 的模块级引用）让图谱与依赖追踪出现冗余边，虽然运行时等价，但读者可能误以为门面绕过了 barrel 有特殊意图；
- 批判视角二：`__getattr__` 返回类型标注为 `Callable`（:15）掩盖了"可能是任意函数签名"的事实，静态检查器无法对弃用路径做签名校验——弃用层的类型安全是放弃的。这两个代价都可接受，因为该层的预期寿命有限（警告期结束后登记表清空即可删除整个 `__getattr__`）。

## 6. 新人提示

1. 写新代码永远 `from torchjd.autojac import backward`；在本仓测试跑 `pytest -W error`（AGENTS.md:13 约定）时，任何旧式导入会直接炸测试。
2. 想知道"还有哪些顶层名字活着"：看 `__all__`（:12）而不是 `dir(torchjd)`——后者会被 `__getattr__` 的存在与否误导（未触发时 dir 不含弃用名）。
3. 若参与"下一个弃用周期"（比如未来 `jac_to_grad` 移位），照抄 :7-10 的表驱动模式加条目，并在 `tests/unit/test_deprecations.py` 补一个 `deprecated_call` 块。
4. 本文件是"读完整库的最短起点"：顺着 :4 进 `_mixins.py`（02 篇）、顺着 :5 进 `autojac`（09 篇），两条线正好覆盖包内核与主 API。
