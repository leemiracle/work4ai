# 11 · pina/_src/callback/refinement/r3_refinement.py —— R3 自适应配点：按残差排序的 Retain-Resample-Release

## 一、角色定位

PINN 的配点（collocation points）不是一次定终身的：解在局部有边界层或激波时，全域均匀撒点会把预算浪费在"已解得很好"的区域。`R3Refinement` 是 PINA 的回答——挂在 Lightning 训练循环上的 Callback，每隔 `sample_every` 个 epoch 按残差做一次"保留-重采样-释放"（Retain-Resample-Release），把预算倾斜向误差大的区域。文件 105 行，一个类一个核心方法 `sample`，是 callback 子系统里唯一深度介入数据集的回调。算法出处：Daw et al. 2023（`pina/_src/callback/refinement/r3_refinement.py:23`，DOI 在 L26）。

## 二、内部结构

- `pina/_src/callback/refinement/r3_refinement.py:10`：`class R3Refinement(BaseRefinement)`——周期调度、条件校验、钩子全在基类，本文件只实现"怎么换点"。
- `pina/_src/callback/refinement/r3_refinement.py:34-39`：`__init__(sample_every, residual_loss=torch.nn.L1Loss, condition_to_update=None)`。L58 调 `super().__init__` 存周期与条件名单；L61-65 `check_consistency` 校验损失类合法；L68 `self.loss_fn = residual_loss(reduction="none")`——必须逐点损失，聚合后的标量无法排序。
- `pina/_src/callback/refinement/r3_refinement.py:70-105`：核心 `sample(current_points, condition_name, solver)` 六步：
  1. L81 取 `root_device`，L82-83 把现有点搬上设备并 `requires_grad_(True)`（残差要对输入求导）。
  2. L86 `target = condition.evaluate({"input": current_points}, solver)`——复用训练管线的条件求值；L87-89 `self.loss_fn(target, torch.zeros_like(target)).mean(dim=...)` 把逐点损失在非 batch 维平均，得每点标量残差。
  3. L92-94 从 `condition.domain` 反查 `domains` 字典拿域对象，并取初始点数 `num_old_points`。
  4. L97 `mask = (residuals >= residuals.mean()).flatten()`——以残差均值为阈值；L98-99 保留高残差点（记得补回 `.labels`）。
  5. L102 `num_new_pts = max(num_old_points - len(high_residual_pts), 0)`；L103 `domain.sample(num_new_pts, "random")` 全域均匀补新点。
  6. L105 `LabelTensor.cat([high_residual_pts, samples])` 拼回总量恒定的新点集。

基类 `pina/_src/callback/refinement/base_refinement.py` 的骨架：L13 `class BaseRefinement(Callback, RefinementInterface)` 双继承（Lightning 钩子 + 抽象契约，`pina/_src/callback/refinement/refinement_interface.py:33-34` 把 `sample` 定为 abstractmethod）；L42 `check_positive_integer(sample_every, strict=True)` 挡住 0 与负数；L55 `on_train_start` 三件事——L70-74 `isinstance` 强校验 solver 必须是 `PhysicsInformedSingleModelSolver`，L77-82 在 `condition_to_update=None` 时默认收集所有带 `domain` 属性的条件，L102-106 抓取 `trainer.datamodule.train_datasets` 记录初始规模；L108 `on_train_epoch_end` 在 `epoch % sample_every == 0 and epoch != 0`（L122）时逐条件执行 L127-129：取点 → `sample` → 写回。

## 三、外部连接

imports 四条出边：`core/utils.check_consistency`（塔基校验器，全库 fan-in 95）、`core/label_tensor.LabelTensor`（点的载体）、`loss/dual_loss_interface.DualLossInterface`（`pina/_src/loss/dual_loss_interface.py:7`，`torch.nn._Loss` 的双张量抽象接口，`forward(input, target)` 在 L13-14——"输入+目标"形态的自定义损失都可插进 `residual_loss` 槽位）、`base_refinement`。一条特殊逆向边：`pina/_src/callback/refinement/base_refinement.py:3-5` import 求解器类做类型闸门，callback→solver 是全仓罕见的依赖方向。入边 1 条：`pina/callback/__init__.py:25` 把本类提到公共 API（L16 列入 `__all__`）。tested_by：`tests/test_callback/test_r3_refinement.py`，L10-12 三维 parametrize 共 2×2×3 组合。

## 四、数据流

一次细化周期的走读（默认 `sample_every=5`，`pina/_src/callback/refinement/r3_refinement.py:31` docstring 示例）：

1. 训练前 `on_train_start`（`pina/_src/callback/refinement/base_refinement.py:55`）：若用户没传 `condition_to_update`，L77-82 收集 problem 中所有带 `domain` 的条件（如 Poisson 案例的 `"D"` 与 `"boundary"`），L103-106 记下初始点数——后续"总量守恒"的基准。
2. epoch 4 结束时 `on_train_epoch_end`（L108）被 Lightning 调用，L122 判定 `4 % 5 != 0` 跳过；epoch 5 结束时条件满足。
3. 对每个目标条件，L127 从 `conditions[name].data.input` 取当前配点（训练前已被 `move_discretisation_into_conditions` 物化成 input 形态），交给 `pina/_src/callback/refinement/r3_refinement.py:70` 的 `sample`。
4. `sample` 里 L86 的 `condition.evaluate` 与训练同一条路：InputEquationCondition 求值 → `equation.residual(samples, solver.forward(samples), ...)`（`pina/_src/condition/input_equation_condition.py:134-136`）→ operator 自动微分。细化标准与训练目标天然同源，设计的巧妙处。
5. L97 筛出高残差点，L102-103 域上均匀补点，L105 拼接；L129 写回条件的数据槽，下一个 epoch 立即用新点。

## 五、设计决策（含批判视角）

- **残差复用训练管线**：`sample` 不自建误差估计，直接调 `condition.evaluate(..., solver)`（L86）——零重复实现，"细化依据"与"训练目标"严格一致；代价是每次细化要对全部配点做带自动微分的前向，`sample_every=1` 时开销可观。
- **均值阈值 vs 论文的百分比 retain/release**：实现用 `residuals >= residuals.mean()`（L97）硬切分，保留比例随残差分布漂移——重尾分布保留过半，均匀误差约一半。"Release"没有显式步骤，是 L102 总量守恒的隐式结果：低残差点被挤出。与 Daw et al. 2023 的固定比例三步法相比是简化；`residual_loss` 换 L1/MSE 也改变排序形状（L1 对离群点更钝）。
- **全域均匀重采样**：L103 `domain.sample(num_new_pts, "random")` 全域均匀抽新点而非向高残差邻域偏置。对狭窄边界层/激波，新点落入关键区域的概率与面积成正比，收敛增益受限；更激进的 RAD 概率加权采样要改 `sample`——好在基类把它留成唯一抽象点。
- **`isinstance` 闸门过窄**：`pina/_src/callback/refinement/base_refinement.py:70-74` 只认 `PhysicsInformedSingleModelSolver`，CausalPINN/RBAPINN 等物理信息变体被 RuntimeError 拒绝（docstring L62-63 还提已移除的 `PINNInterface` 旧名）。
- **直接改写训练数据集**：L129 写 `conditions[name].data.input` 绕过 DataModule，换取零重启热更新；代价是 checkpoint 点集与细化后不一致，恢复训练会回退。

## 六、新人提示

用法三行：`R3Refinement(sample_every=5)` 塞进 `Trainer(solver=..., callbacks=callback, ...)`（`tests/test_callback/test_r3_refinement.py:57-62` 是最小样例）。三条注意：L122 的 `epoch != 0` 意味着首轮绝不换点，`sample_every` 取 `max_epochs` 的约数才均匀触发；验证细化生效别只看点数——测试断言口径就是"总量恒等于初始规模"（`tests/test_callback/test_r3_refinement.py:88-89`）；细化指定条件传 `condition_to_update=["D"]`，该条件必须带 `domain` 属性（`pina/_src/callback/refinement/base_refinement.py:95-99` 报错）。实验时 `residual_loss` 槽位是现成注入点：任何 `_Loss` 子类或 `DualLossInterface` 实现都能改变"何谓高残差"。

---
*自报：正文不计空格字符 4740；file:line 锚 16 处（对 commit 60ea474a 逐条核实）。*
