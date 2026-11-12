# 精讲 01：kernel.cu——GPU workload 三形态与 __globaltimer 计时

## 角色定位

`src/kernel.cu`（301 行）是 GPU 侧全部实现：三个 MAC 交换 kernel（每突发触发/持久常驻/CUDA Graphs）+ 三个 host 侧启动包装。它是本仓的测量对象本体——整个 l2fwd-nv 就是为了量这三种形态在转发路径上的代价差。README:23-27 的五种 workload 模式里，三种 GPU 形态的代码落点全部在此文件。

## 内部结构

计时原语先行：`__globaltimer()`（`kernel.cu:25`）封装 NVIDIA GPU 的全局定时器特殊寄存器（`__device__ __forceinline__`），每包负载模拟用它做**设备侧自旋**——`:42-43` 记起点、`:70-71` `while((__globaltimer()-pkt_start) < wtime_n)` 空转到指定纳秒。这一设计让 `-t` 参数模拟的负载真实占用 SM，而非 host 侧 sleep 假等待；上限 20ms 由 `common.h:63` `MAX_WTIME_NS` 把守。

三个 kernel 同构异触发：`kernel_mac_update`（`:35`）单 block 256 线程（`common.h:29-30`）协作处理一个 comm_list 项，`:45` 把包地址转 `rte_ether_hdr*` 后交换源/目的 MAC，完成置包状态；`kernel_persistent_mac_update`（`:111`）外层无限循环轮询 comm_list 各项（`:144-147` 见 READY 才处理），CPU 只需置状态字（`main.cpp:476`）；`kernel_graphs_mac_update`（`:213`）单个 kernel 覆盖 8 个前瞻突发（`common.h:36` `GRAPH_BURST=8`）。三个 host 包装 `workload_launch_gpu_processing`（`:94`，`:104` 每次 `<<<>>>` 提交）、`workload_launch_persistent_gpu_processing`（`:195`，`:206` 生命周期一次）、`workload_launch_gpu_graph_processing`（`pipeline.cpp:71-72` 在流捕获期间被调用从而录进图）。

## 外部连接

上游：`rx_core`（`main.cpp:499`）每突发异步触发 mode 2；`Pipeline` 构造函数（`pipeline.cpp:60-61/:66-76`）在启动期提交持久 kernel 或录制 512 张图（`N_GRAPHS = MAX_BURSTS_X_QUEUE/GRAPH_BURST = 4096/8`，`common.h:35-37`）。数据依赖：`rte_gpu_comm_list`（DPDK gpudev 通信列表，kernel 与 CPU 共享的状态机：FREE→READY→DONE，`common.h:39-42`）。NVTX 范围标注（PUSH_RANGE/POP_RANGE，`cuda_related.h:41/:65`）与 CUDA_CHECK（`:71`）贯穿。

## 数据流

mode 2：rx_core 收包 → `rte_gpu_comm_populate_list_pkts`（`main.cpp:462`）登地址 → 置 READY（`:476`）→ host 包装向专属流提交 kernel → kernel 逐包换 MAC+自旋 → 置 DONE → tx_core 发包。mode 3 省掉提交步：kernel 常驻自轮询状态字。mode 4 把"提交+处理"整体录成图：构造期对每 8 个槽位录制一张图（`pipeline.cpp:70-74` BeginCapture→8 次提交→EndCapture→Instantiate），运行期 rx_core 只回放对应图——启动成本被摊到 512 分之一且免每突发 API 调用。

## 设计决策

- **设备侧计时而非 host 计时**：测"GPU 参与转发路径的开销"必须让负载发生在 SM 上，`__globaltimer` 保证 kernel 内时间测量与 host 时钟解耦。
- **状态机放 comm_list 而非单独同步结构**：DPDK gpudev 的 `rte_gpu_comm_list` 天然是 CPU/GPU 共享内存，附加重同步结构反而引入一致性成本；`rte_gpu_wmb`（`main.cpp:475`）写屏障保证可见性序。
- **三种形态刻意共享同一 kernel 体**：差异全在触发方式，测量才是目的——变量控制得极干净。

## 新人提示

tree-sitter 对 .cu 文件零提取（digest 钉版），图谱里本文件的函数结构是手扫补充的，节点行号以本文件源码为准。调优读数时先分清三层成本：kernel 执行（`-t` 控制）、kernel 启动（mode 2 每突发一次）、状态轮询开销（mode 3 的 CPU↔GPU 时延）——nsight systems 里对应 SM 轨、CUDA API 轨与 gap。`-t` 加大后 mode 3/4 的优势会被 kernel 执行时间稀释，这是 README:184"组合 -t 与 -b 找最优"的原理。
