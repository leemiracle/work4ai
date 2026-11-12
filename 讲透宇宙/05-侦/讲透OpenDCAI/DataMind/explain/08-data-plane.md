# 08 · workspace/ 数据平面：增量存储、直构装配与指纹短路豁免

> 对象：`datamind/data_plane.py`（119 行门面）、`datamind/runtime.py`（143 行装配器）、`datamind/workspace_incremental.py`（803 行增量存储核心）、`datamind/workspace_native.py`（488 行 Dolt 原生层）与 `capabilities/ingest/ledger.py` 的指纹豁免。这是 v2.1.0 增量 workspace 存储（CHANGELOG 首条）的落点。

## 一、角色定位

数据平面（data plane）是 DataMind"模型不做数据决策"哲学的物理载体：Codex 负责 SQL/三元组的编写与解释，数据平面只提供**策略校验过的直连数据工具**。`data_plane.py` L1 的 docstring 一句话定调："Direct, policy-checked data tools. Codex owns planning and interpretation."。它与 agent loop 彻底解耦——装配时（runtime.py L49 `assemble_data_plane`）从不构造对话客户端或模型循环（L50-51 docstring 明示），这意味着 ingest/检索/SQL 执行不需要任何 LLM 凭据即可运转。

workspace 家族五文件（workspace.py 548 行 / workspace_incremental.py 803 行 / workspace_native.py 488 行 / workspace_catalog.py 355 行 / workspace_migration.py 283 行）则是数据平面之下 2.1.0 新增的第二存储引擎：共享不可变源对象 + 源级 SQLite 图断言 + LanceDB 版本 + Dolt 提交，替代每次发布全量快照的旧模式。

## 二、内部结构

**DataPlane 类**（data_plane.py L36-113）核心是 L49-86 的 `call()`：取 ToolSpec → read_only 时拒绝 WRITE 工具（L52-53）→ profile 匹配校验（L55-56）→ 过滤 Python 调用方传入的 None 可选参（L60-62）→ jsonschema `Draft202012Validator` 校验并强制 `additionalProperties: False`（L66-67）→ hooks.pre 三态分流：`Deny` 抛 PermissionError（L70-71）、`AskUser` 直接返回 requires_confirmation 结构不执行（L72-75）、`Rewrite` 改参后重校验（L76-78）→ 执行 handler → finally 里 hooks.post（L84-86）记录成败。L17-20 的 `MODEL_TOOLS` frozenset 列出五个"模型内部生成"工具（`db_query_nl`、`graph_add_path` 等）——直连平面会把它们过滤掉（runtime.py L140-141），因为 Codex 应自己写 SQL 而不是调 NL2SQL。

**workspace_incremental.py 的 18 处函数内延迟 import** 是本文件最显眼的体味：L68、L92（openpyxl）、L195-197、L337、L465、L541、以及 L699-708 **连续十条**的构建期集中导入（GraphService、build_db_tools、build_kb_tools、KBService、LanceDBVectorStore、retriever_registry、ToolAccess、PinnedVectors/PinnedDB、GraphView、runtime）。这不是风格癖好而是**破循环下沉**：本模块被 capabilities/{graph,db,kb} 的工具构建函数反过来引用，若在模块顶层 import 就形成 import 环。L699-708 那段是"运行中重建服务集"的函数——它需要的能力层恰好都依赖本模块，只能就地导入。

**workspace_native.py** 三个原生类：`PinnedVectors`（L43，钉版本的向量读视图）、`DoltRepository`（L76，L79 把原生 Dolt 仓放在 `workspace.root / "shared" / "dolt"`）、`PinnedDB`（L292，钉版本 SQL 视图，L369 list_versions）。L82 `_reap_interrupted_server` 处理上次进程死亡残留的 dolt sql-server（L100 以命令名 `dolt` 结尾做防误杀判定）。L388 `prune_native` 做原生层压实。

## 三、外部连接

- **直构绕过工厂——SkillsService 无语义索引**：runtime.py L73-75 直接 `SkillsService(skills_dir=..., profile_skills_dir=..., embedding=None, vector_store=None)`，而正规工厂 `build_skills_service`（capabilities/skills/service.py L218-249）在检测到 embedding/LLM 凭据时会构建 embedding 并在 `storage_dir / "chroma_skills"` 建 Chroma 集合（L233-240）。**直构显式传 None，等于数据平面里的 skills 检索永远只有精确名/manifest 查找，Chroma 语义索引不启用**——这是有意为之：装配注释（runtime.py L50-51）强调数据平面不建对话客户端，工厂那套"有 key 就建索引"的隐式行为被刻意关掉。
- workspace_incremental.py L541 延迟导入 `LanceDBVectorStore`、L196 导入 `workspace_graph.put_graph`——增量存储同时挂接 KB 向量栈与图栈。
- `data_plane.py` L116-118 的 `build_data_plane` 是薄转发到 runtime 的 `assemble_data_plane`（seed 脚本与测试走这个入口）。
- ledger 指纹豁免（见下）把 ingest 工具的幂等语义与 workspace 发布语义缝合在一起。

## 四、数据流

一次带回执的写操作：调用方 → `DataPlane.call`（schema+hooks 闸）→ `with_receipts` 包装的业务写（runtime.py L136）→ `IngestLedger` 先算源指纹查历史回执 → 命中且不豁免则直接返回 `status="unchanged"` 的零写回执；否则执行真实写入并追加回执。workspace 侧：增量构建走 `DoltRepository.build`（L172，base+tables+revision）产出新 Dolt 提交，向量侧写 LanceDB 版本，图断言写源级 SQLite；发布后 `WorkspaceReader`（workspace.py L449）提供不可变读视图。

**指纹短路的豁免语义**（ledger.py L207-220）是本篇最值得记住的设计：注释 L207-211 写明"回执只证明这些参数过去成功过，不证明目标表现在还含那些行；替换类操作必须在 A→B→A 场景仍然执行"。实现是两个豁免集合：`replaces_table`（L212-215）= 三个 `db_import_*` 工具且 `if_exists == "replace"`；`replaces_source`（L216-220）= kb_add_file、kb_update_workspace、workspace_publish、graph_replace_source 等十四个源替换型工具。**非豁免的 append/fail 类导入保留回执短路重试行为**——同参数重复调用直接判 unchanged，防重复 append。

## 五、设计决策（含批判）

1. **验证三明治**：call() 里 schema 校验出现在 hooks 之前与 Rewrite 之后各一次（L66-67、L78），保证改写后的参数同样合规。批判：两次手写校验有漂移风险，可提取成局部函数。
2. **豁免白名单是补丁式演进**：replaces_source 集合十四个工具名硬编码在 ledger 内（L216-220），新增源替换工具若忘了登记就会被指纹短路误判 unchanged——名字集合分散在 tools 注册处与 ledger 两处，没有单一事实源。
3. **18 处延迟 import 是循环依赖的显式税**：能跑但可读性差。若把"运行中重建服务集"抽到独立模块，L699-708 十条可消掉一半。批判性地看，这是 capabilities 层与 workspace 层互相引用的架构味道，2.1.0 为赶增量存储没有做彻底分层。
4. **aclose 的幂等去重**（data_plane.py L101-113）用 `id(resource)` 集合防止同一客户端被关两次——细节到位。
5. **SkillsService 关语义索引**的取舍：换来实现"数据操作零凭据"（安装后 `datamind info` 即可用），代价是 skills 检索质量降级到精确匹配——对中文模糊问句不友好，属已知妥协。

## 六、新人提示

- 测试 `datamind/tests/test_two_agent_data_plane.py`、`test_workspace_incremental.py`、`test_workspace_native_db.py` 是本层的 tested_by 主力；`test_replace_receipts.py` 专测指纹豁免的 ABA 场景。
- 动 capabilities 层的构建函数签名时，先 grep `workspace_incremental.py` 的延迟 import 清单——那 18 处是最容易被重构破坏的隐性契约。
- 排查"明明导入过数据却查不到"：先看回执是不是 `unchanged`（指纹短路命中），再确认工具是否在豁免集合里。
- Dolt 相关测试只在 CI 的 databases job（装了 dolt extra+钉版二进制）真跑，本地没装 dolt 会 skip——CI 用 `scripts/ci_required_tests.py` 把 skip 变失败，本地不复现。
- `chroma_skills` 目录只在走 `build_skills_service` 工厂的路径才会创建（skills/service.py L236）；数据平面路径下看到它说明有别的入口（如 legacy seed 脚本清理清单 seed_enterprise_demo.py L900 还列着它）跑过。

行号锚：data_plane.py:1/17-20/36/49-86/101-113/116-118 · runtime.py:49-51/61-63/73-75/82-88/124/132-141 · workspace_incremental.py:68/92/195-197/337/465/541/699-708 · workspace_native.py:43/76/79/82/100/172/292/369/388 · workspace.py:37/56/449 · capabilities/ingest/ledger.py:207-220/212-215/216-220 · capabilities/skills/service.py:218-249/233-240
