# MatX 双后端线性代数：cuda/lapack 成对实现与 matmul 多后端

锚定 commit ce764c0。

## 一、角色定位

`transforms/` 是 MatX 的数值执行层：用户写 `(out = lu(a)).run(exec)` 惰性表达式，`operators/` 只做类型与形状检查，库调用全在 transforms 的 `*_impl` 自由函数里。本文覆盖线代子家族：五个成对分解目录（lu/chol/qr/svd/eig）+ solve/matmul/convert + `solver_common.h`、`solver_cusolverdx.h`，共 26 文件（全目录实为 58 文件）。

招牌设计是**同名双实现**：每个分解有两个同名 `lu_impl` 重载——`cudaExecutor` 版（`lu_cuda.h:264`）走 cuSOLVER 64 位 X API，`HostExecutor` 版（`lu_lapack.h:223`）走宿主 LAPACK，由重载决议按执行器（即数据所在域）自动选择；dispatch 证据 `operators/lu.h:154-156`：`is_cuda_executor_v<Executor>` 分流，else 进 LAPACK 分支。

## 二、内部结构

**成对文件模式**。cuda 版 plan 构造时先查 workspace（`cusolverDnXgetrf_bufferSize`，`lu_cuda.h:117`）再分配，lapack 版无需 workspace；chol/qr/svd/eig 同构（`chol_cuda.h:114` 对 `chol_lapack.h:167-173`）。

**两个基类**（`solver_common.h`）：`matxDnCUDASolver_t`（187 行）持有 cuSOLVER 句柄、workspace 与 `d_info`，纯虚 `GetWorkspaceSize()`（249 行）；`AllocateWorkspace`（218-247 行）区分 batched API（单份 workspace）与逐矩阵循环（`batches*dspace` 切片），且因 cuSOLVER 复数 bug 需先 memset。`matxDnHostSolver_t`（273 行）仅宿主工作区。

**缓存四件套**：每变换一套 Params+KeyHash+KeyEq+cache 别名；KeyHash 只哈希 `m/n/batch/stream`，KeyEq 追加 `dtype` 判等（`lu_cuda.h:215-232`）。

**matmul 六后端**：

| 后端 | 文件 | 场景 |
|---|---|---|
| cuBLASLt | matmul_cuda.h | device 默认（`matmul_cuda.h:65`） |
| CUTLASS | matmul_cuda.h | 编译期开关；C 列主序（1279 行）与 rank>4 批量（1187 行） |
| 宿主 CBLAS | matmul_cblas.h | HostExecutor；NVPL/OpenBLAS/BLIS（51-64 行） |
| cuBLASDx | matmul_cublasdx.h | device 侧块级 GEMM，JIT 生成供融合内联 |
| cuSPARSE SpMM | matmul_cusparse.h | 稀疏×稠密（206 行） |
| cuSPARSE SpMV | matvec_cusparse.h | 稀疏矩阵-向量（198 行） |

**LAPACK_CALL 宏**（`solver_common.h:37-58`）三路展开：NVPL→`NVPL_LAPACK_##fn`（44 行）、OPENBLAS→`LAPACK_##fn`（55 行）；都没有则宏不定义，`lu_lapack.h:51` 的 `#if MATX_EN_CPU_SOLVER` 整体不编译。

## 三、外部连接

**operator 层三重 include 门**（`operators/lu.h:41-46`）：`lu_cuda.h` 无条件包含；`solver_cusolverdx.h` 仅 `MATX_EN_MATHDX && __CUDACC__` 时包含（device 侧 JIT 求解）；`lu_lapack.h` 仅 `MATX_EN_CPU_SOLVER` 时包含。

**pivot 类型桥接**：cuda 版与 LAPACK 版对 pivot 类型要求不同（见第六节）；operator 层兜底，宿主路径类型不符时临时分配 `lapack_int_t` 张量跑完再逐元素转回（`operators/lu.h:159-181`）。

**core/cache.h 的 plan 缓存**：transform 共享单例 `GetCache()`（`core/cache.h:742`），核心 API `LookupAndExec`（`core/cache.h:222`）以外层键 thread+device、内层键参数查表，MISS 造 plan、HIT 直接执行。LU 接入点 `lu_cuda.h:297`，GEMM 在 `matmul_cuda.h:1476`。

**版本与宏门控**：`eig_cuda.h:128` 用 `CUSOLVER_VERSION>11701` 决定走原生批量 `XsyevBatched`（`eig_cuda.h:195`）还是逐矩阵 `Xsyevd` 循环。`support.h:57-60` 推出 `MATX_EN_CPU_SOLVER`。稀疏转换是两段式协议：`dense2sparse_cusparse.h` 的 bufferSize→analysis（131/139 行）→convert（214 行）。

## 四、数据流

**device LU 全链路**（`lu_cuda.h:264-313`）：① `OpToTensor` 物化表达式；② 行主序 WAR——cuSOLVER 只有列主序，`TransposeCopy` 转入列主序缓冲（`lu_cuda.h:284-288`）；③ 进缓存 `LookupAndExec`（297 行）；④ `Exec`（`lu_cuda.h:140`）内非原位先 `(out=a).run(exec)`，`SetBatchPointers`（`solver_common.h:140`）展平批量维；⑤ 逐矩阵循环调 `cusolverDnXgetrf`（`lu_cuda.h:168`，因"无批量 64 位 LU 接口"），workspace 按 `i*dspace` 切片；⑥ `d_info` 拷回后 `cudaStreamSynchronize`（`lu_cuda.h:179-183`，注释自认"会阻塞"），断言 `info<0` 参数非法、`info>0` 报 `U(i,i)=0` 奇异（`lu_cuda.h:185-192`）；⑦ `PermuteMatrix` 转置拷回。

**host LU 对照**（`lu_lapack.h:127-162`）：同构但更轻——`info` 栈变量直接读，批循环 `getrf_dispatch` 分派 `LAPACK_CALL(s/d/c/zgetrf)`（174-186 行）。

**matmul 数据流**（`matmul_cuda.h:1536`）：`as_type` 提升 A/B 到 C 类型 → `getCublasSupportedTensor`（`matmul_cuda.h:1383`）查末两维至少一个 stride==1，否则物化 → 列主序 C 用恒等式 `Cᵀ=BᵀAᵀ` 递归换序（1571 行）→ `WithMatmulOperand`（1417 行）优先把 `hermitianT/conj` 映射为 cuBLASLt 元数据操作（零拷贝）→ 查缓存 → `Exec`（651 行）→ `MatMulDispatchA/B/C`（1310/1289/1262 行）按 stride 判内存序，落 cuBLASLt 或 CUTLASS。

**solve 双计划**：`dense_solve_impl` 先把 A 转列主序（531 行），按 `DenseSolveCanUseCublasBatched`（`solve_cuda.h:123-133`，batches>1）选批量计划或 `Xgetrf`+`Xgetrs` 循环计划（343 行）。

## 五、设计决策

**为什么双后端**：同一表达式两域可跑，CPU 版是 GPU 版的正确性参照；维护代价用"基类+四件套"压到照抄 LU 骨架即可。

**行主序统一表象的隐藏税**：cuSOLVER/LAPACK/CBLAS 全列主序而 MatX 对外行主序，稠密求解器入口都要 `TransposeCopy` 进出各一次（278-288 行）；matmul 用恒等式把 C 的转置吸收进 GEMM（1571 行、`matmul_cblas.h:532`）零物化——**求解器付转置税，GEMM 不付**。

**批处理三策略**按上游能力择优：① 原生批量 API（eig `XsyevBatched`）；② 逐矩阵循环（LU，注释"等接口可用后改回"）；③ 运行时门控（solve 的 batches>1）。循环时 workspace 切片复用、`d_info` 整块分配（`solver_common.h:230/241`）。

**plan 缓存边界**：句柄创建与 cuBLASLt 启发式选算法（`matmul_cuda.h:959`）都贵，值得按参数缓存；但缓存键含 stream（`lu_cuda.h:219/230`），换 stream 即 MISS 重建。LAPACK 侧不缓存；手动清理 `ClearCaches()`（`core/cache.h:755`）。

**错误处理**：LAPACK `info` 完整翻译成异常——参数非法与奇异位置精确报出（`lu_cuda.h:186-191`）。

**甄别修正（以源码为准）**：① 任务书称 matmul_cuda.h 含"自研 tile kernel Exec L651"——不成立：该 `Exec` 属 `MatMulCUDAHandle_t`（270 行），仅分派到 `MatMulDispatchA`（658 行），落 cuBLASLt 或 CUTLASS；`kernels/` 目录无 matmul 内核，GEMM 完全外包。② singular 检测 cuda 版实际在 `lu_cuda.h:185-193`、host 版在 154-160 行。③ matmul_cblas.h 并非"cuBLAS 桥"：宿主分支仅 NVPL/OpenBLAS/BLIS。④ 基类实名 `matxDnHostSolver_t`。

## 六、新人提示

1. **pivot 双轨制是第一坑**：直接调 `lu_impl` 时 cuda 要 `int64_t`（`lu_cuda.h:108`）、host 要 `lapack_int_t`（`lu_lapack.h:106`）；走 operator 层自动桥接（`operators/lu.h:159-181`）。
2. LU 不支持 half（`lu_cuda.h:106` 静态断言）。
3. **cuBLASDx/cuSolverDx 是编译期双门控的实验性品类**：需 `MATX_EN_MATHDX && __CUDACC__`（`operators/lu.h:41-42`）。它们不是独立执行后端而是 JIT 融合引擎的能力项：运行时拼 device 函数源码（`matmul_cublasdx.h:370` 起），NVRTC 按符号前缀识别。
4. **稀疏乘法在 operator 层分流**：`is_sparse_tensor_v<OpA>` 走 `sparse_matmul_impl`（`operators/matmul.h:384-391`），稀疏只支持左操作数。
5. plan 不命中先查 stream 是否换了；新增求解器最短路径=拷一对 lu 文件、替换库调用与 Params 字段。
