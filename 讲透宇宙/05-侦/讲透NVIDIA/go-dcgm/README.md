# 讲透 NVIDIA go-dcgm（DCGM 的 Go 绑定）

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/go-dcgm` @ commit `d6ecefea`（go 1.27.2，2026-11 快照）
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki 抓取 | ✅ 完成 | `deepwiki/`（INDEX + wiki 全页 + _coverage-check） |
| understand 图谱 | ✅ 完成 | 仓内 `knowledge-graph.json`：**602 节点 / 3001 边 / 12 层 / 16 步导览**，validator 0 issues，fingerprints 基线 **178 文件 @ d6ecefea** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节，9798 非空白字符，58 个 file:line 锚，全部源码核实） |
| explain 精讲 | ✅ 4/4 完成 | `explain/01..04-*.md`，六节结构、行号锚全源码核实（下表索引） |
| 勘误清单 | ✅ 9 条 | 见下文，全部经本仓源码一手核实 |

## explain 索引（4 篇）

| # | 篇目 | 主题 | 锚数（去重） |
|---|---|---|---|
| 01 | cgo 核心与回调跳板 | dlopen 三模式/引用计数门面/12 ops 接口/三 C 跳板 | 32 |
| 02 | 字段体系与 gen-fields 生成链 | dcgm_fields.h 解析状态机/3301 行生成物/对象池 | 20 |
| 03 | 策略健康诊断与 REST 注入 | 七类条件分发器/符号探测降级/deps 注入范式 | 27 |
| 04 | 测试组织与双 NVML 镜像 | internal.go 注入/mockgen/生产编译 helpers/nvsmi 真值 | 14 |

字数口径：**不计空格字符**。四篇含锚总量 2572-2633（行号锚密度所致的口径上浮，系列既往同款现象）；**剔锚正文 2006-2257**，全部落在 1500-2500 区间，双口径并记。

## 16 步图谱导览速览

项目定位（README/CONTRIBUTING 字段五步法）→ C 契约镜像（agent/structs/errors/api_export）→ NVML 双镜像与测试三头 → gen-fields 生成链 → 会话生命周期（dlopen 三模式+引用计数）→ cgo ops 底座 → 三回调跳板 → 设备信息与状态 → 拓扑/CPU/MIG/进程 → 字段体系（watch+池化）→ 策略分发器 → 健康/诊断/错误元数据 → 注入与 mock 物料 → 包内测试组织 → REST 解耦范式 → 集成测试与构建闭环。

## 勘误清单（9 条，全部源码一手核实）

以下勘误针对图谱层/导览描述与常见直觉口径，每条给出可复核锚点（仓库根相对路径）：

1. **ops 接口是 12 个不是 15 个**：图谱 L03 层描述与 tour step-06 均称"15 个细分 ops 接口"；实测 `pkg/dcgm/native_calls.go` 只有 12 个 `interface{}`（sessionCalls native_calls.go:19 → topologyOps :108），mockgen 生成命令（native_calls_mock_test.go:4）的 `-mock_names` 也恰好列 12 个——15 是图谱高估。
2. **可执行示例是 9 个不是 13 个**：图谱 samples 层称"13 个可执行示例"；实测 `samples/` 下 9 个 main.go（8 个 CLI：deviceInfo/diag/dmon/health/hostengineStatus/policy/processInfo/topology + restApi 1 个服务端）。samples/README.md 共 23 个标题（`##` 节仅 2 个），"13"在仓内无对应实体，属图谱高估。
3. **pkg/dcgm 测试文件是 46 个不是 43 个**：图谱 pkg-tests 层称"43 个 _test.go"；实测 `ls pkg/dcgm/*_test.go | wc -l` = 46（含 unit/集成/回调/Benchmark/别名回归五类）。
4. **不存在 `Client` 结构体**：图谱多个节点 summary 写"func (c *Client) WatchFields/HealthSet"式方法；实测全库无 `type Client`，全部 API 是包级函数（`pkg/dcgm/api.go:23-237` 的 26 个导出函数，`grep -rn "func (c \*Client)" pkg/dcgm` 零命中）。
5. **legacy 字段是 43 个不是 44 个**：`pkg/dcgm/legacy_fields.csv` 共 44 行**含表头** `name,id`（legacy_fields.csv:1），数据行 43 个（:2 起）；"44 个旧字段名"把表头数进去了。
6. **CI-Dockerfile 代际漂移（重要）**：`.gitlab-ci.yml:14/16/17` 声明 CUDA 13.3.1 / Go 1.26.7 / DCGM 4.6.1-1，且 :38-41 引用 `--target samples` 构建阶段；当前 `.devcontainer/Dockerfile` 是 CUDA 13.4.3（Dockerfile:3，按 sha256 钉）、DCGM 4.7.0-2（:5）、Go 1.27.2（hack/versions.env:1）且**无 samples target**——GitLab 侧是旧版多阶段构建残留，照着改版本会改错地方。
7. **`_test_helpers.go 是生产编译单元（刻意设计非事故）**：9 个 `*_test_helpers.go`（cpu/device_info/diag/field_policy/field_values/health/mndiag/process_info/profile）不以 `_test.go` 结尾故进入生产构建——cgo 桩需要 C 编译期在场，小写 `test` 前缀符号仅包内可见（如 `pkg/dcgm/cpu_test_helpers.go` 直接 `#include` C 头）。这是把测试物料下沉包内的组织手法，不是"忘了加 _test"。
8. **dlopen 三模式 + 协议降级链**：libdcgm 并非链接而是 `dlopen` 加载（admin.go:91，库名 libdcgm.so.4 admin.go:86，LDFLAGS admin.go:20-21）；Standalone 连接按 `dcgmConnect_v3` 符号可用性自动降级 V2（admin.go:190-191/226-227），V3 需 DCGM 4.5.0+（admin.go:229）——排查连接问题先看这三层。
9. **nvsmi 是独立真值通道 & one_switch 是 NVSDM mock**：`tests/nvsmi.go:11/33` 用子进程 `nvidia-smi` 而非 NVML 绑定做 A/B 对照（绑定自证不可信）；`pkg/dcgm/testdata/one_switch.yaml` 经环境变量 `DCGM_NVSDM_MOCK_YAML`（test_utils.go:29-30）加载，消费点 api_test.go:64——它模拟的是 NVSDM fabric 设备（vendor_id 0xbaca），不是 GPU。

## 与 DCGM 本体的关系

本仓是 `NVIDIA/DCGM`（C++ 引擎本体，另有 `../../../../讲透宇宙/05-侦/讲透NVIDIA//DCGM/` 全链产物）的 Go 消费端绑定：契约镜像 vendor 自引擎头文件，`libdcgm.so.4` 即 datacenter-gpu-manager-4 包（devcontainer 钉 4.7.0-2）。dcgm-exporter/GPU Operator 经此库取数——上游引擎勘误见 DCGM 仓 README 的 16 条清单。

## 上手路径（新人 30 分钟版）

1. 读 `README.md` + `CONTRIBUTING.md`（字段更新五步法）；
2. devcontainer 起环境（自带 DCGM 4.7.0-2 + CUDA 13.4.3）；
3. 跑 `samples/dmon` 感受监控输出；
4. 精读 `onboarding/ONBOARDING.md` 第 2-3 节（会话与 cgo 核心）；
5. 按需进入 `explain/` 四篇深读。
