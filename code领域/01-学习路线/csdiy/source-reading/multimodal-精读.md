# 多模态精读：CLIP / LLaVA / 视觉语言模型

> 参照：CLIP (Radford 2021) / LLaVA (Liu 2023) / BLIP-2 / GPT-4V
>
> csdiy 对应：tinyembedding + tinyvector + tinyrag + transformer-attention-deep

---

## 一、多模态：让 AI "看懂" 图片

```
文本模型（GPT/LLaMA）: 只懂文字
视觉模型（ResNet/ViT）: 只懂图片
多模态模型（GPT-4V）: 文字+图片都懂 → "这张图里有什么？"
```

---

## 二、CLIP（Contrastive Language-Image Pre-training）

### 核心：对比学习对齐图像和文本

```
训练数据: 4 亿 (图片, 文本描述) 对

方法:
  ① 图像编码器: Image → 512 维向量
  ② 文本编码器: Text → 512 维向量
  ③ 对比学习: 同一对的余弦相似度高，不同对的低
```

### 对比损失（InfoNCE）

```
对 N 个 (image_i, text_i) 对：
  最大化: sim(image_i, text_i) / sim(image_i, text_j)
  
= softmax over 所有 text j，正确 text_i 的对数似然
```

### 零样本分类

```
不需要训练分类器：

图片: [一只猫的图片]
候选标签: ["a photo of a dog", "a photo of a cat", "a photo of a car"]

CLIP:
  sim(image, "a photo of a cat") = 0.92  ← 最高
  sim(image, "a photo of a dog") = 0.31
  sim(image, "a photo of a car") = 0.05

→ 预测: cat
```

### CLIP 的能力

```
✅ 零样本图像分类（不需要训练分类头）
✅ 图像检索（"搜索'海滩日落'的图片"）
✅ 图文匹配
❌ 不能生成文本描述（只能打分）
```

---

## 三、BLIP-2（Bootstrapping Language-Image Pre-training）

### 架构：冻结视觉 + 冻结 LLM + 训练 Q-Former

```
图片 → 冻结的视觉编码器(ViT) → 视觉特征
                                      ↓
                        Q-Former（可训练，~188M 参数）
                                      ↓
                              固定长度的视觉 token
                                      ↓
文字 prompt + 视觉 token → 冻结的 LLM → 文本输出
```

### Q-Former

```
学习一组可训练的 query（如 32 个 token）
→ 从视觉特征中"提取"最相关的信息
→ 压缩成 LLM 能理解的 token

= 视觉信息的"翻译器"
```

### 为什么冻结视觉和 LLM

```
训练 Q-Former ≈ 训练 188M 参数
vs 训练完整模型 ≈ 10B+ 参数
→ 省 50x 训练成本
```

---

## 四、LLaVA（Large Language and Vision Assistant）

### 核心：最简单的多模态 LLM

```
① 视觉编码器: CLIP-ViT（冻结）
② 投影层: 线性层（可训练）→ 把视觉特征对齐到 LLM 的词嵌入空间
③ LLM: LLaMA/Vicuna（可训练或 LoRA）
```

### 训练流程

```
Stage 1: 预训练投影层
  数据: 595K (图片, 描述) 对
  只训练投影层，冻结其他
  → 学会把视觉特征"翻译"为 LLM 的语言

Stage 2: 指令微调
  数据: 158K (图片, 指令, 回答) 三元组
  训练投影层 + LLM（或 LoRA）
  → 学会回答关于图片的问题
```

### 效果

```
"这张图片有什么有趣的地方？"
→ LLaVA: "图中有一只猫坐在键盘上，这很搞笑因为..."

→ 接近 GPT-4V 的能力（在部分基准上）
→ 训练成本极低（~$500 GPU 时间）
```

---

## 五、GPT-4V / Gemini 的多模态

### 端到端训练

```
CLIP/LLaVA: 两阶段（视觉编码器 + LLM 分开训练）
GPT-4V:     端到端（视觉 token 直接和文本 token 拼接 → 一起训练）

→ 视觉和语言从预训练就交互 → 更深层的融合
```

### 能力

```
✅ 图片问答（"这道数学题怎么解？" + 拍照）
✅ 图表理解（"这个图表的趋势是什么？"）
✅ 多图推理（"这两张图有什么共同点？"）
✅ OCR（识别图片中的文字）
✅ 视觉创意（"画一个..." → DALL-E 生成）
```

---

## 六、多模态的 Embedding 对齐

### 问题：视觉向量和文本向量在不同空间

```
图片 "猫" → CLIP 图像编码 → [0.3, -0.5, ...] (图像空间)
文字 "猫" → CLIP 文本编码 → [0.4, -0.6, ...] (文本空间)

→ 对比学习让两个空间对齐 → 可以跨模态搜索
```

### 跨模态检索

```
用文字搜图片: text("沙滩日落") → 最相似的 images
用图片搜文字: image → 最相似的 text descriptions
```

---

## 七、和 tinyrag 的交叉

你的 `tinyrag` 可以扩展为多模态 RAG：

```python
# 文本 RAG
query_embedding = text_embedder.embed("猫的习性")
results = vectorstore.search(query_embedding)

# 多模态 RAG（扩展）
image_embedding = clip_image_encoder(image)
text_embedding = clip_text_encoder("描述这张图片")
combined = combine(image_embedding, text_embedding)
results = vectorstore.search(combined)
```

---

## 八、模型对比

| 模型 | 架构 | 视觉编码器 | LLM | 能力 |
|------|------|-----------|-----|------|
| CLIP | 双塔对比 | ViT | Transformer | 零样本分类/检索 |
| BLIP-2 | Q-Former | ViT (冻结) | OPT/FlanT5 | 图文理解/生成 |
| LLaVA | 线性投影 | CLIP-ViT (冻结) | LLaMA | 图片问答 |
| GPT-4V | 端到端 | 内置 | GPT-4 | 全能 |
| Gemini | 端到端 | 内置 | Gemini | 全能+视频 |
| Qwen-VL | 线性投影 | ViT | Qwen | 中英多模态 |

---

## 九、一句话总结

> CLIP = 对比学习对齐图文（零样本分类的基础）。
> LLaVA = 冻结视觉 + 线性投影 + LLM（最简单的多模态 LLM）。
> GPT-4V = 端到端融合（最强但不开源）。
>
> **多模态 = 让 AI 从"读文字"进化到"看世界"。**

---

*配套：tinyembedding（`../projects/tinyembedding/`） | [tinyrag/vectorstore.py](../projects/tinyrag/vectorstore.py) | [transformer-attention-deep](transformer-attention-deep-精读.md)*
