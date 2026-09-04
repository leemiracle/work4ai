# 深度解析：`python/sglang/srt/model_executor/cuda_graph_runner.py`

> 源码: python/sglang/srt/model_executor/cuda_graph_runner.py @ commit ec075d8bc

## 目录

- [一、这个文件做什么](#一这个文件做什么)
- [二、背景知识：CUDA Graph 三分钟速成](#二背景知识cuda-graph-三分钟速成)
- [三、核心类与函数总览](#三核心类与函数总览)
- [四、静态输入 buffer：`DecodeInputBuffers`](#四静态输入-bufferdecodeinputbuffers)
- [五、捕获流程（capture）](#五捕获流程capture)
- [六、replay 路径](#六replay-路径)
- [七、与其他模块的交互](#七与其他模块的交互)
- [八、关键设计决策](#八关键设计决策)
- [九、端到端时序：一次 decode step 的完整旅程](#九端到端时序一次-decode-step-的完整旅程)
- [十、常见问题与误区](#十常见问题与误区)
- [十一、阅读建议](#十一阅读建议)

---

## 一、这个文件做什么

`cuda_graph_runner.py` 是 SGLang **CUDA Graph 执行器**的实现（模块 docstring，L14："Run the model with cuda graph and torch.compile"）。它的核心职责一句话概括：

> **在服务启动时，把 decode 阶段（自回归逐 token 生成）的整条前向计算一次性"录制"成 CUDA Graph；此后每次 decode step 只需把新数据拷进固定地址的输入 buffer，然后调用 `graph.replay()`，让 GPU 按录制好的 kernel 序列整图重放，从而消除 CPU 侧逐 kernel 的 launch 开销。**

### 1.1 为什么 decode 阶段特别需要 CUDA Graph

decode 的计算特征是"每步只算极少量 token（batch 内每请求 1 个），单 kernel 只有几十微秒，但 kernel 数量成百上千"。此时 kernel launch 的 CPU 开销（每次约 5-10 微秒，含驱动校验、参数打包、流同步语义）会超过 kernel 本身的 GPU 执行时间：

```
无 CUDA Graph（CPU 成为瓶颈）：
CPU:  [launch k1][launch k2][launch k3][launch k4] ...     ← CPU 忙着发射
GPU:            [==k1==]        [==k2==]        [==k3==]   ← GPU 中间有空隙

有 CUDA Graph：
CPU:  [graph.replay()]                                     ← 一次提交
GPU:  [==k1==][==k2==][==k3==][==k4==]...                  ← 背靠背执行
```

CUDA Graph 把整个 kernel 序列编译成一个可一次性提交的执行图，launch 开销从 O(kernel 数) 摊薄为 O(1)。对 LLM 这类一次 decode 前向要跑几百上千个小 kernel 的负载，这通常意味着 decode 吞吐提升 1.5~3 倍（小 batch 下更明显）。

### 1.2 全文件的核心矛盾

CUDA Graph 的代价是：**图内所有 kernel 的参数（尤其是指针地址）在捕获后不可变**。而推理输入天然动态——batch size 变、seq len 变、token 内容每步都变。所以这个文件的全部复杂度都来自一件事：

> **把"动态的推理输入"塞进"静态的图输入"。**

三板斧：

- **静态 buffer**（`DecodeInputBuffers`）：输入张量一次分配、地址永不变，数据靠拷贝进同一块内存；
- **batch size 离散化 + padding**（`capture_bs` 列表）：bs 连续变化不可图化，就预捕一组离散档位，运行时向上 pad 到最近档；
- **每 bs 一张图**（`self.graphs` 字典）：`{bs: CUDAGraph}`，replay 时按档位取图。

理解了这个矛盾，下面的所有代码就都顺理成章了。

### 1.3 家族成员

本文件在 `model_executor/` 目录下还有三个"兄弟"变体：

| 文件 | 特点 |
|---|---|
| `cpu_graph_runner.py` | CPU 版（自称"follows the CudaGraphRunner"，L16），结构刻意对齐本文件 |
| `piecewise_cuda_graph_runner.py` | 分段捕获，配合 torch.compile，段间可插入动态逻辑 |
| `breakable_cuda_graph_runner.py` | 可中途逃逸到 eager 的图，L52-61 直接从本文件 import 共享设施 |

本文件是其中最核心、最完整的一份，其余变体都建立在它的概念与工具之上。

---

## 二、背景知识：CUDA Graph 三分钟速成

读这个文件前，需要以下 PyTorch/CUDA 语义垫底（对应 `torch.cuda.CUDAGraph` API）：

1. **捕获（capture）**：在一条**非默认 stream** 上，以"捕获模式"执行一遍目标计算。期间所有 CUDA 调用不被真正执行，而是被录制进图对象。本文件用 `graph_capture()`（来自 `parallel_state`，L861）获取满足分布式协同语义的捕获 stream。
2. **重放（replay）**：`graph.replay()` 一次性把整张图提交给 GPU。**kernel 读写的是捕获时的那些地址**——这是"静态 buffer"的由来。
3. **内存池（graph pool）**：捕获期间分配的中间 tensor（激活值等）不归还常规分配器；多个图若**共享同一个 pool**（`torch.cuda.graph_pool_handle()`），后捕获的图可以复用先捕获图的内存块。本文件的全局池见 L520-530。
4. **捕获禁区**：捕获中不能有 host 同步（`cudaDeviceSynchronize`、`.item()` 类隐式同步）、不能有依赖 host 端数据的控制流、不能触发 `cudaFree`。这解释了后文的 warmup ×2、GC 冻结等一整套"防御性仪式"。
5. **torch.compile 的关系**：`torch.compile` 是 kernel 级编译优化，与 CUDA Graph 正交且可叠加——先把 python 前向编译成高效 kernel 序列，再把这序列录成图。注意 compile mode 必须选 `max-autotune-no-cudagraphs`（L455），把图管理权留给本文件。

---

## 三、核心类与函数总览

| 组件 | 行号 | 职责 |
|---|---|---|
| `_grouped_foreach_copy_` | L110-128 | 按 (dst_dtype, src_dtype) 分组批量拷贝，replay 前的数据搬运核心 |
| `DecodeInputBuffers` | L131-377 | 所有图输入的**静态 GPU buffer**（`create` + `populate_from_forward_batch`） |
| `is_capture_mode` / `model_capture_mode` | L381-401 | 全局"捕获中"标志，供外部（如 torch.compile 包装）感知 |
| `freeze_gc` | L404-420 | 捕获期间冻结 Python GC，防 gc 触发析构破坏捕获 |
| `patch_model` / `_to_torch` | L423-464 | 捕获时把模型包上 `torch.compile`（可选） |
| `set_torch_compile_config` | L467-480 | Inductor/Dynamo 调优开关 |
| `get_batch_sizes_to_capture` | L483-517 | 计算**要捕获哪些 batch size**（`capture_bs` 列表） |
| `global_graph_memory_pool` | L520-530 | 全局共享的 CUDA Graph 内存池（跨图复用中间 tensor 内存） |
| `CudaGraphRunner` | L533-1405 | 主类：`__init__` / `capture` / `can_run` / `replay` |
| `CUDA_GRAPH_CAPTURE_FAILED_MSG` | L1408-1415 | 捕获失败的排查建议文案 |
| `DeepEPCudaGraphRunnerAdapter` | L1418-1435 | DeepEP MoE 通信 buffer 的 capture/replay 模式对齐 |

调用关系鸟瞰：

```
ModelRunner.__init__ (惰性, model_runner.py:2815)
  └─ CudaGraphRunner.__init__                    L536
       ├─ get_batch_sizes_to_capture             L483  → capture_bs / compile_bs
       ├─ attn_backend.init_cuda_graph_state     L637  → backend 自备静态数组
       ├─ DecodeInputBuffers.create + share      L673-696
       └─ capture()                              L703 → L813
            └─ capture_one_batch_size(bs)        L917  (for bs in reversed(capture_bs))
                 ├─ 构造 ForwardBatch(静态切片)   L925-1053
                 ├─ backend 捕获元数据            L1073-1081
                 ├─ warmup ×2 (sync+barrier)     L1125-1129
                 └─ _capture_graph               L877 → torch.cuda.CUDAGraph 录制

ModelRunner.forward (model_runner.py:3284-3308)
  └─ can_run(forward_batch)                      L718
  └─ replay(forward_batch)                       L1260
       ├─ replay_prepare                         L1174
       │    ├─ recapture_if_needed               L1142 (hidden mode 变化→整树重捕)
       │    ├─ bisect 选 padding 档位             L1195-1198
       │    ├─ buffers.populate_from_forward_batch L1200 (拷数据)
       │    └─ backend 重放元数据                 L1240-1249
       └─ graphs[graph_key].replay()             L1298 → 切静态输出 buffer 返回
```

---

## 四、静态输入 buffer：`DecodeInputBuffers`

### 4.1 为什么需要它

CUDA Graph 捕获时记录的是"对哪些地址做什么操作"。重放时 kernel 读写的仍然是**捕获时的那些地址**。因此所有输入必须驻留在**一次分配、永不搬家**的 tensor 里——这就是 `DecodeInputBuffers`（L131，继承 `ForwardInputBuffers`）。

字段清单（L134-151）：

| 字段 | 形状（按 max） | 说明 |
|---|---|---|
| `input_ids` | `(max_num_token,)` int64 | 本步输入 token |
| `input_embeds` | `(max_num_token, hidden)` | dflash draft 走 embedding 输入 |
| `req_pool_indices` | `(max_bs,)` int64 | 每请求在 req pool 的行号 |
| `seq_lens` / `seq_lens_cpu` | `(max_bs,)` int32 | GPU/CPU 双份（部分 backend 读 CPU 版） |
| `out_cache_loc` | `(max_num_token,)` | 新 KV 写入的槽位 |
| `positions` | `(max_num_token,)` int64 | 位置 id |
| `mrope_positions` | `(3, max_num_token)` | 多模态 RoPE 三段坐标 |
| `num_token_non_padded` | `(1,)` int32 | 非 padding token 数 |
| `custom_mask` | 大 bool 数组 | 推测解码树注意力掩码（L184-187 按 fill value 定尺寸） |
| `next_token_logits_buffer` | `(max_num_token, vocab)` float | logits 直写目标（省一次拷贝） |
| `mamba_track_indices/mask` | `(max_bs,)` | mamba 状态跟踪 |
| `global_num_tokens_gpu` | `(dp_size,)` 或 `(1,)` | DP 拓扑的 token 计数 |
| `encoder_lens` | `(max_bs,)` int32 | encoder-decoder 专用 |
| `pp_proxy_tensors` | `{name: (max_bs, hidden)}` | pipeline 并行的层间传递 |
| `ngram_embedding_info` | 结构体 | ngram 推测解码 |

`create`（L153-270）用 `with torch.device(device)` 上下文按 `max_bs`（捕获的最大 batch）一次性分配。注意两个细节：

- `seq_lens_cpu` 特意留在 CPU 上并注释"Keep seq_lens_cpu as a true CPU tensor, like the old implementation"（L243-249）——CUDA Graph 同样可以捕获 CPU→GPU 拷贝或 CPU 侧读取，只要地址固定。
- L696 的 `self.buffers.share_buffers()`（基类 `ForwardInputBuffers` 提供）保证多进程/多 worker 视角下 buffer 是同一份存储。

### 4.2 replay 前的数据搬运：`populate_from_forward_batch`

这是**每次 decode step 都要跑的热路径**（L272-377）。逻辑分三段：

**第一段：padding 残留清理**（L286-297）。真实 batch（`raw_bs`）通常小于图捕获的 `bs`（padding 后），此时 buffer 尾部残留上一次 replay 的旧数据。做法是：

```python
if bs != raw_bs:
    self.seq_lens.fill_(seq_len_fill_value)   # 填充值 = backend 给的最大 seq len
    self.out_cache_loc.zero_()
    # Pair with seq_lens fill: padded rows must point at reserved
    # req_pool slot 0 (req_to_token[0, :] is all zeros from init), ...
    self.req_pool_indices.zero_()
```

L289-293 的注释解释了 `req_pool_indices.zero_()` 的深意：padding 行的 req pool 指针指向 **slot 0**，而 `req_to_token[0, :]` 从初始化起就是全零，于是 dummy attention 读到的 KV 索引全部落在安全的零号位置，不会读到上一次 replay 留下的过期行。**padding 的正确性不靠"不算这些行"，而靠"算了也无害"**——因为图中无法做数据相关的控制流跳过。这是整个 padding 机制安全性的基石，也是"CUDA Graph 与内存池（req_to_token_pool）布局耦合"的最直接体现：图的行为隐式依赖 slot 0 永远保留且全零这一约定。

**第二段：批量拷贝**（L299-371）。把 `forward_batch` 的真实数据（`[:raw_bs]` / `[:raw_num_token]` 切片）拷进静态 buffer 对应前缀。所有 GPU 拷贝收集进 `dsts`/`srcs` 两个列表：

```python
dsts = [self.input_ids[:raw_num_token], self.req_pool_indices[:raw_bs],
        self.seq_lens[:raw_bs], self.out_cache_loc[:raw_num_token],
        self.positions[:raw_num_token]]
srcs = [forward_batch.input_ids, forward_batch.req_pool_indices, ...]
# ...按需追加 mamba/encoder_lens/mrope/num_token_non_padded/pp_proxy_tensors
_grouped_foreach_copy_(dsts, srcs)          # L371
```

`_grouped_foreach_copy_`（L110-128）按 `(dst_dtype, src_dtype)` 分组后调用 `torch._foreach_copy_`（L107 探测可用性，老版本回退逐对 `copy_`），把 N 次 launch 合并成每组 1 次——**这本身就是"消除 launch 开销"哲学在 replay 路径上的延续**：数据搬运本身也是被优化的对象。条件字段（encoder_lens、mamba、mrope、pp_proxy_tensors 等）只有存在才追加进列表；ngram 的 `column_starts`/`req_lens` 单独直拷（L315-322）；DP 拓扑下 `global_num_tokens_gpu` 直接 `fill_(bs * num_tokens_per_bs)`（L345-347，注意填的是 padding 后的 bs——与捕获时 L959-990 的填法保持一致，图内读到的才不变）。

**第三段：CPU 拷贝**（L374-377）`seq_lens_cpu` 无法和 GPU 拷贝合并，单独做；若 `bs != raw_bs` 也要先整体 fill。

---

## 五、捕获流程（capture）

主链路：`CudaGraphRunner.__init__` → `capture()`（L813）→ 每个 bs 调 `capture_one_batch_size()`（L917）→ 内部 `_capture_graph()`（L877）执行真正的图录制。

### 5.1 `__init__`：决定"捕什么、怎么捕"（L536-707）

关键的几步决策：

**(a) 捕获哪个 forward mode**（L602-620）。默认 `ForwardMode.DECODE`、`num_tokens_per_bs = 1`。但推测解码（speculative decoding）下捕获的是 `TARGET_VERIFY` 模式，每请求一次算 `num_tokens_per_bs` 个 draft token（L612-617，draft 数由 `get_num_tokens_per_bs_for_target_verify` 依 draft worker 与否给出）；dllm 则捕 `DLLM_EXTEND`（L618-620）。也就是说**"decode 图"实际是"每请求固定 token 数的图"**，这个不变量由 `num_tokens_per_bs` 参数化——图静态性的本质是"每请求 token 数固定"，而不是"必须是 1"。

**(b) batch size 列表 `capture_bs`**（L623-625 调 `get_batch_sizes_to_capture`，函数在 L483-517）。默认列表来自 `server_args.cuda_graph_bs`（一组预定义 bs，如 1,2,4,8,...,160），然后做三重过滤/修正：

- `mul_base` 对齐（L489-497）：two-batch-overlap 要 ×2、gathered buffer（DP attention）要 ×attn_tp_size、还要能被 attention cp size 整除——因为模型输入 token 数 = bs × num_tokens_per_bs 必须能被 TP/CP 组整除（L506 注释）；
- 若 `--max-running-requests` 很小导致最大捕获 bs 大于 req pool 容量，则追加 `num_max_requests` 补齐（L499-504，先向上 pad 到 mul_base 的倍数避免被过滤掉）；
- 过滤掉超容量（L508）和对齐不满足的 bs（L507），去重排序（L509）。

同时返回 `compile_bs`（L512-516）：仅当 `--enable-torch-compile` 时，bs ≤ `torch_compile_max_bs` 的那些才走 torch.compile 编译——**编译大 batch 的图收益递减而编译耗时爆炸**，所以设上限。

**(c) attention backend 的图状态**（L635-637）：`attn_backend.init_cuda_graph_state(max_bs, max_num_token)`——attention backend 自己也要分配静态 buffer（如 FlashInfer 的 plan 工作数组、page table 槽位），这是 CudaGraphRunner 与 backend 的第一处耦合。PDMux（多路复用）模式下要对 backend 组里每个 backend 都初始化（L709-713）。

**(d) `seq_len_fill_value`**（L641-645）：来自 `attn_backend.get_cuda_graph_seq_len_fill_value()`，即该 backend 支持的最大可表示 seq len。padding 行的 seq_lens 填这个值（配合 4.2 第一段），保证任何真实请求的 seq len 都不超过它，attention kernel 的 metadata 数组不会越界。dllm 则直接用 block_size。encoder-decoder 下 `encoder_len_fill_value` 取 `max_source_positions`（L648-652），注释点明"Non-zero encoder length ensures cross-attention kernels are captured in the graph"——用非零值捕获才能保证交叉注意力的分支真的进图。

**(e) LoRA 两阶段初始化**（L657-664）：MoE buffer 在 ModelRunner 里早已初始化（Phase 1），这里做 Phase 2 的 dense batch metadata。捕获时用 `lora_ids = [None] * bs`（L1000-1005）是安全的，因为 LoRA kernel 在 `--enable-lora` 下总会发射、id 为空时立即返回（L1001-1002 注释）——又一个"把条件分支改成无条件执行+内部短路"的图友好手法。

**(f) 最后才是捕获本身**（L700-707）：在 `model_capture_mode()` 上下文里执行 `self.capture()`；失败则抛出带 `CUDA_GRAPH_CAPTURE_FAILED_MSG`（L1408-1415）的异常，提示降 `--mem-fraction-static`、降 `--cuda-graph-max-bs`、关 torch.compile 或干脆 `--disable-cuda-graph`。

### 5.2 `capture()`：逆序捕获与共享内存池（L813-875）

```python
with freeze_gc(...) as ...:
    if not self.enable_pdmux:
        with graph_capture() as graph_capture_context, profile_context as prof:
            self.stream = graph_capture_context.stream
            _capture_one_stream()               # 内部 for bs in reversed(self.capture_bs)
    else:
        set_pdmux_status(False)
        for i, sg in enumerate(self.stream_groups):    # PDMux: 每流一套图
            with graph_capture(stream=sg[1]) as ...:
                _capture_one_stream(i)
```

四个要点：

1. **逆序捕获**（L824-829 `reversed(self.capture_bs)`，L856-858 注释）："Capture the large shapes first so that the smaller shapes can reuse the memory pool allocated for the large shapes"。CUDA Graph 捕获期间分配的中间 tensor 不还内存，但**多张图共享同一个 memory pool 时，后捕获的图可以复用先捕获图已分配的块**。先捕最大的，小图的中间结果直接落在大图留下的块里，总显存≈最大那张图的峰值而不是所有图之和。捕获顺序在这里是**显存可行性的关键决策**，不是随意的。
2. **全局共享池**（L520-530 + L1131-1134）：`global_graph_memory_pool` 是模块级单例，"Reuse this memory pool across all cuda graph runners"（L520 注释）——draft/target 两个 worker 各有 runner，也共用一个池。首次捕获时惰性创建（`graph_pool_handle()`，L1132），并通过 `set_graph_pool_id`（L1134，来自 `pynccl_allocator`）告知 NCCL 分配器，使对称内存通信也能跨图共享。
3. **stream 语义**（L861-862）：`graph_capture()`（来自 `parallel_state`）返回的上下文提供一条专用捕获 stream。CUDA Graph 要求捕获发生在非默认 stream 上（默认 stream 的操作无法录制），且 TP 组内所有 rank 必须在同一条逻辑 stream 语义下捕获，否则集合通信（NCCL）的录制会错乱。PDMux 分支（L865-872）则为每个 stream group 各捕一套图，key 变成 `f"{stream_idx}_{bs}"`。
4. **GC 冻结**（`freeze_gc`，L404-420）：捕获中任何 Python 对象析构都可能触发 CUDA 事件（如 tensor 生命周期结束触发 `cudaFree`），直接毁掉捕获。先 `gc.collect()` 清场，再 `gc.freeze()` 把幸存对象移出收集代际，结束后 `unfreeze` + 再次 collect。

每个 bs 的捕获单元里（L830-854），`patch_model`（L841-846）按 `bs in compile_bs` 决定是否用 `torch.compile(model.forward)` 替换裸 forward（详见 5.6），产物存入 `self.graphs[key]` 与 `self.output_buffers[key]`（L852-854）。TP rank 0 上还包一层 tqdm 进度条实时显示剩余显存（L825-839，`get_available_gpu_memory(empty_cache=False)`）——捕获是启动时最可能 OOM 的阶段，进度可视化非常实用。

### 5.3 `capture_one_batch_size()`：单张图的完整录制（L917-1140）

这是全文件最长的函数，流程分五幕：

**第一幕：切 buffer、构造 ForwardBatch**（L920-1062）。注意所有输入都是 `self.buffers` 的**前缀切片**（`buffers.input_ids[:num_tokens]` 等，L926-937）——切片共享存储，图的输入地址即 buffer 首地址，这就是"静态地址"的落地。随后填充各类全局量：

- `num_token_non_padded`（L941-951，先填满 `num_tokens`，再按 attn TP 做本地化修正——与 replay 路径 4.2 第二段的填法逐字对齐，注释 L939-940 明说"matching replay path"）；
- PP 代理张量切片（L954-957）；
- DP 拓扑的 `global_num_tokens_gpu`（L959-992：mlp_tp_gather 时填 `[num_tokens]*dp_size`，attn_tp_gather 时填 `[num_tokens]`）；
- spec_info（L994-998，见 5.5）；
- LoRA 空id（L1000-1005）、mamba 跟踪（L1007-1017）、pdmux 的 backend 选择（L1019-1023）；
- 最后组装 `ForwardBatch`（L1025-1053）：`forward_mode=self.capture_forward_mode`、`seq_lens_sum=seq_lens.sum().item()`（L1035——捕获时这个标量被固化为常量进图，重放时由 `replay_prepare` 用公式修正，见 6.3）、`return_logprob=False`、`dp_padding_mode=DpPaddingMode.get_default_mode_in_cuda_graph()`；
- hisparse 协调器"喂"一个 `num_real_reqs.fill_(bs)`（L1057-1059）让其分支进图；
- ngram embedding 的 `slice(bs)`（L1061-1062）。

**第二幕：backend 元数据 + 预备钩子**（L1064-1081）。注释（L1064-1066）强调：这些钩子读 `forward_context` 里的 attn_backend，所以必须与 warmup/捕获 forward 处在**同一个 `ForwardContext`** 中。顺序是 tbo_plugin → lora prepare → `attn_backend.init_forward_metadata_capture_cuda_graph(...)`（L1073-1081）——backend 用捕获专用的假元数据（满 bs、满 seq len）初始化自己的静态计划数组。

**第三幕：`run_once` 闭包**（L1083-1121）。这是被 warmup 和捕获反复调用的"一次前向"：

```python
def run_once():
    # Without this, warmup-1 caches the translation; the capture
    # run hits the cache, skips the gather, and replay reuses
    # stale SWA locations.
    if self.model_runner.is_hybrid_swa:
        self.model_runner.token_to_kv_pool.invalidate_loc_cache()
    forward_batch.dp_local_start_pos = forward_batch.dp_local_num_tokens = None
    set_dp_buffer_len(global_dp_buffer_len, num_tokens, ...)
    set_is_extend_in_batch(False)
    kwargs = {}  # PP → pp_proxy_tensors 克隆; dflash draft → input_embeds
    logits_output_or_pp_proxy_tensors = forward(input_ids, forward_batch.positions,
                                                forward_batch, **kwargs)
    return logits_output_or_pp_proxy_tensors
```

- L1087-1088：hybrid SWA 模型先 `invalidate_loc_cache()`。注释讲了一个精妙的 bug：warmup 第一次跑时 loc cache 缓存了翻译结果，捕获跑命中缓存跳过了 gather，**重放时就会用过期的 SWA location**——所以每次 run_once 都要使缓存失效，强迫捕获到完整路径。三个 runner 变体里有同款修复（piecewise L603、breakable L393 都注释"same fix as in cuda_graph_runner.run_once"），说明这是真实踩过的坑。
- L1090-1098：清空 DP 局部量、`set_dp_buffer_len`、`set_is_extend_in_batch(False)`——把全局可变状态摆到 decode 图的"标准姿势"。
- L1100-1113：按函数签名探测式传参（`inspect.signature(forward).parameters`），PP 时克隆代理张量传入（克隆是为了不污染 buffer 原值），dflash draft worker 传 `input_embeds`。

**第四幕：两次 warmup**（L1125-1129）：

```python
for _ in range(2):
    self.device_module.synchronize()
    self.model_runner.tp_group.barrier()
    run_once()
    attn_backend.on_after_cuda_graph_warmup()
```

两次而非一次，因为第一次跑会触发各种惰性初始化（cuBLAS handle、kernel JIT/autotune、FlashInfer plan），**这些初始化里有些含 host 同步或非法的 stream 操作，绝不能发生在图录制中**；第二次跑才是干净的、可录制的稳态路径。每次前 `synchronize()` + TP `barrier()` 保证全组 rank 步调一致（集合通信捕获要求 rank 间以相同顺序进入捕获区）。backend 的 `on_after_cuda_graph_warmup()` 钩子则做诸如"把 plan 结果固化为可重放形态"的收尾。

**第五幕：正式捕获**（L1131-1138）。池懒初始化 + `set_graph_pool_id` 后调 `self._capture_graph(graph, get_global_graph_memory_pool(), stream, run_once)`。

### 5.4 `_capture_graph`：三种图后端（L877-908）

按配置选择图上下文：

| 后端 | 条件 | 行号 |
|---|---|---|
| BreakableCUDAGraph | `SGLANG_USE_BREAKABLE_CUDA_GRAPH` 开启 | L888-893 |
| Memory Saver | `enable_memory_saver` + `SGLANG_MEMORY_SAVER_CUDA_GRAPH` | L883-886, L895-897 |
| 常规 `torch.cuda.CUDAGraph` | 默认 | L898-899 |

- **Breakable CUDA Graph**（来自 `breakable_cuda_graph/`，非 HIP 平台专属，L95-100 才 import）：支持图中标记 `eager_on_graph` 的段落逃逸出图回 eager 执行——用于调试（`--debug-cuda-graph` 强制要求开启它，L878-881 的 assert）或某些无法捕获的算子。`_create_device_graph`（L910-915）同样按此选择图对象类型，HIP 上直接报不支持。
- **Memory Saver 模式**：`TorchMemorySaverAdapter` 配合 sleep/wake 机制，图内存可被标记（`tag=GPU_MEMORY_TYPE_CUDA_GRAPH`，L34）并在休眠时释放；与 Breakable 互斥（L889-892）。
- 最终 `with graph_ctx(cuda_graph=graph, pool=pool, stream=stream): out = captured_fn()`（L906-908）——在捕获上下文里执行 `run_once`，CUDA runtime 把这一趟发出的所有 kernel 录进 `graph`，返回值（输出 tensor 的引用）存入 `output_buffers`，其地址此后永久有效。

### 5.5 `get_spec_info`：推测解码的捕获骨架（L1332-1405）

按 spec 算法构造 verify 阶段的输入骨架（capture 时填假值，replay 时覆盖）：

- **EAGLE / standalone**（L1334-1363）：`EagleVerifyInput`，`custom_mask` 引用 `buffers.custom_mask` 这个静态大数组；standalone 用 `CaptureHiddenMode.NULL`，EAGLE 用 FULL（hidden states 是 draft 输入）；draft worker 到这里直接报错（L1340-1341，draft 走另一套捕获参数）。
- **DFLASH**（L1364-1389）：先 `resolve_dflash_verify_mask_policy` 探测 backend 能否用内建因果路径表达 verify（能则不启用 custom mask，L1370-1374 注释），draft worker 用 NULL、target 用 FULL。
- **NGRAM**（L1391-1404）：`NgramVerifyInput`，树掩码同样引用 `buffers.custom_mask`，hidden mode 固定 NULL。

共同点：所有"每步变化的数据"都以 `buffers.*` 静态数组为载体，spec_info 只是引用它们——这又是静态地址哲学的体现。

### 5.6 `patch_model` 与 torch.compile 的协作（L423-464）

`patch_model` 是上下文管理器：进入时若 `bs in compile_bs`，先 `_to_torch(model, ...)` 递归遍历模块树，把所有 `MultiPlatformOp`（自定义 CUDA 算子包装）切到 torch.compile 兼容模式（L423-431），再：

```python
yield torch.compile(
    torch.no_grad()(model.forward),
    mode=os.environ.get("SGLANG_TORCH_COMPILE_MODE", "max-autotune-no-cudagraphs"),
    dynamic=_is_hip and get_bool_env_var("SGLANG_TORCH_DYNAMIC_SHAPE"),
)
```

注意三点：(1) **compile mode 明确禁用 inductor 自己的 cudagraph**（`no-cudagraphs`），因为图管理权归 CudaGraphRunner，两层图会打架；(2) `torch.no_grad()` 内联包裹，捕获的前向天然无梯度；(3) dynamic shape 仅 HIP + 显式开关时启用。退出时反向恢复（L461-464）。L447-451 保留的注释还透露一段历史：曾经试过捕获期间禁用 custom allreduce（`tp_group.ca_comm = None`），因为自定义 allreduce 比 torch 内建（即使 `ENABLE_INTRA_NODE_COMM=1`）快得多而被回退。`set_torch_compile_config`（L467-480）打开 coordinate descent 调优、kernel 名唯一化、fx graph 缓存（加速重编译）、放宽 dynamo 缓存上限（L476-478 标注 FIXME 的 tmp workaround），最后 `monkey_patch_torch_compile()`（L480）修补兼容性。

### 5.7 捕获模式的全局标志（L380-401）

模块级 `is_capture_mode`（L381）+ `get_is_capture_mode`（L384）+ `model_capture_mode` 上下文管理器（L394-401）。`compile_in_capture_mode`（L388-391）展示用途：只在捕获期间才对某函数套 `torch.compile`。这是一个简单但必要的"侧信道"——模型内部组件无法都拿到 runner 引用，用模块级标志让它们感知"现在处于图捕获中"，从而切换到图友好的代码路径。

---

## 六、replay 路径

### 6.1 入口：`ModelRunner` 的分发

CudaGraphRunner 不自己决定何时用图。`model_runner.py` 的 forward（L3270-3308）做三步判定：

```python
can_run_graph = bool(
    forward_batch.forward_mode.is_cuda_graph()      # 模式允许（decode 类）
    and self.graph_runner                          # runner 已初始化
    and self.graph_runner.can_run(forward_batch)   # 本批次可捕获判定
)
if can_run_graph:
    ret = self.graph_runner.replay(forward_batch, skip_attn_backend_init=..., ...)
    return ModelRunnerOutput(logits_output=ret, can_run_graph=can_run_graph)
```

**分工边界**：`ModelRunner` 拥有模型、权重、attention backend、req/kv 池，负责"这次 forward 用不用图"（以及不用图时的完整 eager 路径）；`CudaGraphRunner` 拥有图和静态 buffer，负责"怎么捕、怎么放"。Scheduler 更上层只管把请求组装成 `ForwardBatch`，对图无感知。同文件还有 piecewise/breakable 两个 runner 变体的平行分发（L3086-3101），优先于本 runner 判定。

### 6.2 `can_run`：可捕获条件全集（L718-787）

逐条过"什么情况会拒绝走图"：

| # | 条件 | 行号 | 拒绝原因 |
|---|---|---|---|
| 1 | `forward_batch.replace_embeds is not None` | L720-721 | token embedding 覆盖是每请求动态的，图内无法表达 |
| 2 | bs 超界 | L737-741 | `disable_padding` 时要求 `graph_key in self.graphs`（精确命中已捕获 bs）；默认允许 `cuda_graph_bs <= max_bs`（靠 padding） |
| 3 | DP mlp sync 不一致 | L743-744 | `require_mlp_sync` 时还需 `forward_batch.can_run_dp_cuda_graph`——DP 各 rank 的图形状必须一致，本 rank bs 再小也得跟着跑大图 |
| 4 | 混合 encoder batch | L749-753 | encoder-decoder 下 `encoder_lens` 必须全 >0（不能 prefill-only 请求混入），否则交叉注意力行为不同，一张图装不下两种形态 |
| 5 | hidden mode 不匹配 | L755-767 | 请求的 `capture_hidden_mode`（NULL/LAST/FULL，取 forward_batch 与 spec_info 的 max）必须与捕获时一致或可兼容；不一致则触发**重新捕获**（见 6.4）而非直接拒绝 |
| 6 | tbo 不可用 | L768-770 | two-batch-overlap 的分裂条件不满足 |
| 7 | ngram 形状不符 | L772-779 | ngram 推测解码要求 `bs * num_tokens_per_bs == input_ids.numel()` |

另外 `cuda_graph_bs` 的算法（L722-731）值得一提：mlp_tp_gather（DP attention）时用**全局 token 数最大值**折算 bs（EAGLE/standalone/dflash 还要除以 `num_tokens_per_bs`），保证 DP 组所有 rank 选到同一张图——这是 DP 一致性的关键。PDMux 下 key 加 stream 前缀（L734-735）。L746-748 的 NOTE 还预告了一个简化机会：若彻底不支持混合批，`encoder_lens` 可以从图输入里删掉（因为掩码恒为全 1）。

### 6.3 `replay` 与 `replay_prepare`（L1260-1330 / L1174-1258）

`replay()` 的骨架意外地短：

```python
self.deepep_adapter.replay()                      # L1266: 恢复捕获时的 DeepEP dispatch 模式
if not skip_attn_backend_init:
    self.replay_prepare(forward_batch, ...)       # 数据搬运 + backend 元数据
else:                                             # L1270-1281: 推测解码多步复用
    self.buffers.input_ids[: self.raw_num_token].copy_(forward_batch.input_ids)
    self.buffers.positions[: self.raw_num_token].copy_(forward_batch.positions)
    # (+ dflash 的 input_embeds)
...
with ctx:                                         # device_timer 打点（可选）
    self.graphs[graph_key].replay()               # L1298: 整图重放，一行!
output = self.output_buffers[graph_key]           # L1300: 输出直接从静态 buffer 切
```

`skip_attn_backend_init=True` 的分支服务于推测解码的多步 draft：同一张图连续 replay 时 backend 元数据已就绪，只需补拷最小输入集。

`replay_prepare` 的核心步骤：

1. **`recapture_if_needed`**（L1180，见 6.4）。
2. **padding 选图**（L1186-1198）：`bisect.bisect_left(self.capture_bs, raw_bs)` 找到 ≥ 真实 bs 的最小捕获 bs。`capture_bs` 有序，二分查找 O(log n)。mlp_tp_gather 时先从全局 token 数折算（与 can_run 的算法镜像对称）。
3. **`populate_from_forward_batch`**（L1200-1213）：即第 4.2 节的数据搬运。
4. **tbo / idle / dflash 的补丁**（L1215-1230）：dflash draft 的 `input_embeds` 拷贝；tbo 的 `replay_prepare`；idle 模式（DP rank 无请求）把 `buffers.custom_mask` 挂给 spec_info。
5. **backend 重放元数据**（L1240-1249）：

```python
attn_backend.init_forward_metadata_replay_cuda_graph(
    bs, buffers.req_pool_indices[:bs], buffers.seq_lens[:bs],
    forward_batch.seq_lens_sum + (bs - raw_bs) * self.seq_len_fill_value,  # ← 关键修正
    buffers.encoder_lens[:bs] if self.is_encoder_decoder else None,
    self.capture_forward_mode, forward_batch.spec_info,
    seq_lens_cpu=buffers.seq_lens_cpu[:bs],
)
```

attention 的 page table、seq len 数组是图输入的一部分，必须在 replay 前写进 backend 的静态数组。`seq_lens_sum` 的修正公式（L1244）：捕获时它是满 padding 的和（L1035 固化进图），重放时给 backend 的这个标量也必须补上 padding 行的贡献（每行 `seq_len_fill_value`），两边才对得上。L1237-1239 的 FIXME 自曝了一个设计债：某些 backend（dsv4）需要完整 `forward_batch`，于是临时塞到 `attn_backend._replay_forward_batch` 这个"隐式通道"上，用完置 None——TODO 是把它变成接口的正经参数。

6. **记录 raw_bs/bs**（L1252-1258）供输出裁剪；hisparse 的 `num_real_reqs` 填**真实** bs（L1257-1258，对比捕获时填满 bs，L1059——捕获时填满是为了分支进图，重放时填真值是为了语义正确，这个不对称是理解"图形状 vs 运行时语义"分离的好例子）。

输出处理（L1300-1330）：图输出也是静态 buffer，按 `raw_num_token` 切出真实部分返回 `LogitsProcessorOutput`（next_token_logits/full_logits/hidden_states 裁剪，dllm 与普通模式互换取用），PP 场景裁 `PPProxyTensors`（按 `self.bs`）。**用户侧看到的输出与 eager 路径同构，padding 完全不可见**。

### 6.4 `recapture_if_needed`：运行时重捕（L1142-1172）

`capture_hidden_mode`（是否返回/如何返回 hidden states）有三级来源：forward_batch、spec_info、`--enable-return-hidden-states`（L1147-1158）。取 max 得到"当前需要的模式"（L1163-1167，注释说明层级兼容性：FULL 可模拟 LAST/NULL，LAST 可模拟 NULL）。若与捕获时不一致——例如 EAGLE target worker 起初不需要 hidden，后来 spec 策略要求——就更新 `self.capture_hidden_mode` 并**整体重新 `capture()`**（L1170-1172）。这是一个"运行时自适应重录"的机制，代价高昂但极少发生（`__init__` 里 L631-632 已经把 `enable_return_hidden_states` 场景预捕为 FULL，注释明言"avoid double-capture on startup"）。

### 6.5 `DeepEPCudaGraphRunnerAdapter`（L1418-1435）

DeepEP（MoE 专家并行的 all-to-all 通信库）内部有 normal/low-latency 两种 dispatch 模式，且 buffer 状态参与图捕获。adapter 在捕获时记录 `get_deepep_mode().resolve(is_extend_in_batch=False)`（L1426-1428，decode 图固定用非 extend 分支），replay 前 `set_dispatch_mode` 恢复并断言一致（L1431-1435）——**通信库内部状态也是"图参数"的一部分**，这个 30 行的小类是把该依赖显式化的全部代价。

---

## 七、与其他模块的交互

- **`model_executor/model_runner.py`**：构造（L2815 惰性初始化）与 replay 分发（L3270-3308）；`enable_return_hidden_states`/LoRA/DP 等开关都从 `model_runner.server_args` 读取。同文件还有 piecewise/breakable 两个 runner 变体的分发逻辑（L3086-3101）。
- **`model_executor/forward_batch_info.py`**：`ForwardBatch`/`ForwardMode`/`CaptureHiddenMode`/`PPProxyTensors` 的定义；`forward_mode.is_cuda_graph()` 是走图的准入条件；`can_run_dp_cuda_graph`/`can_run_tbo` 字段由调度侧在生产 ForwardBatch 时填好。
- **`model_executor/input_buffers.py`**：`ForwardInputBuffers` 基类与 `share_buffers`。
- **attention backend（`layers/attention/*`）**：三段式钩子 `init_cuda_graph_state` / `init_forward_metadata_capture_cuda_graph` / `init_forward_metadata_replay_cuda_graph`（+`on_after_cuda_graph_warmup`、`get_cuda_graph_seq_len_fill_value`）。CudaGraphRunner 只定义协议不管实现，backend 自带静态数组——这是 runner 与 backend 解耦的全部接口面。
- **`distributed/parallel_state.py` 的 `graph_capture`**：提供捕获 stream 与 TP 组协同；`set_pdmux_status` 支撑 PDMux。
- **`distributed/device_communicators/pynccl_allocator.py` 的 `set_graph_pool_id`**（L36-38, L1134）：把共享池 id 通报给 NCCL 分配器以启用对称内存。
- **`batch_overlap/two_batch_overlap.py` 的 `TboCudaGraphRunnerPlugin`**：micro-batch 重叠的捕获/重放钩子（L1068, L1222-1228）。
- **`layers/moe/token_dispatcher/deepep.py` 的 `DeepEPBuffer`** + 本文件 `DeepEPCudaGraphRunnerAdapter`（6.5 节）。
- **`utils/torch_memory_saver_adapter.py`** 与 **`breakable_cuda_graph/`**：两种图内存/可逃逸的变体后端。
- **`utils/patch_torch.py` 的 `monkey_patch_torch_compile`**（L480）：修补 torch.compile 与 SGLang 的兼容性。
- **`environ.py` 的 `envs`**（L45）：`SGLANG_USE_BREAKABLE_CUDA_GRAPH` 等环境变量的规范入口。
- **兄弟实现**：`piecewise_cuda_graph_runner.py`、`cpu_graph_runner.py`、`breakable_cuda_graph_runner.py`（见 1.3）。

---

## 八、关键设计决策

1. **"静态地址 + 离散 bs + padding"三件套化解动态性**。LLM decode 的动态维度（bs、seq len、token 内容）中，只有 token 内容能通过"拷进固定 buffer"解决；bs 靠预捕一张图矩阵、运行时 padding 到最近档位（4.2/6.3）；seq len 靠 fill value 上界化（5.1d）。这是所有 CUDA Graph 推理系统的通用范式，SGLang 的实现特别点在于 padding 行的安全性靠 **req pool slot 0 的零初始化**兜底（L289-293），而非试图在图内做掩码——"算了也无害"比"想办法不算"便宜得多。
2. **跨图共享 memory pool + 逆序（大→小）捕获**（L520, L824-829, L1131-1134）。捕获期分配的显存不归还，若每图独立池，几十张图的中间 tensor 会吃掉数 GB。共享池让小图复用大图的块，整体显存≈最大图的峰值；且池跨 worker（draft/target）全局共享，并打通到 NCCL 对称内存。这是让"每 bs 一张图"在显存上可行的配套决策，两者缺一不可。
3. **warmup ×2 + synchronize + TP barrier 的捕获纪律**（L1125-1129）。惰性初始化、autotune、host 同步都是捕获杀手；先跑两遍稳态化再录，是踩坑后的标准配方。配套的还有 GC 冻结（L404-420）、SWA loc cache 每次 `run_once` 失效（L1087-1088 的注释完整记录了这个 stale-location bug 的成因，且三个 runner 变体都复制了同款修复）——这些"防御性仪式"每一处都对应一类真实的捕获失败，读它们等于读一份故障史。
4. **图管理权集中于 runner，可捕获性判定分散到数据生产方**。`can_run`（L718-787）用五个布尔 AND 收口，但每个布尔的语义（replace_embeds、can_run_dp_cuda_graph、encoder_lens、capture_hidden_mode、ngram 形状）由上游在构造 ForwardBatch 时就决定。同样，attention/LoRA/DeepEP/TBO 各自通过钩子协议参与捕获，runner 不理解它们的内部，只编排时机（同一 `ForwardContext` 内完成钩子与捕获，L1064-1067 注释）。这使 CUDA Graph 这种"侵入式优化"没有扩散污染整个代码库——新增一种 backend 只要实现三段式钩子即可接入图。
5. **把"逃逸舱口"做成一等公民**。BreakableCUDAGraph（`eager_on_graph`，L96-100, L888）、memory saver（L883-899）、`skip_attn_backend_init` 的轻量重放（L1270-1281）、运行时 `recapture_if_needed`（L1142-1172）——承认"一刀切的整图"无法覆盖所有场景，从设计上就留好了降级与重录路径，而不是失败即崩溃。捕获失败的用户出口也有现成文案（`CUDA_GRAPH_CAPTURE_FAILED_MSG`，L1408-1415）。

---

## 九、端到端时序：一次 decode step 的完整旅程

把前面所有组件串成一条时间线（普通 TP、无推测解码、默认 padding 开启）：

```
[S Scheduler]   组装 running batch → ForwardBatch(bs=37, decode)
                     │
[M ModelRunner.forward]
                     ├─ forward_mode.is_cuda_graph() ✓
                     ├─ graph_runner.can_run(fb):
                     │     replace_embeds None ✓; 37 <= max_bs ✓;
                     │     encoder 无关 ✓; hidden mode NULL==NULL ✓
                     ▼
[R CudaGraphRunner.replay(fb)]
                     ├─ deepep_adapter.replay()                    L1266
                     ├─ replay_prepare:                            L1174
                     │    ├─ recapture_if_needed → 无需             L1142
                     │    ├─ bisect(capture_bs, 37) → bs=48        L1197
                     │    ├─ populate_from_forward_batch:          L1200
                     │    │    seq_lens.fill_(fill_value) 尾部 11 行
                     │    │    req_pool_indices.zero_() → slot 0
                     │    │    foreach_copy: ids/positions/seq_lens/...
                     │    ├─ attn_backend.init_forward_metadata_...replay
                     │    │    (page table/seq_lens_sum 修正)        L1240
                     │    └─ self.bs=48, self.raw_bs=37             L1252
                     ├─ graphs[48].replay()    ← 整图上 GPU         L1298
                     │    （图内：embedding→31×decoder→logits→
                     │      写 next_token_logits_buffer，全是录好的 kernel）
                     └─ output_buffers[48].next_token_logits[:37]   L1312
                          → LogitsProcessorOutput → Sampler → 下一个 token
```

对照启动时的准备：`__init__` 里已按 `capture_bs=[1,2,4,...,160]` **逆序**捕好 160/128/.../1 共 N 张图，全部挂在全局共享 pool 上；每张图捕前跑了两遍 warmup，捕时 `buffers` 的切片地址就是图输入地址。replay 阶段做的全部工作只是：**把 37 行真实数据拷到那些地址、告诉 backend 真实元数据、按一下重放键、从静态输出 buffer 切前 37 行**。

---

## 十、常见问题与误区

**Q1：为什么不像 prefill 一样也给 extend 捕图？**
extend 的 token 数每批差异巨大且无上界可枚举，图矩阵会爆炸；且 prefill 是 compute-bound，launch 开销占比小，收益本来就低。SGLang 的选择是只捕 decode 形态（含推测解码的 verify——它本质也是"每请求固定 token 数"），prefill 走 eager/piecewise。

**Q2：padding 到 48 不会浪费算力吗？**
会，多算 11 个 dummy 行。但 dummy 行的读指针都指向 slot 0 的零区（L289-293），结果被丢弃；与省下的 launch 开销相比仍然净赚。若业务 bs 分布集中，可用 `--disable-cuda-graph-padding` 换成精确匹配模式（L737-741），或用 `--cuda-graph-bs` 自定义档位列表减少浪费。

**Q3：图输出会不会被下一次 replay 覆盖？**
会。`output_buffers[key]` 是静态 buffer，replay 完必须立刻切片消费（L1300-1330 返回的是**视图**）。上层若需要跨 step 持有 logits，得自己 clone——`LogitsProcessorOutput` 的消费方（sampler）在同一步内同步读完，这是隐含契约。

**Q4：`seq_lens_sum` 为什么捕获时是 `.item()`（host 同步）也没事？**
`.item()` 发生在 warmup/捕获**前**的 ForwardBatch 构造阶段（L1035），那时还在普通模式；真正进图的只是这个标量的**值**。而重放时 backend 需要的动态和由公式 `+ (bs-raw_bs)*fill_value` 补齐（L1244）。host 同步不是绝对禁区，"发生在捕获区外"才是要求。

**Q5：`can_run` 返回 False 之后去哪了？**
落到 ModelRunner 的 eager 路径（model_runner.py L3310 往下：prepare_mlp_sync_batch / prepare_attn_tp_scatter_input → 正常 forward）。图是快路径不是唯一路径，这就是"逃逸舱口"思想在调用侧的体现。

**Q6：torch.compile 和 CUDA Graph 是不是二选一？**
不是，是叠加关系：compile 负责"每页 kernel 更快"，graph 负责"发射更便宜"。叠加点在 `patch_model`（L452-458），且 compile 的 cudagraph 模式必须关掉（`max-autotune-no-cudagraphs`）避免两层图冲突。

---

## 十一、阅读建议

1. **先读 `DecodeInputBuffers.populate_from_forward_batch` 再读 capture**。理解"重放时数据怎么进来"，反过来才能理解"捕获时为什么那样布置地址"。配合 `replay()`（L1260）看一遍端到端：拷数据 → backend 元数据 → `graphs[key].replay()` → 切输出。
2. **对照 attention backend 读钩子协议**。挑一个简单实现（如 `flashinfer_backend.py`）看 `init_cuda_graph_state` / `init_forward_metadata_capture_cuda_graph` / `init_forward_metadata_replay_cuda_graph` 三联函数怎么操作自家的静态数组，能具体感受到"CUDA Graph 与内存池地址固定的耦合"。
3. **用实验感知收益**：`--enable-profile-cuda-graph`（L566-568, L789-811）会产出按 CUDA/CPU 时间排序的 profiler 表和内存快照 pickle；再对比 `--disable-cuda-graph` 跑 `bench_decode`，观察 decode 吞吐差距。
4. **调试捕获失败**：按 `CUDA_GRAPH_CAPTURE_FAILED_MSG`（L1408-1415）的顺序排查（显存→max-bs→torch.compile→整体禁用）；想逐步定位可开 `--debug-cuda-graph` + `SGLANG_USE_BREAKABLE_CUDA_GRAPH`（L878-881）用分段图把失败点圈出来。
5. **横向对比三个变体**：`piecewise_cuda_graph_runner.py`（torch.compile 分段图）、`breakable_cuda_graph_runner.py`（可逃逸图）、`cpu_graph_runner.py`（CPU 图）与本文件的结构差异，会看清哪些是 CUDA Graph 的本质约束（静态地址、无控制流），哪些是本实现的选择（padding 策略、warmup 次数）。
6. **延伸阅读顺序**：`model_runner.py` 的 `forward`/`forward_decode`（图的总入口）→ `forward_batch_info.py`（ForwardMode 状态机）→ `parallel_state.graph_capture`（捕获 stream 的分布式协同）→ PyTorch 官方 "CUDA Graphs" 文档（`torch.cuda.CUDAGraph`/`graph_pool_handle`/`make_graphed_callables` 的语义）。
