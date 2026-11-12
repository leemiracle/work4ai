# 02 · ace_client：gRPC 客户端群——C++ 如何消费 proto 生成物

> 源码：`source/ace_client/`（19 文件约 2250 行）+ 生成物 ace_grpc_cpp/。核心五件：a2f_controller_client（双向流主力）、grpc_client（连接/认证基建）、a2f_healthcheck_client、animation（帧仓库）、a2x_config_client；数据结构 frame_receiver.h/parameters.h/audio.cpp。

## 一、角色定位

ace_client 是插件里**唯一知道网络存在的地方**：把 Maya 侧浮点参数与 int16 音频封装成 proto 消息发往 A2F Controller 微服务（本地 Triton 或云端 NVCF），返回帧还原成普通 C++ 结构体。Maya 节点层只见 `ConnectAndSendAudio()` 一个入口。分层自底向上：`grpc_client.cpp` 管 channel/认证/超时 → `IA2FClient` 接口（`a2f_client_interface.h:39`）→ `A2FControllerClient` 唯一实现 → `NetworkedAnimation`（`animation.h:26`，继承 NVCFGrpcClient）做帧管理与插值；healthcheck 与 a2x_config 是旁路。

## 二、内部结构

**A2FControllerClient**（320 行）是"一个方法打天下"：`SendAudio()`（L100-283）走完整双向流协议。发送侧三段式——①AudioStreamHeader（L115-118，`buildAudioStreamHeader` L295：PCM/单声道/16000Hz/16bit L299-302 + 三组参数 map L304-315）；②音频按 **CHUNK_SIZE=16000×2 字节**（L55-56，恰 1 秒 PCM）分块，每块带 `time_code=offset/SAMPLE_RATE`（L139）和十情绪 insert（L141-150）；③EndOfAudio（L159）+ `WritesDone()`（L163）。接收侧：响应头必须是第一条消息（L171-178），blendshape 名单从 `skel_animation_header` 提取（L184-190）；情绪从 `metadata["emotion_aggregate"]` 的 `Any` 解包（L201-206），权重帧落进 AnimDataFrame（L231-244，L233 注释：每包仅一个元素）。

**grpc_client.cpp**（96 行）薄基建：`CreateChannel`（L60-74）按 `https://` 前缀选 SslCredentials 或 Insecure；`SanitizeAddress`（L80-89）剥协议前缀——**gRPC channel 地址不能带 scheme**，用户贴完整 URL 也不出错的原因。`ExtendDeadline`（L76-78）每次读写前重置 deadline 为 now+3 秒（`grpc_client.h:31`）。钉版发现：`grpc_client.h:64` 的 `m_function_id` **默认硬编码 UUID `462f7853-60e8-474a-9728-7b598e58472c`**（NVCF A2F-3D NIM 的 function id），不填时静默启用，开箱即连云端。

**双构造**（L76-82）：channel 版之外还有 `StubInterface` 版——测试注入 mock stub 不发真包即可验证协议封装。**a2x_config_client.cpp**（124 行）消费 `GetConfigs` 服务端流：每读一条就 `ExtendDeadline`（L64-70），大配置不被总超时误杀。**a2f_healthcheck_client.cpp**（109 行）用标准 `grpc.health.v1` Health stub 探活，要求 SERVING（L91）。

## 三、外部连接

向上，`NetworkedAnimation` 被 ace_player 节点持有，Maya 属性变化经 `SetClientParamaters`（animation.cpp:285）刷进参数 map。向下，多类 proto 生成物被直接消费：a2f_controller.v1 的 `A2FControllerService::StubInterface`（`a2f_controller_client.h:24`）、controller.v1 的 AudioStream/AnimationDataStream、a2f.v1 的三组参数消息（成员即 `protobuf::Map<string,float>`，与 parameters.h 的 `GetParameterMap()` 对齐）、emotion_aggregate.v1、health 标准包。向旁，`GetA2XConfig`（a2x_config_client.cpp:39-54）服务 a2x 导出，metahuman_batch 的 Python 走 grpc_py 同款 proto 的另一套生成物。

## 四、数据流

一次完整的云端推理（`ConnectAndSendAudio`，animation.cpp:199-229 四步：建 channel → **健康检查** → InitializeClient → SendAudio）：音频 float 读入（audio.cpp:78 重采样）→ 转 int16（L68）→ 每秒一块流式写出，服务端边收边算边回推 → 收齐存 `m_frames` → Maya 求值时按时间取帧。取帧两条精加工：浮点时间在两帧间**线性插值**（L106-127）；越界帧按 post_infinity 三模式（L157-174：Constant 夹末帧/Cycle 循环/Linear 返空）。超时语义是"逐操作续期"：每次 Write/Read 各续 3 秒（L61-70）——空闲不占预算，卡死即断。

## 五、设计决策

- **错误分类靠字符串匹配**：healthcheck（L57-83）把 gRPC 错误消息文本匹配到六类状态（Unauthenticated/SSL/Deadline/Credits expired/DNS/Connection refused），L57 注释直言"error code 不能准确反映失败原因"——代价是服务端改措辞就静默降级 ERROR_UNKNOWN。
- **流终止是客户端假设**：`SendAudio` status 分支（L251-253）注释承认 proto 没定义流如何结束，客户端"假设"以 ERROR/SUCCESS 终止。
- **FetchFrame 是空壳**（L285-293 `do nothing`）：接口预留"按时间拉单帧"语义，但帧在 SendAudio 已全量预取（animation.cpp:265-283 注释明确）——接口超前于服务端，为流式服务留位。
- **帧数据结构极简**：`AnimDataFrame`（frame_receiver.h:26-36）是六个公共向量的裸聚合，frame_receiver.cpp 全文仅一行默认构造——"receiver"名不副实。测试性内建于 StubInterface 注入，*_mock.grpc.pb.h 在测试里被真正消费。

## 六、新人提示

1. 换自建服务端先过 healthcheck：非 SERVING 一律拒绝；认证走 `authorization: Bearer` + `function-id` 两个 header（L104-109），本地 Triton 通常留空。
2. 硬编码默认 function_id（grpc_client.h:64）意味着**不填 functionId 也真连 NVCF 计费服务**——排查"没配也走云"先查这里。
3. 加新参数走三处：proto 的 FloatParams map（见 03 篇）、parameters.h 的 struct、SetClientParamaters 搬运——参数以 string key 透传不校验键名，拼错即静默无效。
4. 服务端回显的音频（L228-230 空分支）被有意丢弃；音画同步预览需自行解包。
5. 情绪名匹配是**双向约定**：发送侧 insert 十键（L141-150），接收侧按同枚举取值、缺键补 0（L210-216）——服务端换情绪集合会静默全零。
