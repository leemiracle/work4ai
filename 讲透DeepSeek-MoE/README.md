# 讲透 DeepSeek-MoE

> "极致专家专业化"架构预研仓：细粒度专家分割 + 共享专家隔离，2B→16B→145B 三级验证，治好 MoE"专家不专"的架构病——V2/V3/Coder-V2/VL2 全系的专家路由基因来自这里。commit `66edeee`（2024-01-16）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 16 页（deepwiki/） |
| 论文精读 | 无独立篇：《DeepSeekMoE》（arXiv:2401.06066）已在 [讲透DeepSeek-Coder/paper/](../讲透DeepSeek-Coder/paper/PAPER-DEEPREAD.md) 三合一篇中完整覆盖 |
| 知识图谱 | 19 节点 / 20 边 / 3 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点（摘自 Coder 三合一篇）

- **两大创新**：①细粒度专家分割（专家切细，每个管更窄知识，路由组合更灵活）②共享专家隔离（把"通用知识"从路由专家中抽走，消除冗余）
- **三级验证路线**：2B 对照实验（与同 FLOPs dense 比）→ 16B（首个 MoE 化开源轻量模型之一）→ 145B 无损对齐 dense 性能
- 实验方法学扎实：专家 specialization/冗余度的量化分析成为后续 MoE 论文标配引用
- 与北大/清华/南大合作发表；训练框架 HAI-LLM
- 与本系 ESFT 互为表里：一个证明"专家分工可学"，一个利用"专家分工可挑"

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-MoE/.understand-anything/knowledge-graph.json`。发布仓特性：模型卡+脚本为主，图谱小属正常，重点在论文与 DeepWiki。

## 姊妹篇

- 直系继承：[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)、[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)、[讲透DeepSeek-Coder-V2](../讲透DeepSeek-Coder-V2/README.md)、[讲透DeepSeek-VL2](../讲透DeepSeek-VL2/README.md)
- 完整精读：[讲透DeepSeek-Coder](../讲透DeepSeek-Coder/README.md)；专家微调：[讲透ESFT](../讲透ESFT/README.md)
