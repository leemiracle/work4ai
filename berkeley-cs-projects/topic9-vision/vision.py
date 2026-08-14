"""
CS 280 Computer Vision — UC Berkeley (Malik/Efros)
================================================
覆盖主题：
- 边缘检测：Sobel / Canny（Lec 3-4）
- 特征描述：HOG（Lec 6）
- RANSAC + 单应性矩阵（Lec 8-9）
- 图像分割：k-means（Lec 10-11）
- CNN 前向传播（Lec 14-16）

核心教材/参考：
- Szeliski "Computer Vision: Algorithms and Applications" 2nd ed (Springer 2022), Ch 4-5
- Dalal & Triggs "Histograms of Oriented Gradients for Human Detection" CVPR 2005
- Fischler & Bolles "Random Sample Consensus" Communications of the ACM 24(6) (1981)
- Lowe "Distinctive Image Features from Scale-Invariant Keypoints" IJCV 60(2) (2004)

本文件实现：
- Sobel 边缘 + Canny（非极大值抑制）
- HOG 描述子
- RANSAC 单应性估计
- k-means 分割
- CNN 前向（conv + pool + FC，纯 Python）

运行：
    python vision.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ============================================================
# 0. 图像 = 2D list of [0,255]
# ============================================================

def make_synthetic_image(h=16, w=16):
    """生成含方形 + 圆形的合成图"""
    img = [[100] * w for _ in range(h)]
    # 方形 [4:8, 4:8] = 白
    for r in range(4, 8):
        for c in range(4, 8):
            img[r][c] = 200
    # 圆形中心 (10, 11)，半径 2
    for r in range(h):
        for c in range(w):
            if (r - 10) ** 2 + (c - 11) ** 2 <= 4:
                img[r][c] = 180
    return img


# ============================================================
# 1. Sobel + Canny（Szeliski §4.2）
# ============================================================

def sobel_edges(img):
    """
    Sobel 算子：
        Gx = [[-1,0,1],[-2,0,2],[-1,0,1]]  水平梯度
        Gy = [[-1,-2,-1],[0,0,0],[1,2,1]]  垂直梯度
    梯度幅值 = sqrt(Gx² + Gy²)
    """
    h, w = len(img), len(img[0])
    Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    grad = [[0.0] * w for _ in range(h)]
    angle = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            gx = sum(Gx[i][j] * img[r+i-1][c+j-1] for i in range(3) for j in range(3))
            gy = sum(Gy[i][j] * img[r+i-1][c+j-1] for i in range(3) for j in range(3))
            grad[r][c] = math.sqrt(gx * gx + gy * gy)
            angle[r][c] = math.atan2(gy, gx)
    return grad, angle


def canny_edges(img, low=None, high=None):
    """Canny: Sobel → 非极大值抑制 → 双阈值（自适应 = max 梯度 × 10%/30%）"""
    grad, angle = sobel_edges(img)
    h, w = len(img), len(img[0])
    max_grad = max(max(row) for row in grad)
    if low is None:
        low = 0.1 * max_grad
    if high is None:
        high = 0.3 * max_grad
    # 非极大值抑制（沿梯度方向只保留局部最大）
    nms = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            ang = angle[r][c] * 180 / math.pi
            if ang < 0:
                ang += 180
            # 量化到 4 方向
            if (0 <= ang < 22.5) or (157.5 <= ang <= 180):
                n1, n2 = grad[r][c-1], grad[r][c+1]
            elif 22.5 <= ang < 67.5:
                n1, n2 = grad[r-1][c+1], grad[r+1][c-1]
            elif 67.5 <= ang < 112.5:
                n1, n2 = grad[r-1][c], grad[r+1][c]
            else:
                n1, n2 = grad[r-1][c-1], grad[r+1][c+1]
            if grad[r][c] >= n1 and grad[r][c] >= n2:
                nms[r][c] = grad[r][c]
    # 双阈值
    edges = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if nms[r][c] >= high:
                edges[r][c] = 255  # strong
            elif nms[r][c] >= low:
                edges[r][c] = 128  # weak
    return edges, grad


# ============================================================
# 2. HOG 描述子（Dalal & Triggs 2005）
# ============================================================

def hog_descriptor(img, cell_size=4, n_bins=9):
    """
    HOG（Histogram of Oriented Gradients）：
    1. 计算每像素梯度幅值+方向
    2. 在 cell 内统计方向直方图（n_bins）
    3. block normalization（L2）
    """
    grad, angle = sobel_edges(img)
    h, w = len(img), len(img[0])
    # 每 cell 统计方向直方图
    cells_h = h // cell_size
    cells_w = w // cell_size
    hist = [[[0.0] * n_bins for _ in range(cells_w)] for _ in range(cells_h)]
    for ci in range(cells_h):
        for cj in range(cells_w):
            for di in range(cell_size):
                for dj in range(cell_size):
                    r = ci * cell_size + di
                    c = cj * cell_size + dj
                    if 0 <= r < h and 0 <= c < w:
                        a = angle[r][c] % math.pi  # 0..π
                        mag = grad[r][c]
                        b = int(a / math.pi * n_bins) % n_bins
                        hist[ci][cj][b] += mag
    # Block normalization (2x2 cells)
    descriptor = []
    for ci in range(cells_h - 1):
        for cj in range(cells_w - 1):
            block = []
            for di in range(2):
                for dj in range(2):
                    block.extend(hist[ci+di][cj+dj])
            norm = math.sqrt(sum(x * x for x in block) + 1e-6)
            block = [x / norm for x in block]
            descriptor.extend(block)
    return descriptor


# ============================================================
# 3. RANSAC 单应性（Fischler & Bolles 1981）
# ============================================================

def ransac_line(points, n_iters=100, threshold=1.0):
    """
    RANSAC 拟合 2D 直线（简化单应性的演示）：
    1. 随机选 2 点拟直线
    2. 统计 inlier（距离 < threshold）
    3. 用所有 inlier 重拟合
    """
    if len(points) < 2:
        return None, []
    best_inliers = []
    best_line = None
    for _ in range(n_iters):
        p1, p2 = random.sample(points, 2)
        if p1 == p2:
            continue
        # 直线 ax + by + c = 0
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = p2[0] * p1[1] - p1[0] * p2[1]
        norm = math.sqrt(a * a + b * b)
        if norm < 1e-10:
            continue
        inliers = []
        for p in points:
            dist = abs(a * p[0] + b * p[1] + c) / norm
            if dist < threshold:
                inliers.append(p)
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
            best_line = (a, b, c)
    # 用所有 inlier 重拟合（least-squares）—— docstring 承诺的步骤
    if best_inliers and len(best_inliers) >= 2:
        xs = [p[0] for p in best_inliers]
        ys = [p[1] for p in best_inliers]
        nn = len(xs)
        sx, sy = sum(xs), sum(ys)
        sxx = sum(x * x for x in xs)
        sxy = sum(x * y for x, y in zip(xs, ys))
        denom = nn * sxx - sx * sx
        if abs(denom) > 1e-10:
            slope = (nn * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / nn
            # y = slope*x + intercept  →  slope*x - y + intercept = 0
            best_line = (slope, -1.0, intercept)
    return best_line, best_inliers


# ============================================================
# 4. K-means 分割（MacQueen 1967）
# ============================================================

def kmeans_1d(data, k=3, n_iters=20):
    """1D k-means（用于灰度图分割），k-means++ 初始化（避免重复中心）"""
    # k-means++ 初始化：按距离平方权重采样初始中心
    centers = [random.choice(data)]
    for _ in range(1, k):
        dists = [min((x - c) ** 2 for c in centers) for x in data]
        total = sum(dists)
        if total < 1e-10:
            centers.append(random.choice(data))
        else:
            r = random.random() * total
            cum = 0.0
            chosen = None
            for x, d in zip(data, dists):
                cum += d
                if cum >= r:
                    chosen = x
                    break
            centers.append(chosen if chosen is not None else random.choice(data))
    centers = sorted(centers)
    for _ in range(n_iters):
        clusters = defaultdict(list)
        for x in data:
            best = min(range(k), key=lambda i: abs(x - centers[i]))
            clusters[best].append(x)
        new_centers = []
        for i in range(k):
            if clusters[i]:
                new_centers.append(sum(clusters[i]) / len(clusters[i]))
            else:
                new_centers.append(centers[i])
        if new_centers == centers:
            break
        centers = new_centers
    return centers, dict(clusters)


# ============================================================
# 5. CNN 前向传播（纯 Python）
# ============================================================

def conv2d(img, kernel):
    """2D 卷积（无 padding，stride=1）"""
    h, w = len(img), len(img[0])
    kh, kw = len(kernel), len(kernel[0])
    out_h, out_w = h - kh + 1, w - kw + 1
    out = [[0.0] * out_w for _ in range(out_h)]
    for r in range(out_h):
        for c in range(out_w):
            s = 0.0
            for ki in range(kh):
                for kj in range(kw):
                    s += img[r+ki][c+kj] * kernel[ki][kj]
            out[r][c] = s
    return out


def relu2d(feature_map):
    return [[max(0.0, v) for v in row] for row in feature_map]


def maxpool2d(feature_map, pool_size=2):
    """最大池化"""
    h, w = len(feature_map), len(feature_map[0])
    out_h, out_w = h // pool_size, w // pool_size
    out = [[0.0] * out_w for _ in range(out_h)]
    for r in range(out_h):
        for c in range(out_w):
            vals = []
            for pi in range(pool_size):
                for pj in range(pool_size):
                    vals.append(feature_map[r*pool_size+pi][c*pool_size+pj])
            out[r][c] = max(vals)
    return out


def cnn_forward(img, kernels, fc_weights):
    """
    简化 CNN 前向：Conv → ReLU → Pool → FC
    kernels: list of 3x3 kernels
    fc_weights: dict {(flatten_idx): [logits]}
    """
    # Conv1 → ReLU → Pool
    features = []
    for k in kernels:
        conv = conv2d(img, k)
        relu = relu2d(conv)
        pooled = maxpool2d(relu, pool_size=2)
        # flatten
        flat = [v for row in pooled for v in row]
        features.append(flat)
    # Concat all feature maps
    concat = []
    for f in features:
        concat.extend(f)
    # FC
    n_classes = len(next(iter(fc_weights.values())))
    logits = [0.0] * n_classes
    for i, val in enumerate(concat):
        if i in fc_weights:
            for j in range(n_classes):
                logits[j] += val * fc_weights[i][j]
    return logits, features


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 280 Computer Vision Demo")
    print("=" * 60)
    random.seed(42)

    img = make_synthetic_image(16, 16)
    print(f"   合成图 16×16（方形+圆形）")

    # 1. Sobel + Canny
    print("\n📋 1. Sobel 边缘检测")
    grad, _ = sobel_edges(img)
    # 显示梯度幅值 ASCII
    max_g = max(max(row) for row in grad)
    print("   梯度图（# = 强边缘）:")
    for r in range(0, 16, 2):
        line = ""
        for c in range(0, 16, 2):
            v = grad[r][c] / max_g if max_g > 0 else 0
            line += "#" if v > 0.5 else ("+" if v > 0.2 else ".")
        print(f"   {line}")

    print("\n📋 2. Canny（双阈值 + NMS, 自适应阈值）")
    low_thr = 0.1 * max_g
    high_thr = 0.3 * max_g
    edges, _ = canny_edges(img, low=low_thr, high=high_thr)
    n_strong = sum(row.count(255) for row in edges)
    n_weak = sum(row.count(128) for row in edges)
    print(f"   自适应阈值: low={low_thr:.1f}, high={high_thr:.1f} (max_grad={max_g:.1f})")
    print(f"   strong edges (≥{high_thr:.0f}): {n_strong}, weak ({low_thr:.0f}-{high_thr:.0f}): {n_weak}")

    # 2. HOG
    print("\n📋 3. HOG 描述子")
    desc = hog_descriptor(img, cell_size=4, n_bins=9)
    print(f"   描述子维度: {len(desc)}")
    print(f"   前 10 值: {[f'{x:.3f}' for x in desc[:10]]}")
    print(f"   L2 norm: {math.sqrt(sum(x*x for x in desc)):.3f}（归一化后≈每 block=1）")

    # 3. RANSAC
    print("\n📋 4. RANSAC 直线拟合（含离群点）")
    # 在线 y=2x+1 加噪声 + 离群
    true_line_points = [(x, 2*x + 1 + random.gauss(0, 0.1)) for x in range(20)]
    outliers = [(random.uniform(0, 20), random.uniform(0, 50)) for _ in range(15)]
    all_pts = true_line_points + outliers
    random.shuffle(all_pts)
    line, inliers = ransac_line(all_pts, n_iters=200, threshold=0.5)
    print(f"   总点数: {len(all_pts)}（20 inlier + 15 outlier）")
    print(f"   RANSAC 找到 {len(inliers)} 个 inlier")
    if line:
        a, b, c = line
        # 转换 y = mx + k 形式
        if b != 0:
            slope = -a / b
            intercept = -c / b
            print(f"   拟合直线: y = {slope:.2f}x + {intercept:.2f}  (真值 y=2x+1)")

    # 4. K-means 分割
    print("\n📋 5. K-means 图像分割")
    pixels = [img[r][c] for r in range(16) for c in range(16)]
    centers, clusters = kmeans_1d(pixels, k=3, n_iters=20)
    print(f"   聚类中心: {[round(c) for c in centers]}")
    print(f"   各簇大小: {[len(v) for v in clusters.values()]}")
    print(f"   （背景100, 圆180, 方200 → 3 个簇）")

    # 5. CNN forward
    print("\n📋 6. CNN 前向（Conv→ReLU→Pool→FC）")
    random.seed(0)
    kernel1 = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(3)]  # 边缘检测器
    kernel2 = [[random.gauss(0, 0.5) for _ in range(3)] for _ in range(3)]
    fc_w = {i: [random.gauss(0, 0.1) for _ in range(3)] for i in range(49 * 2)}  # 简化
    logits, features = cnn_forward(img, [kernel1, kernel2], fc_w)
    print(f"   输入: 16×16")
    print(f"   Conv (3×3): {len(features)} 个 feature map")
    print(f"   每个 feature map pool 后大小: {len(features[0])} 像素")
    print(f"   FC 输出 logits: {[f'{l:.2f}' for l in logits]}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   RANSAC 在 42.9% 离群率（15/35）下仍能精确找到直线！")
    print("   传统最小二乘会被离群点严重拉偏，但 RANSAC")
    print("   通过'投票'机制（最多 inlier 的模型胜出）天然抗离群。")
    print("   理论：只要采样至少一次纯 inlier 集合（概率=p^n），")
    print("   n=2（直线）、p=0.57 → 单次概率 32%，200 次几乎必然命中。")
    print()
    print("   Sobel 3×3 卷积核能'发现'图像中的边缘，")
    print("   因为它本质是一阶差分近似（中心差分）。")
    print("   CNN 把这种手工核替换为可学习的卷积核，")
    print("   让网络自己学出最优的'特征探测器'。")


if __name__ == "__main__":
    demo()
