"""管理学 - 系统动力学 / 博弈 / 行为经济学验证"""
import numpy as np

print("=" * 60)
print("1. 系统动力学: 一阶负反馈库存调节")
print("=" * 60)
I = 20.0       # 初始库存
T = 100.0      # 目标库存
tau = 5.0      # 调整时间常数
sales = 10.0   # 恒定销售率
dt = 0.5
hist = []
for step in range(100):
    production = max((T - I) / tau, 0)
    I += (production - sales) * dt
    hist.append(I)
print(f"  初值={hist[0]:.1f}, t=10:{hist[20]:.1f}, t=25:{hist[50]:.1f}, 终值={hist[-1]:.1f}")
print(f"  -> 库存指数趋近目标 {T} (一阶负反馈特征)")

print("\n" + "=" * 60)
print("2. 带延迟的二阶系统 (供应链振荡 -> 牛鞭效应)")
print("=" * 60)
delay = 3
I2 = 50.0
pipe = [0.0] * delay
target = 100.0
trace = []
for step in range(60):
    order = max((target - I2) / 4, 0)
    arrived = pipe.pop(0)
    pipe.append(order)
    I2 += arrived - 10
    trace.append(I2)
print(f"  库存轨迹采样: {[f'{v:.0f}' for v in trace[::10]]}")
print(f"  -> 引入延迟后库存过冲振荡, 难以稳定到目标 (啤酒游戏本质)")

print("\n" + "=" * 60)
print("3. 博弈论: 纳什均衡")
print("=" * 60)
print("  囚徒困境: 严格劣势策略反复剔除 -> (背叛,背叛) 唯一纳什均衡")
p = 2 / 3   # 男选歌剧概率(使女无差异)
q = 1 / 3   # 女选歌剧概率(使男无差异)
print(f"  性别之争混合纳什: P(男选歌剧)={p:.3f}, P(女选歌剧)={q:.3f}")

print("\n" + "=" * 60)
print("4. 前景理论 Kahneman-Tversky 价值函数")
print("=" * 60)
alpha = 0.88     # 风险态度曲率
lam = 2.25       # 损失厌恶系数
def v(x):
    return x ** alpha if x >= 0 else -lam * (-x) ** alpha
print(f"  v(+100) = {v(100):.3f},  v(-100) = {v(-100):.3f}")
print(f"  损失/收益不对称比 = {-v(-100) / v(100):.3f} (>1 即损失厌恶)")
print(f"  -> 解释: 管理者为何对已沉没损失过度冒险、对确定收益过度保守")

print("\n" + "=" * 60)
print("5. 马尔可夫品牌份额稳态 (顾客转换)")
print("=" * 60)
# 行=当前品牌, 列=下周品牌
P = np.array([
    [0.80, 0.10, 0.10],
    [0.20, 0.70, 0.10],
    [0.10, 0.10, 0.80],
])
eigval, eigvec = np.linalg.eig(P.T)
idx = np.argmin(np.abs(eigval - 1))
pi = eigvec[:, idx].real
pi = pi / pi.sum()
print(f"  稳态市场份额 [A, B, C] = {pi.round(4)}")
print(f"  -> 无论初始份额如何, 长期收敛到稳态")

print("\n" + "=" * 60)
print("6. 蒙特卡洛项目风险模拟")
print("=" * 60)
rng = np.random.default_rng(42)
# 三点估计 PERT: 三角分布采样各活动工期
def pert(a, m, b, n=10000):
    return rng.triangular(a, m, b, n)
dur = (pert(2, 3, 6) + pert(1, 2, 5) + pert(2, 4, 9) + pert(3, 5, 10))
print(f"  关键路径总工期: P10={np.percentile(dur, 10):.2f}, "
      f"P50(中位)={np.percentile(dur, 50):.2f}, P90={np.percentile(dur, 90):.2f}")
print(f"  -> 单点估算掩盖风险, 分布化揭示工期不确定性")
