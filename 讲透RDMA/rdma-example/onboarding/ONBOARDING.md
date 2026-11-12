# rdma-example 新人上手指南（ONBOARDING）

> 仓库：animeshtrivedi/rdma-example（本地 `/usr-data/data2/kylin/network/rdma/rdma-example`，commit `615b85d2`）。行号锚均经源码核实（2026-11-11）。

## 1. 项目定位

Animesh Trivedi（src/rdma_common.h:5）的**极简 RDMA 教学示例**，社区最流行入门代码。聚焦演示 Linux 两大用户态 API：**rdma_cm**（连接管理，librdmacm）与 **ibverbs**（数据面，libibverbs）——把建连、注册内存、交换元数据、单边读写、清理全生命周期压进两个注释极密的程序。

生态位置：向下依赖内核 RDMA 栈（或 SoftiWARP）与两库（CMakeLists.txt:25-28）；perftest 测性能，本仓**教 API 语义**。教学主角是 RDMA 本质卖点**单边操作**：客户端用 `IBV_WR_RDMA_WRITE/READ`（src/rdma_client.c:333、L364）凭授权直接读写服务端内存，对端 CPU 零参与；"SEND/RECV 双边换元数据 + 单边搬数据"即 NCCL/SPDK 等 RDMA 层的标准配方骨架。

## 2. 快速上手

```bash
sudo apt install libibverbs-dev librdmacm-dev cmake build-essential
cd rdma-example && cmake . && make          # 产物在 bin/（README.md:23-28）
./bin/rdma_server                            # 终端 1，默认 0.0.0.0:20886（src/rdma_server.c:438,461）
./bin/rdma_client -a 127.0.0.1 -s textstring # 终端 2，-s 必填
```

输出以 `SUCCESS, source and destination buffers match`（src/rdma_client.c:545，完整样例 README.md:36-46）收尾——字符串经 WRITE 写到服务端、READ 读回第二个本地缓冲后 memcmp 一致（src/rdma_client.c:31-34）。**无网卡**：README.md:50-51 指路 SoftiWARP，普通网卡可模拟跑通。

## 3. 架构总览

三层分工：**公共底座 rdma_common + 被动方 rdma_server + 主动方 rdma_client**。图谱 9 层：

| 层 | 名称 | 职责 |
|---|---|---|
| L01 | 构建文档 | CMake 两目标（CMakeLists.txt:32-33）；README 流程 |
| L02 | 公共契约 | rdma_common.h；线格式 rdma_buffer_attr（src/rdma_common.h:61-70） |
| L03 | MR 四件套 | alloc/register/deregister/free（src/rdma_common.c:40-105） |
| L04 | 事件原语 | CM 事件（src/rdma_common.c:107-138）、CQ 完成（L141-193） |
| L05 | 地址调试 | get_addr（src/rdma_common.c:197-209）、show_*（L10-38） |
| L06 | 服务端建连 | listen/建 QP（src/rdma_server.c:127-197、L33-124）、预挂后 accept（L200-274） |
| L07 | 服务端数据面 | 发授权/断连回收/main（L277-357、L361-421、L432-489） |
| L08 | 客户端建连 | resolve/预挂/connect（src/rdma_client.c:37-173、L176-203、L206-236） |
| L09 | 客户端数据面 | 交换/单边写读/清理/main（L243-302、L309-388、L393-454、L463-552） |

两端互不引用、只靠线格式耦合，各以文件级 static 持全套资源指针（src/rdma_server.c:14-26、src/rdma_client.c:11-28）。

## 4. 核心链路

```text
服务端                           客户端
start_rdma_server (L127-197)     client_prepare_connection (L37-173)
  bind (L149) listen (L160)        resolve_addr/route (L61,84)→各等一事件
  等CONNECT_REQUEST (L173)
setup_client_resources (L33-124)    分PD (L110) CQ (L135) RC型QP (L163)
accept_client_connection (L200-274) pre_post_recv (L176-203) 预挂 (L194)
  注册元数据 MR (L211)              connect_to_server (L206-236)
  预挂 receive (L229)【先于accept】  rdma_connect (L215)→等ESTABLISHED (L221)
  rdma_accept (L244)→等ESTABLISHED ◄─ 建连 ─►
send_server_metadata (L277-357)   xchange_metadata (L243-302)
  等收 client 元数据 (L286)          注册 src (L247)、SEND 三元组 (L281)、等 2 WC (L292)
  按请求长度 alloc 缓冲 (L298)、SEND remote_memory_ops (L309-388)
  服务端三元组 (L341)                 注册 dst (L313)；WRITE (L333-341)；
disconnect_and_cleanup (L361-421)    READ (L364-370)；memcmp (L33)
  等DISCONNECTED (L367)→逆序销毁    [服务端零参与] disconnect→清理 (L398,418)
```

四个要紧时序点：①**预挂接收先于建连**（src/rdma_server.c:211-231、src/rdma_client.c:179-196）——SEND 要求对端接收队列已有挂好的 receive 工作请求，否则 RNR 错误，新手第一大坑。②**元数据双向双边交换**——16 字节 packed 三元组（src/rdma_common.h:61-70）。③**单边只在客户端**——WR 带 rkey（=收到的 remote_stag，src/rdma_client.c:336）与 remote_addr（L337），网卡直接 DMA 服务端内存。④**清理互为镜像**——QP→cm_id→CQ→完成通道→MR→PD→CM 通道，与创建严格相反。

## 5. 关键模块深讲

**（1）rdma_buffer_attr——16 字节授权协议（src/rdma_common.h:61-70）**。全仓唯一跨网结构：`uint64_t address; uint32_t length; union stag{local_stag;remote_stag;}`。**stag 联合体是钥匙**：发送方填 local_stag，接收方读 remote_stag——同一 32 位值换视角即完成授权。

**（2）MR 四件套（src/rdma_common.c:40-105）**。网卡绕过内核直接 DMA，**只能访问注册过的内存**：register（L61-80）是 ibv_reg_mr（L70）薄封装；alloc（L40-59）calloc+register 一步到位；free/deregister（L82-105）为其逆。服务端数据缓冲带 `LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE`（src/rdma_server.c:300-302）——后两位即"允许对端单边读写"的授权开关。

**（3）process_work_completion_events——CQ 样板（src/rdma_common.c:141-193）**。四步：①get_cq_event 等通知（L148）；②立即 req_notify_cq 重挂（L156）——漏掉则第二次完成永远收不到通知；③do-while 轮询 poll_cq（L167-177）处理返回 0；④校验 WC_SUCCESS（L180-187）后 ack_cq_events（L189-191，ack 事件数非 WC 数）。

**（4）client_remote_memory_ops——单边核心（src/rdma_client.c:309-388）**。两段近乎对称：WRITE 段 SGE 指 src（L326-328）、opcode=IBV_WR_RDMA_WRITE（L333）、rkey/remote_addr（L336-337）；READ 段换 SGE 指 dst、opcode=IBV_WR_RDMA_READ（L364）。**唯一区别是数据流向与本地 SGE**。

## 6. 设计决策与取舍

1. **只演示 RC**：两端硬编码 `qp_type=IBV_QPT_RC`（src/rdma_server.c:108、src/rdma_client.c:158）——RDMA WRITE/READ 单边语义只在 RC 上有定义（UC/UD 不支持）。
2. **收发共用 CQ + 容量写死**：CQ=16/SGE=2/WR=8（src/rdma_common.h:47-51），收发共用（src/rdma_server.c:110-111）；生产常拆 CQ 并按设备 probe（src/rdma_server.c:100-102 注释自认）。
3. **全局静态变量而非 context**（src/rdma_server.c:14-26、src/rdma_client.c:11-28）：代价是天然单连接，换来零参数签名。
4. **阻塞同步而非回调**：process_* 原语（src/rdma_common.c:107-193）让全程序直线逻辑；真实服务用轮询/事件循环。
5. **控制面/数据面分离**：元数据走 SEND/RECV（src/rdma_client.c:281、src/rdma_server.c:341），数据走单边；客户端元数据服务端不消费（src/rdma_client.c:238-241）。
6. **连接参数小值**：initiator_depth=responder_resources=3（src/rdma_server.c:241-243、src/rdma_client.c:212-214）。

## 7. 新人学习路径（图谱 tour 14 步）

先跑通再读码（函数锚见 §3 表）：

1.（t01）README.md:5-20 建两端流程图；CMakeLists.txt:32-33 看目标构成
2.（t02）rdma_common.h：packed 与 stag 双视角（src/rdma_common.h:61-70）、常量 L47-53
3.（t03-04）MR 四件套（src/rdma_common.c:40-105）——注册内存、权限位、先 deregister 再 free
4.（t05）事件双原语（src/rdma_common.c:107-193）——全仓最重要一段，CQ 四步要能默写
5.（t06）get_addr 与 show_*（src/rdma_common.c:10-38、197-209）
6.（t07-08）服务端建连三函数（见 §3 表 L06）——重点体会预挂先于 accept
7.（t09）send_server_metadata_to_client 看 rkey 授权；服务端 main 看编排
8.（t10-11）客户端建连三函数（见 §3 表 L08）——与第 6 步对照看两端镜像
9.（t12）数据面双雄（全仓精华）：xchange + remote_memory_ops 逐行读
10.（t13）两端 disconnect/cleanup 并排读，整理销毁顺序清单
11.（t14）两个 main 串完整故事；合码手画时序图自测

## 8. 已知坑与勘误

均经源码核实：

1. **CMake 的 CXX 选项不作用于 .c**。CMakeLists.txt:12-21 把标准与优化（-O2 等）全设在 C++ 变量，但两目标编译的全是 .c（CMakeLists.txt:32-33，走未设置的 CMAKE_C_FLAGS）——**全部优化实际未生效**。
2. **硬编码个人路径**：`HINTS /home/atr/local/lib`（CMakeLists.txt:25-26）与 `include_directories("/home/atr/local/include/")`（L30）是作者环境残留，移植应删。
3. **lkey 被当 rkey 发**。服务端授权填 `server_buffer_mr->lkey`（src/rdma_server.c:317），客户端当 rkey 用（src/rdma_client.c:336、L367）。verbs 语义跨端应发 `mr->rkey`；能跑通**依赖 provider 恰好给同一 MR 分配相同 lkey/rkey**（SoftiWARP 及多数网卡如此，非规范保证），换设备可能远程访问错误。客户端侧同填 lkey（src/rdma_client.c:260），因服务端不消费（src/rdma_server.c:294-295）未暴露。
4. **src/dst 无 NUL 终止**。calloc/strncpy 均按 strlen(optarg) 不含结尾（src/rdma_client.c:478-485）；MR 长度（L249）与 memcmp（L33）全用 strlen(src)——printf("%s") 会越界读。
5. **错误路径不回收资源**（作者自认）：src/rdma_server.c:7 TODO 明说；失败即 return，资源全泄漏。
6. **单连接单次**：backlog=8（src/rdma_server.c:160）但只等一个请求（L173-179），断连后退出（L483-488）。
7. **ACN_RDMA_DEBUG 无构建开关**：守卫在 src/rdma_common.h:34-44 但全仓无定义处，需 `cmake . -DCMAKE_C_FLAGS=-DACN_RDMA_DEBUG`；客户端 -s 必填（src/rdma_client.c:458）。

---
*understand-anything onboarding · 2026-11-11 · 行号锚全量核实*
