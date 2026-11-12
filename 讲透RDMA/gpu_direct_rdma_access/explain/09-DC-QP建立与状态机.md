# 09 DC QP 的建立与状态机：DCT 与 DCI 的不对称编排

> 对应 tour 第 7 步「打开 HCA：设备发现与 DC QP 建立」的 QP 半场。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

第 4 篇把 `rdma_open_device_client/server` 当黑盒给了契约，本篇拆开这个黑盒的 QP 半场，回答三个问题：DC QP（Dynamically Connected QP，不是任何图算法）怎么创建、两侧状态机各走到哪站、为什么形状不对称。全仓对 DC 的理解浓缩在 `struct rdma_device` 的三行注释里：`srq /* for DCT (client) only */`、`qpex /* DCI (server) only */`、`mqpex /* DCI (server) only */`（gpu_direct_rdma_access.c:109-112）——client 的 DCT 是只收不发的"靶"，server 的 DCI 是只发不收的"弓"，连 QP 附属句柄都不重叠。库还提供了身份判据 `is_server()`：`return device->srq == NULL`（gpu_direct_rdma_access.c:171-175）——一个字段同时编码了"没有 SRQ"与"是发起方"两件事。

DC 的本质：**连接不上协议栈建立，而在每个报文里现搭**。发起方 DCI 发包时携带目标地址三元组（AH + DCTN + DC_KEY，见 mlx5dv_wr_set_dc_addr，gpu_direct_rdma_access.c:969），HCA 在硬件里即时建立/复用到目标 DCT 的临时连接。所以两侧状态机可以各自 unilateral 地走完，没有任何握手报文——这与 RC QP 需要交换 QPN/PSN 的 CONNECT 语义是根本差异。

## 二、内部结构

三个 modify 函数构成状态机的全部迁移边：

```
client DCT:  RESET ──INIT──> INIT ──RTR──> RTR（终态，只收）
server DCI:  RESET ──INIT──> INIT ──RTR+RTS──> RTS（终态，只发）
错误恢复:     RTS/ERR ──> ERR ──排干──> RESET ──INIT→RTR→RTS──> RTS（第 11 篇）
```

- `modify_target_qp_to_rtr`（gpu_direct_rdma_access.c:387-418）：目标侧单跳到 RTR。min_rnr_timer=16（:395，RNR 退避基值——DCT 配 SRQ 做响应方，SRQ 暂空时靠它告知对端重试节奏）、path_mtu（:394）、attr_mask 带 `IBV_QP_MIN_RNR_TIMER // for DCT`（:404-407）——这条边是 DCT 专属参数的唯一落点。
- `modify_source_qp_to_rtr_and_rts`（gpu_direct_rdma_access.c:424-476）：源侧两连跳。RTR 半段只设 STATE|AV|PATH_MTU（:442-444）；RTS 半段设 timeout=16、retry_cnt=7、rnr_retry=7、max_rd_atomic=1（:455-460）——重试参数全拉满、深度参数取最小，样例的取舍：可靠优先、流水线深度 1 够用。
- `modify_source_qp_rst2rts`（gpu_direct_rdma_access.c:491-523）：从零重建的三连跳 INIT→RTR→RTS，供 open 时（server 侧）与错误恢复（第 11 篇）复用同一通道。

创建段分居两个 open：client 在 gpu_direct_rdma_access.c:585-658（SRQ→DCT→INIT→RTR），server 在 gpu_direct_rdma_access.c:775-834（DCI→qpex→mqpex→rst2rts）。

## 三、外部连接

创建走的全是 mlx5 vendor 口，而非 verbs 标准口：`mlx5dv_create_qp`（gpu_direct_rdma_access.c:624、811）接收 `attr_ex.qp_type = IBV_QPT_DRIVER`（:605、784）+ `attr_dv.dc_init_attr.dc_type`（:620、798）——IBV_QPT_DRIVER 是 verbs 留给厂商扩展的 QP 类型通道，DCT/DCI 是 mlx5 的私货，标准 verbs 里根本没有这两个词。DCI 还要两级句柄升级：`ibv_qp_to_qp_ex`（:818）拿到 verbs-ex 批量提交句柄，`mlx5dv_qp_ex_from_ibv_qp_ex`（:823）再拿到 vendor 扩展句柄——第 10 篇的 wr_start 系列与 mlx5dv_wr_set_dc_addr 分别落在这两级上。

DC_KEY 是横跨两侧的共享秘密：`0xffeeddcc`（gpu_direct_rdma_access.c:68，注释 "defined for both sides"）。它在 DCT 创建时作为 `dct_access_key`（:621），又在每个 WR 上由发起方再次呈交（:969、987）——DCT 校验不一致即拒，这是 DC 模型里唯一的"准入控制"。client 把 DCT 的 qp_num（即 DCTN）写进凭据串上链（gpu_direct_rdma_access.c:1256，第 4 篇），server 由此知道往哪打。

此外每条 GRH 路径都带 `traffic_class = TC_PRIO << 5`（TC_PRIO=3，gpu_direct_rdma_access.c:70），三处设置点（:402、440、1410）共用同一行注释：`<<3 for dscp2prio, <<2 for ECN bits`——把优先级编进 DSCP 高 3 位，是 RoCE 流量调度的标准姿势。

## 四、数据流

**client 建靶**（rdma_open_device_client 内）：先建 SRQ（max_wr=2、max_sge=1，gpu_direct_rdma_access.c:588-589——响应侧收 buffer 极小，DC 的响应方只被动接 READ/WRITE 请求，不收大流量）；再建 DCT（attr_ex 挂 SRQ，:616 注释 "Should use SRQ for client only"）；INIT 时授 `REMOTE_READ | LOCAL_WRITE | REMOTE_WRITE` 三权（:637）——这是**准入策略**：允许远端对本 DCT 后面的 MR 做什么；最后 modify_target_qp_to_rtr 到 RTR 终态（:652）。qpex/mqpex 保持 NULL——client 没有任何发送路径。

**server 建弓**（rdma_open_device_server 内）：不建 SRQ（:775 注释）；DCI 创建时声明的全是发送侧资源——`max_send_wr = SEND_Q_DEPTH`（640，:800）、`max_send_sge = MAX_SEND_SGE`（10，:801）、`send_ops_flags = IBV_QP_EX_WITH_RDMA_WRITE | IBV_QP_EX_WITH_RDMA_READ`（:804-805，把可提交的动词白名单写进 QP）；再加 `MLX5DV_QP_CREATE_DISABLE_SCATTER_TO_CQE`（:807-808，注释 "driver doesnt support scatter2cqe data-path on DCI yet"——2019 年驱动限制，主动关掉 CQE 内联散射优化换正确性）。两级句柄升级后直接 `modify_source_qp_rst2rts`（:828）——**开箱即 RTS**，无握手等待，server 起来就能放箭。

**复位重建**（modify_source_qp_rst2rts，gpu_direct_rdma_access.c:491-523）：INIT 段的 qp_attr 填了 `qp_access_flags = IBV_ACCESS_LOCAL_WRITE`（:499），但 attr_mask 里该位被显式清零并注释 "we must zero this bit for DCI QP"（:501-504）——结构体字段值是死字，真正生效的只有 STATE|PKEY_INDEX|PORT。这是 verbs 的历史坑：字段填了不代表提交。链尾恢复 `qpex->wr_flags = IBV_SEND_SIGNALED`（:520），为第 10 篇的信令语义复位默认值。

## 五、设计决策

- **为什么 DCT 停在 RTR、DCI 直达 RTS**：RTR 是"可响应"的最低状态，RTS 是"可发起"的状态。靶不需要 RTS，弓不需要在 RTR 停留——两个终态各自最小化。整个系统因此**没有连接建立时延**：client 注册完即可发凭据，server 收到即可提交，任何时刻都不存在"还没连上"的窗口。这正是 DC 对存储扇出场景的价值：N 个 client 共享零连接开销。
- **为什么 INIT 权限两侧不同**：DCT 的三权（:637）是远端访问授权，决定 RDMA WRITE/READ 能不能落进来；DCI 的 access_flags 被 mask 清零（:504）——发起方不需要任何 remote 访问权，LOCAL_WRITE 字段纯属无效填空。
- **为什么 SRQ 只属于 DCT**：SRQ 是接收侧资源池。DCI 不收任何东西，没有 RQ；DCT 是所有发起方共享的响应点，SRQ 让它的接收 buffer 与连接数解耦。is_server() 用 srq==NULL 判身份因此天然正确。
- **max_rd_atomic=1 的保守**：每个 DCI 同时只允许 1 个在飞的 RDMA READ 响应处理（:460）。demo 每迭代一个任务，深度 1 足够；生产高并发要调大。
- **重试参数全满（7/7）**：retry_cnt/rnr_retry=7（:457-458）是verbs 最大值——样例环境（首次跑通优先）选择"绝不轻言失败"，代价是故障场景下恢复变慢，第 11 篇的人工排干路径正是为此兜底。

## 六、新人提示

1. **看状态迁移先开 `-D 1`**：每个 ibv_modify_qp 前后都有 DEBUG_LOG 打印 qp 状态与 attr_mask（如 gpu_direct_rdma_access.c:643-650），调试会话里状态机是可观测的，比读代码快。
2. **IBV_QPT_DRIVER 不是"任意驱动 QP"**：它是 verbs 的厂商扩展槽位，真正语义在 attr_dv 的 dc_type 里。去掉 mlx5dv 头文件这层，qp_type 本身不传达 DCT/DCI 信息——搜索代码时 grep "DCTYPE" 而不是 "QPT_DRIVER"。
3. **qp_num 打印格式不一致**：DEBUG_LOG 用 `%x`（:415）与 `%lx`（:452、473）混打 qp_num——uint32 值在 %lx 下读高位垃圾是经典假象，对比日志时只看低 32 位。
4. **DC_KEY 必须两侧同值**：硬编码 0xffeeddcc（:68）是 demo 便利。生产环境这是"任何知道 DCTN+key 的发起方都能读写你显存"的活凭证管理问题——凭据串走明文 TCP（第 8 篇），样例的安全模型整体是"内网可信"。
5. **别给 DCT 找 RTS**：读 RDMA 文档时 RC 的 RESET→INIT→RTR→RTS→SQD→SQE→ERR 七态全家桶会先入为主；DC 两侧各自只走子集，且 DCT 的 RTR 不带 dest_qp_num/dest_psn——它没有"对端"概念，地址由发起方报文携带。把 RC 思维带进 DC 是新人最大误读。
