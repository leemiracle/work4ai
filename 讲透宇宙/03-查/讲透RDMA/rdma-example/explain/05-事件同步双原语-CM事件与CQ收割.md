# 05 事件同步双原语：process_rdma_cm_event 与 process_work_completion_events

> 对应导览第 5 步「事件同步双原语」｜节点：`function:src/rdma_common.c:process_rdma_cm_event`、`function:src/rdma_common.c:process_work_completion_events`

## ① 角色定位

rdma_cm 与 ibverbs 都是**异步事件驱动**的 API，但本仓两端代码读起来像顺序脚本——"发一个请求、等它完成、再下一步"。把异步翻译成顺序的，正是这对函数：前者阻塞等待并校验指定的连接管理（CM）事件，后者完成"等通知→重挂请求→poll 收割→ack"的完成队列（CQ）四步收割。图谱里它们是第 4 层「CM/CQ 事件同步原语」仅有的两个节点，却吸走了全仓最多的 calls 边——**两端程序的每一步等待都经过它们**，没有第三个等待点。

## ② 内部结构

**`process_rdma_cm_event(echannel, expected_event, &cm_event)`**（`src/rdma_common.c:107-138`）三段：
1. `rdma_get_cm_event`（`:112`）——阻塞取出事件通道上的下一个事件，失败返回 `-errno`。
2. status 校验（`:119-125`）：`status != 0` 视为坏事件，**先 ack 再返回负 status**（`:123`）——错误路径也不忘归还事件资源。
3. 类型校验（`:127-134`）：实际事件 != 期望类型时同样先 ack（`:132`）再返回 -1，错误消息用 `rdma_event_str` 同时打印"收到什么/期待什么"。
4. 成功路径只返回 1，**不 ack**——`:136` 注释明示"The caller must acknowledge the event"，ack 责任移交调用方（因为调用方往往还要从事件里取数据，见⑥-2）。

**`process_work_completion_events(comp_channel, wc, max_wc)`**（`src/rdma_common.c:141-193`）四段：
1. `ibv_get_cq_event`（`:148-150`）——阻塞等完成通道通知，顺便带回是哪个 CQ 有活动（`&cq_ptr`）。
2. `ibv_req_notify_cq(cq_ptr, 0)`（`:156`）——**立即重新挂上**通知请求，防止收割期间到达的新 CQE 落入无通知窗口。
3. do-while 收割循环（`:167-177`）：反复 `ibv_poll_cq` 直到凑满 `max_wc` 个 WC；`:161-165` 注释直言这与 pthread 条件变量同一逻辑——poll 可能返回 0（虚假唤醒），要循环。
4. 逐 WC 状态校验（`:180-187`）：任何一个 `wc[i].status != IBV_WC_SUCCESS` 都打印 `ibv_wc_status_str` 并返回 `-(wc[i].status)`；全部通过则 `ibv_ack_cq_events(cq_ptr, 1)`（`:189-191`）——注释强调 ack 的是**1 个事件通知**而非 WC 个数，最后返回 total_wc。

## ③ 外部连接（图谱 calls 边）

CM 侧 6 条边、CQ 侧 3 条边，覆盖两端全部等待点：

**CM 事件**（每条边 = 一个"期望事件类型"锚点）：
- client `client_prepare_connection → process_rdma_cm_event`：代码内两次调用，等 ADDR_RESOLVED（`src/rdma_client.c:67-69`）与 ROUTE_RESOLVED（`:90-92`）。
- client `client_connect_to_server →` 等 ESTABLISHED（`src/rdma_client.c:221-223`）。
- client `client_disconnect_and_clean →` 等 DISCONNECTED（`src/rdma_client.c:403-405`）。
- server `start_rdma_server →` 等 CONNECT_REQUEST（`src/rdma_server.c:173-175`）。
- server `accept_client_connection →` 等 ESTABLISHED（`src/rdma_server.c:254-256`）。
- server `disconnect_and_cleanup →` 等 DISCONNECTED（`src/rdma_server.c:367-369`）。

**WC 收割**：
- server `send_server_metadata_to_client`：两次调用各等 1 个 WC（收客户端元数据 `src/rdma_server.c:286`、发服务端元数据 `:350`）。
- client `client_xchange_metadata_with_server`：一次等 **2 个** WC（自己的 send + 对端的 recv，`src/rdma_client.c:292-293`）。
- client `client_remote_memory_ops`：WRITE 与 READ 各等 1 个（`:348-349, 379-380`）。

## ④ 数据流

一次 RDMA WRITE 的 WC 旅程（串起第 12 步数据面）：客户端 `ibv_post_send`（`src/rdma_client.c:339`）→ 网卡取 WR、DMA 读本地 src、经 RC 流量写穿远端内存 → 完成 → **CQE 入 CQ** → 完成通道 fd 变可读 → 本函数 `ibv_get_cq_event` 醒来拿到 cq_ptr → 重挂通知 → poll 把 CQE 翻译成 `struct ibv_wc`（含 status/opcode/byte_len）→ 校验 SUCCESS → ack → 返回 1，调用方才继续。CM 事件旅程类似：内核 CM 状态机把连接事件排入 event channel → `rdma_get_cm_event` 取出 `struct rdma_cm_event`（含 `id`/`status`/`event` 三关键字段）→ 双重校验 → 调用方消费 → `rdma_ack_cm_event` 归还。

## ⑤ 设计决策

- **为什么收到通知后要立即 req_notify 再收割**（`:156`）：CQ 通知是一次性（边沿触发）的——不立即重挂，收割期间新到的 CQE 将来不会产生任何通知，程序会永远沉睡。先重挂后收割是标准 ibverbs 模板的固定姿势。
- **为什么 poll 要循环**：注释（`:161-165`）自答"Same logic as MUTEX conditional variables"——`ibv_poll_cq` 本身非阻塞、可返回 0，条件满足与否要靠循环重查。教学上这是全仓最值得背下来的一段注释。
- **为什么 CM 的 ack 拆两半**（错误路径函数内 ack、成功路径调用方 ack）：事件结构体 ack 后即失效，而成功路径调用方要从 `cm_event->id` 取连接标识（server `src/rdma_server.c:184` 先取 id、`:190` 才 ack）——函数无法代劳这个消费动作，索性把 ack 时机交给唯一知道"何时用完"的一方。
- **返回值语义**：成功返回正数（CM 恒 1，CQ 为 total_wc），失败返回负数（-errno / -status / -1）——调用方用 `ret != 1`、`ret != 2` 精确断言期望的完成数（如 `src/rdma_client.c:294`）。

## ⑥ 新人提示（坑与勘误）

1. **收割循环可能忙等死循环**：do-while（`:167-177`）在 poll 返回 0 且 total_wc < max_wc 时会空转——它隐含假设"通知到达时所有期望 WC 都已入队"。本例 client 等 2 个 WC（`:292-293`）恰好 send/recv 同时完成所以成立；若对端只完成了一部分，这里会烧 CPU 等剩下的。生产代码应加超时或改事件数驱动。
2. **cm_event->id 必须在 ack 前拷走**：ack 释放事件结构体（`src/rdma_server.c:185-189` 注释专门解释），先 `cm_client_id = cm_event->id`（`:184`）再 ack（`:190`）的顺序不可颠倒——本仓服务端的写法是官方推荐姿势。
3. **WC status 不是 errno**：`:185` 返回 `-(wc[i].status)`，值域是 `ibv_wc_status` 枚举（IBV_WC_WR_FLUSH_ERR=5 等），与 errno 数字空间无关，打印必须走 `ibv_wc_status_str`。
4. **ack 计数=1 的含义**：`ibv_ack_cq_events(cq_ptr, 1)`（`:189-191`）ack 的是**事件通知次数**；WC 数量由 poll 自然消耗、无需逐个 ack。把 1 改成 total_wc 是新手高频错误，会导致内核事件计数错乱、后续 get_cq_event 行为异常。
5. **本函数不区分收/发 WC**：client 等 2 个 WC 时（`src/rdma_client.c:289-298`）拿到的是"send 完成 + recv 完成"两枚混排的 WC，函数只查 status 不查 opcode——顺序教学够用，真要区分哪个先完成得自己看 `wc[i].opcode`。

——至此公共层 9 个函数讲完 8 个，剩下三个辅助函数（get_addr 与 show 族）留在下一篇收尾。
