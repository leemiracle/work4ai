# 04 · ops 调度与 pybind 绑定：从 `get_minkowski_function` 到 `MinkowskiEngineBackend._C`

> 涉及：`MinkowskiOps.py`、`MinkowskiFunctional.py`、`MinkowskiCommon.py`、`pybind/minkowski.cpp`、`extern.hpp`

## ① 角色定位

Python 层是薄壳，算力全在 C++/CUDA 扩展 `MinkowskiEngineBackend._C` 里。连接两侧的是字符串拼接调度链：`get_minkowski_function`（`MinkowskiCommon.py:110`）拼"算子名+设备后缀"`getattr` 动态取函数，全引擎稀疏算子都经这 11 行进 C++。对照 `MinkowskiOps.py`/`MinkowskiFunctional.py` **不走**此链：前者 `cat/_sum/mean/var`（L158/185/212/243）经 `_tuple_operator`（L70）校验坐标图一致后用 torch 稠密算；后者约 26 个激活函数经 `_wrap_tensor`（`MinkowskiFunctional.py:30`）代理 torch.nn.functional。分工契约：**形状不变的逐元素操作留给 PyTorch，凡要动坐标集合（kernel map）的操作才下放 C++**。

## ② 内部结构

**调度核心**：`get_postfix`（`MinkowskiCommon.py:101-103`）按 `is_cuda` 返回 GPU/CPU；`get_minkowski_function`（L110-120）L111 拼名、L112-113 `getattr` 命中即返回，CUDA 未命中抛"请以 cuda available 重编译"（L115-118）——CPU_ONLY 构建里 GPU 符号不存在的直接后果；目标模块 L33 `import MinkowskiEngineBackend._C`。

**七处调用点**（forward/backward 成对）：Broadcast（`MinkowskiBroadcast.py:62/86`）、Interpolation（`MinkowskiInterpolation.py:51/70`）、Pruning（`MinkowskiPruning.py:53/65`）、LocalPooling（`MinkowskiPooling.py:69/88`）、LocalPoolingTranspose（`MinkowskiPooling.py:468/488`）、GlobalPooling（`MinkowskiPooling.py:605/619`）、InstanceNorm（`MinkowskiNormalization.py:207-208/261-262`）。第七处无专属 C++ 算子：InstanceNorm 用 GlobalPooling 求统计、Broadcast 做线性变换（L219-246），绕开后端不存在的除法广播。卷积族是第八个调用者（`MinkowskiConvolution.py:71/98`），机理相同。

**pybind 绑定面**（`minkowski.cpp:36-68`）四块：①常量 4 个（L38-41），`is_cuda_available`（`extern.hpp:808-814`）是 `#ifndef CPU_ONLY` 的**编译期常量**非运行时探测；②模板算子：`instantiate_cpu_func<int32_t>`（`minkowski.cpp:57`，实体 `extern.hpp:516-574`）注册 13 对共 26 函数，GPU 同构（`extern.hpp:577-646`），全挂 `gil_scoped_release`；③非模板工具：quantize 四兄弟+direct_max_pool+两个 coo_spmm（`extern.hpp:649-666`）；④枚举+类：`MinkowskiAlgorithm`（L684）、`RegionType`（L697）、`PoolingMode` 13 值（L703-728）、`BroadcastMode` 仅加/乘（L730-735，`ELEMENTWISE_ADDITON` 系笔误）、`CoordinateMapKey`（L744-763）与三份 `CoordinateMapManager`（L767-806，实例化 CPU/GPU_default/GPU_c10）。

## ③ 外部连接

上游是各 autograd Function（如 `MinkowskiBroadcast.py:40`）的 forward/backward；下游 C++ 实现在 `src/*_cpu.cpp`/`*_gpu.cu`（经 `extern.hpp:55-509` 前置声明对接）。管理器路由 `MinkowskiCoordinateManager.py:132-147`：拼后缀 `getattr` 出类（L146）实例化为 `self._manager`——每次算子调用的末参。

## ④ 数据流

以 Pruning 为例：forward 先 `.contiguous()`（`MinkowskiPruning.py:52`）→ L53 依 `is_cuda` 得 `PruningForwardGPU` → L54-60 传五参（含 `coords_manager._manager`）→ pybind 按 manager 类型在同名重载中选 default/c10 实例（双注册 `minkowski.cpp:60-64`）→ `AT_DISPATCH_FLOATING_TYPES` 按 dtype 实例化 → `at::Tensor` 回包 SparseTensor。

## ⑤ 设计决策

- **字符串拼接+getattr 而非注册表**：零生成代码，代价是拼错名运行时才炸，但 L115-118 单独点明 CPU_ONLY 场景，防御便宜；
- **同名双注册做分配器分发**：借 pybind 重载解析按 manager 类型分流；
- **`dtypestr` 传空串**（L57）：坐标类型仅 int32 单实例化，参数位留给多坐标类型却从未启用；
- **InstanceNorm 组合而非下沉**：复用两个已验证原语，不扩 C++ 面。

## ⑥ 新人提示

1. **裸模块名与 sys.path hack 是第一坑**：扩展是顶层路径 `MinkowskiEngineBackend._C`（`setup.py:312`），包内却全是裸绝对导入（`MinkowskiOps.py:30/37`）；`__init__.py:31-32` 用 `sys.path.append(包目录)` 才能解析——动 import 前先想清，`__init__.py:49`"先 import torch 再进后端"同样必须遵守；
2. "函数不存在"报错先查：构建是否 CPU_ONLY、张量设备与函数后缀是否一致；
3. `is_cuda_available()` 是构建期烙印，装 CPU_ONLY 版照样 false；
4. 新增 C++ 算子三处必改：`src/` 实现、`extern.hpp` 声明+注册、Python 调用名，拼写必须严格一致。
