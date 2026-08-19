# 04 · 项目内 Skills 知识互链网

> 孤儿文件 = 死亡内容。本篇把 `Skills生态全景/` 织入 work4ai 既有知识网：5 条主线互链 + 用户自身环境的活案例。快照 2026-08-19。

---

## 1. 五条互链主线

### ① 与 MCP协议生态全景（最紧的姊妹篇）

`../../MCP协议生态全景/`（github.com/topics/mcp，64,438 仓，2026-08-19 同日快照）

- **概念分工**：MCP=插座（动态能力连接，JSON-RPC 进程）；Skills=操作手册（静态程序性知识，文件夹+Markdown）。Anthropic 官方定位 skills"补足 MCP"。见本目录 [`02`](02-规范演进与SKILL.md解剖.md) §4。
- **标准策略同构**：Anthropic 两连击——先自家用（MCP 2024-11 / Skills 2025-10-16），再开放标准换生态（MCP 开放 / Skills 2025-12-18），对手跟进。Skills 采纳 48 小时 vs MCP 数月。
- **协议设计互为镜鉴**：MCP 2026-07-28 无状态化瘦身（删 initialize/session/ping，见对方 notes/02）在做的减法，正是 Skills 出生时的形态（2 必填字段）。**2026 年 Agent 基建的共同方向：更小的协议、更多的约定**。
- **检索方法论共享**：topic 盲区 + awesome 对账双口径（对方教训：深层链接层级错=系统性断链）。

### ② 与 deepseek-harness插件化框架（能力打包的两种粒度）

`../../deepseek-harness插件化框架/`（dsh，219 插件包源码级深读）

- dsh 的插件（六组件宿主+金字塔验证）与 SKILL.md 都是"把能力/纪律打包进 agent"的载体，粒度不同：**插件=进程级接缝（hook/工具/沙箱），skill=context 级接缝（指令+脚本）**。
- anthropics/claude-plugins-official 的 plugin 结构（`.claude-plugin/plugin.json` + 可选 `skills/ commands/ agents/ .mcp.json`）证明两者在收敛：**plugin 是分发壳，skill 是内容单元**。
- obra/superpowers 用纯 skills 实现了 dsh 式方法论（TDD/subagent 开发）——"方法论不需要插件框架也能注入"的对照样本。

### ③ 与 harness 三综述/全景（方法论层）

- `../../透视GitHub-Harness高星仓库全景.md`（topic:harness 37 仓）：superpowers 本质是 harness 方法论的 skills 化，可视为该全景的"后续演化章"。
- `../../harness精华笔记.md`（37 仓蒸馏）：其中 addyosmani 的 Harness Engineering 系列与 agent-skills 仓同源（/spec→/ship 生命周期 = harness 仪式的 skill 表达）。

### ④ 与 prompt 工程/harness 工程手册（资产化视角）

- 项目 prompt 工程手册（12 章，2026-08-17）：skill = **可版本化、可跨工具携带的 prompt 资产**；progressive disclosure = prompt 分层加载的标准化（metadata≈system prompt 摘要层，body≈任务指令层，references≈RAG 层）。手册 12 章"长 prompt 瘦身"（ADDITIVE 476→143 行）与 SKILL.md <500 行预算同一上下文经济学。
- harness 工程手册（14 本）：06 验证金字塔 ↔ skills-ref validate + microsoft evals CI；08 Router ↔ skill 触发路由（description 即路由表）。

### ⑤ 项目内既有 Skills 资产（织入存量）

- `../../../../前沿与媒体/103-AgentSkills开放标准深度解析.md`：本目录是其**生态观测数据层**（该文解析标准路线，本目录补 11,492 仓实况与七赛道）。
- `../../../Agent上下文案例/graphify知识图谱skill/README.md`：已有"skill vs MCP 对照"活案例（graphify 同时是 topic:skills 榜内 107,976★ 仓，见 notes/01 §4.2 噪声样本——高星弱相关判定需回读其案例笔记修正：graphify 实为"/graphify 命令+知识图谱 skill"形态，相关性强于初判）。
- `~/.config/opencode/skills/` 全局技能库（本机 30+ 技能）= 用户侧活案例，见 §2。

### ⑥ 与讲透模型宇宙 Part IV（能力地图视角）

`../../../../讲透模型宇宙/`：Part IV 18-19 章（建/调/改模型能力）把"驾驭模型"作为工作能力总纲——Skills 生态是**开发者侧驾驭 agent 的能力分发层**：17 章能力地图的"工具调用/工作流"维度，2026 年的具体形态就是 MCP+Skills 双栈。

---

## 2. 用户环境的活案例（本会话实测）

本机 opencode 的技能目录 `~/.config/opencode/skills/` 下 30+ 技能（concept-3layer / impl-from-scratch / frontier-briefing / paper-mastery……）即 Agent Skills 标准的实现（该路径被 cloudflare/skills README 官方矩阵收录）。**用户日常已在消费这个生态，且用户自己的 skill 组织方式（SKILL.md + 触发词 + 分层指令）与 anthropics/skills 的最佳实践同构**：

| Agent Skills 官方实践 | 用户 skill 现状 | 差距/可借鉴 |
|---|---|---|
| description 写"何时用"触发语 | 各 skill 已有 Triggers 段 | ✅ 一致 |
| <500 行正文，细节拆 references/ | 部分技能靠引用外部文件（如 trending-projects 指向本地克隆） | ✅ 同构 |
| skills-ref validate CI | 无校验 | ⚠️ 可引入 |
| registry/namespace 治理 | 全局+项目两级 scope | ⚠️ 项目级覆盖全局级≈namespace 优先级 |
| evals CI（microsoft 双工作流） | 无 | 💡 远期：对高频技能做命中评测 |

---

## 3. 挂网清单（本目录产出已链接到）

| 位置 | 链接形态 |
|---|---|
| `../README.md`（Agent框架案例索引） | 案例表新增行 + 速查新增两条 |
| `../MCP协议生态全景/README.md` | 姊妹篇互指（对方已挂"Skills 姊妹篇"） |
| 本目录 notes/01↔02↔03↔04 | 四篇互链闭环 |

## refs
- 见各篇 refs；互链目标均为项目内相对路径

*updated: 2026-08-19*
