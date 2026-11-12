# DeepWiki 索引 — anthropics/cwc-long-running-agents

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 16 页 · 全文 100362 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Repository Layout and Runtime State Files](1.2-repository-layout-and-runtime-state-files.md)
- [2 Harness Primitives and Quality Loop](2-harness-primitives-and-quality-loop.md)
  - [2.1 Default-FAIL Evidence Contract](2.1-default-fail-evidence-contract.md)
  - [2.2 Fresh-Context Evaluator Subagent](2.2-fresh-context-evaluator-subagent.md)
  - [2.3 Session Handoff and Progress Tracking](2.3-session-handoff-and-progress-tracking.md)
  - [2.4 Operator Controls: Kill Switch and Steering](2.4-operator-controls-kill-switch-and-steering.md)
- [3 Claude Code Hook Implementation](3-claude-code-hook-implementation.md)
  - [3.1 Hook Wiring in settings.json](3.1-hook-wiring-in-settings.json.md)
  - [3.2 Hook Script Reference](3.2-hook-script-reference.md)
  - [3.3 Extending and Customizing the Gate](3.3-extending-and-customizing-the-gate.md)
- [4 Unattended Multi-Session Operation](4-unattended-multi-session-operation.md)
  - [4.1 Outer Loop: /goal, ralph-loop, and Wrapper Scripts](4.1-outer-loop-goal-ralph-loop-and-wrapper-scripts.md)
  - [4.2 Scaling Patterns: Sprint Contracts, Planner, Rubrics](4.2-scaling-patterns-sprint-contracts-planner-rubrics.md)
- [5 Glossary](5-glossary.md)
