#!/usr/bin/env python3
"""
tinygen/demo.py — 生成模型集 端到端演示

3 种生成模型的完整演示：
  1. DDPM 扩散模型（前向加噪 → 反向去噪采样）
  2. GAN 生成对抗网络（Generator vs Discriminator）
  3. VAE 变分自编码器（编码 → 潜空间 → 解码 → 生成/重建/插值）
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinygen.diffusion import DiffusionProcess, demo as diffusion_demo
from tinygen.gan import GAN, demo as gan_demo
from tinygen.vae import VAE, demo as vae_demo

def main():
    print("=" * 60)
    print("  tinygen — 生成模型集 端到端演示")
    print("  参照 DDPM + GAN + VAE")
    print("=" * 60)
    t0 = time.time()

    # DDPM 扩散模型
    diffusion_demo()

    # GAN
    gan_demo()

    # VAE
    vae_demo()

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  全部完成 ({elapsed:.1f}s)")
    print(f"  tinygen = diffusion.py + gan.py + vae.py + demo.py")
    print(f"  覆盖: 扩散模型 / 对抗生成 / 变分推断")
    print(f"{'='*60}")
    print(f"\n  三种生成模型对比:")
    print(f"    DDPM:  最强质量，慢（1000 步去噪）→ Stable Diffusion")
    print(f"    GAN:   最快推理，训练不稳定 → StyleGAN/FaceSwap")
    print(f"    VAE:   最快训练，质量中等 → 数据压缩/异常检测")

if __name__ == "__main__":
    main()
