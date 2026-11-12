# 03 · ASR recognizer 链路：recognizer / model / runner / fe / batching

## 角色定位

这是 ASR 业务主干五件套：recognizer.h/.cpp 是线程安全门面（进程内与传输适配器共享的 ASR 入口，recognizer.h:3-4 注释）；asr/model.h/.cpp 是模型层（CtcModel/RnntModel 双架构 + FastConformer 编码尾部）；runner.h 是每流的执行策略层（三派生覆盖缓冲流式/cache-aware 流式/离线）；features/fe.h 是 NeMo 兼容 log-mel 前端；batching.h 是跨流动态微批协调。五者回答一个问题：任意采样率的 float32 音频如何变成带词时序与说话人标签的转写。

## 内部结构

**Recognizer**（recognizer.h:123）：成员以 BackendManager 打头（recognizer.h:171-173 注释：model+postproc 对着它装载、逆序析构），后随 AsrModel/DiarModel/两套 IngressBatchCoordinator/共享 FlashlightResources（recognizer.h:173-187，KenLM 跨流共享）/Postprocessor/共享 SileroVadModel（每流只持递归状态）。RecognizerConfig（recognizer.h:39-64）聚合 backend/batching/model/streaming/decoder/vad/endpointing/diar/postproc 九组子配置，每组 Register 到 ParameterParser。入口三件：streaming_recognize() 返回 RecognitionStream（recognizer.cpp:609-612 先 make_runner）；recognize() 离线单发（recognizer.cpp:621）；make_runner() 构造流 runner（recognizer.cpp:218）。构造在 recognizer.cpp:98。

**RecognitionStream**（recognizer.h:67）：单线程契约，push 缓冲音频（首个非空 push 钉死输入采样率，recognizer.h:74-77）、force_endpoint 手动断句、next() 推进一步（recognizer.h:79-85 注释钉死 drain 循环：final 则继续、interim 则 break、nullopt 终止——实现在 recognizer.cpp:529，thread_local cohort 继承自 recognize 的 ingress wave）、finish() 冲尾（recognizer.cpp:570）。内置 AudioResampler 把任意输入率重采样到模型率；refresh_speaker_tags 用 diarizer 修订时间线重标词（recognizer.h:92-96，说话人标签在此时刻前不可变）。

**模型层**：AsrModel 基类（src/asr/model.h:48）暴露 sample_rate/subsampling_factor/ms_per_enc_frame（src/asr/model.h:62-68）与 diagnostic_sessions；Common 装载结构聚合 GGUFLoader+命名空间+编码器配置+FE 配置+vocab（src/asr/model.h:97-105）；内嵌 SentencePiece（src/asr/model.h:92-94，asr.tokenizer.spm_model，词增强两路径共用）。CtcModel（src/asr/model.h:129-154）给 infer_ctc/infer_ctc_from_mel/infer_ctc_greedy 三入口——greedy 是设备端 argmax+胜出概率的紧凑路径，Flashlight 才要全分布；RnntModel（src/asr/model.h:177，双继承 AsrModel+RnntEngine）37 方法覆盖流式预测/联合/融合与 prompt 融合。model.cpp 承载 FastConformer 尾部三变体与预测-联合两级解码。

**runner 三派生**（runner.h）：①BufferedStreamRunner（runner.h:115）适配非 cache-aware 编码器：滑窗 [左垫|chunk|右垫] 默认 1.92/0.16/1.92s 只解码中心块（StreamingConfig，runner.h:28-34）；audio_buf_/mel_buf_ 是滑动存储（audio_base_/mel_base_frame_ 是元素 0 的全局序号，trim_buffers 只挪底座不动物理游标，runner.h:187-199）；ensure_mel_cache 增量补算新 mel 帧——相邻窗重叠 ~96%，无此缓存每步重算整窗（runner.h:148-153）；poll_endpoint 在解码时钟上巡检端点（runner.h:135）。②CacheStreamRunner（runner.h:254）适配 cache-aware 编码器：mel 帧几何由 GGUF 钉死（runner.h:298-305 注释给出 NeMo 三公式：首块/后续块/shift）；K/V/conv 缓存经 AsrModel::make_cache_state() 懒分配、设备驻留、图内更新零主机拷贝（runner.h:349-353）；attn_mask 仍是每调用 Input（随 cache_filled_frames 增长，主机侧每 chunk 上传，runner.h:354-356）；prompt_index 支撑多语言提示融合（runner.h:308-311）。③OfflineRunner（runner.h:212）：整段一次编码，pad_audio_to_bucket_ 静音填充对齐批形状，offline_segments_ 切段。

**fe**：MelSpectrogramExtractor（fe.h:63）双路径同布局——bm 非空走缓存 ggml 图、null 走 CPU radix-2 FFT（fe.h:139-143），输出 frame-major 使 ne[0]=n_mels 对齐 ggml 约定（fe.h:74-76）；compute 的 reflect_left/normalize 两旗区分流式中段调用（fe.h:78-87）；MelSpecConfig 的数值考古密集：log_zero_guard 必须取 NeMo 的 2^-24（fe.h:37-41——1e-5 会把静音抬高 ~5 nats 扰动 cache-aware 编码器翻转首词语言决策）、hann_periodic 与 stft_center_window 的 NeMo 行为开关、mask_invalid_frames 补 NeMo 归一化路径不 mask 尾帧的缺口（fe.h:44-56）。流式侧 produce_new_mel_frames（fe.h:168-170）只释放右缘是真实样本的帧。

**batching**（batching.h:31-66）：默认 enabled=false（避免单流排队）；ingress_cohort_delay_us 20ms 独立于 max_queue_delay_us 5ms——流式入口波次需要更宽的主机收集窗；offline_bucket_ms 把离线句静音填充到时长倍数让混合长度共享批 key；ScopedBatchCohort（thread_local g_batch_cohort_target，batching.h:94-112）让一个请求线程声明"本波有多少兄弟"，神经阶段据此提前放行；BatchMetrics（batching.h:68-86）区分 capacity/ready_set/deadline 三种放行原因。

## 外部连接

上游：RecognitionStream 的 push 来自 C API（include/nemo_speech/asr.h 的流式协议）、gRPC StreamingAsrSession、http_server 的 SSE 转写；diar sidecar 与 ASR 共用同模型率音频（DiarStream 挂 runner 旁）；postproc 管线消费 StreamingUpdate 的 token/词时序做 ITN/PnC。下游：model 层建在 ggml runtime 的 Module/Session 上（见 explain/01）；runner 构造 CtcHeadModule/GreedyCtcDecoder/RnntGreedyDecoder 或 FlashlightDecoder（explain/04）；diar/sortformer 与 pnc 各自独立建 Session 但共享 BackendManager。EngineRegistry::load_asr 免费派生内嵌 Diarizer（engine_registry.cpp:53-60）。

## 数据流

流式一路：push(任意率 float32) → 重采样进 runner.audio_buf_ → VAD 喂到已观测水位（audio_fed_to_vad_，runner.h:178）→ next()：ensure_mel_cache 增量产 mel 帧 → 取窗（VAD masker 在原始 log-mel 副本上置零静音帧，缓存本体永不被污染）→ per_feature 归一化 → Session::run 跑编码器+头 → StreamingUpdate（token/transcript/词时序/confidence/audio_processed_sec，runner.h:50-69）→ poll_endpoint 决定 EOU → build_result_ 拼词时序+说话人标签+late_punctuation。离线一路：feed_audio 累积 → finalize 一次 infer（桶填充对齐）→ 同一个 Result 结构。

## 设计决策

①runner 与 RecognizerConfig 同源（runner.h:110-114 注释：无独立 per-runner 配置防漂移）。②VAD 每步观测一次共享给 masker+endpointer，杜绝双推理（runner.h:171-174）。③mel 缓存存原始 log-mel、归一化在窗副本上做——流式/离线/VAD-mask 三路径数值可互换的底座。④exact-shape 微批：只有形状完全相容的工作才合并，dynamic shape 会触发图重捕获（docs/development/asr-batching.md）。⑤EOU 时 endpointer 发火一次即重武装，且 reset_utterance 保留 LSTM 状态跨句（riva EOU 契约，tests/cpp/asr/test_decoders.cpp 覆盖）。

## 新人提示

阅读顺序：recognizer.h → runner.h 三类注释（密度极高=设计文档）→ recognizer.cpp:529 的 next() 看 drain → fe.h 的 MelSpecConfig 数值考古。调试：NEMO_SPEECH_TIMING 看 Session 分段耗时；流式几何对不上先查 model 的 subsampling_factor 与 StreamingConfig 窗口乘积关系。坑：改 mel 归一化务必同时看 GPU/CPU 两路径（fe.cpp 双实现必须位级同布局，tests 有奇偶校验）；diar 标签的不可变时刻（stable_speaker_time）晚于直觉——它排除了 provisional chunk 与追溯重标。
