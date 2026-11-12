# 03 · 测试族：宏注册测试框架、三基准与 pplat.cu 手扫域

> 对象：`tests/sanity.cpp`（2537 行）+ `tests/testsuites/` + `tests/copybw.cpp`/`copylat.cpp`/`apiperf.cpp`/`pplat.cu` + `tests/common.cpp|hpp`。行号锚 @fcec3ce0 源码核实。

## 一、角色定位

tests/ 是"一功能三基准一延迟"的完整验证矩阵：`sanity` 做功能回归（37 用例，覆盖 pin/map/copy、fd 跨进程传递、多线程、bar 模式、异常信号），`copybw`/`copylat` 刻画带宽与时延曲线，`apiperf` 单测 API 自身开销，`pplat`（ping-pong latency）测 GPU↔CPU 往返延迟。它自带一套极简 C++ 测试框架（`testsuites/`），不依赖 gtest——这是嵌入式内核周边项目的常见选择。

## 二、内部结构

**框架本体**：`testsuites/testsuite.hpp:26` 的 `GDRCOPY_TEST(name)` 宏把每个用例展开为"类 `GDRCopy_Test_##name`（继承 `Test` 基类，`testsuite.hpp:56`）+ 静态自注册对象 + `test()` 成员定义"三件套；`GDRCOPY_EXTENDED_TEST`（`testsuite.hpp:37`）多传 `true` 标记扩展用例（默认不跑）。sanity.cpp 有 36 处 `GDRCOPY_TEST(` + 1 处 `GDRCOPY_EXTENDED_TEST(` 调用点。运行器 `run_tests`（`testsuite.cpp:63`）按名单调度，`Test::run`（`testsuite.cpp:143`）fork 子进程隔离执行（崩溃不拖垮整套），`Test::run_executor`（`testsuite.cpp:228`）是子进程侧执行体。入口 `main`（`sanity.cpp:2480`）支持 `-l` 列用例（`print_all_tests`，`sanity.cpp:2463`）。

**sanity 基建**：CUDA 初始化 `init_cuda`（`sanity.cpp:64`）；平台过滤 `coherent_platform_filter`（`sanity.cpp:124`，一致性/非一致性平台筛用例）与 `waive_if_dma_buf_mmap_backend`（`sanity.cpp:138`）；信号崩溃捕获 `exception_signal_handle`（`sanity.cpp:55`）；跨进程 fd 传递 `sendfd`/`recvfd`（`sanity.cpp:160`/`sanity.cpp:203`，Unix 域套接字 SCM_RIGHTS）；多线程用例共享结构 `mt_test_info`（`sanity.cpp:2151`）；v2 pin 封装 `pin_buffer_v2_helper`（`sanity.cpp:241`）。

## 三、外部连接

全部测试链接 libgdrapi 与 CUDA Driver API（构建规则 `tests/Makefile` 按 CUDA gencode 编译）；显存获取统一走 `gpu_mem_alloc`（`common.cpp:45`，cuMemAlloc 与 dma-buf 双路径）/`gpu_mem_free`（`common.cpp:82`）；平台可用性探测 `check_gdr_support`（`common.cpp:301`，决定测试提前跳过）；正确性断言 `compare_buf`（`common.cpp:254`，逐字节比对并报告首个不一致）；会话获取 `gdr_open_safe`（`common.hpp:148`）。`common.hpp` 用尖括号 `<gdrapi.h>` 引库头（依赖 `-Iinclude` 解析），与引号风格混用是本仓 include 特点。

## 四、数据流（以 copybw 为例）

`main`（`copybw.cpp:154`）解析设备号/块大小列表/方向/上报间隔 → 分配显存与 host 缓冲 → `run_test`（`copybw.cpp:68`）按块大小循环调 `gdr_copy_to/from_mapping` 累计字节计时 → 输出各块大小 GB/s 表。`copylat`（`copylat.cpp:70`）同构但固定小尺寸测时延，并与普通可缓存内存做基线对照；`apiperf`（`apiperf.cpp:62`/`apiperf.cpp:178`）对单条 API 循环计时出直方图（`print_histogram`，`common.cpp:344`）。pplat 的数据流独立成环：CPU 与 GPU 各持线程，以原子标志交替生产/消费（4 个 `__global__` kernel：`pplat.cu:50`/`pplat.cu:70`/`pplat.cu:107`/`pplat.cu:142`），数据版 kernel 在标志同步外搬运载荷。

## 五、设计决策

- **子进程隔离**：用例可能触发 SIGBUS/SIGSEGV（映射失效场景正是测试目标），fork 隔离让信号死亡只记一个 FAIL（`testsuite.cpp:143`）。
- **pplat 的多内存位置矩阵**：`gh_mem_alloc`（`pplat.cu:261`）把 host/device/gdr mapping/零拷贝四类位置统一成一种句柄，主循环 `main`（`pplat.cu:378`）按参数切换，直接对比 GDRCopy 与 cudaHostRegister 路径的往返延迟；`check_timeout`（`pplat.cu:355`）自旋看门狗防挂死。
- **.cu 单独存在的原因**：ping-pong 必须 GPU kernel 与 CPU 代码同文件共享标志语义，nvcc 编译（`tests/Makefile` 单列 gencode）。这也是 tree-sitter 盲区：.cu 零提取，图谱 9 个函数（4 kernel + `gh_mem_alloc`/`gh_mem_free`/`print_usage`/`check_timeout`/`main`）全部人工手扫补充——手扫域锚勿信 scanner 复跑。

## 六、新人提示

跑回归：`insanity`（若有）/`sanity -l` 先看用例清单，`sanity -t <name>` 单跑；CI 视角记住 37 用例中 1 个是 EXTENDED（默认跳过）。读宏机制从 `testsuite.hpp:26` 展开式入手，一分钟后 `sanity.cpp` 里所有 `GDRCOPY_TEST(...){...}` 都不再神秘——那不是函数调用，是类定义+静态对象。改动拷贝路径后优先跑 copybw 扫块大小矩阵 + copylat 小尺寸段，再用 pplat 验证映射本身没退化。跨进程用例（sendfd/recvfd）是 gdrdrv `gdrdrv_check_same_process`（`gdrdrv.c:468`）语义的活文档：fd 可以传，句柄不能跨进程裸用。
