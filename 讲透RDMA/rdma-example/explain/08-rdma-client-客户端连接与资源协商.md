# 08 rdma_client：客户端连接与资源协商

> 对应导览第 10-11 步「客户端开场：解析路由建 QP / 预挂接收并发起连接」｜节点：`function:src/rdma_client.c:client_prepare_connection`、`function:src/rdma_client.c:client_pre_post_recv_buffer`、`function:src/rdma_client.c:client_connect_to_server`

## ① 角色定位

客户端是整条连接的**主动方与发起方**：地址要它解析、路由要它解析、连接要它发起、元数据要它先发、数据面 READ/WRITE 也全由它驱动（服务端甚至懒得用客户端的元数据，见 `src/rdma_client.c:238-242` 注释"this program is client driven"）。`main`（`src/rdma_client.c:517-531`）的前三步调用构成本篇主线：`client_prepare_connection` 完成地址→路由→资源三段式准备，`client_pre_post_recv_buffer` 连接前预挂收货箱，`client_connect_to_server` 发起 CM 握手并等 ESTABLISHED。与服务端（第 07 篇）相比，客户端多出"两次 resolve"这个 RDMA 特有前置动作——TCP 程序员最容易在这里踩坑：**CM id 在路由解析前连设备都还没绑定**。

## ② 内部结构

**`client_prepare_connection`（`src/rdma_client.c:37-173`）——三段式：**

*第一段：地址与路由解析（CM 线）*
1. `rdma_create_event_channel`（`:42`）+ `rdma_create_id(..., RDMA_PS_TCP)`（`:51-53`）——与服务端同款起手。
2. `rdma_resolve_addr(cm_client_id, NULL, s_addr, 2000)`（`:61`）：源地址传 NULL 让 CM 自己挑；超时 2000ms。注释（`:58-60`）点出关键副作用——**成功后 cm_id 被绑定到某个本地 RDMA 设备**。
3. 等 `RDMA_CM_EVENT_ADDR_RESOLVED`（`:67-69`）→ ack（`:75`）。
4. `rdma_resolve_route(cm_client_id, 2000)`（`:84`）→ 等 `RDMA_CM_EVENT_ROUTE_RESOLVED`（`:90-92`）→ ack（`:98`）。这步在查"到对端走哪条路径"，为建 QP 提供路径信息。

*第二段：verbs 资源四件套（与源码顺序一致地排在路由之后）*
5. `ibv_alloc_pd(cm_client_id->verbs)`（`:110`）——`verbs` 字段此刻才有效：resolve_addr 之前它是 NULL，PD 抢跑会拿到空设备。这就是四件套必须在第一段之后的根因。
6. `ibv_create_comp_channel`（`:122`）→ `ibv_create_cq`（`:135-139`）→ `ibv_req_notify_cq`（`:145`）。
7. `qp_init_attr`（`:153-161`，MAX_SGE/MAX_WR/IBV_QPT_RC/收发共 CQ）→ `rdma_create_qp(cm_client_id, pd, ...)`（`:163-165`）→ 别名 `client_qp = cm_client_id->qp`（`:170`）。此段与服务端 `setup_client_resources`（`src/rdma_server.c:33-124`）**逐行同构**。

**`client_pre_post_recv_buffer`（`src/rdma_client.c:176-203`）**：注册 `server_metadata_attr` 为 MR（`:179-182`）→ 填 SGE（`:187-189`）→ `ibv_post_recv`（`:194-196`）。注释（`:175`）把时序讲白了："Pre-posts a receive buffer **before** calling rdma_connect()"。

**`client_connect_to_server`（`src/rdma_client.c:206-236`）**：`conn_param` 三件套——`initiator_depth=3`（`:212`）、`responder_resources=3`（`:213`）、`retry_count=3`（`:214`，注释"if fail, then how many times to retry"，CM 报文级重试）→ `rdma_connect`（`:215`）→ 等 `RDMA_CM_EVENT_ESTABLISHED`（`:221-223`）→ ack（`:228`）。retry_count 为客户端独有（服务端 conn_param `src/rdma_server.c:239-243` 无此字段）——只有主动发 REQ 的一方才需要定义重试。

## ③ 外部连接（图谱 calls 边）

- `client_prepare_connection → process_rdma_cm_event` ×2（ADDR_RESOLVED `:67`、ROUTE_RESOLVED `:90`）、`client_connect_to_server →` ×1（ESTABLISHED `:221`）：建立期 3 个 CM 事件加断连期 1 个（`:403-405`），全经同一函数校验（第 5 篇）。
- `client_pre_post_recv_buffer → rdma_buffer_register`（`:179`）：与服务端 `accept_client_connection→rdma_buffer_register`（`src/rdma_server.c:211`）构成图谱上对称的两条边——两端各有一个"连接前注册"，注册的都是 `rdma_buffer_attr` 收货箱。
- 交接面：`client_xchange_metadata_with_server`（`:243`，第 09 篇）接过本篇交出的 ESTABLISHED 连接、就绪 QP 与预挂 RQ 空位。
- `main → get_addr`（`:494`）与 `main` 的 `calloc`/`strncpy`（`:478-490`）在上游备好 src/dst 与目标地址（默认 LOOPBACK `:468`）。

## ④ 数据流

客户端视角的连接时间线（与服务端 t0-t7 时间线在同一坐标轴上）：

```
c1 create_event_channel + create_id
c2 rdma_resolve_addr(2000ms) ──内核选设备、绑 id──→ ADDR_RESOLVED
c3 rdma_resolve_route(2000ms) ──查路径──→ ROUTE_RESOLVED   [verbs 可用]
c4 PD → comp_channel → CQ(+req_notify) → QP               [四件套]
c5 post_recv(server_metadata_attr)                        [RQ 备好空位]
c6 rdma_connect ──CM REQ 出网──→ 服务端 t3 收到 CONNECT_REQUEST
c7 (服务端装修中：PD/CQ/QP/pre-post)                       [客户端无感]
c8 服务端 rdma_accept ──CM REP 回来──→
c9 ESTABLISHED → ack → "connected successfully"(:234)
```

物理上 c2/c3 各是一次与子网管理/CM 内核态的对话；c6-c9 是 CM 握手（REQ/REP/确认），客户端在 `rdma_get_cm_event` 上睡着等 ESTABLISHED。数据（元数据、WRITE/READ）一行都还没走。

## ⑤ 设计决策

- **两次 resolve 拆开做**：地址解析（我该用哪块网卡）与路由解析（路径通不通）是两个独立失败点，rdma_cm 用两个事件分开报告；本例都给 2000ms 超时、都精确断言事件类型——第一次 resolve 失败绝不会走到建 QP，资源零浪费。
- **verbs 资源排在 resolve 之后的隐式契约**：`cm_client_id->verbs` 由 resolve_addr 填充（`:58-60` 注释），四件套全部以它为设备锚。把 `ibv_alloc_pd` 挪到 resolve 之前是新手高频翻车点——编译不报错，运行时 alloc 直接失败。
- **pre-post 必须在 connect 前**（`:194` 早于 `:215`）：服务端 accept 后随时可能 SEND 元数据过来，客户端 RQ 里必须已有空位。与服务端"pre-post 在 accept 前"（`src/rdma_server.c:229→244`）互为镜像——**两端都是"先备货、后开门"**。
- **rdma_create_qp 交给 CM 管状态机**：用 `rdma_create_qp`（而非裸 `ibv_create_qp`）造的 QP，INIT→RTR→RTS 的迁移由 rdma_cm 在 connect/accept 内部自动完成——这就是本仓通篇没有 `ibv_modify_qp` 的原因。

## ⑥ 新人提示（坑与勘误）

1. **CONNECT_RESPONSE 在本仓零出现**：老教程常写"connect 后等 CONNECT_RESPONSE"。本仓直接等 ESTABLISHED（`:221-223`）。`RDMA_CM_EVENT_CONNECT_RESPONSE` 在 rdma_cma.h 里确实存在（REP 到达的历史事件名），但 PS_TCP 主动端实际收到的是 ESTABLISHED——若真等前者，`process_rdma_cm_event` 的类型校验（`src/rdma_common.c:127-134`）会把它当 unexpected event 打回。跟着本仓写 ESTABLISHED 即可。
2. **REJECTED/CONNECT_ERROR/UNREACHABLE 一个都没处理**：对端拒绝或不可达时，第 5 篇的校验函数会打印"Unexpected event received"返回 -1——死得明白，但没有针对性恢复；生产要 switch 事件类型分诊。
3. **resolve 的 2000ms 是 CM 内部超时**，而 `rdma_get_cm_event` 本身无超时——超时事件若丢失，客户端会在 `:67` 永久阻塞；长跑服务必须配 epoll+定时器。
4. **conn_param 注释与字段的错位**：`:212-213` 两个深度字段注释的语义粒度含混（initiator_depth 是"我将发起的 outstanding 单边操作数"，responder_resources 是"我为对端预留的资源数"）；本例全填 3 无碍，照抄注释理解会在生产容量规划时栽跟头。
5. **`:175` 的 `rdma_connect (` 带空格出现在注释里**：grep 调用点时别把它算成代码，真正的调用在 `:215`。
6. **src/dst 缓冲没留 NUL**：`calloc(len,1)` + `strncpy` 恰好 strlen 字节（`:478-484`）不补终止符；后续 `strlen(src)`（`:249`、`:315`）能安全工作全靠 calloc 给的零尾（第 1 篇勘误⑥）。

——连接就绪、收货箱就位，下一场戏是两端互递"我的内存在哪"：第 09 篇拆解 `rdma_buffer_attr` 的交换协议。
