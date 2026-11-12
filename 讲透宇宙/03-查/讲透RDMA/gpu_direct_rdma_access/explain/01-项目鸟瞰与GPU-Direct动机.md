# 01 项目鸟瞰与 GPU Direct 动机：绕过主机内存的拷贝路径对比

> 对应 tour 第 1 步「动机：让 RDMA 直接落到 GPU 显存」。源码锚均对 HEAD `a99d506` 核实。

## 一、角色定位

gpu_direct_rdma_access 是 Mellanox 官方的 GPU Direct RDMA 教学样例，全仓仅 14 个文件、4231 行（含两个脚本与 README），干一件事：演示如何用 DC QP（Dynamically Connected QP）把 RDMA Read/Write 直接打到**远端 GPU 显存**。它不是库、不是产品，而是一份"能跑的最小契约"——client 跑在 DGX2 这类 GPU 机器上，server 模拟文件存储后端（README.md:2），server 按客户指令把数据直接 RDMA Write 进 client 的显存缓冲，全程 client CPU 不搬运一个字节。

理解本仓的钥匙是"没有 GPU Direct 时的痛"。传统路径上，server 磁盘数据要进 client GPU，必须走三段：NIC DMA 到 server 主机内存→网络→client NIC DMA 到 client 主机内存→client CPU 发起 cudaMemcpy H2D 再进显存。每一跳都是 PCIe 往返加一次 CPU 主持的搬运，时延叠加、带宽减半、CPU 被占死。GPU Direct 把中间人干掉：数据包从 server NIC 直接 DMA 落进 client 显存——前提有二，一是显存页被 pin 住且映射为 NIC 可 DMA 的物理地址（nv_peer_memory 内核模块，README.md:42），二是两侧使用支持 DC 的 ConnectX-5 及以上网卡（README.md:2）。

## 二、内部结构

仓内角色分工极清晰，README.md:10-17 的 Content 节与实际一一对应：

| 文件 | 角色 | 关键锚 |
|---|---|---|
| gpu_direct_rdma_access.h/.c | RDMA 核心库，对外仅 9 个 API | gpu_direct_rdma_access.h:90-158 |
| gpu_mem_util.h/.c | GPU/CPU 双形态内存分配 | gpu_mem_util.c:232-258 |
| server.c / client.c | 两个 main，只 include 头文件 | client.c:47-49 |
| map_pci_nic_gpu.sh、arp_announce_conf.sh | 主机级拓扑/网络准备脚本 | map_pci_nic_gpu.sh:79 |
| utils.c | 地址解析与带宽结算 | utils.c:66-83 |

值得注意的是**依赖方向的干净**：client.c 与 server.c 各只 include utils.h、gpu_mem_util.h、gpu_direct_rdma_access.h 三个本地头（client.c:47-49、server.c:48-50），核心库 1548 行的 gpu_direct_rdma_access.c 被两个 main 完全当作黑盒使用。库的对外 API 恰好 9 个：open/close/reset 三个设备生命周期、reg/dereg/get_desc_str 三个缓冲操作、submit/poll 两个数据面动作（gpu_direct_rdma_access.h:90-158）。整个系统的形状是"两个薄 main + 一个厚库 + 一层薄显存抽象"。

## 三、外部连接

本仓对外的三大依赖边界都在 README.md:21-50 的 Installation Guide 里：

1. **MLNX_OFED**（README.md:23-29）：verbs 与 mlx5 DV 接口的来源，CQ/PD/QP 全靠它。
2. **CUDA Toolkit**（README.md:30-39）：client 侧选卡、建 context、分配显存（gpu_mem_util.c:164-210）。
3. **nv_peer_memory**（README.md:40-42）：没有它 `ibv_reg_mr` 注册显存必失败——显存页默认不可被 PCIe 外设 DMA，该内核模块负责 pin 页并建立 NIC 可用的映射。

拓扑上还依赖一个隐含契约：**client 选的 GPU 要与所用 HCA 共享同一 PCI bridge**（README.md:6），这样 NIC 与 GPU 之间的 DMA 不穿越 CPU 侧的 PCIe 根复合体，带宽与时延才最优。仓内 map_pci_nic_gpu.sh 就是这个契约的探测工具（详见第 2 篇）。client 与 server 之间则有两条通道：控制面 TCP socket（传缓冲凭据与 ack），数据面 RDMA（DC QP 直写显存）——两条通道严格分离，是全仓最该记住的形状。

## 四、数据流

一次完整迭代的骨架（README.md:4 描述的正是它）：

1. **client 开机三件事**：`main` 入口 client.c:302→`rdma_open_device_client` 建好 DCT 设备（client.c:338）→`work_buffer_alloc` 按 `-u BDF` 选卡分配显存（client.c:347）→`rdma_buffer_reg` 注册拿 rkey（client.c:362）。
2. **凭据上链**：`rdma_buffer_get_desc_str` 把显存地址/rkey/LID/DCTN/GID 序列化成七段冒号串（client.c:370），`rdma_task_attr_flags_get_desc_str` 把任务标志也串化（client.c:371），`pack_payload_data` 按 `|type 1B|size 2B|payload|` 长度前缀格式打包两段（client.c:144-159、:384-394），循环 `write` 发给 server（client.c:417）。
3. **server 直写**：server 收到两段凭据后还原 flags（server.c:337），组 `task_attr.wr_id = cnt`（server.c:348），调 `rdma_submit_task`（server.c:370）——库内解析凭据、建地址句柄、在 DCI 上发 RDMA Write，数据从 server 内存直落 client 显存（执行细节见第 4/5 篇）。
4. **收割与回执**：server 轮询 CQ 直到拿到完成事件（server.c:380），经 TCP 回 "rdma_task completed" ack（server.c:399）；client `recv` 到 ack 进入下一迭代（client.c:425）。全部迭代结束后双方各自 `print_run_time` 结算吞吐（client.c:440、server.c:407，实现在 utils.c:66-83）。

注意数据面里 **client 是靶、server 是弓**：发起 RDMA 动词的是 server，client 只是被动接收——这模拟的正是"存储后端主动推送数据到计算节点显存"的场景。

## 五、设计决策

- **为什么用 DC QP 而不是 RC QP**：存储场景是一对多扇出，RC 需要为每条连接维护一个 QP 状态机；DC 的发起方 DCI 无连接概念、地址随报文携带，目标方一个 DCT 可像 SRQ 一样被任意多发起方共享。client 侧因此只需一份 DCT+SRQ（gpu_direct_rdma_access.c:586-624），server 一条 DCI 打天下（:796-798）。代价是两侧共享硬编码 `DC_KEY 0xffeeddcc`（:68），样例里无所谓，生产必改。
- **为什么控制面走 TCP**：RDMA 凭据（rkey/DCTN/GID）的交换本质上是一次带外信令，TCP 的可靠性把这个握手问题从 RDMA 侧剥离，库的数据面得以只关心 submit/poll。代价是每次迭代一次 socket 往返（client.c:417-425），吞吐测量因此偏向带宽而非纯时延。
- **为什么显存分配放在独立文件**：gpu_mem_util 把 CUDA 依赖隔离进 `#ifdef HAVE_CUDA`（gpu_mem_util.c:51-54、:66-226），server 机器零 CUDA 依赖即可编译，client 不给 `-u` 还能退化成 CPU 基准对照——一套代码三种形态，这是样例工程的自觉。
- **为什么 64KB 对齐**：显存按 64KB 向上取整分配（gpu_mem_util.c:158-162），与 nv_peer_memory 的 pin 粒度对齐，避免跨页注册的碎片成本（详见第 3 篇）。

## 六、新人提示

1. **先读 README.md:2-6 再读代码**：三段话讲清角色、流程、拓扑要求，后面所有代码都是它的展开。
2. **别从 gpu_direct_rdma_access.c 顺读**：1548 行会淹死新人。建议路径：本篇→第 2 篇跑起来→第 4 篇看 API 契约→两个 main 各顺一遍（client.c:302-466、server.c:239-427）→最后回攻核心库三个半场。
3. **client.c:434-436 的"打印收到的数据"只在 CPU 模式生效**：`if (!usr_par.use_cuda)` 守住了对显存指针的 sprintf——显存不能直接解引用，这是 CUDA 新手最常见的崩溃点，仓里用一句 if 防住了。
4. **测出的 Mbit/sec 不是网卡极限**：每迭代夹着一次 TCP ack 往返（client.c:425），且 server 侧 SDEBUG_LOG_FAST_PATH 在 debug 模式下会往数据缓冲本身写串（server.c:351，该宏实为 sprintf，见 server.c:64），带宽数字仅供纵向对比。
5. **调试开关有两档**：`-D` 位 0 是 debug（慢速诊断信息），位 1 是 debug_fast_path（数据路径打点，见 client.c:202-203 的 usage 文案）；深挖第 4/5 篇时开 fast_path 才能看到每笔 RDMA 的 rkey/DCTN。
