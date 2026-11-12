# 05 · MagpieTTS C++ 主体与流式运行时

## 角色定位

src/tts/magpietts/（20 文件）是 MagpieTTS 合成线的 C++ 主体，负责"文本 token 流 → 8 码本音频 token 流 → PCM"的全过程编排。与 ASR 线建在 ggml Module 协议上不同，MagpieTTS 直接持 ggml_tensor* 裸指针自建图（magpietts/model.h:280-299），并在 CUDA 上用持久内核绕开 ggml 图执行（explain/06）；magpietts.cpp（2173 行，全仓第二大文件）承担流式合成主循环，runtime.h 的 MagpieTtsRuntime 是同步 pimpl 门面，synthesizer.h 的 Synthesizer 再包一层 TN→分词→运行时→重采样给服务层。

## 内部结构

**模型层**：magpietts_hparams（magpietts/model.h:44-94）钉死音频词表几何——8 码本×2016 码本、BOS/EOS/mask id、frame_stacking_factor 区分 v2602（vocab 2362×堆叠 1）与 v2607（vocab 3359×堆叠 2，一个解码位预测两连续 codec 帧，magpietts/model.h:96-105）；magpietts_unstack_codes/magpietts_first_eos_lane/magpietts_frames_to_emit（magpietts/model.h:113-155）三函数处理堆叠帧的拆分与 EOS lane 截断。MagpieModel（magpietts/model.h:260-299）从单 GGUF 装载三个 transformer（encoder/decoder/local，magpietts_transformer 在 magpietts/model.h:176-192）+ text/audio embedding + baked_context 烘焙音色（110×768×5 speakers）+ LT 头与逐码本输出投影。MagpieAttentionPriorState（magpietts/model.h:203-223）与 Longform 变体（magpietts/model.h:225-258）维护注意力先验：从交叉注意力对齐分数统计文本侧已读位置（last_attended_），经 update() 平滑成 prior_ 向量，作为后续解码步交叉注意力的 softmax 偏置——TTS 没有显式对齐器，这是让音频进度跟上文本的机制。MagpiePinnedHostScratch（magpietts/model.h:303-334）提供 cudaHostAlloc 暂存，magpietts_should_stage_pinned 决定何时走 staged 上传（magpietts/model.h:328-334）。

**流式主循环**（magpietts.cpp）：入口 stream_magpie_to_audio（magpietts.cpp:1130）。请求级设置：hparams 按请求覆写一份副本（:1137 注释：模型跨请求共享、覆写只落副本）；speaker 越界与码本数不匹配硬校验（:1146-1155）；stateful codec 模式下历史/未来帧归零（:1172-1179）；LT/采样后端解析——cuda LT 必须配 cuda 采样，cpu LT 配 cuda 采样直接拒绝（:1184-1203）。工作区：MagpieStreamingRuntime::Impl（:345）管理 workspace.beginRequest + localSampler + prewarmLocalTransformer（:1241-1252）；MagpieDecoder/MagpieEncoder/双 KV cache（cond/uncond + cross）从 workspace 取（:1254-1264）。后台线程 codec_stream_worker 在 :1272 构造并 start。

**codec_stream_worker**（magpietts.cpp:793-928）：经典三条件变量生产者-消费者——has_work/has_room/first_audio（:811-814）。write_frame 阻塞等待缓冲低于 max_buffered_frames（queue_depth×chunk_size+history+future+1，:843-845）；wait_first_audio（:877-883）阻塞生产者直到首块音频解码完成——注释写明目的：防一个占满 GPU 的解码步推迟首音频，TTFA 直接受益；eos_frame() 返回硬编码 8 码本 token 串 {621,1455,1184,1038,463,377,1536,1742}（:885-896），finish_tokens 补 future_size 个 EOS 帧冲刷流水（:911-919）。

**解码主循环要点**：forbid_eos 在生成帧数不足 min_generated_frames 前禁 EOS（:1626）；采样可走 cuda_sample（:1710-1733）或 CPU rng（:1832-1839）；EOS 判定找最早命中 audio_eos_id 的 lane（:1885-1888，magpietts_first_eos_lane），非最终 chunk 的 EOS 推迟——"attention 未达 chunk 末尾前 EOS 无效"（:1893-1924 的对齐守护）；首帧后 wait_first_audio（:1936-1940）。**长文本 chunk_prefetch**（:1305-1397）：chunk k 生成时旁路线程并行跑 chunk k+1 的编码器/cross-KV/烘焙上下文 prefill；唯一未知量是文本历史长度（取决于注意力先验停在哪），用默认窗投机生成、边界校验失配即回退同步路径（chunk_prefetch_state 注释 :1305-1317）。

**指标**：stream_run_metrics（magpietts.h:98-128）双轨——decoder/codec/e2e 三个 stream_latency_metrics（magpietts.h:76-96，事件间延迟分位数 p95/p99）+ ttfa/rtfx 计数；magpie_pcm_callback（magpietts.h:130）是音频块回调出口。对外 C 风格包装 magpie_stream_runtime_*（magpietts.h:167-177）供 C ABI 使用。

## 外部连接

上游：Synthesizer（synthesizer.h）在 prepare 阶段做 TN+Sparrowhawk、MagpieTokenizer 分词（多语言 profile 见 explain 系 tokenizer 主题）后把 token chunk 喂进来；EngineRegistry::load_tts 装载后 warmup（engine_registry.cpp:77 调 keep_cuda_graphs_resident——逐帧图必须驻留）。下游：NanoCodec 解码（codec_stream_worker 内嵌 nc::NanoCodecModel/Decoder 引用，:794-799）；audio_pp 后处理（重采样/Hann 窗整形）。平行组件：decoder.cpp/encoder.cpp/lt.cpp 是 ggml 图路径的 C++ 实现（magpietts/lt.cpp:55 LocalTransformerGraph、:87 GraphBank），与 explain/06 的 CUDA 持久内核互为回退——magpietts_resolve_lt_backend（magpietts/model.h:436-440）决定走哪条。runtime.h 的 MagpieRuntimeConfig/MagpieSynthesisStats（magpietts/runtime.h:31、:75）服务同步单发。

## 数据流

请求进入：tokens（或 text 经分词）→ stream_magpie_to_audio：文本编码器一次性出 memory → 逐帧解码器步（CFG 双 lane：cond/uncond hidden、KV、cross-KV 各一份）→ LT 环节把 decoder hidden 变成 8 码本 logits → 采样（CFG 公式合并双 lane、top-k、温度、EOS 禁令）→ 堆叠帧拆分 → write_frame 入队 → worker 线程按 chunk_size 凑块 → NanoCodec 逐帧解码出 1024 样本/帧 @22.05kHz → audio_pp 窗整形 → pcm_callback 外送。注意力先验每步 update：对齐分数回读（completeAlignment 延迟取回与采样重叠，magpietts/model.h:196-200）→ prior 平滑 → 下一步交叉注意力 bias。EOS lane 命中即收尾：finish_tokens 补 EOS、worker 冲刷、metrics.finish。

## 设计决策

①生产者-消费者而非全流水 GPU：解码步占 GPU 时 codec 块可在 CPU/另一流并行，wait_first_audio 只在首块前挡一次。②CFG 双 lane 共享位置/编码 memory，只分叉 KV 与 hidden——省一半编码成本。③EOS 的对齐守护：非最终 chunk 的 EOS 被忽略到注意力真达 chunk 末——防先验滞后造成的提前截断。④hparams 请求级副本：模型常驻共享，温度/top_k/步数按请求覆写零锁。⑤投机 prefetch + 校验回退：长文本首字延迟摊平，正确性靠边界校验兜底。⑥注意力先验状态机（含 Longform 跨 chunk 绝对坐标）：无对齐器 TTS 的核心可解释机制。

## 新人提示

阅读顺序：magpietts.h 参数与指标结构 → magpietts/model.h:44-105 的 hparams/profile → magpietts.cpp:1130 起的主循环（对照 verbose 日志格式 :1218-1237 读每个字段）→ codec_stream_worker（:793-928）看三条件变量。调试：MAGPIETTS_LOGIT_DUMP/MAGPIETTS_FORCE_CODES 两个 env 可注入确定性码本帧做回归（:1211-1216）；metrics 的 ttfa_ms 与 inter_chunk_p95 是流式健康主指标。坑：v2602/v2607 两代 profile 的帧堆叠语义不同，堆叠拆分错了症状是音频时快时慢；use_stateful_codec 与 codec_history_frames 互斥（:1174-1179）；EOS token 串是硬编码的，换新 codec 词表要先核对 :886。
