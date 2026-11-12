# 精讲：styles/globals.css + pages/_app.tsx + pages/_document.tsx + components/Section.tsx —— Tailwind v4 CSS-first 样式壳与区块插槽原语

> 区域：`styles/globals.css`（132 行）+ `pages/_app.tsx`（24 行）+ `pages/_document.tsx`（24 行）+ `components/Section.tsx`（44 行），顺带 `components/icons/` 五小组件。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read/Grep 从源文件核实（2026-11-01）。

## 角色定位

这四个文件构成本站的**样式与骨架壳**：globals.css 是唯一的样式表（Tailwind v4 CSS-first 范式 + 全仓唯二的自定义 CSS：字体与跑马灯动画）；_app.tsx 是每页都执行的 App 壳（**全局样式的注入点**、SEO meta、Vercel Analytics）；_document.tsx 是服务端文档骨架（html/lang/双 favicon）；Section.tsx 是六个内容区块复用的**插槽原语**——统一 section 容器、h2 标题、最大宽度与水平 padding。三者分工是 Pages Router 的教科书布局：谁渲染（_document，SSR-only）→ 谁常驻（_app，每页）→ 谁长什么样（globals.css + Section）。

**版本口径勘误（任务书）**：Section 的消费方实测为 **6 个组件**（grep `from "@/components/Section"` 实证：Why/About/FAQ/HowToUse/Examples/Compatibility 各 1 处），非 7——首页 8 区块里 Hero 是 `<header>`、Footer 是 `<footer>`，均不走 Section。

## 内部结构

**globals.css 五段（132 行）**：

| 段 | 行号 | 内容 |
|---|---|---|
| Tailwind 入口 | `:1` | `@import "tailwindcss";` 单行——v4 CSS-first：**仓内无 tailwind.config.js**（文件清单实证）；PostCSS 仅挂 `@tailwindcss/postcss`（postcss.config.mjs L2），版本 4.1.11（package.json L12/L17） |
| 字体 | `:3-73` | 7 个 `@font-face`——OpenAI Sans 四字重 × 正体/斜体，全外链 `cdn.openai.com`（首例 L8），`font-display: swap`（L4） |
| 主题变量 | `:75-93` | `:root` 定义 `--background/--foreground/--font-sans`（L75-79）；`@theme inline`（L81-86）把 CSS 变量桥接成 Tailwind token（→ 生成 `bg-background` 类）；dark 媒体查询下换暗色值（L88-93） |
| 基础样式 | `:95-111` | body 消费三变量（L95-99）；`pre/code` 全局强制 `pre-wrap + overflow-x: visible`（L102-111，注释 L101 自述 "Ensure code blocks wrap..."） |
| 跑马灯 | `:113-132` | `.logo-marquee-track`（max-content + `animation ... var(--marquee-duration, 70s)` + will-change，L113-117）；keyframes `translateX(0→-50%)`（L119-126）；`prefers-reduced-motion` 关停（L128-132） |

**_app.tsx（24 行）**：L1 `import "@/styles/globals.css"`——全局样式唯一引入点；L4 引 `@vercel/analytics/next`；L7-20 用 **next/head**（与 _document 的 Head 不是同一组件）装页面级 meta——title（L8）、description（L9，含 "60k" 口径）、twitter 五条（L10-15）、og 四条（L16-19）；L21-22 渲染页面并挂 `<Analytics />`。

**_document.tsx（24 行）**：骨架四件套 `Html/Head/Main/NextScript`（L1）；`lang="en"`（L5）；**双 favicon 按系统主题切换**——light 挂 `media="(prefers-color-scheme: light)"`（L7-11）、dark 挂 L12-16；`<body className="antialiased">`（L18）。仅服务端每请求渲染一次，不放 React 状态与 CSS import。

**Section.tsx（44 行）**：Props（L3-16）——`title` 必传，`id`/`className`/`center`（L10）/`maxWidthClass`（L15，默认 `max-w-6xl`，L24）。渲染（L28-42）：`<section id className+px-6>`（L29）→ 容器 `${maxWidthClass} mx-auto flex flex-col gap-6`（L26）→ h2 `text-3xl font-semibold tracking-tight`（L31-35，center 加 `mx-auto text-center`）→ 内容槽 `prose prose-neutral dark:prose-invert max-w-none`（L38-40）。L36-37 注释认真讨论 prose 行为——但见勘误 2。

## 外部连接

- **Section 的 6 个消费方**（各用 1 次）：WhySection L9-15（`max-w-3xl` center）、ExamplesSection L12（默认 max-w-6xl）、CompatibilitySection L328-334（`maxWidthClass` 动态切换 + `!px-0` 出血，03 篇）、HowToUseSection L46-51（max-w-3xl）、AboutSection L4（max-w-3xl + `pb-0`）、FAQSection L92-98（max-w-3xl + `py-20`）。窄内容区一律 3xl、宽内容（卡片网格）用默认 6xl，是全站的排版节拍。
- **globals.css ← CompatibilitySection**：`--marquee-duration` 自定义属性由组件 L248 注入、L115 消费；`.logo-marquee-track` 类名由组件 L254 挂载。
- **globals.css → CodeExample**：L102-111 的 pre 规则作用于其 `<pre>`（L174）——层叠关系见设计决策 3。
- **_app ← 全部页面**：Pages Router 中 _app 包住每个 page（此处仅 index.tsx），故 L1 的 CSS 与 L7-20 的 meta 全站生效；Hero.tsx 无自有 head，`<title>` 唯一来源就是 _app L8。
- **icons/ 五小组件（120 行）一句带过**：CopyIcon（15 行，CodeExample L171）、ClipboardIcon（27 行，WhySection L29）、GitHubIcon（24 行，Hero L55）、LinkIcon/UserIcon（各 27 行，WhySection L38/L47）——手写 `<svg path>` 函数组件，className 可覆写，无 svgr/图标库依赖。

## 数据流（样式与暗色模式的注入链）

```
_document.tsx（SSR 骨架，每请求一次）
 └─ <html lang="en"> + 双 favicon（L7-16 media 查询）+ <body class="antialiased">
_app.tsx（每页包裹层）
 ├─ L1 import globals.css → PostCSS 展开 v4：四层 @layer + 源码类名扫描成原子 CSS
 ├─ next/head：title/meta（L7-20）注入 <head>
 └─ <Component>（index.tsx）→ 6 个 Section 消费方
暗色模式全链（零 JS、零 class 切换，纯 OS 级跟随）：
 prefers-color-scheme
 ├─ :root 变量换值（globals.css L88-93 → body L96-97）
 ├─ dark: variant（v4 默认 media 策略）
 └─ 双 favicon（_document L7-16）+ 双 logo 图（CompatibilitySection L186/L193）
```

## 设计决策

1. **Tailwind v4 CSS-first 的极简落地**——没有 tailwind.config.js、没有 content 数组（v4 自动探测源码）、主题定制只有一段 `@theme inline`（L81-86）。`inline` 关键字让 token 直接内联引用 `:root` 变量，暗色切换只改变量值（L88-93）而无需重生成 utilities——媒体查询级暗色模式的最省实现。
2. **样式注入点在 _app 而非 _document**——Pages Router 的硬规则：_document 只在服务端渲染，往里面 import CSS 不会进入客户端激活路径；_app 是每页常驻组件，L1 的 import 保证样式随每个页面 bundle 注入。常见迁移错误（把 App Router 习惯带进来在 _document 引样式）在本仓被正确规避。同理 meta 进 _app 的 next/head（可按页覆盖），favicon 进 _document 的 Head（文档级静态）——两个 Head 各司其职。
3. **unlayered CSS 压制 utility 的隐蔽杠杆**——globals.css L102-111 的 `pre {}` 写在文件顶层（不在任何 @layer），而 Tailwind v4 utilities 位于 `@layer utilities`；按层叠规则**未分层样式优先**，故 CodeExample L175 的 `overflow-x-auto` 实际被 L103 的 `visible` 覆盖——代码块永远换行、永不横向滚动。这是设计而非意外（L101 注释直书意图）：AGENTS.md 样例是"给 agent 抄的原文"，完整性优先于排版。
4. **字体外链 CDN 而非自托管**——七个字重全走 `cdn.openai.com`（L8 等）：零构建资产；代价是可用性绑外部 CDN（离线时回退 Arial/Helvetica，L78 fallback 链）。
5. **Section 用组合而非继承适配六种区块**——maxWidthClass/center/className 三个开放参数让 About（pb-0）到 Compatibility（!px-0 出血）共用一个骨架；硬编码的 `px-6`（L29）留了 important 逃生舱——插槽原语的"窄接口 + 破例通道"形态。

## 新人提示

1. **勘误 1（本轮新发现）：`--font-geist-mono` 悬空引用**。globals.css L85 `--font-mono: var(--font-geist-mono)`——但 `--font-geist-mono` 全仓未定义（grep 实证：该名字仅此一处；仓内无 next/font、无 Geist 字体加载），且 `font-mono` 工具类也全仓零消费。这是 create-next-app **App Router 模板的遗产**：模板在 layout.tsx 用 next/font 定义该变量，移植到 Pages Router 时字体加载被删、@theme 里的引用残留。双死链（定义死、消费也死），删除 L85 无任何影响。
2. **勘误 2（本轮新发现）：Section L38 的 `prose prose-neutral dark:prose-invert` 是惰性类名**。`prose` 系来自 @tailwindcss/typography 插件——实测该包未安装（package.json L11-18 依赖清单无）、globals.css 也无 v4 的 `@plugin "@tailwindcss/typography";` 指令（132 行全读实证）→ 三个类名零 CSS 产出，仅 `max-w-none` 有效。L36-37 注释还在认真讨论 prose 的 margin 行为，说明作者当它活着。视觉上无 bug（没有 prose 反而避免了意外 margin），但"想调正文字距/标题尺度时改 prose 配置"这条路是死的——实际排版靠消费者自传类名。修复路径：装插件 + globals.css 加一行 @plugin；或删掉三个死类名与误导注释。
3. **勘误 3（本轮新发现）：`@svgr/webpack` 是死依赖**。package.json L20 的 devDependencies 声明了它，但全仓零 `.svg` import（grep 实证 exit 1——logo 走 next/image 与 CSS mask，icons 是手写 JSX），next.config.ts 也只有 `reactStrictMode: true` 无 webpack 配置。装而不用，可安全移除。
4. **加全局样式的正确姿势**：布局级（pre 换行这类）直接写 globals.css 顶层——记住设计决策 3 的杠杆：顶层规则压过一切 utility，慎用；组件级优先 Tailwind 类名；真正的新 token 走 `@theme`（普通块生成新 utility，`inline` 块内联变量）。
5. **暗色模式没有手动开关**——全链绑定 OS 偏好（媒体查询），想加 toggle 须引入 next-themes 切 class 策略，并同步改造 `:root` 变量（L88-93）与全部 `dark:` 前缀的生效条件——改动面远大于"加个按钮"。
6. **Section 加新区块先查参数表**：窄内容传 `maxWidthClass="max-w-3xl"` + `center`（四家先例）；全宽出血学 Compatibility 的 `!px-0` + `max-w-none`（L331-333）；`id` 需要页内锚点才传（FAQ 传了 `faq`，多数没传）。

---

> 非空白字符 6000 / 锚 82
