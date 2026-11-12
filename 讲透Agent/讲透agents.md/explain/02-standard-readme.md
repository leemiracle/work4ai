# 精讲：README.md —— AGENTS.md 标准本体（规范定义与最小示例的真正居所）

> 区域：`README.md`（50 行）为主，对照根 `AGENTS.md`（43 行）。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read 从源文件核实（2026-11-01）。

## 角色定位

对大多数仓库，README 是项目说明书；对这个仓库，README **就是产品本体**——AGENTS.md 不是一个软件而是一个**文件格式约定**（"a simple, open format for guiding coding agents"，README L5），而格式的规范定义、最小示例、官网入口全部落在这 50 行 Markdown 里。这个仓库里没有 .proto、没有 JSON Schema、没有 normative 章节（对比同目录下的 A2A 规范仓），"标准"的全部规范性内容就是一句定义（L5-8）加一个可复制的样例（L12-33）：AGENTS.md 是仓库根目录（或子目录）下一个普通 Markdown 文件，写给 AI coding agent 读，替代/补充人类向的 README。

**第一勘误（本仓最易踩的认知陷阱）**：仓根的 `AGENTS.md` **不是**标准文档。它是这个仓库自己雇 coding agent（注释明写 Codex CLI，AGENTS.md L4）干活时的**本仓开发协作指南**——讲的是"改本网站代码时用 dev server 别跑 build"（L8-15）、"改依赖记得更新 lockfile"（L17-22）。两个文件名字互为镜像：`README.md` 装着 AGENTS.md 标准，`AGENTS.md` 装着本仓的 README 式协作说明。更妙的是，根 AGENTS.md 的存在本身就是这个标准的**活样本（dogfooding）**——官网仓库先用自己倡导的格式来指导自己的开发。

## 内部结构

**README.md 五段式（50 行）**：

| 段 | 行号 | 内容 |
|---|---|---|
| 标识 | `:1-3` | `# AGENTS.md` 标题 + logo 图（引用 `./public/og.png`，L3——官网 og 分享图复用作 README 门面） |
| 一句话定义 | `:5-8` | "simple, open format for guiding coding agents"（L5）+ 核心比喻 "**a README for agents**: a dedicated, predictable place"（L7-8） |
| 最小示例 | `:10-33` | L10 引出，L12-33 一段 \`\`\`markdown 围栏代码：`# Sample AGENTS.md file` + 三个小节——`## Dev environment tips`（4 条 pnpm/turbo/Vite 命令）、`## Testing instructions`（7 条测试纪律）、`## PR instructions`（2 条提交规范，L30-33） |
| Website | `:35-38` | 仓里还包含一个 Next.js 网站，托管在 https://agents.md/（L37） |
| 本地运行 | `:40-49` | 三步：`pnpm install`（L43）→ `pnpm run dev`（L47）→ localhost:3000（L49） |

注意示例的选材用心：它不是抽象占位符，而是一份**真实可用的 pnpm monorepo 工作流指南**（turbo run where 跳包、vitest -t 聚焦单测、PR 标题格式 `[<project_name>] <Title>`），三节恰好对应 agent 干活的三类高频需求——环境搭建、验证闭环、提交规范。

**根 AGENTS.md 四节（43 行）**：L3-6 背景说明（本仓是根目录 Next.js 应用，强调保住 HMR 热更新）；§1（L8-15）**最重要的一条纪律**——迭代时永远用 `npm run dev`（或 pnpm/yarn dev，L10），**禁止在 agent 会话里跑 `npm run build`**（L12-13），因为生产构建会把 `.next` 切到生产资产、废掉热更新，确需生产构建要移出交互会话（L15）；§2（L17-22）改依赖后更新 lockfile 并重启 dev server；§3（L24-28）编码约定——新代码优先 TypeScript、组件样式与组件同目录；§4（L30-38）命令速查表，L37 的 build 行加粗警告 "do not run during agent sessions"；L41-43 结语"拿不准就重启 dev server 而不是跑生产构建"。

## 外部连接

- **官网文案三处同源**：README L5 的定义句与 Hero.tsx L21（"A simple, open format for guiding coding agents"）完全一致；"60k open-source projects" 规模口径同时出现在 README 无、而 Hero L30、_app.tsx L9（meta description）、ExampleListSection L79（"View 60k+ examples"）三处——README 反而没提规模数字，措辞最保守。
- **最小示例的双份维护**：README L12-33 的样例与 CodeExample.tsx L34-61 的 `EXAMPLE_AGENTS_MD` 常量是**同一段文字的两份手工拷贝**（后者用反斜杠续行折行）——网站默认展示的"AGENTS.md in action"代码块就是它。改样例要改两处，且没有任何同步机制（05 篇详述）。
- **治理线**：AboutSection L21-25 声明 AGENTS.md 由 Agentic AI Foundation（aaif.io）在 Linux Foundation 下托管；Footer L7 版权行 "a Series of LF Projects, LLC"；仓根的 `Technical_Charter.pdf` 是对应章程文件。README 本身不提治理，把这条线留给了官网 About 区块。
- **AGENTS.md 自述的命令表 vs package.json 现实**：AGENTS.md L36 列了 `npm run test` 并诚实标注 "(if present)"——实测 package.json L5-10 的 scripts 只有 dev/build/start/lint 四个，**没有 test**。表格与现实的这个缺口被括号注释提前对冲了。
- **包管理器口径**：README 本地运行用 pnpm（L43/L47），与 package.json L26 的 `packageManager: pnpm@9.15.1` 一致；根 AGENTS.md 则用 npm 泛称并在 L10 括号里兼容 "or pnpm dev, yarn dev, etc."——两文件写于不同手的痕迹。

## 数据流（标准如何被消费）

AGENTS.md 标准的"运行时"不在本仓，而在**消费方工具**的实现里，但本仓官网给出了语义基准（跨文件汇编）：

1. **格式自由**：FAQSection L15 "AGENTS.md is just standard Markdown. Use any headings you like"——没有必需字段、没有 schema，agent 直接解析文本。
2. **就近优先**：子目录可再放 AGENTS.md，"agents automatically read the nearest file in the directory tree, so the closest one takes precedence"（HowToUseSection L38，顺带给出规模注脚：当时 OpenAI 主仓有 88 个 AGENTS.md 文件）；FAQ L20 补上冲突规则——离编辑文件最近的赢，用户聊天里的显式指令覆盖一切。
3. **执行性**：写进 AGENTS.md 的测试命令会被 agent 自动执行并在完工前修复失败项（FAQ L23-25）。
4. **迁移与工具接入**：FAQ L36-44 给出 `mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md` 软链兼容方案，L57-62（Aider 配 `.aider.conf.yml` 的 `read: AGENTS.md`）与 L75-85（Gemini CLI 的 `.gemini/settings.json` context.fileName）给出两家工具的接入样例。

这条"规范即惯例"的路线与 A2A 式的 proto 真相源路线形成鲜明对照：AGENTS.md 的规范性由 23 家工具（CompatibilitySection L14-142 名单）的事实采纳来背书，而非由规范文档强制。

## 设计决策

1. **规范定义放 README 而非独立 SPEC 文档**——50 行装下定义+示例+建站说明，刻意维持"这个标准小到不需要规范文档"的姿态。这与格式哲学自洽：AGENTS.md 本身就是"约定优于配置"（任何 Markdown 都合法），官网若搞出几百行 normative spec 反而自我矛盾。代价是边界语义（就近优先、冲突裁决）散落在官网 FAQ/Hero/HowToUse 的 JSX 里，README 只字未提——想完整理解标准必须读网站源码或看渲染后的页面。
2. **最小示例选 monorepo 场景**——样例瞄准的是 AI agent 最容易翻车的真实工程场景（多包工作区里跑错目录、漏跑 lint），而非 hello world。这也是 OpenAI 主仓实践（88 个文件）的蒸馏。
3. **根 AGENTS.md 把"禁跑 build"放在第一节第一条**——教训型排序：agent 会话里跑 build 破坏 HMR 是协作中最高频的实际事故，规范条目按事故代价而非逻辑分类排序。这一条同时暴露了写作者视角：它是写给 Codex CLI 这类**长驻交互式 agent** 的，与一次性 CI 任务的指令文件需求不同。
4. **README 不放 60k 数字**——规模声明集中在网站（Hero/meta/Examples），README 保持极简。推断：数字会过时，静态 README 改起来不如网站文案勤（建站文案与 GitHub code search 链接 Hero L25 实时查询结果联动，README 则不做此承诺）。

## 新人提示

1. **找"AGENTS.md 是什么"的定义，入口是 README L5-33，不是根 AGENTS.md**——后者读完你只会知道怎么给这个网站提 PR。这是本仓文件命名的最大陷阱，也是讲解本仓时必须首先澄清的勘误。
2. **想给标准提意见**：改 README 的定义/示例（L5-33）+ 同步改 CodeExample.tsx L34-61 的镜像常量 + 视情况更新 FAQ/Hero 文案——标准文本在这三处之间没有任何单一真相源。
3. **给本仓提代码**：先读根 AGENTS.md——尤其别在 agent 会话里跑 `pnpm build`（L12-13 的禁令），本地验证一律 `pnpm dev`；改依赖后记得 `pnpm install` 刷 lockfile 并重启 dev server（L17-22）。
4. **别在 README 里找 API/Schema**——这个标准没有。评估某工具是否"支持 AGENTS.md"，看 CompatibilitySection L14-142 名单里它的链接指向的是产品页还是规则配置文档（如 Aider L49 直指 conventions 页锚点），粒度参差是常态。
5. **AGENTS.md L36 的 `npm run test` 跑不了**——scripts 里没有 test（package.json L5-10 实证）；表格是通用模板而非本仓事实，括号 "(if present)" 是作者留下的免责。

---

> 非空白字符 4798 / 锚 59
