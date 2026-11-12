# app.js — demo 控制台前端控制器：令牌取用、三段命令驱动与纯观察式渲染

## 一、角色定位

app.js 是 demo 控制台唯一的脚本（index.html:142 以 ES module 引入），244 行无框架、无构建、无依赖。它扮演"agent 的仪表盘"：把 demo.py 暴露的 `/api/{reset,predict,act,tick}` 三段协议（demo.py:118）翻译成单步/自动两种操作节奏，再把返回的 agent 快照渲染成截图、候选动作概率榜、目标覆盖层与执行轨迹。定位上有两条铁线：**前端不碰任何业务逻辑**——决策、新鲜度、预算全在 agent.py，这里只发命令与画状态；**它是纯观察面板**（图谱 hub 原话），页面里的"浏览器"只是 base64 截图，不是真的 iframe。安全模型上它承接服务端的令牌注入：启动第一行就从 `<meta name="demo-token">` 取每进程随机 token（app.js:2，index.html:6 占位符由 demo.py:101 替换），之后每个 POST 都带 `X-Demo-Token` 头（app.js:24）。

## 二、内部结构

**基础层（app.js:1-20）**：`$` 是 getElementById 简写（app.js:1）；模块级 `state/busy/automatic` 三态（app.js:3-5）；`goals` 字典内置三个场景的任务语句（app.js:6-11，flights 语句与 examples/flights.py:12-15 逐字一致）；`escape` 做 HTML 转义（app.js:12-19）——所有动态 innerHTML 拼接前都过它；`percent` 把 0-1 概率转百分比，小于 1% 时保留一位小数（app.js:20）。

**通信层 call（app.js:21-32）**：`fetch("/api/${name}")` POST JSON，失败抛 `data.error`（app.js:28，服务端 400/500 的错误原文直接冒泡）；成功则 `state = data; render()`（app.js:29-30）——每次调用都是"命令→全量重渲染"。

**互斥层 perform（app.js:45-68）**：所有按钮动作的公共外壳。`busy` 旗标防重入（app.js:46-47）；catch 块做三件事——关自动模式、重新拉 `/api/state` 让 UI 与服务端对齐（app.js:56）、显示错误并把状态置"Paused · needs attention"（app.js:61-63）。注意拉状态失败被静默吞掉以保留原始错误（app.js:58-59）。

**渲染层 render（app.js:69-147）**，全文件重心：文本模型名（app.js:71）→ 计划步骤（app.js:72-77，`plan_index` 命中项高亮）→ 状态标签五连（app.js:82-89）→ 截图 `data:image/jpeg;base64`（app.js:96）→ 决策指标区（延迟/目标置信度/操作，app.js:104-106）→ 操作概率 chips 按概率降序（app.js:108-110）→ 候选元素榜（app.js:114-119，有决策时按元素概率排序，app.js:115）→ 目标覆盖层（app.js:120-126）→ 历史轨迹（app.js:127-134）→ "What the model sees" JSON（app.js:136-145）。

**事件绑定（app.js:148-235）**：表单提交→reset（app.js:148-156）；场景切换自动填任务（app.js:157-159）；Choose/Execute 单步（app.js:160-168）；自动循环与暂停（app.js:169-192）；覆盖层开关（app.js:193-195）；榜单与覆盖层双向高亮（app.js:196-216）；trace 下载（app.js:217-235）；启动时拉初态（app.js:236-244）。

## 三、外部连接

上行只连 demo.py 一个进程：GET `/api/state`（app.js:56、236）与 POST `/api/*`（app.js:22-24）。下行消费的数据形状全部由 agent.py 决定——`state.elements` 来自 `action_space(page.actions)[0]`（agent.py:49），`decision` 的 `target_probabilities/operation_probabilities/request` 来自 model.py:140-147。DOM 契约方是 index.html 的 id 集合（约 30 个 `$()` 调用一一对应）；style.css 提供 `.bar` 概率条（宽度吃 `--probability` 变量，app.js:118 注入）与 `.target.selected` 橙色高亮（app.js:124 加 `selected` 类）。浏览器本体与它无关——Chrome 由 browser-harness daemon 独立持有，前端看到的只是 JPEG。

## 四、数据流

一条主循环：用户操作 → perform 包裹 → call POST → 服务端持锁执行（demo.py:111）→ 全量 state 返回 → render 重画。三个关键转换值得记：① **元素概率的取值函数**（app.js:111-112）：下拉元素自身索引（如 "3"）不在 `target_probabilities` 里，键是 "3:1"/"3:2" 这类选项索引（model.py:75），故先用 `e.index` 直查、查不到则取其 options 概率最大值——`?? -1` 使无概率元素显示 "—"；② **目标覆盖层索引对齐**（app.js:120-124）：覆盖层给去重后的 node 顺序编号 `i+1`，与 action_space 的元素编号天然对齐——前提是 scroll/wait 这类合成动作没有 rect（snapshot.js:102-104 确实不带），否则错位；③ **fingerprint 传递**（app.js:165、179）：Execute 把 `state.page.fingerprint` 回传给 act，正是 agent.py:88 的过期决策闸。

自动模式数据流有两条路径（app.js:169-187）：勾选 Slow motion 时走 `predict → 450ms 停顿 → act`（app.js:175-179，人为可视化的节奏）；否则直接 `tick`（app.js:181，服务端原子步）。循环上限 `state.max_steps * 2`（app.js:173）对齐 agent.py:75 的决策预算（questions.py:26 的 MAX_STEPS=60，故 120 次）；状态进 done/blocked 即停（app.js:183）。

## 五、设计决策与取舍

1. **全量重渲染而非增量 DOM**：每次 call 后整体重画，代码量最小；代价是长列表滚动位置丢失——对演示场景可接受。2. **错误后重拉状态**（app.js:56）：agent 抛错时服务端 state 仍可能已前进（如动作已执行），重拉避免 UI 停留在过期画面。3. **done 后仍显示最后一个决策**（app.js:80-81，`decisions.at(-1)` 兜底）：让 DONE 选择本身可被检视，呼应"模型自报不是证明"的审计姿态。4. **trace 下载剥离截图**（app.js:218-222，`screenshot: undefined`）：导出 JSON 去掉 base64 大字段，文件名固定 typesafe-browser-trace.json（app.js:232）。5. **慢放是前端 sleep 而非服务端节流**（app.js:177）：服务端计时不受演示节奏污染，测量口径得以保真。6. **model-state 投影**（app.js:141）：展示请求时剥掉 `rect/node`，对齐模型真实所见（model.py:110-116 的 state 构造）。7. 零依赖 ES module：与全仓"small enough to read"一致，node --check 即可静态校验（AGENTS.md Checks）。

## 六、新人提示

- token 是**随 HTML 下发**的（demo.py:101 对所有静态文件做 `__TOKEN__` 替换）——重启服务后必须刷新页面，否则所有 POST 得 403。
- `probability()` 用 `??` 而非 `||`（app.js:111）：概率 0 是合法值不会被兜底吞掉；`-1` 哨兵表示"无概率"，渲染成 "—" 与 0% 条。
- 覆盖层编号与元素编号对齐是**隐式不变量**：依赖 snapshot.js 里 scroll/wait 无 rect（snapshot.js:102-104）。若未来给合成动作加几何信息，app.js:120-126 的 `i+1` 编号会静默错位。
- `pointerover` 高亮匹配的是字符串相等（app.js:197-205），选中态基准 `decision.target.split(':')[0]` 取的是元素段——SELECT 目标 "3:2" 会高亮 3 号元素的框，属刻意取整。
- 初态拉取失败只显示 "Cannot reach local demo server"（app.js:242-244）——别在浏览器里直接 file:// 打开 index.html，占位 token 未替换且无 API。
- 图谱 hub 称本文件"渲染按模型概率排序的候选动作、目标覆盖层与执行轨迹，支持 trace 下载"——逐条与源码核对一致（app.js:115/120-126/127-134/217-235），无出入。
