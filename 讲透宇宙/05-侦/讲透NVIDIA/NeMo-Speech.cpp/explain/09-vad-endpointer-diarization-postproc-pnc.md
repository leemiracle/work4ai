# 09 · VAD、说话人分离与 ASR 后处理线（L4 · 28 节点群）

## 角色定位

图谱 L4 的 28 节点是 ASR 主链（识别核心在 L3/L11）的"质量层"：音频进入解码器前后，由 VAD 决定哪些帧算语音、diar 决定谁在说话、postproc+pnc 决定文本以什么形态出仓。四个子目录职责分明——`vad/`（Silero 推理 + 特征掩码 + 端点检测三件）、`diar/`（Sortformer v2/v3 流式说话人分离）、`postproc/`（亵渎词过滤 + ITN + 标点大小写的编排链）、`pnc/`（BERT 标点/大写模型）。它们全部可以作为可选组件单独缺席：配置路径为空即禁用（pipeline.h:30-35 的 PostprocConfig 三空即三禁；DiarConfig model_path 空=不可用，diar_pipeline.h:31）。

## 内部结构

**VAD 三件套**：`SileroVad` 是从 whisper.cpp 移植的推理原语（silero_vad.h:5-8）：STFT 前端→4 层 Conv1D 编码器→LSTMCell→sigmoid，每 512 样本（16kHz 下 32ms）产出一个语音概率；超参固化 silero-v6（window 512/context 64/hidden 128，silero_vad.h:28-44）。关键的共享设计：同一个推理实例同时喂两条消费者——`observe_audio()` 完成窗口推理后立即做 onset/offset 滞回二值化（默认 0.5/0.3，silero_vad.h:181-182），把每个 512 样本窗展开到它覆盖的 mel 帧上记 speech bit；`VadMasker` 读它做特征掩码、`VadEndpointer` 读它做 VAD 驱动 EOU，"Nothing is computed twice"（silero_vad.h:131-140 注释）。掩码策略四步：binarize→pad（默认前后各 200ms）→merge（短于 500ms 的静音隙不掩）→mask（帧外填 -16.635 的原始 log-mel 值，归一化前，vad_masker.h:6-19 与 :24-33）。`VadEndpointer` 是尾静音 EOU 策略：默认 token-silence 时间线（无 VAD 模型也能端点），`vad_based=true` 切到 Silero 时间线（vad_endpointer.h:13-19）；到阈值只触发一次、语音前进才重新武装（:42-45），`force()` 复刻 riva 的 force_eou 客户端强推（:49-51），`set_stop_history_eou_ms` 支持逐请求覆盖阈值（:60-61）。

**diar 线**：`SortformerModel` 一张图跑 v2/v3 两代（sortformer_model.h:3-29）——v2 是 NEST pre_encode 8× 深度卷积干 + 17 层 FastConformer 复用 + 18 层 post-LN transformer + sigmoid 头；v3 换成 8× feature stacking + 31 层 pre-LN RoPE Transformer + 8× subpixel Conv1D，输出原生 10ms 概率。流式状态机 `AoscState` 是 NeMo `streaming_update/_compress_spkcache` 的宿主侧移植：每 chunk 重预测整个 [spkcache|fifo|chunk] 拼接，只有 embedding 被持久化（aosc_state.h:3-10）。几何预设钉死四档（aosc_state.h:36-41）：riva_streaming {160,80,20}、riva_offline {312,100,100}、v3_streaming 1.04s 中心 chunk 低延迟档、v3_offline。`DiarStream` 面向长流：概率时间线超 20 分钟触发压缩，只在"全员静音的隙"处切——冻结段+重算尾在全同配置下与全量重算**精确相等**（diar_pipeline.h:168-176）；词级归因用 onset 锚定，因为迟到的标点发射会把 transducer 词 span 拉进下一个说话人的回合（:192-194）。`ChannelBirthGate` 抑制瞬态通道重绘变成新说话人身份（aosc_state.h:55-59）。

**postproc+pnc 线**：`Postprocessor::apply` 的链序钉死为 profanity→ITN→PnC，注释明言"Ordering matches Riva"（pipeline.cpp:333）。profanity 是整词掩码（保留首字符大小写，其余 \*，尾部 ASCII 标点保留，profanity.h:5-19）。ITN 包 Sparrowhawk WFST（tokenize_and_classify.far + verbalize.far 文法目录，itn.h:8-19），CMake 选项默认 OFF 时是纯直通；PIMPL 无条件使用保证 ABI 在有无 `NEMO_SPEECH_WITH_NORM` 间一致（itn.h:38-43）。词时序跨改写投影由 `itn_align` 完成：读 Sparrowhawk 的 Token:/Word: 链接，把"twenty twenty three"三个带时词的跨度合并挂到"2023"一个书面词上（itn_align.h:3-14）。PnC 是 BERT-base 双头模型（768/12 层/12 头，pnc_model.h:22-33），`PncRunner` 用贪心最长匹配 WordPiece 分词（输入已小写无标点，BERT BasicTokenizer 退化为空白切分，wordpiece.h:3-8）跑滑窗 128 token（pnc_runner.h:3-6）。

## 外部连接

上游被 `asr::Recognizer`/runner 持有：SileroVad 由 runner 拥有、VadMasker 借用（vad_masker.h:20-21）；postproc 的过滤/模型在构造时装载一次，逐请求 `AsrRequestOptions` 只开门（pipeline.h:3-5）。PnC 跑在共享 BackendManager 上，Postprocessor 暴露 `pnc_batch_metrics()` 汇入批指标（pipeline.cpp:282-285）。diar 既独立成流（diar_pipeline.h:8 "independently or as an ASR sidecar"）也被 diar_recognizer 组合（tests/cpp/asr/test_diar_recognizer.cpp 对应）。ITN 文法目录支持按语言子目录发现并查重（pipeline.cpp:118-131）。

## 数据流

VAD：样本→`feed_audio` 512 样本窗累积→概率→binarize 滞回→mel 帧 speech bit 时间线→双消费（掩码/端点）；`discard_timeline_before` 让 runner 解码游标过境后丢弃旧帧，长流内存有界（silero_vad.h:156-159）。Diar：样本→mel→就绪 chunk（右上下文齐）→Sortformer 前向→AOSC 更新→原生节奏概率→`diar_segments_from_probs`（pyannote binarize 语义：滞回→边缘 pad→填短隙→删短段，默认值来自 callhome 调参且注释警告数据集敏感，diar_pipeline.h:97-111）。Postproc：final transcript→executor 有界 CPU 线程池（workers 2/queue 64 反压而非无界排队，pipeline.h:34-35）→亵渎掩码（含逐词同步，pipeline.cpp:334-339）→ITN 归一化+对齐重挂词时（:341-349）→回主线程跑 PnC（GPU，:300-302）→标点间距清洗或格式剥除（:305-308）。

## 设计决策

- **一次推理两用**：掩码与端点共享 Silero 时间线，省一半 VAD 前向（silero_vad.h:131-140）。
- **声学模型自标点时跳过 PnC**：`model_self_punctuates=true` 直接忽略 --pnc-model，因为 PnC BERT 为纯文本 CTC 输出设计，叠加会让标点翻倍/错乱（pipeline.h:52-58；构造期 WARNING pipeline.cpp:266-269）。
- **diar 长流压缩的正确性切点**：只在静音隙切，保证与全量重算逐段相等（diar_pipeline.h:168-176）；`hold_frames_from` 让"词定稿才打标"的调用方约束切点（:178-183）。
- **ITN 的 ABI 稳定 PIMPL**：可选依赖不泄漏到头文件布局（itn.h:38-41）。
- **profanity/ITN 在 CPU 池、PnC 在 GPU**：apply 拆 apply_cpu 派发 + 主线程 PnC 两段（pipeline.cpp:294-302）。

## 新人提示

调端点延迟从 `--stop-history-eou-ms` 入手（默认 800ms 对齐 riva，vad_endpointer.h:20）；掩码默认关（vad_masker.h:24），开掩码时 mask_value 是归一化**前**的原始 log-mel 填充值，别与归一化后数值混淆。diar 预设优先于单键覆写，混用不支持（diar_pipeline.h:32-35）；离线 `diarize_offline` 有 5000 帧（约 6.6 分钟）位置编码硬上限，长音频必须走 DiarStream（diar_pipeline.h:83-89）。跑 postproc 计时看 `NEMO_SPEECH_TIMING`（pipeline.cpp:291、316-318）。干净朗读语音想要好 diar 分段，调低 onset 并加大 pad（diar_pipeline.h:102-103 警告）。test_pnc/test_postproc/test_vad/test_endpointer/test_diar_* 五组单测是行为基准。
