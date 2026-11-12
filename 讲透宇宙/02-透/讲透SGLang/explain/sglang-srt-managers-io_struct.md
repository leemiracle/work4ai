# 深度解析：`python/sglang/srt/managers/io_struct.py`

> 源码: python/sglang/srt/managers/io_struct.py @ commit ec075d8bc

这是 SGLang 进程间 ZMQ 通信的"消息圣经"——TokenizerManager、Scheduler、DetokenizerManager 三个（组）进程之间流转的所有对象都在本文件定义（模块 docstring 第 14-17 行原话：*"The definition of objects transferred between different processes (TokenizerManager, DetokenizerManager, Scheduler)"*）。文件全长 2159 行，包含约 90 个 dataclass，覆盖四条主干消息流（请求下行、token ID 批次、解码文本上行、embedding 上行）以及权重更新、abort、缓存管理、profile、LoRA、负载观测等十余族控制消息。所有消息类共享 `BaseReq`/`BaseBatchReq` 基座，且文件末尾的 `_check_all_req_types()`（L2136）在 **import 时**强制校验命名约定（`*Req`/`*Input`/`*Output` 后缀必须与基类继承关系一致），使这个单文件成为唯一可信的消息注册表。

---

## 0. 先建立全景：消息拓扑与 ZMQ 信道

SGLang server 的多进程架构（`--tokenizer-worker-num 1` 的经典形态）：

```
HTTP Server (FastAPI, uvicorn)
   │  GenerateReqInput / EmbeddingReqInput（进程内调用或经 http_ipc）
   ▼
TokenizerManager ──── send_to_scheduler (ZMQ_PUSH, ipc) ────▶ Scheduler
       ▲                                                          │
       │ ◀── send_to_tokenizer (Scheduler 的应答/直通输出) ────────┘
       │ ◀── send_to_tokenizer (DetokenizerManager 的解码文本) ── DetokenizerManager
       │                                        ▲
       └────────────────────────────────────────┘
                          Scheduler ── send_to_detokenizer ──▶ DetokenizerManager
```

一条生成请求的完整消息生命周期：

1. **TokenizerManager → Scheduler**：`TokenizedGenerateReqInput`（L719，单条）或 `BatchTokenizedGenerateReqInput`（L813，批量包装）——分词完成后经 `send_to_scheduler.send_pyobj` 发出。
2. **Scheduler → DetokenizerManager**：`BatchTokenIDOutput`（L1082）——一批请求跑完（或流式跑出若干 token）后，Scheduler 把输出 token id、logprobs 等原始数字结果发给 DetokenizerManager。
3. **DetokenizerManager → TokenizerManager**：`BatchStrOutput`（L1154）——增量解码成字符串后发回（detokenizer_manager.py L364 构造、L152 `send_to_tokenizer.send_pyobj` 发送）。
4. **TokenizerManager → 客户端**：asyncio event loop 里按 `rid` 匹配 state，推给等待的 Future/Stream。

所有控制类消息（abort、权重更新、profile、flush cache……）**复用同一条 TokenizerManager↔Scheduler 信道**，靠对象类型分发。因此本文件按"消息流向"分组是最自然的读法，下文即按此组织。

---

## 1. 公共基座（L53-134）

### `BaseReq`（L53-73）——单请求类消息的 ABC

```python
@dataclass
class BaseReq(ABC):
    rid: Optional[Union[str, List[str]]] = field(default=None, kw_only=True)
    http_worker_ipc: Optional[str] = field(default=None, kw_only=True)
```

- `rid`（request id）：全链路关联键。TokenizerManager 生成 `uuid.uuid4().hex`；Scheduler、DetokenizerManager 原样透传；TokenizerManager 收到输出后靠它在 `self.rid_to_state` 里找到对应的 asyncio Future。
- `http_worker_ipc`：多 HTTP worker 部署时标记该请求来自哪个 worker 的 IPC 通道，回程路由用。
- `regenerate_rid()`（L58）：重新生成 rid（支持批量 list 形态），用于内部派生请求。
- `_validate_rid_uniqueness()`（L66）：批量请求展开后校验 rid 无重复，`Counter` 统计后抛 `ValueError`——这是防止用户显式传重复 rid 导致下游 state 覆盖的第一道闸。

### `BaseBatchReq`（L76-84）——批量输出类消息的基座

注意与 `BaseReq` 是**平行的两个基类**（不是继承关系）：`rids`/`http_worker_ipcs` 均为 `List[str]`。所有 `Batch*Output` 继承它。`_check_all_req_types` 对两个基类都做后缀校验。

### `SpeculativeDecodingMetricsMixin`（L87-107）——投机解码指标混入

三个字段：`spec_verify_ct`（verify 前向次数）、`spec_num_correct_drafts`（严格接受的 draft 数，不含 bonus token）、`spec_correct_drafts_histogram`（接受长度直方图，`histogram[k]=c` 表示 c 个 step 接受了 k 个）。混入 `BatchTokenIDOutput` 和 `BatchStrOutput`，避免两处重复定义；投机解码关闭时 histogram 为空 list。

### `SessionParams`（L111-117）——会话续写参数

`id`/`rid`/`offset`/`replace`/`drop_previous_output` 五个 Optional 字段，随 `TokenizedGenerateReqInput.session_params` 下行，供 Scheduler 侧 session 管理做多轮前缀续写。

### 多模态类型别名（L120-134）

`MultimodalDataInputFormat` 是关键：允许**单对象 / List / List[List]** 三种嵌套形态（`MultimodalDataInputItem` 为 image/video/audio 的并集）。这就是 `GenerateReqInput.image_data` 等字段的类型来源，也是后文 `normalize_batch_and_arguments` 要拍平的对象。

---

## 2. API 入口层（HTTP → TokenizerManager，进程内）

这一组的特殊之处：它们既是 ZMQ 消息定义，也是 **FastAPI 的请求体模型**（OpenAI 兼容层直接构造它们），同时是 `Engine.generate()` 的编程接口。它们不跨 ZMQ（跨 ZMQ 的是其 token 化后的形态），但定义在"消息圣经"里，因为离线引擎（`launch_engine`）模式下它们会随 Engine 调用链进入同一套归一化管线。

### `GenerateReqInput`（L137-716）——生成请求的"胖"形态，全文最复杂的类

约 60 个字段，按功能分块：

| 字段块 | 代表字段 | 行号 | 说明 |
|---|---|---|---|
| 输入 | `text` / `input_ids` / `input_embeds` | L140-149 | 三选一；`input_ids` 用 `PlainValidator(validate_optional_list_i64_1d_2d)` 替代 pydantic 逐元素校验（C 循环提速，L144 注释） |
| 多模态 | `image_data` / `video_data` / `audio_data` / `use_audio_in_video` | L156-162 | 三种嵌套格式见上文类型别名 |
| 采样 | `sampling_params` | L164 | Dict 或 List[Dict]，具体约束在 `SamplingParams` |
| logprob | `return_logprob` / `logprob_start_len` / `top_logprobs_num` / `token_ids_logprob` / `return_text_in_logprobs` | L166-175 | `logprob_start_len=-1` 表示只返回输出部分 |
| 输出控制 | `stream` / `return_hidden_states` / `return_routed_experts` / `return_entropy` / `return_indexer_topk` | L177-251 | hidden states / MoE 路由 / 熵等各类回传开关 |
| 会话 | `session_params` | L193 | 见 `SessionParams` |
| LoRA | `lora_path` / `lora_id` | L196-198 | path 由用户给，uid 由 TokenizerManager 分配 |
| 高级 | `custom_logit_processor` / `positional_embed_overrides` | L200-207 | 前者是序列化的 `CustomLogitProcessor`；后者含 torch.Tensor 故类型标 `Any` 绕开 pydantic schema（L206 注释） |
| PD 分离 | `bootstrap_host/port/room/pair_key` / `decode_tp_size` | L210-214 | prefill/decode 分离引导连接 |
| DP 路由 | `routed_dp_rank` / `disagg_prefill_dp_rank` / `data_parallel_rank`(废弃) | L220-224 | 外部 router 指定 DP worker |
| 可观测 | `priority` / `extra_key` / `routing_key` / `no_logs` / `custom_labels` / `external_trace_header` / `received_time` | L233-255 | 优先级调度 / cache_salt / 分布式追踪上下文 |

**核心方法 `normalize_batch_and_arguments()`（L279-313）**——TokenizerManager 收到请求后第一步调用：

1. `data_parallel_rank` 废弃迁移（L292-302，发 DeprecationWarning）；
2. `_validate_inputs`（L315）：text/input_ids/input_embeds 必须恰好给一个；
3. `_determine_batch_size`（L328）：探测 `is_single` 与 `batch_size`，同时清掉互斥字段（给了 text 就抹掉 input_embeds）；
4. `_handle_parallel_sampling`（L356）：读 sampling_params 的 `n`，`n>1` 时单请求升格为 batch；
5. 批量路径 `_normalize_batch_inputs`（L397）把**所有** per-request 字段展开成等长 list：`_expand_inputs`（L418，text/ids/embeds 乘以 n）、`_normalize_rid`（L516，用户给 str 则展开成 `{rid}_{i}`）、`_normalize_image_data`（L447，顺带推导 `modalities` 为 "image"/"multi-images"/None）、`_normalize_logprob_params`（L533，list 型 logprob 参数与 n>1 互斥直接报错）等 11 个子方法；
6. 最后 `_validate_rid_uniqueness` 收尾。

**`__getitem__(i)`（L637-716）**：把 batch 中第 i 条切出来变成单条 `GenerateReqInput`。两个细节：① `_sub_obj_cache` 缓存（L640），重复 `obj[i]` 返回**同一实例**——注释明说是为了避免不同调用点拿到发散对象引发隐蔽 bug；② 逐请求字段按 `self.xxx[i]` 切、全局字段（`stream`/`no_logs`/`priority`）原样传，切分规则与 normalize 的展开规则严格互逆。

### `EmbeddingReqInput`（L828-1032）——embedding/rerank 请求的胖形态

与 `GenerateReqInput` 同构但更瘦：无 sampling/logprob（`sampling_params` 是"兼容性占位"，normalize 时强写 `max_new_tokens=0`，L931/L943）；独有 `is_cross_encoder_request`（L866，rerank 打分）、`dimensions`（L880，Matryoshka 嵌入维度裁剪）、`embed_override_token_id`+`embed_overrides`（L846-853，token 位置嵌入替换，位置解析推迟到 tokenizer 之后）、`return_pooled_hidden_states`（L888）。`normalize_batch_and_arguments`（L894-947）逻辑同款精简版。`__getitem__`（L979）对 cross-encoder 请求走特殊切分（text 包成单元素 list，L987）。

---

## 3. TokenizerManager → Scheduler：请求下行主干

**触发时机**：TokenizerManager 完成 tokenize（+ 多模态预处理）后立即发送。Scheduler 的 event_loop 在每轮迭代开头 `recv_requests()` 非阻塞收件，新请求进 waiting_queue。

### `TokenizedGenerateReqInput`（L719-810）——生成请求的"瘦"形态

胖形态归一化+分词后的单条结果。字段全部是定态类型（不再有 Union[List, T] 两栖形态）：`input_ids: array[int]`（L724，用标准库 `array` 而非 list，pickle 更小更快）、`mm_inputs: object`（预处理好的多模态张量打包）、`sampling_params: SamplingParams`（已是解析后的对象而非 Dict）、`token_ids_logprob: List[int]`，以及与胖形态一一对应的直通字段（lora/bootstrap/priority/……）。新增 `time_stats: Optional[Union[APIServerReqTimeStats, DPControllerReqTimeStats]]`（L810）——观测时间戳从 API server 一路带到 Scheduler。

### `BatchTokenizedGenerateReqInput`（L813-825）

薄包装：`batch: List[TokenizedGenerateReqInput]` + `__len__/__getitem__/__iter__`。存在意义是让一次 ZMQ send 携带多条（TokenizerManager 攒批后发，减少 IPC 次数；tokenizer_manager.py L1231 处按首元素类型分流生成/嵌入）。

### `TokenizedEmbeddingReqInput`（L1035-1064）与 `BatchTokenizedEmbeddingReqInput`（L1067-1079）

embedding 版同构物。前者独有 `token_type_ids`（L1044，BERT 系需要）与 `image_inputs: dict`（L1042）；`dimensions`/`return_pooled_hidden_states` 直通。

### 控制消息（同样走 TokenizerManager → Scheduler）

- **`AbortReq`（L1673-1684）**：客户端断连或 `/abort` 时发。`abort_all=True` 清空全部在途请求；`rid=""` 是兼容旧行为的 hack（L1682 FIXME 注释自认）；可携带 `finished_reason`/`abort_message` 生成 ABORTED 类结束原因。触发时机：流式请求的 generator 被 GC/取消、健康检查超时主动放弃。
- **`FlushCacheReqInput`（L1258）/ `FlushCacheReqOutput`（L1263）**：`/flush_cache` 端点；Scheduler 在**空闲**（waiting/running 均空）时才真正 flush radix cache 并重建，忙时拒绝（`success=False`）。
- **`ClearHiCacheReqInput/Output`（L1248-1255）**：清分层缓存（HiCache）的 host/storage 层。
- **外部语料四件套（L1270-1305）**：`AddExternalCorpusReqInput`（挂载外部 KV 语料，支持 file_path/documents/token_chunks 三种来源）、`RemoveExternalCorpusReqInput`、`ListExternalCorporaReqInput` 及各自 Output——服务 RAG-ish 的 KV 注入场景。
- **`AttachHiCacheStorageReqInput`（L1308-1340）/ `DetachHiCacheStorageReqInput`（L1349）**：运行时动态挂/卸 HiCache 存储后端（如 mooncake）；`__post_init__` 校验 `prefetch_policy ∈ {best_effort, wait_complete, timeout}` 与 `write_policy ∈ {write_back, write_through, write_through_selective}`（L1322-1340）——枚举约束内嵌在消息定义里，坏参数在发送端就炸。
- **`PauseGenerationReqInput`（L1362-1389）**：权重热更的前奏。三种 mode（docstring 写得非常清楚）：`abort`（中止全部在途）、`retract`（在途请求退回 waiting_queue，之后可 flush cache，恢复时重算）、`in_place`（冻结 event_loop 但保留 KV，恢复后无损继续）。
- **`ContinueGenerationReqInput`（L1392-1399）**：解除暂停；`torch_empty_cache=True` 时先归还 PyTorch allocator 缓存块再恢复（避免与活跃 stream 竞争）。
- **`GetInternalStateReq/SetInternalStateReq`（L1692-1710）**：读取/热改 Scheduler 内部状态（server_args 子集）。
- **`SlowDownReqInput`（L1663）**：给每个 forward 加 sleep，混沌测试用。
- **`FreezeGCReq`（L1766）/ `ConfigureLoggingReq`（L1771）**：冻结 Python GC（避开周期性长尾停顿）、动态改请求日志配置。
- **`ProfileReqInput`（L1713）→ `ProfileReq`（L1744）→ `ProfileReqOutput`（L1760）**：三段式。HTTP 层先收 `ProfileReqInput`（含 `activities=["CPU","GPU","MEM","RPD"]`、`profile_by_stage`、`num_steps` 自动停止等），TokenizerManager 转成带 `ProfileReqType`（START/STOP，L1739）的 `ProfileReq` 发给 Scheduler，Scheduler 挂 torch profiler 后回 Output。
- **`ExpertDistributionReq`（L1812）/ `ExpertDistributionReqOutput`（L1817）**：MoE 专家分布统计的 START/STOP/DUMP_RECORD 三动作（`ExpertDistributionReqType` L1806）。
- **`BlockReqInput`（L1940）+ `BlockReqType`（L1935）**：BLOCK/UNBLOCK 调度器接客（运维熔断）。
- **会话三件套（L1782-1798）**：`OpenSessionReqInput`（`capacity_of_str_len` 预留会话窗口）→ `OpenSessionReqOutput`（返回分配的 `session_id`）、`CloseSessionReqInput`。走的是 TokenizerManager 自己的 session 通道。
- **`ReleaseMemoryOccupationReqInput/Output`（L1627-1636）与 `ResumeMemoryOccupationReq*`（L1639-1648）**：RL 场景专用——训练间隙按 `tags ∈ {weights, kv_cache}` 归还/恢复 GPU 显存占用（配合 KVCache 的 memory saver adapter）。
- **dump 族（L2103-2132）**：`SetInjectDumpMetadataReqInput`、`LazyDumpTensorsReqInput`、`DumperControlReqInput`——张量/元数据 dump 的遥控器。
- **`WatchLoadUpdateReq`（L2098）**：方向相反！这是 **Scheduler → TokenizerManager** 的负载推送（见第 6 节）。

---

## 4. Scheduler → DetokenizerManager：token ID 批次

**触发时机**：每个调度 step 结束、输出张量 `copy_to_cpu()` 后（scheduler.py L2970/L3026/L3069），Scheduler 把该批的原始输出打包发出。`--skip-tokenizer-init` 时它也会被"直通"发给 TokenizerManager（见 `output_ids` 字段注释 L1091）。

### `BatchTokenIDOutput`（L1082-1151）——纯数字结果集

字段全景（全部 List，一个元素对应批内一个请求）：

- **完成与解码状态**：`finished_reasons: List[BaseFinishReason]`（L1085）、增量解码四元组 `decoded_texts/decode_ids/read_offsets`（L1087-1089，DetokenizerManager 靠 read_offset 做增量增量解码）、`skip_special_tokens/spaces_between_special_tokens/no_stop_trim`（L1093-1095，detokenize 配置随数据走）；
- **token 计数**：`prompt_tokens/reasoning_tokens/completion_tokens/cached_tokens`（L1098-1101）——计费与 usage 统计的直接来源；
- **logprob 大全集**（L1104-1116）：12 个字段，`{input,output}×{token,top,token_ids}×{val,idx}` 组合加 `output_token_entropy_val`。val/idx 分离的紧凑布局（避免 List[List[dict]] 的 pickle 膨胀）；
- **张量型附加输出**：`output_hidden_states`（L1119）、`routed_experts: List[Optional[torch.Tensor]]`（L1125，形状 (token, layer, top_k)，注释言明由 DetokenizerManager 负责 base64 化以挪出 tokenizer 热路径）、`indexer_topk`（L1127）；
- **占位符信息**：`placeholder_tokens_idx/val`（L1132-1133），多模态展开 token 的位置/长度，供输出侧对齐；
- **调度元数据**：`retraction_counts`（L1136，该请求被 retract 的次数——SGLang 特色的 decode 内存不足回退机制）、`token_steps`（L1139，RL 权重版本步号）、`load: GetLoadsReqOutput`（L1142，搭便车：结果批次顺路捎回本 DP rank 负载）、`cached_tokens_details`（L1146，device/host/storage 分源的缓存命中明细）、`dp_ranks`（L1148）、`time_stats: List[SchedulerReqTimeStats]`（L1151）。

注意它继承 `BaseBatchReq` + `SpeculativeDecodingMetricsMixin` 双基座。

---

## 5. DetokenizerManager → TokenizerManager：文本/嵌入上行

**触发时机**：DetokenizerManager 收到 `BatchTokenIDOutput`，做增量 detokenize（含 stop string 检查、增量 decode）后立即构造下列消息经 `send_to_tokenizer` 发出。

### `BatchStrOutput`（L1154-1217）——最终用户可见的结果

与 `BatchTokenIDOutput` 字段几乎镜像（logprob 12 件套、token 计数、hidden states、retraction_counts、time_stats……），差异点：

- `output_strs: List[str]`（L1159）取代增量解码三元组——已是完整文本；
- `finished_reasons: List[dict]`（L1157）——注意这里是 **dict** 而 TokenID 侧是 `BaseFinishReason` 对象，跨进程序列化时被规范化；
- `routed_experts: List[Optional[str]]`（L1190）——base64 字符串而非 Tensor（L1187-1189 注释：编码工作被刻意放在 DetokenizerManager，"off the tokenizer hot path"）。

### `BatchEmbeddingOutput`（L1220-1245）

embedding 模型的对应物：`embeddings: Union[List[List[float]], List[Dict[int, float]]]`（L1225，第二种形态用于稀疏 embedding）+ token 计数 + `pooled_hidden_states`（L1243，注释强调"单个 stacked tensor 发送以最小化 pickle 开销"）。

### 各类 `*ReqOutput` 应答

权重更新、flush cache、profile 等的应答（`success/message` 二元组为主）由 **Scheduler 直接**经其 `send_to_tokenizer` socket 发回 TokenizerManager（不经过 DetokenizerManager）。

---

## 6. 负载观测族：/v1/loads 与 DP 感知路由（L1945-2100）

这是近期演进出的一整块子系统，消息方向混合，单列一节：

- **五个指标 dataclass**：`MemoryMetrics`（L1945，weight/kv_cache/graph 显存 + token 容量）、`SpeculativeMetrics`（L1959，accept_length/accept_rate）、`LoRAMetrics`（L1976，槽位利用）、`DisaggregationMetrics`（L1987，PD 分离六项队列深度 + KV 传输速度/延迟）、`QueueMetrics`（L2015，waiting/grammar/paused/retracted 四队列）。每个字段用 `field(metadata={"metric": ("gauge", "...")})` 声明式标注——metrics 导出器按 metadata 自动注册 gauge，消息定义即监控定义。
- **`GetLoadsReqInput`（L2029-2048）**：TokenizerManager → Scheduler。`include` sections 白名单（core/memory/spec/lora/disagg/queues/all）在 `__post_init__` 校验；`dp_rank` 可指定查询某个 DP rank。
- **`GetLoadsReqOutput`（L2051-2095）**：Scheduler → TokenizerManager。核心字段：`num_running_reqs`、`num_waiting_reqs`、`num_used_tokens`、`num_total_tokens`（L2069，= used + 等待队列预填 token，注释说明含 disagg bootstrap/prealloc/transfer 队列，**专用于 DP 负载均衡**）、`token_usage`（L2077，FIXME 注释坦白这实际是所有池的 max 利用率而非纯 KV，改名需走 API 弃用流程）、`cache_hit_rate`、`utilization`，外加五个可选子结构。
- **`WatchLoadUpdateReq`（L2098）**：Scheduler → TokenizerManager 的周期性负载推送（tokenizer_manager.py L1957 处接收并更新缓存）。DP 感知路由器（data_parallel_rank 路由、cache-aware 路由）依赖它做决策。

---

## 7. 权重更新族（L1416-1660）——RL/在线学习热更协议

全部 **TokenizerManager → Scheduler**（Input）/ **Scheduler → TokenizerManager**（Output）方向。这是 SGLang 作为 RL rollout 引擎的核心控制面：

| 消息 | 行号 | 要点 |
|---|---|---|
| `UpdateWeightFromDiskReqInput/Output` | L1416/1443 | 从磁盘路径整装换权重。关键字段：`abort_all_requests`、`is_async`、`keep_pause`（更新后保持暂停，配合 `PauseGenerationReqInput` 组成"pause → update → (optionally flush) → continue"协议）、`recapture_cuda_graph`（换权重后图重捕）、`flush_cache`、`token_step`（RL 训练步号，透传到输出侧 `token_steps`，让训练器知道采样自哪步权重）、`manifest`（张量元数据）。Output 带 `num_paused_requests` |
| `UpdateWeightsFromDistributedReqInput/Output` | L1450/1469 | 经 NCCL process group 收权重（names/dtypes/shapes + group_name），典型的 torch.distributed broadcast 场景 |
| `UpdateWeightsFromTensorReqInput/Output` | L1475/1498 | 序列化张量直传（`serialized_named_tensors: List[Union[str, bytes]]`），JSON 友好；`disable_draft_model` 可选只更大模型 |
| `InitWeightsUpdateGroupReqInput/Output` | L1575/1591 | 建组（master_address/port/rank_offset/world_size/backend="nccl"） |
| `DestroyWeightsUpdateGroupReqInput/Output` | L1597/1602 | 拆组 |
| `InitWeightsSendGroupForRemoteInstanceReqInput/Output` | L1504/1540 | 面向**跨实例**发送方的建组（EPD/多机推拉） |
| `SendWeightsToRemoteInstanceReqInput/Output` | L1546/1556 | 把本实例权重推给远端实例 |
| `UpdateWeightsFromIPCReqInput/Output` | L1522/1534 | 经 ZMQ IPC socket 收权重，L1520 注释言明仅供 Checkpoint Engine（MoonshotAI/checkpoint-engine）使用 |
| `UpdateWeightVersionReqInput` | L1608 | 只切版本号不搬张量（权重已在显存） |
| `GetWeightsByNameReqInput/Output` | L1616/1622 | 按名读权重（`truncate_size` 截断防大响应），验证/调试用 |
| `CheckWeightsReqInput/Output` | L1651/1656 | 权重完整性检查，Output 带 `payload: Dict` |
| `UpdateExpertBackupReq`（L1562）/ `BackupDramReq`（L1567） | — | MoE 专家备份 / DRAM 备份控制（`weight_pointer_map`+`session_id`+`buffer_size`） |

配合 `Pause/Continue` 与 `Release/ResumeMemoryOccupation`，这族消息构成完整的"训练-推理交替"协议栈。

---

## 8. LoRA 族（L1870-1932）

- **`LoadLoRAAdapterReqInput`（L1870-1887）**：TokenizerManager → Scheduler。`lora_name`+`lora_path`+`pinned`（钉在显存防逐出）+`lora_id`（TokenizerManager 分配的 uid）。`to_ref()`（L1881）转换为 `LoRARef` 供调度器侧 LoRA registry 使用——消息层自带 DTO 转换。
- **`UnloadLoRAAdapterReqInput`（L1890-1901）**：卸载，同样带 `to_ref()`。
- **`LoadLoRAAdapterFromTensorsReqInput`（L1904-1920）**：从序列化张量装 LoRA（`config_dict`+`serialized_tensors`），`to_ref()` 里 `lora_path="__tensor__"` 作哨兵值。
- **`LoRAUpdateOutput`（L1923-1927）**：三种操作的统一应答（L1930-1932 直接别名赋值 `LoadLoRAAdapterReqOutput = UnloadLoRAAdapterReqOutput = ... = LoRAUpdateOutput`），带 `loaded_adapters: Dict[str, LoRARef]` 快照。

---

## 9. TokenizerManager 附属服务（HTTP → TokenizerManager，不经 Scheduler）

这组消息发给 TokenizerManager 自己处理（tokenizer 进程本身提供无模型推理的文本加工服务）：

- **`Function`（L1822）/ `Tool`（L1829）**：OpenAI function-calling 的工具描述 DTO。
- **`ParseFunctionCallReq`（L1835-1843）**：把生成文本解析成 tool call；`tool_call_parser` 指定解析器（'llama3'/'qwen25'/'mistral'），不指定则全试。
- **`SeparateReasoningReqInput`（L1846-1849）**：推理/正文分离（如 deepseek-r1 的 `<think>` 解析）。
- **`VertexGenerateReqInput`（L1852-1855）**：Vertex AI 兼容端点的请求转换。
- **`RpcReqInput/Output`（L1858-1867）**：通用 RPC 隧道（method+parameters），TokenizerManager 反射调用——一个逃生舱口避免每加一个轻量功能就定义新消息。
- **`HealthCheckOutput`（L1801）**：健康检查应答。Scheduler event_loop 每轮发（scheduler.py L3119），TokenizerManager 据此更新 scheduler 存活状态；`GenerateReqInput.log_metrics=False` 的 health_generate 请求与之配合（L178-179 注释）。
- **`ActiveRanksOutput`（L1687）**：`status: List[bool]`，DP 各 rank 存活位图。

---

## 10. 命名约定与 import 时自检（L2136-2159）

```python
def _check_all_req_types():
    ...
    is_io_struct = name.endswith("Req") or name.endswith("Input") or name.endswith("Output")
    is_base_req = issubclass(class_type[1], BaseReq) or issubclass(class_type[1], BaseBatchReq)
    if is_io_struct and not is_base_req:
        raise ValueError(...)
    if is_base_req and not is_io_struct:
        raise ValueError(...)
```

`inspect.getmembers` 枚举本模块全部类，双向强制：叫 `*Req/*Input/*Output` 的必须继承基座，继承基座的必须叫这三个后缀之一。最后一行 `_check_all_req_types()`（L2159）**模块级直接调用**——任何破坏约定的改动在 import 瞬间崩掉。约定语义：

- `*Input`：请求方向（下行或跨进程发往服务进程）；
- `*Output`：应答/上行方向；
- `*Req`：无需应答的内部控制命令（如 `AbortReq`、`ProfileReq`）。

---

## 附录 A：全量消息速查表（按方向分组）

表中"方向"列：TM=TokenizerManager，S=Scheduler，D=DetokenizerManager，HTTP=HTTP Server/客户端。这是对正文的机器可对照索引，覆盖文件中全部消息类。

### A.1 请求与生成主干（数据面）

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `GenerateReqInput` | L137 | HTTP→TM | /generate 入口或 Engine.generate() |
| `EmbeddingReqInput` | L828 | HTTP→TM | /encode、/score（rerank）入口 |
| `TokenizedGenerateReqInput` | L719 | TM→S | tokenize+多模态预处理完成后 |
| `BatchTokenizedGenerateReqInput` | L813 | TM→S | 攒批后一次发送多条 |
| `TokenizedEmbeddingReqInput` | L1035 | TM→S | embedding 请求 tokenize 完成后 |
| `BatchTokenizedEmbeddingReqInput` | L1067 | TM→S | embedding 批量化发送 |
| `BatchTokenIDOutput` | L1082 | S→D | 每个 step 输出 copy_to_cpu 后 |
| `BatchStrOutput` | L1154 | D→TM | 增量 detokenize 完成后 |
| `BatchEmbeddingOutput` | L1220 | S→D→TM | embedding 前向完成后（可直接回 TM） |

### A.2 请求生命周期控制

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `AbortReq` | L1673 | TM→S | 客户端断连、超时、/abort 端点 |
| `PauseGenerationReqInput` | L1362 | TM→S | 权重热更前 / 运维暂停（abort/retract/in_place 三模式） |
| `ContinueGenerationReqInput` | L1392 | TM→S | 恢复推理 |
| `OpenSessionReqInput` / `OpenSessionReqOutput` | L1782/L1795 | TM↔TM 侧 session 通道 | open session API |
| `CloseSessionReqInput` | L1790 | 同上 | close session API |
| `BlockReqInput`（+`BlockReqType` L1935） | L1940 | TM→S | BLOCK/UNBLOCK 接客开关 |
| `SlowDownReqInput`/`Output` | L1663/L1668 | TM→S | 混沌测试注入 forward sleep |

### A.3 缓存管理

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `FlushCacheReqInput`/`Output` | L1258/L1263 | TM↔S | /flush_cache，Scheduler 空闲时执行 |
| `ClearHiCacheReqInput`/`Output` | L1248/L1253 | TM↔S | 清 HiCache host/storage 层 |
| `AttachHiCacheStorageReqInput`/`Output` | L1308/L1343 | TM↔S | 运行时挂载存储后端（mooncake 等） |
| `DetachHiCacheStorageReqInput`/`Output` | L1349/L1356 | TM↔S | 运行时卸载存储后端 |
| `AddExternalCorpusReqInput`/`Output` | L1270/L1277 | TM↔S | 注入外部 KV 语料 |
| `RemoveExternalCorpusReqInput`/`Output` | L1285/L1290 | TM↔S | 移除语料 |
| `ListExternalCorporaReqInput`/`Output` | L1296/L1301 | TM↔S | 列出已挂语料 |

### A.4 权重更新族（RL 热更）

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `UpdateWeightFromDiskReqInput`/`Output` | L1416/L1442 | TM→S→TM | /update_weights_from_disk |
| `UpdateWeightsFromDistributedReqInput`/`Output` | L1450/L1469 | TM→S→TM | NCCL 组内广播权重 |
| `UpdateWeightsFromTensorReqInput`/`Output` | L1475/L1498 | TM→S→TM | 序列化张量直传 |
| `UpdateWeightsFromIPCReqInput`/`Output` | L1522/L1534 | TM→S→TM | Checkpoint Engine 专用 |
| `InitWeightsUpdateGroupReqInput`/`Output` | L1575/L1591 | TM→S→TM | 建权重传输 NCCL 组 |
| `DestroyWeightsUpdateGroupReqInput`/`Output` | L1597/L1602 | TM→S→TM | 拆组 |
| `InitWeightsSendGroupForRemoteInstanceReqInput`/`Output` | L1504/L1540 | TM→S→TM | 跨实例发送方建组 |
| `SendWeightsToRemoteInstanceReqInput`/`Output` | L1546/L1556 | TM→S→TM | 推权重到远端实例 |
| `UpdateWeightVersionReqInput` | L1608 | TM→S | 只切版本号 |
| `GetWeightsByNameReqInput`/`Output` | L1616/L1622 | TM↔S | 按名读权重（验证） |
| `CheckWeightsReqInput`/`Output` | L1651/L1656 | TM↔S | 权重完整性检查 |
| `UpdateExpertBackupReq` | L1562 | TM→S | MoE 专家备份 |
| `BackupDramReq` | L1567 | TM→S | DRAM 备份 |
| `ReleaseMemoryOccupationReqInput`/`Output` | L1627/L1634 | TM→S→TM | RL 间隙按 tags 归还显存 |
| `ResumeMemoryOccupationReqInput`/`Output` | L1639/L1646 | TM→S→TM | 恢复显存占用 |

### A.5 观测与运维

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `GetLoadsReqInput`/`GetLoadsReqOutput` | L2029/L2051 | TM↔S | /v1/loads 查询（周期缓存） |
| `WatchLoadUpdateReq` | L2098 | S→TM | Scheduler 周期推送负载（DP 路由依据） |
| `MemoryMetrics`/`SpeculativeMetrics`/`LoRAMetrics`/`DisaggregationMetrics`/`QueueMetrics` | L1945/L1959/L1976/L1987/L2015 | （GetLoadsReqOutput 子结构） | include sections 请求时填充 |
| `HealthCheckOutput` | L1801 | S→TM | event_loop 每轮心跳 |
| `ActiveRanksOutput` | L1687 | S→TM | DP rank 存活位图 |
| `GetInternalStateReq`/`Output`、`SetInternalStateReq`/`Output` | L1692-L1710 | TM↔S | 内部状态读写 |
| `ProfileReqInput`、`ProfileReq`、`ProfileReqOutput`（+`ProfileReqType` L1739） | L1713/L1744/L1760 | HTTP→TM→S→TM | /start_profile /stop_profile |
| `FreezeGCReq` | L1766 | TM→S | 冻结 GC 消长尾 |
| `ConfigureLoggingReq` | L1771 | TM→S | 动态改日志配置 |
| `ExpertDistributionReq`/`Output`（+`ExpertDistributionReqType` L1806） | L1812/L1817 | TM↔S | MoE 专家分布统计开关 |
| `SetInjectDumpMetadataReqInput`/`Output` | L2103/L2108 | TM↔S | dump 元数据注入 |
| `LazyDumpTensorsReqInput`/`Output` | L2113/L2118 | TM↔S | 惰性 dump 张量 |
| `DumperControlReqInput`/`Output` | L2123/L2129 | TM↔S | dumper 通用遥控 |

### A.6 LoRA 与 tokenizer 附属服务

| 类名 | 行号 | 方向 | 触发时机 |
|---|---|---|---|
| `LoadLoRAAdapterReqInput` | L1870 | TM→S | /load_lora_adapter |
| `UnloadLoRAAdapterReqInput` | L1890 | TM→S | /unload_lora_adapter |
| `LoadLoRAAdapterFromTensorsReqInput` | L1904 | TM→S | 张量直传装 LoRA |
| `LoRAUpdateOutput` | L1923 | S→TM | 上述三者统一应答（L1930 别名） |
| `Function`/`Tool` | L1822/L1829 | — | tool 描述 DTO |
| `ParseFunctionCallReq` | L1835 | HTTP→TM | tool call 解析服务 |
| `SeparateReasoningReqInput` | L1846 | HTTP→TM | 推理/正文分离服务 |
| `VertexGenerateReqInput` | L1852 | HTTP→TM | Vertex 兼容端点 |
| `RpcReqInput`/`Output` | L1858/L1864 | HTTP→TM→HTTP | 通用 RPC 隧道 |

## 附录 B：两条关键控制流时序

### B.1 abort 一条流式请求

```
客户端断连
  → HTTP 层 asyncio generator 取消
  → TM: AbortReq(rid=...) 经 send_to_scheduler 下发
  → S: 收到后在 waiting_queue/running_batch 中按 rid 标记
       （若已进入当前 batch，则构造 finished_reason=ABORTED 随正常输出流带出）
  → D: 照常 BatchTokenIDOutput → BatchStrOutput
  → TM: rid 对应 Future 以 AbortReq.finished_reason/abort_message 收尾，
        释放 state，Scheduler 侧 cache_finished_req 归还 KV 槽位
```

### B.2 权重热更（pause → update → continue）

```
TM: UpdateWeightFromDiskReqInput(keep_pause=True, token_step=N, abort_all_requests=...)
  → S: 收到后（若 abort_all）中止/暂停在途请求；is_async=True 时立即回 ack，
       加载线程后台搬权重
  ← S: UpdateWeightFromDiskReqOutput(success, num_paused_requests)
TM: UpdateWeightVersionReqInput(new_version=...)        # 可选：切版本号
TM: ContinueGenerationReqInput(torch_empty_cache=True)  # 恢复推理
  → S: empty_cache 归还瞬态分配 → 解除暂停 → 恢复调度
输出侧: token_steps 携带 N 随 BatchStrOutput 上行，
        训练器据此知道每个样本来自第几步权重
```

## 与其他模块的交互

- **`tokenizer_manager.py`**：本文件最大消费者。构造 `Tokenized*Input`（L1036/L1127 附近）、实现 `parse_function_call`/`separate_reasoning` 服务、接收 `Batch*Output` 与 `WatchLoadUpdateReq`、维护 rid→state 映射。
- **`scheduler.py` + `scheduler_components/`**：event_loop 收发中枢；`batch_result_processor`/`batch_result_generator` 构造 `BatchTokenIDOutput`；权重更新协议的执行端。
- **`detokenizer_manager.py`**：`BatchTokenIDOutput` → `BatchStrOutput/BatchEmbeddingOutput` 的转换器，承担 base64 编码等重活。
- **`schedule_batch.py`**：`BaseFinishReason`（Batch 输出的 finish 语义）、`Modality`（多模态枚举）由它提供；`Req` 对象的 `origin_request` 字段引用着 `TokenizedGenerateReqInput`。
- **`sampling/sampling_params.py`**：`GenerateReqInput.sampling_params` 的 Dict 在 tokenizer 侧解析成 `SamplingParams` 对象后进入 `TokenizedGenerateReqInput`。
- **`observability/req_time_stats.py`**：`time_stats` 三级时间戳（APIServer/DPController/Scheduler）跨进程接力。
- **`lora/lora_registry.py`**：`LoRARef` 与 `to_ref()` 的落点。
- **HTTP 层（`http_server.py` + entrypoints）**：`GenerateReqInput/EmbeddingReqInput` 作为 FastAPI body 模型；`field_validators.py` 提供 `input_ids` 的 C 循环校验器。
- **Engine 模式（`engine.py`）**：离线 `Engine.generate` 直接构造同样的消息对象走 tokenizer→scheduler 管道，与 server 模式共享 100% 协议。

## 关键设计决策

1. **单文件 + import 时自检的消息注册表**：所有跨进程对象集中一处，命名约定机器强制（L2136-2159）。代价是文件膨胀到 2100+ 行，但换来"看一个文件就懂全部协议"的可审计性——分布式系统里协议漂移是最难查的 bug 源，这里把它变成 import error。
2. **胖/瘦两态分离，把归一化复杂度挡在 tokenizer 进程**：`GenerateReqInput` 容忍 7 种输入形态并在入口拍平（parallel sampling 展开、rid 补齐、多模态包装），`TokenizedGenerateReqInput` 之后的世界全是定态类型。Scheduler 因此永远不用处理"用户给了 str 还是 list"这类问题。
3. **控制面与数据面共用一条 ZMQ 信道，一切皆 dataclass**：abort、权重更新、profile 无单独通道，靠 pickle 对象类型分发。简化拓扑（固定三条 PUSH socket），代价是消息必须可 pickle、且要维持类型注册的唯一性（于是有了决策 1）。
4. **输出消息 val/idx 分离 + base64 延迟编码**：logprob 12 字段的全展平布局、`routed_experts` 由 DetokenizerManager 编码（L1187 注释）、`pooled_hidden_states` 单张量堆叠（L1243 注释）——三处都在做同一件事：压缩 ZMQ 上的 pickle 体积、把序列化开销从热路径挪走。
5. **协议内嵌校验**：`AttachHiCacheStorageReqInput.__post_init__` 的枚举检查、`GetLoadsReqInput` 的 sections 白名单、`_validate_rid_uniqueness` 的重复检查——坏消息在**发送端**就被拒绝，而不是在 Scheduler 深处变成诡异状态。
6. **兼容性债务显式管理**：`data_parallel_rank` 的 DeprecationWarning 迁移（L292）、`token_usage` 的 FIXME（L2075）、`AbortReq.rid=""` 的 hack 注释（L1682）——每个历史包袱都有注释锚点，方便后续版本清理。

## 阅读建议

1. **第一遍按本文第 0 节的四条主干流读**：`GenerateReqInput → TokenizedGenerateReqInput → BatchTokenIDOutput → BatchStrOutput`，配合 tokenizer_manager.py 的 `_handle_batch_request` 和 detokenizer_manager.py 的 `handle_loop`，两小时可建立完整心智模型。
2. **重点精读 `normalize_batch_and_arguments` 及其 11 个子方法（L279-617）**：这是 SGLang 对外 API 宽容性的全部秘密，也是改输入格式时最容易踩坑的地方（例如 list 型 logprob 参数与 n>1 的互斥约束在 L544）。
3. **用 `_check_all_req_types`（L2136）当地图**：在 REPL 里 `import` 本模块后 `inspect.getmembers` 枚举，可机器化地导出完整消息清单。
4. **追一条控制流做纵深练习**：推荐权重热更协议 `PauseGenerationReqInput → UpdateWeightFromDiskReqInput → UpdateWeightFromDiskReqOutput → ContinueGenerationReqInput`，串起 scheduler.py 的 pause 状态机与 KVCache flush 逻辑，能同时理解消息层与调度层。
5. **对照测试读**：`test/srt/managers/` 下有针对 normalize 与 `__getitem__` 切分一致性的单测；改本文件任何字段时，注意 `__getitem__` 与 normalize 的互逆性必须同步维护。
6. **注意本文件不含 Scheduler 内部并发原语**：overlap schedule 的两份消息、TP worker 内部通信等在别的模块；这里只有"跨进程"对象——判断标准就是 docstring 那三个进程名。
