"""
10_3d_rope.py
============
3D Rotary Position Embedding (3D RoPE) — 2024-2025 视频模型的关键。

RoPE (Rotary Position Embedding, Su et al. 2021) 是 LLaMA 系的位置编码。
原理：通过对 query/key 做角度旋转，让 attention 自然编码相对位置。

3D RoPE：把 RoPE 扩展到 (T, H, W) 三维 —— HunyuanVideo、Wan、CogVideoX 都用。

本文件实现：
1. 1D RoPE（基础）
2. 3D RoPE（视频）
3. 演示相对位置感知
"""
import torch
import torch.nn.functional as F
import math


def rotate_half(x):
    """把后半部分取负并交换：[a, b] → [-b, a]（旋转矩阵的核心）"""
    x1, x2 = x[..., :x.shape[-1] // 2], x[..., x.shape[-1] // 2:]
    return torch.cat([-x2, x1], dim=-1)


def apply_rope_1d(q, freqs):
    """1D RoPE：q, k 旋转 freqs 角度。freqs: [N, dim/2]"""
    # q: [B, H, N, D], freqs: [N, D]
    cos = freqs.cos().unsqueeze(0).unsqueeze(0)  # [1, 1, N, D]
    sin = freqs.sin().unsqueeze(0).unsqueeze(0)
    q_rot = q * cos + rotate_half(q) * sin
    return q_rot


def rope_freqs_1d(N, dim, base=10000, device='cpu'):
    """生成 1D RoPE 频率表"""
    half = dim // 2
    pos = torch.arange(N, device=device).float()
    inv_freq = 1.0 / (base ** (torch.arange(0, half, device=device).float() / half))
    freqs = torch.einsum('i,j->ij', pos, inv_freq)
    # 复制成 dim 大小（cos/sin 用）
    return torch.cat([freqs, freqs], dim=-1)  # [N, dim]


def rope_freqs_3d(T, H, W, dim, base=10000, device='cpu'):
    """
    3D RoPE：把 dim 三等分，分别编码 T, H, W 位置。
    返回 [T*H*W, dim] 频率表。
    """
    d3 = dim // 3
    # 补齐：每轴 dim/3，总 dim。最后一轴吸收余数
    d_t, d_h, d_w = d3, d3, dim - 2 * d3
    # rope_freqs_1d(N, dim) 返回 [N, dim]，三轴拼接总长 = d_t + d_h + d_w = dim
    ft = rope_freqs_1d(T, d_t, base, device)  # [T, d_t]
    fh = rope_freqs_1d(H, d_h, base, device)  # [H, d_h]
    fw = rope_freqs_1d(W, d_w, base, device)  # [W, d_w]

    # 笛卡尔积 + 拼接
    freqs = []
    for t in range(T):
        for h in range(H):
            for w in range(W):
                f = torch.cat([ft[t], fh[h], fw[w]])
                freqs.append(f)
    return torch.stack(freqs)  # [T*H*W, dim]


def apply_rope_3d(q, T, H, W, dim, device='cpu'):
    """
    对视频 token 序列应用 3D RoPE。
    q: [B, n_heads, T*H*W, dim]
    """
    freqs = rope_freqs_3d(T, H, W, dim, device=device)  # [N, dim]
    cos = freqs.cos().unsqueeze(0).unsqueeze(0)  # [1, 1, N, dim]
    sin = freqs.sin().unsqueeze(0).unsqueeze(0)
    q_rot = q * cos + rotate_half(q) * sin
    return q_rot


def demonstrate_relative_encoding():
    """演示：3D RoPE 让 attention 自然感知空间-时间距离"""
    torch.manual_seed(0)
    T, H, W = 2, 4, 4
    dim = 96
    n_heads = 4

    # 随机 query/key
    N = T * H * W
    q = torch.randn(1, n_heads, N, dim)
    k = torch.randn(1, n_heads, N, dim)

    # 应用 3D RoPE
    q_rot = apply_rope_3d(q, T, H, W, dim)
    k_rot = apply_rope_3d(k, T, H, W, dim)

    # attention 矩阵
    attn_no_rope = torch.einsum('bhnd,bhmd->bhnm', q, k) / math.sqrt(dim)
    attn_with_rope = torch.einsum('bhnd,bhmd->bhnm', q_rot, k_rot) / math.sqrt(dim)

    # 看每个 token 对"自己的最近邻（空间相邻，同时刻）"的注意力
    print("[3D RoPE 注意力模式分析]")
    print(f"  网格: T={T}, H={H}, W={W}, N={N}, dim={dim}")

    # 计算 token 0 (t=0, h=0, w=0) 到所有其他 token 的"真实距离"
    coords = [(t, h, w) for t in range(T) for h in range(H) for w in range(W)]
    dists_from_0 = [math.sqrt((c[0]-coords[0][0])**2 + (c[1]-coords[0][1])**2 + (c[2]-coords[0][2])**2)
                    for c in coords]

    # 看 RoPE 后 attention 与距离的相关性
    attn_head0 = attn_with_rope[0, 0, 0]  # token 0 的 attention 分布
    corr = torch.corrcoef(torch.stack([torch.tensor(dists_from_0, dtype=torch.float32), attn_head0]))[0, 1]
    print(f"  token 0 的 attention 与'真实距离'相关性 (RoPE): {corr:.3f}")

    attn_head0_norope = attn_no_rope[0, 0, 0]
    corr_no = torch.corrcoef(torch.stack([torch.tensor(dists_from_0, dtype=torch.float32), attn_head0_norope]))[0, 1]
    print(f"  token 0 的 attention 与'真实距离'相关性 (无 RoPE): {corr_no:.3f}")
    print(f"\n  → RoPE 让 attention 倾向关注'位置近'的 token（相关性更负）")


if __name__ == "__main__":
    print("=" * 60)
    print("3D RoPE (Rotary Position Embedding) demo")
    print("=" * 60)
    demonstrate_relative_encoding()

    print("\n[使用情况]")
    print("  HunyuanVideo (13B): 3D RoPE + 双流 DiT")
    print("  Wan 2.1/2.2:        3D RoPE + flow matching")
    print("  CogVideoX:          3D RoPE + 专家 Transformer")
    print("  LLaMA / Qwen:       1D RoPE（文本）")
    print("\n[vs ALiBi / 绝对位置编码]")
    print("  - 绝对位置编码：attention 不直接感知相对距离")
    print("  - ALiBi：线性偏置，无外推限制但缺乏语义")
    print("  - RoPE：通过旋转编码相对位置，外推性好")
    print("  - 3D RoPE：直接扩展到视频时空，无需 flattening 歧义")
    print("=" * 60)
