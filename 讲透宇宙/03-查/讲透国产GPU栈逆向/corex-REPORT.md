# 天数智芯 corex 通信栈逆向报告（ixccl 线）

> 第八轮主线（TASK-vendor.md 2026-11-11）。样本源：node14 镜像 `dev-community-acr-registry.cn-shanghai.cr.aliyuncs.com/dev-community/vllm-iluvatar:0.27.1_py3.12-corex.5.0.0-ubuntu24.04-aarch64`（image id 558e5793eb4c）。
> 本报告增量写作（1308/死机防丢稿）；死机恢复后 21:5x 重建死前 18:23-18:26 发现。
> 对照上游：本地 `/usr-data/data2/repos/agent-repos/NVIDIA/nccl` @ v2.32.3-1（12df1a1）。

## 0. 样本清单（已 md5 验收）

| 样本 | 尺寸 | md5 | 来源 |
|---|---|---|---|
| `libnccl.so.5.0.0.2289` | 146,499,032 | 8e6a28e2b4ed346f3b01520a2e8064f2 ✓ | 镜像 /usr/local/corex/lib64（SONAME=libnccl.so.2） |
| `libnccl_static.a` 成员清单 | 238 成员（`corex-nccl-ar.txt`） | — | 同上（ar t 远端执行） |
| `libixsysnccl.so` | 205,680 | — | 同上（profiler 适配层） |
| `ixccl.h` + `nccl.h` + `IX/mapping_nccl.h` 等 4 头 | 624/406/333/24 行 | — | 镜像 /usr/local/corex/include + include/IX/（19 个 mapping 头） |
| `libcudart.so.10.2.89` / `libnvrtc.so.10.2.89` | 7.8MB / 1.5MB(not stripped) | — | 镜像 lib64（CUDA 10.2 版号兼容层全套） |
| host/`libcuda.so.1` + `libixml.so` + `ixsmi` | 14.97MB / 691KB / 1.5MB | — | node14 宿主 /usr/local/corex-5.0.0/{lib64,bin}（driver 层） |

UCCL 真机表对照（/usr-data/data2/kylin/uccl/src/providers/provider.cpp:15-18）：ts provider dlopen `libnccl.so.2` + `libcudart.so.10.2`，prefix `nccl`——与镜像供给完全吻合（真机在用版本即本样本）。

## 1. 血统链判定：NCCL 2.28.9 源码 fork + nccl→ixccl 机械改名（CONFIRMED 多重锚）

1. **头文件层**（samples/corex/ixccl.h:1-5）：NVIDIA 版权头 `Copyright (c) 2015-2021, NVIDIA CORPORATION` 原样保留；全部 API `ncclX→ixcclX` 系统性改名（sed 式）；`NCCL_*` 宏名未改（NCCL_MAX_CHANNELS/NCCL_CONFIG_INITIALIZER/NCCL_WIN_COLL_SYMMETRIC...）。
2. **版本三重锚**（ixccl.h:23-28）：`NCCL_MAJOR 2 / MINOR 28 / PATCH 9 / VERSION_CODE 22809`；文件名尾缀 2289 同源；结构体版本戳链 `ixcclConfig_v21700`（上游 2.17 引入 config）/`ixcclSimInfo_v22200`（上游 2.22 GroupSimulateEnd）——fork 基线=2.28.9。
3. **静态库成员名 = 上游源文件名原封**（corex-nccl-ar.txt）：bootstrap.o/channel.o/collectives.o/init.o/proxy.o/transport.o/topo.o/trees.o/search.o/rings.o/paths.o/connect.o/argcheck.o/env.o/param.o/shmutils.o/... 与上游 src 树一一对应。
4. **上游插件 ABI 面全保留**：`net_v6.o…net_v11.o`（net 插件 6 代）、`tuner_v2.o…tuner_v5.o`、`profiler_v1.o…profiler_v5.o`、`env_v1.o`。
5. **DOCA GPUNetIO 传输全套**：doca_verbs_{qp,cq,device_attr,umem,srq,uar}.o + doca_gpunetio{,_log,_high_level,_gdrcopy,_cuda_wrapper,_mlx5dv_wrapper,_ibv_wrapper}.o。
6. **探桩模式保留但改名**：上游 pnccl\* 探桩 → `pixccl*`（55 个导出，见 §2）；mapping_nccl.h:26 同步映射 `#define pncclMemAlloc pixcclMemAlloc`。
7. **编译期兼容架构**（IX/mapping_nccl.h）：`#define ncclAllReduce ixcclAllReduce` 等 333 行宏映射——CUDA 源码 include nccl.h 即无感切换到 ixccl 符号；IX/ 目录 19 个 mapping 头覆盖 cudart/cublas/cublasLt/cufft/cudnn/curand/cusolver/cusparse/nvrtc/nvml/nvtx/cupti/profiler_api/ixsdk 全工具链。

**结论**：天数 ixccl = NCCL 2.28.9 完整源码树 fork（非重写、非二进制包装），改名策略=符号层 ixccl\*/pixccl\*，SONAME 与 nccl\* 兼容导出保留双命名空间。血统链：**NCCL 2.28.9 →(fork+改名)→ ixccl 5.0.0(corex 5.0.0)**。

### 1.1 gin/Team/Lsa/LLA2A 归属甄别（CONFIRMED 2026-11-11 22:2x——修正死前初判）

死前初判 gin_\*/Team/Lsa/LLA2A 为"天数私有增量"，**交叉验证后反转**：

- NV libnccl.so.2.27.3 二进制 **零 GIN 串**（strings 全扫，NCCL_GIN/GinBarrier 0 命中）——2.27.3 无 GIN。
- 上游 v2.32.3 源码有**完整 GIN 子系统**：`src/gin/{gin_host.cc,gin_host_proxy.cc,proxy_gpucontext}` + `src/include/nccl_device/gin_barrier.h` + `ncclGinProxy{Listen,Connect,RegMrSym,DeregMrSym,FlushesAllPutsOnAnySignal}`（gin_host_proxy.cc:347-450）——**对称内存 RDMA 代理原语族**（GPU 发起、IBGDA 类）；`ncclGinBarrierCreateRequirement/ncclTeamRail` 符号在 src/dev_runtime.cc、sym_kernels.cc、windows_stubs.cc 多处引用。
- **结论：GIN=上游 NCCL 2.28 代新面**（2.27.3 无→2.32.3 全量），corex 2.28.9 fork 自带；符号名与上游逐字吻合（ncclGinBarrierCreateRequirement/ncclTeamRail 双侧一致）。
- **同版本二进制终审（2026-11-12 补：aidp-vllm-nv-v024 镜像得 NV 正版 2.28.9 sys 版 x86_64/cuda13.0/189MB）**：NV 2.28.9 vs 2.27.3 上游增量恰=16 符号 {AlltoAll/Gather/Scatter/CommRevoke/DevCommCreate/Destroy/ResetDebugInitInternal/GinBarrier/Team{Lsa,Rail,RankToLsa,RankToWorld,World}/LLA2A×2/LsaBarrier}——**上表 GIN/Team/LLA2A/Lsa 归属从"交叉推断"升格"同版本 NV 二进制逐字实证"**；corex vs NV 同版本：NV 零独有（严格超集），**corex 额外导出收缩为 11 符号**={CommGet/SetAttribute（私有已判）+DevFunc/DevKernel/Symk/GetExportTable 内省族（NV 2.28.9 sys 不导出、上游 2.32 才公开面——天数提前开放或自加，介于上游/天数间标注）}。
- **天数真实私有增量收缩为**：①ixccl/pixccl 改名层；②IXCCL\_* env 别名域（§4.3）；③CONFIG_ENUM 调优面+NCCL_RBUFF（§3）；④GIN 实现侧调优 env。**GDAKI 亦为上游件**：上游 `transport/net_ib/gdaki/`（Makefile:33-34,116-118）+DOCA GPUNetIO 挂其下（ar 中 doca_\*.o 全为上游）——corex 对上游的结构性改动≈零，= **vanilla 上游 2.28.9+改名层+私有 env/config 皮**。
- **私有项上游零命中终判（2026-11-11 深挖，v2.32.3 源码树 grep）**：`ncclCommGet/SetAttribute`+`NCCL_RBUFF`+`MIX_NV` 上游 src 零命中=**天数私有 CONFIRMED**；`ncclCommRevoke`（nccl.h.in+init.cc）与 `ResetDebugInitInternal`（debug.cc）在上游=**上游 2.28 面**。corex fork 点精确钉 2.28.9：上游 2.32.3 公共头（src/nccl.h.in，217 符号）比 corex 多出的 2.29+ 新面=Config 变体集体操作族（AllReduceConfig 等）/CommGrow/Suspend/Resume（弹性）/EncryptionConfig/HostCft/NvlsHostMode——**天数尚未回吸 2.29-2.32 任何一代**。
- **GDAKI 实现层（静态符号 4328 个直供）**：`ixcclGinIbGdaki`（d）+`ixcclGinIbGdakiDevIndexes`+模板实例 `ixcclCudaMemcpy<ixcclGinGdaki{MemHandle,GPUContext}>`/`ixcclCudaMemcpyAsync<...>`（消费 `IXDRVstream_st` 天数驱动流类型）+`ixcclGinGdakiProgress`——**GDAKI=GIN-IB 之上的 GPU 发起异步拷贝层**（IBGDA 类），驱动接口走 IXDRV。
- 上游 libnccl.map（src/libnccl.map:17-20）通配导出 `nccl*; pnccl*`——天数私有扩展（ncclTeam\* 等）以 nccl\* 前缀自动落导出面，无需改 map。
- 沐曦/海光同代对照价值：MCCL 2.16.5/RCCL 2.22.3 均早于 GIN 引入→**GIN 是 NV/TS 独有代际差**，跨厂商统一层（UCCL）无法以 GIN 为公共面。

## 2. ABI 对照（vs 上游）

### 2.1 导出面（nm -D，libnccl.so.5.0.0.2289）

- 导出 110 T + 55 W + 2 D + 5 R；`nccl*` 兼容导出 53 个、`ixccl*` 57 个、`pixccl*` 55 个、`pnccl*` **0 个**。
- SONAME=libnccl.so.2 + DT_NEEDED={libcuda.so.1, libcudart.so.10.2, libpthread, librt, libdl, libstdc++, libm, libgcc_s, libc}——即 UCCL 陷阱#5（原厂库 DT_NEEDED 不在 ldconfig 时需 RTLD_GLOBAL 先行）的天数实证。
- **无版本符号表**（.gnu.version 仅 glibc/glibcxx/cuda/cudart 依赖标记，无 NCCL_* 版本节点）——与上游 nccl 无 symbol versioning 一致。

### 2.2 nccl\* 兼容导出中的私有扩展（53 个清单甄别）

上游 2.27.3 公共面之外（**归属终判见 §1.1：下表全部为上游 2.28 代新面，非天数私有**；此处按语义线分列）：

| 符号 | 语义（结合 ar 成员） | 归属 |
|---|---|---|
| `ncclGinBarrierCreateRequirement` | GIN 互联 barrier 语义（gin_barrier.o） | GIN 线 |
| `ncclLLA2ACreateRequirement` / `ncclLLA2ACalcSlots` | LL 协议 all-to-all（ll_a2a.o） | LLA2A 线 |
| `ncclLsaBarrierCreateRequirement` | LSA barrier（lsa_barrier.o） | LSA 线 |
| `ncclTeamLsa` / `ncclTeamRail` / `ncclTeamRankToLsa` / `ncclTeamRankToWorld` / `ncclTeamWorld` | **Team/Rail 拓扑抽象**（rail-optimized 机架拓扑，多网卡多轨） | Team 线 |
| `ncclDevCommCreate` / `ncclDevCommDestroy` | device-side communicator | 上游新面（2.27+）待核对 |

⚠️ 私有扩展以 **nccl\* 原生前缀导出**（非 ixccl\*）——跨厂商库共存场景（UCCL 陷阱#2 符号共存）下这些是同名碰撞高发面。

### 2.3 结构体尺寸（ABI 陷阱素材）

`ixcclConfig_t`（ixccl.h:81-101）字段：size/magic/version + blocking, cgaClusterSize, minCTAs, maxCTAs, netName, splitShare, trafficClass, commName, collnetEnable, CTAPolicy, shrinkShare, nvlsCTAs, nChannelsPerNetPeer, nvlinkCentricSched = **sizeof = 8+4+4 + 13×4 + padding ≈ 76/80B**。上游 2.27 ncclConfig_t 同构（cgaClusterSize=Hopper CGA cluster 概念在国产 IVCore 的对应物）。magic=0xcafebeef 沿用上游。

## 3. 能力探测面

- **对称内存族 ✅**（UCCL 四栈表实证 TS 独有）：`ixcclCommWindowRegister/Deregister`（ixccl.h:295-300）+ `NCCL_WIN_COLL_SYMMETRIC`/`NCCL_WIN_REQUIRED_ALIGNMENT 4096`（:62-65）+ ar 成员 sym_kernels.o/symmetric_sched.o/sym_kernels_host.cu.o——**完整对称内存 kernel+调度栈**。
- CommSplit/CommShrink/CommRevoke/CommInitRankScalable 全有（2.28 面）。
- **pixccl\* 探桩 55 个**=pnccl\* 模式国产对应物（dlsym 探活不发调用即返回的 weak 语义——本库中为 T 强导出）。
- 私有调优面：`ixcclCommGetAttribute/SetAttribute` + CONFIG_ENUM 9 项（ixccl.h:605-618）：FORCESYNC_DISABLE/USE_DIRECT/USE_STREAMS/USE_MULTI_CU/FUSED_ENABLE/PRIM_P2P_LEVEL/USE_HIGHPRIORITYWARP/P2P_CHUNKSIZE/**MIX_NV**——MIX_NV 语义待二进制字符串/反汇编甄别（疑混合 NVLink 类高速域+网络域调度开关）。
- `NCCL_RBUFF 16384`（ixccl.h:603）私有常量。

### 3.1 内嵌 device 容器层（任务书动作 6，2026-11-11 终章 CONFIRMED）

`.nv_fatbin` 节 0x6d23c26=114.4MB（146MB 库的 78%）+ `.nvFatBinSegment` 注册段 3KB：
- **127 个天数自研 fatbin 单元拼接**（每单元 16B 头：magic 0x20160329@+0 + version@+4 + fat_size@+8；尺寸 14.8KB~8.2MB，合计=节大小精确吻合）——**第七轮工具链线的 magic 0x20160329 结论在通信库同样成立**。
- CUDA 系 AOT 分发（cubin 内嵌），与 metax 的 bitcode-JIT/海光的五架构 AOT 形成三模式对照（见 metax/dtk 报告同节）。

## 4. 协议常量与私有 env 面（2026-11-11 22:1x 补齐）

### 4.1 版本串锚

`NCCL version 2.28.9+cuda10.2`@0x189a48 / `NCCL version 2.28.9 compiled with CUDA 10.2`——**品牌串保留 NCCL**（对照：沐曦改 MCCL、海光改 RCCL）——fork 改名只到符号层，日志/版本串层未清洗。

### 4.2 env 旋钮普查（四库）

NV 170 / **TS 231（最多）** / MX 201 / HG 172。corex vs NV 2.27.3：新增 62、删除 3（NCCL_MEM_SYNC_DOMAIN/NVLS_CHUNKSIZE/NVLS_ENABLE——删 NVLS 专控+Hopper mem sync domain，无对应硬件）。

### 4.3 天数私有 env 双前缀体系（核心发现）

- **NCCL_GIN_\* 全家桶**（GIN 传输层）：`NCCL_GIN_ENABLE`@0x19d160、GIN_TYPE/NCONTEXTS/PROXY_QUEUE_SIZE/SIGNAL_POOL_SIZE/COUNTER_POOL_SIZE/ERROR_QUERY_SEC、**`NCCL_GIN_GDAKI_{NIC_HANDLER,QP_DEPTH}`**@0x19a350（GDAKI=GIN 的 IB RDMA 直达路径，QP 深度可调）、GIN_IB_ALLGATHER_TAG/GIN_IB_ALLTOALL_TAG（协议 tag 约定）。
- 网络设备名：`GIN_IB_GDAKI` / `GIN_IB_PROXY`（NCCL_NET_DEVICE_GIN_{GDAKI,PROXY} 指定语法在场）——**UCCL 跨厂商数据面互操作素材：GIN 网络走 IB verbs，可与自研 ibverbs 数据面同构对接**。
- **IXCCL\_* 别名域**：`IXCCL_MIX_NV`@0x18eaa8、IXCCL_USE_DIRECT/USE_STREAMS/USE_MULTI_CU/FUSED_ENABLE/PRIM_P2P_LEVEL/USE_HIGHPRIORITYWARP/P2P_CHUNKSIZE/PROFILING_NETWORK/MAX_GRAPH_BUFFERS_SIZE/EXPORT_UUID/RAS_OP_TRACE_*——与 CONFIG_ENUM 调优面一一对应，**每个私有旋钮 NCCL_/IXCCL_ 双前缀可配**。
- IXDRV_DEVICE_ATTRIBUTE_\* 串族（CAN_FLUSH_REMOTE_WRITES/STREAM_MEM_OPS/64_BIT_STREAM_MEM_OPS 等）——驱动属性按名查询枚举串。
- MIX_NV 语义定界待反汇编（疑混合高速域+网络域调度，或 NV 模式混跑开关）。

### 4.4 协议常量

LL128/NVLS/COLLNET_{DIRECT,CHAIN}/NVLS_TREE/MNNVL 字串全在场（上游 fork 全量继承）；天数无 NVLS 硬件但代码路径未裁——NVLS 符号面在场≠能力，探测必须走运行时。

## 4.5 四库导出面 diff 总表（2026-11-11 22:1x，NV=libnccl.so.2.27.3 基线）

| 维度 | NV 2.27.3 | TS corex 2.28.9 | MX mccl 2.16.5 | HG rccl 2.22.3 |
|---|---|---|---|---|
| SONAME | libnccl.so.2 | libnccl.so.2（同！） | libmccl.so | librccl.so.1 |
| 导出总数 | 74 | 172 | 208（含 165 C++ 污染） | 120 |
| API 前缀 | nccl\*/pnccl\* | nccl\*+ixccl\*+pixccl\* 三空间 | mccl\* 单空间 | **nccl\* 原生前缀**+du\* |
| p 探桩 | pnccl\* 37 | pixccl\* 55 | pmccl\* 头声明二进制缺 | pnccl\* 部分 |
| 对称内存 Window | ✅ 符号在（2.27 新面） | ✅+Symk 内省族 | ❌ | ❌ |
| AllToAll{,v}/Gather/Scatter | ❌ | ✅（2.28 面） | ✅ +AllToAlld/Ext 族 | ✅ +du\* 族 |
| 版本品牌串 | NCCL | **NCCL（未清洗）** | MCCL | RCCL |
| 私有域 | — | IXCCL_ 双前缀 env+CONFIG_ENUM（GIN=上游 2.28 新面非私有，见 §1.1） | CUBE_RINGS/Pivot/Ext | XHCL/ROME/XDP |

**corex 归一后=NV 2.27.3 严格超集**（NV 零独有；corex 多 27 API=2.28 上游新面 AlltoAll/Gather/Scatter/GetExportTable/DevKernel 内省族 + 上游 2.28 GIN/Team 新面，见 §1.1 修正）。

### 4.6 探桩 T/W 别名机制四库普查（2026-11-11 22:3x，NVIDIA 线反哺）

NV 2.27.3 机制（nm 实证）：`pncclAllReduce@0x58b40 (T)` ≡ `ncclAllReduce@0x58b40 (W)` **同地址别名对×37**——**p 前缀=强符号本体，无前缀=weak 别名**（外部强定义可抢占 weak 名=可 interposition；p 名永远绑定本库=探活安全）。

| 库 | T/W 配对 | 语义 |
|---|---|---|
| NV 2.27.3 | 37 T(pnccl\*) + 37 W(nccl\*) | 完整 weak-alias 探桩机制 |
| **corex 2.28.9** | pixccl\* 55 T + ixccl\* 55 W 同地址（ixcclAllReduce@0x67178 W ≡ pixcclAllReduce@0x67178 T 实证）+ **nccl\* 兼容层 53 个全 T** | 机制保留但改名；**兼容层升强符号**——与 NV 真 libnccl 同 SONAME(libnccl.so.2) 共存时抢占语义反转（UCCL 陷阱#2 升级点） |
| metax 2.16.5 | 43 mccl\* 全 T，零 W | 无机制（pmccl\* 头声明/二进制无） |
| dtk 2.22.3 | 36 nccl\*+12 du\* 全 T，零 W | 无机制（pnccl\* 头声明 rccl-real.h:700/二进制 0 个） |

**跨厂商结论：weak-alias 探桩=NV 系（2.27+）专属；AMD 系两家（RCCL/MCCL）头文件抄了 p 声明但没实现**。UCCL 探测逻辑：nv/ts 可依赖 p 名强绑定语义；mx/hg 只能符号存在性探测且**必须 RTLD_DEEPBIND**（全强符号库共存时按加载序解析）。

## 5. libixsysnccl.so 定性（CONFIRMED）

天数系统层 NCCL profiler 适配器（205KB，独立 .so）：
- 导出 `ixcclProfiler_v5`@0x20160（数据槽）+ C++ 族 `ixsysNcclProfiler{Init,Start,Stop,Finalize,RecordEventState}`（签名消费 `ncclProfilerEventDescr_v5_t`/`ncclProfilerEventStateArgs_v5_t`）——即**上游 profiler 插件 v5 ABI 的宿主侧实现**，把 NCCL 事件写 trace 文件。
- env 旋钮：`IXSYS_NCCL_PROFILER_MASK` / `IXSYS_NCCL_PROFILE_ALLOC_CHUNK` / `IXSYS_NCCL_TRACE_FILENAME`。
- 与 libnccl 内 profiler_v1-v5.o 成员呼应：原厂库按 v5 注册点回调本适配器（天数的 profiling 闭环=nccl 插件面原生实现，NVIDIA 对应物=nsys/ncu）。

## 5.1 WindowRegister（插入节） 天数 vs NV 实现对照（Ghidra+DWRAF，2026-11-11 深挖 CONFIRMED）

corex lib 146MB=**debug build 带 DWARF**（ghidra 直接解析 `ixcclWindow_vidmem**/ixcclDevrRegTask*/ixcclComm{symmetricSupport,devrState,groupNext,intraComm0,commHash,channels,memScoped}` 类型）：

| 维度 | NV 2.27.3 | corex 2.28.9 |
|---|---|---|
| 源锚 | register/register.cc {0x98-0xf6} | **dev_runtime.cc {899,0x388,0x389,0x38b,0x38d,0x397} + include/alloc.h:0x88**（结构迁移：窗口逻辑移入 dev_runtime 子系统） |
| 架构 | 同步：cudaPointerGetAttributes→2MiB 双对齐前置检查→注册 | **异步：ixcclDevrRegTask{userPtr,userSize,winFlags,outWinDev} 入 comm->devrState.regTaskQueue 队列→group 处理**（ixcclDevrInitOnce+bigSize 状态机） |
| 对称判定 | (baseAddr\|baseSize)&0x1fffff==0 前置硬拒 | `comm->symmetricSupport` 字段运行时探测；不满足→ixcclParamLocalRegister 回退路径；**2MiB 检查未前置**（下沉 devr 任务端，分配语义由 IXDRVmemAllocationProp 承载） |
| 驱动调用 | cudawrap dlsym 函数指针表 | `ixcclCudaMemcpy<ixcclGinGdaki{MemHandle,GPUContext}>`（IXDRVstream_st 直连模板）+ixSetDevice/ixGetErrorString |

**结论：Window API 签名照抄上游，实现被天数重构为 dev_runtime 异步任务队列架构**——UCCL 若以 NV 语义假设"注册即对齐已校验"会在天数上踩坑（回执异步化，错误码时点后移）。

## 6. 待办（2026-11-11 终夜清账）

- [x] ~~gin/enhcompat/ce_coll 上游归属定界~~（§1.1：全为上游 2.28 代件——本地仓 git 史被压扁改用"NV 2.27.3 二进制零串 vs 上游 2.32.3 源码全量"交叉定界）
- [x] ~~上游符号面精确 diff~~（§1.1 归一 diff：NV 零独有+corex 多 27；私有项上游零命中终判；2.29+ 未吸面清单）
- [x] ~~§4 协议常量扫描~~（§4.1-4.4）
- [x] ~~MIX_NV/RBUFF 语义~~（机制级 CONFIRMED 2026-11-11 续夜：CONFIG_ENUM 族全部位于命名空间 **`legacy::env`**（ixcclParamMixNv@0xb8fb8/UseDirect/UseMultiCu/FusedEnable/ForceSyncDisable/UseHighPriorityWarp）——**遗留调度调优面定位钉版**；访问器读 `IXCCL_MIX_NV`@0x18eaa8，INT64_MIN 哨兵默认+全局缓存 0x6f253f0；**零 BL 直接调用**（param 注册表函数指针间接模式）；GetAttribute@0xb90c8（T/W 别名对）分发=**comm 级覆盖表（comm+0x841e0→int64[9]，SetAttribute 写）优先→回落 legacy::env 全局默认**双层机制。MIX_NV 具体调度含义属调度器深水区，遗留低优先；**消费者扫描终判（ADRP 普查 2026-11-12）**：41 处 ADRP 指向参数页 0x6f25000 但零处直接加载 0x3f0——**库内无内部消费者，仅经访问器/GetAttribute 暴露给外部调优器，本构建无激活调度路径**——语义链三层闭合）
- [x] ~~反哺清单终版~~（§7 七条）

## 7. 反哺清单（终版 2026-11-11）

1. UCCL ts provider 的能力探测应以 `pixccl*` 探桩+`ixcclCommWindowRegister` 符号对（symmetric window）定级——与 multivendor skill 四栈表 TS 对称内存 ✅ 一致。
2. 天数私有扩展以 nccl\* 原生前缀导出（Team/Rail/LLA2A/GinBarrier——均为上游 2.28 面）——UCCL 多库共存时这些符号无 ixccl 前缀别名，dlsym 名单要单独维护。
3. DT_NEEDED 含 libstdc++/libm/libgcc_s——海光/沐曦栈没有的额外依赖，容器裁剪时注意。
4. **WindowRegister 语义差异（§5.1）**：天数=异步 devr 任务队列（回执后移、2MiB 契约下沉任务端）vs NV=同步前置检查——UCCL 对称内存适配层在 ts 域不能假设"注册返回即对齐已校验"，错误处理要覆盖异步失败路径。
5. **探桩语义分层**：pixccl\*=T 本体+ixccl\*=W 别名（同地址），但 nccl\* 兼容层 53 个升强符号——UCCL dlsym 探测用 ixccl\* 名（W 语义同 NV nccl\*），透传调用可用 nccl\* 名但注意与真 NCCL 共存时的抢占差异。
6. **互操作 env 前缀**：天数 COMM_ID/SOCKET_IFNAME/IB_GID_INDEX 用 NCCL\_ 原名（未改 IXCCL\_）——UCCL 跨厂商 bootstrap 适配表 ts/nv/hg 同前缀，仅 mx 需 MCCL\_ 映射。
7. 真私有面全集=改名层+IXCCL\_/NCCL\_ 双前缀 env 别名+CONFIG_ENUM 9 项+NCCL_RBUFF+GDAKI 调优 env（GDAKI 本体上游件）——上溯上游 2.29+（CommGrow/Suspend/Resume/Config 变体/Encryption/HostCft）天数未吸，UCCL 若依赖这些新 API 会在 ts 域缺失。
