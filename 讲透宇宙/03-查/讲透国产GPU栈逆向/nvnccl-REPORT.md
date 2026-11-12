# NVIDIA libnccl 2.27.3 主机侧深挖报告（对照线·Ghidra 线）

> 第八轮（2026-11-11 夜）。样本：samples/libnccl.so.2.27.3（411MB，节点 13 CUDA 12.9 toolkit）。
> Ghidra 12.2 headless（节点 13 /root/ghidra-proj3 nccl-re 工程，JDK25，40min 全量分析完成）。
> 产物：work/nvnccl/nccl-decomp-s1.txt（541 行）+ nccl-decomp-s2.txt（431 行）。
> 角色定位（TASK-vendor.md）：为国产三栈血统对照提供 NV 侧锚——四库导出面 diff 表已落 reports/corex-REPORT.md §4.5/§4.6，本报告补充机制层。

## 1. pnccl\* 探桩机制二进制级定性（CONFIRMED）

- dynsym 级：`pncclCommWindowRegister@0x1011e0 (GLOBAL FUNC)` ≡ `ncclCommWindowRegister@0x1011e0 (WEAK FUNC)`——**同地址别名对，p 前缀=GLOBAL 强符号本体、无前缀=WEAK 别名**，37 对全如此（nm/readelf 双证）。
- **pncclAllReduce@0x58b40 反编译=完整集体操作实现**（group enqueue+`__cxa_guard` 静态初始化+cudawrap 惰性符号表），非薄探桩。
- 语义定论：**"p 探桩"≠独立探测函数，而是强符号命名通道**——dlopen 场景 dlsym("pncclX") 永得本库实现（weak 名可被进程内其他强定义抢占）；这是 NCCL 2.27 文档"probe-safety"的二进制机制。
- 对照结论（回灌 multivendor-gpu-comms skill 四栈表）：corex 保留机制改名（pixccl GLOBAL/ixccl WEAK@0x67178 同址；nccl\* 兼容层 53 个反而升 GLOBAL）；metax/dtk 完全无此机制（全 GLOBAL 强符号）。

## 2. ncclGetVersion（CONFIRMED）+ 同版本双构建形态与 CET/IBT 真相（2026-11-12 补）

`*version = 0x58af`（=22703=2×10000+27×100+3）硬编码常量@0x1708b0——无运行时计算；null 出参→返回 ncclInvalidValue(4)。

**同版本双构建形态实证**（aidp-vllm-nv-v024 镜像双样本，均 2.28.9+cuda13.0）：

| 构建 | pncclGetVersion 绑定/地址 | 首字节 | 判定 |
|---|---|---|---|
| sys 版（usr/lib，189MB） | T@0x98670 ≡ W ncclGetVersion 同址 | `f30f1efa` ENDBR✓ | -fcf-protection=full |
| **pip 版（nvidia-nccl wheel，218MB）** | T@0x91c4b ≡ W 同址 | `4885ff` **无 ENDBR✗** | **wheel 构建缺 CET 保护** |

- pip 版桩体解码（16B 全解）：`test rdi,rdi; je+9; mov dword[rdi],0x5919(=22809); xor eax,eax; ret`——**完整 GetVersion 实现（版本码内联），非薄桩**。
- **"弱桩"真相终判**：T/W 同地址别名结构三代稳定（2.27.3/2.28.9 sys+pip）；UCCL 开发线真机 SIGSEGV 139 的机制=**wheel 构建无 ENDBR × CET/IBT 强制环境（间接调用无 ENDBR 目标→#CP→SIGSEGV）**，非 NCCL 机制变化，且**由分发渠道决定**（apt/deb 有保护、wheel 无）。
- ⚠️ **UCCL 修复预警（实锤升级 2026-11-12）**：nccl_family.cpp:23-40 用 p 探桩面替代普通面——**2.29.7 x86_64 wheel（开发线真机同渠道，PyPI 下载实测）pncclGetVersion(T)@0xa8f3f ≡ ncclGetVersion(W) 同地址且同无 ENDBR**（桩体=完整实现版本码 0x597b=22907 内联；pncclAllReduce(T)≡ncclAllReduce(W)@0x74ea0 同样）——**换 p 面在 IBT 强制机器上不能解决 #CP 崩溃**（p/普通面是同一地址同一函数体）。若开发线换 p 面后真机不再崩，则原 SIGSEGV 根因可能并非 IBT（如双 libnccl 共存下 dlsym 句柄错配），建议复核。稳妥方案=dlsym 后查首字节 `f3 0f 1e fa`，无 ENDBR 且需间接调用时走直连或 IBT=Permissive。**wheel 全版本线（2.28.9/2.29.7/2.30.7 aarch64+x86_64）无 ENDBR，sys/deb 带保护——分发渠道决定 CET 兼容性定型**。源码侧互证：上游 Makefile/CMake 零 cf-protection 强制+pnccl\* 为真实独立函数声明（nccl.h.in:263-284，非宏别名）。样本归档 samples/nv-pip297-libnccl.so.2.29.7（400MB）。

## 3. ncclCommWindowRegister/Deregister 对称窗口主机侧路径（CONFIRMED，源码级锚）

反编译全量（431 行，nccl-decomp-s2.txt）：

1. **上游源码锚**：日志格式串保留 `"register/register.cc"` + 行号 {0x98,0xcf,0xd5,0xd7,0xdd,0xe0,0xf6}——NCCL 上游 `src/register/register.cc`（用户缓冲注册子系统）原样编译。
2. **对称注册硬语义**（register.cc:0xdd 错误串全文）："buffer %p (baseAddr %p align %d) size %zu (baseSize %ld align %d) does not satisfy symmetric registration requirements"——判定式 `(baseAddr | baseSize) & 0x1fffff) == 0`，即 **baseAddr 与 baseSize 双 2MiB 对齐**（对称内存窗口的物理对齐契约，直连 GPU 大页）。**UCCL/跨厂商 window register 适配的硬前提**：沐曦/海光无 Window API，若 UCCL 用自研对称内存模拟此契约，须复制 2MiB 对齐分配。
3. env 开关 `NCCL_LOCAL_REGISTER`（默认 0x8000…0000=UNDEF 语义，FUN_001c5260 参数解析器）。
4. CUDA 调用走**函数指针表**（`(*DAT_189839a0)(&attrs,…)` 模式=cudawrap.cc 的 dlsym 惰性解析）——nvcc 不静态链 cudart，与 DT_NEEDED 无 libcudart 一致（对照 corex DT_NEEDED 硬依赖 libcudart.so.10.2——天数 fork 把 cudawrap 换成了直接链接，ABI 加载顺序差异点）。
5. cudaPointerGetAttributes 取 baseAddr/baseSize 后走 winFlags（param_5，NCCL_WIN_COLL_SYMMETRIC=0x01）分支。

## 4. NV 2.27.3 源码树路径普查（strings 全扫，国产栈 diff 的上游底图）

| 子系统 | 路径（.cc 计 1 串/处） |
|---|---|
| transport/ | shm、nvls、net_socket、net_ib、net、generic、coll_net |
| register/ | register、coll_reg |
| ras/ | rasnet、ras、peers、**collectives**、client_support |
| plugin/ | tuner、profiler、net |
| misc/ | utils、strongstream、socket |

**对 corex ar 成员表的解码钥匙**：ar 重复的 `collectives.o`=src/collectives.cc 与 ras/collectives.cc 双物；`coll_reg.o/sendrecv_reg.o`=register/ 子系统——corex ar 238 成员与 NV 2.27.3 路径图+2.28 新增（gin/、sym_kernels、devRuntime 表）完全对号，**零无法归位成员**——血统链判定（vanilla fork）的最后一环闭合。

2.27.3 无：gin/（GIN 系 2.28+）、sym_kernels（对称内核）、net_vN/tuner_vN/profiler_vN 版本化插件目录（2.28 起插件 ABI 多版本并存）。

## 5. 四库对照锚速查（详见 corex-REPORT §4.5/§4.6）

- 版本常量：NV=0x58af@0x1708b0；corex=22809（头）/2.28.9 串@0x189a48；mx=21605；hg=2.22.3 串@0x2254a。
- 探桩：NV 37 对 T/W；TS 改名保留+兼容层升强；MX/HG 无。
- 对称窗口：NV 2.27.3 已有符号+完整实现；TS 同（+Symk 内省族）；MX/HG 无。
- dt kd du/Ext/AllToAll 族：MX/HG 有 NV 无（AMD 线增量）；TS 有（2.28 上游新面）。

## 5.1 ncclMemAlloc 精读（CONFIRMED，decomp s1:340-470）

- 源锚 `"allocator.cc"` 行号 {0x1e,0x31,0x3b,0x4f,0x5b}（上游 src/allocator.cc）。
- 惰性 cudawrap：`PTR_FUN_1896b930(libHdl,"ncclMemAlloc")` 按名取驱动符号（cuGetProcAddress 风格带版本参数）——与 WindowRegister 同一间接调用模式。
- **分配语义**：`size' = ((granularity-1)+size) - ((granularity-1)+size) % granularity`——**按驱动报告的分配粒度上取整**（头文件"actual size might be larger"的机制本体）；粒度经设备属性 0x80/0x6e 查询。
- 双路径：环境探测 FUN_001bfe60() 不满足→回退 FUN_00287600（经典 cudaMalloc 路径）；满足→cuMemAlloc 属性化分配+错误码 800/801 降级重试（memPool 类型 9→1 退化）。
- 多卡 peer 循环（FUN_00292990≈cudaDeviceCanAccessPeer）——分配器在所有可达设备建立映射（对称内存前提）。

## 6. proxy/bootstrap 定位与跨厂商互操作约定（CONFIRMED，2026-11-11 深挖）

- **代码簇定位（字节扫描 rip-relative lea）**：NV 2.27.3 内 `bootstrap.cc` 串被 157 处 lea 引用（簇首 0x45de5→socketRecv@FUN_00145d80 ghidra 实证）、`proxy.cc` 160 处（簇 0x8238e→FUN_00182160）——bootstrap 子系统≈[0x45000,0x48000)、proxy≈[0x82000,0x85000)（+0x100000 为 ghidra 基址）。工具：本地 rip-lea 扫描脚本（本轮即席，原理记 tools/xdis.py 同目录）。
- **bootstrap 寻址约定（上游源码权威锚 src/bootstrap.cc:112-117,436-446）**：`NCCL_COMM_ID` 格式 `<ipv4>:<port>` / `[<ipv6>]:<port>` / `<hostname>:<port>`；root 监听临时端口、其余 rank 连 COMM_ID；`NCCL_SOCKET_IFNAME` 选网卡。
- **GID 约定**：`NCCL_IB_GID_INDEX`（IB GID 索引选择，四库串全在场）。
- **跨厂商互操作三元组验证**：COMM_ID+SOCKET_IFNAME+IB_GID_INDEX 四库语义同构——**NV/TS/HG 用 NCCL\_ 原名，MX 改 MCCL\_ 前缀**（MCCL_COMM_ID/MCCL_SOCKET_IFNAME/MCCL_IB_GID_INDEX）。UCCL 跨厂商 bootstrap 互通只需 env 前缀适配表，无需协议翻译（multivendor-gpu-comms skill 回灌点）。
- 对照 corex 静态符号（4328 个，DWARF 未 strip）：proxy/bootstrap 子系统全图直读——`ixcclProxyInit(comm,ixcclSocket*,ixcclSocketAddress*,ulong)`/`ixcclProxyPost(ixcclProxyOpsPool,int,int)`/`ixcclProxyStart/Stop`+`bootstrap{Init,Send,Recv,Abort,Close,Split,Barrier,NetInit}`+类型 `ixcclNetAttr_v11_t`（net 插件 v11 属性对应 net_v11.o）——与 NV 2.27.3 函数簇一一对应，proxy/bootstrap 架构 fork 零改动证据再+1。

## 7. 待办（Ghidra 线后续）

- [x] ~~ncclMemAlloc 全文精读~~（§5.1）
- [x] ~~proxy.cc/bootstrap.cc 定位+端口/GID 约定~~（§6）
- [x] ~~proxy 线程模型深挖~~（双层 CONFIRMED 终章：①FUN_00182160=**64×512B op 槽位暂存队列**（plan ~40 字段复制+组内一致性校验+控制块@+0x8000）；②**主循环 ixcclProxyProgress@0xa0718**（corex DWARF 版反编译=NV 同源模型）：**sched_yield 自旋等 op + op 链表 vtable 进度回调（op+0x4000 函数指针）+ 双链摘除（next@+0x40d0/peer@+0x40d8）**；线程名 **"NCCL Progress%2d"（未改名！）**；profiler v5 埋点闭环（ixcclProfilerProxyCtrlIdle 事件↔libixsysnccl 适配器）；**`NCCL_PROXY_DUMP_SIGNAL` env+信号 dump 后门**（ixcclDumpProxyState+全局 ixcclLastProxyState——性能调试可观测性入口）；源锚 proxy.cc:{0x3a8,0x3ad,0x3d7}）
- [x] ~~corex WindowRegister 对照~~（corex-REPORT §5.1——异步 devr 任务队列架构 vs NV 同步前置检查）

## 7. 工具资产钉版

- tools/ghidra_decomp_force.java（强制建函数反编译；Ghidra 12.2 坑：SourceType 无 CUSTOM/USER 静态引用编译失败、CreateFunctionCmd 构造器变体不可用→**用 GhidraScript 内建 createFunction(a,null)**）
- 节点 13 专属脚本目录 /root/ghscripts（/root 有杂散 java 会连坐编译）；ghidra 工程 /root/ghidra-proj3(nccl-re) 已全量分析可 -process 复用
- **Ghidra x86-64 so 基址 0x100000 坑再现**（第七轮钉版第二犯）：nm 地址→ghidra 地址必须 +0x100000，且十六进制加法要仔细（本轮 0x1011e0+0x100000 误算成 0x1111e0 浪费两轮）
