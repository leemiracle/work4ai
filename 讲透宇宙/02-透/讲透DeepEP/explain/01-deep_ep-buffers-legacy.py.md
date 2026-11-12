# 精讲：deep_ep/buffers/legacy.py —— V1 Buffer 的 Python 门面

> 原文件：`deep_ep/buffers/legacy.py`（DeepEP，713 行）

## 一、角色定位

DeepEP 是面向 MoE 的专家并行（EP）通信库，本文件的 `Buffer` 类是其 **V1 接口的 Python 门面**（图谱 tour 第 2 步），覆盖三种通信模式：节点内 NVLink all-to-all（高吞吐）、跨节点 RDMA+NVLink all-to-all（高吞吐）、低延迟 RDMA all-to-all（IBGDA，推理场景）。它本身不含通信逻辑，职责是：初始化引导（IPC/NVSHMEM 握手）、配置推荐、参数校验与转发到 `_C.Buffer` C++ 运行时、以及把裸 C++ 返回值包装成带文档的类型。上接 `deep_ep/__init__.py` 的导出，下接 `csrc/legacy/buffer.hpp`（93KB 宿主实现）。

## 二、内部结构

- **`__init__`**：支持 torch `group` 或 mpi4py `comm` 二选一（内建 `all_gather_object` 闭包统一两者）；构造 `_C.Buffer` 后交换 device id、IPC 句柄；RDMA/低延迟模式下设置一整套 NVSHMEM 环境变量并广播 root unique id 完成引导。
- **配置推荐**：`get_dispatch_config`/`get_combine_config` 按 rank 数查表返回 `Config(num_sms, num_max_nvl_chunked_send_tokens, num_max_nvl_chunked_recv_tokens, num_max_rdma_chunked_send_tokens, num_max_rdma_chunked_recv_tokens)`（字段名已在 `csrc/legacy/config.hpp` 核实），覆盖 2–160 rank 十二档。
- **主路径**：`get_dispatch_layout`（预计算路由布局）、`dispatch`/`combine`（按 `get_num_rdma_ranks()>1` 自动路由到 `internode_*` 或节点内实现，均带 handle 缓存与非缓存两分支）、`internode_dispatch`/`internode_combine`。
- **低延迟族**：`low_latency_dispatch`/`low_latency_combine`（`use_fp8`/`round_scale`/`use_ue8m0`/`return_recv_hook`）、`clean_low_latency_buffer`、mask 三件套（`low_latency_update_mask_buffer`/`query`/`clean`）、`get_next_low_latency_combine_buffer`（零拷贝预留缓冲）。
- **杂项**：`destroy`、`capture`（取 `EventOverlap`）、`get_comm_stream`、`get_local_buffer_tensor`、`get_low_latency_rdma_size_hint`。

## 三、外部连接

`import deep_ep._C as _C`（pybind 扩展，`Config`/`EventHandle` 均来自此处）；`..utils.event.EventOverlap`（事件与张量生命周期托管）；`..utils.envs.check_nvlink_connections`/`check_torch_deterministic`（每次 dispatch/combine 前置检查）。类属性 `num_sms = 20` 是全局默认 SM 预算，可由 `set_num_sms` 静态修改（要求偶数）。

## 四、数据流

以 `dispatch` 为例：①`check_torch_deterministic`；②config 缺省则查表；③跨节点则转 `internode_dispatch`；④节点内路径把 `x` 拆成 `(x, x_scales)`（FP8 时为二元组），非缓存分支把 `topk_idx/topk_weights/num_tokens_per_rank/is_token_in_rank/num_tokens_per_expert` 全量传给 `runtime.intranode_dispatch`，收回 11 元组（recv_x、recv_topk_idx/weights、每专家接收数列表、6 个布局中间量、event），并把后者打包成 handle 返回；⑤缓存分支仅传 handle 内的 prefix 矩阵等，收回数据即返回。`combine` 是逆过程：解包 handle 第三、五个元素（注释提醒发送侧字段应取第三个），调 `runtime.intranode_combine` 归约。低延迟 dispatch 的 handle 是 5 元组 `(packed_recv_src_info, packed_recv_layout_range, num_max_dispatch_tokens_per_rank, hidden, num_experts)`，并断言 `nvshmem_qp_depth >= (num_max_dispatch_tokens_per_rank + 1) * 2`。

## 五、设计决策

- **NVSHMEM 环境在 Python 侧定调**：IBGDA 开关、QP 深度（默认 1024，保证大于在途 WR 数以跳过 WQ 槽检查）、`MAX_TEAMS=7`、`CUMEM_GRANULARITY=256MiB`、禁 NVLS/MNNVL——都是"省显存+GPU 直发 RDMA"的低延迟取向。
- **handle 两段式**：首次 dispatch 计算并返回布局句柄，重放时跳过布局计算，是 CUDA Graph 与静态路由场景的性能关键。
- **缓冲复用即零拷贝**：接收张量直接是注册缓冲的视图，因此有"同时最多持有 2 个低延迟结果"的硬约束（双缓冲轮换）。
- **`explicitly_destroy` 语义**：注释明言析构释放可能挂死 Python 异常处理流程，生产环境建议显式销毁。
- **钩子式接收**：`return_recv_hook` 把"发起 RDMA 请求"与"等数据到达"拆开，供上层与计算重叠。

## 六、新人提示

三件易翻车事：①跑过低吞吐 dispatch/combine 后必须 `clean_low_latency_buffer` 再进低延迟内核——低延迟路径要求缓冲区零初始化；②config 查表只认特定 rank 数，自定义集群规模要自己调 `Config`；③`allow_nvlink_for_low_latency_mode` 与 hook 重叠"某种程度上不兼容"（docstring 原话），且 PCIe 互连会因内存序问题出错，确保全 NVLink。理解本文件后再读 `csrc/legacy/buffer.hpp` 才有地图。
