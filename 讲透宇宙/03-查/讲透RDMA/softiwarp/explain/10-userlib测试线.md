# 10 · userlib 测试线：从 constructor 到 doorbell，用户态如何驱动内核路径

> 仓库 zrlio/softiwarp @ 5d8a418 · 本文行号锚全部经源码核实

## 一、角色定位

userlib/ 是 libsiw——挂进 libibverbs 框架的用户态提供者（provider）库，215 行的 siw.c 加上 siw_uverbs.c/siw_verbs.c 两个 490 行文件。它回答一个工程问题：**没有 PCI 设备的"假 RNIC"，用户态库该长什么样**。答案分两层：慢路径（建 PD/MR/CQ/QP 等资源管理）经标准 ibv_cmd_* 系统调用进内核；快路径（post_send/poll_cq）按内核暴露的 `if_type` 二选一——OFED 模式仍走 syscall，或 **mapped 模式直接写内核共享的 SQ/RQ/CQ 环**，整个提交只剩一次 doorbell。本仓 README.md:7-9 已声明此版仅作历史参考，但它作为**被 perftest/rdma_cm 类标准 RDMA 工具照常驱动的完整样本**，是验证内核路径的天然测试线：任何 ibverbs 程序都是它的测试程序。

## 二、内部结构

**装载链（siw.c，库加载即注册）**：`siw_register_driver`（siw.c:211-214）带 `__attribute__((constructor))`——**进程加载 libsiw.so 的瞬间**（而非首次调用）就向 libibverbs 报名"siw"驱动名。之后 ibv_get_device_list 遍历系统 /sys/class/infiniband 时，libibverbs 对每个设备调各 driver 的 init。`siw_driver_init`（:152-209）做三段握手验证：读 sysfs `ibdev` 文件得设备名（:167-174），拼出 /sys/class/infiniband/<name> 路径后读 `node_desc` 必须以 "Software iWARP stack" 开头（:176-182，SIW_NODE_DESC_COMMON，common/siw_user.h:53）——**软件设备没有 vendor/device ID 可验，字符串即身份**；再读 `sw_version` 对 `VERSION_ID_SOFTIWARP`（=2，common/siw_user.h:57）严判相等、`if_type` 必须 0/1（:184-198）——**版本不符直接拒载**，防止新用户库配老内核的 ABI 错配。

**context 双模式（siw.c:83-138）**：`siw_alloc_context` 经 ibv_cmd_get_context 拿内核响应（含 `resp.siw.dev_id` 与 **`rdma_db_nr`**——专有 doorbell 系统调用号，:104-105 存全局），然后按 driver_init 时记下的 if_type 给快路径装不同函数表：SIW_IF_OFED（:113-120）→ post_send/post_recv/poll_cq 全走 ibv_cmd_*；SIW_IF_MAPPED（:122-129）→ 装 siw_post_send_mapped 等直写版本。慢路径 ops（alloc_pd 到 req_notify_cq，:59-81）两种模式共享，都进 siw_verbs.c（用户态侧）的 ibv_cmd 封装。

**ABI 契约（siw_abi.h + common/siw_user.h）**：内核 uverbs 响应结构尾部叠加 siw 私有字段——alloc_pd_resp 多 pd_id、create_cq_resp 多 cq_key/cq_id/num_cqe、create_qp_resp 多 sq_key/rq_key 等（siw_abi.h:47-88）。**内核 key → 用户 mmap 地址**的翻译在 siw_verbs.c（用户态）的 create 流程里做：拿到 cq_key 后按 siw_umem 式偏移映射出 `cq->queue/ctrl` 指针。common/siw_user.h 是**两侧唯一共享头**：siw_sqe/siw_rqe/siw_cqe 布局、SIW_WQE_VALID/SIGNALLED/SOLICITED 标志位、notify 枚举——mapped 模式的全部正确性押在这份布局契约上。

**mapped 快路径（siw_uverbs.c）**：`push_send_wqe`（:161-239）把 ibv_send_wr 翻成 siw_sqe——flags 映射（:151-156，IBV_SEND_INLINE→SIW_WQE_INLINE 等）、INLINE 数据 memcpy 进 SQE 尾部（:172-190，上限 SIW_MAX_INLINE）、单 SGE 快通道（:192-196）、多 SGE 依赖"siw 与 ofa SGE 布局相同"的假设直接 memcpy（:197-199，注释自曝）。`siw_post_send_mapped`（:247-300）：pthread_spin 持 qp->sq_lock → 沿环找空槽（`!(sqe_flags & SIW_WQE_VALID)` :268-269）逐个 push → **doorbell**：`rdma_db_nr > 0` 则 `syscall(rdma_db_nr, SIW_DB_SQ, dev_id, qp_id)`（:288-291）直入内核 siw_doorbell_sq（siw_verbs.c:920）；否则退化为 `siw_db_ofa`（:218-244）——**发一个 wr_count=0 的空 IB_USER_VERBS_CMD_POST_SEND 写 cmd_fd**，内核 post_send 入口被空请求唤醒后顺带扫描 SQ。poll_cq_mapped 同理直读共享环维护用户侧 cq_get；notify（:71-73）直接 `_store_shared(cq->ctrl->notify, ...)` 写共享内存（08 篇的握手用户侧半场）。

**构建链**：autogen.sh → configure（autotools）→ Makefile.am 产 `src/libsiw.la`（三源文件 :18），`-release @IBV_DEVICE_LIBRARY_EXTENSION@` 让产物名带 providers 后缀（libsiw-rdmav2.so），**siw.driver 文件装到 $(sysconfdir)/libibverbs.d/**（:29-30）——内容就一行 `driver siw`（siw.driver），告诉 libibverbs 按设备 ABI 名加载 libsiw。

## 三、外部连接

上游：libibverbs 框架（ibv_register_driver/ibv_cmd_* 与 completion channel 的 fd 协议）；一切标准 RDMA 应用——perftest、rdma_cm、ibverbs-examples，乃至 diags 工具。下游经两种 syscall 进内核：uverbs 命令通道（/dev/infiniband/uverbsN 的 write，对应 siw_main.c:388-412 的 uverbs_cmd_mask 白名单 23 条）与 doorbell（若有 rdma_db 补丁内核，IMPLEMENTATION.txt:96-99 自述该 syscall **不随本软件分发**，是实验内核补丁）。测试视角的全链：`ibv_get_device_list→driver_init 验签 → open_device→alloc_context 拿 db_nr → create_qp（内核建 QP+发 key）→ mmap SQ/CQ → post_send：写共享环+doorbell → 内核 TX 线程跑 05 篇流水 → CQE 写共享环 → poll_cq 用户态收割`。

## 四、数据流

以 perftest 一次 WRITE 为例的两侧分工：**用户态**（零 syscall 除 doorbell）：translate_wr → push_send_wqe 写 SQE（VALID 发布）→ syscall db。**内核态**：siw_doorbell_sq 在**调用者上下文**直接跑一轮 siw_qp_sq_process（省 kthread 唤醒延迟，05 篇①入口）→ 错误/未竟部分交 kthread。完成回流：CQE 由内核 smp_store_mb 发布 → 用户 poll_cq_mapped 读 `cq->queue[cq_get % num_cqe]` 的 VALID 位 → 翻译成 ibv_wc → 清 flags 推 cq_get。**每一跳的同步全靠共享内存标志位+屏障**，两侧唯一强约定是 common/siw_user.h 的结构布局。

## 五、设计决策

1. **sysfs 字符串验签代替 PCI ID**：软件设备无总线身份，node_desc+版本号是唯一可验指纹；顺带完成"用户库-内核模块"版本配对检查（老内核配新库必拒）。
2. **双 if_type 而非单快路径**：mapped 模式依赖 mmap 与共享环语义，保守部署可回退纯 syscall 模式——一套库两种部署形态，由内核模块在 sysfs 暴露的 if_type 单点决定（内核侧 siw.h:61-62 同枚举）。
3. **空命令当 doorbell**：无专有 syscall 的内核上，wr_count=0 的 POST_SEND 是合法唤醒手段——复用现有 uverbs 入口，零内核改动；代价是每次 doorbell 一次完整 syscall 进出。
4. **布局假设显式化**：SGE 直接 memcpy 依赖两侧结构一致（:198 注释）——common 头单点维护让假设可审计，但任何一侧私自改布局都会静默错乱。
5. **constructor 注册**：注册发生在 main 之前，应用无需显式 init——libibverbs 生态的惯例做法，保证 ibv_get_device_list 一定能看到 siw。

## 六、新人提示

1. 验证库是否被加载：`IBV_DRIVERS=siw`（或看 /etc/libibverbs.d/siw.driver）+ `strace` 应用看是否 open libsiw*.so；设备名形如 siw_eth0（内核 SIW_IBDEV_PREFIX+网卡名）。
2. mapped 模式调试抓不到 post_send syscall 是**正常现象**——断点应设在内核 siw_doorbell_sq 或 siw_qp_sq_process；纯 OFED 模式才见 write(cmd_fd, IB_USER_VERBS_CMD_POST_SEND)。
3. **本仓的测试程序就是任何 ibverbs 程序**：最简冒烟=ibv_devinfo（只走慢路径）；要触发快路径跑 perftest（ib_write_bw），并确认内核 sysfs if_type=1。
4. rdma_db_nr 需要打过 doorbell 补丁的内核；主线无此 syscall 时全局恒 -1，自动退化 siw_db_ofa——看到"空 POST_SEND"流量别当 bug。
5. 动手：在 push_send_wqe 的 siw_debug 打印处开 `extern const int siw_debug`（siw.c:57），链接期置 1 重编，可看到每次 post 的 SQE 五元组——最便宜的用户态探针。

📌 下一篇：11 篇做考古——死代码、条件编译与构建文件的层积岩，哪些分支永远到不了。
