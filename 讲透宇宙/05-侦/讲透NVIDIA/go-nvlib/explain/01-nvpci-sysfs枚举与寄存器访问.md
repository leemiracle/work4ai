# 01 · nvpci：sysfs PCI 枚举与寄存器级访问

## 角色定位

`pkg/nvpci` 是 go-nvlib 在 sysfs 侧主线的心脏：不依赖 NVML，直接以文件系统视角回答"这台机器上有哪些 NVIDIA PCI 设备、它们如何互联、寄存器里写了什么"。上游是 Linux sysfs 契约，下游是 `nvmdev`/`nvpassthrough` 两个操作包和 k8s GPU 设备插件一族的发现逻辑。没有它，vGPU 创建与 VFIO 直通都找不到操作对象。

## 内部结构

门面文件 `nvpci.go` 以常量 `PCIDevicesRoot = "/sys/bus/pci/devices"`（`nvpci.go:34`）锚定枚举根。公开入口 `GetNvidiaDeviceByPciBusID`（`nvpci.go:258`）委托内部 `getNvidiaDeviceByPciBusID`（`nvpci.go:284`）——全库最核心的 162 行，按 PCI 地址拼 sysfs 属性路径、填充 `NvidiaPCIDevice` 全字段（vendor/device/class、NUMA、IOMMU 组、BAR 资源）。SR-IOV PF/VF 关系由 `getSriovInfoForPhysicalFunction`（`nvpci.go:530`）扫 `virtfn*` 符号链接推导。分类视图四个：`Get3DControllers`（`nvpci.go:449`）、`GetVGAControllers`（`nvpci.go:466`）、`GetNVSwitches`（`nvpci.go:483`）、`GetGPUs`（`nvpci.go:500`）。`mlxpci.go` 扩展 Mellanox 面：`PCIMellanoxVendorID = 0x15b3`（`mlxpci.go:26`）、`GetNetworkControllers`（`mlxpci.go:34`）、`GetPciBridges`（`mlxpci.go:50`）。

寄存器访问三件在子包：`mmio/mmio.go` 的 `OpenRO/OpenRW`（`mmio.go:88/93`）mmap 设备内存；`resources.go` 把 BAR 包成 `MemoryResource`（`OpenRW`，`resources.go:41`）并聚合可寻址内存（`resources.go:89`）；`config.go` 的 `GetPCICapabilities`（`config.go:89`）沿 capability 链表指针（`config.go:31-33`）解析配置空间。

## 外部连接

nvpci 被 `nvmdev.New`（经 `WithNvpciLib`，`nvmdev.go:82`）与 `nvpassthrough.New`（`nvpassthrough.go:100`）注入为 `nvpci.Interface`——同接口可换 mock 实现。`pciids` 为枚举结果提供人类可读名：`NewDB`（`pciids/pciids.go:191`）+`GetDeviceName`（`pciids.go:262`）。测试侧 `mock.go` 的 `NewMockNvpci`（`mock.go:37`）与 `AddMockA100`（`mock.go:70`）伪造整棵 sysfs 树。

## 数据流

一次"发现 GPU"的数据流：`GetGPUs` 遍历 `/sys/bus/pci/devices/*` → 读 `vendor` 文件过滤 `0x10de`（NVIDIA）→ 对每个命中地址走 `getNvidiaDeviceByPciBusID`（`nvpci.go:284`）读十几个属性文件 → 读 `resource` 文件得 BAR 列表交给 `MemoryResources` → SR-IOV 设备再走 `virtfn` 符号链接补 VF 拓扑。寄存器读取则在拿到 BAR 后：`MemoryResource.OpenRO` → `mmio` 视图 → `LittleEndian()/BigEndian()`（`mmio.go:101/105`）切字节序视图 → 按 PMC 寄存器偏移读写。

## 设计决策

① **只信 sysfs 不碰 `/proc`**——枚举面单一可信源，代价是字段可用性随内核版本浮动；② **视图而非复制**：`mmio.Slice`（`mmio.go:97`）与 bytes 包的 `Slice`（`swapbo.go:93`）同构返回零拷贝视图，读寄存器热路径无分配；③ **读写分离的字节序**：跨端寄存器（PMC）由 swapbo 逐字段换序而非整块 byteswap，见 `bytes/swapbo.go:27-80`；④ **mock 即产品**：`CreateMockA100SysfsFiles`（`mock.go:143`）把 sysfs 契约固化为可执行规格，内核接口变更时测试先红。

## 新人提示

从 `nvpci_test.go` 入手最快：它演示如何用 `mock.go:70` 的 `AddMockA100` 起一棵树再走公开 API 断言。注意 `GetNvidiaDeviceByPciBusID`（`nvpci.go:258`）内部带 cache map 防重入；`mlxpci.go:68-73` 的 `IsNetworkController/IsPciBridge` 是设备侧判定，别与门面侧 Get* 混淆。改枚举字段时先确认 mock 树同步造了对应文件，否则 CI 会告诉你"属性不存在"。
