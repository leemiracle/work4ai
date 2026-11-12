# 12 · 已知 bug 与坑专篇：拼写三连、定义处勘误、destructive 标记与同名异物

> 本篇收拢 explain 系列各篇散见的坑，全部给出源码行号锚，并标注"以源码为准"的口径修正——其中两处（worksapce 断链、db_rollback 非唯一 destructive）与仓库早期笔记的口径不同，本文按当前源码钉版。

## 一、角色定位

这一篇是防御性地图：新人改 ingest 工具、查 GraphEvidence、做 destructive 审计、读 demo 语料时最容易被名字骗的六个点。它们的共性是**名字与实体错位**——拼写错误形成的三点断链、定义处与直觉文件不符、标记字段的多处分布、语料虚构系统与真系统同名。每一处都给出判别命令级的锚。

## 二、worksapce 拼写三连：cocoindex 模式下的真断链

`datamind/capabilities/ingest/tools.py` 里三个位置把 workspace 拼成 worksapce：

- **L89** `async def _kb_update_worksapce() -> dict:` ——handler 函数定义
- **L90** `return await svc.kb_update_worksapce()` ——对服务侧的调用
- **L679** `handler=_kb_update_worksapce` ——工具注册处引用

而工具对外名是**正确拼写**：L672 `name="kb_update_workspace"`。关键分歧在服务侧：`capabilities/ingest/service.py` L1106 定义的是 `async def kb_update_workspace(`（拼对了）。**因此这不是"两边都拼错所以能跑通"的对称巧合，而是真断链**：该工具只在 `svc.ingest_mode == "cocoindex"` 时注册（tools.py L669），一旦注册并被调用，L90 的 `svc.kb_update_worksapce()` 立即 AttributeError，因为 IngestService 上只有正确拼写的那个方法。判别：`grep -rn "worksapce" datamind/` 恰好只命中这三行。另外 ledger.py L217 的豁免集合里登记的是正确拼写 `kb_update_workspace`——即使修好调用，豁免语义按工具名（正确拼写）走，不受影响。修复方向：L89-90 两行改成正确拼写，L679 引用同步改，一行 sed 的事，但目前（v2.1.0）仍在。

## 三、GraphEvidence 定义处勘误：在 core/protocols.py，不在 graph/evidence.py

按文件名直觉，`datamind/capabilities/graph/evidence.py` 应该是 GraphEvidence 的家——**不是**。该文件只有两个纯函数：`persist_input`（L7）与 `persist_bytes`（L13），做的是内容寻址落盘（sha256 摘要命名写到 `data_dir / 'triplets' / 'evidence'`，L16-17，冲突时字节级完整性校验 L21-23）——它是"图断言的不可变输入记录"的存储器。真正的 Pydantic 模型 `class GraphEvidence(BaseModel)` 定义在 **`datamind/core/protocols.py` L116**，被同文件 L139/L164 两个协议结构以 `evidence: list[GraphEvidence]` 引用，并被 workspace_incremental.py L17 `from datamind.core.protocols import GraphTriple, GraphEvidence` 消费。命名教训：capabilities 层的 evidence.py 是 IO 层，core 层的 protocols.py 才是类型层；跨包找类型定义先 grep `class X`，别信文件名。

## 四、destructive: True 标记：db_rollback 并非唯一

`db_rollback` 的注册在 `capabilities/db/tools.py` L239（name）与 **L262**（`metadata={... "destructive": True,}`），其 description（L242-252）明确语义：按 commit hash 把**数据**回滚到历史版本，历史本身保留（revert commit 叠加），但对当前工作数据是破坏性的。**但全仓 destructive: True 共四处**，不是只有它：

- `capabilities/graph/tools.py` **L177**（graph_upsert_triples 的 _upsert）
- `capabilities/kb/tools.py` **L133**（kb_reindex 的 _reindex，附 source_path 元数据）
- `capabilities/memory/tools.py` **L180**（memory_forget 的 _forget）
- `capabilities/db/tools.py` **L262**（db_rollback）

与之并行的还有另一套 destructive 语义：`core/hooks.py` L84-88 的 `confirm_destructive=True` 确认参数流（DestructiveSqlHook 看 SQL 而非标记）。做权限审计或 UI 红标时，四处 metadata + hook 的 SQL 判定要一起算，漏任何一处都会低估破坏面。

## 五、demo 语料虚构 Chroma：同名异物防混淆

`seed_enterprise_demo.py` 造的虚构公司语料里，"Chroma"是**虚构公司内部的向量检索业务系统**：L159 运维手册"索引写入失败：检查 Chroma 集群状态，联系 Bob"、L238 架构文档"Chroma Cluster：向量检索主存储，分片数 16"、L519-520 问答对"Chroma 跟 Elasticsearch 什么关系？…… RRF 融合"、L619 图三元组 `Search Platform Product —has_component→ Chroma Cluster`、L806 项目表行 `'Chroma Sharding Upgrade'`、L848 事故表 `'Chroma OOM under spike traffic'`。而 DataMind **自身**的 Chroma 是 KB 向量库实现之一（config.py L260 `vector_store: Literal["chroma","lancedb"]`），其磁盘痕迹是 L900 清理清单里的 `chroma`（KB 库）与 `chroma_skills`（skills 库）目录。问"Chroma 集群状态"这类问题时答案来自语料叙事，与系统自身用什么向量库毫无关系——排障与评测都要先分清这两个 Chroma。demo-uploads/02-project-kepler-tech-spec.md L40/L52 同样是语料层 Chroma。

## 六、DataSettings 别名与扫描盲区

`datamind/config.py` **L341 `DataSettings = Settings`** 是一句裸别名赋值——真身在 L288 `class Settings(BaseSettings)`（14 个嵌套配置组 L290-303，env 前缀 `DATAMIND__` + 双层分隔 `__` 见 L305-312）。消费者大多用别名：`datamind/mcp.py` L14/L62、`datamind/server.py` L19/L41、`datamind/scripts/hello_codex.py` L4。坑在**静态工具盲区**：`Name = Name` 形式的赋值不产生 class 定义节点，依赖树（含本仓 understand 图谱的 neighborMap）里 DataSettings 与 Settings 的等价关系、别名消费者的类型归属都会断链，需人工补（docs/LEGACY_RUNTIME.md 的示例代码也用 DataSettings，别误以为它是独立类）。查配置字段永远去 L288 的 Settings 及其各 Config 类。

## 七、其余收录坑（速查）

- **start_ccr.sh 绝对路径**（scripts/start_ccr.sh **L36**）：`DEFAULT_ENTRY="/Users/lianghao/Desktop/DataMind/KDD-CUP-DataAgent/vendor/claude-code-router/..."` 是作者个人 macOS 路径且指向兄弟仓的 vendored CCR；L37 可用 `CCR_SERVER_ENTRY` 覆盖，L39-43 缺文件时 fatal exit 2 带 hint。非 macOS 必须显式覆盖（详见 09 篇）。
- **benchmark vendored 不接线**：`benchmark/metrics/golden_answer_metrics.py` L15-17 三个 import 全走外部包名 `open_rag_eval.*`，隔壁 `benchmark/models/` 的拷贝不被消费；不装 open-rag-eval 此三文件 import 即炸（详见 07 篇）。
- **static/ 双份拷贝**：仓根 `static/` 与 `datamind/static/` 的 app.html/markdown.js diff 相同，服务端只用后者（server.py L94），改前者无效（07 篇）。
- **legacy 裸导入**：modules/* 的 `from config import settings`（agent.py:20 等）依赖仓根 cwd，装成包后必失败（07 篇）。

## 八、设计决策（含批判）

这批坑的成因分三类：**演进残留**（worksapce 断链是 cocoindex 分支少人走、CI databases/versioning job 只测 direct 路径的工具面）、**命名让位**（graph/evidence.py 被 IO 职能占用导致类型定义漂移到 core）、**语料与系统同域**（虚构公司恰好也做向量检索）。批判：拼写断链能存活说明**该路径无任何测试覆盖**——test_ingestion_skills.py 不触 cocoindex 模式的这个工具；最便宜的根治是给每个注册工具加一条"handler 可解析"冒烟断言。destructive 四处分布则提示 metadata 契约没有集中 schema，新增工具靠复制粘贴对齐。

## 九、新人提示

- 动 ingest 工具前先 `grep -rn "worksapce"` 确认三连是否已修；若你要启用 cocoindex 模式（config.py L259-268：还需 vector_store=lancedb），kb_update_workspace 是已知雷。
- 查类型定义用 `grep -rn "^class GraphEvidence"`；本仓"文件名=类型名"的直觉在 graph/、kb/ 两层都不成立。
- 写权限相关 UI/hook 时，destructive 四处（graph:177 / kb:133 / memory:180 / db:262）做成常量清单引用，别硬编码"只有 db_rollback"。
- 评测脚本读 enterprise_demo 语料时把"Chroma Cluster/集群"当普通实体处理，与系统配置项 `vector_store=chroma` 严格区分。
- 给静态分析/图谱工具写规则时，把 `DataSettings = Settings` 这类别名赋值列入人工补录清单（同款还有 modules 层的 settings 单例 re-export）。

行号锚：tools.py:89/90/672/679/669 · service.py:1106 · ledger.py:217 · core/protocols.py:116/139/164 · graph/evidence.py:7/13/16-17/21-23 · workspace_incremental.py:17 · db/tools.py:239/242-252/262 · graph/tools.py:177 · kb/tools.py:133 · memory/tools.py:180 · core/hooks.py:84-88 · seed_enterprise_demo.py:159/238/519-520/619/806/848/900 · config.py:260/288/305-312/341 · mcp.py:14/62 · server.py:19/41 · start_ccr.sh:36/37/39-43 · golden_answer_metrics.py:15-17 · datamind/server.py:94 · modules/agent/agent.py:20
