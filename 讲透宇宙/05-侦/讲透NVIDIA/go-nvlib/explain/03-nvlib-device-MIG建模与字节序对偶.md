# 03 · nvlib/device 的 MIG 建模与 bytes 字节序对偶

## 角色定位

本文横跨两条线：`pkg/nvlib/device` 是 NVML 侧主线的设备抽象层（k8s-device-plugin 的 MIG 共享直接消费它），`pkg/nvpci/bytes` 是 sysfs 侧最底层的字节序基元（PMC 寄存器跨端读取保证）。二者放在一起讲，因为它们体现同一设计母题：**用接口 + 成对实现把"同一契约的两种视角/两种语义"分开**。

## 内部结构

device 包主文件 `device.go`（605 行）定义 `Device` 接口（`device.go:28`）。MIG 四方法（`GetMigDevices/GetMigProfiles`，`:34-35`；`VisitMigDevices/VisitMigProfiles`，`:41-42`）存在**双 receiver 同名实现**：单设备视角 `(d *device)`（`:319/357/419/432`）与全库视角 `(d *devicelib)`（`:501/522/563`，回调多一个 `(i int, dev Device)`）。工厂 `New`（`pkg/nvlib/device/api.go:50`）默认跳过 "DGX Display"（`pkg/nvlib/device/api.go:63-64`），`WithSkippedDevices`（`:78`）可覆盖。

MIG 文法四级解析：`parseMigProfile`（`mig_profile.go:254`）→ `parseMigProfileFields`（`mig_profile.go:320`）→ `parseMigProfileField`（`mig_profile.go:303`）→ `parseMigProfileAttributes`（`mig_profile.go:355`），吃下 `3g.20gb` 与 `Cg.Gb+Cg.Gb` 两态格式；`Matches`（`mig_profile.go:215`，接口在 `mig_profile.go:43`）保持属性出现顺序。`identifier.go` 的判定族：`IsGpuIndex`（`identifier.go:31`）、`IsMigIndex`（`identifier.go:39`）、`IsUUID`（`identifier.go:53`）、`IsGpuUUID`（`identifier.go:59`）、`IsMigUUID`（`identifier.go:71`）。

bytes 包：接口 `Bytes`（`bytes/bytes.go:48`）由 `Raw/Reader/Writer`（`bytes.go:25/30/39`）组成，构造器 `New/NewLittleEndian/NewBigEndian`（`bytes.go:74/79/88`）。两实现 **13 个方法同名对偶**（实测）：`native.go`（78 行）主机序直读；`swapbo.go` 的 `type swapbo`（`swapbo.go:23`）按目标端序**逐字段换序**（Read8/16/32/64 与 Write8/16/32/64，`swapbo.go:27-80`），`Slice/LittleEndian/BigEndian`（`swapbo.go:93/98/102`）链式返回视图。

## 外部连接

device 包上游是 go-nvml 的 `nvml.Interface`（`pkg/nvlib/device/api.go:50` 注入），info 包的 builder 装配 devicelib 后供 GPU Operator 判定平台（`info/builder.go`）；identifier 的输出直接对应 `nvidia.com/mig-1g.10gb` 这类 k8s 资源名的解析需求。bytes 包被 `nvpci/config.go`（`config.go:89`）与 `resources.go`（PMC 读取判字节序）消费；mmio 子包镜像同一接口（`mmio/mmio.go:97-105`）。

## 数据流

MIG 清点流：`devicelib.VisitMigDevices`（`device.go:501`）遍历 GPU → 每卡调 `device.VisitMigDevices`（`device.go:319`）→ NVML 查 MIG 实例 → `GetMigProfiles` 去重（`device.go:432`）→ `Matches`（`mig_profile.go:215`）比对用户请求串（如 `1g.10gb+none`），属性序敏感。寄存器流：`MemoryResource` 打开 BAR → 读 PMC 前先试字节序 → 命中 swap 语义则换 `swapbo` 视图 → Read32 落在 `swapbo.go:38` 的逐字段重排上，数值自动还原。

## 设计决策

① **双 receiver 而非泛型**：Go 1.26 仍选了两套同名方法表达"库级/设备级"视角，签名差异（回调 3 参 vs 4 参）在编译期强制定位；② **Matches 保序**：`1g.10gb+2g.20gb` 与 `2g.20gb+1g.10gb` 不等价，因为内核枚举 MIG 布局时属性有序——这是 k8s 插件匹配语义的关键；③ **swapbo 非大端**：它不是 BigEndian 的别名，而是"按目标端序逐字段换"的策略对偶（`swapbo.go:27-80`），故能处理字段宽度混合的寄存器块；④ **跳过 DGX Display 默认开**（`pkg/nvlib/device/api.go:63-64`）：显示设备不参与 MIG 语义，误纳入会污染资源清点。

## 新人提示

`mig_profile_test.go` 与 `identifier_test.go`（109 行）是文法与分类语义的活教材，改 `Matches` 前先跑。查"为什么我的 GPU 没出现"时第一站是 `api.go:63` 的跳过名单。拿纸笔跟踪一次 `swapbo.Read32`（`swapbo.go:38`）的字节重排胜过读十遍注释；`bytes.go:59` 的 `init()` 注册默认实现，替换走构造器。
