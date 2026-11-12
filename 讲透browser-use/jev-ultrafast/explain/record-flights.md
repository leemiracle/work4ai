# record_flights.py — 带连续 screencast 的实录运行：时间轴锚定与证据链生产

## 一、角色定位

scripts/record_flights.py（75 行）做一件事：在真实 Google Flights 上跑一次**被测量的**完整 agent 运行，同时用 CDP screencast 连续录屏，最后把「视频帧 + 机器可读 state.json + 源码指纹」打包成一个不可变的证据目录。docstring 一句话定调（record_flights.py:1）："A measured live run with continuous CDP screencast; original timestamps retained"——**原始时间戳保留**是它的灵魂：render_demo.py 之后按 1× 原速合成视频（AGENTS.md 明令「Keep demonstration footage at its original speed」），docs/demo.mp4 里 Google 加载的每一毫秒等待都来自真实时钟，不做加速。它与 measure_flights.py 是测量线的两支：后者只计时（CDP 调用统计），本脚本计时+录屏+落帧，产出 docs/flights-measurement.json 与演示视频的原料。

## 二、内部结构

**目录与指纹（record_flights.py:17-23）**：输出目录取 argv[1]，默认 artifacts/flights/recorded（record_flights.py:17），`mkdir(exist_ok=False)`（record_flights.py:18）——**同一目录绝不复用**，每次实录都是新证据件，防止半途覆盖旧证据。启动即对 jev_ultrafast 包内全部 .py/.js 做 sha256（record_flights.py:19-23），随 state.json 落盘——任何"这段视频是哪个版本代码跑的"的质疑可回查。

**首帧与线程准备（record_flights.py:24-33）**：`Agent(URL, GOALS)` 建立浏览器（URL/GOALS/verify 复用 examples/flights.py，record_flights.py:14）；手动调 `Page.captureScreenshot` 存 `frames/000000.jpg`（record_flights.py:26-28）作为 t=0 帧；建 `screencast/` 目录、`threading.Event` 停止旗、`epoch` 时间原点与 `errors` 收集表（record_flights.py:29-33）。

**capture 工作线程（record_flights.py:36-48）**：daemon 线程轮询 `drain_events()`（browser_harness.helpers:80，从 harness daemon 的事件缓冲拉取 CDP 通知）；三道过滤与转换——只收 `Page.screencastFrame` 且 `session_id` 等于本 agent 会话（record_flights.py:40，其他标签页的帧丢弃）；时间戳换算 `(metadata.timestamp - epoch)*1000` 取整并 `max(0, …)` 钳负（record_flights.py:43——worker 启动到 run 开始之间的帧会得到负值，钳成 0）；按 `{毫秒:06d}.jpg` 落盘后**必须回 ack**（record_flights.py:45，`Page.screencastFrameAck` 不回 Chrome 几帧后就停发）。轮询节奏 `stop.wait(0.015)`（record_flights.py:46）；线程内异常不炸主流程，进 `errors` 表随 state 持久化（record_flights.py:47-48）。

**开录与时间锚（record_flights.py:51-55）**：`Page.startScreencast` 参数 jpeg/quality 80/maxWidth 1120/maxHeight 780/everyNthFrame 2（record_flights.py:51）——宽高与 browser.py:25 的视口 override 完全一致（帧不缩放），隔帧采样≈30fps 上限的一半；worker 起跑后、`agent.run()` 之前**重设 epoch**（record_flights.py:55），注释点明用意（record_flights.py:54）：视频时间轴锚定到首次预测——这正是 agent 计时器的同一起点（agent.py:69，首次 predict 才启动 `started_at`）。

**运行与收尾（record_flights.py:57-75）**：`for state in agent.run()` 每步打印 elapsed/status/action（record_flights.py:57-59）；finally 里顺序讲究——`sleep(0.08)` 等最后一帧到达，注释明说**在 agent 计时之外**（record_flights.py:61）；停线程、join 3 秒、`Page.stopScreencast`（record_flights.py:62-64）；`agent.snapshot()` 后再做一次**全新观察** `observe(screenshot=False)` 作 final_page（record_flights.py:66，verify 不需要截图），跑独立校验 `verify(final_page)`（record_flights.py:67）——不复用 run 里最后一帧，规避"验证页=决策页"的循环论证；补 source_hashes 与 recording_errors（record_flights.py:68-69）；state.json 与 session.json 落盘（record_flights.py:70-71）。最后两道闸：打印校验与帧数（record_flights.py:72-73），**校验不过 SystemExit 非零退出**（record_flights.py:74-75）——失败的实录无法被误当成功证据。

## 三、外部连接

依赖两端：examples/flights.py 供 URL/GOALS/verify（record_flights.py:14）——任务与判据与测量线共用同一份；browser_harness.helpers 供 drain_events（record_flights.py:11）——CDP 事件经 daemon 缓冲，本脚本与 browser.py 共用同一条 IPC 通道但互不干扰（browser.py 只发请求收响应）。下游是 render_demo.py：它要求目录里 `state.json` 的 `verification.passed` 为真且 `recording_errors` 为空（render_demo.py:17），拼 `frames/000000.jpg` + `screencast/*.jpg` 按原始时间戳取帧（render_demo.py:18-19、43-45），逐帧裁掉顶部 64px 账号条（render_demo.py:59）合成 docs/demo.mp4 与 flights-result.png（render_demo.py:99、118）。README 首屏视频、index.html:25 的 /demo.mp4 链接最终都回溯到本脚本的产物。

## 四、数据流

三条并行流在 run 期间交汇：① 命令流（主线程）——agent.run 每步 predict/act 经 browser.py 发 CDP 请求；② 事件流（capture 线程）——daemon 缓冲的 screencastFrame 被轮询拉走，按事件自带 metadata.timestamp 换算成相对首预测的毫秒名落盘，Chrome 收到 ack 继续推帧；③ 观察流——每次 act 后 observe 产生新页面状态与 fingerprint。收尾时三流汇入 state.json：elapsed_ms（agent 计时）、history（动作轨迹）、screencast/ 帧名即时间轴、final_page+verification（独立复核）。时间基准的一致性靠 epoch≈started_at 保证，视频里第 N 毫秒的画面与 state.json 里第 N 毫秒的动作可互相印证。

## 五、设计决策与取舍

1. **screencast 而非逐观察截图**：观察截图每步一张（agent.py:149-152，record 模式已有），粒度绑在动作上；screencast 是连续帧，Google 的加载等待、动画、弹层时序全被捕捉——「loading waits included」的公开口径有帧为证。代价是额外线程与 ack 协议的复杂度。2. **时间锚定首预测而非脚本启动**（record_flights.py:54-55）：与 agent 的 elapsed_ms 同源同点，视频时间码即任务时间码，渲染端零换算。3. **everyNthFrame=2 的半采样**： halves 帧量又不至于丢快速弹层（calendar 翻页约百毫秒级）；q80 JPEG 权衡体积。4. **独立 final 观察**（record_flights.py:66）：验证读的是 run 结束后的页面实况，而非模型决策所依据的那帧——与「DONE 不是证明」的仓训一致。5. **errors 表持久化**（record_flights.py:69）+ 渲染端断言（render_demo.py:17）：录屏中途的网络抖动不会静默产出缺口视频。6. **目录 exist_ok=False**：证据不可变原则的工程化，配合 source_hashes 让每个目录自洽可溯。7. **15ms 轮询而非事件回调**：drain_events 是拉式 IPC，轮询间隔即延迟下限，15ms 对 30fps 帧间隔（33ms）够用。

## 六、新人提示

- 本脚本**真花钱**（TypeSafe + 文本模型），不在 pytest 里，须手跑。
- `time.sleep(0.08)`（record_flights.py:61）不是随手魔法数：screencast 帧是异步推送，run 一停就停录会丢最后 1-2 帧；注释明言这段时间**不计入** agent 的 elapsed_ms，别误以为视频尾帧超时。
- 帧文件名重复即覆盖：`{timestamp:06d}.jpg` 若两帧同毫秒，后写者胜（record_flights.py:44）——实际影响极小（33ms 间隔），但统计帧数时 `len(glob)` 可能略少于实际收到数。
- verify 的输入是 `final_page`（record_flights.py:66-67），不是 snapshot 里的 page——与 examples/flights.py:55 的做法（直接验证 state["page"]）不同，scripts 一侧的验证更严格（run 后新观察）。两处口径差异在对比 state.json 时要心里有数。
- `drain_events` 拉的是**全局**事件缓冲：若同机有别的 CDP 会话在发事件，session 过滤（record_flights.py:40）是唯一防线——并发跑两个录制会互相稀释缓冲，帧可能迟到。
- 图谱 tour 第 11 步称本脚本「按相对首次预测的毫秒时间戳落盘对齐时间轴的帧」——与 record_flights.py:43、54-55 逐条相符，无出入。
