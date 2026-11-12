# 04 NVIDIAImageScaling 子模块：空目录的真相与 NIS/DLSS 双轨定位

## 角色定位

`NVIDIAImageScaling/` 在本仓是一个特殊存在：目录存在但为空，图谱未收录任何节点。它不是被裁剪，而是 git 子模块未初始化——`.gitmodules:2-3` 声明 `path = NVIDIAImageScaling`、`url = https://github.com/NVIDIAGameWorks/NVIDIAImageScaling`。本仓对 NIS 的全部"内容"就是三处引用：README 的介绍与拉取命令、gitmodules 的指针、以及 NGX 特性枚举里的 ImageSuperResolution 条目。

## 内部结构（本仓视角）

`README.md:5-6` 是官方定位声明：NIS 提供单一的空间放大+锐化算法（single spatial scaling and sharpening algorithm），跨平台支持，含可集成进 DX11/DX12/Vulkan 的计算着色器。`README.md:8-14` 给两种获取方式：克隆时 `--recurse-submodules`（`:10`），或事后 `git submodule update --init --recursive`（`:14`）。注意 `README.md:12` 有上游拼写瑕疵"clonned"——README 原文如此。

NGX 契约层也有 NIS 的影子：`include/nvsdk_ngx_defs.h:194` 的 `NVSDK_NGX_Feature_ImageSuperResolution = 3`（特性 ID 3，紧跟 SR 的 1）；`:582-585` 四个只读 EParameter（ScaleFactor_2_1/3_1/3_2/4_3——NIS 只支持这四个固定比例，与 DLSS 的连续分辨率自由形成对照）；`:689-692` 对应的普通参数键；`:653`/`:660`/`:676` 的 Available/NeedsUpdatedDriver/MinDriverVersion 三件套按特性正交展开。

## 外部连接

NIS 真身在上游 NVIDIAGameWorks/NVIDIAImageScaling 仓（MIT 许可的计算着色器集合，含 HLSL/GLSL 源码与各引擎集成示例），本仓经子模块指针引用。图纸上 NIS 与 DLSS 是双轨互补：NIS 纯空间算法（单帧、无运动矢量、无时序累积），任何 GPU 可跑；DLSS-SR 时序超分（吃运动矢量/深度/多帧历史），要 RTX 张量核。工程上常见"NIS 兜底 DLSS"的分级策略：RTX 卡走 DLSS，非 RTX 走 NIS——两者共享同一套分辨率档位 UI 语义。

## 数据流（如走 NGX 通道）

若应用经 NGX 体系用 NIS：CreateFeature 传 `NVSDK_NGX_Feature_ImageSuperResolution`（ID 3），能力查询读 ScaleFactor_* 只读键（defs.h:582-585）确认四档比例支持；但 NIS 主推路径是直接嵌计算着色器（子模块里的 NVScaler/NVSharpen），不经 NGX——所以本仓 include/ 里没有任何 ImageSuperResolution 的 helpers 函数（对比 SR/RR/FG 三族均有专属打包器），这是"NIS 不依赖 NGX 运行时"的旁证。

## 设计决策

1. **子模块而非 vendor 目录**：NIS 独立仓独立发版（MIT），DLSS SDK（专有许可）不吞并其源码——许可与节奏双重解耦。
2. **特性 ID 占位**：NGX 枚举为 ImageSuperResolution 留位说明早期 NGX 架构想统一托管所有 RTX 特性，后演化成"NIS 直嵌着色器、DLSS 走 NGX"的现实分野。
3. **四固定比例**：2.1/3.1/3.2/4.3 与 DLSS 的 Quality/Balanced/Performance 档位比例（约 1.5/1.7/2.0）刻意错开，避免两算法在同一档位打架。

## 新人提示

克隆本仓后见 NVIDIAImageScaling/ 空目录不是损坏；要读 NIS 源码先跑 `git submodule update --init --recursive`。图谱/理解流水线层面：该目录无文件不产生节点，涉及 NIS 的分析须到上游仓进行（本 work4ai 组未收录 NIS 独立图谱，讲透NVIDIA/DLSS 仅覆盖引用关系）。鉴别许可时注意——子模块内容是 MIT，DLSS SDK 本体是 LICENSE.txt:1 的 RTX SDKs 专有许可，两者不可混同再分发。
