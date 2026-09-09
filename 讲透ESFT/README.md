# 讲透 ESFT

> MoE 原生 PEFT：用路由分数挑出与任务最相关的一小撮 experts 只训它们、其余全冻——~1.4B 可训参（vs 全参 15.7B）打平甚至超过 full fine-tuning，通用能力不掉、训练省 30%、存储省 90%。commit `3746ca7`（2025-05-22）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 19 页（deepwiki/） |
| 论文精读 | 1 篇：《Let the Expert Stick to His Last: Expert-Specialized Fine-Tuning for Efficient Instruction Tuning》（arXiv:2407.01906） |
| 知识图谱 | 96 节点 / 176 边 / 6 层 / 10 步导览（含完整训练代码，图谱较厚） |

## 论文精读要点

- **方法极简**：按路由分数选 top experts（阈值 p 控制）只训它们+attention，其余 expert/embedding 全冻——"鞋匠守鞋楦"，让每个 expert 守好擅长的领域
- **效果**：~1.4B 可训参数在定制任务上打平/超过全参微调，通用 benchmark 几乎不掉；训练时间省 30%、存储省 90%（每任务一个小增量包）
- 作者与 DeepSeekMoE/V2 架构组高度重合；出发点实际：百亿千亿 MoE 下游定制全参成本爆炸
- 与 DeepSeekMoE"极致专家专业化"互为表里：一个证明专家分工可学，一个利用专家分工可挑
- 实践提醒：V2/V3 之后超大 MoE（共享专家占比更高、路由更复杂）直接套用需重验阈值 p 与 score 函数；expert 选择思想被后续 LoRA-MoE 混合方法反复引用

## 知识图谱

路径：`~/ai/explore/deepseek-ai/ESFT/.understand-anything/knowledge-graph.json`。训练+评测代码完整，图谱较厚实。

## 姊妹篇

- 架构前提：[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)、[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)、[讲透DeepSeek-Coder-V2](../讲透DeepSeek-Coder-V2/README.md)
