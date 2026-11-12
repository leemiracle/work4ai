# 01 · audio2face.h 公共 API 层——DLL 门面与工厂转发模式

> 锚点前缀：仓库根 `audio2face-sdk/`。行号锚全部从源码核实（commit 1ca0f025）。

## 一、角色定位

`include/audio2face/audio2face.h` 是整个 audio2face SDK 的唯一公共入口：427 行头文件（audio2face.h:21-427）以 `namespace nva2f`（audio2face.h:41）收拢全部 C 风格自由函数，配合 `AUDIO2FACE_DLL_API` 宏（dll_export.h:23-30，Windows 下 dllexport/dllimport 二选一、其他平台空展开）实现跨平台 DLL 导出。它只做两件事：**声明工厂**与**声明访问器**——不含任何实现。真正的对象构造在 `source/audio2face/audio2face.cpp`（892 行），而这个 .cpp 本身也不实现逻辑，只把每个公共函数 2-5 行转发给 `_INTERNAL` 后缀的内部函数，并注明 "Implementations are inside audio2face-core.lib"（audio2face.cpp:25）。这是典型的 **DLL 门面 + 工厂转发**三层切分：公共头（ABI 稳定）→ 门面 .cpp（符号导出）→ audio2face-core 静态实现库（符号隐藏）。NOTE：本文件并不编入独立 audio2face DLL，而是与 audio2emotion/audio2x 的同名门面一起被编入聚合共享库 `audio2x`（audio2x-sdk/CMakeLists.txt:2,18），Linux 侧用 `-Bsymbolic + --exclude-libs,ALL` 隐藏 core 符号。

## 二、内部结构

门面 .cpp 的结构是严格的两段式：第 26-311 行是全部 `_INTERNAL` 内部函数的原型声明块（如动画器族 audio2face.cpp:26-36、缓冲区族 :38-59、Read 族 :70-114、Get/Set 族 :116-181、交互执行器族 :193-272、Bundle 族 :275-311），第 313 行以 `//////////////////////////////////////////////` 分隔后是逐个 2-5 行的转发体。实测定义段共 **92 个转发包装**：Create\* 30 个（CreateAnimatorPcaReconstruction audio2face.cpp:315、CreateMultiTrackAnimatorSkin :335、CreateBlendshapeSolver :424 等）+ Read\* 15 个（ReadAnimatorParams :429、ReadRegressionModelInfo :441 及五路径重载 :445-455）+ Get/Set\* 访问器 + AreEqual 比较 + 位算子。对象生命周期统一"一函数一 new、Destroy() 虚方法自删"：`GeometryExecutorBase::Destroy()` 即 `delete this`（executor.cpp:39-41），门面从不保留所有权。头文件侧按资产类型分四簇：缓冲区/绑定工厂（audio2face.h:67-110）、模型装载 Read 族（:114-172）、执行器工厂（:245-265、:362-382）、一键 Bundle 装载（:386-425）。

## 三、外部连接

头文件 include 了全部子契约头（audio2face.h:23-39），其中 `audio2x/inference_engine.h`（:39）把 TensorRT 推理基座接进来——回归/扩散两套 buffer 工厂（CreateInferenceInputBuffersForRegressionModel audio2face.h:67、Diffusion 版 :80-94，多出 IInferenceStateBuffers 状态缓冲 :84）与绑定描述（GetBindingsDescriptionForRegressionModel :100）都依赖 nva2x 命名空间。门面 .cpp 只依赖 `audio2face/audio2face.h` 单个 include（audio2face.cpp:21），与 core 库的唯一耦合就是 `_INTERNAL` 自由函数签名——这正是符号边界干净的原因。Get/Set 访问器族（audio2face.h:175-359）并非直接调成员，而是转发给 executor.cpp 中基于 `dynamic_cast<AccessorType*>` 的内部访问器（executor.cpp:337-354、358-377），实现"C 风格 API 与 private 细节解耦"。

## 四、数据流

典型离线流：用户 `ReadRegressionGeometryExecutorBundle`（audio2face.h:386-393，带 nbTracks/帧率分子分母）→ 门面转发（audio2face.cpp:822-833）→ core 内部 parse_helper 装模型、建执行器、装配 Bundle 返回。交互流：`ReadDiffusionGeometryExecutorBundle`（audio2face.h:395-402）多出 `identityIndex`（多身份模型选人）与 `constantNoise`（固定噪声种子以复现）两参数。混合管线流：`CreateHostBlendshapeSolveExecutor`（audio2face.h:256-259）接收"所有权转移"的 geometry executor（注释明示 Ownership transferred，:254-255），包装成二级 blendshape 执行器——门面层即完成了两级管线的组装协议（audio2face.cpp:638-650）。

## 五、设计决策

①**转发而非直接实现**：把 ABI 面压成纯自由函数 + 抽象接口，core 库符号全隐藏（audio2x-sdk/CMakeLists.txt 的 exclude-libs），更换 core 实现不破坏二进制兼容。②**重载即便利层**：ReadRegressionModelInfo 单文件版（audio2face.h:123）与五文件版（:125-131）最终都落到同一个 `_INTERNAL`（audio2face.cpp:441-455）。③**operator|/operator& 导出**：连 ExecutionOption 位算子都要走 DLL 导出（audio2face.h:268-276；转发经 internal 命名空间中转 audio2face.cpp:652-670），避免跨 DLL 边界的内联不一致。④**图谱甄别**：批阶段甄别"工厂函数多为 3-5 行转发不建函数节点"（NOTES-DIGEST batch-12-part-2），文件级节点承载该架构事实——本篇行号锚为手工复核版。

## 六、新人提示

读 SDK 先读 audio2face.h 的四簇分组再读 sample（samples 用带 Destroyer 删除器的 unique_ptr 管理生命周期）；不要在门面 .cpp 里找逻辑，一律 grep `_INTERNAL` 跳到 audio2face-core。注意 `GetExecutor*` 族失败返回 `eUnsupported` 而非崩溃——传入的 executor 未实现对应 Accessor 接口时 dynamic_cast 落空（executor.cpp:340），这是能力探测不是错误。创建 BlendshapeSolve 执行器后原 geometry 指针已被接管，不可再 Destroy（audio2face.h:255）。
