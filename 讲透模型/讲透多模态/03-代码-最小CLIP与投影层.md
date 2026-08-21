---
card_id: MM-03
title: "第 3 幕 · 代码：最小 CLIP 对比 + LLaVA 投影层"
universe: 讲透多模态
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: MM-04
---

# 💻 第 3 幕 · 代码：InfoNCE 对比 + LLaVA 投影层

用 numpy 演示 CLIP 的 InfoNCE loss 梯度方向，再用 PyTorch 写 LLaVA 风格的投影层。

## 1. InfoNCE 前向 + 梯度方向（numpy）

```python
import numpy as np

def InfoNCE(sim_matrix, temperature=0.07):
    """sim_matrix: [N,N], sim[i,j] = 图 i 与 文 j 的相似度.
    正对在对角线. 返回 loss."""
    N = sim_matrix.shape[0]
    logits = sim_matrix / temperature
    # 数值稳定
    logits = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    softmax = exp / exp.sum(axis=1, keepdims=True)
    loss = -np.log(softmax[np.arange(N), np.arange(N)] + 1e-9).mean()
    return loss, softmax

def grad_direction(sim_matrix, temperature=0.07):
    """InfoNCE 对相似度的梯度方向 (用于演示拉近正对/推远负对)."""
    _, softmax = InfoNCE(sim_matrix, temperature)
    N = sim_matrix.shape[0]
    grad = softmax.copy()
    grad[np.arange(N), np.arange(N)] -= 1.0  # dL/d sim
    return grad / N

if __name__ == "__main__":
    N = 4
    np.random.seed(0)
    # 假装: 图和文嵌入算出的相似度矩阵 (正对在对角线)
    sim = np.random.randn(N, N) * 0.3
    np.fill_diagonal(sim, 0.5)  # 正对相似度设高一点
    loss, _ = InfoNCE(sim)
    g = grad_direction(sim)
    print(f"初始 sim 矩阵:\n{np.round(sim,2)}")
    print(f"\nInfoNCE loss: {loss:.3f}")
    print(f"\n梯度方向 (负梯度=拉近, 正=推远):\n{np.round(g,3)}")
    print(f"\n对角线(正对)梯度: {np.round(np.diag(g),3)} (全负=拉近)")
    print(f"非对角(负对)梯度: {np.round(g[~np.eye(N,dtype=bool)],3)} (正=推远)")
    print("\n洞察: InfoNCE 自动拉近正对、推远负对. 这就是 CLIP 学对齐的机制.")
```

## 2. LLaVA 风格投影层（PyTorch）

```python
import torch, torch.nn as nn

class LLaVAProjector(nn.Module):
    """LLaVA 的核心: 把视觉特征投影成 LLM token."""
    def __init__(self, vis_dim=512, llm_dim=768):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(vis_dim, llm_dim),
            nn.GELU(),
            nn.Linear(llm_dim, llm_dim),
        )
    def forward(self, vis_features):  # [B, n_patches, vis_dim]
        return self.mlp(vis_features)  # [B, n_patches, llm_dim] -> 当视觉 token

class FakeVisionEncoder(nn.Module):
    """模拟 CLIP 视觉编码器."""
    def __init__(self, vis_dim=512):
        super().__init__()
        self.net = nn.Linear(3*14*14, vis_dim)  # 假装处理 14x14 RGB patch
    def forward(self, images):  # [B, 3, 14, 14]
        B = images.size(0)
        return self.net(images.view(B, -1)).unsqueeze(1)  # [B, 1, vis_dim]

class FakeLLM(nn.Module):
    """模拟 LLM 前向."""
    def __init__(self, dim=768, vocab=1000):
        super().__init__()
        self.embed = nn.Embedding(vocab, dim)
        self.out = nn.Linear(dim, vocab)
    def forward(self, vis_tokens, text_ids):
        text_emb = self.embed(text_ids)
        full = torch.cat([vis_tokens, text_emb], dim=1)  # 视觉 token 在前
        return self.out(full)  # [B, 1+T, vocab]

if __name__ == "__main__":
    vision = FakeVisionEncoder()
    proj = LLaVAProjector()
    llm = FakeLLM()
    img = torch.randn(2, 3, 14, 14)
    text = torch.randint(0, 1000, (2, 5))
    vis_feat = vision(img)
    vis_tokens = proj(vis_feat)
    logits = llm(vis_tokens, text)
    print(f"图像 {img.shape} -> 视觉特征 {vis_feat.shape}")
    print(f"-> 投影成视觉 token {vis_tokens.shape}")
    print(f"-> 拼文本 token -> LLM -> logits {logits.shape}")
    print(f"\n这就是 LLaVA 的全部'多模态融合': 一个 2 层 MLP.")
    print("重活在 vision encoder 和 LLM, 投影层只是维度对齐.")
```

## 这段代码教什么

1. **InfoNCE 梯度**：对角线（正对）梯度为负→拉近；非对角（负对）梯度为正→推远
2. **LLaVA 投影层**：整个「多模态融合」就一个 MLP——简单得让人怀疑，但有效
3. **token 拼接**：视觉 token 和文本 token 拼接送进 LLM，复用 LLM 全部推理

📌 **下一张卡** → `04-不足-多模态失败模式.md`
