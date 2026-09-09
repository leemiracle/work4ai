"""
PCA 特征值分解与人脸图像压缩
============================
数学概念：特征值分解 (EVD) / 主成分分析 (PCA) / 低秩近似
应用领域：图像压缩、人脸识别、数据降维
核心思想：对高维数据协方差矩阵做特征值分解，保留方差最大的前 k 个主成分，
         即可将数据投影到低维子空间实现压缩与重建。最优低秩近似由 Eckart-Young 定理保证。
运行方式：python "01-PCA特征值_人脸压缩.py"
依赖：numpy, matplotlib, scikit-learn (可选, 提供真实人脸数据)
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------- 全局设置：中文显示 ----------
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 数据生成 / 加载 ============
def load_faces(n_faces=200, h=64, w=64):
    """加载人脸数据。优先用 sklearn 真实数据；失败则用随机合成数据。"""
    try:
        from sklearn.datasets import fetch_olivetti_faces

        data = fetch_olivetti_faces(shuffle=True, random_state=42)
        faces = data.data[:n_faces]  # (n, 4096) 已归一化到 [0,1]
        h = w = 64
        print(f"[Olivetti] 加载 {faces.shape[0]} 张真实人脸, 每张维度 {faces.shape[1]}")
    except Exception:
        # 合成人脸：低频噪声 + 椭圆轮廓，模拟人脸大致结构
        rng = np.random.RandomState(0)
        yy, xx = np.mgrid[0:h, 0:w]
        cy, cx = h / 2, w / 2
        mask = ((yy - cy) / cy) ** 2 + ((xx - cx) / (cx * 0.8)) ** 2 < 1
        faces = []
        for _ in range(n_faces):
            base = np.zeros((h, w))
            base[mask] = 0.3 + 0.5 * np.random.rand()
            # 加入低频结构（模拟五官）
            for _ in range(5):
                r0, c0 = np.random.randint(0, h), np.random.randint(0, w)
                base[r0, c0] = np.random.rand()
            base = np.clip(base + 0.05 * np.random.randn(h, w), 0, 1)
            faces.append(base.ravel())
        faces = np.array(faces)
        print(f"[合成] 生成 {n_faces} 张合成人脸, 每张维度 {h * w}")
    return faces, h, w


# ============ 2. 数学建模：PCA (特征值分解) ============
def pca_fit(X, k):
    """
    用特征值分解实现 PCA。
    1) 中心化：去均值
    2) 计算协方差矩阵 C = X^T X / n
    3) 特征值分解 C = V Λ V^T
    4) 取前 k 大特征值对应特征向量（主成分）
    返回：主成分矩阵 V_k, 均值, 特征值 (降序)
    """
    mean = X.mean(axis=0)
    Xc = X - mean
    # 使用 SVD 等价求解，数值更稳定 (奇异值 = 特征值的开方)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    eigvals = (S ** 2) / (X.shape[0] - 1)          # 特征值 (方差)
    V_k = Vt[:k]                                    # 前 k 个主成分 (k, d)
    return V_k, mean, eigvals


def pca_reconstruct(X, V_k, mean):
    """将数据投影到主成分子空间再重建：X_hat = (X-μ)V_k V_k^T + μ"""
    Xc = X - mean
    proj = Xc @ V_k.T          # 编码 (n, k)
    return proj @ V_k + mean    # 重建 (n, d)


# ============ 3. 可视化与结果分析 ============
def main():
    X, h, w = load_faces(n_faces=200)
    Ks = [1, 5, 10, 20, 50, 100, 200]              # 不同主成分个数
    errors = []
    for k in Ks:
        V_k, mean, eigvals = pca_fit(X, k)
        X_hat = pca_reconstruct(X, V_k, mean)
        # 相对重建误差 (Frobenius 范数)
        err = np.linalg.norm(X - X_hat) / np.linalg.norm(X)
        errors.append(err)
        print(f"k={k:3d} | 方差解释率={eigvals[:k].sum()/eigvals.sum()*100:5.1f}% | "
              f"重建误差={err:.4f} | 压缩比={X.shape[1]/k:.1f}x")

    # ---- 绘图：方差解释曲线 + 重建误差曲线 ----
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax = axes[0]
    cum_var = np.cumsum(eigvals) / eigvals.sum()
    ax.plot(cum_var, "b.-", lw=1.2)
    ax.axhline(0.95, color="r", ls="--", label="95% 方差")
    ax.set_xlabel("主成分个数 k")
    ax.set_ylabel("累计方差解释率")
    ax.set_title("PCA 累计方差解释率")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(Ks, errors, "ro-", lw=1.2)
    ax.set_xlabel("主成分个数 k")
    ax.set_ylabel("相对重建误差")
    ax.set_title("人脸重建误差 vs 主成分数")
    ax.set_xscale("log")
    ax.grid(alpha=0.3)

    # ---- 展示原始与重建人脸 ----
    ax = axes[2]
    V_k, mean, _ = pca_fit(X, 50)
    X_hat = pca_reconstruct(X, V_k, mean)
    combined = np.zeros((2 * h + 8, 3 * w + 8))  # 行数需 ≥ 2h+6 以装下两行图片
    for j in range(3):
        combined[2:h + 2, j * (w + 4):j * (w + 4) + w] = X[j].reshape(h, w)
        combined[h + 6:2 * h + 6, j * (w + 4):j * (w + 4) + w] = X_hat[j].reshape(h, w)
    ax.imshow(combined, cmap="gray")
    ax.set_title("上: 原始人脸  |  下: k=50 重建")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig("01-PCA_结果.png", dpi=120)
    print("\n[结果] 图像已保存: 01-PCA_结果.png")
    print("[解读] 仅用约 50 个主成分(维度从 4096 降至 50, 压缩 80x)即可很好重建人脸, "
          "验证了 PCA 在人脸数据上的高效降维能力。")


if __name__ == "__main__":
    main()
