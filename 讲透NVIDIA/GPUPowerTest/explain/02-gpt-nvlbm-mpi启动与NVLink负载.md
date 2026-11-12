# gpt.c 与 nvlbm.cu：MPI 启动器与 NVLink 负载生成器

## 角色定位

gpt.c 是全仓唯一的纯 C 主程序（225 行），扮演「MPI 启动器 + CLI + 线程调度器」：解析七个选项、把 MPI local rank 映射为 GPU 号、起压测线程、到时以 SIGUSR1 收割。nvlbm.cu（196 行）是独立的 NVLink 负载生成器，不依赖 MPI，用 P2P cudaMemcpy 对拷打满 GPU 间互连。两者一纵一横：gpt「单卡深烧」（每 rank 一卡），nvlbm「跨卡流量」，可同时运行（README:70-71）。

## 内部结构

gpt.c 三个顶层构件：`gpt_args`（gpt.c:40-47，四 int + 两 double）是 CLI 到 burn 的参数载体；`sig_usr1`（gpt.c:51-55）五行信号处理器直接 `pthread_exit`；`launch_kernel`（gpt.c:57-71）压测线程体，先 `MPI_Barrier` 对齐再调 burn。main（gpt.c:73-222）串联全程。

nvlbm.cu 两个构件：`gpu_args`（nvlbm.cu:45-51）与 `nvl_load` 线程体（nvlbm.cu:57-106）——查 P2P 可达（nvlbm.cu:69）、双端各 100MB（nvlbm.cu:42、75-78）、双向 peer access（nvlbm.cu:80-83）、非阻塞流无限 D2D 拷贝（nvlbm.cu:90-94）。main（nvlbm.cu:108-195）清点设备、奇数卡弃尾（nvlbm.cu:131-138）、首尾配对每对两反向线程（nvlbm.cu:156-185）。

## 外部连接

gpt.c 与 burn.cu 的桥是前向声明 `void burn(...)`（gpt.c:49）对接 burn.cu 的 `extern "C"` 定义——纯 C 侧不 include 任何 C++ 头即可链接。向上依赖 OpenMPI（`MPI_Init_thread` 用 `MPI_THREAD_SINGLE`，gpt.c:78）、pthread、getopt。nvlbm.cu 只依赖 CUDA Runtime 与 pthread，由 `bld_nvlbm.sh:34` 的 nvcc 单文件编译，不进 CMake 主构建（CMakeLists.txt:91）。

## 数据流

gpt 启动序：`MPI_Init_thread`（gpt.c:78）→ 读 `OMPI_COMM_WORLD_LOCAL_RANK` 定 GPU（gpt.c:104-105）→ getopt 七选项（gpt.c:126，-h 见 gpt.c:114-123）→ 填 gpt_args（gpt.c:181-186）→ `sigaction` 注册 SIGUSR1（gpt.c:192-195）→ `pthread_create` 起 launch_kernel（gpt.c:199）→ 主线程 `MPI_Barrier`（gpt.c:207）+ `sleep(load_time)`（gpt.c:209）→ `pthread_kill(tids[i], SIGUSR1)`（gpt.c:212）→ join（gpt.c:217）→ `MPI_Finalize`（gpt.c:221）。

退出协议是本文件最精妙的设计：burn 方波主循环无自然出口，唯一优雅终止路径是外部信号触发 `sig_usr1` 里的 `pthread_exit`（gpt.c:54）。注意 `act.sa_sigaction = sig_usr1` 但 `sa_flags=0` 未设 `SA_SIGINFO`（gpt.c:193-194），内核实际按单参 handler 语义调用——能工作靠 sigaction union 的布局巧合。

nvlbm 数据流全在 `nvl_load`：`cudaMemcpyAsync` D2D + `cudaStreamSynchronize` 循环到超时（nvlbm.cu:91-94）。

## 设计决策

- **local rank 即 GPU 号**（gpt.c:105）：OpenMPI 本地编号天然与 GPU 序号对齐；代价是 MPI 模式下 `-i` 失效（gpt.c:146-148），单进程裸跑才生效。
- **SIGUSR1 而非超时标志**：压测线程可能阻塞在 `cudaDeviceSynchronize` 任意深处，标志位检查时机不可控；信号中断 + `pthread_exit` 是唯一保证「到时即停」的手段；主线程用 `sleep` 计时（gpt.c:209）求简。
- **main 线程不烧 GPU**：压测放子线程，主线程专职 MPI 同步与计时，`MPI_Barrier` 不会被长 GEMM 卡住。
- **nvlbm 首尾配对+方向翻转**（nvlbm.cu:156-185）：GPU i 对 last_gpu，每对两线程反向制造双向流量；sleep 1 错峰（nvlbm.cu:172、184）避免竞态。
- **gpt.c:175-180 悬空 else**：`} else` 后紧跟独立 if，`up+down>load_time` 校验只在无参数时执行——笔误但默认值合法。

## 新人提示

1. 多卡前先用 examples 冒烟：mpi_build.sh（mpicc）+ run.sh（mpirun 本机 4 进程，run.sh:1）；mpi_sync_test.c:9-36 是 rank 0 三路 `MPI_Send` 最小演示，c_0..c_4 是演算草稿（c_1≈定稿）。
2. gpt 时间线以 stdout 相位日志为准，配 `dcgmi dmon` 采样；`-t` 与方波相位无对齐，SIGUSR1 可落在任意相位中段。
3. nvlbm 三坑：README:73/75 说选项 `-t`、代码实际解析 `-d`（nvlbm.cu:141-149）；join 缩进陷阱（nvlbm.cu:188-192）使错误检查只覆盖最后一个线程；`MAX_GPUS=8`（nvlbm.cu:43、116）在 10+ 卡机型写越界 tids。
4. 默认值在 gpt.c:91-96；`MAX_GPU_INDEX 15`（gpt.c:36）硬限 GPU 号 0-15。
