# 02 api_client：NVCF 云端三件套最小客户端

## 角色定位
`scripts/audio2face_3d_api_client/` 是面向 **NVCF（NVIDIA Cloud Functions）托管 A2F-3D NIM** 的最小示例：48 行入口 + 79 行 auth + 242 行 service，教你用四个必填参数（音频/config/apikey/function-id）把一段 wav 换成 blendshape CSV。它是三套客户端里唯一全程 grpc.aio 异步、且不依赖本地 GPU 的一套。

## 内部结构
三件套各司其职。**auth.py**：create_channel（:21-39）三种模式——传 ssl_cert 或 use_ssl 时组装 ssl+metadata 复合凭据的 secure_channel（:26-36），否则 insecure；metadata_callback（:23-24）把授权头注入每个请求。Auth 类（:41-80）是 Riva 血统的活化石：docstring 写 "a Riva URI"（:57），且默认值 localhost:50052（:46）与 docstring 声称的 50051（:57）自相矛盾。**service.py**：write_to_stream（:171-243）读 wav→按 1 秒切块（:204-207）→首包 AudioStreamHeader 装配五组参数（:182-199，全部来自 config yml 的五个 section）→首块音频捎带情绪时间码表（:213-229）→EndOfAudio 收尾（:242）；read_from_stream（:91-168）处理三类消息：header 存 blendshape 名单+音频头（:129-136）、animation_data 逐帧 dict(zip(bs_names, values)) 攒 key frames 并追加音频字节（:137-153）、status 打印 0-3 语义（:154-168）；EOF 时建时间戳目录落盘三 CSV+out.wav（:109-127）。parse_emotion_data（:61-89）用 Any.Unpack 拆 EmotionAggregate 三路情绪。**nim_a2f_3d_client.py**：main（:31-45）拼 function-id+Bearer metadata（:34）→NVCF 端点建通道（:36）→A2FControllerServiceStub→双 asyncio 任务并发读写（:41-42）→await 收官。

## 外部连接
依赖 proto 层 6 个模块（service.py:19-25：animation_data/a2f/audio/services.a2f_controller/controller/emotion_*）；config/ 三份 257 行 yml（face_parameters camelCase 直配 proto map、blendshape_parameters、post_processing_parameters、emotion_with_timecode_list、live_transition_time/beginning_emotion）——与 interaction app 的 config 逐字节同 md5；requirements（无扩展名文件）声明 grpcio/scipy/pandas 等。

## 数据流
wav 文件 → scipy 读采样率 → AudioHeader(samples_per_second, 16, 1, PCM) + config 参数 → 双向流写入 → 服务端 A2F+A2E 推理 → AnimationData 帧流回 → 客户端聚合 → `{时间戳目录}/animation_frames.csv + a2f_smoothed_emotion_output.csv + a2f_input_emotions.csv + out.wav`（README:5-7 明言 out.wav 应与输入一致，可作回环校验）。

## 设计决策
①读写拆两个 coroutine 是双向流的标准姿势——写侧不被读侧反压阻塞；②情绪时间码只在第 0 包发送（:209-212 注释解释流式场景可后补）；③get_audio_bit_format（:34-43）对回传音频做格式白名单，非 PCM16 直接拒写；④--function-id 同时给 required=True 和 default=""（nim_a2f_3d_client.py:28）——default 是死代码，纯防御式写法。

## 新人提示
休眠 bug 警示：emotion_key_frames 初始化只有 input/a2f_smoothed_output 两键（:101-104），而 parse_emotion_data 会写 a2e_output 键（:76）——NVCF 端真回 A2E 输出条目时此处 KeyError，且 a2e_output 数据本就无 CSV 落盘通道；跑通后先 `python3 ./nim_a2f_3d_client.py ../../example_audio/Claire_neutral.wav config/config_claire.yml --apikey <KEY> --function-id <ID>`（README 默认命令）。端口/端点疑问时记住：本套默认连云端 443，别拿 50051/50052 docstring 当真。
