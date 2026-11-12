# 沐曦 metax 通信栈逆向报告（mccl 线）

> 第八轮主线（TASK-vendor.md 2026-11-11）。样本源：node14 镜像 `cr.metax-tech.com/public-init/minimax-h3/sglang-0.5.14-minimax-h3-0801:latest`（image id a93d0eadb7f1）内 `/opt/maca-3.8.2.2/`（SDK 3.8.2.2，driver 3.8.2.22）。镜像平台 amd64（宿主 arm64 不可 run）→ 全静态分析（行为学 --help 不可得，如实记录）。
> 第七轮工具链线（work/metax/notes.md）已有 maca 目录布局/mxcc/cu-bridge 素材，本报告专注**通信库线**。

## 0. 样本清单（全 md5 验收 ✅）

| 样本 | 尺寸 | 锚 |
|---|---|---|
| `libmccl.so` | 815,304,744（md5 3779f679…，**四库最大**，超 NV 411MB 一倍） | 版本串@0x2dda20 |
| `libmcruntime.so` | 76,480,776（md5 6fbd293a…） | UCCL mx runtime 线 |
| `libmxshmem_host.so` | 46,470,184（md5 0eb3cae5…） | mxshmem（NVSHMEM 对应物） |
| `mccl.h` | 653 行（真 ABI 头） | 版权栈:1-5 |
| `cu-bridge-nccl.h` | 225 行（CUDA 兼容桥头） | |
| `driver/libmxsml.so.2.3.4`（+libmxsml.a） | 2.57MB | mxdriver 层（NVML 对应=MXSML） |

UCCL 真机表对照（provider.cpp:16）：mx dlopen `libmccl.so`+`libmcruntime.so`，prefix `mccl` ✓。

## 1. 血统链（CONFIRMED，头文件版权栈一行钉死）

mccl.h:1-5 版权栈注释 = 完整血统链：

```
Copyright (c) 2015-2021, NVIDIA CORPORATION            ← NCCL 本源
Modifications Copyright (c) 2019-2023 Advanced Micro Devices   ← RCCL（AMD）
Modifications Copyright (c) Microsoft Corporation (MIT)        ← MSCCL（含 du/direct 贡献）
2026 - Modified by MetaX Integrated Circuits (Shanghai)        ← 沐曦 2026 年改动戳
```

**血统链：NCCL → RCCL(AMD) → MSCCL(Microsoft) → MCCL(沐曦)**——任务书预判（KCCL mccl.h 模式推广）100% 命中。

辅证：
- `#define ENABLE_HIP_TO_MACA_ADAPTOR 1`（mccl.h:8）——HIP→MACA 适配层总开关，沐曦从 HIP 生态平移。
- 错误码 `mcclUnhandledMacaError=1`（mccl.h:40 附近）——CUDA→Maca 改名痕迹。
- 二进制版本串 `MCCL version 2.16.5` @0x2dda20 / `MCCL version 2.16.5 compiled with MACA` @0x2e7c85——**MCCL 版本号沿用 RCCL 系版本序列（2.16.5），非 NCCL 上游同代**（本镜像 2.16.5；UCCL 注释记录另有 2.30.4 真头 2026-11-07 核对——集群在用版本比镜像新，两代并存）。
- `MCCL_BFLOAT16/GATHER_SCATTER/ALLTOALLV/MULTIRANKPERGPU`（mccl.h:27-30）特性宏=RCCL/MSCCL 增量特性的编译开关。

## 2. ABI 对照（vs NV libnccl.so.2.27.3，mccl→nccl 归一）

### 2.1 导出面

- 共 208 导出：**mccl\* 43 个、pmccl\* 0 个、nccl\* 兼容 0 个**；其余 165 个为 C++ STL 模板符号（libstdc++ hashtable/string 实例化外泄——未加 visibility hidden，符号污染面，多库共存时 RTLD_DEEPBIND 仍必要）。
- **头/二进制 ABI 失配实锤**：mccl.h 声明 `pmcclRedOpCreatePreMulSum/pmcclAllToAll/pmcclAllToAllv…`（:328/:554/:577），但二进制 **pmccl\* 零导出**（nm -D 验证）——dlsym("pmcclX") 必返 NULL。UCCL/KCCL 探测逻辑禁止依赖 p 前缀探桩（沐曦无探桩语义）。
- `mcclCommSplit` 导出=1 @0x5be10（T）——**与 multivendor skill 四栈表"MX CommSplit ❌"冲突**：该表为 UCCL 真机实证（真机集群 libmccl 可能更老/裁剪版），本镜像 2.16.5 二进制有符号。建议 UCCL 线复核真机 dlopen 到的 mccl 实际路径与版本。
- `mcclCommRegister` 导出=0（NV/TS 有）——无用户 buffer 注册族 ✓（与 skill 表一致）。

### 2.2 沐曦独有 API 族（vs NV 2.27.3）

| 族 | 符号 | 语义 |
|---|---|---|
| **Ext 族** | mcclAllReduceExt/AllGatherExt/ReduceScatterExt/SendExt/RecvExt/AllToAllExt/AllToAllvExt | 带扩展参数变体（异步/补充语义，头文件 :549-601 全签名） |
| **AllToAll 家族** | mcclAllToAll@0xf3000、mcclAllToAllv@0xf38f0、mcclAllToAlld@0xf4670（+各 Ext/p 版） | RCCL/MSCCL 血统增量；**AllToAlld=指针数组语义**（mccl.h:593-601：`sendbuff[]/recvbuff[]` 每 peer 独立缓冲、无 displs、counts 单位=元素——与 AllToAllv 连续缓冲+displs 数组互补）；**Ext 与非 Ext 签名逐参相同**（:549-581）——Ext 是内部实现路径变体（非 ABI 参数差异） |
| 多卡多进程 | mcclCommInitRankMulti | 单进程多 communicator 初始化 |
| 设备查询 | mcclCommMcDevice | MACA 设备号查询（对应 ncclCommCuDevice 但沐曦缺失后者） |

mcclAllToAllv 签名（mccl.h:569-）：`(sendbuff, const size_t sendcounts[], const size_t sdispls[], recvbuff, const size_t recvcounts[], const size_t rdispls[], datatype, comm, stream)`——与 UCCL provider.h alltoallv 注释（counts/displs 均 size_t 数组）一致 ✓。

### 2.3 缺失面（NV 有/沐曦无）

ncclCommCuDevice / CommDeregister / CommRegister / CommInitRankScalable / CommShrink / CommWindowRegister/Deregister / GroupSimulateEnd / ResetDebugInit——对称内存族全缺 ✓（skill 表一致）。

## 3. 能力探测面

- **无 p 探桩**（pmccl\* 二进制缺失）——能力探测只能靠符号存在性（mcclAllToAllv 等），不能靠"调用探桩无副作用"模式。
- **T/W 机制缺位**（43 mccl\* 全 T 零 weak，对照 NV 2.27.3 的 37 对 pnccl(T)/nccl(W) 同地址别名）——AMD 系（RCCL/MCCL）通病：头文件抄了 p 声明、二进制无实现。全强符号→多库共存按加载序解析，RTLD_DEEPBIND 必须保留。
- mccl.h 版本宏 `MCCL_VERSION_CODE 21605`（:23）可编译期判别；运行时 `mcclGetVersion`。
- mxshmem（libmxshmem_host.so 46MB + device .bc/.a）=对称内存能力由**独立库**承载（NVSHMEM 对应物），不在 mccl 内——跨厂商对称内存快路径应探测 libmxshmem 而非 libmccl 符号。

## 4. 协议常量与私有面

- **201 个 MCCL\_* env 旋钮**（四库第二多）。私有亮点：`MCCL_CUBE_RINGS`@0x2e5714（立方环拓扑——沐曦多维互联拓扑算法）、`MCCL_CGA_CLUSTER_SIZE`（CGA 簇概念在 MACA 的对应物）、`MCCL_LL128_FORCE_ENABLE`/`MCCL_LL128_BUFFSIZE`（LL128 保留可用）。
- 协议名串：`LL128`/`Simple` + kernel 命名 `SendRecvRingSimpleSum_i8`@0x2dcc28、**`AllToAllPivotRingSimpleSum_i8`**@0x2dcc28 区段（pivot 中枢法 all-to-all——沐曦私有算法族）。
- **算法调度表层（静态符号 14574 个直供，2026-11-11 深挖）**：`mcclFC_<Coll>_<ALGO>_<PROTO>` 函数表族——AllToAll×{**EOAM16**, EOAM16_LL, EOAM16_R, **FC2**, FC2_DIRECT, CUBE_HFC32} + AllReduce/AllGather/ReduceScatter×CUBE_HFC32（d 符号@0x30a40000 区段）+ device stub `__device_stub__mcclkernel_AllToAll_CUBE_HFC32_int8_t`（HIP 风格 stub 命名）——**算法×协议二维调度表在数据段以函数表实存**。
- **拓扑层 CONFIRMED**：`parseDragonfly16CubeRing(mcclTopoSystem*,mcclTopoGraph*)`@0xc8f90 + `mcclParamDisableReverseCubeRing`——**沐曦互联拓扑=Dragonfly16**，MCCL_CUBE_RINGS env 即此（立方环=dragonfly 维度环）；ReverseCubeRing 可禁（拓扑对称性调优）。
- 互联面：`mcDeviceGetMetaxLinkPortInfo`（MetaxLink 端口拓扑 API）、CXL9 串（CXL 语义）。
- DT_NEEDED（ABI 陷阱#5 实锤）：`libmcToolsExt.so`+`libmccompiler.so`+`libmcruntime.so`+`libmaca_mathlib_host.so` 四个 MACA 私有库——非 MACA 主机 dlopen 直接失败；UCCL 需先 RTLD_GLOBAL 加载 runtime 链或 dlopen 全路径。
- **内嵌 device 容器层（任务书动作 6 CONFIRMED）**：`.mc_fatbin` 节 0x2fecc055=**803MB（815MB 库的 98.6%）**+`.mcFatBinSegment` 12KB；**ClangOffloadBundle v7**（对照海光 v6——LLVM fork 版本差 19.1.3 vs 17 的容器代际投影），成员={host-x86_64, **xcore1000-bc/xcore1500-bc/xcore1600-bc**}——**device 以 LLVM bitcode 分发（JIT 模式），xcore1500 为第七轮架构表（1000-2000）中间代实证**；**这是 DT_NEEDED 含 libmccompiler.so 的根因：运行时编译器依赖不是设计冗余，是 device 分发模式决定的**（对照：海光五架构 AOT→零编译器依赖；天数 127 单元 AOT→同零）。
- 协议层补充：JIT 意味着 mccl 首次装载有编译延迟——UCCL 性能门测试要预热（已含）。
- 编译器：mxcc 1.0.0 (890c70f3aa)@0x308565b1（内嵌 clang 系版本串，与第七轮 mxcc=LLVM 19.1.3 fork 结论互证）。

## 5. 与 KCCL 仓对照

/usr-data/data2/kylin/kccl 的 mccl.h（KCCL 轮血统链结论）与本镜像 mccl.h 同构同链——KCCL 封装的 libmccl 与本样本同族；版本差（KCCL 真机 2.16.5 线 vs UCCL 注释 2.30.4 头）待 KCCL 线复核。

## 6. 待办（2026-11-11 终夜清账）

- [x] ~~AllToAlld 全签名+指针数组语义~~（§2.2：sendbuff[]/recvbuff[] 每 peer 独立缓冲无 displs）
- [x] ~~Ext 族扩展参数差异~~（§2.2：签名逐参相同=内部路径变体，非 ABI 差异）
- [x] ~~AllToAllPivot 算法面~~（§4：mcclFC_Algo_Proto 调度表+Dragonfly16 拓扑符号定位；kernel 级反汇编属私有 ISA 深水区按任务书§6 不硬啃）
- [x] ~~反哺清单终版化~~（§7 七条）

## 7. 反哺 UCCL/KCCL（终版 2026-11-11）

1. **mx provider 探测逻辑修正**：pmccl\* 探桩二进制缺失——能力探测改符号存在性+版本号双判；mcclCommSplit 符号在 2.16.5 已存在，UCCL caps 表 MX CommSplit 应按版本条件化。
2. DT_NEEDED 四私有库——UCCL mx 加载器保持"先 runtime 后 comm"顺序的同时，建议 dlopen 全路径（/opt/maca*/lib/）而非裸 soname。
3. AllToAllv 真签名确认（size_t counts/displs）——provider.h 现签名正确，勿回退；**AllToAlld 补充**：sendbuff[]/recvbuff[] 指针数组语义（每 peer 独立缓冲、无 displs）——若 UCCL 要暴露 a2a 快路径，Alld 免 displs 计算但有 N 指针入参。
4. 符号污染：libmccl 外泄 165 个 C++ STL 导出——共存场景 RTLD_DEEPBIND 必须保留（陷阱#2）。
5. **对称内存走独立库**：mxshmem（libmxshmem_host.so+device .bc）承载——UCCL mx 域对称内存探测改探 libmxshmem 而非 libmccl 符号（mccl 内零 Window 族）。
6. **互操作 env 前缀映射**：MX_COMM_ID/MX_SOCKET_IFNAME/MX_IB_GID_INDEX（MCCL\_ 前缀）——四库中唯一改 bootstrap 寻址 env 前缀者，UCCL 跨厂商 bootstrap 适配表需 mx 专属映射行。
7. **拓扑面提示**：parseDragonfly16CubeRing+MCCL_CUBE_RINGS——沐曦机内拓扑=dragonfly 立方环，UCCL 混合域算法若按 NV 双平面/树假设调优会在 mx 域失配；算法表 mcclFC_*（EOAM16/FC2/CUBE_HFC32）可作调优档位参考。
