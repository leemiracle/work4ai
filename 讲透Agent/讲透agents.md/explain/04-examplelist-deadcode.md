# 精讲：components/ExampleListSection.tsx —— 案例卡片网格与三处准死代码的甄别

> 区域：`components/ExampleListSection.tsx`（188 行）。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read/Grep 从源文件核实（2026-11-01）。

## 角色定位

官网 Examples 区块的下半段：把 4 个真实开源仓库渲染成"谁在用 AGENTS.md"的卡片墙，每张卡片带 GitHub 语言色徽章、top3 贡献者头像串（数据来自 index.tsx 构建期注入的 `contributorsByRepo`，01 篇）与贡献者计数，点击直达该仓库的 AGENTS.md 文件。它是全仓**死代码密度最高**的文件——188 行里有一个整分支、一个恒假 prop、一条断头样式链处于不可达或失效状态；同时它还是跨文件手工同步耦合（index.tsx 的 `repoNames` ↔ 本文件 `REPOS`）的一端。讲透它等于做一次小型代码考古。

## 内部结构

自上而下四段：

**① 语言色表（L4-10）**：`LANG_BG_COLORS` 五键——TypeScript `#3178c6`、Java `#b07219`、Python `#3572a5`、Rust `#dea584`、C++ `#f34b7d`，取自 GitHub linguist 官方语言色。查不到的语言走 `#6b7280` 灰兜底（L125）。

**② 数据与卡片 props（L12-45）**：`RepoCardProps`（L12-19）name/description/language 三字段；`REPOS` 常量（L22-45）硬编码 4 仓——`openai/codex`（Rust，L26）、`apache/airflow`（Python，L32）、`temporalio/sdk-java`（Java，L37）、`PlutoLang/Pluto`（C++，L43）。L21 注释自认性质："Hard-coded examples used for the marketing page"——营销页精选，非动态统计。

**③ InnerGrid（L52-83）**：响应式网格 `grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4`（L58）平铺 4 卡；L63-70 从 `contributorsByRepo[repo.name]` 取头像（`?? []` 兜底）与计数（三级回退 `?.total ?? ?.avatars.length ?? 0`）；L74-81 尾部居中一个外链——指向 GitHub code search 的实时查询 `path:AGENTS.md NOT is:fork NOT is:archived`（L76，URL 编码形态），文案 "View 60k+ examples on GitHub"（L79）。

**④ 双分支外壳（L85-105）+ ExampleCard（L115-186）**：外壳按 `standalone` 分流（详下）；卡片是 `<a>` 整卡可点（L128-139），链到 `https://github.com/${repo.name}/blob/-/AGENTS.md`（L129——用 `-` 占位 ref，GitHub 会重定向到默认分支）；`lg:aspect-video`（L132）让宽屏下卡片保持 16:9。卡内三块：标题+描述（L141-150，标题 truncate 防溢出）；底部左侧语言徽章（L153-158，inline style 背景色）；底部右侧头像串——有数据时 `avatars.slice(0, 3).reverse()`（L123）渲染 3 个 `<img>`（L164-169，带 L163 的 eslint-disable 注释豁免 next/image 规则），无数据时 `Array.from({ length: 3 })` 渲染 3 个灰色占位圆（L171-177）；计数徽章 `+ {totalContributors}`（L179-181）。L122 注释点破 reverse 的语义："ensure highest-ranked appears rightmost"——contributors API 按贡献降序返回，slice 后反转使第一名落到视觉最右（或理解为按贡献从左到右递增排列，与"+ N"计数自然衔接）。

## 外部连接

- **上游**：`ExamplesSection`（唯一调用方，ExamplesSection.tsx L19）透传 `contributorsByRepo` 并显式传 `standalone`；数据源头是 index.tsx 的 getStaticProps（L47-160）。
- **标题职责上移**：ExamplesSection 自带 `<Section title="Examples">`（ExamplesSection.tsx L12），同屏还先渲染了一个宽版代码块（L15）再渲染本组件——**这正是本文件死分支的成因**（见设计决策 1）。
- **下游外链**：GitHub blob 页（L129）与 code search（L76）；头像 `<img>` 直连 `avatars.githubusercontent.com`（运行时由浏览器加载，构建期只存 URL）。
- **手工同步对端**：index.tsx L48-49 注释 "Keep in sync with the REPOS constant in that component" + L50-55 的 `repoNames` 四仓——两个文件各持一份相同的仓库名单，无任何生成或校验机制。

## 数据流（构建期到像素）

```
构建期：getStaticProps 逐仓抓 contributors（index.tsx L96-145）
 → contributorsByRepo["openai/codex"] = { avatars: [url×3], total: 1234 }
运行时渲染链：
 index.tsx L24 → ExamplesSection L19（standalone=true）
 → 本组件 L89-95（裸 div 分支，无 section 无 h2）
 → InnerGrid L59 逐卡：repo.name 命中 contributorsByRepo → 头像/计数；
     未命中（两份名单失同步时）→ L63 ?? [] 灰圆占位、L67-69 ?? 0 计数为零
 → ExampleCard：徽章取 L4-10 语言色 → 头像 slice(0,3).reverse()（L123）→ 整卡 <a> 链到 blob/-/AGENTS.md（L129）
```

## 设计决策（含三处准死代码甄别）

1. **整分支不可达：非 standalone 分支（L97-104）**。唯一调用方 ExamplesSection.tsx L19 写死 `<ExampleListSection ... standalone />`（shorthand 即 `standalone={true}`），故 L89-95 的裸 div 分支恒走，**L97-104 的 `<section className="px-6 pb-12 -mt-36">` 与 L100 的 `<h2>Who uses AGENTS.md?</h2>` 永不渲染**。考古结论：该组件曾独立成区块（`-mt-36` 负 margin 是为钻进上方区块的视觉叠压，px-6/pb-12 自带边距），后来被收编进 ExamplesSection 的 Section 插槽，标题职责上移给 Section 的 `title="Examples"`，旧外壳成了化石。注意它不是 tree-shake 意义上的死代码——同文件内导出组件带着它进 bundle，只是运行时不可达；改 L100 文案永远看不到效果，是维护陷阱。
2. **恒假 prop：`hideOnSmall={key > 3}`（L64）**。REPOS 恰 4 条、索引 0-3，`key > 3` 永为 false → L133-134 的 `"hidden lg:flex"` 类永不施加。姊妹 prop `hideOnMedium={key > 2}`（L65）半活：index 3（Pluto）为 true → 走 L136 `"flex md:hidden lg:flex"`（小屏显示、md 三列时隐藏、lg 四列时回归）。这对手感明显的断点规则（第 5+ 卡小屏藏、第 4+ 卡中屏藏）是**卡片数 >4 时代的遗迹**——如今 4 卡布局下，hideOnSmall 纯死、hideOnMedium 只影响一张卡在 md 断点的显隐。若未来精简到只保留 4 卡，L64/L111/L133-134 与 L112/L65/L135-136 可整组评估删除。
3. **跨文件手工同步（无机制保障）**：index.tsx `repoNames`（L50-55）↔ 本文件 `REPOS`（L22-45）。失同步的症状是**静默降级**而非报错：新仓有卡片但头像三灰圆、计数 0（L63/L67-69 的 `??` 链接住）；旧仓残留则数据抓了没人用（构建期多两次 API 请求）。注释（index.tsx L48-49）是唯一防线。改进方向很直白：REPOS 从本文件 export，index import——但小仓选择了复制粘贴+注释，属于可接受的惰性权衡。
4. **头像三灰圆占位（L171-177）**而非条件隐藏——数据未到/失败时保持布局不跳（CLS 友好），也暗示"这里有信息，只是没加载"。
5. **整卡 `<a>` + `target="_blank" rel="noopener noreferrer"`（L130-131）**——卡片即链接的可达性模式（无嵌套交互元素），比"标题可点"宽容得多。

## 新人提示

1. **加第五个示例仓库的三步**：REPOS 加条目（L22-45）→ index.tsx `repoNames` 同步加（L50-55，漏了就灰圆零计数）→ 若语言不在 L4-10 表中补色键（不补则灰徽章）。此时 `key > 3` 的 hideOnSmall 会**复活**——第 5 张卡在小屏自动隐藏（L134），这是遗留断点规则的意外回魂，先想清楚要不要。
2. **想给卡片区加标题/h2**：别改本文件 L100（不渲染）——区块标题在 ExamplesSection.tsx L12 的 Section `title` prop；或者取消 L19 的 `standalone` 让旧分支复活（但 `-mt-36` 的叠压样式需要重新校准）。
3. **`blob/-/AGENTS.md`（L129）的 `-` 是 ref 占位符**，GitHub 收到无效 ref 会落到默认分支——好处是免维护分支名（main/master 之争），代价是链接多一跳重定向。
4. **验证死代码的快捷命令**：`grep -rn "ExampleListSection" --include="*.tsx" .` 只有 ExamplesSection 一个消费方；`grep -n "standalone" components/ExamplesSection.tsx` 确认无值 shorthand。做重构删除前先跑这两条，防止又有新调用方带着 `standalone={false}` 回来。
5. **别学这里的双名单模式**——新代码应单一导出源（REPOS export + index import）；本文件保留现状只因改动收益小于 touches。同理 L49 注释 `// if false wraps with its own section` 描述的语义是对的（false → 自带 section），但它描述的分支已不可达，读代码时别被它带偏以为两种模式都在用。

---

> 非空白字符 4747 / 锚 79
