# 01 · 软 iWARP 动机与模块鸟瞰：在 TCP 上重造一台 RDMA 网卡

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位：这个仓库在解决什么问题

RDMA 的两个卖点——内核旁路的一步式数据放置、显式完成语义——传统上绑定 InfiniBand/RoCE 专用网卡。没有 RNIC 的机器想跑 verbs 应用（perftest、NFS-RDMA、NVMe-oF），过去只有两条路：买卡，或者改代码。softiwarp（siw）给出第三条：**纯软件在普通网卡的 TCP 字节流之上实现完整 iWARP 协议族**（MPA/DDP/RDMAP，RFC 5044/5041/5040），对上仍暴露标准 RDMA verbs（kernel/IMPLEMENTATION.txt:3-9）。

它的本质是一台"用 CPU 模拟的 RNIC"：硬件里 DDP 头解析、DDP 段重组、CRC 校验是管线上的固定电路，siw 把它们摊平成两个软件状态机（siw_qp_tx.c 发送、siw_qp_rx.c 接收）；硬件的 DMA 引擎在 siw 里是假象——`siw_dma_map_single` 直接返回内核虚拟地址（siw_mem.c:199-204，注释自述"siw uses kernel virtual addresses"）。

两条时间线必须先钉住：①本仓自 Linux 5.2 起并入内核主线 drivers/infiniband/hw/siw，zrlio 仓仅存参考（README.md:3-9 DISCLAIMER）；②kernel/README_KERNEL_VERSIONS.txt 记录 3.15 起弃用 OFA core 的 ib_umem_get 改自研钉页。**新部署应走主线版**，本仓的不可替代价值是：源码即 RFC 的可运行参考实现，且带一个独立的用户态映射快路径。

## 二、内部结构：两半工程 + 一个 ABI 头

**kernel/ 可加载模块 siw.ko**（约 9,700 行 C），按职责分四组：

| 组 | 文件 | 一句话职责 |
|---|---|---|
| 入口与基座 | siw_main.c（770 行）、siw.h（822 行）、iwarp.h（370 行） | 模块生命周期、设备注册；对象模型字典头；RFC wire 结构的 C 语言化 |
| verbs 面 | siw_verbs.c（1934 行）、siw_obj.c、siw_mem.c、siw_cq.c | ib_device 全部回调、idr+kref 对象管理、自研 umem 钉页、完成出口 |
| 连接管理 | siw_cm.c（1952 行）、siw_cm.h | TCP+MPA 双重握手、CEP 状态机、iw_cm 事件胶合 |
| 数据面 | siw_qp.c（1161 行）、siw_qp_tx.c（1413 行）、siw_qp_rx.c（1351 行） | QP 状态机与分发表、SQ 发送引擎、RQ 接收引擎 |

辅助件：siw_ae.c 异步事件桥（113 行）、siw_debug.c/h debugfs 与 dprint 开关。

**userlib/ libsiw**：siw.c 214 行——constructor `siw_register_driver`（userlib/src/siw.c:211）向 libibverbs 注册驱动名 "siw"；siw_uverbs.c 493 行是 mapped 快路径（直写共享环）；siw_verbs.c 491 行是 OFED 慢路径；siw_abi.h 叠加私有扩展。

**common/siw_user.h（212 行）是两侧唯一公共头**：定义共享环元素 siw_sqe/siw_rqe/siw_cqe、各创建命令的 uresp 响应（带 mmap key）、opcode 与 flag 枚举。它的存在解释了整个仓库最硬的约束：环布局一变，内核与用户库必须同步重编。

## 三、外部连接：四个接壤面

1. **RDMA core（内核侧）**：siw 以 ib_device provider 身份注册（siw_main.c:148），verbs 回调 31 个在 siw_device_create 中逐一挂上（siw_main.c:415-458）；连接管理挂 iw_cm 八回调（siw_main.c:460-467）。
2. **TCP 栈**：CM 阶段用 kernel socket 全套（bind/connect/accept/sendmsg，siw_cm.c:1268-1295）；数据阶段 TX 走 kernel_sendmsg/sendpage（siw_qp_tx.c:338/:409），RX 在 socket 数据就绪回调里 `tcp_read_sock` 拉取（siw_qp.c:184）——收发都不再经过 VFS 层。
3. **netdev 子系统**：notifier 监听 NETDEV_REGISTER/UP/DOWN/UNREGISTER（siw_main.c:517-620），每个合格网卡动态生成一个 siw 设备，命名 `siw_<netdev名>`（SIW_IBDEV_PREFIX，common/siw_user.h:55）。
4. **用户态 libibverbs**：sysfs 三件套 node_desc/sw_version/if_type 决定 userlib 是否认领设备（userlib/src/siw.c:176-198，node_desc 必须匹配 "Software iWARP stack"）。

## 四、数据流：帧格式与一次 WRITE 的旅程

iWARP 的封装自内向外是四层：**RDMAP**（语义：SEND/READ/WRITE，opcode 在 ddp_rdmap_ctrl 低 4 位，iwarp.h:143）→ **DDP**（放置：tagged 段带 STag+TO 直写缓冲，untagged 段带 QN+MSN+MO 走队列，iwarp.h:267-283）→ **MPA**（成帧：2 字节长度前缀恢复消息边界 + 4 字节 CRC32C trailer，iwarp.h:102/:121）→ **TCP**（可靠字节流）。一个 FPDU（帧协议数据单元）= MPA 长度头 + DDP/RDMAP 头 + 载荷 + 0-3 字节 pad + CRC。TCP 不保消息边界，正是 MPA 层存在的全部理由。

`ibv_post_send(RDMA_WRITE)` 的七跳速览（后续五篇逐层展开）：

1. 用户态 `siw_post_send_mapped` 直写 mmap 共享 SQ 环（siw_uverbs.c:247），`syscall(rdma_db_nr,...)` 或空 OFA 调用敲 doorbell（siw_uverbs.c:288-292）；
2. 内核 `siw_doorbell_sq` 校验 RTS 后激活 TX（siw_verbs.c:920-994）；
3. `siw_qp_sq_process` 逐 WQE 推进（siw_qp_tx.c:1040），查 `iwarp_pktinfo` 静态表取控制字模板（siw_qp.c:80）；
4. 按 MSS 切 DDP 段、优先 sendpage 零拷贝推送（siw_qp_tx.c:314-320）；
5. 对端 socket 回调 `siw_qp_llp_data_ready`（siw_qp.c:156）→ `tcp_read_sock(..., siw_tcp_rx_data)`（siw_qp.c:184）；
6. 接收状态机从字节流切出 FPDU、查同一张表分派，WRITE 走 `siw_proc_write`（siw_qp_rx.c:566）：验 STag/边界/权限后载荷直接放进目标注册内存，**不消耗对端 RQ**；
7. SIGNALED 的 WQE 生成 CQE；连接异常则 `siw_cq_flush` 整队出 FLUSH 完成（siw_cq.c:132）。

## 五、设计决策：软件实现的得与失

- **收益**：可移植（任意以太网卡/loopback）、可调试（软件状态机可 dprint、debugfs 三视图）、零硬件成本——这是协议参考实现与教学样本的双重价值。
- **代价**：所有协议处理在 CPU 上，延迟与吞吐都追不上硬件；iWARP 相比 RoCE 还额外背 CRC32c 计算成本（协商开启时 TX/RX 各挂一个 crc32c shash，siw_qp.c:349-375）。
- **MPA 减配**：Marker 收发明确缺失（IMPLEMENTATION.txt:119-120）。Marker 本用于 TCP 半关闭后重同步帧边界，正常连接场景几乎用不到，砍掉换实现简洁。
- **sendpage 实验性**：仅在非 SIGNALED、载荷超 PAGE_SIZE、未开 CRC 时启用（siw_qp_tx.c:314-320 + IMPLEMENTATION.txt:47-57），因为完成语义只保证"已交 TCP"，TCP 重传期间用户改缓冲会同时破坏数据与 CRC。
- **并入主线的战略**：作者把维护重心移入内核树后，本仓成为化石标本——读它更像读 iWARP 的"出厂图纸"，主线版才是活体。

## 六、新人提示

1. **阅读顺序**：本篇 → common/siw_user.h 全文（212 行，半天）→ iwarp.h 对照 RFC 5040/5041/5044 的 wire 图过一遍 → siw_main.c 跟一次模块加载 → 再按 02-06 篇顺序进各引擎。
2. **勘误先行**（详见 ONBOARDING 第 8 节）：全仓真正的死代码是 SIW_TX_FULLSEGS（4 处 #ifdef 永假，siw_qp.c:276、siw_qp_tx.c:805/818/954）；而 `USE_SQ_KTHREAD` 在 siw.h:542 **默认 #define，是活代码**——per-CPU 内核线程是默认 TX 执行模型，被排除的是 workqueue 备选。把这两个说反是最常见的误读。
3. **词汇陷阱**：ORQ/IRQ 是 outbound/inbound read queue（READ 操作的两半），与中断无关；SQE/RQE/CQE 分别指三个环上的元素。
4. **动手验证**：`insmod siw.ko` 后看 dmesg "SoftiWARP attached" 与 TX 线程启动日志（siw_main.c:702/:1307）；`ibv_devices` 应列出 siw_lo 等设备；debugfs `/sys/kernel/debug/siw/<dev>/stats` 可看收发计数。
5. **不要在本仓上追新内核**：基线老（README_KERNEL_VERSIONS.txt 记录到 3.x 时代的接口变迁），新内核编译预期失败；要跑就取主线 drivers/infiniband/hw/siw。

📌 下一篇预告：02 篇进 siw_main.c/siw_verbs.c，看一个 netdev 如何变成 RDMA 设备、verbs 入口如何分发。
