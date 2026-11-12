# 03 · pybind.cpp 与 tensor/——PyTorch 注册面与量化张量族

> 源文件：`transformer_engine/pytorch/csrc/extensions/pybind.cpp`（846 行，165 个 m.def）+ `transformer_engine/pytorch/tensor/`（8 类共 9346 行）+ `transformer_engine/pytorch/quantized_tensor.py`（基类）。图谱把 pybind.cpp 标注为"common C API→Python"唯一桥，tensor/ 是入度最高的 Python 节点群之一。

## ① 角色定位：这个子系统解决什么问题

common 层只认 C 指针与 NVTETensor，PyTorch 只认 torch.Tensor——pybind.cpp 是两者间唯一粘合层：把 `nvte_*` C API 包成 `transformer_engine_torch` 扩展模块的 165 个 Python 函数。tensor/ 解决另一半：**FP8/FP4 数据以"看起来是高精度"的姿态活在 autograd 图里**——QuantizedTensor 代理类对外伪装 bf16/fp32 张量，对内持有低精度数据+scale_inv+转置缓存，让现有 nn.Module 零改动接入量化。

## ② 内部结构：关键类/函数与行号锚

**注册面（`pybind.cpp`）**：`PYBIND11_MODULE`（`pybind.cpp:193`）开头给 DType 枚举补 `__eq__`（:195，pybind 枚举默认不比较的小补丁）；随后分区注册 `quantize`（:209）与 GEMM/activation 族。MoE fused_topk 单独成函数（:143-190）——:134 注释明言为绕开 cpplint 函数长度上限。NVSHMEM 引导也在此面（:645）。

**基类双壳（`pytorch/quantized_tensor.py`）**：`QuantizedTensorStorage`（`quantized_tensor.py:53`）docstring 写明全族契约：每种类型 X 都要建 `XTensorStorage`（纯数据成员，可脱离 torch 子类独立存在）+ `XTensor`（继承 Storage 与 QuantizedTensor，只实现"像 torch.Tensor 的行为"）。`QuantizedTensor(torch.Tensor)`（:723）经 `_make_wrapper_subclass` 造代理（:751），`dtype` 缓存成成员变量避免属性查找开销（:766）；torch 操作落入 `__torch_dispatch__`（:874），:26 起的白名单让部分自定义 op 直通不脱壳。

**Float8 主类型**：`class Float8Tensor(Float8TensorStorage, QuantizedTensor)`（`float8_tensor.py:440`）是上述契约的实例。Storage 四关键成员（`storage/float8_tensor_storage.py:85-92`）：`_data`（rowwise FP8）、`_transpose`（columnwise 缓存+脏标记）、`_scale_inv`、`_quantizer`。`quantize_`（`float8_tensor.py:507`）遇 QuantizedTensor 输入先 dequantize 再量化（:524）。

**类型矩阵**：MXFP8（`mxfp8_tensor.py:27` Quantizer、:227 Tensor）、NVFP4（`nvfp4_tensor.py:114`、:405，rowwise/columnwise 双开关）、blockwise 2D（`float8_blockwise_tensor.py:28`、:258）、Grouped（`grouped_tensor.py:68`，MoE 变长组）、Identity（`identity_tensor.py:176`，透传类型）、Hybrid（`hybrid_tensor.py:19`、:376，组合两种量化表示）。

## ③ 外部连接：与哪些子系统互依

pybind 的每个 m.def 背后是 pytorch/csrc/extensions/ 的 C++ 翻译层，再向下打到 common 的 `nvte_*`（01/02 篇）。tensor/ 被 `pytorch/module/`（Linear/LayerNorm 消费 quantize_）、`pytorch/ops/`（06 篇）、fp8 API（recipe 状态写 `_scale_inv`）三方消费。Quantizer 与 01 篇 scaling mode 一一对应——Tensor 是配方在 Python 世界的具象。

## ④ 数据流：一次典型调用的路径

Linear 前向量化激活：①module 调 `tex.quantize(tensor, quantizer)`（pybind :209）→C++ 按 quantizer 类型建空量化张量再调 `nvte_quantize_v2`；②返回的 Float8Tensor 持有 `_data`/`_scale_inv`；③GEMM 直接吃 Float8Tensor——`__torch_dispatch__`（`quantized_tensor.py:874`）拦截路由到 tex GEMM，免先反量化；④普通算术时 `dequantize()` 走 autograd 保梯度。

## ⑤ 设计决策：为什么这么设计

**Storage/Tensor 双壳**：autograd Function 内部不需要 torch 子类机制，裸 Storage 零代理开销——docstring 直言是性能优化（:56-59）。**伪装高精度 dtype**：optimizer/checkpoint/DDP 无需感知量化，迁移零成本；代价是 `__torch_dispatch__` 须精确拦截每个操作。**_transpose 脏标记**：TN GEMM 要列主序数据，缓存转置、更新时置 invalid 按需重算。**Hybrid 的存在**：NVFP4 GEMM 两侧需不同方向 scale（rowwise 激活、columnwise 权重），组合类免手工管理。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`quantized_tensor.py:53` docstring（全族契约）→`float8_tensor.py:440`→storage 同名文件对照读。
- **坑一：dtype 是谎言**。`Float8Tensor.dtype` 返回 nominal 高精度（:766），真数据在 `_data`（uint8）。
- **坑二：columnwise-only 时 `_data` 可为 None**（`float8_tensor.py:533` clone 注释），Hopper/L40 只配 `_transpose`——空判断别只查 `_data`。
- **坑三：新增量化类型必须双类成对**，只写 Tensor 不写 Storage 破坏 autograd 性能假设。scale_inv 常在多张量间共享（`clear()` :127 注释），释放别想当然 free 全部。
