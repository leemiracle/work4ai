# 04 · 测试组织与双 NVML 镜像（internal.go / mock 物料 / *_test_helpers / tests/ 集成）

## 角色定位

go-dcgm 的核心工程命题：**在没有 GPU 的 CI 里测一个 GPU 绑定库**。答案是四层测试物料——生产包注入 API、mockgen 全家桶、`_helpers.go` 物料下沉、NVSDM mock 配置——外加 tests/ 集成包用 nvidia-smi 子进程做**独立真值通道**。两份 NVML 头镜像则是排障最易踩的坑。

## 内部结构

- **注入 API（internal.go）**：`CreateFakeEntities`（internal.go:56）造假 GPU 实体（构造 `dcgmCreateFakeEntities_v2` internal.go:62-63 调 C API :82）；`InjectFieldValue`（internal.go:114）往字段管理器注值——单测"无中生有"出设备+遥测。
- **mockgen 全家桶**：`native_calls_generate_test.go:4` 的 `//go:generate` 指令；产物 `native_calls_mock_test.go` 986 行（:1 `DO NOT EDIT.`，:4 命令含 12 个 `-mock_names`），12 个 ops 接口各得 Mock+MockRecorder。
- **9 个 `*_test_helpers.go`**：cpu/device_info/diag/field_policy/field_values/health/mndiag/process_info/profile——文件名不以 `_test.go` 结尾故**编译进生产包**，小写 `test` 前缀符号仅包内可见（cgo 桩需 C 编译期在场）。
- **门控脚手架（test_utils.go）**：`runOnlyWithLiveGPUs`（test_utils.go:70）跳过无 GPU、`withInjectionGPUs`（:81）启用注入、`withNvsdmMockConfig`（test_utils.go:185）经 `DCGM_NVSDM_MOCK_YAML`（常量 test_utils.go:29-30）加载 mock 拓扑——`testdata/one_switch.yaml`（消费点 api_test.go:64，vendor_id 0xbaca/lid 1）驱动 DCGM 内置网络设备模拟。
- **包内 46 个 `_test.go`**（实测，图谱称 43）分五层：unit 纯逻辑（api_unit_test/field_values_unit_test）、实机集成（admin_test/policy_test）、回调背压（field_values_limit_test）、Benchmark（field_values_performance_test）、别名回归（alias_resolution_test）。
- **tests/ 集成包**：12 个 Go 文件与 CLI 样例一一对应；bazel 标签 `manual`+`requires-dcgm`（tests/BUILD.bazel:27-30）；`nvsmi.go:11` 定义 `bin="nvidia-smi"`，nvsmi.go:33 `exec.Command` 子进程查询——**真值对照走独立于绑定的通道**。

## 外部连接

双 NVML 镜像在此交汇：`pkg/dcgm/nvml.h`（12600 行完整版）与 `pkg/dcgm/dcgm_nvml.h`（12790 行内嵌裁剪版）来源不同、代际可能不同步——**NVML 符号排障第一步是确认看的哪份**。注入通路在 C 头层预留：`dcgm_test_apis.h`/`dcgm_test_structs.h`/`dcgm_structs_internal.h`（条件包含 nvml_injection.h）。mock 物料服务全包：`getPciBandwidthWithOps`（device_info.go:147）注入 Mock 即离线可测。

## 数据流

离线：unit test→造假实体（internal.go:56）→注值（internal.go:114）→纯函数断言（deviceStatusFromValues device_status.go:156）；或 Mock 录制期望→被测函数→断言序列。在线：`runOnlyWithLiveGPUs`（test_utils.go:70）门控→真实 DCGM→与 nvsmi.go 子进程输出 A/B 对照（两通道不一致即绑定层 bug）。NVSDM：withNvsdmMockConfig（test_utils.go:185）注入 yaml→DCGM 模拟 fabric 设备。

## 设计决策

1. **注入 API 进生产包（internal.go）**而非 build tag：cgo 的 C 物料必须编译期在场，运行时才能调用；小写命名控制可见性，公开面零污染。
2. **`_helpers.go` 命名騙术**：go 工具链按 `_test.go` 后缀排除生产编译——`_test_helpers.go` 不匹配该后缀但语义上是测试物料，是 cgo 库下沉物料的组织手法（9 个文件一致遵守）。
3. **双 mock 分层**：mockgen 生成 ops 接口 mock（行为级）+internal.go 注入（数据级），前者测控制流后者测数据流。
4. **nvidia-smi 独立真值（nvsmi.go:11）**：绑定库的自证不可信，第三方通道对照是集成测试的黄金标准。

## 新人提示

写新测试先选层：纯逻辑→`*_unit_test.go` 零依赖直接写；需要设备→withInjectionGPUs（test_utils.go:81）；需要网络拓扑→withNvsdmMockConfig+yaml（api_test.go:64 是模板）；必须真机→`runOnlyWithLiveGPUs`（test_utils.go:70）并挂 requires-dcgm 标签。改 ops 接口后记得重跑 `go generate`（native_calls_generate_test.go:4），mock 不同步是最常见的 CI 红。**报告"NVML 符号未定义"时先查两份镜像**（nvml.h vs dcgm_nvml.h），再查 dlopen 的实际库版本。
