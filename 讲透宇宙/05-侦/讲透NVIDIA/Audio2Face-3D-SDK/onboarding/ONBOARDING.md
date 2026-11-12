# Audio2Face-3D-SDK ONBOARDING

> 知识图谱：726 节点 / 1312 边 / 15 层 / 16 步 tour，validator 0 issues，fingerprints 267 文件基线 @ git 1ca0f025（2026-11-06 分析）。
> 本文档全部行号锚均从该 commit 源码逐一核实；与图谱批阶段摘要不一致处以源码为准（勘误见文末）。
> 上游论文：arXiv:2508.16401（CITATION.md:11-14）；许可 MIT（LICENSE.txt）。

## 1. 项目定位

Audio2Face-3D-SDK 是 NVIDIA 开源的**音频驱动 3D 面部动画推理 SDK**：输入语音（PCM 流式或整段 wav），输出面部网格顶点动画（geometry/pose）与 blendshape 权重，并行输出情感分类结果。它是 Omniverse Audio2Face-3D 产品背后的核心推理栈，以**单仓多 SDK** 形态发布：

- **audio2face-sdk（a2f）**——几何动画线：音频→TRT 推理（回归或扩散模型）→多轨动画→blendshape 求解；
- **audio2emotion-sdk（a2e）**——情感线：音频→情感分类器→后处理管线→a2f 情绪库注入；
- **audio2x-common（a2x）**——两 SDK 共享的公共基座：张量家族、三累积器、TensorRT 推理引擎抽象、错误码与日志宏；
- **audio2x-sdk**——伞形共享库，把三个门面 .cpp 聚合为一个可分发的 `audio2x.so/dll`。

技术栈为纯 **C++/CUDA/TensorRT**（无 Python 运行时；Python 仅用于生成测试数据，README.md 系统要求节：CUDA 12.8+、TensorRT 10.x、Python 3.10+）。设计哲学在 docs/README.md:91-94 钉死四条：Performance First（GPU-first）、Model Abstraction（模型不同接口统一）、Asynchronicity（执行调用只调度立即返回）、Efficiency（禁用功能零浪费）。README.md（279 行）是 22 节快速上手，docs/README.md（376 行）是概念总纲——新人先读后者。

模型资产不在仓内：`download_models.sh:15-21` 用 `hf download` 拉 5 个 HuggingFace 门控模型——A2F 四个（v3.0 / v2.3.1-Claire / v2.3.1-James / v2.3-Mark）+ A2E 一个（v2.2），落地 `_data/` 目录。

## 2. 架构总览

### 2.1 三库 × 三层的矩阵结构

每个库内部都是同一三层范式（这也是图谱 15 层的划分依据）：

| 层 | 语义 | 典型形态 |
|---|---|---|
| **公共契约** `include/<sdk>/` | 纯虚接口 + C 风格工厂声明，跨编译器 ABI 稳定 | a2f L06 / a2e L09 / a2x L03 |
| **internal 实现头** `include/<sdk>/internal/` | 实现类骨架、模板、宏；不对外 | a2f L07 / a2e L10 / a2x L04 |
| **源实现** `source/<sdk>-core/` | .cpp/.cu 落地；门面 .cpp 只做一行转发 | a2f L08 / a2e L11 / a2x L05 |

除纵向三层外还有一个横切面——**L12 CUDA 设备代码层**：9 个 .cu 设备实现文件（a2f 5 个 / a2e 1 个 / a2x 3 个）不按库分目录归属，而是作为独立一层汇聚——因为 nvcc 编译单元与 C++ 编译单元的边界（Eigen 头在 nvcc 下告警雪崩，mask_extraction.h:1-37 因此独立成文件）与库的公共/internal 边界正交。

### 2.2 ABI 兼容三原则（全 SDK 的宪法）

docs/README.md:242-261 钉版：

1. **接口化设计**（:248）——所有组件经纯虚接口暴露（`nva2x::IExecutor`、`nva2f::IBlendshapeSolver` 等），实现细节不跨 ABI；
2. **避免 STL 跨界**（:250-252）——公共 API 不出现 `std::vector/std::string`；唯一例外 `std::error_code`（ABI 稳定且错误处理必需）；
3. **Create+Destroy 对象协议**（:260-261）——工厂函数创建，释放一律走 `obj->Destroy()` 虚方法而非 `delete`（分配与释放在同一边界完成）。

三原则的落地证据遍布代码：`cuda_fwd.h:23-24` 单行前置声明 `typedef struct CUstream_st *cudaStream_t;` 让公共头在无 CUDA toolkit 环境可编译；`tensor_void.h:55-56,74-75` 用 `static_assert(sizeof(...)==16/alignof(...)==8)` 把视图 ABI 焊死；`internal/unique_ptr.h:29-32` 的 `Destroyer` 删除器（`operator()` 内调 `obj->Destroy()`）是全 SDK 智能指针统一范式。

### 2.3 门面转发模式（链接层隔离）

三个门面文件全部是"声明 `_INTERNAL` 原型 + 一行透传"：

- `audio2face-sdk/source/audio2face/audio2face.cpp:25` 注释直说 "Implementations are inside audio2face-core.lib"；
- `audio2emotion.cpp` 同构（333 行 27 个 API 全部透传 `_INTERNAL`，audio2emotion.cpp:40-60 可见原型声明段）；
- `audio2x-common/source/audio2x/audio2x.cpp`（1004 行，75 个 `nva2x::` 工厂定义，如 :28 `CreateAudioAccumulator` 转发 `internal::CreateAudioAccumulator`）。

这套模式把**导出面（audio2x.so）与编译单元（*-core 静态库）解耦**：改实现不动 ABI，加接口只动门面。

### 2.4 图谱分层导航（15 层 → 三纵两横）

- **纵三线**：L03-L05（a2x：契约→基座→源实现）、L06-L08（a2f）、L09-L11（a2e）；
- **横两块**：L12（CUDA 内核）+ L15（cmake 构建链）是跨库汇聚层；L13（benchmarks 18 文件）与 L14（samples 14 文件）是验证生态；L01-L02 是文档与 bat/sh 对偶工具链。

## 3. 主推理链（audio2face 几何线）

数据流全景：**wav → 音频累积器 → TRT 推理 → 回归/扩散几何 → 多轨动画 → blendshape 求解 → 面部动画**；情感线并行注入（见第 4 节）。

### 3.1 API 面与资产装载 Bundle

`audio2face-sdk/include/audio2face/audio2face.h`（427 行）是 API 总括头：:44-110 声明全部 `Create*` 工厂（单轨/多轨动画器、情绪库、JobRunner、回归与扩散四类模型缓冲、噪声生成器、blendshape 求解器），:114 起 `ReadAnimatorParams` 与 `Read*Info` 资产读取族。

"读资产→建执行器"一步式契约在公共 `parse_helper.h`：`namespace IRegressionModel`（:31-107，内含 INetworkInfo:34 / IGeometryModelInfo:71 / IBlendshapeSolveModelInfo:94）与 `namespace IDiffusionModel`（:109-184）各一套 Info 接口；`IGeometryExecutorBundle`:215 与 `IBlendshapeExecutorBundle`:246 是 Bundle 接口——一次 Read 调用返回装配好的执行器全家桶，替代手工逐件拼装（internal 版 parse_helper 是其 62 方法实现，从 JSON+npz 读取网络与动画器数据）。

### 3.2 执行器层次

公共 `executor.h` 三层：`IFaceExecutor`:33（继承 a2x 根接口 `nva2x::IExecutor`）→ `IGeometryExecutor`:61（产姿态）与 `IBlendshapeExecutor`:113（产权重）双分支。internal `executor.h:35-80` 定义 8 个 `IFaceExecutorAccessor*` 能力探测接口（InputStrength/GeometryExecutor/GeometryResultsCallback/BlendshapeSolvers/Skin/Tongue/Teeth/Eyes Parameters）——C 风格 Get/Set API 经 Accessor 触达 private 细节，是 a2e 同款协议（第 4 节）的 a2f 版。

### 3.3 回归链与扩散链（双模型骨架共享）

- **公共骨架**：`executor_core.cpp:88-251` 的 `GeometryExecutorCoreBase::BaseInit`（163 行）装配动画器/缓冲/数据上载，是双模型共用入口；
- **回归链**：`executor_regression.cpp:45-282` Execute 主循环 237 行——按批推理→PCA 重建→动画后处理→回调；创建参数支持任意 FPS 分数帧率（frameRateNumerator/Denominator，executor_core.cpp:91-93）与情绪库引用、显式情绪注入（ReadExplicitEmotion）；
- **扩散链**：`executor_diffusion.cpp:46-359` Execute 313 行——推理→噪声→后处理→回调。随机性可控：`noise.h:32` `CurandGeneratorHandle` 包装 cuRAND 句柄，`noise.h:53` `NoiseGenerator` 每轨一个句柄，`noise.h:59` `Reset(trackIndex, generateIndex)` 可把生成器重置到指定序号——**扩散输出的可复现开关**；`executor_diffusion_core.h:81` 核心持有 `_noiseGenerator`。GRU 状态跨帧传递：`model_diffusion.h:79-86` 四组 Get*GRUStateTensor 访问器 + `CopyOutputToInputGRUState`（:84 注释明确 GRU 状态是 interleaved 布局，无法给单轨全量视图）。

### 3.4 单轨废弃 → 多轨取代（代际活化石）

`animator.h:27-30` 文件注释直说单轨类 "obsolete and ... replaced by the multi-track animator classes"——废弃但保留兼容。多轨版 `multitrack_animator.h` 五接口（:30 `IMultiTrackAnimatorPcaReconstruction`、:72 Skin、:119 Tongue、:168 Teeth、:217 Eyes）支持位掩码选择性执行（:53 `SetActiveTracks(const uint64_t*, size_t)`，nullptr=全激活）与批量 `Animate`（:56，batchSize 参数）。实现侧 `multitrack_animator.cpp`（1023 行）组合单轨数据与 cuBLAS 句柄，`animator.cpp`（935 行）是单轨遗留实现。

### 3.5 blendshape 求解器双路径：CPU BVLS / GPU ADMM

公共 `blendshape_solver.h:30-35` 钉默认正则参数：`kDefaultL1Reg=1.0f`、`kDefaultL2Reg=3.5f`、`kDefaultSymmetryReg=100.0f`、`kDefaultTemporalReg=0.0f`、`kDefaultTemplateBBSize=54.7f`、`kDefaultTolerance=1e-10f`。

- **CPU 路径 = Eigen + BVLS**（有界变量最小二乘）：`internal/bvls.h` 八个数值例程——`constrainedMin`:29（主入口）、`costAndGradient`:36、`initialFeasiblePoint`:43、`computeKktOptimality`:51、`varToDetach`:56、`makePointFeasible`:64、`updateOnBound`:71、`solveSystem`:78；实现 `bvls.cpp`（372 行）含梯度/最速下降变量选择/KKT 检查/边界投影全流程。CPU 异步由线程池承载：`job_runner.h:38` `ThreadPoolJobRunner`（:47 condition_variable + :49 `std::deque<std::packaged_task<void()>>`）。docs/README.md:210 说明：用户可用 `nva2f::IJobRunner` 自控线程，不提供则默认 `std::thread` 池。
- **GPU 路径 = cuBLAS + ADMM**：`blendshape_solver_gpu.cpp`（343 行）工作缓冲全驻显存，迭代核心在 `admm.cu`——:32 `ADMMupdateKernel`（z/u 交替更新）+ :75 `ClipKernel`（上下界投影），声明头 `internal/admm.h`。

工厂侧 `audio2face.h:110` `CreateBlendshapeSolver(bool gpuSolver)` 一开关选路径。

### 3.6 两级管线与交互式协议

**两级管线**＝几何执行器（产姿态）→ blendshape 求解执行器（姿态→权重）。`executor_blendshapesolve.h:30-35` `BlendshapeSolveExecutor` 六重继承（`IBlendshapeExecutor` + 5 个 Accessor），经几何执行器回调桥接；交互版 `interactive_executor_blendshapesolve.h:30-38` 九重继承（+Teeth/Eyes Parameters 等 8 个 Accessor）。

**交互式协议**根接口定义在 a2x 公共层（模型无关）：`audio2x/interactive_executor.h:33` `IInteractiveExecutor`，四个关键方法 `Invalidate`:40（层失效）、`ComputeFrame`:62（单帧流式）、`ComputeAllFrames`:64、`Interrupt`:68。a2f 侧 `interactive_executor.h:28` 一行别名 `using IFaceInteractiveExecutor = nva2x::IInteractiveExecutor;` 直接复用。模型无关骨架 `interactive_executor.cpp`（476 行，GeometryInteractiveExecutorBase 47 方法）；回归版 `interactive_executor_regression.cpp:108` Compute 主流程（按批推理→PCA 重建→动画后处理，PCA 帧区间缓冲）；扩散版 `interactive_executor_diffusion.cpp`（517 行）带 ProgressScope 进度守护与预览推理数限制。

## 4. audio2emotion 链（情感线）

### 4.1 双命名空间契约——本 SDK 最独特的形态

a2e 公共 API 全在 `nva2e` 命名空间，`audio2emotion.h`（202 行）声明 27 个 C 风格 DLL API（31 处 `AUDIO2EMOTION_DLL_API` 声明，含 4 个双参重载）：执行器工厂（:73 `CreateClassifierEmotionExecutor`、:80/:88 `CreatePostProcessEmotionExecutor` 两重载）、交互版（:131/:139/:148）、模型信息读取器（:154-183，classifier/post-process 双模型变体）与 Bundle 一步装配（:186 `ReadClassifierEmotionExecutorBundle`、:195 `ReadPostProcessEmotionExecutorBundle`）。

**双命名空间**是理解 a2e 的钥匙：公共 `parse_helper.h:30-87` `namespace IClassifierModel` 与 :89-116 `namespace IPostProcessModel` 各定义一套 INetworkInfo/IConfigInfo/IEmotionModelInfo——classifier 模型（音频→情感向量）与 post-process 模型（情感向量→处理后输出）是两个独立 TRT 网络，可单独装配（postprocess 版可在无有效推理模型时单独跑）。internal 版 `parse_helper.cpp`（662 行）承载 JSON 解析与双装配线：`InitClassifier`:407、`InitPostProcess`:469、全部 `Read*_INTERNAL`:529 起。图谱批阶段正是用命名空间限定名消歧这两套同构接口（NOTES-DIGEST 记录在案）。

### 4.2 执行器链：classifier 推理 + postprocess 双段

`executor.cpp:148` `EmotionExecutorBase::BaseExecute` 驱动"读音频→推理→后处理→分发回调"循环。classifier 核心封装音频窗口读取、推理缓冲绑定与 TRT 批量 RunInference 完整数据通路（`executor_classifier_core.cpp`）；postprocess 核心只装配后处理算子链（`executor_postprocess_core.cpp`）。internal `executor.h` 的 Accessor 协议（Get/SetExecutorXxx 经接口访问 private）与 a2f 同款——C 风格 API 与 C++ 实现解耦的桥。

### 4.3 单轨八算子（host 侧顺序管线）

`postprocess.h:44-67` `PostProcessParams` 十参数定义后处理语义：emotionContrast/maxEmotions/beginningEmotion/preferredEmotion/liveBlendCoef/enablePreferredEmotion/preferredEmotionStrength/liveTransitionTime/fixedDt/emotionStrength。

`postprocess.cpp`（331 行）八个 Apply* 算子按序调度（:250-273 调度点）：

| 序 | 算子 | 行号 | 语义 |
|---|---|---|---|
| 1 | `inplace_softmax` | :36（调用 :60） | 归一化为概率分布 |
| 2 | `ApplyEmotionContrast` | :56 | 对比度增强 |
| 3 | `ApplyNullifyUnmappedEmotion` | :63 | 未映射情感置零 |
| 4 | `ApplyMaxEmotions` | :73 | 只保留 top-maxEmotions |
| 5 | `ApplyA2FEmotionIndexConversion` | :94 | a2e 索引→a2f 索引转换 |
| 6 | `ApplyBlending` | :111 | live/preferred 混合 |
| 7 | `ApplyTransitionSmoothing` | :126 | 时间过渡平滑 |
| 8 | `ApplyEmotionStrength` | :138 | 总强度缩放 |

### 4.4 多轨位图后处理（`__popcll` 紧凑映射）

多轨版 `multitrack_postprocess.h:57` `SetActiveTracks(const uint64_t*, size_t)` 携带轨道激活位图。CUDA 侧 `multitrack_postprocess_cuda.cu`（531 行）三个 `__global__` 内核：:35 `PostProcessSetKernel`（置初值）、:63 `PostProcessKernel`（通用路径）、:245 `PostProcessKernelLocal`（局部快路径）。核心技巧在位图→紧凑下标映射：`:52` `inputTrackIdx += __popcll(activeTracks[i])`（前缀计数 64 位字内激活位）+ `:55` 尾部部分字掩码计数——把"轨道号"映射到"激活轨数组下标"，跳过未激活轨零浪费（Efficiency 原则的设备端落地）。主机入口声明头 `multitrack_postprocess_cuda.h:47` 的 `useFastPath` 参数分派通用/快路径两条 kernel。

情感线终点回接 a2f：处理后的情感向量经 `IEmotionDatabase`（`audio2face/include/audio2face/emotion.h:28`）写入情绪库，作为回归链的额外输入（3.3 节），形成 a2e→a2f 闭环。

## 5. audio2x 基座（公共库）

### 5.1 张量家族——数据流的通用货币

`tensor.h` 总括头定义四标量类型（bool/float/int64/uint64）与 `TensorBatchInfo`:32-38（offset/size/stride 批切片描述）。`tensor_float.h`（340 行）是使用最广的接口族；**类型擦除视图** `tensor_void.h` 的 `DeviceTensorVoidView` 只含 data+size（:55-56 `static_assert(sizeof==16/alignof==8)` 锁 ABI），是各标量视图公共基形态——公共 API 传 `void` 视图、实现侧再还原类型，避免模板跨界。实现层 `internal/tensor.h`（300 行）是 HostTensor/DeviceTensor 模板与视图转换。

**四个 .cpp 完全同构**：`tensor_bool.cpp` / `tensor_float.cpp` / `tensor_int64.cpp` / `tensor_uint64.cpp` 各 104 行、各 12 个 4 行转发（批阶段甄别：纯转发不建函数节点，tensor_bool.cpp:1-104 与 tensor_float.cpp:1-104 逐行同构）。

### 5.2 对象生命周期：Destroyer 范式

`internal/unique_ptr.h:29-32` `struct Destroyer { void operator()(T* obj) const { obj->Destroy(); } }` + :49 shared_ptr 版 lambda 删除器——全 SDK 的 `UniquePtr/SharedPtr` 别名都从这出发，与 ABI 三原则的 Create+Destroy 协议（2.2 节）配套。samples 里的标准写法见 `sample-a2e-inference/main.cpp`：带自定义 Destroyer 的 `unique_ptr` + `CHECK_SUCCESS/CHECK_NOT_NULL` 宏。

### 5.3 三累积器——流式推理的数据供给侧

- **音频累积器**（最复杂）：`audio_accumulator.cpp`（440 行）环形写入 PCM + 滑窗读取推理窗口；`internal/audio_accumulator.h:69` `WindowProgressParameters`（窗口大小/步进/时间戳）与 :87 `WindowProgress` 多窗口读取进度跟踪——低延迟流式协议的关键：音频边写边算，窗口就绪即触发推理；
- **情绪累积器**：`emotion_accumulator.h:27-37` `IEmotionAccumulator`（13 方法），类注释明确 thread-safe、GPU 加速——a2f/a2e 双线并发写的情感通道；
- **浮点累积器**：通用 float 时间序列累积。

### 5.4 TensorRT 推理引擎抽象（唯一推理通道）

公共 `inference_engine.h` 三件套：`IBufferBindingsDescription`（绑定描述）/ `IBufferBindings`（运行时绑定集合）/ `IInferenceEngine`（引擎初始化与执行）——对 TRT 的唯一抽象层，a2f 与 a2e 的模型推理都经此通道。实现 `inference_engine.cpp`（541 行）：反序列化引擎、动态维度协商、`CheckBindings`:299-401（约百行严格校验：绑定名/维度/顺序三路比对，internal `inference_engine.h` 的 BindingDescription 含比较与排序校验）。

### 5.5 错误码与日志

`error.h` 是三 SDK 共同错误基座（图谱 fanIn=57 全仓最高）：ErrorCode 枚举通用 0-5 / CUDA 20+ / TensorRT 60+ 分段。各 SDK 有独立 error.h 再分段细化（a2f 版见 3.x，:42 起 eCudaEventCreateError=20、:47 eDataNotSet=60、:49 eSampleRateTooLow=100、:51 eCublasCreateError=200、:57 eCurandCreateError=300、:64 eEmotionNotAvailable=400）。`error.cpp`（113 行）switch 生成可读消息。日志三级（ERROR/INFO/DEBUG）宏基座在 `audio2x/internal/logger.h`，各 SDK macros.h 包装自家前缀（`A2F_CHECK_RESULT`/`A2E_CHECK_RESULT` 等），编译期 `AUDIO2FACE_LOG_LEVEL` 开关。

## 6. CUDA 内核层

### 6.1 9 个 .cu 设备实现 + 5 个 kernel 声明头

源码侧 9 个 .cu（不含 tests/ 下 5 个测试 .cu）：

| 库 | 文件 | 行数 | 内容 |
|---|---|---|---|
| a2f | `multitrack_animator_cuda.cu` | 755 | 多轨动画 9 内核（6.2） |
| a2f | `animator_cuda.cu` | 347 | 单轨合成两步（Interpolator*:63/76/94 + AnimatorSkin*:155/164/175/193 等） |
| a2f | `admm.cu` | 167 | ADMM 双内核（3.5 节） |
| a2f | `blendshape_solver_cuda.cu` / `_gpu.cu` | — | 求解器辅助 |
| a2e | `multitrack_postprocess_cuda.cu` | 531 | 位图后处理三内核（4.4 节） |
| a2x | `tensor_cuda.cu` / `animated_tensor_cuda.cu` / `audio_accumulator_cuda.cu` | — | thrust par_nosync 流式 lerp/乘法/填充小件 |

kernel 声明头 5 个：a2f `internal/multitrack_animator_cuda.h`、a2e `internal/multitrack_postprocess_cuda.h`、a2x `internal/{tensor_cuda,animated_tensor_cuda,audio_accumulator_cuda}.h`。

### 6.2 multitrack_animator_cuda.cu——755 行 9 个 `__global__` 内核

源码逐个数（**勘误：图谱摘要记 10 个，源码实为 9 个**）：

:39 `TracksSetKernel`（初始化）、:51 `AnimatorSkinGetYKernelPacked`、:60 `AnimatorSkinGetFaceMaskLowerKernel`、:115 `AnimatorSkinEverythingKernel`、:169 `AnimatorSkinControlKernel`（皮肤 Everything/Control 两变体对应全脸/部分控制点模式）、:231 `AnimateTongueKernel`、:266 `ComputeJawTransformKernel`（**下颌变换**：:34 include `tbtSVD/SVD.h`，:337 `SVD::svd(A)` 在设备侧做 SVD 分解求刚体变换）、:468 `ComputeEyesRotationEverythingKernel`、:492 `ComputeEyesRotationControlKernel`（眼球旋转双变体）。

### 6.3 admm / bvls 的分工

admm.cu 两内核（ADMMupdateKernel:32 + ClipKernel:75）只服务 GPU 求解路径；CPU 路径完全不走 CUDA（Eigen + bvls.cpp 纯 host），双路径共享的只是 blendshape_solver.h 的参数与回调契约——同一数学问题（带界约束+四种正则的最小二乘）两条实现路线。

### 6.4 批阶段工程事实

.cu 文件对 tree-sitter **全盲**（NOTES-DIGEST 实证），图谱中全部 CUDA 函数节点为手工建立；mask_extraction.h 独立成文件是因为 Eigen 头在 nvcc 下告警雪崩。nvtt 追踪：`internal/nvtx_trace.h` 的 `NvtxTraceScope` RAII 域（USE_NVTX 未定义时编译为空零开销），执行主循环首行 `NVTX_TRACE(...)` 处处可见（如 executor_regression.cpp:46）。

## 7. 构建与部署

### 7.1 三级构建链（图谱 L15 层 22 个构建文件）

1. **顶层 CMakeLists.txt**：configure 时自动跑 fetch_deps（:26 注释/:36 拼脚本名）拉依赖，:147-150 `add_subdirectory` 汇入四子项目（audio2x-common → audio2emotion-sdk → audio2face-sdk → audio2x-sdk）；共 14 个 `find_package`；:81 `set(CMAKE_CUDA_ARCHITECTURES "75;80;86;87;89;90;100;120")`——从 Turing 到 Blackwell 全代际覆盖。
2. **cmake/Modules 12 个自带 FindXxx**：AudioFile/Benchmark/CXXOPTS/Cnpy/Eigen3/GTest/MagicEnum/NlohmannJson/ReflCpp/TbtSVD/TensorRT/ZLIB——`CMAKE_MODULE_PATH` 指向此处，不依赖系统安装的 Find 模块版本。
3. **库级**：`audio2face-core/CMakeLists.txt:30-38` GLOB_RECURSE 收 cpp/cu，PUBLIC 暴露 include 根 + PRIVATE 暴露 internal 头，链接 CUDA::cublas/CUDA::curand（:30-31）、Eigen3（:34）、magic_enum、refl-cpp、tbtSVD（:38）；a2x-common 另链 Cnpy/TRT/ZLIB（npz 资产读取）。

### 7.2 audio2x-sdk 伞形打包（可分发布局）

`audio2x-sdk/CMakeLists.txt`：:2 `add_library(audio2x SHARED)`，:17-19 把三个门面 .cpp（audio2emotion.cpp/audio2face.cpp/audio2x.cpp）编进同一共享库；Linux 侧 :56-57 `"LINKER:-Bsymbolic"` + `"LINKER:--exclude-libs,ALL"` 隐藏 core 库符号——防止与其他二进制链接时符号冲突（伞形库对外只剩门面 C 符号）；:92-100 POST_BUILD 拷贝 VERSION.md 与公共头到 bin 目录；:103 `add_library(audio2x-sdk::audio2x ALIAS)`。最终交付物 = 一个 audio2x.so + include/ 头目录 + 模型数据，无其他运行时依赖（CUDA/TRT 由目标机器提供）。

### 7.3 依赖与模型获取

- `fetch_deps.sh:21/27`：packman 分别拉 `deps/build-deps.packman.xml`（cmake/ninja 等构建工具）与 `deps/target-deps.packman.xml`（eigen/tensorrt 等）——**configure 即触发，无需手动**；
- `download_models.sh:15-21`：`hf download` 拉 5 个门控模型到 `_data/`（模型转 TRT engine 的步骤见 README.md 构建节）；
- `run_sample.sh:46-51`：运行前装配环境——`PATH` 前插 `${BUILD_DIR}/${BUILD_TYPE}/audio2x-sdk/bin`、`PYTHONPATH` 加 audio2x-common/scripts、`CUDA_PATH` 存在时补 `${CUDA_PATH}/bin`；bat/sh 对偶（全工具链 Windows/Linux 双份）。

### 7.4 验证生态

- **单元测试**：三仓 tests/（GTest；CUDA 测试自有 5 个 test_core_batch_*_cuda.cu）；
- **benchmarks**（L13 层 18 文件）：Google Benchmark 两套——a2f 六源文件覆盖求解器双路径/两级管线/纯几何/交互式四类，a2e 四源文件按 `kLayerInference/kLayerPostProcessing` 分层隔离度量延迟；`test_benchmark.sh` 冒烟（a2f 12 条/a2e 3 条 filter）；`benchmarks/interactive_executor.cpp:56-64` 的 `InteractiveExecutorBundle` 聚合 struct（cudaStream+audioAccumulator+emotionAccumulator+interactiveExecutor 四字段）是 SDK 组装范式的基准复刻；两套 utils.cpp 各自 WAV 读取+重采样，a2f 版多链 Cnpy/ZLIB 读 NPZ 姿态数据；
- **samples**（L14 层 14 文件，5 个示例——**勘误：图谱摘要记 6 个**）：a2f 三（`sample-a2f-a2e-executor` main.cpp 793 行最全：双模型×Bundle/Pieces×三运行模式×a2f+a2e 联合；`sample-a2f-executor` 238 行 Bundle 一步创建；`sample-a2f-low-level-api-fullface` 281 行绕过 executor 手工组装全脸管线）+ a2e 两（executor 高层 278 行=推荐起点；inference 低层 118 行=手动张量/绑定教学）。

## 8. 新人上手

### 8.1 关键入口文件（按打开顺序）

| # | 文件 | 作用 |
|---|---|---|
| 1 | `docs/README.md`（376 行） | 概念总纲：累积器/多轨/执行器层次/ABI 三原则（:242 起） |
| 2 | `audio2face-sdk/include/audio2face/audio2face.h`（427 行） | a2f API 总面：:44-110 工厂声明 |
| 3 | `audio2emotion-sdk/include/audio2emotion/audio2emotion.h`（202 行） | a2e 27 API |
| 4 | `audio2x-common/include/audio2x/interactive_executor.h` | 根协议 IInteractiveExecutor:33 |
| 5 | `audio2face-sdk/source/samples/sample-a2f-a2e-executor/main.cpp`（793 行） | 端到端全组合示例 |
| 6 | `audio2face-sdk/source/audio2face-core/executor_core.cpp:88` | BaseInit 装配现场 |

### 8.2 推荐阅读路线（三条，各 ~2h）

1. **应用集成线**（只想用）：docs/README.md → sample-a2e-executor → sample-a2f-executor → sample-a2f-a2e-executor——从高层 Bundle API 到低层逐件拼装，读完能写集成代码；
2. **几何内核线**（想懂 a2f）：audio2face.h → executor.h 三层接口 → executor_core.cpp BaseInit → executor_regression.cpp Execute:45 → multitrack_animator.h → blendshape_solver.h → bvls.h/admm.cu——沿 3.x 节主线走一遍；
3. **基座线**（想改 a2x 或做移植）：tensor.h 家族 → internal/unique_ptr.h → inference_engine.cpp → audio_accumulator.cpp → audio2x-sdk/CMakeLists.txt——张量/生命周期/TRT 抽象/打包四件套。

### 8.3 上手即懂的五个心智模型

1. **一切经接口**：你拿到的每个对象都是 `I*` 纯虚接口 + `Create*` 工厂 + `Destroy()`，没有 public 构造函数；
2. **门面=转发**：改行为去 *-core 找实现，门面 .cpp 永远一行透传（audio2face.cpp:25 注释）；
3. **累积器驱动流式**：低延迟不是回调魔法，是音频累积器的滑窗就绪语义（WindowProgress）在驱动推理节奏；
4. **双模型共享骨架**：回归/扩散只是 Execute 主循环与缓冲不同（GRU/噪声），BaseInit/动画器/回调全部共享；
5. **GPU/CPU 同构双路径**：blendshape 求解与单轨/多轨动画都存在 CPU 与 GPU 两套实现，公共接口不变，工厂参数切换。

### 8.4 二次开发热点

- 新增后处理算子：postprocess.cpp 八算子链尾部追加 + PostProcessParams 加参数（host 与 multitrack CUDA 双侧同步）；
- 新模型接入：parse_helper.h 加命名空间 + executor_*_core 继承 GeometryExecutorCoreBase；
- 新平台移植：cuda_fwd.h 模式（前置声明隔离 toolkit）+ 12 个 FindXxx 模块是移植面。

## 勘误与甄别记录（源码核实 > 图谱摘要）

1. **multitrack_animator_cuda.cu 内核数**：图谱摘要 10 个 → 源码 grep 实为 **9 个** `__global__`（:39-492 逐一列举）；
2. **samples 数量**：图谱摘要"六示例" → 实为 **5 个**（3 a2f + 2 a2e，main.cpp 逐一点名）；
3. **bvls.h 例程数**：图谱摘要"九个" → 实为 **8 个**自由函数（:29-78）；
4. **上游文件名笔误**：`interactive_executor_classifer.cpp` 少一个 i（应为 classifier）；
5. **上游注释笔误**：a2e `internal/interactive_executor_postprocess.h:54` 命名空间闭合注释误写 `IClassifierModel`，实际开的是 :29 `namespace IPostProcessModel`；
6. **上游宏笔误**：a2e `internal/logger.h:34-36` LOG_ERROR 块的 `#else` 空宏误写为 `LOG_INFO`（应为 LOG_ERROR 空实现）；
7. 图谱工程事实：CMakeLists 被 scanner 归 docs 类别已修正为 config；.cu 对 tree-sitter 全盲、节点全手工；audio2face.h 的 Create*/Read* 单行声明不建函数节点由文件级节点承载。

## 产物与元信息

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/Audio2Face-3D-SDK/.understand-anything/knowledge-graph.json`（726n/1312e/15 层/16 步 tour，validator 0 issues，fingerprints 267 文件 @ 1ca0f025）
- 批甄别笔记：同目录 `NOTES-DIGEST.md`（36 条）
- 覆盖：`~/ai/work4ai/讲透NVIDIA/Audio2Face-3D-SDK/deepwiki/`（前置轮产物）
