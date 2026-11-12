# 02 · SKILL.md 正本、三平台变体与同步器（方法核心引擎）

> 对应图谱 L3「技能定义主文件」，tour t03。核心文件：`skills/planning-with-files/SKILL.md`（正本，242 行）、`.agent/` `.factory/` `.kilocode/` 三变体、`scripts/sync-ide-folders.py`（同步器）。

## ① 角色定位

SKILL.md 是整个项目的**方法引擎与宪法**：模型何时触发（description）、可用哪些工具（allowed-tools）、harness 何时强制注入什么（hooks）、全部行为规则（正文 14 节）。正本 skills/planning-with-files/SKILL.md 以 Claude Code 插件形态分发；16 个平台各持一份变体，图谱收录的 `.agent`/`.factory`/`.kilocode` 三份代表三种分化形态。`scripts/sync-ide-folders.py` 是防止变体腐化的同步器——但**刻意永不同步 SKILL.md 本身**。

## ② 内部结构

正本 frontmatter 五段（skills/planning-with-files/SKILL.md:1-27）：name/description（触发条件 skills/planning-with-files/SKILL.md:3：plan out/break down/organize 或 >5 tool calls）；`user-invocable: true`（skills/planning-with-files/SKILL.md:4）；`allowed-tools: "Read, Write, Edit, Bash, Glob, Grep"`（skills/planning-with-files/SKILL.md:5，无 WebFetch/WebSearch——安全修复见⑥）；内挂四组 hooks（skills/planning-with-files/SKILL.md:6-24，详见第 6 篇）；metadata version 2.23.0（skills/planning-with-files/SKILL.md:26）。

正文骨架：FIRST: Restore Context——先读三件套+跑 session-catchup（skills/planning-with-files/SKILL.md:33-54）；Where Files Go——规划文件在用户项目目录而非技能目录（skills/planning-with-files/SKILL.md:56-64）；Quick Start 五步（skills/planning-with-files/SKILL.md:66-76）；**Critical Rules 七条**（skills/planning-with-files/SKILL.md:95-137）——含 2-Action Rule（skills/planning-with-files/SKILL.md:100-103，每 2 次 view/browser 操作必须回写 findings）、Read Before Decide（skills/planning-with-files/SKILL.md:105-106）、Never Repeat Failures（skills/planning-with-files/SKILL.md:125-130，`next_action != same_action`）、Continue After Completion（skills/planning-with-files/SKILL.md:132-137，v2.23.0 新增）；3-Strike 协议（skills/planning-with-files/SKILL.md:138-160：修复→换法→重思→升级用户）；**Read vs Write 决策矩阵**（skills/planning-with-files/SKILL.md:162-172，"Just wrote a file → DON'T read"）；5-Question Reboot Test（skills/planning-with-files/SKILL.md:173-183）；When to Use/Skip（skills/planning-with-files/SKILL.md:185-197）；Security Boundary（skills/planning-with-files/SKILL.md:220-228）；Anti-Patterns 八条（skills/planning-with-files/SKILL.md:230-241）。

**三变体分化**：`.agent` 版最精简——frontmatter 仅三行（.agent/skills/planning-with-files/SKILL.md:1-5），零 hooks，正文以 Core Principle 开头（.agent/skills/planning-with-files/SKILL.md:11）；`.kilocode` 版与正本几乎逐字，仅 Stop 钩子根变量换成 `KILOCODE_SKILL_ROOT`（.kilocode/skills/planning-with-files/SKILL.md:24，对照正本 skills/planning-with-files/SKILL.md:24）；`.factory` 版无 hooks frontmatter，正文却最全——独有 Read vs Write 决策矩阵（.factory/skills/planning-with-files/SKILL.md:98）与 5-Question Test（.factory/skills/planning-with-files/SKILL.md:123），含错误表示例（.factory/skills/planning-with-files/SKILL.md:59-66）。

## ③ 外部连接

SKILL.md 是纯枢纽：引三模板（skills/planning-with-files/SKILL.md:203-205）、三脚本（skills/planning-with-files/SKILL.md:211-213）、reference.md/examples.md（skills/planning-with-files/SKILL.md:217-218）；四组 hooks 运行时调 `${CLAUDE_PLUGIN_ROOT}/scripts/` 下的 check-complete（skills/planning-with-files/SKILL.md:24）。变体↔正本的关系由 `scripts/sync-ide-folders.py` 定义：CANONICAL 源=skills/planning-with-files（scripts/sync-ide-folders.py:29），同步模板/参考/脚本三类共享资产（scripts/sync-ide-folders.py:32-49）；SKILL.md 在 NEVER touches 清单（scripts/sync-ide-folders.py:14-16，"IDE-specific frontmatter differs per IDE"）。13 个 IDE 的 manifest 由 `_build_manifest()` 参数化生成（scripts/sync-ide-folders.py:55-98）：ref_style 分 flat/subdir/skip（.gemini 用 references/ 子目录 scripts/sync-ide-folders.py:109-113；.factory/.agent 用合并版直接 skip scripts/sync-ide-folders.py:163-174），codex/codebuddy 额外拷 assets/templates/（scripts/sync-ide-folders.py:119）；.kiro 是结构完全不同的特例：steering 体系只同步 4 个脚本（scripts/sync-ide-folders.py:182-190）。

## ④ 数据流

触发期：斜杠命令或 description 语义匹配→SKILL.md 全文进上下文→模型按正文建三件套。运行期：hooks 输出（计划头 30 行/提醒/完成度报告）持续注入——SKILL.md 定义的不只是"读什么"，还有"harness 替你复读什么"。发布期：维护者改正本→跑 `python scripts/sync-ide-folders.py` 摊平到 13 目录（--dry-run 预览、--verify 查漂移 exit 1，scripts/sync-ide-folders.py:237-246/:306-310）。

## ⑤ 设计决策与陷阱

- **SKILL.md 不同步是双刃剑**：好处是每平台 frontmatter 可精准适配（根变量/钩子有无）；代价是**正文也在分叉**——.factory 版的决策矩阵、5-Question、错误表示例在 .agent 版全缺（diff 实证），"正本=超集"并不成立——正本 skills/planning-with-files/SKILL.md:162-172 也有决策矩阵，两版各自演化。改规则要逐版核对 7 份 IDE SKILL.md（CHANGELOG.md:11 提到 "all 7 IDE SKILL.md files"）。
- **路径根变量是分叉的根因**：`CLAUDE_PLUGIN_ROOT`（插件缓存）vs `KILOCODE_SKILL_ROOT`（用户目录）vs 硬编码 `~/.kilocode/...`（.kilocode/skills/planning-with-files/SKILL.md:39）——fork 新平台先定自己的根变量。
- **allowed-tools 收紧过**：v2.21.0 移除 WebFetch/WebSearch（docs/article-v2.md:34），现白名单是修复后形态（skills/planning-with-files/SKILL.md:5）；fork 慎加回（放大链见第 6 篇）。
- **.agent 版模板目录反直觉**：模板在 references/ 而非 templates/（scripts/sync-ide-folders.py:172 注释 "custom layout, not synced"）。
- sync 用 SHA-256 幂等可重跑（scripts/sync-ide-folders.py:196-201）；须在仓根执行否则退出（scripts/sync-ide-folders.py:256-259）。

## ⑥ 新人提示

读懂正本（skills/planning-with-files/SKILL.md）后只需精读两处差异：`.kilocode` 根变量替换、`.factory` 正文增料——其余 13 个变体是 frontmatter 微调。改共享内容后必跑 sync-ide-folders.py；改 SKILL.md 正文无同步可依赖，须手工逐版对齐。变体新旧比对该行（正本 skills/planning-with-files/SKILL.md:26 与 .kilocode 同为 2.23.0）。Security Boundary（skills/planning-with-files/SKILL.md:220-228）是 fork 者必读：task_plan.md 会被钩子反复注入，"外部内容只进 findings.md"是红线而非建议。
