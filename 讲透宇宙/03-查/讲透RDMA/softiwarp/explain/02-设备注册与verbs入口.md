# 02 · 设备注册与 verbs 入口：从 netdev 到 ib_device 的装配线

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位

siw_main.c（770 行）回答"设备从哪来"：它不枚举 PCI，而是把**已有网络设备逐个认领**成 RDMA 设备；siw_verbs.c（1934 行）回答"拿到设备后能干什么"：RDMA core 看到的 31 个 ib_device 回调全在此实现。两文件合起来是 siw 与 OFA 生态的边界层——所有外部请求的第一站。对内核态消费者（如 NFS-RDMA）这里是唯一入口；对用户态应用，这里是与 userlib 共谋 mmap 快路径的服务端。

## 二、内部结构

**模块加载序列**（siw_init_module，siw_main.c:633-724）：总线与伪 DMA 设备注册（:652/:658，xprtrdma 需要一条 bus 来设 path MTU）→ siw_cm_init（:662）→ siw_sq_worker_init（:666）→ debugfs（:670）→ **register_netdevice_notifier（:672）**——从这一刻起所有 netdev 事件都会回流到 siw_netdev_event → per-CPU TX 线程拉起（:694-700，`siw_create_tx_threads` 在每颗合格 CPU 上 kthread_create+bind `siw_run_sq`，siw_main.c:296-300）。

**设备生命周期三函数**：

- `siw_device_create`（siw_main.c:341-513，约 170 行装配线）：ib_alloc_device 分配 → 挂 iwcm ops 表（:351）→ 设备名 `siw_<netdev>`（:361-363）→ node_guid 取网卡 MAC、loopback 用设备名前 6 字节顶替（:365-375）→ uverbs_cmd_mask 放行 22 条命令（:378-401）→ node_type=RDMA_NODE_RNIC、phys_port_cnt=1、num_comp_vectors=1（:403-413）→ 31 个 verbs 回调逐个赋值（:415-458）→ iw_cm 八回调（connect/accept/reject/create_listen/destroy_listen/add_ref/rem_ref/get_qp，:460-467）→ attrs 上限拷贝自 siw.h:68-81 的 SIW_MAX_* 宏（QP 10 万、WR 3.2 万、MR 百万，:477-493）。
- `siw_device_register`（:141-183）：ib_register_device 挂入 RDMA core，再补两个 sysfs 属性（sw_version/if_type）与 debugfs 节点；vendor_part_id 用静态 dev_id 自增分配——它就是 doorbell 要用的 dev_id。
- 销毁链 deregister→destroy（:185-235）：八项 WARN_ON 校验对象计数归零（:202-208），泄漏的 CEP 直接 kfree 并告警（:212-222）。

**触发时机由 siw_netdev_event 决定**（:517-620）：NETDEV_REGISTER 时 `siw_dev_qualified` 过滤（:320-339：iface_list 白名单匹配 + ARPHRD_ETHER/IEEE802/INFINIBAND/LOOPBACK 四类；loopback 默认启用，:72）→ create 但**不注册**；NETDEV_UP 且 `in_dev->ifa_list` 非空（已配 IP）才真正 register（:551-565）。即插了没配 IP 的网卡会有 siw 设备壳子但没有 verbs 能力。

**verbs 入口侧关键函数**：`siw_alloc_ucontext`（siw_verbs.c:184-231）做配额检查后把 `dev_id` 和 `rdma_db_nr`（doorbell 系统调用号，无则 -1）塞进 uresp 回给用户（:209-221）；`siw_mmap`（:151-181）凭 key 取出 uobj 并 `remap_vmalloc_range` 把 vmalloc 内核环映射进用户地址空间——快路径的地基；`siw_reg_user_mr`（:1559-1648）：MR 配额 → RLIMIT_MEMLOCK 预检（:1588-1600）→ `siw_umem_get` 自研钉页（siw_mem.c:114，can_do_mlock :121、get_user_pages :163、CHUNK_SHIFT=9 二维页表）→ `siw_alloc_mr` 入 idr，**lkey=rkey=id<<8**（:1532），用户传入的 stag_key 直接 OR 进两个 key（:1622-1623，源码自带 `/* XXX ??? */` 注释）→ STAG_VALID 激活（:1633）。

## 三、外部连接

上游：RDMA core 的 ib_register_device 与回调分发；netdev notifier 链。下游：userlib 的认领流程 `siw_driver_init`（userlib/src/siw.c:152-209）读 sysfs 三件套——node_desc 须匹配 "Software iWARP stack"（:180-182）、sw_version 须等于 2、if_type 决定快慢路径（siw.c:111-129：SIW_IF_MAPPED→siw_post_send_mapped，SIW_IF_OFED→走 ibv_cmd 全家）。注意内核注册时固定 `attrs.iftype = SIW_IF_MAPPED`（siw_main.c:472），mapped 快路径是默认形态。横向：debugfs（siw_debug.c）、siw_obj.c 的 idr+kref 给所有 verbs 对象提供编号与生命周期。

## 四、数据流

设备出生线：`netdev register → qualify → siw_device_create（壳）→ netdev up+配 IP → siw_device_register（ibv_devices 可见）`。

用户上下文建立线：`ibv_open_device → kernel siw_alloc_ucontext → uresp{dev_id, rdma_db_nr} → userlib 存下两者（siw.c:104-105）`。之后每次 create_qp/create_cq 的 uresp 都带 mmap key，用户态 mmap 拿到 SQ/RQ/CQ 环的共享视图，post_send 只剩"写环+敲铃"两个动作。

MR 注册线：`ibv_reg_mr → RLIMIT 预检 → GUP 钉页成二维页表 → idr 编号 → key=id<<8|stag_key → 用户拿到 stag`。RX/TX 侧用 `lkey>>8` 反查（siw_qp.c:750、siw_qp_rx.c:594），闭环。

## 五、设计决策

1. **一对一设备映射**：每个 netdev 一个 siw 设备、单口（phys_port_cnt=1，:411 注释明言当前模型）。简单，代价是设备数随网卡数膨胀。
2. **注册推迟到配 IP**：没有 IP 的口对 CM 无意义，port state 停在 INIT。这让 siw 设备的"可用性"与网络配置天然同步。
3. **max_mr_size = rlimit(RLIMIT_MEMLOCK)**（:487）：软件 RDMA 的资源上限不是硬件显存而是进程可锁内存，诚实地把约束暴露给上层。
4. **软件 DMA 假象**：dma_device 指向全局 `siw_generic_dma_device`（:124-128/:414），mapping ops 返回内核虚拟地址（siw_mem.c:199-227）——RDMA core 的 DMA 抽象层被原样架空，这是纯软件 provider 的特权。
5. **lkey/rkey 同源**：一个 24 位 id 同时充当两种 key 的基座（:1532），权限差异只在 siw_mem.perms 位图里区分——比对硬件 per-key 的实现更朴素，也埋下"两 key 等价"的语义简化。

## 六、新人提示

1. **调试入口**：dmesg 顺序应是 "SoftiWARP attached"（:702）→ "Registered 'siw_xx'"（:172）；若设备不出现在 ibv_devices，先查 `ip addr`（无 IP 不注册）、再查 iface_list 是否排除了它、最后查 /proc/net/dev 的接口类型是否在四类之内。
2. **三个 id 别混**：vendor_part_id（=dev_id，doorbell 参数）、QP id（idr 编号，qp_num）、uobj key（mmap 偏移）。doorbell 调用签名 `syscall(rdma_db_nr, SIW_DB_SQ, dev_id, qp_id)`（siw_uverbs.c:289-290）用的就是前两个。
3. **rhel/老内核适配多**：siw_verbs.c/siw_main.c 里大量 `LINUX_VERSION_CODE` 分支（如 :147/:417），读代码时注意你所在内核版本走的是哪一支——本仓基线老，新内核上这些分支会集体失配。
4. **siw_get_dma_mr**（:1659-1688）注册的是"无 umem 的全域 MR"（len=ULONG_MAX），内核态消费者用；用户态标准路径始终走 reg_user_mr。
5. **动手**：`cat /sys/class/infiniband/siw_lo/node_desc` 应输出 "Software iWARP stack"；对照 siw_main.c:111-117 看两个 DEVICE_ATTR 如何生成 sw_version/if_type 文件。

📌 下一篇：03 篇进 siw_create_qp 与 QP 八态机——verbs 世界里最重的对象如何诞生与流转。
