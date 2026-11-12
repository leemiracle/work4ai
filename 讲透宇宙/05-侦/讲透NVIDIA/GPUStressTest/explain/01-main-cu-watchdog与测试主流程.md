# 01 · main.cu：watchdog 与测试主流程

## 角色定位

main.cu（1374 行）是 gst 唯一的程序主体，源自 NVIDIA 内部 cublasMatmulBench、为微软 GPU 验收改造（main.cu:43-46）。它身兼四职：进程编排（起 watchdog 线程、枚举挑选 GPU）、套件调度（逐卡逐测试喂参数）、GEMM 执行引擎（test_cublasLt→test_engine→lt_gemm 三层模板）与计时报告（calc_matmul_perf_time + cublasPrintPerf）。理解了它就理解了 gst 的全部运行时行为。

## 内部结构

自上而下六个函数：

- **watchdog**（main.cu:119-165）：读 `GST_WATCHDOG_TIMEOUT_SEC` 覆盖默认 600s（:123-125），先 `sem_post(&go)` 放行 main，循环 `sem_wait(&wd)` 等测试开始 → `sem_timedwait(&done, now+600s)`（:143）限时等完成；超时且 `tstate[i].test_state==1` 判 hung（:144-149），其他错误则置 watchdog_bailed 自杀。
- **calc_matmul_perf_time**（:195-359）：内嵌三结构——DurationEvent 宿主钟、CudaDurationEvent cudaEvent 对、SemaphoreControls pinned 映射计数器（:204-268）；1 轮 warmup 后每轮 `cublasLtMatmul`（:295），统计 min/max/p20/p50/去极值均值。
- **auto_tuning**（:361-453）：`cublasLtMatmulAlgoGetHeuristic` 要 8 个候选（:372），每算法跑 5 次取 median（:403/:425），最优 memcpy 出（:432）。
- **lt_gemm**（:455-669）：配 matmulDesc 转置/epilogue/bias、四个 Layout；workspace 按 `device_version<900` 选 4MB/32MB（:476-477）；三路 catch 转返回码（:657-666）。
- **test_engine**（:671-883）：校验 ld 与维度、`device_memory::allocate` 分配 A/B/C(/D)（:763-768）、fillMatrixDevice 填充或 cudaMemset 清零、cublasLtCreate 后调 lt_gemm，失败 `exit(-1)`（:865）。
- **test_cublasLt**（:899-984）：按 math_type 六分支分发；FP8 需 SM90（:906-909）、IMMA 需 SM75 且强制 NT/TN 与 COL32/COL32_2R_4R4 排布（:948-963）。

## 外部连接

main.cu 是全仓依赖汇聚点：include 十个 util 头（main.cu:53-61）；消费 GST 套件（util/GST.h）、BlasOpts（util/common_header.h:84-125）、fillMatrixDevice 与 wait_kernel（util/fill_matrix.h:108-120 / util/test_util.cu:57）；输出格式被 util/parse_memory_targets.bash 消费（但该脚本期望的 FINAL 标记已不存在，见 03 篇）；Docker/software/run.sh:8 以 `-T=$loop` 调用它。

## 数据流

argv → CommandLine → main 的 P_arg if-chain（main.cu:1206-1302，与 test_args.cu:132-175 宏表重复维护）写七元组类型到 blas_opts → m/n/k/ta/tb 来自 gst.stress_tests（:1304-1309）→ `sem_post(&wd)`（:1325）通知 watchdog → test_cublasLt 按运行时枚举经 TEST_ENGINE_MAPPING（:885-896）选编译期特化 → test_engine 分配/填充 → lt_gemm → cublasLtMatmul → "^^^^ CUDA : elapsed/Gflops" 行（util/measure.cc:101-104）→ PASS/FAIL 判定（:1335-1342）。注意 PASS 路径 `continue`（:1344）跳过 done/go 握手与 test_state 复位（:1346-1359）——这是当前代码最大的隐患（下节）。

## 设计决策

1. **三信号量而非条件变量**：wd/go/done 三个 sem_t（main.cu:114）把"开始/放行/完成"拆成单向信道，注释钉版语义（:108-113）；跨平台只要 POSIX 兼容层（Windows 用 vcpkg pthread）。
2. **显存一致性前置检查**（:1057-1062）：异构显存机器直接退出，保证 12 套件尺寸假设成立。
3. **warmup+握手计时**：wait_kernel 自旋把每轮迭代隔离开，避免上一轮尾流污染下一轮 cudaEvent。
4. **debug 留门**：DEBUG_MATRIX_SIZES（:1071-1089）用 13 项名字列表替换真实 GPU 名走全部分支——但分配照旧，不是真正 mock。

## 新人提示

读代码先看 main.cu:108-165 的 watchdog 与 main.cu:988-1368 的 main，两处注释就是设计文档。要改超时别动 TEST_WAIT_TIME，用环境变量。改 PASS/FAIL 逻辑时务必注意 :1344 的 continue 跳过了 :1356-1359 的握手——若你看到长跑被误判 hung，先查这里而不是 GPU。类型组合新增要同步 main.cu if-chain 与 test_args.cu 宏表两处。
