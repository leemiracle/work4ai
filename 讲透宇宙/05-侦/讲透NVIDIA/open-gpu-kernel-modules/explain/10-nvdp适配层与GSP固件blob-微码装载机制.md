# 10 · nvdp 适配层与固件/微码装载：DP 宿主桥接 + GSP boot 镜像 + headsurface shader 三种"码"的入轨方式

> 仓库 @ 615.71.09。本篇覆盖 `src/nvidia-modeset/src/dp/nvdp-*`（9 文件，2577 行 C++）、`src/nvidia/generated/g_bindata_*`（64 个生成文件）与 `src/nvidia-modeset/src/shaders/`（五代 GLSL 编译产物 + 布局表）。

## 一、角色定位：两个"桥"，三种"码"

本篇把两组通常不被放在一起的代码放在一起讲，因为它们回答同一个工程问题——**二进制微码如何进入驱动、按代际选择、最后落到硬件**：

- **nvdp-\***（DP 适配层）：第 9 篇的 DP 库定义了五个平台契约（MainLink/AuxBus/Timer/EvoInterface/EventSink），nvdp 就是 NVKMS 交出的答卷。它把 DP 协议事件翻译成 NVConnectorEvo 状态，把 NVKMS 的内存/定时器/RM 通道注入协议库。
- **GSP 固件 blob 族**：GSP（GPU System Processor，Falcon/RISC-V 微控制器）运行整套 RM 固件；`src/nvidia/generated/` 下 64 个 `g_bindata_*.c` 文件把 boot 镜像、Booter 微码、FMC 固件、SPDM 证书全部以 C 数组形式嵌进 `nvidia.ko`。
- **headsurface shader 微码**：五个无扩展名二进制（`g_{turing,ampere,hopper,blackwell,gb20x}_shaders`），是第 7 篇 headsurface 软件合成的 GPU 端程序，经 xz 压缩嵌入模块。

一个先钉死的事实：开源构建的 `nvidia-modeset.ko` 与 `nvidia.ko` 一样是混合模块——`kernel-open/nvidia-modeset/nvidia-modeset.Kbuild:43` 定义 `NVIDIA_MODESET_BINARY_OBJECT := nv-modeset-kernel.o_binary`，NVKMS 核心、DP 库、nvdp 适配层、shader 微码全部位于该二进制核内；开源仓这些源码是参考实现。GSP bindata 则随 `nvidia.ko` 的闭源核链接。

## 二、内部结构

**nvdp 九文件**按注入契约分工：

| 文件 | 行数 | 实现的契约/职责 |
|---|---|---|
| nvdp-connector.cpp | 1244 | 连接器生命周期主控：`nvDPNotifyLongPulse/ShortPulse`（:117/:137）、modeset 钩子 `nvDPPreSetMode/PostSetMode`（:845/:884）、`nvDPLibIsModePossible`（:606）模式可行性核算、暂停/恢复 `nvDPPause/nvDPResume`（:927/:1026） |
| nvdp-connector-event-sink.cpp | 718 | EventSink 全量实现：`newDevice`（:326）/`lostDevice`（:415）/`bandwidthChangeNotification`（:473）等 11 个回调，把 DP 设备事件落到 NVConnectorEvo 与 nvkms 事件队列 |
| nvdp-device.cpp | 214 | Device 查询封装：EDID/DisplayID2.x/GUID/电源状态 |
| nvdp-evo-interface.cpp(+hpp) | 168 | EvoInterface：`rmControl0073/rmControl5070` 转发到 nvkms-rmapi |
| nvdp-timer.cpp(+hpp) | 141 | DP 库 RawTimer→`nvkms_alloc_timer` 包装 |
| nvdp-host.cpp | 92 | 内存/杂项主机钩子：`dpMalloc/dpFree`（:33 起）落到 nvAlloc/nvFree |

ConnectorEventSink 类（nvdp-connector-event-sink.hpp）`class ConnectorEventSink : public DisplayPort::Object, public DisplayPort::Connector::EventSink`——双继承，持一个 `NVConnectorEvoPtr pConnectorEvo` 反向锚点，每个回调末尾都能找到宿主连接器。

**GSP bindata 族**按内容分六类：`GspRmBoot`（×10 芯片：GA100/GA102/AD102/GB100/GB202/GB20B…）、`BooterLoadUcode/BooterUnloadUcode`（×5）、`ConcatenatedFMC + ConcatenatedFMCDesc`（×4，GR100/GH100/GB100/GB202）、`GspRmFmcGfwProdSigned/DebugSigned`（×12）、SPDM 证书（`IndividualL3Certificate`×12 / `L2`×4 / `L1`×1，第 12 篇联动）与 ksec2 微码（×2）。单个容器以 GB202 为例：`g_bindata_kgspGetBinArchiveGspRmBoot_GB202.c` 共 **36555 行**，分四段——`UCODE_IMAGE_DBG`（源文件 `kernel/inc/gspcc/bin/g_gsp_gb20x_dyn_dbg_image.bin`，290816 字节，:35-45 注释块+数组）、`UCODE_DESC_DBG`（:18243）、`UCODE_IMAGE_PROD`（:18277）、`UCODE_DESC_PROD`。每段是 `NvU64` 数组字面量 + `BINDATA_STORAGE_PVT` 描述符（:18227/:18261），元信息（文件名/尺寸/压缩标记）全部保留在注释里，可追溯。

框架层在 `src/nvidia/inc/kernel/core/bin_data.h`：`BINDATA_ARCHIVE`（归档=多标签容器）+ `bindataArchiveGetStorage(archive, label)` / `bindataGetBufferSize` / `bindataWriteToBuffer`（:122-123 API 面）。标签枚举（:43-54）从 `HEADER_DBG/PROD` 一路到 `PATCH_LOC/PATCH_META`（签名打补丁定位）。

**shader 微码**：`shaders/` 下五枚无扩展名二进制（turing 236KB 级→gb20x 252KB 级），配五张 `g_*_shader_info.h` 布局表（每枚约 10KB）与 `g_shader_names.h`（:44 `NUM_PROGRAMS 34`——34 个程序名：headsurface 基础/customSampling/overlay/yuv420/pixelShift/reversePrime 等变体）。布局表每项含 `.offset`（微码内偏移）、`.registerCount`、`.stage`（NV3D_HW_SHADER_STAGE_PIXEL 等）、`.bindGroup`；`g_nvidia-headsurface-shader-info.h` 再为每个程序标注八个布尔能力位（pixelShift/yuv420/blend/offset/overlay/blendAfterWarp/customSampling/reversePrime），供运行期按合成需求选程序。

## 三、外部连接

nvdp 三个方向的接口：向上直接操作 NVConnectorEvo/NVDpyEvo（nvkms 连接器抽象）与 nvkms 事件；向下创建 DP 库 Connector（构造注入 nvkms 的 MainLink/AuxBus/Timer 实现）；旁路经 nvdp-evo-interface 把库的 RM 需求（0073/5070 控制命令）转给 `nvkms-rmapi.c`。热插拔入口在 nvkms-evo.c 侧：连接器 HPD 中断→`nvDPNotifyLongPulse`。

GSP 镜像的消费者是 `kernel_gsp.c:6242` 的 `kgspPrepareBootBinaryImage_IMPL`：先 `kgspGetGspRmBootUcodeStorage_HAL`（:6263）按芯片代际拿 storage——GA102 路径（kernel_gsp_ga102.c:109-124）直接 `bindataArchiveGetStorage(archive, DEBUG?UCODE_IMAGE_DBG:UCODE_IMAGE_PROD)`；GB100 路径（kernel_gsp_gb100.c:126 起）多一层决策：**机密计算（CC）启用时改用 ConcatenatedFMC 归档**（:141-153 dbg/prod 双档），未启用则回退 GA102 路径（:165）。拿到 storage 后 `bindataGetBufferSize` 量尺寸、`memdescCreate` 在 sysmem 分配 4K 对齐缓冲（CC 场景追加 `MEMDESC_FLAGS_ALLOC_IN_UNPROTECTED_MEMORY`，:6270-6273）、`memdescMap` 映射，最终 `pGspRmBootUcodeImage` 指向可执行镜像（:6295）。

## 四、数据流：三种"码"各自的入轨路径

**路径一（GSP boot，C 数组 → sysmem → 微控制器）**：编译期 bindata 数组随 nvidia.ko 链接 → 引导期按芯片+模式（dbg/prod/CC）选档 → 拷入 sysmem → Booter（`BooterLoadUcode` 归档）接力把镜像搬进 GSP 私有内存并验签（LC128 标签、HS_SIG_PATCH_METADATA 签名补丁标签即为此服务）→ GSP 启动、接管 RM。

**路径二（headsurface shader，xz 压缩二进制 → ELF 段 → 运行时解压 → 显存）**：`src/nvidia-modeset/Makefile:201-211` 的 `COMPRESS_SHADERS` 宏对五代微码各执行 `xz -ce -C none`（无校验和的纯流）→ `READ_ONLY_OBJECT_FROM_FILE_RULE` 把 .xz 包成只读 ELF 目标文件（.xz.o）→ 与模块链接。运行期：headsurface 初始化时用**内核态 xz 单次解码器**（CFLAGS `XZ_DEC_SINGLE` + `NV_XZ_CUSTOM_MEM_HOOKS` + `NV_XZ_USE_NVTYPES`，Makefile:195-197）把整块微码解压，再按 `g_*_shader_info.h` 的 offset 表切片上传显存，`nvkms-headsurface.c` 合成时按 `g_nvidia-headsurface-shader-info.h` 的能力位选程序发 3D 通道方法。

**路径三（nvdp，纯运行时对象流）**：HPD 长脉冲→`nvDPNotifyLongPulse`（nvdp-connector.cpp:117）→ DP 库拓扑发现→ConnectorEventSink::newDevice（event-sink.cpp:326）→ nvkms dpy 注册→用户态 QueryDpy*；modeset 时 `nvDPPreSetMode`（:845）先于硬件应用做 DP 侧准备（链路重训/带宽变更），`nvDPPostSetMode`（:884）收尾。

## 五、设计决策

1. **C 数组 vs objcopy 的取舍**：GSP 固件用 36555 行 C 源数组（体积代价 8 字节/元素格式化），shader 用 objcopy 嵌段。差别在**链接器可裁性**：C 数组被 HAL 引用函数包裹，`--force-group-allocation` 死代码消除（Makefile:229-235）能按实际支持的芯片裁掉无关固件；而 shader 五代必须全量在模块里（模块不知道会插什么卡）。
2. **xz 单次解码而非按需流式**：shader 是整块使用（一次解压全量入显存），单次解码器代码量最小，符合内核模块体积敏感约束。代价是解压时需要临时全量缓冲。
3. **dbg/prod/CC 三维选档**：镜像选择 = 调试与否 × 机密计算与否 × 芯片代，三维护度全部在 HAL storage 函数里就地展开（GB100 :126-165 的 if 树），不搞配置表——分支少、可读、每代可独立演化。
4. **元信息注释化**：bindata 生成文件把源文件名/字节尺寸/压缩标记写进注释（GB202 :36-44），36555 行巨文件因此仍然可审计——改一眼就知道哪段数组对应哪个 .bin。
5. **nvdp 的 adapter 全薄**：九文件最大才 1244 行，全部是翻译层；DP 协议复杂度留在库、NVKMS 语义留在 nvkms-evo，适配层不藏私货——双向都看不到对方的内部结构。
6. **能力位驱动的程序选择**：34 个 shader 程序不按名字硬编码选择，而是 8 布尔能力位（g_nvidia-headsurface-shader-info.h）匹配合成需求，新增变体只需加程序+加位，不改选择逻辑。

## 六、新人提示

- **别通读 bindata**：36555 行里 99% 是数组字面量，读头部注释块（:35-44）+ BINDATA_ARCHIVE 描述符即可；要抽验内容可用 `od` 对比源 .bin。
- 找"我的卡加载了哪个固件"：读 `kgspGetGspRmBootUcodeStorage_*` 系列的 arch 文件（turing/ampere/adamper/blackwell 各一个），芯片代际→HAL 函数→归档名三步定位。
- nvdp 调试入口：`nvDPGetDeviceGUIDStr`（event-sink.hpp 尾部声明）是贯穿日志的设备指纹；MST 问题按"长脉冲→newDevice→bandwidthChange"三事件在两份 nvdp 文件里串时间线。
- shader 布局表与微码必须同代配套使用——offset 是同代微码内的偏移，跨代表查会取到错位程序（每张 info.h 只服务同名无扩展名文件）。
- 五代 shader 与第 7 篇 dispTable 的对应：turing=C5、ampere=C6、blackwell=C9、gb20x=CA；hopper（GH100）无显示引擎（headless 数据中心卡），其 shader 表存在的意义是对外提供一致的 headsurface 能力声明。
- 想改 headsurface GLSL：源码不在此仓（shader 由 GLSL 编译管线预生成），此仓只有产物与布局表。

---

**本篇甄别备注**：任务描述"GspRmBoot_GB202 36555 行"与"五个无扩展名 shader 微码"均经源码核实无误（wc -l 实测 36555；shaders/ 目录五枚 data 文件）。GSP bindata 归档的编译归属在闭源构建链（src/nvidia/srcs.mk 体系），开源 kernel-open 构建不含这些生成文件；nvdp 与 DP 库编入 nv-modeset-kernel.o_binary（nvidia-modeset.Kbuild:43），开源仓内为参考源码。
