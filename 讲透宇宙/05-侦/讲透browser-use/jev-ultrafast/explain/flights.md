# examples/flights.py — 真实 Google Flights 实战：任务常量与独立验证器 verify()

> 本篇选讲 examples/flights.py 而非 docs/design.md：它是测量线（record_flights/measure_flights）共同的任务源与判据源，也是仓训「验证与模型自报解耦」的可执行门面；design.md 的架构论点已分散落在其余 11 篇的「设计决策」节。

## 一、角色定位

examples/flights.py（68 行）在真实网站上跑完整 agent 循环：给定 URL 与一段自然语言目标，苏黎世→伦敦、2026-09-20、单程、经济舱，跑完对最终页面做**独立于模型 DONE 自报**的硬校验。docstring 两句各管一头（flights.py:1）："Live Google Flights search" 定场景，"never selects or book a flight" 定安全边界——只搜不订。它在代码库里是被 import 最多的小文件：`GOALS/URL/verify` 三样被 record_flights.py:14 与 measure_flights.py:22 复用，demo 控制台的默认任务（index.html:40-41、app.js:7）也与 GOALS 逐字相同——**演示、录制、测量三线共用同一任务与同一判据**，口径统一是性能数字可信的前提。README 的表述即此文件的方法论浓缩：「The Flights example supplies a goal and independently verifies the outcome」。

## 二、内部结构

**任务常量（flights.py:11-15）**：URL 带 `hl=en` 锁英语界面（flights.py:11）——verify 的标签匹配全部依赖英文可访问名，语言漂移即校验失效；GOALS 是**带括号的长字符串**而非元组（flights.py:12-15 的 `(` `)` 只是换行包裹），末句「Stop when matching flight options are visible. Do not select or book a flight.」同时定义停止条件与禁令。Agent 构造对 str 与序列都兼容（agent.py:14）。

**verify(page)（flights.py:18-38）**——全仓最重要的 20 行。输入只需 page 的 `url/actions/text` 三字段（快照来自 snapshot.js:105-106），无截图、无视觉。分解：
- **URL 解析**（flights.py:20-21）：取查询参数 `tfs`——Google Flights 把全部搜索状态编码进这个 base64 protobuf 串。
- **年份双路验证**（flights.py:22-25）：urlsafe base64 手工补 `=` 填充（`"=" * (-len(encoded) % 4)`，flights.py:23）后解码，在字节流里找 `b"2026-09-20"`（日期在 tfs 里以字符串字段序列化，子串命中即有效）；解码抛 ValueError 则置 False。
- **动作字典**（flights.py:26-28）：`values` 以 strip 后的标签为键映射当前值（flights.py:27）；`flights` 收所有标签含 "Select flight" 的动作（flights.py:28）——结果卡的标志。
- **七项 checks**（flights.py:29-37）：`search_page` 要求 host+path 精确为 /travel/flights/search（flights.py:30，证明搜索真的执行了而非停留在表单页）；`one_way/origin/destination/date` 四项比对表单回显值——键是 Google 的可访问名原文，出发地期望 **"Zürich" 带变音**（flights.py:32）、日期期望 "Sun, Sep 20"（flights.py:34，**不含年份**，这正是年份要走 URL 的原因）；`year` 双路：tfs 命中或页面文本含 "departing 2026-09-20"（flights.py:35）；`results` 要求至少一张结果卡**且所有** "Select flight" 标签都写着 "Sunday, September 20"（flights.py:36——防止错年份结果混入）。
- **返回**（flights.py:38）：`passed` 为七项全真，附 checks 明细与可见航班标签列表。

**main（flights.py:41-64）**：`--output` 默认 artifacts/flights/latest、`--keep-open` 保留浏览器标签页供人工检查（flights.py:43-44）；建 Agent 后逐 tick 打印 elapsed/status/action（flights.py:48-52）；finally 里 snapshot → **verify(state["page"])**（flights.py:55）→ state.json 与 session.json 落盘（flights.py:56-59，session.json 存 target/session 两个 ID 供事后 attach 调试）→ 非 keep-open 才关浏览器（flights.py:60-61）；末尾打印校验 JSON，**失败 SystemExit 非零**（flights.py:62-64）。

## 三、外部连接

上游：jev_ultrafast.Agent（flights.py:9）——三段协议循环、决策、执行全在库内，本文件不含任何编排逻辑。下游两个 script 消费者（record_flights.py:14、measure_flights.py:22）与一个演示端（demo.py 的 flights 场景用同一 URL，demo.py:55；app.js:7 用同一目标语句）。被 tests 隔离于 pytest 之外（AGENTS.md「Tests must not call paid APIs」——它真调 TypeSafe）。产物 state.json 喂给 docs/flights-measurement.json 一类报告材料。

## 四、数据流

单线直通：URL+GOALS → Agent（建 Browser、首观察）→ run 循环（predict/act 交替，agent.py:163-165）→ DONE 后 snapshot → verify 读取最终 page 的三字段 → checks 字典。注意 page 从哪来：main 验证的是 `state["page"]`（flights.py:55）——**run 内最后一次观察的页面**，即模型决定 DONE 时所见的同一帧；两个 scripts 则在 run 后重新 observe 再验（measure_flights.py:56、record_flights.py:66）。三处产出同构 state.json（verification 字段），但验证输入新鲜度不同，比较时须留意。

## 五、设计决策与取舍

1. **验证器只信页面不信模型**（flights.py:19 docstring 原话 "not the model's DONE answer"）：DONE 只是又一次选择，成功与否由独立检查判定——AGENTS.md 第 8 条不变量的落地。2. **七项全过才算过**（flights.py:38 的 all()）：单边检查（如只看 URL）会被"搜索了但日期错"骗过；checks 明细同时落盘，失败可定位到具体维度。3. **年份独立成项**：日期字段 UI 不显示年份，故从 tfs 字节流取证——对 Google 序列化格式的子串级依赖是脆弱点，双路兜底（页面文本）降低单点失效风险。4. **results 检查取"全称"语义**（flights.py:36 的 all()）：任何一张结果卡日期不符即失败，宁严勿松。5. **安全靠目标语句约束而非机械封锁**：禁令写在 GOALS 里（flights.py:15），执行器没有"不许点 Select flight"的硬闸——诚实取舍：通用策略不引入站点专属规则（AGENTS.md 第 1 条）。6. **session.json 落盘**：跑挂时可用 target/session 两 ID 复查现场。7. **退出码即门禁**（flights.py:63-64）：外层脚本/CI 可直接以退出码判成败。

## 六、新人提示

- **图谱勘误**：图谱 hub 两处称 verify() 做「八项硬校验」，实际 checks 字典是**七项**（flights.py:30-36：search_page/one_way/origin/destination/date/year/results）——hub 自己列举的名字也只有七个，"八项"系计数错误。
- 标签键是**精确匹配**且依赖 Google 现行可访问名：实测数据里 "Where to? " 带尾随空格（docs/flights-measurement.json 的 text_calls 字段可见）——flights.py:27 的 strip 只作用于页面侧标签，校验键（flights.py:31-34）若照抄含尾空格的 a11y 名就会静默失配。Google 改 UI 文案即断，属已知的活体依赖。
- GOALS 是字符串不是元组（flights.py:12-15）——别按序列语义去迭代它。
- "Zürich" 必须带变音（flights.py:32）：Google 选中建议后回显的是 Zürich 而非 Zurich，打字稿里少个 umlaut 的对照实验请绕开这条。
- 本脚本花钱且不可进 pytest；`--keep-open` 留着标签页时会跳过 agent.close（flights.py:60-61），长跑脚本记得手动清理。
- verify 不读截图字段：给它 `observe(screenshot=False)` 的产物即可（record_flights.py:66 正是这么做的），省 base64 体积。
