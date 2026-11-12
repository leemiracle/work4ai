# Deep-Learning-Accelerator-SW 仓库 ONBOARDING

> 图谱基线：94 节点 / 151 边 / 10 层 / 15 步 tour @ commit 25a39b07（Apache-2.0 relicensed）
> 所有行号锚以该 commit 源码为准。

## 1. 这个仓库是什么（定位）

NVIDIA DLA（Deep Learning Accelerator）是 Orin/Xavier SoC 上的固定功能深度学习加速器：Jetson AGX Orin 双二代 DLA 贡献整机 38%-74% 的 INT8 峰值算力（随功率档位变化），能效比 GPU 平均高 3-5 倍（README.md:25-33）。本仓不是 DLA 编译器/驱动本体（那些闭源在 DRIVE OS/JetPack 里），而是把它们用起来的**配套软件层**，四大件各管一段：

- `operators/` — 算子重建（op reconstruction）：把 DLA 不支持的 ONNX 算子改写成等价的 DLA 支持算子组合；
- `scripts/prepare_models/` — 参考模型准备：MLPerf 系网络的图手术与下载-准备-运行手册；
- `tools/qdq-translator/` — QAT 量化翻译器：Q/DQ 图 → 无 Q/DQ 图 + int8 scale + TRT 校准缓存；
- `samples/cuDLA/` — cuDLA 层级统计样例：Hybrid（CUDA 协同）与 Standalone（纯 NvSci）两种编程模型对照。

一句话：**DLA 部署链上"模型到 loadable"之间所有需要用户动手的图变换，这个仓给出配方与工具**。DLA 编译器把网络图编成 loadable 二进制、运行时栈含固件+内核态/用户态驱动（README.md:8-10），那些通过 TensorRT/NvMedia-DLA/cuDLA 间接调用，不在这个仓里。

## 2. 五分钟上手

宿主机（不需要 Jetson）：

```bash
pip install -r requirements.txt        # onnx/onnxruntime/onnx-graphsurgeon（requirements.txt）
cd operators && python3 test.py        # 全算子回归，期望 11/11 passed
cd scripts/prepare_models && python3 resnet50.py   # 下载的 ONNX → DLA 友好图
```

算子单测可以单独跑：`python3 op_reconstruction/GRU.py`（每个算子文件自带 `main()`）。设备侧（cuDLA 样例）需要 Jetson/DRIVE Orin + TRT 产出的 loadable：`./cuDLALayerwiseStatsHybrid model.bin 1152 1 out` 逐层输出 CSV。

## 3. 架构总览（图谱 10 层）

图谱把 51 个文件分成 10 层，阅读顺序即依赖顺序：

| 层 | 内容 | 关键节点 |
|---|---|---|
| L1 | 文档基座 | README、FAQ、CONTRIBUTING、requirements |
| L2 | 算子重建框架基座 | Operator 基类、BinaryOperator、IndexSelectionOperator、onnxruntime_utils |
| L3 | 注册与测试 | registry.py、test.py、op_reconstruction barrel、支持矩阵 |
| L4-L7 | 四族重建算子 | 布尔/一元（And/Or/Xor/Not/Neg）、重排（DepthToSpace/SpaceToDepth）、索引选择（Gather/ScatterElements/Where）、循环（GRU） |
| L8 | 模型准备 | common.py 图手术 + 5 个模型脚本 |
| L9 | QDQ 翻译器 | qdq_translator.py(732 行) + utils + e2e workflows |
| L10 | cuDLA 样例 | Hybrid main.cu(888 行) + Standalone main.cpp(1338 行) |

Python 侧 import 骨架（34 条边）：11 个算子文件 → 三个基类之一 → Operator.py → onnxruntime_utils.py；`registry.py:21` 的 `RECONSTRUCTOR_REGISTRY` 列表 → `op_reconstruction/__init__.py` barrel → 11 算子。C++ 两个样例互相独立、零项目内 import，是纯 API 教学。

## 4. 核心机制一：算子重建的黄金循环（operators/）

一切从 `Operator` 基类（operators/common/Operator.py:31）开始，它定义了 generate → reconstruct → test 循环：

1. **generate**（Operator.py:37）用 graphsurgeon 造单算子 ONNX 图；
2. **reconstruct**（Operator.py:63）在子类里把节点改写成 DLA 支持的算子（原地改 `node.op` + 注入常量）；
3. **test**（Operator.py:68）保存原图 → 重放 reconstruct → `run_comparison`（Operator.py:156）用 ONNX Runtime 跑两张图取 `maxabsdiff`；
4. 顺带 `save_inputs_and_ref_outputs`（Operator.py:127）导出 fp16/int8 参考数据与 `save_scales`（Operator.py:118）的 int8 scale（`max(|low|,|high|)/127` 对称量化，贯穿全仓）。

三条重建套路（这是本仓最有复用价值的知识）：

- **算子替换+常量注入**：Neg → `Mul` + 追加 -1.0 常量（op_reconstruction/Neg.py:37）；And → `Mul` + bool 转 float32（op_reconstruction/And.py:27）；
- **one-hot 卷积核编码**：SpaceToDepth/DepthToSpace 用 kernel=stride=blocksize 的 one-hot Conv 权重实现像素重排（op_reconstruction/SpaceToDepth.py:28），Gather 用 1×1 one-hot Conv 实现按索引选通道（op_reconstruction/Gather.py:55）；
- **转置对轴归一**：DLA 只支持 channel 维（axis=1）索引，`insert_transposes_if_needed`（operators/common/IndexSelectionOperator.py:29）在节点前后插一对互逆 Transpose 把 axis 2/3 搬到 channel 位再复原。

GRU 是复杂度天花板（op_reconstruction/GRU.py:31，508 行）：`reconstruct_step`（GRU.py:176）逐时间步展开，`add_gru_conv/act/elementwise` 等静态方法搭 Conv+Sigmoid/Tanh+Mul 积木。它是唯一浮点容差非零的算子——`MAXABSDIFF_THRESHOLDS['GRU'] = 1e-6`（operators/test.py:23），其余算子默认 0.0（位级等价，test.py:22）。

## 5. 核心机制二：量化翻译（tools/qdq-translator/）

QAT（量化感知训练）产出的 ONNX 带 QuantizeLinear/DequantizeLinear 节点对；DLA 部署链（老版本 TensorRT/直接喂 DLA 编译器）需要的是**裸图 + 每张量 int8 scale**。`QATModelParser`（qdq_translator.py:99）干的就是这个翻译：

- `get_quantized_tensor`（qdq_translator.py:118）：区分权重量化器（per-channel，scale 为 Variable）与激活量化器（per-tensor），并兼容 TF 导出的 Constant 形态——两个 `_fake_quantize_*_err_hint` 常量是 PyTorch/TF 导出姿势错误的官方修复指引；
- `verify_weight_scales`（qdq_translator.py:204）：按 TensorRT 的口径（逐行 dyn_range/127，MatMul 需转置）反推 scale 校验一致性，容差 `WEIGHT_SCALE_TOLERANCE=1e-3`；
- `extract_precision_config`（qdq_translator.py:335）决定哪些层保 fp16（`--layerPrecisions` 参数）；`parse`（qdq_translator.py:612）是总入口，产出无 QDQ ONNX + scale JSON；
- `export_to_trt_calib`（utils.py:28）把 scale 按 IEEE754 十六进制（`float_to_hex`，utils.py:22）写成 `TRT-8600-EntropyCalibration2` 头的 calib cache。

默认相邻算子传播集合 `DEFAULT_OPS_TO_INFER_ADJACENT_SCALES = {MaxPool, Flatten, Relu, Pad, Transpose, Reshape, Squeeze, Sigmoid}`（qdq_translator.py:33）——这些不改数值的算子可以上下游共享 scale。

## 6. 核心机制三：模型准备与 cuDLA 双模式

**模型准备**（scripts/prepare_models/common.py:22 起）三个招牌变换：垂直融合 `fuse_mul_into_conv`（common.py:22，scale 乘进权重）/`fuse_add_into_conv`（common.py:36，折成 bias）；**水平融合** `fuse_convs_horizontally`（common.py:63）把多条同属性 Conv 分支按输出通道拼成一个大 Conv——DLA 上提 batch 吞吐的关键；`simplify_classification_head`（common.py:130）把 GAP+MatMul 链换成 DLA 友好形态。五个模型脚本（ResNet-50 双版/RetinaNet/SSD×2）按 `scripts/prepare_models/README.md` 的下载-准备-trtexec 手册串起来。

**cuDLA 双模式**是同一功能的两套内存/同步模型，对照读收获最大：

| | Hybrid（main.cu:219） | Standalone（main.cpp:461） |
|---|---|---|
| 设备 | `cudlaCreateDevice(..., CUDLA_CUDA_DLA)`（main.cu:305） | `cudlaCreateDevice(..., CUDLA_STANDALONE)`（main.cpp:526） |
| 内存 | cudaMalloc + `cudlaMemRegister` 包装 | NvSciBufAttrList Reconcile + `NvSciBufObjAlloc`（main.cpp:905） |
| 同步 | CUDA stream（`cudlaSubmitTask` 带 stream，main.cu:697） | NvSciSync fence + CpuWaitContext 阻塞等待 |
| 依赖 | CUDA toolkit | 只需 NvSci（findnvsci.mk 探测路径） |

两者都用 `cudlaModuleGetAttributes` 枚举输入/输出/统计张量描述符（main.cu:345，main.cpp:554），逐层 submit 后输出 `layer_name,start_ms,end_ms` CSV——DLA 上做逐层 profile 的标准姿势。

## 7. 如何验证与扩展（工作流）

- **跑回归**：`operators/test.py` 的 `test()`（test.py:37）遍历 `RECONSTRUCTOR_REGISTRY`（registry.py:21），按阈值分桶 passed/failed 并 `log_results`（test.py:27）汇总通过率；
- **加新算子重建**：继承三个基类之一 → 实现 `reconstruct` 类方法 + `test` 实例方法 → 在 `op_reconstruction/__init__.py` 导出 → 加进 `RECONSTRUCTOR_REGISTRY` → 跑 test.py；先查 `operators/README.md` 的支持矩阵确认 TensorRT 列状态（Native/Reconstruction/RFE）；
- **复现精度基线**：按根 README 的表（RetinaNet mAP 0.3741 vs GPU 0.3740 等）对齐你的量化流程；
- **确定性**：`operators/__init__.py:21` 固定 `np.random.seed(0xdeadbeef)`，Gather/ScatterElements 的随机索引可复现。

## 8. 坑与勘误（新人必读）

1. **`op_reconstruction/` 脚本是配方不是运行时库**：官方说明（operators/README.md:19 附近）明确它们示范"如何在 ONNX 域后训练重建"，你也可以选择在训练框架内做等价变换——不要把它当成部署依赖；
2. **DLA SW 与 TensorRT 是两条版本线**：支持矩阵双列常出现"DLA SW 已 Native、TensorRT 列 RFE"（如 Acos as of DLA 3.14.0）——软硬两栈解耦，升级 JetPack 不等于 TRT 暴露跟上；
3. **GPU 与 DLA 不产生位级一致结果**（README 明示），算子重建的 0.0 阈值是"重建前后 ONNX 图"等价，不是 GPU vs DLA 等价；
4. **QDQ Translator 有最低版本门槛**：DLA 用途需 DLA SW ≥ 3.13.0（tools/qdq-translator/README.md:8 附近）；
5. **裸名 `test.py` 的坑**：merge 工具的测试文件判定只认 `test_` 前缀/`_test` 后缀，`operators/test.py` 不匹配（所以图谱里 registry→test 的 tested_by 边被工具判 prod↔prod 丢弃，测试关系保留在 imports 边里）——你重命名它反而会破坏 README 指引；
6. **样例 C++ 的 cleanUp 极长**（main.cpp:102-377，276 行）不是坏味道：cuDLA/NvSci 句柄类型多、失败路径都要安全释放，这是嵌入式资源管理的常态；
7. **Standalone 的内存协调是概念门槛**：NvSciBufAttrListReconcile 是"CPU 与 DLA 双方约束求交"再分配（createAndSetAttrList，main.cpp:384），理解它才能读懂零拷贝为什么成立。

## 9. 延伸阅读（图谱 tour 入口）

知识图谱 tour 15 步（`/usr-data/data2/repos/agent-repos/NVIDIA/Deep-Learning-Accelerator-SW/.understand-anything/knowledge-graph.json`）按 T01→T15 走：文档定位 → 支持矩阵 → Operator 循环 → 数值裁判 → 三族算子 → GRU → 测试台 → 模型准备 → QDQ 翻译 → e2e 工作流 → cuDLA 双模式。配合本目录 `../explain/` 五篇精讲食用。
