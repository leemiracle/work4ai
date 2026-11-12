# 09 · pina/_src/model/block/kan_block.py —— 可学习 B 样条替代 Linear+激活：KAN 的单层积木

## 角色定位

model/block 组合块目录里的"可学习激活"代表作：一个 166 行的 `KANBlock`，把经典层的 `nn.Linear` + 固定激活替换为**每条输入边一个可学习单变量 B 样条**，可选再并联一条 SiLU 线性残差路（pina/_src/model/block/kan_block.py:12-14 的 docstring 自述）。它实现 KAN 论文（Liu et al., arXiv:2404.19756，引用见同文件 L18-23）的"边上是可学习函数、节点只求和"表示，是 FeedForward 之外追求表达力上限的选项。依赖图上它是标准积木：仅被 `KolmogorovArnoldNetwork` 堆叠成全网、经 `pina.model.block` 桶导出，自身只依赖塔基工具与同层的 `VectorizedSpline`——后者并不在 block/ 目录，而在 `pina/_src/model/vectorized_spline.py`（同文件 L4 的 import 实证），这是本文件给新人的第一个定位陷阱。

## 内部结构

单类 `KANBlock(torch.nn.Module)`（同文件 L8），构造参数全家福在 L34-46：`input_dimensions/output_dimensions`、`spline_order=3`（三次样条）、`n_knots=10`、`grid_range=[0,1]`、`base_function=torch.nn.SiLU`、`use_base_linear=True`、`use_bias=True`、`init_scale_spline=1e-2`、`init_scale_base=1.0`。内部按四段展开：

- **参数校验**（同文件 L77-90）：`check_consistency(base_function, torch.nn.Module, subclass=True)` 允许传类或实例（L77）；四个正整数走 `check_positive_integer(..., strict=True)`（L78-81）；`grid_range` 长度必须为 2（L89-90）。
- **结点向量构造**（同文件 L93-106）：两端各重复 `spline_order` 个端点值（L93-94）构成 clamped B 样条结点；内部结点数 `n_internal = max(0, n_knots - 2*spline_order)`（L97），在区间上均匀 `torch.linspace`（L100-102）；拼接后 repeat 到每个输入维（L105-106）。
- **可学习组件注册**：样条控制点 `randn(input, output, #basis) * init_scale_spline`（同文件 L109-116），基函数个数 `#basis = 结点数 − spline_order`（L113）；`self.spline = VectorizedSpline(order, knots, control_points)`（L119-121）——控制点在 VectorizedSpline 的 setter 里被包成 `torch.nn.Parameter(..., requires_grad=True)`（pina/_src/model/vectorized_spline.py:545），这是"样条系数即模型参数"的注册点。基函数路并联 `self.base_function = base_function()`（L124）与 `base_weight` 参数（L128-131，按 `init_scale_base/sqrt(in)` 缩放，或 None L133）；`bias` 零初始化（L137，可关 L139）。
- **forward**（同文件 L141-166）：`y = self.spline(x)` 得 `[batch, in, out]`（L153）；有 base 路时 `einsum("bi,oi->bio", base_function(x), base_weight)` 相加（L155-158）；**`y.sum(dim=1)` 在块内完成跨输入维聚合**（L161）——这一行就是 KAN 的"节点求和"；最后加 bias（L163-164）。

数学上这一层计算 $f_j(x)=\sum_i \phi_{ij}(x_i)+b_j$，$\phi_{ij}$ = 样条 + SiLU 线性残差，即 Kolmogorov-Arnold 表示的可学习化。

## 外部连接

- **imports 出边 2 条**：`pina/_src/core/utils.py`（同文件 L5，取 `check_consistency` 与 `check_positive_integer`）与 `pina/_src/model/vectorized_spline.py`（同文件 L4）。
- **fan-in 2 条**：桶文件 pina/model/block/__init__.py（`__all__` 收录于 L28、import 在 L54）与 `pina/_src/model/kolmogorov_arnold_network.py`（L2 import KANBlock）。另：`VectorizedSpline` 本尊也被顶层 pina/model/__init__.py:39 直接导出（`__all__` L20），可脱离 KAN 单独使用。
- **tested_by 1 条**：tests/test_block/test_kan_block.py，3 个测试函数，构造测试高度参数化（L15 起）覆盖合法组合与非法入参（`input_dimensions=-1` 在 L30、`output_dimensions=-1` 在 L34 等）。

## 数据流

一次 forward 走进样条内部：`x [batch, in]` 进 `self.spline(x)` 后，`VectorizedSpline.forward`（pina/_src/model/vectorized_spline.py:381）先调 `basis(x)`（L286 起）——以向量化 Cox-de Boor 递推对每个输入特征算出全部 B 样条基函数值，得 `[batch, in, #basis]`；随后 `torch.einsum("bsc,soc->bso", basis, self.control_points)`（同文件 L404）把基函数值与控制点线性组合成 `[batch, in, out]` 返回。回到 KANBlock.forward，并联的 base 路对同一输入过 SiLU 再与 `base_weight` 外积（pina/_src/model/block/kan_block.py:156-157），两路相加后 `sum(dim=1)` 聚合输入维、加 bias 出层（L161-164）。全网层面由 `KolmogorovArnoldNetwork`（pina/_src/model/kolmogorov_arnold_network.py:6）驱动：构造时仅校验 `layers` 为 int 且长度 ≥2（L77-81），随后 `ModuleList` 按 `layers[i]→layers[i+1]` 生成 `len(layers)-1` 个 KANBlock 并透传全部样条超参（L84-100）；forward 就是逐块链式前向（L102-115）。反向传播时，梯度同时流向 `control_points`、`base_weight`、`bias` 三类参数——样条系数与权重同权优化，无需交替训练。

## 设计决策（含批判视角）

- **双路残差结构是稳定性关键**：样条路 `init_scale_spline=1e-2`（同文件 L44、L115）使初始状态近似一个 SiLU 线性层，base 路（scale 1.0，L45）兜底全局形状——避免了"一出生就是随机摆动样条"的优化灾难，与 KAN 论文的噪声样条初始化同理。代价：学习率太小时样条路可能始终被 base 路压制。
- **聚合内置在块内**（L161）：一个 KANBlock 就是一层完整 KAN，而非论文那种"每条边一模块"的可视化粒度——想画每条边学到的函数得手动重构 `control_points`，可解释性工具缺位。
- **clamped 结点与硬约束**：两端重复结点（L93-94）让端点处样条退化为局部支集，`VectorizedSpline` 构造时强校验 `#knots = order + #control_points`（pina/_src/model/vectorized_spline.py:200 的报错文本）并在控制点数小于 order 时告警"degenerate spline"（L210）。`grid_range` 固定不可学习——输入超出范围时 B 样条在边界平坦外推，**喂入前归一化到 grid_range 是硬要求**，否则边界外误差无声放大。
- **参数/计算成本约为 Linear 的 8 倍**：默认三次、10 结点时 `#basis=7`（n_internal=4，总结点 2×3+4=10，同文件 L97、L113），样条参数 7·in·out，加 base 的 in·out 与 bias——同尺寸 Linear 是 in·out+out，前向还多出基函数递推。且无训练中扩格等网格自适应，深窄配置开销失控快，宽而少层更划算。
- **文档与默认值漂移三处**：`KolmogorovArnoldNetwork` 的 docstring 写 `n_knots` "Default is 3"（pina/_src/model/kolmogorov_arnold_network.py:55，实际 10）、写 `grid_range` "Default is [0, 1]"（L57，实际代码 L39 是 `[-1, 1]`）；而 KANBlock 自己的默认是 `[0,1]`（同文件 L40）——堆叠时 block 继承网络传入值所以行为无冲突，但三处口径不一致足以误导调参。顺带：两处引用均标 "2025"（同文件 L20 与 pina/_src/model/kolmogorov_arnold_network.py:19）而 arXiv:2404.19756 首发于 2024，年份笔误。
- **组织小瑕疵**：核心依赖 VectorizedSpline 放在 model/ 根而非 block/（同文件 L4），跨目录引用削弱了"block 目录=积木库"的直觉。

## 新人提示

1. 实际使用请走 `KolmogorovArnoldNetwork(layers=[2, 16, 1])`（pina/_src/model/kolmogorov_arnold_network.py:27-29 官方示例），别手搓 block；网络 grid_range 默认 `[-1,1]`（L39），先与输入归一化范围对齐。
2. 调参预算：每层参数 ≈ 8×同尺寸 Linear；观察 `spline.control_points` 范数是否离开 1e-2 量级，判断样条路是否真在学（否则等价普通 SiLU 网络）。
3. 输入范围、grid_range、n_knots 三个量要一起看：区间越大、结点越稀，样条越"钝"。
4. 构造参数合法组合直接抄 tests/test_block/test_kan_block.py:15-30 的参数化表，非法用例（L30、L34）是校验行为速查。

---
*自报：不计空格字符数 4,779；仓根全路径 `文件:行号` 锚 11 处 + 「同文件 LNN」行引用 15 处，全部经 Read/grep 对 commit 60ea474a 逐条核实。*
