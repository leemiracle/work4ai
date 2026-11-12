# 05 · sep-automation/src/processor.ts — SEP 生命周期机器人的编排中枢

## 1. 角色定位

`processor.ts` 是图谱 L10 层「SEP 生命周期自动化机器人」（31 节点：actions 三件套、hooks 双件、github client、rules、sep analyzer/detector、maintainers resolver）的核心 `file:` 节点。守护对象是仓库根部 `seps/` 目录——MCP 规范提案库（100+ 文件）：每个 SEP 是一个 PR/issue，状态用 GitHub label 表示，六态机 `proposal → draft → in-review → accepted → final` 加 `dormant` 支路（types.ts:6）。

为何需要自动化：提案量大、时限严格（proposal 90 天 ping 作者、180 天休眠关闭，rules.ts:82-87）、sponsor 资格须对照 steering-committee 组织树实时核验——人工跟踪必遗漏。`SEPProcessor`（processor.ts:50）因此成为编排中枢：图谱入边为 index.ts 的 imports（L77 组装）与测试 imports，自身却不 import 任何 GitHub 客户端、不含一句用户文案——纯调度壳。

一处勘误：常被描述为"事件驱动 webhook"，实为**批处理扫描器**——index.ts:5-6 声明 `npm start`（全量 sweep）与 `--issue 123`（单发）两模式；认证身份确是 GitHub App（github/client.ts:6 `createAppAuth`），但触发模型是定时轮询。

## 2. 内部结构：process() 三段流水线

`process(sep)`（processor.ts:63）串起四步：

**前置过滤**——L78 `isClosed` 直接返回空结果。

**第一段·自动迁移**：L84 调 `checkAutoTransition`（L135）——L138 双门（`state === "proposal"` 且 assignees 非空）→ L142 `getSponsor` 核验 assignee 中有无 steering-committee 成员 → L152 `executeTransition(sep, "draft", ...)`。关键短路在 L95：迁移成功即提前 return，**不再查陈旧**，避免同轮既迁移又 ping。

**第二段·陈旧检查**：L99 调 `checkStaleness`（L163）——L166 `analyzer.analyze(sep)` 产出 `StaleAnalysis`（types.ts:31），L168 判 `shouldPing`/`shouldMarkDormant` 全假则返回 null，否则 L172 `executePing`。

**第三段·维护者问责**：L110 门只放行 `draft`/`in-review`，L111 调 `checkMaintainerAccountability`（L183）——L190 `canSponsor` 逐个过滤，**只 ping 核心维护者**；L199 `checkUserActivity` 查活跃，L204 达阈值即 L214 `pingMaintainerDirectly`。

**汇总回填**：`updateSummaryFromStaleness`（L230）按 action.type（switch L241）分派进 `SummaryData` 四桶 transitions/pings/needsSponsor/dormant（L20-39）；ping 目标解析在 `getTargetUser`（L274：author 直取，sponsor/maintainer 都走 `getSponsor`）。`ProcessResult`（L42）交还执行结果与汇总。

## 3. 外部连接：六组件协作网

**组装端** index.ts：L69-74 依次构造 GitHubClient、MaintainerResolver、SEPDetector、SEPAnalyzer、TransitionHandler、PingHandler；L77-84 六依赖注入 processor；L87-88 注册 HookRegistry 挂 DiscordHook。主循环 L122-138 逐 SEP 处理，单条失败不中断。

**执行端 actions/**：transition.ts `executeTransition`（L27）先 L46 校验迁移合法性（引用 rules.ts:156 `isValidTransition`），再 L64 摘旧 label → L68 贴新 label → L73 发评论；ping.ts `executePing`（L42）L46 优先休眠分支，`pingSponsor`（L151）L156 查无合格 sponsor 时 L160 降级 `postNeedsSponsor` 求助；`markDormant`（L212）L227 用 `STATE_TRANSITIONS` 再校验、L258 按需 closeIssue。文案全出自 comment.ts 七个工厂（L8 `createTransitionComment`、L111 `createNeedsSponsorComment` 等）。

**判定端**：maintainers/resolver.ts 以 `SPONSOR_ROOT_TEAM = "steering-committee"`（L12）为根，L46 `getAllDescendantTeams` 递归子队聚合 sponsor 集合，L109 `getSponsor` 取首个合格 assignee；sep/analyzer.ts 管活跃度与冷却；sep/detector.ts L26-29 用 `label:SEP is:open` 与 `SEP in:title is:open` 双搜索去重，L81 `extractState` 提取状态。

**通知端 hooks/**：registry.ts L30 `dispatch` 用 `Promise.all` 广播，L34-43 每 hook 独立 try-catch——通知失败不伤主流程；discord.ts L31 显式只消费 summary 事件。与 `seps/` 目录是纯语义连接：detector 搜出的 PR 即往 `seps/` 加文档的 PR，机器人不读写这些文件，只治理承载它们的 GitHub 对象。

## 4. 数据流：一个 SEP PR 从提交到 Final 的旅程

1. **proposal 期**：新 PR 贴 `proposal` label、无 assignee。sweep 扫到 → L138 因 assignees 为空返回 null → 进陈旧检查。责任人判定（analyzer.ts:204-209）：非 accepted 态取第一 assignee 否则回退作者，此处即作者。`analyzeProposal`（L74）双阈值：≥90 天 ping 作者（L89），≥180 天休眠+关闭（L76）——ping.ts 落地为评论。
2. **晋升 draft**：核心维护者 self-assign → 下轮 sweep L138 命中 → L142 确认资格 → L152 迁移。transition.ts L46 查规则表（rules.ts:20 `proposal: ["draft","dormant"]` 合法）后换 label 发评论。
3. **draft 期双线监控**：陈旧线 `analyzeDraft`（analyzer.ts:112）90 天无 sponsor 活动 ping sponsor；assignee 全非核心则 ping.ts:160 转 needs-sponsor。问责线 processor.ts:110 放行：核心维护者 14 天无活动（rules.ts:108）被点名。
4. **in-review/accepted 人工推进**：自动化仅 proposal→draft 一条自动边（rules.ts:123-132 `AUTO_TRANSITION_RULES`）。accepted 态 30 天（rules.ts:96）ping 作者催参考实现（analyzer.ts:137 此态责任人强制为作者）。
5. **终态与复活**：`final: []`（rules.ts:40）不可迁出；`dormant: ["proposal","draft"]`（L44）可复活。
6. **防打扰**：动作后 14 天冷却（rules.ts:116 → config.ts:91 → analyzer.ts:37-51 读最后一条 bot 评论日期）；bot 评论不计入用户活跃（L231 查 `BOT_COMMENT_MARKER`）——否则 ping 刷新 `updated_at` 造成永不过期的假活跃。
7. **收尾广播**：四桶在 index.ts:149-165 组装 `SummaryEvent`（hooks/types.ts:51）→ dispatch → Discord embed（discord.ts:44 带 10s 超时）。

## 5. 设计决策

**processor 只编排不含业务**：阈值全集中 rules.ts 单一事实源——config.ts:63-65 从 `STALENESS_RULES` 提默认值，L86-91 允许 env 覆盖，改策略零代码。动作在 actions/、文案在 comment.ts、通知在 hooks/，processor 只剩三职责：调用顺序（迁移优先陈旧）、短路（L95）、汇总分派（L241）。测试因此可只桩 TransitionHandler（processor.test.ts:59）而用真 PingHandler（L61）。

**resolver 独立成模块**：sponsor 资格是组织结构问题而非工作流问题——子队会增减，硬编码必腐。L46 走 `listOrgTeams + parent` 遍历避开 admin 权限。缓存（L18-19 `sponsorSet`/`loadAttempted`）带熔断：L91-93 加载失败不 fallback 名单而是返回空集——宁可全员"无资格"（机器人静默），不可误授权。

**Discord 走 registry**：`SEPHook` 接口（hooks/types.ts:67）留扩展位，加 Slack 只需 register 一实现；discord.ts:31 只听 summary 防逐条事件打爆频道；registry 错误隔离使通知成纯旁路。`dryRun` 全链贯穿：processor L156/L174/L218 透传，transition.ts:53-59 干跑只记日志。

## 6. 新人提示

- **改状态机从 rules.ts:16 `STATE_TRANSITIONS` 进**——一张表管全部合法迁移，transition.ts 与 ping.ts 都查它。新增状态须同步 types.ts:6 `SEPState` 与 rules.ts:51 `STATE_LABELS`；新增自动迁移边注意目前仅 proposal→draft 一条硬编码。
- **测试**：test/unit/processor.test.ts 112 行两用例——L66 验证陈旧 ping 进 summary 桶（mock 的 `addComment` 会真把评论 push 回数组）；L90 验证 dormant 汇总保留 `wasClosed` 决策。跑法 `npm test`（vitest）。
- **活跃度与冷却看 analyzer.ts**：入口 `analyze`（L24），责任人活跃度在 L33（注释明言"不是任何活动——bot ping 会刷新 updated_at"），冷却判定 L37-51，按用户粒度的 `checkUserActivity` 在 L165。

> 非空白字符 4786 / 锚 95
