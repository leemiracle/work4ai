# 06 struct connection：匿名枚举驱动的握手状态机

> 对象：`rdma-common.c` 的 `struct connection`（L25-L56）及其状态迁移逻辑（on_completion L180-L235）；行号锚经源码核实（commit `c760004`）。

## 一、角色定位

struct connection 是 write_read 示例的协议主体：每个 RDMA 连接一份实例，挂载在 `cm_id->context`（build_connection L86），从建立存活到断开。它的前半（L26-L42）是资源容器——cm_id/QP 指针、四块 MR 指针、对端 MR 副本 `peer_mr`（L36，值拷贝非指针）、两个消息缓冲与两个数据区；**后半（L44-L55）是本仓最精巧的设计：两个匿名枚举构成的握手状态机**，把「SEND 互发 MR 钥匙→单边 WRITE/READ→MSG_DONE 握手→断开」这条四幕剧压进 7 个枚举值。on_completion（L180-L235）是它的发动机，poll_cq 逐事件供油（见第 05 篇）。send_recv 组的 connection（send_recv/client.c:23-L34）没有状态机只有 num_completions 计数——两组示例的复杂度差正浓缩在这两个结构体的 diff 里。图谱把它记为 class 节点（tree-sitter 对 C struct 的误判，languageNotes 已标注），它无任何方法，行为全靠外部函数操纵。

## 二、内部结构

```c
enum { SS_INIT, SS_MR_SENT, SS_RDMA_SENT, SS_DONE_SENT } send_state;   // L44-L49
enum { RS_INIT, RS_MR_RECV, RS_DONE_RECV }               recv_state;   // L51-L55
```

send_state 走发送侧四态：SS_INIT（未发过 MR）→SS_MR_SENT（MR 的 SEND 完成）→SS_RDMA_SENT（单边 WR 完成）→SS_DONE_SENT（MSG_DONE 的 SEND 完成）；recv_state 走接收侧三态：RS_INIT→RS_MR_RECV（收到对端 MR）→RS_DONE_RECV（收到 DONE）。**两个关键声明细节**：枚举是匿名的且直接内嵌为成员——C 的经典惯用法，枚举值（SS_INIT 等）泄漏到文件作用域当常量用，成员本身按 int 大小存储；两态各自独立计数，不是一条流水线。状态机没有专门的事件处理函数，全部转移逻辑寄生在 on_completion 的两个 `++` 上：RECV 完成一律 `conn->recv_state++`（L188），非 RECV（SEND/RDMA WRITE/READ）完成一律 `conn->send_state++`（L199）。状态与协议消息的对应靠「消息到达顺序」隐式锁定：本协议保证每侧恰收两条（先 MSG_MR 后 MSG_DONE），故 ++ 两次后 recv_state 必然停在 RS_DONE_RECV。初值在 build_connection 置 SS_INIT/RS_INIT（L91-L92）。

## 三、外部连接

状态机的输入输出全在 on_completion：**输入侧**三个消费点——L187 `wc->opcode & IBV_WC_RECV` 位与判断（RECV 与 RECV_WITH_IMM 都命中，ibverbs 惯例）；L190 读 `recv_msg->type` 区分 MSG_MR/MSG_DONE；L203/L231 两个汇合判断读双态。**输出侧**四个动作——收到 MSG_MR：memcpy 对端钥匙进 peer_mr（L191）+rearm（L192，注释明言 only rearm for MSG_MR，故全连接恰预挂两次 RECV）+若己方仍 SS_INIT 则回发 MR（L194-L195，被动端的应答通道）；双态达 SS_MR_SENT∧RS_MR_RECV：构造单边 WR（L204-L226）并发 MSG_DONE（L228-L229）；双态达 SS_DONE_SENT∧RS_DONE_RECV：打印对端缓冲+rdma_disconnect（L231-L233）。入口层唯一交互点是 on_connect 置 `connected=1`（L237-L240），解掉 send_message 的自旋（L326）。`connected` 字段与状态机平行存在——它是线程同步标志而非协议状态，别混为一谈。

## 四、数据流

以 M_WRITE 模式 client 视角走全表（server 同构，仅首步改由 L194-L195 应答触发）：

| 事件（CQE） | 转移 | 副作用 |
|---|---|---|
| ESTABLISHED→send_mr 提交 | （SS_INIT） | 钥匙入 send_msg（L335-L336） |
| SEND[MR] 完成 | SS_INIT→SS_MR_SENT | 打印 send completed（L200） |
| RECV[对端 MSG_MR] | RS_INIT→RS_MR_RECV | 存 peer_mr、rearm、（被动端）回发 MR |
| **汇合判定 L203 通过** | — | post RDMA WRITE（L226）+发 MSG_DONE（L228） |
| RDMA WRITE 完成 | SS_MR_SENT→SS_RDMA_SENT | 打印（L200 复用） |
| SEND[DONE] 完成 | SS_RDMA_SENT→SS_DONE_SENT | 打印 |
| RECV[对端 MSG_DONE] | RS_MR_RECV→RS_DONE_RECV | — |
| **终态判定 L231 通过** | — | 打印 remote buffer、断开（L232-L233） |

两个跨端事实：①L203 的汇合条件在**两端各自独立成立**——双方都收到对方 MR、都发过自己的 MR，于是双方各 post 一个单边 WR，演示实为对称双向；②终态两条件的到达顺序不确定（DONE 发送完成与收到对端 DONE 谁先皆可），`&&` 判断天然容忍两种交错——这正是用两条独立计数而非单一序列状态的价值。

## 五、设计决策

①**隐式中间态 SS_RDMA_SENT（L47）**：全仓最著名的「不存在分支」——从未有任何 `if (send_state == SS_RDMA_SENT)`。它是 L199 的 ++ 流经的过渡态，存在意义是让枚举值域与「实际发生的 SQ 完成事件数」精确对齐（MR、RDMA、DONE 三次 signaled 提交各贡献一次 ++）。**该设计有一根隐藏的承重梁**：单边 WR 必须带 IBV_SEND_SIGNALED（L218）——若改成 unsignaled，RDMA 完成不产生 CQE，send_state 停差一步，L231 的 SS_DONE_SENT 永不满足，连接挂死。SIGNALED 在此同时承担通知与状态机步进双职。②**计数式推进（++）而非显式赋值**：协议正确性完全寄托在「每个请求恰产生一个完成」的 ibverbs 契约上，任何多发一条消息都会让状态漂移——例如 client 侧若对端 MR 的 RECV 先于自己 SEND 完成被 poll，L194 会再发一次 MR 使状态机过冲；实际不发生是因为 CQ FIFO+网络因果（client SEND 的 ACK 先于 server 的回包入队）双重保序，属于「对但脆」的教学设计。③**应答式回发（L194-L195）**让被动端无需在事件循环里发钥匙（rdma-server.c 的 ESTABLISHED 只置位），一套状态机同时适配主动/被动两种角色。④**消息协议与状态一一咬合**：MSG_MR 携带全部载荷（联合体装 ibv_mr），MSG_DONE 是零载荷哨兵——协议只有两种消息，状态机只有两次 RECV，rearm 恰好只做一次（L192），多余的接收槽都不留。⑤server 断开后 return 0 继续守听（rdma-server.c:80）而状态机实例随 destroy_connection 释放——状态机生命周期=连接生命周期，不跨连接复用。

## 六、新人提示

读 L180-L235 时手画状态表（照抄第四节表格），每遇一个 `++` 就在表上走一步，十分钟后整个协议了然。**三个「别找」**：别找 SS_RDMA_SENT 的判断分支（不存在）；别找 MSG_DONE 的显式处理 case（它的全部作用就是让 recv_state 过 RS_DONE_RECV 这道坎）；别找状态回退逻辑（单向计数，无回退）。调试技巧：在 L188/L199 两个 ++ 后各加一行 printf 打印双态当前值，跑一次 write 模式即可看到两端交错的真实轨迹——比读十遍代码都清楚。改协议时记住三条不变量：每侧 RECV 次数=预挂次数（多发必 RNR）、每个 signaled 提交恰推一步 send_state（少发即挂死）、终态判断必须覆盖最后一个完成事件（否则无人调 disconnect）。面试相关：QP 的 RESET→INIT→RTR→RTS 状态机是**网卡侧**状态、由 rdma_cm 封装（build_qp_attr L129-L141 只见参数不见迁移），与本篇**应用侧**状态机是两层不同的东西，被问「RDMA 状态机」时先分清对方问的是哪一层——这是 interview 板块真题的高频混淆点。
