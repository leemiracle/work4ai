# 05 QueuePair——通信原语全家桶：一个模板铸出全部 verbs 操作

> 源文件：`src/infinity/queues/QueuePair.h`（159 行）/ `src/infinity/queues/QueuePair.cpp`（590 行）

## ① 角色定位

QueuePair 处于 L09，全库体量最大、真正干活的文件：把 ibv_post_send 的全部写法封装成类型安全的 C++ 方法。覆盖面精确清点（以源码为准）：**9 个操作族、17 个公开重载、7 种 verbs opcode**——send×3（IBV_WR_SEND，双边）、write×3（IBV_WR_RDMA_WRITE）、read×3（IBV_WR_RDMA_READ）、multiWrite×1、sendWithImmediate×1、writeWithImmediate×1、multiWriteWithImmediate×1（IBV_WR_RDMA_WRITE_WITH_IMM）、compareAndSwap×2（IBV_WR_ATOMIC_CMP_AND_SWP）、fetchAndAdd×2（IBV_WR_ATOMIC_FETCH_AND_ADD）。导览材料"11 族"口径系把 CAS/FAD 的全量与便捷重载分立计数（7+2+2），本篇按方法名计 9 族。同文件还有 OperationFlags 值对象（QueuePair.h:29-42）。向上承接 Buffer（本地内存）与 RegionToken（远端凭证），向下只碰 ibv_post_send/ibv_modify_qp 两个 verbs 入口。

## ② 内部结构

**OperationFlags**（QueuePair.h:29-42）：fenced/signaled/inlined 三布尔，ibvFlags() 折成 IBV_SEND_FENCE/IBV_SEND_SIGNALED/IBV_SEND_INLINE 位掩码（QueuePair.cpp:24-36）。

**生命周期**：构造建 QP 转 INIT（QueuePair.cpp:38-75）；activate/setRemoteUserData 是 protected（QueuePair.h:66-67），仅 friend QueuePairFactory（QueuePair.h:46）可调——**连接协商是工厂职权，QP 自己不碰网络**；析构 ibv_destroy_qp（:79）。

**四组操作**（QueuePair.h:95-141）：send/write/read 各三重载（便捷版收 Buffer+token，全量版收 offset/size/flags）；复杂组四方法（multiWrite/sendWithImmediate/writeWithImmediate/multiWriteWithImmediate）；原子组 CAS/FAD 各两重载（便捷版免传 previousValue，自动用 context->defaultAtomic，QueuePair.cpp:529/533）。

**信息面**：getLocalDeviceId/getQueuePairNumber/getSequenceNumber（QueuePair.cpp:133-143）与 userData 三访问器（:576-586）。

## ③ 外部连接

**依赖**：Context 供 PD/双 CQ/SRQ/端口/LID（QueuePair.cpp:44-46/54/62/104）；Buffer 供 addr/lkey；RegionToken 供 remote_addr/rkey；RequestToken 供完成回执；Configuration 供队列深度与 SGE 上限（:47-50）。

**被谁用**：QueuePairFactory 三入口都 `new QueuePair` 后 activate（QueuePairFactory.cpp:89/138/173）；示例的全部通信动作都落在它身上（read-write-send.cpp:83/87/91；send-performance.cpp:97/118/137/142）。图谱中 QueuePair.cpp 是入边最多的实现文件（六处依赖）。

## ④ 数据流

**构造→INIT**（QueuePair.cpp:38-75）：RC 型（IBV_QPT_RC，:51，可靠连接是单边原语前提）+ 绑定 Context 的共享 CQ/SRQ（:44-46）+ max_send/recv_sge=MAX_NUMBER_OF_SGE_ELEMENTS（:48/50）→ ibv_create_qp（:54）→ 转 INIT 开四权限含 REMOTE_ATOMIC（:60-65）→ random_device 掷 24bit 随机 PSN（:69-71）。

**activate→RTR→RTS**（QueuePair.cpp:89-123）：RTR 填对端三元组（dest_qp_num/rq_psn/dlid，:94-104），RTS 填本端 PSN 与重试参数（:111-116）。全参数硬编码：path_mtu=4096（:95）、min_rnr_timer=12（:99）、timeout=14/retry_cnt=7/rnr_retry=7（:112-114）、**max_rd_atomic=1（:98/:116）——单 QP 在途 read/atomic 仅 1 个**，read 密集负载此值即瓶颈。

**统一模板**（以 write 全量版为例，QueuePair.cpp:241-282）：①token 非 NULL 则 reset+setRegion（:244-247）；②组装单 ibv_sge（addr=buffer 地址+localOffset、length、lkey，:253-256）；③组装 ibv_send_wr：wr_id=token 指针（:262）、opcode 定族别（IBV_WR_RDMA_WRITE，:265）、token 非 NULL 强制 IBV_SEND_SIGNALED（:267-269）；④单边专属：remote_addr=token 地址+remoteOffset、rkey（:270-271）；⑤防御断言（本地越界 :258、远端越界 :273）；⑥ibv_post_send（:276）。17 个重载全是此模板的参数替换——multiWrite 只是把 SGE 换成 calloc 数组循环填充（:337/344-357）。

**原子组**：CAS 把 compare/swap 填进 wr.atomic（QueuePair.cpp:517-518），FAD 把加数填 compare_add（:564）；**原值落点**是本地 Atomic 缓冲（previousValue 作 SGE 目标，:502-504/549-551）——网卡把旧值 DMA 回来，CPU 零参与。

**异步等待**：wr_id 随请求进硬件，CQE 回来时 Context::pollSendCompletionQueue 按 wr_id 找到 token 调 setCompleted（Context.cpp:174-176）；waitUntilCompleted() 忙轮询该泵（RequestToken.cpp:40-44）。token=NULL 且未置 signaled 时无 CQE——fire-and-forget，send-performance.cpp:142 每 128 条才同步一次即此技巧。

## ⑤ 设计决策

**复制粘贴式统一**：17 个方法共享同一套 30 行模板却各自展开，不抽公共 buildWr 函数——牺牲 DRY 换每方法直读可调试性（学术库风格，零共享状态）。

**signaled 与 token 绑定**：要完成通知就必须给 token（强制 SIGNALED，:179-181），无 token 默认静默——"在途控制"旋钮交给调用者，库不搞隐藏同步。

**硬编码传输参数**：MTU/重试/在途深度全写死，换网络（RoCE 需 GRH 但 is_global=0，:100）或调优都要改源码重编——原型定位：单 IB 集群、质量优先。

**multiWrite 的 SGE=1 名不副实**：代码支持 N 段聚合（QueuePair.cpp:329-379），但 Configuration.h:35 `MAX_NUMBER_OF_SGE_ELEMENTS=1` 使 :341/:394 断言在默认编译下（被编译掉）直接越界 UB——真用多段须改常量重编，QP 构造的 max_send_sge（:48）同源限制。

## ⑥ 新人提示

上手顺序：先 ctor+activate 理解 QP 状态机（INIT→RTR→RTS 是 verbs 入门必修），再精读 write 全量版这一个模板，其余 16 个重载触类旁通。五个坑：①write/read 便捷重载把 uint64 的 buffer 尺寸**隐式截断**成 uint32 参数后才执行、事后再断言（QueuePair.cpp:233/:438）——>4GB buffer 默认编译下静默截断；②便捷 CAS/FAD 共享 context->defaultAtomic，多线程并发用便捷重载互踩落点，须自带 previousValue；③wr_id 是裸指针回传，token 必须存活到 CQE 被轮询——栈上 RequestToken 在 wait 前返回是典型悬垂；④fire-and-forget 堆积会撑爆 16351 深的 CQ；⑤inlined 要求消息 ≤ 网卡 inline 阈值（常见几十字节），超限 post 失败。
