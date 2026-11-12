# 03 · 通信线：NCCL 与集合通信

> 系列第 03 篇：**多 GPU 必然要通信，代价怎么压到最小**。原料 nccl v2.32.3-1/nvshmem/nvbandwidth/nccl-tests/gdrcopy；站在《讲透NCCL》（12 explain+10 勘误+infra-quant）之上。行号锚 2026-11-04 于 `/usr-data/data2/repos/agent-repos/NVIDIA/` 核实。

## 一、第一性原理设问：数据并行为什么逃不掉 all-reduce

数据并行契约：N 卡各持完整副本、各算各的梯度；要让下一步参数一致，N 份梯度必须归约成一份且人人可见。把"信息必须流动"定量化（每卡 M 字节）：ReduceScatter 阶段每卡有 (N−1)/N·M 依赖他人、必须到达；AllGather 阶段其余分片的归约结果也要到达——合计**每卡收发下界 = 2(N−1)/N·M**，渐近 2M、与卡数无关。朴素 gather+broadcast 的 root 收 (N−1)·M、发 N·M 随 N 爆炸；ring 把每条链路流量摊到恰好下界。

通信线因此是四层逼近：算法（ring 逼近 2(N−1)/N·M，逐 bit 无冗余）→ 协议（LL/LL128/Simple 换档逼近链路带宽）→ 拓扑（PATH 阶梯 × channel 让每条链路干活）→ 系统（单边+对称内存把通信藏进计算）；时间上 T = α·steps + bytes/B，ring 串行 2(N−1) 步、树 2·log₂N 步——带宽 vs 延迟贯穿全篇。

## 二、直觉层：环是流水线，树是广播塔，协议是快递档位

**ring = 环形流水线**：N 个厨师围圈传菜，前 N−1 轮边传边叠味（reduce-scatter）、后 N−1 轮转圈补齐（all-gather）；任何时刻每对手臂都在传（链路满载 = 带宽最优），但一道菜要摸过 2(N−1) 双手（延迟 O(N)）。**tree = 广播塔**：水波向上汇聚再向下广播，log₂N 跳起步快；但塔顶电梯（近 root 链路）搬运多份拷贝，大流量先挤爆（带宽打折）。

**协议三档 = 快递档位**：Simple = 整车集装箱——满载高吞吐，但要装满才发车、整批对账（chunk 同步）；LL = 每 8B 货附 4B 签收单——到件即取，单据吃 1/3 带宽；LL128 = 128B 托盘——15/16 载荷率，又快又能装，但对路况（PCIe 拓扑）挑剔。

**NVSHMEM = 去中心化**：集合通信是全员定时集会（所有 rank 的 CPU 同时到场按同一议程发言）；MoE dispatch 是动态稀疏逐 token 路由，议程排不出来。NVSHMEM 发全员通讯录（对称堆同虚地址），GPU 线程在 kernel 里直接往远端工位放东西（单边 put）——零 CPU、零集体同步。

## 三、机制层：公式怎么变成代码

### 3.1 环代数与分层树

轮次硬编码于 `nccl/src/tuning/tuning_general.cc:15-23`：AllReduce = 2×(nRanks−1)、ReduceScatter/AllGather = nRanks−1。环带宽模型（`nccl/src/tuning/ring.cc:37-46`）：busBw = bw×nChannels，折扣后换算 generalBandwidths = busBw×nRanks/nSteps——移项即 **busbw = algbw×2(N−1)/N**，与 nccl-tests 验收公式同构。跨机分层环：`ring.cc:84` nInterSteps = 2×(nNodes−1)，跨机/机内步分别吃 inter/intra 延迟；SIMPLE 另付 interLat×2 + netOverhead×3（`ring.cc:63,81`）。树是机内扁平+机间 log₂ 分层树（`nccl/src/tuning/tree.cc:57`）。交叉点由 2(N−1)α_r + 2M/B_r = 2log₂N·α_t + 4M/B_t 决定，H100 单机 8 卡实测 ≈680–691 KB——**成本模型是公式+拟合系数的混合物**。

### 3.2 协议三档：折扣、封顶、拓扑耦合

设备侧常量（`nccl/src/include/device.h`）：NCCL_STEPS=8（:26 在途窗口）、LL flag 轮转（:104）、LL128 行 128B = 16×8B 含 15 载荷、每线程 120 元素（:113-118）。工程折扣（`ring.cc:38-42`）：LL 取 min(llMaxBw, busBw×0.5)——理论 2/3、实测对折（每 8B 一次 flag 读-判-写依赖链）；LL128 取 min(busBw×0.92, nChannels×perCh 封顶)，**Hopper 每 channel 36.7 GB/s 封顶**（8ch 仅 294 → 大消息必切 SIMPLE）。拓扑耦合（`cost_model.cc:119-139`）：128B 整行写要求原子可见，Hopper 及以前 LL128 只许到 PATH_PXB，Blackwell/Rubin+驱动 ≥13030 才放开 PXN/P2C（参数 :117）。选型：对每 (algo, proto) 算 timeUs = lat + size/bw（`ring.cc:138`）取最小（管线 `tuning.cc:180-234`；延迟全表 `cost_model.cc:145-184`），NCCL_ALGO/NCCL_PROTO 可缩候选。

### 3.3 channel 与拓扑：PATH 阶梯决定一切

启动扫 sysfs 建 XML 图，为每对 GPU/NIC 算路径类型——`nccl/src/include/graph.h:121-151` 的 PATH 阶梯从 LOC、NVL 到 PHB、SYS、NET 共 11 档，越后越贵。路径决定可用协议（LL128 限制）、环/树走向与 channel 数（`src/graph/search.cc` 饱和搜索）。**channel = 独立流水线**：自有三协议 buffer 与专属 GPU thread block；单 channel 受封顶与 SM 排程限制，多 channel 并行才填满带宽。跨 PCIe 慢两条物理原因：PIX/PXB 带宽低一个量级；Intel CPU 把 GPU P2P 翻成 64B TLP 多吃 20%（`nccl/src/graph/topo.h:44`）。捷径两条：**NVLS** 让 NVSwitch 在交换芯片内归约（`nccl/src/transport/nvls.cc:8,57`）；**CUDA Graph** 让集合可整图重放，channel 计划 capture 时注册（`nccl/src/enqueue/enqueue.cc:332`）。

### 3.4 NVSHMEM：单边通信为什么必须存在

集合通信两条枷锁：全员同步（CPU 逐 rank launch）+ 固定等量布局；MoE dispatch 是 token 级动态稀疏路由、目的地运行时才知道——NCCL all-to-all 装不下，DeepEP 因此以 NVSHMEM 为底座。两个原语：**对称堆**——`nvshmem_malloc`（`nvshmem/src/host/mem/mem_heap.cpp:2289`）在所有 PE 分配同虚地址堆（PGAS 根基）；**设备端单边 put**——`nvshmem/src/include/device/nvshmem_defines.h:95-99` 是 `__device__` 内联，GPU 线程 kernel 内直接发起远程写。put 为 fire-and-forget（收口 quiet/fence，通知 put_signal）。传输双路：有 RDMA 设备直 post IB verb（零 CPU），无则退化 proxy 由 CPU 从共享 command buffer 代发（`nvshmem/src/host/proxy/proxy.cpp:47-50`）。DeepGEMM MegaMoE 的 dispatch+GEMM+combine 融合 kernel 正靠此；NCCL 也在吸收：`nccl/src/sym_kernels.cc:36` 起 symmetric kernel 族，GB300 NVL64 对称 AR 实测 992 GB/s。

### 3.5 观测与旁路

**nvbandwidth** 分测同一链路两种发起：CE（copy engine DMA）vs SM（kernel 写）——`nvbandwidth/testcases.cpp:160-161`、kernel 在 `kernels.cu:56,64`；差值暴露 SM 排程瓶颈（CE 实测 +3pp）。**gdrcopy** 把显存映射进 CPU 用户态（bar1），小消息 0.1–0.2 µs vs cudaMemcpy 6–7 µs（NCCL 绑定 `src/misc/gdrwrap.cc`）。**GPUDirect RDMA**：NIC 直 DMA 显存；`net_ib/gdr.cc` 探测 peermem 非 GDRCopy 本体（《讲透NCCL》勘误 #4）。

## 四、程序员实操：三层漏斗

**第 1 层 nvbandwidth 体检物理链路**（装机/变更后）：`./nvbandwidth -t 10_11_12_13 -b 0.5G` 与 CE 口径分别记录；低于 NVLink 标称先查 `nvidia-smi topo -m`。

**第 2 层 nccl-tests 验收**：**看 busbw 别看 algbw**——源码实证 `nccl-tests/src/all_reduce.cu:59-64`：factor = 2(nranks−1)/nranks，busBw = baseBw×factor。`./build/all_reduce_perf -b 8 -e 8G -f 2 -g 8 -w 20`；判读（官方 v2.32.3 表）：H100 NVL8 AR 大消息 ≈484 GB/s（超 450 单向 = 双向通道，正常）、AG/RS ≈360–378（已知缺口）；低于 200 先怀疑拓扑降级。

**第 3 层运行时调优**：`NCCL_DEBUG=INFO NCCL_DEBUG_SUBSYS=INIT,TUNING,GRAPH` 看 via 行与 channel 数。常用：NCCL_ALGO/NCCL_PROTO、NCCL_MIN/MAX_NCHANNELS、NCCL_NTHREADS/NCCL_LL128_NTHREADS（`tuning_general.cc:12-13`）、NCCL_LL128_C2C、NCCL_BUFFSIZE；conf 优先级 env>NCCL_CONF_FILE>~/.nccl.conf。

**高频坑**：① 跨 PCIe 慢一个量级 = ring 穿 PHB/SYS、channel 被砍；② 大消息 channel 不满 = MAX_NCHANNELS 被压或注册失败，两 rank channel 数对不上 = 一侧走错传输；③ 容器 sysfs 裁剪致拓扑探测退化；④ IB 无 peermem → host 双跳，busbw 掉 2/3；⑤ CUDA Graph 先 warmup 再 capture。

## 五、批判边界

1. **成本模型是拟合产物**：0.5/0.92/36.7 全是特定硬件+驱动的标定值。铁证：Blackwell 树×LL128 带宽 55.6 GB/s/ch 反超环的 40.0（`cost_model.cc:198,205`）——升级后重跑 nccl-tests。
2. **环延迟 O(N) 不可救药**：千卡小消息靠树/CollNet/PAT 兜延迟；算法空间是延迟-带宽平面的多点布防，无全能点。
3. **AG/RS 的 81% 天花板**：链路模型算不到 SM 执行与 chunk 协调；CE 路径与 symmetric kernel 是绕缺口的手段。
4. **集合语义的天花板**：动态稀疏通信超出 all-to-all 表达力——DeepSeek EP 通信用 DeepEP（NVSHMEM）而非 NCCL，两线互补非替代。
5. **同步陷阱**：NCCL 同 communicator 集合串行化；NVSHMEM put 后不 quiet/fence 就读 = 数据竞争。
6. **busbw ≠ 链路带宽**：链路层口径用 nvbandwidth。

## 六、费曼检验

1. **为什么 ring AR 的 busbw 能超单向链路带宽（484 > 450 GB/s），朴素算法不能？** busbw 是等效归约口径 = algbw×2(N−1)/N；环上每卡同时用上下行 channel 注入（NVSwitch 全双工，割集 2×450），每卡收发恰为下界 2(N−1)/N·M；朴素算法 root 链路先饱和。
2. **LL128 为什么在 Hopper 被限在 PATH_PXB 以内，Blackwell+新驱动才放开 PXN？** LL128 依赖 128B 整行写的原子可见性；跨 PCIe 域/C2C 无硬件保证，Blackwell 起驱动给出保证才放开（见 3.2 锚）。
3. **DeepEP 为什么不用 NCCL 的 all-to-all 而要 NVSHMEM？** MoE dispatch 是 token 级动态稀疏路由：要 GPU 线程 kernel 内逐目的地发起（`nvshmem_defines.h:95-99`）+ 对称堆寻址（`mem_heap.cpp:2289`）+ 零 CPU 介入；NCCL all-to-all 是静态等量布局+全员同步，前提皆不成立。

**一句话总结**：通信线的全部戏码，是把 2(N−1)/N·M 这个信息论下界逐层逼近到硅——算法层用环摊匀链路、协议层 LL/LL128/Simple 换档、拓扑层 PATH 阶梯把通路编入 channel、系统层单边对称内存让通信溶解进 kernel；NCCL 与 NVSHMEM 分守"同步集合"与"动态单边"两个半场。

---

## 勘误（旧文/deepwiki/常见认知 vs 本仓源码）

1. **LL128 效率"94%"为讹传**：行载荷 15/16 = 0.9375（`device.h:113-115`），工程实取 0.92 且**按 channel 封顶**（`ring.cc:41-42` 注释 120.0/128.0 即 15/16 每线程口径，`device.h:118` 呼应）——漏封顶解释不了切 SIMPLE。
2. **《讲透NCCL》infra-quant 引的 `cost_model.cc:470` 行号已漂移**：锚基于 kylin clone（3e46c089），本仓（12df1a1）重构后在 `ring.cc:138`（声明 `cost_model.h:70`），公式未变；本篇锚全按本仓重核。
3. **"NCCL 用二项树"不准确**：实为机内扁平+机间 log₂ 分层树（`tree.cc:57`）。
4. 《讲透NCCL》10 条勘误继续有效不重复（占位符风格 / param 双轨 / pnccl 别名 / gdr.cc=peermem / reduceScatterChunk 不存在 / kernel 主体在 device/*.h / bootstrap 婚介所）。
