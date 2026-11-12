# 07 · QPInfo 交换协议：sock 线上的自定义协议设计

## ① 角色定位

第 3 篇讲了 sock.c 这个"传输工具箱"（六个函数怎么实现的），本篇讲跑在这些工具之上的**应用层协议本身**——一个作者自设计的带外交换协议。它散落在三个文件里：载荷定义在 ib.h:29-33（`struct QPInfo`），序列化编解码在 sock.c:144-178，协议编排（时序、配对、屏障）在 setup_ib.c 的 connect_qp_server（setup_ib.c:13-127）与 connect_qp_client（setup_ib.c:129-237）。把这三块拼起来，你会看到一个教科书级的"最小分布式握手协议"：**10 字节定长载荷 + 上行/下行两轮交换 + 双向 sync 屏障**，总共不到 250 行，却完整解决了"两个刚创建的 RC QP 如何找到彼此"的问题。理解这个协议的设计（而不是实现），是理解 rdma_cm 这类工业库在帮你做什么的前提——rdma_cm 的 CM 报文干的就是同样的事。

## ② 内部结构

**载荷：QPInfo（ib.h:29-33）**。三字段各司其职：`lid`（uint16）是 IB 子网内的链路层地址，告诉对端"网卡在哪个交换机端口"；`qp_num`（uint32）是 QP 的编号，RC 报头里的 Dest QP 靠它路由到具体队列；`rank`（uint32）是**配对键**——本机在节点列表中的序号（config.c:108-126 由 hostname 匹配得出），它不参与任何 IB 语义，纯粹为协议层的多对端配对服务。`__attribute__((packed))` 压掉填充，线上严格 2+4+4=10 字节。

**编解码对称对（sock.c:144-178）**。sock_set_qp_info 把三字段经 htons/htonl 转网络序写入栈上临时结构（sock.c:149-151），整块 sock_write；sock_get_qp_info 整块 sock_read 后 ntohs/ntohl 还原（sock.c:170-172）。临时结构 + 逐字段转换（而非整结构 dump）意味着**字节序转换点被显式声明在字段粒度**——这是二进制协议的可审计写法。

**屏障：SOCK_SYNC_MSG（sock.h:8）**。5 字节的 "sync" 字符串（sizeof 含结尾 NUL），内容无意义，作用是确保**双方都完成 RTS 迁移之后**才放行数据面。没有它，client 可能在 server 还没 modify_qp_to_rts 时就 post_send，触发 RNR（Receiver Not Ready）错误。

## ③ 外部连接

协议三块的依赖方向值得注意：sock.c 的序列化函数签名里出现 `struct QPInfo *`，而 QPInfo 定义在 ib.h——sock.h:6 `#include "ib.h"` 让**协议载荷穿过了模块边界**（传输层依赖了 RDMA 层的头文件）。这是有意的取舍：与其为 10 字节结构单开一个协议头文件，不如挂在 RDMA 语义的拥有者 ib.h 上，代价是 sock 模块不再是纯传输工具。上游调用方只有 setup_ib.c 的两个 connect_qp_* 函数；sync 收发不走任何包装函数，直接调 sock_read/sock_write（setup_ib.c:96/101、200/205），因为 5 字节定长读取不需要 QPInfo 级别的序列化逻辑。

## ④ 数据流

两侧完整时序（以 2 client × 1 server 为例，client 视角 i=0）：

```
server                                client_0 / client_1
  | sock_create_bind(port) L25              |
  | listen(fd, 5) L27                        |
  |                                          | sock_create_connect(srv, port) L143
  | accept ×2 → peer_sockfd[0..1] L32-36 <——+  (到达顺序即槽位!)
  | local_qp_info[i] = {lid, qp[i], rank} L43-47
  |                                          | local_qp_info = {lid, qp[0], rank} L153-157
  |            (1) 上行: client 先发          |
  | sock_get_qp_info(peer_sockfd[i]) <———————| sock_set_qp_info L161
  |   → remote_qp_info[i] L54-57             |
  |            (2) 下行: server 按 rank 回发   |
  | peer_ind = find(remote[j].rank==i) L62-69|
  | sock_set_qp_info(peer_sockfd[i],         |
  |   &local_qp_info[peer_ind]) L70 ————————>| sock_get_qp_info → remote_qp_info[0] L171
  |            (3) 各自 RTS 迁移              |
  | modify_qp_to_rts(qp[peer_ind],           | modify_qp_to_rts(qp[0],
  |   remote[i].qp_num, remote[i].lid) L84-86|   remote[0].qp_num...) L188-190
  |            (4) 双向 sync 屏障             |
  | sock_read(sync) L96  <———————————————————| sock_write(sync) L200
  | sock_write(sync) L101 ——————————————————>| sock_read(sync) L205
  | close ×N L105-109                        | close ×N L209-212
```

注意交换方向的不对称：**client 永远先发后收，server 永远先收后发**。这不是任意选择——server 必须先收齐所有 client 的 QPInfo 才能计算配对，所以"先发"的一方只能是 client；而 server 回发的信息本身依赖全体上行完成，协议天然形成两轮全收集（all-gather）结构。

**rank 配对算法**（setup_ib.c:62-69）是协议的核心一段：对每个目标 rank i，在 remote_qp_info[] 里线性查找 rank==i 的槽位 j，把 local_qp_info[peer_ind] 发回 peer_sockfd[i]。同样的查找在 RTS 段又做了一遍（setup_ib.c:77-83）——O(N²) 但 N≤2，教学场景无所谓。

## ⑤ 设计决策

**① 为什么需要 rank 这个第三字段**。仅凭 lid+qp_num 双方已能连通，但 server 有 num_clients 条 QP 和 num_clients 个 socket，**"哪条 QP 对应哪个 socket 对端"必须显式表达**。rank 就是把这个映射拍在协议明面上：server 知道"remote rank i 的连接信息从槽 i 读到、我的 qp[peer_ind] 要配给它"。没有 rank，多对端场景下只能赌 accept 顺序。

**② 信道与身份的绑定是隐含契约（本协议最大的设计弱点）**。细读回发逻辑：发给 peer_sockfd[i] 的载荷是"rank==i 的 QP 信息"——这隐含假设**accept 槽位 i 的 TCP 连接恰好来自 rank i 的 client**。但 TCP 不保证到达顺序：若 client_1 的 SYN 先到，它占据槽 0，server 会把"连 client_0 的 QP"信息发给 client_1，后者用错误的 qp_num 配 RTR，连接建立后第一笔数据即触发对端 QP 错误。协议用 rank 做了半程配对（QP↔QP 正确），却没有做信道↔身份的闭环验证。工业协议的做法是让身份随消息走（如 TCP 四元组天然绑定），或在载荷里回显对端身份做校验。第 12 篇会把这一条并入拓扑假设链。

**③ 定长 packed 而非 TLV/文本**。10 字节定长配"读满为止"的 sock_read，免疫短读、无分隔符歧义——这是最小正确实现；代价是加字段就破坏线格式兼容（但教程两侧同版本编译，无演进需求）。

**④ sync 用字节计数而非字符串语义**。sizeof(SOCK_SYNC_MSG)=5（含 NUL），双方各写各读 5 字节即可对齐，sync 的"内容"从未被校验（setup_ib.c:96 收进 sock_buf 后 L101 原样回写）。屏障只关心"事件发生"，不关心"内容是什么"。

## ⑥ 新人提示

读协议代码建议按"载荷→时序→屏障"三遍读：第一遍只看 ib.h:29-33 和 sock.c:144-178（载荷与编解码），第二遍对照上面的时序图逐行核 setup_ib.c（重点 L60-72 的配对循环），第三遍思考"哪里会坏"。两个动手实验：① 在 QPInfo 里加一个 `uint32_t num_qps` 字段，验证 packed 定长协议的扩展只需改结构体定义（第 3 篇⑥的延续）；② 故意让两个 client 同时发起连接并多跑几次，观察 accept 槽位与 rank 错位导致的偶发失败——这是比读代码更深刻的"协议边界"体验。最后提醒：本协议的"先收齐再回发"结构在 N 对端时是全串行屏障，扩展到大规模需改为流水线式逐连接处理；对教程的 2 节点场景，这个简单结构恰恰是优点。
