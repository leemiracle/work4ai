# helpers/grade.py 精讲 — 有界调色：测量驱动的保守修正

## 一、角色定位：流水线里唯一的"图像 reasoning"执行器

`grade.py`（376 行）在六个 helper 中扮演色彩科学模块：把根 SKILL.md:168 的口号"reason about the image, not apply a preset"（推理画面，而非套预设）落成可执行代码。双重身份：既是独立 CLI（`grade.py <in> -o <out>` 直接出调色后视频），更重要的身份是 **render.py 的库依赖**——25 行 docstring 末句明说"Can also be imported by render.py: `get_preset(name)` and `auto_grade_for_clip(path, edl_range)`"。EDL 的 grade 字段写 `"auto"` 时，render.py 的 `extract_all_segments` 会对每个分段调 `auto_grade_for_clip` 逐段出修正滤镜（render.py:367-368 行）。

它处在管线的**分段抽取步**而非成片步——根 SKILL.md:180 硬规则："apply per-segment during extraction (not post-concat, which re-encodes twice)"，调色必须烤进分段，否则整片二次编码。

## 二、内部结构：预设字典 → 采样分析 → 有界决策 → 施加

**`PRESETS`（38-63 行）**四个命名预设，注释各自写明性格：
- `subtle`（41 行）`eq=contrast=1.03:saturation=0.98`——"barely perceptible cleanup"，分析不可用时的安全地板；
- `neutral_punch`（44-47 行）轻对比 + S 曲线（`curves=master='0/0 0.25/0.23 0.75/0.77 1/1'`），无色偏；
- `warm_cinematic`（52-59 行）唯一创意向预设：+12% 对比、压黑、-12% 饱和、暖阴影冷高光（colorbalance 三段）加胶片曲线，50-51 行注释郑重声明"OPT-IN creative preset… Not a default"，来源 HEURISTICS §6 且"too aggressive for standard launch content"——主动劝退默认使用；
- `none`（62 行）空串哨兵，`apply_grade` 遇空串走 `-c copy` 直拷（277-280 行），语义"跳过此源"。

**`get_preset`（66-72 行）**名字查表，未知名抛 KeyError 且报错文案列出全部可用名（70-71 行）——render.py 的 `resolve_grade_filter` 捕获这个 KeyError 后把未知名当原生滤镜串放行（render.py:82-84 行）。

**`_sample_frame_stats`（78-175 行）**是测量引擎。104-112 行构造 ffmpeg 命令 `fps=N,signalstats,metadata=print:file=...`——signalstats 滤镜把每帧的 YMIN/YMAX/YAVG/SATAVG 写进 metadata 文件；98 行采样率 `fps = max(0.5, min(n_samples / duration, 10.0))` 两端钳制。解析段最有含金量的是**位深归一化**：114-118 行注释说明 signalstats 按解码帧原生位深报告（8bit→0-255，10bit→0-1023），故先读 `YBITDEPTH`（133-136 行）再以 `2^depth - 1` 归一（159 行），统计量统一到 0..1。154-156 行防御底线：一个 YAVG 都没采到就返回中性默认 `{"y_mean": 0.5, "y_std": 0.18, "sat_mean": 0.25}`（不修正）。171 行坦白近似 `y_std = y_range / 4.0`，注释直言"range ÷ 4 ≈ stddev for normal-ish distributions"。

**`auto_grade_for_clip`（178-271 行）**决策核心，三轴规则全部**只修不创**：
- 对比度（216-223 行）：目标极差 0.72；y_range < 0.65 时把 [0.50, 0.65] 映射到增益 [1.08, 1.03]（越平越加），否则回落 1.03 基线；**只升不降**（216 行注释"Boost gently if flat, never reduce"）；
- Gamma（226-233 行）：目标均值 0.48；过暗（<0.42）把 [0.30, 0.42] 映射到 [1.10, 1.02] 温和提亮，过曝（>0.60）轻微回拉 0.97；
- 饱和度（236-244 行）：默认 0.98 微收（238 行注释：消费级显示器上数字视频普遍偏饱和）；极平（<0.18）提到 1.04，已很艳（>0.38）压到 0.96，**从不激进去饱和**。

随后 247-249 行三轴硬钳（contrast [0.94,1.08]、gamma [0.94,1.10]、sat [0.94,1.06]）——docstring 12 行的"±8% cap"。253-258 行死区：偏离 1.0 不足 0.005 的轴不写进滤镜串，261 行三轴全中性返回空串（不调色）。duration 缺省先 ffprobe 探（194-205 行），失败兜底 10 秒。

**`apply_grade`（274-291 行）**：有滤镜时 libx264 fast CRF 18 重编码（285 行，比 render.py 分段档 CRF 20 更精细，因独立 CLI 输出即最终产物）；空滤镜 `-c copy`。

**`main`（294-371 行）**四个无副作用模式：`--list-presets`（330-335 行）、`--print-preset`（337-339 行，根 SKILL.md:172 提到 agent 用它抄滤镜串）、`--analyze`（341-347 行只打印不写文件）；不传 preset/filter 时**默认 auto**（361-362 行）。

## 三、外部连接：render.py 的软依赖 + 根 SKILL.md 的调色章节

被 render.py 以 try/except 导入（render.py:32-40 行）是最重要的对外关系——软依赖的降级 stub 恰好内联了 `subtle` 预设字面量（render.py:39 行与本文 41 行逐字符相同），保证 grade.py 缺位时退化为"全段 subtle"而非崩盘。render.py 三处消费：`resolve_grade_filter` 用 get_preset 解析预设名（render.py:81）、auto 模式逐段调 `auto_grade_for_clip`（render.py:368）、分段滤镜进 ffmpeg `-vf` 链（render.py:306）。

对根 SKILL.md 的契约：L172-179 给三预设使用建议（warm_cinematic"Shipped in a real launch video"、none 是用户没要求时的默认）；L170 给出 ASC CDL 心智模型（`out = (in * slope + offset) ** power`，slope 管高光、offset 管阴影、power 管中间调）——本文件的 eq/curves 参数正是该模型的 ffmpeg 方言；L180 两条硬规则（分段施加、未测肤色不上激进调色）界定调用纪律。它不 import 任何仓内代码，唯一外部依赖是 ffmpeg。

## 四、数据流：视频区间 → 帧统计 → 滤镜字符串

核心数据形态很特别：**函数返回值是 ffmpeg 滤镜表达式字符串**而非视频。`auto_grade_for_clip` 返回 `(filter_string, stats)` 二元组（183 行）——先"读"（区间采样出三个标量），再"写"（拼出 `eq=contrast=…:gamma=…:saturation=…`）；真正作用于像素的执行发生在调用方的 ffmpeg 命令里（本文件 CLI 的 283 行，或 render.py 的 extract 链）。

这条数据流使调色决策**可打印、可审计、可人工覆盖**：`--analyze` 模式（341-347 行）把 stats 与滤镜串打到 stdout，agent 可先看数再决定是否采纳——正是根 SKILL.md:168"Look at a frame, decide what's wrong, adjust one thing, look again"工作流的量化版。stats 字典被 render.py 丢弃式接收（render.py:368 行 `_stats`），当前只有滤镜串是有效载荷。

## 五、设计决策与取舍

**"Clean, not graded"（14 行）是纲领**：auto 模式刻意限定在曝光/平/淡三缺陷的修正，不做创意色彩（无 LUT、无 teal/orange、无胶片曲线），创意全部留给显式 opt-in 的 warm_cinematic 或 `--filter` 原生串。这个划分把"正确性"（auto 兜底）与"品味"（显式选择）解耦——与根 SKILL.md:14"Hard Rules 是正确性、其余是艺术自由"的总纲同构。

**±8% 硬顶 + 0.005 死区**双保险：钳制保证最坏情况不出怪色，死区保证近中性素材零处理（省一次编码——空串触发 `-c copy`）。宁可欠调不可过调，因为调色错误是静默的——观众说不出哪里不对但就是觉得"廉价"。

**signalstats 而非逐像素 numpy**：借 ffmpeg 原生统计避免把帧搬进 Python，10 帧采样开销近似一次 seek，两小时素材也秒级出结果；代价是统计粒度粗（无直方图、无 per-channel），但目标是"三标量决策"，够用。**极差/4 估 stddev**（171 行）是全文最大的统计近似——auto 决策只消费 y_std×4 还原回极差（210 行），近似两侧抵消、闭环自洽。临时文件用后即删（174-175 行）。

## 六、新人提示：坑与勘误

1. **默认行为是 auto 不是 none**：裸跑 `grade.py in -o out` 自动分析调色（361-362 行）；要"什么都不做"必须显式 `--preset none`——与根 SKILL.md:176"'none' — Default when the user hasn't asked"存在张力：那指**对话层**默认不调色（EDL 不写 grade 字段）。
2. **`--analyze` 与渲染分离**：分析结果不自动持久化，复用滤镜串需自己抄下来传 `--filter`；render.py 的 auto 路径每次渲染重新分析（同源同区间结果确定）。
3. **采样区间必须传源视频坐标**：`_sample_frame_stats` 的 start/duration 是源坐标系——render.py 传 EDL range 原值（render.py:368），误传输出时间轴坐标会分析错画面段。
4. **YBITDEPTH 缺失时按 8bit**（123 行初值）：某些容器的 signalstats 不报位深，10bit 源被误当 8bit 归一（统计偏小），决策趋于"更平→加对比"；影响在 ±8% 顶内但值得知道。
5. **warm_cinematic 别当默认**：50-51 行注释自认"too aggressive for standard launch content"；skin tone 未验证时上它违反根 SKILL.md:180 硬规则。
6. **KeyError 是接口契约**：render.py 靠捕 KeyError 把未知预设降级为原生滤镜（render.py:82-84），把 get_preset 改成返回 None 会静默破坏那条路径。
