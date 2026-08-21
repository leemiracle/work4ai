---
card_id: CV-03
title: "第 3 幕 · 代码：最小 CNN / ViT / DDPM"
universe: 讲透CV
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: CV-04
---

# 💻 第 3 幕 · 代码：numpy conv2d + mini-ViT + DDPM 采样器

三个范式的最小实现，每个都能跑。

## 1. numpy conv2d 前向

```python
import numpy as np

def conv2d(x, kernel):
    """x: [H,W], kernel: [k,k] -> 输出 [H-k+1, W-k+1]."""
    k = kernel.shape[0]
    H, W = x.shape
    out = np.zeros((H-k+1, W-k+1))
    for i in range(H-k+1):
        for j in range(W-k+1):
            out[i,j] = np.sum(x[i:i+k, j:j+k] * kernel)
    return out

if __name__ == "__main__":
    img = np.random.rand(8, 8)
    # 边缘检测核 (Sobel-x)
    sobel = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    edges = conv2d(img, sobel)
    print(f"conv2d: {img.shape} --sobel--> {edges.shape}")
    print(f"边缘响应均值: {edges.mean():.3f} (原图梯度越大越亮)")
```

## 2. mini-ViT（PyTorch，100 行内）

```python
# pip install torch (CPU 即可)
import torch, torch.nn as nn

class MiniViT(nn.Module):
    """超小 ViT: patch embed + 1 层 transformer."""
    def __init__(self, img_size=28, patch_size=7, in_ch=1, d=64, n_classes=10):
        super().__init__()
        self.n_patches = (img_size // patch_size) ** 2
        self.patch_embed = nn.Conv2d(in_ch, d, patch_size, patch_size)  # 把图切块投影
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d))
        self.pos_embed = nn.Parameter(torch.zeros(1, self.n_patches+1, d))
        enc_layer = nn.TransformerEncoderLayer(d, nhead=4, batch_first=True)
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=2)
        self.head = nn.Linear(d, n_classes)

    def forward(self, x):  # x: [B, C, H, W]
        p = self.patch_embed(x).flatten(2).transpose(1,2)  # [B, N, d]
        c = self.cls_token.expand(p.size(0), -1, -1)
        p = torch.cat([c, p], dim=1) + self.pos_embed
        p = self.encoder(p)
        return self.head(p[:, 0])  # cls token 做分类

if __name__ == "__main__":
    model = MiniViT()
    x = torch.randn(2, 1, 28, 28)  # MNIST 风格
    logits = model(x)
    print(f"mini-ViT: input {x.shape} -> logits {logits.shape}")
    print(f"参数量: {sum(p.numel() for p in model.parameters()):,}")
```

## 3. DDPM 采样器（去噪生成）

```python
import numpy as np

def ddpm_sample(model_score, shape, n_steps=100):
    """从纯噪声开始, 反复去噪生成样本.
    model_score: 函数, 给 x_t 返回预测的噪声 epsilon.
    """
    betas = np.linspace(1e-4, 0.02, n_steps)
    alphas = 1 - betas
    alpha_bars = np.cumprod(alphas)
    x = np.random.randn(*shape)  # x_T ~ N(0, I)
    for t in reversed(range(n_steps)):
        eps = model_score(x, t)
        mu = (x - betas[t]/np.sqrt(1-alpha_bars[t]) * eps) / np.sqrt(alphas[t])
        if t > 0:
            x = mu + np.sqrt(betas[t]) * np.random.randn(*shape)
        else:
            x = mu
    return x

# demo: model_score 是个 toy (真实场景是 U-Net)
def toy_score(x, t):
    """简化: 假装预测的噪声就是 x 的某个变换."""
    return 0.5 * x / (np.linalg.norm(x) + 1e-6)

if __name__ == "__main__":
    sample = ddpm_sample(toy_score, shape=(4,))
    print(f"DDPM 采样结果: {sample}")
    print(f"从 N(0,I) 噪声出发, 去噪 100 步得到: 均值={sample.mean():.3f}, std={sample.std():.3f}")
    print("(toy score 下结果无意义, 真实场景 model_score 是训过的 U-Net)")
```

## 这段代码教什么

1. **conv2d**：参数共享的局部线性，numpy 双循环直观
2. **mini-ViT**：patch embed 把图变 token，之后和 NLP Transformer 一样
3. **DDPM**：从噪声反向去噪，核心是 `(x - β/√(1-ᾱ)·ε)/√α` 的迭代

**真实场景**：conv2d 用 im2col 加速；ViT 用预训练权重（DINOv2）；DDPM 用 U-Net + classifier-free guidance。

📌 **下一张卡** → `04-不足-CV失败模式.md`
