"""
实验 02 — 优化模型：线性规划（生产计划）
==========================================
暴力枚举 LP：工厂生产 A/B 两种产品，求最大利润。
A: 利润300, 耗原料2+工时1; B: 利润500, 耗原料3+工时2。原料100, 工时80。
跑法: python3 02_optimization.py  (纯标准库, <1秒)
"""
best_profit, best_xa, best_xb = 0, 0, 0

for xa in range(51):          # 2*xa <= 100
    for xb in range(34):      # 3*xb <= 100
        if 2 * xa + 3 * xb <= 100 and xa + 2 * xb <= 80:
            profit = 300 * xa + 500 * xb
            if profit > best_profit:
                best_profit, best_xa, best_xb = profit, xa, xb

print("=" * 55)
print("线性规划：生产计划（A利润300 / B利润500）")
print("=" * 55)
print(f"约束: 原料 2A+3B≤100, 工时 A+2B≤80")
print(f"最优解: A={best_xa}, B={best_xb}")
print(f"最大利润: {best_profit}")
print(f"原料用量: {2*best_xa+3*best_xb}/100, 工时用量: {best_xa+2*best_xb}/80")
print()
print("LP 的美: 局部最优=全局最优（凸性保证）")
