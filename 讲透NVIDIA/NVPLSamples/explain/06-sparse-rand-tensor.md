# 06 · nvpl_sparse / nvpl_rand / nvpl_tensor：三个现代描述符式 API 库合讲

## 1. 角色定位

三个小目录展示 NVPL"现代描述符式 API"一支：`nvpl_sparse/`（8 个 C 示例+`example_helper.h`）演示稀疏 spmv/spmm/spsv，API 复刻 cuSPARSE（`spmv_csr.c:1-48` 的 1993-2023 NVIDIA 版权头透着 CUDALibrarySamples 血统）；`nvpl_rand/`（7 个 C++ 示例+`common.hpp`）演示单线程/多线程随机数，以 cuRAND 逐位一致为卖点；`nvpl_tensor/`（6 个子目录）是 cuTensor 风格张量 API。共性：handle/descriptor/op 三段式、显式 workspace 查询、错误码+宏检查。

## 2. 内部结构

**nvpl_sparse** 按"3 存储格式×3 算子"排布：spmv 有 COO/CSR/SELL 全三种，spmm 仅 COO/CSR，spsv 三种全有。公共件 `example_helper.h` 两件套：`sparseGetStatusString` 把 13 种 `nvpl_sparse_status_t` 映射为可读串（`:7-36`，保留 "kernel launch failure" 等 cuSPARSE 措辞）；`CHECK_SPARSE` 宏打印 `__LINE__`+状态串+码并返回失败（`:38-46`）。各示例走同一条四段流水线（以 `spmv_csr.c` 为标杆）：create handle（`:75`）→`create_csr`（`:78-81`，双 index 参数 `INDEX_32I`×2；COO 版仅一个，`spmv_coo.c:77-80`）→`spmv_buffer_size` 查外部缓冲（`:89-92`）→malloc→`spmv_analysis`（`:97`）→`spmv`（`:102`）→六个 destroy+free（`:107-113`）。SELL 见格式差异：`create_sliced_ell` 带 slice_size=2/values_size=12，列索引 -1、值 0.0 填充（`spmv_sell.c:54-70`）。spsv 另演示属性：`sp_mat_set_attribute` 挂 `FILL_MODE_LOWER`+`DIAG_TYPE_NON_UNIT`（`spsv_csr.c:85-92`），X={1,8,23,52} 解得 {1,2,3,4}，即同一矩阵的下三角求解。验证用直接浮点相等，注释自认 "not reliable"（`spmv_csr.c:117-119`），靠示例值全为精确可表示整数撑腰。

**nvpl_rand** 按库分两组：`add_rand_example` 链单线程 `nvpl::rand`，`add_rand_mt_example` 链 `nvpl::rand_mt`（含全部单线程 API，`CMakeLists.txt:55-61`）。单线程代表 `rand_st_distribution_config.cpp`：MRG32K3A（`:14`），专用 API `GenerateUniformRangeDouble` 与通用分布 API `GenerateDistributionDouble`+config 结构对照（`:20/:23-27`），再演示 Dirichlet order-4（`:38-41`）。多线程 API：`nvplRandMTCreateGenerator(gen,PHILOX4_32_10,64)`、`MTCreateGeneratorDefault`、`MTSetGeneratorOrdering`（`compare_curand.cpp:16/:19`）。两组一致性对照是灵魂：① `compare_st.cpp` 证同 seed/offset 下 MT 设 `ORDERING_STRICT` 与 ST 逐位相同（`:28/:42`）；② `compare_threads.cpp` 证 STRICT 下线程数不影响序列（`:18-27`）。与 cuRAND 对照须切 `ORDERING_CURAND_LEGACY`（对应 `CURAND_ORDERING_PSEUDO_LEGACY`）才逐位相等（`compare_curand.cpp:19/:47`）——ordering 枚举是跨库兼容的钥匙。该文件双轨验证：有 CUDA 时真拉 cuRAND 比向量（`:31-80`）；无 CUDA 走 **xor 哈希兜底**——全序列异或对金常数，Philox `0xc7042bf2`（`:87`）、SOBOL64 `0xa75c795246aa956c`（`compare_curand_sobol.cpp:92`）。`common.hpp` 三宏：`NVPL_RAND_CHECK`（`:7-13`）+条件编译的 `CUDA_CHECK`/`CURAND_CHECK`（`:19-32`），全 `_Exit(EXIT_FAILURE)`。另 `verify_version.cpp` 断言 `nvplRandGetVersion`==编译期宏；`rand_mt_generate_normal_fp64.cpp` 以 PCG 生成正态样本后 Kahan 补偿求和算统计量（`:24-56`）。

**nvpl_tensor** 六子目录=六类算子（version/contraction/reduction/permutation/elementwise_binary/elementwise_trinary），除 version 外同构于 `contraction.c`：create handle→`SetNumThreads(4)`（`:124`）→`CreateTensorDescriptor`（对齐 128，`:131-140`）→建操作描述符 `CreateContraction`（`:147-149`）→查 `SCALAR_TYPE` assert（`:156-159`）→`CreatePlanPreference`+`EstimateWorkspaceSize`+`CreatePlan`（`:168/:176/:183`）→执行 `nvpltensorContract`（`:191-210`）→逆序销毁（`:214-219`）。各算子差异浓缩在描述符/执行一对：reduction `CreateReduction`/`Reduce`（`reduction.c:156/:208`）、permutation `CreatePermutation`/`Permute`（`permutation.c:154/:204`，无 workspace 参数）、binary/trinary `CreateElementwiseBinary/Trinary`+`Execute`（`elementwise_binary.c:154/:207`；trinary 三系数见 `elementwise_trinary.c:243`）。每文件自带 `HANDLE_ERROR`+`nvpltensorGetErrorString`（`contraction.c:10-18`）。

## 3. 外部连接

sparse 顶层 `find_package(OpenMP REQUIRED COMPONENTS C)`+`find_package(nvpl REQUIRED COMPONENTS sparse)`（`CMakeLists.txt:10-12`），子目录却链**裸名 `nvpl_sparse`** 而非 `nvpl::sparse`（`c/CMakeLists.txt:8`），目标加 `c_` 前缀、file(GLOB) 收录（`:3-9`）。rand 的 CMake 最扎眼：`:41` `set(CUDAToolkit_FOUND FALSE CACHE BOOL "")` 硬编码——把 `:40` 注释掉的 `find_package(CUDAToolkit)` 结果钉死 FALSE，连带 `:118` 注释掉的 curand/cudart 链接，`NVPL_RAND_EXAMPLE_CURAND_AVAILABLE` 永不定义（`:129-131`），xor 兜底成为实际路径。tensor 顶层 `find_package(nvpl REQUIRED COMPONENTS tensor)`（`CMakeLists.txt:8`）；`nvpl_tensor_version` 同构 `_c`/`_cxx` 两可执行（`nvpl_tensor_version/CMakeLists.txt:11-16`），源码逐行等价只差 `<stdio.h>`/`<cstdio>`（`nvpl_tensor_version.c:5` vs `.cxx:5`），证明头文件 C/C++ 双语言开箱即用。线程模型三对照：sparse 链 OpenMP、rand 靠 rand_mt 内部并行、tensor 走 `SetNumThreads` API。

## 4. 数据流

sparse：宿主端数组描述矩阵（CSR=offsets+columns+values；COO 加 rows；SELL=sliceOffsets+填充）→描述符仅存指针不拷数据→analysis 预研→execute 原地写输出；spmv/spmm 均有"第四描述符复用输出缓冲"细节（vecZ 建在 Y 上，`spmv_csr.c:86-87`；matD 建在 C 上，`spmm_coo.c:93`），示范 in-place。rand：create→设 seed/offset/ordering→generate 直写宿主 vector（与 cuRAND 的 cudaMalloc/memcpy 往返对照，`compare_curand.cpp:40/:57`）。tensor：`rand()` 初始化的连续数组+extent/mode 描述→plan 固化策略与 workspace→execute 消费原始指针；`C_{0,2,1,3}=alpha*A_{0,4,5,1}B_{2,5,3,4}+beta*C`（`contraction.c:31-33`）即 mode 标签数组（`:35-40`）的记法，共享标签即收缩维。

## 5. 设计决策

①**验证策略三档**：sparse 精确值比较（输入全整数使输出精确可表示）、rand 逐位相等+xor 金常数（位级可复现是硬规格）、tensor 不验证数值只 assert 元数据（`contraction.c:159/:196`）——强度与结果可预测性成正比；②**workspace 显式化**：sparse 的 buffer_size/analysis 与 tensor 的 Estimate/CreatePlan/REQUIRED_WORKSPACE 都把临时内存决定权交还调用者，GPU 生态礼仪在 CPU 库全盘保留；③**ordering 枚举是兼容枢纽**：STRICT 保库内一致、CURAND_LEGACY 保跨库逐位一致，两个 compare 各绑一个枚举值，把"什么时候序列会变"做成可执行文档。

## 6. 新人提示

顺序：`spmv_csr.c`（最完整四段式）→`spsv_csr.c`（属性设置）→`rand_st_distribution_config.cpp`→两个 compare→`contraction.c`（最长模板）。坑：① sparse 的 destroy 与创建严格逆序，少一个即泄漏，示例列全就是当清单抄；② MT 不设 `ORDERING_STRICT` 则与 ST 及不同线程数结果都不一致，跨机复现先固定 ordering+seed/offset；③ CUDAToolkit 被硬编码关闭，要跑真 cuRAND 对照需删 `nvpl_rand/CMakeLists.txt:41` 并解开 `:40/:118` 注释；④ tensor 示例不校验数值，别当正确性参考实现；⑤ `rand()/RAND_MAX` 是整型除法恒 0（`contraction.c:104`），示例输入实际全是常数——教学无碍，别学这行生成测试数据。
