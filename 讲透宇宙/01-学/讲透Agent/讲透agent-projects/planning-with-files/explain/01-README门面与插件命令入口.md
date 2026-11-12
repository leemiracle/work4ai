# 01 · README 门面、插件清单与斜杠命令入口（仓库第一印象层）

> 对应图谱 L1「项目门面与元文档」+ L2「斜杠命令入口」，tour t01/t02。锚点全部从源码核实（v2.23.0，commit 快照 2026-03-16）。

## ① 角色定位

这一组文件是仓库的"门面+入口"三层：`README.md` 是 27.7k★ 项目唯一的销售文档与方法总览；`.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json` 是 Claude Code 插件市场的分发元数据（机器读的身份证）；`commands/` 下三份 markdown 是用户交互最外层——斜杠命令的定义体。三者合起来回答"这是什么、怎么装、怎么触发"。

值得先说清定位：README.md:124 给出自我定义——"A Claude Code plugin that transforms your workflow to use persistent markdown files"，即**方法本体不足 10 个文件，其余全是平台适配工程**；README.md:186 用 "Meta acquired Manus for $2 billion" 的叙事做钩子，方法的合法性来自 Manus 上下文工程（引语见 README.md:188）。

## ② 内部结构

**README.md**（383 行）是折叠区块式结构：作者公告（README.md:12-18）、社区 fork 展示表（README.md:23-28，含 devis/multi-manus-planning/plan-cascade 等 4 个衍生品）、版本亮点表（README.md:44-64）、Session Recovery 说明（README.md:68-83）、16 平台支持矩阵（README.md:88-105）、BoxLite 沙箱区（README.md:114-118）、Quick Install（README.md:144-146 的 `npx skills add`）、Problem/Solution 叙事（README.md:191-217，RAM/Disk 隐喻在 README.md:213-216）、Manus Principles 对照表（README.md:219-227）、Benchmark 结果表（README.md:248-259）、Key Rules 四条（README.md:261-266）、目录树（README.md:281-352）。

**plugin.json** 是标准插件清单：版本 2.23.0（.claude-plugin/plugin.json:3）、一句兼容性描述（.claude-plugin/plugin.json:4 "Works with Claude Code, Kiro, Clawd CLI, Gemini CLI, Cursor, Continue, and 11+ AI coding assistants"）、19 个 keywords（.claude-plugin/plugin.json:11-30，含 clawd/kiro-steering 等引流词）。**marketplace.json** 更薄：单插件条目指向仓根（.claude-plugin/marketplace.json:10 `"source": "./"`）。

**commands/ 三件**厚薄悬殊：`plan.md` 全文 13 行——frontmatter 一句 description（commands/plan.md:2）+ 正文"Invoke the skill and follow it exactly"（commands/plan.md:5）加建三文件清单（commands/plan.md:7-10）；`start.md` 最薄，仅 6 行，且 frontmatter 带 `disable-model-invocation: true`（commands/start.md:3）——禁止模型自动调用，只许用户显式触发；`status.md` 反而最厚（49 行），是唯一带输出格式规范的命令：5 项展示内容（commands/status.md:9-13）、状态图标映射（commands/status.md:17-20）、ASCII 输出模板（commands/status.md:24-37）与"Keep It Brief"原则（commands/status.md:47-49）。

## ③ 外部连接

- README → docs/ 全家桶：安装指 docs/installation.md（README.md:182）、快速上手指 docs/quickstart.md（README.md:246）、评测指 docs/evals.md（README.md:259 徽章与链接）；16 平台矩阵每行链到对应分册。
- commands → skill：plan.md/start.md 的第一指令都是 "Invoke the planning-with-files:planning-with-files skill"（commands/plan.md:5、commands/start.md:6），即命令层是薄壳，真正的方法引擎在 `skills/planning-with-files/SKILL.md`（本系列第 2 篇）。
- plugin.json/marketplace.json → Claude Code 插件系统：用户执行 `/plugin marketplace add OthmanAdi/planning-with-files`（docs/installation.md:8）后，市场按 marketplace.json 定位插件、按 plugin.json 注册命令与技能，`commands/` 目录名会被自动映射为 `/planning-with-files:plan` 等命令（README.md:164-168 的三命令表）。
- CHANGELOG.md 与 README 版本表互为镜像，但不同步（见⑤）。

## ④ 数据流

用户路径：装插件（marketplace.json 注册）→ 会话中输入 `/plan`（或让模型按 SKILL.md 的 description 自动触发，触发条件是">5 tool calls 的多步任务"，skills/planning-with-files/SKILL.md:3）→ 命令文件展开为 prompt 注入 → 引用 SKILL.md 执行 → 在**用户项目目录**（非技能目录）创建三件套。`/plan:status` 则只读 `task_plan.md` 的 "## Current Phase" 与 "**Status:**" 行渲染单屏摘要（commands/status.md:9-12）。README 的作用止于"安装前的一次阅读"，运行期零参与。

## ⑤ 设计决策与陷阱

- **README 版本滞后实证**：README.md:44 写 "Current Version: v2.18.2"，而 .claude-plugin/plugin.json:3 与 .claude-plugin/marketplace.json:12 均为 2.23.0——版本亮点表也停在 v2.18.2（README.md:48）。判断版本一律以 plugin.json/SKILL.md frontmatter 为准。
- **目录树失真**：README.md:307 声称存在根级 `planning-with-files/` 插件技能目录，磁盘上并不存在；commands 树只列 plan.md/start.md（README.md:286-287）漏了实际存在的 status.md。README 目录树是"历史快照"而非实时文档。
- **start.md 的 `disable-model-invocation`**（commands/start.md:3）是刻意设计：原始入口只许显式调用，避免模型在简单任务上误触发带来 +68% token 开销（docs/evals.md:98）。
- **status.md 用 emoji 图标**（⏸️/🔄/✅/❌，commands/status.md:17-20）在 Windows 终端可能乱码——v2.16.1 曾专修 Copilot 乱码（README.md:52），同类风险仍在。
- README.md:64 提到的 `.planning/{uuid}/` 并行规划隔离在 experimental 分支，主分支没有。

## ⑥ 新人提示

先读 README.md 的 Problem/Solution 区（README.md:191-227）建立"RAM/Disk"心智模型，再直接跳 docs/quickstart.md 动手；README 的目录树和版本表**不要当事实引用**。三条命令只需记 `/plan`（自动补全最短，v2.11.0 加入）；想知道"为什么 start.md 快死了"——它是 v2.2.0 之前的原始入口，保留只为兼容。改 commands 时注意：命令名=文件名，`plan:status` 的冒号二级名来自文件路径约定；改 README 徽章数据须同步 docs/evals.md 的实测数字。
