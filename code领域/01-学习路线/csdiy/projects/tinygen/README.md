# tinygen — 生成模型集

> 参照 DDPM (扩散模型) + GAN (对抗生成) + VAE (变分自编码器)，三大生成模型范式。

## 模块清单

| 文件 | 参照 | 核心内容 |
|------|------|---------|
| `diffusion.py` | DDPM (Ho 2020) / Stable Diffusion | 前向加噪 + 反向去噪 + 训练损失 |
| `gan.py` | GAN (Goodfellow 2014) / DCGAN | Generator + Discriminator 对抗训练 |
| `vae.py` | VAE (Kingma 2013) | 编码器→重参数化→解码器 + KL 散度 + 潜空间插值 |
| `demo.py` | — | 3 种生成模型端到端演示 |

## 三种生成模型对比

| 维度 | DDPM 扩散 | GAN 对抗 | VAE 变分 |
|------|----------|---------|---------|
| 原理 | 逐步加噪/去噪 | 博弈论（纳什均衡） | 变分推断（ELBO） |
| 生成质量 | ⭐⭐⭐⭐⭐ 最佳 | ⭐⭐⭐⭐ 好 | ⭐⭐⭐ 中等 |
| 生成速度 | ⭐ 最慢（1000步） | ⭐⭐⭐⭐ 快 | ⭐⭐⭐⭐ 快 |
| 训练稳定性 | ⭐⭐⭐⭐ 稳定 | ⭐⭐ 不稳定 | ⭐⭐⭐⭐ 稳定 |
| 代表应用 | Stable Diffusion | StyleGAN / FaceSwap | 异常检测 / 压缩 |
| 数学核心 | 随机微分方程 | 极小极大博弈 | KL 散度 + 重参数化 |

## 端到端演示

```bash
python3 projects/tinygen/demo.py
```

## csdiy 知识交叉

- `tinytorch` — 生成模型的训练框架（autograd + optimizer）
- [nanoGPT 精读](../../source-reading/nanoGPT-读懂最小GPT.md) — 扩散模型的 U-Noise 架构类比
- `tinyml`（已整合到 tinytorch）— 梯度下降是所有生成模型的基础
