# 04 · subagent-driven-development：制衡铁三角与代码评审验证

## 角色定位

subagent-driven-development（SDD）是本仓最重的执行模式：同会话内按计划逐任务派发全新子代理，控制器（主会话）编排"实现者→spec 评审→质量评审"三角色循环。核心信条一行讲透："Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration"（skills/subagent-driven-development/SKILL.md:12）。它解决两个问题：子代理不继承主会话上下文（无污染、可精确投喂），主会话自己的上下文留给协调工作（SKILL.md:10）。

行为纪律上最特别的一条是**连续执行**："任务之间不要停下来向人伙伴请示——执行就执行到底"，唯一停下来的理由是无法解决的 BLOCKED、真正阻碍进度的歧义、或全部完成（SKILL.md:14）。"要不要继续？"式请示被明确定性为浪费时间。

## 内部结构

**编排循环**（SKILL.md:44-87 的 dot 流程图）：读计划一次、抽取全部任务全文建 TodoWrite → 每任务派实现者子代理 →（有问先答）→ 实现者实现/测试/提交/自审 → 派 spec 合规评审 → 有问题回实现者修→再审 → 过关才派代码质量评审 → 有问题回修→再审 → 标记完成 → 下一任务 → 全部完成后派最终整体评审 → 移交 finishing-a-development-branch。红旗里钉死顺序："spec 合规未 ✅ 前禁启质量评审（顺序错误）"（SKILL.md:249）。

**三份 prompt 模板构成制衡铁三角**：

- **implementer-prompt.md（113 行）**：任务全文+场景设定由控制器粘贴（"不让子代理读文件"，SKILL.md:243）；开工前提问窗口——对需求/方案/依赖有任何不清楚"现在就问"（skills/subagent-driven-development/implementer-prompt.md:19-27）；文件纪律——文件超出计划意图就报 DONE_WITH_CONCERNS 而非擅自拆分（L50-51）；最关键的行为塑形句："**Bad work is worse than no work. You will not be penalized for escalating.**"（L59-60）——把升级去污名化，堵住"硬着头皮交差"的失败模式。汇报前自审四查：完整性/质量/纪律/测试（L74-98）。汇报格式四态：DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT（L103）。
- **spec-reviewer-prompt.md（61 行）**：合规评审的核心信条是"**绝不信任实现者的汇报**"——"实现者完成得可疑地快，汇报可能不完整、不准确、过于乐观，你必须独立验证一切"（skills/subagent-driven-development/spec-reviewer-prompt.md:21-24）。三查方向：漏做（声称实现但没做）、多做（没要求的功能/nice-to-have）、误解（解错了题）（L41-55）。输出格式带 file:line 引用。
- **code-quality-reviewer-prompt.md（25 行）**：不自带人设，直接复用 requesting-code-review/code-reviewer.md 的 Senior Reviewer 模板，外加文件职责/独立可测/符合计划结构/是否让文件显著膨胀四问（skills/subagent-driven-development/code-quality-reviewer-prompt.md:11-23）。只在 spec 评审通过后派发（L7）。

**四态处置**（SKILL.md:104-120）：DONE 进评审；DONE_WITH_CONCERNS 区分正确性疑虑（先处理）与观察记录（继续）；NEEDS_CONTEXT 补上下文重派；BLOCKED 四路归因——上下文问题补信息、推理不足换更强模型、任务太大就拆、计划本身错了升级给人。"绝不忽视升级或让同模型原地重试——实现者说卡住，就一定有什么要变"（SKILL.md:120）。

**模型分档**（SKILL.md:89-102）：机械任务（1-2 文件+清晰 spec）用便宜快模型——计划写得好的话大多数实现任务都是机械的；集成/判断任务用标准模型；架构/设计/评审用最强模型。

## 外部连接

上游必读：writing-plans（产出它消费的计划，计划头部的 agentic workers 指令行直指本技能）；工作区：using-git-worktrees 保证隔离（SKILL.md:270）；每任务评审复用 requesting-code-review（SKILL.md:272）；完工移交 finishing（SKILL.md:273）；子代理内部应遵循 test-driven-development（SKILL.md:276）。姊妹技能分工：dispatching-parallel-agents 管"2+ 独立问题并行调查"，本技能红旗明确"**禁止并行派多个实现子代理（冲突）**"（SKILL.md:242）——实现串行、独立调研才并行。

评审验证侧的姊妹技能：**requesting-code-review**（103 行）规定何时派评审（SDD 每任务后/大功能后/合并前为强制，SKILL requesting-code-review/SKILL.md:14-17），评审者只拿精确构造的上下文（描述+需求+BASE_SHA..HEAD_SHA 区间）绝不继承会话历史（skills/requesting-code-review/SKILL.md:8）；人设模板 code-reviewer.md（168 行）定义 Senior Code Reviewer——查计划对齐/代码质量/架构/测试真实性/生产就绪五维（skills/requesting-code-review/code-reviewer.md:33-63），输出分级 Critical/Important/Minor+明确裁决（L80-121），校准段要求"先承认做得好的再列问题——准确表扬让实现者信任其余反馈"（L65-69）。**receiving-code-review**（213 行）立场相反：收到评审要技术评估不要情绪表演——禁答"You're absolutely right!"（skills/receiving-code-review/SKILL.md:29-33），六步响应模式 READ→UNDERSTAND→VERIFY→EVALUATE→RESPOND→IMPLEMENT（L16-25），外部评审者的建议要先验证"对本代码库技术正确吗"再实现（L68-84）。**verification-before-completion**（139 行）是终点闸门：`NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`（skills/verification-before-completion/SKILL.md:19）——"未经核实就宣称完成是不诚实，不是高效"（L10），常见失败表里"Agent completed"一行要求看 VCS diff 而非信 agent 汇报（L49）。

## 数据流

一个任务的完整往返：控制器从已抽取的任务库取全文+场景 → 填 implementer 模板派 Task(general-purpose) → 实现者（可能先问一轮）TDD 实现+提交+自审 → 四态汇报 → 控制器派 spec 评审（喂任务原文+实现者汇报，强调别信汇报）→ ❌ 则回实现者修→再审循环 → ✅ 则取 git SHA 区间派质量评审（喂 code-reviewer.md 模板+四问）→ ❌ 则修→再审 → ✅ 标记完成。全部任务后派最终整体评审→finishing。集成测试实测数据（docs/testing.md:103-115）：一次运行 41 条消息、8 个子代理、总成本约 $4.6——主会话 cache 121 万 token 占大头，每个子代理独立 2.2-2.6 万 cache token，这个成本结构正是"控制器喂全文"设计的直接体现。

## 设计决策

- **两阶段评审强排序的理由**：spec 合规查"做的是不是要求的"（防漏做/多做），质量评审查"做得好不好"——顺序颠倒会在错误的东西上浪费高质量评审；spec 评审的"不信汇报"条款是对抗子代理乐观汇报的针对性设计。
- **控制器喂全文而非让子代理读文件**：SKILL.md:218 列为效率增益（无读文件开销）+质量增益（上下文精确可控）双动机；红旗"Make subagent read plan file"明令禁止。
- **自审不能替代真评审**：红旗"Let implementer self-review replace actual review (both are needed)"（SKILL.md:248）——自审是第一道网，独立评审是第二道，不可合并。
- **命名代理的祛魅**：v5.1.0 移除了唯一的命名代理 superpowers:code-reviewer——全仓统一改为 Task(general-purpose)+prompt 模板模式，人设并入 code-reviewer.md（RELEASE-NOTES.md:8）；这消除了对特定 agent 注册的运行时依赖。
- **成本意识内建**：模型分档表把"用能胜任的最弱模型"写成默认（SKILL.md:91），评审用最强模型——因为评审是最能省返工的环节。

## 勘误与新人提示

勘误：(1) code-quality-reviewer-prompt.md 自 v5.1.0 起指向 Task(general-purpose)，旧文档/记忆里的 `Task (superpowers:code-reviewer)` 写法已失效（RELEASE-NOTES.md:8）；(2) SDD 的 Integration 节在 v5.1.0 被整体移除，当前 SKILL.md 的"Required workflow skills"清单（L267-273）是残留的唯一引用块；(3) skills/writing-plans/SKILL.md:52 的 agentic workers 指令行与 tests/subagent-driven-dev 夹具的首行指令措辞不完全一致（前者含 checkbox 说明）。

新人提示：控制器自身别动手修——"不要手工修（污染上下文），派修复子代理给具体指令"（SKILL.md:263-265）；四态里 DONE_WITH_CONCERNS 最容易被误读成"要停"，技能要求先读疑虑再决定；看 docs/testing.md 的 token 分解表是理解"为什么喂全文反而省钱"的最快方式（cache 命中率）。
