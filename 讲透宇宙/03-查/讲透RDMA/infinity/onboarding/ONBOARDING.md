# infinity ONBOARDING——RDMA 单边通信原语库中文导览

> claudebarthels/infinity @ c6cbbbf · 12 层/15 步 tour · 锚经源码核实（2026-11-12）

## 1. 项目定位：单边通信原语为什么值得一个库

Claude Barthels（ETH Zurich）为 RDMA join 研究打造（SIGMOD 2015/VLDB 2017，README.md:54-65）的 C++ ibVerbs 轻量封装——数百行样板压成「Context+Region+QueuePair」。两类通信：

- **双边**：send/receive，接收方先 post 接收缓冲，报文 DMA 进对端内存产生 CQE。
- **单边**：read/write/atomic，凭对端 RegionToken（地址+rkey）直接读写远端注册内存，**远端 CPU 零参与**。

PS/大规模训练同款：pull=read、push=write 不打断 server CPU；计数器与无等待同步用网卡原子 compareAndSwap/fetchAndAdd（QueuePair.cpp:489/536）——远端不参与就没有远端瓶颈，库只给最薄单连接原语、做上层框架地基层。

## 2. 快速上手

```sh
make library    # 需 libibverbs-dev；产出 release/{libinfinity.a,include/}
make examples   # release/examples/ 两示例
```

Makefile:29-38 列 10 cpp、:40-53 列 14 头、`-O3 -std=c++0x`（:16）、ar 归档（:74-79）、示例链接（:91-92）。

双机：A 机 `read-write-send -s`（判定 read-write-send.cpp:29-42，端口 8011:21），B 机去 `-s` 并改源码 SERVER_IP。接入 `#include <infinity/infinity.h>`（infinity.h:12-24）+libinfinity.a -libverbs。

## 3. 架构总览：12 层从外到内

25 文件 12 层，依赖单向：L01 构建与配置（Configuration.h:25-47）·L02 Context 资源中枢（Context.h:50）·L03 ibv_reg_mr 封装（RegisteredMemory.cpp:20-47）·L04 已注册内存视图（Region.h:23）·L05 远端寻址凭证（RegionToken.h:19）·L06 内存载体（Buffer.h:19）·L07 8 字节原子槽（Atomic.h:21）·L08 请求句柄（RequestToken.h:21）·L09 11 族原语核心（QueuePair.cpp:38）·L10 TCP 带外引导（QueuePairFactory.cpp:33）·L11 教程+基准（read-write-send.cpp:25）·L12 barrel 门面（infinity.h:9）。

三主线：**内存线** RegisteredMemory→Region→Buffer/Atomic→RegionToken（内存如何被触达/寻址）；**队列线** Context→QueuePair→Factory（发出与对账）；**请求线** RequestToken 以 wr_id 挂工作请求、完成按 wr_id 回填。

Context.h:52-58 以 **7 个 friend class** 限定 PD/CQ/SRQ/registerQueuePair/pollSendCompletionQueue 仅内部可用，公开面仅 receive+postReceiveBuffer+两公共槽（Context.h:85-88）。

## 4. 核心链路：read-write-send

**① 初始化**：`new Context()`（read-write-send.cpp:44）→ 设备/PD（Context.cpp:35-49）、LID（:52-54）、双 CQ（:58-59）、SRQ（:62-68）、公共槽（:71-72）。

**② 注册与凭证（server）**：`new Buffer(context, 128)`（:51）→ posix_memalign（Buffer.cpp:28）→ ibv_reg_mr 三权限注册生成 rkey（:33-34）；`createRegionToken()`（:52）快照五元组（Region.cpp:21-23）；postReceiveBuffer 预挂 SRQ（read-write-send.cpp:56→Context.cpp:102-127）。

**③ QP 建立（TCP 带外）**：server `bindToPort(8011)`（:59）+`acceptIncomingConnection(bufferToken, sizeof(RegionToken))`（:60）——**RegionToken 原始字节**当握手数据；client `connectToRemoteHost`（:73）。TCP 交换三元组+数据（QueuePairFactory.cpp:23-31），activate 推 RTR/RTS（QueuePair.cpp:89-123），client 由 `(RegionToken*) qp->getUserData()`（:74）得远端寻址。

**④ 三原语与等待（client）**：read/write/send 依次 :83/:87/:91，opcode 对应 QueuePair.cpp:470（RDMA_READ，addr/rkey 取 token :475-476）/:265（RDMA_WRITE）/:177（SEND，双边）。每操作 reset+setRegion 塞令牌进 wr_id（QueuePair.cpp:156-159/:174）；`waitUntilCompleted()`（:84/:88/:92）忙轮询（RequestToken.cpp:40-44→Context.cpp:169-189）；server `receive` 忙等（read-write-send.cpp:63-64→Context.cpp:135-167）。

send-performance 每 128 消息才同步、余 NULL 即忘（send-performance.cpp:134-144）——NULL 不产 CQE，窗口式在途控制基础。

## 5. 关键模块深讲

### 5.1 Region 继承树（Region.h:23→Buffer.h:19/Atomic.h:21）

Region 是根，七访问器暴露地址/lkey/rkey（Region.h:45-47/:51-52，Region.cpp:41-59）；createRegionToken 三重载（Region.cpp:21-31）=全量/偏移/定长快照。

- **Buffer** 三构造=三种所有权：自分配+注册（Buffer.cpp:22-40）；切 RegisteredMemory 视图复用 ibv_mr（:42-54）；只注册外部内存（:56-70）。析构按标志 dereg/free（:72-81）；resize :108 断言只许自注册内存（:87-110）。
- **Atomic**：构造把 `uint64_t value`（Atomic.h:36）全权限注册为 8 字节区（Atomic.cpp:16-29）；getValue/setValueNonAtomic（:31-41）是裸读写**无原子语义**，原子性在网卡 compareAndSwap/fetchAndAdd（QueuePair.cpp:510/:557）。

### 5.2 QueuePairFactory：accept/connect/loopback

QP 建立需交换 LID/QPN/PSN 而交换尚无 RDMA——TCP 带外解决；三入口（QueuePairFactory.h:35/40/45）：

- **bindToPort+accept（被动）**：bindToPort（QueuePairFactory.cpp:48-72）建 socket+打印 IP（:68，Configuration.h:47 "ib0"）；accept（:74-116）：recv 三元组（:85）→new QueuePair（:89，RC 型+随机 PSN，QueuePair.cpp:51-71）→send 回三元组+数据（:91-97）→activate（:105）/setRemoteUserData（:106）/登记（:108→Context.cpp:191-193）。
- **connectToRemoteHost（主动）**（:118-169）：connect（:129-136）后**先 send 后 recv**（与 accept 互补防死锁），:158-161 activate+登记。
- **createLoopback**（:171-181）：自三元组 activate 自己（:174），同进程自测最短路径。

activate 硬编码（QueuePair.cpp:94-116）：path_mtu=4096（:95）、min_rnr_timer=12（:99）、timeout/retry=14/7（:112-114）、**max_rd_atomic=1（:116）——单 QP 在途 read/atomic 仅 1**，read 密集须调大重编。

### 5.3 QueuePair：一个模板吃遍 11 族

11 族（QueuePair.h:95-141）：send/write/multiWrite 各含 WithImmediate 变体+read/compareAndSwap/fetchAndAdd，统一模板：ibv_sge→ibv_send_wr（wr_id=RequestToken，QueuePair.cpp:174，opcode 定族别）→ibv_post_send（:183）。OperationFlags（QueuePair.h:29-42）折位掩码（QueuePair.cpp:24-36）；token 非 NULL 强制 IBV_SEND_SIGNALED（:179-181）。activate/setRemoteUserData 仅 friend QueuePairFactory（QueuePair.h:46/66-67）。

## 6. 设计决策：三个取舍

**① RegionToken 是独立 const 快照非子类。** RegionToken.h:39-44 五字段全 const——不可变值快照，与 verbs 零交互；继承图仅 Buffer/Atomic 两条边；跨机传递需可拷贝平数据非多态。默认构造（RegionToken.cpp:14-24）全零 UNKNOWN 备按字节重建。

**② 指针 RegionToken 的 POD memcpy hack。** read-write-send.cpp:60 把 token **整对象按 sizeof memcpy 进握手**，client :74 重铸——零序列化。前提：无虚函数+可平凡拷贝；`Region*` 回指（RegionToken.h:39）在对端**悬垂**，全库靠「QP 路径不解引用」纪律兜住。代价：跨 ABI 脆弱。

**③ multiWrite 的 SGE=1 约束。** 名义聚合多段一次 post（QueuePair.cpp:329-379），但 Configuration.h:35 `MAX_NUMBER_OF_SGE_ELEMENTS=1`，:341/:394 断言——**默认传 >1 必失败**（断言被编译掉则越界 UB，见坑①）；max_send/recv_sge 同此常量（QueuePair.cpp:48/50），真用须改重编。

## 7. 新人学习路径：按 15 步 tour 走

**一·动机与形态（步 1-2）**：README 背景→Makefile→make 产出。

**二·内存线（步 3-8）**：Context→RegisteredMemory→Region→RegionToken→Buffer→Atomic；吃透 token 铸出（Region.cpp:21-31）、Buffer 所有权（Buffer.cpp:22-70）、Atomic 原子性在网卡。

**三·队列线（步 9-13）**：RequestToken→QueuePair 11 族→单边→双边+网卡原子→Factory 三入口；对照 read-write-send.cpp:73-92 把每行映射到 opcode。

**四·收尾（步 14-15）**：跑通示例→send-performance.cpp:134-144 的 128 窗口→createLoopback（QueuePairFactory.cpp:171-181）写自测程序→回看 barrel。

验收：默画 12 层图；说出原语调用到 CQE 的路径；解释 memcpy hack 前提。

## 8. 已知坑与勘误

**坑① Debug.h 双宏：默认编译下 INFINITY_ASSERT 全被编译掉。** 两宏分别受 INFINITY_DEBUG_ON/INFINITY_ASSERT_ON 控制（Debug.h:15-19/:21-25），无宏时均空 `{}`；**Makefile 无任何 -D**——默认零断言：multiWrite（QueuePair.cpp:341/:394）、resize（Buffer.cpp:108）等断言静默失效，违规输入即 UB。调试加 `-DINFINITY_ASSERT_ON` 重编。

**坑② README 快速上手代码不可编译。** README.md:29 `new RegionToken(REMOTE_BUFFER_INFO)`：REMOTE_BUFFER_INFO 源码零定义，RegionToken 只有默认/六参构造（RegionToken.h:23-24）；真实获取靠握手+`getUserData()` 强转（read-write-send.cpp:60/:74），以示例为准。

**坑③ RegisteredMemory.cpp 尾注释旧项目名残留。** 头部实为 `namespace infinity { namespace memory {`（RegisteredMemory.cpp:17-18），尾部却写 `} /* namespace pool */ } /* namespace ivory */`（:78-79）——ivory 是前身代号。

**坑④ 图谱口径：scanner 对 .h include 盲区约 32 条系手补。** 173 边含 imports 72，头文件间 #include 约 32 条系重扫补录。存疑边回源码 grep `#include` 复核。
