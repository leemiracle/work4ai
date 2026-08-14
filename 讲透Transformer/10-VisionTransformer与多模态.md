# 10 Vision Transformer 与多模态

> Transformer 不只属于语言。2020 年 ViT 把它搬进视觉, 2021+ CLIP/Flamingo 让它跨模态。
> 2025+ 趋势: **原生多模态 (early fusion)**, 文本和视觉 token 从第 1 层就融合。

> 💡 **CS25 连接**:
> - Andrew Brown (Meta, CS25 V5) "Transformers for Video Generation"
> - Sayak Paul (HuggingFace, CS25 V5) "Transformers in Diffusion Models"
> - Ming Ding (智谱, CS25 V4) "From LLMs to Large Multimodal Models" (CogVLM/CogAgent)

---

## 一、Vision Transformer (ViT, 2020)

### 把图像变成"token 序列"
图像 $\to$ 切成 $16 \times 16$ patch $\to$ 每个 patch 拉平成向量 $\to$ 当成一个 token。然后**原封不动**套用 NLP 的 Transformer Encoder。

$$\text{image } 224{\times}224 \to 196 \text{ 个 } 16{\times}16 \text{ patch} \to 196 \text{ 个 token}$$

### 关键洞察
- 之前 CV 用 CNN (局部归纳偏置强)。ViT 证明: **数据足够多时, Transformer 的全局 attention 比 CNN 局部卷积更强**。
- patch 是"图像里的词", self-attention 让远处的 patch 也能直接交互 (CNN 要堆很多层才间接交互)。

---

## 二、CLIP (2021) — 对比对齐

**双塔结构**: 图像 encoder + 文本 encoder, 对比学习让"图和它的描述"嵌入靠近, "图和不相关文本"远离。

$$\text{loss} = -\log\frac{\exp(\text{sim}(I,T^+)/\tau)}{\sum_j \exp(\text{sim}(I,T_j)/\tau)}$$

**意义**: 学到统一的图文嵌入空间, 零样本分类 (用类别名当文本)。这是所有现代多模态的基础。

---

## 三、多模态架构演化

### 1. Adapter/晚期融合 (LLaVA, 2023)
- 冻结的 vision encoder (常是 CLIP) 提取图像特征
- 一个 **projection/adapter** 把视觉特征对齐到语言模型的 token 空间
- 语言模型 (LLaMA) 处理"文本 token + 视觉 token"
- 简单有效, 但视觉和语言是"先各自处理再拼接"

### 2. 原生多模态 / 早期融合 (Llama 4, Gemini 3, 2025) 🔥
- 视觉 token 和文本 token **从第 1 层就拼在一起**进 Transformer
- **cross-modal attention 从第 1 层就建立**, 不再是事后对齐
- 更强的跨模态推理 (如"这张代码截图哪里错了")
- Gemini 3 扩展到视频 + 音频, 称"首个真正原生多模态基础模型"

> Ming Ding (智谱, CS25 V4): CogVLM (17B) 和 CogAgent 展示了视觉理解 + GUI/OCR 的应用方向。

---

## 四、Transformer 在生成模型里的角色

### Diffusion + Transformer (DiT)
扩散模型 (Stable Diffusion) 原本用 U-Net (CNN)。**DiT (2022)** 把去噪网络换成 Transformer, 成为 Sora/现代视频生成的架构。

### 视频生成
Andrew Brown (Meta, CS25 V5): 视频生成 = 时空 token 序列 + Transformer + 扩散。Transformer 的全局注意力天然适合长程时空依赖。

---

## 多模态速查

| 方法 | 融合方式 | 代表 | 时代 |
|------|---------|------|------|
| ViT | 图像分类 (纯视觉) | ViT, DeiT | 2020 |
| CLIP | 双塔对比 | CLIP | 2021 |
| LLaVA | 晚期融合 (adapter) | LLaVA, CogVLM | 2023 |
| **原生多模态** | **早期融合** | **Llama 4, Gemini 3** | 2025+ |

---

## 参考文献
- Dosovitskiy et al. 2020, *An Image is Worth 16x16 Words* (ViT)
- Radford et al. 2021, *Learning Transferable Visual Models* (CLIP)
- Peebles & Xie 2022, *Scalable Diffusion Models with Transformers* (DiT)
- CS25 V4: Ming Ding (CogVLM); V5: Andrew Brown (视频), Sayak Paul (Diffusion)
