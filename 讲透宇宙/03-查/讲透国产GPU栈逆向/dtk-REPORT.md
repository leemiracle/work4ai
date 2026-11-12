# 海光 dtk 通信栈逆向报告（rccl 线）

> 第八轮主线（TASK-vendor.md 2026-11-11）。样本源：node18（10.44.11.18, amd64）宿主 `/opt/dtk-26.04.1/`（DTK 26.04.1，2026-08-20 构建）。第七轮工具链线（work/hyhal/）已有 hyptxas/hyfatbin/三层 API 栈素材，本报告专注**通信库线**。

## 0. 样本清单（全 md5 验收 ✅）

| 样本 | 尺寸 | 锚 |
|---|---|---|
| `librccl.so.1.0`（SONAME librccl.so.1） | 173,809,384（md5 b548581f…） | 版本串@0x2254a |
| `rccl.h`（shim）/`rccl-real.h`（真头 1183 行） | 869B / 1183 行 | 版权栈 rccl-real.h:2-4 |
| `libgalaxyhip.so.5` | 12,422,552（md5 ea10d029…） | HIP runtime（hipamd fork "galaxy"） |
| `hy-smi` | 25,966,144 | 混合装载（见 §5） |

UCCL 真机表（provider.cpp:18）：hg dlopen `librccl.so.1`+`libamdhip64.so`（→实际 symlink 到 libgalaxyhip.so.5），prefix `nccl` ✓。

## 1. 血统链（CONFIRMED）

rccl-real.h:2-4 版权栈：

```
Copyright (c) 2015-2021, NVIDIA CORPORATION          ← NCCL 本源
Modifications Copyright (c) 2019-2023 Advanced Micro Devices ← RCCL（AMD，止于 2023）
```

**血统链：NCCL → RCCL(AMD 2.22 系) → 海光 dtk 内部构建**（海光未加自家版权戳——纯内部 fork 消费，工程痕迹在构建串不在版权）：

- 二进制版本串 **`RCCL version : 2.22.3`**@0x2254a——沿用 RCCL 版本序列。
- 构建系统泄露（实锤内部 LLVM fork）：`clang version 17.0.0 (http://10.4.0.1/dcutoolkit/driverruntime/llvm-project.git ff5bf917a679c83afe927af051a20b86fef7b07d)`——**内网 git 10.4.0.1 + dcutoolkit/driverruntime/llvm-project**（commit ff5bf91）。海光全栈用自家 LLVM17 fork 构建。
- 与 RCCL 上游关系：无 Microsoft 跳（沐曦链有、海光无）——海光=AMD RCCL 直接后裔，非 MSCCL 后代。

## 2. ABI 对照（vs NV libnccl.so.2.27.3）

### 2.1 导出面（最大碰撞风险库）

- 共 120 导出：**nccl\* 36 个（原生 nccl 前缀！）+ du\* 族 12 个 + rccl\* 0 个**。
- **rccl.h 类型沿用 nccl 命名**：头文件全部 `ncclResult_t`/`ncclComm_t`（rccl-real.h 通篇，`rcclResult_t` 计 0）——RCCL 传统（保持源码级 NCCL 兼容）。
- **与真 NCCL 同前缀同名共存风险最高**：librccl 导出 ncclAllReduce/ncclBroadcast 等 36 个与 NV libnccl 完全同名的 T 符号——UCCL 多 provider 同进程共存时，必须 RTLD_DEEPBIND+独立 dlopen 句柄（陷阱#2 的海光极端案例）。

### 2.2 海光独有 API 族（vs NV 2.27.3）

| 族 | 符号 | 语义 |
|---|---|---|
| **du\* 第二命名空间** | duNcclAllreduce@0xa46d7d0、duNcclAllToAll@0xa46eb60、duNccl{Allgather,AllToAllv,Bcast,Broadcast,Gather,Recv,Reduce,ReduceScatter,Scatter,Send} 共 12 | **独立数据面 CONFIRMED**（capstone 反汇编调用集对比：du 区间 [0xa46d7d0,0xa46f02a) 共享 helper 0xa475f00→du 核心 0xa47b060 链，与 ncclAllToAll@0xa4e6ba0 的调用集零交叉——非薄封装非别名）；**传输层定性（续夜 CONFIRMED）：du 数据面构建在标准 HIP runtime 之上**——librccl 导入面=纯 hip\*（hipExtLaunchKernel/hipEvent\*/hipDeviceCanAccessPeer/EnablePeerAccess/hipMalloc），零 du\*/hsa\* 导入——与 libgalaxyhip 的 du\* AQL 族是上下两层（rccl-du→hip→galaxyhip-du AQL）；du=DCU Unified 集合层第二入口 |
| RCCL 增量 | ncclAllToAll/ncclAllToAllv（rccl-real.h:697-726 含 p 版声明）+ ncclGather/ncclScatter | RCCL/MSCCL 线增量（NV 2.27.3 无） |
| pnccl\* 探桩 | 头声明 pncclAllToAll:700 等 | 导出待精确核（120 中含若干 p 版） |

### 2.3 缺失面（NV 有/海光无）

ncclCommInitRankScalable / CommShrink / CommWindowRegister/Deregister / ResetDebugInit——对称内存族缺 ✓（skill 表 HG 一致）；CommRegister/CommDeregister 存在与否待精核（2.22 基线）。

## 3. 能力探测面

- **du\* 族=能力旁路**：海光私有能力（DU 直达路径）不走 nccl\* 演进——跨厂商统一层若只对齐 nccl\* 面会漏掉 du\* 快路径（KCCL/UCCL 反哺点）。
- **无 p 探桩**（pnccl\* 头声明 rccl-real.h:700/二进制 0 个）+ **全强符号**（36 nccl\*+12 du\* 全 T 零 W，对照 NV 37 对 T/W 同地址别名机制）——AMD 系通病，与沐曦 pmccl 同病；共存必须 RTLD_DEEPBIND。
- kernel 框架：`ncclDevFunc_AllGather_RING_LL128_Sum_i8`/`ncclDevFunc_AllReduce_TREE_SIMPLE_*`/`ncclDevFunc_Reduce_RING_SIMPLE_MinMax_u8`（+**bf8** 类型）——**NCCL dev-kernel 表框架完整保留**（与 corex 2.28.9 导出的 ncclDevKernelCount 族同框架，版本更早）。
- tuning 串：`tuning=4,ll128Enabled=1,baseBw=161.4`——拓扑调优模型参数内嵌。

## 4. 协议常量与私有面（RCCL\_ env 41 个）

海光私有亮点（vs AMD 上游 RCCL 的增量，全 [file+偏移] 锚）：
- **XHCL 定性 CONFIRMED（内部符号直供）**：`RCCL_COLL_XHCL_CHANNEL_NUM`@0x243b7 对应参数访问器 `rcclParamCollXHCLChannelNum`@0xa523f50（t）+ `rcclParamP2pXHCLChannelNum`@0xa523f90 + 双互斥锁@0xa61c0e0/0xa61c108；**XHCL 实为 ROCm SMI/HSA 扩展的海光互联链路查询族**——未定义导入 `rsmi_dev_xhcl_link_{number,remote_bdfid,remote_dev_type,state}_get`（来自 librocm_smi64）+ `rocm_hsa_ext_get_xhcl_link_count(hsa_agent,hsa_agent,uint*)`@0xa4edca0 + `pfn_hsa_ext_get_xhcl_link_count`@0xa617c20——**链路数/对端 BDF/对端类型/状态四元查询=topo 检测专用**；Coll/P2P 两组通道数参数=走 XHCL 链路的通道调优。
- **ROME 定性 CONFIRMED**：`RCCL_DUMP_ROME_MODEL_FILE`@0x1972b（消费串@0x2281a）——内部符号 `rome_models.cc`（_GLOBAL__sub_I）+ `parseRome4P2HP(ncclTopoSystem*,ncclTopoGraph*,char const*)`@0xa4af7e0 + `find_gpu_hives`/`checkAlltoallWidth`/`permuteGpuIds`/`permuteNetIds` + **内嵌数据模型 `rome_model_22`@0xa52da40 / `rome_model_23`@0xa546d10 两版**——ROME=海光按机型预置的整机拓扑画像系统（模型版本 22/23 与 DTK 代际对应），dump env 为可观测后门。
- **`RCCL_GDR_WRITE_USE_XDP_ENABLE`**@0x194d8——**XDP（eXpress Data Path）**承载 GDR 写路径——内核旁路网络在 RCCL 数据面的应用（AMD 上游无）。
- `RCCL_ENABLE_INTRANET`/`RCCL_INTRANET_THRESHOLD`——内网优化路径阈值。
- `RCCL_DISABLE_RAIL_TREES`/`RCCL_ALL_TO_ALL_PIVOT_ENABLE`——rail 树+pivot a2a（与沐曦 AllToAllPivot 概念趋同，跨厂商收敛点）。
- `RCCL_LL128_FORCE_ENABLE`（LL128 保留）。
- NVLSTree 串在场（上游遗留）。

DT_NEEDED：libgalaxyhip.so.5 + **librocm_smi64.so.2** + pthread/m/rt/dl/stdc++/gcc_s——纯 ROCm 系运行时栈（UCCL 表 hg runtime=libamdhip64.so ✓ 同物异名）。

**内嵌 device 容器层（任务书动作 6 CONFIRMED）**：`.hip_fatbin` 节 0xa419328=**172MB（173MB 库的 99.2%）**+`.hipFatBinSegment` 48B（**HIPF v1×2 条目，第七轮 HIPF 24B 结论在通信库同样验证**）；**ClangOffloadBundle v6**（对照沐曦 v7），成员={host-x86_64, **hipv4-amdgcn-amd-amdhsa--gfx{906,926,928,936,938}**}——**五 gfx 架构全 AOT 分发**（与第七轮 hyptxas 输出表 gfx906/926/928/936/938 精确一致）；零运行时编译器依赖（DT_NEEDED 无 compiler 库）——对照沐曦 bitcode-JIT 的分发模式两极。

## 4.7 DTK 25.04.2→26.04.1 年度演进（镜像 vs 宿主双样本 diff，2026-11-11）

- **版本串冻结**：两代均 "RCCL version : 2.22.3"——海光在 2.22.3 基线上内部演进不升版本号（129MB(2025-10)→173MB(2026-08)，+44MB/+34%）。
- **导出面清洗**：25.04.2 导出 353（C++ STL 泄漏严重，同沐曦病）→ 26.04.1 导出 120（修剪到位，对齐 NV 的干净面）。
- **内核 ABI 内变**：`ncclDevKernel_Generic<ncclDevKernelArgsStorage<4096>>`→`<1024>`（内核参数存储 4096B→1024B）。
- **26.04 新 env 仅 2 个**：`RCCL_GDR_WRITE_USE_XDP_ENABLE`（**XDP GDR 写=26.04 新特性**）+ `RCCL_P2P_BATCH_ENABLE`。

## 5. 与第七轮工具链线互证

- 三层栈（220KB libcuda shim→libgalaxyhip→HSA）在通信域的投影：librccl 直依赖 galaxyhip，不经过 CUDA shim 层。
- hy-smi 25MB（第七轮记录品牌词 HCU）与 librocm_smi64 同源。

## 6. 待办（2026-11-11 终夜清账）

- [x] ~~pnccl\* 精确清单~~（120 导出中 pnccl\*=0；头声明 rccl-real.h:700 二进制无）
- [x] ~~duNccl\* 调用关系~~（§2.2：独立数据面 CONFIRMED——capstone 调用集对比零交叉）
- [x] ~~XHCL/ROME 深挖~~（§4：XHCL=rsmi 链路查询族四 API+参数访问器定位；ROME=rome_models.cc+model_22/23 内嵌——内部符号直供）
- [x] ~~dtk-25.04 镜像对照~~（§4.7：版本冻结+导出清洗 353→120+内核参数槽 4096→1024+XDP 26.04 新增）
- [x] ~~反哺清单终版化~~（§7 七条）

## 7. 反哺 UCCL/KCCL（终版 2026-11-11）

1. **hg provider 探测**：du\* 12 符号族应纳入能力位图（**独立数据面已实锤**：与 nccl\* 调用集零交叉——不是别名不是封装，是平行实现，语义兼容性需逐 API 验证）；XHCL 通道数 env（Coll/P2P 双参数）可作海光特化调优输入。
2. 同名碰撞极值：librccl 与 libnccl 36 符号全同名——UCCL 共存测试矩阵必须加"hg+nv 双载互踩"用例（RTLD_DEEPBIND 回归）。
3. libamdhip64.so 只是 symlink 面（真身 libgalaxyhip.so.5）——UCCL runtime 库探测失败时回退试 galaxyhip 名。
4. ROME model dump 是海光拓扑调优的可观测性后门（性能分析素材；rome_model_22/23 两版内嵌对应 DTK 代际）。
5. **版本冻结陷阱**：25.04.2 与 26.04.1 版本串同为 2.22.3 但导出面 353→120/内核参数槽 4096→1024B/XDP 新增——**不能用版本串判海光能力，必须符号探测**（对 multivendor skill"按符号存在性定级"原则的最强背书）。
6. **互操作 env 前缀**：海光用 NCCL\_ 原名（COMM_ID/SOCKET_IFNAME/IB_GID_INDEX）——与 nv/ts 同前缀，UCCL 适配表无需 hg 专属行。
7. 拓扑查询链路：XHCL=rsmi_dev_xhcl_link_* 四元查询（链路数/对端 BDF/类型/状态）——UCCL 混合域拓扑感知可复用该 API 族（经 librocm_smi64）。
