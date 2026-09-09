# 讲透 DeepSeek-OCR-2

> Visual Causal Flow：把 encoder 里的 CLIP 换成 0.5B LLM（Qwen2-0.5B），用"视觉 token 双向注意力 + 可学习 query 因果注意力"混合掩码让 encoder 按语义因果顺序重排视觉 token，OmniDocBench v1.5 以最少 token 上限（1120）拿 91.09。commit `2f3699e`（2026-02-03）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 32 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-OCR 2: Visual Causal Flow》（arXiv:2601.20552） |
| 知识图谱 | 31 节点 / 48 边 / 5 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **认知动机**：现有 VLM 按光栅扫描序展平 2D patch 是"不当归纳偏置"——人类扫视是语义驱动的因果流；两个级联 1D 因果结构（encoder 重排 + decoder 自回归）逼近真 2D 推理
- **混合掩码**：视觉 token 间双向注意力保并行编码，learnable query 对视觉 token 因果注意力学"先送什么进 LLM"
- 代码对照实证：qwen2_d2e.py query_768=144 / query_1024=256，math_templates.py 四模板与论文附录 A.1-A.4 逐字对应
- **Native Multimodality 愿景**（§6.2）：单一 LLM 式 encoder 共享 Wk/Wv/attention/FFN，仅靠模态专属 learnable queries 区分图像/音频/文本——V1 压缩 + V2 LM 式 encoder 被定位为通往该愿景的两步
- 与 Chameleon/Fuyu 的"LLM 直接多模态初始化"路线遥相呼应

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-OCR-2/.understand-anything/knowledge-graph.json`。发布仓，图谱小属正常，重点在论文与代码对照。

## 姊妹篇

- 前作：[讲透DeepSeek-OCR](../讲透DeepSeek-OCR/README.md)（光学压缩可行性）
- LM 式 encoder 远亲：[讲透DeepSeek-VL2](../讲透DeepSeek-VL2/README.md)、[讲透Janus](../讲透Janus/README.md)
