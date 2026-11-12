# helpers/pack_transcripts.py 精讲 — 从原始转录到 LLM 主阅读视图的 token 压缩器

## 一、角色定位：Principle 1 点名的"唯一值得存在的派生工件"生产者

video-use 架构里有个反直觉的立场：根 SKILL.md:10 Principle 1 规定 LLM 从原始转录推理，**反对**预计算各种派生索引（328 行反模式清单明禁"带 USABILITY/tone 标签/镜头分层的层级化预计算格式"），唯一例外就是本文件的产物——10 行原文："The only derived artifact that earns its keep is a packed phrase-level transcript (`takes_packed.md`)"。`pack_transcripts.py`（207 行）就是这唯一例外的生产者，根 SKILL.md:76 的一句话规格："transcripts/*.json → takes_packed.md (phrase-level, break on silence ≥ 0.5s)"。

它为什么能豁免？因为解决的是**上下文经济学**问题而非决策问题：6-7 行 docstring 给出账目——一小时素材的原始 Scribe JSON 约十倍于打包后 markdown（"fits one hour of takes in a tenth the tokens"），且打包后仍保留词边界精度（每行带 `[start-end]` 时间前缀）。编辑子代理选段（根 SKILL.md:129-164 的 brief 模板，INPUTS 第一项就是 takes_packed.md）、主对话"预扫描问题"（根 SKILL.md:86）都读它。

## 二、内部结构：三个纯函数 + 一个格式化器

**`format_time`（24-27 行）**`f"{seconds:06.2f}"`——固定 6 字符宽（如 `002.52`），docstring 点明目的是对齐（"fixed 6-char width for alignment"）：所有行首时间前缀等宽对齐，肉眼扫读时时间成一列竖线。**`format_duration`（29-35 行）**双形态：小于 60 秒 `43.0s`，否则 `3m 12.5s`。

**`group_into_phrases`（38-122 行）**是算法核心，111 行单遍状态机。输入 Scribe `words` 数组，其三类型结构在 45-47 行注释钉版：`'word'`（真词）、`'spacing'`（词间空隙，**静音信息由它的 start/end 承载**）、`'audio_event'`（笑声掌声等）。两条断句规则：

1. **静音断**（两处实现）：91-99 行遇 spacing 条目时算 `gap = end - start`，超阈值即 flush；112-113 行对 word 条目再算一次与前一词尾的间隙——双保险覆盖 Scribe 输出中 spacing 缺失或错位的情况。
2. **说话人断**（108-109 行）：`speaker_id` 变化即 flush（二重判空：current_speaker 与 speaker 都非 None 才比较，容忍 Scribe 偶发的缺字段）。

flush 闭包（54-84 行）做文本整理：audio_event 文本强制括号包裹（65-67 行，`(laughs)` 风格）；74 行四个 replace 把 ` ,`→`,` 等标点贴合（Scribe 逐词输出天然带空隙）；75 行短语终点取末词的 end 回退 start。119 行 `prev_end = w.get("end", start)` 持续滚动词尾时间。

**`pack_one_file`（125-134 行）**单文件封装：json 读入→分组→时长取 `phrases[-1]["end"] - phrases[0]["start"]`（131 行，注意这是**首尾短语跨度**而非容器时长，无声的头部尾部不计入）。

**`render_markdown`（137-162 行）**装配输出：139-143 行文件头三行（标题、分组规则说明、"Use `[start-end]` ranges to address cuts in the EDL"——直接教下游怎么用时间前缀写 EDL）；145 行每 take 一节 `## C0103  (duration: 43.0s, 8 phrases)`；147 行空转录打 `_no speech detected_`；153-157 行剥 `speaker_` 前缀（Scribe 返回 `speaker_0`，输出 `S0` 省字符）；160 行正文行格式 `  [002.52-005.36] S0 Ninety percent of what...`——与根 SKILL.md:122 示例行逐字符同构。

**`main`（165-202 行）**：`--edit-dir` 必填；`--silence-threshold` 默认 0.5（171 行）；`-o` 覆盖默认输出 `<edit-dir>/takes_packed.md`（194 行）。187 行 `sorted(glob("*.json"))` 保证 take 顺序确定，197-202 行收尾统计短语数/总时长/KB。

## 三、外部连接：转录目录的读方，编辑子代理的写方

上游直接消费 transcribe.py / transcribe_batch.py 落盘的 `transcripts/*.json`（183-189 行），依赖其 words 三类型契约（45-47 行）——契约由 transcribe.py 的 `timestamps_granularity=word` + `tag_audio_events=true` + `diarize=true` 三参数共同保证（transcribe.py:92-94 行）。注意它 glob 全部 `.json` 而非按 EDL sources 过滤——目录里有什么打包什么，包括 `--audio-track` 生成的 `.track1.json` 变体会成为独立一节。

下游两方：**编辑子代理**（根 SKILL.md:135 INPUTS 第一项、L153 规则"Start/end times must fall on word boundaries"直接消费时间前缀做切割寻址）；**主对话**在流程第 2 步预扫描 verbal slips（根 SKILL.md:86）读它。根 SKILL.md:118 的说明（"This is the artifact the editor sub-agent reads to pick cuts"）是它的需求规格书。timeline_view.py 是它的可视化对偶——一个把转录压成文本供读、一个画成波形供看，但后者自我定位"on-demand drill-down, not a background index"（timeline_view.py:10-11），与本文的全量打包互补而非冗余。

## 四、数据流：words JSON → phrases 列表 → 等宽 markdown

数据三次变形：(1) **解析**：`data.get("words", [])` 原样进状态机，无预处理；(2) **分组**：产出 `{start, end, text, speaker_id}` 短语字典列表——时间戳继承自词级数据（短语 start=首词 start，end=末词 end），精度仍词级；(3) **渲染**：markdown 文本，有损压缩点仅两处——标点贴合（74 行）与 speaker 前缀缩短（156 行），词文本零修改（保证预扫描能发现口误原文）。

坐标系全程保持**源视频本地时间**（秒浮点），不做输出时间轴换算——换算是 render.py build_master_srt 的职责（Hard Rule 5）。这个纪律让 takes_packed.md 里的时间可以直接抄进 EDL 的 ranges（根 SKILL.md:143 规则的现实基础）。反向流不存在：改阈值就整文件重生成（幂等，纯函数式）。

## 五、设计决策与取舍

**0.5 秒阈值 vs 0.4 秒切割线的双阈值体系**：本文件断句阈值默认 0.5s（171 行），而根 SKILL.md:112 说"Silences ≥400ms are usually the cleanest cut candidates"、timeline_view.py:135 的 find_silences 默认 0.4——**阅读分组比切割候选更保守**。这是有意分工：短语分组太碎则行数膨胀（token 省不下来）、太长则一行内混入多个可切点；0.5s 保证一行基本是"一口气说完的话"，切割决策在更细的 0.4s 粒度由编辑代理自行做。阈值是参数（`--silence-threshold`），快语速素材可调紧。

**为什么不做更多派生**（填充词标注、take 评分、镜头分类）：根 SKILL.md:328-329 立场是"LLM picks better than any heuristic you'll write"——预计算启发式只会稀释判断。takes_packed.md 例外恰因它**不做任何判断**，只做无损压缩：断句是客观规则（静音/说话人），不是质量评分。

**等宽时间前缀是接口设计**：`[002.52-005.36]` 让时间寻址成为文本协议——编辑代理输出 EDL 时直接回抄这两个数字（根 SKILL.md:160 示例 `"start": 2.42, "end": 6.85` 正是这种回抄），人类用户也能肉眼对表。6 字符宽（26 行）支持到 999.99 秒即 16 分钟单 take，超出会宽一格但仅影响对齐不影响功能。

**每 take 一个 `##` 节**（145 行）而非平铺：markdown 层级让长文档的 take 定位靠标题跳转，duration+短语数的节头（`duration: 43.0s, 8 phrases`）本身就是决策摘要——代理扫节头即可预估素材量。

**duration 口径取首尾短语跨度**（131 行）：比容器时长更贴切——剪辑者关心的是"有话可剪的部分"多长，片头片尾的死静音本來就要切掉。

## 六、新人提示：坑与勘误

1. **空转目录是硬错**：`transcripts/` 不存在或无 `.json` 直接 `sys.exit`（185、189 行）——先跑 transcribe/transcribe_batch 再跑本脚本，顺序不可倒。
2. **`.track1.json` 会成为独立 take 节**：多轨转录的变体文件名（transcribe.py:124）被 glob 一视同仁打包，同一素材会出现两节内容相近的 take——编辑代理若不知情可能重复选段。多轨工作流里要么删旧轨转录、要么在 brief 里注明。
3. **speaker_id 为 None 时不显示说话人标签**（158-159 行 spk_tag 空串）：单说话人素材常见全文件无 S 标签，别当成 diarize 失败——diarize 开着但 Scribe 对独白也可能省 speaker_id。
4. **阈值改动影响整个下游话语体系**：`--silence-threshold 0.3` 产出更碎的行，编辑代理的"一行一短语"心智模型随之变细；改完后历史对话里引用的行号/短语全部失效，应整会话重读。
5. **6 字符时间宽的隐性上限**：超过 999.99s 的 take 时间前缀变 7 字符（如 `1002.52`），对齐列断——纯视觉问题，但自动解析该行的正则若写死 `\d{6}\.\d{2}` 会漏匹配。
6. **重跑是安全的、且应当重跑**：新转录进目录后必须重跑本脚本刷新 takes_packed.md，没有增量模式——纯函数全量重建（191-195 行）保证一致性，代价是大目录重打包耗时以秒计，可忽略。
7. **它不做音频事件的时间展开**：`(laughs)` 只是文本标记，其 start/end 留在 words 里但短语行只显示文本——需要事件精确时刻得回原始 JSON 查。
