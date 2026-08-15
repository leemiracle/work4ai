"""
14_rans.py
==========
论文级 rANS (range Asymmetric Numeral Systems) 实现 —— AV1 的熵编码器。

参考：Fabian Giesen 的经典博客 "Interleaved entropy coders"（ryg blog 2014）
以及 Jarek Duda 的原始论文 (arXiv:1311.2540)。

为什么 AV1 弃 CABAC 选 rANS：
- CABAC 强串行（每 bit 依赖前一个）
- rANS 是 64/256 路 interleaved（多状态并行解码），硬件/软件都友好
- 相同压缩率下解码速度快 3-5×

实现要点：
- 静态频率表 f[s]，M = Σf[s]（编码区间基数，b=2 的幂便于移位）
- 编码：x' = (x // f[s])·M + cum[s] + (x mod f[s])   ← 一个除法+乘法
- renorm：x 太小则吸收 k bits
- 解码：slot = x mod M → 查表得 s；逆向恢复 x
- interleaved：N 个独立状态轮流编/解码 → 流水线并行

本文件实现单状态 + 8 状态 interleaved 版本，往返验证，对比熵极限。
"""
import numpy as np


class rANSCoder:
    """单状态静态概率 rANS（b=2, renorm 精度 16-bit）"""

    def __init__(self, freqs, prob_bits=14):
        self.prob_bits = prob_bits
        self.M = 1 << prob_bits          # 总质量 2^14 = 16384
        freqs = np.asarray(freqs, dtype=np.int64)
        # 归一化频率到 Σ = M（静态表的标准做法）
        self.freqs = np.maximum(1, np.round(freqs / freqs.sum() * self.M).astype(np.int64))
        diff = self.M - self.freqs.sum()
        self.freqs[0] += diff            # 修正舍入误差
        self.cum = np.concatenate([[0], np.cumsum(self.freqs)])[:-1]
        self.n_symbols = len(freqs)
        self.L = 1 << 16                 # renorm 下界（IO 精度 16 bits）
        self.IMAX = (1 << 32) - 1        # x 上界（防溢出）

    # ---------- 编码（符号从后往前 → 解码从前往后）----------
    def encode(self, symbols):
        x = self.L
        stream = []                      # (n_bytes_of_bits, value) 对；demo 直接存 bytes
        bitbuf = []                      # 简化：存 renorm 出来的 bit 流（用整数对）
        for s in reversed(symbols):
            f = int(self.freqs[s]); c = int(self.cum[s])
            # renorm：确保 x // f 之后仍在 32-bit 内
            while x >= (self.IMAX // self.M) * f:
                bitbuf.append(x & 0xFFFF)   # 输出低 16 bits
                x >>= 16
            x = (x // f) * self.M + c + (x % f)
        return x, bitbuf

    def decode(self, x, bitbuf, n_symbols):
        out = []
        bi = len(bitbuf) - 1
        for _ in range(n_symbols):
            slot = x % self.M
            s = int(np.searchsorted(self.cum, slot, side='right') - 1)
            # 限制到有效符号
            s = min(s, self.n_symbols - 1)
            out.append(s)
            x = (x // self.M) * int(self.freqs[s]) + (slot - int(self.cum[s]))
            # 反 renorm：x 太小则从流里吸收 16 bits
            while x < self.L and bi >= 0:
                x = (x << 16) | bitbuf[bi]
                bi -= 1
        return out


class InterleavedrANS:
    """
    8 状态 interleaved rANS —— AV1 实际形态。
    8 个独立 x 轮流编码 → 解码端 8 路并行（SIMD 一次处理 8 个）。
    """
    def __init__(self, freqs, prob_bits=14, n_lanes=8):
        self.lanes = [rANSCoder(freqs, prob_bits) for _ in range(n_lanes)]
        self.n_lanes = n_lanes

    def encode(self, symbols):
        n = len(symbols)
        # 分发：符号 i 给 lane (i % 8) —— 但各 lane 拿到的子序列要保持顺序
        xs, bufs = [], []
        for k in range(self.n_lanes):
            sub = symbols[k::self.n_lanes]     # interleaved 分发
            x, buf = self.lanes[k].encode(sub)
            xs.append(x); bufs.append((buf, len(sub)))
        return xs, bufs

    def decode(self, xs, bufs, n_total):
        sub_results = []
        for k in range(self.n_lanes):
            buf, n_sub = bufs[k]
            sub_results.append(self.lanes[k].decode(xs[k], buf, n_sub))
        # interleave 合并回来
        out = [0] * n_total
        for k in range(self.n_lanes):
            for i, v in enumerate(sub_results[k]):
                idx = i * self.n_lanes + k
                if idx < n_total:
                    out[idx] = v
        return out


def demo():
    print("=" * 62)
    print("论文级 rANS：AV1 同款熵编码器")
    print("=" * 62)

    # 模拟 DCT 系数符号分布：重尾（大量小值，少量大值）
    alphabet = 16
    freqs = np.array([5000, 2000, 1000, 600, 400, 250, 150, 100,
                      60, 40, 25, 15, 10, 6, 4, 2], dtype=np.float64)
    probs = freqs / freqs.sum()
    H = -np.sum(probs * np.log2(probs))

    np.random.seed(7)
    N = 20000
    symbols = np.random.choice(alphabet, size=N, p=probs).tolist()

    # --- 单状态 ---
    coder = rANSCoder(freqs)
    x, bitbuf = coder.encode(symbols)
    decoded = coder.decode(x, bitbuf, N)
    n_bits_single = 32 + 16 * len(bitbuf)   # 最终 x + 输出的 bits
    ok_single = decoded == symbols

    # --- 8 路 interleaved（AV1 形态）---
    ic = InterleavedrANS(freqs, n_lanes=8)
    xs, bufs = ic.encode(symbols)
    decoded_i = ic.decode(xs, bufs, N)
    n_bits_inter = 8 * 32 + 16 * sum(len(b[0]) for b in bufs)
    ok_inter = decoded_i == symbols

    print(f"\n符号数: {N}, 字母表: {alphabet}，分布重尾（模拟 DCT 系数）")
    print(f"理论熵: H = {H:.3f} bits/symbol → 熵极限 {int(H*N)} bits")
    print(f"\n[单状态 rANS]")
    print(f"  压缩后: {n_bits_single} bits ({n_bits_single/N:.3f} bits/sym)")
    print(f"  效率 vs 熵: {H*N/n_bits_single*100:.1f}%")
    print(f"  往返验证: {'✅' if ok_single else '❌'}")
    print(f"\n[8 路 interleaved rANS（AV1 形态）]")
    print(f"  压缩后: {n_bits_inter} bits ({n_bits_inter/N:.3f} bits/sym)")
    print(f"  效率 vs 熵: {H*N/n_bits_inter*100:.1f}%")
    print(f"  往返验证: {'✅' if ok_inter else '❌'}")

    print(f"\n与 CABAC 对比：")
    print(f"  CABAC (H.264/HEVC): 每 bit 串行决策，效率 ~99%（见 13_cabac_full.py）")
    print(f"  rANS (AV1):         效率 ~{H*N/n_bits_inter*100:.0f}%，但 8/64 路可并行")
    print(f"  → AV1 解码吞吐量比 CABAC 高 3-5×（关键工程权衡）")

    print(f"\n机制核心：")
    print(f"  编码: x' = (x // f[s])·M + cum[s] + (x mod f[s])")
    print(f"    ↑ 把符号 s'压进'整数 x 的数值结构里（Z → Z·M 的嵌入）")
    print(f"  解码: slot = x mod M → 查 cum 表 → 逆运算恢复 x")
    print(f"  renorm: x 超界时吐/吸 16 bits → x 永远 ~32-bit")


if __name__ == "__main__":
    demo()
