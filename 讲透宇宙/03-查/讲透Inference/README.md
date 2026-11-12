# 讲透 Inference（Xinference）

> Xorbits 入规模化模型推理平台 @b3de260 · understand 图谱全链 2026-11-09
> 真源：/data/usershare/ai/inference/.understand-anything/（活体，fingerprints 支持增量）

## 产物

| 产物 | 规模 | 状态 |
|---|---|---|
| understand/knowledge-graph.json | 2785 节点 / 5826 边 / 14 层 / 16 步 tour | ✅ 双验 0 issues |
| understand/ONBOARDING.md | 5071 字 8 节 | ✅ 17 锚全中 |
| understand/explain/ | 12 篇 41797 字符 | ✅ 真坏 0（三型判读） |
| deepwiki/ | 49 页（2026-09-04 轮） | ✅ TRUE_100 |

## 一句话定位

八模态（LLM/Embedding/Rerank/Image/Audio/Video/World/Flexible）×多引擎（vLLM/transformers/MLX/SGLang 等）的规模化推理平台：supervisor-worker-model 三 Actor 分布式骨架 + RESTful/CLI/Web UI + 完整监控栈。

## 关联

13 仓流水线 understand 线成员（与 TIRx-kernels/localai/xgrammar/web-llm/mlc-llm/llamafile/TransformerLens/ktransformers/local-deep-research 同链）。
