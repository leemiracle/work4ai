# planning-with-files 新人导览（ONBOARDING）

> 基于知识图谱（49 节点/127 边/13 层/15 步 tour）撰写，文件锚已核实。本地仓位于 agent-repos/agent-projects/planning-with-files，v2.23.0。

## 1. 项目定位

OthmanAdi/QuinnPeng 维护的 27.7k★ 项目（MIT，v2.23.0），本质上是一个 **Claude Code 规划技能插件**：把 Manus 团队公开的"上下文工程"方法论复刻成可安装的 skill。一句话概括——用三个 markdown 规划文件（`task_plan.md` / `findings.md` / `progress.md`）把**文件系统当持久 Disk、上下文窗口当易失 RAM**，对抗长任务中 agent 的目标漂移与上下文重置。

仓库形态是"一个方法 + 16 个 IDE 的适配工程"：方法核心不足 10 个文件，其余全是平台变体、安装设施与评测复盘。

## 2. 技能形态与运行机制

以 Claude Code 插件分发：`.claude-plugin/plugin.json` 声明元数据，`skills/planning-with-files/SKILL.md` 是正本。SKILL.md 的 YAML frontmatter 声明触发条件（>5 次工具调用的多步任务）与 `allowed-tools` 白名单，并直接内挂四组钩子：

- **UserPromptSubmit**：检测到 `task_plan.md` 存在则提醒先读三件套；
- **PreToolUse**：在 Write/Edit/Bash/Read/Glob/Grep 前自动 `cat task_plan.md | head -30`，把计划逐次重注入上下文；
- **PostToolUse**：Write/Edit 后提醒沉淀到文件；
- **Stop**：收尾时校验完成度。

用户入口是三条斜杠命令：`/plan`（`commands/plan.md`，一键创建三文件）、`/start`（`commands/start.md`，原始入口，支持 /clear 后会话恢复）、`/plan:status`（`commands/status.md`，单屏状态速览）。

## 3. 仓库目录速览

- 根级元文档：`README.md`（方法全貌+16 平台矩阵）、`CHANGELOG.md`（30 版演进史）、`CONTRIBUTORS.md`、`MIGRATION.md`（v1→v2 迁移）
- `commands/`：三条斜杠命令定义（薄入口）
- `skills/planning-with-files/`：技能正本（SKILL.md+reference.md+examples.md+templates+scripts）
- `templates/`：三件套模板根级副本；`scripts/`：`scripts/init-session.sh`（建文件）、`scripts/check-complete.sh`（收尾校验）、`scripts/session-catchup.py`（会话恢复）、`scripts/sync-ide-folders.py`（跨 IDE 同步）+ .ps1 版
- `docs/`：使用主线 + 安装枢纽 + 16 平台分册 + 评测安全
- 平台变体目录：`.agent/` `.factory/` `.kilocode/` `.cursor/`（hooks/ 8 个钩子脚本）`.kiro/`（steering/ 转向文件）`.gemini/` `.codex/` `.continue/` `.mastracode/` `.openclaw/` `.opencode/` `.pi/` `.adal/` `.codebuddy/`
- `examples/boxlite/`：微 VM 沙箱示例（`examples/boxlite/quickstart.py`）

## 4. 内容架构（图谱 13 层主线）

图谱 13 层自顶向下即天然阅读顺序：

1. **门面元文档**：README / CHANGELOG / CONTRIBUTORS / MIGRATION，建立全局地图；
2. **斜杠命令入口**：commands/ 三件，用户交互最外层；
3. **技能定义主文件**：`.agent` / `.factory` / `.kilocode` 三变体 SKILL.md——同源非逐字：.factory 版独有 Read vs Write 决策矩阵，.kilocode 版 frontmatter（v2.23.0）挂四组钩子；
4-6. **三件套模板三层**（task_plan / findings / progress）：三变体模板 diff 实证零分叉，读一份即可；
7. **实战示例与理论参考**：examples.md 四场景 + references.md Manus 六原则，教学与理论层；
8. **方法主文档四件**：`docs/quickstart.md`（五步上手）、`docs/workflow.md`（ASCII 图解 hooks 闭环）、`docs/troubleshooting.md`（10 类排障）、`docs/windows.md`；
9. **安装枢纽与沙箱**：`docs/installation.md`（总枢纽）、`docs/boxlite.md`（微 VM 运行形态）；
10. **钩子平台分册**：`docs/cursor.md`（三钩子+自动续跑，强制力最强）、`docs/copilot.md`（四钩子 JSON 协议）、`docs/kilocode.md`、`docs/mastra.md`；
11. **自动发现平台分册**：`docs/gemini.md`、`docs/antigravity.md`（自动发现、团队共享）、`docs/kiro.md`（独用 .kiro/steering/ 转向文件）、`docs/codebuddy.md` 等 7 篇；
12. **轻量手动平台分册**：`docs/codex.md`（往 AGENTS.md 注入三步指令）、`docs/continue.md`、`docs/pi-agent.md`（不执行钩子纯手动）、`docs/opencode.md`（会话恢复解析有限）；
13. **评测与安全复盘**：`docs/evals.md` + article 两版。

## 5. 核心方法论

1. **核心隐喻**：上下文窗口=RAM（断电即失），文件系统=Disk（持久），一切围绕关键状态落盘。
2. **三件套分工**：task_plan.md 是"磁盘上的工作记忆"——单句 Goal + 五阶段三态状态机（需求发现→规划→实现→测试→交付）+ 关键问题/决策/错误三张表；findings.md 是上下文外的知识库——需求、研究结论、技术决策、多模态观察；progress.md 是会话时间线——动作、文件变更、测试结果、带时间戳错误日志。
3. **六条关键规则**：开工前先建计划；2-Action Rule；Read-Before-Decide；做后更新；记录全部错误；永不重复失败。
4. **2-Action Rule**：每 2 次 view/browser/search 类操作后必须回写 findings.md，防内容随上下文重置丢失——最硬的落盘纪律。
5. **Read-Before-Decide**：重大决策前重读 task_plan.md。本质是注意力刷新机制，让 agent 在 ~50 次工具调用后不失焦（出处=Manus"复诵操纵注意力"原则）。
6. **3-Strike 错误升级协议**：同一错误第三次出现必须停下换路并记录进错误表。
7. **5-Question Reboot Check**：我在哪/去哪/目标/学到什么/做了什么——答案分别锚定 task_plan 与 findings，把三件套绑成可自检的断点恢复系统。
8. **理论根基**（`skills/planning-with-files/reference.md`）：Manus 上下文工程六原则（KV-cache 命中率优先、掩码不移除工具、文件系统即外部记忆、复诵操纵注意力、保留错误轨迹、防 few-shot 漂移）+ 三策略（压缩/多智能体隔离/卸载）；量化锚点 ~50 次工具调用/任务、100:1 token 比。
9. **效果与代价**（`docs/evals.md`，v2.22.0，skill-creator 框架 5 任务 30 断言）：with_skill 96.7% vs without 6.7%，盲测 A/B 3/3 全胜；成本 +68% token / +17% 时间。

## 6. 新人上手路径（15 步 tour 压成 6 个里程碑）

- **M1 全局地图**（t01）：读 `README.md` 与 `CHANGELOG.md` 建立全局认知；
- **M2 触发链路**（t02+t03）：`commands/plan.md` → 精读 `skills/planning-with-files/SKILL.md`，再对比 `.agent` 与 `.factory` 变体差异；
- **M3 三件套**（t05-t07）：读 `templates/` 三模板（task_plan→findings→progress），脑内跑一个假想任务；
- **M4 理论与实战**（t04+t08）：`skills/planning-with-files/reference.md` 六原则 + examples.md 四场景演示；
- **M5 使用主线**（t09+t10）：`docs/quickstart.md` → `docs/workflow.md` 闭环图 → `docs/troubleshooting.md` 备查；
- **M6 效果、安全与平台工程**（t11-t15）：`docs/installation.md` → 挑自家 IDE 分册（如 `docs/cursor.md`）→ `docs/evals.md` + `docs/article-v2.md` 收官，理解效果/成本/安全三角。

## 7. 陷阱与注意

- **README 滞后**：版本区块停在 v2.18.2（CHANGELOG 已至 2.23.0），目录树声称的根级 planning-with-files/ 目录磁盘上已不存在——以源码为准；
- **CHANGELOG 含大量历史路径**（docs/moltbot.md、.kilocode/rules/ 等）多已删除，引用前先验证；
- **三变体 SKILL.md 非逐字拷贝**：.factory 版独有读写决策矩阵；.agent 版模板在 references/ 子目录而 .factory/.kilocode 在 templates/——改内容须同步多处（`scripts/sync-ide-folders.py` 为此而生）；
- **安全红线**：PreToolUse 逐次重读 task_plan.md 与 WebFetch/WebSearch 组合曾构成间接 prompt injection 放大链（WebSearch 内容落盘→每回合被重注入），v2.21.0 已从 allowed-tools 移除 web 工具修复（`docs/article.md`）——fork 时慎加回；
- **Windows 三坑**（路径分隔符/换行符/PowerShell）见 `docs/windows.md`；
- **无钩子平台降级**：Continue/Pi/Codex 上方法退化为纯人工三步纪律（先建文件、决策前重读、阶段后更新），效果依赖自觉；
- **成本敏感**：+68% token 开销是效果的代价，短任务（<5 工具调用）不该触发。

## 8. 延伸阅读

- `docs/article-v2.md`：安全复盘，核心论点"allowed-tools 是攻击面分类信号"；
- `MIGRATION.md`：v1→v2 四步迁移与三协议推广；
- `docs/boxlite.md`：微 VM 沙箱形态（技能注入 VM、规划文件跨会话持久化、快照回滚）；
- Manus 官方博客（`skills/planning-with-files/reference.md` 末尾附出处链接）——六原则一手来源；
- 同目录 `../deepwiki/`（12 章全量页）与 `.understand-anything/knowledge-graph.json` 图谱可交叉检索。
