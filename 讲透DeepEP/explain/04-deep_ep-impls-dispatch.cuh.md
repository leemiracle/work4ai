# 精讲：deep_ep/include/deep_ep/impls/dispatch.cuh —— V2 elastic dispatch 设备内核模板

> 原文件：`deep_ep/include/deep_ep/impls/dispatch.cuh`（DeepEP，411 行，命名空间 `deep_ep::elastic`）

## 一、角色定位

这是 DeepEP V2 dispatch 的**设备侧内核模板**（图谱 tour 第 7 步"JIT 设备内核模板家族"的首席成员），把 MoE token 按 top-k 路由发往各 rank 的对称缓冲。它体现 V2 的两大底座：**NCCL Gin 对称内存**（设备侧 `ncclGin` 原语直接 `put`/`get_sym_ptr` 写对端窗口）与 **JIT 特化**（rank 数、hidden 字节数、topk、SM/QP 数、超时周期全是编译期常量）。同目录姊妹模板：`hybrid_dispatch.cuh`（分层多跳）、`combine.cuh`（逆操作）、`engram_fetch.cuh`/`pp_send_recv.cuh`。

## 二、内部结构

单个 `__global__ void dispatch_impl`，模板参数即配置全貌：`kIsScaleupNVLink`（纯 scaleup 单跳 or 带 scaleout）、`kDoCPUSync`、`kReuseSlotIndices`（handle 缓存重放）、`kNumSMs`、`kNumNotifyWarps`/`kNumDispatchWarps`（warp 角色配比）、`kNumRanks`、`kNumHiddenBytes`/`kNumSFPacks`、`kNumMaxTokensPerRank`、`kNumExperts`/`kNumTopk`/`kExpertAlignment`、`kNumQPs`、`kNumTimeoutCycles`；`team_t` 随场景取 `ncclTeamTagLsa`（NVLink 子团队）或 `ncclTeamTagWorld`。内核开头先 `comm::gpu_barrier` 网格同步，随后按 warp 身份分成**通知 warps** 与 **dispatch warps** 两大角色，结尾再次 `gpu_barrier` 后 `cudaTriggerProgrammaticLaunchCompletion()`（PDL 触发后续拷贝尾核）。

## 三、外部连接

include `nccl.h`/`nccl_device.h`（NCCL 设备 API）与公共库 `common/comm.cuh`（gpu_barrier、QP 模式）、`common/layout.cuh`（`WorkspaceLayout`/`TokenLayout`/`BufferLayout` 三套偏移计算）、`common/ptx.cuh`（mbarrier、TMA 1D、cp.async、`deduplicate`、named_barrier）、`common/handle.cuh`（`NCCLGin` 封装）、`common/math.cuh`（`encode_decode_positive` 等）。宿主侧由 `csrc/kernels/elastic/` 的运行时工厂在 JIT 编译后经 `jit/handle.hpp` 发射。

## 四、数据流

**通知阶段**（`warp_idx < kNumNotifyWarps`）：各 warp 分块扫 token，`atomicAdd` 共享内存里的 expert/rank 计数（rank 侧先 `ptx::deduplicate` 去重——一个 token 的多个专家落同一 rank 只算一次）；随后把计数打包成 64 位 `(到达数<<32)|计数` 做**全网格归约**，SM0 等全部 SM 到齐后取低 32 位，经 `math::encode_decode_positive` 奇数编码后用 `gin.put_value`/`gin.put`（NVLink 逐元素 or RDMA 批量）分发给所有对端；等回对端计数、按 `kExpertAlignment` 对齐本地每专家接收数、写未对齐副本与统计张量；`kDoCPUSync` 时同步写宿主 workspace 供 CPU 读；最后两条 warp 分别对 rank 计数（含）与专家计数（排他）做 `do_psum` 前缀和——正是 `ElasticBuffer.EPHandle` 里那两个 psum 张量的出生地。

**发送阶段**（dispatch warps）：每 warp 持一块 TMA 暂存 smem，按 `warp*NumSMs+sm` 步进扫 token：①TMA load 整条 hidden 到 smem（SF 用 `cp.async` 补装并以 `cp_async_mbarrier_arrive` 计入到达）；②lane<topk 读 expert/权重、写源元数据 `rank*kNumMaxTokensPerRank+token_idx`；③rank 去重后 `atomicAdd` 对端发送计数器领槽位（或 `kReuseSlotIndices` 直接读缓存槽位）；④等 mbarrier 翻相；⑤目标可达 NVLink 则 `gin.get_sym_ptr` 拿对端地址直接 `tma_store_1d`；否则先把 token TMA store 进发送缓冲，再 `gin.put` 走 RDMA（跳过 NVLink 可达 rank）。

## 五、设计决策

- **计数与数据同内核两阶段**：省一次宿主往返与额外 kernel 发射，代价是 warp 角色静态划分（notify warps 必须为 4 的倍数组成 warpgroup）。
- **64 位打包归约 + 奇数编码**：高 32 位数到达、低 32 位数计数一次 `red_add` 完成；`encode_decode_positive`（×2+1 类编码）让"值为 0"与"未初始化"可区分，等待循环 `timeout_while` 超时还能打印 rank/thread 级诊断。
- **每 warp 一个"channel"**：`comm::get_qp_mode` 把 warp 映射到 QP 与共享模式，天然让 QP 并行度随 warp 数扩展。
- **发送侧 rank 去重 + 原子领槽**：同一 token 发同一 rank 只传一份，槽位顺序即接收端拼接顺序。
- **PDL 链式尾核**：`cudaTriggerProgrammaticLaunchCompletion` 让宿主预置的拷贝尾核（`dispatch_copy_epilogue_impl`，见 elastic.py 注释）无缝接力做重排/对齐。
- **收尾清零原子计数器**：为下一次 dispatch 复用 workspace 保持干净。

## 六、新人提示

读此文件前先掌握 `common/layout.cuh` 的三套 Layout 类，否则所有偏移量都是天书。调超时问题看两个 printf（"notify (GPU reduction) timeout" 与 "notify timeout"）即可定位是网格归约段还是跨 rank 等待段。改 token 遍历或 smem 写入顺序时注意两处注释红线：TMA buffer 的共享内存写在写完源元数据后不得再有（TMA store 一致性），以及 `cp_async_mbarrier_arrive` 必须先于 `mbarrier_arrive_and_set_tx`。多跳组网场景请转读 `hybrid_dispatch.cuh`，本模板是单跳基准实现。
