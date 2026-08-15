"""
COS 429 / 529 Computer Vision（Princeton）
=============================================
覆盖主题：
- conv2d（2D 卷积，含 padding/stride）
- Canny 边缘检测（Sobel → NMS → 双阈值滞后）
- 形态学操作（erode / dilate / opening / closing）
- SIFT-like DoG（Difference of Gaussians 特征点检测）

核心论文/教材：
- Szeliski "Computer Vision: Algorithms and Applications" Ch 3-4
- Canny 1986 "A Computational Approach to Edge Detection" IEEE TPAMI
- Lowe 2004 "Distinctive Image Features from Scale-Invariant Keypoints" IJCV (SIFT)
- Dalal & Triggs 2005 "Histograms of Oriented Gradients for Human Detection" CVPR

本文件实现：
1. conv2d (with padding & stride)
2. Canny edge detection (Sobel gradient → NMS → hysteresis)
3. Morphological operations (erode / dilate)
4. DoG (Difference of Gaussians) keypoint detection

运行：
    python vision.py
"""
from __future__ import annotations
import math


# ================================================================
# 1. Conv2D
# ================================================================

def gaussian_kernel(size: int, sigma: float) -> list[list[float]]:
    """Generate Gaussian kernel."""
    k = []
    center = size // 2
    s2 = 2 * sigma * sigma
    for i in range(size):
        row = []
        for j in range(size):
            dx, dy = i - center, j - center
            row.append(math.exp(-(dx * dx + dy * dy) / s2) / (math.pi * s2))
        k.append(row)
    # Normalize
    total = sum(sum(r) for r in k)
    return [[v / total for v in r] for r in k]


def conv2d(image: list[list[float]], kernel: list[list[float]],
           padding: int = 0, stride: int = 1) -> list[list[float]]:
    """2D convolution. Image is H×W, kernel is K×K."""
    h, w = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])

    # Pad
    if padding > 0:
        padded = [[0.0] * (w + 2 * padding) for _ in range(h + 2 * padding)]
        for i in range(h):
            for j in range(w):
                padded[i + padding][j + padding] = image[i][j]
    else:
        padded = image

    ph, pw = len(padded), len(padded[0])
    oh = (ph - kh) // stride + 1
    ow = (pw - kw) // stride + 1
    output = [[0.0] * ow for _ in range(oh)]

    for oi in range(oh):
        for oj in range(ow):
            total = 0.0
            for ki in range(kh):
                for kj in range(kw):
                    pi = oi * stride + ki
                    pj = oj * stride + kj
                    total += padded[pi][pj] * kernel[ki][kj]
            output[oi][oj] = total
    return output


# ================================================================
# 2. Canny Edge Detection
# ================================================================

def sobel_gradients(image):
    """Compute gradients using Sobel operators."""
    sx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    sy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    gx = conv2d(image, sx, padding=1)
    gy = conv2d(image, sy, padding=1)
    magnitude = []
    angle = []
    for i in range(len(gx)):
        mag_row = []
        ang_row = []
        for j in range(len(gx[0])):
            mag = math.sqrt(gx[i][j] ** 2 + gy[i][j] ** 2)
            ang = math.atan2(gy[i][j], gx[i][j]) * 180 / math.pi
            if ang < 0:
                ang += 180
            mag_row.append(mag)
            ang_row.append(ang)
        magnitude.append(mag_row)
        angle.append(ang_row)
    return magnitude, angle


def non_max_suppression(magnitude, angle):
    """Non-maximum suppression: thin edges to 1 pixel."""
    h, w = len(magnitude), len(magnitude[0])
    result = [[0.0] * w for _ in range(h)]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            a = angle[i][j]
            # Quantize angle to 4 directions
            if (0 <= a < 22.5) or (157.5 <= a <= 180):
                n1, n2 = magnitude[i][j - 1], magnitude[i][j + 1]
            elif 22.5 <= a < 67.5:
                n1, n2 = magnitude[i - 1][j + 1], magnitude[i + 1][j - 1]
            elif 67.5 <= a < 112.5:
                n1, n2 = magnitude[i - 1][j], magnitude[i + 1][j]
            else:
                n1, n2 = magnitude[i - 1][j - 1], magnitude[i + 1][j + 1]
            if magnitude[i][j] >= n1 and magnitude[i][j] >= n2:
                result[i][j] = magnitude[i][j]
    return result


def hysteresis(image, low_thresh, high_thresh):
    """Double threshold + edge tracking by hysteresis."""
    h, w = len(image), len(image[0])
    strong = [[0 for _ in range(w)] for _ in range(h)]
    # Mark strong and weak edges
    for i in range(h):
        for j in range(w):
            if image[i][j] >= high_thresh:
                strong[i][j] = 2  # strong edge
            elif image[i][j] >= low_thresh:
                strong[i][j] = 1  # weak edge

    # Connect weak edges to strong edges (iterative)
    changed = True
    while changed:
        changed = False
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if strong[i][j] == 1:
                    # Check 8-neighbors for strong edge
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            if strong[i + di][j + dj] == 2:
                                strong[i][j] = 2
                                changed = True
                                break
    # Binary output
    return [[1 if strong[i][j] == 2 else 0 for j in range(w)] for i in range(h)]


def canny_edge(image, low=30, high=80):
    """Full Canny pipeline."""
    # 1. Smooth with Gaussian
    gauss = gaussian_kernel(3, 1.0)
    smoothed = conv2d(image, gauss, padding=1)
    # 2. Sobel gradients
    mag, ang = sobel_gradients(smoothed)
    # 3. Non-maximum suppression
    nms = non_max_suppression(mag, ang)
    # 4. Hysteresis
    edges = hysteresis(nms, low, high)
    return edges


# ================================================================
# 3. Morphological Operations
# ================================================================

def dilate(binary, struct_size=3):
    """Dilation: grow white regions."""
    h, w = len(binary), len(binary[0])
    result = [[0] * w for _ in range(h)]
    pad = struct_size // 2
    for i in range(h):
        for j in range(w):
            if binary[i][j] == 1:
                for di in range(-pad, pad + 1):
                    for dj in range(-pad, pad + 1):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < h and 0 <= nj < w:
                            result[ni][nj] = 1
    return result


def erode(binary, struct_size=3):
    """Erosion: shrink white regions."""
    h, w = len(binary), len(binary[0])
    result = [[0] * w for _ in range(h)]
    pad = struct_size // 2
    for i in range(pad, h - pad):
        for j in range(pad, w - pad):
            all_white = True
            for di in range(-pad, pad + 1):
                for dj in range(-pad, pad + 1):
                    if binary[i + di][j + dj] == 0:
                        all_white = False
                        break
                if not all_white:
                    break
            if all_white:
                result[i][j] = 1
    return result


def morph_open(binary, struct_size=3):
    """Opening: erode then dilate (removes small noise)."""
    return dilate(erode(binary, struct_size), struct_size)


def morph_close(binary, struct_size=3):
    """Closing: dilate then erode (fills small holes)."""
    return erode(dilate(binary, struct_size), struct_size)


# ================================================================
# 4. DoG (Difference of Gaussians) — SIFT-like
# ================================================================

def dog_keypoints(image, sigma1=1.0, sigma2=2.0, threshold=0.5):
    """Find keypoints using Difference of Gaussians."""
    g1 = conv2d(image, gaussian_kernel(5, sigma1), padding=2)
    g2 = conv2d(image, gaussian_kernel(5, sigma2), padding=2)
    # DoG = G(sigma1) - G(sigma2)
    h, w = len(image), len(image[0])
    dog = [[g1[i][j] - g2[i][j] for j in range(w)] for i in range(h)]
    # Find local extrema
    keypoints = []
    for i in range(2, h - 2):
        for j in range(2, w - 2):
            val = dog[i][j]
            if abs(val) < threshold:
                continue
            is_max = True
            is_min = True
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if di == 0 and dj == 0:
                        continue
                    n = dog[i + di][j + dj]
                    if n >= val:
                        is_max = False
                    if n <= val:
                        is_min = False
            if is_max or is_min:
                keypoints.append((i, j, val))
    return keypoints, dog


# ================================================================
# Helper: generate test image
# ================================================================

def make_test_image(size=16):
    """Create a simple test image: bright square on dark background."""
    img = [[0.1] * size for _ in range(size)]
    for i in range(size // 4, 3 * size // 4):
        for j in range(size // 4, 3 * size // 4):
            img[i][j] = 0.9
    return img


def make_circle_image(size=20):
    """Circle on dark background."""
    img = [[0.1] * size for _ in range(size)]
    cx = cy = size // 2
    r = size // 3
    for i in range(size):
        for j in range(size):
            if (i - cx) ** 2 + (j - cy) ** 2 < r * r:
                img[i][j] = 0.8
    return img


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 429/529: Computer Vision Demo")
    print("=" * 60)

    # --- 1. Conv2D ---
    print("\n📋 1. Conv2D (Gaussian smoothing)")
    img = make_test_image(12)
    gauss = gaussian_kernel(3, 1.0)
    smoothed = conv2d(img, gauss, padding=1)
    print(f"   原图: 12×12, 中心 6×6 方块")
    print(f"   平滑后中心像素: {smoothed[6][6]:.4f} (原: {img[6][6]:.1f})")
    print(f"   边缘像素变化: {smoothed[3][3]:.4f} (原: {img[3][3]:.1f})")

    # --- 2. Canny Edge ---
    print("\n📋 2. Canny 边缘检测")
    edge_img = make_test_image(14)
    edges = canny_edge(edge_img, low=0.5, high=1.5)
    edge_count = sum(sum(row) for row in edges)
    print(f"   输入: 14×14 方块图像")
    print(f"   检测到 {int(edge_count)} 个边缘像素")
    # Show ASCII edges (sample)
    print("   边缘图 (前8×8区域):")
    for i in range(min(8, len(edges))):
        print(f"     {''.join('#' if edges[i][j] else '.' for j in range(min(8, len(edges[0]))))}")

    # --- 3. Morphology ---
    print("\n📋 3. 形态学操作")
    binary = [[0] * 10 for _ in range(10)]
    binary[3][3] = binary[3][4] = binary[4][3] = 1  # small blob
    binary[6][6] = binary[6][7] = binary[7][6] = binary[7][7] = 1
    binary[2][8] = 1  # noise pixel

    dilated = dilate(binary, 3)
    eroded = erode(binary, 3)
    opened = morph_open(binary, 3)

    def count_ones(img):
        return sum(sum(row) for row in img)

    print(f"   原始二值图: {count_ones(binary)} 个白像素")
    print(f"   膨胀后:     {count_ones(dilated)} 个白像素")
    print(f"   腐蚀后:     {count_ones(eroded)} 个白像素")
    print(f"   开运算后:   {count_ones(opened)} 个白像素 (噪声被去除)")

    # --- 4. DoG ---
    print("\n📋 4. DoG 关键点检测")
    circle = make_circle_image(20)
    kps, dog = dog_keypoints(circle, threshold=0.01)
    print(f"   输入: 20×20 圆形图像")
    print(f"   检测到 {len(kps)} 个 DoG 关键点")
    if kps:
        print(f"   前5个关键点: {kps[:5]}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    # Canny on circle should detect contour, not interior
    circle_edges = canny_edge(make_circle_image(16), low=0.5, high=1.5)
    interior = circle_edges[8][8]  # center
    contour = circle_edges[8][3]   # near left edge of circle (center=8, r=5)
    print(f"   圆形中心点(8,8)是否为边缘: {bool(interior)} (应为 False)")
    print(f"   圆形轮廓点(8,3)是否为边缘: {bool(contour)} (应为 True)")
    print(f"   → Canny 的非极大值抑制确保边缘只有 1px 宽")
    print(f"   → 这就是为什么 Canny 至今仍是工业标准边缘检测器")

    print("\n✅ COS 429/529 Demo 完成！")


if __name__ == "__main__":
    demo()
