# 07 · S2S VoiceChat 流水线与神经编解码器（L8 · 32 节点群）

## 角色定位

`src/s2s/` 是全仓最重的子系统：speech-to-speech（S2S）全双工语音对话的 C++ 编排层，把感知、LLM、TTS、神经编解码四类引擎捏进一个 80ms 节拍的实时循环。图谱 L8 层 32 个节点恰好覆盖四条子目录线（`codec/` 8、`eartts/` 10、`llm/` 5、`perception/` 2）加顶层 `pipeline.*` 与 `voicechat.*`。定位上它是"编排者而非算子"：真正的张量计算分别下沉到 ggml Session（perception/codec/heads）、llama.cpp 序列（两个 backbone）与原生 batched RNNT 引擎（perception.h:14-16 复用 `asr::RnntModel`）。对外只暴露两个门面——`VoiceChat`（voicechat.h）给 server/http 与示例用，`S2SPipeline::process_chunk()`（pipeline.cpp:1591）是唯一的推进原语：一次调用消费 160ms 音频（2 步 × 80ms），返回文本增量、ASR 增量、工具调用 JSON 与 22050Hz 音频（pipeline.h:85-91 `S2SChunkResult`）。

## 内部结构

七件 GGUF 资产在 `voicechat_config_from_model_dir()` 集中装配（voicechat.cpp:26-33）：`perception.gguf`、`nano-v2-vllm/nano-v2-llm.gguf`（NemotronH 9B，n_embd=4480，llm/backbone.h:3 与 :33）、`llm_aux.gguf`（嵌入表+函数头，Q8_0，heads.h:3-5）、`eartts_vllm/` 三件（Gemma3 backbone n_embd=1152 + side 网络 + prompt）、`codec.gguf`、`rnnt_tokenizer/vocab.json`。引擎构造顺序见 pipeline.cpp:598-607；side 网络约 500MB 由 embedder 与 sampler 共享一个 loader（pipeline.cpp:602-605）。

编解码器三件套在 `codec/`：`CodecConfig::from_gguf` 读超参（rates {7,7,9}、stage_channels {384,768,1536}、samples_per_frame=1764，config.h:25-32）。`S2SCodec::decode_wav()`（codec.cpp:94）做流式 codes→wav：codes 从 (T,Q) 行主序重排为 q-major（codec.cpp:107-110），decoder 上采样各级的因果卷积尾缓存按 stage 逆序分配（codec.cpp:43-48），STFT overlap 的 re/im tail 跨调用续接（codec.cpp:135-136），输出回写新缓存（codec.cpp:162-164）。窗口合成包络的倒数向量按 n_frames 缓存避免重算（codec.cpp:61-91 + envelope_cache_:71）。`compute_silence_codes()`（codec.cpp:169）复刻 model.py：对 10 帧全零频谱跑 encoder，取最常见 31 元组（codec.cpp:200-215）——Q=31 个量化器，这是 TTS EOS 静音替换的种子。

EarTTS 的 CFG 结构藏在 backbone.h:4-8 注释里：每逻辑流占 cond+uncond 两个 llama seq 槽，KV 池预留 2×(max_streams+1) 个 4500 位置槽位。`allocate_pair()` 必须分配连续升序对——llama.cpp 的 `split_equal(sequential=true)` 只有 `seq_id[1]==seq_id[0]+1` 时才把两个 CFG token 留在同一 ubatch，否则子图节点跨调用重排会毁掉 CUDA graph 预热（backbone.h:44-52）。

## 外部连接

向内依赖 `runtime.h`（ggml Session/GGUFLoader/BackendManager）、llama.cpp（双 backbone）、`asr::` 的 RNNT 引擎与 `IngressBatchCoordinator`（pipeline.h:258）。向外：`VoiceChat` 被 server/http 的 s2s_realtime 端点消费；perception 复用 ASR 主线的 FastConformer 批处理设施（perception.h:18-21 构造签名带 `asr::BatchingConfig`）。表头注释声明 S2S frontend 刻意关闭归一化（perception.h:4-5）——同一张 FastConformer 图扇出两路：voicechat 投影（喂 LLM hidden）与 RNNT joint 编码投影（喂原生解码器）。

## 数据流

`process_chunk()` 的骨架（pipeline.cpp:1591-1747）：①工具快路径门——extract/inject 期间直接返回静音帧（:1611-1615）；②实时性门——音频不足 min_samples 则 skipped（:1636-1642）；③ingress cohort——所有微批器对齐同一波到达而非各付定时器（:1644-1653）；④桶化窗口——尾部音频向上 pad 到 16000/32000/56000/89600 四档之一（:1663-1669），把 perception 的输入形状钉死在 4 种，避免每 chunk 触发全图重建+预热的多秒停顿（:1655-1659 注释）；⑤每步序：LLM→RNN-T EOU 证据→turn-token 纠正→RNN-T display→TTS（:1704-1706），保证 TTS 在同一 80ms 帧内看到 RNN-T 注入的 BOS/EOS。turn-taking 是状态机重写器：静音满 `rnnt_eos_silence_frames` 强制写 BOS（:1244-1254）、说话中再遇 BOS 改写成 EOS 并强制静音（:1212-1216）、barge-in/比例上限/绝对上限三条刹车（:1266-1294），且新回合一律 `reset_tts_for_turn()` 把 TTS 槽位克隆回不可变语音提示的 KV 态（:1190-1200）。

## 设计决策

- **双 RNN-T 预测器分权**：每会话两个独立 predictor，一个管轮次证据（eou），一个管用户可见转写（display）（pipeline.h:135-139；批槽位因此 ×2，pipeline.cpp:594-596）。
- **bf16_round 对齐参考数值**：prefill 嵌入叠加后逐元素 bf16 舍入（pipeline.cpp:800-807），感知输出整向量舍入（pipeline.cpp:1693），为的是与 PyTorch 参考实现位级可比。
- **系统提示拼两份**：`prefill_system_prompt` 把剥掉 `<TOOL_ACK_MESSAGES>` 的提示复制两遍（pipeline.cpp:785-792），ack 消息解析为工具名→话术表（:764-783）。
- **大量环境变量覆写**（LLM_TOP_P/RNNT_*，pipeline.cpp:548-585）——调参不重编译。
- **warmup 显式化**：空音频会话跑遍四个桶触发 per-shape graph capture 与 cuDNN JIT（pipeline.h:198-201），`VoiceChat::warmup` 用 `call_once` 保证（voicechat.cpp:88-90）。

## 新人提示

读码顺序建议 pipeline.h（全部状态一眼看全）→ process_chunk → apply_rnnt_turn_taking → codec.cpp。两个易踩点：`S2SCodec::decode_wav` 被 `streams_mutex_` 全程序列化（codec.cpp:96-99，当前 codec 图是 scalar-stream，其余神经阶段仍可并发批处理）——别在此处加并发；`max_steps` 上限会被钳到 EarTTS 位置容量（pipeline.h:46），`steps_exhausted` 后再调用直接抛异常（pipeline.cpp:1607-1608）。调试用 `S2S_DEBUG_TIMING` 环境变量打开分段计时（:1593、:1740-1742）。函数调用是异步快路径线程（pipeline.h:169-173 的六个 FnState），主循环靠原子标志门控，改状态机时先读 `maybe_start_fast_paths`（pipeline.cpp:1506）与 `end_stream` 的取消序（pipeline.cpp:819-822）。
