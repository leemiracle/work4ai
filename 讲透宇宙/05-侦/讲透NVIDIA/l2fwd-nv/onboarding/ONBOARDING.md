# l2fwd-nv 讲透导航（Onboarding）

> 基于图谱 44 节点/68 边/4 层/6 步 tour @ commit 3ef308b7，行号锚经源码核实（2026-11）。配套：`../deepwiki/`、`../explain/` 2 篇、`../README.md`（勘误 6 条）。

## 1. 这个仓库是什么

NVIDIA 的 **DPDK×GPU 二层转发基准程序**：在标准 l2fwd（DPDK 经典示例，收包→改 MAC→发包）的 RX/TX core 之间插入一个**可切换的 workload 实体**，用同一套数据面精确度量"GPU 参与网络转发路径"的三种姿态各付多少代价。README:10-14 定义每条流水线：RX core 从专属 DPDK 队列收包聚成 burst → 异步触发 workload（MAC 交换）→ TX core 等完成、把改好的 burst 发回。全部代码只有 4 个实现文件（`main.cpp` 931 行 / `utils.cpp` 356 行 / `kernel.cu` 301 行 / `pipeline.cpp` 109 行）+ 4 个头文件，却拖着两个源码子模块（`.gitmodules`：`external/dpdk` 官方 DPDK + `external/gdrcopy`），构建时 DPDK 以 meson/ninja 源内拉起（`CMakeLists.txt:101-118`）并禁用大量无关驱动（`:62-75` 起 `DPDK_DISABLED_DRIVERS` 串：baseband/*、crypto/nitrox、net/ark 等长清单）省编译时间。

## 2. 五种 workload 模式：全局形

`include/common.h:74-80` 的 `enum workload_flags` 是命令行 `-w` 的落点（README:179 给出口径）：`NO_WORKLOAD=0`（纯 I/O 转发不换 MAC）、`CPU_WORKLOAD=1`（CPU 换 MAC）、`GPU_WORKLOAD=2`（每突发一个新 kernel）、`GPU_PK_WORKLOAD=3`（持久 kernel 常驻轮询）、`GPU_GRAPHS_WORKLOAD=4`（CUDA Graphs 回放）。注意 `main.cpp:25` 的默认值是 `CPU_WORKLOAD` 而非 0。burst 尺寸/核配置等常量也在 common.h：`DEFAULT_PKT_BURST=32`（`:26`）、`MAC_CUDA_BLOCKS=1/MAC_THREADS_BLOCK=256`（`:29-30`）、`MAX_BURSTS_X_QUEUE=4096`（`:35`）、`GRAPH_BURST=8` 与 `N_GRAPHS=4096/8`（`:36-37`）、burst 状态机四态 `BURST_FREE/READY/DONE/EXIT`（`:39-42`）；`struct burst_item`（`:85`）是一次突发的描述单元。**硬约束两条**（main.cpp 参数校验）：mempool 用 GPU 内存 + CPU workload 必须开 buffer split（`:348`）；buffer split 下只接受 NO/CPU 模式（`:353-354`）。

## 3. 公共契约层：三个头文件

- `include/headers.h` 是全局 aggregator：`:23-42` libc/系统头、`:47-70` DPDK 全家桶（rte_eal/ethdev/mbuf/gpudev…）、`:75-77` 仓内三头（cuda_related/common/pipeline），并集中声明全部跨编译单元函数。**它和 pipeline.h 互相包含**（`headers.h:77` ↔ `pipeline.h:20`），靠 include guard 撑住——图谱 L3/L4 交界处因此有一个合法的环。
- `include/cuda_related.h`：`PUSH_RANGE/POP_RANGE`（`:41/:65`）NVTX 范围标注宏带 11 色分类 ID（`COMM_COL=1` `:28`、`SM_COL=2` `:29`、`WARMUP_COL=7` `:34`，与 nsight systems 轨道联动），未定义 `USE_NVTX` 时退化为空宏（`:67-68`）；`CUDA_CHECK`（`:71`）与 CU_CHECK 两级断言贯穿全部实现。
- `include/pipeline.h`：`Time` 工具类（`:30`，chrono 纳秒取时与单位换算）与 `Pipeline` 类（`:62`）——每条流水线聚合专属 RX/TX 队列号、GPU id、workload 类型、`rte_gpu_comm_list *comm_list`（`:75`）与专属非阻塞 CUDA 流（`:76`）。

## 4. GPU workload 三形态（kernel.cu）

三种 MAC 交换 kernel 共用同一个计时原语 `__globaltimer()`（`kernel.cu:25`，`__device__ __forceinline__`）——每包处理时长 `-t` 用**设备侧时钟自旋**消耗（`:42-43` 取起点，`:70-71` 等待），保证"模拟负载"测得的是真实 SM 占用而非 host 侧假等待：

- `kernel_mac_update`（`:35`）：单 block 多线程逐包交换 `rte_ether_hdr` 源/目的 MAC；host 包装 `workload_launch_gpu_processing`（`:94`，`:104` 提交）由 rx_core 每突发异步触发（`main.cpp:499`）。
- `kernel_persistent_mac_update`（`:111`）：整条流水线生命周期只提交一次（`pipeline.cpp:60-61` 调 `workload_launch_persistent_gpu_processing`，`kernel.cu:206` 真正 launch），常驻轮询 comm_list 各项状态，CPU 置 READY（`main.cpp:476` `rte_gpu_comm_set_status(..., RTE_GPU_COMM_LIST_READY)`）即在 GPU 侧完成该突发，消除每突发启动开销。
- `kernel_graphs_mac_update`（`:213`）：单个 graph 节点处理 8 个前瞻突发；`pipeline.cpp:66-76` 构造期录制——`N_GRAPHS=512` 张图，每张 `cudaStreamBeginCapture`（`:70`）后连发 8 个 `workload_launch_gpu_graph_processing`（`:71-72`）再 EndCapture+Instantiate（`:73-74`）。

## 5. 运行时主线（main.cpp + pipeline.cpp + utils.cpp）

`main`（`main.cpp:625`）总指挥：EAL+参数解析（`parse_args :232`，全部委托 `utils.cpp:122-191` 的 l2fwd_parse_* 家族）→ **mlx5 硬校验**（`:687-690`：`strcmp(dev_info.driver_name,"mlx5_pci")!=0 → rte_exit("Non-Mellanox NICs have not been validated")`）→ `RTE_GPU_FOREACH`（`:695`）枚举 GPU 并注册外部内存（`:727`）→ 建 mempool（GPU 显存或 CPU pinned，`:744/:752`，buffer split 时 payload/header 双池）→ `check_all_ports_link_status`（utils.cpp，最多 9 秒轮询）→ 逐 pipeline `new Pipeline`。`Pipeline` 构造函数（`pipeline.cpp:19-78`）：`:33` `rte_gpu_comm_create_list(gpu_id, MAX_BURSTS_X_QUEUE)` 建通信列表，`:49-50` GPU 模式建非阻塞流，`:55-77` 按 workload 类型提前启动持久 kernel 或录制 CUDA Graph——三种 GPU 模式的分歧点全在此。线程侧：`rx_core`（`main.cpp:393`）收包 → `:413` 查槽位状态 → `:462` `rte_gpu_comm_populate_list_pkts` 把包地址登进通信列表（buffer split 时 `:470-472` 手工逐包登记）→ `:476` 置 READY → `:499` 触发 workload；`tx_core`（`:523`）轮询到 DONE，CPU 模式在 `:570` 直接调 `workload_macswap_cpu`（utils.cpp:56，含 `wait_until_ns` 自旋模拟负载）。`signal_handler`（`:614`）把 SIGINT/SIGTERM/**SIGUSR1** 三种信号统一为 `force_quit`。`print_stats`（`:96`）每秒聚合 Mpps/Gbps，`print_opts`（`:179`）回显全部生效配置。

## 6. 新人上手路线

1. 读 README 的架构图与五种 workload 说明（`:23-27`），对照第 2 节 enum；
2. 按依赖序读头：`common.h`（契约）→ `cuda_related.h`（宏）→ `headers.h`（聚合+声明）→ `pipeline.h`（运行时结构）；
3. 主线读 `main.cpp` 的 main → rx_core → tx_core 三段，遇 workload 分派跳 `kernel.cu` 对应 kernel；
4. 跑通前确认三硬条件：Mellanox mlx5 网卡（`:689`）、CUDA ≥11（`CMakeLists.txt` FIND_PACKAGE(CUDA 11 REQUIRED)）、DPDK/gdrcopy 子模块已 init；推荐从 `-w 0`（纯 I/O）起步再加压 `-t`；
5. 性能分析开 `ENABLE_NVTX`（CMakeLists.txt:32）+ nsight systems，按第 3 节色轨读图；进阶读 `explain/01`（三种 GPU 模式深讲）与 `explain/02`（main.cpp 运行时主线）。
