# 06 · __init__.py + utils.py：API 门面、模型矩阵与输出层

## 角色定位

这两个文件构成仓库的"门面 + 出口"。`__init__.py`（161 行）身兼三职：包 barrel（re-export 全部公共 API）、**模型注册仓库**（URL+SHA256 硬编码）、`load_model` 装配线。`utils.py`（329 行）是转写结果的落盘层：六种格式 writer 与三个小工具（compression_ratio/make_safe/format_timestamp）。用户从 `import whisper` 到拿到 .srt 文件，首尾两端都是这两个文件。

先钉版勘误：任务书建议本篇含 "vad"——**仓库不存在 vad.py**。VAD（语音活动检测）从未进入本仓主干（静音检测靠 `<|nospeech|>` token 概率，whisper/decoding.py:689-693；代码注释两次自认"更好的分段应基于 VAD"，whisper/timing.py:307-308）。本篇按源码实际改为 utils.py 输出层。

## 内部结构

**__init__.py 三段**：

1. **`_MODELS` 注册表（whisper/__init__.py:17-32）**：14 个键→Azure CDN URL，SHA256 就嵌在 URL 倒数第二段路径里（如 tiny.en 的 `d3dd57d…dd03`）。注意别名：`large` 与 `large-v3` 同 URL、`turbo` 与 `large-v3-turbo` 同 URL——14 键实际 **12 个唯一权重**。`_ALIGNMENT_HEADS`（whisper/__init__.py:36-51）配对地存 14 份 base85 编码的 (层数,头数) 布尔数组，whisper 词级时间戳按模型挑头（消费见 whisper/timing.py:207）。
2. **`_download`（whisper/__init__.py:54-95）**：缓存优先——命中且 SHA256 匹配直接返回（whisper/__init__.py:63-67），不匹配告警后重下；下载用 urllib 流式 8KB 块拷贝（whisper/__init__.py:73-87），完档再校验一次，失败即 raise（whisper/__init__.py:90-93）。
3. **`load_model`（whisper/__init__.py:103-161）**：设备缺省 cuda-if-available（whisper/__init__.py:130-131）、缓存根缺省 `~/.cache/whisper`（尊重 XDG_CACHE_HOME，whisper/__init__.py:132-134）；三分支：官方名下载 / 本地路径直读 / 都不是则报错并列出可用模型（whisper/__init__.py:136-145）；torch>=1.13 用 `weights_only=True` 反序列化（whisper/__init__.py:150-151，**安全细节：避免 pickle 任意代码执行**）；按 checkpoint["dims"] 构造 Whisper、load_state_dict、注入 alignment_heads（whisper/__init__.py:154-159），最后 `.to(device)`。

模型矩阵（README 表 + 注册表对照）：tiny 39M / base 74M / small 244M / medium 769M / large 1550M / turbo 809M；`.en` 只有前四档；turbo 是 large-v3 的蒸馏提速版（约 8x）。**注册表里还有 large-v1/v2** 两个历史版本——README 六档表不含它们，属"注册表比文档全"的常见漂移。

**utils.py 四块**：

1. **编码防护**：`make_safe` 在非 UTF-8 系统（Windows GBK 终端）把不可编码字符替换成 `?`（whisper/utils.py:10-15，规避 discussions/729 的 UnicodeEncodeError）；UTF-8 下是恒等函数（whisper/utils.py:17-21）。
2. **量测与格式化**：`compression_ratio = len(utf8 bytes)/len(zlib压缩)`（whisper/utils.py:45-47）——转写文本越可压缩越重复，>2.4 触发温度回退（whisper/transcribe.py:204-208）；`format_timestamp` 整数毫秒分解到 hh:mm:ss.mmm 并可换小数点符（whisper/utils.py:50-68，SRT 要逗号）；`get_start/get_end` 从 segments 抽首末词时间（whisper/utils.py:71-82）。
3. **Writer 族谱**：抽象基类 `ResultWriter` 定义 `__call__`（按音频文件名派生输出路径，whisper/utils.py:91-101）与抽象 `write_result`；六个子类——WriteTXT（whisper/utils.py:109）、WriteVTT（whisper/utils.py:238）、WriteSRT（whisper/utils.py:251）、WriteTSV（whisper/utils.py:265，整数毫秒列，注释说明规避小数点被 locale 换成逗号的风险）、WriteJSON（whisper/utils.py:287）、WriteJSONL（whisper/utils.py:296，每 segment 一行）。中坚是 `SubtitlesWriter.iterate_result`（whisper/utils.py:119-235）：当 segments 带 words 时按 max_line_width/max_words_per_line 重新断行、`highlight_words` 给当前词加 `<u>` 下划线（whisper/utils.py:210-219，字幕卡拉OK 效果）、长停顿 >3s 强制换 subtitle（whisper/utils.py:159-161）；无 words 时退化为 segment 级输出。
4. **`get_writer` 工厂（whisper/utils.py:306-329）**：格式名→类映射字典，`"all"` 返回串联调用六 writer 的闭包（whisper/utils.py:318-327）——CLI 默认 `--output_format all` 的实现。

## 外部连接

- `__init__` re-export 的 API 面：load_model/available_models（自有）、Whisper/ModelDimensions（model.py）、transcribe/decode/detect_language/DecodingOptions/DecodingResult（三模块各借方法绑定进 Whisper 类，whisper/model.py:350-352）。
- utils 的消费方：transcribe CLI 的写出（whisper/transcribe.py:597,616）、verbose 打印的 make_safe（whisper/transcribe.py:482）、compression_ratio 在 decoding.py 收尾时计算（whisper/decoding.py:784）。
- 写出路径：`output_dir/<音频名>.<ext>`（whisper/utils.py:94-98）。

## 数据流（CLI 一次调用）

```
$ whisper meeting.mp3 --model small --output_dir out
cli() 解析参数（whisper/transcribe.py:528-567）
→ load_model("small") 注册表查 URL→缓存校验→下载→装配（whisper/__init__.py:136-161）
→ transcribe(model, "meeting.mp3", **args) 返回 result dict（whisper/transcribe.py:615）
→ get_writer("all", "out") 返回六联 writer（whisper/utils.py:318-327）
→ writer(result, "meeting.mp3") 落盘 meeting.{txt,vtt,srt,tsv,json,jsonl}（whisper/utils.py:91-101）
```

## 设计决策

1. **权重分发走"URL 即清单"**：不加配置文件、不做 API，一个 dict 解决；SHA256 进 URL 的设计使校验值与下载源天然同源，无法错配。
2. **weights_only 反序列化**：torch>=1.13 强制开启（whisper/__init__.py:150），关闭 pickle 攻击面——对"从网上下二进制再加载"的场景是必要的安全底线。
3. **六格式一套抽象**：ResultWriter 只约束路径派生，write_result 全权交给子类；字幕三格式共享 iterate_result 的复杂断行逻辑，避免 SRT/VTT 各写一份。
4. **make_safe 只在打印路径**：transcribe 的 verbose 输出过 make_safe（whisper/transcribe.py:482），但写文件的 always UTF-8（whisper/utils.py:100）——终端兼容与文件正确性分开处理。
5. **Writer 是 callable 对象**而非函数，携带 output_dir 状态，CLI 一次构造多次复用（多音频文件循环，whisper/transcribe.py:613-616）。

## 新人提示

- 离线/内网部署：预下载 .pt 到 `~/.cache/whisper/`（或 XDG_CACHE_HOME 下 whisper 目录），load_model 命中缓存零网络（whisper/__init__.py:63-67）。
- 想拿结构化结果做后处理：直接用 WriteJSONL 的输出（每行一个 segment，含 words/tokens/概率），比解析 SRT 舒服得多。
- 自定义输出格式照抄 WriteTSV 的样子：继承 ResultWriter、声明 extension、实现 write_result、注册进 get_writer 字典（whisper/utils.py:309-316）。
- 报 "Model not found" 时先 `whisper.available_models()` 对表（whisper/__init__.py:98-100）；URL 失效属 CDN 问题，本地路径分支不受影响。

## 勘误

1. **无 vad.py**：任务书选题建议含 "vad"，全仓无此文件；静音检测走 `<|nospeech|>` 概率（whisper/decoding.py:689-693），词级幻觉跳过是启发式（whisper/transcribe.py:419-472），都不是 VAD。社区 whisper 变体（如 faster-whisper/whisperX）引入 Silero VAD 是仓外演进。
2. **checkpoint 数量口径**：图谱摘要称 13 个；`_MODELS` 实为 **14 键/12 唯一 URL**（whisper/__init__.py:17-32，large≡large-v3、turbo≡large-v3-turbo）。README 六档表还不含 large-v1/v2 两个历史键——三处口径（README 6、图谱 13、源码 14/12）互不一致，以源码为准。
3. `_download` 的进度条读 `Content-Length` 头（whisper/__init__.py:75），某些 CDN/镜像不回此头时 `int(None)` 会 TypeError——潜在的兼容性弱点，属未设防的外部输入。
4. utils.py 的 `system_encoding = sys.getdefaultencoding()`（whisper/utils.py:8）在 Python3 恒为 "utf-8"，因此 make_safe 的非恒等分支**实际不可达**——它是 Python2 时代的遗产代码（discussion/729 引用的正是历史问题），留着无害但已死。
