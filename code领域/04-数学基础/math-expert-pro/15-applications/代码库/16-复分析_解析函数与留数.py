import math
"""
复分析：解析函数、柯西定理与留数
================================
数学概念：复函数 / 解析函数 / 柯西积分定理 / 留数定理 / 定义域着色 / 保形映射
应用领域：信号处理 / 量子力学 / 流体力学 / 电磁学 / 数论
核心思想：复函数 f(z) 在解析区域有极其优美的性质——柯西定理说闭合路径积分为 0，
         留数定理说闭合积分 = 2πi × Σ留数。
  解析性：满足 Cauchy-Riemann 方程 ∂u/∂x = ∂v/∂y, ∂u/∂y = -∂v/∂x
  柯西定理：∮_C f(z)dz = 0（C 在解析区域内）
  柯西公式：f(z₀) = (1/2πi) ∮_C f(z)/(z-z₀) dz
  留数定理：∮_C f(z)dz = 2πi Σ Res(f, zₖ)
  定义域着色：用颜色编码复数值（色相=辐角，亮度=模）
运行方式：python "16-复分析_解析函数与留数.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 定义域着色（Domain Coloring）============

def domain_coloring(f, xmin=-3, xmax=3, ymin=-3, ymax=3, N=400):
    """定义域着色可视化复函数。
    色相 = arg(f(z))（辐角）
    亮度 = |f(z)| 的对数压缩（避免无穷大/零处的问题）
    """
    x = np.linspace(xmin, xmax, N)
    y = np.linspace(ymin, ymax, N)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    W = f(Z)  # 复函数值

    # 辐角 → 色相 [0, 1]
    hue = (np.angle(W) / (2 * np.pi)) % 1.0

    # 模 → 亮度（对数压缩 + 等值线）
    magnitude = np.abs(W)
    value = 1.0 - 1.0 / (1.0 + 0.3 * np.log(magnitude + 1))
    # 添加模的等值线
    value *= 0.7 + 0.3 * (np.log(magnitude + 1e-10) % 1.0 < 0.3)

    saturation = np.ones_like(hue) * 0.9

    hsv = np.stack([hue, saturation, value], axis=-1)
    rgb = hsv_to_rgb(hsv)
    return X, Y, rgb


# ============ 2. 留数计算 ============

def residue_simple_pole(f_coeff, z0):
    """计算一阶极点的留数：Res(f, z0) = lim_{z→z0} (z-z0)f(z)
    对于 f(z) = g(z) / (z - z0)，Res = g(z0)
    """
    return f_coeff(z0)


def numerical_contour_integral(f, z0, r, n=1000):
    """数值计算圆路径积分 ∮ f(z)dz，路径为以 z0 为心半径 r 的圆。
    用于验证柯西定理和留数定理。
    """
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    dtheta = 2 * np.pi / n
    z = z0 + r * np.exp(1j * theta)
    dz = 1j * r * np.exp(1j * theta) * dtheta
    integral = np.sum(f(z) * dz)
    return integral


# ============ 3. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：定义域着色——看复函数的「面孔」")
    print("=" * 60)

    # 定义几个经典复函数
    functions = {
        'f(z) = z': lambda z: z,
        'f(z) = z²': lambda z: z**2,
        'f(z) = 1/z': lambda z: 1.0 / (z + 1e-30),
        'f(z) = e^z': lambda z: np.exp(z),
        'f(z) = sin(z)': lambda z: np.sin(z),
        'f(z) = (z²-1)/(z²+1)': lambda z: (z**2 - 1) / (z**2 + 1 + 1e-30),
    }

    print("定义域着色编码：")
    print("  色相 = arg(f(z))（辐角）—— 红色=正实轴方向")
    print("  亮度 = |f(z)|（模）—— 亮=大，暗=小")
    print("\n关键特征：")
    print("  零点：所有颜色汇聚的点（色相环绕一次）")
    print("  极点：所有颜色汇聚但方向相反（色相逆环绕）")

    print("\n" + "=" * 60)
    print("实验 2：柯西积分定理验证")
    print("=" * 60)

    # f(z) = z² 在 z=0 附近解析
    # 柯西定理：∮ z² dz = 0（任意闭合路径）

    f_analytic = lambda z: z**2
    z0, r = 0, 1.0
    integral_analytic = numerical_contour_integral(f_analytic, z0, r)

    print(f"f(z) = z² 在以 z₀={z0}, r={r} 的圆路径上积分：")
    print(f"  ∮ z² dz = {integral_analytic:.6f}")
    print(f"  理论值 = 0（柯西定理）{'✓' if abs(integral_analytic) < 0.01 else '✗'}")

    # f(z) = 1/z 有极点（非解析）
    f_pole = lambda z: 1.0 / (z + 1e-30)
    integral_pole = numerical_contour_integral(f_pole, z0, r)

    print(f"\nf(z) = 1/z 在以 z₀={z0}, r={r} 的圆路径上积分（包围极点）：")
    print(f"  ∮ (1/z) dz = {integral_pole:.6f}")
    print(f"  理论值 = 2πi = {2j * np.pi:.6f}")
    print(f"  匹配 {'✓' if abs(integral_pole - 2j*np.pi) < 0.1 else '✗'}")
    print(f"  留数 Res(1/z, 0) = 1")

    print("\n" + "=" * 60)
    print("实验 3：留数定理——计算实积分的利器")
    print("=" * 60)

    # 计算 I = ∫_{-∞}^{∞} dx / (1 + x²)
    # 解析延拓 f(z) = 1/(1+z²) = 1/((z-i)(z+i))
    # 上半平面极点 z = i，留数 Res = 1/(2i)
    # I = 2πi × Res = 2πi × 1/(2i) = π

    print("计算 I = ∫_{-∞}^{∞} dx / (1 + x²)")
    print("\n步骤：")
    print("  1. 解析延拓 f(z) = 1/(1+z²) = 1/((z+i)(z-i))")
    print("  2. 上半平面极点：z = i")
    print("  3. 留数 Res(f, i) = lim_{z→i} (z-i)f(z) = 1/(2i)")
    print("  4. I = 2πi × 1/(2i) = π")

    # 数值验证
    x_real = np.linspace(-100, 100, 100000)
    I_numerical = np.trapz(1.0 / (1 + x_real**2), x_real)
    print(f"\n数值验证：∫dx/(1+x²) ≈ {I_numerical:.6f}")
    print(f"理论值 π = {np.pi:.6f}")
    print(f"误差 = {abs(I_numerical - np.pi):.2e}")

    print("\n[解读] 留数定理把实积分变成代数运算——这是复分析的威力。")
    print("       很多物理问题（电磁场/量子散射/流体）都靠留数定理求解。")

    print("\n" + "=" * 60)
    print("实验 4：解析函数的性质——幂级数展开")
    print("=" * 60)

    print("解析函数的惊人性质：知道一点的信息 = 知道全域信息")
    print()
    print("f(z) = e^z 的泰勒展开（在 z₀=0）：")
    for n in range(7):
        coeff = 1.0 / math.factorial(n) if hasattr(np, 'math') else 1.0 / math.factorial(n)
        term = f"z^{n}/{n}!" if n > 0 else "1"
        print(f"  n={n}: {term} = {1.0/math.factorial(n):.6f}")

    # 数值验证 e^z 的泰勒级数
    z_test = 0.5
    taylor_sum = sum(z_test**n / math.factorial(n) for n in range(20))
    exact = np.exp(z_test)
    print(f"\n在 z={z_test} 处：")
    print(f"  泰勒级数（20项）= {taylor_sum:.10f}")
    print(f"  e^z 精确值     = {exact:.10f}")
    print(f"  误差 = {abs(taylor_sum - exact):.2e}")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    for idx, (name, f) in enumerate(functions.items()):
        ax = axes[idx // 3, idx % 3]
        X, Y, rgb = domain_coloring(f, N=300)
        ax.imshow(rgb, extent=[-3, 3, -3, 3], origin='lower')
        ax.set_title(name, fontsize=12)
        ax.set_xlabel('Re(z)')
        ax.set_ylabel('Im(z)')

    plt.tight_layout()
    plt.savefig("16-复分析_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 16-复分析_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 定义域着色：色相=辐角，亮度=模 → 一眼看穿复函数")
    print("2. 零点=颜色汇聚（正环绕）；极点=颜色汇聚（逆环绕）")
    print("3. 柯西定理：解析区域内闭合积分为 0（拓扑性质）")
    print("4. 留数定理：闭合积分 = 2πi × Σ留数（计算实积分的利器）")
    print("5. 解析函数：一点信息 → 全域信息（泰勒级数无限收敛半径）")
    print("\n[解读] 复分析被誉为'数学中最完美的理论'——")
    print("       柯西定理的拓扑性、留数定理的计算力、")
    print("       解析函数的刚性（local→global），三位一体。")
    print("       黎曼猜想本质上就是关于复函数零点位置的命题。")


if __name__ == "__main__":
    main()
