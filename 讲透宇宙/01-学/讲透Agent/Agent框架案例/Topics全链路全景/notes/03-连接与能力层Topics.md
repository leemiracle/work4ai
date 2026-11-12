# 03 · 连接与能力层 Topics：MCP/Tools（L3）/ Skills/Agents（L4 身份 + 执行机制）

> 本层是项目内已深潜的两站，本篇做**索引层浓缩 + topics 使用背景**，不重复深潜内容。深潜篇：[`../../MCP协议生态全景/`](../../MCP协议生态全景/README.md)（64,438 仓全套分析）、[`../../Skills生态全景/`](../../Skills生态全景/README.md)（11,492 仓全套分析）。

---

## L3 MCP/Tools 层——"agent 怎么获得手"

### topic:mcp（64,438）/ mcp-server（24,858）/ mcp-client（1,582）/ modelcontextprotocol（663）

- **使用背景**：MCP 双名现象最严重的领域——
  - `mcp`：社区通俗名，64,438 仓，覆盖全部 MCP 相关（server/client/网关/教程/awesome）；
  - `mcp-server`：**做一个 server 的人**的标签（把某 API/数据库/工具暴露给 agent），24,858 仓——想找"X 工具的 MCP 封装"用它最准；
  - `mcp-client`：客户端/宿主实现（1,582）；
  - `modelcontextprotocol`：官方长名（663），规范类/SDK 类仓库偏好打它——**检索规范演进与官方 SDK 用它，噪声最低**。
- **代表仓**：punkpeye/awesome-mcp-servers（92,548★，生态索引）；github/github-mcp-server（32,347★，平台官方样本）；mcp-use/mcp-use（10,502★，客户端框架）；microsoft/mcp-for-beginners（17,018★，教学）。
- **深潜**：协议 2026-07-28 无状态化重构、六赛道、SDK v2 格局 → MCP协议生态全景 notes/01-03。

### topic:tool-calling（1,933）/ function-calling（1,147）/ tool-use（1,123）/ mcp-security（347）

- **使用背景**：
  - `function-calling`：OpenAI 2023-06 功能名，工程界沿用——SDK 示例/工具封装/结构化输出交界的项目；
  - `tool-calling`/`tool-use`：通用名（Anthropic 倾向 tool use），与 function-calling 三者高度重叠，**检索时三选一即可，交叉去重**；
  - `mcp-security`：MCP 安全沙箱/审计/网关（347 仓）——2025 下半年起新兴， enterprises 采 MCP 前的安全审查需求（wassette WebAssembly 隔离方向）。
- **批判**：L3 的 topics 是"协议名 x 厂商用词"的矩阵，同一项目可能打其中 2-3 个——检索覆盖面要求高时用 OR 组合：`topic:mcp-server OR topic:function-calling`。

## L4 Skills/Agents 层——"agent 怎么获得手册与自主性"

### topic:ai-agents（74,088）/ agentic-ai（20,004）/ autonomous-agents（5,163）/ llm-agents（4,062）/ multi-agent（13,821）

- **使用背景**：五个"agent 大词"的分工——
  - `ai-agents`：**万仓级领域名**（74k），agent 相关的一切都会打，趋势观测用、找具体项目不用；
  - `agentic-ai`：产品化叙事词（20k），SaaS/低代码平台偏好（"agentic workflow"营销语境）；
  - `autonomous-agents`：AutoGPT 血统的自主执行框架（5,163）；
  - `llm-agents`：LLM 特化（4,062），研究味更浓（论文复现/benchmark）；
  - `multi-agent`：多智能体编排（13,821），LangGraph/CrewAI/AutoGen 生态。
- **代表仓**：langchain-ai/langchain（144,515★）；microsoft/autogen（60,505★）；crewAIInc/crewAI（57,291★）。
- **检索建议**：找编排框架 → `multi-agent` + `agent-orchestration`；找自主执行 → `autonomous-agents`；看生态大盘 → `ai-agents` 按 star 排序。

### topic:agent-skills（16,276）/ skills（11,492）

- **使用背景**：SKILL.md 标准的双名——官方源仓只挂 `agent-skills`（anthropics/skills 170,317★），社区两 name 混用；**标准词已反超通俗词**（16,276 > 11,492），生态在向标准名收敛。检索官方生态用 `agent-skills`，看中文社区/杂项用 `skills`（含人类技能学习旧语义，需过滤）。
- **深潜**：七赛道/20 仓卡/规范演进 → Skills生态全景 notes/01-03。

### topic:agent-memory（2,849）

- **使用背景**：跨会话持久记忆（memU/EverOS/MemOS 一类），与 L2 `memory-management` 的区别：这里是**为 agent 设计的记忆系统**（纯度高），那里是通用内存管理。项目内活案例：`../../Agent记忆系统案例/mem0开源记忆层/`。

### L4 执行机制补全：Loop（隐形家族）与 Graph 编排（产品代言家族）——2026-08-20 补测

上面四个小节是 L4 的"身份形态"面；agent 还有"执行机制"面——**循环怎么转**（loop）与**流程怎么编**（graph orchestration），8-19 首测遗漏、8-20 补测（数字见 01 总纲 §3.1）。

**Loop 家族——机制越基础，topic 越隐形**：

- `agent-loop` 156 / `agentic-loop` 36 / `llm-loop` 0 / `prompt-loop` 1 / `self-correction` 91 / `reflection` **2,098**。
- 悖论解读：loop 是一切 harness 的心脏（`LLM call → tool → observe → repeat`，harness工程手册 12 章骨架），但**没有大 topic 收纳它**——没有人给"人人都有"的机制打标签（同 `reasoning-model`=9）。反而循环的单个**环节**有名有姓：reflection（反思环节）2,098 是家族最大标签。
- **检索建议**：找 loop 机制项目用**环节词**（reflection / self-correction）或**框架名**（langgraph 仓里的 loop 实现），概念词全失灵。配套工程视角：`../../harness工程手册/` 06 验证金字塔（loop 内的反馈约束）+ 13 行为定位章（在 loop 里定位行为）。

**Graph 编排家族——范式被单一产品代言**：

- `graph-engineering`（概念名）**74** vs `langgraph`（产品名）**11,327**——代言比 153:1；概念层补充：`agent-orchestration` 2,704 / `agentic-workflows` 1,374 / `llm-orchestration` 714 / `workflow-orchestration` 552 / `agent-workflow` 384；第二产品极 `autogen` 784。
- 解读：图编排（state graph / DAG workflow / checkpoint 回放）在 topic 体系里被 LangGraph 一家代言——比 `vllm`/`inference`（0.55:1）极端两个数量级，说明"graph 即 LangGraph"已成社区心智默认。
- 交叉：`graph-rag` 339（GraphRAG：图既是编排结构又是检索结构，横跨 L4/L5）。
- **检索建议**：找图编排实现 → 直接 `langgraph`；要框架中立的综述 → `agent-orchestration` + `agentic-workflows` 双查；GraphRAG → `graph-rag` 并入 L5 RAG 检索组合。

## 连接层与能力层的分界（一句话）

L3 给 agent **手**（动态工具，MCP 协议连接，进程级）；L4 给 agent **手册与人格**（静态程序性知识，SKILL.md 文件级）+ **自主性**（框架级）——"MCP=插座、Skills=手册"的比喻在本项目两篇深潜中已锚定，topics 数据再次验证：两个生态的标签几乎不重叠（打 mcp-server 的仓很少打 skills，反之亦然——工具与知识自觉分仓）。

## 本层 5W2H 速览（详解见 06 篇）

- **Who**：工具作者（mcp-server）、平台方（官方厂牌 skills）、框架工程师（multi-agent）
- **When**：要接外部系统 → L3；要固化工作流 → L4 skills；要多角色协作 → L4 multi-agent
- **How much**：ai-agents 74k / mcp 64k / agent-skills 16k——连接与自主是 agent 时代两大主题，规模并列应用层之最

## refs
- GitHub Search API 实测 2026-08-19；代表仓 star repos API 同日（langchain 144,515 / autogen 60,505 / crewAI 57,291 / awesome-mcp-servers 92,548 / github-mcp-server 32,347 / mcp-use 10,502 / mcp-for-beginners 17,018）
- Loop/Graph 编排家族 16 topics 补测 2026-08-20（同法；crewai/self-refine 因 rate limit 未测成）；配套工程锚点 `../../harness工程手册/`（loop=harness 心脏）
- 深潜互链：MCP协议生态全景/、Skills生态全景/（同为 2026-08-19 快照）

*updated: 2026-08-19*
