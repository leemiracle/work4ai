# 精讲：pages/index.tsx —— 单页装配主线与 getStaticProps 的 GitHub 数据注入

> 区域：`pages/index.tsx`（160 行，全站唯一页面）。仓根：`/usr-data/data2/repos/aaif-projects/repos/agents.md`。本文所有行号锚均经 Read 从源文件核实（2026-11-01）。

## 角色定位

这是 AGENTS.md 官网（agents.md）的**整站入口**——Pages Router 下 `pages/index.tsx` 映射根路由 `/`，而本仓没有第二个 page 文件（`pages/` 目录仅 index/_app/_document 三件套），所以它就是"单页应用的全部路由层"。它做两件事：一是**装配**——把 8 个区块组件按营销叙事顺序串成一屏滚动页；二是**供数**——用 `getStaticProps` 在构建期向 GitHub REST API 抓 4 个示范仓库的贡献者头像与计数，喂给 ExamplesSection。整站唯一的动态数据来源、唯一的网络请求逻辑、唯一的 SSG 数据契约（`LandingPageProps`）都收在这个文件里；其余组件全部是纯静态展示件。

## 内部结构

160 行清晰地分成三段：

**装配段（L17-35）**：组件 `LandingPage` 接收 `contributorsByRepo`（L17），JSX 按 L21-32 顺序渲染 8 个顶级元素——`Hero`（L21，首屏双栏：左文案+CTA，右代码示例）→ `WhySection`（L22，为什么需要）→ `CompatibilitySection`（L23，23 个兼容工具跑马灯）→ `ExamplesSection`（L24，唯一接收 props 的区块，贡献者数据在此下传）→ `HowToUseSection`（L25，四步上手）→ 一个 `flex-1` 包裹 div（L26-29，内含 `AboutSection`+`FAQSection`，`mt-16` 拉开间距）→ `Footer`（L32，LF Projects 版权行）。注意 Hero 是 `<header>`、Footer 是 `<footer>`、中间 6 个区块才是 Section 语义组件——页面骨架即"6 个 Section 插槽 + 首尾语义标签"（L19-20 的 `min-h-screen items-stretch flex flex-col` 保证 Footer 沉底）。

**缓存声明段（L37-45）**：模块级变量 `cachedContributors`（L40-45）——`{ data, fetchedAt }` 形状，`fetchedAt` 存 epoch 毫秒（L43 注释）。L37-39 的注释写明双场景动机：生产环境避免 Node 进程生命周期内重复抓取，开发环境防刷页面撞 GitHub 匿名限额（60 req/hr）。这是**进程内存缓存**，不是 ISR 缓存——与下文的 `revalidate` 是两层东西。

**数据获取段（L47-160）**：`getStaticProps`（L47）逐仓串行抓取，细节见"数据流"。

## 外部连接

- **上游数据源**：GitHub REST API `api.github.com/repos/{fullName}/contributors`（L100、L116 两个端点变体），公共只读，无需登录。
- **下游消费者**：`contributorsByRepo` 只流向 `ExamplesSection`（L24）→ 再透传给 `ExampleListSection` 做头像与计数徽章。数据形状 `Record<string, { avatars: string[]; total: number }>`（L14）是横跨 index/ExamplesSection/ExampleListSection 三个文件的接口契约。
- **环境变量**：`GH_AUTH_TOKEN`（L92）可选——存在则加 `Authorization: Bearer`（L93）把限额从 60/hr 提到 5000/hr。L84-86 注释解释了为何条件添加：空 `Authorization` 头反而会被 GitHub 判为匿名请求。
- **请求头**：`User-Agent: agents-md-site`（L88）+ `Accept: application/vnd.github+json`（L89）。
- **手工同步耦合**：L48-49 注释自曝——`repoNames`（L50-55，4 仓）必须与 ExampleListSection 的 `REPOS` 常量手工保持同步（04 篇详述这个跨文件约定）。

## 数据流

构建期（`next build` 或 ISR 再生时）的一次完整取数：

```
getStaticProps 触发
 ├─ 12h 内存缓存判定（L63-66）：命中 → 直接返回缓存数据，revalidate: 3600（L74）
 └─ 未命中 → 逐仓串行循环（L96）：
     ├─ 请求① avatars：?per_page=3（L100）→ res.ok ? json : []（L106-108）
     │   → avatarsData.slice(0,3).map(c => c.avatar_url)（L110）
     ├─ 请求② count：?per_page=1&anon=1（L115）
     │   ├─ 读 Link 响应头（L122）→ /rel="last"/ 测试（L123）
     │   │   → 正则 /&?page=(\d+)>; rel="last"/ 提取页码（L124）→ parseInt 即总数（L126）
     │   └─ 无 last 链接（贡献者一页装完）→ 读 body 长度兜底（L129-130）
     ├─ 内层 catch：保留 fallback（L132-135）；外层 catch：{ avatars: [], total: 0 }（L141-144）
     └─ 写入 contributorsByRepo[fullName]（L137-140）
 → 写内存缓存（L147-150）→ 返回 props，revalidate: 86400（L158）
```

**Link header 页码技巧是这个文件最值得学的工程点**（L112-127）：GitHub contributors 端点不返回总数字段，代码用 `per_page=1` 请求并解析响应头 `Link: <...&page=2...>; rel="next", <...&page=87...>; rel="last"`——`rel="last"` 里的页码乘以 per_page(=1) 就是贡献者总数，一次请求拿到精确计数而无需拉全量列表。`anon=1`（L116）把匿名贡献者计入总数，与官网"贡献者"口径一致。两条正则分工：L123 的 `test` 先确认 last 链接存在，L124 的 `match` 再提取数字。

**三层降级链**保证页面永不因 GitHub 故障而构建失败：请求①失败 → 空头像数组（L106-108）；请求②失败 → `total` 回退为头像数组长度（L113，最多 3）；整仓失败 → 零值占位（L143）。这就是为什么线上偶发 GitHub 抖动时最多看到卡片头像变灰圈、计数为 0，而站点本身永远能构建出来。

## 设计决策

1. **SSG + 双层 TTL 而非 CSR**——贡献者数据只在构建期取（getStaticProps），浏览器端零 API 调用。`revalidate: 86400`（L158）让生产站每天后台再生一次；内存缓存 12h（L60）是叠加在其上的第二层。**一个微妙后果**：缓存命中分支返回的 `revalidate: 3600`（L74）形同虚设——ISR 每小时确实可能触发再生，但再生执行的还是这个 getStaticProps，撞上 12h 内存缓存就拿旧数据返回。真实数据新鲜度由 12h 决定，1h 的 revalidate 只是让 ISR 机制保持运转（L71-73 注释对此有自aware的说明）。
2. **模块级缓存解决的是开发体验**——dev 模式下每次刷新页面都可能重跑 getStaticProps（Pages Router dev 无 ISR 概念），没有这层缓存，几次刷新就烧光匿名限额。用模块变量而非更复杂的方案，代价是 dev server 重启缓存即失效（L156-157 注释自认"between dev server restarts"）。
3. **串行而非并行 fetch**（L96 的 for-await）——4 个仓库 8 个请求，串行最坏 ~8 个 RTT，构建期无感知；换并发只是徒增复杂度。这是"构建期代码可以为简单牺牲速度"的典型取舍。
4. **L129 的 `as any[]` 是全仓唯一一处 any 断言**——tsconfig 严格模式下，对"形状不确定的降级响应"作者选择局部 any 而非编一个精确接口，务实但不完美（同文件 L107 对称场景用了精确类型 `Array<{ avatar_url: string }>`）。

## 新人提示

1. **加一个区块的正确位置**：写新组件 → 在 L21-32 的 JSX 序列里按叙事位置插入。注意"6 Section + Hero + Footer"的格局——纯内容区块直接复用 `Section` 原语（06 篇），不要自带 `<section>` 包装。
2. **换展示仓库必须改两处**：`repoNames`（L50-55）与 `ExampleListSection.tsx` 的 `REPOS`（L22-45）。只改 index 这边 → 卡片能渲染但头像/计数全空（键查不到，走 L63/L67-69 的 `??` 回退）；只改组件那边 → 新仓有卡片但 contributorsByRepo 里没数据。L48-49 的注释就是这颗雷的警示牌。
3. **本地构建看到空头像不是 bug**：无 `GH_AUTH_TOKEN` 且匿名限额耗尽时，L141-144 的兜底就是 `{ avatars: [], total: 0 }`；等一小时或 export token 再跑。想强制刷新数据，重启 dev server 清掉模块缓存即可。
4. **别把这个文件当 SSR**——它是纯 SSG（getStaticProps），页面 HTML 构建期就已定死；数据更新依赖 ISR 后台再生（生产）或重启（开发）。改文案立刻可见，改贡献者数据要等再生窗口。
5. **Link header 解析的适用边界**：L124 的正则假设 GitHub 的 Link 头里 `rel="last"` 紧跟 URL 尖括号。这是 GitHub API 的稳定格式，但若换其他 API（如 GitLab），Link 头的 rel 顺序/引号风格可能不同，直接搬会静默失配——失配后果只是 total 退化为 1（L129-130 的单页长度），不会崩。

---

> 非空白字符 4322 / 锚 69
