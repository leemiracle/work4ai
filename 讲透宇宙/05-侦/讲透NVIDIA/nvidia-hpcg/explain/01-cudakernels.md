# 01 · src/CudaKernels.cu — GPU 单体：从可压缩显存到向量化 CG kernel

## 一、角色定位

`src/CudaKernels.cu`（2792 行，约 90 个函数）是 NVIDIA HPCG 的 GPU 侧全部家当：显存生命周期、合成问题生成、halo 交换、图着色、SELL 构造、以及 cuSPARSE/cuBLAS 覆盖不到的自研 CG 支撑 kernel，全在这一个翻译单元里。它与 `src/CpuKernels.cpp` 构成 CPU/GPU 镜像对——两个 `AllocateMem*/ColorMatrix*/CreateSell*` 函数族签名一一对应，`OptimizeProblem.cpp` 双路径各调一边。

## 二、内部结构

按行号分五大函数族：

1. **显存族（50-425 行）**：`EstimateLUmem`（`src/CudaKernels.cu:146`）按层估 L/U 存储；`AllocateMemCuda`（`src/CudaKernels.cu:177`）分配 gpuAux/sellDev 双数组群；L2 压缩走 CUDA VMM 手工路径——`setProp`（`src/CudaKernels.cu:61`）填 `CUmemAllocationProp`，`cudaMallocCompressible`（`src/CudaKernels.cu:84`）按 `cuMemGetAllocationGranularity` 对齐后 `cuMemCreate`。
2. **生成族（727-1261 行）**：`generateProblem_kernel`（`src/CudaKernels.cu:727`）与 `setupHalo_kernel`（`src/CudaKernels.cu:936`）直接在 device 上生成 27 点问题和邻居映射——问题从不经过 host 中转。
3. **通信族（1290-1444 行）**：`ExchangeHaloCuda`（`src/CudaKernels.cu:1314`）一个函数五模式（`--p2p`）：MPI_CPU 走 pinned host 暂存+`copy_done` 事件（`src/CudaKernels.cu:1322`），NCCL 模式按邻居成对 `ncclSend/ncclRecv` 包进一个 group（`src/CudaKernels.cu:1422-1433`），`extMv_kernel`（`src/CudaKernels.cu:2586`）+`ExtSpMVCuda`（`src/CudaKernels.cu:2635`）补 halo 行外积 SpMV。
4. **着色/置换族（1446-2176 行）**：`minmaxHashStep_kernel`（`src/CudaKernels.cu:1459`）是 Jones-Plassmann/Luby 变体——`__brev(i)` 位反转当确定性哈希（`src/CudaKernels.cu:1468`），每轮同时选出局部 min/max 染两个颜色；`ColorMatrixCuda`（`src/CudaKernels.cu:1865`）宿主侧用手调颜色序 `{7,0,5,6,2,1,3,4}`（`src/CudaKernels.cu:1869-1877`）循环 4 轮，超 15 色时用 `testHashStep3_kernel`（`src/CudaKernels.cu:1505`）压缩色号，最后 `thrust::sort_by_key` 按颜色排序行号即得置换（`src/CudaKernels.cu:1954`）；`ellPermColumnsValues_kernel`（`src/CudaKernels.cu:1580`）一步产出列主序 SELL（转置在 kernel 内就地完成）。
5. **CG 支撑族（2330-2635 行）**：WAXPBY 向量化——`CgVectorWidth`（`src/CudaKernels.cu:2336`）进程内缓存一次探测，**sm_107（Rubin）取 V=4** 走 256-bit `double4_32a`（CTK≥13.4 才有，否则退化 `double4`，`src/CudaKernels.cu:2358-2362`），其余架构 V=2（`double2`）；`computeWAXPBY_kernel` 模板 `<THREADS,ROUNDS,V>` 带尾部标量回退（`src/CudaKernels.cu:2381`）。SYMGS 配角三件 `SpmvDiagCuda`/`AxpbyCuda`/`SpFmaCuda`（`src/CudaKernels.cu:2535`/`:2551`/`:2567`）。

## 三、外部连接

- **上游调用**：`OptimizeProblemGpu`（`src/OptimizeProblem.cpp:66`）消费着色+SELL 族；`ComputeSPMV`/`ComputeSYMGS`/`ExchangeHalo`/`ComputeWAXPBY` 分发层消费计算族；`src/main.cpp:461-462` 消费生成族。
- **依赖**：cuSPARSE（描述符）、cuBLAS（DDOT）、NCCL（可选）、thrust（count/sort/reduce 三处）。
- **被构建**：仅 `Makefile.ext:220-221` 的 nvcc 规则编译它（根 Makefile 无此目标）。

## 四、数据流

优化期一次性格局：CSR 原序 →（着色 kernels + thrust 排序）→ `ref2opt/opt2ref` →（`ellPermColumnsValues_kernel`）→ 列主序 SELL A + L/U 切片偏移 →（prefix-sum/slice-offset kernels，`src/CudaKernels.cu:2044`）→ 交给 cuSPARSE 描述符。迭代期热路径：`computeWAXPBY_kernel` 与 cuSPARSE/cuBLAS 句柄在 `stream` 上排队，`copy_stream` 专供 halo 的 H2D/D2H，两流靠 `copy_done` 事件交接（`src/CudaKernels.cu:1354-1357`）。

## 五、设计决策

- **确定性优先于最优**：着色不用随机数（`seed` 形参恒 0），哈希选 `__brev`，颜色序硬编码——同矩阵必得同置换，GPU/CPU 两路径共享同一序（CPU 侧展开后同值，`src/CpuKernels.cpp:684-686`）。
- **Ibarrier 优化已死**：SYMGS 在第 0 层传 `use_ibarrier=1` 想预热 Allreduce（`src/ComputeSYMGS.cpp:160`），但 `ExchangeHaloCuda` 内两处 `MPI_Ibarrier` 均被 `#if 0` 关闭（`src/CudaKernels.cu:1349`/`:1387`）——当前构建该参数是死参数。
- **架构分派最小化**：仅向量化宽度一处做运行时架构分派（sm_107 判定 `src/CudaKernels.cu:2343`），其余靠编译期 gencode 门控。

## 六、新人提示

先读 1446-1544 的三个着色 kernel（每个 <60 行，注释完整），再读 `ColorMatrixCuda` 宿主循环理解"4 轮双色 + 色号压缩"节奏；改 SELL 布局时注意 `IndexMode` 运行时宽度（offset 可能 32 也可能 64 位），kernel 侧一律用 `byteOffset()`/模板 `OffsetT` 取址，别直接解引用。`--l2cmp` 实验注意成绩不可提交（`src/main.cpp:193-196` 提示）。

---
*字数 3225（非空白字符）/锚 32（唯一 file:line 锚）*
