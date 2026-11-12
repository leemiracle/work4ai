# 03 nvsdk_ngx_helpers 族：static inline 参数打包器与 deprecated 转发桩甄别

## 角色定位

helpers 十件（图谱 L06-L08 层）是门面 API 之上的"语法糖层"：不引入新符号、不进链接库，纯 `static inline` 把"填几十个参数键"压成一次结构体调用。分三组——基座四件（helpers.h 聚合 + d3d/cuda/vk 各一）、DLSS-RR 子族四件（dlssd 前缀）、DLSS-FG 子族三件（dlssg 前缀）；其中 `include/nvsdk_ngx_helpers_dlssd.h` 与 `include/nvsdk_ngx_helpers_dlssg.h` 是两个 17 行的 deprecated 转发桩。

## 内部结构

**聚合头** `include/nvsdk_ngx_helpers.h`：`:20-63` 的 `NGX_DLSS_GET_STATS/1/2` 三层嵌套（2 取全量，1/0 用 dummy 降参），内部经 `DLSSGetStatsCallback` 回调（`:26`）取回 VRAM 字节/OptLevel/IsDevSnippetBranch；回调为空时返回 FAIL_OutOfDate（`:27-33`），注释列两大原因——驱动太老、或误用 AllocateParameters（应换 GetCapabilityParameters，能力键才预填回调）。`:65-114` 的 `NGX_DLSS_GET_OPTIMAL_SETTINGS` 是分辨率档位问答机：设入用户分辨率+质量档（`:89-91`，`:92` 还给老 DLL 补 RTXValue=false），回调后取 Out/动态 Max/Min 四组（`:101-111`），`:104-107` 老驱动无动态键时 min/max 回退最优值。`:116-117` 拉入 d3d/cuda 两支（Vulkan 需单独 include helpers_vk.h——聚合头不带它，因 vk 头需 Vulkan 原生类型）。

**D3D 主力** `include/nvsdk_ngx_helpers_d3d.h`：D3D11 侧 `NVSDK_NGX_D3D11_DLSS_Eval_Params`（`:34-70`，颜色/深度/MV/jitter 必填 + subrect 六组 + GBuffer 十七槽 + 光追五输入）；`NGX_D3D11_EVALUATE_DLSS_EXT`（`:103-167`）逐键展开 58 个 Set 后调 `EvaluateFeature_C`。D3D12 侧镜像（`:225-261`/`:297-361`），Create 版多设 CreationNodeMask/VisibilityNodeMask（`:283-284`，多 GPU 节点路由）。DLISP（图像信号处理）create/eval 成对（`:169-208`/`:363-406`），eval 前显式校验 sharpness/denoise ∈[0,1]（`:189-192`），atlas 场景用 Rect 四键只放大子区（`:199-205`）。

**CUDA/VK 支**：`include/nvsdk_ngx_helpers_cuda.h:20-26` 用 `CUtexObject*` 代 D3D 资源；`include/nvsdk_ngx_helpers_vk.h:19` 的 `NVSDK_NGX_ENSURE_VK_IMAGEVIEW` 宏在 eval 前校验资源类型（传了 VkBuffer 立即 FAIL_InvalidParameter），`:21-43` 的 Create_ImageView/Buffer_Resource_VK 帮忙填 defs_vk.h 的 Resource_VK 结构。

**deprecated 桩甄别**：`include/nvsdk_ngx_helpers_dlssd.h:15` 与 `include/nvsdk_ngx_helpers_dlssg.h:15` 均 `#pragma message("... is deprecated; #include \"..._d3d.h\" instead")`，`:17` 直接 include 新名。两者版权年 2026、仅 17 行——是 API 从"每特性单头"重构为"特性×图形 API 矩阵"时的兼容壳。编译见此告警即换 include，行为无差（纯转发）。

## 外部连接

全部依赖 params.h 的 C ABI Set*/Get*（不碰 C++ 虚表）；RR 子族（`include/nvsdk_ngx_helpers_dlssd_d3d.h:117`/`:418` 双 API 结构、`:227`/`:529` create、`:247`/`:552` evaluate；cuda 版 `include/nvsdk_ngx_helpers_dlssd_cuda.h:130`/`:150` create、`:247` evaluate；vk 版 `include/nvsdk_ngx_helpers_dlssd_vk.h:131`/`:157`）与 FG 子族（`include/nvsdk_ngx_helpers_dlssg_d3d.h:46-63` create、`:66` evaluate、`:197` ESTIMATE_VRAM；vk 版 `include/nvsdk_ngx_helpers_dlssg_vk.h:45`/`:62`/`:195`）同构。FG 子族无 _cuda 文件——后端矩阵从文件布局即可读出。

## 数据流

一次 D3D12 SR 帧调用：游戏填 `NVSDK_NGX_D3D12_DLSS_Eval_Params`（大多字段零值即默认）→ `NGX_D3D12_EVALUATE_DLSS_EXT` 展开 Set（`include/nvsdk_ngx_helpers_d3d.h:303-358`，注意 `:311-312`/`:355-356` 的 `==0.0f?1.0f` 兜底）→ `NVSDK_NGX_D3D12_EvaluateFeature_C`。打包器存在的意义就是把"58 个键序"这种易错知识固化进头文件。

## 设计决策

1. **inline 而非库函数**：零链接负担、每调用点可内联优化；代价是编译期膨胀（include helpers_d3d.h 的 TU 变大）。
2. **`_EXT` 后缀**：标记"接收结构体参数的扩展版"，与裸 CreateFeature/EvaluateFeature API 区分。
3. **静默默认值**：MV scale/PreExposure/ExposureScale 传 0 自动当 1.0（`:117-118`/`:161-162`）——便利但也是排障盲点（以为传 0 生效，实际被改写）。

## 新人提示

include 顺序：D3D/CUDA 只需 `#include "nvsdk_ngx_helpers.h"`；Vulkan 要显式 `nvsdk_ngx_helpers_vk.h`。见 dlssd/dlssg 无后缀头告警别慌，换 `_d3d` 后缀名即可。统计接口（GET_STATS）必须用 GetCapabilityParameters 返回的参数对象——AllocateParameters 的空表里没有回调键。
