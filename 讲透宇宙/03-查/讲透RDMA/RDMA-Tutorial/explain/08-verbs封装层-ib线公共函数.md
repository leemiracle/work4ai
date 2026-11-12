# 08 · verbs 封装层：ib.c/ib.h 公共函数的参数学

## ① 角色定位

ib.c（121 行）+ ib.h（49 行）是全仓唯一的 verbs API 封装层：三个函数（modify_qp_to_rts / post_send / post_srq_recv）+ 一组协议常量，client 与 server 两侧共用，对应图谱"verbs 封装层"（第 8 层，tour 第 11 步）。第 5 篇从状态机视角讲了 modify_qp_to_rts 的三段编排（INIT→RTR→RTS 的"为什么"），本篇换镜头看**参数学**：每段 qp_attr 里每个字段填什么、attr_mask 怎么与字段对应、post_send 的六个参数各自去哪了——这是把"看得懂"变成"改得动"的一篇。ib.h 的另一半职责是充当**协议常量与公共类型的家**：QPInfo、MsgType、IB_* 宏都在这里，因为它被 sock.h（sock.h:6）和 main.c（main.c:5）等所有模块 include，是事实上的"公共头"。

## ② 内部结构

**ib.h 常量区（ib.h:11-17）**分三类：链路参数 `IB_MTU=IBV_MTU_4096`、`IB_PORT=1`、`IB_SL=0` 是三处硬编码的物理假设（第 12 篇展开）；基准参数 `NUM_WARMING_UP_OPS=500000`、`TOT_NUM_OPS=10000000` 控制预热与总量；魔数 `IB_WR_ID_STOP=0xE000000000000000` 是停止信令的 wr_id 标记。`SIG_INTERVAL=1000`（ib.h:17）全仓零引用，是死宏（grep 实证仅定义处一次）。

**ib.h:19-27 的 htonll/ntohll**：按字节序条件编译的 64 位转换对，全仓零调用——又一个预留未用的死代码（第 9 篇会把它并入 debug.h 死宏清单一起盘点）。

**modify_qp_to_rts（ib.c:7-74）三段的字段-mask 对应表**（verbs 的铁律：改哪个字段，attr_mask 就必须列哪个 IBV_QP_* 位，漏一个则该字段被静默忽略）：

| 段 | 设置字段 | attr_mask（ib.c:24-25/46-49/65-67） |
|---|---|---|
| INIT | qp_state / pkey_index / port_num / **qp_access_flags 四权限全开**（ib.c:17-20：LOCAL_WRITE+REMOTE_READ+REMOTE_ATOMIC+REMOTE_WRITE） | STATE\|PKEY_INDEX\|PORT\|ACCESS_FLAGS |
| RTR | qp_state / **path_mtu=IB_MTU** / **dest_qp_num=target** / rq_psn=0 / max_dest_rd_atomic=1 / **min_rnr_timer=12** / ah_attr{is_global=0, **dlid=target_lid**, sl=IB_SL, port_num} | STATE\|AV\|PATH_MTU\|DEST_QPN\|RQ_PSN\|MAX_DEST_RD_ATOMIC\|MIN_RNR_TIMER |
| RTS | qp_state / **timeout=14** / **retry_cnt=7** / **rnr_retry=7** / sq_psn=0 / max_rd_atomic=1 | STATE\|TIMEOUT\|RETRY_CNT\|RNR_RETRY\|SQ_PSN\|MAX_QP_RD_ATOMIC |

值得注意的细节：本仓缓冲注册时只给了 LOCAL|REMOTE_READ|REMOTE_WRITE 三权限（setup_ib.c:279-281），但 QP INIT 段开了四权限（多一个 REMOTE_ATOMIC）——权限粒度不冲突（QP 权限是上限，MR 权限是实际授权），但看得出两处权限清单不是同一份拷贝。定时器三值（12/14/7）都是 verbs 教程惯用的保守指数编码值，语义为重传超时、Go-Back-N 重试上限与 RNR 等待，精确的微秒换算依赖 IB spec 编码表，本篇不展开。

**post_send（ib.c:76-99）**：参数六进六出——req_size→`list.length`（ib.c:84），lkey→`list.lkey`（ib.c:85），buf→`list.addr`（ib.c:83，经 `(uintptr_t)` 转换），wr_id 原样进 `send_wr.wr_id`（ib.c:89），imm_data 经 **htonl** 进 `send_wr.imm_data`（ib.c:94），qp 决定投递目标。两个固定选择：单 SGE（`num_sge=1`，ib.c:91）与 `IBV_WR_SEND_WITH_IMM`（ib.c:92）+ `IBV_SEND_SIGNALED`（ib.c:93）。返回值直接透传 ibv_post_send 的 errno 语义（ib.c:97-98），不包 check——让调用方决定热路径要不要查（第 6 篇⑤③已析）。

**post_srq_recv（ib.c:101-121）**：与 post_send 同构的 SGE 组装，投递目标是 **srq 而非 qp**（ib.c:119 `ibv_post_srq_recv`），且无 opcode/flags——接收 WR 的属性只有 sg_list 与 wr_id。

## ③ 外部连接

调用方矩阵：modify_qp_to_rts 只被 setup_ib.c 的两个建连函数调（setup_ib.c:84/188）；post_send 被两侧数据面的预投、控制广播、回显共 6 处调用（client.c:96/142、server.c:67/105/115）；post_srq_recv 被预投与补投共 6 处调用（client.c:57/77/146、server.c:59/108）。反向依赖：sock.h:6 include ib.h 拿 QPInfo（第 7 篇③）；main.c:5 也 include ib.h，但 main.c 正文不含任何 ib.h 符号（IB_* 宏、QPInfo、ibv_* 均未出现）——**冗余 include**，可能是历史演进的残留。ib.c 自身 include 链极简：arpa/inet.h（htonl）+ ib.h + debug.h（check）。

## ④ 数据流

**target 参数的来源链**（modify_qp_to_rts 的第 2/3 参数）：调用点 setup_ib.c:84-86 传入 `remote_qp_info[i].qp_num / .lid`——正是第 7 篇协议从 TCP 线上收来的对端信息。也就是说 RTR 段的 dest_qp_num 与 ah_attr.dlid 是**全程序中唯一一处对端地址的消费点**：QPInfo 协议 10 字节里的 6 字节（lid+qp_num）在这里变成硬件可用的路由目标，rank 那 4 字节则在配对阶段用尽即弃。

**imm_data 的字节序闭环**：post_send 入口 htonl（ib.c:94）→ 线上网络序 → 两侧完成事件 ntohl（client.c:130、server.c:103）。闭环两端分居 ib.c 与两个数据面文件——**编码在封装层、解码在使用方**，这个不对称意味着读 server.c:103 时必须知道 ib.c:94 才能拼出完整语义，是封装层"藏了一半"的代价。

**wr_id 的透传语义**：post_send/post_srq_recv 对 wr_id 不做任何加工（ib.c:89/114），同一参数在三种调用点承载三种身份——接收缓冲指针（client.c:57）、0（回显发送，client.c:142）、停止魔数（server.c:115）。封装层把语义解释权完全留给调用方，wr_id 是 verbs 里罕见的"用户全权字段"。

## ⑤ 设计决策

**① 为什么只封装这三个函数**：全仓 verbs 调用共约 20 个 API，资源创建类（open_device/alloc_pd/reg_mr/create_cq/create_srq/create_qp）只在 setup_ib 顺序执行一次且参数结构各不相同，封装无收益；而 modify_qp_to_rts（重复 3 段×N 对端）、post_send/post_srq_recv（热路径每秒百万次）参数模式固定、调用密集，封装消除的是**重复**而非复杂度。这是"按调用频次决定抽象边界"的最小实践。

**② attr_mask 显式列举而非 IBV_QP_USE_ALL**：verbs API 没有"全字段"掩码，且不同 QP 状态迁移的合法字段集不同。本仓逐字段列 mask（ib.c:24-25/46-49/65-67）虽然啰嗦，但与上方 designated initializer 一一对照，学生能逐行验证"改的=列的"——漏 mask 是 verbs 新手第一大坑（字段静默不生效，连接莫名不通），这种写法把坑摊开在明处。

**③ 单 SGE+全 SIGNALED 的教学取舍**：每条消息一个 scatter/gather 条目、每条发送都产生完成事件，最简但牺牲性能（多 SGE 聚合与批量 Signaled 是生产标配）——第 6 篇⑤⑤已从吞吐角度分析，本篇补充封装视角：固定的 `num_sge=1` 让 SGE 组装只有 3 行，如果把 num_sge 也参数化，函数签名要多两个参数，教程可读性下降。

**④ htonll 死代码的存在猜测**：imm_data 是 32 位、QPInfo 字段最长 32 位，64 位转换对从未被需要。它坐在 ib.h 而非被删掉，更像是作者从别的项目模板带来的"标准件"——小仓的死代码大都不是设计而是历史。

## ⑥ 新人提示

读 ib.c 顺序：先 ib.h 全文（49 行，一半是常量一半是声明），再 post_send（最短），最后 modify_qp_to_rts 对照第 5 篇状态机。三个动手实验：① 把 IB_MTU 改成 IBV_MTU_1024 重跑——path_mtu 必须 ≤ 两侧端口及路径上所有交换机的 MTU，且**两侧必须一致**，否则 RTR 后第一笔发送就报 transport 错；② 把 RTS 段 retry_cnt 从 7 改成 0 感受可靠传输差异；③ 试着删掉 ib.c:48 的 IBV_QP_PATH_MTU 再看 RTR 是否还生效——这是"漏 mask 静默失败"的最直接体验。改造提醒：若要支持 RDMA WRITE（Example 2 的方向，见第 11 篇④），post_send 需要 opcode 参数化，届时 `imm_data` 与 `IBV_WR_RDMA_WRITE` 的 addr/rkey 组合会逼你扩展这个 6 参数签名——它是本封装层扩展的第一个受力点。
