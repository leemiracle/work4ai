"""实验2: Leslie 矩阵模型 —— 年龄结构种群动态
验证: 主特征值 λ1 = 渐近增长率; 对应特征向量 = 稳定年龄分布。
用濒危物种假想数据演示弹性分析(保护哪个年龄阶段最有效)。
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 假想: 一种长寿哺乳动物(如海龟/鲸) 4个年龄组
# 列: [幼体(0-1), 亚成体(1-2), 成体(2-3), 老成体(3+)]
F = np.array([0.0, 0.5, 8.0, 10.0])      # 各龄生育力
S = np.array([0.4, 0.6, 0.85, 0.7])      # 各龄存活率(最后1个=老成体留级率)

# 构建 Leslie 矩阵
n = 4
L = np.zeros((n, n))
L[0, :] = F
for i in range(1, n):
    L[i, i-1] = S[i-1]

print("Leslie 矩阵 L =\n", L)

# 特征值分解
eigvals, eigvecs = np.linalg.eig(L)
idx = np.argmax(np.real(eigvals))
lam1 = np.real(eigvals[idx])
print(f"\n主特征值 λ1 = {lam1:.4f}  ({'增长' if lam1>1 else '稳定' if lam1==1 else '衰减!'})")

# 稳定年龄分布(右特征向量归一化)
stable_age = np.real(eigvecs[:, idx])
stable_age = stable_age / stable_age.sum()
print(f"稳定年龄分布 = {stable_age.round(4)}")

# 再生值(左特征向量 = 右特征向量 of L.T)
_, left_eigvecs = np.linalg.eig(L.T)
repro = np.real(left_eigvecs[:, idx])
repro = repro / repro.max()
print(f"再生值(相对) = {repro.round(4)}  <- 哪个年龄对未来贡献最大")

# 弹性分析: e_ij = (∂λ/∂a_ij)*(a_ij/λ) = (v_i * x_j * a_ij)/(λ * <v,x>)
right = np.real(eigvecs[:, idx])
v = np.real(left_eigvecs[:, idx])
denom = v @ right
elasticity = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        elasticity[i, j] = (v[i] * right[j] * L[i, j]) / (lam1 * denom)
print(f"\n弹性矩阵 =\n", elasticity.round(4))
col_sum = elasticity.sum(axis=0)
row_sum_fert = elasticity[0,:].sum()
row_sum_surv = elasticity[1:,:].sum()
print(f"\n各列(年龄)弹性贡献: {col_sum.round(4)}")
print(f"总生育弹性 = {row_sum_fert:.4f},  总存活/生长弹性 = {row_sum_surv:.4f}")
print(f"-> 保护启示: 弹性最大的年龄组是第 {np.argmax(col_sum)+1} 组, 应优先保护")

# 种群动态模拟
print("\n--- 100年种群模拟(初始: 幼体100) ---")
pop = np.array([100.0, 0.0, 0.0, 0.0])
N_history = []
for t in range(100):
    N_history.append(pop.sum())
    pop = L @ pop
N_history.append(pop.sum())
print(f"初始 N={N_history[0]:.0f}, 100年后 N={N_history[-1]:.1f}")
print(f"实际增长率(后段) = {(N_history[-1]/N_history[-20])**(1/20):.4f} (应≈λ1={lam1:.4f})")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(range(n), stable_age, color='teal')
axes[0].set_title(f'稳定年龄分布 (λ1={lam1:.3f})')
axes[0].set_xlabel('年龄组'); axes[0].set_ylabel('比例')
axes[1].plot(N_history, 'b-', lw=2)
axes[1].set_title('种群动态(初始幼体100) -> 渐近指数增长')
axes[1].set_xlabel('年'); axes[1].set_ylabel('总种群 N'); axes[1].set_yscale('log')
plt.tight_layout()
plt.savefig('/tmp/opencode/ecology/fig2_leslie.png', dpi=110)
print("\n图已保存: fig2_leslie.png")
