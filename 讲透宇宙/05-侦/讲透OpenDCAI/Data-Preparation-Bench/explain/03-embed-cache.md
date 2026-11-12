# 03 · 嵌入与缓存：三后端嵌入器与 RedisCache

## 角色定位

`src/distflow/embed/` 与 `src/distflow/cache/` 是数据质量评测线的底座，负责"把样本变成向量"与"向量别重复算"。嵌入器是 MMD 距离与 DAS 指标的唯一数据入口；缓存层把昂贵嵌入变成跨数据集可复用资产——没有它，每次算 MMD 都要重嵌几千至几十万条样本。

## 内部结构

**统一契约 BaseEmbed（embed/base.py:6-19）**：ABC 只有一个抽象方法 `embed(dataset) -> list[EmbeddingResult | None]`。两个关键决定：接口**同步**（异步实现内部自行 asyncio.run 驱动）；失败项不抛异常而返回 **None 占位**，保持与输入等长——mmd.py:66-99 的 `_filter_embeddings` 据此过滤并查失败率。`EmbeddingInputItem` 是 `DatasetProcessOutputItem` 别名（embed/types.py:7）；`EmbeddingResult`（L10-13）捆回向量、原样本、meta。

**三后端**。`openai_embed.py:16` OpenAIEmbed：名义 OpenAI SDK，实际瞄准 **vLLM 的 embeddings 扩展**——truncate_prompt_tokens / chat_template 等构造参数（L30-42）全是 vLLM 专有，标准 API 不认；请求体直接传 messages（L129-131）让 server 端处理 template 与截断；Semaphore 限 50 并发、3 次退避（L221-244）。`sentence_transformers.py:15`：本地模型延迟初始化（L51-70 首次 embed 才加载），messages 拼 `role: content`（L94）。`vllm.py:15` VllmEmbed：进程内直起 vLLM 引擎（enforce_eager=True，L53），apply_chat_template 转 token ids 包 TokensPrompt（L102-119），并处理 vLLM 0.19.0 前后 import 分叉（L87-90）。

**缓存协议与实现**。`cache/protocol.py:4-7` CacheProtocol 仅两个 async 方法 `load_cache/save_cache`——又是 Protocol 结构化满足。唯一实现 `redis_cache.py:10` RedisCache：懒连接+ping 探活（L37-58），读写各 3 次重试、失败重置客户端重连（L69-83），Semaphore 限并发。

**两个缓存包装器**。`cache_wrapper.py:19` CachedEmbed 继承 BaseEmbed 包任意嵌入器：批量并发查缓存 → 分离命中/未命中 → 未命中走底层 → 批量回写（L90-154）。缓存键两代格式（L55-76）：legacy 含完整 data_item，新版仅 `model_id + messages`（**不含 meta**）；换模型默认缓存失效，显式传 `cache_model_id` 可迁移后续吃旧缓存。`async_cached_embed.py:26` AsyncCachedOpenAIEmbed 纯异步变体，刻意**不继承 BaseEmbed**（docstring L4：同步接口装不下单条粒度的 async 生命周期），每条独立"查→嵌入→写"（L92-145）；内部传 dummy Semaphore 放行（L66），复用 OpenAIEmbed 私有 `_embed_single`（L130）。

## 外部连接

上游吃 DatasetProcessOutputItem（data_formatter 的 Alpaca/ShareGpt Formatter 产出）；下游唯一消费者是 MMDDistance 与 DASMetric。OpenAIEmbed 对接 vLLM 服务（examples/compute_mmd.py:28 配 localhost:8000 + Qwen3-Embedding-8B）；RedisCache 对接独立 Redis。注意 `embed/__init__.py` 是**空文件**——无包级导出，必须从子模块精确 import。

## 数据流

```
list[DatasetProcessOutputItem]
  → CachedEmbed: 并发查 Redis(SHA256(model_id+messages))
  → 命中组装；未命中 → 底层嵌入器 → 回写
  → 等长结果列表(None 占位) → MMDDistance 滤 None → 核矩阵
```

## 设计决策（含批判）

1. **同步门面+异步内核**：BaseEmbed 同步让 MMD 调用方无感，但 CachedEmbed.embed 内两次 asyncio.run（L96、L152）意味着**外层已有事件循环时必炸**，纯异步场景走 AsyncCachedOpenAIEmbed。
2. **缓存键不含 meta 是双刃剑**：换来数据集间复用（同一批 messages 跨指标共享向量）；代价是 meta 参与嵌入语义时（prompt 前缀变化）会静默命中错缓存——SentenceTransformersEmbed 有 prompt 参数，撞上须手动换 cache_model_id。
3. **CachedEmbed 结尾 `[r for r in results if r is not None]`（L157）破坏等长契约**：失败项被压缩，返回长度≠输入，按下标配对会错位——MMD 路径恰先过 `_filter_embeddings` 才免疫。
4. **失败"None 而非异常"**成就 2% 容错语义，但错误吞进日志，长跑需盯 warning。

## 新人提示

跑通顺序：起 vLLM 嵌入服务+Redis，先用 examples/compute_mmd.py 感受裸奔成本，再给 MMDDistance 换 CachedEmbed 复跑——第二次命中率应近 100%。读码重点：cache_wrapper.py 的键构造与命中分流是缓存通用范式。动手任务：修掉 L157 长度破坏（None 占位保持等长）；实现 FileCache 满足 CacheProtocol——不改 CachedEmbed 一行即可替换 Redis。
