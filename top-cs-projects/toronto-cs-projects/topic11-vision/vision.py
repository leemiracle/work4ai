"""
CSC 420 Introduction to Computer Vision (University of Toronto)
================================================================
覆盖主题：
- 高斯/Sobel 滤波（边缘检测基础）
- Canny 边缘检测（多步管线）
- SIFT-like DoG（尺度不变特征）
- RANSAC 单应性估计
- FCN 语义分割（可训练全卷积网络）

核心论文/教材：
- Szeliski "Computer Vision: Algorithms and Applications" (2nd ed.)
- Lowe "Distinctive Image Features from Scale-Invariant Keypoints" IJCV, 2004
- Fischler & Bolles "Random Sample Consensus" CACM, 1981
- Long, Shelhamer, Darrell "Fully Convolutional Networks" CVPR 2015

本文件实现（纯 numpy + ASCII 可视化）：
- 高斯模糊 + Sobel 梯度
- Canny 边缘检测（NMS + 双阈值）
- DoG（Difference of Gaussians）关键点检测
- RANSAC 单应性矩阵估计
- FCN（全卷积网络：conv → ReLU → conv → sigmoid，含训练循环）

运行：
    python vision.py
"""
from __future__ import annotations
import numpy as np
import math
import random


# ============ 1. Gaussian & Sobel Filter ============

def gaussian_kernel(size=5, sigma=1.0):
    """生成高斯卷积核"""
    kernel = np.zeros((size, size))
    center = size // 2
    for i in range(size):
        for j in range(size):
            kernel[i, j] = math.exp(-((i - center) ** 2 + (j - center) ** 2) / (2 * sigma ** 2))
    return kernel / kernel.sum()


def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """2D 卷积（same padding）"""
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    padded = np.pad(image, ((ph, ph), (pw, pw)), mode='reflect')
    result = np.zeros_like(image, dtype=float)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            result[i, j] = np.sum(padded[i:i+kh, j:j+kw] * kernel)
    return result


def sobel_gradients(image: np.ndarray):
    """Sobel 算子计算梯度"""
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    Ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=float)
    Gx = convolve2d(image, Kx)
    Gy = convolve2d(image, Ky)
    magnitude = np.sqrt(Gx ** 2 + Gy ** 2)
    angle = np.arctan2(Gy, Gx)
    return Gx, Gy, magnitude, angle


# ============ 2. Canny Edge Detection ============

def canny_edge(image: np.ndarray, low_thresh=30, high_thresh=60, sigma=1.0):
    """
    Canny 边缘检测管线：
    1. 高斯模糊（降噪）
    2. Sobel 梯度
    3. 非极大值抑制（NMS）
    4. 双阈值 + 连接
    """
    # Step 1: Gaussian blur
    kernel = gaussian_kernel(5, sigma)
    blurred = convolve2d(image.astype(float), kernel)

    # Step 2: Sobel gradients
    _, _, magnitude, angle = sobel_gradients(blurred)

    # Step 3: Non-Maximum Suppression
    nms = np.zeros_like(magnitude)
    angle_deg = angle * 180 / math.pi
    angle_deg[angle_deg < 0] += 180

    for i in range(1, magnitude.shape[0] - 1):
        for j in range(1, magnitude.shape[1] - 1):
            a = angle_deg[i, j]
            # 量化方向
            if (0 <= a < 22.5) or (157.5 <= a <= 180):
                n1, n2 = magnitude[i, j+1], magnitude[i, j-1]
            elif 22.5 <= a < 67.5:
                n1, n2 = magnitude[i+1, j+1], magnitude[i-1, j-1]
            elif 67.5 <= a < 112.5:
                n1, n2 = magnitude[i+1, j], magnitude[i-1, j]
            else:
                n1, n2 = magnitude[i+1, j-1], magnitude[i-1, j+1]
            if magnitude[i, j] >= n1 and magnitude[i, j] >= n2:
                nms[i, j] = magnitude[i, j]

    # Step 4: Double threshold + hysteresis
    edges = np.zeros_like(nms)
    strong = nms >= high_thresh
    weak = (nms >= low_thresh) & (nms < high_thresh)
    edges[strong] = 255

    # 连接弱边缘到强边缘
    changed = True
    while changed:
        changed = False
        for i in range(1, edges.shape[0] - 1):
            for j in range(1, edges.shape[1] - 1):
                if weak[i, j] and edges[i, j] == 0:
                    if np.any(edges[i-1:i+2, j-1:j+2] == 255):
                        edges[i, j] = 255
                        changed = True

    return edges


# ============ 3. DoG (SIFT-like) Keypoints ============

def dog_keypoints(image: np.ndarray, sigma1=1.0, sigma2=2.0, threshold=5.0):
    """
    Difference of Gaussians 关键点检测
    DoG = G(σ1) - G(σ2)
    极值点 = 候选关键点
    """
    g1 = convolve2d(image, gaussian_kernel(5, sigma1))
    g2 = convolve2d(image, gaussian_kernel(5, sigma2))
    dog = g1 - g2

    # 找局部极值（3x3 邻域最大/最小）
    keypoints = []
    for i in range(1, dog.shape[0] - 1):
        for j in range(1, dog.shape[1] - 1):
            patch = dog[i-1:i+2, j-1:j+2]
            if abs(dog[i, j]) > threshold:
                if dog[i, j] == patch.max() or dog[i, j] == patch.min():
                    keypoints.append((i, j, dog[i, j]))
    return keypoints, dog


# ============ 4. RANSAC Homography ============

def ransac_homography(src_points: np.ndarray, dst_points: np.ndarray,
                       threshold=3.0, max_iter=200, sample_size=4):
    """
    RANSAC 单应性估计
    H 满足: dst = H @ src（齐次坐标）

    返回 inlier mask 和估计的 H
    """

    def estimate_homography(pts1, pts2):
        """DLT 算法估计 H（至少 4 对点）"""
        n = len(pts1)
        A = []
        for i in range(n):
            x, y = pts1[i]
            xp, yp = pts2[i]
            A.append([-x, -y, -1, 0, 0, 0, x * xp, y * xp, xp])
            A.append([0, 0, 0, -x, -y, -1, x * yp, y * yp, yp])
        A = np.array(A)
        _, _, Vt = np.linalg.svd(A)
        H = Vt[-1].reshape(3, 3)
        return H / H[2, 2] if abs(H[2, 2]) > 1e-10 else H

    def reprojection_error(H, pts1, pts2):
        errors = []
        for i in range(len(pts1)):
            src = np.array([pts1[i][0], pts1[i][1], 1])
            projected = H @ src
            if abs(projected[2]) < 1e-10:
                errors.append(float('inf'))
                continue
            projected = projected[:2] / projected[2]
            errors.append(np.linalg.norm(projected - pts2[i]))
        return np.array(errors)

    best_inliers = None
    best_count = 0
    n = len(src_points)

    for _ in range(max_iter):
        indices = random.sample(range(n), min(sample_size, n))
        H = estimate_homography(src_points[indices], dst_points[indices])
        errors = reprojection_error(H, src_points, dst_points)
        inliers = errors < threshold
        count = np.sum(inliers)
        if count > best_count:
            best_count = count
            best_inliers = inliers

    # 用所有 inliers 重新拟合
    if best_inliers is not None and best_count >= 4:
        H_final = estimate_homography(src_points[best_inliers], dst_points[best_inliers])
    else:
        H_final = np.eye(3)

    return H_final, best_inliers, best_count


# ============ 5. ASCII Image Display ============

def ascii_image(image: np.ndarray, width=30, chars=' .:-=+*#%@'):
    """ASCII 可视化 2D 图像"""
    h, w = image.shape
    if h == 0 or w == 0:
        return "(empty)"
    scale = width / w
    new_h = max(int(h * scale * 0.5), 1)  # 字符宽高比
    # 简单降采样
    sh, sw = max(h // new_h, 1), max(w // width, 1)
    min_v, max_v = float(image.min()), float(image.max())
    lines = []
    for i in range(0, h, sh):
        line = []
        for j in range(0, w, sw):
            block = image[i:i+sh, j:j+sw]
            if block.size == 0:
                line.append(' ')
                continue
            val = float(np.mean(block))
            # 归一化到 0-1
            norm = (val - min_v) / (max_v - min_v + 1e-10)
            idx = min(int(round(norm * (len(chars) - 1))), len(chars) - 1)
            line.append(chars[idx])
        lines.append(''.join(line))
    return '\n'.join(lines)


# ============ 6. FCN (Fully Convolutional Network) ============

def compute_iou(pred, target):
    """Intersection-over-Union for binary masks."""
    inter = np.sum(pred & target)
    union = np.sum(pred | target)
    return inter / (union + 1e-10)


class FCN:
    """
    最小可训练 Fully Convolutional Network（语义分割）。
    全卷积结构（无全连接层），输出与输入等大的像素级概率图：
      Conv(1→4, 3×3, same-pad) → ReLU → Conv(4→1, 3×3, same-pad) → Sigmoid
    训练: 像素级二元交叉熵（BCE）+ SGD 反向传播（从零实现 backward）。
    """

    def __init__(self, lr=0.8):
        rng = np.random.RandomState(0)
        self.W1 = rng.randn(4, 1, 3, 3) * np.sqrt(2.0 / 9)
        self.b1 = np.zeros(4)
        self.W2 = rng.randn(1, 4, 3, 3) * np.sqrt(2.0 / 36)
        self.b2 = np.zeros(1)
        self.lr = lr

    @staticmethod
    def _relu(z):
        return np.maximum(0, z)

    @staticmethod
    def _sigmoid(z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -250, 250)))

    @staticmethod
    def _conv_same(X, W, b):
        """X:(C_in,H,W) same-padding(1) → (C_out,H,W)；同时返回 padded 输入供反向传播"""
        _, H, Wd = X.shape
        C_out = W.shape[0]
        padded = np.pad(X, ((0, 0), (1, 1), (1, 1)))
        out = np.zeros((C_out, H, Wd))
        for co in range(C_out):
            for i in range(H):
                for j in range(Wd):
                    out[co, i, j] = np.sum(padded[:, i:i + 3, j:j + 3] * W[co]) + b[co]
        return out, padded

    def forward(self, X):
        """X:(H,W) 灰度图 → p:(H,W) 前景概率图"""
        x = X[None, :, :]                                # (1,H,W)
        self.z1, self.x_pad = self._conv_same(x, self.W1, self.b1)
        self.a1 = self._relu(self.z1)
        self.z2, self.a1_pad = self._conv_same(self.a1, self.W2, self.b2)
        self.p = self._sigmoid(self.z2)                  # (1,H,W)
        return self.p[0]                                 # (H,W)

    def backward(self, Y):
        """Y:(H,W) 目标 mask。计算各参数梯度并 SGD 更新。"""
        H, W = Y.shape
        N = H * W
        # sigmoid + BCE 合并梯度: dL/dz2 = (p - y) / N
        dz2 = (self.p[0] - Y)[None, :, :] / N            # (1,H,W)

        # ---- conv2 权重/偏置梯度 ----
        dW2 = np.zeros_like(self.W2)
        for ci in range(4):
            for di in range(3):
                for dj in range(3):
                    dW2[0, ci, di, dj] = np.sum(
                        dz2[0] * self.a1_pad[ci, di:di + H, dj:dj + W])
        db2 = np.array([dz2.sum()])

        # ---- 输入梯度: 转置卷积还原 da1 ----
        da1_pad = np.zeros_like(self.a1_pad)
        for ci in range(4):
            for di in range(3):
                for dj in range(3):
                    da1_pad[ci, di:di + H, dj:dj + W] += dz2[0] * self.W2[0, ci, di, dj]
        dz1 = da1_pad[:, 1:H + 1, 1:W + 1] * (self.z1 > 0)   # ReLU'

        # ---- conv1 权重/偏置梯度 ----
        dW1 = np.zeros_like(self.W1)
        for co in range(4):
            for di in range(3):
                for dj in range(3):
                    dW1[co, 0, di, dj] = np.sum(
                        dz1[co] * self.x_pad[0, di:di + H, dj:dj + W])
        db1 = dz1.sum(axis=(1, 2))

        # ---- SGD 更新 ----
        self.W2 -= self.lr * dW2; self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1; self.b1 -= self.lr * db1


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 420: Introduction to Computer Vision Demo")
    print("=" * 60)

    np.random.seed(42)
    random.seed(42)

    # 创建合成图像：有边缘的方块
    print("\n📋 1. 高斯滤波 + Sobel 梯度")
    image = np.zeros((20, 30))
    image[5:15, 8:22] = 1.0  # 白色方块
    print("   原始图像（方块）：")
    print(ascii_image(image, width=30))

    kernel = gaussian_kernel(5, sigma=1.0)
    print(f"\n   高斯核 (5x5, σ=1.0) 中心值: {kernel[2,2]:.4f}")
    print(f"   核 sum = {kernel.sum():.6f}（应=1.0）")

    blurred = convolve2d(image, kernel)
    print("\n   高斯模糊后：")
    print(ascii_image(blurred, width=30))

    Gx, Gy, mag, ang = sobel_gradients(image)
    print(f"\n   Sobel 梯度幅值：")
    print(ascii_image(mag, width=30))
    print(f"   梯度幅值范围: [{mag.min():.2f}, {mag.max():.2f}]")
    print(f"   → 边缘处梯度最大（方块边界）")

    # 2. Canny
    print("\n📋 2. Canny 边缘检测")
    edges = canny_edge(image, low_thresh=0.3, high_thresh=0.5, sigma=1.0)
    print("   Canny 边缘结果：")
    print(ascii_image(edges, width=30))
    edge_pixels = np.sum(edges > 0)
    print(f"   边缘像素数: {edge_pixels}")
    print(f"   → 只保留了细边缘（NMS 去除了非极大值）")

    # 3. DoG
    print("\n📋 3. DoG 关键点检测")
    # 创建更复杂的图像
    image2 = np.zeros((24, 24))
    image2[6:18, 6:18] = 1.0
    image2[10:14, 10:14] = 2.0  # 内部更亮
    image2 += np.random.randn(24, 24) * 0.05  # 噪声

    keypoints, dog = dog_keypoints(image2, sigma1=1.0, sigma2=3.0, threshold=0.1)
    print(f"   检测到 {len(keypoints)} 个关键点")
    for kp in keypoints[:5]:
        print(f"     ({kp[0]:2d}, {kp[1]:2d}) 响应={kp[2]:.4f}")
    print(f"   → 关键点集中在角点和边缘（尺度空间极值）")

    # 4. RANSAC
    print("\n📋 4. RANSAC 单应性估计")
    # 生成干净 + 有噪声的点对
    true_H = np.array([[1.1, 0.1, 5], [0.05, 0.95, 3], [0.0001, 0.0002, 1]])
    n_points = 50
    src = np.random.rand(n_points, 2) * 100
    # 变换
    dst_clean = []
    for p in src:
        h = true_H @ np.array([p[0], p[1], 1])
        dst_clean.append([h[0] / h[2], h[1] / h[2]])
    dst_clean = np.array(dst_clean)

    # 加 10 个 outlier
    dst = dst_clean.copy()
    for i in range(10):
        dst[i] += np.random.randn(2) * 50  # 大偏移

    H_est, inliers, inlier_count = ransac_homography(src, dst, threshold=5.0, max_iter=300)
    print(f"   生成 {n_points} 个点对（含 10 个 outlier）")
    print(f"   RANSAC 识别 inliers: {inlier_count}/{n_points}")
    print(f"   Inlier 比例: {inlier_count/n_points:.1%}")
    print(f"\n   估计 H ≈")
    for row in H_est:
        print(f"     [{row[0]:8.4f} {row[1]:8.4f} {row[2]:8.4f}]")
    print(f"\n   反直觉：即使 20% outlier，RANSAC 仍能正确拟合")

    # 5. FCN 语义分割（可训练全卷积网络）
    print("\n📋 5. FCN 语义分割（可训练全卷积网络）")
    rng_fcn = np.random.RandomState(1)
    H, W = 12, 12

    def make_sample():
        """随机位置方块 → (image, mask)"""
        img = np.zeros((H, W))
        r0, c0 = rng_fcn.randint(0, H - 6), rng_fcn.randint(0, W - 6)
        sz = rng_fcn.randint(4, 7)
        img[r0:r0 + sz, c0:c0 + sz] = 1.0
        img += rng_fcn.randn(H, W) * 0.1
        mask = np.zeros((H, W))
        mask[r0:r0 + sz, c0:c0 + sz] = 1.0
        return img, mask

    fcn = FCN(lr=0.8)
    n_params = fcn.W1.size + fcn.b1.size + fcn.W2.size + fcn.b2.size
    print(f"   图像 {H}×{W}, 结构: Conv(1→4,3×3)+ReLU → Conv(4→1,3×3)+Sigmoid")
    print(f"   参数总数: {n_params}（全卷积，无全连接层）")

    # 训练前 IoU
    x0, y0 = make_sample()
    p0 = fcn.forward(x0)
    print(f"\n   训练前 IoU = {compute_iou(p0 > 0.5, y0 > 0.5):.3f}（接近随机）")

    print(f"\n   训练 80 步（每步一个新样本）:")
    print(f"   {'step':>5} {'BCE loss':>9} {'IoU':>8}")
    for step in range(80):
        x, y = make_sample()
        p = fcn.forward(x)
        fcn.backward(y)
        if step % 20 == 0 or step == 79:
            bce = -np.mean(y * np.log(p + 1e-10) + (1 - y) * np.log(1 - p + 1e-10))
            print(f"   {step:5d} {bce:9.4f} {compute_iou(p > 0.5, y > 0.5):8.3f}")

    # 测试集平均 IoU
    test_ious = []
    for _ in range(20):
        xt, yt = make_sample()
        test_ious.append(compute_iou(fcn.forward(xt) > 0.5, yt > 0.5))
    mean_iou = np.mean(test_ious)
    print(f"\n   训练后测试集平均 IoU = {mean_iou:.3f}（应 > 0.5）")

    # 可视化一个样本
    xv, yv = make_sample()
    pv = fcn.forward(xv)
    print(f"\n   样本可视化（左=输入, 中=真值, 右=预测）:")
    print("   输入:"); print(ascii_image(xv, width=24))
    print("   真值:"); print(ascii_image(yv, width=24, chars=' .:#'))
    print("   预测:"); print(ascii_image(pv, width=24, chars=' .:#'))
    print(f"\n   反直觉发现：仅 2 层 3×3 卷积（{n_params} 参数）即可学会像素级分割")
    print(f"   → 全卷积的威力：输出空间分辨率与输入相同（逐像素分类）")

    print("\n✅ CSC 420 完成！")
    print("💡 覆盖：高斯/Sobel + Canny边缘 + DoG关键点 + RANSAC单应性 + FCN分割")


if __name__ == "__main__":
    demo()
