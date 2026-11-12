# Whisper 新人导航（ONBOARDING）

> 仓库：openai/whisper @ 86098128（版本 `20250625`，whisper/version.py:1）｜图谱 130 节点/306 边
> 定位：论文《Robust Speech Recognition via Large-Scale Weak Supervision》官方 PyTorch 推理实现——编码器-解码器 Transformer 做多语言 ASR 与 X→英翻译，无训练代码。

## 1. 一图流总览

```
音频文件（任意格式）
  │ whisper/audio.py:25  load_audio：ffmpeg 子进程 → 16kHz mono float32
  ▼
波形（480000 样本/30s）
  │ whisper/audio.py:110 log_mel_spectrogram：STFT(400)→mel(80)→log 归一
  ▼
log-Mel 谱 (80, 3000)
  │ whisper/model.py:181 AudioEncoder：卷积降采样+正弦位置编码+自注意力栈
  ▼
音频特征 (1500, d)
  │ whisper/model.py:214 TextDecoder：因果自注意力+交叉注意力
  ▼
logits（vocab=51865）
  │ whisper/decoding.py:508 DecodingTask：掩码→贪心/束搜索→选优
  ▼
token 序列（夹 <|0.00|> 时间戳标记）
  │ whisper/transcribe.py:38 transcribe：30s 滑窗+温度回退+幻觉防御
  ▼
{text, segments, language} ── whisper/utils.py:306 get_writer → 六种字幕格式
```

分工口诀：audio 管前端、model 管网络、tokenizer 管词表、decoding 管单窗生成、transcribe 管长音频编排、timing 管词级时间戳、utils 管落盘；normalizers 管评测归一化，与推理链路零耦合（whisper/normalizers/__init__.py:1 仅 re-export）。

## 2. 技术栈与依赖

依赖矩阵极简（pyproject.toml:26-34）：torch、numpy、numba（CPU 侧 DTW JIT，whisper/timing.py:57,82）、tiktoken（BPE 内核，whisper/tokenizer.py:8）、triton（CUDA kernel，仅 x86_64 Linux 条件依赖，pyproject.toml:33；whisper/triton_ops.py:6-10）、more-itertools。两个外部契约：ffmpeg 必须在 PATH（whisper/audio.py:42-43）；mel 滤波器组是离线资产（whisper/audio.py:97-101），运行时不需要 librosa。

## 3. 目录地图

```
whisper/__init__.py    包入口兼模型仓库：14 个 checkpoint URL+SHA256（17-51 行）与 load_model
whisper/__main__.py    python -m whisper 三行入口
whisper/audio.py       ffmpeg 解码/pad_or_trim/log-Mel；硬编码超参 13-22 行
whisper/model.py       AudioEncoder+TextDecoder+Whisper（论文 Figure 1）
whisper/tokenizer.py   100 语种表 + tiktoken 封装 + 中文切词
whisper/decoding.py    826 行最大：DecodingTask 策略引擎
whisper/transcribe.py  滑窗编排 transcribe() + CLI（517 行起）
whisper/timing.py      交叉注意力 QK → DTW 词级时间戳（论文 3.6 节）
whisper/triton_ops.py  DTW/中值滤波 CUDA kernel
whisper/utils.py       六格式 writer 与小工具
whisper/normalizers/   评测归一化（推理链路零消费）
whisper/assets/        两份 BPE 词表 + mel_filters.npz
tests/                 六测试 + jfk.flac；seed42（conftest.py:11-15）
notebooks/ data/       评测 notebook 与标注
```

## 4. 核心链路：音频 → mel → 模型 → 解码 → 转写文本

**前端契约**：超参硬编码于 whisper/audio.py:13-22——16kHz、N_FFT=400、HOP_LENGTH=160、30s=480000 样本=3000 帧；编码器第二层卷积 stride=2（whisper/model.py:187）故 **2 帧 mel=1 音频 token=0.02 秒**（whisper/audio.py:20-22，whisper/transcribe.py:228-233 据此得 time_precision）。改任何数都与预训练权重失配。

**模型**：`Whisper`（whisper/model.py:259）按 `ModelDimensions`（whisper/model.py:25-36）装配。编码器卷积后接正弦位置编码（whisper/model.py:62-68）；解码器上三角 -inf 因果掩码（whisper/model.py:231），输出层与嵌入权重绑定（whisper/model.py:252-254）。LayerNorm/Linear/Conv1d 三个子类把权重 cast 到输入 dtype（whisper/model.py:39-59），是 fp16 兼容关键。

**单窗解码**：全在 `DecodingTask.run`（whisper/decoding.py:712）。`_get_initial_tokens`（whisper/decoding.py:587）拼 `[sot_prev? prompt…, sot, 语言token, 任务token]`；`_main_loop`（whisper/decoding.py:680）逐步前向、应用掩码、交给 GreedyDecoder（whisper/decoding.py:272）或 BeamSearchDecoder（whisper/decoding.py:301）；MaximumLikelihoodRanker 选优（whisper/decoding.py:190）。KV 缓存靠 forward hook（whisper/model.py:317-348），束搜索按幸存 beam 重排（whisper/decoding.py:172-176）。

**长音频编排**：`transcribe()`（whisper/transcribe.py:38）把整段算成一张大 mel（whisper/transcribe.py:139），30s 窗口滑动，seek 推进**信任模型自吐的时间戳 token**（whisper/transcribe.py:371-377）——长音频不重不漏的核心机制。每窗失败沿温度阶梯重试（whisper/transcribe.py:43,184-224）。

## 5. 关键设计决策

1. **时间戳进词表**：1501 个 `<|0.00|>`~`<|30.00|>` 作为特殊 token（whisper/tokenizer.py:350），分段成为生成任务的一部分；ApplyTimestampRules（whisper/decoding.py:441-505）以掩码强制成对且单调不减（whisper/decoding.py:474-484）。
2. **幻觉防御三件套**：压缩率>2.4 判重复（whisper/utils.py:45-47）、平均 logprob<-1.0 判低质（whisper/transcribe.py:45）、no_speech_prob>0.6 判静音跳窗（whisper/transcribe.py:298-310）；词级模式再加幻觉静音跳过（whisper/transcribe.py:419-472）。模型卡直言转录可能含幻觉，这些全是工程兜底。
3. **资产离线化**：BPE 词表与 mel 滤波器随包分发，摆脱 librosa 运行时依赖。
4. **策略模式解耦**：Inference/TokenDecoder/SequenceRanker/LogitFilter 四族基类（whisper/decoding.py:130,216,179,407），贪心/束搜索/采样共享同一主循环。
5. **一套算法双实现**：DTW/中值滤波 CPU 走 numba（whisper/timing.py:82）、CUDA 走 triton（whisper/triton_ops.py:13-40），失败自动回退（whisper/timing.py:141-151）。
6. **权重即校验**：SHA256 嵌在 URL 路径（whisper/__init__.py:57 取倒数第二段），前后双校验（whisper/__init__.py:66,90）。

## 6. 数据流实例走读（tests/jfk.flac，11 秒肯尼迪演讲）

`model.transcribe("jfk.flac")`（tests/test_transcribe.py:11-42 即此断言链）：

1. `load_audio` 起 ffmpeg 得 176000 样本（whisper/audio.py:45-55），除以 32768 归一（whisper/audio.py:62）。
2. mel 计算时右侧垫 30s 零（whisper/transcribe.py:139），`content_frames` 标记真实语音仅 1100 帧（whisper/transcribe.py:140-141）。
3. 语言未指定 → 前 30s 做一次 `detect_language`（whisper/transcribe.py:151-153）：单 token 前向+语言 token 掩码 argmax（whisper/decoding.py:56-63）得 `en`。
4. 第一窗 `pad_or_trim` 到 3000 帧（whisper/transcribe.py:286），束搜索生成 `<|0.00|> And so my fellow <|1.75|>…`。
5. 相邻时间戳对切 segment（whisper/transcribe.py:342-367）；末时间戳 4.87s×50 帧/s → seek 跳到 243（whisper/transcribe.py:374-377），**直接跳过其后 6 秒静音**。
6. 第二窗全静音：no_speech 高+logprob 低 → 整窗跳过（whisper/transcribe.py:308-310）。
7. 返回 dict（whisper/transcribe.py:510-514）；测试断言 "my fellow americans" 在文本且 "Americans" 覆盖 1.8s（tests/test_transcribe.py:24,37-39）。

## 7. 扩展点

- **本地模型接入**：checkpoint 只需 `dims`+`model_state_dict` 两键（whisper/__init__.py:139-141）；本地模型不注入对齐头（whisper/__init__.py:158-159），词级时间戳退回后半层默认（whisper/model.py:279-283）。
- **自定义解码**：新 LogitFilter/TokenDecoder 挂进 `DecodingTask.__init__`（whisper/decoding.py:553-570）。
- **prompt 注入**：`initial_prompt` 进首窗（whisper/transcribe.py:239-242），`carry_initial_prompt` 贯穿全程（whisper/transcribe.py:288-291）。
- **区间转写**：`clip_timestamps="10,30,60,90"` 走 seek_clips（whisper/transcribe.py:168-177）。
- **评测复现**：notebooks 两件套；归一化用 EnglishTextNormalizer（whisper/normalizers/english.py:467）。
- **新输出格式**：实现 `ResultWriter.write_result` 注册进 get_writer（whisper/utils.py:309-316）。

## 8. 新人上手路径

1. 跑通：装 ffmpeg 后 `whisper audio.flac --model tiny`（CLI 默认 turbo，whisper/transcribe.py:530）。

2. 读 README 模型表：tiny(39M)→large(1550M)→turbo(809M)，`.en` 四档英文专用。
3. 按 tour 读码：`__init__.py` → `audio.py` → `tokenizer.py` → `model.py` → `decoding.py`（最难）→ `transcribe.py` → `timing.py`。
4. 实验：用 jfk.flac 对比 `--temperature 0` 与 `--word_timestamps True` 输出差异。
5. 避坑：CPU 上 fp16 自动降 fp32（whisper/transcribe.py:128-133）；`.en` 模型传非英文被强制改 en（whisper/transcribe.py:577-582）；高温窗口不作下窗 prompt（whisper/transcribe.py:503-505）。

## 9. 勘误与安全发现（源码核实）

1. **`_get_audio_features` 真 bug**：dtype 校验失败时 `return TypeError(...)` 而非 `raise`（whisper/decoding.py:660）——校验形同虚设，错误在别处炸出难懂堆栈。
2. **注册表数量口径**：图谱称 13 个；`_MODELS` 实为 **14 键**（whisper/__init__.py:17-32），`large`≡`large-v3`、`turbo`≡`large-v3-turbo` 同 URL，去重 **12 个唯一权重**。
3. **compression_ratio 实为 zlib**（whisper/utils.py:45-47）；docstring（whisper/transcribe.py:76-77）写 "gzip"，属文档漂移。
4. **cantonese 有码无 token**：LANGUAGES 字典 100 条，但多语言模型 `num_languages = 51865-51765-1 = 99`（whisper/model.py:314-315），get_encoding 只为前 99 语言造 token（whisper/tokenizer.py:343）——末位 yue（whisper/tokenizer.py:110）**无对应 token**，指定它转写抛 KeyError（whisper/tokenizer.py:223）。
5. **transcribe.py:179 的 `punctuation` 常量**与 prepend/append_punctuations 默认值近似重复但不联动：自定义标点时幻觉判定的标点集不变。
6. **无 VAD 模块**：静音检测全靠 `<|nospeech|>` token 概率（whisper/decoding.py:689-693）；注释自认"更好的分段应基于 VAD"（whisper/timing.py:307-308）。
