# A-07 `memvid/memvid`（16.2K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\memvid__memvid
> Rust（~30+ 模块，src 下 100+ .rs 文件）/ Apache-2.0 ｜ 一句话定位：单文件（.mv2）嵌入式记忆容器——内嵌 WAL + Tantivy 全文索引 + HNSW 向量索引，"从视频载体退化为数据库文件载体"的 AI 记忆层。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
src/
├── lib.rs               # crate 入口，feature 门控（lex/vec/clip/whisper/replay/encryption…）src/lib.rs:77-140
├── memvid/              # 核心引擎（lifecycle=打开/创建/绑定；mutation=提交/真空回收；ask=RAG 问答管线）
│   ├── lifecycle.rs     # Memvid::create/open/bind_memory（记忆↔文件绑定）
│   ├── mutation.rs      # 3814 行：commit/begin_batch/vacuum/tombstone
│   ├── ask.rs           # 1458 行：ask() 混合检索+RRF+语义重排（类 RAG 管线）
│   ├── search/          # Tantivy 引擎选择 + SimHash sketch 预过滤 + 时间过滤
│   ├── memory.rs        # 结构化 MemoryCard（entity-slot-value 三元组卡片）
│   ├── builder.rs       # 并行摄取（parallel_segments feature）
│   └── sketch.rs        # SimHash 帧级草图，亚毫秒候选生成
├── io/                  # WAL（wal.rs）、time_index、manifest_wal——崩溃恢复
├── search/              # 查询解析 parser.rs + tantivy 子引擎
├── vec.rs / vec_pq.rs   # HNSW（≥1000 向量切换）与 PQ 量化
├── text_embed.rs        # 本地 BGE-small 嵌入（384 维）
├── clip.rs / whisper.rs # 多模态：CLIP 图像嵌入、Whisper 音频转写
├── triplet/             # SPO 三元组抽取（摄取期）
├── encryption/          # 口令加密胶囊（.mv2e）
├── replay/              # agent 会话时间旅行回放
└── reader/ table/       # PDF/DOCX/XLSX 等文档摄取与表格结构化
```

单文件布局：Header(4KB) → 内嵌 WAL → 数据段 → Lex 索引段 → Vec 索引段 → Time 索引段 → TOC 页脚（MV2_SPEC.md:10-28）。

## 2. 记忆机制深读（本笔记核心，每个论断必须钉 `相对路径:行号`）

### ⚠️ 前置重大发现："视频作为记忆载体"已被官方废弃
- README 明示：`Memvid v1 (QR-based memory) is deprecated … If you are referencing QR codes, you are using outdated information`（README.md:504-506）。
- 全仓 grep `qr|mp4|h264|ffmpeg` 仅命中 lib.rs:1259-1355 的**测试代码**（把 mp4 当二进制 blob 存取，"video" 只是媒体附件 mime，不是帧内嵌文本编码）。没有任何 QR/视频编码器。
- 现在的"Smart Frame"是纯逻辑概念：`A Smart Frame is an immutable unit that stores content along with timestamps, checksums and basic metadata`（README.md:69）；`draws inspiration from video encoding, not to store video`（README.md:67）。
- 结论：本项目 16.2K 星的名声建立在 v1 的"MP4+QR 码"概念上，但当前 Rust 重写版是**单文件嵌入式数据库**（WAL+Tantivy+HNSW），与视频无关。

### 2.1 写入/抽取管线

写入与检索数据流：

```
put_bytes/embedding ──> WAL(entry+CRC32) ──checkpoint──> 数据段(zstd 帧)
                                            ├─ Lex 段（Tantivy：body/title/uri/tags）
                                            ├─ Vec 段（<1000 线性 / ≥1000 HNSW / PQ 可选）
                                            └─ Time 段（frame_id,timestamp,offset）
检索 search(): 查询解析 → 日期/temporal/replay 预过滤 → SimHash sketch 预过滤
              → Tantivy BM25 → 失败降级 lex fallback
问答 ask(): 问题分类 → 多路查询变体+向量候选+correction → RRF 融合
           → 语义重排 → 时间极值/correction 提权 → context_fragments
```

- 入口 `put_bytes_with_options` / `put_with_chunk_embeddings`（src/memvid/mutation.rs:3104-3146）：载荷 + 可选父级 embedding + chunk embeddings；chunk embeddings 存在时子块才可语义检索（src/memvid/builder.rs:99-104 注释明确"Only parent embedding - chunks won't be searchable via semantic"）。
- 并行摄取 `put_parallel_inputs`：默认段参数 segment_tokens=2048、zstd_level=3、内存上限 4GiB、队列深 64（src/memvid/builder.rs:23-29,46-54），分 Lex/Vec/Time 三类段产物逐一落盘（src/memvid/builder.rs:184-211）。
- 摄取期富化：后台 enrichment worker 做预算内全文重抽取（skim 帧升级）+ 批量 embedding 生成（src/memvid/enrichment.rs:1-15）；另有 SPO 三元组抽取模块（src/lib.rs:110-111）与时态富化（src/lib.rs:150-156）。
- 结构化记忆卡片：`put_memory_card` 写 entity/slot/value 三元组，非严格模式下 schema 校验失败仅告警（src/memvid/memory.rs:78-99）；卡片带版本与时间戳，`supersedes()` 判定新旧覆盖关系（src/types/memory_card.rs:176-248）。

### 2.2 存储后端与数据模型
- 一切在单文件 `.mv2`：`Everything lives in one file: header, write-ahead log, data segments, search indices, and metadata. No sidecar files.`（MV2_SPEC.md:5-7）。
- Header 4KB：magic `MV2\0`、footer_offset、wal_offset/size、WAL 序号、TOC SHA-256（MV2_SPEC.md:35-49）。
- 帧模型（MV2_SPEC.md:91-101）原文：
  ```
  frame_id u64 | uri String (mv2://path) | title String? | created_at u64
  encoding u8 (0=Raw/1=Zstd/2=Lz4) | payload bytes | payload_checksum [u8;32]
  tags Map<String,String> | status u8 (0=active, 1=tombstoned)
  ```
- WAL 嵌入式写前日志，容量按文件大小分档 1-64MB，checkpoint 在 75% 占用或每 1000 事务触发（MV2_SPEC.md:55-85）；entry 含 CRC32 校验（MV2_SPEC.md:64-72）。
- 不变量：单文件保证、append-only 帧、确定性（同 API 调用产出相同字节）、崩溃安全（MV2_SPEC.md:212-218）。
- 向量索引双形态：<1000 向量走未压缩 bincode 线性表，≥1000 切换 HNSW（src/vec.rs:22-23,57-61）；PQ 量化阈值 MIN_VECTORS_FOR_PQ=100，多数段仍以未压缩存储（src/vec.rs:145-157）。

### 2.3 检索策略
- `search()` 主链路（src/memvid/search/mod.rs:46-294）：查询解析→text/field tokens→日期范围预过滤→（可选）temporal/replay 过滤→SimHash sketch 预过滤（hamming_threshold=32、max_candidates=max(top_k*10,500)，BM25 兜底重排）（src/memvid/search/mod.rs:191-229）→Tantivy BM25→失败则 lex fallback。
- `ask()` 是完整 RAG 式问答管线（src/memvid/ask.rs:23-437）：
  - 问题分类启发式：aggregation/recency/analytical 三类问题分别放大 top_k ×3/×2/×5（src/memvid/ask.rs:39-57）；
  - 四级降级：精确查询→OR 析取→词法 fallback→单复数扩展→timeline 采样兜底（src/memvid/ask.rs:131-208）；
  - 多候选列表（词法变体+向量+**correction 专用检索** `uri:mv2://correction/*`）用 RRF 融合，RRF_K=60（src/memvid/ask.rs:19,280-306）；
  - 语义重排：对每 hit 取帧 embedding 算 cosine 后 reorder（src/memvid/ask.rs:476-548）；时间极值提升（update/recency 问题把最新/最旧帧前置，src/memvid/ask.rs:326-332）与 correction 最终提权（src/memvid/ask.rs:367-369）。
- 向量默认 384 维 BGE-small、cosine、HNSW M=16/ef_construction=200（MV2_SPEC.md:168-173）。

### 2.4 遗忘·整合·演化
- 删除即墓碑（status=1 tombstone，MV2_SPEC.md:77 `0x03 Frame delete (tombstone)`）；`vacuum()` 全量重写：仅 Active 帧载荷重写回文件、清空全部索引段强制重建（src/memvid/mutation.rs:3013-3063）——O(n) 全文件重写，非增量 compaction。
- 演化机制：MemoryCard 版本链 `supersedes()`（src/types/memory_card.rs:248）；correction 帧（`mv2://correction/*` URI）在问答时高优先覆盖旧信息（src/memvid/ask.rs:278-297）。
- 无自动 decay/遗忘曲线；时间演化靠 Time Index + temporal track（MV2_SPEC.md:134-146）与 replay 时间旅行（src/lib.rs:124-127）。

### 2.5 注入上下文的方式
- `AskResponse` 携带 `context_fragments`（rank/frame_id/uri/score/chunk_text 完整片段），支持 `context_only` 模式只取上下文不合成答案（src/memvid/ask.rs:382-424）——即"拼装好的检索包"交给外部 LLM；`build_context(hits)` 生成拼接上下文（src/memvid/ask.rs:323,380）。无显式 token 预算控制，仅 snippet_chars 截断（src/memvid/search/mod.rs:78-82）。
- 记忆绑定：`bind_memory` 将 memory_id(Uuid)/api_url 写入文件头（src/types/binding.rs:12-20；src/memvid/lifecycle.rs:812），支持"这个文件属于哪个 agent 记忆库"的元数据级归属。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**摘录 1：单文件格式总布局（MV2_SPEC.md:10-28）**
```
│ Header                 │ 4 KB                               │
│ Embedded WAL           │ 1-64 MB (capacity-dependent)       │
│ Data Segments          │ Variable - Frame payloads          │
│ Lex Index Segment      │ Tantivy index (optional)           │
│ Vec Index Segment      │ HNSW vectors (optional)            │
│ Time Index Segment     │ Chronological ordering             │
│ TOC (Footer)           │ Segment catalog + checksums        │
```

**摘录 2：SimHash sketch 预过滤参数（src/memvid/search/mod.rs:191-199）**
```rust
if self.has_sketches() && has_text_terms && !request.no_sketch {
    let sketch_options = crate::SketchSearchOptions {
        // Use relaxed threshold for better recall - BM25 will rerank anyway
        hamming_threshold: 32,
        // Get more candidates than needed - BM25 will select the best
        max_candidates: (params.top_k * 10).max(500),
        min_score: 0.0,
    };
```
且 ask() 显式 `no_sketch: true`，注释承认"SimHash can filter out semantically relevant documents that use different wording"（src/memvid/ask.rs:105-107）。

**摘录 3：RRF 融合多路候选（src/memvid/ask.rs:299-306）**
```rust
// Fuse all candidates with RRF and rebuild retrieval.
if let Some(fused) = fuse_hits_rrf(candidate_lists, effective_top_k.max(24)) {
    retrieval.hits = fused;
    retrieval.total_hits = retrieval.hits.len();
    if vector_used {
        retrieval.engine = SearchEngineKind::Hybrid;
    }
}
```

**摘录 4：HNSW 切换阈值（src/vec.rs:22-23,57-61）**
```rust
const HNSW_THRESHOLD: usize = 1000;
...
pub fn finish(self) -> Result<VecIndexArtifact> {
    if self.documents.len() >= HNSW_THRESHOLD {
        return self.finish_hnsw();
    }
```

**摘录 5：vacuum 全量重写（src/memvid/mutation.rs:3013-3054 节选）**
```rust
pub fn vacuum(&mut self) -> Result<()> {
    self.commit()?;
    let mut active_payloads: HashMap<FrameId, Vec<u8>> = HashMap::new();
    ... // 读出全部 Active 帧载荷后逐帧重写
    self.toc.segments.clear();
    self.toc.indexes.lex_segments.clear();
    self.toc.segment_catalog.vec_segments.clear();
```

### 2.6 多模态与安全子系统（补充）
- CLIP 图像嵌入（feature `clip`）支持"视觉检索"——但检索的是**作为媒体附件存入的图像**的嵌入（src/clip.rs:1-455 含完整本地 CLIP 推理与 L2 归一化），与 v1"帧内嵌文本的视觉检索"不是一回事。
- Whisper 本地转写（feature `whisper`，src/whisper.rs:399-418 含 RMS 静音检测/重采样）：音频→文本→入帧，属于摄取管线而非检索。
- 加密胶囊 `.mv2e`：口令派生密钥封装整个文件（feature `encryption`，src/encryption/capsule.rs、capsule_stream.rs；lib.rs:129-132），tests/encryption_capsule.rs 有集成测试——"可邮寄的记忆文件"的保密形态。
- ACL：帧级访问控制列表（src/memvid/acl.rs、src/types/acl.rs），search 命中后按 `acl_enforcement_mode` 过滤并重算 total/context（src/memvid/search/mod.rs:266-274）——默认非强制，Enforce 模式才生效。
- Replay（feature `replay`）：记录 agent 的 put/find 动作，支持 `as_of_frame/as_of_ts` 时间旅行查询（src/memvid/search/mod.rs:155-187；src/replay/engine.rs）——"回放 agent 当时看到了什么"。
- 结构化文档感知：PDF/DOCX/PPTX/XLSX 读取器 + 表格布局检测（src/reader/、src/table/layout.rs:93 距离几何）+ SymSpell 修复 PDF 断词（feature `symspell_cleanup`，data/ 内置英文词频字典）。
- 图检索：triplet SPO 抽取（src/triplet/extractor.rs）+ graph_search 混合检索（src/lib.rs:110-114），与 MemoryCard 实体槽位体系并行。

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）
- README.md:47-53 声明：`+35% SOTA on LoCoMo`、`+76% multi-hop, +56% temporal vs. the industry average`、`0.025ms P50 / 0.075ms P99`、`1,372× higher throughput`、自称 "Fully reproducible benchmarks"。**全部 [自封][不可复现]**——仓库内无 LoCoMo 评测代码/数据/脚本（全仓无 eval 目录），bench/ 下仅 criterion 微基准：`search_precision_benchmark.rs` 用 5 条合成主题句的小语料测隐式 AND 运算符改动的精度/延迟（benches/search_precision_benchmark.rs:1-50），与 LoCoMo 口径完全无关。
- 另一基准 `benches/vec_search_benchmark.rs` 只测向量检索路径；`examples/generate_performance_report.rs` 是报告生成器而非评测。
- 工程质量信号（正面）：tests/ 有 crash_recovery/doctor_recovery/replay_integrity/mutation/model_consistency 等崩溃与一致性集成测试，CI 完整（.github/workflows/ci.yml）——格式层的可靠性主张有测试支撑，区别于 README 的性能主张。
- "0.025ms P50" 更可能是单文件内 sketch/BM25 单查询微基准，而非端到端 ask()（ask 含四级降级重试+embedding，远不止 0.025ms）。
- "替代 RAG"声明（README.md:60 `Instead of running complex RAG pipelines … fast retrieval directly from the file`）：实际成色=**单机嵌入式混合检索引擎**（BM25+向量+RRF+启发式重排），替代的是"向量化数据库服务"的部署形态，而非检索增强范式本身——ask.rs 本身就是一条 RAG 管线。极限：(a) 容量受单文件与 4GiB 摄取内存上限约束（builder.rs:27），vacuum 是全文件重写；(b) 精度依赖启发式问题分类与四级 fallback，无交叉编码器重排；(c) 成本=零部署（单文件、无服务）但换来单写者文件锁（src/lock.rs、lockfile.rs）与不可水平扩展。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **单文件记忆胶囊**：WAL+索引+数据+TOC 全内嵌、SHA-256 逐段校验、append-only 不变量（MV2_SPEC.md:212-218）——可像文件一样备份/邮件传送/挂在 git LFS 里的"记忆资产"，是 mem0（服务+DB）之外的一个正交形态。
2. **correction 作为一等公民**：专属 `mv2://correction/*` 命名空间 + 检索后最终提权（ask.rs:278-297,367-369），让"用户纠错"压过一切排序信号——对话记忆里纠错优先于相关性的具体实现范式。
3. **问题类型感知的检索预算**：aggregation/recency/analytical 三分类动态放大 top_k 与查询改写（ask.rs:39-81），比固定 top-k 的朴素 RAG 更贴对话记忆场景。
4. **SimHash sketch 预过滤 + 明确弃用条件**：search 用 sketch 提速、ask 关掉 sketch 保精度（ask.rs:105-107）——"同一索引，两套精度/延迟策略"的取舍样本。
5. **MemoryCard(entity-slot-value) + supersedes 版本链 + schema 严格/宽松双模式**（memory.rs:78-99；types/memory_card.rs:248）：结构化槽位记忆与文档帧并存于同一容器。
6. **单文件内多索引段并存**（Lex/Vec/Time 三段+TOC 目录，MV2_SPEC.md:20-27）：同一份记忆可选启用哪类索引（feature 门控），容器格式层面解耦"数据"与"索引策略"。
7. **记忆绑定元数据**（bind_memory 将 memory_id/api_url 写入文件头，lifecycle.rs:812；types/binding.rs:12-20 含 machine_id/last_synced）：单文件记忆资产与云端记忆库的可选锚点，支持"本地文件↔云库"同步定位。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- **概念债**：项目名与 16K 星建立在已废弃的 QR/视频机制上，新用户认知成本高（README.md:504-506 需要专门辟谣段）。
- vacuum 全量重写 + 索引全清重建（mutation.rs:3050-3063）：大文件上代价高昂；墓碑帧不回收则文件只增不减。
- 多路 fallback 每级都重跑一次 search（ask.rs:131-208）：最坏情况一次 ask 触发 4+ 轮全索引查询，尾延迟不可控。
- 单写者模型：FileLock/lockfile（src/lock.rs）不支持并发写扩展；无网络层，"替代向量数据库"仅限单机。
- 启发式问题分类（is_aggregation/is_recency 等）为关键词级，跨语言（中文问题）效果存疑。
- 加密为 feature-gated 可选（lib.rs:129-132），默认文件明文+无 ACL 强制（search/mod.rs:271 才按 Enforce 模式过滤命中）。

## 7. 一句话对比 mem0
mem0 是"云端服务化的记忆抽取/更新层"（LLM 抽事实入 DB），memvid(Rust v2) 是"单文件自包含的嵌入式记忆数据库"（容器格式+混合检索引擎）——前者管记忆怎么提炼，后者管记忆怎么打包与检索；且 memvid 的明星卖点（视频存记忆）已在代码层面自我否定。
