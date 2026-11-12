# PINA explain 系列：12 篇重要文件精讲

> 依据 PINA 仓知识图谱（1326 节点 / 2581 边 / 15 层 / 16 步 tour，validator 0 issues）与源码撰写，全部行号锚对 commit **`60ea474a`**（version 0.3.2）逐条核实。与 `../onboarding/ONBOARDING.md`（全局上手）互补：onboarding 答"全仓怎么读"，本系列答"这 12 个文件里面到底发生了什么"。

## 索引

| # | 文件 | 精讲主文件 | 一句话 | 字符数 | 全路径锚 |
|---|---|---|---|---|---|
| 01 | [01-pina-facade.md](01-pina-facade.md) | `pina/__init__.py` | 37 行的门面：PINA 公共 API 契约本身 | 3,444 | 22 |
| 02 | [02-core-utils.md](02-core-utils.md) | `pina/_src/core/utils.py` | 塔基工具集：全库第二高 fan-in（95）的无状态函数层 | 3,543 | 25 |
| 03 | [03-core-operator.md](03-core-operator.md) | `pina/_src/core/operator.py` | 向量微分算子库：PINN 物理残差的数学引擎 | 3,869 | 32 |
| 04 | [04-base-problem.md](04-base-problem.md) | `pina/_src/problem/base_problem.py` | 声明式问题抽象的根 BaseProblem（注意：仓内无 abstract_problem.py） | 4,712 | 21 |
| 05 | [05-condition.md](05-condition.md) | `pina/_src/condition/condition.py` | 训练契约的六路分派门（__new__ + _SPECS） | 4,091 | 12 |
| 06 | [06-cartesian-domain.md](06-cartesian-domain.md) | `pina/_src/domain/cartesian_domain.py` | 盒几何基元：区间字典驱动与四种采样 | 4,059 | 18 |
| 07 | [07-advection-equation.md](07-advection-equation.md) | `pina/_src/equation/zoo/advection_equation.py` | 100 行装下一条 PDE：平流方程的声明式封装 | 4,458 | 9 |
| 08 | [08-deeponet.md](08-deeponet.md) | `pina/_src/model/deeponet.py` | MIONet 与 DeepONet 同居一文件（L9/L324 继承） | 4,580 | 6 |
| 09 | [09-kan-block.md](09-kan-block.md) | `pina/_src/model/block/kan_block.py` | 可学习 B 样条替代 Linear+激活：KAN 的单层积木 | 4,779 | 11 |
| 10 | [10-pinn-solver.md](10-pinn-solver.md) | `pina/_src/solver/physics_informed_single_model_solver.py` | 标准 PINN 求解器：两个 mixin 名拼出的物理信息训练入口 | 4,799 | 28 |
| 11 | [11-r3-refinement.md](11-r3-refinement.md) | `pina/_src/callback/refinement/r3_refinement.py` | R3 自适应配点：按残差排序的 Retain-Resample-Release | 4,796 | 16 |
| 12 | [12-tests-conftest.md](12-tests-conftest.md) | `tests/conftest.py` | 17 行共享装置与"每文件自洽"的测试哲学 | 3,738 | 8 |

选题按图谱 tour 核心步与边权重微调：原计划的 `abstract_problem.py`/`solver/pinn.py`/`equation/zoo/advection.py` 在 v0.3.2 中实际为 `base_problem.py`/`physics_informed_single_model_solver.py`/`advection_equation.py`，已按真实结构落位；`pinn.py` 一篇由 mixin 化的 PINN 求解器 + base_solver 邻接覆盖。

## 统一口径说明（字数与锚）

- **字数口径**：每篇"不计空格总字符"= `len(re.sub(r'\s', '', text))`，即剔除全部空白（空格/换行/制表）后的字符数，含标题、表格、代码片段与文末自报行；窗 2,500–4,800，12 篇全部在窗内（合计 50,759）。各篇文末斜体行自报的数字与主编会话独立复测一致。
- **锚两种形态**：①仓根全路径锚 `pina/_src/core/operator.py:316`（含行区间 `:69-82`）；②「同文件 L 式」`L324`——仅当同篇前文已给出该文件全路径后才允许使用，指向同一文件的后续行。`pina/` 顶层同名转发 shim（`pina/utils.py`、`pina/operator.py` 等）与 `_src` 实现文件一律以全路径消歧，禁止裸 basename 锚。
- **锚验证**：两道工序——写手对每条锚先 grep/sed 核实行内容再写入；主编会话再跑机械校验（文件存在 + 行号在界内，218 处全路径引用零坏）并独立抽验语义（锚行内容与文中声称逐条比对，01-06 抽 20 处、07-12 抽 24 处、另核 4 处关键 L 式，**48/48 命中**）。锚量合计：全路径锚 218 处引用（208 唯一）+ 同文件 L 式唯一引用 297 处。

## 系列级实证发现（各篇详述的勘误/反直觉点）

1. **DeepONet 按文件名找不到**：`MIONet` 在 deeponet.py L9、`DeepONet(MIONet)` 在 L324，继承关系倒挂；`model` property 存在 docstring 与代码不符的复制粘贴级 bug（L313-321，返回 `self._indeces` 而非子网列表）。
2. **方程 zoo 不用塔基 advection 算子**：`operator.advection` 的契约要求 velocity 取自输出标签（operator.py L507 校验），常数速度场景（AdvectionEquation/BurgersEquation）退回两次 `grad` 手工组装。
3. **`move_discretisation_into_conditions` 的真实调用点**在 `pina/_src/data/data_module.py:120`（DataModule 构造期），非 Trainer 直接调；`DomainEquationCondition.evaluate` 本体是 `NotImplementedError`，域条件在训练前被物化为 input 条件。
4. **顶层 shim 只转发子集**：`pina/utils.py` 仅 re-export 3/10 个函数，`torch_lhs`/`chebyshev_roots` 是内部基元；从顶层 import 不到不等于不存在。
5. **R3 细化用残差均值阈值**（r3_refinement.py L97）而非论文的固定百分比，release 是总量守恒下的隐式结果。
6. **定点维 int64 陷阱**（`CartesianDomain({"t": 0})`）由 `.opencode/skills/RULES.md:59-63` 文档兜底而非类型系统；partial() 边界面不去重、grid 模式边界角点双计数，均为批判视角实锤。
7. **测试体系唯一共享装置**是 conftest.py 的 `clean_tmp_dir`（实测 12 个消费文件），显式、无状态、每文件可独立阅读；CI 矩阵三 OS × 五 Python（tester.yml:16-17）。
