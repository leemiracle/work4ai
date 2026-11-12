# 04 · Hybrid 混合架构——Mamba/GDN/GDP 三大 mixer 与推理脚手架

> 主战场：`megatron/core/ssm/`（21 文件 5286 行）+ `megatron/core/models/hybrid/` + `models/mamba/` 兼容 shim 层。知识图谱：HybridModel 是「解析 hybrid_layer_pattern 组装 HybridStack，MTP/mHC/hash-MoE 校验/细粒度卸载/推理 CUDA Graph」的混合语言模型主类。

## ① 角色定位：这个子系统解决什么问题

纯注意力模型的 KV cache 随上下文线性膨胀，而线性注意力/SSM 族（Mamba2、Gated Delta Net、Gated Delta Product）用固定大小的递归状态换掉了 KV cache——代价是召回能力弱。2025-2026 代的答案（Qwen3-Next、Falcon-H1、Samba 等）是**混合堆叠**：大部分层用 SSM mixer，少量层保留注意力。mcore 的 hybrid 子系统解决三件事：①用一个**模式串 DSL** 把"第几层是什么"声明清楚（`"M-M-|M-M*-"`，含 PP 边界与 MTP 段）；②把三种 mixer 统一在同一套训练与推理接口下；③给所有"携带递归状态而非 KV cache"的 mixer 提供**动态批推理的共享脚手架**——decode 与 prefill 分区、投机解码状态快照、状态槽位分配，这些控制流与 mixer 种类无关。

## ② 内部结构：关键类/函数与行号锚

**三大 mixer**，继承签名完全一致 `(SSMDynamicInferenceMixin, MegatronModule, TwoStageAttentionLayer)`：
- `MambaMixer`（`ssm/mamba_mixer.py:144`，1531 行；构造参数 docstring 从 d_model 到 chunk_size 共 30 余项）；
- `GatedDeltaNet`（`ssm/gated_delta_net/gdn.py:70`，基类 `_GDNBase` 在 `gated_delta_net/common.py:94`）；关键配置在 `_setup_variant_attrs`（gdn.py:72）：in_proj 按六段切分 `["query","key","value","z","beta","alpha"]`（:91-99，供 CP head 置换与 sharded checkpoint 共用）；`deterministic_mode` 时换 `torch_chunk_gated_delta_rule`（:100-105），且与 pre-GDR 融合互斥（:78-84 的 ValueError："Pre-GDR fusion is non-deterministic"）；
- `GatedDeltaProductMixer`（`ssm/gated_delta_product.py:170`，1728 行，目录最大）。其方法布局是两阶段注意力的典型：`forward_pre_attn_and_core_attn`（:512）/`forward_post_core_attn`（:526）/`forward`（:530）；推理钩子 `ssm_decode`（:1127）/`ssm_prefill`（:1230）；状态管理 `allocate_inference_cache`（:1378）/`mamba_state_shapes_per_request`（:1399）/`_get_states_from_cache`（:1416）；checkpoint 侧有整套 in_proj/conv 的分片布局函数（`_get_in_proj_checkpoint_split_layout` :1631、`_get_conv_checkpoint_split_layout` :1654）。

注意 **GDN2 是例外**：`GatedDeltaNet2(_GDNBase)`（`gdn2.py:40`）**不带 mixin**，gdn2.py:179 直接 assert "GDN2 does not currently support dynamic inference batching."——新变体还没接上动态推理线。

**推理脚手架 `SSMDynamicInferenceMixin`（`ssm/ssm_inference.py:132`）**：模块 docstring（:3-50）就是设计文档——六步控制流：①从 context 取本层 (conv_state, ssm_state) 槽位 →②in_proj →③把 packed batch 切成 **decode 分区（每请求 1 token，放前面）与 prefill 分区（变长，放后面）**（kernel 不能混跑）→④分别跑两个钩子 →⑤按 packed 顺序合并 →⑥out_proj。"Only the kernels in step 4 differ between variants"——mixin 拥有共享控制流，变体只实现 `ssm_decode`/`ssm_prefill` 两钩子。钩子直接拿 `DynamicInferenceContext`，从 `context.mamba_metadata`/`mamba_slot_allocator` 自取元数据，**故意不做"解包成长参数列表"的中间层**。静态批（legacy）推理明确不进此接口。文件里还有 `ssm_chunking`（:76）按层类型表推导分块策略。

**GDP 内核 fork（`ssm/ops/gdp/`，12 文件）**：`__init__.py` docstring 钉死身份——"Inference-only fork of the Gated Delta Product kernels from flash-linear-attention (v0.5.1)。训练与静态批推理走 pip 的 fla 包（它拥有 backward），只有动态批 decode/prefill 路由到这里，**所有入口 forward-only**"。三个入口：`fused_recurrent_gated_delta_rule_update`（decode）、`gdp_decode_prepare`（decode 前置重塑/门控，一个 Triton kernel 全做完，且"aims to be bitwise identical to the eager path"）、`chunk_gated_delta_product_varlen`（prefill）。`chunk.py` docstring 给出四段 prefill 流水（log decays 交错累加 → WY 表示 → 块间状态递推 → 块内注意力合并），并强调**双 chunking 陷阱**：query/output 在 token 流，key/value/beta 在 Householder 展开流（M 倍长），`ceil(L*M/64) ≠ M*ceil(L/64)`。`fused_recurrent.py` 头注释讲投机解码：单 token 折叠成 M 长序列（query 放最后一份），S 个 draft token → S*M 折叠长度，`intermediate_states` 每 draft token 快照一次递归状态供验证回滚——"Mamba2 selective_state_update 的 intermediate_ssm_states dump 的直接类似物"。

**模型层与模式串（`models/hybrid/`）**：`HybridModel`（hybrid_model.py:104，LanguageModule+GraphableMegatronModule）接受 `hybrid_layer_pattern`（格式 `"<main>/<mtp>/<mtp>..."`，`|` 定 PP 边界，例："M-M-|M-M*-" 即 2 段 fVPP）；构造里依次：`pattern_from_ratios` 兼容旧 ratio 参数（:237 附近）、解析层分配（:246）、校验 TP 通信重叠（:317，本 rank 是否建 MTP 确定后）、最后 `self.decoder = build_module(...)`（:385）。解析器全家在 `hybrid_layer_allocation.py`：`parse_hybrid_pattern`/`_validate_pattern`/`validate_segment_layers`/`select_pipeline_segment`（按 PP rank+VP stage 选段）/`get_layer_maps_from_layer_type_list`（全局↔各类型层索引映射）。

**兼容 shim 层（models/mamba→models/hybrid 迁移）**：三层新旧映射全是 star re-export——`ssm/mamba_hybrid_layer_allocation.py`（5 行→hybrid_layer_allocation）、`ssm/mamba_block.py`（5 行→hybrid_block）、`models/mamba/mamba_layer_specs.py`→hybrid_layer_specs。`models/mamba/mamba_model.py:16` 的 `MambaModel(HybridModel)` 是活的 deprecated 包装：log 警告 "MambaModel has been deprecated. Use HybridModel instead."（:17-19），把弃用的 `mamba_stack_spec` 换名塞进 `hybrid_stack_spec`（:20-26）。

## ③ 外部连接：与哪些子系统互依

最强的一条边指向第 05 篇的推理引擎：mixin 直接 import `DynamicInferenceContext` 与 `triton.tensor_ops` 的 `tensor_get_slice_after`/`tensor_merge`（ssm_inference.py:60-66）——SSM 推理就是动态引擎的一等公民，`context.mamba_metadata`/`mamba_slot_allocator` 是引擎专门为 SSM 层维护的槽位分配器（HybridModel 的图谱 summary 也点了"推理 CUDA Graph"）。第二条边连第 03 篇：Symbols 词表与 `create_layer_config` 由 hybrid 层分配调用，Mamba/GDN 与 CSA/HCA 共存于同一模式串；`models/hybrid/layers/` 下还有 `hybrid_hyper_connection.py` 的 `HyperConnectionHybridLayer`，mHC 残差流对 mixer 层同样生效。第三条边连第 01 篇并行基座：CP 方向有专门的 `mamba_context_parallel.py`（434 行）与 `gdp_context_parallel.py`（342 行）——SSM 的 CP 交换的是递归状态而非 KV，不能复用注意力的 CP 路径。训练侧连 pipeline_parallel（`|` 段与 fVPP 布局）与 dist_checkpointing（GDP 的 sharded_state_dict 分片布局）。外围：`ops/mamba2/`（ssd_* 内核族）、`ops/common/causal_conv1d_triton.py`、`triton_cache_manager.py:31`（`ParallelFileCacheManager`，多进程安全缓存编译产物）。

## ④ 数据流：一次典型调用的路径

动态批推理一步（假设 batch 里 3 个请求在 decode、2 个在 prefill，GDP 层）：

1. 引擎调度到该层，`ssm_dynamic_inference`（ssm_inference.py:190）启动：从 `DynamicInferenceContext` 按本层 id 取 (conv_state, ssm_state) 槽位 slab。
2. packed 输入过 `in_proj`；按引擎给的元数据把序列切成 decode 分区（3 token 在前）与 prefill 分区（变长在后）。
3. decode 分区：`gdp_decode_prepare` 一次 Triton kernel 完成短卷积后重塑/门控 → `fused_recurrent_gated_delta_rule_update` 跑递推；若本步带 MTP 投机的 S 个 draft token，状态每 token 快照一次。
4. prefill 分区：`chunk_gated_delta_product_varlen` 走四段 chunked 流水，产出输出与终态。
5. `tensor_merge` 按 packed 顺序合并两分区；新状态写回槽位（验证失败回滚到快照）；`out_proj` 出层。
6. 训练路径则完全不同：走 pip `fla` 包的带 backward 内核（`chunk_gated_delta_rule` 等），由 `forward`/`_gdp_chunk_forward`（gated_delta_product.py:625）编排。

## ⑤ 设计决策：为什么这么设计

**为什么 fork 一份 forward-only 的 fla 内核而不是直接依赖 pip 包？** `ops/gdp/__init__.py` 说得直白：动态批需要的变长/折叠/快照语义（S*M 折叠、intermediate_states）上游 fla 没有，而 mcore 只需要 forward——**不需要拖上整个 backward**。fork 点锁定 v0.5.1，MIT 许可保留原作者版权头（chunk.py:1-3）。训练继续用上游包，等于"训练用社区版、推理用自维护版"的分叉策略（推断：这也是 graph 甄别里 dead-shim 反模式的对立面——这里每个 shim 都标注了 canonical 位置）。

**为什么钩子直接拿 context 而不做中间参数层？** ssm_inference.py:44-46 明说 "deliberately no intermediate 'unpack the metadata into a long argument list' layer"——mamba_metadata 字段在快速演进，每加一个字段就改一遍所有签名会拖死变体开发。代价是钩子与 context 结构强耦合，但变体数量少（三个），收益大于代价。

**为什么 decode 分区放在 packed 序列前面？** （推断）decode 是每步都发生的热路径且长度固定为 batch 大小，放前面让 kernel 的 launch 形状稳定、也便于 CUDA graph 捕获；prefill 变长放后面隔离形状抖动。

**为什么旧路径全是 star re-export shim？** models/mamba→models/hybrid 是一次**目录级重命名式迁移**：外部脚本（pretrain_mamba.py 还在仓根）import 旧路径必须继续工作。shim 文件里只留 5 行注释指路 canonical 位置，让 grep 可追踪。这与 MambaModel 的"活的弃用警告"配套，是教科书式的渐进迁移。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`ssm_inference.py` 的模块 docstring（:3-50，全篇最好的设计文档）→ `models/hybrid/hybrid_layer_allocation.py` 的 pattern 解析 → `gdn.py:70-130`（最小的 mixer 变体配置）→ `gated_delta_product.py` 的 `ssm_decode`/`ssm_prefill` → `ops/gdp/__init__.py` 与 `chunk.py`/`fused_recurrent.py` 头注释。
- **模式串是单一事实来源**：层数、PP 分段、MTP 段全由它推导（`get_hybrid_total_layer_count`/`select_pipeline_segment`），改层数别去改 config 里的 num_layers 类参数。
- **GDN2 目前无动态推理**（gdn2.py:179 assert）——做推理服务选型时只能用 GDN/GDP/Mamba。
- **双 chunking 陷阱**（chunk.py docstring）：读 GDP kernel 时先分清当前张量在 token 流还是 Householder 展开流，两个 chunk 网格不是比例关系。
- **deterministic_mode 与融合开关互斥**：GDN 的 pre-GDR 融合非确定性（gdn.py:78-84），复现实验先关融合。
- shim 三件套（mamba_hybrid_layer_allocation.py/mamba_block.py/models/mamba/*）**只读不写**——新代码一律走 `models/hybrid` canonical 路径；仓根 `pretrain_mamba.py`/`pretrain_hybrid.py` 是两代入口并存的现场。
- `mamba_context_parallel.py` 与 `gdp_context_parallel.py` 是 SSM 专属 CP；如果混合模型里还有注意力层，两条 CP 路径会同时激活，排查 CP 问题先分清层类型。
