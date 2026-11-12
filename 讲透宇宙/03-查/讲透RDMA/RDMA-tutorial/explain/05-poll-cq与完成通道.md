# 05 poll_cq 与完成通道：阻塞收割模型

> 对象：`rdma-common.c` 的 `poll_cq`（L242-L257）及其配套 comp_channel 机制；教程 2.3.5（tutorial.md:197-L218）互证；行号锚经源码核实（commit `c760004`）。

## 一、角色定位

poll_cq 是 RDMA 编程「下半场」的全部：上半场 post 请求，下半场收割完成通知（CQE）。本仓的 poll_cq 是**event-triggered polling 策略的标准实现**——教程 2.2 节五参数中 poll 策略（tutorial.md:88）的代码落点，也是 ONBOARDING 定义的「全仓最重要互证锚点」：同一份 14 行函数在 tutorial.md:202-L217 作为教材、在 rdma-common.c:242-L257 作为生产路径、在 send_recv 两文件（client.c:127-L142、server.c:124-L139）作为镜像前身，三处一字不差。它以独立线程形态存在（build_context L118 pthread_create），是整个示例「唯一的并发构件」——main 线程跑 rdma_cm 事件循环、poll 线程跑 CQ 收割，两条线程经 `conn` 指针共享状态、由 RDMA 硬件的事件流串行化。

## 二、内部结构

函数本体四行骨架+两层循环：

- 外层 `while (1)`（L247）：进程生命周期内永不退出；
- `ibv_get_cq_event(comp_channel, &cq, &ctx)`（L248）：**阻塞**睡眠直到 CQ 有事件——这是与 busy polling 的本质分界，CPU 在此让出；
- `ibv_ack_cq_events(cq, 1)`（L249）：确认取走 1 个通道事件（ibverbs 的 channel 事件需要显式 ack 才能继续计数）；
- `ibv_req_notify_cq(cq, 0)`（L250）：**重新 arm** CQ，下一轮完成才能再触发通道事件；
- 内层 `while (ibv_poll_cq(cq, 1, &wc))`（L252）：非阻塞排空 CQ，每次取 1 个 WC 喂给 `on_completion(&wc)`（L253），取空返回 0 退回外层继续睡。

配套设施分散在 build_context：comp_channel 创建（L114）、CQ 创建时把 channel 挂上（L115 第五参）、首次 arm（L116）。收割到的 `struct ibv_wc` 里两个字段被下游消费：`wc->wr_id`（post 时填的 conn 指针，on_completion L182 反查连接）与 `wc->opcode`（RECV/SEND/RDMA 分派依据，L187）。

## 三、外部连接

**上游**是网卡硬件：每次 post 的请求完成（send_flags 含 IBV_SEND_SIGNALED，rdma-common.c:218/L320）产生 CQE 入 CQ，CQ 首个 CQE 触发 channel 事件唤醒本线程。**下游**是 on_completion（L253）：每个 CQE 必经此处，RECV 完成推进 recv_state、SEND/RDMA 完成推进 send_state——第 06 篇的状态机靠本函数逐事件供油。**横向连接**三路：教程 2.3.5（tutorial.md:199）明言「busy polling 就不需要前三行代码，直接循环地 poll cq」——把 L248-L250 删掉、内层 while 提到外层即得 busy 版；send_recv 组的同名函数（client.c:127-L142）逐字符相同，证明 write_read 公共库是直接收编而非重写；paper 线的 HERD 笔记讲「CPU 轮询 key 自实现 busy poll」，是本模型的论文级反例——低延迟 KV 场景宁可烧 CPU 也不睡。**跨线程连接**：main 线程的 on_disconnect/destroy_connection（rdma-client.c:71-L77）会销毁 QP/MR/conn，而 poll 线程可能仍阻塞在 get_cq_event——教学代码未做 join，拆除时序存在理论竞态（实际演示中 CQ 已排空、大概率无害）。

## 四、数据流

一次完整收割的数据流：网卡完成某 WR→CQE 写入 CQ（CQE 含 wr_id/status/opcode）→因 CQ 处于 armed 状态，同时向 comp_channel 发完成事件→poll 线程从 L248 的睡眠中醒来，得到 cq 指针→ack（L249，channel 事件清账）→**先 re-arm 再排空**（L250）→L252 循环逐个取出 WC：返回正数=取到一个、0=CQ 空、负数=取 WC 出错（本示例 TEST_NZ 不检查 ibv_poll_cq 返回值，只判真假，负数会被当「有事件」喂给 on_completion，再由其 status 检查兜底 L184-L185）→on_completion 按 opcode 分派→排空后回到 L248 睡眠。`wc` 是栈上单变量逐个复用，on_completion 内部需即时消费完（如 memcpy peer_mr L191）才能进入下一轮——这就是协议消息处理必须「收货即搬走」的原因。

## 五、设计决策

①**为什么 ack 与 re-arm 要在 poll 之前做**：这是全函数最精妙处。若先 poll 后 arm，则 poll 排空到 arm 之间到达的新 CQE 会因 CQ 未 armed 而**不触发通道事件**，线程睡死、事件丢失；先 arm（L250）再 poll（L252）则窗口期新 CQE 既会触发下一轮通道事件、又被本轮排空兜底——**事件最多被处理两次判定，但绝不丢失**（重复取不到：poll 取走即消）。②**每事件 ack 一次**（L249 的 1）：channel 事件是「CQ 从空到非空」级别的粗粒度通知，一次事件后排空全部 CQE 是标准搭配。③**为什么用独立线程**：get_cq_event 阻塞语义与 main 的 rdma_get_cm_event 阻塞语义天然互斥，双线程是教学上最省事的并发模型；代价是 conn 共享状态无锁（靠「完成事件串行到达」的硬件保证）。④**cqe=10**（L115 注释 arbitrary）：CQ 深度只需容纳两次事件间累积的完成数，示例协议峰值约 3-4 个/侧，10 绰绰有余；生产场景需按在途 WR 数配。⑤**unsigaled 陷阱**（tutorial.md:87）：若 SEND 不带 SIGNALED 则无 CQE，本状态机将失去步进来源直接卡死——L218/L320 的 SIGNALED 同时承担「通知」与「驱动协议」双职。

## 六、新人提示

把 L248-L253 五行抄在笔记本上，面试问 event vs busy polling 时默写即可：睡眠点在 get_cq_event、arm 点在 req_notify_cq、排空点在 poll_cq、三者的顺序是 arm 先于 poll。动手实验两枚：一，按教程提示删前三行做 busy 版，用 `top` 对比两版 CPU 占用（教程 2.6 的 poll 实验图 image/实验结果-poll.png 就是这组对比的结果）；二，把 L252 的 `1` 改成 `8` 并改用 wc 数组（ibv_poll_cq 支持批量取），体会批量收割对延迟的意义。两个读码陷阱：`ibv_poll_cq` 返回值是「取到的个数」不是布尔，负数是错误（本示例用 while 真值判断掩盖了这一点）；on_completion 里 RECV 判断用 `wc->opcode & IBV_WC_RECV` 位与而非 `==`（L187），因为 RECV_WITH_IMM 等 opcode 叠加标志位——send_recv 组同款写法（client.c:212）。最后记住教学简化边界：死循环无退出、无错误分级、拆除竞态，这三条在生产代码（参考 perftest 源码）都有对应解法。
