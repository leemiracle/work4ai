# 讲透 langchain-ai/open_deep_research

> A 层清库 #15（小仓全链一体 7 批）· 2026-11-02

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：194n/373e/5层/8步，0 issues，fingerprints 41@fb77e90f |
| 综合讲透 | `讲透.md`：4529 字 19 锚（含 mermaid 三层嵌套架构） |

**一句话**：LangChain 官方深度研究 agent——supervisor 规划+worker 并行研究的**三代演进活样本**（asyncio.gather 现行版 vs LangGraph Send legacy）。

**重磅勘误**：`deep_researcher.py:370` `or True:` 恒真——token 判定死代码，任何并行异常都降级"用已有 notes 出报告"；MCP 单服务器硬编码（utils.py:513 TODO）；配置优先级 env>UI。
