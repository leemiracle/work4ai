# A-02 `MemPalace/mempalace`（58K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\MemPalace__mempalace
> Python 3.9+，v3.7.1 ｜ 核心包 79 个 .py / ~2.2MB，最大文件 mcp_server.py 8080 行 ｜ 测试 155 文件 / ~3MB ｜ MIT ｜ 一句话定位：local-first 逐字存储记忆宫殿——"不做抽取、只做结构化索引"，主打零 API、零 LLM 的检索基线

## 0. 反虚荣甄别（先回答"58K 星的实质"）
- **真实实现深度：高，且反营销姿态罕见。** 核心包 79 文件 2.2MB（mempalace/ 目录实测），测试 155 文件 3.1MB（tests/ 实测）——测试代码量超过核心包一半，不是 star-farm 空壳。
- README 主动声明"impostor sites"风险（README.md:16-17），docs/HISTORY.md:63 有"2026-04-11 Impostor domains and malware"公告——项目曾遭仿冒域名投毒，星数部分反映这场社区事件而非纯技术热度。
- **基准诚实度是三仓中最高的**：README.md:216-218 明确拒绝发布"100%"数字并承认"最后 0.6% 是 inspecting specific wrong answers 达成的 teaching to the test"；README.md:229-233 拒绝与 Mem0/Zep/Supermemory 横向列表，理由是"检索 recall 与端到端 QA accuracy 不可比"。**"best-benchmarked"声明的实质：自封措辞，但可复现性做得最扎实**——评测脚本（benchmarks/longmemeval_bench.py 等 5 个）、逐题结果 jsonl/json（benchmarks/results_*_20260414_*，8 个文件）、50/450 切分文件（benchmarks/lme_split_50_450.json）全部入库，`uv run python benchmarks/longmemeval_bench.py <dataset>` 一条命令可跑（README.md:242）。**[自封但高可复现]**。

## 1. 架构总览（目录地图）
```
mempalace/
├── palace.py(1668行)        # 宫殿骨架：集合管理、closet 生成、mine 锁、FTS5 校验
├── miner.py(2289行)         # 文件→drawer 摄取：gitignore、room 路由、分块、日期抽取
├── convo_miner.py(1238行)   # Claude Code/Gemini 会话 JSONL→wing/room
├── searcher.py(1967行)      # 混合检索核心（本笔记 §2.3）
├── layers.py(529行)         # L0-L3 四层记忆栈 + wake_up 注入
├── closet_llm.py            # 可选 LLM 增强 closet（opt-in，stdlib urllib 零依赖）
├── knowledge_graph.py(764行)# SQLite 时序三元组图
├── hallways.py / palace_graph.py  # wing 间连接 / 图视图
├── backends/                # chroma(默认)/sqlite_exact/milvus/qdrant/pgvector 五后端
├── mcp_server.py(8080行)    # 44+ MCP 工具（读/写/维护，见文件头 mcp_server.py:7-22）
├── sweeper.py / daemon.py / wal.py / dedup.py  # 会话级逐条 drawer / 常驻 / 预写日志 / 去重
└── i18n/(15语言) entity 检测模式
```

## 2. 记忆机制深读

### 2.1 写入/抽取管线（谁触发、规则为何）
- 触发：CLI `mempalace mine <dir>`（README.md:177-178）或 Claude Code hook 自动保存（README.md:269-287）或 MCP 工具 `mempalace_add_drawer`。
- 日期抽取五级瀑布（miner.py:1164-1361）：ISO 正文匹配 `_try_iso_match`（miner.py:1164）→ 文件名日期 `_try_filename_date`（:1177）→ frontmatter `_try_frontmatter_date`（:1222）→ 正文正文日期 `_try_content_body_date`（:1275）→ mtime `_try_mtime_date`（:1349），统一入口 `_extract_content_date`（:1361）——authored_at 是检索排序与时间窗过滤的根基，故抽取链最重。
- wing（人/项目）路由：会话按路径解析 `_resolve_wing()`（convo_miner.py:850）；文件按已知实体词表 `add_to_known_entities()`（miner.py:882）。
- **核心理念：无 LLM 抽取**。`miner.py` 纯规则：room 路由四级优先级（目录名→文件名→关键词计分→general），`detect_room()` miner.py:583-622；分块 `chunk_text()`（段落边界优先、chunk_index+line_start/line_end 定位）miner.py:630-646。
- **closet（二级索引）**：`build_closet_lines()` palace.py:643-703 从 drawer 内容用正则抽"主题指针行"——动作动词短语（`built|fixed|wrote|added|...` 正则，palace.py:697）+ Markdown 标题（palace.py:701）+ 出现≥2 次的专名实体（palace.py:688-691，CoCA 高频词过滤 palace.py:685-686，复合专名预掩码 "Claude Code"/"GitHub Copilot" palace.py:670-674）。指针格式 4 段式 `topic|entities|YYYY-MM-DD:Lstart-Lend|→drawer_ids`（palace.py:650）。
- 可选增强：`closet_llm.py` 模块头自述 "OPTIONAL and opt-in... Core memory operations remain API-free by design"，任意 OpenAI 兼容端点重建 closet（closet_llm.py:1-40）。
- **会话摄取管线**（`convo_miner.py`，1238 行）：Claude Code/Gemini 的 JSONL 会话按"交换轮"分块而非固定窗口——`chunk_exchanges()`/`_chunk_by_exchange()`（convo_miner.py:298/334），room 走专用 `detect_convo_room()`（convo_miner.py:484），wing 由路径解析 `_resolve_wing()`（convo_miner.py:850）；增量靠 mtime 比对 `_is_unchanged_since_last_mine()`（convo_miner.py:828）。
- **消息级摄取**（`sweeper.py`）：每条 user/assistant 消息一个 verbatim drawer，幂等可续跑——`sweep()` sweeper.py:203，游标 `get_palace_cursor()` sweeper.py:157，确定性 ID `_drawer_id_for_message(session_id, message_uuid)` sweeper.py:193（UUID 决定幂等）。

### 2.2 存储后端与数据模型
- 空间隐喻三层：**wing（人/项目）→ room（主题）→ drawer（原始内容块）**，外加 **closet**（指向 drawer 的指针集合）与 **hallway**（wing 间连接，hallways.py:198）。README.md:28-32 原文："people and projects become wings, topics become rooms, original content lives in drawers"。
- 后端契约 `backends/base.py` + 5 实现（README.md:160-166 表）；默认 ChromaDB 嵌入式。换后端零改业务码（resolve_backend_name palace.py:374）。契约层异常族完备：`PalaceNotFoundError / CollectionNotInitializedError / BackendClosedError / UnsupportedFilterError / UnsupportedCapabilityError`（backends/base.py:26-65）——能力探测式契约（如 lexical_search 可选）是 5 后端异构共存的关键。
- 并发与一致性工程：文件级 mine 锁 `mine_lock()`（palace.py:826-946，含陈锁回收 `reap_stale_mine_locks` palace.py:1012）、宫殿级锁 `mine_palace_lock()`（palace.py:1281）、fork 后锁状态重置（palace.py:1187）、FTS5 完整性事后校验 `_validate_palace_fts5_after_mine`（palace.py:1116）；预写日志 `wal.py` 与常驻 `daemon.py` 支撑 hook 自动保存。
- 后端规模旁证：chroma.py 2609 行 / pgvector.py 1631 / qdrant.py 1483 / milvus.py 1333 / sqlite_exact.py 1240——每个后端都是完整实现而非薄封装。
- 时序知识图 SQLite schema 原文摘录（knowledge_graph.py:163-178）：```sql
CREATE TABLE IF NOT EXISTS triples (
    id TEXT PRIMARY KEY, subject TEXT NOT NULL, predicate TEXT NOT NULL,
    object TEXT NOT NULL, valid_from TEXT, valid_to TEXT,
    confidence REAL DEFAULT 1.0, source_closet TEXT, source_file TEXT,
    source_drawer_id TEXT, adapter_name TEXT, ...
```
  每条三元组带 `valid_from/valid_to` 有效窗，查询支持 `as_of` 时间点过滤（`_temporal_filter_sql` knowledge_graph.py:106）与失效/替代操作（invalidate:338 / timeline:591）——**写入时保留证据链（source_drawer_id），图可回溯到原文**。
- 实体 id 规则朴素：`name.lower().replace(" ","_").replace("'","")`（knowledge_graph.py:227-228）——同形异义实体（"Apple 公司/苹果水果"级）无消歧，规模大时是隐患。
- hallway（wing 间连接）：基于 wing 内共现实体计算 `compute_hallways_for_wing()`（hallways.py:198），持久化为 JSON 列表文件（`_load_hallways/_save_hallways` hallways.py:86/122），id 由 `wing+entity_a+entity_b` 哈希决定（hallways.py:185）。
- schema 迁移手写 introspect：无 `ADD COLUMN IF NOT EXISTS`，靠 `PRAGMA table_info` 逐列补（knowledge_graph.py:188-202）——单机 SQLite 的务实选择。

### 2.3 检索策略（本仓最值得抄的部分）
入口 `search_memories()` searcher.py:1601-1915，四级信号：
1. **向量主检索**：过采样 `pool = _candidate_pool_size()`（searcher.py:1709），drawer 集合直查（searcher.py:1710-1720）；
2. **closet 秩次加护（boost-as-signal-not-gate）**：closet 命中仅作排名信号，注释明确 "Closets are a ranking SIGNAL, never a GATE"（searcher.py:1702-1708，防"弱 closet 回归"）；加护表 `CLOSET_RANK_BOOSTS = [0.40, 0.25, 0.15, 0.08, 0.04]` + `CLOSET_DISTANCE_CAP = 1.5`（searcher.py:1754-1755），实现为距离减法 `effective_dist = clamp(dist - boost, 0, 2)`（searcher.py:1788）——注释解释了为何用**秩次而非绝对距离**：叙事内容 closet 距离挤在 1.2-1.5 区间无区分度（searcher.py:1751-1753）；
3. **BM25+向量凸组合重排**：`_hybrid_rank()` searcher.py:276-330，`0.6*vec + 0.4*bm25_minmax`（searcher.py:279-280,315）；BM25 在**候选集内**算 corpus-relative IDF 再 min-max 归一（searcher.py:291-293）；距离→相似度按后端声明的 metric 分别映射（cosine: `1-d` / l2: `1/(1+d)` / ip: logistic，searcher.py:236-255）；
4. **源内 grep 精化（drawer-grep enrichment）**：closet 加护命中者，回到源文件全部 chunk 里做查询词计数选最佳 chunk±1 邻接，替换向量命中的 chunk（searcher.py:1821-1877，注释："The closet said 'this source is relevant'; vector may have picked the wrong chunk within it; grep picks the right one"），10K 字符截断（searcher.py:1826）。
- 候选策略 `"union"`：并入后端 lexical_search 候选，BM25-only（distance=None）候选在设了 max_distance 时被拒（searcher.py:1646-1661）。
- 降级路径完整：HNSW 容量漂移探测→`vector_disabled` 走 sqlite-only BM25（searcher.py:1642-1645,795）；closet 集合缺失→纯 drawer 检索（searcher.py:1747-1749）。
- **BM25 实现细节**（`_bm25_scores()` searcher.py:166-223）：Okapi 标准 k1=1.5 / b=0.75（searcher.py:169-170）；IDF 用 Lucene/BM25+ 平滑公式 `log((N-df+0.5)/(df+0.5)+1)` 保证非负（searcher.py:175-176,206），且 docstring 明确承认 IDF 是**候选集内**的（"IDF then reflects how discriminative each query term is within the candidates" searcher.py:178-180）——小候选集重排的正确取舍，代价是排序依赖池大小。
- 结果信封字段（`_search_result_envelope` searcher.py:1334 起）：每条命中携带 `distance`（原始）/`effective_distance`（扣 boost 后）/`closet_boost`/`matched_via`（drawer vs drawer+closet）——**检索可解释性为一等公民**，对照 mem0 的 explain 开关。
- 嵌入层（`embedding.py` 模块 docstring）：三种模型可选——`minilm`（all-MiniLM-L6-v2, 384d 存量默认）/ `embeddinggemma-300m`（ONNX q8，Matryoshka 截断 384d，100+ 语言，跨语种 cosine ~0.88 vs MiniLM ~0.35）/ `openai-compat`（任意 /v1/embeddings 端点，LM Studio/llama.cpp/vLLM/Ollama）；设备 auto→CUDA→CoreML→DirectML→CPU 链式回退（"mining must still work on a laptop without CUDA"）；**换模型必须 `repair rebuild-index`**（向量空间不同）。
- 配置优先级 env > `~/.mempalace/config.json` > 默认（config.py:4）；默认宫殿 `~/.mempalace/palace`、集合名 `mempalace_drawers`（config.py:221-222）；分块默认值单一真源在 config.py:269-271。

### 2.4 遗忘·整合·演化
- 无 decay。演化=KG 三元组 `valid_to` 关窗 + supersede（mcp 工具 `mempalace_kg_supersede`）；去重走显式命令 `dedup_palace()`（dedup.py:169）。
- 去重算法（dedup.py:98-146）：源内分组→按文档长度降序贪心保留，每条与已保留集做向量查询（top-5），距离 < 阈值即判重删除；**默认 dry_run=True**，<20 字符直接删；失败时保守保留（dedup.py:139-140）。
- 层级再组织：`repair.py`（2413 行，含 rebuild-index）；虚拟行号网格：drawer 永不改写、closet 指针 `→2026-01-18:L55-L72` 在**读时**应用行号网格（searcher.py:1918-1934 注释 "Source drawer text is never mutated"，渲染入口 `render_with_line_numbers` searcher.py:1933）。
- 实体注册表：已知实体跨 wing 复用 `_refresh_known_entities_cache()` / `add_to_known_entities()`（miner.py:778/882），词表 `data/known_systems.json` + CoCA 高频词表 `data/coca_content_words.json`。

### 2.5 注入上下文方式
- 四层栈 `MemoryStack`（layers.py:384-431）：L0 身份（~100 tok，`~/.mempalace/identity.txt` 纯文本，layers.py:39-73）→ L1 精要故事（~500-800 tok，最多 15 drawer / 3200 字符硬顶，layers.py:88-90）→ L2 按需 wing/room 召回 → L3 深检索。`wake_up()` 输出 L0+L1 约 600-900 token（layers.py:404-423）直接注入 system prompt。
- L1 排序的诚实注释：importance 字段实际不存在，filed_at（最新优先）才是**当前生效**的排序信号（layers.py:129-138）——预设了 importance 字段等未来打分填充。
- 注入编排的三种触发面：CLI `mempalace wake-up`（README.md:184）；Claude Code/Codex/Cursor 的 session-start hook 自动召回（README.md:269-287）；MCP 工具按需（`mempalace_search` 等返回结构化 dict，供 agent 自己拼 prompt）。
- MCP 工具面（mcp_server.py 文件头 :7-22 + 全文去重统计）：读（status/list_wings/list_rooms/get_taxonomy/search/check_duplicate/get_drawer/list_drawers/list_hallways/list_tunnels/find_tunnels/follow_tunnels/graph_stats/diary_read/artifact_get/event_list/whoami 类）｜写（add_drawer/delete_drawer/delete_by_source/diary_write/event_append/kg_add/hallway 删建/artifact_put/checkpoint 类）｜维护（reconnect/hook_settings 等）；支持 `--read-only` 模式：写工具从 tools/list 隐藏并在分发层拒绝（mcp_server.py:297-321）。
- Agent 协作面：每个 specialist agent 独占 wing + diary，运行时经 `mempalace_list_agents` 发现、"不撑大系统提示"（README.md:262-267）；logstream 事件（event_append/event_wait/event_ack）+ artifact 交接（artifact_put/get）构成多 agent 总线（mcp_server.py:7380 logsync 线程佐证）。

## 3. 关键代码摘录
摘录①（closet 加护，searcher.py:1776-1788）：
```python
if source in closet_boost_by_source:
    c_rank, c_dist, c_preview = closet_boost_by_source[source]
    if c_dist <= CLOSET_DISTANCE_CAP and c_rank < len(CLOSET_RANK_BOOSTS):
        boost = CLOSET_RANK_BOOSTS[c_rank]
        matched_via = "drawer+closet"
effective_dist = max(0.0, min(2.0, dist - boost))
```
摘录②（源内 grep 精化，searcher.py:1860-1868）：
```python
query_terms = set(_tokenize(query, stop_words))
best_idx, best_score = 0, -1
for idx, d in enumerate(ordered_docs):
    s = sum(1 for t in query_terms if t in d.lower())
    if s > best_score: best_score, best_idx = s, idx
start = max(0, best_idx - 1); end = min(len(ordered_docs), best_idx + 2)
expanded = "\n\n".join(ordered_docs[start:end])
```
摘录③（stdio 保护，mcp_server.py:27-44）：MCP stdio 模式下 Python 层+fd 层双重 stdout→stderr 重定向，防 chromadb/onnxruntime 的 C 层 banner 打破 JSON-RPC。

摘录④（去重贪心，dedup.py:120-138）：
```python
results = col.query(query_texts=[doc], n_results=min(len(kept), 5),
                    include=["distances"])
for rid, dist in zip(results["ids"][0], dists):
    if rid in kept_ids_set and dist < threshold:
        is_dup = True; break
```
摘录⑤（时序 KG 查询窗，knowledge_graph.py:106 附近的 as_of 过滤 + invalidate:338 / timeline:591）：三元组级 `valid_from/valid_to` 双时间戳 + `as_of` 点查询，替代"整条记忆过期"的粗粒度方案。

## 4. 基准/评测声明
| 声明 | 数值 | 定性 |
|---|---|---|
| LongMemEval raw R@5 | 96.6%（500题，零 LLM）| [自封-可复现] 结果文件+脚本+切分入库 |
| hybrid v4 held-out 450 | 98.4% | [自封-可复现] README.md:204 自称"honest generalisable figure" |
| hybrid v4 + Haiku rerank | 100% | [自封-过拟合已自认] BENCHMARKS.md:87-92 承认 99.4→100 是 teaching to the test，**只作内部数字不进公开面** |
| 对比表（Mem0/Zep/Supermemory/Mastra）| 混排 QA accuracy 与 R@5 | [拒绝发布] README.md:229-233，罕见克制 |
| LoCoMo R@10 | raw 60.3% / hybrid 88.9% | [自封-可复现] README.md:224-225 |
| ConvoMem / MemBench | 92.9% / 80.3% | [自封-可复现] README.md:226-227，results_* 文件在库 |

关键：其 R@5 是"检回标注会话"而非答案正确率（BENCHMARKS.md:45 注明），与 mem0 的 LoCoMo QA 分**不同口径**，不能直接比大小。竞品标注也佐证口径混乱：同表将 Supermemory 标为 "~99% QA accuracy, not R@5, Experimental"、Mastra 标为 "94.87% QA accuracy, different metric"（BENCHMARKS.md:70-78）。复现资产清单：`longmemeval_bench.py / locomo_bench.py / convomem_bench.py / membench_bench.py / mine_bench.py` + `HYBRID_MODE.md` + `model_eval/` + 8 份 `results_*_20260414_*` 逐题结果 + `lme_split_50_450.json` 切分（benchmarks/ 目录实测）。

## 5. 可借鉴模式（区别于 mem0 的增量）
- **"boost-as-signal-not-gate"**：任何二级索引（closet/摘要/图）只调分不过滤，保证基线直检永远可达——对 mem0 式 threshold 前置门槛是一剂反面解药。
- **两级检索粒度**：源级（closet 定位哪个文件/会话相关）+ chunk 级（源内 grep 选段），中间用"秩次 boost"而非距离拼接——叙事型语料上比绝对距离稳健。
- **读时行号网格**：原文永不改写，指针带 `date:Lstart-Lend`，检索结果可回跳原 span——可审计性与 mem0 的"抽取后原文即丢"形成对照。
- **时序 KG 的证据链**：三元组带 source_drawer_id + valid_from/to（knowledge_graph.py:163-178），支持 as_of 查询——图记忆的时间处理比 mem0 的 expiration_date 通用。
- **四层 token 预算注入**：L0/L1 常驻 ~900 tok，L2/L3 按需——比"一次 search 塞 top-k"更接近 agent 工作记忆分层。

## 6. 局限与风险
- 正则抽取的 closet 对非英文/隐性主题弱（closet_llm.py:1-4 自认），i18n 靠 15 份 locale 正则模式硬扛（mempalace/i18n/）。
- mcp_server.py 8080 行单文件（含 logstream/agent 协调/watchdog 多子系统），巨石化明显；wing/room 隐喻映射依赖 `data/known_systems.json` 等静态词表。
- BM25 在候选集内算 IDF（searcher.py:291-293）——候选池大小变化会改变 IDF，排序不稳定（候选数本身受 pool_size 启发式影响，searcher.py:1181）。
- L1 wake-up 无真正重要性评分：importance 字段全库缺失，实际按 filed_at 新鲜度排序（layers.py:129-138 自认），"top moments" 承诺未完全兑现。
- 检索日期窗过滤在**检索后**执行（ChromaDB 不支持字符串 $gte/$lt，searcher.py:1632-1635），靠扩池缓解——深窗口查询可能漏召回（响应含 `date_filter_pool_truncated` 自曝，searcher.py:1635）。
- 58K 星与"HISTORY.md 仿冒域名事件"强相关，社区热度≠采用度；PyPI 周下载量需另行验证。

## 7. 一句话对比 mem0
mem0 用 LLM 在**写入端**把对话蒸馏成事实句；mempalace 拒绝蒸馏、把力气全花在**检索端**（closet 指针+秩次 boost+源内 grep 精化），用可复现的 R@5 证明"逐字存储+好检索"这一极简路线足以打平重管线——是对"抽取式记忆"路线最系统的反驳样本。

## 附：工程卫生度抽查（反虚荣补证）
- 测试资产：tests/ 155 个 py 文件、~3.1MB，超过核心包体积的一半；测试名与 issue 号联动（如 `#1815`、`#1580`、`#1222`、`#2063`、`#1128` 等在源码注释中反复出现，searcher.py:337/1834/1643、palace.py:634）——**回归测试由真实事故驱动**，非凑覆盖率。
- RFC 化演进：源码注释引用 "RFC 001 backend metric declaration"（searcher.py:230,262）、"RFC 002 §5.5"（knowledge_graph.py:191）、"Tier 6a"（palace.py:650,664）——架构变更有编号设计文档传统。
- 版本卫生：CHANGELOG.md + version.py 独立模块 + uv.lock 锁定；Docker 多架构（amd64/arm64）与 GPU 变体分开（Dockerfile/Dockerfile.gpu，README.md:140-147 连 ARM 上 GPU 构建失败的原因都写明）。
- 坦白文化：README.md:99-100 连"首次运行慢且需联网下模型，别误以为容器挂了"这类运维噪音都写进文档。

（附注：本章所有 issue 号与 RFC 编号均摘自源码注释原文，可 grep 复核；如 `git grep "#1815"`。）
