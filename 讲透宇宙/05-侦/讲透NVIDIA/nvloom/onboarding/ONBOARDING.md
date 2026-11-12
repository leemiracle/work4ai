# 讲透 nvloom：MNNVL fabric 跨节点测试工具 Onboarding

> 仓库：`NVIDIA/nvloom` @ commit `c2995c1e`（v2.2.0，2026-10-19）｜图谱 108 节点/225 边/4 层/6 步导览，fingerprints 23 文件
> 本文所有 `file:line` 锚均为主会话对源码逐一核实的结果（2026-11-09）。

## 一、这个仓库是什么：给 NVLink fabric 做体检的工具

nvloom（NV "loom"=织机，织起多节点 NVLink 网）是 **MNNVL（Multi-Node NVLink）fabric 的可扩展带宽/延迟测试工具**，以 library（libnvloom.so）+ CLI（nvloom_cli）双形态发布。它测的不是单卡 memcpy，而是**跨节点 GPU 显存互访**：GB200 这类把多台机的 GPU 用 NVLink fabric 直连的域里，任意两张卡（甚至跨机架）之间的读写带宽、组播吞吐、fabric 拥塞行为。

README 给出运行约定与量级感：依赖 CUDA 13.0 / 580 驱动 / MPI / Boost.program_options 1.74（`README.md:12-17`）；**每 GPU 一进程**的 MPI 模型——"benchmarking 72 GPU GB200 MNNVL domain" 就是在 18 节点上各起 4 个进程（`README.md:66`）。工具自带运行时长观：pairwise 套件是 O(n²)（与 nvbandwidth 兼容而保留，`README.md:98`），大域推荐 `gpu-to-rack`/`fabric-stress`/`rack-to-rack` 三个线性或饱和型套件（`:102-104`），冒烟用 `bisect_write_sm`——"completes in around 3 seconds on a 72-GPU MNNVL domain"（`:116`）。

CHANGELOG 显示这是一个快速演化的工具（`CHANGELOG.md:3` 起 v2.2.0，2026-10-19）：v2.2 加本地化 CE 基准、CFT all-to-one/all-from-one、JSON 输出（实验性）、clique 探测（cuDeviceGetCliqueInfo）；v2.1 引入 **CFT（CUDA Compute Fabric Transport）**编程模型与全随机/环/二分 fabric stress；CFT 句柄从逐分配改为按 testcase 池化。许可 Apache-2.0；**不接受外部贡献**——CONTRIBUTING.md 是一行拒绝文本（见勘误）。

## 二、分层全景：四层地图

| 层 | 内容 | 代表文件（锚） |
|---|---|---|
| L01 配置与文档（5 文件） | README/CHANGELOG/顶层 CMake/样例 Dockerfile | `README.md:49`、`CMakeLists.txt`、`Dockerfile:4` |
| L02 库契约与引擎（6 文件） | nvloom.h 公共 API 面、nvloom.cpp 基准引擎、枚举/错误宏 | `library/nvloom.h:182`、`library/nvloom.cpp:506`、`library/enums.h:25` |
| L03 分配器与 kernel（4 文件） | 26 类型分配器族 + 12 个 `__global__` kernel | `library/allocators.h:46`、`library/kernels.cu:64` |
| L04 CLI 应用（8 文件） | 选项解析、用例工厂、CSV 扩展、输出矩阵、可视化 | `cli/nvloom_cli.cpp:96`、`cli/testcases.cpp:735`、`cli/plot_heatmaps.py` |

构建线：顶层 `CMakeLists.txt`（66 行，CUDA+CXX 双语言、C++17/CUDA17、Release 默认）聚合 `library/` 与 `cli/`；`library/CMakeLists.txt:42` 产出 SHARED libnvloom.so，链 cuda/nvidia-ml/Boost（`:44`）与 MPI（`:54`），`-DMULTINODE` 宏在 `:55` 开启多节点路径。**架构面是条件化的**：CUDA 编译器 ≥13.4 才编 `90;100;103;107` 四架构，否则 `90;100;103` 三架构（`library/CMakeLists.txt:46-49`）——"sm90-107 四架构"的说法要看工具链版本。Dockerfile 是两阶段样例（devel 用 `nvidia/cuda:13.4.1-devel-ubuntu24.04` 构建，`:4`；runtime 只带 openmpi/python3/uv 与两个产物，`:17-22`），官方注明仅为样例、不强制容器。

## 三、库核心：NvLoom 门面与 Benchmark 引擎

`library/nvloom.h`（285 行）是全部用法的起点，四个关键类型：

- **MPIWrapper**（`:44`）——进程拓扑与通信的单例封装（`:62` 的静态实例）；
- **Copy/Latency 拷贝描述**（`:80-95`）——一次测量的原子单元：目标/源 `MemoryAllocation` + 方向 + `CopyType copyType`（`:80`）+ `executingMPIrank`（`:81`），构造器 `Copy(...)` 在 `:84`；`Latency`（`:94-95`）是退化特例；
- **Benchmark 引擎**（`:128`）——持有 copies/filteredCopies/streams，状态机 `BenchmarkState` 五态：NOT_STARTED→WARMUP→SYNCHRONIZE→RUNNING→EXTRA_WORK（`:120-126`）；
- **NvLoom 门面**（`:182`）——静态入口 `doBenchmark`/`doBenchmarkCore`（`:208-209`）、初始化与系统检查；辅助面 `filterCopyType`（`:271`）与 `getCopyTypeName`（`:279`）。

实现 `library/nvloom.cpp`（1019 行）的主线：`NvLoom::initialize`（`:847`）接设备号与机架映射；`doBenchmark`（`:506-553`）是总入口，核心测量在 `doBenchmarkCore`（`:468`）；warmup 是显式状态（`:569` 的 warmup 标记）；**spin-kernel 负载维持**是独门设计——`spinKernelMultistage` 让非参与 rank 的 SM 保持占用（`:312` 的调用点，`:479` 的开关），防止空闲 GPU 进低功耗态污染带宽读数。错误处理是四级断言宏 `ASSERT/CU_ASSERT/CUDA_ASSERT/NVML_ASSERT`（`library/error.h:59/70/86/99`），失败时带 `hostname:device` 上下文打印并转储驱动日志（`getCudaLogs`，`error.h:39`）。

## 四、枚举坐标系：CopyType 18 形态与三分配策略

`library/enums.h`（73 行）定义了全仓的命名中枢。**CopyType 实测 18 个枚举值**（`:25-46`；图谱摘要记 19，勘误见 README）：CE（驱动 copy engine）、LOCALIZED_CE（本地化 CE，v2.2 新增）、SM（kernel 拷贝）、组播四态（WRITE / LD_REDUCE / RED_SINGLE 单 GPU 发 multimem.red / RED_ALL 全体发）、LATENCY（pointer-chase）、TMA 三态、CFT 七态（READ/WRITE/WRITE_MULTICAST/RED_SINGLE/RED_ALL/PULLRED）。组播 RED_SINGLE 与 RED_ALL 执行同一 kernel 但校验算法不同（`:31-34` 注释）。配套枚举：CopyDirection（`:20`）、MemoryPurpose 源/目的（`:49`）、FillPattern 校验填充（`:54`）、CliqueSharing（`:62`）。

分配策略三选一（CLI `--allocatorStrategy`，默认 reuse，`README.md:174-180`）：`unique` 每次测量新分配、`reuse` 复用、`cudapool` 走 CUDA Stream-Ordered 分配器（组播仍走 unique）。这个策略维在测试空间里与 CopyType 正交——工厂层用 6 个分配器模板参数把它编译期展开（见第五节）。

## 五、分配器族与 kernel 家族：MNNVL 的数据面

### 26 类型分配器树（library/allocators.h 511 行 / allocators.cpp 962 行 53 方法）

根类 **MemoryAllocation**（`:46-89`）持 ptr/allocationSize/MPIrank 与静态 uniqueIdCounter；`library/README.md:24` 明言"meant to be a base for inheritance of your custom allocators"——自定义分配器继承指南是官方文档。家族按语义分层：

- 单节点侧：DeviceMemoryAllocation（`:91`）、HostMemoryAllocation（`:102`）、MemoryChunk（`:40`，struct）；
- 多节点骨架：MultinodeMemoryAllocationBase（`:112-124`，fabric 句柄交换/跨节点映射公共面）→ Unicast（`:126`）、Localized Unicast（`:136`，配 LOCALIZED_CE）、EGM（`:172`，扩展 GPU 显存）；
- 组播支：MulticastRef（`:334-359`，组播绑定/解绑引用语义）→ Multicast（`:386`）、MulticastCudaPool（`:410`）、CFT 组播双支（`:310/:312/:361`）；
- 池化支：UnicastLogicalEndpoint（`:204`）+Pool（`:233`）、RangeAllocator（`:185`）、MemoryChunkAllocation（`:162`）、MultinodeMemoryPoolAllocation*（`:416-433`）、AllocationPool（`:444`）与 MulticastPool（`:474`）。

实现面 `allocators.cpp` 是 CUmemAllocation 级 API 的封装层：VMM 物理句柄创建、fabric 句柄经 MPI 交换、cuMemMap/cuMemSetAccess 跨节点映射、组播组创建（cuMulticastCreate 系）。**分配器族是 CUmemAllocation 系列驱动 API 的教科书式应用**——想学 CUDA VMM 多节点编程，读这 962 行比读文档直白。

### 12 个 __global__ kernel（library/kernels.cu 991 行）

tree-sitter 对 .cu 零提取，12 个 kernel 全部批阶段手扫（行号已核实）：stridingMemcpy（`kernels.cu:64`）与 simpleMemcpy（`kernels.cu:116`）是 SM 拷贝双形态；memcpyKernelTma（`kernels.cu:300`）TMA 拷贝；CFT 三件 cftPut/cftGet/cftPullred（`kernels.cu:517`、`kernels.cu:562`、`kernels.cu:605`）；spinKernelDeviceMultistage（`kernels.cu:706`）负载维持；patternFill/patternCheck（`kernels.cu:747` 与 `kernels.cu:812`）校验数据的发生与核对；pointerChaseFill/pointerChase（`kernels.cu:886` 与 `kernels.cu:905`）延迟测量；getSmIds（`kernels.cu:927`）SM 拓扑探测。底层大量内联 PTX：cp.async.bulk、TMA mbarrier、multimem.ld/st/red、fabric 专用指令。声明面 `kernels.cuh`（65 行）的 copyKernel 全家族在 `:30-38`，**CFT 五声明包在 `#if CUDA_VERSION >= 13030` 里**（`:39-44`）——CFT 需要 CUDA 13.3+ 工具链，这是构建的前提条件之一。

## 六、CLI 与用例体系：从选项到热力图

`cli/nvloom_cli.cpp`（363 行）：`run_program`（`:96-354`）用 boost::program_options 定义 20+ 选项（bufferSize/allocatorStrategy/suite/testcase/TMA 块大小/带宽单位/jsonOutput 等），解析后 MPI 环境里构建用例表循环执行；`shouldContinue`（`:45-63`）实现按 duration 的循环控制（rank 0 决策 + `MPI_Bcast` 广播，`:56-58`）。

用例抽象两层（`cli/testcases.h` 79 行）：`Testcase` 基类纯虚 `run`（`:46-48`）+ `TestcaseDstSrc` 单源单目的骨架（`:66`）。**内置用例是模板类矩阵**（`cli/testcases.cpp`）：N_squared_pattern（`:98`）、N_squared_bidir（`:122`）、bisect_pattern（`:147`）、fully_random_pattern（`:190`）、random_ring（`:234`）、all_to_one（`:319`）、all_to_one_rack_aware（`:337`）、multicast_one_to_all（`:377`）/all_to_all（`:418`）/ld_reduce（`:446`）/red（`:469`）、gpu_to_rack（`:533`）……工厂总入口 `buildTestcases(AllocatorStrategy)`（`:929`）按三策略把 `buildTestcasesLower`（`:735`）的模板组合实例化（pairwise 套件的 CE/SM × 读写四连发在 `:740-743`）；`addTestcase`（`:719`）登记用例与套件归属；gpu-to-rack 的随机采样器是 `pickRandomSamplesWithSkip`（`:495`，`:571` 处按 gpuToRackSamples 使用）。

**CSV 扩展通道**（`cli/csv_testcase.h:122-140` 的 csv_pattern 模板类，携带 6 个分配器模板参数）：用 CSV 文件描述 AllocationDescription（`:23-66`）与 CopyDescription（`:68-120`），`run`（`csv_testcase.cpp:36`）解析 CSV→逐 copy 过滤→`MPI_Allreduce` 全体裁决支持性（`:52`，MPI_LAND）→组装 Copy→交给 `NvLoom::doBenchmark`。这意味着**新测试模式可以不改 C++ 就描述出来**。

输出侧：`OutputMatrix`（`cli/util.h:40`，MeasurementType 枚举 `:42`、StatisticsStrings 四统计 `:47`）聚合 min/max/avg/med；`util.cpp` 提供机架发现 `discoverRanks`（`:84`，按 hostname 聚类成 rack→rank 映射，rack-aware 用例的拓扑基础）、JSON 输出 `printJson`（`:229`）/`setJsonOutputFile`（`:202`）、字节后缀解析 `getBufferSizeInBytes`（`:288`）。可视化 `cli/plot_heatmaps.py`（488 行）把 CSV 渲染成机架×GPU 热力图/直方图，依赖以 PEP 723 内联声明（`README.md:246`），推荐 `uv` 运行。

## 七、运行方式、设计决策与新人路线

**跑起来**（README.md:66-80）：MPI 每 GPU 一进程启动（如 18 节点 ×4 进程=72 GPU），`nvloom_cli -s <suite>` 选套件；无参全跑不被推荐（`:80`）。大域建议三件套 `gpu-to-rack rack-to-rack fabric-stress`（`:109` 给出命令行）；冒烟 `bisect_write_sm` 约 3 秒。结果 CSV→`plot_heatmaps.py` 出图，或 `--jsonOutput`（实验性）。

**四个关键设计决策**：

1. **每 GPU 一进程而非单进程多 GPU**：MPI rank 与 GPU 一一对应，fabric 拓扑发现（hostname 聚类）建立在进程模型上——这与 NCCL/nccl-tests 的习惯一致，但让"谁在写谁"的矩阵输出天然可读；
2. **测量空间三维正交**：CopyType（18）× 分配策略（3）× 用例模式（12+ 模板类）在编译期模板展开、运行期选择——膨胀的是二进制体积，换来的是零虚函数开销的测量路径；
3. **spin-kernel 负载维持 + warmup 状态机**：把"空闲 GPU 降频污染带宽"这个 fabric 测量的经典噪声源显式管起来（`nvloom.cpp:312/479`）；
4. **数据校验内建**：FillPattern 伪随机填充+核对（kernels `:747/:812`），组播 RED_SINGLE/RED_ALL 同 kernel 异校验（`enums.h:31-34` 注释）——带宽数字带正确性背书。

**新人路线**（对应图谱 6 步导览）：README→`nvloom.h` 通读（285 行）→`enums.h`（73 行）建立坐标系→`kernels.cu` 挑 stridingMemcpy（`:64`）读一个 kernel→`testcases.cpp` 读 N_squared_pattern（`:98`）看用例如何组装分配器→跑一次 `bisect_write_sm`→按专题深入：学 VMM 进 `allocators.cpp`，学 TMA/CFT 进 `kernels.cu:300/:517`，做报告进 `plot_heatmaps.py`。

**三个坑**：CFT 路径需要 CUDA ≥13.3（`kernels.cuh:39`）且驱动 580+；sm107 需要 CUDA ≥13.4（`library/CMakeLists.txt:46`），工具链旧了架构面静默缩水；pairwise 套件在 72 GPU 域是 O(n²)——兼容 nvbandwidth 用的，大规模别全跑。
