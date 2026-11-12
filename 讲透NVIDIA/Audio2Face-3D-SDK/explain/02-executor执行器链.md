# 02 · executor 执行器链——基类骨架、双模型实现与两级管线

> 锚点前缀：仓库根 `audio2face-sdk/`。行号锚全部从源码核实。

## 一、角色定位

执行器链是 audio2face 推理的"主循环所在"。公共侧三个接口构成继承塔：`IFaceExecutor`（executor.h:33）定义情感回调与读取进度（SetEmotionsCallback executor.h:47、GetNextAudioSampleToRead :54）；`IGeometryExecutor`（:61）产出几何结果，用 4 位 `ExecutionOption` 控制计算面（Skin/Tongue/Jaw/Eyes 位掩码，:64-72）；`IBlendshapeExecutor`（:113）产出 blendshape 权重，区分 HOST/DEVICE 两种回调（:137 与 :161）。实现侧分三层：executor.cpp（490 行）的 `GeometryExecutorBase` 是骨架；executor_regression.cpp 与 executor_diffusion.cpp 是两份并列的 `Execute()` 主循环实现；executor_blendshapesolve.cpp 把 geometry 执行器包成第二级管线。

## 二、内部结构

`GeometryExecutorBase` 持每轨 `TrackData`（audio/emotion accumulator + WindowProgress，internal/executor.h:197），骨架方法全是模板化的公共逻辑：`GetNbAvailableExecutions` 委托 nva2x 窗口计算并校验三依赖非空（executor.cpp:49-62）；`GetTotalNbFrames` 要求音频已关闭、按累计样本反推总帧数再减去 `_nbFramesBeforeAudio`（:64-82）；`BaseInit` 初始化逐轨数据、校验情感尺寸匹配（:269-308 中 :286-290），并在 :299-303 预计算"音频开始前的帧数"——注释明示只有 diffusion 用到、回归应为 0。所有可变状态都走"启动前"闸门：SetExecutionOption / SetEmotionsCallback / SetResultsCallback 一律在 `HasExecutionStarted` 后拒绝（:102-115、:141-150、:169-179），SetResultsCallback 还校验"回调空则 userdata 必空"（:175）。访问器走 internal/executor.h 的 Accessor 接口族（IFaceExecutorAccessorInputStrength :35、SkinParameters :59 等），executor.cpp 匿名空间的 `GetExecutorParameters` 模板用 `dynamic_cast` 打通（:337-354，NOTE 注释自认跨编译器 dynamic_cast 有风险 :333-336）。

## 三、外部连接

向上消费 audio2x 的 `IAudioAccumulator/IEmotionAccumulator`（GeometryExecutorCreationParameters 数组传入，executor.h:168-179），向下驱动 core 内的多轨动画器与 TensorRT 推理。两级管线的挂接在 executor_blendshapesolve.cpp：`HostBlendshapeSolveExecutor::Execute` 先驱动被包装的 geometry 执行器（:263-269），Device 版同构（:533-539）；几何结果回调里再对每轨 skin/tongue solver 发起 `SolveAsync`（SkinSolveAsyncHost :421-423），CPU 求解器经 job runner 异步、注释明示"SolveAsync 在 CPU 求解器上实际是阻塞语义的变体"（:385-388）。工厂在 executor_regression.cpp:337-348 与 executor_diffusion.cpp:399-410，均 make_unique→Init→release。

## 四、数据流

两份 `Execute()` 是同构五段式。**回归版**（executor_regression.cpp:45-282）：①遍轨判可执行性并读音频窗与显式情感（:63-99，"Data is not tightly packed to avoid moving data around if indices are skipped" :59-60）；②`nbExecutedTracks > 0` 闸门（:101）；③单次批量推理（:103-106）；④按 ExecutionOption 做批量后处理——skin 走 PCA 重建+皮肤动画两级动画器（:123-149），tongue 同构（:151-177）、jaw/eyes 各一段（:179-211），全轨参与时传 `nullptr` 活跃位图省去下发（:118-120）；⑤逐轨回填 Results 并触发 emotions/results 双回调（:254-272）后 `IncrementReadWindowCount`（:274）。Init 固定 `nbFramesPerInference = 1`（:305）并断言 `_nbFramesBeforeAudio == 0`（:309），隐式情感从 EmotionDatabase 取 sourceShot 首帧（:313-322）。**扩散版**（executor_diffusion.cpp:46-359）差异在：推理一次出多帧（帧数 = `numFramesCenter`，:377）、逐帧读情感（:93-103）、按轨生成噪声（:105-113）、推理前显式 BindBuffers（:121）、推理后 GRU 状态缓冲 Swap 并给未执行轨道回拷旧状态（:127-144，优化注释 :129-134）、后处理与回调按帧序优先（:156-158 帧主序注释），回调返回 false 即标记 `_doneTracks` 提前停（:335-344）。

## 五、设计决策

①**批内活跃位图**：`_executedTracks`（bit_vector）贯穿判活-后处理-汇报三段，避免稀疏轨道搬移数据（executor_regression.cpp:61、119-120）。②**回调即节流阀**：results_callback_t 返回 bool（executor.h:103），多帧执行时用户可中途叫停——diffusion 版真正消费该语义，回归版单帧忽略返回值（executor_regression.cpp:268-272）。③**错误宏统一**：A2F_CHECK_ERROR_WITH_MSG 全链路带人话消息与错误码，getter 失败返回哨兵值 0/min 而非异常（executor.cpp:50-54）。④**两级管线的所有权转移**：blendshape 执行器持有 geometry 执行器指针，门面注释明确 Ownership transferred（audio2face.h:255）——一份数据两次增值，不重复推理。

## 六、新人提示

先读 executor.h 的三个 Results 结构体（executor.h:87-99、128-133、145-151）理解"一次执行可能出多帧、字段按 ExecutionOption 可选填充"，再对照读两份 Execute 的 ④⑤ 段即可对齐主干。调试"回调不触发"先查三处：results callback 未设（executor_regression.cpp:52 直接报错）、情感不足 `eEmotionNotAvailable`（:91-95）、目标帧超出累计样本（:80-84）。`GetFrameTimestamp` 有意给 frameIndex 加 `_nbFramesBeforeAudio` 偏移（executor.cpp:94）——diffusion 从音频前就开始出帧，时间轴可为负时间戳（nva2x::timestamp_t 是 int64 样本索引）。
