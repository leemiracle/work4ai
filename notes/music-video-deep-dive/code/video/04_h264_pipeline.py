"""
04_h264_pipeline.py
===================
H.264/AVC 完整编码 pipeline 的简化实现（教学版）。

完整流程：
  帧 → 切宏块 → 帧类型 (I/P/B) → 预测 (帧内/帧间) → DCT → 量化 → 熵编码 (CABAC) → 码流

本文件实现端到端的简化版本，演示每一步的角色。
"""
import numpy as np


# 1. 切宏块
def split_macroblocks(frame, mb_size=16):
    H, W = frame.shape
    nH, nW = H // mb_size, W // mb_size
    blocks = frame[:nH * mb_size, :nW * mb_size].reshape(nH, mb_size, nW, mb_size).swapaxes(1, 2)
    return blocks  # [nH, nW, mb, mb]


# 2. 帧内预测（Intra Prediction）：H.264 有 9 种 4×4 模式 + 4 种 16×16 模式
def intra_predict_dc(block):
    """最简单的 DC 预测：用左/上邻居均值预测"""
    # 教学：直接用块均值预测（实际 H.264 用相邻像素）
    pred = np.full_like(block, np.mean(block))
    return pred


def intra_predict_vertical(block, top_row):
    """垂直预测：用上方一行复制"""
    pred = np.tile(top_row, (block.shape[0], 1))
    return pred


# 3. DCT (整数近似，H.264 用 4×4)
def dct4x4_int(block):
    """H.264 整数 DCT 4×4（避免浮点误差）。
    核心：Y = Cf * X * Cf^T，然后右移。
    教学版直接用 float DCT。"""
    M = dct_matrix(4)
    return M @ block @ M.T


def dct_matrix(N=4):
    M = np.zeros((N, N))
    for k in range(N):
        for n in range(N):
            M[k, n] = np.cos(np.pi * (2 * n + 1) * k / (2 * N))
    M *= np.sqrt(2 / N); M[0, :] *= 1 / np.sqrt(2)
    return M


# 4. 量化
def quantize(coeffs, QP=20):
    """标量量化。QP 越大质量越差。"""
    scale = (QP + 1) * 1.5
    return np.round(coeffs / scale).astype(np.int32)


def dequantize(qcoeffs, QP=20):
    scale = (QP + 1) * 1.5
    return qcoeffs * scale


# 5. 熵编码（教学：用简单的 RLE + 类 Huffman）
def rle_encode(arr):
    """行程编码：把长串 0 压成 (run, value)"""
    flat = arr.flatten()
    result = []
    run = 0
    for v in flat:
        if v == 0:
            run += 1
        else:
            result.append((run, int(v)))
            run = 0
    if run: result.append((run, 0))
    return result


# 6. 运动估计（简化版，复用 02_motion_estimation 的思路）
def motion_estimate_block(cur, ref, by, bx, bs=16, sr=8):
    best_cost = float('inf'); best_mv = (0, 0)
    cb = cur[by:by+bs, bx:bx+bs]
    for dy in range(-sr, sr+1):
        for dx in range(-sr, sr+1):
            ry, rx = by+dy, bx+dx
            if ry<0 or rx<0 or ry+bs>cur.shape[0] or rx+bs>cur.shape[1]: continue
            cost = np.sum(np.abs(cb.astype(int) - ref[ry:ry+bs, rx:rx+bs].astype(int)))
            if cost < best_cost:
                best_cost = cost; best_mv = (dy, dx)
    return best_mv


def encode_frame(cur, ref=None, mb_size=16, qp=20, is_intra=True):
    """编码一帧：返回 (mv_map, residuals, n_bits_estimate)"""
    H, W = cur.shape
    mv_map = []
    residuals = []
    total_bits = 0
    for by in range(0, H - mb_size + 1, mb_size):
        for bx in range(0, W - mb_size + 1, mb_size):
            cur_mb = cur[by:by+mb_size, bx:bx+mb_size].astype(np.int32)
            if is_intra or ref is None:
                # 帧内预测：DC
                pred = np.full_like(cur_mb, cur_mb.mean())
                mv = (0, 0)
            else:
                # 帧间：运动估计
                mv = motion_estimate_block(cur, ref, by, bx, mb_size)
                ry, rx = by+mv[0], bx+mv[1]
                pred = ref[ry:ry+mb_size, rx:rx+mb_size].astype(np.int32)
            residual = cur_mb - pred
            # 4×4 DCT + 量化
            qres = np.zeros_like(residual)
            for iy in range(0, mb_size, 4):
                for ix in range(0, mb_size, 4):
                    blk = residual[iy:iy+4, ix:ix+4]
                    C = dct4x4_int(blk)
                    q = quantize(C, qp)
                    qres[iy:iy+4, ix:ix+4] = q
            # 估算 bits（RLE 后的长度）
            rle = rle_encode(qres)
            bits = len(rle) * 8 + 8  # 粗略
            mv_map.append((by, bx, mv))
            residuals.append(qres)
            total_bits += bits
    return mv_map, residuals, total_bits


if __name__ == "__main__":
    np.random.seed(0)
    H, W = 64, 64
    # 帧 1（随机纹理 + 平滑区域）
    ref = (np.random.rand(H, W) * 200 + 30).astype(np.uint8)
    # 帧 2 = 帧 1 整体平移 (3, -2) + 噪声
    cur = np.zeros_like(ref)
    cur[3:, :W-2] = ref[:-3, 2:]
    cur = np.clip(cur.astype(int) + np.random.randint(-3, 3, cur.shape), 0, 255).astype(np.uint8)

    print("=" * 60)
    print("H.264 简化 pipeline 演示（64×64 帧）")
    print("=" * 60)

    # I 帧（帧内编码）
    mv_i, res_i, bits_i = encode_frame(ref, is_intra=True, qp=20)
    print(f"\n[I 帧] 帧内预测 + DCT + 量化")
    print(f"  宏块数: {len(mv_i)}")
    print(f"  估计码率: {bits_i} bits = {bits_i/8} bytes")

    # P 帧（帧间编码）
    mv_p, res_p, bits_p = encode_frame(cur, ref=ref, is_intra=False, qp=20)
    print(f"\n[P 帧] 运动估计 + 残差 DCT")
    print(f"  宏块数: {len(mv_p)}")
    print(f"  估计码率: {bits_p} bits = {bits_p/8} bytes")
    print(f"  节省: {(1 - bits_p/bits_i)*100:.0f}%  ← 这就是 P 帧的核心价值")

    # 显示前几个宏块的 MV
    print(f"\n  前 8 个宏块的运动矢量（真值应为 dy=3, dx=-2）：")
    for by, bx, mv in mv_p[:8]:
        print(f"    ({by:>2},{bx:>2}) MV = {mv}")

    print("\n" + "=" * 60)
    print("完整 H.264 还包含（教学简化省略）：")
    print("  - 9 种 4×4 帧内预测模式（不只 DC）")
    print("  - 1/4 像素亚像素运动估计（需双线性/Wiener 插值）")
    print("  - 多参考帧（最多 16 个）")
    print("  - CABAC 上下文自适应二进制算术编码")
    print("  - 环路去块滤波（deblocking filter）")
    print("  - B 帧（双向预测，需 reordering）")
    print("=" * 60)
