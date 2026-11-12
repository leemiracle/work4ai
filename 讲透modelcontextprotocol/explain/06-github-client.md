# 06 · github/client.ts — sep-automation 的 GitHub API 封装

## 1. 角色定位

`tools/sep-automation/src/github/client.ts`（334 行）是 sep-automation 与 GitHub 之间的**唯一网络通道**。index.ts:69 `new GitHubClient(config)` 构造一次，随即注入五个组件：MaintainerResolver（index.ts:70）、SEPDetector（index.ts:71）、SEPAnalyzer（index.ts:72）、TransitionHandler（index.ts:73）、PingHandler（index.ts:74）。

为何独立封装：①**认证集中**——双认证只出现一次，上层无感；②**分页集中**——统一 paginate + `per_page: 100`；③**类型收窄**——Octokit 响应 `as` 断言为本仓五个只读接口（types.ts:5 / 19 / 27 / 35 / 40）。这也是 mocks.ts:15-26 能整体 mock 它的前提。

## 2. 内部结构

| 分区 | 行 | 内容 |
|---|---|---|
| 查询常量 | client.ts:12-15 | SEARCH_QUERIES 两个搜索串 |
| 构造器 | client.ts:24-40 | 双认证三分支 |
| 懒初始化 | client.ts:46-79 | App installation token 获取 |
| 读 API | client.ts:84-150 | search / label / comments / events |
| 写 API | client.ts:155-211 | comment / labels / close |
| 团队 API | client.ts:216-306 | membership / members / teams / 子团队递归 |
| 静态 getter | client.ts:324-333 | SEP 查询串暴露 |

**双认证策略**：构造器三分支——`appId && appPrivateKey` 优先（client.ts:30；L29 注释：App auth 有更好的 org 级权限）但只放占位实例（client.ts:32）；仅 `githubToken` 时立即认证并 `initialized = true`（client.ts:34-35）；都没有则占位（client.ts:38）。App 认证延迟到 `ensureInitialized()`（client.ts:46）：先用 appId+privateKey 建 app 级 Octokit（client.ts:51-57），`apps.getRepoInstallation`（client.ts:60-63）换 `installation.id`，再建带 installationId 的实例（client.ts:66-73）。每个公开方法第一句 `await this.ensureInitialized()`（client.ts:85/104/122），已初始化则直接返回（client.ts:47）。

**请求层与错误处理**：本文件**没有重试/退避层**——Octokit 默认不重试，限流直接抛出；错误处理只有一种模式：`isHttpError(error, 404)` 吞掉语义化 404（removeLabel 标签不存在 client.ts:193、isTeamMember 非成员 client.ts:228），其余 rethrow（client.ts:196/231）。isHttpError 本体 errors.ts:18-24，只比较 `.status`。

**分页**：列表方法统一 `per_page: 100`（client.ts:91/112/129/146/245/261），游标翻页由 Octokit 托管。searchIssues 特殊：搜索端点返回 `{total_count, items}` 包裹，需 mapFn 剥出 items（client.ts:95）。

**子团队递归 getAllDescendantTeams**（client.ts:272-306）：不逐层调 API，而是**一次拉全 org 团队列表、内存里走 parent 链**——listOrgTeams（client.ts:273；底层 teams.list 分页 client.ts:257-263）→ 建 slug→team Map（client.ts:276-279）→ 查根团队（client.ts:282），查不到则保守退化为只返回根 slug（client.ts:285）→ 每团队 `while (current?.parent)` 沿 parent 链上溯（client.ts:296-302），命中根 slug 即收集并 break（client.ts:297-299），否则 `current = teamBySlug.get(current.parent.slug)` 续溯（client.ts:301）。parent 定义在 types.ts:44（`{id, slug} | null`）。

## 3. 外部连接

imports（client.ts:5-9）：@octokit/rest（client.ts:5）与 @octokit/auth-app（client.ts:6，package.json:18-19）为 npm 包，图谱不建边只记 notes；建边的是仓内依赖 ../config.js（client.ts:7）、./types.js（client.ts:8）、../utils/index.js（client.ts:9）。

消费面（grep 实证）：detector.ts:26/29 searchIssues、detector.ts:44 getIssuesWithLabel、detector.ts:97 getIssue；analyzer.ts:28-29/169-170 getComments/getEvents；transition.ts:64/68/73 标签与评论；ping.ts:100/138/181/254/294 addComment、ping.ts:246/250 标签、ping.ts:258 closeIssue；resolver.ts:46 getAllDescendantTeams、resolver.ts:61 getTeamMembers。认证注入自 config.ts:68-70 三个 env（GITHUB_TOKEN/APP_ID/APP_PRIVATE_KEY）；config.ts:73-77 加载期强制二选一，缺则 throw。

## 4. 数据流

**判定某用户是否可 sponsor**：resolver.ts:12 定根团队 `steering-committee` → canSponsor（resolver.ts:101）首次触发 ensureSponsorsLoaded → getAllDescendantTeams（resolver.ts:46-49）展开全量团队 → 逐团队 getTeamMembers（resolver.ts:61-63，单团队失败只记 debug 跳过 resolver.ts:68-74）→ 并集缓存进 sponsorSet（resolver.ts:18/77）→ 此后 canSponsor 是纯内存 `Set.has`（resolver.ts:103）。缓存"一次性+失败记忆"：loadAttempted（resolver.ts:19/41）保证失败也只试一次、直接空集（resolver.ts:92）；clearCache（resolver.ts:121-124）供测试重置。

**installation token 获取-刷新-过期流**：index.ts:69 构造（无网络）→ 首个 API 调用触发 ensureInitialized → getRepoInstallation 换 installationId → 之后全部请求走 auth-app 策略。installation token 官方 1 小时过期，但**刷新由 @octokit/auth-app 内部托管**，临期自动用私钥重签——本层没有任何 token 生命周期代码（client.ts:66-73 用 authStrategy 而非手动换 token 正因于此）。PAT 路径整轮 token 不变。

## 5. 设计决策

**双认证并存**：App installation token 走 org 级细粒度授权——listOrgTeams 只需 Members 读权限（client.ts:252-254 注释明说），适合 CI；PAT 配置最简，适合本地 dry-run。优先级 App > token 硬编码于 client.ts:29-33；config.ts:73-77 加载期就拦死"两者皆无"，client.ts:77 的 throw 只是纵深防御。

**子团队为何内存展开而非 API 递归**：GitHub 原生 `teams.listChildInOrg` 要 admin 权限（client.ts:268-271 注释），teams.list 普通读权限即可；MCP org 的 steering-committee 存在嵌套子团队，sponsor 名单必须含子团队成员，遂用"全量列表 + parent 链"绕开权限墙，代价是根团队不可见时保守退化（client.ts:285）。

**334 行不再拆细**：所有方法共享同一 octokit 实例与 initialized 状态，拆文件只搬运状态；类型已独立到 types.ts。

## 6. 新人提示

- **区分认证与限流**：401=token 无效/过期；403=权限不足**或**二级限流（看响应头 Retry-After）；404 被语义化吞掉（非成员 client.ts:228）。isHttpError（errors.ts:18-24）只认 `.status`。
- **mock 方式**：mocks.ts:31-44 createMockGitHubClient() 预置 10 个 mock 方法，经 asGitHubClient（mocks.ts:142-144）强转注入被测类——新增公开方法必须同步 mocks.ts:15-26 接口，否则测试炸 undefined。
- **mock 已漂移（实测）**：MockMaintainerResolver.isCoreMaintainer（mocks.ts:82/92）在真实 resolver 不存在（真方法是 canSponsor/getSponsor，resolver.ts:101/109）；mock 还缺 getTeamMembers/getAllDescendantTeams，test/unit/ 也无 resolver.test.ts。
- **静态查询 getter 是死面**：client.ts:324-333 的 SEP_LABEL_QUERY/SEP_TITLE_QUERY 全仓零消费者，detector.ts:26/29 硬编码同样字符串——改查询串要改两处。
- **懒初始化不对称**：getAllDescendantTeams（client.ts:272）是唯一不直接调 ensureInitialized 的公开方法，靠 client.ts:273 的 listOrgTeams 传递初始化——别弄丢 listOrgTeams 内的 `await this.ensureInitialized()`（client.ts:256）。
- **性能要点**：per_page 已顶格 100；团队多时 getAllDescendantTeams 之后的逐团队 getTeamMembers（resolver.ts:59-74）是串行 N 次分页调用，为主要耗时点。

> 非空白字符 4796 / 锚 91（源码核验 0 坏）
