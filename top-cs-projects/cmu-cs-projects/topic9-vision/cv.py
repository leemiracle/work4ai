"""
16-385 Computer Vision (CMU)
================================================
覆盖主题（对应 lecture）：
- Feature extraction: HOG descriptor (Dalal & Triggs)
- Corner detection: Harris corner detector
- Model fitting: RANSAC for line fitting
- Optical flow: Lucas-Kanade (sparse)

核心教材/论文：
- "Dalal & Triggs 2005 CVPR" — Histograms of Oriented Gradients (HOG)
- "Harris & Stephens 1988 Alvey Vision" — corner detector (M structure tensor)
- "Fischler & Bolles 1981 CACM" — Random Sample Consensus (RANSAC)
- "Lucas & Kanade 1981 IJCAI" — differential optical flow

本文件实现：
- HOG descriptor (gradient → orientation histogram → block normalization)
- Harris corner response (structure tensor M, R = det - k*trace²)
- RANSAC line fitting (inlier/outlier classification)
- Lucas-Kanade optical flow (sparse, aperture problem demo)

运行：
    python3 cv.py
"""
from __future__ import annotations
import math
import random

# ============ 1. HOG Descriptor ============

def compute_hog(image, cell_size=4, n_bins=9):
    """
    Compute HOG descriptor for a 2D grayscale image.
    image: 2D list of pixel values [0, 255].
    """
    h, w = len(image), len(image[0])
    # Step 1: gradients
    gx = [[0.0]*w for _ in range(h)]
    gy = [[0.0]*w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            gx[i][j] = (image[i][min(j+1,w-1)] - image[i][max(j-1,0)])
            gy[i][j] = (image[min(i+1,h-1)][j] - image[max(i-1,0)][j])

    mag = [[math.sqrt(gx[i][j]**2 + gy[i][j]**2) for j in range(w)] for i in range(h)]
    ang = [[math.degrees(math.atan2(gy[i][j], gx[i][j])) % 180
            for j in range(w)] for i in range(h)]

    # Step 2: cell histograms
    cells_h = h // cell_size
    cells_w = w // cell_size
    histograms = [[[0.0]*n_bins for _ in range(cells_w)] for _ in range(cells_h)]
    bin_width = 180.0 / n_bins

    for ci in range(cells_h):
        for cj in range(cells_w):
            for di in range(cell_size):
                for dj in range(cell_size):
                    i = ci*cell_size + di
                    j = cj*cell_size + dj
                    if i < h and j < w:
                        b = int(ang[i][j] / bin_width) % n_bins
                        histograms[ci][cj][b] += mag[i][j]

    # Step 3: block normalization (2×2 cells)
    descriptor = []
    for bi in range(cells_h - 1):
        for bj in range(cells_w - 1):
            block = []
            for di in range(2):
                for dj in range(2):
                    block.extend(histograms[bi+di][bj+dj])
            # L2 normalize
            norm = math.sqrt(sum(v*v for v in block))
            if norm > 0:
                block = [v/norm for v in block]
            descriptor.extend(block)
    return descriptor


# ============ 2. Harris Corner Detector ============

def harris_corners(image, k=0.04, threshold=0.01):
    """Detect corners using Harris response R = det(M) - k*trace(M)²."""
    h, w = len(image), len(image[0])
    # gradients
    gx = [[0.0]*w for _ in range(h)]
    gy = [[0.0]*w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            gx[i][j] = image[i][min(j+1,w-1)] - image[i][max(j-1,0)]
            gy[i][j] = image[min(i+1,h-1)][j] - image[max(i-1,0)][j]

    # structure tensor components (smoothed with box filter)
    Ixx = [[gx[i][j]**2 for j in range(w)] for i in range(h)]
    Iyy = [[gy[i][j]**2 for j in range(w)] for i in range(h)]
    Ixy = [[gx[i][j]*gy[i][j] for j in range(w)] for i in range(h)]

    # box filter smoothing (3×3)
    def box_avg(mat, i, j, r=1):
        total, count = 0.0, 0
        for di in range(-r, r+1):
            for dj in range(-r, r+1):
                ni, nj = i+di, j+dj
                if 0 <= ni < h and 0 <= nj < w:
                    total += mat[ni][nj]
                    count += 1
        return total / max(count, 1)

    corners = []
    max_r = 0.0
    responses = [[0.0]*w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            sxx = box_avg(Ixx, i, j)
            syy = box_avg(Iyy, i, j)
            sxy = box_avg(Ixy, i, j)
            det_M = sxx*syy - sxy*sxy
            trace_M = sxx + syy
            R = det_M - k * trace_M**2
            responses[i][j] = R
            max_r = max(max_r, R)

    for i in range(h):
        for j in range(w):
            if responses[i][j] > threshold * max_r:
                corners.append((i, j, responses[i][j]))
    return corners, max_r


# ============ 3. RANSAC Line Fitting ============

def ransac_line(points, n_iters=100, threshold=1.0, min_inliers=5):
    """
    RANSAC for 2D line fitting.
    points: list of (x, y). Returns (best_a, best_b, best_c) for ax+by+c=0.
    """
    best_inliers = []
    best_model = None
    for _ in range(n_iters):
        if len(points) < 2:
            break
        s1, s2 = random.sample(points, 2)
        # line through s1, s2: (y1-y2)*x + (x2-x1)*y + (x1*y2-x2*y1) = 0
        a = s1[1] - s2[1]
        b = s2[0] - s1[0]
        c = s1[0]*s2[1] - s2[0]*s1[1]
        norm = math.sqrt(a*a + b*b)
        if norm < 1e-10:
            continue
        inliers = []
        for p in points:
            dist = abs(a*p[0] + b*p[1] + c) / norm
            if dist < threshold:
                inliers.append(p)
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
            best_model = (a/norm, b/norm, c/norm)
    return best_model, best_inliers


# ============ 4. Lucas-Kanade Optical Flow ============

def lucas_kanade(img1, img2, points, window=5):
    """
    Lucas-Kanade optical flow at sparse points.
    img1, img2: two consecutive frames. points: list of (y, x).
    Returns flow vectors (dy, dx) for each point.
    """
    h, w = len(img1), len(img1[0])
    # spatial + temporal gradients
    flows = []
    for py, px in points:
        # local window gradients
        Ix_sum = Iy_sum = It_sum = 0.0
        Ixx = Iyy = Ixy = Ixt = Iyt = 0.0
        for dy in range(-window, window+1):
            for dx in range(-window, window+1):
                ny, nx = py+dy, px+dx
                if 0 <= ny < h-1 and 0 <= nx < w-1:
                    Ix = (img2[ny][nx+1] - img2[ny][nx-1]) / 2
                    Iy = (img2[ny+1][nx] - img2[ny-1][nx]) / 2
                    It = img2[ny][nx] - img1[ny][nx]
                    Ixx += Ix*Ix; Iyy += Iy*Iy; Ixy += Ix*Iy
                    Ixt += Ix*It; Iyt += Iy*It
        # Solve: [[Ixx, Ixy],[Ixy, Iyy]] @ [u, v] = -[Ixt, Iyt]
        det = Ixx*Iyy - Ixy*Ixy
        if abs(det) < 1e-6:
            flows.append((0.0, 0.0))
        else:
            u = (-Iyy*Ixt + Ixy*Iyt) / det
            v = (Ixy*Ixt - Ixx*Iyt) / det
            flows.append((u, v))
    return flows


# ============ Demo ============

def demo():
    print("=" * 60)
    print("16-385 Computer Vision: HOG, Harris, RANSAC, LK")
    print("=" * 60)
    random.seed(42)

    # --- 1. HOG ---
    print("\n📋 1. HOG Descriptor")
    # 12×12 image with a vertical edge
    image = [[0]*6 + [255]*6 for _ in range(12)]
    hog = compute_hog(image, cell_size=3, n_bins=9)
    print(f"   Image: 12×12 (vertical edge at col 5/6)")
    print(f"   HOG descriptor length: {len(hog)}")
    print(f"   First block (9 bins): [{', '.join(f'{v:.3f}' for v in hog[:9])}]")
    print(f"   💡 边缘在 0°/180° 方向梯度最大 → histogram 集中在 bin 0 或 8")

    # --- 2. Harris Corner ---
    print("\n📋 2. Harris Corner Detection")
    # 10×10 image with a corner (L-shape)
    corner_img = [[0]*10 for _ in range(10)]
    for i in range(5, 10):
        for j in range(10):
            corner_img[i][j] = 255
        corner_img[i][5] = 255
    corners, max_r = harris_corners(corner_img, k=0.04, threshold=0.1)
    print(f"   Image: 10×10 with L-shaped bright region")
    print(f"   Max Harris response: {max_r:.0f}")
    print(f"   Detected {len(corners)} corner points")
    if corners:
        print(f"   Strongest: {max(corners, key=lambda c: c[2])}")
    print(f"   💡 Harris 检测两个主梯度方向都大的点 = 角点")

    # --- 3. RANSAC ---
    print("\n📋 3. RANSAC Line Fitting")
    # Points on line y = 2x + 1, plus outliers
    inlier_pts = [(x, 2*x + 1 + random.gauss(0, 0.2)) for x in range(20)]
    outlier_pts = [(random.uniform(0, 20), random.uniform(0, 45)) for _ in range(15)]
    all_pts = inlier_pts + outlier_pts
    random.shuffle(all_pts)
    model, inliers = ransac_line(all_pts, n_iters=100, threshold=1.0)
    print(f"   True line: y = 2x + 1 (20 inliers, 15 outliers)")
    if model:
        a, b, c = model
        # convert to slope-intercept
        slope = -a/b if abs(b) > 1e-6 else float('inf')
        intercept = -c/b if abs(b) > 1e-6 else 0
        print(f"   RANSAC found: y = {slope:.2f}x + {intercept:.2f}")
    print(f"   Inliers found: {len(inliers)}/35 (expected ~20)")
    print(f"   💡 RANSAC 在 {len(outlier_pts)} 个 outlier 中仍能拟合真线（鲁棒性）")

    # --- 4. Lucas-Kanade ---
    print("\n📋 4. Lucas-Kanade Optical Flow")
    # Two frames: object shifted right by 1 pixel
    img1 = [[0]*10 for _ in range(10)]
    for i in range(3,7):
        for j in range(3,7):
            img1[i][j] = 200
    img2 = [row[:] for row in img1]
    for i in range(3,7):
        for j in range(4,8):
            img2[i][j] = 200
        img2[i][3] = 0
    pts = [(5, 5), (3, 4), (4, 3)]
    flows = lucas_kanade(img1, img2, pts, window=2)
    print(f"   Frame shift: object moved right by 1 pixel")
    for (py,px), (du,dv) in zip(pts, flows):
        print(f"   Point ({py},{px}): flow = ({du:.2f}, {dv:.2f})")
    print(f"   💡 LK 假设局部恒定亮度 + 小运动 → 求解 A^T A u = A^T b")

    print("\n✅ 16-385 Computer Vision 完成！")
    print("   覆盖：HOG / Harris Corner / RANSAC / Lucas-Kanade")


if __name__ == "__main__":
    demo()
