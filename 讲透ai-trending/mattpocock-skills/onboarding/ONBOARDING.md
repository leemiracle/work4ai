# mattpocock/skills 上手指南（ONBOARDING）

> 仓库：`/usr-data/data2/repos/ai-trending/skills`（mattpocock/skills @ e3d8b73，74 个功能文件）
> 性质：Matt Pocock（Total TypeScript/AI Hero 作者）日常使用的 agent skills 库——Claude Code 插件 `mattpocock-skills`，口号 "Skills For Real Engineers"（`README.md:11`）：给真做工程的人用，不是 vibe coding。
> 图谱：76 节点/137 边（11 批），批产物在仓内 `.understand-anything/intermediate/`。

## 1. 库定位与分发机制

仓库回答：**当编码 agent 接管大量写码后，老派工程纪律（对齐/领域语言/反馈环/模块设计）如何装回 agent 工作流？** README 以"四大失败模式"组织全部 skill（`README.md:44`）：①没懂我要什么→grilling；②太啰嗦→共享语言；③代码不工作→反馈环；④烂泥球→关注设计——思想引自《The Pragmatic Programmer》《DDD》《A Philosophy of Software Design》《XP Explained》（`README.md:48`）。

分发走三条通道：

1. **skills.sh 安装器**（对外主通道）：`npx skills@latest add mattpocock/skills`（`README.md:30`），**必须选 `/setup-matt-pocock-skills`** 做每仓初始化（`README.md:33`）。
2. **插件清单**：`/usr-data/data2/repos/ai-trending/skills/.claude-plugin/plugin.json:2` 名为 `mattpocock-skills`，列 15 个目录（engineering 10+productivity 5）。**勘误：misc 4 个不在清单**，与 `CLAUDE.md:10` 自述矛盾，以实文件为准。
3. **本地软链**：`/usr-data/data2/repos/ai-trending/skills/scripts/link-skills.sh:26` find 全仓 SKILL.md（排除 deprecated）软链到 `~/.claude/skills/`，带防自指保护（L13-22）。

## 2. skills 分类地图

skills/ 下六桶（`CLAUDE.md:1-8`），生命周期即分类：

| 桶 | 数量 | 定位 | 进插件？ |
|---|---|---|---|
| engineering | 10 | 日常代码工作 | 是 |
| productivity | 5 | 日常非代码工作流 | 是 |
| misc | 4 | 保留但少用 | **实况：否**（勘误见上） |
| personal | 2 | 绑定作者本人环境 | 否 |
| in-progress | 4 | 草稿孵化区 | 否 |
| deprecated | 4 | 已弃用化石 | 否 |

每桶一个 README 索引（如 `skills/engineering/README.md:5-14`）。桶纪律由 `CLAUDE.md:10` 强制：公开三桶必进顶层 README+plugin.json，私人三桶两处不得出现。

工程桶内部成协作网：`setup` 是配置源点（硬依赖者 to-issues/to-prd/triage，见 `docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md:7-8`）；`grill-with-docs` 生产文档，improve-codebase-architecture/tdd/diagnose/zoom-out 消费。

## 3. 工程类技能解剖

**旗舰 `/grill-with-docs`**：无情访谈（一次一问、附推荐答案、代码库能答自己查 L12）+域感知——术语冲突当场点名（L58）、模糊词收敛（L62）、陈述与代码对质（L70）、术语解决内联写盘（L74）、ADR 三条件齐备才提议（L80-84）。格式契约两份：`skills/engineering/grill-with-docs/ADR-FORMAT.md:15`（单段落即合法）与 CONTEXT-FORMAT.md（L12-19，术语+定义+_Avoid_）。

**架构救援 `/improve-codebase-architecture`**：找"深化机会"（shallow→deep，`skills/engineering/improve-codebase-architecture/SKILL.md:8`）。词汇宪法 `skills/engineering/improve-codebase-architecture/LANGUAGE.md:7` 定八术语（Module/Interface/Depth/Seam/Adapter/Leverage/Locality），四原则（删除测试/接口即测试面/两适配器才立缝/深度是接口属性，L36-39），否决 Ousterhout 行数比（L51）。产出=系统临时目录的 Tailwind+Mermaid HTML 报告（L51）；`skills/engineering/improve-codebase-architecture/DEEPENING.md:9-26` 依赖四分类；跨目录复用 grill-with-docs 格式文档（SKILL.md L78 引 `../grill-with-docs/CONTEXT-FORMAT.md`）。

**质量双环**：`/tdd` 封杀"水平切片"（`skills/engineering/tdd/SKILL.md:20`），正道 tracer bullet 垂直切片（L29）、GREEN 后才 refactor（L99）；mocking 只许在系统边界（`skills/engineering/tdd/mocking.md:3`）。`/diagnose` 六阶段，Phase 1 宣示 "**This is the skill.**"（`skills/engineering/diagnose/SKILL.md:14`），10 种反馈环手段（L18-29），追 2 秒确定性环（L41）。

**工作流三件套**：`/to-prd` 合成 PRD（明确**不访谈**，`skills/engineering/to-prd/SKILL.md:6`）；`/to-issues` 拆垂直切片 issue（HITL/AFK 二分，`skills/engineering/to-issues/SKILL.md:26`）；`/triage` 状态机分诊（`skills/engineering/triage/SKILL.md:23-34`），AI 评论强制免责声明（L10-14）。另有极简 `/zoom-out`（正文一段，`skills/engineering/zoom-out/SKILL.md:7`）与双分支 `/prototype`（逻辑 TUI/外观多变体，`skills/engineering/prototype/SKILL.md:14-15`）。

## 4. 生产力类技能

productivity 桶五个 skill 全非代码向：

- **`/teach`**：最重的（113 行）——当前目录变有状态教学工作区，六载体（`skills/productivity/teach/SKILL.md:14-19`）；知识+技能+智慧三层，"绝不信任参数化知识"（L29）；learning-records 是 ADR 的教学移植（L17），驱动最近发展区（L55-65）。
- **`/grill-me`**：grill-with-docs 的 10 行原点（`skills/productivity/grill-me/SKILL.md:6`）。
- **`/caveman`**：超压缩模式省 ~75% token（`skills/productivity/caveman/SKILL.md:10`，正文本身即 caveman 语体——形式即示范）；自动清晰例外（L37-39）。
- **`/handoff`**：交接文档写 OS 临时目录、敏感信息必脱敏（`skills/productivity/handoff/SKILL.md:13`）。
- **`/write-a-skill`**：元技能——description 是 agent 选技能唯一信号，必须含 "Use when [触发词]"（`skills/productivity/write-a-skill/SKILL.md:62-74`）。

misc 桶是工具箱：git-guardrails（hook 拦危险 git）/migrate-to-shoehorn（自家 TS 测试库）/scaffold-exercises（课程脚手架）/setup-pre-commit（Husky 安装器）。

## 5. 设计模式共性（SKILL.md 结构范式）

29 个 SKILL.md 高度同构（write-a-skill 是显式成文，`skills/productivity/write-a-skill/SKILL.md:39-58` 模板）：

1. **frontmatter 契约**：name+description（≤1024 字符、第三人称、第二句 "Use when…"）；可选 disable-model-invocation（仅显式触发）与 argument-hint。
2. **渐进披露**：重内容下沉到同目录大写命名参考文档（ADR-FORMAT/LANGUAGE/LOGIC/UI/AGENT-BRIEF…），"References one level deep"（L116）；正文两种组织法：标题分节（tdd/diagnose）与 XML 标签 `<what-to-do>/<supporting-info>`（`skills/engineering/grill-with-docs/SKILL.md:6,16`、writing-* 系列）。
3. **确定性操作配脚本**：diagnose 带 hitl-loop.template.sh（step/capture 两助手，`skills/engineering/diagnose/scripts/hitl-loop.template.sh:17,22`），git-guardrails 带 block-dangerous-git.sh。
4. **防过时写作纪律**：agent brief 禁文件路径行号（`skills/engineering/triage/AGENT-BRIEF.md:13-14`），to-issues 同禁（唯一例外=原型决策密集片段，`skills/engineering/to-issues/SKILL.md:67`）。
5. **词汇表驱动**：CONTEXT-FORMAT/LANGUAGE/GLOSSARY-FORMAT 三处同构的"术语+定义+_Avoid_"三元组（`skills/productivity/teach/GLOSSARY-FORMAT.md:14-17` 可对照）。

## 6. docs 与 scripts 支撑

**docs/adr/**：自举证据——ADR-0001 定"仅硬依赖技能写显式 setup 指针"（`/usr-data/data2/repos/ai-trending/skills/docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md:7-8`），10 行全文即 "单段落 ADR" 范式的自我示范。

**.out-of-scope/**：被拒特性知识库（OUT-OF-SCOPE.md 机制的活实例），三记录各附 issue 先例：tracker 限主流（#99，`.out-of-scope/mainstream-issue-trackers-only.md:25`）、grilling 不设上限（#44）、setup 不加 verify（#106）。

**CONTEXT.md**：仓库自用术语表（Issue tracker/Issue/Triage role+backlog 歧义消解，`CONTEXT.md:25`）——README 称共享语言"全库最酷"（`README.md:91`），作者用自家机制治自家仓。

**scripts/**：link-skills.sh（分发）+list-skills.sh（清单对账 `scripts/list-skills.sh:7`；两者排除口径不同：后者不排除 deprecated）。

**deprecated/ 四化石**：ubiquitous-language→grill-with-docs（批式提取→内联沉淀）；design-an-interface→INTERFACE-DESIGN.md；qa→triage。`deprecated/qa/SKILL.md:26` 仍引用旧名 UBIQUITOUS_LANGUAGE.md——文字化石。

## 7. 扩展点

- **加新 skill**：建 `skills/<bucket>/<name>/SKILL.md`，公开桶需同步三处（顶层 README/桶 README/plugin.json，`CLAUDE.md:10`；注意 misc 实况缺席 plugin.json）。
- **接新 issue tracker**：在 setup 桶加 issue-tracker-<name>.md 并在 SKILL.md L40-45 登记——但非主流工具会被 `.out-of-scope/mainstream-issue-trackers-only.md` 拒（每个后端=永久维护面）。
- **定制 triage 角色**：五 canonical 角色是协议常量，映射在目标仓 docs/agents/triage-labels.md（种子 `skills/engineering/setup-matt-pocock-skills/triage-labels.md:5-11` 右列可改）。
- **孵化新写作技能**：in-progress 桶是官方试验田（`skills/in-progress/README.md:3`），写作三件套 fragments→beats→shape 在此孵化。
- **fork 自用**：README 明示 "Hack around with them. Make them your own."（`README.md:19`）——设计为可拆装小组件而非接管流程的框架（对 GSD/BMAD/Spec-Kit 的批评 L17）。

## 8. 新人上手

1. **5 分钟理解论**：只读 `README.md:42-141` 四节失败模式，读完即懂全库地图。
2. **30 秒安装**：`npx skills@latest add`→勾 setup→目标仓跑 `/setup-matt-pocock-skills` 三决策（`skills/engineering/setup-matt-pocock-skills/SKILL.md:36-68`）。
3. **第一次实战**：改动前先 `/grill-me`（代码仓 `/grill-with-docs`）——README 称其"最热门，每次改动都该用"（L61）。
4. **读源码顺序**：grill-with-docs/SKILL.md→CONTEXT-FORMAT.md→LANGUAGE.md（词汇密度最高）→tdd→diagnose。
5. **避坑**：①plugin.json 无 misc 四件套；②write-a-skill 的 100 行规范与存量不符（setup 121/diagnose 117/teach 113/自身 117/triage 103 均超）——指导非门槛；③README quickstart 提 Linear（L36）而 setup 实际枚举 GitLab（L42-45），Linear 仅在 other 路径——以 SKILL.md 为准。
6. **一句话总评**：这是一套把对齐/语言/反馈/设计成本显式化的工程操作系统——每个 skill 都是某本经典的一个可执行章节。

*生成：understand-anything 流水线 · 2026-11-02 · 图谱 76n/137e · 锚 44 处（全部行号经 sed 现场核验；锚格式=仓根相对路径或 L 紧跟全路径上下文）*
