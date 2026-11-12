# transcribe_batch.py — 4 线程并行批量转录：流水线的 Inventory 引擎

> 源码：`helpers/transcribe_batch.py`（127 行）。行号锚均从源码逐一核实。

## ① 角色定位

这是整个剪辑流水线的**第一台机器**。video-use 的工作方式是"先把整个素材目录变成词级时间戳，再让 agent 在文本层面思考剪辑"——把一堆原始视频变成 `edit/transcripts/*.json` 的就是这个 127 行小文件。它是单文件转录器 `transcribe.py` 的批量扇出包装：找到目录里所有视频、剔除已转录的、剩下的丢进 4 线程池并行跑 `transcribe_one`（docstring L1-4）。

出现时机在 SKILL.md 里钉死：L75 命令速查表 "**`transcribe_batch.py <videos_dir>`** — 4-worker parallel transcription. Use for multi-take"，以及六步工作流第 1 步 Inventory（L85）——它是 Inventory 三连的第二棒：ffprobe 摸容器元数据，本文件摸内容文本，pack_transcripts.py 把 JSON 压成 agent 可读 markdown。

值得注意的反差：**转录是整条流水线唯一花钱的环节**（ElevenLabs Scribe 按量计费），install.md L137 也告诫安装期 "Full transcription test is optional — it burns Scribe credits"。所以本文件的缓存设计（见⑤）不是锦上添花而是成本闸门。

## ② 内部结构

文件极简，只有两个函数，主函数占据四分之三篇幅：

**`VIDEO_EXTS`（L26）**：`{".mp4", ".MP4", ".mov", ".MOV", ".mkv", ".MKV", ".avi", ".AVI", ".m4v"}`——八种扩展名，每种大小写各列一次。这不是冗余：`Path.suffix` 区分大小写，OBS 在不同平台会写出 `.MP4` 或 `.mp4`，只列小写会静默漏文件。`.m4v` 只列了小写是唯一的不对称。

**`find_videos`（L29-34）**：`iterdir()` 单层遍历（**不递归**子目录）+ 后缀过滤 + `sorted`——排序保证输出顺序稳定，agent 拿到的清单可复现。

**`main`（L37-122）** 按序做六件事：

1. 参数：`videos_dir` 位置参数；`--edit-dir` 缺省 `<videos_dir>/edit`（L71）；`--workers` 默认 4（L46）；`--language`/`--num-speakers`/`--audio-track` 原样透传（L47-64）。`--audio-track` 帮助文本（L63）藏着领域知识："OBS: 0 = game, 1 = mic"——OBS 录制默认游戏音频写 0 轨、麦克风写 1 轨，转录错轨就是白花钱。
2. 建目录：`(edit_dir / "transcripts").mkdir(parents=True, exist_ok=True)`（L72）。
3. 缓存差集（L78-80）：用 `transcript_path(edit_dir, v, args.audio_track).exists()` 把视频分成 `already_cached` 和 `pending` 两堆——**缓存判定与单文件模式共用同一个函数**，关键设计（见⑤）。
4. 提前打印统计（L82），全缓存时 "nothing to do" 直接返回（L83-85）——幂等重跑零成本。
5. 主线程 load 一次 API key（L87），`ThreadPoolExecutor(max_workers=args.workers)`（L93）把 `pending` 全部 `pool.submit`（L94-106）。`futures` 字典做 future→video 反查，`as_completed`（L107）按完成序收割：成功打印 `+`（L110-111），失败进 `errors` 列表打印 `x ... FAILED`（L112-114）——**单文件失败不炸整批**。
6. 结算（L116-122）：打印总耗时；有失败则逐条列出并 `sys.exit(1)` 退出——退出码是给 agent 的机器可读信号"还有活没干完，重跑即断点续传"。

## ③ 外部连接

- **上游依赖（L23）**：`from transcribe import load_api_key, transcribe_one, transcript_path`——全部来自单文件转录器。`load_api_key`（transcribe.py L36-49）翻 `.env` 找 `ELEVENLABS_API_KEY`，双失败退出；`transcribe_one`（transcribe.py L128-189）是完整单视频流水线：抽音→峰值预检（静音轨拒传，transcribe.py L165-173）→上传 Scribe→落盘 JSON；`transcript_path`（transcribe.py L116-125）定义 `<edit>/transcripts/<stem>[_trackN].json` 落盘约定。
- **注意 import 形态**：`from transcribe import ...` 是裸模块名导入，意味着**必须以 `python helpers/transcribe_batch.py` 运行**（脚本目录自动进 sys.path）——helpers/ 不是包，pyproject `py-modules = []` 确认无安装态模块。
- **下游**：`edit/transcripts/*.json` 被 `pack_transcripts.py` 压成 `takes_packed.md`，被 `render.py` 的 `build_master_srt`（L468）生成字幕，被 `timeline_view.py` 的 `words_in_range`（L118）画词标——一份转录三处复用。
- **工作流位置**：SKILL.md L85 第 1 步 Inventory 的核心动作。

## ④ 数据流

```
videos_dir/
 ├─ find_videos（单层、后缀过滤、排序）
 │    └→ [v1.mp4, v2.MOV, ...]
 ├─ 缓存差集：transcript_path(v).exists() ?  cached  :  pending
 │    （路径含轨道号：stem.track1.json ≠ stem.json，换轨=换缓存键）
 ├─ load_api_key()（主线程一次）
 └─ ThreadPoolExecutor(4)
      └─ transcribe_one(video, edit_dir, api_key, ..., verbose=False)
           ├─ transcript 已存在？→ 立即返回（双保险）
           ├─ ffmpeg 抽 mono 16kHz wav（-map 0:a:N 选轨）
           ├─ peak_dbfs < -60dBFS → RuntimeError 拒传（省一次计费上传）
           ├─ POST api.elevenlabs.io/v1/speech-to-text（timeout 1800s）
           └→ edit/transcripts/<stem>[.trackN].json
结算：成功计数 + errors[] → 退出码 0/1
```

数据流的要点是**缓存键 = 文件路径 + 音轨号**。`transcript_path` 的轨道后缀逻辑（transcribe.py L124-125：track 0 无后缀保持旧文件兼容，非 0 加 `.trackN`）保证"用 --audio-track 1 重跑"不会误读 track 0 的旧转录。

## ⑤ 设计决策与取舍

**线程池而非进程池/异步**：转录的两个重活是 ffmpeg 子进程（CPU 在 ffmpeg 进程里）和 HTTP 上传（纯 IO），Python 侧只做编排——GIL 不是瓶颈，ThreadPoolExecutor 是最简正确选择。4 并发是给 Scribe API 留余量的经验值。

**缓存判定函数共享，"two cannot drift apart"**：本文件最值得抄的设计。transcribe.py L119-123 注释写明：批处理的缓存测试必须用 `transcript_path` 这同一个函数，"one function, so the two cannot drift apart"——批量模式若自己拼路径字符串，落盘约定一变（如引入轨道后缀），缓存判定和实际写入就漂移，出现"永远重传"或"误读旧文件"两类静默 bug。共享真源函数从根上消灭分歧。

**fail-soft 收集而非 fail-fast**：10 个视频第 3 个失败时继续跑完剩下 7 个，最后统一报告（L118-121）。对按量计费的服务，fail-fast 会浪费已完成的转录机会，这个方向是对的；代价是错误报告滞后。

**verbose=False 压制单文件日志**（L102）：单文件模式的进度打印乘以文件数会淹没摘要；批模式只打一行一条的 `+`/`x` 结果。

**无重试无退避**：`transcribe_one` 对 HTTP 失败不重试，靠外层"重跑命令=断点续传"做粗粒度恢复——agent 看到退出码 1 和失败清单自己决定何时重跑，比脚本里埋指数退避更透明。

## ⑥ 新人提示（坑/勘误）

1. **不递归子目录**：`find_videos` 只 `iterdir()` 一层（L31），素材按日期建子文件夹的习惯在这里会扑空——先把文件摊平到一个目录，或按子目录分别调用。
2. **大小写覆盖不完整**：VIDEO_EXTS 列了四种常见格式的大小写双拼，但 `.m4v` 只有小写（L26）；`.Mov` 这类混合大小写后缀会被漏掉。遇到"明明有视频却说 no videos found"，先查后缀大小写。
3. **缓存键含音轨号，双刃剑**：先无脑跑一遍（默认 track 0）再想起 mic 在 track 1，重跑 `--audio-track 1` 会生成新文件不覆盖旧的——正确，但目录里会留下两套转录，pack_transcripts 读哪套取决于它自己的路径解析，别混用。
4. **pending 集合用 `not in` 判重（L80）**：`v not in already_cached` 是 O(n) 列表扫描，目录几千个视频时是 O(n²)——实际规模（几十条 take）无所谓，但搬去别的场景要知道这个上限。
5. **失败清单只到消息级**：`errors` 收集的是 `str(e)`（L113），Scribe 的 HTTP 错误体被 transcribe.py 截到 500 字符（transcribe.py L111），排障足够；但注意 `peak_dbfs` 拒传也会以普通 RuntimeError 进失败清单——看到 "is silent (peak -inf dBFS)" 不是 API 问题，是选错了音轨（提示信息会给出正确的 --audio-track 值，transcribe.py L170-172）。
6. **api_key 每线程共享**：主线程 load 一次传给所有 worker（L87、L99）。ElevenLabs key 无 per-request 派生需求，共享是安全的；但意味着轮换 key 需要重跑整个命令（缓存会跳过已完成的，成本可控）。
7. **测试盲区**：tests/ 目录只有 render.py 的三个测试文件，本文件与 transcribe.py 均无单测——缓存差集、轨道后缀这些逻辑的回归全靠手工。改 `transcript_path` 约定时记得这里 L78-79 是隐式消费方。

---
*下一篇：production-quality.md（Manim 技能出厂验收清单）。*
