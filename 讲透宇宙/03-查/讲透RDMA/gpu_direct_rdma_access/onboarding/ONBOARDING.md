# gpu_direct_rdma_access 新人导览（ONBOARDING）

Mellanox 官方 GPU Direct RDMA 示例（`/usr-data/data2/kylin/network/rdma/gpu_direct_rdma_access`，git HEAD `a99d506`），走通"RDMA 直接读写远端 GPU 显存"，行号锚均经源码核实。

## 1. 项目定位：为什么 RDMA 要绕过主机内存

传统路径 server 数据进 client GPU 要三段式：NIC→server 主机内存→网络→client 主机内存→cudaMemcpy→显存，两次 PCIe 进出+一次 CPU 主持的 H2D。GPU Direct 把中间人干掉——NIC 直接对端显存 DMA。本示例 client 跑 DGX2 等 GPU 机器，server 模拟文件存储（README.md:2）；client 把 GPU 缓冲描述凭据经 TCP 发过去，server 用 **DC QP** 直接对远端显存 RDMA Write（README.md:4）；性能根基是与 NIC 同 PCI bridge 的选卡（README.md:6）。库对外仅 9 个 API（gpu_direct_rdma_access.h:90-158），两个 main 各只 include 它。

## 2. 快速上手：构建与环境准备

开关全在 Makefile：`USE_CUDA=1` 加 CUDA include、定义 `-DHAVE_CUDA`、链 `-lcuda`（Makefile:5-9）；`PRINT_LAT=1` 加 `-DPRINT_LATENCY`（Makefile:15-16）；三个公共目标文件分别与 client.o/server.o 链成两个可执行文件（Makefile:41-45）。client 机器 `make USE_CUDA=1`、server 机器 `make`（README.md:61-66）。跑通前两处主机级准备：

- **ARP 卫生**：多宿主 RoCE 机器 ARP 应答源地址错乱会废掉 GID 路由，脚本对 UP 端口 ndev 设 `arp_announce=1`/`arp_ignore=2`（arp_announce_conf.sh:55-56）。
- **PCI 拓扑亲和**：`map_pci_nic_gpu.sh` 解析 NIC 的 PCI 路径与上级 bridge（map_pci_nic_gpu.sh:57-60），遍历 `/sys/class/pci_bus` 找同桥设备（:70）后 `lspci` 打印 is near 清单（:75-79），指导 `-u BDF` 选卡。

运行示例 README.md:70/88；默认端口 18515/4096 字节/1000 迭代（client.c:210-213）。前置依赖 MLNX_OFED、CUDA、nv_peer_memory（README.md:42）——没有它显存页 pin 不住，注册必失败。

## 3. 架构总览：12 层图谱

64 节点划 12 层：**L01** 构建配置｜**L02** 通用工具（utils.c:44-86）｜**L03** GPU 显存层（gpu_mem_util.c:113-275）｜**L04** khash.h+ibv_helper.h（:88-176）｜**L05** API 契约（gpu_direct_rdma_access.h:69-78）｜**L06** 设备发现与 QP 状态机｜**L07** 内存注册与 AH 缓存｜**L08** 任务执行与完成收割｜**L09-L12** 两 main/主机脚本/README。两个 main 只依赖 L05 头；L05-L08 全在 1548 行的 gpu_direct_rdma_access.c。控制面（TCP）与数据面（RDMA）严格分离是全仓最该记住的形状。

## 4. 核心链路：一次 RDMA Write 的完整生命周期

1. **client 打包上链**：main（client.c:302）→`rdma_open_device_client` 建 DCT 设备（:338）→`work_buffer_alloc` 按 BDF 分配显存（:347）→`rdma_buffer_reg` 拿 rkey（:362）→描述串（:370-371）→`pack_payload_data` 以 `|type 1B|size 2B|payload|` 长度前缀打包（client.c:144-159）→循环 `write`（:417）、`recv` 等 ack（:425）。
2. **server 收凭据并直写远端**：`open_server_socket` 监听-accept-关临时 socket（server.c:89-144）；收 type/size/payload 三跳（:313-340），`sscanf` 还原 flags（:337）组 task_attr（wr_id=迭代号，:348）→`rdma_submit_task`（gpu_direct_rdma_access.c:1342）解析凭据、建 AH（:1363-1413）→`rdma_exec_task`（:1416）：在 DCI 上 `ibv_wr_start`（:905）、按 READ/WRITE 标志选 `ibv_wr_rdma_read/write`（:899-901）、`mlx5dv_wr_set_dc_addr` 带对端 DCTN+DC_KEY（:969）、`ibv_wr_complete` 敲门铃（:992）——数据从 server 内存直落 client 显存。
3. **完成收割**：server 轮询 CQ（server.c:379-382），库内 `ibv_poll_cq` 收 CQE（:1527）、去重回填应用 wr_id（:1538-1544）；出错时 persistent 模式走 `rdma_reset_device`（server.c:391-393）后回 ack（:399）。
4. **带宽结算**：双方 `print_run_time`（client.c:440、server.c:407），按起始时间戳出总字节、Mbit/sec、usec/iter（utils.c:77-83）。

## 5. 关键模块深讲：gpu_direct_rdma_access.c 三连层

1548 行核心库分三个半场，对应 L06/L07/L08。

**半场一：设备发现与 QP 状态机（L06）**。`open_ib_device_by_addr`（:244-296）用 rdma_cm 的 `rdma_bind_addr`（:250-262）按本地 IP 定位 HCA；`rdma_set_lid_gid_from_port_info`（:332-381）查端口拿 MTU/LID，Ethernet 链路经 `ibv_find_sgid_type` 定位 RoCE v2 sgid 索引（:350-353）。角色分流：client 侧 `rdma_open_device_client`（:526-711）建 PD/CQ、SRQ（:586-596），`mlx5dv_create_qp` 以 `MLX5DV_DCTYPE_DCT` 建被动 QP（:618-624，权限三位全开 :637），`modify_target_qp_to_rtr`（:387-418）迁 RTR 即待连——DCT 无 RTS，是被连的靶。server 侧 `rdma_open_device_server`（:714-886）无 SRQ，建 DCI（:796-798）并带出 qpex/mqpex（:818-823），`modify_source_qp_rst2rts`（:491-523）经 INIT→RTR→RTS 直达发包态。出错时 `rdma_reset_device`（:1009-1075）迁 ERR、投 `WR_ID_FLUSH_MARKER` 排空 CQ（:1039-1054）后重建 RTS。

**半场二：内存注册与 AH 缓存（L07）**。`rdma_buffer_reg`（:1155-1192）对任意地址 `ibv_reg_mr`（:1170），权限三位全开（:1166）——显存地址由 nv_peer_memory 把 GPU 页 pin 成 NIC 可 DMA 物理页；`rdma_buff_cnt` 挂在设备上，close 时非零拒关（:1083-1086）。`rdma_buffer_get_desc_str`（:1242-1262）以七段式 `addr:size:rkey:lid:dctn:g:gid` 序列化（:1251-1259），长度 sizeof 字面量定死（:1240）；对端 `wire_gid_to_gid`（:1215-1227）逐 32 位 ntohl 还原。`rdma_create_ah_cached`（:1264-1305）以整个 ah_attr 结构 memcmp 相等为键查 khash（:186-190），命中复用、未命中 create 入表带回滚（:1289-1292）。

**半场三：任务执行与完成收割（L08）**。`rdma_submit_task`（:1342-1419）是唯一数据面入口：解析描述串→offset 平移远端窗口（:1381-1382）→仅 debug 模式跑 `buff_size_validation`（:1388-1395，错尺寸交硬件兜底）→组 exec_params 转调。`rdma_exec_task`（:889-1006）先按 `ceil(iovcnt/MAX_SEND_SGE)` 预算 WR 配额（:893-898），环形取槽登记应用 wr_id（:920-934），把**槽位下标**而非应用 wr_id 写进 qpex->wr_id（:936）；多 SGE 按 MAX_SEND_SGE=10 分片，仅末片置 SIGNALED（:944-970）。`rdma_poll_completions`（:1422-1548）批收 CQE 后按虚拟 wr_id 查记账槽：ACTIVE 位在才上报并清零（:1538-1539），同时归还 qp_available_wr（:1540）——聚合上报与去重全靠这个环。

## 6. 设计决策

- **DC QP 选型**：发起方 DCI 无连接、报文自带地址，目标方 DCT 像 SRQ 一样被共享——client 一份 DCT+SRQ 服务任意多 server（:586-624），server 建 DCI 主动发包（:796-798），免 per-connection 维护，适合存储一对多扇出。两侧共享硬编码 `DC_KEY 0xffeeddcc`（:68），发起时带 AH+DCTN+DC_KEY（:969），DCTN 藏在描述串第五段（:1256）。
- **nv_peer_memory pin**：显存页默认不可被 PCIe 外设 DMA，`ibv_reg_mr` 注册显存能成全靠该内核模块；配套 64KB 对齐分配（gpu_mem_util.c:158-162）与 `CU_CTX_MAP_HOST` 上下文（:188）。
- **USE_CUDA 条件编译**：CUDA 依赖全关进 `#ifdef HAVE_CUDA`（gpu_mem_util.c:51-54、:66-226），`work_buffer_alloc` 一套 API 双形态（:232-258）——server 零依赖编过，client 不给 `-u` 就退化 CPU 基准。
- **wr_id 挂 app_wr_id[SEND_Q_DEPTH]**：硬件 CQE 的 wr_id 域复用为记账数组下标（:936），真实 wr_id/占用 WR 数/活跃标志存 640 槽（:82-86）。一个设计解三件事：多 WR 聚合上报（signaled 仅末片 :946）、CQE 去重（:1539）、发送配额记账（:893-898、:1540）。

## 7. 新人学习路径（按 14 步 tour）

①README 动机→②Makefile 双开关→③ARP+拓扑两脚本→④头文件 9 API 定分工（gpu_direct_rdma_access.h:90-158）→⑤gpu_mem_util 选卡分配（gpu_mem_util.c:113-211）→⑥khash+RoCE v2 GID 定位（ibv_helper.h:147-176）→⑦设备发现与 DC 状态机（第 5 节半场一）→⑧MR 注册与描述串（半场二）→⑨server 前半（server.c:89-144）→⑩client 全流程（client.c:302-437）→⑪server 循环体直写（server.c:300-373）→⑫数据面三件套 submit→exec→poll（半场三）→⑬错误恢复与关闭（:1009-1152）→⑭utils 收官结算（utils.c:66-86）。节奏：①-④建全局观，⑦⑫攻核心库，⑨-⑪连起两个 main 隔空握手。

## 8. 已知坑与勘误

1. **khash.h 是 klib 定制版非原版**：新增 `KHASH_TYPE`/`KHASH_IMPL` 两段式宏（khash.h:382-386），声明进头、实现集中一个 .c，与上游 `KHASH_INIT` 单体宏不兼容；核心库用法是 :76 声明+:192-193 实现+自定义 hash/equal（:178-190）。
2. **`#ifdef HAVE_CUDA` 块是静态分析盲区**：gpu_mem_util.c 的 init_gpu/free_gpu/get_gpu_device_id_from_bdf 全在条件块内（:66-226），不开 USE_CUDA 时符号不存在，tree-sitter 提取不全需人工补齐。
3. **open_ib_device_by_name 是死代码**：定义于 :197-241 但全仓无调用，两个 open 入口都走 by_addr（:542、:730）。
4. **PRINT_LATENCY 分支潜伏编译 bug**：rdma_poll_completions 该分支 :1453 引用 `wc[i].wr_id`，但分支内既无 `wc` 也无 `i`（CQE wr_id 在 `rdma_dev->cq->wr_id`）——`make PRINT_LAT=1` 必编译失败，此路径久未被构建验证。
5. **server 的 debug 宏实为 sprintf**：server.c:62-64 用 `sprintf` 非 `fprintf`，:351 把迭代号写进数据缓冲本身——debug 模式下兼任 payload 填充，client.c:434-436 打印收到的就是这个串。
6. **角色不对称贯穿收尾**：rdma_reset_device 明文仅 server 可执行（:1011-1014），client 的 DCT 出错由驱动管理——"没有 reset 接口"不是缺失是设计。

——锚均对 HEAD `a99d506` 核实；`../deepwiki/` 23 页可交叉参考。
