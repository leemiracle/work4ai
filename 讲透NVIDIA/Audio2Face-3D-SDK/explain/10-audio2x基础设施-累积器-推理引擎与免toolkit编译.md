# 10 · audio2x 基础设施——三种累积器、TensorRT 引擎抽象与 cuda_fwd.h 枢纽

## 角色定位

audio2x-common 除张量家族外的另一半是**运行时基座**：三个累积器管理流式时序数据，`inference_engine.h` 把 TensorRT 包成纯虚接口，`cuda_fwd.h` 一行前向声明让公共头免装 CUDA toolkit 即可编译，error/logging 两件套收口诊断。这是 L04"实现基座"层主体，三 SDK 执行器全踩在它上面。

## 内部结构

**累积器三级**。基座 `IFloatAccumulator`（float_accumulator.h:36-86）：`timestamp_t=int64_t` 允许负时间戳 lookback（float_accumulator.h:40）；`Accumulate` 宿主/设备双版本（45-46，GPU async）、`Close()`（49）、`Read(destination, absoluteStartSample, cudaStream)`（55-56）、`DropSamplesBefore`（63，归还缓冲给 tensor pool）、计数器族（67-79）。`IAudioAccumulator` 直接继承它并**用 final 模板方法收窄 Read**：无 inputStrength 的 `Read` 被 final 实现为转发到带 inputStrength 的虚版本（audio_accumulator.h:41-45），子类只实现四参版（audio_accumulator.h:35-37）——NVI 惯用法。`IEmotionAccumulator` 独立成接口（emotion_accumulator.h:20-83）：情感向量必须**严格单调递增时间戳**追加（注释"strictly monotonically increasing"），`Accumulate` 双内存版本、`Read` 插值读取。三者皆声明"thread-safe except Destroy()"（float_accumulator.h:31-33 等）。

**TRT 引擎抽象**（inference_engine.h）三接口：`IBufferBindingsDescription` 元数据（inference_engine.h:34-64，`IOType`:37 与 `DimensionType{UNKNOWN,FIXED,BATCH,DYNAMIC}`:43 两枚举撑起动态形状描述）；`IBufferBindings` 运行期缓冲（inference_engine.h:69-102，Set/Get 吃 void 视图 + `Set/GetDynamicDimension`:89,95）；`IInferenceEngine` 五步生命周期 `Init→GetMaxBatchSize→CheckBindings→BindBuffers→Run(cudaStream)`（inference_engine.h:110-125，Run 是 GPU Async）。实现层 `internal/inference_engine.h`：`InferenceEngine` 持 `nvinfer1::IRuntime/ICudaEngine/IExecutionContext` 三指针（internal/inference_engine.h:195-197），`NvInfer.h` 引入被诊断宏包裹压警告（26-38）；另有一套 constexpr 排序/比较工具（`CompareCStr`:84、`CompareBindingDescription`:104、`IsSorted`:110、`GetInputCount`:119），并 `#warning` 自嘲"C++20 可用后这些可简化"（75-81）。`BufferBindings` 动态维度存 `vector<unordered_map<size_t,size_t>>`（internal/inference_engine.h:178）。

**cuda_fwd.h 枢纽**（cuda_fwd.h:24）：一行 `typedef struct CUstream_st *cudaStream_t;` 复刻 CUDA Runtime 真声明，公共接口头不 include 任何 CUDA 头——**下游免装 CUDA toolkit 即可编译**，只有链接实现库才需要真符号。

**诊断两件套**：`error.h` 定义分段枚举（eCuda*=20 起、eInfer*=40 起、eNotInitialized=60、eIO=80、eExecutor=100）+ `std::is_error_code_enum` 特化（error.h 末尾）允许枚举隐式构造 error_code；`internal/logger.h` 是编译期日志开关：`AUDIO2X_LOG_LEVEL` 三档宏（logger.h:25-27），`A2X_BASE_LOG_ERROR/INFO/DEBUG` 按档位定义为流输出或空（logger.h:34-50），SDK 专属宏固定 category 字符串（logger.h:53-55），构建侧 CMake 统一压到 1（error only）。TRT 日志经 `TRTLogger::log` 按严重度映射到三档宏（logger_trt.cpp:26-42），全局单例 `trtLogger`（logger_trt.cpp:44）。

## 外部连接

上游：TensorRT（nvinfer1）、CUDA Runtime（internal/cuda_stream 与 tensor_pool）。下游：a2f/a2e 执行器把累积器当输入源（`EmotionExecutorBase::TrackData` 直存两累积器指针，internal/executor.h:101-106）；parse_helper 的 Bundle `InitBase` 成对 new 两种累积器（internal/parse_helper.h:338-339）；nvtx_trace.h 的 `NVTX_TRACE(name)` RAII 域宏（nvtx_trace.h:36-44，USE_NVTX 开关）挂在各执行路径做 profile。

## 数据流

流式主循环：音频块 `Accumulate(HostTensorFloatConstView, stream)` → tensor pool 扩容/复用 → 执行器按帧 `Read(view, startSample, 1.0f, stream)` 取窗 → TRT `BindBuffers+Run` → 情感结果经 `EmotionBinder` 回灌 EmotionAccumulator → 动画层按时间戳 `Read` 插值。`DropSamplesBefore/DropEmotionsBefore` 在安全窗口后回收显存，形成环形供给。

## 设计决策

- **final 模板方法**（audio_accumulator.h:41-45）锁死默认 inputStrength=1.0，消除子类遗漏默认值。
- **接口/实现硬隔离 + 免 toolkit 编译**：公共头零 CUDA/TRT include，重度依赖全在 internal/——消费方集成成本最低。
- **error_code 全程无异常**：连 TRT 回调都 noexcept（logger_trt.cpp:25-26）。
- **日志零运行时开销**：档位预处理期裁剪，发布版宏为空。
- **is_error_code_enum 特化**：可直接 `return ErrorCode::eXxx;` 隐式成 error_code。

## 新人提示

1. 读情感插值行为要从 `EmotionAccumulator` 实现入手，接口注释只说 interpolates；时间戳重复/乱序是未定义契约，先查上游推流逻辑。
2. cuda_fwd.h 的前向声明**不能**与真 CUDA 头混用于同一段声明周期冲突场景——实现 .cpp 内应 include 真 `cuda_runtime.h` 而非 fwd。
3. `InferenceEngine::GetMaxBatchSize` 返回 int64 且 -1 表示失败（inference_engine.h:114-115），不是 error_code 路径，注意判别。
4. `internal/inference_engine.h:75-81` 的 #warning 在 C++20 模式会刷屏，属上游已知自嘲，非构建故障。
