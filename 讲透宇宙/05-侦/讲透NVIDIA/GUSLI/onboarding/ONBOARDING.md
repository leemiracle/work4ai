# GUSLI Onboarding（Gusli = G3+ User Space Access Library）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/GUSLI（git d3fb64e，v0.0.4）；图谱：仓内 .understand-anything/knowledge-graph.json（199n/345e/9 层/14 步）

## 1. 项目定位

NVIDIA 开源的**用户态块设备 IO 库**（README.md:26）：client 提交读/写，server 经后端（SPDK bdev/RAM/文件）执行，同机用户态零内核参与。交付两对：`libgusli_clnt.so+gusli_client_api.hpp`、`libgusli_srvr.so+gusli_server_api.hpp`（Makefile:303 装进 /usr）。

三个主张：①**client/server 分离=解耦编译链接依赖**（README.md:33）——后端可为 SPDK 应用而 client 不必链接 SPDK，门面以 `BREAKING_VERSION==1`（gusli_client_api.hpp:254）做 ABI 代际检测；②**零拷贝内核旁路**——IO 缓冲注册成 /dev/shm 共享内存（`/gs_iobuf_%06d`，shared_mem_bufs.hpp:67），控制面 socket 只传 64B 小消息（cp_messaging.hpp:148），数据走共享内存 SQ/CQ 环；③**1 client 多 server，每 server 一个 bdev**（README.md:30）。性能：单核对单核 1.5-2.5M IOPS（README.md:111）；server 单线程、client 每 bdev 一监听线程（README.md:104）。

## 2. 技术栈

- **C++20**（Makefile:170 `-std=c++2a`），内核风格基建：BUILD_BUG_ON 编译期断言（utils.hpp:40）、release 也崩溃取证的 BUG_ON（utils.hpp:122）、侵入式链表、位图。
- **POSIX 共享内存**：shm_open+mmap+MAP_POPULATE（atomics.hpp:135 t_shared_mem）。
- **UDS/TCP/UDP 三模**：按地址首字符判型——`/`→UDS 默认、`u`→UDP、`t`→TCP（cp_messaging.hpp:29）；后两者端口 2051（cp_messaging.hpp:27）。
- **libaio/liburing（可选）**：uring 需 `HAS_URING_LIB`（Makefile:136 pkg-config 探测），大 scatter-gather 受益，K8s 默认容器不可用（gusli_client_api.hpp:165）。
- **SPDK（可选）**：`../spdk` 存在才开 `-DSUPPORT_SPDK=1` whole-archive 链接（Makefile:144-166）；**NIXL**：gusli plugin，`80scripts/integration_with_nixl.sh`（NVMESH-5239）。硬依赖为零（README.md:49）。

## 3. 模块地图（9 层）

- **L01 文档构建**：README/SECURITY/CHANGELOG/CONTRIBUTING、.security-triage.yaml、Makefile。
- **L02 00utils**：atomics.hpp（四锁策略+completion_t+t_shared_mem）、bitmap.hpp（small_ints_set<512>，L99）、list.*、utils.*（三模 socket/tDbg/invoke_crash 崩溃注入 utils.cpp:436）。
- **L03 控制面与注册表**：cp_messaging.hpp 的 MGMT 定义 17 种消息（hello/注册/注销/close/die/ping/reboot/dp_submit/dp_complete，L37-63）；shared_mem_bufs 全局缓冲表（上限 16 段，shared_mem_bufs.hpp:66）。
- **L04 数据面环**：dp_io_ring.hpp（sqe/cqe/模板环/datapath_t）+dp_io_air_io.hpp 在途跟踪。
- **L05 API 双门面**：仅有的两个对外头。
- **L06 客户端引擎**：client_imp.hpp/.cpp+io_executors.hpp 执行器族。
- **L07 服务端引擎**：server_imp.hpp/.cpp（消息泵+backend_io_executor）。
- **L08 示例 server**：fail_server_ram（故障注入）、read_only_ram、spdk_server_ram+spdk_app_1server+spdk_bdev.conf（dhs_bdev0/1）。
- **L09 client 示例+测试+脚本**：fork_servers_and_connect、sample_client、io_submittion_example（unitest_io）；unitest/（876 行+run）；80scripts/。

## 4. 核心数据流

1. **连接**：bdev_connect→hand_shake（client_imp.cpp:796）换 bdev_info；create_dp（client_imp.cpp:770）以 producer 建环写 cookie `0xa8a9aaabacadaeaf`（cp_messaging.hpp:35），server 映射校验（server_imp.cpp:39）；每 bdev 起监听线程（client_imp.cpp:1019）。
2. **注册内存**：map_buf（client_imp.cpp:840）发 register_buf；server __clnt_bufs_register（server_imp.cpp:26）建反向映射回 ack。
3. **提交**：submit_io（client_imp.cpp:623）——本地选 sync/aio/uring；dummy 'x' 秒败 's' 挂死；远端选 wrap 执行器后 clnt_send_io（dp_io_ring.hpp:219）写 SQE+插在途，必要时 doorbell。
4. **server 执行**：run_once（server_imp.cpp:245）收 dp_submit→__clnt_on_io_receive（L215）批量摘环→backend_io_executor::run（L173）remap 缓冲（多 range 先拷 SGL，dp_io_ring.hpp:176）→后端 exec_io。
5. **完成**：set_success/set_error→_io_done_cb（server_imp.cpp:143）srvr_finish_io 写 CQE+dp_complete→client clnt_receive_completion（dp_io_ring.hpp:233）→回调/轮询/解锁；用户必须 done()（gusli_client_api.hpp:209）。

## 5. 构建与运行

- `make all`：双 .so+静态单测 z_gusli_clnt_unitest、SPDK 双端 z_gusli_spdk_both_unitest 等；生产 `make clean all BUILD_RELEASE=1 BUILD_FOR_UNITEST=0`；开关 USE_CLANG/ALLOW_USE_URING/USE_SANITIZERS。
- 单测：`./unitest/run {spdk_both|all|ci}`——ci 为完整流水（make→8 组参数→5 轮 SPDK 双端→查 core 判 PASS，run:47-71）。
- 调试：`source 80scripts/service.sh; GUSLI {show|clean|huge_pages}`（service.sh:22-58）；SPDK 环境走 integration_with_spdkbdev.sh，单测需 sudo。

## 6. 关键设计决策

1. **控制面 socket+数据面共享内存分离**：管理低频走 socket、数据走环；close 后 socket 保留待重开（server_imp.cpp:297）。
2. **io_csring 模仿 NVMe SQ/CQ**：dp_io_ring.hpp:24 注释点名借鉴 3FS IoRing/mini_liburing/libaio（"no code stealing"）；CAPACITY=512（L113）+client 在途限流⇒生产者永不因环满阻塞（L121）。
3. **三纯虚契约**：后端只实现 open1/close1/exec_io（gusli_server_api.hpp:53-55），引擎 pimpl 隐藏（L66）；read_only_ram.hpp 全文 101 行即完整后端。
4. **执行器策略模式**：io_executors.hpp 七种执行器共享基类生命周期（引用计数/detach/cancel）；never_reply_executor 与 'x'/'s' dummy 把故障注入做成一等公民。
5. **位域 params_t ABI 紧凑**：gusli_client_api.hpp:157-203 位域塞进 48B；__compilation_verification（dp_io_ring.hpp:262）BUILD_BUG_ON 锁死跨进程结构尺寸（io_request=64B=一 cache line）。
6. **同构三层身份**：io_request_base→backend_io_req（set_error/set_success+release fence 防回调 UAF，gusli_server_api.hpp:26）→server_io_req，三者同尺寸（dp_io_ring.hpp:272-273），SQE 整体搬运零序列化。
7. **五型设备一等公民**：'x'/'s'/'F'/'K'/'N'（gusli_client_api.hpp:59-66），dummy 无需 server 即可复现全部错误路径。

## 7. 已知坑与勘误（行号逐一 grep 核实）

1. **代码自认竞态**：client_imp.cpp:620 注释 "race condition...fix me"；L673 nvTODO 明言 clnt_send_io 后访问 *this 可能 use-after-free；README.md:133 自曝断线重连/取消设计未完。
2. **无 git 构建版本烟雾**：Makefile:128 dummy `VER_TAGID:=v3.1.0` 与 CHANGELOG v0.0.4 不符。
3. **文件名拼写**：`io_submittion_example.hpp` 的 "submittion" 应为 "submission"（原生拼写）。
4. **死代码**：cp_messaging.hpp:197/223 while(true) 后的 return ios_error 不可达。
5. **is_still_running 会阻塞**：wrap_remote_io_exec_blocking（io_executors.hpp:298）实为 completion_t.wait()，名实不符。
6. **三处 bdev_descriptor 魔数**：dummy=100000001（client_imp.cpp:153）、RAM=202020202（fail_server_ram.hpp:34）、SPDK=555——仅日志用途。
7. **安全面**：SECURITY.md 点名 utils.cpp:151-154 UDS chmod rwxrwxrwx、dp_io_ring.hpp:192 恶意 n_entries 未完全校验（HIGH/DEFERRED）。
8. **容量口径**：bdev_info 注释 num_max_inflight_io [1..500]（gusli_client_api.hpp:47），槽位硬上限 small_ints_set<512>（dp_io_air_io.hpp:59）；示例 256（common.hpp:41）+环 512 靠 client throttle 保环不满。
9. **图谱盲区**：dp_io_ring 模板类、io_executors.hpp:334-448 uring（#ifdef）、spdk_app_1server 整文件（#ifdef，无 SPDK 退化 ENOEXEC 桩 L109-120）、utils.hpp:294 base_library 均 tree-sitter 盲区、节点人工补录；merge 词法曾误杀 6 条 unitest.cpp tested_by 边。
10. **BUG_ON 不随 NDEBUG 消失**（utils.hpp:122）：release 断言失败出 core。

## 8. 新人上手路径

1. 读 README 建立"两个 .so+一条 shm 环"心智模型。
2. 按 14 步 tour：README/Makefile→gusli_client_api.hpp（五型+params_t）→gusli_server_api.hpp→dp_io_ring.hpp→client_imp.cpp submit_io→io_executors.hpp→server_imp.cpp→示例→unitest。
3. 最小闭环：`make all && ./z_gusli_clnt_unitest -n 8 -c 64 -l 0`（纯本地/dummy，无需 SPDK）。
4. 写后端：私有继承 srvr_backend_bdev_api，对照 read_only_ram.hpp。
5. 观测：`GUSLI show` 看共享内存与 gusli_ 前缀线程（gusli_client_api.hpp:227）。
6. 取消语义：unitest.cpp:334/668 两级卡死限流测试。
7. 改跨进程结构前必过 __compilation_verification（dp_io_ring.hpp:262）——ABI 守门员。

（约 4800 字符不计空格；行号锚 50+ 处均经核实）
