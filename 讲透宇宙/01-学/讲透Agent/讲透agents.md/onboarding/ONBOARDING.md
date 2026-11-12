# agents.md 官网仓新人 Onboarding（AGENTS.md 标准展示站）

> 基于知识图谱（55 节点 / 81 边 / 12 层 / 14 步 tour，commit `d001185`）与原仓源码逐行核实编写；文中所有 `路径 L行号` 锚均已对源码程序化验证。仓本地路径 `/usr-data/data2/repos/aaif-projects/repos/agents.md`。

## ① 这是什么仓

一句话：**AGENTS.md 开放标准的官方网站**——一个单页 Next.js 16 展示站（线上地址 https://agents.md），用一屏滚动的营销页语法讲清这个标准"是什么、为什么、怎么用、谁在用、谁在维护"。标准本体一句话可述：给 coding agent 的简单开放格式，"README for agents"；定义在 `README.md L5`-L8，最小示例文件在 `README.md L10`-L33（Dev environment tips / Testing instructions / PR instructions 三节的 pnpm+turbo+vite 工作流）。

核心事实速览：

- **栈极简**：Next.js 16.1.0 Pages Router + React 19.2.3 + Tailwind v4.1.11（CSS-first，经 `@tailwindcss/postcss`）+ `@vercel/analytics`，运行时依赖只有 4 个（`package.json L11`-L18）；`packageManager` 钉死 pnpm@9.15.1（`package.json L26`）；dev 脚本带 `--turbopack`（`package.json L6`）。
- **仓极小**：60 余个文件，裁掉 public/ 静态资产与 pdf 后入图分析约 29 个（`.understandignore L1`-L7）；`pages/` 只有 3 个文件，`pages/index.tsx` 是唯一页面与 composition root。
- **单页装配**：LandingPage 按固定顺序渲染 8 个区块 Hero→Why→Compatibility→Examples→HowToUse→About→FAQ→Footer（`pages/index.tsx L21`-L32）。
- **唯一数据流**：`getStaticProps` 在构建期抓 GitHub contributors API（`pages/index.tsx L47`-L160），全站再无第二个数据获取点。
- **治理**：标准源自 OpenAI Codex/Amp/Jules/Cursor/Factory 生态协作（`components/AboutSection.tsx L8`-L12，LICENSE 仍是 MIT © 2025 OpenAI），现由 Agentic AI Foundation（Linux Foundation 旗下）托管（`components/AboutSection.tsx L21`-L25），站点版权收束 LF Projects, LLC（`components/Footer.tsx L7`）。

**新人第一认知（本仓第一勘误）**：根目录 `AGENTS.md` 不是标准本体，而是本仓自己的开发协作指南（吃自家狗粮）——面向在本 Next.js 仓上干活的 AI agent（点名 Codex CLI），规定开发期只跑 `npm run dev` 保住 HMR、严禁在 agent 会话内跑 `npm run build`（`AGENTS.md L8`-L15，命令速查表 `AGENTS.md L37` 再次标红），另有 lockfile 同步（L17-L22）与"新组件用 TypeScript、样式与组件同目录"（L24-L28）两条约定。**标准的定义与最小示例在 README.md**。先读 README 再看站，别把根 AGENTS.md 当规范读。

## ② 仓库地图

| 位置 | 职责 | 关键锚 |
|---|---|---|
| `pages/index.tsx` | 唯一页面：8 区块装配 + getStaticProps 数据获取 | L17 装配、L47 数据 |
| `pages/_app.tsx` | 全局装配：注入 globals.css、SEO meta、Vercel 统计 | L1 样式、L8-L19 meta、L22 Analytics |
| `pages/_document.tsx` | 服务端 HTML 骨架 + 亮暗双 favicon；不导样式 | L7-L16 favicon |
| `components/`（16 文件） | 8 个区块组件 + Section 布局原语 + CodeExample 渲染器 + 5 枚手写 SVG 图标 | 见 ④⑤ |
| `styles/globals.css` | 全站唯一样式表：Tailwind v4 CSS-first、8 个 @font-face、跑马灯动画 | L1、L81、L113 |
| `public/`（31 文件） | og.png、favicon 三件、27 个工具 logo SVG（23 条目消费：19 单色 + 4 明暗对） | — |
| 根配置（5 文件） | package.json / tsconfig.json（`@/*` 别名 L20-L24）/ next.config.ts（只开 reactStrictMode）/ postcss.config.mjs / next-env.d.ts（自动生成，L5 注明勿手改） | — |
| 根文档 | README.md（标准本体载体）、AGENTS.md（本仓开发规范）、LICENSE（MIT, OpenAI）、Technical_Charter.pdf（AAIF 章程，被裁剪排除） | — |

依赖方向一句话：`index.tsx` 装配一切 → 各 XxxSection 复用 `Section.tsx` 原语与 `CodeExample.tsx` → 底层是 5 枚图标 + globals.css。没有任何反向依赖、没有状态管理库、没有测试目录、没有 CI workflow——这是一个把"极简"贯彻到底的展示站。

## ③ 分层架构：12 层走查

- **L01 构建与工具链配置**（5 文件）：next 16 + react 19 + tailwind v4 钉死版本，tsconfig 定义 `@/* → ./*` 路径别名，next.config.ts 实际只开 reactStrictMode 一项，postcss 唯一插件 `@tailwindcss/postcss` 走 v4 CSS-first 通道。
- **L02 全站样式与设计令牌**（1 文件）：globals.css 一份文件扛起全站视觉——v4 令牌、OpenAI Sans 字体、亮暗主题、跑马灯 keyframes 全在这。
- **L03 全局装配与 HTML 骨架**（2 文件）：_app.tsx 管样式注入与 SEO，_document.tsx 管 HTML 骨架与双 favicon，标准 Pages Router 分工。
- **L04 通用布局原语**（1 文件）：Section.tsx 是被 6 个区块复用的 children 插槽布局原语（见勘误 #3 的计数甄别）。
- **L05 基础图标组件库**（5 文件）：Copy/Clipboard/GitHub/Link/User 五枚无状态 SVG，currentColor 跟随主题。
- **L06 代码示例渲染器**（1 文件）：CodeExample.tsx（207 行）自带轻量 markdown 渲染与一键复制，是全站唯一有交互逻辑的组件。
- **L07 叙事内容区块**（4 文件）：Hero（首屏双 CTA）、WhySection（价值主张）、HowToUseSection（四步指南）、AboutSection（治理背景），全部纯静态。
- **L08 生态与案例展示区块**（3 文件）：CompatibilitySection（23 工具跑马灯/网格双视图）+ ExampleListSection（硬编码 4 仓案例墙）+ ExamplesSection（装配器）。
- **L09 FAQ 与页脚**（2 文件）：FAQSection 七条问答内嵌 compact CodeExample；Footer 收法律链接。
- **L10 首页装配主线**（1 文件）：pages/index.tsx，composition root + 全站唯一数据流起点。
- **L11 标准文档与协作指南**（2 文件）：README.md（标准本体）与根 AGENTS.md（工程规范），二者职责之辨是本仓第一课。
- **L12 图谱流水线元文件**（2 文件）：.understandignore 界定图谱范围，PROGRESS.md 是流水线台账（非网站内容）。

## ④ 新人导览路线：14 步 tour 叙事

**第一步先立甄别，最后一步收边界，中间按"底座→骨架→内容→数据"推进。**

1. **标准本体之辨**：README.md 是标准定义与最小示例的载体；根 AGENTS.md 是本仓开发规范（dev-not-build 铁律）。带着这个区分看站，才不会把工程约定当标准语义。
2. **工具链**：package.json 四依赖 + pnpm 钉版，next.config.ts 只开 strictMode——扫完即可确定全仓没有隐藏的构建复杂度。
3. **样式系统**：没有 tailwind.config.js；`@import "tailwindcss"`（globals.css L1）+ `@theme inline`（L81-L86）就是 v4 CSS-first 全貌，设计令牌直接写在 CSS 里。
4. **全局骨架分工**：改全站外观动 `_app.tsx`（globals.css 在 L1 注入），改 favicon/lang 动 `_document.tsx`——后者不碰样式。
5. **装配主线**：`pages/index.tsx L21`-L32 的八区块顺序就是页面滚动顺序，对着它的 import 列表走完全程。
6. **Section 原语**：`Section.tsx L18`-L44 只有几十行——id 锚点、h2、children 插槽、maxWidthClass 覆写（默认 max-w-6xl，L24）。读懂它，每个 XxxSection 就只剩内容差异。
7. **首屏 Hero**：大标题（L18）、60k 采用数链接（L24-L31，指向 GitHub code 搜索 `path:AGENTS.md NOT is:fork NOT is:archived`）、双 CTA（L42-L57，主按钮锚到 `#examples`），右列内嵌 HERO_AGENTS_MD 代码卡（L61-L66）。
8. **CodeExample**：轻量 markdown 渲染 parseMarkdown（L66-L101，标题加粗/列表/反引号行内代码高亮）+ 一键复制（L136-L144，成功后切换对勾图标 L156-L169）；compact 形态供 FAQ 单行命令内嵌（L193-L195）。
9. **WhySection**：README 面向人类、AGENTS.md 面向代理的分工论证（L17-L25），三条图标要点（L29/L38/L47），收尾开放格式立场（L56-L60）。
10. **HowToUse + About**：四步指南的重点在第 4 步 monorepo 嵌套规则——目录树中最近的 AGENTS.md 优先，OpenAI 主仓现有 88 个（`components/HowToUseSection.tsx L38`）；AboutSection 交代出身与 AAIF 治理归属。
11. **兼容跑马灯**：CompatibilitySection 是全站数据最密、逻辑最重的组件（详见 ⑥/⑦）。
12. **案例墙与数据流**：index→ExamplesSection→ExampleListSection 的 contributorsByRepo 透传链是全站唯一运行时数据流。
13. **FAQ + Footer**：七条问答覆盖标准关键语义——无必填字段（L13-L16）、冲突时最近的 AGENTS.md 胜且用户聊天提示最高（L18-L21）、旧文档迁移改名+symlink（L40）、Aider/Gemini CLI 配置片段（L58、L76-L80）。
14. **图谱边界**：public/ 静态资产、pnpm-lock.yaml、Technical_Charter.pdf 都被 .understandignore 裁在图外——图中没有它们不代表仓里没有。

## ⑤ 核心链路：pages/index.tsx 装配 + getStaticProps 数据流

**装配侧**：LandingPage（L17-L35）接收 `contributorsByRepo` prop 只透传给 ExamplesSection（L24），其余七区块零 props。注意 About 与 FAQ 被包进同一个 `flex-1` div（L26-L29），Hero 与 Footer 各自裸放（L21、L32）。

**数据侧**（getStaticProps，L47-L160，构建期执行一次）：

1. **清单与手工同步契约**：`repoNames` 四仓硬编码（L50-L55），上方注释明示"Keep in sync with the REPOS constant in that component"（L48-L49）——与 `ExampleListSection.tsx L22`-L45 的 REPOS 是**两份独立维护的同源数据**，加示例仓必须两头改。
2. **12 小时模块级内存缓存**：命中缓存直接返回且 `revalidate: 3600`（L60-L76）；新鲜抓取后写缓存并 `revalidate: 86400`（L147-L158）。缓存动机写在注释里：开发期反复刷新会撞 GitHub 匿名限额 60 req/h（L57-L59）。
3. **认证可选**：仅当环境变量 `GH_AUTH_TOKEN` 存在才附加 Authorization 头（L92-L94）——空 Authorization 头会被 GitHub 按匿名处理，故条件注入（L83-L86 注释）。
4. **头像**：每仓 `contributors?per_page=3` 取 top3（L99-L110）。
5. **总数用 Link header 技巧**：`per_page=1&anon=1` 请求（L115-L120），从响应 Link header 的 `rel="last"` 页码正则抽总数（L122-L127）——**不拉全量列表就算出贡献者总数**；无 Link header 时回退数组长度（L128-L131），单仓异常兜底空数据（L141-L144）。
6. **消费端**：ExamplesSection（L10-L22）在 Section(id=examples) 内先放 compact CodeExample（L15）再嵌 `standalone` 形态的案例墙（L19）；ExampleListSection 的 InnerGrid 按 REPOS 渲染卡片（L52-L83），头像倒序保证最高贡献者居右（L123），总数徽章 `+ N`（L180），卡片整体链到各仓 `blob/-/AGENTS.md`（L129），底部"View 60k+ examples"外链 GitHub 搜索（L74-L81）。

一句话：这是教科书式的 SSG 数据流——构建期抓一次、内存缓存防限流、ISR revalidate 保新鲜，客户端零请求。

## ⑥ 关键设计决策

1. **依赖面最小化**：4 个运行时依赖撑起整站；图标手写 SVG（5 文件）、跑马灯纯 CSS 动画、markdown 渲染自写 60 行（`CodeExample.tsx L66`-L121）而非引入 react-markdown——展示站不值得为此加包。
2. **Tailwind v4 CSS-first**：无 tailwind.config.js，`@theme inline`（globals.css L81-L86）把 CSS 变量映射为设计令牌；亮暗主题靠 `prefers-color-scheme` 换 `:root` 变量（L88-L93），零 JS 主题切换。
3. **品牌 logo 双方案跟随主题**：单色 logo 用 CSS `mask-image`（`CompatibilitySection.tsx L196`-L211，底色 `bg-gray-700 dark:bg-gray-400` L199）；明暗敏感 logo（VS Code/Ona/Devin/Windsurf）用双 SVG 按 `dark:hidden/dark:block` 切换（L179-L195）。
4. **跑马灯的工程质量**：挂载后洗牌避免固定排序偏袒某家（L271-L273，Fisher-Yates L144-L151）；IntersectionObserver + getBoundingClientRect 双重判定视口可见性、离屏暂停（L286-L305）；动画时长由组件注入 `--marquee-duration`（L248，globals.css L115 只是 70s 回退缺省），上 70s/下 80s 且下行 offset -35 制造交错感（L356-L362）；`prefers-reduced-motion` 时整体关闭（globals.css L128-L132）。
5. **数据获取的礼貌设计**：Link header 页码技巧 + 12h 内存缓存 + 条件认证，全部为了把 GitHub API 压力压到最低（见 ⑤）。
6. **开放格式哲学的代码自证**：CompatibilitySection 的 23 条目里 Aider/Gemini CLI/opencode/Zed/Warp 的 url 直链各家长文档的 conventions/rules 页而非首页（L49、L54、L70、L80、L90）；网格/跑马灯切换按钮带 aria-controls/aria-expanded（L370-L371）——标准的中立性与无障碍细节都写进了组件。

## ⑦ 常见误读与勘误（源码实证）

1. **根 AGENTS.md ≠ 标准本体**（第一勘误，详见 ①）：它是本仓开发协作指南；标准定义与最小示例在 README.md。
2. **兼容工具条目是 23 个，不是图谱层描述的 24 个**：`grep -c '^    name: "' components/CompatibilitySection.tsx` = 23（Codex L16 … Junie L137 逐一清点）；public/logos 的 27 个 SVG = 19 单色 + 4 明暗对 ×2，与 23 条目严格对账吻合。批次摘要里的"24"系计数误差。
3. **Section 的复用方是 6 个，不是 7 个**：`<Section` JSX 调用全仓 6 处——Examples（L12）/FAQ（L92）/About（L4）/Compatibility（L328）/Why（L9）/HowToUse（L46）；Hero 与 Footer 自带标签不经过 Section。
4. **"Who uses AGENTS.md?" 标题是准死代码**：ExampleListSection 唯一调用方 ExamplesSection 传 `standalone`（`ExamplesSection.tsx L19`），走裸网格分支（L89-L95）；带 h2 标题与 `-mt-36` 上提留白的非 standalone 分支（L97-L104）现站永不渲染，仅为独立使用保留。
5. **CodeExample 两处死代码**：`ClipboardIcon` import 后零使用（`CodeExample.tsx L2`，实际只用 CopyIcon L171 与内联对勾 L157-L169）；`href` prop 声明+解构（L8-L9、L128）但渲染体从不引用——Hero 传入的 GitHub 链接（`Hero.tsx L65`）被静默丢弃。
6. **`--font-geist-mono` 从未定义**：globals.css L85 的 `--font-mono: var(--font-geist-mono)` 引用了一个全仓不存在的变量（grep 实证仅此一处出现），font-mono 令牌实际解析为空。
7. **_app/_document 分工**：样式只在 `_app.tsx L1` 注入；`_document.tsx` 只管骨架与双 favicon——在 _document 里找样式注入会扑空。
8. **跑马灯不是 CSS 固定 70s**：真实时长由组件内联注入（70/80s 双行不同速），globals.css 的 70s 只是 `var()` 回退。
9. **README 示例与站内示例是双头维护**：`README.md L13`-L32 的最小示例与 `CodeExample.tsx L34`-L61 的 EXAMPLE_AGENTS_MD 逐字同源（仅换行续行符差异）——但**没有任何注释提示同步**（对比 repoNames/REPOS 有明示注释），改文案极易漏一边。
10. **`hideOnSmall` 恒 false**：`ExampleListSection.tsx L64` 的 `key > 3` 在当前 4 仓（key 0-3）下永不触发，只有第 4 张卡经 `key > 2`（L65）在 md 断点隐藏（md 3 列排不下第 4 张）；hideOnSmall 是为 5+ 仓预留的死参数。
11. **HowToUseSection 没有页内锚点**：它的 Section 调用（L46-L51）不传 id，而 Why/Compatibility/Examples/FAQ 都有（why/compatibility/examples/faq）——Hero 主 CTA 锚的是 `#examples` 不是 HowToUse。
12. **@svgr/webpack 疑似遗留 devDep**：`package.json L20` 声明，但 next.config.ts 只开 reactStrictMode、无任何 webpack/svg 配置消费它。
13. **数字口径**：站内"60k"两处（Hero L30、ExampleListSection L79）都是 GitHub 搜索结果数的快照文案，非实时统计。

## ⑧ 上手验证

**跑起来**（README.md L40-L49）：`pnpm install` → `pnpm run dev`（turbopack）→ 打开 http://localhost:3000。**切记本仓铁律**：agent 会话内绝不跑 `pnpm build`（根 AGENTS.md L12-L15——会把 .next 切成生产资产导致 HMR 失效）。想看生产构建去 CI 或本机手动会话外执行。

**改哪里看效果**（每条都是最小验证回路）：

| 想改什么 | 动哪里 | 验证 |
|---|---|---|
| 首屏文案/CTA | `components/Hero.tsx L18`-L57 | dev server 热更直接看首屏 |
| 主题色 | `styles/globals.css L75`-L79（:root 变量） | 切系统亮暗模式看双色 |
| 加一个兼容工具 | `CompatibilitySection.tsx agents 数组 L14`-L142 加条目 + `public/logos/` 放 SVG（单色走 mask，明暗敏感放两个） | 跑马灯/网格双视图都应出现新条目 |
| 换示例仓 | **两处同步**：`pages/index.tsx L50`-L55 + `ExampleListSection.tsx L22`-L45（注释明示的契约） | Examples 区卡片与贡献者数据一致 |
| 站内示例文案 | `CodeExample.tsx L34`-L61（建议连 README.md L13-L32 一起改，见勘误 #9） | Hero/Examples 代码卡更新 |
| 贡献者数据不刷新 | dev 重启或等 12h 缓存过期（`pages/index.tsx L60`）；设 `GH_AUTH_TOKEN` 提额（L92） | Examples 卡片头像/总数变化 |

**无构建验证锚点**（不跑任何命令的纯文本审计）：`grep -c '^    name: "' components/CompatibilitySection.tsx` 应得 23；`grep -rn 'ClipboardIcon' components/CodeExample.tsx` 只有 import 一行（死 import 实证）；`grep -rn 'geist' styles/ pages/ components/` 只有 globals.css L85 一处（未定义变量实证）。

> 非空白字符 9871 / 锚 48
