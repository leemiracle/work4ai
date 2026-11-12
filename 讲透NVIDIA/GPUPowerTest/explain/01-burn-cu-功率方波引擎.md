# burn.cu：GPU 功率方波引擎

## 角色定位

burn.cu 是 GPUPowerTest 的负载心脏：633 行单文件实现 `BurnGPU` 类（burn.cu:82-626），把「功率方波」概念翻译成 GPU 循环 GEMM——up 相位用 8000×8000 大矩阵 `cublasLtMatmul` 推满功耗，dn 相位换小矩阵下台阶。它不做数值验证，唯一产出是功率与热。对外只暴露 `extern "C"` 的 `burn()`（burn.cu:628-631）。

## 内部结构

- **core_spin**（burn.cu:60-69）：CPU 自旋线程体，`gettimeofday` 忙等到目标毫秒戳；`CORE_SPIN` 宏（burn.cu:71-80）按 `-c` 核数起一批线程，让 CPU 与 GPU 功耗同步抬升。
- **构造函数**（burn.cu:189-218）：`cudaMalloc` 七块显存（burn.cu:211-217）——up 相位 A/B/C 各 256MB、dn 三块、外加 256MB workspace（burn.cu:138）。
- **矩阵三档**：`SEED_UP 8000 / SEED_DN_LOW 10 / SEED_DN_HOT 1000`（burn.cu:109-111），dn 维度由 low 开关三元选择（burn.cu:120-122）。size 三行（burn.cu:123-125）的 `SEED_DN_LOW : SEED_DN_HOT * (...)` 是真 bug：low 模式只分配 10 元素（40 字节），layout 却按 100 元素描述，curand 灌充与 GEMM 读均越界，静默 UB。
- **Drop 内嵌类**（burn.cu:149-186）：随机掉载模拟器，见数据流节。

## 外部连接

向上，`burn()` 是 gpt.c 的 `launch_kernel` 线程（gpt.c:57-71）的直接调用目标，六参数对应 CLI 七选项；向下依赖 cublasLt 双 handle（burn.cu:223、230）、curand（burn.cu:446-454）、pthread 与 MPI。主循环的 `MPI_Barrier(MPI_COMM_WORLD)`（burn.cu:532）对齐全 rank 相位。退出依赖外部信号——主循环无自然出口，gpt.c 主线程 `pthread_kill(SIGUSR1)` 后信号处理器 `pthread_exit`（gpt.c:51-55）终止本线程。

## 数据流

`operator()()`（burn.cu:220-554）前半初始化：双套 matmulDesc、TRANSA/B/C 全 `CUBLAS_OP_N`（burn.cu:255-301），六份 MatrixLayout 全 `CUBLASLT_ORDER_COL`（burn.cu:336-444，其中 `Adesc_dn` 在 burn.cu:314 与 325 重复创建、第一份句柄泄漏）；curand 用 seed 777 灌满六块（burn.cu:447-448）。

无限方波循环（burn.cu:472-541）：
1. **up 相位**：反复 `cublasLtMatmul`，C 原地累加（burn.cu:481-484），`cudaDeviceSynchronize` 后读墙钟至 `target_up_ms`（burn.cu:494-497）；
2. join CPU 自旋线程（burn.cu:503-505），**dn 相位**小 GEMM 至 `target_dn_ms`（burn.cu:506-531）；
3. `MPI_Barrier` 等齐（burn.cu:532），重设下周期 `target_up_ms` 并重拉 CORE_SPIN（burn.cu:535-539）。

时间体系是整数毫秒（`K=1000`，burn.cu:38）避免浮点漂移；入口 usleep 对齐整秒（burn.cu:466）。

**Drop 随机模型**（burn.cu:161-185）：6 秒窗口掷一次硬币——`rand()%2` 决定是否掉载（burn.cu:183），时刻取窗口内随机偏移（burn.cu:184），到点 `sleep`（burn.cu:168）。细看时长：`drop_delay_sec=(ms/1000)%4`、0 提升为 1（burn.cu:181-182），实际取值 1-3 秒且由窗口起始秒数决定——与 README 的 "1 - 4 sec" 有出入。

## 设计决策

- **三档矩阵**：8000³ 同时压满张量核与 HBM；1000³ 中档保留 GEMM 流、功率台阶不满载（模拟降频不停机）；10×10 近乎空闲测供电瞬态。覆盖满/中/空三态。
- **in-place GEMM**（C→C，burn.cu:481-484）：省显存且制造读写依赖，堵住 cublasLt 更省电的拆分路径。
- **固定 seed 777**（burn.cu:448）：矩阵内容一致，功耗曲线可横向比对，回归测试的前提。
- **barrier 后重算时间戳**（burn.cu:535-539）：barrier 耗时不定，以出口时刻为锚使相位误差不逐周期累积。
- **生命周期从简**：catch 不重抛（burn.cu:551-553）、new 无 delete（burn.cu:629）——进程注定被信号击杀，析构几乎不执行。

## 新人提示

1. 从 `burn()`（burn.cu:628-631）跳进 `operator()()`，跳过 burn.cu:220-470 的描述符样板，主循环只在 burn.cu:472-541。
2. 改档位只需动三个 `SEED_*` 宏（burn.cu:109-111），注意 ld 与 dims 联动（burn.cu:107-108 注释）与 low 档 size bug。
3. 验证方波直接 `dcgmi dmon` 采样画图；Iterations 计数（burn.cu:500）是 up 相位 GEMM 次数旁证。
4. SIGUSR1 击杀后残留上下文靠下次运行构造函数的 `cudaDeviceReset`（burn.cu:193）兜底；Drop 只在 -D 时调用（burn.cu:462）。