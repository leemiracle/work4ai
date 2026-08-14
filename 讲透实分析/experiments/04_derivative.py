"""
讲透实分析 04 章实验：导数 + 中值定理 + Taylor + 链式法则。
跑法：python3 -u experiments/04_derivative.py
核心：导数 = 极限 / MVT 连接局部全局 / ReLU 不可微但 NN 能 work / 链式法则 = 反向传播
"""
import math


def part1_mvt():
    """中值定理：f(x)=x² on [1,3]"""
    print("=" * 65)
    print("[1] 中值定理：f(x)=x² on [1, 3]")
    print("=" * 65)
    a, b = 1.0, 3.0
    avg_slope = (b**2 - a**2) / (b - a)
    print(f"  平均斜率 = (f(b)-f(a))/(b-a) = ({b**2}-{a**2})/({b}-{a}) = {avg_slope}")
    c = avg_slope / 2
    print(f"  f'(x) = 2x → 解 2c = {avg_slope} → c = {c}")
    print(f"  c ∈ (1, 3)? {a < c < b}  → MVT 保证 ✓")


def part2_taylor():
    """Taylor 展开：sin(x) 多项式逼近"""
    print()
    print("=" * 65)
    print("[2] Taylor 展开：sin(x) 在 a=0 处的多项式逼近")
    print("=" * 65)
    x = 0.5
    print(f"\n  在 x = {x} 处（真值 sin({x}) = {math.sin(x):.10f}）：")
    print(f"  {'阶 n':<6} {'n 阶 Taylor 逼近':<20} {'误差':<15}")
    approx = 0.0
    true_sin = math.sin(x)
    for n in range(8):
        term = ((-1)**n) * (x**(2*n+1)) / math.factorial(2*n+1)
        approx += term
        err = abs(approx - true_sin)
        print(f"  {n:<6} {approx:<20.10f} {err:<15.2e}")


def part3_relu():
    """ReLU 不可微但 NN 还能 work"""
    print()
    print("=" * 65)
    print("[3] ReLU 在 0 不可微，但神经网络还能 work")
    print("=" * 65)
    print("  ReLU(x) = max(0, x)")
    print("  左导数 lim_{h→0⁻} ReLU(h)/h = 0")
    print("  右导数 lim_{h→0⁺} ReLU(h)/h = 1")
    print("  左 ≠ 右 → 不可微 ✗")
    print()
    print("  但 0 点测度为 0 → '几乎处处可微' → 反向传播仍 work")
    print("  → 这是神经网络能用 ReLU 的数学基础")


def part4_chain_rule():
    """链式法则 = 反向传播"""
    print()
    print("=" * 65)
    print("[4] 链式法则 = 反向传播")
    print("=" * 65)
    f = lambda t: (math.sin(t**2))**3
    x = 1.5
    h = 1e-8
    numeric = (f(x+h) - f(x-h)) / (2*h)
    analytic = 3 * (math.sin(x**2))**2 * math.cos(x**2) * 2 * x
    print(f"  f(x) = sin(x²)³, 在 x = {x}:")
    print(f"    数值导数  = {numeric:.10f}")
    print(f"    解析导数  = {analytic:.10f}  (3·sin²·cos·2x)")
    print(f"    差异      = {abs(numeric - analytic):.2e}")
    print("  → PyTorch backward() = 在计算图上自动应用链式法则")


def main():
    print("讲透实分析 04 章实验：导数 + 中值定理 + Taylor + 链式法则")
    part1_mvt()
    part2_taylor()
    part3_relu()
    part4_chain_rule()
    print()
    print("=" * 65)
    print("✓ 4 个核心概念验证完毕。")
    print("=" * 65)


if __name__ == "__main__":
    main()
