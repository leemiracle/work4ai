# 04 · setup_ib：IB 资源生命周期

## ① 角色定位

setup_ib.c（378 行）是全仓核心与最大文件，在图谱中占"IB 资源生命周期"（第 9 层）层，tour 第 10 步。它回答一个 RDMA verbs 编程的第一性问题：**在真正收发数据之前，要把哪些资源、按什么顺序、以什么依赖关系创建出来**。一个文件承担三个职责：定义全局资源结构 ib_res（setup_ib.c:11，结构契约在 setup_ib.h:6-19）；setup_ib（setup_ib.c:239-340）按 verbs 教科书顺序创建整条资源链；close_ib_connection（setup_ib.c:342-378）逆序销毁。另两个建连编排函数 connect_qp_server/client（setup_ib.c:13-237）在第 05 篇单独讲——它们是 setup_ib 尾部的分发分支。

"全局单例"是它的形态决定：ib_res 是与 config_info、log_fp 并列的三大全局之一，数据面（client.c:24-28、server.c:24-28）无参直读它的 qp/cq/srq/mr——教程把"传参链"换成"全局直连"，换来了主循环代码的极度干净。

## ② 内部结构

**IBRes 契约**（setup_ib.h:6-19）：七个 verbs 句柄 ctx/pd/mr/cq/qp(二级指针)/srq、两个属性快照 port_attr/dev_attr、计数 num_qps、缓冲 ib_buf/ib_buf_size。这 11 个字段就是一条 RC 数据面的全部家当。

**setup_ib 创建链**（setup_ib.c:239-333，调用序即依赖链）：

1. memset 清零 ib_res（setup_ib.c:244）——为 main 的幂等清理埋下伏笔（见 ⑤）。
2. **定 QP 数**（setup_ib.c:246-250）：`is_server ? num_qps=num_clients : num_qps=num_servers`——QP 数=对端数，每对端一条 RC 连接。
3. ibv_get_device_list 枚举设备（setup_ib.c:253）→ ibv_open_device(**dev_list) 打开**第一个**设备（setup_ib.c:257，`*dev_list` 直接解引用，多卡机器不挑卡）。
4. ibv_alloc_pd 分保护域（setup_ib.c:261）。
5. ibv_query_port 查端口属性（setup_ib.c:265，IB_PORT=1 硬编码于 ib.h:12）——port_attr.lid 后面进 QPInfo。
6. **注册内存**：注释漂移区（setup_ib.c:269-272，见 ⑤）→ 三因子算 buf_size=msg_size×num_concurr_msgs×num_qps（setup_ib.c:273）→ memalign(4096) 页对齐分配（setup_ib.c:274）→ ibv_reg_mr 以 LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE 注册（setup_ib.c:277-282）。
7. ibv_query_device 查设备属性（setup_ib.c:285）——**必须排在 create_cq 之前**，因为 CQ 深度用 dev_attr.max_cqe（setup_ib.c:289）。
8. ibv_create_cq（setup_ib.c:289-291）。
9. ibv_create_srq（setup_ib.c:294-299）：max_wr 取 dev_attr.max_srq_wr、max_sge=1——共享接收队列，所有 QP 共用一个接收池。
10. 建 QP：qp_init_attr（setup_ib.c:302-313）send_cq=recv_cq=同一个 cq、挂 srq、cap 全取 dev_attr.max_qp_wr、qp_type=IBV_QPT_RC；calloc 指针数组（setup_ib.c:315）后循环 ibv_create_qp（setup_ib.c:319-322）。
11. **分发建连**（setup_ib.c:325-329）：is_server 走 connect_qp_server，否则 connect_qp_client——TCP 与 QP 状态机在此汇合。
12. ibv_free_device_list 收尾（setup_ib.c:332）。

**close_ib_connection 销毁链**（setup_ib.c:342-378）：逐 QP destroy→free 数组（setup_ib.c:346-353）→ srq（setup_ib.c:355）→ cq（setup_ib.c:359）→ dereg_mr（setup_ib.c:363）→ pd（setup_ib.c:367）→ ctx（setup_ib.c:371）→ free(ib_buf)（setup_ib.c:375）——**与创建顺序严格互逆**，每个 destroy 前判 NULL。

## ③ 外部连接

上游：main.c:31 唯一调用 setup_ib、main.c:42 唯一调用 close_ib_connection；config_info 提供全部参数输入（角色、num_clients/num_servers、msg_size、num_concurr_msgs）。内部：建连分支调 sock.c 全部六个原语与 ib.c 的 modify_qp_to_rts（经 connect_qp_*）。下游：client.c/server.c 数据面直读 ib_res 的 qp/cq/srq/mr->lkey/ib_buf/ib_buf_size/num_qps（client.c:18/24-33、server.c:18/24-33）——ib_res 是资源层通向数据面的唯一接口。图谱上它左接 main/配置层，下接 sock/ib 原语层，右被双负载线引用，是依赖图的枢纽节点。

## ④ 数据流

setup_ib 自身不搬运数据，它是**句柄与参数的装配线**：配置数字流入（msg_size、num_concurr_msgs、num_clients/num_servers）→ 资源句柄流出（ib_res 各字段）。两条派生关系值得盯住：

- **QP 数的传染性**：num_qps（setup_ib.c:246-250）同时决定 QP 数组长度、缓冲三因子第三项（setup_ib.c:273）、数据面的 num_peers（client.c:18/server.c:18）——同一个数字在三层各表一次，含义都是"对端数"。
- **lid 的流向**：ibv_query_port 查出的 port_attr.lid（setup_ib.c:265）经 connect_qp_* 填进 local_qp_info（setup_ib.c:44/154），经 TCP 线送到对端，最终成为对端 RTR 的 dlid（ib.c:39）——本地一次查询，横跨两台机器落地。

close 的数据流是镜像：句柄逐个归还内核，最后 free 的 ib_buf 正是数据面整个生命周期唯一真正"装过数据"的内存。

## ⑤ 设计决策

**① 注释漂移实证（setup_ib.c:269-272）**：四行注释声称"buf_size 是 msg_size×num_concurr_msgs 的**两倍**大、接收缓冲占前半、发送缓冲占后半"——而实现 setup_ib.c:273 的公式**没有乘 2**，收发两侧用 `(buf_offset+msg_size)%buf_size` 环形复用**同一块**缓冲（client.c:58/98、server.c:60）。注释描述的是某个未实现（或已放弃）的分区方案。这是读老代码的经典陷阱：**注释与代码二选一时永远信代码**——环形复用在 RC 流控下成立，因为预投深度被 num_concurr_msgs 精确限制。

**② 三个"取设备上限"**：CQ 深度=max_cqe（setup_ib.c:289）、SRQ 深度=max_srq_wr（setup_ib.c:295）、QP wr=max_qp_wr（setup_ib.c:307-308）——教程干脆全取上限，把容量规划问题从示例代码里挤出去；工程代码这里要按 num_concurr_msgs×num_qps 实算。

**③ 单 CQ + SRQ 的极简扇入**：收发共用一个 CQ（setup_ib.c:303-304），所有 QP 共享一个 SRQ（setup_ib.c:305）——数据面一个线程 poll 一个 CQ 就能看到全部事件；代价是完成事件不带来源 QP 信息，埋下第 06 篇 imm_data 路由的伏笔。

**④ memset 驱动的幂等清理**：setup_ib.c:244 清零 + close_ib_connection 全判 NULL + setup_ib 自己的 error 路径只 free dev_list（setup_ib.c:335-339）不碰半成品——三者合力，让 main 的"成败都清理"成立。资源半途失败时，已创建部分由 main.c:42 兜底销毁，**这是本仓错误处理设计里最精巧的一环**。

**⑤ MR 权限与 QP 权限错位（冷知识）**：MR 只注册 LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE（setup_ib.c:279-281），而 QP 迁 INIT 时却声明了 REMOTE_ATOMIC（ib.c:19）——remote atomic 要求 MR **同时**带 IBV_ACCESS_REMOTE_ATOMIC 权限位，两侧缺一不可；本示例不做 atomic 操作故无害，但"QP 权限超集于 MR 权限"的错位是真实工程里 atomic 调用莫名失败的经典隐患源。

## ⑥ 新人提示

把 setup_ib.c:239-340 的每个 verbs 调用对照注释读一遍，就掌握了 verbs 资源创建的**规范顺序**：device→ctx→pd→(buf+mr)→cq→srq→qp→连接。改实验的入手点：msg_size/num_concurr_msgs 改了以后，buf_size 三因子自动跟随（setup_ib.c:273），无需动这里；但 msg_size 超过 IB_MTU=4096（ib.h:11）会在 RTR 阶段被拒。三个易踩点：① 多 HCA 机器上它永远开第一个设备（setup_ib.c:257），要挑卡得自己遍历 dev_list 比对 ibv_get_device_name；② memalign 是 glibc 特有（setup_ib.c:274），跨平台要换 posix_memalign；③ close_ib_connection 在 num_qps>实际创建数时也安全——calloc 出的数组多出的槽位是 NULL，destroy 循环判 NULL 跳过（setup_ib.c:347-351）。

验证练习：跑通后 `cat /sys/class/infiniband/mlx5_0/ports/1/lid` 对比日志里 qp 配对行打印的 lid（setup_ib.c:89-90），确认 IB_PORT=1 的选择。
