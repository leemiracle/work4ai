# 04 · bindings 生成管线与 update-nvml-h（Makefile / gen/nvml / docker / versions.mk）

## 角色定位

图谱 L02+L11 层：把"C 头文件→Go 绑定"工业化的完整流水线。NVML API 随 CUDA 版本持续生长（gen/nvml/nvml.h 已 15744 行），人工同步 428 个 wrapper 不现实；本管线让"升级到新 nvml.h"变成三条 make 命令。全部编排在 263 行 Makefile，工具链钉死在容器里保证可复现。

## 内部结构

**nvml.h 双镜像**是理解管线的钥匙：gen/nvml/nvml.h 是真相源（update-nvml-h 从 NVIDIA CUDA redistributable JSON 下载，Makefile:199-202 CUDA_VERSION 钉 13.4.2）；pkg/nvml/nvml.h 是补丁产物——**15744 → 15772 行，净 +28 行、17 个 diff hunk**，由 `make patch-nvml-h` 两步生成（Makefile:156-160）：①sed 正则（Makefile:159）把 `typedef struct nvmlXxx_st* nvmlXxx_t;` 包裹成带 handle 字段的结构（实证：pkg/nvml/nvml.h:158-166）；②spatch（Makefile:160）应用 gen/nvml/anonymous_structs.cocci（100 行）把匿名结构体提取成具名类型（pkg/nvml/nvml.h:821-828 `nvmlGpuThermalSettingsSensor_t`）——cocci 用 fresh identifier `ST =~ "^nvmlGenerated_struct___"` 生成唯一类型名，python 段拼接命名，这是 sed 正则做不到的**语义级**补丁。

管线主干：`bindings: .create-bindings .strip-autogen-comment .strip-nvml-h-linenumber`（Makefile:162）→ `c-for-go -out pkg gen/nvml/nvml.yml`（Makefile:165）产 nvml.go/const.go/types_gen.go → `go tool cgo -godefs types.go > types_gen.go`（Makefile:166-168）固化 ABI 类型 → 删中间产物（Makefile:170）。generateapi.go（420 行）随后反向 AST 解析生成九接口（generateapi.go:301-312）。头文件升级线 `update-nvml-h`（Makefile:210）用 `read -p` **交互式**选版（非交互 CI 跑不了），wget tar.xz 后 sed 注入两行 NVML VERSION 出处头（Makefile:233-234）。

## 外部连接

上游输入：developer.download.nvidia.com 的 redistrib_$(CUDA_VERSION).json（Makefile:202，jq 提取 cuda_nvml_dev 包版本与相对路径）。工具链依赖全部钉死：versions.mk 的 C_FOR_GO_TAG 8eeee8c3（钉 commit 防 c-for-go 上游漂移）、GOLANG_VERSION 1.27.1；docker/Dockerfile.devel 单 stage ubuntu:22.04 装 coccinelle（Dockerfile.devel:25，供 spatch）、`go install c-for-go@${C_FOR_GO_TAG}`（Dockerfile.devel:44）、moq（Dockerfile.devel:46）——Darwin 上 jq/sed 不一致时走容器跑管线。下游产出直接喂给 01/02/03 篇的绑定层与接口层。CI（.github/workflows/golang.yml）四作业中 test 作业（golang.yml:52）全程容器化。

## 数据流

完整升级一次绑定：`make update-nvml-h`（拉新 nvml.h 进 gen/，写出处头）→ `make patch-nvml-h`（cp+sed+spatch 产 pkg/ 镜像）→ `make bindings`（c-for-go+cgo -godefs 产三巨头）→ `make generate`（moq 产 mock，Makefile:40）→ `make test-bindings`（Makefile:188）→ 人肉补 lib.go 探测清单与 device.go 包装（README.md:595-605）→ 生成产物提交回主干（README.md:630-649）。后处理目标 .strip-autogen-comment/.strip-nvml-h-linenumber（Makefile:162）剥 c-for-go 注释噪音。

## 设计决策

①**补丁产物而非 fork 头文件**：gen/ 存档上游原文，pkg/ 镜像可随时重建。②**sed+spatch 分工**：可枚举的 typedef 包裹用 sed，语义级的匿名结构体用 coccinelle——正则处理不了嵌套匿名 struct 的命名与引用一致性。③**工具链 commit 钉死+容器化**：c-for-go 无 semver 纪律，钉 tag 才可复现。④**生成产物进版本库**：消费方无需装工具链即可 build（go.mod 仅 `go 1.20`），代价是 diff 巨大。⑤出处头注入（Makefile:233-234）令双镜像版本可追溯。

## 新人提示

先 `make clean`（Makefile:151）清三巨头再 `make bindings` 走一遍，diff 产物理解每步。改 nvml.h 永远在 gen/ 侧，pkg/ 是只读派生。升级卡住按管线定位：patch 后 `diff gen/nvml/nvml.h pkg/nvml/nvml.h` 应恰好 +28 行型差异，否则 sed/cocci 没跑全。锚 25。
