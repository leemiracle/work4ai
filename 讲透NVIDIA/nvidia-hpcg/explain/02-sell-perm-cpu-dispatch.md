# 02 · SELL-P 重排管线与架构自适应——着色置换、MIDR 派发、hpcg.sh 亲和

## 一、角色定位

HPCG 的性能分几乎全部来自一个决定：**把自然序 CSR 矩阵重排成"颜色连续、切片对齐"的 sliced-ELLPACK（SELL-P）**，让 cuSPARSE/NVPL Sparse 的 SpMV/SpSV 在规整布局上跑满带宽。本文串起三件事：①`OptimizeProblem` 的重排管线；②Grace CPU 侧按 MIDR_EL1 派发调优库的 `nvidia-cpu/` 子系统；③`bin/hpcg.sh` 的进程亲和启动层——三者合起来是"数据布局→库选择→进程放置"的完整自适应栈。

## 二、内部结构

**重排管线（每 MG 层各跑一遍，共 4 层）**：

1. 着色：GPU `ColorMatrixCuda`（`src/OptimizeProblem.cpp:87`）/CPU `ColorMatrixCpu`（`src/OptimizeProblem.cpp:271`）产出 `color[]` 与按颜色排序的置换。CPU 侧先把位反转哈希整表预计算（`src/CpuKernels.cpp:676-682`，注释明言省掉 O(nrow·degree·steps) 重算），颜色计数用 per-thread 计数器归并（`src/CpuKernels.cpp:769-790`），注释点明"用顺序归并而非原子操作"（`src/CpuKernels.cpp:792`）。
2. 置换表：`ref2opt/opt2ref` 双表互逆；发送行号同步置换（`src/OptimizeProblem.cpp:287-291`，OpenMP 并行）。
3. SELL 直构：`EllPermColumnsValuesCuda` 一步产出**列主序** SELL（`src/OptimizeProblem.cpp:99-101`，kernel `src/CudaKernels.cu:1580`）；L/U 每片最大行长经 prefix-sum×slice_size 换算成字节偏移（`src/OptimizeProblem.cpp:109-113`）；CPU 侧等价物是 `CreateSellPermCpu`（`src/OptimizeProblem.cpp:282`，定义 `src/CpuKernels.cpp:811`）。
4. 描述符：三个 `cusparseCreateSlicedEll`（L/U/A，`src/OptimizeProblem.cpp:138-153`）或 NVPL 等价 `nvpl_sparse_create_sliced_ell` 三连（`src/OptimizeProblem.cpp:315-325`）。

**两个关键参数**：切片宽度 `--gss`（GPU 默认 4096）/`--css`（CPU 默认 8），`src/init.cpp:426`/`src/init.cpp:429`；索引宽度 `--mi` 三态（`src/IndexMode.hpp:67-71`：I32_I32/I64_I32/I64_I64），运行时由 `dispatchIndexMode` 泛型 lambda 决定按 4 还是 8 字节读 slice offset（`src/OptimizeProblem.cpp:306-312`），并统一映射到 cuSPARSE/NVPL 索引枚举（`src/IndexMode.hpp:139-145`）。

**MIDR 派发（`nvidia-cpu/`）**：每 CPU 型号编译一份调优 .so（Grace=Neoverse-V2、Vera=Olympus，枚举在 `nvidia-cpu/dispatch/hpcg_cpu_detect.h:24-29`），再加一个**刻意只编 armv8-a 基线的通用 dispatcher**（`nvidia-cpu/Makefile:31`），运行时读 cpu0 的 MIDR_EL1 选库 dlopen（`nvidia-cpu/Makefile:18-19`；探测入口 `hpcg_cpu_variant_from_midr`，`nvidia-cpu/dispatch/hpcg_cpu_detect.h:31`）。NVPL 本体也会自行在 Grace/Vera 间分派（`nvidia-cpu/Makefile:48` 注释）。

## 三、外部连接

- 重排管线的消费端：`main.cpp` 在进/出优化路径时用 `PermVectorCuda(opt2ref/ref2opt)` 置换 b/x（`src/main.cpp:741`/`src/main.cpp:937`）；层间注入算子也要置换（`F2cPermCpu`，`src/OptimizeProblem.cpp:444`）。
- `nvidia-cpu/` 与主构建解耦：`setup/Make.CUDA_AARCH64` 产主二进制，派发库是旁路（`nvidia-cpu/Makefile:57` 注释）。
- 异构 GPU+CPU 的形状语义：`--g2c` + `--lpm` 四态（GPU_RATIO/GPU_ABS/GPU_CPU_RATIO/GPU_CPU_ABS，`src/init.cpp:366-377`），GPU/CPU 本地问题只允许一个维度不同以便 halo 对齐。

## 四、数据流

CPU rank 的一次优化期：`AllocateMemCpu` 先按启发式预留 → `ColorMatrixCpu` 染色+计数 → `firstRowOfColor` 前缀（`src/OptimizeProblem.cpp:275-279`）→ `CreateSellPermCpu` 重排 → NVPL 描述符+SpMV/SpSV analysis；其中 int32 时代的 SpSV 工作区启发式在 64 位偏移模式下会被**丢弃重查**以防堆损坏（`use_prealloc_spsv_workspace` 判定 `src/OptimizeProblem.cpp:370-371`，弃用补偿 `src/OptimizeProblem.cpp:382`）。

## 五、设计决策

- **切片宽度双默认值差 512 倍**（GPU 4096 vs CPU 8）：GPU 靠宽切片喂 SM，Grace 靠窄切片贴合 NUMA/向量寄存器——同一格式两种机器观。
- **确定性重排跨实现成立**：GPU/CPU 用同一手调颜色序（`src/CudaKernels.cu:1869-1877` vs `src/CpuKernels.cpp:684-686`），保证同矩阵同置换。
- **A 矩阵按最坏情况 padded**：`sell_nnz = slices × slice_size × HPCG_MAX_ROW_LEN` 64 位计算防溢出（`src/OptimizeProblem.cpp:149`）。
- hpcg.sh 的亲和是**表驱动按 local rank 查表**而非自动发现：GPU/CPU/MEM/NET 四张冒号分隔表（`bin/hpcg.sh:383-402`），NET 表落到 `UCX_NET_DEVICES`（`bin/hpcg.sh:374-381`），CPU/MEM 表拼成 `numactl --physcpubind/--membind`（`bin/hpcg.sh:404-406`）；rank 身份从 OMPI/PMIX/PMI/SLURM 四种环境依次探测（`bin/hpcg.sh:350-372`）。OMP 绑定固定 `OMP_PROC_BIND=TRUE`+`OMP_PLACES=sockets`（`bin/hpcg.sh:30-31`）。

## 六、新人提示

调异构负载先读 `bin/RUNNING-aarch64` 的形状设计，再对着 `--g2c/--lpm/--ddm` 四态语义（`src/init.cpp:366-377`）算 GPU/CPU 各自 nx×ny×nz；性能对切片宽度敏感，GPU 侧用 `--gss` 扫 2048/4096/8192，注意粗层行数小于 slice 时有 cuSPARSE≥12.5 闸（`src/main.cpp:631`）；`nvidia-cpu` 单独 `make grace-only` 可只出 Grace 库（`nvidia-cpu/Makefile:25`）。

---
*字数 3411（非空白字符）/锚 36（唯一 file:line 锚）*
