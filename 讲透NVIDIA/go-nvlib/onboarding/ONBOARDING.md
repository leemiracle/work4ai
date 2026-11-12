# go-nvlib 深度导览（ONBOARDING）

> 仓库：github.com/NVIDIA/go-nvlib @ d3f4ca8 · 图谱 309 节点 / 535 边 / 8 层 / 14 步 tour · fingerprints 基线 64 文件
> 本文所有行号锚均从源码逐一核实（2026-11-08），口径为 `文件:行`。

## 1. 这个库是什么：GPU 管理软件的 Go 包集合

README 一句话定位：**ease the development of GPU management software**（`README.md:3-5`）——它是构建在 [`go-nvml`](https://github.com/NVIDIA/go-nvml) 之上的 Go 包集合。`go.mod` 里模块 `github.com/NVIDIA/go-nvlib`、`go 1.26.0`，直接依赖仅四个：`go-nvml v0.13.4-1`、`google/uuid`、`testify`、`golang.org/x/sys`（`go.mod:5-12`）。

理解本库的关键是看清**两条主线**：

- **sysfs 侧主线**：`pkg/nvpci`（PCI 枚举与寄存器）、`pkg/nvmdev`（vGPU mediated device）、`pkg/nvpassthrough`（VFIO 直通）、`pkg/pciids`（PCI ID 数据库）——这些能力 NVML 根本不提供，是本库的独立价值；
- **NVML 侧主线**：`pkg/nvlib/device`（设备/MIG 抽象）与 `pkg/nvlib/info`（平台探测与装配）——是对 go-nvml 的上层封装，直接消费者是 k8s 设备插件、GPU Operator 一族。

下游实证：NVIDIA `k8s-device-plugin`、`gpu-operator`、`kubevirt-gpu-device-plugin`、`vgpu-device-manager` 都 import 本库——它是 NVIDIA 云原生 GPU 栈的"系统编程底座"。

## 2. 分层架构总览（图谱 8 层）

| 层 | 主题 | 代表文件 |
|---|---|---|
| L01 | 底座基元：字节序与 PCI ID 数据 | `bytes/native.go`、`bytes/swapbo.go`、`pciids/pciids.go` |
| L02 | 硬件访问原语：mmio 与配置空间 | `nvpci/mmio/mmio.go`、`nvpci/config.go`、`nvpci/resources.go` |
| L03 | nvpci 核心：sysfs 枚举 | `nvpci/nvpci.go`（598 行）、`nvpci/mlxpci.go`、`nvpci/mock.go` |
| L04 | 上层操作：vGPU 与 VFIO 直通 | `nvmdev/nvmdev.go`（401 行）、`nvpassthrough/nvpassthrough.go`（470 行） |
| L05 | NVML 设备抽象与 MIG 建模 | `nvlib/device/device.go`（605 行）、`mig_profile.go`、`identifier.go` |
| L06 | 平台探测与装配 | `nvlib/info/property-extractor.go`、`resolver.go`、`root.go`、`builder.go` |
| L07 | 构建与 CI | `Makefile`、`versions.mk`、`.github/workflows/golang.yml` |
| L08 | 治理与法务 | `NOTICE`、`THIRD_PARTY_NOTICES.md`、`hack/generate-third-party-notices.sh` |

依赖方向严格单向：L01/L02 零内部依赖，L03 用它们，L04 用 L03，L05/L06 独立走 NVML 线，L07/L08 是外围。没有任何包反向 import，层次与目录一一对应——新代码放哪一层基本没有歧义。

## 3. sysfs 侧主线①：nvpci 枚举与寄存器访问

`pkg/nvpci/nvpci.go` 是门面：包级常量 `PCIDevicesRoot = "/sys/bus/pci/devices"`（`nvpci.go:34`）是全部枚举的锚点。公开入口 `GetNvidiaDeviceByPciBusID`（`nvpci.go:258`）委托给内部递归实现 `getNvidiaDeviceByPciBusID`（`nvpci.go:284`）——这是全库最核心的 162 行：按 PCI 地址拼出 sysfs 路径，逐属性读取 vendor/device/class/NUMA/IOMMU 组并填充 `NvidiaPCIDevice` 全字段。SR-IOV 信息由 `getSriovInfoForPhysicalFunction`（`nvpci.go:530`）扫 `virtfn*` 符号链接推导出 PF/VF 关系。分类视图 `Get3DControllers`（`nvpci.go:449`）、`GetVGAControllers`（`nvpci.go:466`）、`GetNVSwitches`（`nvpci.go:483`）、`GetGPUs`（`nvpci.go:500`）都在此文件。`mlxpci.go` 把枚举面扩到 Mellanox：常量 `PCIMellanoxVendorID = 0x15b3`（`mlxpci.go:26`），`GetNetworkControllers`（`mlxpci.go:34`）与 `GetPciBridges`（`mlxpci.go:50`）。

寄存器级访问在 L02：`mmio/mmio.go` 的 `OpenRO/OpenRW`（`mmio.go:88/93`）封装 mmap 打开设备内存区域；`Slice/LittleEndian/BigEndian`（`mmio.go:97/101/105`）**返回新视图而非复制**——与 bytes 包同构的接口设计。`resources.go` 封装 BAR 资源（`MemoryResource.OpenRW`，`resources.go:41`；`GetTotalAddressableMemory`，`resources.go:89`）。`config.go:89` 的 `GetPCICapabilities` 沿 capability 链表指针（`config.go:31-33`）解析标准+扩展配置空间。

`pkg/pciids` 解决"这个 vendor/device ID 是什么"：`pciids.go:186` 的 `//go:embed default_pci.ids` 把 42856 行数据库快照嵌进二进制；运行时优先读发行版路径（Ubuntu `/usr/share/misc/pci.ids` 等，`pciids.go:178-181`），找不到才回退内置。查询入口 `NewDB`（`pciids.go:191`）与 `GetDeviceName`（`pciids.go:262`）。

## 4. sysfs 侧主线②：nvmdev vGPU 与 nvpassthrough 直通

`pkg/nvmdev` 抽象 vGPU mediated device：常量 `mdevParentsRoot = "/sys/class/mdev_bus"`（`nvmdev.go:32`），`GetAllParentDevices`（`nvmdev.go:89`）枚举可创建 vGPU 的父 GPU，`GetAllDevices`（`nvmdev.go:123`）列现存 mdev，`NewDevice`（`nvmdev.go:145`）按类型创建实例（写 `create` 文件）。类型名解析有独立文法 `parseMdevTypeName`（`nvmdev.go:242`）。

`pkg/nvpassthrough` 处理 GPU VFIO 直通（交给虚机）。核心是 **sysfs 写协议**：`BindToVFIODriver`（`nvpassthrough.go:170`）先 `unbind` 解绑当前驱动（`nvpassthrough.go:219`）、再 `bind` 到 vfio-pci（`nvpassthrough.go:222`）；SR-IOV 场景还要对每个 aux function 重复（`nvpassthrough.go:240-244`）。绑定前 `kmod.go:34-35` 以 `chroot <hostRoot> modprobe <module>` 按需加载内核模块——chroot 是为了在容器内对宿主 root 操作。

匹配引擎 `modalias.go`：`parseModAliasString`（`modalias.go:56`）分解 `pci:v...d...sv...sd...bc...sc...i...` 七字段串；`getVFIOAliases`（`modalias.go:135`）从 `lib/modules/<kernel>/modules.alias`（`modalias.go:141`）提取 `alias vfio_pci:` 前缀条目（前缀常量 `modalias.go:31`）；`FindBestVFIOVariant`（`nvpassthrough.go:125`）按通配符逐字段命中数打分选最佳驱动变体。匹配语义由 `modalias_test.go:26` 起的表驱动用例覆盖。

## 5. NVML 侧主线：device 抽象、MIG 文法与 info 装配

`pkg/nvlib/device/device.go`（605 行）定义 `Device` 接口（`device.go:28`），MIG 四方法 `GetMigDevices/GetMigProfiles/VisitMigDevices/VisitMigProfiles`（`device.go:34-42`）**同时存在于两个 receiver**：单设备视角 `device`（`device.go:319/357/419/432`）与全库视角 `devicelib`（`device.go:501/522/563`，回调多一个设备序号参数）——对外 API 与单设备视角双实现，图谱把同名方法合并为单节点是建模简化，读源码须按 receiver 区分。工厂 `New`（`pkg/nvlib/device/api.go:50`）默认跳过 "DGX Display" 设备（`pkg/nvlib/device/api.go:63-64`）。

MIG profile 有完整文法：`parseMigProfile`（`mig_profile.go:254`）→`parseMigProfileFields`（`mig_profile.go:320`）→`parseMigProfileField`（`mig_profile.go:303`）→`parseMigProfileAttributes`（`mig_profile.go:355`）四级解析 `3g.20gb` / `Cg.Gb+Cg.Gb` 格式；`Matches`（`mig_profile.go:215`，接口声明 `mig_profile.go:43`）**保持属性出现顺序**——这是 k8s 设备插件匹配语义的关键。`identifier.go` 把用户输入分类：`IsGpuIndex`（`identifier.go:31`）、`IsMigIndex`（`identifier.go:39`）、`IsUUID/IsGpuUUID/IsMigUUID`（`identifier.go:53/59/71`）。

`pkg/nvlib/info` 是平台探测与装配：`property-extractor.go` 四探针 `HasDXCore`（`property-extractor.go:38`）、`HasNvml`（`:50`）、`HasTegraFiles`（`:69`）、`HasAnIntegratedGPU`（`:106`）各返回 `(bool, 证据串)` 二元组；`resolver.go` 定义预设 `PlatformAuto/NVML/Tegra`（`resolver.go:23-25`），`ResolvePlatform`（`resolver.go:36`）按属性组合决策（`resolver.go:57` 的 case 是判定核心）；`root.go` 的 `tryResolveLibrary`（`root.go:52`）经 `filepath.EvalSymlinks`（`root.go:86`）沿符号链接链解析真实库路径——容器内 `/usr` 与 host 路径映射就靠它找对 `libnvidia-ml.so`。`builder.go`+`options.go` 用函数式选项把这些依赖注入成 `infolib`。

## 6. 底座双基元：bytes 字节序对偶与 pciids 文法

`pkg/nvpci/bytes` 是全库最底层。接口三件套 `Raw/Reader/Writer` 汇成 `Bytes`（`bytes.go:25-48`），构造器 `New/NewLittleEndian/NewBigEndian`（`bytes.go:74/79/88`）。两个实现 **13 个方法完全同名对偶**（实测各 13 个，`grep -c` 验证）：`native.go`（78 行）按主机序直读；`swapbo.go`（112 行，`type swapbo` 定义于 `swapbo.go:23`）是 "swapped byte order"——**与大端小端二元切换不同，它按目标端序逐字段换序**（`swapbo.go:27-80` 的 Read/Write8/16/32/64），服务 PMC 等寄存器的跨端读取。两实现的 `Slice/LittleEndian/BigEndian`（`swapbo.go:93/98/102`）也返回视图。

`pciids.go` 内嵌手写 lexer：`type scanner`（`pciids.go:50`）+ `readline`（`pciids.go:62`）+ `scanEntry`（`pciids.go:89`），按前导 tab 层数区分层级（`isLeadingOneTab/isLeadingTwoTabs`，`pciids.go:97-98`）——`pci.ids` 纯文本格式的完整文法实现，无任何第三方解析依赖。

## 7. 测试金字塔与工程化：无硬件怎么测

本仓最大工程特色是**无硬件测试金字塔**：`nvpci/mock.go` 的 `AddMockA100`（`mock.go:70`）在临时目录伪造 A100 完整 sysfs PCI 树（`CreateMockA100SysfsFiles`，`mock.go:143`），含 SR-IOV（`sriov_totalvfs/sriov_numvfs` 写入，`mock.go:113-131`）；`nvpci_mock.go`（458 行）以 mockery 风格给每方法配 `Get*Calls` 记录器；`nvmdev/mock.go` 同法伪造 mdev 树。上层 nvmdev/nvpassthrough 的集成测试全靠这套伪造树。注意 `nvlib/info/property-extractor_mock.go`（178 行）是 `api.go` go:generate **moq** 指令产物——与手写的 mockery 风格并存，两种 mock 范式不是同一工具链。

构建与 CI：`Makefile:15` include `versions.mk` 作单点版本源（`GOLANG_VERSION ?= 1.27.1`，`versions.mk:25`）；`update-pcidb` target（`Makefile:84`）刷新内置 pci.ids 快照；`check-vendor` 用 `git diff --exit-code` 验证 vendor 目录一致。GitHub Actions 四 job（lint/check-vendor/test/build）每个都重复 "Get Golang version" 步骤从 versions.mk grep（`.github/workflows/golang.yml:33-36`）；GitLab 侧仅 `include .common-ci.yml`（`.gitlab-ci.yml:15-16`）。法务：529 行纯 bash 的 `hack/generate-third-party-notices.sh`（SPDX 短语表+动态围栏）生成 394 行 `THIRD_PARTY_NOTICES.md`；`NOTICE:1-3` 是 pci.ids 的 BSD-3 分发声明（见勘误）。

## 8. 新人上手路线与常见坑

按 14 步 tour 精简为 5 段路线：

1. **先立骨架**（tour step-1）：读 `README.md` + `go.mod`，记住两条主线分工；
2. **读底座**（step-2/3）：`bytes/bytes.go` 接口 → `mmio/mmio.go` → `resources.go`，理解"视图非复制"的设计语言；
3. **读枚举核心**（step-4/5）：`nvpci.go:284` 的 162 行 + `mock.go` 伪造树，跑 `pkg/nvpci` 测试体会无硬件测试；
4. **按需选主线**（step-6~10）：做 vGPU 读 `nvmdev`，做直通读 `nvpassthrough/modalias.go`，做设备插件读 `nvlib/device`+`info`；
5. **收尾工程面**（step-13/14）：改依赖跑 `make vendor check-vendor`，改数据跑 `make update-pcidb`。

常见坑：① 图谱/IDE 里 `VisitMigDevices` 等同名方法看似重复定义，实为双 receiver；② mmio/bytes 的 `LittleEndian()` 是视图切换不是数据转换；③ kmod 加载走 chroot，容器内测试需给 `WithHostRoot`；④ 想当然以为库会读 `/proc/driver/nvidia`——全部枚举只走 sysfs；⑤ `versions.mk` 与 go.mod 的 Go 版本（1.27.1 vs 1.26.0）分别是工具链与语言最低版本，升级时要同步改。

> 勘误与甄别清单见 `../README.md`；三篇深讲见 `../explain/`。
