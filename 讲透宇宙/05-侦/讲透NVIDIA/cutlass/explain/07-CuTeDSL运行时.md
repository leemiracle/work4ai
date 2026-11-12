# 07 · CuTeDSL 运行时：基型系统、JIT 执行器与 host 运行时设施

## 角色定位

`python/CuTeDSL/cutlass/base_dsl/` 是 CuTeDSL Python 包的运行时底座（图谱域 1410 节点/97 文件）：把 Python 数值语义映射为 MLIR SSA 类型（基型系统）、把 cubin 装载进 CUDA 上下文并驱动调用（JIT 执行器）、把宿主内存/流管理与 kernel 语义隔离（runtime/ 子包）。`cute/experimental/` 提供 host 回调与流水线原语。许可证分界：CuTeDSL 整包受 NVIDIA 专有 EULA 约束（与仓根 EULA.txt 逐字节相同），异于 C++ 侧 BSD-3-Clause。

## 内部结构

**基型系统**（base_dsl/typing.py）：`Integer` 抽象基类（typing.py:2090，metaclass=`IntegerMeta` typing.py:579）派生全部整数基型，`Int32` 在 typing.py:2697（声明式类体，width/signed 编进 metaclass）；`recast_width` 的五档 `type_map`（typing.py:701-705）是位宽重铸唯一分派表；bool 参与算术显式提升 `to(Int32)`（typing.py:875）。

**JIT 执行器**（base_dsl/jit_executor.py，1850 行）类层次一条线：`CudaModuleAndKernel`（jit_executor.py:88）→ `ArgMeta`（L208）→ `ExecutionArgs`（L387，ctypes 打包）→ `JitExecuteContext`（L1035）→ `JitModule`（L1052）→ `JitExecutor`（L1140，`__call__` L1253）→ `JitFunctionArtifacts`（L1266）→ `ExportProvider`（L1303）→ `JitCompiledFunction`（L1336，对外可调用对象，`__call__` L1611）。CUDA 方言特化 `CudaDialectJitModule`（cutlass_dsl/cuda_jit_executor.py:47）与 `CudaDialectJitCompiledFunction`（cuda_jit_executor.py:86）。

**AuxRuntimeFunc**（jit_executor.py:1313，abc.ABC）是 host 回调入类型系统的门面：`QueryDeviceWorkspaceFunc`（cute/experimental/host_runtime.py:45）继承它，`__call__` 返回 `AllocationRequirement`（host_runtime.py:25，ctypes.Structure）——host_runtime.py 全文仅 97 行，即该协议的参考实现。

**参数打包**（base_dsl/tvm_ffi_builder/）：`CallProvider` 抽象（tvm_ffi_builder/tvm_ffi_builder.py:178）两实现——`NopCallProvider`（call_provider.py:36）与 `DynamicParamPackCallProvider`（call_provider.py:44），后者 `pack_params`（call_provider.py:194）含 stride-one 探测（L110）与 FP4 双元素打包 `_make_f4x2_mapper`（L123），`generate_llvm_call`（L236）生成 LLVM 调用序列；参数规格由 `Param(ABC)`（tvm_ffi_builder/spec.py:86）描述。

**runtime/ 子包**：cuda.py（957 行）手写 driver API 绑定——`DeviceInfo`（cuda.py:179）、`checkCudaErrors`（L347）、`load_cubin_module`（L508）、`DevicePrimaryContext`（L494）；device_tensor.py 的 `allocate`（L22）/`to_gpu`（L108）/`from_gpu`（L115）；`StreamAdapter`（stream_adapter.py:28）；dlpack_types.py 手写 DLPack ABI（`DLTensor` dlpack_types.py:65）。

**流水线原语**（cute/experimental/pipeline.py，1403 行）11 类：`GenericPipelineBase`（pipeline.py:59）下有 `TMAToUMMAPipeline`（L420）、`TMAToUMMACircularPipeline`（L711）、`TMAToAsyncPipeline`（L881）、`AsyncToUMMAPipeline`（L931）、`UMMAtoAsyncPipeline`（L991）、`TMAStorePipeline`（L1106），及调度侧 `GroupedGemmSchedulerPipeline`（L1235）、`CLCPipeline`（L1299）。

## 外部连接

`cute/runtime.py` 是基型系统向上出口：`_Tensor`（runtime.py:163）、`from_dlpack`（L777）、`make_ptr`（L837）、`nullptr`（L892）、`TensorAdapter`（L909）、fake tensor 工厂（L707，无 GPU 推演用）。向下 cuda.py 依赖 cuda-python 包；向旁 operators 库的 CuTeDSL provider（第 09 篇）以 `JitExecutor` 为执行后端；`export/c_header_generator.py` 导出 C 头文件（接第 12 篇）。

## 数据流

JIT 调用主链：用户函数经 AST 预处理（见第 08 篇 PyIR 线）产出 MLIR → 编译出 cubin → `load_cubin_module`（cuda.py:508）→ `CudaModuleAndKernel` 持句柄（jit_executor.py:88）→ `ExecutionArgs` 收集实参（L387）→ `pack_params` 打包 FFI 结构（call_provider.py:194）→ `JitCompiledFunction.__call__` 发射（jit_executor.py:1611）；kernel 需要 host 工作区时 `QueryDeviceWorkspaceFunc.__call__`（host_runtime.py:67）先返回 `AllocationRequirement`，分配后二次进入。

## 设计决策

1. **AuxRuntimeFunc 抽象而非回调指针**（jit_executor.py:1313）：host 询问行为做成类层级，可组合、可静态校验。
2. **ctypes 直译 driver API**（cuda.py 手写绑定+错误检查 L347）：不引 pytorch/cupy，零重依赖；代价是 DLPack 结构也手写（dlpack_types.py:23-65）。
3. **Pipeline 用继承而非配置对象**：circular 与非 circular 显式分家（pipeline.py:420 vs 711），继承树即文档。
4. **基型声明式一行开新品类**（typing.py:2697）：类型代数统一由 IntegerMeta 实现（提升/重铸 typing.py:697）。

## 新人提示

- 读码从 `JitCompiledFunction.__call__`（jit_executor.py:1611）切入，上追 ExecutionArgs、下追 runtime/cuda.py，一天通主链。
- 基型判断用 `Integer` 基类与 `is_static` trait（与 C++ CuTe 的 integral_constant.hpp 同名同义）。
- experimental/ 是显式命名的不稳定面（IKET profiler 等），API 不保证兼容。
- fake tensor（runtime.py:707）是无 GPU 调试利器。
