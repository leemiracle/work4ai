# Agent 上下文案例 · 给 Agent 的代码智能（Code Intelligence for Agents）

> 一句话定位：**Agent 的"眼睛"——预索引的代码知识图谱 / 语义检索基础设施，让 agent 一次调用拿到精确代码，而不是 grep/glob/Read 逐文件爬仓库。**
>
> 与 [`Agent框架案例/`](../Agent框架案例/)（harness 层：进程/工具/信任）、[`Agent记忆系统案例/`](../Agent记忆系统案例/)（记忆层：跨会话知识）平行，本目录是**上下文层**：单次任务内"给模型看什么代码"。
>
> 首个案例：[`codegraph代码知识图谱/`](./codegraph代码知识图谱/)（66.4k★，2026-01 首发 npm，本地验证 2026-08-14）
> 第二案例：[`graphify知识图谱skill/`](./graphify知识图谱skill/)（106k★，PyPI `graphifyy`，skill 交付 + 多模态语料，本地验证 2026-08-14）

---

## 1. 为什么 2026 年这个领域爆发了

Baseline 是每个 coding agent 的原生探索循环：**grep → glob → Read，一次一个文件**。这在大仓库上意味着：回答一个架构问题（如"VS Code 的 extension host 怎么和主进程通信？"）需要 **28–43 次工具调用 + 最多 19 次文件读取**，模型把预算烧在"重新推导仓库结构"上——而结构本来是可以**预先算好**的。

于是 2023–2026 出现了一整条赛道：把代码库变成**可查询的索引**（符号图 / 调用边 / 依赖边 / 路由 / 向量），agent 一次查询拿到 surgical context。codegraph 的实测（2026-08 重测，Claude Opus 4.8，7 仓库 4 次取中位）：**工具调用 -88%、耗时 -53%、token -62%、成本 -44%、文件读取 7/7 仓库降为 0**。

## 2. 六条技术路线（领域全景）

| # | 路线 | 机制 | 代表项目 | 新鲜度 | 本地性 |
|---|---|---|---|---|---|
| R1 | **无索引·即时检索** | grep/glob/Read 现场爬 | Claude Code / Codex / opencode 原生 | 永远新鲜 | 本地 |
| R2 | **词法/符号索引** | ctags、FTS、tree-sitter tags | universal-ctags、ripgrep（地基） | 快照 | 本地 |
| R3 | **预构建代码知识图谱** | 解析+跨文件解析成图：符号/调用边/依赖边/路由/桥接 | **codegraph**（本案例）、**graphify**（本案例，AST+LLM 混合）、Greptile（托管）、Joern/CodeQL/Glean/Kythe/Stack Graphs（安全/大厂血统） | watcher 增量同步 / hook 重建 | codegraph、graphify 本地 / Greptile 云 |
| R4 | **LSP 实时语义** | 语言服务器在线回答"定义/引用/实现" | **Serena**（28k★，40+ 语言，MCP） | 实时（查询时解析） | 本地 |
| R5 | **嵌入向量检索** | chunk → embedding → 相似度召回 | Cursor codebase indexing、Continue.dev、Augment context engine | 增量重嵌 | Cursor/Augment 云 / Continue 本地 |
| R6 | **LLM 生成摘要/地图** | 把仓库蒸馏成 token 预算内的地图或 wiki | Aider repo map（tree-sitter + 图排序）、DeepWiki（Cognition 托管 wiki）、repomix/code2prompt（整仓打包） | 地图随改随算（Aider）/ 托管快照（DeepWiki） | Aider 本地 / DeepWiki 云 |

**核心 trade-off**：预计算（快、贵在维护、可能过期） vs 实时查询（永远新鲜、慢、依赖语言服务器装好） vs 向量（模糊语义近邻、可跨语言、但不精确且不可解释）。codegraph 用"三层 auto-sync"把 R3 的新鲜度短板补到秒级；Serena 干脆不建索引、把新鲜度做到极致但每次查询更重。

## 3. 全领域项目速查表（2026-08-14 核对）

### 3a. Agent 原生（可装进任意 agent 的 MCP/CLI）

| 项目 | Stars | 机制 | 语言 | 交付面 | License | 一句话 |
|---|---|---|---|---|---|---|
| [codegraph](https://github.com/colbymchenry/codegraph)（[案例](./codegraph代码知识图谱/)） | 66.4k | Rust 内核解析成图 → SQLite+FTS5 | 20+（Rust 原生 20） | MCP（默认单工具 `codegraph_explore`）+ CLI | MIT | 最快的完整代码图谱，本地优先，auto-sync 秒级 |
| [graphify](https://github.com/Graphify-Labs/graphify)（[案例](./graphify知识图谱skill/)） | 106k | Python 七段管线：tree-sitter AST（零 LLM）+ LLM 语义 pass；每条边带 EXTRACTED/INFERRED/AMBIGUOUS 置信标签 | 36 语法 + docs/PDF/Office/音视频/arXiv | **skill（`/graphify`，20+ 平台）** + CLI + MCP/HTTP 可选；产物三件套可 git 共享 | Apache-2.0+MIT | 代码之外的一切（文档/PDF/视频/why 注释）也进图；Leiden 社区 + god nodes + path 查询；YC S26 |
| [Serena](https://github.com/oraios/serena) | 28k | LSP 抽象层（或付费 JetBrains 插件后端） | 40+ | MCP（多工具：找符号/引用/重构/符号级编辑）+ 记忆系统 | MIT | "agent 的 IDE"——语义检索**加**精确编辑重构 |
| [code-index-mcp](https://github.com/johnhuang316/code-index-mcp) | 1k | tree-sitter 深解析 10 语言 + fallback 50+ 文件类型 | 10 深/50+ 浅 | MCP（搜索为主，浅/深两级索引） | MIT | 轻量索引搜索，Claude 生态出身 |
| Aider [repo map](https://aider.chat/docs/repomap.html) | — | tree-sitter 抽符号 → 文件依赖图上跑图排序（PageRank 式）→ 1k token 预算内出地图 | tree-sitter 全系 | prompt 注入（每轮随请求发送） | Apache-2.0 | "图排序选 top 符号"思想的原点（2023-10） |

### 3b. 闭源/托管（团队级）

| 项目 | 机制 | 卖点 | 交付面 |
|---|---|---|---|
| [Greptile](https://greptile.com) | 托管图索引 + agent swarm 并行审 PR | 22k+ 团队；审 PR/写测试（TREX）；从团队 PR 评论里持续学习规范 | GitHub App / MCP / Claude 插件 / `$30/seat`，可自托管 |
| Cursor codebase indexing | 云端嵌入索引 | `@codebase` 语义搜索，IDE 内置 | IDE |
| [Sourcegraph](https://sourcegraph.com)（Cody/Amp） | 代码搜索 + SCIP 索引 + context engine | 十年代码搜索积累，跨仓库 | IDE/CLI/Web |
| Augment context engine | 实时代码索引（宣称秒级感知变更） | "real-time knowledge" | IDE |
| [DeepWiki](https://deepwiki.com) | LLM 生成的仓库 wiki | 免费看开源仓库的"第二入口"；见 dsh 案例 [DeepWiki 对照笔记](../Agent框架案例/deepseek-harness插件化框架/notes/06-deepwiki/01-DeepWiki对照与增补.md)：**章节全但引用行号需复核** | Web |

### 3c. 血统层（AI 之前就存在的代码图谱，今天被 agent 复用）

| 项目 | 出身 | 贡献 |
|---|---|---|
| [Joern](https://joern.io) | 安全审计 | **Code Property Graph**（AST+CFG+DDG 合一）——"代码即图"的工程范本 |
| [CodeQL](https://codeql.github.com) | GitHub | 图查询语言做变体分析；安全研究标配 |
| [Glean](https://glean.dev) | Meta 开源 | 全球最大规模代码索引系统（FB 全库） |
| [Kythe](https://kythe.io) | Google 开源 | 代码知识图谱的学术级 schema 与跨语言锚点（锚点→定义的叮咬模型） |
| [Stack Graphs](https://github.com/github/stack-graphs) | GitHub，Rust | tree-sitter 之上做增量名字解析——codegraph R3 路线的直接先驱 |
| SCIP / LSIF | Sourcegraph | 索引交换格式（LSIF 2018 → SCIP 2023），让索引与消费解耦 |
| universal-ctags / tree-sitter | 社区 | 一切符号提取的地基（ctags 1979 谱系；tree-sitter 是增量解析+容错） |

## 4. 领域演进时间线

```
1979/1996  ctags / universal-ctags        —— 符号索引的史前时代
2016       LSP（微软）                    —— 语义查询标准化，编辑器统一
2018       LSIF / tree-sitter 兴起        —— 索引可离线；解析可容错增量
2020-2022  Glean(Meta) · Kythe(Google) · Stack Graphs(GitHub)
                                          —— 大厂把"全库代码图"工程化
2023-10    Aider repo map                 —— 第一次为 LLM 设计"token 预算内的图排序地图"
2023-2024  Cursor/Cody/Sourcegraph 嵌入索引 —— RAG 思路搬到代码
2024       Greptile                       —— 图索引 + agent swarm 审 PR（SaaS 化）
2025       Serena                         —— LSP 路线接入 MCP（语义不止检索，还能编辑）
2026-01    codegraph 首发（npm @colbymchenry/codegraph）
2026       graphify（PyPI graphifyy）       —— skill 交付路线爆红（106k★）：AST+LLM 双 pass、
                                          置信标签全边化、多模态语料、图 commit 进 git 共享
2026-08    codegraph 66.4k★，v1.5.0       —— Rust 内核 + 单 MCP 工具面 + 三层 auto-sync
```

规律：**每一步都在把"agent 自己临时推导结构"的成本，换成"基础设施预先持有结构"**——这正是 [`软件即熵治理`](../软件即熵治理.md) 在上下文层的投影：索引是**预付的熵减**。

## 5. 与本项目其他模块的接口

| 模块 | 关系 |
|---|---|
| [`工程化手册库/ContextEngineering手册`](../工程化手册库/ContextEngineering手册/README.md) | 理论框架：SPACC 五要素中的 **S（Selection）** 的工业化实现；本目录是 S 的案例层 |
| [`Agent框架案例/deepseek-harness插件化框架`](../Agent框架案例/deepseek-harness插件化框架/README.md) | 层级互补：dsh 管**进程/工具/信任**（harness 层），codegraph 管**知识/检索**（上下文层）；dsh 的 MCP 命名空间 `mcp__<server>__<tool>` 正是接这类工具的插槽 |
| [`欺骗动力学-AI纪实验包.md`](../欺骗动力学-AI纪实验包.md) | 反欺骗切面：codegraph 的基准方法论（双臂封锁、0 污染）与诚实披露（residual context +80%）是"评测不自欺"的工业范本，见 [笔记 02](./codegraph代码知识图谱/notes/02-基准方法论与诚实披露.md) |
| [`讲透上下文缓存`](../讲透上下文缓存/README.md) | 相邻问题：驻留上下文的经济学（codegraph 披露的 67k vs 18k 驻留差正是 cache 上下文的问题） |

## 6. 选型速查

- **小仓库（<几百文件）**：R1 就够——Claude Code 原生 grep/Read 已经很强，索引是纯开销。
- **大仓库/多语言/跨文件问题**：R3（codegraph，图+精确）或 R4（Serena，LSP 全语义 + 编辑重构）。
- **项目理解/知识管理**（docs/PDF/视频/设计缘由进图，`path A B` / 社区 / god nodes）：graphify——R3 里唯一的多模态语料 + skill 分发。
- **只要搜索不要图**：code-index-mcp（轻）或 ripgrep（零依赖）。
- **团队 PR 审查/规范学习**：Greptile（云）；graphify 的 `prs --conflicts`（本地，图社区共享 = 合并序风险）；或等 codegraph platform。
- **IDE 内语义跳转 + @codebase**：Cursor（闭源）或 Continue（开源本地）。
- **离线/隐私硬约束**：codegraph（100% 本地 SQLite）、Serena（本地 LSP）、graphify `--code-only`/`--backend ollama`（代码+音视频全离线）、Continue（本地向量）——四者都不出网。

## 📌 导航

- 案例一：[`codegraph代码知识图谱/`](./codegraph代码知识图谱/)（MCP 常驻路线 · README + 3 篇笔记）
- 案例二：[`graphify知识图谱skill/`](./graphify知识图谱skill/)（skill 按需路线 · README + 3 篇笔记；与案例一正面互文）
- 待办案例位：Serena（LSP 路线）、Greptile（SaaS 路线）、Aider repo map（地图路线）——按需增补
