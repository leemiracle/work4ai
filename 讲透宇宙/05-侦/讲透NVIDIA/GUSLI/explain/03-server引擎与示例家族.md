# 03 · server 引擎与示例家族：srvr_imp、故障注入与 SPDK 集成

> 文件：`gusli_server_api.hpp`（69 行）、`03backend/server_imp.hpp/.cpp`（99/404 行）、`07examples/`、`unitest/`、`80scripts/`；图谱 L07+L08+L09

## 角色定位

server 侧把后端抽象到极致：实现 srvr_backend_bdev_api 三个纯虚函数（open1/close1/exec_io，gusli_server_api.hpp:53-55）即可，其余交给引擎。srvr_imp 是引擎本体（单线程消息泵+每 IO 一个 executor 对象）；07examples 给 RAM/故障/只读/SPDK 四类参考后端；unitest+80scripts 构成验证闭环。README.md:104 明言：**server 单线程是有意设计**（每 bdev 一核），多 bdev 横向扩展。

## 内部结构

**三纯虚契约**（gusli_server_api.hpp）：backend_io_req（L24-39）加结果回写——set_rv 先把 has_callback 快照到栈、release fence（L26-27）、写 out.rv、再回调，是"写完 rv 后 this 可能立即被释放"的 UAF 防护教科书；set_success 强校验全字节完成（L35-38）。init_params（L46-52）两开关：has_external_polling_loop（SPDK，run() 单步）、use_blocking_client_accept（多 bdev 同线程必须关）。impl 指针 pimpl 隐藏引擎（L66）；create_and_get_metadata_json（L61）从派生构造调用。

**server_imp.cpp 十二方法**：__clnt_bufs_register（L26-47，环走 init_consumer+cookie 校验 L39）、__clnt_bufs_unregist（L49-62）、__clnt_close（L78-92，残留时强清）、client_accept/reject（L94-123）、send_to（L64-76，失败断连停机）。**backend_io_executor**（L125-203）：每到达 IO 一堆对象——构造取 SQE（L168）；run()（L173-197）插在途→存 client 上下文→换自己回调→remap→后端 exec_io，非法参数 set_error 快速失败；_io_done_cb（L143-160）BUG_ON 校验回调同线程（L146）→srvr_finish_io 写 CQE→按需 doorbell→_io_free（多 range free SGL 拷贝 L136-137）；abandon（L199-202）放弃在途。**run_once**（L245-326）消息泵：accept→按 17 型分派——hello→b.open1 回 hello_ack（L269-283 下发 bdev_info）；die（L300-306 回 die_ack 自杀）；reboot（L307-310 模拟崩溃）；log（L311-317）；dp_submit→__clnt_on_io_receive；未知回 build_wrong（L320）。run（L328-341）外部轮询单步/内部循环；init（L343-366）三模监听；destroy（L368-380）unlink UDS。

**故障注入三层**（fail_server_ram.hpp）：dummy_server_ram（L22-42）内存基座（num_max_inflight_io=4 制造小容量）；fail_server_ram（L44-56）exec_io 直接 set_error，all_ios_stuck 时不回复（server 侧卡死）；zero_server_ram（L59-79）读 IO 清零缓冲仍 set_success 假成功——专测数据损坏检测。**read_only_ram.hpp**（L30-101）：101 行最小完整后端。**SPDK 家族**：spdk_server_ram.hpp backend_dev_t（L35-84）管描述符/channel/zone reset/try_later；open1（L99-125）spdk_bdev_open_ext+对齐校验；exec_io（L161-187）提交 read/write，io_ranges_counter 复用 io 的 _exec 槽当计数器（L136-141 免分配）；cmp_io_cb（L142-159）聚合回写。spdk_app_1server.hpp（L24-107）#ifdef 双分支：有 SPDK 时 poller 全速轮询 run_g_server_once（L59-65）驱动多 bdev、Ctrl+C 二次强退（L45-58）；无 SPDK 退化 ENOEXEC 桩（L109-120）。spdk_bdev.conf（L1-15）：malloc 两内存盘 dhs_bdev0（40960 块）/dhs_bdev1（300 块），块 4096。

## 外部连接

- 引擎依赖 dp_io_ring（receive/finish/remap）+cp_messaging+shared_mem_bufs；bdev_stats_srvr 五计数器（server_imp.hpp:31-56）与 client 单计数器不对称。
- **unitest.cpp 876 行十七组**（main L841-876：非法调用→auto open/close→本地卡死限流→双端卡死→竞态→4GB 大映射 L815→压测→无应答）；unitest/run 三入口：spdk_both（L30-39 双进程 @s/@c）、all、ci（L47-71：make→8 组参数→5 轮 SPDK 双端→查 core 判 PASS）。
- **80scripts**：service.sh 的 GUSLI 命令（show/clean/huge_pages，L22-58）；integration_with_spdkbdev.sh 搭 SPDK；integration_with_nixl.sh（NVMESH-5239）在 NIXL 容器装 GUSLI 跑 plugin 单测×50。Makefile 双 .so 由 SOURCES_BASE+各自 .cpp 链接（L270-276）；`../spdk` 存在即 whole-archive 链 27 模块（L144-166）。

## 数据流

server 视角一条 IO：run_once 收 dp_submit→__clnt_on_io_receive（L215-243）批量摘环（第三分支 "Best method" L231-242 一次 doorbell 清空环，前两个 if(0) 是保留实验策略）→逐个 run()：remap→后端 exec_io→_io_done_cb 写 CQE+doorbell→_io_free。断线：run_once 读失败→client_reject→__clnt_close 查 is_still_used→强清缓冲+__abandon_all_clnt_io（L205-213 逐个 abandon 泄漏计数后清除）。

## 设计决策

1. **回写必须同线程**：契约注释明言（gusli_server_api.hpp:55），_io_done_cb BUG_ON 校验（L146）——与 SPDK 单线程 reactor 对齐。
2. **abandon 优于 cancel**：server 不主动取消后端 IO，断线时 abandon 标记取消并泄漏计数（README 已知问题 1 自曝 ghost IO）。
3. **批量摘环**：一次 doorbell 处理环上全部 IO，摊薄控制面开销——2M IOPS 结构性来源之一。
4. **dummy/zero server 是测试基建**：client 全部错误路径（限流/卡死/数据损坏）靠这三类真实走通。

## 新人提示

- 写后端从 read_only_ram.hpp 抄起：私有继承+构造函数 set_thread_name+create_and_get_metadata_json+三函数。
- SPDK 集成必须 use_blocking_client_accept=false 且先 GUSLI huge_pages。
- 挂死先 GUSLI show 看 /dev/shm/gs* 与线程名，再 GUSLI clear；ci 判定是"无 core"而非退出码（run:64-69）。
- set_success 必须传 buf_size() 全量——部分完成变 E_BACKEND_FAULT。
- spdk_app_1server 整文件 #ifdef：无 SPDK 可编译但 get_rv() 恒 ENOEXEC——单测天然跳过。

（约 2350 字符不计空格；锚 40+ 处均经核实）
