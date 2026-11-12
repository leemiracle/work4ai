# 02 · fused_attn/ 与 comm_gemm_overlap/——融合注意力与通信即计算

> 源文件：`transformer_engine/common/fused_attn/`（flash_attn.cu 900 行、fused_attn_fp8.cu 1525 行、context_parallel.cu 960 行）+ `transformer_engine/common/comm_gemm_overlap/`（comm_gemm_overlap.cpp 1414 行、userbuffers.cu 2762 行）。图谱中两族是"注意力子系统"与"GEMM-通信重叠"两大 hub 的主干。

## ① 角色定位：这个子系统解决什么问题

`fused_attn/` 解注意力三瓶颈：用 cuDNN frontend 把 QKV·softmax·PV 融成单图（FP8 内嵌 descale/scale 节点）；KV cache 重排与 THD 紧致布局服务推理；context_parallel 的 LSE 修正核把序列切到多卡。`comm_gemm_overlap/` 解另一问题：TP 通信藏不进 GEMM——userbuffers 把通信做成**与 GEMM 同流的 CUDA kernel**（producer/consumer 分块流水）。

## ② 内部结构：关键类/函数与行号锚

**FP8 建图**：`create_graph_fp8_fwd`（`fused_attn_fp8.cu:51`）搭图，descale_q/k/v/s、attn_scale、scale_s/o 全是图节点（:93-95）；`fused_attn_fp8_fwd_impl`（:390）查缓存图、build_plans、组 variant_pack；调度入口 `nvte_fused_attn_fwd_v2`（`fused_attn.cpp:467`）按 backend 分流。

**图缓存**：`CacheEntry`（`graph_cache.h:34`）用 once_flag 守护一次性 plan build；`GraphCache`（:41）是进程级 map；`get_graph`（:132）/`support_verdict`（:143）/`build_plans`（:158）被 f16/fp8×fwd/bwd 四站点共享。精髓是 `UnsupportedByCudnn`（:52）——"不支持"与真错误分型，前者降级后者必抛。

**外围核**：FA 先 BSHD→BHSD+pad（`prepare_flash_attn_fwd`，`flash_attn.cu:87`）；KV cache 入口 `nvte_copy_to_kv_cache`（`kv_cache.cu:295`）；CP 的 THD 簇——读对端半张量（`context_parallel.cu:196`）与 LSE 修正（:276、:341 反向）。

**userbuffers**：`ub_request`（`userbuffers.h:66`，optype/counter/credit）与 `communicator`（:90，对称内存+peer 指针表+multicast 句柄）；`producer`/`consumer`（:149-150）分块 kernel 依赖 flags 计数推进；原语 `allgather2_userbuff_inplace`（:195）与 `reducescatter2_userbuff_inplace`（:211）及 fp8/atomic 变体族。

**重叠编排**：`CommOverlapCore`（`comm_gemm_overlap.cpp:58`）持 NCCL/cuBLASMp 上下文；`CommOverlapBase`（:396）三策略——`bulk_overlap`（:444）、`atomic_gemm_overlap_rs`（:509）、`split_overlap_rs`（:617，逐块流水）。

**NVSHMEM 用点（grep 实证）**：common 树仅 `nvshmem_api/nvshmem_waitkernel.cu` 一处，角色是**对称内存信号等待三姿势**（:27）：自旋核（:22）/NVSHMEM native/STREAM_WAIT（driver API）。PyTorch 侧 `init_nvshmem_backend`（`pytorch/csrc/extensions/nvshmem_comm.cpp:22`）借 NCCL 进程组广播 uniqueid 引导，注册于 `pybind.cpp:645`。

## ③ 外部连接：与哪些子系统互依

fused_attn 被两前端 attention 消费（`pytorch/attention.py`、`jax/attention.py`）；comm_gemm_overlap 类经 `pytorch/module/base.py` 包装，`fused/userbuffers_forward_linear.py`（06 篇）接进 ops 序列。userbuffers 自举依赖 ipcsocket+multicast，窗口可对接 NCCL window（`comm_window.h:23`）。NVSHMEM 是独立可选件，与 userbuffers 不混用。

## ④ 数据流：一次典型调用的路径

FP8 前向：①pytorch 层打包 Float8 Q/K/V 与 descale 调 `nvte_fused_attn_fwd_v2`；②impl 查 `get_graph`（:420），命中则 build_plans 否则建图；③图内 amax_s/amax_o 供 recipe 更新。重叠 GEMM：`split_overlap_rs`（`comm_gemm_overlap.cpp:617`）→每 chunk 先 GEMM（:672）再 reducescatter 推 flags，第 i 块 RS 与第 i+1 块 GEMM 交错。

## ⑤ 设计决策：为什么这么设计

**通信做分块 kernel 而非 NCCL**：NCCL 是整块同步语义，无法细粒度交错；producer/consumer 逐块推进天然重叠，fp8 变体还在通信核里做类型转换。**plan build 延迟到首次使用**（`graph_cache.h:158`）：多数缓存图从未被用到。**UnsupportedByCudnn 进类型系统**：降级依赖"不支持"与"失败"可区分。**三 wait 并存**：自旋核/native/STREAM_WAIT 各有拓扑最优。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`graph_cache.h`→`fused_attn_fp8.cu:51`→`userbuffers.h:66-146`→`comm_gemm_overlap.cpp:617`。
- **坑一：IBGMM 是历史名**。本树 userbuffers.cu 无 IBGMM 字面量，等价物是 sendrecv/atomic 族；老文档 IBGMM≈现 atomic 重叠路径（:509）。
- **坑二：NVSHMEM 与 userbuffers 是两条对称内存路线**，编译期二选一。
- **坑三：THD 贯穿 CP**：CP 核全吃 cu_seqlens，先分清 sequence 与 cp-rank 顺序（:927）。
