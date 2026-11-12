# explain-10 · internal/application/service/wiki_ingest.go — Wiki 摄取管线的心脏

```
文件路径: internal/application/service/wiki_ingest.go
行数:     3246 行
所属层:   应用服务层（layer:application，Wiki 后台任务族）
一句话:   wikiIngestService——文档进 Wiki 知识库后的异步 LLM 摄取管线：持久化待办队列 + 防抖触发 + 并发批次调度 + LLM 调用模板引擎，承载"Wiki 自动生成"的全部常量与骨架。
```

## 一、角色定位

Wiki 模式下每篇上传文档要被 LLM 抽取实体/概念、合并进共享页面、生成摘要页，织成互链知识库——重 LLM、可失败、可并发的后台工作。本文件定义整个管线的**骨架**：入队 API（`EnqueueWikiIngest`/`EnqueueWikiRetract`）、asynq 处理器分发（`Handle`）、并发与锁的全部常量（Phase 1-4 演进）、批次上下文类型，以及 LLM 调用统一出口 `generateWithTemplate`。批次主循环 `ProcessWikiIngest`/`ProcessWikiFinalize` 在 `wiki_ingest_batch.go`（L192/L916），Map/引文/去重/分类在兄弟文件。属 L2 应用服务层，向下调 L6 模型网关与 L4 仓储，由 asynq wiki 池驱动（container.go:267 注册）。

## 二、内部结构

**1. 常量块（L38-261，约 220 行）**：注释钉版四阶段演进——Phase 1 把索引重建等 KB 级收敛从每批尾部挪到防抖的 `wiki:finalize` 独立 lane（L206-256，N 篇导入只重建一次索引）；Phase 3 移除每 KB 互斥锁，改为行级 claim（`wikiClaimStaleAfter=90m`，L56）+ 按 slug 的 reduce 锁（L61）+ 身份预约 Lua 脚本（L76-91，防两个模型给同一标题发不同 slug）；Phase 4 每 KB 在途上限（`wikiInflightReserveScript` L945，ZSET 过期清扫自愈）。另有防抖 30s、限速退避 60s、每批 5 篇、`wikiLLMMaxTokens=32768`（L190，修 #2604：DeepSeek 默认 8192 截断长 JSON）。

**2. 类型与结构（L263-395）**：`WikiIngestPayload`（asynq 触发器，KB 级、**不携带文档 ID**）；`WikiPendingOp`（行载荷，隐藏 dbID 贯穿 Map/Reduce 供回删行）；`wikiIngestService` 12 个依赖 + 并发件：`liteLocks`（Lite 模式互斥）、`llmRequests`（singleflight 合并相同 prompt）、`promptWarmups`（同前缀首请求串行化，喂饱供应商 prompt 缓存后放行并发）。

**3. 入队与锁（L468-1085）**：`EnqueueWikiIngest` 写一行 task_pending_ops（dedup_key=knowledgeID，重复上传折叠）→ 触发器 `ProcessIn(30s)`（L583-588）；生产触发点在 knowledge_post_process.go:268/317/435。`peekPendingList`（L852，Lite 偷看）vs `claimPendingList`（L879，Redis 原子认领不相交行集）；`withSlugLock`（L912）在 Redis 故障时**开锁放行**——宁冒丢更新之险也不静默丢贡献。

**4. LLM 统一出口 `generateWithTemplate`（L2521-2644）**：模板渲染 → 图片 base64 换占位 token（保护前缀缓存）→ 组装消息 → Temperature 0.3、关 thinking、32768 预算 → 3 次尝试、2s 起指数退避、仅瞬态错误重试（L2732）→ singleflight 合并 → 还原图片。

**5. 文本辅助**：`wikiLinkRE` 解析 `[[slug|显示]]`（L1510）；`sanitizeDeadSummaryLinks`（L1534）纯替换修摘要页死链；`WikiBatchContext`（L1300-1351）用懒加载 fetcher 取代一次性加载 10 万页的内存炸弹。

## 三、外部连接

**依赖**：`chat.Chat`（经 `modelService.GetChatModel` 取 KB 综合模型）、agent 包 8 个 Wiki prompt 模板、asynq/redis/singleflight、wiki/kb/knowledge/chunk 仓储、`SpanTracker`（postprocess.wiki 子 span，L453-466）。**被依赖**：knowledge_post_process（上传触发）、knowledge_clone_move.go:1245/1292（克隆移动）、知识删除清理调 `EnqueueWikiRetract` 与 Redis 墓碑 `WikiDeletedTombstoneKey`（L285，让在途任务快速跳过已删文档）。

## 四、数据流：一篇文档变成 Wiki 页面

① 上传完成 → 后处理写 pending op + 30s 防抖触发；② asynq wiki 池 → `Handle`（L671）→ `ProcessWikiIngest`：Lite 抢进程锁或 Redis 过在途配额 → 校验 KB 开了 Wiki、取模型 → 认领 ≤5 行（异常退出自动 ReleaseByIDs，batch 文件 L391-404）；③ Map 相：LLM 联合抽取实体+概念+详情，批内去重（L2306）；④ Reduce 相：按 slug 加锁合并进共享页面（同前缀经 warmup 串行吃 prompt 缓存），每篇另产摘要页；⑤ 写 finalize lane 行 → 20s 防抖后 `ProcessWikiFinalize` 一次性重建索引导语、清死链、注交叉链、剪空目录。

## 五、设计决策

- **PG 持久队列取代 Redis list**：L349-356 注明旧方案在 4 万文档规模被 24h TTL 逐出——把"应存活"的数据放进了"可丢"的存储，典型架构纠偏；Redis 只留锁/墓碑/配额等短期标记。
- **演进靠注释钉版**：Phase 1-4 每步动机写在常量旁，改代码前必读。
- **双模式贯穿**：`redisClient == nil` 分叉出 Lite 语义（每 KB 串行），小部署零 Redis 可用。
- 批判点：`generateWithTemplate` 一个函数管模板/掩码/缓存键/重试/合并五种关注点；常量块 + 跨 9 个兄弟文件的切片让"一个行为改哪里"的定位成本偏高，好在两条 lane 的 task_type 命名纪律弥补了一部分。

## 六、新人提示

- 批次怎么跑去 wiki_ingest_batch.go，一篇怎么抽去 cite/dedup/taxonomy 文件，本文件是常量与公共件。
- asynq 载荷没有文档 ID，文档在 task_pending_ops 表——排查"没生成"先查它和死信表。
- LLM JSON 解析报 "unexpected end of JSON input"，想起 #2604，先怀疑 max_tokens 截断。
- 观测走 Langfuse：postprocess.wiki span 的 output 有抽取预览（L1426）。
- 延伸：DeepWiki `11.7-wiki-mode-and-auto-wiki-generation.md`、`4.2-document-upload-and-processing.md`。
