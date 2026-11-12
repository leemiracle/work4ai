# A-26 `agentscope-ai/ReMe`（3.3K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\agentscope-ai__ReMe
> Python ｜ 阿里 AgentScope 团队 ｜ "Memory as File" 文件原生长期记忆管理工具包：对话/文件 → Markdown 知识库（YAML frontmatter + wikilink 图），通过 CLI/HTTP/MCP 服务暴露

## 1. 架构总览（目录地图）

- `reme/application.py` — `Application` 中枢：建 workspace 目录、按 YAML 实例化 service/components/jobs（`reme/application.py:21-97`），依赖拓扑排序启动（deepwiki 称 Kahn 算法 [deepwiki-已验证至 `_instantiate`/registry 机制，`reme/application.py:99-130`]）
- `reme/components/` — 基础设施后端：`file_store/`（local/faiss/zvec 三实现 + BM25 + file_graph）、`agent_wrapper/`（agentscope/codex/claude-code 三种 LLM 代理）、`keyword_index/bm25_index.py`、`file_graph/`（local/networkx/neo4j）、`service/`（http/mcp/cli）
- `reme/steps/` — 原子算子：`file_io/`（read/write/edit/frontmatter/daily_*）、`index/`（search/search_v2/vector_search/bm25_search/traverse/watch_changes）、`evolve/`（auto_memory/auto_resource/dream/）、`benchmark/`（lme/beam）
- `reme/schema/` — Pydantic 数据模型：`file_node.py`、`file_chunk.py`、`file_link.py`、`dream.py`
- `reme/config/default.yaml` — 声明式 Job 编排（watch loop / cron / base job 三种）
- `benchmark/` — longmemeval、beam、pibench、toolmemory 四套自研评测 harness
- 核心抽象链：**Component（可插后端，注册表 `R`）→ Job（Base/Stream/Background/Cron）→ Step（原子 LLM 工作流单元）**。算子化设计：每个 Step 用 `@R.register("xxx_step")` 注册（如 `reme/steps/evolve/auto_memory.py:60`），由 YAML 里的 `backend: xxx_step` 字符串引用组装。

## 2. 记忆机制深读

### 2.1 写入/抽取管线
- **auto_memory（Remember 算子）**：输入 `messages + session_id`，先把原始对话经 `_sanitize_msg_for_save` 清洗——**剔除 tool_result 与 base64 块**，防"检索到的事实伪装成用户原话"（`reme/steps/evolve/auto_memory.py:21-37` 注释明言此动机）；按 msg.id 去重合并、按 created_at 排序后追加写 `session/dialog/<session_id>.jsonl`（`auto_memory.py:179-214`）。随后用 LLM agent 判定是否值得记（prompt 明示"模棱两可时默认写入——丢记忆比多写更糟"，`reme/steps/evolve/auto_memory.yaml:65`），新笔记走 `daily_write` 工具一次成文，已有笔记限定单路径合并（`auto_memory.py:333` 注入 `_allowed_paths` 限制 agent 只能改本笔记）。
- **prompt 结构**（`auto_memory.yaml:1-23` system prompt）：像人一样记五类事实——用户持久事实/决策叙事/当前状态/可复用流程/其他；frontmatter 规则强制 `name`=kebab-case 主题 stem、`description`=详尽摘要、**永不设 `status`**（保留给下游 dream 处理，`auto_memory.yaml:23`）。合并规则按内容类型分治：时间线只追加、当下状态整段重写、其余合并去重（`auto_memory.yaml:150-153`）。
- **auto_resource**：watchfiles 监听 `resource/` 目录（default.yaml:20-36 `resource_watch_loop` 后台 job），LLM 解读 PDF/CSV/HTML 为 resource card，frontmatter 写 `source_resource` wikilink 回链原文。
- **auto_dream（Refine 算子）**：cron `0 23 * * *` 每晚触发（`reme/config/default.yaml:56-70`），四步流水线 `dream_extract → dream_integrate → dream_topics → dream_finish`。extract 扫近 `scan_days=2` 天 daily 文件，按 mtime 对比 catalog 找 changed 集合（`reme/steps/evolve/dream/extract.py:69-75`），LLM 全局抽取"记忆单元"（name/bucket/summary/paths）与兴趣主题，失败自动重试一次、再失败仅告警不阻塞（`extract.py:113-158`）。

### 2.2 存储后端与数据模型
- **存储即文件系统**：workspace 四层结构 `session/`（原始对话 jsonl）、`resource/`（外部原料）、`daily/`（工作记忆：`daily/YYYY-MM-DD/<name>.md` + 日索引 `daily/YYYY-MM-DD.md` + `interests.yaml`）、`digest/`（长期记忆，按 bucket 分 `personal/procedure/wiki` 三目录，`reme/enumeration/dream_bucket_enum.py:6-11`）、`metadata/`（索引/目录/图，zstd 压缩 jsonl）。
- 节点模型：`FileNode{path, st_mtime, links[], chunk_ids[], front_matter}`（`reme/schema/file_node.py:9-16`）——**文件即图节点**，wikilink `[[...]]` 即边；chunk（`FileChunk`）带 `scores: dict` 支持多路分数并存。
- `LocalFileStore` 聚合 embedding_store（faiss 可选）+ BM25 keyword_index + file_graph 三件套，`FaissLocalFileStore`/`ZvecLocalFileStore` 为替代后端（`reme/components/file_store/`）。graph 后端三选：local-json / networkx / neo4j（`reme/components/file_graph/`）。

### 2.3 检索策略
- **混合检索 + RRF**：`search_v2_step` 并行跑 vector_search 与 keyword_search 各取 `limit×candidate_multiplier(5.0)`、上限 `_MAX_CANDIDATES=200` 候选（`reme/steps/index/search_v2.py:24-27,134`），RRF 融合公式 `w/(K+rank)`，`K=60`、vector_weight 默认 0.7（`search_v2.py:54-85,115`）；单路命中时退化为单路结果不融合（`search_v2.py:184-192`）。
- **图扩展**：对 top 结果按 wikilink out/in 双向扩展邻居（每向上限 10），带 anchor 分组（`reme/utils/link_expansion.py:58-80`），作为答案附注而非参与排序。
- **会话块区间合并 + 去重**：`_ToolContextDedupMixin` 按 tool_context_id 记忆已见 chunk（TTL 24h），同 session 相邻 chunk 合并区间（`search_v2.py:199-209`）。
- **可选 LLM 压缩**：session 原始转写命中时可调 `compressor` job 做 query-aware 压缩，压缩更长则弃用，缺失 job 优雅降级（`search_v2.py:249-330`）。
- 日期过滤规范化进 `search_filter`，非法日期剔除并告警（`search_v2.py:147-169`）。

### 2.4 遗忘·整合·演化
- 无 decay/TTL 删除——演化靠**分层压缩**：daily（当天）→ dream 萃取 → digest 三桶（procedure/personal/wiki）；integrate 步对每个 unit 调 LLM（工具含 node_search/read/edit），写前/写后快照 digest 目录以恢复副作用，app 级 asyncio.Lock 串行化（`reme/steps/evolve/dream/integrate.py:17-37,79-90`）。
- **兴趣演化**：`dream_topics_step` 每日产出 `daily/<date>/interests.yaml`，`topic_diversity_days=7` 避免近 7 天主题重复（`reme/config/default.yaml:115-117`）；`proactive_step` 读取 interests.yaml 供主动提醒（`reme/steps/evolve/dream/proactive.py:9-43`）。
- 文件删除会同步清理 catalog（extract 步的 deleted 集合，`extract.py:75-83`）；`optimize_index_cron` 每晚 02:00 优化索引（default.yaml:72-76）。

### 2.5 注入上下文的方式
- 检索结果渲染为带行号的 chunk 块 `========== path:start-end [score=... keyword=...] ==========`（`docs/en/reme_scene.md:186` 实例），经 MCP 工具/HTTP `/action` 返回给宿主 agent（Claude Code/QwenPaw 插件在 `plugins/`），由宿主自行拼 prompt——ReMe 本身不做 token 预算裁剪，仅 `DEFAULT_MAX_FILE_BYTES` 限制单文件读量（`reme/constants.py`，`reme/steps/base_step.py:18`）。

## 3. 关键代码摘录

**摘录 1：防记忆污染的对话清洗（`reme/steps/evolve/auto_memory.py:24-31`）**
```python
def _sanitize_msg_for_save(msg: Msg) -> Msg:
    new_content = []
    changed = False
    for block in msg.content:
        # Tool results often contain recalled memory/search/read output. Keeping
        # them in saved conversation history lets retrieved facts masquerade as
        # user-provided context in future auto-memory runs.
        if block.type == "tool_result":
            changed = True
            continue
```

**摘录 2：RRF 融合核心（`reme/steps/index/search_v2.py:53-67`）**
```python
@staticmethod
def _rrf_merge(vector, keyword, vector_weight):
    """Fuse two ranked lists with Reciprocal Rank Fusion, keyed by chunk.id."""
    text_weight = 1.0 - vector_weight
    merged: dict[str, FileChunk] = {}
    for rank, chunk in enumerate(vector, start=1):
        contrib = vector_weight / (_RRF_K + rank)
        c = chunk.model_copy(deep=False)
        c.scores = {**chunk.scores, "vector": chunk.scores.get("vector", chunk.score), "score": contrib}
        merged[c.id] = c
```

**摘录 3：dream 变更检测（`reme/steps/evolve/dream/extract.py:69-75`）**
```python
nodes = await self.file_catalog.get_nodes()
indexed_all = {n.path: n.st_mtime for n in nodes if n.path in day_mds or n.path.startswith(day_prefixes)}
indexed = {path: mt for path, mt in indexed_all.items() if path not in interest_rels}
changed = [rel for rel, mt in existing.items() if indexed.get(rel) != mt]
```

**摘录 4：cron 化的记忆固化编排（`reme/config/default.yaml:56-70`）**
```yaml
dream_cron:
  backend: cron
  cron: "0 23 * * *"
  steps:
    - backend: dream_extract_step
      file_catalog: dream
      topic_session_id: interests
      scan_days: 2
      max_units: 5
    - backend: dream_integrate_step
    - backend: dream_topics_step
      topic_count: 3
      topic_diversity_days: 7
    - backend: dream_finish_step
```

**摘录 5：文件即图节点（`reme/schema/file_node.py:9-16`）**
```python
class FileNode(BaseModel):
    """A workspace file as a graph node."""
    path: str = Field(default=..., description="Path relative to the workspace")
    st_mtime: float = Field(default=..., description="Filesystem mtime (seconds)")
    links: list[FileLink] = Field(default_factory=list, description="Outgoing wikilinks")
    chunk_ids: list[str] = Field(default_factory=list, description="Owned FileChunk ids")
    front_matter: FileFrontMatter = Field(default_factory=..., ...)
```

## 4. 基准/评测声明（反虚荣视角）
- README 自报：LongMemEval cleaned-s **89.4%**（500 题）、BEAM 100K **66.1%**（400 题）、BEAM 1M **65.0%**（700 题）、PI-Bench "2.4% above NanoBot"（`README.md:305-310`）——全部 **[自封]**，但 harness 全部开源可跑（`benchmark/longmemeval/run.py`、`benchmark/beam/run.py`，含 LLM-as-judge 配置与 rubric），非空口号；数字口径（模型/成本/token）README 表格未完整披露 **[部分可复现]**。
- 注意 LongMemEval 用的是 "cleaned-s" 自清洗子集而非官方全集口径 **[口径自定义]**

## 5. 可借鉴模式（增量，区别于 mem0）
1. **记忆=文件** 的 ground truth 哲学：一切中间态（session/daily/digest）都是人可读 Markdown + frontmatter，可 git 版本化、可手工纠错——mem0 的黑盒 vector store 做不到（`reme/schema/file_node.py:9-16`）
2. **算子化**：记忆操作被拆成可 YAML 编排的 Step 算子（@R.register 注册表），cron/watch/background 三种 Job 复用同一批算子——比 mem0 的 `add/search/get_all` 三 API 表达力高一档（`reme/config/default.yaml:56-119`）
3. **tool_result 清洗防自污染**：保存对话前剔除工具返回块，阻断"检索结果→被当成用户事实→再抽取"的回环污染（`reme/steps/evolve/auto_memory.py:24-31`）——通用性洞见，任何会检索的 agent 记忆系统都适用
4. **三桶 digest + 兴趣主题演化**：personal/procedure/wiki 语义分桶 + interests.yaml 主题多样性约束（7 天不重复），给"遗忘"提供了不删数据的替代方案——蒸馏分层而非衰减（`reme/enumeration/dream_bucket_enum.py:6-11`、`default.yaml:115-117`）
5. **RRF 混合检索默认权重 0.7 向量** + wikilink 邻居扩展作为附注不参与排序——图扩展的克制用法（`search_v2.py:54-85`、`link_expansion.py:58-80`）

## 6. 局限与风险
- 无删除/衰减机制，daily 层无限累积（仅靠 dream 蒸馏，原文保留）；长周期后 session/jsonl 与 daily 双份存储膨胀
- auto_memory 每会话一笔记、agent 单次成文的质量完全依赖 LLM；`edit` 失败退化为全量 `write` 重写，有丢历史风险（`auto_memory.yaml:160`）
- dream 每晚一次、scan_days=2 窗口固定，跨 >2 天才浮现的价值会漏（`default.yaml:63`）
- 检索无 rerank、无 token 预算控制；compressor 分支是 benchmark 特化（`search_v2.py:267-269` 注释自认 benchmark config 忘配时的降级）
- LLM agent 写文件路径校验依赖 `validate_filename_component`，但 agent 拥有 write/edit 工具权限，越权风险靠 `_allowed_paths` 软约束（`auto_memory.py:333`）

## 7. 一句话对比 mem0
mem0 把记忆藏进向量库黑盒用三条 API 操作；ReMe 把记忆摊开成 Markdown 文件 + wikilink 图，用可编排的 Step 算子（Remember=auto_memory、Refine=dream 三步流水线）做分层蒸馏，换取可解释可编辑，代价是存储翻倍与无遗忘机制。
