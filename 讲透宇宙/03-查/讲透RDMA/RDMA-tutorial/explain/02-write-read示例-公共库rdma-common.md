# 02 write/read 示例：公共库 rdma-common

> 对象：`example code/rdma_write_read/rdma-common.h`（29 行）+ `rdma-common.c`（345 行）；行号锚经源码核实（commit `c760004`）。

## 一、角色定位

rdma-common 是 rdma_write_read 示例的「公共层」，全仓含金量最高的代码：345 行装下了 RDMA 单边通信需要的全部机制——建连、QP/CQ/PD 资源创建、四块内存注册、MR 钥匙交换协议、单边工作请求构造、完成收割。两个入口 rdma-client.c（113 行）/rdma-server.c（104 行）只管事件循环与命令行，通信重活全在这里。它解决的核心问题是**单边传输的鸡生蛋困境**：WRITE/READ 需要先拿到对端内存的地址+rkey，而钥匙交换只能靠双边 SEND——于是本库在 send/recv 机制之上叠加了一层「先互发钥匙、再做单边传输」的协议。send_recv 示例没有这个公共层（client.c/server.c 各自镜像自包含），本库的分层是 write_read 组独有的工程决策。

## 二、内部结构

**契约（rdma-common.h）**：`TEST_NZ/TEST_Z` 两个错误检查宏（L11-L12）保证每个 verb 返回值都被检查；`enum mode`（L14-L17）的 M_WRITE/M_READ 是贯穿全库的模式开关；8 个函数原型（L19-L27）构成对入口层暴露的全部接口：die/build_connection/build_params/destroy_connection/get_local_message_region/on_connect/send_mr/set_mode。

**实现（rdma-common.c）按三结构+六函数族组织**。三结构：`struct message`（L5-L14）是钥匙协议的消息格式——type 取 MSG_MR/MSG_DONE，联合体直接装下整个 `struct ibv_mr`；`struct context`（L16-L23）是进程单例 `s_ctx`（L67），持有 PD/CQ/comp_channel/poll 线程；`struct connection`（L25-L56）是每连接状态机（详见第 06 篇）。函数族五条线：建连线 `build_connection`（L76-L98）→`build_context`（L100-L119）→`build_qp_attr`（L129-L141）；内存线 `register_memory`（L276-L307）+`post_receives`（L259-L274）；协议线 `send_message`（L309-L329）/`send_mr`（L331-L339）；收割线 `poll_cq`（L242-L257）→`on_completion`（L180-L235，状态机发动机）；清理线 `destroy_connection`（L143-L162）。`s_mode` 全局变量（L68，默认 M_WRITE）由 `set_mode`（L341-L344）从命令行注入。

## 三、外部连接

上游被两个入口调用：rdma-client.c 在 ADDR_RESOLVED 事件里调 `build_connection`（rdma-client.c:56）、ESTABLISHED 里调 `on_connect`+`send_mr`（L65-L66）；rdma-server.c 在 CONNECT_REQUEST 里调 `build_connection`+`build_params` 后 `rdma_accept`（rdma-server.c:60-L63）。`get_local_message_region` 被两端入口用来在连接期写入待发消息（rdma-client.c:57、rdma-server.c:62）。对下依赖三个系统库：rdmacm（连接管理）、libibverbs（verb 本体）、pthread（poll 线程），Makefile L5 一次链接。与教程的连接：2.3.2 注册内存（tutorial.md:159-L165）对应 register_memory；2.4 的四行单边骨架（tutorial.md:227-L230）是 on_completion L215-L226 的浓缩。send_recv 组的 client.c:92-L125 有 build_context/build_qp_attr 的镜像拷贝——两库同源，read them side by side 可见「公共层抽出了什么」。

## 四、数据流

**建连数据流**：入口传入 `id` →`build_connection` 先 `build_context(id->verbs)` 创建 PD（L113）、comp_channel（L114）、CQ（L115，cqe=10 注释自认 arbitrary）并 arm（L116）、起 poll 线程（L118）；再 `build_qp_attr` 填 RC 型 QP 参数（L135，深度 10/SGE 1）→`rdma_create_qp`（L84）→malloc connection、初始化状态机（L91-L92）→`register_memory`（L96）→`post_receives`（L97）预挂一个 RECV 等钥匙。

**内存注册与权限矩阵**：register_memory 分配 2 个 message 缓冲+2 个 1KB 数据区（L278-L282），注册四块 MR，权限按「**对方要对我做什么**」给：send_mr 仅 LOCAL_WRITE（L284-L288）；recv_msg 与 rdma_remote_region 在 M_WRITE 模式给 REMOTE_WRITE、M_READ 模式给 REMOTE_READ（L294、L306）；rdma_local_region 仅 LOCAL_WRITE（L296-L300）。**所有权语义**在此显形：`rdma_remote_region` 是「让对端单边操作的牺牲区」，其注册权限就是发给对端的授权书；`send_mr`（L331-L339）把整个 `rdma_remote_mr`（含 addr+rkey）memcpy 进消息体（L336）用 SEND 发走——rkey 就是远端内存的钥匙，收到方存进 `peer_mr`（L191）后才有资格构造单边 WR：`wr.wr.rdma.remote_addr=peer_mr.addr`、`rkey=peer_mr.rkey`（L219-L220）。一次 WRITE/READ 提交（L226）即完成不经对端 CPU 的传输，随后立刻发 MSG_DONE（L228-L229）作终结握手。

## 五、设计决策

①**一个 enum mode 换全套行为**：模式开关同时决定权限注册（L294/L306）、缓冲角色选择（get_local/get_peer_message_region L164-L178 按 s_mode 翻转 local/remote 语义）、WR opcode（L215 三目）——命令行一个参数换 verb，两端各自独立解释，故必须一致。②**四块 MR 的 local/remote 命名**按「谁对这块内存动手」而非「谁分配」：rdma_remote_region 由本端 malloc+注册，但内容等待对端写入（M_WRITE）或被对端读取（M_READ），get_peer_message_region（L172-L178）在不同模式下分别返回 remote/local 区——M_READ 模式下本端消息写进 remote 区（注册 REMOTE_READ 供对端读）、对端数据落进 local 区，命名与角色随模式翻转。③**SEND 完成后打印 "send completed successfully"（L200）**对三种 opcode（MR/DONE SEND、RDMA WRITE/READ）一律生效——单边 WR 也走 SQ 完成回调，这正是状态机能步进的前提（见第 06 篇）。④**教学简化点**：`send_message` 里 `while (!conn->connected);`（L326）自旋等连接标志、poll_cq 死循环（L247）、CQ 深度 10 写死——都不可用于生产。⑤build_params（L121-L127）给 `rnr_retry_count=7`（注释 infinite retry），是对端无预挂 RECV 时的保命参数。

## 六、新人提示

读此库的顺序：先 rdma-common.h 记 8 原型 → L5-L56 三结构 → build 链 → register_memory 权限矩阵 → on_completion（全仓最核心一段，单独见第 06 篇）。最易困惑的两点：一，权限方向——REMOTE_WRITE 是「允许**别人**写我」，不是「允许我写别人」；二，peer_mr 是**对端**内存的描述符，WR 里填的 remote_addr/rkey 都是对方家的地址，lkey 才是本地缓冲的凭证。动手实验建议：把 L294 的 REMOTE_WRITE 改成 REMOTE_READ 再跑 write 模式，观察对端网卡以权限错拒绝写入——这是理解 rkey 授权机制最快的路径。`-Werror`（Makefile:3）让任何未检查返回值的改动直接编译失败，改代码时注意。
