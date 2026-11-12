# DataMind ONBOARDING.md

> 基于知识图谱（868 节点/1818 边/16 层/15 步 tour，commit 36e189d，2026-11-03）撰写，行号锚均经源码核实。

## 1. 一句话定位

DataMind 是 OpenDCAI 的"数据心智"系统：以 LanceDB 为默认知识库（Chroma 备选）、HybridRetriever 混合检索（BM25+向量+RRF）、CodexHost 单主 agent 宿主为核心，向 Codex 暴露 KB/SQL/Graph/Skills/Memory 五大能力面的共享工作区数据层。仓内双栈并存：`datamind/` 是 v1.0 生产新栈，仓根 `config.py`+`modules/` 是 LlamaIndex 时代 legacy 原型；仓根 main.py/server.py 已是转发新栈的兼容启动器（main.py:1 自述 Compatibility launcher）。README 钉死分工："Codex reasons, ingests and retrieves; DataMind stores data, executes tools, and returns evidence and write receipts"。

## 2. 心智模型

五环节流水线依次咬合：

1. **KB 存储**：`kb/providers/lancedb_store.py:21` 主后端（表快照+add_version:279 版本化），chroma_store 备选，config.py:260 `vector_store: Literal["chroma","lancedb"]` 切换。
2. **Embedding**：openai_compatible 用裸 httpx 兼容任意同形状端点（OpenAI/智谱/SiliconFlow），huggingface 本地模型为可选 extra。
3. **检索**：`providers/hybrid_retriever.py:46` BM25+向量双路，L193 RRF（weight/(rrf_k+rank+1)）融合；词法视图可按历史版本重建。
4. **能力包**：kb/db/graph/skills/memory/ingest 六包各自 tools.py 产出带元数据的 ToolSpec（group/surface/access/destructive），汇入 ToolRegistry。
5. **宿主**：`host.py:33` CodexHost 只做适配与回执收集，不规划不生成 SQL——智能全在外部主 agent。

`runtime.py:49` assemble_data_plane 是装配唯一入口。旧栈是另一套心智（LlamaIndex bootstrap+FunctionAgent 四引擎），与新栈互不调用，仅 schema/types.py:25 RAGChunk 契约跨栈。

## 3. 代码地图（按 16 层）

- **L01 工程与 CI**：pyproject.toml 单包+双 .env 样例+CI 双流水线。
- **L02 内核**：config.py（DATAMIND__ 前缀 14 子配置，Settings 真身 L288、L341 DataSettings 裸别名）、core/logging.py 每行一 JSON、core/errors.py 错误族。
- **L03 协议中枢**：core/protocols.py 21 个 DTO+Protocol 全部抽象（GraphEvidence 在 L116）；core/hooks.py 四决策 deny-wins；contracts/registry。
- **L04 KB 存储**：lancedb/chroma 双后端、indexer.py（_hash:48 内容寻址、build_index:173、corpus_fingerprint:241 指纹）、filters.py。
- **L05 向量与检索**：embedding factory；hybrid_retriever、multi_query LLM 改写。
- **L06 Ingest/Graph**：ingest/service.py 2011 行全仓最大（kb_add_text:628/kb_add_file:702）；ledger.py 幂等回执；formats.py 11 格式（extract_document:222）；graph networkx 单 JSON 持久化。
- **L07 DB**：nl2sql 单条只读 SELECT；safeguard 三防线；sqlite/mysql/dolt 三方言（dolt 自起 sql-server 版本管理）。
- **L08 Skills/Memory/Hooks**：skills SKILL.md 语义索引+代码技能；memory 短期窗+scope-typed 长期；钩子三件套（destructive_sql sqlglot AST/path_allowlist/audit Merkle 链）。
- **L09 Workspace**：workspace.py CAS+epoch 防 ABA；workspace_native 绑定 LanceDB 版本与 Dolt 提交；workspace_incremental.py 803 行多 surface 增量。
- **L10 宿主**：host.py、codex.py SDK 包装、agent/loop_native（仅基线实验，产品不组装）。
- **L11 三入口**：cli.py（chat:99）、mcp.py STDIO、server.py FastAPI 17 路由。
- **L12 Legacy**：modules/ 六子包（rag/indexer.py 393 行多模态三模式）。
- **L13 Plugins**：plugins/datamind-context Codex 插件（零 agent 逻辑）。
- **L14 评测**：benchmark/ vendored open-rag-eval（provenance+故障注入+LLM 判官）。
- **L15 Demo**：demo-uploads 六件语料+data/ 样本。
- **L16 文档**：docs/ 12 篇+adr/。

## 4. 核心链路走读：一次知识摄取与查询的旅程

**摄取**：demo-uploads/03-customers-2026.csv 经 CLI/MCP 调 ingest 工具 → ingest/service.py:702 kb_add_file → formats.py:222/268 统一抽取 → kb/indexer.py:48 内容寻址 chunk id、build_index:173 分块 → embedding 向量化 → lancedb_store.py:154 add（版本化走 add_version:279）→ ledger 回执落账。整库同步走 cocoindex 后端 kb_update_workspace（service.py:1106，ingest_mode 必须 cocoindex）。

**查询**：Codex 发 kb_search（kb/tools.py:78）→ hybrid_retriever.py:46 双路检索 RRF 融合 → 带证据返回；历史版本走 kb_search_at_version:143。DB 面 Codex 生成 SQL → safeguard 三防线 → 方言 provider 只读执行 → host.py:33 汇总回执交还 agent。宿主全程不插手规划。

## 5. 运行与调试

- **安装**（GETTING_STARTED.md 为准，venv+pip 而非 uv）：`python -m venv .venv && pip install -e '.[codex]'`；本地 Codex 插件 `./scripts/install_codex_plugin.sh --force --skip-deps`。
- **两套 env**：新栈 `.env.datamind`（DATAMIND__ 前缀双层 __ 分隔）；旧栈 `.env`（LLM_API_BASE 等裸变量，仅 legacy 用）。KB 需独立 embedding——本地可 `pip install -e '.[huggingface]'`+DATAMIND__EMBEDDING__PROVIDER=huggingface。
- **hello_codex 冒烟族**（datamind/scripts/ 12 个）：hello_kb/db/graph/skills/memory/hooks/agent/agent_sdk/sdk/sdk_native/codex/enterprise 逐能力面最小验证；seed_enterprise_demo 造演示数据，verify_sqlite_demo 验只读防线。
- **CLI**：`python -m datamind info / ask "..." --show-tools / chat`（cli.py:99）。
- **CI 六 job**（python-ci.yml）：test（3.11/3.12 矩阵）/versioning/databases/package/codex/gate，另有 python-publish 发版。

## 6. 已知坑（源码逐条钉版）

1. **worksapce 断链 bug（真 bug）**：ingest/tools.py:89-90 的 `_kb_update_worksapce` 调 `svc.kb_update_worksapce()`——方法名拼错，服务侧真身是 ingest/service.py:1106 的 `kb_update_workspace`；tools.py:679 把坏 handler 注册进工具，agent 一调即 AttributeError。
2. **assemble_data_plane 绕过工厂**：runtime.py:73-74 直接 `SkillsService(embedding=None, vector_store=None)` 裸构造，绕过 skills/service.py:219 build_skills_service 工厂（才会建 chroma_skills 语义索引）——宿主装配的 skills 只剩精确名匹配。
3. **GraphEvidence 不在 graph/evidence.py**：类在 core/protocols.py:116；graph/evidence.py（L7/13）只是证据文件持久化函数。"文件名=类型名"直觉在此失效。
4. **destructive:True 非唯一，源码实为 5 处**（explain 12 篇写 4 处，以源码为准）：kb/tools.py:133（kb_reindex）、kb/tools.py:196（kb_rollback，仅 lancedb 注册）、graph/tools.py:177、db/tools.py:262、memory/tools.py:180；core/hooks.py:84-88 的 confirm_destructive 参数流是独立语义（DestructiveSqlHook 看 SQL AST 非标记），权限审计两套一起算。
5. **start_ccr.sh:36 硬编码 macOS 路径**：DEFAULT_ENTRY 指向作者私人 /Users/lianghao/... vendored claude-code-router；非 macOS 必须用 L37 CCR_SERVER_ENTRY 覆盖，缺文件 fatal exit 2。
6. **demo 语料虚构 Chroma 防混淆**：seed_enterprise_demo.py 语料里 "Chroma" 是虚构公司的向量检索业务系统（L159/238/519/619/806/848），与 DataMind 自身 Chroma 向量库（config.py:260）毫无关系。

## 7. 上游与生态

- **vendored open-rag-eval**：benchmark/ 整目录内嵌（run.py/robustness.py/metrics/models），评测链不依赖外部拉取。
- **LlamaIndex legacy**：modules/ 六子包依赖 requirements-legacy.txt 钉住的旧版 llama_index，与新版互不升级。
- **存储方言**：KB 双后端 LanceDB/Chroma；DB 三方言 sqlite/mysql/dolt——dolt 提交级版本管理与 workspace_native 深度绑定。
- **Codex 生态**：官方 Codex SDK（codex.py）+ plugins/datamind-context 原生插件 + start_ccr.sh 的 claude-code-router 通道（作者环境专用）。
- **OpenDCAI org 关系**：DataMind 是 org 内"agent 数据层"定位仓，与 DataFlow（数据清洗）构成"清洗→入库→检索"互补线；README 双语+GitHub Pages 文档站。

## 8. 学习路径

图谱 15 步 tour 与 explain 12 篇这样配：**第一天**走 t01-t04（双栈心智→工程配置→内核→协议中枢）配 explain/01-dual-stack、03-embedding-providers；**第二天**走 t05-t07（KB 存储→检索→摄取图谱）配 02-kb-lancedb、07-legacy-archaeology；**第三天**走 t08-t10（DB→hooks/skills/memory→workspace）配 08-data-plane；**第四天**走 t11-t12（宿主→三入口）配 05-agent-host、06-entries-mcp；**收官**t13-t15（legacy 考古→插件→评测）配 04-capabilities、09-mcp-plugin、10-testing、11-scripts-tools，最后用 12-known-bugs 对照源码复核本文件第 6 节。动手验证：GETTING_STARTED 的 info→ask→store→chat 四连，再跑 hello_kb 与 seed_enterprise_demo 看完整数据面。

