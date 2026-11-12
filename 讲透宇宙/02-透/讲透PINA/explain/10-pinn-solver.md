# 10 · pina/_src/solver/physics_informed_single_model_solver.py —— 标准 PINN 求解器：两个名字拼出的物理信息训练入口

## 一、角色定位

这是 PINA 库内最常用的 PDE 求解入口：旧名 `PINN` 的正统继承者（`pina/solver/__init__.py:69` 的弃用映射把 `"PINN"` 指向本类）。它只做一件事——把 problem（物理契约）、model（逼近器）、loss/weighting/optimizer/scheduler 装配成 Lightning 可训练对象。104 行里约 60 行是 docstring：class 声明、条件白名单、一行委托构造就是全部实现——v0.3 重构关键词 **mixin 组合** 的直接体现。

## 二、内部结构

主文件三块：

- `pina/_src/solver/physics_informed_single_model_solver.py:12`：`class PhysicsInformedSingleModelSolver(PhysicsInformedMixin, SingleModelSolver)`——灵魂行。MRO 为 PhysicsInformedMixin → SingleModelSolver（`pina/_src/solver/single_model_solver.py:10`，又是 `SingleModelMixin + ConditionAggregatorMixin + BaseSolver` 三拼）→ BaseSolver（`pina/_src/solver/base_solver.py:17`）→ LightningModule。
- `pina/_src/solver/physics_informed_single_model_solver.py:63-67`：`accepted_conditions_types = (InputTargetCondition, InputEquationCondition, DomainEquationCondition)`——监督数据、固定点残差、域上采样残差三类训练信号的白名单（import 行号 L4/L5/L7-9）。
- `pina/_src/solver/physics_informed_single_model_solver.py:95-104`：`__init__` 只把参数传给 `SingleModelSolver.__init__`。

docstring 锚：L33-39 给出目标函数 $\mathcal{L}_{\mathrm{problem}}$（域内+边界残差之和），L44-51 引 Karniadakis et al. 2021。继承链各层职责：

- **PhysicsInformedMixin**（`pina/_src/solver/mixin/physics_informed_mixin.py`）：全文 40 行只有两个方法——L16 与 L29 各挂 `@torch.enable_grad()` 装饰 `validation_step`（L17）与 `test_step`（L30），方法体是 `return super().validation_step(...)`（L27）。原因：Lightning 默认在验证/测试期关梯度，而物理残差必须求导。
- **ConditionAggregatorMixin**（`pina/_src/solver/mixin/condition_aggregator_mixin.py:15` `batch_evaluation_step`）：逐条件循环算标量损失（L34-41）并打日志（L47-53），交 weighting 聚合（L56）。
- **SingleModelMixin**（`pina/_src/solver/mixin/single_model_mixin.py`）：`forward` 就是 `self.model(x)`（L16-26）；`configure_optimizers`（L28-52）经 `optimizer.hook(...)`（L36）延迟实例化优化器，InverseProblem 再追加未知参数组（L39-47）。
- **BaseSolver**（`pina/_src/solver/base_solver.py`，434 行样板）：构造期三闸门——LightningModule 初始化（L50）、逐条件过白名单（L55-56）、InverseProblem 参数收集与 clamp（L63-68），`labelize_forward` 包装 forward（L71-76）。损失核心 `_compute_condition_loss`（L273）：L293 `condition.evaluate(data, self)` 得逐点残差 → `_loss_from_residual`（L299）→ 正则化钩子（L302-307）→ reduction（L310）。L314 与 L326 两个空方法是 GradientPINN/RBA 的覆盖点。

## 三、外部连接

图谱视角：imports 出边 5 条——三个条件类加 `pina/_src/solver/mixin/physics_informed_mixin.py`、`pina/_src/solver/single_model_solver.py`；入边 2 条——solver 桶文件（`pina/solver/__init__.py:31-33`）与 `pina/_src/callback/refinement/base_refinement.py:3-5`（R3 回调反向 import 本类做类型检查的罕见逆向边）。tested_by 为 `tests/test_solver/test_physics_informed_single_model_solver.py`；solver→condition 的 26 边是全仓最大子系统依赖。弃用通道：`pina/solver/__init__.py:63-76` 的 `_DEPRECATED_IMPORTS` 映射 12 个旧名，`_REMOVED_IMPORTS`（L83-86）里 `PINNInterface` 的报错说明其逻辑"现由 PhysicsInformedMixin 承担"。

## 四、数据流

一次 `trainer.train()` 中单个 batch 的走读：

1. DataModule 吐出 `batch = [(condition_name, data), ...]`，进入 `training_step`（`pina/_src/solver/base_solver.py:216`）→ `batch_evaluation_step`（L226），后者对每个条件调 `_compute_condition_loss`（`pina/_src/solver/base_solver.py:273`）。
2. 关键前置：Trainer 启动时已调 `move_discretisation_into_conditions`（`pina/_src/problem/base_problem.py:216`）把 DomainEquationCondition 物化成 `Condition(input=离散化点集, equation=...)`（L227-231），训练期真正被求值的是 InputEquationCondition。
3. `InputEquationCondition.evaluate`（`pina/_src/condition/input_equation_condition.py:111`）：L133 `requires_grad_(True)` 后执行 `self.equation.residual(samples, solver.forward(samples), solver._params)`（L134-136），equation 内部用 core/operator 的 grad 算微分；监督条件走 `pina/_src/condition/input_target_condition.py:86`，残差是 `forward(input) - target`（L107）。
4. 残差经 `_loss_from_residual`（`pina/_src/solver/base_solver.py:359-361`）与 reduction（L310）变标量，`weighting.aggregate`（`pina/_src/solver/mixin/condition_aggregator_mixin.py:56`）配平后交 Lightning 反向传播。

## 五、设计决策（含批判视角）

- **mixin 组合替代继承树**：v0.2 的 `PINNInterface` 继承层次拆成 9 个正交 mixin，16 个导出求解器（`pina/solver/__init__.py:3-20`）由组合产生。代价：行为分散五层文件，`super().validation_step`（`pina/_src/solver/mixin/physics_informed_mixin.py:27`）这类协作式调用要读者脑补完整 MRO；docstring 示例还在用旧名 `PINN`（`pina/_src/solver/physics_informed_single_model_solver.py:55`），文档债的物证。
- **域条件的"声明态/运行态"二分**：`DomainEquationCondition.evaluate` 干脆 `raise NotImplementedError`（`pina/_src/condition/domain_equation_condition.py:101`），域条件只是声明，训练前被物化为 input 条件——DataModule 只需处理张量批，但 conditions 字典被静默换对象（`pina/_src/problem/base_problem.py:238`）。白名单同理是 fail-fast 闸门（`pina/_src/solver/base_solver.py:55-56`），错误当场爆而非训练中段。
- **反演内嵌而非外挂**：`InverseProblem` 未知参数直接进优化器参数组（`pina/_src/solver/mixin/single_model_mixin.py:39-47`）并每步 clamp 到参数域（`pina/_src/solver/base_solver.py:88-98`），一个 solver 通吃正/反问题。

## 六、新人提示

用法样例直接抄测试：`tests/test_solver/test_physics_informed_single_model_solver.py:16` 的 `define_direct_problem_model` 展示物理条件之外混入监督条件（L27），五段式（constructor L53 / train L74 / validation L100 / test L126 / 存取恢复 L151）与十一个 solver 实现对应。三条实操：新代码永远用新名，旧名 `PINN` 只触发 DeprecationWarning（`pina/solver/__init__.py:97-102`）；`move_discretisation_into_conditions` 勿手动调；改行为先看 `pina/_src/solver/base_solver.py:314` 空钩子。

---
*自报：正文不计空格字符 4743；file:line 锚 28 处（对 commit 60ea474a 逐条核实）。*
