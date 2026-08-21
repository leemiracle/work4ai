---
card_id: MM-00
title: "讲透多模态：模态对齐与统一表示"
universe: 讲透多模态
burke:
  scene: "图、文、音、视频是不同模态，机器要在它们之间互译与推理"
  agent: "想做跨模态应用的人"
  agency: "CLIP / cross-attention / vision tokenizer / early-fusion"
  act: "把不同模态映射到统一语义空间"
  purpose: "做图/文/音/视频的互译、检索、推理"
tension: "不同模态有不同的几何结构（modality gap），找共同语义空间是核心难题"
arc: [直觉(翻译的故事), 数学(对齐形式化), 代码(CLIP+projector), 不足(失败模式), 应用(原生多模态)]
status: done
next_card: MM-01
refs:
  - "Radford et al., CLIP, 2021"
  - "Liang et al., Modality Gap, 2022"
  - "Team Chameleon, Meta, 2024"
  - "GPT-4o (native multimodal), OpenAI, 2024"
  - "Qwen2-VL, Alibaba, 2024-2025"
  - "LLaVA, Liu et al., 2023"
updated: 2026-08-15
---

# 🎭 讲透多模态：模态对齐与统一表示

> **User Story**：作为一个想做跨模态应用的人，我想理解不同模态如何被映射到统一表示，以便做图/文/音/视频的互译与推理。

## 🎭 戏剧张力

多模态的核心难题（Liang et al. 2022 的「modality gap」）：

> **即使你用对比学习把图像和文本对齐了，它们的嵌入在共同空间里仍会形成两个分离的簇——「modality gap」。** 这个 gap 不是 bug，是不同模态的内在几何结构差异。整部「讲透多模态」在回答：**怎么缩小这个 gap？还是干脆放弃统一空间、改用 early-fusion token 化？**

## 📚 五幕总览（全部 ✅）

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | [`01-直觉-多模态是翻译的故事.md`](01-直觉-多模态是翻译的故事.md) | CLIP/BLIP/Flamingo/LLaVA → 原生多模态的演化 |
| 数学 | [`02-数学-对齐形式化.md`](02-数学-对齐形式化.md) | InfoNCE / cross-attention / VQ tokenizer / modality gap |
| 代码 | [`03-代码-最小CLIP与投影层.md`](03-代码-最小CLIP与投影层.md) | numpy InfoNCE 前向 + PyTorch LLaVA projector |
| 不足 | [`04-不足-多模态失败模式.md`](04-不足-多模态失败模式.md) | modality gap / 幻觉 / 分辨率折中 / interleaved 难度 |
| 应用 | [`05-应用-2024-2026原生多模态浪潮.md`](05-应用-2024-2026原生多模态浪潮.md) | GPT-4o / Chameleon / Qwen2-VL / Sora / Veo3 |
| 辅助 | [`HISTORY.md`](HISTORY.md) | 四代范式编年（第 3 代=把 LLM 推理能力扩展到视觉领域）|

## 🗺️ 多模态的四代演化（叙事主线）

```
第 1 代 双塔对比 (CLIP, 2021)
  图像编码器 + 文本编码器 → 对比学习对齐
  强项: 检索/零样本分类
  弱项: 不能生成, 不能复杂推理
       ↓
第 2 代 融合 + 跨注意力 (BLIP/Flamingo, 2022)
  把图像特征作为 K/V 注入 LLM 的注意力
  强项: 图像问答
  弱项: 仍依赖外部视觉编码器
       ↓
第 3 代 投影 + LLM (LLaVA, 2023)
  视觉编码器 → MLP 投影层 → 塞进 LLM token 序列
  强项: 工程简单, 复用 LLM 能力
  弱项: 投影层是信息瓶颈
       ↓
第 4 代 原生多模态 (GPT-4o/Chameleon/Gemini, 2024-)
  early-fusion: 图/文/音都变成 token, 同一个 Transformer 处理
  强项: 真正统一, 实时交互
  弱项: 训练极难, 数据配比敏感
```

## 📊 2024-2026 原生多模态浪潮

| 系统 | 路线 | 突破 |
|---|---|---|
| **GPT-4o** (OpenAI 2024) | 原生多模态，端到端 | 实时语音+视觉对话，延迟 ~300ms |
| **Chameleon** (Meta 2024) | early-fusion token 化 | 图文混合 token，一个模型搞定 |
| **Qwen2-VL** (Alibaba 2024-2025) | 任意分辨率 + 动态 token | 解决 VLM 分辨率折中 |
| **Gemini 2.5** (Google 2025) | 原生多模态 + 长上下文 | 统一处理图/视频/音频/文 |
| **Sora 2 / Veo 3** (2025) | 视频生成 + 音频 | 文生视频+音频的工业化 |
| **3D 多模态** (GS/NeRF+LLM) | 3D 场景理解 | 空间智能兴起 |

## 🔗 与其他宇宙

- 与 **`讲透CV/`**：CV 讲「视觉感知本身」，本宇宙讲「视觉与语言/音频的对齐」。
- 与 **`讲透上下文缓存/`**：多模态 token 比纯文本 token 多得多，缓存更关键。
- 与 **[`讲透LLM/`](../讲透LLM/README.md)**：第 3 代范式（LLaVA 投影）的本质是**复用 LLM 已激活的推理能力**——见 [`激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md) §5 架构接入层。
- 与 **[`讲透Prompt/`](../讲透Prompt/README.md)**：CLIP 零样本是"提示词式能力释放"的起点；多模态失败缓解靠结构化 prompt + 分步生成（04 篇）。
- 与 **`故事原语/01-原语DSL`**：多模态对齐 = 给不同模态找「共同的故事语言」。



## 💡 核心洞察

> **多模态的本质是「翻译」——不是把图像翻译成文字，而是把所有模态翻译成一种「共享的语义语言」。** CLIP 用对比学习做「词典对照」，LLaVA 用投影层做「翻译机」，Chameleon 用 token 化做「世界语」。**越统一的世界语 = 核心熵减越彻底 = 边缘能组合的跨模态故事越多。** 这是 `故事原语/02-熵论辩证` 在模态层的直接体现。

> 维特根斯坦说「语言的界限即世界的界限」。对多模态 AI 而言：**它能统一多少模态到一种表示，它的「世界」就有多大。**

---

📌 **下一步**：五幕已齐。核心深读点是 `02`（InfoNCE + modality gap 数学）与 `04`（幻觉）；想接能力激活主线 → [`激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md) §5（LLaVA = 架构接入激活的范式样本）。
