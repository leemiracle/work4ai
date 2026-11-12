# 13 · Coding 深化（Agentic Coding 新范式）

> [`02-软件研发`](02-软件研发.md) 给了 AI 辅助编程的**概览**（补全/审查/DevOps）。本篇深化 **2025-2026 爆发的 agentic coding 深水区**——agent 不再只是"补全"，而是**自主完成任务、并行干大项目、重塑整个软件生命周期和组织**。这是 AI 应用证据最硬的领域（有 RCT、有 SWE-Bench 基准、有 ROI 数字）。

---

## 先看硬证据：2026 coding agent 的能力与边界

**SWE-Bench Verified（真实 GitHub issue 解决率）**：13%（2024 初）→ **78%（2026-05，Claude Code Opus 4.7）**，趋近饱和。

| Agent | SWE-Bench | 真实 PR 接受率 | 中位 time-to-PR |
|-------|-----------|--------------|----------------|
| Claude Code (Opus 4.7) | ~78% | ~48% | ~14 min |
| OpenAI Codex agent (GPT-5 Pro) | ~76% | — | — |
| Cursor Agent (Sonnet 4.6) | ~67% | ~42% | ~8 min |
| Aider | ~63% | — | — |
| Devin | ~58% | ~38% | ~22 min |
| Cline (开源) | ~58% | — | — |
| 开源权重 + Llama | ~32-45% | — | — |

**两条关键认识**（贯穿本篇）：
1. **真实 PR 接受率（35-50%）远低于 SWE-Bench**——真实代码库有隐含约定/审查期望，benchmark 测不到。
2. **仓库大小是死亡线**：~200K 行可靠，>500K 行所有 agent 都崩（theeditorial 1200-issue 实测）。

---

### 场景 65：AI IDE 与 ambient pair-programming（autonomy slider）
- **痛点**：手写样板慢；想随时问代码又不想切工具。
- **输入 → 输出**：自然语言 + 代码上下文 → 编辑/补全/解释。
- **模型方案**：**AI IDE**（Cursor/Windsurf）或 **IDE 插件**（Copilot）。核心是 **autonomy slider**——从 Cmd+K 精确编辑到全自主 agent。
- **真实案例（2026）**：**Adevinta RCT**（77 工程师/165 任务/4 周）：Claude Code 提升最大（~43%、完成率 74%、评分 4.2），Cursor 中等（~24%、59%、3.6），**GitHub Copilot 几乎可忽略（~1%、44%、2.8）**——关键原因：Claude Code 自动选最强模型（比其他多 60 倍）。Cursor 最佳 bang-for-buck（$20/月/人 vs Claude Code $84）。
- **工具栈**：Cursor / Windsurf / Claude Code（VS Code+JetBrains 插件）/ Copilot。
- **陷阱**：IntelliJ/XCode 用户转 VSCode 系有学习曲线（Adevinta：63% 用 IntelliJ）；扁平月费工具默认不上最强模型 → 手动选或用 consumption 模型。
- **起步 MVP**：本周用 Cursor 的 Agent 模式做一个真实功能，对比手写省时。

### 场景 66：Agentic coding 工作流（plan→edit→run→fix 循环）
- **痛点**：补全只解决"下一行"；要解决"一个任务"需自主循环。
- **输入 → 输出**：任务描述 → agent 自主（读代码→编辑→跑测试→修错→提交）。
- **模型方案**：**命令行/IDE agent**（Claude Code / Cline / Aider）。核心循环：规划→编辑→执行（测试/构建）→读错误→修，直到通过。
- **真实案例（2026）**：**Datadog** 用 Claude+Cursor 做 Stream Router 迁移（FoundationDB→PostgreSQL）——"窄 prompt（单方法+失败测试）远优于宽 prompt"；先让 Claude 生成旧代码**意图 markdown 文档**再迁移，显著减少来回。**theeditorial**：Claude Code 重构准确率 **91%**（Django 15 万行，4 个核心方法跨 23 文件，6.3 分钟，3400 测试全绿）。
- **工具栈**：Claude Code / Cline（VS Code）/ Aider（CLI）；测试套件是地基。
- **陷阱**：宽 prompt → 上下文过载/幻觉接口（Datadog 教训）；agent 卡死/无限循环 → 超时+状态约束。
- **起步 MVP**：给 Claude Code 一个有测试的小重构（重命名跨文件），看它能否保持测试绿。

### 场景 67：自主软件工程师（多小时/多日任务）
- **痛点**：复杂任务（建模块、研究+实现）要数小时；人想委托。
- **输入 → 输出**：高阶任务 → agent 数小时自主（规划+研究+实现+测试+PR）。
- **模型方案**：**自主 agent**（Devin / OpenHands / SWE-agent）+ 沙箱执行 + 长时事件溯源状态管理。
- **真实案例（2026）**：**OpenHands V1 SDK**（MLSys 2026 Industry）：事件溯源+确定性回放+原生沙箱+多 LLM 路由+安全分析，V1 比 V0 系统故障减 **61%**。**Devin** 最 ambitious（多小时/规划/联网研究），但 theeditorial 实测大仓库（>50K 行）最差、$500/月最贵。**DeepSWE**（arXiv:2607.07946）：原创长horizon基准（113 任务/91 仓库，不合并上游防污染，手写功能 verifier）。
- **工具栈**：Devin / OpenHands（MIT 开源）/ SWE-agent；自建 → 沙箱（Firecracker/Docker）+ 事件溯源。
- **陷阱**：自主越久漂移越大 → judge agent 定期校准 + fresh start；大仓库崩溃 → 分而治之。
- **起步 MVP**：用 OpenHands 跑一个 SWE-Bench 任务，看它能否自主解决。

### 场景 68：多 agent 并行长自主（planner/worker/judge）
- **痛点**：单 agent 干不了"团队级"大项目（建浏览器、大规模迁移）。
- **输入 → 输出**：宏大目标 → 几百 agent 并行（规划→分工→执行→裁决）。
- **模型方案**：**角色分离**：planner（探索代码库+建任务，可递归子规划）→ worker（只管干分配的任务）→ judge（每轮裁决继续否）。这是 06 财务 Rippling supervisor 模式在 coding 的极致。
- **真实案例（2026）**：**Cursor**（2026-01 博客）：planner/worker/judge → **几百 agent 并行，近一周写 100 万行代码/1000 文件**（从零建浏览器，GitHub 开源）；Solid→React 迁移 3 周（+266K/-193K）；视频渲染 Rust 重写 **25x 快**（已合并上线）。**关键洞察**：**模型选角**——GPT-5.2 适合长自主（专注不漂移），Opus 4.5 易抄近路；GPT-5.2 比 GPT-5.1-Codex 更会规划（虽后者专训 coding）。"**prompt 比模型和 harness 都重要**"。
- **工具栈**：Cursor cloud agents / 自建（planner-worker-judge + 沙箱 VM）。
- **陷阱**：tunnel vision → judge + 周期 fresh start；worker 冲突 → 同分支推送最小冲突设计。
- **起步 MVP**：用 Cursor 并行 3 个 cloud agent 干一个小项目的不同模块。

### 场景 69：遗留代码迁移 / 现代化
- **痛点**：COBOL/Assembly/老框架迁移耗年；文档缺失；人才断层。
- **输入 → 输出**：遗留代码 → 现代化等价实现 + 业务逻辑文档。
- **模型方案**：**AI 理解旧代码→生成业务摘要/流程图→逐程序翻译**。先文档化意图，再迁移。
- **真实案例（2026）**：**NAB（国民银行）** 6000 开发者标准化 Cursor（评估过 Amazon Q/Copilot）：遗留现代化（单体→微服务、**Assembly 主机迁移**）**快 3x**；BizCalc（Silverlight→Java/React）6 月→2 月，**pre-work 从 2 月→1 周**（Ask Mode 文档化业务逻辑 + Plan Mode 生成用户故事/API spec）；Assembly 迁移快 3x（直接从 Assembly 生成流程图+业务摘要，逐程序修）。**Amplitude**：cron automation 跑遗留迁移（CSS→Tailwind、**2 万+** React 组件替换），每小时 chip 一点。
- **工具栈**：Cursor（Plan/Ask Mode）/ Claude Code；内部上下文工程库（NAB-CEL 用 rules/skills/hooks）。
- **陷阱**：旧代码无文档 → 先 AI 生成意图文档；业务逻辑理解错 → 人工核对关键路径。
- **起步 MVP**：选一个老模块，让 AI 生成"业务逻辑摘要+流程图"，对比你的理解。

### 场景 70：TDD 式 AI 重构（测试质量是天花板）
- **痛点**：重构高风险；怕改坏行为。
- **输入 → 输出**：旧实现 + 新 schema + 失败测试 → 通过测试的新实现。
- **模型方案**：**TDD 收敛循环**：给 AI（旧实现+新设计+失败测试）→ 生成 → 跑测试 → 喂失败输出 → 迭代到通过。把迁移变成"AI 迭代 + 测试裁决"的收敛问题。
- **真实案例（2026）**：**Datadog** Stream Router 迁移（2025-12→2026-02，3 月，PoC 4 周）：每方法 TDD 循环，端到端测试套件是"二值成功标准"；blue/green 验证服务每 30 秒比对 live 流量数周才切流。**核心教训**："**你测试套件的质量，是你能信任 AI 代码的天花板**"。AI 擅长重活（提取逻辑、逐方法翻译），但 **SQL 性能优化仍需人**（AI 生成正确但非最优查询；人优化一次后 AI 能复用模式）。
- **工具栈**：Claude/Cursor + 强测试套件 + blue/green 验证。
- **陷阱**：测试覆盖不足 → AI 改对测试覆盖的部分、改坏没覆盖的；性能 AI 搞不定 → 人工优化。
- **起步 MVP**：选一个有强测试的方法，TDD 循环让它换实现，看测试是否保持绿。

### 场景 71：规格驱动开发（为 agent 写 living docs）
- **痛点**：agent 执行发散；需求文档与代码脱节。
- **输入 → 输出**：明确规格（PRD/技术需求）→ agent 按规格执行 + 规格作评估框架。
- **模型方案**：**为 agent 写 living docs**（PRD/技术需求显式写给 agent），规格既引导执行又作实现后评估。
- **真实案例（2026）**：**Coinbase**："现在为 agent 显式写产品和技术需求，这些 living docs 引导执行并作评估框架"。**Money Forward**：PM 用 Cursor 从代码抽系统关系/架构图/写接地 PRD；"即使规格不在文档，Cursor 能直接从代码识别"。**Amplitude**：Slack bug 报告→cloud agent 调查→开 ticket→开 PR（全自主，规格化触发）。
- **工具栈**：Cursor Plan Mode / Claude Code；MCP 接 Jira/Notion/Linear。
- **陷阱**：规格含糊 → agent 发散；规格过死 → 失去 agent 灵活性；规格与代码漂移 → 代码即规格（从代码反抽）。
- **起步 MVP**：为一个待做功能写一份"给 agent 看的 PRD"（含验收标准），让 agent 实现。

### 场景 72：自动化测试生成
- **痛点**：写测试烦；覆盖不足。
- **输入 → 输出**：用户故事/Jira/代码 → 结构化测试用例 + 可跑脚本。
- **模型方案**：**双 agent**：一个生成结构化测试用例，一个翻译成 Playwright/单测脚本。`tdd` skill 的 agent 化。
- **真实案例（2026）**：**Money Forward**：QA 工程师用 MCP 喂 Cursor（Jira+Notion）→ 双 agent（结构化用例 + Playwright 脚本），**测试生成时间 -70%**；QA 转向上游（风险测试/质量门）。**theeditorial**：Cursor 测试通过率 67%（review 前）。
- **工具栈**：Cursor/Claude Code + Playwright/JUnit/pytest；MCP 接 ticket 系统。
- **陷阱**：生成的测试"形式对但断言弱" → 人工审断言；测试维护成本 → 生成可读可维护的。
- **起步 MVP**：给一个用户故事，让 agent 出测试用例 + Playwright 脚本，跑通。

### 场景 73：Agent 化代码审查 / PR 风险分级
- **痛点**：人工 review 走形式；PR 多审不过来。
- **输入 → 输出**：PR → 风险分级 + 自动修/路由 + 审查意见。
- **模型方案**：**风险分级 agent**（低风险自动合并，高风险路由）+ **review agent**（Bugbot 类，捕人漏的问题）。
- **真实案例（2026）**：**Amplitude** Bugbot（dedicated 审查层）+ PR 风险分级 automation：**60-70% 低风险 PR 自动合并无需开发介入**，高风险自动路由对的工程师；Cursor 成 commit 量 **top3 贡献者**，每周 1000+ agent run 无人触发。**Coinbase**："人工逐行 review 会趋零，工程师升到更高层：决定建什么、架构、评估 agent 产出"。
- **工具栈**：Cursor Automations / CodeRabbit / 自建（风险分级 + review agent）。
- **陷阱**：自动合并错 → 风险分级阈值保守 + 可回退；review 噪音 → 高置信才报。
- **起步 MVP**：给一个低风险 PR 类型（如依赖升级）配自动合并 automation。

### 场景 74：全生命周期 agent 化（idea→prod）
- **痛点**：开发周期长；环节多、交接损耗。
- **输入 → 输出**：idea/ticket → 全链 agent（规划→实现→测试→review→CI/CD→部署）。
- **模型方案**：**agent-first 工程模型**——工程师从"写+审代码"转向"定意图+验结果"；多 agent 异步并行。
- **真实案例（2026）**：**Coinbase**（2400 开发者）：idea→production **20 天→1.8 天（-90%）**，目标 4 小时；75% PR 由 agent 创建，人周省 7 小时，PR/工程师 +55%，1-2 人干原来整团队的活；agent speedruns（30 分钟每人 ship 一个 PR，从 50-70→500 PR）；Superbuilder 角色（专职提速内部工具）；Slack coding agent（idea→实现少手工交接）；工程师并行跑 5-7 个异步 agent。**Amplitude**：cloud agent 后生产 commit **3x**，推进到 CI/CD/构建验证/部署的后半生命周期。
- **工具栈**：Cursor（cloud/local agent + Automations）/ Claude Code + Slack/GitHub/Linear MCP。
- **陷阱**：legacy 系统/流程才是真瓶颈（非开发者，Coinbase）；agent-first 要重塑流程非塞进旧流程。
- **起步 MVP**：统计你的 idea→production 周期，找一个交接损耗大的环节 agent 化。

### 场景 75：非工程团队用 coding agent（PM/设计/QA）
- **痛点**：非工程师难触达代码；跨职能协作墙。
- **输入 → 输出**：PM/设计/QA 的需求 → 直接用 agent 产出（PRD/原型/测试/分析）。
- **模型方案**：**给非工程团队配 coding agent**（Cursor browser/全栈上下文 + MCP 接业务工具）。
- **真实案例（2026）**：**Money Forward**（1000+ 员工）：PM 从代码抽系统关系/架构图/接地 PRD（识别边缘情况）；设计师对 live 前端迭代 + MCP 接产品分析；QA 测试生成 -70%。**NAB** 扩到 10000+ 员工（含 PM/设计/领导），每职能有培训路径。
- **工具栈**：Cursor（browser 可视化 + 全栈上下文）/ Claude Code；MCP 接分析/ticket/设计工具。
- **陷阱**：非工程师用错 agent → 培训路径；触达生产代码风险 → 只读 + 沙箱。
- **起步 MVP**：让 PM 用 Cursor 从代码反抽一个功能的真实逻辑，对比文档。

---

## Coding 领域落地的六条铁律（2026 一手提炼）

1. **测试质量是信任 AI 代码的天花板**（Datadog）——没有强测试套件，别让 AI 动关键系统。
2. **窄 prompt >> 宽 prompt**（Datadog/Cursor）——单方法+失败测试远优于"帮我重构这个大模块"。
3. **仓库大小是死亡线**（~200K 行可靠，>500K 崩）——大库必须分而治之 + 多 agent。
4. **autonomy slider + 模型选角**（Cursor）——GPT-5.2 长自主不漂移、Opus 易抄近路；按角色选模型，不一统天下。
5. **agent-first 要重塑流程，不是塞进旧流程**（Coinbase）——legacy 流程才是瓶颈，工程师从"写审"转"定意图+验结果"。
6. **真实 PR 接受率（35-50%）远低于 benchmark**——benchmark 是能力上限非部署就绪下限；隐含约定/审查期望测不到。

> **Coding 领域的心法**：agentic coding 不是"让 AI 写代码"，是"**重塑软件如何被生产**"——工程师升维到"意图+架构+验证"，机械实现交给 agent 并行干。最大杠杆在**全生命周期 + 组织变革**（Coinbase 20 天→1.8 天、NAB 3x、Amplitude 3x），而非单点补全。这正是 Ch22"规模杠杆"在工程组织的极致。

---

---

## 🔧 深度实操要点（本类场景）

> 本类场景的实操指引。通用骨架代码/评估清单/排错指南见 [00 深度实操手册总纲](00-深度实操手册总纲.md)。

- **决策速查**：pair-programming→IDE AI；自主任务→Claude Code/Cline(D)；大项目→planner/worker/judge
- **关键骨架**：骨架 D (agent) — 本类核心，含SWE-Bench基准
- **评估要点**：SWE-Bench解决率(78%)；真实PR接受率(35-50%)；idea→prod天数(Coinbase 20→1.8)
- **头号陷阱**：仓库>500K行崩→分而治之；测试质量是天花板(Datadog)；窄prompt>>宽prompt
- **进阶路径**：IDE→agent工作流→多agent→全生命周期agent-first

**回到**：[02 软件研发概览](02-软件研发.md) ｜ [场景库 README](README.md) ｜ [Ch19 调与改](../19-调与改.md)
