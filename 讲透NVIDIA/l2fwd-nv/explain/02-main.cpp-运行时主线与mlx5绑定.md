# 精讲 02：main.cpp——运行时主线、mlx5 硬校验与 mempool 双形态

## 角色定位

`src/main.cpp`（931 行）是应用总指挥：EAL 初始化、参数解析、设备/GPU 枚举校验、mempool 与队列配置、逐流水线创建与线程分派、周期统计。l2fwd-nv 能不能在你的机器上跑起来，第一道门就在这个文件——它对硬件做了明确的白名单约束。

## 内部结构

按行号纵切：`print_stats`（`main.cpp:96`，每秒聚合各 pipeline 的 RX/TX 包数/字节数为 Mpps/Gbps，含 warmup 剔除与首包时延列）→ `print_opts`（`:179`，启动后回显全部生效配置）→ `parse_args`（`:232`，EAL 之后的长短选项 getopt 循环，全部委托 `utils.cpp:122` 起的 l2fwd_parse_* 家族：device_id/dataroom/burst/pipelines/warmup/performance…）→ `rx_core`（`:393`）→ `tx_core`（`:523`）→ `signal_handler`（`:614`）→ `main`（`:625`）。模块级 `conf_*` 配置群由 parse_args 填充、三个线程函数消费；注意 `:25` `static int conf_workload = CPU_WORKLOAD;`——默认 workload 是 CPU 而非 NO。

## 外部连接

向下：`Pipeline`（`pipeline.cpp:19` 构造）、`kernel.cu` 的三个 host 包装（`:499` 触发）、`utils.cpp` 的解析器与 CPU workload（`tx_core :570` 调 `workload_macswap_cpu`）。向上：DPDK EAL/ethdev/gpudev。**mlx5 硬校验**是本文件最出名的三行：`:687` 打印 `dev_info.driver_name`，`:689-690` `strcmp(...,"mlx5_pci")!=0 → rte_exit(EXIT_FAILURE,"Non-Mellanox NICs have not been validated in l2fwd-nv")`——非 Mellanox 网卡直接拒跑。这不是洁癖：收包路径依赖 mlx5 的 GPUDirect 特性与 gpudev 通信列表语义，其他 PMD 未验证。

## 数据流

`main` 六步：EAL+parse_args → 端口/GPU 枚举（`:695` `RTE_GPU_FOREACH`，`:727` 显存注册 gpudev）→ mempool 与 RX/TX 队列（`:744` payload 外部缓冲池 + `:752` header 池构成 buffer split 双段；`:66` RX offload 显式开 `RTE_ETH_RX_OFFLOAD_BUFFER_SPLIT`）→ 链路等待 → 逐 pipeline `new Pipeline`（构造期即分派 workload 形态：建流/启动持久 kernel/录 512 张 CUDA Graph，`pipeline.cpp:49-77`）→ launch rx/tx 线程。参数硬校验两条：`-m 1`（GPU 显存）+ CPU workload 必须开 buffer split（`:348`）；buffer split 下拒绝任何 GPU workload（`:353-354`）——GPU 直收场景与 buffer split 互斥。信号处理（`:614-618`）把 SIGINT/SIGTERM/SIGUSR1 统一为 `force_quit` 置位（SIGUSR1 当优雅退出用是本仓小特色）。

## 设计决策

- **单 mempool 全队列共享**（README 明示）：流水线间不隔离内存，测的是路径成本不是分配器。
- **mempool 双形态**：`MEM_DEVMEM`（GPU 显存，`common.h:60`）走 gpudev 注册+GDRCopy 子模块；`MEM_HOST_PINNED`（`:61`）走 CPU pinned——同一程序量"包在显存 vs 主存"对 GPU workload 的差。
- **统计线程内联**：没有独立 stats 线程，`print_stats` 由主循环按秒驱动，避免与 rx/tx 抢核。

## 新人提示

跑不起来先查三件事：网卡是不是 mlx5（`:690` 的报错文案很直白）；DPDK/gdrcopy 子模块是否 `git submodule update --init`（CMakeLists 会源内 meson 编 DPDK，首次很慢）；buffer split 与 workload 组合是否撞 `:348/:353` 两条校验。读代码建议主线三段式（main→rx_core→tx_core），把 `conf_*` 全局当作参数总线对照 `print_opts :179` 的输出理解。`headers.h:77` 与 `pipeline.h:20` 互相包含是刻意的 aggregator 模式，新增跨单元函数声明写在 headers.h 即可。
