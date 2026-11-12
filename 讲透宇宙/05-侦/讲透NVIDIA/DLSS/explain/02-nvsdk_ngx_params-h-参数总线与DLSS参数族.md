# 02 nvsdk_ngx_params.h：NVSDK_NGX_Parameter 双面总线与三族创建参数

## 角色定位

`include/nvsdk_ngx_params.h`（117 行）定义全 SDK 的参数总线 `NVSDK_NGX_Parameter`——一个由 NGX 实现、应用填写的键值对接口，以及 DLSS-SR/DLDenoise 的创建参数结构体。DLSS 一切输入（分辨率、颜色缓冲、运动矢量、jitter、质量档……）最终都汇成总线上的一次 `Set(name, value)`；同目录的 params_dlssd.h/params_dlssg.h 是 RR/FG 两族的平行扩展。

## 内部结构

**C++ 纯虚面**（`:52-74`）：`Set` 8 种重载（unsigned long long/float/double/unsigned int/int/ID3D11Resource*/ID3D12Resource*/void*，`:55-62`），`Get` 对称 8 种（`:64-71`）返回 `NVSDK_NGX_Result`，加 `Reset()`（`:73`）。注意它被 `extern "C"` 包裹却是带虚函数的 C++ 抽象类——虚表跨编译器不可移植，所以才有 C 面。

**C ABI 面**（`:79-110`）：`NVSDK_NGX_Parameter_SetULL/SetF/SetD/SetUI/SetI/SetD3d11Resource/SetD3d12Resource/SetVoidPointer` 与对应 Get*，每对伴一个 `PFN_` 函数指针类型。C 引擎（或跨编译器场景）用这组自由函数操作同一对象——helpers 系全部走这组 C 函数而非虚表。

**创建参数结构**：`NVSDK_NGX_Feature_Create_Params`（`:27-35`）四元组 InWidth/InHeight/InTargetWidth/InTargetHeight + 可选 InPerfQualityValue；`NVSDK_NGX_DLSS_Create_Params`（`:37-43`）嵌套之并加 InFeatureCreateFlags（对应 defs.h 的 `DLSS_Feature_Create_Flags`）与 InEnableOutputSubrects；`NVSDK_NGX_DLDenoise_Create_Params`（`:45-50`）是 RR 旧形态的镜像。

**两族扩展**：`include/nvsdk_ngx_params_dlssd.h:19-33` 的 `NVSDK_NGX_DLSSD_Create_Params` 把 RR 三模式（InDenoiseMode/InRoughnessMode/InUseHWDepth，枚举在 defs_dlssd.h:17-33）前置再接分辨率四元组；`include/nvsdk_ngx_params_dlssg.h:31-39` 的 `NVSDK_NGX_DLSSG_Create_Params` 则是输出分辨率 + NativeBackbufferFormat + 内部渲染分辨率 + DynamicResolutionScaling 开关。

## 外部连接

上游依赖仅 defs.h（`:17`）；下游被门面 nvsdk_ngx.h:76 include，参数对象的分配/销毁由门面的 AllocateParameters/GetCapabilityParameters/DestroyParameters 三组 API 管理（nvsdk_ngx.h:380-451）。FG 的 eval 参数独此一家：`include/nvsdk_ngx_params_dlssg.h:41-136` 的 `NVSDK_NGX_DLSSG_Opt_Eval_Params` 是全仓最大参数结构——multiFrameCount/Index（`:45-48`）、五个 4×4 矩阵 cameraViewToClip/clipToCameraView/clipToLensClip/clipToPrevClip/prevClipToClip（`:52-60`，注释强调不得含 TAA jitter）、相机位姿九元组（`:69-75`）、near/far/FOV/aspect（`:78-84`）、九个布尔开关（`:87-99`，HDR/深度反转/正交投影/菜单检测等）与 11 组 subrect（`:109-135`）。

## 数据流

典型 SR 流：`GetCapabilityParameters` 拿预填能力表 → 填 `NVSDK_NGX_DLSS_Create_Params` → `NGX_D3D12_CREATE_DLSS_EXT`（helpers_d3d.h:275-294）把结构体拆成 Width/Height/OutWidth/OutHeight/PerfQualityValue/Flags/Subrects 七个 Set → CreateFeature → 每帧填 `NVSDK_NGX_D3D12_DLSS_Eval_Params`（helpers_d3d.h:225-261）由 `NGX_D3D12_EVALUATE_DLSS_EXT` 展开 ~58 个 Set → EvaluateFeature。结构体只是键值总线的语法糖。

## 设计决策

1. **双语言面并存**：C++ 虚表便利 vs C ABI 可移植，用同一底层对象同时服务两类引擎——代价是两套 API 必须永远同步演化。
2. **键字符串而非序号**：字典序自由扩展（`"DLSS.TransparencyLayerMvecs"` 等），代价是每次 Set 一次字符串查找；只读 EParameter 才用 `"#\xNN"` 魔法串（defs.h:572-645）。
3. **OPTIONAL 注释约定**：结构体内用 `/*** OPTIONAL ***/` 分隔（`:33`/`:40`），零值即默认——与 helpers 的 `0.0f?1.0f` 兜底三目（helpers_d3d.h:161-162）配合成"零值安全"契约。

## 新人提示

写集成代码时优先用 helpers 而非手拼 Set（易漏 subrect 类键）；FG 的矩阵注释（params_dlssg.h:50）常被忽视——矩阵含 jitter 是帧生成错位的头号原因。C 工程链这组 Set*/Get* 函数时注意 `NVSDK_CONV` 调用约定宏（defs.h:42-46，GNU 下为空、MSVC 为 __cdecl）。
