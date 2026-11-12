# video-use 新人上手文档（ONBOARDING）

> 基于知识图谱（84 节点 / 128 边 / 12 层 / 13 步 tour，commit `43cfc56`），结论均经源码核实，锚 `file:line`。

## 1. 项目一句话定位

video-use 是 browser-use 组织的**对话式视频剪辑技能**：素材丢进文件夹，与 Claude Code（或任何 shell agent）对话，拿回 `final.mp4`（README.md:7-9）。没有时间线界面与预设菜单——剪辑决策全部由 LLM 在对话中完成，仓库只提供注入 agent 的**方法论提示词**（SKILL.md）与六个**执行脚本**（helpers/）。

核心洞察："LLM 从不看视频，它**读**视频"（README.md:73）——常驻词级转录 + 按需视觉合成图，用约 12KB 文本替代朴素抽帧的 45M token 噪音（README.md:89-90）。

**与 browser-use 主框架的关系**：哲学同源、领域不同——browser-use 给 LLM 结构化 DOM 而非截图来操控浏览器，video-use 把同一思想移植到视频（README.md:92）。共同命题：agent 的瓶颈在感知表示。

## 2. 总体架构

图谱 12 层归并为四大子系统：

- **配置基座（L01）**：pyproject.toml 声明五依赖与 manim 可选组（pyproject.toml:7-16），但 `py-modules = []`（pyproject.toml:23）——不打包含包，脚本按 `python helpers/<name>.py` 裸调用；`.env.example` 仅一条 `ELEVENLABS_API_KEY`（.env.example:1）。
- **文档与提示词层（L02/L03）**：README.md 面向人；install.md **面向执行安装的 agent**（install.md:1-4）。SKILL.md 是全仓灵魂：7 条原则（SKILL.md:10-16）、12 条硬规则（SKILL.md:18-33）、EDL 契约与反模式（SKILL.md:324-342），helpers 调用方式全在此约定。
- **执行层（L04-L06）**：转录三脚本"素材进、文本出"；timeline_view.py 唯一视觉下钻工具；render.py + grade.py 渲染成片。
- **manim 技能线（L08-L11）与测试（L12）**：`skills/manim-video/` 是独立的 3B1B 风格动画管线（SKILL.md:211），入口三件套 + references/ 14 份参考；tests/ 三份单测全针对 render.py，锁字幕/fps/方向三类契约。

## 3. 核心链路：raw footage → final.mp4

流水线（README.md:96-100）途经文件：

1. **Inventory**：`transcribe_batch.py <dir>` 按扩展名扫描、4 worker 并发、逐文件缓存跳过（transcribe_batch.py:26,46,78）。
2. **转录**：transcribe.py = ffmpeg 抽 mono 16kHz WAV（transcribe.py:74-81）→ 峰值预检低于 -60 dBFS 拒传（transcribe.py:165-173）→ Scribe 上传固定 diarize+音频事件+词级时间戳（transcribe.py:90-95）→ 落盘 `edit/transcripts/<stem>.json`（transcribe.py:180）。
3. **压包**：pack_transcripts.py 按 ≥0.5s 静音或说话人切换切短语（pack_transcripts.py:38-122），产出 `takes_packed.md`——编辑子代理挑 cut 的主工件，token 约为原始 JSON 十分之一（pack_transcripts.py:5-7）。
4. **对话提案**：产出 4-8 句策略并**等确认**（SKILL.md:88）；多 take 时 spawn 编辑子代理选 take（SKILL.md:131）。
5. **执行**：写出 `edl.json`（契约 SKILL.md:288-305），`render.py` 四步固定顺序（render.py:3-9）：逐段提取（调色+30ms 淡入淡出，render.py:284-286）→ `-c copy` 无损 concat（render.py:385-401）→ 单滤镜图合成、字幕殿后（render.py:675-680）→ 两遍 loudnorm 到 -14 LUFS（render.py:529-531）。
6. **自评**：对**渲染输出**在每个切点 ±1.5s 跑 timeline_view 查跳变/爆音/字幕被盖（SKILL.md:91-97），上限 3 轮（SKILL.md:103）。

全链只烧一次外部 API（Scribe），其余全本地 ffmpeg/Python。

## 4. 关键模块深读

**transcribe.py（242 行）**：`transcript_path` 把音轨编号编进文件名，单/批缓存判定共用同一函数不漂移（transcribe.py:116-125）；`--audio-track` 专为 OBS 双轨设计（transcribe.py:214-220）。

**pack_transcripts.py（207 行）**：Scribe `words` 含 word/spacing/audio_event 三类型，静音信息藏在 spacing 条目起止时间里（pack_transcripts.py:90-98）；flush 闭包修复空格标点（pack_transcripts.py:74）。

**timeline_view.py（393 行）**：胶片条（帧高 180，timeline_view.py:201）+ 波形带 + 词标 + 静音阴影；`compute_envelope` 用 stdlib wave 手动读 PCM，注释明言"avoid librosa as a hard dep"（timeline_view.py:89-93）；定位为决策点工具、禁止扫描循环调用（timeline_view.py:9-11）。

**render.py（802 行，全仓最重）**：四类边界处理使它远超 ffmpeg 包装器——HDR→SDR tone mapping（render.py:123-132）；旋转判定只认 side_data（render.py:149-186）；fps 用 Fraction 归一、失败回退 24（render.py:189-212）；多源 EDL 统一取第一源 fps 保证无损 concat（render.py:341-352）。

**grade.py（376 行）**：预设查表（subtle/neutral_punch/warm_cinematic/none，grade.py:38-63）+ 数学自动分析；`auto_grade_for_clip` 用 signalstats 抽帧统计亮度/对比度/饱和度（grade.py:78-175），修正硬夹 ±8%（grade.py:246-249），目标是"clean, not graded"（grade.py:14-16）。

**skills/manim-video 提示词库**：入口 SKILL.md（v1.0.0）实际含 **12 个主节**与 7 模式路由表（skills/manim-video/SKILL.md:29-39）；创意标准是精华：几何先于代数（:15）、不透明度三层 1.0/0.4/0.15（:19）、每动画后 `self.wait()` 呼吸感（:21）。references/ 14 份覆盖方法论/API 速查/出品闸/排障；setup.sh 自检四依赖（setup.sh:8-11）。主技能 overlay 需要动画时切换到该技能（SKILL.md:211）。

## 5. 数据流与制品

所有会话制品集中 `<videos_dir>/edit/`，技能目录保持干净（SKILL.md:33,41-56）：transcripts/*.json 是不可变缓存，源不变永不重转写（SKILL.md:29），track 后缀支持多音轨（transcribe.py:124）；takes_packed.md 是编辑"菜单"，由 transcripts 幂等派生；edl.json 是剪辑决策单一事实源；clips_graded/（render.py:333-335）存逐段产物（render.py:365）；base.mp4 与 *.prenorm.mp4 是 concat 与 loudnorm 的中间件（render.py:790）；master.srt 字幕时间 = `word.start - segment_start + segment_offset`（render.py:473）；verify/ 收 timeline_view 输出（timeline_view.py:377）；project.md 为会话记忆（SKILL.md:309-322）。

素材只读、转录只写一次、其余可由 edl.json + transcripts 幂等重建。

## 6. 设计决策与取舍

- **提示词为主体，代码是执行器**：全仓 Python 约 2250 行，文档体量更大。SKILL.md 强调"每个具体值都是 worked example 而非命令，唯一必须遵守的是 Hard Rules"（SKILL.md:14,35），并专设 Anti-patterns 预先钉死失败模式（SKILL.md:324-342）——品味进提示词、正确性进代码。
- **软依赖降级**：render.py 对 grade.py 的导入包 try/except，失败回落内联 stub——`get_preset` 返回空串、`auto_grade_for_clip` 返回固定 `eq=contrast=1.03:saturation=0.98`（恰是 subtle 预设值，render.py:32-39 对照 grade.py:41）——grade.py 丢失只损失自动调色，不阻断渲染。
- **依赖声明冗余是已知取舍**：librosa/matplotlib 声明于 pyproject.toml:9-10 但零 import（timeline_view.py:89 明言绕开 librosa），运行时必需仅 requests/pillow/numpy + ffmpeg。
- **不打包**：helpers 以裸脚本与 SKILL.md 同目录共生（install.md:28），注册方式是符号链接整个仓库目录（install.md:72-79）。
- **token 经济学驱动一切表示设计**：pack 的 0.5s 阈值与 timeline_view 的决策点禁令（timeline_view.py:9-11）是同一预算约束的产物（README.md:79-90）。
- **品味与平台规则分离**：render.py 的 MarginV=90 注释是典范——竖屏平台 UI 盖住底部约 25-30%，libass 以 PlayResY=288 自动缩放，MarginV=90 让字幕在任何宽高比下避开 UI（render.py:42-51）。

## 7. 上手路径：第一天阅读路线

按 tour 顺序：

1. **t01 门面**（15 分钟）：README.md 建立两层读视频图景；扫 install.md 感受面向 agent 的安装文档。
2. **t02 宪法**（1 小时，全仓最重要）：精读 SKILL.md——7 原则、12 硬规则、EDL 格式、反模式。
3. **t03 转录层**：三脚本按序读，重点看静音预检、缓存约定、group_into_phrases 的三类型词处理。
4. **t05 视觉层**：timeline_view.py 配 poster.html 对照读——poster 用内联 SVG 复刻了工具输出形态。
5. **t06 渲染层**：render.py 四步主流程（render.py:3-9）+ grade.py，再钻 HDR/旋转/fps 边界处理。
6. **t07 测试**：三份单测反向读 render——用例即契约。
7. **t08-t14 manim 线**（可延后）：入口三件套 → 方法论与 API 速查 → 出品闸与排障。

动手验证：`python helpers/grade.py --list-presets`；`bash skills/manim-video/scripts/setup.sh`（别照抄 README 旧路径，见下节）。

## 8. 常见坑与勘误

文档-代码漂移与坑（按严重度）：

1. **SKILL.md 字幕示例与代码不符**：SKILL.md:188-195 示例写 `MarginV=35`，但 render.py:56 实际 `SUB_FORCE_STYLE` 为 `MarginV=90`——代码已升级为平台安全区规则（render.py:42-51），文档未同步，以代码为准。
2. **manim README 引用已迁移旧路径**：skills/manim-video/README.md:22 写 `skills/creative/manim-video/scripts/setup.sh`，多出 `creative/` 一级，实际在 `skills/manim-video/scripts/setup.sh`，照抄必报文件不存在。
3. **timeline_view 两处坑**：:292 注释说词标"≥120ms"但 :302 实际 50ms；`--edl` 是未实现占位，传入即 `sys.exit`（timeline_view.py:355-356）。
4. **工作流实为 8 步非 6 步**：README.md:96-100 流水线图六段，但 SKILL.md:83-104 列了 8 个编号步骤，"六步"是 README 口径。
5. **依赖清单含零消费项**：pyproject.toml:9-10 的 librosa/matplotlib 零 import，最小安装只需 requests/pillow/numpy + ffmpeg。
6. **测试加载方式**：三份单测均经 `importlib` 动态加载 render.py（tests/test_render_captions.py:9-13）——仓库无包结构，写新测试沿用此范式。

### 勘误（图谱 summary vs 源码）

- 图谱称 manim SKILL.md 为"29 节"：实测 `##` 主节 12 个、`###` 子节 16 个，以源码层级为准。
- 图谱的"约 12KB"源自 README.md:79 宣传值（一小时素材量级），非脚本常量。
- 其余图层 summary（分层、职责、函数行号）抽查与源码一致。
