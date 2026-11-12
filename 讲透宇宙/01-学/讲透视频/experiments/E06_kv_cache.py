"""
E06 解答 · 因果注意力 + KV-cache: 流式生成为什么快
====================================================
逐 token 因果生成, 对比:
  (a) 无 cache: 每步重算全部前缀的 K/V 再 attention
  (b) KV-cache: 历史 K/V 只算一次并缓存, 每步只算新 q 的 k/v

运行: python3 E06_kv_cache.py    # 约 15 秒
输出: E06_kv_cache.png
"""
import torch
torch.set_num_threads(1)
torch.manual_seed(0)
import time
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

D, HEADS = 256, 4
HS = D // HEADS
Wq, Wk, Wv = (torch.randn(D, D) * 0.05 for _ in range(3))


def attn(q, K, V):
    """q: (heads,1,hs); K,V: (heads,T,hs) → 因果性天然满足(K 全为历史)。"""
    a = torch.softmax((q @ K.transpose(-2, -1)) / HS ** 0.5, -1)
    return (a @ V).reshape(-1)


def gen_no_cache(T):
    """每步对全部前缀重新计算 K/V(浪费: 同一个 token 的 k/v 被反复重算)。"""
    tokens = [torch.randn(D)]
    for _ in range(1, T):
        X = torch.stack(tokens)                          # (t,D)
        K = (X @ Wk).view(-1, HEADS, HS).permute(1, 0, 2)  # 重算全部 K
        V = (X @ Wv).view(-1, HEADS, HS).permute(1, 0, 2)  # 重算全部 V
        q = (tokens[-1] @ Wq).view(HEADS, 1, HS)
        o = attn(q, K, V)
        tokens.append(tokens[-1] + o[:D])
    return tokens


def gen_with_cache(T):
    """KV-cache: 每个 token 的 k/v 只算一次, 存起来拼接。"""
    Kc, Vc = [], []
    x = torch.randn(D)
    for _ in range(T):
        Kc.append(x @ Wk)                                # 只算新 token
        Vc.append(x @ Wv)
        K = torch.stack(Kc).view(-1, HEADS, HS).permute(1, 0, 2)
        V = torch.stack(Vc).view(-1, HEADS, HS).permute(1, 0, 2)
        q = (x @ Wq).view(HEADS, 1, HS)
        o = attn(q, K, V)
        x = x + o[:D]
    return x


# 预热
gen_with_cache(16); gen_no_cache(16)

sizes = [64, 128, 256, 512]
t_nc, t_wc = [], []
for T in sizes:
    t0 = time.time(); gen_no_cache(T); t_nc.append((time.time() - t0) * 1000)
    t0 = time.time(); gen_with_cache(T); t_wc.append((time.time() - t0) * 1000)
    print(f"T={T:4d}  无cache {t_nc[-1]:8.1f}ms  |  KV-cache {t_wc[-1]:8.1f}ms  |  加速 {t_nc[-1]/t_wc[-1]:.1f}x")

fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(sizes, t_nc, 'o-', label='无 cache: 每步重算全部 K/V  $O(T^2)$ 总量')
ax.plot(sizes, t_wc, 's-', label='KV-cache: 每 token 只算一次  $O(T)$ 总量')
ax.set_xlabel('生成 token 数 T'); ax.set_ylabel('流式生成总耗时 (ms)')
ax.set_title(f'E06 · 因果注意力 + KV-cache (T=512 时 {t_nc[-1]/t_wc[-1]:.1f}x)\n—— CausVid 9.4 FPS 流式视频生成的机制基础')
ax.legend(); ax.grid(ls=':')
plt.tight_layout(); plt.savefig('E06_kv_cache.png', dpi=110, bbox_inches='tight')
print("\n[输出] E06_kv_cache.png")
