"""
12_wan2_inference.py
====================
调用阿里 Wan 2.1 (1.3B) — 2025 年开源视频生成 SOTA。

关键事实（来自 arXiv:2503.20314）：
- 主流 diffusion transformer paradigm
- 1.3B 模型仅需 8.19 GB VRAM（消费级 GPU 友好！）
- 14B 验证视频生成 scaling law
- DiT + 3D VAE + flow matching + 多语言文本条件
- 覆盖 T2V / I2V / 视频编辑 / 个性化生成

需要：diffusers + transformers + accelerate（首次会下载 ~5GB 权重）
无网络时降级到离线说明。
"""
import sys


def check_deps():
    try:
        import diffusers
        import torch
        return True, None
    except ImportError as e:
        return False, str(e)


def try_run_wan():
    ok, err = check_deps()
    if not ok:
        print(f"[依赖缺失] {err}")
        return explain_only()

    import torch
    try:
        from diffusers import AutoPipelineForText2Video
        from diffusers.utils import export_to_video
    except ImportError:
        print("[!] diffusers 版本过旧，无 Wan。pip install -U diffusers")
        return explain_only()

    has_cuda = torch.cuda.is_available()
    if not has_cuda:
        print("[!] 无 CUDA，Wan 推理会非常慢。继续？(y/N)")
        if input().strip().lower() != 'y':
            return explain_only()

    print("[Wan 2.1] 加载 1.3B T2V 模型（仅需 8.19 GB VRAM）...")
    try:
        pipe = AutoPipelineForText2Video.from_pretrained(
            "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
            torch_dtype=torch.float16,
        ).to("cuda")
    except Exception as e:
        print(f"[!] 加载失败：{e}")
        return explain_only()

    prompts = [
        "A serene mountain lake at sunrise, mirror reflection, mist rising, cinematic 4K",
        "A futuristic city with flying cars, neon lights, rain, cyberpunk style",
        "A panda eating bamboo in a lush forest, soft sunlight, slow motion",
    ]

    for prompt in prompts:
        print(f"\n[Wan] 生成: {prompt[:60]}...")
        try:
            output = pipe(
                prompt=prompt,
                negative_prompt="blurry, low quality, distorted",
                num_frames=49,       # ~2 秒 @ 24fps
                num_inference_steps=30,
                guidance_scale=5.0,
                generator=torch.Generator("cuda").manual_seed(42),
            ).frames[0]
            fname = "wan_" + prompt[:20].replace(" ", "_").replace(",", "") + ".mp4"
            export_to_video(output, fname, fps=24)
            print(f"  saved {fname}")
        except Exception as e:
            print(f"  生成失败：{e}")


def explain_only():
    print("""
============================================================
Wan 2.1 架构详解（离线说明模式）
============================================================

【模型规格】(arXiv:2503.20314, 2025.3)
- Wan2.1-T2V-1.3B: 消费级 GPU（8.19 GB VRAM）
- Wan2.1-T2V-14B:  SOTA 开源，验证 scaling law

【架构 = DiT + 3D VAE + Flow Matching】

  prompt: "A panda eating bamboo"
              ↓
  [umT5 文本编码器]  (多语言支持)
              ↓ txt_emb [B, L, dim]
              ↓
  z_0 ~ N(0, I), shape = [B, C=16, T=21, H=W=latent_size]
              ↓
  for t in flow_matching_steps (4-50):
      v = DiT(z_t, t, txt_emb)  ← 3D RoPE + flow matching
      # Classifier-Free Guidance:
      v_uncond = DiT(z_t, t, "")
      v = v + w * (v - v_uncond)
      z_{t+dt} = z_t + v * dt
              ↓
  z_final
              ↓
  [3D VAE Decoder]  (时空联合解码)
              ↓
  pixel video [B, 3, T*4=84, H*8, W*8]

【关键创新】
1. 3D causal VAE: 因果卷积避免未来泄漏 → 长视频自回归可行
2. 3D RoPE: 直接编码时空相对位置
3. Flow Matching (rectified flow): 训练稳，推理快
4. Multi-resolution training: 多分辨率、多宽高比、多时长
5. Motion score conditioning: 用户控制运动强度

【DiT 结构（14B）】
- dim ≈ 5120, depth ≈ 40, heads ≈ 40
- 全 3D attention（T×H×W token 一起 attend）
- window attention 节省显存
- 双流：文本 token 与视频 token 联合注意力（类似 HunyuanVideo）

【推理加速技巧】
- TeaCache: 相邻去噪步 attention 输出近似 → 跳过部分计算
- FP8 量化: 显存减半，速度 2-3×
- Tiled VAE: 分块解码省显存
- CFG distillation: 减少 guidance 步数

【Wan 2.2 (2025.5+) 新增】
- 音视频同步生成（参考 Veo 3 方向）
- 更长时长支持
- 改进的运动控制
============================================================

替代模型对比（2025）：
| 模型 | 开源 | 参数 | 特点 |
|------|------|------|------|
| Wan 2.1/2.2 | ✓ | 1.3B/14B | 最佳开源，1.3B 消费级友好 |
| HunyuanVideo | ✓ | 13B | 双流 DiT，最大开源 |
| CogVideoX | ✓ | 5B/30B | 专家 Transformer |
| Open-Sora 2.0 | ✓ | 11B/20B | 数据驱动复刻 Sora |
| Mochi-1 | ✓ | 10B | Asymm DiT |
| LTX-Video | ✓ | 2B | 实时（秒级推理）|
| Sora | ✗ | 未公开 | 闭源标杆 |
| Kling 2.0 | ✗ | 未公开 | 闭源 SOTA |
| Veo 3 | ✗ | 未公开 | 同步音频 |
""")


if __name__ == "__main__":
    try_run_wan()
