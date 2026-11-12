# 11 · CUDA 内核层总览——三库九个 .cu 的分工、thrust 优先与 26 个手写内核

## 角色定位

L12"CUDA 设备代码层"横跨三库共 **9 个生产 .cu**：audio2x-common 三个 + audio2face-sdk 五个（admm/animator_cuda/blendshape_solver_cuda/blendshape_solver_cuda_gpu/multitrack_animator_cuda）+ audio2emotion-sdk 一个（multitrack_postprocess_cuda）；6 个 tests 侧 .cu 不在此列。总纲是一条清晰分界线：**audio2x 公共层零手写内核（纯 thrust），业务层（a2f/a2e）才有 `__global__` 内核**——共 26 个。tree-sitter 对 .cu 全盲（NOTES batch-8），图谱内核与主机入口节点全部手工建立。

## 内部结构

**audio2x-common：thrust 即内核（0 个 `__global__`）**。三个 .cu 全是"主机函数 + thrust 算子"：`tensor_cuda.cu` 的 `FillOnDevice<Scalar>` 用 `thrust::fill_n(par_nosync.on(cudaStream), ...)`（tensor_cuda.cu:34-38），尾部四条显式模板实例化即四型张量 Fill 全部真身（tensor_cuda.cu:43-46）；`animated_tensor_cuda.cu` 的 `Lerp` 用 `thrust::transform` 配仿函数（animated_tensor_cuda.cu:52-66）；`audio_accumulator_cuda.cu` 的 `MultiplyOnDevice` 用 `thrust::transform`+`placeholders::_1`（audio_accumulator_cuda.cu:35-41，声明 internal/audio_accumulator_cuda.h:30）。甄别要点：**"GPU 加速"≠"手写内核"**——公共层只做元素级操作，thrust 自动生成内核省代码免维护。

**audio2face-sdk：23 个手写内核按"单轨旧线 vs 多轨新线"分布**。单轨旧线 `animator_cuda.cu`（8 内核）：插值器三件套 `InterpolatorInitDataKernel/UpdateKernel/UpdateKernelNoOp`（animator_cuda.cu:63,76,94），皮肤线 `AnimatorSkinGetYKernel/GetFaceMaskLowerKernel/ComposeKernelStep1/Step2`（155,164,193,175），舌头 `AnimatorTongueOffsetKernel`（212）；主机入口为类方法 `AnimatorSkin::Animate`（animator_cuda.cu:280）、`AnimatorTongue::Animate`（320）与自由函数 `AnimatorSkinCalculateFaceMaskLower`（231）。多轨新线 `multitrack_animator_cuda.cu`（9 内核）：`TracksSetKernel`（39）、`AnimatorSkinGetYKernelPacked`（51，packed 布局专版）、`AnimatorSkinEverything/ControlKernel`（115,169——整管线融合与仅控制流两档）、`AnimateTongueKernel`（231）、`ComputeJawTransformKernel`（266）、`ComputeEyesRotationEverything/ControlKernel`（468,492）；主机入口全列在 internal/multitrack_animator_cuda.h:30-103。求解器线：`admm.cu` 两内核 `ADMMupdateKernel/ClipKernel`（admm.cu:32,75）配 `admm_init/admm_update`（93,143）；`blendshape_solver_cuda.cu` 一个 `copyIndicesKernel`（37）；`blendshape_solver_cuda_gpu.cu` 三个工具内核（34,55,75）。

**audio2emotion-sdk：3 内核 + popcount 设备函数**。`multitrack_postprocess_cuda.cu`：`PostProcessSetKernel`（35）、通用 `PostProcessKernel`（63）、warp 级快路径 `PostProcessKernelLocal`（245）；`__device__ popcount`（49）用 `__popcll` 逐字累加把"轨道位图下标"映射到"激活轨紧凑数组下标"（52-55）——多轨稀疏性的核心翻译器。

## 外部连接

每库一对"纯声明头 + .cu 实现"：multitrack_postprocess_cuda.h:32,37 声明 `PostProcess_Set/PostProcess`；multitrack_animator_cuda.h 与 admm.h 同理（节点手工补建，NOTES batch-9）。错误回报统一 `CUDA_CHECK_ERROR(cudaGetLastError(), eCudaKernelError)`（animator_cuda.cu:130 等全仓 50+ 处）；thrust 失败用 `eCudaThrustError`（tensor_cuda.cu:42）。

## 数据流

以多轨后处理为例（multitrack_postprocess_cuda.cu:472-528 `PostProcess`）：位图先经 `PostProcess_Set` 上 GPU——**循环逐 64 位字启动单线程块小内核**（450-468，注释自述"类似 memcpy 但用内核避免 CPU/GPU 同步"）；主处理按 `useFastPath` 分流：情感尺寸 ≤ warp 走 `PostProcessKernelLocal`——每轨一线程、warp 内归约、`kReductionStartOffset=4` 压缩归约起点（483-507），否则 1024 线程/块通用 `PostProcessKernel`（509-527）。动画线同理：Everything 一步算完皮肤管线（multitrack_animator_cuda.cu:115），Control 只更新控制状态（169）。

## 设计决策

- **thrust/手写二分法**：可向量化内存操作（fill/lerp/multiply）下沉公共层交 thrust；有轨间交互或归约结构的算法才手写。
- **Everything/Control 双档内核**（multitrack_animator_cuda.cu:115 vs 169）：批处理全量一步到位，流式低延迟只走控制面——同一算法两种调度形态显式成对。
- **内核代替 memcpy 搬位图**（450-468）：保持纯异步，宁可启动 N 个小内核也不在主机侧等同步。
- **`par_nosync` 执行策略**（tensor_cuda.cu:35）：CUDA 12.0+ 无同步 thrust 派发，与全仓 async 风格一致。
- **单轨 animator_cuda 保留为 obsolete**：animator.h:27-29 注释明言单轨类已被多轨取代，旧内核线仍编译只为兼容。

## 新人提示

1. 图谱 L12 函数节点系手工补建——能搜到内核名但无函数体细节；改内核签名须同步 internal/*.h 声明头。
2. 排查"Unrecognized error"文本先看是不是 eCudaKernelError（09 篇勘误）——这层报错几乎全是它。
3. 读 `popcount`（multitrack_postprocess_cuda.cu:49-55）：位图是 uint64 数组，`trackIdx/64` 定位字、`%64` 定位位，前缀和只在激活轨累积。
4. thrust 函数在 Nsight 里内核名是自动生成的长名，别搜 `MultiplyOnDevice`。
