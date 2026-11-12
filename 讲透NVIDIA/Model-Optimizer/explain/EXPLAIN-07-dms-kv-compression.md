# EXPLAIN-07 · experimental/dms：可学习 KV 逐出策略（Dynamic Memory Sparsification）

## 一、角色定位

`experimental/dms` 是独立实验线：把 **KV cache 逐出策略从手工规则变成可学习参数**。出处 NeurIPS 2025（arXiv 2506.05345，README.md:3-8）。动机：推理时扩展瓶颈常在 KV cache 体积，DMS 学 per-head 逐出策略，压 cache 保精度（README.md:10-14）。卖点（README.md:18-21）：8× 压缩精度损失极小；默认只训逐出 adapter 冻结底座；Qwen3-8B 约 250 步 / 8×H100 四小时。边界（README.md:117、:119）：仅 adapter 训练（全参 recipe 计划支持）；推理仅单轮 prefill→generate，多轮走慢速 fallback。

## 二、内部结构

四层目录：`dms/` 核心库（core/attention/attention_prefill/cache/cache_paged/training）、`models/qwen3/` 适配、`configs/` 两 YAML、`scripts/` 三个 shell，与 README.md:87-111 结构图一致（实测 find 无出入）。

**逐出决策两条路线**（ARCHITECTURE.md:9-12）：

1. **单神经元**（`dms_separate_alpha=False`，DMC 论文 §3.1）：决策 logits 取 query 最后一维——core.py:165-168 的 `query_states[:, ::gqa_factor, :, -1] * scale - offset`；core.py:173/:175 两处置零再过 RoPE 防干扰。零新增参数，但要底座"腾"一个维度当决策器。
2. **学习型 adapter**（`separate_alpha=True`，本论文 §3.2）：新增 `dms_proj_alpha`（hidden→num_kv_heads）+ RMSNorm（core.py:180-188，modeling_qwen3_dms.py:88-92），决策来自 pre-attn-norm hidden states，与主干解耦。

粒度 `dms_alpha_per`（configuration_qwen3_dms.py:49）：`"head"` 各 head 独立（cache 长度可不同）/`"layer"` 层内共享，core.py:204-211 用 broadcast 统一形状。**可导化**是方法论核心：决策是 0/1 开关不可导，训练态用 Gumbel 门控——`get_gating_with_noise`（core.py:242-253）logits 加噪除 τ 过 sigmoid，straight-through 估计器（core.py:251）前向离散反向可导；推理态退化硬阈值（core.py:199）；teacher 模式强制全保留（core.py:217-219 decisions 清零、logits 填 -1000）。

## 三、外部连接

- **transformers**：`Qwen3ForCausalLMDMS`（modeling_qwen3_dms.py:362）继承 PreTrainedModel+GenerationMixin；`Qwen3AttentionDMS` 只改 forward（:73）；`Qwen3ConfigDMS`（configuration_qwen3_dms.py:37）扩展 Qwen3Config，`dms_*` 参数可经 from_pretrained 注入。
- **flash-attn**：推理态用 `flash_attn_with_kvcache`（attention.py:33 导入，:230-240 带 block_table 分页寻址）。
- **FlexAttention**：训练与 prefill 都走 flex_attention（attention.py:22、attention_prefill.py:21），prefill 要求 `return_aux=AuxRequest(lse=True)`（attention_prefill.py:156）。
- **训练栈**：accelerate + HF Trainer + FSDP（qwen3_8b.yaml:57 `full_shard offload`），数据 blend 走 training/data.py，评测 RULER。
- 独立 pyproject 单独安装（README.md:44），不依赖 `modelopt/` 主包——实验区不污染主库。

## 四、数据流

**训练态**（dms_cache 为 None，attention.py:67 分派）：`prepare_attention_input`（core.py:120，@torch.compile）算 Q/K/V+决策，训练态加 Gumbel 噪声（core.py:192-197）；`dms_attn_train_mode`（attention.py:105）把决策 logits 右移一位补零（attention.py:139——token i 的逐出由 token i+1 判断），转 `logsigmoid(-logits)` 软惩罚入分；score_mod（attention.py:146-157）实现"滑窗内正常 + 窗外软门控 + 因果掩码 -50000（attention.py:102）"，flex 被 torch.compile 包裹（attention.py:159）。损失：`distillation_loss`（engine.py:348）学生/教师 logits forward KL，按 vocab_chunk 分块省显存（engine.py:374-385），叠加 DMS 压缩损失（ARCHITECTURE.md:27）。课程表 `dms_schedule`（engine.py:222）把 cr 从 initial 线性推到 final，`target=1-1/cr`（engine.py:240-244）；qwen3_8b.yaml:21-23 配 1.0→16.0、510 步。

**推理态两相**：Prefill 相（attention.py:245）走 `dms_prefill_flex`（attention_prefill.py:188）——构造 FlashMask 风格 compressed_attention_mask（逐出项设 `pos+window`，:331-349，明言不支持 gaps）；注意力分两路：contiguous 近期段走 flex（:359-366），分页段走 flash-attn 要回 LSE（:373-384），重加权精确合并（:400-421）；`rewrite_cache_in_left_padding_style`（:34）用 scatter 把逐出 KV 压实成左 padding（:84-93）。Generate 相：新 token 先 update 进分页 cache（attention.py:220-228），再 flash_attn 读 block table（:230-240）；seq_len==1 且 cache 非空自动切 inference_mode（core.py:311-328）。

**分页 cache**：`DMSPagedCacheLayer`（cache_paged.py:460，**实测 1054 行——勘误：任务书称 874**）默认 block_size=256（:467），约束 `block_size<=window`（:474）；块表按 1.5 因子扩容（:563-611），可预分配（ARCHITECTURE.md:45-49）。`DMSCombinedCacheLayer`（cache.py:167）组合 contiguous+paged，`Mode` 枚举（cache.py:159）管状态机。**分块 prefill**（core.py:287）切长输入逐段过 decoder（:330-331、:344-377），降峰值显存（ARCHITECTURE.md:35-41）。

## 五、设计决策

1. **Gumbel straight-through 而非连续松弛**：前向保持真 0/1，训练推理行为一致；噪声种子由 `process_index+grad_acc_step+current_step` 决定（engine.py:211-217，fork_rng 隔离），FSDP 多卡各副本独立可复现，断点续训与噪声对齐（ARCHITECTURE.md:128-130）。
2. **决策移位一位**（attention.py:139、attention_prefill.py:274-277）：最后 token 永不逐出，逐出是滞后决策=延迟合并表示（README.md:14）。
3. **eviction_info 三态**（attention_prefill.py:282）：0 保留/1 DMS 逐出/2 mask padding，数据 padding 与模型决策统一进同一 rewrite 管线。
4. **训练 Flex / 推理 Flash 双态**：训练要 score_mod 表达软门控，推理要 paged KV 硬件路径；prefill 的 LSE 合并保证软→硬切换注意力数学精确。
5. **adapter-only 训练**（engine.py:76 过滤）比全参便宜约两个数量级（README.md:117），开源版对论文的务实降级。
6. **`dms_cr` 仅文档字段**（configuration_qwen3_dms.py:64）：实际压缩比由课程表决定，改 config 不改压缩率。
7. **每层独立 compile**（core.py:119、:224）层多撞 dynamo 缓存上限，故有 `setup_compile_limit_for_dms(72)`（core.py:37）。

## 六、新人提示

- 跑通顺序：先 `scripts/train_small_debug.sh`（README.md:51 单卡调试）再上 8 卡；train.sh 先单进程备数据再 accelerate 拉起（scripts/train.sh:24-29）。
- 主旋钮在 qwen3_8b.yaml:14-23：`separate_alpha: true`（:18）=adapter 路线；`alpha_per: head`（:19）；`tau: 0.1`（:20）；final_cr 16（:22）。复刻单神经元方案改 separate_alpha=false。
- **YAML 键与 config 参数名有映射差**：yaml `alpha_scale/window_size` vs config `dms_alpha_scale/dms_window_size`（configuration_qwen3_dms.py:42-54），别拿 yaml 键直接 grep config。
- 多轮对话是已知短板（README.md:119），agent 应用先看 example_inference.ipynb。
- 加载产物必须装 dms 包（README.md:81），跨环境别只拷权重。
- 新模型族照 ARCHITECTURE.md:63-72 四步接入，核心算子模型无关，模型侧只需供 Q/K/V 与 norm。
- 断言极多是有意的（如 core.py:169-171）：改张量布局让断言先报错，比静默错位好查。
