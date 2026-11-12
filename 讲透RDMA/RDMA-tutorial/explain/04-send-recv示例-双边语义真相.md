# 04 send/recv 示例：双边语义的真相——实际是一次单向演示

> 对象：`example code/rdma_send_recv/client.c`（299 行）与 `server.c`（280 行）；行号锚经源码核实（commit `c760004`）。**本篇核心是勘误：名为双边示例，实际行为是单向。**

## 一、角色定位

send_recv 组是教程 2.3 节（two-sided verb）的配套示例，`example code/README.md:3` 标注「rdma_send_recv: two-sided verb(send/recv)」。它采用与 write_read 组相反的工程形态：**无公共库，client.c/server.c 各自镜像自包含**，两文件约 300/280 行、逐函数对称（die/build_context/build_qp_attr/poll_cq/post_receives/register_memory/on_event 几乎逐行相同）。这使它成为读「单文件即可看全 RDMA 双边通信」的入门样本，也是与 write_read 组做「找不同」练习的对照组（MR 数量、权限、状态机、预挂时机的差异）。但必须先讲清它的真实行为：**图谱/tour 第 11/12 步称「server 会主动 SEND 问候、client 收完回复再断开」——代码证据显示这条回路从未闭合**，实况是 client 发一条、server 收一条、client 拍屁股走人。

## 二、内部结构

client.c（主动端）：struct context（L14-L21，与 rdma-common.c:16-L23 同构）+ struct connection（L23-L34，**多一个 num_completions 计数器 L33**，无状态机枚举）；main（L53-L84）解析地址+resolve_addr+事件循环；on_addr_resolved（L179-L203）建 QP/注册内存；on_connection（L223-L248）构造并发送问候；on_completion（L205-L221）按 opcode 打印并计数；poll_cq（L127-L142）后台收割。server.c（被动端）：struct connection（L21-L29）**没有 id 字段、也没有计数器**，只有 qp+两块 MR+两块缓冲；main（L47-L81）硬编码端口 22222（L57 `htons(22222)`）；on_connect_request（L191-L214）建 QP+注册内存+**预挂 RECV（L208）**+accept；on_completion（L176-L189）按 opcode 打印；on_connection（L216-L240）问候函数——**死代码，下详**。

## 三、外部连接

依赖面与 write_read 完全一致（rdma_cma+ibverbs+pthread，Makefile:5），但编译仅 `-Wall`（Makefile:3），不像 write_read 用 `-Werror`。与教程 2.3 节的连接最直接：tutorial.md:186-L195 的发送请求代码块（opcode=IBV_WR_SEND+SIGNALED）即 client.c:233-L245 的骨架——注意教程版多了 `IBV_SEND_INLINE`（tutorial.md:187），示例实际未用。与 write_read 组的镜像关系：本组两文件自带的 build_context/build_qp_attr/post_receives/register_memory/poll_cq 五函数，就是 rdma-common.c 对应函数（L100-L141/L259-L307）的「前身拷贝」——write_read 组把它们抽公共库后，入口才瘦到 110 行。readme.md:8-L9 的启动命令（`./server`/`./client <地址> <端口>`）与 Makefile:7 的产物名（server/client）一致，无 write_read 那种命令名错误。

## 四、数据流

**实际运行时序（单向真相）**：server 起 listener 端口 22222→client resolve_addr/resolve_route→ESTABLISHED→client 的 on_connection 把 `"message from active/client side with pid %d"` 写进 send_region（L229）并 post SEND（L245）→server 网卡收到，因 on_connect_request 已预挂 RECV（L208），数据落进 server 的 recv_region，CQE 产生→server poll 线程 on_completion 走 RECV 分支打印 `received message: ...`（L181-L184）→**server 的 ESTABLISHED 分支什么都不做**（L269-L271）→client 侧 SEND 完成产生 CQE→client on_completion 走 SEND 分支打印（L214-L215）→`++conn->num_completions == 1`（L219）立即 `rdma_disconnect`（L220）→双方收 DISCONNECTED 各自清理（client 返回 1 退循环 L268，server 返回 0 继续守听 L260）。全程 client 从未预挂 RECV，也从未收到任何字节。

**死代码三处证据**：①server.c:269-L271——`RDMA_CM_EVENT_ESTABLISHED` 分支里 `r = on_connection(event->id->context);` 整行被注释（L270），只余 `r = 0;`（L271），问候函数 on_connection（L216-L240）因此永不执行；②client.c:198——on_addr_resolved 里 `post_receives(conn);` 被注释（L198），client 的 RQ 永远空；③server 的 on_connection 本身还有第三重锈迹：构造 WR 时**漏设 `wr.wr_id`**（L226-L235 无赋值，对照 client.c:235 有），一旦真被启用，完成回调拿到的 wr_id 是 memset 后的 0，RECV 分支解引用即崩——它连「随时可恢复启用」的资格都没有。

## 五、设计决策

两处注释**互为因果、不是孤立失误**：若只取消 server 的注释让 server 发问候，而 client 仍无预挂 RECV，server 的 SEND 会撞上 RNR（receiver not ready）；本组 client 的 `rdma_connect` 传全零 cm_params（L295-L296，无 rnr_retry_count），RNR 重试为 0 即直接报错。也就是说作者（或上游演进过程）把「回信-收信」这条腿整条砍掉才保持可运行——砍得自洽，但从未更新 README/教程的叙事。从教学视角看这反而有一个意外好处：**两行注释本身成了最直观的教具**——恢复双向只需取消两处注释并补上 server 的 wr_id 赋值，diff 不到五行，正好拿来当练习。其余设计对照：本组 register_memory 给两块 MR 都挂 `LOCAL_WRITE|REMOTE_WRITE`（L170/L176）——双边 verb 本不需要远端权限，这是从 write_read 语义带过来的冗余授权；num_completions==1 即断（L219-L220）写死了「一次发送就拜拜」的生命周期；server 的 poll 线程与 client 一样永不退出（L129 while(1)），进程退出靠 main return，存在教学级的拆除时序竞态（main 销毁资源时 poll 线程可能仍在 comp_channel 上阻塞）。

## 六、新人提示

阅读顺序建议先 server 后 client：server 的 on_connect_request（L191-L214）一次看完「建 QP+注册+预挂+accept」完整被动端流程，比 write_read 分层版更连贯。**看代码前先跑一遍建立正确预期**：两侧各打印一条、client 先退——别等一条永远不来的「server 回复」。三个易被坑点：一，想当然按 tour 描述找 server 发送路径，注意 L270 那行注释，on_connection 是陈列品不是活代码；二，`wc->opcode & IBV_WC_RECV` 用位与而非相等判断（L181/L212）是因为 opcode 可能叠加立即数标志位，这是 ibverbs 的惯例写法；三，本组 client.c 的 struct connection 没有 write_read 版的 peer_mr/状态机——双边 verb 不需要钥匙交换，结构差异本身就是两种 verb 的语义对照表。把「恢复双向」当结业实验：补 wr_id、取消两处注释、给 client 的 cm_params 设 rnr_retry_count，三步做完你对 RNR 机制的理解就到位了。
