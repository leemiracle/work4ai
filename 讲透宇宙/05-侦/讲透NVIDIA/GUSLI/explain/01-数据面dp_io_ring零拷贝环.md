# 01 · 数据面 dp_io_ring：共享内存 SQ/CQ 零拷贝环

> 文件：`01common/dp_io_ring.hpp`（280 行）+ `01common/dp_io_air_io.hpp`、`01common/shared_mem_bufs.hpp/.cpp`；图谱 L04，fanOut 23 全仓最高之一

## 角色定位

dp_io_ring 兑现"零拷贝内核旁路"主张：client/server 的 IO 请求与完成不走 socket，而在双方 mmap 的共享内存上用模仿 NVMe SQ/CQ 的双环交换。文件头（dp_io_ring.hpp:24-28）点名思想来源：DeepSeek 3FS IoRing、内核 mini_liburing、libaio、io-uring-ipc（"no code stealing"）。控制面只管 doorbell 唤醒与生命周期——**控制面传命令，数据面传数据**，是全仓最重要的职责切分。

## 内部结构

- **io_csring_sqe**（L30-42）：提交条目，整体搬运 48B 的 io_request::params_t 作 user_data；init_from（L37-40）把客户端 IO 指针塞进完成上下文，server 凭此找回对端结构。
- **io_csring_cqe**（L44-56）：完成条目，仅 {server_io_req* io_ptr; int64_t rv}。
- **io_csring_queue**（L58-110）：模板环，容量 CAPACITY-1；head/tail 双指针+自旋锁（L61）；is_full 判 head==tail（L69）——牺牲一槽换空/满不混淆。非类型模板参数 const char dbg_name（'s'/'c'）只服务注释掉的调试打印（L88）。
- **io_csring**（L112-124）：sq+cq 双环；CAPACITY=512（L113）；is_big_enough_for 保证容量≥最大在途+1（L121 注释 "+1 for debug"）。
- **datapath_t**（L127-173）：每 bdev 一条数据路径，聚合 shm_ring+shm_io_bufs+reg_bufs_set+in_air+stats；构造按 producer（client，L142）/consumer（server）分支。

## 外部连接

- **shared_mem_bufs.hpp**：shm_io_bufs_global_t 全局注册表（L61-102）——client insert_on_client 发 buf_idx、server insert_on_server 建反向映射；base_shm_element::convert_to_my（L37-46）做「对端指针偏移换算」——**数据从未搬运，只有指针被翻译**，这是零拷贝关键。上限 16 段（L66 注释直言线性搜索慢、留待未来）。
- **dp_io_air_io.hpp**：in_air_ios_holder（L51-151）用 small_ints_set<512> 位图（L59）+指针数组管在途槽位，满载计 n_throttled_ios（L98）形成限流反馈；server_io_req（L26-48）叠加 11 位 uid 与取消语义。
- **控制面**：doorbell 消息 dp_submit/dp_complete（cp_messaging.hpp:61-62）；t_shared_mem（atomics.hpp:135）是 mmap 载体，MAP_POPULATE+预热防 SIGBUS。

## 数据流

提交：clnt_send_io（L219-230）校验（未设 safe_io 走 verify_io_param_valid，L205-216 逐 range 查对齐/LBA 界内/已注册）→sq.insert 写 SQE+插在途→返回是否 doorbell。L228 注释：插入瞬间完成就可能到达，此后访问 io 有已知竞态（client_imp.cpp:673 nvTODO 自认）。server：srvr_receive_io（L247-250）取环→srvr_remap_io_bufs_to_my（L176-202）翻译地址——单 range 直接 remap；多 range 先 posix_memalign 拷整张 SGL（L184-199，注释两理由：SGL 属 client 可能重遍历、client 可能重试）再逐条翻译。完成：srvr_finish_io（L253-260）组 CQE 插 cq；client clnt_receive_completion（L233-244）取出回调。

## 设计决策

1. **锁策略模板化**：环用自旋锁（短临界区）、注册表互斥锁，atomics.hpp 四策略可整体替换。
2. **编译期 ABI 守门**：__compilation_verification（L262-277）十余条 BUILD_BUG_ON 锁死跨进程尺寸：params_t=48B、io_request=64B（一 cache line）、三种 IO 结构同尺寸（L272-273）——同一 64B 在用户/后端/引擎三视角间整体搬运，零序列化。
3. **cookie 防错连**：client 建环首 8B 写 MGMT::shm_cookie（client_imp.cpp:781），server 映射后校验（server_imp.cpp:39）。
4. **"不可能满环"**：环满触发 BUG_ON(true)（L226）——in_air 限流先行，环满即内部 bug 崩溃取证（BUG_ON release 也生效，utils.hpp:122）。
5. **禁构造基类**：io_csring 等继承 no_constructors_at_all（utils.hpp:85-88），防跨进程对象被构造函数二次初始化。

## 新人提示

- 改跨进程结构先过 __compilation_verification——断言失败=ABI 已破。
- template 类+位域是 tree-sitter 盲区：本文件核心类节点系人工补录，图谱无函数级粒度。
- GUSLI show 看 /dev/shm/gs*：环 `/gs<uuid>ring`（cp_messaging.hpp:96）、缓冲 `/gs_iobuf_%06d`（shared_mem_bufs.hpp:67）。
- 多 range 在 server 侧有一次 SGL 深拷贝（L187-192）——"零拷贝"指数据缓冲本体，元数据仍有百字节级拷贝。
- 环为何永不满：L121 的 "+1" 与 in_air_ios_holder 的 throttle（dp_io_air_io.hpp:97-100）连读。

（约 2250 字符不计空格；锚 30+ 处均经核实）
