# MinkowskiEngine 新人导览（ONBOARDING）

> 图谱：832 节点/1812 边/12 层/14 步 tour，commit `02fc608b`；行号锚均已核实。

## ① 项目一句话定位与技术栈

MinkowskiEngine 是 NVIDIA 开源的**高维稀疏张量神经网络自动微分库**：把"坐标矩阵 C + 特征矩阵 F"的 COO 表示推广到任意 D 维空间（3D 点云、4D 时空），提供 GPU 加速的稀疏卷积/池化/广播/插值/剪枝算子。技术栈：PyTorch 前端 + pybind11 + C++14/CUDA 后端（CPU 走 OpenMP，GPU 走 cuBLAS/cuSPARSE）。版本 0.5.4（`MinkowskiEngine/__init__.py:L25`），支持纯 CPU 编译（`setup.py:L126`）。

**版本口径三冲突（第一坑）**：`requirements.txt:L2` 写 `torch>=1.4,<1.7`，`README.md:L63` 要求 >= 1.7，`docker/Dockerfile:L5` 钉 1.12.0，`setup.py:L285` 又按 `torch.__version__ < "1.7.0"` 分支——requirements 是陈旧快照，以 README 与 setup.py 为准。

## ② 总体架构：12 层从底到顶

- **L02 vendored 底座**：GPU 并发哈希表（`src/3rdparty/concurrent_unordered_map.cuh:L131`）、桶容量预估（`src/3rdparty/hash/helper_functions.cuh:L40`）、robin_hood、NVTX——零外部依赖。
- **L03 类型与数学基座**：`src/types.hpp:L57` 定型全仓标量（uint32 索引/int32 坐标/float 特征）；八元组缓存键（`src/types.hpp:L183`）；`gpu_gemm` 走 cuBLAS（`src/math_functions.cuh:L37`）；网格步进宏（`src/gpu.cuh:L134`）。
- **L04 坐标图与 kernel map（引擎心脏）**：`CoordinateMap` 基类（`src/coordinate_map.hpp:L107`）+ CPU/GPU 双实现 + `CoordinateMapManager`（`src/coordinate_map_manager.hpp:L87`）+ 两版 kernel map 容器（`src/kernel_map.hpp:L46` / `src/kernel_map.cuh:L48`）。
- **L05/L06 算子内核**：稀疏卷积与转置卷积（Direct-GEMM vs Copy-GEMM）+ 池化/广播/插值/剪枝，全部复用 L04 的 kernel map。
- **L07 pybind11 桥**：`pybind/extern.hpp` 集中声明全部算子模板（唯一接口契约）；`pybind/minkowski.cpp:L36` 产出 `MinkowskiEngineBackend._C`。
- **L08 Python 前端**：Tensor/SparseTensor/TensorField 三件套、CoordinateManager 包装、`get_minkowski_function` 调度、全套 nn.Module 算子。
- **L09 外围工具**：量化/批整理/gradcheck、MinkowskiOps 聚合与 dense↔sparse、spmm（`MinkowskiEngine/sparse_matrix_functions.py:L32`）。
- **L10 示例/L11 测试/L12 文档**为消费者；**L01 构建配置**横跨全栈。

高扇入枢纽（动则全量重编）：`MinkowskiEngine/__init__.py`（fanIn 50）、`src/types.hpp`（44）、`src/utils.hpp`（39，timer 在 `src/utils.hpp:L40`）、`MinkowskiEngine/MinkowskiSparseTensor.py`（28）。

## ③ 核心数据流：一次 stride-2 卷积的端到端链路

1. **量化**：`sparse_quantize`（`MinkowskiEngine/utils/quantization.py:L136`）按 quantization_size 体素化去重（哈希在 L32/L49）。
2. **建 SparseTensor**：`__init__`（`MinkowskiEngine/MinkowskiSparseTensor.py:L122`）三选一路径；给坐标数组时先造空键（L272），`initialize_coordinates`（L293）调 `insert_and_map` **去重插入**；`self._F`/`self._C` 落位（L284-286）。
3. **管理器持有真图**：`CoordinateManager`（`MinkowskiEngine/MinkowskiCoordinateManager.py:L107`）按设备动态实例化 `_C.CoordinateMapManager{CPU,GPU_default,GPU_c10}`（L146），默认 c10 分配器（L46）。GPU 坐标图核心 `concurrent_unordered_map`（`src/coordinate_map_gpu.cuh:L65`），CPU 是 robin_hood（`src/coordinate_map_cpu.hpp:L296`）。
4. **Python 调度**：autograd Function（`MinkowskiEngine/MinkowskiConvolution.py:L44`）经 `get_minkowski_function`（L71，实现于 `MinkowskiEngine/MinkowskiCommon.py:L110`）按设备拼后缀从 `_C` 动态取函数——全引擎派发咽喉。
5. **输出坐标图生成**（`src/convolution_gpu.cu:L86-113`）：`stride_tensor_stride` 算输出 stride（L93）；`expand_coordinates` 走 `stride_region`（L107）否则 `stride`（L112）；`CoordinateMapKey` 惰性绑定（`src/coordinate_map_key.hpp:L44`）——先建层、前向才绑真图。
6. **kernel map 查询**：`p_map_manager->kernel_map(...)`（`src/convolution_gpu.cu:L117`；CPU 在 `src/convolution_cpu.cpp:L110`）。八元组键查缓存 `m_kernel_maps`（`src/coordinate_map_manager.hpp:L544`）——同参数层直接复用，性能命门（`docs/guides.md:L7`）。映射本体是 (kernel_id, in_row, out_row) 三列。
7. **特征计算**：`check_direct_gemm_forward`（`src/convolution_kernel.cu:L46`）按经验规则二选一——Direct-GEMM 直接做共享内存分块 matmul（kernel L115-116，`__shared__` L146）；Copy-GEMM 先 gather 再 cuBLAS。
8. **反向**：`ConvolutionBackwardKernelGPU`（声明 `src/convolution_kernel.cuh:L53`）复用同一 kernel map 做梯度 scatter。
9. **出口**：`dense()` 稠密化（`MinkowskiEngine/MinkowskiSparseTensor.py:L460`）与 slice/interpolate 逐点采样；`TensorField.splat()` 反向散射（`MinkowskiEngine/MinkowskiTensorField.py:L381`）。

## ④ 关键子系统深潜

**4.1 坐标管理系统**：一套接口双实现（CPU 子类 `src/coordinate_map_cpu.hpp:L283`，GPU 子类 `src/coordinate_map_gpu.cuh:L47`）。Manager 是"图池+双缓存"：`std::map` 按 (tensor_stride, string_id) 持全网络坐标图（`src/coordinate_map_manager.hpp:L107`），kernel map 与 field→sparse 各一张缓存，9 个 detail 仿函数做编译期分派，GPU 按 default/c10 双实例化（L694-698）。**注意**：`docs/terminology.rst:L44` 仍教访问 `coords_man`，真实属性是 `coordinate_manager`（`MinkowskiEngine/MinkowskiTensor.py:L212`）。

**4.2 kernel map 生成**：核区域三型 HYPER_CUBE/HYPER_CROSS/CUSTOM（`src/types.hpp:L137`；十字核生成 `src/kernel_region.hpp:L223`，仅奇数核）。缓存键含 is_transpose：转置卷积交换 in/out 复用普通卷积的 map（`docs/guides.md:L17`）。自定义核形状走 `KernelGenerator`（`MinkowskiEngine/MinkowskiKernelGenerator.py:L245`）；`gpu_kernel_map` 支持分段访问与 thrust decompose。

**4.3 pybind 桥**：`pybind/minkowski.cpp:L46-52` 按 CPU/GPU_default/GPU_c10 三管理器类型批量 `instantiate_manager`；`pybind/minkowski.cu:L38-41` 注册 `is_cuda_available` 等。**已知 bug**：`cpu_div<double>` 误调 `vdMul` 而非 `vdDiv`（`src/math_functions_cpu.cpp:L94`）——CPU 双精度"除法"实为乘法，仅 double 受影响。

## ⑤ 构建与开发工作流：三条构建线

1. **setup.py（主线）**：`--cpu_only`/`--force_cuda`（`setup.py:L126-127`）；`SOURCE_SETS`（`setup.py:L223`）按目标选源文件（同名 .cpp/.cu 双轨绕 Ninja 坑）；产出 `MinkowskiEngineBackend._C`（`setup.py:L312`）。
2. **Makefile（旧线）**：nvcc gencode sm_30–sm_75 九档（`Makefile:L80-88`）产出 libminkowski.a；`CHANGELOG.md:L93` 明言安装已不走它，只服务原生 C++ 调试。
3. **tests/cpp/setup.py（测试线）**：SOURCE_SETS 11 组编译单元（`tests/cpp/setup.py:L34`），`--test=<name>` 选目标（L84），产出 `MinkowskiEngineTest._C`（L120），绕过 Python 层直压 C++。

日常循环：改 src/ 或 pybind/ → `python setup.py install` 重编 → tests/python 回归；只调 C++ 数据结构优先走 tests/cpp 线。

## ⑥ 测试体系与已知陈旧引用坑

- **tests/python**：unittest 覆盖全部算子（convolution/pool/broadcast/interpolation/pruning/kernel_map 等 20+ 文件），梯度校验统一走 `MinkowskiEngine/utils/gradcheck.py`。
- **tests/cpp**：pybind 测试扩展直压 C++（坐标 batch 插入/stride 等），`test_all.sh` 串行 11 目标（`tests/cpp/test_all.sh:L1` 钉 `CXX=g++-7`）。
- **陈旧坑三处**：① `tests/cpp/convolution_gpu_test.py:L9`（及 cpu 版）`from gradcheck import gradcheck`，但 tests/cpp/gradcheck.py 已不存在（搬去了 utils/）——import 即断；② `examples/completion.py:L603` 的 `coords_man`/`create_coords_key`、`examples/vae.py:L437` 的 `get_row_indices_per_batch` 均为 v0.4 旧 API，照抄必 AttributeError；③ 死代码：`MinkowskiEngine/utils/coords.py:L26` 裸模块导入必断（导出在 `MinkowskiEngine/utils/__init__.py:L26` 已被注释）；`MinkowskiEngine/modules/senet_block.py` 的 SELayer 无人消费。

## ⑦ 常见任务入口

**加一个新算子（含前后向）**——五处落笔：① `src/` 新增 `<op>_cpu.cpp`+`<op>_gpu.cu`（+kernel 头），入口照 `src/convolution_cpu.cpp:L84-110` 三段式：生成输出坐标→查 kernel_map→数学内核；② `pybind/extern.hpp` 加声明、`pybind/minkowski.cpp` 注册；③ SOURCE_SETS 两 target 各加一行（`setup.py:L223`）；④ Python 侧 `Minkowski<Op>.py`（autograd Function+nn.Module，模板即 `MinkowskiEngine/MinkowskiConvolution.py:L44`），`__init__.py` re-export，函数式加进 `MinkowskiEngine/MinkowskiFunctional.py:L47` 起的 46 个镜像；⑤ 单测+gradcheck。

**自定义核形状**：`KernelGenerator` 传 region_offsets + RegionType.CUSTOM；高维优先试 HYPER_CROSS。

**调试 C++ 坐标管理**：在 `tests/cpp/setup.py:L34` 加小组件目标单独编译；GPU 内存策略 `ME.set_gpu_allocator`（`MinkowskiEngine/MinkowskiCoordinateManager.py:L63`）可在 c10 池与 raw CUDA 间切换。

## ⑧ 进一步阅读：14 步 tour 浓缩

- **步 1-2 心智模型**：README + `docs/terminology.rst` 术语表。
- **步 3 三件套**：Tensor → SparseTensor（COO 核心）→ TensorField（连续坐标场，`sparse()` 在 `MinkowskiEngine/MinkowskiTensorField.py:L286` 量化）。
- **步 4-5 C++ 心脏**：哈希坐标图 → Manager → kernel map 与惰性键。
- **步 6-8 内核三连**：Direct-GEMM 卷积 → cuSPARSE 底座（`src/spmm.cu:L80`）→ 池化·广播·插值·剪枝。
- **步 9-11 桥与前端**：pybind 三实例化矩阵 → `__init__` 聚合（`MinkowskiEngine/__init__.py:L211`）→ 量化/批整理管线。
- **步 12 用起来**：`examples/example.py:L38` 最小可跑 → `examples/minkunet.py:L35` 的 MinkUNetBase（L244 的 MinkUNet34C 是 ScanNet 标杆）→ `examples/resnet.py:L53`。
- **步 13-14 工程资源**：双线测试 → `docs/benchmark.md`（对比 SparseConvNet，k=7 前向 0.165s vs 0.583s，L37）→ `docs/guides.md` → issues.md+migration_05.md。

> 阅读顺序：示例先跑（步 12）→ 术语（步 2）→ 本文第③节 → 按需下潜。
