# 讲透 NVIDIA/go-gpuallocator

> 定位：NVIDIA 官方 Go 单节点 GPU 分配决策库（只决策不指派，README.md:7-10）。微仓：生产代码 8 文件，主包 6 + internal/links 2 + 示例 1。
> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/go-gpuallocator` @ 9cae2256724fc41e0439f743fcbb6ae4bbeec455

## 全链状态表

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki/ | ✅ 完成 | 21 页 100%（10-30 全量清单轮 A 层补抓，INDEX+_coverage-check 在目录内） |
| 图谱 | ✅ 完成 | 156n/264e/4层/5步/0 issues，fingerprints 30@9cae2256，仓内 .understand-anything/ |
| onboarding/ONBOARDING.md | ✅ 完成 | 8 节 8510 非空白字符，107 个唯一行号锚全源码核实 |
| explain/ | ✅ 完成 | 3 篇（01 主包 API/02 策略族与拓扑/03 示例与工程链），六节结构，各 2200+ 字符 |
| 本 README | ✅ 完成 | 状态表+勘误清单 |

## 一句话架构

```
调用方 ──> Allocator(账本: remaining/allocated) ──Policy──> {Simple | BestEffort | StaticDGX×3}
                                                    │              │评分依据
                                                    │              ▼
                                                NewDevices ──> internal/links{GetP2PLink,GetNVLink,PciInfo}
                                                    │              │ NVML + sysfs(numa_node)
                                                    ▼
                                             go-nvml/go-nvlib(vendor)
```

发现（NewDevices O(n²) 填链路表 device.go:114-134）→ 策略（BestEffort 划分枚举+NVLink×100/PCIe×10-60 评分寻优 besteffort_policy.go:307-377）→ 分配（AllocateSpecific 账本双写 allocator.go:112-113）/释放（Free UUID+指针双校验 allocator.go:125-128）。

## 源码级勘误清单（全部行号实证 @9cae2256）

1. **"rm/ 多后端（静态/NVML/共享）" 不存在**：全仓无 rm/ 目录（find 实证）。本仓真实三族=Policy 三实现族（Simple/BestEffort/StaticDGX），"静态"实指 staticdgx_policies.go 的硬编码 DGX 表。图谱 L02 层描述与任务书前提均失真，产物已按源码改写。
2. **README.md:55 Policy 签名过时**：文档写 `Allocate(devices []*Device, num int)`，实际 `Allocate(available, required []*Device, size int)`（gpuallocator/allocator.go:31）——缺 required 参数。
3. **README.md:46-48 AllocateSpecific 返回类型过时**：文档写返回 `[]*Device`，实际返回 `error`（gpuallocator/allocator.go:99）。
4. **图谱 tour "三示例" 失真**：examples/ 下只有 devices 一个示例（examples/devices/main.go 为唯一示例文件，L03 fileCount=2 计入了入口函数节点）。
5. **DGX-2 策略零测试覆盖**：`NewDGX2VoltaNode()` 是 `return nil` 空壳（gpuallocator/common_test.go:410-412）；staticdgx_test.go 只覆盖 DGX-1 Pascal/Volta。
6. **NewStaticDGX1Policy 非法 GPUType 返回 nil 而非 error**（gpuallocator/staticdgx_policies.go:28）——nil Policy 延迟到 Allocate 调用才 panic。
7. **Details() nil 解引用风险**：CPUAffinity 可为 nil（internal/links/pciinfo.go:55 NUMA 缺失返 nil），而 Details() 无条件 `*d.CPUAffinity`（gpuallocator/device.go:181）——无 NUMA 信息的机器上 examples/devices 会 panic。
8. **Makefile 死目标**：build-image 引用不存在的 images/devel/Dockerfile（Makefile:19），且 :92-95 引用 versions.mk 未定义的 CLIENT_GEN/CONTROLLER_GEN/MOQ 版本变量——模板继承残留，docker-% 全系不可用。
9. **CPUAffinity/NumaNode/SocketAffinity 三名一数**：internal/links/pciinfo.go:52-59 把 NUMA 节点号直接当 CPU 亲和值，device.go:181 打印成 SocketAffinity——语义漂移，非真亲和掩码。
10. **go.mod 语言版本滞后**：声明 go 1.21（go.mod:3），工具链实为 1.24.4（versions.mk:24，CI 从此 grep）。
11. **GetNVLink 不处理 NVSwitch**：TODO(klueska) 注释钉版（internal/links/device.go:198），计数靠远端 PCI BusID 匹配（:154-197），NVSwitch 全互联语义不完备（NOTES-DIGEST 佐证）。
12. **图谱 hub 笔误**：hub 笔记称 DGX-1 Volta fixture "按 {0,3},{1,2} 配对表编排"——该配对实为 staticdgx 策略 validSets（staticdgx_policies.go:76）；测试 fixture 实为每卡 4 条 NVLink 网状（common_test.go:302-340）。
13. **deprecated 字段仍被消费**：nvlibDevice 的 UUID/PCI/CPUAffinity 标注 deprecated（device.go:26-28），但 Details() 与 BestEffort 评分路径仍用。
14. **Allocate 失败即 panic**：策略输出违约走 panic 不走 error（allocator.go:90-91）——自研 Policy 者的安全契约。

## 精读要点（NOTES-DIGEST 14 条中经源码复核存真者）

- 双注入口设计：函数式选项 WithNvmlLib/WithDeviceLib（options.go:34-45）+ 包级变量 nvmlNew（device.go:256-258，测试唯一通道 setNVMLNewDuringTest，device_test.go:84-93）。
- besteffort 以别名 nvml 导入 internal/links（besteffort_policy.go:9-12，TODO 待迁 go-nvlib）；iterateGPUSets 迭代展开替代 size 层嵌套 for（:164-213）；划分枚举 padding+首元素固定法去重（:241,275-285）。
- 类型别名挂方法惯用法：`type PciInfo nvml.PciInfo`（pciinfo.go:30）；NumaNode 直读 sysfs（:65）。
- NVML 引用计数语义：go-nvml Init 直通 C 层无 Go 计数（vendor init.go），NewAllocator→build 双 Init+defer Shutdown+finalizer Shutdown 依赖 C 层配平。
- 测试拓扑 fixtures 手工编排：DGX-1 Pascal/Volta 各约 120 行 8×8 双向链路（common_test.go:168-408）；表驱动执行器 RunAllocTests/RunPolicyAllocTests（:63-111）。
- CI Go 版本单点真源：四作业均 grep versions.mk（golang.yml:36,59,74,90）；golangci-lint v9 + gosec，examples/ 豁免 lint。

## 阅读路线

ONBOARDING.md（全貌+坑清单）→ explain/01（Allocator/Policy/Device）→ explain/02（BestEffort 算法+links 探测）→ explain/03（示例+构建链）→ 源码按 allocator.go→device.go→besteffort_policy.go 顺序半日通读。
