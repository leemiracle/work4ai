# 讲透 NVIDIA/go-nvml

NVML（NVIDIA Management Library）官方 Go 绑定：C 真相源 nvml.h → c-for-go 生成 428 个 cgo wrapper → 手工包装层 → 九接口契约 → moq 替身全家桶。仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/go-nvml`。

## 全链状态表

| 阶段 | 状态 | 产物 | 口径 |
|---|---|---|---|
| deepwiki | ✅ 2026-10-26 | `deepwiki/` 21 文件（18 结构页全命中，真一百分终判） | dw_fetch_mcp + dw_reconcile |
| understand 图谱 | ✅ 2026-11-08 | 仓内 `.understand-anything/knowledge-graph.json` | **269 节点/1193 边/12 层/16 步 tour，validator 0 issues**，fingerprints 85 文件@`1a1e86da`（tag v0.13.4-1） |
| onboarding | ✅ 2026-11-08 | `onboarding/ONBOARDING.md` | 不计空格 7650 字符，8 节，**51 锚/26 文件**（全部源码核实） |
| explain | ✅ 2026-11-08 | `explain/` 4 篇 | 每篇 2100-2600 不计空格字符，六节结构，锚 21/30/20/13 |
| 勘误 | ✅ 见下 | 本文件 §勘误 | 11 条，含图谱构建勘误 4 条 + 源码级勘误 7 条 |

## explain 索引

1. `explain/01-cgo绑定与类型翻译.md` —— nvml.go 428 wrapper 的 preamble 灵魂、类型双轨制、packPCharString 零拷贝、count 回填裁剪
2. `explain/02-版本协商双机制与dl加载.md` —— 编译期宏 + 运行期 dl.Lookup 热升级、pkg/dl 的 LockOSThread、refcount/errorStringFunc 生命周期
3. `explain/03-九接口契约与moq替身.md` —— zz_generated.api.go 九接口（Interface 407/Device 280）、814 方法 mock 控制面板、fixture 三层装配
4. `explain/04-bindings管线与update-nvml-h.md` —— nvml.h 双镜像、sed+spatch 分工、c-for-go 工具链钉死、CUDA redist 升级线

## 勘误（11 条，全部源码/图谱实测）

**图谱构建勘误（消费图谱者必读）**

1. **scanner Go 包级 import 过度展开含 _test 假边**：图谱 1193 边中 344 边（29%）touch `_test` 文件——Go 测试文件与生产代码同包，scanner 把 `_test.go` 的 import 也展开成包级依赖边（如 device_test.go→mock）。**这些边不代表生产依赖方向**，做依赖分析时须先剔除 _test 端点边再下结论。
2. **巨文件 sub-node 预算采样**：device.go 635 函数只入图 6 个 sub-node、nvml.go 428 函数→6、mock/interface.go 18919 行/814 方法仅少量入图。批分析的 sub-node 预算对巨文件是采样而非全集——**图谱是结构图不是函数索引**，"某函数在哪"必须回源码 grep。
3. **Makefile 无 file 节点、versions.mk 靠手工**：Makefile 的 19 个节点全为 type=pipeline（scanner 对 Makefile 不产 file 节点）；versions.mk 因 tree-sitter 无 mk 支持系手工分析（批笔记钉版）。mock/gpus/*.go 为纯 var 配置块，tree-sitter 提取不到函数，图中近乎空壳——fixture 语义要看 var 块本身（a100.go:24-65）。
4. **nvml.h 双镜像是 patch 产物不是拷贝**：pkg/nvml/nvml.h（15772 行）= gen/nvml/nvml.h（15744 行）+ 净 28 行/17 个 diff hunk，由 Makefile:156-160 的 sed（handle 包裹，:159）+ spatch（匿名结构体具名化，:160）两步生成。直接 diff 两文件看到的差异全是 patch-nvml-h 的产物（如 pkg/nvml/nvml.h:158-166 的 nvmlDevice_t handle 包裹、:821-828 的 nvmlGpuThermalSettingsSensor_t），**不是上游版本差异**；gen/ 才是真相源。

**源码级勘误**

5. **版本协商符号数：grep 会数错**。lib.go updateVersionedSymbols（lib.go:205）grep `l.dl.Lookup` 得 23 处，但 lib.go:236 的 `nvmlDeviceRemoveGpu_v2` 被注释，活跃探测实为 **22** 个符号族（首个是 `err :=` 声明易被 `^	err =` 正则漏计）。
6. **"九接口"实为 9+1**：zz_generated.api.go 的九接口之外，api.go:32-34 还有第十个 `ExtendedInterface`（仅 LookupSymbol）。其方法清单与 gen/nvml/generateapi.go:46 的排除清单**手工同步**（api.go:27-30 TODO 自认未自动化）——给 Interface 加方法漏改任一边都会造成 mock/接口漂移。
7. **Shutdown 行为已变（PR#206，2026-10 合入）**：未 Init 直接调 `Shutdown()` 现在返回 `ERROR_UNINITIALIZED`（init.go:44），不再是静默成功。网上旧资料与旧版 README 描述的"幂等 Shutdown"已过时。
8. **数组 API 的 count 裁剪修复（PR#212，2026-09 合入）**：GetTopologyNearestGpus（device.go:275）、GetSamples（device.go:1343）、SystemGetTopologyGpuSet（system.go:81）三处成功时按 C 侧回写 count 裁剪 slice。**v0.13.4 之前版本这些 API 返回的 slice 可能含零值尾巴**——历史代码若依赖旧长度语义需复查。
9. **GOLANG 双版本口径**：go.mod 声明 `go 1.20`（最低兼容），versions.mk 的 GOLANG_VERSION=1.27.1（构建工具链）。讨论"这个库要求什么 Go 版本"时要先分清口径；CI 以 versions.mk 为准（golang.yml 的 Get Golang version 步骤读它）。
10. **update-nvml-h 交互式设计**：Makefile:210 的 `read -p` 选版交互无法在非交互 CI/脚本中执行；CUDA_VERSION 钉死 13.4.2（Makefile:200），升级头文件必须本地跑 `make update-nvml-h`。产物头两行出处注释（Makefile:233-234 注入）是判断 pkg/nvml/nvml.h 版本的唯一可靠依据。
11. **c-for-go 工具链钉 commit 而非版本号**：versions.mk 的 `C_FOR_GO_TAG ?= 8eeee8c3...` 是裸 commit hash——c-for-go 上游无 semver 纪律，**换 tag 重新生成可能产出 diff**（生成器行为漂移）；升级工具链必须整管线回归（`make clean && make bindings && make test-bindings`）。

## 上手入口

- 5 分钟：`examples/devices/main.go`（Init→DeviceGetCount→DeviceGetHandleByIndex→Shutdown 全闭环，27-46 行）
- 30 分钟：README.md:109-231（生成原理）+ lib.go 全文（300 行，版本协商心脏）
- 深入：按 explain 01→02→03→04 顺序读

（2026-11-08 生成，图谱 commit `1a1e86da`）
