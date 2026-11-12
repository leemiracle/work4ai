# 06 · 调优代价模型：src/tuning/tuning.cc 与 src/include/tuning.h

## 一、角色定位

拓扑搜索决定"通道怎么排"，调优子系统决定**每次集合通信调用选哪个 algorithm/protocol/kernel 变体**。`src/tuning/tuning.cc`（343 行）是这个决策的编排层：把所有候选编进一个**统一 ID 空间**，逐个用内部 cost model 仿真耗时，允许外部 tuner 插件改写耗时表，最后取最小者。`src/include/tuning.h`（110 行）定义全部数据结构与 ID 布局。邻居分工：`cost_model.cc` 提供 per-algo 解析模型（ring/tree/collnet/nvls/pat/symk/ce 的 Sim 函数），`tuning_general.cc` 提供线程/通道数计算，本文件只做"遍历-仿真-选优-善后"。`ncclTuningCompute` 在每次集合调用规划时触发（enqueue.cc:2192、task_prep.cc:24），初始化 `ncclTuningInit` 由 init.cc:1899 调用。

## 二、内部结构

### 1. 统一 ID 空间（tuning.h 的骨架）

tuning.h:17-25 定义三段式 ID 布局：`[0, NCCL_NUM_ALGORITHMS×NCCL_NUM_PROTOCOLS)` 是常规 algo×proto 组合；`NCCL_TUNING_SYM_KERNEL_ID_OFFSET` 起是对称内核（`AllReduce_AGxLL_R`、`AllGather_TmaST` 等）；`NCCL_TUNING_CE_METHOD_ID_OFFSET` 起是 CE（copy engine）方法；配套 `NCCL_TUNING_MASK_GENERAL_KERNELS/SYM_KERNELS/CE/ALL` 四个 bitmask（tuning.h:21-25）。这让"候选集"变成 uint64 位图（`tuningMask`，tuning.h:59），上层可任意裁剪候选，模型层只按位遍历。`ncclTuningExpandId`（tuning_general.cc:204）负责反解：常规段 `algo=id/NUM_PROTOCOLS, proto=id%NUM_PROTOCOLS`（tuning_general.cc:216-217），后两段减各自 OFFSET。

### 2. 三个关键结构

`ncclTuningInput_t`（tuning.h:57-79）是单次调用上下文：tuningMask、func/redOp/datatype/nBytes/numPipeOps（流水线深度）、winRegType/regBuff（buffer 注册状态）、collNetSupport/nvlsSupport、captured（graph capture 中）、CTA 限额。`ncclTuningResult_t`（tuning.h:42-55）是仿真输出：timeUs、selectionTimeUs、algo/proto/symKernelId/ceMethodId、nChannels/maxChannels/nWarps、forced（环境变量强制位）。`ncclTuningContext_t`（tuning.h:81-95）挂在 comm 上：`forced[]`、`enabled[NCCL_TUNING_COUNT][NCCL_NUM_FUNCTIONS]`（模型×collective 启停矩阵）、latency/bandwidth 缓存、threadThresholds/maxThreads。

### 3. 初始化：ncclTuningInit（tuning.cc:44）

顺序严格：`ncclTuningCostModelPreInit`（tuning.cc:47，填默认常量）→ `ncclTunerPluginLoad`（tuning.cc:49，dlopen `NCCL_TUNER_PLUGIN`）→ 插件 `tuner->init`（tuning.cc:51）→ `ncclTuningCostModelInit`（tuning.cc:56，逐模型 init，失败即禁用）→ `ncclTuningSetThreadThresholds`（tuning.cc:57）。rank 0 随后打印 algorithm×protocol 的 latency/bandwidth 大表（tuning.cc:59-102，`NCCL_DEBUG=INFO,SUBSYS=TUNING` 可见）。

### 4. 主入口：ncclTuningCompute（tuning.cc:180）

流程四步：

1. **单 rank 直通**：nRanks≤1 直接给 Ring/Simple、零通道（tuning.cc:192-200）。
2. **全量仿真**：`ncclTuningComputeAllTunings`（tuning.cc:128）遍历 `NCCL_TUNING_COUNT`，tuningMask 位过滤（tuning.cc:137）→ ExpandId → `ncclTuningComputeTuning`（tuning.cc:339）→ `ncclTuningCostModelSimModel`（cost_model.cc:470）：查 modelMap 拿模型函数、查 `enabled[id][func]`（cost_model.cc:478），timeUs≤0 视为无效，统一置 `NCCL_TUNING_IGNORE`+valid=0（cost_model.cc:483-486）。
3. **插件改写**：comm->tuner 非空时，把仿真结果折进 `generalTable[algo][proto]`（初值全 NCCL_TUNING_IGNORE，tuning.cc:204-216），调 `tuner->getCollInfo` 改写耗时并给 nMaxChannels（tuning.cc:219-229）。**插件只能改耗时与通道上限，不能新增候选**——这就是内部模型与外部插件的边界。
4. **选优与后处理**：`ncclTuningSelectBestTuning`（tuning.cc:155）按 selectionTimeUs（缺省退化为 timeUs，tuning.cc:162）取最小；`ncclTuningGetChannels`（tuning.cc:234）算通道/线程数。两个特殊补丁：`NCCL_CTA_POLICY_EFFICIENCY` 且 buffer 已注册时偏向 NVLS/Simple（tuning.cc:240-257，插件在场则跳过）；sym kernel 回退（tuning.cc:258-298）——缓冲未注册+多 GPU 单进程时 LL 对称内核跑不了，回退 general 模型重选。失败时把 NCCL_ALGO/NCCL_PROTO 设置值拼进 WARN（tuning.cc:308-329），用户设错报 ncclInvalidUsage。

### 5. 模型注册表与启停（cost_model.cc）

`modelMap[]`（cost_model.cc:230）与 `src/config/algorithm_registry.cc` 的 algRegistry 强制同步（cost_model.cc:229 注释）。条目分三组：21 个常规 algo/proto 槽（无实现的填 nullptr，如 CollNetDirect/LL，cost_model.cc:237）、sym kernel 槽、CE 方法槽（cost_model.cc:271-272）。每条带 `enabled[NCCL_NUM_FUNCTIONS]` 静态开关，例如 Tree 系列只对 AllReduce 开（`{0,0,0,0,1}`，cost_model.cc:234）。**强制启停**两来源：环境变量 `NCCL_ALGO`/`NCCL_PROTO` 由 `parseList`（cost_model.cc:33）解析——分号分组、冒号前缀按 collective 过滤、`^` 取反（示例 cost_model.cc:21-31），结果写 `forced[]` 并裁剪 enabled；per-call tuningMask 再收窄一层。

### 6. 耗时公式（tuning_general.cc）

通用公式 `ncclTuningGetTime`（tuning_general.cc:52）：`lat×latCount + nBytes/(1000×bw)`，latCount 对 Ring 是 numPipeOps、树类按 `NCCL_MAX_DEV_WORK_BATCH_COLLS` 折半（tuning_general.cc:54）。fp8 且 Ring 深 reduce 会丢精度，直接乘 1024 惩罚系数压到最后（tuning_general.cc:58-63）。`ncclTuningSetThreadThresholds`（tuning_general.cc:86）设 maxThreads（LL 512/LL128 640/Simple 上限）与 threadThresholds（Ring/LL 乘 nRanks，tuning_general.cc:113），`NCCL_THREAD_THRESHOLDS` 可覆写。

## 三、外部连接

include：tuning_int.h/cost_model.h/tuner.h/transport.h/comm.h/device.h（tuning.cc:8-15）。被调：`ncclTuningInit`（init.cc:1899，紧跟 transport 建连）；`ncclTuningCompute`（enqueue.cc:2192/2202/2214、task_prep.cc:24 每任务预处理、symmetric_sched.cc:206 对称内核调度、ce_coll.cc:96 CE 方法选择）；`ncclTuningFinalize`（comm 销毁）。向外依赖：`ncclTunerPluginLoad/Unload`（tuner.h:20）加载外部 `ncclCommTuner` 符号；`ncclNvlsRegResourcesQuery`（tuning.cc:247）查 NVLS 注册通道余量。

## 四、数据流

```
comm 创建: ncclTuningInit                        [tuning.cc:44]
  PreInit(默认常量) → 插件 load+init → CostModelInit(逐模型)
  → SetThreadThresholds → rank0 打印 lat/bw 表

每次集合调用: ncclTuningCompute(input)            [tuning.cc:180]
  input{func,datatype,nBytes,tuningMask,...}      [tuning.h:57]
  → AllTunings: 遍历 NCCL_TUNING_COUNT 个 ID      [tuning.cc:128]
      mask 过滤 → ExpandId(algo/proto/symk/ce)    [tuning_general.cc:204]
      → CostModelSimModel → modelMap[id].model    [cost_model.cc:470]
      → timeUs(或 NCCL_TUNING_IGNORE+valid=0)
  → tuner 插件 getCollInfo 改写 generalTable      [tuning.cc:219]
  → SelectBestTuning(按 selectionTimeUs)          [tuning.cc:155]
  → GetChannels(nChannels/nWarps)
  → bestTuning{algo,proto,timeUs,nChannels} → enqueue 决定 kernel
```

## 五、设计决策

1. **统一 ID 空间吸收异构候选**：常规 kernel、对称内核、CE 方法本是三类东西，塞进连续 ID+位图掩码后，选优循环、启停矩阵、插件接口全部归一——新增实现只改 modelMap 一行（须同步 algorithm_registry，cost_model.cc:229）。
2. **内部模型优先、插件只改数不改集**：插件拿到的 generalTable 初值是内部仿真结果（tuning.cc:204-216），能改 timeUs 与 maxChannels，但候选集合由 mask 与 modelMap 决定，插件挂了系统仍可用（NOWARN 路径 enqueue.cc:2192）。
3. **enabled×func 矩阵静态表达先验**：Tree 只服务 AllReduce（cost_model.cc:234）、PAT 只对 AG/RS 开，把"哪些 collective 有意义"写成编译期数据而非运行时 if。
4. **selectionTimeUs 与 timeUs 分离**：允许插件表达"训练贵、推理便宜"的调度偏好，内部模型两者相同（tuning.cc:162）。

## 六、新人提示

- 排查"为什么没用 XX 算法"：`NCCL_DEBUG=INFO,NCCL_DEBUG_SUBSYS=TUNING` 看 Init 的表与 Compute 的 Best tuning 行；再查 NCCL_ALGO/NCCL_PROTO 是否被设（WARN 带你的设置值，tuning.cc:317-328）。
- LL128 在跨代硬件上有硬件级限制（`isLL128Enabled`，cost_model.cc:107：PXB 以上的 PxN 路径、不同 compcap 混布都会关），混布集群性能异常先想到它。
- 写 tuner 插件时记住：getCollInfo 返回的表中没动的格子必须保持传入值或 NCCL_TUNING_IGNORE，返回 0 或负数会被当成"更快"而误选。
- 调 nChannels/nWarps 不是改 tuning.cc，而是 `NCCL_NTHREADS`/`NCCL_THREAD_THRESHOLDS` 等（tuning_general.cc:87-127）。
- 改 modelMap 顺序是高危操作：ID 空间是 ABI，modelMap 的行序必须与 algorithm_registry.cc 完全一致，错位会让 mask 过滤选到完全不同的实现。
