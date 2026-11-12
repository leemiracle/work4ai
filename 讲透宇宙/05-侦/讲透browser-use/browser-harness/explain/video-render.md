# video_render.py — 审阅页生成与"验证后才能导出"的 MP4 出口

## 一、角色定位

`video_render.py` 是视频子系统的**第二只手**：`video.py` 负责把录制事件编译成 composition.js（纯数据加工），本文件负责一切需要**真实浏览器和真实 ffmpeg** 的环节——审阅拼图、全分辨率隐私脱敏帧，以及五重门禁通过后导出并验证 MP4。文件头自述（video_render.py:2）："Prepare compact renderer review sheets, then export and verify an MP4"。

它存在的原因是一条产品级铁律：**导出的视频必须先被人审阅过**。`export()` 第一件事就是查 `--reviewed` 标志（video_render.py:415-416），没有它直接抛 "inspect the review sheet and full-resolution privacy frames, then rerun with --reviewed"。
## 二、内部结构

文件按流水线阶段自上而下排布：

1. **常量与清单（video_render.py:23-38）**：`TEMPLATE` 指向随包的 `video-template.html`（:23）；`MARKER`（:24）是子进程 stdout 行协议前缀；`REVIEW_ARTIFACTS`（:25-31）列出五个导出前必须未被改动的产物；`OBSOLETE_REVIEW_FILES`（:32-38）是历史遗留审阅产物，review 时删。
2. **编译包装（:41-54）**：`compile_recording()` 调 `video.verify_source_manifest` + `video.compile_brief`，`write` 参数决定是否落盘——review 写、export 复核只算不写（:427）。
3. **采样策略（:57-78）**：`review_samples()` 决定每个 beat 何时截图。explanation 型 beat 按每条 reveal 等距采样（首条 1.1s、末尾留 3.0s，:65-66）；普通 beat 取 1.0s（有卡片）或 `duration/2`（无卡片，钳 0.12-0.5s，:75）。
4. **本地 HTTP 服务（:81-99）**：`serve()` 用 `ThreadingHTTPServer` 绑 `127.0.0.1:0` 随机端口，录制目录当静态根，产出 `http://127.0.0.1:<port>/video.html`；`_QuietHandler`（:81-83）压访问日志。
5. **浏览器驱动（:102-204）**：`run_harness()`（:106-123）以 `sys.executable -m browser_harness.run` 起子进程跑内嵌 Python，从 stdout **倒序**找 `MARKER` 行解析 JSON（:120-122）。`_review_browser()`（:126-204）生成那段代码：开新标签、等 `window.videoReady()`、跑 preflight/clickVisibility、按 samples 逐点 seek+截图，normal 与 reduced（CDP `Emulation.setEmulatedMedia` 注入 `prefers-reduced-motion: reduce`，:147-148）各一遍。
6. **拼图与脱敏（:207-274）**：`contact_sheet()`（:207-225）用 PIL 拼 4 列 400×225 瓦片审阅大图；`masked_frame()`（:228-251）按 composition 的 `redact` 矩形画圆角遮盖块（pad/fill/stroke/radius 逐矩形可覆盖全局配置，:239-246）；`privacy_review()`（:254-274）对 `video.used_frames()` 每帧生成脱敏 JPG 存 `.privacy-review/`。
7. **主编排 `review()`（:277-331）**：删过期文件→编译→拷模板→隐私帧→起服务→浏览器审阅→汇总 errors/warnings（preflight 错误、点击落在安全视口外都算 error，:301-304）→拼图→写报告（含五产物 sha256，:317-319）。
8. **导出 `export()`（:414-524）**：见下节数据流。

## 三、外部连接

- **video.py 受控环**：`from . import video`（:20）只借其纯函数（load_composition/compile_brief/write_composition/verify_source_manifest/used_frames/file_hash/HOUSE_STYLE/SOURCE_MANIFEST/load_revealed_text/load_json）。反向依赖是延迟的：CLI 的 `video review|export` 经 run.py:360-363 进 video.run_cli，后者在函数体内 `from . import video_render`（video.py:733-737）委托回来，避免循环导入。
- **browser_harness.run 自举**：`_harness_command()`（:102-103）用 `python -m browser_harness.run` 起新 harness 会话——渲染器用自家 harness 驱动浏览器，吃自己的狗粮。
- **video-template.html**：渲染器唯一 HTML 入口，review 时 `shutil.copy2` 进录制目录（:282），export 时 hash 强校验与包内模板一字不差（:437-439）。
- **ffmpeg/ffprobe**：外部二进制依赖，缺失即抛（:417-418）。
- **Chrome 下载机制**：导出靠页面内 `window.exportVideo()` 触发 MediaRecorder 下载，父进程用 CDP `Browser.setDownloadBehavior` 重定向到目标目录（:356）。

## 四、数据流

**review 链**：edit-brief.json + recording-summary.json + events.jsonl →（compile_brief）→ composition.js 落盘 → 模板拷入 → 隐私帧 JPG + 双模式 PNG → 拼图 + renderer-review.json（errors/warnings/时长/五产物 hash/耗时）→ 退出码 `1 if errors else 0`（:331）。

**export 链**（video_render.py:414-524）分五段计时：
1. **门禁（:415-449）**：`--reviewed` 标志 → ffmpeg 存在 → renderer-review.json 无 errors → composition 与重算结果逐字节相等（:428-429）→ 五产物 hash 与 review 报告一致（:433-436）→ 渲染器与共享模板 hash 一致（:437-439）→ 输出必须 .mp4 且不覆盖已有文件（:444-449）。
2. **捕获（:451-479）**：_start_export 等 videoReady、preflight/clicks 再验，轮询 webm 出现且尺寸两连不变（:465-471），截止 `expected+30` 秒；finally 里 `_close_editor` 恢复不了 Chrome 下载行为就抛错（:475-478）。
3. **转码（:481-487）**：`libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart`（:484-486）。
4. **验证（:489-494）**：ffprobe 时长与预期差不得超过 `max(1.0s, 8%)`（:492）；再整片解码 `ffmpeg -err_detect explode -f null -`（:494）抓坏帧。
5. **终检（:496-524）**：抽三帧（:498-501）拼终检图，写 video-export.json（含 sha256 与四段耗时）。

## 五、设计决策与取舍

- **审阅不可绕过，产物被 hash 钉死**。review 的价值依赖"人看到的就是导出的"，export 用三层 hash（composition 重算相等、五产物 hash、模板 hash）封死 review 后偷改的口子——证明链先于产出。
- **用自家 harness 驱动浏览器 + MARKER 行协议**（:106-123）。不引入第二个浏览器栈，把一段 Python 代码喂给 `browser_harness.run`，用 stdout 标记行回传结果。零新依赖，代价是协议脆弱：任何 helper 往 stdout 打印都会污染（mcp_server.py 同款问题）。
- **`BH_RECORD=0`（:107）**：渲染期子 harness 显式关录制，否则"为录制生成视频"会把渲染过程又录进去，无限递归。
- **webm 中转而非直出 MP4**：Chrome MediaRecorder 只产 webm，转码交给 ffmpeg。时长容差 8%（:492）正是给 MediaRecorder 计时抖动留的。
- **reduced-motion 双模式审阅**（:147-148, :295-308）：减动效与正常版本都要过检，两类截图都进拼图。
- **`_close_editor` 失败必须报错**（:475-478）：Chrome 下载行为不恢复默认，用户后续下载会静默落错目录，宁可中断导出。
- **webm 稳定判据用"尺寸两连不变"**（:467-470）而非 `.crdownload` 消失，兼容 Chrome 下载中间态命名差异。

## 六、新人提示

- **先 review 后 export 是硬顺序**。直接 export 会连吃三个错：没有 `--reviewed`（:416）、没有 renderer-review.json（:421）、即便有也要重验 composition（:429）。
- **勘误：review 产物有三件**——`video-review-contact-sheet.jpg`（拼图）、`.privacy-review/`（全分辨率脱敏帧）、`renderer-review.json`（机器可读报告）。看拼图没问题 ≠ 看原始脱敏帧也没问题，后者刻意留全分辨率供细查。
- **`comp != expected_comp` 报错（:429）最常见诱因**：review 后手改了 edit-brief.json 或 events.jsonl。任何输入变动都要重跑 review；composition 不含时间戳噪声，逐字节比较稳定。
- **导出卡在"timed out waiting for webm"（:473）**：查 Chrome 是否弹下载许可、目标盘是否满；轮询要求尺寸两连稳定，网络盘抖动可能拖到 deadline。`-err_detect explode`（:494）是全片解码校验，长视频这段可能比捕获还慢，不是卡死。
- **改 `video-template.html` 须同版本发布**：export 拿录制目录里的 video.html 与包内 TEMPLATE 对 hash（:437-439），旧模板直接判死，重跑 review 拷新即可。也不要加"跳过审阅"的后门参数——五重门禁是隐私防线，`--reviewed` 的语义就是"人已看过并对此负责"。
