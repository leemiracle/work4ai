# 讲透 Janus

> DeepSeek 统一多模态理解与生成的解耦路线：理解与生成对视觉表征的粒度需求根本不同——解耦成两条视觉编码通路、共用一个 transformer；1.3B 模型理解基准打赢 7-13B 对手、生成基准打赢 SDXL/DALL-E 2。commit `1daa72f`（2025-02-01）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 19 页（deepwiki/） |
| 论文精读 | 1 篇（双论文）：《Janus: Decoupling Visual Encoding for Unified Multimodal Understanding and Generation》（arXiv:2410.13848）+《Janus-Pro》（arXiv:2501.17811） |
| 知识图谱 | 145 节点 / 283 边 / 8 层 / 11 步导览（训练/推理代码均在，图谱较厚） |

## 论文精读要点

- **核心主张**：理解要抽象语义（SigLIP）、生成要具体细节（VQ tokenizer），别共用一个视觉编码器——"两张脸各看一个方向"（罗马双面神命名）
- 1.3B 小模型双线超预期：理解侧打赢一批 7B-13B 专模，生成侧 GenEval 打赢 SDXL/DALL-E 2
- **Janus-Pro**（2501.17811）= 同架构在训练策略/数据/规模三轴升级：GenEval 61%→80%，未发新架构——证明瓶颈在数据与配方
- ⚠️ **ID 勘误（钉版）**：2411.07975 是 **JanusFlow**（CVPR 2025，整流流生成头姊妹工作），**不是 Janus-Pro**；Janus-Pro 正确 ID=2501.17811（arXiv 页+GitHub bibtex 双核实）
- 后续影响：解耦编码成统一模型标配设计；DeepSeek 内部此线汇入 VL 系实践

## 知识图谱

路径：`~/ai/explore/deepseek-ai/Janus/.understand-anything/knowledge-graph.json`。含训练 pipeline，图谱较厚实。

## 姊妹篇

- 多模态同门：[讲透DeepSeek-VL](../讲透DeepSeek-VL/README.md)、[讲透DeepSeek-VL2](../讲透DeepSeek-VL2/README.md)
- 视觉 token 路线远亲：[讲透DeepSeek-OCR](../讲透DeepSeek-OCR/README.md)、[讲透DeepSeek-OCR-2](../讲透DeepSeek-OCR-2/README.md)
