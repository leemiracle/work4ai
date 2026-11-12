# 精讲：components/CodeExample.tsx —— 伪 Markdown 高亮代码块与复制交互（含两处死代码勘误）

> 区域：`components/CodeExample.tsx`（207 行，全仓第二大组件）。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read/Grep 从源文件核实（2026-11-01）。

## 角色定位

全站的"代码展示原语"：渲染一段 AGENTS.md 样例文本，做轻量 Markdown 视觉强化（标题加粗、行内代码块底色），右上角挂一枚复制按钮。它是被复用次数最多的组件——**5 个调用点横跨 3 个区块**：Hero 右栏（首屏示例，Hero.tsx L61-66）、ExamplesSection 宽版样例（ExamplesSection.tsx L15）、FAQ 里三条命令行速记（FAQSection.tsx L39-44 的 `mv ... && ln -s ...`、L57-62 的 `read: AGENTS.md`、L75-85 的 Gemini JSON 配置）。它还持有两份 AGENTS.md 样例文案常量：`HERO_AGENTS_MD`（L22-32，导出给 Hero）与默认值 `EXAMPLE_AGENTS_MD`（L34-61，即 README 最小示例的镜像拷贝）。同时它是本仓死代码勘误的双料现场——死 import 与死 prop 各一处。

## 内部结构

四层结构，自上而下：

**① Props 契约（L5-20）**：五参全可选——`code`（L7，缺省回落 EXAMPLE_AGENTS_MD）、`href`（L9，注释承诺 "Optional URL for View on GitHub link"）、`compact`（L11，true 则去掉 section 灰底包装只留代码块）、`heightClass`（L13，覆盖默认高度类）、`centerVertically`（L15-19，单行命令在矮容器里垂直居中，注释点名 FAQ 场景）。

**② 两份文案常量（L22-61）**：`HERO_AGENTS_MD`（L22-32）是 10 行的迷你样例（Setup commands / Code style 两节）；`EXAMPLE_AGENTS_MD`（L34-61）是 pnpm monorepo 完整样例——与 README.md L12-33 **逐字同文**（差异仅是源码里的反斜杠续行折行）。两份样例 + README 那份 = 同一标准示例的三处手工维护。

**③ 伪高亮渲染器（L66-121）**：`parseMarkdown`（L66-101）按行分派——行首 `# `/`## `/`### ` 判标题套 `font-bold`（L74-79）；`- ` 判列表项（L80-86）；空行渲染 `&nbsp;` 占位（L87-89）；其余原样（L90-97）。每行再过 `renderLineWithInlineCode`（L106-121）：用捕获组正则 `` /(`[^`]+`)/g `` 按反引号段切分（L107），命中段套 `bg-gray-200 dark:bg-gray-800 px-1 rounded`（L113）。L63-64 注释自评准确："Very lightly highlight the Markdown without fully parsing it"——不解析语法树，不做列表缩进/链接/多级标题差异化，只认行首标记与行内反引号两种 pattern。

**④ 主组件（L126-207）**：`md = code ?? EXAMPLE_AGENTS_MD`（L133）；`copied` 布尔 state（L134）；`copyToClipboard`（L136-144）三步——`navigator.clipboard.writeText(md)`（L138）→ `setCopied(true)` + 2000ms 后自动复位（L139-140）→ catch 里只 console.error 不打断 UI（L141-143）。JSX 两侧：按钮（L149-173）绝对定位右上（`absolute right-3`，centerVertically 时改 `top-1/2 -translate-y-1/2` 垂直居中，L151-153），`aria-label="Copy to clipboard"`（L154）；`copied` 为真渲染内联 SVG 对勾（L156-169，path `M5 13l4 4L19 7`），否则渲染 `CopyIcon`（L171）。`<pre>`（L174-188）双主题底色 + 高度类三级决策（L178-183）：显式 `heightClass` > `compact`（不设高）> 默认 `min-h-[250px] max-h-[500px]`。外壳按 `compact` 分流：true 裸 div（L193-195），false 套灰底 section + `h2 "AGENTS.md in action"`（L197-206）——后者全站无人使用（5 个调用点全部 compact），又是一处休眠分支。

## 外部连接

- **上游 5 个调用点**：Hero.tsx L61-66（`compact + heightClass="min-h-[160px] max-h-[300px]" + code={HERO_AGENTS_MD} + href`）、ExamplesSection.tsx L15（仅 `compact`）、FAQSection L39-44 / L57-62 / L75-85（`compact + heightClass="min-h-[48px]" + centerVertically + code` 单行命令）。FAQ 三处把 `centerVertically` 的设计意图用满。
- **icons 依赖**：`CopyIcon`（L3 导入、L171 消费，15 行手写双框复制图标）；`ClipboardIcon`（L2 导入、**零消费**，见勘误 1）。
- **README 镜像关系**：L34-61 ↔ README.md L12-33 同文双份（02 篇详述）。
- **全局样式**：globals.css L102-111 的 `pre { white-space: pre-wrap; word-break: break-word }` 作用于本组件的 `<pre>`——代码块换行而非横向滚动（该 CSS 与 L175 的 `overflow-x-auto` 的层叠关系见 06 篇）。

## 交互流

用户点击复制按钮的一次完整链路：

```
点击（L150 onClick）→ copyToClipboard（L136）
 → navigator.clipboard.writeText(md)（L138，Clipboard API，需 secure context——
   agents.md 走 https 无碍；http 环境会 reject）
 → setCopied(true)：按钮图标 CopyIcon → 内联对勾 SVG（L156-169 切换）
 → setTimeout 2000ms（L140）→ setCopied(false) 图标弹回
 失败路径：writeText reject → catch（L141-143）console.error，按钮保持原样，页面无感知
```

一个已知小瑕疵：L140 的定时器没有在组件卸载时清理（无 useEffect cleanup）——若用户点完复制 2 秒内翻页卸载组件，会对已卸载组件 `setCopied`。React 18 起这不再触发警告也无实际泄漏危害，属可容忍粗糙。

## 设计决策

1. **伪高亮 vs 引入 Markdown 渲染器**——react-markdown + remark 一个依赖就能真渲染，但样例文案本身就是"给 agent 看的纯文本 Markdown"，**源码形态即展示形态**（用户要复制的正是带 `#` 和反引号的原文）恰恰是卖点；真渲染反而让用户拿到的是渲染后的富文本语义。56 行手写 parse（L66-121）换来零依赖与"所见即所抄"，是对场景的精准判断。
2. **复制的是 `md` 原文而非 DOM 文本**（L138）——直接写剪贴板源字符串，绕过 `innerText` 提取的空白/换行失真问题。
3. **2000ms 自动复位而非等下次 hover**——对勾反馈要短暂到不打扰（复制是高频小动作），2 秒是"看见了对勾但不会误以为按钮永久变了"的经验值。
4. **高度类三级决策**（L178-183）让同一组件适配三种容器：Hero 中等高（调用方给 heightClass）、默认大块（250-500px）、FAQ 单行矮条（48px + 垂直居中）——用 props 分层而非派生组件，保持了单一原语。

## 新人提示

1. **勘误 1（任务书给定，已实证）：L2 的 `ClipboardIcon` 是死 import**。grep 全文件 `ClipboardIcon` 仅 L2 一处（声明即终点）：复制态用的是 L156-169 的内联 SVG 对勾、待复制态用的是 L171 的 `CopyIcon`。注意**文件本身不死**——`components/icons/ClipboardIcon.tsx` 由 WhySection.tsx L29 正常消费；死的只是 CodeExample 这行 import（推断为复制按钮早期用 ClipboardIcon、改版成 CopyIcon+对勾后忘删）。安全删法：直接删 L2，无任何引用链受影响。
2. **勘误 2（本轮新发现）：`href` 是死 prop**。接口声明 L9 + 解构 L128 之外，组件体内**零渲染**——没有 "View on GitHub" 链接存在于任何 JSX。唯一传参方 Hero.tsx L65 传的 `href="https://github.com/openai/codex/blob/main/AGENTS.md"` 被静默丢弃（grep 实证：`href` 在本文件仅 L9/L128 两处）。考古推断：早期版本代码块带 GitHub 跳转按钮，后移除，props 残留。处理建议二选一：删 L9/L128 与 Hero L65 的传参；或把 L9 注释承诺的链接真正渲染出来。
3. **改默认样例文案要动两处**：本文件 L34-61 与 README.md L12-33（同文双份）；若 Hero 的迷你样例也要改，则是第三处（L22-32）。三处零同步机制。
4. **`compact` 分支之外还有个休眠分支**：非 compact 的 L197-206（灰底 section + "AGENTS.md in action" 标题）当前无人触发——5 个调用点全 compact。新调用方若想要独立成块的代码示例（带标题），这正是现成开关，别急着重构删掉。
5. **剪贴板 API 的环境约束**：`navigator.clipboard` 只在 secure context（https 或 localhost）可用——本地 `pnpm dev` 没问题，但如果把静态产物挂到裸 http 域名下，复制按钮会静默失败（catch 只 console.error）。排查"复制没反应"先看协议。
6. **给 FAQ 式单行命令加新条目**：照 FAQSection L57-62 的配方——`code` 传命令字符串、`compact`、`heightClass="min-h-[48px]"`、`centerVertically` 四件套，长命令无需换行处理（globals.css 的 pre-wrap 全局接管）。

---

> 非空白字符 4653 / 锚 86
