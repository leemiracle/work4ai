# 11 · vGPU 虚拟化线：11443 行 rpc.c 的版本化 RPC 与 hypervisor 四家探测

> 仓库 @ 615.71.09。本篇覆盖 `src/nvidia/src/kernel/vgpu/`（七文件约 17,500 行）与 `src/nvidia/src/kernel/virtualization/hypervisor/`（核心 368 行 + 四家各 ~100 行）。

## 一、角色定位：guest 内 RM 的"对外使馆"与虚拟化感知层

vGPU 架构下，guest 虚拟机里的驱动（就是本仓编译出的 nvidia.ko）并不直接拥有 GPU——真实的资源管理在 host 侧（物理机 RM 或 GSP 固件内）。guest RM 每遇需要真实硬件动作的 API（分配显存、建通道、提交 engine 作业），就把整个 RM API 调用**打包成 RPC 消息**转发出去；本篇的 `rpc.c`（11443 行）就是这条转发通道的 guest 侧全部实现，连同配套的 `rpcstructurecopy.c`（4298 行，消息结构在版本间的字段迁移拷贝）。

`virtualization/hypervisor/` 则回答另一个前置问题："我现在跑在谁家虚拟机里？"四家（Xen/KVM/Hyper-V/VMware）各一个小适配文件，向 RM 提供 P2P 支持判定、child partition 探测等差异化行为。两块代码合起来构成驱动的"虚拟化人格"：先识别宿主，再以 vGPU 身份对外通信。

版本骨架在 `inc/kernel/vgpu/vgpu_version.h`：RPC 版本号是 32 位字段（:28-29 `NV_RPC_VERSION_NUMBER_MAJOR 31:24 / MINOR 23:16`），当前驱动 ABI 对应 `VGX_MAJOR_VERSION_NUMBER 0x2F`（:33），并保留历史 vGPU 大版本锚点（17.0=0x25、18.0=0x29、19.0=0x2B，:36-39）——**guest 驱动与 host vGPU 软件版本必须协商出共同 RPC 版本**才能工作，这是 vGPU 兼容矩阵的代码根源。

## 二、内部结构

**vgpu/ 七文件**：

| 文件 | 行数 | 职责 |
|---|---|---|
| rpc.c | 11443 | RPC 核心：消息收发、全部 RM API 的 RPC 封装（版本化函数族）、共享内存基础设施、vGPU 管理面 |
| rpcstructurecopy.c | 4298 | 消息结构体跨版本深拷贝（ipVersion 分派） |
| vgpu_events.c | 583 | 事件环形缓冲（host→guest 反向通知）：`_readEventBufPut/Get`（:68/:73）+ `_setupGspEventInfrastructure`（:94）+ 事件服务（`vgpuServiceEventGuestAllocated` :193、`vgpuServiceEventRC` :212） |
| objvgpu.c | 502 | OBJVGPU 对象与全局实例表 `NvVGPU_Table[NV_VGPU_MAX_INSTANCES]`（:40） |
| vgpu_util.c | 497 | 杂项工具 |
| vgpuctrl.c / vgpuapi.c | 117/80 | 控制命令与 API 面 |

rpc.c 的万行体量不是堆出来的，是**版本化函数族**撑出来的：同一个 RM API 按固件 RPC 版本各留一个实现——`rpcAllocObject_v25_08 / v26_00 / v27_00 / v29_06 / v2B_04 / v2C_01`（rpc.c:4017-4295，六代并存）、`rpcAllocMemory_v13_01`（:3486）、`rpcMapMemoryDma_v2C_05`/`rpcUnmapMemoryDma_v2C_05`（:4350/:4379）、`rpcAllocRoot_v07_00`（:3382）、`rpcFree_v03_00`（:3353）、`rpcLog_v03_00`（:3018）等。版本协商入口 `rpcSetIpVersion`（:1008）在初始化时按协商结果把选中的函数族挂上分派；rpcstructurecopy.c 同理按 ipVersion 选结构拷贝逻辑（:994 `rpcStructureCopySetIpVersion`）。

基础设施三件套加一张位图：GSP 共享内存（`_setupGspSharedMemory` :504）、GSP 调试缓冲（:535）、GSP 休眠共享缓冲（:594，vGPU 休眠/恢复用）与 sysmem PFN 位图（`_setupSysmemPfnBitMap` :699，跟踪 guest 物理页以便 host 侧脏页跟踪与脏页日志）。

**hypervisor/ 五文件**：`hypervisor.c`（368 行）持有 ops 数组 `static HYPERVISOR_OPS _hypervisorOps[OS_HYPERVISOR_UNKNOWN]`（:40），`_hypervisorLoad`（:48-53）填四家 ops。枚举定义在**仓级公共头** `src/common/sdk/nvidia/inc/nv-hypervisor.h:31-37`：`OS_HYPERVISOR_XEN=0 / VMWARE / HYPERV / KVM / UNKNOWN`（注意顺序与直觉的字母序不同，Xen 是 0 号）。每家 ops 的身份锚是 12 字节 CPUID 签名：xen.c:52 `"XenVMMXenVMM"`、kvm.c:51 `"KVMKVMKVM\0\0\0"`、vmware.c:51 `"VMwareVMware"`、hyperv.c:101 `"Microsoft Hv"`——正是 x86 虚拟化工业标准里 CPUID leaf 0x40000000 返回的厂商串。

## 三、外部连接

**对 GSP/host**：传输层 `_rpcSendMessage_VGPUGSP` / `_rpcRecvPoll_VGPUGSP`（rpc.c:126-127 声明、:1874/:1884 实现），统一出口 `rpcSendMessage_IMPL/rpcRecvPoll_IMPL`（:1862/:1868）。消息体经共享内存缓冲搬运，序列号（pSequence）配对请求与响应。轮询式接收（RecvPoll）意味着 guest 侧 RPC 是同步阻塞语义——发一条、等对应的 func+sequence 回包。

**对 RM 内部**：guest RM 的 rmapi 层（alloc_free/control 路径）检测到 `IS_VIRTUAL(pGpu)` 时把本地执行替换为 rpc 调用；objvgpu.c 挂在 GPU 对象树上（`GPU_GET_VGPU`，objvgpu.c:142），vGPU 实例注册进 `NvVGPU_Table`。

**对 hypervisor**：`hypervisorDetection`（hypervisor.c:89 起）用 CPUID 探测 + 签名匹配设定 `pHypervisor->type`；RM 各处用 `hypervisorIsType(OS_HYPERVISOR_*)` 查询。两处典型消费：P2P 判定 `hypervisorPcieP2pDetection_IMPL`（:73-88）——四家可各自声明 `hypervisorIsPcieP2PSupported`，KVM 的实现是恒 FALSE（kvm.c:30 `_dummyKvmIsP2PSupported`）；vGPU GSP 路径在 Hyper-V 下有专门分支（objvgpu.c:80 `hypervisorIsType(OS_HYPERVISOR_HYPERV) && !IS_VIRTUAL_WITH_FULL_SRIOV`，rpc.c:9850 同款判定）——Hyper-V 的 SR-IOV 完整直通场景走不同初始化。

**身份上报**：guest 还要告诉 host 自己是什么系统。`vgpuUpdateGuestOsType`（rpc.c:218）把架构（X86_64/AARCH64）、OS（NV_UNIX→LINUX）、页阶（`nvLogBase2(osGetPageSize()) - 12`）打包进 `NV_VGPU_GUEST_OS_TYPE` 位域上报——host 侧拷贝引擎配置（页大小相关）依赖它。

## 四、数据流

**下行（guest→host 请求）**：guest 应用发 RM API（如 NVOS32 分配显存）→ guest rmapi 查 IS_VIRTUAL → `rpcAllocMemory_v13_01`（:3486）填 RPC 消息头（func/序列号）与参数体 → `_rpcSendMessage_VGPUGSP`（:1874）写入共享缓冲、敲 GSP 通知 → `_rpcRecvPoll_VGPUGSP`（:1884）轮询直到 expectedFunc+expectedSequence 回包 → 结果结构经 rpcstructurecopy 的版本化拷贝回填 → guest RM 返回用户态。host 侧真实分配（含 vGPU 显存配额扣减）对 guest 透明。

**上行（host→guest 事件）**：host 把事件写进事件环形缓冲（vgpu_events.c），guest 驱动按 `_readEventBufPut`/`_writeEventBufGet`（:68/:78）游标消费，逐条经 `vgpuServiceEvent*` 分派——如 `vgpuServiceEventRC`（:212）处理 robust channel 错误（guest 通道非法操作被 host 判死后的恢复），`vgpuServiceEventGuestAllocated`（:193）处理 guest 自分配内存的登记。

**管理面**：`updateHostVgpuFbUsage`（rpc.c:123）周期性把 guest 实际显存占用上报 host（vGPU 计费/超卖监控依赖此数据）；vGPU 休眠走 hibernate 共享缓冲（:594）把 guest 显存状态换出到 host 磁盘。

## 五、设计决策

1. **版本族并存而非 ABI 演进**：RPC 结构体直接嵌在消息里（无 TLV/protobuf），新版本加字段就复制一份新函数（v25_08→v2C_01 六代 AllocObject）。臃肿但极稳：每个版本的线格式被函数名钉死，永不误读。代价就是 rpc.c+rpcstructurecopy.c 合计 15,741 行。
2. **同步轮询 RPC**：不做异步管线，一问一答。guest 内核上下文简单可靠；vGPU 性能瓶颈在 host 调度而非 guest 出口，这层不值得复杂化。
3. **CPUID 签名探测而非 ACPI/设备树**：四家签名是 x86 事实标准，一次 CPUID 全搞定；Hyper-V 额外做 child partition 探测（其余三家恒 true，kvm.c:40-45 注释明言"keep consistency"）。枚举放公共 SDK 头（nv-hypervisor.h）使 nvidia.ko 与用户态工具共享同一套类型值。
4. **KVM P2P 恒 FALSE 是显式能力声明**：不是没实现，是 KVM 的 vfio 架构下跨 guest P2P 不安全，用 ops 钩子把"不支持"固化在探测层而非散布在使用点。
5. **PFN 位图自建**：host 需要知道 guest 哪些 sysmem 页在用（迁移/快照），guest 驱动维护位图（:699）而非依赖 hypervisor 接口——四家 hypervisor 无统一的脏页跟踪接口，自建跨平台。
6. **Hyper-V 特判收口两处**：只在本篇两个文件出现 HYPERV 判定（objvgpu.c:80/rpc.c:9850），其余代码一律经抽象跑——特判聚集度高，便于跟踪微软侧协议变化。

## 六、新人提示

- **读码顺序**：vgpu_version.h（版本锚）→ rpc.c:1008-1110（协商与基础设施）→ 任选一个版本化函数（推荐 rpcFree_v03_00，:3353 起，最短）跟一条完整消息 → vgpu_events.c 全文（不足 600 行）→ hypervisor.c 全文（368 行）+ 任一家 ops。
- 调 vGPU 兼容问题先查两边版本：guest 的 VGX 主版本（vgpu_version.h:33）与 host vGPU 软件大版本的映射表在 NVIDIA vGPU release notes；协商失败通常报 RPC version mismatch。
- rpc.c 不要通读——万行里六成是版本孪生函数，认准 `_v<十六进制版本>` 后缀成族读。
- `IS_VIRTUAL` / `IS_VIRTUAL_WITH_FULL_SRIOV` / `IS_PASSTHROUGH` 三态是 vGPU 判定的基本词汇：vGPU=共享虚拟 GPU、FULL_SRIOV=直通虚拟函数、PASSTHROUGH=整卡直通，RPC 通道只有第一态才走。
- 改 RPC 结构字段时：必须同时动 rpc_vgpu.h（定义）、rpcstructurecopy.c（每个受影响版本的拷贝）、GSP 侧对应文件——三处不同步是最常见的版本事故。
- 与 UVM 的边界（任务描述括号里"nvidia-uvm 之外"）：UVM 是 HMM/统一内存的 guest 内服务，不经 RPC；本篇 RPC 只覆盖 rmapi 转发与 vGPU 管理面。

---

**本篇甄别备注**：任务描述"rpc.c 11443 行"实测无误；hypervisor 四家适配的实际位置在 `src/nvidia/src/kernel/virtualization/hypervisor/`（xen/kvm/hyperv/vmware 四目录 + hypervisor.c 核心），vgpu/ 目录本身只含两处 Hyper-V 判定，"四家适配"归属 virtualization 子树。OS_HYPERVISOR 枚举定义于 `src/common/sdk/nvidia/inc/nv-hypervisor.h:31-37`（非 vgpu 头内）。
