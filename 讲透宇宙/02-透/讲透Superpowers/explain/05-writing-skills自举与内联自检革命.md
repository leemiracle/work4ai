# 05 · writing-skills：元技能自举、内联自检革命与一份死资产

## 角色定位

writing-skills（655 行，仓内最长技能）是技能库的自举层——"写技能的技能"。开篇定义斩钉截铁："**Writing skills IS Test-Driven Development applied to process documentation.**"（skills/writing-skills/SKILL.md:10）：测试用例=带子代理的压力场景，生产代码=技能文档，RED=无技能时代理违规的基线，GREEN=有技能时代理合规，REFACTOR=堵新漏洞。核心原则同样一句："没看过代理在没有技能时失败，你不知道这技能教的东西对不对"（SKILL.md:16）。

它在整个体系里承担"方法论宪法"的角色：CLAUDE.md:90 规定改技能必须用本技能+对抗压测+前后 eval；TDD 映射表（SKILL.md:30-45）把 11 个 TDD 概念逐项翻译到技能创作；铁律 `NO SKILL WITHOUT A FAILING TEST FIRST`（SKILL.md:377）对新技能与对既有技能的编辑同等生效——"没测试就写技能？删掉重来。没测试就改技能？同罪"（SKILL.md:379-389）。

## 内部结构

六大部分：

- **技能分类与创建判据**：Technique（具体步骤）/Pattern（思维方式）/Reference（API 文档）三类（SKILL.md:61-70）；创建判据要求"技术对你不直觉显而易见、跨项目可复用、非项目特定"（SKILL.md:47-53）；"能用 regex/校验强制的机械约束就该自动化，文档留给判断题"（SKILL.md:59）。
- **SKILL.md 结构规范**：YAML frontmatter 两必填字段 name/description（max 1024 字符，见 agentskills.io 规范）、标准章节模板（Overview/When to Use/Core Pattern/Quick Reference/…，SKILL.md:93-137）。
- **CSO（Claude 搜索优化）**：四手段——富 description/关键词覆盖/动词优先命名/token 效率（getting-started 类技能 <150 词）。最重要的一条铁律："**Description = When to Use, NOT What the Skill Does**"（SKILL.md:150）。实测证据：SDD 技能的 description 曾写 "code review between tasks"，结果 Claude 只做了一次评审而流程图明明要求两阶段；改成纯触发条件后 Claude 才正确读了正文（SKILL.md:154-158）。"总结工作流的 description 是 Claude 会走的捷径，技能正文成了被跳过的文档"（SKILL.md:158）。
- **测试方法论**（SKILL.md:395-531 + testing-skills-with-subagents.md 384 行）：按技能类型分四路测——纪律型技能必须 3+ 组合压力压测、技术型/模式型/参考型各有判据（SKILL.md:395 起）。**压测类型学七种**：时间/沉没成本/权威/经济/疲惫/社交/"务实 vs 教条"（testing-skills-with-subagents.md:128-141），最好组合 3+ 种；好场景五要素——具体选项逼选择、真实约束、真实路径、让代理行动（"你做什么"而非"应该做什么"）、无退路（L144-150）；场景开头模板"IMPORTANT: This is a real scenario"（L154-158）。**堵漏三件套**（L178-210）：规则显式否定（Before:"写码前没测试？删掉"→After:"删掉重来。No exceptions: 别留作参考/别边写测试边改/别看它/delete 就是 delete"）、借口表加条目、红旗清单加条目。**元测试**（L240-265）：GREEN 不灵时先怀疑测试本身——场景是否真有压力、子代理是否理解技能可用。
- **反防合理化工程**（SKILL.md:459-531）：显式关闭每个漏洞、"精神 vs 字面"论证预先反驳（TDD 技能里那句"违反规则的字面就是违反规则的精神"就是这么来的）。
- **配套资产**：anthropic-best-practices.md（1150 行官方指南镜像，SKILL.md:20 声明是互补参考非权威——本仓哲学与 Anthropic 公开指南不同，CLAUDE.md 拒收"合规性"重写）；persuasion-principles.md（187 行）给出心理学实证根基：Meincke et al. 2025 七原则实验 N=28,000，说服技术让合规率 33%→72%（skills/writing-skills/persuasion-principles.md:7）——权威（祈使句"No exceptions"）、承诺（宣告+TodoWrite）、稀缺（"Before proceeding"）等原则解释了技能文本为何满是祈使句与红旗表；examples/CLAUDE_MD_TESTING.md 是完整实测战役记录（测的是 CLAUDE.md 文档变体而非 SKILL.md）；graphviz-conventions.dot 用 DSL 自证地定义流程图规范（文件本身是合法可渲染的 dot 程序，skills/writing-skills/graphviz-conventions.dot:1-2）；render-graphs.js（168 行）把 SKILL.md 里的 dot 代码块渲染成图。

## 外部连接

上游硬依赖：REQUIRED BACKGROUND 指向 test-driven-development（SKILL.md:18）——TDD 是母方法论，testing-skills-with-subagents.md:13 重申；testing-anti-patterns 也声明同一前置。下游：所有 16 个技能都是它的"运行时产物"；CLAUDE.md 的贡献政策（94% 拒绝率、"技能是被测代码"）以它为执行机制。测试连接：tests/claude-code/test-worktree-native-preference.sh 是方法论的活样本——RED（无 Step 1a 时代理用 git worktree add）/GREEN（有 Step 1a 用 EnterWorktree）/PRESSURE（时间压力+已有 .worktrees/ 诱导合理化回退）三相（test-worktree-native-preference.sh:1-14），50/50 全过（20 GREEN+20 PRESSURE+10 全文），关键洞察"修复靠 Step 1a 的文本而非文件分离"（L9-12）正是 CSO 哲学的又一实证。

## 数据流

一次技能创作的 RED-GREEN-REFACTOR 回路（SKILL.md:533-560）：设计压力场景（≥3 组合压）→ 无技能跑子代理、逐字记录违规与合理化（RED=看它失败）→ 写最小技能文本只针对那些具体借口（GREEN）→ 同场景带技能重跑验证合规 → 上线后捕获新合理化 → 三件套堵漏 → 再验直到 bulletproof（REFACTOR）。检查清单（SKILL.md:596-638）把三阶段+质量检查+部署各拆成 checkbox。真实迭代案例：TDD 技能自身的加固史——初始测试失败→加反制→加基础原则→连续通过（testing-skills-with-subagents.md:282-308）。

## 设计决策

- **v5.0.6 内联自检革命（本篇的戏剧核心）**：2026-01-22 设计的"文档评审系统"给 brainstorming/writing-plans 各加一个子代理评审循环（派新代理审 spec/计划、3 轮迭代上限）。35 天后（v5.0.0 引入 03-09，v5.0.6 移除 03-24）被内联自检替换，理由是硬数据：**评审循环让执行时间翻倍（~25 分钟开销）而计划质量无可测提升——5 个版本×5 试次的回归测试质量分完全相同**（RELEASE-NOTES.md:100-107）；内联四查 30 秒抓 3-5 个真 bug，缺陷率与子代理版相当。brainstorming 的内联自检=占位符/一致性/范围/歧义四查（skills/brainstorming/SKILL.md:116-124），writing-plans 的=spec 覆盖/占位符/类型一致三查（skills/writing-plans/SKILL.md:122-132）。
- **死资产的甄别**：skills/brainstorming/spec-document-reviewer-prompt.md（49 行）正是那套被移除循环的 spec 评审载荷——现盘上 SKILL.md 全文不引用它，仅历史 plan/spec、RELEASE-NOTES 与 tests/claude-code/test-document-review-system.sh:81 还提到。它是"删除机制、保留产物"式退场的典型：不删文件但断了消费边，读代码时须意识到这不是活流程的一部分。writing-plans 侧的 plan-document-reviewer-prompt.md 命运相同。
- **CSO 反直觉但有实验依据**：description 越"有用"（总结流程）越坏事——这是从实测失败反推的设计规则，也是"技能文本=行为代码、会被模型走捷径绕过"的底层洞察。
- **自举的证据链**：本技能自己就附带压测方法论、反合理化清单与 checklist——用被定义的方法论写成，与 graphviz-conventions.dot 的"用 DSL 写 DSL 规范"同构。

## 勘误与新人提示

勘误：(1) 上述两份 *-document-reviewer-prompt.md 均为死资产，勿当作现行流程；(2) v5.0.6 曾修正本技能一处假声明——frontmatter 并非"只有两个字段"而是"两个必填字段"（完整字段见 agentskills.io 规范，RELEASE-NOTES.md:118，PR #882）——老教程引用需核对；(3) testing-skills-with-subagents 的历史路径（skills/meta/testing-skills-with-subagents）在 CREATION-LOG 等旧文档中残留。

新人提示：想给本仓提 PR，先跑一遍 RED 基线并留逐字记录——没有 before/after eval 的行为塑形类改动直接拒收（CLAUDE.md:90-94）；写 description 时自查"我是否在描述它做什么"——是就重写；pressure 场景模板最易犯的错是给出退路（"你会问人伙伴吗？"），要逼选择。
