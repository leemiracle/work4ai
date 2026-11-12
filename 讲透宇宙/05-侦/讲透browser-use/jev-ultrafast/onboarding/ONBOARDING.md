# Jev Ultrafast 新人上手文档（ONBOARDING）

> 图谱基线：78 节点/179 边/13 层/15 步 tour@1231850a；锚点经源码核实。本仓文件名全局唯一，锚点用 basename（agent.py 即 jev_ultrafast/agent.py）。

## 1. 项目一句话定位

Jev Ultrafast 是 Browser Use × TypeSafe 的极简类型安全浏览器 agent 脚手架：一句目标下，TypeSafe 的 Jev 模型只在"观察到的动作"里做选择，小 LLM 仅在 TYPE_TEXT 时写字段文本，执行权归代码——`__init__.py:1` docstring 钉版："Jev chooses an observed action. Code owns execution."。公共 API 只有 Agent 与 Browser（`__init__.py:6`）。

生态关系：运行时依赖仅 browser-harness==0.1.13 与 httpx[http2]（`pyproject.toml:8`）；browser-harness 是 pip 依赖而非子模块，`browser.py:9-10` 只导入其 ensure_daemon 与 cdp。与 browser-use 主框架是主张对照：主框架走通用 LLM 工具调用，本仓用动态索引动作空间把"选操作+选目标"压成一次网络往返（README 主打 Flights 7.1 秒实录）。

## 2. 总体架构（13 层归并五带）

- 入口带（L01）：pyproject、.env.example 双凭据模板（六变量）、`__init__.py` barrel。
- 策略决策带（L02-L03）：`questions.py` 三段提示词与 MAX_STEPS=60（`questions.py:26`）；`model.py` 模型访问层；`agent.py` 三段式循环。
- 执行带（L04）：`browser.py` 单一 CDP 会话封装 + `snapshot.js` 原子 DOM 快照 IIFE。
- 演示示例带（L05-L06）：`demo.py` 回环服务器 + static 三件 + fixture.html 零外网夹具；examples 两入口（run.py 万能模板、flights.py 实战+验证）。
- 证据带（L07-L13）：scripts 五脚本（冒烟/守卫/测量/录制/渲染）、docs 四份测量 JSON 与三份报告、`test_agent.py` 离线契约套件（20 测试）。

高扇入枢纽：browser.py（fanIn 13）与 `__init__.py`（fanIn 9，外部唯一入口）。

## 3. 核心链路

三段式协议：`Agent.command()` 接受 tick/predict/act（`agent.py:52`）。tick 为 predict+act 组合（`agent.py:57-58`）；predict 先 fresh 校验、陈旧即重观察（`agent.py:70-71`）；act 在任何变更或模型调用前一次性消费决策（`agent.py:90-91`，注释 "Consume once...A retry cannot double-click"）。

单请求双决策：`choose()`（`model.py:81-148`）构造 questions——operation 主问题（含 DONE/BLOCKED 语义，`model.py:90`）加各操作独立 target 头（`model.py:95`），附 url/title/text、元素表与近 10 条史（`model.py:113`），一次 POST 到 systemone 接口（`model.py:119`），只校验被选中操作的 target 头（`model.py:126-127`）。

动作空间折叠：`action_space()`（`model.py:48-78`）让同一 DOM 节点只分一个递增索引，click/fill/select 各持独立候选字典（select 目标形如 "3:2"，`model.py:75`），其余归 controls。

预算与熔断：模型调用上限 120（`agent.py:75-76`）、动作上限 60 触顶即 blocked（`agent.py:102-104`）、连续三条无进展熔断（`agent.py:153-158`）。TYPE_TEXT：fill 前 fresh 并组 field_context（goal+字段+6000 字符正文+近 6 条史，`model.py:151-157`），文本仅完整输入一致时复用（`agent.py:110-111,118`）。

## 4. 关键模块深读

agent.py（174 行）：state 为普通 dict（`agent.py:27-41`）；StalePage 在 tick 层捕获后回滚 ready 并重观察（`agent.py:59-64`）；执行记录先于观察写入 history（`agent.py:120-121`）。

browser.py（194 行）+ 内嵌 snapshot.js：READ_STATE 模块加载期读入 snapshot.js 全文（`browser.py:13`）；构造即后台标签页+1120x780 视口+焦点仿真（`browser.py:25-27`）。observe 带 10 次重试（`browser.py:77-85`），fill 后等 combobox 可见 option（`browser.py:51-74`）；fresh() 对 click/select 走 pageKey+guard 双级校验、其余走 marker 比对（`browser.py:88-98`）。执行前 JS 六重校验（连接/禁用/可见/只读/几何/遮挡，`browser.py:144-160`），节点 ID 为代码观测的真实节点、非模型生成选择器（`browser.py:141-143`）；fill 用 selectAll+insertText 替换（`browser.py:175-185`）；select 中断抛 RuntimeError 禁按 stale 重试（`browser.py:130-131`）。

snapshot.js（107 行）：单个 IIFE；`window.__jevFast` 缓存 WeakMap（元素→id）与 Map（id→活引用），断连节点即时剪枝（`snapshot.js:3-8`）；guard 取最近 form/dialog/article/li/tr 作用域 6000 字符上下文，作用域外变化不失效（`snapshot.js:47-54`）；select 按未选项逐一展开（`snapshot.js:68-71`）；可编辑元素同时产生 fill 与 "Open xxx" click（`snapshot.js:79`）；动作表超 250 截断、截断项不可选（`snapshot.js:99-100`）；末尾追加 scroll 与 wait（`snapshot.js:102-104`）。

demo 控制台 static 三件：demo.py 只绑 127.0.0.1:8766（`demo.py:16`），POST 三重校验（Host/X-Demo-Token/Origin，`demo.py:104-110`）加非阻塞锁（409）与 8KB 体上限（`demo.py:111-115`），serve 时替换 `__TOKEN__`（`demo.py:101`）；app.js 为纯观察面板（`app.js:2,21-22`）；fixture.html 为 507 行零外网旅行站，四视图函数（`fixture.html:391-487`）。

## 5. 数据流与制品

flights 链：`flights.py` 循环后对最终页面（非模型 DONE 自报）执行 verify() 八项校验（`flights.py:18-38`）：URL 路径、单向、出发/目的地/日期、年份（tfs 参数 base64 双路验证，`flights.py:23,35`）、可见航班；state.json 与 session.json 落盘 artifacts（`flights.py:56-59`）。

测量链：`measure_flights.py` 把 cdp monkey-patch 成计时包装（`measure_flights.py:30-41`），逐 CDP 方法统计调用数/毫秒，连同源码 sha256（`measure_flights.py:26-29`）与 task_hash 写入 state.json（`measure_flights.py:60-66`）；计时不含建置与最终校验（`measure_flights.py:44,55-57`）。录制链：`record_flights.py` 开 CDP screencast 按相对首次预测的毫秒时间戳落帧，render 脚本按原始时间戳合成 1x 视频，全程不加速。

source_hashes 锚定机制：docs 四份 JSON 均带被测源码 sha256 指纹，性能声明可回溯到确切源码版本（full-speed-measurement.json 另记 baseline_commit=68c077bf）。关键数字：flights-measurement.json 记 7073ms、17 次决策（中位 178ms）、11 动作；full-speed-measurement.json 三对交替运行中位 9450→7092ms、请求 22→17、CDP 调用 1092→101；measurement.json 本地基线中位 1242ms；`performance.md:18` 如实标注符号检验 p=0.25 统计力不足。

## 6. 设计决策与取舍

- NEXT_ACTION 结构（`questions.py:3-14`）：页面文本不可信、自动补全填完必选、日期三击、过滤器设了才算数、可见证据才 DONE 等固化为通用策略；`AGENTS.md:5` 明令禁止站点特定计划与硬编码字段值。TARGET 头（`questions.py:16-19`）声明"本题只选该操作的目标、另一问题决定操作"，补偿 target 读不到 operation 答案的并行问法。
- MAX_STEPS=60 预算：动作 60/决策 120 双上限（`agent.py:75,102`）界定最坏成本；smoke.py 的 --max-actions 默认 15 是更紧活体闸（`smoke.py:19`）。
- 验证与模型解耦：DONE 不是成功证明（`AGENTS.md:12`），verify() 被三脚本复用为统一判据。
- 为何内嵌 JS：snapshot.js 与 browser.py 的 MARKER/guard 表达式（`browser.py:14,94-95`）共享 `__jevFast` 协议；单文件分发免去 npm 依赖与打包，代价是无直接测试覆盖，靠 check_guards.py 间接回归。
- 概率校验：validate_choice 要求概率键与 id 集完全一致、和为 1±0.02、被选项达最大值-1e-6（`model.py:30-45`），坏输出一律拒绝。

## 7. 上手路径（按 tour 15 步首日路线）

1. README + pyproject.toml；2. design.md + AGENTS.md（架构宪法与 10 条铁律，改核心文件前必读）；3. `__init__.py` + run.py；4. model.py + .env.example；5. questions.py + agent.py；6. browser.py + snapshot.js；7. demo.py + index.html；8. app.js + style.css；9. fixture.html + smoke.py；10. flights.py + measure_flights.py；11. record_flights.py + 两 render 脚本；12. measurement.json + flights-measurement.json；13. full-speed-measurement.json + performance.md；14. performance-prepared.md + launch-draft.md；15. test_agent.py + check_guards.py。

实操：uv sync + cp .env.example .env 填 key，uv run jev 开 127.0.0.1:8766 点 Start demo → Run automatically；改码后跑 `AGENTS.md:16` 四检查（ruff/pytest/node --check/uv build）。

## 8. 常见坑与勘误

源码级陷阱：

- select 执行中断是 RuntimeError 不是 StalePage——重试会双发 change 事件（`browser.py:130-131`）。
- 文本缓存只在完整 field_context 一致时复用；上下文一变就重新调付费 API（`agent.py:110-114`）。
- fingerprint 刻意排除 screenshot（`browser.py:115-117`）：只跟踪语义值与节点身份。
- field_text 缺 TEXT_MODEL_API_KEY 直接抛错、绝不猜值（`model.py:161-163`）；默认 base DeepSeek 自动关 thinking，OpenRouter 走 reasoning low/none（`model.py:164-168`）。
- demo token 每次启动随机生成并注入静态页；缓存旧页面会 403。
- tests 严禁调付费 API（`AGENTS.md:11`），活体验证走 smoke.py（不被 pytest 收集）。

图谱过程发现与勘误：

1. tree-sitter 对 IIFE 内函数零提取：snapshot.js 全文件零 function 声明（grep 计 0），identity/pageKey/guard 等全是 IIFE 内 const 箭头函数（`snapshot.js:4-54`），图谱只能以文件级节点呈现。
2. fixture.html 内嵌脚本同理（`fixture.html:391-487`）；app.js 的 async function 也部分超出 scanner 提取面。
3. `style.css:737` 尾部有一段压缩格式的 .operation-choices 后补样式，与正文排版迥异，系追加写入而非生成错误。
4. 图谱称 .env.example 六变量全在 model.py 消费——核实为真（`model.py:108,119,161-167`）；demo.py 另读 TYPESAFE_DEMO_PORT/TEXT_MODEL（`demo.py:16,34`），不在该清单，无矛盾。
5. 图谱各节点 lineRange 与源码逐一核对全部命中，无需修正。
