# explain-12 · 单元测试夹具体系：tests/unit/test_ff_config.c（cmocka + fixture 契约）

## 角色定位

test_ff_config.c（3394 行、103 个注册用例）是全测试体系最大的一块，也是"夹具即契约"哲学的样板：58 个 fixtures/*.ini 文件（valid_* 33 + invalid_* 25）逐一对应 ff_config.c 的一条解析分支或校验规则——invalid_drain_ring_size_pow2.ini 的注释直说理由（"非 2 的幂必须拒绝——rte_ring 会静默向上取整"）。测试对象是配置装载全链 ff_load_config（头注释 `:10` 说明为何端到端：所有 _handler 都是 static，只能经公共入口传递性覆盖）。它同时是夹具体系的"用法教材"：fatal 函数 wrap、OOM 注入、fork 判活桩、valgrind 防泄漏 setup——其他 14 个 test_ff_*.c 复用同一套模式。

## 内部结构

骨架三件：① test_setup（`:125-133`）每个用例前跑 ff_unload_config + memset 归零——注释记载这修掉了"19 个 TC 间渗漏 ~50KB"的 valgrind 伤（Stage-6 Phase-8 编号），load_with_fixture（`:136-153`）组装 "f-stack -c <fixture>" 的 argv 并重置 optind（getopt 状态污染是 R-S2-3 钉过的坑）；② 用例体：valid 路径断言 ff_global_cfg 字段直值（minimal 用例 `:160-180` 逐项核 lcore_mask=="1"、channel==4、pkt_tx_delay==100），invalid 路径断言返回非零+部分填充状态（lcore_mask 用例 `:232-243` 断言 rv!=0 但 lcore_mask 已被写入 "ZZZ_NOT_HEX"——**装了一半也要如实暴露**）；③ main（`:3266-3394`）103 个 cmocka_unit_test_setup_teardown 注册，注释按 Stage/Phase 分层（Stage-3/6/7/8 覆盖率扩展的考古地层都在）。三类特型用例：isolated 系（test_vlan_cfg_handler_isolated 等，直接调 static handler 的进阶玩法）、OOM 系（FU-S8-CFG-OOM：__wrap_calloc `:62` 传透 __real_calloc，armed 后第 N 次分配返回 NULL，专打 `if (X==NULL)` 分支——头注释强调 cmocka 自己的分配只在 disarmed 时发生）、M5 系（`:2318` 起：fork 一个子进程 waitpid 收尸后把 pid 塞进 slot 当"已死 master"，验证世代目录判活的 fresh-stamp/死 pid 两维）。

## 外部连接

被测物：lib/ff_config.c（explain-04）+ ff_reload.h 的目录仲裁函数（M5 用例借 ff_reload_peer_coord 验证 USR2 死代识别）。桩基建在 tests/unit/common/：rte_stub.c 的 __wrap_rte_exit/__wrap_rte_panic（`:22-45`）把 DPDK 的致命退出重定向成 mock_assert(0) → cmocka longjmp 回 runner——**致命路径变成可断言的失败**而不是杀掉整个测试进程；ff_log_stub 供日志类测试。链接层：Makefile:44 `BASE_WRAPS := -Wl,--wrap=rte_exit -Wl,--wrap=rte_panic` 全局生效，test_ff_log 额外加 4 个 rte_log wrap（`:49-52`）；P0 分层（Makefile:56 test_p0 目标：ini_parser/log/callout 三件套最先跑）。旁支：tests/integration/ 起真 EAL 测 dpdk_if/KNI/gendir，test_reload_harness.py 与 test_graceful_reload.sh 是热升级真机 harness——单测管"每块砖"，集测管"整面墙"。

## 数据流

一个典型 invalid 用例的数据流：fixtures/invalid_greload_hb_small.ini（注释标 UT-NR-20/22：reload_heartbeat_timeout_ms=5 低于 >=10 的下限）→load_with_texture 构 argv→ff_load_config：默认值→INI 解析（这里 hb=5 被原样读入，ff_config.c:1047 只拦 <=0）→ff_check_config 的下限校验拒绝→rv=-1→用例 assert_int_not_equal(rv,0) + 检查失败路径没留脏状态。fixture 文件本身就是文档：每份头部注释带编号（UT-NR-xx / M2 Batch B / C-NR-305）反查需求规格（docs/unit_test_spec）。valid_greload_hb_negative.ini 则验证负数被重映射默认值（对应 ff_config.c:1053 的防御，explain-04 讲过）——同一配置键一正一反两份夹具，边界即契约。

## 设计决策

① **fixture 文件而非内联字符串**：配置解析的输入天然是文件（ini_parse 只吃路径），58 份夹具让"配置契约"脱离测试代码可独立审阅——改 ff_config.c 的人跑一遍就知道踩了哪条契约；代价是夹具与断言分离，读测试要两头看。② "接受 0 或 -1"的宽容断言策略（头注释 `:20-23`）：ff_load_config 可能因下游校验（port addr 缺失）返回 -1 但解析器部分已正确填充——用例直接断言 ff_global_cfg 状态而非纠结返回值，**测的是组件行为不是函数签名**。③ rte_exit/rte_panic 全局 wrap 是"致命即失败"原则的落地：lib 代码在错误路径大量 rte_exit（如 ff_kni_alloc 的 panic），单测进程绝不能真退出；mock_assert 的 longjmp 语义与 cmocka 天作之合。④ OOM 注入用 --wrap=calloc 而非 LD_PRELOAD 或 fork rlimit：精确到"第 N 次分配失败"，能把纵深错误路径（每个 if (NULL) 一条）逐条点亮，覆盖率报告（run_full_coverage.sh 三阶段合并）因此可信。

## 新人提示

跑法：tests/unit 下 make test（全量 sanity+P0~P3 分层）或 make test_p0；单文件 cc -MD 起的依赖链别手改 Makefile。加新配置键的完整动作三件套：ff_config.c 的 handler+default+check、fixtures 加一正一反两份（命名 valid_/invalid_ 前缀 + 语义后缀）、test_ff_config.c 加用例并注册进 main 的数组——漏任何一件，coverage_threshold.sh 的门槛会拦你。读 M5 用例先看 ff_reload.h 的 slot 语义（FF_RELOAD_SLOT_LIVE/DEAD、pad 当毫秒时间戳），fork+waitpid 的"死 pid"技巧在 valgrind 下无告警。误报排查顺序：先看是不是 optind 未重置（老坑复发）、再查 ff_unload_config 是否被跳过（跨用例渗漏）、最后才怀疑被测代码。tests/README.md 的分层表（P0~P3）与 docs/unit_test_spec/ 的用例编号是两份索引，改夹具注释时保持编号可反查。
