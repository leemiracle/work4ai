# A-06 `vectorize-io/hindsight`（19.9K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\vectorize-io__hindsight
> Python 后端 + Rust CLI + Next.js 控制面 / ~4000 文件 / MIT ｜ "让 Agent 学习而不只是记住"的记忆系统：PostgreSQL 上的 retain→consolidation→reflect 三段式管线，事实→观察→心智模型三层记忆

## 1. 架构总览（目录地图，标出核心目录的职责）
- `hindsight-api-slim/hindsight_api/` — 核心 API 与引擎。`engine/retain/`（写入：防御→事实抽取→链接）、`engine/consolidation/`（观察合成/纠错）、`engine/reflect/`（Agentic 反思 + 心智模型增量刷新）、`engine/search/`（四路混合检索+重排）、`engine/providers/`（20+ LLM 适配）、`engine/db/`（PostgreSQL/Oracle 双后端）、`extensions/`（memory_defense 等）
- `hindsight-all/` — 嵌入式单包（`hindsight/embedded.py` 两行代码接入 LLM wrapper）；`hindsight-all-npm/` — TS 客户端
- `hindsight-cli/`（Rust）、`hindsight-control-plane/`（Next.js 管理 UI）、`hindsight-embed/`（Python 客户端）、`hindsight-dev/benchmarks/`（LongMemEval/LoCoMo/OBS 评测套件）
- 存储为 PostgreSQL（向量 pgvector/vchord + 全文 tsvector/VectorChord-bm25/ParadeDB 三选一，见 `hindsight-api-slim/hindsight_api/alembic/versions/5a366d414dce_initial_schema.py:307-331`），租户单位是 memory bank（bank_id）

## 2. 记忆机制深读（本笔记核心）

### 2.1 写入/抽取管线（retain）
- 入口先过 **Memory Defense**：策略化敏感数据扫描，决定 allow/redact/block，命中触发 webhook 且原始值只以指纹形式出网（`hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py:18-24,32-46,97-150`）
- 事实抽取 `fact_extraction.py`：LLm 结构化 JSON 输出"语义事实+实体+时间信息"，实体支持 map 型标签 schema 递归展开（`engine/retain/fact_extraction.py:1-45,29-45`）；超长文档切子批、body 复用同一次筛查避免重复扫描（issue #3282，`orchestrator.py:54-77`）
- 文档级增量：`documents.original_text` 存原文，若新 body 是已存文本的**严格前缀追加**则跳过重抽（`orchestrator.py:80-94`）
- 链接创建：为事实批量建 temporal（时间邻近）/semantic/causal 三类 `memory_links`（`engine/retain/link_creation.py:1-25`）；causal 关系收敛为单一规范类型 `caused_by`，旧类型仅保留在导入/导出路径（`engine/causal_links.py:9-14`）

### 2.2 存储后端与数据模型（原文摘录 schema）
- 核心表 `memory_units`（`alembic/versions/5a366d414dce_initial_schema.py:265-305`）：
```sql
sa.Column("text", sa.Text(), nullable=False),
sa.Column("embedding", Vector(384), nullable=True),
sa.Column("context", sa.Text(), nullable=True),
sa.Column("event_date", ..., nullable=False),
sa.Column("occurred_start"/"occurred_end"/"mentioned_at", ...),
sa.Column("fact_type", sa.Text(), server_default="world"),
sa.Column("confidence_score", sa.Float(), nullable=True),
sa.Column("access_count", sa.Integer(), server_default="0"),
-- CHECK: fact_type IN ('world','bank','opinion','observation')
-- CHECK: opinion 必须带 confidence；observation 由引擎生成
```
- `fact_type` 四分类是分层记忆的物理载体：world（世界事实）/bank（bank 级事实）/opinion（带置信度观点）/**observation（引擎合成的观察，带 proof_count + source_memory_ids + history JSONB**，`engine/consolidation/consolidator.py:8-12`）
- 辅助表：documents（original_text+content_hash）、entities（canonical_name+mention_count+first/last_seen）、memory_links、mental_models、audit_log、observation_history（版本表迁移 `a7b8c9d0e1f2_split_history_into_own_tables.py`）

### 2.3 检索策略（四路混合+双阶段激励）
- 四臂检索 semantic/bm25/graph/temporal，逐臂截 cap 后 **RRF 融合 k=60**（`engine/search/fusion.py:29,56,85`）——臂名硬编码于 fusion 源码
- 融合后过 cross-encoder 重排（本地 ms-marco CE）+ recency/temporal 打分，候选池 300 上限（`engine/search/recall_boost.py:45-54`）
- **可配置臂激励**：`HINDSIGHT_API_RECALL_STRATEGY_BOOSTS` 用 low/medium/high 人话级别在两个尺度上加权——重排前乘 RRF 贡献（low=1.0/medium=3.0/high=6.0），重排后加平坦权重（0.05/0.2/0.5），数值是对 LoCoMo 真实召回轨迹调参的（`recall_boost.py:62-72`）

### 2.4 遗忘·整合·演化（学习闭环 = 本仓灵魂）
- **consolidation（纠错/强化引擎）**：retain 完成后的后台作业，对新记忆做出 CREATE 新观察 / UPDATE 既有观察 / DELETE 三类决策，"新证据支持/矛盾/细化旧观察时更新之"（`engine/consolidation/consolidator.py:1-16`）。prompt 规则八条（`engine/consolidation/prompts.py:36-50`）：①宁 UPDATE 勿 CREATE ②按实体/facet 匹配而非话题 ③状态变化简洁更新 ④级联修改所有受影响观察 ⑤新事实解析旧占位符（"home city"→具体城市）⑥重大历史事件永不 DELETE ⑦禁止自行计算数值 ⑧每条决策必须给 reason（输出契约 `:108`）
- 防漂移护栏：精确文本对账守卫——LLM 既 UPDATE 又 CREATE 同文本时丢弃 CREATE（case-sensitive 空白归一匹配，`:121-150`）；语义判重用观察自身 embedding 取 top-5 候选（`:153-160`）；任务失败时取消兄弟任务、孤儿写入不可见、由恢复清扫兜底（`:64-99`）
- **reflect + 心智模型（增量学习）**：mental_models 表存用户定义的固定查询（pinned 文档），刷新分 full/delta 两模式——delta 只看 `created_after = last_refreshed_at` 水位之后的新记忆，DB 快照上界保证不漏（`engine/mental_model_refresh.py:65-87`）
- **delta_ops（结构性防漂移的精髓）**：LLM 不重写文档，只输出结构化操作（append_block/insert_block/replace_block/remove_block/add_section/remove_section/replace_section_blocks，`engine/reflect/delta_ops.py:55-120`）；未提及的 section 物理拷贝、"散文漂移在结构上不可能"；非法操作整批丢弃、失败=零变更——"文档只会变好或不变，不会变坏"（`:1-24`）
- reflect agent 是带原生工具调用的 Agentic 循环（≤10 轮，`engine/reflect/agent.py:55`），分层检索：先 search_mental_models（用户策展）→ search_observations（带新鲜度的整合知识）→ recall（原始事实为 ground truth）（`agent.py:1-8`）
- 弱化信号：`access_count` 列+索引记录被检索命中（`initial_schema.py:279,337`）；被矛盾证据推翻的观察走 DELETE（`consolidator.py:2569` "Delete a superseded or contradicted observation"）且历史进 observation_history 表

### 2.5 注入上下文的方式
- 主打 **LLM Wrapper 两行接入**：包一层客户端，memorize/recall 自动随调用发生（`README.md:37-41`；`hindsight-all/hindsight/embedded.py`）
- reflect 输出可直接带 JSON Schema 结构化结果（`reflect/agent.py:109-150`）；工具调用失败的传输（如 litellm Vertex 剥掉 tools 定义）显式 fail loudly 而非把工具 JSON 当答案（`agent.py:63-74`）

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

① 学习闭环定义（`engine/consolidation/consolidator.py:1-16`）：
```python
"""The consolidation engine runs as a background job after retain operations complete.
It processes new memories and either:
- Creates new observations from novel facts
- Updates existing observations when new evidence supports/contradicts/refines them

Observations are stored in memory_units with fact_type='observation' and include:
- proof_count: Number of supporting memories
- source_memory_ids: Array of memory UUIDs that contribute to this observation
- history: JSONB tracking changes over time
"""
```

② delta 操作防漂移宣言（`engine/reflect/delta_ops.py:9-24`）：
```python
Sections and blocks not mentioned by any op are physically copied through
unchanged — there is no LLM-mediated re-emission of unchanged text, so prose
drift is structurally impossible.
...
Failure modes are by design conservative: an operation list that fails to
parse against the Pydantic schema, or an LLM that returns invalid ops, results
in zero changes — the document stays as-is. The structure can only get better
or stay the same per refresh, never get worse.
```

③ 双尺度策略激励（`engine/search/recall_boost.py:68-72`）：
```python
BOOST_LEVELS: dict[str, BoostWeights] = {
    "low": BoostWeights(rrf=1.0, additive=0.05),
    "medium": BoostWeights(rrf=3.0, additive=0.2),
    "high": BoostWeights(rrf=6.0, additive=0.5),
}
```

④ 观察对账守卫（`engine/consolidation/consolidator.py:132-150`）：
```python
def _duplicate_create_target(create_text, shown_obs_by_text, update_texts):
    norm = _norm_obs_text(create_text)
    matched = shown_obs_by_text.get(norm)
    if matched is not None:
        return f"shown observation {str(matched.id)[:8]}"
    if norm in update_texts:
        return "an UPDATE in this response"
    return None
```

⑤ RRF 四臂融合（`engine/search/fusion.py:56,85`）：
```python
source_names = ["semantic", "bm25", "graph", "temporal"]
...
rrf_scores[doc_id] += 1.0 / (k + rank)
```

## 4. 基准/评测声明（反虚荣视角）
- README 声称："most accurate agent memory system ever tested"、LongMemEval SOTA，且"benchmark performance data … **independently reproduced** by research collaborators at the Virginia Tech Sanghani Center … and The Washington Post. Other scores are self-reported by software vendors"（`README.md:28-34`）→ 口径判定：**[第三方复现（口头声称）+ 自跑 harness 在库]**。附 arXiv 论文 2512.12818；但对比数字放在 PNG 图片（`hindsight-benchmarks.png`）里，仓库文本中无对照表，第三方复现报告未随库提供链接，可复现性依赖自跑
- 自跑基础设施扎实：`hindsight-dev/benchmarks/` 含 LongMemEval/LoCoMo/OBS（含入库数据集 locomo10.json、herb_garden.txt）与 perf 套件，脚本可重放（`benchmarks/README.md:17-79`）
- 诚实的性能自曝：consolidation 吞吐 ~0.7-1.0 op/sec，**LLM 占 80-87% 时间是主瓶颈**（`benchmarks/consolidation/README.md:39-43`）——学习闭环的代价被明码标出

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
- **"操作而非重写"的更新范式**：LLM 只发结构化编辑指令，未提及内容物理透传——把"LLM 改记忆引入漂移"从概率问题变成结构不可能问题（`delta_ops.py:9-19`），这是对 mem0 全量重写式 UPDATE 的直接升级
- **证据计数型记忆**：observation 带 proof_count/source_memory_ids/history，"观察"是可被后续证据支持/矛盾/细化的一等公民，矛盾即删且历史留档（`consolidator.py:8-12,2569`）
- **水位式增量刷新**：delta refresh 用 DB 快照上界+last_refreshed_at 水位保证不重不漏（`mental_model_refresh.py:65-87`），比定时全量省 token
- **双尺度检索臂激励**：用 low/medium/high 语义级别分别在 RRF 尺度与重排尺度加权，且调参依据（300-cap 边界 RRF≈0.0055、CE 双峰分布）写进注释（`recall_boost.py:45-67`）
- **fail-loudly 的工具调用传输校验**：检测 provider 假装支持 function calling（`agent.py:63-74`）
- 取消式并发卫生：gather 失败先 cancel 再上抛，孤儿写入靠 witness 行提交语义自然回滚（`consolidator.py:64-99`）

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 学习闭环全程强 LLM 依赖：consolidation 0.7-1.0 op/sec 意味着高写入率 Agent 的观察合成显著滞后于事实入库；LLM 决策错误只能靠对账守卫挡"同文本重复"这类低级错，语义级误 UPDATE 无护栏
- 复杂度重：30+ alembic 迁移、PostgreSQL/Oracle 双后端、三种全文后端（native/VectorChord/ParadeDB）、vchord/pgvector 两套向量——部署矩阵大，`ops_oracle.py` 与 `ops_postgresql.py` 并行维护是长期税
- 四臂检索臂名硬编码在 fusion（`fusion.py:56`），加新臂要改核心；boost 调参绑死 LoCoMo 轨迹（336 候选→300-cap），换 reranker 或预算需重调
- 基准主证据是图片+口头第三方复现；"most accurate ever tested" 属营销级全称断言，仓库内无法独立验证
- reflect 每轮最多 10 次迭代×分层检索×LLM 调用，思考型查询成本高；无 token 预算式的注入上限声明（与 agentmemory 的显式 budget 相比）

## 7. 一句话对比 mem0
mem0 用"LLM 抽取+覆盖更新"管理记忆，hindsight 把记忆做成带证据链的演化系统：事实入库后由 consolidation 以"操作+对账"方式持续纠错强化，用 delta_ops 结构性杜绝重写漂移，用水位增量刷新心智模型——学习能力强得多，但也为此背上了全链路 LLM 依赖、亚秒级吞吐和庞大部署矩阵。
