# 10 · version-warning.js —— 六版本同站共存下的"你在看旧版"UX 卫兵

## 1. 角色定位

`docs/version-warning.js` 是图谱 `file:` 节点，归第 14 层站点装配——与 footer.js（23 行 LF 版权注入）、style.css 同为 docs 根的站点资产，不隶属任何 MDX 内容页。它解决的问题：MCP 用日期版本制，`docs/specification/` 与 `docs/docs/` 各有 6 个版本目录（2024-11-05/2025-03-26/2025-06-18/2025-11-25/2026-07-28/draft，ls 实证），docs.json navigation 的 Documentation 与 Specification 两 tab 各挂 6 个 version 条目（2026-07-28 为 default:true）。旧版页被搜索与外链长期引用，读者落进 2024-11-05 毫无感知——本文件是这棵版本树的 UX 卫兵：旧版页亮黄色 warning、draft 页亮中性 info，并附"跳最新版等价页"链接。

注入方式经反证核实：docs.json 全文（grep '\.js\|footer\|warning'）零引用本文件与 footer.js，无显式注册——挂载全靠 Mintlify 目录约定"自动加载 docs 目录全部 .js"，该约定的唯一文档即文件头注释 L5-6。头注释 L1-10 同时给出三条承诺：警示旧版与 draft（L2-3）、以站点 latest 重定向为真源故发版零改动（L6-9）、样式复用原生 callout 类（L9-10）。

## 2. 内部结构（197 行地图）

配置区 L12-69：`DRAFT_VERSION` L12；SECTIONS 数组 L13-29 描述两个受保护区，每项五元组——路径正则 L15/L22（同时捕获日期版/draft/latest 与子路径）、latest 别名 L16/L23、sessionStorage 键 L17/L24、名词 L18/L25、draft 文案 L19/L26-27；`BANNER_ATTR` L30 定义 `data-spec-version-banner`，是全文件去重锚；样式常量 L32-48（warning 黄 L32-36 / info 中性 L37-40，内建 dark: 变体 L35/L39）；内联 SVG 图标 L50-69。

四个函数（批分析三主节点 L79-92/L94-123/L127-180，外加一个）：

- parseVersionedPath L71-77：遍历 SECTIONS 试正则 L72-74，命中返回 {section, version, subPath}。
- resolveLatestVersion L79-92：latest 判定三级真源——sessionStorage 缓存 L80-81；miss 则对 latestAliasPath 发 HEAD L83；fetch 自动跟随重定向，`new URL(response.url).pathname` L84 取落地路径再同正则反解 L85-86；仅解析成功且非 "latest" 才回写缓存 L88-90（失败不缓存，下次重试）。
- createBanner L94-123：纯 DOM 组装。容器 L95 按 isDraft 选样式 L96，设 role="alert" L97、去重锚 L98、data-callout-type L99；innerHTML 只喂静态 SVG 常量 L104；文案与链接全走 textContent L111/L113-115——运行时数据不经 innerHTML，无 XSS 面。
- insertWarningBanner L127-180：主编排（见第 4 节）。

双查重为何必要：Mintlify 是 SPA，换页靠 pushState 换 DOM、不重载脚本，且本文件自己的插入也会触发 observer 形成自触发回路。三道闸：`inserting` 标志 L125 在入口 L128 拦重入、finally L177-179 复位；入口查横幅已存在即返回 L129；关键在 L136 的 await 之后——fetch 往返期间 SPA 可能已换页、并发调用可能已插入，故 L143 复查横幅、L144-147 比对当前 URL 的 version 是否仍等于发起时的版本，任一不符即放弃，防插错页或重复。引导 L182-186 按 readyState 二选一；L189-197 的 MutationObserver 监听 body 全子树，横幅不存在且 URL 仍版本化 L191-192 才重插——这就是横幅在 SPA 导航后的存活机制。

## 3. 外部连接

与 footer.js 的姐妹关系：共享同一套三件套骨架——readyState 引导（footer.js L14-18 对应本文件 L182-186）、body MutationObserver（footer.js L21-22 对应 L189-197）、幂等锚点（footer.js L5 查 lf-copyright 对应 L129 查 BANNER_ATTR）。差异：footer.js 以 IIFE 封装 L2，observer 无条件重跑 addCopyright、靠 L5 幂等闸兜住；本文件顶层 const、observer 回调带前置条件 L190-193 才调用。

与 docs.json 的数据耦合：本文件不读 docs.json，靠 HTTP 重定向间接对接。docs.json 的 redirects 配 4 条 latest 规则：/specification/latest→/specification/2026-07-28 与 /docs/latest→/docs/2026-07-28/getting-started/intro（各含 :slug* 通配版）。L83 的 HEAD 命中的正是这组规则，L84 的 response.url 即重定向落地 URL。另：docs.json 的 footer 键只有 socials，LF Projects 版权全靠 footer.js 客户端补——declarative 与 imperative 双轨 footer 并存。保护对象是图谱低层 document 节点的版本树：六日期版 × spec/docs 两区，横幅按 L15/L22 正则识别其中每一个。

## 4. 数据流：点开 /specification/2025-06-18/basic/lifecycle 的完整时序

1. 引导：Mintlify 自动加载脚本，L182-186 按 readyState 调 insertWarningBanner。
2. URL 解析：L131 取 pathname 交 L71-77，正则 L15 捕获 version=2025-06-18、subPath=/basic/lifecycle。
3. latest 解析：L136 → 缓存 miss L80-81 → HEAD /specification/latest L83 → 服务端按 docs.json 规则 308 到 /specification/2026-07-28 → L84 取落地 pathname → L85 反解得 2026-07-28 → L89 回写 sessionStorage。
4. 比对与复查：版本不等，L139 不提前返回；确认无横幅 L143、URL 版本未变 L144-147。
5. 定位与渲染：L149-151 按 `#content-area, main, article, .content` 找内容区；latestHref=别名+subPath L156，借 :slug* 重定向落到最新版等价页（注释 L154-155 明言此意图）；链接文本 L157；非 draft 走旧版文案 L162 与 warning 样式 L96；L164 交 createBanner。
6. 挂载：Mintlify 把 H1 包在 header#header，L169-171 取它（兜底裸 h1），L173 insertAdjacentElement("afterend") 插标题块正下方，再兜底插内容区顶部 L175。
7. SPA 存活：此后任何 DOM 变更触发 L189→L194 重插；切到 latest 版页面则 L139 版本相等静默退出；切到 /community 等非版本路径则 L131 得 null 全程静默。draft 页同链路，仅 L159 分叉 isDraft，换 INFO 样式与 L19 专属文案。

## 5. 设计决策

- 客户端 JS 而非构建期注入：Mintlify 托管平台不开放渲染管线；六版本 × 全部 MDX（含从 schema.ts 生成的 schema.mdx）逐页加组件不现实。".js 自动加载"是唯一免注册的全站钩子，于是横幅长在 DOM 里而非源文档里。
- latest 以重定向为真源（L6-9）：硬编码版本号则每次发版要改两处；改为请求 /specification/latest 让服务端重定向代答，真源收敛到 docs.json redirects 单点——发版只改 docs.json，本文件零改动，即注释 L8-9 "requires no updates when a new version is published" 的含义。代价是首访多一次 HEAD 往返，L80/L89 的 sessionStorage 把每会话每 section 摊销到最多一次。
- 197 行不引框架：只依赖 fetch/DOM/MutationObserver 三个原生 API；安全靠分工——innerHTML 只承载 L50-69 静态 SVG，版本号等运行时数据走 textContent L111，subPath 被 L15 正则约束为以 / 开头的路径段，无法构造 javascript: href。
- 日期版本制的简化：`\d{4}-\d{2}-\d{2}`（L15）字典序即时间序，"是否最新"退化为 L139 一次字符串不等比较，无需 semver 解析；draft 不参与排序，经 L159 单独走 info 分支。
- 样式复用 callout 类（L9-10、L32-48）：与 Mintlify 原生 callout 同观感（含暗色 L35/L39），降低维护与视觉漂移成本。

## 6. 新人提示

- 改横幅文案：旧版模板在 L162，draft 文案 per-section 在 L19 与 L26-27，链接文本在 L157。
- 发新版本要动几处：docs.json redirects 4 条 latest 目标改成新日期 + navigation 两 tab 的 versions 头部插入新条目（版本目录与 schema 生成另见仓库根 CLAUDE.md）；version-warning.js 一行不改——若发版必须改它，即违背 L8-9 承诺，应视为 bug。
- 加新受保护区（如给 /extensions 配横幅）：在 SECTIONS L14-20 复制一个五元组条目，前提是 docs.json 先配好对应 latest 重定向。
- 调试技巧：`sessionStorage.removeItem('mcp-latest-spec-version')` 后刷新可强制重走 L83 的 HEAD 重解析；控制台 `document.querySelector('[data-spec-version-banner]')` 验证挂载（L98 设的属性即现成调试锚）；在旧版页点版本切换器模拟 SPA 导航，观察 L144-147 如何拦截"fetch 期间已换页"的错插。
- 排坑：横幅忽隐忽现优先查三道闸 L125/L129/L143；全站 git grep 横幅文案只会命中本文件——别去 MDX 里找，它是 DOM 注入不是文档组件。

---

> 非空白字符 4649 / 锚 78（version-warning.js 75 + footer.js 3，全部对照源码逐行核实）
