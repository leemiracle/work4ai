# gpt-researcher 深读卡 —— 把"规划→并行爬取→压缩→成文"跑成一条流水线的自主研究 Agent

> **定位**：GPT Researcher 是受 Plan-and-Solve 与 RAG 论文启发的自主研究 Agent：先用 STRATEGIC_LLM 把大问题拆成子查询，再并行多源爬取（web/local/hybrid + MCP），经 embedding 相似度压缩上下文，最后由 SMART_LLM 综合成带引用的研究报告。单 Agent（`GPTResearcher` 门面 + 7 个 Skill Managers）之外还有一套 LangGraph 版多智能体编辑部（Chief Editor → Researcher/Reviewer/Reviser/Writer/Publisher）。深度绑定 Tavily 搜索生态，支持 25+ LLM providers。

> **本地**：`repos/gpt-researcher`（assafelovic/gpt-researcher）｜**深读**：deepwiki 75 子页归档 `deepwiki/gpt-researcher/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 入口层 | pip 库 / FastAPI+WebSocket 服务 / NextJS 前端 / Claude Skill | `main.py`、`gpt_researcher` 包、`frontend/`、`npx skills add` |
| 编排层 | 研究生命周期门面、状态与成本跟踪 | `GPTResearcher`（agent.py:36）、`Config`（env > config.json > 默认） |
| Skill 层 | 规划/爬取/压缩/策展/写作各管一段 | `ResearchConductor`、`BrowserManager`（WorkerPool 并发 15）、`ContextManager`、`SourceCurator`、`ReportGenerator`、`DeepResearchSkill`、`ImageGenerator` |
| 动作层 | 可复用的原子操作 | `choose_agent()`、`plan_research_outline()`、`get_search_results()`、`scrape_urls()` |
| 智能层 | 三层 LLM 策略 / 提示词族 / 记忆 | `GenericLLMProvider`（25+ providers）、`FAST_LLM`/`SMART_LLM`/`STRATEGIC_LLM`、`get_prompt_family()`、`Memory`(embeddings) |
| 数据层 | 检索器（默认 tavily）/ 文档加载 / 向量库 / MCP | `retrievers/`、`DocumentLoader`、`VectorStoreWrapper`、`MCPRetriever`（fast/deep/disabled 三策略） |
| 多智能体层 | LangGraph 编辑部（STORM 式） | `multi_agents/`：`ChiefEditorAgent` + 8 专职 Agent，`ResearchState`/`DraftState`；另有 AG2(AutoGen2) 替代实现 |

## 二、核心机制

1. **Plan-and-Solve 查询分解 + 三级降级**（来源：9.1 Query Planning / 6.3）：先用 `retrievers[0]` 做一次初始搜索拿基线上下文 → `plan_research_outline()` 用 `STRATEGIC_LLM`（默认 `openai:o4-mini`，`REASONING_EFFORT=medium`）生成子查询（`MAX_ITERATIONS=3`）；失败先按 `STRATEGIC_TOKEN_LIMIT=4000` 重试，再 fallback 到 `SMART_LLM`（gpt-4.1）；MCP 是唯一检索器时直接跳过分解（MCP server 自带内部工具调用）。`choose_agent()` 用 SMART_LLM 生成 persona JSON，`json_repair` 容错解析。
2. **并行采集 + 全局限流**（来源：9.2 Parallel Sub-Query）：`asyncio.gather(*[_process_sub_query(sq)])` 并行子查询；`BrowserManager` 持 `WorkerPool`（`MAX_SCRAPER_WORKERS=15`，信号量）并挂 `GlobalRateLimiter` 跨实例强制最小延迟；MCP 策略三选一——`fast` 只跑一次原查询并缓存于 `_mcp_results_cache` 复用、`deep` 每个子查询都跑、`disabled` 跳过；最后 `_combine_mcp_and_web_context()` 合并结构化 MCP 结果与非结构化 web 内容。
3. **Embedding 相似度压缩管线**（来源：9.3 Context Management）：总字符 < `COMPRESSION_THRESHOLD`(8000) 走 fast path 直接返回；否则 LangChain 管线 `RecursiveCharacterTextSplitter`(chunk 1000/overlap 100) → `EmbeddingsFilter`(余弦相似度阈值 0.35) → `pretty_print_docs`（带 URL/title 的结构化上下文）；`WrittenContentCompressor` 用更高阈值 0.5 找"已写过的高相关段落"，防 detailed_report 重复；embedding 费用经 `estimate_embedding_cost` 回写 `add_costs` 全程记账。
4. **LangGraph 编辑部：五阶段 + review-revision 状态机**（来源：10.1/10.3）：`ChiefEditorAgent` 编排 browser→planner→human（反馈循环，`max_plan_revisions=3` 超限抛 `MaxPlanRevisionsExceededError` 防死循环）→ 并行分节研究 → writer → publisher；每节一个 `DraftState` 的 `StateGraph`：`researcher → reviewer ⇄ reviser`，条件边 `review is None → END`，即"审稿人点头才算过"，Reviewer 对复审 prompt 明确要求"仅致命问题才再提意见"防无限迭代。

## 三、与讲透系列的对位

| gpt-researcher 机制 | 讲透系列/技能对位 |
|---|---|
| Plan-and-Solve 子查询分解（STRATEGIC_LLM + 降级链） | `deep-research` 技能 5 阶段之 **plan**（本身就是 gpt-researcher 式工作流） |
| `asyncio.gather` + WorkerPool + RateLimiter 并行爬取 | Python asyncio 章节 + 铁律 8（同步阻塞 IO 必 `asyncio.to_thread`，否则并行退化串行——此仓库是正面教材） |
| EmbeddingsFilter / 递归分块 / 相似度阈值压缩 | 讲透 NLP 的 RAG 检索压缩（chunk/overlap/余弦相似度的工程默认值范本） |
| 三层 LLM（FAST/SMART/STRATEGIC）成本分层 | llm-mastery / prompt-engineering：按任务难度路由模型的成本工程 |
| LangGraph `DraftState` review-revision 状态机 | agent-development 的多智能体协作（LangGraph 条件边 + 防死循环设计的现成案例） |
| SourceCurator LLM 策展 + 引用跟踪 | deep-research 之 **synthesize/report**：来源可信度排序与引用规范 |

## 四、关键入口

```python
# pip 包（库用法）
from gpt_researcher import GPTResearcher, ReportType

researcher = GPTResearcher(
    query="...", report_type="research_report",  # detailed_report / subtopic_report / deep
    report_source="web",                          # web / local / hybrid / vectorstore
)
await researcher.conduct_research()   # 规划→并行爬取→压缩→策展
report = await researcher.write_report()          # SMART_LLM 综合成文
```

```bash
# 服务/前端
python -m uvicorn main:app            # FastAPI + WebSocket(8000)
docker-compose up --build             # gptr-nextjs(3000) + backend(8000)
python multi_agents/main.py           # LangGraph 多智能体模式（task.json 配置）
```

## 五、深读子页地图（75 页精选 6）

| 子页 | 价值 |
|---|---|
| 3.2 ResearchConductor and Workflow | 研究主引擎：路由 web/local/hybrid + 关键默认值表 |
| 6.3 Three-Tier LLM Strategy | FAST/SMART/STRATEGIC 成本分层与 fallback 链 |
| 9.3 Context Management and Compression | RAG 压缩管线完整参数（0.35/8000/1000+100） |
| 10.1 ChiefEditorAgent Orchestration | LangGraph 五阶段编排 + HITL 反馈环 |
| 10.3 Review-Revision Workflow | `review is None → END` 质量环状态机源码级拆解 |
| 13.2 WebSocket Protocol Reference | 流式进度协议（前后端实时通信契约） |

## 六、与"我们"的关系（一句话）

它是 `deep-research` 技能的"原型机"——我们 5 阶段工作流（plan→search→scrape→synthesize→report）的每个工程细节（子查询分解、并行限流、embedding 压缩、审改环）都能在这里找到生产级参考实现。

---
生成：2026-08-21 · deepwiki 75 页全归档
