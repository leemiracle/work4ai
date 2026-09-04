# 深度解析：`python/sglang/srt/model_executor/forward_batch_info.py`

> 源码: python/sglang/srt/model_executor/forward_batch_info.py @ commit ec075d8bc（1279 行）

## 目录

- [一、职责概述](#一职责概述)
- [二、先看一个具体例子：一次 decode step 的数据](#二先看一个具体例子一次-decode-step-的数据)
- [三、核心类与函数](#三核心类与函数)
  - [3.1 `ForwardMode` 模式枚举](#31-forwardmodeforward-模式枚举l75-186)
  - [3.2 `CaptureHiddenMode`](#32-capturehiddenmodel189-208)
  - [3.3 模块级辅助](#33-模块级辅助l211-270)
  - [3.4 `ForwardBatch` 字段全景](#34-forwardbatch-字段全景l273-449)
  - [3.5 `init_new` 唯一工厂方法](#35-init_new唯一工厂方法l451-674)
  - [3.6 DP attention 填充-截断对](#36-dp-attention-填充-截断对l900-1137)
  - [3.7 多模态与 mrope](#37-多模态与-mrope)
  - [3.8 `PPProxyTensors` 与位置计算内核](#38-ppproxytensors-与位置计算内核l1148-1279)
- [四、与其他模块的交互](#四与其他模块的交互)
- [五、关键设计决策](#五关键设计决策)
- [六、阅读建议](#六阅读建议)

## 一、职责概述

如果说 `ModelRunner` 是推理执行器，那么 `ForwardBatch` 就是执行器的**单次调用参数包**：一次 forward pass 需要的全部输入——输入 token、位置、KV cache 写入位置、请求索引、序列长度、attention backend 上下文、采样信息、多模态输入——全部汇聚在这个 dataclass 里。文件开头的模块 docstring（L14-26）给出了精确的定位：

```
ScheduleBatch -> ForwardBatch

- ScheduleBatch 由 scheduler.py::Scheduler 管理：
  高层调度数据，主要在 CPU 上。
- ForwardBatch 由 model_runner.py::ModelRunner 管理：
  底层张量数据，主要是 GPU 张量。
- 由 ForwardBatch.init_new 直接从 ScheduleBatch 构造。
```

这是 SGLang 批处理体系**两层设计的分界线**：scheduler 世界（CPU、请求生命周期、radix cache、预算控制）与执行世界（GPU、token 级张量、kernel 参数）之间唯一的桥。理解本文件就理解了 SGLang"一次 forward 到底喂给模型什么"。

文件包含五类内容：

1. **`ForwardMode` 枚举**（L75-186）：12 种 forward 模式 + 20 余个谓词方法，是全代码库判断执行路径的"中央交通信号灯"；
2. **`CaptureHiddenMode` 枚举**（L189-208）：隐藏态捕获粒度（投机解码/返回隐藏态用）；
3. **`ForwardBatch` dataclass**（L273-1141）：约 70 个字段，按来源分 8 组注释（这是全文件最值得精读的组织结构）；
4. **构造与变换方法**：唯一工厂 `init_new`（L451）、DP attention 的 `prepare_mlp_sync_batch`/`post_forward_mlp_sync_batch` 填充-截断对、通用 `_pad_inputs_to_size`；
5. **位置计算工具**（L1178-1279）：`compute_position`（Triton fused / torch 双实现）、`clamp_position`（CUDA JIT kernel / native 双实现）、`PPProxyTensors`、`NgramEmbeddingInfo`。

一个必须先澄清的事实：任务描述中提到的 "capture_for_ 系列静态构造方法" 是 vLLM `MetadataBuilder` 风格的命名；**SGLang 此版本中不存在 `capture_for_*` 方法族**。对应角色由唯一的 classmethod 工厂 **`ForwardBatch.init_new`（L451-674）**承担；而 CUDA Graph 捕获所需的静态 ForwardBatch 并不在本文件构造——它由 `cuda_graph_runner.py` 的 `DecodeInputBuffers` 供数、`ModelRunner._dummy_run`（model_runner.py L2661-2692）手工组装。下文按真实代码解析。

## 二、先看一个具体例子：一次 decode step 的数据

假设 batch 里有两个请求，分别已生成 10 和 7 个 token（含 prompt），本步 decode 各生成 1 个新 token。进入 `ModelRunner.forward` 时 ForwardBatch 大致长这样：

```
forward_mode      = ForwardMode.DECODE
batch_size        = 2
input_ids         = tensor([9231, 512])          # 上一步采样出的 token id，shape [2]
positions         = tensor([9, 6])               # RoPE 位置 = seq_lens - 1（clamp 过）
seq_lens          = tensor([10, 7])              # 注意力要看的 KV 长度
seq_lens_cpu      = tensor([10, 7])              # CPU 镜像（省 D2H）
req_pool_indices  = tensor([12, 87])             # 在 req_to_token_pool 中的行号
out_cache_loc     = tensor([55123, 80117])       # 新 KV 写入 token_to_kv_pool 的槽位
seq_lens_sum      = 17
extend_seq_lens   = None                         # decode 没有 extend 字段（L480-481 置 None）
extend_prefix_lens= None
capture_hidden_mode = CaptureHiddenMode.NULL
sampling_info     = SamplingBatchInfo(temperatures, top_p, ...)
...
```

attention backend 随后在 `init_forward_metadata(forward_batch)` 中用 `req_pool_indices` + `seq_lens` 去 `req_to_token_pool` 查每请求的 KV 槽位表，生成 decode kernel 的 plan；模型 forward 完把新 KV 写到 `out_cache_loc` 指向的槽。一个 batch 的"读哪里、算什么、写哪里"三件事，分别锚定在 `req_pool_indices` / `input_ids+positions` / `out_cache_loc` 上。

## 三、核心类与函数

### 3.1 `ForwardMode`：forward 模式枚举（L75-186）

```python
class ForwardMode(IntEnum):
    EXTEND = auto()          # 序列扩展：前缀 KV 已算好的增量计算，俗称 prefill   L78
    DECODE = auto()          # 每请求生成一个 token                              L80
    MIXED = auto()           # chunked prefill 时同批含 EXTEND 和 DECODE          L82
    IDLE = auto()            # 本 worker 无请求（DP attention 下部分 rank 空转）   L84
    TARGET_VERIFY = auto()   # 投机解码：target 模型验证草稿 batch                 L87
    DRAFT_EXTEND = auto()    # 投机解码：draft 模型对 batch 做 extend              L89
    DRAFT_EXTEND_V2 = auto() # eagle v2：固定 shape logits 输出                    L91
    PREBUILT = auto()        # PD 分离 decode worker：KV 已就位直接开 decode       L95
    SPLIT_PREFILL = auto()   # PD 复用：prefill 按层分段                          L98
    DLLM_EXTEND = auto()     # diffusion LLM 的 extend                            L101
```

比枚举值本身更重要的是**谓词方法族**——它们把"模式属于哪条执行路径"的判断集中在一处，全库（scheduler、attention backend、logits processor、cuda graph runner）都调用这些谓词而不是手写比较：

| 谓词 | 行号 | 判定集合 | 典型用途 |
|---|---|---|---|
| `is_extend()` | L106-115 | EXTEND, MIXED, DRAFT_EXTEND, (v2 可选), TARGET_VERIFY, SPLIT_PREFILL, DLLM_EXTEND | "本次 forward 是批量 token 计算"总判断 |
| `is_prefill()` | L103-104 | 即 `is_extend` | 语义别名 |
| `is_decode()` / `is_mixed()` / `is_idle()` | L128-135 | 单值 | 基础判定 |
| `is_decode_or_idle()` | L137-138 | DECODE, IDLE | `init_new` 决定 extend_* 字段是否置 None（L480-481） |
| `is_target_verify()` | L140-141 | 单值 | spec verify 路径 |
| `is_draft_extend(include_v2)` | L143-146 | DRAFT_EXTEND (v2 可选) | spec draft 路径 |
| `is_draft_extend_v2()` | L148-150 | 单值 | eagle v2 固定 shape logits |
| `is_extend_or_draft_extend_or_mixed()` | L152-159 | EXTEND, DRAFT_EXTEND, MIXED, SPLIT_PREFILL, (v2 可选) | logits processor 取最后 token 位置 |
| `is_cuda_graph()` | L161-167 | **DECODE, TARGET_VERIFY, IDLE, DLLM_EXTEND** | 整图 CUDA Graph 可捕获模式白名单 |
| `is_cpu_graph()` | L169-170 | DECODE | CPU graph 只覆盖 decode |
| `is_split_prefill()` / `is_prebuilt()` / `is_dllm_extend()` | L172-186 | 单值 | 特殊路径 |
| `is_context_parallel_extend(v2)` | L117-126 | EXTEND, MIXED, (v2 可选) | CP（上下文并行）prefill 判定 |
| `is_extend_without_speculative()` | L175-180 | extend 且非 verify/draft | 排除投机解码的"纯"extend |

谓词真值速查（√ 属于，— 不属于）：

| 模式 | is_extend | is_decode | is_idle | is_cuda_graph | 投机解码族 |
|---|---|---|---|---|---|
| EXTEND | √ | — | — | — | — |
| DECODE | — | √ | — | √ | — |
| MIXED | √ | — | — | — | — |
| IDLE | — | — | √ | √ | — |
| TARGET_VERIFY | √ | — | — | √ | √ |
| DRAFT_EXTEND | √ | — | — | — | √ |
| DRAFT_EXTEND_V2 | 默认—（opt-in） | — | — | — | √ |
| PREBUILT | — | — | — | — | — |
| SPLIT_PREFILL | √ | — | — | — | — |
| DLLM_EXTEND | √ | — | — | √ | — |

注意 `TARGET_VERIFY` 同时属于 `is_extend()` 和 `is_cuda_graph()`——验证步一次算多个 draft token（批量 token 形态）但 batch 形状固定（可捕获），两个看似矛盾的属性在这里统一。`DRAFT_EXTEND_V2` 到处用 `include_draft_extend_v2` 开关参数（L103/106/143/152），因为 v2 是后加模式，旧调用方语义上"不想看见它"，新调用方显式 opt-in——枚举演进兼容的实用模式。

### 3.2 `CaptureHiddenMode`（L189-208）

```python
@total_ordering
class CaptureHiddenMode(IntEnum):
    NULL = 0   # 不捕获          L192
    LAST = 1   # 只捕获最后 token L194
    FULL = 2   # 捕获全部 token   L196
```

`need_capture()/is_full()/is_last()` 三谓词（L198-205）；`__lt__`（L207-208）+ `@total_ordering` 使其可比较、可取 max——scheduler 合并 batch 时取各请求 capture 需求的最大值。`LAST` 供 eagle draft（只要最后一个位置的隐藏态），`FULL` 供 eagle3 aux hidden 与 `return_hidden_states`。

### 3.3 模块级辅助（L211-270）

- **`compute_local_num_token_non_padded`（L211-228）**：把 DP 组内的全局非 padding token 数裁到**本 attention-TP rank 的局部值**：

  ```python
  tokens_per_rank = num_tokens_per_dp // attn_tp_size
  return torch.clamp(global_num_token_non_padded - tokens_per_rank * attn_tp_rank,
                     0, tokens_per_rank)
  ```

  EP>1 时（`enable_num_token_non_padded()` L1144-1145 返回 `get_moe_expert_parallel_world_size() > 1`）MoE dispatch 需要真实 token 数以跳过 padding，避免给专家喂假 token 污染负载统计。
- **`NgramEmbeddingInfo`（L231-270）**：LongCat 模型 n-gram embedding 的 token 表元数据：`token_table`（全局共享，shape 与 req_to_token 池对齐）+ 输入侧 `column_starts/req_lens` + 输出侧 `out_column_starts/out_req_lens`。`create` 类工厂（L241-261）预分配四组 `batch_size` 形状 int32 缓冲；`slice(bs)`（L263-270）返回裁剪视图，供 CUDA Graph 按捕获 batch size 复用。

### 3.4 `ForwardBatch` 字段全景（L273-449）

`@dataclass class ForwardBatch(ForwardBatchDeepSeekMHAMixin)`（L273-274）——继承 DeepSeek MHA chunked prefix cache 的 mixin（`forward_batch_deepseek_mha_mixin.py`），把该模型族特有的 chunked KV 索引准备逻辑隔离在外。字段分组注释（L277-449）是官方给的字段分类学，逐组解析：

**① Required core inputs（L277-291）——必填、从 ScheduleBatch 借用**

| 字段 | 行号 | 含义 |
|---|---|---|
| `forward_mode: ForwardMode` | L279 | 本次 forward 模式 |
| `batch_size: int` | L281 | 请求数 |
| `input_ids: torch.Tensor` | L283 | 展平的输入 token id（extend 时长度=Σ extend_len；decode 时=bs） |
| `req_pool_indices: torch.Tensor` | L285 | 每请求在 `req_to_token_pool` 中的行索引——attention 据此查"该请求每个 token 的 KV 在哪个槽" |
| `seq_lens: torch.Tensor` | L287 | 每请求当前序列长度 |
| `out_cache_loc: torch.Tensor` | L289 | **本次 forward 产出的 token 要写入 token_to_kv_pool 的槽位索引**（与 input_ids 对齐） |
| `seq_lens_sum: int` | L291 | Σ seq_lens |

`req_pool_indices`（读 KV 布局）与 `out_cache_loc`（写 KV 槽位）一读一写，构成 KV cache 管理的双锚点。

**② Borrowed GPU tensors（L293-322）**：

| 字段 | 行号 | 含义 |
|---|---|---|
| `orig_seq_lens` | L298 | chunk 前的原始长度（Qwen-1M 超长上下文相关） |
| `mamba_track_indices` | L301 | mamba 状态槽索引，[b] int64 |
| `mamba_track_mask` | L303 | 是否需要跟踪 mamba 状态，[b] bool |
| `mamba_track_seqlens` | L305 | masked 跟踪时的 seqlen，仅 prefill |
| `mamba_cow_src_indices` / `mamba_cow_dst_indices` | L307-308 | 延迟执行的 copy-on-write 源/目的对（在 forward stream 上执行） |
| `mamba_clear_indices` | L309 | 延迟执行的清零槽 |
| `input_embeds` | L312 | 直接注入输入 embedding（跳过 embedding 查表） |
| `replace_embeds` / `replace_positions` | L314-315 | 指定位置的 embedding 覆写（稀疏替换） |
| `token_type_ids` | L318 | cross-encoder 模型的 token 类型 |
| `encoder_lens` / `encoder_out_cache_loc` | L321-322 | encoder-decoder 的编码器长度 / 编码器 KV 写槽 |

L294-296 的 FIXME 坦言这些当前是**引用别名**（aliased by reference），未来要在边界克隆为 ForwardBatch 自有副本做流隔离——"借用 vs 拥有"是本类最核心也最微妙的语义。

**③ Borrowed config/flags（L324-343）**：

| 字段 | 行号 | 含义 |
|---|---|---|
| `return_logprob` | L326 | 是否要 logprob |
| `is_prefill_only` | L328 | 纯 prefill 批（不需生成） |
| `spec_algorithm` | L329 | 投机解码算法 |
| `dimensions` | L331 | matryoshka embedding 维度 |
| `return_pooled_hidden_states` | L333 | 返回池化隐藏态（pre-head 输出） |
| `is_extend_in_batch` / `all_extend_in_batch` | L336-338 | DP attention：批内是否含 extend（后者为下游 fork 保留的镜像） |
| `can_run_dp_cuda_graph` | L339 | DP CUDA Graph 资格 |
| `global_forward_mode` | L340 | 全局（跨 DP rank 统一）的模式 |
| `tbo_split_seq_index` | L343 | two-batch overlap 的序列切分点 |

**④ Borrowed host metadata（L345-361）**：`seq_lens_cpu`（GPU seq_lens 的 CPU 镜像——DP 判定与 cudagraph 路径省一次 D2H）、`top_logprobs_nums`/`token_ids_logprobs`（logprob 需求）、`mm_inputs: List[MultimodalInputs]`、`encoder_cached`/`encoder_lens_cpu`、`multi_item_delimiter_indices`（多 item 打分如 reranker 的分隔索引，CPU 张量每请求一份）。

**⑤ Compound（L363-367）**：`sampling_info: SamplingBatchInfo`（自带设备张量的采样参数包）、`spec_info: SpecInput`（投机解码输入：draft token、custom mask、hidden states、retrieve 树结构…）。

**⑥ Derived from SB.reqs（L369-373）**：`lora_ids`、`rids`——`init_new` 时从请求对象列表现抽（L558-559）。

**⑦ Resolved one-shot overrides（L375-378）**：`capture_hidden_mode`、`return_hidden_states_before_norm`——**"消费即重置"契约**（见 3.5 第①幕）。

**⑧ Forward-derived / Runtime-filled（L380-449）**——ForwardBatch 自己算出或运行期回填：

| 子组 | 字段 | 行号 |
|---|---|---|
| 位置 | `positions` | L382 |
| extend 族 | `extend_num_tokens/extend_seq_lens/extend_prefix_lens/extend_start_loc(+_cpu)/extend_logprob_start_lens_cpu/extend_input_logprob_token_ids_gpu` | L384-392 |
| DP MLP 同步 | `original_global_num_tokens_cpu/global_num_tokens_cpu/global_num_tokens_gpu`、`global_num_tokens_for_logprob_cpu/gpu`（**graph 捕获时必须为 None**，L398） | L394-400 |
| padding | `num_token_non_padded(_cpu)`、`padded_static_len` | L402-404, L436 |
| logits 后处理缓冲 | `next_token_logits_buffer/temperature/top_p` | L407-410 |
| split prefill 中间态 | `hidden_states/residual/model_specific_states/split_index` | L412-418 |
| 多模态 | `mm_input_embeds` | L421 |
| encoder-decoder | `cross_attention_custom_mask` | L424 |
| DP padding | `dp_padding_mode/dp_local_start_pos/dp_local_num_tokens/global_dp_buffer_len` | L427-433 |
| Qwen2-VL | `mrope_positions` | L439 |
| TBO | `tbo_parent_token_range/tbo_padded_len/tbo_children` | L442-444 |
| CP | `attn_cp_metadata: ContextParallelMetadata` | L446 |
| n-gram | `ngram_embedding_info` | L449 |

**attention backend 上下文如何进入 forward？** 答案是"不在字段里"：各 backend 的 `init_forward_metadata(forward_batch)` 在 `ModelRunner.forward_decode/extend`（model_runner.py L3028/L3109）中消费 ForwardBatch，把产出（plan、页表、workspaces）存在 **backend 自己身上**，并通过 `forward_context`（ForwardContext）向模型层发布。ForwardBatch 只承载"跨模块都要用的通用张量"，backend 私有元数据不进 dataclass——这是刻意的边界。

### 3.5 `init_new`：唯一工厂方法（L451-674）

`@classmethod init_new(cls, batch: ScheduleBatch, model_runner: ModelRunner)`，六幕结构：

```python
# ① 消费 one-shot 覆盖并重置（L457-465）
capture_hidden_mode = batch.capture_hidden_mode
batch.capture_hidden_mode = None                 # 消费即重置
seq_lens_cpu_cache = batch.seq_lens_cpu_cache
batch.seq_lens_cpu_cache = None
return_hidden_states_before_norm = batch.return_hidden_states_before_norm
batch.return_hidden_states_before_norm = False

# ② capture_hidden_mode 默认推导（L469-477）
if capture_hidden_mode is None:
    if batch.return_hidden_states:      capture_hidden_mode = CaptureHiddenMode.FULL
    elif batch.spec_info is not None:   capture_hidden_mode = spec_info.capture_hidden_mode
    else:                               capture_hidden_mode = CaptureHiddenMode.NULL
```

```
③ 模式相关字段裁剪（L479-485）
   decode/idle：extend_seq_lens = extend_prefix_lens = extend_logprob_start_lens = None
   否则从 SB.extend_lens / SB.prefix_lens 借
④ grammar 镜像 + 陈旧缓存防护（L489-512）
   - SB.has_grammar 时把 req.grammar 填进 sampling_info.grammars（镜像自历史上的
     ScheduleBatch.get_model_worker_batch，L487-493）
   - seq_lens_cpu_cache.shape 必须 == seq_lens.shape，assert 失败即"stale override"——
     防 filter/merge_batch 后忘刷新导致 DP/cudagraph 拿错 CPU 镜像（L498-507）
   - seq_lens_sum 惰性补算（L511-512）
⑤ dataclass 构造（L514-563）
   一次性传入 ①-⑧ 组全部字段；GPU 张量搬运 extend_input_logprob_token_ids（L567-570）
⑥ 派生字段计算（L572-674）
```

⑥ 的分步骤（这是本方法真正的计算重心）：

```
6a. num_token_non_padded（EP>1 时上 GPU，L572-577）
6b. MLP sync 的 global_num_tokens：spec_info 存在时先取
    get_spec_adjusted_global_num_tokens(batch) 调整（L580-602）——
    target_verify 每请求占 draft_token_num 个 token，各 DP rank 的对齐数要重算
6c. IDLE 提前返回：positions = torch.empty((0,))（L604-606）
6d. positions 三来源（L608-651）：
    - dllm_config → 按 req.dllm_block_offset × block_size 展开整块位置；
      dtype 在 HIP/NPU 上用 int64（rotary kernel 兼容，L611-612）
    - spec_info.positions 存在 → 直接复用（草稿位置由 spec worker 决定）
    - decode/target_verify → positions = clamp_position(seq_lens)（L628-630）
    - extend → extend_seq_lens/extend_prefix_lens 转 int32 上 GPU（non_blocking）
               + compute_position() 算 positions 与 extend_start_loc（L641-646）
               + 保留各 _cpu 列表副本（L649-651）
6e. ngram embedding 信息（L653-654 → _init_ngram_embedding_info L747-758：
    decode 用 (seq_lens-1, 1)，extend 用 (extend_prefix_lens, extend_seq_lens)）
6f. mrope 三维位置（spec 版 L760-810、普通版 L825-883，见 3.7）
6g. LoRA：非 overlap 加载模式下 fetch_new_loras + prepare_lora_batch（L665-672）
```

所有 H2D 搬运都用 `.to(device, non_blocking=True)` 配合 pinned memory——这是 overlap schedule（CPU 调度与 GPU 前向流水线化）的性能前提。

### 3.6 DP attention 填充-截断对（L900-1137）

**`prepare_mlp_sync_batch(model_runner)`（L900-995）**——DP attention 开启时（`ModelRunner._forward_raw` 在 graph 未命中时调用，model_runner.py L3311-3312），把各 DP rank 不同的 batch 填充到可集合通信的统一形状：

1. 两级 `ceil_align`：先对齐 `attn_tp_size`（MLP 后走 reduce-scatter，L910-913），再对齐 `attn_cp_size*2`（CP 负载均衡成 2×CP 块，L917-919）；
2. `DpPaddingMode.get_dp_padding_mode(...)`（L921-923）选 **max_len 模式**（all_gather_into_tensor，各 rank 等长，buffer_len = max×N，L926-933）或 **sum 模式**（buffer_len = Σ，L934-935）；
3. `set_dp_buffer_len(...)` + `set_is_extend_in_batch(...)` 写入 dp_attention 模块全局状态（L943-946）——模型层 MLP 通信算子从这里读 buffer 长度；
4. **decode→EXTEND 模式改写**（L950-967）：

   ```python
   if self.is_extend_in_batch and dp_padding_mode.is_max_len():
       setattr(self, "_original_forward_mode", self.forward_mode)   # 备份
       self.forward_mode = ForwardMode.EXTEND                        # 改写
       self.extend_num_tokens = bs
       self.extend_seq_lens = torch.full_like(self.seq_lens, 1)      # 伪造每请求 1 token
       self.extend_prefix_lens = self.seq_lens - 1
       self.extend_start_loc = torch.arange(bs, dtype=torch.int32, ...)
   ```

   本批 mixed 时 decode 步也必须走 extend kernel 路径（同一 kernel 才能处理"有的请求 1 token、有的请求 N token"的混合批）；否则按 `num_tokens`（spec 场景除以 `num_tokens_per_req`）重设 batch_size；
5. `_pad_inputs_to_size`（见下）统一填充；
6. `TboForwardBatchPreparer.prepare`（L985-987）处理 two-batch overlap 子批拆分，子批再各自 pad（L991-995）。

一个 worked example（DP=2、attn_tp=1、无 CP、max_len 模式）：

```
rank0: extend 批 100 token / rank1: extend 批 37 token
→ 不对齐 attn_tp（=1 无操作）→ max_len 模式
→ global_num_tokens = [100, 100]，buffer_len = 200
→ rank0 不用 pad；rank1 input_ids/out_cache_loc/positions 右侧补 63 个 0
→ MLP all_gather 后 hidden_states [200, d]，reduce-scatter 各取一半
→ post_forward_mlp_sync_batch 截回 rank1 真实的 37 行 logits
```

**`_pad_inputs_to_size(model_runner, num_tokens, bs)`（L997-1068）**——通用右填充：

| 填充目标 | 字段 |
|---|---|
| 到 num_tokens | `input_ids`、`out_cache_loc`、`positions`、spec_info 的 `hidden_states` |
| 到 bs | `req_pool_indices`、`seq_lens`、`encoder_lens`、`mamba_track_indices/mask/seqlens`、`extend_seq_lens` |
| 补 None/值 | `lora_ids` 补 None（L1001）、`seq_lens_sum` 加填充贡献（L1006-1008）、`mrope_positions` 补零列（L1032-1041） |

两个精妙点：

- **seq_lens 的填充值不是 0** 而是 `model_runner.attn_backend.get_cuda_graph_seq_len_fill_value()`（L1003-1005）——不同 backend 对"假序列长度"有不同要求（有的要 1 避免 0 长度 kernel 崩溃），语义决策**委托给 backend**；
- spec_info 为 draft 输入时，先备份 `out_cache_loc`/`hidden_states` 到 `output_cache_loc_backup`/`hidden_states_backup`（L1049-1050），再逐字段 getattr 防护式填充——`EagleDraftInput` 与 `EagleDraftExtendInput` 各持有不相交字段子集（L1051-1068 注释明示）。

**`post_forward_mlp_sync_batch(logits_output)`（L1083-1137）**——forward 后的对称截断：恢复 `_original_forward_mode`/`_original_batch_size`（L1085-1086）；按模式截断 logits：

| 模式 | 截断长度 | 行号 |
|---|---|---|
| decode（draft） | `hidden_states_backup.shape[0]`，并恢复 positions/seq_lens/req_pool_indices | L1090-1100 |
| target_verify | `bs × spec_info.draft_token_num` | L1101-1106 |
| draft_extend / draft_extend_v2 | `bs`（v2 再乘 `num_tokens_per_req`） | L1107-1117 |
| extend / idle | `bs` | L1118-1120 |
| 无 spec 的 decode/idle | `bs` | L1127-1130 |
| 无 spec 的 extend | `seq_lens_sum` | L1131-1137 |

最后恢复两个备份（L1122-1125）。**填充与截断必须严格配对，否则 logits 错位**——这是 DP attention 排查数值问题的第一现场。

**`prepare_attn_tp_scatter_input`（L1070-1081）**：非 DP 场景下若 attn-TP 使用 input scatter（`attn_tp_context.use_input_scattered(self)`），把 extend token 数对齐到 `tensor_model_parallel_world_size` 的倍数再填充。

### 3.7 多模态与 mrope

- `merge_mm_inputs`（L693-714）：批内多个 `MultimodalInputs` 合并为一个；用 `valid_inputs[0].__class__(mm_items=[])` 绕开循环导入（L706-708 的 TODO 问"is it expensive?"）；`contains_image/audio/video/mm_inputs` 四谓词（L716-745）；
- `_compute_mrope_positions`（L825-883）普通路径，逐请求处理：
  - decode：文本请求填 `(3,1)` 的 `seq_len-1`；多模态请求用 `mm_input.mrope_position_delta_repeated_cache` 缓存展开（`_expand_mrope_from_input` L812-823，**刻意在 CPU 上算避免小 kernel 风暴**，L817 注释）；`rl_on_policy_target` 配置下强制按纯文本处理（L834-836）；
  - extend：多模态请求直接切 `mm_input.mrope_positions[:, prefix : prefix+len]`，空则退回 delta 展开（L870-877）；
- `compute_spec_mrope_positions`（L760-810）投机路径：draft_extend 按 `extend_lens` 切分 spec positions 逐段加 delta（TODO 注明"暂不支持批量 delta"）；target_verify/draft_decode 整批向量化——**纯文本批直接走全零 delta 张量，避免一次 D2H 同步**（L792-795 注释：SpecV2 text-only 批的优化）。

### 3.8 `PPProxyTensors` 与位置计算内核（L1148-1279）

- **`PPProxyTensors`（L1148-1175）**：PP 各 rank 间传递中间激活的 dict 包装（改自 vLLM `IntermediateTensors`，L1149 源注释）。手写 `__init__` 的注释（L1153-1156）解释了为何不用 dataclass：Dynamo/torch.compile 需要知道类来自本文件，dataclass 会用字符串求值生成 `__init__` 丢失源文件信息。支持 str 取值与 slice 批量切片（L1159-1163）。
- **`compute_position`（L1178-1194）**：extend 模式位置计算总入口，按 `support_triton(attn_backend)` 分派：
  - `compute_position_triton`（L1197-1220）+ `compute_position_kernel`（L1223-1250）：fused 版，每个 program 处理一个请求。kernel 内部：读 `prefix_len/seq_len` → **O(pid) 串行前缀和**求 `cumsum_start`（L1238-1240，注释自认大 bs 下慢）→ 按 `BLOCK_SIZE=512` 分块写 `positions[cumsum_start+offset] = prefix_len+offset`（mask=offset<seq_len）→ 写 `extend_start_loc[pid]=cumsum_start`。一次 kernel 同时产出两个张量，这就是"fused"的含义；
  - `compute_position_torch`（L1253-1267）：`cat([arange(prefix, prefix+len) for ...])` 朴素版 + `cumsum` 求 start_loc。
- **`clamp_position`（L1270-1279）**：decode 位置 = `clamp(seq_lens-1, min=0)`（防 0 长序列出负）；CUDA/HIP 走 `sglang.jit_kernel.clamp_position_cuda`（L1274-1277），其余平台 `_clamp_position_native`（L1270-1271）。decode 每步都调用，值得一个专用 kernel。

## 四、与其他模块的交互

| 模块 | 交互点 |
|---|---|
| `managers/schedule_batch.py` | `init_new` 的唯一输入；one-shot override 契约（capture_hidden_mode 等）双向读写 SB 字段 |
| `model_executor/model_runner.py` | `init_new(batch, model_runner)` 读 device/LoRA/ngram/mrope/dllm 配置；`_forward_raw` 调 `prepare_mlp_sync_batch`；`_dummy_run` 手工构造本类；`sample` 用 positions/seq_lens |
| `layers/attention/*`（各 backend） | backend 消费 ForwardBatch 生成自己的 forward_metadata；`get_cuda_graph_seq_len_fill_value()` 反向决定填充语义；`is_cuda_graph()` 决定捕获资格 |
| `model_executor/cuda_graph_runner.py` | graph replay 时 `replay_prepare` 把静态缓冲值拷进 ForwardBatch 引用的张量；`NgramEmbeddingInfo.slice(bs)` 按捕获 bs 裁剪 |
| `layers/dp_attention.py` | `set_dp_buffer_len`/`set_is_extend_in_batch` 全局状态；`DpPaddingMode`；`get_attention_tp_size/rank`、`get_attention_dp_rank` 用于填充计算 |
| `batch_overlap/two_batch_overlap.py` | `TboForwardBatchPreparer.prepare` 生成 `tbo_children`；`can_run_tbo`、`tbo_parent_token_range/tbo_padded_len` |
| `layers/logits_processor.py` | 消费 `capture_hidden_mode`/`next_token_logits_buffer`；`dp_local_start_pos/num_tokens` 在 `LogitsMetadata.from_forward_batch` 重算（L429-431 注释） |
| `sampling/sampling_batch_info.py` | `sampling_info` 复合字段；grammar 镜像填充在 `init_new` 完成 |
| `speculative/spec_info.py`（Eagle/DFlash/Ngram） | `spec_info` 复合字段；`get_spec_adjusted_global_num_tokens`；draft 输入的防护式填充 |
| `layers/utils/cp_utils.py` | `attn_cp_metadata: ContextParallelMetadata`（CP prefill） |
| `sglang.jit_kernel`（clamp_position）+ triton | 位置计算的两条 kernel 依赖 |
| `forward_batch_deepseek_mha_mixin.py` | 父类 mixin：DeepSeek MHA chunked prefix cache 的 KV 索引准备 |

## 五、关键设计决策

1. **"借用视图 + 分组注释"而非深拷贝**：约 70 个字段中绝大多数是 ScheduleBatch 张量的引用别名（L293-296 FIXME 已计划改为边界克隆）。收益是零拷贝、低延迟；代价是**生命周期耦合**——SB 被复用/合并/过滤时 ForwardBatch 会跟着变。字段分 8 组注释（Required/Borrowed-GPU/Borrowed-flag/Borrowed-host/Compound/Derived-from-reqs/One-shot/Forward-derived）等于在类型系统缺失处用文档维护所有权语义。
2. **ForwardMode 谓词集中制**：模式的业务含义（"算不算 extend"、"能不能进 CUDA Graph"）全部收敛为枚举方法（L103-186），12 种模式 × 20 个谓词构成语义矩阵。新增模式（如 DRAFT_EXTEND_V2、DLLM_EXTEND）只需改这一处全库自动跟进——代价是每个谓词要显式决定新模式的归属（`include_draft_extend_v2` 参数就是这种显式化的产物）。
3. **one-shot override 的"消费即重置"契约**（L457-465, L375-378）：ScheduleBatch 上可放 per-forward 覆盖（capture_hidden_mode/seq_lens_cpu_cache/return_hidden_states_before_norm），`init_new` 读取后立刻清空。用注释声明的契约（无运行时强制）换取调度器灵活注入能力，配套 shape assert（L503-506）是防陈旧覆盖的最低保险。
4. **DP attention 的填充/截断对称设计**：`prepare_mlp_sync_batch` 改写 forward_mode（decode→EXTEND 伪造）+ `_pad_inputs_to_size` 填充 + `post_forward_mlp_sync_batch` 恢复截断，三者构成事务。填充值语义下放给 attention backend（`get_cuda_graph_seq_len_fill_value`），把"什么填充值对 kernel 安全"这一 backend 私有知识留在 backend 内。
5. **位置计算的性能分级**：decode 的 `clamp_position` 有专用 CUDA JIT kernel；extend 的 `compute_position` 有 Triton fused 实现（一次 kernel 同时产出 positions 和 extend_start_loc）并以 torch 版兜底不支持 Triton 的平台；mrope 的 delta 展开刻意放在 CPU（L817 注释"avoid frequent small kernels"）并用 `mrope_position_delta_repeated_cache` 缓存——每个热路径都有"kernel 化/缓存/CPU 化"的明确取舍记录。
6. **backend 上下文与通用数据的分界**：ForwardBatch 只装"任何 backend 都要用的通用张量"；backend 私有 plan/metadata 存 backend 自身、经 forward_context 发布。这避免了 dataclass 被十几家 backend 的字段撑爆，也让 backend 可以自由重组自己的元数据结构。

## 六、阅读建议

1. **先读三段**：模块 docstring（L14-26，两层设计的定义）→ `ForwardMode`（L75-186，谓词矩阵）→ `ForwardBatch` 字段分组注释（L277-449）。这三段读完，SGLang 的 batch 数据模型已在脑中成型，再读 `init_new` 只是验证理解。
2. **对着调用方读**：`init_new` 只有两个高频调用点——`ScheduleBatch.get_model_worker_batch` 之后（正常路径）与 `ModelRunner._dummy_run`（graph 捕获路径，绕过 init_new 手工构造）。对照后者可以看清"graph 静态捕获需要哪些字段、可以丢掉哪些"（答案：CPU 镜像与 logprob 相关字段大多可缺省，`global_num_tokens_for_logprob` 捕获时必须为 None，L398）。
3. **调试 DP attention 数值问题时**：沿 `prepare_mlp_sync_batch`（L900）→ `_pad_inputs_to_size`（L997）→ `post_forward_mlp_sync_batch`（L1083）三点一线检查：填充长度与截断长度是否互逆、`_original_forward_mode` 是否被恢复、spec_info 的备份是否回填（L1122-1125）。logits 多出/少了 padding 行几乎都在这条链上。
4. **改字段时**：新字段必须回答三个问题——属于 8 个分组中的哪一组（决定默认值与注释位置）？DP 填充时是否需要进 `_pad_inputs_to_size`？CUDA Graph 捕获时它应保持 None 还是需要静态缓冲（对照 L398 的注释）？
5. **延伸阅读**：`forward_batch_deepseek_mha_mixin.py`（chunked prefix cache 的 KV 索引如何准备）；`layers/dp_attention.py`（`set_dp_buffer_len` 的消费侧）；`batch_overlap/two_batch_overlap.py`（tbo_children 的生成与 merge）；`managers/schedule_batch.py`（借用字段的源头，理解"借用"的完整生命周期）；`model_executor/model_runner.py` 解析篇（本文件的两个主要消费者视角）。

## 附录：本文件方法级索引

**枚举**：`ForwardMode` L75（值 L78-101；谓词 L103-186）· `CaptureHiddenMode` L189

**模块级函数**：`compute_local_num_token_non_padded` L211 · `enable_num_token_non_padded` L1144 · `PPProxyTensors` L1148 · `compute_position` L1178 · `compute_position_triton` L1197 · `compute_position_kernel`（triton.jit）L1223 · `compute_position_torch` L1253 · `_clamp_position_native` L1270 · `clamp_position`（平台分派）L1274-1279

**`NgramEmbeddingInfo`**：`create` L242 · `slice` L263

**`ForwardBatch`**（含 mixin 继承）：
- 构造：`init_new` L451
- DP/TP 同步：`adjust_num_token_non_padded_for_attn_tp` L676 · `prepare_mlp_sync_batch` L900 · `_pad_inputs_to_size` L997 · `prepare_attn_tp_scatter_input` L1070 · `post_forward_mlp_sync_batch` L1083
- 多模态：`merge_mm_inputs` L693 · `contains_image_inputs` L716 · `contains_audio_inputs` L724 · `contains_video_inputs` L732 · `contains_mm_inputs` L740
- 位置：`compute_spec_mrope_positions` L760 · `_expand_mrope_from_input` L812 · `_compute_mrope_positions` L825 · `_pad_tensor_to_size` L885
- 其它：`_init_ngram_embedding_info` L747 · `can_run_tbo`（property）L1139
