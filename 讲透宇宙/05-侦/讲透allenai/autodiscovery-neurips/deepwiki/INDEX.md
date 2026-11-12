# DeepWiki 索引 — allenai/autodiscovery-neurips

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 20 页 · 全文 164069 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Key Concepts and Terminology](1.2-key-concepts-and-terminology.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 MCTS Discovery Loop](2.1-mcts-discovery-loop.md)
  - [2.2 Multi-Agent Orchestration](2.2-multi-agent-orchestration.md)
  - [2.3 Belief System and Bayesian Reward](2.3-belief-system-and-bayesian-reward.md)
- [3 Dataset Integration](3-dataset-integration.md)
  - [3.1 Metadata Formats](3.1-metadata-formats.md)
  - [3.2 Dataset Loading and Experiment Initialization](3.2-dataset-loading-and-experiment-initialization.md)
- [4 Configuration Reference](4-configuration-reference.md)
- [5 Output, Persistence, and Utilities](5-output-persistence-and-utilities.md)
  - [5.1 State Persistence and Resumption](5.1-state-persistence-and-resumption.md)
  - [5.2 Deduplication and CSV Export](5.2-deduplication-and-csv-export.md)
  - [5.3 MCTS Tree Visualization](5.3-mcts-tree-visualization.md)
  - [5.4 Logging Infrastructure](5.4-logging-infrastructure.md)
- [6 Structured Outputs and LLM Utilities](6-structured-outputs-and-llm-utilities.md)
  - [6.1 Pydantic Schemas](6.1-pydantic-schemas.md)
  - [6.2 LLM and Infrastructure Utilities](6.2-llm-and-infrastructure-utilities.md)
- [7 Glossary](7-glossary.md)

## 附：结构清单外的页
- [Agent Roles and Prompts](x1-agent-roles-and-prompts.md)
- [Belief Distribution Formats](x2-belief-distribution-formats.md)
- [Conversation Flow and Transitions](x3-conversation-flow-and-transitions.md)
- [MCTSNode Data Model](x4-mctsnode-data-model.md)
- [Reward Calculation and Surprisal](x5-reward-calculation-and-surprisal.md)
- [Selection Strategies](x6-selection-strategies.md)
