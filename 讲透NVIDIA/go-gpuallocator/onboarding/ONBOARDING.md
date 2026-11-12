# go-gpuallocator 新人上手指南（ONBOARDING）

> 仓：`github.com/NVIDIA/go-gpuallocator` @ 9cae2256 · 图谱 156n/264e/4层/5步 · 全部行号锚经源码核实（2026-11）
> 勘误前提：任务书与图谱 L02 层所称 "rm/ 多后端（静态/NVML/共享）" 在本仓**不存在**——全仓没有 rm/ 目录，"静态"实指 `staticdgx_policies.go` 的硬编码 DGX 拓扑表。本文按源码实际结构讲述。

## 1. 一页纸定位：这是什么库

go-gpuallocator 是 NVIDIA 官方的**单节点 GPU 分配决策库**（Go）。README 第一段就划清了边界：它"不做实际 allocation，只运行决定选哪些 GPU 的算法"（README.md:7-10）。换句话说，它是**决策层**——输入"节点上有哪些 GPU + 要几块"，输出"建议选哪几块"；真正把 GPU 绑给容器/进程是调用方（典型如 Kubernetes 设备插件生态）的事。README.md:15-19 明确举例：K8s 系统决定给容器几块 GPU 后，用本库按拓扑亲和性挑出最优子集。

三条边界钉版：
- **单节点，不是集群调度器**——没有跨机概念，一切发生在 `Allocator` 所在节点；
- **只决策，不指派**——不碰 cgroup、不碰容器运行时；
- **策略可插拔**——核心接口只有一个 `Policy.Allocate`（gpuallocator/allocator.go:31），内置三种策略族全部实现它。

代码体量极小：生产代码仅 8 个 .go 文件（主包 6 + internal/links 2 + 示例 1），其余全是测试、构建配置与 vendor（go-nvlib/go-nvml/testify，go.mod:5-9）。它是微库而非框架——读完本指南即可通读全仓。

## 2. 对外 API：Allocator 与 Policy 两级抽象

**`Allocator` 是主对象**（gpuallocator/allocator.go:14-20）：持有 `GPUs []*Device`（节点全量设备）、`policy`（策略）与 `remaining`/`allocated` 两个 `DeviceSet`（分配状态账本）。三个动作构成生命周期：
- `Allocate(num int)`（allocator.go:85-95）：委托策略选设备，再走 `AllocateSpecific` 落账；若策略返回的设备不在 remaining 中——这是**内部一致性错误**——直接 `panic`（allocator.go:90-91），不返回错误；
- `AllocateSpecific(devices ...*Device) error`（allocator.go:99-116）：逐一校验设备在 `remaining` 里（allocator.go:103），然后原子地 `Insert` 进 allocated、`Delete` 出 remaining（allocator.go:112-113）；
- `Free(devices ...*Device)`（allocator.go:119-133）：以 UUID 反查 allocated 并要求**指针同一**才归还（allocator.go:125-128）——同 UUID 的伪造设备会被静默忽略（有专门测试 allocator_test.go:38-50 验证）。

**`Policy` 是策略接口**（allocator.go:24-32），真实签名是 `Allocate(available []*Device, required []*Device, size int) []*Device`——注意**README.md:55 的签名是过时的**（缺 `required` 参数）。`required` 表示"必须包含的设备"（K8s 已分配给容器一部分后追加的场景）。

**构造器三件套**：`NewSimpleAllocator()`/`NewBestEffortAllocator()`（allocator.go:36-44）是便捷封装；通用入口 `NewAllocator(policy)`（allocator.go:47-68）做三件事：① `nvml.New()+Init()`（allocator.go:48-51）；② `NewDevices(WithNvmlLib(nvmllib))` 枚举设备（allocator.go:53-55）；③ `runtime.SetFinalizer` 注册 GC 兜底 Shutdown（allocator.go:62-65）——用户忘了显式释放也不会泄漏 NVML 句柄。注意 NVML C 库自带引用计数：NewAllocator 的 Init 与 build() 内部再次 Init+defer Shutdown（device.go:93-98）最终依赖 C 层计数平衡到零。

## 3. 设备模型与发现链：Device/DeviceList/DeviceSet

**`Device`**（gpuallocator/device.go:18-22）组合而非继承：内嵌 `nvlibDevice`（device.go:24-34）再挂 go-nvlib 的 `device.Device` 接口，外加 `Index` 与 `Links map[int][]P2PLink`（到其它 GPU 的链路表）。`nvlibDevice` 里的 UUID/PCI.BusID/CPUAffinity 三个字段被注释标为**deprecated**（device.go:26-28）——应改用接口方法，但目前 `Details()` 打印与 BestEffort 评分仍在消费它们。

**发现链** `NewDevices(opts ...Option)`（device.go:76-89）：应用函数式选项 → 默认 `nvmlNew()` 与 `device.New(nvmllib)`（device.go:81-86）→ 委托 `build()`。选项就两个（gpuallocator/options.go:34-45）：`WithNvmlLib` 注入 NVML 实现、`WithDeviceLib` 注入设备枚举库——测试可测性的关键注入口。`build()`（device.go:92-137）里最重的一步是 **O(n²) 双重遍历**填充 `Links`（device.go:114-134）：对每对设备调 `links.GetP2PLink` 与 `links.GetNVLink`，非 Unknown 才入表。这就是"分配前先付一次拓扑探测成本"的设计。

**集合类型**：`DeviceList` 有序列表（device.go:70）；`DeviceSet` 以 UUID 为键的 map（device.go:73），配套 `Insert/Delete/Contains/ContainsAll/SortedSlice`（device.go:201-253，SortedSlice 按 Index 排序）。`NewDevicesFrom(uuids)`（device.go:140-149）从 UUID 列表过滤构建，`Filter` 要求 UUID 必须存在否则报错（device.go:151-168）；注意它内部调 `NewDevices()` **不带任何选项**（device.go:144），mock 注入只能靠包级变量 `nvmlNew`（device.go:256-258，测试手法见第 6 节）。

## 4. 拓扑探测层：internal/links

这是库的"物理感知"来源，两个文件：

**P2PLinkType 枚举**（internal/links/device.go:27-57）：PCIe 侧 7 档（Unknown/CrossCPU/SameCPU/HostBridge/MultiSwitch/SingleSwitch/SameBoard）+ NVLink 1-18 条共 18 档，一个 uint 枚举通吃两类链路。`GetP2PLink`（device.go:116-139）经 NVML 拓扑公共祖先级别映射——`TOPOLOGY_NODE` 处有注释"NVML_TOPOLOGY_CPU was renamed NVML_TOPOLOGY_NODE"（device.go:131），是 NVML 上游改名的活化石。`GetNVLink`（device.go:142-201）用状态机式 switch 逐条累计 NVLink 计数（一次 BusID 匹配升一档），**尾部挂着 TODO(klueska): Handle NVSwitch semantics**（device.go:198）——NVSwitch 全互联拓扑下此计数语义不完备，是已知边界。

**PciInfo 工具**（internal/links/pciinfo.go）：Go 类型别名惯用法（pciinfo.go:30，`type PciInfo nvml.PciInfo`）——为外部结构体挂方法而不包装。`BusID()`（pciinfo.go:34-48）截 C 字符串、小写化、裁掉 `0000` 域前缀；`NumaNode()`（pciinfo.go:63-74）**绕过 NVML 直读 sysfs** `/sys/bus/pci/devices/<busid>/numa_node`（pciinfo.go:65）；`CPUAffinity()`（pciinfo.go:52-59）把 NUMA 节点号直接当亲和值返回（负值返 nil）——命名三处漂移（CPUAffinity/NumaNode/SocketAffinity 实为同一个数），且 `Device.Details()` 无条件解引用它（device.go:181），**NUMA 信息缺失的机器上跑示例会 panic**，这是真风险点。

## 5. 三种内置策略族

| 策略 | 文件 | 拓扑感知 | 思路 |
|---|---|---|---|
| Simple | gpuallocator/simple_policy.go:13-35 | 否 | 排序取前 size 台，required 优先（simple_policy.go:32-33） |
| BestEffort | gpuallocator/besteffort_policy.go:37-98 | 是 | 组合枚举+链路评分全局寻优 |
| StaticDGX×3 | gpuallocator/staticdgx_policies.go | 硬编码 | 按 DGX 机型查有效索引组合表 |

**BestEffort 是算法重心**。注释（besteffort_policy.go:26-36）讲清了它为何不用贪心：链路非层次化，单集合最高分不等于整体最优。算法三步：① `iterateGPUPartitions` 枚举全部等尺寸划分（besteffort_policy.go:218-299），先 padding 到整除（besteffort_policy.go:241），用"首元素固定法"去重等价划分（besteffort_policy.go:275-276），并剪枝"部分 padding"的集合（besteffort_policy.go:282-285）；② 对每个划分算总分，取**全局最优划分**（besteffort_policy.go:57-69）——这保证"假设未来分配也都是同尺寸"时整体最优；③ 在最优划分内取最高分集合返回，且过滤掉含 padding 的集合（besteffort_policy.go:74-83）。评分表在 `calculateGPUPairScore`（besteffort_policy.go:307-377）：NVLink 每条 100 分（1-18 条=100-1800 分），PCIe 按层级 10-60 分（CrossCPU=10 … SameBoard=60）；pair 的 Links 必须双向对称否则 panic（besteffort_policy.go:316-319）。`iterateGPUSets`（besteffort_policy.go:164-213）用 indices/level 数组**迭代展开 size 层嵌套循环**（注释在 besteffort_policy.go:173-186），避免递归开销。

**StaticDGX 是历史方案**：三张硬编码 validSets 表——DGX-1 Pascal 双卡组合 {0,2},{1,3},{4,6},{5,7}（staticdgx_policies.go:50-55）、DGX-1 Volta {0,3},{1,2},{4,7},{5,6}（staticdgx_policies.go:74-79）、DGX-2 十六卡（staticdgx_policies.go:98-104）。核心查表在 `findGPUSet`（staticdgx_policies.go:111-156）。两个坑：① `NewStaticDGX1Policy` 遇未知 GPUType **返回 nil 而非 error**（staticdgx_policies.go:28），调用方拿到 nil Policy 要到 Allocate 时才炸；② size 不在表键里（如 3）时 `validSets[size]` 为 nil，静默返回空分配——非 2 的幂尺寸必然失败。`GPUType` 枚举只有 Pascal/Volta 两值（staticdgx_policies.go:10-13），**没有 Ampere 及以后**：新机型请用 BestEffort。

## 6. 测试体系：变量注入 + 手工拓扑 fixtures

**mock 注入手法**：包级函数变量 `nvmlNew`（device.go:256-258）是唯一注入口；测试用 `setNVMLNewDuringTest` 临时替换并返回还原闭包（gpuallocator/device_test.go:84-93），配合 vendor 里的 go-nvml 官方 `mock.Interface`（device_test.go:28-52 伪造单设备 NVML）。策略测试则完全绕开 NVML——手工构造拓扑。

**拓扑 fixtures**（gpuallocator/common_test.go）：`TestGPU`/`TestNode` 类型（common_test.go:17-18）+ `NewTestGPU`（common_test.go:113-122）+ 双 receiver 的 `AddLink`（common_test.go:124-131，TestGPU 与 TestNode 各一个，Go 无跨 receiver 重载）。四个构造器：`New4xRTX8000Node`（common_test.go:141-166）、`NewDGX1PascalNode` 与 `NewDGX1VoltaNode`（common_test.go:168-287/289-408，各约 120 行手工编排 8×8 双向链路——DGX-1 Volta 每卡 4 条 NVLink 网状互联），以及 **`NewDGX2VoltaNode` 直接 `return nil`**（common_test.go:410-412）——DGX-2 策略因此**零测试覆盖**（staticdgx_test.go 只测 DGX-1 两代）。

**覆盖面**：BestEffort 最厚——除 1/2/4/8 卡分配矩阵（besteffort_test.go:380-536），还单测两个枚举器（besteffort_test.go:130/228）、最优划分保持性（besteffort_test.go:353）、padding 排除（besteffort_test.go:549）。表驱动执行器 `RunAllocTests`/`RunPolicyAllocTests`（common_test.go:63-111）是共享基建。

## 7. 工程链：Makefile / versions.mk / CI / vendor

- **模块**：`github.com/NVIDIA/go-gpuallocator`（versions.mk:18），go.mod 声明 go 1.21（go.mod:3）但工具链实为 1.24.4（versions.mk:24）——语言版本声明滞后。依赖三件：go-nvlib v0.10.0 / go-nvml v0.13.0-1 / testify v1.11.1（go.mod:5-9），**vendor 目录提交入库**。
- **Makefile**：`make build` 用 `GOOS=linux` 硬约束（Makefile:26,28-29）；`make test` 先 build 再 `go test -coverprofile`（Makefile:58-59）；`make vendor` + `check-vendor` 用 `git diff --quiet` 锁 vendor 与 go.mod/go.sum 零漂移（Makefile:65-71）；`TARGETS` 列表经 `patsubst` 批量生成 `docker-%` 目标（Makefile:22-24,100-110）。**坑**：`build-image` 引用不存在的 `images/devel/Dockerfile`（Makefile:19）且用了 versions.mk 未定义的 CLIENT_GEN/CONTROLLER_GEN/MOQ 版本变量（Makefile:92-95）——模板继承残留，docker 系目标实际跑不通。
- **CI 四作业**（.github/workflows/golang.yml）：check（golangci-lint@v9 + check-vendor，:28-49）、test（:50-65）、build（:66-80）、check-third-party-notices（:81-96）。Go 版本由 CI **从 versions.mk grep 出来**（golang.yml:36）——单点真源。lint 启用 gosec/gocritic 等（.golangci.yml）。
- **许可合规**：`make third-party-notices` 调 hack/generate-third-party-notices.sh（Makefile:78-79），用 go-licenses@v2.0.1（versions.mk:26，安装到 bin/，Makefile:73-76）生成 THIRD_PARTY_NOTICES.md，CI 强制无漂移（Makefile:81-86）。

## 8. 新人路线图与坑清单

**推荐阅读顺序**（半日通读）：① README.md 建立定位 → ② allocator.go（134 行，全部 API）→ ③ device.go 的 NewDevices/build（发现链）→ ④ internal/links 两文件（拓扑来源）→ ⑤ besteffort_policy.go（算法重头）→ ⑥ 跑 `cd examples/devices && go run .`（examples/devices/main.go:26-38，NewDevices+Details 十行讲完最简用法）→ ⑦ common_test.go 看 fixtures 怎么伪造 DGX。

**坑清单（全部源码实证）**：
1. 全仓**没有 rm/ 目录**，也没有"共享后端"——别按 k8s-device-plugin 的心智模型找资源管理器；本库的"状态管理"就是 Allocator 里两个 DeviceSet。
2. README 的 Policy 与 AllocateSpecific 签名过时（README.md:46-48,55），以 allocator.go:31/:99 为准。
3. `NewStaticDGX1Policy` 非法类型返 nil（staticdgx_policies.go:28）；StaticDGX 只认 1/2/4/8(/16) 卡。
4. `Device.Details()` 在 NUMA 缺失机器上会 nil 解引用 panic（device.go:181 ← pciinfo.go:55 返 nil）。
5. GetNVLink 不处理 NVSwitch（internal/links/device.go:198）；NVLink 计数靠远端 PCI BusID 匹配，多 GPU 同 BusID 不存在所以可行，但语义只到"条数"。
6. `Allocator.Allocate` 失败路径是 panic 不是 error（allocator.go:90-91）——策略实现者务必保证返回设备 ⊆ available。
7. DGX-2 策略零测试（common_test.go:410-412 空壳 fixture），改动它没有安全网。
8. 跑 make build 即出 linux 二进制约束；docker-% 目标因缺 Dockerfile 不可用（Makefile:19）。
