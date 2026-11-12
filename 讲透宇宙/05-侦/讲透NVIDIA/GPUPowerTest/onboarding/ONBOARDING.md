# GPUPowerTest Onboarding（NVIDIA GPU 功率循环压测工具）

> 图谱基线 commit `a9534be48969025a0cfe64752bebe25156431b6c`，6 层/12 步 tour。所有行号锚经源码核实。

## 1. 项目定位一句话

GPUPowerTest（可执行名 `gpt`）是 NVIDIA 开源的 GPU 功率方波压测工具：用 OpenMPI 把多机多 GPU 组织成 rank-per-GPU 进程阵列，每个 GPU 在 up 相位跑 8000×8000 大矩阵 cublasLt GEMM 拉满功耗、dn 相位切换 1000×1000（或 -L 时 10×10）小矩阵降载，配合 CPU 自旋与随机功率跌落，测试供电系统对周期性负载骤变和随机掉载的响应。整机验收（RMA 复现、电源纹波）需要可控、可复现、跨节点相位对齐的功率激励，gpu-burn 类工具只能恒定负载。

## 2. 技术栈与依赖

- **CUDA Runtime + cublasLt**：负载主体 `cublasLtMatmul`（burn.cu:473 与 burn.cu:507），`CUBLAS_COMPUTE_32F_FAST_16F` 计算类型（burn.cu:97），workspace 256MB（burn.cu:138）。
- **curand**：MRG32K3A、固定 seed 777 灌六块矩阵（burn.cu:446-454）。
- **OpenMPI（>=4.1.3）**：`OMPI_COMM_WORLD_LOCAL_RANK`（gpt.c:104）做 GPU 映射、`MPI_Barrier`（gpt.c:207、burn.cu:532）做相位对齐；路径硬编码 /opt/openmpi-4.1.5（CMakeLists.txt:83-84）。
- **pthread**：gpt 侧一个压测线程，burn 侧 cores 个自旋线程，nvlbm 侧每 GPU 对两个拷贝线程。
- **DCGM（外部监测，非链接依赖）**：README:81 推荐 `dcgmi dmon -e 100,155,1002,1011,1012`。全仓零 `nvml.h`——功耗监测走 DCGM 而非 NVML；另需 CUDA>=11.0 与 fabricmanager（README:35-39）。

## 3. 目录与模块地图（按 6 层图谱）

| 层 | 内容 | 关键文件 |
|---|---|---|
| L01 许可与元数据 | CUDA samples 衍生声明（README:13-15）、MIT SPDX | License、OSS_License |
| L02 构建与运行脚本 | CMake 主构建 + nvlbm 独立编译 + MPI 包装 | CMakeLists.txt、bld_nvlbm.sh:34、gpt.sh:2 |
| L03 MPI 教学示例族 | Send/Recv 与 Barrier 最小例 + 草稿变体 + 2 份 ELF | mpi_sync_test.c:9-36、mpi_barrier.c:3-7 |
| L04 NVLink 负载生成器 | P2P D2D 无限对拷打满 NVLink | nvlbm.cu |
| L05 GPU 功耗方波核心 | BurnGPU 方波引擎 + Drop 掉载 + core_spin | burn.cu:82-626 |
| L06 gpt 主程序与文档 | 纯 C 启动器/CLI + SOP | gpt.c:73-222、README |

核心三件：`gpt.c`（谁跑跑多久）、`burn.cu`（怎么烧）、`nvlbm.cu`（额外 NVLink 流量）；examples/ 是 mpitutorial.com 演算稿，不参与构建。

## 4. 核心数据流/控制流

控制链：`mpirun` → `gpt.c:main`（gpt.c:73）→ `MPI_Init_thread`（gpt.c:78）→ 读 `OMPI_COMM_WORLD_LOCAL_RANK` 定 GPU 号（gpt.c:104-105）→ getopt 七参数（gpt.c:126）→ 注册 SIGUSR1（gpt.c:195）→ `pthread_create` 起 `launch_kernel`（gpt.c:199）→ 后者先 `MPI_Barrier` 对齐再调 `burn()`（gpt.c:64、70）→ `burn()` new BurnGPU 后立刻执行 functor（burn.cu:628-631）→ `operator()()` 无限方波循环（burn.cu:220）。

方波单周期（burn.cu:472-541）：
1. **up 相位**：循环 `cublasLtMatmul` 8000×8000（三块共 768MB 显存/卡），`cudaDeviceSynchronize` 后查墙钟（burn.cu:473-497）；
2. 到达 `target_up_ms` 后 join 掉 CPU 自旋线程（burn.cu:503-505）；
3. **dn 相位**：循环小矩阵 GEMM 至 `target_dn_ms`（burn.cu:506-531）；
4. `MPI_Barrier` 对齐相位边界（burn.cu:532），以出口时刻重设下周期 `target_up_ms`（burn.cu:535-536）并重拉 CORE_SPIN（burn.cu:539）。

退出协议：主线程 `sleep(load_time)` 到时后 `pthread_kill(tids[i], SIGUSR1)`（gpt.c:209-212），信号处理器 `sig_usr1` 直接 `pthread_exit`（gpt.c:51-55）——burn 无限循环的唯一优雅出口。CPU 侧功耗由 `core_spin` 忙等线程抬高（burn.cu:60-69），每周期经 `CORE_SPIN` 宏按 `-c` 核数重建（burn.cu:71-80）；随机掉载由内嵌类 `Drop` 注入（burn.cu:149-186）。

## 5. 构建与运行

**双轨构建**：CMake 主轨只编 gpt——`add_executable(gpt gpt.c burn.cu)` 链 `cublasLt mpi curand`（CMakeLists.txt:91-92），SM_LIST 默认 sm_90 即 Hopper（CMakeLists.txt:27）。nvlbm 绕过 CMake，由 `bld_nvlbm.sh` 的 `nvcc -o nvlbm nvlbm.cu -lpthread` 单文件编译（bld_nvlbm.sh:34）。

标准 SOP（README:28-51）：先验 MPI 与 `ldd ./gpt`（libmpi.so.40/libcublasLt.so.11 可达），再 `mpirun -np 8 -H localhost:8 ./gpt -t 14400 -d 0.1 -u 35 -D`（README:51）。多机时 `-H` 列多主机、总数对齐 `-np`（README:48-50）；CMT 禁用机用 `--map-by ppr:2:numa:pe=11:overload-allowed`（README:64）。旁路 `dcgmi dmon -e 100,155,1002,1011,1012`（README:81）；NVLink 加压 `./nvlbm -d 300`（README:75 写 `-t` 有误，见勘误 10），可与 gpt 同跑（README:70-71）。快捷脚本 gpt.sh：`./gpt -t ${1:-10} -i $OMPI_COMM_WORLD_LOCAL_RANK`（gpt.sh:2）。

## 6. 关键设计决策

- **三档矩阵 8000/1000/10**（burn.cu:109-111）：up 档 8000³ GEMM 让张量核与 HBM 同时饱和，测供电峰值；dn 档默认 1000³ 中档保留 GEMM 流、只降功耗台阶（模拟降频不停止）；`-L` 档 10×10 逼近空闲测瞬态。对应满载/中载/近空三态。
- **SIGUSR1 退出而非标志位**：burn 主循环深嵌 cublasLt/同步调用，查标志时机不可控；信号驱动 `pthread_exit` 可从任意深度打断（gpt.c:212→gpt.c:54），代价是析构（burn.cu:556-624）不执行。
- **MPI_Barrier 相位同步**：方波边沿跨节点对齐才有整机功率台阶意义。dn 结束处 barrier（burn.cu:532）保证最慢 rank 不拖累相位起点，以出口时刻重算毫秒戳消解 barrier 抖动（burn.cu:459-461 注释明言此意图；burn.cu:466 usleep 对齐整秒）。
- **rank-per-GPU 映射**：`OMPI_COMM_WORLD_LOCAL_RANK` 直接当 GPU 号（gpt.c:105），天然一进程一卡；单进程才用 -i。
- **固定 seed 777**（burn.cu:448）：负载可复现；**毫秒整数时间运算**（`K=1000`，burn.cu:38）避免浮点误差累积。

## 7. 已知坑与勘误

| # | 坑/勘误 | 实证 |
|---|---|---|
| 1 | 功耗监测走 DCGM 而非 NVML，全仓无 `nvml.h`，程序自身不回读功耗 | README:81 |
| 2 | -L 低档越界读隐患：三元式 `SEED_DN_LOW : SEED_DN_HOT*(...)` 使 low 模式 `As_dn` 只分配 10 元素（40 字节），layout 却按 10×10=100 元素建，curand 灌充与 GEMM 读均越界（应为 `SEED_DN_LOW*SEED_DN_LOW`），静默 UB | burn.cu:120-125 |
| 3 | `Adesc_dn` 创建两次（复制粘贴），第一份句柄被覆盖泄漏，析构只销毁后者 | burn.cu:314-334 |
| 4 | 悬空 else：`up+down>load_time` 校验只在无参数时执行，带参数即跳过 | gpt.c:175-180 |
| 5 | `burn()` 泄漏与吞异常：new 无 delete；catch 打印不重抛；SIGUSR1 退出连 operator() 尾部清理也跳过 | burn.cu:629、551-553、544-549 |
| 6 | 双轨构建：CMake 只产 gpt，nvlbm 必须另跑 bld_nvlbm.sh | CMakeLists.txt:91、bld_nvlbm.sh:34 |
| 7 | examples/ 是草稿场：c_0..c_4 为教程演算变体（c_1≈定稿），两份 not-stripped ELF 入库 | mpi_sync_test.c_1 |
| 8 | MPI 模式 -i 被忽略，GPU 号由 local rank 决定 | gpt.c:146-148 |
| 9 | README 无扩展名纯文本；CMakeLists.txt 曾被 scanner 误判为 docs（实为 config） | CMakeLists.txt |
| 10 | README 的 nvlbm 选项写 `-t`，代码实际解析 `-d`——按 README 跑会走 Usage 退出 | README:73/75、nvlbm.cu:142-148 |
| 11 | nvlbm pthread_join 缩进陷阱：for 体只有一条语句，错误检查在循环外 | nvlbm.cu:188-192 || 12 | nvlbm MAX_GPUS=8 溢出边界：每对 GPU 2 线程，8 卡恰好满格，10+ 卡写越界 tids | nvlbm.cu:43、116、166-183 |

## 8. 新人上手路径

1. **先读 README**：SOP 前置清单（MPI 验证、libcublasLt.so.11、fabricmanager）是排障第一站。
2. **跑 examples 冒烟**：`cd examples && ./mpi_build.sh && ./run.sh`（run.sh:1 本机 4 进程）——gpt 多卡的前置。
3. **单卡短跑**：`./gpt -t 30 -u 5 -d 2`，旁开 `dcgmi dmon` 看方波，观察 `up/dn phase begin at ms.` 相位日志（burn.cu:500、537）。
4. **按控制流读码**：gpt.c:73-222 → gpt.c:57-71 → burn.cu:628-631 → burn.cu:220-554，这条线读懂全仓 80% 就通。
5. **再读三个特种件**：Drop（burn.cu:149-186）、core_spin（burn.cu:60-69）、nvlbm.cu:57-106；多卡长跑按 README:51 加 -D/-L，10+ 卡机型先修坑 12。
