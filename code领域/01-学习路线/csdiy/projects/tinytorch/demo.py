#!/usr/bin/env python3
"""
tinytorch/demo.py — 端到端演示

3 个经典任务验证框架正确性：
  1. XOR 问题（非线性分类，参照 micrograd demo）
  2. 月亮分类（2D 二分类）
  3. 正弦回归（连续值预测）
"""
import random, math, sys, os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinytorch.tensor import Value
from tinytorch.nn import MLP, Sequential, Linear, Tanh, ReLU, LayerNorm
from tinytorch.optim import SGD, Momentum, Adam, AdamW, CosineScheduler
from tinytorch.loss import mse_loss, cross_entropy
from tinytorch.train import DataLoader, Trainer

def demo_xor():
    """XOR 学习（参照 micrograd demo.ipynb）"""
    print("┌─────────────────────────────────┐")
    print("│  Demo 1: XOR 非线性分类         │")
    print("└─────────────────────────────────┘\n")

    random.seed(42)
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [0, 1, 1, 0]  # XOR

    model = MLP(2, [8, 8, 1])
    optimizer = Adam(model.parameters(), lr=0.01)

    print(f"  模型: 2 → 8 → 8 → 1 (参数: {len(model.parameters())})")
    print(f"  优化器: Adam (lr=0.01)\n")

    # 训练
    for epoch in range(300):
        optimizer.zero_grad()
        total_loss = Value(0.0)
        for xi, yi in zip(X, y):
            pred = model([Value(xi[0]), Value(xi[1])])[0]
            pred = pred.tanh()  # 输出压到 [-1, 1]
            total_loss = total_loss + (pred - Value(yi)) ** 2
        avg_loss = total_loss * 0.25
        avg_loss.backward()
        optimizer.step()

        if epoch % 100 == 0 or epoch == 299:
            print(f"  epoch {epoch:3d}  loss = {avg_loss.data:.6f}")

    # 验证
    print(f"\n  结果:")
    model.eval()
    for xi, yi in zip(X, y):
        pred = model([Value(xi[0]), Value(xi[1])])[0].tanh().data
        label = 1 if pred > 0 else 0
        print(f"    XOR{xi} = {pred:+.4f} → {label} (期望: {yi}) {'✅' if label == yi else '❌'}")


def demo_moon():
    """月亮分类（2D 二分类）"""
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 2: 月亮分类（2D）         │")
    print("└─────────────────────────────────┘\n")

    random.seed(42)
    # 生成月亮形数据
    X, y = [], []
    for _ in range(80):
        t = random.uniform(0, math.pi)
        X.append([math.cos(t) + random.gauss(0, 0.1) - 0.3, math.sin(t) + random.gauss(0, 0.1)]); y.append(0)
        t = random.uniform(math.pi, 2 * math.pi)
        X.append([math.cos(t) + random.gauss(0, 0.1) + 0.3, math.sin(t) + random.gauss(0, 0.1)]); y.append(1)

    model = MLP(2, [16, 2])  # 2 输入 → 16 隐层 → 2 类
    optimizer = Adam(model.parameters(), lr=0.01)

    print(f"  数据: {len(X)} 样本, 2 类")
    print(f"  模型: 2 → 16 → 2 (CE loss)\n")

    for epoch in range(200):
        random.shuffle(list(zip(X, y)))
        optimizer.zero_grad()
        correct = 0
        total_loss = Value(0.0)
        for xi, yi in zip(X, y):
            logits = model([Value(xi[0]), Value(xi[1])])
            total_loss = total_loss + cross_entropy(logits, yi)
            pred = max(range(2), key=lambda i: logits[i].data)
            if pred == yi: correct += 1
        avg_loss = total_loss * (1.0 / len(X))
        avg_loss.backward()
        optimizer.step()
        if epoch % 50 == 0 or epoch == 199:
            print(f"  epoch {epoch:3d}  loss={avg_loss.data:.4f}  acc={correct/len(X):.1%}")


def demo_regression():
    """正弦回归（连续值预测）"""
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 3: 正弦函数回归           │")
    print("└─────────────────────────────────┘\n")

    random.seed(42)
    X = [[random.uniform(-3, 3)] for _ in range(100)]
    y = [math.sin(x[0]) for x in X]

    model = Sequential(Linear(1, 32), Tanh(), Linear(32, 32), Tanh(), Linear(32, 1))
    optimizer = Adam(model.parameters(), lr=0.01)

    print(f"  数据: {len(X)} 样本, f(x) = sin(x)")
    print(f"  模型: 1 → 32 → 32 → 1 (MSE loss)\n")

    for epoch in range(200):
        optimizer.zero_grad()
        total_loss = Value(0.0)
        for xi, yi in zip(X, y):
            pred = model([Value(xi[0])])[0]
            total_loss = total_loss + (pred - Value(yi)) ** 2
        avg_loss = total_loss * (1.0 / len(X))
        avg_loss.backward()
        optimizer.step()
        if epoch % 50 == 0 or epoch == 199:
            print(f"  epoch {epoch:3d}  MSE = {avg_loss.data:.6f}")

    # 测试几个点
    print(f"\n  验证:")
    model.eval()
    for x_test in [-3.0, -1.5, 0.0, 1.5, 3.0]:
        pred = model([Value(x_test)])[0].data
        actual = math.sin(x_test)
        print(f"    sin({x_test:+.1f}) = {actual:+.4f}  预测 = {pred:+.4f}  差 = {abs(pred-actual):.4f}")


def main():
    print("=" * 60)
    print("  tinytorch — 深度学习框架 端到端演示")
    print("  参照 micrograd + PyTorch + nanoGPT")
    print("=" * 60)

    t0 = time.time()
    demo_xor()
    demo_moon()
    demo_regression()
    elapsed = time.time() - t0

    print(f"\n{'=' * 60}")
    print(f"  全部完成 ({elapsed:.1f}s)")
    print(f"  tinytorch = tensor.py + nn.py + optim.py + loss.py + train.py")
    print(f"  理解这 5 个文件 = 理解 PyTorch 的核心设计")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import time
    main()
