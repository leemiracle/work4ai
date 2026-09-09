# 讲透 DeepSeek-Coder-V2

> DeepSeek 首个 MoE 化代码模型：236B 总参/21B 激活，338 语言 6T tokens 续训（V2 中间 checkpoint），把开源代码与数学模型首次推到 GPT-4-Turbo 同档。commit `a2b4e0a`（2025-11-11）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 20 页（deepwiki/） |
| 论文精读 | 1 篇（**符号链接** → `../../讲透DeepSeek-Coder/paper/PAPER-DEEPREAD.md`，三合一共享篇，含 arXiv:2406.11931） |
| 知识图谱 | 6 节点 / 3 边 / 3 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **与 Coder-V1 共享一篇精读**（本地 paper/ 为符号链接）：V1→MoE→V2 三篇演进链在讲透DeepSeek-Coder 中完整拆解
- 合流配方：DeepSeek-V2 中间 checkpoint + 6T tokens 续训（代码/数学配比大增）= MoE 化代码模型，省去从零成本
- 236B/21B 激活；338 语言；HumanEval/MBPP/Aider 等代码榜与 MATH/GSM8K 数学榜同时进入 GPT-4-Turbo 同档
- 架构 = DeepSeek-V2 的 MLA + 细粒度 MoE，路由与负载均衡直接继承
- 后续被自家 Prover-V1.5 用作 CoT 注释生成器（236B 版）

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Coder-V2/.understand-anything/knowledge-graph.json`。发布仓特性：inference 脚本为主，图谱小属正常，重点在论文精读与 DeepWiki。

## 姊妹篇

- 前作与共享精读：[讲透DeepSeek-Coder](../讲透DeepSeek-Coder/README.md)；底座：[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)
- MoE 预研：[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)；下游使用者：[讲透DeepSeek-Prover-V1.5](../讲透DeepSeek-Prover-V1.5/README.md)
