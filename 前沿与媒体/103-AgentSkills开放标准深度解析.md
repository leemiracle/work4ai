# Agent Skills 开放标准 · 深度解析与项目落地

> 一句话灵魂：**skill 是"给 agent 的可移植程序性知识"——一个文件夹 + 一份 SKILL.md，经三级渐进披露进入上下文；它正在成为跨 46 个 agent 客户端的事实标准，而 work4ai 恰好站在标准的两端：既是标准的消费者（可把自己的方法论变成 skill），又有全网少见的"harness 源码级 skill 机制笔记"（dsh 案例）。**
>
> 来源：[agentskills.io](https://agentskills.io) 全站 9 页（Overview / Specification / Clients / Quickstart / Best practices / Optimizing descriptions / Evaluating skills / Using scripts / Adding skills support），抓取于 2026-08-14。
> 标准起源：Anthropic 开发并开放，现由社区在 [github.com/agentskills/agentskills](https://github.com/agentskills/agentskills) 演进。

---

## 0. 为什么这个标准值得 work4ai 认真对待

三个事实决定了它的权重：

1. **46 个客户端已采纳**（agentskills.io/clients，2026-08）：Claude/Claude Code、ChatGPT & Codex、GitHub Copilot、VS Code、Cursor、Gemini CLI、OpenCode、Goose、Amp、Roo Code、Kiro、TRAE、OpenClaw、Hermes Agent……连 Spring AI（Java 框架）、Laravel Boost（框架技能包）都入了列。**这不是 Anthropic 的私有格式，是 agent 时代的 "markdown 级" 互操作层。**
2. **与本项目已分析的 dsh 生态互相印证**：dsh-plugin 生态分析（见 [Agent框架案例](../Agent框架案例/deepseek-harness插件化框架/notes/07-ecosystem/01-dsh-plugin生态分析.md)）里头部 skill 包（archify 12.3k 星、colleague-skill 21.9k 星、harmony-next、sealos-skills）**全部跨宿主**——因为 SKILL.md 是数据不是代码。**插件绑生态、skill 绑工作流**，两条曲线已分叉。
3. **标准的哲学与 work4ai 项目宪法同构**：渐进披露 ≈ 本项目"三层宪法"；"从真实专长出发、不许 LLM 空想" ≈ 项目"禁止伪代码、每个论断 bash 可验"；eval 驱动迭代 ≈ 项目 F5 反欺骗质量门。**学这个标准 = 给项目方法论找互操作出口。**

---

## 1. 规范全录（Specification 精确要点）

### 1.1 目录结构

```text
my-skill/
├── SKILL.md          # 必需：元数据 + 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：按需加载的文档
├── assets/           # 可选：模板、资源
└── ...               # 任意附加文件
```

skill = **含 SKILL.md 的目录**。规范只约束内容，**不约束发现位置**（位置是客户端约定）。

### 1.2 frontmatter 字段表（逐字段）

| 字段 | 必需 | 约束 |
|---|---|---|
| `name` | ✅ | ≤64 字符；仅小写字母/数字/连字符；不得首尾连字符、**不得连续连字符**；**必须与父目录名一致** |
| `description` | ✅ | ≤1024 字符；非空；描述"做什么 + 何时用"；应含任务匹配关键词 |
| `license` | ❌ | 许可证名或捆绑许可证文件引用 |
| `compatibility` | ❌ | ≤500 字符；环境要求（目标产品/系统包/网络） |
| `metadata` | ❌ | string→string 任意映射（如 `version: "1.0"`——**规范本身无版本号**，版本只能放这里） |
| `allowed-tools` | ❌ | **实验性**；空格分隔的预批准工具列表，如 `Bash(git:*) Bash(jq:*) Read` |

合法性 vs 非法性 `name` 示例：`pdf-processing` ✅；`PDF-Processing`（大写）❌；`-pdf`（首连字符）❌；`pdf--processing`（双连字符）❌。

### 1.3 三级渐进披露（标准的心脏）

| 层 | 加载什么 | 何时 | token 成本 |
|---|---|---|---|
| 1. 目录（Catalog） | name + description | 会话启动，全部技能 | **~50-100 token/skill** |
| 2. 指令 | SKILL.md 全文 | 激活时 | **<5000 token（推荐）** |
| 3. 资源 | scripts/references/assets | 指令引用时 | 按需 |

配套硬指标：**SKILL.md 保持 500 行以内**。长的内容下沉 `references/`，且必须告诉 agent **何时读哪个文件**（"API 返回非 200 时读 `references/api-errors.md`" 优于泛泛的 "详见 references/"）。

### 1.4 客户端实现要点（Adding-skills-support 精要）

- **发现位置**：项目级 `<project>/.agents/skills/` 与用户级 `~/.agents/skills/` 是**跨客户端互操作约定**（各客户端另有自己的 `.<client>/skills/`）；扫描 = 找子目录里名为 SKILL.md 的文件，跳过 `.git`/`node_modules`，限深 4-6、约 2000 目录。
- **遮蔽规则**：项目级覆盖用户级（普遍约定）；同级冲突须一致地取先见/后见并告警。
- **信任门**：项目级 skill 可能来自不可信仓库——应经用户对项目文件夹的信任标记再加载（防静默提示注入）。
- **激活双路**：模型自主（file-read 或专用 `activate_skill(name)` 工具，name 参数约束为合法技能枚举防幻觉）+ 用户显式（`/skill-name`）。
- **上下文管理**：已激活内容**豁免压缩**（中途丢指令 = 静默退化）；同会话去重；可选子代理隔离执行。
- **空集处理**：无技能则完全不注入目录、不注册空工具。
- **宽容解析**：name/目录不一致→警告但加载；**description 缺失/为空→跳过**（渐进披露的命门就是 description）；YAML 坏→跳过。

---

## 2. 创作方法论（四篇指南的综合）

### 2.1 内容从哪来（Best practices 上半）

**铁律：从真实专长出发，不许 LLM 凭通用知识空想。** 最大坑 = 让 LLM 无上下文生成 skill，产出 "handle errors appropriately" 式的空话。好素材：内部 runbook/事故报告、API spec/schema/配置、code review 评论与 issue、版本历史里的补丁、真实失败案例。"从团队真实事故报告合成的数据管道 skill 必胜从通用文章合成的"——**项目特定材料 > 通用参考**。

**用真实执行回流**：跑真实任务，把全部结果（不只失败）喂回创作；**读执行轨迹而非只读最终输出**；一轮"执行-修订"就明显提质，复杂领域多轮。

### 2.2 上下文经济学（Best practices 中段）

- 每条内容过筛："**没有这条指令 agent 会做错吗？**" 不会→删。agent 本来就做得好的任务，skill 不增值。
- **内聚单元**：划分 skill 像划分函数——太窄→一个任务触发多个 skill（开销+指令冲突）；太广→触发不精确。查询+格式化=内聚；+DB 管理=过载。
- **适度细节**：简洁分步 + 一个可运行示例 > 面面俱到的文档；边界情况多数交给 agent 自己的判断。
- **校准控制粒度**：指令的具体度匹配任务的脆弱度——多种做法皆可时给自由（讲 *为什么* 优于死板规定）；操作脆弱/顺序敏感时**精确到命令**（"运行恰好这个序列，不要改命令不要加 flag"）。多数 skill 是混合体，**逐段独立校准**。
- **给默认不给菜单**："可以用 A、B、C、D…" ❌；"用 A（默认）；扫描件需 OCR 时改用 B" ✅。
- **教方法不教答案**：教"如何approach一类问题"，不是"这个实例产出什么"。例外：输出模板、"永不输出 PII"类约束、工具特定指令。

### 2.3 六大内容模式（可直接套用）

| 模式 | 用法 | 要点 |
|---|---|---|
| **Gotchas 清单** | 环境特有、违反合理假设的事实 | 多数 skill 的最高价值内容；放 SKILL.md 正文（agent 需在遭遇情境**前**读到）；agent 犯错被纠正时→把纠正加进来 |
| **模板** | 输出格式 | agent 对具体结构 pattern-match 极好；短模板内联、长模板入 assets/ |
| **检查单** | 有依赖/验证门的多步任务 | 帮 agent 跟踪进度、防跳步 |
| **验证循环** | 做→跑验证器→修→直到通过 | 验证器可以是脚本、参考检查单或自检 |
| **计划-验证-执行** | 批量/破坏性操作 | 先产结构化中间计划→对事实源验证→才执行；验证脚本的报错要给足自纠信息 |
| **捆绑脚本** | agent 每次重造同样的轮子时 | 写一次测好的脚本入 scripts/；这是"发现该写脚本"的信号 |

### 2.4 description 触发优化（Optimizing-descriptions 精要）

description **独自承担全部触发负担**（启动时只有它在上下文）。四原则：**祈使句**（"Use when…" 而非 "This skill does…"）；**对用户意图**而非实现；**宁 pushy 勿 shy**（显式列出适用语境，含用户没点名的："即使他们没明说 CSV 或 analysis"）；**简洁**（几句到一小段）。

**评测驱动优化协议**（数字全录）：

- 评测集 ~**20 条查询**：8-10 应触发 + 8-10 **近失不应触发**（共享关键词但实际要别的——"更新 Excel 预算公式"对 CSV 分析 skill 是强负例，"写斐波那契"是弱负例测不出东西）。
- 每条跑 **3 次**算**触发率**，阈值 **0.5**；总计 ~60 次调用，要脚本化、结果明确即提前停。
- **训练/验证 6:4 分割**（随机打散、固定、跨迭代不变）——只对训练集诊断失败，**禁止把失败查询的特定关键词塞进 description（= 过拟合）**，要归纳到一般类别。
- 迭代约 **5 轮**足够；**按验证集通过率选最优**（未必是最后一轮）；上线前用 **5-10 条全新查询**做出诚实检验；全程盯 **1024 字符上限**（description 在优化中倾向于膨胀）。

### 2.5 输出质量评测（Evaluating-skills 精要）

**A/B 基线协议**：每条测试用例跑两次——**带 skill / 不带 skill**（或旧版快照）；干净上下文起跑（子代理天然隔离）；记录 token 与时长（**改进但 3 倍 token** 与**又好又便宜**是不同的交易）。

**断言纪律**：好断言可程序验证/可观察/可计数；坏断言模糊（"输出是好的"）或脆断（逐字匹配）；**PASS 必须有具体证据**——"有个叫 Summary 的标题但只有一句空话 = FAIL（标签在、实质不在）"；首轮跑完再写断言（跑之前你不知道"好"长什么样）。

**模式分析五步**：删双配置全过的断言（虚增通过率）→ 查双配置全败的（断言坏/测太难/查错东西）→ **研究"带 skill 过、不带败"的断言——skill 的真实价值所在** → 高方差异→收紧指令降歧义 → 3 倍时长离群→读轨迹找瓶颈。

**迭代停止条件**：满意 / 反馈持续为空 / 迭代间不再有有意义改进。LLM 提改的元原则：从反馈归纳一般化修复（不打窄补丁）、**保持精瘦**（通过率停滞时试着**删**指令）、讲为什么（"做 X 因为 Y 常导致 Z" > "ALWAYS/NEVER"）、重复劳动捆成脚本。

---

## 3. 与 dsh skill 机制的对照（项目已有知识的再利用）

work4ai 的 [dsh 插件机制笔记](../Agent框架案例/deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md) §10 已源码级解剖 dsh 的 skill 实现，两者对齐如下：

| 维度 | agentskills.io 开放标准 | dsh 实现（源码验证） | 评价 |
|---|---|---|---|
| 本体 | SKILL.md + frontmatter（name/description 必需） | 相同 + 可选 `whenToUse`/`metadata`/`disable-model-invocation`/`user-invocable` | dsh **超集**：调用策略是类型化双面（modelInvocable/userInvocable 四组合） |
| 发现 | `.agents/skills/` 跨客户端约定 + 各客户端自有 | provider 注册表（`ctx.skills.registerProvider`，ScopedLayers 形状、preset 分层就近遮蔽） | 标准管**内容**、dsh 管**供给**——文件系统只是 dsh 的一个 provider |
| 渐进披露 | 三层（目录/指令/资源） | 相同三层：`<skill_content>` 目录块按 **digest 变更**才重发布（防刷屏）；`skill(name=…)` 拉全文；`/<name>` 用户手势 | dsh 加了 **durable 会话目录**（catalog 本身入会话日志）——比标准多一层可审计性 |
| 与插件关系 | （标准不涉及） | "skill 是**数据**不是代码，从不在运行时执行；插件是代码" | dsh 三分法：**插件（代码）> hook（外部进程）> skill（数据）**——标准只覆盖第三层 |
| 安全 | 信任门建议（项目级需用户信任标记） | skill 无执行面（天然低危）；真正执行面在插件层（bash 等价信任 + allowBuilds 白名单） | 标准的 `allowed-tools`（实验性）是在给"数据型 skill"补执行语义——走向 dsh 插件已解决的问题 |
| 触发 | description 独扛 | 相同；`whenToUse` 是 dsh 的补充字段 | dsh 等待标准演化的同时自带了扩展位 |

**结论**：dsh 的 skill 子系统可以视为开放标准的一个**工业化超集实现**——它把标准里"建议级"的东西（去重、digest 防刷、审计、调用策略类型化）做成了机制。反向看，标准之所以只约束 SKILL.md 内容而不约束位置和实现，正是为了让 dsh 这类宿主保留自己的供给层。

---

## 4. 对 work4ai 的落地评估与行动清单

### 4.1 现状盘点（诚实）

- 项目内已有 **1 个合规 skill**：[`费曼学习法/skill/SKILL.md`](../费曼学习法/skill/SKILL.md)（`feynman-check`）。对照规范逐项审计：
  - ✅ name 合规（小写+连字符、与语义一致）；description 含"做什么+何时用+触发词"；正文 128 行（<500）；分层结构（何时触发/两套工具/检验表）符合"检查单+模板"模式。
  - ⚠️ **目录名 ≠ name**：目录叫 `skill`，name 是 `feynman-check`——违反"必须与父目录名一致"。**修复动作：目录改名 `feynman-check/`。**
  - ⚠️ description 的 "Triggers: …" 关键词堆叠正是 2.4 节警告的**过拟合式写法**——按四原则重写为意图导向（祈使句、宁 pushy、含未点名场景），再用 20 查询评测协议验证。
- 大量方法论（三层宪法、欺骗动力学检测 Prompt 库、视角库、质量门）**具备 skill 化潜质但尚未打包**。

### 4.2 候选 skill 清单（按价值排序）

| 候选 | 来源 | 为什么值得 | 类型 |
|---|---|---|---|
| `dsh-case-audit` | dsh 案例笔记的"验证命令"模式 | 教 agent"对任何 repo 做行号钉版审计"：Select-String 复核、HEAD 记录、行号漂移检查——本项目已验证的方法论 | 方法型 |
| `feynman-check`（升级） | 已有 | 补 evals/（2-3 用例 + 断言）；description 重写 | 质量门型 |
| `anti-deception-review` | 欺骗动力学-检测Prompt库 | 把 D1-D4 检测变成 agent 可执行审查流程 | 方法型 |
| `bilingual-doc-pairing` | dsh i18n 三件套笔记 | 教 agent 维护 md/zh.md/i18n.yaml 三件套一致性 | 流程型 |
| `case-notes-writer` | Agent 案例目录约定 | 分层笔记结构（定位/深读/教训/诚实声明）作为模板 | 模板型 |

### 4.3 与项目宪法的映射（标准方法论 ≈ 项目既有原则）

| agentskills.io 原则 | work4ai 对应 |
|---|---|
| "从真实专长出发，不许 LLM 空想" | "禁止伪代码，每个论断 bash 可验" |
| 渐进披露三级 | 三层宪法（直觉→数学→代码跑通）的上下文版 |
| "没有这条指令 agent 会做错吗" | 文档预算/一词一句有据（反虚荣） |
| eval 驱动迭代 + 触发率阈值 | F5 反欺骗质量门（证据可验） |
| 断言须有具体证据才 PASS | 每条论断给行号 + 审计命令 |
| 诚实记录（弱负例测不出东西） | 自曝 gap（F2 反自我欺骗） |

**洞察**：work4ai 的方法论与该标准是**同构**的——前者面向人类学习者，后者面向 agent。把项目方法论 skill 化不是改造成别的东西，而是**同一套原则换一个运行时**。

### 4.4 行动清单

1. **立即可做**：`费曼学习法/skill/` → `费曼学习法/feynman-check/`（目录名对齐）；按 2.4 重写 description。
2. **短期**：为 `feynman-check` 建 `evals/evals.json`（2-3 用例 + 可数断言），跑一次带/不带 A/B。
3. **中期**：把 §4.2 前两个候选做成合规 skill，放 `.agents/skills/`（跨客户端互操作位置）。
4. **知识接线**：本文档作为"标准参考页"挂进 dsh 案例笔记（skill 机制节）与生态分析（skill 赛道节）的交叉引用。

### 4.5 生态与趋势判断

- **46 客户端里没有 DeepSeek Harness**——但 dsh 源码证实其 skill 子系统兼容此格式（skill-filesystem provider 读 SKILL.md frontmatter）。dsh 未上榜更可能因为 developer preview 而非不兼容。
- **`allowed-tools`（实验性）是标准最有想象力的演化方向**：给数据型 skill 加执行语义，等于向 dsh"插件>hook>skill"金字塔的中间层靠拢。work4ai 跟踪此字段即可预判标准走向。
- **skill 是 agent 时代的"README 时刻"**：当年 README.md 让任何项目在任何平台可被理解；SKILL.md 让任何工作流在任何 agent 可被执行。work4ai 的"讲透 X"系列天然是这个标准的优质素材库。

---

## 📌 导航

- 上游标准：[agentskills.io](https://agentskills.io) ｜ [规范](https://agentskills.io/specification) ｜ [GitHub](https://github.com/agentskills/agentskills)
- dsh skill 机制源码级笔记：[`Agent框架案例/deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md`](../Agent框架案例/deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md) §10
- 生态中 skill 赛道分析：[`Agent框架案例/deepseek-harness插件化框架/notes/07-ecosystem/01-dsh-plugin生态分析.md`](../Agent框架案例/deepseek-harness插件化框架/notes/07-ecosystem/01-dsh-plugin生态分析.md) §2.2
- 项目内首个 skill：[`费曼学习法/skill/SKILL.md`](../费曼学习法/skill/SKILL.md)
---
