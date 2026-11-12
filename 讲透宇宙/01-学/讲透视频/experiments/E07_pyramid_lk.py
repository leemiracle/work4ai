"""
E07 解答 · 金字塔 Lucas-Kanade: 修复大位移低估
================================================
实验 05 中单层 LK 低估大位移(一阶泰勒仅小位移成立)。
金字塔 LK: 先在最粗层估大位移(等效小位移化), 逐层×2 细化。

要点: 位移取 2 的幂 (8,4), 使各层下采样后恰为整数位移, 避免混叠。

运行: python3 E07_pyramid_lk.py    # 约 4 秒
输出: E07_pyramid_lk.png
"""
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def make_frame(shape, cx, cy, r=6):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    return (((xx - cx) ** 2 + (yy - cy) ** 2) < r ** 2).astype(np.float32)


def shift(img, dx, dy):
    """整数位移(保证金字塔各层一致)。"""
    out = np.zeros_like(img)
    H, W = img.shape
    for i in range(H):
        for j in range(W):
            ni, nj = i - int(round(dy)), j - int(round(dx))
            if 0 <= ni < H and 0 <= nj < W:
                out[i, j] = img[ni, nj]
    return out


def bilinear_sample(img, fi, fj):
    """双线性插值采样(比最近邻平滑, Gauss-Newton 才能收敛)。"""
    H, W = img.shape
    i0, j0 = int(np.floor(fi)), int(np.floor(fj))
    di, dj = fi - i0, fj - j0
    val = 0.0
    for wi, (ii, wc) in enumerate([(i0, 1 - di), (i0 + 1, di)]):
        for wj, (jj, wr) in enumerate([(j0, 1 - dj), (j0 + 1, dj)]):
            if 0 <= ii < H and 0 <= jj < W:
                val += img[ii, jj] * wc * wr
    return val


def lk_single(I1, I2, d0, center, window=11, iters=20):
    """在 I1/I2 上以 center 为窗口中心迭代 LK, 初值 d0。双线性 warp。"""
    H, W = I1.shape
    d = np.array(d0, dtype=np.float64)
    Iy, Ix = np.gradient(I1)
    ci, cj = center
    half = window // 2
    r0, r1 = max(0, ci - half), min(H, ci + half + 1)
    c0, c1 = max(0, cj - half), min(W, cj + half + 1)
    sel = np.zeros((H, W), bool); sel[r0:r1, c0:c1] = True
    A = np.stack([Ix[sel], Iy[sel]], 1)
    ATA = A.T @ A
    for _ in range(iters):
        warp = np.zeros_like(I1)
        for i in range(H):
            for j in range(W):
                warp[i, j] = bilinear_sample(I1, i - d[1], j - d[0])
        It = (I2 - warp)[sel]
        if np.linalg.cond(ATA) < 1 / 1e-9:
            dd = np.linalg.lstsq(ATA, A.T @ (-It), rcond=None)[0]
            d = d + dd
    return d


def pyramid_lk(I1, I2, q_center, levels=3):
    """q_center: 目标(I2 中圆盘)中心坐标(原分辨率)。coarse→fine, 每层 d×2。"""
    pyr1, pyr2 = [I1], [I2]
    for _ in range(levels - 1):
        pyr1.insert(0, pyr1[0][::2, ::2])
        pyr2.insert(0, pyr2[0][::2, ::2])
    d = np.array([0.0, 0.0])
    for l in range(len(pyr1)):
        scale = 2 ** l  # 本层分辨率 = 原始 / 2^(levels-1-l) → 中心除以 2^(levels-1-l)
        s = 2 ** (levels - 1 - l)
        cen = (q_center[0] // s, q_center[1] // s)
        d = d * 2  # 上采样到本层尺度
        d = lk_single(pyr1[l], pyr2[l], d0=d, center=cen)
        print(f"  level{l} ({pyr1[l].shape[0]}×{pyr1[l].shape[1]}, 中心{cen}): d={d.round(2)}")
    return d


# ---------- 大位移 (8,4): 2 的幂, 各层整数 ----------
true_dx, true_dy = 8.0, 4.0
I1 = make_frame((64, 64), 32, 32)
I2 = shift(I1, true_dx, true_dy)          # 圆盘 → (40,36)

print(f"[真值] 位移 = ({true_dx}, {true_dy})")
d_single = lk_single(I1, I2, d0=(0, 0), center=(40, 36))
print(f"[单层 LK]  = ({d_single[0]:.2f}, {d_single[1]:.2f})  ← 大位移下严重低估")
print("[金字塔 LK]")
d_pyr = pyramid_lk(I1, I2, q_center=(40, 36), levels=3)
print(f"[金字塔]    = ({d_pyr[0]:.2f}, {d_pyr[1]:.2f})")

fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
axes[0].imshow(I1, cmap='gray'); axes[0].set_title('I₁ (圆盘@中心)'); axes[0].axis('off')
axes[1].imshow(I2, cmap='gray'); axes[1].set_title(f'I₂ (平移 {true_dx},{true_dy})'); axes[1].axis('off')
ax = axes[2]
ax.bar(['单层LK', '金字塔LK', '真值'],
       [np.hypot(*d_single), np.hypot(*d_pyr), np.hypot(true_dx, true_dy)],
       color=['#c66', '#4c9', '#369'])
ax.axhline(np.hypot(true_dx, true_dy), ls='--', c='k', lw=1)
ax.set_ylabel('位移模长 |d|')
ax.set_title(f'{np.hypot(*d_single):.1f} vs {np.hypot(*d_pyr):.1f} vs 真值 {np.hypot(true_dx, true_dy):.1f}', fontsize=10)
plt.suptitle('E07 · 金字塔 LK: 把"大位移"分解成逐层"小位移"', fontweight='bold')
plt.tight_layout(); plt.savefig('E07_pyramid_lk.png', dpi=110, bbox_inches='tight')
print("\n[输出] E07_pyramid_lk.png")
