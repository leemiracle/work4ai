"""
讲透数值线代 01 章实验：SVD + 条件数 + 低秩近似。
"""
import numpy as np


def hilbert_matrix(n):
    """n×n Hilbert 矩阵（经典病态）"""
    H = np.array([[1.0 / (i + j + 1) for j in range(n)] for i in range(n)])
    return H


def part1_hilbert_condition():
    print("=" * 65)
    print("[1] Hilbert 矩阵的条件数（经典病态）")
    print("=" * 65)
    print(f"  {'n':<4} {'cond(H)':<20} {'是否病态'}")
    for n in [3, 5, 8, 10, 12, 15]:
        H = hilbert_matrix(n)
        kappa = np.linalg.cond(H)
        status = "灾难" if kappa > 1e15 else ("病态" if kappa > 1e6 else "OK")
        print(f"  {n:<4} {kappa:<20.2e} {status}")


def part2_svd_low_rank():
    """SVD 低秩近似"""
    print()
    print("=" * 65)
    print("[2] SVD 低秩近似：rank-k 近似误差")
    print("=" * 65)
    # 构造一个 rank=3 的矩阵 + 噪声
    np.random.seed(0)
    A_true = np.random.randn(20, 3) @ np.random.randn(3, 15)
    A = A_true + 0.1 * np.random.randn(20, 15)
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    print(f"  奇异值（前 8 个）：{s[:8].round(3)}")
    print(f"  → 前 3 个大，后面是噪声")
    print(f"\n  {'k':<4} {'||A - A_k||_F':<16} {'捕获能量 %'}")
    for k in [1, 2, 3, 5, 10, 15]:
        A_k = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
        err = np.linalg.norm(A - A_k, 'fro')
        energy = 1 - err**2 / np.linalg.norm(A, 'fro')**2
        print(f"  {k:<4} {err:<16.4f} {energy*100:.2f}%")


def part3_lora_demonstration():
    """LoRA 思想：低秩更新"""
    print()
    print("=" * 65)
    print("[3] LoRA 思想：低秩微调大矩阵")
    print("=" * 65)
    # 原 W（100×100，模拟 LLM 权重）
    W = np.random.randn(100, 100) * 0.1
    # 微调 ΔW（假设是低秩）
    true_rank = 4
    B_true = np.random.randn(100, true_rank) * 0.01
    A_true = np.random.randn(true_rank, 100) * 0.01
    delta_true = B_true @ A_true
    # 训练后：W_new = W + ΔW
    W_new = W + delta_true
    delta = W_new - W
    U, s, Vt = np.linalg.svd(delta)
    print(f"  ΔW = W_new - W 的奇异值：{s[:8].round(4)}")
    print(f"  → 前 {true_rank} 个奇异值大，之后 ≈ 0（低秩）")
    print(f"  → LoRA：只学 B, A（参数 100×4 + 4×100 = 800 vs 全量 100×100 = 10000）")


def part4_image_compression_demo():
    """模拟图像压缩（数字矩阵代替真图）"""
    print()
    print("=" * 65)
    print("[4] 图像压缩思想：截断 SVD 保留多少信息")
    print("=" * 65)
    np.random.seed(42)
    # 模拟"图"：50×50 矩阵，有结构
    x = np.linspace(0, 4*np.pi, 50)
    img = np.sin(x[:, None]) * np.cos(x[None, :]) + 0.5 * np.outer(x, x) / 1000
    U, s, Vt = np.linalg.svd(img)
    print(f"  50×50 '图像'，奇异值（前 10）：{s[:10].round(2)}")
    print(f"  {'k':<4} {'存储（vs 全量）':<18} {'能量保留 %'}")
    for k in [1, 2, 5, 10, 25, 50]:
        energy = (s[:k]**2).sum() / (s**2).sum() * 100
        storage = (50*k + k + k*50) / (50*50) * 100  # U[:,:k] + Σ + Vt[:k,:]
        print(f"  {k:<4} {storage:<18.1f} {energy:.2f}%")


def main():
    print("讲透数值线代 01 章实验：SVD + 条件数 + 低秩近似")
    part1_hilbert_condition()
    part2_svd_low_rank()
    part3_lora_demonstration()
    part4_image_compression_demo()
    print()
    print("=" * 65)
    print("✓ SVD 核心验证。")
    print("  → Hilbert 矩阵条件数随 n 爆炸")
    print("  → 截断 SVD = 最佳低秩近似")
    print("  → LoRA / PCA / 压缩都基于 SVD")
    print("=" * 65)


if __name__ == "__main__":
    main()
