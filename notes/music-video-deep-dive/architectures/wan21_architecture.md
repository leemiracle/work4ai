# Wan 2.1 架构分析

> 阿里 Wan 团队（2025.3），开源视频生成 SOTA。
> 论文：*Wan: Open and Advanced Large-Scale Video Generative Models* (arXiv:2503.20314)
> 论文实测：14B 在亿级图文+视频上训练，验证视频生成 **scaling law**。
> 1.3B 仅需 **8.19 GB VRAM**（消费级 GPU 友好）

## 1. 设计哲学

Wan 的核心贡献不是单一技术突破，而是**系统性工程**：
- 主流 diffusion transformer paradigm（DiT + flow matching + 3D VAE）
- 大规模数据筛选（数十亿图文 + 亿级视频）
- 自动评估指标
- 全开源（代码 + 1.3B + 14B 权重）

## 2. 模型规格

| 模型 | 参数 | VRAM | 目标 |
|------|------|------|------|
| Wan2.1-1.3B | 1.3B | 8.19 GB | 消费级 GPU（RTX 3060/4060）|
| Wan2.1-14B | 14B | ~60 GB（FP8 后 30 GB）| SOTA 质量 |

## 3. 架构

```
prompt → [umT5 文本编码器]
              ↓
z_0 ~ N(0,I)  ↓
   ↓          ↓
   DiT (3D RoPE + flow matching + 全 3D attention)
              ↓
        v_θ(z_t, t, text)
              ↓
   Euler + CFG → z_final
              ↓
   [3D VAE Decoder] → video
```

## 4. 关键组件

### 4.1 umT5 文本编码器
多语言 T5（中、英、日、韩、欧语），让 Wan 支持非英文 prompt。

### 4.2 DiT 主干（14B）
- 40 层 Transformer block
- dim ≈ 5120
- **全 3D attention**（不分离时空）
- window attention + full attention 混合（省显存）

### 4.3 3D VAE
- 自研架构
- 压比 4 × 8 × 8（时间 4，空间 8）
- chunk-based 训练（处理长视频）

### 4.4 3D RoPE
- 编码时空相对位置
- 外推性好（训练 5s，可推 10s+）

### 4.5 Flow Matching
- rectified flow 训练
- 推理 30 步

## 5. 训练数据

- **图像**：数十亿张（图文对）
- **视频**：亿级片段
- 严格筛选：
  - 运动幅度过滤（避免静止视频）
  - 美学评分（用美学分类器）
  - 文本对齐（用 VLM 自动 caption + 过滤）
- 多分辨率、多宽高比、多时长分桶

## 6. Scaling Law 实证

论文关键贡献之一：**首次系统证明视频生成遵循 scaling law**——
- 模型从 1.3B → 14B
- 数据从 1B → 100B tokens
- 验证损失单调下降
- 主观质量显著提升

→ 这为继续 scaling 到 100B+ 提供理论依据。

## 7. 8 个下游任务

Wan 不只是 T2V，而是视频基础模型：

1. **T2V**（text-to-video）
2. **I2V**（image-to-video）
3. **First-Last Frame to Video**
4. **Video Editing**（指令引导）
5. **Video Composition**（多视频融合）
6. **Personal Video Generation**（参考身份）
7. **Camera Control**（镜头方向控制）
8. **Audio Generation**（Wan 2.2 加入）

## 8. 评估指标

Wan 团队贡献了自动化评估：
- VBench（多维质量）
- Motion Score（运动强度）
- Text-Video Alignment（CLIP-Sim）
- Aesthetic Score

## 9. 推理加速

- **TeaCache**：跨步复用 attention
- **FP8 量化**：显存减半
- **Tiled VAE**：分块解码
- **CFG distillation**：减少步数

## 10. Wan 2.2（2025.5+）新增

- **音视频同步生成**（参考 Veo 3 方向）
- 更长视频支持
- 改进 motion control
- 更细可控性（reference frame / sketch）

## 11. 复现成本评估

- 1.3B 模型：消费级 GPU（RTX 3060 12GB）即可跑
- 14B 模型：A100/H100 单卡或 4×4090
- 训练：未公开，估计千卡规模 + 数月
- 数据：未公开，但社区有 1B+ 开源视频可用

## 12. 对行业的意义

Wan 2.1 是**开源视频生成追赶闭源的关键里程碑**：
- 首次有开源模型在 VBench 上接近 Kling/Sora
- 1.3B 版本让普通开发者也能跑视频生成
- 全开源（含训练细节）推动社区快速迭代
