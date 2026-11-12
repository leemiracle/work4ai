# C-01 `pingcap/tidb`（40.4K★）—— 只回答一个问题：TiDB 作为 Agent 记忆后端的适配性

> 层级：C 层外围（topics:memory stars>3K）。不克隆，信息源 = GitHub API（README/目录树/源文件原文）+ deepwiki。
> 语言 Go ｜ Apache-2.0 ｜ 定位：MySQL 兼容的分布式 HTAP 数据库（TiKV 行存 OLTP + TiFlash 列存分析）。
> 核验基线：仓库目录树 API `truncated:false`，以下路径均为 HEAD 实测存在。

## 0. 一句话结论

TiDB 是"记忆数据库"而非"记忆系统"：它给 Agent 记忆提供了**向量检索 + ACID 事务 + 实时分析三合一**的单一后端，但向量能力（HNSW）寄生在 TiFlash 副本上，部署重量与约束明显重于嵌入式专用记忆层（LanceDB）或抽象层（mem0）。

## 1. 向量搜索能力与代码位置（均已核验）

### 1.1 VECTOR 类型
- `pkg/types/vector.go` — `VectorFloat32` 类型：4 字节长度头 + float32 数组，强制小端序（非小端机 init 即 panic，vector.go:31-38）；NaN/Inf 拒绝入库（`CreateVectorFloat32`，vector.go:41-55）；文本格式即 JSON 数组（`ParseVectorFloat32` 用 jsoniter 严格解析，拒绝 "null" 与尾随字符，vector.go:223-278）。
- **维度上限 16383**：`maxVectorDimension = 16383`（vector.go:90-101 `CheckVectorDimValid`）。主流嵌入模型（≤4K 维）足够，但对超宽多模态嵌入（如 Jina CLIP v2 的 8K+）仍有余量，属于够用而非宽裕。

### 1.2 距离函数
- `pkg/types/vector_functions.go` — 实现了 `L2Distance`（省 sqrt 的平方距离优化，vector_functions.go:30-48）、`InnerProduct`、`NegativeInnerProduct`、`CosineDistance`（含除零返回 NaN、similarity 截断到 [-1,1]，vector_functions.go:86-119）。均为纯 Go 标量循环（源码注释 "Hope this can be vectorized"），即暴力计算路径。
- 设计文档 `docs/design/2024-07-12-support-vector-index.md` 的函数分阶段表：Phase 1 = L2 + Cosine，Phase 2 = Negative Inner Product，L1 为 TBD（design doc "Limitations and Constraints" 节）。

### 1.3 HNSW 向量索引（关键：索引数据在 TiFlash，不在 TiKV）
- 设计文档：`docs/design/2024-07-12-support-vector-index.md`（tracking issue #55693，作者 zimulala）。核心论断原文："**since the actual vector index data is added to TiFlash, there is no process for populating the index data to TiKV**"。
- DDL：新增 `ActionAddVectorIndex` DDL job，走普通索引同款状态机（None → Delete-Only → Write-Only → Write-Reorg → Public），但 Write-Reorg 阶段不做 backfill，而是同步 `VectorIndexInfo` 元数据到 TiFlash、由 TiFlash 的 LocalIndexerScheduler 以 segment 为单位并行建 HNSW 索引（`VectorIndexHNSWBuilder`），进度查询走 TiFlash 系统表 `system.dt_local_indexes` 的 `ROWS_STABLE_NOT_INDEXED`。
- 查询形态：ANN 只支持 Top-N 语义 —— `SELECT * FROM foo ORDER BY VEC_COSINE_DISTANCE(data, '[3,1,2]') LIMIT 5`，CBO 可选向量索引，支持 `USE INDEX` hint 与 EXPLAIN（design doc "Planner && Executor" 节）。
- TiDB↔TiFlash 协议：tipb 新增 `ANNQueryInfo`（query_type / distance_metric / top_k / ref_vec_f32 / hnsw_ef_search / index_id 等字段，design doc 内 protobuf 摘录）。
- 元数据：`IndexInfo` 增加 `VectorInfo *VectorIndexInfo{Kind, Dimension, DistanceMetric}`（design doc "Meta Information" 节）。

### 1.4 测试证据（目录树实测）
- `pkg/planner/core/casetest/vectorsearch/vector_index_test.go` + `testdata/ann_index_suite_*.json`（planner 层 ANN 索引选路回归）。
- `tests/clusterintegrationtest/t/vector.test`、`vector_index_ddl.test`、`vector_long.test` 及 `python_testers/vector_recall.py`（含召回率测试，说明官方用 recall 指标把关 ANN 质量）。
- 注意区分：`pkg/expression/vectorized.go` / `builtin_vectorized.go` 是**表达式批量化执行**（vectorized execution），与向量搜索无关——检索仓库时同名易混。

## 2. 对 agentic workload 的适配点

### 2.1 HTAP = 记忆写入与记忆分析共库
- README:37（原文核验）：TiFlash 经 **Multi-Raft Learner** 协议实时复制 TiKV 数据，TiDB Server 统一协调两引擎上的查询执行。
- Agent 记忆的典型双负载——高频小事务写入（会话/事实/偏好 upsert，走 TiKV 行存）+ 周期性分析（跨会话聚合、遗忘曲线统计、记忆质量报表，走 TiFlash 列存）——可在**同一份数据**上完成，无需双写管道、无需 ETL。这是 LanceDB/Chroma 类纯向量层完全不具备的。
- agentic 场景具体化：mem0 式"抽取→去重→更新"管线本质是"读旧记忆 + 事务写新记忆"，ACID 保证抽取不丢不重；TiFlash 侧则可对全量记忆做 `GROUP BY user` 的使用统计而无须另建数仓。

### 2.2 "免费 txn"的正确理解
- TiDB 的市场叙事是"向量搜索内建在已有 MySQL 兼容库中，无需另购向量数据库"（README:59 将 vector search 列为 key feature 并链到 docs.pingcap.com 专页）。
- 事务能力是 OLTP 引擎原生的：记忆写入获得 ACID 保障与乐观/悲观事务选择——恰是多数向量库（最终一致、无跨记录事务）的短板。
- TiDB Cloud Serverless 有免费额度属产品层声明 [未验证，未在代码中体现]。

### 2.3 SQL 组合检索
- 向量距离可与 WHERE 过滤、全文索引（repo 内有 `pkg/planner/core/fts_resolve_index.go` 全文索引解析代码，目录树实测）、JOIN、窗口函数组合。
- mem0 式"向量召回 + 元数据过滤"可表达为单条 SQL；记忆元数据表与嵌入列可真正同表/外键关联，无"向量库与元数据库两套一致性"问题。
- 按设计文档语法拼一个 Agent 记忆表的理想形态（语法出自 design doc "Parser" 节，为提案语法非逐字复制）：

```sql
CREATE TABLE agent_memories (
    id      BIGINT PRIMARY KEY AUTO_RANDOM,
    user_id BIGINT NOT NULL,
    kind    VARCHAR(32),              -- fact / preference / episode
    content TEXT,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    VECTOR INDEX idx_emb USING HNSW ((VEC_COSINE_DISTANCE(embedding)))
);
-- 检索：语义近邻 + 元数据过滤 + 时间衰减，一条 SQL 完成
SELECT id, content
FROM agent_memories
WHERE user_id = ? AND kind = 'fact'
ORDER BY VEC_COSINE_DISTANCE(embedding, '[...]') LIMIT 10;
```

### 2.4 横向扩展
- TiKV/PD 多副本 Raft，记忆规模超单机时无需换架构（对比 LanceDB 嵌入式单机、IVF-PQ 单进程索引）；对多租户 SaaS 记忆服务（per-user 分区）是天然形态。

## 3. 与专用记忆层的取舍

| 维度 | TiDB | mem0（抽象层） | LanceDB（嵌入式向量库） |
|---|---|---|---|
| 层次 | 存储引擎（SQL） | 记忆抽取/管理管线，存储可插拔 | 嵌入式向量存储 |
| 向量索引 | 仅 HNSW，且必须 TiFlash | 各后端自带 | IVF-PQ/HNSW 等，单进程 |
| 事务 | ACID（TiKV） | 依赖后端 | 无 |
| 分析 | TiFlash 列存实时分析 | 无 | 无（需导出） |
| 部署重量 | 最小可用 = TiDB+PD+TiKV(×3)+TiFlash，向量索引硬性要求 TiFlash 副本（design doc "A replica of TiFlash is required"） | pip install + 任一后端 | 单文件/单进程 |
| 嵌入管理 | 无（只存不抽） | 有（LLM 抽取管线） | 无 |
| 记忆语义 | 无（纯 SQL） | 用户/会话/Agent 三级记忆 | 无 |

### 1.5 结论判定
- TiDB 与 mem0 不构成竞争而构成**互补候选**——mem0 负责"记忆该记什么"（抽取/更新/遗忘语义），TiDB 可做"记得又稳又可分析"的底座。
- mem0 的 vector store provider 列表是否已含 TiDB [未验证]；若以 TiDB 自建，需自己补齐抽取与遗忘语义（TiDB 不提供任何记忆语义）。
- 对单机轻量 Agent，TiDB 集群运维成本显著高于 LanceDB（嵌入式、单文件、零运维）。

## 4. 局限与风险（面向记忆后端选型）

1. **向量索引硬约束**（design doc "Limitations"）：必须 TiFlash 副本；不能做主键索引；不能复合索引；同列可按不同距离函数建多个索引、同距离函数不可重复建；静态加密 TiFlash 节点不可用；不支持 analyze 统计。
2. **运维一致性**：删向量索引不等待 TiFlash 数据实际删除（design doc Drop 节），存在短暂"幽灵索引数据"窗口，对记忆合规/删除场景需注意。
3. **能力面窄**：单一 HNSW、f32 only、16383 维上限、无量化/磁盘索引选项；大规模记忆库（亿级向量）下与专用 ANN 引擎（DiskANN/IVF-PQ）的召回-成本曲线对比无公开数据 [未验证]。
4. **MySQL 兼容的双刃**：MySQL 9.0 自家 vector 语法官方表态暂不兼容（design doc "MySQL 9.0" 节），跨库迁移 SQL 需改写。

## 5. 可借鉴模式（对本调研的增量）

- **"列存副本承载向量索引"**：把 ANN 从主 OLTP 路径剥离到分析引擎（异步 build + `ROWS_STABLE_NOT_INDEXED` 进度表），A 层记忆系统若做"写入不阻塞检索"可参考该解耦。
- **距离函数即索引定义**：`CREATE VECTOR INDEX ... ((VEC_COSINE_DISTANCE(col)))` 把距离度量写进索引而非查询时指定，杜绝"索引与查询度量不匹配"这类静默退化——比多数向量库的运行时参数更工程化。
