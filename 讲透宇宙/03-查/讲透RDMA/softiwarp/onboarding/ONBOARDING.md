# softiwarp 新人导览（ONBOARDING）

> 仓库 zrlio/softiwarp @ 5d8a418 · 知识图谱 274 节点/495 边/15 层/15 步 tour · 行号锚全部经源码核实（2026-11-12）

## 1. 项目定位：没有 RDMA 网卡，也能跑 verbs

RDMA 的核心价值是旁路内核的零拷贝传输与显式完成语义，传统上要靠 RoCE/InfiniBand 专用网卡。softiwarp（siw）反其道：**纯软件在任意网卡的 TCP 字节流之上实现完整 iWARP 协议族（MPA/DDP/RDMAP，RFC 5044/5041/5040），让无 RDMA 硬件的普通 Linux 跑标准 verbs 应用**。两半组成：`kernel/` 的可加载模块 siw.ko（ib_device 提供者 + iw_cm 连接管理）与 `userlib/` 的 libsiw（libibverbs 用户态驱动），两侧只共享 `common/siw_user.h` 一个 ABI 头。siw 用 CPU 换可移植与可调试，是可运行的 RFC 参考实现。

两条时间线先钉住：①本仓自 Linux 5.2 起**并入内核主线**（drivers/infiniband/hw/siw），zrlio 仓仅作参考（README.md:3-9 DISCLAIMER）；②`kernel/README_KERNEL_VERSIONS.txt` 记录 3.15 起弃用 OFA core 的 ib_umem_get、改自研钉页（OFA 用户页管理低效）。新部署走主线版。

## 2. 快速上手：编译、加载、验证

前置：内核头（/lib/modules/$(uname -r)/build）+ libibverbs 开发包。

```bash
cd userlib && ./autogen.sh && ./configure && make install  # 装入 /etc/libibverbs.d/
cd ../kernel && make        # 外部模块机制，产出 siw.ko
sudo insmod ./siw.ko                       # 所有 CPU 起 TX 线程
sudo insmod ./siw.ko tx_cpu_list=0,2       # 指定 CPU 起 TX 线程
```

验证：`ibv_devices` 列出设备（网络设备 notifier 动态注册，loopback 默认启用，siw_main.c:72）；debugfs 三视图 `/sys/kernel/debug/siw/<dev>/qps|ceps|stats`。参数：`iface_list` 白名单（siw_main.c:68）、`zcopy_tx` sendpage 开关（siw_qp_tx.c:63）。

## 3. 架构总览：15 层地图

| 块 | 层 | 要点 |
|---|---|---|
| 文档 | L01 | README、IMPLEMENTATION.txt（设计总纲）、内核版本史 |
| 构建 | L02 | kernel 侧 Makefile+Kbuild 外部模块；userlib 侧 autotools 链+RPM spec |
| 契约 | L03 | `common/siw_user.h` 两侧唯一公共头（共享环元素 siw_sqe/siw_rqe、siw_cqe、带 mmap key 的创建响应）；`siw_abi.h` 叠加私有扩展 |
| 内核基座 | L04-L08 | L04 字典双头：`siw.h` 对象模型（被 10 个 .c 依赖）+`iwarp.h` 370 行 RFC 的 C 语言化；L05 入口 siw_main.c+事件桥 siw_ae.c；L06 siw_obj.c idr+kref；L07 siw_mem.c 自研钉页+软件 DMA；L08 siw_verbs.c 1934 行 verbs 面 |
| 连接与数据面 | L09-L12 | L09 siw_cm.c MPA 握手；L10 siw_qp.c 状态机+分发表、siw_cq.c 完成出口；L11 siw_qp_tx.c 发送引擎；L12 siw_qp_rx.c 接收引擎 |
| 用户态 | L13-L15 | L13 debugfs；L14 libsiw 装载注册；L15 快慢双路径 siw_verbs.c（慢）/siw_uverbs.c（快） |

三个横切点：**共享 ABI 是地基**——mapped 快路径即用户态直写共享 SQ/RQ 环，布局一变两侧同步重编；**软件 DMA 是假象**——dma 地址即物理/内核地址直通（siw_verbs.c:1655 注释）；**枢纽**——siw.h（fanIn 11）、siw_cm.h、siw_obj.h（各 fanIn 10）是内核十字路口。

## 4. 核心链路：一次 RDMA WRITE 的一生

以 `ibv_post_send(WR: RDMA_WRITE)` 为例，七跳：

1. **用户态入队**：`push_send_wqe`（siw_uverbs.c:161）直写 mmap 共享 SQ 环，`siw_db_ofa`（siw_uverbs.c:223）敲 doorbell——零 syscall。
2. **内核触发**：`siw_doorbell`（siw_verbs.c:996）→`siw_doorbell_sq`（:920）激活 TX。
3. **SQ 流水**：`siw_qp_sq_process`（siw_qp_tx.c:1040）逐 WQE 推进；`-EINPROGRESS` 时 `siw_sq_queue_work`（:1119）交棒 `siw_run_sq`（:1295，siw_main.c:297）。
4. **FPDU 构造**：查 `iwarp_pktinfo`（siw_qp.c:80）取控制字模板，按 MSS 切段，优先 sendpage。
5. **对端接收**：`siw_qp_llp_data_ready`（挂于 siw_qp.c:297）调 `tcp_read_sock(..., siw_tcp_rx_data)`（siw_qp.c:184）。
6. **接收状态机**：`siw_tcp_rx_data`（siw_qp_rx.c:1201）三态机从字节流切出 FPDU，查同一张表分派——WRITE 走 `siw_proc_write`（siw_qp_rx.c:566）：校验 STag/长度/访问位后**把载荷直接放置进目标注册内存，不消耗对端 RQ**。
7. **完成**：SIGNALED WQE 结束生成 CQE；连接异常时 `siw_cq_flush`（siw_cq.c:132）整队生成 FLUSH 错误完成。

变体：SEND 走 `siw_proc_send`（siw_qp_rx.c:457）匹配 RQ/SRQ 投递；READ 请求 `siw_proc_rreq`（:641）挂 IRQ 应答，响应 `siw_proc_rresp`（:765）核对 ORQ 后放置。

## 5. 关键模块深讲

### 5.1 siw_verbs.c：RDMA core 看到的全部面孔（1934 行）

31 个 ib_device.ops 回调。两个最重路径：

**`siw_create_qp`（siw_verbs.c:510，215 行）**：闸门——SIW_MAX_QP 配额（:526）、仅 RC（:531）、WR/SGE/inline 上限（:536-549，SGE 上限即 SIW_MAX_SGE=6）、SQ+RQ 须非零（:554）；`siw_qp_add` 入 idr（:585）；队列长度 `roundup_pow_of_two`（:589）；内核态 vmalloc、用户态 `vmalloc_user`（:592-595，mmap 共享环的前提）。

**`siw_reg_user_mr`（siw_verbs.c:1559-1648）**：SIW_MAX_MR 配额（:1578）→ RLIMIT_MEMLOCK 预检（:1588-1600）→ `siw_umem_get` 钉页 → `siw_alloc_mr` 入 idr → stag_key 直接 OR 进 lkey/rkey（:1622-1623，源码自带 XXX 注释），`STAG_VALID`（:1633）激活。配套 `siw_umem_get`（siw_mem.c:114）即替代 ib_umem_get 的自研实现：can_do_mlock（:120）、pinned_vm 记账（:138-143）、CHUNK_SHIFT 二维页表，核心 `get_user_pages`（siw_mem.c:163）。

### 5.2 siw_qp_tx.c：SQ 流水（1413 行）

**`siw_qp_sq_process`（siw_qp_tx.c:1040-1188）**是"取件-处理-完成-再取件"循环：互斥闸门 `wait_event(!in_use)`（:1048）；`tx_suspend` 置位即停（:1062）；`SIW_WQE_IS_TX` 区分线上发送与本地操作（:1068-1071）。三种退出：`rv==0` 完成——SIGNALED 生成 CQE，`siw_activate_tx` 取下一件（:1073-1109）；`-EAGAIN` 缓冲满暂停（:1111）；`-EINPROGRESS` 交 worker 接力（:1118-1119）。错误路径：READ 失败清 ORQ 槽（:1142-1146），`siw_qp_cm_drop`（siw_cm.c:385）降级断连并上报 QP_FATAL（:1156-1165）。MSS 预算由 `tx_ctx.tcp_seglen` 跟踪（siw.h:533）。

### 5.3 siw_qp_rx.c：接收状态机（1351 行）

**`siw_tcp_rx_data`（siw_qp_rx.c:1201-1351）**驱动整个接收侧。外层 `while (skb_new)` 消耗字节，`rx_suspend` 置位直接吞掉剩余（:1219-1223）——SEND 无 RQ 匹配时的背压。内层三态：**GET_HDR**（:1226）凑齐 FPDU 头、CRC 协商开启则验头（:1229）、算载荷预算与对齐 pad（:1234-1243）；**GET_DATA_START/MORE**（:1247-1275）按 opcode 调 `proc_data` 处理器，返回 0 转 TRAILER，缺数据停在 MORE（:1256）；**GET_TRAILER**（:1277）收 CRC+pad，DDP_FLAG_LAST 置位则 `siw_rdmap_complete` 结算整条消息（:1290-1296）。错误处理：注释明写 TERMINATE 优雅处理是 TODO（:1308），协议错误直接 `siw_qp_cm_drop(qp,1)` 断连（:1339）。SEND_INVAL/SEND_SE_INVAL 走 `siw_proc_unsupp`（:855），但**SEND_SE 实际绑定 siw_proc_send**（siw_qp.c:131-132）。

## 6. 设计决策：软件实现 iWARP 的得与失

- **帧格式的软件代价**：硬件把 DDP/RDMAP 头解析做成管线一级，siw 摊在两个软件状态机里——TX 每 FPDU 查表+续传游标，RX 在 TCP 字节流上跑三态机还原帧边界（TCP 不保消息边界，正是 MPA 层存在的理由：长度前缀+CRC trailer）。`iwarp_pktinfo`（siw_qp.c:80）一张静态表同时服务收发。
- **MPA 减配**：MPA Marker 明确缺失（IMPLEMENTATION.txt:119-120）——TCP 已是可靠字节流，半关闭重同步场景几乎不发生。
- **kthread 为主、workqueue 为备**：`USE_SQ_KTHREAD` 在 siw.h:542 **默认 #define**，编译期即选定 per-CPU 内核线程路径；workqueue 备选被 `#ifndef` 排除（siw_qp_tx.c:1212）。**警示："USE_SQ_KTHREAD 是死代码"说法是错的——真正从未定义的是 SIW_TX_FULLSEGS**（第 8 节）。
- **sendpage 实验性**（IMPLEMENTATION.txt:39-55）。
- **自研 umem**：公共设施成瓶颈时提供者自研是正当选项，代价是与主线演进脱钩。

## 7. 新人学习路径：按 15 步 tour

- **第一天（t01-t04）**：README+IMPLEMENTATION.txt+版本史；浏览 `common/siw_user.h`；`iwarp.h` 对照 RFC 过一遍 wire 结构。
- **第一周（t05-t08）**：siw_main.c 跟模块加载到设备注册；siw_obj.c 的 idr+kref；精读 siw_umem_get；siw_verbs.c 先啃 create_qp 与 reg_user_mr。
- **第二周（t09-t12）**：siw_cm.c 跟 connect→MPA 握手→socket 移交 QP；吃透 iwarp_pktinfo 与 siw_qp_modify（siw_qp.c:382）；深钻 siw_qp_sq_process 与 siw_tcp_rx_data 两条主循环。
- **第三周（t13-t15）**：debugfs 实测；userlib/src/siw.c:211 constructor 自注册；对照 siw_uverbs.c 快路径与 siw_doorbell 接通零 syscall 链路。练习：在 siw_tcp_rx_data 三个 case 加 dprint 跑 perftest。

## 8. 已知坑与勘误

1. **Kbuild 笔误**：`siw-objs` 列表 `siw_cm.o` 出现两次（kernel/Kbuild 第 4、5 行），构建自动去重。
2. **SIW_TX_FULLSEGS 才是死代码**：全仓 0 处 #define，4 处 #ifdef 永假——siw_qp.c:276 与 siw_qp_tx.c:805/818/954。USE_SQ_KTHREAD 在 siw.h:542 默认定义、是活代码（第 6 节）。
3. **图谱 52 函数盲区已回补**：tree-sitter 静态提取漏 52 个函数，构建时人工回补；`siw_cm_exit`（siw_cm.c:1946）void 返回漏建已补回。
4. **SEND_SE 分派**：SEND_INVAL/SEND_SE_INVAL 走 unsupp，但 SEND_SE 走 siw_proc_send（siw_qp.c:131-132）。
5. **lkey/rkey 同源**：同一 stag_key OR 进两 key（siw_verbs.c:1622-1623）。
6. **新内核编译预期失败**：基线 2.6.36.2，5.x 上撞 OFA 接口演进；活代码在内核主线。
7. **词汇陷阱**：ORQ/IRQ（outbound/inbound read queue）是 READ 操作两半，与中断无关；RQE/SQE/CQE 分别指 RQ/SQ 请求结束与入 CQ 环事件。
