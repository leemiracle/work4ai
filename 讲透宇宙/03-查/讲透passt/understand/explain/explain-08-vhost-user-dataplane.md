# explain-08 · vhost_user.c + vu_common.c：vhost-user 数据面与性能天花板

## 1. 角色定位

`--vhost-user`（MODE_VU）是 passt 的第三种模式：不再让 qemu 把以太网帧写进 UNIX socket，而是把 **guest 内存的 mmap 与 virtio 描述符环直接交给 passt**。passt 在这里扮演一个 userspace vhost-user net backend：处理 vhost-user 协议控制消息（`vhost_user.c`，1215 行）、操作 vring 收发描述符（`vu_common.c` + 移植自 QEMU libvhost-user 的 `virtio.c`），`tcp_vu.c`/`udp_vu.c` 直接在描述符上组段。收益是双向零拷贝：guest 发包时 passt 读 guest 内存里的数据原样送 socket；passt 收包时把 L3/L4 头直接写进 guest 提供的可写描述符，全程没有 tap 模式那层帧缓冲拷贝。`tap.c` 的 `tap_backend_init()` 在 vu 模式下调 `vu_init()` 并把报文池 base 指向 vhost 内存（`tap.c:1596-1597`）——tap 抽象层完整保留，L4 逻辑无感切换。

## 2. 内部结构

**vhost_user.c = 协议控制面**。文件头声明血统（`vhost_user.c:8-20`：部分代码取自 QEMU subprojects/libvhost-user）。`vu_print_capabilities()`（`vhost_user.c:58`）是 vhost-user 约定的第一课：qemu 以 `--print-capabilities` 探测时后端打印 `{"type": "net"}` 即退场。`vu_request_to_string()`（`vhost_user.c:72`）用 `REQ()` 宏把 40 个 VHOST_USER_* 请求号映射成名字——debug 日志的功臣。消息收发三件套：`vu_message_read_default()`（`vhost_user.c:188`，含 SCM_RIGHTS 收 fd）、`vu_message_write()`（`vhost_user.c:261`）、`vu_send_reply()`（`vhost_user.c:304`）。

核心是一张 `vu_handle[]` 分发表，每个请求一个 `vu_*_exec` 处理器：`vu_get/set_features_exec`（`vhost_user.c:320/359`）协商 virtio 特性位；`vu_set_owner_exec`（`:384`）；**`vu_set_mem_table_exec`（`:425`）是整个模式的支点**——QEMU 通过 SCM_RIGHTS 传来 guest 各内存区域的 memfd，passt 逐个 `mmap(PROT_READ|PROT_WRITE, MAP_SHARED|MAP_NORESERVE)`（`:462-466`），记录 `gpa/qva/size/mmap_addr` 四元组（guest 物理地址、QEMU 虚拟地址、大小、我们这边的映射基址），已建过的 vring 要 `map_ring()` 重映射（`:483-488`——热迁移换内存表时队列指针全部要搬家）。`qva_to_va()`（`:134`）做 QEMU 地址到本进程地址的翻译，vring 的 desc/avail/used 环指针由此得来。vring 家族：`vu_set_vring_num/addr/base_exec`（`:634/654/700`）配置环；`vu_set_vring_kick_exec`（`:792`）接管 kick eventfd 并挂进 epoll（EPOLL_TYPE_VHOST_KICK，ref.queue 带队列号）；`vu_set_vring_call_exec`（`:832`）收 call fd（我们通知 guest 的门铃）。日志家族 `vu_set_log_base/fd_exec`（`:569/611`）+ `vu_log_write()`（`:544`）支持脏页记录，是热迁移时 qemu 增量同步 guest 内存的前提。新近的 `vu_set_device_state_fd_exec`/`vu_check_device_state_exec`（`:1006/1039`）对接 vhost-user 迁移协议的设备状态传输阶段。

两个事件入口：`vu_control_handler()`（`:1162`）处理控制 socket（EPOLL_TYPE_VHOST_CMD）：读消息→查 `vu_handle[]`→按 NEED_REPLY 标志回包（`:1193-1200` 的兜底：处理器没主动回但协议要求回，就补一个 0）；尾部还兼职迁移收尾判断（`:1202-1214`：CHECK_DEVICE_STATE 且非迁移目标且 migrate_exit 置位 →"Migration complete, exiting"）。`vu_init()`（`:1051`）初始化全部队列的 fd 为 -1、notification=true，并 `migrate_init()`。`vu_cleanup()`（`:1076`）/`vu_sock_reset()`（`:1127`）处理前端断连的复位。

**vu_common.c = 数据面公共路径**。`vu_kick_cb()`（`vu_common.c:224`）是收包起点：guest 踹了 kick eventfd → 读掉事件 → TX 队列则 `vu_handle_tx()`（`:169`）：循环 `vu_queue_pop()` 弹出描述符（out 方向=guest 要发的数据）→ 剥掉 virtio-net 头（`IOV_DROP_HEADER(struct virtio_net_hdr_mrg_rxbuf)`）→ **`tap_add_packet()` 直接入池**（`:203`）——与 tap 模式共用同一条上行管线！弹完一批后 `vu_queue_fill/flush/notify`（`:209-214`）归还描述符并按门铃。`vu_collect()`（`:68`）是发包侧的收集器：从 RX 环弹出 guest 备好的可写缓冲，凑够一帧的 iovec 链（支持 VIRTIO_NET_F_MRG_RXBUF 合并缓冲；`:80-84` 对无 in 缓冲的元素告警并 detach）。`vu_set_vnethdr()`（`:122`）填 virtio-net 头（`VU_HEADER` 常量+num_buffers）。`vu_flush()`（`:140`）把收来的元素填回去、通知 guest。`vu_send_single()`（`:248`）是给协议应答器（DHCP/NDP）用的单帧路径：collect → 拷数据进 guest 缓冲 → flush，tap.c 的 `tap_send_single()` 在 MODE_VU 分支转到这里（`tap.c:157-158`）。`vu_packet_check_range()`（`:32`）校验一段指针区间确实落在映射的 guest 内存内——防越界的护栏。

## 3. 外部连接

`vhost_user.h` 定义 `struct vu_dev`（内存区域表+VHOST_USER_MAX_VQS 个 `vu_virtq`）；`virtio.c` 提供 `vu_queue_pop/fill/flush/notify` 等环操作原语（libvhost-user 血统）。依赖：tap.c（vu_send_single/tap_add_packet 桥接）、pcap.c（收发都可抓）、migrate.c（`migrate_init` 与设备状态阶段）、repair.c（vu 模式初始化时起 repair socket，`tap.c:1613`）。被依赖：`tcp_vu.c`/`udp_vu.c` 用 vu_collect/vu_flush 组包；passt.c 的两个 epoll 入口（VHOST_CMD→vu_control_handler、VHOST_KICK→vu_kick_cb）；tap.c 的三处模式分派。`epoll_ctl.h` 的 `epoll_ref.queue` 字段专为 kick fd 的队列号而设。

## 4. 数据流

guest 发一个 TCP 段：guest 驱动把数据写进 TX 环描述符、踹 kick fd → epoll VHOST_KICK → `vu_kick_cb` → `vu_handle_tx`：pop 描述符得到指向 guest 内存的 out_sg → 剥 virtio-net 头 → `tap_add_packet` 入池（tap.c 照常学 MAC、分池）→ `tap_handler` → tcp.c 翻译 → socket send——**payload 从 guest 内存到 socket 只有一次 DMA 级读取，无中间拷贝**。反向：socket 可读 → `tcp_sock_handler` → `tcp_vu_data_from_sock`：`vu_collect` 从 RX 环借 guest 可写缓冲 → 直接把 IP/TCP 头+payload 写进去（头就地构造，payload recv 到 guest 内存）→ `vu_flush` 按铃。对比 tap 模式（组帧→帧缓冲→sendmsg），少两次拷贝且省掉 qemu 转发线程的调度。

## 5. 设计决策

其一，**协议栈复用、数据面替换**：vu 模式没有另起一套 L4 代码，`tap_add_packet`/`tap_send_single` 两个缝合点让 tcp.c/udp.c/arp.c 无差别运行——模式差异被压在 tap.c 与 tcp_vu/udp_vu 的分派里，这是"抽象层付红利"的典范。其二，**mmap MAP_NORESERVE 共享映射**（`vhost_user.c:462-466`）：guest 内存本来就是 qemu 分配好的 memfd，passt 只是映射同一份物理页，进程 RSS 几乎不涨；注释顺带解释为什么不用 mmap 的 offset 参数（映射地址必须页对齐，offset 记在 `mmap_offset` 里手工加）。其三，**SET_MEM_TABLE 的重映射纪律**（`:483-488`）：内存表在迁移/启动阶段可能多次下发，先 munmap 旧的再映射新的、活着的 vring 逐一 remap——顺序错了就是悬空指针。

## 6. 新人提示

调试入口：`vu_request_to_string` 的 debug 表 + `--debug` 能看到每条控制消息的名字与参数（region 表的 gpa/qva/mmap_addr 全打印）；`--pcap` 在 vu 模式同样可用（pcap 钩子在 tap_add_packet/vu_flush 两侧）。坑三条：vring 三个 fd（kick/call/err）生命周期不同步，cleanup 时要按 `vu_cleanup()` 的顺序处理；`vu_packet_check_range` 的越界返回 -1 时上层通常静默丢包，排查 guest 内存相关诡异问题先怀疑这里；qemu 侧必须用 `-object memory-backend-memfd,share=on`（`tap.c:1383` 的启动提示就是现成模板），普通匿名内存后端映射不进来。加新 vhost-user 消息支持：`vu_handle[]` 表加处理器 + 需要回包时返回 true。
