# video.py 精讲 — 录制到成片的编译器：编辑简报、节奏预算与隐私闸门

> 源码：`src/browser_harness/video.py`（749 行）｜图谱层 L07「视频编译与渲染」

## ① 角色定位

video.py 是 `browser-harness video init|review|export` 子命令的实现（run.py:360-363 分发过来），把 recorder 产出的"动作+截图"文件夹**编译**成一段解说视频。它自己不渲染像素：播放器是 video-template.html（读 `window.COMPOSITION`），review/export 由 video_render.py（审片表格+ffmpeg）延迟代劳（video.py:733-737）。这 749 行是**编译器**——把人工/agent 撰写的 `edit-brief.json` 与 `recording-summary.json` 校验、节拍化、脱敏，输出 `composition.js`。

设计哲学浓缩在 `BriefError` 的 docstring 里："An edit brief violates the deliberately small authoring contract"（video.py:96-97）——合同**故意**小：brief 只准写任务/计划/解说/隐私字段，节奏、运镜、配色全部由 `HOUSE_STYLE` 房风锁死（video.py:29-55）。作者是内容编辑，不是样式编辑。

## ② 内部结构

- **三份清单即 schema**（video.py:56-92）：`ACTION_KEYS`（12 个动作字段白名单）、`BRIEF_KEYS`（9 个顶层字段）、`EXPLANATION_KEYS`（afterAction/title/summary/observed/mistake/correction）。`reject_unknown` 对任何越权字段直接 BriefError（video.py:176-179）——不做前向兼容、不静默忽略，逼作者对着报错改稿。
- **脱敏正则组**（video.py:18-28）：`SENSITIVE` 抓邮箱/租户 ID/UUID；`ROUTE_UNSAFE` 额外抓 `@ ?# ://`——路由字幕必须语义化（"搜索页"），原始 URL 一律不许上画面；`OPAQUE_HEX` 强制遮盖矩形填充色为不透明 6 位 hex，半透明遮盖=能被看清的脱敏。
- **源料冻结**（video.py:140-173）：`init` 时 `write_source_manifest` 对 events.jsonl/meta.json/recording-summary.json/全部帧算 sha256 落 `video-source.json`；`review/export` 前 `verify_source_manifest` 全量复验——初始化后源料被改动即拒绝编译。
- **时长模型**（video.py:198-304）：卡片时长=字数/380wpm（card_duration，video.py:198-207）；动作时长按类型起步（点击 1.15s、打字 0.6s+0.035s/字符，video.py:261-277）；总预算 `duration_budget`：22s 基础 + 超出 5 个动作每个 +1.25s + 超出 1 条解说每条 +3s + raw 转 card 每个 +0.55s，**硬顶 32s**（video.py:280-292）。超预算即 BriefError，报错文案就是编辑指南："Shorten card copy... viewers can pause for detail"（video.py:586-591）。
- **叙事节奏警察**（video.py:307-336）：`validate_narration_cadence` 两条规则——段内（卡片之间）超半数动作带旁白=旁白不"粘"；连续 3 个动作都换旁白=文本与截图同拍。逐帧复述被结构性禁止，旁白只能在"想法变化"时出现。
- **编译主体**（video.py:339-614）：`compile_action`（逐动作→beat）、`compile_brief`（组装 intro 卡→动作 beats→解说卡→outcome 卡→预算校验→composition dict）。
- **隐私闸门**（video.py:438-470）：composition 用到的每帧必须在 `privacy.reviewedFrames` 里（缺一即错，video.py:445-447）；`redact` 只许遮 composition 用到的帧；矩形几何必须有限正数。
- **init 的安全降采样**（video.py:661-713）：见数据流。

## ③ 外部连接

- **上游 recorder**：events.jsonl 是唯一源料；`init --require-explicit` 拒绝 auto 录制（meta.auto 为真即 BriefError，须用 start_recording 返回的精确路径，video.py:667-668）。
- **下游 video_render.py**：`review(recording)` 生成审片材料，`export(recording, output, --reviewed)` 用 ffmpeg 导出 MP4——不带 `--reviewed` 直接 export 会被拒，提示先看审片表与全分辨率隐私帧（video_render.py:414-418）。
- **video-template.html**：`shutil.copy2` 进录制目录（video.py:670），播放器首行 `const C = window.COMPOSITION`（video-template.html:26）；`write_composition` 产出 `window.COMPOSITION = {...};` 前缀可往返解析的赋值文件（video.py:617-627 的 load_composition 校验前后缀）。
- **run.py/recorder**：CLI 分发与源料生产（run.py:360-363；recorder 的 `_CTX_JS` 焦点框、`_mask` 密码掩码在本阶段被消费）。

## ④ 数据流

**`video init <recording>`**（video.py:661-713）：逐行读 events.jsonl → 只留有帧的事件 → 每条经 `safe_text/safe_label` 降密（type_text 一律 `<typed text hidden>`；密码或命中 SENSITIVE 的值 `<sensitive>`；标签截 120 字符，video.py:642-658）→ 落 `recording-summary.json`（sourceLine/cursor/box/password 等字段）→ 写源清单。输出提示下一步写 edit-brief.json（video.py:712）。

**`video review`**：load edit-brief → `load_revealed_text` 重读原始 events.jsonl 建 `sourceLine→明文` 映射（仅非密码打字事件，video.py:622-639）→ `compile_brief`：
- 校验 plan 2-5 条、outcomes 1-5 条、actions 非空（video.py:477-481）；
- 首个动作的视口成为全片视口，任何引用事件视口差超 `VIEWPORT_TOLERANCE=2px` 即 BriefError（"split or normalize the recording first"，video.py:250-258）；
- `compile_action` 逐个翻译：click 事件必须有 cursor 坐标、typing 必须有焦点框（video.py:399-418）；`showTyping` 揭示原文的前提=非密码框 + sourceLine 在映射里，否则默认六个圆点+redact 标记（video.py:408-418）；连续动作目标点距离超视口对角线 0.58 倍自动插 `cameraCut`（video.py:425-429）；
- 解说卡按 afterAction 插到对应动作后，固定 Observed/Mistake/Correction 三点结构（video.py:528-547）；
- 节奏校验→预算校验→`validate_privacy`（reviewedFrames 完备性）→ 输出 composition.js（video.py:580-614）。

**`video export --reviewed`**：复验源清单→渲染→ffmpeg 编码+校验（video_render.py:484-500）。

## ⑤ 设计决策与取舍

- **作者合同小、机器权力大**：作者不能调时长、不能改运镜（autoFollow/autoZoom 1.7/cursorDuration 全在 HOUSE_STYLE.motion，video.py:44-53）。换来的是所有成片节奏一致、预算可预测。
- **预算硬顶 32s 与"观众会暂停"**：超时不警告而是拒绝编译，编辑方向被强制为"删"而非"调"。
- **两段式隐私**：静态脱敏在 init（summary 里的敏感文本已替换）；动态隐私在 review/export（reviewedFrames 声明 + redact 矩形 + export 人工确认 flag）。明文只在一个受控通道回流：`load_revealed_text` 按行号映射 + showTyping 显式 opt-in + 密码框绝对禁止揭示（video.py:409-410）。
- **sourceLine 而非帧号关联明文**：帧号会因丢帧重排漂移，events.jsonl 行号在 init 冻结后是稳定主键。
- **init 拒收 auto 录制**：auto 录制无人工在场背书，从源头杜绝"无人审阅的会话被一键成片外流"。

## ⑥ 新人提示（坑/勘误）

- video.py 只是编译器；黑屏/渲染 bug 去 video-template.html，导出/ffmpeg 问题去 video_render.py（ffmpeg、ffprobe 缺失在 export 时才报，video_render.py:417-418）。
- brief 里写错字段名不会静默忽略——`reject_unknown` 报 "unsupported field(s)"，这是特性不是不友好（video.py:176-179）。
- 旁白限 7 词（video.py:215-217）；"narration is sticky" 与 "three consecutive actions" 两条 cadence 报错（video.py:324-336）是编辑最常撞的墙，解法是删中间旁白而非删动作。
- 用了帧却没列入 reviewedFrames 是 review 阶段必报错；反过来 redact 里列了没用到的帧同样报错（video.py:445-450）——两侧都要对齐 composition 实际引用集。
- composition.js 可被 `load_composition` 往返校验（前缀+分号+JSON 三查，video.py:114-127）：手工改它再 review 时，格式走样会被当 BriefError 拒绝，而不是静默半解析。
- 想让打字过程显形：事件必须在 events.jsonl 里有原始 type 行（sourceLine 映射）、不能是密码框、brief 该动作加 `"showTyping": true`——三条件缺一即 BriefError（video.py:409-413）。
