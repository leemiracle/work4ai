# NVIDIA DALI ONBOARDING（图谱驱动新人导览）

> 基于代码知识图谱（4002 节点 / 8966 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 1954 文件 @ commit `5fdb0b6a`）+ 源码逐锚核实撰写。版本锚：`VERSION`=2.4.0dev，`CMakeLists.txt:31` 声明 `project(DALI CUDA CXX C)`。全部行号锚均在本 commit 源码 grep 核实。

---

## 1. 项目定位：GPU 加速的数据加载库

DALI（Data Loading Library）是 NVIDIA 开源的**数据预处理全管线加速库**——把深度学习训练中"读文件→解码→增强→变换→送进 GPU"这条传统上由 CPU DataLoader 承担的流水线，整体搬到 CPU/GPU 混合并行执行。`README.rst:7` 的一句话定义："The NVIDIA Data Loading Library (DALI) is a GPU-accelerated library for data loading and processing"，覆盖图像/视频/音频三类模态。

解决的核心痛点是**输入管线瓶颈**：nvJPEG/NVDEC 硬件解码、CUDA kernel 增广直接在 GPU 上运行，避免 CPU 解码再 H2D 拷贝的往返；执行器把算子组织成 DAG 做多流并发调度（见第 5 节），使数据供给与训练计算重叠。

形态上是**C++ 核心多语言消费**的分层架构：

- **C++ 核心**（`dali/`）：类型系统、内存管理、kernel 框架、DAG 执行引擎、全部算子实现，1954 个分析文件中占绝对主体；
- **Python 主包**（`dali/python/nvidia/dali/`）：`pipeline.py`（2527 行）+ `fn`/`ops` 命名空间，是绝大多数用户入口；
- **五框架插件**：PyTorch/PaddlePaddle/JAX/TF/Triton/Numba 迭代器与自定义算子桥（`dali/python/nvidia/dali/plugin/`、`dali_tf_plugin/`）；
- **双层 C API**：一代 `include/dali/c_api.h` 与二代 `include/dali/dali.h`（互斥包含，`dali.h:19` 有编译期报错防混用）。

依赖管理上，DALI 把第三方库版本集中钉在根目录 `DALI_DEPS_VERSION`（当前 hash `6e60570a`），nvJPEG/libtiff/FFmpeg/nvImageCodec 等全部经 `cmake/Dependencies` 拉取；对 CUDA 运行时之外的动态库（cufile/nvcomp/nvml/cuvid）一律 dlopen 运行期解析（`dali/core/dynlink_cufile.inl`、`dali/util/nvml_wrap.h` 是范式样板），保证二进制可跨驱动环境分发。仓库还带 `skills/dali-dynamic-mode/SKILL.md`——NVIDIA 自己也在用 agent skill 协作开发此仓。

---

## 2. 架构总览：16 层依赖自底向上

图谱把全仓 4002 个节点组织成 16 层，本质是一条**从设备原语到框架生态**的依赖链，自底向上读就是正确的理解顺序：

| 层 | 名称 | 内容与代表锚点 |
|---|---|---|
| L01 | 工程配置与构建系统 | 根 CMake/`cmake/`、CI、conda 打包、`internal_tools/`；`document:CMakeLists.txt` 实为构建核心（scanner 误归 docs 的已知盲区） |
| L02 | 核心类型与设备原语 | `include/dali/core/` 安装头树：TensorShape/TensorView/Span/SmallVector、CUDA 流池、`static_switch.h:97` TYPE_SWITCH |
| L03 | 内存资源与 GDS 直存 | `dali/core/mm/` pmr 资源族 + `dali/util/cufile*`、`dali/operators/reader/gds_mem.h` |
| L04 | kernels 执行框架 | `dali/kernels/kernel.h:68`、KernelManager、dynamic_scratchpad、BlockSetup |
| L05 | kernels 图像处理家族 | `dali/kernels/imgproc/`：resample/convolution/color_manipulation/warp/structure |
| L06 | kernels 通用计算家族 | `dali/kernels/signal|audio|reduce|slice|transpose/`，signal 含 ARM NEON |
| L07 | pipeline DAG 执行引擎 | `dali/pipeline/`：Pipeline/op_graph2/CSE/executor 三代/executor2 流着色 |
| L08 | 数据读取与文件后端 | `dali/operators/reader/`（loader+parser）+ `dali/util/` 文件/云存储抽象 |
| L09 | 图像解码器族 | `dali/operators/imgcodec/` CRTP Backend + `decoder/cache/` 三策略缓存 |
| L10 | 图像处理算子族 | `dali/operators/image/`：resize/crop/color/convolution/remap/paste |
| L11 | 数学与表达式引擎 | `dali/operators/math/expressions/`：表达式树 + 100 个宏工厂实例 |
| L12 | 通用几何随机与注册 | generic/geometry/bbox/random + `dali/operators/operators.cc` 全算子注册入口 |
| L13 | 视频序列音频信号算子 | `dali/operators/video/`（三代解码）、`sequence/optical_flow`、`audio/`、`signal/` |
| L14 | Python 主包 | `dali/python/nvidia/dali/`：pipeline.py 2527 行、fn/ops、experimental/dynamic |
| L15 | AutoGraph vendored | `_autograph/`：TF AutoGraph 控制流转换器的 DALI 适配版（pyct AST 栈） |
| L16 | 框架插件与 C API | plugin/{pytorch,jax,paddle,tf,numba}、`dali/c_api`+`dali/c_api_2`、`include/` 头树 |

三条贯穿性设计原则：

1. **头文件即接口**：`include/dali/` 是对外安装树（core/util + dali.h/c_api.h/operators.h），`dali/` 内部实现与单测镜像对应——改公共类型先改安装头。
2. **双层泛型**：类型泛型靠 `TYPE_SWITCH`（`include/dali/core/static_switch.h:97`）/`VALUE_SWITCH`（`:131`）在编译期展开；设备泛型靠 CPU/GPUBackend 空标签类（`dali/pipeline/data/backend.h:29-31`）作模板参数驱动分配与拷贝分派。
3. **dlopen 隔离**：所有可选硬件能力（GDS、NVDEC、NVML、nvcomp）都是运行期探测加载，缺库不致命只降级，这是它能一个 wheel 通吃各代驱动的原因。

---

## 3. core 与内存：类型基石 + mm 资源族 + GDS 直存

### 3.1 类型层（被引用最多的层）

- **TensorShape**（`include/dali/core/tensor_shape.h`）：`struct TensorShape` 前置声明于 `:78`，基类 `TensorShapeBase` 在 `:89` 承载迭代器/operator[] 公共代码，动态形状特化 `TensorShape<DynamicDimensions>` 在 `:189`，其容器是 `DynamicTensorShapeContainer = SmallVector<int64_t, 6>`（`:183`）——6 维以内栈上零分配。静态形状是 `TensorShape<N>` 编译期定长。
- **TensorView**（`include/dali/core/tensor_view.h:98`）：`TensorView<Backend, DataType, ndim>` 零拷贝视图，是 kernel 层与算子层之间的数据通货；配套 `TensorListView` 管 batch。`backend_tags.h:23-28` 的 StorageGPU/StorageCPU/ComputeGPU/ComputeCPU 标签把"存哪"与"算哪"解耦。
- **SmallVector**（`include/dali/core/small_vector.h:86` SmallVectorBase / `:155` SmallVector）与 **span**（`include/dali/core/span.h:33` dynamic_extent）：全库热路径容器与传参基础件。
- **static_switch**（`include/dali/core/static_switch.h:97/:131`）：把运行时 typeid 整数展开成 `case` 分支的宏，DALI 泛型化的心脏，也是静态分析器盲区（宏展开结构 tree-sitter 零提取，图谱经人工补扫还原）。
- **convert**（`include/dali/core/convert.h:242`）提供饱和转换/浮点截断的全类型对特化；`geom/vec.h` 是几何代数 1-4 维向量（图像增广的数学底座）。

### 3.2 mm 内存资源族：pmr 风格三层组合

`dali/core/mm`（安装头在 `include/dali/core/mm`）复刻 libcu++ 的 `memory_resource` 语义（`include/dali/core/mm/cuda_memory_resource.h:176` memory_resource_base，纯虚 `do_allocate/do_deallocate` 在 `:244-245`，流序异步版本 `allocate_async` 在 `:302`），之上组合出资源层级：

- 上游裸资源：host/device/managed 各自的 malloc/cudaMalloc 封装；`memory_resource.h:46-57` 给出 `host_memory_resource`/`device_async_resource` 等别名总表；
- **pool_resource**（`include/dali/core/mm/pool_resource.h:90`）：块池化，减少 cudaMalloc 次数；
- **binning_resource**（`include/dali/core/mm/binning_resource.h:44` binning_resource_base / `:137` binning_resource）：按尺寸分桶路由到不同 pool，治小分配碎片；
- **async_pool_resource**（`include/dali/core/mm/async_pool.h:44`）：流序异步池，配合 `cuda_stream_view` 实现 stream-ordered 分配；
- **cuda_vm_resource**（`include/dali/core/mm/cuda_vm_resource.h:44`）：CUDA 虚拟内存（cuMemAddressReserve）粒度管理，供大缓冲按需 commit；
- 装配点在 **default_resources**（`include/dali/core/mm/default_resources.h:74` SetDefaultResource / `:141` PreallocateDeviceMemory / `:157` PreallocatePinnedMemory / `:125` ReleaseUnusedMemory）——`DALI_PREALLOCATE` 环境变量驱动的全局分配器就在这里挂接。

### 3.3 GDS 直存三处分布

GPU Direct Storage（绕过 CPU page cache 直读进显存）在仓内呈**三个层次**分布，读代码时别混淆：

1. **驱动绑定层**：`dali/core/dynlink_cufile.cc` + `.inl`（dlopen libcufile，`.inl` 单行模板是解析盲区）；
2. **文件流层**：`dali/util/cufile.h:28` `CUFileStream`（继承 FileStream，`ReadGPU` 在 `:50`、`ReadAtGPU` 在 `:58`）与回退实现 `dali/util/std_cufile.h:31` `StdCUFileStream`；`dali/util/odirect_file.h:27` `ODirectFileStream` 是 Linux O_DIRECT 预读变体；
3. **reader 侧消费层**：`dali/operators/reader/gds_mem.h` 的 GDSAllocator（`:37`）/GDSStagingBuffer（`:80`）/GDSStagingEngine（`:114`）管理已注册缓冲，`dali/operators/reader/loader/cufile_loader.h:39` `CUFileLoader` 把 CUFileStream 接进通用 FileLoader 模板——注释明示它必须持有 cuFileDriverHandle 的生命周期。

---

## 4. kernels 执行框架：算子之下的中立计算层

DALI 把"纯计算"从"算子调度"中剥离成 kernels 子系统：**算子层管 batch/参数/workspace，kernel 层只认 TensorView + 参数 + 上下文**，因而同一个 kernel 可被任意算子复用。

框架五件套：

- **Kernel 契约**（`dali/kernels/kernel.h:68` `struct Kernel`）：Setup（算需求）/Run（执行）两段式；
- **KernelRequirements**（`dali/kernels/kernel_req.h:33`）：Setup 的返回值，声明输出形状/dtype/暂存需求；
- **KernelContext**（`dali/kernels/context.h:199`）：内含 `gpu` 子上下文（`:201`，流/设备）与 `scratchpad` 指针（`:206`）；`dali/kernels/dynamic_scratchpad.h:133` DynamicScratchpad 按请求即时分配临时内存——`:123` 的注释警告 scratchpad 不得做成员持有，否则是"不可检测的内存泄漏"；
- **KernelManager**（`dali/kernels/kernel_manager.h`）：按 (类型×设备) 键在编译期实例化并缓存 kernel，是 kernel 与算子层的桥梁；
- **BlockSetup**（`dali/kernels/common/block_setup.h:91`，BlockDesc `:32`、SetupBlocks `:130`）：GPU 图像核共享的输出块划分器，喂给 CUDA grid。

### 案例深读：resample 重采样族（RandomResizedCrop 的终点）

这是理解"CPU/GPU 双实现 + 组合"范式的最佳标本，目录 `dali/kernels/imgproc/resample/`：

- 对外门面只有两个别名：`dali/kernels/imgproc/resample.h:28` `ResampleGPU`（Impl 指向 SeparableResamplingFilter）与 `resample_cpu.h:26` `ResampleCPU`——算子侧只见门面不见实现；
- **参数与 Setup**：`params.h` 定义 ResamplingParams（每维 scale/bias），`resampling_setup.h:110` SeparableResamplingSetup / `:161` BatchResamplingSetup 计算输出几何；
- **GPU 实现**：`resampling_impl.cuh` 三个轴向的 device 函数族——`ResampleHorz_Channels`（`:59`）、`ResampleVert_Channels`（`:288`）、`ResampleHorz/Vert`（`:622`/`:659`），由 `resampling_batch.cu` 的 kernel 拉起；
- **CPU 实现**：`resampling_impl_cpu.h:89` SIMD_vert_resample_impl / `:127` SIMD_horz_resample_impl，用编译器 SIMD 手写滤波循环；
- **滤波器窗**：`resampling_windows.h` 定义窗函数族——Gaussian（`:26`）、Triangular（`:35`）、Lanczos/Lanczos3（`:44`/`:50`）、Cubic（`:54`），FilterWindow 结构在 `:67`；`resampling_filters.cuh:70` ResamplingFilters 是预生成系数表的单例；`separable.h:30` SeparableResamplingFilter 把逐维滤波组合成 N 维重采样。

### 双实现的三个工程细节（易踩坑）

1. `.cuh` 是 CUDA 头：`resampling_filters.cuh` 全部函数 `__host__ __device__` 双标记，非 CUDACC 编译时回退 cmath/algorithm——这是 kernels 头能同时进 .cc 与 .cu 的机制；
2. **模板头是静态分析盲区**：`resample_cpu.h` 只有一行 using 别名、`expression_impl_factory.h` 全宏展开，tree-sitter 提取为空，图谱结构靠人工补扫；读这类文件要看包含点还原语义；
3. 家族横向对照：convolution 的 `CyclicWindowWrapper`（`dali/kernels/imgproc/convolution/convolution_cpu.h:101`）环形边界窗口、color_space_conversion 用 constexpr 编译期展开系数表（`color_space_conversion_impl.h:41` scale_factor）、connected_components 用 disjoint_set 并查集合并标签（`structure/connected_components.h:117`，LabelSlice 递归按 ndim 分派 `:89`）、reduce 以 StridedTensor 为归约基类（`reduce/reduce_cpu.h:74`）、signal 的 CPU 重采样在 ARM 上走 NEON 向量（`dali/kernels/signal/resampling_cpu.cc:20` `__ARM_NEON` / `:57` vsetq_f32）。`dali/kernels/dummy.cu` 文件头注释自述其存在理由：老 CMake 用 Clang 链接 .cu，此空文件强制走 NVCC——编译系统的历史包袱有明确锚点。

---

## 5. pipeline DAG 引擎：从用户代码到流着色调度

### 5.1 建图（Pipeline → OpGraph）

`dali/pipeline/pipeline.h:62` `class Pipeline` 是用户 API 与执行的中枢：构造参数含 `prefetch_queue_depth`（`:77`），`Build`（`:296`）触发图装配。`dali/pipeline/pipeline.cc:377` AddOperatorImpl 处理算子实例化与常量提升；Build 后在 `:620`/`:637` 调 AddMakeContiguousNode **自动插入 MakeContiguous 节点**（`:802` 直接 OpSpec("MakeContiguous") 构造，PrepareMakeContiguousNode 在 `:1133`）——当下游设备与上游输出布局不一致时，用户没写的拷贝算子由建图器补上。

图表示是 `dali/pipeline/graph/op_graph2.h:121` `OpGraph`（Builder 模式 `:244`），优化包括 **CSE 公共子图消除**（`graph/cse.h:84` EliminateCommonSubgraphs）与 graph2dot 可视化。管线可序列化为 protobuf（`dali/pipeline/proto/dali.proto`），支持跨进程重建；checkpoint 亦有 protobuf 通道（`dali/pipeline/pipeline.h:332` SerializeToProtobuf）。

### 5.2 算子框架（自描述体系）

- `dali/pipeline/operator/operator.h`：`Run`（`:98`）→ `RunImpl`（`:123` 纯虚）两段，中间夹 metadata 校验；SaveState/RestoreState（`:186`/`:197`）支撑随机算子的 checkpoint/恢复（epoch 续训必需）；无状态算子经 StatelessOperator 跳过 checkpoint。
- `dali/pipeline/operator/op_schema.h:154` OpSchema 是**算子自描述核心**：NumInput（`:352` 定数 / `:355` 区间）、AddArg（`:446`）、OutputDTypeFn（`:336`）与 CalculateOutputs 等**供前端做动态类型推断**——Python 侧 `fn.decoders.image(...)` 能预先知道输出形状，靠的就是 schema 回调而非运行。
- 参数传递走类型擦除的 Argument：`dali/pipeline/operator/argument.h:52` Value / `:73` ValueInst / `:158` ArgumentInst，配合 INSTANTIATE 宏覆盖全类型。
- 运行期数据是 `dali/pipeline/data/tensor.h:43` Tensor 与 TensorList（`tensor_list.h:658` 内嵌 State 状态机管理分配/共享；Tensor↔TensorList 经 share/views 互转）；workspace 体系在 `dali/pipeline/workspace/workspace.h`：ArgumentWorkspace（`:51`）→ WorkspaceBase（`:138`）→ 批级 `Workspace : WorkspaceBase<TensorList>`（`:766`），另有逐样本 SampleWorkspace 变体。
- 类型注册表 `dali/pipeline/data/types.h:273` TypeTable 单例（GetTypeId 模板静态注册 `:278`，RegisterType `:315`），用户可注册自定义类型。

### 5.3 执行器三代与流着色

- 接口：`dali/pipeline/executor/executor.h:52-53` 纯虚 `Run()/Prefetch()`；
- 二代：pipelined_executor（预取流水线）+ async_separated_pipelined_executor（CPU/GPU 阶段分离多线程）；
- **三代 executor2**（`dali/pipeline/executor/executor2/`）：`exec2.cc:69` 用 PIMPL 把调度逻辑收进 `Executor2::Impl`；`exec_graph_lowering.cc:25` `ExecGraph::Lower` 把定义图降级成可执行图；**杀手锏是 `stream_assignment.h` 把 CUDA 流分配建模为图着色**——Single 策略（`:70`）、PerBackend（`:105`）、PerOperator（`:182`）三档，无依赖算子着同色共用流、有依赖分色天然串行，这是 GPU 管线执行器的教科书设计。
- 调度策略相关还有 workspace_policy.h / queue_policy.h（L07 层的 workspace/队列策略节点群）。

---

## 6. operators 六大算子家族

`dali/operators/` 下 21 个子目录，`operators.cc` 是全算子注册总入口。注册范式统一：`.cc` 内 `DALI_SCHEMA(名)` 声明参数 schema + `DALI_REGISTER_OPERATOR` 绑定 CPU/GPU/Mixed 模板实例（范式标本 `dali/operators/generic/reduce/reduce.cc:25` 起；`imgcodec/mixed_decoder.cc:41-42` 一类对两 schema）。六大家族分述：

### 6.1 解码器族（imgcodec + cache）

`dali/operators/imgcodec/image_decoder.h:131` `ImageDecoder` 是统一解码入口：CRTP 式 Backend 模板 + **逐样本 SampleState**（`:153`，`:635`/`:915` 以 unique_ptr 向量持有），host/mixed/ROI 三种设备策略各是一个 Backend 特化；`mixed_decoder.cc:21` MixedDecoder 是默认 `fn.decoders.image(device="mixed")` 后端——CPU 读码流、GPU 解码的混合流。底层对接 nvImageCodec。解码缓存三策略在 `dali/operators/decoder/cache/`：blob（`image_cache_blob.h:28` 整块缓存）/largest（`image_cache_largest.h:28` 只缓存大图）/thresholded，经 `image_cache_factory.h:26` 工厂选择，`cached_decoder_impl.h:29` CachedDecoderImpl 组合"缓存命中直拷+未命中解码回填"。

### 6.2 图像增强家族（image/）

`dali/operators/image/` 是增广主力：Resize（`resize/resize.h:34`，ResizeBase 用 extern template 控制编译膨胀 `resize_base.h:121`）；裁剪族以 SliceBase（`dali/operators/generic/slice/slice_base.h:44`）与 CropAttr（`crop/crop_attr.h:34`）为基；色彩 BrightnessContrast（`color/brightness_contrast.h:58`，SequenceOperator 支持逐帧参数）；GaussianBlur（`convolution/gaussian_blur.h:42`，GPU 侧按 dtype 一型一 .cu 文件实例化 `gaussian_blur_gpu/gaussian_blur_impl_{f32,i8,...}.cu` 控制编译时长）；融合典范是 new_crop_mirror_normalize.cu:109——按 output_layout/dtype 在 SliceHwc2HwcChwNormalizeGPU 等三条融合核路径中动态选择，一核完成切片+翻转+归一化+HWC→CHW；remap/paste/clahe/形态学构成外围。

### 6.3 数学表达式引擎（math/expressions）

DALI 允许直接写 Python 算术表达式（`(img - mean) / std`）驱动 C++ 执行：`arithmetic.h:313` ArithmeticGenericOp 是表达式算子，`:152`/`:169` CreateExecutionTasks 把表达式树拓扑排序成 ExprImplTask 序列（`:386` exec_order_ + `:389` ExprImplCache）。类型推导是 `arithmetic_meta.h`：`:298` binary_op_promotion 两两类型提升表、`:408` arithm_meta 主模板。算子工厂的极致自动化在 `expression_factory_instances/`：**100 个文件 = 49 个 CPU .cc + 49 个 GPU .cu 实例**（如 `expression_factory_abs.cc:22` 整文件一条 `IMPLEMENT_OP_FACTORY_CPU_UNARY(abs);`），宏定义集中在 `dali/operators/math/expressions/expression_factory_instances/expression_impl_factory.h:160-186` 五个变体（注意：`dali/operators/math/expressions/` 下另有同名头，992 行的真宏定义在此 instances 目录这份）——纯模板头，静态分析零提取，结构靠宏上下文还原（图谱人工补扫钉版）。

### 6.4 几何与随机家族（geometry/ + random/）

几何：`affine_transforms/transform_base_op.h:49` TransformBaseOp 是 CRTP 基类，crop/rotation/scale/shear/combine 各文件产出变换矩阵，矩阵喂给 kernels/imgproc/warp 完成采样——"先算矩阵再 warp"两段式。随机：`dali/operators/random/rng_base.h:70` `rng::OperatorWithRng` 是 CPU/GPU 随机分布算子统一基类——**种子与 checkpoint 序列化由框架管，算子只定义分布函数**；GPU 侧 `rng_base_gpu.cuh:128` `RNGKernel` 拉起逐样本核（noise/normal/uniform/coin_flip 均此类）。bbox/segmentation/ssd 子族让框标注与图像增广同步变换。

### 6.5 视频家族：NVDEC 三代（video/）

- **一代 CUVID**：`video/legacy/reader/video_reader_op.h:48` VideoReader（`fn.readers.video` 原型），解码器在 `legacy/reader/nvdecoder/nvdecoder.h:98-100` 以 handle_sequence/handle_decode/handle_display 三回调对接 CUVID 解析器（SDK 头 vendored 于 `video/dynlink_nvcuvid/cuviddec.h`，MIT）；
- **二代 mixed**：`video/decoder/video_decoder_base.h:38` `template <typename Backend, typename FramesDecoderImpl>`——解码与读取分离，CPU/GPU 由模板参数选择；
- **三代统一**：`video/frames_decoder_base.h` 定义抽象基类（ReadNextFrame `:256`、SeekFrame `:263`、Flush `:355`、BuildIndex `:374` 全虚函数），`frames_decoder_cpu.h:25` FramesDecoderCpu（FFmpeg）与 `frames_decoder_gpu.h:127` FramesDecoderGpu（NVDEC，`:72` NVDECLease 租约管理解码器缓存）成对实现；`video/input/video_input.h` 是新一代输入算子。三代并存是真实的演进地层，新代码勿再入 legacy。
- 周边谱系：序列处理 optical_flow（`sequence/optical_flow/optical_flow.h:56`，vendored nvOpticalFlow SDK 头）、per_frame/element_extract；音频与信号见 6.6。

### 6.6 音频与信号家族（audio/ + signal/）

`dali/operators/audio/resample.h:31` ResampleBase（复用 kernels/signal 重采样核）、mfcc/mel_scale（`audio/mfcc/mfcc.h`）与 `dali/operators/signal/fft/`（FFT/decibel 谱系算子）构成音频特征管线；底层核在 L06 层 `dali/kernels/signal|audio/`。reader 侧的接入层在 L08：`dali/operators/reader/reader_op.h:57` `DataReader` 是约 500 行模板重基类，**把 loader 生命周期（PrefetchWorker 线程 `:142`、StartPrefetchThread `:159`）与管线执行模型（prefetch/epoch）解耦**——loader 家族（file_loader.h:45 FileLoader、coco/webdataset/numpy/mxnet/caffe/tfrecord/nemo 等）只需实现"读一个样本"，线程/epoch/张量组装全由基类与 `dali/util` 文件后端（FileStream、mmap、S3/GCS 云文件系统）承担。

---

## 7. Python 生态：nvidia.dali 主包 + 五框架插件 + AutoGraph

### 7.1 主包结构（dali/python/nvidia/dali/）

- **pipeline.py**（2527 行）：`class Pipeline`（`:97`）+ `run`（`:1515`）+ `pipeline_def` 装饰器（`:2210`，条件编译出三个重载 `:2179`/`:2186`）。`@pipeline_def` 装饰的 Python 函数（图定义函数）在调用时被转换为 Pipeline 工厂——函数体里的 `fn.*` 调用只产生 DataNode 符号，并不执行。
- **ops 与 fn 双命名空间**：`ops/__init__.py:722` `_load_ops` 在**模块导入期**（`:898` 直接调用）动态发现并绑定全部 C++ 扩展算子；`fn/__init__.py:31` `_to_snake_case` 把 PascalCase 类名转 snake_case，`:66`/`:115` `_wrap_op_fn/_wrap_op` 生成带 docstring 的包装——用户写 `fn.random_resized_crop`，底层是 `ops.RandomResizedCrop`。
- **张量类型**：`tensors.py:16` 从 backend 再导出 TensorCPU/TensorGPU/TensorListCPU/TensorListGPU 四类；真正的类定义在 C++ 扩展 `backend_impl` 中（`backend.py:15` import from nvidia.dali.backend_impl，`:32` star re-export），`.pyi` 存根供类型检查器。C++ 侧 `dali/python/backend_impl.cc` 分区注册：ExposeTensor（`:683`）、ExposeTensorListCPU（`:1542`）、ExposeTesorListGPU（`:1879`——**单 s 拼写错误的历史命名**，`:2146` ExposeTensorList 汇聚调用处原样引用）。
- **math.py**：全部算术包装是 6-7 行薄封装，共享 `_arithm_op`（`:21`；sqrt 例 `:35`）——对接第 6.3 节表达式引擎。
- **external_source.py:312** ExternalSource 的 `__call__`（`:700`）对 source 参数做**鸭子类型三模式判定**：callable（接受 SampleInfo/BatchInfo）/可迭代 cycle/None，docstring（`:523` 起）详列 batch=True/False 下的合法形态。
- **experimental/dynamic**：正在发展的定义式新 API（capture/checkpoint 机制）+ torchvision 兼容层；**NVIDIA 已为它写了 agent skill**（仓根 `skills/dali-dynamic-mode/SKILL.md`）。

### 7.2 vendored AutoGraph（_autograph/）

`pipeline_def` 的 if/while/for 之所以能在图定义函数里工作，靠的是从 TensorFlow vendored 的 AutoGraph（L15 层整层）：`pyct/` 是完整 AST 工具链（parser/cfg/静态分析 liveness·reaching_definitions/缓存），`converters/` 做控制流→符号图转换，`impl/api.py`+`impl/conversion.py` 是转换入口，`operators/` 做 Python 运算符的符号替换。`pipeline_def(enable_conditionals=True)`（`dali/python/nvidia/dali/pipeline.py:2210`）即开启此通道。改动这部分要意识到它**上游是 TF 的代码**，修 bug 前先看 TF 侧是否已修。

### 7.3 五框架插件（plugin/ + dali_tf_plugin/）

统一入口 `plugin/base_iterator.py` 之上各框架出迭代器：PyTorch `plugin/pytorch/__init__.py:43` DALIGenericIterator（`:285` DALIClassificationIterator 便捷类，支持 LastBatchPolicy）；Paddle `plugin/paddle.py:145`（`:401` 同名分类迭代器）；JAX `plugin/jax/iterator.py:409` `data_iterator` 装饰器（impl `:278`），走 `jax.Array` 零拷贝；TF 走独立 `dali_tf_plugin/`（自定义算子 daliop + Dataset 接入，`plugin/tf.py:433` _DALIDatasetV2/`:840` DALIDataset 两代）；Numba 插件（`plugin/numba/__init__.py:67` address_as_void_pointer 类型桥）让用户 numba jit 函数直接成为管线算子（C++ 侧 `dali/operators/numba_function/numba_func.cc` 与 `python_function/python_function.cc` 同型）。C++ 插件加载器 `dali/plugin/plugin_manager.cc:26` LoadLibrary：dlopen + RTLD_LAZY（`:28-31`），allow_fail 容缺。

---

## 8. 新人上手：公共头树、C API 双代与阅读路线

### 8.1 include/dali 公共头树（C++ 用户消费面）

`include/dali/` 是安装头树，五大件：`core/`（L02/L03 全部公共类型与 mm）、`util/`（FileStream 等文件抽象的公共部分）、`operators.h`（算子注册宏，`:67` 收束）、`dali.h`（**新 C API**，1560 行）与 `c_api.h`（**旧 C API**，846 行）。内部实现与测试在 `dali/` 镜像目录——找实现时把 `include/dali/core/x.h` 映射到 `dali/core/x.cc` 即可。

### 8.2 C API 双代并存

- **一代** `include/dali/c_api.h:135` `daliCreatePipeline`（`:163`/`:187` 已演化出 2/3 号变体）：句柄型 API，`dali/c_api/c_api.cc:124` 起 handle→`std::shared_ptr<Pipeline>` 映射表统一翻译，异常捕获转错误码——为 TF 时代插件而生；
- **二代** `include/dali/dali.h`（c_api_2）：builder 风格——`:429` `daliPipelineCreate` 建空管线、`:473` `daliPipelineAddOperator` 逐步加算子、`:486` `daliPipelineSetOutputs`、配套 daliPipelineParams_t（`:332`）/IODesc（`:353`）描述结构。两代**互斥包含**：`dali.h:19` 显式 `#error` 防同翻译单元混用。C++ 内部实现 `dali/c_api_2/pipeline.h:27` `_DALIPipeline` 持有真 Pipeline，`:43` Build；checkpoint/outputs 在同目录 checkpoint.h/pipeline_outputs.h。新集成一律用二代。

### 8.3 推荐阅读路线（图谱 16 步 tour 的精华版）

1. **Day 1 地基**：`README.rst` → `dali/pipeline/pipeline.h:62`（Pipeline API 全貌）→ `include/dali/core/tensor_shape.h:89`/`tensor_view.h:98`（一切数据的表示）→ 跑通官方 quick start；
2. **Day 2 内存**：`include/dali/core/mm/memory_resource.h:46` 别名总表 → pool/binning/async 三资源 → `default_resources.h:141` 预分配入口 → GDS 三层（`dali/util/cufile.h:28` → `gds_mem.h:37` → `cufile_loader.h:39`）；
3. **Day 3 kernel 范式**：`dali/kernels/kernel.h:68` 契约 → resample 全家（第 4.节案例）→ 任选一个 CPU 算子（如 crop）从 op 读到 kernel；
4. **Day 4 执行引擎**：`dali/pipeline/pipeline.cc:377` 建图与 MakeContiguous 自动插入（`:802`）→ `op_graph2.h:121` → `executor2/stream_assignment.h:70` 流着色三策略 → 用 `DALI_LOG_PIPELINE_GRAPH` 类调试开关对照 graph2dot 输出；
5. **Day 5 算子广度**：六大族各挑代表（mixed_decoder / resize / arithmetic / affine / frames_decoder_gpu / rng_base）通读，注意 6.3 的宏工厂与 6.5 的三代地层；
6. **Day 6 Python 面**：`pipeline_def`（`dali/python/nvidia/dali/pipeline.py:2210`）→ `fn/__init__.py:31` 命名转换 → `_autograph/impl/` → 任一插件迭代器（推荐 pytorch）。

### 8.4 实操提示（勘误与坑）

- 算子注册的 ground truth 是各 `.cc` 的 DALI_SCHEMA/DALI_REGISTER_OPERATOR 与 `dali/operators/operators.cc`，文档滞后时以 schema 为准；
- `resize_base.h:121` 的 extern template + `.cc` 尾部显式实例化、gaussian_blur 一型一 .cu、`dali/kernels/dummy.cu` 强制 NVCC——三个编译膨胀控制点，改模板前先懂它们；
- 查拼写历史命名（ExposeTesorListGPU）与 vendored 代码（half.hpp、AutoGraph、cuviddec.h）时，别按 DALI 风格"修正"它们；
- 进阶资料：`STYLE_GUIDE.md`、`CONTRIBUTING.md`、`guided_contribution_tutorial.md`、Doxyfile（生成 API 文档）；版本钉版看 `VERSION` 与 `DALI_DEPS_VERSION`。

---

## 附：本导览的图谱底账

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/DALI/.understand-anything/knowledge-graph.json`（4002 节点 / 8966 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 1954 文件）
- 源码 commit：`5fdb0b6a`（analyzedAt 2026-11-07）；版本 2.4.0dev
- 输入：`onboard-input.json`（16 层+16 步 tour+30 hubs）+ `NOTES-DIGEST.md`（155 条批阶段甄别笔记）+ 源码逐锚 grep 核实
- 姊妹产物：`../deepwiki/`（DeepWiki 全量页）；本文件为 understand 流水线 onboard 阶段产物
