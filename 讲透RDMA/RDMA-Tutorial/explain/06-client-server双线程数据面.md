# 06 · client/server 双线程数据面：imm_data 与 echo 基准

## ① 角色定位

server.c（214 行）与 client.c（218 行）是全仓的"负载层"：建连（05 篇）完成后由 main.c:34-38 分发进入，跑完 echo 吞吐基准再交还控制权。图谱占"服务端/客户端工作负载线"两层（第 11/12 层），tour 第 13/14 步。两文件是刻意的镜像结构：run_server/run_client（server.c:166-213 / client.c:167-217）各创建**恰好 1 个** joinable 工作线程（num_threads=1，server.c:169/client.c:170），线程本体 server_thread/client_thread_func 是全仓仅有的两个热循环。"单线程 + 忙轮询 CQ + 绑核"是低延迟基准的经典最小配置——没有锁、没有上下文切换、没有事件通知开销。

协议分工：**server 是发令者**——广播 START 启动、计满 TOT_NUM_OPS 广播 STOP 收尾、全程只回显；**client 是执行者**——等齐 START 后预投发送，此后对每条收到的消息回显回去。吞吐统计（Mops/s）两侧各自打印（server.c:154/client.c:155）。

## ② 内部结构

**server_thread 五阶段**（server.c:12-164）：

1. 准备：本地变量从全局直取（server.c:16-33，num_peers=ib_res.num_qps L18、num_wc=20 L23）→ **重复 calloc**（见 ⑤②：L43 一次、L54 又一次）→ 绑核 CPU 0（L47-51）→ 预投 num_peers×num_concurr_msgs 个 SRQ 接收，缓冲按 `(buf_offset+msg_size)%buf_size` 环形切分（L57-63）。
2. **启动**：向全部对端 post **0 字节** SEND_WITH_IMM，imm=MSG_CTL_START（L66-69，控制枚举 ib.h:35-38：START=100/STOP=101）。
3. **echo 主循环**（L71-111）：ibv_poll_cq 批量取完成（L73）→ 每个 RECV：ops_count++（L90）；第 50 万次打起点时间戳（L93-95，NUM_WARMING_UP_OPS，ib.h:15）；第 1000 万次打终点并置 stop（L96-100，TOT_NUM_OPS，ib.h:16）；取 imm_data 与缓冲指针（L103-104，msg_ptr=(char*)wc.wr_id）；**回显** post_send(msg_size,…,imm_data,qp[imm_data],msg_ptr)（L105）；原缓冲补投接收（L108）。
4. **停止**：广播 0 字节 STOP，wr_id 填魔数 IB_WR_ID_STOP（L114-117，ib.h:14）→ 排空循环数 SEND 完成事件里的 STOP 魔数直到收齐 num_peers 个（L119-148）。
5. 统计与退出（L151-157）：duration 微秒、throughput=ops/duration 即 Mops/s。

**client_thread_func 镜像五阶段**（client.c:12-165）：等待 START（L64-88，忙旋 `do{poll}while(n<1)` L66-67，每条 RECV 先补投 L77 再数 START 到齐 L79-85）→ 预投发送 num_peers×num_concurr_msgs 条，**imm 填循环变量 i**（L96）→ echo 主循环（L103-149，与 server 同构，STOP 数齐即停 L133-139）→ 统计（L152-155）。错误路径 pthread_exit(-1)（server.c:163/client.c:164），由 run_* 的 join 捕获（server.c:191-195）转为返回码。

## ③ 外部连接

向上：唯一调用方 main.c 的分发（main.c:34-38）。向下：三原语全用 ib.c——post_send（ib.c:76-99，IBV_WR_SEND_WITH_IMM L92、SIGNALED L93、imm 经 htonl L94）与 post_srq_recv（ib.c:101-121）；ibv_poll_cq 是数据面唯一直呼的 verbs 函数。资源面：全局直读 ib_res 六个字段（client.c:24-33/server.c:24-33）与 config_info 三参数。图谱上它是依赖图终端——只被 main 引用，引用 config/setup_ib/ib/debug 四层，无下游。

## ④ 数据流

**imm_data 的三义复用**是数据面的灵魂（所有 imm 都经 ib.c:94 htonl 发出、server.c:103/client.c:130 ntohl 还原）：

1. **控制字**：START/STOP 用 0 字节 SEND_WITH_IMM 携带（server.c:67/115）——控制信令搭数据的便车，零额外报文零额外字节，0 长度 SGE 在接收端照样产生带 imm 的 RECV 完成事件。
2. **发送方对端索引**：client 预投发送时 imm=循环变量 i（client.c:96），语义是"这条消息发往我的第 i 条 QP"（即第 i 个 server）。
3. **回显路由索引**：两侧收到 RECV 后按 qp[imm_data] 回显（server.c:105/client.c:142）。

**wr_id 的两种身份**同样精妙：接收 WR 的 wr_id=缓冲指针（client.c:57/77/146、server.c:59/108），完成事件里直接取回 `msg_ptr=(char*)wc.wr_id`（client.c:131/server.c:104）——免去任何查找表，补投与回显用同一指针；发送 WR 的 wr_id 平时为 0，仅 STOP 用魔数 IB_WR_ID_STOP 标记（server.c:115/139）。

**稳态流**：环形缓冲预投覆盖全池（容量=msg_size×num_concurr_msgs×num_qps，04 篇三因子），此后每完成一条就原位补投一条——池大小恒定，恰好由 num_concurr_msgs 限制在途深度。SRQ 让全部对端共享这个池：server 不必知道消息来自哪条 QP，**配对信息完全由 imm 携带**。

## ⑤ 设计决策

**① imm 拓扑假设（单 client 单 server 才严格成立）**：client 预投的 imm 是**自己视角的 server 索引**（client.c:96），而 server 回显把 imm 当**client 索引**用（server.c:105，配对约定"server qp[k] 连 client k"，05 篇）。两个索引空间只有 1×1 拓扑必然重合。多 client（N×N）时：client k 发往 server s 的消息带 imm=s，server 收到后回显给 qp[s]=client s 而非原主 client k——**数据不丢但 echo 配对错位**（每条 RECV 仍触发一条回显，op 守恒，基准照常跑完）；错位后流量退化为对角配对（c,c）间的乒乓循环（推断：错位消息的 imm 不再变化，client s 与 server s 互相回显）。更隐蔽的是 1 client×N server：server_s 收到 imm=s，但它的 qp 数=num_clients=1，qp[s≥1] 直接越界读指针数组（源码推演，未实测）——这组下标语义混用是复用 imm 做路由的固有代价，工程化要么改传真实 source rank，要么回到 per-QP RQ。

**② server.c 重复 calloc（实证泄漏）**：server.c:43-44 已 `wc=calloc(num_wc,…)`，server.c:53-55 在"pre-post recvs"注释下**再次 calloc 同一指针**——首次分配（20×sizeof(struct ibv_wc)）被覆盖泄漏；client.c:52 对应位置只有一次。对比两文件可见是复制粘贴残留：server 侧第一处 calloc 孤悬在变量声明与绑核之间，client 侧同位置没有。

**③ 热路径丢弃 post 返回值**：server.c:105/108、client.c:142/146 的回显与补投不检查返回值（预投阶段倒是查了，client.c:97）——基准代码"完成事件兜底一切"的取舍：若 post 失败，最终会以 CQ 错误或 op 数不达标的形式暴露。

**④ 预热窗口与统计口径**：计时从第 50 万次接收起算（server.c:93-95/client.c:126-128），到 1000 万次止；但分子 ops_count 是**全量**计数——server 报告值≈1000万/950万≈**系统性偏高 5%**（client 侧分子还含 START 控制帧，偏差更大）。读论文级数字时要意识到这把尺子的误差。

**⑤ 全 Signaled + 忙轮询**：每条发送都 IBV_SEND_SIGNALED（ib.c:93），配合无阻塞 poll（server.c:73、client.c:66-67/106）把每条消息的完成都显式化——简单但每条消息一个 CQE，吞吐上限被 CQ 事件率压住；生产代码会按 NUM_WR 批量+选择性 Signaled。

## ⑥ 新人提示

对读两文件时抓三组镜像：wait-START（client 等）vs 广播 START（server 发）；client 先预投**发送**（client.c:94-101）vs server 只预投**接收**（server.c:57-63）——echo 模型里 server 永远被动应答；STOP 双保险（server 数自己的 SEND 魔数 L138-146、client 数收到的 STOP L133-139）。调参入手点：num_concurr_msgs 直接改在途深度（预投数量与缓冲三因子联动）；msg_size 注意别超 IB_MTU=4096。排查三锚点：ops_count 的 debug 输出（server.c:91，需 make debug，debug.h:36）、CQ 错误状态打印（server.c:81-86 带 ibv_wc_status_str）、吞吐行（server.c:154）。最值得动手的练习：把 client.c:96 的 imm 改成 `config_info.rank`（真实身份），多 client 配对错位即修复一半——另一半在 server 侧仍按 imm 索引 qp，改完再观察 N×N 下配对表（05 篇 L89-90 日志）与流量归属的变化，会对"SRQ 无来源信息"有切身体感。
