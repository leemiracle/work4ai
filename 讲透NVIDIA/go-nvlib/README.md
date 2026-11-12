# 讲透 NVIDIA/go-nvlib

> GPU 管理软件的 Go 包集合：sysfs 侧（PCI 枚举/vGPU/VFIO 直通）+ NVML 侧（设备/MIG/平台探测）双主线。
> 仓库：github.com/NVIDIA/go-nvlib @ d3f4ca8 · 上游：构建于 go-nvml v0.13.4-1 之上（`go.mod:5`）

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| 知识图谱 | 仓内 `.understand-anything/knowledge-graph.json`（309 节点 / 535 边 / 8 层 / 14 步 tour，validator 0 issues） | ✅ fingerprints 64 文件基线 @d3f4ca82 |
| 深度导览 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8 节，40+ 行号锚） | ✅ 2026-11-08 |
| 文件精讲 | [explain/](explain/) 3 篇（nvpci 枚举与寄存器 / nvmdev+nvpassthrough / device MIG 与字节序对偶） | ✅ 2026-11-08 |
| 勘误甄别 | 见下方（7 条，全部源码锚实证） | ✅ 2026-11-08 |

## 速览

- **两主线**：sysfs 侧 `pkg/nvpci`+`nvmdev`+`nvpassthrough`+`pciids`（NVML 不覆盖的独立价值）；NVML 侧 `pkg/nvlib/device`+`info`（k8s-device-plugin / gpu-operator 直接消费）。
- **底座母题**：接口 + 成对实现——bytes 的 native/swapbo 13 方法同名对偶、device 的 MIG 双 receiver、mockery 与 moq 两代 mock 并存。
- **测试哲学**：无硬件金字塔——`pkg/nvpci/mock.go:70` 的 `AddMockA100` 伪造整棵 sysfs 树（含 SR-IOV，`pkg/nvpci/mock.go:113-131`），上层包全部可离线集成测试。

## 勘误与甄别（7 条，均经源码核实）

1. **非 NVML 采样/监控库**。go-nvlib 不是 DCGM 类采样库，也不是 go-nvml 的 fork——`README.md:3-5` 定位是"GPU 管理软件的 Go 包集合"；约一半能力（vGPU mdev、VFIO 直通、sysfs 枚举）与 NVML 无关。按"NVML 封装"理解会漏掉 L03/L04 整条线。
2. **MIG 方法双 receiver 同名，图谱合并是建模简化**。`VisitMigDevices/GetMigDevices/VisitMigProfiles/GetMigProfiles` 在 `device`（`pkg/nvlib/device/device.go:319/419/432`）与 `devicelib`（`device.go:501/563`）两个 receiver 上各有一份、回调签名不同（3 参 vs 4 参）。IDE 跳转/图谱节点看似"重复定义"，实为库级与单设备两级 API。
3. **两种 mock 样板并存，非同一工具链**。`pkg/nvpci/nvpci_mock.go`（458 行，mockery 风格：每方法配 `Get*Calls` 记录器）是手写维护的；`pkg/nvlib/info/property-extractor_mock.go`（178 行）是 `info/api.go` 的 go:generate **moq** 指令产物。改接口时前者手改、后者重新 generate，流程不同。
4. **NOTICE 是数据文件声明，不是项目声明**。`NOTICE:1-3` 全文只讲一件事：`pkg/pciids/default_pci.ids` 按 3-clause BSD 由 PCI ID Project 维护分发。项目自身许可是根 `LICENSE`（Apache-2.0），第三方明细在 `THIRD_PARTY_NOTICES.md`（394 行，由 `hack/generate-third-party-notices.sh` 生成）。把 NOTICE 当项目法务入口会答错再分发义务。
5. **default_pci.ids 是数据不是代码**。42856 行占全仓行数绝对大头，但语义是 `//go:embed`（`pkg/pciids/pciids.go:186`）进二进制的离线快照；运行时优先读发行版路径（`pciids.go:178-181`），内置库仅兜底。按"代码行数"评估本仓规模严重失真，`make update-pcidb`（`Makefile:84`）才是它的更新通道。
6. **swapbo 不是"大端模式"的别名**。`bytes/swapbo.go` 与大端小端二元切换无关——它按目标端序**逐字段换序**（`swapbo.go:27-80`），与 `native.go` 构成 13 个同名方法的对偶实现，服务 PMC 等字段宽度混合寄存器的跨端读取。称其为 "big-endian backend" 是错的。
7. **mmio/bytes 的 `Slice()`/`LittleEndian()` 返回视图而非复制**。`mmio/mmio.go:97/101` 与 `swapbo.go:93/98` 全是零拷贝新视图，写子视图会写穿到原映射。当成"切片拷贝"使用会引入静默数据污染。

## 延伸阅读

- 三篇精讲：[01 nvpci sysfs 枚举与寄存器访问](explain/01-nvpci-sysfs枚举与寄存器访问.md) · [02 nvmdev+nvpassthrough vGPU 与 VFIO 直通](explain/02-nvmdev-nvpassthrough-vGPU与VFIO直通.md) · [03 device MIG 建模与字节序对偶](explain/03-nvlib-device-MIG建模与字节序对偶.md)
- 生态位：同 org 的 `go-nvml`（下层数据源）、`k8s-device-plugin`/`gpu-operator`/`kubevirt-gpu-device-plugin`/`vgpu-device-manager`（典型消费者）、`mig-parted`（MIG 配置工具，与本仓 MIG 抽象互补）。
