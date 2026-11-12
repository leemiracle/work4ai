# 04 · animator 单轨到多轨演进——废弃自证、位图调度与 CUDA 内核族

> 锚点前缀：仓库根 `audio2face-sdk/`。行号锚全部从源码核实。内核计数为源码实测（任务书口径"10 内核"，实测 9 个 `__global__` + 2 个 `__device__` 辅助 + 8 个主机入口，以下以实测为准）。

## 一、角色定位

animator 家族把神经网络推理输出变成可渲染的面部资产：PCA 重建、皮肤变形、舌头、下颌（牙齿）、眼球扫视五类。它的演进故事写在文件头注释里——animator.h:27-30 明示："单轨 animator 已废弃（obsolete），被多轨 animator 取代；多轨提供更高效的批处理，并把部分 CPU 实现替换为 GPU 实现"。单轨 animator.h（405 行纯虚接口）与 animator.cpp（935 行）仍完整保留并继续导出（CreateAnimatorSkin 等工厂还在 audio2face.h:44-52），但执行器链只消费多轨版本——**废弃靠注释自证、代码不清除**，是这份 SDK 的兼容策略。

## 二、内部结构

单轨接口四件套共享同一骨架：参数结构体（AnimatorSkinParams 11 字段 animator.h:35-47、Tongue/Teeth/Eyes :49-72）、`RangeConfig<T>` 默认/最小/最大三元组（:75-93）、HostData/DeviceData 双视图、逐字段 setter（IAnimatorSkin 的 11 个 Set\* :169-191）。关键差异在**内存与计算位置**：IAnimatorTeeth 与 IAnimatorEyes 只有 HostData（animator.h:276-284、:327-330），ComputeJawTransform/ComputeEyesRotation 签名吃**主机张量**（:314-315、:378-380）——这两类单轨实现是 CPU 计算（animator.cpp:580、:798-800 均为 host 视图），还带 SetFrameIndex/IncrementLiveTime 的逐帧游标（:374-376）。多轨版本 multitrack_animator.h（265 行）五接口全部重写为批处理语义：Animate 吃 `DeviceTensorFloatView + TensorBatchInfo`（IMultiTrackAnimatorSkin::Animate multitrack_animator.h:104-107）、参数按轨存取（:88-92）、新增 `SetActiveTracks(activeTracks, size)` 位图协议（:97-101，注释说明其保证"批内取数正确 + 不活跃轨状态不被更新 + 提供优化机会"），teeth/eyes 全部落到设备张量（ComputeJawTransform :201-205、ComputeEyesRotation :251-255），眼睛的逐帧游标改为按轨 `SetLiveTime`（:249）。

## 三、外部连接

执行器是唯一上游消费者：回归链批量后处理按四类动画器逐段调度（executor_regression.cpp:123-211），并把 `_executedTracks` 位图直接喂给 SetActiveTracks（:131、:212 后同）。下游设备代码集中在 multitrack_animator_cuda.cu（755 行）：9 个 `__global__` 内核——TracksSetKernel(:39)、AnimatorSkinGetYKernelPacked(:51)、AnimatorSkinGetFaceMaskLowerKernel(:60)、AnimatorSkinEverythingKernel(:115)、AnimatorSkinControlKernel(:169)、AnimateTongueKernel(:231)、ComputeJawTransformKernel(:266)、ComputeEyesRotationEverythingKernel(:468)、ComputeEyesRotationControlKernel(:492)，加 `__device__` 辅助 ComputeSkinPostProcessing(:72) 与 ComputeEyesRotation(:386)；主机入口 8 个在 `nva2f::cuda` 命名空间（:520-755），声明于 internal/multitrack_animator_cuda.h（Tracks_Set、AnimateSkin_Everything/Control、ComputeEyesRotation_Everything/Control 等）。

## 四、数据流

多轨皮肤动画的调度是演进精髓（multitrack_animator.cpp:297-374）：Animate 先校验 stride×轨数=张量尺寸（:305-316），然后**双条件分支**——`checkAllSet(_activeTracks)` 且 `checkAllSet(_initializedTracks)` 全真时走 `AnimateSkin_Everything` 快路径（:323-341，无位图判断开销）；否则先把两张主机位图 `Tracks_Set` 上传（:343-350）再走 `AnimateSkin_Control` 慢路径（:351-366），事后把活跃位并进已初始化位 `_initializedTracks[i] |= _activeTracks[i]`（:368-370）。首次执行时初始化位为空、必走 Control 路径以建立插值状态；稳态后全部命中 Everything 路径。眼睛的 liveTime 由 GPU 端维护：分配清零（:817-818）、Reset 归零（:859）、SetLiveTime 写入 `liveTime * 30.0f`（:888，30 帧/秒换算内嵌在宿主代码）、ComputeEyesRotation 双路径分流（:894-950）。

## 五、设计决策

①**Everything/Control 成对内核**是典型的"全集快路径 + 位图守卫慢路径"两分法，皮肤与眼睛两族同构复用（115/169、468/492 两对内核），无状态部件（PCA、tongue、teeth）不需要对——multitrack_animator.h:51-53、:147-149、:197-199 的注释明说"无状态、每次全算"。②**单轨不删**：公共工厂照常导出保 ABI，注释声明废弃转移维护成本，历史 sample 仍可用。③**参数下发走两份**：宿主 `ValidatorProxy` 逐字段校验（multitrack_animator.cpp:384-395）后打包成 9 float 的 SoA 设备数组（:398），GPU 内核按 stride 取参——参数校验与设备布局解耦。④**眼动状态内嵌**：saccade（扫视）需要时间累计，单轨用 SetFrameIndex/IncrementLiveTime 由外部推帧，多轨改为 GPU 端 liveTime 数组自持——状态归属从调用方移进动画器。

## 六、新人提示

读多轨代码先看 multitrack_animator.h 的五个 SetActiveTracks 注释块（:47-53、:97-101、:145-150、:193-199、:242-246），它们标注了每个部件是否有状态——这决定 Control 路径是否需要 initializedTracks 位图。改皮肤内核时注意 Everything 与 Control 两个版本必须语义等价，否则全活跃稳态与混合态会产出不一致的帧；调参走 SetParameters 会经 ValidatorProxy 逐字段限界（:385-395），越界值在这里被拦。单轨 IAnimatorTeeth/IAnimatorEyes 是 host 计算（animator.h:314、:378），若 sample 里看到 cudaMemcpy 回传那是单轨路径而非 bug。
