# 07 skills 体系与 agent-first 仓库设计

## 一、角色定位

多数开源框架的文档写给人看；NAT 仓库根的 `AGENTS.md` 与 `skills/` 写给 **AI 编码代理**执行。这是 NAT 区别于普通框架的核心设计：它假定贡献者首先是 coding agent，把"代理在这个仓库怎么干活"沉淀为 11 个可路由、可引用、可进化的技能单元。AGENTS.md:18 自我定位 "AI Agent Entry Point"，AGENTS.md:20 声明技能全部住在仓库根 `skills/` 且**扁平布局**。与之并行的 `docs/source/`（build-workflows/components/extend/get-started 等章节）仍服务人类读者——双轨制：人类文档讲概念叙事，技能文档讲操作判据，每条都是代理可执行的指令。

## 二、内部结构

### 第一层：AGENTS.md 入口路由

共 83 行，四件事。其一 `Mandatory Repository Rules`（AGENTS.md:22-29）：编辑前 `git status` 保护用户未提交修改（L24）、优先现有模式（L25）、不加依赖不动 lock（L26）、命名规范——公开文档首次用全称 "NVIDIA NeMo Agent Toolkit"，`nat` 仅留给 CLI、Python 命名空间、包元数据等技术标识符（L27）。其二 Skills Directory 清单（L31-43）列 11 个 skill。其三 Task Routing 表（L45-65）映射任务到 skill：写 workflow YAML 找 nat-workflow-creation、选 agent 找 nat-agent-configuration、修路径检查失败找 nat-path-checks。其四 Quick Commands（L73-81）给三条基线命令。

### 第二层：11 个 skill 分域手册

每个 skill 一个目录，契约是单个 `SKILL.md`（frontmatter 含 name/description/author）加可选 `references/`。全部 SKILL.md 合计仅 391 行，最长的 skill-evolution 也只 69 行——**入口薄、参考厚**。`nat-user-rules/SKILL.md:3` 的 description 写明 "Use first"，是代理第一跳；L12 起的 Mandatory Rules 与 AGENTS.md 同源但更操作化：写任何 YAML 前先跑 `nat info components` 发现 `_type`、"绝不凭记忆发明 `_type` 名和配置键"——直指 LLM 代理最大失败模式（幻觉配置键）。L37 给五个现成 `nat info components -t <类型>` 命令。其余 skill 各管一域：nat-installation、nat-workflow-creation（YAML 与 LLM 配置）、nat-agent-configuration（agent 选型）、nat-tools-and-functions、nat-evaluation、nat-optimization（`nat optimize`）、nat-telemetry、nat-mcp-and-serving、nat-path-checks（CI 路径检查）。

### 第三层：references/ 深参考

细节全部下沉。最典型是 nat-agent-configuration：SKILL.md 仅 24 行，L19 References 直接指路，深料在 `references/agents.md`（136 行）——L3 开门见山 "The nine built-in agent types"，agents.md:7-9 先教**分类法**（固定步骤无 LLM 决策 → executor 或普通函数；研究/分析/决策类 → agent；拿不准先问一个澄清问题），agents.md:13-19 一张表对照七种 agent 的工具支持与适用场景，L23 起逐个给 YAML 片段与 Use when/Avoid when 判据。配套 `subagents.md:7` 给出组合公理："Any agent defined under `functions:` can be referenced by name in another agent's `tool_names`, `branches`, or `tool_list`"——agent 即工具，层级组合由此展开；`subagent-patterns.md` 落成四模式：Router 分流（L7）、Reasoning 包裹（L64）、并行扇出（L96）、顺序流水线（L152）。

### 元技能：skill-evolution 预编辑门

`skills/skill-evolution/SKILL.md:3` 触发条件是元层面的："Use before creating, editing, or deciding whether to update any AI coding agent skill"。AGENTS.md:67-71 把它钉成硬门：改 `skills/` 下任何文件前必先读 skill-evolution，不得跳过直接编辑目标 skill（AGENTS.md:69）。它定义何时更新（用户纠正且可泛化、命令失败且恢复值得记、参考过时——SKILL.md:12），怎么更新（SKILL.md:25-32 六步：先完成用户任务、找最小受影响 skill、SKILL.md 保持简洁、长材料移入 references/、**新增 skill 或路由变化必须同步 AGENTS.md**（SKILL.md:31）、跑链接检查），以及质量线（SKILL.md:63："Skills should tell agents what to do, what to read next, and what to validate"，偏好指向仓库权威文档而非复制长文）。

## 三、外部连接

**与 docs/source 双轨**：skill-evolution 的 Quality Bar（SKILL.md:63-68）明言 "Prefer canonical repository docs over copied long-form explanations"——技能层是路由与判据层，链接而非复制人类文档；docs/source/components/ 是组件规范文档。**与 CI 连接**：nat-path-checks 存在的唯一理由是把 `ci/scripts/path_checks.py` 的失败输出翻译成修复决策——SKILL.md:3 点名该脚本，SKILL.md:24 的 Fix Decision Table 是八行语义分类表（如散文缩写 `pass/fail` 改写成 "pass or fail"、CLI 字面量 `tools/list` 包 inline code），SKILL.md:37 的 Important Distinctions 给总纲："斜杠 token 不是要被逐字复制就改写成散文；要被逐字复制就放进代码；指向真实文件就修目标而不是转义"；验证命令在 SKILL.md:45。**与 CLI 连接**：多个 skill 第一步都是 `nat info components -t <type>`，消费的正是适配器包安装期写进 `nat.components` 组的注册成果。**与 pre-commit 连接**：skill-evolution L32 要求改 skill 后跑链接检查，把技能维护纳入现有审查基础设施。

## 四、数据流：AI 代理接到任务后的技能路由路径

以"给这个 workflow 换个更合适的 agent"为例：

1. **入口判定**：代理读 AGENTS.md，Task Routing 表 L55 命中 "Choosing or configuring agents → skills/nat-agent-configuration/SKILL.md"；
2. **门禁检查**：本任务不改 skills/，预编辑门不触发；若任务是"加一个新 skill"，必须先绕道 skill-evolution/SKILL.md；
3. **加载手册**：nat-agent-configuration/SKILL.md L12 的 Workflow 给四步心法（先分类 workflow 形态、优先内置组件、子 agent 作工具、小评测集验证）；
4. **下钻参考**：按 L19 进 references/agents.md，L7-9 分类法判定"研究/分析/决策类 → agent"，L13-19 表格比选候选；
5. **事实校验**：写 YAML 前按 nat-user-rules/SKILL.md:12 跑 `nat info components -t function` 核实 `_type` 与配置键，禁止凭记忆；
6. **组合扩展**：需要多 agent 时查 subagents.md L7 公理与四模式；
7. **验证收尾**：小 config 跑通；若教训可泛化，任务完成后回 skill-evolution 决定是否写回 agents.md。

本质是**把 LLM 的自由推理约束成有限跳数的路由**：每跳有明确下一步指针（what to read next）与验证动作（what to validate）。

## 五、设计决策

**为什么入口是 AGENTS.md。** 它是 coding agent 生态的事实约定（代理启动自动读仓库根该文件），NAT 把它做成纯路由层：15 行任务表不掺教程，长知识全部下沉 skill——入口 token 预算最小，代理冷启动成本恒定。

**为什么扁平布局。** skill-evolution SKILL.md:34-46 规定 `skills/nat-*/SKILL.md + references/` 两层结构，禁更深嵌套。扁平让 Task Routing 表一行一个 skill 全量枚举，路由 O(1)；嵌套树要求先理解目录语义才能定位。

**为什么预编辑门是元技能。** AGENTS.md:69 括号说得很直白："don't jump directly to editing a named target skill without consulting skill-evolution"。技能体系本身会腐烂（参考过时、路由漂移），把"如何改技能"也做成技能且排在任何编辑前——给知识库装抗熵机制；L31 强制路由与清单同步，防单一事实源分裂。

**为什么把 CI 知识做成 skill。** nat-path-checks 是"工具型 skill"模板：CI 失败输出是机器生成、高度重复的，但**修复决策需要语义分类**（这个斜杠 token 是散文还是字面量还是真实路径）。八类决策固化成表（SKILL.md:24），代理从"猜着修"变"查表修"——比每次重读 path_checks.py 省一个数量级 token，比放任乱改 allowlist 稳。

## 六、新人提示

贡献前先假装代理走一遍路由：读 AGENTS.md → 查表进 skill → 下钻 references，这条链就是仓库真正的贡献者指南。三个提醒：改任何 `skills/` 文件前先读 skill-evolution/SKILL.md，跳过会被 review 打回；skill 内容与源码冲突时以源码为准——如 references/agents.md L3 说 "nine built-in agent types"，逐个数 langchain 包会见到七种 agent + 两种 executor 的口径差（L13-19 表格），引用前自行核实；想理解这套体系的工程价值，读 nat-path-checks/SKILL.md 全文 54 行——最小却完整示范"重复决策固化为查表、CI 噪声翻译为语义修复"。复制这套设计的最小集 = AGENTS.md 路由表 + 三五个分域 SKILL.md + references/ + 一个 skill-evolution 预编辑门。
