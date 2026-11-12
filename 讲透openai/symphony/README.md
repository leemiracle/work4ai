# 讲透 openai/symphony

> A 层清库 #14（9 批大仓含 Elixir 新语言钉版）· 2026-11-02

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：**543n/842e/8层/10步**，0 issues，fingerprints 125@be10a1b7 |
| 综合讲透 | `讲透.md`：4463 字 43 锚（五节） |
| NOTES-DIGEST | 44 条 |

**一句话**：OpenAI "low key engineering preview"——**项目工作变隔离自主 Codex agent 运行**（Linear→agent→CI 证明→PR）；elixir/ 参考实现+语言无关 SPEC 18 章（SPEC 即 prompt 的双资产形态）。

**本轮新钉版（Elixir 首次入流水线）**：tree-sitter 零支持三形态（extract 全空/batchImportData 全空/Code.require_file 盲区）→自写提取器（单行 do:/匿名块/fn 计数三 bug 修）；**camel→snake 必做**（.lower() 假路径漏边）；反 Macro.underscore 三例（GitHub→github/）；测试替身=脚本化 fake codex 二进制。
