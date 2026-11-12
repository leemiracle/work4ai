# 02 · nvmdev + nvpassthrough：vGPU 管理与 VFIO 直通

## 角色定位

这两个包是 go-nvlib 里"动手"的一层：`nvmdev` 管理 vGPU mediated device 的创建/删除/清点，`nvpassthrough` 把物理 GPU 交给虚拟机（VFIO 直通）。它们都构建在 `nvpci.Interface` 之上，把"sysfs 写协议"封装成 Go API——这正是 NVML 完全不覆盖、而 GPU Operator / kubevirt-gpu-device-plugin 天天要做的操作面。

## 内部结构

`nvmdev/nvmdev.go`（401 行）锚定 `mdevParentsRoot = "/sys/class/mdev_bus"`（`nvmdev.go:32`）。`New` 工厂（`nvmdev.go:67`）收函数式选项，`WithNvpciLib`（`nvmdev.go:82`）注入 nvpci 实例。API 四组：`GetAllParentDevices`（`nvmdev.go:89`）枚举支持 mdev 的父 GPU、`GetAllDevices`（`nvmdev.go:123`）列现存实例、`NewDevice`（`nvmdev.go:145`）写 `create` 文件创建、`Device.Delete` 走 `remove`。类型体系有独立文法：`mdev.Type()`（`nvmdev.go:219`）经 `mdev_type` 符号链接解析，`parseMdevTypeName`（`nvmdev.go:242`）处理如 `nvidia-155` 的类型名；`driver()`（`nvmdev.go:252`）与 `iommuGroup()`（`nvmdev.go:260`）暴露归属信息。

`nvpassthrough/nvpassthrough.go`（470 行）核心是绑定协议：`BindToVFIODriver`（`nvpassthrough.go:170`）先 `unbind`（`:219`）再 `bind` 到 vfio-pci（`:222`）；SR-IOV 设备还要对每个 auxiliary function 重复一轮（`:240-244`）。通用版 `BindToDriver`（`:252`）供绑定任意驱动。`kmod.go` 的 `load`（`kmod.go:34`）以 `chroot <root> modprobe` 按需加载内核模块——chroot 让容器内操作宿主 root 生效。

## 外部连接

匹配引擎 `modalias.go` 是直通的"大脑"：`parseModAliasString`（`modalias.go:56`）分解七字段 `pci:v/d/sv/sd/bc/sc/i` 串；`getVFIOAliases`（`modalias.go:135`）定位 `lib/modules/<kernel>/modules.alias`（`modalias.go:141`）抽取 `alias vfio_pci:` 前缀条目（前缀常量 `modalias.go:31`）；`FindBestVFIOVariant`（`nvpassthrough.go:125`）按通配符逐字段命中数打分选出如 `vfio-pci-core` vs `vfio-pci` 的最佳变体。`WithLoadKernelModules`（`nvpassthrough.go:109`）与 `WithHostRoot`（`nvpassthrough.go:93`）是行为开关。两包测试都吃自己的 mock 树（`nvmdev/mock.go` 198 行）。

## 数据流

创建一个 vGPU：调用方给父 GPU PCI 地址 → `nvmdev` 读 `/sys/class/mdev_bus/<addr>/mdev_supported_types/` 得可用类型与余量 → `NewDevice`（`nvmdev.go:145`）生成 UUID 并写 `<type>/create` → 内核实例化 mdev → `GetAllDevices` 可见新设备，`driver()/iommuGroup()` 给后续直通提供参数。直通一块卡：`FindBestVFIOVariant`（`nvpassthrough.go:125`）按 modalias 打分选驱动 → 可选 `kmod.load` 预载模块（`kmod.go:34`）→ unbind/bind 协议执行（`nvpassthrough.go:219-222`）→ SR-IOV 卡继续对 aux function 循环（`nvpassthrough.go:240-244`）。

## 设计决策

① **先解绑再绑定**的写序（`nvpassthrough.go:219-222`）是 sysfs 驱动绑定的内核契约，顺序颠倒直接报错；② **modalias 打分而非精确匹配**：内核别名表存在大量通配条目，按七字段命中数选最优（`modalias.go:56` 的解析保证 `*` 语义）最贴近 `modprobe` 行为；③ **chroot 执行 modprobe** 而非信任 PATH，是 GPU Operator 容器化部署的现实约束；④ **mdev 类型走文法解析**（`nvmdev.go:242`）而非正则一刀切，为 NVIDIA 未来类型命名留余地。

## 新人提示

读 `modalias_test.go:26` 起的表驱动用例是理解七字段匹配语义的最快路径——292 行覆盖空串、多冒号、通配符各类边角。测 `nvpassthrough` 记得它依赖 mock 的 sysfs 树提供 `driver` 符号链接与 `driver_override` 文件；`WithLoadKernelModules` 默认关闭（`nvpassthrough.go:107` 注释），开测时要换假 modprobe。删除 mdev 前先查 `driver()`——已绑定驱动的 mdev 删除会失败，这是排障第一现场。
