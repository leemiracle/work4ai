# 02 · 坐标管理器与 kernel map：稀疏引擎的"真理持有者"

> 涉及：`MinkowskiEngine/MinkowskiCoordinateManager.py`、`src/coordinate_map_manager.hpp/.cpp`、`src/coordinate_map_gpu.cuh/.cu`、`src/coordinate_map_cpu.hpp`（行号锚均经源码核实）

## ① 角色定位

全引擎只有一份"坐标真理"：特征归 PyTorch autograd，**坐标集合永远住在 C++ 侧的 CoordinateMapManager 里**，Python 只拿 `CoordinateMapKey` 句柄。本条线三层：`MinkowskiCoordinateManager.py` 薄封装建图/查询，`src/coordinate_map_manager.hpp:87` 模板类 `CoordinateMapManager` 是图池+缓存实体，`coordinate_map_gpu.cuh:47` `CoordinateMapGPU` 与 `coordinate_map_cpu.hpp:283` `CoordinateMapCPU` 是设备侧哈希图双实现。v0.5 卖点"坐标管理全 CUDA 化"即把图操作搬进 `__global__` kernel。

## ② 内部结构

**Python 封装**：`class CoordinateManager`（`MinkowskiCoordinateManager.py:107`）构造按 `CoordinateMapType` 从 `_C` 取 `CoordinateMapManagerCPU/GPU_default/GPU_c10` 实例化；`set_gpu_allocator`（`MinkowskiCoordinateManager.py:63`）切 default/c10 内存池。方法四族：建图 `insert_and_map`（py:153，去重插入）、查映射 `kernel_map`（py:377）、`stride_map`（py:429，池化/跨 stride）、`union_map`（py:432，二元运算坐标并集）。

**C++ 图池**：`CoordinateMapManager` 持四张容器（`src/coordinate_map_manager.hpp:534/539/544/554`）：`m_coordinate_maps`（坐标图池，键=(tensor_stride,string_id)）、`m_field_coordinates`（连续坐标场）、`m_kernel_maps`（kernel map 缓存）、`m_field_to_sparse_maps`（场转稀疏缓存）。`kernel_map()`（`src/coordinate_map_manager.hpp:418-428` 声明，`src/coordinate_map_manager.cpp:637` 实现）查缓存未命中才调 `kernel_map_functor`（`src/coordinate_map_manager.cpp:751`）现场生成——同参数层直接复用，重复迭代性能的命门。模式随 `MinkowskiAlgorithm` 定（hpp:141-151）：SPEED_OPTIMIZED 双向映射，MEMORY_EFFICIENT 单向省显存。

**设备双实现**：GPU 图核心是 `concurrent_unordered_map`（`src/coordinate_map_gpu.cuh:65`，来自 `src/3rdparty/concurrent_unordered_map.cuh:29`），CPU 图是 `robin_hood::unordered_flat_map`（`src/coordinate_map_cpu.hpp:296`）——并发安全 vs 缓存友好的性能取向。`coordinate_map_gpu.cu` kernel 群分区：`quantize_coordinates_kernel`（cu:107，同 voxel 折叠）、`insert_and_map_kernel`（cu:71，原子插入去重）、`kernel_region_insert`（cu:502，核区域展开插点）、`prune_copy_and_insert`（cu:988）、`remap`（cu:1035）；`CoordinateMapGPU::insert_and_map`（cu:285）为调度壳。

## ③ 外部连接

上游：`SparseTensor.initialize_coordinates` 建首图（`MinkowskiEngine/MinkowskiSparseTensor.py:304`）；`TensorField.splat()` 走场转稀疏缓存。下游最大消费者是卷积族——`src/convolution_gpu.cu:117`（普通）/cu:203（转置）持 `kernel_map(...)` 返回的 (kernel_id, in_row, out_row) 三列；池化/剪枝/插值各再调一次。各算子 autograd Function 经 `coords_manager._manager` 直通 C++。

## ④ 数据流

一次建图：IntTensor 坐标入 `insert_and_map` → pybind 按 manager 类型选 GPU 重载 → `quantize_coordinates_kernel`（cu:107）折叠同 voxel → `insert_and_map_kernel`（cu:71）并发哈希插入、重复坐标只留首行号 → 回填 unique 坐标与行号映射 → 图池登记新键，`CoordinateMapKey` 返回 Python。此后算子凭 (in_key, kernel, stride, is_transpose…) 查 `m_kernel_maps`（hpp:544）复用。

## ⑤ 设计决策

- **图池+缓存**：同一坐标图全网络共享，kernel map 按"算子指纹"缓存——map 生成从每层前向摊销成一次；
- **键含 `is_transpose`**：转置卷积交换 in/out 方向复用普通卷积映射，缓存必须区分两个方向；
- **`string_id` 隔离**：不同网络实例的图池互不可见，防串键；
- **GPU/CPU 双实现而非单写**：CPU 版服务调试与无卡环境，接口同一（hpp:87 模板+hpp:66 特化）。

## ⑥ 新人提示

1. 文档教 `coords_man`（`docs/terminology.rst:44`），真实 API 是 `coordinate_manager`/`coordinate_map_key`（`MinkowskiEngine/MinkowskiTensor.py:212`）——术语滞后一代；
2. `decomposed_coordinates` 的 batch 内行序来自 GPU 哈希插入完成顺序，**非确定**，断言别依赖顺序；
4. kernel map 模式由 `MinkowskiAlgorithm` 全局控制（hpp:141-151），MEMORY_EFFICIENT 省显存但牺牲反向遍历。
