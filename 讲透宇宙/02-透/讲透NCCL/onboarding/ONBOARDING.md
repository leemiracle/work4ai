# NCCL 仓库 Onboarding（v2.32.3-1）

> 仓库 `/usr-data/data2/kylin/nccl`（commit 3e46c089）；图谱 4306 节点/7631 边/16 层/16 步导览。锚均经源码核实。

## 1. 这是什么仓库

NCCL（NVIDIA Collective Communications Library）是 NVIDIA 官方开源的多 GPU/多节点集合通信库——PyTorch/Megatron 训练时梯度 AllReduce 的默认底座。版本 2.32.3（`makefiles/version.mk:9` 起版本三元组），支持到 Blackwell。图谱分析范围 723 文件：头文件 327、C++ 实现 204、Python 50，其余为 CUDA 与构建脚本。

## 2. 五分钟心智模型

训练栈位置：**框架（DDP/Megatron）→ NCCL（选算法、发 kernel）→ CUDA driver → NVLink/NVSwitch/IB/RoCE**。NCCL 在 GPU 上 launch 自己的 kernel，把集合通信拆成算法（Ring/Tree/CollNet/NVLS/PAT）×协议（LL/LL128/Simple），多通道流水线执行。

- **communicator**：`ncclComm`（`src/include/comm.h`），rank 集合的通信上下文。rank 0 调 `ncclGetUniqueId`（`src/init.cc:209`）产出带外 token，各 rank 持同一 id 调 `ncclCommInitRank`（`src/init.cc:2946`）；初始化期 bootstrap TCP 互认（`src/bootstrap.cc:754`）。
- **collective**：`ncclAllReduce` 等用户 API（实现在 `src/collectives.cc`），每次调用被选型为"算法×协议×通道数"映射到专用 device kernel。
- **plugin**：运行时 dlopen 的扩展点，六族 NET/GIN/RMA/TUNER/PROFILER/ENV（`src/plugin/plugin_open.cc:22`），网络后端/调优/profiler 均可不重编替换。

## 3. 目录地图

| 目录 | 职责 |
|---|---|
| `src/` 根 | 主干：`collectives.cc`（集合 API 入口）、`init.cc`（4007 行全仓最大）、`group.cc`、`bootstrap.cc`、`transport.cc`、`proxy.cc`、`dev_runtime.cc`（对称内存）、`ce_coll.cc`（Copy Engine）、`nccl.h.in` |
| `src/include/` | 头基座：`comm.h`（ncclComm 结构）、`device.h`（host/device 共享协议）、transport/graph/enqueue/proxy 各头、`plugin/`（ABI 版本塔） |
| `src/enqueue/` | 发射引擎：`enqueue.cc`（3601 行）、`task_prep/`、`task_sched/` |
| `src/graph/`+`src/tuning/` | 拓扑选路（`topo/search/rings/trees/xml.cc`）与代价模型（`tuning.cc`+各通道时间模型） |
| `src/transport/` | `p2p.cc`/`shm.cc` 机内、`net.cc` 网络入口、`net_ib/`（含 vendored kdaki/DOCA）、`net_socket/`、`nvls.cc`/`coll_net.cc` |
| `src/device/` | GPU kernel：`common.cu/h`、各集合 `.h`、`prims_ll/ll128/simple.h` 三协议原语、`symmetric/` 新路径 |
| `src/plugin/`+`plugins/` | 插件加载适配层；示例插件与 inspector profiler |
| 其余 | `param/misc/config/os` 参数、`ras/` 诊断、`bindings/`（nccl4py+ir） |

## 4. 核心架构：分层走读

图谱 16 层重组为六大层，自上而下单向依赖：

1. **API 面与参数基座**（L01-02/L14）：`nccl.h.in` 1025 行模板由 `src/generate_header.cmake:8` 替换占位符生成 `nccl.h`；conf 装载在 `src/misc/param.cc:61`，`NCCL_DEBUG` 经 `DEFINE_NCCL_PARAM` 注册（`src/debug.cc:43`）。
2. **生命周期与拓扑**（L03/L05）：`ncclCommInitRankConfig`（`src/init.cc:3049`）做 bootstrap 建链与 peer 交换；`ncclTopoGetSystem`（`src/graph/topo.cc:1989`）从 sysfs/NVML 建模拓扑，`ncclTopoCompute`（`src/graph/search.cc:1151`）搜索最优通道图。
3. **调优**（L06）：`ncclTuningCompute`（`src/tuning/tuning.cc:180`）用 cost model 选算法×协议；有 tuner 插件则由 `tuner->getCollInfo` 决策（`src/tuning/tuning.cc:219`）。
4. **发射引擎**（L11）：enqueue 生成任务与 plan；`ncclProxyCreate`（`src/proxy.cc:2130`）为每 GPU 起 service（`src/proxy.cc:2157`）+progress（`src/proxy.cc:1033`）双线程推进网络收发。
5. **传输与网络**（L07-08）：`ncclTransports[]` 注册 p2p/shm/net/collNet 四 vtable（`src/transport.cc:15`）；网络内置 IB/RoCE+TCP 兜底，缺省回退外部插件（`src/plugin/net.cc:357`）；CE 路径（`src/ce_coll.cc`）免 SM 执行。
6. **设备 kernel 与出口**（L04/L09-10/L12-13/L16）：`src/device` 传统 kernel、`symmetric/` 对称内存新路径、`src/nccl_device` 设备 API；对称内存底座（`src/dev_runtime.cc`）横切其间。

## 5. 一条 ncclAllReduce 的完整旅程

1. **API 入口**：`ncclAllReduce`（`src/collectives.cc:206`）→ `ncclAllReduceConfigImpl`（:192）打包成 `ncclInfo` 交 `ncclEnqueueCheck`（:201）。
2. **入队**：`ncclEnqueueCheck`（`src/enqueue/enqueue.cc:3478`）隐式包裹 GroupStart/End；`taskAppend`（:3337）四路分派（集合/send-recv/RMA/raw）；group 深度归零时 `ncclGroupEndInternal`（`src/group.cc:1039`）触发发射。
3. **调优与调度**：`doLaunches`（`src/group.cc:427`）→ `ncclPrepareTasks`（enqueue.cc:423）：`ncclTaskPreTuning`（`src/enqueue/task_prep/task_pretuning.cc:263`）组装输入，`ncclTuningCompute`（`src/tuning/tuning.cc:180`）选型，`ncclTasksRegAndEnqueue`（enqueue.cc:351）登记。
4. **装配 kernel**：`plan->kernelFn = ncclDevKernelForFunc[task->devFuncId]`（enqueue.cc:905），索引由 `ncclDevFuncId(coll,redop,type,algo,proto)` 编译期映射（`src/include/device.h:646`）。
5. **发射与代理**：`ncclLaunchKernel`（enqueue.cc:1886）组装 grid/block/shmem 并 cuLaunchKernel；需 CPU 的网络切片交 proxy 线程推进。
6. **设备执行**：`ncclDevKernel_Generic`（`src/device/common.cu:23`）→ `ncclKernelMain`（`src/device/common.h:420`）逐 work 执行 `ncclDevFuncTable[funcId]()`（:486）；AllReduce 展开 `runRing`（`src/device/all_reduce.h:14`）/`runTreeUpDown`（:86）/`runTreeSplit`（:146），由 prims_ll/ll128/simple 三协议原语（`src/device/primitives.h`）收发归约。

## 6. 新人导览路线

16 步 tour 压缩为 8 步：

1. `README.md`+根 `Makefile`（`Makefile:21` `default: src.build`；`Makefile:29` `TARGETS := src pkg nccl4py ir`）。
2. `src/nccl.h.in` 通读 API 面，对照 `src/collectives.cc` 看入口统一收敛——"所有集合调用同构"。
3. `src/init.cc`+`src/bootstrap.cc`+`src/graph/topo.cc`→`search.cc`：communicator 从 uniqueId 诞生；拓扑探测与选路是 NCCL 的"智能"。
4. `src/tuning/tuning.cc`：图搜索产物如何变成算法/协议选择。
5. `src/transport.cc`+`p2p.cc`/`shm.cc`：传输 vtable 抽象与 proxy 契约。
6. `src/enqueue/enqueue.cc`+`task_prep/`：发射管线，对照第 5 节读。
7. `src/device/common.cu`+`all_reduce.h`+`primitives.h`：协议与算法正交组合，再看 `symmetric/`。
8. `src/plugin/`+`plugins/`：动手改 tuner 示例收尾。

## 7. 构建与插件加载

**双构建体系**：Make 路径由根 `Makefile` 聚合（`make -j src.build`；`src/Makefile:92` 拼 `libnccl.so.2.32.3` soname）；CMake 负责生成 `nccl.h`（`src/generate_header.cmake:2`）。

**插件加载**：`tryOpenLib`（`src/plugin/plugin_open.cc:28`）经 `ncclOsDlopen`（:39）按六族名搜库；环境变量值 `STATIC_PLUGIN` 表示静态链接、跳过 dlopen（`src/plugin/plugin_open.cc:35`）。网络插件由 `NCCL_NET_PLUGIN` 指定（默认 `libnccl-net.so`，`src/plugin/net.cc:297`）；tuner 由 `NCCL_TUNER_PLUGIN` 指定（`src/plugin/tuner.cc:59`）。

**版本塔**：ABI 兼容靠"最新 typedef+逐代回退数组"——`ncclNet_t` 钉 v12（`src/include/plugin/nccl_net.h:54`），加载时按 `getNcclNet[] = {v12, v11, ... v6}`（`src/plugin/net.cc:42`）逐代试插件符号；tuner 钉 v6（`src/include/plugin/nccl_tuner.h:21`）。

## 8. 上手第一周与常见坑

**Day 1-2**：`make -j src.build` 后跑 `bindings/nccl4py/examples/01_basic`（示例多在 `plugins/*/example`）；加 `NCCL_DEBUG=INFO`（`src/debug.cc:43`）看 init/拓扑/通道日志。

**Day 3**：`NCCL_ALGO`/`NCCL_PROTO` 强制算法协议（注册表 `src/config/algorithm_registry.cc:32` 起）对比带宽；持久化走 `/etc/nccl.conf`（`src/misc/param.cc:65`）。

**Day 4-5 tuner 插件（最短路径）**：抄 `plugins/tuner/example/`——最简可不写 C：改 CSV 的 `nccl_tuner.conf`（格式见该文件头注释），make 后 `NCCL_TUNER_PLUGIN=libtuner.so` 生效；写逻辑则改 `plugin.c` 实现 v6 的 `init/getCollInfo/finalize`。

**常见坑**：
- **`nccl.h` 是生成物**：源码只有 `src/nccl.h.in`（1025 行模板），占位符替换在 `src/generate_header.cmake:8`；改 API 改模板而非 `include/nccl.h`。
- **kdaki/DOCA 是 vendored**：`src/transport/net_ib/gdaki/` 内嵌 DOCA GPUNetIO 头（`mlx5_ifc.h` 5702 行，全仓最大头），供 GIN 的 GD-RDMA 用，别当自研逻辑读改。
- **插件版本错配**：只导出老符号（如 `ncclNetPlugin_v6`）的插件靠版本塔回退（`src/plugin/net.cc:42`），但头 typedef 已是 v12。
- **proxy 慢≠kernel 慢**：网络收发由 proxy 线程（`src/proxy.cc:2157`）推进，排障时分开看。
- **优先级**：环境变量先于 conf 文件生效（`src/misc/param.cc:53-65`），排障先查残留 `NCCL_*`。
