# 07 · disagg 与传输：双层状态机、Bounce 信用流控与双 gRPC 面

## 一、角色定位

分离式推理（disaggregated serving）把 prefill 与 decode 拆到不同 GPU/节点上，中间必须有人把 KV cache（以及请求辅助状态）可靠地从发送端搬到接收端。本主题覆盖三件套：**Python 编排层** `tensorrt_llm/_torch/disaggregation/native/transfer.py`（4588 行，会话/任务编排与正确性仲裁）、**C++ 数据面** `cpp/tensorrt_llm/executor/cache_transmission/`（NIXL/UCX/Mooncake/MPI 四种 agent 后端 + bounce 可靠传输层）、**两个 gRPC 服务面**（openengine 与 smg）。它是图谱 L07 层的主体，上接 scheduler 下接 RDMA/NVLink 硬件。

## 二、内部结构

**transfer.py 是一台双层状态机。** 逻辑层回答"这次交付的承诺是什么"：`TaskStatus`（transfer.py:204，INIT/TRANSFERRING/TRANSFERRED/ERROR）与不可变决策记录 `_LogicalOutcome`（transfer.py:212）成组写入 `_LogicalOutcomes` cohort（transfer.py:220），每个 task 绑定后逻辑结局即告冻结。物理层回答"某个 peer 对源内存的访问是否确已停止"：`_PhysicalOperationState`（transfer.py:598）六态——ADMITTED/SUBMITTING/SUBMITTED/NOT_SUBMITTED/BACKEND_DONE/IN_DOUBT，源码注释明写合法前向路径，且只有 NOT_SUBMITTED 与 BACKEND_DONE 两种"排水态"能证明操作不再触碰源内存（transfer.py:612 `_DRAINED_PHYSICAL_OPERATION_STATES`）。IN_DOUBT 态是证据悬置区：后端状态可能丢，必须保留 backend 根（`_PhysicalOperation`，transfer.py:628）直到物理静默。接收侧对应 `_ReceiveOperationOwner`（transfer.py:331）管理 writer cohort 的发布/结算。控制面走 ZMQ + msgpack，`MessageType` 定义 7 种控制消息（transfer.py:184）。

**Bounce 是 NIXL 之上的自研可靠传输层。** `BounceTransport.cpp`（2163 行）头部注释（BounceTransport.h:57-103）完整描述了 reactor 拓扑：BounceContext/BounceSender（BounceTransport.h:271）/BounceReceiver（:176）/BounceTransport（:472）四件套，单 IO 线程驱动协议推进 + M 个 scatter worker；消息四面：WANT→GRANT→DATA→ACK。发送方 gather 到本地 arena 区再 RDMA 写，接收方 scatter 到目标池。失败原因枚举 `BounceFailReason` 九种（BounceTransport.h:106），从 kPlanRejected 到 kPeerNack 全链可解释。

**CreditScheduler 是信用流控的心脏**（CreditScheduler.h:78）：纯逻辑类，无线程无 CUDA。`Grant`（CreditScheduler.h:40）= 一次接收方 arena 区的独占写权限（flow/offset/addr/len）；`onWant`（:91）按流声明 chunk 尺寸、`onScatterDone`（:94）释放并再调度、`reclaimByPrefix`（:104）按 peer 前缀整体回收。flow id 是 "peer\x1frid" 而非裸 agent 名——同一 peer 的多个并发请求是独立流。

## 三、外部连接

数据面后端四选一：`cache_transmission/nixl_utils/`（默认，bounce 目录 10 源文件 3769 行 + GatherScatterKernel.cu）、`mooncake_utils/transferAgent.cpp`、`mpi_utils/connection.cpp`、`ucx_utils/`。Python 侧同样有两代 bounce：`native/bounce/`（6 文件 1550 行，per-region 粒度）与 C++ bounce v2（transfer-agent staging buffer 共享收发）；开关 `agent_bounce_buffer_enable` 在 transceiver.py:190-196 显式路由到其一，`kv_cache_bounce_size_mb` 兼作容量与总开关（bounce/config.py:1-3），环境闸门 `TRTLLM_KV_CACHE_BOUNCE_MIN_BYTES/MIN_BLOCKS` 区分 recurrent-state 与 plain-KV。gRPC 双面：openengine proto 定义 Inference（openengine.proto:38，Generate 流式）与 Control（:43，GetServerInfo/GetModelInfo/GetLoad/Health/Abort/LoadLora/UnloadLora/ListLoras/GetKvEventSources/SubscribeKvEvents 流式共 10 RPC）；smg 是对接外部 router（如 sgl-router）的高速面，pre-tokenized 输入直入（smg/servicer.py:27），实现 Generate/Embed/HealthCheck/Abort/GetModelInfo/GetServerInfo 六 RPC。

## 四、数据流

以一次 KV 发送为例：`KVSendTask`（transfer.py:845）经 `Sender.dispatch_task`（:1828）等到全部 peer 的 `RecvReqInfo`（:111，to_bytes/from_bytes msgpack 序列化）→ `_build_kv_write_meta`（:1651）组装 src/dst 指针数组 → `_submit_transfer`（:1153）交付 NixlTransferAgent → IO 线程轮询在途写（`_poll_in_doubt_transfers`，:1236）；接收端 `Receiver`（:2847）的 `_respond_with_kv`（:1943）回 KV_AGENT_RESULT，`_fanin_bounce_safe`（:3010）处理多发送端扇入。异常路径全走 `_retain_in_doubt_transfer`（:1216）留证 → poll 复核 → 逻辑层结算。C++ 侧 bounce 一轮：submit() 返回 `shared_future<BounceResult>`，IO 线程收 GRANT 挂 credit、postWrite 延到 gather 完成与 credit 双就绪，ACK 全齐 resolve SUCCESS。

## 五、设计决策

① **逻辑/物理双层解耦**是分布式传输正确性的通用范式：物理证据可能迟到（backend status 丢失），逻辑承诺不能因此悬置——两层各排各的水位线，`resources_drained` 双侧都绿才算会话可关。② **Buddy 分配器而非 exact-fit**（CreditScheduler.h 注释）：最多 2× 内碎片换确定性 O(1) 合并；区域只活几毫秒，浪费的是瞬态并发不是驻留内存，且 XOR buddy 查找无需在 GPU buffer 里放 boundary tag。③ **隔离（quarantine）而非立释放**：单侧 RDMA 写无法中止，peer 掉线后其 granted 区只能按超时隔离再回收——把不可取消的硬件操作转译成可等待的协议状态。④ **为什么不用 notifMsg**：BounceTransport.h 注释明言轮询在途写 Done 即发 DATA，数据落远端这一事实本身就是通知，省掉一条控制消息。

## 六、新人提示

先读 BounceTransport.h:53-103 的 reactor 注释（全主题最好的地图），再读 transfer.py:598-631 的状态机注释，最后按 WANT/GRANT/DATA/ACK 顺序跟一遍 CreditScheduler 的事件方法。注意三个易混点：flow id ≠ agent 名；bounce 有 Python/C++ 两代且由同一配置字段开关；mooncake_utils 下没有 bounce（那是 agent 后端，别找错树）。调参入口 `kv_cache_bounce_size_mb=0` 即整链退化为逐块直传（transceiver.py:214 的报错文案可作行为确认）。proto 生成码勿手改，契约源在 `tensorrt_llm/grpc/openengine/proto/openengine/v1/`。
