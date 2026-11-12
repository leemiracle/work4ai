# fixture.html — 零依赖内嵌旅行站「Forma」：四个视图的本地演练靶页

## 一、角色定位

fixture.html 是 507 行的单文件测试夹具：CSS、JS、数据、"图片"全部内嵌，零外部请求、零框架。它在系统里身兼三职：① demo 场景 travel/research 的靶页——demo.py:57 在 reset 时让 agent 导航到 `{ORIGIN}/fixture.html?scenario=...`，Chrome 会回头请求本服务器；② smoke.py 的验收对象（smoke.py:26 直接指向 `?scenario=travel`，断言 Casa Flora 详情页）；③ 离线演练场——agent 的观察/守卫/执行全链路（snapshot.js 提取、browser.py 的新鲜度与点击前几何校验）都可在无外网条件下复现。页面标题「Forma · Find a place to slow down」（fixture.html:6）与品牌调性刻意做成真实商业站的样子，让元素标签（"Find stays"、"Free cancellation"）具有野外页面的语义复杂度，而非 test-id 式的玩具标签。

## 二、内部结构

**内嵌样式（fixture.html:7-343）**：定义 header/搜索栏/筛选行/三列房源网格/详情页/文章列表全套样式。最有意思的是**纯 CSS 风景插画**：`.photo` 容器配 `:before` 伪元素画墙体（fixture.html:161-170，box-shadow 拼出立柱）、`:after` 画拱门（fixture.html:171-184，多重 box-shadow 复制出四个拱）、`.tree` 与 `.sun` 两个 span 补树和太阳（fixture.html:185-204），`nth-child` 变体换三张卡的底色（fixture.html:205-216）——无任何图片资源却呈现"有照片"的版式，且渲染确定性极强（截图对比不随网络抖动）。

**状态与数据（fixture.html:356-387）**：`root` 指 `#content`（fixture.html:354-356）；四个视图级变量 `query/category/free/searched`（fixture.html:357-360）构成页面的全部持久状态；数据是三套硬编码——房源 `places` 三条（Casa Flora 里斯本 Design 免取消 145 欧，fixture.html:362-370；The Glasshouse 哥本哈根 fixture.html:371-378；Serra Lodge 里斯本 Nature 不可退 fixture.html:379-386）与文章 `articles` 三篇（fixture.html:449-471）。

**四个视图函数**：
- `travel()`（fixture.html:391-412）：列表页。整页 innerHTML 模板一次性写入（fixture.html:393）——搜索表单（search input + Find stays 按钮）、Category 下拉（all/Design/Nature/Coastal）、Free cancellation 复选框、结果容器与 footer；随后回填状态（fixture.html:394-396）并绑三个事件：提交设 `query` 并标 `searched`（fixture.html:397-402），下拉与复选框变更即时重算（fixture.html:403-410）。
- `results()`（fixture.html:413-439）：过滤纯函数式重算——三个条件与运算：未搜索或城市名包含查询词、类别匹配、免取消开关（fixture.html:414-420）；计数文案（fixture.html:421-422）；命中渲染卡片（`View stay ↗` 按钮携带 `data-place`，fixture.html:428），空结果显示 dashed 提示框（fixture.html:431）；卡片按钮 onclick 绑到 `detail()`（fixture.html:432-438）。
- `detail(p)`（fixture.html:440-448）：详情页。设 `location.hash` 为房名 slug（fixture.html:441）、改标题（fixture.html:442）、写模板——含 `.fixture-note` 一行**回显当前三个筛选状态**（fixture.html:443，调试友好），返回按钮清 hash 回列表（fixture.html:444-447）。
- `research()`/`article(id)`（fixture.html:472-492）：阅读室列表与文章页。`article()` 按 id 切换正文，唯 choices 一篇有三段加料内容，讲"有限选择控制浏览器 agent"的原理（fixture.html:490）——demo 里 research 场景的任务"打开讲 finite choices 的文章"（app.js:9-10）就落在它身上。

**入口分发（fixture.html:493-504）**：header 三个链接绑定（fixture.html:493-501）后，读 `?scenario=` 查询参数：research 走阅读室，其余（含 travel 与缺省）走列表（fixture.html:502-504）——这正是 demo.py:57 构造 URL 的消费端。

## 三、外部连接

唯一的服务方是 demo.py：静态路由 `/fixture.html` 白名单命中（demo.py:96），token 替换对它同样执行但页面并不消费。上游消费者三个：demo 的 agent 导航（demo.py:57）、smoke.py:23 的完整循环、以及用户浏览器（演示时用户可在另一个标签页直接打开它对照。app.js 不加载它）。交互元素类型刻意覆盖 agent 的三类操作：search input 供 TYPE_TEXT、Category select 供 SELECT、复选框与按钮供 CLICK——与 action_space 的三操作枚举（model.py:51）一一对应，是天然的"操作空间全覆盖"教具。

## 四、数据流

页面内：视图函数 → root.innerHTML 全量替换 → 事件回调改状态变量 → 重渲染。跨系统：demo reset 请求携带 scenario（app.js:153）→ demo.py:57 拼 URL → agent 的 Browser 导航（browser.py:28）→ snapshot.js 在该页面上提取元素/动作/rect（snapshot.js:105-106）→ 模型选择 → browser.py 的 act 在真实 DOM 上执行（browser.py:144-160，点击前做 checkVisibility/elementFromPoint 命中校验）→ 页面事件回调（如 fixture.html:397-410）改变渲染 → 下一次 observe 看到新状态。筛选状态对 agent 的反馈通道是计数文案与卡片集合的变化——smoke.py 正是断言这些文本。

## 五、设计决策与取舍

1. **单文件零依赖**：与 fixture 场景"无外网可复现"的目标直接对齐；对照 index.html 还需 rsms.me 字体（index.html:8），fixture 是纯离线。2. **innerHTML 全量重绘**：每次视图切换/筛选变更都重写容器，无 diff——代码最短，代价是输入焦点丢失，但 agent 用 CDP 事件而非真实焦点，无影响。3. **hash 只做面包屑不做路由**：detail 设 hash（fixture.html:441）却无 popstate/hashchange 监听——刷新会回到初始分发视图，浏览器后退键不切换视图；这避免了维护路由状态，也给 agent 的观察一致性让路（hash 变化不触发重渲染，页面语义状态只由三个变量决定）。4. **CSS 插画代替图片**：免网络、免资源加载抖动、截图逐像素稳定，还让 .photo 区域不可交互（不产生动作候选）。5. **三房源数据的过滤张力设计**：Free cancellation + Design + Lisbon 三条件交集**只有 Casa Flora 一个**（fixture.html:361-387），使 smoke 断言"打开 Casa Flora"有一个唯一正确终点，错一步都能被查出来。6. **文章正文夹带自我指涉内容**（fixture.html:490）：讲的就是本仓的 finite-choice 方法论，演示叙事与靶页内容互证。

## 六、新人提示

- **scenario 参数只认 research**：`?scenario=travel` 与不带参数同效走列表（fixture.html:502-504 的三元判断）——demo.py:57 传 travel 只是显式语义，别以为页面有 travel 特殊分支。
- 浏览器**后退按钮不工作**是预期行为（无 hashchange 监听）；agent 也永远不会用它——返回靠点击"← All stays"按钮（fixture.html:444）。
- 卡片是 `button` 不是链接（fixture.html:428），而文章列表是 `a href="#id"`（fixture.html:479）——两种元素都会进 snapshot.js 的动作表，但语义角色不同，观察 label 时注意区分。
- `searched` 旗标（fixture.html:360）决定查询词过滤是否生效：**提交前**改类别/复选框是对全量房源过滤，提交后才叠加城市条件——排查"为什么搜空前还有结果"先看这个旗标。
- 图谱 hub 说本页"四个视图切换"且"刻意提供 search input/select/checkbox/button"——与源码核对一致（travel/detail/research/article 四函数，fixture.html:391/440/472/487）；tour 第 9 步描述亦无出入。
- 页面对 agent 完全无感知：没有任何为测试留的钩子或 data-testid，agent 走的是与真实网站完全相同的观察-执行通道——这正是它的价值。
