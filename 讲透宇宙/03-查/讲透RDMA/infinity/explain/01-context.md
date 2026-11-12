# 01 Context——verbs 资源中枢：一个对象管住设备、PD、双 CQ 与 SRQ

> 源文件：`src/infinity/core/Context.h`（167 行）/ `src/infinity/core/Context.cpp`（225 行）

## ① 角色定位

Context 是全库唯一"持家"对象：RDMA 的 verbs 资源有严格的从属与生命周期——设备要先 `ibv_open_device`、保护域（PD）挂在设备上、内存注册挂在 PD 上、QP 又引用 PD 与 CQ。infinity 把这些原料收进 Context 一处持有、按依赖序创建销毁，其余模块一律经它取料。它处于 12 层架构的 L02（Context.h:50），是内存线（L03-L07）与队列线（L09-L10）共同的根依赖；图谱中 `class:src/infinity/core/Context.h:Context` 被 7 个类消费，全库入度最高。

## ② 内部结构

**公共面只有四件**（Context.h:77-88）：两个 `receive` 重载（取一条接收完成）、`postReceiveBuffer`（预挂接收缓冲）、以及两个公共槽 `defaultRequestToken`/`defaultAtomic`（Context.cpp:71-72 构造时创建，给 CAS/FAD 便捷重载与 send-performance 示例复用）。

**verbs 资源成员**（Context.h:139-154）：`ibvContext`（设备上下文）、`ibvProtectionDomain`、`ibvDevice`/`ibvLocalDeviceId`/`ibvDevicePort`、发送与接收两个完成队列 `ibvSendCompletionQueue`/`ibvReceiveCompletionQueue`、共享接收队列 `ibvSharedReceiveQueue`。

**保护面取料器**（Context.h:95-132）：getInfiniBandContext/getLocalDeviceId/getDevicePort/getProtectionDomain/getSendCompletionQueue/getReceiveCompletionQueue/getSharedReceiveQueue/pollSendCompletionQueue/registerQueuePair——全部 protected，靠 Context.h:52-58 的 **7 个 friend class**（Region/Buffer/Atomic/RegisteredMemory/QueuePair/QueuePairFactory/RequestToken）限定仅库内部可用。

**辅助类型**：`receive_element_t`（Context.h:42-48）为接收完成载荷（buffer 指针+字节数+immediate 值+来源 QP）；`queuePairMap`（Context.h:159）以 QPN 为键登记全部 QP。

## ③ 外部连接

**被谁用**：RegisteredMemory/Buffer/Atomic 构造时经 getProtectionDomain 注册 MR；QueuePair 构造取双 CQ+SRQ+PD（QueuePair.cpp:44-46/54）并回读端口/LID；QueuePairFactory 三入口结束时调 registerQueuePair 登记（QueuePairFactory.cpp:108/161/177→Context.cpp:191-193）；RequestToken 等待时回调 pollSendCompletionQueue（RequestToken.cpp:35/42）。示例第一步都是 `new Context()`（read-write-send.cpp:44）。

**依赖谁**：仅 Configuration.h（队列深度常量）与 utils/Debug.h；对上是 verbs API 的薄封装。

## ④ 数据流

**构造**（Context.cpp:31-74）：`ibv_get_device_list` 枚举并三重断言（:35-39）→ `ibv_open_device`（:46）→ `ibv_alloc_pd`（:48）→ `ibv_query_port` 取 LID（:53-54）→ 按 SEND/RECV_COMPLETION_QUEUE_LENGTH（各 16351，Configuration.h:25-27）建双 CQ（:58-59）→ 建 SRQ（:62-67，`sia.attr.max_sge = 1` 与全库 SGE=1 约束同源）→ 建 defaultRequestToken/defaultAtomic（:71-72）。默认 `device=0, devicePort=1`（Context.h:65），多网卡机器须显式指定。

**接收路径** receive（Context.cpp:135-167）：`ibv_poll_cq` 收一条 CQE（:138）→ 按 opcode 分流：IBV_WC_RECV（双边 send）把 wr_id 还原为 Buffer 指针交还用户（:140-142），**不自动重挂**，用户须再调 postReceiveBuffer（send-performance.cpp:71/87 即此模式）；IBV_WC_RECV_RDMA_WITH_IMM（单边写带通知）则 buffer 置 NULL 并**自动重挂回 SRQ**（:143-148）。immediate 值经 ntohl 转字节序（:151）；要来源 QP 时以 wc.qp_num 查 queuePairMap（:158-159）。

**postReceiveBuffer**（Context.cpp:102-127）：组装单 SGE 接收请求（addr/length/lkey 取自 Buffer），**wr_id 直接放 Buffer 指针**（:117），完成时靠它无损还原对象；`ibv_post_srq_recv` 挂入 SRQ（:124）。

**发送完成** pollSendCompletionQueue（Context.cpp:169-189）：轮询一条发送 CQE，wr_id 解释为 RequestToken 指针并 setCompleted（:174-176）——RequestToken 异步等待的底层泵。

**析构**（Context.cpp:76-100）：严格逆序——token/atomic→SRQ→双 CQ→PD→关设备。

## ⑤ 设计决策

**friend 包围圈代替 public**：verbs 句柄一旦裸露，用户层乱序销毁即内核资源泄漏；7-friend 方案让公开面缩到 4 个符号，库外代码碰不到 PD/CQ。代价是 friend 列表与模块清单强耦合——新增内存类必须改 Context.h。

**全局单 SRQ + 共享双 CQ**：所有 QP 共用一个 SRQ 与一对 CQ（QueuePair 构造直接绑定，QueuePair.cpp:44-46），接收缓冲一次挂入全连接可用——多连接接收侧零额外内存管理；代价是所有连接的完成事件混在一个 CQ，须靠 wr_id（Buffer/RequestToken 指针）与 qp_num 区分来源。

**非阻塞单条轮询**：receive/pollSendCompletionQueue 一次取一条、无事件即返回 false，等待策略（忙轮询/让出 CPU）交给上层——示例用 `while(!context->receive(...))` 忙等（read-write-send.cpp:64）。

**析构顺序契约不设防**：Context 析构不检查是否还有 QP 存活；QP 必须先于 Context 删除（read-write-send.cpp:99-101 正是此序），顺序错了默认编译下（断言被编译掉，Debug.h:21-24）是未定义行为。

## ⑥ 新人提示

上手顺序：先读构造函数看懂持有哪些原料，再跟 receive 走一条 CQE 的旅程，最后回看 friend 列表理解封装边界。三个坑：①receive 在 IBV_WC_RECV 分支把 Buffer 交还后**必须手动重挂**，忘了则 SRQ 干涸、对端 send 会 RNR 报错；②16351 深度看着大，但 fire-and-forget 堆积会 CQ 溢出；③默认 device=0/port=1，双端口网卡或多 HCA 机器连错网段是新手第一大坑，构造时显式传参。要断言生效需 `-DINFINITY_ASSERT_ON` 重编（Makefile 默认不加任何 -D）。
