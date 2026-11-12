# WeKnora 端侧 SQLite 优化与全局搜索配合方案

> 2026-09-20 · 基于 /usr-data/data1/WeKnora(commit 5c5d46d9)一手代码实证 + 四路并行审计
> 场景钉版:**端侧 + SQLite,不迁移**。WeKnora Lite 形态:`DB_DRIVER=sqlite` + `RETRIEVE_DRIVER=sqlite`
> 命题:数据量增长导致的性能下降——风险查验与全部优化点

---

## 0. 端侧技术栈实况(证据)

| 组件 | 实况 | 位置 |
|---|---|---|
| 主存储 | GORM + mattn/go-sqlite3 v1.14.24 (cgo),DSN 仅 `_journal_mode=WAL&_busy_timeout=5000&_foreign_keys=on` | internal/container/container.go:799 |
| 连接池 | sqlite 分支已设 `SetMaxOpenConns(1)`(读写全串行) | container.go:885-889 |
| 向量检索 | sqlite-vec v0.1.6 `vec0(embedding float[dim] distance_metric=cosine)`,按维度分表 `vec_embeddings_{dim}` | internal/application/repository/retriever/sqlite/repository.go:114 |
| 关键词检索 | FTS5 contentless 表 `lite_embeddings_fts`(`contentless_delete=1`,unicode61)+ **Go 层手工 CJK bigram 预分词** | repository.go:73-78, 588-635 |
| 元数据+全文 | `lite_embeddings` 表(content 全文副本、dimension、多索引) | repository.go:21-36 |
| chunk 主表 | `chunks`(content+source_content 双文本、软删 deleted_at) | migrations/sqlite/000000_init.up.sql:242-285 |
| 检索编排 | 默认 rewrite+expansion+rerank 全开,top_k 30/30 | config/config.yaml:12-21 |
| 批量 embedding | BATCH_EMBED_SIZE 默认 5 | internal/models/embedding/batch.go:32-34 |

**端侧安全规模**:vec0 为暴力 KNN(无 ANN 索引),1024 维 float32 下 1 万 chunk(~30ms)无压力、10 万(~150-300ms)吃紧、50 万+ 不可行——见 §4 规模对照表。

---

## 1. 风险清单(全部实证,按严重度)

### CRITICAL

**C1 · vec0 暴力扫描,无 ANN** — repository.go:114
sqlite-vec 0.1.6 的 vec0 每次查询全表算 cosine,O(N·dim)。这是「数据太多性能下降」的第一性原因。10 万 chunk(400MB 向量)→ 100-300ms 且内存吃紧;100 万(4GB)端侧不可行。

**C2 · rowid IN 过滤语义未验证(正确性风险)** — repository.go:391-409
```sql
WHERE v.embedding MATCH ? AND k = ?
AND v.rowid IN (SELECT filtered.id FROM lite_embeddings filtered WHERE ...)
```
过滤包在子查询里,KNN 无论如何扫全表;`k` 在过滤前还是过滤后计数未实测——若过滤前取满 k,带知识库过滤的检索会**结果不足 k 甚至空结果**(top-k 全落别的 KB 时)。跨多 KB 全局检索时 IN 列表本身也膨胀。

**C3 · 检索同步层逐条事务(入库慢主因)** — repository.go:160-184
`BatchSave` 主表批量 INSERT 后,`syncFTS5Insert`/`insertVec` **逐行独立 `db.Exec`** = 每行一个自动事务一次 fsync(synchronous 默认 FULL)。1000-chunk 文档 ≈ 2000 次独立事务。chunks 主表无辜(上游批插 500/批健康)——慢点精确锁定在 lite_embeddings 的 FTS5/vec0 同步层。

### HIGH

**H1 · 删除路径全量捞大字段 + 逐条 DELETE** — repository.go:194-213, 503-522
`Find(&rows)` 把待删行 content 全文捞进内存(只需 id/dimension);vec0/FTS5 逐 rowid DELETE。删万级 chunk 的知识库 = 数万次 Exec + 内存峰值。

**H2 · FTS5 表 5 个元数据列纯浪费** — repository.go:73-78
`source_id/chunk_id/knowledge_id/knowledge_base_id` 未标 `UNINDEXED`,被 unicode61 切成 token 进倒排索引;且 contentless 表下 SELECT 这些列**永远返回 NULL**(查询实际从 JOIN 的 e 表取)——零收益纯膨胀。

**H3 · 检索编排层 LLM 前置默认全开(端侧延迟另一半)** — config/config.yaml:12-21
`enable_rewrite+enable_query_expansion+enable_rerank` 全 true,top_k 30/30。一次问答 = 2 次 LLM 前置调用 → 向量+FTS5 各取 30 → rerank 串行链。端侧本地 LLM 单次 0.5-2s,**优先级高于 SQLite 侧优化**。

**H4 · messages 胖行每轮全量拉 + OFFSET 深分页** — internal/application/repository/message.go:65-107
`GetRecentMessagesBySession` 每轮 agent 都跑且无列裁剪(content/rendered_content/agent_steps/knowledge_references 大字段整行读);历史翻页 OFFSET。**cursor 版 AfterCursor/BeforeCursor 已存在(message.go:156-197)只是没接**——切换成本≈0。

**H5 · 软删无 purge + SQLite 文件只涨不缩**
chunks/messages/sessions/knowledges 全软删(deleted_at),全仓无物理 purge 作业(audit_logs/temporary_documents/memory 有治理,chunks/messages 没有)。SQLite 默认非 auto_vacuum 下**免费页永不回收**;反复「重导入→软删」churn 后表膨胀拖慢所有 seq scan——而 SQLite 的 seq scan 就在检索路径上。

### MEDIUM

- **M1 日志洪水+隐私**:repository.go:334,343,441 每条检索结果 Info 级 content_preview(60 字原文进日志)。
- **M2 FTS5 重建迁移全量进内存**:repository.go:83-101 升级时全表 SELECT+逐条 INSERT,无分批无事务。
- **M3 N+1 家族**:CopyIndices 逐 chunk First+Create+copyVec(222-247);BatchUpdateChunkEnabledStatus/TagID 逐条 Update(250-262);KB 列表每库 2-3 条 COUNT+列表不分页(internal/application/service/knowledgebase.go:369-398,单连接下全部串行)。
- **M4 GORM 性能开关全关**:container.go:807-812 只设 NowFunc,无 SkipDefaultTransaction/PrepareStmt。
- **M5 无界增长表**:① knowledge_processing_spans(每文档每 attempt 树状 span,repo 无任何删除函数,文档删除不清理→孤儿永久累积);② task_dead_letters(设计钉版无 TTL,last_error 8KB 堆栈,无 prune API);③ sync_logs/auth_tokens 属「死配置」——CleanupOldLogs/DeleteExpiredTokens 已实现但零调用。
- **M6 BATCH_EMBED_SIZE=5**:1000-chunk 文档 = 200 次 embedding 服务往返。
- **M7 content 四副本**:chunks.content + chunks.source_content + lite_embeddings.content + FTS5 tokens,1GB 原文 → 3-4GB DB。
- **M8 单连接读写串行**:入库高峰期检索排队抖动(与解析并发叠加即「导入中检索卡」)。

### LOW

- L1 文档搜索 `LOWER(file_name) LIKE '%kw%'` 前导通配全表扫(knowledge.go:916-917;端侧文档数通常 <1 万可容忍)。
- L2 chunks/messages UUIDv4 varchar(36) 主键随机写页分裂(端侧写频低);sessions 每轮 UPDATE 大 JSON 热行;chunk_revisions 无 TTL(低速率)。
- L3 wiki 全文检索 `to_tsvector('simple')` 不分词中文(端侧默认 `ENABLE_GRAPH_RAG=false` 不触发,启用 wiki 前须知)。

---

## 2. L0 · 配置层优化(零代码,当天可做)

| 项 | 改法 | 收益 |
|---|---|---|
| fsync | DSN 加 `_synchronous=NORMAL` | WAL 下安全(掉电最多丢最后事务),写吞吐 5-50× |
| 页缓存 | `_cache_size=-65536`(64MB,按端侧内存调) | FTS5/元数据热页驻内存 |
| 内存映射 | `_mmap_size=268435456`(256MB) | 向量 blob 扫描减少 syscall |
| auto_vacuum | **新库** `PRAGMA auto_vacuum=INCREMENTAL`(建库即设);已有库转换需 VACUUM 重建,要早决定 | 配合 purge 真正回收空间 |
| 维护作业 | 空闲时:purge(见 §6)→ `PRAGMA incremental_vacuum` → `ANALYZE` → 按膨胀度 `INSERT INTO lite_embeddings_fts(lite_embeddings_fts) VALUES('rebuild')` | 防文件膨胀/统计过期/FTS5 索引漂移 |
| 检索链路裁剪 | 关 `enable_query_expansion`(收益/延迟比最差);`enable_rewrite` 仅长查询开;top_k 30→10(与库内默认 embedding_top_k=10 对齐) | 每次问答省 1-2 次 LLM 调用 |
| 批量 embedding | `BATCH_EMBED_SIZE=16~32`(受 embedding 服务能力约束) | 往返次数 ÷4 |
| 连接策略 | 保留 MaxOpenConns(1)(稳);检索延迟敏感才做读写分池:写池 1 连接 + 读池 2-4 连接(同文件双 DSN,读池 `?mode=ro`) | 消除读写排队 |

---

## 3. L1 · 代码层修复(小改动大收益,按优先级)

1. **入库事务化**(修 C3):`BatchSave` 全流程(主表批插+FTS5+vec)包单事务,vec/FTS5 拼多值批量 INSERT。1000 chunk:2000 commit → 1。
2. **C2 语义实测**(15 行 Go 测试):构造两 KB 各 10 条、KB-A 查询 k=10 过滤 KB-B——若返回 <10 即坐实正确性 bug。修复:外层过采(k×3)再过滤(零风险兜底),或先物化过滤 rowid 集。
3. **删除瘦身**(修 H1):`Find` 改 `Select("id","dimension")`;vec0/FTS5 DELETE 按维度分组拼 `rowid IN (...)` 批量。
4. **FTS5 建表修正**(修 H2):5 个元数据列删除或标 `UNINDEXED`;已有库走一次性分批迁移(顺带修 M2:分批+事务化重建)。
5. **messages 接 cursor + 列裁剪**(修 H4):现成 AfterCursor/BeforeCursor 接进 handler;recent-messages 只取轻列或限 N 轮。
6. **日志降级**(修 M1):每行结果日志降 Debug、去 content_preview(隐私)。
7. **GORM 开关**(修 M4):`SkipDefaultTransaction:true` + `PrepareStmt:true`(与第 1 项互补:一个砍无谓事务,一个合并必要事务)。
8. **KB 列表聚合**(修 M3 之一):循环 COUNT 改三条 `GROUP BY knowledge_base_id` 一次聚合。
9. **CopyIndices/BatchUpdate 批量化**(修 M3 之二):批量 Create+copyVec SELECT 批量;Update 拼单语句 VALUES。

---

## 4. L2 · 架构层(数据量上量级才做,按投入从低到高)

1. **int8 标量量化(首选)**:vec0 原生支持 `int8[dim]` 列,体积与扫描量降 4×;召回损失 1-3% 由 FTS5 混合通道吸收(WeKnora 本就 keywords+vector 混合检索)。改动最小。
2. **两级检索**:bit 向量+汉明距离毫秒级粗筛 top-100 → float cosine 精排。粗筛比 float 快 8-32×。
3. **按 KB 分 shard 表**:`vec_embeddings_{dim}_{kb}` 查询按目标 KB 路由;全局检索并行各 shard 合并 top-k(§5)。
4. **降维**:换 512 维 embedding 模型,扫描量减半、模型更小。
5. **自建 IVF**:k-means 中心表+桶分配,查询只扫 top-n 桶。10 万+ chunk 才值得。
6. **content 单一真相源**(修 M7):lite_embeddings 不存全文改存 chunk 行引用,检索命中回 chunks 取;省 1/3 存储。

**规模对照表**(1024 维,含 FTS5/元数据,粗估):

| chunk 量 | 现状(float32 单表) | L2-1 后(int8) | 结论 |
|---|---|---|---|
| 1 万 | ~30ms / 150MB | ~10ms / 60MB | 无压力 |
| 10 万 | 150-300ms / 1.4GB | 40-80ms / 600MB | L0+L1 后可用 |
| 50 万 | >1s / 7GB | ~300ms / 3.2GB | 需 L2-1/2/3 |
| 100 万+ | 不可行 | ~700ms / 6.4GB | 需 L2-3+4 组合 |

> 不迁移的边界:SQLite 内优化收益封顶约 700ms(百万级)。真到那一步,选项是 usearch(单文件 ANN,Go 可嵌,SQLite 仍管元数据)——「换索引不换库」,代价远小于迁移向量数据库。

---

## 5. 与全局搜索的配合方案

### 分工原则(核心)

```
全局搜索层(毫秒)──发现──> WeKnora RAG 层(秒)──生成──> 答案
   轻索引:title/摘要/tags       重资产:chunk+向量+FTS5
   键入即搜、联想、跳转          显式触发(Enter/「问AI」)
```

两层**不共享存储、不共享锁**:全局搜索要延迟下限,RAG 要召回质量,混在一个 WAL 里互相拖累。

### 路线 A · WeKnora 自身跨库全局检索优化

- 现状 `Retrieve` 不传 KnowledgeBaseIDs 即全局 = vec0 全表 KNN。
- 落地 L2-3 shard 后:全局检索 = 各 KB shard 并行 KNN(端侧 KB 通常 <20,goroutine 并行)→ 归并全局 top-k。
- FTS5 侧天然全局(单表)不动;可加 KB 命中分布路由缓存,下次优先扫热点 shard。

### 路线 B · 与端侧融合搜索引擎协同(kylin-fusion-search 形态)

把 WeKnora 变成融合搜索生态里**一个可搜 bundle**,而非并列系统:

1. **bundle 注册**:`lite_embeddings_fts` 本身就是现成 FTS5 索引——以 knowledge/KB 为粒度注册进全局搜索数据源(bundle="weknora"),全局搜索直接搜到知识库内容,零重复索引。
2. **轻索引同步**:WeKnora 文档入库/删除时向全局层写轻记录(knowledge_id、title、file_type、tags、updated_at)——走全局搜索 write 入口,量级文档级而非 chunk 级(1:1000 缩减)。
3. **下钻链路**:全局搜索命中 → chunk 摘要 → 点「问 AI」→ 带 knowledge_id 过滤调 WeKnora Retrieve → 流式生成(过滤检索复用 §3-2 修复后的语义)。
4. **库与进程边界**:分库分进程(各自 WAL checkpoint 互不干扰);同进程可 ATTACH 但绝不跨库写事务。Android 端沿用 kylin-fusion-search 钉版经验:**一切写入统一走单写闸**。
5. **UX 阶梯**:输入即时联想(全局层 <10ms)→ 结果页含知识命中 → 点按进 RAG 问答(流式)。

### 可直接复用的 kylin-fusion-search 钉版经验

- FTS5 unicode61 下 CJK 连续串=单 token:WeKnora 的 Go 层 bigram 是正确解法(kylin 侧同结论);中缀子串查询仍只有 LIKE 通道。
- 外部内容 FTS5 无 `_content` 影子表的坑;`'rebuild'` 接线(换驱动/重建场景)。
- 端侧一切写入统一单写闸(connect 闸),杜绝 database is locked 家族问题。

---

## 6. 数据治理清单

**模板**:抄仓内最佳实践——audit_logs(默认 90 天+created_at 专用索引+每日小步删)与 memory 子系统(每身份上限 200+expires_at 归档+tombstone 只存指纹)。

| 表 | 动作 |
|---|---|
| chunks/messages/sessions/knowledges | 定期 `DELETE WHERE deleted_at < now-N天` 批量 purge → incremental_vacuum |
| knowledge_processing_spans | 知识删除路径补 span 清理 + 按 created_at 保 30-90 天(纯诊断数据,端侧可激进) |
| task_dead_letters | 90 天 sweep + 管理端 prune 入口 |
| sync_logs / auth_tokens | 「死配置复活」:已实现的 CleanupOldLogs/DeleteExpiredTokens 接进调度,一行调用的事 |
| FTS5/vec0 索引 | 重灌频繁的部署按膨胀度定期 FTS5 'rebuild';vec0 删插无膨胀问题(无图结构) |

---

## 7. 优先行动排序

1. **C2 语义实测**(15 行测试,判定正确性 bug 还是纯性能)
2. **L0 八项配置**(半天):DSN 三参数 + 维护作业 + 检索链路裁剪 + BATCH_EMBED_SIZE
3. **L1-1 入库事务化**(打 repository.go 同步层,收益最大)
4. **L1-4 FTS5 建表修正 + L1-5 messages cursor**(复用已有代码)
5. **治理 purge**(抄 audit 模式)
6. **路线 B bundle 注册 PoC**(全局搜索搜到 WeKnora 知识库)
7. 数据量逼近 10 万 chunk 前启动 L2-1 int8 量化

---

*附注:服务器端(PG/ParadeDB + 专用向量库)的四路完整审计报告未纳入本篇(场景限定端侧);将来「端侧→服务器端」迁移评估时第一检查项为「向量索引仅覆盖 798/1024/3584 三维度,换 embedding 模型维度即全表扫」。*
