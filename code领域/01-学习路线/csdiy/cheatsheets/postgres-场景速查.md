# PostgreSQL · 排障与调优场景速查

> 一行场景 → 一条 SQL。慢查询看 EXPLAIN，死锁看 pg_locks，复制看 lag。

## 🚨 最常用 5 条
```sql
SELECT * FROM pg_stat_activity WHERE state != 'idle';     -- 谁在跑、卡在哪
SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;  -- 跑最久的
SELECT pid, query FROM pg_stat_activity WHERE state='active'; -- 拿到 pid 准备终止
SELECT pg_terminate_backend(<pid>);                       -- 杀掉某条 SQL
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;  -- 历史 top10 慢
```

---

## 慢查询
### 开启慢查询统计
```sql
-- 需 postgresql.conf 设 shared_preload_libraries='pg_stat_statements' 并重连
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- 总耗时 top / 平均耗时 top / IO 大户
SELECT query, calls, total_exec_time, mean_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
SELECT query, shared_blks_read+shared_blks_hit AS blocks FROM pg_stat_statements ORDER BY blocks DESC LIMIT 10;
SELECT pg_stat_statements_reset();           -- 重置统计，便于观察一段时间
```

### 当前慢查询（>1 分钟）
```sql
SELECT pid, now()-query_start AS duration, state, left(query,100) AS q
FROM pg_stat_activity WHERE state!='idle' AND now()-query_start > interval '1 minute' ORDER BY duration DESC;
```

### 单条日志慢查询阈值
```bash
# postgresql.conf
log_min_duration_statement = 500           # 慢于 500ms 的 SQL 自动记日志
# auto_explain 自动记录执行计划（shared_preload_libraries 加 auto_explain；log_min_duration='1s' log_analyze=on）
```

### EXPLAIN ANALYZE 读法
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;    -- 真实跑一遍看耗时
-- 节点行示例：Seq Scan on users (cost=0.00..154.00 rows=100 width=4) (actual time=0.5..3.2 rows=100 loops=1)
```
```
读法：
  cost 起启..总成本，高=慢；estimated rows vs actual rows 差很多 → 跑 ANALYZE 表更新统计
  Buffers: shared hit=N read=M；hit 高好，read 大要读盘
  Seq Scan 大表 = 没用索引；Index Scan/Index Only Scan 才快
  Nested Loop 大表+内表无索引=灾难；Sort external merge Disk = 溢出磁盘，调大 work_mem
  loops=N 的 actual time 是每次循环的，总时间要 × loops
```

### 索引失效（用了但没生效）
```sql
SELECT * FROM t WHERE lower(name)='abc';          -- 函数调不用索引；建 expression index: CREATE INDEX ON t(lower(name));
SELECT * FROM t WHERE date_trunc('day',ts)>now(); -- 改成 ts >= '2024-01-01' 才能用索引
SELECT * FROM t WHERE id='123';                   -- id 是 int，传字符串可能不用索引（类型不匹配）
SELECT * FROM t WHERE name LIKE '%abc';           -- 前导 % 用不了 B-tree；建 pg_trgm GIN：
CREATE EXTENSION pg_trgm; CREATE INDEX ON t USING gin (name gin_trgm_ops);
-- != / NOT IN / 隐式转换 / OR 子句 / NULL 比较通常也不用索引
-- 验证：EXPLAIN 出现 Index Scan / Index Only Scan = 用了
```

### 重建统计
```sql
ANALYZE users;                  -- 更新统计信息（不锁表），VACUUM ANALYZE 顺带清死版本
SET enable_seqscan = off;       -- 临时禁用 seqscan 测试是否真有索引可用（仅测试，勿在产线开）
EXPLAIN SELECT ...; RESET enable_seqscan;
```

---

## 死锁 / 锁
### 看当前锁
```sql
-- 谁在等谁（最常用）
SELECT blocked.pid, blocked.query AS waiting,
       pg_blocking_pids(blocked.pid) AS blocked_by
FROM pg_stat_activity blocked
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0;
-- 锁对象 + 模式细节
SELECT pid, locktype, relation::regclass, mode, granted FROM pg_locks WHERE NOT granted;
```

### 锁模式速查
```
ACCESS SHARE      SELECT 自动加（最弱）
ROW EXCLUSIVE     INSERT/UPDATE/DELETE 自动加
SHARE             CREATE INDEX（阻塞写不阻塞读）
ACCESS EXCLUSIVE  ALTER/DROP/TRUNCATE/VACUUM FULL（最强，全阻塞）
```

### 死锁日志与终止
```bash
# postgresql.conf
log_lock_waits = on            # 锁等待超 deadlock_timeout 就记日志
deadlock_timeout = '200ms'     # 检测死锁的间隔
# 日志出现 "deadlock detected" + 两条 SQL → 两事务加锁顺序不一致；解决：统一按 id 升序加锁
```
```sql
SELECT pg_cancel_backend(<pid>);                 -- 取消当前查询（SIGINT）
SELECT pg_terminate_backend(<pid>);              -- 直接杀连接（SIGTERM）
-- 一键杀 idle in transaction 超 10 分钟的
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state='idle in transaction' AND state_change < now() - interval '10 minutes';
```

---

## 复制
### 主从延迟
```sql
-- 主库：看 WAL 发送情况
SELECT application_name, state, sync_state,
       sent_lsn, write_lsn, flush_lsn, replay_lsn,
       (sent_lsn - replay_lsn) AS replication_lag
FROM pg_stat_replication;

-- 从库：看接收/回放
SELECT status, receive_lsn, replay_lsn,
       (receive_lsn - replay_lsn) AS apply_lag
FROM pg_stat_wal_receiver;

-- 延迟秒数（从库执行）
SELECT now() - pg_last_xact_replay_timestamp() AS lag_seconds;
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(),
       pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) AS bytes;
```

### replication slot（堆积爆盘）
```sql
SELECT slot_name, plugin, slot_type, active,
       pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots;
-- active=f 且 lag_bytes 一直涨：消费者挂了，slot 在主库堆 WAL，会撑爆磁盘！
-- 删除无用 slot
SELECT pg_drop_replication_slot('old_slot_name');
```

### 复制冲突
```sql
-- 从库执行
SELECT * FROM pg_stat_database_conflicts;
-- 常见：主库 truncate/锁变更，从库查询还在跑 → 从库取消查询
-- 解决：调 max_standby_streaming_delay，或业务从库只读 + 短查询
```

---

## VACUUM / 膨胀
### 看膨胀程度
```sql
-- pgstattuple 扩展精确测量（开销大，按需）
CREATE EXTENSION pgstattuple;
SELECT * FROM pgstattuple('users');               -- dead_tuple_percent 高 = 膨胀

-- 估算：n_dead_tup / n_live_tup
SELECT relname, n_live_tup, n_dead_tup,
       round(n_dead_tup::numeric/NULLIF(n_live_tup,0)*100, 2) AS dead_pct,
       last_autovacuum, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC LIMIT 20;
```

### autovacuum 调
```bash
# postgresql.conf
autovacuum = on                          # 默认开，别关
autovacuum_max_workers = 6               # 并发 worker 数
autovacuum_naptime = '30s'               # 轮询间隔
# 触发阈值：dead = autovacuum_vacuum_scale_factor * 表行数 + autovacuum_vacuum_threshold
# 大表写多：单独设更激进
```
```sql
-- 单表设更激进的 autovacuum（写入大表）
ALTER TABLE events SET (
  autovacuum_vacuum_scale_factor = 0.05,    -- 5% 死元组就触发（默认 20%）
  autovacuum_analyze_scale_factor = 0.02,
  autovacuum_vacuum_cost_limit = 1000       -- 给这张表更多 cost 配额
);
-- 立刻手动 vacuum（不锁表）
VACUUM (ANALYZE) events;
-- VACUUM FULL 锁表+重建（生产慎用，改用 pg_repack 在线）
```

### xid wraparound（最严重的故障）
```sql
-- 距 wraparound 还有多远（age 接近 20 亿 = 危险，PG 会强制只读保护）
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0*age(datfrozenxid)/2e9, 2) AS pct_to_wrap
FROM pg_database ORDER BY xid_age DESC;
SELECT relname, age(relfrozenxid) FROM pg_class
WHERE relkind IN ('r','t','m') ORDER BY age(relfrozenxid) DESC LIMIT 10;
-- 日志出现 "not accepting commands to avoid wraparound data loss" → 立刻 VACUUM FREEZE 高 age 表
VACUUM FREEZE big_table;
```

---

## 连接池
### 连接数
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
-- max_connections 默认 100，每个连接 fork 一个进程，>500 性能急剧下降
SHOW max_connections;
-- 哪些应用连最多
SELECT datname, usename, application_name, count(*)
FROM pg_stat_activity GROUP BY 1,2,3 ORDER BY 4 DESC;
```

### idle in transaction（最危险，持锁 + 阻塞 vacuum）
```sql
SELECT pid, usename, application_name, state,
       now() - xact_start AS xact_duration,
       now() - state_change AS idle_duration,
       left(query, 100)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY xact_start;
-- 事务开着但应用没继续提交，长时间占锁/阻塞 vacuum
-- 配置：idle_in_transaction_session_timeout = '5min' 自动杀
```

### pgbouncer（连接池方案）
```ini
# pgbouncer.ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
pool_mode = transaction       ; transaction 模式：连接复用最强（多数场景选这个）
max_client_conn = 5000        ; 客户端连接上限
default_pool_size = 25        ; 每库/用户的后端连接数
reserve_pool_size = 5
server_idle_timeout = 600
```
```bash
# transaction 模式限制：不能用 prepared statement（除非 pgbouncer 1.21+ 配 max_prepared_statements）
# SET/RESET session 变量在 transaction 模式跨事务不保留
# 排查 pgbouncer 状态
psql -p 6432 -d pgbouncer -c 'SHOW POOLS;'
psql -p 6432 -d pgbouncer -c 'SHOW CLIENTS;'
psql -p 6432 -d pgbouncer -c 'SHOW STATS;'
```

---

## 高负载诊断
### pg_stat_activity（实时在跑啥）
```sql
SELECT pid, usename, application_name, client_addr,
       state, wait_event_type, wait_event,
       now() - query_start AS query_age,
       left(query, 80) AS q
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

### wait_events（等什么）
```sql
SELECT wait_event_type, wait_event, count(*)
FROM pg_stat_activity WHERE state='active'
GROUP BY 1,2 ORDER BY 3 DESC;
-- 常见组合：Lock/transactionid=行锁；Lock/relation=表锁
-- IO/DataFileRead=磁盘读慢；IO/BufFileWrite=work_mem 不够写临时文件
-- LWLock/buffer_content=热点页争用；Client/ClientRead=等应用读（正常）
```

---

## 备份 / 恢复
### 逻辑备份
```bash
pg_dump -h host -U user -Fc -d mydb -f mydb.dump          # 自定义压缩格式（推荐）
pg_dump -h host -U user -j 4 -Fd mydb -f mydb_dir/        # 并行 4 目录格式（大库快）
pg_dump -h host -U user -t users -t orders -d mydb -f p.dump   # 只备份部分表
pg_dumpall -h host -U user --roles-only -f roles.sql      # 备份所有角色
# 恢复
pg_restore -h host -U user -d newdb -Fc mydb.dump         # 恢复 .dump
pg_restore -j 4 -d newdb mydb_dir/                        # 并行恢复
pg_restore -t users -d newdb mydb.dump                    # 只恢复一张表
psql -h host -U user -d newdb -f mydb.sql                 # 恢复纯 SQL
```

### PITR（时间点恢复）
```bash
# 1. postgresql.conf 开 WAL 归档
archive_mode = on
archive_command = 'test ! -f /backup/wal/%f && cp %p /backup/wal/%f'
wal_level = replica
# 2. 物理基础备份（同时用于建从库 / 异地容灾）
#    主库先建复制角色：CREATE ROLE repl WITH REPLICATION LOGIN PASSWORD 'pwd';
pg_basebackup -h master -U repl -D /data -Fp -Xs -P -R     # -R 写 standby.signal+primary_conninfo
# 3. 恢复到指定时间点：data 目录放 recovery.signal（PG12+），postgresql.auto.conf:
restore_command = 'cp /backup/wal/%f %p'
recovery_target_time = '2024-06-15 14:30:00+08'
recovery_target_action = 'promote'                         # 恢复完提升为主
pg_ctl start
```

---

## 数据迁移
### 零停机：逻辑复制
```sql
-- 源库建发布，目标库建订阅（表结构需先存在）
CREATE PUBLICATION pub_all FOR ALL TABLES;                 -- 或 FOR TABLE users, orders
CREATE SUBSCRIPTION sub_all
  CONNECTION 'host=src user=repl password=pwd dbname=mydb' PUBLICATION pub_all;
SELECT * FROM pg_stat_subscription;                        -- 目标库看进度
SELECT * FROM pg_stat_replication;                         -- 源库看发送
-- 切换：① 停源库写入  ② 等 lag=0  ③ 校验数据  ④ 改 DNS  ⑤ 删订阅
```

### trigger（双写过渡期）
```sql
CREATE FUNCTION sync_to_new() RETURNS trigger AS $$
BEGIN
  INSERT INTO new_users(id,name) VALUES (NEW.id,NEW.name)
  ON CONFLICT(id) DO UPDATE SET name=NEW.name;
  IF TG_OP='DELETE' THEN DELETE FROM new_users WHERE id=OLD.id; END IF;
  RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_sync AFTER INSERT OR UPDATE OR DELETE ON users
  FOR EACH ROW EXECUTE FUNCTION sync_to_new();
-- 迁移完成后：DROP TRIGGER trg_sync ON users; DROP FUNCTION sync_to_new();
```

### 常见迁移套路
```sql
ALTER TABLE users ADD COLUMN status int NOT NULL DEFAULT 0;   -- PG 11+ 加列默认值秒级，不重写表
-- 改列类型大表会锁很久，分两步：加新列 → 分批 UPDATE → 删旧列 → 改名
UPDATE users SET new_id = old_id WHERE id BETWEEN 1 AND 1e6;  -- 按 id 分批
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);    -- 在线建索引不阻塞写；失败留 INVALID 要 DROP 后重建
ALTER TABLE users DROP COLUMN old_col;                        -- 元数据删，磁盘空间等 vacuum 回收
pg_repack -h host -U user -d mydb -t users                    -- 在线表重建（trigger+影子表）替代 VACUUM FULL 无长锁
```

---
*参考：本仓库 `notes/db-程序员视角-从慢SQL到原理.md`（慢查询/索引/MVCC 原理）、`github-repos/ddia/`（DDIA 中文版，第 5/6 章复制与分区）、`github-repos/references/REKCARC-TSC-UHT/`（数据库课程大作业）。PostgreSQL 官方手册 https://www.postgresql.org/docs/ 永远是第一手资料。*
