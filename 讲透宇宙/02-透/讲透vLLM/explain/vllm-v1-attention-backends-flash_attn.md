# vllm/v1/attention/backends/flash_attn.py — FlashAttention 后端：FA2/3/4 统一封装与 varlen 执行内核

> 源码：`vllm/v1/attention/backends/flash_attn.py`（1879 行）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

vLLM v1 对 FlashAttention（FA2/FA3/FA4 统一封装）的**默认主力后端**，遵循三件套协议：`AttentionBackend`（能力协商）→ `MetadataBuilder`（每步构建元数据）→ `Impl`（每层一个实例执行 forward）。它处于 forward 最内层：ModelRunner 的 `_build_attention_metadata` 调 builder.build()，每层 attention 落到 `FlashAttentionImpl.forward()`。**2026-10 重大反转：cascade attention（级联注意力）已整体移除（PR #61126）**——旧版三大执行路径之一消失，common_prefix_len 沦为遗留参数（详见⑤3）。

## ② 内部结构

**`FA4DenseAttentionKernel`**（:97）：`VllmJitKernel` 子类，把 flash_attn_varlen_func 包装成可 JIT 预热的 kernel——frozen CompileKey（:100）锁定 dtype/head_dim/page_size/窗口/softcap/num_splits；`get_warmup_keys`（:145）按架构给预热矩阵（:174-189）；`compile()`（:206）造假形编译，FA4 SplitKV combine 要在 FakeTensorMode 里调 `_flash_attn_fwd_combine` 填原生缓存（:251-273）。Gemma4 在 builder `__init__` 注册 warmup（:720-729）。文件尾单例 `_FA4_DENSE_ATTENTION_KERNEL`（:1879）是**所有** FA 版本 forward 的统一入口。

**`FlashAttentionBackend`**（:286）：classmethod 协商。`supports_kv_cache_update_bypass=True`（:287）、`forward_includes_kv_cache_update=False`（:369）。块尺寸协商三态（:357-367）：SM90 FA4 FP8-KV→64（:300）；FA4 hd256→256（:329）；默认 MultipleOf(16)。`supports_combination`（:462）是仲裁点：sink 需 SM90+（:474）、FP8 KV 文案"需 SM90 FA3 / SM90 FA4 hd512 / SM100 FA4"（:496）、mm_prefix 必须 FA4（:499-513）。

**`FlashAttentionMetadata`**（:518）：头部长度关系图注释（:519-525）是理解 varlen 的钥匙。基础四件（query_start_loc/seq_lens/block_table/slot_mapping）之外：DCP 专用（:536-544）、FA3 AOT scheduler_metadata、**causal 可为 per-request int32 张量**（:550，FA4 专属）、mm_prefix 区间张量（:555）、R-SWA 三件（:563-565）。

**`FlashAttentionMetadataBuilder`**（:600）：`_cudagraph_support` FA3/4=ALWAYS、FA2=UNIFORM_BATCH（:619-623，FA2 max_query_len=1 packed-GQA 限制）；`supports_update_block_table=True`（:624）。`__init__`（:685）预分配全部 graph 安全缓冲：FA3 scheduler_metadata 上界 `1+round_up(max_batch,4)*4`（:752-766）、max_num_splits 上界（:770）、DCP/R-SWA/mm_prefix 持久张量（:774/:786/:799）。aot_schedule 仅 FA3（:708）且要求全层滑窗一致（:839-853）；fused draft decode 的 metadata 复用在 DCP 下禁用（:735-741，Python 侧字段不随 replay 刷新）。

**`FlashAttentionImpl`**（:1057）：构造（:1061）解析 FA 版本（:1104）、滑窗转 (left,right)——ENCODER_ONLY 对称化（:1084-1087）；SM90 FA4 FP8-KV 走"原生 FP16 Q+核内反量化"特例（:1158）；DCP combine 按 backend 选 a2a 或 allgather（:1167）。

## ③ 外部连接

- **依赖**：fa_utils（版本/能力探测）、merge_attn_states（:44）、DCP 算子（:40）、`current_workspace_manager`（:45，:1542 借 workspace）、jit_warmup（:14）、cp_utils FA2 混批拆分（:82）。
- **被依赖**：flash_attn_diffkv 直接继承 Backend/Impl（vllm/v1/attention/backends/flash_attn_diffkv.py:34）；update_block_table 被 gpu_model_runner.py:2409 跨组元数据缓存消费；get_cudagraph_support 参与 cudagraph mode 降级仲裁。

## ④ 数据流

**主路径 `forward()`**（:1182）：签名带 output/output_scale（fused 输出量化不支持 :1221）；attn_metadata 为 None 是 profiling，填零返回（:1226）。**开头警告注释（:1232-1239）仍是第一法则：piecewise CUDA graph 下此函数 eager 执行，view/切片都有可观 CPU 开销，任何改动必须基准测试**。流程：encoder 分流（:1244）→ transpose+split 劈 K/V 视图（:1257）→ 修退化 stride（:1261，TP num_kv_heads=1 时 TMA 要 ≥16B）→ fp8 view（:1276）→ descale expand（:1288）→ DCP 分流（:1298）→ 窗口**层自身优先于组**（:1316，Gemma-3 混组）→ mm_prefix 构造 mask_mod 并**手动关 causal/sliding_window**（:1325-1361，FA #155 后 mask_mod 不再自动短路内置 causal）→ R-SWA mask_mod（:1363-1380）→ per-request causal 需 FA4 否则 raise（:1382-1393）→ hd256 页对齐+禁 SplitKV（:1396-1402）→ 统一经 `_FA4_DENSE_ATTENTION_KERNEL`（:1404）进 flash_attn_varlen_func。

**KV 写 `do_kv_cache_update()`**（:1432）：reshape_and_cache_flash 按 slot_mapping scatter 写——slot_mapping 形状决定实际 token 数，无需切 [:num_actual_tokens]（:1452-1456）。**读用 block_table、写用 slot_mapping**。

**DCP 路径 `_forward_with_dcp()`**（:1468）：无 context 时纯本地因果（:1490）；否则 query 跨 rank all_gather（:1516）、输出借 workspace（:1542）、FA2 混批拆分（:1547）、context 段非 causal+query 段 causal 两段 LSE 合并（:1605-1642）。

**mask_mod 工厂**：`_make_mm_prefix_mask_mod`（:1718）functools.cache 缓存闭包——FA4 hash_callable 混入闭包 cell 的 repr()，不缓存则每次 forward 全量 JIT（:1726-1729）；kernel 传**局部** q_idx，用 `seqlen_k - seqlen_q` 偏移换算绝对位置（:1730-1736）；(-1,-1) 哨兵自然落空免 key 侧查表（:1743）。`_make_rswa_mask_mod`（:1826）编码"causal AND (kv<prefix OR abs_q-kv<window)"（:1855-1873），use_fast_sampling 让 FA4 跳全掩码块。

## ⑤ 设计决策

1. **varlen 打包代替 padding**：token 稠密拼接+cu_seqlens_q 划界，batch 维不进张量——形状不随请求数变化是 CUDA graph 重放的前提。
2. **AOT scheduler_metadata（FA3）**：host 侧预算 split 调度，forward 零 host 计算；持久 buffer **尾部清零**（:677-681，残留脏值会让 thread block 覆写输出）；graph 模式用 num_splits 上界换预分配确定性（:855-865）。
3. **cascade attention 移除（2026-10 反转）**：共享前缀两段式整条路径随 #61126 下线，common_prefix_len 参数与 runner 侧 use_cascade_attn 形参只剩兼容壳。
4. **mask_mod 扩展机制（FA4）**：R-SWA/mm_prefix 的精确 token 级掩码编译进 kernel 而非 block 近似；代价是闭包身份管理（cache）与 caller 手动关内置 causal 的脆弱契约。
5. **统一 JIT kernel 入口**：_FA4_DENSE_ATTENTION_KERNEL 让稳态调用与预热注册共享同一 dispatch 路径，FA4 冷启动被吸收进 kernel_warmup；块尺寸协商也从 MultipleOf(16) 泛化升级为两个"必须等于"定值（64/256），块布局与内核 TMA tile 严格对齐。

## ⑥ 新人提示

- 切入点：Metadata 长度关系图注释（:519-525）→ forward 主路径（:1182）→ 按兴趣跳 DCP（:1468）与 mask_mod 工厂（:1718/:1826）。
- 易混淆点①：forward_includes_kv_cache_update=False——forward 只读，KV 写由框架单独节点/do_kv_cache_update 完成；supports_kv_cache_update_bypass=True 允许写被整体跳过。
- 易混淆点②：build() 收到的 common_prefix_len 是遗留参数，cascade 分支已不存在。
- 易混淆点③：_store_scheduler_metadata 只在 use_full_cuda_graph 时写持久 buffer 并清零尾部，piecewise 直接返回新 tensor；build(fast_build=True) 关 AOT。
- 性能直觉：decode 小 batch 瓶颈在 host 侧元数据构建而非 kernel——DCP 免同步推上界（:917-928）、causal 张量强制 int32 防build 期 cast 分配（:953-958）都为此服务。
