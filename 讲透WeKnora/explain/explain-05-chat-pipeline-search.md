# explain-05 · chat_pipeline/search.go — RAG 问答管线的检索阶段

> **文件**：`internal/application/service/chat_pipeline/search.go`（652 行）
> **所属层**：应用服务层 · chat_pipeline RAG 管线（导览第 6 步）
> **一句话定位**：挂在 `CHUNK_SEARCH` 事件上的检索编排插件——并行调度知识库混合检索与网络搜索，按 embedding 模型分组省调用，低召回自动扩招。

## 1. 角色定位

WeKnora 的 RAG 问答是"管线+插件"架构：`types/chat_manage.go:320` 定义 rag 管线为 `CHUNK_SEARCH→RERANK→MERGE→INTO_CHAT_MESSAGE→CHAT_COMPLETION`。本文件的 `PluginSearch` 负责检索一环：问题已改写（RewriteQuery），如何从多个 KB 目标加互联网高效召回。它不碰向量库，只做编排：分组、扇出、合并、降级。

## 2. 内部结构

- **插件骨架**（L18-59）：持 9 个接口依赖；构造函数 L52 自注册进 EventManager；`ActivationEvents()`（L57）只响应 `CHUNK_SEARCH`。
- **主入口 OnEvent**（L62-163）：L66 查 `HasKnowledgeRetrievalScope`——无 KB 目标且未开网搜则返回 nil 跳过；L93 双 goroutine 并行 KB 检索与网搜；L141 低召回时 `runQueryExpansion` 扩招；L151 有结果 `next()` 进下一环，否则 `ErrSearchNothing` 终止管线。
- **目标分组 searchByTargets**（L348-519）：核心优化。L382 按模型名+端点解析真实 embedding 身份，L384 聚组——同组只算一次 query embedding（L418）；embedding 失败按 `targetReportsEmbedFailure`（L330：FAQ 报错、有关键词索引的库降级）筛选目标；L444 整库目标合并成一次 `HybridSearch`（L479），带标签目标走 `searchSingleTarget`（L522，可覆盖阈值）。
- **去重函数**（L183-303）：`removeDuplicateResults`（ID+内容签名）与 `removePartialOverlaps`（子串包含或 token 重叠 ≥0.85 判冗余），被 merge.go 复用。
- **网搜**（L583-652）：租户配置+agent 覆盖；L631 起有注释掉的压缩逻辑化石。

## 3. 外部连接

import 六个内部包。实现 `chat_pipeline.go:11` 的 Plugin 接口，由 EventManager 织成洋葱链。下游经 `HybridSearch`（knowledgebase_search.go:125）落到 retriever 引擎；装配点 container.go:455。流式管线走 `CHUNK_SEARCH_PARALLEL`，由 search_parallel.go 处理——其 L62 直接构造 `PluginSearch` 当 worker。

## 4. 数据流

用户开两个 KB（一整库、一带标签子集）并开网搜问"报销制度变了什么"：前置插件改写问题 → 触发 `CHUNK_SEARCH` → OnEvent 并行：KB 路发现两目标共用同一 embedding 模型，只调一次 embedding API，整库目标合成一次 HybridSearch、标签目标单独一次；网搜路转 SearchResult。合并写入 `chatManage.SearchResult`，不足再扩招，`next()` 进重排。

## 5. 设计决策

按"模型名+端点"而非模型 ID 分组是老练细节：跨租户两个 ID 不同的 KB 可能是同一物理模型，按身份分组才能安全合并。embedding 失败分级降级，避免"向量挂了整库变空气"。批评点：手工 WaitGroup+锁可用 errgroup 简化；OnEvent 混三种关注点，好在去重已是纯函数。

## 6. 新人提示

① 两事件别混：`CHUNK_SEARCH`（非流式）与 `CHUNK_SEARCH_PARALLEL`（流式，叠加实体检索），后者复用前者；② `ErrSearchNothing` 终止整个问答，返回 nil 是静默跳过，语义相反；③ `removePartialOverlaps` 是 O(n²)，改时保持"输入先按 ID 去重"前置（L222 注释）。搭配 DeepWiki《3.2 RAG Pipeline Architecture》Retrieval Pipeline 节与《11.6 Hybrid Retrieval Strategies》第 1-2 节。
