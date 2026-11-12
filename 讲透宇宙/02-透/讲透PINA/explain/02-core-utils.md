# 02 · pina/_src/core/utils.py —— 塔基工具集：全库第二高 fan-in 的无状态函数层

## 1. 角色定位

`pina/_src/core/utils.py`（306 行）是依赖金字塔塔基的核心工具集：十个纯函数、零类、零全局状态，唯一的 import 依赖是 `LabelTensor`（pina/_src/core/utils.py:7）与 torch/标准库。图谱统计其 imports 入边 95 条，全库第二高（仅次于门面）——被 model 族（rbf_block、fourier_neural_operator、pirate_network 等几乎全部模型文件）、domain 采样、condition 校验广泛消费。它提供三类原语：**类型校验协议**（check_consistency 一族）、**采样数学**（torch_lhs、chebyshev_roots）、**张量组合**（merge_tensors 一族）。一个必须先钉的消歧事实：顶层 `pina/utils.py` 是同名转发 shim，只 re-export 其中 3 个符号（pina/utils.py:9-13：merge_tensors/check_consistency/check_positive_integer）——本篇讲的是 `pina/_src/core/utils.py` 实现，两者不是同一文件。

## 2. 内部结构

函数地图（图谱 contains 摘要列了 9 个，源码实证实为 10 个——`is_function` 被图谱漏计）：

| 行号 | 函数 | 簇 |
|---|---|---|
| pina/_src/core/utils.py:11 | `custom_warning_format` | 杂项：警告单行化 |
| pina/_src/core/utils.py:30 | `check_consistency` | 校验 |
| pina/_src/core/utils.py:96 | `labelize_forward` | 张量：前向装饰器 |
| pina/_src/core/utils.py:135 | `merge_tensors` | 张量：笛卡尔合并 |
| pina/_src/core/utils.py:161 | `merge_two_tensors` | 张量：合并私有核 |
| pina/_src/core/utils.py:182 | `torch_lhs` | 采样：拉丁超立方 |
| pina/_src/core/utils.py:224 | `is_function` | 校验 |
| pina/_src/core/utils.py:235 | `chebyshev_roots` | 采样：切比雪夫节点 |
| pina/_src/core/utils.py:255 | `check_positive_integer` | 校验 |
| pina/_src/core/utils.py:274 | `in_range` | 校验 |

`check_consistency(object_, object_instance, subclass=False)` 的四象限协议是本文件的灵魂：非容器输入先包成 list（pina/_src/core/utils.py:53-54）；`subclass=True` 分支要求传入的是类且为目标类的子类（pina/_src/core/utils.py:64-79）；默认分支则相反——传了类会直接报错"要实例不要类"（pina/_src/core/utils.py:81-86）。四条错误消息全部带期望类型名与实际类型名，格式统一。

## 3. 外部连接

imports 出边仅 1 条：`label_tensor.py`（merge_tensors 的返回类型、labelize_forward 的 extract 都依赖它）。入边 95 条，消费主力是 `_src/model/`（block 与算子家族逐文件 import check_consistency 做构造参数校验），其次是 domain（torch_lhs/chebyshev_roots 被 CartesianDomain 的 lh/chebyshev 采样模式调用）。tested_by 出边 1 条指向 `tests/test_utils.py`。顶层 shim `pina/utils.py` 是它的公共 API 出口，但注意 shim 只转发 3/10——`torch_lhs`、`chebyshev_roots` 属于"内部基元"，用户侧只能经 `problem.discretise_domain(mode="lh")` 间接触达。

## 4. 数据流

走读 `discretise_domain(mode="lh")` 到 torch_lhs 的调用链：domain 层解析出每维的 n 与 dim 后调 `torch_lhs(n, dim)`（pina/_src/core/utils.py:182）。内部三步：先 `torch.rand(size=(n, dim))` 撒均匀噪声（pina/_src/core/utils.py:209）；再构造每维的 1..n 整数行并用 `torch.randperm` 逐维随机换列（pina/_src/core/utils.py:211-215）——这保证每维每层恰好一个点，是 LHS 的分层本质；最后 `(perms - samples) / n`（pina/_src/core/utils.py:219）把"层内均匀噪声"折算成 [0,1) 坐标。返回普通 tensor，由上层包成 LabelTensor。再看 grid 模式的合并链：各维独立采样后 `merge_tensors` 用 `reduce(merge_two_tensors, tensors[1:], tensors[0])` 折叠（pina/_src/core/utils.py:157）；`merge_two_tensors` 的外积核是 repeat 配对——tensor1 `repeat(n2,1)` 整块复制、tensor2 `repeat_interleave(n1)` 逐点复制（pina/_src/core/utils.py:175-177），二者对齐后 `append` 拼列（pina/_src/core/utils.py:179），得到 n1×n2 全组合网格。

## 5. 设计决策

设计上最值得学的是**校验协议中心化**：全库几十个构造器的参数检查收敛到一个函数、一套错误文案，用户在任何子系统踩坑看到的是同一种报错——这是 fan-in 95 的正当性来源，而非"工具箱贪多"。`labelize_forward` 展示了对 torch.compile 的工程妥协：直接 `LabelTensor(output)` 会编译报错，改为 `output.as_subclass(LabelTensor)` 再补 labels（pina/_src/core/utils.py:126-129，源码注释明说）。批判视角有三：其一，`check_positive_integer` 用裸 `assert`（pina/_src/core/utils.py:264-271），`python -O` 下校验整段蒸发——同一文件里 check_consistency 抛 ValueError、这里用 assert、in_range 又是"check_consistency+assert+返回 bool"三种风格混搭（pina/_src/core/utils.py:295-299），错误处理协议并不如表面统一；其二，`in_range` 的 docstring 声称 strict 控制"strictly positive"，实现却是 `(lower, upper)` 开闭区间（pina/_src/core/utils.py:303-306），文档语义漂移；其三，merge 的外积实现内存峰值 n1×n2×dim，高维 grid 采样会翻倍放大，无分块策略。

## 6. 新人提示

写自定义 model/block 时，构造器第一行学仓内惯例先 `check_consistency`，报错信息免费获得统一风格。想直接实验采样算法，import 路径是 `from pina._src.core.utils import torch_lhs`（顶层 shim 没有）；日常用户只需记住 `"lh"` 模式即"每维分层各一点"，比 `"random"` 低离散度。调试 LabelTensor 丢失标签的问题时，优先怀疑未经 labelize_forward 包装的裸 forward。最后：改这个文件影响 95 个下游文件，动一行前先跑 tests/test_utils.py 建立基线。

*不计空格字符数：3,524；行号锚引用：26 处（全部经 sed/grep 逐条核实）*
