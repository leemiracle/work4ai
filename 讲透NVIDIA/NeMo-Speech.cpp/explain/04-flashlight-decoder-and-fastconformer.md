# 04 · flashlight_decoder + FastConformer 族：KenLM 重打分与编码器主干

## 角色定位

src/asr/decoders/flashlight_decoder.cpp（570 行）是流式 CTC 的 LM 重打分解码器：在贪心 argmax 之上引入 flashlight-text 的 LexiconDecoder（词典 trie+KenLM），把"声学最优"校正为"语言最优"，并承接词级热词偏置。src/asr/encoder/ 是 FastConformer 主干族（相对位置注意力/RoPE 变体/cache-aware 流式几何），四个解码器实现全部消费它的编码输出。一个管"读得准"，一个管"听得懂"。

## 内部结构

**FlashlightResources**（flashlight_decoder.h:70-105）是不可变资源束：token_dict/word_dict/KenLM/trie/lexicon，跨流共享（recognizer.h:182-183）。构造（flashlight_decoder.cpp:157-197）：token_dict 按 GGUF vocab 建索引、blank 追加（flashlight_decoder.cpp:163-172）；loadWords 装词典（:174-178）；KenLM 装载后取 <unk> unigram 作 oov_lm_score（:187-190）；build_lexicon_trie 打 KenLM 分插 trie 再 MAX smear（:104-154）。**词不匹配自检**：token piece 不在模型 vocab 的词典条目被丢弃，丢弃率 ≥2% 即告警 lexicon/tokenizer 与模型不匹配（flashlight_decoder.cpp:141-151）——静默 WER 退化变加载期可见。**clone_for_mutation**（flashlight_decoder.cpp:199-205）只深拷 word_dict 重建 trie，KenLM/token_dict/lexicon 共享——OOV 增词不触发 ~700MB KenLM 重载（:242-246 注释）。

**BoostedLm**（flashlight_decoder.cpp:48-86）装饰器包 KenLM：in-vocab=KenLM 分数+boost（:70-74）；OOV（idx ≥ base_word_count，不在 KenLM vocab map，硬查越界）=<unk> unigram+boost 且不改上下文（:65-69）——boost 量纲对两类词一致。

**FlashlightDecoder**（flashlight_decoder.h:107-234）：flashlight_decoder.cpp:212-223 构造时 adopt_resources + build_decoder（LexiconDecoderOptions 全套 beam 参数，flashlight_decoder.cpp:254-273）。reset_utterance 保 last_emit_frame 跨句（flashlight_decoder.h:121-125——端点静音时间线跨 utterance）。step()（flashlight_decoder.cpp:432-477）：首 chunk 记 seg_global_start_frame_（:441-442）→ decodeStep 喂 T 帧 → track_speech_frame_ 每帧 argmax 维护 last_emit_frame_（:452-462，token-silence 端点唯一信号——beam 在 commit 时刻发词）→ seg_frames_ 触 max_segment_frames（1500 帧≈2min，flashlight_decoder.h:57-62）即 commit_segment → getBestHypothesis 拼 partial_。commit_segment（:479-494）decodeEnd/decodeBegin 重启 beam 并把最优假设并进 committed_words_；finalize（:497-505）同构；extract_timings（:508-531）用 DecodeResult per-frame words/tokens 换算词时序，零二次对齐。

**set_request_options 的热词双路径**（flashlight_decoder.cpp:275-415）：boost 先夹到 ±max_boost（flashlight_decoder.cpp:341-351，防 beam 内重复发射）→ in-vocab 只记 boost map 不动资源（flashlight_decoder.cpp:371-373）→ OOV 经内嵌 SentencePiece 编码 token pieces（GGUF 内嵌 tokenizer 保证与模型 vocab 匹配；flashlight_decoder.cpp:282-322）→ ensure_private_resources 克隆资源束（flashlight_decoder.cpp:238-252）→ word_dict_->addEntry + trie_->insert（flashlight_decoder.cpp:395-400，叶分数=oov_lm_score_）→ 重 smear（flashlight_decoder.cpp:410）→ BoostedLm 包装重建 beam（flashlight_decoder.cpp:412-414）。防御：kMaxBoostWords=256 上限（flashlight_decoder.cpp:329）、kMaxOovTokens=40、spm 失败一次性告警。

**FastConformer 族**（fastconformer.h）：EncoderConfig（fastconformer.h:42-106）参数化离线与流式几何——ConvNorm/ConvContext/CacheMode 三枚举区分 Parakeet（BatchNorm+对称卷）与 Nemotron cache-aware（LayerNorm+因果卷，fastconformer.h:27-40）；cache_right_ctx=R 与 cache_chunk_frames=1+R 是训练钉死的延迟档位（fastconformer.h:64-68）；cache_drop_extra 剥 chunk 与前块尾重叠（fastconformer.h:70-74）；子采样 8× 三级 conv（fastconformer.h:91-105）。LayerCacheIO（fastconformer.h:122-164）是每层缓存契约：K/V/conv 指针之外还有 CUDA 融合路径的 kv_cache_arena+slot_ids+ring_heads（fastconformer.h:140-143）、chunk 不变 pos_proj 预投影（fastconformer.h:151）、channel-inner 重排深度卷积权重 dw_conv_w_ct（fastconformer.h:157）。ConformerLayer（fastconformer.h:276-316）标准 macaron 结构，缓存版 MHA 走 build_mha_cached（fastconformer.h:313）。FastConformerEncoder（fastconformer.h:337-410）持 per-layer KV/conv cache arena 命名（fastconformer.h:375-377）与一次性预计算触发键 kPrecomputeTrigger（fastconformer.h:392）。planar_q8_weight_load_hook（fastconformer.h:319-327）实现 tensor-planar Q8 契约：非 CUDA 缓冲直接拒绝。Sortformer/NEST 的 split 入口 build_pre_encode/build_graph_from_embeddings（fastconformer.h:348-366）对应 NeMo pre_encode+bypass 语义。

## 外部连接

上游：BufferedStreamRunner/OfflineRunner 喂 (n_classes,T) 的 CTC log-probs（decoder.h 17 方法契约）；词时序/last_emit_frame 被 endpointer 与 diar 消费。依赖：third_party 的 kenlm/flashlight-text（LGPL KenLM 经 cmake/kenlm_runtime.cmake 成可替换运行时，getopt.c 因 AT&T 许可证被排除）；SentencePiece 来自 GGUF 内嵌（src/asr/model.h:92-94）。FastConformer 被 CtcModel/RnntModel/Sortformer 复用；CacheAwareEncoder（cache_aware_encoder.h:23）是 CacheStreamRunner 的编码器驱动。

## 数据流

每步：runner 下载 CTC log-probs → decodeStep 喂 beam（trie 收敛 token、KenLM 在词完成时打分）→ partial_=committed_words_+当前最优 → 端点/上限触发 commit_segment 定型 → detokenize_word_ids 拼文本（跳 <unk>）。编码侧：mel → SubSampling 8× → ×pos_enc → N 层 ConformerLayer（缓存版 K/V 拼缓存、深度卷积吃 kernel-1 状态、图末回写 *_cache_next）→ joint 投影。热词：speech_contexts → in-vocab 记 map / OOV 克隆+插 trie → BoostedLm 重建 beam。

## 设计决策

①共享不可变+私有可变：~700MB KenLM 全进程一份，OOV 增词才付克隆代价。②unigram 对称校准使 boost 语义跨两类可比。③beam 连续喂不按静音切段（riva 同款）：LM 上下文跨停顿对 WER 重要，内存靠 max_segment_frames 后盾。④时间戳复用 DecodeResult 向量，零额外对齐。⑤lexicon 丢弃率自检把错配变成加载告警。⑥pos_proj/dw_ct 预计算：chunk 不变量移出每步图。

## 新人提示

读 flashlight 先看 flashlight_decoder.h:70-105 资源束注释，再顺 set_request_options（flashlight_decoder.cpp:275-415）走热词全路径；调 WER 先确认 lexicon 丢弃率告警。FastConformer 入口是 fastconformer.h:42-106 的 EncoderConfig——三枚举+cache 几何公式都在；延迟档位由 GGUF 钉死，rnnt_right_context=-1 用训练默认。测试：tests/cpp/asr/test_decoders.cpp（828 行无模型）与 test_cache_stream_geometry.cpp 是几何契约活文档。注意 blank_id=vocab.size()（parakeet-ctc 约定）与 sil_token="▁"（flashlight_decoder.h:64-67）。
