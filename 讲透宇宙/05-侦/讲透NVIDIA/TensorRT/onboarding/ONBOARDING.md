# TensorRT 开源仓 ONBOARDING

> 图谱基线：3344 节点 / 6537 边 / 16 层 / 16 步导览 / validator 0 issues / fingerprints 1452 文件 @ `98adec82`（TensorRT 11.3.0.99，"TensorRT 11.3 OSS Release (#4858)"，VERSION 文件=11.3.0.99）
> 本文行号锚全部从该 commit 源码逐一核实；口径：文件路径:行号。生成于 2026-11-06。

---

## 1. 项目定位：推理引擎的"生态壳"，不是引擎本体

第一件必须钉死的事：**这个仓不包含 TensorRT 推理引擎的核心实现**。`libnvinfer`（builder/optimizer/runtime 执行器）是 NVIDIA 闭源二进制，经官网 tar 包发布；开源仓给的是围绕这个闭源核心的**全部生态接口**——API 契约头、官方插件库、Python 绑定、四个配套工具。README.md:106-109 的下载链接（TensorRT-Enterprise-11.3.0.99-Linux-x86_64 tar 包）与 README.md:116 的 `export TRT_LIBPATH=.../lib` 说明：编译本仓产物（插件、绑定）需要先装好闭源库。

因此仓库的正确心智模型是**五域一壳**：

| 域 | 内容 | 图谱层 |
|---|---|---|
| `include/` | NvInfer 全套 C++ API 契约头（合计 20634 行，最大单头 NvInfer.h 11892 行） | L02 |
| `parsers/` | ONNX parser 公共件 + `parsers/onnx` 子模块（onnx-tensorrt 独立仓） | L03 |
| `plugin/` | 32 个官方插件目标 + 公共基座 + 181 个 cubin 二进制资产 | L04-L08 |
| `python/` | pybind11 绑定源码 + 四轨 wheel 打包 | L09-L10 |
| `tools/` | Polygraphy / onnx-graphsurgeon / pytorch-quantization / tensorflow-quantization / polygraphy-extension-trtexec | L11-L15 |

根 CMakeLists.txt:261/265/308 只 `add_subdirectory(plugin / parsers / python)` 三域（tools 是独立 pip 包各自构建，samples:362 按开关拉起），cmake 门槛 3.31（CMakeLists.txt:18）。

**11.x 是断代版本**。README.md:8-12 列了五条移除清单，每条都直接改变本仓代码面貌：①弱类型网络移除→强类型网络（Strongly Typed Networks）；②隐式量化移除→显式量化（Q/DQ 路线，这就是 tools/ 两个量化工具的地位来源）；③**IPluginV2 全系移除→IPluginV3**（本仓所有插件目录里成对出现的 `*PluginLegacy.cpp` 双轨文件正是这次断代的遗迹）；④TREX 工具移除→Nsight Deep Learning Designer；⑤Python 3.9- 绑定移除，RHEL/Rocky 8/9 RPM 改依 Python 3.12。CHANGELOG.md 以 59 个版本小节倒序记录 11.3 GA（2026-09-22，`CHANGELOG.md:3`）回溯到 7.2.1（2020-10）的全部演进，11.3 里 `Removed demoDiffusion`（CHANGELOG.md:7-8 附近）——demo 目录如今只剩 DeBERTa 与 EfficientDet 两个演示。

治理面：CONTRIBUTING.md 要求所有增强/修复先建 Issue 经 NVIDIA 工程师审批才进评审；CODING-GUIDELINES.md 27 节 C++ 规范；`.clang-format` 定 4 空格+Allman 变体大括号。子模块三件（.gitmodules）：`third_party/protobuf`（branch 3.20.x）、`third_party/cub`（NVlabs 1.8.0）、`parsers/onnx`（指向 github.com/onnx/onnx-tensorrt.git branch release/10.7-GA）——第三件直接证明 **onnx parser 主体在独立仓**，本仓 parsers/ 只留构建接线与共享头。

一句话定位：**闭源引擎的开放边界层**——想懂"TensorRT 怎么被编程、怎么被扩展、怎么被调试量化"，全部素材在这个仓；想看引擎 internals，这里没有。

## 2. 架构总览：16 层 = 五域拓扑 × 资产性质三分

图谱 16 层的第一刀切在**目录域**上，第二刀切在**资产性质**上。资产性质三分是理解本仓的特殊钥匙：

1. **真源码**（可读可改）：插件逻辑 .cpp/.cu、Polygraphy/gs/量化工具的 Python——共约 1200 文件层节点；
2. **二进制资产源码化**（不可读、只可当数据）：L06 的 181 个 cubin .cpp，单个文件 10 万字节级、内容全为 `0x7f, 0x45, 0x4c, 0x46, ...` 十六进制字面量（ELF magic 开头，见第 5 节）；
3. **纯契约**（声明密集、实现为零）：include/ 的 11 个核心头，tree-sitter 类工具对纯声明头零提取，API 谱系节点全靠批甄别手工建立。

16 层速览（节点数=层内文件级节点，1452 层内节点与 fingerprints 基线严格一致）：

| 层 | 名 | 节点 | 域 |
|---|---|---|---|
| L01 | 仓根与工程治理 | 10 | README/CHANGELOG/CMake |
| L02 | NvInfer 核心 API 头谱系 | 14 | include |
| L03 | ONNX Parser 公共域 | 5 | parsers |
| L04 | 插件公共基座与注册 | 70 | plugin/common+api |
| L05 | BERT FMHA 插件逻辑层 | 20 | plugin/bertQKVToContextPlugin 逻辑半边 |
| L06 | FMHA 预编译 SASS cubin 资产坐标系 | 181 | 同插件二进制半边 |
| L07 | 归一化/注意力/张量变换插件群 | 108 | plugin 混合 |
| L08 | 检测/分割/点云插件群 | 102 | plugin 检测系 |
| L09 | Python pybind11 绑定源码 | 19 | python/src |
| L10 | wheel 打包与 tensorrt.plugin 包 | 36 | python/packaging |
| L11 | Polygraphy 核心运行时库 | 219 | tools/Polygraphy/polygraphy |
| L12 | Polygraphy 示例与测试资产 | 232 | examples 117+tests 115 |
| L13 | Polygraphy 文档域与 trtexec 扩展 | 106 | docs 72 rst+ci+扩展 18 |
| L14 | onnx-graphsurgeon 图手术库 | 82 | tools/onnx-graphsurgeon |
| L15 | 量化工具双域 | 167 | pytorch-quantization 85+tensorflow-quantization 82 |
| L16 | 构建部署基础设施与演示/Agent 技能 | 81 | cmake/docker/shared/demo/.agents |

三点结构性观察：

- **Polygraphy 是体量之王**：三分 539 个文件层节点（L11 219 + L12 232 + L13 106 减去 trtexec 扩展 18），占全仓文件层的 37%。图谱 3344 节点中 function 1069 / file 1025 / class 815 / document 301 / config 119，Polygraphy 的 function/class 节点贡献了最大份额——工具域是"活代码"，引擎域反而是"死契约+死数据"，这个反直觉分布是本仓最重要的架构事实。
- **L05/L06 的 20↔181 切分**是全图谱最戏剧性的单目录：一个插件的逻辑半边 20 个文件，二进制半边 181 个文件。插件目录普遍是"8-10 文件 + README + PluginConfig.yaml"的模板化结构（如 scatterElementsPlugin、topkLastDimPlugin），bertQKV 是唯一膨胀出资产坐标系的特例。
- **层内 1452 = fingerprints 基线**：所有层节点可增量校验；本 ONBOARDING 锚定的行号全部落在这些文件内。

五域数据流一句话：ONNX 模型 →（gs 图手术 / 量化工具插 Q/DQ）→ parser 契约（NvOnnxParser.h）→ 闭源 builder 消费 include/ 契约构建 engine → 运行期 ICudaEngine/IExecutionContext 执行，自定义算子经 plugin 域注册（IPluginV3）→ 全链可用 Polygraphy 跨后端比对验证、trtexec 扩展做性能回归。这条流在第 7、8 节展开。

怎么用这张 16 层图导航：想要"读懂某个 API"从 L02 的 14 个头节点入手；想改或新增插件沿 L04 基座 → L07/L08 同族样板 → 回 L02 核对契约；做部署集成从 L09-L10 的绑定与打包入手；做精度/性能问题排查直奔 L11-L13 的 Polygraphy 三分。图谱 16 步导览（t01 全景→t16 收官）与本文八节大体同构，可交替使用。

## 3. NvInfer API 谱系：IRuntime→ICudaEngine→IExecutionContext 与三代插件 ABI 同仓并存

include/ 是闭源引擎的全部公开契约。读它的正确顺序：

**入口聚合**：`include/NvInfer.h:21-22` 以 IWYU export 方式聚合 `NvInferLegacyDims.h` 与 `NvInferRuntime.h`，本体 11892 行内直接定义 builder 族——`INetworkDefinition`（NvInfer.h:8162）、`IBuilderConfig`（NvInfer.h:10579）、`IBuilder`（NvInfer.h:11513）。

**运行时主链**（NvInferRuntime.h，5479 行，全仓最大公共头）：
- `IRuntime`（NvInferRuntime.h:1900）——引擎反序列化的工厂；
- `ICudaEngine`（NvInferRuntime.h:3087）——编译产物；
- `IExecutionContext`（NvInferRuntime.h:4032）——执行上下文，现代执行入口 `bool enqueueV3(cudaStream_t stream)`（NvInferRuntime.h:4721）。
- 旁支 `IRuntimeConfig`（NvInferRuntime.h:3024）。

**版本协商机制**是这套头最独特的工程：`IVersionedInterface`（NvInferRuntimeBase.h:283）是版本协商根接口；全部演进接口按 `v_x_y` 命名空间叠层（NvInferRuntime.h 内 `namespace v_` 出现 26 处，首个 v_1_0 块在 NvInferRuntime.h:613），再以 using 声明提升到 `nvinfer1`——NvInferRuntime.h:1281 的注释直言 "DO NOT REFER TO namespace v_1_0 IN CODE. ALWAYS USE nvinfer1 INSTEAD"。同一文件里 V3 插件也走这套：`v_1_0::IPluginV3OneBuild` 与 v2 世代（NvInferRuntime.h:1192 `class IPluginV3OneBuild : public v_1_0::IPluginV3OneBuild`，注释块 1238-1273）。编译期版本判定用 NvInferVersion.h:30-31 的 `NV_TENSORRT_MAJOR/MINOR`（本代映射到 TRT_MAJOR_ENTERPRISE 宏）。实现侧镜像在 NvInferImpl.h（1402 行，V 前缀实现类 + 前 200 行密集前向声明）。

**插件三代 ABI 同仓并存**是第 4 节的引子，契约面就在这几个头：
- V2 末代：`class TRT_DEPRECATED IPluginV2DynamicExt : public nvinfer1::IPluginV2Ext`（NvInferRuntime.h:417）——已打弃用标记，11.x 正式移除 API 但本仓 Legacy 源文件仍保留给旧引擎加载；
- V2 全家桶收拢在 NvInferRuntimePlugin.h（925 行，PluginTensorDesc/DynamicPluginTensorDesc 张量描述体系）与 NvInferRuntimeCommon.h（253 行聚合头）；
- V3 基座：`IPluginCapability`（NvInferPluginBase.h:140）、`IPluginV3`（NvInferPluginBase.h:205）及能力分面接口 `getCapabilityInterface(PluginCapabilityType)`（NvInferPluginBase.h:227）；三个能力面 `IPluginV3OneCore`（NvInferRuntime.h:830）、`IPluginV3OneBuild`（NvInferRuntime.h:873）、`IPluginV3OneRuntime`（NvInferRuntime.h:1095）——"单类多继承、按需 static_cast 分面"是 V3 的核心设计；
- 用户侧总入口只有一个：NvInferPlugin.h 全文 42 行，`extern "C"` 声明 `initLibNvInferPlugins`（实现在 plugin/api/inferPlugin.cpp:172），并聚合 NvInfer.h 与 NvOnnxParser 相关头。

**parser 契约**：NvOnnxParser.h:127 `IParserError`（错误码+文件内定位）、:189 `IParser`、:220 `virtual bool parseFromFile(char const* onnxModelFile, int verbosity)`——注意 :197 的注释引导用 parseFromFile 拿更好的诊断。parsers/CMakeLists.txt:19-23 有一处强工程手段：把 vendored protobuf/abseil 全局改命名空间（`-Dgoogle=google_trtrepack -Dabsl=absl_trtrepack`）后合并进 `libnvonnxparser_static.a`——静态库合并发布的 ABI 隔离术，代价是任何符号冲突排查都要先想起这层重命名。

给 Python AOT 插件留的契约在 include/impl/NvInferPythonPlugin.h（603 行）：`ISymExprs`（:85）持 `ISymExprsImpl*`（:116）的 pimpl 双层，`IPluginV3QuickCore/QuickBuild` 快速插件接口（:276/:291）——这是第 6 节 tensorrt.plugin 包的 C++ 对端。

## 4. 插件体系：静态注册表、dlopen 四件套与"注册名≠类名"

### 4.1 注册与构建

注册中心是 plugin/api/inferPlugin.cpp（212 行）：`PluginCreatorRegistry` 单例（:79，getInstance :82）+ `initLibNvInferPlugins`（:172）内联 36 次 `initializePlugin<...Creator>`（:174-211，含 GridAnchor/GridAnchorRect、InstanceNormalization/V2、EfficientNMS 三变体等多 Creator 插件）。构建侧 plugin/CMakeLists.txt:34 `TRT_PLUGIN_NAMES` 列 28 个基础插件目录，`if(TRT_BUILD_INCLUDE_BERT_QKV_PLUGIN)` 再追加 bertQKVToContextPlugin/embLayerNormPlugin/fcPlugin/skipLayerNormPlugin 四件（:66-70，共 32 目标），:78 foreach 逐个 add_subdirectory。插件目录全仓 36 个（32 目标 + api/vc/common 支撑目录）。

公共基座三件套（几乎所有 legacy 插件的地基）：
- plugin/common/plugin.h:53 `BasePlugin : public IPluginV2`、:69 `BaseCreator : public IPluginCreator`（命名空间簿记等通用面）；
- plugin/common/serialize.hpp:30/33 `serialize_value/deserialize_value` 递归模板——全部插件 serialize/deserialize 的统一平坦缓冲协议；
- 检查宏三层：plugin/vc/checkMacrosPlugin.h:317 `PLUGIN_ASSERT`（硬断言）、:270 `PLUGIN_VALIDATE`（软校验带消息）、:203 `caughtError`（异常→状态码，V3 的 noexcept 方法禁止异常逃逸，靠它兜底）。

### 4.2 dlopen 四件套：不链 CUDA 库的插件构建术

plugin/common/ 下五个 Wrapper（cublas/cublasLt/cudnn/cufft/cudaDriver）是同一个模式的四次实例化：**运行时 dlopen 原厂库、以本地类型拷贝复刻不透明 ABI、彻底回避编译期链接 CUDA 数学库**。双平台宏消除 OS 差异——cublasWrapper.cpp:28 `#define dllOpen(name) (void*) LoadLibraryA(name)`（Windows）与 :35 `dlopen(name, RTLD_LAZY)`（POSIX），:97 首次加载 cublas。ABI 复刻两种手法：cublasLtWrapper.h:39-56 用 `uint64_t data[8]`/`data[32]` 数组复刻 Algo/Preference 等不透明结构；cublasWrapper.h:144 用 `using cublasHandle_t = struct cublasContext*;` 前向声明指针（不 include cublas.h 而保持 ABI 兼容）。最现代的一件是 cufftWrapper.cpp:44 `cufftLibCandidates()`——cuFFT 的 SONAME major 与 CUDA toolkit major 相互独立（libcufft.so.12 配 CUDA 13.x），所以必须按候选序列探测（:46 先取 `getCudaLibVersionMaj()`（cudaDriverWrapper.h:142）再走硬编码回退链，:91 逐名尝试）。这与麒麟 KCCL 仓的 dlopen 门面是同一设计空间（对照参考）。

### 4.3 bertQKV：仓库最大单插件，20 逻辑文件 ↔ 181 cubin

`plugin/bertQKVToContextPlugin/` 的逻辑半边只有 20 文件，但承载了三层结构：

1. **注册名≠类名（本仓最高频的认知陷阱）**：qkvToContextPlugin.cpp:45-47 定义三个字符串常量——`kQKV_TO_CONTEXT_PLUGIN_VERSION{"4"}`、`kQKV_TO_CONTEXT_VAR_SEQLEN_PLUGIN_VERSION{"5"}`、`kQKV_TO_CONTEXT_PLUGIN_NAME{"CustomQKVToContextPluginDynamic"}`。用户在 ONNX 图里写的是这个**注册名字符串**，而 C++ 类是 `QKVToContextPluginDynamic`（v4 定长）与 `QKVToContextVarSeqlenPlugin`（v5 变长，qkvToContextPlugin.cpp:760 分节注释起，构造器 :764/:794）。Creator 注册用 `REGISTER_TENSORRT_PLUGIN(QKVToContextVarSeqlenPluginCreator)`（qkvToContextPlugin.cpp:55）。PluginConfig.yaml 里的 `name: CustomQKVToContextPluginDynamic`（yaml:18）、`interface: "IPluginV3"`（yaml:19）、versions `"4"`（yaml:21）与 `"5"`（yaml:151，带 input_mask 双输入与 var_seqlen 属性 yaml:168/176）与之对应。
2. **host 侧调度器**：mhaRunner.h:42 抽象基类 `MHARunner`（isValid :98），:148 `FusedMHARunnerFP16`（v1 路线）、:205 `FusedMHARunnerFP16v2`；qkvToContextPlugin.cpp:852 `createMHARunner()` 按 hiddenSize/S/SM 选执行器，:869 优先 v2（`FusedMHARunnerFP16v2`）。mhaRunner.cu 的运行期分派里 kSM_90 有特殊通道：v1 在 :954（S∈{128,256,384}），v2 在 :1122（S∈{128,192,256,384,512}）；架构合法性断言在 :928/:1099（kSM_75..kSM_120 全列）。变长 padding 由 zeroPadding2d.cu:36/:64 的 `zeroPadding2dKernel` 双模板（标量版+int4 向量化版）处理。
3. **互引约定**：maskIdx 掩码格式与 embLayerNormPlugin 互引——embLayerNormPlugin.h:38 `computeMaskIdx()`，embLayerNormPlugin.cpp:325-326 把它作为 outputs[1] 产给下游 bertQKV 消费；共享工具在 plugin/common/bertCommon.h:102 `getMHAMaskPackedSize`（按 SM/S/dtype 算 packed mask 尺寸）、:163 `doesHwSupportBertMHAPlugin` 硬件探测。embLayerNorm 自己的注册名常量在 embLayerNormPlugin.cpp:37（`CustomEmbLayerNormPluginDynamic`）。

另两个值得钉的实证：PluginConfig.yaml:72 `golden_io_path: "plugin/CustomQKVToContextPluginDynamic_PluginGoldenIO.json"` 是**悬空引用**——全仓不存在该文件（golden IO 数据不在开源域）；README 标注本插件自 TensorRT 10.15 起废弃（BERT 系推理已转向 TensorRT-LLM 路线）。

### 4.3bis 三代插件 ABI 对照速查

| 维度 | V2（IPluginV2/Ext） | V2 动态（IPluginV2DynamicExt） | V3（IPluginV3 + 能力面） |
|---|---|---|---|
| 契约位置 | NvInferRuntimePlugin.h | NvInferRuntime.h:417（TRT_DEPRECATED） | NvInferPluginBase.h:205 + NvInferRuntime.h:830/873/1095 |
| shape 语义 | 构建期定长 getOutputDimensions | 运行期 supportsFormatCombination + configure | PluginCapabilityType 分面：OneCore/OneBuild/OneRuntime |
| 面向能力 | 单接口全包 | 单接口全包+动态 shape | 单类多继承、getCapabilityInterface 按需 static_cast 分面 |
| 异常约束 | 允许有限逃逸 | 允许有限逃逸 | noexcept 全覆盖，caughtError 统一转状态码 |
| 本仓遗迹 | `*PluginLegacy.cpp` 成对文件 | bertQKV/qkvToContextPluginLegacy.cpp 等 | 全部主 `*.cpp` 现行实现 |
| Python 侧 | pyPlugin.cpp:85 pyObjVec 记账 V2 对象 | 同左 | _plugin_class.py:227/:319 JIT/AOT 模板类 |

读任何一个插件目录的固定套路：先看有没有 `*Legacy.cpp`（有=V2/V3 双轨并存），再看主文件的 Creator 注册名常量与 REGISTER_TENSORRT_PLUGIN 行，最后按上表定位它的能力面实现段。

### 4.4 家族二分：NLP/注意力系 vs 检测/点云系

- **NLP/注意力线**（L07）：embLayerNorm/skipLayerNorm（BERT 前处理）、disentangledAttention（DeBERTa 相对位置注意力）、multiscaleDeformableAttn（DETR）。V3 范式样板是 multiscaleDeformableAttnPlugin.cpp:37-50：`getCapabilityInterface` 按 PluginCapabilityType `static_cast` 到 `IPluginV3OneBuild/OneRuntime/OneCore` 分面返回，:28-29 同名静态常量 `DMHA_VERSION{"2"}`/`DMHA_NAME{"MultiscaleDeformableAttnPlugin_TRT"}` 与 Legacy 文件构成"1"/"2"双版本注册。
- **检测/点云线**（L08）：efficientNMSPlugin 序列化为单块裸 POD——efficientNMSPlugin.cpp:42-45 deserialize 直接整体读，:104 serialize 直写，无版本前缀，靠 PLUGIN_ASSERT 对账长度（:514 Creator.deserializePlugin）；generateDetectionPlugin 自 TRT 10.12 起 DEPRECATED 且官方明言无替代计划（generateDetectionPlugin/README.md:3）；RoI 栅格系（roiAlign/proposalLayer/multilevelProposeROI/pyramidROIAlign）与 BEV 线（pillarScatter/voxelGenerator/decodeBbox3D）服务两阶段检测与自动驾驶点云。
- **共享 kernel 库**：plugin/common/kernels/ 26 个 .cu（gridAnchorLayer.cu、topkLastDim.cu、maskRCNNKernels.cu 3101 行 24 kernel 等）——注意 topkLastDimPlugin 与 gridAnchorPlugin 的 kernel 实际在 common/kernels（插件源码注释里的本目录路径是误导，经 CMake 公共库链接解析、不是死引用）。

## 5. FMHA cubin 资产坐标系：文件名即四维坐标，跨架构靠枚举不靠 JIT

L06 的 181 个文件是"闭源 kernel 以源码化二进制随开源仓分发"的教科书案例。**实测口径（盘上逐一统计）**：v1 目录 `fused_multihead_attention/` 55 个 .cpp，v2 目录 `fused_multihead_attention_v2/` 126 个 .cpp，合计 181；每个文件除 SPDX 头注释外只有一条 `unsigned char xxx[] = {0x7f, 0x45, 0x4c, 0x46, ...}`——首四字节正是 ELF magic（cubin 本就是 ELF 目标文件），单文件 106-122KB（如 fused_multihead_attention_fp16_64_64_kernel.sm75.cpp=106564 字节）。任务书口径"109 blob"与盘上不符，特此勘误：**真实口径是 181 个资产文件 / 头文件共声明 171 个 blob 符号（v1 45 + v2 126）**。

**坐标系（文件名即坐标）**：`fused_multihead_attention[_v2]_{dtype}_{S}_{D}_kernel.sm{arch}.cpp`
- dtype ∈ {fp16, int8, il_int8}（il=interleaved，v2 独有 27 个，如 fused_multihead_attention_v2_il_int8_128_64_kernel.sm90.cpp）；
- S ∈ {64, 96, 128, 192, 256, 384, 512}；
- D ∈ {64, 少量 32}（如 v2 的 fp16_128_32_kernel.sm80.cpp）；
- sm_arch ∈ {sm72(仅 v2 头宏), sm75(Turing), sm80/86/87(Ampere/Orin), sm89, sm90(Hopper), sm100/120(Blackwell/DRIVE Thor)}。

**一处必钉的语义勘误**：文件名第二个数字不是 warps、也不是"head 数"，而是 **head size（mD）**。元信息结构体 `FusedMultiHeadAttentionKernelMetaInfoV2`（fused_multihead_attention_v2.h:410-421）字段依次为 `mDataType/mS/mD/mSM/mCubin/mCubinSize/mFuncName/mSharedMemBytes/mThreadsPerCTA/mUnrollStep/mInterleaved`；首条元数据 `{DATA_TYPE_FP16, 64, 64, kSM_75, ..., 24576, 128, 0, false}`（v2.h:424-429）明示 S=64、D=64、每 CTA 128 线程（=4 warps，在线程字段而非文件名里）。v1 结构体同构（fused_multihead_attention.h:478-489）。

**两代符号命名并存**（hex 数组符号名与文件名不是一回事）：
- v1 目录：13 个旧代 fatbin 符号 `fused_multihead_attention_fp16_*_kernel_sm75_cu_o[]`（如 fused_multihead_attention.h:346-351，sm75/80/86 代）+ 42 个 `cubin_fmha_v1_*` 风格 cubin 符号（头内 extern 共 45 条：32 条 `cubin_fmha_v1_*` + 13 条 `_cu_o`）；
- v2 目录：31 个新命名 `fused_multihead_attention_v2_*_kernel_sm*_cubin[]`（v2.h:111-117）与 95 个旧命名 `cubin_fmha_v2_*`（v2.h:395-398），126 条 extern 与 126 文件一一对应。
同代文件内甚至混用：v2.h:118 一行之隔就是 `cubin_fmha_v2_int8_512_64_sm75_cu_cubin[]` 与新式命名并存。选载靠静态注册表：v1 `sMhaKernelMetaInfos[]`（fused_multihead_attention.h:495，查找函数 :646）、v2 `sMhaKernelMetaInfosV2[]`（v2.h:423，查找 :1247）。

**构建期筛架构、运行期驱动选载**：两代 CMakeLists.txt 同构——fused_multihead_attention/CMakeLists.txt:29-30 与 fused_multihead_attention_v2/CMakeLists.txt:29-30 均 `foreach(SM IN LISTS BERT_QKV_SUPPORTED_SMS)` + `should_compile_kernel` 决定哪些 sm 资产进构建；头文件侧有 `#error` 保护（v2.h:400-405：未定义 ENABLE_SM72/75/80/86/87/89/90/100/120 之一即拒绝编译）。sm100/sm120 的存在与 CHANGELOG 的 gb10.0/gb20x 预编译 cubin 记录互证——Blackwell 覆盖靠坐标枚举而非 JIT。**生成脚本不在仓库内**（generate.py 等产出 hex 数组的工具链属 NVIDIA 内部），所以这些文件只能整块替换、无法在仓内再生成。

**独家死资产发现**：v1 目录 55 个数组里有 10 个 sm100/sm120 blob（fp16_256_64_sm100/120 与 int8_64/96/192/256_64_sm100/120，如 `cubin_fmha_v1_int8_192_64_sm100_cu_cubin`）在**全仓零 extern 声明、零引用**（定义文件外的任何头/源均不出现）——Blackwell 预留位或清理遗漏，读码时可直接跳过。另注意 v1 的 55 文件 vs 头 45 声明的差值正是这 10 个。

## 6. Python 绑定与打包：宏模板实例化 + 构建期占位符

### 6.1 绑定源码（python/src/，四文件 7175 行）

模块入口 pyTensorRT.cpp 只有 63 行，但藏着一个关键设计：`PYBIND11_MODULE(TENSORRT_MODULE, m)`（pyTensorRT.cpp:26）——**模块名是编译期宏**，不是字面量。python/CMakeLists.txt:39-40 的模块清单 {tensorrt, tensorrt_lean, tensorrt_dispatch} 经 :192 `TENSORRT_MODULE=${moduleName}` 注入编译，:247-251 双 foreach（模块 × Python 版本）批量实例化同一份源码。这就是"一套绑定源码出三个 wheel"的机制。:40 的 `py::class_<FallbackString, std::unique_ptr<FallbackString, py::nodelete>>(..., py::module_local())` 一行干两件事：`py::nodelete` 防 Python GC 误释放 TRT 持有的字符串；`py::module_local` 让 tensorrt 与 tensorrt_lean/tensorrt_dispatch 可同进程导入。

三个 infer/ 大文件各有性格：
- **pyCore.cpp（1924 行）**：pybind11 `def_property` 链式风格的典型（:1059 extra_memory_target、:1305-1317 debug_sync/profiler/engine/device_memory/active_optimization_profile）。注意 `PYBIND11_MODULE` 宏体是 tree-sitter 的提取盲区——宏内 lambda 与 def 链全靠批甄别手扫建节点，静态工具分析此文件会系统性低估。
- **pyGraph.cpp（1250 行）**：`utils::throwingDimsGetter` 包装 getter 使维度属性可抛 Python 异常（:411 tensor.shape、:451/453/461-467 卷积系属性）；:275-318 的 `attention_set_operation/causal_kind/query_form/...` 与 `kv_cache_update_layer_set_*` 系列 setter 桥接 10.x 注意力/KV 缓存语义；:25/:168 的 `#if ENABLE_INETWORK_SERIALIZE` 在开源仓无对应文件——内部构建特性，开源侧恒为关闭。
- **pyPlugin.cpp（3938 行）**：trampoline 双层结构——Python 基类捕获 override，`*Impl` 包装类管 py::handle 生命周期，全局 `std::map<IPluginV2*, py::handle> pyObjVec`（pyPlugin.cpp:85）记账防泄漏；`PLUGIN_API_CATCH`（:32）/`PLUGIN_API_CATCH_CAST`（:42）宏统一吞异常，因为 noexcept 虚函数不能让 Python 异常外溢。

utils.cpp 的 dtype 映射里 kINT4/kFP4 分支挂着 TRT-22011 TODO、sub-byte 尺寸返回 -1（utils.cpp:80-96 的 switch）。

### 6.2 打包四轨与占位符（python/packaging/）

四轨并行：`bindings_wheel`（含编译产物的绑定 wheel）/`frontend_sdist`（纯前端源码分发）/`libs_wheel`（独立闭源库 wheel，CMakeLists.txt:31 说明 moduleName ∈ tensorrt/tensorrt_dispatch/tensorrt_lean）/`metapackage`（元包，CMakeLists.txt:27 同三模块名）。加上模块三实例，打包矩阵是"3 模块 × 4 轨"。

`##TENSORRT_MODULE##` 是构建期替换占位符，密集出现在 bindings_wheel/tensorrt/__init__.py（224 行）：:26 `import ##TENSORRT_MODULE##_libs`、:45 兼容重打包路径、:84 以占位符为键的分派表、:96 `from .##TENSORRT_MODULE## import *`、:98 `__version__ = "##TENSORRT_PYTHON_VERSION##"`、:135 RTX 分支（`"##TENSORRT_MODULE##" == "tensorrt" or ... == "tensorrt_rtx"`）；:180 的 `import numpy as np` 在函数体内延迟（重依赖不挡 import）。

**双份镜像的真相（勘误）**：frontend_sdist 与 bindings_wheel 都带 tensorrt/plugin/ 子包，但**并非逐字节镜像**——sdist 版 _lib.py 第 18 行只有一条 `from ##TENSORRT_MODULE##_bindings.plugin._lib import *`（薄壳转出口），而 bindings_wheel 版顶部有完整的 `import tensorrt as trt`/`from ._plugin_class import _TemplateJITPlugin` 等实现导入（两文件 diff 实证）。

### 6.3 tensorrt.plugin 子包：Python 原生插件的 AOT/JIT 双模式

这是 TRT 10.x 引入的"用 Python+triton 写插件"通道，C++ 对端契约即第 3 节末的 NvInferPythonPlugin.h：
- plugin/__init__.py:28-41 用 `importlib.import_module` + `pkgutil.iter_modules` 做运行时包发现（静态 scanner 盲区，全部 8 个子模块边靠人工补）；它与 _lib.py 互为循环导入，靠晚导入解环；
- _lib.py 装饰器内五处延迟 `import tensorrt.plugin as trtp`（:404/481/556/654/669，解循环）与两处 `import triton`（:482/557，JIT 编译器按需拉起）；
- _plugin_class.py:25 `if IS_AOT_ENABLED:` 条件块内的 `_TemplateAOTPlugin`（:319）是提取盲区（条件缩进块内类定义 tree-sitter 漏收、批甄别手补）；与之相对 `_TemplateJITPlugin`（:227）在常规缩进——**AOT（triton 离线编译）/JIT 双模式**是该包架构要点；
- _tensor.py:1141 `class KernelLaunchParams`（同样藏在 IS_AOT_ENABLED 块，:1138 起）：用运算符重载把 TRT 尺寸表达式伪装成 int 语义（常量可求值、非常量走 exprBuilder），SymInt 体系让插件代码能同时跑在静态与动态 shape 上。

## 7. 四工具生态：Polygraphy 三分、gs 图手术、QAT 双域、trtexec 扩展

### 7.1 Polygraphy（0.53.6，__init__.py:3）——深度学习推理"瑞士军刀"

三分 539 文件层节点（L11 核心运行时 219 / L12 examples 117+tests 115 / L13 docs 72 rst+ci 88；另 18 属 trtexec 扩展单列 7.4）：
- **backend 分舱制**：polygraphy/backend/ 下 base/common/onnx/onnxrt/pluginref/pyt/tf/trt/tensorrt_rtx 九舱，每舱同构 Loader+Runner 对。trt 舱最厚——runner.py:171 `class TrtRunner(BaseRunner)`、:231 `activate_impl`、:600 `infer_impl`，配 calibrator.py（INT8 校准桥）、algorithm_selector.py（算法选择回调）、config/profile/file_reader。pluginref 舱是纯 Python 参考实现（跑不了 GPU 也能对拍插件语义）。tensorrt_rtx 是 RTX 硬件后端新舱，选择开关在 mod/trt_importer.py:27-35：按 `config.USE_TENSORRT_RTX` 在 `tensorrt` 与 `tensorrt_rtx>=1.0` 间惰性切换导入。
- **comparator 七件套**（comparator/compare/data_loader/postprocess/struct/util/comparator）：跨后端输出比对引擎，精度调试的心脏。
- **CLI 骨架**：tools/script.py:67 `ensure_safe` 安全模型守门全部写入 API、:226 `class Script`（--gen-script 生成脚本引擎）、:307 `add_import`；tools/registry.py:41 `importlib.import_module` 字符串动态加载子命令（导入副作用即注册，又一 scanner 盲区）；args 框架基类 BaseArgs（tools/args/base.py:33-175）定义 add_parser_args/parse/add_to_script 三段生命周期。
- **调试方法论落在子工具**：tools/check/subtool/（accuracy.py/lint.py——lint 用模型切分-重推理循环定位最小故障集）与 tools/debug/subtool/（build/precision/reduce/repeat——迭代构建定位精度损失层）。debug.py 的 docstring 本身就是一篇精度调试方法论。

### 7.2 onnx-graphsurgeon（0.6.2，__init__.py:10）——ONNX 图手术

`import onnx_graphsurgeon as gs` 的唯一入口是 __init__.py 的 from-import re-export（Graph/Node/Tensor/Constant/Variable/Function/GraphPattern 全在此汇聚）。三个工程亮点：
- **惰性求值防大常量物化**：ir/tensor.py:222 `class LazyValues`、:274 `SparseValues` 实现 `__getitem__` 惰性访问；
- **防循环延迟导入**：ir/graph.py:384 `cleanup` 内部才 import Function/export_onnx（:416 cleanup_subgraphs），:696 `fold_constants`，onnxruntime 到 :1175/:1255 才真正加载；
- **导出器三细节**（exporters/onnx_exporter.py）：:174 FP4 数组经 numpy 导入字节翻倍、必须 `onnx.numpy_helper._pack_4bitx2` 重打包；:243 AttributeRef 按名引用而非内联；为绕 Netron 空 tensor 崩溃塞 dummy 数据。
graph_pattern/graph_pattern.py 提供模式匹配改写 DSL（Polygraphy 的 surgeon/weight_strip 也复用它）；examples/ 13 个目录 30 个脚本覆盖替图/剪枝/常量折叠/局部函数标准动作。

### 7.3 量化双域：pytorch-quantization（85 文件）与 tensorflow-quantization（82 文件）

两工具都走 QAT（量化感知训练）路线，产出带 Q/DQ 节点的图对接 TRT builder 的显式量化管线：
- **pytorch-quantization**：nn/modules/tensor_quantizer.py:34 `class TensorQuantizer(nn.Module)`（455 行单类是量化模块运行时心脏；:98/:103 按 `calib_method` 字符串延迟实例化 Max/Histogram 校准器）；quant_modules.py:28 namedtuple 三元组（orig_mod/mod_name/replace_mod）+ :126 `initialize()` + :151-152 `apply_quant_modules()` 的模块级全局单例猴子补丁（`import pytorch_quantization.nn as quant_nn` 即触发入口）；tensor_quant.py:620-624 以 `xxx = XxxFunction.apply` 形式导出 tensor_quant/fake_tensor_quant/scaled_e4m3 等可调用别名。
- **tensorflow-quantization**：quantize_wrappers.py:29 `DISABLED_LAYER_QUANTIZATION_DEFAULT` 默认对 MaxPooling2D/BatchNormalization/Add/Multiply 不量化（NVIDIA 方案，可被 qspec 显式开启）；quantize_wrapper_base.py:175 在 call() 内延迟 `from tensorflow_quantization import G_NUM_BITS...` 规避 __init__ 循环导入；quantize.py 是图遍历改写主引擎，custom_qdq_cases.py 收纳特殊 Q/DQ 位置用例。

### 7.4 polygraphy-extension-trtexec（18 文件）——巨石工具插件化接入的教科书

把命令行工具 trtexec 接入 Polygraphy runner 框架成为第 N 个后端：backend/runner.py:135 `class TrtexecRunner(BaseRunner)`、:44 `TRTEXEC_DEFAULT_PATH = "trtexec"`、:116 `get_inference_time(perf_output)` 解析 trtexec 性能输出；args/runner.py 继承 polygraphy 的 BaseRunnerArgs 四段式（get_name_opt_impl/add_parser_args_impl/parse_impl/add_to_script_impl），:286 `add_to_script_impl` 经 `script.add_import(frm="polygraphy_trtexec.backend")` 让**生成脚本运行时引用** TrtexecRunner（非 Python import 边），:299-300 含 `polygraphy>=0.39.0` 版本分支才取 TrtConfigArgs.refittable。可见性协议：包级 `import *` 只暴露 @mod.export() 装饰对象，未装饰的辅助函数须从子模块直取（tests/test_runner_backend.py 即如此绕行）。

## 8. 新人上手：阅读路线、可跑路径与仓内 Agent 技能

### 8.1 十步阅读路线（对应图谱 16 步 tour 的精编版）

1. **边界认知**：README.md:5-12（11.x 移除清单）→ .gitmodules（parsers/onnx 指向独立仓）→ CHANGELOG.md 头部。先接受"生态壳"设定，避免找引擎源码。
2. **API 主链**（半天）：NvInfer.h:21-22 聚合关系 → NvInferRuntime.h 的 IRuntime(:1900)/ICudaEngine(:3087)/IExecutionContext(:4032)/enqueueV3(:4721) → NvInferVersion.h:30 版本宏。
3. **插件 ABI**（半天）：NvInferPluginBase.h:205 IPluginV3 → NvInferRuntime.h:417 被弃用的 V2DynamicExt 对照 → inferPlugin.cpp:172 注册中心。
4. **读一个 V3 插件样板**（1 小时）：multiscaleDeformableAttnPlugin.cpp:37-50 的 getCapabilityInterface 分面——最小完整 V3 生命周期样本。
5. **读 bertQKV**（半天，选做深水区）：先逻辑半边（mhaRunner.h:42 类族 → qkvToContextPlugin.cpp:852 createMHARunner）再资产半边（fused_multihead_attention_v2.h:410-429 元信息表）；**跳过 10 个死 blob**（第 5 节）。
6. **Python 层**（1 小时）：pyTensorRT.cpp:26 宏模块名 → python/CMakeLists.txt:247-251 实例化矩阵 → bindings_wheel __init__.py:96 占位符。
7. **工具线按需**：精度调试读 Polygraphy check/debug 子工具族；改图读 gs ir/graph.py:384；量化读 quantize_wrappers.py:29 默认豁免表。
8. **端到端演示**：demo/DeBERTa 五件链——deberta_pytorch2onnx.py → deberta_onnx_modify.py（gs 改图实战）→ deberta_ort_inference.py（ORT 对照基准）→ deberta_tensorrt_inference.py（TRT 推理）——正好是本仓五域能力的一次全链彩排。

### 8.2 最短可跑路径

- `quickstart/`：IntroNotebooks（Notebook 入门）+ SemanticSegmentation + deploy_to_triton，配 Makefile/Makefile.config——官方认可的 30 分钟上手线；
- `samples/`：41 个 .cpp 的最小示例族（sampleOnnxMNIST/sampleCudla/sampleDynamicReshape/sampleNonZeroPlugin 等，每个含 README+CMakeLists），是 NvInfer API 的可编译文档；
- `documents/supported_models.md` + `documents/import_workflows.md`：官方支持模型矩阵与 ONNX/TF 导入工作流（配三份 roadmap PDF：2025q1/2026q1/2026q3）。

### 8.3 .agents/skills：NVIDIA 仓内原生 agent 协作开发实证

仓根 `.agents/skills/` 下五张技能卡，是主流 GPU 厂商把 agent 协作工作流直接进仓的实证（与 TensorRT-LLM 仓内 CLAUDE.md 同一趋势）：
- **trt-cpp-runtime-quickstart / trt-onnx-quickstart / trt-torch-quickstart**：三张单 SKILL.md 快速上手卡（C++ runtime / ONNX / PyTorch 三条部署线）；
- **trt-perf-analysis**：最重的一张，含 report_template/ + schemas/ + scripts/（analyze_trt_perf.py、package_report.py、validate_analyze_data.py + trt_perf 包）——把 engine 性能分析做成可校验的数据管线（schema 校验 + 打包报告）；
- **trt-strong-typing-migration**：scripts/migrate.py 是 AST 级 10.x→11.x 迁移器——:39 `_is_attr`、:57/:65 builder/network flag 识别、:73 `_strongly_typed_arg`、:111 `visit_Call`、:156 `_is_weak_network_arg` 自动把弱类型网络调用改写为强类型，配 verify.sh 验证。11.x 断代（第 1 节）的迁移成本被 NVIDIA 自己工具化在这张卡里。

### 8.4 版本锚点与本仓特有陷阱清单

- 版本三锚：VERSION 文件（11.3.0.99，CMake 与 wheel 注入源）、NvInferVersion.h:30 编译期宏、CHANGELOG.md:3（11.3 GA 2026-09-22）。图谱与本文全部锚定 git `98adec82`。
- **陷阱一：注册名≠类名**。ONNX 图/PluginConfig.yaml 里写的是字符串常量（qkvToContextPlugin.cpp:47），grep 类名找不到注册入口——永远从 `REGISTER_TENSORRT_PLUGIN` 与 inferPlugin.cpp 反查。
- **陷阱二：文档与源码漂移**。generateDetectionPlugin/README.md:3 官宣 deprecated 但 cpp/h 无任何废弃标记；detectionLayerPlugin README 类名小写 l 笔误；multilevelProposeROI README 参数表缺列；PluginConfig.yaml:72 golden_io_path 悬空。本仓 README 是"意图文档"，判定以源码为准。
- **陷阱三：cubin 两代符号**。同目录混合 `*_kernel_sm{arch}_cubin`/`_cu_o[]` 与 `cubin_fmha_v{1,2}_*` 两代命名（第 5 节），grep 时两套 pattern 都要试。
- **陷阱四：dlopen 间接层**。插件不链接 cublas/cudnn——符号经 Wrapper 五件套运行时解析（第 4.2 节），排查链接问题先看 cublasWrapper.cpp:97 这类 dllOpen 调用点。
- **陷阱五：构建期占位符**。##TENSORRT_MODULE## 在源码里是合法 Python 的破坏者（__init__.py:26/:96 直接语法报错），clone 后不能直接 import，必须经 packaging 构建链替换。

### 8.5 一周自检清单

读完本 ONBOARDING 后，用六问自检是否真正建立了本仓的心智模型（答案全部在正文锚点处）：
1. 引擎本体在哪个仓？为什么 plugin 域编译前要设 TRT_LIBPATH？（第 1 节）
2. enqueueV3 在哪个头哪一行？它与 executeV2 的代际关系？（第 3 节）
3. 用户在 ONNX 里写的 "CustomQKVToContextPluginDynamic" 与 C++ 类 QKVToContextVarSeqlenPlugin 是什么关系？（第 4.3 节）
4. 一个 cubin 文件名 fused_multihead_attention_v2_int8_128_64_kernel.sm87.cpp 的四个坐标各是什么？为什么仓库里找不到生成它的脚本？（第 5 节）
5. 为什么 clone 下来的 python/packaging/bindings_wheel 不能直接 import？（第 6.2 节）
6. 精度回退了，Polygraphy 里哪两个子工具族是标准工作流？（第 7.1 节）
六问全答对，即可进入 explain 系列的深水区（bertQKV 调度链、pybind11 trampoline、gs 惰性求值三篇是推荐首读），并结合仓内五张技能卡把认知落到可复现的工程操作上。

---

### 附：本文行号锚清单（65 处，全部 @ 98adec82 逐一经源码核实）

仓根与治理：README.md:5-12/51/106-109/116 · CHANGELOG.md:3-8 · CMakeLists.txt:18/261/265/308/362 · .gitmodules（3 子模块）· VERSION
include：NvInfer.h:21-22/8162/10579/11513 · NvInferRuntime.h:417/613/830/873/1095/1192/1281/1900/3024/3087/4032/4721 · NvInferRuntimeBase.h:283 · NvInferPluginBase.h:140/205/227 · NvInferPlugin.h(42 行全文) · NvInferVersion.h:30-31 · NvInferImpl.h(1402 行) · NvOnnxParser.h:127/189/197/220 · NvInferPythonPlugin.h:85/116/276/291
plugin：plugin/CMakeLists.txt:34/66-70/78 · inferPlugin.cpp:79/82/172/174-211 · plugin.h:53/69 · serialize.hpp:30/33 · vc/checkMacrosPlugin.h:203/270/317 · cublasWrapper.cpp:28/35/97 · cublasWrapper.h:144 · cublasLtWrapper.h:39-56 · cufftWrapper.cpp:44/46/91 · cudaDriverWrapper.h:142 · qkvToContextPlugin.cpp:45-47/55/760/852/869 · mhaRunner.h:42/98/148/205 · mhaRunner.cu:928/954/1099/1122 · zeroPadding2d.cu:36/64 · bertCommon.h:102/163 · PluginConfig.yaml:18/19/21/72/151/168 · fused_multihead_attention.h:346-351/478-489/495/646 · fused_multihead_attention.h(45 extern) · fused_multihead_attention_v2.h:111-118/395-398/400-405/410-429/423/1247 · v2 CMakeLists.txt:29-30 · embLayerNormPlugin.cpp:37/325-326 · embLayerNormPlugin.h:38 · multiscaleDeformableAttnPlugin.cpp:28-29/37-50 · efficientNMSPlugin.cpp:42-45/104/514 · generateDetectionPlugin/README.md:3
python：pyTensorRT.cpp:26/40 · pyCore.cpp:1059/1305-1317 · pyGraph.cpp:25/168/275-318/411/451-467 · pyPlugin.cpp:32/42/85 · utils.cpp:80-96 · python/CMakeLists.txt:39-40/192/247-251 · bindings_wheel __init__.py:26/45/84/96/98/135/180 · plugin/__init__.py:28-41 · _lib.py:404/481-483/556-558/654/669 · _plugin_class.py:25/227/317-319 · _tensor.py:1138/1141 · frontend_sdist _lib.py:18 · metapackage/CMakeLists.txt:27 · libs_wheel/CMakeLists.txt:31
tools：Polygraphy __init__.py:3 · trt_importer.py:24-35 · runner.py(trt) :171/231/600 · script.py:67/226/307 · registry.py:41 · args/base.py:33-175 · gs __init__.py:10 · ir/graph.py:384/416/696/1175 · ir/tensor.py:222/274 · onnx_exporter.py:174/243 · tensor_quantizer.py:34/98/103 · quant_modules.py:28/126/151-152 · tensor_quant.py:620-624 · quantize_wrappers.py:29 · quantize_wrapper_base.py:175/190 · trtexec backend/runner.py:44/116/135 · args/runner.py:286/299-300
技能与演示：.agents/skills/trt-strong-typing-migration/scripts/migrate.py:39/57/65/73/111/156 · demo/DeBERTa（5 py 文件链）· documents/（supported_models.md/import_workflows.md）
