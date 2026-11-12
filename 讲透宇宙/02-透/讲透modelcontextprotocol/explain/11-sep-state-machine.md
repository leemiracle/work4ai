# 11 · sep-automation/src 状态机三件套 —— analyzer / rules / transition：SEP 六态机的规则、判定与执行

## 1. 角色定位

这三个文件（sep/analyzer.ts 257 行 + rules.ts 168 行 + actions/transition.ts 102 行，合计 527 行）是图谱 L10 层「SEP 生命周期自动化机器人」的**域逻辑核心**。与姊妹篇构成严格三层：05 篇 processor.ts 是编排壳（决定"何时查、查什么、先迁移还是先查陈旧"），06 篇 github/client.ts 是 I/O 层（所有 GitHub API 调用的唯一出口），本篇三件套夹在中间——processor 调它们做判定与执行，它们经 client 落地读写。图谱连接度给三者定价：transition 10 条出边、analyzer 9 条、rules 5 条，均为工具链高连接节点。

三件套内部分工一句话：**rules.ts 是单一事实源**——六态邻接表、阈值声明、四个判定函数，零副作用；**analyzer.ts 是状态→行为的判定器**——纯读，产出"该做什么"的意图，不写任何东西；**transition.ts 是合法迁移的执行器**——查表校验后对 GitHub 做三连写。

一处对直觉的**勘误**：这套状态机的输入是 GitHub label / event / comment，**不是 seps/ 目录的 markdown 正文**。seps/*.md 头部的 `- **Status**: Final` 行由 render-seps.ts L64 正则解析，是另一条平行的人类维护表示，且其词汇表是六态的超集——rejected/withdrawn/superseded（render-seps.ts L114-121 各有徽章配色）在 types.ts L6 的 `SEPState` 里根本不存在。机器人不读 markdown，markdown 也不读机器人，两者之间没有程序性同步。

## 2. 内部结构

**rules.ts——168 行管全部规则**。核心 `STATE_TRANSITIONS`（L16-45）六态邻接表：`proposal: ['draft', 'dormant']`（L20，L18 注释明言 draft 边由核心维护者赞助触发）、`draft: ['in-review', 'dormant']`（L25）、`'in-review': ['accepted', 'draft', 'dormant']`（L31，唯一带回退边的状态）、`accepted: ['final', 'dormant']`（L36）、`final: []`（L40，终态零出边）、`dormant: ['proposal', 'draft']`（L44，可复活）。`STATE_LABELS`（L51-58）六态字面量数组。`StalenessRule` 接口（L70-76）五字段；`STALENESS_RULES`（L78-100）三条政策：proposal 90 天 ping 作者 / 180 天休眠并关闭（L82-86，`closeOnDormant: true`）、draft 90 天 ping sponsor（L88-93）、accepted 30 天 ping 作者催参考实现（L94-99）。两个全局常量：`MAINTAINER_INACTIVITY_DAYS = 14`（L108）、`PING_COOLDOWN_DAYS = 14`（L116）。四个 helper：`isStateLabel` 类型守卫（L137-139）、`extractState` 从 label 数组提取状态（L144-151，首个命中者胜）、`isValidTransition`（L156-161——L157-159 `fromState` 为 null 恒真，"初始状态赋值总是合法"）、`getStalenessRule`（L166-168）。

**analyzer.ts——判定器，analyze() 主入口**（L24-72）五步：L28-29 一次性拉取评论与事件**共享给所有检查**（省 API 配额）；L33-34 算责任人活跃天数；L37-51 **冷却闸先于一切分派**——距上次 bot ping 不足 `pingCooldownDays`（14 天）直接返回全否结论（L41-50，reason 文案 L48），这是防打扰第一道闸；L54-71 按状态 switch 分派，in-review/final/dormant **落 default 分支（L61-70）返回全否**——自动化对这三态的陈旧性保持沉默。三个专责分析器同构（阈值比较 → 构造 `StaleAnalysis`）：`analyzeProposal`（L74-110）180 天休眠+关闭（L76-86）、90 天 ping 作者（L89-99）；`analyzeDraft`（L112-135）90 天 ping sponsor（L114-124）；`analyzeAccepted`（L137-160）30 天 ping 作者（L139-149，reason L147 点明 "awaiting reference implementation"）。`checkUserActivity`（L165-178）是第二入口，供问责线调用，L174 `?? item.createdAt` 兜底无活动记录者。私有工具群：`getResponsibleUsername`（L204-209——accepted 恒取作者 L205-207，其余取 `assignees[0] ?? author` L208）；`findLastUserActivity`（L214-243）双循环扫 events（L221-228）与 comments（L230-240），L231-233 跳过含 `BOT_COMMENT_MARKER` 的 bot 评论后取最大日期；`findLastBotPingDate`（L248-256）从数组尾部倒序找第一条 bot 评论——评论按时间升序，尾部即最新。

**transition.ts——执行器，executeTransition() 时序**（L27-86）六步：L33-42 构造 `SEPAction`（`ActionType.Transition` L35；`fromState ?? undefined` L37 处理无态项）；L45-51 **校验前置**——`fromState` 存在才调 `validateTransition`，非法即 warn 并失败返回；L53-59 dryRun 早退（只记日志返回 success，不触碰 GitHub）；L61-79 真执行三连写——摘旧 label（L63-65，同样以 fromState 存在为前提）→ 贴新 label（L68）→ 发评论（L71-73，L71 把 null 折叠成 `'none'` 字面量喂给 comment.ts L8 `createTransitionComment`，`addComment` 解构回 `url` L73）；L81-85 catch 经 `getErrorMessage` 兜底。`validateTransition`（L91-101）单独暴露**为测试服务**（L89 注释明言）——合法时 L93 区分 'Valid transition' 与 'Initial state assignment'，非法时 L96-100 从 `STATE_TRANSITIONS` 取合法目标列表拼进错误信息。

## 3. 外部连接

**上游 processor.ts**：陈旧线 `checkStaleness` L166 调 `analyzer.analyze`；自动迁移线 `checkAutoTransition`（L135-158）L138 双门（`state === "proposal"` 且 assignees 非空）为**硬编码**、L142 `getSponsor` 核验资格、L152 调 `executeTransition`；问责线 `checkMaintainerAccountability`（L183）L190 `canSponsor` 过滤、L199 调 `checkUserActivity`、L204 达阈值即 L214 `pingMaintainerDirectly`。

**横向 actions/**：ping.ts `executePing`（L42）L46-48 优先休眠分派给 `markDormant`（L212-270）——这是**第二个迁移执行器**：L227-233 直接查 `STATE_TRANSITIONS` 校验 dormant 边（不走 `isValidTransition`，同语义两处写法），L244-247 同款 remove-first 顺序（注释明言 "safer order - avoids dual-label state"），L257-259 按需 `closeIssue`。comment.ts 七工厂供全部文案。

**壳层 sep/types.ts**：12 行 re-export 垫片（L6-11）把 `STATE_TRANSITIONS` 别名为 `VALID_TRANSITIONS` 连同 `STATE_LABELS`/`isStateLabel`/`extractState` 转发，L5 注释明言 backward compatibility。真实消费者只有 detector.ts（L8 import、L81 `extractState(labels)` 把 GitHub label 翻译成 `SEPState`——**状态机入口的真正发生地**）与 sep-types.test.ts。

**配置链 config.ts**：L63-65 用裸 `.find` 从 `STALENESS_RULES` 提三态默认值（L86-89 六个 env 可逐项覆盖），L90-91 注入两个 14 天常量——analyzer 消费的是 config 对象而非 rules 原表。utils/dates.ts L10-11 `daysBetween` 用 `Math.floor`。

**测试**：transition.test.ts（103 行）——validateTransition 三例（L34 合法 / L45 非法 / L51 初始赋值）+ executeTransition 三例（L60 dry-run / L75 真实 / L90 非法拒绝）；sep-types.test.ts（58 行）经 shim 覆盖表与提取，L35 实证 `extractState(['proposal','draft'])` 返回 `'proposal'`（顺序敏感）。

## 4. 数据流：两条主干链路

**迁移链（proposal→draft 自动晋升）**：sweep 扫描 → detector `findAllSEPs` 双搜索（detector.ts L26-29，`label:SEP is:open` 与 `SEP in:title is:open` 去重合并）→ `toSEPItem` L81 `extractState` 翻译 label → processor L138 双门命中 → L142 sponsor 资格 → transition.ts L46 查表（rules.ts L20 proposal 行含 draft）→ 摘 `proposal` label → 贴 `draft` label → 发评论。一次表查询、三次写。

**陈旧链（proposal 90 天 ping）**：同一 sweep → processor L166 `analyze` → L28-29 拉评论事件 → L37 冷却闸（14 天内 ping 过即短路）→ L33 责任人活跃度：L208 取 `assignees[0] ?? author`（proposal 无 assignee 时即作者）→ `findLastUserActivity` 逐条比对 login，**跳过 bot 评论**（L231-233）→ `daysBetween` 取整 → switch 进 `analyzeProposal` → 90 天命中返回 `shouldPing: true, pingTarget: 'author'` → processor L172 交 pingHandler 落地评论。

**bot 评论的双重身份**是防打扰机制核心：`BOT_COMMENT_MARKER`（types.ts L72）既是假活跃过滤器（L231——否则 ping 本身刷新时间戳，SEP 永不陈旧），又是冷却时钟的针（L251——倒序找最新 bot 评论日期）。一个 HTML 注释同时供养两套机制。

**天数语义**：`daysBetween` 是 floor（dates.ts L11），阈值 90 的实际含义是"满 90 个 24 小时后的首次 sweep 触发"；sweep 频率叠加在其上，实际触发日在 90–91 天之间浮动，比较逻辑对此免疫。

## 5. 设计决策

**表与 switch 的分裂**：`STALENESS_RULES` 是声明式意图（每条带政策注释），但 analyzer 的分派结构是硬编码 switch——**数值**经 config 解耦（改阈值走 env 零代码），**结构**没有：新增状态至少六处手术（rules.ts L16 邻接表、L51 STATE_LABELS、STALENESS_RULES 加行、types.ts L6 SEPState、analyzer L54 switch、config 加字段）。数据驱动只做了一半：表管住了"多少天"，没管住"哪些状态参与陈旧判定"。

**判定/执行分离的回报与代价**：analyzer 纯读返回 `StaleAnalysis` 意图（types.ts L31-39，shouldPing/shouldMarkDormant/shouldClose/pingTarget 四元组），可无副作用测试，dryRun 因此能在执行层而非判定层实现（transition.ts L53、ping.ts L235 两处）。代价是"迁移"有**两个执行器**：transition.ts 管显式迁移，ping.ts L212 `markDormant` 管休眠支路，各自实现"查表+摘旧+贴新+评论"，平行而有微妙差异（后者多 close 一步）。

**remove-first 的失败模式**：L63-65 先摘后贴防双 label 态，但两次写之间无事务——`addLabels` 失败时 SEP 陷入**无态真空**：`extractState` 返回 null → analyzer L61 default 静默 → 自动迁移 L138 因 `state !== 'proposal'` 不触发——机器人对无态项永久沉默，需人工补 label。L71 的 `'none'` 折叠说明作者意识到该态存在并预留了文案路径，但未提供自愈。

**三处勘误（源码 grep 实证）**：① `AUTO_TRANSITION_RULES`（rules.ts L123-132）是**死导出**——全仓（src+test）零消费，真实自动迁移硬编码在 processor.ts L135-158；这张"自动迁移规则表"是文档性声明而非活代码路径，**别把它当真源**。② `getStalenessRule`（rules.ts L166-168）同样零消费——config.ts L63-65 用裸 `.find` 绕过了它。③ analyzer.ts L180-187 `findResponsiblePersonActivity` 的 JSDoc 声称 "For 'proposal' and 'accepted' states, this is the author"，与 L204-209 实现**直接矛盾**（实现里仅 accepted 恒取作者，proposal 取第一 assignee）——以实现为准，05 篇数据流叙述即按实现。另有一处轻量注释漂移：rules.ts L67 注释称 pingTarget 可为 "author, sponsor, or maintainer"，L74 类型却只有 `'author' | 'sponsor'`（maintainer 仅存在于 types.ts L37 的 StaleAnalysis.pingTarget）。

## 6. 新人提示

- **改状态机前数清同步点**：新增一条边只改 rules.ts L16-45；新增一个状态是上节六处手术；改阈值只动 env（config.ts L86-91，`PROPOSAL_PING_DAYS`/`PROPOSAL_DORMANT_DAYS`/`DRAFT_PING_DAYS`/`ACCEPTED_PING_DAYS`/`MAINTAINER_INACTIVITY_DAYS`/`PING_COOLDOWN_DAYS`），不动代码。
- **排查"为什么我的 SEP 没被 ping"**按序查三闸：①冷却（analyzer L37-51，14 天）②责任人活跃度（L33——只看本 SEP 的 events/comments，sponsor 在别处的活动不算）③状态白名单（L54-60，in-review/final/dormant 永不 ping）。
- **测试锚点**：状态表与提取看 sep-types.test.ts（经 shim 导入，兼容层自身有测试覆盖）；迁移校验与执行看 transition.test.ts L33-101——`validateTransition` 单独暴露就是为了让测试不碰 GitHub。
- **别被两个执行器绊倒**：显式迁移走 transition.ts，休眠走 ping.ts `markDormant`——后者不调前者而是自己查表（L227）。改 `STATE_TRANSITIONS` 两处自动受益；改执行逻辑必须检查两份。
- **label 与 markdown 是两个世界**：seps/*.md 的 Status 行由人维护、render-seps.ts L64 消费，词汇表含 rejected/withdrawn/superseded 等 `SEPState` 没有的态；机器人只认 GitHub label。文档站显示状态与机器人治理状态无程序性同步，漂移只能靠 review 兜底。
- **双状态 label 是未定义行为**：`extractState` 首个命中者胜（sep-types.test.ts L35），GitHub label 顺序不承载语义优先级——同时贴 proposal+draft 时谁先出现谁赢，摘 label 的 remove-first 顺序正是为了从源头避免这种态。

> 非空白字符 7629 / 锚 147（覆盖 analyzer.ts / rules.ts / transition.ts / sep/types.ts / detector.ts / types.ts / config.ts / processor.ts / ping.ts / dates.ts / render-seps.ts / comment.ts / transition.test.ts / sep-types.test.ts，全部源码逐条核实）
