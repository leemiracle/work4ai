# 03 · 九接口契约与 moq 替身（zz_generated.api.go / api.go / mock/）

## 角色定位

图谱 L06 接口契约面 + L07 替身群。zz_generated.api.go（1252 行）把散落在 library/句柄方法上的 700+ API 收敛成**九个接口**，是外部消费方（k8s-device-plugin、gpuallocator 等）编程时真正 import 的类型面；mock/ 包（11 文件，interface.go 18919 行/814 方法）是这九接口的镜像替身——**mock 比 API 本体还大**，"可测试性优先"的极致体现。

## 内部结构

九接口按声明序：`Interface`（zz_generated.api.go:435，407 方法，库级入口）、`Device`（zz_generated.api.go:848，280 方法）、`GpuInstance`（zz_generated.api.go:1134）、`ComputeInstance`（zz_generated.api.go:1161）、`EventSet`（zz_generated.api.go:1169）、`GpmSample`（zz_generated.api.go:1183）、`Unit`（zz_generated.api.go:1192）、`VgpuInstance`（zz_generated.api.go:1205）、`VgpuTypeId`（zz_generated.api.go:1235）——MIG 三代际（GI/CI）、事件、GPM、SXM 机箱单元、vGPU 全覆盖。第十个 `ExtendedInterface` 在 api.go:32-34（仅 `LookupSymbol(string) error`），方法清单与 gen/nvml/generateapi.go:46 的 `Exclude: ["LookupSymbol"]` **手工同步**（api.go:27-30 TODO 自认未自动化——改一边漏一边的漂移点）。

mock/ 侧是 matryer/moq 产物：每文件一个接口，每方法一对 `Func` 回调字段 + `Calls` 记录切片，锁保护，**未设 Func 直接调用即 panic**（mock/device.go 惯例）。巨型 interface.go 对应 Interface 的 407 方法控制面板。装配线 server/shared.go：`NewServerWithGPUs`（shared.go:128）一站式建 Server（shared.go:76），三组 `SetMockFuncs` 按 receiver 区分（Go 无重载靠 receiver）：Server 级 shared.go:182、Device 级 shared.go:242、GpuInstance 级 shared.go:353。options.go 提供 WithGPUs 函数式选项。

## 外部连接

上游：generateapi.go 用 go/parser AST 解析 nvml.go（:301-312 `parser.ParseFile`，:419 `unicode.IsUpper` 判公开性）生成九接口；mock 全部以 zz_generated.api.go 为源。下游：`var _ Interface = (*library)(nil)`（lib.go:57）等编译断言保证实现同步；上游 gpuallocator 项目直接 import mock 包构造伪 NVML 环境（mock/README.md 有架构图）。fixture 供料线：gpus/ 纯 var 块（a100.go:25 `A100_PCIE_40GB` 起）→ server → dgxa100/dgxh100/dgxh200/dgxb200 整机预置（dgxb200.go:25 `New()`=8×B200_SXM5_180GB）。

## 数据流

测试方视角：`dgxb200.New()` → NewWithGPUs → server.NewServerWithGPUs 装配 Interface+Device+GI+CI 四层 mock → 被测代码拿到的 `nvml.Interface` 全部调用落到 Func 回调 → 断言 Calls 记录。包内单测走另一条轻量线：包级函数变量 stub 注入，如 device_test.go:90 `setNvmlDeviceGetTopologyCommonAncestorStubForTest`（device_test.go:82 用 defer 还原）；gpm.go:59-61 `nvmlGpmMetricsGetStub`/`nvmlGpmQueryDeviceSupportStub` 是产品代码里预留的注入口。真机测试由 nvml_test.go:23-26 `requireLibNvidiaML` 门控，无库环境 Skip。

## 设计决策

①**接口生成而非手写**：407 方法手写必漂移，AST 提取保证接口与实现永远同步（编译断言兜底）。②**moq 而非手写 fake**：814 方法手写不可维护；moq 的 panic-on-nil-Func 把"漏配回调"从静默零值变成显式失败。③**两种 mock 阈值**：普通 moq panic、`moq -stub` 零值——dynamicLibrary_mock.go（lib.go:41 生成指令）用后者，因 dl 接口的零值语义恰好正确。④**Exclude 机制**：LookupSymbol 属调试工具非常规管理面，故移出主接口。⑤fixture 用纯 var 配置块而非 builder：纯数据可 grep 可 diff。

## 新人提示

给被测代码造环境：小场景直接 `mock.NewInterfaceMock` 设几个 Func；整机场景用 dgxb200.New() 一行拿全套。排障口诀：mock panic=漏设 Func；Calls 数不符=被测代码多次调用或漏 Reset。给九接口加方法的唯一正道是改 generateapi.go 的排除/包含逻辑再 `make generate`，手改 zz_generated.api.go 会被覆盖。锚 18 处。
