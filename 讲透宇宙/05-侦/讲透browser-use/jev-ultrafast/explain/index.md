# index.html — 控制台骨架：令牌占位、任务表单与 workspace 双栏的 DOM 契约

> 本篇选讲 index.html 而非 style.css：144 行骨架承载了安全模型（token 注入位）、三场景入口与 app.js 的全部 DOM 契约，信息密度高于纯视觉的 style.css（737 行，其要点已并入 app.md）。

## 一、角色定位

index.html 是 demo 控制台的结构层：静态白名单四文件之一（demo.py:93），由 do_GET 读盘并做 `__TOKEN__` 替换后原样下发（demo.py:101）。它定义了三样东西：**安全模型的客户端锚点**——`<meta name="demo-token" content="__TOKEN__">`（index.html:6）是 token 进入前端的唯一通道；**任务入口**——场景下拉 + 目标 textarea + Start 按钮的表单（index.html:30-46）；**展示骨架**——workspace 双栏（浏览器面板 + 决策侧栏）、决策轨迹区、"What the model sees" 折叠面板，共约 30 个 id 节点，全部由 app.js 按 id 精确驱动。它是纯静态骨架：无内联脚本、无内联事件，唯一脚本引用是尾部 `<script type="module" src="/app.js">`（index.html:142）。

## 二、内部结构

**head（index.html:3-10）**：demo-token meta（index.html:6）；标题「Jev Ultrafast · Browser Use」（index.html:7）；两个样式表——rsms.me 的 Inter 字体 CSS（index.html:8，**全页唯一外部资源**，离线时控制台仍可用只是字体回退）与本地 `/style.css`（index.html:9）。

**header 与 intro（index.html:12-29）**：品牌条 browser<span>use</span> × TypeSafe（index.html:13-14，span 由 style.css:37-39 染橙）；「Jev Ultrafast」local 徽标（index.html:16）。intro 区一句话主张「Every page is a set of possibilities.」（index.html:22），并挂出 `/demo.mp4` 真实 Flights 演示视频链接（index.html:25，由 demo.py:88-91 回放 docs/demo.mp4——render_demo.py:118 的产物）与「jev-latest + text helper」模型标签（index.html:28）。

**任务表单（index.html:30-46）**：`#task-form` 含场景 `#scenario` 三选项（index.html:33-37）——flights 走真实 Google Flights、travel/research 走本地 fixture（映射在 demo.py:54-57）；`#goal` textarea 预填的默认任务（index.html:40-41）与 app.js:7 的 goals.flights 及 examples/flights.py:12-15 三处逐字一致；提交按钮 `#start`（index.html:42-44）。

**工具栏（index.html:47-61）**：状态点 + `#status` 文本（index.html:48-51，app.js:82-89 的五标签写入处）；`#pace` 慢放开关（index.html:52，消费在 app.js:175-179）；`#overlays` 目标覆盖层开关默认勾选（index.html:53-55）；四个动作按钮 `#choose/#execute/#auto/#stop`（index.html:56-59）——stop 初始 `hidden`，与 auto 互斥切换（app.js:41-42）。

**workspace 双栏（index.html:63-122）**：左栏浏览器面板——伪地址栏（红绿灯装饰 index.html:66、`#url`、LIVE 标）、`#viewport` 视口内含空态 `#empty`（index.html:71-78）、`#screenshot` img（index.html:79-83，初始 hidden）与覆盖层容器 `#targets`（index.html:84）、底栏 `#page-title` 与流程标签（index.html:86-89）。右栏 aside——NEXT ACTION 头部与 `#choice-title`/`#action-count`（index.html:92-98）、计划容器 `#plan`（index.html:99）、三格指标 `#latency/#confidence/#completion`（index.html:100-109）、操作概率 chips 容器 `#operation-choices`（index.html:110）、元素榜标签与 `#choices`（index.html:111-117）、以及关键旁注「Operation and target are separate choices in one request. Text is generated only for TYPE_TEXT.」（index.html:118-120——把 model.py 的双决策单请求架构写进了 UI 文案）。

**轨迹与调试（index.html:123-140）**：`#history` 决策轨迹 + `#download` 导出按钮（index.html:123-131）；`<details>` 折叠的 `#model-state` pre（index.html:132-136，app.js:136-145 填充请求 JSON）；footer 的 `#helper` 显示文本模型名（index.html:139，app.js:71 写入）。

## 三、外部连接

对 demo.py：静态路由 `/`（demo.py:93）serve 本文件；`__TOKEN__` 替换发生在所有静态文件上（demo.py:101），但只有本文件的 meta 消费它（app.js:2）。对 app.js：约 30 个 id 是双方共同契约，缺一个 app.js 即 TypeError（`$()` 返回 null）。对 style.css：类名体系（.workspace/.target/.choice/.trace-row 等）在此声明。对 /demo.mp4：intro 链接 target=_blank 新开（index.html:25），demo.py:88-91 直接回字节流。字体 rsms.me 是唯一出网请求，与 fixture.html 的纯离线形成对照。

## 四、数据流

页面加载：GET / → token 注入 → app.js module 执行 → 读 meta token（app.js:2）→ GET /api/state 初态（app.js:236-244）→ render() 按 id 填充。此后单向流：用户事件 → app.js 命令 → 服务端 state → render 改写各节点。骨架本身无状态，所有动态性都在 id 节点的 textContent/innerHTML/disabled/hidden 四个属性上流转；空态设计（#empty 显示、#screenshot 隐藏）在首次 render 有 page 后翻转（app.js:94-95）。

## 五、设计决策与取舍

1. **token 走 meta 而非 cookie**：免 CSRF 复杂度，且 POST 校验三件套（Host/X-Demo-Token/Origin，demo.py:105-110）里 token 由 JS 显式带头，读代码即可见安全模型全貌。2. **默认任务与示例/前端三处同步**（index.html:40-41 = app.js:7 = examples/flights.py:13-14）：演示所见即测量所测，口径统一。3. **慢放/覆盖层做成 checkbox 而非按钮**：两者是持续态不是动作，语义正确且免 busy 管理。4. **「What the model sees」用 details 折叠**：默认收起大 JSON，审计时可展开——透明性与降噪兼顾。5. **旁注文案写架构**（index.html:118-120）：UI 自解释双决策单请求与 TYPE_TEXT 才调小模型，降低演示讲解成本。6. **静态骨架 + module 脚本分离**：HTML 可被 demo.py:101 的字符串替换安全处理，不会误伤脚本。

## 六、新人提示

- **页脚流程标签是一处过时表述**：`AX tree → typed actions → CDP`（index.html:88）——现行实现并不读 CDP accessibility tree；snapshot.js 直接遍历 DOM 提取 HTML/ARIA 语义，一次调用成快照（browser.py:1、design.md「one browser-side DOM snapshot」）。反复读 AX tree 是被替换的旧原型（performance.md「Where the time went」）。看到这行别去 DOM.getFlattenedDocument 系 API 里找实现。
- `#action-count` 初始文案「0 options」（index.html:97），但 app.js:99 写入的是「N elements」——两处措辞不一致，属文案遗留非 bug。
- 外链字体（index.html:8）在离线环境加载失败会有样式回退，控制台功能不受影响；但 serve 它需要 demo.py 可达，直接 file:// 打开必然残缺（token 未替换）。
- `#stop` 用 `hidden` 而非 `disabled`（index.html:59）：未运行时彻底不占位，避免工具栏出现永久灰按钮——改 UI 时别换成 disabled 破坏布局切换（app.js:41-42 依赖 hidden 语义）。
- demo.mp4 链接依赖 docs/demo.mp4 存在（demo.py:90），缺失时该路径 404——那是 render_demo.py 的产物，不在 git LFS 之外另行分发。
- 图谱 tour 第 7 步称本文件「任务表单与 workspace 双栏的操作台骨架，serve 时注入会话令牌」——与源码一致，无出入。
