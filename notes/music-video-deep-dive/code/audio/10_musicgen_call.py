"""
10_musicgen_call.py
===================
调用 Meta MusicGen（开源文本到音乐模型）。

需要：transformers + torch（已安装）+ 首次运行会下载 ~5GB 权重。
如果无网络或显存不足，会优雅降级到说明模式。

MusicGen 架构（Copet et al., Meta 2023）：
1. EnCodec 把音频压成离散 token（RVQ 多码本）
2. 单 Transformer 自回归预测 token（"delay pattern"把多码本展平成单序列）
3. 文本通过 T5/FLAN-T5 encoder 提供 conditioning
4. Classifier-free guidance

模型规模：300M / 1.5B / 3.3B
"""
import sys


def check_deps():
    try:
        import transformers
        import torch
        return True
    except ImportError as e:
        print(f"[依赖缺失] {e}")
        return False


def try_run_musicgen():
    if not check_deps():
        return explain_only()

    import torch
    try:
        from transformers import MusicgenForConditionalGeneration, AutoProcessor
    except ImportError:
        print("[!] transformers 版本过旧，无 MusicGen。pip install -U transformers")
        return explain_only()

    print("[MusicGen] 加载 processor 和小模型 (300M)...")
    try:
        processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    except Exception as e:
        print(f"[!] 加载失败（可能无网络/磁盘空间）：{e}")
        return explain_only()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"[MusicGen] 设备: {device}")

    prompts = [
        "80s pop track with groovy synth bass and electronic drums",
        "lo-fi hip hop, mellow piano, vinyl crackle, slow tempo",
        "epic orchestral cinematic, soaring strings, timpani",
    ]

    for prompt in prompts:
        print(f"\n[MusicGen] 生成: {prompt[:60]}...")
        inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
        # 5 秒音频（每秒约 50 个 token）
        audio_values = model.generate(**inputs, max_new_tokens=256, do_sample=True, guidance_scale=3.0)

        # 保存
        sr = model.config.audio_encoder.sampling_rate
        audio = audio_values[0, 0].cpu().numpy()
        try:
            from scipy.io import wavfile
            audio16 = (audio / max(abs(audio.max()), abs(audio.min())) * 32767).astype("int16")
            fname = "musicgen_" + prompt[:20].replace(" ", "_").replace(",", "") + ".wav"
            wavfile.write(fname, sr, audio16)
            print(f"  saved {fname}  ({len(audio)/sr:.1f}s @ {sr} Hz)")
        except Exception as e:
            print(f"  保存失败: {e}")


def explain_only():
    print("""
============================================================
MusicGen 架构详解（无网络时的离线说明模式）
============================================================

输入: 文本 "80s pop track with groovy bass"
      ↓
[T5 / FLAN-T5 encoder]  (文本 → 语义向量)
      ↓
[Transformer decoder]   (自回归预测 audio tokens)
      │                  用 "delay pattern" 把多码本 EnCodec token
      │                  展平成单序列，统一 attention
      ↓
[EnCodec decoder]       (token → 波形)
      ↓
输出: 24 kHz mono PCM

关键算法：
  - Classifier-Free Guidance (CFG):
      training 时随机 drop 文本 10-20%
      inference: ε_guided = ε_cond + w·(ε_cond - ε_uncond)
      w=3 典型
  - Delay pattern: 把第 c 个码本延迟 c 步，确保每步只预测一个新 token
  - 多码本并行：每个时间步同时输出所有码本的 token

模型规模：
  - musicgen-small: 300M  → 快速实验
  - musicgen-medium: 1.5B → 质量明显提升
  - musicgen-large: 3.3B  → 最佳质量

替代/相关模型：
  - Jasco (Meta 2024): 可控和弦/节拍/旋律
  - Stable Audio Open (Stability 2024): 扩散路线
  - Suno v4 / Udio: 商业，闭源但据信类似 token 自回归

跑起来后，你可以：
  - 改 max_new_tokens 控制时长（约 50 tokens/秒）
  - 改 guidance_scale（1=保守, 3=推荐, 10=激进）
  - 用 transformers 中 MusicgenForConditionalGeneration 的 .generate_from_codes 输入参考音频
============================================================
""")


if __name__ == "__main__":
    try_run_musicgen()
