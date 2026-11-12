# RDMA-tutorial 仓库 ONBOARDING

> 仓库：StarryVae/RDMA-tutorial（commit `c760004`）；图谱 84 节点/127 边/12 层/16 步 tour，0 issues；行号锚均经源码核实（2026-11-11）。

## 一、项目定位：中文 RDMA 教程的生态位置

**以中文教程为主体、示例代码为验证、论文笔记为延伸**的 RDMA 学习笔记仓，根 `README.md:3` 自述「记录自己学习的RDMA的一些知识，方便后面实验室同学的快速入门」。它并非生产库，而是国内 RDMA 入门流传最广的中文一手资料（英文对应物：rdmamojo/Mellanox 示例），把「教程+可编译示例+面经+论文精读」整合于一处且全程中文。

四板块（`README.md:5-7` 索引）：`tutorial.md` 主教程约 330 行（图谱 L02）；`example code/` 两组 C 示例——rdma_send_recv 双边、rdma_write_read 单边（L03-L07）；`interview/` 复习提纲与面经（L08）；`paper/` 11 篇论文笔记（L09-L12）。教程 2.5 节（`tutorial.md:237-241`）与 `example code/README.md:3-4` 互相回指，paper 线沿第三章（L303-317）展开。全仓 26 文件，一两天走完。

## 二、快速上手：编译与运行两组示例

依赖 `rdma/rdma_cma.h`+`librdmacm`/`libibverbs`/`libpthread`；需 RoCE/IB 设备（软 RoCE 亦可）。

**rdma_send_recv（双边）**：`make` 产出 `server`/`client`（`Makefile:7`）。先 `./server`（端口硬编码 22222，`server.c:57`），再 `./client <地址> 22222`。两侧各打印一条后 client 断开——实为**单向**演示（见第 8 节勘误 1）。

**rdma_write_read（单边）**：`make` 产出 `rdma-server`/`rdma-client`（`Makefile:7`）。先 `./rdma-server write`——server **不接受端口参数**，绑随机端口并打印 `listening on port <N>`（`rdma-server.c:32-37`），client 须填该端口：`./rdma-client write <地址> <端口>`。两端模式**必须一致**，否则 MR 权限错位。终点 `remote buffer: ...` 即单边证据——client 直接读到 server 写进其内存的串，server CPU 不参与。

## 三、架构总览：教程线 / 示例线 / paper 线三分

**教程线（L02）**：一章讲内核旁路/零拷贝与 RNIC 抽象；二章是核心——2.1（L63）QP/CQ 微观传输、2.2（L80）五参数（QP 类型 RC/UC/UD、verb、inline、signal、poll）、2.3（L96）send/recv、2.4（L220）write/read、2.6（L243）性能实验；三章（L303）梳理传输层/网络层/虚拟化方向，即 paper 板块目录。

**示例线（L03-L07）**：`rdma_write_read` **分层设计**：`rdma-common.h`（契约）+`rdma-common.c`（公共库 345 行）+两薄入口（各约 110 行）；`rdma_send_recv` **自包含镜像**：client.c（300 行）/server.c（280 行）全逻辑自带、逐函数对称、无公共文件。

**paper 线（L09-L12）**：11 篇四层——verb 选择与 RPC（HERD/FaSST/RFP）、硬件微架构与集群配置（Design Guidelines/Cluster Configuration）、资源共享与隔离（LITE/Resource Sharing/Isolation Anomalies）、分布式应用与拥塞控制（Hybrid is Better/TensorFlow/HPCC）。阅读顺序：教程→示例→面经→paper。

## 四、核心链路：教程章节 → 示例代码的对照学习路径

本仓最有价值的学法是**互证**——教程 2.3/2.4 概念在 write_read 示例的落点：建连（2.3.1）→`rdma-client.c:37-45`+`on_event`（L79-95）；注册内存（2.3.2）→`rdma-common.c:276-307`；预挂接收（2.3.3）→`rdma-common.c:259-274`；发起发送（2.3.4）→`rdma-common.c:309-329`；poll 完成（2.3.5）→`rdma-common.c:242-257`；write/read（2.4）→L212-226。send_recv 同构按名对号（预挂 `server.c:141-156`、发送 `client.c:223-248`）。

**poll_cq 是全仓最重要的互证锚点**：教程 2.2 节分 busy polling 与 event-triggered 两种策略，示例取后者——`ibv_get_cq_event` 阻塞等通知（`rdma-common.c:248`）、ack 并重 arm（L249-250）、`ibv_poll_cq` 排空喂 on_completion（L252-253）；HERD 笔记讲「CPU 轮询 key 自实现 busy poll」——三处连读打通 poll 参数从概念到论文的取舍。教程 2.4 节引用的四行单边代码（`tutorial.md:230-234`）在 L215-226 一字不差落地。另：面经考的 QP reset→INIT→RTR→RTS 被 rdma_cm 封装，但 `build_qp_attr`（L129-141）与 `build_params`（L121-127）即协商参数一部分。

## 五、关键模块深讲：rdma-common.c 的协议状态机

`rdma_write_read/rdma-common.c`（345 行）是全仓含金量最高的文件。

**三结构构成协议栈**：`struct message`（L5-14）是 MR 交换协议消息——type 取 MSG_MR/MSG_DONE，联合体携带整个 `struct ibv_mr`，用 SEND 把本端 MR（地址+rkey）交给对端；`struct context`（L16-23）是进程单例（`s_ctx`，L67）；`struct connection`（L25-56）是每连接状态机——cm_id/QP、四块 MR、对端 `peer_mr`（L36），加**两个匿名枚举状态机**：send_state（SS_INIT→SS_MR_SENT→SS_RDMA_SENT→SS_DONE_SENT）与 recv_state（RS_INIT→RS_MR_RECV→RS_DONE_RECV，L44-55）。

**建连链**：`build_connection`（L76-98）串起 `build_context`（L100-119，PD/CQ+poll 线程）→`build_qp_attr`（L129-141，RC 型）→`rdma_create_qp`（L84）→初始化状态机（L91-92）→`register_memory`+`post_receives`（L96-97）。权限考点（L294、L306）：`recv_msg` 与 `rdma_remote_region` 按 s_mode 给 REMOTE_WRITE/READ——权限跟着「对方要对我做什么」走。

**`on_completion`（L180-235）是状态机发动机**：RECV 分支（L187-196）推进 recv_state，收到 MSG_MR 则拷对端 MR 进 peer_mr（L191）、rearm（L192）、若尚在 SS_INIT 立即回发自己的 MR（L194-195）——后收到的一方也交钥匙；SEND 分支（L198-201）只推 send_state。两态在 L203 汇合即构造单边 WR：按 s_mode 选 `IBV_WR_RDMA_WRITE/READ`（L215），远端地址/rkey 取 peer_mr、本地 SGE 用 rdma_local_region+lkey（L219-224），`ibv_post_send`（L226）——一次提交完成不经对端 CPU 的传输，随即发 MSG_DONE（L228-229）；终态（L231-233）打印对端缓冲并断开。全流程：**SEND 互发 MR 钥匙→单边 WRITE/READ→DONE 握手→断开**；`poll_cq` 线程（L242-257）驱动，回收在 `destroy_connection`（L143-162）。

## 六、设计决策：示例为何分 write_read 与 send_recv 两组

①**对应教程两节且互相依存**（`example code/README.md:3-4`）：send_recv 演示 two-sided（2.3），write_read 演示 one-sided（2.4）。单边传输有鸡生蛋问题——WRITE/READ 需先拿到对端 MR 地址与 rkey，而钥匙交换只能靠双边 SEND（教程 2.4 节明言），故 write_read 复用 send/recv 全机制再叠加 MR 协议与状态机，复杂度递增。
②**send_recv 刻意最小**：两块 MR、无消息协议、无状态机，on_completion 仅按 opcode 打印（`server.c:176-189`）；write_read 以一个 `enum mode`（`rdma-common.h:14-17`）贯穿权限注册（common.c:294）、region 选择（L164-178）到 WR 构造（L215），一个命令行参数换 verb。write_read 用 `-Werror`（Makefile:3）而 send_recv 仅 `-Wall`。

## 七、新人学习路径：按 16 步 tour 走

**概念奠基（步 1-4，半天）**：根 README 认四板块→一章+2.1 节理解 QP/CQ→2.2/2.3 五参数与五小节→2.4 单边、2.6 性能实验、第三章方向。不动代码，只建「QP/CQ/MR/verb」词汇表。

**代码实证（步 5-10，一天，重心）**：example README 看映射→`rdma-common.h:11-12` 宏与 8 原型→rdma-common.c 主体：结构、建连、内存注册、MR 交换→精读 on_completion 与 poll_cq（「全仓最核心一段代码」）→看两个入口之薄，体会「事件循环+公共库」分层→make 跑通两模式。

**镜像对比（步 11-12，两小时）**：转 send_recv 看镜像结构，沿 client.c 主线走完 CM 循环与 poll 线程生命周期，并做「找不同」：MR 数量、权限、状态机、预挂时机差异。

**输出倒逼输入（步 13-16）**：interview 提纲自检+四公司面经实测（建连状态机、QP/verb 参数、网卡收发包是真题）→paper 线：Performance Isolation Anomalies→HERD（最推荐初学）→FaSST→RFP 与 Design Guidelines、Cluster Configuration→LITE/Avatar、Hybrid is Better、TensorFlow、HPCC，对位第三章三方向。

最短路径：步 2-3-7-8-10-13，三小时建立最小闭环。

## 八、已知坑与勘误

**运行预期类：**
1. **send_recv 实为单向演示，图谱/tour 描述与代码不符**：tour 第 11/12 步称服务端会主动 SEND 问候、client 收完回复再断开；实际 `server.c:269-271` 把 ESTABLISHED 分支的 on_connection 调用注释（问候函数 L216-240 成死代码），`client.c:198` 的 post_receives 也被注释。真实行为：client 发问候→server 收到打印→client 在自己的 SEND 完成后（`client.c:219`）即断开，从不收回复。
2. **write_read readme 命令名错**：写 `./server`/`./client`，产物实为 `rdma-server`/`rdma-client`（`Makefile:7`）。
3. **write_read 端口非 22222**：server 绑端口 0 由内核分配（`rdma-server.c:27-37` 打印实际端口）；readme 的「default: 22222」系从 send_recv（`server.c:57`）复制的误导。
4. **两端模式必须一致**：权限（`rdma-common.c:294,306`）与 region 选择（L164-178）各按本端 s_mode 走，错配即失效。
5. **教学代码勿照搬**：`send_message` 自旋忙等（`rdma-common.c:326`）、poll_cq 死循环（L247）均为简化。
6. **教程重号**：tutorial.md 两个 2.6.2（L259/L271，后者应为 2.6.3）。

**图谱/工具类：**
7. **tree-sitter 漏函数**：图谱缺席 5 处（派发口径称 4，实测 5）——`get_peer_message_region`（`rdma-common.c:172-178`）、`usage`×2（`rdma-client.c:108-112`、`rdma-server.c:99-103`）、`die`×2（`send_recv/client.c:86-90`、`send_recv/server.c:83-87`），检索直翻源码。
8. **C struct 误判 class**：`struct connection`（`rdma-common.c:25-56`）被记为 class 节点，languageNotes 已标注「C struct（tree-sitter 报告为 class）」；它无方法，靠匿名枚举实现状态机。
9. **隐式中间态**：`SS_RDMA_SENT`（`rdma-common.c:47`）从未被显式判断——协议靠 MSG_DONE 推进（L228-231），别找对应 if，不存在。
10. **PDF/图片不在图谱**：`paper/pdf/` 11 份 PDF 与 `image/` 插图被 .understandignore 排除，笔记图号引用要去 image/ 找原图。
