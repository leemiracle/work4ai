# E2E 演练 ③：DEC — Domain Engineering Contract

> **执行者**：@domain-expert。输入：PRC（`2-PRC.md`）。四层编译依据：`AGENT-OS.md` §二③ + agent 定义六铁律。
> **领域路由检索**：`讲透RAG/`、`讲透Agent/`（管线与引用机制）、`讲透AI应用全景/06-企业AI应用.md`——未凭记忆编造管线细节。

## L1 Product Intent（回传）

`make_answers_verifiable`——每个论断可核证；门槛：引用覆盖 ≥95% / 幻觉 ≤2% / 过期引用 ≤3%。

## L2 Domain Model（企业知识库域，最小够用版）

**实体**：文档（带版本号 v*，共 120 家租户隔离）、段落 chunk、查询（事实型/流程型/数据型）、论断（答案里的原子事实）、引用锚点（论断↔chunk 的绑定）。
**领域规则**（编译的关键发现）：①**版本共存**是本域特有——v37 上线不删 v12，"引用了存在但过期"≠幻觉，是 freshness 违规（和 PRC 三门槛分别对应三类修复，不可混）；②**权限边界**跨租户/组，检索层过滤在 query 侧而非 corpus 侧（0 容忍项的工程位置）；③论断粒度 = 句级（引用锚点的最小单位）。
**异常路径**：语料无答案（→能力拒绝）；跨文档合成答案（引用锚点必须 ≥2）。

## L3 Technical Model（技术分解 + 竞争假设）

管线：`chunking → embedding → 检索(top-k) → rerank → 生成 → 引用对齐(现状:段落级裸引用)`

**三个竞争根因假设**（PRC OQ1，不提前收敛）：

| 假设 | 机制 | 可观测预言 | 初始置信（客服标签先验） |
|---|---|---|---|
| **H1 引用对齐缺失** | 生成内容与检索段落无 span 级绑定：答对了但用户点不开/对不上→被判"不可信" | 投诉案例中"答案正确但无锚点"占比高；裸引用点击率低 | 中高（34% 标签在其附近） |
| **H2 版本盲检索** | 检索不感知版本号，旧版段落因词面匹配占优 | 过期引用集中在"版本迭代频繁的文档"；freshness 19% 可解释 | 中（19%） |
| **H3 chunking 破坏结构** | 表格/跨页流程被切碎，检索到残段→答案缺限定条件 | 投诉集中在含表格/多级列表的文档 | 中低（12% completeness） |

**问题判型**（铁律 3）：H1=工程问题（对齐器）+H2=检索算法问题+H3=数据预处理问题——**三个都不是模型问题**，进一步否证"换旗舰"。

## L4 DEC 契约（Code Agent 任务包）

```yaml
domain: enterprise_kb_rag v1.0
product_goal: make_answers_verifiable          # 回传（trace 链头）
domain_problem: 论断不可核证（引用缺失/过期/残缺三路）
technical_problem: [H1 引用对齐, H2 版本感知检索, H3 结构感知 chunking]
hypotheses:
  - {id: H1, verify: 投诉案例锚点覆盖率统计, evidence: 87 条打标+200 条新集, confidence: 0.55}
  - {id: H2, verify: 过期引用×文档版本迭代率相关分析, confidence: 0.30}
  - {id: H3, verify: 投诉×文档结构(表格/列表)相关分析, confidence: 0.15}
repository: thinkbase-svc/modules/{ingest, retrieve, generate, cite}
task_graph:                                   # DAG（type 按宪法枚举）
  - {id: T1, type: inspect,      target: cite/ + retrieve/, action: 投诉 87 案例管线复现，统计锚点覆盖/版本分布/结构分布}
  - {id: T2, type: build_dataset, target: eval/, depends_on: [T1], action: 200 条分层错误集（行业3×查询类型3×错误维度5），标注锚点 ground truth}
  - {id: T3, type: evaluate,     target: -, depends_on: [T2], action: H1/H2/H3 竞争假设判决实验（各出独立证据，输出根因排序）}
  - {id: T4, type: modify,       target: cite/|retrieve/|ingest/, depends_on: [T3], action: 按判决实施：H1→span 级对齐器 / H2→版本感知打分 / H3→表格感知 chunking（可能并行多路）}
  - {id: T5, type: regression,   target: eval/, depends_on: [T4], action: 回归集（含权限边界 0 容忍集）+ 三门槛复测}
  - {id: T6, type: evaluate,     target: -, depends_on: [T5], action: 灰度 2 周（5 家低风险客户）投诉信号监控}
metrics:
  primary: {attribution_coverage: >=0.95, hallucination: <=0.02, stale_citation: <=0.03}   # 与 PRC.success_definition 对齐
  secondary: {p95: <=3.5s, cost_delta: <=15%, permission_violation: 0}
constraints: 权限违规回归=零容忍一票否决；T4 起任何改动先跑 T5 回归
acceptance:
  - cmd: pytest eval/test_trust.py -k "attribution or factuality or freshness"
  - expect: "ALL PASS（三门槛 + 分片 -1pp 容差）"
  - cmd: python eval/run_regression.py --zero-tolerance permission
  - expect: "0 failures"
trace:
  make_answers_verifiable -> 论断不可核证 -> [H1,H2,H3] -> [T4]
  SC.churn:0 -> PRC 在线投诉-50% -> T6 灰度信号
```

## 验证协议（Validator 与执行者分离）

- **离线**：`eval/test_trust.py`（T2 建的 200 条集 + 500 条人工 rubric 抽检，kappa≥0.8）——执行者不得自判
- **在线**：投诉率看板（分客户行业切片）+ 灰度对照
- **回流格式**（三段式）：结果（三门槛实测值）→ 领域解读（H 判决与根因结构）→ **[产品解读由 @ai-pm 补]** → PIC → @ceo

## 剩余未知（诚实清单）

① 三假设若判决为混合根因（H1+H2 并重），T4 预算需重排（回 CEO 备案）；② span 对齐器对生成延迟的影响未测（P95 余量 0.3s，紧）；③ 200 条错误集的标注 kappa 若 <0.8，门槛测量本身不可信（先修标注再修产品）。
