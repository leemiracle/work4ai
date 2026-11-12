# 11 ibv-verbs 调用图谱：全仓 API 速查表

> 横跨全部 14 步导览｜覆盖节点：三个 .c 的全部 24 个函数节点（本篇按 API 而非函数组织）

## ① 角色定位

本仓是名副其实的"verbs 阅读理解题"：全仓 **32 个不同的 ibv_*/rdma_* API、61 个原始调用点**（不含 `rdma_error` 打印宏与 `rdma_buffer_*` 自研薄封装），把 libibverbs+librdmacm 的最小闭环完整走了一遍。本篇把它们全部铺成一张按生命周期分组的速查表——每个 API 给出角色、全部调用点行号、参数要点，读源码卡壳时查这里。这张表也暴露了 verbs 世界的分工：**rdma_ 管"连接怎么建"，ibv_ 管"数据怎么飞"**，两条线只在 `rdma_create_qp` 一个点上握手。

## ② 内部结构（速查表）

**A. CM 连接线（rdma_*，17 个）**

| API | 调用点 | 角色与参数要点 |
|---|---|---|
| rdma_create_event_channel | 服务端 `src/rdma_server.c:132`/客户端 `src/rdma_client.c:42` | 建 CM 事件通道，无参；进程各一条 |
| rdma_create_id | `:142`/`:51` | (channel,&id,NULL,**RDMA_PS_TCP**)：PS_TCP=RC 连接型 |
| rdma_bind_addr | 服务端 `:149` | 监听侧绑定 IP/端口；主动侧由 resolve_addr 隐式完成 |
| rdma_listen | 服务端 `:160` | (id, **backlog=8**)，非阻塞；连接请求变成通道上的事件 |
| rdma_resolve_addr | 客户端 `:61` | (id, **NULL** 源地址, 对端, **2000**ms)；副作用：绑定本地设备并填 id->verbs |
| rdma_resolve_route | 客户端 `:84` | (id, 2000ms)；查路径，成功后建 QP 所需路径信息可用 |
| rdma_connect | 客户端 `:215` | (id,&conn_param)：发 CM REQ，主动端专属 |
| rdma_accept | 服务端 `:244` | (id,&conn_param)：回 REP 并自动把 QP 推进到 RTR/RTS |
| rdma_disconnect | 客户端 `:398` | 发 DREQ；服务端全仓零调用（`:360` 仅注释） |
| rdma_get_cm_event | `src/rdma_common.c:112` | 阻塞取事件；全部等待共用此一处 |
| rdma_ack_cm_event | 共 9 处：`src/rdma_common.c:123,132`；服务端 `src/rdma_server.c:190,262,375`；客户端 `src/rdma_client.c:75,98,228,411` | 归还事件；**取数据必须在 ack 前** |
| rdma_event_str | `src/rdma_common.c:129,130,135` | 事件名转字符串，打印用 || rdma_get_peer_addr | 服务端 `:269` | 从 cm_id 取对端 sockaddr（演示用） |
| rdma_create_qp | 服务端 `:113`/客户端 `:163` | (cm_id,pd,&attr)：**CM 与 verbs 的唯一握手点**，此后 QP 状态归 CM 管 |
| rdma_destroy_qp | 服务端 `:383`/客户端 `:418` | 销毁前必须已无未决 WR |
| rdma_destroy_id | 服务端 `:385,413`（连接 id+监听 id）/客户端 `:420` | QP 未摘除时返回 EINVAL |
| rdma_destroy_event_channel | 服务端 `:418`/客户端 `:451` | 永远压轴 |

**B. 资源对象线（ibv_*，5 建 + 4 销）**

| API | 调用点 | 角色与参数要点 |
|---|---|---|
| ibv_alloc_pd | 服务端 `:50`/客户端 `:110` | 唯一参 `cm_id->verbs`——须在 resolve 之后才有效 |
| ibv_create_comp_channel | 服务端 `:66`/客户端 `:122` | 完成通知通道，与 CM 通道是两条线 |
| ibv_create_cq | 服务端 `:80`/客户端 `:135` | (verbs,**CQ_CAPACITY=16**,NULL,ch,0) |
| ibv_req_notify_cq | 服务端 `:93`/客户端 `:145`/收割器 `src/rdma_common.c:156` | 一次性通知，get_cq_event 后须重挂 |
| ibv_reg_mr / ibv_dereg_mr | `src/rdma_common.c:70` / `:104` | 全仓唯一注册/注销点，7 次注册全经此 |
| ibv_dealloc_pd | 服务端 `:407`/客户端 `:446` | 名下 MR/CQ/QP 未清空则 EBUSY |
| ibv_destroy_cq | 服务端 `:391`/客户端 `:426` | QP 还引用着则 EBUSY |
| ibv_destroy_comp_channel | 服务端 `:397`/客户端 `:432` | 必须晚于 destroy_cq |

**C. 数据面（2 个）**

| API | 调用点 | 角色与参数要点 |
|---|---|---|
| ibv_post_send | 服务端 `:341`；客户端 `:281,339,370` | 三种 opcode 各登场一次：SEND（两端元数据）、RDMA_WRITE（`:339`）、RDMA_READ（`:370`）；单边另填 wr.rdma.**rkey/remote_addr**（`:336-337,367-368`） |
| ibv_post_recv | 服务端 `:229`/客户端 `:194` | 仅两处，都在连接建立前预挂（第 09 篇的窗口纪律） |

**D. 完成收割线（4 个，全在 `src/rdma_common.c`）**

| API | 调用点 | 角色与要点 |
|---|---|---|
| ibv_get_cq_event | `:148` | 阻塞等通知带回活跃 CQ 指针 |
| ibv_poll_cq | `:168` | 非阻塞收割，可返回 0，须循环（`:167-177`） || ibv_ack_cq_events | `:189` | 第二参恒 **1**=ack 通知次数而非 WC 数 |
| ibv_wc_status_str | `:183` | WC status 与 errno 异值域，打印必经此 |

## ③ 外部连接（薄封装层映射）

61 个调用点里近半不直接出现在业务代码中，而是被 6 个自研封装收编：`rdma_buffer_alloc/register`（`src/rdma_common.c:40,61`→ibv_reg_mr+calloc）、`rdma_buffer_free/deregister`（`:82,94`→ibv_dereg_mr+free）、`process_rdma_cm_event`（`:107`→get+双校验+ack）、`process_work_completion_events`（`:141`→get_cq_event+req_notify+poll+ack 四连）。图谱 22 条 calls 边里，业务函数到 verbs 世界的通路**全部经过这 6 个封装**——这也是 verbs 原语只落在公共层 4 个函数内的原因。

## ④ 数据流（一次完整运行的全部调用骨架）

把表格按执行顺序压成时序骨架（S=服务端、C=客户端，61 个调用点归并排布）：

```
S: create_event_channel→create_id→bind_addr→listen
C: create_event_channel→create_id→resolve_addr→[ADDR_RESOLVED]→resolve_route→[ROUTE_RESOLVED]
C: alloc_pd→create_comp_channel→create_cq→req_notify_cq→create_qp→post_recv ┐
S: ←[CONNECT_REQUEST]→ alloc_pd→…同四件套…→create_qp→post_recv           ├ 两端镜像
S: accept →[ESTABLISHED]← C: connect                                        ┘
C: reg_mr×2→post_send(SEND) → S: [WC]→alloc+register→reg_mr→post_send(SEND)
C: [WC×2]→post_send(WRITE)→[WC]→post_send(READ)→[WC]→memcmp
C: disconnect → S: [DISCONNECTED]
两端: destroy_qp→destroy_id→destroy_cq→destroy_comp_channel→dereg×N→dealloc_pd→destroy_event_channel
```

## ⑤ 设计决策

- **一 API 一职责的分层自觉**：CM 线从不碰数据（最贴近的是 conn_param 两个深度字段），verbs 线从不碰连接状态（QP 状态迁移全部让渡给 rdma_cm）——本仓 0 次调用 `ibv_modify_qp` 不是漏写，而是选了 `rdma_create_qp` 路线的必然结果。
- **同步等待贯穿始终**：61 个调用点里没有"投递后不等"的用法——每次 post 紧跟收割（第 05 篇）。C 组 4 个 post_send 旁边各钉着一个 WC 等待，这是全仓读起来像顺序脚本的原因。
- **收割线 4 个 API 只在公共层出现一次**：两端对 CQ 的所有操作压进 `process_work_completion_events` 一个函数体——要改并发收割策略（批量 poll、超时），只动一处。

## ⑥ 新人提示（坑与勘误）

1. **表里"缺席"的 API 同样是信息**：没有 ibv_get_device_list/ibv_open_device（设备发现全由 rdma_cm 的 resolve 代办）、没有 ibv_modify_qp（状态迁移由 CM 代办）、没有 ibv_query_device/port（容量写死 `src/rdma_common.h:47-51`）——**rdma_cm 帮你省掉的每个调用，都是裸写 ibverbs 时要自己补的**。想知道省了多少事，拿本表对 `ibv_rc_pingpong`（纯 ibverbs 例子）数差集。
2. **rdma_ack_cm_event 的 9 个调用点是数出来的**：封装内错误路径 2 处（`src/rdma_common.c:123,132`）+两端成功路径 7 处——每个 `process_rdma_cm_event` 成功调用都配对一次调用方 ack，少一个就泄漏一个事件结构体。
3. **post_send 的 SGE 都只有 1 个元素**（num_sge=1，如 `src/rdma_client.c:277`）而 QP 容量是 MAX_SGE=2——分散/聚集（多段内存拼一个报文）这个 SGE 的本职用法完全没演示，别误以为 num_sge 恒为 1。
4. **conn_param 没进速查表因为它不是 verbs API**：它是 rdma_connect/accept 的参数结构（客户端 `src/rdma_client.c:208-214`、服务端 `src/rdma_server.c:239-243`），三个字段的语义坑在第 08 篇勘误④。
5. **表内行号是本仓快照**：上游 animeshtrivedi/rdma-example 若演进，以本仓 `src/` 为准；引用时带 `file:line` 锚可直接 grep 验证。

——速查表收好全仓的"怎么做"；最后一篇退一步问"这样做离生产还差什么"。
