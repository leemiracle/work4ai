# 10 · onnx-graphsurgeon：图手术 IR、惰性求值与 Layer API

> 图谱锚：L14「onnx-graphsurgeon 图手术库」（82 节点）。源码根 `tools/onnx-graphsurgeon/onnx_graphsurgeon/`（ir/importers/exporters 三域 + 12 组示例）。

## 一、角色定位

gs 是「直接用 Python 对 ONNX 图做外科手术」的库：TRT 部署管线里 90% 的预处理步骤——裁剪子图、折叠常量、替换自定义算子（如第 12 篇 DeBERTa 的 DisentangledAttention_TRT 注入）、改动态 batch——都靠它完成。它刻意**不用**重型图框架抽象：`import onnx_graphsurgeon as gs` 后你拿到四个核心类（Graph/Node/Variable/Constant），操作语义接近「拿张量引用直接连线」的伪代码。对上是仅依赖 onnx+numpy 的纯 Python 库；对下是 Polygraphy surgeon 工具族与各 TRT 插件 demo 的图改造底座。

## 二、内部结构

入口 `onnx_graphsurgeon/__init__.py:1-8` 以 from-import re-export 汇聚全部公共 API（export_onnx/GraphPattern/Function/import_onnx/Graph/Node/Tensor 族/异常），是 examples 与外部用户唯一的 import 面。

- **ir 三件套**：`ir/tensor.py:25` `Tensor` 基类 → tensor.py:171 `Variable`（图中的边）与 tensor.py:392 `Constant`（initializer）；`ir/node.py:27` `Node`（算子+属性+张量引用）；`ir/graph.py:45` `Graph` 聚合 nodes/tensors/inputs/outputs/opsets，graph.py:30 `NodeIDAdder` 派发唯一 ID。
- **Layer API**：`Graph.register` 装饰器（graph.py:55，register_func 在 graph.py:78）把算子函数动态注入 Graph 类——`@Graph.register()` 后 `graph.relu(...)` 链式构图成为可能（examples/01 主题）；`Graph.__setattr__`（graph.py:204）保证 tensors 集合随属性赋值同步。
- **图手术核心方法**：`Graph.cleanup`（graph.py:384，内嵌 cleanup_subgraphs graph.py:416 递归处理 If/Loop 子图）做拓扑排序+死代码消除+去孤儿；`fold_constants`（graph.py:696）按需拉起 onnxruntime 折叠（延迟 import）。
- **importers/exporters**：`importers/onnx_importer.py:552` `import_onnx` 唯一入口，配套 `get_onnx_tensor_shape`（onnx_importer.py:64）/`get_itemsize`（onnx_importer.py:91）/`get_numpy_type`（onnx_importer.py:113）桥接函数族；`exporters/onnx_exporter.py:41` `dtype_to_onnx` 反向桥接，onnx_exporter.py:76 `check_duplicate_node_names` 查重名。
- **本篇甄别（死代码）**：`get_onnx_tensor_type` 在 onnx_importer.py 中**逐字重复定义两次**（onnx_importer.py:170 与 onnx_importer.py:194，函数体完全相同）——Python 后定义覆盖前定义，第一份纯死代码，上游遗留原样保留。

## 三、外部连接

上游硬依赖仅 onnx/numpy；`graph_pattern.py` 的 GraphPattern 提供 DSL 式子图形状描述（Polygraphy `tools/surgeon/subtool/weight_strip.py` 用它声明可剥离子图）。下游：Polygraphy 全部 surgeon/convert 工具、demo/DeBERTa 图修改脚本（第 12 篇）、TRT 各插件 README 里"图修改脚本"的落点。examples 12 组（01 创建模型 → 12 numpy 不支持 dtype）是官方教学资产：07 演示同名算子按 opset 分版本注册（`opsets=[11]` 与 `opsets=[1]` 各一份，后者对本图永不生效）；08 的 min/max 层函数名刻意遮蔽 Python 内置；11 覆盖 Function 三特性（AttributeRef 按名引用、attrs 默认值入 attribute_protos、子图复用）。

## 四、数据流

`import_onnx(model_proto)`：OnnxImporter（onnx_importer.py:218）遍历节点与张量表，**常量不立即物化**——包成 `LazyValues`（`ir/tensor.py:222`）：其 `__init__`（tensor.py:232 起）内延迟 import `get_onnx_tensor_shape/get_onnx_tensor_dtype/get_itemsize` 三函数（规避 ir↔importer 循环依赖，NOTES batch-15 钉版），只预计算 shape/dtype/nbytes；取值时才转 numpy。稀疏常量走 `SparseValues`（tensor.py:274）。用户改图后 `export_onnx`：onnx_exporter.py:190-192 对 LazyValues **直通原始 TensorProto 字节**避免二次拷贝；FP4 数组因 numpy 导入后字节翻倍须 `onnx.numpy_helper._pack_4bitx2` 重新打包（onnx_exporter.py:174）；`Node.AttributeRef`（onnx_exporter.py:243 分支）为绕 Netron 空 tensor 崩溃 bug 塞入 dummy 数据——导出器藏着对下游工具缺陷的兼容层。

## 五、设计决策

1. **惰性常量是命门**：LLM 时代 ONNX 图动辄数百 MB 权重，导入即物化会把 gs 变成内存炸弹；LazyValues 惰性求值 + 导出直通，两头都不过 numpy。
2. **循环依赖靠函数内延迟导入化解**：ir 层与 importer 互相引用，gs 的解法是使用点延迟 import——小库务实选择，代价是静态分析需手补边。
3. **Node 持张量引用而非 ID**：`node.inputs[0] = new_tensor` 天然生效，无需图级 rebuild——图 surgery 的高频操作是重连边。
4. **register 装饰器做猴子补丁式 API 扩展**：算子族可无限扩展而不膨胀 Graph 本体；tests/models/make_models.py 用同机制注入测试算子。
5. **onnxruntime 只在 fold_constants 需要时加载**：保持纯图改场景零 ORT 依赖。

## 六、给新人的提示

学习路径就是 examples 01→12 顺序刷（每组 <100 行带注释）。改图铁律：动过结构必调 `graph.cleanup()`，否则残留孤儿张量让导出失败或 TRT 解析报未知节点。调试用 `graph.print()` 先看结构再动手。踩 FP4/FP8 新 dtype 导出问题先看 onnx_exporter.py:174 的打包分支；Netron 显示异常记得 onnx_exporter.py:243 附近塞过 dummy 数据。往上游提 PR 前先跑 `tests/`——量化联动场景有二进制向量回归对照。
