# HunyuanVideo 双流 DiT 深度拆解

> 腾讯混元视频生成模型（2024.12），13B 参数，**当前最大开源视频 DiT**。
> 论文：*HunyuanVideo: A Systematic Framework For Large Video Generation Models*

## 1. 整体架构

```
prompt: "..."
    ↓
[umT5 / multilingual text encoder] → txt_tokens [B, L_t, dim]
                                            │
z_0 ~ N(0,I), shape [B, C=16, T, H, W]      │
    │                                        │
    │   ┌────────────────────────────────────┘
    │   │
    ↓   ↓
┌─────────────────────────────────────────────────┐
│  双流 DiT (Dual-Stream DiT)                     │
│                                                 │
│  Stream A (video tokens):                      │
│   video_toks = patchify(z_t) → [B, N_v, dim]   │
│                                                 │
│  Stream B (text tokens):                        │
│   txt_toks → [B, L_t, dim]                     │
│                                                 │
│  每个 block:                                    │
│   1. video self-attention                       │
│   2. text self-attention                        │
│   3. video-text cross-attention (联合)          │
│   4. MLP                                         │
│   5. adaLN-Zero 调制（time + text 条件）         │
└─────────────────────────────────────────────────┘
    ↓
v_θ(z_t, t, txt)  ← flow matching 向量场预测
    ↓
Euler 积分 → z_final
    ↓
[3D VAE Decoder] → 像素视频
```

## 2. 关键创新点

### 2.1 双流注意力（Dual-Stream）
不同于传统 DiT 把文本 token 拼接到视频 token 序列末尾，HunyuanVideo 让**视频和文本各自做 self-attention，再 cross-attention 交换信息**。
- 优点：文本语义信息更细粒度注入视频
- 类似 Qwen2-VL、Janus 的多模态分离设计

### 2.2 3D VAE
- 压比 **4 × 8 × 8 = 256×**（时间 4，空间 8）
- **chunk-based**：训练时把长视频分块编码，避免显存爆炸
- 因果卷积（避免未来泄漏）

### 2.3 3D RoPE
- 把 RoPE 三等分，分别编码 T/H/W
- 比 ALiBi 或绝对位置编码外推性更好

### 2.4 Flow Matching（不是 DDPM）
- 用 rectified flow 训练
- 推理只需 30 步即可高质量
- 比 DDPM 训练更稳

### 2.5 分桶训练（Bucket Training）
- 多分辨率（512², 720p, 1080p）
- 多宽高比（16:9, 9:16, 1:1, 4:3）
- 多时长（5s, 10s）
- 让单一模型支持各种输出格式

## 3. 13B 参数的组成

| 组件 | 参数占比 | 说明 |
|------|---------|------|
| umT5 文本编码器 | ~5B | 多语言（中英日韩等）|
| DiT 主体 | ~7B | 40 层，dim 5120 |
| 3D VAE | ~1B | 编码器 + 解码器 |

## 4. 训练数据
- 数千万视频片段（开源/许可数据）
- 严格质量筛选：运动幅度、美学评分、文本对齐
- 文本 caption 用 VLM 自动生成 + 人工筛选

## 5. 推理流程

```python
# 伪代码
text = umT5(prompt)                    # 文本编码
z = randn(B, 16, T//4, H//8, W//8)    # 初始噪声
for t in flow_steps:                  # 30 步
    v_cond = dit(z, t, text)
    v_uncond = dit(z, t, "")
    v = v_uncond + w * (v_cond - v_uncond)  # CFG, w≈6
    z = z + v * dt                     # Euler
video = vae.decode(z)                  # 3D VAE 解码
```

## 6. 性能对比（VBench，截至 2025.5）

| 模型 | 总分 | 开源 |
|------|------|------|
| HunyuanVideo 13B | 84.2 | ✓ |
| Wan 2.1 14B | 86.1 | ✓ |
| Kling 1.6 | ~85 | ✗ |
| Sora | 未公布 | ✗ |
| Veo 2 | ~87 | ✗ |

## 7. 工程优化

- **FP8 量化**：显存从 60GB → 30GB
- **TeaCache**：跨去噪步复用 attention，加速 1.8×
- **Tiled VAE**：分块解码省显存
- **序列并行**：长序列 attention 分布式计算

## 8. 局限

- 长视频（>10s）一致性差
- 物理细节（玻璃破裂、流体）经常错误
- 文本渲染（特定字幕、logo）不稳定

## 9. 后续（Wan 2.2 思路借鉴）
- 加入音频生成（参考 Veo 3）
- 改进 3D VAE 减少时间下采样损失
- 更长 context 训练
