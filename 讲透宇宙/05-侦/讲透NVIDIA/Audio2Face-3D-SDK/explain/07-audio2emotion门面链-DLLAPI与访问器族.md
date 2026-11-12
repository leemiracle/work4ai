# 07 · audio2emotion 门面链——纯声明 DLL 头、16 个工厂/解析函数与 Get/Set 访问器族

## 角色定位

`audio2emotion.h` 是 audio2emotion-sdk 对外的唯一门面头：一个**纯 `AUDIO2EMOTION_DLL_API` 函数声明头**（`audio2emotion.h:22-202`），自身不含任何实现。它把"C++ 类 + 虚函数"的内部世界包装成 **C 风格自由函数 API**——用户只拿接口指针，经 `Create*/Read*` 工厂创建、经 `Destroy()` 虚方法销毁，跨 DLL 边界不泄漏 STL 类型（值类型 `std::error_code` 除外）。tree-sitter 对单行 DLL 声明提取为空，图谱 16 个函数节点全部手工补建（NOTES-DIGEST batch-7-part-1）。

## 内部结构

头文件结构分四段（全在 `namespace nva2e`，audio2emotion.h:35）：

1. **依赖聚合**：include 七个本 SDK 接口头 + 跨库的 `audio2x/inference_engine.h` 与 `audio2x/emotion_accumulator.h`（audio2emotion.h:24-33）——门面头同时是"推荐 include 集"。
2. **16 个工厂/解析函数节点**：`GetBindingsDescriptionForClassifierModel`（audio2emotion.h:39）、`CreateBindingsForClassifierModel`（audio2emotion.h:43）、`CreatePostProcessor`（audio2emotion.h:47）、`CreateClassifierEmotionExecutor`（audio2emotion.h:73）、`CreatePostProcessEmotionExecutor`（audio2emotion.h:80）、`CreateEmotionBinder`（audio2emotion.h:94）、`CreateClassifierEmotionInteractiveExecutor`（audio2emotion.h:131）、`CreatePostProcessEmotionInteractiveExecutor`（audio2emotion.h:139）与 8 个 `Read*`（audio2emotion.h:154-199）。**四个函数各有两个参数重载**（CreatePostProcess* 与 Read*ModelInfo），图谱各建首个签名并在摘要说明——重载不能跨 C 边界导出，但这是 C++ 头，无碍。
3. **Get/Set 访问器族（不建函数节点）**：批量执行器 4 个——`Get/SetExecutorInputStrength`（audio2emotion.h:50,55）、`Get/SetExecutorPostProcessParameters`（audio2emotion.h:60,65）；交互执行器 6 个——`Get/SetInteractiveExecutorInferencesToSkip`（audio2emotion.h:101,106）、`InputStrength`（audio2emotion.h:111,116）、`PostProcessParameters`（audio2emotion.h:121,126）；外加比较工具 `AreEqual`（audio2emotion.h:70）。
4. **一站式 Bundle**：`ReadClassifierEmotionExecutorBundle`（audio2emotion.h:186-192，参数含 nbTracks/bufferLength/帧率分子分母/inferencesToSkip/outModelInfo）与 `ReadPostProcessEmotionExecutorBundle`（audio2emotion.h:195-200）。

配套的 `dll_export.h` 是两段式宏：`_WIN32` 下按 `AUDIO2EMOTION_SDK_DLL_EXPORTS` 区分 dllexport/dllimport（dll_export.h:23-28），非 Windows 恒空宏（dll_export.h:29-31）——构建侧由 CMake 决定导出方。

## 外部连接

门面的转发实现在 `source/audio2emotion/audio2emotion.cpp`：前部集中声明 27 个 `*_INTERNAL` 自由函数（audio2emotion.cpp:26-132，注释言明实现在 audio2emotion-core.lib，audio2emotion.cpp:25），L134 分隔线后每个公有函数一行透传（audio2emotion.cpp:135-137、263-265）。这是**三层门面**：DLL 导出层 → 静态库内部层（`*_INTERNAL`）→ 具体类。NOTES-DIGEST 钉版：3-5 行转发不建函数节点，文件级节点承载该架构事实。

访问器族的真正机制在 `internal/executor.h`：两个能力探测接口 `IEmotionExecutorAccessorInputStrength`（executor.h:35-39）与 `IEmotionExecutorAccessorPostProcessParameters`（executor.h:41-46），`EmotionExecutorBase` 同时继承二者（executor.h:56-58）。core 侧 executor.cpp 用 `dynamic_cast` 把公有 `IEmotionExecutor&` 降型到 Accessor 再调用（executor.cpp:310-335 整段说明注释，338-340 即 `GetExecutorInputStrength_INTERNAL` 实现），失败返回 `eUnsupported`。

## 数据流

以典型调用为例：`ReadClassifierEmotionExecutorBundle(path)` → parse_helper 解析 model.json 得 ModelInfoOwner → 组装 CUDA 流+音频/情感累积器+执行器四件套返回 Bundle。运行期调参：`SetExecutorInputStrength(executor, v)` → audio2emotion.cpp:153-157 透传 → executor.cpp:351 dynamic_cast 到 Accessor → 具体执行器的 `SetInputStrength`。错误全程 `std::error_code`。

## 设计决策

- **dynamic_cast 能力探测而非接口膨胀**：公有 `IEmotionExecutor` 保持精简，可选能力拆成 Accessor 接口，查询失败=不支持（executor.cpp:310-313 注释自我批评了 RTTI 跨编译器边界的风险）。
- **Destroy() 虚方法而非 delete**：对象在 DLL 内 new/delete，规避跨边界分配器不匹配——三库统一范式。
- **重载成对暴露**：PostProcess 执行器提供"classifier 参数版"与"postprocess 参数版"两套重载（audio2emotion.h:80-91），后者无需有效推理模型即可只跑后处理。
- **Set 类访问器先查执行状态**再改值（executor.cpp:359 附近模式），防止运行中途改参数。

## 新人提示

1. 找"某个 API 到底干了什么"别停在 audio2emotion.cpp——全是转发，真身在 core 同名 `_INTERNAL` 函数。
2. 改门面签名要同步三处：audio2emotion.h 声明、audio2emotion.cpp 前向声明+转发体、core 实现——漏一处即链接错误。
3. 图谱 16 个函数节点系手工补建（tree-sitter 盲区），上游加新 API 时图谱增量需人工补。
4. 访问器返回 `eUnsupported` 不一定是 bug——传错执行器类型也会走到这。
