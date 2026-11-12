# 05 · session_manager.rs：SQLite 会话持久化——跨进程重启的记忆底座

> 源文件：`crates/goose/src/session/session_manager.rs`（2891 行，含 853 行测试）
> 图谱定位：第 1 层「Agent 会话引擎（goose 核心）」（16 层之首），入边 21 条，是全仓被依赖最广的存储枢纽。

## 一、角色定位：谁在读写它

goose 是多进程形态并存的产品：CLI REPL（`goose`）、终端集成（`goose term`）、桌面端（Electron 经 `goosed` REST）、ACP 客户端（IDE 插件）、后台调度器（scheduled sessions）。这些进程各自独立启动、随时崩溃重启，唯一的公共记忆就是 `SessionManager` 管的那一个 SQLite 文件。图谱给出的 21 条入边覆盖了所有消费方：

| 消费方 | 落库点（行号锚实证） |
|---|---|
| Agent 核心循环 | `agents/agent.rs:303` 构造时挂 `SessionManager::instance()`；消息逐条 `add_message`（agent.rs:2373、1718） |
| CLI 命令 | `goose-cli/src/cli.rs:384/458/1401`、`commands/session.rs:95-329`（session 子命令）、`commands/schedule.rs:98-246`、`commands/term.rs:183-325` |
| goosed REST（桌面端后端） | `goose-server/src/routes/session.rs:616-633` 注册 `/sessions` 路由组，`list_sessions`/`get_session`/`truncate_conversation`（routes/session.rs:555）全走它 |
| ACP 协议层 | `acp/server/new_session.rs:40-44` 建会话；`load_session.rs:226` 恢复会话；`manage_sessions.rs:80` 删除会话 |
| 调度器 | `scheduler.rs:843-846` 以 `SessionType::Scheduled` 建定时会话 |
| 遥测/供应商库存 | `posthog.rs:444`、`providers/inventory/mod.rs`（建表被卷进本文件迁移链 v11） |

进程内的组织方式是两级：全局单例 `SESSION_STORAGE: LazyLock<Arc<SessionStorage>>`（session_manager.rs:52-53，绑定 `Paths::data_dir()`），而 `SessionManager`（session_manager.rs:288-290）只是包了一层 `Arc<SessionStorage>` 的薄壳——`instance()` 克隆单例（329-333），`new(data_dir)` 则可指向临时目录（测试隔离用）。所以"多进程共享一个 DB 文件 + 进程内共享一个连接池"是它的双重并发前提。

一个关键语义：**SessionType 七分类**（session_manager.rs:41-50）——`User`（默认）/`Scheduled`/`SubAgent`/`Hidden`/`Terminal`/`Gateway`/`Acp`。默认列举只返回 `User + Scheduled`（session_manager.rs:1687-1690），SubAgent/Hidden 等是"存在但不进历史列表"的隐形会话；ACP 侧按 meta 里有无 `client` 字段区分 User 与 Acp（new_session.rs:22-25）。

## 二、内部结构：单例、三张表、迁移链、事务

### 2.1 常量与连接池

三个公开常量定义了存储布局（session_manager.rs:22-24）：`CURRENT_SCHEMA_VERSION: i32 = 13`、`SESSIONS_FOLDER = "sessions"`、`DB_NAME = "sessions.db"`。`SessionStorage::new` 把它们拼成 `data_dir/sessions/sessions.db`（session_manager.rs:674-675）。

连接池的建立有三处讲究（`create_pool`，session_manager.rs:658-671）：

- `create_if_missing(true)`——首启直接建库；
- `foreign_keys(true)` + `busy_timeout(30s)` + **WAL journal**（663-668）——WAL 是多进程并发读写不打架的基石，busy_timeout 给写冲突留 30 秒重试窗口；
- `connect_lazy_with`——构造时不真连，把初始化推迟到首次查询。

### 2.2 惰性初始化：pool() 是全文件的闸门

`pool()`（session_manager.rs:683-705）用 `tokio::sync::OnceCell` 保证初始化只跑一次，内部逻辑是个分流器：查 `sqlite_master` 有没有 `schema_version` 表（686-691）——**有则走 `run_migrations` 升级，没有则 `create_schema` 直接建到最新版**，并且只在全新建库时尝试导入 JSONL 遗留会话 `import_legacy`（697-699，失败仅 warn 不阻断）。此后所有 API 第一句都是 `self.pool().await?`，等于把"迁移/建表"挂在每个方法的入口懒执行。

### 2.3 三张核心表（外加迁移链衍生物）

`create_schema`（session_manager.rs:713-819）在一个 `BEGIN IMMEDIATE` 事务里建齐：

1. **schema_version**（730-733）：`version INTEGER PRIMARY KEY, applied_at TIMESTAMP`。注意它不是单行版本号，而是**迁移审计流水**——每个版本一行，读取时取 `MAX(version)`（session_manager.rs:968）。
2. **sessions**（746-771）：24 列。主键 `id TEXT`（形如 `20260214_7` 的日期+序号），一列一语义：命名三件套（`name`/`description`/`user_set_name`）、token 九列（当轮 total/input/output + 累计三列 + `accumulated_cost REAL`）、配置快照四列（`recipe_json`/`user_recipe_values_json`/`provider_name`/`model_config_json`——复杂结构全走 JSON 列）、`extension_data TEXT DEFAULT '{}'`、`goose_mode`、`archived_at`、`project_id`。
3. **messages**（779-789）：消息级存储。`id INTEGER PRIMARY KEY AUTOINCREMENT`（插入序）+ `message_id TEXT`（稳定字符串 id）+ 外键 `session_id REFERENCES sessions(id)` + `role` + `content_json`（整个 content 数组的 JSON）+ `created_timestamp INTEGER`（业务时间戳）+ `timestamp`（DB 默认当前时间）+ `tokens` + `metadata_json`。

六个索引（795-809）：messages 的 session_id/timestamp/message_id 三索引 + sessions 的 updated_at DESC/session_type 两索引。**任务书说"三张表"是主干，但完整事实是五张以上**——迁移 v10 又建了 `threads`/`thread_messages` 双表（session_manager.rs:1129-1155），v11 建 providers inventory 表（1164）；它们与三张核心表同库共存。

### 2.4 迁移链：13 个版本的阶梯

`run_migrations`（session_manager.rs:927-950）的逻辑极简：取 `MAX(version)`，若小于 13，则 `for version in (current+1)..=13` 逐版本执行 `apply_migration` 并**立刻插一行新版本号**（938-941、975-984）。每个版本一个 match 臂（987-1211），阶梯史即功能演化史：

- v2/v3：加 `user_recipe_values_json`、`metadata_json` 列（1001-1018）；
- v4：加 `name`+`user_set_name`（1019-1035）——会话从"仅描述"进化出"用户命名"；
- v5：加 `session_type`+类型索引（1036-1048）；
- v6：加 `provider_name`+`model_config_json`（1049-1065）；
- v7：加 `message_id` 列并**回填** `'msg_' || session_id || '_' || id`，再建索引（1066-1087）——存量消息无字符串 id 的补课；
- v8：`goose_mode`（1088-1096）；
- v9：数据修正迁移——把名叫 'ACP Session' 的 user 会话批量改成 `session_type='acp'`（1097-1109）；
- v10：threads 双表 + `thread_id` 列，用 `pragma_table_info` 先查列存在再 ALTER（1110-1162，幂等防御）；
- v12/v13：`archived_at`/`project_id`（1166-1191）、`accumulated_cost`（1192-1204），同样 pragma 防重。

### 2.5 事务与并发：BEGIN IMMEDIATE 是铁律

全文件**所有写路径**统一 `pool.begin_with("BEGIN IMMEDIATE")`（session_manager.rs:726、866、928、1221、1416、1468、1506、1694、1932、1977 十处）。为什么不用默认 DEFERRED？`create_schema` 上方的大段注释（713-725）给出了官方答案：两个进程首启同时看到"表不存在"，第二个的 CREATE TABLE 会撞 `table already exists`；IMMEDIATE 让 SQLite 跨进程串行化写者。更硬的证据是专门写的回归测试 `test_begin_immediate_prevents_lock_upgrade_deadlock`（2402-2433）：用 barrier 强制两个任务同时持 SHARED 锁再双双升级写锁，断言裸 `BEGIN` 必然 SQLITE_BUSY（2418-2422），而 `BEGIN IMMEDIATE` 全部成功（2424-2432）。`update_tool_request_meta` 的文档注释同样点明"Uses BEGIN IMMEDIATE so concurrent writers serialize correctly"（1962-1966）。另有 10 并发会话创建的集成测试（2500 起）锁行为。

读路径则不走事务（如 `get_conversation` 1428-1438 直接 fetch_all），靠 WAL 的读写不互斥。

## 三、外部连接：上游容器、下游文件、导入链

**上游——Session 是行+消息的复合体**。`Session` struct（session_manager.rs:55-89）的 `conversation: Option<Conversation>` 字段就是内存态消息容器：DB 里 sessions 行 + messages N 行，读出时组装成 `Conversation`。`Conversation`/`Message` 实际定义在 `crates/goose-providers/src/conversation/message.rs`，经 `crates/goose/src/lib.rs:12-14` 的 `pub mod conversation { pub use goose_providers::conversation::*; }` re-export 进来——**注意 goose 仓没有 `src/conversation/` 目录**，追代码时直接找会扑空。`Message` 五字段：`id: Option<String>`、`role`、`created: i64`、`content: Vec<MessageContent>`、`metadata`（message.rs:751-758）；`Message::user()` 的 `created` 是**秒级** `Utc::now().timestamp()`（message.rs:788-793）；`with_id` 是 builder 式设 id（809）。

**下游——SQLite 文件路径**。`Paths::data_dir()`（config/paths.rs:42-44）用 etcetera 选平台策略，参数硬编码 `top_level_domain: "Block", author: "Block", app_name: "goose"`，注释明言是为兼容老安装目录"Changing this would orphan existing installations"（paths.rs:20-25）。具体落点以官方调试脚本为准：`scripts/goose-db-helper.sh:104` 给 Linux 路径 `~/.local/share/goose/sessions/sessions.db`，105 行给 macOS `~/Library/Application Support/Block/goose/data/sessions/sessions.db`（该脚本还内置了 DB 备份到 `goose-db-backups/` 与迁移元数据查阅功能，5-19 行）。测试可用 `GOOSE_PATH_ROOT` 环境变量整体重定向数据目录（paths.rs:8-10）。

**导入链——两条**。① 异构 agent 会话导入：`import_session`（session_manager.rs:1758-1802）第一行就调 `import_formats::convert_to_goose_session_json`（1764），由 `detect_format`（import_formats/mod.rs:42-96）嗅探首行 JSON 特征——Codex 必以 `{"type":"session_meta"}` 开头、Pi 以 `{"type":"session"}` 开头、Claude Code 每行带 `sessionId`，goose 原生则是带 `working_dir` 的整块 JSON——四格式统一转成 goose Session JSON 再走同一导入管线（mod.rs:101-108，子模块 claude_code/codex/pi 各三百余行）。② 遗留 JSONL 导入：`import_legacy`（session_manager.rs:821-863）扫描 sessions 目录里的 `.jsonl`（legacy.rs:13-29），按"首行元数据+后续每行一条消息"解析（legacy.rs:62-99），单文件上限 50MB（legacy.rs:11）。

**token 计数衔接**：`update_session_metrics`（agents/reply_parts.rs:499 起）在每轮推理后把 ProviderUsage 写进九个 token 列 + 累计成本；`get_insights` 的聚合 SQL 用双层 COALESCE 兜底——`SUM(COALESCE(accumulated_total_tokens, total_tokens, 0))`（session_manager.rs:1732），老会话没有累计列时回退当轮值。**上下文管理衔接**：`context_mgmt/mod.rs:66` 的 `compact_messages` 压缩完成后，由 agent.rs:1584 调 `replace_conversation` 整体落库。历史搜索 `chat_history_search.rs` 直接共享同一个 pool（图谱 imports 边）。

## 四、数据流：一轮对话从内存到磁盘

以"用户发一条消息、assistant 回一条"为例：

1. **建会话**：`create_session`（session_manager.rs:1213-1256）生成人类可读 id：`today = %Y%m%d`（1223），INSERT 语句里内联子查询 `MAX(CAST(SUBSTR(id, 10) AS INTEGER)) + 1`（1228-1232）——当日第 N 个会话就是 `20260214_N`，序号取第 10 字符之后正好剥掉"8 位日期+下划线"。`RETURNING *` 直接拿回行转 Session。
2. **用户消息落库**：reply 循环里 `messages_to_add` 逐条 `session_manager.add_message(&session_config.id, msg)`（agent.rs:2373）。`add_message`（session_manager.rs:1466-1499）一个事务干两件事：INSERT messages（`message_id` 无则现场生成 `msg_{session_id}_{uuid}`，1472-1475；`role` 经 `role_to_string` 只映射 user/assistant 两值，546-551；content 与 metadata 各自 JSON 序列化）+ `UPDATE sessions SET updated_at = datetime('now')`（1492）——**每条消息都会顶新会话的排序时间戳**。
3. **assistant 回复落库**：流式回复的最终消息同样走 `add_message`（agent.rs:1718），stop-hook 拒绝注入的上下文消息也走它（1744）。
4. **token 回写**：`update_session_metrics`（reply_parts.rs:499）组装 `SessionUpdateBuilder` 九个字段 `.apply()`，落到 `apply_update`（session_manager.rs:1295-1426）：动态拼 `UPDATE sessions SET` 子句（`add_update!` 宏只拼 Some 字段），**末尾无条件追加 `updated_at = datetime('now')`（1342）**，rows_affected==0 报 Session not found（1420-1421）。
5. **会话名生成**：`maybe_update_name`（session_manager.rs:429-467）在用户消息数 ≤3（`MSG_COUNT_FOR_SESSION_NAME_GENERATION = 3`，providers/base.rs:98）时让 provider 生成会话名并 `system_generated_name` 写回（450-455）；用户手动命名后（user_set_name=true）永不覆盖（436-438）。

**恢复/列举/删除**：

- 恢复：`get_session(id, true)`（session_manager.rs:1258-1292）查 sessions 行后调 `get_conversation`（1428-1464）重放消息，`ORDER BY created_timestamp, id`——1431-1434 的注释解释了为什么需要双键：`created_timestamp` 是秒级，同一秒内的 tool request/response 靠 AUTOINCREMENT id 保插入序。重建的 Message 用 `Conversation::new_unvalidated`（1463）绕过校验。`include_messages=false` 时只 `COUNT(*)` 不搬数据（1283-1287）。ACP 恢复会话就是这条路径（load_session.rs:226）。
- 列举：统一入口 `list_sessions_matching`（1550-1634）动态拼 WHERE（类型 IN/工作目录/游标）+ JOIN messages 统计 message_count + `ORDER BY updated_at DESC, id DESC`（1581-1585）。分页是 keyset 式：游标 `(updated_at, session_id)` 双键比较（1563-1569），多取一条 `page_size + 1` 探测下一页（1663-1679）。1623 行注释坦承库里混存 SQLite `CURRENT_TIMESTAMP` 与 RFC3339 两种格式，游标比较前必须 `datetime()` 归一。
- 删除：`delete_session`（1692-1718）先 `DELETE FROM messages` 再 `DELETE FROM sessions`（1706-1714），先子后父保外键约束，单事务防半删。
- 特殊写路径：`truncate_conversation` 按 `created_timestamp >= ?` 删尾部（1849-1858，server 端 routes/session.rs:555 与 term.rs:284 的"重发前清掉未答消息"都靠它）；`replace_conversation` 是 DELETE 全部 + 逐条重插（1506-1537），压缩/重试换历史时用；`update_tool_request_meta`（1967-2017）在 content_json 里定位某个 ToolRequest 打补丁合并 tool_meta，配 `merge_tool_meta` 的保旧键浅合并（2022-2036），让 LLM 生成的工具标题跨重载存活（523-526 注释）。

## 五、设计决策：注释背书与推断

**为何 SQLite 而非 JSON 文件**（部分有注释背书，部分推断）：①多进程并发是硬需求——CLI、goosed、调度器可同时开，注释明言"SQLite serializes writers across processes"（session_manager.rs:715-716），WAL+busy_timeout 30s（667-668）是这套并发的三件套；②查询能力——按类型/工作目录/时间窗过滤、keyset 分页、全文历史搜索（search_chat_history，469-488）都要在存储层做，JSON 文件只能全量扫（推断）；③一次性导入 JSONL 遗留格式反而证明 JSON 文件的局限——现在它们只是被迁移的客 体（821-863）。

**schema_version 流水 vs 单行版本 vs 重建**：采用"每版本一行+MAX 取当前"（730-733、968）而非 UPDATE 单行，保留了"何时升到 v 几"的审计痕迹（applied_at 列）；v9 这种**数据修正型迁移**（1097-1109）只有流水模型才能表达；v10/v12/v13 先 `pragma_table_info` 查列再 ALTER（1112-1117 等）——因为 create_schema 直接建到最新版（739-742 还 `INSERT OR IGNORE` 版本号），新旧两条初始化路径会交错，幂等防御成了必需。迁移失败的代价是全库不可用，所以整个阶梯裹在单事务里（928-948），任何一版失败整体回滚。

**消息级而非会话级粒度**：messages 表一行一消息（779-789），收益是 append-only 增量写（add_message 一条 INSERT）+ 可对单消息打补丁（update_message_metadata 1920-1960、update_tool_request_meta 1967-2017）+ 时间戳截断（truncate 1851）；代价是压缩场景要整表重写（replace_conversation 1506-1537）——goose 选择了"常规路径廉价、压缩路径昂贵"的取舍，而压缩本来低频（推断）。

**双时间戳体系**：`created_timestamp`（业务时间，排序键）与 `timestamp`（DB 默认，审计键）分列（785-786）；updated_at 由 `datetime('now')` 维护（1342、1492）。已知毛边：本文件测试自己用 `timestamp_millis()`（2527）而生产路径是秒级 `timestamp()`（message.rs:792），同会话混用两种精度时"同秒平局靠 id"的注释（1431-1434）语义会漂移——这是坑不是设计。

## 六、新人提示

**迁移加字段的正确姿势**（五处同步，缺一静默失败）：
1. `CURRENT_SCHEMA_VERSION` +1（session_manager.rs:22）；
2. `apply_migration` 加 match 臂，**先 `pragma_table_info` 查列存在**（照抄 v13 模板 1192-1204）；
3. `create_schema` 的 CREATE TABLE sessions/messages 同步加列（746-771/779-789）——否则新装用户走直建路径拿不到该列；
4. `Session` struct 加字段（55-89）+ `FromRow` 实现加 `try_get`（592-654）；
5. `SessionUpdateBuilder` 加 `Option<Option<T>>` 字段 + setter（106-286）+ `apply_update` 的 `add_update!` 与 bind 两段（1312-1413）——**SELECT 列清单也要加**（get_session 的 1262-1268 与 list_sessions_matching 的 1594-1600），漏了会直接 SQL 报错缺列。

**调试入口**：
```bash
DB=~/.local/share/goose/sessions/sessions.db   # Linux；macOS 见 goose-db-helper.sh:105
sqlite3 $DB "SELECT version, applied_at FROM schema_version;"   # 迁移史
sqlite3 $DB "SELECT id, name, session_type, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 5;"
sqlite3 $DB "SELECT message_id, role, created_timestamp FROM messages WHERE session_id='20260214_1' ORDER BY id;"
sqlite3 $DB ".schema messages"
bash scripts/goose-db-helper.sh            # 官方备份/迁移查看器
```
进程内追踪首启迁移日志：`run_migrations` 会逐版打 info（933-944）。

**坑清单**：
- `FromRow` 对 `model_config_json`/`accumulated_cost`/`goose_mode` 等大量用 `try_get(...).ok().flatten()` 静默容错（session_manager.rs:603、638、646-650）——**列值损坏不报错而是悄悄变 None/default**，排查"字段丢了"先怀疑这里；`goose_mode` 塞 'garbage' 会静默回退 'auto'（测试 2798-2821 实证）。
- `get_conversation` 对未知 role 直接 `continue` 丢消息（1444-1448），脏数据会无声缩水。
- `role_to_string`（546-551）只映射两种 Role 且无 `_` 兜底——rmcp Role 加变体时这里编译期报错，是故意的不留退路。
- 单例 `instance()` 全进程共享 `Paths::data_dir()`，**测试必须用 `SessionManager::new(TempDir)`**（2404、2502 均如此），否则测试互踩真库。
- `replace_conversation` 会换 messages 的整型主键 id（DELETE+重插，1508-1534），依赖行 id 的外部逻辑会断；但字符串 `message_id` 保留（1516-1519）。
- 会话 id 的当日序号取 `SUBSTR(id, 10)`（1229）——**前 9 字符必须是 8 位日期+下划线**，手工插 id 破坏此格式会让序号回卷到 1。
- 时间格式混存（1623 注释）：任何拿 updated_at 做比较的 SQL 都要包 `datetime()` 归一，游标逻辑已经踩过。
- `import_legacy` 失败只 warn（697-699），升级后"少了老会话"去日志找 `Failed to import`。

---

### 附：本篇行号锚清单（全部 sed/grep 核实）

session_manager.rs：22-24, 41-50, 52-53, 55-89, 106-130, 288-290, 329-333, 429-467(450), 523-526, 540-544, 546-551, 592-654(603,638,643), 658-671(663-668), 674-675, 683-705(686-691,697-699), 713-725, 726, 730-733, 746-771, 779-789(785-786), 795-809, 821-863, 927-950(938-941,968), 975-984, 987-1211(1019-1035,1066-1087,1097-1109,1110-1162(1112-1117,1129-1155),1164,1192-1204), 1213-1256(1223,1228-1232), 1258-1292(1262-1268,1283-1287), 1295-1426(1312-1413,1342,1420-1421), 1428-1464(1431-1434,1444-1448,1463), 1466-1499(1472-1475,1492), 1501-1539(1506-1537,1508-1534,1516-1519), 1550-1634(1563-1569,1581-1585,1594-1600,1623), 1644-1685(1663-1679), 1687-1690, 1692-1718(1706-1714), 1720-1751(1732), 1753-1756, 1758-1802(1764), 1849-1858(1851), 1869-1883, 1920-1960, 1962-1966, 1967-2017, 2022-2036, 2402-2433(2418-2422,2424-2432), 2500, 2502, 2527, 2798-2821
其他文件：providers/base.rs:98 · agents/agent.rs:303,1584,1718,2373 · agents/reply_parts.rs:499 · context_mgmt/mod.rs:66 · session/import_formats/mod.rs:42-96,101-108 · session/legacy.rs:11,13-29,62-99 · goose-cli/src/commands/term.rs:183-325(284) · goose-server/src/routes/session.rs:555,616-633 · acp/server/new_session.rs:22-25,40-44 · acp/server/load_session.rs:226 · acp/server/manage_sessions.rs:80 · scheduler.rs:843-846 · goose-providers/src/conversation/message.rs:751-758,788-793,809 · config/paths.rs:8-10,20-25,42-44 · lib.rs:12-14 · scripts/goose-db-helper.sh:5-19,104,105 · session/mod.rs:15-17

与任务书的两处出入（按源码为准）：①"三张表"实为核心三表 + threads/thread_messages（v10）+ inventory（v11）同库共存；②SessionType 除任务书点名的交互类型外共七种，SubAgent/Hidden/Terminal/Gateway 四种是列表默认不可见的隐形会话。
