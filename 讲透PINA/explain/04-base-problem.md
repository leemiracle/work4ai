# 04 · pina/_src/problem/base_problem.py —— 声明式问题抽象的根 BaseProblem

## ① 角色定位

PINA 的核心心智模型是"问题 = 变量 + 域 + 条件"，三者在同一个 Python 类里以属性/方法声明，没有配置文件、没有 DSL。这个抽象的根就是 `BaseProblem`（pina/_src/problem/base_problem.py:19）。先澄清一个命名事实：本仓并不存在 `abstract_problem.py`，问题层的抽象基类文件名是 `base_problem.py`，其上还有一层更薄的 `ProblemInterface`（pina/_src/problem/problem_interface.py:6，`ABCMeta` 元类）声明八个抽象方法，`BaseProblem` 是这些骨架的实现者，再往下才是 `SpatialProblem`、`TimeDependentProblem`、`ParametricProblem`、`InverseProblem` 与 `SupervisedProblem` 五个场景子类。图谱给它 7 条 imports 入边（六个子类文件加 `pina/_src/solver/base_solver.py:13` 的直接 import）——它是 problem 层唯一被 solver 层消费的文件，相当于 problem 子系统对训练侧的"插座"。

## ② 内部结构

单类文件，成员地图：

| 成员 | 行号 | 职责 |
|---|---|---|
| `__init__` | pina/_src/problem/base_problem.py:33 | 条件回绑 + domains 字典收集 |
| `__deepcopy__` | pina/_src/problem/base_problem.py:55 | 手写深拷贝，绕过 `__init__` |
| `discretise_domain` | pina/_src/problem/base_problem.py:74 | 采样入口：四模式 + sample_rules 逐变量规则 |
| `add_points` | pina/_src/problem/base_problem.py:178 | 向已离散化域追加点 |
| `move_discretisation_into_conditions` | pina/_src/problem/base_problem.py:216 | 采样点搬进条件，域条件→输入条件 |
| `input_variables` | pina/_src/problem/base_problem.py:240 | 派生属性：spatial+temporal+parameters 聚合 |
| `discretised_domains` | pina/_src/problem/base_problem.py:262 | 采样结果字典 |
| `are_all_domains_discretised` | pina/_src/problem/base_problem.py:275 | 就绪判定（L283 一行 `all()`） |

`__init__` 只做两件事。第一，条件回绑：遍历 `self.conditions`，把问题自身与条件名写回条件对象——pina/_src/problem/base_problem.py:40-42 的 `self.conditions[condition_name].problem = self` 与 `.name = condition_name`，后续采样、残差计算都靠这条回链找到归属。第二，domains 收集：若子类没定义类属性 `domains` 就建空字典（L45-46），再把条件里直接传入的 `DomainInterface` 对象收编进 `self.domains` 并原地替换成名字字符串（L49-53）——于是"在 Condition 里传域对象"与"声明类属性 domains 再用字符串引用"两种写法都合法。

## ③ 外部连接

图谱边：imports 入边 7（inverse/parametric/spatial/time_dependent/supervised 问题文件 + base_solver.py + problem 桶），出边 6（condition.py、domain_equation_condition.py、label_tensor.py、core/utils.py、domain_interface.py、problem_interface.py），tested_by 出边 1 指向 tests/test_problem/test_base_problem.py（158 行）。注意它 import 了 `Condition`（pina/_src/problem/base_problem.py:8）——不是给用户用，而是 `move_discretisation_into_conditions` 内部要构造新条件。抽象契约在 `ProblemInterface`：`input_variables`（pina/_src/problem/problem_interface.py:85）、`conditions`（L105）等八个 abstractmethod 全部由本文件落地；场景子类再加码，如 `SpatialProblem.spatial_domain` 挂 `@abstractmethod`（pina/_src/problem/spatial_problem.py:34-35）强制子类给域，配套派生属性 `spatial_variables`（L41）直接从域对象取变量名；`TimeDependentProblem` 完全对称（pina/_src/problem/time_dependent_problem.py:33-34 的 `temporal_domain`、L40 的 `temporal_variables`）。

## ④ 数据流

走一遍 Poisson zoo 的实例化链（pina/_src/problem/zoo/poisson_problem.py:27 的 `Poisson2DSquareProblem(SpatialProblem)`）：

1. 用户 `Poisson2DSquareProblem()`：类属性 `output_variables`（L69）、`spatial_domain`（L70）、`domains`（L72-75）、`conditions`（L77-82）随类就绪；
2. `BaseProblem.__init__` 回绑 "D" 与 "boundary" 两个条件，并保留类属性 domains；
3. 用户调 `discretise_domain(n=100, mode="grid", domains=["D", "boundary"])`：domains 缺省取全部（L123-124），`n` 过 `check_positive_integer(n, strict=True)`（L154），每域一次 `self.domains[d].sample(n, mode)` 存入 `_discretised_domains`（L176）；
4. `Trainer` 构造 DataModule 时触发 `self.problem.move_discretisation_into_conditions()`（pina/_src/data/data_module.py:120）；
5. 该方法遍历带 `domain` 属性的条件，用采样点构造新条件 `Condition(input=self.discretised_domains[cond.domain], equation=cond.equation)`（pina/_src/problem/base_problem.py:227-230）并整体替换（L238）——DomainEquationCondition 从此变成 InputEquationCondition 形态，训练期 solver 只需处理"输入点 + 方程"一种形态，这是问题层给求解器层的最大减负。

`sample_rules` 是并行通道：按变量配不同 n/mode（L129-150 校验键集合必须与 `input_variables` 完全一致、规则形状合法），逐维采样后用 `merge_tensors`（pina/_src/core/utils.py:135）笛卡尔合并（L165-171）。

## ⑤ 设计决策（含批判视角）

- **回链换来的循环引用**：`cond.problem = self` 让条件能反查问题，代价是 problem↔condition 互相持引用，深拷贝必须手写——`__deepcopy__` 用 `__new__` 裸建实例再平移 `__dict__`（L65-70），刻意绕过 `__init__` 以免回绑重跑。批判：绕过 `__init__` 意味着类不变量不被重建，未来 `__init__` 增加任何派生状态都会与拷贝路径静默失配，且这条约束没有测试锁定。
- **覆盖 vs 追加的语义不对称**：重复 `discretise_domain` 对同一域是整体覆盖（L176 直接赋值），追加语义留给 `add_points`（L211-214 的 `LabelTensor.vstack`）。动态加密配点（R3 refinement 一类）必须走 add_points 通道。
- **就绪判定是浅检查**：`are_all_domains_discretised` 只查 key 存在（L283），不检查点集非空或标签一致——防御性弱，换来零开销。
- **采样模式的几何限制写在 docstring warning**（L110-120）：只有 `"random"` 对 Cartesian/Ellipsoid/Simplex 三种几何通用，`latin/chebyshev/grid` 仅 CartesianDomain 实现。限制根源在域层，但报错要到运行采样时才暴露。
- **两套声明风格并存**：zoo 风格的类属性 domains + 字符串引用，与条件内联域对象（L49-53 自动收编），灵活但没有 lint 区分，混用排查全靠读 `__init__`。

## ⑥ 新人提示

- 写新问题直接抄 pina/_src/problem/zoo/poisson_problem.py:69-82 的骨架：`output_variables` → `spatial_domain` → `domains` → `conditions`，再配 `solution` 方法对拍。
- `conditions` 可以是类属性 dict 也可以是 property，但条件对象不需要手动设 `problem` 属性——构造问题时自动回绑。
- `sample_rules` 的键必须与 `input_variables` 逐字一致（L133-139 严格 sorted 比对），多一个少一个都 ValueError。
- `move_discretisation_into_conditions` 由 DataModule 自动调（pina/_src/data/data_module.py:120），用户脚本不要手动调，否则条件会被二次替换。
- `input_variables` 是派生量（L253-258 聚合 spatial/temporal/parameters 三组），给问题加新自由度应声明 `parameters` 而不是覆盖该 property。

*自报：不计空格字符 4689；行号锚 46 处（file:line 锚 22 + 同文件 L 式行引用 24），均经 grep 对 commit 60ea474a 核实。*
