# rdb_perfStat.cpp 精讲 — RDB SQL 执行耗时观测打点器

`frameworks/native/rdb/src/rdb_perfStat.cpp`（配 `include/rdb_perfStat.h`，2025 年新增，267 行）。

## 1. 角色定位

rdb-kernel 层的横切观测设施：不含数据库功能，只回答"这条 SQL 花在哪了"。四段拆分——拿连接排队（waitTime_）、编译（prepareTime_）、执行（executeTime_）、端到端（totalTime_），载体 `SqlObserver::SqlExecutionInfo`（`rdb_types.h:515`）。

它是 2024 年 `rdb_sql_statistic.cpp` 的升级版：新增按 storeId 订阅（实传 `config_.GetPath()`）、Pause 抑制、事务 seqId 聚合，两轨并存（`sqlite_statement.cpp:66-67` 双打）。

**勘误钉版**：本模块不直接调 HiSysEvent/HiTrace，出口是进程内 `OnStatistic` 回调（订阅方为 JS 应用）；HiSysEvent 属姊妹模块 `frameworks/native/dfx/`（fault/radar/stat 三类 reporter），HiTrace 属 `rdb/include/hitrace.h:25` RAII 封装（`RDB_TRACE_ON` 编译期启用）。

## 2. 内部结构

单类全静态（L31-36）：`observers_`（storeId→observer 集合）、`execInfos_`（uint64_t→SqlExecInfo）、`threadParams_`（tid→抑制计数与行数）、`enabled_`、原子 `seqId_`。方法四组：

- **订阅**：`Subscribe`(L37) 插入并置 `enabled_=true`；`Unsubscribe`(L47) 全空时关开关、清两 map(L53)。
- **RAII 采集**：构造(L67)记 `steady_clock` 时点，按 9 态 Step（`rdb_perfStat.h:37-48`）绑定或新建 SqlExecInfo；析构(L109)把微秒 interval 按 step 累加到对应字段(L119-150)并 erase 聚合键。
- **完成处理**：`GetRelease`(L153) 是点睛——SqlExecInfo 挂自定义 deleter：普通调用挂 `Notify`(L189)、事务挂 `Merge`(L169)，上报时机由引用归零决定。
- **辅助**：`Pause/Resume`(L217/222)；`FormatSql`(L228) 按 `"),("` 首现折叠批量 VALUES 为 `...,N`。

## 3. 外部连接

知识图谱 imports 边实证。**依赖**：`rdb_types.h`（SqlObserver）、`task_executor.h`、`rdb_platform.h`、`concurrent_map.h`。

**打点源**（5 文件）：
- `connection_pool.cpp:335/351/434` — `Acquire_connection` 等打 STEP_WAIT（连接池排队）；
- `sqlite_statement.cpp:67/73`（TOTAL_REF/RES）、`156`（PREPARE 带 SQL）、`416/781`（EXECUTE）；
- `rdb_store_impl.cpp` — `Insert`(1763)、`ExecuteSql`(2054)、`CreateTransaction`(3512) 等 API 入口打 STEP_TOTAL；
- `transaction_impl.cpp:38/46/109/137`（TRANS_START/END）、`199-308`（TRANS 带 seqId_）；`suspender.cpp:25` 的 `Suspender(SQL_STATISTIC)` 构造即 `Pause()`，抑制内部 SQL 自扰。

**消费端**：`napi_rdb_store.cpp:1456` `OnPerfStat` → `NapiPerfStatObserver`（UvQueue 回 JS）；Taihe `taihe_sql_observer.cpp:70`。`OnStatistics`(1411) 订阅的是旧 SqlStatistic。

## 4. 数据流

以 `ExecuteSql`（rdb_store_impl.cpp:2042）为例：

1. L2054 栈上 `PerfStat(path,"",STEP_TOTAL)`：`enabled_`/`IsPaused` 检查(L69)→ `observers_.Find(storeId)` 命中才干活(L72)→ 新建 SqlExecInfo 以 threadId 为键入 map，deleter=Notify；
2. `Acquire_connection`(351) 打 STEP_WAIT，析构 `waitTime_ +=`(L121)——与外层 Find(threadId) 是同一 info，天然聚合；
3. `Prepare`(156)：statement 的 seqId_ 查 miss 后回退 Find(threadId)(L91-94) 挂同一 info，FormatSql 落 SQL；`Execute`(416) 累加 executeTime_；
4. 外层 ~PerfStat(L129)：totalTime_ 累加、Erase(threadId)→引用归零→`Notify`(L189)：sql 为空丢弃；否则投 `TaskExecutor` 后台线程(L198) 调 `OnStatistic`(L211)——不在用户线程上报，JS 侧经 UvQueue 送达应用回调；
5. **事务变体**：TransactionImpl ctor(38) 把 `GenerateId()` 的 seqId 绑到外层 info(L96-98)；事务内语句在 worker 线程各自 STEP_TRANS 建临时 info，析构经 `Merge`(L169) 汇入 `execInfos_[seqId]`(L178)；TRANS_END 抹聚合键，由外层 Notify 一次上报整个事务。

## 5. 设计决策

- **独立模块而非内联**：9 态 × 5 埋点文件，内联则每处都要管 map/锁/生命周期；业务一行 `PerfStat perfStat(path,"",Step)` 即埋点，语义集中演进。
- **deleter 驱动完成回调**：map、栈对象、事务聚合条目各持引用，嵌套/跨线程不漏报不重报，重活推到最后释放。
- **开销控制**：三层闸门（enabled_ 短路 L69 → store 级 Find L72 → Pause 计数）+ 异步 Notify + 单调钟；无订阅者时只多一次 bool 读。
- **粒度取舍**：四段覆盖三大瓶颈（池竞争/编译/执行）；seqId==0 用 threadId、事务用原子序号(L62)。

## 6. 新人提示

- **切入**：`rdb_types.h:513` → Step 枚举 → 构造/析构分支 → `GetRelease/Notify/Merge` 三角。警惕 deleter 里裸 `delete execInfo`(L186/215) 与 map 中 shared_ptr 并存；L131 有 `[[fallthrough]]`。
- **排查慢查询**：订阅后按四段归因——waitTime 高=连接池竞争；prepareTime 高=未走缓存或超长 SQL；executeTime 高=索引缺失，拿 sql_ 去 `EXPLAIN QUERY PLAN`。
- **测试**：`rdb_perfStat_test.cpp`（unittest/rdb_error_log_test 下，`BlockData<bool>` 同步等异步 Notify，L112）。
- Subscribe 首参虽叫 storeId，实传的是数据库文件路径。
