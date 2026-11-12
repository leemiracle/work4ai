# 讲透Loop 论文与灰色文献核实清单

> 核实日期：2026-08-26。核实方式：websearch 直抓 arXiv HTML 全文 + arXiv 官方列表页交叉确认（当日 arxiv.org abs 页网络不通，项目已知坑）。
> 纪律：任何 ID 引用前必须本表在册；表外 ID 一律现场核实。

## 学术线（arXiv，按相关度排序）

| ID | 标题 | 核实状态 | 关键贡献 | 用在 |
|----|------|---------|---------|------|
| **2607.00038** | Stop Hand-Folding Your Coding Agent: Engineering the Loops that Replace Step-by-Step Prompting | ✅ HTML 全文抓取 | ① loop specification 定义：trigger/goal/verification/stopping rule/memory 五件套；② 五级验证阶梯；③ **Loop Library 50 个真实 loop 人工编码**：74% 命名终态 / 70% 自主验证 / 66% 可验证目标，但仅 22% 自动触发 / 20% 用具名 skills / 32% 持久记忆；④ 五个终态：success/no-op/blocked/stalled/exhausted；⑤ sandeco-loop skill（github.com/sandeco/prompts）；⑥ 反模式锚定 self-correction/reward hacking/model-as-judge 文献 | Ch02/Ch03/Ch05 |
| **2608.21884** | Loop Engineering: Building Blocks, Adoption, and Impact（JAWs@ASE 2026 workshop，2026-08-25 提交） | ✅ HTML 全文 + cs.SE 列表页双确认 | ① 首篇实证：36,710 仓扫描（36,645 有效），253 仓有 trigger（35 scheduled / 205 event / 13 both）；② 256 抽检 217 确认真跑 loop（精确率 0.868）= **0.59% 采用率**；③ **几乎无人提交 state file**（仅 2 个满足内容标准）——循环运行时状态游离在版本控制之外；④ 计划中 C1/C2/C3 自治度对照实验；⑤ 定义：调度或事件触发 + 机器可查停止条件 + 持久状态 + verifier sub-agent + token 预算 + 人工升级点 | Ch02/Ch06/Ch11 |
| **2607.13104** | Self-Improvements in Modern Agentic Systems: A Survey | ✅ HTML 全文抓取 | ① agent = 基础模型 + 支架（prompt/memory/tools/控制逻辑）的配置观；② 自改进形式化：A_{t+1}=IMPROVE(A_{1:t}; S_t)；③ 三类信号：内生示范 D_t / 内生评价 e_t / 外生探索 τ_t；④ 失败模式：confidently wrong 的自一致性塌缩、分解破坏约束、盲区放大；⑤ 防塌缩护栏：保留种子数据 / 外部验证器 / 多样性池扩充 / 不确定性驱动生成（TT-SI） | Ch08 |
| **2607.07663** | Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops（Mingguang Chen, Licheng Wang, Bo Qu） | ✅ HTML 全文抓取 | ① 1,250 篇 arXiv（2024-2026）两轴分类：改进对象（部署行为/策略/评估器/研究过程）× 循环闭合度（人在环→全闭环）；② **验证层级**：formal verifiers（最强）→ 外部工具 → 判官模型 → 过程奖励 → 内在自评（最弱）；③ 实证规律：自改进强度沿层级递减排列，失败模式（self-confirming loops / model collapse / 多样性塌缩）恰是层级违反的后果；④ bounded self-refinement（收敛、可评估、已是工业实践）vs open-ended RSI（受 grounding/collapse/compute 三重约束） | Ch03/Ch08 |

姊妹篇已核实（复用）：2604.24797（Mathlib 网络分析，MATH_LOOP_ENGINE 证据）、2503.23037（Agentic LLM 综述 v3：ReAct/Reflexion/Self-Refine/PHP/ToT 谱系）、2602.12430（26.1% 社区 skills 含漏洞——循环放大风险的证据，讲透Skills 已核实）。

## 灰色文献线（一手博客，按时间序）

| 日期 | 来源 | 核实状态 | 关键贡献 |
|------|------|---------|---------|
| 2025-09-30 | Simon Willison "Designing agentic loops"（simonwillison.net） | ✅（被 2607.00038 引用转述） | 民间先行版本；无公开 ROI 研究的经济警告 |
| 2026-06-07 | **Addy Osmani "Loop Engineering"**（addyosmani.com/blog/loop-engineering/ + addyo.substack.com/p/loop-engineering 双版 06-08） | ✅ 双版抓取 | **命名文**。"replacing yourself as the person who prompts the agent"；五构建块（automations/worktrees/skills/connectors/subagents）+ 第六记忆；/loop vs /goal 原语；maker-checker 用于停止条件本身（fresh model 判官）；Steinberger/Cherny 源流；"same loop, opposite results" 认知警告 |
| 2026-06-16 | LangChain "The Art of Loop Engineering"（langchain.com/blog） | ✅ 全文抓取 | **四层循环堆叠**：① agent loop（create_agent）→ ② verification loop（RubricMiddleware）→ ③ event-driven loop（cron/webhook）→ ④ hill climbing loop（trace→分析→改 harness，LangSmith Engine）；"外环的手伸进内环"；价值复合在 L3/L4；swyx loopcraft 引用；Satya：学习循环=组织护城河 |
| 2026-06-24 | DataScienceDojo "10 loop engineering design patterns" | ✅ 全文抓取 | **10 模式三分层**：基础（ReAct/Reflection/Tool Use/Prompt Chaining）→ 实践（**Ralph Loop**=确定性测试做退出条件+每轮重置上下文/Evaluator-Optimizer/Multi-Agent Supervisor）→ 生产（Circuit Breaker 停滞检测/Heartbeat+重叠锁/Bounded Execution+Context Engineering）；"多数生产故障来自跳过最后三个" |
| 2026-06-25 | aipatternbook.com "Loop Engineering" 词条 | ✅ 全文抓取 | 百科定位：loop eng 在 harness eng 上一层；"autonomy is capped by verification reach——验证到哪里，自治就到哪里"；Dark Factory 谱系 |
| 2026-06-25 | eesel.ai "Loop engineering explained" | ✅ 全文抓取 | 五杠杆映射：tools(ACI)/stopping/context/verification/guardrails；Anthropic 200+ 特征 passes:false 清单；Willison $5 Fly.io 预算沙盒；支持工单=近完美循环的跨域论证 |
| 2026-07-16 | vibeengines "The Loop Engineering Handbook" | ✅ 全文抓取 | **四形状**（Heartbeat/Cron/Hook/Goal，触发×停止二维）；**三守卫**（hard caps/机器可查条件/独立验证）；state 两规则（读帧写验·绝不在 run 中间写；事实非 vibes+resume-point）；成本=设计轴；goal loop 天然"keep going"最危险 |
| 2026-07-25 | Osmani 开发者八阶段修订版 | ✅（2608.21884 转述） | agency（单 agent 走多远）与 orchestration（多少 agent 谁协调）两维分离；自治是按任务的选择不是达成的等级；**验证成本=委托的上限** |

## 待核实（写 Ch07/Ch10 时用）

- [ ] swyx "loopcraft: the art of stacking loops" 原文（目前仅经 LangChain 转述）
- [ ] Peter Steinberger 原始列表（Osmani 文中引用的源头）
- [ ] Anthropic "Building effective agents"（2024-12）与 long-running agents 博客（eesel 转述的 200+ 特征清单出处）
- [x] DeepVerifier（ACL 2026 Findings）——✅ 2026-08-26 已核：aclanthology.org/2026.findings-acl.1243 一手 abstract（websearch 直抓）；rubric 分解验证 vs vanilla agent-as-judge/LLM judge 高 12-48% meta-eval F1；test-time 迭代收益 3-4 轮封顶后早停；已引用于 Ch03（arXiv ID 未查，ACL anthology 为稳定一手源，不影响引用）

## 引用纪律提醒

- 2607.00038 与 2608.21884 均为 **workshop/under review**，写引用时标注状态，不当作定刊
- 灰色文献的结论（如"验证是中央技能"）转述时注明是实践共识（gray literature largely agrees），不是实证定论——2608.21884 的贡献恰是指出"实践共识 + 证据真空"并存
