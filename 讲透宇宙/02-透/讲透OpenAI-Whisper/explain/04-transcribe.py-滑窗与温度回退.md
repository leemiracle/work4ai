# 04 · transcribe.py：30 秒滑窗主循环与温度回退

## 角色定位

transcribe.py（623 行）是**产品层编排中枢**：用户调用的 `model.transcribe()` 与 CLI `whisper` 命令都落在这一文件。它不发明新的模型能力，而是回答一个工程问题——"一个只能看 30 秒、只输出到 4484 token 上限的模型，如何正确转写一小时音频？"答案由三件事组成：滑窗推进（seek 循环）、失败重试（温度阶梯）、幻觉防御（三阈值 + 静音跳过）。束搜索/贪心等单窗策略本体在 decoding.py（任务书把 beam 归到此篇，实际边界是：transcribe 只做**逐窗调度**，beam_size 经 `**decode_options` 透传给 DecodingOptions，whisper/transcribe.py:55 与 whisper/transcribe.py:200-201）。

## 内部结构

**transcribe() 主函数（whisper/transcribe.py:38-514）**按执行顺序分六块：

1. **环境准备**：CPU 上 fp16 降级 fp32 并告警（whisper/transcribe.py:128-133）；整段音频一次算成大 mel 谱并垫 30s 零（whisper/transcribe.py:139），`content_frames = mel.shape[-1] - N_FRAMES` 记录真实语音帧数（whisper/transcribe.py:140-141）；语言未指定时用前 30 秒做一次 `model.detect_language`（whisper/transcribe.py:151-153）。
2. **clip 与 prompt 预备**：clip_timestamps 字符串解析成 seek_clips 剪辑区间对（whisper/transcribe.py:168-177）；initial_prompt 编码进 all_tokens 并扣减 prompt 预算（whisper/transcribe.py:239-244，上限 n_text_ctx//2-1）。
3. **decode_with_fallback 闭包（whisper/transcribe.py:184-224）**——温度回退心脏：沿 `temperature` 元组逐档尝试（默认 (0.0,0.2,0.4,0.6,0.8,1.0)，whisper/transcribe.py:43）；t=0 时禁 best_of、t>0 时禁 beam_size 与 patience（whisper/transcribe.py:192-198，因束搜索在采样温度下无意义）；每档算完按三条件判 `needs_fallback`——压缩率超 2.4 判重复（whisper/transcribe.py:204-208）、avg_logprob 低于 -1.0 判低质（whisper/transcribe.py:209-213）、no_speech 高 **且** logprob 低则视为静音**不再回退**（whisper/transcribe.py:214-220）——静音不是失败，重试只会更糟。
4. **seek 主循环（whisper/transcribe.py:272-508）**：注释自陈"obscure flattened loop"（whisper/transcribe.py:268-271，双循环压成单层求 diff 可读）。每轮：切片 mel、pad_or_trim 到 3000 帧（whisper/transcribe.py:283-286）；组 prompt（上一窗输出 or initial_prompt，whisper/transcribe.py:288-293）；调 decode_with_fallback（whisper/transcribe.py:295）；静音跳窗判定（no_speech 高且 logprob 不高 → seek += segment_size 直接翻页，whisper/transcribe.py:298-310）。
5. **时间戳切分与 seek 推进**：检测相邻时间戳 token 对（whisper/transcribe.py:339-343 的位运算：`tokens.ge(timestamp_begin)` 布尔序列找连续 True）；有配对时间戳则按对切片成 segment（whisper/transcribe.py:344-367）；末尾单时间戳=尾部无语音 → seek += segment_size 整窗翻页（whisper/transcribe.py:369-371），否则 seek 跳到最后一个时间戳位置（`last_timestamp_pos * input_stride`，whisper/transcribe.py:374-377）——**这就是"信任模型自吐时间戳"的滑窗机制：语音 4.87 秒就跳 4.87 秒，绝不重叠也不空转**。无配对时间戳的退化路径用最后一个时间戳估时长（whisper/transcribe.py:378-399）。
6. **词级分支与收尾**：word_timestamps=True 时调 add_word_timestamps（whisper/transcribe.py:401-411）并用词尾时间精化 seek（whisper/transcribe.py:413-416）；hallucination_silence_threshold 启用时执行三层幻觉静音跳过启发式（whisper/transcribe.py:419-472：首段异常跳前导静音、被静音包围的异常段整体跳过，判据 `word_anomaly_score` 以概率<0.15、时长<0.133s 或>2s 计分，whisper/transcribe.py:316-334）；瞬时/空文本 segment 清空（whisper/transcribe.py:484-489）；温度>0.5 的窗口不作为下窗 prompt（whisper/transcribe.py:503-505，防高温噪声污染上下文）；最后拼 `{"text", "segments", "language"}` 返回（whisper/transcribe.py:510-514）。

**cli()（whisper/transcribe.py:517-619）**：40+ 个 argparse 参数；默认模型 turbo（whisper/transcribe.py:530）；`.en` 模型配非英文语言参数强制改 en（whisper/transcribe.py:577-582）；`--temperature_increment_on_fallback` 把标量温度展开成阶梯元组 `np.arange(t, 1.0+1e-6, increment)`（whisper/transcribe.py:584-588）；逐文件转写-写出、异常捕获后跳下一个文件（whisper/transcribe.py:613-619）。

## 外部连接

- 上游：`Whisper.transcribe = transcribe_function`（whisper/model.py:351）；CLI 三行入口 whisper/__main__.py:1-3。
- 依赖 audio.py 的五个常量与两个函数（whisper/transcribe.py:11-19）——`input_stride = N_FRAMES / n_audio_ctx = 2`、`time_precision = 0.02s` 全由此来（whisper/transcribe.py:228-233）。
- 依赖 decoding.py 的 DecodingOptions/DecodingResult（whisper/transcribe.py:20）与 timing.py 的 add_word_timestamps（whisper/transcribe.py:21）；utils 的 get_writer/make_safe/format_timestamp（whisper/transcribe.py:23-32）。
- 下游：cli 把 result 交给 writer（whisper/transcribe.py:597,616）；测试用 jfk.flac 端到端断言（tests/test_transcribe.py:11-42）。

## 数据流（2 小时会议录音）

```
mel (80, 720000+)                                    whisper/transcribe.py:139
└─ 窗1 [0:3000] → decode T=0 beam5 → "…<|27.4|>"
   ├─ segments 切出 6 段；seek=27.4s×50=1370 帧       whisper/transcribe.py:374-377
   └─ prompt=窗1 tokens（condition_on_previous_text） whisper/transcribe.py:293
└─ 窗2 [1370:4370] → 压缩率 3.1>2.4 → needs_fallback
   └─ T=0.2 重解 → 2.0 ✓ 接受（记录 temperature）      whisper/transcribe.py:190-222
└─ 窗N 全静音 → no_speech 0.91、logprob -1.4
   └─ should_skip=True → seek += segment_size 翻页     whisper/transcribe.py:298-310
└─ seek ≥ content_frames 循环结束 → 6 格式落盘         whisper/transcribe.py:616
```

## 设计决策

1. **时间戳驱动滑窗优于固定步长**：窗口边界由语音内容决定，静音自动快进，代价是模型时间戳漂移会累积——所以才有 word_timestamps 下的 seek 精化（whisper/transcribe.py:413-416）双保险。
2. **温度回退是"保底重采样"而非解码策略**：失败判定全部基于事后统计量（压缩率/logprob），简单、可解释、无需额外模型；静音特判（whisper/transcribe.py:214-220）避免对无解窗口无限重试。
3. **prompt 条件化的取舍**：条件化提升跨窗一致性但会传播错误循环（docstring 明言，whisper/transcribe.py:86-89），于是高温窗口自动切断 prompt（whisper/transcribe.py:503-505）。
4. **幻觉静音跳过只做减法**：检测到疑似幻觉就跳过静音区间重来（whisper/transcribe.py:419-472），不试图"修复"文本——宁缺毋滥。
5. **扁平化循环换取可 diff 性**：whisper/transcribe.py:268-271 的注释坦承这是权宜，新人别学。

## 新人提示

- 长音频转写质量差时先看三件事：日志里的 temperature 是否一路升到 1.0（源窗口有问题）、compression_ratio 是否贴 2.4（重复幻觉）、condition_on_previous_text 试着关掉（whisper/transcribe.py:47 参数）。
- `--word_timestamps True` 是最重的可选功能（每窗多一次前向+DTW），纯文本转写别开。
- prompt 机制：initial_prompt 只影响首窗；要全程序贯用 carry_initial_prompt（whisper/transcribe.py:288-291），但它会挤占上下文预算。
- 调 seek 逻辑时打印 `time_offset/segment_size/last_timestamp_pos` 三元组（whisper/transcribe.py:281-285,374-377），比读代码快。

## 勘误

1. **任务书把 beam 归入 transcribe 篇**：beam search 本体在 whisper/decoding.py:301-404，transcribe 仅透传参数；本篇按源码边界重划。
2. transcribe.py:179 的模块级 `punctuation` 串与 prepend/append_punctuations 参数默认值（whisper/transcribe.py:51-52）近似重复但**硬编码不联动**——自定义标点参数时，幻觉判定的标点集不变，属隐性配置漂移。
3. docstring 称压缩率为 "gzip compression ratio"（whisper/transcribe.py:76-77），实现是 zlib（whisper/utils.py:45-47）——gzip 仅是 deflate 的容器包装，比率近似，文档措辞漂移。
4. 静音判定双实现语义微差：decode_with_fallback 里 no_speech 高+logprob 低 → 不回退（whisper/transcribe.py:214-220）；主循环里 no_speech 高+logprob **不低** → 不跳窗（whisper/transcribe.py:301-306）。两处条件方向相反但目的一致（"logprob 高就信文本"），读代码时极易混淆。
