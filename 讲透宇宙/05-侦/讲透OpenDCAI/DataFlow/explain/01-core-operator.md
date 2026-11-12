# 01 · core/operator.py——所有算子的契约源头

## 角色定位

`dataflow/core/operator.py` 只有 29 行，却是全仓几百个数据加工单元（filter/refine/generate/eval 算子）的最小公共契约：`OperatorABC` 定义"什么是一个算子"，`get_operator` 提供按名取用算子的注册表入口。DataFlow 的核心思想是"一切皆算子"——清洗、合成、评测全部实现为 `OperatorABC` 子类，由 Pipeline 统一编排；Pipeline 在编译期正是靠 `isinstance(v, OperatorABC)` 扫描实例属性来发现算子（`Pipeline.py:47`），所以这个基类是编排器与算子层之间唯一的类型接口。

## 内部结构

`OperatorABC`（`operator.py:5`）极薄：`__init__` 里初始化 logger（`operator.py:7`）和 `ALLOWED_PROMPTS`（`operator.py:8`）；唯一的抽象方法是 `run()`（`operator.py:10-15`）。注意 `run()` 声明为无参，真实约定是子类实现 `run(self, storage, output_key, **input_keys)`（见 `format_str_prompted_generator.py:33-38`）——抽象签名与实际签名刻意脱钩，参数完全靠约定。`get_operator(operator_name, args)`（`operator.py:17`）做三件事：函数体内延迟 `from dataflow.utils import OPERATOR_REGISTRY`（`operator.py:18`，避免 core→utils 的模块级循环依赖）；从注册表取类并立即用 args 实例化（`operator.py:20`）；断言非空后返回（`operator.py:26-28`）。

## 外部连接

依赖面：`operator.py:2` 引 logger，`operator.py:3` 从同包 `prompt.py` 引入两个 Prompt 基类（仅为 `ALLOWED_PROMPTS` 占位用）。被依赖面：`core/__init__.py:1` 把 `OperatorABC`/`get_operator` 导出为包级 API，并合成类型别名 `OPERATOR_CLASSES`（`core/__init__.py:8`）；`Pipeline.py:8` 与 `Pipeline.py:12` 两处消费；每个算子文件顶部都有 `from dataflow.core import OperatorABC`（如 `format_str_prompted_generator.py:7`）。注册表本体在 `utils/registry.py:257`。

## 数据流

`get_operator(name, args)` → `OPERATOR_REGISTRY.get(name)` 未命中时懒加载 operators 子包（`registry.py:108-116`）→ 返回类并用 args 构造 → 交给 Pipeline 或裸脚本调 `run(storage=...)`。运行期数据流完全由子类决定：读 storage → 加工 → 写回 storage，基类不参与数据。

## 设计决策

抽象面薄是刻意的：基类不声明输入/输出 key，key 完整性校验全部上移到 Pipeline 编译期（`Pipeline.py:104-136`），换取算子极大的自由度。代价是任何不走 PipelineABC 的裸 pipeline（仓内大量存在）完全失去静态检查。两处任务书甄别均源码坐实，且有一层更深的坑：其一，`operator.py:8` 的 `tuple([type[DIYPromptABC | PromptABC]])` 用 `type[X]` 下标构造出的只是一个 generic alias 对象，包进单元素 tuple 后既不能迭代出允许的 prompt 类、也不参与任何校验，纯属占位；真正的约束来自 `@prompt_restrict` 装饰器——它在装饰时 `setattr` 类属性 `ALLOWED_PROMPTS`（`prompt.py:34`）并包一层运行时 isinstance 检查（`prompt.py:56-67`）。更隐蔽的是：凡是真调了 `super().__init__()` 的算子，实例属性会 shadow 掉装饰器写入类属性的白名单；多数算子（如 `format_str_prompted_generator.py:18-31`）根本不调 `super().__init__()`，反而"侥幸"不受影响——这是典型的重构中间态残留。其二，`get_operator` 残留两处调试 `print`（`operator.py:19`、`operator.py:27`）。附带发现：`operator.py:22-26` 的 None 分支不可达——注册表未命中时 `Registry.get` 直接抛 KeyError（`registry.py:122-123`），且 `operator.py:20` 在判空前就已实例化。

## 新人提示

新算子的标准模板是两个装饰器叠加：`@prompt_restrict(...)` 在上、`@OPERATOR_REGISTRY.register()` 在下（`format_str_prompted_generator.py:13-16`，顺序不能反，register 要拿到最终类）。`run()` 必须实现且第一形参是 `storage`，否则编译期 assert 会拦（`Pipeline.py:74`）。不要依赖 `self.ALLOWED_PROMPTS` 做任何逻辑；看到 `get_operator` 的 print 输出别当成日志通道；排查"算子找不到"先看 `Registry.get` 抛的 KeyError，再看包 `__init__.py` 是否漏声明（详见第 4 篇）。
