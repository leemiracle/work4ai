# 08 · pina/_src/model/deeponet.py —— MIONet 与 DeepONet 同居一文件：分支-干算子网络的组合数学

## 角色定位

这是 model 子系统"神经算子线"的核心文件（486 行，model 层内聚度最高的单文件之一），实现从**函数到函数**的算子映射：不学一个解，而学"一族传感输入 → 一族解"的映射规律。它承载一个勘误级事实：**文件名叫 deeponet，基类却是 `MIONet`**（pina/_src/model/deeponet.py:9），大名鼎鼎的 `DeepONet(MIONet)` 要到 L324 才登场、且只是双分支特化——按文件名找"DeepONet 的实现"会在前 320 行扑空。两者由 pina/model/__init__.py:26 一行同时导出（`__all__` 见 pina/model/__init__.py:7-8）。它可同时配 Supervised 与 Physics-Informed 求解器训练（MIONet docstring 明言，同文件 L13-15），原始文献锚在类 docstring：MIONet=Jin et al. 2022 SIAM JSC（同文件 L19-22），DeepONet=Lu et al. 2021 Nat Mach Intell（同文件 L334-339）。

## 内部结构

两类共享一套骨架，方法地图如下：

- **`MIONet.__init__(networks, aggregator="*", reduction="+", scale=True, translation=True)`**（同文件 L25）：`networks` 是"子网 → 输入列索引表"的 dict；`self.models = torch.nn.ModuleList(networks.keys())`（L130）与 `self._indeces = networks.values()`（L131）把子网与索引解耦保存；scale/translation 按 `nn.Parameter(torch.tensor([1.0]))` 或普通张量二选一注册（L138-147）。
- **符号 DSL `_symbol_functions`**（同文件 L149-166，staticmethod）：返回 `{"+": sum, "*": prod, "mean", "min", "max", "id"}` 六个 `partial(..., dim=-1)` 函数表；`_init_aggregator`（L168-185）与 `_init_reduction`（L187-204）查表命中或接受自定义 `nn.Module`/函数（L179-180，用 core/utils 的 `is_function` 判定），否则 ValueError。
- **`_get_vars(x, indeces)`**（同文件 L206-235）：str 索引走 `x.extract(indeces)`（L221），对裸 Tensor 触发 AttributeError 时转译成人话 RuntimeError（L222-228）；int 索引走 `x[..., indeces]`（L229-230）。
- **`MIONet.forward(x)`**（同文件 L237-261）：逐子网前向（L248-251）→ `torch.dstack` 堆叠后过 aggregator（L254）→ reduction（L257）→ 若 reduction 是符号函数则 reshape 补尾部维（L258-259）→ `self._scale * output_ + self._trasl` 仿射收尾（L261）。
- **属性区**（同文件 L263-321）：aggregator/reduction/scale/translation/`indeces_variables_extracted`（L303-311）共 5 个只读 property；注意 L313-321 的 `model` property **docstring 写"返回子网列表"、代码却 `return self._indeces`**——复制粘贴级 bug，与 L303 返回同一物。
- **`DeepONet.__init__(branch_net, trunk_net, input_indeces_branch_net, input_indeces_trunk_net, ...)`**（同文件 L343）：仅把两个子网拼成 dict `{branch_net: ..., trunk_net: ...}`（L445-448）后透传 super（L449-455）；`forward` 完全委托父类（L457-466）；`branch_net`/`trunk_net` property 靠 dict 插入序映射 `self.models[0]`/`self.models[1]`（L468-476、L478-486）。

## 外部连接

- **imports 出边 1 条**：仅 `pina/_src/core/utils.py`（pina/_src/model/deeponet.py:6 取 `check_consistency` 与 `is_function`，两者分别定义于 pina/_src/core/utils.py:30 与 :224）——model 层只依赖塔基的纪律在此文件的体现；torch 系 import 不计入图谱子系统边。
- **fan-in 1 条**：pina/model/__init__.py（L26 一行 `from pina._src.model.deeponet import DeepONet, MIONet`）。
- **tested_by 2 条**：tests/test_model/test_deeponet.py（8 个测试：构造 L16、str 提取前向 L29、int 提取前向 L44、int 提取反传 L58 等）与 tests/test_model/test_mionet.py（7 个测试：构造 L13、str/int × 前向/反传四组合 L21-L62）。两套测试的命名直接对应 `_get_vars` 的两条路径（L219-230），可当最简用例抄。

## 数据流

以 DeepONet 监督训练一个 forward 步为例走读：输入是带标签的 LabelTensor，列里混着传感器的函数离散值（如 `["u0", ..., ]`）与查询坐标（如 `["x", "t"]`）。`forward(x)`（同文件 L457）直落 `MIONet.forward`：第一步 `_get_vars` 按构造时的索引表把 branch 列与 trunk 列分别切出来（L249）——这就是"分支吃传感函数、干网吃查询点"的物理含义；第二步各子网独立前向得 branch 特征 `b ∈ R^p` 与 trunk 特征 `t ∈ R^p`（要求两子网 output_dimensions 相同，同文件 L360 有约定）；第三步 `torch.dstack` 把 N 个子网输出堆成 `[batch, p, N]`（L254），aggregator `"*"` 即逐元素积——对 DeepONet（N=2）就是 `b_i · t_i` 的按位乘；第四步 reduction `"+"` 沿特征维求和（L257）得内积 Σᵢ bᵢtᵢ，正是 DeepONet 的基函数展开 Σᵢ cᵢ(b) ψᵢ(t)；第五步补一维输出（L259）、乘可学习 scale 加 translation（L261）。梯度经两子网与 scale/translation 三个可学习来源反传。MIONet（N>2）的 `"*"` 把内积推广为多因子逐位积——对应其论文标题里的 tensor product（同文件 L20）。

## 设计决策（含批判视角）

- **继承方向倒置是刻意设计**：MIONet 是数学上更一般的"多输入算子"，DeepONet 退化特化只需覆盖构造签名——代价是 API 认知负担：新人 grep "class DeepONet" 会先撞见 320 行 MIONet 代码。若追求可读性，拆两文件或至少在文件头 docstring（L1）点名两者关系更好。
- **符号 DSL + 自定义可调用**的 aggregator/reduction（L149-166）让组合方式可扩展（甚至可微，若传 nn.Module），是本文件最优雅的部分；但 forward 里 L258 每步重建函数表做成员判定，属微小的重复计算坏味道。
- **docstring 与代码漂移**：`__init__` docstring 承诺 "ValueError: If the passed networks have not the same output dimension"（同文件 L62-63），但构造代码（L119-147）没有任何输出维校验——维数不匹配会在训练第一步 `torch.dstack`（L254）处才炸，报错离病因很远。docstring 亦自认 forward 不查输入类型（L65-72 warning），裸 Tensor 配 str 索引只能在运行时靠 `_get_vars` 的转译报错兜底（L222-228）。
- **两个实现级 bug/笔误值得留意**：`model` property 返回错对象（L313-321，应 return `self.models`）；`_trasl` 拼写（L143，应为 `_transl`）。后者私有无伤大雅，前者会直接误导调用方。
- **translation 初始化为 1.0 而非 0.0**（L143-147）：默认输出 = 1·Σ+1，初始即带偏置 1——与"translation"直觉相悖，复现论文数值或对比基线时注意这个 warm-start 偏差；好在两个仿射参数都可选关闭（构造传 `scale=False/translation=False` 变普通缓冲）。
- **批判：单标量 scale/translation** 只能整体缩放平移，不能逐输出维自适应；多输出算子任务里表达能力受限，需要时应在外部自行归一化数据。

## 新人提示

1. 最小可跑样例直接抄 tests/test_model/test_deeponet.py:16-27：两个 FeedForward（output_dimensions 相同！）+ str 索引表即可构造；配 physics-informed 训练时把 `Condition(domain=..., equation=...)` 照常挂 problem，模型侧无需改动。
2. 子网输出维 p 是"基函数个数"旋钮：p 大表达强但易过拟合，从 20-40 起调；branch 网吃传感采样、trunk 网吃查询坐标，两网的 input_dimensions 由你的标签列数决定。
3. 记住 L313 的 `model` property 是坏的——取子网请用 `model.models`（ModuleList）或 DeepONet 的 `branch_net`/`trunk_net` property（L468-486）。
4. 调 dstack 形状错误时先逐个打印子网输出 shape：十有八九是两子网 output_dimensions 不一致，而构造期不会替你发现（见上文 docstring 漂移）。

---
*自报：不计空格字符数 4,580；仓根全路径 `文件:行号` 锚 6 处 + 「同文件 LNN」行引用 13 处，全部经 Read/grep 对 commit 60ea474a 逐条核实。*
