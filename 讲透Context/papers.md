# papers.md —— 讲透Context 素材核实清单（2026-08-26）

> 铁律执行记录：每条 arXiv ID 标注核实方式。✅一手 = 直接看到 arxiv.org html/abs 页或论文 bib；
> 🔁转引 = 仅从二级来源看到编号，章节引用前须 webfetch abs 页再核实。

## 一、综述与理论（Ch00/10 的骨架）

| ID | 标题/内容 | 核实 | 关键结论 |
|----|----------|------|---------|
| arXiv 2507.13334 | A Survey of Context Engineering for LLMs（Mei et al., 1400+ 篇） | ✅一手（arxiv html v1 摘要全文） | 三组件：Retrieval&Generation / Processing / Management；四实现：RAG / Memory / Tool-Integrated / Multi-Agent；核心 gap：**理解强 vs 长输出弱的不对称** |
| arXiv 2608.01326 | Context Compaction Theory（2026-08） | ✅一手（arxiv html v1 摘要全文） | compaction 两游戏：Selection（选子集）vs Generation（任意摘要）；**Generation ≡ 单向通信复杂度**（Thm 1）；Selection 比 Generation 多花 Θ(log n) 预算（Thm 3）；实测 Anthropic compaction endpoint 在 set membership 上接近随机猜，输给同尺寸 Bloom filter |
| arXiv 2512.13564 | Memory in the Age of AI Agents（45 位作者，2026-01） | ✅一手（alphaxiv 摘要+bib） | Forms(token/parametric/latent) × Functions(factual/experiential/working) × Dynamics 分类；"context engineering 把窗口当资源优化，agent memory 管窗口之外的知识演化" |
| arXiv 2602.06052 | Agent Memory in the Second Half（TMLR 2026-07，v4 2026-08-04） | ✅一手（alphaxiv 摘要） | memory 是自进化基座；RL-learned context curation；skills = 可移植外显记忆 |
| NAACL 2025 Long 368 | Prompt Compression for LLMs: A Survey（Li et al.） | 🔁转引（redhat memory-hub survey + aclanthology 链接） | 压缩方法分类法；写作时直接引 aclanthology.org/2025.naacl-long.368/ |

## 二、Compaction 与压缩（Ch05/06 的弹药）

| 来源 | 标题/内容 | 核实 | 关键结论 |
|------|----------|------|---------|
| arXiv 2510.04618 | ACE: Agentic Context Engineering（Stanford/SambaNova/UCB） | ✅双源（redhat survey + InfoQ 报道） | Generator/Reflector/Curator 三分工；delta 更新防"brevity bias"与"context collapse"；+10.6% agent 基准；开源 DeepSeek-V3.1+ACE 追平生产 GPT-4.1 agent |
| arXiv 2510.00615 | ACON: 优化长程 agent 的观察与历史压缩（2025-10） | ✅双源（redhat survey + 直接链接） | 同时压环境观察与交互历史 |
| Anthropic Cookbook（platform.claude.com，2026-03-20） | Memory vs Compaction vs Tool Clearing | ✅一手（全文抓取） | 三原语操作粒度：compaction=**全转录**操作 / clearing=**子转录**（只换 tool_result 块）/ memory=**窗口外**；`compact_20260112` beta：触发阈值默认 150K、最小 50K |
| redhat-ai-americas/memory-hub research | Context Compaction & Agentic CE Survey（2026-04-10） | ✅一手（GitHub 全文） | Factory.ai 实测：结构化摘要 3.70 vs 自由摘要 3.44（Anthropic）/3.35（OpenAI），36,611 消息；**30K token 后退化加速，70% 利用率主动压缩优于 95% 被动**；Anthropic server-side 压缩比 99.3% 但不可解释 |
| arXiv 2307.06945 / 2310.05736 / 2403.12968 / 2310.06839 | ICAE / LLMLingua / LLMLingua-2 / LongLLMLingua | 🔁转引（redhat survey 列表） | 压缩技术线：4× 上下文压缩（ICAE）、token 级提示压缩（LLMLingua 系）；写 Ch05 时核实 |
| arXiv 2504.19413 / 2505.22101 / 2507.03724 | Mem0 / MemOS（两版） | 🔁转引（redhat survey 列表） | 记忆系统产品线；写 Ch07 时核实 |

## 三、Context Rot 与长上下文实证（Ch02/03 的骨架）

| 来源 | 标题/内容 | 核实 | 关键结论 |
|------|----------|------|---------|
| Chroma 技术报告（research.trychroma.com/context-rot，2025-07-14） | Context Rot: How Increasing Input Tokens Impacts LLM Performance（Hong, Troynikov, Huber） | ✅一手（官网全文 + GitHub README + bibtex） | **注意：是 tech report，无 arXiv ID，勿虚构**。18 前沿模型；4 实验：语义 needle（相似度越低退化越快）/distractor 非均匀伤害/**haystack 有序反而伤性能（shuffle 提升）**/LongMemEval/重复词复制；结论："Whether relevant information is present is not all that matters; **how it is presented matters more**" |
| arXiv 2307.03172 | Lost in the Middle（Liu et al. 2023） | 🔁转引（Ch02 引用；定稿前 webfetch 核实） | 20 文档 QA 的 U 型位置曲线——本单元 E2 词面 needle 未复现（任务太易），语义 needle 待验 |
| arXiv 2410.10813 | LongMemEval | ✅转引升级（chroma-core/context-rot README 直接引用） | 会话式长上下文 QA 基准 |
| NoLiMa / AbsenceBench | 非词面匹配 needle / 缺失检测 | 🔁转引（Chroma 报告内引用） | NIAH 高估长上下文能力的两条证据线；E2/E3 本地复证此批评；写 Ch03 扩展时补 ID |

## 四、工程方法论（Ch04/07/08/09/11 的骨架，全部一手）

| 来源 | 关键结论 |
|------|---------|
| Anthropic《Effective Context Engineering for AI Agents》 | 定义"策展论"；长时程三技术：**compaction / structured note-taking / sub-agent**；subagent 探索数万 token 只回传 1-2K 蒸馏摘要；compaction 提示词调法：先最大化 recall 再修 precision |
| Anthropic《How we built our multi-agent research system》 | "The essence of search is compression"；lead agent 先把 plan 存 memory 再派 subagent；effort 分级规则（简单 1 agent 3-10 calls / 复杂 10+ subagents） |
| Anthropic《Effective Harnesses for Long-Running Agents》 | initializer agent + coding agent 双段式；claude-progress.txt + git log = 跨窗口交接面；JSON 特性表比 Markdown 更不容易被模型乱改 |
| Anthropic《Harness Design for Long-Running Apps》 | **context anxiety** 概念（接近窗口上限时提前草草收工）；context reset（换新窗口+结构化交接）vs compaction（同窗口压缩）的区别与取舍 |
| dair-ai 指南 context-engineering 三篇（`_source/`） | Search Planner 案例：schema 字段表+日期注入+JSON 示例自动生成 schema；deep research agent 的单 agent 过载→分工改造 |

## 五、前沿系统（Ch10 素材）

| 来源 | 标题/内容 | 核实 | 关键结论 |
|------|----------|------|---------|
| arXiv 2608.21690 | Scroll: Context as an Environment（2026-08） | ✅一手（arxiv html 摘要全文） | 会话=可执行 Session Environment：append-only Event Log + 持久 Python kernel；**eviction ≠ 删除**（地址锚定可回溯）；LOCA256K 超最佳系统 37.4pp |
| preprints 202605.2065 | Context Compression for LLM Agents: Survey（2026-05-29） | ✅一手（preprints 页摘要） | 三维分类：压什么/怎么压/谁触发；失败三型 **F1 压缩前决策错 / F2 压缩中信息损失 / F3 压缩后访问失败**（Ch05 直接采用） |

## 六、本仓库活案例（Ch11 现成证据，零成本）

- `讲透Skills/experiments` E2：38 skills 渐进披露 L1 清单 3,626 tok vs 全量 52,606 tok = **省 93.1%**（= Anthropic "progressive disclosure" 的本地实证）
- `AGENTS.md` + memory blocks + `RESUME-*.md`：跨会话 context 接力的三级架构（宪法/档案/断点）
- ClaudeCode 源码研究（讲透Skills articles/14）：清单=窗口 1% 预算、desc 250 字符硬截断（工业界 context budget 管理实例）
