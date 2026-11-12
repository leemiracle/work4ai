# 09 · net_ib：IB/RoCE 网络后端（init.cc / common.cc / connect.cc / gdr.cc）

## ① 角色定位

`src/transport/net_ib/` 是 NCCL 的 InfiniBand/RoCE（RDMA）网络传输插件，跨节点通信的默认主力。它以 `ncclNet_t` 对象（`common.cc:244-267` 的 `ncclNetIb`）注册进框架，向上实现 init/listen/connect/accept/regMr/isend/irecv/iflush/test 全套虚表，向下经 verbs API 驱动 HCA。本篇以 `init.cc`（744 行）为主线，串联 `common.cc`、`connect.cc`（连接状态机与 QP）、`gdr.cc`、`reg.cc` 与 `p2p.cc`（数据面）。

先钉一个误解：**gdr.cc 不是 GDRCopy**。它探测 GPUDirect RDMA 内核支撑——`nvidia_peermem` 模块（`gdr.cc:14-21`）与 DMA-BUF（`gdr.cc:45-83` fd=-1 dummy 探测）。GDRCopy 本体在 `src/misc/gdrwrap.cc`，由 `src/transport/net.cc` 消费，与本目录解耦。

## ② 内部结构

**verbs 符号绑定**：旧版用 weak symbol，v2.32.3 已换成符号表——`wrap_ibv_symbols()` 经 `std::call_once` 填表（`ibvwrap.cc:26-29`）。`NCCL_BUILD_RDMA_CORE` 直接取链接符号（`ibvsymbols.cc:16-70`）；否则运行时 dlopen（`NCCL_IBVERBS_LIB`→`libibverbs.so`→`.so.1`，`ibvsymbols.cc:80-86`）后 dlvsym 按版本挑：基础锁 `IBVERBS_1.1`，`ibv_reg_mr_iova2`/`ibv_reg_dmabuf_mr` 分别从 `IBVERBS_1.8`/`IBVERBS_1.12` 挑（`ibvsymbols.cc:123-125`），挑不到静默置 NULL。

**设备发现（ncclIbInitDevices，`init.cc:429-675`）**：`netRefCount` 保证进程内只跑一次（`init.cc:25,431`）：`ibv_fork_init`→找唯一 OOB IP 接口（`init.cc:447-452`）→解析 `NCCL_IB_HCA`（`^` 排除、`=` 精确，`init.cc:462-466`）→逐端口过滤 ACTIVE 且链路层 IB/Ethernet（`init.cc:499-508`），每个 (device,port) 填一项 `ncclIbDevs[]`（上限 32，`common.h:131`），speed 优先 `ibv_query_port_speed` 否则查表（`init.cc:127-138`），再按 PCI 拓扑排序保证跨 rank 一致（`init.cc:636`）。

**vDevice（NIC 融合）**：物理设备之上是 `ncclIbMergedDevs[]`（上限 256，`common.h:132`）。`ncclIbMakeVDeviceInternal`（`init.cc:208-280`）把多物理口融合成一个 vNIC：名字 `+` 拼接、speed 累加、链路层必须一致（`init.cc:261-274`）；单设备也包成 vDevice，上层只见其索引。

**连接状态机（connect.cc）**：listen/connect/accept 全是可重入非阻塞状态机，`ncclIbCommStage` 记 state/offset/buffer（`connect.cc:45-50`），按 state `goto` 断点续跑（`connect.cc:846-851`）；元数据走 TCP（OOB），数据面才走 RDMA。握手：先互换 vDeviceProps+oooRq 能力、取两侧 max 得 nqps（`connect.cc:898-922`），再互发 `ncclIbConnectionMetadata`（QPN/GID/MTU/rkey/SL/TC，`connect.cc:1046-1063`），最后发 ready（`connect.cc:1118-1121`）。QP 走 create→INIT（`connect.cc:369-379`）→RTR（`connect.cc:432-487`）→RTS（`connect.cc:489-505`），以 stripe 轮转铺在物理设备上（`connect.cc:687-692`）；三段 attr 缓存在 `ncclIbQp`（`common.h:316-336`）供故障重建；超时/重试默认 20/7（`connect.cc:16-17`）。

## ③ 外部连接

- 上游 `src/transport/net.cc` 插件框架持有 `ncclNetIb`；graph/tuning 层从 `ncclIbGetProperties` 读 speed/railId/maxComms（即 maxQp，`init.cc:712`）。
- OOB 依赖 `src/misc/socket.cc`；`ibvwrap.cc`/`ibvsymbols.cc`/`mlx5dvwrap.cc` 是 verbs 间接层。
- 下游 proxy 线程（`src/proxy.cc`）在进度回调里调 isend/irecv/test；resiliency 子模块经 `ncclIbResiliencyInit` 挂进每条 comm（`common.cc:72`），enable 后强制 BY_ID 与 prepost（`common.cc:76-81,93-104`），端口恢复线程随 `ncclIbInit` 启动（`init.cc:682`）；`ptrSupport` 打 `NCCL_PTR_CUDA`/`NCCL_PTR_DMABUF`（`init.cc:701-708`）。

## ④ 数据流

一次 isend/irecv 对（`p2p.cc`）：

1. **接收端发布**：`ncclIbIrecv`（`p2p.cc:457-567`）按 slot=`fifoHead % NET_IB_MAX_REQUESTS` 把 rkey/addr/size/tag 填进影子 CTS（`p2p.cc:545-557`），`ncclIbPostFifo` 用 RDMA WRITE 把 CTS 写到 sender 的 ctsFifo（`p2p.cc:391-455`）；CTS 为 unsignaled 写，靠 `slot==devIndex` 周期 signaled 防队列涨死（`p2p.cc:413-439`）。
2. **发送端等 CTS**：`ncclIbIsend` 自旋等 `slots[0].idx==fifoHead+1`（`p2p.cc:294-303`），凑齐 nreqs 进 `ncclIbMultiSend`。
3. **MultiSend 装配 WR 链**（`p2p.cc:83-273`）：每子请求一条不 signaled 的 `IBV_WR_RDMA_WRITE`，末条 `RDMA_WRITE_WITH_IMM` 带 immData 且 signaled（`p2p.cc:155-159`）；immData 在 BY_INDEX 传 size、BY_ID 传 id（`p2p.cc:133-140`）。数据按设备权重切块并按 `IB_WRITE_CHUNK_ALIGNMENT=128` 对齐——注释直言这是"让 LL 和 LL128 协议能工作"的对齐要求（`p2p.cc:80-81`）。这是 IB 层与设备协议的唯一耦合点：**net_ib 对 LL/LL128 无感知**，标志位由 GPU kernel 写入，RDMA 只搬字节。
4. **QP 选择与完成**：`(id*nqps+qpIndex)%nqps` 轮转（`common.h:475-486`），多设备按 weights 分带宽（`common.h:405-418`）。`ncclIbTest`（`p2p.cc:924-997`）逐设备 `ibv_poll_cq` 按 opcode 分发：RECV_RDMA_WITH_IMM 扣 events、补挂 recv WR 并回填 size（`p2p.cc:851-885`）；RDMA_READ/RDMA_WRITE 分别是 flush/CTS 完成。events 四槽全零才完成（`p2p.cc:675-682`）。
5. **GDR flush 与 MR**：数据落显存后用 loopback QP 自读 1 字节刷 HCA 缓存（`connect.cc:1334-1392`）；`reg.cc:10-68` 做按页对齐的 MR 引用计数缓存。

## ⑤ 设计决策

- **AR 默认开在 IB 网络上**：链路层为 IB 时 `ar=1`，可被 `NCCL_IB_ADAPTIVE_ROUTING` 覆盖（`init.cc:588-591`）。AR 乱序破坏 imm 顺序语义，故大消息拆"纯 WRITE 主体+带 imm 尾包"（阈值默认 8192，`p2p.cc:13-14,143-147`）；OOO RQ 开启时阈值被忽略（`init.cc:628-634`）。
- **PCI 排序+rail/plane**：按 `fullPciPath` 数值排序（`init.cc:45-59`）保证跨节点一致；CX9 rail 布局 FLIP/ALT/BLOCK（`init.cc:318-339`，识别条件 vendorId=0x02c9 且 fwVer "82." 前缀 `init.cc:310-314`），planeId 最高位留虚拟融合位（`init.cc:104-125`）。
- **RX 匹配双方案**：默认 BY_INDEX；resiliency 或 OOO RQ 强制 BY_ID（`common.cc:73-81`）以容忍乱序与重放。CTS FIFO 等有 32 字节对齐断言（`common.h:559-564`）防 Relaxed Ordering 拆写乱序。
- **异步致命错误监测**：每设备一条 detached async 线程（`init.cc:602-604`）循环收事件，DEVICE_FATAL/CQ_ERR/QP_FATAL 记 fatal 计数（`common.cc:166-242`），数据面每次 test 前查计数快速失败（`common.cc:33-39`）；GID/SPEED 事件驱动热刷新与 LB 重平衡（`common.cc:116-163`）。

## ⑥ 新人提示

1. 先跑 `NCCL_DEBUG=INFO`：`init.cc:596-600` 的 per-device 日志含 provider/speed/pciPath/ar，是诊断网卡选择的第一手。
2. ibvwrap 里 grep 不到 weak symbol 是正常的——机制已换成 ibvsymbols 表；排查加载失败看 `dlvsym failed on ...` 告警，必要时 `NCCL_IBVERBS_LIB` 指库。
3. 错误三连 HINT（`common.h:755-777`）：LOC_PROT_ERR→查 ACS（`NCCL_NET_GDR_LEVEL=0` 验证）；WR_FLUSH_ERR→同节点 NIC 互通；RETRY_EXC_ERR→调大 `NCCL_IB_TIMEOUT`。
4. 读 connect.cc 先画状态机跳转图（enum `connect.cc:32-43`），`goto` 重入是配合外层 poll 的异步分步。
5. "发了没完成"先回看事件模型：events 按设备累计、CTS 也有 CQE；调 QP 数前先看 `common.h:450-465` 理清 WR 预算。
