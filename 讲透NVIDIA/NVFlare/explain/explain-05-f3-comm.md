# explain-05 · f3 通信底座：Cellnet 如何托起整个 NVFlare

## ① 角色定位

f3 是 NVFlare 2.x 的消息中枢：admin 命令、任务分发、作业提交、文件流、心跳注册全走它。源码在 `nvflare/fuel/f3/`，自称 **FCI（Flare Communication Interface）**（`nvflare/fuel/f3/communicator.py:58`）；社区俗称 "FireFighting Fabric"，但仓库内无此字样，命名以 FCI/Cellnet 为准。核心抽象只有一个：**Cell**——server、client、job runner、admin console 都是 cell，靠 FQCN（全限定 cell 名）互相寻址，用 channel/topic 二级主题路由。分层：drivers 传输 → sfm 连接管理 → Communicator/Endpoint → CoreCell 路由 → StreamCell 分块流 → Cell 请求回复。

## ② 内部结构

**FQCN 寻址**。FQCN 是祖先名点号串联，合法字符 `^[A-Za-z0-9_.~-]*$`（`nvflare/fuel/f3/cellnet/fqcn.py:18`）。core_cell 文档给出经典例子（`nvflare/fuel/f3/cellnet/core_cell.py:334`）：`server`（根）、`server.J12345`（服务器上某 job 的 cell）、`client_1.J12345.R0`（client_1 上该 job 的 rank0）——**job 与 rank 都是 cell 而非进程**，这是 2.x 单进程模拟器能成立的前提。

**channel/topic 路由**。消息头全带 `cn__` 前缀（`nvflare/fuel/f3/cellnet/defs.py:14`）。channel 枚举见 `defs.py:160`——注意线上取值的"考古层"：`CLIENT_MAIN="admin"`、`SERVER_MAIN="task"`，是 2.x 迁移前的历史语义，常量名极易误导。回调查表在 `nvflare/fuel/f3/cellnet/registry.py:44`：精确 `(channel,topic)` 未命中先降级 `channel:*` 再降级 `*:*`，这就是各处 `topic="*"` 通配注册能工作的原因。

**Message 与 Shareable 的关系**。f3 的信封是 `Message(headers, payload)`（`nvflare/fuel/f3/message.py:30`）；联邦层的 Shareable 是**装进 payload 的内容物**。序列化在 `encode_payload`（`nvflare/fuel/f3/cellnet/utils.py:133`）：payload 为 None 记 NONE、bytes 族记 BYTES、其余一律 FOBS 序列化，对端 decode 再 fobs.loads。FOBS 支持 buffer 分片，配合 streaming 层把大 payload 切块传输。

**四类原语与 `__getattr__` 魔法**。`Cell(StreamCell)`（`nvflare/fuel/f3/cellnet/cell.py:231`）按信道动态分派：调用 `send_request/broadcast_request/fire_and_forget` 时，流信道转本类 `_xxx` 版本，否则转 CoreCell 同名方法（`cell.py:257`）。非流信道白名单见 `cell.py:42`（CLIENT_MAIN/SERVER_MAIN/RETURN_ONLY 等八大信道直发）。CoreCell 的 `send_request` 其实是单目标 broadcast（`core_cell.py:1471`），真正的核心是 `broadcast_multi_requests`——注释自称 "the core of the request/response handling. Be extremely careful!"（`core_cell.py:1483`），并记录了极快网络下 waiter 双线程竞态 bug（`core_cell.py:1489`）。任务书提的 "get_cb_result" 原语并不存在，流路径对应物是 `_get_result`（`cell.py:410`）。

**三段式流请求**。`_send_one_request`（`cell.py:518`）把一次请求拆成 sending → remote processing → receiving 三段等待（`cell.py:546`），每段支持 progress 续命：超时后查传输进度，仍有字节流动就继续等——大模型上传不会被固定 timeout 误杀。回复走专用 RETURN_ONLY 信道（`cell.py:238` 注册）。

**Adapter 回调桥**。流信道的请求回调经 `Adapter` 包装（`cell.py:89`）：收到 blob 首字节后解码 payload、调用户回调，结果经 RETURN_ONLY 流回 origin。`_register_request_cb` 同时向 core_cell 注册原回调、向 blob_streamer 注册 Adapter（`cell.py:705`）——双轨是因为 broadcast_multi_requests 可能直穿 core_cell。PASS_THROUGH 头可让接收端不解码张量、仅持 LazyDownloadRef 供下一跳下载（`cell.py:104`）。

**传输与安全**。driver 按 URL scheme 选择：tcp/stcp（`nvflare/fuel/f3/drivers/tcp_driver.py:60`）、grpc/grpcs 及 agrpc 变体（`grpc_driver.py:228`）、http/https、file；**本仓无 inproc driver**（任务书所列有误）。端到端加密由 CellCipher 承担（`cellnet/cell_cipher.py:189`），身份由 CellIdentityResolver 按 FQCN 前缀/精确映射校验 mTLS 对端（`cellnet/identity.py:100`）。

## ③ 外部连接

- **服务端运行时**：`_register_cellnet_cbs` 在 SERVER_MAIN 信道注册 Challenge/Register/Quit/HEART_BEAT/REPORT_JOB_FAILURE 五个 topic（`nvflare/private/fed/server/fed_server.py:438`）——客户端注册与心跳都在这层；SERVER_PARENT_LISTENER 供上级 server 中继（`fed_server.py:466`）。
- **job cell 工厂**：`create_job_cell`（`fed_server.py:630`）为每个 job 起 FQCN=`server.<job_id>` 的子 cell，secure 模式注入证书 credentials，start 后挂 NetAgent 与 ServerCommandAgent（`fed_server.py:667`）。
- **客户端运行时**：CommandAgent 在 CLIENT_COMMAND（admin 命令）与 AUX_COMMUNICATION（aux 消息）信道注册通配回调，aux 消息按 topic dispatch 给引擎（`nvflare/private/fed/client/command_agent.py:47`）。
- **运维面**：NetAgent 在 CELLNET 信道注册 route/peers/conns/speed/echo/stress 等诊断 topic（`nvflare/fuel/f3/cellnet/net_agent.py:129`），是排查路由的现成工具箱。
- **管理面落点**：上一篇的 HCI 命令与文件上传，最终都走 `send_blob`（`nvflare/fuel/f3/stream_cell.py:108`）与 blob 回调。

## ④ 数据流

以一轮训练往返为例：① client 在 AUX_COMMUNICATION 收到 DO_TASK，executor 产出 Shareable；② 结果装入 `new_cell_message({}, shareable)`（定义在 `nvflare/fuel/f3/cellnet/utils.py:78`）经 SERVER_MAIN 发往 job cell；③ FOBS 编码并注入 NUM_RECEIVERS；④ StreamCell 把 payload 切块流过 tcp/grpc 连接，driver 由 URL scheme 选定；⑤ 对端 blob 回调聚齐后，Adapter 解码出 Shareable，回调返回的 reply 走 RETURN_ONLY 流回；⑥ 发起方 `_process_reply` 用 STREAM_REQ_ID 关联 waiter 唤醒调用线程（`cell.py:643`）。失败路径同样明确：接收端拒绝流时回发 stream error，`_process_stream_error` 校验 failed destination 归属后置 waiter 为 COMM_ERROR（`cell.py:655`）；server job cell 遇不可恢复的 blob 尺寸错误直接 `os._exit(1)` 快速失败防挂死（`cell.py:135`）。

## ⑤ 设计决策与批判

- **"一切皆 cell"**：统一寻址让 simulator 单进程建起全量 server/client/job cell；代价是概念栈深（Message→FOBS→blob→chunk→frame 五层），排障必须逐层对账。
- **`__getattr__` 动态分派双刃剑**：流/非流信道共用一套 API，但方法名不可跳转、拼写错误运行时才炸，报错点离调用处隔一层闭包。
- **信道常量名与线上值不一致**（CLIENT_MAIN="admin"）是历史包袱，也是新人最大误读源。
- **CoreCell 全局 ALL_CELLS 类字典**（`core_cell.py:289`）+ 同名 FQCN 直接报错：单进程 cell 名唯一性靠全局字典，测试忘 stop 会污染后续用例。
- **进度感知超时**（`cell.py:421`）解决大传输被误杀的真问题，但 timeout 语义变成"无进度窗口"而非总时限，调用方易误以为有硬截止。

## ⑥ 新人提示

1. 读任何 channel 相关代码，先翻 `defs.py:160` 对照线上取值再定语义。
2. 追消息走向靠 `req_id`/`stream_req_id` 贯穿日志，同一 id grep 串起全链。
3. 自定义通信的标准入口是 `register_request_cb` + topic 常量（参考 `nvflare/private/fed/server/fed_server.py:438` 的五连注册），不要绕过 Cell 直接摸 driver。
4. 传输问题先分三层：连接层看 EndpointState（`nvflare/fuel/f3/endpoint.py:18`）、流层看 StreamFuture.error、业务层看 RETURN_CODE（`defs.py:81` 十四种取值）。
5. `fuel/f3/qat/` 不是量化，是 f3 自带的多 cell 测试场（net_config*.json 定义拓扑、run_cell.py 起 cell），学原语比读文档快。
