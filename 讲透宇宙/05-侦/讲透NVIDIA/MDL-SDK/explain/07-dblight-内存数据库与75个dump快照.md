# 07 · dblight：MDL SDK 的内存数据库与 75 张 dump 快照

## 1. 角色定位

`src/base/data/dblight/` 是 MDL SDK 自带的**轻量级内存数据库**（"DB light"）：实现 `base/data/db` 抽象层（`DB::Database`/`DB::Scope`/`DB::Transaction`/`DB::Info`）的完整契约，但砍掉完整 neuray 数据库的分布式能力——无跨主机通信、无换页（`set_memory_limits()` 直接忽略配置，dblight_database.h:143-145），状态恒为 `DB_OK`（dblight_database.h:147-149）。它是 API 层唯一 DB 后端：`src/api/api/mdl/mdl_neuray_impl.cpp:244` 在启动时以 `DBLIGHT::factory(...)` 建库——**用户装的每个 MDL SDK 都在跑这套数据库**。工厂入口在 `i_dblight.h:58`。库本体四件套 database/scope/transaction/info.cpp（517/553/1850/2114 行）；`test.cpp`(4865 行) 是回归主战场与本篇另一半主角。

## 2. 内部结构

**Database_impl**（dblight_database.h:100）是门面，聚合三大 manager（dblight_database.h:174-186）：**Scope_manager** 管 privacy level 树（子 scope level 须严格高于父，dblight_scope.h:317-329）；**Transaction_manager** 管单调事务 ID 与序列号；**Info_manager** 管版本链。核心是 **Info_impl**（dblight_info.h:106）：每个元素版本是一条 Info，以 `(scope_id, transaction_id, version)` 三元组字典序定序（dblight_info.h:71-102）。它**同时挂在三个 intrusive 容器**上——name set / tag set（bi::set，dblight_info.h:219-221）与 scope list（bi::list，dblight_info.h:223），一次插入换三条索引、零额外分配。成员几乎全 const，注释枚举仅有的六个可变成员（dblight_info.h:226-233）。可见性靠 `State_and_visibility_ptr`（dblight_info.h:267-271）：指向创建事务状态，指针失效即全局可见。`m_references` 是 `get_references()` 的缓存（dblight_info.h:258-265）。pin 语义特殊：`unpin()` 减到零**不触发析构**（dblight_info.h:148-149），回收交给 `m_gc_candidates_pin_count_zero`（dblight_info.h:947）与 `cleanup_tag_with_pin_count_zero()`（dblight_info.h:815-825）。

`test.cpp` 的测试桩同样结构化：`My_element`（test.cpp:90，类 ID `0x4d79656c`="Myel"）持 int 值 + Tag_set；`My_job`（test.cpp:121）的 `execute()`（test.cpp:155-163）演示惰性求值；`My_parent_job`（test.cpp:198）在 execute 里**再 store 子 job**（test.cpp:232-243）测嵌套调度；`My_failing_job`（test.cpp:254）execute 返回 nullptr 测失败路径；`My_transaction_listener`（test.cpp:392）把事务事件序列写进流供断言。

## 3. 外部连接

- **上游抽象**：六个 `i_db_*.h` 纯虚接口（test.cpp:58-66），dblight 是 SDK 内唯一实现。
- **基础设施注入**：`THREAD_POOL::Thread_pool` 与 `SERIAL::Deserialization_manager` 可注入或自建（dblight_database.h:288-297）；API 层注入共享线程池（mdl_neuray_impl.cpp:240-244）。第三方依赖 boost::intrusive（dblight_info.h:40-45）。
- **调度器**：`SCHED::Job<>` CRTP 模板（test.cpp:121/198/254/271）；job 存库、首次 access 执行——`Job_transaction` 为此重载 store，其 `commit()`/`abort()` 直接 `MI_ASSERT(!"must not be invoked")`（dblight_transaction.cpp:1824-1832）。
- **测试框架**：auto suite（test.cpp:31-38），`MI_TEST_AUTO_FUNCTION(test_dblight)`（test.cpp:4825）串约 90 个场景（test.cpp:4783-4822）；可选 admin server HTTP 巡检（dblight_database.h:366-369）。

## 4. 数据流

一次 store→commit 旅程：

1. `Test_db` 构造（test.cpp:528-542）：factory 建库 → static_cast 拿 impl → 注册五个测试类。
2. `Transaction_impl::store()`（dblight_transaction.cpp:451）：先 `allocate_tag()`（原子自增 `m_next_tag`，dblight_database.h:359），再入 `store_element_internal()`（dblight_transaction.cpp:607）。
3. 内部建 `Info_impl`（pin=1，dblight_info.h:104-105）三挂进容器，`increment_pin_counts(references)`（dblight_info.h:848）给被引用元素记账；dump 显示 `visibility ID = (current transaction only)`。
4. `commit()` → `end_transaction(true)`（dblight_transaction.cpp:81-86）→ 状态转 COMMITTED、state_and_visibility 释放，dump 文本变 `(globally visible)`；abort 路径清理该事务创建的 infos（`test_gc_simple_reference_abort.dump.txt` 固化差异）。
5. `edit_element()`/`finish_edit()`（dblight_transaction.cpp:406）在同 tag 下追加新 version Info 形成版本链，GC 延迟回收旧版本（`test_gc_delayed.dump.txt`）。

**dump 快照流**：`Test_db::dump()`（test.cpp:538-543）把 `m_db_impl->dump(m_dump, verbose, mask_pointer_values=true)` 追加进内存流并打 stderr；`Database_impl::dump()`（dblight_database.cpp:464-470）持共享锁依次调三个 manager 的 dump，指针值默认掩码保证可复现。析构时 `export_dumps_and_compare()`（test.cpp:546-600）：写 `data/<name>.dump.txt` → initial tag/transaction id 非默认则跳过对比（test.cpp:559-568，这正是 factory 可配初值的用意）→ 从 `mi_src_path("base/data/dblight/data")`（test.cpp:571）读参考 → `compare_files()` 逐行比（test.cpp:582）。失败路径硬核：非 Windows 直接 `system("diff -u ...")` 打全量 diff（test.cpp:597-600），再打出 **approval command** `cp 输出 参考`（test.cpp:605-607），然后 `abort()`。`data/` 下 75 个 `*.dump.txt` 即 75 次人工"审批"后的黄金标准，覆盖 store 多版本、scope 增删、GC、journal、双事务可见性等状态机转移。

## 5. 设计决策

- **三元组定序替代时间戳**：(scope, transaction, version) 字典序天然给出版本全序，代价是头文件明写的三个 2^32 环回限制（dblight_database.h:92-99），"够用就好"的边界工程。
- **intrusive 多索引**：一条 Info 进三容器省三份分配，代价是 Info_impl 须预埋 hook、不可变成员换线程推理安全（dblight_info.h:226-233）。
- **dump 即规格**：不断言拼状态，而是全库序列化成文本与人审快照对比，diff 自解释；代价是格式变动须重审批 75 文件。
- **隐私级检查默认只 debug 开**：`#ifdef NDEBUG` 分支（dblight_database.h:317-321），注释直言"理想应常开，但性能影响不明"。
- **journal 默认关**（i_dblight.h:53-54；上限 1000 万条，dblight_database.h:333），只为 6 个测试场景存在。
- **统计跨实例共享**（i_dblight.h:46-47）：实例独立、计数器全局，测试可并行而指标不打架。

## 6. 新人提示

- 读码顺序：i_dblight.h(69 行) → dblight_database.h → dblight_info.h 的 Info_impl 段(67-330) → test.cpp 的 Test_db(453-620) → dblight_transaction.cpp。懂 Info 三挂结构后其余顺很多。
- **改 dump 格式 = 75 文件重审批**。动 `Info_manager::dump()`（dblight_info.cpp:1348）会连环 abort；approval 的 cp 方向是"输出 → 参考"，别反了污染基线。diff 输出在 Windows 上被关掉（test.cpp:596），只见 abort 不见 diff。
- 别对 `Job_transaction` 调 commit/abort——assert 直接崩（dblight_transaction.cpp:1824-1832）；job 结果生命周期跟着 `DB::Access` 走。
- `unpin()` 减到零不释放（dblight_info.h:148-149）；排查"内存不降"先看 pin count 与 `cleanup_tag_with_pin_count_zero()`（dblight_info.h:815）。新元素类型记得在 Test_db 构造里 `register_class`（test.cpp:535-541），漏注册会在序列化检查路径炸出怪错。
