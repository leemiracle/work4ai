# 12 · device kernel：GPU 侧集合通信（all_reduce.h + primitives 框架）

## ① 角色定位

`src/device/` 是集合通信的 GPU 侧：真正搬数据与做归约的 CUDA kernel。与直觉相反，**kernel 主体全在 .h 头文件**——`all_reduce.h`（788 行）等按 collective 组织算法模板，`common.cu` 只有 32 行入口壳：声明 `__shared__ ncclShmem`（`common.cu:14`）、定义通用入口 `ncclDevKernel_Generic`（`23-25`）。特化 kernel 由 `generate.py` 枚举 7 coll×5 redop×12 dtype×3 proto×7 algo 生成（`generate.py:13-16`），经 `DEFINE_ncclDevKernel` 宏（`common.h:506-509`）实例化 ncclKernelMain。本篇以 all_reduce.h 为主线讲 CTA 切块、三种协议与归约框架。

## ② 内部结构

**入口分发（ncclKernelMain，`common.h:420-501`）**。block 启动后：args 拷进 shmem（`common.h:426-428`）；channelMask 的 popcl 把 blockIdx.x 映射成 channelId（`434-437`）；warp0 载 ncclKernelComm、warp1 载本 channel 数据、其余 warp 经 `loadWorkBatchToShmem`（`common.h:142`）按 offsetBitset 位图取 work——求 n'th set bit 用 shmem 而非 PTX fns，因 fns 展开太慢（`147-152` 注释）。循环体：funcId 命中编译期特化就直接调 RunWorkBatch，否则查 `ncclDevFuncTable`（`481-487`）；nextBatchIx 链式加载后续 batch（`489-497`）。

**CTA/warp 切块（RunWorkBatch，`common.h:302-336`）**。一个 CTA=一个 channel；batch 内多 work 顺序执行，每个 work 只用 `nWarps*WARP_SIZE` 线程——`if (tid < subtn) RunWorkColl<...>().run(...)`（`329-333`），nWarps 不同补 `__syncthreads()`（`324-328`）。warp 数由 tuning 决定。

**算法层（all_reduce.h）**。匿名 namespace 提供 `runRing`（`14-83`）、`runTreeUpDown`（`86-143`）、`runTreeSplit`（`146-225`）：Ring 用 2(n-1) 步 reduce-scatter+allgather，第 n-1 步在自己 chunk 上 `directRecvReduceCopyDirectSend(postOp=true)` 落最终结果（`60-64`）；TreeSplit 把线程分给 reduce-up 与 broadcast-down（LL/LL128 下 7:3，`155-163`）。文件尾注册 10 个 RunWorkColl 特化：六算法×SIMPLE 加 RING/TREE×LL/LL128（`229-788`）。NVLS/CollNet 按角色分 warp 组而非按 channel 均分（`396-408`）。TREE+SIMPLE 有 CUDA 11.2-11.4 的 workaround（`239-243`）。

**Primitives 框架（primitives.h）**。`Primitives<T,RedOp,Fan,Direct,Proto,P2p>` 按协议特化为三个实现（`primitives.h:116-117` 声明，`166-168` include）。协议类是模板参数而非枚举：ProtoSimple 携带 SlicePerChunk/StepPerSlice/Unroll 等编译期常量（`25-45`），ProtoLL/LL128 只带 Id 与步长计算（`47-75`）；Fan 类静态编码收发扇出上界（`83-113`）。LL/LL128 无 direct 路径，`PrimitivesWithoutDirect` 适配器把 directSend 降级为普通 send/recv、`directRecvDirectSend` 为空操作（`121-152`）。

**三种协议实现**：
- **prims_simple.h**：数据经 channel 固定 buffer 中转，`genericOp`（`prims_simple.h:178-304`）按 slice 循环 waitPeer→subBarrier→reduceCopy→barrier→postPeer；reduceCopy 是多源多汇归约拷贝引擎（`241-277`）。带宽高但同步粒度大。
- **prims_ll.h**：每 16 字节一行 `ncclLLFifoLine`——8 字节数据+两侧 4 字节 flag（`device.h:77-88`，flag 在数据后，防网络先收 flag 后收数据）。`storeLL` 一条 v4.u32 原子写 data+flag（`154-158`）；`readLL` 自旋等两 flag 相等（`108-122`）；步进 flag 环绕计数、CLEAN_MASK 周期清零（`device.h:103-111`）。带宽减半（flag 占 50%）但延迟极低。
- **prims_ll128.h**：128 字节 line=120 数据+8 flag（`device.h:113-115`），flag 由每 warp 第 31 线程持有（`prims_ll128.h:10`）；数据用 `load128/store128` 16 字节向量访存（`op128.h:13-27`）；sm90 起 postSend 前 `__threadfence_system`（`88-95`）。带宽 ~94% 且延迟低，但受时钟漂移影响，由 tuner 启用。

**归约框架（reduce_kernel.h）**。**勘误：旧资料的 `reduceScatterChunk` 在 v2.32.3 已不存在**（本仓 grep 无此符号），现行是类型泛化 pack 框架：`FuncSum/FuncProd/FuncMinMax/FuncPreMulSum/FuncSumPostDiv` 定义单元素语义（`reduce_kernel.h:44-77,874-936`），`Apply_Reduce::reduce` 按 BytePack 宽度生成向量化归约（`310-446`），入口 `applyReduce/applyPreOp/applyPostOp`（`198-212`）；preOp/postOp 实现 Avg（网络只见 Sum）与 PreMulSum 标量注入；FP8/bf16 有特化（`874-1085`）。

## ③ 外部连接

- 上游 enqueue：work 的 channelLo/Hi、cbd.countLo/Mid/Hi、chunkGrains 由 enqueue 写入，kernel 用 `ncclCollCbdPart` 反解本 channel 的数据段（`all_reduce.h:21-22`）。
- 连接数据：`ncclShmem.channel.peers[peer]` 的 head/tail/step 指针与 direct buffer 地址由 p2p/net 传输层在 connect 阶段写入，prims 构造时读入寄存器。
- 同步对端：SIMPLE 跨 GPU 走对端 tail/head 指针；net 侧对端是 proxy 线程（第 11 篇），IB 层对协议无感知、只保证 128 字节对齐搬运（第 09 篇）。
- abort：所有自旋等待调 `checkAbort`（`primitives.h:154-164`），每 10000 次自旋查一次 abortFlag。

## ④ 数据流

以 RING+SIMPLE 单 channel 单 work 为例：

1. **入**：ncclKernelMain 映射 channelId→载 channel→RunWorkBatch 取 work→`ncclCollCbdPart` 得本 channel 数据段。
2. **构造**：Primitives ctor 读 ring->prev/next 的 connInfo，缓存 buff 指针与 head/tail（`prims_simple.h:614-700`）。
3. **2(n-1) 步循环**：前 n-1 步 `directRecvReduceDirectSend`（`all_reduce.h:50-56`）——从 prev 收、与本地 reduce、发往 next；第 n-1 步在自己 chunk 上落最终结果（`60-64`）；后 n-1 步纯 `directRecvCopyDirectSend` 分发。每步内部 genericOp：waitPeer（等对端 tail）→reduceCopy（srcs[0]==dsts[0] 时直读写用户 buffer 免中转，`prims_simple.h:241-251`）→postPeer。
4. **出**：work 完成，workCounter 累加，profiler 记时间戳（`common.h:377-417`），nextBatchIx 有值则加载下一 batch。

## ⑤ 设计决策

- **头文件即 kernel**：算法模板须对 T/RedOp/Proto/Fan 全特化才能内联成无分支直线代码，放 .h 由 generate.py 展开成数千入口；代价是产物巨大，可 regex 裁剪（`generate.py:33-43`）。
- **协议三分**：SIMPLE 求带宽（大消息）、LL 求最低延迟（小消息）、LL128 折中；tuner 按大小选择，算法模板只认 Proto 统一接口。
- **direct 通路双刃**：SIMPLE 的 Direct=1 让接收端直写用户 buffer 省一次拷贝；LL/LL128 无 direct，数据必须落协议 buffer 编 flag；适配器让算法层无感切换。
- **双入口兜底**：编译期特化省函数表跳转，`ncclDevKernel_Generic`（`common.cu:23`）兜底任何 funcId。
- **flag/数据原子性**：LL 的 flag 在数据后（`device.h:78-81`）依赖"IB RDMA 8 字节原子写或 socket 连续到达"；LL128 依赖 16 字节原子访存——跨 GPU/网络同步正确性的基石。
- **进度对账**：progressCounters 用 slot 位图+原子加记录每 channel 完成 work 数（`common.h:342-375`）。

## ⑥ 新人提示

1. 别在 common.cu 找算法——它只是 32 行壳；读 `generate.py:13-16` 枚举表即知一个 allreduce f32 ring simple kernel 的真名。
2. 调协议看 `NCCL_PROTO=Simple/LL/LL128` 强制后的行为差异；理解三者优劣先看 `primitives.h:36-74` 的 calcBytePerStep（LL 直接除 2）。
3. warp 数是调优参数：work->nWarps 由 tuning 决定；改算法先确认对 nthreads 的假设。
4. 旧版符号（reduceScatterChunk 等）在本版已重构，查资料须对齐 v2.32 源码；归约语义从 applyReduce 读下去最顺。
5. NCCL_DEBUG=TRACE 不进 device，kernel 内行为用 nsys 配 profiler 时间戳看。hang 先判协议——LL 卡 flag、SIMPLE 卡 tail。
