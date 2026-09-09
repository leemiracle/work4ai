# 讲透 DeepSeek-V2

> "架构级创新换经济性"路线的标志性论文：236B 总参/21B 激活 MoE，MLA 压掉 93.3% KV cache，DeepSeekMoE 省 42.5% 训练成本，5.76× 生成吞吐，V3/R1 全系架构直系祖先。commit `ec98ee3`（2024-09-25）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 13 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model》（arXiv:2405.04434） |
| 知识图谱 | 5 节点 / 2 边 / 3 层 / 3 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **MLA（Multi-head Latent Attention）**：KV cache 压缩 93.3%，关键设计是"解耦 RoPE"（与 RoPE 作者 Jianlin Su 论文附录讨论印证）
- **DeepSeekMoE**：细粒度专家分割 + 共享专家隔离，训练成本省 42.5%（直觉：专家切细管窄知识，共享专家抽走通用知识消除冗余）
- 236B/21B 激活同时拿下开源最强性能与 5.76× 吞吐；前身 DeepSeek LLM（2401.02954）攒数据与配方，V2 换骨架——"V1 攒数据，V2 换骨架"
- ⚠️ **勘误（ID 核实）**：2311.18743 是清华 AlignBench（中文对齐评测基准，README 榜单 7.91 分出处），**不是** DeepSeek 论文；真正前身是 2401.02954
- 推理三路径：Transformers(eager) / SGLang(MLA+FP8 优化) / vLLM(PR#4650)

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-V2/.understand-anything/knowledge-graph.json`。发布仓特性：源码薄图谱小属正常，重点在论文与 DeepWiki。

## 姊妹篇

- 前身：[讲透DeepSeek-LLM](../讲透DeepSeek-LLM/README.md)；MoE 预研：[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)
- 后继：[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)；中间 checkpoint 复用者：[讲透DeepSeek-Coder-V2](../讲透DeepSeek-Coder-V2/README.md)
- 专家微调：[讲透ESFT](../讲透ESFT/README.md)；多模态平移：[讲透DeepSeek-VL2](../讲透DeepSeek-VL2/README.md)
