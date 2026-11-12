# 01 · 算子重建框架：Operator 黄金循环与三个基类

> 文件：`operators/common/Operator.py`、`BinaryOperator.py`、`IndexSelectionOperator.py`、`onnxruntime_utils.py`
> 图谱层：L02 算子重建框架基座 | tour 步：T03/T04

## 角色定位

DLA 是固定功能加速器，只认 Conv/Scale/ElementWise 等一小撮算子；真实网络里的 And/Xor/Gather/GRU 怎么办？这个框架的回答是：**在 ONNX 图域把它们改写成 DLA 支持算子的等价组合**，并用 ONNX Runtime 双图对比证明"等价"不是嘴上说说。operators/README.md:19 附近明确说这些脚本"是配方"——你可以在部署前照抄，也可以在训练框架里做同样变换。

## 内部结构

核心是 `Operator` 基类（Operator.py:31）的黄金循环：

- `generate`（Operator.py:37）：graphsurgeon 造单算子图，`gs.Node(op=类名)` 让子类零成本复用；
- `reconstruct`（Operator.py:63）：类方法，在子类原地改 `node.op`、注入常量、插节点；
- `test`（Operator.py:68）：保存原图 → 重放 reconstruct → `run_comparison`（Operator.py:156）双图推理取 `maxabsdiff`；
- `save_gs_graph`（Operator.py:90）静态落盘（可选 shape inference），`save_scales`（Operator.py:118）按 `max(|low|,|high|)/127` 产 int8 对称量化 scale，`save_inputs_and_ref_outputs`（Operator.py:127）导 fp16/int8 参考 IO。

两个特化基类各切一族：`BinaryOperator`（BinaryOperator.py:25）把布尔二元算子的 generate 强制 `dtype=bool`、test 改为显式真值表输入；`IndexSelectionOperator`（IndexSelectionOperator.py:25 起）给 Gather/Scatter 类提供 `insert_transposes_if_needed`（IndexSelectionOperator.py:29）——DLA 只支持 channel 维索引，axis=2/3 的节点前后插一对互逆 Transpose 把目标轴搬到 axis=1 再复原。

## 外部连接

数值裁判是 `onnx_inference`（onnxruntime_utils.py:25）：薄封装 InferenceSession，dtype 映射表白名单只有 bool/float32。上游消费者是 `registry.py:21` 的 `RECONSTRUCTOR_REGISTRY`（11 算子）与 `test.py` 回归台；`operators/__init__.py:21` 的 `np.random.seed(0xdeadbeef)` 保证随机索引造图可复现。

## 数据流

一个 And 节点的旅程：`generate` 造 bool 图 → `reconstruct`（And.py:27）把 op 改 Mul、全部 tensor 转 float32 → 双图各跑一次 onnxruntime → `maxabsdiff` 对照阈值。GRU 之外的所有算子阈值是 0.0（test.py:22 的 defaultdict 默认）——重建必须做到位级等价，这比"近似等价"要求苛刻得多，也解释了为什么重建套路都是精确代数变换而非数值拟合。

## 设计决策

- **图域重建而非运行时 fallback**：GPU 上不支持的算子可以 fallback 回 GPU，DLA 路线选择在进 DLA 编译器前就消灭不支持算子——换来的是整图驻留 DLA 的确定性延迟；
- **原地改写而非生成新图**：`reconstruct` 直接改传入节点，降低图重建成本，也要求所有变换保持拓扑有效；
- **三个基类按"数据形态"而非"算子类别"切分**：bool 族/索引族/通用族，新算子几乎总能对号入座。

## 新人提示

读代码顺序建议 Neg（最小范例：Neg.py:37 三行核心，Mul + (-1.0) 常量）→ And → SpaceToDepth（one-hot Conv，SpaceToDepth.py:28）→ Gather（转置对 + one-hot 1×1 Conv，Gather.py:55）。注意 `qualifies_for_reconstruction` 的守门逻辑常比重写本身更长——Gather 要求输入数=2、索引为 Constant、axis∈{1,2,3}，条件不满足就静默跳过，调试"为什么没重建"先查这里。
