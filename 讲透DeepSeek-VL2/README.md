# 讲透 DeepSeek-VL2

> DeepSeek 第二代 MoE 多模态模型：动态 tiling（任意宽高比切片）+ DeepSeekMoE/MLA，以 4.5B 激活参数打赢一票 7-8B dense 模型，并新增视觉 grounding 能力线。commit `ef9f91e`（2025-02-26）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 15 页（deepwiki/） |
| 论文精读 | 无本地副本：VL2 论文（arXiv:2412.10302）在 [讲透DeepSeek-VL/paper/](../讲透DeepSeek-VL/paper/PAPER-DEEPREAD.md) 综合篇中与 V1 一并精读——**共享 VL 的 paper** |
| 知识图谱 | 134 节点 / 267 边 / 7 层 / 10 步导览（训练/推理代码均在，图谱较厚） |

## 论文精读要点（摘自 VL 综合篇）

- **动态 tiling**：按图像原生宽高比切块再编码，摆脱 V1 钉死的 1024×1024，长图/超大分辨率（InfographicVQA 场景）直接受益
- **架构三件套**：DeepSeekMoE 细粒度专家 + MLA 潜注意力 + aux-loss-free 负载均衡——V2/V3 主力 LLM 成果的系统性平移
- Tiny/Small/Base 三档（1B/2.8B/4.5B 激活），定位"高分辨率与低推理成本同时推向极致"
- 新增 **grounding**（视觉定位）能力线，弥补 V1 空白
- 阅读顺序建议：先读 MoE（2401.06066）与 V2 报告再读本文

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-VL2/.understand-anything/knowledge-graph.json`。含训练 pipeline 与 VL2 各档模型卡，图谱较厚实。

## 姊妹篇

- 前作与共享精读：[讲透DeepSeek-VL](../讲透DeepSeek-VL/README.md)；架构基座：[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)、[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)
- 统一理解/生成路线：[讲透Janus](../讲透Janus/README.md)
