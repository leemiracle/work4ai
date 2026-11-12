# nvidia-hpcg 仓库 Onboarding

> 仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-hpcg`（commit abe78e0，自称 Build v0.6.2，`src/main.cpp:168`）；图谱规格 258 节点/481 边/10 层/12 步（fp=126 文件）。**本文全部行号锚经源码逐条核实**（源码直读法产出；仓内图谱经复核自洽无污染——初判"串拷"系相对路径误读父会话工作目录所致，详见 README 勘正注记）。

## 1. 这是什么仓库

NVIDIA 版 HPCG 基准：对 Sandia HPCG 3.1 的官方 NVIDIA 加速改写。基准本体是"固定 50 次迭代的 multigrid 预条件共轭梯度（对称 Gauss-Seidel 平滑子）"（`README.md:7`），性能分来自优化路径。NVIDIA 版的差异化：稀疏矩阵全程用 **sliced-ELLPACK（SELL）** 格式（`README.md:20`），SpMV/SpSV 下沉到 cuSPARSE（GPU）与 NVPL Sparse（Grace CPU）两个 NVIDIA 数学库（`README.md:10`），并支持 GPU-only / CPU-only(aarch64) / Grace Hopper 异构 GPU+CPU 三种执行模式（`--exm`，`src/init.cpp:360`）。

## 2. 五分钟心智模型

- **两套实现并存**：每个算子都有 `X.cpp`（优化版，按 rank 类型分发 GPU/CPU）与 `X_ref.cpp`（上游参考版），目录即对照系。
- **rank 类型驱动一切**：`InitializeRanks`（`src/init.cpp:112`）给每个 MPI rank 定 GPU/CPU 身份；此后 `ComputeSPMV`/`ComputeSYMGS`/`ComputeDotProduct` 等分发层全部按 `A.rankType` 二分（GPU→cuSPARSE/cuBLAS 路径，CPU→NVPL 路径）。
- **优化=重排**：`OptimizeProblem`（`src/main.cpp:649`）做图着色，把行/列按颜色重排成颜色连续的 SELL 布局，`ref2opt`/`opt2ref` 双置换表贯穿始终（进出优化路径都要置换向量，`src/main.cpp:741`/`src/main.cpp:937`）。
- **通信三件套**：halo 交换 `--p2p` 五模式（`src/CudaKernels.cu:1314`）、DDOT 全局归约 `--ar` 独立后端（`src/main.cpp:114` 的 `Dot_Allreduce_Mode`，解析于 `src/main.cpp:282-298`）、NCCL communicator 仅在 GPU-only+NCCL halo 时建立（`src/init.cpp:208`）。

## 3. 目录地图

| 位置 | 职责 |
|---|---|
| `src/` 根 | 驱动与算子分发：`main.cpp`（1026 行九阶段主流程）、`init.cpp`（参数/rank 划分/NCCL init）、`OptimizeProblem.cpp`（着色+SELL 构造）、`CG.cpp`（PCG 主迭代）、各 `Compute*.cpp` 分发器；`*_ref.cpp` 参考实现 |
| `src/CudaKernels.cu` | 2792 行 GPU 单体：内存分配（含可压缩显存）、问题生成、halo、着色、SELL 构造、向量化 CG 支撑 kernel，约 90 个函数 |
| `src/CpuKernels.cpp` | 1562 行 CPU 镜像：NVPL 路径的着色（`ColorMatrixCpu`，`src/CpuKernels.cpp:667`）、SELL 重排（`CreateSellPermCpu`，`src/CpuKernels.cpp:811`） |
| `src/IndexMode.hpp` | SELL 索引宽度运行时三态 I32_I32/I64_I32/I64_I64（`src/IndexMode.hpp:67-71`），统一映射 cuSPARSE/NVPL 索引类型 |
| `nvidia-cpu/` | **独立子构建**：按 MIDR_EL1 探测 CPU 型号（Neoverse-V2=Grace / Olympus=Vera，`nvidia-cpu/dispatch/hpcg_cpu_detect.h:24-29`），dlopen 对应调优 .so |
| `bin/` | `hpcg.sh`/`hpcg-aarch64.sh` 启动器（亲和性绑定）、`RUNNING-x86`/`RUNNING-aarch64` 运行手册、`TUNING`、`sample-*` |
| `setup/` + `configure` + `Makefile.ext` | 真构建链（根 `Makefile` 不含 GPU 对象，见 §6） |

## 4. 分层走读

自上而下六层：

1. **入口与参数**（init.cpp）：22 个 CLI 选项 `cparams`（`src/init.cpp:256-258`）；无几何参数时回退读 `./hpcg.dat`（`src/init.cpp:302`）；维度 <16 强制抬到 16（`src/init.cpp:320`）。`--gss` GPU slice 默认 **4096**、`--css` CPU slice 默认 8（`src/init.cpp:426`/`src/init.cpp:429`）。
2. **问题生成**（GPU 路径在 device 上直接生成）：`generateProblem_kernel`（`src/CudaKernels.cu:727`）→ `setupHalo_kernel`（`src/CudaKernels.cu:936`）→ 四层粗化 `GenerateCoarseProblem`（`src/main.cpp:463-467`，层数硬编码 4 于 `src/main.cpp:428`）。
3. **优化阶段**：GPU 在 `OptimizeProblemGpu`（`src/OptimizeProblem.cpp:66`）内完成"着色→置换表→SELL 直构→三个 `cusparseCreateSlicedEll` 描述符（L/U/A，`src/OptimizeProblem.cpp:138-153`）→SpMV/SpSV 缓冲查询与 analysis"；CPU 在 `OptimizeProblemCpu`（`src/OptimizeProblem.cpp:257`）走 NVPL 镜像流程。
4. **计算层**：PCG 迭代（`src/CG.cpp:151`）按 rank 分发——SpMV=`cusparseSpMV`（`src/ComputeSPMV.cpp:78`）+halo 行外积 `ExtSpMVCuda`（`src/ComputeSPMV.cpp:85`，kernel 在 `src/CudaKernels.cu:2635`）；SYMGS=两次 `cusparseSpSV_solve` 夹一次对角 SpMV（见 §7）；DDOT=`cublasDdot`+NCCL/MPI 归约（`src/ComputeDotProduct.cpp:90-121`）；WAXPBY=自研向量化 kernel（`src/CudaKernels.cu:2414`）。
5. **通信层**：`ExchangeHaloCuda` 五模式（MPI_CPU/MPI_CUDA_AWARE/MPI_GPU_All2allv/MPI_CPU_All2allv/NCCL，`src/CudaKernels.cu:1322-1435`），NCCL 模式按邻居成对 `ncclSend/ncclRecv` 包在 group 里（`src/CudaKernels.cu:1422-1433`）。
6. **CPU 派发子系统**（nvidia-cpu/）：每 CPU 一份调优 .so + 通用 armv8-A dispatcher 运行时按 MIDR 选库（`nvidia-cpu/Makefile:18-31`）。

## 5. 数据流与控制流

main 九阶段：HPCG_Init→几何/库版本闸（cuSPARSE≥12.2 `src/main.cpp:387`；大 slice 再闸 ≥12.5 `src/main.cpp:631`）→问题生成→参考计时（benchmark 模式跳过，`src/main.cpp:598-604`）→OptimizeProblem→验证（TestCG/TestSymmetry `src/main.cpp:722-725`）→b 向量置换入优化序→warmup（--wt，全局 Allreduce 取 max 判停 `src/main.cpp:807`）→校准→定时 CG 循环：`numberOfCgSets = runningTime/opt_worst_time+1`（`src/main.cpp:887`），容差强制 0、迭代数固定（`src/main.cpp:899-900`）→x 置换回参考序→ReportResults。计时桶 t1-t5 记 DDOT/WAXPBY/SPMV/AllReduce/MG（`src/CG.cpp:231-235`）。

## 6. 构建与运行

`build_sample.sh` 在 `build/` 里跑 `configure`（把 `Makefile.ext` sed 成 `build/Makefile`，`configure:34`），再 `make`。**三个易踩点**：①根 `Makefile` 的 `HPCG_DEPS` 不含 `CudaKernels.o/CpuKernels.o`（`Makefile:32-42`），真正链接靠 `Makefile.ext:71-72`；②全部 .cpp 也经 **nvcc** 编译（`setup/Make.CUDA_X86:203-204`，`CXX=nvcc` + `-Xcompiler -Ofast,-fopenmp,-mcpu=native`），CUDA gencode 按工具链版本门控 sm_80/90→100/120→103→107（`setup/Make.CUDA_X86:186-197`）；③`build_sample.sh:53-73` 用第 5/6/7 位置参数控 USE_CUDA/USE_AARCH64/USE_NCCL。运行用 `bin/hpcg.sh`：按 local rank 查 GPU/CPU/MEM/NET 亲和表（`bin/hpcg.sh:383-402`），`numactl --physcpubind/--membind` 包住二进制（`bin/hpcg.sh:404-421`），并设 `OMP_PROC_BIND=TRUE`/`OMP_PLACES=sockets`（`bin/hpcg.sh:30-31`）。

## 7. 设计决策与陷阱

- **SYMGS 不是顺序 Gauss-Seidel**：`ComputeSYMGS_Gpu` 把一次对称扫重构成"TRSV(D+L)→对角 SpMV→TRSV(D+U)"两遍三角求解（`src/ComputeSYMGS.cpp` step 分支，halo 行外积并入第二遍，`src/ComputeSYMGS.cpp:132`）；对角线经 `cusparseSpSV_updateMatrix` 热更新（`src/OptimizeProblem.cpp:209-210`），避免 D 存两份。
- **着色确定性**：Jones-Plassmann/Luby 变体用 `__brev` 位反转当哈希（`src/CudaKernels.cu:1468`），每轮同时定 min/max 两个颜色；GPU 与 CPU 用**同一手调颜色序** `{7,0,5,6,2,1,3,4}`（`src/CudaKernels.cu:1869-1877` = `src/CpuKernels.cpp:684-686` 展开）保证双路径置换一致。
- `A->totalColors` 直接硬编码 8，忽略着色函数输出的 `num_colors`（`src/OptimizeProblem.cpp:79-89`）——27 点模板至多 8 色的先验写死。
- **索引宽度运行时可换**（--mi）：`dispatchIndexMode` lambda 按 mode 读不同宽度的 slice offset（`src/OptimizeProblem.cpp:306-312`）；cuSPARSE 报 NOT_SUPPORTED 时自动回退旧模式（`src/IndexMode.hpp:171`）。
- **显存压缩**是 CUDA VMM 手工路径：`cudaMallocCompressible` 用 `cuMemCreate` 系（`src/CudaKernels.cu:84` 起，granularity 对齐），对应 `--l2cmp`（`src/main.cpp:158`，输出会提示成绩不可提交）。
- **sm_107 自适应向量化**：WAXPBY 线程宽 V=4（256-bit）仅 Rubin（cc 10.7）启用，其余 V=2（`src/CudaKernels.cu:2336-2345`）。

## 8. 新人上手指引

1. 先读 `README.md` → `bin/RUNNING-x86` → `src/main.cpp` 九阶段注释（每阶段有横幅注释）。
2. 想懂性能核心：`OptimizeProblem.cpp`（90 行内看懂 SELL 构造全流程）→ `ComputeSYMGS.cpp` → `CudaKernels.cu` 的 1446-2176 段（着色+SELL kernel 群）。
3. 改参数做实验：全部 CLI 语义在 `bin/hpcg.sh:41-57` 的 usage；异构模式的 g2c 比例语义见 `src/init.cpp:366-377` 四态注释。
4. 跑通验证：`run_sample.sh` 四例 + `--rt=0` quickPath（`src/main.cpp:154`，每段只跑一次）。

---
*字数 5798（非空白字符）/锚 64（唯一 file:line 锚）*
