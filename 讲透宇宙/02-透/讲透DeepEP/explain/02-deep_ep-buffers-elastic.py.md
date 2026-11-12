# 精讲：deep_ep/buffers/elastic.py —— V2 ElasticBuffer 宿主编排

> 原文件：`deep_ep/buffers/elastic.py`（DeepEP，1107 行，全仓最大 Python 文件）

## 一、角色定位

`ElasticBuffer` 是 DeepEP **V2 的核心宿主类**（对应图谱 tour 第 5 步"V2 核心"），一个缓冲统一承载四类通信：EP dispatch/combine（NVLink 和/或 RDMA）、Engram（远程 KV cache 拉取，RDMA）、流水线并行 pp_send/pp_recv（NVLink）、all-gather reduce-scatter 会话（AGRS）。"Elastic"指底层内存形态可弹性演进——当前 GPU-only，CPU 与 GPU+CPU 混合在路线图上（docstring 明言）。与 V1 依赖 NVSHMEM 不同，V2 底座换成 **NCCL 对称内存（Gin 窗口）**，于是引导流程也变为 NCCL 通信句柄与 POSIX FD 交换。本文件还包含 `EPHandle`——dispatch/combine 之间的路由凭据。

## 二、内部结构

- **`EPHandle`**：缓存 dispatch 上下文（`psum_num_recv_tokens_per_scaleup_rank`、`psum_num_recv_tokens_per_expert`、`recv_src_metadata`、`dst_buffer_slot_idx`、hybrid 模式专属的 `token_metadata_at_forward`/`channel_linked_list` 等）；其 `deterministic_sort` 是确定性排序 epilogue 的纯 PyTorch 实现。
- **`ElasticBuffer.__init__`**：大缓冲时设 `NCCL_WIN_STRIDE`（NCCL 内部按 4GiB 对齐窗口步长）；多平面网络设 `NCCL_SYM_REUSE_SYSMEM_HANDLES`；QP 数自动定（hybrid 且支持 fast RDMA atomic 为 65，否则 129，非 hybrid 17）；CPU 段经 `create_cpu_handle` + `all_gather_object` 交换 (pid, fd)；最后算逻辑域（scaleout/scaleup）与物理域（rdma/nvlink）索引，三重同步收尾。
- **容量提示族**：`get_buffer_size_hint`（2MB 对齐）、`get_engram_storage_size_hint`（GPU 接收区+CPU 存储，按 32B 对齐 LDG.256）、`get_pp_buffer_size_hint`（环形收发×双缓冲）、AGRS 两提示。
- **理论资源模型**：`get_theoretical_num_sms`（`@weak_lru` 缓存，按 RDMA/NVLink 带宽与每 SM 读 200GB/s、写 50GB/s 建模，`prefer_overlap_with_compute` 时少用 SM，否则至少 64）；`get_theoretical_num_qps`（直连模式 `min(num_sms, 9)` 省 doorbell 开销，hybrid 模式 `num_sms*16+1` 每通道独立 QP）。
- **主路径**：`dispatch`（自动 SM/QP、handle 缓存、`do_expand`/`do_zero_padding`、确定性 epilogue 挂钩）与 `combine`；另有 `barrier`、`engram_write`/`engram_fetch`（返回等待钩子）、pp 三件套、AGRS 会话（`agrs_new_session` 上下文管理器 + `all_gather` + `agrs_get_inplace_tensor`）。

## 三、外部连接

`_C.ElasticBuffer`/`_C.calculate_elastic_buffer_size`/`_C.create_cpu_handle` 是 C++ 侧对应物；`utils.comm.get_nccl_comm_handle`（可强制新建 communicator，CPU 段场景必需）；`utils.envs` 的带宽探测 `get_rdma_gbs`/`get_nvlink_gbs` 与硬件检查；`utils.semantic.weak_lru`/`value_or`、`utils.math.align`、`EventOverlap`。设备侧由 `deep_ep/include/deep_ep/impls/dispatch.cuh` 等 JIT 模板承接。

## 四、数据流

`dispatch()` 走读：①从 handle 或入参取 `num_topk`，SM/QP 自动定并断言不超已分配 QP；②解包 `(x, sf)`；③handle 非空时强校验 `(num_experts, expert_alignment, num_max_tokens_per_rank)` 与 handle 上下文一致，且强制 `do_cpu_sync=False`；④把 10 项缓存布局与全部参数（约 30 个）透传 `runtime.dispatch`；⑤收回 17 元组，非缓存时构造 `EPHandle`（`do_handle_copy` 决定是否克隆 topk_idx 防用户篡改）；⑥`deterministic` 时把 `handle.deterministic_sort` 注册为 event 后置钩子或同步执行；⑦重组 `(recv_x, recv_sf)` 返回。`combine()` 则复用 handle 内的 SM 数与元数据调 `runtime.combine`。

## 五、设计决策

- **NCCL Gin 取代 NVSHMEM**：对称窗口+设备侧 `ncclGin` 原语让 V2 与 NCCL 生态（多平面、symmem 复用）共生，QP/SL 可调（`EP_OVERRIDE_RDMA_SL`）。
- **带宽反推 SM 数**：以"通信时间 ÷ 每 SM 读写带宽"求饱和所需 SM，×1.25 余量后取偶，兼顾与计算重叠；模型假设均衡门控（docstring 提醒 V3.0 group-limited gate 不适用）。
- **expand 布局**：`do_expand` 让每个 (token, expert) 占独立槽，天然适配分组 GEMM；配套 `do_zero_padding` 清对齐空隙。
- **确定性路由**：双键排序（`expert_idx * 1e10 + src_global_idx`）保证跨运行位序可复现，代价是 epilogue 一次 permute。
- **CPU 同步可选**：`num_recv_tokens` 在免同步时"可能不准"，用 psum 末元素与 OOB mask 兜底——为 CUDA Graph 兼容牺牲精确计数。

## 六、新人提示

三个易混点：①V1 `Buffer` 与 V2 `ElasticBuffer` 并存，测试分别在 `tests/legacy` 与 `tests/elastic`，读代码别串；②handle 复用的前提是路由拓扑不变，`topk_idx` 会从 handle 取，传入即断言报错；③`EP_BUFFER_DEBUG=1` 能打印缓冲尺寸与 SM 近似的全部中间量，调带宽模型的第一工具。Engram/PP/AGRS 均标注 Experimental，API 可能变动。
