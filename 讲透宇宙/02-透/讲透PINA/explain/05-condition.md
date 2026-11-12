# 05 · pina/_src/condition/condition.py —— 训练契约的六路分派门

## ① 角色定位

`Condition` 是问题定义与求解器之间的数据契约：一个 problem 挂多少条件、每个条件是物理残差还是监督数据，都从这里声明。它也是全库最反直觉的类之一——`class Condition`（pina/_src/condition/condition.py:15）没有任何 `__init__` 逻辑，全部魔法在 `__new__`：按传入关键字组合分派到六种具体条件类之一，并返回**具体类的实例**。docstring 明说用户应永远直接实例化 `Condition` 而非具体子类（L77-81 的 note）。损失语义（这个条件怎么进 loss）完全由 solver 侧解释，condition 自己只装载数据与方程——纯数据对象，这让同一份问题定义可以被不同求解器重新解释。

## ② 内部结构

文件只有一个类加两张类级表：

- `_SPECS` 元组（pina/_src/condition/condition.py:107-122）：六行声明式规格，每项为 `(条件类, 必选 kwargs 集合, 可选 kwargs 集合)`——
  - `InputTargetCondition`：`{input, target}`（L108），监督数据对；
  - `InputEquationCondition`：`{input, equation}`（L109），固定配点上算残差；
  - `DomainEquationCondition`：`{domain, equation}`（L110），域上采样施加物理残差，PINN 的核心条件；
  - `DataCondition`：`{input}` + 可选 `conditional_variables`（L111），无监督；
  - `TimeSeriesCondition`：`{input, n_windows, unroll_length}` + 可选 `randomize`（L112-116），滑窗时间序列；
  - `GraphTimeSeriesCondition`：同 TimeSeries 再加可选 `key`（L117-121），图序列版本。
- `available_kwargs`（L125）：由 `_SPECS` 并集推导的全部合法参数名，类级常量。
- `__new__`（L127）：位置参数直接 ValueError（L142-146，报错附上 available_kwargs）；然后顺序遍历 `_SPECS`，`required <= set(kwargs) <= allowed` 双侧子集判断（L155）命中即 `return condition_cls(**kwargs)`（L156）；全部不中则枚举所有合法签名抛 ValueError（L159-167）。

## ③ 外部连接

文件头部 import 六个具体类（pina/_src/condition/condition.py:3-12），具体类各自继承 `BaseCondition`（pina/_src/condition/base_condition.py，153 行）或彼此继承——`GraphTimeSeriesCondition(TimeSeriesCondition)`（pina/_src/condition/graph_time_series_condition.py:13）。图谱 imports 入边 13：base_problem.py + 九个 problem zoo 文件 + 两个桶 `__init__`；出边 6 正对六个具体条件文件（input_target 129 行 / input_equation 136 行 / domain_equation 153 行 / data 133 行 / time_series 247 行 / graph_time_series 147 行）。公共桶 `pina/condition/__init__.py:8-18` 导出 9 个符号（接口、基类、门面加六具体类）。tested_by 值得注意：tests/test_condition/ 下是六个按具体类命名的测试文件，**门面分派逻辑本身没有专门测试**——它的正确性只靠下游测试间接锁定。测试里两种导入并存（tests/test_condition/test_input_target_condition.py:4 直接 import `InputTargetCondition`、:7 经 `from pina import Condition`），恰好演示了用户路径与内部路径的分野。

## ④ 数据流

以 pina/_src/problem/zoo/poisson_problem.py:78 的 `Condition(domain="boundary", equation=FixedValue(0.0))` 为例走分派链：

1. `__new__` 收到 kwargs `{"domain": ..., "equation": ...}`（pina/_src/condition/condition.py:127）；
2. 顺序遍历 `_SPECS`：InputTarget 要求 `{input,target}`，required ⊄ kwargs，跳过；InputEquation 要求 `{input,equation}`，同样跳过；
3. 第三行 DomainEquationCondition 命中：`{domain,equation} <= set(kwargs) <= {domain,equation}`（L155）；
4. 返回 `DomainEquationCondition(**kwargs)`（L156）。该类用 `__fields__ = ["domain", "equation"]`（pina/_src/condition/domain_equation_condition.py:33）装载数据，并持类型白名单：domain 接受 `DomainInterface` 或 str、equation 接受 `BaseEquation`（L33-35）；
5. `BaseProblem.__init__` 回绑 `.problem`/`.name`（pina/_src/problem/base_problem.py:41-42），问题侧收集 domains；
6. 训练期 DataModule 调 `move_discretisation_into_conditions`（pina/_src/data/data_module.py:120）后，该域条件被替换为 input+equation 形态的新条件（pina/_src/problem/base_problem.py:227-238），solver 逐条件取 input 前向、按 equation 算残差、交 weighting 配平。

也就是说：**门面分派发生在问题定义期，一次定型；训练期条件对象还可能被问题层二次替换**，Condition 类对此毫不知情——两个生命周期阶段各管各的。

## ⑤ 设计决策（含批判视角）

- **`__new__` 工厂优于 `__init__` 分派**：返回值是 InputTargetCondition 等具体类实例而非 Condition 实例，`isinstance(cond, Condition)` 为 False。收益是六种条件零耦合独立演化、公共 API 只暴露一个名字；代价是静态类型世界失效（IDE 推断与 mypy 只能看到 Condition），六类用法说明全部压进 docstring（L33-75）。
- **双侧子集判断**（L155）用一行集合代数同时防"缺必选"与"传多余"，零反射；失败路径枚举全部合法签名（L159-167），报错即文档，这是值得抄的 API 设计。
- **顺序敏感的匹配**：第一个命中即返回。当前六行规格互斥，但 `DataCondition` 的 required={input} 是最宽松的一行且排在 TimeSeries 之前——若未来新增"input-only 但语义不同"的条件，插入位置就成了隐式行为开关，而这层顺序约束既无注释也无专门测试锁定，属于隐性脆弱点。
- **纯数据对象**：条件不持 loss 方法，权重配平交给 weighting、聚合交给 solver。好处是同一 InputTargetCondition 能被监督 solver 与 PINN solver 各自解释（半物理训练得以成立）；坏处是"哪类条件配哪个 solver"的兼容矩阵只存在于文档与运行时报错里。
- 时间序列条件把 `n_windows`/`unroll_length` 设为必选（L112-116）——把滑窗超参固化进数据契约，缺省滑窗是常见错误源，这是好的工程决断；代价是调窗必须重建条件对象，无法在 Trainer 层热改。

## ⑥ 新人提示

- 只用关键字参数，传位置参数立刻 ValueError（L142-146）。
- 拿不准签名时故意传错一次：错误消息（L165-166）会打印全部合法签名，比查文档快。
- 六类选型口径：正向解 PDE 用 domain+equation（内部域与边界各建一个条件）；已有固定配点快照用 input+equation；有标签数据用 input+target；无监督数据用 input（可加 conditional_variables）；时间序列必须带 n_windows 与 unroll_length。
- debug 时看实际类型：`type(problem.conditions["D"])` 是 DomainEquationCondition 而非 Condition；训练开始后它还会被 move_discretisation_into_conditions 换成 InputEquationCondition，不要对类型做硬断言。
- 六个 tests/test_condition/ 文件就是六类条件的最小用例集，用法疑问先去那里找。

*自报：不计空格字符 4068；行号锚 34 处（file:line 锚 12 + 同文件 L 式行引用 22），均经 grep 对 commit 60ea474a 核实。*
