# E2E 演练 ④：接口检验报告（dry run finding）

> 检验对象：SC → PRC → DEC 三契约接力（本目录 ①②③）。方法：逐字段追踪上下游承接 + 回流路径完整性。
> 结论先行：**契约下行链（SC→PRC→DEC）字段衔接顺畅，六个检验点全过；回流链（Evidence→PIC→CEO）发现 3 个缺口，已回修 AGENT-OS.md（v1.1）。**

## 下行链检验（6/6 通过）

| # | 检验点 | 结果 | 证据 |
|---|---|---|---|
| 1 | SC.open_questions → PRC 承接 | ✅ | Q1→五维归因表、Q2→留存 -23pp、Q3→门槛经济学推导（全转译为产品证据） |
| 2 | SC.avoid/constraints → PRC 传递 | ✅ | avoid（不换旗舰）落到 cql_seat；constraints（P95/成本/隔离）直传 PRC.constraints→DEC.constraints |
| 3 | PRC.open_questions → DEC 承接 | ✅ | OQ1→竞争假设 H1/H2/H3 + T1-T3 判决实验；OQ2/OQ3→T4 实施路径 |
| 4 | PRC.success_definition → DEC.metrics 对齐 | ✅ | 三门槛逐字对齐（0.95/0.02/0.03），分片要求进 acceptance |
| 5 | PRC.domain_area → Domain 路由命中 | ✅ | 命中 讲透RAG/ + 讲透Agent/ + 应用全景/06，L2 领域模型来自知识源而非记忆 |
| 6 | DEC.trace 双向可追溯 | ✅ | product_goal 回传 + SC.churn→T6 映射；任何 code change 可上溯公司目标 |

**附带验证**：反 PM 权力链条成立——CEO 在源头否决"换旗舰模型"（下注纪律），PM 用归因数据支持（53% 投诉与模型无关），Domain 用问题判型第三次否证（三假设均非模型问题）——**三层各自独立地杀掉了同一个坏方案**，这是分权设计的预期收益。

## 回流链缺口（3 个，已修复）

| # | 缺口 | 严重度 | 修复 |
|---|---|---|---|
| G1 | **PIC 无 schema**——AGENT-OS 只定义 SC/PRC/DEC 三契约，Evidence 回流载体只有名字 | P0 | AGENT-OS §二新增 ④PIC schema（验证结果/对门槛影响/产品解读/剩余未知/建议） |
| G2 | DEC 的"剩余未知"向上回流无承接字段——诊断产生的假设变更（如混合根因需重排预算）没有明确通道 | P1 | PIC 加 `escalations` 字段（触发 CEO amend 决策）；闭环流程补第 8bis 步 |
| G3 | 假设/预算变更回 CEO 后，Decision Memory 条目怎么改没有约定（防止静默改写历史） | P2 | AGENT-OS §三补规则：变更 = decision-log 新增 `type: amend` 条目引用原 id，不覆写 |

## 复演成本与结论

- 三契约接力延迟（人读+写）：SC→PRC 一次交接确认（open_questions 是有效接口——PM 不用猜 CEO 要什么证据）；PRC→DEC 同样。
- 最大摩擦点：PRC.data_status 的"缺"清单需要 PM 提前知道 Domain 能建什么（200 条错误集）——**接口知识跨界泄漏**，可接受（PM 的 03 章素养覆盖），但新用户需培训。
- 结论：宪法 v1.0 下行链可用；v1.1 修复回流链后，全链闭环（含演练）**通过**。

## 本案例的教学价值

1. 三层如何各自独立杀死"换旗舰模型"（分权红线的实证）。
2. 五维可信度归因 → 三个竞争假设 → DAG 任务的完整编译路径（PRC open_questions 是接口的枢纽字段）。
3. 版本共存（v37/v12）这类**领域规则的编译发现**——L2 阶段才浮出的知识，PRD 阶段不可见（四层编译不跳层的理由）。
