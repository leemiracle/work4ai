# open-gpu-kernel-modules（OGKM）新人导览 ONBOARDING.md

> 图谱基线：commit `61dcc93722ecb418bb5f2e00923f05b4b8051dd1` · 16795 节点 / 35744 边 / 16 层 / 16 步 tour（understand-anything 历史第一大图谱）。本文件全部行号/路径锚均经源码级核实（2026-11-06 快照）。

## 1. 一句话定位与版本坐标

**这是 NVIDIA 官方开源的 Linux GPU 内核驱动 GPL 侧源码**：把"OS 无关的 RM（Resource Manager）内核 + NVKMS 显示核心"编成静态库，再与 `kernel-open/` 的 Linux 粘合层链接成 `nvidia.ko` 等五个内核模块。实测版本 `README.md:4` 明写 "version 615.71.09"，且 README 要求配套同版本 GSP 固件与用户态组件——**开源的只是内核壳与 RM 客户端侧，GPU 控制面的真正本体跑在 GSP 固件里，以 C 数组 blob 内嵌**（`src/nvidia/generated/g_bindata_kgspGetBinArchiveGspRmBoot_GB202.c` 实测 36555 行、1.8MB）。理解这一"GPL 壳 + MIT 生成层 + 二进制固件"的三明治结构，是本仓一切阅读的前提。

版本坐标：615 分支（2025 线），支持 x86_64/aarch64（`README.md:33` 声明），代际覆盖 Turing→Blackwell→Rubin（`src/nvidia/src/kernel/gpu/arch/` 实测 10 个代际目录：ada/ampere/blackwell/hopper/maxwell/pascal/rubin/t23x/t26x/turing）。仓库另含 NVSwitch 独立驱动与 `nouveau/` 固件提取脚本（`nouveau/extract-firmware-nouveau.py` 1141 行），即社区 Nouveau 生态也从这里取固件。

## 2. 分层架构总览（16 层全景）

图谱把 4000+ 文件切成 16 层，自下而上是"构建 → 第三方地基 → 生成代码 → 接口字典 → RM 内核 → 硬件子系统 → 内核模块群"的依赖梯度：

| 层 | 名 | 文件数 | 职责与代表锚 |
|---|---|---|---|
| L01 | 构建配置与仓库顶层 | 37 | 两段式构建：顶层 `Makefile:13-17` 定义 `nv-kernel.o`→`*_o_binary` 符号链接，`Makefile:29` 注释明言 "nv-kernel.o is the OS agnostic portion"；`kernel-open/conftest.sh`（5989 行 shell）探测内核特性 |
| L02 | 第三方基础库 | 115 | Berkeley softfloat IEEE-754（`src/common/softfloat/source/f64_add.c`）、xz 迷你解压器、libdwarf/libelf |
| L03 | libspdm 安全协议栈 | 126 | DMTF libspdm 3.5.0 完整拷贝（`src/nvidia/src/libraries/libspdm/3.5.0/`），支撑 GSP 设备认证；`kernel-open/nvidia/` 另有内核态裁剪拷贝 |
| L04 | RM 支撑库 | 139 | 容器（btree/map/list）、NVPort、TLS、ressrv 资源服务器、CrashCat 崩溃解码 |
| L05 | NVOC 生成层与运行时 | 481 | `src/nvidia/generated/` 实测 533 文件其中 424 个 `*_nvoc.*`；运行时 `src/nvidia/src/libraries/nvoc/src/runtime.c`（359 行）+ `rtti.h`（80 行）+ 手写接入点 `src/nvidia/inc/libraries/nvoc/prelude.h`（300 行） |
| L06 | swref 硬件参考头 | 429 | `src/common/inc/swref/published/` 按代际组织的 `dev_*.h` 寄存器字典（Kepler→Rubin 含 NVSwitch） |
| L07 | RM class 接口头 | 307 | `src/common/sdk/nvidia/inc/class/cl00xx.h` 资源类 ID 谱系 |
| L08 | RM ctrl 与 SDK 公共头 | 268 | `ctrl/ctrlxxxx.h` 命令编码宏 + `ctrl/ctrl2080/`（53 个子头）等控制命令结构；实测 205 个 ctrl 头带 FINN 生成标记 |
| L09 | RM 内核核心与平台 | 402 | OBJGPU 主体 `gpu.c`（7980 行）、`gpu/arch/` 分代 HAL、platform/NBSI |
| L10 | 显存与 MMU | 228 | `mem_mgr.c`（4293 行）/`heap.c`（4263 行）/GMMU 页表遍历 `gmmu_walk.c`（1026 行）/MIG 切分 `kernel_mig_manager.c`（10280 行） |
| L11 | GPU 引擎与基础子系统 | 324 | fifo/CE/GR/intr/bus/perf/rc/conf_compute，每类配 `arch/<代际>` HAL |
| L12 | GSP 固件与虚拟化 | 190 | `kernel_gsp.c`（7886 行）固件装载与 RPC、g_bindata 固件 blob、vGPU 管理器 `kernel_vgpu_mgr.c`（5606 行） |
| L13 | 显示通道 RM→NVKMS | 342 | RM disp HAL（`arch/v02-v05`）→ `nvkms.c`（7196 行）→ DP 协议库与 EVO 助手 |
| L14 | nvidia.ko 内核主模块 | 181 | `kernel-open/nvidia/nv.c`（6735 行）OS 粘合 + drm/peermem 对接 |
| L15 | UVM 统一虚拟内存 | 222 | 独立模块 `nvidia-uvm`：fault 重放、SVM 区间（`uvm_va_range.c` 2640 行）、内核 API 兼容层 |
| L16 | NVSwitch/NVLink 互连 | 209 | 独立驱动：`lr10.c`（8359 行）/`ls10.c`（6895 行）两代交换芯片 + RM 侧 `kernel_nvlink.c`（4682 行） |

三条贯穿全仓的目录学规律：**① `src/nvidia/src` 是 OS 无关世界，`kernel-open/` 是 Linux 世界，两侧同名文件靠拷贝而非共享符号**（`nv-kthread-q.c` 四份字节级相同拷贝 md5 全一致）；**② 每个子系统 = 公共实现 + `arch/<代际>` HAL** 的范式从 fifo 到 disp 一以贯之；**③ 生成代码（generated/）与手写代码（src/、inc/）物理隔离**，薄壳头做转接。

## 3. 核心数据流

主控制流（用户态到硬件）一条线：

```
用户态(nvidia-smi/CUDA/Xorg)
  → /dev/nvidiactl ioctl（cmd magic 'F'，kernel-open/common/inc/nv-ioctl-numbers.h:33）
  → nvidia_ioctl()（kernel-open/nvidia/nv.c:2627；先经 nv.c:2575 nv_ioctls_table 白名单校验）
  → rm_ioctl()（nv.c:2982，进入 OS 无关 RM；适配器生命周期由 nv.c:1667 rm_init_adapter 驱动，
     声明于 kernel-open/common/inc/nv.h:1188）
  → RM_API vtable（src/nvidia/src/kernel/rmapi/rmapi.c:56 g_RmApiList[RMAPI_TYPE_MAX]，
     L114-118 初始化 EXTERNAL/EXTERNAL_KERNEL/MODS_LOCK_BYPASS/API_LOCK_INTERNAL/GPU_LOCK_INTERNAL 五种接口形态）
  → 资源服务器（src/nvidia/src/libraries/resserv/src/rs_server.c，5177 行，句柄→对象树+访问控制；
     resource_desc.c:117 注释"按 externalClassId 排序以便二分查找"，L154 命中 g_RsResourceDescList）
  → NVOC 对象体系（g_gpu_nvoc.h:1043 struct OBJGPU；类定义/RTTI/up-cast 链全由 NVOC 生成）
  → OBJGPU 状态机（gpu.c:2126 gpuStatePreInit_IMPL → gpuStateLoad；L6306 gpuServiceInterruptsAllGpus_IMPL 分发中断；
     HAL 分发经 g_gpu_nvoc.h:1065 起的 __xxx__ halified 函数指针族 + g_chips2halspec_nvoc.h 代际位掩码）
  → KernelGsp（src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c:5429 _kgspBootGspRm 引导固件；
     控制命令封成 RPC 经 message_queue_cpu.c 队列发出——kernel_gsp.c:211 _kgspRpcSendMessage / L213 _kgspRpcRecvPoll / _kgspRpcDrainEvents）
  → GSP 固件（RISC-V 处理器上的闭源 RM）直接操作 MMIO 寄存器（寄存器名字典在 L06 swref）
```

三条旁路绕开这条主干：**UVM 数据面**（`kernel-open/nvidia-uvm/uvm.c:997 uvm_ioctl` 独立字符设备，fault 缓冲重放与页迁移不占 RM API 路径）；**modeset**（RM 只保留 disp 对象管理 `disp_objs.c`，实际 push buffer 由 OS 无关 NVKMS `src/nvidia-modeset/src/nvkms.c:5049 nvKmsIoctl` 接管，经 `kernel-open/nvidia-modeset/nvidia-modeset-linux.c` 挂到内核）；**NVSwitch**（交换芯片完全绕开 RM，`kernel-open/nvidia/linux_nvswitch.c:120 nvswitch_pci_driver` 独立 PCI 驱动，probe 入口 L104）。

vGPU 场景下主控制流再加一跳：guest RM 的 RPC 协议结构在 `src/nvidia/generated/g_rpc-structures.h`（12367 行；L1437 rpc_gsp_rm_alloc_v03_00、L1452 rpc_gsp_rm_control_v03_00 是两种最核心命令，L8095 起 vmiopd_fdesc_t 描述符表供 vmioplugin 侧符号化），编解码与等待逻辑集中在 `src/nvidia/src/kernel/vgpu/rpc.c`（11443 行，全仓最大单文件之一；L3018 rpcLog_v03_00 / L3353 rpcFree_v03_00 为代表）。

## 4. 关键模块深读（五件）

**① NVOC 生成机制（generated/ 533 文件，424 个 \*_nvoc.\*）**。NVOC 是 NVIDIA 自研的"C 元对象编译器"：手写文件里用宏标注类（`prelude.h` 是手写侧接入点），编译期生成 RTTI、构造/析构分发、up-cast 链与 HAL 函数表。看 `g_gpu_nvoc.h:1043` 的 `struct OBJGPU`：L1062 `__nvoc_pbase_OBJGPU` 基类指针、L1065 起 `__gpuConstructDeviceInfoTable__` 等 halified 函数指针——**继承和多态全部被展平成结构体内嵌+函数指针**。代际开关在 `g_chips2halspec_nvoc.h`（177 行）：用 `GB202|GB203|GB205` 位掩码描述每代芯片启用了哪些 IP 版本，L152 甚至保留 "// delete DISPv0502 & ~(GB202 | ...)" 这样的策略注释。**生成层一律勿手改**。

**② g_gpu_class_list 全类注册表（src/nvidia/generated/g_gpu_class_list.c，4767 行）**。RM 的"哪些类号在哪代芯片可用"总账本：L34 genericClassDescriptorList（全代通用类）起步，L59 起 halTU102ClassDescriptorList 按代际列表。上游消费点在 `src/nvidia/src/kernel/gpu/gpu_resource_desc.c:381`（"Populate the ClassDB with information from the static class list"）。而人类可读的类号→名字总表是 `g_allclasses.h`（1253 行，头注释注明"generated by chip-config from Classes.pm"），逐行 `#include <class/cl0000.h> // NV01_ROOT` 风格。

**③ g_rpc-structures.h：12367 行的 RPC 契约**。guest RM ↔ host RM/物理 RM 的全部命令结构按版本号（v03_00/v25_1B…）演进式堆叠，头部先 include `g_sdk-structures.h`（5913 行 SDK 参数结构）。这是内核↔固件边界的"协议宪法"：加新 RPC 命令两边都要对齐这里（实际由生成器产出，人改的是 finn/Classes.pm 源）。

**④ kernel_mig_manager.c：10280 行的 MIG 切分大脑**。Multi-Instance GPU 的 GPU 实例/GI/CI 三级切分、执行资源区间计算（L642 kmigmgrGetGRCERange_HAL 按代际取 GR/CE 引擎区间）、SR-IOV 联动。它是"一份物理 GPU 切成多份 vGPU 给不同租户"的数据中心核心，也是 L10 显存层与 L11 引擎层的交汇点。

**⑤ kernel-open/nvidia 主模块（nv.c 6735 行）**。五个内核模块（nvidia/nvidia-modeset/nvidia-drm/nvidia-uvm/nvidia-nvswitch）的母模块：nv.c:823 nv_register_chrdev 统一注册设备号（L1059 普通设备区间 + L1066 控制设备），fops 表 L266 起（.mmap=nvidia_mmap 等）。配套 `nv-pci.c`（3560 行）做 PCI 探测与 BAR 映射。理解"一次 CUDA 调用如何进内核"从 nv.c:2627 的 ioctl switch 开始读最快。

## 5. 新人导览路线（16 步 tour 精炼）

按图谱 tour 顺序，三天可走完的渐进路线（每步给出核心文件与"看什么"）：

| 步 | 主题 | 核心锚 | 看什么 |
|---|---|---|---|
| 01 | 全景与两段式构建 | `Makefile:58`、`kernel-open/conftest.sh:38`（test_xen 起 38 个探测函数）、`kernel-open/dkms.conf` | 先懂"src/ 编 OS 无关库 → kernel-open/ 链成 .ko" |
| 02 | 内核态入口 nvidia.ko | `nv.c:2627` nvidia_ioctl、`nv.c:1667` rm_init_adapter | ioctl 主分发与 RM 交接 |
| 03 | 内核公共 OS 抽象 | `kernel-open/common/inc/nv-ioctl-numbers.h:33`、四份 nv-kthread-q.c | 模块间靠拷贝共享代码的现实 |
| 04 | DRM 对接与 RDMA peer | `kernel-open/nvidia-drm/nvidia-drm-drv.c`、`nvidia-peermem/nvidia-peermem.c` | GEM/PRIME 与 GPU 显存注册进 RDMA |
| 05 | RM API 门面与资源服务器 | `rmapi.c:114`、`rs_server.c`、`resource_desc.c:117` | vtable 装配、句柄树、类号二分 |
| 06 | NVOC 元对象编译机制 | `g_gpu_nvoc.h:1043`、`runtime.c`、`prelude.h` | 读懂"类"如何被生成 |
| 07 | OBJGPU 与 HAL 分派 | `gpu.c:2126`、`arch/blackwell/kern_gpu_gb100.c` | 每 GPU 一实例的状态机 |
| 08 | 显存与 GMMU | `mem_mgr.c`、`heap.c`、`gmmu_walk.c`、`inc/libraries/mmu/gmmu_fmt.h` | 堆/物理页/页表格式与遍历 |
| 09 | 引擎与基础子系统 | `kernel_fifo.c`（4180 行）、`kernel_channel.c`（4961 行）、`intr.c` | 通道调度与中断路由范式 |
| 10 | GSP 客户端与固件 | `kernel_gsp.c:5429`、`message_queue_cpu.c`、`gsp_fw_wpr_meta.h:60` GspFwWprMeta | 固件引导、WPR 显存布局、RPC 队列 |
| 11 | vGPU 与虚拟化 | `kernel_vgpu_mgr.c`、`rpc_vgpu.h` | vGPU 生命周期与迁移 |
| 12 | UVM 统一虚拟内存 | `uvm.c:1163` uvm_init、`uvm_va_range.c` | SVM 区间、fault 重放、\*_test.c 单测 |
| 13 | 显示通道 RM→NVKMS | `disp_objs.c`、`nvkms.c:5049`、五个无扩展名 shader | EVO 推送与时序 |
| 14 | DisplayPort 协议库 | `src/common/displayport/src/dp_discovery.cpp`、`dp_evoadapter.cpp` | MST 拓扑发现、DSC |
| 15 | NVSwitch 与 NVLink | `lr10.c`、`ls10.c`、`kernel_nvlink.c`、`linux_nvswitch.c:120` | 链路训练与 SOE 微控 |
| 16 | swref 硬件参考与第三方地基 | `swref/published/blackwell/gb100/dev_gsp.h`、softfloat、libspdm | 寄存器字典与安全地基 |

建议节奏：第 1 天 01-06（构建+对象体系骨架），第 2 天 07-10（GPU 核心与 GSP），第 3 天按兴趣选 11-16。

## 6. 设计决策与取舍

**双许可证三明治**。内核粘合层 GPL、生成层与 SDK 头 MIT、GSP 固件纯二进制（以 `g_bindata_*` C 数组内嵌，规避固件文件分发问题）。这个架构让 NVIDIA 同时满足 Linux 内核 GPL 合规与 IP 保护——代价是**社区只能读代码、改代码，无法审计真正的控制面**（固件行为只能黑盒观察，`nouveau/extract-firmware-nouveau.py` 就是为社区提取这些 blob 而生）。

**NVOC 手写元编程而非 C++**。内核态禁 C++ ABI/异常/RTTI，NVIDIA 选择"宏标注 + 编译期生成 C"路线换取面向对象能力。代价是 424 个生成文件的巨大噪音（`src/nvidia/inc/` 下 418 个 .h 中实测 205 个 ≤4 行、占 49%——如 `src/nvidia/inc/kernel/gpu/gpu.h` 全文 3 行仅 `#include "g_gpu_nvoc.h"`）；收益是零运行时开销的类型系统与 HAL 分发。

**HAL 代际铺开 vs 家族兼容**。`gpu/arch/` 10 代并存、Blackwell 一个代内再分 gb100/gb10b/gb202/gb20b/gb20c 五个 SKU 文件——选择"每个代际/SKU 一个 HAL 文件"的铺开式而非 if-else 家族兼容式，读起来机械但 merge 冲突少、可按需裁剪编译。`g_chips2halspec_nvoc.h` 的位掩码声明式描述（GB202|GB203|GB205 共享 DISPv0502）是代际→IP 版本映射的唯一事实源。

**RPC 而非直接 MMIO**。现代 RM 内核侧大量命令不直接写寄存器，而是封 RPC 发给 GSP 固件执行——换来固件可独立更新、行为可黑盒演化，代价是调试链路变长（内核态看到的失败只剩超时与状态码，`kernel_gsp.c:215` 的限流打印是排障第一现场）。

**代码拷贝而非符号共享**。内核模块间不共享符号（GPL 导出限制），于是 `nv-kthread-q.c` 在 nvidia/nvidia-drm/nvidia-modeset/nvidia-uvm 四处各一份字节级相同拷贝（md5 全一致）、nvtypes.h 双份（src 侧 807 行/kernel-open 侧 844 行）。新人常误以为可以只改一份——**改公共文件必须同步全部拷贝**。

## 7. 已知坑与勘误（实测钉版）

**勘误 1：nvidia.ko 不用 nvGpuOps\*，走 rm_\* 家族。** 直觉记忆常把两者混为一谈。实测 `kernel-open/nvidia/nv.c` 全文 grep `nvGpuOps` 零命中——nv.c:1667 调的是 `rm_init_adapter`（声明于 `kernel-open/common/inc/nv.h:1188`，配套 rm_shutdown_adapter:1190）。`nvGpuOps*` 真函数族在 `src/nvidia/inc/kernel/rmapi/nv_gpu_ops.h:54-87`（352 行，nvGpuOpsCreateSession/DestroySession/DeviceCreate/AddressSpaceCreate…），实现于 `src/nvidia/src/kernel/rmapi/nv_gpu_ops.c:866` 起，服务对象是 NVKMS 等内核内消费者。两套 API 并存：**rm_\* 是 nvidia.ko 边界、nvGpuOps 是内核内客户的对象化封装**。

**坑 2：五个无扩展名文件是原始二进制微码，不是 C 数组。** `src/nvidia-modeset/src/shaders/` 下 `g_turing_shaders`/`g_ampere_shaders`/`g_hopper_shaders`/`g_blackwell_shaders`/`g_gb20x_shaders` 实测 244480-253184 字节的**裸二进制**（head 直接是乱码字节流），配套 `*_shader_info.h` 元数据。构建期由 `src/nvidia-modeset/Makefile:202-208` 的 COMPRESS_SHADERS 规则 `xz -ce -C none` 压缩后经 READ_ONLY_OBJECT_FROM_FILE_RULE 变成 `.xz.o` 只读段嵌入模块，L211-215 对五代逐一 eval。运行时由 xzminidec 解压。别试图文本工具打开它们。

**事实 3：GspRmBoot_GB202 是全仓最大单文件。** `g_bindata_kgspGetBinArchiveGspRmBoot_GB202.c` 实测 36555 行、1825650 字节，全是 `0x` 字节字面量（实测 36360 处）——GB202 的 GSP-RM 固件镜像本体。同族还有 GB100（1262450B）/GB10B/GH100/GR100 等 9 份代际镜像。

**坑 4：被引用但不存在的"NDA 域头"（4 个，实证）。** 本会话按 Makefile 实际 include 根全量解析 `src/nvidia/src/kernel/`，确认 8 个疑似缺失中 4 个是真缺失，且全部有条件编译守卫：`kernel_sec2.c:39-42` 在 `#if RMCFG_MODULE_ENABLED(GSP)` 内 include 的 `gpu/gsp/gsp.h` 与 `gpu/falcon/objflcnable.h`（GSP 内部域头，不开源）；`rmapi/embedded_param_copy.c:57-59` 在 `#ifdef USE_AMAPLIB` 内的 `amap_v1.h`；`mem_mgr/phys_mem_allocator/numa.c:41-44` 在 `#else`（SRT_BUILD）分支的 `pma_test_stubs.h`。**遇到编译错误找不到头，先看宏守卫再怀疑自己漏 clone。**

**坑 5：ctrl 头是 FINN 生成物。** `ctrl/ctrl2080.h` 头注释明言 "generated with FINN, an NVIDIA coding tool. Source file: ctrl/ctrl2080.finn"——实测 205 个 ctrl 头带 FINN 标记（finn 源不在仓内）。ctrl2080.h 本身只 91 行，实际内容在 `ctrl/ctrl2080/` 目录 53 个子头（ctrl2080gpu/bus/fb/fifo/nvlink/perf…）。改 ctrl 结构须从上游 finn 源走，直接改生成头会被下轮更新覆盖。

**坑 6：module include 前缀多套并存的解析陷阱。** 同一文件里 `#include "gpu/gpu.h"`（相对 inc/kernel）、`#include <ampere/ga100/dev_runlist.h>`（相对 swref/published，nv_gpu_ops.c:98）、`#include <containers/queue.h>`（相对 inc/libraries）三种根并存；`-I` 根清单在 `src/nvidia/Makefile` CFLAGS 段（L46 起，含 `$(SRC_COMMON)/inc/swref/published`）。新人写解析脚本若只按文件相对路径找，会大面积假报缺失（本会话实测：错误根路径下报 300+ 假缺失，正确根下仅 4 真缺失）。

**坑 7：version 615 不是 git tag 化的版本。** 仓库 git 历史无版本 tag，版本只写在 `README.md:4` 与 `kernel-open/dkms.conf` 的 `__VERSION_STRING` 占位符（打包时由 nvidia-installer 注入）。

## 8. 二次开发指引

**加新 HAL 代际（如新 SKU GB20x）**：① `src/nvidia/src/kernel/gpu/arch/<gen>/` 建 `kern_gpu_<chip>.c`，参照 `arch/blackwell/kern_gpu_gb202.c`（同目录 8 文件是最小样板）；② 在 `g_chips2halspec_nvoc.h` 加芯片位掩码并声明该代启用的 IP 版本（L152 的 DISPv0502 行是模板）；③ 各子系统 `arch/<gen>/` 下按需加 HAL 文件（NVOC 生成器会在构建期把 `__xxx__` 函数指针按 chipspec 表装配，**生成物勿手改，源头是手写 .h 里的 NVOC 宏标注**）；④ swref 寄存器头如未发布需走内部流程，公开代际参考 `swref/published/blackwell/gb100/`。

**加新 ctrl 控制命令**：上游在 finn 源（`.finn` 文件，仓内无），仓内落点是 `src/common/sdk/nvidia/inc/ctrl/ctrl<xxxx>/` 生成头（ctrl2080 子目录 53 头是最大集群）+ `src/nvidia/src/kernel/gpu/subdevice/subdevice_ctrl_*.c` 或对应子系统文件里的 handler + `rmapi/control.c` 路径上的权限/锁分类。命令号编码宏 `NVXXXX_CTRL_CMD(cat,idx)` 在 `ctrl/ctrlxxxx.h`。若只是内核内部实验，绕开 finn 直接在 `kernel-open` 加私有 ioctl 号（`nv-ioctl-numbers.h`）更轻。

**加新 RM class（用户态可分配对象）**：① 上游 Classes.pm 加类（本仓只收生成物）；仓内对应 `class/cl<xxxx>.h`（L07 层 307 个）与 `g_allclasses.h`/`g_gpu_class_list.c` 再生成；② `src/nvidia/src/kernel/<subsystem>/` 写 NVOC 类实现（`prelude.h` 是宏接入点，类骨架参照小类如 `compute/fm_session_api.c`）；③ 注册进 `resource_desc.c` 的 g_RsResourceDescList（保持 externalClassId 有序，L117 注释）。

**改内核粘合层**：nv.c/nv-pci.c 可直接改（GPL 侧）；公共头改动必须同步 4 份 nv-kthread-q 拷贝与双侧 nvtypes.h；构建改动记得 conftest.sh（新增内核特性探测加 test_ 函数，现有 38 个是模板）与 dkms.conf 模块清单占位符 `__DKMS_MODULES`。

**永远不要手改**：`src/nvidia/generated/` 全部（含 g_rpc-structures.h/g_gpu_class_list.c/g_bindata_\*）、`kernel-open/nvidia/Makefile` 与 `kernel-open/Kbuild`（文件头自动生成警告）、swref `dev_*.h`。

---
*产出：understand-anything onboarding 写作子代理 · 2026-11-07 · 锚点全部源码级核实于 commit 61dcc937*
