"""tinygen — 参照 DDPM/GAN/VAE 的生成模型集"""
from .diffusion import DiffusionProcess
from .gan import GAN, Generator, Discriminator
from .vae import VAE, Encoder, Decoder
