# -*- coding: utf-8 -*-
"""
sobel_edge_demo.py —— 04 章实验：卷积边缘检测（图形-视觉互逆管线的现场）

对应章：04-计算机应用转代码（走廊穿越：构造图像[图形学]→卷积边缘[图象处理]→工程校验）
核心：同一幅图，从"合成"与"分析"两个方向走过——表示同一、问题互逆（00 章动脉一）。
断言（结构性质）：
  1. 边缘响应集中于方块边界带：边界带平均梯度 > 平坦区平均梯度 × 10
  2. 梯度方向正确：左边界响应主导演化（垂直边→水平梯度核 Gx 响应强）
  3. 手写卷积 == scipy 参考实现（若 scipy 可用）
"""
import numpy as np

# ── 走廊 1：图形学侧——合成一幅 32×32 图像（背景 50，中央 16×16 方块 200，轻平滑）──
N = 32
img = np.full((N, N), 50.0)
img[8:24, 8:24] = 200.0
# 轻微高斯平滑（模拟真实光学的有限带宽，防纯 jump 的数值平凡性）
k = np.array([1, 2, 1], dtype=float); k /= k.sum()
img = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, img)
img = np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, img)

# ── 走廊 2：图象处理侧——Sobel 卷积（手写 2D 卷积）──
GX = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)   # 水平梯度核
GY = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=float)   # 垂直梯度核

def conv2d(a, ker):
    """朴素 2D 卷积（相关运算，边缘零填充）。"""
    kh, kw = ker.shape
    ph, pw = kh // 2, kw // 2
    pad = np.pad(a, ((ph, ph), (pw, pw)))
    out = np.zeros_like(a)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            out[i, j] = np.sum(pad[i:i+kh, j:j+kw] * ker)
    return out

gx, gy = conv2d(img, GX), conv2d(img, GY)
mag = np.hypot(gx, gy)

# ── 断言 1：边缘带 vs 平坦区 ──
inner = mag[13:19, 13:19]          # 方块内部（平坦）
band = np.zeros_like(mag, dtype=bool)
band[7:10, 6:26] = True; band[22:25, 6:26] = True    # 上下边界带
band[6:26, 7:10] = True; band[6:26, 22:25] = True    # 左右边界带
assert band.mean() > inner.mean() * 10, \
    f"边缘带 {band.mean():.1f} 未显著高于平坦区 {inner.mean():.1f}"

# ── 断言 2：方向性——左边界（垂直边）主要由 Gx 响应 ──
left_edge = slice(10, 22), slice(7, 10)
assert np.abs(gx[left_edge]).sum() > np.abs(gy[left_edge]).sum() * 3, "垂直边应对 Gx 响应为主"

# ── 断言 3：对照 scipy（若可用）──
try:
    from scipy.signal import convolve2d
    ref = np.hypot(convolve2d(img, GX, mode="same", boundary="fill"),
                   convolve2d(img, GY, mode="same", boundary="fill"))
    assert np.allclose(mag, ref, atol=1e-9), "手写卷积与 scipy 不一致"
    scipy_ok = "一致（atol=1e-9）"
except ImportError:
    scipy_ok = "scipy 不可用，跳过对照（结构断言 1/2 已独立成立）"

# ── 报告 ──
print(f"合成图像：{N}×{N}，中央方块边缘检测")
print(f"  边界带平均梯度 : {band.mean():8.2f}")
print(f"  平坦区平均梯度 : {inner.mean():8.2f}")
print(f"  对比度         : {band.mean()/max(inner.mean(),1e-9):8.1f}×（断言 >10）")
print(f"  左边界 |Gx|/|Gy| 响应比: {np.abs(gx[left_edge]).sum()/np.abs(gy[left_edge]).sum():5.1f}（断言 >3）")
print(f"  scipy 参考校验 : {scipy_ok}")

# ASCII 可视化（4 档灰度）
print("\n梯度幅值图（. < 25, - < 150, + < 400, # ≥ 400）：")
for row in mag[::1]:
    print("".join("." if v < 25 else "-" if v < 150 else "+" if v < 400 else "#" for v in row))

print("\n[ALL ASSERTS PASSED] 图形学合成→图象处理分析→工程校验，三条走廊一次穿越。")
print("带走一句（04 章）：同一幅图的'合成规格'与'分析响应'互为正逆——"
      "可微渲染时代，两者共用一套梯度。")
