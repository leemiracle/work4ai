# 03 · issue 生命周期管线：setup → to-prd → to-issues → triage

> 对象：`/usr-data/data2/repos/ai-trending/skills/skills/engineering/` 下的 setup-matt-pocock-skills（6 文件 251 行）、to-prd（74 行）、to-issues（83 行）、triage（3 文件 372 行）。四者构成一条从"配置一次"到"issue 从生到死"的完整流水线，是全库耦合最深的 skill 群。

## 一、角色定位

管线解决 agent 时代特有问题：**技能怎么知道"issue"在你的仓里是什么？** GitHub/GitLab/本地 markdown/千仓千面的标签。ADR-0001 裁决（`/usr-data/data2/repos/ai-trending/skills/docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md:7-8`）：**硬依赖**（to-issues/to-prd/triage：无配置输出即错，须写显式 setup 指针）vs **软依赖**（diagnose/tdd/improve-codebase-architecture/zoom-out：配置只让输出更锐，模糊行文即可）——setup 的存在不打扰不需要它的技能。

`setup-matt-pocock-skills` 是**配置源**（README:33 安装时必选）；`to-prd`/`to-issues` 是**正向生成**（对话→PRD→可认领 issue）；`triage` 是**反向治理**（incoming→分类→就绪/补信息/拒绝）。四者读写同一套每仓配置：docs/agents/ 下 issue-tracker/triage-labels/domain 三文件。

## 二、内部结构

**setup 六文件**=1 主指令+5 种子模板。`skills/engineering/setup-matt-pocock-skills/SKILL.md`（121 行）自我定性"prompt-driven skill, not a deterministic script"（L15）。三决策一次一节（L32）：A issue tracker（L40-45 GitHub 默认/GitLab/本地/Other 自由描述）；B 标签映射（L49-59 五角色对接既有标签如 `bug:triage`）；C 域文档布局（L61-68）。写盘（L79-117）：CLAUDE.md 存在则编辑否则 AGENTS.md（L87）；已有块原地更新（L89）；docs/agents/ 三文件从种子起步（L109-115）。种子五件：issue-tracker-github（gh 全操作）/issue-tracker-gitlab（glab 差异：评论叫 notes、PR 叫 mr）/issue-tracker-local（`.scratch/<feature-slug>/` L7-11）/triage-labels（五行映射表 L5-11 右列可改）/domain（**缺席静默继续** L11）。

**to-prd**（74 行）**明确不访谈**——"Do NOT interview the user — just synthesize what you already know"（L6）：对齐是 grilling 的职责，本 skill 只做合成。流程：探仓→勾测试缝（L14-16 优先既有缝、用最高缝，与用户确认）→按模板写 PRD（L20-72，含超长编号 user stories）→发布并**直接打 `ready-for-agent`**（L18）。L8 是硬依赖指针原句。

**to-issues**（83 行）把 PRD 拆成 tracer bullet 垂直切片：`<vertical-slice-rules>`（L28-32）——每片窄但完整穿透所有集成层、独立可演示、宁多薄勿少厚；每片标 **HITL/AFK** 二型（L26，"Prefer AFK over HITL"）。流程：取上下文→探仓→起草→**向用户过颗粒度/依赖/HITL 标记**迭代到批准（L36-50）→按**依赖序**发布（L56 blockers first 以回填真实编号）。L10 硬依赖指针。issue 模板禁路径与代码片段，唯一例外 L67：原型的决策密集片段可裁剪内联。

**triage 三文件**=状态机+两份重文档。SKILL.md（103 行）：**AI 评论强制免责声明**（L10-14）；角色=2 类别×5 状态、恰一类一态（L36）；canonical→实际标签映射来自 setup 产物（L38）；迁移（L40：未标→needs-triage 起步、needs-info 回复后回归）。分诊：读全文+扫 `.out-of-scope/` 先例（L63）→推荐→bug 先试复现（L67 失败=强 needs-info 信号）→必要时 `/grill-with-docs`（L69）→按目标态落地（L72-77，wontfix-enhancement 写 .out-of-scope 后关闭）；口头指定目标态则跳过 grilling（L79-81）。AGENT-BRIEF.md（168 行）定义 ready-for-agent 评论的合同：**durability over precision**（L9-15 禁路径禁行号、改述接口契约）；**behavioral, not procedural**（L19-24）；**验收标准逐条可独立验证**（L26-31）+显式 out-of-scope 防镀金；L39-66 模板、L70-160 好坏示例。OUT-OF-SCOPE.md（101 行）定义拒绝知识库：**一概念一文件**（L17）、理由必须实质（L62-68）、按**概念相似度匹配**（L75"'night theme' matches dark-mode.md"）、仅 enhancement 拒绝写入（L86）。

## 三、外部连接

- **setup 的产物是三份协议文档**：issue-tracker.md 被 to-issues/to-prd/triage/in-progress review 消费；triage-labels.md 被 triage 消费；domain.md 被 tdd/diagnose/improve-codebase-architecture/zoom-out 四个软依赖技能消费。
- **triage↔grill-with-docs**：L69 的补 flesh 就是跑 grilling 会话。
- **to-issues↔prototype**：L67"原型片段例外"让 prototype 的答案沉淀直达 issue 正文。
- **triage↔.out-of-scope/**：本仓根目录三个文件就是 OUT-OF-SCOPE.md 机制的活实例（如 `/usr-data/data2/repos/ai-trending/skills/.out-of-scope/mainstream-issue-trackers-only.md:25` 的先例 #99）。
- **演进前身**：deprecated/qa 被 triage 状态机+agent brief 取代，其"禁文件路径、用户视角、复现必填"纪律被 AGENT-BRIEF.md 完整继承。
- **CONTEXT.md 术语表**（`/usr-data/data2/repos/ai-trending/skills/CONTEXT.md:7-8`）定义 Issue tracker/Issue 并明言管线成员读写——全员统一用语出自这里。

## 四、数据流

正向流：对话 → `/to-prd` 合成 PRD（+ready-for-agent）→ `/to-issues` 拆垂直切片、依赖序发布阻塞号回填 → AFK agent 按 agent brief 认领。

反向流：incoming issue → `/triage` 读全文+扫先例 → 推荐 → bug 试复现 → 缺信息则 grilling→分诊笔记（L83-99 模板：已确立/仍需你提供）；下次分诊**读旧笔记不重问**（L101-103）；拒绝的 enhancement→.out-of-scope/<concept>.md→关闭。

配置流：`/setup` 一次性生成 `## Agent skills` 块+docs/agents/ 三文件；此后直接改 docs/agents/*.md 即可，仅换 tracker 才需重跑（L121）。

## 五、设计决策

1. **为什么 setup 是 prompt 驱动而非脚本？** `.out-of-scope/setup-skill-verify-mode.md:9`：验证等变体都能用自然语言表达（"don't rewrite anything, just check drift"），加 flag 只会分裂维护面。
2. **为什么一次只问一节？** SKILL.md L32——每节先给 explainer 再给选项，假设用户不懂这些术语；三决策同时砸下超出非专家带宽。
3. **为什么 to-prd 禁访谈？** L6 的分工观：访谈是 grilling 的职责，PRD 只落规格——重复访谈既浪费又引入新的不对齐。
4. **为什么 to-issues 发布前必须过用户？** L36-50 四问（颗粒度/依赖/拆合/HITL 标记）——拆分是高杠杆决策，错粒度让并行 agent 全线返工。
5. **为什么 agent brief 禁路径禁行号？** AGENT-BRIEF.md:9-13：brief 寿命以周计、代码库持续演化，描述接口契约与类型名才能跨重构存活。
6. **为什么 AI 评论强制免责声明？** `skills/engineering/triage/SKILL.md:10`——公开场域读者须知道内容出自 AI；全库唯一"输出必须加标语"处。
7. **为什么 wontfix 的 enhancement 落盘而 bug 不用？** OUT-OF-SCOPE.md:86：增强类拒绝会被反复重提（先例追加机制），bug 一次性；落盘=机构记忆外化，未来重复分诊变成一次 grep。
8. **为什么 canonical 角色与实际标签分离？** 同文件 L38+triage-labels.md 映射表：技能说统一语言，落地打你仓真实标签串——协议常量与本地实现解耦。

## 六、新人提示

- 第一次跑的顺序是死的：先 `/setup-matt-pocock-skills`（README:35 之后"Bam - you're ready to go"），否则 to-issues/to-prd/triage 第一步就会提醒缺配置。
- 接手已有标签体系的仓：setup Section B 专为这准备——把 `bug:triage` 映射进表右列（triage-labels.md L5-11），不产生重复标签。
- 用 `/to-prd` 前先 grilling 对齐——它明确不做访谈，喂模糊上下文只会得到自信的模糊 PRD。
- `/to-issues` 发布前人工抽查两个 slice 的 Blocked by；依赖序发布（L56）为回填真实编号，依赖判断本身仍可能错。
- `/triage` 最高效姿势是自然语言（L44-49"Show me anything that needs my attention"），指定目标态走 Quick override（L79）秒办。
- 拒绝 feature request 时让它写 .out-of-scope：三个月后同款请求再来，L75 的概念相似度匹配替你翻旧账——管线里复利最高的一次性投入。
- 本仓自己也吃这套：`.out-of-scope/` 三个文件+`docs/adr/0001` 就是作者用自家管线治理自家仓库的实证。

*锚 30 处，全部 sed 现场核验 · understand-anything · 2026-11-02*
