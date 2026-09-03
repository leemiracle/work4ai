# 讲透 Context：有限窗口里的信息设计学（Context Engineering）

> 知识卡宇宙：`讲透X` 系列 | 三层宪法：**直觉 → 公式 → 代码（bash 跑通）** | 五幕：直觉→数学→代码→不足→应用
> 定位：`讲透Prompt/` 的姊妹篇与升维——Prompt 研究**单次调用里一句话怎么写**，Context 研究**整个窗口里放什么、怎么放、何时换**。
> 🌱 2026-08-26 谱系升级：vanja.io 判断"决定什么进窗口的越来越是**图**"（The Next Layer After Context）——本单元的上一楼层见 `讲透Graph/`（五环谱系：Prompt→Context→Harness→Loop→Graph）。
> 本章证据标准：**每个知识点配一个真实可跑的实验**（`experiments/` 下 py + 结果 json/png），绝不停留在"博客说"。

## 为什么要有这个单元

Anthropic 的原话："Context engineering is the natural progression of prompt engineering"——
**从不断膨胀的候选信息宇宙里，为有限窗口策展最小高信号 token 集合的艺术与科学**（"find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome"）。本单元的三个增量：

1. **实证化**：Context Rot（输入越长越蠢）、位置效应、compaction 信息损失，全部用本地 Qwen2.5-0.5B + 智谱 GLM 复现成曲线，而不是复述 Chroma/Anthropic 的图；
2. **数学下场**：2026-08 的 Context Compaction Theory（arXiv 2608.01326）把 compaction 形式化为**单向通信复杂度**——本单元用 E6 让 Bloom filter 与 LLM 摘要在同等 token 预算下真刀真枪对决，这是全中文圈罕见的数学级复现；
3. **活案例**：本仓库自己就是 context engineering 现场——AGENTS.md、memory blocks、RESUME 断点续传、skills 渐进披露（讲透Skills E2 实测省 93.1% token）全部是 Ch04/Ch07/Ch11 的现成证据。

## 核心心智模型（一图流）

```
            候选信息宇宙（无限增长）
  ┌─────────────────────────────────────────┐
  │ system prompt · tools/MCP · RAG 检索     │
  │ 对话历史 · 记忆 · 工具结果 · agent 自述   │
  └──────────────────┬──────────────────────┘
                     │  策展（本单元的全部内容）
                     ▼
        ┌──────────────────────────┐
        │   上下文窗口（有限预算）    │   ← Context Rot：
        │   开头◆◆◆◆◆◆◆◆◆结尾    │      放进去 ≠ 用得上
        └──────────────────────────┘
                     │
                     ▼  三大逃生通道（Anthropic 长时程三技术）
        compaction（窗口内压缩）
        note-taking/memory（窗口外持久化）
        sub-agent（上下文隔离+蒸馏）
```

## 篇目表（目录宪法）

| # | 章节 | 核心实验 | 状态 |
|---|------|---------|------|
| 00 | 开场白：从 Prompt 到 Context——同一门实验科学的升维 | — | ✅ |
| 01 | [上下文窗口解剖学：token 都花在哪](01-窗口解剖学.md) | E1 窗口构成实测 ✅ query 占比 1%/渐进披露省 78% | ✅ |
| 02 | [位置效应：放进去 ≠ 用得上](02-位置效应.md) | E2 双模型 24 格全满=零结果 ✅ | ✅ |
| 03 | [★ Context Rot：越长越蠢的实证](03-ContextRot.md) | E3 干扰×长度崩塌+模型依赖 ✅ | ✅ |
| 04 | [组装：检索、结构化与渐进披露](04-组装.md) | E4 组装消融 ✅ 日期锚救 glm(0→4/4)不救 Qwen(全 0)；schema 救 Qwen 字段(0→6/6) | ✅ |
| 05 | [★ Compaction：压缩的艺术与三种失败](05-Compaction.md) | E5 F1/F2/F3+幻觉实测 ✅ | ✅ |
| 06 | [★ Compaction 的数学：通信复杂度下场](06-Compaction的数学.md) | E6 Bloom vs LLM 摘要 ✅ 97.9% | ✅ |
| 07 | [记忆：窗口之外的持久化](07-记忆.md) | E7 笔记接力对决 compaction ✅ 91.7%>83.3% | ✅ |
| 08 | [Sub-agent：上下文隔离与蒸馏率](08-SubAgent上下文隔离与蒸馏率.md) | E8 蒸馏悬崖 ✅ 抽取 1/2→67%/1/5→17% | ✅ |
| 09 | [Token 经济学：一次 compaction $13 的算术](09-Token经济学.md) | 成本模型三算术 ✅ | ✅ |
| 10 | [★ 前沿 2025-2026：ACE/ACON/Scroll/理论化](10-前沿2025-2026.md) | 六线综述（papers.md §一§二§五） | ✅ |
| 11 | [★ 活案例：本仓库自己的上下文工程](11-活案例-本仓库的上下文工程.md) | 现场分析（AGENTS/memory/RESUME/skills） | ✅ |
| 12 | [不足与展望：批判收尾](12-不足与批判收尾.md) | E1-E8 负面结果总账 | ✅ |

★ = 用户重点主题（Context Rot / Compaction 及其数学 / 前沿 / 活案例）。
**诚实状态（2026-08-26 收官）**：E1-E8 八实验全跑通（json+png），00-12 十三章全写完嵌实测数字，篇目表物理链接化。断点档案见 `RESUME-0826.md`。

## 实验环境（与讲透Prompt 同一基座，真实可复现）

- **本地**：Qwen2.5-0.5B-Instruct（transformers, CPU, `~/ai/models/`，thread=1 铁律）
- **API**：智谱 GLM（glm-4-flash / glm-5 thinking off），密钥走 opencode auth.json，绝不硬编码
- **铁律**：①小模型 thread=1 ②实验独立可跑 ③结果存 json+png ④arXiv ID 全部核实（见 `papers.md`）⑤长实验前台跑 timeout≥1500s

## 与讲透Prompt 的分工（互不重复）

| 问题 | 讲透Prompt | 讲透Context |
|------|-----------|-------------|
| 研究对象 | 单条 prompt 的措辞/结构 | 整个窗口的信息构成 |
| 典型技巧 | CoT/few-shot/ToT/ReAct | compaction/memory/sub-agent/检索组装 |
| 失败模式 | prompt 注入/敏感性 | Context Rot/位置盲区/压缩失真 |
| 数学接口 | OPRO 优化循环 | 通信复杂度/Bloom filter（E6） |

## 挂网（本单元的桥）

- 上游：`../讲透Prompt/`（Ch01 参数与 Ch02 few-shot 是本单元 Ch02 位置效应的实验基座）
- 下游：`../讲透Agent/`（harness 把 context 当资源管理）、`../讲透Agent/讲透Skills/`（E2 渐进披露=本单元 Ch04 活证据）、`../讲透KV Cache/`（窗口之外的机器级"记忆"）
- 横向：`../top-math-courses/MATH_LOOP_ENGINE.md`（E6 是 reward=机器可验证的范例）、`../讲透信息论/`（压缩与信息损失的物理学）
- **运行环境层（2026-08-26 新建）：`../讲透Harness/`**——工程四部曲收官（Prompt→Context→Loop→Harness）：C 组件（上下文管理）在该单元被放进带验证与账本的运行循环做消融；其 E3 崩溃恢复=compaction/memory 之外的第三条逃生通道（状态账本）的实测
- **系统层（2026-08-26）：`../讲透Graph/`**——五环谱系（Prompt→Context→Harness→Loop→Graph）收口环："决定什么进窗口的越来越是图"。同构证据：Graph E3 bi-temporal（作废不删除）与本章 E7 的时间戳/弃权教训；Graph E2 拓扑税与本章 Ch09 的 O(N²) 历史税是同一平方律的两侧

## 来源与核实

- 3 篇源文存档 `_source/`（2026-08-25 抓自 dair-ai/Prompt-Engineering-Guide，MIT）
- 关键论文与工程报告的逐条核实状态见 `papers.md`（2026-08-26）；Anthropic/Chroma 博客为官方一手
