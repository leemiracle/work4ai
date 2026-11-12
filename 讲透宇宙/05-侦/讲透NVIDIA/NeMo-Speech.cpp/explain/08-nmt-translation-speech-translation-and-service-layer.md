# 08 · NMT 翻译、语音翻译级联与服务层（L9 · 32 节点群）

## 角色定位

这一层回答的问题是：单机 GGUF 模型如何变成"一个端口上的多协议语音服务"。图谱 L9 的 32 节点分四条线：`src/nmt/`（文本翻译内核）、`src/speech/`（ASR→NMT→TTS 级联）、`src/services/` + `src/server/` + `proto/`（gRPC/Riva 协议面）、`server/http/`（OpenAI 风格 HTTP + WebSocket 实时端点）外加 `config/` 七个 YAML 样例。设计哲学是"核心能力先于协议适配器"（riva_server.cc:341 注释）——Recognizer/Translator/Synthesizer 以 shared_ptr 存活，gRPC/HTTP 两个壳都从它们派生。

## 内部结构

**NMT 内核**（src/nmt/，6 文件）：`Translator` 用 pimpl 把 llama.h 完全藏在实现后面（translator.h:3-7），消费方链接时不看见 llama/ggml。它包装 llama.cpp 跑 Riva-Translate 解码器：贪心采样（translator.cpp:181）、prefill 按 n_batch 分块喂入（translator.cpp:132-137）、逐 token 生成直到 EOG（translator.cpp:140-148）。上下文池是并发核心——`pool.contexts` 个 (context+sampler) 槽位，`acquire/release` 用 condition_variable 配对（translator.h:47-57；translator.cpp:83-97），`translate()` 线程安全但并行度受槽位数封顶。默认 `n_ctx=1024` 是刻意的：按句/短轮次翻译的常见情形（bs=1）设计，KV 缓存线性成本约 0.13 MiB/token（translator.h:28-33）；提示超长时报清晰错误而非玄学解码失败（translator.cpp:122-126）。

**语言对表**（langpairs）：静态表从 `en-zh-cn` 到 `fi-en` 约 40 个 tag（langpairs.cc:17-60），每个 pair 都有英语在一边（langpairs.h:29）。`resolve_tag` 容忍三种输入形态：双码拼接、单字段塞现成 tag、BCP-47 归一化（langpairs.cc:145-176；`normalize_language_code` 把 en-US 落到 en，langpairs.h:15-18）。`build_prompt` 手工复刻模型 chat template 加 `add_generation_prompt` 的输出，使手拼提示与内嵌模板逐字一致（langpairs.h:32-35）。

**语音翻译级联**（src/speech/speech_translator.*）：传输中立的 `SpeechTranslator` 持三个 shared_ptr——Recognizer、Translator、可选 Synthesizer（speech_translator.h:67-69）。每流一个 `SpeechTranslationStream`，回调三类：`translation`（每个 ASR final 译出后触发）、`audio`（每个合成 PCM 块）、`utterance_end`（语义句边界，speech_translator.h:32-44）。级联逻辑在 `Impl::emit_final`：空转写直接跳过（speech_translator.cpp:79-80），译文先回调、再按需走 TTS（:90-113），任一回调返回 false 即置 cancelled 反压上游（:127 循环退出）。

## 外部连接

**Riva gRPC 服务**（src/server/riva_server.cc）：单二进制按模型配置在同端口托管 ASR/TTS/NMT（riva_server.cc:3-4）。三服务各有 `ServiceEnablement` 三态开关，`Auto` 表示"配了模型就开"（riva_server.cc:41-45、146-157）；NMT+ASR 同时启用时调用 `keep_skinny_q8_weights_separate()` 防权重格式互踩（:337-339）。配置优先级 defaults < YAML < env < CLI，env 键为 `NEMO_SPEECH_<KEY>`（:172-173）。ASR+NMT 在场即组装 `SpeechTranslator`，并按有无 TTS 打印级联能力（:411-423）。消息尺寸上限拉到 INT32_MAX 保住离线长音频（:457-461）。

**三个 gRPC 适配器**（src/services/）：`GrpcNmtService` 四个 RPC——`TranslateText`（批量文本，grpc_nmt.cc:123-144）、`ListSupportedLanguagePairs`（按 model_name 分组上报，:146-158）、`StreamingTranslateSpeechToText` 与 `...SpeechToSpeech`。流式 RPC 共用 `drive_audio` 模板：Pcm16StreamDecoder 解码→push→finish，全程响应客户端取消（grpc_nmt.cc:80-108）。S2S 变体要求 ASR+TTS 双在场否则 `FAILED_PRECONDITION`，`utterance_end` 回调发一个空 audio 消息标记句边界（grpc_nmt.cc:245-260 一带）。输入校验钉死 LINEAR_PCM、单声道、8k-96k（grpc_nmt.cc:50-62）。

**HTTP/Realtime 层**（server/http/）：OpenAI 风格路由矩阵——`/v1/audio/transcriptions`（http_server.cpp:642）、`/v1/audio/speech`（:707）、`/v1/audio/translations`（:799）、`/v1/audio/speech/translations`（:864）、`/v1/translations`（:935）、`/v1/diarizations` 与别名（:1001-1002）。实时线两条：`/v1/audio/transcriptions/realtime`（WebSocket 流式转写）与 S2S 专属 `/v1/realtime`+`/realtime`（:1208-1215，挂 `handle_s2s_realtime` 与子协议选择器）。ServerConfig 暴露 `preempt_tts`（新请求取消旧合成，http_server.h:30）、会话时长上限 300s 与 function response 队列上限 64（:33-34）、TLS/API key/CORS（:26-28）。proto 由 vendored riva-common 五个 .proto 生成静态库，双路径解析依赖（config 包 vs NGC 系统库，proto/CMakeLists.txt:2-13）。

## 数据流

文本翻译：texts → `resolve_tag` → 逐条 `acquire` 槽位 → `build_prompt`+分词 → 分块 prefill → 贪心解码至 EOG → ltrim → `Translation{text, 实际目标语}`（translator.cpp:190-218——返回语言取 tag 的目标侧而非原始请求，translator.cpp:199-200 注释）。语音翻译：音频块 → decoder → `SpeechTranslationStream::push` → `drain_finals` 逐 final 级联 → TTS PCM 块回调 → 句边界回调；`finish()` 把尾包 flush 成最后一个 final（speech_translator.cpp:170-176）。

## 设计决策

- **pimpl 隔离 llama**：NMT 作为库被 server 与 SDK 同时链接，头文件污染为零（translator.h:7）。
- **级联而非端到端**：语音翻译走 ASR final→NMT 级联，复用三个独立引擎而非训练联合模型——工程复用优先。
- **优雅停机三部曲**：信号 handler 只写 atomic（async-signal-safe，riva_server.cc:178-184），watcher 线程轮询后调 `Shutdown(10s deadline)`，活动客户端不能无限拖延 SIGTERM（:489-502）；不可恢复类故障（SIGSEGV/SIGFPE）明确不捕获、打印一行后重抛让 systemd/k8s 重启（:191-205）。
- **Auto 启用语义**：默认按模型路径存在与否决定服务面，最小心智负担起一个全功能节点（riva_server.cc:170-171 usage 文案）。

## 新人提示

起服务最小命令见 `print_usage`（riva_server.cc:164-167）：ASR 只要 `--asr.model.path`，TTS 要三件（magpie/codec/tokenizer dir）。想看吞吐瓶颈先加 `nmt.pool.contexts`（每槽一份 KV 缓存，translator.h:50-52）；文档级长输入需同步抬 `n_ctx`（模型上限 8192，translator.h:36）。调试 HTTP 用 `/health`、`/ready`、`/version`、`/v1/models` 四个只读端点（http_server.cpp:502-543）。gRPC 端口默认 50051、HTTP 默认 127.0.0.1:8080（riva_server.cc:217；http_server.h:11）。改 proto 后注意两条依赖路径都要过 CI：Windows vcpkg 与 Linux NGC 镜像（proto/CMakeLists.txt:7-13）。
