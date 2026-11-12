# 02 · service/server/database.py — 双后端抽象 + 1292 行 DDL：平台唯一 schema 权威

## 1. 角色定位

database.py 承担两件事：其一，**SQLite/PostgreSQL 双后端连接抽象**——所有业务 SQL 以 SQLite 方言书写，PG 后端在执行前逐条改写（database.py:193-201）；其二，**整个平台的建表迁移权威**——`init_database()`（database.py:403）从 403 行一路铺到 1695 行文件尾，约 1292 行的巨型幂等迁移函数。

先钉版一处高价值勘误：**全库表数是 49 张，不是 21 也不是 22**。`grep -c "CREATE TABLE IF NOT EXISTS"` 实测 49（database.py:414-1338）；ONBOARDING 引用的 migrate_sqlite_to_postgres.py TABLE_ORDER 只有 22 张，那是历史一次性迁移脚本的子集（缺 challenges/team_missions/experiments 等三大族的全部表），**database.py 才是权威快照**——以迁移脚本倒推表数会漏掉一半业务域。

另有一枚血统化石：SQLite 默认落盘路径是 `data/clawtrader.db`（database.py:25），AI-Trader 由 ClawTrader fork 改名的铁证直接写进了数据层。

## 2. 内部结构

文件可分四段：

**方言适配管线（database.py:27-207）**。五个正则 + 三个改写函数构成 SQL 翻译器：`AUTOINCREMENT`→`SERIAL PRIMARY KEY`（:195）、`REAL`→`DOUBLE PRECISION`（:196）、`ALTER TABLE ... ADD COLUMN`→加 `IF NOT EXISTS`（:197）、`datetime('now')` 系→PG 的 `to_char(...AT TIME ZONE 'UTC')`/`INTERVAL` 形式（:182-190，UTC 钉死消除时区漂移）。两个精妙细节：`_escape_psycopg_percent_literals`（:161-179）必须先于 `?`→`%s` 翻译执行（:199-200 调用顺序），否则新引入的 `%s` 会被二次转义；`_replace_unquoted_question_marks`（:90-158）是手写状态机，逐字符追踪单/双引号、行/块注释四种上下文，只翻译「不在字符串里」的 `?`——`LIKE '%foo?'` 这类字面量不会被误伤。

**包装类（database.py:210-302）**。`DatabaseCursor.execute` 在 PG 分支做适配+一个关键补丁：对无 `RETURNING` 的 `INSERT INTO` 自动追加 `RETURNING id` 并捕获回填 `self.lastrowid`（:221-228）——用 PG 能力模拟 SQLite 的 lastrowid 语义，让上层业务代码完全无感后端差异。`DatabaseConnection` 是上下文管理器：异常走 rollback+close、正常走 commit+close（:286-299），`__getattr__` 兜底透传原生连接属性（:301-302）。

**连接工厂（database.py:305-359）**。`using_postgres()` 就是 `bool(DATABASE_URL)`（:48-49）——判断极简，代价是 config 必须保证空串与 None 等价。PG 用 `psycopg.connect(..., row_factory=dict_row)` 统一字典行（:312）；SQLite 侧开 `journal_mode=WAL` + `busy_timeout=30000`（:322-323），30 秒写锁等待是本地并发跑 worker+API 的缓冲垫。psycopg 是可选依赖（:16-21 try import），没装且没配 PG 时启动不炸、配了才报 RuntimeError（:308-311）。

**巨型 DDL（database.py:403-1695）**。PG 下先存旧 autocommit 再切 True（:407-409），跑完恢复（:1692-1693）——psycopg 默认隐式事务下 DDL 混着 ALTER 异常捕获会卡住。49 张表分七族铺开：agent 基础（:414-475）、交易市场（listings/orders/signals/positions 等 :477-676）、polymarket 结算（:678）、实验族（:700-766）、挑战族十表（:767-1016）、团队任务族八表（:1057-1191）、四条快照线+profit_history（:1192-1338）。71 个 `CREATE INDEX IF NOT EXISTS` 压轴在 :1340-1688——「先建全表再统一建索引」的顺序一目了然。

**迁移模式**：20 处 `ALTER TABLE ... ADD COLUMN` 全部裹 `try/except Exception: pass`（如 :964-966、:1250-1252）——列已存在则吞异常，实现幂等升级。专门函数 `_ensure_challenge_trades_source_signal_nullable`（:362-400）处理 SQLite 没有 `ALTER COLUMN DROP NOT NULL` 的硬限制：PG 一行搞定（:365），SQLite 走 rename→重建表→复制→删备份的四步重建（:374-400）。

## 3. 外部连接（对齐图谱边）

- **config.py**：`from config import DATABASE_URL`（:14）是唯一配置入口；`DB_PATH` 环境变量可改 SQLite 路径（:26）。
- **main.py / worker.py**：进程启动时调 `init_database()`+`get_database_status()`，是本模块的两个进程级消费者。
- **全部业务模块**（services/routes_*/challenges/team_missions/rewards/experiments 等）：统一经 `get_db_connection()` 取连接，无一例外走 DatabaseCursor 翻译层——没有任何模块直连 sqlite3/psycopg。
- **写事务惯例**：`begin_write_transaction`（:56-61，PG 用 `BEGIN`、SQLite 用 `BEGIN IMMEDIATE` 立即拿写锁）被 8 个业务模块使用（experiments/challenges/rewards/team_missions/experiment_metrics/signal_quality/routes_signals 及两个 repair 脚本）——多步写（如奖励发放+余额更新）的原子性靠它。
- **可重试错误判定**：`is_retryable_db_error`（:64-87）识别 SQLite locked/busy 与 PG sqlstate 40001（序列化失败）/40P01（死锁）/55P03（锁不可用，:45）；services.py 的积分发放重试环（services.py:152-153，3 次退避 `0.5*(attempt+1)` 秒）直接消费它。

## 4. 数据流

一条 SQL 的完整旅程：业务代码 `cursor.execute(sql, params)` → DatabaseCursor 判后端 → PG 路径先 `_adapt_sql_for_postgres` 五连改写，若是纯 INSERT 再补 `RETURNING id`，执行后 fetch 回填 lastrowid → 结果统一 `fetchone/fetchall`（PG 已是 dict_row）。事务边界三种形态并存：①上下文管理器自动 commit/rollback（读多写少场景）；②显式 `begin_write_transaction` 包多步写；③PG 默认隐式事务+DDL 期 autocommit 例外。连接生命周期短平快——services.py 的典型用法是「取连接→单查询→close」（services.py:21-27），没有连接池，靠 PG 侧自身与 SQLite 的低并发假设支撑。

## 5. 设计决策

- **SQLite 方言为书写基准、PG 为翻译目标**：团队只维护一套 SQL，本地零依赖起步、生产 PG 部署共用代码。代价是 SQL 必须守方言兼容子集——不能写 PG 独有的 `ON CONFLICT ... DO UPDATE`（SQLite 支持但版本敏感）、JSONB、窗口函数随意用等，新人写查询前先想「翻译器认不认」。
- **启动期幂等 DDL 替代版本化迁移工具**：无 Alembic、无 schema_version 表，靠 `IF NOT EXISTS`+try/except 吞异常实现「每次启动收敛到最新 schema」。优点是零心智负担、永不半途卡死；代价是迁移历史只能靠 git 考古，且 except Exception 过宽会吞掉真错误（如磁盘满同样被静默）。
- **重建式迁移的隐患**：`_ensure_challenge_trades_source_signal_nullable` 的 SQLite 重建路径中，重建表结构含 token_id/outcome 两列（:383-384）但 INSERT 复制清单只列 11 列（:394-397）不含这两列——若一个老 SQLite 库在触发重建前已通过后续 ALTER（:964/:968）积累了 token_id 数据，重建会把它们清成 NULL。触发面窄（仅「source_signal_id 还是 NOT NULL 的老库」+SQLite），生产 PG 走 :365 一行路径不受影响，但这是 try/except 迁移模式「静默吞数据」风险的活标本。
- **BEGIN IMMEDIATE 而非默认 BEGIN**：SQLite 默认 BEGIN 是 deferred 锁，多写事务并发时会在第一条写语句处爆发锁冲突风暴；立即拿写锁把冲突提前到事务起点，配合 busy_timeout 整体重试，与 is_retryable_db_error 形成闭环。
- **DDL 期 autocommit 切换**（:407-409/:1692-1693）：迁移语义（每条独立生效、失败可跳过）与业务事务语义（原子回滚）本质冲突，这里明确选择了前者。

## 6. 新人提示

1. 加新表/新列只改这一个文件：新表抄 `CREATE TABLE IF NOT EXISTS` 骨架放 :414-1338 区间对应族位置，索引进 :1340-1688 压轴区；给老表加列必须同时写「新 CREATE 里的列定义」+「try/except ALTER」两处，漏后者则老库升级即崩。
2. 写业务 SQL 前自查翻译器五条规则（:193-201）；字符串字面量里的 `?` 和 `%` 都已被状态机正确处理，不必手动转义。
3. 多步写操作记得 `begin_write_transaction`，否则 PG 隐式事务下中途异常会出现半提交语义不一致；单查询不需要。
4. 排查「本地没有这张表」类问题直接 grep 本文件表名——49 张表全在此，别信迁移脚本或文档的表清单（都是 22 张口径的旧快照）。
5. 想看某表完整列结构，直接跳到对应 CREATE 行号（如 team_missions :1057、experiments :719、agent_reward_ledger :749）；列级变更史则 grep `ALTER TABLE <表名>` 把 try/except 段捞出来对照。
