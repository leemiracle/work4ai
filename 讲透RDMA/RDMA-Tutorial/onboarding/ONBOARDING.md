# RDMA-Tutorial ONBOARDING（jcxue/RDMA-Tutorial，commit be4d713）

> 基于 .understand-anything 知识图谱（46 节点/121 边/13 层/15 步 tour）生成，锚经核实。

## 1. 项目定位

基于示例的 RDMA 教学项目：一个 C 程序演示 InfiniBand verbs 编程全套骨架——资源创建、TCP 带外交换队列对（QP）信息、RC 传输三段状态迁移、client/server 双角色 echo 吞吐基准。README.md:2 定位 example based tutorial，4 示例按 git commit 组织（README.md:18-21），HEAD 是最终 echo 基准。环境：Mellanox HCA/OFED 3.3（README.md:5-9）。全仓约 1200 行；同一二进制跑所有节点，靠配置 hostname 匹配定角色（config.c:92）。

## 2. 快速上手

`make` 出优化版；`make debug` 以 `-g -DDEBUG` 重写 CFLAGS（Makefile:13-15）打开 debug.h:33-41 宏输出。7 个源文件（Makefile:7）经 `-Wall -Werror -O2` 编译，链接 -libverbs -lrdmacm -pthread（Makefile:4-5），产物 rdma-tutorial。

运行需多台 IB 机器：`./rdma-tutorial config_file sock_port`（main.c:19-22）。sample.config 即格式：servers:/clients: 区段写 `server1 .. server2` 区间，加 num_concurr_msgs 与 msg_size。前提：节点名前缀被硬编码二选一展开（config.c:77-81，见坑 2）；get_rank 以 hostname 匹配列表定角色（config.c:108-126）。server 先起，日志写 server[n].log/client[n].log（main.c:52/54），跑完输出 Mops/s 吞吐（server.c:154）。

## 3. 架构总览（13 层）

图谱 46 节点分 13 层，七个区带：**L01 构建**（README+Makefile，`-Werror` 零警告）；**L02 main 骨架**（main.c:15-45 六段编排）；**L03 角色契约**（client.h/server.h 最小声明）；**L04-L05 配置体系**（config.h:14-27 ConfigInfo 契约+config.c 解析器）；**L06-L07 TCP 原语与 QPInfo 交换**（sock.c 六原语，QP 地址交换全靠带外 TCP）；**L08 verbs 封装**（ib.h 协议常量+ib.c 三原语，两侧共用）；**L09-L10 资源生命周期与 QP 编排**（全局 ib_res；setup_ib→connect_qp_server/client；close 逆序销毁）；**L11-L12 双负载线**（各建 1 工作线程跑 echo）；**L13 debug 横切**（debug.h 全宏框架，check 范式贯穿全部 7 个 .c）。依赖 main→(config/setup_ib/client/server)→(sock/ib/debug)，无循环。

## 4. 核心链路

**main 六段生命周期**（main.c:15-45）：argc 校验→parse_config_file→init_env→setup_ib→按 is_server 分发（main.c:34-38）→error 标签统一清理（main.c:41-43），失败亦走完整清理。

**配置解析**（config.c:135-202）：fgets+clean_up_line 剔空白（config.c:13-26），区段标记切 ATTR_* 状态（config.c:153-165），节点列表交 parse_node_list 展开区间（config.c:36-90），数值走 atoi；末尾 get_rank 以 hostname 先扫 servers 再扫 clients 定 rank（config.c:92-133）。

**TCP 建连与 QPInfo 交换**：服务端 sock_create_bind（sock.c:55-98）→listen→accept 收齐 num_peers 条（setup_ib.c:27-36）→收各 client QPInfo 并按 rank 配对回发本端信息（setup_ib.c:43-72）。客户端 sock_create_connect（setup_ib.c:142-146）→先发本端→再收对端（setup_ib.c:160-173）。序列化对（sock.c:149-153/170-172）转网络序整块传输；末尾双向 sync 握手（setup_ib.c:95-207）。

**setup_ib 资源创建**（setup_ib.c:239-340，调用序即依赖链）：按角色定 QP 数——server=num_clients、client=num_servers（setup_ib.c:246-250）→open_device/alloc_pd/query_port 取 lid（setup_ib.c:257-265）→memalign 4096 缓冲+ibv_reg_mr（setup_ib.c:273-281，容量=msg_size×num_concurr_msgs×num_qps）→以设备上限建 CQ/SRQ（setup_ib.c:289/294-299）→建 RC QP 收发共用同一 CQ/SRQ（setup_ib.c:302-322）→分发 connect_qp_*（setup_ib.c:325-329）。

**RC 三段迁移**（ib.c:7-74）：INIT 开放远端权限（ib.c:12-27）→RTR 配 path_mtu/dest_qp_num/dlid（ib.c:30-51）→RTS 配超时与重试（ib.c:54-69）。

**数据收发**：server_thread 预投 num_peers×num_concurr_msgs 个 SRQ 接收（server.c:57-63）→向全部对端 post 0 字节 MSG_CTL_START（server.c:66-69）→echo 循环按 imm_data 定位 QP 回显并补投接收（server.c:71-111）→计满 TOT_NUM_OPS=1000 万（ib.h:16）广播 MSG_CTL_STOP 并等收完成事件（server.c:114-148）。client 镜像：等收齐 START（client.c:64-88）→预投发送→echo 主循环；预热 50 万次后起计时。

**逆序清理**：close_ib_connection 按 qp→srq→cq→mr→pd→ctx→buf 销毁（setup_ib.c:346-377），与创建对称；destroy_env 收尾（main.c:67-73）。

## 5. 关键模块深讲

**setup_ib.c（378 行，全仓核心）**："全局资源结构+四个生命周期函数"。IBRes（setup_ib.h:6-19）持全套 verbs 句柄与缓冲，setup_ib.c:11 定义全局 ib_res，数据面直读不传参（client.c:24-28）。缓冲三因子（setup_ib.c:273）="单条长度×单 QP 在途深度×QP 数"，即 SRQ 接收侧总缓冲；预投用 `buf_offset=(buf_offset+msg_size)%buf_size` 环形切分（client.c:57-60），wr_id 携带缓冲指针、完成事件直接取回（client.c:131）。main.c（73 行）另定义 log_fp（main.c:10）被 debug.h:15 extern；error 标签正常路径也执行，清理判 NULL 幂等。

**config.c（245 行）**：区间表达式单趟扫描（config.c:43-59），clean_up_line 压平空白（config.c:15-25）。

**sock.c（178 行）**：sock_read 处理短读/对端关闭/EINTR 三态（sock.c:17-28）；QPInfo 整块收发+packed（ib.h:33）线上 10 字节定长。

**ib.c（121 行）**：modify_qp_to_rts 每段 attr_mask 与字段一一对应（ib.c:45-49）；post_send 固定单 SGE 的 IBV_WR_SEND_WITH_IMM，imm_data 经 htonl 捎带（ib.c:94）；post_srq_recv 投共享接收队列（ib.c:119），SRQ 全 QP 共享接收池是多对端支持的关键。

**debug.h（44 行）**：check（debug.h:31）全仓唯一错误范式；log 双通道（debug.h:37/40），DEBUG 版 stderr+文件、release 只写文件；线程失败 pthread_exit(-1)（client.c:160-164），run_* 经 join 判成败。

## 6. 设计决策

**① QP 数=对端数**（setup_ib.c:246-250）：每对端一条 RC 连接，server 建 num_clients 条、client 建 num_servers 条。

**② 自定义 QPInfo 交换协议而非 rdma_cm**：手写 TCP 通道+10 字节 packed QPInfo+双向 sync 握手，让 rdma_cm 藏起来的每步显式可见（-lrdmacm 链接实为冗余，见坑 8）。

**③ 线程模型**：每进程固定 1 个工作线程（client.c:170、server.c:169），pthread_setaffinity_np 绑核（client.c:45-49）——单线程+CQ 轮询是低延迟基准的经典最小配置。

**④ SRQ+imm_data 复用**：SRQ（setup_ib.c:294-299）让 N 对端共享接收池；imm_data 三义——控制字 START/STOP、发送方对端索引（client.c:96）、回显路由索引（server.c:105），信令揉进数据面无额外报文。

**⑤ 全局结构体直连**：config_info/ib_res/log_fp 三全局（config.c:10、setup_ib.c:11、main.c:10）——教程可读性优先。

**⑥ check/goto error 统一错误处理**：单出口+幂等清理，LCTHW 风格。

## 7. 新人学习路径（按 15 步 tour）

**第一段·全局（1-3，半天）**：README+Makefile 知环境→main.c:15-45 背六段生命周期，其余文件都是其中一段的展开→client.h/server.h 理解角色分发。**第二段·配置与地基（4-9，半天）**：config.h+sample.config 契约→config.c 解析（135-202）→debug.h，此后错误路径都长 check 的样子→sock 六原语按 sock.c 顺序读。**第三段·RDMA 本体（10-12，一天）**：setup_ib（setup_ib.c:239-340）逐 verbs 调用对照注释，全仓核心；connect_qp_server/client+modify_qp_to_rts（setup_ib.c:13-237/ib.c:7-74）两侧对读——TCP 与 QP 状态机在此汇合。**第四段·数据面与收尾（13-15，半天）**：client_thread_func（client.c:12-165）与 server_thread（server.c:12-164）对读；close_ib_connection（setup_ib.c:342-378）看逆序销毁。改参数实验从 msg_size/num_concurr_msgs 入手。

## 8. 已知坑与勘误（全部源码核实）

1. **server.c 重复 calloc 覆盖指针**：server.c:43 已 `wc=calloc(...)`，server.c:54 再次 calloc 同一指针，首次分配泄漏；client.c:52 对应位置只一次，系复制粘贴残留。
2. **节点名硬编码**：parse_node_list 以 strstr 前缀嗅探在 `mnemosyne%02d`/`saguaro%d` 间二选一（config.c:77-81），其他前缀被静默改写，换环境必改。
3. **connect_qp_server 内存泄漏**：local/remote_qp_info（setup_ib.c:39/50）两条路径均未 free（client 侧有，setup_ib.c:214-215）。
4. **destroy_config_info 是死代码**：config.c:204-227 定义了释放函数，但 main.c:42-43 只调 close_ib_connection+destroy_env，全仓无调用（图谱 tour 第 15 步的描述与实际控制流不符）。
5. **setup_ib 注释漂移**：setup_ib.c:269-272 称"buf_size 两倍大、收前半发后半"，实现无乘 2 且环形复用同一块。
6. **imm_data 三义的拓扑假设**：client 预投 send 携带循环变量 i（client.c:96），server 按 qp[imm_data] 回显（server.c:105，qp[k] 连 client k）——仅单 client 拓扑必然正确；多 client 下数据不丢但 echo 配对错位。
7. **accept 顺序假设**：connect_qp_server 的 peer_ind 查找（setup_ib.c:62-69）只修正 local_qp_info/qp 索引，回发 socket 与 RTR 目标（setup_ib.c:70/84-86）仍按 accept 槽位索引，隐含 accept 顺序假设。
8. **-lrdmacm 链接冗余**：Makefile:5 链接 rdmacm 但全仓零调用。
9. **热路径丢弃 post 返回值**：server.c:105/108、client.c:142 失败被静默吞掉。小瑕疵：print_config_info 拼写 Configuraion（config.c:231）；SIG_INTERVAL 死宏（ib.h:17）；memalign 为 glibc 特有。
10. **图谱工具层**：tree-sitter 对 `void *func(void *arg)` 线程函数签名有提取盲区，client_thread_func/server_thread 已人工补齐入图谱，阅读以源码为准。
