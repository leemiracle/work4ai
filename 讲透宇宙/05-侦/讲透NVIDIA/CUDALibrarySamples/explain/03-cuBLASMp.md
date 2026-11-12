# 03 cuBLASMp：PBLAS 风格分布式 GEMM 与 TP 算子田

## 角色定位

cuBLASMp 目录（2026 版权头，全仓最新代示例之一）演示多 GPU/多节点分布式稠密线性代数，API 语义直承 ScaLAPACK/PBLAS：全局矩阵、2D 块循环分布、进程网格 p×q。14 个算子 .cu 文件平铺在根目录——gemm/symm/syrk/syr2k/syrkx/trmm/trsm/geadd/tradd 是 PBLAS 对应物，gemr2d 是分布式矩阵搬运（TRRN），matmul_ag/matmul_ar/matmul_rs/tp_matmul 四件则瞄准 LLM 张量并行（TP）的 AllGather/AllReduce/ReduceScatter 融合算子（图谱 t04"张量并行算子田"）。

## 内部结构

单文件三层结构贯穿全部算子（以 `gemm.cu` 510 行为例）：`check_gemm_result` 模板（:27-:182）负责正确性、`run_gemm`（:184-:460）负责执行与计时、`main`（:462-:510）负责参数解析与启动。run_gemm 内部再现 PBLAS 全套概念：由 rank 算 myprow/mypcol（:219-:220，支持 'c'/'r' 两种网格布局）、`cublasMpNumroc` 数本地行列（:238-:243，即 ScaLAPACK NUMROC）、`cublasMpMatrixDescriptorCreate` 建全局描述符（:278-:283）。两种 API 代际并存：gemm.cu 等用老式 `cublasMpGemm`（:342），tp_matmul.cu 与 matmul_* 用新式描述符化 `cublasMpMatmul`（`tp_matmul.cu:143-:149` 建 matmulDesc 后 :208 调用）。

TP 旗舰 `tp_matmul.cu`（509 行）一文件两实验：块一"AG + Matmul"（:77-:267，m=n=64×nranks、k=64，X0 列切分经行主网格描述符聚合）；块二"Matmul + RS"（:269-:454），块一的输出 d_X1 直接作为块二的 B 操作数（:348）——正是 Megatron 前向的两步通信算子。它还演示性能关键组合：`ncclMemAlloc` 分配对称显存（:178）+ `cublasMpBufferRegister` 注册（:180），注册失败仅告警并退化为 NO_OVERLAP 非重叠算法（:183-:188）。双网格并存（:72-:73：nranks×1 列主 + 1×nranks 行主）是表达不同切分方向的手法。

## 外部连接

`helpers.h`（1526 行）是 MPI+NCCL 双后端枢纽：MPI_CHECK/NCCL_CHECK/CUBLASMP_CHECK 三宏（:40/:51/:73）；`MAKE_TYPE_TRAITS` 宏表覆盖 fp4/fp8×3/bf16/half/fp32/fp64 八类型（:127-:142）；`string_to_scale_type` 六种缩放模式（:207-:241，scalar_fp32 到 blk128x128_fp32，即 MXFP8/NVFP4 块缩放）。`Comm` 类（:801-:1133）是分布式生命周期容器：`MPI_Init_thread` 按 gpus_per_process>1 要求 FUNNELED 线程级（:824）、rank0 生成 NCCL UniqueId 经 MPI_Bcast 扩散（:922-:924）、SPMG（单进程多 GPU）模式下每线程一 GPU。`collective_launch`（:1025-:1132）用 std::thread 池执行 worker、exception_ptr 捕获首异常重抛（:1126-:1129）、三连 MPI_Allreduce 聚合错误/NOT_SUPPORTED/耗时（:1110-:1112）。`matmul.h`（896 行）则提供单卡参照系：`cublaslt_matmul`（:390-:576，全量 epilogue/缩放属性封装）与 `check_matmul_result`（:618-:895）。

## 数据流

标准流：main 里 designated initializer 填默认 Options（gemm.cu:464-:484）→ parse/validate（validate 强制 `(ia-1)%mbA==0` 的子矩阵对齐，helpers.h:672-:715）→ `Comm comm(nranks, gpus_per_process)` + `collective_launch(lambda)`（gemm.cu:496-:497）。验证流走"gather-再算-比对"：`gather_matrix`（helpers.h:1364，借 `cublasMpGemr2D` 把分布矩阵收到单卡）×4 → rank0 用本地 `cublasGemmEx` 重算（gemm.cu:151-:170）→ `allclose_device` 比对（:172，容差按类型 if constexpr 分级：fp8 rtol 6.5e-1、fp4 7e-1，helpers.h:1194-:1258）。窄精度缩放验证最精巧：`gather_scale_tensor`（matmul.h:307-:388）必须把各 rank 的缩放 tile 重排成 cuBLASLt 的 Tiled32x4x4 swizzle 全局布局（`scale_swizzle_offset` :131-:138，BC=32/BR=4/BI=4），单纯 AllGather 拼接是不够的（:303-:306 注释明言）。计时流：warmup+cycles 循环夹 cudaEvent（gemm.cu:335-:375），打印 GFlops（:501）。

## 设计决策

分布式正确性验证选"gather 到 rank0 + 单卡库重算"而非各 rank 局部验证——参照系复用成熟单库，代价是通信与显存峰值；FP64/FP32 仿真钩子统一在 helpers（`string_to_emulation_strategy` :243-:264，gemm.cu:285-:290 切 `CUBLAS_COMPUTE_32F_EMULATED_16BFX9`）；NOT_SUPPORTED 视作成功（`status_ok` :786-:789），让示例在老架构上优雅跳过而非失败。

## 新人提示

先跑 gemm -p 2 -q 1 理解 Numroc/lld 概念，再读 tp_matmul 看 AG/RS 描述符如何只用网格方向表达切分。改参数时牢记 ia/ja 必须落在块边界上（否则 validate 直接退出）；SPMG 模式（-gpus-per-process N）可在单机多卡上模拟多 rank。检查数值时先看 helpers.h:1194 的容差表——fp4 比对 rtol 0.7 是"设计如此"，不是算错。
