# Sora：我们已知什么、不知道什么

> OpenAI 视频生成模型（2024.2 发布），未公开技术报告，未开源。
> 本文整理从演示视频、博客、专利、社区逆向工程推测的信息。

## 1. 官方信息（OpenAI 公开过的）

OpenAI 在 2024.2.15 发布博客 *"Sora 抢先看"*，明确：
- "Sora 是文本到视频的扩散模型"
- "我们将视频和图像统一表示为 **patches**（时空 token）"
- "和 LLM 用 text token 类似，Sora 用 visual patches"
- "目标是 **world simulators**（世界模拟器）"

这是关键：Sora 用 **DiT (Diffusion Transformer) + 时空 patch tokenization**，**不是 U-Net**。

## 2. 推测架构

```
prompt: "..."
    ↓
[text encoder, 可能是 CLIP/T5]
    ↓
spatiotemporal patches ← 视频切 (t, h, w) 三维 patch
    ↓
DiT Transformer (大模型，规模未公开)
    ↓
denoised patches
    ↓
patch decoder → 像素视频
```

## 3. 关键技术推测

### 3.1 Spatiotemporal Patchification
- 把视频看作 3D tensor
- 切成 (t_patch × h_patch × w_patch) 立方体
- 每个立方体 flatten 成一个 token
- 这是 DiT 标准做法（Peebles & Xie ICCV 2023）

### 3.2 不用 VAE？还是用？
- 官方未明确
- 推测：用 latent（类似 SD），但 patchify 在 latent 空间
- 也可能直接像素 patch（计算量大但避免 VAE 失真）

### 3.3 训练数据
- 未公开
- 推测：DALL-E 3 / GPT-4V 数据复用 + 大规模视频
- 可能用 Sora 自己生成的数据训练（self-distill）

### 3.4 规模
- 完全未公开
- 推测：100B+ 参数（基于演示质量）
- 训练算力：估计数千 H100 × 数月

## 4. 已知能力（从演示推断）

- 最长 **60 秒**视频
- 高分辨率（1080p+）
- 复杂场景（多人、多物体、镜头切换）
- 一致性物体（角色跨镜头保持身份）
- 物理近似（重力、碰撞、流体）—— 但有失败案例
- 文本渲染（字幕、招牌）

## 5. 已知失败模式（OpenAI 自己公开）

OpenAI 在博客里展示过失败案例：
- **玻璃杯从桌上摔下，杯子穿过桌面** → 物理错误
- **人咬了一口饼干，下一秒饼干完整** → 持续性错误
- **左右颠倒** → 空间理解错误
- **多人互动混乱**（如握手时手指融合）

→ 这些证明 Sora 学的是"像素相关"，**不是真正的物理因果模型**。

## 6. Sora 的"世界模型"叙事争议

OpenAI 强调 Sora 是"world simulators"。但学术圈争议：

**支持方**：
- 视频模型确实学到一些隐式 3D/物理
- 大规模 + 大模型可能涌现物理理解

**反对方**（LeCun 等）：
- 生成像素 ≠ 理解世界
- 真世界模型应该预测抽象 latent（如 JEPA），不是像素
- Sora 失败案例证明它没有真正的因果模型

## 7. Sora 的发布延迟

- 2024.2 演示
- 2024.12 "12 Days of OpenAI" 仍未对公众开放
- 限制访问给红队、艺术家、电影人
- 推测原因：算力成本、安全（Deepfake）、未达到产品标准
- 直到 2024.12 才对 ChatGPT Plus/Pro 用户开放

## 8. 与开源对比（2025.5）

| 模型 | 是否开源 | 公众可达 | VBench |
|------|---------|---------|--------|
| Sora | ✗ | ChatGPT 付费 | 未公布 |
| Kling 2.0 | ✗ | 网页免费 | ~85 |
| Wan 2.1 14B | ✓ | HuggingFace | 86.1 |
| HunyuanVideo | ✓ | HuggingFace | 84.2 |

**开源已经追上甚至部分超越 Sora**（Wan 2.1 14B）。

## 9. Sora 启示

即使没公开技术，Sora 改变了视频生成领域：
- 确立 **DiT + spatiotemporal patch** 为标准范式
- 推动 **scaling law** 在视频生成的应用
- 引发 **world model** 大讨论
- 让开源社区全力追赶（Open-Sora, CogVideoX, HunyuanVideo, Wan）

## 10. 进一步阅读

- OpenAI 2024.2.15 blog: *"Sora 抢先看"*
- Peebles & Xie ICCV 2023 *Scalable Diffusion Models with Transformers* (DiT 原论文)
- Open-Sora, CogVideoX, HunyuanVideo, Wan 论文（开源复刻/超越）
- LeCun JEPA 系列论文（反对生成式世界模型）
