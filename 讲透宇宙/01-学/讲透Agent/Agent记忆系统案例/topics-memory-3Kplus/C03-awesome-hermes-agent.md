# C-03 `0xNyk/awesome-hermes-agent`（5.3K★）—— 生态扫描：memory providers 收录格局与 A 层对照

> 层级：C 层外围。不克隆，信息源 = GitHub API（README 全文 + 目录树）。
> 本体：README-only 精选目录（仓库仅 README/assets/CI 模板，无代码），0xNyk 个人维护、明确声明"非 Nous Research 官方项目"，服务于 NousResearch/hermes-agent（自称 self-improving agent，内建 persistent memory）。
> 生态快照：README 标注 "last reviewed: 2026-07-16"，Hermes Agent v0.18.2。每条目带成熟度标签：**production / beta / experimental**（编辑性快照，基于文档、安装证据、维护与采用信号）。

## 1. Memory Providers 板块的运行规则（README:275-277 原文口径）

- 定义："Persistent memory backends for Hermes Agent. **Every install picks one**" —— 单供应商模型，一个实例只配一个记忆后端，经 `hermes plugins` 管理，配置见官方文档 memory-providers 页。
- 插件契约（由条目 README:298 hermes-penfield 侧面披露）：实现完整 **MemoryProvider ABC = prefetch（预取）/ pre-compress（预压缩）/ system prompt block（系统提示块注入）** 三个挂点 —— 即记忆层在"LLM 调用前"的生命周期位置（与 C02 的 F13 pre-fetch、F3 上下文构造完全同构）。
- Hermes 自身记忆观：README:131 "Skills are **procedural memory** —— 可复用能力由经验创造并在使用中改进"（技能即记忆）；README:450 要求刻意维护 `USER.md` / `MEMORY.md`（画像记忆当高信号基础设施经营）。

## 2. 收录全表（21 个 memory provider，标签如实转录）

| 标签 | 项目 | 要点 |
|---|---|---|
| production | vectorize-io/hindsight | retain/recall/reflect 工作流；语义+图+时间检索；plugin 或 MCP 接入 |
| production | mem0ai/mem0 | 通用记忆层，user/session/agent 三级；官方 Hermes 集成 |
| production | supermemoryai/supermemory | 云+自托管记忆 API |
| beta | plastic-labs/honcho | 异步用户心理建模 |
| beta | elkimek/honcho-self-hosted | Honcho 自托管封装 |
| beta | JanYork/llm-wiki-cli (LWC) | SQLite Wiki + FTS5 项目记忆 CLI；`pre_llm_call` 生命周期钩子 |
| beta | Lians-ai/Lians | SQLite 本地 MCP 记忆；双时态事实（何时为真）、记忆谱系、防篡改回执 |
| beta | DrDroidLab/open-index | 类型化知识图谱上下文层；SQLite/OpenSearch |
| beta | yantrikos/yantrikdb-hermes-plugin | 嵌入式 DB（pip 即用）；`conflicts()` 显式暴露矛盾、recall 带 `why_retrieved` 归因 |
| beta | amanning3390/flowstate-qmd | 预期式记忆：查询到达前预取上下文 |
| beta | AxDSan/Mnemosyne | 专为 Hermes 造：SQLite+sqlite-vec 混合（50%向量/30%FTS5/20%重要度）；BEAM 分层（working/episodic/scratchpad）+ 时间知识图谱 |
| beta | stephenschoettler/hermes-lcm | Lossless Context Management，长会话防退化 |
| beta | yoloshii/ClawMem | 端上记忆层，零外部 API |
| beta | garrytan/gbrain | 结构化个人记忆 |
| beta | keepnotes-ai/keep | 反思式记忆，情境性复现笔记 |
| beta | yepyhun/Brainstack | 分层记忆内核栈，优先级召回 |
| beta | greyhaven-ai/autocontext | 递归自改进上下文，自动策展+压缩 |
| beta | sourcevault-ai/sourcevault-code-tools | 本地代码记忆（语义检索+引用） |
| beta | codenamekt/hexus | Postgres+pgvector；本地 MiniLM-L6-v2 嵌入使热路径无 LLM/HTTP |
| beta | penfieldlabs/hermes-penfield | Penfield 知识图谱前端（付费云，无免费层） |
| experimental | TerminallyLazy/tree-ring-memory-skill | 文件级记忆卫生（recall/capture/审计/整合/**有意遗忘**），"作为方法收录而非即插后端" |

**分布：3 production / 17 beta / 1 experimental** —— production 仅有的三个全是 A 层收录过的通用记忆层（hindsight、mem0、supermemory），beta 长尾则绝大多数是 Hermes 原生小插件。

## 3. 散落其他板块的记忆相关条目（体现"记忆是横切关注点"）

- Skills & Plugins：plasma-ai/wiki（Git 追踪 Markdown 知识库，明确"无托管记忆服务/向量库"）、plur-ai/plur（**开放 engram 格式 YAML** 的共享记忆层）、hermes-snow-search（跨会话 SQLite FTS5 全史检索，CJK/英文分词自动路由）、robrain（记录被否决的备选方案及理由 = 决策记忆，Postgres）。
- Multi-Agent：MisakaNet（**Git 分布式群体记忆**：一节点解题、全节点经 GitHub Issues 同步 markdown lessons）、space0-mcp（3D 体素空间记忆）。
- 周边：screenpipe（屏幕/音频捕获 → "对你看过说过听过的长期记忆"，MCP）；hermes-backup-recovery（对 `$HERMES_HOME` 下 memory/skills/聊天史的加密备份与恢复演练）。
- Operational Playbooks（README:447）："memory pressure 处理" 作为生产故障模式单列 —— 记忆系统是被运维的对象，不只是被安装的对象。
- Level-Up Blueprints（README:458）给出官方推荐记忆栈排布：**内建记忆 → honcho-self-hosted（跨会话用户建模）→ hindsight（大历史 retain/recall/reflect）→ plur（可携带共享 engram）→ flowstate-qmd（主动召回）** —— 这是目录里最接近"记忆层选型路线图"的素材。

## 4. 与 A 层 29 仓对照：谁被收录、谁没有

**入选 4/29**：mem0（A01，production）、supermemory（A03，production）、hindsight（A06，production）、honcho（A15，beta）。

**未入选 25 个**中可归为四类：
1. **中国生态系全部缺席**：TencentDB-Agent-Memory（A05）、ms-agent（A22）、MineContext（A18）、memU（A09）——语言/社区圈层是显著边界。
2. **研究型/论文驱动系统**：MemOS（A11）、PixelRAG（A12）、mempalace（A02，自称"最强基准"）——与该目录"production/beta 按可安装证据评级"的工程取向不合。
3. **基础设施型而非记忆后端型**：deeplake（A13 数据运行时）、memvid（A07 视频载体）、agentmemory（A04 面向编码 Agent 自用）——不实现 Hermes MemoryProvider 契约即不收录。
4. **同期新项目**：Memori（A08）、EverOS（A10）、memory-lancedb-pro、OpenMemory、Acontext（A24，"Agent Skills 即记忆"与 Hermes 的 skills-as-procedural-memory 观点完全同构却未收录）等——目录最后审阅 2026-07-16，收录滞后于 GitHub 趋势榜。

**折射的生态格局**：
- 记忆层生态呈"**双态结构**"——少数跨平台通用层（mem0/supermemory/hindsight/honcho，均主动做官方集成）+ 大量宿主原生小插件（SQLite/FTS5/pgvector 系，为单一 Agent 框架深定制）。
- **入选门槛 = 集成意愿 × 可安装证据**，与 star 数相关性弱（beta 长尾多为 <1K★ 项目；3K+ 的 A 层项目 25/29 未入）。
- 技术口味清晰：本地优先（SQLite 系至少 6 家）、混合检索（向量+FTS5+重要度加权）、时间感知（双时态/事实失效）、矛盾显式化（conflicts/why_retrieved）、遗忘与压缩（tree-ring/autocontext/lcm）——与 A 层头部系统的功能词表高度趋同，验证这些已是 2026 记忆层"标配语义"。
- 单供应商模型（"every install picks one"）说明记忆层尚处**替换式消费**阶段：组合多个记忆后端（如事实库+用户模型分用两家）的编排需求已在 blueprint 里以"逐步加装"方式隐性表达，但契约层未支持。

## 5. 风险与局限

- 单人维护、编辑性标签、无量化评测——"production"≠ 第三方验证 [自封]；条目链接经 CI（links.yml）校验存活但不校验质量。
- 收录偏 Hermes 实操视角，A 层对照中的"缺席"不能直接推断为技术劣势（多为圈层/时机原因，见上）。
