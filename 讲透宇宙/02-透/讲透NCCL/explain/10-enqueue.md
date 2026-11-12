# 10 · enqueue：任务入队与 kernel plan（enqueue.cc）

## ① 角色定位

`src/enqueue/enqueue.cc`（3601 行）是 collective API 与 GPU 执行之间的编译器：把 group 里的调用翻译成可执行 kernel plan，链条"调用→taskAppend 分派→聚合→channel/algorithm 切分→launch 参数装配→proxy op 生成"。入口是 `ncclEnqueueCheck`（`enqueue.cc:3478`），产出设备侧 work 结构、一次 cuLaunchKernelEx、给 proxy 的 ncclProxyOp 队列。`task_prep/`（预调优）与 `task_sched/`（p2p/CE/RMA 调度器）是子模块。

## ② 内部结构

**第一路：taskAppend 四路分派（`enqueue.cc:3337-3476`）**：group 内每个 collective 的判断树——`NCCL_ENQUEUE_REARCH_ENABLE` 走 rawTaskAppend 实验路径（`3341-3342`）；Send/Recv 走 p2pTaskAppend（`3343-3345`）；Put/Signal/WaitSignal 走 rmaTaskAppend（`3346-3347`）；其余走主路：count==0 丢弃（`3350`），FP8 归约要求 sm90+（`3360-3366`），单 rank 走 ncclLaunchOneRank（`3373-3377`），AllToAll/Gather/Scatter 降级为成对 p2p（`3414-3459`），再按 CTA policy 与对称内存路由到 CE（`3398-3400`）或 collTaskAppend（`2757-2851`）。

**任务对象化**：collTaskAppend 生成 `ncclTaskColl`，NCCL_CONFIG_SET 宏按 env>per-call>comm 解析 minCTAs/maxCTAs/nvlsCTAs/cgaClusterSize（`enqueue.cc:2825-2836`），按 trafficBytes 插入 collSorter（`2847`）；无配置 Broadcast 升级为批量 AllGatherV（`2774-2798`）。p2pTaskAppend 生成 `ncclTaskP2p` 挂 peers 队列并做首见 peer 预连接（`2701-2740`）。

**第二路：算法与 chunk**。group 结束后 `ncclGetAlgoInfo`（`enqueue.cc:2159-2226`）组 tuning 输入调 `ncclTuningCompute` 选出 algorithm/protocol/nWarps/maxChannels（`2214-2220`），支持 per-call algSelection 与 tuner 回退。`calcCollChunking`（`2228-2530`）按 func×algo 定 pattern（AllReduce+RING→RingTwice，`2253-2259`），从协议 buffer 大小推 chunkSize（LL 减半、LL128 按 120/128 折算，`2272-2273`），再按 NVLS/CollNet/PAT 特调，最后填 proxyOp 的 nsteps/chunkSteps/sliceSize/loopSize（`2417-2441`）。

**第三路：plan 装配**。`ncclLaunchPrepare`（`enqueue.cc:1695-1867`）循环取 plan 直到任务耗尽，顺序 coll→bcast→p2p——注释明言必须先排空 coll，否则各 rank 切 kernel 位置不一致会死锁（`1740-1744`）。`scheduleCollTasksToPlan`（`644-947`）按 kernel args 预算估算装几个 coll（`654-689`），以 32KB 最小流量为粒度算 cells，产出 countLo/Mid/Hi 与 channelLo/Hi（`742-799`），每 channel 一个 work batch 加一个 proxyOp（`845-894`）。`ncclAddWorkBatchToPlan`（`153-234`）管 batch 合并：workType/funcId 不同、P2P 超上限、同 round 重复都开新 batch，offsetBitset 用 64 位位图标槽位（`225`）。`finishPlan`（`236-330`）把 batch 按 channel 轮转铺进 kernel args、work 塞得下就用 args 否则落 fifo（`245-247`），并把各 channel proxyOp 按 opCount 归并成全局队列（`282-329`）。

**第四路：upload 与 launch**。`uploadWork`（`enqueue.cc:1365-1492`）支持三种 work 存储：Args（随参数直传）、Fifo（环形缓冲 `waitWorkFifoAvailable` 等设备消费 `1333-1349`，GDR 写后 `wc_store_fence` `1435`）、Persistent（graph 捕获专用 cudaMallocAsync buffer `1454`）。`ncclLaunchKernel`（`1886-2012`）以 channelMask 位数作 grid.x（`1889-1891`），args 经 CU_LAUNCH_PARAM_BUFFER_POINTER 直传（`1902-1903`），sm90+ 挂 CGA cluster、mem-sync domain、launch completion event（`1919-1969`），最终 `cuLaunchKernelEx`（`1992`）。`uploadProxyOps`（`1514-1556`）把 plan 内 opCount 平移到 comm 全局序列供 proxy 排序。

## ③ 外部连接

- 上游 `src/init.cc` API 层经 `ncclEnqueueCheck` 进入；group 语义由 GroupStart/EndInternal 包裹（`enqueue.cc:3491,3519`），depth==1 才触发 plan。
- 算法决策下沉 `src/graph/tuning.cc` 与 tuner 插件；chunk 参数回读 `comm->buffSizes`。
- 设备侧：kernel 入口表由 `src/device/generate.py` 生成（`enqueue.cc:905` 的 `ncclDevKernelForFunc[devFuncId]`）；work 结构契约在 `src/include/device.h`。
- proxy 侧：`ncclAddProxyOpIfNeeded`（`enqueue.cc:140-149`）先 justInquire 探测是否需要代理（纯 NVLink/SHM 通道不需要），需要才复制进 plan，由 `src/proxy.cc` 消费；CUDA Graph 捕获时 work 转 Persistent、host 回调挂 hostStream、plan 引用计数由 persistentDestructor 回收（`enqueue.cc:1858-1863`）。

## ④ 数据流

以一次 group 内 AllReduce 为例：

1. **入队**：ncclEnqueueCheck→ArgsCheck 校验（`enqueue.cc:3503`）→taskAppend→collTaskAppend 生成 ncclTaskColl 入 collSorter。
2. **group end**：ncclLaunchPrepare 循环建 plan；ncclGetAlgoInfo 定 algo/proto；calcCollChunking 定 chunk 与 proxyOp 骨架。
3. **channel 切分**：scheduleCollTasksToPlan 把 count 切 Lo/Mid/Hi 映射 channel 区间，写 ncclDevWorkColl（`enqueue.cc:796-826`）；funcId 决定特化 kernel（`904-907`）。
4. **上传发射**：uploadWork 写 work（`enqueue.cc:1869-1879`）→ncclLaunchKernel 调 cuLaunchKernelEx→hostStreamPlanTask 在 host 回调里 uploadProxyOps 并 ncclProxyStart 唤醒代理（`1558-1577`）；走 host func 是为 graph replay 可重放（`1831-1856`）。
5. **收尾**：reclaimer 回收任务内存（`1589-1633`）；KernelFinishCallback 处理事件与错误（`2024-2036`）。

## ⑤ 设计决策

- **plan 是调度与发射的原子单位**：跨 plan 不合并 batch、p2p 以 epoch 隔离防死锁（`enqueue.cc:1700-1704`）；预算模型（`enqueue.cc:338-349`）让一个 kernel 尽量多吃任务摊薄 launch 开销，超了再切 plan。
- **per-call 配置隔离**：带 algSelection/CTA 覆盖的 coll 设 aggIsolate 独占 plan（`enqueue.cc:665-666`），避免共享 channel 预算被稀释。
- **三种 work 存储**：优先塞 kernel args 免一次设备读；fifo 服务长流水；persistent 供 graph 捕获保证重放幂等。
- **opCount 编码顺序语义**：coll 用偶数（<<1|0）、p2p 用奇数 id，proxy 端按位旋转排序保证 coll 先于 p2p（`enqueue.cc:1516-1542`）。
- **launch 属性面向新硬件**：CGA cluster 要求 grid 可整除否则退化（`enqueue.cc:1930-1931`）；sm90 默认 Remote mem-sync domain（`1938-1942`）。

## ⑥ 新人提示

1. 调性能先看 rank0 的 NCCL_TUNING 日志：`enqueue.cc:912-914` 打印"Bytes→Algo/proto/channel{Lo..Hi}/cgaClusterSize"，一眼看出算法与通道选择是否符合预期。
2. 先抓三个队列：planner 的 collTaskQueue/collWorkQueue/planQueue；finishPlan 后 work 队列顺序与 channelMask 一致是关键不变量。
3. CUDA 11.2-11.4 的 sm80 有 TREE 用 runTreeUpDown 的 workaround（`enqueue.cc:239-243`），别当成通用路径。
4. group 语义坑：taskAppend 里 nRanks==1 走 OneRank、count==0 被丢弃——群里"空操作"不产生 plan，排障时别找 kernel。
5. 追一个 collective 落点：从 devFuncId 反查 generate.py 特化表，再进 `src/device/all_reduce.h` 看 RunWorkColl；enqueue 只装参数不算数据。
