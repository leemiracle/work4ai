# recorder.py 精讲 — 会话录制：每动作一帧一行的观测层

> 源码：`src/browser_harness/recorder.py`（343 行）｜图谱层 L05「会话观测：录制与遥测」

## ① 角色定位

recorder 把 agent 的浏览器会话落成**一个普通文件夹**（docstring 的定义，recorder.py:1-9）：`<BH_AGENT_WORKSPACE>/recordings/<name>/` 下 `meta.json`（元信息）+ `events.jsonl`（每动作一行 JSON：helper 名、坐标/文本、URL、视口、焦点元素框、帧文件名）+ `0001.jpg…`（每动作后的视口截图）。这是刻意去数据库化的设计——文件夹可直接 zip 分享、可被 video.py 逐行重放。

三个铁律写在文件头：跨 CLI 调用用**标记文件**携带激活状态（daemon 完全不感知录制）；run.py 在每个成功 helper 后调 `observe()`，只有 `ACTIONS` 集合内的动作产生帧（recorder.py:12-14）；**录制失败一律吞掉**——观测层绝不允许弄断被观测的运行（recorder.py:14）。

## ② 内部结构

- **`ACTIONS` 白名单**（recorder.py:31-36）：16 个"改变屏幕内容"的 helper（导航/点击/输入/滚动/标签页/等待）。js、page_info、capture_screenshot 等只读 helper 不出帧——注释点明否则检查密集型会话的录制会被无视觉增量的帧撑爆。
- **URL 脱敏**（recorder.py:44-53）：`_URL_SECRETS` 正则把 `code/access_token/id_token/refresh_token/token/assertion/client_secret/session_state/api_key/sig/auth/password/secret` 等凭据类 query/fragment 参数值替换为 REDACTED——OAuth 重定向的授权码 otherwise 会真实落进人们共享的文件夹。
- **页面上下文探针 `_CTX_JS`**（recorder.py:58-67）：一段 JS 收集 url/title/视口/滚动/dpr，加上**焦点元素**的 bounding box 与类型（`input` 字段标记密码框）。焦点框正是视频阶段"镜头推向正在输入的框"的数据来源。
- **开关与偏好**（recorder.py:86-90, 160-191）：优先级 `BH_RECORD` 环境变量 > `config_dir()/recording.json` > 默认关。`BH_RECORD=0` 是硬禁（显式 start_recording 也 raise，recorder.py:102-103）；`set_auto_recording` 原子写（tmp+replace）且非 Windows chmod 600，关闭偏好时顺手清掉 auto 录制的标记文件（recorder.py:180-191）。
- **自动录制生命周期**（recorder.py:204-236）：`BH_RECORD_IDLE`（默认 180s）空闲即翻卷——"上一次动作以来的停顿=一个任务的结束"，防止永远开着的录制把无关会话焊在一起或无限增长；`_auto_start` 静默启动（无 stdout，agent 会解析输出）、meta 带 `auto:True`、同秒冲突加 `-2/-3` 后缀；显式 `start_recording` 永不自动翻卷（recorder.py:228-229）。
- **核心 `observe`**（recorder.py:239-260）：入口即查 ACTIONS 与 BH_RECORD 硬禁；随后两步卫生——auto 录制遇到偏好已关则弃、遇到空闲超阈则弃（recorder.py:247-252）；无活动录制且偏好开则静默 auto 起；`sleep(_SETTLE_SECONDS=0.15)` 等页面重绘再截图；整体 try/except Exception: pass（recorder.py:259-260）。
- **`_capture`**（recorder.py:263-310）：见数据流。
- **`_details`/`_mask`**（recorder.py:313-343）：按 helper 挑最小参数集记录（click 记 x/y，goto 记 to，type 记 text…）；`_mask` 在焦点是密码框时把文本打成圆点，普通文本截 500 字符。

## ③ 外部连接

- **与 helpers 的刻意循环依赖**：helpers.py 底部 `from .recorder import start_recording, stop_recording, recording_dir`（helpers.py:648-650，注释言明"让 recorder 自己的 `from . import helpers` 看到完整定义的模块"）；本模块在 `_capture` 内**延迟导入** helpers（recorder.py:264，行内注释"late: helpers imports recorder at its bottom"）。导入顺序：import helpers → 末尾 import recorder → recorder 顶层不碰 helpers → 首次截图时才反向取用。
- **run.py**：`_traced` 成功路径调 `recorder.observe(name, args, kwargs, duration)`（run.py:174）；`recordings` 子命令消费 `latest_recording/auto_recording_setting/set_auto_recording`（run.py:336-359）。
- **video.py**：录制文件夹是视频管线的源料——`video init` 读 events.jsonl 生成 recording-summary.json（video.py:661-713）。
- **paths.py**：workspace_dir/config_dir 决定 recordings 根与偏好文件位置。

## ④ 数据流

一个动作（如 `click_at_xy(300,400)`）成功返回后：

1. run.py `_traced` → `observe("click_at_xy", (300,400), {}, 0.42)`；
2. 通过 ACTIONS/硬禁/标记文件三道闸（必要时翻卷或 auto 启动）；
3. `sleep(0.15)` 等重绘；
4. `_capture`：先跑 `_CTX_JS` 拿页面上下文（失败则 event 缺这一截但继续，recorder.py:269-272）；再 **`Page.captureScreenshot` 用与 helpers 截图同款的 60 秒预算**（注释：云浏览器截图 routinely 超过 5s 默认 IPC 超时，不调预算则每帧超时被吞、录出零帧录制，recorder.py:278-286），JPEG quality 80；
5. 帧号 = 目录现存 `*.jpg` 计数 +1，写盘用 `open("xb")` 独占模式，撞名（FileExistsError）则号 +1 重试——多进程并发录制同一目录也安全（recorder.py:287-296）；
6. 截图失败不静默：`event["frame_error"] = f"{type(e).__name__}: {str(e) or 'no detail'}"` 截 200 字符——注释专门处理无参异常字符串化为空串的反模式（recorder.py:298-304）；
7. URL/to 字段过 `_scrub_url`（recorder.py:274-276）；写 events.jsonl 用 `errors="replace"`——页面可控字符串（document.title 等）会经 CDP 的 `\uDXXX` 转义带进 lone surrogate，一个就足以毒死整条 trace，统一替换 U+FFFD（与 run.py 给 stdout 的同款药方，注释互相引用，recorder.py:305-310）。

## ⑤ 设计决策与取舍

- **标记文件而非 IPC 状态**：录制状态放在文件系统（`recordings/.active-<BU_NAME>`，recorder.py:93-94），daemon 零参与——录制崩溃不影响控制面，控制面崩溃不丢录制标记。
- **帧 = 动作后快照**（而非前快照或双快照）：每动作一帧、settle 0.15s，把存储成本压到线性且帧帧有"结果"语义；代价是没有"点击前"状态，视频阶段用 `afterEvent`/`frameEvent` 双引用补偿。
- **吞异常但留证据**：frame_error 字段是"永不 raise"与"可诊断"的折中——症状从"帧数莫名变少"变成"events.jsonl 里有具名错误"。
- **auto 录制默认关**：磁盘与隐私都要求 opt-in；BH_RECORD 环境变量保留进程级一票否决权。
- **`recordings()` 的排序键**用 events.jsonl 的 mtime（缺则目录 mtime，recorder.py:145-147）——目录 mtime 会因删帧等无关操作抖动，以"最后写入证据"定新旧更稳。

## ⑥ 新人提示（坑/勘误）

- **改 helpers 公开函数名要同步 ACTIONS**：改名单里有 `ensure_real_tab`/`dispatch_key` 等，新增改屏 helper 忘加就不出帧（ recorder.py:31-36）。
- 显式 `start_recording` 与 auto 录制是两种身份（meta.auto 区分）：auto 会翻卷、会在偏好关闭后被 observe 清掉；显式录制两者都不（recorder.py:194-198, 247-252）。
- `stop_recording` 的"no frames captured"警告会指引看 events.jsonl 的 frame_error——零帧录制九成是截图超时或 CDP 断连，先查这个字段（recorder.py:125-126）。
- 密码框掩码依赖 `_CTX_JS` 拿到的 `input=="password"`；若上下文探针失败该帧没有掩码信息，`_mask` 退化为原文截断——敏感场景验证录制前先确认 events.jsonl 里 box/input 字段在。
- 视频 `showTyping` 揭示原文的通路：events.jsonl 里 type_text 的 text 已被 `_mask`，video.py 靠 `load_revealed_text` 重读**原始 events.jsonl 的 sourceLine** 还原非密码文本（video.py:622-639）——所以删改 events.jsonl 会破坏视频阶段。
- 每个 BU_NAME 一个标记文件：多实例并行录制互不踩踏，但共享同一个 recordings 根目录，帧号撞名重试逻辑（recorder.py:289-296）是为跨目录安全设计的，同目录并发仍然依赖它。
