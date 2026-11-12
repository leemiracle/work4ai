# MatX kernels 与 executors：手写 kernel 库与执行器抽象

## 一、角色定位

`kernels/`（11 个 .cuh）与 `executors/`（9 头）是 MatX 立即层的"地面"：前者存放无法用库调用表达、必须手写的 CUDA kernel（转置、卷积、稀疏 SpMV、SAR 成像、pwelch、多速率重采样、双 float 扩展精度），后者把"在哪执行、怎么执行"抽象成类型——`cudaExecutor`（流执行）、`CUDAJITExecutor`（运行期融合编译）、`HostExecutor`（CPU）。transforms/ 的每个立即变换最终都落到某个 executor 上调某个 kernel 或库。

## 二、内部结构

### 2.1 executors：三种执行域

- **cudaExecutor**（executors/cuda.h:57，注释 :50 明言"non-JIT path"）：`class cudaExecutor : public detail::CudaExecutorBase`，构造即转发（:65-66/:68），本体极薄——全部状态（stream/profiling/NVTX 计时）在基类 CudaExecutorBase（cuda_executor_common.h:86），三种构造：cudaStream_t、int 句柄、默认 0 流（:97/:104/:115）。
- **HostExecutor**（host.h:82）：`Exec(const Op&)` noexcept（:148），服务 host 张量表达式与 LAPACK/FFTW 后端。
- **CUDAJITExecutor**（jit_cuda.h:325）：融合执行器。核心管线在 core/nvrtc_helper.h：`nvrtc_compile_and_run`（:696）把整棵算子树序列化成 CUDA 源码 → NVRTC 编译（可产 LTO-IR，:956 nvrtcGetLTOIRSize）→ **cubin 走 LTOIR 缓存**（:792 GetLTOIRCachedBytes，命中即 `cuModuleLoadDataEx` 直接装载 :806）→ 启动。kernel 按 `device_<id>_sm_<arch>` 键缓存（jit_cuda.h:133/:143），与表达式类型键共同保证"同表达式同架构只编译一次"。:59/:66 的注释解释两级缓存分工：外层执行参数缓存 + 内层 kernel 缓存。
- distributed.h + core/distributed_tensor.h：多 GPU 分布式执行器（分布式张量与 MaterializeTo 语义，见 base_operator.h:207 一带的分派）。

### 2.2 kernels：每文件一个硬问题

- **transpose.cuh**：`transpose_kernel_oop`（:28，out-of-place 模板 kernel）——被 transforms/transpose.h 当非连续输入时的后备路径（transform 层 :75 一带 `if (!in.IsContiguous())` 判定后走 permute+copy 复合）。
- **matvec.cuh**：对角格式稀疏 SpMV 双实现 `diai_spmv_kernel`/`diaj_spmv_kernel`（:44/:61），DIA-I/DIA-J 两种对角偏移存储的乘法。
- **sar_bp.cuh**：SAR 后向投影成像 kernel 群（:87 主模板、:129 相位 LUT 填充 `SarBpFillPhaseLUT`、:157 分发层），计算类型 strict/loose 双精度策略可参数化。
- **pwelch.cuh**：`pwelch_kernel`（:48）分段加窗功率谱。
- **conv.cuh/filter.cuh/resample_poly.cuh/channelize_poly.cuh**：直接卷积与多相滤波引擎——streaming 层（conv1d_stream.h:38-49 注释）点名复用 conv.cuh 的 VALID 引擎。
- **tensor_accessor.h**：`BoundAccessor`（:63 一带）把张量视图绑定成 kernel 可用的访问器，让 LDC 类常量在构造期物化（:75 注释）。
- **fltflt.h**：双 float 扩展精度类型（:40 注释声明动机），`struct alignas(8) fltflt`（:57）两个非重叠 fp32 分量；构造函数从 double 位型无 FP64 指令拆 hi/lo（:73），支持 host/device 运算符重载（:129-133 一带）。用于无 FP64 硬件（部分嵌入式 GPU）上逼近 double。

### 2.3 执行器与 kernel 的接线

transforms/ 各立即变换在 `Exec()` 里：有库可用（cuFFT/cuBLAS/cuSOLVER）走库；没有库的（conv/resample/sar_bp/pwelch）调 kernels/ 的 `__global__` 函数，grid/block 由 core/get_grid_dims.h 计算；JIT 路径则整树序列化，此时 kernels/ 的手写函数也通过 `solver_cusolverdx_func` 式符号前缀（nvrtc_helper.h:387 一带识别 `fft_cufftdx_func` 等）进入生成源码。

## 三、外部连接

- **向上**：BaseOp::run(ex) 是唯一入口（base_operator.h:181 起，分派链见 explain 02/03）；
- **横向**：core/allocator.h 供 kernel 临时内存、core/cache.h 供 JIT cubin 与库句柄缓存、core/get_grid_dims.h 供启动参数；
- **生态**：executors/cuda.h 的 profiling 开关联动 core/nvtx.h NVTX 域（examples/simple_radar_pipeline.cu:83-95 的四段 range 就是 NVTX 消费者）；distributed 依赖 NCCL 风格集合通信抽象（distributed_tensor.h）。

## 四、数据流

JIT 融合一次完整数据流（最能体现本层价值）：`(y = x * hamming(N) |> fft).run(CUDAJITExecutor{...})` → run 识别 jit executor 直接 `ex.Exec(*tp)`（base_operator.h:188 一带，跳过 PreRun/PostRun）→ 算子树各节点吐 ToJitString（生成器/算子/fft_cufftdx 各自的源码片段）→ NVRTC 编译单 kernel → cubin 进 LTOIR 缓存（nvrtc_helper.h:792-806）→ cuLaunchKernel。对比非 JIT：三个独立 kernel + 两次全局存取。**融合是 MatX 对"手写 CUDA 才能达到的性能"的回答**。

## 五、设计决策

1. **执行器是类型不是运行时对象图**：全部编译期分派（is_executor_t/is_cuda_executor_v concept），零分发开销，代价是 run() 的 if constexpr 链复杂（base_operator.h:181-300）。
2. **kernel 库最小化**：只手写"库覆盖不到"的（多相滤波/SAR/稀疏 SpMV/双 float），能调库绝不自研——matmul 双轨制（自研 tile kernel matmul_cuda.h:651 + cuBLAS 桥）是显式权衡而非重复建设。
3. **JIT 两级缓存**：LTOIR 按 cubin 文件名缓存（nvrtc_helper.h:792），launch 参数按 device+sm 缓存（jit_cuda.h:133）——跨进程版本还可落盘（cache 目录，cache.h 的 GetKernelCacheDirectory 一带）。
4. **fltflt 的定位**：不是通用 float2 替代品，而是"消费级卡跑科研精度"的窄场景补丁，bench/00_misc/fltflt_arithmetic.cu 单独量测其代数性能。
5. **甄别**：tensor_accessor.h 不是普通工具头——它是 kernel 侧的张量协议绑定层（BoundAccessor :63），手写 kernel 与 core 张量体系的耦合点。

## 六、新人提示

1. 想知道表达式走了哪条执行路径，开 NVTX profiling 构造 executor，用 nsys 看域；
2. JIT 首次调用慢（NVRTC 编译）属预期，第二次起命中缓存；改表达式类型才会重编；
3. 手写 kernel 目录的模板签名普遍很长（tensor 模板参数直传），改 kernel 先看 transforms 层怎么调它再动手；
4. fltflt 需要 include matx/kernels/fltflt.h 且硬件无 FP64 时才有收益，别在 A100/H100 上用它；
5. 新增 executor 的门槛很高（run 分派链、五类 concept、缓存协作都要懂），多数需求新增 transform 就够；
6. distributed 执行器需多卡环境，test/00_tensor/DistributedTensorTests.cu 是行为参照。

*锚清单：cuda.h:50/57/60/65-66/68、cuda_executor_common.h:86/97/104/115、host.h:82/148、jit_cuda.h:59/66/133/143/325/383/392、nvrtc_helper.h:387/696/755/792/796/806/949-953/956、transpose.cuh:27-28、matvec.cuh:44/61、sar_bp.cuh:87/128-129/157、pwelch.cuh:48、tensor_accessor.h:51/54/63/75、fltflt.h:40/55/57/64/73/129-133、base_operator.h:181/188/207、conv1d_stream.h:38-49、bench/00_misc/fltflt_arithmetic.cu。*
