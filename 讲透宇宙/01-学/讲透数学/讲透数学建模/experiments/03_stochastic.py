"""
实验 03 — 蒙特卡洛方法（概率统计模型）
======================================
用随机采样估计 π，验证收敛率 O(1/√N)。
跑法: python3 03_stochastic.py  (纯标准库，几秒跑完)
"""
import random
import math

random.seed(42)

print("=" * 55)
print("蒙特卡洛估计 π：随机撒点，落圆内的比例 ≈ π/4")
print("=" * 55)
print(f"{'N':>12}  {'π估计':>10}  {'误差':>10}  {'1/√N':>10}")
print("-" * 55)

for N in [1_000, 100_000, 10_000_000]:
    inside = 0
    for _ in range(N):
        x, y = random.random(), random.random()
        if x * x + y * y < 1.0:
            inside += 1
    pi_est = 4.0 * inside / N
    err = abs(pi_est - math.pi)
    theoretical = 1.0 / (N ** 0.5)
    print(f"{N:>12,}  {pi_est:>10.5f}  {err:>10.5f}  {theoretical:>10.5f}")

print("-" * 55)
print("结论：误差随 N 按 1/√N 缩小（精度提10倍需多采100倍）")
