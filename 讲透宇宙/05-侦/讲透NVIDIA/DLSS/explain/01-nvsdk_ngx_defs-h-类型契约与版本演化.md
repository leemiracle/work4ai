# 01 nvsdk_ngx_defs.h：全 SDK 的类型契约总根与版本演化史

## 角色定位

`include/nvsdk_ngx_defs.h`（859 行）是 DLSS SDK 全部 23 个头文件的公共依赖：门面（nvsdk_ngx.h/nvsdk_ngx_vk.h）、参数（params 族）、加载器（loader/standalone）、打包器（helpers 族）无一不 include 它。它不声明任何函数，只输出四类资产——版本宏、枚举与结构体、回调类型、参数键字符串宏。全仓 44 条 import 边里近半指向此文件，是图谱 L02 层的绝对核心。

## 内部结构

**版本契约**：`NVSDK_NGX_VERSION_API_MACRO = 0x0000015`（`include/nvsdk_ngx_defs.h:56`，即 1.5.0），`:50-55` 注释即版本日志——0x14 加应用日志回调、0x15 支持多 GPU（bug 3270533）。`:94` 把它转成 `NVSDK_NGX_Version` 枚举，应用 Init 时默认传 `NVSDK_NGX_Version_API`，驱动据此判断 SDK/驱动新旧配对。

**结果码族**（`:96-178`）：Success=0x1（`:99`），失败族基址 Fail=0xBAD00000（`:102`），后接 18 个失败码按位或递增——FeatureNotSupported、PlatformError、FeatureAlreadyExists、InvalidParameter、ScratchBufferTooSmall（`:130`）、OutOfDate（`:154`，"需要更新的驱动或特性库"）、OutOfGPUMemory、Denied（`:173`，"NVIDIA 限制该应用使用此特性"）、NotImplemented 等。配套判定宏用 `0xFFF00000` 掩码（`:183-184`）而非精确比较——为未来低位扩展留空间。

**Feature 枚举**（`:186-237`）：SuperSampling=1（DLSS-SR）、ImageSuperResolution=3（NGX 体系内的 NIS 变体）、ImageSignalProcessing=9（DLISP）、DeepResolve=10、FrameGeneration=11、DeepDVC=12、RayReconstruction=13（`:208-214`），尾部 `:232-236` 还为 SDK/Core/Unknown 留 32764-32766 段——"不是严格特性但需要同枚举标识"的系统组件。

**preset 演化化石**：`:70-88` 的 `NVSDK_NGX_DLSS_Hint_Render_Preset` 是 DLSS 模型代际活化石：A-D 已删除（`:73-76` 注释 directing 改用 J/K）、E/F Deprecated、G/H/I "勿用回退默认"、J=10（`:82`，鬼影略少但闪烁多）、K=11（`:83`，transformer 基底、DLAA/Balanced/Quality 默认、画质最佳但性能更贵）、L=12 Ultra Perf 默认、M=13 Perf 默认。配套 `:848-853` 六个质量档 preset 参数键。`:60-66` 的 `SR_DEPRECATED_SHARPENING`（C++14 `[[deprecated]]`）标记锐化已废弃，`:296` 的 DoSharpening flag 同被标记。

## 外部连接

被 nvsdk_ngx.h（`:75` include）、loader.h（`:16`）、standalone_cuda.h（经 standalone_common/loader 链）、全 helpers 族直接依赖；defs_vk.h/defs_dlssd.h/defs_dlssg.h 是它的per-特性扩展（各自再被 vk.h 与 dlssd/dlssg helpers 引用）。`:552-559` 的 D3D 类型前向声明（ID3D11Texture2D/ID3D12Resource 等）让本文件不必包含 D3D 头。

## 数据流（参数键如何被消费）

`:572-645` 的只读 `NVSDK_NGX_EParameter_*` 用 `"#\x01"` 式魔法串（区别于普通字符串键，应用不该手拼）；`:647-853` 近 200 个 `NVSDK_NGX_Parameter_*` 键宏是键值总线的字典——从 `SuperSampling.ScaleFactor`（`:649`）、`Jitter.Offset.X/Y`（`:762-763`）、`DLSS.Feature.Create.Flags`（`:767`）、subrect 十件套（`:800-812`）到 `InvViewProjectionMatrix`/`ClipToPrevClipMatrix`（`:824-825`）。helpers 族把结构体逐键 Set 的目标就是这些宏。

## 设计决策

1. **单头契约**：所有共享类型集中一文件，代价是 defs.h 膨胀到 859 行；dlssd/dlssg 后续按特性拆出 _defs_ 前缀头（2023/2026），说明 NVIDIA 自己也承认单头策略到极限。
2. **掩码判错 + 0xBAD 基址**：可读的调试观感（BAD00000）与可扩展的位段并存。
3. **PrecisionInfo**（`:342-350`）：低精度资源用 `hi = lo * Scale + Bias` 仿射还原，为未来低精度渲染管线预留。

## 新人提示

读此文件按"版本→Result→Feature→preset→参数键"五段跳读；`:572` 起的魔法串区容易看漏——那是最古老的一批只读参数。排障 `NVSDK_NGX_Result_FAIL_OutOfDate` 时先查 `:148-154` 注释理解语义，再回 nvsdk_ngx.h:318-322 找降级路径。
