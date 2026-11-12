# timeline_view.py — 胶片条+波形合成：唯一的可视化下钻工具

> 源码：`helpers/timeline_view.py`（393 行）。行号锚均从源码逐一核实。

## ① 角色定位

video-use 是一个"对话式剪辑"仓库：agent 读转写、写 EDL、调 render.py 出片。整条流水线几乎一切都是文本和 JSON，唯独这个文件负责把一段视频"变成一张可以看的图"。它的输出不是数据而是**判断材料**——一张 PNG：上半部是 N 帧均匀抽取的胶片条，下半部是对应时间窗的音频波形包络，叠上转写词标和静音阴影（docstring L1-7）。

它的身份被反复钉死为"决策点工具"：docstring L3 自称 "The only visual drill-down tool"，L9-10 明令 "Do NOT call it in a scan loop over every utterance; it's an on-demand drill-down, not a background index"。主 SKILL.md 同样两处强调：L77 "On-demand visual drill-down. **Not a scan tool** — use it at decision points, not constantly"；L91 第 7 步自检要求对**渲染后的成片**（而非源素材）在每个切点边界开 ±1.5s 窗口跑它逐图检查。这个定位是成本设计：一次调用 = N 次 ffmpeg 抽帧 + 一次音频抽取 + 一次 PIL 合成，滥用在扫描循环里会拖垮整个会话。

它支撑三类决策场景：剪辑前的**素材理解**（SKILL.md L85 第 1 步 "Sample one or two timeline_views for a visual first impression"——抽样一两张非全量）、剪辑中的**歧义仲裁**（L89 第 5 步 "Drill into timeline_view at ambiguous moments"）、调色迭代回路（L168 "Look at a frame (via timeline_view), decide what's wrong, adjust one thing, look again"）。

## ② 内部结构

文件按四个清晰段落组织，全部是模块级函数，无类：

**抽帧段 `extract_frames`（L37-62）**：把 `[start, end]` 均匀切成 N 个时间点。n=1 时特判取中点（L42-43），否则 `step = (end - start) / (n - 1)`（L45）——注意分母是 n-1，首尾两点都落在区间端点上。每个时间点独立跑一次 ffmpeg：`-ss` 放在 `-i` 之前（L52-54，输入前 seek，快且在此精度下足够准），`-frames:v 1` 只取一帧，`-q:v 4` 中高画质，`-vf scale=320:-2` 统一压到 320 宽（L51-59）。stdout/stderr 全部 DEVNULL（L60），agent 终端不被 ffmpeg 刷屏。

**音频包络段 `compute_envelope`（L68-112）**：先用 ffmpeg 把时间窗抽成 mono 16kHz 16-bit PCM 临时 wav（L77-84）；失败或空文件返回全零数组优雅降级（L86-87）——源可能没有音轨。然后是全文件最有意思的一手：**用 stdlib `wave` 模块手读 WAV**（L90-92），`np.frombuffer(dtype=np.int16).astype(np.float32) / 32768.0` 归一化（L93），窗口 RMS 得到固定长度包络（L98-106，短了 pad 长了截断），除以最大值压到 [0,1]（L107-109）。`finally` 确保临时 wav 删除（L111-112）。

**转写叠加段（L115-148）**：`words_in_range`（L118-132）读 transcript JSON 的 `words` 数组，跳过缺 start/end 的条目（L127-128），保留与窗口相交的词（L129）。`find_silences`（L135-148）以 0.4s 为阈值找"保留 token 之间的空隙"：跳过 `type == "spacing"` 填充条目（L140-141），逐词推进 `prev_end`（L145），收尾再查到区间末端的空隙（L146-147）。

**合成段 `render_timeline`（L184-330）**：布局硬编码——画布宽 1920、帧高 180、波形带高 220（L199-206）。帧图统一缩放到帧高后拼条（L209-214）；总宽超可用条宽则整条等比缩放垂直居中（L244-253）。`time_to_x`（L259-261）把时间线性映射到条内像素，是所有叠加物的共同坐标系。绘制顺序即图层顺序：波形底色（L264）→ 静音半透明蓝衬（L267-272）→ 包络上下轮廓 + 多边形半透明填充（L275-290）→ 词标与短刻度（L292-311）→ 时间刻度尺（L313-321）→ 静音图例（L324-326）。字体走五候选列表（L154-160：macOS 三路径 + Linux 两路径），全落空回退 PIL 默认位图字体（L170）。

入口 `main`（L333-388）：`--n-frames` 默认 10（L339）；`--transcript` 缺省时自动探测 `<video_parent>/edit/transcripts/<stem>.json`（L370-373）；输出缺省落到 `<video_parent>/edit/verify/<stem>_<start>-<end>.png`（L376-379）。参数校验：end 必须大于 start（L365-366）。

## ③ 外部连接

- **上游**：消费 `helpers/transcribe.py` 的产物格式（`{"words": [{type, text, start, end}, ...]}`），词标与静音检测都依赖词级时间戳；transcript 缺失时功能退化——只出胶片条+波形。
- **下游**：PNG 落在 `edit/verify/`，正是 SKILL.md L53 声明的 "`verify/` ← debug frames / timeline PNGs"——agent 与人共用这个目录做验收凭证。
- **工作流挂点**：SKILL.md 六步流程挂三处——第 1 步抽样（L85）、第 5 步歧义下钻（L89）、第 7 步成片切点自检（L91）；调色循环（L168）也靠它看帧。
- **进程边界**：外部依赖只有 ffmpeg + numpy/PIL（pyproject.toml L11-12）。不 import 任何兄弟 helper——helpers 里少数零内部依赖的文件。

## ④ 数据流

一次调用 `timeline_view.py clip.mp4 4.0 9.5` 的完整数据流：

```
video + [start, end]
 ├─→ ffmpeg × N      ──→ 临时 f_000.jpg…f_009.jpg（320 宽）
 │                        └→ PIL 打开 → 等高缩放 → 拼条/溢出缩放
 ├─→ ffmpeg × 1      ──→ 临时 mono wav
 │                        └→ stdlib wave 手读 → int16→float32 → 窗口 RMS → 归一化包络
 └─（可选）transcript.json ──→ words_in_range → 词标 + find_silences → 静音衬
三方汇合 → 1920×~620 RGB 画布（RGBA draw 层画半透明）
        → edit/verify/clip_4.00-9.50.png（optimize 落盘，L329）
```

两条 ffmpeg 通道互相独立：静音衬表达"转写意义上的静默"（词间隙 ≥0.4s），波形起伏表达"物理能量"——两者对照正是人工判断"这里该不该切"的证据组合。

## ⑤ 设计决策与取舍

**为什么手读 WAV 而不用 librosa**：L89 注释直说 "Read the WAV manually — avoid librosa as a hard dep"。librosa 拉着 numba/llvmlite 一串重型依赖，而这里只需要"一段 mono PCM 的能量包络"——stdlib `wave` + 十行 numpy 就够。但见勘误：pyproject 仍声明着 librosa。

**为什么逐帧独立 ffmpeg 而非一次 `select` 滤镜抽 N 帧**：select 要解码整个区间且滤镜表达式繁琐；`-ss` 前置的单帧抽取是 ffmpeg 最快路径（关键帧跳转 + 少量解码），N=10 时十次进程开销远小于解码全区间。对"按需下钻"的使用频率，简单粗暴是最优解。

**静音检测用词间隙而非音频能量**：find_silences 完全建立在转写时间戳上，不看包络。取舍：词间隙与"说话停顿"语义对齐（物理静音可能只是换气）；代价是无 transcript 时静音层消失（L267-268），转写时间戳抖动会传导进来。

**画布 RGB + 绘制层 RGBA**：`Image.new("RGB")` 建画布（L220）但 `ImageDraw.Draw(canvas, "RGBA")` 开 RGBA 上下文（L221），SILENCE 色带（L180）和波形填充 60 透明度（L290）才得以半透明叠加，避免整画布升 RGBA 的内存翻倍。

**包络采样数与条宽挂钩**：`samples=max(strip_span, 200)`（L275）——每像素至少一个采样点，波形不欠采样。

## ⑥ 新人提示（坑/勘误）

1. **`--edl` 是公开的未实现占位**：docstring L18 写明 "(full-project view — not yet)"；真传 `--edl` 会被 L355-356 直接 `sys.exit("--edl mode is not implemented yet; use range mode")`。全项目时间轴视图是规划中功能，别在 agent 提示词里依赖。
2. **pyproject 声明 librosa/matplotlib 但 helpers 零消费**：`pyproject.toml` L9-10 声明 `librosa` 和 `matplotlib`，全仓 grep 实证（排除 .understand-anything）它们只出现在 install.md L49 的转述和 timeline_view.py L65/L89 的注释里——**没有任何代码真正 import 它们**。装依赖时纯属白装（librosa 还很重）。
3. **L65 段落标题撒谎**：注释写 "Audio envelope (librosa if available, ffmpeg fallback)"，但函数体（L68-112）不存在 librosa 分支——无 try import、无条件调用。早期设计的残留注释，描述了一个从未实现的方案，实情是"纯 ffmpeg + 手读"。
4. **词标阈值注释与代码不一致**：L292 注释说 "only words lasting ≥ 120ms to avoid clutter"，L302 实际代码是 `if (we - ws) < 0.05: continue`——50ms，不是 120ms。以代码为准。
5. **字体候选无 Windows 路径**：FONT_CANDIDATES（L154-160）只覆盖 macOS 和 Linux，Windows 上会静默落到 PIL 默认位图字体，词标观感明显退化。
6. **n_frames=1 语义**：单帧不是取 start 而是取区间中点（L42-43），防止拿它当"第 0 帧截图"用错语义。
7. **静音图例硬编码文案**：L325 图例写死 "silences ≥ 400ms"，与 L268 显式传的 `threshold=0.4` 及 L135 默认值一致——改阈值只改一处图例就撒谎，三处要同步。

---
*下一篇：transcribe_batch.md（转录流水线的批量入口）。*
