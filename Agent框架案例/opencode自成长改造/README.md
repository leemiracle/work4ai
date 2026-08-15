# opencode 自成长改造（hermes × ECC 蓝图）· 案例笔记

> 一句话定位：**把自定义 opencode 从"一次性会话工具"改造成"自成长 Agent"——仿 NousResearch/hermes-agent 的闭环学习环（技能自创→使用中自改→记忆策展→跨会话召回），按 affaan-m/ECC 的 harness 性能优化四层（skills/instincts/memory/安全）组织扩展点。**
> 🆕 **v2 自动层（2026-08-15 当晚）**：新增 `agent/auto.md` 全自动助手并覆写为**默认主 agent**（`opencode.jsonc` 的 `build.prompt` 指向它）——意图路由取代命令输入，用户**零斜杠命令**。见 §8。

> 蓝图仓库：hermes-agent 230K★（自成长 Agent）、affaan-m/ECC 240K★（harness 性能优化系统）
> 宿主：opencode 1.18.18（`work4ai\.tools\opencode.exe`），模型 zhipuai GLM
> 改造日期：2026-08-15 · 全部扩展点均为 opencode 原生机制，零代码侵入

## 1. 为什么是这两个蓝图

| 蓝图 | 核心机制 | 我们取什么 |
|---|---|---|
| **hermes-agent** | 唯一内置学习环的 agent：复杂任务后**自主创建技能**、技能**使用中自改**、periodic nudges 提醒持久化知识、FTS5 会话搜索 + LLM 摘要跨会话召回、Honcho 辩证用户建模、MEMORY.md/USER.md/SOUL.md 三件套 | 闭环学习环的全部语义（技能孵化/记忆策展/用户画像/每日日志） |
| **ECC** | `plan → test → implement → review → verify → remember → improve` 七字环；68 agents/284 skills/94 commands；instincts（常载规则）+ rules（按语言选载）+ AgentShield（密钥/注入/权限/MCP 六面扫描）；原生支持 opencode target | 四层组织法 + 七字工作环 + 安全红线（ECC 对 opencode 官方安装路径是 `./install.sh --target opencode`，我们选择手搓轻量版避免 284 技能与本地 225+ 冲突） |

**取舍判断**：ECC 整包安装与本地已有 225 个 skills 冲突风险高、且中文场景规则包不适配——故按其**架构思想**而非其**资产**改造；hermes 是 Python 全家仓不可移植，取其**闭环语义**映射到 opencode 扩展点。

## 2. 蓝图 → 扩展点映射（改造全景）

| 层 | 蓝图来源 | 落地文件 | opencode 机制 |
|---|---|---|---|
| **直觉层** | ECC instincts/rules + hermes 良性约束 | `~/.config/opencode/AGENTS.md`（全局：记忆召回/七字环/写入纪律/安全红线/Token 经济学）<br>`work4ai\AGENTS.md`（项目：知识卡宪法/孤儿率红线/挂网规范） | AGENTS.md 自动注入每次会话 |
| **技能层** | hermes autonomous skill creation + ECC 284 skills | `work4ai\.agent\skills-incubator\`（candidate→verified→晋升三级生命周期）<br>`/grow` 命令执行晋升 → `~/.config/opencode/skills\<name>\SKILL.md` | agentskills.io 开放标准（与 hermes/ECC 互通） |
| **记忆层** | hermes MEMORY.md/USER.md/日记 + FTS5 召回 | `work4ai\.agent\MEMORY.md`（教训+证据+日期，合并升格制）<br>`USER.md`（辩证用户画像）<br>`journal\YYYY-MM-DD.md`（每日日志；旧账 .workbuddy-ai 只读） | AGENTS.md 会话启动协议强制召回 |
| **Agent 层** | hermes 技能引擎 + ECC 专职 agents | `~/.config/opencode/agent\grow.md`（成长工程师：复盘/孵化/晋升）<br>`curator.md`（记忆策展人：去重/衰减/洞察/防密钥泄漏） | opencode 自定义 subagent（mode: subagent） |
| **命令层** | hermes /insights /compress + ECC commands | `/remember` `/retro` `/grow` `/insights` `/shield` 五命令 | opencode command/*.md（$ARGUMENTS 传参） |
| **安全层** | ECC AgentShield | `/shield` 六面审计（密钥/注入/权限/MCP/记忆污染/破坏命令）+ 全局红线第 3-5 条 | 命令层 + AGENTS.md 常载 |

## 3. 成长飞轮（怎么转起来）

```
会话启动                    会话中                          会话尾
─────────                 ─────────                       ─────────
读 MEMORY/USER     →      干活（七字环）          →       /retro 复盘四问
读 journal 近2天           search-first（先查后造）          教训 → MEMORY.md
查孵化器候选               模式第2次出现 → 孵化器            模式 → 候选技能
                          /shield 周期安全审计             日志 → journal/
                                                          
                    ┌──────────────────────────────────────────┐
                    │  /grow：候选 ≥2 次验证 → 晋升正式 skill    │
                    │  /insights：journal 横断洞察 + 记忆衰减    │
                    └────────────── 飞轮闭环 ──────────────────┘
```

## 4. Top10 生态位利用表（用户指定十仓的取用方式）

| 仓库 | 生态位 | 在本改造中的用途 |
|---|---|---|
| affaan-m/ECC | harness 性能优化系统 | **主蓝图**：四层组织法 + 七字环 + AgentShield |
| NousResearch/hermes-agent | 自成长 Agent | **主蓝图**：闭环学习环全部语义 |
| Significant-Gravitas/AutoGPT | 自主 Agent 先驱 | 思想史锚点：从"自主执行"到"自成长"的范式差 |
| ollama/ollama | 本地模型一键运行 | 备选推理后端：opencode.jsonc 可加 ollama provider（离线场景） |
| firecrawl/firecrawl | 上下文 API | /retro 与调研任务的网页上下文源（可作 MCP 接入，装前审） |
| f/prompts.chat | Prompt 集合 | 技能孵化的模式素材库（人类提示词经验 → SKILL.md 步骤） |
| huggingface/transformers | 模型定义框架 | 本地模型侧（配合 ollama）跑 curator/grow 等低风险子代理省 token |
| langgenius/dify | Agent 工作流平台 | 对照系：可视化工作流 vs 文件协议工作流的取舍参照 |
| open-webui/open-webui | 自托管 AI 界面 | 未来给自成长系统加 Web 观察面板的候选 |
| langchain-ai/langchain | Agent 工程平台 | 对照系：代码内 Agent vs harness 内 Agent 的边界 |

## 5. 使用手册（速查）

| 场景 | 命令/动作 |
|---|---|
| 会话中想固化一条经验 | `/remember <教训>`（curator 去重合并后写入） |
| 任务/会话收尾 | `/retro [任务名]`（四问 + 落盘三件套） |
| 模式重复第 2 次 | 候选自动进 `.agent/skills-incubator/candidate/`（grow 在 /retro 中做） |
| 周期性技能晋升 | `/grow [技能名]`（查重 → 晋升 → 报告） |
| 周回顾 | `/insights [天数]`（横断洞察 + 记忆衰减 + 画像矛盾） |
| 安全体检 | `/shield [范围]`（六面审计表） |

## 6. 审计命令

```powershell
# 结构完整性：agents/commands/memory 三层
Get-ChildItem C:\Users\mirac\.config\opencode\agent, C:\Users\mirac\.config\opencode\command | Select-Object Name
Get-ChildItem C:\workspace\work4ai\.agent -Recurse -File | Select-Object FullName
# 直觉层常载验证：两份 AGENTS.md 存在
Test-Path C:\Users\mirac\.config\opencode\AGENTS.md; Test-Path C:\workspace\work4ai\AGENTS.md
# opencode 可运行
& C:\workspace\work4ai\.tools\opencode.exe --version
```

## 7. 与项目互链

- 方法论根基：[`../../复杂系统迭代work4ai.md`](../../复杂系统迭代work4ai.md)（本改造 = 给 work4ai 治理体系装上"自增长引擎"的负熵回路实验）
- 姊妹案例：[`../deepseek-harness插件化框架/`](../deepseek-harness插件化框架/README.md)（插件化 harness 对照：dsh 改造 harness 本身，本案例改造 harness 的使用者）
- 姊妹案例：[`../prompt工程工具链/`](../prompt工程工具链/README.md)（技能精化支线：/optimize /ptest /evalrag 三命令 + prompts/evals 资产目录，与本改造共用 .agent/ 基建）
- 用例库锚点：B 册 hermes-agent 卡、E19 opencode 卡（opencode 已归档续于 crush——本改造证明其文件协议扩展点依然有效）
- 讲透Agent 实战篇已收录本案例

## 8. v2 自动层：auto 全自动助手（零命令架构）

**问题**：v1 的 5 命令 + 4 agents + skills 仍需用户知道"何时敲什么"——手动操作成本高。

**解法**：把路由智能装进**默认主 agent**。opencode 机制：`opencode.jsonc` 覆写内置 `build` agent 的 `prompt.path` → 指向 `agent/auto.md`——开机即默认，Tab 可切回 plan/general。

```
用户自然语言 ──→ auto 意图路由（无需任何命令）
                  ├─ 记忆类话语 → curator 协议（自动读写 MEMORY/USER）
                  ├─ prompt 文本/优化请求 → promptsmith 五步环（重要的落盘 prompts/）
                  ├─ 选型/对比/用什么 → llm-landscape catalog + /stack 协议
                  ├─ 仓库分析 → codegraph 三板斧 → 知识卡入库
                  ├─ 知识生产/翻译 → 知识卡宪法 + 挂网 + 行数对账
                  ├─ 多对象调研 → research 流水线
                  ├─ RAG 质量 → evalrag 四指标
                  ├─ 装插件/危险操作 → 先问 + shield 六面
                  ├─ 跨领域裁决 → 派 polymath
                  └─ 普通任务 → 七字环直接做
自动驾驶（hermes nudges，静默）：里程碑自动记账 / 模式第2次自动孵化 /
  会话尾自动简版retro / 每周首次会话自动shield快扫+journal洞察
```

**设计原则**：命令与子代理全部保留为**手动覆盖入口**，但默认零输入——"命令是快捷键，不是门槛"。自动化动作失败不阻塞主任务（一行报告即可）。

**实测入口**：新开 opencode 会话直接说"帮我选个本地跑 70B 的方案"或"记住 XX 教训"——无需 /stack /remember。
