# 05 设备算法与 NVLS——kernel 内的集合通信与硬件多播

## 角色定位

设备集合算法（图谱 L07，11 节点）是 NVSHMEM 区别于传统 SHMEM 的招牌能力：alltoall/barrier/broadcast/fcollect/reduce/reducescatter 七算法以设备函数身份编译进 bitcode/LTOIR 设备库，用户 kernel 内的线程组（thread/warp/block）直接调用，零宿主往返。NVLS 归约更进一步——用 NVLink SHARP 的多播指令让一次归约的内存流量从 O(n) 降到 O(1) 级。team（L09）是集合的通信域底座，把逻辑组映射到 NVLS 多播资源。

## 内部结构

主实现 `src/include/non_abi/device/coll/reduce.cuh`（2739 行）：核心是 `multimem.ld_reduce + multimem.st` PTX 指令的多播归约——8B/16B 变体宏在 reduce.cuh:180 与 reduce.cuh:148（`nvshmemi_<PTX_TYPE>_add_reduce_mcast16_v4_threadgroup` 等命名直接暴露 mcast 语义，4B 版在 reduce.cuh:209），tile 版 allreduce 有 v1/v2/v4 三代实现（分别在 reduce.cuh:478、reduce.cuh:361、reduce.cuh:237）由 reduce.cuh:553-565 按条件静态分派，全部 `__device__ NVSHMEMI_DEVICE_ALWAYS_INLINE`。支撑件：`wait/` 的 wait_until 轮询族、`threadgroup/nvshmemi_common_device_defines.cuh`（149 行，thread/warp/block 粒度公共宏，被 include 22 次）、`defines/utils`。team 侧 `src/host/team/team_internal.cpp`（2819 行）：init_team_pool_and_psync 起于 team_internal.cpp:1478（长 121 行，调用点 team_internal.cpp:1744）决定对称堆 pSync 布局；v1/v2 双代际 team_idx 设置对应 libnvshmem 与新 runtime 两种 API 代际。`team_internal_nvls.cpp` 把 team 绑定到 NVLS 多播对象，`nvshmemi_nvls_rsc.hpp` 管理资源生命周期，`topo.cpp` 构建 PE-GPU-NIC 拓扑供 NIC-PE 映射调优。

## 外部连接

宿主集合走另一条线：`src/host/coll/rdxn/rdxn.cpp` 全文件仅 37 行——`DEFN_NVSHMEM_TYPENAME_OP_REDUCE` 宏（rdxn.cpp:16）+ `NVSHMEMI_REPT_FOR_BITWISE_REDUCE_TYPES`（rdxn.cpp:29-31 对 and/or/xor）与 STANDARD（rdxn.cpp:33-34 max/min）、ARITH（rdxn.cpp:36-37 sum/prod）三族类型表展开出上百个 `nvshmem_<type>_<op>_reduce` 符号，函数体统一调 nvshmemi_reduce_on_stream 后 cudaStreamSynchronize（rdxn.cpp:17-26 的宏体）；reducescatter.cpp 同构。测试底座 `test/common/reduce_common.h`（433 行，common 线最大）被 21 个 reduce_*.cu 消费，`reducescatter_common.h`（194 行）被 21 个变体消费。on-stream 变体在 `src/host/stream/` 按算子逐文件展开。设备算法的调用面是 `device/nvshmem_defines.h` 38 个 static inline 与 nvshmemx 集合启动（collective_launch 基础设施）。巅峰示范在 `examples/gemm_allreduce/`：CUTLASS Sm100 GEMM 在 epilogue 直接接 NVLS allreduce（sm100_gemm_tma_warpspecialized_allreduce.hpp 的 WarpCategory+IsParticipant 双机制分派 warp 角色）。

## 数据流

设备 reduce 的多播流：各 PE kernel 调 reduce_mcast 变体 → 一条 multimem.ld_reduce 指令从 NVLS 多播对象聚合读（硬件在交换机/NVSwitch 完成 op）→ multimem.st 写回 → fence/wait_until 轮询 pSync 到位。team 参与流：nvshmem_team_split → team_internal 分配 team_idx（v1/v2 代际）→ team_internal_nvls 建立/绑定多播对象 → 对称堆 pSync 区域按 init_team_pool_and_psync 的布局分配。

## 设计决策

三代 tile allreduce 模板（v1/v2/v4）并存而非替换——不同 dtype/规模下最优展开不同，:553 的静态分派把选择留给编译期；宏生成器（rdxn.cpp 37 行生百符号）用最小源码面积覆盖 OpenSHMEM 规范的类型×算子矩阵，reducescatter 等族直接复制此范式；NVLS 资源三处联动（team_internal_nvls 绑定、nvls_observer 监听堆变化、nvls_rsc 管生命周期）是因为多播对象必须覆盖对称堆的真实映射——堆变则多播对象变。v1/v2 双代际是 API 演进期兼容的代价，读码时先确认自己走哪代。

## 新人提示

性能调优先看 skills/nvshmem-tune-performance 与 perftest/device/coll 的 9 组时延基准（含 redmaxloc）；NVLS 需要硬件/驱动支持，nvshmem-info 可查多播可用性。读 reduce.cuh 按 148→237→553 的顺序（标量 mcast→tile v4→分派器）。写自定义 kernel 集合参考 examples/moe_shuffle.cu 的 WARP_SCOPED 模板切换 warp/block 发射。注意 non_abi 目录名本身就是警告：这些设备符号非稳定 ABI，跨版本不可依赖。
