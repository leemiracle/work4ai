# 02 · 全局混入双件套：`src/torchjd/_mixins.py`

## 1. 角色定位

37 行（wc 实测）的包内核文件，定义了两个被全库共享的混入类（mixin）：`Stateful` 与 `_WithOptionalDeps`。前者是"跨调用保状态"这一行为的**契约中心**——所有带 EMA、迭代式权重、可学习参数的聚合器/标量化器都以实现 `reset()` 的方式宣告自己有状态；后者是**可选依赖的统一门卫**——把"缺依赖"的报错从调用点推迟到实例化点，并给出可执行的安装提示。它是全库 fan-in 最高的源码文件之一：图谱实测 17 条 imports 入边（另有 3 条 documents 边），被 aggregation 的 9 个文件（`_sdmgrad.py`、`_cr_mogm.py`、`_excess_mtl.py`、`_fairgrad.py`、`_gradvac.py`、`_modo.py`、`_nash_mtl.py`、`_pcd.py`、`_cagrad.py`）、scalarization 的 `_dwa.py`/`_famo.py`、`linalg` 的消费方、`tests/utils/optional_deps.py` 与 `tests/trajectories/optimize.py` 共同引用（图谱）。

## 2. 内部结构：类/函数地图

**`Stateful(ABC)`**（:6-11）
- docstring 一句话："Mixin adding a reset method."（:7）
- 唯一成员：`@abstractmethod def reset(self) -> None`（:9-11），docstring "Resets the internal state."（:11）
- 注意 `__init__` 都没有——纯契约类，不参与 MRO 的构造链。

**`_WithOptionalDeps`**（:14-37）
- 类属性声明（仅类型）：`_REQUIRED_DEPS: list[str]`（:27）、`_INSTALL_HINT: str`（:28）
- `__init__(self, *args, **kwargs)`（:30）：`missing = [name for name in self._REQUIRED_DEPS if find_spec(name) is None]`（:31）逐个用 `importlib.util.find_spec` 探测；非空则 `raise ImportError(f"{self.__class__.__name__} requires {missing} ... {self._INSTALL_HINT}")`（:33-36）；通过则 `super().__init__(*args, **kwargs)`（:37）原样下传。
- docstring 的 `.. warning::`（:22-24）是本文件最重要的一句工程约定：**该混入必须放在继承列表第一位**，否则其 `__init__` 不会先于"用到了可选依赖的基类"运行——这是 Python 协作式 `super()` 链的硬约束。

imports 仅 3 条（:1-3：`abc`、`importlib.util.find_spec`、`typing.Any`），零 torch 依赖——这使它能被任何子系统（包括不依赖 torch 的纯类型层）安全引用。

## 3. 外部连接

图谱给出 17 条 imported_by 边（上文角色定位已列）。按消费方式分两类：

**`Stateful` 的实现者**（提供 `reset()`）：典型如 `class UW(Scalarizer, Stateful)`（`src/torchjd/scalarization/_uw.py:11`，`reset` 在 :77 将 `log_var` 清零）、`_NashMTLWeighting(_WithOptionalDeps, _MatrixWeighting, Stateful, _NonDifferentiable)`（`src/torchjd/aggregation/_nash_mtl.py:24`，四重混入的极端案例）。顶层 `__init__.py:4` 导入它并作为唯一 `__all__` 成员（`src/torchjd/__init__.py:12`）——这是它"全库公共契约"身份的直接体现。

**`_WithOptionalDeps` 的使用者**（全库 4 处，grep 实测）：`QuadprogProjector(_WithOptionalDeps, DualConeProjector)`（`src/torchjd/_linalg/_dual_cone.py:59`，`_REQUIRED_DEPS = ["numpy", "qpsolvers", "quadprog"]` :71）、`CAGradWeighting`（`_cagrad.py:21`）、`FairGradWeighting`（`_fairgrad.py:24`）、`_NashMTLWeighting`（`_nash_mtl.py:24`）。注意 4 处无一例外把本混入放在首位——warning 条款被严格执行。

测试侧无直接单测文件（图谱 tested_by 为 0），其行为由消费者的测试间接覆盖（如 `tests/utils/optional_deps.py` 的降级逻辑，见 11 篇）。

## 4. 数据流：一次"缺依赖实例化"的走读

用户在裸环境（`pip install torchjd`，未装 quadprog）执行 `UPGrad()`：

1. `UPGrad.__init__` → `GramianWeightedAggregator.__init__` → ... 最终构造 `QuadprogProjector`（经 `projector_or_default(None)`，`src/torchjd/_linalg/_dual_cone.py` 导出）；
2. MRO 首位是 `_WithOptionalDeps.__init__`（:30）：`:31` 对 `["numpy", "qpsolvers", "quadprog"]` 逐个 `find_spec`——**只探测可定位性，不真正 import**，避免半加载状态；
3. 假设 `quadprog` 缺失：`:33-36` 抛 `ImportError`，消息含类名、缺失清单与 `_INSTALL_HINT`（:72 的 `pip install "torchjd[quadprog_projector]"`）——用户拿到的是一行可复制粘贴的修复命令，而非裸 `ModuleNotFoundError` 堆栈；
4. 依赖齐全时：`:37` `super().__init__(*args, **kwargs)` 把参数原封传给 `DualConeProjector.__init__`，混入对正常路径零侵入。

对照路线：若用户直接 `from torchjd.linalg import QuadprogProjector`，`_dual_cone.py` 顶部的 try-import 会**静默抑制** ImportError（ONBOARDING 坑 #4），直到实例化才由本混入兜底报错——两层配合把"导入时静默、实例化时明确"的体验固定下来。

## 5. 设计决策（含批判视角）

- **报错时机选在实例化而非 import**：库作者的核心权衡——`import torchjd` 必须永远成功（否则未用聚合器的用户被无关依赖拖死）；把失败推迟到"真正用到该算法"的瞬间，错误半径最小。
- **`find_spec` 而非 `importlib.import_module`**：探测不执行模块顶层代码，即使目标包损坏也不会在探测阶段产生副作用；代价是无法发现"包存在但版本不兼容"，这类错误仍会漏到真实调用点。
- **`Stateful` 是 ABC 而非 Protocol**：强制显式继承（ nominal typing）。好处是 `isinstance(x, Stateful)` 判断可靠、IDE 能沿继承树导航；代价是鸭子类型的外部实现（用户自定义聚合器写了个 `reset` 但没继承）不被识别——对本库"聚合器族全在库内"的现状来说，这个取舍合理。
- 批判视角一：`_WithOptionalDeps.__init__` 每次实例化都跑一遍 `find_spec`（:31），`find_spec` 涉及文件系统 stat，热循环里反复实例化聚合器时有可观开销——库的现状是"聚合器构造一次、循环外"，问题被使用模式掩盖；
- 批判视角二：`Stateful` 未定义 `__init__`、也不显式参与 `super()` 链，多混入时 MRO 顺序正确与否完全靠人肉遵守（本库未提供检测工具），:22-24 的 warning 是文档性约定而非运行时保障——这是 Python 多继承混入的通病，本仓用 lint 惯例（继承列表顺序在 code review 中人工把关）而非机制解决。

## 6. 新人提示

1. 写任何"内部状态跨调用存活"的聚合器/标量化器：继承 `Stateful` 并实现 `reset()`；`tests/trajectories/optimize.py` 这类长循环工具会在 episode 边界调用 reset，缺失实现会在运行时以 ABC 抽象方法错误暴露。
2. 新增依赖第三方求解器的算法：照抄 `_cagrad.py:21` 的四件套——首位 `_WithOptionalDeps`，声明 `_REQUIRED_DEPS`/`_INSTALL_HINT` 两个类属性（普通赋值，不是 :27-28 的裸标注），并在 `pyproject.toml` 加对应 optional-dependencies 组（`docs/source/installation.md:15-17` 有映射表）。
3. 读到继承列表里混入顺序与文档不符的代码要警惕：`_NonDifferentiable`（aggregation/_mixins.py:7）也有"位置敏感"警告（置于主基类前会遮蔽 `__call__` 文档签名），两个混入同时出现时约定顺序是 `_WithOptionalDeps` → 主基类 → `Stateful` → `_NonDifferentiable`。
4. 本文件与 `py.typed`、`_vector_str.py` 同属 Layer 0；改这里的签名等于触碰全库 17+ 文件（图谱），需同步跑 `uv run pytest tests/unit`（AGENTS.md:6-7 一切经 `uv run`）。
