# 04 · capabilities 六能力包：ingest/graph/skills/db 勘误与暗坑

## 角色定位

`datamind/capabilities/` 八目录实为"六能力面+两横切"：kb/db/graph/skills/memory 五面可开关（`runtime.py:53` `defaults = {"kb","db","graph","skills","memory"}`），ingest 永远构建（`runtime.py:82-88`）；hooks/embedding 是横切层。每包同构：`service.py` 装配 + `tools.py` 出 ToolSpec + `providers/` 插件。

## 内部结构

**ingest**（service.py 2011 行，全仓最大）：安全核心是路径 allow-list——`_resolve_safe_path`（`ingest/service.py:98`）把用户路径 resolve 后逐一验根，越界抛 CapabilityError（L109-117）。默认根在 L150-170：profile data_dir + cwd + **cwd 父目录** + 临时目录 + `/tmp` + `/private/tmp`。父目录即 L153 注释明说的场景："lets users keep demo data in `~/Desktop/DataMind/demo-uploads/` while running the server from `~/Desktop/DataMind/DataMind/`"。**graph**：唯一后端 `graph/providers/networkx_store.py:33-34` 的 `@graph_registry.register("networkx") NetworkXGraphStore`，实现 `core/protocols.py:302` 的 `@runtime_checkable GraphStore`（L301）。**skills**：`SkillsService`（`skills/service.py:29`）统一 SKILL.md 知识技能（索引进独立 Chroma）与代码技能（ToolSpec 不进索引）。**db**：SQLite/MySQL/Dolt 三方言（`db/providers/sqlite.py:19-20`、`mysql.py:25-26`、`dolt.py:44-45`）同承 `db/base.py:32`；Dolt 走 MySQL 线协议再叠 commit 级版本化（build_engine 自起 `dolt sql-server` 子进程）。

## 外部连接

**GraphEvidence 勘误（重要）**：常被想当然到 `graph/evidence.py` 找——错。实定义在 `core/protocols.py:116`，被 `GraphTriple.evidence` 引用（L139）。`graph/evidence.py` 其实是**落盘器**：`persist_input/persist_bytes`（L8/L12）把非文件来源证据按 sha256 内容寻址写 `data_dir/triplets/evidence/`，重名内容不符抛 integrity 错（L17-19）。skills 复用 kb 基础设施——`skills/service.py:31` 特意 import chroma_store 保证 KB 未加载时 Chroma 也在注册表。

## 数据流

ingest 工具面写、kb/db/graph 工具面读；写操作经 `with_receipts` 包账本（`ingest/ledger.py:293`，IngestLedger L117 落 `ingest_ledger.sqlite3`）。`db_rollback`（`db/tools.py:239`）消费 Dolt 历史。workspace 增量层（`datamind/workspace_incremental.py`，803 行）为破 import 环把依赖下沉函数体：L68、L195-197、L337、L541、L699-708 共 16 处 `from datamind ...` 延迟导入——顶层只留无环依赖，GraphService/KBService/LanceDBVectorStore 等重件进函数才 import。

## 设计决策（含批判）

①allow-list 默认带 cwd 父目录是"演示友好换爆炸半径"的取舍，注释自认，生产须用 `hooks.path_allowlist_extra` 收紧；②`db_rollback` 带 `destructive: True`（`db/tools.py:262`）——危险位显式建模（同标记另有三处：`graph/tools.py:177`、`kb/tools.py:133`、`memory/tools.py:180`，非唯一）。**批判——worksapce 拼写三连是真 bug**：`ingest/tools.py:89-90` 闭包 `_kb_update_worksapce` 调 `svc.kb_update_worksapce()`，L679 handler 同拼错；但服务侧方法实为正确拼写 `kb_update_workspace`（`ingest/service.py:1106`），工具名 L672 也拼对。全仓无 `def kb_update_worksapce`、无 `__getattr__` 兜底——该工具一被调用必 AttributeError（潜伏：仅 cocoindex+LanceDB 路径会调它）。注意三连在 ingest/tools.py 而非 skills 包。

## 新人提示

找图证据类型去 `core/protocols.py`；`graph/evidence.py` 是内容寻址落盘器。报 path outside allowed roots 先对照 L161-170 根列表。读 ingest/service.py 从 `_resolve_safe_path` 调用点反查。workspace_incremental 莫名 ImportError 先想 import 环。Dolt DSN 形如 `mysql+pymysql://root:@127.0.0.1:3307/db`。
