# 11 · HostIR 与多层 CUTLASS：host 侧 JIT 与张量库的三层实体

## 1. 角色定位

nvFuser 不只生成 device kernel：多设备融合里「launch kernel → 通信 → 再 launch」的 host 编排本身也需要被编译，这就是 **Host IR + HostIrJit**——用 LLVM ORC 把 host 侧指令流编成原生 main 函数，实现类型化、可重放的执行（CUDA Graph 的代码级等价物）。另一条线是 CUTLASS 集成：仓库里同名"cutlass"有**三层不同实体**，分别承担预编译封装、运行时代码生成、外部依赖三种角色，混淆它们是读码第一大坑。

## 2. 内部结构

**HostIrJit 的 Pimpl**：`csrc/host_ir/jit.h:18` 前向声明 `struct HostIrJitImpl`，`jit.h:20` 公开类 `HostIrJit` 只持 `std::unique_ptr<HostIrJitImpl> pimpl_`（`jit.h:34`），把 LLVM 头文件污染挡在 jit.h 之外。实现体 `jit.cpp:65` 起的 `HostIrJitImpl`：`compile()`（`jit.cpp:863`）创建 `host_ir_jit_module`、构造 entry basic block、`llvm::verifyModule` 校验（约 899）后包成 `llvm::orc::ThreadSafeModule` 交给 LLJIT（头文件 `jit.cpp:26-28`）；构造函数（918）调 `InitializeNativeTarget`；`registerExternalFunctions`（938）把 C++ 宿主函数注册进 JIT 符号表；`runWithInputs`（949）驱动执行。公开包装层 1008-1034：析构 1008、构造 1012、`runWithInputs` 1017、`inputs/outputs/container` 1022/1026/1030。

**逐算子 Dispatcher**：`HostIrCompileDispatcher`（`jit.cpp:523`，上一行注释「Not handled instructions automatically trigger an error」）继承 `OptInDispatch`——**未 handle 的指令直接报错**，这使 host 代码生成的完备性可审计。handle 重载矩阵：ReshapeOp@524、LoadStoreOp@567、MatmulOp@627（调 `kMatmulOutFuncName`，634）、LinearOp@637、`hir::LaunchKernel`@662（调 `kLaunchKernelDirectFuncName`，751）、Allocate@763、Deallocate@843。外部函数签名注册集中在 460-512：launch_kernel_direct（471）、matmul_out（481）、linear_out（491）、permute（499）、reshape（506）、main（512）。

**host_ir 目录其余部件**：`lower.cpp`（182 行）按 SchedulerType 分段处理，Communication 段要求单表达式（`lower.cpp:169-177`）；`lower_to_communication.cpp` 把算子转 Communication 原语；`container/evaluator/passes` 支撑容器遍历与常量求值。

**三层 CUTLASS 实体甄别**：
1. **仓根 `cutlass/`** = 手写 kernel 封装层，CMake 构建为共享库 **libnvf_cutlass.so**（`cutlass/CMakeLists.txt:31` `add_library(nvf_cutlass SHARED ...)`，源码清单 23-29：group_mm.cu 573 行、mxfp8_scaled_mm 321、nvfp4_scaled_mm 375、nvfp4_scaled_mm_blockscale、nvfp4_scaled_group_mm 790、nvf_cutlass.cpp、cutlass_utils.cpp），include 的是 third_party 外部库（`CMakeLists.txt:33-34`），本层做模板实例化与 launch 适配。
2. **`csrc/cutlass/`** = 运行时代码生成层：`gemm.cpp`（736 行）的 `CutlassCodeGenerator`（55）、`TensorArg`（191）、`KernelTraits`（221）、`Fp4GemmSm100`（249）、`Inputs`（410）以 R"(...)" 原始字符串拼接 C++ 源码（19 处，首个 cutlass include 在 164），产出走 NVRTC；入口 `generateCode`（`csrc/cutlass/codegen.h:22`，NVF_API）。
3. **`third_party/cutlass/`** = 外部 submodule（本快照未 checkout，目录为空壳）。
另有**第四个易混实体**：`csrc/scheduler/cutlass.cpp`（138 行，2025 新增）的 `CutlassScheduler` 受 `EnableOption::CutlassScheduler` 门控默认关闭（`cutlass.cpp:69-71`），`CutlassParams::toString`（28）、`canScheduleCompileTime`（66），对接 nvmmh 路线。

## 3. 外部连接

HostIR 上游是多设备 FusionExecutor 路径（HostIrContainer 由分段+lower 产出）；下游 LLVM ORC LLJIT 在进程内 native 执行，kernel 仍由 `kLaunchKernelDirect` 直推 cuLaunchKernel。CUTLASS 三层的消费方各不相同：libnvf_cutlass.so 被 `python/python_direct/cutlass.cpp`（121 行）绑到 Python 侧做 A/B 对比；`csrc/cutlass` 生成层被 matmul 系调度器按 dtype（fp8/fp4）触发；submodule 层服务前两者。

## 4. 数据流

多设备融合 → hir::HostIrContainer（LaunchKernel/Communication/Matmul 等指令）→ HostIrJit::compile：Dispatcher 逐指令发射 LLVM IR → verify → LLJIT 编译 → 运行时 registerExternalFunctions 补符号 → runWithInputs 传张量指针数组执行 main。CUTLASS 生成层：Fusion+CutlassParams → generateCode 拼源码（引用 third_party 头）→ NVRTC → cubin。

## 5. 设计决策

Pimpl 是编译防火墙——LLVM 头极重，不锁住会污染整个 include 图。OptInDispatch 的"未处理即报错"与分段器 "change of world view" 断言同一哲学：宁可编译期炸，不让指令静默丢失。CUTLASS 分三层是**编译期预算的分治**：稳定模式（grouped/scaled GEMM）预编译进 .so 省运行时开销；探索性模式走生成层保灵活；社区库以 submodule 锁版本。

## 6. 新人提示

- 找"host 侧到底执行了什么"，读 `jit.cpp:460-512` 的 extern 函数签名表——它就是 HostIR 可执行域的白名单。
- 三层 cutlass 同名不同物：`cutlass/`（.so 封装）、`csrc/cutlass/`（代码生成）、`third_party/cutlass/`（submodule），加上 `csrc/scheduler/cutlass.cpp`（新调度器）共四处，引用路径必须写全。
- third_party/cutlass 空目录不是克隆损坏——submodule 未 init；构建 CUTLASS 相关目标前需 `git submodule update`。
- LLJIT 在多线程下的模块所有权由 ThreadSafeModule 保证，二次 compile 同一 container 需新建 context。
