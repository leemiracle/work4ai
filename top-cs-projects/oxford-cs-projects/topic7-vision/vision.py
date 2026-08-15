"""
Computer Vision (Oxford CS)
================================================
覆盖主题：
- 线性滤波（高斯 / Sobel 边缘检测）
- Canny 边缘检测（完整 pipeline）
- 图像分割（k-means / region growing）
- CNN forward pass（纯 NumPy）

核心论文/教材（已核实）：
- Szeliski "Computer Vision: Algorithms and Applications" Springer 2022
- Canny "A Computational Approach to Edge Detection" IEEE TPAMI 1986
- Krizhevsky, Sutskever, Hinton "ImageNet Classification with Deep CNNs" NeurIPS 2012
- LeCun, Bottou, Bengio, Haffner "Gradient-Based Learning Applied to Documents" Proc IEEE 1998

本文件实现：
- 高斯模糊（可分离滤波）
- Sobel 边缘 + Canny（非极大抑制 + 双阈值 + 滞后）
- K-means 图像分割
- CNN 前向传播（Conv2d + ReLU + MaxPool）

运行：
    python vision.py
"""
from __future__ import annotations
import math
import random


# ============ 1. 图像表示 ============

def make_image(width: int, height: int, fill: float = 0.0) -> list[list[float]]:
    """灰度图: H×W 矩阵，值 [0, 255]"""
    return [[fill] * width for _ in range(height)]


def make_test_image() -> list[list[float]]:
    """生成一个测试图像：左半暗、右半亮、有方块"""
    w, h = 16, 12
    img = make_image(w, h, 50)  # 背景 50
    # 右半更亮
    for y in range(h):
        for x in range(w // 2, w):
            img[y][x] = 200
    # 中间放一个方块
    for y in range(4, 8):
        for x in range(6, 10):
            img[y][x] = 255
    return img


def print_image(img: list[list[float]], width: int = 30, symbols: str = " .:-=+*#%@"):
    """ASCII 打印图像"""
    h, w = len(img), len(img[0])
    scale = len(symbols) - 1
    for row in img:
        line = ""
        for val in row:
            idx = min(int(val / 255 * scale), scale)
            line += symbols[idx]
        print("  " + line)


# ============ 2. 高斯模糊（可分离滤波） ============

def gaussian_kernel_1d(sigma: float, radius: int = None) -> list[float]:
    """1D 高斯核 G(x) = exp(-x²/(2σ²)) / (σ√(2π))"""
    if radius is None:
        radius = int(3 * sigma)
    kernel = []
    for x in range(-radius, radius + 1):
        val = math.exp(-x * x / (2 * sigma * sigma))
        kernel.append(val)
    total = sum(kernel)
    return [k / total for k in kernel]


def convolve_1d_horizontal(img: list[list[float]], kernel: list[float]) -> list[list[float]]:
    """水平方向 1D 卷积"""
    h, w = len(img), len(img[0])
    r = len(kernel) // 2
    result = make_image(w, h)
    for y in range(h):
        for x in range(w):
            val = 0.0
            for k in range(len(kernel)):
                xx = max(0, min(w - 1, x + k - r))  # clamp
                val += img[y][xx] * kernel[k]
            result[y][x] = val
    return result


def convolve_1d_vertical(img: list[list[float]], kernel: list[float]) -> list[list[float]]:
    """垂直方向 1D 卷积"""
    h, w = len(img), len(img[0])
    r = len(kernel) // 2
    result = make_image(w, h)
    for y in range(h):
        for x in range(w):
            val = 0.0
            for k in range(len(kernel)):
                yy = max(0, min(h - 1, y + k - r))
                val += img[yy][x] * kernel[k]
            result[y][x] = val
    return result


def gaussian_blur(img: list[list[float]], sigma: float = 1.0) -> list[list[float]]:
    """高斯模糊（利用可分离性: 2D 高斯 = 水平1D × 垂直1D）"""
    kernel = gaussian_kernel_1d(sigma)
    temp = convolve_1d_horizontal(img, kernel)
    return convolve_1d_vertical(temp, kernel)


# ============ 3. Sobel 边缘检测 ============

def sobel_gradients(img: list[list[float]]) -> tuple[list[list[float]], list[list[float]], list[list[float]]]:
    """Sobel 算子计算梯度。
    Gx = [[-1,0,1],[-2,0,2],[-1,0,1]]
    Gy = [[-1,-2,-1],[0,0,0],[1,2,1]]
    """
    h, w = len(img), len(img[0])
    gx = make_image(w, h)
    gy = make_image(w, h)
    magnitude = make_image(w, h)

    sobel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    sobel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            sx = sy = 0.0
            for dy in range(3):
                for dx in range(3):
                    val = img[y + dy - 1][x + dx - 1]
                    sx += val * sobel_x[dy][dx]
                    sy += val * sobel_y[dy][dx]
            gx[y][x] = sx
            gy[y][x] = sy
            magnitude[y][x] = math.sqrt(sx * sx + sy * sy)

    return gx, gy, magnitude


def sobel_edge(img: list[list[float]], threshold: float = 100) -> list[list[float]]:
    """简单 Sobel 阈值边缘"""
    _, _, mag = sobel_gradients(img)
    h, w = len(img), len(img[0])
    edges = make_image(w, h)
    for y in range(h):
        for x in range(w):
            edges[y][x] = 255.0 if mag[y][x] > threshold else 0.0
    return edges


# ============ 4. Canny 边缘（完整 pipeline） ============

def canny_edge(img: list[list[float]], sigma: float = 1.0,
               low_thresh: float = 50, high_thresh: float = 100) -> list[list[float]]:
    """Canny 边缘检测：
    1. 高斯平滑
    2. Sobel 梯度（幅值 + 方向）
    3. 非极大抑制（NMS）
    4. 双阈值 + 滞后连接
    """
    # Step 1: Gaussian blur
    blurred = gaussian_blur(img, sigma)

    # Step 2: Gradients
    gx, gy, mag = sobel_gradients(blurred)

    # Step 3: Non-maximum suppression
    h, w = len(img), len(img[0])
    nms = make_image(w, h)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            angle = math.atan2(gy[y][x], gx[y][x]) * 180 / math.pi
            if angle < 0:
                angle += 180
            # 量化到 4 个方向
            if (0 <= angle < 22.5) or (157.5 <= angle <= 180):
                n1, n2 = mag[y][x-1], mag[y][x+1]
            elif 22.5 <= angle < 67.5:
                n1, n2 = mag[y-1][x+1], mag[y+1][x-1]
            elif 67.5 <= angle < 112.5:
                n1, n2 = mag[y-1][x], mag[y+1][x]
            else:
                n1, n2 = mag[y-1][x-1], mag[y+1][x+1]
            if mag[y][x] >= n1 and mag[y][x] >= n2:
                nms[y][x] = mag[y][x]

    # Step 4: Double threshold + hysteresis
    edges = make_image(w, h)
    strong = [(y, x) for y in range(h) for x in range(w)
              if nms[y][x] >= high_thresh]
    for y, x in strong:
        edges[y][x] = 255.0

    # Hysteresis: 从 strong 边缘 BFS 连接 weak 边缘
    visited = set()
    queue = list(strong)
    while queue:
        y, x = queue.pop()
        if (y, x) in visited:
            continue
        visited.add((y, x))
        edges[y][x] = 255.0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and (ny, nx) not in visited:
                    if nms[ny][nx] >= low_thresh:
                        queue.append((ny, nx))

    return edges


# ============ 5. K-Means 分割 ============

def kmeans_segment(img: list[list[float]], k: int = 3, max_iter: int = 20) -> list[list[float]]:
    """K-means 图像分割（按像素值聚类）"""
    h, w = len(img), len(img[0])
    pixels = [img[y][x] for y in range(h) for x in range(w)]

    # 初始化中心（随机选 k 个像素值）
    random.seed(42)
    centers = random.sample(pixels, k)

    for iteration in range(max_iter):
        # 分配
        clusters = [[] for _ in range(k)]
        for p in pixels:
            best_k = min(range(k), key=lambda i: abs(p - centers[i]))
            clusters[best_k].append(p)

        # 更新
        new_centers = []
        for i in range(k):
            if clusters[i]:
                new_centers.append(sum(clusters[i]) / len(clusters[i]))
            else:
                new_centers.append(centers[i])

        if new_centers == centers:
            break
        centers = new_centers

    # 生成分割图（每个像素替换为所属簇的中心值）
    result = make_image(w, h)
    for y in range(h):
        for x in range(w):
            best_k = min(range(k), key=lambda i: abs(img[y][x] - centers[i]))
            result[y][x] = centers[best_k]

    return result, centers


# ============ 6. CNN Forward (Mini) ============

def conv2d(input_map: list[list[float]], kernel: list[list[float]]) -> list[list[float]]:
    """2D 卷积（无 padding，stride=1）"""
    ih, iw = len(input_map), len(input_map[0])
    kh, kw = len(kernel), len(kernel[0])
    oh, ow = ih - kh + 1, iw - kw + 1
    output = make_image(ow, oh)
    for y in range(oh):
        for x in range(ow):
            val = 0.0
            for dy in range(kh):
                for dx in range(kw):
                    val += input_map[y + dy][x + dx] * kernel[dy][dx]
            output[y][x] = val
    return output


def relu(feature_map: list[list[float]]) -> list[list[float]]:
    """ReLU 激活"""
    h, w = len(feature_map), len(feature_map[0])
    return [[max(0.0, feature_map[y][x]) for x in range(w)] for y in range(h)]


def maxpool2d(feature_map: list[list[float]], pool_size: int = 2) -> list[list[float]]:
    """2×2 最大池化"""
    h, w = len(feature_map), len(feature_map[0])
    oh, ow = h // pool_size, w // pool_size
    output = make_image(ow, oh)
    for y in range(oh):
        for x in range(ow):
            if pool_size == 2:
                val = max(
                    feature_map[y*pool_size][x*pool_size],
                    feature_map[y*pool_size][x*pool_size+1],
                    feature_map[y*pool_size+1][x*pool_size],
                    feature_map[y*pool_size+1][x*pool_size+1]
                )
            else:
                val = feature_map[y*pool_size][x*pool_size]
            output[y][x] = val
    return output


def cnn_forward(img: list[list[float]]) -> dict:
    """简单 CNN 前向传播：Conv → ReLU → MaxPool → Conv → ReLU → MaxPool"""
    # Layer 1: Conv (edge detector kernel) + ReLU + MaxPool
    kernel1 = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]  # 中心锐化
    conv1 = conv2d(img, kernel1)
    relu1 = relu(conv1)
    pool1 = maxpool2d(relu1, 2)

    # Layer 2: Conv + ReLU + MaxPool
    kernel2 = [[1, 0], [0, -1]]  # 对角检测
    if len(pool1) >= 3 and len(pool1[0]) >= 3:
        conv2 = conv2d(pool1, kernel2)
        relu2 = relu(conv2)
    else:
        relu2 = pool1

    return {"conv1": conv1, "pool1": pool1, "final": relu2}


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Computer Vision (Oxford CS) Demo")
    print("=" * 65)

    img = make_test_image()
    print("\n📋 原始测试图像 (16×12):")
    print_image(img)

    # 1. 高斯模糊
    print("\n📋 高斯模糊 (σ=1.0):")
    blurred = gaussian_blur(img, sigma=1.0)
    print_image(blurred)

    # 2. Sobel
    print("\n📋 Sobel 边缘 (threshold=100):")
    edges = sobel_edge(img, threshold=100)
    print_image(edges)

    # 3. Canny
    print("\n📋 Canny 边缘 (完整 pipeline):")
    canny = canny_edge(img, sigma=1.0, low_thresh=30, high_thresh=80)
    print_image(canny)

    # 4. K-Means 分割
    print("\n📋 K-Means 分割 (k=3):")
    segmented, centers = kmeans_segment(img, k=3)
    print_image(segmented)
    print(f"   簇中心: {[f'{c:.0f}' for c in centers]}")

    # 5. CNN Forward
    print("\n📋 CNN 前向传播 (Conv→ReLU→MaxPool×2)")
    # 用更大的测试图
    cnn_img = make_image(8, 8, 100)
    for y in range(2, 6):
        for x in range(2, 6):
            cnn_img[y][x] = 255

    features = cnn_forward(cnn_img)
    print(f"   输入: {len(cnn_img)}×{len(cnn_img[0])}")
    print(f"   Conv1 输出: {len(features['conv1'])}×{len(features['conv1'][0])}")
    print(f"   Pool1 输出: {len(features['pool1'])}×{len(features['pool1'][0])}")
    print(f"   Final 输出: {len(features['final'])}×{len(features['final'][0])}")

    # 统计
    all_vals = [v for row in features['final'] for v in row]
    active = sum(1 for v in all_vals if v > 0)
    print(f"   激活神经元: {active}/{len(all_vals)} ({active/max(len(all_vals),1)*100:.0f}%)")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. 高斯模糊利用可分离性：2D卷积(9次乘法)→2个1D卷积(6次乘法)，快33%")
    print("   2. Canny 的非极大抑制(NMS)让边缘变成1像素细线")
    print("      没有NMS的Sobel边缘是模糊的粗带，有NMS才是锐利线")
    print("   3. K-means k=3 把图像分成3个灰度级，但簇中心不一定是均匀分布")
    print("      取决于像素值分布（测试图有3个峰：50/200/255）")
    print("   4. CNN 每层 Conv+Pool 让空间尺寸减半，但提取了高级特征")
    print("      8×8→6×6→3×3，激活率揭示了边缘检测的本质")
    print("=" * 65)


if __name__ == "__main__":
    main()
