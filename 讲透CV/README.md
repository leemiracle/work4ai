---
card_id: CV-00
title: "讲透 CV：从 CNN 到 ViT 到 SAM 到 Diffusion 的视觉演化"
universe: 讲透CV
burke:
  scene: "让机器'看懂'世界是 AI 最古老的梦想"
  agent: "想看懂机器视觉全谱系的人"
  agency: "CNN / ViT / SAM / Diffusion / VLM"
  act: "从'识别猫狗'到'分割万物'到'生成世界'到'视觉推理'"
  purpose: "做视觉应用时不被术语淹没"
tension: "视觉的本质是逆图形学——从 2D 像素反推 3D 世界，这是病态问题"
arc: [直觉(三范式), 数学(统一视角), 代码(CNN/ViT/DDPM), 不足(失败模式), 应用(前沿)]
status: in_progress
next_card: CV-01
refs:
  - "Krizhevsky et al., AlexNet, 2012"
  - "Dosovitskiy et al., ViT, 2020"
  - "Kirillov et al., SAM, 2023"
  - "Ho et al., DDPM, 2020"
  - "Rombach et al., LDM (Stable Diffusion), 2022"
  - "SAM 2 (Meta), 2024"
  - "SigLIP 2 (Google), 2025"
updated: 2026-08-13
---

# 👁️ 讲透 CV：视觉的三次范式更迭

> **User Story**：作为一个想看懂机器怎么「看」的人，我想从 CNN 一路走到 SAM/Diffusion/VLM，以便做视觉应用。

## 🎭 戏剧张力

视觉的根本困难：

> **从 2D 像素反推 3D 世界是病态问题（inverse graphics）**——同一张 2D 图对应无限多种 3D 场景。CV 的全部历史，就是用不同的归纳偏置（卷积/注意力/扩散先验）来约束这个病态反演。每次范式更迭，都是换了一种「先验」。

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | `01-直觉-视觉三次范式更迭.md` | CNN(2012) → ViT(2020) → SAM/Diffusion/VLM(2022-) |
| 数学 | `02-数学-卷积注意力扩散的统一视角.md` | 卷积=局部线性；attention=动态全局；diffusion=去噪先验 |
| 代码 | `03-代码-最小CNN-ViT-Diffusion.md` | numpy conv2d + PyTorch mini-ViT + DDPM 采样器 |
| 不足 | `04-不足-CV失败模式.md` | adversarial patch / 长尾 / OOD / 可解释差 |
| 应用 | `05-应用-2024-2026CV前沿.md` | SAM2 / SigLIP2 / Qwen2-VL / Sora / Gaussian Splatting |

## 🗺️ 三次范式更迭（叙事主线）

```
第 1 范式 CNN 时代 (2012-2020)
  AlexNet → ResNet → EfficientNet
  归纳偏置: 局部性 + 平移不变性 + 层次抽象
  任务: 分类/检测/分割 (ImageNet 黄金十年)
  局限: 感受野有限, 长距离依赖弱
       ↓
第 2 范式 基础模型时代 (2020-2022)
  ViT → CLIP → MAE → DINOv2
  归纳偏置: 把图切块当 token, 用 Transformer 全局聚合
  突破: 大规模预训练 + 迁移
  局限: 仍是判别模型, 不能生成
       ↓
第 3 范式 多模态/生成时代 (2022-)
  SAM (分割万物) / Diffusion (生成) / VLM (视觉推理)
  归纳偏置: 用语言对齐语义 + 用扩散学分布
  突破: 从"识别"到"创造"和"理解"
```

## 📊 2024-2026 CV 前沿

| 系统 | 突破 | 意义 |
|---|---|---|
| **SAM 2** (Meta 2024) | 视频分割万物，零样本 | 分割任务的 GPT 时刻 |
| **SigLIP 2** (Google 2025) | 改进 CLIP 对比学习 | 更强的视觉-语言对齐 backbone |
| **Florence-2** (Microsoft 2024) | 统一视觉基础模型 | 一个模型做所有视觉任务 |
| **Qwen2-VL** (Alibaba 2024-2025) | 任意分辨率处理 | 解决 VLM 的分辨率折中 |
| **GPT-4V / Claude vision** | 视觉推理 | VLM 进入主流 |
| **Sora / Veo 3** | 视频生成 | 「是不是世界模型」争议 |
| **Gaussian Splatting / NeRF** | 3D 重建 | 从 2D 重建 3D 场景 |

## 🔗 与其他宇宙

- 与 **`讲透多模态/`**：CV 讲「视觉感知」，多模态讲「视觉与其他模态对齐」。
- 与 **`讲透模型宇宙/` `讲透基础模型/`**（已有）：ViT 是基础模型在视觉的化身。
- 与 **`讲透世界模型/`**：视频生成模型是不是视觉世界模型？



## 💡 核心洞察

> **CV 的每次范式更迭，都是「先验」的熵减重构**——CNN 的卷积先验最死板（熵减最强，但限制大）；ViT 放弃卷积先验、用数据学（熵减减弱，灵活性上升）；Diffusion 用「去噪」这一更通用的生成先验。**越通用的先验 = 核心越简单 = 边缘越能发散**——这正是 `故事原语/02-熵论辩证` 的「世界级」模式。

---

📌 **下一步**：`02`（三范式数学统一）和 `03`（三个最小实现）是技术核心。
