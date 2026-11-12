# 03 · pina/_src/core/operator.py —— 向量微分算子库：PINN 物理残差的数学引擎

## 1. 角色定位

`pina/_src/core/operator.py`（521 行）实现 PINA 的向量微分算子：`grad / div / laplacian / advection` 四个通用版加 `fast_grad / fast_div / fast_laplacian / fast_advection` 四个低内存变体，外加三个私有核。它是"物理信息"三个字的机制所在——训练信号不来自标注数据，而来自用自动微分在网络输出上现场求导、组装 PDE 残差；方程 zoo 的全部 11 个方程类（poisson/burgers/advection/helmholtz 等）以及 `gradient_enhanced_mixin`、`inverse_poisson_problem` 都 import 本文件（图谱 imports 入边 13 条），它自己只依赖 `LabelTensor`（pina/_src/core/operator.py:19）。消歧提醒：顶层 `pina/operator.py` 是转发 shim，把 8 个公开算子 re-export（pina/operator.py:9-18）——用户侧 `from pina.operator import grad` 与本文件是同一实现。

## 2. 内部结构

三私有 + 八公开的分层地图：

| 行号 | 函数 | 职责 |
|---|---|---|
| pina/_src/core/operator.py:22 | `_check_values` | 公共前置校验：LabelTensor 双检、标签子集检查、None 补全 |
| pina/_src/core/operator.py:72 | `_scalar_grad` | 梯度核：一次反传拿单分量对所有输入维的导数 |
| pina/_src/core/operator.py:98 | `_scalar_laplacian` | 拉普拉斯核：两次 fast_grad 链式求二阶导 |
| pina/_src/core/operator.py:124 | `fast_grad` | 无校验梯度：scalar 快路径 + vector 逐分量 |
| pina/_src/core/operator.py:167 | `fast_div` | 无校验散度：梯度张量取对角列求和 |
| pina/_src/core/operator.py:198 | `fast_laplacian` | 无校验拉普拉斯：std / divgrad 双方法 |
| pina/_src/core/operator.py:275 | `fast_advection` | 无校验平流：∇u 与速度场内积 |
| pina/_src/core/operator.py:316 | `grad` | 通用版 = _check_values + fast_grad |
| pina/_src/core/operator.py:357 | `div` | 通用版，另加 components/d 等长校验 |
| pina/_src/core/operator.py:405 | `laplacian` | 通用版，透传 method 参数 |
| pina/_src/core/operator.py:456 | `advection` | 通用版，另加速度场标签与维度校验 |

导数结果的列命名协议是跨文件契约：梯度列 `d{c}d{i}`（如 `dudx`，pina/_src/core/operator.py:150、163）、拉普拉斯列 `dd{c}`（pina/_src/core/operator.py:229）、平流列 `adv_{c}`（pina/_src/core/operator.py:313）——方程 residual 里 `extract("dudx")` 能工作全靠这套命名。

## 3. 外部连接

imports 出边 1 条（label_tensor.py：算子的输入输出类型与 extract 机制）；入边 13 条：顶层 shim `pina/operator.py`、equation zoo 七个 PDE 加 FixedFlux/FixedGradient/FixedLaplacian 三个边界类、`inverse_poisson_problem.py`、solver 侧的 `gradient_enhanced_mixin.py`。tested_by 出边 1 条指向 `tests/test_operator.py`（独立于 equation zoo 测试——算子数学与方程封装分层验证）。下游消费模式统一：zoo 方程的 residual 函数里一行 `from pina._src.core.operator import laplacian`，方程层自己永远不做微分。

## 4. 数据流

走读 PoissonEquation 残差的二阶导链（PINN 最典型路径）：residual 调 `laplacian(u, x)` → 通用版先 `_check_values`（pina/_src/core/operator.py:443-445）：确认输入输出都是 LabelTensor（pina/_src/core/operator.py:46-51）、components/d 是标签子集（pina/_src/core/operator.py:62-67）→ 委托 `fast_laplacian`（pina/_src/core/operator.py:447-453）→ 单输出走 scalar 快路径（pina/_src/core/operator.py:226-230）进 `_scalar_laplacian`：第一次 `fast_grad` 得一阶梯度（pina/_src/core/operator.py:112-114），第二次把梯度当输出再 `fast_grad` 得二阶（pina/_src/core/operator.py:115-117），`extract` 出对角项 `dudx` 的 d/dx 分量并求和（pina/_src/core/operator.py:118-121）。这一切成立的前提藏在 `_scalar_grad` 的反传参数里：`torch.autograd.grad(..., create_graph=True, retain_graph=True)`（pina/_src/core/operator.py:86-93）——不建二阶图，第二次 fast_grad 根本无图可反。

## 5. 设计决策

**其一，"通用版=校验+fast 版"的模板方法**（grad 的全部逻辑就两行，pina/_src/core/operator.py:351-354）：把安全与速度拆成两层，库内热路径（zoo 方程、solver）可直取 fast 版，用户手写算子走通用版。**其二，性能账要算清**：`fast_grad` 的 vector 分支是对每个分量各调一次 `_scalar_grad` 的列表推导（pina/_src/core/operator.py:154-160）——每次调用都是一次完整 backward。RULES.md"六次单独 grad 就是六次 backward"的机制根源在此：算子不缓存，且单次 `grad(components=[u,v])` 与两次 `grad(u)`、`grad(v)` 的反传次数相同，真正的浪费是用户对同一网络输出重复发起整条前向+反传链。正确姿势是一次调用拿全部分量再逐列 extract。**其三，拉普拉斯双方法**：`std` 走 Hessian 迹（pina/_src/core/operator.py:239-248），`divgrad` 先求梯度再对梯度张量求散度（pina/_src/core/operator.py:250-265），数学等价但计算图形状不同，给不同后端留了选择。批判视角：无条件 `create_graph=True + retain_graph=True`（pina/_src/core/operator.py:90-91）意味着整个训练期反传图常驻，高维问题的内存代价显著，而库没有提供 no-create-graph 的一阶专用路径；`allow_unused=True`（pina/_src/core/operator.py:92）在输入确实未被使用时静默返回 None，报错被推迟到取列那一步（pina/_src/core/operator.py:95），排错距离拉长；vector 逐分量 Python 循环（pina/_src/core/operator.py:154-160）未用 functorch/vmap 矩阵化，d 维输出的反传次数随 d 线性增长。

## 6. 新人提示

第一铁律：输入输出必须是 LabelTensor，普通 tensor 在 `_check_values` 就被拦下（pina/_src/core/operator.py:46-51）。写自定义方程时记住列名协议——想取 du/dx 就 `extract("dudx")`，二阶是 `ddu`，平流是 `adv_u`；这些名字不是文档约定而是 L150/L229/L313 的硬编码。热路径（残差函数内）优先用 fast 系列，但必须自备 list 形式的 components/d 且自己保证标签合法——校验全部免去是它的契约。若训练 OOM，先查是不是在循环里对同一输出反复调 grad：合并成一次调用、一次 backward，常有多倍速差。

*不计空格字符数：3,850；行号锚引用：34 处（全部经 sed/grep 逐条核实）*
