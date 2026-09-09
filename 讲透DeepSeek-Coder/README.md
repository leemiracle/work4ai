# 讲透 DeepSeek-Coder

> 开源代码模型 V1→V2 演进主线：V1 证明"仓库级预训练 + FIM + 从零训练"可追平 GPT-3.5；V2 嫁接 MoE 底座后以 21B 激活首次把开源推到 GPT-4-Turbo 同档。commit `2f9fd85`（2025-11-11）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 18 页（deepwiki/） |
| 论文精读 | 1 篇（三合一）：《DeepSeek-Coder》（arXiv:2401.14196）+《DeepSeek-Coder-V2》（arXiv:2406.11931）+《DeepSeekMoE》（arXiv:2401.06066） |
| 知识图谱 | 218 节点 / 334 边 / 6 层 / 12 步导览（含训练/评测代码，图谱相对厚实） |

## 论文精读要点

- **三篇论文五个月演进链**：DeepSeekMoE（架构预研，细粒度专家+共享隔离，2B→16B→145B 三级验证）→ DeepSeek-Coder（数据预研，repo 级语料管线 + FIM 消融，1.3B-33B dense）→ Coder-V2（合流：V2 中间 checkpoint + 6T 续训 = MoE 化代码模型）
- V1 关键件：87 程序语言 repo 级语料（top-down 按目录切分）、FIM 3 种模式、单 epoch 从零训练
- V2 关键件：338 语言、6T tokens 续训、236B/21B 激活，代码与数学首次与 GPT-4-Turbo 同档
- MoE 论文解决"专家不专"架构病——被 V2/V3 全系继承
- 训练框架统一 HAI-LLM（幻方），V1/MoE 与北大 HCST 等高校合作

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Coder/.understand-anything/knowledge-graph.json`。本仓含真实训练/评测代码，图谱在模型仓中最厚实。

## 姊妹篇

- 架构基座：[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)、[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)
- V2 专仓（共享本篇精读）：[讲透DeepSeek-Coder-V2](../讲透DeepSeek-Coder-V2/README.md)
- Coder-v1.5 是 DeepSeekMath 基座：[讲透DeepSeek-Math](../讲透DeepSeek-Math/README.md)；CoT 注释使用者：[讲透DeepSeek-Prover-V1.5](../讲透DeepSeek-Prover-V1.5/README.md)
