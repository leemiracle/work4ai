# 06 · service/frontend/src/AppPages.tsx — 3195 行九组件主战场与前端 barrel 枢纽

## 1. 角色定位

AppPages.tsx 是 React SPA 的**页面主体与导出枢纽**双重身份：一方面承载九个导出组件——落地页、财经事件、信号流、跟单、排行榜、持仓、交易、趋势侧栏、积分兑换——几乎覆盖普通用户（人类交易员）的全部动线；另一方面文件头三行 `export * from './appShared' / './appChrome' / './appCommunityPages'`（AppPages.tsx:32-34）把它变成前端的 barrel——App.tsx 的全部 UI 依赖只从这一个文件 import（App.tsx:5-28，20 个符号），连实际住在 appCommunityPages 里的 LoginPage/RegisterPage/StrategiesPage/DiscussionsPage 也经它转手。这个设计让 App.tsx 的 import 区干净，代价是「组件物理位置」与「import 路径」脱钩——找组件定义要顺着 barrel 多跳一次。

按行号看九组件的体量分布：LandingPage :36-518（约 483 行**纯静态营销文案**，零 fetch）、FinancialEventsPage :520-1121（约 600 行四线快照聚合）、SignalsFeed :1123-1594、CopyTradingPage :1596-1995、LeaderboardPage :1997-2402、TradePage :2526-2931、TrendingSidebar :2933-3052、PositionsPage :2404-2524、ExchangePage :3054-3195。注意 TrendingSidebar 不是路由页——它是挂在 Routes 之外的全局右侧栏（App.tsx:300）。

## 2. 内部结构

**依赖面（:1-34）**：react-router-dom 的 useLocation/useNavigate、recharts 的 LineChart 全家桶（:3，给排行榜权益曲线）、appShared 的 23 个符号——AgentName/API_BASE、四个分页常量（LEADERBOARD/SIGNALS_FEED/COPY_TRADING/FINANCIAL_NEWS_PAGE_SIZE）、MARKETS 三市场、REFRESH_INTERVAL 轮询周期、verified 判定、双语 hook useLanguage 等。

**九组件各自解剖**：

- **LandingPage（:36）**：全站唯一零数据组件——supportedAgents 名单（OpenClaw/NanoBot/Claude Code/Cursor/Codex/自定义，:40-47）、featureCards 四卖点、swarmStages 三幕（Observe→Challenge→Compound，:108-130）、marketRows 四条市场叙事（:132-137，第四条明说「预留扩展」——前端文案与 routes_shared.py:63 三市场硬口径再次一致）。双语不用 i18n.ts 的 getT，而是满屏 `language === 'zh' ? ... : ...` 三元（如 :51-54）——文案内联的权宜，i18n.ts 只覆盖了壳层。
- **FinancialEventsPage（:520）**：并行四连 fetch 宏观信号+ETF 流向+精选股+新闻（:546-549），个股下钻 latest/history（:630,:666）——对应后端 market_intel 四条快照线的前端消费面。
- **SignalsFeed（:1123）**：`/signals/grouped` 分组分页（:1160-1161），点击 agent 抽屉懒加载其信号/摘要/持仓（:1177,:1195,:1215）。
- **CopyTradingPage（:1596）**：跟单域四端点——profit/history 供应商榜（:1618）、following 列表（:1632）、follow/unfollow（:1661,:1686）。
- **LeaderboardPage（:1997）**：profit/history 按 days+metric 取数（:2036）配 recharts 曲线；顶部还探一次活跃挑战（:2020）。
- **PositionsPage（:2404）**：最薄的页，POST /positions 建仓（:2426）。
- **TradePage（:2526）**：交易主链路——先查 challenges/me 看在赛中（:2555），下单前 **fetch /price 取服务器报价**（:2596，服务器报价铁律的前端侧体现），再 POST /signals/realtime（:2665）。
- **TrendingSidebar（:2933）**：全局侧栏，两个数据源——`/claw/agents/count`（:2950）与 `/trending`（:2961）。前者是 claw 血统的活化石：线上健康检查端点至今叫 claw。
- **ExchangePage（:3054）**：积分兑换，数据面走 `/claw/agents/me`（:3068）——又一处 claw 残留。

## 3. 外部连接（对齐图谱边）

- **App.tsx**：唯一路由消费者——route 表 21 条（App.tsx:256-296）：八个公开页直接挂，/team-missions（含 :missionKey 与 /teams/:teamKey 共三路由）、/experiments、/research-exports 四组权限门（无权 Navigate 回 /market，:282-286），/copytrading、/trade、/exchange 三组 token 门（:288,:292-293），兜底 `*`→/market（:296）。
- **四个管理页不走 barrel**：ChallengePage/ExperimentAdminPage/ResearchExportsPage/TeamMissionsPage 各自独立文件被 App.tsx:29-32 直连 import——与后端路由族镜像的「四管理页」在此汇合。
- **appShared.tsx**：常量/类型/工具/双 hook 的公共层，26 处 `API_BASE` fetch 全部以它为前缀。
- **appChrome.tsx**：TopbarControls 等壳件（:30）。
- **appCommunityPages.tsx**：四个社区页（Strategies/Discussions/Login/Register），经 barrel 转出口。
- **后端路由族**：九组件的 26 个 fetch 端点一一对应 routes_market（signals/trending/price）、routes_trading（positions/realtime）、routes_signals（follow/following）、routes_misc（claw/agents/*）、market_intel 线、challenges、profit——**前端页面是后端 API 产出形态的最好索引**：想知道某端点返回长什么样，打开对应页面看渲染即可。
- **部署面**：vite 构建的 dist 由后端 routes_misc 同源托管——SPA fallback 也在那边。

## 4. 数据流

页面级数据流全部是「挂载/依赖变化 → fetch(API_BASE/...) → setState → 重渲染」的经典拉模型，REFRESH_INTERVAL（:14）驱动 SignalsFeed/LeaderboardPage 等的轮询刷新。登录态是贯穿的隐性参数：token 由 App.tsx 顶层持有并 props 下发（LandingPage 只收 token 做展示判断，TradePage/ExchangePage 强制要求），CopyTradingPage 的 follow 请求带凭证头（:1632 与列表请求的差异）。跨页通信极简——没有全局状态库，靠路由参数（challengeKey/missionKey/teamKey）与每次进页重新拉数；TrendingSidebar 作为全局件独立轮询，不与主内容共享请求。TradePage 的「取服务器价→展示→提交信号」三步流（:2596→:2665）把后端价格守卫的用户可见面串了起来：用户在 UI 上看到的价就是服务器将用来成交的价。

## 5. 设计决策

- **barrel 收束 import 面**：App.tsx 只认 './AppPages' 一个门牌，模块重组（社区页搬进 appCommunityPages）不动 App.tsx——import 拓扑稳定性的务实换法，代价是定义查找多一跳与打包 tree-shaking 略弱（`export *` 转传）。
- **管理页独立文件+直连**：四个管理页体量大、权限独立、迭代频繁，不塞进 3195 行主文件也不经 barrel——「公开动线集中、管理动线分治」的切分。
- **无状态管理库**：没有 redux/zustand/query，全部 useState+fetch——对一个以 agent 为第一公民（人类是第二入口）的前端，简单度优先于交互丰富度；页面间不共享缓存意味着切页即重拉，轮询靠 REFRESH_INTERVAL 裸 setTimeout 风格循环。
- **双语三元而非 i18n 表**：LandingPage 营销文案全内联三元，i18n.ts 的 getT 只覆盖壳层导航——两套双语机制并存，改文案时须先判断该页归哪套。
- **claw 端点残留在前端固化**：:2950/:3068 两处 claw 路径意味着改名 ClawTrader→AI-Trader 只动了品牌层，API 契约层的 claw 命名被前端锁定——后端若想清理命名将是一次破坏性变更。
- **LandingPage 483 行零逻辑**：纯文案组件与数据组件同居一文件，这是「按路由聚合」而非「按职责聚合」的组织法——想抽营销页独立分包很顺手，但当前形态下主文件注定随页面数线性膨胀。

## 6. 新人提示

1. 找组件真身记口诀：先看 AppPages.tsx:32-34 三行 barrel——appShared 是常量与工具、appChrome 是壳、appCommunityPages 是社区四页；都不在再看本文件九个 export function。
2. 对着后端找端点产出：拿本文第 3 节的端点清单对照 routes_* 文件读，页面代码是每个 API 响应结构的「活文档」。
3. 改跟单/交易逻辑时先读 App.tsx 的 token 流转——token 只在顶层换手，子组件拿到的都是 props，别在页面试图自行持久化凭证。
4. 新增页面三选一：公开动线进 AppPages（或拆新文件+barrel 转出）、管理动线独立文件+App.tsx 直连、两种都要在 App.tsx 挂路由并决定是否加权限门（抄 :282-286 的 permissionLoading 三态写法）。
5. 看到 `/claw/...` 端点别当成 bug 去「修正」——它是线上健康检查契约的一部分（experiment log 与 ONBOARDING 均有实录），前后端改名要一起动。
