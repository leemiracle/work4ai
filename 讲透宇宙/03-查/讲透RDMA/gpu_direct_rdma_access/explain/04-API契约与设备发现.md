# 04 API 契约与设备发现：九个函数、两个 open 入口与 DC QP 建立

> 对应 tour 第 4、7 步「库的门面」「打开 HCA：设备发现与 DC QP 建立」。锚均对 HEAD `a99d506` 核实。

## 一、角色定位

gpu_direct_rdma_access.h（164 行）是全仓的宪法：它定义了 9 个对外 API（gpu_direct_rdma_access.h:90-158）、一个不透明设备句柄 `struct rdma_device`（:51）、一个任务描述 `struct rdma_task_attr`（:69-78）。client.c 与 server.c 各只 include 这一个库头（client.c:49、server.c:50），所以**读这 164 行等于读完了两个 main 能看到的一切**。实现侧 gpu_direct_rdma_access.c 的 1548 行则按"设备发现→QP 状态机→注册与描述串→数据面→错误恢复"分层展开，本篇覆盖前两层（发现与建立），注册留给第 5 篇、数据面留给组 2 的第 12 步篇目。

九个 API 按生命周期排：`rdma_open_device_client/server`（:90-91，同一对外的两种角色形态）→`rdma_buffer_reg/dereg/get_desc_str`（:106-120）→`rdma_submit_task`（:138）+`rdma_poll_completions`（:156-158）→`rdma_reset_device`（:96）→`rdma_close_device`（:101）。头文件的注释就是契约文本：例如 get_desc_str 明说"client 应把描述串传给 server"（:112-113），submit 明说完成结果从 poll 来（:133-134）——控制流被文字钉死。

## 二、内部结构

**设备发现有一对双胞胎，但只有一个活着**。`open_ib_device_by_name`（gpu_direct_rdma_access.c:197-241）走传统路线：ibv_get_device_list 枚举（:207）、按名字 strcmp 匹配（:218）、ibv_open_device 打开（:229）。但它是**死代码**——全仓无调用；两个 open 入口实际都走 `open_ib_device_by_addr`（:542、:730）。by_addr 借 rdma_cm 之力：rdma_create_event_channel（:250）→rdma_create_id（:256）→`rdma_bind_addr` 把本地 IP 绑上去（:262）——rdma_cm 自动找到该 IP 所属 netdev 对应的 HCA，省掉手工枚举，还顺手拿到 port_num（:282）。

**「星号返回」的所有权盲区**：by_addr 返回 `struct ibv_context *`（星号指针，:288 返回 `rdma_dev->cm_id->verbs`），调用方把它存进 `rdma_dev->context`（:542）。陷阱在于这个 context **归 cm_id 所有**——close_ib_device 若走 cm 路径，先显式 `rdma_dev->context = NULL`（:304-305 注释原话 "we just referance the cma's ibv_context"），只销毁 id 与 channel（:309、:316），绝不 ibv_close_device；只有非 cm 打开的 context 才走 ibv_close_device（:319-325）。另一处盲区：IP 绑上了不网卡不存在的接口时 rdma_bind_addr 可能成功但 `cm_id->verbs == NULL`，必须显式判空（:277-280）——星号非 NULL 不代表背后有 HCA。

**QP 建立按角色分裂**。client 侧 `rdma_open_device_client`（:526-711）建的是**被动的靶**：PD（:555）→CQ 深度 640（:577）→SRQ 仅 max_wr=2/max_sge=1（:586-589，象征意义大于实用）→`mlx5dv_create_qp` 以 `MLX5DV_DCTYPE_DCT` 建 DCT（:618-624）→INIT 态权限三位全开 LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE（:633-638）→RTR（:652 调 modify_target_qp_to_rtr :387-418）。**DCT 没有 RTS**——它不主动发包，迁到 RTR 即就位待连。server 侧 `rdma_open_device_server`（:714-886）建**主动的弓**：无 SRQ（:775 注释），DCI 类型（:796-798），max_send_wr=SEND_Q_DEPTH=640（:800）、`qp_available_wr` 记满配额（:802），声明 RDMA_WRITE/READ 两个 send op（:804-805），并 `DISABLE_SCATTER_TO_CQE`（:807-808 注释：驱动尚不支持 DCI 上的 scatter2cqe 数据路径）。随后 `ibv_qp_to_qp_ex`/`mlx5dv_qp_ex_from_ibv_qp_ex` 拿到动词式编程句柄 qpex/mqpex（:818、:823）——数据面靠它们流式发 WR。状态机走 `modify_source_qp_rst2rts`（:491-523）：INIT 时 attr_mask 故意置 0 掉 `IBV_QP_ACCESS_FLAGS` 位（:501-504 注释 "we must zero this bit for DCI QP"），再经 RTR 直达 RTS（:515→:424-476，timeout=16/retry=7/rnr_retry=7，:456-458），最后默认 wr_flags=SIGNALED（:520）。

## 三、外部连接

头文件 include verbs 与 mlx5dv 两个系统头（gpu_direct_rdma_access.h:38-39），把 verbs 类型（struct iovec 经 sys/uio.h，:36）漏到调用方——task_attr 里 local_buf_iovec 直接用 iovec（:74）。client.c 以本地 IP 调 open_client（client.c:338），server.c 以 `-a` 地址调 open_server；GID 定位依赖 ibv_helper.h 的 `ibv_find_sgid_type`（ibv_helper.h:147，在 gpu_direct_rdma_access.c:351-353 被调，找 RoCE v2 sgid 索引——详见第 6 篇）。角色判定有个巧妙的内部约定：`is_server()` 即 `srq == NULL`（:171-175），SRQ 的有无成了角色标志位。

## 四、数据流

client 启动流（client.c:338）：calloc 设备对象（:531）→by_addr 定位 HCA（:542）→`rdma_set_lid_gid_from_port_info`（:547 调 :332-381）：ibv_query_port 拿 active_mtu/lid（:337、:343-344），Ethernet 链路时用 `ibv_find_sgid_type` 找 RoCE_V2 的 gidx（:350-353），ibv_query_gid 填 gid（:363），`is_global = interface_id != 0`（:374）——这些值之后全部进第 5 篇的描述串。→PD/CQ/SRQ/DCT 依次建（:555-630）→INIT/RTR（:633-655）→AH 哈希初始化（:658，见第 6 篇）→返回句柄。server 流对称（:714-886），差异全在第二节。一次成功的 open 之后，设备对象里已具备：qp（DCT 或 DCI）、qpex/mqpex（仅 server）、lid/gid/gidx/mtu、app_wr_id 记账环、AH 缓存——后续所有数据面动作只消费这些。

## 五、设计决策

- **by_addr 替代 by_name 是演进终点**：按 IP 找设备让命令行 `-a` 同时承担"选 HCA+选网段"双语义，且天然兼容多宿主；by_name 遗骸保留（:197-241）但无人问津——读代码时可跳过，但它是"样例如何演化"的化石。
- **DC_KEY 硬编码 0xffeeddcc**（:68）两侧共享：DC 目标端用它过滤非法发起方。样例求简，生产应换成带外协商的密钥。
- **DCT 权限三位全开 vs DCI 不设 access_flags**：被写方（client 显存）必须声明远端可写可读+本地可写（:637）；发起方 DCI 的权限模型不同，INIT 时 access_flags 位必须清零（:501-504）——两套 QP 的 verbs 语义差异被封装在两个 modify 函数里。
- **CQ/QP 深度 640**（:66-67）与 wr_id 记账环同尺寸（:122），SEND_Q_DEPTH 是发送配额与完成去重的共用常数——一个数字贯穿三处设计（详见第 12 步篇目）。
- **PRINT_LATENCY 撕裂类型**：开宏后 cq 变 ibv_cq_ex（:104-108），QP 创建时还得 `ibv_cq_ex_to_cq` 转回基础类型填 send_cq（:607-608）——条件编译在类型系统上打补丁的代价。

## 六、新人提示

1. **读 9 个 API 注释优先于读实现**：头文件 :79-158 的注释把调用顺序、返回值语义、错误路径写全了，是这份样例最接近"文档"的东西。
2. **别追 open_ib_device_by_name 的调用者**——追不到，它是死代码（ONBOARDING 勘误 #3）；两个入口在 :542 与 :730。
3. **verbs QP 状态机在此仓被两函数封装**：想理解 DCT 为何无 RTS，对照 modify_target_qp_to_rtr（:387）与 modify_source_qp_to_rtr_and_rts（:424）的 attr_mask 差异，再看 :501-504 那行"必须清零"注释，胜读半章规范。
4. **is_server 的隐式契约**：新增"第三种角色"会破坏 `srq==NULL` 判定（:174），改结构体前先想清楚。
5. **排查 open 失败先看两条**：IP 不属任何 HCA（verbs==NULL，:277）与 RoCE v2 GID 找不到（gidx<0 报错，:355-358）——前者查 `-a` 与 map 脚本输出是否同源，后者查驱动是否带 RoCE v2 支持（第 6 篇的 sysfs 探测正是为此）。
