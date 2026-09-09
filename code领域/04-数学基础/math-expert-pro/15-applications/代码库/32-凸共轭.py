"""凸共轭：Fenchel对偶与Moreau包络
================================
数学概念：凸共轭(Fenchel共轭) / Lagrangian对偶 / Moreau包络 / proximal算子 / 双共轭
应用领域：变分推断 / EM算法 / ADMM / 鲁棒优化 / 稀疏恢复(Lasso) / 强化学习
核心思想：凸共轭 f*(y) = sup_x[⟨x,y⟩ - f(x)] 是"用切线表示函数"的对偶。
  双共轭定理：f** = f（当f是闭凸函数）→ 完全可恢复
  Moreau分解：x = prox_f(x) + prox_{f*}(x) · σ（对偶proximal）
  proximal：prox_f(x) = argmin_z[f(z) + ½||z-x||²]（Lasso的核心算子）
  Lasso = min ½||Ax-b||² + λ||x||₁ → soft-thresholding = prox of L1
运行方式：python "32-凸共轭.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def fenchel_conjugate_numerical(f, x_range, y_range, n=200):
    """数值计算 Fenchel 共轭 f*(y) = sup_x[<x,y> - f(x)]。"""
    x = np.linspace(*x_range, n)
    fx = f(x)
    y_grid = np.linspace(*y_range, n)
    f_star = np.zeros_like(y_grid)
    for i, y in enumerate(y_grid):
        f_star[i] = np.max(y * x - fx)
    return y_grid, f_star

def soft_threshold(x, lam):
    """L1的proximal算子（软阈值）。prox_{λ|·|₁}(x) = sign(x)·max(|x|-λ, 0)"""
    return np.sign(x) * np.maximum(np.abs(x) - lam, 0)

def main():
    np.random.seed(42)
    print("="*60); print("实验 1：经典函数的凸共轭"); print("="*60)
    # f(x) = x²/2 → f*(y) = y²/2（自共轭！）
    f_quad = lambda x: x**2 / 2
    y1, fs1 = fenchel_conjugate_numerical(f_quad, (-5,5), (-5,5))
    # f(x) = |x| → f*(y) = 0 if |y|≤1, +∞ otherwise（指示函数）
    f_abs = lambda x: np.abs(x)
    y2, fs2 = fenchel_conjugate_numerical(f_abs, (-5,5), (-2,2))
    # f(x) = exp(x) → f*(y) = y log(y) - y (y>0)
    f_exp = lambda x: np.exp(x)
    y3, fs3 = fenchel_conjugate_numerical(f_exp, (-5,3), (-1,10))

    print("经典共轭对：")
    print(f"  f(x)=x²/2  ↔  f*(y)=y²/2   （自共轭！f**=f）")
    print(f"  f(x)=|x|   ↔  f*(y)=I(|y|≤1)（指示函数）")
    print(f"  f(x)=eˣ    ↔  f*(y)=y ln(y)-y（y>0）")
    print(f"  f(x)=I(x≥0)↔  f*(y)=0       （支撑函数 y≤0→0）")

    print("\n"+"="*60); print("实验 2：双共轭 f**=f（凸函数的自恢复）"); print("="*60)
    # 数值验证 f** = f
    _, f_star_vals = fenchel_conjugate_numerical(f_quad, (-5,5), (-5,5))
    x_check = np.linspace(-5, 5, 200)
    f_double_star = np.zeros_like(x_check)
    y_grid = np.linspace(-5, 5, 200)
    for i, xx in enumerate(x_check):
        f_double_star[i] = np.max(xx * y_grid - f_star_vals)
    max_err = np.max(np.abs(f_double_star - f_quad(x_check)))
    print(f"对 f(x)=x²/2 的双共轭验证：")
    print(f"  ||f**-f||_∞ = {max_err:.2e} {'✓ 恢复成功' if max_err < 0.1 else '≈ 近似恢复'}")

    print("\n"+"="*60); print("实验 3：Proximal算子——Lasso的核心"); print("="*60)
    x_test = np.linspace(-3, 3, 200)
    print("Lasso问题：min ½||Ax-b||² + λ||x||₁")
    print("解法 = 软阈值 soft_threshold(x, λ) = sign(x)·max(|x|-λ, 0)")
    print(f"\n{'λ':<8} {'输入x':<10} {'prox(x)':<10} {'效果'}")
    for lam in [0.0, 0.3, 0.5, 1.0, 2.0]:
        x_in = 1.5
        x_out = soft_threshold(np.array([x_in]), lam)[0]
        effect = "无变化" if lam==0 else f"压缩{lam}" if x_out>0 else "置零"
        print(f"{lam:<8.1f} {x_in:<10.2f} {x_out:<10.4f} {effect}")
    print(f"\n[解读] soft-thresholding = L1的proximal = Lasso的核心算子。")
    print(f"       小系数被'压缩到零' → 稀疏解。这就是 L1 正则化产生稀疏的原理。")

    print("\n"+"="*60); print("实验 4：Moreau分解——对偶proximal"); print("="*60)
    print("Moreau分解：x = prox_f(x) + prox_{f*}(x)")
    print("  → proximal 算子和对偶 proximal 互补")
    print("  → ADMM/分裂算法的理论基础")
    x_val = np.array([1.5, -0.8, 0.3, -2.0])
    lam = 0.5
    prox_f = soft_threshold(x_val, lam)
    # f*(y) = I(|y|≤1) 的 proximal = 投影到 [-1,1] 球
    prox_fstar = np.clip(x_val, -1, 1)
    reconstruction = prox_f + prox_fstar
    print(f"\n验证 Moreau 分解 (prox_{{λ|·|₁}} + prox_{{I_{{|·|≤1}}}} = x):")
    print(f"  x = {x_val}")
    print(f"  prox_L1(x) = {prox_f}")
    print(f"  prox_conj(x) = {prox_fstar}")
    print(f"  和 = {reconstruction}")
    print(f"  匹配 {'✓' if np.allclose(reconstruction, x_val) else '✗'}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax = axes[0,0]
    x_plot = np.linspace(-4, 4, 200)
    ax.plot(x_plot, x_plot**2/2, 'b-', lw=2, label='f(x)=x²/2')
    ax.plot(y1, fs1, 'r--', lw=2, label='f*(y)=y²/2（自共轭）')
    ax.set_xlabel('x / y'); ax.set_ylabel('f / f*')
    ax.set_title('凸共轭：f(x)=x²/2 ↔ f*(y)=y²/2'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[0,1]
    ax.plot(x_plot, np.abs(x_plot), 'b-', lw=2, label='f(x)=|x|')
    ax.plot(y2, fs2, 'r--', lw=2, label='f*(y)=I(|y|≤1)')
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('x / y'); ax.set_ylabel('f / f*')
    ax.set_title('凸共轭：f(x)=|x| ↔ f*(y)=I(|y|≤1)'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,0]
    for lam, color in [(0.0,'gray'), (0.3,'green'), (0.5,'blue'), (1.0,'red'), (2.0,'purple')]:
        ax.plot(x_plot, soft_threshold(x_plot, lam), color=color, lw=2, label=f'λ={lam}')
    ax.plot(x_plot, x_plot, 'k--', alpha=0.3, label='y=x')
    ax.set_xlabel('x'); ax.set_ylabel('prox_{λ|·|₁}(x)')
    ax.set_title('软阈值函数 = L1 的 proximal 算子'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axes[1,1]
    ax.bar(range(len(x_val)), x_val, alpha=0.3, color='gray', label='原始 x')
    ax.bar(range(len(x_val)), prox_f, alpha=0.7, color='red', label='prox_L1(x)（稀疏）')
    ax.set_xlabel('分量'); ax.set_ylabel('值')
    ax.set_title(f'Proximal 算子产生稀疏（λ={lam}）'); ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("32-凸共轭_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 32-凸共轭_结果.png")
    print("\n[总结] 1. 凸共轭f*=sup[<x,y>-f(x)]=函数的切线表示")
    print("2. f**=f(双共轭恢复)=凸分析的核心定理")
    print("3. proximal=近端算子=Lasso/ADMM/变分推断的核心")
    print("4. soft-threshold=L1的proximal=稀疏化的原理")

if __name__ == "__main__": main()
