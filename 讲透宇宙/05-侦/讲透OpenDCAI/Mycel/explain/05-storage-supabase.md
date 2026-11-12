# 05 · 存储三层：contracts 契约 / sqlite 控制面 / supabase 仓群与 StorageContainer

## 角色定位

`storage/` 是全仓的数据底座，三层分明：**contracts.py（808 行）**用 typing.Protocol + Pydantic 定义约 25 个仓库接口（SandboxRuntimeRepo/ThreadRepo/UserRepo……44 个 class，契约先行）；**providers/sqlite/** 是沙箱控制面本地库（terminal/sandbox_runtime/chat_session/queue/summary 五仓 + kernel 连接层）；**providers/supabase/** 31 个 py 文件是云上主力（约 29 个仓库实现），由 `storage/container.py` 的 StorageContainer 工厂统一发放。上一层的业务代码（backend/*）只见 repo 接口，不见 SQL 与表名。schema 的真源在 `storage/schema/`：`app_schema.sql` 基线 + `app_schema_manifest.json` 清单 + 10 个增量 patch。

## 内部结构

**契约层**：contracts.py:16 起就是一排 `class XxxRepo(Protocol)`——方法签名即合同，如 `SandboxRuntimeRepo`（contracts.py:16-51）规定 close/get/create/find_by_instance/adopt_instance/observe_status/persist_metadata 等十来个方法，`create` 连 `owner_user_id` 什么时候必填都写进签名（L19-27）。Protocol 是结构化类型：实现类不需要显式继承，鸭子对了就过——所以 sqlite 与 supabase 两套实现天然共享同一契约。

**Container 工厂与声明式注册表**：`_REPO_REGISTRY`（container.py:36-71）把 **34 个**仓库名映射到 `(模块路径, 类名)` 二元组——例如 `"sandbox_runtime_repo": ("storage.providers.supabase.sandbox_runtime_repo", "SupabaseSandboxRuntimeRepo")`（L47）、`"messages_repo"` 等 messaging 系四仓都指向同一个 messaging_repo 模块的不同类（L59-65）。`StorageContainer._build`（container.py:80-83）拿到名字后 `importlib.import_module(mod_path)` 动态加载再实例化——**import 推迟到首次取用时**，COMMUNICATION 形态的进程不会为用不到的仓付 import 成本（呼应 01 篇延迟装配）。`purge_thread`（container.py:187-198）示范了跨仓清理的正确姿势：四个仓各开-清-关，任何一步异常也保证 close。客户端解析在 storage/runtime.py：策略由 `LEON_STORAGE_STRATEGY`（默认 supabase，runtime.py:13-14）决定；supabase 客户端要么显式传入，要么由 `LEON_SUPABASE_CLIENT_FACTORY=<module>:<callable>` 字符串引用构造（runtime.py:211-245，importlib 拆冒号加载并校验产物必须暴露 callable 的 `table()` 方法，L248-253）——storage 层因此不 import 任何后端身份代码，web 后端把自己的工厂（backend.identity.auth.supabase_runtime:create_supabase_client，runtime.py:10）注入进来。

**supabase 仓群的三个防御性细节**：
1. **sandbox_runtime 把运行时状态藏进 JSONB**：`SupabaseSandboxRuntimeRepo` 落在 `container.sandboxes` 表上（sandbox_runtime_repo.py:10-11），运行时身份与全量状态藏在 `config` JSONB 的 `runtime_handle` / `runtime_state` 键里（L15-17，读取在 L50-57 与 L83-92：recipe_id/workspace_key/recipe_json/instance_created_at 都从 config.runtime_state 解出），缺键直接 RuntimeError 拒绝脏行；sandbox 主键由 runtime id 经 UUIDv5 确定性派生（L26-29，`sandbox-{uuid5(NAMESPACE_URL, "mycel-runtime:<id>")}`）——同一 runtime 重放得到同一行，天然幂等 upsert。
2. **PostgREST 大 IN 过滤 502 防御**：`_query.py` 统一查询助手定义 `IN_FILTER_CHUNK_SIZE = 80`（_query.py:6），`value_chunks`/`rows_in_chunks`/`execute_in_chunks`（L106-132）把任意大的 IN 列表切成 80 一批执行；更激进的场合干脆不发 IN——sandbox_monitor_repo.py:242-244 的 @@@monitor-binding-query 注释直说："remote PostgREST can 502 on large sandbox_id IN filters here; monitor already loaded all sandboxes, so filter the small workspace/thread projections locally"（monitor 反正已拉全量沙箱，小的 workspace/thread 投影本地过滤即可，别让这个端点变脆）。
3. **PostgREST 会话保真**：@@@preserve-schema-session（_query.py:28）修 postgrest-py 的坑——`schema()` 会重建全新 httpx client，包装层显式保留原会话。

**sqlite 控制面的双表+指针模式**：terminal 仓两张表——`abstract_terminals`（一 thread 多 terminal，terminal_repo.py:46-57）+ `thread_terminal_pointers`（每 thread 一行，active/default 两个外键指针，L58-69）。建表后用 `PRAGMA table_info` 核对 `REQUIRED_ABSTRACT_TERMINAL_COLUMNS/REQUIRED_TERMINAL_POINTER_COLUMNS`（列集合权威在消费方 sandbox/terminal.py，terminal_repo.py:9-12 导入），缺列或发现旧单终端 schema 残留的 UNIQUE(thread_id) 索引都 RuntimeError + "Purge the configured sandbox sqlite db and retry"（L89-104，@@@no-thread-unique）。sandbox_runtime 仓同款三表（sandbox_runtimes/sandbox_instances/sandbox_runtime_events，契约见 03 篇 runtime_handle 的 REQUIRED_* 集合）。唯一真正"自愈"的是 message_queue：缺 metadata_json 列就地 `ALTER TABLE ADD COLUMN`（queue_repo.py:140-142）——控制面里只有这张高流量表享受自动补列待遇。kernel.py 的 `SQLiteDBRole`（kernel.py:14-29）用 `LEON_SANDBOX_DB_PATH` 显式指定路径，WAL 模式开 journal（terminal_repo.py:43）。

**schema 基线与 manifest 互证**：`app_schema_manifest.json` 声明 schema_version 1、baseline=app_schema.sql、`baseline_table_count: 47`、baseline_function_count 4、六个自有 schema（agent/chat/container/identity/library/observability）与 10 个 patch（agent_config_resolved_config_hardcut.sql、chat_join_requests.sql……）。实测 `grep -c "CREATE TABLE" app_schema.sql` 恰为 **47**——基线 SQL 与 manifest 互证一致，改表必须同时动两处，否则这个数字就是漂移探测器。

## 外部连接

- 上游：01 篇 bootstrap/storage.py 的 `build_storage_container/build_supabase_client` 即本层 runtime.py 出口；lifespan 装配的五个 repo（user/thread/sandbox_runtime/workspace/sandbox）全从这里取。
- 下游：04 篇 threads/messaging 各仓、03 篇沙箱控制面三仓（supabase 双轨开关 `_use_supabase_storage`）、eval 域两仓（eval_repo/eval_batch_repo）。
- 外部系统：Supabase Postgres + PostgREST（表按六 schema 分域）；sqlite 文件按 role 解析路径，沙箱进程与 web 进程共享读写。

## 数据流

一次 web 请求取数据的路径：路由函数从 `app.state` 拿 repo（lifespan 期由 container.xxx_repo() 建好）→ 若是 supabase 仓，经 `_query.py` 组查询（schema_table → select/eq/in_ → execute → rows 校验）→ PostgREST → Postgres；大集合 IN 自动 80 分片。沙箱控制面则本地得多：manager 直接操作 sqlite 三表，desired/observed 状态与事件流写 `sandbox_runtime_events`，WAL 保证多进程读不阻塞。Supabase 双轨时，同一份 SandboxRuntimeRepo 契约有两种实现，`_use_supabase_storage`（03 篇 runtime_handle.py:75）按部署形态选边。线程清理走 `purge_thread`：checkpoint/run_event/file_operation/summary 四仓顺序清，各自 close。

## 设计决策（含批判）

1. **Protocol 契约而非 ABC 继承**：两套实现零耦合，第三套（如 postgres 直连）随时可加。批判：Protocol 不做运行时检查，实现少了方法要到首次调用才炸——好在 `_query.py` 的 validate_client/rows 每步都显式校验能力（hasattr 检查配报错指引，L100-103），把"晚爆炸"压缩到连接建立期。
2. **JSONB 藏状态是给 Supabase 的妥协**：运行时状态结构进化快，塞 JSONB 免去频繁 ALTER TABLE 与跨 schema 迁移；代价是数据库侧无法约束 runtime_state 内部结构，脏数据防御全靠读取端 RuntimeError（L35-45 那排检查就是为此）与 schema patch SQL 兜底。
3. **80 分片 + 本地过滤双保险**：分片治普遍场景，monitor 场景干脆重构查询面治本——"别让端点变脆"这句注释值得当成 PostgREST 使用守则。
4. **fail-loud 清库文化**（与 03 篇一脉相承）：sqlite 缺列一律要求 purge 重来，唯一例外 message_queue 自动补列。对小流量表这正确；若哪天控制面表要在线迁移，这套哲学需要升级而不是硬扛。
5. **manifest 计数互证**是低成本高杠杆的工程习惯：47 这个数字把"基线 SQL 改了忘更新 manifest"类漂移变成一眼可见。批判：目前没有 CI 断言强制比对（数字躺在 JSON 里靠人眼），自动化一步之遥。

## 新人提示

- 加新表的正确顺序：先写 patch SQL 放 storage/schema/ → manifest 的 patches 数组追加文件名（动了基线才改 baseline_table_count）→ contracts.py 加 Protocol → supabase/ 建实现 → container.py 注册表加一行 + 工厂方法。五步缺一，`grep -c CREATE TABLE` 与 manifest 的互证就断。
- 调"schema mismatch: missing [...]"：按报错清 `LEON_SANDBOX_DB_PATH` 指向的库；如果反复出现，说明两处 REQUIRED_* 列集合与建表 SQL 分歧了，去对 sandbox/runtime_handle.py:32-69 与对应 repo 的建表语句。
- 查数据不知道去哪个 schema：六域口诀——agent（threads/checkpoints）、chat（消息）、container（sandboxes/workspaces）、identity（users）、library（skills/recipes）、observability（监控快照）。
- 大 IN 查询爆 502 时别调大 chunk——用 monitor 的思路改查询面（拉小投影本地过滤）；80 这个值是经验阈值，不是规格。
- `LEON_SUPABASE_CLIENT_FACTORY` 报 "Invalid format" 时检查冒号分隔与两侧非空（runtime.py:232-234）；报 "must expose a callable table(name)" 说明工厂返回的不是 supabase-py 风格客户端。
