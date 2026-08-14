# 11 · Agent / 自动化场景

> Agent 是模型能力的"终极杠杆"——不只回答，而是**自主完成多步任务**（检索→决策→执行→验证）。2026 年 67% 企业已上生产 agentic AI。本类 5 个场景，是前面所有场景的"高阶自动化形态"。

---

### 场景 49：跨系统工作流 Agent（企业核心）
- **痛点**：流程跨多个系统（ERP/CRM/邮件），人工搬运数据、易错。
- **输入 → 输出**：业务事件 → 跨系统编排执行 + 审计轨迹。
- **模型方案**：**Agent + MCP（工具协议）+ 知识库 SOP + 人工审批**。这是 2026 企业 agent 黄金范式。
- **真实案例**：**Klarna** agent = **853 FTE** 工作量（aihive，2026）。**Rivian**（Strands + Bedrock AgentCore + MCP）—— SOP 存知识库、agent 检测 SAP 异常→算计提→生成待审凭证，月末省 15+ 天（AWS，2026）。**Sanofi** Concierge → 50K 周活/72K 月活，1100 万对话，90% 好评，演进成"agent hub"统一入口替代数千遗留应用（AWS，2026）。
- **工具栈**：Strands Agents / LangGraph / Bedrock AgentCore + MCP + 知识库 + 审批。
- **陷阱**：权限蔓延（agent 持过多写权限 = 攻击面）→ 最小权限 + 时限；**确定性 vs 生成**平衡（Kogan 教训：关键流程确定性脚本，模糊处用 LLM）。
- **起步 MVP**：选一个跨 3 系统的重复流程，SOP 文档化，让 agent 按文档跑，人工审。

### 场景 50：数据分析 Agent（自然语言查数）
- **痛点**：业务要数据但不会 SQL；IT 排队。
- **输入 → 输出**：自然语言问题 → SQL → 结果 + 可视化 + 钻取。
- **模型方案**：**Agent（Text-to-SQL + schema 检索 + 可视化）**。
- **真实案例**：**Jefferies** 交易助手 —— 交易员问"美国交易板块分布"，agent 生成 SQL + 饼图，内存数据库秒级响应；Python 做 LLM 实验、Java 做高吞吐业务处理（AWS，2026）。
- **工具栈**：Strands/LangGraph + Text-to-SQL + Bedrock Knowledge Bases（schema）+ BI。
- **陷阱**：SQL 错 → schema 检索 + 语法校验 + 只读连接；大表慢 → 内存数据库。
- **起步 MVP**：一个库的 schema 做知识库，让 agent 答业务问题，对比人工 SQL。

### 场景 51：研究助理 Agent（多源综合）
- **痛点**：研究/尽调/竞品分析要聚合大量来源。
- **输入 → 输出**：研究问题 → 多源检索 → 综合 → 引用报告。
- **模型方案**：**Agent（搜索→阅读→综合→引用）**。这是 `deep-research`/`research-companion` skill 的 Agent 化。
- **真实案例**：Perplexity/ChatGPT 搜索是消费版；企业版 → LangGraph + 搜索 API + RAG。
- **工具栈**：LangGraph/LlamaIndex + 搜索 API + 引用约束。
- **陷阱**：编造引用 → 强制真实 URL + 可点；来源过时 → 日期过滤；深度有限 → 多轮规划。
- **起步 MVP**：用 Agent 做一个竞品对比，逐条核对引用真实性。

### 场景 52：企业 AI 平台（统一入口）
- **痛点**：碎片化 AI 试点；员工不知用什么；数据孤岛。
- **输入 → 输出**：员工请求 → 统一对话入口 → 路由到专项 agent。
- **模型方案**：**平台架构（编排层 + 上下文工作室 + MCP 网关 + 治理 + 可观测）**。
- **真实案例**：**IBM** Enterprise Advantage on AWS —— 编排/上下文/工具网关/可观测全栈，90 天从评估到生产；金融/生命科学已落地（IBM，2026）。**Sanofi** Concierge 从工具演进成"公司主数字门户 + agent hub"（AWS，2026）。**Rippling** 6 个月全产品 AI-native，supervisor agent 协调 5-7 子 agent（read/RAG/action），百万用户（LangChain，2026）。
- **工具栈**：IBM Advantage / Bedrock AgentCore / 自建（编排 + MCP + 治理）。
- **陷阱**：碎片化试点 → 先统一编排层；治理后置 → 治理先行（Databricks：有治理的企业生产项目多 12×）；模型锁定 → 多模型架构。
- **起步 MVP**：先不建平台——选 1 个最高价值用例做到生产，沉淀模式再平台化（Kogan/Siemens/Rivian 都这么走）。

### 场景 53：多 Agent 协作（复杂任务分解）
- **痛点**：单 agent 干不了复杂跨域任务；上下文爆炸。
- **输入 → 输出**：复杂请求 → 多 agent 分工（读/RAG/行动）+ supervisor 协调。
- **模型方案**：**Supervisor + 专项子 agent**（读/RAG/行动分工）+ 上下文压缩。
- **真实案例**：**Rippling** —— supervisor + 5-7 子 agent，语义层先定域再注入技能，re-ranker 砍上下文 100-500×；关键洞察：LLM 复述长 ID 会幻觉 → 用 REPL 变量名传递而非原始字符串（LangChain，2026）。
- **工具栈**：LangChain Deep Agents / LangGraph supervisor 模式；可观测 → LangSmith。
- **陷阱**：上下文爆炸 → 语义层预筛 + 激进 re-rank；ID 幻觉 → 变量名传递；失败难调 → 分层 eval（离线/集成/部署门禁/连续）+ 半自动 self-healing。
- **起步 MVP**：一个跨 2 域的任务（如"查余额 + 查政策"），用 supervisor + 2 子 agent 试。

---

## 场景库总结：2026 企业 Agent 落地的五条铁律

走完 60 个场景 + 5 个 Agent 场景，2026 一手案例反复印证五条铁律：

1. **从一个窄用例起步，验证再扩**（Kogan/Siemens/Rivian/AMD 无一例外）。
2. **治理先行，不是后置**（有治理企业生产项目多 12×；ISO 42001 成门槛；78% 要求 human-in-the-loop）。
3. **数据/集成是真正瓶颈，不是模型**（遗留系统 61% 最大障碍；模型能力已不是瓶颈）。
4. **SOP 存知识库、agent 按文档执行、人工审批**（Rivian 黄金范式；业务改流程改文档不改代码）。
5. **确定性 vs 生成平衡**（Kogan：关键流程确定性脚本，模糊处用 LLM；过度确定性反脆弱）。

> **终极心法**：Agent 不是"替换人"，是"**重组工作**"——AI 执行重复任务，人专注判断/策略/风险（Swiftwater 法律；AMD HR；McLeod 医疗；Rivian 财务，全部同理）。能落地的 Agent，永远是"**人机协作 + 审计留痕**"的，不是"全自动黑箱"。

---

---

## 🔧 深度实操要点（本类场景）

> 本类场景的实操指引。通用骨架代码/评估清单/排错指南见 [00 深度实操手册总纲](00-深度实操手册总纲.md)。

- **决策速查**：跨系统工作流→Agent+MCP(D)；数据查询→Text-to-SQL agent；研究→多源agent
- **关键骨架**：骨架 D (Agent) — 本类的核心
- **评估要点**：任务完成率；人工降幅(Klarna=853FTE)；审计通过率
- **头号陷阱**：权限蔓延→最小权限+时限；过度自主→架构性human-in-the-loop(Tuskira)
- **进阶路径**：单agent→多agent协作→企业AI平台

**回到**：[场景库 README](README.md) ｜ [Part IV 能力地图](../17-模型工作能力地图.md) ｜ [Ch22 沟通与拓展](../22-沟通与拓展.md)
