"""
Part IB Computer Vision (Cambridge CST)
=======================================
覆盖主题：
- 边缘检测（Sobel / Prewitt）
- 特征描述（HOG）
- 角点检测（Harris）
- 鲁棒估计（RANSAC）
- 光流（Lucas-Kanade）

核心教材：
- Forsyth & Ponce 2011 "Computer Vision: A Modern Approach" 2nd ed, Pearson
- Szeliski 2022 "Computer Vision: Algorithms and Applications" 2nd ed, Springer
- Trucco & Verri 1998 "Introductory Techniques for 3-D Computer Vision"

核心论文（真实引用）：
- Dalal & Triggs 2005 "Histograms of Oriented Gradients for Human Detection" CVPR
- Harris & Stephens 1988 "A Combined Corner and Edge Detector" Alvey Vision Conf
- Fischler & Bolles 1981 "Random Sample Consensus" CACM 24(6)
- Lucas & Kanade 1981 "An Iterative Image Registration Technique" IJCAI

本文件实现：
- Sobel 边缘检测
- HOG 描述子
- Harris 角点检测
- RANSAC 直线拟合
- Lucas-Kanade 光流（稀疏）

运行：
    python vision.py
"""
from __future__ import annotations
import math
import random


# ================================================================
# 图像工具（纯 list of list）
# ================================================================

def make_checkerboard(size=16, n=4):
    """生成棋盘格测试图像"""
    img = []
    for i in range(size):
        row = []
        for j in range(size):
            block = size // n
            row.append(200 if ((i // block) + (j // block)) % 2 == 0 else 50)
        img.append(row)
    return img


def make_gradient(size=16):
    """水平梯度图像"""
    return [[int(255 * j / size) for j in range(size)] for _ in range(size)]


def make_circle(size=16, r=5):
    """圆形图像"""
    cx, cy = size // 2, size // 2
    img = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if (i - cy)**2 + (j - cx)**2 <= r**2:
                img[i][j] = 200
    return img


# ================================================================
# 1. Sobel 边缘检测
# ================================================================

SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


def convolve(img, kernel):
    """3×3 卷积"""
    h, w = len(img), len(img[0])
    out = [[0] * w for _ in range(h)]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            val = 0
            for di in range(3):
                for dj in range(3):
                    val += img[i + di - 1][j + dj - 1] * kernel[di][dj]
            out[i][j] = val
    return out


def sobel_edge(img):
    """返回 (gradient_magnitude, gradient_angle)"""
    gx = convolve(img, SOBEL_X)
    gy = convolve(img, SOBEL_Y)
    h, w = len(img), len(img[0])
    mag = [[0] * w for _ in range(h)]
    angle = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            mag[i][j] = math.sqrt(gx[i][j]**2 + gy[i][j]**2)
            angle[i][j] = math.atan2(gy[i][j], gx[i][j])
    return mag, angle


# ================================================================
# 2. HOG (Histogram of Oriented Gradients)
# ================================================================

def hog_descriptor(img, cell_size=4, n_bins=9):
    """
    简化版 HOG:
    1. 计算梯度
    2. 分 cell，每个 cell 统计梯度方向直方图
    3. 拼接为特征向量
    """
    mag, angle = sobel_edge(img)
    h, w = len(img), len(img[0])
    cells_h = h // cell_size
    cells_w = w // cell_size
    descriptor = []
    for ci in range(cells_h):
        for cj in range(cells_w):
            hist = [0.0] * n_bins
            for di in range(cell_size):
                for dj in range(cell_size):
                    i = ci * cell_size + di
                    j = cj * cell_size + dj
                    if i < h and j < w:
                        # 角度 [−π,π] → [0,π)
                        a = angle[i][j] % math.pi
                        bidx = int(a / math.pi * n_bins) % n_bins
                        hist[bidx] += mag[i][j]
            # 归一化
            norm = math.sqrt(sum(x**2 for x in hist)) + 1e-6
            hist = [x / norm for x in hist]
            descriptor.extend(hist)
    return descriptor


# ================================================================
# 3. Harris 角点检测
# ================================================================

def harris_corners(img, threshold=1000, k=0.04):
    """
    Harris 角点响应: R = det(M) - k*trace(M)^2
    M = Σ [[Ix², IxIy],[IxIy, Iy²]]  (窗口内)
    """
    gx = convolve(img, SOBEL_X)
    gy = convolve(img, SOBEL_Y)
    h, w = len(img), len(img[0])
    Ix2 = [[gx[i][j]**2 for j in range(w)] for i in range(h)]
    Iy2 = [[gy[i][j]**2 for j in range(w)] for i in range(h)]
    IxIy = [[gx[i][j] * gy[i][j] for j in range(w)] for i in range(h)]

    corners = []
    window = 1  # 3×3 window
    for i in range(window, h - window):
        for j in range(window, w - window):
            Sxx = sum(Ix2[i+di][j+dj] for di in range(-window, window+1)
                      for dj in range(-window, window+1))
            Syy = sum(Iy2[i+di][j+dj] for di in range(-window, window+1)
                      for dj in range(-window, window+1))
            Sxy = sum(IxIy[i+di][j+dj] for di in range(-window, window+1)
                      for dj in range(-window, window+1))
            det = Sxx * Syy - Sxy**2
            trace = Sxx + Syy
            R = det - k * trace**2
            if R > threshold:
                corners.append((i, j, R))
    corners.sort(key=lambda x: -x[2])
    return corners


# ================================================================
# 4. RANSAC（直线拟合）
# ================================================================

def ransac_line(points, n_iter=100, threshold=2.0, min_inliers=5):
    """
    RANSAC 直线拟合:
    1. 随机采样 2 点
    2. 拟合直线
    3. 统计内点（距离 < threshold）
    4. 重复，返回内点最多的模型
    """
    random.seed(42)
    best_inliers = []
    best_line = None
    for _ in range(n_iter):
        if len(points) < 2:
            break
        p1, p2 = random.sample(points, 2)
        x1, y1 = p1
        x2, y2 = p2
        if x2 - x1 == 0:
            continue
        # y = a*x + b
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        # 计算内点
        inliers = []
        for px, py in points:
            # 点到直线距离
            dist = abs(a * px - py + b) / math.sqrt(a**2 + 1)
            if dist < threshold:
                inliers.append((px, py))
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
            best_line = (a, b)
    return best_line, best_inliers


# ================================================================
# 5. Lucas-Kanade 光流
# ================================================================

def lucas_kanade(img1, img2, points, window=2):
    """
    稀疏光流:
    Ix*Vx + Iy*Vy = -It  (亮度恒常假设)
    窗口内最小二乘求 Vx, Vy
    """
    gx = convolve(img1, SOBEL_X)
    gy = convolve(img1, SOBEL_Y)
    h, w = len(img1), len(img1[0])
    flows = []
    for py, px in points:
        if py < window or py >= h - window or px < window or px >= w - window:
            flows.append((py, px, 0, 0))
            continue
        A = []
        b_vec = []
        for di in range(-window, window + 1):
            for dj in range(-window, window + 1):
                i, j = py + di, px + dj
                It = float(img2[i][j] - img1[i][j])
                A.append([gx[i][j], gy[i][j]])
                b_vec.append(-It)
        # 最小二乘: V = (A^T A)^{-1} A^T b
        n = len(A)
        Sxx = sum(a[0]**2 for a in A)
        Syy = sum(a[1]**2 for a in A)
        Sxy = sum(a[0] * a[1] for a in A)
        Sxa = sum(A[i][0] * b_vec[i] for i in range(n))
        Sya = sum(A[i][1] * b_vec[i] for i in range(n))
        det = Sxx * Syy - Sxy**2
        if abs(det) < 1e-6:
            flows.append((py, px, 0, 0))
            continue
        vx = (Syy * Sxa - Sxy * Sya) / det
        vy = (Sxx * Sya - Sxy * Sxa) / det
        flows.append((py, px, vx, vy))
    return flows


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB Computer Vision — Demo")
    print("=" * 64)

    # 1. Sobel
    print("\n📋 1. Sobel 边缘检测（棋盘格）")
    img = make_checkerboard(16, 4)
    mag, ang = sobel_edge(img)
    # ASCII 可视化
    print("   原图 (8×8 采样):")
    for i in range(0, 16, 2):
        row = "   "
        for j in range(0, 16, 2):
            row += "░" if img[i][j] < 100 else "▓"
        print(row)
    print("   梯度幅值:")
    max_m = max(max(r) for r in mag)
    for i in range(0, 16, 2):
        row = "   "
        for j in range(0, 16, 2):
            row += " ·" if mag[i][j] < max_m * 0.3 else " █"
        print(row)
    print(f"   边缘像素数 (mag>50): {sum(1 for r in mag for v in r if v > 50)}")

    # 2. HOG
    print("\n📋 2. HOG 描述子")
    circle = make_circle(16, 5)
    desc = hog_descriptor(circle, cell_size=4, n_bins=9)
    print(f"   圆形图像 HOG: {len(desc)} 维 ({4}cells × {9}bins)")
    # 可视化前 2 cell 的方向分布
    for c in range(2):
        cell_hist = desc[c*9:(c+1)*9]
        bar = ""
        for v in cell_hist:
            bar += "█" * int(v * 40)
        print(f"   Cell {c} HOG: |{bar}")

    # 3. Harris
    print("\n📋 3. Harris 角点检测")
    corners = harris_corners(circle, threshold=500)
    print(f"   圆形图像检测到 {len(corners)} 个角点")
    for c in corners[:5]:
        print(f"     ({c[0]}, {c[1]}) R={c[2]:.0f}")

    # 4. RANSAC
    print("\n📋 4. RANSAC 直线拟合（含离群点）")
    # 生成 y = 2x + 1 + noise 的内点 + 随机离群点
    random.seed(42)
    inlier_pts = [(x, 2*x + 1 + random.gauss(0, 0.5)) for x in range(20)]
    outlier_pts = [(random.randint(0, 25), random.randint(0, 60)) for _ in range(15)]
    all_pts = inlier_pts + outlier_pts
    line, inliers = ransac_line(all_pts, n_iter=200, threshold=2.0)
    print(f"   总点数: {len(all_pts)} ({len(inlier_pts)} 内点 + {len(outlier_pts)} 离群)")
    print(f"   真实直线: y = 2x + 1")
    print(f"   RANSAC:  y = {line[0]:.2f}x + {line[1]:.2f}, {len(inliers)} 内点")
    print(f"   RANSAC 正确拒绝 {len(all_pts) - len(inliers)} 个离群点")

    # 5. Lucas-Kanade
    print("\n📋 5. Lucas-Kanade 光流")
    img1 = make_gradient(16)
    # img2 = img1 整体右移 1 像素
    img2 = [[img1[i][(j-1) % 16] if j > 0 else img1[i][0]
             for j in range(16)] for i in range(16)]
    pts = [(8, 4), (8, 8), (8, 12)]
    flows = lucas_kanade(img1, img2, pts, window=2)
    print(f"   图像右移 1 像素，追踪 {len(pts)} 个点:")
    for py, px, vx, vy in flows:
        arrow = "→" * max(1, int(abs(vx))) if vx > 0.1 else "·"
        print(f"     ({py},{px}): V=({vx:.2f}, {vy:.2f}) {arrow}")

    print("\n✅ Computer Vision 完成！")
    print("\n💡 反直觉发现：")
    print("   - Harris R = det(M) - k·trace(M)²: 角点是两个方向都有大梯度")
    print("   - RANSAC 用最少样本(2点)反而最鲁棒（离群率 50% 也能拟合）")
    print("   - Lucas-Kanade 假设「亮度恒常」→ 大位移会失败（需金字塔）")


if __name__ == "__main__":
    demo()
