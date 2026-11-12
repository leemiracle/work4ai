"""
实验 05 — 数据驱动建模：Bias-Variance 权衡
=============================================
用 1/3/5/10/15/20 阶多项式拟合带噪 sin，观察 train/test 误差。
跑法: python3 05_data_driven.py  (需 numpy, <1秒)
"""
import numpy as np

np.random.seed(42)
# 训练数据：[0, 2π] 内 20 个带噪点
x = np.linspace(0, 2 * np.pi, 20)
y = np.sin(x) + np.random.normal(0, 0.2, 20)
# 测试数据：干净 sin
x_test = np.linspace(0, 2 * np.pi, 100)
y_test = np.sin(x_test)

print("=" * 58)
print("Bias-Variance：多项式阶数 vs train/test 误差")
print("=" * 58)
print(f"{'阶数':>6}  {'train_err':>10}  {'test_err':>10}  {'现象':<20}")
print("-" * 58)

for deg in [1, 3, 5, 10, 15, 20]:
    c = np.polyfit(x, y, deg)
    train_err = np.mean((np.polyval(c, x) - y) ** 2)
    test_err = np.mean((np.polyval(c, x_test) - y_test) ** 2)
    if train_err > 0.2:
        phenomenon = "欠拟合"
    elif test_err < 0.05:
        phenomenon = "★ 甜点"
    elif test_err > 0.1:
        phenomenon = "过拟合"
    else:
        phenomenon = "—"
    print(f"{deg:>6}  {train_err:>10.4f}  {test_err:>10.4f}  {phenomenon}")

print("-" * 58)
print("结论: 阶数↑→train_err↓ 但 test_err 先降后升（过拟合）")
