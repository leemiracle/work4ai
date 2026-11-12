# explain-06 · keywords_vector_hybrid_indexer.go — 关键词+向量混合检索引擎

> **文件**：`internal/application/service/retriever/keywords_vector_hybrid_indexer.go`（383 行）
> **所属层**：应用服务层 · retriever 子包（导览第 7 步"检索存储：向量库与混合引擎"）
> **一句话定位**：实现 `RetrieveEngineService` 的引擎门面——要不要算向量、怎么分批、并发多少在此收敛，底层存储（pgvector/ES/OpenSearch/Doris/SQLite）由注入的 Repository 决定。

## 1. 角色定位

WeKnora 支持 8 种检索后端，上层不想关心查的是哪种库。`KeywordsVectorHybridRetrieveEngineService` 是统一门面：关键词+向量收敛成一套索引/检索/删除/迁移方法，DSL 与存储格式下推给 `RetrieveEngineRepository`。服务两条线：问答的 `Retrieve` 与入库的 `BatchIndex`。

## 2. 内部结构

- **防护常量**（L20-39）：单条 embedding 上限 2 万字符；重试 5 次/基准 200ms；正则把内联 base64 图片洗成 `[image]`。
- **读路径**（L43-66）：结构体仅仓储+engineType 两字段；`Retrieve` 纯转发仓储。
- **索引路径**（L70-127）：`Index` 单条——含 `VectorRetrieverType` 才 sanitize 后 embed（L76）；`BatchIndex` 主路径——批量 embedding（带回退）→ 按 40 条切片 → ≤5 批全并发，否则信号量限流 5（L110）。
- **embedding 加固**（L132-176）：`batchEmbedWithBackoff` 指数退避且尊重取消；`sanitizeForEmbedding` 仅当内容含 `base64,` 才跑正则（L163），再 2 万 rune 截断。
- **并发保存**（L179-270）：四组方法（有/无 embedding × 简单/限流），均用 errgroup。
- **维护**（L273-383）：三类 Delete、`EstimateStorageSize`（L299 零向量假数据）、CopyIndices；L352 断言探测 `KnowledgeIndexMover`，不支持则报错。

## 3. 外部连接

import models/embedding、models/utils、types/interfaces、errgroup。实现 `RetrieveEngineService`，包装 `RetrieveEngineRepository`（各实现于 repository/retriever/ 下按存储分目录）。装配于 container.go:1235 起，每种后端一实例。调用方 `knowledgeBaseService`：HybridSearch 按 store 组解析引擎，`retrieveFromStores`（knowledgebase_search_fanout.go:48）单组直通、多组限流并发；索引侧由知识任务 worker 调 BatchIndex。

## 4. 数据流

80 页 PDF 入库：分块得 600 chunk → `BatchIndex` → 内容过 sanitize（base64 截图换成 `[image]`）→ 批量算向量（首轮网络抖动，退避后成功）→ 切批限流并发 `BatchSave` → pgvector 写表、关键词建倒排。提问时 `Retrieve` 进来，同表双路召回。

## 5. 设计决策

"策略在上、存储在下"使新增向量库只写 Repository 不动引擎——并列 8 后端的前提。信号量限流是 Go 惯用法；四个 save 变体是复制粘贴分叉，抽回调参数可合并。`EstimateStorageSize` 用零向量务实，但其键用 ChunkID 而 `Index` 用 SourceID，不一致、仅影响估算。重试放引擎层，不走本引擎的调用方享受不到退避，防护边界=最常用路径。

## 6. 新人提示

① 本文件**不做**分数融合——合并与归一化在 knowledgebase_search.go 与 ScoreNormalizer；② 新加后端：实现仓储接口全套 + container.go 注册即可，`MoveKnowledgeIndices` 可不实现（L353 断言挡下）；③ `safetyMaxChars` 是 rune 数非字节数（L170），中文实际字节约 3 倍；④ 搭配 DeepWiki《11.6 Hybrid Retrieval Strategies》第 1/4 节与《8.5 Retrieval Engine Configuration》。
