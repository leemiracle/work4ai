# 03 early_access authoring：逐帧取姿态的授权客户端与双部署

## 角色定位
`early_access/a2f-3d-authoring-sample-app/`（4 文件共约 1120 行）是 **A2F-3D Authoring 微服务**（早期访问版）的官方测试客户端。与其余两套的"流式推理"范式不同，它消费 A2FAuthoringService 的两个一元 RPC（services.a2f_authoring.v1.proto:10-16）：UploadAudioClip 传整段音频换 SHA-256 哈希，GetAvatarFacePose 按时间戳逐帧买 blendshape——为离线动画制作（authoring）而非实时流设计。三种用法：health_check 探活、data_capture 全片采集、latency 压延迟。

## 内部结构
**common.py（642 行，共享库）**：三组常量——DEFAULT_FACE_PARAMS 14 项（:52-67）、EMOTION_KEYS 10 情绪（:69-80）、TIME_1_FRAME=1/30 即 30fps（:82）。四个核心函数：upload_audio_clip_and_get_hash（:263-302）构造 AudioClip（PCM16 mono AudioHeader + 字节，:283-291）取回哈希与 blendshape 名单；make_face_pose_request（:305-338）组装 FacePoseRequest（preferred_emotions 全零、max_emotions=6 等写死参数）；get_avatar_face_pose（:341-363）单帧 RPC；perform_parallel_data_exchange（:598-619）= prepare_requests（:400-434，按 30fps 算帧数、random.seed(42) 确定性洗牌时间码）+ perform_parallel_requests（:476-542，threading.Thread 起 N 个 LatencyTesterClient、join 后汇总）。**LatencyTesterClient**（:545-595）三段式 run：initialize_channel（本地 insecure / NVCF secure，:559-566）→upload_audio→make_requests（逐帧计时 perf_counter）。**LatencyResult**（:101-260）持延迟表，__str__ 出 P1-P99 十档文本（:193-205），plot_percentiles（:209-260）出 viridis 配色的百分位直方图。**双入口**：client_local_deploy.py（--url 明文直连，:132）与 client_nvcf_deploy.py（--apikey/--function-id/--version-id 三元组 metadata，:169-173；三子命令全部 required，:114-158），data_capture 落盘 output_blendshape.csv + output_emotions.csv（client_local_deploy.py:168-185）。

## 外部连接
auth.py（49 行）与 api_client 版近同源，关键差异是本版 create_channel 返回**同步** grpc.secure_channel（auth.py:46-48），配套 GRPC_URI 常量 grpc.nvcf.nvidia.com:443（:22）——因为 common 的压测走线程而非 asyncio。proto 依赖 6 模块（common.py:32-46：health/a2f/a2f_authoring/audio/services.a2f_authoring）。

## 数据流
wav→30fps 帧数→UploadAudioClip（一次）→audio_clip_hash→[GetAvatarFacePose(hash, t=i/30)]×N→BlendShapeData（blendshapes 数组+time_code+emotions map，a2f_authoring.v1.proto:45-54）→CSV 两份（blendshape 按名单列序、emotion 按 EMOTION_KEYS 列序）。

## 设计决策
①"上传一次、按帧买"把状态留在服务端（哈希即句柄），规避流式时序问题；②线程+同步通道做并发压测，与 api_client 的 asyncio 路线互为对照，也是两份 auth.py 分化的根因；③latency 模式先上传后压帧（LatencyTesterClient.upload_audio 计入 time_upload 单独统计，:568-574）；④README 实录服务端回 55 个 blendshape 名（52 ARKit + 3 个 HeadRoll/Pitch/Yaw_deprecated），多出的废弃头部自由度只在此 API 出现。

## 新人提示
拼写地雷三处：Receivedd（:301）、blenshape_names（:532,:557）、README 的 "Saved lantecy data"——搜代码时用错拼会漏检；latency 并发别开太猛（README 警告 too high concurrency increases latencies）；Python 要求 3.10（README 声明，用了 `list[str] | None` 语法）；本地探活示例端口 50051 与 api_client docstring 的 50052 又不同——三套客户端三个默认端口口径，一律以实际部署的 --url 为准。
