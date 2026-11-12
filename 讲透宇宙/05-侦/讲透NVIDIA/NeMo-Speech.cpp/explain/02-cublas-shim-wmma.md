# 02 · cublas_shim：WMMA kernels 的 cublas 替身

## 角色定位

kernels/cublas_shim.cu（1587 行）是仓内自带的 drop-in libcublas 替换。动机写在头注释（cublas_shim.cu:3-20）：ggml-cuda 对非量化 GEMM——FastConformer 注意力 scores/context、下采样卷积、CTC 头——调用一小撮 cuBLAS 入口，而真 cuBLAS 会连带拖进 514MB 的 libcublasLt；shim 精确实现 ggml 导入的那组符号，后端是形状特化的 CUDA kernel 与 WMMA tensor core 路径（fp32 累加），让发布归档既不需要真 cuBLAS 也不需要 cuBLASLt。它是"为什么叫 shim"的标准答案：不修改 ggml 一行，靠 ELF SONAME/符号名匹配让动态装载器把 ggml 的 cuBLAS 依赖解析到这个更小的库上。

## 内部结构

**ABI 层**：不 include cublas_v2.h（cublas_shim.cu:15-17——其函数在 nvcc 下标成 __host__ __device__ 会编译失败），改为裸 int/void* 声明 + 固定 ABI 枚举值：OP_N/OP_T、R_32F/R_16F/R_16BF、COMPUTE_16F/COMPUTE_32F（cublas_shim.cu:36-39），typedef 五个句柄类型（cublas_shim.cu:42-50）。语义对齐 cuBLAS：C(m×n, col-major, ldc) = alpha·op(A)·op(B) + beta·C（cublas_shim.cu:19-20）。

**句柄与 workspace**：ShimHandle 只记 device/stream 与 split-K workspace 表（cublas_shim.cu:59-71）。workspace 按 stream 分配、LRU 上限 8 个（kMaxSplitKWorkspaces，cublas_shim.cu:89），优先 cudaMallocAsync、失败回退 cudaMalloc（cublas_shim.cu:130-142）；淘汰时 cudaDeviceSynchronize 后释放（cublas_shim.cu:117-129）。容量按 12MiB/流 上界钉死（kBlockSplitMaxElems 等常量，cublas_shim.cu:85-98）。

**kernel 族**：WMMA 路径 k_hgemm_tn_wmma（cublas_shim.cu:214 起，fragment 声明 :233-241，load_matrix_sync/mma_sync :259-261，store col-major :265）；fp32 累加变体 k_hgemm_tn_wmma_facc（:301-302）；块形状分档 64×32（k_hgemm_tn_wmma64x32_facc，:392-393）与 64×64（:478-479）。朴素路径是共享内存 tile 的 gemm_tile（cublas_shim.cu:1080-1082 定 EDGE_TM/TN/TK=64/64/16；协作装载 cublas_shim.cu:1102-1120；acc[4][4] 寄存器累加 cublas_shim.cu:1128-1136；alpha/beta epilogue cublas_shim.cu:1141-1154），批版本 k_strided_tiled（cublas_shim.cu:1162-1172）。

**调度谓词与分发**：use_wmma_tn/use_hgemv_tn/use_sgemv_tn（cublas_shim.cu:1183-1189）按转置组合、dtype 与 n==1（GEMV）选路；use_tiled 的 crossover 是 m·n·batch ≥ 64K——小输出走朴素并行、大输出吃 k 复用（cublas_shim.cu:1174-1181 注释写明是 Thor 经验值）。launch() 分发器（:1237 起）按谓词挑 kernel 并 trace_launch 记录（EDGE_SHIM_TRACE_SHAPES env，:1191-1205）；launch_strided/launch_ptrs 处理批（:1376-1389）；launch_status 把 kernel 启动失败如实上报而非假成功（:1410-1418）。

**导出层**：extern "C" 块（cublas_shim.cu:1419）实现 13 个符号——cublasCreate_v2（cublas_shim.cu:1421-1430）、cublasDestroy_v2（cublas_shim.cu:1431-1457，同步后释放全部 workspace）、cublasSetStream_v2（cublas_shim.cu:1459-1464）、cublasSetMathMode/SetWorkspace_v2（cublas_shim.cu:1465-1474，接受即忽略——shim 自管 workspace）、cublasGetStatusString 恒返 EDGE_SHIM_OK（cublas_shim.cu:1475-1478）、GemmEx（cublas_shim.cu:1481-1496）、GemmStridedBatchedEx（cublas_shim.cu:1498-1513）、GemmBatchedEx（cublas_shim.cu:1515-1530）、Sgemm_v2（cublas_shim.cu:1532-1546）、SgemmStridedBatched/SgemmBatched（cublas_shim.cu:1548-1587）。gemm_has_work 短路零工作量调用。

**构建接线**（CMakeLists.txt:263-299）：GGML_CUDA+NEMO_SPEECH_CUBLAS_SHIM 时建 SHARED；SOVERSION 按 CUDA 工具链 13.0 分界钉 12 或 13（CMakeLists.txt:266-271）；未设架构时回退 compute_80 PTX（JIT 可移植到 sm_80..Blackwell 含 Thor，:277-279）；Windows 下 OUTPUT_NAME cublas64_{12,13} 对齐 toolkit 导入库记录的 DLL 名实现 app-local 替换（:283-287），Linux 下 OUTPUT_NAME cublas + SOVERSION，并用 kernels/ver_cublas.map 生成的 version script 锁符号版本（:290-299）；map 文件里 global 正是那 13 个符号、local:* 兜底（ver_cublas.map）。CUDA_SEPARABLE_COMPILATION ON 支撑 device 端内联。

## 外部连接

唯一调用方是 ggml-cuda 的动态装载解析——没有任何仓内代码 include 它。启动链：ggml CUDA 后端初始化 → dlopen libcublas.so.12/.13 → 命中 shim。受影响负载即 FastConformer 注意力/下采样卷积/CTC 头的非量化 GEMM 与 VAD/Sortformer 的非量化投影；量化 GEMM 走 ggml 自己的 kernel，与 shim 无关。诊断面：EDGE_SHIM_TRACE_SHAPES 打印每次 launch 的 (m,n,k,op,dtype,path)，docs/development/cublas-shim.md 是官方深水文档。

## 数据流

ggml 构图时发现 cuBLAS 可算的 mul_mat → ggml-cuda 经 cublasHandle 调 GemmEx/StridedBatchedEx → shim 校验 gemm_has_work → stream_for_handle 取该 handle 的 stream → launch() 按 (opA,opB,ta,tb,tc,n) 谓词选 kernel：n==1 的 TN 走专用 GEMV warp kernel；FP16 TN 且 C 是 F32/F16/BF16 走 WMMA tensor core（fp32 累加）；大输出走 tiled 共享内存 kernel；CPU 每次调用的 alpha/beta 由 host_scalar 按 computeType 解引用。C 就地更新（beta≠0 时读-改-写），无内部同步——异步语义与真 cuBLAS 对齐，由调用方在流上同步。

## 设计决策

①SONAME 劫持而非链接期替换：保留 ggml 上游零改动的项目铁律（与 patches/ 的 patch-系列同一哲学）。②ABI 裸声明而非引官方头：规避 nvcc 的 __host__ __device__ 语义冲突，代价是枚举值必须与 toolkit 永久对齐——所以 SOVERSION 按工具链分代。③形状特化优于通用：本仓 GEMM 形状谱系窄（语音编码器几何），TN/F16 主路径吃 tensor core，朴素 kernel 兜住其余，省掉 cuBLASLt 的启发式搜索。④workspace 自管 + LRU 按流：接受 cublasSetWorkspace 的用户缓冲但不用，避免与 ggml 的 buffer 生命周期耦合。⑤12MiB/流 上界：split-K 收益有限，宁可用小 workspace 保多流共存。

## 新人提示

先读头注释 20 行（cublas_shim.cu:3-20）——动机、约束、语义全在里面；再读 ver_cublas.map 数符号；最后读 launch() 分发器（cublas_shim.cu:1237）看谓词瀑布。验证 shim 是否生效：ldd 二进制看 libcublas 解析路径，或设 EDGE_SHIM_TRACE_SHAPES 跑一次转写观察路径分布。改 kernel 时记住 fp32 累加是精度契约（BF16/FP16 输出的 C 也要 fp32 累加再转），回归靠 tests/cpp 的数值奇偶校验族。新增符号必须同时改 ver_cublas.map，否则符号不出现在导出表、装载器找不到直接崩。
