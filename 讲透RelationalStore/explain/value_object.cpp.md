# value_object.cpp — ValueObject 列值对象

> `frameworks/native/rdb/src/value_object.cpp`（405 行；声明 `interfaces/inner_api/rdb/include/value_object.h`，对内公开 API）

## 1. 角色定位

属 **rdb-kernel 层**，整个 RDB 栈唯一的"单元格值"表示：`ValuesBucket` 行值（`values_bucket.h` L42 `map<string, ValueObject>`）、SQL 绑定参数、结果集取列、谓词 bindArgs、云同步资产列全部收敛到它；NAPI/Taihe/NDK 出口的值最终都落到它。存在原因：SQLite 动态类型——同列值类型随行而变，需要一个能表达 NULL/INT/REAL/TEXT/BLOB 加扩展型（Asset/Assets/FloatVector/BigInt）的值语义类型，还要能拷贝移动、能全序比较、能 IPC 序列化。405 行无业务逻辑，纯"判别+取值+转换+序"基础设施。

## 2. 内部结构

核心 `Type = std::variant<Nil, int64_t, double, std::string, bool, Blob, Asset, Assets, FloatVector, BigInt>`（h L47；`Nil=monostate`、`Blob=vector<uint8_t>`、`Asset=AssetValue`、`BigInt=BigInteger`），公开成员 `value`（L107）。TypeId 枚举（L83-106）非手写：`index_of` 元编程（L48-78）编译期从 variant 顺序推导 `TYPE_INDEX<T>`，加型自动重编号；`DECLARE_TYPES[TYPE_BUTT]`（L391-412）给 "INT"/"REAL"…"UNLIMITED INT" SQL 风格名。方法五组：

- **构造**（L57-102）：`int` 加宽 int64_t（L57）；`const char*` 判空（L77 nullptr→空串+WARN）；Asset 族移动构造；赋值带自赋值检查（L104-120）。
- **类型判别**：`GetType`（L122）= `value.index()`，O(1)。
- **严格取值**：私有模板 `Get<T>`（L340-349）`std::get_if` 精确匹配否则 `E_INVALID_OBJECT_TYPE`；`GetInt`（L127）委托 `GetLong` 后无条件窄化；`GetString`（L150-174）唯一宽容派：string 直取，失败依次降级 double→int64→bool 的 `std::to_string`。
- **宽松转换 operator**：`int64_t`（L196，覆盖 INT/DOUBLE/BOOL/STRING，字符串 `strtoll` base 0、空串得 0）；`double` L213；`bool` L230（字符串仅 `"0"` 为假）；`std::string` L263 配静态 `GetPrecision`（L247，`max_digits10` 内逐位探最短小数位）fixed 序列化，杜绝 3.1400000000000001；`Blob` L286 兼容 STRING 字节拷贝。Asset/Assets/FloatVector/BigInt 四 operator（L299-333）严格 `get_if` 不匹配返空。
- **全序**：`operator<`（L351-393）异型按类型索引定序、同型按各语义比较，switch 穷举十型；`==`/`!=`（L395/400）由 `<` 双向推导。

## 3. 外部连接

依赖：`asset_value.h`（AssetValue：name/uri/createTime/modifyTime/size/path + `Status` 状态机 STATUS_INSERT/UPDATE/DELETE/DOWNLOADING）、`big_integer.h`、`rdb_errno.h`。被依赖（grep 实证）：①`sqlite_statement.cpp`——`ACTIONS[TYPE_MAX]` 跳表（`sqlite_statement.h` L87-88）以 `value.index()` 下标分发（cpp L265），前置 `CheckValueObjectValid`（L282）拦 `valueless_by_exception`；②`rdb_sql_utils.cpp` `GetInsertSqlInfo`（L180）/`GetUpdateSqlInfo`（L222）——前者对资产值 `UpdateAssetStatus(STATUS_INSERT)`（sqlite_sql_builder.cpp L328，经 `Traits::get_if` 原地改写），`TYPE_ASSETS`+`ON_CONFLICT_REPLACE` 拒 `E_INVALID_ARGS`（L203）；后者把资产列改写 `merge_asset(col,?)`/`merge_assets(col,?)`（L249-255），UDF 注册于 `SqliteFunctionRegistry`（`sqlite_default_function.h` L45-46）；③读回侧 `step_result_set.cpp` `GetValueObject`（L379）按 sqlite3_column_* 重建并校验类型（L393）；④`shared_block_serializer_info`/`cache_block`/`transaction` 等。图谱边：imports logger/sqlite_utils/rdb_errno/value_object.h，contains GetString/GetPrecision/operator<。

## 4. 数据流：insert(values) 的类型流转

设 `insert("T", {name:"a", age:30, avatar:asset})`：
1) `ValuesBucket::PutString/PutLong` 各自构造 ValueObject（int widening、string move）存入 `values_`。
2) `RdbStoreImpl::Insert`（rdb_store_impl.cpp L1755）→ `RdbSqlUtils::GetInsertSqlInfo` 拼占位符 SQL，逐列拷贝进 bindArgs；avatar 是 TYPE_ASSET → status 改写 STATUS_INSERT 标记待上传。
3) `SqliteStatement::Bind`（sqlite_statement.cpp L344）：参数不足用默认构造 ValueObject（TYPE_NULL）补齐，超数报 `E_INVALID_BIND_ARGS_COUNT`；`BindArgs`（L250）逐个校验后 `ACTIONS[value.index()]` 分发：int64→`sqlite3_bind_int64`（L816）、bool→1/0（L843）、空 Blob→`sqlite3_bind_zeroblob`（L859）、**Asset/Assets/FloatVector/BigInt 经 `RawDataParser::PackageRawData` 打包成 blob**（L865-905）——扩展类型压扁成 SQLite 原生五型的关键变换。
4) 读回：`StepResultSet::Get`（L338）按列类型重建 ValueObject，期望类型不符报 `E_INVALID_COLUMN_TYPE`（L393）。

## 5. 设计决策

- **variant 而非 OOP 继承**：①值语义——拷贝/移动天然正确，无虚表、内联存 tag；②`index()` 判别 + 跳表分发是编译器可查漏的穷举，继承做"值"既重又给不出全序；③`operator<` 使其能进 `std::map`、能排序去重（分布式变更集按主键值比较需要）；④贴合 SQLite 动态类型模型。
- **双访问风格分层**：`Get*`（严格、错误码）给内核路径；`operator T`（宽松、静默默认值）给应用便利（GetString 降级链 L150-174）。混用是 bug 之源。
- **Asset/Assets 附件引用设计**：行内存资产描述符（uri/path/size/时间戳/状态）而非文件字节，BindAsset 打包 blob；更新经 `merge_asset` UDF 按 Status 状态机与旧行合并——附件本体驻留文件/资产服务，行里只旅行元数据，云同步按需拉取，即"引用而非值存储"。
- **TypeId 编译期推导** + DECLARE_TYPES 定长数组：加型必须同时补名字否则编译失败，防枚举漂移。
- **GetPrecision 最短小数位格式化**：REAL→TEXT 保真不冗余，服务跨设备同步的字符串一致归一。

## 6. 新人提示

- **切入点**：h 的 variant 定义与 TypeId 推导（L47-106）→ cpp 的 `Get<T>`（L340）与 `operator int64_t`（L196）两族对照 → `sqlite_statement.cpp` 跳表（L265/L811-905）看类型落到 `sqlite3_bind_*`。
- **易错点**：①**类型判别 switch 漏分支是头号坑**——`operator int64_t`（L196）对 BLOB/ASSET 等未列类型静默返 0；加 variant 型必须审计本 cpp 全部 6 处 switch/if 链；②bool 转换字符串只认 `"0"`（L242），`"0.0"`/`"false"` 为真；③`GetInt` 窄化（L129）无范围检查；④空串转数值为 0（L208）；⑤`==` 先比类型索引，`"1"` 与 `1` 不等；⑥asset status 被 `UpdateAssetStatus` 原地改写，复用同一 ValuesBucket 二次插入时状态已是 INSERT。
- **测试**：`rdb_step_result_set_test.cpp`、`rdb_store_impl_test.cpp`（值类型端到端）；`raw_data_parser_test.cpp` 专测 Asset/FloatVector/BigInt 打包；资产 merge 语义看 `rdb_distributed_test.cpp`。
