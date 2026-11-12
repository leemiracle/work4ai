# helpers/transcribe.py 精讲 — Scribe 转录：全流水线的事实源头

## 一、角色定位：唯一的外部 API 消费者，一切决策的数据地基

video-use 的核心哲学是根 SKILL.md:10 的 Principle 1："LLM reasons from raw transcript"——剪辑决策不来自看画面，而来自读转录。`transcribe.py`（242 行）就是生产这份事实源头的脚本，也是全仓**唯一**发外部大模型 API 请求的代码：33 行 `SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"` 是仓里唯一的远端模型端点，`ELEVENLABS_API_KEY` 是唯一的 API 凭据（.env.example 里也只有这一行）。图谱 L04"转录流水线"层的根。

它的产出 `edit/transcripts/<name>.json` 是三个下游的共同输入：pack_transcripts.py 把它压成 takes_packed.md（编辑子代理的主读物）、render.py 的 build_master_srt 从它生成字幕、timeline_view.py 的 words_in_range 从它取词标签与静音着色。可以说这个仓里除像素外的一切时间信息都源于这里。

## 二、内部结构：凭据 → 探测 → 上传 → 缓存

**`load_api_key`（36-49 行）**按两级位置找 `.env`：先仓根（37 行 `Path(__file__).resolve().parent.parent / ".env"`，即 helpers/ 的上级），再当前工作目录；键值解析是手写的——跳过空行与 `#` 注释、按第一个 `=` 切分（43 行 `split("=", 1)`）、剥两端引号（45 行）；.env 都没有则查环境变量（46 行），再没有就 `sys.exit` 报错（48 行）。没有第三方 dotenv 依赖，requests 是唯一 pip 依赖（30 行）。

**三个探测函数**构成上传前的防线：
- `count_audio_tracks`（52-59 行）ffprobe 数音频流，为多轨源给出提示；
- `peak_dbfs`（62-71 行）用标准库 `wave`+`array` 分块读 16-bit PCM 求**数字峰值**——68 行注释解释分块动机：批量模式并发跑多个文件，两小时素材的 16kHz 单声道 wav 有 230MB，一次性 array 拷贝会翻倍内存；71 行 `20*log10(peak/32768)` 换算 dBFS，全静音返 `-inf`；
- `extract_audio`（74-81 行）ffmpeg 抽单声道 16kHz `pcm_s16le` wav（78 行）——这是语音识别的标准喂料形态，也顺手把体积压到可上传量级。

**`call_scribe`（84-113 行）**是 API 调用本体，五个请求参数里三个是 Hard Rule 8（根 SKILL.md:29"词级 verbatim、永不 SRT/短语模式"）的代码化：91 行 `model_id=scribe_v1`、92 行 `diarize=true`（说话人分离）、93 行 `tag_audio_events=true`（把笑声/掌声标记为事件，根 SKILL.md:111 把它们当节拍信号用）、94 行 `timestamps_granularity=word`（词级时间戳——剪辑精度的根基）。可选 `language_code` 与 `num_speakers`（96-99 行）。101-108 行以 multipart 上传 wav，**timeout=1800 秒**（107 行）容忍长素材；110-111 行非 200 抛 RuntimeError 并截取响应前 500 字。

**`transcript_path`（116-125 行）**决定落盘名，是缓存键：124 行 `suffix = "" if audio_track == 0 else f".track{audio_track}"`——track 0 保持裸名是为了向后兼容（121-122 行注释：该旗标出现前生成的转录仍有效）；118-121 行注释点名设计约束："Batch mode tests its cache with this too — one function, so the two cannot drift apart"，单文件与批量共用这一个函数当缓存判据，杜绝两处逻辑漂移。

**`transcribe_one`（128-189 行）**主流程四步：先查缓存命中即返（145-148 行，Hard Rule 9"缓存转录、源没变就永不重转录"）；多轨源打印提示（153-156 行）；临时目录里抽音频（159-161 行）；**静音守卫**（165-173 行）——`peak < -60.0 dBFS` 直接抛错拒绝上传，167-173 行的报错信息是精心设计的产品文案：说明哪条轨静音、还剩哪些轨可试（170-171 行动态拼出其他轨号），因为"上传静音与上传语音同价却返回空"（163-164 行注释）；最后落盘 JSON 并报词数（180-187 行）。

**`main`（192-237 行）**：四个旗标里 `--audio-track`（213-220 行）的 help 文本藏着一手实测知识："OBS writes the game on track 0 and the mic on track 1"——OBS 双轨录制者若不指定，ffmpeg 默认选声道最多的轨（219 行），常会选中游戏音轨而非人声。

## 三、外部连接：上游 ElevenLabs，下游三消费者，兄弟 transcribe_batch

对上是 ElevenLabs Scribe API（计费方，也是根 SKILL.md:62 要求冷启动先验 `ELEVENLABS_API_KEY` 的原因）。对下三条消费线已如角色定位所述。横向关系最密的是 `transcribe_batch.py`：23 行 `from transcribe import load_api_key, transcribe_one, transcript_path` 三个符号全数复用——批量版只是给 `transcribe_one` 加了 ThreadPoolExecutor 并发（batch 93-106 行）与逐文件错误收集，缓存判据也调 `transcript_path`（batch 78-79 行），印证 118-121 行"one function"的设计承诺。

与根 SKILL.md 的契约点：L74 的用法条目（"single-file Scribe call. Cached."）、L85 流程第一步把它与批量版连用、Hard Rule 8/9 是它的行为规范。注意根 SKILL.md:330-331 的反模式清单点名"本地 CPU 跑 Whisper"与"Whisper SRT/短语输出"皆禁——hosted Scribe + 词级 verbatim 是唯一正路，这正是本文件存在的理由。

## 四、数据流：视频文件 → 16kHz wav → Scribe JSON → 永久缓存

数据变形链清晰可数：输入任意容器/编码的视频路径 → ffmpeg 抽目标音轨为 mono 16kHz 16-bit wav（临时文件，用完随 TemporaryDirectory 消失）→ multipart 上传 → ElevenLabs 返回 JSON（`words` 数组，每项含 `type: word|spacing|audio_event`、`text`、`start`、`end`、`speaker_id`）→ `indent=2` 美化落盘到 `transcripts/<stem>[.trackN].json`（180 行）。

关键性质：**这个 JSON 是 immutable 的**——一经写出，下游（pack/render/timeline_view）只读不改，源文件不变就永不重跑（Hard Rule 9）。时间坐标系是"源视频本地时间"（秒，浮点），render.py 的 Rule 5 换算负责把它翻译到成片时间轴。words 的三类型结构是下游两个分组算法的共同输入：pack_transcripts 按 spacing 断短语、render 字幕按 word 加 gap 断句、timeline_view 按 spacing 着色静音带——同一份数据三种切法，这正是"derive at decision time"（根 SKILL.md:10）的字面实现。

## 五、设计决策与取舍

**标准库至上**：wav 解析用 `wave`+`array`（62-71 行），.env 解析手写（36-49 行）——整个文件唯一的第三方依赖是 requests（30 行）。换来的是极端可部署性：一台装了 ffmpeg 的机器加一个 API key 就能跑。

**防呆优先于防错**：静音守卫（165 行）拦下"花钱买空结果"这一最贵的错误类别；报错文案不是栈迹而是操作指引（170-172 行直接给出应试的轨号）。这类把产品知识写进异常消息的做法贯穿全仓（render.py:107 同款风格）。

**track 后缀的兼容术**（124 行）：新功能（多轨）以"track 0 不变名"的方式引入，旧缓存全部自然延续——宁可文件名方案稍不均匀，也不做一次缓存失效。

**1800 秒超时**：长素材上传+识别是真实场景（两小时 take），超时给足；代价是网络真死时失败反馈慢，但这是"宁可慢成功不要快失败"的正确取舍，因为转录是整条流水线最贵的一步（Hard Rule 9 的存在本身就是为此）。

**verbose 参数**（134 行）让批量模式静音、单文件模式有声——同一函数两种人格，批量的进度由外层统一打印（batch 111 行）。

## 六、新人提示：坑与勘误

1. **`.env` 只认仓根与 cwd 两处**（37 行）：把 `.env` 放视频目录里是无效的；根 SKILL.md:62 也明确要求 key 永不写进 `<videos_dir>`。
2. **track 后缀陷阱**：用 `--audio-track 1` 生成的转录文件名是 `<stem>.track1.json`，下游（pack/render）按 `<stem>.json` 找文件时会**静默找不到**这套转录——多轨工作流要手动对齐文件名或统一轨号，这是当前设计的一个真实缝隙。
3. **静音阈值 -60 dBFS 是数字静音级别**：真实录音环境噪声通常在 -50 以上，所以该守卫只拦"完全选错轨"型事故，不拦低音量素材——低音量照样上传，质量问题留给后面的 loudnorm。
4. **转录文件不可手改后复用缓存**：缓存判据只看文件存在（145 行），不看内容——手工修过时间戳想生效必须删文件重跑或改名。
5. **`peak_dbfs` 返回 `-inf` 时**（71 行）浮点比较 `peak < -60.0` 在 Python 中为 True，行为正确；但若有人把日志打印 `{peak:.1f}` 会得到 `-inf` 字样，别当成 bug。
6. **requests 无重试**：网络抖动直接抛异常，单文件模式会非零退出；批量模式把它计入错误清单（batch 112-114 行）不中断其他文件——单文件重跑即可，缓存保证不重复计费。
