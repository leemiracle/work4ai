# 讲透 Transformer

> 从 Self-Attention 基础到 2026 前沿 (DeepSeek MLA / Llama 4 iRoPE / mHC), 配合 Stanford CS25 讲座体系。
> 实验驱动: 全部结论用 Python 实跑验证。

---

## 📚 文档导航 (按学习路径)

### 基础 (先读)
| 文档 | 主题 |
|------|------|
| [00-Transformer全景](00-Transformer全景.md) | 整体架构 + mini-GPT 实验 (三件套总装) |
| [01-Self-Attention深度](01-Self-Attention深度.md) | KV Cache + FlashAttention 原理 |

### 组件深入 (LLaMA 配方四件套)
| 文档 | 主题 | 2026 标准 |
|------|------|----------|
| [02-位置编码演进](02-位置编码演进.md) | sin/cos → **RoPE** → iRoPE | RoPE |
| [03-注意力变体](03-注意力变体.md) | MHA → MQA → **GQA** → **MLA** | GQA / MLA |
| [04-FFN与激活变体](04-FFN与激活变体.md) | ReLU → GELU → **SwiGLU** | SwiGLU + 8/3 |
| [05-归一化与残差](05-归一化与残差.md) | Post-LN → **Pre-LN + RMSNorm** | Pre + RMSNorm |

### 系统视角
| 文档 | 主题 |
|------|------|
| [06-架构演进与MoE](06-架构演进与MoE.md) | 四时代 + LLaMA 配方 + MoE 革命 |
| [07-预训练与ScalingLaws](07-预训练与ScalingLaws.md) | Next-token + Chinchilla 定律 |
| [08-对齐训练](08-对齐训练.md) | RLHF → DPO → GRPO |
| [09-推理优化](09-推理优化.md) | KV Cache / 量化 / 投机解码 |
| [10-VisionTransformer与多模态](10-VisionTransformer与多模态.md) | ViT / CLIP / 原生多模态 |

### 输入与系统工程
| 文档 | 主题 |
|------|------|
| [13-Tokenizer](13-Tokenizer.md) | BPE / SentencePiece / 大词表 (Transformer 文本前端) |
| [14-训练并行](14-训练并行.md) | DP/ZeRO/TP/PP/EP/SP 五种并行 (大模型训练系统基础) |
| [15-长上下文](15-长上下文.md) | RoPE scaling / 稀疏注意力 / Ring Attention (突破 O(n²)) |

### 源码对照 (原理 → 生产代码)
| 文档 | 主题 |
|------|------|
| [11-HuggingFace源码对照](11-HuggingFace源码对照.md) | LLaMA/Mixtral/DeepSeek-V3 真实源码逐类对照 |

### 资源
| 文档 | 主题 |
|------|------|
| [12-权威资源库](12-权威资源库.md) | ★ 24 个硬核博客+课程, 按 ezyang 风格分级, 含阅读路径 |
| [CS25-讲座索引](CS25-讲座索引.md) | Stanford CS25 V4/V5/V6 全部讲座 + 讲者速查 |

---

## 🧪 实验

```
experiments/
├── transformer_overview.py    # 3 个子实验 (已实跑)
│   ├── 实验1: 手写 Self-Attention (纯 numpy, 验证 = 矩阵乘法)
│   ├── 实验2: 注意力热力图 (Encoder 全连接 vs Decoder causal)
│   └── 实验3: mini-GPT (106K 参数, 字符级, 真的学会语言)
├── 12_verify_real_llama.py    # 用真实 transformers 验证 11 篇源码对照 (已实跑)
│   ├── Part1: 验证 RMSNorm/RoPE/SwiGLU/GQA/CE 每处最大差异 0.00
│   └── Part2: 真实 LLaMA(77K参) vs 简化 mini-GPT(105K参) 训练对比
├── attention_heatmap.png      # 注意力可视化
└── mini_gpt_training.png      # 训练曲线 (loss 3.47→0.13)
```
跑法: `cd experiments && python3 transformer_overview.py` 或 `python3 12_verify_real_llama.py`

**mini-GPT 生成样本** (温度 0.3): *"tion instead of recurrence it enables palllel train"*——10 万参数的玩具, 用 Self-Attention + GELU + CrossEntropy + Adam, 学会了真实语言!

---

## 🌳 知识树 (本项目在其中的位置)

```
激活函数 (表达能力)  ──┐
损失函数 (目标)      ──┼──> Transformer (架构)  ──> 预训练 ──> 对齐 ──> 推理部署
优化器   (更新)      ──┘                                              ↓
                                                                    ChatGPT/DeepSeek/...
```
本项目把前三者 (见 `讲透激活函数/` `讲透损失函数/` `讲透优化器/`) 总装成 Transformer, 并讲清后续全链路。

---

## ✅ 完整度盘点: Transformer 相关是否讲完了?

**已完整覆盖 (16 篇文档 + 实验)**: 架构全组件 (00-05) · 系统全链路 (06-10) · 输入前端与工程 (13-15) · 源码对照 (11) · 权威资源 (12) · CS25 索引。

**故意留作"应用层"的边界** (不算 Transformer 本身, 属下一站主题):
- 📦 **RAG / Agent / 工具调用** — 在 Transformer 之上的应用 (用 LLM, 非讲 LLM)
- 🛠️ **微调实战 (LoRA/QLoRA)** — 08 篇讲了原理, 实战操作是工程教程
- 📊 **评估与 benchmark** — 怎么测模型好不好, 独立方法论
- 🔒 **安全/越狱/红队** — 12 篇资源库指向 Lilian Weng, 属外围

**仍在快速演化的前沿** (本项目跟踪到 2026.07, 持续更新可订阅 12 篇资源库):
- DeepSeek V4 (mHC 残差革命) · Llama 4 (iRoPE) · 原生多模态 · SSM/Mamba 替代架构

> **结论**: 作为一个"讲透 Transformer 本身"的学习项目, **核心已完整闭环**。要继续深入, 选 12 篇资源库里的硬核博客 (ezyang/Tri Dao/苏剑林), 或进入下一个大主题 (RAG/微调/Agent)。

---

## 🎯 2023-2026 架构收敛速查 (jytan.net 53 模型统计)

| 组件 | 2017 原版 | **2026 现代标准** |
|------|----------|------------------|
| 归一化 | Post-LayerNorm | **Pre-RMSNorm** |
| 位置编码 | 绝对 sin/cos | **RoPE** (iRoPE 新趋势) |
| 激活/FFN | ReLU, 2 层 | **SwiGLU, 8/3 扩展** |
| Attention | MHA | **GQA** (或 **MLA**) |
| bias | 有 | **全去掉** |
| 架构 | Encoder-Decoder | **Decoder-Only** |
| 缩放轴 | Dense | **MoE** (256+ 专家) |

---

## 📖 核心参考文献

- Vaswani et al. 2017, *Attention Is All You Need* — 开山
- Dao et al. 2022, *FlashAttention* — 工程突破
- DeepSeek-AI 2024, *DeepSeek-V2/V3* — MLA + MoE
- Touvron et al. 2023, *LLaMA* — 配方结晶
- jytan.net 2025, *The Crystallization of Transformer Architectures* — 53 模型统计
- largo.dev 2026, *Frontier LLM Architectures 2026* — mHC/iRoPE/early fusion
- Karpathy, *nanoGPT* — 最佳参考实现
- **HuggingFace transformers** — https://github.com/huggingface/transformers (生产级源码, 见 11 篇)
- **Stanford CS25** (V4/V5/V6) — https://web.stanford.edu/class/cs25/
