# 讲透 DeepSeek-OCR

> 把 OCR 重新定义为"上下文光学压缩"的可行性实验：紧凑 VLM 从极少量 vision tokens 解码出 10 倍文本信息（10× 压缩精度 ~97%），顺手造出端到端 SOTA 实用 OCR 模型。commit `09eaf52`（2026-01-27）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 38 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-OCR: Contexts Optical Compression》（arXiv:2510.18234） |
| 知识图谱 | 34 节点 / 54 边 / 5 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **核心论点跃迁**：从"更好的 OCR"转向"用视觉作为 LLM 长上下文的压缩介质"——视角级贡献
- **压缩-解码曲线**：10× 压缩下解码精度 ~97%，20× 仍有 ~60%，首次量化"视觉 token 的信息密度上限"
- **DeepEncoder**：SAM 400 token 低层 + 中间层裁剪（64/128/256 档）+ 512 高层 token 三段式，兼顾 grounding 与压缩
- 工程落地极快：2025-10-20 开源、10-21 挂 arXiv、10-23 进 vLLM 上游（`vllm.model_executor.models.deepseek_ocr`）
- 团队为 Vary / GOT-OCR2.0 / OneChart 一作班底；3 个月后 OCR-2（2601.20552）升级 encoder 验证路线可扩展

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-OCR/.understand-anything/knowledge-graph.json`。发布仓（推理+数据管线脚本），图谱小属正常，重点在论文。

## 姊妹篇

- 架构升级续篇：[讲透DeepSeek-OCR-2](../讲透DeepSeek-OCR-2/README.md)；多模态基座脉络：[讲透DeepSeek-VL](../讲透DeepSeek-VL/README.md)
