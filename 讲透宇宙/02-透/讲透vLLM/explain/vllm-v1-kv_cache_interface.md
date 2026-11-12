# vllm/v1/kv_cache_interface.py — KVCacheSpec 类型系统：KV cache 的格式合同与传输公共语言

> 源码：`vllm/v1/kv_cache_interface.py`（1660 行）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`kv_cache_interface.py` 是 v1 引擎 KV cache 子系统的**接口层/类型层**：不分配一块显存，却定义了四方协作的全部名词——(a) `KVCacheSpec` 族 17 个 frozen dataclass 描述"某层（组）的 KV cache 长什么样"；(b) 尾部三大件（`KVCacheTensor`:1475/`KVCacheGroupSpec`:1505/`KVCacheConfig`:1526）描述整个模型怎么摆、分几组、哪些组可外传；(c) `KVQuantMode`:40 把 `--kv-cache-dtype` 变成可判定枚举。上游模型层产出 spec，规划层聚合成 config，`KVCacheManager` 按组分配（姊妹篇 vllm-v1-core-kv_cache_manager.md），KVConnector 按 config 选组传输——本文件即四方合同文本。2026 年它已长成混合架构中枢：HiSparse 双池、Mamba 状态池、DCP 分片（:207）、kernel block 拆分（:348）全靠它表达。

## ② 内部结构

五段：量化枚举（:40-153）、spec 基类与视图工具（:201-482）、17 个 spec 子类（:485-1401）、kind 帮手（:1404-1471）、尾部三大件（:1474-1660）。

量化段：`KVQuantMode` 值 0-14（fp8/int8/int4/nvfp4/turboquant/octave/ultraquant 等），判别 property 族（:72/:85/:110）；`get_kv_quant_mode`（:121）字符串→枚举；CUSTOM 由平台 handler 返回（协议 vllm/config/cache.py:77），表示"后端自管 kernel 派发"。

基类 `KVCacheSpec`（:202）核心字段：`block_size`、`dcp_sharded`:207、`block_stride_alignment`:210（`MultipleOf(n)` 表 kernel block 粒度）、`is_draft`:215（compare=False 不影响分组）。抽象 property `page_size_bytes`（:259）/`tokens_per_state`（:251）；内存上界 `max_memory_usage_bytes`（:281）与块表宽度 `max_num_blocks_per_req`（:290）；分组协议 `merge`（:307）与 `is_uniform_with_collection`（:315，经注册表 `get_uniform_type_base_spec` 判同族）；能力开关 `has_layer_views`:328/`uses_slot_mapping`:338（自管寻址不占 slot mapping 行）。视图工具链：compute_layer_kv_cache_shape_bytes:360 给逻辑 4D `[B,H,N,C]`（C 计字节）、compute_layout_strides:379 算五轴步长、create_kv_cache_views:418 用 `torch.as_strided` 切每层视图（kernel block 拆分要求稠密页，:444）。

spec 子类三层谱系：HiSparse 双池（:486 一次性热缓存/:520 可回收驻留页，均不可前缀缓存）；`AttentionSpec`（:552）加 `num_kv_heads/head_size/dtype` 与打包字段（`tokens_per_state`:569——整数>1 是 DSv4 sparse MLA 多 token 一态、分数<1 是 Whisper 一 token 多态）；`FullAttentionSpec`（:619，`non_causal`:634 让 engine core 免看 TP 布局调调度）→`MLAAttentionSpec`（:729，alignment padding :719）→Sink:1232；旁支 `SlidingWindowSpec`（:901，`extra_retained_tokens`:908 为投机解码延迟释放）→`SlidingWindowMLASpec`（:1008，`bounded_replay`:1015 关前缀缓存）；另有 ChunkedLocal:861、CircularBuffer:968（每请求恒一页）、RSWA:816、Cross:1221、EncoderOnly:1214（返回 0）、`MambaSpec`（:1094，shapes+dtypes 描述状态张量+checkpoint 判定 :1169/:1189）。`UniformTypeKVCacheSpecs`（:1291）是聚合包装：组内每层各留一份 spec，`page_size_bytes` 求和（:1319）。

尾部：`KVCacheTensor`（:1475）只有五个数（size/layers/两 stride/offset），地址区间重叠即别名——块 ID 归一组所有故安全（:1485）；`KVCacheGroupSpec`（:1505）带 `enable_kv_transfer`（:1521）与 HiSparse `role`（:1522）；`KVCacheConfig`（:1526）聚合 num_blocks+tensors+groups 与引擎核心回填字段（`hash_block_size`:1545 等），cached_property transfer_group_ids:1561、select_transfer_block_ids:1603、needs_kv_cache_zeroing:1651（mamba 或混合精度才清零）。

## ③ 外部连接

- **上游产出**：每层 `get_kv_cache_spec(vllm_config)`——通用实现 vllm/model_executor/layers/attention/attention.py:611（encoder-only 返回 None）、MLA 同目录 mla_attention.py:1371；收集器 vllm/v1/worker/gpu/attn_utils.py:138（跳过 kv_sharing 层、标 is_draft）。
- **规划**：vllm/v1/core/kv_cache_planning.py——分组:187、统一页:346、打包:910、组装 config:642。
- **下游**：`KVCacheManager.__init__`（vllm/v1/core/kv_cache_manager.py:132）持 config 建组；下发（vllm/v1/worker/gpu_worker.py:869）后经 vllm/v1/worker/utils.py:618 调 `create_kv_cache_views` 真实分配。
- **KV 传输**：kv_connector v1（vllm/distributed/kv_transfer/kv_connector/v1/nixl/connector.py:176 读 `transfer_group_ids`；`select_transfer_block_ids`:1603 裁子集；mooncake/moriio 同协议）。
- **注册表与布局**：vllm/v1/kv_cache_spec_registry.py 的 `@register_kv_cache_spec` 挂 spec↔manager↔base 三元组（内置注册 single_type_kv_cache_manager.py:2656）；`KVCacheLayout`（vllm/v1/kv_cache_layout.py:15）被 strides 消费。
## ④ 数据流

```
每层 get_kv_cache_spec（vllm/model_executor/layers/attention/attention.py:611）
  → attn_utils.py:138 收集 → kv_cache_planning.py:187 同族分组（merge:307）
  → :346 统一页 → :910 打包 → :642 组装 KVCacheConfig
  → vllm/v1/worker/gpu_worker.py:869 → vllm/v1/worker/utils.py:618 切层视图
运行期：KVCacheManager 按组 allocate/free；KVConnector 走
  transfer_group_ids:1561 → select_transfer_block_ids:1603 → 传输/加载
```

## ⑤ 设计决策

1. **frozen dataclass 当合同**：spec 只声明格式不参与执行；`merge`（:307）与各子类 merge 的 assert 全钉死"All layers in the same KV cache group must..."（FullAttention 版 :667 逐字段比对）——分组不变量启动期炸掉而非运行期漂移。`replace_as`（:156）做跨类重建（SWA→FullAttention 降级）。
2. **"启动池容量=运行期准入闸"单一事实源**：SWA:918/ChunkedLocal:864/HiSparseResident:533 的 `max_admission_blocks_per_request` 同时服务池容量与运行期准入，`max_memory_usage_bytes` 委托它。
3. **包装器陷阱显式救治**：`UniformTypeKVCacheSpecs` 不是 `FullAttentionSpec` 子类，裸 isinstance 漏掉 DeepSeek-V4 MLA 组，故配 is_full_attention_spec:1404/iter_layer_specs:1392 统一解包。
4. **KVQuantMode.CUSTOM 与 OCTAVE_K3V4 同值 12**（:61/:69）：IntEnum 语义下 CUSTOM 是 OCTAVE_K3V4 的别名（同一成员），`is_custom_mode`（:110）与 `is_octave`（:85）在值 12 上不可区分——ROCm Octave 路径会被同时判成 CUSTOM。疑似合并残留（两族由不同 handler 产出暂未见炸点）；worker 情报"15 态"未提此别名。
5. **传输协议钉在 config**：transfer 族 cached_property（:1561-1601）让所有 connector 共用分组语义，ephemeral 副本组排除在外（:1518）。

## ⑥ 新人提示

- 读法：:202-345 基类 → :552-616 AttentionSpec → :1474-1660 三大件 → 再跳 planning。
- 加新 attention 类型：spec 子类 + `@register_kv_cache_spec`；分组兼容性由 base spec 决定。
- 排查"KV 显存比预估大"：先看 page_size_padded:562（alignment padding 放大页）再看 max_num_blocks_per_req 的 DCP 分支:610。
- needs_kv_cache_zeroing:1651 三态：混合精度不清零会把旧块重解释出 NaN（#35219 教训入 docstring）。
- 与 vllm-v1-core-kv_cache_manager.md 配对读：本篇是合同，那篇是执行。
