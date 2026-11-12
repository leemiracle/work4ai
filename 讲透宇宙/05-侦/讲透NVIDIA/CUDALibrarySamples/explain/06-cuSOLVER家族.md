# 06 cuSOLVER 家族：稠密分解、分布式求解与 cuDSS 迁移的四级跳

## 角色定位

cuSOLVER 家族横跨图谱两层（L09 cuSOLVER 域 102 节点 + L10 分布式与稀疏直接求解域 83 节点），是"稠密分解→多 GPU→稀疏直接→通信层测试"的四级跳板。`cuSOLVER/` 本体 30 个示例目录分三支：经典稠密 17 例（gesv/getrf/potrfBatched/syevd/syevj/sygvd/gesvd/gesvdj/orgqr/ormqr/csrqr 等）、Mg* 多 GPU 3 例（MgGetrf/MgPotrf/MgSyevd）、X* 64 位索引 10 例（Xgeev 到 Xtrtri）。勘误：README 首条链接指向不存在的 `MgGetrs/` 目录（实际目录名 MgGetrf）。

## 内部结构

`cuSOLVERMp/` 16 个示例（15 个 .c + 唯一 .cpp 的 mp_newton_schulz，540-777 行/个）结构高度统一：helpers.h（370 行）提供 parse（:169，getopt 循环）、validate、`getLocalRank`（:331，MPI_Comm_split_type SHARED 探本地 rank）与 `createNcclComm`（:343-:370，先广播 ncclGetUniqueId 的成败状态再广播 Id 本体——两段式防单点挂死）。以 `mp_potrf_potrs.c`（708 行）为型：main（:87）→ MPI_Init（:115）→ `cusolverMpCreate(&handle, localRank, stream)`（:178）→ `createDeviceGrid` 建网格（:305-:308）→ `createMatrixDesc`（:314-:318）→ bufferSize 双查（:346/:358）→ `cusolverMpPotrf`（:431）+`Potrs`（:465）→ gather 验证。三文件族精度的代码级对照是亮点：fp32 版与 fp32emulation 版 diff 仅 12 行——在 CUSOLVER_VERSION≥12000 下插 `cusolverMpSetMathMode(CUSOLVER_FP32_EMULATED_BF16X9_MATH)` 加 `SetEmulationStrategy`（mp_potrf_potrs_fp32emulation.c:181-:192），与篇 01 的 cuBLAS FP64 仿真同源同型。

## 外部连接

`cuSOLVERSp2cuDSS/` 是官方迁移教材：单头模板 `cuSolverSp2cuDSS.hpp`（441 行）承载全部逻辑，`driver<value_type>` 模板（:37）+ `--solver cudss|cusolver` 双后端开关（:60），日志直接点题"solver: cudss, hpd vs cusolversp, cholesky"（:78）；cudssHandle/Config/Data 三件套创建（:119-:121）与 lambda finalize（:123-:126）；关键语义差异写在注释里——显式重排序仅 cusolver 需要、"cudss does not need this process"（:183-:184）。四个 24 行薄 .cpp 各实例化一种 value_type（float/double/scomplex/dcomplex），utils.hpp（986 行）用 enable_if 分流实/复整族函数；另有 cuSolverRf2cuDSS.hpp（591 行，矩阵重因子化迁移）与 csreigs/csreigvsi 两个特征值示例（423/415 行）。

## 数据流

`cuDSS/` 23 个示例从 simple 走到通信层测试。三阶段执行是主干：`cudssExecute` 依次 ANALYSIS/FACTORIZATION/SOLVE（simple_mgmn_distributed_matrix.cpp:583-:594），MGMN 模式先注入通信器（:560，注释明示该模式"为大规模系统而生" :54）。最重的一篇是 `test_communication_layer/test_communication_layer.cu`（1017 行）：把通信后端做成 dlopen 插件——`dlopen(comm_layer_libname, RTLD_NOW)`（:889）+ `dlsym` 取 `cudssDistributedInterface_t` 函数表（:901）；编译期 openmpi/nccl 二选一互斥（:46-:51 双 #error）；接口版本门槛 0.8.0（:34-:36，运行时三段比较 :960-:976）；main 顺序跑九项测试：init_env_comm（:181）、bcast_raw（:190）、bcast_device（:236）、comm_rank_size（:271）、bcast_host（:291）、reduce_allreduce（:318）、send_recv（:420）、scatterv（:492）、comm_split_free（:605）。函数表 Host/Device 双轨成对出现（cudssBcastHost/Device 等），NCCL 后端的 host 侧 API 仍回退 MPI_Comm（`host_comm_world` :129-:134）。姊妹篇 test_threading_layer.cu 仅 209 行，对照鲜明。

## 设计决策

家族分工即架构决策：单机稠密（cuSOLVER）、多 GPU 分布式（cuSOLVERMp，2D 循环分布复用 ScaLAPACK 心智）、稀疏直接（cuDSS 三阶段显式化）、可插拔通信（dlopen 接口表而非编译期绑定——同一 cuDSS 库可自由换 openmpi/nccl 后端）。Sp2cuDSS 用"同一 driver 双后端"的 A/B 设计让迁移成本一目了然；cuSOLVERMp 的版本宏包裹仿真开关则保证老 CUDA 工具链可编译。utils 双头（cusolver_utils.h + cusolverMg_utils.h，后者含 IDX2F 宏）对应单机/多机两代 API。

## 新人提示

按 cuSOLVER/potrfBatched → MgPotrf → cuSOLVERMp/mp_potrf_potrs → cuDSS/simple 的顺序走完四级跳。cuSOLVERMp 全部示例默认 2×1 网格、每进程一卡（README 明言示例只为 API 教学不做性能）。跑 test_communication_layer 需自备通信层 .so 与 CUDA-aware OpenMPI；出错时看它的两段式 NCCL 初始化与 MPI_Abort 语义（:136-:146 注释强调"部分失败立即全组终止防挂死"）。读 Sp2cuDSS 先看 :183 的重排序差异注释——那是迁移最常踩的语义坑。
