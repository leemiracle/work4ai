# 讲透 DeepSeek-VL

> DeepSeek 首代"务实主义"多模态模型：SAM+SigLIP 混合编码器在固定 576 token 预算内吃下 1024 分辨率，70% 纯文本配比保语言能力；与 VL2 组成"混合编码器 → 动态 tiling + MoE"演进叙事。commit `681bffb`（2024-04-24）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 21 页（deepwiki/） |
| 论文精读 | 1 篇（VL+VL2 综合篇）：《DeepSeek-VL》（arXiv:2403.05525）+《DeepSeek-VL2》（arXiv:2412.10302），两 ID 均经 arXiv 核实 |
| 知识图谱 | 125 节点 / 247 边 / 7 层 / 10 步导览（训练/推理代码均在，图谱较厚） |

## 论文精读要点

- **混合视觉编码器**：SAM（局部细节/grounding）+ SigLIP（语义），混合后压到 576 token——"数据高效 + 高吞吐"的务实解
- **70% text-only 配比**：VL 模型普遍被视觉数据带崩语言能力，V1 用配比硬保住；数据六大门类中文档 OCR 自建主力（140 万 arXiv 源码+PDF 用 Nougat 渲染）
- **Web Code 数据**：自建 plot-to-code——146 万 Jupyter notebook 抽图+代码得 110 万对，chart 理解的关键弹药
- **VL2 扬弃两点**：固定 1024 分辨率 → 动态 tiling 任意宽高比；dense → DeepSeekMoE/MLA（4.5B 激活打赢 7-8B dense），并新增 grounding
- 作者线与 V2/V3 主线高度重叠——VL2 是把主力 LLM 架构成果平移到多模态的系统性动作

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-VL/.understand-anything/knowledge-graph.json`。含完整训练 pipeline，图谱在模型仓中较厚实。

## 姊妹篇

- 后继：[讲透DeepSeek-VL2](../讲透DeepSeek-VL2/README.md)（共享本篇精读）；解耦路线：[讲透Janus](../讲透Janus/README.md)
- 视觉 token 压缩远亲：[讲透DeepSeek-OCR](../讲透DeepSeek-OCR/README.md)；架构基座：[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)
