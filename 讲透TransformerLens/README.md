# 讲透 TransformerLens · 深度知识库

> 基于 DeepWiki 全量文档 + understand-anything 中文知识图谱 + 核心源码深解的 TransformerLens 学习知识库。
> 生成于 2026-09-05，对应源码 commit `2a05c15`（2026-09-01）。

## 这是什么

TransformerLens 是面向机制可解释性（mechanistic interpretability）研究的 Transformer 逆向工程库：将 GPT-2/Llama/Mistral/Gemma/Qwen 等 70+ 架构（9000+ 模型）转换为统一钩子架构——每个注意力头/MLP/层均可挂 hook，配合 ActivationCache/logit lens/activation patching 等技术观测内部电路。PyTorch 实现。

**双系统架构**：legacy `HookedTransformer`（经典 API）与 v3 `TransformerBridge`（model_bridge 新体系，141 个适配器文件）并存。

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 新人系统上手 | `onboarding/ONBOARDING.md` | 项目总览→14 层架构→14 个关键概念→14 步学习路径 |
| 按图索骥查专题 | `deepwiki/`（43 页） | 查 `deepwiki/INDEX.md` |
| 啃核心源码 | `explain/`（5 篇） | hook-points / hooked-transformer / activation-cache / bridge / adapter-system |
| 交互式探索 | 知识图谱（仓内） | 4507 节点/10361 边/14 层/14 步导览，`~/ai/TransformerLens/.understand-anything/knowledge-graph.json` |

## 目录结构

```
讲透TransformerLens/
├── README.md
├── deepwiki/                  # DeepWiki 抓取（43 页 + INDEX + 覆盖率检查）
├── onboarding/ONBOARDING.md  # 新人指南（5976 字，8 节）
└── explain/                   # 5 篇核心深解
    ├── tl-hook-points.md          # HookPoint 钩子机制（add_hook/perma_hook）
    ├── tl-hooked-transformer.md  # legacy 主门面（from_pretrained/run_with_cache）
    ├── tl-activation-cache.md    # 激活缓存（logit_attrs/accumulated_resid）
    ├── tl-bridge.md              # v3 TransformerBridge（5614 行/128 方法）
    └── tl-adapter-system.md      # 适配器体系（141 文件/80+ 架构）
```

## 生成方式

- DeepWiki 43 页 100% + understand 流水线（1059 文件→47 批→4507 节点/10361 边→14 层→14 tour→0 issues→fingerprints）
- 指南与深解：图谱+源码只读交叉验证（TransformerBridge 128 方法 awk 实测、141 适配器文件实数）
