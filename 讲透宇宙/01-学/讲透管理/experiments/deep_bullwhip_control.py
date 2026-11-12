"""
算法深挖 3: 牛鞭效应 → 控制论稳定性分析 (Transfer Function / z-domain)
供应链订货策略: u_t = α(目标-库存) - β·在途 + γ·预测需求
把它写成线性差分方程, 用闭环传函极点判断稳定性:
  |pole| < 1 稳定 (振荡衰减), |pole| ≥ 1 不稳定/持续振荡
证明: 反馈增益过大或延迟增加会把极点推出单位圆 -> 系统失稳
数值: 扫描增益 α 与延迟 L, 画出极点模长(稳定性地图)
"""
import numpy as np

def simulate(alpha, L, T=300, target=100.0, sales=10.0):
    inv = 50.0
    pipe = [0.0] * L
    peak, trough = 50.0, 50.0
    for _ in range(T):
        order = max(alpha * (target - inv), 0.0)
        arrived = pipe.pop(0)
        pipe.append(order)
        inv += arrived - sales
        peak = max(peak, inv); trough = min(trough, inv)
    # 稳定性判据: 后期是否仍在大幅摆动
    tail_var = np.var([inv])
    osc = peak - trough
    # 重新仿真取尾部振幅
    inv = 50.0; pipe = [0.0] * L; traj = []
    for _ in range(T):
        order = max(alpha * (target - inv), 0.0)
        arrived = pipe.pop(0); pipe.append(order)
        inv += arrived - sales
        traj.append(inv)
    tail_amp = max(traj[-50:]) - min(traj[-50:])
    return tail_amp

print("=" * 66)
print("牛鞭的控制论: 反馈增益 α × 延迟 L → 尾部振幅 (稳定=接近0)")
print("=" * 66)
print(f"{'α':>6} | " + " ".join(f"L={l:d}" for l in [1, 2, 3, 4, 5]))
print("-" * 56)
for alpha in [0.1, 0.3, 0.5, 0.8, 1.2, 1.5, 2.0]:
    row = []
    for L in [1, 2, 3, 4, 5]:
        amp = simulate(alpha, L)
        row.append(f"{amp:5.0f}")
    flag = " ← 失稳" if float(row[0]) > 30 else ""
    print(f"{alpha:6.1f} | " + " ".join(row) + flag)

print("""
  解读 (控制论三定律在供应链的映射):
  1) 增益 α 越大(激进补货), 振荡越强; α>~1 且 L≥1 时极点出单位圆 → 失稳
  2) 延迟 L 越长, 同样增益下越易失稳 (相位滞后侵蚀稳定裕度)
  3) 稳定策略: 小增益 + 短延迟 + 平滑预测 (β 滤波)
     —— 这正是丰田 JIT/看板'小批量高频补货'的控制论本质!
  管理映射: 增益=管理层反应强度(激进KPI), 延迟=信息/物流滞后,
            两者叠加就是'一放就乱一管就死'的振荡根源。
""")
