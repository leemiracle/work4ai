# 09 · codegen 与 NVRTC 执行：源字符串到可加载 kernel 的全链

## 1. 角色定位

nvFuser 不走离线编译，而是**运行时生成 CUDA C++ 源码字符串，再用 NVRTC 现场编译成 cubin/ptx，经 Driver API 加载执行**。这条链分三级：`csrc/codegen.cpp`（4886 行）负责 kir→源码文本；`csrc/runtime/executor.cpp` 的 `KernelExecutor::compile`（`executor.cpp:170-326`，156 行）是编译期总调度；`csrc/runtime/compiled_kernel.cpp`（1537 行）封装 NVRTC 调用、模块加载与 kernel_db 缓存。理解这条链就理解了 nvFuser "JIT 编译器" 四个字的全部工程含义。

## 2. 内部结构

**codegen.cpp 的 11 组顶层实体**：辅助函数 `ptrType`（`codegen.cpp:33`）、`genTemplate`（114）、`genCall` 两重载（124/132）、`genPtrType`（142）、`genStaticCast`（149）、`genReinterpretCast`（154）、`getMinimumValue/getMaximumValue`（158/173）；`ArgumentBuilder`（`codegen.cpp:55`）——逗号/换行自适应的参数列表构建器，含 bool 特化（101-106）；压轴的 `CudaKernelGenerator`（`codegen.cpp:189`，私有继承 `kir::ConstIrVisitor`）独占 4000+ 行；唯一公共入口 `generateCudaKernel`（`codegen.cpp:4876`）只是转发到 `generateKernelDefinition`。

**CudaKernelGenerator 是 handle 重载森林**：Predicate@625、TensorIndex@721、UnaryOp@871、RNGOp@941/945、BinaryOp@1094、TernaryOp@1158、ScatterOp@1315、ArgsortOp@1386、TopKOp@1542、ScanOp@1665、BroadcastOp@2026、ReductionOp@2189、LoadStoreOp@2230、WelfordOp@2435、GridReduction@2574、GroupedGridReduction@2847、GridBroadcast@3446、AllocateFusedReduction@3667、ForLoop@3993、IfThenElse@4049、Allocate@4081、Asm@4183、BlockSync@4485 等 50+ 个 `handle` 分支，每类 KIR 节点对应一段 CUDA 文本生成。串行 grid 归约、allreduce、grouped 变体各有专门 generate 函数（2645/2710/2779/3016/3335）。

**executor.cpp 编译期**：`KernelExecutor::compile`（`executor.cpp:170`）先探测 cpAsyncBulk（TMA）——命中则强制 int32 索引并关 magic_zero（`executor.cpp:200-204`）；GpuLower 后构造 `CompiledKernel`（`executor.cpp:240`），绑定输入推导 launch 参数，最后 `compiled_kernel_->compile(launch_params)`（`executor.cpp:275`）。

**compiled_kernel.cpp 编译现场**：`kernelPreamble`（`compiled_kernel.cpp:99`）把 stringify 后的 `nvfuser_resources::*_cu`（basic_type_traits/bit/complex_number/fp16/bf16/fp8/fp4/type_traits/array/casts 等，`compiled_kernel.cpp:101-114`）注入生成代码——这就是 runtime/*.cu 设备库的进链方式。`NvrtcCompileDriver::invoke`（161）调 `nvrtcCompileProgram`（171）并处理 log 尺寸陷阱（175-177 注释：log size 虚高需截断）；`CuModuleLoadDataDriver`（323，invoke 在 348-355）走 `cuModuleLoadDataEx`。`fillCompileOptions`（464）装配 `--std=c++17`（473）、调试 `-G`（475）、`--diag-suppress=177`（480）、`-default-device`（498）、`--fmad` 开关（501-503）、`--use_fast_math`（508）、`-lineinfo`（513）、`-DNDEBUG`（518）、`--ptxas-options`（531）。`queryTargetGPUVersion`（751）决定是否 compile_to_sass；cudaMemPool 上下文由 `executor_utils::initializeCudaContext`（745）保证。

**kernel_db 编译缓存**：`KernelDb` 单例（`kernel_db.cpp:29/41`）以生成代码字符串为 key（`kernel_db.h:41-43`），`KernelDbEntry` 记录 kernel_signature/compile_args/kernel_code_file/cubin_file 四元组（`kernel_db.h:30-38`）。使用点在 `compiled_kernel.cpp:791-815`：`kernel_db.query`（796）命中直接取 cubin，未命中才 `compileSource`（801）并 `kernel_db.write`（806）回写。开关是 `EnableOption::KernelDb`（`options.cpp:165`）。

## 3. 外部连接

上游：GpuLower 产出的 `kir::Kernel`（经 `CompiledKernel` 持有的 lowered()）；runtime/*.cu 设备库以 stringified 资源形式被 include。下游：`KernelExecutor::run`（`executor.cpp:1013`）取 cubin 句柄 `cuLaunchKernel` 或走 CUDA Graph 捕获；TensorCache/FusionExecutorCache 依赖 kernel_db 的字符串指纹做跨进程级去重。NVRTC 与 Driver API（libnvrtc/libcuda）是仅有的两个外部运行时依赖。

## 4. 数据流

kir::Kernel → generateCudaKernel 拼源码（kernelPreamble + 生成体）→ KernelExecutor::compile 定索引类型/构造 CompiledKernel → kernel_db.query 查缓存 → 未命中则 fillCompileOptions + nvrtcCompileProgram（ptx 或 sass）→ kernel_db.write 回写 → cuModuleLoadDataEx 进上下文 → run() 阶段 cuLaunchKernel。

## 5. 设计决策

源码字符串而非 LLVM IR，换来的是 NVRTC 单依赖与 nvcc 级语法自由（模板/C++17）；代价是每次 miss 的编译延迟，故 kernel_db 以「代码串+编译选项」为指纹缓存 cubin。TMA 场景强制 int32 索引（`executor.cpp:200-204`）是因为 TMA 的坐标语义在 64 位下有额外开销。compile_to_sass 受 `DisableOption::CompileToSass` 与 CUDA 版本双闸（`compiled_kernel.cpp:757-763`），默认 ptx 便于跨 sm 版本兜底。

## 6. 新人提示

- 抓生成代码：`NVFUSER_DUMP=cuda_kernel`/`cuda_full`；对照 `NVFUSER_DUMP=lower_verbose`（篇 08）可看同一 kernel 在两级 IR 的形态。
- NVRTC log 尺寸注释（`compiled_kernel.cpp:175-177`）是真实踩坑记录：直接用返回 size 会读到垃圾尾巴。
- kernel_db 命中不等于免加载——cubin 仍要 cuModuleLoadDataEx；它省的是 NVRTC 编译，不是模块加载。
- codegen.cpp 的 `handle(kir::Predicate*)`（625）是所有控制流文本的汇聚点，找生成代码里 `if(...)` 的来源从这里下手。
