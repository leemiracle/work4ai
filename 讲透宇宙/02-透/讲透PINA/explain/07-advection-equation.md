# 07 · pina/_src/equation/zoo/advection_equation.py —— 100 行装下一条 PDE：平流方程的声明式封装

## 角色定位

这是 equation zoo 里最适合当"第一篇精读"的方程类：它足够典型（一个时间导数 + 一个空间梯度内积），又足够小巧（全文件 100 行）——读通它，zoo 里其余 11 个方程类全是同一模板的变奏。它在架构里扮演的角色是**数学内核的消费者**：自己一行微分都不实现，把 ∂u/∂t 与 c·∇u 全部委托给塔基 `pina/_src/core/operator.py` 的 `grad` 算子（pina/_src/equation/zoo/advection_equation.py:5 只 import 了 `grad`），再用闭包把 residual 组装成一个可调用对象交给 `Equation` 基类包装。图谱视角：fan-in 仅 2（被 `pina/equation/zoo.py` 转发清单与 `advection_problem.py` 预置问题消费），tested_by 指向 tests/test_equation_zoo/test_advection_equation.py——zoo 类是叶子节点，改它影响面极小，但它是 problem→condition→solver 链路上"物理"二字的落点。

## 内部结构

全文件只有一个类 `AdvectionEquation(Equation)`（同文件 L9），但其内部结构暗藏两层：

- **构造层 `__init__(self, c)`**（同文件 L28）：`check_consistency(c, (float, int))` 做元素级类型校验（L39）；空列表抛 `ValueError("'c' cannot be an empty list.")`（L42）；标量归一为单元素列表后，`self.c = torch.tensor(c).unsqueeze(0)` 存成 `[1, len(c)]` 张量（L47）。docstring 声明公式 ∂u/∂t + c·∇u = 0（L14-16 的 math 块），`c` 支持标量（各空间维同速）或逐维列表两种形态（L32-35）。
- **闭包层 `def equation(input_, output_)`**（同文件 L49）：真正的 residual 实现，捕获 `self.c`。内部步骤：取标签并排除时间维 `spatial_d = [di for di in input_lbl if di != "t"]`（L64）；强制输入含 `'t'` 否则 ValueError（L67-70）；列表形态的 `c` 长度必须等于空间维数（L73-77）；`c` 先 repeat 到 batch 维、必要时按空间维数广播、再 unsqueeze 出内积轴（L80-85）；两次 `grad` 分别取 `d="t"` 与 `d=spatial_d`（L88-89）；梯度 reshape 成 `[..., out_dim, spatial_d]` 再 transpose（L92-93）；`(tmp * c).sum(dim=ndim-2)` 完成加权求和（L96）；最后 `return time_der + adv`（L98）。
- 收尾一行 `super().__init__(equation)`（同文件 L100）把闭包上交——这是全 zoo 的统一句式。

对照 PoissonEquation（pina/_src/equation/zoo/poisson_equation.py:9）能看清模板弹性：Poisson 的 residual 只有 `lap - self.forcing_term(input_)` 两行（同文件 L46-47），一次 `laplacian` 算子搞定；Advection 因为 `c` 是常数参数而非输出场，才需要两次 `grad` 加手工内积。

## 外部连接

图谱给这个文件的边很少，恰好刻画了它"叶子"的本分：

- **imports 出边 3 条**：`pina/_src/core/operator.py`（grad）、`pina/_src/core/utils.py`（check_consistency）、`pina/_src/equation/equation.py`（Equation 基类）——全部指向塔基与同层基类，零跨子系统依赖，符合"方程层不做微分、全靠塔基算子"的金字塔纪律。
- **fan-in 2 条**：`pina/equation/zoo.py`（12 个方程类统一转发，AdvectionEquation 在 pina/equation/zoo.py:19 导入、:4 进 `__all__`）与 `pina/_src/problem/zoo/advection_problem.py`（预置问题在 L25 `class AdvectionProblem(SpatialProblem, TimeDependentProblem)`、L98 以 `Condition(domain="D", equation=AdvectionEquation(self.c))` 消费它）。
- **tested_by 1 条**：tests/test_equation_zoo/test_advection_equation.py，单测试函数 `test_advection_equation(c)`（L14）参数化覆盖四类行为——空列表构造抛错（L21）、非法类型抛错（L25）、缺 `'t'` 标签抛错（L31）、列表长度与空间维不符抛错（L37-38）。注意它测的全是防御路径，residual 的数值正确性只断言了 `residual.shape == u.shape`（L28）——zoo 对拍的数值精度校验要靠 test_problem_zoo 那条线（预置问题的解析解对拍）。

## 数据流

走一遍 solver 训练时这个类被调用的真实链路：`PhysicsInformedSingleModelSolver` 对挂了 `DomainEquationCondition` 的 batch 逐条件调 `equation.residual(input_, output_)`；`Equation.residual`（pina/_src/equation/equation.py:40）先用 `inspect.signature` 存下的参数个数分派——2 参走正向问题 `self.__equation(input_, output_)`（同文件 L61-62），3 参才走反演路径注入 `params_`（同文件 L65-66）；于是控制权进入我们在 L49 定义的那个闭包。闭包里两次 `grad`（同文件 L88-89）各自触发 `torch.autograd.grad` 反传（pina/_src/core/operator.py:316 的通用 `grad` 对每个输出列求 ∂output/∂input）；reshape/transpose 只是把 `[batch, out×spatial]` 的扁平梯度重排成可内积的形状；L96 的逐元素乘加得到 `[batch, out]` 的 `c·∇u`，与 `time_der` 相加即 residual。solver 侧再对 residual 取模方、经 weighting 配平、反向传播。整条链路里本文件的代码只在"求 residual"一步出现——这就是声明式的含义：物理知识以一个可调用对象的形式被注入训练循环。

## 设计决策（含批判视角）

- **闭包而非方法**：residual 写成 `__init__` 内的局部函数并捕获参数（L49、L100），使 `Equation` 基类可以统一包装任意"自定义方程 lambda"与"zoo 方程类"两种来源（Equation 本身就接受 lambda，见 pina/_src/equation/equation.py:18 的示例）。代价是闭包与实例生命周期绑定、不可 pickle——想保存/加载含 zoo 方程的问题对象时要小心。
- **常数 c 走手工内积而非 operator.advection**：塔基明明有 `advection` 算子（pina/_src/core/operator.py:456），但它的契约是 `velocity_field` 必须取自**输出标签**（同文件 L507 强制校验），即速度本身是网络输出的场景；zoo 这里的 `c` 是外部常数，于是退回两次 `grad` 手工组装。BurgersEquation 同理（pina/_src/equation/zoo/burgers_equation.py:77-78 也是两次 `grad`）。这条分界线读代码前最好先知道，否则会疑惑"为什么有现成算子不用"。
- **防御式校验前置到构造期与 residual 期两级**：类型/空列表在 `__init__`（L39-42），`'t'` 缺失与维度不匹配推迟到 residual（L67-77）——因为空间维数只有拿到真实输入标签才知道。合理，但报错位置离用户组装 Condition 的位置较远，调试时栈里看到的是训练期的错。
- **批判：标量与单元素列表不可区分**。`c=2.0` 与 `c=[2.0]` 走同一广播路径（L73 的 `shape[-1] > 1` 条件放过单元素列表），行为一致是巧合而非设计保证；且 `c` 不含学习参数，反演问题里想学速度场时这个类帮不上忙，得自己写 Equation。
- **批判：residual 数值正确性在单测里是薄弱环节**。test 只断言形状（tests/test_equation_zoo/test_advection_equation.py:28），解析对拍被推给了 problem zoo 侧；如果你改动了 L92-96 的 reshape/sum 逻辑而只跑这个测试文件，维度对但求和轴错了的 bug 会漏网——自测时应手算一个小 batch 对拍。

## 新人提示

1. 抄这个文件写自定义 PDE 是最快的入门路径：复制 `__init__` 校验骨架 + 闭包模板，把 L88-98 换成你的残差式子即可，注意导数结果按 `dudx` 式标签扁平排列，reshape 前先打印 `grads.shape` 对齐。
2. CLAUDE.md 的铁律在此文件的映射：`grad` 不缓存，L88-89 已经是"一次计算多分量"的正确写法——千万别写成对每个空间维单独调一次 `grad`（六次 backward 与一次的差）。
3. 输入必须带 `'t'` 标签且时间维命名固定为 `"t"`（L64-70）；做稳态问题时换 Poisson/Helmholtz，别硬塞一个假 t。
4. 排查 residual 形状错误的顺序：先查 `input_.labels` 顺序（`spatial_d` 由标签排除法得出，L64），再查 L92 的 reshape 是否与 `output_.shape` 匹配——这两处是最常见的断点。

---
*自报：不计空格字符数 4,458；仓根全路径 `文件:行号` 锚 9 处 + 「同文件 LNN」行引用 9 处，全部经 sed/grep 对 commit 60ea474a 逐条核实。*
