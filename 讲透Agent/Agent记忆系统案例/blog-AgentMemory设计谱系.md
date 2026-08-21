# Agent Memory 设计谱系：三份源码，一个收敛点

> 一篇 blog，基于三份一手源码深读：ClaudeCode（泄露 TS 本体 512,664 行）、openclaw（386K★，memory 子系统 ~165K 行）、mem0 v3 + Letta（官方文档与论文 arXiv:2504.19413）。
> 写作日期：2026-08-21。证据级：ClaudeCode/openclaw 为 file:line 级源码实证；mem0/Letta 为官方文档+论文（2026-08 检索）。

## Hook：同一个问题，三个相反的答案

"agent 该怎么记住东西？"

2026 年，你能在三份源码里找到三个截然相反的答案：

- **ClaudeCode**（Anthropic 的终端 agent，源码泄露版实证）：**没有向量库，没有 embedding，没有巩固管线**。记忆是 Markdown 文件，检索靠 grep。
- **openclaw**（9 个月 386K star 的现象级开源个人助手）：为记忆写了 **~165,000 行代码**——SQLite 溯源、六信号排序、三阶段"做梦"、双车道召回。
- **mem0**（记忆中间件，arXiv:2504.19413）：你们都太复杂了，应用只需要调 `add()` 和 `search()`，抽取、去重、图谱、时间推理**全交给中间件**。

一个几乎不建机器，一个建了座城市，一个把城市外包了。但把三份源码都读完后，我看到的是相反的结论：**它们正在收敛成同一个形状。**

## 背景：四年，从论文隐喻到生产系统

2023 年 MemGPT 把记忆做成操作系统隐喻：core memory（常驻上下文）= RAM，archival memory（向量库）= 磁盘，agent 自己调函数在两级之间换页。同年 Generative Agents（arXiv:2304.03442）证明了另一件事：**记忆的质量取决于写入时的策展，而不是索引时的算法**——重要性打分写时一次，检索时零模型调用。

2025 年 sleep-time compute（arXiv:2504.13171）补上最后一块：agent 空闲时用后台算力预先消化上下文，主对话时更快更准。

2026 年，这三条线各自落地成了产品。按出身分三派：

| 派系 | 代表 | 出身 | 记忆哲学 |
|---|---|---|---|
| 极简派 | ClaudeCode | 终端工具 | 结构越少越可控 |
| 治理派 | openclaw | 个人助手 | 检索要强，写入要严 |
| 服务派 | mem0 / Letta | 中间件 / MemGPT 团队 | 记忆是基础设施 |

## 三派解剖：写路径 × 读路径

看一个记忆系统，只需要问两个问题：**谁有权写？怎么读回来？**

### ClaudeCode：一摞笔记本 + grep

写路径：agent 在对话中顺手把要点写进 `CLAUDE.md` 和 auto-memory 目录的 Markdown 文件。没有 gate，没有打分，没有后台巩固——写了就是写了。
读路径：CLAUDE.md 全文注入每轮上下文；历史记忆靠文件搜索工具（grep 语义）。
哲学一句话：**记忆必须人可读可改，其他一切复杂度都是风险**。这在源码实证里表现为：整个记忆子系统没有一行向量代码。

### openclaw：带审核制度的图书馆

写路径是全系统最重的部分（细节见[《openclaw memory 体系深读》](../../../Agent框架案例/openclaw/notes/06-memory体系深读.md)）：

- durable 记忆（`MEMORY.md`）只有**一个写者**：夜间 dreaming 巩固
- 巩固前过三层确定性 gate：六信号加权（relevance 0.30 / frequency 0.24 / diversity 0.15 / recency 0.15 / consolidation 0.10 / conceptual 0.06）→ 三阈值（分数 ≥0.75、被召回 ≥3 次、来自 ≥3 个不同查询）→ 模型重写必须过结构校验（旧条目损失 ≤25%、≤10K 字符、逐条带 `Source: path#Lx-Ly` 溯源锚点）
- 每条记忆在 SQLite 里带**不可伪造的溯源列**：`origin_class ∈ {owner, agent, untrusted, system}`（CHECK 约束，prose 声称自己是主人写的没用）——untrusted/system 内容在进 prompt 之前就被结构性剔除

读路径分双车道：Lane 1 每轮零模型调用（bootstrap 注入 + 混合搜索 vector 0.7/BM25 0.3 + trigger 注入 ≤3 条）；Lane 2 只在"消息显式指向过去且 Lane 1 无强命中"时才启动真子代理（15s 超时，熔断降级）。
哲学一句话：**写路径就是安全边界**——记忆投毒（OWASP ASI06）靠写时溯源结构性防御，不靠事后检测。

### mem0 v3 / Letta：记忆即服务

**mem0 v3**（2026 年新算法）写路径是"单遍 ADD-only 抽取"：一次 LLM 调用抽出事实 → MD5 哈希去重 → 批量嵌入 → 实体抽取链接。**v2 的 UPDATE/DELETE 被整体砍掉**——官方理由：改写会毁信息，覆盖即丢失；矛盾的新旧事实并存，交给检索排序区分"曾经住在纽约"和"现在住在旧金山"。读路径是四信号并行融合：semantic（向量）+ keyword（BM25，带动词词形归一）+ entity（实体图 boost）+ temporal（写时抽取的时间元数据 vs 查询时间意图）。账面成绩：检索 token 从 full-context 的 25,000+ 降到 **<7,000**，LoCoMo 91.6 / LongMemEval 93.4。

**Letta**（MemGPT 团队）最有意思的是演化路径：论文时代是 OS 隐喻（换页、分级），双 agent 架构（primary agent 对话，sleep-time agent 专管记忆，可以用更强的模型因为不受延迟约束）。而 2026 年的 Letta Code 已经长成了：**MemFS——一个 git-backed 的记忆文件系统**，`/init` 引导、`/remember` 显式教学、`/doctor` 审计记忆层级、**"dreaming"后台子代理巩固**（甚至这个词都和 openclaw 用的一样）、大扫除前自动备份当前仓库。

## 反直觉发现

**发现一：四个起点，同一个形状。** 终端工具（ClaudeCode）、个人助手（openclaw）、中间件（mem0）、学术论文（Letta）——四个完全不同的出发点，2026 年收敛到：**人可读的文件或记忆块 + 后台巩固 + 保守写入**。这与本库 44 仓全量调查的结论互相印证（`topics-memory-3Kplus/00-总览` 六条共识，其中第 3 条原话是"**写入保守主义被反复独立发明**"）。连命名都收敛了：openclaw 的 dreaming 和 Letta 的 dreaming 是同一个东西——sleep-time compute 的工程化。

**发现二：mem0 的"退步"是进步。** 从 v2 的四操作（ADD/UPDATE/DELETE/NOOP）退到 v3 的只加不删，看起来是功能缩水，实则是承认了一个深刻事实：**让 LLM 在写入时做冲突裁决，是信息丢失的主要来源**。openclaw 用另一种方式表达同一件事：允许模型重写 MEMORY.md，但旧条目损失超 25% 就整体拒绝、回退 append-only。一个禁止删，一个限制删——殊途同归的写入保守主义。

**发现三：调参真相只在代码注释里。** openclaw 文档写 trigger 阈值 0.72，代码实际 0.65（`trigger-recall.ts:13-18`），注释里藏着完整实验记录：20 个触发词/50 条无关消息的合成语料上，0.65 零误报，0.72 会误杀合法改写，0.68 是单词触发的理论上限（0.85×0.8）。连文档极其完善的顶级项目，**魔数的最终裁判所也是代码注释，不是文档**。

**发现四：记忆可能是负债。** 44 仓调查里最反直觉的一条实证：Agent-S 四代演进中，**删掉记忆+加强推理反而涨分**——记忆系统的增量必须超过它引入的检索噪声，否则是负资产。mem0 自己的 BEAM 基准（1M/10M token 规模）也承认：10M 规模下 temporal reasoning、event ordering、multi-session reasoning 是全领域未解难题，64.1 分（满分 100）。

## 我的观点：谱系其实是一个坐标系

把三派放进三维坐标系：**检索强度**（grep → 混合+重排）× **写入治理**（无 gate → 确定性 gate → ADD-only）× **可见性**（服务黑箱 → 人可读文件）。

2026 年的共识底部已经清楚：人可读、后台巩固、保守写。真正的分歧在顶部——**信任模型**。ClaudeCode 信任人（文件就是文件）；openclaw 信任制度（溯源+gate，不信任任何单次模型判断）；mem0 信任中间件（应用不管，我负责）；Letta 信任分工（专门的记忆 agent）。

选型其实是选信任模型：个人开发者和本地终端 → 极简派；always-on 个人助手（7×24 挂在聊天频道里，会被投毒）→ 治理派；多 agent 多租户平台 → 服务派。

三个开放问题：①**多语言**——openclaw 的"回忆意图"检测 14 条正则全英文，中日韩是补丁（中文用户 escalate 命中率存疑），整个领域的清洗规则都是英文中心；②**评估乱象**——44 仓审计发现各家自报数字口径互不可比（recall@5 混 QA 准确率），BEAM 是唯一在 1M+ token 规模测的；③**遗忘的数学**——FSRS/艾宾浩斯的 decay 数学在 SRS 领域已成熟 375 行可实现，但 AI 记忆至今没人认真用（44 仓调查称之"明牌机会"）。

---

**本文证据链**：ClaudeCode 记忆无向量库 → `Agent框架案例/ClaudeCode源码深读/`；openclaw 五层/dreaming/阈值 → `Agent框架案例/openclaw/notes/06-memory体系深读.md`（钉版 f612675284）；mem0 内部 → 本库 `mem0开源记忆层/` 专档 + 官方 docs（2026-08）；Letta → docs.letta.com + sleep-time compute 博客（2025-04）；44 仓收敛共识 → `topics-memory-3Kplus/00-总览与横向综合.md`。
