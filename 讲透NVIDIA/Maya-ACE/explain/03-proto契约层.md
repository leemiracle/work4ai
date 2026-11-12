# 03 · proto 契约层：12 个 .proto 源与三套生成物的对照

> 源：`examples/metahuman_batch/proto/protobuf_files/` 12 个 .proto（数据 7+控制 1+服务 4）；生成物 `source/ace_grpc_cpp/`（87 文件含 17 个 mock）与 `python/grpc_py/`（镜像 9 包+health/version 独立两件）。

## 一、角色定位

这一层是 Maya-ACE 与 A2F-3D 微服务生态的**唯一接口契约**：Maya 插件（C++）、批处理示例（Python）、mock 服务端三方共享同一 schema，改一字段三方同时受影响。12 个 proto 分三层：**数据层**（a2f/animation_data/animation_id/audio/emotion_aggregate/emotion_with_timecode/status 七包只定义消息）、**控制层**（controller.v1 定义无 ID 的流式消息）、**服务层**（四个 services.* 只定义 rpc 签名）。生成物三路：C++ 头给插件、Python pb2 给示例与 mock、mock 生成物给单测——全仓 CMake 无 protoc 调用，**生成物全部预生成入库**，.proto 不参与构建。

## 二、内部结构

**控制层 controller.v1** 是理解全协议的钥匙。`AudioStream` 的 oneof（nvidia_ace.controller.v1.proto:32-39）定义流生命周期：header 第一条、AudioWithEmotion 至少一条、EndOfAudio 最后（:37-38）。两处 "IMPORTANT NOTE"（:42-44）披露刻意设计：controller.v1 头消息**不带 ID**，a2f.v1 同名消息带 AnimationIds——突发会话无需寻址，长驻管线才需 ID 复用。`AnimationDataStream` 的 oneof（:106-115）注释明言 status "must be sent last and may be sent in between"——02 篇"假设 ERROR/SUCCESS 终止"正源于此注释模糊。`END_OF_A2F_AUDIO_PROCESSING`（:59-64）区分"算完"与"收完"；`start_time_code_since_epoch` 注释（:86-95）是少见的分布式时钟讨论（NTP/PTP）。

**服务层四包 = 四种流形态**：`ProcessAudioStream`（nvidia_ace.services.a2f_controller.v1.proto:29-30）双向流，"single clip ... in a burst"——插件现用唯一通道；`A2FService.PushAudioStream`（nvidia_ace.services.a2f.v1.proto:26-28）客户端流返单 Status；`AnimationControllerService` 四 RPC（nvidia_ace.services.animation_controller.v1.proto:31-44）：RequestAnimationIds（unary 领 ID）→ PullAnimationDataStream（服务端流）→ PushAudioStream（客户端流）→ UpdateAnimationGraphVariable（客户端流改图变量），一套有状态会话协议；`AnimationDataService` 的 Push/Pull 对偶（nvidia_ace.services.animation_data.v1.proto:36-43）注释给方向判据：**生产者是客户端用 Push**（A2F→Animation Graph）、**是服务器用 Pull**（Renderer←Animation Graph），Animation Graph 两边都实现（:29）。

**数据层**要点：a2f.v1 的 FaceParameters 是三个 map（nvidia_ace.a2f.v1.proto:69-73）——02 篇"参数以 string key 透传"的源头在这，弱类型 map 换跨版本兼容；BlendShapeParameters 两个 map（:98-100）。status.v1 枚举 SUCCESS=0/INFO/WARNING/ERROR（nvidia_ace.status.v1.proto:22-27），0 是 proto3 默认值——**服务端忘填 code 时客户端读到 SUCCESS**，隐性坑。

## 三、外部连接

向上，`A2FControllerClient` 消费 controller.v1+a2f.v1 生成物（见 02 篇）；向下，pb2_all.py 聚合全部消息供示例与 mock_server 使用（MockA2FAuthoringServiceServicer 见 mock_server.py:66，注册于 mock_server.py:162-163）。横向对比：两套生成物对应 12 proto 中的 9 包，**外加 a2f_authoring 与 version 两服务有生成物却无 .proto 源**。health 是 grpc 标准包拷贝：health_pb2.py:17 内嵌完整 descriptor（含 C++ 端未用的 Watch RPC），源在 grpc 仓库。

## 四、数据流

以 Maya 云端工作流为轴：客户端组装 AudioStream（header→分块 AudioWithEmotion→EndOfAudio）经 ProcessAudioStream 发出；服务端按序回 AnimationDataStream（header 带 blendshape/joint 名单（nvidia_ace.controller.v1.proto:83）→若干 AnimationData，情绪藏在 metadata 的 Any→末尾 Status）。突发通道外生态还有两条管线流：A2F→Animation Graph 走 Push（算完主动推），Renderer←Graph 走 Pull（按 AnimationIds 订阅拉），两向共用 animation_data.v1 消息族。插件今天只用三形态之一，但生成物全量编译——契约面远大于用量。

## 五、设计决策

- **生成物入库而非构建期生成**：免版本漂移，克隆即编译；代价是契约变更须三处同步（proto 源、C++/Python 生成物）且无 CI 校验。
- **a2f_authoring/version 无 proto 源之谜**：全仓 grep 证实这两个服务只有生成物（RPC 为 UploadAudioClip/GetAvatarFacePose 两个 unary，见 nvidia_ace.services.a2f_authoring.v1.grpc.pb.h:46/:54），.proto 从未随仓。可行解释：.pb.h 内嵌序列化 descriptor 使 C++ 无源文件即可编译，维护者拿到的是上游预生成包而非源；mock_server 却实现了 authoring（mock_server.py:66）供离线演练——它是**云端 avatar 制作服务的预留接口**，插件尚未接、mock 先行。
- **弱类型参数 map** 换向前兼容：加参数不改 schema，但拼错 key 静默无效（02 篇坑 3 的根源）。
- **SUCCESS=0 与 proto3 默认值重合**：依赖"服务端总显式填 code"的君子协定，防御只能放客户端。
- **同消息双形态（带/不带 ID）**：用注释而非类型系统区分使用场景，靠人读 IMPORTANT NOTE 不踩坑。

## 六、新人提示

1. 读协议先读 controller.v1 两条 oneof 注释——全部流的时序合同；"流怎么结束"的答案只能是 nvidia_ace.controller.v1.proto:105 那句含糊注释+客户端防御假设。
2. 改 .proto 不生效——须重新 protoc 生成三套产物并一起提交，否则源与产物静默漂移。
3. 对接自建服务从 mock_server.py 起步：12 个 proto 消息语义的可执行样例，不花云端积分。
4. Push/Pull 的选择看**数据生产者在连接中的角色**，不是数据方向——注释原文是唯一权威。
5. 想找 a2f_authoring/version 字段定义只能反推生成物（打印 v1_pb2 的 descriptor 即可），别找不存在的 .proto。
