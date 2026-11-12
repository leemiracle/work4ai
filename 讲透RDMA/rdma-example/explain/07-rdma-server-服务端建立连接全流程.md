# 07 rdma_server：服务端建立连接全流程

> 对应导览第 7-8 步「服务端开场：监听连接请求 / 资源分配与预挂接收时序」｜节点：`function:src/rdma_server.c:start_rdma_server`、`function:src/rdma_server.c:setup_client_resources`、`function:src/rdma_server.c:accept_client_connection`

## ① 角色定位

rdma_server.c 的前半生只干一件事：**把一条被动连接从"监听"带到"可收发"**。`main`（`src/rdma_server.c:463-483`）用三步调用串起这条线：`start_rdma_server` 开监听并等到 CONNECT_REQUEST，`setup_client_resources` 为这条连接造齐 PD/comp_channel/CQ/QP 四件套，`accept_client_connection` 预挂接收缓冲后才 `rdma_accept`。与 socket 世界最大的不同藏在顺序里：**accept 被刻意推迟到全部资源就绪之后**（`:244` 前有 `:229` 的 pre-post）——RDMA 的"接电话"分两段拍，中间夹着一段资源准备期，这是本篇主线。文件头 `:14-26` 的 8 组 static 全局正是这条时间线将逐一点亮的资源清单。

## ② 内部结构

**`start_rdma_server`（`src/rdma_server.c:127-197`）——开监听五连：**
1. `rdma_create_event_channel`（`:132`）：CM 事件的搬运通道，全进程一条。
2. `rdma_create_id(cm_event_channel, &cm_server_id, NULL, RDMA_PS_TCP)`（`:142`）：监听用 cm id，端口空间选 TCP（RC 连接型）。
3. `rdma_bind_addr`（`:149`）：把 `main` 里填好的 sockaddr（默认 INADDR_ANY，`src/rdma_server.c:437-438`）绑上去。
4. `rdma_listen(cm_server_id, 8)`（`:160`）：backlog=8，注释自注"same as TCP"；但本服务端是单连接一次性程序，8 只是个没人兑现的许诺（见⑥）。
5. 阻塞等 `RDMA_CM_EVENT_CONNECT_REQUEST`（`:173-175`，走第 5 篇的 `process_rdma_cm_event`），事件到达后**先拷走 `cm_event->id` 再 ack**（`:184` 取、`:190` ack）——`cm_client_id` 这个新 id 才是后续所有资源真正的挂靠对象。

**`setup_client_resources`（`src/rdma_server.c:33-124`）——四件套，全部以 `cm_client_id->verbs` 为设备锚：**
1. `ibv_alloc_pd(cm_client_id->verbs)`（`:50`）：保护域。注释（`:46-48`）给出全书最好记的类比——PD 之于 RDMA 资源 ≈ 进程之于 OS，跨 PD 访问即保护错误。
2. `ibv_create_comp_channel`（`:66`）：I/O 完成通知通道，注释（`:60-65`）强调它与 CM 事件通道是**两条完全不同的线**。
3. `ibv_create_cq(verbs, CQ_CAPACITY, NULL, io_completion_channel, 0)`（`:80-84`）+ `ibv_req_notify_cq`（`:93`）：容量 16（`src/rdma_common.h:47`），并立刻挂上通知请求。
4. `rdma_create_qp(cm_client_id, pd, &qp_init_attr)`（`:113`）：QP 挂在**客户端连接 id** 而非监听 id 上；`qp_init_attr`（`:103-111`）填 MAX_SGE=2/MAX_WR=8、`IBV_QPT_RC`、收发共用同一个 CQ（`:110-111`）。`:121` 的 `client_qp` 别名仅为少打字。

**`accept_client_connection`（`src/rdma_server.c:200-274`）——先备货后开门：**
1. 注册 `client_metadata_attr` 为 MR（`:211-214`，仅 `IBV_ACCESS_LOCAL_WRITE`）——将来装客户端元数据的收货箱。
2. 填 SGE（`:222-224`）+ `ibv_post_recv`（`:229-231`）：接收 WR 在 QP 尚未就绪时就排进 RQ。
3. `conn_param.initiator_depth = 3 / responder_resources = 3`（`:241-243`）后 `rdma_accept`（`:244`）：rdma_cm 会在 accept 内部把 QP 自动推进到 RTR/RTS（`rdma_create_qp` 造的 QP 才享此待遇）。
4. 等 `RDMA_CM_EVENT_ESTABLISHED`（`:254-256`）→ ack（`:262`）→ `rdma_get_peer_addr` 拷出对端地址打印（`:268-272`）。

## ③ 外部连接（图谱 calls 边）

- `start_rdma_server → process_rdma_cm_event`（等 CONNECT_REQUEST，`src/rdma_server.c:173`）、`accept_client_connection →` ×2（注册 MR `:211`、等 ESTABLISHED `:254`）：本篇两处阻塞点都委托给公共层双原语。
- `send_server_metadata_to_client`（下一篇 09 的主角）从 `accept_client_connection` 手里接过已就绪的 QP/CQ/MR 三件套——图谱 t08→t09 的交接面。
- 客户端镜像：`client_pre_post_recv_buffer`（`src/rdma_client.c:176-203`）与服务端 `:211-231` 逐行同构（同一份代码复制改名），两端"预挂"语义对称。
- `main → get_addr`（`src/rdma_server.c:444`）：CLI 传 IP 时才走（第 6 篇已讲清端口覆盖坑）。

## ④ 数据流

服务端视角的连接时间线（t0 起）：

```
t0 rdma_create_event_channel/create_id     [监听骨架立起]
t1 rdma_bind_addr + rdma_listen(8)         [printf "listening" :166-168]
t2 ——阻塞在 rdma_get_cm_event（:173）———   [客户端 resolve/connect 在另一端推进]
t3 CONNECT_REQUEST 到达 → cm_client_id 诞生 [ack 后事件结构体失效]
t4 PD → comp_channel → CQ → QP 四件套       [全部锚定 cm_client_id->verbs]
t5 注册元数据收货箱 + post_recv             [RQ 里有了一个空位]
t6 rdma_accept                              [CM 发 REP；QP 自动转 RTR→RTS]
t7 ESTABLISHED 到达（对端确认后）→ 连接可用  [peer addr 打印，交棒给 09]
```

注意 t3→t6 这段窗口：客户端已经在敲門，服务端却在"装修"——CM 协议替你把这个窗口折叠成一次 accept，客户端只会觉得连接慢了些，不会失败。

## ⑤ 设计决策

- **为什么资源建在 CONNECT_REQUEST 之后、accept 之前**：QP 必须挂在连接专属的 `cm_client_id` 上，而这个 id 在 CONNECT_REQUEST 里才诞生（`:184`）；又因为 RC 连接一旦 ESTABLISHED，对端 SEND 随时可到，接收 WR 必须先于 QP 转入 RTR 就位（`:229` 在 `:244` 之前）——否则首包就撞 RNR（receiver not ready）错误。顺序不是风格，是协议要求。
- **initiator_depth/responder_resources 的取舍**（`:241-243`）：注释明说"For this exercise, we put a small number"——这两个值是给对端单边操作预留的 outstanding 额度，本例客户端只发 2 次单边操作，3 绰绰有余；生产端要看实际在飞的 read 深度。
- **收发共用一个 CQ**（`:109-111`）：注释自认"We use same completion queue, but one can use different queues"——省一个 fd 和一套收割路径；代价是 WC 混排、收割方要靠上下文分辨（第 5 篇勘误⑤）。
- **`client_qp` 别名**（`:120-122`）：rdma_create_qp 之后 QP 藏在 `cm_client_id->qp` 里——但销毁时仍要回到 `rdma_destroy_qp(cm_client_id)`（`:383`），别名不能 destroy。

## ⑥ 新人提示（坑与勘误）

1. **函数名是反向的**：`setup_client_resources`（`:33`）跑在**服务端**上，准备的是"服务这条客户端连接所需的资源"。第一次读几乎人人疑惑，看注释 `:28`"cm_client_id must be set"即解。
2. **两个 cm_id 别混**：`cm_server_id`（监听 id，`:142` 造）生命周期贯穿始终（`:413` 才销毁）；`cm_client_id`（连接 id，`:184` 出生）承载全部数据面资源，`:385` 先走。销毁顺序见第 10 篇。
3. **backlog=8 是装饰品**：`rdma_listen(cm_server_id, 8)`（`:160`）之后程序只 `process_rdma_cm_event` **一次**（`:173`），处理完一条连接直接进收尾——多来的连接请求没人消费。
4. **注释里的拼写事故**：`RDMA_CM_EVNET_CONNECT_REQUEST`（`:169`）、`RDMA_CM_EVNET_ESTABLISHED`（`:249`）——EVNET 应为 EVENT，代码里真正传的是正确的枚举（`:174/:255`），注释别照抄。
5. **错误路径全泄漏**：文件头 TODO（`:7`）自曝"Cleanup previously allocated resources in case of an error condition"从未兑现——`main` 任一步失败直接 `return ret`（`:464-487`），已建的 PD/CQ/QP 全漏，且不给对端发 disconnect（对端会干等到超时）。教学可忍，复用必改（见第 12 篇）。
6. **`rdma_disconnect` 在服务端零调用**：`:360` 出现在注释里（"waits for the client to call rdma_disconnect()"），grep 别数错——服务端是被断方，只等 DISCONNECTED 事件（`:367-369`），主动断连永远是客户端的活（`src/rdma_client.c:398`）。

——连接建立后，服务端只剩一场"收元数据、发元数据"的对话；这场对话的协议细节是第 09 篇的主题，本篇先看到它的前半场入口 `send_server_metadata_to_client`（`:277`）。
