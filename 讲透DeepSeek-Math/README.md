# 讲透 DeepSeek-Math

> 首个在竞赛级 MATH 基准破 50%（51.7%）且不用外部工具与投票的开源 7B：120B token 自挖掘数学语料 + 提出 GRPO（后来成为 R1 与整个开源 RLHF 社区的标准算法）。commit `b8b0f8c`（2024-04-15）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 22 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models》（arXiv:2402.03300） |
| 知识图谱 | 150 节点 / 282 边 / 6 层 / 12 步导览（评测仓，含 evaluation/ 代码） |

## 论文精读要点

- **GRPO 诞生地**：去掉 critic、用组内相对排名估 baseline，成 DeepSeek-R1 与 TRL/verl 等社区标准算法
- **数据管线**：以 OpenWebMath 为种子，从 Common Crawl 迭代挖掘 120B token 数学语料（fastText 分类器迭代 + 多源去重），打破"arXiv 语料迷信"
- 三阶段产物：Base / Instruct / RL 7B；DeepSeekMath-RL 在 MATH 51.7%（无工具无投票）
- ⚠️ **勘误（ID 核实）**：2310.06786 是多伦多大学的 OpenWebMath（语料种子论文），**不是** DeepSeek 前身；真正基座是 DeepSeek-LLM（2401.02954）+ DeepSeek-Coder-v1.5（2401.14196）
- 仓内**无训练代码**：GRPO/预训练/SFT 均在内部框架完成，仓库定位"模型发布 + 论文评测复现"

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Math/.understand-anything/knowledge-graph.json`。发布仓+评测代码，训练细节需回论文。

## 姊妹篇

- GRPO 下场：[讲透DeepSeek-R1](../讲透DeepSeek-R1/README.md)（大规模 RL）与 [讲透DeepSeek-Math-V2](../讲透DeepSeek-Math-V2/README.md)（自验证）
- 同班底证明线：[讲透DeepSeek-Prover-V1.5](../讲透DeepSeek-Prover-V1.5/README.md)（RLPAF 复用 GRPO）
- 基座：[讲透DeepSeek-LLM](../讲透DeepSeek-LLM/README.md)、[讲透DeepSeek-Coder](../讲透DeepSeek-Coder/README.md)
