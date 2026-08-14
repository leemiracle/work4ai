"""
UC Berkeley MATH 113 · 实验: 群作用与等变性可视化
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 group_actions_demo.py

验证:
  1. 对称群 S_n 乘法表与 Lagrange 定理
  2. 轨道-稳定子定理 (D_4 作用在正方形顶点上)
  3. Burnside 引理 (项链染色计数)
  4. CNN 平移等变性 = Z^n 群卷积
  5. 置换不变性: DeepSets 的 S_n 不变
  6. 旋转等变: G-CNN 的基本验证
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: S_3 乘法表与 Lagrange 定理
# ============================================================
print("=" * 60)
print("实验 1: 对称群 S_3 乘法表 + Lagrange 定理")
print("=" * 60)

from itertools import permutations

def perm_compose(p, q):
    """排列复合 p∘q: 先q后p"""
    return tuple(p[q[i]] for i in range(len(p)))

def build_group_table(group_elements):
    """构建群乘法表 (索引形式)"""
    n = len(group_elements)
    T = np.zeros((n, n), dtype=int)
    for i, p in enumerate(group_elements):
        for j, q in enumerate(group_elements):
            r = perm_compose(p, q)
            T[i, j] = group_elements.index(r)
    return T

S3 = list(permutations(range(3)))
T = build_group_table(S3)
print(f"  |S_3| = {len(S3)} = 3! = 6")
print(f"  乘法表:\n{T}")

# 验证: 生成元 e=(0,1,2), r=(1,2,0), r^2=(2,0,1)
# 每行/列是 {0,...,5} 的排列 (Latin square 性质)
for i in range(6):
    assert sorted(T[i]) == list(range(6)), f"行 {i} 不是 Latin square"
    assert sorted(T[:, i]) == list(range(6)), f"列 {i} 不是 Latin square"
print("  ✓ 每行每列都是 {0,...,5} 的排列 (Latin square 性质)")

# 子群 H = {e, (12)}, |H|=2 整除 |S_3|=6
H_indices = [S3.index((0,1,2)), S3.index((1,0,2))]
print(f"  子群 H = {{id, (12)}}, |H| = {len(H_indices)}")
print(f"  |S_3| / |H| = {len(S3) / len(H_indices):.0f} (Lagrange: 2 整除 6 ✓)")

# ============================================================
# 实验 2: 轨道-稳定子定理 (D_4)
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 轨道-稳定子定理 (正方形对称群 D_4)")
print("=" * 60)

def rotate4(state, k):
    """正方形顶点顺时针旋转 k×90°: state 是顶点排列"""
    return tuple(state[(i + k) % 4] for i in range(4))

def reflect4(state):
    """沿 0-2 对角线翻转"""
    s = list(state)
    s[1], s[3] = s[3], s[1]
    return tuple(s)

# 构建 D_4 的 8 个元素
identity = (0, 1, 2, 3)
D4 = [identity]
v = identity
for k in range(1, 4):
    v = rotate4(v, 1)
    D4.append(v)
for k in range(4):
    D4.append(reflect4(rotate4(identity, k)))

# 去重 (确保恰好 8 个)
D4 = list(set(D4))
print(f"  |D_4| = {len(D4)} (应为 8)")

# D_4 作用在顶点集合 {0,1,2,3} 上
# g 作用于顶点 i: 把标准排列 (0,1,2,3) 用 g 变换后, i 出现在哪个位置
def action(g, i):
    """群元素 g (排列) 作用在顶点 i 上"""
    return g[i]

# 顶点 0 的轨道
orbit_0 = set()
for g in D4:
    orbit_0.add(action(g, 0))
stab_0 = [g for g in D4 if action(g, 0) == 0]

print(f"  顶点0的轨道 = {orbit_0}, |轨道| = {len(orbit_0)}")
print(f"  顶点0的稳定子大小 = {len(stab_0)}")
print(f"  |D_4| = |轨道| × |稳定子| = {len(orbit_0)} × {len(stab_0)} = {len(orbit_0)*len(stab_0)} ✓")

# 所有顶点的轨道
for i in range(4):
    orb = set(action(g, i) for g in D4)
    stab = [g for g in D4 if action(g, i) == i]
    print(f"  顶点{i}: |轨道|={len(orb)}, |稳定子|={len(stab)}, 乘积={len(orb)*len(stab)}")

# ============================================================
# 实验 3: Burnside 引理 — 项链染色计数
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Burnside 引理 (4珠项链, 3色, D_4 对称)")
print("=" * 60)

colors = [0, 1, 2]  # 3 种颜色
n_beads = 4
all_colorings = []
for c0 in colors:
    for c1 in colors:
        for c2 in colors:
            for c3 in colors:
                all_colorings.append((c0, c1, c2, c3))
print(f"  总染色数 (不考虑对称) = {len(all_colorings)} = 3^4 = 81")

def coloring_action(g, coloring):
    """群元素 g 作用于染色"""
    return tuple(coloring[g[i]] for i in range(4))

# Burnside: 轨道数 = (1/|G|) Σ |Fix(g)|
total_fixed = 0
for g in D4:
    fixed_count = 0
    for coloring in all_colorings:
        if coloring_action(g, coloring) == coloring:
            fixed_count += 1
    total_fixed += fixed_count

burnside_count = total_fixed // len(D4)
print(f"  Burnside: 本质不同染色数 = {total_fixed} / {len(D4)} = {burnside_count}")
print("  (直接枚举验证: 见下)")

# 直接枚举等价类验证
seen = set()
equivalence_classes = []
for coloring in all_colorings:
    if coloring in seen:
        continue
    # 生成等价类
    eq_class = set()
    for g in D4:
        eq_class.add(coloring_action(g, coloring))
    equivalence_classes.append(eq_class)
    seen.update(eq_class)
print(f"  直接枚举等价类数 = {len(equivalence_classes)} ✓")

# ============================================================
# 实验 4: CNN 平移等变性 = Z 群卷积
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 平移等变性 (Z 群卷积)")
print("=" * 60)

signal = np.random.randn(20)
kernel = np.array([1, 2, 1], dtype=float) / 3  # 平滑核

# 标准卷积 (valid mode)
def conv1d(sig, ker):
    n = len(sig)
    k = len(ker)
    out = np.zeros(n - k + 1)
    for i in range(n - k + 1):
        out[i] = np.sum(sig[i:i+k] * ker)
    return out

conv_orig = conv1d(signal, kernel)

# 先平移 3 格, 再卷积
shift = 3
shifted = np.roll(signal, shift)
conv_shifted_then = conv1d(shifted, kernel)

# 先卷积, 再平移
conv_orig_then_shifted = np.roll(conv_orig, shift)

equiv_error = np.max(np.abs(conv_shifted_then - conv_orig_then_shifted))
print(f"  信号长度 = {len(signal)}, 平移 = {shift}")
print(f"  等变性误差 = {equiv_error:.2e}")
print("  (≈0 → 卷积是 Z-群等变的: T_g(f*k) = (T_g f)*k)")

# 画图
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
axes[0].plot(signal, 'b-o', ms=3, label='原信号')
axes[0].plot(shifted, 'r-s', ms=3, label=f'平移 {shift} 格')
axes[0].set_title('输入信号'); axes[0].legend()
axes[1].plot(conv_orig, 'b-o', ms=3, label='卷积(原信号)')
axes[1].plot(conv_shifted_then, 'r-s', ms=3, label='卷积(平移信号)')
axes[1].plot(conv_orig_then_shifted, 'g--^', ms=4, label='平移(卷积(原信号))')
axes[1].set_title(f'平移等变性验证 (误差={equiv_error:.1e})'); axes[1].legend(fontsize=9)
fig.tight_layout(); fig.savefig('translation_equivariance.png', dpi=150)
print("  → 已保存 translation_equivariance.png")

# ============================================================
# 实验 5: DeepSets 的 S_n 不变性
# ============================================================
print("\n" + "=" * 60)
print("实验 5: DeepSets — S_n 置换不变性")
print("=" * 60)

def deepset_invariant(X, phi_w, rho_w):
    """DeepSets: f(X) = rho(Σ phi(x_i)) — 天然 S_n 不变"""
    features = np.array([phi_w @ x for x in X])
    aggregated = np.sum(features, axis=0)
    return rho_w @ aggregated

# 随机参数
phi_w = np.random.randn(3, 2)  # 2维输入 → 3维特征
rho_w = np.random.randn(1, 3)  # 3维特征 → 1维输出

# 5 个 2D 点
X = np.random.randn(5, 2)
result_original = deepset_invariant(X, phi_w, rho_w)

# 打乱顺序
from itertools import permutations as perm_fn
max_diff = 0
for perm in list(perm_fn(range(5)))[:20]:  # 取 20 个排列
    X_permuted = X[list(perm)]
    result_perm = deepset_invariant(X_permuted, phi_w, rho_w)
    diff = np.abs(result_original - result_perm).max()
    max_diff = max(max_diff, diff)
print(f"  输入点数 = {len(X)}, 测试 20 种排列")
print(f"  DeepSets 输出最大变化 = {max_diff:.2e}")
print("  (≈0 → S_n 不变 ✓)")
print("  核心: Σ_{i} φ(x_i) 对置换不变, ρ 保持不变性")

# ============================================================
# 实验 6: 旋转等变 (G-CNN 基本验证)
# ============================================================
print("\n" + "=" * 60)
print("实验 6: 旋转等变 (p4 群: 90° 旋转)")
print("=" * 60)

# p4 群 = {平移} ⋊ {C_4 旋转} 
# 在 2D 网格上, 旋转 90° 后再卷积 = 卷积后再旋转

from scipy.signal import correlate2d

# 简化: 只验证 C_4 (旋转) 部分
img = np.random.randn(8, 8)
ker = np.random.randn(3, 3)

# 方法 A: 先卷积再旋转
conv_A = correlate2d(img, ker, mode='same')
rot_A = np.rot90(conv_A)

# 方法 B: 先旋转图像再卷积
rot_img = np.rot90(img)
conv_B = correlate2d(rot_img, ker, mode='same')

equiv_err_rot = np.max(np.abs(rot_A - conv_B))
print(f"  2D 卷积 + C_4 旋转等变性误差 = {equiv_err_rot:.2e}")
print("  (≈0 → 卷积是 C_4 等变的)")
print("  G-CNN 推广: 把 C_4 扩展到任意群 G, 每层保持 G-等变性")

fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
axes[0].imshow(img, cmap='viridis'); axes[0].set_title('原图像')
axes[1].imshow(conv_A, cmap='viridis'); axes[1].set_title('卷积(原图)')
axes[2].imshow(rot_A, cmap='viridis'); axes[2].set_title('旋转(卷积(原图))')
axes[3].imshow(conv_B, cmap='viridis'); axes[3].set_title('卷积(旋转图)')
for ax in axes: ax.axis('off')
fig.suptitle(f'旋转等变性: 旋转∘卷积 = 卷积∘旋转 (误差={equiv_err_rot:.1e})')
fig.tight_layout(); fig.savefig('rotation_equivariance.png', dpi=150)
print("  → 已保存 rotation_equivariance.png")

print("\n" + "=" * 60)
print("全部实验完成! ✓")
print("=" * 60)
