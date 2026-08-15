"""
02_motion_estimation.py
=======================
视频压缩核心算法：块匹配运动估计（Block Matching Motion Estimation）。

视频相邻帧 99% 像素相同 → 不重新编码，只记录"从哪里搬来 + 残差"。
这就是 P 帧和 B 帧的基础，是 H.264/265/AV1 都用的核心算法。

本文件实现：
1. 全搜索（Full Search, 最准但慢）
2. 菱形搜索（Diamond Search, H.263 用，速度快）
3. 演示残差远小于原图（这就是能压缩的原因）
"""
import numpy as np


def sad(a, b):
    """Sum of Absolute Differences - 块匹配代价函数"""
    return np.sum(np.abs(a.astype(np.int32) - b.astype(np.int32)))


def satd(a, b):
    """Sum of Absolute Transformed Difference (Hadamard) - 更准但慢"""
    d = a.astype(np.int32) - b.astype(np.int32)
    # 2D Hadamard
    def hadamard(x):
        h = np.array([[1, 1], [1, -1]])
        # 扩到 8×8 递归构造
        H = np.ones_like(x)
        n = x.shape[0]
        # 简化：用 scipy
        from scipy.linalg import hadamard as hd
        H = hd(n)
        return H @ x @ H.T / n
    return np.sum(np.abs(hadamard(d)))


def full_search(cur, ref, block_pos, block_size=16, search_range=8):
    """全搜索：在 ±search_range 范围内每个位置都试。最准但慢。"""
    by, bx = block_pos
    cur_block = cur[by:by + block_size, bx:bx + block_size]
    best_cost = float('inf')
    best_mv = (0, 0)
    for dy in range(-search_range, search_range + 1):
        for dx in range(-search_range, search_range + 1):
            ry, rx = by + dy, bx + dx
            if ry < 0 or rx < 0 or ry + block_size > ref.shape[0] or rx + block_size > ref.shape[1]:
                continue
            ref_block = ref[ry:ry + block_size, rx:rx + block_size]
            cost = sad(cur_block, ref_block)
            if cost < best_cost:
                best_cost = cost
                best_mv = (dy, dx)
    return best_mv, best_cost


def diamond_search(cur, ref, block_pos, block_size=16, max_steps=20):
    """
    菱形搜索（Large Diamond Search Pattern, LDSP）。
    H.263 用的快速算法：从大菱形开始，逐渐缩小到小菱形。
    """
    by, bx = block_pos
    cur_block = cur[by:by + block_size, bx:bx + block_size]
    # 大菱形 8 个点（相对偏移）
    large_diamond = [(0, -2), (0, 2), (-2, 0), (2, 0),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]
    # 小菱形 4 个点（终止时确认）
    small_diamond = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    cy, cx = 0, 0  # 当前最佳相对偏移
    for step in range(max_steps):
        # 大菱形
        best_cost = float('inf')
        best_off = (0, 0)
        for dy, dx in large_diamond:
            ny, nx = cy + dy, cx + dx
            ry, rx = by + ny, bx + nx
            if ry < 0 or rx < 0 or ry + block_size > ref.shape[0] or rx + block_size > ref.shape[1]:
                continue
            cost = sad(cur_block, ref[ry:ry + block_size, rx:rx + block_size])
            if cost < best_cost:
                best_cost = cost
                best_off = (dy, dx)
        if best_off == (0, 0):
            # 进入小菱形阶段
            for dy, dx in small_diamond:
                ny, nx = cy + dy, cx + dx
                ry, rx = by + ny, bx + nx
                if ry < 0 or rx < 0 or ry + block_size > ref.shape[0] or rx + block_size > ref.shape[1]:
                    continue
                cost = sad(cur_block, ref[ry:ry + block_size, rx:rx + block_size])
                if cost < best_cost:
                    best_cost = cost
                    best_off = (dy, dx)
            cy, cx = cy + best_off[0], cx + best_off[1]
            break
        cy, cx = cy + best_off[0], cx + best_off[1]
    return (cy, cx), best_cost


def make_synthetic_frames(H=64, W=64):
    """合成两帧：第二帧是第一帧整体偏移 (5, -3)"""
    np.random.seed(0)
    ref = (np.random.rand(H, W) * 255).astype(np.uint8)
    # 真值运动：dy=5, dx=-3
    cur = np.zeros_like(ref)
    cur[5:, :W - 3] = ref[:H - 5, 3:]
    # 加少量噪声
    cur = np.clip(cur.astype(np.int32) + np.random.randint(-5, 5, cur.shape), 0, 255).astype(np.uint8)
    return ref, cur, (5, -3)


if __name__ == "__main__":
    ref, cur, true_mv = make_synthetic_frames()
    print(f"[合成] 真值运动矢量: dy={true_mv[0]}, dx={true_mv[1]}")

    block_pos = (20, 20)
    print(f"\n[全搜索] 块位置 {block_pos}...")
    mv_fs, cost_fs = full_search(cur, ref, block_pos, block_size=16, search_range=8)
    print(f"  估计 MV = {mv_fs}  (cost={cost_fs})")

    print(f"\n[菱形搜索] 同位置...")
    mv_ds, cost_ds = diamond_search(cur, ref, block_pos, block_size=16)
    print(f"  估计 MV = {mv_ds}  (cost={cost_ds})")

    # 残差 vs 原块对比
    by, bx = block_pos
    cur_block = cur[by:by + 16, bx:bx + 16]
    ref_block_at_mv = ref[by + mv_fs[0]:by + mv_fs[0] + 16, bx + mv_fs[1]:bx + mv_fs[1] + 16]
    residual = cur_block.astype(np.int32) - ref_block_at_mv
    print(f"\n[压缩效果]")
    print(f"  原块 SAD:        {sad(cur_block, np.zeros_like(cur_block)):>8}")
    print(f"  运动补偿后残差:   {np.sum(np.abs(residual)):>8}")
    print(f"  压缩比: 残差/原 = {np.sum(np.abs(residual))/np.sum(cur_block.astype(np.int32))*100:.1f}%")
    print("  → 这就是 P 帧只需 I 帧 1/5 码率的原因")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        axes[0].imshow(ref, cmap='gray'); axes[0].set_title("reference frame")
        axes[1].imshow(cur, cmap='gray'); axes[1].set_title("current frame")
        axes[2].imshow(residual, cmap='gray'); axes[2].set_title(f"residual (after MV={mv_fs})")
        # 显示运动矢量场（多个块）
        mvs = []
        for by in range(0, 48, 16):
            for bx in range(0, 48, 16):
                mv, _ = full_search(cur, ref, (by, bx), 16, 8)
                mvs.append((by + 8, bx + 8, mv[0], mv[1]))
        axes[3].imshow(cur, cmap='gray', alpha=0.5)
        for y, x, dy, dx in mvs:
            axes[3].arrow(x, y, dx, dy, color='r', head_width=2)
        axes[3].set_title("motion vector field")
        for ax in axes: ax.axis('off')
        plt.tight_layout(); plt.savefig("motion_estimation.png", dpi=80); print("\n[saved] motion_estimation.png")
    except ImportError:
        pass
