# abs_result_set.cpp 精讲 — 结果集抽象基类与三形态骨架

> `frameworks/native/rdb/src/abs_result_set.cpp`（659 行）+ `interfaces/inner_api/rdb/include/abs_result_set.h`；配对三形态 `step_result_set.cpp` / `sqlite_shared_result_set.cpp`+`abs_shared_result_set.cpp`+`share_block.cpp` / `cache_result_set.cpp`

## 1. 角色定位

rdb-kernel 与 inner_api 交界处的模板方法基类。一次 query 返回的数据怎么被消费——逐行游标、共享内存窗口、内存快照，三种形态差异巨大，但对外必须呈现同一个 `ResultSet` 接口（游标移动/取列/取值/关闭）。本文件把"与存储无关的部分"全部前置实现：游标位置状态机、列名元数据缓存、类型化取值与类型校验、整行/批量读取；只留四个原语（`Get`/`GetColumnNames`/`GoToRow`/`GetColumnType`）给子类。它存在的原因：让 StepResultSet 等"每值都碰 SQLite"的实现与 CacheResultSet 等"纯内存"实现共享同一套导航与元数据语义，上层绑定（napi/taihe/NDK）零感知。

## 2. 内部结构

继承链：`ResultSet`（inner_api 纯接口）→ `AbsResultSet`（本文件，头文件 :34）→ 三分支：`StepResultSet`（step_result_set.cpp 直接继承）、`AbsSharedResultSet`（abs_shared_result_set.cpp:37，多继承 `SharedResultSet`）→ `SqliteSharedResultSet`、`CacheResultSet`（直接继承）。另有 `RowEntity`（L54-101）：`map<string,ValueObject> values_` + `vector<map::iterator> indexs_` 双结构，名字索引与列序索引兼得。

方法五组：①列元数据——`InitColumnNames`(L159，懒加载+globalMtx_ 双检，`columnMap_` 用 string_view 键指向 `wholeColumnNames_` 保证生命周期)、`GetAllColumnNames`(L139 按列序回填)、`GetColumnIndex`(L515：精确匹配失败后剥表前缀 `xxx.`+忽略大小写重试)、`GetColumnCount/GetColumnName`；②类型化取值——`GetBlob/GetString/GetInt/GetLong/GetDouble`(L198-276) 全部转调虚函数 `Get` 再验型，TYPE_ASSETS/ASSET/BIGINT/VECS 一律 E_INVALID_OBJECT_TYPE；扩展型 `GetAsset/GetAssets/GetFloat32Array`(L593-653)；③行级读取——`GetRow`(L293 出 RowEntity)、`GetRowData`(L317 出有序 vector)、`GetRowsData`(L349 按 position+maxCount 批量，E_ROW_OUT_RANGE 视为自然结束)；④导航——`GoTo/GoToFirstRow/GoToNextRow/GoToPreviousRow` 全部归约到 `GoToRow(rowPos_±n)`（L406-456），`IsEnded`(L482)=`rowPos_==rowCount_`，rowPos_ 语义 [-1 起始, n 结束]；⑤生命周期——`Close`(L581) 清 columnMap_/重置 rowPos_/rowCount_。线程安全是可选的：`Lock<Mtx>` 模板（头文件 L321-351），`AbsResultSet()` 默认不分配互斥量，`AbsResultSet(true)` 才有——AbsSharedResultSet 与 TransDB 里的 StepResultSet（trans_db.cpp:239 传 true）用安全态，RdbStoreImpl 普通查询（rdb_store_impl.cpp:1986）用无锁态。

## 3. 外部连接

依赖（图谱 imports 边）：`result_set.h`、`value_object.h`、`sqlite_utils.h`（Anonymous 脱敏+列名清洗 REP）、`rdb_errno.h`、`rdb_trace.h`、`logger.h`。被依赖（grep 实证）：`step_result_set.h`、`cache_result_set.cpp`、`abs_shared_result_set.h`、`iresult_set.h` 四处直接包含。再往上：`RdbStoreImpl::QuerySql`(rdb_store_impl.cpp:1966) 造 SqliteSharedResultSet、`QueryByStep`(:1986) 造 StepResultSet、Returning 结果造 CacheResultSet(:3598)；`TransDB::QuerySql/QueryByStep`(trans_db.cpp:227/239) 在事务内造后两形态；云共享链路 js_cloud_share.cpp:93 与 taihe cloud_data 也产 CacheResultSet。共享块侧依赖 AppDataFwk::SharedBlock（app_data_fwk 部件，ashmem 窗口），share_block.cpp 提供 Def*（直填块）与 Seri*（序列化）两套回调。

## 4. 数据流

一次 QueryByStep 的完整流转：`pool->AcquireRef(true)` 借读连接→StepResultSet 构造：`PrepareStep`(step_result_set.cpp:84) 建 statement、`ReadOnly()` 校验必须是 SELECT、Bind 参数；`options.preCount` 为真则 `statement->Count()`（sqlite_statement.cpp:385，isCountAllRows 空走全表只计数不物化）填 rowCount_。消费期 `GoToNextRow`→`statement->Step()`，遇 E_SQLITE_BUSY/LOCKED 重试 50 次×1ms（:236-250，超限报 E_STEP_RESULT_QUERY_EXCEEDED）；`Get(col,value)`→`GetValueObject`(:379)→`statement->GetColumn`。`Close()`(:277) 释放 conn_ 与 statement_，连接经 deleter 归还连接池。共享形态：构造时同样 Count，块在 `GetBlock`（abs_shared_result_set.cpp:64）懒建（DEFAULT_BLOCK_SIZE 2MB，低内存置 lowMem_ 降级返回 nullptr）；`GoToRow`→`UpdateBlockPos`→虚 `OnGo`（SqliteSharedResultSet :156）判断目标行是否在窗口 [startPos,lastPos) 内，不在则 `FillBlock`：`PickFillBlockStartPosition`(:193) 取 `pos-容量/3` 为窗口起点，`ExecuteForSharedBlock`(:244) 让 statement 把该窗数据写进块，之后取值直接读块内 CellUnit，连接只在窗口未命中时被触碰。缓存形态：从 `vector<ValuesBucket>` 构造（cache_result_set.cpp:31，用首行建 colNames_/colTypes_），自带 shared_mutex，全程不碰连接。

## 5. 设计决策

三形态取舍是本类的存在理由：**StepResultSet** 零物化、内存最小，但后退要 Reset 重走（GoToRow :203）、未 preCount 时 GetRowCount 会踏遍全表（:294 先存旧位置再恢复）、持有连接直到 Close；**SqliteSharedResultSet** 窗口物化换来窗口内随机访问与可共享/可序列化的数据块（跨进程 IPC 场景），2MB 上界+低内存降级；**CacheResultSet** 与连接彻底解耦，适合 RETURNING 回传值和云端数据——连接已释放结果仍可用。基类侧的关键选择：模板方法模式把差异压缩到 4 个原语；rowPos_/rowCount_ 统一状态机让三种游标语义一致；可选锁省掉单线程场景的互斥开销；`GetColumnIndex` 的模糊匹配（剥前缀+忽略大小写）对齐用户写 `t.name` 的直觉。

## 6. 新人提示

- 切入点：先读本文件 `GoToRow/GoToNextRow/InitColumnNames` 三个骨架，再对照 step_result_set.cpp 的 4 个原语实现，最后看 abs_shared_result_set.cpp 的窗口逻辑。
- 易错点：①StepResultSet 不 Close 就长期占一条池连接，并发场景直接连接饥饿；②事务 QueryByStep 的结果集在事务收尾被强制 Close，先消费后 Commit；③preCount=false 时 GetRowCount 有全表遍历副作用；④GetColumnIndex 大小写不敏感可能命中非预期列；⑤columnMap_ 键是 string_view，勿在 Close 后再访问列名（析构顺序注释见 L113）。
- 测试：`rdb_step_result_set_test.cpp`、`rdb_sqlite_shared_result_set_test.cpp`、`cache_result_set_test.cpp`、`rdb_transaction_query_without_rowCount_test.cpp`，fuzz 见 `absresultset_fuzzer`/`abssharedresultset_fuzzer`/`cacheresultset_fuzzer`。
