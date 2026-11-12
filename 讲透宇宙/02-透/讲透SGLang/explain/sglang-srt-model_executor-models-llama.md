# 深度解析：`python/sglang/srt/model_executor/models/llama.py`

> 源码: python/sglang/srt/model_executor/models/llama.py @ commit ec075d8bc
>
> （路径说明：本次分析的 commit `ec075d8bc` 中，模型文件已从历史路径 `srt/model_executor/models/` 整体迁移至 `python/sglang/srt/models/llama.py`，全仓 193 个模型实现文件都在新位置；下文行号均以新路径的实际文件为准，标题保留历史路径以对应旧版资料。）

llama.py 是读懂 SGLang 全部 200+ 模型实现的"罗塞塔石碑"：它用约 860 行实现了最标准的 dense decoder-only Transformer，把 SGLang 推理引擎对模型层的**全部约定**——统一 forward 签名、`ForwardBatch` 驱动、`RadixAttention` 间接层、attention backend 双模式分派、KV cache 写入路径、TP/PP/DP 三种并行的接入点、quantization/LoRA 注入点、权重名重映射——以最小噪声的方式完整暴露出来。其他 190+ 个模型文件全部是对这份模板的"变奏"：Qwen 系列只是换了 rope 与注意力细节，DeepSeek 系列把 MHA 换成 MLA，Mixtral 在 MLP 处插入 MoE——骨架完全一致。更妙的是 `Phi3ForCausalLM`、`InternLM3ForCausalLM` 等架构对它零成本复用（840-849 行，纯继承一行通过），说明这份文件定义的就是 SGLang 的"模型实现协议"本身。读透它，再看任何新模型只需 diff 出增量。

---

## 核心类与函数

### 1.1 全景：四层类结构

```
LlamaForCausalLM            # 463 行：对外入口（registry 注册的就是它）
 ├── .model = LlamaModel    # 339 行：骨干网络（embed + N × decoder layer + final norm）
 │    ├── .embed_tokens     # VocabParallelEmbedding（仅 PP 首 rank，351-357 行）
 │    ├── .layers           # make_layers() 构造的 ModuleList（366-378 行）
 │    └── .norm             # RMSNorm（仅 PP 末 rank，380-383 行）
 ├── .lm_head               # ParallelLMHead / 或与 embed 共享（498-507 行）
 ├── .logits_processor      # LogitsProcessor（508 行）
 └── .pooler                # Pooler（509 行，embedding 任务用）
```

每一层 decoder layer 内部：

```
LlamaDecoderLayer           # 256 行
 ├── .input_layernorm       # RMSNorm（309 行）
 ├── .self_attn = LlamaAttention   # 287-301 行
 │    ├── .qkv_proj         # QKVParallelLinear（173-181 行）
 │    ├── .o_proj           # RowParallelLinear（182-188 行）
 │    ├── .rotary_emb       # get_rope(...) 工厂（190-197 行）
 │    └── .attn             # RadixAttention（198-206 行）★ 无参数的"注意力插座"
 ├── .post_attention_layernorm  # RMSNorm（310-312 行）
 └── .mlp = LlamaMLP        # 302-308 行
      ├── .gate_up_proj     # MergedColumnParallelLinear（85-93 行）
      └── .down_proj        # RowParallelLinear（94-104 行）
```

关键洞察：**`RadixAttention` 本身没有任何可计算的东西**（radix_attention.py:54-147），它只是携带元数据（head 数、head_dim、layer_id、k_scale 等）的"插座"；真正的 attention 计算发生在运行时被注入的 `AttentionBackend` 里。这就是 SGLang 能让同一份模型代码跑在 FlashInfer/Triton/FA3/TRT-LLM/CUTLASS-MLA 等十几种后端上的根源。

### 1.2 LlamaMLP（71-124 行）

```python
self.gate_up_proj = MergedColumnParallelLinear(   # 85-93 行
    hidden_size, [intermediate_size] * 2, ...)     # 两列拼成一个矩阵
self.down_proj = RowParallelLinear(...)            # 94-104 行
self.act_fn = SiluAndMul()                        # 110 行
```

- HF 的 `gate_proj` + `up_proj` 两个独立矩阵在此**融合为单个 `gate_up_proj`**（列并行，输出维 `2×intermediate_size`），forward 里一次 GEMM 后由 `SiluAndMul` 拆分相乘（118-119 行），再过 `down_proj`（行并行）。GEMM 次数从 3 降到 2，这是为 batch 变长场景下的 kernel 启动开销做的标准优化。
- 105-109 行：硬性检查 `hidden_act == "silu"`——样板文件不支持其他激活，其他模型（如 gelu 系）需要换 `activation.py` 里的实现。
- 两个 TP 定制参数预埋在此：`use_dp_attention_reduce`（82/103 行，DP attention 时 `down_proj` 的 all-reduce 改在 attention-TP 组上做，见 1.7 与设计决策 5）与 forward 的 `use_reduce_scatter`（116 行→122 行 `skip_all_reduce=use_reduce_scatter`，配合 reduce-scatter 通信融合）。

### 1.3 LlamaAttention（127-253 行）

**构造期（128-206 行）做了五件事：**

1. **TP 头切分**（147-160 行）：`num_heads`、`num_kv_heads` 除以 `tp_size`。152-159 行处理 GQA 的两种情况——KV 头 ≥ TP 数则均分；KV 头 < TP 数则**复制**（`tp_size % total_num_kv_heads == 0`），保证每个 rank 至少有一个完整 KV 头。`self.num_kv_heads = max(1, ...)`（160 行）。
2. **head_dim 推断**（162-164 行）：`getattr(config, "head_dim", hidden_size // total_num_heads)`——兼容 Mistral-Nemo 等显式声明 head_dim 的配置。
3. **qkv 融合投影**（173-181 行）：`QKVParallelLinear(hidden_size, head_dim, total_num_heads, total_num_kv_heads, ...)`——Q/K/V 三个 HF 矩阵融合成一个 GEMM，输出布局为 `[q | k | v]`，且每个 rank 只含自己那份头。
4. **RoPE 工厂**（190-197 行）：`get_rope(head_dim, rotary_dim, max_position, base, rope_scaling, is_neox_style)`——所有 rope 变体（linear/yaRN/dynamic NTK/partial rotary）都在这个工厂里分发，模型文件不用关心。
5. **RadixAttention 插座**（198-206 行）：传入本 rank 的 `num_heads`、`head_dim`、`scaling=head_dim**-0.5`（169 行）、`num_kv_heads`、`layer_id` 和 `quant_config`。

**quantization 注入点**：注意 `quant_config` 一路透传给 `qkv_proj`/`o_proj`（179/187 行）和 `RadixAttention`（204 行）。每个线性层内部会用 `quant_config.get_quant_method()` 决定用 FP8/GPTQ/AWQ 哪种 kernel；RadixAttention 则在 radix_attention.py:96-99 处拿 quant_method 创建 KV cache 量化参数（`k_scale`/`v_scale`，90-93 行），供 `load_kv_cache_scales`（437-456 行）从标定文件回填。**模型代码里没有任何 if-else 量化分支**——量化是线性层的"内政"。

**LoRA 注入点**：模型文件里同样看不到 LoRA。`ModelRunner` 构造模型后，若开启 LoRA，会在 model_runner.py:1999 创建 `LoRAManager`，后者扫描 `named_modules()` 并把命中 target（qkv_proj/gate_up_proj/...）的模块**原地替换**为 LoRA 包装层（lora_manager.py:715-719，`get_lora_layer(module, backend)` + `replace_submodule`）。forward 时的 per-request adapter 选择则由 `ForwardBatch.lora_ids`（forward_batch_info.py:371/558 行）+ `prepare_lora_batch`（forward_batch_info.py:665-672 行）完成。

**forward（229-253 行）——两条硬件路径：**

```python
def forward(self, positions, hidden_states, forward_batch):
    if not _is_npu or ... or forward_batch.forward_mode.is_extend():   # 235-239 行
        q, k, v = self.forward_prepare_native(positions, hidden_states)
    else:
        q, k, v = self.forward_prepare_npu(positions, hidden_states, forward_batch)
    attn_output = self.attn(q, k, v, forward_batch)   # 251 行 ★ 核心一行
    output, _ = self.o_proj(attn_output)              # 252 行
    return output
```

- `forward_prepare_native`（208-212 行）：qkv GEMM → 按 `[q_size, kv_size, kv_size]` 切三段（210 行）→ rope 只作用于 q/k（211 行）。
- `forward_prepare_npu`（214-227 行）：昇腾 NPU 上把"split + rmsnorm + rope"融合进 `split_qkv_rmsnorm_rope` 单核（68 行 import），cos/sin 缓存每层只在 `layer_id == start_layer` 时刷新一次（216-217 行）。这是样板文件里唯一的硬件特化分支，展示了 SGLang 如何塞厂商融合核：**不动接口，只替换 prepare 段**。

### 1.4 LlamaDecoderLayer（256-336 行）

构造期值得注意的是配置兼容层：267-281 行处理 `rope_parameters`（新式配置）与 `rope_theta`/`rope_scaling`（旧式）两套字段并注入 `original_max_position_embeddings`；282-286 行兼容 llamafy Qwen / InternLM 的 `attention_bias`。

forward（314-336 行）是 SGLang 招牌的 **fused residual + layernorm** 模式：

```python
if residual is None:                          # 322-324 行：第一层
    residual = hidden_states
    hidden_states = self.input_layernorm(hidden_states)
else:                                         # 326 行：后续层
    hidden_states, residual = self.input_layernorm(hidden_states, residual)
```

`RMSNorm.forward(x, residual)` 在一个 kernel 里完成"残差累加 + 归一化"，返回 `(normed, new_residual)`——省一次显存往返。334 行 `post_attention_layernorm` 同样返回双值。**residual 作为独立张量在层间流转**是所有 SGLang 模型的统一约定（它也因此能被 `PPProxyTensors` 跨流水级传递，见 1.5）。

### 1.5 LlamaModel（339-461 行）

- **PP 感知的嵌入**（350-359 行）：`is_first_rank` 才建 `embed_tokens`，否则 `PPMissingLayer()` 占位。
- **层区间切分**（361-378 行）：`get_pp_indices(num_hidden_layers, rank, world_size)` 算出本 rank 负责的 `[start_layer, end_layer)`，`make_layers()`（utils/common.py:686-727）生成 ModuleList：前段/后段都是 `PPMissingLayer` 占位（保证层号与权重名对齐），中段才真正构造。`make_layers` 同时是 offloader（层级权重换入换出）的挂钩点。
- **forward（386-432 行）**：
  - 394-399 行：首 rank 做 `embed_tokens(input_ids)`（或直接用外部 `input_embeds`，多模态模型靠这个口子注入视觉特征），`residual = None`；
  - 400-405 行：非首 rank 从 `pp_proxy_tensors["hidden_states"]/["residual"]` 恢复中间态——**上一流水级的输出只有这两个张量**（FIXME 注释表明未来想减少）；
  - 408-417 行：`for i in range(self.start_layer, self.end_layer)` 逐层调用，`hidden_states, residual = layer(positions, hidden_states, forward_batch, residual)`；409-410 行在此截获 `aux_hidden_states`（EAGLE3/DFLASH 训练目标需要中间层特征，`layers_to_capture` 由 813-837 行的方法填充）；
  - 419-425 行：非末 rank 把 `(hidden_states, residual)` 打包成 `PPProxyTensors` 返回（由 scheduler 层负责发送）；末 rank 427 行做 final norm。
- `load_kv_cache_scales`（437-456 行）：FP8 KV 标定回填，451-452 行直接写 `attn.k_scale/v_scale`。

### 1.6 LlamaForCausalLM（463-838 行）

构造（485-519 行）：

- **tie_word_embeddings**（496-507 行）：Llama-3.2-1B 等小模型 `lm_head` 直接复用 `embed_tokens` 的 Python 对象（499 行），省一份 vocab×hidden 大矩阵；否则建 `ParallelLMHead`，且 `use_attn_tp_group=get_global_server_args().enable_dp_lm_head`（506 行）——DP attention 时 lm_head 的词表切分口径切换到 attention-TP 组（见设计决策 5）。
- `LogitsProcessor(config)`（508 行）与 `Pooler(pooling_type=PoolingType.LAST, normalize=True)`（509 行）：一个类同时伺候生成任务和 embedding 任务。
- 465-483 行三张类级映射表是给 **bitsandbytes 量化加载器**用的（`bitsandbytes_stacked_params_mapping` 把 HF 的 `.q_proj/.k_proj/.v_proj` 映射到融合后的 `.qkv_proj` 的 0/1/2 槽位）。
- `stacked_params_mapping`（510-517 行）是给 `get_module_name_from_weight_name`/`get_weights_by_name`（单测/debug 用）用的实例级映射；`load_weights` 里 631-638 行还有一份局部同款——加载路径自包含，不依赖构造期状态。

**forward（529-563 行）**——整个文件的中枢：

```python
@torch.no_grad()
def forward(self, input_ids, positions, forward_batch,
            input_embeds=None, get_embedding=False, pp_proxy_tensors=None):
    hidden_states = self.model(input_ids, positions, forward_batch,
                               input_embeds, pp_proxy_tensors=pp_proxy_tensors)  # 539-545 行
    if self.capture_aux_hidden_states:                       # 548-549 行
        hidden_states, aux_hidden_states = hidden_states
    if self.pp_group.is_last_rank:                           # 551 行
        if not get_embedding:
            return self.logits_processor(                    # 553-559 行 ★
                input_ids, hidden_states, self.lm_head, forward_batch, aux_hidden_states)
        else:
            return self.pooler(hidden_states, forward_batch) # 561 行
    else:
        return hidden_states                                 # 563 行（即 PPProxyTensors）
```

统一签名 `(input_ids, positions, forward_batch, **kwargs)` 是 SGLang 对所有 200+ 模型的硬性协议——ModelRunner 用 `inspect.signature(self.model.forward).parameters` 探测可选参数（model_runner.py:569/2711-2712 行），而不是为每个模型写分支。

**forward_split_prefill（565-604 行）**：PD 多路复用（`ForwardMode.SPLIT_PREFILL`）的专用入口。与普通 forward 的区别是：中间态 `hidden_states/residual` 不走返回值，而是**存在 forward_batch 上**（578-596 行，`forward_batch.hidden_states`/`forward_batch.residual`，对应 forward_batch_info.py:414-418 行的字段），使一次 prefill 可以拆成多次调度片段执行，`split_interval=[start,end)` 指定本次跑哪些层。

**权重加载 load_weights（630-701 行）**——静态权重世界的"翻译器"：

1. 643-646 行：AWQ 风格的 `.activation_scale`→`.input_scale`、`.weight_scale_inv`→`.weight_scale` 改名；
2. 648-657 行：PP 场景跳过不属于自己的层（`layer_id < start_layer or >= end_layer`）；
3. 658-663 行：丢弃 `rotary_emb.inv_freq/cos_cached/sin_cached`（RoPE 表运行时自算）和 vision tower 残留；
4. 666-667 行：tie embeddings 时跳过 `lm_head.weight`；
5. 669-672 行：`maybe_remap_kv_scale_name` 处理 FP8 KV scale 的各种历史命名；
6. 674-686 行核心循环：命中 `stacked_params_mapping` 的权重改名后调 `param.weight_loader(param, loaded_weight, shard_id)`——**融合矩阵的 TP 切块逻辑由参数对象自带的 weight_loader 完成**（它知道自己该取 loaded_weight 的哪个行区间）；
7. 687-701 行：普通权重直接 load；查无此参则 warning（容忍噪声 checkpoint）。

### 1.7 forward 全流程：ForwardBatch 如何驱动一层 Transformer

先澄清一个版本演进点：**早期 SGLang 的模型文件里有 `forward_native` 与 `forward_cuda_graph` 两个静态方法**，由 ModelRunner 二选一；在当前 commit 已收敛为**单一 `forward`**（本文件 grep 不到任何 `forward_cuda_graph`），因为 CUDA graph 捕获的就是普通调用——cuda_graph_runner.py:453 直接 `torch.no_grad()(model.forward)` 录图。所以现在的分派是两级的：

```
Scheduler.run_batch
  └─ ModelRunner._forward_raw (model_runner.py:3263)
       ├─ 发布 ForwardContext(attn_backend=self.attn_backend)   # 3274-3277 行
       ├─ 第一级：graph vs eager（3284-3308 行）
       │    can_run_graph = mode.is_cuda_graph() and graph_runner.can_run(batch)
       │    ├─ True  → graph_runner.replay(forward_batch)        # 3303 行，重放解码图
       │    └─ False → 按 forward_mode 走 eager 分支（3338-3361 行）
       │         ├─ DECODE        → forward_decode  (3008 行)
       │         ├─ SPLIT_PREFILL → forward_split_prefill (3131+ 行, 调 1.6 的方法)
       │         ├─ EXTEND/...    → forward_extend  (3057 行)
       │         │     └─ 内部先问 piecewise_cuda_graph_runner.can_run() (3086-3100 行)
       │         └─ IDLE          → forward_idle   (3125 行，DP attention 空转 rank)
       └─ 每个 eager 分支都先 attn_backend.init_forward_metadata(forward_batch)
          (3028/3109 行) 再 self.model.forward(input_ids, positions, forward_batch, **kwargs)
          (3042/3117 行)
```

`is_cuda_graph()`（forward_batch_info.py:161-167 行）= DECODE / TARGET_VERIFY / IDLE / DLLM_EXTEND——即**所有"每序列 token 数固定"的模式**都能进图；变长的 prefill 永远 eager（或走 piecewise 图把 attention 段切出去）。

为方便对照分派逻辑，把 `ForwardMode` 十个枚举值（forward_batch_info.py:75-101 行）与它们的归宿整理成表：

| ForwardMode | 含义 | is_extend? | is_decode? | is_cuda_graph? | 典型消费者 |
|---|---|---|---|---|---|
| EXTEND | prefill/chunk 新增段（KV 前缀已算好） | ✓ | | | forward_extend（eager/piecewise） |
| DECODE | 每序列出 1 token | | ✓ | ✓ | forward_decode / graph replay |
| MIXED | chunked prefill 中 EXTEND+DECODE 同批 | ✓ | | | forward_extend（NPU 另有 forward_mixed） |
| IDLE | DP attention 空转 rank | | | ✓ | forward_idle，backend 返回空张量 |
| TARGET_VERIFY | 投机解码 target 批量验证 draft 候选 | ✓ | | ✓ | forward_decode 形态（多查询） |
| DRAFT_EXTEND / DRAFT_EXTEND_V2 | draft 模型扩展 | ✓ | | V2 支持定形输出 | draft worker |
| PREBUILT | PD 分离 decode 端 KV 已就位直接解码 | | | | decode 路径 |
| SPLIT_PREFILL | PD 多路复用把 prefill 按层段拆跑 | ✓ | | | forward_split_prefill（1.6 节） |
| DLLM_EXTEND | 扩散式 LLM 的块式去噪步 | ✓ | | ✓ | logits_processor 的 dllm 分支 |

注意 `is_extend()`（106-115 行）是一个**宽谓词**：EXTEND/MIXED/DRAFT_EXTEND/TARGET_VERIFY/SPLIT_PREFILL/DLLM_EXTEND 都算——因为它们在 RadixAttention 分派里全走 `forward_extend`（base_attn_backend.py:123-132 行的 else 兜底）。模式的语义细分在 ModelRunner 层，attention 层只关心"一序列多 token 还是一 token"。

数据侧，一次 decode 的完整旅程：

```
Scheduler 分配 KV 槽位 → batch.out_cache_loc（token_to_kv_pool 分配器给的槽位号）
ForwardBatch.init_new (forward_batch_info.py:451-674)
  ├─ 7 个必填核心字段 (277-291 行)：forward_mode / batch_size / input_ids /
  │   req_pool_indices / seq_lens / out_cache_loc / seq_lens_sum
  ├─ decode: positions = clamp_position(seq_lens)        # 628-630 行
  ├─ extend: extend_seq_lens/prefix_lens/start_loc 转成 GPU 张量
  │   positions, extend_start_loc = compute_position(...) # 632-651 行
  └─ lora: fetch_new_loras + prepare_lora_batch          # 665-672 行

LlamaForCausalLM.forward
  ├─ embed_tokens(input_ids) → [num_tokens, hidden]      # 词表并行，自动 all-reduce
  ├─ for i in layers: LlamaDecoderLayer.forward
  │    ├─ RMSNorm(x, residual) → (normed, residual')
  │    ├─ qkv_proj → split → rope                         # 1.3 节
  │    ├─ attn(q,k,v,forward_batch) → RadixAttention      # ★ 见 1.8
  │    ├─ o_proj（行并行 all-reduce）
  │    ├─ RMSNorm → mlp（gate_up GEMM → SiluAndMul → down GEMM）
  │    └─ 返回 (hidden', residual')
  ├─ final norm
  └─ logits_processor(input_ids, hidden, lm_head, forward_batch)
       # logits_processor.py:288-359：先 _get_pruned_states 只保留
       # 每序列最后一个 token（decode 时=全部，extend 时=每序列末位），
       # 再 lm_head GEMM —— 避免对整个 prefill 算 vocab 大小 logits
```

### 1.8 attention 层如何调用 attn backend 的 forward_extend/forward_decode

`LlamaAttention.forward` 251 行的 `self.attn(q, k, v, forward_batch)` 落到 RadixAttention.forward（radix_attention.py:106-147）：

```python
# ① reshape 到 [num_tokens, num_kv_heads, head_dim]（115-122 行）
if forward_batch.forward_mode.is_extend() and get_forward_context() is not None:
    # ② 编译/piecewise-graph 路径：注册成 custom op 的统一出口
    unified_attention_with_output(q, k, v, output, save_kv_cache, self.layer_id)  # 134 行
else:
    # ③ 普通路径：直接从 ForwardContext 拿 backend
    return get_attn_backend().forward(q, k, v, self, forward_batch, save_kv_cache)  # 139 行
```

两个要点：

1. **模型不持有 backend 引用**。`get_attn_backend()`（forward_context.py:66-67 行）读的是 ModelRunner 在 `_forward_raw` 里发布的模块级 `ForwardContext`（frozen dataclass，forward_context.py:34-41 行）。这是从旧版"`forward_batch.attn_backend` 字段"演化来的依赖反转——ForwardBatch 现在只装数据，控制面走 ForwardContext（PDmux 每流 backend、TBO 子 batch 等场景用 `dataclasses.replace` 换上下文即可）。
2. `unified_attention_with_output`（150-221 行）被 `@register_custom_op` + `@register_split_op` 双装饰（150-151 行）——为了 torch.compile / piecewise CUDA graph 能把 attention 当作可切分的算子边界；它内部做 `real_num_tokens` 裁剪（176-180 行）、临时收窄 `forward_batch.out_cache_loc`（198-201 行）后同样调 `get_attn_backend().forward`。

然后是 base_attn_backend.py:89-132 行的**模式分派器**（本文件要求重点理解的接口）：

```python
def forward(self, q, k, v, layer, forward_batch, save_kv_cache=True, **kwargs):
    if forward_batch.forward_mode.is_idle():        # 101-102 行
        return q.new_empty(q.shape[0], layer.tp_q_head_num * layer.v_head_dim)  # 空转
    elif forward_batch.forward_mode.is_decode():    # 103-112 行
        return self.forward_decode(q, k, v, layer, forward_batch, ...)
    elif forward_batch.forward_mode.is_mixed() and is_npu():  # 113-122 行
        return self.forward_mixed(...)              # chunked prefill 混合批（NPU 专属）
    else:
        return self.forward_extend(q, k, v, layer, forward_batch, ...)  # 123-132 行
```

`forward_decode`（134-145 行）与 `forward_extend`（147-158 行）是抽象方法，语义差异在于：

| | forward_extend | forward_decode |
|---|---|---|
| q 的 token 数 | 每序列多个（prefill/chunk 新增段） | 每序列 1 个（或 spec 的 k 个） |
| k/v 来源 | 调用方现算的张量 | 同左，但注意力要读**全序列历史 KV** |
| kernel 形态 | 变长、常常带显式 causal mask（`custom_mask`） | 定长 1 查询，split-k/页表索引为主 |
| CUDA graph | 不进整图（piecewise 除外） | 可整图捕获 |

配套接口（base_attn_backend.py）：`init_forward_metadata`（21-24 行，每步 eager 前准备 indptr/indices 等）；`init_cuda_graph_state`（26-28 行）+ `init_forward_metadata_capture_cuda_graph`（30-41 行）+ `init_forward_metadata_replay_cuda_graph`（43-55 行）+ `get_cuda_graph_seq_len_fill_value`（57-59 行，图内 seq_lens 填充值通常 0 或 1）构成图捕放协议；`on_after_cuda_graph_warmup`（61-68 行）等钩子服务投机解码的 verify buffer（70-87 行）。

### 1.9 KV 写入 out_cache_loc 的完整路径

先用一个数值化例子建立直觉。假设 2 个请求：A 已有 3 个 token 的 KV 前缀、本次 extend 2 个新 token；B 已有 1 个前缀、本次 extend 1 个：

```
extend 前的池子状态（token_to_kv_pool 槽位号示意）：
  A 的前缀 KV → 槽 [10, 11, 12]      （此前 chunk 写入过）
  B 的前缀 KV → 槽 [40]

ForwardBatch 携带：
  input_ids        = [a4, a5, b2]                    # 3 个新 token
  seq_lens         = [5, 2]                          # 前缀+新增
  out_cache_loc    = [100, 101, 42]                  # 调度器为 3 个新 token 分配的槽位 ★
  extend_prefix_lens = [3, 1]；extend_seq_lens = [2, 1]
  positions        = [3, 4, 1]                       # compute_position 算出

attention backend 内部：
  kv_indices（读历史） = [10,11,12, 100,101, 40, 42]  # req_to_token 展开后并上本次新槽位
  写入：set_kv_buffer(layer, out_cache_loc=[100,101,42], k, v)
        → k_buffer[100]=k[0], k_buffer[101]=k[1], k_buffer[42]=k[2] ...
  注意 100/101 同时出现在"写入"与"读取"两列——本次新增 token 因果可见
```

下一轮 A、B 各 decode 1 个 token 时：`out_cache_loc=[102, 43]`（新槽），`kv_indices=[10,11,12,100,101,102]` 与 `[40,42,43]`——前一轮写入的 100/101/42 已成为可读历史。

"新算的 k/v 怎么进 cache、旧 cache 怎么被读回"——这条链路贯穿四个模块：

```
① 分配：Scheduler 调 token_to_kv_pool 的分配器，为本次 forward 的每个 token
   申请槽位号 → ScheduleBatch.out_cache_loc
② 携带：ForwardBatch.init_new 521 行原样借用（289 行字段注释：
   "The indices of output tokens in the token_to_kv_pool"）
③ 送达：模型层把它透传给 RadixAttention.forward → backend.forward(...forward_batch)
④ 写入：以 TritonBackend.forward_extend 为例（triton_backend.py:927-1041 行）
     954-982 行：if save_kv_cache:
         self.token_to_kv_pool.set_kv_buffer(
             layer, forward_batch.out_cache_loc, k, v)      # 957-962 行
     # FP8 KV 走 974-982 行带 k_scale/v_scale 的重载（k.clone() 防 in-place 污染）
⑤ 读回（同一次调用内）：1029-1030 行 extend_attention_fwd 直接拿
     token_to_kv_pool.get_key_buffer(layer_id)/get_value_buffer(layer_id)，
     按预先算好的 kv_indices（来自 req_to_token 页表，300-313 行 cumsum+kernel 构建）
     对历史 KV 做变长注意力 —— 写与读共用同一池子，本次写入的 token
     立即可被同 batch 内后续序列位置因果可见
⑥ decode 时：forward_decode（1186 行+）不再需要层内可见性，kv_indices 完全由
     req_to_token[req_pool_indices] 展开（init_forward_metadata 298-313 行）
```

两个精妙细节：

- `save_kv_cache=False` 的存在（RadixAttention.forward 112 行的默认参数之外）是为**跨层/跨模型 KV 共享**（如 MLA 的吸收态、cross-layer sharing、draft 复用 target KV）准备的口子；更极端的是 triton_backend.py:943-950 行：调用方传 `k=None, v=None` 时，backend 反向从池里**读出** k/v 供 attention 使用——"写缓存"的 API 同时也是"懒读缓存"的 API。
- `out_cache_loc` 是**扁平 token 级**索引，而 `req_pool_indices`（ForwardBatch 第 4 个必填字段，285 行）索引的是 `req_to_token` 页表（`[max_reqs, max_context]` 的二维表）。两者的桥就是 decode metadata 构建时的 `create_flashinfer_kv_indices_triton`（305-313 行）：`req_to_token[req, :seq_len]` 展开成注意力要 gather 的 kv 槽位列表。

最后把一次 extend forward 的跨模块时序串起来（谁在什么时候做什么）：

```
Scheduler                    ModelRunner                  模型(llama.py)            RadixAttention/Backend
─────────────────────────────────────────────────────────────────────────────────────────────────────
组批+分配槽位
 ScheduleBatch.out_cache_loc
 → ForwardBatch.init_new ──→ _forward_raw
                              发布 ForwardContext ─────────────────────────────────→ get_attn_backend() 可用
                              attn_backend.init_forward_metadata
                              （indptr/indices/kv_indices 在此算好）
                              model.forward ────────────→ LlamaModel.forward
                                                         embed → layer0..N
                                                         每层 self_attn ───────→ RadixAttention.forward
                                                                                 reshape → backend.forward
                                                                                 → forward_extend
                                                                                   ① set_kv_buffer(out_cache_loc)
                                                                                   ② extend_attention_fwd
                                                                                      (读 kv_buffer 全历史)
                                                         ← hidden_states
                              ← LogitsProcessorOutput ←─ logits_processor
                              （prune 末 token → lm_head → 采样交给上层）
```

注意 metadata 准备（`init_forward_metadata`）**先于** `model.forward` 一次性完成，而非每层重复——这就是为什么模型层可以保持对 backend 零感知：所有 backend 特定状态在进入模型前就已就位。

### 1.10 值得扫一眼的其余方法

- `get_embed_and_head`/`set_embed_and_head`/`set_embed`（776-808 行）：EAGLE 系投机解码的 draft 模型与 target 模型**共享嵌入与 lm_head 权重**（省数 GB 显存）；`set_embed` 里 795-800 行处理 EAGLE3 draft/target hidden size 不等时不可共享的边界。
- `set_eagle3_layers_to_capture`（813-825 行）：默认抓 `[2, L//2, L-3]` 三层输出作 draft 训练特征；823-825 行的 `+1` 偏移注释揭示约定——"第 i 层的 aux hidden 取的是第 i-1 层的输出"，对应 1.5 节 409-410 行在进层前截获。
- `get_weights_by_name`（703-774 行）：按 HF 风格名字反查融合矩阵切片（逆映射 stacked_params_mapping + 手动 narrow），仅单测/兼容用。

---

## 模型注册机制

SGLang 的模型发现是**纯约定式、零中心清单**的：

1. **声明**：llama.py 末尾（852-857 行）

```python
EntryClass = [
    LlamaForCausalLM,
    Phi3ForCausalLM,      # 840-841 行：class Phi3ForCausalLM(LlamaForCausalLM): pass
    InternLM3ForCausalLM, # 844-845 行：同样一行继承
    IQuestCoderForCausalLM,
]
```

   `EntryClass` 可以是单个类，也可以是列表（111-125 行的 registry 代码对两种形态都处理）。这就是为什么 Phi3 等架构能"零成本"挂进来：HF config 里 `architectures: ["Phi3ForCausalLM"]` 精确匹配**类名**。

2. **发现**：registry.py:130-131 行在 import 时执行

```python
ModelRegistry = _ModelRegistry()
ModelRegistry.register("sglang.srt.models")
```

   `import_model_classes`（registry.py:94-127 行）用 `pkgutil.iter_modules` 遍历 `sglang.srt.models` 包的每个模块（98 行），逐个 `importlib.import_module`（105 行，单模块失败仅 warning 不炸全局，104-109 行），收集模块级 `EntryClass` 属性建成 `{类名 → 类}` 字典（111-125 行，重名 assert 防冲突）。环境变量 `SGLANG_DISABLED_MODEL_ARCHS` 可按模块名跳过（100-102 行）；`SGLANG_EXTERNAL_MODEL_PACKAGE` 支持注册外部包（133-134 行，overwrite=True）——插件式扩展模型不需要改 SGLang 源码。

3. **解析**：加载模型时 model_loader/utils.py:195-230 行 `get_model_architecture` 读 `model_config.hf_config.architectures`（198 行）→ `ModelRegistry.resolve_model_cls(architectures)`（223 行，registry.py:80-91 行）。`_normalize_archs`（61-78 行）有个兜底：候选全都不认识时追加 `"TransformersForCausalLM"` 到末尾（75-77 行）——即**任何 HF 模型至少能以 Transformers 后端慢速跑起来**，除非显式指定原生实现。Mixtral 量化模型在此还有个历史 hack（199-214 行，按量化方式改写架构名）。

4. **实例化**：ModelRunner 拿到 `model_cls` 后 `model_cls(config, quant_config, prefix=...)` 构造——这也是为什么所有 `*ForCausalLM` 的 `__init__` 签名必须是 `(config, quant_config, prefix)`。

一句话总结：**registry 认的不是文件名而是类名，模型文件用 `EntryClass` 自我声明，包扫描在 import 期完成一次性发现**。要给 SGLang 加新模型，往 `srt/models/` 丢一个定义了 `EntryClass` 的文件即可。

---

## 与其他模块的交互

| 交互对象 | 接口点 | 方向与内容 |
|---|---|---|
| `Scheduler`/`ScheduleBatch` | `ForwardBatch.init_new`（forward_batch_info.py:451） | 调度器把 CPU 侧决策（批组成、槽位分配、模式）物化为 GPU 张量批；模型只见 ForwardBatch |
| `ModelRunner` | `model.forward(input_ids, positions, forward_batch, **kwargs)`（model_runner.py:3042/3117） | 运行器负责 backend 选型（2246-2254 行）、metadata 初始化、图捕放、LoRA 管理（1999 行）；对模型只暴露统一 forward |
| `ForwardContext` | `get_attn_backend()`（forward_context.py:66） | 模型深处（RadixAttention）反向解析控制面；替代了旧版 ForwardBatch.attn_backend 字段 |
| `AttentionBackend` 各实现 | `forward_decode`/`forward_extend` + `init_forward_metadata`（base_attn_backend.py:21/134/147） | 模型递 q/k/v，backend 负责写读 KV 池并做注意力 |
| `mem_cache`（token_to_kv_pool / req_to_token_pool） | `set_kv_buffer(layer, out_cache_loc, k, v)`（triton_backend.py:957） | 层的 `layer_id` 索引到池的第 N 层 buffer；`k_scale/v_scale` 挂在 RadixAttention 上由标定回填（llama.py:437-456） |
| `distributed`（TP/PP） | `QKVParallelLinear`/`RowParallelLinear` 内部 all-reduce；`get_pp_group`/`get_pp_indices`/`PPProxyTensors`（llama.py:28-33/350-378/419-425） | 模型只声明并行意图，通信细节封装在线性层与 pp_group |
| `model_loader` | `load_weights`（630 行）+ `stacked_params_mapping`；`get_model_architecture`（utils.py:195） | HF 权重名 → 融合参数的翻译；registry 解析在这层触发 |
| `lora`（LoRAManager） | `set_lora_module`→`replace_submodule`（lora_manager.py:715-719）；`ForwardBatch.lora_ids`（fbi.py:371/558/665-672） | 构造后模块替换注入；运行期按请求选 adapter |
| `speculative`（EAGLE/MTP） | `capture_aux_hidden_states`/`layers_to_capture`（519/813-837）；`get_embed_and_head`（776）；`ForwardMode.TARGET_VERIFY/DRAFT_EXTEND` | target 模型暴露中间层特征与嵌入权重给 draft；spec 模式改变 forward 分派 |
| `layers/quantization` | `quant_config` 透传（179/187/204 行） | 线性层与 RadixAttention 各自 get_quant_method，FP8 KV 标定走 load_kv_cache_scales |
| `piecewise/breakable cuda graph` | `unified_attention_with_output` 注册 custom op/split op（radix_attention.py:150-151） | attention 作为图切分边界；`forward_split_prefill`（565 行）服务 PD 多路复用 |

---

## 关键设计决策

1. **单一 forward 签名，消灭 forward_native/forward_cuda_graph 双入口**。旧版模型要写两份 forward（图捕版本绕过 Python 副作用），当前设计让 CUDA graph 捕获的就是普通 `model.forward`（cuda_graph_runner.py:453），模型完全无感。代价是 forward 必须满足图友约束：无数据依赖的 Python 分支、输入输出都来自预分配 buffer。收益是**新增模型自动获得图加速**，200+ 模型不用各写一遍。模式分派下沉到 backend 层（base_attn_backend.py:101-132 行的 idle/decode/mixed/extend 四路），forward_mode 成为贯穿全栈的"单一定位信标"（forward_batch_info.py:75-186 行的一组 `is_*` 谓词）。

2. **注意力反转依赖：模型 = 插座，backend = 插头，ForwardContext = 总线**。模型文件里没有任何 `if backend == "flashinfer"`；RadixAttention 只带元数据，运行期经 `get_attn_backend()`（forward_context.py:66）拿到当次 forward 生效的 backend 实例。这使同一份 llama.py 能按部署环境换 Triton/FlashInfer/FA3/Wave/CUTLASS-MLA，也让 PDmux（每流一个 backend 组，model_runner.py:2246-2250）和 TBO（双批重叠）无需模型配合。frozen dataclass 的 ForwardContext 保证上下文不被误改，需要换backend时用 `dataclasses.replace` 明确开新作用域。

3. **KV 写入责任下放 backend，`out_cache_loc` 是唯一契约**。模型层从不触碰 cache 布局；调度器分配槽位、ForwardBatch 携带、backend 执行 `set_kv_buffer`。好处有三：① 换 page/block/paged-hybrid 池型（MHATokenToKVPool/SWA 池/MLA 池）不动模型代码；② `save_kv_cache=False` + "k 为 None 则从池读"（triton_backend.py:943-950 行）天然支持跨层共享与投机解码复用；③ 写入与读取同池同批可见，extend kernel 一遍完成"写新读旧"。（用户资料中提到的 `pass_ut_cache_layout` 在本 commit 已查无此标识——相关布局协商逻辑已收敛进各 backend 的 metadata 构建，特此注明避免误导。）

4. **权重加载即重映射：`stacked_params_mapping` + `param.weight_loader` 两级翻译**。HF checkpoint 的 `.q_proj/.k_proj/.v_proj` 三矩阵在加载期改名进 `.qkv_proj` 融合参数（674-686 行），行区间切分由参数对象自带的 `weight_loader(param, loaded_weight, shard_id)` 完成——TP rank 拿哪一段、GQA 复制哪种头，全是线性层构造参数自描述的。这把"计算布局优化"（融合 GEMM）与"存储格式兼容"（HF 标准）解耦：布局怎么变，加载器跟着参数对象走，模型 forward 不掺和。同名双表（类级 bitsandbytes 表 476-483 行 + 加载期局部表 631-638 行）是历史包袱的诚实呈现。

5. **DP attention 的"双口径 TP"**：注意力计算在小的 attn-TP 组内做、MLP 仍在全 TP 组内做，以在长序列场景把注意力的显存/通信压力按 DP 维切分。样板里的接缝清晰可见：`LlamaMLP.down_proj(use_dp_attention_reduce=...)`（82/103 行）→ RowParallelLinear 的 all-reduce 改走 `get_attention_tp_group()`（linear.py:1544-1545 行）；LM head 可切到 attn 组（`enable_dp_lm_head`，llama.py:506 行，logits_processor.py:256-262 行）；token 流进出 DP rank 用 `dp_gather_partial/dp_scatter`（dp_attention.py:534-558 行）+ ForwardBatch 的 `global_num_tokens_*`/`dp_padding_mode` 字段组（fbi.py:394-400/427-433 行）；没分到序列的 rank 以 `ForwardMode.IDLE` 空转（fbi.py:84 行，backend 直接返回空张量，base_attn_backend.py:101-102 行），保证集合通信全员到齐。**llama.py 本身几乎不为 DP 写代码**——样板示范了"并行策略生长在层工厂参数与 ForwardBatch 字段里，而非模型逻辑里"。

（次级决策，扫读即可：tie_word_embeddings 直接共享 Python 对象而非拷贝权重（498-499 行）；EAGLE3 的 `+1` 层偏移语义（823-825 行）；NPU 融合核只替换 prepare 段不动接口（214-227 行）；`input_embeds` 参数是多模态/嵌入替换的统一注入口（391/535 行 + fbi.py:312-315 行）。）

---

## 阅读建议

**读 llama.py 的正确姿势**：先 1.7 的调用链图自顶向下走一遍 decode，再带着三个问题精读——① residual 为什么是独立张量（答：fused RMSNorm + PP 传递）；② attention 计算到底发生在哪个文件（答：不在模型文件，在 backend，经 ForwardContext 间接调用）；③ 一个 token 的 KV 从产生到被读隔了多少行代码（答：从 `self.attn(...)` 到 `set_kv_buffer`，中间跨 3 个模块）。

**进阶路线（按依赖增量排序）**：

1. `qwen2.py` —— 最小 diff 的姊妹篇（~+50 行差异）：QK-norm、双 rope 配置、不同的 attention_bias 处理。用 diff 读，体会"变奏"的含义。
2. `llama_eagle.py` —— 换个身份看同一骨架：作为 draft 模型如何复用 target 的 embed/lm_head（对照 776-808 行）、如何消费 aux hidden states。
3. `mixtral.py` —— 只动 MLP：把 `LlamaMLP` 换成 MoE 层，看 router/专家并行如何嵌入同一模板。
4. `llama_classification.py` —— `Pooler`/`get_embedding=True` 路径（551-561 行）的完整用法，embedding 任务的样板。
5. `deepseek_v2.py`（终局目标）—— 三重跃迁：MLA 取代 MHA（KV 变成低秩 latent + `k_rope` 解耦，RadixAttention 的 kwargs 通道开始承重）、`wkv_a/wkv_b` 更复杂的权重重映射、absorb 模式下 q/k/v 投影的形态切换；配套读 `attention/mla_backend` 系与 `dsa_backend.py`（稀疏注意力 indexer，base_attn_backend.py:176-182 行 `get_indexer_metadata` 的真正用户）。读完它，NSA/MTP/DeepSeek-V3/V4 的增量就都是小步了。

**自测三问**（能不查代码回答即毕业）：① TP=4、num_kv_heads=8 时每 rank 几个 KV 头？TP=16 时呢？（152-160 行）② `forward_split_prefill` 为什么必须把中间态存在 forward_batch 上而不是返回值里？③ 一个 `EntryClass=[Foo]` 的新文件要被 registry 发现，最低要求是什么？（答：位于 `sglang.srt.models` 包内且模块 import 不抛异常，registry.py:98-109 行）

---

## 附录：核心类/方法 → 行号速查表

**llama.py（857 行）**

| 对象 | 行号 | 一句话 |
|---|---|---|
| `LlamaMLP` | 71-124 | gate_up 融合 + SiluAndMul + down_proj |
| `LlamaMLP.forward` | 112-124 | `use_reduce_scatter`→`skip_all_reduce` |
| `LlamaAttention` | 127-253 | qkv 融合投影 + rope 插座 + RadixAttention |
| TP 头切分 | 147-160 | GQA 头少于 TP 数则复制 |
| `forward_prepare_native` | 208-212 | qkv GEMM → split → rope(q,k) |
| `forward_prepare_npu` | 214-227 | NPU 融合核 split_qkv_rmsnorm_rope |
| `LlamaAttention.forward` | 229-253 | 251 行 `self.attn(q,k,v,forward_batch)` |
| `LlamaDecoderLayer.forward` | 314-336 | fused RMSNorm 双值 residual 流转 |
| `LlamaModel` | 339-461 | PP 切分 + make_layers + 层循环 |
| `LlamaModel.forward` | 386-432 | embed→layers→norm / PPProxyTensors |
| `load_kv_cache_scales` | 437-456 | FP8 KV 标定 → attn.k_scale/v_scale |
| `LlamaForCausalLM.__init__` | 485-519 | tie_word_embeddings / logits_processor / pooler / stacked_params_mapping |
| `LlamaForCausalLM.forward` | 529-563 | 统一签名中枢：logits or pooler or PP 中间态 |
| `forward_split_prefill` | 565-604 | SPLIT_PREFILL 逐层段执行，中间态挂 forward_batch |
| `load_weights` | 630-701 | 权重名翻译 + 分片 weight_loader |
| `get_embed_and_head` / `set_embed*` | 776-808 | EAGLE draft/target 权重共享 |
| `set_eagle3_layers_to_capture` | 813-825 | 默认抓 [2, L//2, L-3] 层，+1 偏移约定 |
| `EntryClass` | 852-857 | 注册声明：4 个架构名 |

**辅助模块**

| 模块 | 对象 | 行号 |
|---|---|---|
| base_attn_backend.py | `AttentionBackend.forward` 分派器 | 89-132（idle 101 / decode 103 / mixed 113 / extend 123） |
| base_attn_backend.py | `init_forward_metadata` / cuda-graph 四件套 | 21-24 / 26-59 |
| forward_batch_info.py | `ForwardMode` + 谓词 | 75-186 |
| forward_batch_info.py | `ForwardBatch` 7 必填字段 | 277-291（out_cache_loc=289） |
| forward_batch_info.py | `init_new` | 451-674（decode positions 628-630 / extend 632-651 / lora 665-672） |
| radix_attention.py | `RadixAttention.forward` | 106-147（custom op 路径 124-137 / backend 路径 139-147） |
| radix_attention.py | `unified_attention_with_output` | 150-221 |
| forward_context.py | `ForwardContext` / `get_attn_backend` | 34-41 / 66-67 |
| registry.py | `import_model_classes` / `resolve_model_cls` / 注册 | 94-127 / 80-91 / 130-134 |
| model_loader/utils.py | `get_model_architecture` | 195-230 |
| model_runner.py | LoRA manager / backend 选型 / `_forward_raw` 分派 / `forward_extend` | 1999 / 2246-2254 / 3263-3367 / 3057-3123 |
| cuda_graph_runner.py | 捕获即普通调用 | 453 / 460 |
| triton_backend.py | `forward_extend`（set_kv_buffer）/ `forward_decode` / metadata | 927-1041（955-982）/ 1186+ / 286-330 |
| lora_manager.py | `set_lora_module`（replace_submodule） | 715-719 |

---

*附：本文引用行号的源文件版本——llama.py(857 行) / base_attn_backend.py(182 行) / forward_batch_info.py(1279 行) / radix_attention.py(224 行) / registry.py(134 行) / model_runner.py(3570 行) / triton_backend.py(1566 行)，均 @ commit ec075d8bc。*
