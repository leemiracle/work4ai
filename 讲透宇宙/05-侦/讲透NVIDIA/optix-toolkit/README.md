# 讲透 NVIDIA/optix-toolkit（OTK）

面向 OptiX 7+ 的 C++/CUDA 工具集：DemandLoading 按需加载 + Memory 内存池 + ShaderUtil 设备算法 + OmmBaking 微波图烘焙 + NeuralTextures 神经纹理 + 示例层（Gui/OTKApp/旗舰 DemandPbrtScene）。"库供能力、示例供组装"双层结构。

## 产物状态

| 产物 | 状态 | 位置 | 规模 |
|---|---|---|---|
| deepwiki | ✅（另有专卷） | `deepwiki/` | — |
| 知识图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json` | 1269 节点 / 2256 边 / 14 层 / 16 步 tour |
| fingerprints | ✅ | 仓内 `.understand-anything/fingerprints.json` | 831 文件 @ 16c7c889 |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md` | 8 节，行号锚 45+ |
| explain | ✅ 5 篇 | `explain/01`~`05` | 每篇 2000-3000 字符（不计空格），锚 12+ |
| 本 README | ✅ | 勘误 9 条 | — |

分析时 commit `16c7c889b00c7f9147ad52b188e21478c69e64e6`。

## 核心数字速查

- `ShaderUtil/.../vec_math.h` **5367 行**（全仓最大工具头）；`examples/DemandPbrtScene/include/.../Params.h` 734 行（示例最大头）
- `OmmBaking/.../CuOmmBaking.h` 505 行（OmmBaking 唯一公开 API 头）；`Memory/.../MemoryPool.h` 437 行
- 核心实现：DemandLoaderImpl.cpp 659 / PagingSystem.cpp 473 / OptixRenderer.cpp 458 / GeometryCache.cpp 509 / SparseTexture.cpp 383 / PbrtScene.cpp 373 / FourierBsdfTable.cpp 360 / ProxyInstances.cpp 296 / PbrtApi.cpp 302
- 框架：`OTKApp.h` 162 行（约 45 方法基类）；`CUDAOutputBuffer.h` 350 行（四后端）；`ImageSource.h` 153 行（17 方法根接口）
- 测试：DemandLoading 54 份 gtest / Memory 16 / OmmBaking 27 / ShaderUtil 19 / DemandPbrtScene 90 份图像回归

## 勘误与图谱口径（9 条）

1. **PbrtApi 不是类**：`examples/pbrtApi/PbrtApi.cpp:16` 是 `static ::otk::pbrt::Api* g_api{}` 单例 + :37/:47 起的自由函数族（pbrtObjectBegin/pbrtShape...）转发到 otk::pbrt::Api 实例——"PbrtApi 类"的说法不成立，它是 C 风格 API 门面。
2. **NTC 是适配器非并列库**：README 把 NeuralTextures 与 Memory/ShaderUtil 并列，但实现上 `NeuralTextureSource.h:19` 继承 `imageSource::ImageSourceBase`、readTile（:45）转发 NTC——本质是 ImageSource 家族的适配器 + OptiX 推理数据打包（makeOptixInferenceData :57），仅 15 文件，重活在 NTC SDK。
3. **C++ 手扫边占比极高**：scan 阶段对 .h/.cu 的 include/template 解析盲区大，C++ 手扫补 1633 条边、净增 1488——引用图谱 imports 边时注意大量来自人工补扫而非 tree-sitter。
4. **旗舰示例路径平铺**：DemandPbrtScene 源码直接在 `examples/DemandLoading/DemandPbrtScene/` 平铺（PbrtScene.cpp 等在目录根），**没有** src/ 子目录；头文件才在 include/ 子目录。图谱层摘要里 "src/PbrtScene.cpp" 的路径是简写错误。
5. **pbrtApi 目录是小写驼峰**：`examples/pbrtApi/`（p 小写），与 PbrtSceneLoader（P 大写）并存——大小写敏感文件系统上写错路径直接找不到。
6. **NeuralTextures 物理位置在仓根**：顶级目录 `NeuralTextures/`，不在 DemandLoading/ 之下（README 六库列表顺序易让人误会是 DemandLoading 子件）；DemandLoading 下的扩展是 DemandGeometry/DemandMaterial 两个 README 未列的家族成员。
7. **NullSuballocator 是宏不是类**：`MemoryPool.h:23-24` `#define NullAllocator HostAllocator` / `#define NullSuballocator HeapSuballocator`——"空分配器策略"实为既有分配器的宏别名，图谱里按类检索会落空。
8. **AliasTable 是 POD struct+函数族**：`AliasTable.h:26` struct AliasRecord + :32 struct AliasTable，配套自由函数建表/采样；不是带方法的 C++ 类，与 vec_math.h 同一头文件库风格。
9. **SelfIntersectionAvoidance 是三实现族**：通用 `SelfIntersectionAvoidance.h`（仅 45 行）+ `SelfIntersectionAvoidance/` 子目录 + CudaSelfIntersectionAvoidance.h + OptixSelfIntersectionAvoidance.h——按运行时能力三选一，"自相交规避算法"单数表述不准确。

## explain 索引

- `explain/01-DemandLoader按需加载.md` —— mapOrRequest 缺页模型、PagingSystem 引擎、LRU 半字节驱逐、请求线程池
- `explain/02-ImageSource族.md` —— 17 方法根接口、读取器×装饰器正交组合、ImageSourceCache
- `explain/03-OmmBaking与NeuralTextures.md` —— GetPreBakeInfo/Bake 两段式、SAT 求值、NTC 适配器桥
- `explain/04-DemandPbrtScene数学库.md` —— pbrtApi 单例转发、FourierBsdf 表解析、ray_cone、双缓冲热切换
- `explain/05-ShaderUtil与Gui框架.md` —— vec_math 底座、AliasTable、自相交三实现、CUDAOutputBuffer 四后端、OTKApp/ MockOptix
