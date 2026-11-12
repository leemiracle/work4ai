# helpers/render.py 精讲 — EDL 到成片的确定性渲染管线

## 一、角色定位：Hard Rules 的机器执行者，流水线的收口

`render.py`（801 行）是六个 helper 中最大、也是唯一把根 SKILL.md 十二条 Hard Rules 中六条**直接编码成代码**的文件。分工：根 SKILL.md 负责对话与决策、产出 `edl.json`（编辑决策列表），本文件吃进 edl.json 吐出 final.mp4。1-20 行 docstring 把管线钉死为四步：逐段抽取（含调色+30ms 音频淡入淡出）→ 无损 `-c copy` 拼接 → 单 filter graph 合成（overlay 带 PTS 偏移、字幕压轴）→ 可选响度归一。纯执行层：没有任何"选择"，一切决策已在 EDL 里。

根 SKILL.md:78 的官方速记"per-segment extract → concat → overlays (PTS-shifted) → subtitles LAST"——四短语分别对应 Hard Rule 2、4、1（根 SKILL.md:22-24）。

## 二、内部结构：软依赖降级 → 源分析 → 四段式管线

**软依赖头（32-40 行）**是全文件第一设计亮点：`from grade import get_preset, auto_grade_for_clip` 包在 try/except 里，失败注入两个降级 stub——`get_preset` 恒返空串（不调色），`auto_grade_for_clip` 恒返 `"eq=contrast=1.03:saturation=0.98"`（grade.py subtle 预设字面量，见 grade.py:41）。grade.py 缺失时渲染照常完成，只是没有逐段调色；33 行注释"same directory"点明同目录约定。

**字幕样式常量 SUB_FORCE_STYLE（52-57 行）**：Helvetica 18 Bold、白字黑描边、Alignment=2（底部居中）、`MarginV=90`。42-51 行长注释解释了"为什么"：MarginV 不是品味而是平台安全区规则——TikTok/Reels/Shorts 的 UI 遮住竖屏底部约 25-30%，libass 以 PlayResY=288 为基准自动缩放画布，故 MarginV=90 在任意画幅下都把字幕基线抬到底部 30% 以上（51 行："没有具体理由不要降到 75 以下"）。

**源分析函数群**是渲染前的体检：
- `is_hdr_source`（135-146 行）ffprobe 查 `color_transfer`，对照 123 行 `HDR_TRANSFERS = {"smpte2084", "arib-std-b67"}`（PQ/HLG）。110-121 行注释：iPhone 默认 HLG，只降位深不做 tone mapping 的话 8bit 输出仍带 HDR 元数据，上传播放过饱和。
- `is_portrait_source`（149-187 行）判竖屏。174 行 `rotation % 360 in (90, 270)` 时交换宽高——167-169 行注释：ffmpeg 会在滤镜前自动旋转 display matrix，故按滤镜实际看到的尺寸选缩放轴；**有意忽略**纯 metadata 的 rotate tag（169-170 行），因其不保证自动旋转；177-186 行九类异常大 except 恒返 False（探测失败按横屏默认）。
- `parse_fps`（189-212 行）fps 守门员：Fraction 规范化后按 ffmpeg AVRational（有符号 32 位）约束分子分母（209-211 行）保证幂等；tests/test_render_fps.py:23-29 验证 `"60"→"60/1"`、`"29.97"→"2997/100"`。`probe_source_fps`（215-242 行）优先 `avg_frame_rate`（可变帧率源更准），`r_frame_rate` 兜底，`0/0` 跳过（235 行）。

**管线四段**：

1. `extract_all_segments`（317-379 行）+ `extract_segment`（248-314 行）。前者先做**全局帧率决议**（341-352 行）：显式 `--fps` 最高，否则探第一源帧率，兜底 24——344-345 行注释：Rule 2 的无损 concat 要求所有段帧率一致，多源混合逐段探测必然发散。`resolve_grade_filter`（68-85 行）把 EDL grade 字段三态化：空=不调、`"auto"`=哨兵 `"__AUTO__"` 逐段分析（367-368 行）、短标识符=预设名（79 行正则判别，与含 `=`/`,` 的滤镜串区分）、未知预设告警后当原生滤镜用（83-84 行）。`extract_segment` 内部：`-ss` 放 `-i` 之前快速精确定位（303-304 行）；竖屏按高缩放横屏按宽（271-274 行）；三级质量阶梯（263-267 行：final=1080p fast CRF20 / preview=medium CRF22 / draft=720p ultrafast CRF28）；285-287 行把 Hard Rule 3 的 30ms 双端 afade 烤进每段。
2. `concat_segments`（385-401 行）：concat demuxer + `-c copy` 零重编码，`_concat.txt` 用后即删（401 行）。
3. 字幕支线：`chunk_words`（439-465 行）+ `build_master_srt`（468-521 行）。四常量（433-436 行）`CHUNK_WORDS=2 / CHUNK_MAX_WORDS=3 / CHUNK_MIN_S=0.35 / CHUNK_PAUSE_S=0.3` 支配分块；456-462 行五个断句条件：无后继词、尾标点（407 行 `PUNCT_BREAK`）、与下词间隙≥0.3s、达 3 词上限、满 2 词且已 ≥0.35s。`build_master_srt` 逐段做 Rule 5 换算（497-500 行）：`输出时间 = 词.start - 段.start + 段偏移`；缺转录段跳过字幕但照常推进偏移（488-491 行）；506-507 行剥尾标点转大写。
4. `build_final_composite`（633-706 行）：659-661 行给每个 overlay 施 `setpts=PTS-STARTPTS+T/TB`（Rule 4，overlay 第 0 帧对齐窗口起点）；663-673 行 overlay 链式叠上；**675-681 行 subtitles 滤镜压轴**（Rule 1）——无 overlay 无字幕则 647-650 行直拷贝零损耗。698 行合成档 CRF 18 高于分段档的 20。

**响度支线**：`measure_loudness`（534-565 行）跑 loudnorm 首遍，从 stderr 里 `rfind("{")...rfind("}")` 抠出 JSON（553-559 行）；`apply_loudnorm_two_pass`（568-627 行）final 两遍精确归一，preview/draft 单遍提速（581-595 行），测量失败降级单遍（600-602 行）。目标 529-531 行：-14 LUFS / -1 dBTP / LRA 11，社媒通行标准（527 行）。**main（712-797 行）**：六旗标 + 模式化 base 命名（765-771 行）+ 默认响度路径 `.prenorm.mp4` 中转（784-794 行）。

## 三、外部连接：EDL 是唯一入口，grade 是唯一软依赖

上游是根 SKILL.md 产出的 `edl.json`（格式在根 SKILL.md:286-305 行）：`sources`、`ranges`、`grade`、`overlays`、`subtitles` 五字段逐一消费。`resolve_subtitles_path`（96-107 行）处理 agent 常写的相对路径歧义：先相对 EDL 目录、再相对 cwd（100-102 行），都不存在则**硬错退出**（98-99 行注释："渲染下去就静默发出无字幕视频"）。

对 grade.py 是全仓唯一的跨 helper import（32-40 行）。对转录目录只读：`build_master_srt` 读 `transcripts/<source名>.json`（487 行），由 transcribe.py 生产。三个测试按路径 `spec_from_file_location` 加载本模块（test_render_captions.py:9-13 行），不依赖包安装。

## 四、数据流：edl.json → clips_*/seg_NN.mp4 → base*.mp4 → master.srt → final.mp4

输入 JSON（路径表+浮点区间+overlay 起止），中途产物三层（分段 mp4、拼接 base、prenorm 中间件），输出 mp4 + 可选 srt。字幕数据流最值得记：Scribe 词级 JSON → `_words_in_range` 按段区间筛词（418-430 行，只留 type=="word" 且时间相交的）→ `chunk_words` 分块 → 输出时间轴换算 → SRT 三元组。tests/test_render_captions.py:21-26 用真实 take 的 Scribe 时间戳做夹具，37 行期望分块 `["90% of", "what a web", "agent does", "is completely", "wasted.", "We fix this."]`——"does is" 跨 0.34s 停顿必须断开（41-43 行注释），73 行断言首条 cue `00:00:00,090`（词 2.64s 减段起点 2.55s 恰 0.09s），Rule 5 的精确回归锚。

## 五、设计决策与取舍

**"每段一次编码、后续全 copy"**是性能与画质的核心取舍：分段时把调色、缩放、HDR 映射、淡入淡出、帧率统一全做完，之后尽量零重编码；唯一不可避免的二次编码在合成步，故分段档 CRF 20、合成档更精 CRF 18 补偿。反面：单遍 filtergraph 是根 SKILL.md:333 列名的反模式（双重编码）。

**探测失败一律降级**：HDR 失败按 SDR、竖屏失败按横屏、fps 失败按 24、调色导入失败用字面量预设、响度测量失败降单遍。但**字幕文件缺失是唯一硬错**（107 行）：其余降级只损画质，无声字幕会静默伤害全部观众。

**三档质量阶梯**对应三种意图：draft 验切口、preview 给用户看、final 出品——不同名目录（334 行）互不污染。**MarginV=90 用注释钉死**（44-51 行），防后来者"优化"掉。

## 六、新人提示：坑与勘误

1. **MarginV 勘误（钉版）**：模块 docstring 第 13 行仍写"MarginV=35"，根 SKILL.md:188、194 也写 `MarginV=35`——但代码 56 行实际是 `MarginV=90`，44-51 行注释解释了从 35 提到 90 的平台安全区理由。**以 56 行为准**。
2. **grade.py 须与 render.py 同目录**：33 行 import 无 sys.path 处理；把 render.py 复制到别处单独跑会**静默**走降级 stub（调色悄悄变 subtle，无报错）。判断：日志没有 auto-grade 分析行就是降级了。
3. **--fps 是全局一致性阀门**：多源混帧率 EDL 必须显式传 `--fps`，否则 349-350 行取第一源帧率，后段帧率不同时 concat 在部分播放器会异常。
4. **其余小坑**：字幕路径双解析（100-102 行）意味着 cwd 下同名文件会意外命中；`--no-loudnorm` 才直出，默认走 790-794 行 prenorm 中转；测试按路径 spec 加载模块（test_render_captions.py:12-13 行），改文件名会全数崩。
