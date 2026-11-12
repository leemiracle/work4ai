# 01 · a2f_player 双播放节点：本地 TRT 推理与云端 NVCF 的两副面孔

> 源码：`source/maya_ace/nodes/` 下 a2f_player.cpp（1830 行）/a2f_player_static.cpp/ace_player.cpp（629 行）+ `common/timeslider.cpp` + `scripts/ace_tools/setup.py`
> 勘误：文件在 `nodes/` 而非 `commands/`；"789 行"指 `initialize()` 单函数体（L122-911），全文件 911 行。

## 一、角色定位

插件向 Maya 注册两个动画播放器依赖节点（`plugin.cpp:96-102`）：**`A2FAnimationPlayer`**（typeName 见 `a2f_player_static.cpp:31`）在 Maya 进程内驱动 A2E/A2F 的 TensorRT 执行器做本地整段推理；**`AceAnimationPlayer`** 把音频打包成 int16 经 gRPC 发往云端（NVCF/NIM），收帧后按时间轴回放。二者无公共基类但共享接口语义（`time`/`outputWeights`/`outputEmotions`），接线脚本无差别对待（`setup.py:355`）——"同契约、双后端"，换后端场景图不重连。

## 二、内部结构

A2FAnimationPlayer 的方法分四层：①生命周期（`postConstructor` L86 注册进度条上下文；删除/undo 靠 `plugin.cpp:54-71` 回调兜底）；②compute 分发（`compute()` L93-156 是纯路由器；L135-139 处理"mesh 属性未连接也会被求值"的 DG 陷阱）；③执行器初始化——`computeInitA2EExecutor`（L335）按 A2E 模型路径分三路：空路径走纯后处理（L384 构造 `defaultEmotionCorrespondence(6,-1)`，-1 即不映射输出情绪）、分类器走 Classifier 执行器（L427）、否则 PostProcess 模型；`computeInitA2FExecutor`（L473）先建 geometry executor，带 blendshape 信息再包一层 solve executor（L566）；fps 等未暴露参数 L376-379 硬编码 30/1。④求值调度（L1418，见第四节）。`a2f_player_static.cpp` 的 `initialize()`（L122-911，**789 行单函数**）创建数十属性并织出依赖图。

AceAnimationPlayer 仅 13 个方法，`compute()`（L74-209）串起 trigger 链：同步别名 → 装音频 → `sendAudio`（L515）调 `animClient.ConnectAndSendAudio()` 完成连接+推流+收帧；L51-63 把 5 种错误映射为人话。钉版发现：`loadAudioFile()` L608-609 的 `padding_before/after` 是**死变量**，从未插入缓冲（L616 只插音频本体）——加 padding 的旧逻辑被删后变量残留。

## 三、外部连接

与 blendshape 节点接线（`setup.py`）走三通道：①几何直通——L248 把 `meshShapeOrig.outMesh` 接到 player 的 `faceGeometryOrig`，L256-259 断开 mesh 原 `inMesh` 改接 `faceGeometry`；②权重通道——L369-390 把 `outputWeights[i]` 逐个接到 `blendShape.weight[i]`，优先按 pose 名别名匹配（`a2f_player.cpp:639`），失配才按下标硬连；③时间通道——L521 接 `time1.outTime`。时间轴连接由 `timeslider.cpp` 实现：`registerCustomDraw()`（L38）注册 2 像素进度条，`draw()`（L125）三色区分——等待灰蓝/进行中黄/完成绿（L140）；全文件被 `#if ENABLE_TIME_SLIDER == 1`（L36）包住，无 GUI 批处理全退化。与 NVCF 的连接有前置闸门：URL 以 `https://grpc.nvcf.nvidia.com` 为前缀先弹 `nvcloud::acquireAgreement()`（`ace_player.cpp:107-113`）——云端推理花积分。

## 四、数据流

本地节点核心是**"快估计先行 + 后台全量"双速推理**：①`isCacheStale()`（L1365）三态判定——参数变则脏、仅 time 变则不脏（用旧缓存取帧）、全同则看 `prevParametersSame` 区分"拖时间轴反复触发同一时刻"与"鼠标抬起重设同值"；②脏时先跑 A2E 全帧（L1477，快），再 `runA2FExecutorOffline(quickEstimate=true)` 只算当前帧（L1493）保证拖动手感；③L1531 起 `std::thread` 跑全帧 `ComputeAllFrames()`，线程入口先 `wait_for(300ms)`（L1155）防抖——连续改参数时让"正在取消"先赢；④结果经回调写入预分配 `HostTensorFloat` 大缓冲：geometry 回调把 skin/tongue/jaw/eyes 四段 GPU 结果依次 `CopyDeviceToHost`（L975-1002），blendshape 回调按 `ResultsType` 分 HOST（L1057）/DEVICE（L1081），回调内同步 `TimeSliderProgress::draw`（L1006）；⑤下游 `computeGeometryResults`（L1574）按 `frameIndex = time×frameRate`（L1127，clamp 防越界）切片：face 点集写回缓存 mesh（L1627），下颌 16 元素矩阵直拷（L1670），眼睛旋转是角度须乘 π/180 转弧度（L1686）——单位不一致是该输出最易踩的坑。云端节点无缓存判定无后台线程：`updateFrameOutput`（L314）按音频时间取已下载帧——计算在云端，本地只剩回放。

## 五、设计决策

- **blendshape multiplier/offset 旁路**：`resetBlendshapeMultipliersAndOffsets()`（L644）先读出执行器 solver 配置填进 Maya 属性，再把执行器内部**强制重置 1.0/0.0**（L663-681）；取帧时手动应用 `w*m+o`（L1762-1769）。动机见 L663-665 注释：让修正量变成**可 keyframe 的属性**而不触发重新推理。
- **双缓冲借脏传播**：`quickEstimateBufferAttr` 恒分配 1 帧（L1310），`backgroundEvaluationBufferAttr` 分配全帧（L1352），均为 typed plugin data，靠 Maya 脏传播携带"何时重算"语义。
- **禁用内建缓存**（L63-70）+**正常/后台上下文双轨**（别名增删只在 `isNormal()` 做，L488-496，推理照跑）——plugin data 无法被 cache 序列化；拆上下文是参与并行求值的前提。
- **云端节点十情绪硬编码**：`ace_player.cpp:217-229` 与 L590-603 的 `switch(i)` 写死 amazement..sadness，三处 TODO 承认要等服务端配置驱动；本地节点已用 `getEmotionNames()`（L537）数据驱动。

## 六、新人提示

1. 新增输入属性必须补 `attributeAffects` 布线，否则改参数不重算——"静默不更新"九成在此。
2. **音频 offset 语义两节点不对称**：本地 `offset>0` 生成前置静音、`<0` 平移起点（a2f_player.cpp:727-731）；云端 offset 只参与取帧换算（ace_player.cpp:388/398），发送音频不带 padding——换节点后对口型不上优先排查此。
3. `outputWeights` 匹配靠 `out_`+pose 名别名，下标手连换 identity 后会静默错位；两节点是平行实现，改名单查另一边。