# 讲透 agents.md

> agentsmd/agents.md —— agents.md 标准官网仓（Next.js）：为网站定义给 AI agent 的说明文件标准（类比 robots.txt 之于爬虫）。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/agents.md（HEAD d001185d，2026-10-21 聚合）

## 状态（2026-11-01 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（**25 页 100%**，全文 223K 字符，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**55 节点/81 边/12 层/14 步 tour，validator 0 issues 0 warnings（内置+独立双跑），fingerprints 29 文件@d001185d**；5 批 2 worker 并行 30 分钟收官——public/ 27 svg+pdf 已裁，2026-11-01） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（9,885 非空白字符/8 节/48 锚） |
| explain 系列 | ✅ | [explain/](explain) 6 篇（小仓口径，A2A 先例；01 index 装配+getStaticProps · 02 README 标准本体 · 03 Compatibility 跑马灯/网格 · 04 ExampleList 准死代码 · 05 CodeExample 复制交互 · 06 Tailwind v4 样式壳；主会话独立抽验 6 锚全中） |

## 源码级勘误钉版（批分析+写手实证，2026-11-01）

1. **根 AGENTS.md 是本仓开发协作指南（Codex CLI/HMR 保护/dev-not-build 约定）非标准本体**——AGENTS.md 标准的规范定义与最小示例在 README.md。
2. **ExampleListSection 的 h2 "Who uses AGENTS.md?" 是准死代码**——唯一调用方 ExamplesSection L19 传 `standalone`，h2 仅在 standalone=false 渲染；hideOnSmall(key>3) 在仅 4 仓时恒假。
3. CompatibilitySection 兼容工具实为 **23 个条目**（非 24）：跑马灯/网格双视图，27 个 logo 文件=19 单色+4 明暗对×2 与 23 严格对账。
4. Section.tsx 布局原语实被 **6 个区块复用**（Hero/Footer 不用它）。
5. globals.css=**Tailwind v4 CSS-first**（@import tailwindcss+@theme inline，无 tailwind.config.js）；样式注入唯一在 _app.tsx，_document.tsx 不导样式；`--font-geist-mono` 引用了全仓未定义变量。
6. getStaticProps=全站唯一数据获取点：Link header rel=last 页码技巧算贡献者总数+12h 模块级内存缓存；repoNames 与 REPOS 常量手工同步（无同步注释的双头维护）。
7. CodeExample L2 ClipboardIcon 死 import；Hero L65 传入的 href 是被静默丢弃的死 prop（L9/L128 声明解构但组件体零渲染）。
8. **Section.tsx L38 `prose prose-neutral dark:prose-invert` 三类名惰性**——@tailwindcss/typography 未安装（package.json 零依赖）且无 `@plugin` 指令，三类名零 CSS 产出。
9. **package.json `@svgr/webpack` 死依赖**——全仓零 `.svg` import（public/ svg 全走 `<img>`），next.config.ts 仅 reactStrictMode。
10. ExampleListSection 三处准死代码：standalone 分支不可达 + hideOnSmall 恒假 + hideOnMedium 半活（04 篇）。

## DeepWiki 章节速览（8 章）

1 Overview · 2 Getting Started · 3 Architecture · 4 Components · 5 Static Assets · 6 Development Guide · 7 AGENTS.md Specification · 8 Glossary

核心章是 7 AGENTS.md Specification（标准本体）；4 章 Components 的 7 个三级页（Grid View / Marquee 动画 / LogoItem 等，deepwiki/x1-x7）偏前端实现细节。

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)（含 2026-10-22 三级页口径甄别结论）
