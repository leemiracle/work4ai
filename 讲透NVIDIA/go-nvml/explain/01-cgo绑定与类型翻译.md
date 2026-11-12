# 01 · cgo 绑定与类型翻译（nvml.go / types_gen.go / const.go / cgo_helpers_static.go）

## 角色定位

图谱 L03 层的 C-Go 接壤带。nvml.go（4035 行）是 c-for-go 从补丁后 nvml.h 自动生成的 **428 个 cgo wrapper 全集**（grep `^func nvml` 实测 428），文件头 nvml.go:15 WARNING 声明禁止手改；types_gen.go:1828 行与 const.go:2725 行是配套的类型/常量翻译层。这层不做任何业务逻辑，只做"C 调用能在 Go 里编译通过"这一件事——Go 惯用性全部留给上层 device.go 手工包装层。

## 内部结构

文件顶部的 cgo preamble 是全文件的灵魂（nvml.go:21-25）：linux 下 `LDFLAGS: -Wl,--export-dynamic -Wl,--unresolved-symbols=ignore-in-object-files` 允许链接期不解析 NVML 符号（运行期才 dlopen），darwin 换 `-undefined,dynamic_lookup`（nvml.go:22）；`CFLAGS: -DNVML_NO_UNVERSIONED_FUNC_DEFS=1`（nvml.go:23）让 C 头只暴露版本化符号。wrapper 模式高度一致：参数先转 C 类型（`cFlags, _ := (C.uint)(Flags), cgoAllocsUnknown`），调 C 函数，返回值断言转 `Return`——见 nvmlInitWithFlags（nvml.go:41）。

类型双轨制：小写 `nvml*` 是内部句柄/原始结构（types_gen.go:8 `nvmlDevice`、:12 `nvmlGpuInstance`、:1630 `nvmlGpuInstanceInfo`），大写版本是公开 API 结构，二者靠 convert 方法族双向转换。const.go 是错误码与枚举唯一权威源（生成头声明）；const_static.go:19 `SYSTEM_PROCESS_NAME_BUFFER_SIZE = 256` 与 :22-24 `STRUCT_VERSION`（反射取结构体大小 `| version<<24` 拼 NVML 结构版本号）是仅有的两个手工补充。

## 外部连接

上游消费补丁后的 pkg/nvml/nvml.h（nvml.go:24 `#include "nvml.h"`）；下游被 device.go/system.go/unit.go/vgpu.go/gpm.go/event_set.go 的手工包装层全量调用（图谱高扇出枢纽第一位）；cgo_helpers_static.go:73 `packPCharString`、:86 `unpackPCharString`、:91 `malloc` 三个助手被全部字符串类 wrapper 复用。

## 数据流

以 `nvmlErrorString`（nvml.go:54）为例：C 返回 `*C.char` → `packPCharString` 用 stringHeader（cgo_helpers_static.go:28）直接重排 `Data/Len` 指针构造 Go string，**零拷贝**（前提：C 侧是 NVML 管理的静态缓冲，永不释放）。出参 buffer 类 API 则反向：上层 make Go slice → 取 `&slice[0]` 传 C → C 回写。数组类 API 有 count 回写语义：`GetTopologyNearestGpus`（device.go:263）成功后必须 `deviceArray[:count]` 裁剪（device.go:275），同型修复还有 device.go:1343 GetSamples、system.go:81——2026-09 PR#212 才补齐的 off-by-truth 坑。

## 设计决策

①**零拷贝 vs 安全**：packPCharString 的 unsafe 指针重排是文档化的 cgo 惯用法，换取热路径无分配；代价是调用方绝不能持有返回串跨 NVML 调用。②**cgoAllocsUnknown 占位**（cgo_helpers_static.go:26）：c-for-go 生成模板里本应追踪 C 分配的位置统一丢弃，简化生成器。③**types.go→types_gen.go 走 `go tool cgo -godefs`**（Makefile:166-168）：保证结构体布局与平台 ABI 对齐而非手写。④event_set.go:102 用 `runtime.Pinner` 固定 Go 指针传 C，是 cgo 安全新姿势（替代 C.malloc 中转）。

## 新人提示

读这层的正确顺序：先 nvml.go:21-25 preamble（不懂 LDFLAGS 就不懂整个加载模型），再挑一个 wrapper 对照 C 原型读，最后读 cgo_helpers_static.go 全文（仅 134 行）。**永远不要手改这四个生成文件**——改了会被 `make bindings` 覆盖；要改行为去 device.go 包装层，要改类型去 gen/nvml/nvml.yml。调试 cgo 崩溃时先怀疑字符串所有权与 Pinner 生命周期。锚 15 处。
