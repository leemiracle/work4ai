# 09 · Python 门面：openjiuwen 包与算法自动注册

## ① 角色定位

`python/openjiuwen/` 不是「用 Python 重写路由」，而是云侧宿主门面——模块 docstring（`python/openjiuwen/__init__.py:1-8`）把身份钉死：Router 与协议类型由 PyO3 扩展 `_openjiuwen` 重导出；扩展没编译时包**仍然可导入**，`AlgorithmProvider`/`StateProvider` 抽象可独立使用；`route`/`report` 在 Python 侧是 async（蓝图云侧门面形态），同步内核仍在 Rust。这个「缺扩展也能活」的降级是整个注册机制的起点：算法注册横跨 Python 类定义与 Rust 槽位两边，任何一边缺席都不能崩。

三个文件构成门面的骨与肉：`__init__.py`（167 行）重导出+Router 包装，`algorithm_provider.py`（96 行）定义算法插件契约，`discover.py`（74 行）扫描随包算法。外加 `state_provider.py` 对位的 StateProvider 抽象。

## ② 内部结构

**`__init__.py`——可降级的重导出**：`__all__`（`python/openjiuwen/__init__.py:17-40`）列 22 个名字。关键结构是 `TYPE_CHECKING` 分支（`:52-70`）与运行时 try/except（`:74-111`）双轨：类型检查时桩永远「在」（从 `.pyi` 来）；运行时 `_openjiuwen` 导入失败则全部置 None（`:94-111`），并给每个赋值挂 `# type: ignore[misc, assignment]`。`Decision = ModelSelection`（`:114`）复刻 Rust 侧别名。`_require_native`（`:117-123`）在真正用 Router 时才报错，错误信息直接给处方：`run maturin develop`。门面 `Router` 类（`:126-160`）是薄壳：持 `_native`，`from_config`/`from_toml` 转发构造，`route_sync`/`report_sync` 直通内核，`route`/`report` 是 async 包装（`:146-153`，目前只是 `return self.route_sync(...)`——不引入事件循环开销的假 async，为将来云侧真异步留形）。收尾两行（`:163-167`）：`bind_register(_register_algorithm)` 注入登记函数，若扩展在则立即 `install()` 随包算法。

**`algorithm_provider.py`——契约与三类校验**：docstring（`algorithm_provider.py:1-21`）值得整段读，它把「纯函数契约」写成三条边界并按重要性排序：1) 算法**不得调用被选中的目标模型**——决策止于返回 selected_model_id，执行是宿主职责（决策与执行分离，不可让步）；2) 算法**可以**自带辅助模型（如小分类器判复杂度）；3) 辅助调用应无状态纯调用——但这条是纪律不是运行时约束，框架管不到开发者模块内部的状态。机制上：模块级 `_register`/`_pending` 两个槽（`:28-29`）；`AlgorithmProvider.__init_subclass__`（`:74-76`）让**类定义本身**触发 `_commit`——子类一旦定义立即注册，无需装饰器或显式调用。`_validate`（`:44-57`）三类校验：未覆写 decide 就 TypeError、name 必须非空字符串且不等于哨兵 "unnamed"、必须无参可构造（配置放类属性，`:53-57` 的错误信息直接给出处方）。`bind_register`（`:32-42`）处理时序问题：若类定义早于扩展就绪，先进 `_pending` 队列，注入 register 时统一补递交（`:38-41`）。`check_purity`（`:86-95`）是辅助验收工具——同输入双调用比对输出，输出不等（依赖 `__eq__`）即断言不纯。`Algorithm = AlgorithmProvider`（`:83`）是旧名兼容。

**`discover.py`——按包扫描不按名导入**：docstring（`discover.py:1-5`）点明解耦目标：算法团队把实现放并列目录（`test_algo`、`test_algo2`），本模块按包扫描，「不按名导入任何一个团队包」。`_host_package`（`:21-25`）用 `__name__.rpartition(".")[0]` 拿宿主包并从 `sys.modules` 取回——不硬编码 "openjiuwen"，改名也不破。`bundled_algorithms`（`:28-51`）：`pkgutil.iter_modules` 遍历一级子包，跳过非包与 `_` 前缀（`:37`），逐个 `importlib.import_module` 且 **ImportError 静默跳过**（`:40-41`，依赖缺额的算法包不拖垮整个门面），再 `walk_packages` 下钻一级（`:46-50`）。`_collect`（`:59-73`）扫模块命名空间里的 AlgorithmProvider 子类，按 `name` 去重（`:70-72`）——同名后定义者输给先到者。`install`（`:54-56`）的返回值是 `[cls.name ...]`，仅靠「导入即注册」的副作用生效。

## ③ 外部连接

- 向下：`from ._openjiuwen import ...`（`python/openjiuwen/__init__.py:75-93`）——依赖 08 篇的 PyO3 扩展与手写 `.pyi` 桩。
- 向算法生态：`discover.py` 的扫描把 `test_algo/cost_aware.py`、`test_algo2/last_available.py` 等随包示例算法自动挂进 Rust 槽位；第三方宿主自建包同理，只要子类了 `AlgorithmProvider` 且随 `import openjiuwen` 被扫到。
- 向 x-router：`x_router/algorithm.py:6-8` 明说注册发生在类定义时——`import openjiuwen` 触发 discover 扫到 x_router 子包，`XRouter` 类定义即占住算法槽名，宿主 profile 写 `algorithm = "x-router"` 就能被 Rust registry 解析。
- 向测试：`pyproject.toml:28-29` 的 `pythonpath = ["python"]` + `tests/conftest.py:7-8` 让 pytest 直接吃源码树。

## ④ 数据流

冷启动序：`import openjiuwen` → 重导出（扩展在则拿真身，不在则置 None）→ `bind_register`（`python/openjiuwen/__init__.py:163`）注入 `_register_algorithm` → 扩展在则 `discover.install()`（`:165-167`）→ 逐子包 import → 各算法类定义触发 `__init_subclass__` → `_commit` → `_validate`（无参实例化试跑）→ `_register(instance)`（Rust `adapter.rs:67-93` 的 register_algorithm）→ 存入 Rust 侧进程级 HashMap。此后 `Router.from_config` 里 `adapter::lookup(&profile.algorithm)`（08 篇 `lib.rs:100-102`）优先命中这个表——Python 算法与 Rust 内置算法在 registry 眼里同权。宿主请求期：async `route` → `route_sync` → PyO3 直通，不经过任何门面逻辑。

## ⑤ 设计决策与权衡

1. **`__init_subclass__` 注册 vs 装饰器/入口点**：零样板、零遗忘风险（定义即注册），代价是「import 即副作用」——仅被 import 就占槽位，测试里定义假算法类会真污染进程级槽（好在槽按 name 覆盖，测试用独立名字即可）。
2. **`_pending` 队列解时序耦合**（`algorithm_provider.py:38-41`）：算法模块可以在扩展构建前被导入（如纯 Python 单测），队列保证扩展后到也能补登记——这让「扩展未构建仍可开发算法」成为真路径而非口号。
3. **ImportError 静默跳过（`discover.py:40-41`）**：可用性优先于诊断——缺 torch 的算法包不该让门面崩。代价是拼错包名无人报错，需靠槽位清单（`install()` 返回值）做人工核对。
4. **假 async（`python/openjiuwen/__init__.py:146-147`）**：现阶段 async 方法体是同步直返，不碰事件循环。为云侧蓝图预留调用形态一致性，避免将来全量改签名；但宿主别指望它让出控制权。
5. **重导出而非重建类型**：门面不复刻任何数据类，`Feedback`/`Message` 等直接用扩展里的 Py 类——一份 `.pyi` 服务两个世界，杜绝两套类型漂移。

## ⑥ 新人提示与坑

- **扩展缺失的报错点很晚**：`import openjiuwen` 永远成功，直到 `Router.from_config` 才 `_require_native` 报错（`python/openjiuwen/__init__.py:117-123`）。诊断先查 `openjiuwen._openjiuwen` 能否单独 import。
- **算法类必须有稳定 name 且无参可构造**：`name = "unnamed"` 或缺省会被拒（`algorithm_provider.py:47-49`）；构造参数放类属性（`:53-57`），这是与 Rust 槽「字符串键+可复现实例」对齐的硬约束。
- **`Algorithm` 是旧名**（`:83`）：新代码一律 `AlgorithmProvider`，读老示例时注意两者同物。
- **同名算法先到先得**：`_collect` 的 `seen` 集合（`discover.py:70-72`）意味着扫描顺序（pkgutil 字母序）决定赢家，别定义与随包算法重名的类。
- **`check_purity` 不是担保**：双调用比对（`algorithm_provider.py:86-95`）只能抓最显式的非纯（随机、时钟），跨请求状态它看不见——契约第 3 条最终靠自觉与评审。
