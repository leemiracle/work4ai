# 精讲：components/CompatibilitySection.tsx —— 23 工具兼容墙：跑马灯/网格双视图的数据组织

> 区域：`components/CompatibilitySection.tsx`（378 行，全仓最大文件）。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read/Grep 从源文件核实（2026-11-01）。

## 角色定位

这是官网叙事的第三屏"信任背书"区块——用一份不断增长的 AI 编码工具名单证明"One AGENTS.md works across many agents"（L330 的 Section 标题）。它是全仓最大的组件（378 行，比第二名 CodeExample 的 207 行多出 83%），大在两处：一是内嵌了整个生态的数据表（L14-142 的 `agents` 数组，本仓唯一的"数据库"）；二是把同一份数据渲染成**两种视图**——默认的双行无缝跑马灯（自动滚动展示）与点击展开的静态网格（逐个可读），外加一套视口感知的动画节能与暗色适配的 logo 染色方案。除了 Section 原语与 next/image，它零依赖实现了这些。

**条目数勘误**：任务书与本仓 DeepWiki 快照口径为"24 工具"，实测 `agents` 数组为 **23 条**（`grep -c '    name: "'` 逐条计数实证；配合 logos 对账 27 个引用文件全部存在）。对外引用请以 23 为准。

## 内部结构

按依赖方向自底向上四层：

**① 数据层（L5-142）**：`AgentEntry` 类型（L5-12）五个字段——`name`/`url` 必填，`from`（出品方）与三种 logo 路径可选。`agents` 数组 23 条硬编码，按三种 logo 策略分型：

| 策略 | 条目 | 代表锚点 | 渲染路径 |
|---|---|---|---|
| 单图 CSS mask | 19 条 | Codex（L15-20）、Aider（L47-51）、Junie（L136-141） | `imageSrc` → mask 染色（L196-211） |
| 明暗双图 | 4 条 | VS Code（L100-104）、Ona（L105-110）、Devin（L111-117）、Windsurf（L118-124） | `imageSrcLight`+`imageSrcDark` → dark:hidden/dark:block 切换（L179-195） |
| 无图 | 0 条 | ——类型允许（`imageSrc?`），实际全数带图 | L211 的 `: null` 兜底永不触发 |

`from` 字段标注出品方共 7 家：OpenAI（L18）、Google（L28 Jules、L55 Gemini CLI）、GitHub Copilot（L95）、Cognition（L113 Devin、L120 Windsurf）、UiPath（L127）、JetBrains（L138）。url 粒度不齐——有的指向产品首页（Cursor L34），有的直抵规则配置文档锚点（Aider L49 的 `#always-load-conventions`、Warp L90 的 `#project-scoped-rules-1`），后者才是"该工具如何消费 AGENTS.md"的证据链接。

**② 渲染原子 LogoItem（L153-226）**：按 `variant` 分形（L166-169）——grid 态 `h-full w-full min-w-0`（自适应卡片），marquee 态 `h-20 min-w-[280px] pr-10`（固定最小宽保证跑马灯节奏）。双图分支（L179-195）两个 next/image 以 `dark:hidden`（L186）/`dark:block`（L193）二选一显示；单图分支（L196-211）是**CSS mask 染色技巧**：`<span>` 铺底色 `bg-gray-700 dark:bg-gray-400`（L199），SVG 仅作 `maskImage`（L201-209 九个前缀属性），logo 形状由 mask 的 alpha 决定、颜色由底色决定——一张单色 SVG 无需暗色变体文件即可适配双主题。文字侧 name 加 `from` 小字（L213-222，`from` 用 font-light 与名字区分）。

**③ 跑马灯行 LogoMarqueeRow（L228-263）**：`doubledAgents = [...agents, ...agents]`（L239）把序列翻倍——配合 CSS `translateX(-50%)`（globals.css L124）实现首尾无缝循环（一半宽度恰好等于一轮内容）。行内样式三元组（L245-249）：`animationPlayState` 由 `isActive` 控制启停（L246）、`animationDelay` 取负 `offset` 错相（L247）、`--marquee-duration` 自定义属性传速度（L248，globals.css L115 以 `var(--marquee-duration, 70s)` 消费）。空数组防御性返回 null（L241-243）。列表 key 用 `${agent.name}-${index}`（L258）——翻倍导致同名条目出现两次，必须带 index 消歧。

**④ 主组件（L265-378）**：状态四件套——containerRef（L266）、isInView（L267）、shuffledAgents（L268，初始值即原数组）、showGrid（L269）。两个 effect + 两个 useMemo + 双视图 JSX，见"交互流"。

## 外部连接

- **globals.css 动画三件**：`.logo-marquee-track` 类（L113-117：`width: max-content` 让轨道宽度由内容撑开、`animation` 引用自定义属性、`will-change: transform` 提升到合成层）；`@keyframes logo-marquee-scroll`（L119-126，0 → -50%）；`prefers-reduced-motion` 下整段动画关闭（L128-132，前庭无障碍）。
- **Section 原语**：本组件是 Section 消费方中最特殊的一个（L328-334）——跑马灯要全幅出血，于是 `className` 传 `!px-0`（L331，Tailwind important 修饰符）强行压掉 Section 内建的 `px-6`（Section.tsx L29），同时 `maxWidthClass` 随视图切换：网格态 `max-w-3xl`、跑马灯态 `max-w-none`（L333）。
- **public/logos/ 静态资产**：27 个 SVG 与 23 条目一一对账全存在（19 单图 + 4×2 双图 = 27），无缺失无冗余。
- **id 协作**：`id="compatibility"`（L329）供页内锚点；`id="supported-agents"`（L343 网格态 / L354 跑马灯态）供切换按钮的 `aria-controls`（L370）指向——同一 id 出现在两个互斥分支里，任一时刻只渲染一个，DOM 合法。

## 交互流

组件挂载后的完整行为链：

```
首帧（SSR/hydration）：按 agents 声明序渲染 → 保证服务端与客户端 HTML 一致
 └─ effect①（L271-273）：setShuffledAgents(shuffleAgents(agents)) —— Fisher-Yates 洗牌
     （shuffleAgents L144-151：倒序遍历+随机交换，不修改原数组）
 └─ effect②（L275-310，依赖 showGrid）：
     ├─ showGrid=true → setIsInView(false) 停表并跳过监听（L276-279）
     └─ 否则挂 IntersectionObserver（L286-293，threshold 0）
         + getBoundingClientRect 立即判定一次（L297-305，弥补 observer 回调异步性：
           首屏内组件不等首个回调即启动动画）
 └─ 洗牌后 useMemo（L312-325）按奇偶分两行：index%2===0 → topRow，其余 → bottomRow
 └─ 渲染：
     ├─ 跑马灯态（L350-363）：topRow 70s（L356）+ bottomRow 80s 且 offset=-35s（L357-362，
     │   负延迟让第二行从动画中段切入，两行错相不同速）
     └─ 点击按钮（L366-374）→ setShowGrid 取反（L368）→ 网格态按**原始声明序**平铺 23 条
         （L346 用 agents 而非 shuffledAgents——网格是查阅视图，稳定性优先于随机性）
```

`isActive`（即 isInView）控制 `animationPlayState: paused/running`（L246）——滚出视口的跑马灯停止动画，节约主线程与电量；这是纯 CSS 动画做不到、React 状态 + IntersectionObserver 的标准配合。

## 设计决策

1. **洗牌放在 effect 而非渲染期**——若在渲染函数里直接 `Math.random()`，SSR 生成的 HTML 与客户端首次渲染就会不一致（hydration mismatch 报错）。首帧用原序、挂载后洗牌重渲，是"随机化 UI"的教科书解法；副作用是用户可能看到一瞬间的顺序跳变，两行奇偶分配（L312-325）又保证任意洗牌结果都均匀铺满两行。
2. **两套 logo 策略并存而非统一**——mask 染色（单色 logo，灰阶随主题反转）成本最低但会抹掉品牌色，于是 4 个有强品牌色/复杂图形的工具（VS Code、Devin、Windsurf、Ona）走双文件切换。判断标准隐含在资产端：官方提供了彩色版就值得两个 SVG。
3. **网格视图不洗牌**（L346）——跑马灯的随机序是"生态平等展示"的姿态（避免声明顺序暗示排名），网格是"我要找某个工具"的查阅场景，回归声明序便于与源码数组对照维护。同一数据两种视图两种秩序，是有意识的分化。
4. **动画节能双层**——`animationPlayState` 视口暂停（JS 层）+ `prefers-reduced-motion` 整体关闭（CSS 层 globals.css L128-132）+ `will-change: transform`（合成层提升，L116），三层分别服务电量、无障碍、流畅度。
5. **无缝循环用序列翻倍而非 JS 克隆位移**——`[...agents, ...agents]`（L239）+ `-50%` 位移是纯 CSS 循环跑马灯的最小实现，无需 requestAnimationFrame 或 JS 计时器；代价是 DOM 节点翻倍（23→46 个 LogoItem/行），对静态链接卡片可忽略。

## 新人提示

1. **新增一个兼容工具只需改一处**：在 L14-142 数组按现有模式加一条（name/url 必填；单色 logo 放 `public/logos/` 后只填 `imageSrc`；有品牌色则备 light/dark 两份填双字段），再把 SVG 放进 public/logos/。跑马灯、网格、奇偶分行、洗牌全部自动生效。
2. **条目计数口径统一说 23**——"24 工具"的说法（含部分文档快照）与数组实测不符；做对账或写文档时用 `grep -c '    name: "' components/CompatibilitySection.tsx` 现场复核。
3. **调跑马灯速度/错相**：速度改 L356/L360 的 `duration`（秒），错相量改 L361 的 `offset`——CSS 侧的 `--marquee-duration` 只是消费方（globals.css L115），不要去 CSS 里改默认值 70s（那是兜底而非常规路径）。
4. **给 logo 换色**：mask 方案的"颜色"其实是 L199 的底色类——改 `bg-gray-700 dark:bg-gray-400` 即全局换色，无需动 SVG；如果某工具 logo 必须显彩色，照 VS Code 条目（L100-104）补双图。
5. **坑：`!px-0` 依赖 Tailwind important 语法**——这行（L331）压的是 Section 原语的 `px-6`（Section.tsx L29）。若重构 Section 的 padding 实现方式（比如移进 containerClasses），这里的 important 覆盖可能静默失效，跑马灯会突然出现左右留白——改 Section 前先搜消费方的 `!` 前缀用法。
6. **坑：key 必须带 index**（L258）——序列翻倍后同名条目重复出现，去掉 index 会触发 React 重复 key 警告并引发错误复用。

---

> 非空白字符 5252 / 锚 89
