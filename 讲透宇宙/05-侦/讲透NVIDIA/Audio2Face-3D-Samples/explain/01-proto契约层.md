# 01 proto 契约层：16 个 .proto 定义的 A2F-3D gRPC 宪法

## 角色定位
`proto/` 是全仓唯一被三套客户端共同依赖的"宪法层"：16 个 .proto 定义 ACE 动画微服务族的全部消息与服务，两条分发路线（预编译 wheel / 本地生成）产出同一棵 `nvidia_ace` Python 包。没有这层，api_client、early_access、interaction app 三层全是空壳——它们不共享任何业务代码，只共享契约。

## 内部结构
分三类。**数据消息**：`nvidia_ace.a2f.v1.proto` 是核心——AudioStream 用 oneof 包装"首包 header / 后续音频"（:29-37）；AudioStreamHeader（:42-62）聚合 audio.v1.proto:22 的 AudioHeader（PCM/单声道/16bit 三硬约束写在注释）、FaceParameters（14 个 float 面部参数 map，:67-77）、EmotionPostProcessingParameters（6 键情绪后处理，:124-166）、BlendShapeParameters（52 个 ARKit blendshape 的乘子/偏移/clamp，注释给出 0.9*3-1 钳位算例，:99-106）、EmotionParameters（live_transition_time + 10 情绪 beginning_emotion，:108-121）；输出侧 AudioWithEmotion（:168-174）。**回传树**：controller.v1.proto 定义无 ID 版 AudioStreamHeader（:45-59）与 EndOfAudio 标记（:28-40）、AnimationDataStream 四分支 oneof（:104-118）；animation_data.v1.proto:76-83 的 AnimationData 带 `map<string, Any> metadata`，SkelAnimation.blend_shape_weights（:107-115）就是逐帧 blendshape 权重曲线；emotion_aggregate.v1.proto:29-39 的三路情绪（input/a2e_output/a2f_smoothed_output）藏于 Any。**服务面**：services.a2f_controller.v1.proto:26-31 的 ProcessAudioStream 双向流是三客户端唯一主入口；另有 A2FService.PushAudioStream（services.a2f.v1.proto:25-30）、A2FAuthoringService 两个一元 RPC（services.a2f_authoring.v1.proto:10-16）、AnimationControllerService 四 RPC（services.animation_controller.v1.proto:26-42）、A2XExportConfigService.GetConfigs（alpha）；health.proto 是 gRPC 官方健康检查协议原样拷贝——但 package 是 grpc.health.v1 而文件名却是 nvidia_ace.health.proto，生成模块为 nvidia_ace/health_pb2*。

## 外部连接
代码生成链三件套：files_to_compile.yaml 列 16 条（animation_data.v1 出现两次，L24/L33；services.animation_data.v1.proto 有文件却不在清单，wheel 也确实不含该模块）；generate_code_from_protos.py:97-118 解析清单→:63-94 逐个调 grpc_tools.protoc→:152-164 把 `nvidia_ace.a2f.v1_pb2.py` 点号文件名重排进 nvidia_ace/ 目录树并递归补 __init__.py（:121-132）；setup.py:22 打包版本 1.2.0。替代路线：sample_wheel/nvidia_ace-1.2.0-py3-none-any.whl 预编译 50 条目（8 个模块族 × _pb2/_pb2_grpc）。proto/README.md:18 钉版：NIM v1.3 仍用 1.2.0 模块——wheel 与 NIM 版本刻意不同步。

## 数据流
一次推理的契约级轨迹：客户端发 controller 版 AudioStream(header)→逐包 AudioWithEmotion（首包可捎带 EmotionWithTimeCode 列表）→EndOfAudio；服务端回 AnimationDataStream(header→AnimationData*→Status)，header 的 SkelAnimationHeader 一次性给出 blendshape 名单与音频头，后续帧按位序对齐（animation_data.v1.proto:94-105 注释的配对规则）；Status code 0-3 对应 SUCCESS/INFO/WARNING/ERROR。

## 设计决策
①"带 ID / 不带 ID"两套同名消息并存（a2f.v1 vs controller.v1 的 AudioStreamHeader、controller.v1 vs animation_data.v1 的 AnimationDataStreamHeader），注释互指（animation_data.v1.proto:28-31），是"端点入口用简版、内部总线带 ID"的分层选择；②情绪回传塞进 Any metadata 且 proto 自标 alpha（emotion_aggregate.v1.proto:24-25），客户端拆包逻辑随时可能变；③动画通用树（关节/相机/缩放曲线）远超 A2F 需求，为整个 ACE 动画管线复用而设计。

## 新人提示
装 wheel 最省事；自生成必须先 `pip3 install -r proto/requirements.txt`；改 proto 后重跑 generate 脚本会先删整个 generated/ 目录（:68-69），自制产物先备份；a2x_export_config.v1.proto 尾注包名笔误（写 a2f_export_config，:43），排错别被它带偏。
